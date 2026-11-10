"""FEA-14-EDIT-1 (PREQ EDIT P16-P20): issue markers.

A marker flags a page (whole page) or one relative point on it. The service
validates the book -> chapter -> page ownership chain before writing, keeps the
state machine (``open`` <-> ``resolved``) idempotent, and deletes markers
physically: a marker is user work product, not protected content, so deleting
one only removes the marker row (ADJ-001 does not apply).
"""

from __future__ import annotations

import uuid

from domain.books.entities import utc_now
from domain.editing.entities import IssueMarker, IssueMarkerState


class IssueMarkerError(Exception):
    """Typed EDIT marker failure (wire maps the code to the error envelope)."""

    def __init__(self, code: str, message: str = "") -> None:
        super().__init__(message or code)
        self.code = code


class IssueMarkerService:
    """Issue-marker use cases (PREQ §8 P16-P20, minor 3)."""

    STATES = {IssueMarkerState.OPEN, IssueMarkerState.RESOLVED}
    MAX_KIND = 64
    MAX_NOTE = 2000

    def __init__(self, repository) -> None:
        self._repo = repository

    # ------------------------------------------------------------------
    # P16 list
    # ------------------------------------------------------------------
    def list_markers(self, book_id: str, state: str | None = None) -> list[IssueMarker]:
        resolved_state = self._normalize_state(state)
        if not self._repo.book_exists(book_id):
            raise IssueMarkerError("TARGET_NOT_FOUND", "Book was not found")
        return self._repo.list_markers(book_id, resolved_state)

    # ------------------------------------------------------------------
    # P17 create
    # ------------------------------------------------------------------
    def create_marker(
        self,
        book_id: str,
        chapter_id: str,
        page_id: str,
        kind: str,
        *,
        note: str | None = None,
        position: tuple[float, float] | None = None,
    ) -> IssueMarker:
        for name, value in (("book_id", book_id), ("chapter_id", chapter_id), ("page_id", page_id)):
            if not isinstance(value, str) or not value:
                raise IssueMarkerError("INVALID_REQUEST", f"{name} must be a non-empty string")
        if not isinstance(kind, str) or not kind.strip():
            raise IssueMarkerError("INVALID_REQUEST", "kind must be a non-empty string")
        if len(kind) > self.MAX_KIND:
            raise IssueMarkerError("INVALID_REQUEST", "kind must be at most 64 characters")
        if note is not None and not isinstance(note, str):
            raise IssueMarkerError("INVALID_REQUEST", "note must be a string or null")
        if note is not None and len(note) > self.MAX_NOTE:
            raise IssueMarkerError("INVALID_REQUEST", "note must be at most 2000 characters")
        position_x, position_y = self._normalize_position(position)

        if not self._repo.book_exists(book_id):
            raise IssueMarkerError("TARGET_NOT_FOUND", "Book was not found")
        if self._repo.chapter_book_id(chapter_id) != book_id:
            raise IssueMarkerError("TARGET_NOT_FOUND", "Chapter was not found in the book")
        if self._repo.page_chapter_id(page_id) != chapter_id:
            raise IssueMarkerError("TARGET_NOT_FOUND", "Page was not found in the chapter")

        marker = IssueMarker(
            marker_id=uuid.uuid4().hex,
            book_id=book_id,
            chapter_id=chapter_id,
            page_id=page_id,
            kind=kind,
            note=note,
            position_x=position_x,
            position_y=position_y,
            created_at=utc_now(),
        )
        self._repo.add_marker(marker)
        return marker

    # ------------------------------------------------------------------
    # P18/P19 state machine
    # ------------------------------------------------------------------
    def resolve_marker(self, marker_id: str) -> IssueMarker:
        marker = self._require_marker(marker_id)
        if marker.state is not IssueMarkerState.RESOLVED:
            marker.state = IssueMarkerState.RESOLVED
            marker.resolved_at = utc_now()
            self._repo.update_marker(marker)
        return marker

    def reopen_marker(self, marker_id: str) -> IssueMarker:
        marker = self._require_marker(marker_id)
        if marker.state is not IssueMarkerState.OPEN:
            marker.state = IssueMarkerState.OPEN
            marker.resolved_at = None
            self._repo.update_marker(marker)
        return marker

    # ------------------------------------------------------------------
    # P20 delete (physical; markers are not protected content)
    # ------------------------------------------------------------------
    def delete_marker(self, marker_id: str) -> bool:
        self._require_marker(marker_id)
        self._repo.delete_marker(marker_id)
        return True

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------
    def _require_marker(self, marker_id: str) -> IssueMarker:
        if not isinstance(marker_id, str) or not marker_id:
            raise IssueMarkerError("INVALID_REQUEST", "marker_id must be a non-empty string")
        marker = self._repo.get_marker(marker_id)
        if marker is None:
            raise IssueMarkerError("TARGET_NOT_FOUND", "Marker was not found")
        return marker

    def _normalize_state(self, state: str | None) -> IssueMarkerState | None:
        if state is None:
            return IssueMarkerState.OPEN
        if not isinstance(state, str):
            raise IssueMarkerError("INVALID_REQUEST", "state must be 'open' or 'resolved'")
        try:
            return IssueMarkerState(state)
        except ValueError as error:
            raise IssueMarkerError("INVALID_REQUEST", "state must be 'open' or 'resolved'") from error

    def _normalize_position(self, position) -> tuple[float | None, float | None]:
        if position is None:
            return None, None
        if not isinstance(position, (tuple, list)) or len(position) != 2:
            raise IssueMarkerError("INVALID_REQUEST", "position must be an {x, y} pair")
        for value in position:
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise IssueMarkerError("INVALID_REQUEST", "position coordinates must be numbers")
            if not 0.0 <= float(value) <= 1.0:
                raise IssueMarkerError("INVALID_REQUEST", "position coordinates must be within 0..1")
        return float(position[0]), float(position[1])
