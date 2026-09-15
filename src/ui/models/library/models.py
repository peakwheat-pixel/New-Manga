"""QAbstractListModel adapters for the bookshelf (TASK-012, D05 §7.1/§9).

Roles mirror the D05 card/row fields. Reading progress has no Book field
yet (TASK-007 delivers none), so the ``progress`` role renders "—" rather
than fabricating a number; GridView/ListView provide the virtualization.
"""

from __future__ import annotations

from PySide6.QtCore import (
    QAbstractListModel,
    QByteArray,
    QModelIndex,
    Qt,
)

_BOOK_ROLES = (
    ("bookId", "book_id"),
    ("title", "title"),
    ("originalTitle", "original_title"),
    ("isFavorite", "is_favorite"),
    ("isArchived", "is_archived"),
    ("lastOpenedAt", "last_opened_at"),
    ("progress", "progress"),
)

_CHAPTER_ROLES = (
    ("chapterId", "chapter_id"),
    ("chapterNumber", "chapter_number"),
    ("title", "title"),
    ("chapterType", "chapter_type"),
    ("readingDirection", "reading_direction"),
    ("pageCount", "page_count"),
)

_PROGRESS_PLACEHOLDER = "—"


class _RoleModelBase(QAbstractListModel):
    """Shared role plumbing; subclasses supply ``_rows`` and ``_roles``."""

    _roles: tuple[tuple[str, str]] = ()
    _rows: list = []

    # Qt wiring -------------------------------------------------------

    def rowCount(self, parent=QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._rows)

    def roleNames(self) -> dict[int, QByteArray]:
        base = super().roleNames()
        start = int(Qt.ItemDataRole.UserRole) + 1
        for offset, (name, _attr) in enumerate(self._roles):
            base[start + offset] = name.encode()
        return base

    # python-side helpers ---------------------------------------------

    def roleForName(self, name: str) -> int:
        start = int(Qt.ItemDataRole.UserRole) + 1
        for offset, (role_name, _attr) in enumerate(self._roles):
            if role_name == name:
                return start + offset
        return -1

    @classmethod
    def _row_from_entity(cls, entity) -> dict:
        row = {}
        for _name, attr in cls._roles:
            value = getattr(entity, attr, None)
            row[attr] = value.value if hasattr(value, "value") else value
        return row

    def _role_value(self, row: int, role: int):
        start = int(Qt.ItemDataRole.UserRole) + 1
        offset = role - start
        if not (0 <= offset < len(self._roles)):
            return None
        _name, attr = self._roles[offset]
        return self._rows[row].get(attr)


class BookListModel(_RoleModelBase):
    _roles = _BOOK_ROLES
    _rows: list[dict]

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._rows = []

    def data(self, index: QModelIndex, role: int = int(Qt.ItemDataRole.DisplayRole)):
        if not index.isValid() or not (0 <= index.row() < len(self._rows)):
            return None
        value = self._role_value(index.row(), role)
        if role == self.roleForName("progress"):
            return value or _PROGRESS_PLACEHOLDER
        return value

    def set_books(self, books: list) -> None:
        self.beginResetModel()
        self._rows = [
            row if isinstance(row, dict) else self._row_from_entity(row)
            for row in books
        ]
        self.endResetModel()

    def refresh(self, books: list) -> None:
        self.set_books(books)


class ChapterListModel(_RoleModelBase):
    _roles = _CHAPTER_ROLES
    _rows: list[dict]

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._rows = []

    def data(self, index: QModelIndex, role: int = int(Qt.ItemDataRole.DisplayRole)):
        if not index.isValid() or not (0 <= index.row() < len(self._rows)):
            return None
        return self._role_value(index.row(), role)

    def set_chapters(self, chapters: list) -> None:
        self.beginResetModel()
        self._rows = [
            row if isinstance(row, dict) else self._row_from_entity(row)
            for row in chapters
        ]
        self.endResetModel()
