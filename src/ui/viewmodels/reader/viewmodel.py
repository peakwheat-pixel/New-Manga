"""ReaderViewModel: reader state between QML and ReadingService (TASK-015).

Published to QML as ``readerViewModel``. The ViewModel owns no business
rules: mode/direction/progress decisions live in ``ReadingService`` and
its store, QML only renders state and calls slots (D05 §60).

- ``openChapter`` loads the chapter through the injected page catalog
  (production binding is an assembly decision, same seam as the
  workbench's page catalog);
- reading time accumulates via a coarse internal heartbeat plus
  ``settleReadingTime`` on every progress-affecting slot, so duration
  survives crashes within the heartbeat granularity (D03 §29);
- ``openExporter`` lazily builds the chapter's ``ExportViewModel`` so the
  reader can hand the export window a ready controller (D05 §51);
- TASK-020 webtoon tiling: when a ``tile_factory`` is injected, webtoon
  chapters are served as rebuildable tile bands (``tiles``/``tilesActive``/
  ``requestTiles``/``clearTileCache``) instead of one whole-page image; the
  rasterizer owns the pixel cache only — progress, regions and render
  revisions stay in the reading service and are never cached here.
"""

from __future__ import annotations

import math
import time
from typing import Callable

from PySide6.QtCore import Property, QObject, QTimer, QUrl, Signal, Slot

from application.export import (
    ExportPage,
    ExportService,
    file_bytes_provider,
)
from application.reading.ports import ReaderPage, ReaderPageCatalog
from application.reading.service import (
    ReadingMode,
    ReadingService,
)
from ui.viewmodels.export.viewmodel import ExportViewModel

HEARTBEAT_MS = 5000  # coarse crash-granularity for accumulated reading time


