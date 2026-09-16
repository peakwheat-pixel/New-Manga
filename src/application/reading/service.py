from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path


class ReadingMode(str, Enum):
    ORIGINAL = "original"
    TRANSLATED = "translated"


@dataclass(frozen=True)
class PageView:
    page_id: str
    original_path: str
    translated_path: str | None
    translated_revision_id: str | None
    current_translated_revision_id: str | None
    translated_text: str = ""

    @property
    def stale(self) -> bool:
        return bool(
            self.translated_path
            and self.translated_revision_id
            and self.current_translated_revision_id
            and self.translated_revision_id != self.current_translated_revision_id
        )

    def source(self, mode: ReadingMode) -> tuple[str, str]:
        if mode is ReadingMode.TRANSLATED and self.translated_path and not self.stale:
            return self.translated_path, ""
        if mode is ReadingMode.TRANSLATED and not self.translated_path:
            return self.original_path, "translated image missing; showing original"
        if mode is ReadingMode.TRANSLATED and self.stale:
            return self.translated_path or self.original_path, "stale translated image; render current version first"
        return self.original_path, ""

    @property
    def source_path(self) -> str:
        return self.source(ReadingMode.TRANSLATED)[0] if self.translated_path else self.original_path

    @property
    def status_message(self) -> str:
        return self.source(ReadingMode.TRANSLATED)[1]


@dataclass(frozen=True)
class ReadingProgress:
    page_index: int = 0
    duration_seconds: float = 0.0
    updated_at: float = 0.0


class ReadingService:
    def __init__(self, state_path: str | Path):
        self._state_path = Path(state_path)
        self._state = self._read_state()
        self.pages: list[PageView] = []
        self.book_id = self.chapter_id = ""
        self.mode = ReadingMode.ORIGINAL
        self.direction = "rtl"
        self.progress = ReadingProgress()

    def open(self, book_id: str, chapter_id: str, pages: list[PageView], *, mode: ReadingMode = ReadingMode.ORIGINAL, direction: str = "rtl") -> None:
        if direction not in {"rtl", "ltr"}:
            raise ValueError("direction must be rtl or ltr")
        self.book_id, self.chapter_id, self.pages = book_id, chapter_id, list(pages)
        self.mode, self.direction = ReadingMode(mode), direction
        key = self._key()
        raw = self._state.get("progress", {}).get(key, {})
        self.progress = ReadingProgress(**raw) if raw else ReadingProgress()
        self.progress = ReadingProgress(min(self.progress.page_index, max(0, len(self.pages) - 1)), self.progress.duration_seconds, self.progress.updated_at)

    @property
    def current(self) -> PageView:
        if not self.pages:
            raise ValueError("reader has no pages")
        return self.pages[self.progress.page_index]

    @property
    def current_source_path(self) -> str:
        return self.current.source(self.mode)[0]

    def status_message(self) -> str:
        return self.current.source(self.mode)[1]

    def record_progress(self, page_index: int, duration_seconds: float = 0.0) -> None:
        if not self.pages or not 0 <= page_index < len(self.pages):
            raise IndexError("page index out of range")
        self.progress = ReadingProgress(page_index, max(0.0, float(duration_seconds)), time.time())
        self._state.setdefault("progress", {})[self._key()] = asdict(self.progress)
        self._write_state()

    def next_page(self) -> None:
        self.record_progress(min(self.progress.page_index + 1, len(self.pages) - 1), self.progress.duration_seconds)

    def close(self) -> None:
        if self.pages:
            self._state.setdefault("progress", {})[self._key()] = asdict(self.progress)
            self._write_state()

    def shelf_summary(self) -> dict[str, float | int]:
        return {"page_index": self.progress.page_index, "page_count": len(self.pages), "duration_seconds": self.progress.duration_seconds}

    def _key(self) -> str:
        return f"{self.book_id}/{self.chapter_id}/{self.mode.value}"

    def _read_state(self) -> dict:
        try:
            return json.loads(self._state_path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _write_state(self) -> None:
        self._state_path.parent.mkdir(parents=True, exist_ok=True)
        temp = self._state_path.with_suffix(self._state_path.suffix + ".tmp")
        temp.write_text(json.dumps(self._state, ensure_ascii=False, indent=2), encoding="utf-8")
        temp.replace(self._state_path)
