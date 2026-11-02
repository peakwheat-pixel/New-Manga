"""M2-DERIVED-GC-1: startup orphan/dead-row sweep of the derived root.

Pins the two failure-class-equivalent reclamation classes only (RC4-12
first slice, PARTIAL mitigation): orphan files under ``previews/``/
``pages/`` (stem absent from the catalog -- un-issuable either way) and
dead ``derived-read-only`` rows (file gone -- the rev 1.7 self-heal
re-publishes deterministic keys; a preview key's issue moves typed code
but still serves no bytes, see the collect_orphans docstring). Live files
with live rows must survive untouched, escaping paths must fail closed,
and the sweep must stay fail-soft at assembly (a GC error never blocks
the service).
"""

from __future__ import annotations

import sys
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from infrastructure.resource_channel.catalog_store import (
    ResourceCatalogStore,
    initialize_namespace,
)
from infrastructure.resource_channel.render_preview import RenderPreviewPublisher


def _make(tmp_path: Path) -> tuple[RenderPreviewPublisher, ResourceCatalogStore, Path]:
    # M2-DERIVED-GC-2 (R4-A1): every file-backed fixture first binds its OWN
    # fresh derived root through the frozen narrow initializer; an unbound
    # store is a typed refusal, never an un-leased write channel.
    root = tmp_path / "derived"
    root.mkdir(parents=True, exist_ok=True)
    catalog_db = tmp_path / "catalog.sqlite"
    initialize_namespace(catalog_db, root)
    catalog = ResourceCatalogStore(catalog_db)
    return RenderPreviewPublisher(root, catalog), catalog, root


def _touch(root: Path, rel_path: str) -> Path:
    target = root / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(b"png-bytes")
    return target


def test_orphan_files_removed_in_both_directories(tmp_path) -> None:
    publisher, catalog, root = _make(tmp_path)
    live = _touch(root, "previews/preview-live.png")
    catalog.upsert("preview-live", "derived-read-only", "previews/preview-live.png")
    orphan_preview = _touch(root, "previews/preview-orphan.png")
    orphan_page = _touch(root, "pages/page-original-orphan.png")

    stats = publisher.collect_orphans()

    assert stats == {"orphan_files_removed": 2, "dead_rows_removed": 0}
    assert live.is_file(), "live file must survive"
    assert not orphan_preview.exists()
    assert not orphan_page.exists()
    assert catalog.lookup("preview-live") is not None


def test_dead_rows_removed_and_live_rows_kept(tmp_path) -> None:
    publisher, catalog, root = _make(tmp_path)
    _touch(root, "previews/preview-alive.png")
    catalog.upsert("preview-alive", "derived-read-only", "previews/preview-alive.png")
    catalog.upsert("preview-dead", "derived-read-only", "previews/preview-dead.png")
    catalog.upsert("page-original-dead", "derived-read-only", "pages/page-original-dead.png")

    stats = publisher.collect_orphans()

    assert stats == {"orphan_files_removed": 0, "dead_rows_removed": 2}
    assert catalog.lookup("preview-alive") is not None
    assert catalog.lookup("preview-dead") is None
    assert catalog.lookup("page-original-dead") is None
    assert (root / "previews/preview-alive.png").is_file()


def test_dead_deterministic_row_self_heals_to_same_key_after_gc(tmp_path) -> None:
    # M2-PAGE-RESOURCE-RESOLVE-1 interplay: removing a dead page-original
    # row must not break the resolve contract -- the next resolve
    # re-publishes under the SAME key (upsert rebuilds the row).
    import io

    from PIL import Image

    publisher, catalog, root = _make(tmp_path)
    buffer = io.BytesIO()
    Image.new("RGBA", (8, 8), (10, 20, 30, 255)).save(buffer, format="PNG")
    published = publisher.publish_original(
        _write_source(tmp_path, buffer.getvalue()), "page-original-p1", ".png"
    )
    assert published == {"resource_id": "page-original-p1", "revision": "original"}
    (root / "pages/page-original-p1.png").unlink()

    stats = publisher.collect_orphans()
    assert stats["dead_rows_removed"] == 1
    assert catalog.lookup("page-original-p1") is None

    republished = publisher.publish_original(
        _write_source(tmp_path, buffer.getvalue()), "page-original-p1", ".png"
    )
    assert republished["resource_id"] == "page-original-p1"
    assert catalog.lookup("page-original-p1") is not None
    assert (root / "pages/page-original-p1.png").is_file()


