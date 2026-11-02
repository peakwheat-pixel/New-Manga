"""Draft and edit-protection value objects (C-13 SC-D01..SC-D12)."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping


class DraftStatus(str, Enum):
    ACTIVE = "active"
    FLUSHED = "flushed"
    DISCARDED = "discarded"
    CONFLICTED = "conflicted"


@dataclass(frozen=True, order=True)
class DraftSequence:
    """Non-negative monotonic patch sequence, starting at zero."""

    value: int = 0

    def __post_init__(self) -> None:
        if isinstance(self.value, bool) or not isinstance(self.value, int) or self.value < 0:
            raise ValueError("DraftSequence must be a non-negative integer")

    def next(self) -> "DraftSequence":
        return DraftSequence(self.value + 1)


@dataclass
class Draft:
    """The eleven SC-D01 fields. Undo history itself is never persisted."""

    draft_id: str
    session_id: str
    page_id: str
    region_id: str | None
    base_revision_id: str | None
    page_binding_version: int
    draft_sequence: int = 0
    patch: dict[str, Any] = field(default_factory=dict)
    undo_cursor: int = 0
    saved_at: str = field(default_factory=lambda: _utc_now())
    status: DraftStatus = DraftStatus.ACTIVE

    def __post_init__(self) -> None:
        if not self.draft_id or not self.session_id or not self.page_id:
            raise ValueError("DraftId, SessionId and PageId are required")
        if isinstance(self.page_binding_version, bool) or not isinstance(
            self.page_binding_version, int
        ):
            raise ValueError("PageBindingVersion must be an opaque integer")
        if (
            isinstance(self.draft_sequence, bool)
            or not isinstance(self.draft_sequence, int)
            or self.draft_sequence < 0
        ):
            raise ValueError("DraftSequence must be a non-negative integer")
        if (
            isinstance(self.undo_cursor, bool)
            or not isinstance(self.undo_cursor, int)
            or self.undo_cursor < 0
        ):
            raise ValueError("undoCursor must be a non-negative integer")
        if not isinstance(self.patch, dict):
            raise ValueError("patch must be an object")
        self.patch = deepcopy(self.patch)
        if not isinstance(self.status, DraftStatus):
            self.status = DraftStatus(self.status)

    @property
    def sequence(self) -> DraftSequence:
        return DraftSequence(self.draft_sequence)

    def apply_patch(self, patch: Mapping[str, Any], *, undo_cursor: int | None = None) -> None:
        """Apply one serialized patch; geometry/style merge by key, text replaces as a domain."""
        if not isinstance(patch, Mapping):
            raise ValueError("patch must be an object")
        if undo_cursor is not None and (
            isinstance(undo_cursor, bool)
            or not isinstance(undo_cursor, int)
            or undo_cursor < 0
        ):
            raise ValueError("undoCursor must be a non-negative integer")
        incoming = deepcopy(dict(patch))
        current_text = self.patch.get("text")
        incoming_text = incoming.get("text")
        if isinstance(current_text, dict) and isinstance(incoming_text, dict):
            self.patch["text"] = incoming_text
            incoming.pop("text")
        for domain in ("geometry", "style"):
            previous = self.patch.get(domain)
            changed = incoming.get(domain)
            if isinstance(previous, dict) and isinstance(changed, dict):
                merged = dict(previous)
                merged.update(changed)
                self.patch[domain] = merged
                incoming.pop(domain)
        self.patch.update(incoming)
        self.draft_sequence = self.sequence.next().value
        if undo_cursor is not None:
            self.undo_cursor = undo_cursor
        self.saved_at = _utc_now()

    def to_json(self) -> dict[str, Any]:
        """Return exactly the eleven persisted SC-D01 fields."""
        return {
            "DraftId": self.draft_id,
            "SessionId": self.session_id,
            "PageId": self.page_id,
            "RegionId": self.region_id,
            "BaseRevisionId": self.base_revision_id,
            "PageBindingVersion": self.page_binding_version,
            "DraftSequence": self.draft_sequence,
            "patch": deepcopy(self.patch),
            "undoCursor": self.undo_cursor,
            "savedAt": self.saved_at,
            "status": self.status.value,
        }

    @classmethod
    def from_json(cls, data: Mapping[str, Any]) -> "Draft":
        return cls(
            draft_id=data["DraftId"],
            session_id=data["SessionId"],
            page_id=data["PageId"],
            region_id=data.get("RegionId"),
            base_revision_id=data.get("BaseRevisionId"),
            page_binding_version=data["PageBindingVersion"],
            draft_sequence=data["DraftSequence"],
            patch=data.get("patch", {}),
            undo_cursor=data.get("undoCursor", 0),
            saved_at=data["savedAt"],
            status=DraftStatus(data["status"]),
        )


@dataclass(frozen=True)
class EditToken:
    token_id: str
    draft_id: str
    draft_sequence: int
    session_id: str
    issued_at: str
    expires_at: str

    def is_expired(self, now: datetime | None = None) -> bool:
        current = now or datetime.now(timezone.utc)
        expires = datetime.fromisoformat(self.expires_at.replace("Z", "+00:00"))
        return current >= expires

    def to_json(self) -> dict[str, Any]:
        return {
            "tokenId": self.token_id,
            "DraftId": self.draft_id,
            "DraftSequence": self.draft_sequence,
            "SessionId": self.session_id,
            "issuedAt": self.issued_at,
            "expiresAt": self.expires_at,
        }


@dataclass(frozen=True)
class RegionCandidate:
    candidate_id: str
    region_id: str
    base_revision_id: str
    origin: str

    def to_json(self) -> dict[str, str]:
        return {
            "candidateId": self.candidate_id,
            "RegionId": self.region_id,
            "BaseRevisionId": self.base_revision_id,
            "origin": self.origin,
        }


@dataclass(frozen=True)
class DraftLease:
    draft: Draft
    can_edit: bool
    token: EditToken | None


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")
