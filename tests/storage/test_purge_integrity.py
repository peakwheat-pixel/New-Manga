"""TASK-044: purge integrity (F-2), generated-asset scope (F-6), manifest
atomicity/rebuild (F-7) and soft-delete visibility for import dedup (F-10).

The fixture builds a **complete** page graph — every table that references
``pages`` gets a row (asserted up front, so the suite can never go back to the
"pages row only" fixture that kept F-2 green), created through the production
artifact repository where an API exists and explicit SQL for the pipeline
tables.

Real SQLite with ``PRAGMA foreign_keys = ON`` + real ``ManagedFileStorage``:
nothing here turns foreign keys off, and every purge assertion is paired with
``PRAGMA foreign_key_check``.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from application.maintenance import TrashService  # noqa: E402
from application.maintenance.trash import _JsonTrashManifest  # noqa: E402
from infrastructure.filesystem.managed_storage import (  # noqa: E402
    ImmutablePathViolation,
    ManagedFileStorage,
)
from infrastructure.sqlite.artifacts import SqliteArtifactRepository  # noqa: E402
from infrastructure.sqlite.connection import open_database  # noqa: E402
from infrastructure.sqlite.library import SqliteLibraryRepository  # noqa: E402
from infrastructure.sqlite.migrator import MigrationRunner  # noqa: E402
from infrastructure.sqlite.schema import default_migrations  # noqa: E402
from ports.repositories.artifacts import (  # noqa: E402
    ArtifactType,
    ContentProvider,
    NewArtifact,
    PendingArtifactCommit,
)

NOW = "2026-09-18T06:00:00+00:00"


def _tables_referencing(conn, parent: str) -> list[tuple[str, str]]:
    """(child_table, child_column) for every FK whose parent is ``parent``.

    Derived at run time from ``PRAGMA foreign_key_list`` so a future migration
    that adds another referencing table makes these tests fail loudly instead
    of silently leaving orphan rows behind.
    """
    tables = [
        row["name"]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
            " AND name NOT LIKE 'sqlite_%' ORDER BY name"
        ).fetchall()
    ]
    edges: list[tuple[str, str]] = []
    for table in tables:
        for row in conn.execute(f'PRAGMA foreign_key_list("{table}")').fetchall():
            if row["table"] == parent:
                edges.append((table, row["from"]))
    return edges


def _fk_violations(conn) -> list:
    return conn.execute("PRAGMA foreign_key_check").fetchall()


@pytest.fixture()
def purge_world(tmp_path: Path):
    """book/chapter + one complete page with a full dependent graph."""
    conn, _opened = open_database(
        tmp_path / "library.db",
        latest_known_schema_version=max(m.schema_version for m in default_migrations()),
    )
    MigrationRunner(conn, default_migrations()).apply_pending()
    storage_root = tmp_path / "managed"
    storage = ManagedFileStorage(storage_root)
    storage.ensure_layout()
    repository = SqliteLibraryRepository(conn)
    artifacts = SqliteArtifactRepository(conn, storage)

    user_source = tmp_path / "user-side" / "original-art.tiff"
    user_source.parent.mkdir(parents=True, exist_ok=True)
    user_source.write_bytes(b"USER SOURCE BYTES")

    with conn:
        conn.execute(
            "INSERT INTO books (book_id, title, created_at, updated_at)"
            " VALUES ('book-1','Book',?,?)",
            (NOW, NOW),
        )
        conn.execute(
            "INSERT INTO chapters (chapter_id, book_id, title, created_at, updated_at)"
            " VALUES ('chapter-1','book-1','Chapter',?,?)",
            (NOW, NOW),
        )

    def add_page(page_id: str, source_order: int = 1) -> dict:
        relative = f"books/book-1/chapters/chapter-1/original/{page_id}.png"
        target = storage_root / Path(relative.replace("/", "\\"))
        target.parent.mkdir(parents=True, exist_ok=True)
        payload = f"original-{page_id}".encode()
        target.write_bytes(payload)
        with conn:
            conn.execute(
                "INSERT INTO pages (page_id, chapter_id, sort_order, created_at,"
                " updated_at, source_filename, source_order, source_hash,"
                " source_size_bytes, width, height, managed_original_ref)"
                " VALUES (?, 'chapter-1', ?, ?, ?, ?, ?, ?, ?, 4, 3, ?)",
                (
                    page_id,
                    source_order,
                    NOW,
                    NOW,
                    f"{page_id}.png",
                    source_order,
                    hashlib.sha256(payload).hexdigest(),
                    len(payload),
                    relative,
                ),
            )
        return {"page_id": page_id, "managed_original_ref": relative, "payload": payload}

    def add_dependents(page_id: str, *, source_revision_id: str | None = None) -> dict:
        """Real artifact + two revisions (rev2 derives from rev1), a region with
        two revisions (rr2 restored from rr1) and a full pipeline chain."""
        artifact = artifacts.create_artifact(
            NewArtifact(
                book_id="book-1",
                chapter_id="chapter-1",
                page_id=page_id,
                artifact_type=ArtifactType.TRANSLATED,
            )
        )
        rev1 = artifacts.commit_revision(
            PendingArtifactCommit(
                artifact_id=artifact.artifact_id,
                content_provider=ContentProvider(payload=f"rev1-{page_id}".encode()),
                mime_type="image/png",
                expected_current_revision_id=None,
                source_artifact_revision_id=source_revision_id,
                file_suffix=".png",
            )
        ).revision
        rev2 = artifacts.commit_revision(
            PendingArtifactCommit(
                artifact_id=artifact.artifact_id,
                content_provider=ContentProvider(payload=f"rev2-{page_id}".encode()),
                mime_type="image/png",
                expected_current_revision_id=rev1.artifact_revision_id,
                source_artifact_revision_id=rev1.artifact_revision_id,
                file_suffix=".png",
            )
        ).revision
        region_id = f"region-{page_id}"
        with conn:
            conn.execute(
                "INSERT INTO regions (region_id, page_id, region_type, geometry_json,"
                " text_json, style_json, created_at, updated_at)"
                " VALUES (?, ?, 'speech', '{}', '{}', '{}', ?, ?)",
                (region_id, page_id, NOW, NOW),
            )
            conn.execute(
                "INSERT INTO region_revisions (region_revision_id, region_id,"
                " revision_no, snapshot_json, origin, review_state, created_at)"
                " VALUES (?, ?, 1, '{}', 'machine', 'unreviewed', ?)",
                (f"rr1-{page_id}", region_id, NOW),
            )
            conn.execute(
                "INSERT INTO region_revisions (region_revision_id, region_id,"
                " revision_no, snapshot_json, origin, review_state,"
                " restored_from_revision_id, created_at)"
                " VALUES (?, ?, 2, '{}', 'restored', 'unreviewed', ?, ?)",
                (f"rr2-{page_id}", region_id, f"rr1-{page_id}", NOW),
            )
            conn.execute(
                "UPDATE regions SET current_revision_id = ? WHERE region_id = ?",
                (f"rr2-{page_id}", region_id),
            )
            run_id = f"run-{page_id}"
            conn.execute(
                "INSERT INTO pipeline_runs (run_id, command_type, scope_type,"
                " requested_targets_json, settings_snapshot_json,"
                " provider_binding_snapshot_json, context_policy_json, status,"
                " run_json, updated_at)"
                " VALUES (?, 'translate', 'page', '[]', '{}', '{}', '{}', 'done', '{}', ?)",
                (run_id, NOW),
            )
            conn.execute(
                "INSERT INTO pipeline_run_targets (run_target_id, pipeline_run_id,"
                " target_id, target_type, page_id, target_order, snapshot_json)"
                " VALUES (?, ?, ?, 'page', ?, 0, '{}')",
                (f"rt-{page_id}", run_id, page_id, page_id),
            )
            conn.execute(
                "INSERT INTO pipeline_tasks (task_id, pipeline_run_id, run_target_id,"
                " target_id, target_type, page_id, status, units_json,"
                " step_run_ids_json) VALUES (?, ?, ?, ?, 'page', ?, 'done', '{}', '[]')",
                (f"task-{page_id}", run_id, f"rt-{page_id}", page_id, page_id),
            )
            conn.execute(
                "INSERT INTO step_runs (step_run_id, pipeline_run_id, task_id,"
                " target_id, page_id, step_type, unit_id, status, input_refs_json,"
                " lock_snapshot_json, output_json)"
                " VALUES (?, ?, ?, ?, ?, 'translate', 'unit-1', 'done', '[]', '{}', '{}')",
                (f"step-{page_id}", run_id, f"task-{page_id}", page_id, page_id),
            )
            conn.execute(
                "INSERT INTO step_run_output_refs (step_run_id, output_order, ref_key,"
                " value_json) VALUES (?, 0, 'out', '{}')",
                (f"step-{page_id}",),
            )
            conn.execute(
                "INSERT INTO step_result_candidates (candidate_id, pipeline_run_id,"
                " step_run_id, target_id, page_id, result_kind, payload_json, reason,"
                " status, created_at) VALUES (?, ?, ?, ?, ?, 'text', '{}', 'ok',"
                " 'accepted', ?)",
                (f"cand-{page_id}", run_id, f"step-{page_id}", page_id, page_id, NOW),
            )
            conn.execute(
                "INSERT INTO pipeline_stage_states (target_type, target_id, stage,"
                " status, updated_at) VALUES ('page', ?, 'translate', 'done', ?)",
                (page_id, NOW),
            )
            conn.execute(
                "INSERT INTO pipeline_stage_states (target_type, target_id, stage,"
                " status, updated_at) VALUES ('region', ?, 'translate', 'done', ?)",
                (region_id, NOW),
            )
        return {
            "artifact_id": artifact.artifact_id,
            "revisions": (rev1.artifact_revision_id, rev2.artifact_revision_id),
            "revision_paths": (rev1.managed_path, rev2.managed_path),
            "region_id": region_id,
            "run_id": run_id,
        }

    manifest_path = storage_root / "trash-manifest.json"
    service = TrashService(repository, storage, _JsonTrashManifest(manifest_path))
    yield {
        "conn": conn,
        "repository": repository,
        "artifacts": artifacts,
        "storage": storage,
        "storage_root": storage_root,
        "service": service,
        "manifest_path": manifest_path,
        "add_page": add_page,
        "add_dependents": add_dependents,
        "user_source": user_source,
        "tmp_path": tmp_path,
    }
    conn.close()


def test_fixture_populates_every_table_that_references_pages(purge_world) -> None:
    """Guard for the fixture itself: F-2 stayed hidden because the old fixture
    created only a ``pages`` row, so an empty dependent graph must fail here."""
    conn = purge_world["conn"]
    page = purge_world["add_page"]("p1")
    purge_world["add_dependents"]("p1")

    referenced = _tables_referencing(conn, "pages")
    assert {table for table, _ in referenced} == {
        "media_artifacts",
        "pipeline_run_targets",
        "pipeline_tasks",
        "regions",
        "step_result_candidates",
        "step_runs",
    }
    populated = {}
    for table, column in referenced:
        populated[table] = conn.execute(
            f'SELECT COUNT(*) FROM "{table}" WHERE "{column}" = ?', (page["page_id"],)
        ).fetchone()[0]
    assert all(count > 0 for count in populated.values()), populated
    assert conn.execute("SELECT COUNT(*) FROM artifact_revisions").fetchone()[0] == 2
    assert conn.execute("SELECT COUNT(*) FROM region_revisions").fetchone()[0] == 2
    assert conn.execute("SELECT COUNT(*) FROM step_run_output_refs").fetchone()[0] == 1
    assert conn.execute("SELECT COUNT(*) FROM pipeline_stage_states").fetchone()[0] == 2
    assert _fk_violations(conn) == []


def test_purge_batch_removes_every_row_referencing_the_page(purge_world) -> None:
    """F-2 / AC ①: a page that really has artifacts and pipeline rows purges."""
    conn = purge_world["conn"]
    page = purge_world["add_page"]("p1")
    dependents = purge_world["add_dependents"]("p1")
    batch = purge_world["service"].soft_delete_pages("chapter-1", ["p1"])

    purge_world["service"].purge_batch(batch.batch_id)

    for table, column in _tables_referencing(conn, "pages"):
        remaining = conn.execute(
            f'SELECT COUNT(*) FROM "{table}" WHERE "{column}" = ?', (page["page_id"],)
        ).fetchone()[0]
        assert remaining == 0, f"{table}.{column} still references the purged page"
    assert (
        conn.execute(
            "SELECT COUNT(*) FROM artifact_revisions WHERE artifact_id = ?",
            (dependents["artifact_id"],),
        ).fetchone()[0]
        == 0
    )
    assert (
        conn.execute(
            "SELECT COUNT(*) FROM region_revisions WHERE region_id = ?",
            (dependents["region_id"],),
        ).fetchone()[0]
        == 0
    )
    assert (
        conn.execute(
            "SELECT COUNT(*) FROM pipeline_stage_states WHERE target_id IN (?, ?)",
            (page["page_id"], dependents["region_id"]),
        ).fetchone()[0]
        == 0
    )
    assert _fk_violations(conn) == []
    assert purge_world["service"].list_batches() == []


def test_purge_cannot_be_restored_into_a_dangling_page(purge_world) -> None:
    """AC ②: after purge the page cannot come back pointing at a missing file."""
    storage = purge_world["storage"]
    page = purge_world["add_page"]("p1")
    purge_world["add_dependents"]("p1")
    managed_file = Path(storage.absolute_path(page["managed_original_ref"]))
    assert managed_file.is_file()
    batch = purge_world["service"].soft_delete_pages("chapter-1", ["p1"])

    purge_world["service"].purge_batch(batch.batch_id)

    with pytest.raises(KeyError, match="unknown trash batch"):
        purge_world["service"].restore_batch(batch.batch_id)
    assert purge_world["repository"].get_pages_by_ids(["p1"]) == []
    assert not managed_file.exists()


def test_purge_deletes_generated_assets_and_keeps_unrelated_files(purge_world) -> None:
    """F-6: permanent delete covers the page's generated assets as well as the
    managed original — and still nothing outside the managed root."""
    storage_root: Path = purge_world["storage_root"]
    page = purge_world["add_page"]("p1")
    dependents = purge_world["add_dependents"]("p1")
    other_page = purge_world["add_page"]("p2")
    other_dependents = purge_world["add_dependents"]("p2")
    generated = [(storage_root / path).is_file() for path in dependents["revision_paths"]]
    assert all(generated), "fixture must have real generated assets on disk"
    # a page that is not being purged keeps everything
    assert (storage_root / other_page["managed_original_ref"]).is_file()
    batch = purge_world["service"].soft_delete_pages("chapter-1", ["p1"])

    purge_world["service"].purge_batch(batch.batch_id)

    for path in dependents["revision_paths"]:
        assert not (storage_root / path).exists(), f"generated asset kept: {path}"
    assert not (storage_root / page["managed_original_ref"]).exists()
    for path in other_dependents["revision_paths"]:
        assert (storage_root / path).is_file(), "another page's asset was deleted"
    assert (storage_root / other_page["managed_original_ref"]).is_file()
    assert purge_world["user_source"].read_bytes() == b"USER SOURCE BYTES"


def test_purge_refuses_generated_asset_paths_outside_the_managed_root(purge_world) -> None:
    """F-6 keeps the boundary: a managed path escaping the root is refused and
    the outside file survives verbatim (``remove_managed`` is not relaxed)."""
    storage_root: Path = purge_world["storage_root"]
    outside = purge_world["tmp_path"] / "outside.png"
    outside.write_bytes(b"precious")
    purge_world["add_page"]("p1")
    dependents = purge_world["add_dependents"]("p1")
    with purge_world["conn"]:
        purge_world["conn"].execute(
            "UPDATE artifact_revisions SET managed_path = '../outside.png'"
            " WHERE artifact_revision_id = ?",
            (dependents["revisions"][1],),
        )
    batch = purge_world["service"].soft_delete_pages("chapter-1", ["p1"])

    with pytest.raises(ImmutablePathViolation):
        purge_world["service"].purge_batch(batch.batch_id)

    assert outside.read_bytes() == b"precious"


def test_purge_clears_cross_page_provenance_instead_of_failing(purge_world) -> None:
    """A revision on another page deriving from a purged revision must not make
    the permanent delete impossible: the dangling provenance pointer is
    cleared, the surviving revision and its file stay."""
    conn = purge_world["conn"]
    storage_root: Path = purge_world["storage_root"]
    purge_world["add_page"]("p1")
    source = purge_world["add_dependents"]("p1")
    purge_world["add_page"]("p2")
    derived = purge_world["add_dependents"](
        "p2", source_revision_id=source["revisions"][1]
    )
    batch = purge_world["service"].soft_delete_pages("chapter-1", ["p1"])

    purge_world["service"].purge_batch(batch.batch_id)

    row = conn.execute(
        "SELECT source_artifact_revision_id FROM artifact_revisions"
        " WHERE artifact_id = ? ORDER BY revision_no LIMIT 1",
        (derived["artifact_id"],),
    ).fetchone()
    assert row is not None, "the surviving page's revision must stay"
    assert row["source_artifact_revision_id"] is None
    for path in derived["revision_paths"]:
        assert (storage_root / path).is_file()
    assert _fk_violations(conn) == []


def test_soft_deleted_pages_do_not_block_reimport_dedup(purge_world) -> None:
    """F-10: a trashed page must not silently swallow a re-import.

    ``existing_source_hashes`` hides soft-deleted rows (re-importing the same
    file produces a page again instead of "skipped, but the chapter looks
    empty"). ``max_source_order`` intentionally keeps counting them so a
    restored page can never collide with a newly imported one — see the
    Handoff for that split and the port-docstring drift it implies.
    """
    repository = purge_world["repository"]
    page = purge_world["add_page"]("p1", source_order=1)
    purge_world["add_page"]("p2", source_order=2)
    source_hash = hashlib.sha256(page["payload"]).hexdigest()

    assert repository.existing_source_hashes("chapter-1") == {
        source_hash,
        hashlib.sha256(b"original-p2").hexdigest(),
    }
    assert repository.max_source_order("chapter-1") == 2

    purge_world["service"].soft_delete_pages("chapter-1", ["p1"])

    assert source_hash not in repository.existing_source_hashes("chapter-1")
    # unchanged on purpose: the trashed page keeps its order slot
    assert repository.max_source_order("chapter-1") == 2


def test_batches_survive_a_corrupt_manifest(purge_world) -> None:
    """F-7: the ledger is derivable from the store (``deleted_at`` *is* the
    batch identity), so a truncated manifest degrades to a rebuild instead of
    disabling restore/purge."""
    service = purge_world["service"]
    purge_world["add_page"]("p1")
    purge_world["add_page"]("p2")
    batch = service.soft_delete_pages("chapter-1", ["p1", "p2"])

    purge_world["manifest_path"].write_text('{"batches": [{"batch_id": "tru', encoding="utf-8")

    rebuilt = service.list_batches()
    assert len(rebuilt) == 1
    assert rebuilt[0].page_ids == ("p1", "p2")
    assert rebuilt[0].chapter_id == "chapter-1"
    assert rebuilt[0].deleted_at == batch.deleted_at

    assert service.restore_batch(rebuilt[0].batch_id) == 2
    restored = purge_world["repository"].get_pages_by_ids(["p1", "p2"])
    assert {page.page_id for page in restored} == {"p1", "p2"}
    assert all(page.deleted_at is None for page in restored)
    assert len(purge_world["repository"].list_pages("chapter-1")) == 2
    assert service.list_batches() == []


def test_manifest_write_is_atomic(purge_world, monkeypatch) -> None:
    """F-7: a crash during the manifest write must leave the previous manifest
    intact — never a truncated half-written file."""
    service = purge_world["service"]
    manifest_path: Path = purge_world["manifest_path"]
    purge_world["add_page"]("p1")
    purge_world["add_page"]("p2")
    first = service.soft_delete_pages("chapter-1", ["p1"])
    before = manifest_path.read_text(encoding="utf-8")
    assert [item["batch_id"] for item in json.loads(before)["batches"]] == [first.batch_id]

    def explode(*args, **kwargs):
        raise OSError("injected failure before the manifest swap")

    monkeypatch.setattr(os, "replace", explode)
    with pytest.raises(OSError):
        service.soft_delete_pages("chapter-1", ["p2"])

    # the previous manifest is byte-identical and still parses
    assert manifest_path.read_text(encoding="utf-8") == before
    assert [item["batch_id"] for item in json.loads(before)["batches"]] == [first.batch_id]
    leftovers = [
        path.name
        for path in manifest_path.parent.iterdir()
        if path.name.startswith(".") and "tmp" in path.name
    ]
    assert leftovers == []