def test_escaping_catalog_row_fails_closed(tmp_path) -> None:
    import sqlite3

    publisher, catalog, root = _make(tmp_path)
    catalog.close()
    # upsert() refuses traversal segments at the write boundary, so an
    # escaping row can only exist if the catalog db was tampered with
    # externally -- exactly the scenario this defence targets.
    with sqlite3.connect(tmp_path / "catalog.sqlite") as conn:
        conn.execute(
            "INSERT INTO resource_catalog (resource_id, scope_class, rel_path)"
            " VALUES ('preview-escape', 'derived-read-only', '../escape.png')"
        )
    reopened = ResourceCatalogStore(tmp_path / "catalog.sqlite")
    tampered = RenderPreviewPublisher(root, reopened)
    import pytest

    with pytest.raises(OSError, match="escaped derived root"):
        tampered.collect_orphans()


def test_managed_scope_rows_are_never_touched_by_the_sweep(tmp_path) -> None:
    # DSH r1 C-1: the same catalog db can carry managed-read-only rows
    # (acceptance_bridge m2ac1-page-*; rel_path relative to the MANAGED
    # root). The sweep must filter on scope_class BEFORE touching anything
    # -- dropping the filter would resolve those rel_paths against the
    # DERIVED root, find no file, and delete live managed rows.
    publisher, catalog, root = _make(tmp_path)
    catalog.upsert(
        "m2ac1-page-0",
        "managed-read-only",
        "books/b1/chapters/c1/translated/x.png",
    )

    stats = publisher.collect_orphans()

    assert stats == {"orphan_files_removed": 0, "dead_rows_removed": 0}
    assert catalog.lookup("m2ac1-page-0") is not None


def test_directory_level_escape_fails_closed(tmp_path) -> None:
    # DSH r1 C-2: the per-directory resolve()/is_relative_to() gate (the
    # only door in front of the unlink loop) must fail closed when the
    # directory itself escapes the derived root -- e.g. previews/ replaced
    # by a junction pointing outside. Nothing outside may be deleted.
    import os
    import sys

    if sys.platform != "win32":
        import pytest

        pytest.skip("directory junctions are a Windows reparse-point facility")

    publisher, catalog, root = _make(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "keep-me.txt").write_bytes(b"do-not-delete")
    catalog.upsert("preview-keep", "derived-read-only", "previews/preview-keep.png")

    junction = root / "previews"
    root.mkdir(parents=True, exist_ok=True)
    # CPython's Windows-only junction API: os.symlink would need elevated
    # privileges, a directory junction does not.
    import _winapi

    _winapi.CreateJunction(str(outside), str(junction))
    try:
        import pytest

        with pytest.raises(OSError, match="escaped derived root"):
            publisher.collect_orphans()
        assert (outside / "keep-me.txt").is_file()
        # the catalogued file "inside" the escaped directory is untouched
        assert catalog.lookup("preview-keep") is not None
    finally:
        # os.rmdir removes the junction itself, never the target contents
        os.rmdir(str(junction))


def test_missing_directories_are_a_clean_noop(tmp_path) -> None:
    publisher, catalog, root = _make(tmp_path)
    catalog.upsert("preview-only-row", "derived-read-only", "previews/preview-only-row.png")

    stats = publisher.collect_orphans()

    # previews/ and pages/ were never created, but the dead row is still
    # reclaimable (the root itself is created by the sweep)
    assert stats == {"orphan_files_removed": 0, "dead_rows_removed": 1}
    assert root.is_dir()


def test_startup_gc_is_fail_soft_and_logs_a_summary(capsys) -> None:
    from bootstrap.core_service import _run_startup_gc

    class ExplodingPublisher:
        def collect_orphans(self):
            raise OSError("derived root on a dead volume")

    # a GC error must never block assembly
    _run_startup_gc(ExplodingPublisher())
    err = capsys.readouterr().err
    assert "[core.derived_gc] skipped:" in err

    class CountingPublisher:
        def collect_orphans(self):
            return {"orphan_files_removed": 3, "dead_rows_removed": 1}

    _run_startup_gc(CountingPublisher())
    err = capsys.readouterr().err
    assert "[core.derived_gc] orphan_files_removed=3 dead_rows_removed=1" in err


