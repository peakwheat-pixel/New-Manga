"""SQLite integration for regions: atomic seam, restart round-trip, guard
rollbacks, pin/restore semantics and the frozen FK/trigger invariants
(TASK-029 AC: Region current/revision with real transactions)."""

import json

import pytest

from application.editing.errors import GuardStatus
from application.editing.service import RegionEditingService
from domain.regions.entities import (
    BBox,
    Region,
    RegionGeometry,
    RegionOrigin,
    RegionRevision,
    RegionType,
    ReviewState,
)
from infrastructure.sqlite.connection import open_database
from infrastructure.sqlite.migrator import MigrationRunner
from infrastructure.sqlite.regions import SqliteRegionRepository
from infrastructure.sqlite.schema import default_migrations


@pytest.fixture()
def db_path(tmp_path):
    return tmp_path / "regions.db"


def make_repo(db_path):
    conn, opened = open_database(db_path, latest_known_schema_version=2)
    MigrationRunner(conn, default_migrations()).apply_pending()
    repo = SqliteRegionRepository(conn)
    return conn, repo


def seed_page(conn, page_id="page-1"):
    now = "2026-01-01T00:00:00.000+00:00"
    with conn:
        conn.execute(
            "INSERT INTO books (book_id, title, created_at, updated_at)"
            " VALUES ('book-1', 't', ?, ?)"
            " ON CONFLICT (book_id) DO NOTHING",
            (now, now),
        )
        conn.execute(
            "INSERT INTO chapters (chapter_id, book_id, title, created_at, updated_at)"
            " VALUES ('chapter-1', 'book-1', 'c', ?, ?)"
            " ON CONFLICT (chapter_id) DO NOTHING",
            (now, now),
        )
        conn.execute(
            "INSERT INTO pages (page_id, chapter_id, sort_order, created_at, updated_at)"
            " VALUES (?, 'chapter-1', 0, ?, ?)"
            " ON CONFLICT (page_id) DO NOTHING",
            (page_id, now, now),
        )


def geo(x=0, y=0, w=10, h=10):
    return RegionGeometry(bbox=BBox(x, y, w, h))


def test_region_service_end_to_end_on_sqlite(db_path):
    """Service + SQLite committer: create → OCR → manual → machine-reject →
    restart keeps everything (real transactions, real JSON round-trips)."""
    first_conn, first_repo = make_repo(db_path)
    seed_page(first_conn)
    service = RegionEditingService(first_repo, committer=first_repo)

    region = service.create_region("page-1", geo(5, 5, 70, 90))
    service.apply_ocr_result(region.region_id, "セリフ")
    service.save_manual_translation(region.region_id, "台词")
    revisions = first_repo.list_revisions(region.region_id)
    assert [rev.revision_no for rev in revisions] == [1, 2, 3]
    assert revisions[2].origin is RegionOrigin.USER
    assert revisions[2].review_state is ReviewState.NEEDS_REVIEW

    # The SQLite adapter rebuilds objects per read: always refresh by id.
    refreshed = service.get_region(region.region_id)
    assert refreshed.current_revision_id == revisions[2].region_revision_id

    # Restart: brand-new connection/repository over the same file.
    second_conn, second_repo = make_repo(db_path)
    second_service = RegionEditingService(second_repo, committer=second_repo)
    loaded = second_service.get_region(region.region_id)
    assert loaded.geometry.bbox.as_tuple() == (5, 5, 70, 90)
    assert loaded.text.ocr_text == "セリフ"
    assert loaded.text.edited_translation == "台词"
    assert loaded.text.translation_locked is True
    assert loaded.current_revision_id == refreshed.current_revision_id

    # The seam still guards correctly against the reloaded state.
    outcome = second_service.apply_machine_translation(
        loaded.region_id, "机译"
    )
    assert outcome.status is GuardStatus.LOCK_CHANGED
    first_conn.close()
    second_conn.close()


def test_stale_expected_input_rolls_back_real_transaction(db_path):
    conn, repo = make_repo(db_path)
    seed_page(conn)
    service = RegionEditingService(conn if False else repo, committer=repo)
    region = service.create_region("page-1", geo())
    stale = service.get_region(region.region_id).current_revision_id
    service.save_manual_translation(region.region_id, "人工12")
    current = service.get_region(region.region_id).current_revision_id

    outcome = service.apply_machine_translation(
        region.region_id, "后台结果", expected_current_revision_id=stale
    )
    # D06 §90: revision guard outranks the lock; nothing was written.
    assert outcome.status is GuardStatus.INPUT_REVISION_CHANGED
    assert outcome.conflicts == (region.region_id,)
    count = conn.execute(
        "SELECT COUNT(*) FROM region_revisions WHERE region_id = ?",
        (region.region_id,),
    ).fetchone()[0]
    assert count == 2  # creation + manual save only
    stored = repo.get_region(region.region_id)
    assert stored.text.edited_translation == "人工12"
    assert stored.text.machine_translation == ""


