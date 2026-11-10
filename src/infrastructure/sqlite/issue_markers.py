"""SQLite persistence for issue markers (FEA-14-EDIT-1, schema v13).

Implements the application-layer marker repository protocol. Ownership checks
are plain existence reads over the frozen v1 books/chapters/pages tables; the
marker table itself is additive (v13) and never writes through those tables.
"""

from __future__ import annotations

from domain.editing.entities import IssueMarker, IssueMarkerState

_COLUMNS = (
    "marker_id, book_id, chapter_id, page_id, position_x, position_y,"
    " kind, note, state, created_at, resolved_at"
)


class SqliteIssueMarkerStore:
    """Repository for ``issue_markers`` rows (schema v13)."""

    def __init__(self, conn) -> None:
        self._conn = conn

    # ------------------------------------------------------------------
    # marker rows
    # ------------------------------------------------------------------
    def add_marker(self, marker: IssueMarker) -> None:
        with self._conn:
            self._conn.execute(
                "INSERT INTO issue_markers"
                f" ({_COLUMNS}) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    marker.marker_id,
                    marker.book_id,
                    marker.chapter_id,
                    marker.page_id,
                    marker.position_x,
                    marker.position_y,
                    marker.kind,
                    marker.note,
                    marker.state.value,
                    marker.created_at,
                    marker.resolved_at,
                ),
            )

    def get_marker(self, marker_id: str) -> IssueMarker | None:
        row = self._conn.execute(
            "SELECT " + _COLUMNS + " FROM issue_markers WHERE marker_id = ?", (marker_id,)
        ).fetchone()
        return None if row is None else _marker_from_row(row)

    def list_markers(self, book_id: str, state: IssueMarkerState | None) -> list[IssueMarker]:
        if state is None:
            rows = self._conn.execute(
                "SELECT " + _COLUMNS + " FROM issue_markers WHERE book_id = ?"
                " ORDER BY created_at, marker_id",
                (book_id,),
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT " + _COLUMNS + " FROM issue_markers WHERE book_id = ? AND state = ?"
                " ORDER BY created_at, marker_id",
                (book_id, state.value),
            ).fetchall()
        return [_marker_from_row(row) for row in rows]

    def update_marker(self, marker: IssueMarker) -> None:
        with self._conn:
            self._conn.execute(
                "UPDATE issue_markers SET state = ?, resolved_at = ? WHERE marker_id = ?",
                (marker.state.value, marker.resolved_at, marker.marker_id),
            )

    def delete_marker(self, marker_id: str) -> None:
        with self._conn:
            self._conn.execute("DELETE FROM issue_markers WHERE marker_id = ?", (marker_id,))

    # ------------------------------------------------------------------
    # ownership reads (frozen v1 tables; read-only)
    # ------------------------------------------------------------------
    def book_exists(self, book_id: str) -> bool:
        row = self._conn.execute(
            "SELECT 1 FROM books WHERE book_id = ? AND deleted_at IS NULL", (book_id,)
        ).fetchone()
        return row is not None

    def chapter_book_id(self, chapter_id: str) -> str | None:
        row = self._conn.execute(
            "SELECT book_id FROM chapters WHERE chapter_id = ? AND deleted_at IS NULL",
            (chapter_id,),
        ).fetchone()
        return None if row is None else str(row[0])

    def page_chapter_id(self, page_id: str) -> str | None:
        row = self._conn.execute(
            "SELECT chapter_id FROM pages WHERE page_id = ? AND deleted_at IS NULL", (page_id,)
        ).fetchone()
        return None if row is None else str(row[0])


def _marker_from_row(row) -> IssueMarker:
    return IssueMarker(
        marker_id=str(row[0]),
        book_id=str(row[1]),
        chapter_id=str(row[2]),
        page_id=str(row[3]),
        position_x=None if row[4] is None else float(row[4]),
        position_y=None if row[5] is None else float(row[5]),
        kind=str(row[6]),
        note=None if row[7] is None else str(row[7]),
        state=IssueMarkerState(str(row[8])),
        created_at=str(row[9]),
        resolved_at=None if row[10] is None else str(row[10]),
    )