def _write_source(tmp_path: Path, data: bytes) -> Path:
    source = tmp_path / "source.png"
    source.write_bytes(data)
    return source


# ---------------------------------------------------------------------------
# M2-DERIVED-GC-2: reference-safe reclamation of retired preview copies.
# The sweep itself runs ONLY under an exclusive namespace lease; these tests
# drive the sweep function directly against a real product SQLite database
# (the lease-exclusivity discrimination lives in
# tests/m2_resource_channel/test_handle_resolver.py).
# ---------------------------------------------------------------------------

_NOW = "2026-01-01T00:00:00.000+00:00"


def _product_core(tmp_path: Path):
    from bootstrap.core_service import assemble_production_core

    return assemble_production_core(tmp_path / "product-data")


def _seed_product_revision(
    core,
    *,
    artifact_id: str,
    revision_id: str,
    revision_no: int,
    managed_path: str,
    sha256: str,
    size: int,
    current_revision_id: str | None,
    is_pinned: bool = False,
) -> None:
    """One TRANSLATED artifact with an exact revision row (SELECT-only for
    the sweep; nothing here is written by it)."""
    conn = core.conn
    conn.execute(
        "INSERT OR IGNORE INTO books (book_id, title, created_at, updated_at)"
        " VALUES ('book', 'b', ?, ?)",
        (_NOW, _NOW),
    )
    conn.execute(
        "INSERT OR IGNORE INTO chapters (chapter_id, book_id, title, sort_order,"
        " created_at, updated_at) VALUES ('chapter', 'book', 'c', 0, ?, ?)",
        (_NOW, _NOW),
    )
    conn.execute(
        "INSERT OR IGNORE INTO pages (page_id, chapter_id, sort_order, created_at,"
        " updated_at) VALUES ('page', 'chapter', 0, ?, ?)",
        (_NOW, _NOW),
    )
    conn.execute(
        "INSERT OR IGNORE INTO media_artifacts (artifact_id, book_id, chapter_id, page_id,"
        " artifact_type, current_revision_id, created_at, updated_at)"
        " VALUES (?, 'book', 'chapter', 'page', 'translated', ?, ?, ?)",
        (artifact_id, current_revision_id, _NOW, _NOW),
    )
    conn.execute(
        "INSERT INTO artifact_revisions (artifact_revision_id, artifact_id,"
        " revision_no, managed_path, file_hash, mime_type, width, height,"
        " size_bytes, integrity_status, is_pinned, created_at)"
        " VALUES (?, ?, ?, ?, ?, 'image/png', 8, 8, ?, 'valid', ?, ?)",
        (revision_id, artifact_id, revision_no, managed_path, sha256, size, is_pinned, _NOW),
    )
    conn.commit()


def _seed_retired_preview(
    tmp_path: Path,
    publisher: RenderPreviewPublisher,
    catalog: ResourceCatalogStore,
    core,
    *,
    resource_id_hint: str = "x",
    producer_root: Path,
    managed_path: str = "books/b/chapters/c/translated/r1.png",
    current_revision_id: str | None = None,
    is_pinned: bool = False,
    revision_no: int = 1,
    managed_payload: bytes = b"managed-source-bytes",
) -> tuple[str, Path]:
    """One full production-shaped cycle: a managed revision row, a preview
    copy published with its verified origin, and the retired mark."""
    import hashlib

    from infrastructure.resource_channel.catalog_store import PreviewOrigin

    managed_file = tmp_path / f"managed-{resource_id_hint}.png"
    managed_file.write_bytes(managed_payload)
    sha256 = hashlib.sha256(managed_payload).hexdigest()

    _seed_product_revision(
        core,
        artifact_id=f"artifact-{resource_id_hint}",
        revision_id=f"revision-{resource_id_hint}",
        revision_no=revision_no,
        managed_path=managed_path,
        sha256=sha256,
        size=len(managed_payload),
        current_revision_id=current_revision_id,
        is_pinned=is_pinned,
    )
    # the published preview copy is byte-for-byte the managed render output
    published = publisher.publish(managed_file, f"rev-{revision_no}", origin=PreviewOrigin(
        producer_root=str(producer_root),
        artifact_id=f"artifact-{resource_id_hint}",
        artifact_revision_id=f"revision-{resource_id_hint}",
        managed_rel_path=managed_path,
    ))
    resource_id = published["resource_id"]
    copy_path = publisher._root / "previews" / f"{resource_id}.png"
    catalog.mark_preview_retired(resource_id)
    return resource_id, copy_path


