"""AC2: the behaviour of a still-referenced preview, asserted rather than assumed.

Task L48 forbids adopting "delete everything and accept stale references" BY DEFAULT -
it says the question needs a product ruling. The user ruled C1: a preview may fail to load
after a permanent delete. Task L53 then requires that, for the chosen direction, the
behaviour of a preview that is still referenced has an explicit assertion. This is it.

The strongest form of "still referenced" available to the Core is a preview read moments
before the delete: the reader asked for it, the view may still be holding it, and the
delete follows immediately. If the ruling were "referenced previews must survive", this
probe would have to assert the opposite and the implementation would have to keep them.

So the assertion is: a preview that was requested immediately before the delete is
reclaimed anyway, and the reclaim is reported, not silent. On the pre-fix code these rows
survived, which is what made it a leak rather than a policy.
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

WS = Path(r"G:\CODEX\New Manga.workspace\agent-output\coordinator\ac2-referenced")
if WS.exists():
    shutil.rmtree(WS, ignore_errors=True)
WS.mkdir(parents=True)

ORIG = b"original bytes"
TRANS = b"translated bytes"

core = assemble_production_core(WS / "data")
derived_root = WS / "derived"
derived_root.mkdir(parents=True, exist_ok=True)
catalog_db = WS / "catalog" / "catalog.sqlite"
catalog_db.parent.mkdir(parents=True, exist_ok=True)
initialize_namespace(catalog_db, derived_root)
catalog = ResourceCatalogStore(catalog_db)
previews = RenderPreviewPublisher(derived_root, catalog)
server = CoreServiceServer(core, render_previews=previews, producer_root=core.storage.root)

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

# --- the reference: a reader request immediately before the delete ---
resp, _err = server.dispatch_request(json.dumps({
    "protocol": "new-manga.core",
    "version": {"major": 2, "minor": 11},
    "request_id": "ac2-referenced",
    "command": "GetReaderProjection",
    "payload": {"chapter_id": "c1", "mode": "translated", "start_position": "beginning"},
}))
assert resp["error"] is None, resp["error"]

referenced = [e for e in catalog.entries() if e.resource_id.startswith("preview-")]
files_before = [p for p in derived_root.rglob("*") if p.is_file()]
print("referenced previews: %s" % [e.resource_id[:24] + "..." for e in referenced])
print("files before delete: %d" % len(files_before))
assert referenced, "INCONCLUSIVE: the reader produced no preview, nothing is referenced"

# --- delete immediately: no delay, the reference is as fresh as it can be ---
result, error = server.handle_permanently_delete_book(
    {"book_id": "b1", "confirm_permanent_delete": True})
print("delete ->", "ok" if error is None else error)
assert error is None, error
print("delete reported success =", result == {"book_id": "b1", "deleted": True})

remaining_rows = [e for e in catalog.entries() if e.resource_id.startswith("preview-")]
remaining_files = [p for p in derived_root.rglob("*") if p.is_file()]
print("after delete: %d rows, %d files" % (len(remaining_rows), len(remaining_files)))

catalog.close()
core.conn.close()

problems = []
if remaining_rows:
    problems.append("a preview that was referenced immediately before the delete survived: %s"
                    % [e.resource_id[:24] + "..." for e in remaining_rows])
if len(remaining_files) > 1:   # only the namespace lock should remain
    problems.append("files survived: %s" % [p.name for p in remaining_files])

print()
if problems:
    for p in problems:
        print("  -", p)
    print("RESULT = FAIL (C1 says referenced previews are reclaimed; they were not)")
    sys.exit(1)

print("AC2: a still-referenced preview is reclaimed, per the C1 ruling - asserted, not assumed")
print("RESULT = PASS")
sys.exit(0)