def test_lock_conflict_rolls_back_real_transaction(db_path):
    conn, repo = make_repo(db_path)
    seed_page(conn)
    service = RegionEditingService(repo, committer=repo)
    region_id = service.create_region("page-1", geo()).region_id
    stored_region = repo.get_region(region_id)
    current = stored_region.current_revision_id

    # A concurrent writer arms the translation lock behind our back.
    with conn:
        conn.execute(
            "UPDATE regions SET translation_locked = 1 WHERE region_id = ?",
            (region_id,),
        )

    from application.editing.ports import RegionLockSnapshot

    result = repo.commit_region_revision(
        stored_region,
        RegionRevision(
            region_revision_id="probe-rev",
            region_id=region_id,
            revision_no=0,
            snapshot=stored_region.snapshot_state(),
            origin=RegionOrigin.MACHINE,
            review_state=ReviewState.NEEDS_REVIEW,
        ),
        expected_current_revision_id=current,
        lock_snapshot=RegionLockSnapshot(
            region_locked=False, translation_locked=False, inpaint_locked=False
        ),
    )
    assert result.status.value == "lock_changed"
    # Rolled back: no revision row, pointer untouched, database consistent.
    assert conn.execute(
        "SELECT COUNT(*) FROM region_revisions"
    ).fetchone()[0] == 1
    assert repo.get_region(region_id).current_revision_id == current
    assert conn.execute("PRAGMA integrity_check").fetchone()[0] == "ok"


def test_pin_updates_flag_only(db_path):
    conn, repo = make_repo(db_path)
    seed_page(conn)
    service = RegionEditingService(repo, committer=repo)
    region = service.create_region("page-1", geo())
    service.save_manual_translation(region.region_id, "钉住这版")

    before = repo.get_revision(region.region_id, 2)
    before_snapshot = json.dumps(before.snapshot, sort_keys=True)
    before_origin = before.origin

    service.set_revision_pinned(region.region_id, 2, True)
    pinned = repo.get_revision(region.region_id, 2)
    assert pinned.is_pinned is True
    # TASK-028 §4.2: pin never rewrites the immutable snapshot.
    assert json.dumps(pinned.snapshot, sort_keys=True) == before_snapshot
    assert pinned.origin is before_origin
    assert pinned.created_at == before.created_at


def test_restore_appends_and_keeps_history_on_sqlite(db_path):
    conn, repo = make_repo(db_path)
    seed_page(conn)
    service = RegionEditingService(repo, committer=repo)
    region = service.create_region("page-1", geo())
    service.apply_ocr_result(region.region_id, "v2")
    service.save_manual_translation(region.region_id, "v3")

    restored = service.restore_revision(region.region_id, 1)
    revisions = repo.list_revisions(region.region_id)
    assert [rev.revision_no for rev in revisions] == [1, 2, 3, 4]
    assert revisions[3].origin is RegionOrigin.RESTORED
    assert revisions[3].restored_from_revision_id == revisions[0].region_revision_id
    assert restored.current_revision_id == revisions[3].region_revision_id
    assert json.dumps(revisions[0].snapshot, sort_keys=True) == json.dumps(
        revisions[3].snapshot, sort_keys=True
    )


def test_reorder_creates_user_revisions(db_path):
    conn, repo = make_repo(db_path)
    seed_page(conn)
    service = RegionEditingService(repo, committer=repo)
    a = service.create_region("page-1", geo())
    b = service.create_region("page-1", geo(200, 0))

    service.reorder_regions("page-1", [b.region_id, a.region_id])
    a_revs = repo.list_revisions(a.region_id)
    b_revs = repo.list_revisions(b.region_id)
    # TASK-028 §3.4: reading_order is revision-owned → every CHANGED
    # region appends a user revision (a: 1→2 moved to the end, b: 2→1).
    assert [rev.revision_no for rev in a_revs] == [1, 2]
    assert a_revs[-1].origin is RegionOrigin.USER
    assert a_revs[-1].snapshot["reading_order"] == 2
    assert [rev.revision_no for rev in b_revs] == [1, 2]
    assert b_revs[-1].snapshot["reading_order"] == 1
    assert service.list_regions("page-1")[0].region_id == b.region_id


def test_current_pointer_invariants_enforced_by_database(db_path):
    conn, repo = make_repo(db_path)
    seed_page(conn)
    service = RegionEditingService(repo, committer=repo)
    region = service.create_region("page-1", geo())
    other = service.create_region("page-1", geo(200, 0))
    other_rev = repo.list_revisions(other.region_id)[0]

    # R-106 pattern: clearing an established current is rejected by trigger.
    import sqlite3

    with pytest.raises(sqlite3.IntegrityError):
        with conn:
            conn.execute(
                "UPDATE regions SET current_revision_id = NULL WHERE region_id = ?",
                (region.region_id,),
            )

    # Cross-region current pointer is rejected by the composite FK.
    with pytest.raises(sqlite3.IntegrityError):
        with conn:
            conn.execute(
                "UPDATE regions SET current_revision_id = ? WHERE region_id = ?",
                (other_rev.region_revision_id, region.region_id),
            )
    assert conn.execute("PRAGMA integrity_check").fetchone()[0] == "ok"


def test_region_json_and_enum_roundtrip(db_path):
    conn, repo = make_repo(db_path)
    seed_page(conn)
    service = RegionEditingService(repo, committer=repo)
    region = service.create_region(
        "page-1",
        RegionGeometry(bbox=BBox(1, 2, 30, 40), polygon=((1, 1), (20, 0), (10, 15))),
        region_type=RegionType.SFX,
        sfx_policy="manual",
    )
    stored = repo.get_region(region.region_id)
    assert stored.region_type is RegionType.SFX
    assert stored.sfx_policy.value == "manual"
    assert stored.geometry.polygon == ((1, 1), (20, 0), (10, 15))
    assert stored.text.final_source == "none"
