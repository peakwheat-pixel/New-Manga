"""Production step handlers for the TASK-013 pipeline seam (TASK-019).

Handlers connect the capability ports to ``PipelineService`` without inventing
a second scheduler: they receive ``(StepRun, PlanUnit, PipelineRun)`` and return
one ``StepResult``. Three invariants shape the code:

- **write scope** — every result names exactly the unit's target, and a Region
  step prepares exactly one Region revision (AC-OCR-001, AC-RFULL-002);
- **pointer ownership** — content revisions are *prepared* here and the seam
  flips the current pointer; a region-scoped artifact (mask/clean) has no slot
  in ``StepResult.revision_updates``, so that pointer is compare-and-set here
  with the same guard semantics;
- **fail closed** — missing binding, not-ready provider, locked region or an
  unimplemented route raise typed errors; nothing is silently substituted and
  no mock result is produced (AC-FALLBACK-001, AC-GPU-001, AC-OPTIONAL-002).

``detect``/``color``/``term_extract``/``render`` are intentionally absent: this
Task owns the detection/OCR/translation/inpaint capability ports only, and an
absent handler is a provider-availability error, never a fake success.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Protocol

from application.editing.ports import RegionRepository
from application.translation.inpaint.mask import (
    DEFAULT_MASK_PARAMS,
    MASK_SOURCE_REFINED,
    MASK_SOURCE_REGION_GEOMETRY,
    area_ratio,
    dilate,
    from_boxes,
    from_polygons,
    mask_record,
    refine,
)
from application.translation.inpaint.step import (
    InpaintStepRequest,
    execute_inpaint_step,
)
from application.translation.pipeline.executor import StepExecutionError
from domain.tasks.models import PipelineRun, PlanUnit, StageState, StepResult, StepRun
from infrastructure.providers.fallback import (
    FallbackChain,
    chain_from_binding,
    run_chain,
)
from application.translation.inpaint.route_catalog import provider_id_for_route
from application.translation.inpaint.router import (
    RoutePolicy,
    RouterFeatures,
    require_route,
)
from infrastructure.providers.registry import ProviderRegistry
from infrastructure.providers.retry import RetryPolicy
from infrastructure.providers.step_writes import (
    UNCHECKED,
    ArtifactStepWriter,
    PreparedArtifact,
    RegionStepWriter,
    artifact_payload_from_frame,
    decode_frame_payload,
    decode_mask_payload,
    mask_payload,
)
from ports.inpaint.ports import (
    ROUTE_BRUSHNET,
    ROUTE_EDGE_BLEED,
    ROUTE_FLUX_FILL,
    ROUTE_SIMPLE_FILL,
    BooleanMask,
    ImageFrame,
)
from ports.ocr.ports import (
    SCRIPT_JAPANESE,
    TEXT_DIRECTION_HORIZONTAL,
    OcrRequest,
)
from ports.providers.errors import (
    ProviderError,
    ProviderInputError,
    ProviderNotConfigured,
    ProviderUnavailable,
)
from ports.providers.profiles import CAPABILITY_INPAINT, CAPABILITY_OCR, CAPABILITY_TRANSLATION
from ports.translation.protocol import (
    ContextPage,
    RegionInput,
    build_request_payload,
)

STEP_OCR = "ocr"
STEP_TRANSLATE = "translate"
STEP_SEGMENT = "segment"
STEP_MASK_REFINE = "mask_refine"
STEP_INPAINT = "inpaint"

ARTIFACT_MASK = "mask"
ARTIFACT_CLEAN = "clean"

DEFAULT_CONTEXT_TOKEN_BUDGET = 2000
DEFAULT_CONTEXT_PAGES = 1


class PageImageSource(Protocol):
    """Supplies decoded pixels; implemented by the bootstrap assembly."""

    def page_frame(self, page_id: str) -> ImageFrame: ...

    def region_crop(
        self, page_id: str, region_id: str
    ) -> tuple[bytes, int, int]: ...


@dataclass(frozen=True)
class RegionMaskGeometry:
    """Region geometry expressed as mask primitives."""

    boxes: tuple[tuple[int, int, int, int], ...] = ()
    polygons: tuple[tuple[tuple[int, int], ...], ...] = ()


class RegionGeometrySource(Protocol):
    def mask_geometry(self, region_id: str) -> RegionMaskGeometry: ...


@dataclass
class HandlerDependencies:
    """Everything the handlers may use; all of it is injected."""

    registry: ProviderRegistry
    regions: RegionRepository
    region_writer: RegionStepWriter
    artifacts: ArtifactStepWriter
    images: PageImageSource
    geometry: RegionGeometrySource
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    heavy_runner: Any = None  # DeviceManager.run_guarded, optional
    route_policy: RoutePolicy = field(default_factory=RoutePolicy)


class ProductionHandlers:
    """Build the ``step_type -> handler`` mapping injected into the pipeline."""

    def __init__(self, dependencies: HandlerDependencies) -> None:
        self.deps = dependencies
        self._handlers: dict[str, Any] = {
            step_type: self._typed(handler)
            for step_type, handler in (
                (STEP_OCR, self.handle_ocr),
                (STEP_TRANSLATE, self.handle_translate),
                (STEP_SEGMENT, self.handle_segment),
                (STEP_MASK_REFINE, self.handle_mask_refine),
                (STEP_INPAINT, self.handle_inpaint),
            )
        }

    @staticmethod
    def _typed(handler: Any) -> Any:
        """Preserve the provider error code across the pipeline seam.

        ``ProductionStepExecutor`` re-raises :class:`StepExecutionError`
        unchanged and flattens everything else into ``PROVIDER_FAILED``; a
        handler therefore converts its typed provider failures itself so the
        StepRun keeps a diagnosable code (D06 §93).
        """

        def wrapped(step_run: StepRun, unit: PlanUnit, run: PipelineRun) -> StepResult:
            try:
                return handler(step_run, unit, run)
            except StepExecutionError:
                raise
            except ProviderError as error:
                detail = error.detail
                if error.provider_id:
                    detail = f"{detail} (provider={error.provider_id})"
                if error.stage:
                    detail = f"{detail} (stage={error.stage})"
                raise StepExecutionError(error.error_code, detail) from error

        return wrapped

    def as_mapping(self) -> dict[str, Any]:
        return dict(self._handlers)

    # ------------------------------------------------------------------
    # OCR (D06 §7, AC-OCR-001/004)
    # ------------------------------------------------------------------

    def handle_ocr(
        self, step_run: StepRun, unit: PlanUnit, run: PipelineRun
    ) -> StepResult:
        region_id = self._require_region(unit)
        chain = self._chain(run, STEP_OCR)
        crop, width, height = self.deps.images.region_crop(unit.page_id, region_id)
        settings = self._section(run.settings_snapshot, "ocr")
        request = OcrRequest(
            region_id=region_id,
            page_id=unit.page_id,
            image_bytes=crop,
            width=width,
            height=height,
            script=str(settings.get("script", SCRIPT_JAPANESE)),
            direction=str(settings.get("direction", TEXT_DIRECTION_HORIZONTAL)),
        )

        outcome = run_chain(
            chain,
            lambda provider_id: self._invoke_provider(
                provider_id, CAPABILITY_OCR, lambda provider: provider.recognize(request)
            ),
            policy=self.deps.retry_policy,
            payload_hash_provider=lambda: _payload_hash(request.image_bytes, request.region_id),
        )
        result = outcome.result
        if result.region_id != region_id:
            raise ProviderInputError(
                "provider answered for a different region",
                provider_id=outcome.final_provider_id,
                stage=STEP_OCR,
            )
        prepared = self.deps.region_writer.prepare_ocr_text(
            region_id,
            result.text,
            provider_id=result.provider_id,
            model=result.model,
            options=dict(result.options),
            source_run_id=run.run_id,
            source_step_run_id=step_run.step_run_id,
            expected_current_revision_id=step_run.input_refs.get("region"),
        )
        outputs = {
            "ocr_text": result.text,
            "confidence": result.confidence,
            "retranslate_hint": prepared.retranslate_hint,
            "revision_no": prepared.revision_no,
            "provenance": {
                **result.provenance(),
                **outcome.as_provenance(),
                "device_host": self._device_host(),
            },
        }
        return StepResult(
            target_id=unit.target_id,
            step_type=unit.step_type,
            outputs=outputs,
            output_target_ids=(unit.target_id,),
            revision_updates={"region": prepared.revision_id},
            next_stage_states={unit.step_type: StageState.COMPLETED},
        )

    # ------------------------------------------------------------------
    # Translate (D06 §18, AC-TRANS/AC-FALLBACK)
    # ------------------------------------------------------------------

    def handle_translate(
        self, step_run: StepRun, unit: PlanUnit, run: PipelineRun
    ) -> StepResult:
        region_id = self._require_region(unit)
        region = self.deps.regions.get_region(region_id)
        if region is None or region.deleted:
            raise ProviderInputError(
                f"region {region_id!r} is not available", stage=STEP_TRANSLATE
            )
        source_text = region.text.ocr_text
        if not source_text.strip():
            raise ProviderInputError(
                "region has no OCR text to translate",
                stage=STEP_TRANSLATE,
            )
        chain = self._chain(run, STEP_TRANSLATE)
        settings = self._section(run.settings_snapshot, "translate")
        payload = build_request_payload(
            page_id=unit.page_id,
            regions=[RegionInput(region_id, source_text)],
            context_pages=self._context_pages(unit.page_id, region_id, run),
            glossary=self._glossary(run),
            token_budget=int(
                settings.get("context_token_budget", DEFAULT_CONTEXT_TOKEN_BUDGET)
            ),
        )
        outcome = run_chain(
            chain,
            lambda provider_id: self._invoke_provider(
                provider_id,
                CAPABILITY_TRANSLATION,
                lambda provider: provider.translate(payload),
            ),
            policy=self.deps.retry_policy,
            payload_hash_provider=payload.payload_hash,
        )
        result = outcome.result
        translations = dict(result.translations)
        if set(translations) != {region_id}:
            raise ProviderInputError(
                "provider output does not map onto the requested region",
                provider_id=outcome.final_provider_id,
                stage=STEP_TRANSLATE,
            )
        prepared = self.deps.region_writer.prepare_machine_translation(
            region_id,
            translations[region_id],
            provider_id=result.provider_id,
            model=result.model,
            options=dict(result.options),
            source_run_id=run.run_id,
            source_step_run_id=step_run.step_run_id,
            expected_current_revision_id=step_run.input_refs.get("region"),
        )
        outputs = {
            "machine_translation": translations[region_id],
            "final_source": prepared.final_source,
            "revision_no": prepared.revision_no,
            "context_provenance": {
                "context_pages": list(payload.context_pages),
                "truncated_context_pages": list(payload.truncated_context_pages),
            },
            "provenance": {
                **result.provenance(),
                **outcome.as_provenance(),
                "payload_hash": payload.payload_hash(),
                "device_host": self._device_host(),
            },
        }
        return StepResult(
            target_id=unit.target_id,
            step_type=unit.step_type,
            outputs=outputs,
            output_target_ids=(unit.target_id,),
            revision_updates={"region": prepared.revision_id},
            next_stage_states={unit.step_type: StageState.COMPLETED},
        )

    # ------------------------------------------------------------------
    # Segment / Mask Refine / Inpaint (D06 §19~§22)
    # ------------------------------------------------------------------

    def handle_segment(
        self, step_run: StepRun, unit: PlanUnit, run: PipelineRun
    ) -> StepResult:
        region_id = self._require_region(unit)
        frame = self.deps.images.page_frame(unit.page_id)
        geometry = self.deps.geometry.mask_geometry(region_id)
        raw_mask = _mask_from_geometry(frame, geometry, region_id)
        if raw_mask.area == 0:
            raise ProviderInputError(
                "region geometry produced an empty mask",
                stage=STEP_SEGMENT,
            )
        record = mask_record(
            raw_mask, raw_mask, source=MASK_SOURCE_REGION_GEOMETRY
        )
        payload, mime, width, height = mask_payload(raw_mask)
        prepared = self.deps.artifacts.prepare_revision(
            page_id=unit.page_id,
            artifact_type=ARTIFACT_MASK,
            payload=payload,
            mime_type=mime,
            suffix=".nmask",
            width=width,
            height=height,
            pipeline_run_id=run.run_id,
            step_run_id=step_run.step_run_id,
            expected_current_revision_id=UNCHECKED,
            options_json=json.dumps(dict(DEFAULT_MASK_PARAMS), sort_keys=True),
            provenance_json=json.dumps(
                {"mask_record": record.as_dict(), "source": MASK_SOURCE_REGION_GEOMETRY},
                sort_keys=True,
            ),
        )
        updates, stages = self._commit_artifacts(unit, {ARTIFACT_MASK: prepared})
        return StepResult(
            target_id=unit.target_id,
            step_type=unit.step_type,
            outputs={
                "mask_revision_id": prepared.revision_id,
                "mask_managed_path": prepared.managed_path,
                "mask_record": record.as_dict(),
            },
            output_target_ids=(unit.target_id,),
            revision_updates=updates,
            next_stage_states=stages,
        )

    def handle_mask_refine(
        self, step_run: StepRun, unit: PlanUnit, run: PipelineRun
    ) -> StepResult:
        self._require_region(unit)
        raw_mask = self._current_mask(unit.page_id)
        settings = self._section(run.settings_snapshot, "inpaint")
        dilate_radius = int(settings.get("dilate_radius", 2))
        erode_radius = int(settings.get("erode_radius", 0))
        final_mask = refine(
            raw_mask, dilate_radius=dilate_radius, erode_radius=erode_radius
        )
        parameters = tuple(
            (key, str(settings.get(key, value)))
            for key, value in DEFAULT_MASK_PARAMS
        )
        record = mask_record(
            raw_mask, final_mask, parameters=parameters, source=MASK_SOURCE_REFINED
        )
        payload, mime, width, height = mask_payload(final_mask)
        prepared = self.deps.artifacts.prepare_revision(
            page_id=unit.page_id,
            artifact_type=ARTIFACT_MASK,
            payload=payload,
            mime_type=mime,
            suffix=".nmask",
            width=width,
            height=height,
            pipeline_run_id=run.run_id,
            step_run_id=step_run.step_run_id,
            expected_current_revision_id=UNCHECKED,
            options_json=json.dumps(dict(parameters), sort_keys=True),
            provenance_json=json.dumps({"mask_record": record.as_dict()}, sort_keys=True),
        )
        updates, stages = self._commit_artifacts(unit, {ARTIFACT_MASK: prepared})
        return StepResult(
            target_id=unit.target_id,
            step_type=unit.step_type,
            outputs={
                "mask_revision_id": prepared.revision_id,
                "mask_managed_path": prepared.managed_path,
                "mask_area_ratio": area_ratio(final_mask),
                "mask_record": record.as_dict(),
            },
            output_target_ids=(unit.target_id,),
            revision_updates=updates,
            next_stage_states=stages,
        )

    def handle_inpaint(
        self, step_run: StepRun, unit: PlanUnit, run: PipelineRun
    ) -> StepResult:
        self._require_region(unit)
        settings = self._section(run.settings_snapshot, "inpaint")
        policy = self._route_policy(settings)
        upstream_clean = self.deps.artifacts.artifact_for(unit.page_id, ARTIFACT_CLEAN)
        upstream_revision = (
            self.deps.artifacts.current_revision_id(upstream_clean)
            if upstream_clean
            else None
        )
        # D06 §22.1 "Original / 当前上游图像": when a Clean revision already
        # exists it is the upstream, so repairing several Regions of one page
        # accumulates instead of overwriting each other's pixels.
        frame = self._upstream_frame(unit.page_id, upstream_clean, upstream_revision)
        current_mask = self._current_mask(unit.page_id)
        features = RouterFeatures(
            mask_area_ratio=area_ratio(current_mask),
            is_speech_bubble=bool(settings.get("is_speech_bubble", True)),
            is_solid_background=bool(settings.get("is_solid_background", True)),
            is_lineart=bool(settings.get("is_lineart", False)),
            has_screentone=bool(settings.get("has_screentone", False)),
            is_color_webtoon=bool(settings.get("is_color_webtoon", False)),
            structure_crossing_mask=bool(settings.get("structure_crossing_mask", False)),
            preferred_quality=str(settings.get("preferred_quality", "balanced")),
            background_complexity=str(settings.get("background_complexity", "low")),
        )
        decision = policy.decide(features)
        request = InpaintStepRequest(
            page_id=unit.page_id,
            region_id=unit.region_id,
            image=frame,
            raw_mask=current_mask,
            final_mask=current_mask,
            features=features,
            policy=policy,
            device="cpu",
            options=(),
            upstream_revision_id=upstream_revision,
            mask_record=mask_record(
                current_mask, current_mask, source=MASK_SOURCE_REFINED
            ),
        )
        step_result = execute_inpaint_step(
            request,
            resolve_provider=lambda candidate: self.deps.registry.resolve(
                CAPABILITY_INPAINT, provider_id_for_route(candidate)
            ),
            decision=decision,
        )
        payload, mime, width, height = artifact_payload_from_frame(step_result.image)
        prepared = self.deps.artifacts.prepare_revision(
            page_id=unit.page_id,
            artifact_type=ARTIFACT_CLEAN,
            payload=payload,
            mime_type=mime,
            suffix=".nmfr",
            width=width,
            height=height,
            source_artifact_revision_id=upstream_revision,
            pipeline_run_id=run.run_id,
            step_run_id=step_run.step_run_id,
            expected_current_revision_id=UNCHECKED,
            options_json=json.dumps(dict(step_result.provenance.get("options", {})), sort_keys=True),
            provenance_json=json.dumps(step_result.provenance, sort_keys=True, default=str),
        )
        updates, stages = self._commit_artifacts(unit, {ARTIFACT_CLEAN: prepared})
        outputs = step_result.as_step_outputs()
        outputs["clean_revision_id"] = prepared.revision_id
        outputs["clean_managed_path"] = prepared.managed_path
        outputs["previous_clean_revision_id"] = prepared.previous_revision_id
        return StepResult(
            target_id=unit.target_id,
            step_type=unit.step_type,
            outputs=outputs,
            output_target_ids=(unit.target_id,),
            revision_updates=updates,
            next_stage_states=stages,
        )

    # ------------------------------------------------------------------
    # shared machinery
    # ------------------------------------------------------------------

    def _commit_artifacts(
        self, unit: PlanUnit, prepared: Mapping[str, PreparedArtifact]
    ) -> tuple[dict[str, str], dict[str, StageState]]:
        """Adopt prepared artifact revisions for a Region-scoped step.

        Artifact-writing steps (segment/mask_refine/inpaint) are always
        Region-scoped here: the planner expands pages into Region units
        (D06 §48), and a Region-less page has no valid OCR stage, so its
        artifact steps are planned ``BLOCKED`` before any handler runs. A
        Region target's ``StepResult`` may only carry ``{"region": ...}``, so
        the page-level Mask/Clean pointer is compare-and-set here with the same
        optimistic guard the pipeline seam would apply (AC-INPAINT-002).
        """
        if not unit.region_id:
            raise ProviderInputError(
                f"step {unit.step_type!r} requires a Region target",
                stage=unit.step_type,
            )
        for artifact in prepared.values():
            self.deps.artifacts.adopt_current(
                artifact_id=artifact.artifact_id,
                revision_id=artifact.revision_id,
                expected_current_revision_id=artifact.previous_revision_id,
            )
        return {}, {unit.step_type: StageState.COMPLETED}

    def _upstream_frame(
        self, page_id: str, clean_artifact_id: str | None, clean_revision_id: str | None
    ) -> ImageFrame:
        """Current Clean revision when present, otherwise the Managed Copy."""
        if not clean_artifact_id or not clean_revision_id:
            return self.deps.images.page_frame(page_id)
        row = self.deps.artifacts.conn.execute(
            "SELECT managed_path FROM artifact_revisions WHERE artifact_revision_id = ?",
            (clean_revision_id,),
        ).fetchone()
        if row is None:
            raise ProviderUnavailable(
                "the current Clean Revision is missing from the database",
                stage=STEP_INPAINT,
            )
        payload = self.deps.artifacts.read_path(row["managed_path"]).read_bytes()
        header, raw = decode_frame_payload(payload)
        return ImageFrame(
            int(header["width"]), int(header["height"]), str(header["mode"]), raw
        )

    def _current_mask(self, page_id: str) -> BooleanMask:
        artifact_id = self.deps.artifacts.artifact_for(page_id, ARTIFACT_MASK)
        if artifact_id is None:
            raise ProviderUnavailable(
                "no Mask Artifact exists for this page; run segment first",
                stage=STEP_INPAINT,
            )
        current = self.deps.artifacts.current_revision_id(artifact_id)
        if current is None:
            raise ProviderUnavailable(
                "the Mask Artifact has no current revision",
                stage=STEP_INPAINT,
            )
        row = self.deps.artifacts.conn.execute(
            "SELECT managed_path FROM artifact_revisions WHERE artifact_revision_id = ?",
            (current,),
        ).fetchone()
        if row is None:
            raise ProviderUnavailable(
                "the current Mask Revision is missing from the database",
                stage=STEP_INPAINT,
            )
        payload = self.deps.artifacts.read_path(row["managed_path"]).read_bytes()
        _header, mask = decode_mask_payload(payload)
        return mask

    def _invoke_provider(self, provider_id: str, capability: str, call):
        provider = self.deps.registry.resolve(capability, provider_id)

        def run():
            return call(provider)

        if self.deps.heavy_runner is not None:
            return self.deps.heavy_runner(
                requires_gpu=bool(getattr(provider, "requires_gpu", False)), call=run
            )
        return run()

    def _chain(self, run: PipelineRun, step_type: str) -> FallbackChain:
        binding = run.provider_binding_snapshot.get(step_type)
        chain = chain_from_binding(binding)
        if chain is None:
            raise ProviderNotConfigured(
                f"no provider binding configured for step {step_type!r}",
                stage=step_type,
            )
        return chain

    def _route_policy(self, settings: Mapping[str, Any]) -> RoutePolicy:
        raw = settings.get("route_policy")
        if raw is None:
            return self.deps.route_policy
        if not isinstance(raw, Mapping):
            raise ProviderInputError(
                "inpaint.route_policy must be a mapping", stage=STEP_INPAINT
            )
        allowed = tuple(
            str(route) for route in raw.get("allowed_routes", ())
        ) or self.deps.route_policy.allowed_routes
        fallbacks = tuple(str(route) for route in raw.get("fallback_routes", ()))
        color_route = raw.get("color_route")
        requirements = {
            str(route): bool(value)
            for route, value in dict(raw.get("requirements", {})).items()
        }
        if color_route and str(color_route) not in allowed:
            allowed = (*allowed, str(color_route))
        return RoutePolicy(
            allowed_routes=allowed,
            fallback_routes=fallbacks,
            color_route=str(color_route) if color_route else None,
            requirements=requirements,
        )

    def _context_pages(
        self, page_id: str, region_id: str, run: PipelineRun
    ) -> tuple[ContextPage, ...]:
        """Neighbouring-page context (D06 §13/§84); never a write target."""
        settings = self._section(run.settings_snapshot, "translate")
        window = int(settings.get("context_pages", DEFAULT_CONTEXT_PAGES))
        if window <= 0:
            return ()
        pages = [
            target
            for target in run.targets
            if target.page_id != page_id
        ]
        context: list[ContextPage] = []
        for target in pages[:window]:
            for region in target.snapshot.region_snapshots():
                if not region.region_id:
                    continue
                live = self.deps.regions.get_region(region.region_id)
                if live is None or not live.text.ocr_text.strip():
                    continue
                context.append(
                    ContextPage(
                        page_id=target.page_id,
                        position="after",
                        text=live.text.ocr_text,
                        reading_order=target.target_order,
                    )
                )
        del region_id
        return tuple(context)

    def _glossary(self, run: PipelineRun) -> dict[str, str]:
        raw = self._section(run.settings_snapshot, "translate").get("glossary", {})
        if not isinstance(raw, Mapping):
            return {}
        return {str(key): str(value) for key, value in raw.items()}

    @staticmethod
    def _section(settings: Mapping[str, Any], name: str) -> Mapping[str, Any]:
        section = settings.get(name)
        return section if isinstance(section, Mapping) else {}

    @staticmethod
    def _require_region(unit: PlanUnit) -> str:
        if not unit.region_id:
            raise ProviderInputError(
                f"step {unit.step_type!r} requires a Region target",
                stage=unit.step_type,
            )
        return unit.region_id

    @staticmethod
    def _device_host() -> str:
        return "cpu"


def _mask_from_geometry(
    frame: ImageFrame, geometry: RegionMaskGeometry, region_id: str
) -> BooleanMask:
    if geometry.boxes:
        return from_boxes(frame.width, frame.height, geometry.boxes)
    if geometry.polygons:
        return from_polygons(frame.width, frame.height, geometry.polygons)
    raise ProviderInputError(
        f"region {region_id!r} has no geometry to build a mask from",
        stage=STEP_SEGMENT,
    )


def _payload_hash(image_bytes: bytes, region_id: str) -> str:
    import hashlib

    digest = hashlib.sha256()
    digest.update(region_id.encode("utf-8"))
    digest.update(image_bytes)
    return digest.hexdigest()


def build_production_handlers(
    *,
    registry: ProviderRegistry,
    regions: RegionRepository,
    region_writer: RegionStepWriter,
    artifacts: ArtifactStepWriter,
    images: PageImageSource,
    geometry: RegionGeometrySource,
    retry_policy: RetryPolicy | None = None,
    heavy_runner: Any = None,
    route_policy: RoutePolicy | None = None,
) -> dict[str, Any]:
    """Convenience wrapper used by ``bootstrap.app``."""
    return ProductionHandlers(
        HandlerDependencies(
            registry=registry,
            regions=regions,
            region_writer=region_writer,
            artifacts=artifacts,
            images=images,
            geometry=geometry,
            retry_policy=retry_policy or RetryPolicy(),
            heavy_runner=heavy_runner,
            route_policy=route_policy
            or RoutePolicy(
                allowed_routes=(ROUTE_SIMPLE_FILL, ROUTE_EDGE_BLEED),
                fallback_routes=(),
                color_route=ROUTE_BRUSHNET,
                requirements={ROUTE_BRUSHNET: False, ROUTE_FLUX_FILL: False},
            ),
        )
    ).as_mapping()


__all__ = [
    "ARTIFACT_CLEAN",
    "ARTIFACT_MASK",
    "HandlerDependencies",
    "PageImageSource",
    "ProductionHandlers",
    "RegionGeometrySource",
    "RegionMaskGeometry",
    "STEP_INPAINT",
    "STEP_MASK_REFINE",
    "STEP_OCR",
    "STEP_SEGMENT",
    "STEP_TRANSLATE",
    "build_production_handlers",
]