def _sweep(tmp_path, publisher, catalog, core, producer_root: Path):
    from bootstrap.core_service import _run_retired_preview_gc

    return _run_retired_preview_gc(
        publisher, catalog, core.conn, producer_root=str(producer_root)
    )


def test_retired_non_current_non_pinned_copy_is_deleted_with_metadata(tmp_path) -> None:
    # D1 (design §4): the only deletable shape -- registered origin, retired,
    # source revision neither current nor pinned, verified copy.
    publisher, catalog, root = _make(tmp_path)
    core = _product_core(tmp_path)
    producer_root = tmp_path / "data"
    resource_id, copy_path = _seed_retired_preview(
        tmp_path, publisher, catalog, core, producer_root=producer_root
    )
    assert copy_path.is_file()
    assert catalog.lookup(resource_id) is not None

    stats = _sweep(tmp_path, publisher, catalog, core, producer_root)

    assert stats["retired_deleted"] == 1
    assert stats["protected_retained"] == 0
    assert not copy_path.exists(), "the verified retired copy must be gone"
    assert catalog.lookup(resource_id) is None, "catalog row removed after the file"
    assert catalog.preview_lifecycle_row(resource_id) is None

    # idempotent re-run (repeated scans are a no-op on empty candidate set)
    again = _sweep(tmp_path, publisher, catalog, core, producer_root)
    assert again["retired_deleted"] == 0


def test_current_revision_retained_flipping_current_deletes(tmp_path) -> None:
    # K2 with a single-condition red/green pair (design §6 G4): the SAME
    # fixture is protected only by the current pointer -- flipping it (and
    # nothing else) turns the copy deletable.
    publisher, catalog, root = _make(tmp_path)
    core = _product_core(tmp_path)
    producer_root = tmp_path / "data"
    resource_id, copy_path = _seed_retired_preview(
        tmp_path, publisher, catalog, core,
        producer_root=producer_root,
        current_revision_id="revision-x",
    )

    stats = _sweep(tmp_path, publisher, catalog, core, producer_root)
    assert stats["retired_deleted"] == 0
    assert stats["protected_retained"] == 1
    assert copy_path.is_file(), "the CURRENT revision's copy must survive"

    # the real rotation shape: the artifact rotates to a NEWER revision and
    # the current pointer follows it (the pointer itself can never be
    # cleared -- schema trigger) -- the older revision is then no longer
    # current and its retired copy becomes deletable.
    _seed_product_revision(
        core,
        artifact_id="artifact-x",
        revision_id="revision-newer",
        revision_no=2,
        managed_path="books/b/chapters/c/translated/r2.png",
        sha256="0" * 64,
        size=1,
        current_revision_id=None,
    )
    core.conn.execute(
        "UPDATE media_artifacts SET current_revision_id = 'revision-newer',"
        " updated_at = ? WHERE artifact_id = 'artifact-x'",
        (_NOW,),
    )
    core.conn.commit()
    stats = _sweep(tmp_path, publisher, catalog, core, producer_root)
    assert stats["retired_deleted"] == 1
    assert not copy_path.exists()


def test_pinned_revision_retained_even_without_current(tmp_path) -> None:
    # K2: a pin protects the revision even when it is not the current one.
    publisher, catalog, root = _make(tmp_path)
    core = _product_core(tmp_path)
    producer_root = tmp_path / "data"
    resource_id, copy_path = _seed_retired_preview(
        tmp_path, publisher, catalog, core,
        producer_root=producer_root, is_pinned=True,
    )

    stats = _sweep(tmp_path, publisher, catalog, core, producer_root)

    assert stats["retired_deleted"] == 0
    assert stats["protected_retained"] == 1
    assert copy_path.is_file()


