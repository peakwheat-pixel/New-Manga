"""WorkbenchViewModel: workbench state between QML and the pipeline (TASK-013).

Published to QML as ``workbenchViewModel``. Responsibilities:

- own the Book/Chapter workbench context and the chapter page catalog;
- build ONE ``TaskProjection`` per refresh and feed both the PageList model
  and the TaskProgressPanel fields (AC-PROGRESS-007, D06 §79);
- keep the Viewer's current page separate from the pipeline's focus page
  (D05 §18.3, AC-PROGRESS-003);
- run commands through the injected ``PipelineService`` and execute them on
  a worker thread via ``RunController`` (AC-NFR-UI-001);
- throttle progress refreshes to ~4 Hz while key events (finish, control
  acknowledgement) refresh immediately (AC-NFR-UI-002, AC-PAUSE-001);
- guard Region/Page navigation behind a save/discard/cancel confirm when
  the inspector is dirty (D05 §55).

Business rules stay out of QML (D05 §60); infrastructure imports stay out
of this layer (architecture guard). Page/region catalog access is a duck-
typed seam so the production binding is an assembly decision.
"""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from PySide6.QtCore import Property, QObject, QTimer, Signal, Slot

from application.tasks.service import PipelineService
from domain.tasks.models import (
    CommandType,
    PipelineError,
    PipelineRun,
    PipelineRunStatus,
    PipelineScope,
    ScopeType,
)
from ui.models.tasks.page_list_model import WorkbenchPageListModel
from ui.models.tasks.projection import (
    STATUS_WAITING,
    TaskProjection,
    build_projection,
    step_label,
)
from ui.viewmodels.workbench.run_controller import (
    RestoreLatchClosedError,
    RunController,
    is_terminal_status,
)

VIEWER_MODES = ("original", "clean", "translated", "compare")

PROGRESS_REFRESH_MS = 250  # ~4 Hz (AC-NFR-UI-002)

# Run-status value shown when no run exists yet.
IDLE_STATUS = "idle"


