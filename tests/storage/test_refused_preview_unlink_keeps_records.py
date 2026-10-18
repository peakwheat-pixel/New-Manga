"""F-004 (Codex R1): a refused preview unlink must not drop its records.

``unlink_preview_without_following`` returns False when it refuses to remove -
a reparse point, a traversing path, or a plain unlink failure. The caller used
to ignore that value and delete the catalog row regardless, so a file that was
still on disk lost its only registration: the leak became permanent AND
untraceable, because nothing was left to retry from.

These tests pin the caller, not the helper. The helper already had its own
injection tests; what was untested was that its refusal actually reaches the
manifest bookkeeping.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path
import sys

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from bootstrap.core_service import assemble_production_core
from infrastructure.resource_channel.render_preview import RenderPreviewPublisher


def _make_junction(link: Path, target: Path) -> None:
    """A junction needs no privilege on NTFS, unlike a symlink."""
    link.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(link), str(target)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 or not link.exists():
        pytest.skip(f"junction could not be created: {result.stderr or result.stdout}")


def test_refused_preview_unlink_keeps_the_catalog_row_and_the_manifest(
    tmp_path: Path,
) -> None:
    core = assemble_production_core(tmp_path / "data")
    try:
        data_root = tmp_path / "data"
        derived_root = tmp_path / "derived"
        derived_root.mkdir(parents=True, exist_ok=True)

        # Stand-in for the preview publisher's catalog: only the attributes
        # remove_managed reads (_root / _catalog) and the row shape matter.
        class _Entry:
            def __init__(self, rel_path: str) -> None:
                self.rel_path = rel_path

        class _Catalog:
            def __init__(self) -> None:
                self.rows: dict[str, _Entry] = {}

            def lookup(self, res_id: str) -> _Entry | None:
                return self.rows.get(res_id)

            def remove(self, res_id: str) -> None:
                self.rows.pop(res_id, None)

        catalog = _Catalog()

        class _Previews:
            _root = derived_root
            _catalog = catalog

        # A preview whose path is a junction: the helper refuses to unlink it.
        outside = tmp_path / "outside"
        outside.mkdir(parents=True, exist_ok=True)
        (outside / "real.png").write_bytes(b"real bytes")
        junction = derived_root / "page-original-p1"
        _make_junction(junction, outside)

        res_id = "page-original-p1"
        catalog.rows[res_id] = _Entry("page-original-p1")

        with core.conn:
            core.conn.execute(
                "INSERT INTO books (book_id, title, created_at, updated_at)"
                " VALUES ('b1', 'Book', 'now', 'now')"
            )
            core.conn.execute(
                "INSERT INTO book_cleanup_manifests (book_id, targets_json,"
                " created_at) VALUES ('b1', ?, 'now')",
                ('{"managed_targets": [], "page_ids": ["p1"]}',),
            )

        all_deleted = core.library._repo.cleanup_book_files(
            "b1", [], None, render_previews=_Previews(), page_ids=["p1"]
        )

        assert all_deleted is False, (
            "remove_managed reported success although the preview was refused"
        )
        assert catalog.rows.get(res_id) is not None, (
            "F-004: the catalog row was removed even though the file was not,"
            " so nothing is left to retry from"
        )
        remaining = core.conn.execute(
            "SELECT COUNT(*) FROM book_cleanup_manifests WHERE book_id = 'b1'"
        ).fetchone()[0]
        assert remaining == 1, (
            "F-004: the cleanup manifest was deleted even though cleanup did not"
            " complete, discarding the retry record"
        )
    finally:
        core.conn.close()


def test_successful_preview_unlink_still_clears_everything(tmp_path: Path) -> None:
    """The fix must not make the happy path stop cleaning up."""
    core = assemble_production_core(tmp_path / "data")
    try:
        derived_root = tmp_path / "derived"
        derived_root.mkdir(parents=True, exist_ok=True)
        preview_file = derived_root / "page-original-p1"
        preview_file.write_bytes(b"preview bytes")

        class _Entry:
            rel_path = "page-original-p1"

        class _Catalog:
            def __init__(self) -> None:
                self.rows = {"page-original-p1": _Entry()}

            def lookup(self, res_id: str):
                return self.rows.get(res_id)

            def remove(self, res_id: str) -> None:
                self.rows.pop(res_id, None)

        catalog = _Catalog()

        class _Previews:
            _root = derived_root
            _catalog = catalog

        with core.conn:
            core.conn.execute(
                "INSERT INTO books (book_id, title, created_at, updated_at)"
                " VALUES ('b1', 'Book', 'now', 'now')"
            )
            core.conn.execute(
                "INSERT INTO book_cleanup_manifests (book_id, targets_json,"
                " created_at) VALUES ('b1', ?, 'now')",
                ('{"managed_targets": [], "page_ids": ["p1"]}',),
            )

        all_deleted = core.library._repo.cleanup_book_files(
            "b1", [], None, render_previews=_Previews(), page_ids=["p1"]
        )

        assert all_deleted is True
        assert not preview_file.exists(), "the preview file should be gone"
        assert catalog.rows == {}
        remaining = core.conn.execute(
            "SELECT COUNT(*) FROM book_cleanup_manifests WHERE book_id = 'b1'"
        ).fetchone()[0]
        assert remaining == 0
    finally:
        core.conn.close()
