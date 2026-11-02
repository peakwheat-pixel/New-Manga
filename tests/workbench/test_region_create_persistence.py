"""T1.1.2 AC: a drawn rectangle lands real rows in regions + region_revisions.

Tasks 3-5 prove the viewmodel calls its injected writer with page-pixel
geometry, against fakes. That is not proof the write persists, so this file
wires the production ``RegionEditingService`` over a migrated SQLite database
and asserts the two tables, the origin, the current pointer, and what a
reload reads back.

The page extent still comes from ``FakePage``: production supplies it via
``_ManagedPageCatalog -> SqliteLibraryRepository.list_pages -> list[Page]``
and those fields are covered by the storage suite. What is proven here is the
write seam, which is what T1.1.2 adds.

The region catalog is the real service too, not a fake list. An empty fake
would make "the deleted region vanished" pass while delete did nothing, and
would hide the case the acceptance list calls out: a row in the database the
workbench never learns about.
"""

from __future__ import annotations

import hashlib
import json

import workbench_helpers  # noqa: F401  (sys.path injection)
from workbench_helpers import FakePage, make_pipeline

from application.editing.service import RegionEditingService
from infrastructure.sqlite.connection import open_database
from infrastructure.sqlite.migrator import MigrationRunner
from infrastructure.sqlite.regions import SqliteRegionRepository
from infrastructure.sqlite.schema import default_migrations
from ui.viewmodels.workbench import WorkbenchViewModel

NOW = "2026-01-01T00:00:00.000+00:00"


def _editing(tmp_path):
    conn, _ = open_database(
        tmp_path / "library.db",
        latest_known_schema_version=default_migrations()[-1].schema_version,
    )
    MigrationRunner(conn, default_migrations()).apply_pending()
    with conn:
        conn.execute(
            "INSERT INTO books (book_id, title, created_at, updated_at)"
            " VALUES ('book-1', 't', ?, ?)",
            (NOW, NOW),
        )
        conn.execute(
            "INSERT INTO chapters (chapter_id, book_id, title, created_at, updated_at)"
            " VALUES ('chapter-1', 'book-1', 'c', ?, ?)",
            (NOW, NOW),
        )
        conn.execute(
            "INSERT INTO pages (page_id, chapter_id, sort_order, created_at,"
            " updated_at) VALUES ('p1', 'chapter-1', 0, ?, ?)",
            (NOW, NOW),
        )
    repository = SqliteRegionRepository(conn)
    return conn, RegionEditingService(repository, committer=repository)


def _vm(tmp_path, managed_original_ref=""):
    conn, editing = _editing(tmp_path)
    service, _ = make_pipeline(pages=[("p1", 1)])
    vm = WorkbenchViewModel(
        pipeline=service,
        page_catalog=workbench_helpers.FakePageCatalog(
            [
                FakePage(
                    "p1",
                    "chapter-1",
                    1,
                    "001.jpg",
                    managed_original_ref=managed_original_ref,
                    width=800,
                    height=1200,
                )
            ]
        ),
        region_catalog=editing,
        region_creator=editing,
        region_deleter=editing,
    )
    vm.setContext("book-1", "chapter-1", "测试书", "第1话")
    vm.selectPage("p1")
    return conn, editing, vm


def test_drawn_rectangle_creates_region_and_first_revision(tmp_path, qapp):
    conn, _editing, vm = _vm(tmp_path)
    before = conn.execute("SELECT COUNT(*) FROM regions").fetchone()[0]

    vm.createRectangle(0.125, 0.16666666666666666, 0.625, 0.6666666666666666)

    assert conn.execute("SELECT COUNT(*) FROM regions").fetchone()[0] == before + 1
    row = conn.execute(
        "SELECT r.page_id, r.geometry_json, r.reading_order, r.current_revision_id,"
        "       v.revision_no, v.origin, v.snapshot_json"
        "  FROM regions r JOIN region_revisions v ON v.region_id = r.region_id"
    ).fetchone()
    assert row[0] == "p1"
    geometry = json.loads(row[1])
    assert geometry["bbox"] == [100, 200, 400, 600]
    assert geometry["polygon"] == [[100, 200], [500, 200], [500, 800], [100, 800]]
    assert row[2] == 1                       # first region on the page
    assert (row[4], row[5]) == (1, "user")   # one revision, drawn by the user
    assert row[3] is not None                # current pointer resolved
    assert json.loads(row[6])["geometry"]["bbox"] == [100, 200, 400, 600]


