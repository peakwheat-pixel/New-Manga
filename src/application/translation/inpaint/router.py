"""Inpaint Router: feature-driven route selection with full provenance.

D06 §21 defines the strategy; D06 §51 allows exactly two fallback sources —
explicit user configuration and routes the architecture itself defines. The
router therefore never "picks whatever is available":

- the **configured route policy** (``allowed_routes``) bounds every decision;
- the chosen route must also be *runnable* (implemented + dependencies met),
  otherwise the decision is BLOCKED with the reason, and the provenance still
  records which candidates were considered and why each was rejected;
- the colored-Webtoon policy (AC-INPAINT-004) selects the color route when the
  user configured it, and records that choice — selecting a learned route does
  not make its execution measurable in this environment.

Provenance fields follow AC-INPAINT-003: provider, model, options,
router_reason and fallback_chain are all carried out of the decision.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from application.translation.inpaint.route_catalog import route_gate
from ports.inpaint.ports import (
    ROUTE_AOT_GAN,
    ROUTE_BRUSHNET,
    ROUTE_EDGE_BLEED,
    ROUTE_FLUX_FILL,
    ROUTE_MANGA_LAMA,
    ROUTE_SIMPLE_FILL,
)
from ports.providers.errors import ProviderInputError, ProviderNotImplemented

QUALITY_FAST = "fast"
QUALITY_BALANCED = "balanced"
QUALITY_QUALITY = "quality"
ALL_QUALITIES = frozenset({QUALITY_FAST, QUALITY_BALANCED, QUALITY_QUALITY})

COMPLEXITY_LOW = "low"
COMPLEXITY_MEDIUM = "medium"
COMPLEXITY_HIGH = "high"
ALL_COMPLEXITIES = frozenset({COMPLEXITY_LOW, COMPLEXITY_MEDIUM, COMPLEXITY_HIGH})

#: A "small, solid" region the Simple Fill baseline is documented for.
SOLID_AREA_RATIO = 0.02

DECISION_ROUTE = "route"
DECISION_BLOCKED = "blocked"


@dataclass(frozen=True)
class RouterFeatures:
    """D06 §21 router inputs, computed from the mask and the source image."""

    mask_area_ratio: float
    is_speech_bubble: bool = False
    is_solid_background: bool = False
    is_lineart: bool = False
    has_screentone: bool = False
    is_color_webtoon: bool = False
    structure_crossing_mask: bool = False
    preferred_quality: str = QUALITY_BALANCED
    background_complexity: str = COMPLEXITY_LOW

    def __post_init__(self) -> None:
        if not 0.0 <= self.mask_area_ratio <= 1.0:
            raise ProviderInputError(
                "mask_area_ratio must be within [0, 1]", stage="router"
            )
        if self.preferred_quality not in ALL_QUALITIES:
            raise ProviderInputError(
                f"unknown preferred_quality: {self.preferred_quality!r}", stage="router"
            )
        if self.background_complexity not in ALL_COMPLEXITIES:
            raise ProviderInputError(
                f"unknown background_complexity: {self.background_complexity!r}",
                stage="router",
            )

    def as_dict(self) -> dict:
        return {
            "mask_area_ratio": round(self.mask_area_ratio, 6),
            "is_speech_bubble": self.is_speech_bubble,
            "is_solid_background": self.is_solid_background,
            "is_lineart": self.is_lineart,
            "has_screentone": self.has_screentone,
            "is_color_webtoon": self.is_color_webtoon,
            "structure_crossing_mask": self.structure_crossing_mask,
            "preferred_quality": self.preferred_quality,
            "background_complexity": self.background_complexity,
        }


@dataclass(frozen=True)
class RouteCandidate:
    route: str
    accepted: bool
    reason: str

    def as_dict(self) -> dict:
        return {"route": self.route, "accepted": self.accepted, "reason": self.reason}


@dataclass(frozen=True)
class RouterDecision:
    """The router's answer plus everything needed to audit it."""

    decision: str
    route: str | None
    reason: str
    candidates: tuple[RouteCandidate, ...] = ()
    allowed_routes: tuple[str, ...] = ()
    fallback_routes: tuple[str, ...] = ()
    color_route_selected: bool = False

    @property
    def blocked(self) -> bool:
        return self.decision == DECISION_BLOCKED

    def as_provenance(self) -> dict:
        return {
            "router_decision": self.decision,
            "router_route": self.route,
            "router_reason": self.reason,
            "router_candidates": [candidate.as_dict() for candidate in self.candidates],
            "router_allowed_routes": list(self.allowed_routes),
            "router_fallback_routes": list(self.fallback_routes),
            "router_color_route_selected": self.color_route_selected,
        }


