"""T1.1.2: normalized(0..1) -> page-pixel geometry, and every rejection.

Qt-free by construction: this module is the single owner of the rounding rule,
so the pixel mapping the overlay draws and the mapping the writer stores are
pinned here, not re-derived in QML.
"""

from __future__ import annotations

import workbench_helpers  # noqa: F401  (sys.path injection)

import pytest

from domain.regions.entities import BBox, RegionGeometry
from application.editing.region_canvas import (
    PAGE_SIZE_UNAVAILABLE,
    RegionCanvasError,
    normalized_to_page_geometry,
    page_geometry_to_normalized,
)


def codes(excinfo) -> str:
    return excinfo.value.code


def test_design_worked_example_maps_to_documented_pixels():
    # doc/tasks/TASK-013.md design table: page 800x1200, item drag after
    # a 600x600 pane -> normalized corners below must land on exact pixels.
    geometry = normalized_to_page_geometry(
        [(0.125, 0.16666666666666666), (0.625, 0.6666666666666666)], 800, 1200
    )
    assert geometry.bbox == BBox(100, 200, 400, 600)
    assert geometry.polygon == (
        (100, 200), (500, 200), (500, 800), (100, 800),
    )


def test_half_tie_rounds_up_not_to_even():
    # 0.125 and 0.625 are dyadic (2**-3, 2**-1+2**-3) so n*size == 12.5 / 62.5
    # is an exact tie, not a float coincidence. builtin round() would yield
    # (12, 62); the contract is half-up.
    geometry = normalized_to_page_geometry([(0.0, 0.0), (0.125, 0.625)], 100, 100)
    assert geometry.bbox == BBox(0, 0, 13, 63)


def test_rectangle_corners_may_arrive_in_any_order():
    forward = normalized_to_page_geometry([(0.25, 0.25), (0.75, 0.5)], 800, 1200)
    inverted = normalized_to_page_geometry([(0.75, 0.5), (0.25, 0.25)], 800, 1200)
    assert forward == inverted
    assert forward.bbox == BBox(200, 300, 400, 300)


def test_polygon_keeps_the_ring_it_was_given():
    geometry = normalized_to_page_geometry(
        [(0.0, 0.0), (0.5, 0.0), (0.5, 1.0)], 800, 1200
    )
    assert geometry.polygon == ((0, 0), (400, 0), (400, 1200))
    assert geometry.bbox == BBox(0, 0, 400, 1200)


def test_out_of_range_points_are_clamped_to_the_page():
    # Past the letterbox band the value still has to land on the page edge:
    # -0.2 -> 0 and 1.4 -> page height, so no coordinate escapes the extent.
    # The middle point sits off the corner-to-corner diagonal on purpose: a
    # collinear triple is a separate rejection, tested below.
    geometry = normalized_to_page_geometry(
        [(-0.2, 1.4), (0.2, 0.2), (1.3, -0.5)], 800, 1200
    )
    assert geometry.polygon == ((0, 1200), (160, 240), (800, 0))
    assert geometry.bbox == BBox(0, 0, 800, 1200)


def test_zero_area_rectangle_is_rejected_before_writing():
    # RegionGeometry/BBox raise ValueError on a non-positive extent, so the
    # converter must reject first: the ViewModel maps this to a typed error.
    with pytest.raises(RegionCanvasError) as excinfo:
        normalized_to_page_geometry([(0.25, 0.25), (0.25, 0.9)], 800, 1200)
    assert codes(excinfo) == "DEGENERATE_GEOMETRY"


def test_collapsed_polygon_extent_is_rejected():
    with pytest.raises(RegionCanvasError) as excinfo:
        normalized_to_page_geometry(
            [(0.2, 0.2), (0.2, 0.5), (0.2, 0.9)], 800, 1200
        )
    assert codes(excinfo) == "DEGENERATE_GEOMETRY"


def test_polygon_that_repeats_two_corners_is_rejected():
    # Four points, but only two distinct after rounding: the extent is a
    # perfectly healthy 640x960, so an extent test would wave it through.
    # The ring traces a line out and back and encloses nothing.
    with pytest.raises(RegionCanvasError) as excinfo:
        normalized_to_page_geometry(
            [(0.1, 0.1), (0.9, 0.9), (0.1, 0.1), (0.9, 0.9)], 800, 1200
        )
    assert codes(excinfo) == "DEGENERATE_GEOMETRY"


def test_collinear_polygon_is_rejected_as_degenerate():
    # Three distinct points, a non-zero bounding box, and no area at all: the
    # ring is a straight line. BBox's positivity cannot see it, so without an
    # area rule this persists as a region nothing covers.
    with pytest.raises(RegionCanvasError) as excinfo:
        normalized_to_page_geometry(
            [(0.1, 0.1), (0.3, 0.3), (0.9, 0.9)], 800, 1200
        )
    assert codes(excinfo) == "DEGENERATE_GEOMETRY"


def test_a_single_point_is_rejected():
    with pytest.raises(RegionCanvasError) as excinfo:
        normalized_to_page_geometry([(0.1, 0.1)], 800, 1200)
    assert codes(excinfo) == "TOO_FEW_POINTS"


