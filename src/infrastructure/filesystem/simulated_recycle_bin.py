"""Simulated original-file recycle bin — D-flow **test double only**.

This module lets the flow-D port
(:class:`application.maintenance.recycle_gateway.OriginalFileRecycleGateway`)
be exercised end to end without any real Windows recycle-bin call: it moves
files and folders inside an **isolated scratch root** only, records an
auditable manifest plus a journal, and never deletes anything permanently.
Production must never construct it — the production default is
:class:`application.maintenance.recycle_gateway.UnavailableOriginalFileRecycleGateway`.

Safety rules enforced structurally, not by convention:

- the configured root must already exist, must be an ordinary directory, must
  not be a filesystem root, must not be (or be reached through) a
  junction/symlink, and must not be the real Windows recycle-bin folder;
- every source path must resolve inside that root: relative paths, ``..``/
  ``.``/empty path components, paths escaping the root, and any junction or
  symlink on the walk are typed ``failed`` items with **zero** filesystem
  effect;
- the gateway's **own** write targets (the simulated bin directory, the
  manifest and the journal) are validated at construction and again before
  every write/read: they must resolve inside the caller's root, must not
  cross a junction/symlink, and an existing manifest/journal file must not be
  hard-linked outside — otherwise a typed :class:`RecycleSafetyError` is
  raised with zero writes;
- the move is ``os.replace`` inside the same root (same volume, atomic per
  item) and is verified afterwards by kind/size/SHA-256; a verification
  failure rolls the item back and reports ``failed`` — ``failed`` always means
  the original file is still in place, otherwise
  :class:`RecycleSafetyError` is raised instead;
- the only mutating calls are ``os.replace`` and the manifest/journal writes,
  all inside the isolated root.  No recycle-bin API, no process spawn, no
  database, no unlink/rmtree: deleting an original is never a fallback here.

Residual risk (why this is still **test infrastructure**, not a hardened
production adapter): the write-target checks and the writes are separate
filesystem calls, so a concurrent re-plant is a TOCTOU window; the slice is
single-writer by construction.  The real OS bridge must bind handles and keep
the SSD/journal single-writer discipline.  The AC2 wording is limited
accordingly (see Task card / `verification/FEA-12-DSIM-1/ISOLATION-EVIDENCE.md`).

The manifest (``simulated-recyclebin/recyclebin-manifest.json``) is the audit
catalogue of what the simulated bin holds; the journal
(``recyclebin-journal.jsonl``, append-only) records the attempt **before** any
move and the receipt after verification (C-01b SC-34).  Crash recovery is not
implemented in this slice (the journal shape is the seam); the real OS bridge
is a separately authorised Host-side task and remains ``NOT_RUN``.
"""

from __future__ import annotations

import hashlib
import json
import os
import stat
import uuid
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

from application.maintenance.recycle_gateway import (
    REASON_ACCESS_DENIED,
    REASON_ALREADY_IN_BIN,
    REASON_IN_USE,
    REASON_INVALID_REQUEST,
    REASON_OUTSIDE_ISOLATED_ROOT,
    REASON_PATH_NOT_FOUND,
    REASON_RECYCLE_REJECTED,
    REASON_UNSUPPORTED_ENTRY,
    REASON_VERIFY_FAILED,
    STATUS_FAILED,
    STATUS_MOVED,
    RecycleAttempt,
    RecycleEntry,
    RecycleItemOutcome,
    RecycleJournal,
    RecycleOutcome,
    RecycleReceipt,
    RecycleSafetyError,
    utc_now,
)

GATEWAY_NAME = "simulated"
#: Subdirectory of the isolated root that stands in for the recycle bin.
BIN_DIR_NAME = "simulated-recyclebin"
MANIFEST_NAME = "recyclebin-manifest.json"
JOURNAL_NAME = "recyclebin-journal.jsonl"
MANIFEST_FORMAT = "simulated-recycle-bin/1"

_CHUNK = 1024 * 1024


