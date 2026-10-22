"""Render use cases (D06 §23 Rendering, §41 rerender_all/selected/single,
§47 single-region force render, §85 SFX Policy Gate; TASK-002 §8.1/§8.2).

Frozen behaviour implemented here:

- rerender only consumes ``current final_translation + current valid
  Clean Artifact + TextStyle`` and never OCR/Translation/Inpaint (the
  service holds no AI provider references at all — AC-RENDER-001).
- a missing Clean artifact is ``BLOCKED: missing_clean_artifact`` and
  never auto-inpainted (AC-RENDER-002).
- page render: every eligible region is resolved (font size chain, D03
  §11) and composed onto the Clean image as one new ``translated``
  ArtifactRevision through the atomic compare-and-write seam; failure or
  conflict keeps the old current (AC-ART / TASK-002 §8.1).
- single-region render (§8.2): the page's current translated image is
  the composition base; only the target region's box is restored from
  Clean and redrawn; a moved-on region revision or page artifact base
  yields ``COMPOSITION_BASE_CHANGED`` without updating any current.
- SFX policy gate (§85): only ``region_type = sfx`` follows ``skip``/``manual``
  (skipped by batch renders as ``skip_policy``); a manual-SFX region renders
  only on an explicit single-region command with ``allow_manual_sfx=True``.
  Non-SFX regions are never gated by this policy, whatever its value, and the
  decision comes from the shared rule
  (:func:`application.translation.context.gate.decide_sfx_translation`) that
  the planner and the Translate Step also use (TASK-035 / F-1).
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from application.editing.ports import RegionRepository
from application.rendering.layout import resolve_direction
from application.rendering.style import (
    FontSizeResolution,
    RenderTextStyle,
    StyleResolutionError,
    resolve_font_size,
)
from application.translation.color.service import SourceStyleService
from application.translation.context.gate import decide_sfx_translation
from domain.regions.entities import RegionType, SfxPolicy, TextStyle
from ports.repositories.artifacts import (
    ArtifactRecord,
    ArtifactRepositoryPort,
    ArtifactRevisionRecord,
    ArtifactType,
    CommitStatus,
    ContentProvider,
    NewArtifact,
    PendingArtifactCommit,
)
from ports.repositories.storage import ManagedFileStoragePort
from ports.rendering.ports import (
    DrawItem,
    FontCatalog,
    ImageCompositor,
    LayoutRequest,
    PageArtifactLocator,
    RenderOp,
    TextLayoutEngine,
)
from ports.rendering.direction import TextDirection

_RENDERED = "rendered"
_SKIPPED = "skipped"


class RenderStatus:
    COMMITTED = "committed"
    BLOCKED = "blocked"
    CONFLICT = "conflict"
    WRITE_FAILED = "write_failed"


@dataclass(frozen=True)
class RegionRenderReport:
    region_id: str
    status: str  # rendered | skipped
    skip_reason: str | None = None
    final_font_size: float | None = None
    resolution: FontSizeResolution | None = None
    font_substituted: bool = False
    direction: TextDirection | None = None


@dataclass(frozen=True)
class RenderOutcome:
    status: str
    artifact_id: str | None = None
    revision_no: int | None = None
    managed_path: str | None = None
    provenance_json: str | None = None
    reports: tuple[RegionRenderReport, ...] = ()
    error_code: str | None = None
    detail: str | None = None


def _blocked(error_code: str, detail: str, **extra) -> RenderOutcome:
    return RenderOutcome(status=RenderStatus.BLOCKED, error_code=error_code, detail=detail, **extra)


class RenderService:
    def __init__(
        self,
        *,
        region_repo: RegionRepository,
        locator: PageArtifactLocator,
        artifacts: ArtifactRepositoryPort,
        storage: ManagedFileStoragePort,
        layout_engine: TextLayoutEngine,
        compositor: ImageCompositor,
        source_styles: SourceStyleService,
        font_catalog: FontCatalog,
        content_decoder: Callable[[str, bytes], bytes] | None = None,
        original_page_reader: Callable[[str], bytes | None] | None = None,
    ) -> None:
        """``content_decoder`` is a TASK-033 assembly bridge, opt-in and
        behaviour-preserving: pipeline artifact revisions are stored in the
        provider layer's ``NMFR`` container (``application/x-newmanga-frame``,
        deliberately not a shareable image format), while rendering composes
        on PNG. The assembly injects a decoder that converts such payloads
        and passes anything else through unchanged; ``None`` (tests, and any
        assembly whose artifacts are already PNG) keeps the historical
        behaviour exactly. The application layer never imports the provider
        container code — the decoder closure comes in from the assembly.
        """
        self._region_repo = region_repo
        self._locator = locator
        self._artifacts = artifacts
        self._storage = storage
        self._layout_engine = layout_engine
        self._compositor = compositor
        self._source_styles = source_styles
        self._font_catalog = font_catalog
        self._content_decoder = content_decoder
        self._original_page_reader = original_page_reader

    # ------------------------------------------------------------------
    # page rerender (D06 §41)
    # ------------------------------------------------------------------

    def rerender_page(
        self,
        page_id: str,
        *,
        style_defaults: RenderTextStyle | None = None,
        expected_translated_revision_id: str | None = None,
    ) -> RenderOutcome:
        clean = self._locate_clean(page_id)
        if clean is None:
            return _blocked(
                "MISSING_REQUIRED_INPUT",
                "rerender requires a current clean artifact "
                "(missing_clean_artifact); run inpaint first",
            )
        clean_record, clean_revision = clean
        try:
            clean_bytes = self._read_managed(clean_revision.managed_path)
        except (OSError, ValueError) as error:
            return _blocked("MISSING_REQUIRED_INPUT", f"clean artifact could not be read: {error}")

        # §8.2: snapshot the composition base when the step starts; the
        # commit compares against this expectation, so anything committed
        # in between is a COMPOSITION_BASE_CHANGED conflict.
        translated = self._locator.locate_current(page_id, ArtifactType.TRANSLATED)
        if translated is None:
            translated_record = self._artifacts.create_artifact(
                NewArtifact(
                    book_id=clean_record.book_id,
                    chapter_id=clean_record.chapter_id,
                    page_id=page_id,
                    artifact_type=ArtifactType.TRANSLATED,
                )
            )
            artifact_id = translated_record.artifact_id
            expected = expected_translated_revision_id
        else:
            artifact_id = translated[0].artifact_id
            expected = (
                expected_translated_revision_id
                if expected_translated_revision_id is not None
                else translated[1].artifact_revision_id
            )

        source_style_result = self._extract_source_style(page_id)
        reports: list[RegionRenderReport] = []
        ops: list[RenderOp] = []
        skipped_sfx = []
        for region in self._active_regions(page_id):
            prepared = self._prepare_region(
                region,
                source_style_result,
                style_defaults,
                allow_sfx=False,
            )
            if prepared.report.status == _SKIPPED:
                if prepared.report.skip_reason not in ("skip_policy", "empty_final"):
                    return _blocked(
                        "MISSING_REQUIRED_INPUT",
                        prepared.report.skip_reason or "region layout could not be resolved",
                    )
                reports.append(prepared.report)
                if (
                    region.region_type is RegionType.SFX
                    and region.sfx_policy in (SfxPolicy.SKIP, SfxPolicy.MANUAL)
                ):
                    skipped_sfx.append(region)
                continue
            if prepared.op is None:  # resolution failure → blocked page
                return _blocked(
                    "MISSING_REQUIRED_INPUT", prepared.report.skip_reason or ""
                )
            reports.append(prepared.report)
            ops.append(prepared.op)

        try:
            # The clean artifact has already erased every inpaint mask. For
            # SFX regions explicitly withheld by the batch policy, restore
            # their original pixels before drawing the remaining translations.
            # This also removes any old translated text because composition
            # starts from clean rather than the prior translated artifact.
            if skipped_sfx:
                original = self._locator.locate_current(page_id, ArtifactType.ORIGINAL)
                try:
                    if original is not None:
                        original_bytes = self._read_managed(original[1].managed_path)
                    elif self._original_page_reader is not None:
                        # Normal import stores the immutable original on Page's
                        # Managed Copy reference; it does not necessarily create
                        # a media_artifacts ORIGINAL row. The assembly callback
                        # reads that existing protected copy without inventing a
                        # second artifact identity.
                        original_bytes = self._original_page_reader(page_id)
                    else:
                        original_bytes = None
                except (OSError, ValueError) as error:
                    return _blocked(
                        "MISSING_REQUIRED_INPUT",
                        f"original source could not be read for skipped SFX: {error}",
                    )
                if not original_bytes:
                    return _blocked(
                        "MISSING_REQUIRED_INPUT",
                        "rerender requires the current original artifact for skipped SFX",
                    )
                for region in skipped_sfx:
                    box = region.geometry.bbox
                    composed_base = self._compositor.compose_region(
                        clean_bytes,
                        original_bytes,
                        box.as_tuple(),
                        _empty_render_op(box.x, box.y, box.width, box.height),
                    )
                    clean_bytes = composed_base
            composed = self._compositor.compose_page(clean_bytes, ops)
        except ValueError as error:
            # The compositor raises ValueError only for unusable input bytes
            # (undecodable images, dimension mismatch, box outside the page):
            # a required-input problem under contract §11, not a write
            # failure.
            return RenderOutcome(
                status=RenderStatus.BLOCKED,
                error_code="MISSING_REQUIRED_INPUT",
                detail=str(error),
                reports=tuple(reports),
            )
        except OSError as error:
            return RenderOutcome(
                status=RenderStatus.WRITE_FAILED,
                error_code="ARTIFACT_WRITE_FAILED",
                detail=str(error),
                reports=tuple(reports),
            )

        return self._commit_translated(
            artifact_id=artifact_id,
            expected=expected,
            content=composed,
            clean_revision_id=clean_revision.artifact_revision_id,
            reports=tuple(reports),
        )

    # ------------------------------------------------------------------
    # single-region rerender (D06 §47, TASK-002 §8.2)
    # ------------------------------------------------------------------

    def rerender_region(
        self,
        region_id: str,
        *,
        allow_manual_sfx: bool = False,
        style_defaults: RenderTextStyle | None = None,
    ) -> RenderOutcome:
        """Rerender one region (D06 §47).

        ``style_defaults`` carries the same meaning as in :meth:`rerender_page`
        (D03 §11.4: persisted Region values win, then the supplied defaults,
        then the D03 §11.6 constants). ``None`` keeps the historical behaviour
        byte-for-byte; the single-region path only differs in its composition
        base, never in style inheritance.
        """
        stored = self._region_repo.get_region(region_id)
        if stored is None or stored.deleted:
            return _blocked("TARGET_NOT_FOUND", f"region {region_id} not found")
        if stored.region_locked:
            # §47 allows rendering under translation/inpaint locks, but a
            # fully region-locked target is not written by any command here.
            return _blocked("LOCK_CHANGED", "region_locked: rendering is blocked")
        page_id = stored.page_id
        snapshot_revision_id = stored.current_revision_id

        clean = self._locate_clean(page_id)
        if clean is None:
            return _blocked(
                "MISSING_REQUIRED_INPUT",
                "rerender requires a current clean artifact (missing_clean_artifact)",
            )
        clean_record, clean_revision = clean
        try:
            clean_bytes = self._read_managed(clean_revision.managed_path)
        except (OSError, ValueError) as error:
            return _blocked("MISSING_REQUIRED_INPUT", f"clean artifact could not be read: {error}")

        final = stored.text.final_translation
        if not final.strip():
            return _blocked(
                "MISSING_REQUIRED_INPUT",
                "region has no final_translation to render",
            )
        if not _sfx_gate_allows(
            stored.region_type.value,
            stored.sfx_policy.value,
            allow_manual=allow_manual_sfx,
        ):
            return _blocked(
                "SKIP_POLICY",
                f"skip_policy: sfx_policy={stored.sfx_policy.value} on an sfx "
                "region requires an explicit manual command (allow_manual_sfx)",
            )

        source_style_result = self._extract_source_style(page_id)
        prepared = self._prepare_region(
            stored,
            source_style_result,
            style_defaults,
            allow_sfx=True,
        )
        if prepared.op is None:
            return _blocked("MISSING_REQUIRED_INPUT", prepared.report.skip_reason or "")

        translated = self._locator.locate_current(page_id, ArtifactType.TRANSLATED)
        if translated is None:
            base_bytes = clean_bytes
            record = self._artifacts.create_artifact(
                NewArtifact(
                    book_id=clean_record.book_id,
                    chapter_id=clean_record.chapter_id,
                    page_id=page_id,
                    artifact_type=ArtifactType.TRANSLATED,
                )
            )
            artifact_id, expected = record.artifact_id, None
        else:
            try:
                base_bytes = self._read_managed(translated[1].managed_path)
            except (OSError, ValueError) as error:
                return _blocked(
                    "MISSING_REQUIRED_INPUT", f"translated artifact could not be read: {error}"
                )
            artifact_id = translated[0].artifact_id
            expected = translated[1].artifact_revision_id

        box = stored.geometry.bbox.as_tuple()
        try:
            composed = self._compositor.compose_region(
                base_bytes, clean_bytes, box, prepared.op
            )
        except ValueError as error:
            # Same input-vs-write split as rerender_page: ValueError means
            # unusable composition input, not a write failure.
            return RenderOutcome(
                status=RenderStatus.BLOCKED,
                error_code="MISSING_REQUIRED_INPUT",
                detail=str(error),
                reports=(prepared.report,),
            )
        except OSError as error:
            return RenderOutcome(
                status=RenderStatus.WRITE_FAILED,
                error_code="ARTIFACT_WRITE_FAILED",
                detail=str(error),
                reports=(prepared.report,),
            )

        # §8.2: re-check the region current before the write transaction.
        current = self._region_repo.get_region(region_id)
        if current is None or current.current_revision_id != snapshot_revision_id:
            return RenderOutcome(
                status=RenderStatus.CONFLICT,
                error_code="COMPOSITION_BASE_CHANGED",
                detail="region revision moved on during composition",
                reports=(prepared.report,),
            )

        return self._commit_translated(
            artifact_id=artifact_id,
            expected=expected,
            content=composed,
            clean_revision_id=clean_revision.artifact_revision_id,
            reports=(prepared.report,),
            composition_base_changed=True,
        )

    # ------------------------------------------------------------------
    # internals
    # ------------------------------------------------------------------

    def _locate_clean(
        self, page_id: str
    ) -> tuple[ArtifactRecord, ArtifactRevisionRecord] | None:
        return self._locator.locate_current(page_id, ArtifactType.CLEAN)

    def _read_managed(self, relative_path: str) -> bytes:
        data = Path(self._storage.absolute_path(relative_path)).read_bytes()
        if self._content_decoder is not None:
            return self._content_decoder(relative_path, data)
        return data

    def _active_regions(self, page_id: str) -> Sequence:
        regions = [
            region
            for region in self._region_repo.list_regions(page_id)
            if not region.deleted
        ]
        return sorted(regions, key=lambda region: region.reading_order)

    def _extract_source_style(self, page_id: str):
        original = self._locator.locate_current(page_id, ArtifactType.ORIGINAL)
        if original is None:
            return None
        try:
            original_bytes = self._read_managed(original[1].managed_path)
        except (OSError, ValueError):
            return None
        return original_bytes

    def _prepare_region(
        self,
        region,
        original_bytes: bytes | None,
        style_defaults: RenderTextStyle | None,
        *,
        allow_sfx: bool,
    ):
        """Resolve one region into a RenderOp + report, or a skip report."""
        from dataclasses import replace as _replace

        final = region.text.final_translation
        if not final.strip():
            return _Prepared(
                _skip_report(region.region_id, "empty_final"), None
            )
        if not _sfx_gate_allows(
            region.region_type.value, region.sfx_policy.value, allow_manual=allow_sfx
        ):
            return _Prepared(_skip_report(region.region_id, "skip_policy"), None)

        style = RenderTextStyle.from_domain(region.style)
        if style_defaults is not None:
            # Use the RAW domain TextStyle to decide what the Region really
            # persisted; ``style`` also carries synthesis defaults (0 stroke,
            # offset 0, ...) that must never shadow the global defaults (B1).
            style = _merge_defaults(region.style, style, style_defaults)

        source_result = None
        if original_bytes is not None:
            source_result = self._source_styles.extract(
                original_bytes, region.geometry.bbox.as_tuple()
            )
            source = source_result.style
            style = _replace(
                style,
                detected_source_font_size=source.detected_source_font_size,
                source_font_size_confidence=source.source_font_size_confidence,
            )
        else:
            source = None

        box = region.geometry.bbox
        direction = resolve_direction(
            style.text_direction, box.width, box.height, source
        )
        resolved_font = self._font_catalog.resolve(style.font_family)

        def fits(size: float) -> bool:
            result = self._layout_engine.layout(
                LayoutRequest(
                    text=final,
                    font_family=style.font_family,
                    font_size=size,
                    direction=direction,
                    box_width=box.width,
                    box_height=box.height,
                    stroke_width=style.stroke_width if style.stroke_enabled else 0.0,
                    line_spacing=style.line_spacing,
                )
            )
            return result.fits

        try:
            resolution = resolve_font_size(style, fits)
        except StyleResolutionError as error:
            return _Prepared(
                RegionRenderReport(
                    region_id=region.region_id,
                    status=_SKIPPED,
                    skip_reason=f"style_resolution_failed: {error}",
                ),
                None,
            )

        layout = self._layout_engine.layout(
            LayoutRequest(
                text=final,
                font_family=style.font_family,
                font_size=resolution.final_font_size,
                direction=direction,
                box_width=box.width,
                box_height=box.height,
                stroke_width=style.stroke_width if style.stroke_enabled else 0.0,
                line_spacing=style.line_spacing,
            )
        )
        op = RenderOp(
            items=layout.items,
            region_x=box.x,
            region_y=box.y,
            region_width=box.width,
            region_height=box.height,
            font_family=resolved_font.resolved_family,
            font_size=resolution.final_font_size,
            text_color=style.text_color,
            stroke_enabled=style.stroke_enabled,
            stroke_color=style.stroke_color,
            stroke_width=style.stroke_width,
            direction=direction,
            text_align=style.text_align,
        )
        report = RegionRenderReport(
            region_id=region.region_id,
            status=_RENDERED,
            final_font_size=resolution.final_font_size,
            resolution=resolution,
            font_substituted=not resolved_font.available,
            direction=direction,
        )
        return _Prepared(report, op)

    def _commit_translated(
        self,
        *,
        artifact_id: str,
        expected: str | None,
        content: bytes,
        clean_revision_id: str,
        reports: tuple[RegionRenderReport, ...],
        composition_base_changed: bool = False,
    ) -> RenderOutcome:
        provenance = {
            "step": "render",
            "ai_invoked": False,  # structural: no AI ports exist here
            "clean_revision": clean_revision_id,
            "regions": {
                report.region_id: {
                    "status": report.status,
                    "skip_reason": report.skip_reason,
                    "final_font_size": report.final_font_size,
                    "font_substituted": report.font_substituted,
                    "direction": report.direction.value if report.direction else None,
                }
                for report in reports
            },
        }
        outcome = self._artifacts.commit_revision(
            PendingArtifactCommit(
                artifact_id=artifact_id,
                content_provider=ContentProvider(payload=content),
                mime_type="image/png",
                expected_current_revision_id=expected,
                source_artifact_revision_id=clean_revision_id,
                provenance_json=json.dumps(provenance, ensure_ascii=False),
                file_suffix=".png",
            )
        )
        if outcome.status is CommitStatus.COMMITTED:
            assert outcome.revision is not None
            return RenderOutcome(
                status=RenderStatus.COMMITTED,
                artifact_id=artifact_id,
                revision_no=outcome.revision.revision_no,
                managed_path=outcome.revision.managed_path,
                provenance_json=json.dumps(provenance, ensure_ascii=False),
                reports=reports,
            )
        status = {
            CommitStatus.CONFLICT: RenderStatus.CONFLICT,
            CommitStatus.WRITE_FAILED: RenderStatus.WRITE_FAILED,
            CommitStatus.HASH_MISMATCH: RenderStatus.WRITE_FAILED,
            CommitStatus.TARGET_NOT_FOUND: RenderStatus.WRITE_FAILED,
            CommitStatus.DB_FAILED: RenderStatus.WRITE_FAILED,
        }[outcome.status]
        return RenderOutcome(
            status=status,
            error_code=(
                "COMPOSITION_BASE_CHANGED"
                if composition_base_changed and outcome.status is CommitStatus.CONFLICT
                else outcome.error_code
            ),
            detail=outcome.detail,
            reports=reports,
        )


@dataclass(frozen=True)
class _Prepared:
    report: RegionRenderReport
    op: RenderOp | None


def _empty_render_op(x: int, y: int, width: int, height: int) -> RenderOp:
    """No-op draw used with compose_region's existing pixel-restore seam."""
    return RenderOp(
        items=(),
        region_x=x,
        region_y=y,
        region_width=width,
        region_height=height,
        font_family="Arial",
        font_size=1,
        text_color="#000000",
        stroke_enabled=False,
        stroke_color="#FFFFFF",
        stroke_width=0,
        direction=TextDirection.HORIZONTAL,
    )


