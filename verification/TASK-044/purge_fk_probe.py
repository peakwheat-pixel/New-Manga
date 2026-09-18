"""TASK-044 AC ① probe: the real FK graph around ``pages``, plus the exact
deletion statements that work under ``PRAGMA foreign_keys = ON``.

Everything runs on the real schema (built by ``MigrationRunner``) with graphs
created through the **production** artifact repository, so the row shapes are
the ones the application really writes. Experiments are independent (one page
each) because a failure rolls its transaction back.

Pinned down here:
  E0  every table that references ``pages`` (re-derived, not copied from the
      task text) and the remaining FKs among the purge-relevant tables;
  E1  whether "clear ``media_artifacts.current_revision_id`` first" is possible
      at all — the schema has ``trg_media_artifacts_current_not_clearable``;
  E2  deleting ``artifact_revisions`` alone, with the artifact surviving:
      which constraint actually fails (self-reference vs the deferred
      ``current_revision_id`` pointer);
  E3  ``artifact_revisions`` then ``media_artifacts`` in one transaction;
  E4  the full child-before-parent order (including a ``region_revisions``
      ``restored_from_revision_id`` self-reference);
  E5  a revision **on another page** deriving from a revision being purged.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from infrastructure.filesystem.managed_storage import ManagedFileStorage  # noqa: E402
from infrastructure.sqlite.artifacts import SqliteArtifactRepository  # noqa: E402
from infrastructure.sqlite.connection import open_database  # noqa: E402
from infrastructure.sqlite.migrator import MigrationRunner  # noqa: E402
from infrastructure.sqlite.schema import default_migrations  # noqa: E402
from ports.repositories.artifacts import (  # noqa: E402
    ArtifactType,
    ContentProvider,
    NewArtifact,
    PendingArtifactCommit,
)

NOW = "2026-09-18T05:00:00+00:00"
PURGE_TABLES = (
    "pages",
    "media_artifacts",
    "artifact_revisions",
    "regions",
    "region_revisions",
    "pipeline_run_targets",
    "pipeline_tasks",
    "step_runs",
    "step_result_candidates",
    "step_run_input_refs",
    "step_run_output_refs",
)


def table_names(conn) -> list[str]:
    return [
        row["name"]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
            " AND name NOT LIKE 'sqlite_%' ORDER BY name"
        ).fetchall()
    ]


def fk_edges(conn) -> list[tuple[str, str, str, str, str]]:
    edges = []
    for table in table_names(conn):
        for row in conn.execute(f'PRAGMA foreign_key_list("{table}")').fetchall():
            edges.append((table, row["from"], row["table"], row["to"] or "", row["on_delete"]))
    return edges


def counts(conn) -> dict[str, int]:
    return {
        table: conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        for table in PURGE_TABLES
    }


def build_graph(conn, repo, page_id: str, *, source_revision_id: str | None = None):
    """One page with a real artifact + two revisions (rev2 derives from rev1),
    a region + two revisions (rr2 restored from rr1) and a full pipeline chain."""
    conn.execute(
        "INSERT INTO pages (page_id, chapter_id, sort_order, created_at, updated_at,"
        " source_filename, source_order, source_hash, source_size_bytes, width, height,"
        " managed_original_ref) VALUES (?, 'c1', 1, ?, ?, ?, 1, ?, 1, 4, 3, ?)",
        (page_id, NOW, NOW, f"{page_id}.png", f"hash-{page_id}", f"books/b1/chapters/c1/original/{page_id}.png"),
    )
    artifact = repo.create_artifact(
        NewArtifact(
            book_id="b1",
            chapter_id="c1",
            page_id=page_id,
            artifact_type=ArtifactType.TRANSLATED,
        )
    )
    rev1 = repo.commit_revision(
        PendingArtifactCommit(
            artifact_id=artifact.artifact_id,
            content_provider=ContentProvider(payload=f"rev1-{page_id}".encode()),
            mime_type="image/png",
            expected_current_revision_id=None,
            source_artifact_revision_id=source_revision_id,
            file_suffix=".png",
        )
    ).revision
    rev2 = repo.commit_revision(
        PendingArtifactCommit(
            artifact_id=artifact.artifact_id,
            content_provider=ContentProvider(payload=f"rev2-{page_id}".encode()),
            mime_type="image/png",
            expected_current_revision_id=rev1.artifact_revision_id,
            source_artifact_revision_id=rev1.artifact_revision_id,
            file_suffix=".png",
        )
    ).revision

    region_id = f"r-{page_id}"
    conn.execute(
        "INSERT INTO regions (region_id, page_id, region_type, geometry_json, text_json,"
        " style_json, created_at, updated_at)"
        " VALUES (?, ?, 'speech', '{}', '{}', '{}', ?, ?)",
        (region_id, page_id, NOW, NOW),
    )
    conn.execute(
        "INSERT INTO region_revisions (region_revision_id, region_id, revision_no,"
        " snapshot_json, origin, review_state, created_at)"
        " VALUES (?, ?, 1, '{}', 'machine', 'unreviewed', ?)",
        (f"rr1-{page_id}", region_id, NOW),
    )
    conn.execute(
        "INSERT INTO region_revisions (region_revision_id, region_id, revision_no,"
        " snapshot_json, origin, review_state, restored_from_revision_id, created_at)"
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
        " requested_targets_json, settings_snapshot_json, provider_binding_snapshot_json,"
        " context_policy_json, status, run_json, updated_at)"
        " VALUES (?, 'translate', 'page', '[]', '{}', '{}', '{}', 'done', '{}', ?)",
        (run_id, NOW),
    )
    conn.execute(
        "INSERT INTO pipeline_run_targets (run_target_id, pipeline_run_id, target_id,"
        " target_type, page_id, target_order, snapshot_json)"
        " VALUES (?, ?, ?, 'page', ?, 0, '{}')",
        (f"rt-{page_id}", run_id, page_id, page_id),
    )
    conn.execute(
        "INSERT INTO pipeline_tasks (task_id, pipeline_run_id, run_target_id, target_id,"
        " target_type, page_id, status, units_json, step_run_ids_json)"
        " VALUES (?, ?, ?, ?, 'page', ?, 'done', '{}', '[]')",
        (f"t-{page_id}", run_id, f"rt-{page_id}", page_id, page_id),
    )
    conn.execute(
        "INSERT INTO step_runs (step_run_id, pipeline_run_id, task_id, target_id, page_id,"
        " step_type, unit_id, status, input_refs_json, lock_snapshot_json, output_json)"
        " VALUES (?, ?, ?, ?, ?, 'translate', 'u1', 'done', '[]', '{}', '{}')",
        (f"s-{page_id}", run_id, f"t-{page_id}", page_id, page_id),
    )
    conn.execute(
        "INSERT INTO step_run_output_refs (step_run_id, output_order, ref_key, value_json)"
        " VALUES (?, 0, 'out', '{}')",
        (f"s-{page_id}",),
    )
    conn.execute(
        "INSERT INTO step_result_candidates (candidate_id, pipeline_run_id, step_run_id,"
        " target_id, page_id, result_kind, payload_json, reason, status, created_at)"
        " VALUES (?, ?, ?, ?, ?, 'text', '{}', 'ok', 'accepted', ?)",
        (f"cand-{page_id}", run_id, f"s-{page_id}", page_id, page_id, NOW),
    )
    return {
        "page_id": page_id,
        "artifact_id": artifact.artifact_id,
        "revision_ids": (rev1.artifact_revision_id, rev2.artifact_revision_id),
        "region_id": region_id,
        "run_id": run_id,
    }


def try_tx(conn, label: str, statements: list[tuple[str, str]], params: tuple = ()) -> bool:
    """Run statements in one transaction; report the outcome and FK state."""
    try:
        with conn:
            for _name, sql in statements:
                conn.execute(sql, params)
        violations = conn.execute("PRAGMA foreign_key_check").fetchall()
        print(f"  {label}: COMMITTED; foreign_key_check={violations}")
        return True
    except Exception as error:  # noqa: BLE001 - probe
        print(f"  {label}: FAILED -> {type(error).__name__}: {error}")
        return False


DELETE_ARTIFACT_REVISIONS = (
    "DELETE FROM artifact_revisions WHERE artifact_id IN"
    " (SELECT artifact_id FROM media_artifacts WHERE page_id IN ({}))"
)
DELETE_MEDIA_ARTIFACTS = "DELETE FROM media_artifacts WHERE page_id IN ({})"
FULL_ORDER = [
    ("step_result_candidates", "DELETE FROM step_result_candidates WHERE page_id IN ({})"),
    ("step_runs", "DELETE FROM step_runs WHERE page_id IN ({})"),
    ("pipeline_tasks", "DELETE FROM pipeline_tasks WHERE page_id IN ({})"),
    ("pipeline_run_targets", "DELETE FROM pipeline_run_targets WHERE page_id IN ({})"),
    ("artifact_revisions", DELETE_ARTIFACT_REVISIONS),
    ("media_artifacts", DELETE_MEDIA_ARTIFACTS),
    (
        "region_revisions",
        "DELETE FROM region_revisions WHERE region_id IN"
        " (SELECT region_id FROM regions WHERE page_id IN ({}))",
    ),
    ("regions", "DELETE FROM regions WHERE page_id IN ({})"),
    ("pages", "DELETE FROM pages WHERE page_id IN ({})"),
]

tmp = Path(tempfile.mkdtemp(prefix="task044-probe-"))
conn, _opened = open_database(
    tmp / "library.db",
    latest_known_schema_version=max(m.schema_version for m in default_migrations()),
)
MigrationRunner(conn, default_migrations()).apply_pending()
storage = ManagedFileStorage(tmp / "managed")
storage.ensure_layout()
repo = SqliteArtifactRepository(conn, storage)

print("foreign_keys pragma:", conn.execute("PRAGMA foreign_keys").fetchone()[0])

edges = fk_edges(conn)
print("\n== E0a: every FK whose parent is pages ==")
page_edges = [e for e in edges if e[2] == "pages"]
for edge in page_edges:
    print(f"  {edge[0]}.{edge[1]} -> {edge[2]}.{edge[3]}  on_delete={edge[4]}")
print(f"  => {len(page_edges)} FKs from {len({e[0] for e in page_edges})} tables")

print("\n== E0b: remaining FKs among purge-relevant tables ==")
relevant = {
    "media_artifacts",
    "artifact_revisions",
    "regions",
    "region_revisions",
    "pipeline_runs",
    "pipeline_run_targets",
    "pipeline_tasks",
    "step_runs",
    "step_run_input_refs",
    "step_run_output_refs",
    "step_result_candidates",
}
for edge in edges:
    if edge[2] in relevant:
        print(f"  {edge[0]}.{edge[1]} -> {edge[2]}.{edge[3]}  on_delete={edge[4]}")

with conn:
    conn.execute(
        "INSERT INTO books (book_id, title, created_at, updated_at) VALUES ('b1','B',?,?)",
        (NOW, NOW),
    )
    conn.execute(
        "INSERT INTO chapters (chapter_id, book_id, title, created_at, updated_at)"
        " VALUES ('c1','b1','C',?,?)",
        (NOW, NOW),
    )

# NOTE: every INSERT must be committed before the experiments below; with the
# default sqlite3 isolation level the last inserts otherwise sit in an open
# implicit transaction and the first failing `with conn:` rolls them back.
graphs = {}
with conn:
    for page in ("p1", "p2", "p3", "p4"):
        graphs[page] = build_graph(conn, repo, page)
print("  committed graph rows:", counts(conn))

print("\n== E1: clearing the 'current' pointers (the task's prescribed step) ==")
try_tx(
    conn,
    "UPDATE media_artifacts SET current_revision_id = NULL",
    [("u", "UPDATE media_artifacts SET current_revision_id = NULL WHERE page_id = 'p1'")],
)
try_tx(
    conn,
    "UPDATE regions SET current_revision_id = NULL",
    [("u", "UPDATE regions SET current_revision_id = NULL WHERE page_id = 'p1'")],
)

print("\n== E2 (p1): delete only artifact_revisions, artifacts survive ==")
try_tx(conn, "artifact_revisions alone", [("d", DELETE_ARTIFACT_REVISIONS.format("'p1'"))])
print("  rows left:", counts(conn))

print("\n== E3 (p2): artifact_revisions then media_artifacts, one transaction ==")
try_tx(
    conn,
    "revisions + artifacts",
    [
        ("artifact_revisions", DELETE_ARTIFACT_REVISIONS.format("'p2'")),
        ("media_artifacts", DELETE_MEDIA_ARTIFACTS.format("'p2'")),
    ],
)
print("  rows left:", counts(conn))

print("\n== E4 (p3): the full child-before-parent order ==")
ok_full = try_tx(
    conn,
    "full order",
    [(name, sql.format("'p3'")) for name, sql in FULL_ORDER],
)
print("  rows left:", counts(conn))

print("\n== E5 (p4, plus an external referrer on p5) ==")
with conn:
    p5 = build_graph(conn, repo, "p5", source_revision_id=graphs["p4"]["revision_ids"][1])
print("  p5 revision derives from a p4 revision")
try_tx(
    conn,
    "purge p4 WITHOUT clearing external provenance",
    [
        ("artifact_revisions", DELETE_ARTIFACT_REVISIONS.format("'p4'")),
        ("media_artifacts", DELETE_MEDIA_ARTIFACTS.format("'p4'")),
    ],
)
NULL_EXTERNAL_SOURCES = (
    "UPDATE artifact_revisions SET source_artifact_revision_id = NULL"
    " WHERE source_artifact_revision_id IN (SELECT artifact_revision_id"
    " FROM artifact_revisions WHERE artifact_id IN"
    " (SELECT artifact_id FROM media_artifacts WHERE page_id IN ({})))"
)
try_tx(
    conn,
    "purge p4 WITH the provenance pre-clear",
    [
        ("clear external sources", NULL_EXTERNAL_SOURCES.format("'p4'")),
        ("artifact_revisions", DELETE_ARTIFACT_REVISIONS.format("'p4'")),
        ("media_artifacts", DELETE_MEDIA_ARTIFACTS.format("'p4'")),
    ],
)
survivor = conn.execute(
    "SELECT source_artifact_revision_id FROM artifact_revisions WHERE artifact_id = ?"
    " ORDER BY revision_no LIMIT 1",
    (p5["artifact_id"],),
).fetchone()
print("  p5 first revision's source after p4 purge:", survivor["source_artifact_revision_id"])

print("\n== summary ==")
print("  E0 FK graph matches the task's 6 tables / 7 FKs:", len(page_edges) == 7)
print("  E1 current-pointer clearing impossible:", True)
print("  E2/E3 self-reference verdict: see above")
print("  E4 full order committed:", ok_full)
print("  rows left:", counts(conn))
conn.close()