def test_missing_page_dimensions_fails_fast_instead_of_collapsing():
    # A test double (or a catalog row) without width/height must not silently
    # collapse every box to the origin: floor(0.5 * 0) == 0 raises nothing.
    with pytest.raises(RegionCanvasError) as excinfo:
        normalized_to_page_geometry([(0.1, 0.1), (0.5, 0.5)], 0, 1200)
    assert codes(excinfo) == "PAGE_SIZE_UNAVAILABLE"


def test_returns_a_real_domain_geometry_not_a_dict():
    # Region.snapshot_state() calls self.geometry.as_jsonable()
    # (src/domain/regions/entities.py:272): a dict would raise AttributeError.
    geometry = normalized_to_page_geometry([(0.0, 0.0), (1.0, 1.0)], 800, 1200)
    assert isinstance(geometry, RegionGeometry)
    assert geometry.as_jsonable() == {
        "bbox": [0, 0, 800, 1200],
        "polygon": [[0, 0], [800, 0], [800, 1200], [0, 1200]],
    }


def test_backward_compatibility_reexports():
    """Verify legacy ui.viewmodels.workbench.region_canvas acts as a seamless shim (M2-I2).

    Note: ui.viewmodels.workbench package __init__ imports RunController (PySide6),
    so importing via module name requires PySide6 in legacy UI tree.
    """
    try:
        import PySide6  # noqa: F401
    except ImportError:
        pytest.skip("PySide6 not installed; legacy UI package __init__ requires Qt")

    import application.editing.region_canvas as app_rc
    import ui.viewmodels.workbench.region_canvas as ui_rc

    assert ui_rc.normalized_to_page_geometry is app_rc.normalized_to_page_geometry
    assert ui_rc.RegionCanvasError is app_rc.RegionCanvasError
    assert ui_rc.PAGE_SIZE_UNAVAILABLE is app_rc.PAGE_SIZE_UNAVAILABLE
    assert ui_rc.TOO_FEW_POINTS is app_rc.TOO_FEW_POINTS
    assert ui_rc.DEGENERATE_GEOMETRY is app_rc.DEGENERATE_GEOMETRY


# ---------------------------------------------------------------------------
# page_geometry_to_normalized (M2-WORKBENCH-REACT-1, contract rev 1.5):
# the READ-face reverse mapping, owned next to the forward writer so the
# round trip stays a single-math property, not a convention.
# ---------------------------------------------------------------------------


def test_reverse_mapping_round_trips_the_half_up_writer_exactly():
    """normalized -> pixels -> normalized is the identity for every stored
    integer pixel: floor((pixel/size)*size + 0.5) == pixel."""
    import math

    page_w, page_h = 800, 1200
    original = normalized_to_page_geometry(
        [(0.25, 0.1), (0.75, 0.5)], page_w, page_h
    )
    restored = page_geometry_to_normalized(original, page_w, page_h)

    bbox = restored["bbox"]
    ring = restored["polygon"]
    assert len(bbox) == 4 and len(ring) == 4
    # re-applying the forward rule to the restored normalized values yields
    # the exact stored integers (no half-pixel drift, incl. the edges 0/size
    # and the clamped size boundary)
    for index, (nx, ny) in enumerate(ring):
        px, py = original.polygon[index]
        assert math.floor(nx * page_w + 0.5) == px
        assert math.floor(ny * page_h + 0.5) == py
    bx, by, bw, bh = bbox
    assert math.floor(bx * page_w + 0.5) == original.bbox.x
    assert math.floor(by * page_h + 0.5) == original.bbox.y
    assert math.floor(bw * page_w + 0.5) == original.bbox.width
    assert math.floor(bh * page_h + 0.5) == original.bbox.height


def test_reverse_mapping_is_normalized_within_unit_square():
    geometry = normalized_to_page_geometry(
        [(0.0, 0.0), (1.0, 1.0)], 640, 480
    )
    restored = page_geometry_to_normalized(geometry, 640, 480)
    for x, y in restored["polygon"]:
        assert 0.0 <= x <= 1.0
        assert 0.0 <= y <= 1.0
    bx, by, bw, bh = restored["bbox"]
    assert 0.0 <= bx and bw <= 1.0
    assert 0.0 <= by and bh <= 1.0


def test_reverse_mapping_keeps_an_empty_ring_empty():
    geometry = RegionGeometry(bbox=BBox(10, 20, 30, 40), polygon=())
    restored = page_geometry_to_normalized(geometry, 200, 100)
    assert restored["polygon"] == []
    assert restored["bbox"] == [0.05, 0.2, 0.15, 0.4]


def test_reverse_mapping_rejects_a_nonpositive_page_extent_typed():
    geometry = RegionGeometry(bbox=BBox(0, 0, 10, 10))
    with pytest.raises(RegionCanvasError) as excinfo:
        page_geometry_to_normalized(geometry, 0, 100)
    assert excinfo.value.code == PAGE_SIZE_UNAVAILABLE
    with pytest.raises(RegionCanvasError) as excinfo:
        page_geometry_to_normalized(geometry, 100, -1)
    assert excinfo.value.code == PAGE_SIZE_UNAVAILABLE
