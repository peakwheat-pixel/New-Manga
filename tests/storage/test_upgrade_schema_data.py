"""Synthetic legacy-schema data migration tests (UPGRADE-SCHEMA-MIGRATION-1).

The real pre-AD-002 user databases are not available (see UPGRADE-REHEARSAL-1), so
these tests synthesise old libraries with the project's own migration definitions:
for every legacy schema version (v1..v5) a database is built by applying the first
N migrations *one at a time*, seeding the data of each era as it is reached (v1
rows; v2 column extensions/tags/regions; v3 pipeline runs/targets/tasks and step
runs/candidates; v4 reading/export; v5 cleanup manifests) and then the remaining
migration chain is applied to the latest schema.

The v5 migration rebuilds four tables (``pipeline_run_targets``,
``pipeline_tasks``, ``step_runs``, ``step_result_candidates``) with
``INSERT ... SELECT`` + ``DROP TABLE``; every one of them is seeded *before* v5
and asserted column-by-column after the whole chain, so an empty-table rebuild
cannot pass.

Assertions are generated from what the seed wrote (``EXPECTED``): every seeded
row is compared column-by-column after the upgrade, foreign keys and the schema
integrity are checked, and key columns/indexes of the latest schema are asserted.
``FROZEN_V1_TABLES`` pins the v1 table set so a change in the migration
definitions fails loudly instead of silently moving both sides of the test.
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

#: Frozen table set of the v1 schema (a regression in the migration definitions
#: must fail this test loudly).
FROZEN_V1_TABLES = frozenset(
    {
        "books",
        "chapters",
        "pages",
        "media_artifacts",
        "artifact_revisions",
        "schema_migrations",
        "application_metadata",
        "backup_records",
    }
)

#: Tables a v1 database must gain by the time it reaches the latest schema.
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

BOOK_ID = "book-legacy"
CHAPTER_ID = "chapter-1"
PAGE_ID = "page-1"
ARTIFACT_ID = "artifact-1"
REVISION_ID = "revision-1"
TAG_ID = "tag-1"
REGION_ID = "region-1"
REGION_REVISION_ID = "region-revision-1"
RUN_ID = "run-1"
RUN_TARGET_ID = "run-target-1"
TASK_ID = "task-1"
STEP_RUN_ID = "step-run-1"
CANDIDATE_ID = "candidate-1"
PROGRESS_ID = "progress-1"
EXPORT_ID = "export-1"

#: Primary key column of every table the tests seed (used by the expected-row
#: assertions).
ID_COLUMNS = {
    "books": "book_id",
    "chapters": "chapter_id",
    "pages": "page_id",
    "media_artifacts": "artifact_id",
    "artifact_revisions": "artifact_revision_id",
    "tags": "tag_id",
    "regions": "region_id",
    "region_revisions": "region_revision_id",
    "pipeline_runs": "run_id",
    "pipeline_run_targets": "run_target_id",
    "pipeline_tasks": "task_id",
    "step_runs": "step_run_id",
    "step_result_candidates": "candidate_id",
    "reading_progress": "progress_id",
    "export_history": "export_id",
    "book_cleanup_manifests": "book_id",
}

#: Columns that exist in the v1 schema per seeded table (used when asserting the
#: v1 rows before the later-version data is present).
V1_COLUMNS = {
    "books": ("book_id", "title", "created_at", "updated_at"),
    "chapters": ("chapter_id", "book_id", "title", "sort_order", "created_at", "updated_at"),
    "pages": ("page_id", "chapter_id", "sort_order", "created_at", "updated_at"),
    "media_artifacts": (
        "artifact_id",
        "book_id",
        "chapter_id",
        "page_id",
        "artifact_type",
        "created_at",
        "updated_at",
    ),
    "artifact_revisions": (
        "artifact_revision_id",
        "artifact_id",
        "revision_no",
        "managed_path",
        "file_hash",
        "mime_type",
        "size_bytes",
        "created_at",
    ),
}

#: (table, id value) -> {column: expected value}; filled by the seed functions.
EXPECTED: dict[tuple[str, str], dict[str, object]] = {}


def _record(table: str, id_value: str, **values: object) -> None:
    EXPECTED.setdefault((table, id_value), {}).update(values)


def _connect(db_path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys=ON")
    return connection


def _build_legacy_database(db_path: Path, version: int) -> sqlite3.Connection:
    """Apply migrations 1..version one by one, seeding the data of each era."""
    EXPECTED.clear()
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
    _record("books", BOOK_ID, book_id=BOOK_ID, title="旧书", created_at=NOW, updated_at=NOW)
    connection.execute(
        "INSERT INTO chapters (chapter_id, book_id, title, sort_order, created_at, updated_at)"
        " VALUES (?, ?, ?, 1, ?, ?)",
        (CHAPTER_ID, BOOK_ID, "第 1 章", NOW, NOW),
    )
    _record(
        "chapters",
        CHAPTER_ID,
        chapter_id=CHAPTER_ID,
        book_id=BOOK_ID,
        title="第 1 章",
        sort_order=1,
        created_at=NOW,
        updated_at=NOW,
    )
    connection.execute(
        "INSERT INTO pages (page_id, chapter_id, sort_order, created_at, updated_at)"
        " VALUES (?, ?, 1, ?, ?)",
        (PAGE_ID, CHAPTER_ID, NOW, NOW),
    )
    _record(
        "pages",
        PAGE_ID,
        page_id=PAGE_ID,
        chapter_id=CHAPTER_ID,
        sort_order=1,
        created_at=NOW,
        updated_at=NOW,
    )
    connection.execute(
        "INSERT INTO media_artifacts (artifact_id, book_id, chapter_id, page_id,"
        " artifact_type, created_at, updated_at) VALUES (?, ?, ?, ?, 'original', ?, ?)",
        (ARTIFACT_ID, BOOK_ID, CHAPTER_ID, PAGE_ID, NOW, NOW),
    )
    _record(
        "media_artifacts",
        ARTIFACT_ID,
        artifact_id=ARTIFACT_ID,
        book_id=BOOK_ID,
        chapter_id=CHAPTER_ID,
        page_id=PAGE_ID,
        artifact_type="original",
        created_at=NOW,
        updated_at=NOW,
    )
    connection.execute(
        "INSERT INTO artifact_revisions (artifact_revision_id, artifact_id, revision_no,"
        " managed_path, file_hash, mime_type, size_bytes, created_at)"
        " VALUES (?, ?, 1, 'managed/page-1.png', 'hash-page-1', 'image/png', 4096, ?)",
        (REVISION_ID, ARTIFACT_ID, NOW),
    )
    _record(
        "artifact_revisions",
        REVISION_ID,
        artifact_revision_id=REVISION_ID,
        artifact_id=ARTIFACT_ID,
        revision_no=1,
        managed_path="managed/page-1.png",
        file_hash="hash-page-1",
        mime_type="image/png",
        size_bytes=4096,
        created_at=NOW,
    )


def _seed_v2(connection: sqlite3.Connection) -> None:
    books_values = {
        "original_title": "原書名",
        "author": "作者",
        "publisher": "出版社",
        "series_title": "系列",
        "description": "简介",
        "source_language": "ja",
        "target_language": "zh",
        "source_url": "https://example.invalid/book",
        "notes": "备注",
        "default_chapter_type": "paged",
        "default_reading_direction": "rtl",
        "is_favorite": 1,
        "is_archived": 0,
        "last_opened_at": NOW,
    }
    for column, value in books_values.items():
        connection.execute(f"UPDATE books SET {column}=? WHERE book_id=?", (value, BOOK_ID))
    _record("books", BOOK_ID, **books_values)

    chapter_values = {
        "chapter_number": "1",
        "subtitle": "副标题",
        "import_order": 2,
        "chapter_type": "paged",
        "reading_direction": "rtl",
        "notes": "章节备注",
    }
    for column, value in chapter_values.items():
        connection.execute(
            f"UPDATE chapters SET {column}=? WHERE chapter_id=?", (value, CHAPTER_ID)
        )
    _record("chapters", CHAPTER_ID, **chapter_values)

    page_values = {
        "source_filename": "page-1.png",
        "source_order": 3,
        "source_hash": "src-hash-1",
        "source_size_bytes": 4096,
        "width": 800,
        "height": 1200,
        "managed_original_ref": "managed/page-1.png",
        "page_locked": 1,
        "review_state": "confirmed",
        "overall_status": "completed",
    }
    for column, value in page_values.items():
        connection.execute(f"UPDATE pages SET {column}=? WHERE page_id=?", (value, PAGE_ID))
    _record("pages", PAGE_ID, **page_values)

    connection.execute(
        "INSERT INTO tags (tag_id, name, created_at, updated_at) VALUES (?, '标签', ?, ?)",
        (TAG_ID, NOW, NOW),
    )
    _record("tags", TAG_ID, tag_id=TAG_ID, name="标签", created_at=NOW, updated_at=NOW)
    connection.execute("INSERT INTO book_tags (book_id, tag_id) VALUES (?, ?)", (BOOK_ID, TAG_ID))
    connection.execute(
        "INSERT INTO regions (region_id, page_id, region_type, reading_order, geometry_json,"
        " text_json, style_json, sfx_policy, region_locked, translation_locked, inpaint_locked,"
        " created_at, updated_at)"
        " VALUES (?, ?, 'speech', 1, '{\"x\":1,\"y\":2,\"w\":3,\"h\":4}', '{\"text\":\"hello\"}',"
        " '{\"size\":12}', 'translate', 1, 1, 0, ?, ?)",
        (REGION_ID, PAGE_ID, NOW, NOW),
    )
    _record(
        "regions",
        REGION_ID,
        region_id=REGION_ID,
        page_id=PAGE_ID,
        region_type="speech",
        reading_order=1,
        geometry_json='{"x":1,"y":2,"w":3,"h":4}',
        text_json='{"text":"hello"}',
        style_json='{"size":12}',
        sfx_policy="translate",
        region_locked=1,
        translation_locked=1,
        inpaint_locked=0,
        created_at=NOW,
        updated_at=NOW,
    )
    connection.execute(
        "INSERT INTO region_revisions (region_revision_id, region_id, revision_no,"
        " snapshot_json, origin, review_state, source_run_id, created_at)"
        " VALUES (?, ?, 1, '{\"snap\":1}', 'imported', 'confirmed', NULL, ?)",
        (REGION_REVISION_ID, REGION_ID, NOW),
    )
    _record(
        "region_revisions",
        REGION_REVISION_ID,
        region_revision_id=REGION_REVISION_ID,
        region_id=REGION_ID,
        revision_no=1,
        snapshot_json='{"snap":1}',
        origin="imported",
        review_state="confirmed",
        created_at=NOW,
    )


def _seed_v3(connection: sqlite3.Connection) -> None:
    run_values = {
        "command_type": "translate",
        "scope_type": "page",
        "requested_targets_json": '{"targets":[{"page_id":"page-1"}]}',
        "settings_snapshot_json": '{"quality":"high"}',
        "provider_binding_snapshot_json": '{"provider":"local"}',
        "context_policy_json": '{"policy":"page"}',
        "status": "succeeded",
        "run_json": '{"run":1}',
        "updated_at": NOW,
    }
    connection.execute(
        "INSERT INTO pipeline_runs (run_id, command_type, scope_type, requested_targets_json,"
        " settings_snapshot_json, provider_binding_snapshot_json, context_policy_json, status,"
        " run_json, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            RUN_ID,
            run_values["command_type"],
            run_values["scope_type"],
            run_values["requested_targets_json"],
            run_values["settings_snapshot_json"],
            run_values["provider_binding_snapshot_json"],
            run_values["context_policy_json"],
            run_values["status"],
            run_values["run_json"],
            run_values["updated_at"],
        ),
    )
    _record("pipeline_runs", RUN_ID, run_id=RUN_ID, **run_values)

    target_values = {
        "pipeline_run_id": RUN_ID,
        "target_id": "target-1",
        "target_type": "page",
        "page_id": PAGE_ID,
        "region_id": None,
        "target_order": 0,
        "snapshot_json": '{"target":1}',
    }
    connection.execute(
        "INSERT INTO pipeline_run_targets (run_target_id, pipeline_run_id, target_id,"
        " target_type, page_id, region_id, target_order, snapshot_json)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            RUN_TARGET_ID,
            target_values["pipeline_run_id"],
            target_values["target_id"],
            target_values["target_type"],
            target_values["page_id"],
            target_values["region_id"],
            target_values["target_order"],
            target_values["snapshot_json"],
        ),
    )
    _record("pipeline_run_targets", RUN_TARGET_ID, run_target_id=RUN_TARGET_ID, **target_values)

    task_values = {
        "pipeline_run_id": RUN_ID,
        "run_target_id": RUN_TARGET_ID,
        "target_id": "target-1",
        "target_type": "page",
        "page_id": PAGE_ID,
        "region_id": None,
        "status": "succeeded",
        "units_json": '{"units":[1]}',
        "step_run_ids_json": '["step-run-1"]',
    }
    connection.execute(
        "INSERT INTO pipeline_tasks (task_id, pipeline_run_id, run_target_id, target_id,"
        " target_type, page_id, region_id, status, units_json, step_run_ids_json)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            TASK_ID,
            task_values["pipeline_run_id"],
            task_values["run_target_id"],
            task_values["target_id"],
            task_values["target_type"],
            task_values["page_id"],
            task_values["region_id"],
            task_values["status"],
            task_values["units_json"],
            task_values["step_run_ids_json"],
        ),
    )
    _record("pipeline_tasks", TASK_ID, task_id=TASK_ID, **task_values)

    step_values = {
        "pipeline_run_id": RUN_ID,
        "task_id": TASK_ID,
        "target_id": "target-1",
        "page_id": PAGE_ID,
        "region_id": None,
        "step_type": "translate",
        "unit_id": "unit-1",
        "status": "succeeded",
        "input_refs_json": '{"refs":[{"artifact_id":"artifact-1"}]}',
        "lock_snapshot_json": '{"locks":[]}',
        "retry_no": 1,
        "error_code": None,
        "error_detail": None,
        "output_json": '{"output":1}',
    }
    connection.execute(
        "INSERT INTO step_runs (step_run_id, pipeline_run_id, task_id, target_id, page_id,"
        " region_id, step_type, unit_id, status, input_refs_json, lock_snapshot_json,"
        " retry_no, error_code, error_detail, output_json)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            STEP_RUN_ID,
            step_values["pipeline_run_id"],
            step_values["task_id"],
            step_values["target_id"],
            step_values["page_id"],
            step_values["region_id"],
            step_values["step_type"],
            step_values["unit_id"],
            step_values["status"],
            step_values["input_refs_json"],
            step_values["lock_snapshot_json"],
            step_values["retry_no"],
            step_values["error_code"],
            step_values["error_detail"],
            step_values["output_json"],
        ),
    )
    _record("step_runs", STEP_RUN_ID, step_run_id=STEP_RUN_ID, **step_values)

    candidate_values = {
        "pipeline_run_id": RUN_ID,
        "step_run_id": STEP_RUN_ID,
        "target_id": "target-1",
        "page_id": PAGE_ID,
        "region_id": None,
        "result_kind": "translated_page",
        "base_revision_id": None,
        "payload_json": '{"payload":1}',
        "reason": "automatic",
        "status": "applied",
        "created_at": NOW,
        "resolved_at": None,
    }
    connection.execute(
        "INSERT INTO step_result_candidates (candidate_id, pipeline_run_id, step_run_id,"
        " target_id, page_id, region_id, result_kind, base_revision_id, payload_json, reason,"
        " status, created_at, resolved_at)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            CANDIDATE_ID,
            candidate_values["pipeline_run_id"],
            candidate_values["step_run_id"],
            candidate_values["target_id"],
            candidate_values["page_id"],
            candidate_values["region_id"],
            candidate_values["result_kind"],
            candidate_values["base_revision_id"],
            candidate_values["payload_json"],
            candidate_values["reason"],
            candidate_values["status"],
            candidate_values["created_at"],
            candidate_values["resolved_at"],
        ),
    )
    _record("step_result_candidates", CANDIDATE_ID, candidate_id=CANDIDATE_ID, **candidate_values)


def _seed_v4(connection: sqlite3.Connection) -> None:
    progress_values = {
        "book_id": BOOK_ID,
        "chapter_id": CHAPTER_ID,
        "mode": "translated",
        "last_page_id": PAGE_ID,
        "last_read_at": NOW,
        "updated_at": NOW,
    }
    connection.execute(
        "INSERT INTO reading_progress (progress_id, book_id, chapter_id, mode,"
        " last_page_id, last_read_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            PROGRESS_ID,
            progress_values["book_id"],
            progress_values["chapter_id"],
            progress_values["mode"],
            progress_values["last_page_id"],
            progress_values["last_read_at"],
            progress_values["updated_at"],
        ),
    )
    _record("reading_progress", PROGRESS_ID, progress_id=PROGRESS_ID, **progress_values)

    export_values = {
        "book_id": BOOK_ID,
        "chapter_id": CHAPTER_ID,
        "pipeline_run_id": RUN_ID,
        "export_type": "pdf",
        "scope_snapshot_json": '{"scope":"chapter"}',
        "output_path": "exports/chapter-1.pdf",
        "render_profile_snapshot_json": '{"profile":"default"}',
        "status": "completed",
        "file_hash": "export-hash-1",
        "created_at": NOW,
        "completed_at": NOW,
        "detail": "ok",
    }
    connection.execute(
        "INSERT INTO export_history (export_id, book_id, chapter_id, pipeline_run_id,"
        " export_type, scope_snapshot_json, output_path, render_profile_snapshot_json,"
        " status, file_hash, created_at, completed_at, detail)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            EXPORT_ID,
            export_values["book_id"],
            export_values["chapter_id"],
            export_values["pipeline_run_id"],
            export_values["export_type"],
            export_values["scope_snapshot_json"],
            export_values["output_path"],
            export_values["render_profile_snapshot_json"],
            export_values["status"],
            export_values["file_hash"],
            export_values["created_at"],
            export_values["completed_at"],
            export_values["detail"],
        ),
    )
    _record("export_history", EXPORT_ID, export_id=EXPORT_ID, **export_values)


def _seed_v5(connection: sqlite3.Connection) -> None:
    connection.execute(
        "INSERT INTO book_cleanup_manifests (book_id, targets_json, created_at)"
        " VALUES (?, '{\"targets\":[]}', ?)",
        (BOOK_ID, NOW),
    )
    _record(
        "book_cleanup_manifests",
        BOOK_ID,
        book_id=BOOK_ID,
        targets_json='{"targets":[]}',
        created_at=NOW,
    )


def _table_names(connection: sqlite3.Connection) -> set[str]:
    return {
        row["name"]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall()
    }


def _assert_v1_rows(connection: sqlite3.Connection) -> None:
    """Assert the v1-era rows only (used for the v1-start-upgrade test)."""
    assert EXPECTED, "seed functions did not record any expected values"
    for (table, id_value), expected in EXPECTED.items():
        if table not in V1_COLUMNS:
            continue
        id_column = ID_COLUMNS[table]
        row = connection.execute(
            f"SELECT * FROM {table} WHERE {id_column} = ?", (id_value,)
        ).fetchone()
        assert row is not None, f"seeded v1 row missing after upgrade: {table}.{id_value}"
        for column in V1_COLUMNS[table]:
            assert row[column] == expected[column], (
                f"{table}.{id_value}.{column}: {row[column]!r} != {expected[column]!r}"
            )


def _assert_expected(connection: sqlite3.Connection) -> None:
    """Every seeded row must be identical after the upgrade (all seeded columns)."""
    assert EXPECTED, "seed functions did not record any expected values"
    for (table, id_value), expected in EXPECTED.items():
        id_column = ID_COLUMNS[table]
        row = connection.execute(
            f"SELECT * FROM {table} WHERE {id_column} = ?", (id_value,)
        ).fetchone()
        assert row is not None, f"seeded row missing after upgrade: {table}.{id_value}"
        for column, value in expected.items():
            assert row[column] == value, (
                f"{table}.{id_value}.{column}: {row[column]!r} != {value!r}"
            )


def _assert_latest(connection: sqlite3.Connection) -> None:
    assert read_schema_version(connection) == LATEST_VERSION
    names = _table_names(connection)
    missing = [name for name in LATEST_TABLES if name not in names]
    assert not missing, f"latest schema is missing tables: {missing}"
    assert connection.execute("PRAGMA integrity_check").fetchone()[0] == "ok"

    # Key column/index/foreign-key structure of the migrated schema.
    expected_columns = {
        "books": {"original_title", "author", "is_favorite", "is_archived"},
        "chapters": {"chapter_number", "chapter_type", "reading_direction"},
        "pages": {"source_filename", "source_hash", "page_locked", "review_state"},
        "regions": {"geometry_json", "text_json", "region_locked", "sfx_policy"},
        "step_runs": {"input_refs_json", "lock_snapshot_json", "output_json"},
        "pipeline_tasks": {"units_json", "step_run_ids_json"},
        "plugin_state": {"manifest_json", "last_error"},
    }
    for table, columns in expected_columns.items():
        actual = {
            row["name"]
            for row in connection.execute(f"PRAGMA table_info({table})").fetchall()
        }
        assert columns <= actual, f"{table} missing columns: {columns - actual}"
    indexes = {
        row["name"]
        for row in connection.execute("PRAGMA index_list(chapters)").fetchall()
    }
    assert "idx_chapters_book_id" in indexes
    foreign_keys = connection.execute("PRAGMA foreign_key_list(chapters)").fetchall()
    assert foreign_keys, "chapters lost its foreign key to books"
    step_indexes = {
        row["name"] for row in connection.execute("PRAGMA index_list(step_runs)").fetchall()
    }
    assert "idx_step_runs_run" in step_indexes


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
    _assert_expected(connection)
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
    assert LEGACY_VERSIONS == list(range(1, LATEST_VERSION)), (
        "legacy versions must be the contiguous prefix of the migration chain"
    )
    connection = _build_legacy_database(tmp_path / "legacy-v1.db", 1)
    v1_tables = _table_names(connection)
    assert v1_tables == FROZEN_V1_TABLES, (
        f"v1 table set changed: extra={v1_tables - FROZEN_V1_TABLES} "
        f"missing={FROZEN_V1_TABLES - v1_tables}"
    )
    for later_table in LATEST_TABLES:
        assert later_table not in v1_tables

    MigrationRunner(connection, MIGRATIONS).apply_pending()
    _assert_latest(connection)
    _assert_v1_rows(connection)
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
    _assert_expected(connection)
    connection.close()