def test_unknown_history_rows_without_lifecycle_are_retained(tmp_path) -> None:
    # U1: a live file with a live catalog row and NO origin record (pre-GC-2
    # history, loader rows) is never a candidate -- no filename/mtime/rev-N
    # guessing, no backfill.
    publisher, catalog, root = _make(tmp_path)
    core = _product_core(tmp_path)
    producer_root = tmp_path / "data"
    live = _touch(root, "previews/preview-historic.png")
    catalog.upsert("preview-historic", "derived-read-only", "previews/preview-historic.png")

    stats = _sweep(tmp_path, publisher, catalog, core, producer_root)

    assert stats == {
        "retired_deleted": 0,
        "protected_retained": 0,
        "unknown_skipped": 0,
        "lifecycle_metadata_reclaimed": 0,
    }
    assert live.is_file()
    assert catalog.lookup("preview-historic") is not None


def test_wrong_producer_root_is_not_a_candidate(tmp_path) -> None:
    # G1: a candidate whose registered producer root differs from this
    # Core's data root is not even enumerated (cross-root rows never delete).
    publisher, catalog, root = _make(tmp_path)
    core = _product_core(tmp_path)
    resource_id, copy_path = _seed_retired_preview(
        tmp_path, publisher, catalog, core,
        producer_root=tmp_path / "somewhere-else",
    )

    stats = _sweep(tmp_path, publisher, catalog, core, producer_root=tmp_path / "this-core")

    assert stats["retired_deleted"] == 0
    assert copy_path.is_file()


def test_page_original_and_managed_scopes_never_become_candidates(tmp_path) -> None:
    # G1/K5: only previews/<resource_id>.png under derived-read-only is
    # candidate-shaped; page originals and managed rows are filtered before
    # any resolution.
    publisher, catalog, root = _make(tmp_path)
    core = _product_core(tmp_path)
    producer_root = tmp_path / "data"
    from infrastructure.resource_channel.catalog_store import PreviewOrigin

    page_copy = _touch(root, "pages/page-original-p1.png")
    catalog.upsert("page-original-p1", "derived-read-only", "pages/page-original-p1.png")
    catalog.execute_foreign = None
    # an origin row planted on a non-preview shape must not surface either
    catalog._connection.execute(
        "INSERT INTO preview_lifecycle (resource_id, producer_root, artifact_id,"
        " artifact_revision_id, managed_rel_path, retired)"
        " VALUES ('page-original-p1', ?, 'a', 'r', 'books/x.png', 1)",
        (str(producer_root),),
    )
    catalog._connection.commit()
    managed_rel = _touch(root, "previews/preview-mng.png")
    catalog.upsert("preview-mng", "managed-read-only", "previews/preview-mng.png")

    stats = _sweep(tmp_path, publisher, catalog, core, producer_root)

    assert stats["retired_deleted"] == 0
    assert page_copy.is_file() and managed_rel.is_file()
    assert catalog.lookup("page-original-p1") is not None
    assert catalog.lookup("preview-mng") is not None


def test_manual_modification_hash_mismatch_retains_copy(tmp_path) -> None:
    # U4: a modified/replaced copy is UNKNOWN -> retained (never delete a
    # file just because its origin row says so).
    publisher, catalog, root = _make(tmp_path)
    core = _product_core(tmp_path)
    producer_root = tmp_path / "data"
    resource_id, copy_path = _seed_retired_preview(
        tmp_path, publisher, catalog, core, producer_root=producer_root
    )
    copy_path.write_bytes(b"hand-edited-png")  # same path, different content

    stats = _sweep(tmp_path, publisher, catalog, core, producer_root)

    assert stats["retired_deleted"] == 0
    assert copy_path.read_bytes() == b"hand-edited-png"
    assert catalog.lookup(resource_id) is not None


def test_inflight_reader_blocks_sweep_delete_until_release(tmp_path) -> None:
    # K4 at the SWEEP level (Codex r1 F-06): a real reader handle held OPEN
    # across the whole sweep makes the delete-open fail (the reader's share
    # mode admits no DELETE access), the copy AND its metadata are retained,
    # and the next safe window after the reader exits reclaims normally.
    publisher, catalog, root = _make(tmp_path)
    core = _product_core(tmp_path)
    producer_root = tmp_path / "data"
    resource_id, copy_path = _seed_retired_preview(
        tmp_path, publisher, catalog, core, producer_root=producer_root
    )

    reader = open(copy_path, "rb")
    try:
        stats = _sweep(tmp_path, publisher, catalog, core, producer_root)
        assert stats["retired_deleted"] == 0
        assert copy_path.is_file(), "an in-flight reader must block the delete"
        assert catalog.lookup(resource_id) is not None, (
            "metadata must not be removed while the copy survives"
        )
        assert catalog.preview_lifecycle_row(resource_id) is not None
    finally:
        reader.close()

    stats = _sweep(tmp_path, publisher, catalog, core, producer_root)
    assert stats["retired_deleted"] == 1
    assert not copy_path.exists()
    assert catalog.lookup(resource_id) is None


