"""Reviewer Round 4 adversarial probe for T1.3.1 / TASK-057 R-011.

Usage: python t057_r011_acl_probe.py <tree-root>

Scenario A (R-011 trigger with a REAL OS failure, not a Mock):
the backup file is readable while ``verify_backup_file`` runs, then a
Windows ACL read-deny is applied before ``sha256_file`` reads it. A fixed
tree must surface a typed ``BACKUP_FILE_UNREADABLE``; a pre-fix tree leaks
the bare ``PermissionError`` (``code=None``). Live revisions, the backup
ledger and the backup root must be untouched either way.

Scenario B (same-stage ``sqlite3.Error`` reachability):
the live database is put in a state where the prevalidation ledger read
itself fails (``backup_records`` dropped, i.e. an un-migrated v0-shaped
live DB). Reports what escapes so the reviewer can judge whether the
R-011 recommendation's parenthetical is a reachable product path.

The probe only ever touches its own system temp directory.
"""

from __future__ import annotations

import getpass
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TREE = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
SRC = TREE / "src"
if not SRC.is_dir():
    print(f"FATAL: no src/ under {TREE}")
    raise SystemExit(2)
sys.path.insert(0, str(SRC))

import infrastructure.sqlite.backup as backup_module  # noqa: E402
from infrastructure.sqlite.backup import (  # noqa: E402
    BackupVerificationError,
    SqliteBackupService,
)
from infrastructure.sqlite.connection import open_database  # noqa: E402
from infrastructure.sqlite.migrator import MigrationRunner  # noqa: E402
from infrastructure.sqlite.schema import default_migrations  # noqa: E402

USER = getpass.getuser()
FAILURES: list[str] = []


def check(label: str, condition: bool, detail: str = "") -> None:
    print(f"   [{'PASS' if condition else 'FAIL'}] {label}{(' — ' + detail) if detail else ''}")
    if not condition:
        FAILURES.append(label)


def icacls(path: Path, *args: str) -> None:
    result = subprocess.run(
        ["icacls", str(path), *args], capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"icacls {args} failed: {result.stdout}{result.stderr}")


def build_workspace(root: Path) -> dict:
    managed_root = root / "managed"
    managed_root.mkdir(parents=True, exist_ok=True)
    conn, _opened = open_database(
        root / "library.db",
        latest_known_schema_version=max(
            m.schema_version for m in default_migrations()
        ),
    )
    MigrationRunner(conn, default_migrations()).apply_pending()
    relative = "books/b/chapters/c/original/p1.png"
    managed_file = managed_root / Path(relative)
    managed_file.parent.mkdir(parents=True, exist_ok=True)
    managed_file.write_bytes(b"p1")
    now = "2026-09-21T00:00:00+00:00"
    with conn:
        conn.execute(
            "INSERT INTO books (book_id, title, created_at, updated_at)"
            " VALUES ('book-1','B',?,?)", (now, now))
        conn.execute(
            "INSERT INTO chapters (chapter_id, book_id, title, created_at, updated_at)"
            " VALUES ('chapter-1','book-1','C',?,?)", (now, now))
        conn.execute(
            "INSERT INTO pages (page_id, chapter_id, sort_order, created_at, updated_at)"
            " VALUES ('p1','chapter-1',1,?,?)", (now, now))
        conn.execute(
            "INSERT INTO media_artifacts (artifact_id, book_id, chapter_id, page_id,"
            " artifact_type, created_at, updated_at) VALUES ('art-p1','book-1',"
            "'chapter-1','p1','original',?,?)", (now, now))
        conn.execute(
            "INSERT INTO artifact_revisions (artifact_revision_id, artifact_id,"
            " revision_no, managed_path, file_hash, mime_type, size_bytes,"
            " is_pinned, created_at) VALUES ('rev-p1','art-p1',1,?,"
            "'0000','image/png',2,1,?)", (relative, now))
    service = SqliteBackupService(
        conn, managed_root / "backups", managed_root=managed_root
    )
    return {
        "conn": conn,
        "service": service,
        "backup_root": managed_root / "backups",
    }


