"""Decisive probe (DSH external review): purge a page that has an artifact row."""
import sys, tempfile, uuid
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(r"G:\CODEX\New Manga")
sys.path.insert(0, str(REPO / "src"))

from infrastructure.filesystem.managed_storage import ManagedFileStorage
from infrastructure.sqlite.connection import open_database
from infrastructure.sqlite.migrator import MigrationRunner
from infrastructure.sqlite.schema import default_migrations
from infrastructure.sqlite.library import SqliteLibraryRepository
from application.maintenance.trash import TrashService

now = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
tmp = Path(tempfile.mkdtemp(prefix="dsh-purge-probe-"))
root = tmp / "storage"
storage = ManagedFileStorage(root); storage.ensure_layout()
conn, _ = open_database(tmp / "app.db", latest_known_schema_version=default_migrations()[-1].schema_version)
MigrationRunner(conn, default_migrations()).apply_pending()
conn.row_factory = __import__("sqlite3").Row

rel = "pages/orig.png"
p = root / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(b"MANAGED ORIGINAL")

with conn:
    conn.execute("INSERT INTO books (book_id,title,created_at,updated_at) VALUES ('b1','B',?,?)", (now, now))
    conn.execute("INSERT INTO chapters (chapter_id,book_id,title,created_at,updated_at) VALUES ('c1','b1','C',?,?)", (now, now))
    conn.execute(
        "INSERT INTO pages (page_id,chapter_id,sort_order,created_at,updated_at,source_filename,source_order,"
        "source_hash,source_size_bytes,width,height,managed_original_ref) "
        "VALUES ('p1','c1',0,?,?, 'a.png',0,'deadbeef',16,10,10,?)", (now, now, rel))
    # the FK child that a real, pipeline-processed page always has:
    conn.execute(
        "INSERT INTO media_artifacts (artifact_id,book_id,chapter_id,page_id,artifact_type,current_revision_id,created_at,updated_at)"
        " VALUES ('a1','b1','c1','p1','original',NULL,?,?)", (now, now))

class Manifest:
    def __init__(self): self.b = []
    def read_manifest(self): return {"batches": list(self.b)}
    def write_manifest(self, m): self.b = m["batches"]

svc = TrashService(SqliteLibraryRepository(conn), storage, Manifest())
batch = svc.soft_delete_pages("c1", ("p1",))
print("batch page_ids     :", batch.page_ids)
print("managed file exists:", p.exists())
try:
    svc.purge_batch(batch.batch_id)
    print("purge_batch        : NO EXCEPTION")
except Exception as error:
    print("purge_batch        :", type(error).__name__, "-", str(error)[:90])
print("managed file after :", p.exists(), "   <-- file already gone?")
print("page row after     :", conn.execute("SELECT COUNT(*) FROM pages WHERE page_id='p1'").fetchone()[0])
print("deleted_at after   :", conn.execute("SELECT deleted_at FROM pages WHERE page_id='p1'").fetchone()[0])
print("batches in ledger  :", len(svc.list_batches()))
try:
    restored = svc.restore_batch(batch.batch_id)
    print("restore_batch      :", restored, "-> live page points at missing file:", not p.exists() and conn.execute("SELECT deleted_at FROM pages WHERE page_id='p1'").fetchone()[0] is None)
except Exception as error:
    print("restore_batch      :", type(error).__name__, "-", str(error)[:90])