def preferred_route_order(features: RouterFeatures) -> tuple[str, ...]:
    """D06 §21 typical strategy, widened by quality/complexity signals."""
    order: list[str] = []
    solid_small = features.is_solid_background and features.mask_area_ratio <= SOLID_AREA_RATIO
    if solid_small or (
        features.mask_area_ratio <= SOLID_AREA_RATIO
        and features.background_complexity == COMPLEXITY_LOW
        and not features.is_lineart
        and not features.has_screentone
        and not features.structure_crossing_mask
        and not features.is_color_webtoon
    ):
        order.append(ROUTE_SIMPLE_FILL)

    if features.is_color_webtoon or features.background_complexity == COMPLEXITY_HIGH:
        order.extend([ROUTE_BRUSHNET, ROUTE_FLUX_FILL, ROUTE_AOT_GAN, ROUTE_MANGA_LAMA])
    elif features.has_screentone or features.structure_crossing_mask:
        order.extend([ROUTE_AOT_GAN, ROUTE_MANGA_LAMA, ROUTE_BRUSHNET, ROUTE_FLUX_FILL])
    elif features.is_lineart:
        order.extend([ROUTE_MANGA_LAMA, ROUTE_AOT_GAN, ROUTE_BRUSHNET, ROUTE_FLUX_FILL])
    else:
        order.extend([ROUTE_MANGA_LAMA, ROUTE_AOT_GAN, ROUTE_BRUSHNET, ROUTE_FLUX_FILL])

    if features.preferred_quality == QUALITY_FAST:
        order.append(ROUTE_SIMPLE_FILL)
    order.append(ROUTE_EDGE_BLEED)  # dependency-free structural last resort
    # stable de-duplication, order preserved
    seen: set[str] = set()
    unique: list[str] = []
    for route in order:
        if route in seen:
            continue
        seen.add(route)
        unique.append(route)
    return tuple(unique)


def acceptable_routes(features: RouterFeatures) -> frozenset[str]:
    """Routes a scene may honestly be repaired with (no silent downgrade).

    A colored Webtoon or a high-complexity background needs a color-capable
    route: the dependency-free structural baselines are *not* acceptable
    substitutes there, so the router blocks (with a reason) instead of quietly
    producing a visibly wrong result.
    """
    if features.is_color_webtoon or features.background_complexity == COMPLEXITY_HIGH:
        return frozenset({ROUTE_BRUSHNET, ROUTE_FLUX_FILL, ROUTE_AOT_GAN, ROUTE_MANGA_LAMA})
    return frozenset(
        {
            ROUTE_SIMPLE_FILL,
            ROUTE_EDGE_BLEED,
            ROUTE_MANGA_LAMA,
            ROUTE_AOT_GAN,
            ROUTE_BRUSHNET,
            ROUTE_FLUX_FILL,
        }
    )


