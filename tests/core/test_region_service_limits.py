"""V11R-F0-1 I3/P2-B: the application service enforces the vertex bound too.

Review r3 (P2-B): ``MAX_GEOMETRY_POINTS`` was only checked on the wire/Host, so
a direct application caller (pipeline/edit command outside the wire, tests,
future use cases) could persist an unbounded polygon inside one write
transaction — exactly the long-write-lock hazard P2-E intended to remove.

The service now rejects before persistence with the typed
``RegionLimitExceeded`` (ValueError family; wire maps it to
INVALID_REQUEST/validation) for create_region, save_geometry, split parts and
the derived merged polygon.
"""

from __future__ import annotations

import io
from pathlib import Path
import sys

import pytest
from PIL import Image

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from application.editing.errors import RegionLimitExceeded  # noqa: E402
from application.editing.region_canvas import MAX_GEOMETRY_POINTS  # noqa: E402
from application.importing.images.ports import ImportSource  # noqa: E402
from bootstrap.core_service import assemble_production_core  # noqa: E402
from domain.regions.entities import BBox, RegionGeometry  # noqa: E402

NOW = "2026-01-01T00:00:00.000+00:00"
RECT = RegionGeometry(bbox=BBox(10, 10, 100, 60))


def _polygon(points: int, *, size: int = 100) -> RegionGeometry:
    ring = tuple(
        (
            (index * 3) % size,
            (index * 7) % size,
        )
        for index in range(points)
    )
    return RegionGeometry(bbox=BBox(10, 10, size, size), polygon=ring)


def _seed_page(core) -> str:
    with core.conn:
        core.conn.execute(
            "INSERT INTO books (book_id,title,created_at,updated_at)"
            " VALUES ('book','b',?,?)",
            (NOW, NOW),
        )
        core.conn.execute(
            "INSERT INTO chapters (chapter_id,book_id,title,created_at,updated_at)"
            " VALUES ('chapter','book','c',?,?)",
            (NOW, NOW),
        )
    buffer = io.BytesIO()
    Image.new("RGBA", (400, 600), (40, 80, 120, 255)).save(buffer, format="PNG")
    payload = buffer.getvalue()
    report = core.importer.import_files(
        "chapter", [ImportSource("service-limits.png", lambda: payload)]
    )
    assert not report.failed and len(report.imported) == 1, report
    return report.imported[0].page.page_id


@pytest.fixture()
def core(tmp_path: Path):
    assembled = assemble_production_core(tmp_path / "data")
    try:
        yield assembled
    finally:
        assembled.conn.close()


def _revision_count(core) -> int:
    return core.conn.execute(
        "SELECT COUNT(*) FROM region_revisions"
    ).fetchone()[0]


def test_create_region_rejects_oversized_polygon_before_persisting(core):
    page_id = _seed_page(core)
    revisions_before = _revision_count(core)

    with pytest.raises(RegionLimitExceeded):
        core.editing.create_region(
            page_id, _polygon(MAX_GEOMETRY_POINTS + 1)
        )

    assert core.conn.execute(
        "SELECT COUNT(*) FROM regions WHERE page_id = ?", (page_id,)
    ).fetchone()[0] == 0
    assert _revision_count(core) == revisions_before


def test_save_geometry_rejects_oversized_polygon_before_persisting(core):
    page_id = _seed_page(core)
    region = core.editing.create_region(page_id, RECT)
    revisions_before = _revision_count(core)

    with pytest.raises(RegionLimitExceeded):
        core.editing.save_geometry(
            region.region_id, _polygon(MAX_GEOMETRY_POINTS + 1)
        )

    assert _revision_count(core) == revisions_before
    stored = core.editing.get_region(region.region_id)
    assert stored.geometry.bbox == RECT.bbox
    assert stored.geometry.polygon == ()


def test_split_rejects_an_oversized_part_before_persisting(core):
    page_id = _seed_page(core)
    source = core.editing.create_region(
        page_id, RegionGeometry(bbox=BBox(0, 0, 100, 50))
    )
    revisions_before = _revision_count(core)

    with pytest.raises(RegionLimitExceeded):
        core.editing.split_region(
            source.region_id,
            [
                RegionGeometry(bbox=BBox(0, 0, 50, 50)),
                _polygon(MAX_GEOMETRY_POINTS + 1),
            ],
        )

    assert _revision_count(core) == revisions_before
    assert {
        region.region_id for region in core.editing.list_regions(page_id)
    } == {source.region_id}


def test_merge_rejects_when_the_derived_polygon_exceeds_the_bound(core):
    page_id = _seed_page(core)
    each = MAX_GEOMETRY_POINTS // 2 + 20  # two sources sum above the bound
    first = core.editing.create_region(page_id, _polygon(each))
    second = core.editing.create_region(page_id, _polygon(each))
    revisions_before_first = _revision_count(core)

    with pytest.raises(RegionLimitExceeded):
        core.editing.merge_regions(page_id, [first.region_id, second.region_id])

    assert _revision_count(core) == revisions_before_first
    assert {
        region.region_id for region in core.editing.list_regions(page_id)
    } == {first.region_id, second.region_id}


def test_at_the_bound_is_allowed(core):
    page_id = _seed_page(core)
    region = core.editing.create_region(page_id, _polygon(MAX_GEOMETRY_POINTS))
    assert region.region_id
    assert len(core.editing.get_region(region.region_id).geometry.polygon) == (
        MAX_GEOMETRY_POINTS
    )