class ReaderViewModel(QObject):
    stateChanged = Signal()
    summaryChanged = Signal()
    exportControllerChanged = Signal()
    tilesChanged = Signal()

    def __init__(
        self,
        reading: ReadingService,
        catalog: ReaderPageCatalog,
        *,
        export_service: ExportService | None = None,
        tile_factory: Callable[[str], object] | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._reading = reading
        self._catalog = catalog
        self._export_service = export_service
        self._tile_factory = tile_factory
        self._rasterizer: object | None = None
        self._tile_rows: list[dict] = []
        self._exporter: ExportViewModel | None = None
        self._heartbeat = QTimer(self)
        self._heartbeat.setInterval(HEARTBEAT_MS)
        self._heartbeat.timeout.connect(self.settleReadingTime)
        self._last_settle = 0.0

    # ------------------------------------------------------------------
    # session control
    # ------------------------------------------------------------------

    @Slot(str, str, str, str, str, bool)
    def openChapter(
        self,
        book_id: str,
        chapter_id: str,
        chapter_title: str,
        chapter_type: str,
        direction: str,
        resume: bool = True,
    ) -> None:
        self.settleReadingTime()
        pages = self._catalog.list_pages(chapter_id)
        self._reading.open(
            book_id,
            chapter_id,
            pages,
            chapter_title=chapter_title,
            chapter_type=chapter_type,
            direction=direction,
            mode=self._reading.mode,
            resume=resume,
        )
        self._rebuild_tiles()
        self._last_settle = time.monotonic()
        self._heartbeat.start()
        self.stateChanged.emit()
        self.summaryChanged.emit()

    @Slot()
    def closeReader(self) -> None:
        self.settleReadingTime()
        self._heartbeat.stop()
        self._reading.close()
        self.summaryChanged.emit()

    @Slot()
    def continueReading(self) -> None:
        """从上次位置继续 (D04 §36) — reopens the current chapter mode."""
        self.settleReadingTime()
        self._reading.open(
            self._reading.book_id,
            self._reading.chapter_id,
            self._reading.pages,
            chapter_title=self._reading.chapter_title,
            chapter_type=self._reading.chapter_type,
            direction=self._reading.direction,
            mode=self._reading.mode,
            resume=True,
        )
        self._rebuild_tiles()
        self.stateChanged.emit()

    @Slot()
    def restartFromBeginning(self) -> None:
        """从章节开头开始 (D04 §36)."""
        self.settleReadingTime()
        self._reading.open(
            self._reading.book_id,
            self._reading.chapter_id,
            self._reading.pages,
            chapter_title=self._reading.chapter_title,
            chapter_type=self._reading.chapter_type,
            direction=self._reading.direction,
            mode=self._reading.mode,
            resume=False,
        )
        self._rebuild_tiles()
        self.stateChanged.emit()

    # ------------------------------------------------------------------
    # properties
    # ------------------------------------------------------------------

    def _has_chapter(self) -> bool:
        return self._reading.progress is not None

    hasChapter = Property(bool, _has_chapter, notify=stateChanged)

    def _chapter_title(self) -> str:
        return self._reading.chapter_title

    chapterTitle = Property(str, _chapter_title, notify=stateChanged)

    def _mode(self) -> str:
        return self._reading.mode

    mode = Property(str, _mode, notify=stateChanged)

    def _direction(self) -> str:
        return self._reading.direction.value

    direction = Property(str, _direction, notify=stateChanged)

    def _chapter_type(self) -> str:
        return self._reading.chapter_type.value

    chapterType = Property(str, _chapter_type, notify=stateChanged)

    def _source_path(self) -> str:
        if not self._has_chapter():
            return ""
        path = self._reading.current_source_path
        # QML Image sources need file URIs (production catalogs hand out
        # storage paths); exports keep consuming the local path.
        return QUrl.fromLocalFile(path).toString() if path else ""

    sourcePath = Property(str, _source_path, notify=stateChanged)

    def _status_message(self) -> str:
        if not self._has_chapter():
            return ""
        return self._reading.status_message

    statusMessage = Property(str, _status_message, notify=stateChanged)

    def _page_number(self) -> int:
        """1-based position for display; 0 with no chapter."""
        return self._reading.page_index + 1 if self._has_chapter() else 0

    pageNumber = Property(int, _page_number, notify=stateChanged)

    def _page_count(self) -> int:
        return self._reading.page_count

    pageCount = Property(int, _page_count, notify=stateChanged)

    def _progress_percent(self) -> float:
        return self._reading.progress_percent

    progressPercent = Property(float, _progress_percent, notify=stateChanged)

    def _can_previous(self) -> bool:
        return self._has_chapter() and self._reading.page_index > 0

    canGoPrevious = Property(bool, _can_previous, notify=stateChanged)

    def _can_next(self) -> bool:
        return self._has_chapter() and self._reading.page_index < self._reading.page_count - 1

    canGoNext = Property(bool, _can_next, notify=stateChanged)

    def _total_read_seconds(self) -> float:
        if self._reading.progress is None:
            return 0.0
        return round(self._reading.progress.total_read_seconds, 3)

    totalReadSeconds = Property(float, _total_read_seconds, notify=summaryChanged)

    def _book_summary(self) -> dict:
        if not self._reading.book_id:
            return {}
        return self._reading.book_summary(self._reading.book_id)

    bookSummary = Property("QVariantMap", _book_summary, notify=summaryChanged)

    def _exporter(self) -> QObject | None:
        return self._exporter

    exportController = Property(QObject, _exporter, notify=exportControllerChanged)

    # ------------------------------------------------------------------
    # QML slots
    # ------------------------------------------------------------------

    @Slot(str)
    def setMode(self, mode: str) -> None:
        self.settleReadingTime()
        self._reading.set_mode(mode)
        self._rebuild_tiles()
        self.stateChanged.emit()

    @Slot()
    def nextPage(self) -> None:
        self.settleReadingTime()
        self._reading.next_page()
        # F-5 (TASK-045): a page turn changes the *source*, so the tile rows
        # must be rebuilt — otherwise the tiled viewer keeps showing the
        # previous page's pixels while progress already points at the new one.
        self._rebuild_tiles()
        self.stateChanged.emit()

    @Slot()
    def previousPage(self) -> None:
        self.settleReadingTime()
        self._reading.previous_page()
        self._rebuild_tiles()
        self.stateChanged.emit()

    @Slot(int)
    def jumpToPage(self, page_index: int) -> None:
        self.settleReadingTime()
        self._reading.jump_to_page(page_index)
        self._rebuild_tiles()
        self.stateChanged.emit()

    @Slot(float)
    def saveScrollOffset(self, offset_y: float) -> None:
        """Webtoon 定期保存 scroll_offset_y (D04 §35)."""
        self._reading.save_scroll_offset(offset_y)
        self.stateChanged.emit()

    def _scroll_offset_y(self) -> float:
        if self._reading.progress is None:
            return 0.0
        return self._reading.progress.scroll_offset_y

    scrollOffsetY = Property(float, _scroll_offset_y, notify=stateChanged)

    # ------------------------------------------------------------------
    # TASK-020 webtoon tiling (rebuildable pixel cache)
    # ------------------------------------------------------------------

    def _rebuild_tiles(self) -> None:
        """(Re)build the tile rasterizer for the current page and mode.

        Only webtoon chapters with an injected factory get tiles; everything
        else (and any factory failure) falls back to the whole-page image
        path. Tiles are a rebuildable pixel cache — clearing them never
        touches reading progress, regions or render revisions.
        """
        self._rasterizer = None
        self._tile_rows = []
        if self._tile_factory is None or not self._has_chapter():
            self.tilesChanged.emit()
            return
        if self._reading.chapter_type.value != "webtoon":
            self.tilesChanged.emit()
            return
        try:
            rasterizer = self._tile_factory(self._reading.current_source_path)
            self._tile_rows = [
                {
                    "index": tile.index,
                    "top": tile.content_top,
                    "height": tile.content_height,
                    "pageWidth": rasterizer.page_size[0],
                    "url": "",
                }
                for tile in rasterizer.grid.tiles
            ]
            self._rasterizer = rasterizer
        except (OSError, ValueError):
            # unreadable page: keep the whole-image path, QML surfaces the error
            self._rasterizer = None
            self._tile_rows = []
        self.tilesChanged.emit()

    def _tiles_active(self) -> bool:
        return self._rasterizer is not None

    tilesActive = Property(bool, _tiles_active, notify=tilesChanged)

    def _tiles(self) -> list:
        return self._tile_rows

    tiles = Property("QVariantList", _tiles, notify=tilesChanged)

    def _page_pixel_width(self) -> int:
        if self._rasterizer is None:
            return 0
        return self._rasterizer.page_size[0]

    pagePixelWidth = Property(int, _page_pixel_width, notify=tilesChanged)

    def _page_pixel_height(self) -> int:
        if self._rasterizer is None:
            return 0
        return self._rasterizer.page_size[1]

    pagePixelHeight = Property(int, _page_pixel_height, notify=tilesChanged)

    @Slot(float, float, float)
    def requestTiles(
        self, viewport_top: float, viewport_bottom: float, scale: float = 1.0
    ) -> None:
        """Materialise the visible tile band (+bounded prefetch) and fill the
        row URLs; QML calls this while scrolling the tiled webtoon viewer.

        Coordinate contract (F-11, TASK-045): the viewport arrives in
        **display** pixels (``Flickable.contentY``/``height``) while the tile
        grid speaks **page** pixels, so the caller passes ``scale`` = display
        pixels per page pixel (``host width / pagePixelWidth``). ``1.0`` — the
        historical behaviour — means the page is shown at 1:1.
        """
        if self._rasterizer is None:
            return
        grid = self._rasterizer.grid
        factor = float(scale) or 1.0
        top = int(math.floor(viewport_top / factor))
        bottom = int(math.ceil(viewport_bottom / factor))
        try:
            # materialise the visible band (+prefetch); the returned paths are
            # re-resolved per tile below, so the return value is not bound
            self._rasterizer.ensure_viewport(top, bottom)
        except (OSError, ValueError):
            self.tilesChanged.emit()
            return
        wanted_indices = {
            tile.index
            for tile in grid.visible_tiles(
                top, bottom, prefetch=self._rasterizer.prefetch
            )
        }
        changed = False
        for row in self._tile_rows:
            if row["url"] or row["index"] not in wanted_indices:
                continue
            path = self._rasterizer.tile_file(row["index"])
            row["url"] = QUrl.fromLocalFile(str(path)).toString()
            changed = True
        if changed:
            self.tilesChanged.emit()

    @Slot()
    def clearTileCache(self) -> None:
        """Drop the rebuildable tile pixels; business truth is untouched."""
        if self._rasterizer is None:
            return
        self._rasterizer.clear()
        for row in self._tile_rows:
            row["url"] = ""
        self.tilesChanged.emit()

    @Slot()
    def settleReadingTime(self) -> None:
        """Fold elapsed wall time into the mode's accumulated duration."""
        if self._reading.progress is None:
            self._last_settle = time.monotonic()
            return
        now = time.monotonic()
        elapsed = now - (self._last_settle or now)
        self._last_settle = now
        if elapsed > 0:
            self._reading.add_time(elapsed)
            self.summaryChanged.emit()

    @Slot()
    def openExporter(self) -> QObject | None:
        """Create (once) the export controller for the open chapter."""
        if self._exporter is None:
            if self._export_service is None:
                return None
            self._exporter = ExportViewModel(
                self._export_service, self._chapter_export_pages, parent=self
            )
            self.exportControllerChanged.emit()
        self._exporter.refreshStaleWarning()
        return self._exporter

    def _chapter_export_pages(self) -> list[ExportPage]:
        """Current chapter's pages as export inputs, in reading order."""
        pages: list[ExportPage] = []
        for page in self._reading.pages:
            pages.append(
                ExportPage(
                    page_id=page.page_id,
                    filename=page.filename,
                    source_provider=file_bytes_provider(page.original_path),
                    translated_provider=(
                        file_bytes_provider(page.translated_path)
                        if page.translated_path
                        else None
                    ),
                    translated_revision_id=page.translated_revision_id,
                    current_translated_revision_id=page.current_translated_revision_id,
                    text=page.text,
                )
            )
        return pages
