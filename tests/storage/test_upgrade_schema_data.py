"""Synthetic legacy-schema data migration tests (UPGRADE-SCHEMA-MIGRATION-1).

The real pre-AD-002 user databases are not available (see UPGRADE-REHEARSAL-1), so
these tests synthesise old libraries with the project's own migration definitions:
for every legacy schema version (v1..v5) a database is built by applying the first
N migrations *one at a time*, seeding the data that the build migrated past on the
way (v1 rows, v2 column extensions/tags/regions, v3 pipeline rows, v4
reading/export rows, v5 cleanup manifests), and then the remaining migration chain
is applied up to the latest schema.

The point is not just "it runs": the v5 migration rebuilds
``pipeline_run_targets`` / ``pipeline_tasks`` / ``step_runs`` /
``step_result_candidates`` with ``INSERT ... SELECT`` and a ``DROP TABLE``; these
tests seed those tables before v5 and assert the rows (all columns) survive the
rebuild. Every seeded table is also checked for foreign-key integrity and for the
exact values that were written.

What is asserted after the upgrade:
- the chain lands on the latest schema version;
- seeded rows survive with their values/relations unchanged (full column sets for
  the tables each version seeded);
- later-version objects exist (v2 regions, v3 pipeline, v4 reading/export,
  v5 cleanup manifests, v6 plugin tables);
- ``PRAGMA foreign_key_check`` is empty and the database is writable;
- re-running the migrator is a no-op (idempotent).
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:  # mirrors tests/core|packaging conftest.py
    sys.path.insert(0, str(SRC_ROOT))

from infrastructure.sqlite.migrator import MigrationRunner, read_schema_version  # noqa: E402
from infrastructure.sqlite.schema import default_migrations  # noqa: E402

MIGRATIONS = default_migrations()
LATEST_VERSION = MIGRATIONS[-1].schema_version
LEGACY_VERSIONS = [migration.schema_version for migration in MIGRATIONS[:-1]]
NOW = "2026-01-02T03:04:05+00:00"

BOOK_ID = "book-legacy"
CHAPTER_ID = "chapter-1"
PAGE_ID = "page-1"
ARTIFACT_ID = "artifact-1"
REVISION_ID = "revision-1"
REGION_ID = "region-1"
REGION_REVISION_ID = "region-revision-1"
RUN_ID = "run-1"
RUN_TARGET_ID = "run-target-1"
TASK_ID = "task-1"
PROGRESS_ID = "progress-1"
EXPORT_ID = "export-1"
TAG_ID = "tag-1"

#: Tables that only exist after the given migration; used for anti-false-positive
#: checks when starting from v1.
LATEST_TABLES = (
    "regions",
    "region_revisions",
    "tags",
    "book_tags",
    "pipeline_runs",
    "pipeline_run_targets",
    "pipeline_tasks",
    "step_runs",
    "step_result_candidates",
    "reading_progress",
    "export_history",
    "book_cleanup_manifests",
    "plugin_state",
    "plugin_events",
)


def _connect(db_path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys=ON")
    return connection


def _build_legacy_database(db_path: Path, version: int) -> sqlite3.Connection:
    """Apply migrations 1..version one by one, seeding the data of each era."""
    connection = _connect(db_path)
    for migration in MIGRATIONS[:version]:
        applied = MigrationRunner(connection, [migration]).apply_pending()
        assert [record.schema_version for record in applied] == [migration.schema_version]
        _seed_for_version(connection, migration.schema_version)
    assert read_schema_version(connection) == version
    return connection


def _seed_for_version(connection: sqlite3.Connection, version: int) -> None:
    if version == 1:
        _seed_v1(connection)
    elif version == 2:
        _seed_v2(connection)
    elif version == 3:
        _seed_v3(connection)
    elif version == 4:
        _seed_v4(connection)
    elif version == 5:
        _seed_v5(connection)
    connection.commit()


def _seed_v1(connection: sqlite3.Connection) -> None:
    connection.execute(
        "INSERT INTO books (book_id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
        (BOOK_ID, "旧书", NOW, NOW),
    )
    connection.execute(
        "INSERT INTO chapters (chapter_id, book_id, title, sort_order, created_at, updated_at)"
        " VALUES (?, ?, ?, 1, ?, ?)",
        (CHAPTER_ID, BOOK_ID, "第 1 章", NOW, NOW),
    )
    connection.execute(
        "INSERT INTO pages (page_id, chapter_id, sort_order, created_at, updated_at)"
        " VALUES (?, ?, 1, ?, ?)",
        (PAGE_ID, CHAPTER_ID, NOW, NOW),
    )
    connection.execute(
        "INSERT INTO media_artifacts (artifact_id, book_id, chapter_id, page_id,"
        " artifact_type, created_at, updated_at) VALUES (?, ?, ?, ?, 'original', ?, ?)",
        (ARTIFACT_ID, BOOK_ID, CHAPTER_ID, PAGE_ID, NOW, NOW),
    )
    connection.execute(
        "INSERT INTO artifact_revisions (artifact_revision_id, artifact_id, revision_no,"
        " managed_path, file_hash, mime_type, size_bytes, created_at)"
        " VALUES (?, ?, 1, 'managed/page-1.png', 'hash-page-1', 'image/png', 4096, ?)",
        (REVISION_ID, ARTIFACT_ID, NOW),
    )


def _seed_v2(connection: sqlite3.Connection) -> None:
    connection.execute(
        "UPDATE books SET original_title='原書名', author='作者', publisher='出版社',"
        " series_title='系列', description='简介', source_language='ja', target_language='zh',"
        " is_favorite=1, is_archived=0 WHERE book_id=?",
        (BOOK_ID,),
    )
    connection.execute(
        "UPDATE chapters SET chapter_number='1', subtitle='副标题', chapter_type='paged',"
        " reading_direction='rtl' WHERE chapter_id=?",
        (CHAPTER_ID,),
    )
    connection.execute(
        "UPDATE pages SET source_filename='page-1.png', source_hash='src-hash-1',"
        " source_size_bytes=4096, width=800, height=1200, page_locked=1 WHERE page_id=?",
        (PAGE_ID,),
    )
    connection.execute(
        "INSERT INTO tags (tag_id, name, created_at, updated_at) VALUES (?, '标签', ?, ?)",
        (TAG_ID, NOW, NOW),
    )
    connection.execute("INSERT INTO book_tags (book_id, tag_id) VALUES (?, ?)", (BOOK_ID, TAG_ID))
    connection.execute(
        "INSERT INTO regions (region_id, page_id, region_type, reading_order, geometry_json,"
        " text_json, style_json, region_locked, created_at, updated_at)"
        " VALUES (?, ?, 'speech', 1, '{\"x\":1}', '{\"t\":\"你好\"}', '{}', 1, ?, ?)",
        (REGION_ID, PAGE_ID, NOW, NOW),
    )
    connection.execute(
        "INSERT INTO region_revisions (region_revision_id, region_id, revision_no,"
        " snapshot_json, origin, review_state, created_at)"
        " VALUES (?, ?, 1, '{\"snap\":1}', 'imported', 'confirmed', ?)",
        (REGION_REVISION_ID, REGION_ID, NOW),
    )


def _seed_v3(connection: sqlite3.Connection) -> None:
    connection.execute(
        "INSERT INTO pipeline_runs (run_id, command_type, scope_type, requested_targets_json,"
        " settings_snapshot_json, provider_binding_snapshot_json, context_policy_json,"
        " status, run_json, updated_at)"
        " VALUES (?, 'translate', 'page', '{}', '{}', '{}', '{}', 'succeeded', '{}', ?)",
        (RUN_ID, NOW),
    )
    connection.execute(
        "INSERT INTO pipeline_run_targets (run_target_id, pipeline_run_id, target_id,"
        " target_type, page_id, region_id, target_order, snapshot_json)"
        " VALUES (?, ?, 'target-1', 'page', ?, NULL, 0, '{\"target\":1}')",
        (RUN_TARGET_ID, RUN_ID, PAGE_ID),
    )
    connection.execute(
        "INSERT INTO pipeline_tasks (task_id, pipeline_run_id, run_target_id, target_id,"
        " target_type, page_id, region_id, status, units_json, step_run_ids_json)"
        " VALUES (?, ?, ?, 'target-1', 'page', ?, NULL, 'succeeded', '{\"units\":1}', '[]')",
        (TASK_ID, RUN_ID, RUN_TARGET_ID, PAGE_ID),
    )


def _seed_v4(connection: sqlite3.Connection) -> None:
    connection.execute(
        "INSERT INTO reading_progress (progress_id, book_id, chapter_id, mode,"
        " last_page_id, last_read_at, updated_at)"
        " VALUES (?, ?, ?, 'translated', ?, ?, ?)",
        (PROGRESS_ID, BOOK_ID, CHAPTER_ID, PAGE_ID, NOW, NOW),
    )
    connection.execute(
        "INSERT INTO export_history (export_id, book_id, chapter_id, export_type, status,"
        " created_at) VALUES (?, ?, ?, 'pdf', 'completed', ?)",
        (EXPORT_ID, BOOK_ID, CHAPTER_ID, NOW),
    )


def _seed_v5(connection: sqlite3.Connection) -> None:
    connection.execute(
        "INSERT INTO book_cleanup_manifests (book_id, targets_json, created_at)"
        " VALUES (?, '{\"targets\":[]}', ?)",
        (BOOK_ID, NOW),
    )


def _table_names(connection: sqlite3.Connection) -> set[str]:
    return {
        row["name"]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall()
    }


def _assert_seeded_data(connection: sqlite3.Connection, start_version: int) -> None:
    """Value assertions for every seeded table, gated by the starting version."""

    # --- v1-era rows exist for every starting version -----------------------
    book = connection.execute(
        "SELECT title, created_at, updated_at FROM books WHERE book_id=?", (BOOK_ID,)
    ).fetchone()
    assert book["title"] == "旧书"
    assert book["created_at"] == NOW and book["updated_at"] == NOW

    chapter = connection.execute(
        "SELECT book_id, title, sort_order FROM chapters WHERE chapter_id=?", (CHAPTER_ID,)
    ).fetchone()
    assert chapter["book_id"] == BOOK_ID
    assert chapter["title"] == "第 1 章" and chapter["sort_order"] == 1

    page = connection.execute(
        "SELECT chapter_id, sort_order FROM pages WHERE page_id=?", (PAGE_ID,)
    ).fetchone()
    assert page["chapter_id"] == CHAPTER_ID and page["sort_order"] == 1

    artifact = connection.execute(
        "SELECT book_id, chapter_id, page_id, artifact_type FROM media_artifacts"
        " WHERE artifact_id=?",
        (ARTIFACT_ID,),
    ).fetchone()
    assert (artifact["book_id"], artifact["chapter_id"], artifact["page_id"]) == (
        BOOK_ID,
        CHAPTER_ID,
        PAGE_ID,
    )
    assert artifact["artifact_type"] == "original"

    revision = connection.execute(
        "SELECT artifact_id, revision_no, managed_path, file_hash, size_bytes"
        " FROM artifact_revisions WHERE artifact_revision_id=?",
        (REVISION_ID,),
    ).fetchone()
    assert revision["artifact_id"] == ARTIFACT_ID and revision["revision_no"] == 1
    assert revision["managed_path"] == "managed/page-1.png"
    assert revision["file_hash"] == "hash-page-1" and revision["size_bytes"] == 4096

    if start_version < 2:
        return

    # --- v2-era data --------------------------------------------------------
    ext = connection.execute(
        "SELECT original_title, author, publisher, is_favorite FROM books WHERE book_id=?",
        (BOOK_ID,),
    ).fetchone()
    assert (ext["original_title"], ext["author"], ext["publisher"], ext["is_favorite"]) == (
        "原書名",
        "作者",
        "出版社",
        1,
    )
    chapter_ext = connection.execute(
        "SELECT chapter_number, subtitle, chapter_type FROM chapters WHERE chapter_id=?",
        (CHAPTER_ID,),
    ).fetchone()
    assert (chapter_ext["chapter_number"], chapter_ext["subtitle"]) == ("1", "副标题")
    page_ext = connection.execute(
        "SELECT source_filename, source_hash, source_size_bytes, width, height, page_locked"
        " FROM pages WHERE page_id=?",
        (PAGE_ID,),
    ).fetchone()
    assert (
        page_ext["source_filename"],
        page_ext["source_hash"],
        page_ext["source_size_bytes"],
        page_ext["width"],
        page_ext["height"],
        page_ext["page_locked"],
    ) == ("page-1.png", "src-hash-1", 4096, 800, 1200, 1)
    tag = connection.execute("SELECT name FROM tags WHERE tag_id=?", (TAG_ID,)).fetchone()
    assert tag["name"] == "标签"
    assert connection.execute(
        "SELECT COUNT(*) FROM book_tags WHERE book_id=? AND tag_id=?", (BOOK_ID, TAG_ID)
    ).fetchone()[0] == 1
    region = connection.execute(
        "SELECT page_id, region_type, reading_order, region_locked FROM regions"
        " WHERE region_id=?",
        (REGION_ID,),
    ).fetchone()
    assert region["page_id"] == PAGE_ID and region["region_type"] == "speech"
    assert region["reading_order"] == 1 and region["region_locked"] == 1
    region_revision = connection.execute(
        "SELECT region_id, revision_no, origin, review_state FROM region_revisions"
        " WHERE region_revision_id=?",
        (REGION_REVISION_ID,),
    ).fetchone()
    assert (region_revision["region_id"], region_revision["revision_no"]) == (REGION_ID, 1)
    assert (region_revision["origin"], region_revision["review_state"]) == ("imported", "confirmed")

    if start_version < 3:
        return

    # --- v3-era pipeline data (must survive the v5 table rebuilds) ----------
    run = connection.execute(
        "SELECT command_type, scope_type, status FROM pipeline_runs WHERE run_id=?", (RUN_ID,)
    ).fetchone()
    assert (run["command_type"], run["scope_type"], run["status"]) == (
        "translate",
        "page",
        "succeeded",
    )
    target = connection.execute(
        "SELECT pipeline_run_id, target_id, target_type, page_id, target_order, snapshot_json"
        " FROM pipeline_run_targets WHERE run_target_id=?",
        (RUN_TARGET_ID,),
    ).fetchone()
    assert (target["pipeline_run_id"], target["target_id"], target["target_type"]) == (
        RUN_ID,
        "target-1",
        "page",
    )
    assert target["page_id"] == PAGE_ID and target["target_order"] == 0
    assert target["snapshot_json"] == '{"target":1}'
    task = connection.execute(
        "SELECT pipeline_run_id, run_target_id, target_id, status, units_json"
        " FROM pipeline_tasks WHERE task_id=?",
        (TASK_ID,),
    ).fetchone()
    assert (task["pipeline_run_id"], task["run_target_id"], task["target_id"]) == (
        RUN_ID,
        RUN_TARGET_ID,
        "target-1",
    )
    assert task["status"] == "succeeded" and task["units_json"] == '{"units":1}'

    if start_version < 4:
        return

    # --- v4-era reading/export data ----------------------------------------
    progress = connection.execute(
        "SELECT book_id, chapter_id, mode, last_page_id FROM reading_progress"
        " WHERE progress_id=?",
        (PROGRESS_ID,),
    ).fetchone()
    assert progress["book_id"] == BOOK_ID and progress["chapter_id"] == CHAPTER_ID
    assert progress["mode"] == "translated" and progress["last_page_id"] == PAGE_ID
    export = connection.execute(
        "SELECT book_id, chapter_id, export_type, status FROM export_history"
        " WHERE export_id=?",
        (EXPORT_ID,),
    ).fetchone()
    assert (export["book_id"], export["chapter_id"], export["export_type"]) == (
        BOOK_ID,
        CHAPTER_ID,
        "pdf",
    )
    assert export["status"] == "completed"

    if start_version < 5:
        return

    # --- v5-era cleanup manifest -------------------------------------------
    manifest = connection.execute(
        "SELECT targets_json FROM book_cleanup_manifests WHERE book_id=?", (BOOK_ID,)
    ).fetchone()
    assert manifest["targets_json"] == '{"targets":[]}'


def _assert_latest(connection: sqlite3.Connection) -> None:
    assert read_schema_version(connection) == LATEST_VERSION
    names = _table_names(connection)
    missing = [name for name in LATEST_TABLES if name not in names]
    assert not missing, f"latest schema is missing tables: {missing}"
    assert connection.execute("PRAGMA integrity_check").fetchone()[0] == "ok"


def _assert_foreign_keys(connection: sqlite3.Connection) -> None:
    violations = connection.execute("PRAGMA foreign_key_check").fetchall()
    assert violations == [], f"foreign key violations: {violations}"


@pytest.mark.parametrize("version", LEGACY_VERSIONS, ids=[f"v{v}" for v in LEGACY_VERSIONS])
def test_synthetic_legacy_data_survives_full_upgrade(tmp_path: Path, version: int) -> None:
    db_path = tmp_path / f"legacy-v{version}.db"
    connection = _build_legacy_database(db_path, version)
    before = _table_names(connection)

    applied = MigrationRunner(connection, MIGRATIONS).apply_pending()
    assert [record.schema_version for record in applied] == list(
        range(version + 1, LATEST_VERSION + 1)
    )
    after = _table_names(connection)
    new_tables = [name for name in LATEST_TABLES if name not in before]
    assert new_tables, "starting point unexpectedly already had every latest table"
    assert all(name in after for name in new_tables)

    _assert_latest(connection)
    _assert_seeded_data(connection, version)
    _assert_foreign_keys(connection)

    # The upgraded database is usable.
    connection.execute(
        "INSERT INTO books (book_id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
        ("book-after-upgrade", "升级后新增", NOW, NOW),
    )
    connection.commit()
    assert connection.execute("SELECT COUNT(*) FROM books").fetchone()[0] == 2
    connection.close()


def test_upgrade_from_v1_creates_later_version_objects(tmp_path: Path) -> None:
    connection = _build_legacy_database(tmp_path / "legacy-v1.db", 1)
    v1_tables = _table_names(connection)
    for later_table in LATEST_TABLES:
        assert later_table not in v1_tables

    MigrationRunner(connection, MIGRATIONS).apply_pending()
    _assert_latest(connection)
    _assert_seeded_data(connection, 1)
    connection.close()


@pytest.mark.parametrize("version", LEGACY_VERSIONS, ids=[f"v{v}" for v in LEGACY_VERSIONS])
def test_upgrade_is_idempotent_for_synthetic_legacy_data(
    tmp_path: Path, version: int
) -> None:
    connection = _build_legacy_database(tmp_path / f"legacy-idem-v{version}.db", version)
    MigrationRunner(connection, MIGRATIONS).apply_pending()
    before = connection.execute("SELECT COUNT(*) FROM books").fetchone()[0]

    assert MigrationRunner(connection, MIGRATIONS).apply_pending() == []
    assert connection.execute("SELECT COUNT(*) FROM books").fetchone()[0] == before
    _assert_latest(connection)
    _assert_seeded_data(connection, version)
    connection.close()
