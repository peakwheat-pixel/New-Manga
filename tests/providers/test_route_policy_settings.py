"""TASK-034 AC ①: the single ``inpaint.route_policy`` interpretation.

The ruling (``doc/reviews/TASK-034-ac1-route-policy-ruling.md``) collapsed the
two private ``_route_policy`` copies into ``RoutePolicy.from_settings``. These
tests are the 12-input matrix from the decision request
(``verification/TASK-034/route-policy-decision-request.md``) plus the two
call-site regressions and the R-2 / Option B observables.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from application.translation.inpaint.router import (  # noqa: E402
    COMPLEXITY_HIGH,
    RoutePolicy,
    RouterFeatures,
    decide_route,
)
from infrastructure.providers.runtime import (  # noqa: E402
    DEFAULT_ROUTE_POLICY,
    build_provider_runtime,
)
from ports.inpaint.ports import (  # noqa: E402
    ROUTE_BRUSHNET,
    ROUTE_EDGE_BLEED,
    ROUTE_FLUX_FILL,
    ROUTE_SIMPLE_FILL,
)
from ports.providers.errors import ProviderInputError  # noqa: E402


def root_with(value) -> dict:
    """A root-shaped settings mapping, as both call sites receive it."""
    return {"inpaint": {"route_policy": value}}


def resolve(value, *, default: RoutePolicy = DEFAULT_ROUTE_POLICY) -> RoutePolicy:
    return RoutePolicy.from_settings(root_with(value), default=default)


# ---------------------------------------------------------------------------
# R-1: the one explicitly parameterized difference between the two call sites
# ---------------------------------------------------------------------------


def test_missing_section_or_key_returns_the_explicit_default() -> None:
    assert RoutePolicy.from_settings({}, default=DEFAULT_ROUTE_POLICY) is DEFAULT_ROUTE_POLICY
    assert (
        RoutePolicy.from_settings({"inpaint": {}}, default=DEFAULT_ROUTE_POLICY)
        is DEFAULT_ROUTE_POLICY
    )


def test_present_non_mapping_section_fails_loud_with_its_own_message() -> None:
    """TASK-036 AC ① (R-02): a wrong *section* type is not "key missing".

    TASK-034's R-7 freeze kept this silent (an ``inpaint`` string fell back to
    the default); TASK-036 lifts the freeze, and the two type errors must be
    distinguishable in the message so a user knows which level to fix.
    """
    for value in ("oops", [], 42, None):
        with pytest.raises(ProviderInputError) as error:
            RoutePolicy.from_settings({"inpaint": value}, default=DEFAULT_ROUTE_POLICY)
        message = str(error.value)
        assert error.value.error_code == "INVALID_INPUT"
        assert "inpaint must be a mapping" in message
        assert "route_policy" not in message
    with pytest.raises(ProviderInputError) as policy_error:
        RoutePolicy.from_settings(
            {"inpaint": {"route_policy": "oops"}}, default=DEFAULT_ROUTE_POLICY
        )
    assert "inpaint.route_policy must be a mapping" in str(policy_error.value)
    # R-1 (key absent) is untouched by the tightening:
    assert RoutePolicy.from_settings({}, default=DEFAULT_ROUTE_POLICY) is DEFAULT_ROUTE_POLICY


def test_the_default_parameter_is_what_distinguishes_the_two_call_sites() -> None:
    custom = RoutePolicy(
        allowed_routes=(ROUTE_EDGE_BLEED,), fallback_routes=(), color_route=None
    )
    assert RoutePolicy.from_settings({"inpaint": {}}, default=custom) is custom
    assert resolve({"allowed_routes": []}, default=custom).allowed_routes == (
        ROUTE_EDGE_BLEED,
    )


# ---------------------------------------------------------------------------
# R-2: a malformed policy fails loudly at both call sites
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("value", ["simple-fill", [], 42, ("edge-bleed",), None])
def test_non_mapping_route_policy_raises_the_same_typed_error(value) -> None:
    with pytest.raises(ProviderInputError) as error:
        resolve(value)
    assert error.value.error_code == "INVALID_INPUT"
    assert "inpaint.route_policy must be a mapping" in str(error.value)


def test_runtime_assembly_reports_a_malformed_policy_instead_of_ignoring_it() -> None:
    """R-2 on the assembly path: startup now reports the configuration error."""
    with pytest.raises(ProviderInputError):
        build_provider_runtime(settings=root_with("simple-fill"))


def test_runtime_assembly_reports_a_malformed_section_instead_of_ignoring_it() -> None:
    """TASK-036 AC ① assembly regression: the *section* type is checked too."""
    with pytest.raises(ProviderInputError) as error:
        build_provider_runtime(settings={"inpaint": "oops"})
    assert "inpaint must be a mapping" in str(error.value)


# ---------------------------------------------------------------------------
# R-3 / R-4 / R-5 / R-6 (unchanged legal semantics) and TASK-036 AC ②/③
# (R-7 freeze lifted: illegal inputs now fail loud instead of being rewritten)
# ---------------------------------------------------------------------------


def test_empty_mapping_uses_the_default_template() -> None:
    policy = resolve({})
    assert policy.allowed_routes == DEFAULT_ROUTE_POLICY.allowed_routes
    assert policy.fallback_routes == ()
    assert policy.color_route is None
    assert policy.requirements == {}


def test_allowed_routes_missing_or_empty_falls_back_to_the_default() -> None:
    assert resolve({"allowed_routes": [ROUTE_EDGE_BLEED]}).allowed_routes == (
        ROUTE_EDGE_BLEED,
    )
    assert resolve({"allowed_routes": []}).allowed_routes == (
        ROUTE_SIMPLE_FILL,
        ROUTE_EDGE_BLEED,
    )


def test_explicit_color_route_is_honoured_and_added_to_allowed_routes() -> None:
    """AC-INPAINT-004: a *configured* color route still takes effect."""
    policy = resolve({"color_route": ROUTE_FLUX_FILL})
    assert policy.color_route == ROUTE_FLUX_FILL
    assert ROUTE_FLUX_FILL in policy.allowed_routes
    assert ROUTE_SIMPLE_FILL in policy.allowed_routes  # baselines kept (R-3)
    already = resolve({"allowed_routes": [ROUTE_BRUSHNET], "color_route": ROUTE_BRUSHNET})
    assert already.allowed_routes.count(ROUTE_BRUSHNET) == 1


@pytest.mark.parametrize("blank", ["", None])
def test_blank_color_route_means_no_color_route_configured(blank) -> None:
    """R-6 / Option B: the default is "no color route", not an unverified model."""
    policy = resolve({"color_route": blank})
    assert policy.color_route is None
    assert ROUTE_BRUSHNET not in policy.allowed_routes


def test_fallback_routes_and_requirements_defaults() -> None:
    """TASK-034 R-4/R-5 defaults stay; only *illegal values* behave differently."""
    policy = resolve({"requirements": {"brushnet": True}})
    assert policy.fallback_routes == ()
    assert policy.requirements == {"brushnet": True}
    assert resolve({"fallback_routes": [ROUTE_EDGE_BLEED]}).fallback_routes == (
        ROUTE_EDGE_BLEED,
    )
    assert resolve({"fallback_routes": []}).fallback_routes == ()
    assert resolve({"requirements": {}}).requirements == {}


@pytest.mark.parametrize("field", ["allowed_routes", "fallback_routes"])
def test_route_lists_reject_a_bare_string(field: str) -> None:
    """TASK-036 AC ②: no more silent character expansion (R-07a freeze lifted).

    This replaces the TASK-034 test that *pinned* the character expansion
    (``test_allowed_routes_as_string_keeps_the_frozen_char_expansion``); the
    freeze is declared lifted in the TASK-036 Handoff.
    """
    with pytest.raises(ProviderInputError) as error:
        resolve({field: ROUTE_SIMPLE_FILL})
    message = str(error.value)
    assert error.value.error_code == "INVALID_INPUT"
    assert f"inpaint.route_policy.{field} must be a sequence of strings" in message
    assert "str" in message


@pytest.mark.parametrize("field", ["allowed_routes", "fallback_routes"])
@pytest.mark.parametrize("value", [42, {"edge-bleed": True}, {"edge-bleed"}, None])
def test_route_lists_reject_non_sequences(field: str, value) -> None:
    with pytest.raises(ProviderInputError) as error:
        resolve({field: value})
    assert f"inpaint.route_policy.{field} must be a sequence of strings" in str(
        error.value
    )


@pytest.mark.parametrize("field", ["allowed_routes", "fallback_routes"])
@pytest.mark.parametrize("value", [[1], [None], [ROUTE_EDGE_BLEED, 3]])
def test_route_lists_reject_non_string_entries(field: str, value) -> None:
    with pytest.raises(ProviderInputError) as error:
        resolve({field: value})
    assert f"inpaint.route_policy.{field} entries must be strings" in str(error.value)


def test_legal_route_sequences_keep_their_meaning() -> None:
    """TASK-036 AC ⑥: for legal inputs nothing changed."""
    assert resolve({"allowed_routes": [ROUTE_EDGE_BLEED]}).allowed_routes == (
        ROUTE_EDGE_BLEED,
    )
    assert resolve({"allowed_routes": (ROUTE_SIMPLE_FILL,)}).allowed_routes == (
        ROUTE_SIMPLE_FILL,
    )
    assert resolve({"fallback_routes": [ROUTE_EDGE_BLEED]}).fallback_routes == (
        ROUTE_EDGE_BLEED,
    )


@pytest.mark.parametrize("value", ["false", "true", 0, 1, None, [], "yes"])
def test_requirements_values_must_be_real_bools(value) -> None:
    """TASK-036 AC ③: ``bool("false")`` is True — coercion is gone (R-07b)."""
    with pytest.raises(ProviderInputError) as error:
        resolve({"requirements": {"brushnet": value}})
    message = str(error.value)
    assert error.value.error_code == "INVALID_INPUT"
    assert "inpaint.route_policy.requirements['brushnet'] must be a bool" in message
    assert type(value).__name__ in message


@pytest.mark.parametrize("value", [True, False])
def test_legal_requirement_flags_keep_their_meaning(value: bool) -> None:
    assert resolve({"requirements": {"brushnet": value}}).requirements == {
        "brushnet": value
    }


def test_requirements_must_be_a_mapping() -> None:
    with pytest.raises(ProviderInputError) as error:
        resolve({"requirements": ["brushnet"]})
    assert "inpaint.route_policy.requirements must be a mapping" in str(error.value)


# ---------------------------------------------------------------------------
# Call-site regressions and the ruled default
# ---------------------------------------------------------------------------


def test_default_policy_matches_the_type_default_and_the_eligible_set() -> None:
    assert DEFAULT_ROUTE_POLICY == RoutePolicy()
    assert DEFAULT_ROUTE_POLICY.allowed_routes == (ROUTE_SIMPLE_FILL, ROUTE_EDGE_BLEED)
    assert DEFAULT_ROUTE_POLICY.fallback_routes == ()
    assert DEFAULT_ROUTE_POLICY.color_route is None
    assert DEFAULT_ROUTE_POLICY.requirements == {}


def test_runtime_call_site_uses_the_shared_parser() -> None:
    """Assembly-time regression: runtime.route_policy == from_settings(default=DEFAULT)."""
    for value in (
        {},
        {"allowed_routes": [ROUTE_EDGE_BLEED]},
        {"color_route": ROUTE_FLUX_FILL},
        {"requirements": {"brushnet": True}},
    ):
        settings = root_with(value)
        runtime = build_provider_runtime(settings=settings)
        assert runtime.route_policy == RoutePolicy.from_settings(
            settings, default=DEFAULT_ROUTE_POLICY
        )
    status = build_provider_runtime(settings={}).status()["route_policy"]
    assert status["allowed_routes"] == (ROUTE_SIMPLE_FILL, ROUTE_EDGE_BLEED)
    assert status["color_route"] is None
    assert status["requirements"] == {}


def test_configured_policy_is_reported_and_used_by_the_router() -> None:
    """The configured color route is visible in status and accepted by the router."""
    settings = root_with(
        {
            "allowed_routes": [ROUTE_BRUSHNET],
            "color_route": ROUTE_BRUSHNET,
            "requirements": {ROUTE_BRUSHNET: True},
        }
    )
    runtime = build_provider_runtime(settings=settings)
    assert runtime.route_policy.color_route == ROUTE_BRUSHNET
    decision = decide_route(
        RouterFeatures(
            mask_area_ratio=0.2,
            is_color_webtoon=True,
            background_complexity=COMPLEXITY_HIGH,
        ),
        allowed_routes=runtime.route_policy.allowed_routes,
        fallback_routes=runtime.route_policy.fallback_routes,
        requirements_satisfied=runtime.route_policy.requirements,
    )
    # runnable only once an implementation exists (TASK-018 R-007), but the
    # candidate list proves the configured route was accepted by the policy.
    reasons = {candidate.route: candidate.reason for candidate in decision.candidates}
    assert "not in the configured route policy" not in reasons[ROUTE_BRUSHNET]


# ---------------------------------------------------------------------------
# Decision invariance for the ruled default (the observable change is the
# reason / allowed set, not which route is chosen)
# ---------------------------------------------------------------------------

#: The pre-ruling ``DEFAULT_ROUTE_POLICY`` as it stood at base ``b34b27e``,
#: reconstructed literally (it no longer exists in ``src/``) so the invariance
#: claim is checkable in the same test run.
_PRE_RULING_DEFAULT = RoutePolicy(
    allowed_routes=(ROUTE_SIMPLE_FILL, ROUTE_EDGE_BLEED, ROUTE_BRUSHNET),
    fallback_routes=(),
    color_route=ROUTE_BRUSHNET,
    requirements={ROUTE_BRUSHNET: False, ROUTE_FLUX_FILL: False},
)

_FEATURE_COMBOS = (
    "colour webtoon",
    "high complexity",
    "line art",
    "plain region",
)


def _features(combo: str) -> RouterFeatures:
    if combo == "colour webtoon":
        return RouterFeatures(
            mask_area_ratio=0.2, is_color_webtoon=True, background_complexity=COMPLEXITY_HIGH
        )
    if combo == "high complexity":
        return RouterFeatures(mask_area_ratio=0.4, background_complexity=COMPLEXITY_HIGH)
    if combo == "line art":
        return RouterFeatures(mask_area_ratio=0.4, is_lineart=True)
    return RouterFeatures(mask_area_ratio=0.4, is_speech_bubble=True)


def _decide(features: RouterFeatures, policy: RoutePolicy):
    return decide_route(
        features,
        allowed_routes=policy.allowed_routes,
        fallback_routes=policy.fallback_routes,
        requirements_satisfied=policy.requirements,
    )


@pytest.mark.parametrize("combo", _FEATURE_COMBOS)
def test_ruled_default_does_not_change_which_route_is_chosen(combo: str) -> None:
    """Evidence: the decision (route or BLOCKED) is identical before and after.

    The colour-webtoon and high-complexity combos are BLOCKED on both sides
    (no learned route is implemented, TASK-018 R-007); the line-art and plain
    combos keep choosing the dependency-free ``edge-bleed`` baseline. Only the
    *reason* and the allowed set changed — see the next test.
    """
    features = _features(combo)
    before = _decide(features, _PRE_RULING_DEFAULT)
    after = _decide(features, DEFAULT_ROUTE_POLICY)
    assert before.decision == after.decision, (combo, before.reason, after.reason)
    assert before.route == after.route


def test_ruled_default_only_changes_the_reason_and_the_allowed_set() -> None:
    features = _features("colour webtoon")
    before = {c.route: c.reason for c in _decide(features, _PRE_RULING_DEFAULT).candidates}
    after = {c.route: c.reason for c in _decide(features, DEFAULT_ROUTE_POLICY).candidates}
    # `brushnet` used to be allowed-but-unimplemented; now it is not configured
    # at all, which is exactly the ruled Option B observable change.
    assert before[ROUTE_BRUSHNET].startswith("not implemented")
    assert after[ROUTE_BRUSHNET] == "not in the configured route policy"
    assert ROUTE_BRUSHNET in _PRE_RULING_DEFAULT.allowed_routes
    assert ROUTE_BRUSHNET not in DEFAULT_ROUTE_POLICY.allowed_routes
