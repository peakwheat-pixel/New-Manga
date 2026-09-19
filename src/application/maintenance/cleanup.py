"""Controlled cleanup use case (TASK-021 frozen subset 2, TASK-056).

Scope and safety boundary (AC 1) — the two lists that govern everything
in this module:

**Cleanable** (only ever these): rebuildable caches and other controlled
copies whose relative path starts with one of ``CACHE_SAFE_PREFIXES``
(production: ``cache/webtoon-tiles/`` tile generations, including the
``_TILE_CACHE_FORMAT`` leftovers of TASK-045 R-005). Model/weight
directories can be registered later; none is registered by this slice
(real provider endpoints are a window exclusion).

**Never cleanable** (structurally, by prefix *and* by root):

- user source files: they live outside the managed root and the injected
  :class:`ControlledFileRemover` refuses any path escaping it;
- current / pinned artifact revisions and every business row: cleanup
  never opens the database — it only addresses files under the safe
  prefixes, and revisions are stored outside ``cache/``;
- Lock-protected objects and task resumability data.

Every run is previewable (targets + bytes, AC 2), returns a structured
per-target result, is idempotent (already-gone files complete silently),
and a failed removal leaves a persisted ``pending_cleanups`` manifest
entry for retry (AC 4 — same ledger pattern as TASK-053 R-04).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Iterable, Protocol

from application.maintenance.ports import (
    ControlledFileRemover,
    TrashManifestStore,
)

#: Relative-path prefixes cleanup may address. Anything else is skipped
#: with a reason and is never handed to the remover.
CACHE_SAFE_PREFIXES = ("cache/",)

_PENDING_KEY = "pending_cleanups"


@dataclass(frozen=True)
class CleanupTarget:
    """One candidate file, addressed relative to the managed root."""

    relative_path: str
    size_bytes: int


class CacheInventorySource(Protocol):
    """Enumerates the cleanable cache population (infrastructure side)."""

    def list_cache_files(self) -> tuple[CleanupTarget, ...]: ...


@dataclass(frozen=True)
class CleanupPreview:
    """AC 2 pre-flight: what would be removed, and how much."""

    targets: tuple[CleanupTarget, ...]
    total_bytes: int


@dataclass(frozen=True)
class CleanupItemResult:
    status: str  # "ok" | "failed" | "skipped"
    reason: str = ""


@dataclass(frozen=True)
class CleanupOutcome:
    """AC 2 structured result of one run (or retry)."""

    items: tuple[tuple[str, CleanupItemResult], ...]

    @property
    def removed(self) -> int:
        return sum(1 for _, item in self.items if item.status == "ok")

    @property
    def failed(self) -> int:
        return sum(1 for _, item in self.items if item.status == "failed")

    @property
    def skipped(self) -> int:
        return sum(1 for _, item in self.items if item.status == "skipped")

    def to_dict(self) -> dict:
        return {
            path: {"status": item.status, "reason": item.reason}
            for path, item in self.items
        }


class CleanupService:
    """Preview / run / retry for the controlled cache population."""

    def __init__(
        self,
        inventory: CacheInventorySource,
        remover: ControlledFileRemover,
        manifest: TrashManifestStore,
    ) -> None:
        self._inventory = inventory
        self._remover = remover
        self._manifest = manifest

    def preview(self) -> CleanupPreview:
        safe = self._safe_targets()
        return CleanupPreview(
            targets=safe, total_bytes=sum(t.size_bytes for t in safe)
        )

    def run(self) -> CleanupOutcome:
        """Remove every safe cache file; idempotent (already-gone files
        report ok). Removal failures are persisted as a pending entry
        before the outcome is returned — retryable, never silent."""
        items: list[tuple[str, CleanupItemResult]] = []
        failed: list[str] = []
        succeeded: list[str] = []
        candidates = dict((t.relative_path, t) for t in self._inventory.list_cache_files())
        for path, _target in sorted(candidates.items()):
            if not is_safe_relative_path(path):
                items.append(
                    (path, CleanupItemResult("skipped", "outside safe cache prefixes"))
                )
                continue
            try:
                self._remover.remove_managed(path)
                items.append((path, CleanupItemResult("ok")))
                succeeded.append(path)
            except OSError as error:
                items.append((path, CleanupItemResult("failed", str(error))))
                failed.append(path)
        # TASK-060 Q-007 ⑤: merge, don't overwrite — a clean run used to
        # pop the whole pending key, silently discarding entries of an
        # earlier run that had never been retried to success.
        self._record_pending(add=failed, remove=succeeded)
        return CleanupOutcome(items=tuple(items))

    def retry_pending_cleanups(self) -> CleanupOutcome:
        """Retry the persisted failure list of the last run (AC 4). The
        same removal semantics apply; cleared entries are dropped, files
        that fail again stay pending."""
        pending = self._pending()
        items: list[tuple[str, CleanupItemResult]] = []
        succeeded: list[str] = []
        for path in pending:
            # TASK-060 Q-007 ④: the retry face re-runs the same predicate
            # — a tampered pending entry must not bypass the whitelist
            # just because it survived a run.
            if not is_safe_relative_path(path):
                items.append(
                    (path, CleanupItemResult("skipped", "outside safe cache prefixes"))
                )
                succeeded.append(path)  # dropped from pending, like the run face
                continue
            try:
                self._remover.remove_managed(path)
                items.append((path, CleanupItemResult("ok")))
                succeeded.append(path)
            except OSError as error:
                items.append((path, CleanupItemResult("failed", str(error))))
        # TASK-060 Q-007 ⑤: merge semantics — only entries this run
        # actually settled leave the pending list; nothing is wiped whole.
        self._record_pending(remove=succeeded)
        return CleanupOutcome(items=tuple(items))

    def pending_cleanup_count(self) -> int:
        return len(self._pending())

    # -- internals ---------------------------------------------------------

    def _safe_targets(self) -> tuple[CleanupTarget, ...]:
        return tuple(
            target
            for target in self._inventory.list_cache_files()
            if is_safe_relative_path(target.relative_path)
        )

    def _pending(self) -> list[str]:
        manifest = self._manifest.read_manifest()
        return list(manifest.get(_PENDING_KEY, []))

    def _record_pending(
        self, *, add: Iterable[str] = (), remove: Iterable[str] = ()
    ) -> None:
        """Merge one face's outcome into the pending list (Q-007 ⑤).

        ``add`` joins the existing entries, ``remove`` drops only the
        entries a face actually settled; an empty result removes the key
        — which under merge semantics now truly means "nothing pending",
        not "discard whatever was there".
        """
        add = [path for path in add if path]
        remove_set = set(remove)
        manifest = self._manifest.read_manifest()
        merged = [
            path
            for path in dict.fromkeys([*manifest.get(_PENDING_KEY, []), *add])
            if path not in remove_set
        ]
        if merged:
            manifest[_PENDING_KEY] = merged
        else:
            manifest.pop(_PENDING_KEY, None)
        self._manifest.write_manifest(manifest)


def is_safe_relative_path(
    relative_path: str, *, prefixes: tuple[str, ...] = CACHE_SAFE_PREFIXES
) -> bool:
    """The single never-clean authority (TASK-060 Q-007).

    Prefix whitelist **after** component checks: a path containing
    ``..`` (or ``.``) components is never safe regardless of its prefix —
    a naive startswith check would let ``cache/webtoon-tiles/../../...``
    escape onto business files inside the managed root (first-review
    R-001).  Every removal face re-uses this one predicate (cache run,
    cache retry, trash pending-purge removal) instead of keeping its own
    guard; ``prefixes`` parameterises the face (the trash face passes an
    empty tuple: business paths are authored by store rows, so only the
    component rule applies there — the root containment stays enforced
    by the remover as the physical backstop).

    The file-system-level half (resolved reparse points, root
    containment) lives with the remover/root owner in
    ``infrastructure.filesystem``; this predicate is the policy half
    every face must pass *before* a removal is even attempted.
    """
    normalized = relative_path.replace("\\", "/")
    parts = PurePosixPath(normalized).parts
    if any(part in ("..", ".") for part in parts):
        return False
    if not prefixes:
        # component-only face (trash): business paths are authored by
        # store rows, so passing the component rule is the whole check
        return True
    return any(normalized.startswith(prefix) for prefix in prefixes)
