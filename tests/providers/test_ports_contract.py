"""Port contracts: success, failure and malformed input (TASK-019)."""

from __future__ import annotations

import pytest

from ports.detection.ports import (
    COORDINATE_SPACE_PAGE,
    COORDINATE_SPACE_TILE,
    DetectionResult,
    RegionCandidate,
    to_page_global,
)
from ports.inpaint.ports import BooleanMask, ImageFrame, InpaintRequest, MaskRecord
from ports.ocr.ports import OcrRequest
from ports.providers.errors import ProviderInputError
from ports.providers.profiles import (
    ALL_CAPABILITIES,
    CAPABILITY_DETECTION,
    CAPABILITY_INPAINT,
    CAPABILITY_OCR,
    CAPABILITY_TRANSLATION,
    ProviderProfile,
)
from ports.translation.protocol import (
    ContextPage,
    RegionInput,
    build_request_payload,
)


def test_capability_set_extends_without_changing_existing_names() -> None:
    assert CAPABILITY_DETECTION == "detection"
    assert {CAPABILITY_OCR, CAPABILITY_TRANSLATION, CAPABILITY_INPAINT} <= ALL_CAPABILITIES
    profile = ProviderProfile(
        provider_profile_id="p1",
        name="vision",
        provider_type="openai-compatible-vision",
        capabilities=frozenset({CAPABILITY_DETECTION, CAPABILITY_OCR}),
        base_url="https://example.invalid/v1",
    )
    assert profile.is_local() is False
    with pytest.raises(ValueError):
        ProviderProfile(
            provider_profile_id="p2",
            name="bad",
            provider_type="x",
            capabilities=frozenset({"unknown-capability"}),
        )


def test_tile_local_polygon_requires_origin_and_maps_globally() -> None:
    polygon = ((10.0, 20.0), (30.0, 20.0), (30.0, 40.0))
    assert to_page_global(
        polygon, coordinate_space=COORDINATE_SPACE_TILE, tile_origin=(0.0, 600.0)
    ) == ((10.0, 620.0), (30.0, 620.0), (30.0, 640.0))
    with pytest.raises(ProviderInputError):
        to_page_global(polygon, coordinate_space=COORDINATE_SPACE_TILE)
    with pytest.raises(ProviderInputError):
        to_page_global(polygon, coordinate_space="screen")
    with pytest.raises(ProviderInputError):
        to_page_global((), coordinate_space=COORDINATE_SPACE_PAGE)


def test_detection_result_keeps_provider_labels_and_reports_provenance() -> None:
    result = DetectionResult(
        page_id="page-1",
        candidates=(
            RegionCandidate(polygon=((0, 0), (5, 0), (5, 5)), provider_label="unmapped-0"),
        ),
        provider_id="vision",
        model="m",
        coordinate_space=COORDINATE_SPACE_PAGE,
    )
    mapped = result.page_global_candidates()
    assert mapped[0].provider_label == "unmapped-0"
    assert result.provenance()["candidate_count"] == 1


def test_ocr_request_contract_rejects_unknown_script_and_direction() -> None:
    OcrRequest(region_id="r1", page_id="p1", image_bytes=b"x")
    with pytest.raises(ProviderInputError):
        OcrRequest(region_id="r1", page_id="p1", script="klingon")
    with pytest.raises(ProviderInputError):
        OcrRequest(region_id="r1", page_id="p1", direction="diagonal")
    with pytest.raises(ProviderInputError):
        OcrRequest(region_id="", page_id="p1")


def test_translation_payload_ordering_and_truncation_are_declared() -> None:
    regions = [RegionInput("r1", "こんにちは")]
    context = [
        ContextPage("page-10", "after", "far", reading_order=10),
        ContextPage("page-2", "before", "near", reading_order=2),
        ContextPage("page-9", "after", "middle", reading_order=9),
    ]
    payload = build_request_payload("page-5", regions, context)
    assert [page.page_id for page in payload.context] == ["page-2", "page-9", "page-10"]

    # Budget that fits exactly the nearest page: the farther pages are dropped
    # together (nearest contiguous run), and the drop list is nearest-first.
    two_pages = build_request_payload("page-5", regions, context[:2]).token_estimate()
    truncated = build_request_payload(
        "page-5", regions, context, token_budget=two_pages - 1
    )
    assert truncated.context_pages == ("page-2",)
    assert truncated.truncated_context_pages == ("page-9", "page-10")
    assert truncated.payload_hash() == truncated.payload_hash()

    with pytest.raises(ProviderInputError):
        build_request_payload("page-5", [])
    with pytest.raises(ProviderInputError):
        build_request_payload("page-5", [RegionInput("", "x")])


def test_inpaint_request_validates_mask_image_and_route() -> None:
    from ports.inpaint.ports import ROUTE_SIMPLE_FILL

    image = ImageFrame(2, 2, "rgb32", bytes(16))
    raw = BooleanMask(2, 2, ((True, False), (False, False)))
    final = BooleanMask(2, 2, ((True, True), (False, False)))
    record = MaskRecord((("dilate_radius", "1"),), 1, 2, (0, 0, 1, 1), (0, 0, 2, 1), True)
    request = InpaintRequest(
        page_id="page-1",
        region_id="r1",
        image=image,
        raw_mask=raw,
        final_mask=final,
        route=ROUTE_SIMPLE_FILL,
        mask_record=record,
    )
    assert request.final_mask.covers(request.raw_mask)

    with pytest.raises(ProviderInputError):
        InpaintRequest(
            page_id="page-1",
            region_id="r1",
            image=image,
            raw_mask=raw,
            final_mask=BooleanMask(2, 2, ((False, False), (False, False))),
            route=ROUTE_SIMPLE_FILL,
            mask_record=record,
        )
    with pytest.raises(ProviderInputError):
        InpaintRequest(
            page_id="page-1",
            region_id="r1",
            image=image,
            raw_mask=raw,
            final_mask=final,
            route="no-such-route",
            mask_record=record,
        )
    with pytest.raises(ProviderInputError):
        InpaintRequest(
            page_id="page-1",
            region_id="r1",
            image=ImageFrame(4, 4, "rgb32", bytes(64)),
            raw_mask=raw,
            final_mask=final,
            route=ROUTE_SIMPLE_FILL,
            mask_record=record,
        )


def test_image_frame_and_mask_are_strict_about_shape() -> None:
    with pytest.raises(ProviderInputError):
        ImageFrame(2, 2, "rgb32", bytes(8))
    with pytest.raises(ProviderInputError):
        ImageFrame(0, 2, "rgb32", b"")
    with pytest.raises(ProviderInputError):
        ImageFrame(2, 2, "cmyk", bytes(16))
    with pytest.raises(ProviderInputError):
        BooleanMask(2, 2, ((True, False),))
    assert BooleanMask(2, 2, ((True, False), (False, False))).bbox() == (0, 0, 1, 1)
    assert BooleanMask(2, 2, ((False, False), (False, False))).bbox() is None


# NOTE (TASK-034 AC ②): the application → infrastructure layering guard that
# used to live here (a line-prefix scan) moved to
# ``tests/core/test_architecture.py`` and now reuses that module's AST
# implementation, which also covers literal ``importlib.import_module(...)``
# calls. Do not add a second copy of it here.
