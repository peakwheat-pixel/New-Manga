"""AC4 retry path: cleanup must reclaim previews from the manifest alone.

Finding 1 (Codex R1) described this sequence: a cleanup is refused, so its catalog row
survives and the delete reports pending; the manifest is what carries the work forward to
the retry. But the preview keys are random (preview-<uuid4>) and media_artifacts is already
gone by then, so before the fix the retry snapshotted an empty list, the rows and files
survived, and the next successful pass deleted the manifest - losing the only record.

The ac4-leak-assert-probe covers the first delete. This covers the retry, by calling
cleanup_book_files with preview_resource_ids omitted exactly as the retry would, after
writing the manifest the way execute_permanent_delete_db does.

Expected: PASS on fixed code. On the pre-fix code the manifest has no
preview_resource_ids field, the fallback returns nothing, and this reports the leak.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

REPO = Path(r"G:\CODEX\New Manga")
sys.path.insert(0, str(REPO / "src"))

from bootstrap.core_service import CoreServiceServer, assemble_production_core  # noqa: E402
from infrastructure.resource_channel.catalog_store import (  # noqa: E402
    ResourceCatalogStore,
    initialize_namespace,
)
from infrastructure.resource_channel.render_preview import RenderPreviewPublisher  # noqa: E402

WS = Path(r"G:\CODEX\New Manga.workspace\agent-output\coordinator\ac4-retry")
if WS.exists():
    shutil.rmtree(WS, ignore_errors=True)
WS.mkdir(parents=True)

ORIG = b"original bytes"
TRANS = b"translated bytes"
READS = 2

core = assemble_production_core(WS / "data")
derived_root = WS / "derived"
derived_root.mkdir(parents=True, exist_ok=True)
catalog_db = WS / "catalog" / "catalog.sqlite"
catalog_db.parent.mkdir(parents=True, exist_ok=True)
initialize_namespace(catalog_db, derived_root)
catalog = ResourceCatalogStore(catalog_db)
previews = RenderPreviewPublisher(derived_root, catalog)

# --- fixture: one book/chapter/page with an original and a translated revision ---
t = core.storage.write_temp(ORIG)
rel_o = core.storage.new_revision_relative_path("b1", "c1", "original", "p1", ".png")
core.storage.publish(t, rel_o)
t = core.storage.write_temp(TRANS)
rel_t = core.storage.new_revision_relative_path("b1", "c1", "translated", "p1", ".png")
core.storage.publish(t, rel_t)
with core.conn:
    core.conn.execute("INSERT INTO books (book_id,title,created_at,updated_at) VALUES ('b1','B','now','now')")
    core.conn.execute("INSERT INTO chapters (chapter_id,book_id,title,created_at,updated_at) VALUES ('c1','b1','C','now','now')")
    core.conn.execute(
        "INSERT INTO pages (page_id,chapter_id,managed_original_ref,source_filename,"
        "source_hash,source_size_bytes,width,height,created_at,updated_at)"
        " VALUES ('p1','c1',?, 'p1.png', ?, ?, 10, 10, 'now', 'now')",
        (rel_o, hashlib.sha256(ORIG).hexdigest(), len(ORIG)),
    )
    core.conn.execute(
        "INSERT INTO media_artifacts (artifact_id,book_id,chapter_id,page_id,artifact_type,"
        "current_revision_id,created_at,updated_at)"
        " VALUES ('a1','b1','c1','p1','translated','ar1','now','now')"
    )
    core.conn.execute(
        "INSERT INTO artifact_revisions (artifact_revision_id,artifact_id,revision_no,"
        "managed_path,file_hash,mime_type,size_bytes,integrity_status,created_at)"
        " VALUES ('ar1','a1',1,?,?,'image/png',?,'valid','now')",
        (rel_t, hashlib.sha256(TRANS).hexdigest(), len(TRANS)),
    )

# --- produce the previews the way production does: through the reader projection.
#     publish() takes (managed_png, revision, origin); rather than hand-build an origin,
#     drive the real path - it mints the preview-<uuid4> keys this defect is about.
server = CoreServiceServer(core, render_previews=previews, producer_root=core.storage.root)
for _ in range(READS):
    resp, _err = server.dispatch_request(json.dumps({
        "protocol": "new-manga.core",
        "version": {"major": 2, "minor": 11},
        "request_id": "ac4-retry",
        "command": "GetReaderProjection",
        "payload": {"chapter_id": "c1", "mode": "translated", "start_position": "beginning"},
    }))
    assert resp["error"] is None, resp["error"]
rows = [e for e in catalog.entries() if e.resource_id.startswith("preview-")]
files = [p for p in derived_root.rglob("*") if p.is_file()]
print("published %d previews -> %d catalog rows, %d files" % (READS, len(rows), len(files)))
assert len(rows) >= 1, "no publish rows were created, nothing to test"

# --- simulate the state a refused cleanup leaves behind: the delete has already run,
#     the manifest survives and carries the preview ids ---
targets = core.repository.list_book_cleanup_targets("b1")
page_ids = core.repository.list_book_page_ids("b1")
snapshot_ids = [e.resource_id for e in rows]

# media_artifacts is gone (the delete ran); that is exactly why the ids had to be persisted
with core.conn:
    core.conn.execute("DELETE FROM artifact_revisions")
    core.conn.execute("DELETE FROM media_artifacts")
    core.conn.execute(
        "INSERT OR REPLACE INTO book_cleanup_manifests (book_id, targets_json, created_at)"
        " VALUES ('b1', ?, 'now')",
        (json.dumps({
            "managed_targets": list(targets),
            "page_ids": list(page_ids),
            "preview_resource_ids": snapshot_ids,
        }, ensure_ascii=False),),
    )
post_snapshot = core.repository.list_page_artifact_ids(page_ids)
print("artifact ids rebuildable after the delete = %d (expected 0)" % len(post_snapshot))
assert post_snapshot == [], "fixture invalid: the mapping still exists, the retry would not be tested"

# --- the retry: cleanup is called WITHOUT preview_resource_ids, as the retry path does ---
ok = core.repository.cleanup_book_files(
    "b1", targets, core.storage,
    render_previews=previews,
    page_ids=page_ids,
    # preview_resource_ids deliberately omitted - this is the retry
)
remaining_rows = [e for e in catalog.entries() if e.resource_id.startswith("preview-")]
remaining_files = [p for p in derived_root.rglob("*") if p.is_file()]
print("cleanup returned %s" % ok)
print("after retry: %d publish rows, %d files" % (len(remaining_rows), len(remaining_files)))
if remaining_rows:
    print("  surviving rows:", [e.resource_id[:24] + "..." for e in remaining_rows[:4]])

leaked_rows = len(remaining_rows)
leaked_files = max(0, len(remaining_files) - 1)   # keep the lifecycle lock file out of it
print()
print("LEAK: %d row(s), %d file(s)" % (leaked_rows, leaked_files))

catalog.close()
core.conn.close()

if leaked_rows == 0 and leaked_files == 0:
    print("RESULT = PASS (retry reclaimed from the manifest alone)")
    sys.exit(0)
print("RESULT = FAIL (retry lost the preview ids)")
sys.exit(1)
