"""Reading session service (TASK-015; D03 §29, D04 §33~36, D05 §37~41).

Owns everything the reader page needs that is not QML:

- Original / Translated modes with fully independent progress and
  accumulated reading time per ``(book, chapter, mode)`` (AC-READ-001/002);
- RTL / LTR paging semantics and the vertical webtoon scroll offset
  (AC-READ-003/004; the full width-fit scrolling render is TASK-020's);
- resume ("continue from last position") vs. restart (D04 §36);
- missing/stale translated fallbacks with explicit status messages;
- the shelf-facing summary data (AC-LIB-004 / D05 §41) — last chapter,
  per-mode progress, last-read time and accumulated duration — which the
  book detail surface consumes via its viewmodel at integration time.

Progress rows mirror the frozen D03 §29 column list so a later SQLite
adapter (schema is frozen outside this task) can take over the store port
without touching this service.
"""

from __future__ import annotations

import json
import os
import tempfile
import uuid
from dataclasses import dataclass, fields, replace
from pathlib import Path

from domain.books.entities import ChapterType, ReadingDirection, utc_now

from application.reading.ports import (
    JsonProgressDocumentStore,
    ProgressDocumentStore,
    ReaderPage,
)


class ReadingMode:
    """Reading content mode (D03 §29 ``mode``); plain strings keep the
    JSON rows primitive."""

    ORIGINAL = "original"
    TRANSLATED = "translated"

    MODES = (ORIGINAL, TRANSLATED)


@dataclass
class ReadingProgress:
    """One progress row (D03 §29 field list, JSON-serializable)."""

    progress_id: str
    book_id: str
    chapter_id: str
    mode: str
    last_page_id: str = ""
    scroll_offset_x: float = 0.0
    scroll_offset_y: float = 0.0
    progress_percent: float = 0.0
    last_read_at: str = ""
    total_read_seconds: float = 0.0
    updated_at: str = ""

    def to_row(self) -> dict:
        return {item.name: getattr(self, item.name) for item in fields(self)}


@dataclass(frozen=True)
class ChapterReadingSummary:
    """Shelf-facing per-chapter, per-mode summary (D05 §41)."""

    chapter_id: str
    mode: str
    progress_percent: float
    last_read_at: str
    total_read_seconds: float


