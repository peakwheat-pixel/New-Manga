"""Background execution of PipelineService runs (TASK-013, AC-NFR-UI-001).

``PipelineService.execute_run`` is a synchronous loop; running it on the
GUI thread would freeze Page switching, scrolling and the settings page
while OCR/translation/inpaint mocks execute. ``RunController`` moves the
call to a QThread worker.

Control requests (pause/stop) are the contract's flag writes on the run
object (``pause_requested`` / ``cancel_requested``), checked by the
executor at its safe boundaries (AC-PAUSE-002); a boolean flag write is
atomic under the GIL, and the executor only ever reads it, so no lock is
needed. Completion is reported back on the GUI thread via a queued
``finished`` signal.
"""

from __future__ import annotations

from PySide6.QtCore import QObject, QThread, Signal, Slot

from domain.tasks.models import PipelineRun, PipelineRunStatus


class _Worker(QObject):
    """Runs inside the QThread; one execution per worker."""

    started = Signal(str)
    finishedRun = Signal(str, str)  # run_id, final status value
    crashed = Signal(str, str)  # run_id, error text

    @Slot(object)
    def execute(self, job: dict) -> None:
        service: object = job["service"]
        run: PipelineRun = job["run"]
        self.started.emit(run.run_id)
        try:
            final = service.execute_run(run.run_id)
        except Exception as error:  # defensive: never kill the thread silently
            self.crashed.emit(run.run_id, str(error))
            return
        self.finishedRun.emit(run.run_id, final.status.value)


class RunController(QObject):
    """Owns the worker thread for the workbench's current run."""

    runStarted = Signal(str)
    runFinished = Signal(str, str)  # run_id, final status value
    runCrashed = Signal(str, str)

    # Emitted on the GUI thread; the queued connection delivers the job to
    # the worker thread's event loop. (Connecting a lambda straight to
    # QThread.started runs it on the *sender's* thread — the GUI thread —
    # so the job must travel through a signal instead.)
    _startRequested = Signal(object)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._thread: QThread | None = None
        self._worker: _Worker | None = None
        self._active_run: PipelineRun | None = None

    # ------------------------------------------------------------------
    # lifecycle
    # ------------------------------------------------------------------

    @property
    def is_running(self) -> bool:
        return self._active_run is not None

    @property
    def active_run_id(self) -> str | None:
        return self._active_run.run_id if self._active_run else None

    def start(self, service, run: PipelineRun) -> None:
        if self.is_running:
            raise RuntimeError("a run is already executing on this controller")
        self._active_run = run
        self._thread = QThread(self)
        self._worker = _Worker()
        self._worker.moveToThread(self._thread)
        self._startRequested.connect(self._worker.execute)  # queued → worker
        self._worker.finishedRun.connect(self._on_finished)
        self._worker.crashed.connect(self._on_crashed)
        self._thread.start()
        self._startRequested.emit({"service": service, "run": run})
        self.runStarted.emit(run.run_id)

    def request_pause(self, run: PipelineRun) -> None:
        """Executor checks this at the next safe boundary (AC-PAUSE-002)."""

        run.pause_requested = True

    def request_stop(self, run: PipelineRun) -> None:
        run.cancel_requested = True

    def shutdown(self, wait_ms: int = 5000) -> None:
        if self._thread is not None:
            if (
                self._active_run is not None
                and self._active_run.status is not PipelineRunStatus.PAUSED
            ):
                self._active_run.cancel_requested = True
            self._thread.quit()
            if not self._thread.wait(wait_ms):
                # R-001: never force-kill an in-flight worker.  This slice has
                # no durable transaction boundary; before persistence is
                # connected, replace this fallback with an acknowledged
                # safe-boundary shutdown protocol.
                return
            self._thread.deleteLater()
            self._thread = None
        if self._worker is not None:
            self._worker.deleteLater()
            self._worker = None
        self._active_run = None

    # ------------------------------------------------------------------
    # worker callbacks (queued onto the GUI thread)
    # ------------------------------------------------------------------

    def _on_finished(self, run_id: str, status: str) -> None:
        was_running = self._active_run is not None
        self.shutdown()
        if was_running:
            self.runFinished.emit(run_id, status)

    def _on_crashed(self, run_id: str, error: str) -> None:
        self.shutdown()
        self.runCrashed.emit(run_id, error)


def is_terminal_status(status: str) -> bool:
    return status in {
        PipelineRunStatus.COMPLETED.value,
        PipelineRunStatus.COMPLETED_WITH_FAILURES.value,
        PipelineRunStatus.FAILED.value,
        PipelineRunStatus.CANCELLED.value,
    }