class UnsafeIsolatedRootError(ValueError):
    """The configured root is not an isolated scratch root (construction
    refusal: the simulated bin must never be pointed at real user data, a
    filesystem root or the real recycle bin)."""


class _ItemFailure(Exception):
    """Internal: per-item refusal carrying a typed reason."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


class _UnsupportedEntry(Exception):
    """Internal: the selected object is not a plain file/folder."""


@dataclass(frozen=True)
class RecycleBinEntry:
    """One catalogue row of the simulated bin (manifest-backed audit view)."""

    request_id: str
    original_path: str
    stored_path: str
    kind: str
    size_bytes: int
    sha256: str
    moved_at: str

    def to_dict(self) -> dict:
        return {
            "request_id": self.request_id,
            "original_path": self.original_path,
            "stored_path": self.stored_path,
            "kind": self.kind,
            "size_bytes": self.size_bytes,
            "sha256": self.sha256,
            "moved_at": self.moved_at,
        }


# ---------------------------------------------------------------------------
# Safety helpers
# ---------------------------------------------------------------------------


def _is_reparse_point(st: os.stat_result) -> bool:
    """Junction/symlink detection that works on both Windows and POSIX."""
    attributes = getattr(st, "st_file_attributes", 0)
    if attributes:
        return bool(attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)
    return stat.S_ISLNK(st.st_mode)


def _assert_isolated_root(root: Path) -> Path:
    """Validate the scratch root once, at construction (no writes)."""
    resolved = Path(os.path.abspath(str(root)))
    if resolved.parent == resolved:
        raise UnsafeIsolatedRootError(
            "filesystem root is not an isolated scratch root"
        )
    if not resolved.exists():
        raise UnsafeIsolatedRootError(
            "the isolated scratch root must already exist"
        )
    if not resolved.is_dir():
        raise UnsafeIsolatedRootError(
            "the isolated scratch root must be a directory"
        )
    if any(
        part.lower().endswith("recycle.bin") for part in resolved.parts
    ):
        raise UnsafeIsolatedRootError(
            "the real Windows recycle-bin folder is not an isolated scratch root"
        )
    # R-001: a root reached through a junction/symlink would move the write
    # containment baseline; refuse it instead of silently writing elsewhere.
    _assert_plain_component_walk(
        resolved, UnsafeIsolatedRootError, "isolated scratch root"
    )
    return resolved


def _assert_plain_component_walk(
    path: Path, error_type: type[Exception], what: str
) -> None:
    """Every existing component of ``path`` must be a plain entry (no reparse).

    Walks from the filesystem anchor down; a junction/symlink anywhere on the
    path means the lexical and the real path disagree, which is exactly the
    condition a containment check must refuse rather than resolve.
    """
    absolute = Path(os.path.abspath(str(path)))
    probe = Path(absolute.anchor)
    for part in absolute.parts[1:]:
        probe = probe / part
        try:
            probe_stat = probe.lstat()
        except OSError:
            break  # nothing there to traverse through
        if _is_reparse_point(probe_stat):
            raise error_type(f"{what} must not cross a junction/symlink: {probe}")


def _assert_write_target(
    root: Path, target: Path, what: str, *, expect_dir: bool = False
) -> None:
    """R-001: a gateway-owned write target must stay inside the caller root.

    Called at construction **and before every write/read** of the simulated
    bin's own paths (bin directory, manifest, journal): a junction or hard
    link pre-planted in the scratch root would otherwise redirect a manifest
    or journal write — or the recycle move itself — outside the isolated root.
    Anything suspicious is a typed ``RecycleSafetyError`` with zero writes.

    Residual risk (documented, not fixed): the check and the write are
    separate filesystem calls, so a concurrent re-plant is a TOCTOU window;
    the simulated slice is single-writer test infrastructure, the real OS
    bridge must bind handles (see module docstring).
    """
    root_absolute = Path(os.path.abspath(str(root)))
    target_absolute = Path(os.path.abspath(str(target)))
    try:
        relative = target_absolute.relative_to(root_absolute)
    except ValueError:
        raise RecycleSafetyError(
            f"{what} escapes the isolated root"
        ) from None
    probe = root_absolute
    for segment in relative.parts:
        probe = probe / segment
        try:
            probe_stat = probe.lstat()
        except OSError:
            break  # nothing there yet
        if _is_reparse_point(probe_stat):
            raise RecycleSafetyError(
                f"{what} crosses a junction/symlink: {probe}"
            )
    resolved_root = Path(os.path.realpath(str(root)))
    resolved_target = Path(os.path.realpath(str(target)))
    if not _is_within(resolved_target, resolved_root):
        raise RecycleSafetyError(
            f"{what} resolves outside the isolated root"
        )
    try:
        target_stat = target_absolute.lstat()
    except OSError:
        return  # does not exist yet: containment/reparse checks are enough
    if expect_dir:
        if not stat.S_ISDIR(target_stat.st_mode):
            raise RecycleSafetyError(
                f"{what} is not a plain directory inside the isolated root"
            )
        return
    if not stat.S_ISREG(target_stat.st_mode):
        raise RecycleSafetyError(
            f"{what} is not a plain file inside the isolated root"
        )
    if target_stat.st_nlink > 1:
        # a pre-planted hard link would make an append write a file the
        # gateway does not own (and that lives outside the root)
        raise RecycleSafetyError(
            f"{what} is hard-linked outside the isolated root"
        )


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(_CHUNK)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _fingerprint(path: Path) -> tuple[str, int, str]:
    """``(kind, size_bytes, sha256)`` for one selected object.

    Directories are fingerprinted recursively (relative path + size + digest
    per file, sorted), so a folder entry is verified as one unit too.  The
    walk never follows a junction/symlink: a selected folder containing one
    is refused as ``unsupported_entry`` instead of being read (and later
    moved) as if the reparse point were ordinary content.
    """
    entry_stat = path.lstat()
    if _is_reparse_point(entry_stat):
        raise _UnsupportedEntry
    if stat.S_ISREG(entry_stat.st_mode):
        return ("file", entry_stat.st_size, _sha256_file(path))
    if not stat.S_ISDIR(entry_stat.st_mode):
        raise _UnsupportedEntry
    digest = hashlib.sha256()
    total = 0
    for current, dirnames, filenames in os.walk(path, followlinks=False):
        current_path = Path(current)
        dirnames.sort()
        filenames.sort()
        for name in dirnames:
            child = current_path / name
            if _is_reparse_point(child.lstat()):
                raise _UnsupportedEntry
            digest.update(
                f"{child.relative_to(path).as_posix()}/\n".encode("utf-8")
            )
        for name in filenames:
            child = current_path / name
            child_stat = child.lstat()
            if _is_reparse_point(child_stat) or not stat.S_ISREG(
                child_stat.st_mode
            ):
                raise _UnsupportedEntry
            digest.update(
                (
                    f"{child.relative_to(path).as_posix()}\0"
                    f"{child_stat.st_size}\0{_sha256_file(child)}\n"
                ).encode("utf-8")
            )
            total += child_stat.st_size
    return ("directory", total, digest.hexdigest())


def _reason_for_oserror(error: OSError) -> str:
    """Map a move refusal onto the typed vocabulary (never free-form)."""
    winerror = getattr(error, "winerror", None)
    if winerror in (32, 33):
        return REASON_IN_USE
    if winerror == 5:
        return REASON_ACCESS_DENIED
    if error.errno in (13, 16):  # EACCES / EBUSY
        return REASON_ACCESS_DENIED if error.errno == 13 else REASON_IN_USE
    return REASON_RECYCLE_REJECTED


def _path_key(path: Path) -> str:
    """Normalised absolute key: case-insensitive on Windows, exact on POSIX."""
    return os.path.normcase(os.path.abspath(str(path)))


def _same_path(left: Path, right: Path) -> bool:
    return _path_key(left) == _path_key(right)


def _is_within(path: Path, root: Path) -> bool:
    """True when ``path`` is ``root`` or lives below it (normalised)."""
    path_key = _path_key(path)
    root_key = _path_key(root)
    return path_key == root_key or path_key.startswith(
        root_key + os.sep
    )


# ---------------------------------------------------------------------------
# Simulated bin
# ---------------------------------------------------------------------------


class SimulatedRecycleBin:
    """Recycle-bin gateway double that only ever moves inside one isolated
    root.  Structural implementation of ``OriginalFileRecycleGateway``."""

    gateway = GATEWAY_NAME

    def __init__(
        self,
        isolated_root: str | Path,
        *,
        failure_injector: Callable[[RecycleEntry], str | None] | None = None,
        clock: Callable[[], str] | None = None,
    ) -> None:
        self._root = _assert_isolated_root(Path(isolated_root))
        self._bin_dir = self._root / BIN_DIR_NAME
        self._manifest_path = self._bin_dir / MANIFEST_NAME
        self._failure_injector = failure_injector
        self._clock = clock or utc_now
        # R-001: the gateway's *own* write targets are validated too — a
        # junction/hard link pre-planted in the caller's scratch root must be
        # refused at construction, not silently followed by the first move.
        self._assert_write_targets()

    # -- read faces (tests / audit) ----------------------------------------

    @property
    def root(self) -> Path:
        return self._root

    @property
    def bin_dir(self) -> Path:
        return self._bin_dir

    @property
    def manifest_path(self) -> Path:
        return self._manifest_path

    def _assert_write_targets(self) -> None:
        """R-001: validate every gateway-owned write/read target.

        Re-run before each write/read (not just at construction) so a target
        re-planted between operations is still refused.  A typed
        ``RecycleSafetyError`` means zero filesystem writes were performed for
        the operation.
        """
        _assert_write_target(
            self._root, self._bin_dir, "simulated bin directory", expect_dir=True
        )
        _assert_write_target(
            self._root, self._manifest_path, "simulated bin manifest"
        )
        _assert_write_target(
            self._root, self._root / JOURNAL_NAME, "simulated bin journal"
        )

    def read_manifest(self) -> dict:
        """The raw manifest (``{"format": ..., "entries": [...]}``)."""
        self._assert_write_targets()
        if not self._manifest_path.is_file():
            return {"format": MANIFEST_FORMAT, "entries": []}
        try:
            manifest = json.loads(
                self._manifest_path.read_text(encoding="utf-8")
            )
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
            raise ValueError(
                f"simulated recycle-bin manifest is unreadable: {error}"
            ) from error
        if (
            not isinstance(manifest, dict)
            or manifest.get("format") != MANIFEST_FORMAT
            or not isinstance(manifest.get("entries"), list)
        ):
            raise ValueError("simulated recycle-bin manifest is malformed")
        return manifest

    def list_entries(self) -> tuple[RecycleBinEntry, ...]:
        return tuple(
            RecycleBinEntry(
                request_id=item["request_id"],
                original_path=item["original_path"],
                stored_path=item["stored_path"],
                kind=item["kind"],
                size_bytes=int(item["size_bytes"]),
                sha256=item["sha256"],
                moved_at=item["moved_at"],
            )
            for item in self.read_manifest()["entries"]
        )

    # -- OriginalFileRecycleGateway ---------------------------------------

    def move_to_recyclebin(
        self, entries: Sequence[RecycleEntry],
        *, journal: RecycleJournal,
    ) -> RecycleOutcome:
        """Move each selected item into the simulated bin, one typed result
        per item.  The attempt is journalled before the first move and the
        receipt after the last verification."""
        operation_id = uuid.uuid4().hex
        requested = tuple(entries)
        journal.record_attempt(
            RecycleAttempt(
                operation_id=operation_id,
                requested_at=self._clock(),
                entries=tuple(
                    (entry.request_id, entry.path) for entry in requested
                ),
            )
        )
        items = tuple(self._recycle_one(entry) for entry in requested)
        outcome = RecycleOutcome(
            gateway=GATEWAY_NAME, items=items, operation_id=operation_id
        )
        journal.record_receipt(
            RecycleReceipt(
                operation_id=operation_id,
                completed_at=self._clock(),
                gateway=GATEWAY_NAME,
                items=outcome.items,
            )
        )
        return outcome

    # -- internals ---------------------------------------------------------

    def _recycle_one(self, entry: RecycleEntry) -> RecycleItemOutcome:
        # Failure injection runs first: an injected refusal is exactly the
        # "OS refused / object in use / volume not recyclable" case and must
        # leave the original untouched (zero filesystem calls for the item).
        if self._failure_injector is not None:
            injected = self._failure_injector(entry)
            if injected:
                return _failed(entry, injected)
        try:
            source = self._confine(entry.path)
        except _ItemFailure as refusal:
            return _failed(entry, refusal.reason)
        if _same_path(source, self._root):
            return _failed(entry, REASON_INVALID_REQUEST)
        if _is_within(source, self._bin_dir):
            return _failed(entry, REASON_ALREADY_IN_BIN)
        if not source.exists():
            return _failed(entry, REASON_PATH_NOT_FOUND)
        try:
            kind, size_bytes, digest = _fingerprint(source)
        except _UnsupportedEntry:
            return _failed(entry, REASON_UNSUPPORTED_ENTRY)
        except FileNotFoundError:
            return _failed(entry, REASON_PATH_NOT_FOUND)
        except OSError:
            return _failed(entry, REASON_ACCESS_DENIED)
        # R-001: re-check the gateway's own targets right before the move.
        self._assert_write_targets()
        try:
            self._bin_dir.mkdir(parents=True, exist_ok=True)
        except OSError:
            # The bin lives inside the isolated root; if it cannot be created
            # the environment is broken, not the user's file: surface it.
            raise
        # A freshly created bin is plain; this also catches a pre-planted one
        # that appeared between the two checks (still a narrow TOCTOU window).
        self._assert_write_targets()
        stored = self._bin_dir / f"{uuid.uuid4().hex[:8]}-{source.name}"
        try:
            os.replace(str(source), str(stored))
        except OSError as error:
            return _failed(entry, _reason_for_oserror(error))
        if not self._verify_moved(source, stored, kind, size_bytes, digest):
            self._rollback(stored, source)
            return _failed(entry, REASON_VERIFY_FAILED)
        self._append_manifest_entry(
            RecycleBinEntry(
                request_id=entry.request_id,
                original_path=str(source),
                stored_path=str(stored),
                kind=kind,
                size_bytes=size_bytes,
                sha256=digest,
                moved_at=self._clock(),
            )
        )
        return RecycleItemOutcome(entry.request_id, STATUS_MOVED)

    def _confine(self, raw: str) -> Path:
        """Resolve one selected path and prove it stays inside the root.

        Same guard order as ``ManagedFileStorage.remove_managed``: lexical
        components first, then containment against the **non-resolving** root
        baseline (a link above the root moves the candidate out of it), then a
        reparse-point walk over the unresolved path.  Anything refused is a
        typed ``failed`` item with zero filesystem effect.
        """
        path = Path(raw)
        if not path.is_absolute():
            raise _ItemFailure(REASON_INVALID_REQUEST)
        segments = raw.replace("\\", "/").split("/")
        if any(segment in ("", ".", "..") for segment in segments[1:]):
            raise _ItemFailure(REASON_OUTSIDE_ISOLATED_ROOT)
        baseline = Path(os.path.abspath(str(self._root)))
        absolute = Path(os.path.abspath(raw))
        try:
            relative = absolute.relative_to(baseline)
        except ValueError:
            raise _ItemFailure(REASON_OUTSIDE_ISOLATED_ROOT) from None
        probe = self._root
        for segment in relative.parts:
            probe = probe / segment
            try:
                probe_stat = probe.lstat()
            except OSError:
                break  # nothing there to traverse through
            if _is_reparse_point(probe_stat):
                raise _ItemFailure(REASON_OUTSIDE_ISOLATED_ROOT)
        candidate = absolute.resolve()
        try:
            candidate.relative_to(baseline)
        except ValueError:
            raise _ItemFailure(REASON_OUTSIDE_ISOLATED_ROOT) from None
        return candidate

    @staticmethod
    def _verify_moved(
        source: Path,
        stored: Path,
        kind: str,
        size_bytes: int,
        digest: str,
    ) -> bool:
        """Re-read the moved object: same identity, original path now gone."""
        try:
            if source.exists():
                return False
            return _fingerprint(stored) == (kind, size_bytes, digest)
        except (_UnsupportedEntry, OSError):
            return False

    @staticmethod
    def _rollback(stored: Path, source: Path) -> None:
        """Put a not-verified item back.  ``failed`` must mean "original still
        in place"; if that cannot be restored we raise instead of lying."""
        if source.exists() or not stored.exists():
            raise RecycleSafetyError(
                "cannot restore a failed recycle item to its original path"
            )
        try:
            os.replace(str(stored), str(source))
        except OSError as error:
            raise RecycleSafetyError(
                "cannot restore a failed recycle item to its original path"
            ) from error

    def _append_manifest_entry(self, entry: RecycleBinEntry) -> None:
        manifest = self.read_manifest()
        manifest["entries"].append(entry.to_dict())
        self._write_manifest(manifest)

    def _write_manifest(self, manifest: dict) -> None:
        """Atomic manifest swap (temp file + ``os.replace``).

        Deliberately no cleanup branch: the D-flow slice contains **no**
        delete call of any kind, not even for its own scratch files — the
        isolated root is disposable, so a failed write may leave a temp file
        behind while the previous manifest stays intact.

        R-001: targets are re-validated immediately before the write so a
        manifest/bin path re-planted after construction is refused.
        """
        self._assert_write_targets()
        self._bin_dir.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(manifest, ensure_ascii=False, indent=2)
        temp_path = self._manifest_path.with_name(
            f".{MANIFEST_NAME}.tmp-{uuid.uuid4().hex}"
        )
        with open(temp_path, "w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, self._manifest_path)


def _failed(entry: RecycleEntry, reason: str) -> RecycleItemOutcome:
    return RecycleItemOutcome(entry.request_id, STATUS_FAILED, reason)


class JsonLinesRecycleJournal:
    """Append-only JSONL journal for the simulated bridge (SC-34 shape).

    Lives inside the same isolated root as the simulated bin; appends and
    fsyncs one line per record so the attempt record is durable before any
    move.  Single-writer by design (test double).
    """

    def __init__(self, isolated_root: str | Path) -> None:
        self._root = _assert_isolated_root(Path(isolated_root))
        self._path = self._root / JOURNAL_NAME
        # R-001: a pre-planted hard link/symlink would make every append write
        # a file outside the isolated root; refuse at construction.
        self._assert_safe()

    @property
    def path(self) -> Path:
        return self._path

    def _assert_safe(self) -> None:
        _assert_write_target(self._root, self._path, "simulated bin journal")

    def record_attempt(self, attempt: RecycleAttempt) -> None:
        self._append({"record_type": "attempt", **attempt.to_dict()})

    def record_receipt(self, receipt: RecycleReceipt) -> None:
        self._append({"record_type": "receipt", **receipt.to_dict()})

    def read_records(self) -> tuple[dict, ...]:
        self._assert_safe()
        if not self._path.is_file():
            return ()
        records: list[dict] = []
        for line in self._path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            records.append(json.loads(line))
        return tuple(records)

    def _append(self, record: dict) -> None:
        # Re-check before every append (R-001): a journal path re-planted
        # between construction and the write must not be followed.
        self._assert_safe()
        line = json.dumps(record, ensure_ascii=False)
        with open(self._path, "a", encoding="utf-8", newline="\n") as handle:
            handle.write(line + "\n")
            handle.flush()
            os.fsync(handle.fileno())


__all__ = [
    "BIN_DIR_NAME",
    "GATEWAY_NAME",
    "JOURNAL_NAME",
    "JsonLinesRecycleJournal",
    "MANIFEST_FORMAT",
    "MANIFEST_NAME",
    "RecycleBinEntry",
    "SimulatedRecycleBin",
    "UnsafeIsolatedRootError",
]