class ReadingService:
    """Stateful facade for one open reader session.

    Every progress-affecting call persists immediately, so a crash or
    process exit never loses more than the in-flight action (重启继续阅读).
    """

    def __init__(self, store: ProgressDocumentStore) -> None:
        self._store = store
        state = store.read()
        rows = state.get("progress_entries", [])
        self._rows: list[dict] = rows if isinstance(rows, list) else []

        self.book_id: str = ""
        self.chapter_id: str = ""
        self.chapter_title: str = ""
        self.chapter_type: ChapterType = ChapterType.PAGED
        self.direction: ReadingDirection = ReadingDirection.RTL
        self.mode: str = ReadingMode.ORIGINAL
        self.pages: list[ReaderPage] = []
        self.progress: ReadingProgress | None = None

    # ------------------------------------------------------------------
    # session lifecycle
    # ------------------------------------------------------------------

    def open(
        self,
        book_id: str,
        chapter_id: str,
        pages: list[ReaderPage],
        *,
        chapter_title: str = "",
        chapter_type: str | ChapterType = ChapterType.PAGED,
        direction: str | ReadingDirection = ReadingDirection.RTL,
        mode: str = ReadingMode.ORIGINAL,
        resume: bool = True,
    ) -> None:
        """Open a chapter and restore this (book, chapter, mode) progress.

        ``resume=False`` implements D04 §36's "从章节开头开始" choice while
        keeping the stored row (the user may still switch back to resume).
        """
        chapter_type = _as_chapter_type(chapter_type)
        direction = _as_direction(direction)
        if chapter_type is ChapterType.WEBTOON and direction is not ReadingDirection.VERTICAL:
            raise ValueError("webtoon chapters must use vertical direction")
        if chapter_type is ChapterType.PAGED and direction is ReadingDirection.VERTICAL:
            raise ValueError("paged chapters cannot use vertical direction")
        if not pages:
            raise ValueError("cannot open a chapter without pages")
        mode = _require_mode(mode)

        self.book_id = book_id
        self.chapter_id = chapter_id
        self.chapter_title = chapter_title
        self.chapter_type = chapter_type
        self.direction = direction
        self.mode = mode
        self.pages = list(pages)

        row = self._find_row(book_id, chapter_id, mode)
        if row is None:
            row = {
                "progress_id": f"rp-{uuid.uuid4().hex[:12]}",
                "book_id": book_id,
                "chapter_id": chapter_id,
                "mode": mode,
            }
            self._rows.append(row)
        progress = _progress_from_row(row)
        if not resume:
            progress.last_page_id = ""
            progress.scroll_offset_x = 0.0
            progress.scroll_offset_y = 0.0
        self.progress = _remap(progress, self.pages)
        self._touch(now=True, persist=False)
        self._persist()

    def close(self) -> None:
        """Persist current progress (duration is settled via ``add_time``)."""
        if self.progress is not None:
            self._touch(now=True)

    # ------------------------------------------------------------------
    # mode switching (AC-READ-001/002)
    # ------------------------------------------------------------------

    def set_mode(self, mode: str, *, resume: bool = True) -> None:
        """Switch Original/Translated; each mode restores its own position
        and keeps its own accumulated time."""
        mode = _require_mode(mode)
        if self.progress is None:
            raise ValueError("no chapter is open")
        if mode == self.mode:
            return
        self._touch(now=True)
        self.open(
            self.book_id,
            self.chapter_id,
            self.pages,
            chapter_title=self.chapter_title,
            chapter_type=self.chapter_type,
            direction=self.direction,
            mode=mode,
            resume=resume,
        )

    # ------------------------------------------------------------------
    # paging (AC-READ-003/004)
    # ------------------------------------------------------------------

    @property
    def page_index(self) -> int:
        if self.progress is None or not self.pages:
            return 0
        index = _index_of_page(self.pages, self.progress.last_page_id)
        return 0 if index is None else index

    @property
    def page_count(self) -> int:
        return len(self.pages)

    @property
    def progress_percent(self) -> float:
        if not self.pages:
            return 0.0
        return round((self.page_index + 1) / len(self.pages) * 100.0, 2)

    def next_page(self) -> None:
        """Advance in reading order; a no-op at the last page."""
        self._goto(min(self.page_index + 1, len(self.pages) - 1))

    def previous_page(self) -> None:
        """Step back in reading order; a no-op at the first page."""
        self._goto(max(self.page_index - 1, 0))

    def jump_to_page(self, page_index: int) -> None:
        self._goto(int(page_index))

    # ------------------------------------------------------------------
    # webtoon scroll (D03 §29 / D04 §35)
    # ------------------------------------------------------------------

    def save_scroll_offset(self, offset_y: float, offset_x: float = 0.0) -> None:
        if self.progress is None:
            raise ValueError("no chapter is open")
        self.progress.scroll_offset_y = max(0.0, float(offset_y))
        self.progress.scroll_offset_x = max(0.0, float(offset_x))
        self._touch(now=False)

    # ------------------------------------------------------------------
    # duration (D03 §29 total_read_seconds, per mode)
    # ------------------------------------------------------------------

    def add_time(self, seconds: float) -> None:
        """Accumulate reading time for the open (book, chapter, mode)."""
        if self.progress is None:
            raise ValueError("no chapter is open")
        self.progress.total_read_seconds = max(
            0.0, self.progress.total_read_seconds + float(seconds)
        )
        self._touch(now=True)

    # ------------------------------------------------------------------
    # page content resolution (缺译图 / stale)
    # ------------------------------------------------------------------

    @property
    def current_page(self) -> ReaderPage:
        if not self.pages:
            raise ValueError("no chapter is open")
        return self.pages[self.page_index]

    def resolve_page(self, page: ReaderPage) -> tuple[str, str]:
        """Return ``(path, status_message)`` for the current mode.

        Translated mode falls back with an explicit message when the render
        is missing, and keeps showing a stale render with an explicit
        notice instead of pretending it is current (D06 §97).
        """
        if self.mode == ReadingMode.ORIGINAL:
            return page.original_path, ""
        if not page.translated_path:
            return page.original_path, "译图缺失，已显示原图"
        if page.translated_stale:
            return page.translated_path, "译图不是最新渲染结果，可重新渲染后阅读"
        return page.translated_path, ""

    @property
    def current_source_path(self) -> str:
        return self.resolve_page(self.current_page)[0]

    @property
    def status_message(self) -> str:
        if not self.pages:
            return ""
        return self.resolve_page(self.current_page)[1]

    def stale_page_ids(self) -> list[str]:
        """Pages whose translated render is not the current revision."""
        return [page.page_id for page in self.pages if page.translated_stale]

    def missing_translation_page_ids(self) -> list[str]:
        return [page.page_id for page in self.pages if not page.translated_path]

    # ------------------------------------------------------------------
    # shelf summary (AC-LIB-004 / D05 §41)
    # ------------------------------------------------------------------

    def chapter_summaries(self, book_id: str) -> list[ChapterReadingSummary]:
        """All progress rows of one book, most recently read first.

        Ties on ``last_read_at`` (same-second writes) fall back to the
        chapter id so the order stays deterministic.
        """
        rows = [
            row
            for row in self._rows
            if row.get("book_id") == book_id and row.get("last_read_at")
        ]
        rows.sort(key=lambda row: str(row.get("chapter_id", "")), reverse=True)
        rows.sort(key=lambda row: str(row.get("last_read_at", "")), reverse=True)
        return [
            ChapterReadingSummary(
                chapter_id=str(row.get("chapter_id", "")),
                mode=str(row.get("mode", "")),
                progress_percent=_as_float(row.get("progress_percent")),
                last_read_at=str(row.get("last_read_at", "")),
                total_read_seconds=_as_float(row.get("total_read_seconds")),
            )
            for row in rows
        ]

    def book_summary(self, book_id: str) -> dict:
        """Book-level reading digest for the book detail surface: 最近阅读
        章节 / 阅读进度 / 最后阅读时间 / 累计阅读时长 (D03 §29)."""
        summaries = self.chapter_summaries(book_id)
        if not summaries:
            return {
                "book_id": book_id,
                "has_progress": False,
                "last_chapter_id": "",
                "last_mode": "",
                "last_read_at": "",
                "progress_percent": 0.0,
                "total_read_seconds": 0.0,
            }
        latest = summaries[0]
        return {
            "book_id": book_id,
            "has_progress": True,
            "last_chapter_id": latest.chapter_id,
            "last_mode": latest.mode,
            "last_read_at": latest.last_read_at,
            "progress_percent": latest.progress_percent,
            "total_read_seconds": round(
                sum(item.total_read_seconds for item in summaries), 3
            ),
        }

    def shelf_summary(self, book_id: str) -> dict:
        """Alias kept for the shelf integration seam (AC-LIB-004)."""
        return self.book_summary(book_id)

    # ------------------------------------------------------------------
    # persistence helpers
    # ------------------------------------------------------------------

    def _find_row(self, book_id: str, chapter_id: str, mode: str) -> dict | None:
        for row in self._rows:
            if (
                row.get("book_id") == book_id
                and row.get("chapter_id") == chapter_id
                and row.get("mode") == mode
            ):
                return row
        return None

    def _goto(self, index: int) -> None:
        if self.progress is None:
            raise ValueError("no chapter is open")
        if not 0 <= index < len(self.pages):
            raise IndexError("page index out of range")
        self.progress.last_page_id = self.pages[index].page_id
        self.progress.progress_percent = self.progress_percent
        self._touch(now=True)

    def _touch(self, *, now: bool, persist: bool = True) -> None:
        if self.progress is None:
            return
        self.progress.updated_at = utc_now()
        if now:
            self.progress.last_read_at = utc_now()
        row = self._find_row(self.book_id, self.chapter_id, self.mode)
        if row is not None:
            row.update(self.progress.to_row())
        if persist:
            self._persist()

    def _persist(self) -> None:
        self._store.write({"progress_entries": self._rows})


