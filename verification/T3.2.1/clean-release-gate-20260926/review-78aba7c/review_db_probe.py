"""Reviewer read-only inspection of the frozen host-simulation DB. Not product or evidence code."""
from __future__ import annotations

import hashlib
import sqlite3
from pathlib import Path

ROOT = Path("G:/CODEX/New Manga.artifacts/T3.2.1-clean-release-gate-20260926")
DB = ROOT / "host-simulation-20260926-rerun1/用户配置隔离/AppData/Local/New Manga/library.db"

print("db_path", DB)
print("db_sha256", hashlib.sha256(DB.read_bytes()).hexdigest())
print("sidecars", [p.name for p in DB.parent.iterdir() if p.name.startswith("library.db")])

conn = sqlite3.connect("file:" + DB.as_posix() + "?mode=ro", uri=True)
print("schema_version", conn.execute(
    "select metadata_key, value_json from application_metadata where metadata_key='schema_version'"
).fetchall())
print("migrations", conn.execute(
    "select schema_version, migration_name from schema_migrations order by schema_version").fetchall())
print("books/chapters/pages", conn.execute(
    "select (select count(*) from books),(select count(*) from chapters),(select count(*) from pages)"
).fetchone())
print("page_row", conn.execute(
    "select page_id, page_locked, review_state, overall_status, source_hash from pages").fetchall())
print("export_history", conn.execute(
    "select export_id, quote(book_id), quote(chapter_id), status, file_hash "
    "from export_history").fetchall())
# Non-invasive only: the reviewer never opens the frozen evidence DB read-write.
# A 0-byte -wal means no pending transactions; the sidecar pair is re-created by
# any read-only WAL open, so its presence here is not app-shutdown evidence.
print("wal_sidecar_present", (DB.parent / "library.db-wal").exists())
print("wal_size", (DB.parent / "library.db-wal").stat().st_size if (DB.parent / "library.db-wal").exists() else None)
print("shm_sidecar_present", (DB.parent / "library.db-shm").exists())