def scenario_a(root: Path) -> None:
    print("== Scenario A: real Windows ACL read-deny between verify and hash ==")
    workspace = build_workspace(root)
    conn, service = workspace["conn"], workspace["service"]
    backup_root = workspace["backup_root"]
    backup_id = service.create_backup("manual", "reviewer-r4-acl")
    target = backup_root / f"{backup_id}.db"
    records_before = conn.execute(
        "SELECT COUNT(*) FROM backup_records").fetchone()[0]
    names_before = sorted(p.name for p in backup_root.iterdir())

    real_verify = backup_module.verify_backup_file
    denied: list[Path] = []
    genuine_os_error = {"seen": None}

    def verify_then_deny(path: Path) -> int:
        version = real_verify(path)
        if Path(path).name == target.name:
            icacls(Path(path), "/deny", f"{USER}:(R)")
            denied.append(Path(path))
            try:
                Path(path).open("rb").read(1)
            except OSError as error:
                genuine_os_error["seen"] = (
                    type(error).__name__, error.errno)
        return version

    backup_module.verify_backup_file = verify_then_deny
    try:
        try:
            service.restore_backup(backup_id)
            print("   restore_backup returned normally (UNEXPECTED)")
            raised = None
        except BaseException as error:  # noqa: BLE001 - probe reports anything
            raised = error
        print(f"   PREVALIDATION_TYPE={type(raised).__name__ if raised else None} "
              f"CODE={getattr(raised, 'code', None)}")
        print(f"   GENUINE_OS_ERROR={genuine_os_error['seen']}")
    finally:
        backup_module.verify_backup_file = real_verify
        for path in denied:
            icacls(path, "/remove:d", USER)

    check("ACL deny produced a genuine OS read failure",
          genuine_os_error["seen"] is not None,
          str(genuine_os_error["seen"]))
    check("failure is typed BackupVerificationError",
          isinstance(raised, BackupVerificationError),
          f"actual={type(raised).__name__}")
    check("typed code is BACKUP_FILE_UNREADABLE",
          getattr(raised, "code", None) == "BACKUP_FILE_UNREADABLE",
          f"actual={getattr(raised, 'code', None)}")
    check("file readable again after ACL reset",
          target.open("rb").read(1) == target.read_bytes()[:1])
    check("live artifact_revisions untouched",
          conn.execute("SELECT COUNT(*) FROM artifact_revisions").fetchone()[0] == 1)
    check("backup ledger row count unchanged",
          conn.execute("SELECT COUNT(*) FROM backup_records").fetchone()[0]
          == records_before,
          f"before={records_before}")
    check("no pre_restore/tmp half-artifact in backup root",
          sorted(p.name for p in backup_root.iterdir()) == names_before,
          f"before={names_before} after={sorted(p.name for p in backup_root.iterdir())}")
    conn.close()


def scenario_b(root: Path) -> None:
    print("== Scenario B: same-stage sqlite3.Error reachability (v0-shaped live DB) ==")
    workspace = build_workspace(root)
    conn, service = workspace["conn"], workspace["service"]
    backup_id = service.create_backup("manual", "reviewer-r4-ledgerless")
    with conn:
        conn.execute("DROP TABLE backup_records")
    try:
        service.restore_backup(backup_id)
        print("   restore_backup returned normally")
        raised = None
    except BaseException as error:  # noqa: BLE001 - probe reports anything
        raised = error
    print(f"   LEDGER_READ_TYPE={type(raised).__name__ if raised else None} "
          f"CODE={getattr(raised, 'code', None)}")
    check("ledger-read failure leaves the live DB unwritten",
          conn.execute("SELECT COUNT(*) FROM artifact_revisions").fetchone()[0] == 1)
    conn.close()


def main() -> int:
    print(f"TREE={TREE}")
    print(f"HEAD_SRC_HAS_TYPED_MAPPING="
          f"{'BACKUP_FILE_UNREADABLE' in (SRC / 'infrastructure' / 'sqlite' / 'backup.py').read_text(encoding='utf-8')}")
    root = Path(tempfile.mkdtemp(prefix="t057-r4-probe-"))
    a_root = root / "a"
    b_root = root / "b"
    a_root.mkdir(parents=True)
    b_root.mkdir(parents=True)
    try:
        scenario_a(a_root)
        scenario_b(b_root)
    finally:
        shutil.rmtree(root, ignore_errors=True)
    print(f"== done: failures={len(FAILURES)} {FAILURES}")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    raise SystemExit(main())
