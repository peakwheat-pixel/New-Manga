"""AC4 regression: after a permanent delete, no preview rows or files may survive.

The existing ac4-leak-count-probe.py only measures - it prints numbers, so it cannot
fail, and a probe that cannot fail verifies nothing. This one asserts.

Sequence: read the translated projection a few times, permanently delete the book, then
assert that no publish-style catalog row and no preview file remains. On the current
implementation this is expected to FAIL, which is the point: C1's plan is to make it
pass, and a fix written against a red probe is verifiable, while one written against a
printed number is not.

Only reads and one dispatch call; no product code is touched. Fixtures under the
workspace.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

# AC4_REPO lets this run against an isolated copy of the tree.  Without it the probe
# silently imports the main checkout's src/, so a "pre-fix" run in a worktree would
# really be testing the fixed code - which is what happened the first time I tried.
REPO = Path(os.environ.get("AC4_REPO", r"G:\CODEX\New Manga"))
sys.path.insert(0, str(REPO / "src"))

from bootstrap.core_service import CoreServiceServer, assemble_production_core  # noqa: E402
from infrastructure.resource_channel.catalog_store import (  # noqa: E402
    ResourceCatalogStore,
    initialize_namespace,
)
from infrastructure.resource_channel.render_preview import RenderPreviewPublisher  # noqa: E402

WS = Path(r"G:\CODEX\New Manga.workspace\agent-output\coordinator\ac4-assert")
if WS.exists():
    shutil.rmtree(WS, ignore_errors=True)
WS.mkdir(parents=True)

ORIG = b"original bytes"
TRANS = b"translated bytes"
READS = 3

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
        "version": {"major": 2, "minor": 11},
        "request_id": "ac4-assert",
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

for _ in range(READS):
    res = rpc(server, "GetReaderProjection",
              {"chapter_id": "c1", "mode": "translated", "start_position": "beginning"})
    assert res["error"] is None, res["error"]

published_before = [e for e in catalog.entries() if e.resource_id.startswith("preview-")]
files_before = [p for p in derived_root.rglob("*") if p.is_file()]
print("after %d reads: %d publish-style rows, %d files" % (READS, len(published_before), len(files_before)))
assert len(published_before) > 0, "INCONCLUSIVE: no preview rows were created, nothing to leak"

# 直接调用 handler：L1112 对 payload 键做严格相等检查，dispatch 封装多带一层时会被拒。
# 直调可排除封装因素，确认删除流程本身的行为。
del_result, del_error = server.handle_permanently_delete_book(
    {"book_id": "b1", "confirm_permanent_delete": True})
print("permanent delete ->", "ok" if del_error is None else del_error)
assert del_error is None, del_error

published_after = [e for e in catalog.entries() if e.resource_id.startswith("preview-")]
files_after = [p for p in derived_root.rglob("*") if p.is_file()]
print("after delete:  %d publish-style rows, %d files" % (len(published_after), len(files_after)))
if published_after:
    print("  surviving rows:", [e.resource_id[:24] + "..." for e in published_after[:5]])
if files_after:
    print("  surviving files:", [p.name for p in files_after[:5]])

leaked_rows = len(published_after)
# R7 Finding 1: counting survivors cannot tell a lock file from a stranded PNG.  The
# namespace lock is the ONLY file that may remain; anything else is a leak, whatever the
# arithmetic says.
survivor_names = sorted(p.name for p in files_after)
# R8 Finding 1: this must be a literal set comparison.  "Filter out the lock, then require
# nothing left" also passes when NOTHING survived - including the lock - which is not the
# expected state.  Require the exact set.
expected_survivors = [".preview-lifecycle.lock"]
# R9 Finding 1: expressing the verdict as a COUNT reintroduced the hole.  An empty
# directory gives len() == 0, which reads as "no leak".  The verdict is now the boolean
# comparison itself; the number is only printed.
survivors_match = (survivor_names == expected_survivors)
leaked_files = 0 if survivors_match else max(1, len(survivor_names))
if not survivors_match:
    print("EXPECTED survivors %s, found %s" % (expected_survivors, survivor_names))
print()
print("survivors: %s" % survivor_names)
print("LEAK: %d row(s), %d unexpected file(s)" % (leaked_rows, leaked_files))
catalog.close()
core.conn.close()

# R1 Finding 4: printing FAIL is not failing.  A caller that only checks the exit code
# would score a leak as success, which is the failure mode this probe exists to catch.
if leaked_rows == 0 and leaked_files == 0:
    print("RESULT = PASS (no leak)")
    sys.exit(0)
print("RESULT = FAIL (leak present)")
sys.exit(1)
