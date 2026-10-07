"""M2-DERIVED-GC-1: startup orphan/dead-row sweep of the derived root.

Pins the two behaviour-equivalent reclamation classes only (RC4-12 first
slice): orphan files under ``previews/``/``pages/`` (stem absent from the
catalog -- un-issuable either way) and dead ``derived-read-only`` rows
(file gone -- already unresolvable; the rev 1.7 self-heal re-publishes
deterministic keys). Live files with live rows must survive untouched,
escaping paths must fail closed, and the sweep must stay fail-soft at
assembly (a GC error never blocks the service).
"""

from __future__ import annotations

import sys
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from infrastructure.resource_channel.catalog_store import ResourceCatalogStore
from infrastructure.resource_channel.render_preview import RenderPreviewPublisher


def _make(tmp_path: Path) -> tuple[RenderPreviewPublisher, ResourceCatalogStore, Path]:
    root = tmp_path / "derived"
    catalog = ResourceCatalogStore(tmp_path / "catalog.sqlite")
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
