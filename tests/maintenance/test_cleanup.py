"""TASK-056 controlled cleanup: cache generations, safety boundary,
preview/run/retry semantics — real ManagedFileStorage + temp layouts.

Discriminating power: the retryable-pending case cannot pass on the
pre-fix tree (no CleanupService/pending_cleanups exists — new
capability, declared not-applicable as a *pre-fix behaviour* test; all
cases here are regression pins for the safety invariants).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from application.maintenance.cleanup import (  # noqa: E402
    CleanupService,
    CleanupTarget,
)
from application.maintenance.trash import _JsonTrashManifest  # noqa: E402
from infrastructure.filesystem.managed_storage import (  # noqa: E402
    ManagedFileStorage,
)
from infrastructure.imaging.tile_cache_sweep import (  # noqa: E402
    WebtoonTileCacheSweeper,
)

NOW = "2026-09-19T03:30:00+00:00"


class StaticInventory:
    """Fixed population for boundary tests (bypasses the sweeper)."""

    def __init__(self, *targets: CleanupTarget) -> None:
        self._targets = tuple(targets)

    def list_cache_files(self) -> tuple[CleanupTarget, ...]:
        return self._targets


class FlakyRemover:
    """Fails the first N removal attempts, then delegates."""

    def __init__(self, inner, failures: int) -> None:
        self._inner = inner
        self._remaining = failures

    def remove_managed(self, relative_path: str) -> None:
        if self._remaining > 0:
            self._remaining -= 1
            raise OSError(f"transient storage fault on {relative_path}")
        self._inner.remove_managed(relative_path)


@pytest.fixture()
def cleanup_workspace(tmp_path: Path):
    managed = tmp_path / "managed"
    storage = ManagedFileStorage(managed)
    storage.ensure_layout()
    tile_dir = managed / "cache" / "webtoon-tiles"
    tile_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = tmp_path / "managed" / "trash-manifest.json"
    manifest = _JsonTrashManifest(manifest_path)
    sweeper = WebtoonTileCacheSweeper(tile_dir, managed)
    service = CleanupService(sweeper, storage, manifest)

    def make_tile(name: str, payload: bytes) -> Path:
        path = tile_dir / name
        path.write_bytes(payload)
        return path

    yield {
        "managed": managed,
        "tile_dir": tile_dir,
        "storage": storage,
        "service": service,
        "manifest": manifest,
        "make_tile": make_tile,
        "sweeper_files": lambda: [t.relative_path for t in sweeper.list_cache_files()],
    }


class TestSweeperInventory:
    def test_lists_every_generation_relative_to_managed_root(
        self, cleanup_workspace
    ) -> None:
        workspace = cleanup_workspace
        workspace["make_tile"]("tile-aaaa-00000.png", b"old-generation")
        workspace["make_tile"]("tile-bbbb-00000.png", b"new-generation")
        assert sorted(workspace["sweeper_files"]()) == [
            "cache/webtoon-tiles/tile-aaaa-00000.png",
            "cache/webtoon-tiles/tile-bbbb-00000.png",
        ]

    def test_missing_cache_dir_is_empty(self, tmp_path: Path) -> None:
        sweeper = WebtoonTileCacheSweeper(
            tmp_path / "managed" / "cache" / "webtoon-tiles", tmp_path / "managed"
        )
        assert sweeper.list_cache_files() == ()


class TestPreviewAndRun:
    def test_preview_reports_targets_and_total_bytes(self, cleanup_workspace) -> None:
        workspace = cleanup_workspace
        workspace["make_tile"]("tile-aaaa-00000.png", b"x" * 10)
        workspace["make_tile"]("tile-bbbb-00001.png", b"y" * 20)
        preview = workspace["service"].preview()
        assert preview.total_bytes == 30
        assert len(preview.targets) == 2

    def test_run_removes_all_generations_with_structured_result(
        self, cleanup_workspace
    ) -> None:
        workspace = cleanup_workspace
        tile_a = workspace["make_tile"]("tile-aaaa-00000.png", b"old")
        tile_b = workspace["make_tile"]("tile-bbbb-00000.png", b"new")

        outcome = workspace["service"].run()

        assert outcome.removed == 2 and outcome.failed == 0
        assert outcome.to_dict()[tile_a.name.replace("tile-", "cache/webtoon-tiles/tile-")][
            "status"
        ] == "ok"
        assert not tile_a.exists() and not tile_b.exists()

    def test_run_is_idempotent(self, cleanup_workspace) -> None:
        workspace = cleanup_workspace
        workspace["make_tile"]("tile-aaaa-00000.png", b"data")
        assert workspace["service"].run().removed == 1
        second = workspace["service"].run()
        assert second.removed == 0 and second.failed == 0


class TestSafetyBoundary:
    def test_paths_outside_safe_prefixes_are_skipped_and_survive(
        self, cleanup_workspace
    ) -> None:
        workspace = cleanup_workspace
        # a managed ORIGINAL (not a cache artefact) must be skipped even if
        # a broken inventory ever reports it
        original = workspace["managed"] / "books" / "b" / "original" / "p1.png"
        original.parent.mkdir(parents=True, exist_ok=True)
        original.write_bytes(b"ORIGINAL")
        inventory = StaticInventory(
            CleanupTarget("books/b/original/p1.png", 8),
            CleanupTarget("cache/webtoon-tiles/tile-cccc-00000.png", 4),
        )
        storage = workspace["storage"]
        service = CleanupService(inventory, storage, workspace["manifest"])
        (workspace["managed"] / "cache" / "webtoon-tiles").mkdir(
            parents=True, exist_ok=True
        )
        (workspace["managed"] / "cache" / "webtoon-tiles" / "tile-cccc-00000.png").write_bytes(
            b"tile"
        )

        outcome = service.run()

        assert outcome.skipped == 1 and outcome.removed == 1
        assert outcome.to_dict()["books/b/original/p1.png"]["status"] == "skipped"
        assert original.is_file(), "original must survive"

    def test_user_source_outside_managed_root_is_never_addressed(
        self, tmp_path: Path
    ) -> None:
        user_source = tmp_path / "user-side" / "art.tiff"
        user_source.parent.mkdir(parents=True, exist_ok=True)
        user_source.write_bytes(b"USER SOURCE BYTES")
        storage = ManagedFileStorage(tmp_path / "managed")
        storage.ensure_layout()
        with pytest.raises(Exception):
            storage.remove_managed("../user-side/art.tiff")
        assert user_source.read_bytes() == b"USER SOURCE BYTES"


class TestRetryableFailures:
    def test_failure_persists_pending_and_retry_clears_it(
        self, cleanup_workspace
    ) -> None:
        workspace = cleanup_workspace
        tile = workspace["make_tile"]("tile-aaaa-00000.png", b"data")
        flaky = CleanupService(
            workspace["service"]._inventory, FlakyRemover(workspace["storage"], 1),
            workspace["manifest"],
        )

        outcome = flaky.run()

        assert outcome.failed == 1
        assert workspace["service"].pending_cleanup_count() == 1

        retry = workspace["service"].retry_pending_cleanups()

        assert retry.removed == 1 and retry.failed == 0
        assert not tile.exists()
        assert workspace["service"].pending_cleanup_count() == 0
