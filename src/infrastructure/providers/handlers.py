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

``detect`` is intentionally absent: this Task owns the
detection/OCR/translation/inpaint capability ports only, and an absent handler
is a provider-availability error, never a fake success. ``color`` /
``term_extract`` / ``render`` were added by TASK-033 (the full-chain closure):
they are assembly-gated — the handler exists but fails closed with a typed
error when its service was not assembled, never a silent degradation.
"""

from __future__ import annotations

import json
import sys
from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from typing import Any, Protocol

from application.editing.ports import RegionRepository
from application.rendering.service import RenderService, RenderStatus
from application.rendering.style import RenderTextStyle
from application.translation.color.service import SourceStyleService
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
from application.translation.knowledge.term_extraction import TermExtractionService
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
from infrastructure.providers.runtime import DEFAULT_ROUTE_POLICY
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
    BooleanMask,
    ImageFrame,
)
from ports.detection.ports import DetectionRequest
from ports.ocr.ports import (
    SCRIPT_JAPANESE,
    TEXT_DIRECTION_HORIZONTAL,
    OcrRequest,
)
from ports.rendering.direction import TextDirection
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

STEP_DETECT = "detect"
STEP_OCR = "ocr"
STEP_COLOR = "color"
STEP_TERM_EXTRACT = "term_extract"
STEP_TRANSLATE = "translate"
STEP_SEGMENT = "segment"
STEP_MASK_REFINE = "mask_refine"
STEP_INPAINT = "inpaint"
STEP_RENDER = "render"

#: CORE-PIPELINE-FIX-1 (empty detection semantics). A page whose detector
#: legitimately finds no text (cover / splash / art-only page) must not fail the
#: whole page task; the step completes with zero Regions and says so in its
#: output. ``fail`` keeps the pre-fix behaviour available for callers that still
#: want a hard ``INVALID_INPUT``. Configured per run through the settings
#: snapshot section ``detect`` (``{"detect": {"empty_detection_policy": "fail"}}``);
#: the key rides the ordinary settings JSON and needs no new settings surface.
EMPTY_DETECTION_POLICY_COMPLETE = "complete"
EMPTY_DETECTION_POLICY_FAIL = "fail"
EMPTY_DETECTION_POLICIES = (
    EMPTY_DETECTION_POLICY_COMPLETE,
    EMPTY_DETECTION_POLICY_FAIL,
)
DEFAULT_EMPTY_DETECTION_POLICY = EMPTY_DETECTION_POLICY_COMPLETE

ARTIFACT_MASK = "mask"
ARTIFACT_CLEAN = "clean"
ARTIFACT_TRANSLATED = "translated"

DEFAULT_CONTEXT_TOKEN_BUDGET = 2000
DEFAULT_CONTEXT_PAGES = 1

#: Batch B-1 (design §4.1): the explicit device preferences. ``auto`` is the
#: historical behaviour and maps to ``preferred_device=None`` (no device
#: planning at all); an unknown/corrupted value must not invent a preference.
_EXPLICIT_DEVICE_PREFERENCES = frozenset({"cpu", "gpu"})


class PageImageSource(Protocol):
    """Supplies decoded pixels; implemented by the bootstrap assembly."""

    def page_frame(self, page_id: str) -> ImageFrame: ...

    def region_crop(
        self, page_id: str, region_id: str
    ) -> tuple[bytes, int, int]: ...

    def page_png(self, page_id: str) -> bytes:
        """The whole Managed Copy page re-encoded as PNG (color step input)."""
        ...


@dataclass(frozen=True)
class RegionMaskGeometry:
    """Region geometry expressed as mask primitives."""

    boxes: tuple[tuple[int, int, int, int], ...] = ()
    polygons: tuple[tuple[tuple[int, int], ...], ...] = ()


class RegionGeometrySource(Protocol):
    def mask_geometry(self, region_id: str) -> RegionMaskGeometry: ...


@dataclass
class HandlerDependencies:
    """Everything the handlers may use; all of it is injected.

    ``source_styles`` / ``terms`` / ``render_service`` are the TASK-033
    assembly points: ``None`` keeps the assembly buildable everywhere, and the
    matching handlers then fail closed with a typed error instead of
    degrading silently (AC-COLOR/TERM/RENDER fail-closed).
    """

    registry: ProviderRegistry
    regions: RegionRepository
    region_writer: RegionStepWriter
    artifacts: ArtifactStepWriter
    images: PageImageSource
    geometry: RegionGeometrySource
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    heavy_runner: Any = None  # DeviceManager.run_guarded, optional
    route_policy: RoutePolicy = field(default_factory=RoutePolicy)
    source_styles: SourceStyleService | None = None  # TASK-033 color
    terms: TermExtractionService | None = None  # TASK-033 term_extract
    render_service: RenderService | None = None  # TASK-033 render
    #: TASK-049 AC ①②: the detection adapter and the application-layer
    #: Region writer for the ``detect`` step. ``None`` (every pre-TASK-049
    #: construction) keeps the assembly buildable, and ``handle_detect`` then
    #: fails closed with a typed error instead of degrading silently.
    detector: Any = None  # ports.detection.ports.DetectionProvider
    # M2-SFX-PROD-1: the 5th argument carries the candidate's anonymous
    # provider_label so the assembly can dispatch the ``sfx-`` prefix to
    # RegionType.SFX (contract zero-change: RegionCandidate keeps its slots).
    plugins: Any = None
    region_creator: Any = None  # (page_id, polygon, reading_order, provenance, provider_label) -> region_id


class ProductionHandlers:
    """Build the ``step_type -> handler`` mapping injected into the pipeline."""

    def __init__(self, dependencies: HandlerDependencies) -> None:
        self.deps = dependencies
        self._handlers: dict[str, Any] = {
            step_type: self._typed(handler)
            for step_type, handler in (
                (STEP_DETECT, self.handle_detect),
                (STEP_OCR, self.handle_ocr),
                (STEP_COLOR, self.handle_color),
                (STEP_TERM_EXTRACT, self.handle_term_extract),
                (STEP_TRANSLATE, self.handle_translate),
                (STEP_SEGMENT, self.handle_segment),
                (STEP_MASK_REFINE, self.handle_mask_refine),
                (STEP_INPAINT, self.handle_inpaint),
                (STEP_RENDER, self.handle_render),
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
    # detect (TASK-049 AC ①②: page-level input face for region steps)
    # ------------------------------------------------------------------

    def handle_detect(
        self, step_run: StepRun, unit: PlanUnit, run: PipelineRun
    ) -> StepResult:
        """Detect text regions on the page and land them as Regions.

        Fail-closed ladder (TASK-049 AC ①, widened by CORE-PIPELINE-FIX-1):

        - no detector / no region writer wired at assembly →
          ``PROVIDER_NOT_CONFIGURED`` (the same taxonomy slot OCR_REGION uses
          when no OCR provider is ready — the failure stays at the capability
          gap, never at a fabricated success);
        - the adapter reports zero candidates → **completed with zero Regions**
          by default (a cover / splash / art-only page is a legitimate empty
          detection, not invalid input). The output records
          ``detection.empty_detection/empty_detection_policy`` and stderr says
          so, so the outcome is observable, never silent. A run that wants the
          old hard failure sets ``detect.empty_detection_policy = "fail"`` and
          gets the previous typed ``INVALID_INPUT``;
        - the adapter raised → typed provider error via ``_typed``.

        Input validation is untouched: a frame the provider rejects still fails
        with the provider's own typed code.

        Idempotency: a page that already has live Regions reuses them (in
        ``reading_order``), so re-planned page tasks never pile up duplicate
        machine regions. The Regions themselves are written by the
        application-layer ``region_creator`` (assembly-injected; TASK-049 AC ②
        reuses :meth:`RegionEditingService.create_region` — no second Region
        write path exists).
        """
        if self.deps.detector is None or self.deps.region_creator is None:
            raise ProviderNotConfigured(
                "no detection provider / region writer is wired at assembly",
                stage=STEP_DETECT,
            )
        live = [
            region
            for region in self.deps.regions.list_regions(unit.page_id)
            if not region.deleted
        ]
        if live:
            region_ids = tuple(
                region.region_id
                for region in sorted(live, key=lambda region: region.reading_order)
            )
            provenance = {"reused_existing_regions": len(region_ids)}
            return self._detect_result(unit, region_ids, provenance)

        frame = self.deps.images.page_frame(unit.page_id)
        request = DetectionRequest(
            page_id=unit.page_id,
            image_bytes=frame.data,
            width=frame.width,
            height=frame.height,
        )
        request = self._hook_request("detect", request, run)
        detection = self.deps.detector.detect(request)
        if self.deps.plugins is not None:
            self.deps.plugins.run_hook("after_detect", {
                "run_id": run.run_id, "page_id": unit.page_id,
                "candidate_count": len(detection.page_global_candidates()),
            })
        candidates = detection.page_global_candidates()
        if not candidates:
            # CORE-PIPELINE-FIX-1: an empty detection is a legitimate outcome on
            # a text-free page. Default = complete with zero Regions (observable
            # in the step output + stderr); ``empty_detection_policy="fail"``
            # keeps the pre-fix INVALID_INPUT contract available.
            policy = self._empty_detection_policy(run)
            if policy == EMPTY_DETECTION_POLICY_FAIL:
                raise ProviderInputError(
                    f"detector returned no candidates for page {unit.page_id!r}",
                    stage=STEP_DETECT,
                )
            provenance = dict(detection.provenance())
            provenance.update(
                {
                    "candidate_count": 0,
                    "empty_detection": True,
                    "empty_detection_policy": policy,
                }
            )
            self._log_empty_detection(unit.page_id, policy)
            return self._detect_result(unit, (), provenance)
        provenance = detection.provenance()
        region_ids = tuple(
            self.deps.region_creator(
                unit.page_id,
                candidate.polygon,
                candidate.reading_order or index,
                provenance,
                # M2-SFX-PROD-1: the label rides along so the assembly's
                # region creator can dispatch the ``sfx-`` prefix to
                # RegionType.SFX (labels stay anonymous provider placeholders).
                candidate.provider_label,
            )
            for index, candidate in enumerate(candidates, start=1)
        )
        return self._detect_result(unit, region_ids, provenance)

    def _hook_request(self, stage, request, run):
        if self.deps.plugins is None:
            return request
        values = {"options": dict(request.options)}
        if stage == "ocr":
            values.update(script=request.script, direction=request.direction)

        def validate(candidate):
            options = candidate["options"]
            if not isinstance(options, dict) or not all(
                isinstance(k, str) and isinstance(v, str) for k, v in options.items()
            ):
                raise ValueError("options must contain string pairs")
            try:
                replace(request, **{**candidate, "options": tuple(options.items())})
            except ProviderError as error:
                raise ValueError(str(error)) from error

        values = self.deps.plugins.apply_input("before_" + stage, {
            "run_id": run.run_id, "page_id": request.page_id, "input": values,
        }, validate)
        return replace(request, **{**values, "options": tuple(values["options"].items())})

    @staticmethod
    def _detect_result(
        unit: PlanUnit, region_ids: tuple[str, ...], provenance: dict
    ) -> StepResult:
        return StepResult(
            target_id=unit.target_id,
            step_type=STEP_DETECT,
            outputs={"region_ids": region_ids, "detection": provenance},
            output_target_ids=(unit.target_id,),
        )

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

        request = self._hook_request("ocr", request, run)
        outcome = run_chain(
            chain,
            lambda provider_id: self._invoke_provider(
                provider_id,
                CAPABILITY_OCR,
                lambda provider: provider.recognize(request),
                run=run,
            ),
            policy=self._retry_policy_for_run(run),
            payload_hash_provider=lambda: _payload_hash(request.image_bytes, request.region_id),
        )
        result = outcome.result
        if self.deps.plugins is not None:
            self.deps.plugins.run_hook("after_ocr", {
                "run_id": run.run_id, "page_id": unit.page_id,
                "region_id": region_id, "text": result.text,
            })
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
            # M2-SFX-SEM-1: carry the region type into the provider request so
            # the prompt can specialize SFX onomatopoeia (widening default
            # keeps every other caller unchanged).
            regions=[
                RegionInput(
                    region_id, source_text, region_type=region.region_type.value
                )
            ],
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
                run=run,
            ),
            policy=self._retry_policy_for_run(run),
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
        # TASK-034 AC ①: the Run-time policy comes from the same single entry
        # point as the assembly-time one; only the explicit `default` differs
        # (R-1) — here it is the policy the runtime was assembled with.
        policy = RoutePolicy.from_settings(
            run.settings_snapshot, default=self.deps.route_policy
        )
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
    # Color / Term Extract / Render (TASK-033 full-chain closure)
    # ------------------------------------------------------------------

    def handle_color(
        self, step_run: StepRun, unit: PlanUnit, run: PipelineRun
    ) -> StepResult:
        """D06 §8 source-style analysis: judgement only, no Region write.

        Fail-closed: without an assembled analyzer this raises instead of
        reporting a fallback default (AC-COLOR). ``needs_fallback`` is the
        *output* of the frozen reliability rule, recorded in provenance —
        the render step applies it, this step only measures.

        CORE-PIPELINE-FIX-1: the production assembly wires the real
        :class:`PillowSourceStyleAnalyzer` (the previous stub had no ``analyze``
        at all, so every color unit died with ``AttributeError``). An analyzer
        failure is re-raised as a typed :class:`ProviderError` so the StepRun
        keeps a diagnosable code (``PROVIDER_FAILED``) instead of a bare
        ``ValueError``/``AttributeError``.
        """
        region_id = self._require_region(unit)
        if self.deps.source_styles is None:
            raise ProviderNotConfigured(
                "no source style analyzer assembled for the color step",
                stage=STEP_COLOR,
            )
        region = self.deps.regions.get_region(region_id)
        if region is None or region.deleted:
            raise ProviderInputError(
                f"region {region_id!r} is not available", stage=STEP_COLOR
            )
        original_png = self.deps.images.page_png(unit.page_id)
        box = region.geometry.bbox.as_tuple()
        try:
            result = self.deps.source_styles.extract(original_png, box)
        except ProviderError:
            raise
        except Exception as error:  # noqa: BLE001 - analyzer contract: any failure is a provider failure
            raise ProviderError(
                f"source style analysis failed: {error}", stage=STEP_COLOR
            ) from error
        style = result.style
        outputs = {
            "source_style": {
                "detected_source_font_size": style.detected_source_font_size,
                "source_font_size_confidence": style.source_font_size_confidence,
                "text_color": style.text_color,
                "stroke_hint_color": style.stroke_hint_color,
                "background_color": style.background_color,
                "direction_hint": (
                    style.direction_hint.value if style.direction_hint else None
                ),
            },
            "needs_fallback": result.needs_fallback,
            "provenance": {
                "step": STEP_COLOR,
                "ai_invoked": False,  # structural: pixel analysis only
                "device_host": self._device_host(),
                "box": list(box),
                "fallback_to_default": result.needs_fallback,
            },
        }
        return StepResult(
            target_id=unit.target_id,
            step_type=unit.step_type,
            outputs=outputs,
            output_target_ids=(unit.target_id,),
            # judgement-only step: no Region revision, no pointer move.
            revision_updates={},
            next_stage_states={unit.step_type: StageState.COMPLETED},
        )

    def handle_term_extract(
        self, step_run: StepRun, unit: PlanUnit, run: PipelineRun
    ) -> StepResult:
        """D06 §12 term candidates from the OCR text; knowledge sources are
        read-only (glossary settings + optional TM scan), the formal glossary
        and TM data are never modified and no request leaves the process
        (TASK-033 AC ②). Fail-closed without the assembled service.
        """
        region_id = self._require_region(unit)
        if self.deps.terms is None:
            raise ProviderNotConfigured(
                "no term extraction service assembled for the term_extract step",
                stage=STEP_TERM_EXTRACT,
            )
        region = self.deps.regions.get_region(region_id)
        if region is None or region.deleted:
            raise ProviderInputError(
                f"region {region_id!r} is not available", stage=STEP_TERM_EXTRACT
            )
        source_text = region.text.ocr_text
        if not source_text.strip():
            raise ProviderInputError(
                "region has no OCR text to extract terms from",
                stage=STEP_TERM_EXTRACT,
            )
        glossary = self._glossary(run)
        book_id = next(
            (
                target.snapshot.book_id
                for target in run.targets
                if target.target_id == unit.target_id
            ),
            None,
        )
        result = self.deps.terms.extract(
            source_text, glossary=glossary or None, book_id=book_id
        )
        outputs = {
            "term_candidates": [
                {
                    "term": candidate.term,
                    "source": candidate.source,
                    "occurrences": candidate.occurrences,
                    "suggested_target": candidate.suggested_target,
                }
                for candidate in result.candidates
            ],
            "provenance": {
                **result.provenance,
                "book_id": book_id,
                "device_host": self._device_host(),
            },
        }
        return StepResult(
            target_id=unit.target_id,
            step_type=unit.step_type,
            outputs=outputs,
            output_target_ids=(unit.target_id,),
            # candidates only: no Region revision, no glossary/TM write.
            revision_updates={},
            next_stage_states={unit.step_type: StageState.COMPLETED},
        )

    def handle_render(
        self, step_run: StepRun, unit: PlanUnit, run: PipelineRun
    ) -> StepResult:
        """D06 §23/§47 render through the application-layer RenderService.

        **Single writer (TASK-033 P0 constraint)**: ``RenderService`` commits
        the page-level ``translated`` pointer itself via the atomic
        compare-and-write seam (``_commit_translated`` → ``commit_revision``
        with ``expected_current_revision_id``). This handler therefore returns
        ``revision_updates={}`` — the pipeline seam must not flip the same
        pointer a second time — and the committed-once property is asserted in
        ``tests/providers/test_full_chain.py``.

        Fail-closed: missing Clean / locked region / skip policy / composition
        conflicts surface as the RenderService's typed error codes, never as a
        silent no-op success.
        """
        region_id = self._require_region(unit)
        if self.deps.render_service is None:
            raise ProviderNotConfigured(
                "no render service assembled for the render step",
                stage=STEP_RENDER,
            )
        # SETTINGS-OPEN-A-1 AC2: the persisted (Run-frozen) ``typeset`` section
        # is the render default style; Region-persisted values still win
        # (D03 §11.4). No section -> None -> the historical behaviour.
        outcome = self.deps.render_service.rerender_region(
            region_id,
            style_defaults=typeset_style_defaults(run.settings_snapshot),
        )
        if outcome.status is not RenderStatus.COMMITTED:
            raise StepExecutionError(
                outcome.error_code or "RENDER_FAILED",
                outcome.detail or f"render outcome={outcome.status}",
            )
        outputs = {
            "render_status": outcome.status,
            "translated_artifact_id": outcome.artifact_id,
            "translated_revision_no": outcome.revision_no,
            "translated_managed_path": outcome.managed_path,
            "region_reports": [
                {
                    "region_id": report.region_id,
                    "status": report.status,
                    "skip_reason": report.skip_reason,
                    "final_font_size": report.final_font_size,
                    "font_substituted": report.font_substituted,
                }
                for report in outcome.reports
            ],
            "provenance": (
                json.loads(outcome.provenance_json)
                if outcome.provenance_json
                else {}
            ),
        }
        return StepResult(
            target_id=unit.target_id,
            step_type=unit.step_type,
            outputs=outputs,
            output_target_ids=(unit.target_id,),
            # RenderService is the sole writer of the `translated` pointer.
            revision_updates={},
            next_stage_states={unit.step_type: StageState.COMPLETED},
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

    def _invoke_provider(
        self, provider_id: str, capability: str, call, *, run: PipelineRun
    ):
        provider = self.deps.registry.resolve(capability, provider_id)

        def invoke():
            return call(provider)

        if self.deps.heavy_runner is not None:
            # Review B1: the GPU declarations live on the ``ProviderDescriptor``,
            # not on the provider instance (``MangaOcrProvider`` et al. do not
            # repeat them), so reading the resolved instance made
            # ``supports_cpu_fallback`` permanently False for every production
            # provider and the user's CPU-fallback switch a no-op. The descriptor
            # is the single declaration source; a registry that cannot answer
            # (test doubles) keeps the historical instance-attribute fallback.
            descriptor = self.deps.registry.descriptor(
                provider_id, capability=capability
            )
            # SETTINGS-OPEN-B-1 AC2: the Run-frozen ``model_gpu`` section picks
            # the device. ``auto`` (and a missing/corrupted section) keeps the
            # historical call shape: ``preferred_device=None`` makes the
            # runtime pass straight through to ``run_guarded(requires_gpu,
            # call)`` -- no ``DeviceManager.plan`` call, zero behaviour change.
            settings = self._section(run.settings_snapshot, "model_gpu")
            preference = settings.get("device_preference")
            preferred_device = (
                preference if preference in _EXPLICIT_DEVICE_PREFERENCES else None
            )
            raw_fallback = settings.get("allow_cpu_fallback")
            # D06 §82: the user switch ANDs with the provider's own declaration
            # inside ``DeviceManager.plan``; an absent/malformed switch keeps
            # the design default (allowed).
            allow_cpu_fallback = (
                raw_fallback if isinstance(raw_fallback, bool) else True
            )
            requires_gpu = (
                descriptor.requires_gpu
                if descriptor is not None
                else bool(getattr(provider, "requires_gpu", False))
            )
            supports_cpu_fallback = (
                descriptor.supports_cpu_fallback
                if descriptor is not None
                else bool(getattr(provider, "supports_cpu_fallback", False))
            )
            # Review M3: a remote / CPU-only provider never uses the local
            # device, so an explicit ``gpu`` preference must not turn its
            # calls into ``DeviceUnavailable`` (translation / vision OCR are
            # remote). Only GPU providers take the preference; every other
            # provider keeps the historical auto path.
            if not requires_gpu:
                preferred_device = None
            return self.deps.heavy_runner(
                requires_gpu=bool(requires_gpu),
                call=invoke,
                preferred_device=preferred_device,
                allow_cpu_fallback=allow_cpu_fallback,
                supports_cpu_fallback=bool(supports_cpu_fallback),
            )
        return invoke()

    def _retry_policy_for_run(self, run: PipelineRun) -> RetryPolicy:
        """Derive this Run's retry policy from its frozen ``tasks`` section.

        SETTINGS-OPEN-B-1 AC3 (design §4.2): ``retry_max_attempts`` /
        ``retry_backoff_seconds`` replace the assembly-time policy for Runs
        started after the write. An absent section (or an absent key) keeps
        :attr:`HandlerDependencies.retry_policy`'s value, and with no usable
        key at all the very same policy object is returned, so an unset
        section is byte-for-byte equivalent to the historical behaviour.

        The write gate already rejects out-of-range values, but a frozen Run
        can be replayed from older/corrupted storage: a numeric value is
        clamped into the accepted domain (the ``runtime._retry_policy``
        clamping discipline), and a non-numeric one is ignored (base value
        kept) instead of crashing the step. A snapshot that is not a mapping
        (independent/replayed handler seam) is treated as an absent section.
        """
        base = self.deps.retry_policy
        section = self._section(run.settings_snapshot, "tasks")
        max_attempts = _clamped_int(
            section.get("retry_max_attempts"), minimum=1, maximum=3
        )
        backoff_seconds = _clamped_number(
            section.get("retry_backoff_seconds"), minimum=0.1, maximum=30.0
        )
        if max_attempts is None and backoff_seconds is None:
            return base
        return RetryPolicy(
            max_attempts=(
                base.max_attempts if max_attempts is None else max_attempts
            ),
            backoff_seconds=(
                base.backoff_seconds if backoff_seconds is None else backoff_seconds
            ),
            # The UI exposes only the two knobs above: every other field of the
            # assembled policy (explicit retry codes, the Retry-After consumer)
            # stays exactly as it was.
            retry_codes=base.retry_codes,
            retry_after_provider=getattr(base, "retry_after_provider", None),
        )

    def _chain(self, run: PipelineRun, step_type: str) -> FallbackChain:
        binding = run.provider_binding_snapshot.get(step_type)
        chain = chain_from_binding(binding)
        if chain is None:
            raise ProviderNotConfigured(
                f"no provider binding configured for step {step_type!r}",
                stage=step_type,
            )
        return chain

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
    def _section(settings: Mapping[str, Any] | None, name: str) -> Mapping[str, Any]:
        # Review m1: a handler is an independent seam -- a replayed/testing
        # caller may hand over ``None``/a non-mapping snapshot. Every consumer
        # documents "absent section = defaults", so a non-mapping snapshot is
        # an absent section, never an AttributeError.
        if not isinstance(settings, Mapping):
            return {}
        section = settings.get(name)
        return section if isinstance(section, Mapping) else {}

    @classmethod
    def _empty_detection_policy(cls, run: PipelineRun) -> str:
        """Resolve ``detect.empty_detection_policy`` for this run.

        Unknown / malformed values fall back to the default (``complete``) and
        say so on stderr: an unrecognised knob must never turn into a silent
        semantic change, and it must never turn a text-free page into a failure.
        """
        raw = cls._section(run.settings_snapshot, "detect").get(
            "empty_detection_policy", DEFAULT_EMPTY_DETECTION_POLICY
        )
        value = raw.strip().lower() if isinstance(raw, str) else ""
        if value in EMPTY_DETECTION_POLICIES:
            return value
        print(
            "[core.detect] ignoring unknown empty_detection_policy "
            f"{raw!r}; using {DEFAULT_EMPTY_DETECTION_POLICY!r}",
            file=sys.stderr,
            flush=True,
        )
        return DEFAULT_EMPTY_DETECTION_POLICY

    @staticmethod
    def _log_empty_detection(page_id: str, policy: str) -> None:
        # Observability without a wire change: the same marker also lands in the
        # step output (``detection.empty_detection``), so a run that completed
        # with zero Regions is never indistinguishable from a run that detected
        # nothing by accident.
        print(
            f"[core.detect] page {page_id!r} produced 0 candidates; "
            f"empty_detection_policy={policy} -> step completed with 0 regions",
            file=sys.stderr,
            flush=True,
        )

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


#: Batch-A ``typeset`` values this reader accepts; the Core write gate
#: (``bootstrap.settings_sections``) already enforces the same domains, so
#: these checks only shield a render from corrupted/legacy stored values.
#: ``text_align`` stays left/center: the compositors do not implement ``right``.
_TYPESET_TEXT_ALIGNS = frozenset({"left", "center"})
_TEXT_DIRECTIONS = {direction.value: direction for direction in TextDirection}


def typeset_style_defaults(settings: Mapping[str, Any]) -> RenderTextStyle | None:
    """Derive the render default style from a Run's frozen ``typeset`` section.

    SETTINGS-OPEN-A-1 AC2: the persisted typeset keys feed
    ``RenderService.style_defaults``; fields absent from the whitelist (e.g.
    ``font_family``) keep the D03 §11.6 defaults, and a missing/non-mapping
    section returns ``None`` (historical render behaviour, byte-for-byte).

    The Core write gate validates every value before persistence, but a frozen
    Run can be replayed from older/corrupted storage. A malformed field is
    therefore skipped (it keeps its default) rather than crashing the render
    step; ``RenderTextStyle.__post_init__`` re-validates the assembled value.
    """
    section = settings.get("typeset") if isinstance(settings, Mapping) else None
    if not isinstance(section, Mapping) or not section:
        return None
    kwargs: dict[str, Any] = {}
    for key in ("text_color", "stroke_color"):
        value = section.get(key)
        if _is_hex_color(value):
            kwargs[key] = value
    for key, target in (
        ("stroke_enabled", "stroke_enabled"),
        ("auto_font_size", "auto_font_size_enabled"),
    ):
        value = section.get(key)
        if isinstance(value, bool):
            kwargs[target] = value
    stroke_width = _bounded_number(section.get("stroke_width"), 0.0, 20.0)
    if stroke_width is not None:
        kwargs["stroke_width"] = stroke_width
    line_spacing = _bounded_number(section.get("line_spacing"), 1.0, 3.0)
    if line_spacing is not None:
        kwargs["line_spacing"] = line_spacing
    text_align = section.get("text_align")
    if isinstance(text_align, str) and text_align in _TYPESET_TEXT_ALIGNS:
        kwargs["text_align"] = text_align
    raw_direction = section.get("text_direction")
    direction = (
        _TEXT_DIRECTIONS.get(raw_direction)
        if isinstance(raw_direction, str)
        else None
    )
    # An unknown direction falls back to the RenderTextStyle default (AUTO),
    # never to a guessed horizontal/vertical value.
    if direction is not None:
        kwargs["text_direction"] = direction
    font_size_offset = section.get("font_size_offset")
    if (
        isinstance(font_size_offset, int)
        and not isinstance(font_size_offset, bool)
        and -5 <= font_size_offset <= 5
    ):
        kwargs["font_size_offset"] = font_size_offset
    manual_font_size = section.get("manual_font_size")
    if manual_font_size is not None:
        manual = _bounded_number(manual_font_size, 1.0, 500.0)
        if manual is not None:
            kwargs["manual_font_size"] = manual
    if not kwargs:
        return None
    try:
        return RenderTextStyle(**kwargs)
    except (TypeError, ValueError):
        # Defense in depth only: skip the whole section instead of letting a
        # corrupted field fail the render step.
        return None


def _is_hex_color(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 7
        and value.startswith("#")
        and all(digit in "0123456789abcdefABCDEF" for digit in value[1:])
    )


def _bounded_number(value: Any, minimum: float, maximum: float) -> float | None:
    """Return ``value`` as a float inside the inclusive bounds, else ``None``."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    if not minimum <= number <= maximum:
        return None
    return number


