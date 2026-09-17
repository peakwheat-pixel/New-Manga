"""Inpaint Step orchestration (D06 §21/§22, AC-INPAINT-002~004).

The Step owns the *contract*, not the pixels:

- it asks the Router for a route and refuses to run when the Router blocks;
- it only ever tries the routes the configured policy names — the fallback
  chain that actually happened is part of the provenance (D06 §51/§53);
- it re-verifies non-target protection on the returned image before the caller
  may persist anything (a violation fails the step, nothing is committed);
- it never overwrites an existing Clean revision: the result names the
  upstream revision it was derived from, and the caller commits a **new**
  ArtifactRevision (AC-INPAINT-002).

The result carries provider, model, options, router reason and fallback chain,
which is exactly the AC-INPAINT-003 provenance set.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field

from infrastructure.providers.inpaint_router import (
    RoutePolicy,
    RouterDecision,
    RouterFeatures,
    require_route,
)
from infrastructure.providers.inpaint_routes import (
    protected_pixel_violations,
    route_gate,
)
from ports.inpaint.ports import (
    BooleanMask,
    ImageFrame,
    InpaintProvider,
    InpaintRequest,
    InpaintResult,
    MaskRecord,
)
from ports.providers.errors import (
    NonTargetWriteViolation,
    ProviderInputError,
    ProviderNotImplemented,
)

ProviderResolver = Callable[[str], InpaintProvider]


@dataclass(frozen=True)
class InpaintStepRequest:
    """Everything the Inpaint Step needs for one target."""

    page_id: str
    image: ImageFrame
    raw_mask: BooleanMask
    final_mask: BooleanMask
    features: RouterFeatures
    policy: RoutePolicy
    region_id: str | None = None
    device: str = ""
    device_provenance: Mapping[str, object] = field(default_factory=dict)
    options: tuple[tuple[str, str], ...] = ()
    upstream_revision_id: str | None = None
    mask_record: MaskRecord | None = None

    def __post_init__(self) -> None:
        if (self.image.width, self.image.height) != (
            self.final_mask.width,
            self.final_mask.height,
        ):
            raise ProviderInputError(
                "mask and image dimensions differ", stage="inpaint"
            )
        if not self.final_mask.covers(self.raw_mask):
            raise ProviderInputError(
                "final mask must cover the raw mask", stage="inpaint"
            )


@dataclass(frozen=True)
class InpaintStepResult:
    """D06 §22.2 output: a new Clean image plus full provenance."""

    page_id: str
    region_id: str | None
    image: ImageFrame
    route: str
    provenance: dict
    mask_record: MaskRecord | None
    upstream_revision_id: str | None
    new_revision_required: bool = True
    masked_pixel_count: int = 0

    def as_step_outputs(self) -> dict:
        """The mapping the pipeline persists on the StepRun."""
        return {
            "route": self.route,
            "upstream_revision_id": self.upstream_revision_id,
            "new_revision_required": self.new_revision_required,
            "masked_pixel_count": self.masked_pixel_count,
            "provenance": dict(self.provenance),
        }


def execute_inpaint_step(
    request: InpaintStepRequest,
    *,
    resolve_provider: ProviderResolver,
    decision: RouterDecision | None = None,
) -> InpaintStepResult:
    """Run the route the Router selected, with explicit fallback only."""
    router_decision = decision or request.policy.decide(request.features)
    route = require_route(router_decision)
    routes = _runnable_routes(route, router_decision.fallback_routes)
    if not routes:
        raise ProviderNotImplemented(
            f"no runnable route for {route!r}", stage="inpaint"
        )

    attempts: list[str] = []
    last_error: Exception | None = None
    for candidate in routes:
        attempts.append(candidate)
        provider = resolve_provider(candidate)
        inpaint_request = InpaintRequest(
            page_id=request.page_id,
            region_id=request.region_id,
            image=request.image,
            raw_mask=request.raw_mask,
            final_mask=request.final_mask,
            route=candidate,
            mask_record=request.mask_record
            or MaskRecord(
                parameters=(),
                raw_area=request.raw_mask.area,
                final_area=request.final_mask.area,
                raw_bbox=request.raw_mask.bbox(),
                final_bbox=request.final_mask.bbox(),
                final_covers_raw=request.final_mask.covers(request.raw_mask),
            ),
            device=request.device,
            options=request.options,
        )
        try:
            result = provider.inpaint(inpaint_request)
        except Exception as error:  # noqa: BLE001 - chain re-raises typed
            last_error = error
            continue
        return _finalise(request, result, router_decision, attempts)

    if last_error is None:  # pragma: no cover - routes is never empty
        raise ProviderNotImplemented("no inpaint route was attempted", stage="inpaint")
    raise last_error


def _runnable_routes(route: str, fallbacks: tuple[str, ...]) -> tuple[str, ...]:
    routes: list[str] = []
    for candidate in (route, *fallbacks):
        if candidate in routes:
            continue
        if route_gate(candidate).runnable:
            routes.append(candidate)
    return tuple(routes)


def _finalise(
    request: InpaintStepRequest,
    result: InpaintResult,
    decision: RouterDecision,
    attempts: list[str],
) -> InpaintStepResult:
    if (result.image.width, result.image.height) != (
        request.image.width,
        request.image.height,
    ):
        raise ProviderInputError(
            "provider changed the image dimensions", stage="inpaint"
        )
    violations = protected_pixel_violations(
        request.image, result.image, request.final_mask
    )
    if violations:
        raise NonTargetWriteViolation(
            f"inpaint changed {len(violations)} pixel(s) outside the mask,"
            f" e.g. {violations[:5]}",
            provider_id=result.provider_id,
            stage="inpaint",
        )

    provenance = dict(result.provenance())
    provenance.update(decision.as_provenance())
    provenance["fallback_chain"] = list(attempts)
    provenance["used_fallback"] = len(attempts) > 1
    provenance["upstream_revision_id"] = request.upstream_revision_id
    provenance["device_provenance"] = dict(request.device_provenance)
    provenance["new_revision_required"] = True

    return InpaintStepResult(
        page_id=request.page_id,
        region_id=request.region_id,
        image=result.image,
        route=result.route,
        provenance=provenance,
        mask_record=result.mask_record or request.mask_record,
        upstream_revision_id=request.upstream_revision_id,
        masked_pixel_count=request.final_mask.area,
    )
