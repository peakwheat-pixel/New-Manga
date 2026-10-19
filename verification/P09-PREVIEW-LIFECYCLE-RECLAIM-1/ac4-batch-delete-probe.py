"""AC4 batch delete: PermanentlyDeleteBooks must reclaim previews too, and only its own.

Two call sites reach cleanup_book_files. The single-book one is covered by
ac4-leak-assert-probe; this covers the batch handler, which I fixed only after grepping for
every call site - my first pass had changed one and missed the other.

It also asserts isolation: deleting book A must not reclaim book B's previews. The batch
path snapshots per book, so a bug there would most likely show up as cross-book
contamination rather than as a plain leak.

is_whole_library() refuses a batch that covers the library, so the fixture deliberately
holds two books and deletes one.
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

WS = Path(r"G:\CODEX\New Manga.workspace\agent-output\coordinator\ac4-batch")
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


def build(book: str, chapter: str, page_id: str) -> None:
    t = core.storage.write_temp(ORIG)
    rel_o = core.storage.new_revision_relative_path(book, chapter, "original", page_id, ".png")
    core.storage.publish(t, rel_o)
    t = core.storage.write_temp(TRANS)
    rel_t = core.storage.new_revision_relative_path(book, chapter, "translated", page_id, ".png")
    core.storage.publish(t, rel_t)
    with core.conn:
        core.conn.execute(
            "INSERT OR IGNORE INTO books (book_id,title,created_at,updated_at) VALUES (?,?,'now','now')",
            (book, book.upper()))
        core.conn.execute(
            "INSERT OR IGNORE INTO chapters (chapter_id,book_id,title,created_at,updated_at) VALUES (?,?,?,'now','now')",
            (chapter, book, "C"))
        core.conn.execute(
            "INSERT INTO pages (page_id,chapter_id,managed_original_ref,source_filename,"
            "source_hash,source_size_bytes,width,height,created_at,updated_at)"
            " VALUES (?,?,?, ?, ?, ?, 10, 10, 'now', 'now')",
            (page_id, chapter, rel_o, page_id + ".png",
             hashlib.sha256(ORIG).hexdigest(), len(ORIG)))
        core.conn.execute(
            "INSERT INTO media_artifacts (artifact_id,book_id,chapter_id,page_id,artifact_type,"
            "current_revision_id,created_at,updated_at)"
            " VALUES (?,?,?,?,'translated',?,'now','now')",
            ("a_" + page_id, book, chapter, page_id, "ar_" + page_id))
        core.conn.execute(
            "INSERT INTO artifact_revisions (artifact_revision_id,artifact_id,revision_no,"
            "managed_path,file_hash,mime_type,size_bytes,integrity_status,created_at)"
            " VALUES (?,?,1,?,?,'image/png',?,'valid','now')",
            ("ar_" + page_id, "a_" + page_id, rel_t,
             hashlib.sha256(TRANS).hexdigest(), len(TRANS)))


build("b1", "c1", "p1")
build("b1", "c1", "p1b")   # R3 Finding 3: AC3 needs cross-PAGE isolation too, so
build("b2", "c2", "p2")    # book 1 holds two pages and both keys must be reclaimed

for chapter in ("c1", "c2"):
    resp, _err = server.dispatch_request(json.dumps({
        "protocol": "new-manga.core",
        "version": {"major": 2, "minor": 11},
        "request_id": "ac4-batch",
        "command": "GetReaderProjection",
        "payload": {"chapter_id": chapter, "mode": "translated", "start_position": "beginning"},
    }))
    assert resp["error"] is None, resp["error"]

rows_before = [e.resource_id for e in catalog.entries() if e.resource_id.startswith("preview-")]
files_before = len([p for p in derived_root.rglob("*") if p.is_file()])
print("before: %d publish rows, %d files" % (len(rows_before), files_before))
assert len(rows_before) >= 2, "need one preview per book, got %d" % len(rows_before)

# R2 Finding 2: the previous version only counted survivors, so it passed when b1's
# snapshot was swapped for b2's ids - the survivor was the wrong book's preview and the
# count still matched.  Record which key belongs to b2 BEFORE the delete and assert
# identity, not arithmetic.
b1_artifact_ids = set(core.repository.list_page_artifact_ids(["p1", "p1b"]))
b1_expected = sorted(
    rid for rid in rows_before
    if (catalog.preview_lifecycle_row(rid) or {}).get("artifact_id") in b1_artifact_ids
)
print("b1 keys expected to be reclaimed: %d" % len(b1_expected))
assert len(b1_expected) == 2, (
    "cross-page fixture must give b1 two previews, got %d" % len(b1_expected)
)

b2_artifact_ids = set(core.repository.list_page_artifact_ids(["p2"]))
b2_expected = sorted(
    rid for rid in rows_before
    if (catalog.preview_lifecycle_row(rid) or {}).get("artifact_id") in b2_artifact_ids
)
print("b2 expected survivor(s): %s" % [x[:24] + "..." for x in b2_expected])
assert len(b2_expected) == 1, (
    "fixture must give b2 exactly one preview, got %d" % len(b2_expected)
)

# --- batch delete: two books exist, delete one, so is_whole_library() stays false ---
result, error = server.handle_permanently_delete_books({
    "book_ids": ["b1"],
    "confirmed_book_ids": ["b1"],
    "confirm_count": 1,
    "confirm_permanent_delete": True,
})
print("batch delete ->", "ok" if error is None else error)
assert error is None, error

rows_after = [e.resource_id for e in catalog.entries() if e.resource_id.startswith("preview-")]
files_after = [p for p in derived_root.rglob("*") if p.is_file()]
print("after:  %d publish rows, %d files" % (len(rows_after), len(files_after)))

# The survivor set must be exactly book 2's preview, not merely non-empty.
commands = core.conn.execute(
    "SELECT count(*) FROM books WHERE book_id = 'b2'").fetchone()[0]
print("book b2 still present =", commands == 1)

# R9 Finding 3: this counted every surviving row, but b2's preview IS expected to survive -
# so the baseline printed "LEAK: 1 row(s)" next to "RESULT = PASS".  Count only rows that
# are not the expected survivor.
leaked_rows = len([r for r in rows_after if r not in b2_expected])
# Expected survivors: b2's own preview file, plus the namespace lifecycle lock.  The
# earlier version subtracted only the lock, which counted b2's preview as a leak - my
# arithmetic, not a product defect.  Count the files that are neither.
# Every surviving file must be explainable by a surviving catalog row (or be the
# namespace lock).  The previous version only allowed publish rows, so book 2's own
# deterministic page-original entry counted as unexplained and I hardcoded '== 1' to let
# the probe pass.  That is a probe passing for the wrong reason, which is worse than a
# probe failing: derive the expectation from the surviving rows instead.
all_rows_after = [e for e in catalog.entries()]
# R9 Finding 2: comparing basenames accepted an orphan with the same name in another
# directory.  Compare each file's full relative path against the surviving rows' paths.
row_rel_paths = {e.rel_path for e in all_rows_after if e.rel_path}
unexplained = [
    p for p in files_after
    if p.name != ".preview-lifecycle.lock"
    and str(p.relative_to(derived_root)).replace("\\", "/") not in row_rel_paths
]
leaked_files = len(unexplained)
survivors_are_b2 = commands == 1 and rows_after == b2_expected

# R8 Finding 2: the probe checked that every surviving FILE maps to a surviving row, but
# not that every surviving ROW still has its file.  R8 deleted b2's preview png, kept its
# catalog row, and the probe still passed.  A row whose file is gone is not a preserved
# preview - it is a broken reference.
missing_files = []
for rid in rows_after:
    entry = catalog.lookup(rid)
    rel = getattr(entry, "rel_path", None) if entry is not None else None
    if not rel:
        missing_files.append(rid)
        continue
    if not (derived_root / rel).is_file():
        missing_files.append(rid)
if missing_files:
    print("rows whose file is missing: %s" % [r[:24] + "..." for r in missing_files])
print("survivors == b2's expected preview:", rows_after == b2_expected)
print()
print("LEAK: %d row(s), %d unexplained file(s)" % (leaked_rows, leaked_files))
if unexplained:
    print("  unexplained files:", [p.name for p in unexplained[:5]])
print("isolation: survivor is exactly b2's preview =", survivors_are_b2)

catalog.close()
core.conn.close()

reclaimed_b1 = [rid for rid in b1_expected if rid not in rows_after]
print("cross-page isolation: %d/%d of b1 keys reclaimed"
      % (len(reclaimed_b1), len(b1_expected)))
if (len(reclaimed_b1) == len(b1_expected)
        and len(rows_after) == len(b2_expected)
        and leaked_files == 0 and survivors_are_b2
        and not missing_files):
    print("RESULT = PASS (batch reclaimed its own preview and only its own)")
    sys.exit(0)
if rows_after != b2_expected:
    print("RESULT = FAIL (survivors are not the expected b2 preview: %s)"
          % [x[:24] + "..." for x in rows_after])
elif missing_files:
    # Injection B exposed this: the probe failed correctly but reported "book b2 itself is
    # gone", because the row-without-its-file case had no branch of its own and fell through
    # to the last one.  A tool whose failure message names the wrong cause is the same class
    # of problem as a probe that passes for the wrong reason.
    print("RESULT = FAIL (row survived but its file is missing: %s)"
          % [r[:24] + "..." for r in missing_files])
elif leaked_files > 0:
    print("RESULT = FAIL (unexplained files survived)")
else:
    print("RESULT = FAIL (book b2 itself is gone)")
sys.exit(1)