def decide_route(
    features: RouterFeatures,
    *,
    allowed_routes: tuple[str, ...],
    fallback_routes: tuple[str, ...] = (),
    requirements_satisfied: dict[str, bool] | None = None,
) -> RouterDecision:
    """Select the best allowed and runnable route, or block with a reason."""
    if not allowed_routes:
        raise ProviderInputError(
            "the inpaint route policy is empty; refusing to choose implicitly",
            stage="router",
        )
    satisfied = requirements_satisfied or {}
    acceptable = acceptable_routes(features)
    candidates: list[RouteCandidate] = []
    chosen: str | None = None
    chosen_reason = ""

    for route in preferred_route_order(features):
        if route not in allowed_routes:
            candidates.append(
                RouteCandidate(route, False, "not in the configured route policy")
            )
            continue
        if route not in acceptable:
            candidates.append(
                RouteCandidate(
                    route, False, "not acceptable for a colored/complex scene"
                )
            )
            continue
        gate = route_gate(
            route, requirements_satisfied=satisfied.get(route, True)
        )
        if not gate.runnable:
            candidates.append(RouteCandidate(route, False, gate.reason))
            continue
        candidates.append(RouteCandidate(route, True, gate.reason))
        chosen = route
        chosen_reason = _reason_for(route, features)
        break

    if chosen is None:
        attempted = ", ".join(
            f"{candidate.route} ({candidate.reason})" for candidate in candidates
        )
        return RouterDecision(
            decision=DECISION_BLOCKED,
            route=None,
            reason=f"no configured route is runnable: {attempted}",
            candidates=tuple(candidates),
            allowed_routes=tuple(allowed_routes),
            fallback_routes=tuple(fallback_routes),
        )

    return RouterDecision(
        decision=DECISION_ROUTE,
        route=chosen,
        reason=chosen_reason,
        candidates=tuple(candidates),
        allowed_routes=tuple(allowed_routes),
        fallback_routes=tuple(fallback_routes),
        color_route_selected=chosen
        in {ROUTE_BRUSHNET, ROUTE_FLUX_FILL}
        and (features.is_color_webtoon or features.background_complexity == COMPLEXITY_HIGH),
    )


def require_route(decision: RouterDecision) -> str:
    """Return the chosen route or fail closed with the router's reason."""
    if decision.blocked or decision.route is None:
        raise ProviderNotImplemented(decision.reason, stage="router")
    return decision.route


def _reason_for(route: str, features: RouterFeatures) -> str:
    if route == ROUTE_SIMPLE_FILL:
        return (
            "solid/small region → Simple Fill"
            f" (area_ratio={features.mask_area_ratio:.4f},"
            f" complexity={features.background_complexity})"
        )
    if route == ROUTE_BRUSHNET:
        return "colored Webtoon/complex background → color route (BrushNet policy)"
    if route == ROUTE_FLUX_FILL:
        return "critical detail escalation → FLUX Fill policy"
    if route == ROUTE_AOT_GAN:
        return "screentone/structure continuity → AOT-GAN policy"
    if route == ROUTE_MANGA_LAMA:
        return "monochrome manga default → Manga LaMa policy"
    if route == ROUTE_EDGE_BLEED:
        return "dependency-free structural baseline"
    return f"configured route {route}"


_MISSING = object()


def _route_sequence(policy: Mapping[str, Any], field: str) -> tuple[str, ...]:
    """Read a route list, rejecting anything that is not a sequence of str.

    TASK-036 AC ② (lifting the TASK-034 R-7 freeze): a bare string used to be
    iterated character by character, silently turning ``"simple-fill"`` into
    eleven single-letter routes.
    """
    value = policy.get(field, _MISSING)
    if value is _MISSING:
        return ()
    if isinstance(value, (str, bytes, bytearray)) or not isinstance(value, Sequence):
        raise ProviderInputError(
            f"inpaint.route_policy.{field} must be a sequence of strings"
            f" (got {type(value).__name__})",
            stage="inpaint",
        )
    for route in value:
        if not isinstance(route, str):
            raise ProviderInputError(
                f"inpaint.route_policy.{field} entries must be strings"
                f" (got {type(route).__name__})",
                stage="inpaint",
            )
    return tuple(value)


def _requirement_flags(policy: Mapping[str, Any]) -> dict[str, bool]:
    """Read ``requirements``, requiring real ``bool`` values.

    TASK-036 AC ③: ``bool("false")`` is ``True``, so coercion silently turned a
    user's ``"false"`` into an enabled requirement.
    """
    value = policy.get("requirements", _MISSING)
    if value is _MISSING:
        return {}
    if not isinstance(value, Mapping):
        raise ProviderInputError(
            "inpaint.route_policy.requirements must be a mapping"
            f" (got {type(value).__name__})",
            stage="inpaint",
        )
    flags: dict[str, bool] = {}
    for route, flag in value.items():
        if not isinstance(flag, bool):
            raise ProviderInputError(
                f"inpaint.route_policy.requirements[{route!r}] must be a bool"
                f" (got {type(flag).__name__})",
                stage="inpaint",
            )
        flags[str(route)] = flag
    return flags


