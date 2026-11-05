"""D-flow port: the independent original-file delete (recycle bin) gateway.

ADJ-001 §3 separates deletion into four flows.  A (soft delete), B (retention
cleanup) and C (explicit permanent delete) never touch a user's original
files; deleting an original file is flow **D**, a separately authorised flow:
the Host lists the exact files, the user confirms, the Host-side Windows
recycle-bin bridge performs the move, and every item is verified afterwards.
Unrecyclable, in-use, network-drive or replaced paths are **kept and
reported**, never degraded to a permanent delete
(AD-003 §3.7; C-09 SC-B05; C-01b SC-31).

This module is the application-layer port for flow D plus the fail-closed
production default.  It contains **no** Windows bridge: the real bridge is a
separately authorised Host-side task and is ``NOT_RUN`` here.  The D-flow
simulation slice (``SimulatedRecycleBin``) lives in
``infrastructure.filesystem.simulated_recycle_bin``, writes only inside an
isolated scratch root and is test infrastructure, not a production adapter.

Typed per-item result — exactly one of:

``moved``
    The bridge moved the item to the recycle bin and verified it.
``failed``
    The item was **not** recycled; its original file is still in place.
    This layer never retries a failed item as a permanent delete.
``not_started``
    The item was never attempted (batch-level refusal such as an unavailable
    gateway).  ``not_started`` is not success.

The keyword-only ``journal`` is the SC-34 seam: an OS delete and the database
have no distributed transaction, so the attempt and its receipt are recorded
first and crash recovery compares the journal against the OS facts before
resending.  The gateway records the attempt **before** any filesystem change
and the receipt after verification; a caller that only needs the typed
outcome still has to supply the journal, so a future production adapter
cannot silently skip the audit trail.

Nothing here touches the filesystem, a database or a process: this module is
pure application-layer types and the fail-closed default.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal, Protocol, runtime_checkable

#: Per-item outcome vocabulary (closed set; never free-form text).
STATUS_MOVED = "moved"
STATUS_FAILED = "failed"
STATUS_NOT_STARTED = "not_started"

RecycleItemStatus = Literal["moved", "failed", "not_started"]

#: Typed failure reasons (closed set; a gateway must not invent new codes
#: without extending this vocabulary in the same change).
REASON_GATEWAY_UNAVAILABLE = "gateway_unavailable"
REASON_INVALID_REQUEST = "invalid_request"
REASON_OUTSIDE_ISOLATED_ROOT = "outside_isolated_root"
REASON_PATH_NOT_FOUND = "path_not_found"
REASON_UNSUPPORTED_ENTRY = "unsupported_entry"
REASON_ALREADY_IN_BIN = "already_in_bin"
REASON_IN_USE = "in_use"
REASON_ACCESS_DENIED = "access_denied"
REASON_RECYCLE_REJECTED = "recycle_rejected"
REASON_VERIFY_FAILED = "verify_failed"

ITEM_STATUSES: frozenset[str] = frozenset(
    {STATUS_MOVED, STATUS_FAILED, STATUS_NOT_STARTED}
)
FAILURE_REASONS: frozenset[str] = frozenset(
    {
        REASON_GATEWAY_UNAVAILABLE,
        REASON_INVALID_REQUEST,
        REASON_OUTSIDE_ISOLATED_ROOT,
        REASON_PATH_NOT_FOUND,
        REASON_UNSUPPORTED_ENTRY,
        REASON_ALREADY_IN_BIN,
        REASON_IN_USE,
        REASON_ACCESS_DENIED,
        REASON_RECYCLE_REJECTED,
        REASON_VERIFY_FAILED,
    }
)


def utc_now() -> str:
    """Journal timestamp (UTC, microseconds) — one format everywhere."""
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


class RecycleSafetyError(RuntimeError):
    """Raised when a failed item's original file can no longer be proven to
    be in place.

    ``failed`` is only allowed to mean "the original file is still there".
    A bridge that moved an item and then cannot roll it back must raise this
    instead of returning a typed failure: the caller must never mistake an
    unknown location for a preserved file (and must never compensate with a
    permanent delete).
    """


@dataclass(frozen=True)
class RecycleEntry:
    """One exact file/folder the user explicitly selected (C-01b SC-31).

    ``request_id`` is the caller's stable opaque id used by the journal and
    the receipt; ``path`` is the exact path the user selected.  The flow never
    expands folders, guesses siblings or feeds the path to any other flow.
    """

    request_id: str
    path: str

    def __post_init__(self) -> None:
        if not isinstance(self.request_id, str) or not self.request_id:
            raise ValueError("request_id must be a non-empty string")
        if not isinstance(self.path, str) or not self.path:
            raise ValueError("path must be a non-empty string")


@dataclass(frozen=True)
class RecycleItemOutcome:
    """Typed result of one requested item (no path, no plaintext: M2-C1
    §5.11.5-style safe projection is what ``to_dict`` returns)."""

    request_id: str
    status: RecycleItemStatus
    reason: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.request_id, str) or not self.request_id:
            raise ValueError("request_id must be a non-empty string")
        if self.status not in ITEM_STATUSES:
            raise ValueError(f"unknown recycle item status: {self.status!r}")
        if self.status == STATUS_MOVED:
            if self.reason:
                raise ValueError("a moved item must not carry a failure reason")
            return
        if self.reason not in FAILURE_REASONS:
            raise ValueError(
                f"unknown recycle failure reason: {self.reason!r}"
            )

    def to_dict(self) -> dict:
        return {
            "request_id": self.request_id,
            "status": self.status,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class RecycleOutcome:
    """Typed result of one D-flow attempt (per item, never a bare boolean)."""

    gateway: str
    items: tuple[RecycleItemOutcome, ...]
    operation_id: str = ""

    @property
    def moved(self) -> int:
        return sum(1 for item in self.items if item.status == STATUS_MOVED)

    @property
    def failed(self) -> int:
        return sum(1 for item in self.items if item.status == STATUS_FAILED)

    @property
    def not_started(self) -> int:
        return sum(1 for item in self.items if item.status == STATUS_NOT_STARTED)

    @property
    def complete(self) -> bool:
        """True only when a non-empty request was moved in full."""
        return bool(self.items) and self.moved == len(self.items)

    @property
    def has_failures(self) -> bool:
        return bool(self.failed or self.not_started)

    def to_dict(self) -> dict:
        """Safe projection: counts + per-item status/reason, never a path."""
        return {
            "gateway": self.gateway,
            "operation_id": self.operation_id,
            "moved": self.moved,
            "failed": self.failed,
            "not_started": self.not_started,
            "items": [item.to_dict() for item in self.items],
        }


@dataclass(frozen=True)
class RecycleAttempt:
    """Journal step 1 (SC-34): what the bridge is about to attempt.

    The journal keeps the exact paths — it is the local audit/recovery seam
    and is never projected to the UI (the safe projection is
    :meth:`RecycleOutcome.to_dict`).
    """

    operation_id: str
    requested_at: str
    entries: tuple[tuple[str, str], ...]

    def to_dict(self) -> dict:
        return {
            "operation_id": self.operation_id,
            "requested_at": self.requested_at,
            "entries": [
                {"request_id": request_id, "path": path}
                for request_id, path in self.entries
            ],
        }


@dataclass(frozen=True)
class RecycleReceipt:
    """Journal step 2 (SC-34): the verified result of one attempt."""

    operation_id: str
    completed_at: str
    gateway: str
    items: tuple[RecycleItemOutcome, ...]

    def to_dict(self) -> dict:
        return {
            "operation_id": self.operation_id,
            "completed_at": self.completed_at,
            "gateway": self.gateway,
            "items": [item.to_dict() for item in self.items],
        }


@runtime_checkable
class RecycleJournal(Protocol):
    """Durable attempt/receipt journal (SC-34).  Implementations live with
    the bridge; the simulated slice appends JSON lines inside its isolated
    root.  Recording must happen before the filesystem change
    (``record_attempt``) and after verification (``record_receipt``)."""

    def record_attempt(self, attempt: RecycleAttempt) -> None: ...

    def record_receipt(self, receipt: RecycleReceipt) -> None: ...


@runtime_checkable
class OriginalFileRecycleGateway(Protocol):
    """Flow-D port: move the user's selected original files to the recycle
    bin, one typed outcome per item.

    Contract:

    - ``entries`` are exact, already-confirmed selections; the port never
      expands a folder or derives sibling paths;
    - a ``failed`` item keeps its original file — never a permanent delete;
    - ``journal`` is mandatory so every OS-level attempt has an audit trail;
    - no Host/UI production wiring is part of this slice.
    """

    def move_to_recyclebin(
        self, entries: Sequence[RecycleEntry], *, journal: RecycleJournal
    ) -> RecycleOutcome: ...


class UnavailableOriginalFileRecycleGateway:
    """Fail-closed production default: typed unavailable, zero operations.

    The real Windows recycle-bin bridge is a separately authorised Host-side
    task; until it exists every production call lands here.  The gateway never
    writes the journal, never touches the filesystem and never degrades to a
    permanent delete: every entry is reported ``not_started`` with
    ``gateway_unavailable``, so no caller can mistake the result for success
    and nothing is ever deleted as a fallback.
    """

    gateway = "unavailable"

    def move_to_recyclebin(
        self, entries: Sequence[RecycleEntry], *, journal: RecycleJournal
    ) -> RecycleOutcome:
        items = tuple(
            RecycleItemOutcome(
                entry.request_id, STATUS_NOT_STARTED, REASON_GATEWAY_UNAVAILABLE
            )
            for entry in entries
        )
        # No operation id: nothing was attempted, nothing was journalled.
        return RecycleOutcome(gateway=self.gateway, items=items, operation_id="")


__all__ = [
    "FAILURE_REASONS",
    "ITEM_STATUSES",
    "OriginalFileRecycleGateway",
    "REASON_ACCESS_DENIED",
    "REASON_ALREADY_IN_BIN",
    "REASON_GATEWAY_UNAVAILABLE",
    "REASON_INVALID_REQUEST",
    "REASON_IN_USE",
    "REASON_OUTSIDE_ISOLATED_ROOT",
    "REASON_PATH_NOT_FOUND",
    "REASON_RECYCLE_REJECTED",
    "REASON_UNSUPPORTED_ENTRY",
    "REASON_VERIFY_FAILED",
    "RecycleAttempt",
    "RecycleEntry",
    "RecycleItemOutcome",
    "RecycleItemStatus",
    "RecycleJournal",
    "RecycleOutcome",
    "RecycleReceipt",
    "RecycleSafetyError",
    "STATUS_FAILED",
    "STATUS_MOVED",
    "STATUS_NOT_STARTED",
    "UnavailableOriginalFileRecycleGateway",
    "utc_now",
]