def _clamped_int(value: Any, *, minimum: int, maximum: int) -> int | None:
    """Return ``value`` clamped into the inclusive bounds, else ``None``.

    ``None`` (not a real integer: booleans, strings, absent keys) lets the
    caller keep its own default; an out-of-range number is clamped like
    ``runtime._retry_policy`` clamps the legacy ``providers.retry`` value.
    """
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return min(maximum, max(minimum, value))


def _clamped_number(
    value: Any, *, minimum: float, maximum: float
) -> float | None:
    """Float flavour of :func:`_clamped_int` (same ``None`` contract)."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return min(maximum, max(minimum, float(value)))


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
    source_styles: SourceStyleService | None = None,
    terms: TermExtractionService | None = None,
    render_service: RenderService | None = None,
    detector: Any = None,
    region_creator: Any = None,
    plugins: Any = None,
) -> dict[str, Any]:
    """Convenience wrapper used by ``bootstrap.app``.

    The TASK-033 services stay optional at the assembly boundary: an omitted
    service still assembles, and its handler then fails closed at run time
    (TASK-033 AC ①/②/③).  ``detector`` / ``region_creator`` are the
    TASK-049 ``detect`` step's optional pair — unwired, ``detect`` fails
    closed with ``PROVIDER_NOT_CONFIGURED``.
    """
    return ProductionHandlers(
        HandlerDependencies(
            plugins=plugins,
            registry=registry,
            regions=regions,
            region_writer=region_writer,
            artifacts=artifacts,
            images=images,
            geometry=geometry,
            retry_policy=retry_policy or RetryPolicy(),
            heavy_runner=heavy_runner,
            # TASK-034 AC ①: reuse the one default policy constant instead of a
            # third hand-written literal (the runtime does not import this
            # module, so this import direction has no cycle).
            route_policy=route_policy or DEFAULT_ROUTE_POLICY,
            source_styles=source_styles,
            terms=terms,
            render_service=render_service,
            detector=detector,
            region_creator=region_creator,
        )
    ).as_mapping()


__all__ = [
    "ARTIFACT_CLEAN",
    "ARTIFACT_MASK",
    "ARTIFACT_TRANSLATED",
    "HandlerDependencies",
    "PageImageSource",
    "ProductionHandlers",
    "RegionGeometrySource",
    "RegionMaskGeometry",
    "STEP_COLOR",
    "STEP_DETECT",
    "STEP_INPAINT",
    "STEP_MASK_REFINE",
    "STEP_OCR",
    "STEP_RENDER",
    "STEP_SEGMENT",
    "STEP_TERM_EXTRACT",
    "STEP_TRANSLATE",
    "build_production_handlers",
    "typeset_style_defaults",
]