@dataclass
class RoutePolicy:
    """The user-configured route policy (persisted with the Run settings)."""

    allowed_routes: tuple[str, ...] = (ROUTE_SIMPLE_FILL, ROUTE_EDGE_BLEED)
    fallback_routes: tuple[str, ...] = ()
    color_route: str | None = None
    requirements: dict[str, bool] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.color_route and self.color_route not in self.allowed_routes:
            # A configured color route is part of the policy by definition;
            # it still has to pass the runnable gate before it can be used.
            object.__setattr__(
                self, "allowed_routes", (*self.allowed_routes, self.color_route)
            )

    def with_color_route(self, route: str) -> "RoutePolicy":
        if route in self.allowed_routes:
            return RoutePolicy(
                allowed_routes=self.allowed_routes,
                fallback_routes=self.fallback_routes,
                color_route=route,
                requirements=dict(self.requirements),
            )
        return RoutePolicy(
            allowed_routes=(*self.allowed_routes, route),
            fallback_routes=self.fallback_routes,
            color_route=route,
            requirements=dict(self.requirements),
        )

    @classmethod
    def from_settings(
        cls, settings: Mapping[str, Any], *, default: "RoutePolicy"
    ) -> "RoutePolicy":
        """The **only** interpretation of the ``inpaint.route_policy`` setting.

        TASK-034 AC ① (ruling R-1..R-6) established the single entry point and
        the fail-closed direction; TASK-036 lifted the R-7 freeze and tightened
        the input validation (AC ①②③ below). Legal inputs keep their meaning
        exactly (see ``verification/TASK-036`` for the before/after matrix).

        - **R-1** (the one allowed difference, made explicit): an absent
          ``inpaint`` section or ``route_policy`` key returns ``default``
          unchanged — the assembly passes ``DEFAULT_ROUTE_POLICY`` and a Run
          passes the policy it was assembled with. That difference is a
          parameter, never a hidden branch.
        - **R-2 / TASK-036 AC ①**: a present but non-mapping ``route_policy``
          raises :class:`~ports.providers.errors.ProviderInputError` at *both*
          call sites, and so does a present but non-mapping ``inpaint``
          **section** — with a message that names the offending level.
        - **R-3**: an absent/empty ``allowed_routes`` falls back to
          ``default.allowed_routes``; **R-4**: ``fallback_routes`` defaults
          to ``()``.
        - **TASK-036 AC ②**: ``allowed_routes``/``fallback_routes`` must be
          actual sequences of ``str``; a bare string (previously char-expanded)
          and non-``str`` entries are rejected.
        - **R-5 / TASK-036 AC ③**: ``requirements`` defaults to ``{}`` and its
          values must be real ``bool``s — ``"false"``/``0``/``1`` are rejected
          instead of being coerced with ``bool()``.
        - **R-6 / Option B**: an absent or blank ``color_route`` means "no color
          route configured" (``None``); an explicitly named color route is
          still honoured and ``__post_init__`` adds it to ``allowed_routes``.
        """
        section = settings.get("inpaint", _MISSING)
        if section is _MISSING:
            return default
        if not isinstance(section, Mapping):
            raise ProviderInputError(
                "inpaint must be a mapping"
                f" (got {type(section).__name__})",
                stage="inpaint",
            )
        raw = section.get("route_policy", _MISSING)
        if raw is _MISSING:
            return default
        if not isinstance(raw, Mapping):
            raise ProviderInputError(
                "inpaint.route_policy must be a mapping"
                f" (got {type(raw).__name__})",
                stage="inpaint",
            )
        allowed = _route_sequence(raw, "allowed_routes")
        fallbacks = _route_sequence(raw, "fallback_routes")
        color_route = raw.get("color_route")
        return cls(
            allowed_routes=allowed or default.allowed_routes,
            fallback_routes=fallbacks,
            color_route=str(color_route) if color_route else None,
            requirements=_requirement_flags(raw),
        )

    def decide(self, features: RouterFeatures) -> RouterDecision:
        return decide_route(
            features,
            allowed_routes=self.allowed_routes,
            fallback_routes=self.fallback_routes,
            requirements_satisfied=self.requirements,
        )
