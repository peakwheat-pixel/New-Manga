"""FEA-15-A4-1: isolated dual-root upgrade + backup + restore + pre_restore rollback drill.

Runs entirely inside G:\\CODEX\\New Manga.workspace\\FEA-15-A4-1\\root:
  * synthesise a legacy v8 library with the project's own migration definitions
    (reusing tests/storage/test_upgrade_schema_data.py helpers),
  * migrate to the current schema and prove the row counts are conserved,
  * create a manual backup, mutate the library, restore the backup (which must
    first write a pre_restore package), then restore the pre_restore package,
  * fingerprint the real %APPDATA% roots before/after (read-only).

No product code is modified; the real user data roots are never written.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sqlite3
import sys

REPO = Path(r"G:\CODEX\New Manga")
WORKSPACE = Path(r"G:\CODEX\New Manga.workspace\FEA-15-A4-1")
ROOT = WORKSPACE / "root"
DATA = ROOT / "data"
THEME = ROOT / "theme"
OUT = WORKSPACE / "a4-result.json"

sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "tests"))

from infrastructure.sqlite.migrator import MigrationRunner, read_schema_version  # noqa: E402
from infrastructure.sqlite.schema import default_migrations  # noqa: E402
from infrastructure.sqlite.nmbak import NmbakBackupService  # noqa: E402
from infrastructure.sqlite.connection import ThreadRoutedConnection  # noqa: E402


def load_upgrade_helpers():
    spec = importlib.util.spec_from_file_location(
        "a4_upgrade_helpers", REPO / "tests/storage/test_upgrade_schema_data.py",
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def fingerprint(directory: Path) -> dict:
    if not directory.exists():
        return {"exists": False, "files": 0, "bytes": 0, "digest": "<absent>"}
    rows = []
    for path in sorted(directory.rglob("*")):
        if path.is_file():
            rows.append(f"{path}|{path.stat().st_size}|{path.stat().st_mtime_ns}")
    sha = hashlib.sha256("\n".join(rows).encode()).hexdigest()
    return {
        "exists": True,
        "files": len(rows),
        "bytes": sum(path.stat().st_size for path in directory.rglob("*") if path.is_file()),
        "digest": sha,
    }



def ensure_managed_files(conn, managed_root: Path) -> int:
    """Create deterministic managed-fixture bytes for every referenced managed path."""
    refs = set()
    for query in (
        "select managed_original_ref from pages where managed_original_ref is not null and managed_original_ref != ''",
        "select managed_path from artifact_revisions where managed_path is not null and managed_path != ''",
    ):
        try:
            for row in conn.execute(query):
                refs.add(str(row[0]))
        except sqlite3.OperationalError:
            continue
    created = 0
    for ref in refs:
        relative = Path(ref)
        if relative.is_absolute() or any(part == ".." for part in relative.parts):
            continue
        target = managed_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            target.write_bytes(b"A4-managed-fixture:" + ref.encode())
            created += 1
    return created
def table_counts(conn: sqlite3.Connection) -> dict:
    names = [
        row[0]
        for row in conn.execute(
            "select name from sqlite_master where type='table' and name not like 'sqlite_%' and name != 'schema_migrations'"
        )
    ]
    counts = {}
    for name in names:
        try:
            counts[name] = int(conn.execute(f'select count(*) from "{name}"').fetchone()[0])
        except sqlite3.Error:
            counts[name] = -1
    return counts


def main() -> int:
    for directory in (ROOT, DATA, THEME):
        directory.mkdir(parents=True, exist_ok=True)
    db_path = DATA / "library.db"
    if db_path.exists():
        db_path.unlink()

    real_data = Path(os.environ["APPDATA"]) / "com.newmanga.desktop"
    real_theme = Path(os.environ["APPDATA"]) / "NewManga"
    before = {"data_root": fingerprint(real_data), "theme_root": fingerprint(real_theme)}

    helpers = load_upgrade_helpers()
    migrations = default_migrations()
    latest = migrations[-1].schema_version
    legacy_version = latest - 1

    conn = helpers._build_legacy_database(db_path, legacy_version)
    legacy_schema = read_schema_version(conn)
    legacy_counts = table_counts(conn)

    applied = MigrationRunner(conn, migrations[legacy_version:]).apply_pending()
    migrated_schema = read_schema_version(conn)
    migrated_counts = table_counts(conn)
    conn.commit()
    conn.close()

    def _open_plain() -> sqlite3.Connection:
        opened = sqlite3.connect(db_path)
        opened.row_factory = sqlite3.Row
        return opened

    routed = ThreadRoutedConnection(_open_plain)
    conn = routed
    managed_created = ensure_managed_files(conn, DATA / "managed")
    backup_service = NmbakBackupService(
        conn,
        backup_root=DATA / "backups",
        managed_root=DATA / "managed",
        app_version="0.1.1-a4",
        data_root=DATA,
    )
    manual = backup_service.create("manual", "FEA-15-A4-1 drill before mutation")

    # Mutate a real business row so restore/rollback have something to undo.
    book_row = conn.execute("select book_id from books limit 1").fetchone()
    mutated = False
    if book_row is not None:
        conn.execute("update books set title = title || ' [a4-mutated]' where book_id = ?", (book_row[0],))
        conn.commit()
        mutated = True
    mutated_counts = table_counts(conn)

    restored = backup_service.restore(manual["backup_id"], confirm_restore=True)
    pre_restore_id = restored.get("pre_restore_backup_id")
    restored_counts = table_counts(conn)
    backups_after_restore = backup_service.list_backups()

    rollback = backup_service.restore(pre_restore_id, confirm_restore=True)
    rollback_counts = table_counts(conn)
    backups_after_rollback = backup_service.list_backups()
    after = {"data_root": fingerprint(real_data), "theme_root": fingerprint(real_theme)}

    result = {
        "ac": "A4-AC1..AC4",
        "data_root": str(DATA),
        "theme_root": str(THEME),
        "legacy_schema": legacy_schema,
        "migrated_schema": migrated_schema,
        "applied_migrations": [record.schema_version for record in applied],
        "legacy_counts": legacy_counts,
        "migrated_counts": migrated_counts,
        "row_counts_conserved": legacy_counts == migrated_counts,
        "manual_backup": manual,
        "manual_backup_listing": [entry for entry in backups_after_restore if entry["backup_id"] == manual["backup_id"]],
        "mutated": mutated,
        "mutated_counts": mutated_counts,
        "restore_result": {
            "status": restored.get("status"),
            "pre_restore_backup_id": pre_restore_id,
            "pre_restore_listed": any(entry["backup_id"] == pre_restore_id for entry in backups_after_restore),
        },
        "restored_counts": restored_counts,
        "rollback_result": {
            "status": rollback.get("status"),
            "restored_backup_id": rollback.get("restored_backup_id") or rollback.get("backup_id"),
            "pre_restore_backup_id": rollback.get("pre_restore_backup_id"),
        },
        "rollback_counts": rollback_counts,
        "rollback_restored_mutated_state": rollback_counts == mutated_counts,
        "real_appdata": {
            "before": before,
            "after": after,
            "unchanged": before == after,
        },
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "migrated_schema": migrated_schema,
        "row_counts_conserved": result["row_counts_conserved"],
        "pre_restore_listed": result["restore_result"]["pre_restore_listed"],
        "rollback_restored_mutated_state": result["rollback_restored_mutated_state"],
        "real_appdata_unchanged": result["real_appdata"]["unchanged"],
    }, ensure_ascii=False))
    ok = (
        migrated_schema == latest
        and result["row_counts_conserved"]
        and result["restore_result"]["pre_restore_listed"]
        and result["rollback_restored_mutated_state"]
        and result["real_appdata"]["unchanged"]
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
