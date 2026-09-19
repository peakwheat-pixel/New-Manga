"""Webtoon tile-cache inventory for the controlled cleanup use case
(TASK-056 AC 3): every ``tile-*.png`` generation under the tile cache
directory is reportable, including the ``_TILE_CACHE_FORMAT`` leftovers
of older generations (TASK-045 R-005) — the cache key embeds the format
tag, the source digest and the geometry, so any change leaves the old
generation behind and this sweeper is what reclaims it.

The sweeper only *lists*; removal goes through the injected controlled
remover so the managed-root boundary stays enforced in one place.
"""

from __future__ import annotations

from pathlib import Path

from application.maintenance.cleanup import CleanupTarget

_TILE_GLOB = "tile-*.png"


class WebtoonTileCacheSweeper:
    """Inventory of one tile-cache directory, addressed relative to the
    managed root (production layout:
    ``<managed_root>/cache/webtoon-tiles/tile-*.png``)."""

    def __init__(self, cache_root: Path, managed_root: Path) -> None:
        self._cache_root = Path(cache_root)
        self._managed_root = Path(managed_root)

    def list_cache_files(self) -> tuple[CleanupTarget, ...]:
        if not self._cache_root.is_dir():
            return ()
        resolved_cache = self._cache_root.resolve()
        prefix = resolved_cache.relative_to(self._managed_root.resolve())
        targets = []
        for path in sorted(self._cache_root.glob(_TILE_GLOB)):
            # TASK-060 Q-007 ②: re-check *after* resolution — a reparse
            # point / symlink named like a tile may point anywhere,
            # including back at a protected revision file inside the
            # managed root.  Such an entry is never reported as a
            # cleanable target.
            resolved = path.resolve()
            try:
                resolved.relative_to(resolved_cache)
            except ValueError:
                continue
            if resolved.is_file():
                relative = (prefix / path.name).as_posix()
                targets.append(CleanupTarget(relative, path.stat().st_size))
        return tuple(targets)