def _skip_report(region_id: str, reason: str) -> RegionRenderReport:
    return RegionRenderReport(region_id=region_id, status=_SKIPPED, skip_reason=reason)


def _sfx_gate_allows(
    region_type: str, sfx_policy: str, *, allow_manual: bool
) -> bool:
    """D06 §85 SFX Policy Gate using the **single shared rule** (TASK-035).

    ``decide_sfx_translation`` is the same implementation the planner and the
    Translate Step use, so the ``region_type == sfx`` precondition and the
    policy mapping exist in exactly one place — F-1's root cause was two
    drifting copies (one per layer).

    ``allow_manual`` is the rendering layer's own escape hatch (D06 §47: an
    explicit single-region force render), not a second policy rule: it only
    lets an *explicitly requested* manual SFX through.
    """
    action = decide_sfx_translation(region_type, sfx_policy)
    if not action.skipped:
        return True
    return allow_manual and SfxPolicy(sfx_policy) is SfxPolicy.MANUAL


def _merge_defaults(
    domain_style: TextStyle,
    style: RenderTextStyle,
    defaults: RenderTextStyle,
) -> RenderTextStyle:
    """Region-persisted values win; D03 §11.4 inheritance order.

    ``domain_style`` is the RAW persisted ``TextStyle`` (the only source of
    "was this field explicitly set?"); ``style`` is its render-side synthesis
    (``RenderTextStyle.from_domain``). The synthesised fields that the domain
    model cannot persist (``stroke_width=0.0`` default, ``font_size_offset=0``,
    ``line_spacing=1.0``, ``text_align="start"``, ``text_direction=AUTO``) must
    NOT shadow the global defaults -- review r1 blocker B1. Only a persisted
    ``font_family`` / ``text_color`` / stroke pair / font-size choice overrides
    the defaults; everything else (including the four fields absent from the
    domain ``TextStyle``) inherits from ``defaults``.
    """
    from dataclasses import replace as _replace

    merged = defaults
    if domain_style.font_family:
        merged = _replace(merged, font_family=style.font_family)
    if domain_style.text_color:
        merged = _replace(merged, text_color=style.text_color)
    # The domain TextStyle has no ``stroke_enabled``: a non-zero width or a
    # stored colour is the persisted marker; the synthesised style then decides
    # enabled/colour/width as a group (historical rendering convention).
    if domain_style.stroke_width != 0.0 or bool(domain_style.stroke_color):
        merged = _replace(
            merged,
            stroke_enabled=style.stroke_enabled,
            stroke_color=style.stroke_color,
            stroke_width=style.stroke_width,
        )
    # ``auto_font_size_enabled=False`` (manual mode) or an explicit font_size is
    # the persisted marker for the font-size group.
    if domain_style.font_size is not None or not domain_style.auto_font_size_enabled:
        merged = _replace(
            merged,
            auto_font_size_enabled=style.auto_font_size_enabled,
            manual_font_size=style.manual_font_size,
        )
    return merged