def test_product_db_busy_retains_everything_fail_soft(tmp_path) -> None:
    # G5: a busy product database keeps the candidates (skip with a reason);
    # busy never lowers protection, and the failure never leaves the sweep
    # half-done on the catalog side.
    publisher, catalog, root = _make(tmp_path)
    core = _product_core(tmp_path)
    producer_root = tmp_path / "data"
    resource_id, copy_path = _seed_retired_preview(
        tmp_path, publisher, catalog, core, producer_root=producer_root
    )

    import sqlite3

    blocker = sqlite3.connect(tmp_path / "product-data" / "library.db", timeout=0.1)
    try:
        blocker.execute("BEGIN IMMEDIATE")
        stats = _sweep(tmp_path, publisher, catalog, core, producer_root)
    finally:
        blocker.rollback()
        blocker.close()

    assert stats["retired_deleted"] == 0
    assert copy_path.is_file()
    assert catalog.lookup(resource_id) is not None


def test_crash_after_unlink_recovers_via_dead_row_cleanup(tmp_path) -> None:
    # §3 crash point "copy deleted, catalog transaction failed/lost": the
    # next safe window's first-slice dead-row pass removes the row AND the
    # dangling origin record (metadata only) -- never another file.
    publisher, catalog, root = _make(tmp_path)
    core = _product_core(tmp_path)
    producer_root = tmp_path / "data"
    resource_id, copy_path = _seed_retired_preview(
        tmp_path, publisher, catalog, core, producer_root=producer_root
    )
    copy_path.unlink()  # the crash happened between unlink and the catalog tx

    orphans = publisher.collect_orphans()
    assert orphans["dead_rows_removed"] == 1
    assert catalog.lookup(resource_id) is None
    assert catalog.preview_lifecycle_row(resource_id) is None


def test_metadata_reclaim_is_metadata_only(tmp_path) -> None:
    # D2 boundary: reclaiming origin rows with no catalog row must never
    # imply anything about files -- a stray file with a reclaimed key stays.
    publisher, catalog, root = _make(tmp_path)
    core = _product_core(tmp_path)
    producer_root = tmp_path / "data"
    resource_id, copy_path = _seed_retired_preview(
        tmp_path, publisher, catalog, core, producer_root=producer_root
    )
    # simulate the lost catalog row (crash between the two deletions is not
    # possible in one transaction; a wiped catalog row is the recoverable
    # shape the D2 rule exists for)
    catalog._connection.execute("DELETE FROM resource_catalog WHERE resource_id = ?", (resource_id,))
    catalog._connection.commit()

    stats = _sweep(tmp_path, publisher, catalog, core, producer_root)

    assert stats["lifecycle_metadata_reclaimed"] == 1
    # the file is NOT touched by the metadata reclaim (it is an orphan for
    # the first slice, which only deletes un-catalogued files inside the
    # sweep directories -- run it to prove the combined effect is bounded)
    orphans = publisher.collect_orphans()
    assert orphans["orphan_files_removed"] == 1
    assert not copy_path.exists()


def test_sweep_reports_skip_reasons_and_survives_publisher_errors(tmp_path, capsys) -> None:
    # G5: per-candidate refusals are counted with a reason on stderr and the
    # sweep stays fail-soft.
    publisher, catalog, root = _make(tmp_path)
    core = _product_core(tmp_path)
    producer_root = tmp_path / "data"
    resource_id, copy_path = _seed_retired_preview(
        tmp_path, publisher, catalog, core, producer_root=producer_root
    )
    copy_path.unlink()  # the delete open will report "file missing"

    stats = _sweep(tmp_path, publisher, catalog, core, producer_root)

    assert stats["retired_deleted"] == 0
    assert stats["unknown_skipped"] == 1
    err = capsys.readouterr().err
    assert "[core.derived_gc] retired copy kept:" in err
