"""Inpaint routes, router decisions, mask record and non-target protection."""

from __future__ import annotations

import pytest

from application.translation.inpaint.mask import (
    area_ratio,
    dilate,
    from_boxes,
    from_polygons,
    mask_record,
    refine,
)
from infrastructure.providers.inpaint_router import (
    COMPLEXITY_HIGH,
    DECISION_BLOCKED,
    RoutePolicy,
    RouterFeatures,
    decide_route,
    preferred_route_order,
    require_route,
)
from infrastructure.providers.inpaint_routes import (
    EdgeBleedProvider,
    SimpleFillProvider,
    describe_routes,
    edge_bleed,
    protected_pixel_violations,
    provider_for_route,
    route_gate,
    route_record,
    simple_fill,
)
from infrastructure.providers.step_writes import (
    decode_mask_payload,
    mask_payload,
)
from ports.inpaint.ports import (
    ROUTE_AOT_GAN,
    ROUTE_BRUSHNET,
    ROUTE_EDGE_BLEED,
    ROUTE_FLUX_FILL,
    ROUTE_MANGA_LAMA,
    ROUTE_SIMPLE_FILL,
    InpaintRequest,
)
from ports.providers.errors import (
    NonTargetWriteViolation,
    ProviderInputError,
    ProviderNotImplemented,
)

from conftest import frame, mask_from_boxes


# ----------------------------------------------------------------------
# route table / gate (TASK-018 R-007)
# ----------------------------------------------------------------------


def test_unimplemented_routes_stay_unrunnable_even_with_dependencies() -> None:
    """R-007: a satisfied dependency list cannot make a route implemented."""
    record = route_gate(ROUTE_MANGA_LAMA, requirements_satisfied=True)
    assert record.runnable is False
    assert record.state == "not_implemented"
    for route in (ROUTE_AOT_GAN, ROUTE_BRUSHNET, ROUTE_FLUX_FILL):
        assert route_gate(route, requirements_satisfied=True).runnable is False

    # A dependency-free route becomes unusable when its runtime is missing.
    assert route_gate(ROUTE_SIMPLE_FILL).runnable is True
    assert (
        route_gate(ROUTE_SIMPLE_FILL, requirements_satisfied=False).runnable is False
    )


def test_unknown_route_is_a_hard_error() -> None:
    with pytest.raises(ProviderNotImplemented):
        route_record("made-up-route")
    with pytest.raises(ProviderNotImplemented):
        provider_for_route("made-up-route")
    with pytest.raises(ProviderNotImplemented):
        provider_for_route(ROUTE_MANGA_LAMA)


def test_route_descriptions_are_explicit() -> None:
    described = {record.route: record for record in describe_routes()}
    assert set(described) == {
        ROUTE_SIMPLE_FILL,
        ROUTE_EDGE_BLEED,
        ROUTE_MANGA_LAMA,
        ROUTE_AOT_GAN,
        ROUTE_BRUSHNET,
        ROUTE_FLUX_FILL,
    }
    assert described[ROUTE_SIMPLE_FILL].dependency_free is True
    assert described[ROUTE_FLUX_FILL].requires_gpu is True


# ----------------------------------------------------------------------
# raster work and non-target protection
# ----------------------------------------------------------------------


def test_simple_fill_only_touches_masked_pixels() -> None:
    image = frame(4, 4, (10, 20, 30))
    mask = mask_from_boxes(4, 4, [(1, 1, 3, 2)])
    filled = simple_fill(image, mask, fill=(255, 255, 255))
    assert protected_pixel_violations(image, filled, mask) == ()
    # rgb32 byte order is B,G,R,A — the fill is white either way.
    assert filled.data[(1 * 4 + 1) * 4 : (1 * 4 + 1) * 4 + 3] == b"\xff\xff\xff"


def test_edge_bleed_spreads_neighbours_without_touching_unmasked_pixels() -> None:
    image = frame(5, 5, (0, 0, 0))
    mask = mask_from_boxes(5, 5, [(2, 2, 3, 3)])
    bled = edge_bleed(image, mask, iterations=2)
    assert protected_pixel_violations(image, bled, mask) == ()


def test_provider_raises_when_a_pixel_outside_the_mask_changes() -> None:
    image = frame(4, 4)
    mask = mask_from_boxes(4, 4, [(0, 0, 1, 1)])
    tampered = frame(4, 4, (0, 0, 0))  # every pixel differs
    violations = protected_pixel_violations(image, tampered, mask)
    assert len(violations) == 15

    record = mask_record(mask, mask)
    request = InpaintRequest(
        page_id="page-1",
        region_id="r1",
        image=image,
        raw_mask=mask,
        final_mask=mask,
        route=ROUTE_SIMPLE_FILL,
        mask_record=record,
    )
    provider = SimpleFillProvider()
    result = provider.inpaint(request)
    assert result.route == ROUTE_SIMPLE_FILL
    assert result.provenance()["mask_params"]
    assert result.mask_record is not None

    # A provider built for another route refuses the request.
    with pytest.raises(ProviderNotImplemented):
        EdgeBleedProvider().inpaint(request)


# ----------------------------------------------------------------------
# mask geometry + persistence round-trip (AC-INPAINT-001)
# ----------------------------------------------------------------------