def test_invalid_drag_writes_no_rows_at_all(tmp_path, qapp):
    # Persistence-side proof of "illegal geometry must not reach the
    # database": the tables stay byte-identical, not merely unselected.
    conn, _editing, vm = _vm(tmp_path)
    tables = conn.execute(
        "SELECT (SELECT COUNT(*) FROM regions), (SELECT COUNT(*) FROM region_revisions)"
    ).fetchone()

    vm.createRectangle(0.4, 0.4, 0.4, 0.9)  # zero width

    assert conn.execute(
        "SELECT (SELECT COUNT(*) FROM regions), (SELECT COUNT(*) FROM region_revisions)"
    ).fetchone() == tables


def test_workbench_sees_the_region_it_just_created(tmp_path, qapp):
    conn, _editing, vm = _vm(tmp_path)
    vm.createRectangle(0.1, 0.1, 0.5, 0.5)

    rows = vm.get_inspector_regions()
    assert [row["region_id"] for row in rows] == [vm.inspectorRegionId]
    assert rows[0]["geometry"]["bbox"] == [80, 120, 320, 480]
    assert conn.execute("SELECT COUNT(*) FROM regions").fetchone()[0] == 1


def test_reopening_the_database_reads_back_the_same_geometry(tmp_path, qapp):
    # The acceptance loop the pixel math exists for: draw in the UI, reload,
    # and the same page position comes back. Zoom and pan are display state
    # and never enter the stored value, which is why this is page pixels.
    conn, _editing, vm = _vm(tmp_path)
    vm.createPolygon("[[0.0, 0.0], [0.5, 0.0], [0.5, 1.0]]")
    original = vm.get_inspector_regions()[0]["geometry"]
    conn.close()

    reopened, _ = open_database(
        tmp_path / "library.db",
        latest_known_schema_version=default_migrations()[-1].schema_version,
    )
    reloaded = RegionEditingService(SqliteRegionRepository(reopened))
    regions = reloaded.list_regions("p1")

    assert [region.geometry.as_jsonable() for region in regions] == [original]
    reopened.close()


def test_deleted_region_disappears_from_the_workbench(tmp_path, qapp):
    conn, _editing, vm = _vm(tmp_path)
    vm.createRectangle(0.1, 0.1, 0.5, 0.5)
    region_id = vm.inspectorRegionId
    assert region_id

    vm.deleteRegion(region_id)

    assert vm.get_inspector_regions() == []
    assert vm.inspectorRegionId == ""
    assert conn.execute(
        "SELECT deleted_at IS NOT NULL FROM regions WHERE region_id = ?",
        (region_id,),
    ).fetchone()[0] == 1


def test_drawing_a_region_leaves_the_source_file_untouched(tmp_path, qapp):
    # Managed Copy / source protection has to survive this new write path.
    # The region belongs to SQLite, so the managed original is not rewritten.
    source = tmp_path / "001.jpg"
    source.write_bytes(b"\xff\xd8\xff managed copy of the original page")
    before = (
        source.stat().st_mtime_ns,
        hashlib.sha256(source.read_bytes()).hexdigest(),
    )
    conn, _editing, vm = _vm(tmp_path, managed_original_ref=str(source))

    vm.createRectangle(0.2, 0.2, 0.7, 0.8)

    after = (
        source.stat().st_mtime_ns,
        hashlib.sha256(source.read_bytes()).hexdigest(),
    )
    assert after == before
    assert conn.execute("SELECT COUNT(*) FROM regions").fetchone()[0] == 1
