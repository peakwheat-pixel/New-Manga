"""QAbstractListModel over the shared task projection (TASK-013, D05 §18).

The rows are page tiles; every row's status comes from the single
``TaskProjection`` built by the viewmodel, so PageList and TaskProgressPanel
can never disagree (AC-PROGRESS-007). Filtering (failed/completed/skipped,
AC-PROGRESS-004/005) only changes which projection rows are visible — counts
always come from the projection itself, never from this filtered view.
"""

from __future__ import annotations

from PySide6.QtCore import (
    QAbstractListModel,
    QByteArray,
    QModelIndex,
    Qt,
    Signal,
    Slot,
)

from ui.models.tasks.projection import PageProjectionRow, TaskProjection

_ROLES = (
    ("pageId", "page_id"),
    ("pageOrder", "page_order"),
    ("filename", "filename"),
    ("status", "status"),
    ("isLocked", "is_locked"),
    ("isPipelineCurrent", "is_pipeline_current"),
    ("isSelected", "is_selected"),
    ("errorCode", "error_code"),
)

FILTERS = ("all", "failed", "completed", "skipped")


class WorkbenchPageListModel(QAbstractListModel):
    filterChanged = Signal()
    selectionChanged = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._rows: tuple[PageProjectionRow, ...] = ()
        self._visible: tuple[PageProjectionRow, ...] = ()
        self._filter = "all"
        self._selected: set[str] = set()

    # Qt wiring -------------------------------------------------------

    def rowCount(self, parent=QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._visible)

    def roleNames(self) -> dict[int, QByteArray]:
        base = super().roleNames()
        start = int(Qt.ItemDataRole.UserRole) + 1
        for offset, (name, _attr) in enumerate(_ROLES):
            base[start + offset] = name.encode()
        return base

    def data(self, index: QModelIndex, role: int = int(Qt.ItemDataRole.DisplayRole)):
        if not index.isValid() or not (0 <= index.row() < len(self._visible)):
            return None
        row = self._visible[index.row()]
        start = int(Qt.ItemDataRole.UserRole) + 1
        offset = role - start
        if not (0 <= offset < len(_ROLES)):
            return None
        name, attr = _ROLES[offset]
        if name == "isSelected":
            return row.page_id in self._selected
        return getattr(row, attr)

    def roleForName(self, name: str) -> int:
        start = int(Qt.ItemDataRole.UserRole) + 1
        for offset, (role_name, _attr) in enumerate(_ROLES):
            if role_name == name:
                return start + offset
        return -1

    # projection input ------------------------------------------------

    def apply_projection(self, projection: TaskProjection) -> None:
        """Replace rows from the shared projection, preserving filter and
        selection (selection of pages that disappeared is dropped)."""

        self.beginResetModel()
        self._rows = projection.rows
        self._selected &= {row.page_id for row in self._rows}
        self._visible = tuple(row for row in self._rows if self._matches_filter(row))
        self.endResetModel()

    def _rebuild_visible(self) -> None:
        self.beginResetModel()
        self._visible = tuple(row for row in self._rows if self._matches_filter(row))
        self.endResetModel()

    def _matches_filter(self, row: PageProjectionRow) -> bool:
        return self._filter == "all" or row.status == self._filter

    # filter (AC-PROGRESS-004/005) ------------------------------------

    def get_filter(self) -> str:
        return self._filter

    def set_filter(self, kind: str) -> None:
        if kind not in FILTERS:
            raise ValueError(f"unknown page filter: {kind!r}")
        if self._filter != kind:
            self._filter = kind
            self._rebuild_visible()
            self.filterChanged.emit()

    filter = property(get_filter, set_filter)

    # selection (AC-PAGE-002: single / ctrl / shift within the chapter) -

    def get_selected_ids(self) -> list[str]:
        ordered = [row.page_id for row in self._rows if row.page_id in self._selected]
        return ordered

    def set_selected(self, page_ids) -> None:
        known = {row.page_id for row in self._rows}
        updated = {page_id for page_id in page_ids if page_id in known}
        if updated != self._selected:
            self._selected = updated
            self._refresh_selection_roles()
            self.selectionChanged.emit()

    selectedIds = property(get_selected_ids)

    def toggle_selected(self, page_id: str) -> None:
        if page_id in {row.page_id for row in self._rows}:
            self._selected ^= {page_id}
            self._refresh_selection_roles()
            self.selectionChanged.emit()

    def clear_selection(self) -> None:
        if self._selected:
            self._selected.clear()
            self._refresh_selection_roles()
            self.selectionChanged.emit()

    def _refresh_selection_roles(self) -> None:
        if not self._visible:
            return
        first = self.index(0)
        last = self.index(len(self._visible) - 1)
        self.dataChanged.emit(
            first, last, [self.roleForName("isSelected")]
        )

    # helpers -----------------------------------------------------------

    def row_index_of(self, page_id: str) -> int:
        for index, row in enumerate(self._visible):
            if row.page_id == page_id:
                return index
        return -1

    @Slot(str, result=int)
    def rowIndexOf(self, page_id: str) -> int:
        """QML scroll target lookup (AC-PROGRESS-003)."""

        return self.row_index_of(page_id)

    @Slot(int, result=str)
    def pageIdAt(self, row: int) -> str:
        page_id = self.page_id_at(row)
        return page_id or ""

    def page_id_at(self, row: int) -> str | None:
        if 0 <= row < len(self._visible):
            return self._visible[row].page_id
        return None
