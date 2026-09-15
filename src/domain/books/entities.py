"""Book / Chapter / Tag domain entities (D03 §3~4, §30).

Pure domain: no sqlite3/PySide6 imports (TASK-005 architecture guards).
No Volume entity exists by design — "卷/话/番外" are chapter titles and
numbers (D03 §3.1, AC-CH-001).
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import Enum


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


class ChapterType(str, Enum):
    """D03 §4.2: a chapter is either paged manga or a webtoon strip."""

    PAGED = "paged"
    WEBTOON = "webtoon"


class ReadingDirection(str, Enum):
    """D03 §4.2: rtl / ltr for paged manga, vertical for webtoon."""

    RTL = "rtl"
    LTR = "ltr"
    VERTICAL = "vertical"


def _require_text(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
    return value


@dataclass
class Book:
    """D03 §3.2. Favorite/archive are system states, never tags (§3.3)."""

    book_id: str
    title: str
    original_title: str = ""
    author: str = ""
    publisher: str = ""
    series_title: str = ""
    description: str = ""
    source_language: str = ""
    target_language: str = ""
    source_url: str = ""
    notes: str = ""
    default_chapter_type: ChapterType = ChapterType.PAGED
    default_reading_direction: ReadingDirection = ReadingDirection.RTL
    is_favorite: bool = False
    is_archived: bool = False
    last_opened_at: str | None = None
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)
    deleted_at: str | None = None

    def __post_init__(self) -> None:
        _require_text(self.title, "title")
        self.default_chapter_type = ChapterType(self.default_chapter_type)
        self.default_reading_direction = ReadingDirection(self.default_reading_direction)

    def apply_edit(self, **changes: str) -> None:
        """Apply user edits to display metadata and bump updated_at."""
        allowed = {
            "title", "original_title", "author", "publisher", "series_title",
            "description", "source_language", "target_language", "source_url", "notes",
        }
        unknown = set(changes) - allowed
        if unknown:
            raise ValueError(f"unknown book fields: {sorted(unknown)}")
        if "title" in changes:
            _require_text(changes["title"], "title")
        for name, value in changes.items():
            setattr(self, name, value)
        self.updated_at = utc_now()

    def set_favorite(self, favorite: bool) -> None:
        self.is_favorite = bool(favorite)
        self.updated_at = utc_now()

    def set_archived(self, archived: bool) -> None:
        self.is_archived = bool(archived)
        self.updated_at = utc_now()

    def mark_opened(self) -> None:
        self.last_opened_at = utc_now()
        self.updated_at = self.last_opened_at

    def soft_delete(self) -> None:
        self.deleted_at = utc_now()
        self.updated_at = self.deleted_at

    @property
    def deleted(self) -> bool:
        return self.deleted_at is not None


@dataclass
class Chapter:
    """D03 §4.3. Defaults inherit from the book; a chapter may override.

    Direction invariant (D03 §4.4): webtoon chapters are vertical; paged
    chapters are rtl or ltr.
    """

    chapter_id: str
    book_id: str
    title: str
    chapter_number: str = ""
    subtitle: str = ""
    import_order: int = 0
    sort_order: int = 0
    chapter_type: ChapterType = ChapterType.PAGED
    reading_direction: ReadingDirection = ReadingDirection.RTL
    notes: str = ""
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)
    deleted_at: str | None = None

    def __post_init__(self) -> None:
        _require_text(self.title, "chapter title")
        _require_text(self.book_id, "book_id")
        self.chapter_type = ChapterType(self.chapter_type)
        self.reading_direction = ReadingDirection(self.reading_direction)
        self._enforce_direction_invariant()

    def _enforce_direction_invariant(self) -> None:
        if self.chapter_type is ChapterType.WEBTOON:
            if self.reading_direction is not ReadingDirection.VERTICAL:
                raise ValueError("webtoon chapters must use reading_direction=vertical")
        elif self.reading_direction is ReadingDirection.VERTICAL:
            raise ValueError("paged chapters cannot use reading_direction=vertical")

    def apply_edit(self, **changes: str) -> None:
        allowed = {"title", "subtitle", "chapter_number", "notes"}
        unknown = set(changes) - allowed
        if unknown:
            raise ValueError(f"unknown chapter fields: {sorted(unknown)}")
        if "title" in changes:
            _require_text(changes["title"], "chapter title")
        for name, value in changes.items():
            setattr(self, name, value)
        self.updated_at = utc_now()

    def reorder(self, sort_order: int) -> None:
        """User reordering touches sort_order only; import_order is frozen."""
        self.sort_order = int(sort_order)
        self.updated_at = utc_now()

    def soft_delete(self) -> None:
        self.deleted_at = utc_now()
        self.updated_at = self.deleted_at

    @property
    def deleted(self) -> bool:
        return self.deleted_at is not None

    def with_inherited_defaults(
        self, book_default_type: ChapterType, book_default_direction: ReadingDirection
    ) -> "Chapter":
        """Return a copy with unset type/direction resolved from the book.

        Paged chapters inherit the book direction only when it is rtl/ltr;
        a webtoon book default does not force vertical onto paged chapters
        (D03 §4.4: paged direction comes from the work settings, rtl/ltr).
        """
        chapter_type = self.chapter_type or book_default_type
        reading_direction = self.reading_direction
        if reading_direction is None:
            if chapter_type is ChapterType.WEBTOON:
                reading_direction = ReadingDirection.VERTICAL
            elif book_default_direction is not ReadingDirection.VERTICAL:
                reading_direction = book_default_direction
            else:
                reading_direction = ReadingDirection.RTL
        return replace(
            self, chapter_type=chapter_type, reading_direction=reading_direction
        )


@dataclass
class Tag:
    """D03 §30: free-form user labels; never encode favorite/archive."""

    tag_id: str
    name: str
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        _require_text(self.name, "tag name")

    def rename(self, name: str) -> None:
        _require_text(name, "tag name")
        self.name = name
        self.updated_at = utc_now()
