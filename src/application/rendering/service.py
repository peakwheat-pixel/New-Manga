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
  yields ``INPUT_REVISION_CHANGED`` without updating any current.
- SFX policy gate (§85): ``skip``/``manual`` regions are skipped by
  batch renders (``skip_policy``); a manual-SFX region renders only on
  an explicit single-region command with ``allow_manual_sfx=True``.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from application.editing.ports import RegionRepository
from application.rendering.layout import resolve_direction
from application.rendering.style import (
    FontSizeResolution,
    RenderTextStyle,
    StyleResolutionError,
    TextDirection,
    resolve_font_size,
)
from application.translation.color.service import SourceStyleService
from domain.regions.entities import SfxPolicy
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
    ) -> None:
        self._region_repo = region_repo
        self._locator = locator
        self._artifacts = artifacts
        self._storage = storage
        self._layout_engine = layout_engine
        self._compositor = compositor
        self._source_styles = source_styles
        self._font_catalog = font_catalog

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
        clean_bytes = self._read_managed(clean_revision.managed_path)

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
        for region in self._active_regions(page_id):
            prepared = self._prepare_region(
                region,
                source_style_result,
                style_defaults,
                allow_sfx=False,
            )
            if prepared.report.status == _SKIPPED:
                reports.append(prepared.report)
                continue
            if prepared.op is None:  # resolution failure → blocked page
                return _blocked(
                    "MISSING_REQUIRED_INPUT", prepared.report.skip_reason or ""
                )
            reports.append(prepared.report)
            ops.append(prepared.op)

        try:
            composed = self._compositor.compose_page(clean_bytes, ops)
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
        self, region_id: str, *, allow_manual_sfx: bool = False
    ) -> RenderOutcome:
        stored = self._region_repo.get_region(region_id)
        if stored is None or stored.deleted:
            return _blocked("TARGET_NOT_FOUND", f"region {region_id} not found")
        if stored.region_locked:
            # §47 allows rendering under translation/inpaint locks, but a
            # fully region-locked target is not written by any command here.
            return _blocked("LOCK_CHANGED", "region_locked: rendering is blocked")
        sfx = SfxPolicy(stored.sfx_policy)
        page_id = stored.page_id
        snapshot_revision_id = stored.current_revision_id

        clean = self._locate_clean(page_id)
        if clean is None:
            return _blocked(
                "MISSING_REQUIRED_INPUT",
                "rerender requires a current clean artifact (missing_clean_artifact)",
            )
        clean_record, clean_revision = clean
        clean_bytes = self._read_managed(clean_revision.managed_path)

        final = stored.text.final_translation
        if not final.strip():
            return _blocked(
                "MISSING_REQUIRED_INPUT",
                "region has no final_translation to render",
            )
        if sfx is SfxPolicy.SKIP or (sfx is SfxPolicy.MANUAL and not allow_manual_sfx):
            return _blocked(
                "SKIP_POLICY",
                f"skip_policy: sfx_policy={sfx.value} requires an "
                "explicit manual command (allow_manual_sfx)",
            )

        source_style_result = self._extract_source_style(page_id)
        prepared = self._prepare_region(
            stored, source_style_result, None, allow_sfx=True
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
            base_bytes = self._read_managed(translated[1].managed_path)
            artifact_id = translated[0].artifact_id
            expected = translated[1].artifact_revision_id

        box = stored.geometry.bbox.as_tuple()
        try:
            composed = self._compositor.compose_region(
                base_bytes, clean_bytes, box, prepared.op
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
                error_code="INPUT_REVISION_CHANGED",
                detail="region revision moved on during composition",
                reports=(prepared.report,),
            )

        return self._commit_translated(
            artifact_id=artifact_id,
            expected=expected,
            content=composed,
            clean_revision_id=clean_revision.artifact_revision_id,
            reports=(prepared.report,),
        )

    # ------------------------------------------------------------------
    # internals
    # ------------------------------------------------------------------

    def _locate_clean(
        self, page_id: str
    ) -> tuple[ArtifactRecord, ArtifactRevisionRecord] | None:
        return self._locator.locate_current(page_id, ArtifactType.CLEAN)

    def _read_managed(self, relative_path: str) -> bytes:
        return Path(self._storage.absolute_path(relative_path)).read_bytes()

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
        except OSError:
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
        sfx = SfxPolicy(region.sfx_policy)
        if sfx is SfxPolicy.SKIP or (
            sfx is SfxPolicy.MANUAL and not allow_sfx
        ):
            return _Prepared(_skip_report(region.region_id, "skip_policy"), None)

        style = RenderTextStyle.from_domain(region.style)
        if style_defaults is not None:
            style = _merge_defaults(style, style_defaults)

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
            error_code=outcome.error_code,
            detail=outcome.detail,
            reports=reports,
        )


@dataclass(frozen=True)
class _Prepared:
    report: RegionRenderReport
    op: RenderOp | None


def _skip_report(region_id: str, reason: str) -> RegionRenderReport:
    return RegionRenderReport(region_id=region_id, status=_SKIPPED, skip_reason=reason)


def _merge_defaults(
    style: RenderTextStyle, defaults: RenderTextStyle
) -> RenderTextStyle:
    """Region-persisted values win; D03 §11.4 inheritance order."""
    from dataclasses import replace as _replace

    domain_set = style
    merged = defaults
    if domain_set.font_family != RenderTextStyle().font_family:
        merged = _replace(merged, font_family=domain_set.font_family)
    if domain_set.text_color != RenderTextStyle().text_color:
        merged = _replace(merged, text_color=domain_set.text_color)
    if domain_set.stroke_width != RenderTextStyle().stroke_width:
        merged = _replace(
            merged,
            stroke_enabled=domain_set.stroke_enabled,
            stroke_color=domain_set.stroke_color,
            stroke_width=domain_set.stroke_width,
        )
    if not domain_set.auto_font_size_enabled:
        merged = _replace(
            merged,
            auto_font_size_enabled=False,
            manual_font_size=domain_set.manual_font_size,
        )
    return _replace(
        merged,
        font_size_offset=domain_set.font_size_offset,
        line_spacing=domain_set.line_spacing,
        text_direction=domain_set.text_direction,
        text_align=domain_set.text_align,
    )
