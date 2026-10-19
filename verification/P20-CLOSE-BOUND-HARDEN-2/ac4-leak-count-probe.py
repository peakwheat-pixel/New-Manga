"""Measure AC4's leak size instead of describing it.

The assessment said each translated read leaks one artifact, but nobody counted. The
number decides how serious this is, and counting needs no permission.

Method: drive the real reader projection repeatedly through the Core server, then
count (a) catalog rows whose resource_id starts with the publish-style prefix and
(b) files left on disk under the derived root. Anything that stays after a permanent
delete is the leak.

Setup mirrors tests/core/test_p09_ac4_translated_preview.py, which already builds the
minimum state for GetReaderProjection. Fixtures are under the workspace.
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

WS = Path(r"G:\CODEX\New Manga.workspace\agent-output\coordinator\ac4-count")
if WS.exists():
    shutil.rmtree(WS, ignore_errors=True)
WS.mkdir(parents=True)

ORIG = b"original bytes"
TRANS = b"translated bytes"
READS = 5

data_root = WS / "data"
core = assemble_production_core(data_root)
derived_root = WS / "derived"
derived_root.mkdir(parents=True, exist_ok=True)
catalog_db = WS / "catalog" / "catalog.sqlite"
catalog_db.parent.mkdir(parents=True, exist_ok=True)
initialize_namespace(catalog_db, derived_root)
catalog = ResourceCatalogStore(catalog_db)


def rpc(server, command, payload):
    response, _ = server.dispatch_request(json.dumps({
        "protocol": "new-manga.core",
        "version": {"major": 2, "minor": 10},
        "request_id": "ac4-count",
        "command": command,
        "payload": payload,
    }))
    return response


previews = RenderPreviewPublisher(derived_root, catalog)
server = CoreServiceServer(core, render_previews=previews, producer_root=core.storage.root)

t1 = core.storage.write_temp(ORIG)
rel_o = core.storage.new_revision_relative_path("b1", "c1", "original", "p1", ".png")
core.storage.publish(t1, rel_o)
t2 = core.storage.write_temp(TRANS)
rel_t = core.storage.new_revision_relative_path("b1", "c1", "translated", "p1", ".png")
core.storage.publish(t2, rel_t)

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


def counts():
    rows = catalog.entries()
    published = [e for e in rows if e.resource_id.startswith("preview-")]
    deterministic = [e for e in rows if e.resource_id.startswith("page-original-")]
    files = [p for p in derived_root.rglob("*") if p.is_file()]
    return len(published), len(deterministic), len(files)


print("initial (rows published-style, rows page-original-style, files) =", counts())
for i in range(READS):
    res = rpc(server, "GetReaderProjection",
              {"chapter_id": "c1", "mode": "translated", "start_position": "beginning"})
    assert res["error"] is None, res["error"]
print("after %d reads                                    = %s" % (READS, counts()))

pub0, det0, files0 = counts()
# What a permanent delete would look for: the deterministic key.
found = catalog.lookup("page-original-p1")
print()
print("cleanup looks up 'page-original-p1' ->", "FOUND" if found else "None  <-- never minted")
print("LEAK: %d published-style row(s) and %d file(s) remain unfindable by cleanup"
      % (pub0, max(0, files0 - 1)))
print("rows per read   = %.2f" % (pub0 / READS))
catalog.close()
core.conn.close()