class WorkbenchViewModel(QObject):
    contextChanged = Signal()
    viewerChanged = Signal()
    inspectorChanged = Signal()
    inspectorDirtyChanged = Signal()
    taskProgressChanged = Signal()
    runStatusChanged = Signal()
    pageFilterChanged = Signal()
    pageLocateRequested = Signal(str)  # page_id — PageList scroll target
    selectionChanged = Signal()
    inspectorDirtyConfirmRequested = Signal("QVariantMap")
    commandError = Signal(str)
    commandErrorChanged = Signal()
    runFinished = Signal(str, str)  # run_id, final status

    def __init__(
        self,
        *,
        pipeline: PipelineService,
        page_catalog,  # duck-typed: list_pages(chapter_id) -> page-like
        region_catalog=None,  # duck-typed: list_regions(page_id) / get_region(id)
        translation_editor=None,  # duck-typed: save_manual_translation(id, text)
        navigation=None,  # NavigationViewModel for the D05 §3.1 badge
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._pipeline = pipeline
        self._page_catalog = page_catalog
        self._region_catalog = region_catalog
        self._translation_editor = translation_editor
        self._navigation = navigation

        self._book_id: str | None = None
        self._chapter_id: str | None = None
        self._book_title = ""
        self._chapter_title = ""
        self._pages: dict[str, dict] = {}  # page_id -> catalog row

        self._page_model = WorkbenchPageListModel(self)
        self._projection: TaskProjection | None = None

        # TASK-052: latest command failure surface (provisional minimal
        # visibility until the TASK-047 design gate converges the UI)
        self._command_error_text = ""

        # viewer vs pipeline focus are two different pages (D05 §18.3)
        self._viewer_page_id: str | None = None
        self._viewer_mode = "original"
        self._selection_anchor: str | None = None

        # inspector / dirty state
        self._inspector_region_id: str | None = None
        self._inspector_saved_text = ""
        self._inspector_text = ""
        self._inspector_dirty = False
        self._pending_navigation: dict | None = None

        # run state
        self._run: PipelineRun | None = None
        self._pausing = False
        # TASK-057 Q-008 前置① / TASK-061 R-004 / review R-001: the
        # restore latch lives on the controller (``RunController.start``
        # is the sole worker birthplace, reached from four VM call
        # sites); ``_restore_in_progress`` is this VM's mirror of it for
        # cheap reads.  The ``_start_run`` pre-check below rejects before
        # ``create_run``/``plan_run`` would write during a restore.
        self._restore_in_progress = False
        self._controller = RunController(self)
        self._controller.runFinished.connect(self._on_run_finished)
        self._controller.runCrashed.connect(self._on_run_crashed)

        self._progress_timer = QTimer(self)
        self._progress_timer.setInterval(PROGRESS_REFRESH_MS)
        self._progress_timer.timeout.connect(self._refresh_from_run)

    # ------------------------------------------------------------------
    # context (D05 §62: empty state until a Book/Chapter is chosen)
    # ------------------------------------------------------------------

    def get_has_context(self) -> bool:
        return bool(self._chapter_id)

    hasContext = Property(bool, get_has_context, notify=contextChanged)

    def get_context_info(self) -> dict:
        return {
            "book_id": self._book_id or "",
            "chapter_id": self._chapter_id or "",
            "book_title": self._book_title,
            "chapter_title": self._chapter_title,
        }

    contextInfo = Property("QVariantMap", get_context_info, notify=contextChanged)

    @Slot(str, str, str, str)
    def setContext(
        self, book_id: str, chapter_id: str, book_title: str, chapter_title: str
    ) -> None:
        self._book_id = book_id
        self._chapter_id = chapter_id
        self._book_title = book_title
        self._chapter_title = chapter_title
        self._viewer_page_id = None
        self._inspector_region_id = None
        self._inspector_dirty = False
        self._load_pages()
        self._refresh_projection()
        self.contextChanged.emit()
        self.viewerChanged.emit()
        self.inspectorChanged.emit()

    @Slot()
    def clearContext(self) -> None:
        self.setContext("", "", "", "")

    def _load_pages(self) -> None:
        self._pages = {}
        if not self._chapter_id:
            return
        for page in self._page_catalog.list_pages(self._chapter_id):
            self._pages[page.page_id] = {
                "page_id": page.page_id,
                "page_order": getattr(page, "sort_order", 0),
                "filename": page.source_filename,
                "locked": bool(getattr(page, "page_locked", False)),
                "managed_original_ref": getattr(page, "managed_original_ref", ""),
            }

    def _page_meta(self) -> dict[str, tuple[int, str, bool]]:
        return {
            page_id: (row["page_order"], row["filename"], row["locked"])
            for page_id, row in self._pages.items()
        }

    # ------------------------------------------------------------------
    # projection → page list model + progress fields (single source)
    # ------------------------------------------------------------------

    def get_page_list_model(self) -> QObject:
        return self._page_model

    pageListModel = Property(QObject, get_page_list_model, constant=True)

    def _refresh_projection(self) -> None:
        if self._run is not None:
            self._projection = build_projection(self._run, self._page_meta())
        else:
            self._projection = self._idle_projection()
        self._page_model.apply_projection(self._projection)
        self._sync_navigation_badge()
        self.taskProgressChanged.emit()
        self.runStatusChanged.emit()

    def _idle_projection(self) -> TaskProjection:
        from ui.models.tasks.projection import PageProjectionRow

        rows = tuple(
            PageProjectionRow(
                page_id=page_id,
                page_order=row["page_order"],
                filename=row["filename"],
                status=STATUS_WAITING,
                is_locked=row["locked"],
            )
            for page_id, row in sorted(
                self._pages.items(), key=lambda item: item[1]["page_order"]
            )
        )
        return TaskProjection(
            run_id="",
            run_status=IDLE_STATUS,
            run_title="",
            overall_progress=0.0,
            current_page_id=None,
            current_step_type="",
            rows=rows,
            total_page_count=len(rows),
            waiting_page_count=len(rows),
        )

    def get_task_progress(self) -> dict:
        projection = self._projection or self._idle_projection()
        return {
            "run_id": projection.run_id,
            "run_title": projection.run_title,
            "run_status": projection.run_status,
            # active = a run is executing on the controller right now; a
            # finished run keeps its projection visible but is not active
            "active": self._controller.is_running,
            "pausing": self._pausing,
            "overall_progress": projection.overall_progress,
            "progress_percent": projection.progress_percent,
            "total_page_count": projection.total_page_count,
            "completed_page_count": projection.completed_page_count,
            "failed_page_count": projection.failed_page_count,
            "skipped_page_count": projection.skipped_page_count,
            "blocked_page_count": projection.blocked_page_count,
            "waiting_page_count": projection.waiting_page_count,
            "processing_page_count": projection.processing_page_count,
            "current_page_id": projection.current_page_id or "",
            "current_page_name": self._page_name(projection.current_page_id),
            "current_step_type": projection.current_step_type,
            "current_step_label": step_label(projection.current_step_type)
            if projection.current_step_type
            else "",
            "step_flow": [
                {"type": step_type, "label": label, "state": state}
                for step_type, label, state in projection.step_flow
            ],
            "blocked_reasons": list(projection.blocked_reasons),
            "can_pause": projection.can_pause and not self._pausing,
            "can_stop": projection.can_stop,
            "can_continue": projection.can_continue,
            "can_restart": projection.can_restart,
            "can_abandon": projection.can_abandon,
            "can_retry_failed": projection.can_retry_failed,
        }

    taskProgress = Property("QVariantMap", get_task_progress, notify=taskProgressChanged)

    def get_run_status(self) -> str:
        if self._projection is None:
            return IDLE_STATUS
        return self._projection.run_status

    runStatus = Property(str, get_run_status, notify=runStatusChanged)

    def _page_name(self, page_id: str | None) -> str:
        if page_id is None:
            return ""
        return self._pages.get(page_id, {}).get("filename", page_id)

    def _sync_navigation_badge(self) -> None:
        if self._navigation is None:
            return
        running = (
            self._run is not None
            and self._run.status is PipelineRunStatus.RUNNING
        )
        self._navigation.setWorkbenchActivity(running, "●" if running else "")

    # ------------------------------------------------------------------
    # page selection: viewer page + multi-select (AC-PAGE-002, D05 §18.3)
    # ------------------------------------------------------------------

    def get_viewer_page_id(self) -> str:
        return self._viewer_page_id or ""

    viewerPageId = Property(str, get_viewer_page_id, notify=viewerChanged)

    def get_selected_page_ids(self) -> list:
        return self._page_model.get_selected_ids()

    selectedPageIds = Property("QVariantList", get_selected_page_ids, notify=selectionChanged)

    def get_selected_page_count(self) -> int:
        return len(self._page_model.get_selected_ids())

    selectedPageCount = Property(int, get_selected_page_count, notify=selectionChanged)

    @Slot(str)
    def selectPage(self, page_id: str) -> None:
        """Open a page in the Viewer; guarded by dirty state (D05 §55)."""

        if page_id not in self._pages:
            return
        if not self._navigate({"kind": "page", "page_id": page_id}):
            return
        self._apply_viewer_page(page_id)

    @Slot(int)
    def stepPage(self, delta: int) -> None:
        """Move the Viewer page; QML only forwards the toolbar action."""

        count = self._page_model.rowCount()
        if count == 0:
            return
        current = self._page_model.row_index_of(self._viewer_page_id or "")
        next_row = max(0, min(count - 1, current + delta))
        page_id = self._page_model.page_id_at(next_row)
        if page_id is not None:
            self.selectPage(page_id)

    @Slot(str)
    def togglePageSelected(self, page_id: str) -> None:
        """Ctrl-click multi-select within the current chapter only."""

        if page_id not in self._pages:
            return
        self._page_model.toggle_selected(page_id)
        self._selection_anchor = page_id
        self.selectionChanged.emit()

    @Slot(str)
    def selectRangeTo(self, page_id: str) -> None:
        """Shift-click: extend a contiguous selection from the anchor."""

        if page_id not in self._pages or self._selection_anchor is None:
            self.togglePageSelected(page_id)
            return
        order = [
            row["page_id"]
            for row in sorted(self._pages.values(), key=lambda row: row["page_order"])
        ]
        start = order.index(self._selection_anchor)
        end = order.index(page_id)
        lo, hi = min(start, end), max(start, end)
        self._page_model.set_selected(order[lo : hi + 1])
        self.selectionChanged.emit()

    @Slot()
    def clearSelection(self) -> None:
        self._page_model.clear_selection()
        self._selection_anchor = None
        self.selectionChanged.emit()

    def _apply_viewer_page(self, page_id: str) -> None:
        if self._viewer_page_id != page_id:
            self._viewer_page_id = page_id
            self._load_inspector(page_id)
            self.viewerChanged.emit()

    # ------------------------------------------------------------------
    # filter + locate (AC-PROGRESS-003/004/005)
    # ------------------------------------------------------------------

    @Slot(str)
    def setPageFilter(self, kind: str) -> None:
        self._page_model.set_filter(kind)
        self.pageFilterChanged.emit()

    @Slot()
    def clearPageFilter(self) -> None:
        self.setPageFilter("all")

    @Slot(str)
    def filterByStatus(self, status: str) -> None:
        """TaskProgressPanel statistic click → PageList filter."""

        if status in ("failed", "completed", "skipped"):
            self.setPageFilter(status)
        else:
            self.setPageFilter("all")

    @Slot()
    def locatePipelinePage(self) -> None:
        """“点击当前 Page”→ PageList scroll + highlight (AC-PROGRESS-003)."""

        projection = self._projection
        if projection is None or not projection.current_page_id:
            return
        self.pageLocateRequested.emit(projection.current_page_id)

    # ------------------------------------------------------------------
    # viewer modes (D05 §20.1)
    # ------------------------------------------------------------------

    def get_viewer_mode(self) -> str:
        return self._viewer_mode

    def set_viewer_mode(self, mode: str) -> None:
        if mode not in VIEWER_MODES:
            raise ValueError(f"unknown viewer mode: {mode!r}")
        if self._viewer_mode != mode:
            self._viewer_mode = mode
            self.viewerChanged.emit()

    viewerMode = Property(str, get_viewer_mode, set_viewer_mode, notify=viewerChanged)

    @Slot(str)
    def setViewerMode(self, mode: str) -> None:
        self.set_viewer_mode(mode)

    def get_viewer_image_url(self) -> str:
        return self._image_url(self._viewer_page_id, self._viewer_mode)

    viewerImageUrl = Property(str, get_viewer_image_url, notify=viewerChanged)

    @Slot(str, result=str)
    def viewerImageUrlFor(self, mode: str) -> str:
        """Image URL of the current viewer page in an arbitrary mode
        (Compare pane needs the translated variant, D05 §20.1)."""

        return self._image_url(self._viewer_page_id, mode)

    @Slot(str, result=str)
    def viewerImageStateFor(self, mode: str) -> str:
        """Typed empty-state of the viewer image (TASK-051 AC ③):
        ``ok`` / ``missing`` / ``invalid`` — lets the VM tell "no data yet"
        from "path escaped the managed root" instead of collapsing both to
        a blank <Image>. QML presentation stays TASK-047-gated."""

        page_id = self._viewer_page_id
        if page_id is None:
            return "missing"
        state = getattr(self._page_catalog, "image_state", None)
        if state is None:
            return "missing"
        return str(state(page_id, mode))

    def get_command_error_text(self) -> str:
        return self._command_error_text

    commandErrorText = Property(
        str, get_command_error_text, notify=commandErrorChanged
    )

    @Slot()
    def clearCommandError(self) -> None:
        """Acknowledge the surfaced failure (TASK-052 AC ①)."""
        if self._command_error_text:
            self._command_error_text = ""
            self.commandErrorChanged.emit()

    def get_viewer_page_name(self) -> str:
        if self._viewer_page_id is None:
            return ""
        return self._pages.get(self._viewer_page_id, {}).get("filename", "")

    viewerPageName = Property(str, get_viewer_page_name, notify=viewerChanged)

    def _image_url(self, page_id: str | None, mode: str) -> str:
        if page_id is None:
            return ""
        resolver = getattr(self._page_catalog, "image_url", None)
        if resolver is not None:
            return str(resolver(page_id, mode))
        if mode != "original":
            return ""  # clean/translated artifacts do not exist in this slice
        ref = self._pages.get(page_id, {}).get("managed_original_ref", "")
        if not ref:
            return ""
        path = Path(ref)
        return path.as_uri() if path.is_absolute() else ""

    # ------------------------------------------------------------------
    # inspector + dirty guard (D05 §55)
    # ------------------------------------------------------------------

    def get_inspector_regions(self) -> list:
        page_id = self._viewer_page_id
        if page_id is None or self._region_catalog is None:
            return []
        regions = []
        for region in self._region_catalog.list_regions(page_id):
            regions.append(
                {
                    "region_id": region.region_id,
                    "reading_order": getattr(region, "reading_order", 0),
                    "region_type": getattr(region, "region_type", "speech"),
                    "ocr_text": getattr(region, "ocr_text", ""),
                    "translation": self._region_text(region),
                    "translation_locked": bool(
                        getattr(region, "translation_locked", False)
                    ),
                }
            )
        return regions

    inspectorRegions = Property(
        "QVariantList", get_inspector_regions, notify=inspectorChanged
    )

    @staticmethod
    def _region_text(region) -> str:
        for attr in ("final_translation", "edited_translation", "machine_translation"):
            value = getattr(region, attr, "")
            if value:
                return value
        return ""

    def get_inspector_region_id(self) -> str:
        return self._inspector_region_id or ""

    inspectorRegionId = Property(
        str, get_inspector_region_id, notify=inspectorChanged
    )

    def get_inspector_text(self) -> str:
        return self._inspector_text

    def set_inspector_text(self, text: str) -> None:
        if self._inspector_text != text:
            self._inspector_text = text
            if not self._inspector_dirty:
                self._inspector_dirty = True
                self.inspectorDirtyChanged.emit()

    inspectorText = Property(
        str, get_inspector_text, set_inspector_text, notify=inspectorDirtyChanged
    )

    @Slot(str)
    def setInspectorText(self, text: str) -> None:
        self.set_inspector_text(text)

    def get_has_dirty_editor(self) -> bool:
        return self._inspector_dirty

    hasDirtyEditor = Property(bool, get_has_dirty_editor, notify=inspectorDirtyChanged)

    @Slot(str)
    def selectRegion(self, region_id: str) -> None:
        if not self._navigate({"kind": "region", "region_id": region_id}):
            return
        self._apply_inspector_region(region_id)

    def _load_inspector(self, page_id: str) -> None:
        self._inspector_region_id = None
        self._inspector_saved_text = ""
        self._inspector_text = ""
        self._set_dirty(False)
        self.inspectorChanged.emit()

    def _apply_inspector_region(self, region_id: str) -> None:
        self._inspector_region_id = region_id
        region = (
            self._region_catalog.get_region(region_id)
            if self._region_catalog is not None
            else None
        )
        self._inspector_saved_text = self._region_text(region) if region else ""
        self._inspector_text = self._inspector_saved_text
        self._set_dirty(False)
        self.inspectorChanged.emit()

    @Slot()
    def saveInspector(self) -> None:
        if not self._inspector_dirty or self._inspector_region_id is None:
            return
        if self._translation_editor is None:
            self._record_command_error("no translation editor bound", stage="editor")
            return
        self._translation_editor.save_manual_translation(
            self._inspector_region_id, self._inspector_text
        )
        self._inspector_saved_text = self._inspector_text
        self._set_dirty(False)

    @Slot()
    def discardInspector(self) -> None:
        self._inspector_text = self._inspector_saved_text
        self._set_dirty(False)

    def _set_dirty(self, dirty: bool) -> None:
        if self._inspector_dirty != dirty:
            self._inspector_dirty = dirty
            self.inspectorDirtyChanged.emit()

    def _navigate(self, target: dict) -> bool:
        """Dirty navigation guard: switching page/region with unsaved
        inspector edits asks save/discard/cancel first (D05 §55)."""

        if not self._inspector_dirty:
            return True
        self._pending_navigation = target
        self.inspectorDirtyConfirmRequested.emit(target)
        return False

    @Slot(str)
    def resolveDirtyConfirm(self, action: str) -> None:
        """Finish a guarded navigation: save / discard / cancel."""

        target = self._pending_navigation
        self._pending_navigation = None
        if action == "cancel" or target is None:
            return
        if action == "save":
            self.saveInspector()
        else:
            self.discardInspector()
        if target["kind"] == "page":
            self._apply_viewer_page(target["page_id"])
        else:
            self._apply_inspector_region(target["region_id"])

    # ------------------------------------------------------------------
    # command entries (D05 §56 Screen-Action Map)
    # ------------------------------------------------------------------

    @Slot()
    def startTranslateAll(self) -> None:
        self._start_chapter_command(CommandType.TRANSLATE_ALL)

    @Slot()
    def startTranslateUntranslated(self) -> None:
        self._start_chapter_command(CommandType.TRANSLATE_UNTRANSLATED)

    @Slot()
    def startTranslateSelected(self) -> None:
        selected = self._page_model.get_selected_ids()
        if not selected:
            self._record_command_error("未选择任何 Page", stage="selection")
            return
        self._start_run(
            CommandType.TRANSLATE_SELECTED,
            PipelineScope(
                ScopeType.PAGE_SELECTION, selected_ids=tuple(selected)
            ),
        )

    @Slot(str)
    def startRegionCommand(self, command_type: str) -> None:
        region_id = self._inspector_region_id
        if not region_id:
            self._record_command_error("未选择 Region", stage="selection")
            return
        self._start_run(
            CommandType(command_type),
            PipelineScope(ScopeType.REGION, selected_ids=(region_id,)),
        )

    def _start_chapter_command(self, command: CommandType) -> None:
        if not self._chapter_id:
            self._record_command_error("尚未选择章节", stage="selection")
            return
        selected = self._page_model.get_selected_ids()
        if selected:
            self._start_run(
                command,
                PipelineScope(
                    ScopeType.PAGE_SELECTION, selected_ids=tuple(selected)
                ),
            )
        else:
            self._start_run(
                command, PipelineScope(ScopeType.CHAPTER, chapter_id=self._chapter_id)
            )

    def _start_run(self, command: CommandType, scope: PipelineScope) -> None:
        if self._restore_in_progress:
            # R-004 / review R-001: reject BEFORE create_run/plan_run —
            # those are writes too, so this path must not even build a run
            # object during a restore.  (The controller latch is the
            # second, birthplace-level net under this.)
            self._record_command_error("恢复进行中，不能启动任务", stage="run")
            return
        if self._controller.is_running:
            self._record_command_error("已有任务在运行", stage="run")
            return
        try:
            run = self._pipeline.create_run(command, scope)
            self._pipeline.plan_run(run.run_id)
        except PipelineError as error:
            self._record_command_error(error)
            return
        self._run = run
        self._pausing = False
        self._refresh_projection()
        if run.status is PipelineRunStatus.PENDING:
            self._start_pending_worker(run)
            self._refresh_from_run()

    # ------------------------------------------------------------------
    # restore gate (TASK-057 Q-008 前置① / TASK-061 R-004, three parts)
    # ------------------------------------------------------------------

    def beginRestore(self) -> bool:
        """Engage the restore latch; ``False`` while a run is executing.

        The three-part gate this participates in: (1) the run worker is
        drained — while a run is still executing ``beginRestore`` refuses
        (app-exit equivalently proves it via ``shutdown() is True``);
        (2) ``not any_in_transaction()`` is the *maintenance caller's*
        duty before calling this — the VM holds no connection handle,
        and the aggregate predicate is a snapshot, not an admission
        gate (R-004); (3) the latch itself lives on the controller and
        closes admission at ``RunController.start()`` — the sole worker
        birthplace, reached from all four VM call sites — until
        :meth:`endRestore` (review R-001).
        """
        if self._restore_in_progress:
            self._record_command_error("恢复已在进行中", stage="run")
            return False
        if self._controller.is_running:
            self._record_command_error("已有任务在运行，不能进入恢复", stage="run")
            return False
        self._controller.set_restore_latch(True)
        self._restore_in_progress = True
        return True

    def endRestore(self) -> None:
        """Release the restore latch — normal runs may start again."""
        self._controller.set_restore_latch(False)
        self._restore_in_progress = False

    @contextmanager
    def restoreGate(self) -> Iterator[None]:
        """Engage the latch for the duration of a restore body.

        Review R-002: an exception inside the body must not leave the
        workbench permanently closed — ``__exit__`` releases the latch
        unconditionally, so a failed restore cannot wedge every start
        path.  Entering refuses (``RuntimeError``) when a run is still
        executing, mirroring :meth:`beginRestore`.
        """
        if not self.beginRestore():
            raise RuntimeError(
                "cannot enter the restore gate: "
                + (self.commandErrorText or "a run is executing")
            )
        try:
            yield
        finally:
            self.endRestore()

    def _start_pending_worker(self, run: PipelineRun) -> None:
        """Birth the run worker through the controller's admission point.

        Sole choke point for the three control paths that reach
        ``controller.start`` directly (``continueRun``,
        ``_restart_or_abandon``, ``retryFailedPages`` — review R-001):
        while the restore latch holds, the controller raises
        :class:`RestoreLatchClosedError` and the refusal lands on the
        typed command-error surface with no worker born.
        """
        try:
            self._controller.start(self._pipeline, run)
        except RestoreLatchClosedError:
            self._record_command_error("恢复进行中，不能启动任务", stage="run")
            return
        self._progress_timer.start()

    # ------------------------------------------------------------------
    # run controls (D06 §103 button matrix)
    # ------------------------------------------------------------------

    @Slot()
    def pauseRun(self) -> None:
        if self._run is None:
            return
        if self._controller.is_running:
            # Optimistic feedback first: UI shows “正在暂停” immediately
            # even though the executor stops at the next safe boundary
            # (AC-PAUSE-001, AC-PAUSE-002).
            self._controller.request_pause(self._run)
            self._pausing = True
            self.taskProgressChanged.emit()
        else:
            try:
                self._pipeline.control_run(self._run.run_id, "pause")
            except PipelineError as error:
                self._record_command_error(error)
                return
            self._refresh_projection()

    @Slot()
    def stopRun(self) -> None:
        if self._run is None:
            return
        if self._controller.is_running:
            self._controller.request_stop(self._run)
            self._pausing = False
            self.taskProgressChanged.emit()
        else:
            try:
                self._pipeline.control_run(self._run.run_id, "stop")
            except PipelineError as error:
                self._record_command_error(error)
                return
            self._refresh_projection()

    @Slot()
    def continueRun(self) -> None:
        if self._run is None:
            return
        if self._restore_in_progress:
            self._record_command_error("恢复进行中，不能启动任务", stage="run")
            return
        try:
            result = self._pipeline.control_run(self._run.run_id, "continue")
        except PipelineError as error:
            self._record_command_error(error)
            return
        if result.new_run_id is not None:
            fresh = self._pipeline.plan_run(result.new_run_id)
            self._run = fresh
        self._refresh_projection()
        if self._run.status is PipelineRunStatus.PENDING:
            self._start_pending_worker(self._run)

    @Slot()
    def restartRun(self) -> None:
        self._restart_or_abandon("restart")

    @Slot()
    def abandonRun(self) -> None:
        self._restart_or_abandon("abandon")

    def _restart_or_abandon(self, action: str) -> None:
        if self._run is None:
            return
        if action == "restart" and self._restore_in_progress:
            self._record_command_error("恢复进行中，不能启动任务", stage="run")
            return
        try:
            result = self._pipeline.control_run(self._run.run_id, action)
        except PipelineError as error:
            self._record_command_error(error)
            return
        if action == "restart" and result.new_run_id is not None:
            fresh = self._pipeline.plan_run(result.new_run_id)
            self._run = fresh
            self._refresh_projection()
            if fresh.status is PipelineRunStatus.PENDING:
                self._start_pending_worker(fresh)
        else:
            self._refresh_projection()

    @Slot()
    def retryFailedPages(self) -> None:
        if self._run is None:
            return
        if self._restore_in_progress:
            self._record_command_error("恢复进行中，不能启动任务", stage="run")
            return
        try:
            fresh = self._pipeline.retry_failed_targets(self._run.run_id)
            self._pipeline.plan_run(fresh.run_id)
        except PipelineError as error:
            self._record_command_error(error)
            return
        self._run = fresh
        self._pausing = False
        self._refresh_projection()
        if fresh.status is PipelineRunStatus.PENDING:
            self._start_pending_worker(fresh)

    # ------------------------------------------------------------------
    # refresh plumbing
    # ------------------------------------------------------------------

    @Slot()
    def refreshProgress(self) -> None:
        """Manual refresh hook (tests, QML debug); production uses the
        4 Hz timer plus run-finished events."""

        self._refresh_from_run()

    def _refresh_from_run(self) -> None:
        if self._run is None:
            return
        self._refresh_projection()

    def _on_run_finished(self, run_id: str, status: str) -> None:
        self._pausing = False
        self._progress_timer.stop()
        # Key event: refresh immediately, not on the next throttle tick
        # (AC-PAUSE-001 / AC-PROGRESS-006).
        self._refresh_projection()
        self.runFinished.emit(run_id, status)

    def _record_command_error(
        self, error: BaseException | str, *, stage: str = "command"
    ) -> None:
        """Single sink for every command failure (TASK-052 AC ①③).

        PROVISIONAL minimal visibility: the machine-readable diagnosis
        (stage / error code) rides in the text itself and the latest
        failure stays bindable via ``commandErrorText`` until the
        TASK-047 design gate converges presentation and hierarchy. The
        legacy ``commandError`` signal keeps firing unchanged.
        """
        if isinstance(error, BaseException):
            code = getattr(error, "code", "") or type(error).__name__
            detail = getattr(error, "detail", "") or str(error)
            text = f"[{stage}/{code}] {detail}"
        else:
            detail = str(error)
            text = f"[{stage}] {detail}"
        self._command_error_text = text
        # the legacy signal keeps emitting the bare detail so existing
        # listeners (and their pinned assertions) stay byte-identical
        self.commandError.emit(detail)
        self.commandErrorChanged.emit()

    def _on_run_crashed(self, run_id: str, error: str) -> None:
        self._pausing = False
        self._progress_timer.stop()
        self._refresh_projection()
        self._record_command_error(error, stage="worker")

    def shutdown(self, wait_ms: int = 5000) -> bool:
        """Drain the run controller; True = drained (TASK-060 Q-003)."""
        self._progress_timer.stop()
        if self._run is not None and not is_terminal_status(
            self._run.status.value
        ):
            # TASK-060 Q-003: on exit there is no session to resume into.
            # A merely PAUSED run's worker has already left, so the
            # controller no longer holds it — the cancel request must be
            # written here, on the run object the VM still owns.
            self._run.cancel_requested = True
        return self._controller.shutdown(wait_ms)