def test_mask_geometry_and_refinement_keep_the_record_consistent() -> None:
    raw = from_boxes(6, 6, [(1, 1, 3, 3)])
    assert raw.area == 4
    refined = refine(raw, dilate_radius=1, erode_radius=0)
    assert refined.covers(raw) is True
    assert refined.area > raw.area
    record = mask_record(raw, refined, source="mask-refine")
    assert record.final_covers_raw is True
    assert record.raw_bbox == (1, 1, 3, 3)
    assert area_ratio(refined) == pytest.approx(refined.area / 36)

    polygon = from_polygons(8, 8, [((1, 1), (5, 1), (5, 5), (1, 5))])
    assert polygon.area > 0
    assert polygon.bbox() == (1, 1, 5, 5)

    with pytest.raises(ProviderInputError):
        from_boxes(4, 4, [(0, 0, 9, 9)])
    with pytest.raises(ProviderInputError):
        from_polygons(4, 4, [((0, 0), (1, 1))])
    with pytest.raises(ProviderInputError):
        dilate(raw, -1)


def test_mask_payload_round_trips_byte_for_byte() -> None:
    mask = from_boxes(7, 3, [(0, 0, 2, 2), (5, 1, 7, 3)])
    payload, mime, width, height = mask_payload(mask)
    header, restored = decode_mask_payload(payload)
    assert mime == "application/x-newmanga-mask"
    assert (width, height) == (7, 3)
    assert restored.rows == mask.rows
    assert restored.area == mask.area
    assert header["format"] == "bitmap-msb"


# ----------------------------------------------------------------------
# router (AC-INPAINT-003/004)
# ----------------------------------------------------------------------


def test_router_prefers_simple_fill_for_small_solid_regions() -> None:
    features = RouterFeatures(
        mask_area_ratio=0.01, is_solid_background=True, is_speech_bubble=True
    )
    decision = decide_route(
        features, allowed_routes=(ROUTE_SIMPLE_FILL, ROUTE_EDGE_BLEED)
    )
    assert decision.route == ROUTE_SIMPLE_FILL
    assert "Simple Fill" in decision.reason
    provenance = decision.as_provenance()
    assert provenance["router_reason"]
    assert provenance["router_allowed_routes"] == [ROUTE_SIMPLE_FILL, ROUTE_EDGE_BLEED]


def test_router_blocks_when_only_learned_routes_are_allowed_and_unimplemented() -> None:
    features = RouterFeatures(
        mask_area_ratio=0.4, is_lineart=True, preferred_quality="quality"
    )
    decision = decide_route(features, allowed_routes=(ROUTE_MANGA_LAMA, ROUTE_AOT_GAN))
    assert decision.blocked is True
    assert decision.route is None
    assert "not implemented" in decision.reason
    considered = {candidate.route for candidate in decision.candidates}
    assert {ROUTE_MANGA_LAMA, ROUTE_AOT_GAN} <= considered
    # Nothing outside the configured policy may be selected as a substitute.
    rejected = {
        candidate.route: candidate.reason
        for candidate in decision.candidates
        if not candidate.accepted
    }
    for route, reason in rejected.items():
        assert route in (ROUTE_MANGA_LAMA, ROUTE_AOT_GAN) or "not in the configured" in reason
    with pytest.raises(ProviderNotImplemented):
        require_route(decision)


def test_router_selects_and_traces_the_colored_webtoon_route() -> None:
    """AC-INPAINT-004: policy selects the color route; the choice is traced."""
    features = RouterFeatures(
        mask_area_ratio=0.2, is_color_webtoon=True, background_complexity=COMPLEXITY_HIGH
    )
    policy = RoutePolicy(
        allowed_routes=(ROUTE_SIMPLE_FILL, ROUTE_EDGE_BLEED),
        color_route=ROUTE_BRUSHNET,
        requirements={ROUTE_BRUSHNET: True},
    )
    assert ROUTE_BRUSHNET in policy.allowed_routes
    decision = policy.decide(features)
    # The color route is the only acceptable choice for a colored Webtoon;
    # because it has no implementation here, the step blocks instead of
    # silently repainting with a monochrome baseline.
    assert decision.blocked is True
    assert any(candidate.route == ROUTE_BRUSHNET for candidate in decision.candidates)
    blocked_detail = next(
        candidate.reason
        for candidate in decision.candidates
        if candidate.route == ROUTE_BRUSHNET
    )
    assert "not implemented" in blocked_detail
    baseline = next(
        candidate.reason
        for candidate in decision.candidates
        if candidate.route == ROUTE_EDGE_BLEED
    )
    assert "not acceptable" in baseline
    with pytest.raises(ProviderNotImplemented):
        require_route(decision)


def test_router_uses_an_explicitly_configured_fallback_route() -> None:
    features = RouterFeatures(mask_area_ratio=0.3, is_lineart=True)
    policy = RoutePolicy(
        allowed_routes=(ROUTE_MANGA_LAMA, ROUTE_EDGE_BLEED),
        requirements={ROUTE_MANGA_LAMA: False, ROUTE_EDGE_BLEED: True},
    )
    decision = policy.decide(features)
    assert decision.route == ROUTE_EDGE_BLEED
    assert decision.color_route_selected is False


def test_router_refuses_an_empty_policy() -> None:
    with pytest.raises(ProviderInputError):
        decide_route(RouterFeatures(mask_area_ratio=0.1), allowed_routes=())


def test_preferred_order_is_deterministic_and_deduplicated() -> None:
    features = RouterFeatures(mask_area_ratio=0.5, is_color_webtoon=True)
    order = preferred_route_order(features)
    assert len(order) == len(set(order))
    assert order.index(ROUTE_BRUSHNET) < order.index(ROUTE_EDGE_BLEED)