def _progress_from_row(row: dict) -> ReadingProgress:
    """Build a progress object from a stored row, tolerating junk values."""
    names = {item.name for item in fields(ReadingProgress)}
    known = {key: value for key, value in row.items() if key in names}
    for name in ("scroll_offset_x", "scroll_offset_y", "progress_percent", "total_read_seconds"):
        known[name] = _as_float(known.get(name))
    for name in ("progress_id", "book_id", "chapter_id", "mode", "last_page_id", "last_read_at", "updated_at"):
        known[name] = str(known.get(name, ""))
    return ReadingProgress(**known)


def _remap(progress: ReadingProgress, pages: list[ReaderPage]) -> ReadingProgress:
    """Clamp/restore a stored row onto the current page list.

    ``last_page_id`` wins when the page still exists (reordering must not
    lose the position); otherwise reading restarts from the first page —
    guessing from a stale percent would land on a wrong page silently.
    """
    if not pages:
        return replace(progress, last_page_id="", progress_percent=0.0)
    if _index_of_page(pages, progress.last_page_id) is None:
        return replace(progress, last_page_id=pages[0].page_id)
    return progress


def _index_of_page(pages: list[ReaderPage], page_id: str) -> int | None:
    for index, page in enumerate(pages):
        if page.page_id == page_id:
            return index
    return None


def _as_chapter_type(value) -> ChapterType:
    return value if isinstance(value, ChapterType) else ChapterType(value)


def _as_direction(value) -> ReadingDirection:
    return value if isinstance(value, ReadingDirection) else ReadingDirection(value)


def _require_mode(mode: str) -> str:
    if mode not in ReadingMode.MODES:
        raise ValueError(f"unknown reading mode: {mode!r}")
    return mode


def _as_float(value) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def default_progress_store() -> ProgressDocumentStore:
    """Store on the shared data root (``NEWMANGA_DATA_ROOT`` or home)."""
    root = os.environ.get("NEWMANGA_DATA_ROOT")
    base = Path(root) if root else Path.home() / ".newmanga"
    return JsonProgressDocumentStore(base / "reading_progress.json")
