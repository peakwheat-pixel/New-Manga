"""TASK-053 AC 1 pre-fix evidence probe: reproduces both TASK-044 leftover
states on the PRE-FIX tree (git archive export, never the working tree).

- R-03: after purge_pages, the run row survives with zero target rows and
  (pre-fix) there is no maintenance entry point to reclaim it;
- R-04: a file-removal failure after the rows are gone leaves the batch
  removed from the ledger with NO persisted file list, so the orphan can
  never be rediscovered (retry impossible).

Run:  python verification/TASK-053/r03_r04_probe.py <exported-tree-root>
Exit: 0 when both pre-fix states are observed (evidence), 1 otherwise.
"""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path

TREE = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(TREE / "src"))

from application.maintenance import TrashService  # noqa: E402
from application.maintenance.trash import _JsonTrashManifest  # noqa: E402
from domain.pages.entities import Page  # noqa: E402
from infrastructure.filesystem.managed_storage import ManagedFileStorage  # noqa: E402
from infrastructure.sqlite.connection import open_database  # noqa: E402
from infrastructure.sqlite.library import SqliteLibraryRepository  # noqa: E402
from infrastructure.sqlite.migrator import MigrationRunner  # noqa: E402
from infrastructure.sqlite.schema import default_migrations  # noqa: E402

NOW = "2026-09-19T02:00:00+00:00"


class FailingRemover:
    """Simulates the transient storage fault of R-04 on the first file."""

    def __init__(self, inner: ManagedFileStorage) -> None:
        self._inner = inner
        self.failed_on: list[str] = []

    def remove_managed(self, relative_path: str) -> None:
        self.failed_on.append(relative_path)
        raise OSError(f"transient storage fault on {relative_path}")


def build(tmp: Path):
    conn, _ = open_database(tmp / "library.db", latest_known_schema_version=3)
    MigrationRunner(conn, default_migrations()).apply_pending()
    storage = ManagedFileStorage(tmp / "managed")
    storage.ensure_layout()
    repository = SqliteLibraryRepository(conn)
    with conn:
        conn.execute(
            "INSERT INTO books (book_id, title, created_at, updated_at)"
            " VALUES ('book-1','B',?,?)", (NOW, NOW))
        conn.execute(
            "INSERT INTO chapters (chapter_id, book_id, title, created_at, updated_at)"
            " VALUES ('chapter-1','book-1','C',?,?)", (NOW, NOW))
    for page_id in ("p1", "p2"):
        relative = f"books/book-1/chapters/chapter-1/original/{page_id}.png"
        f = tmp / "managed" / Path(relative)
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(page_id.encode())
        repository.add_page(Page(
            page_id=page_id, chapter_id="chapter-1", source_filename=f"{page_id}.png",
            source_order=int(page_id[-1]), sort_order=int(page_id[-1]),
            source_hash=hashlib.sha256(page_id.encode()).hexdigest(),
            source_size_bytes=len(page_id), width=4, height=3,
            managed_original_ref=relative))
    return conn, storage, repository


def triggers(conn) -> list[str]:
    return [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='trigger' ORDER BY name")]


def main() -> int:
    ok = True
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as raw:
        tmp = Path(raw)
        conn, storage, repository = build(tmp)
        print("AC 4 trigger enumeration (pre-fix tree):")
        print(" ", json.dumps(triggers(conn)))

        # -- R-04: purge with a failing remover -------------------------
        service = TrashService(repository, storage, _JsonTrashManifest(tmp / "managed" / "trash-manifest.json"))
        batch = service.soft_delete_pages("chapter-1", ("p1",))
        failing = FailingRemover(storage)
        try:
            failing_service = TrashService(repository, failing, _JsonTrashManifest(tmp / "managed" / "trash-manifest.json"))
            failing_service.purge_batch(batch.batch_id)
            print("R-04 probe: purge unexpectedly succeeded - NOT the pre-fix state")
            ok = False
        except OSError as error:
            manifest = json.loads((tmp / "managed" / "trash-manifest.json").read_text(encoding="utf-8"))
            orphan = tmp / "managed" / "books/book-1/chapters/chapter-1/original/p1.png"
            print("R-04 probe: purge failed as designed:", error)
            print("R-04 probe: manifest keys after failure:", sorted(manifest.keys()))
            print("R-04 probe: pending_purges present:", "pending_purges" in manifest)
            print("R-04 probe: orphan file still on disk:", orphan.is_file())
            discoverable = "pending_purges" in manifest
            print("R-04 probe: orphan discoverable via ledger/manifest:", discoverable)
            if "pending_purges" in manifest or not orphan.is_file():
                ok = False

        # -- R-03: a purged page leaves a target-less run row -----------
        conn.execute(
            "INSERT INTO pipeline_runs (run_id, command_type, scope_type,"
            " requested_targets_json, settings_snapshot_json,"
            " provider_binding_snapshot_json, context_policy_json, status,"
            " run_json, updated_at)"
            " VALUES ('run-1','translate','chapter','[]','{}','{}','{}','failed','{}',?)",
            (NOW,))
        conn.execute(
            "INSERT INTO pipeline_run_targets (run_target_id, pipeline_run_id,"
            " target_id, target_type, page_id, target_order, snapshot_json)"
            " VALUES ('run-1-t0','run-1','p2','page','p2',0,'{}')")
        conn.commit()
        service2 = TrashService(repository, storage, _JsonTrashManifest(tmp / "managed" / "trash-manifest.json"))
        batch2 = service2.soft_delete_pages("chapter-1", ("p2",))
        service2.purge_batch(batch2.batch_id)
        targets_left = conn.execute(
            "SELECT COUNT(*) FROM pipeline_run_targets WHERE pipeline_run_id='run-1'"
        ).fetchone()[0]
        run_left = conn.execute(
            "SELECT COUNT(*) FROM pipeline_runs WHERE run_id='run-1'").fetchone()[0]
        has_maintenance = hasattr(sys.modules.get("application.maintenance.ports", object()),
                                  "RunLedgerMaintenance")
        print("R-03 probe: after page purge -> run row remains:", bool(run_left),
              "| its target rows:", targets_left)
        print("R-03 probe: maintenance entry point exists pre-fix:", has_maintenance)
        if not (run_left and targets_left == 0) or has_maintenance:
            ok = False

        conn.close()
    print("PRE-FIX EVIDENCE:", "REPRODUCED" if ok else "NOT REPRODUCED")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
