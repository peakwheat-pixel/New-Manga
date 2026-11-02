"""P13 durable Run runtime acceptance, ownership, recovery and projection tests."""

from __future__ import annotations

import json
import io
import os
from pathlib import Path
import subprocess
import sys
from threading import Event, Thread
import time

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from application.tasks.service import PipelineService
from application.tasks.store import (
    InMemoryPipelineStore,
    InMemorySnapshotProvider,
    InMemoryTargetCatalog,
)
from application.translation.pipeline.executor import (
    DeterministicStepExecutor,
    StepExecutionError,
)
from bootstrap.core_service import (
    CoreServiceServer,
    PROTOCOL_MAJOR,
    PROTOCOL_MINOR,
    _RunSchedulerLease,
    assemble_production_core,
)
from domain.books.entities import Book, Chapter
from domain.pages.entities import Page
from domain.regions.entities import BBox, RegionGeometry
from domain.tasks.models import (
    CommandType,
    PipelineError,
    PipelineRunStatus,
    PipelineScope,
    PipelineTaskStatus,
    RegionSnapshot,
    ScopeType,
    StepResult,
    StepRunStatus,
)
from infrastructure.providers.retry import RetryPolicy, run_with_retry
from ports.providers.errors import (
    LockBlocked,
    MissingCredential,
    ProviderAuthenticationError,
    ProviderInputError,
    ProviderTimeout,
    ProviderRateLimited,
)
from ports.network.transport import TransportOutcome, TransportResponse


def _production_core(tmp_path: Path, page_order=(2, 1)):
    data_root = tmp_path / "data"
    core = assemble_production_core(data_root)
    core.repository.add_book(Book(book_id="book-p13", title="P13"))
    core.repository.add_chapter(
        Chapter(chapter_id="chapter-p13", book_id="book-p13", title="P13")
    )
    for index, sort_order in enumerate(page_order, start=1):
        core.repository.add_page(Page(
            page_id=f"page-{index}",
            chapter_id="chapter-p13",
            source_filename=f"{index}.png",
            source_order=index,
            sort_order=sort_order,
            source_hash=f"hash-{index}",
            source_size_bytes=1,
            width=10,
            height=10,
            managed_original_ref=f"books/book-p13/chapters/chapter-p13/{index}.png",
        ))
    return core


def _chapter_scope() -> PipelineScope:
    return PipelineScope(ScopeType.CHAPTER, chapter_id="chapter-p13")


def test_idempotency_ledger_is_additive_and_does_not_bump_schema_version(tmp_path):
    from infrastructure.sqlite.connection import open_database
    from infrastructure.sqlite.migrator import MigrationRunner, read_schema_version
    from infrastructure.sqlite.schema import default_migrations

    data_root = tmp_path / "data"
    db_path = data_root / "library.db"
    migrations = default_migrations()
    conn, _ = open_database(
        db_path,
        latest_known_schema_version=max(item.schema_version for item in migrations),
    )
    MigrationRunner(conn, migrations).apply_pending()
    version_before = read_schema_version(conn)
    assert conn.execute(
        "SELECT count(*) FROM sqlite_master WHERE type='table' "
        "AND name='pipeline_run_idempotency'"
    ).fetchone()[0] == 0
    conn.close()

    core = assemble_production_core(data_root)
    try:
        assert read_schema_version(core.conn) == version_before
        columns = {
            row["name"]
            for row in core.conn.execute("PRAGMA table_info(pipeline_run_idempotency)")
        }
        assert columns == {
            "idempotency_key", "request_fingerprint", "operation_type", "run_id", "created_at"
        }
        assert core.conn.execute(
            "SELECT count(*) FROM pipeline_run_idempotency"
        ).fetchone()[0] == 0
    finally:
        core.conn.close()


def _memory_pipeline(*, executor=None, provider_bindings=None):
    catalog = InMemoryTargetCatalog()
    catalog.add_page(
        "page-1",
        book_id="book-1",
        chapter_id="chapter-1",
        regions=(RegionSnapshot("region-1", "page-1"),),
    )
    store = InMemoryPipelineStore()
    pipeline = PipelineService(
        catalog,
        store=store,
        snapshots=InMemorySnapshotProvider(
            provider_bindings=provider_bindings or {}
        ),
        executor=executor,
    )
    return pipeline, store


def test_sqlite_start_acceptance_is_atomic_idempotent_and_freezes_targets(tmp_path):
    core = _production_core(tmp_path)
    try:
        pipeline = core.pipeline
        pipeline._snapshots = InMemorySnapshotProvider(
            settings={"mode": "frozen"},
            provider_bindings={"ocr": {"provider_id": "provider-a"}},
            context_policy={"scope": "frozen"},
        )
        scope = _chapter_scope()
        run, created = pipeline.accept_start_run(
            CommandType.TRANSLATE_ALL,
            scope,
            overrides={"settings": {"quality": "high"}},
            idempotency_key="start-key-1",
        )

        assert created is True
        assert [target.page_id for target in run.targets] == ["page-2", "page-1"]
        assert run.settings_snapshot == {"mode": "frozen", "quality": "high"}
        assert run.provider_binding_snapshot["ocr"]["provider_id"] == "provider-a"
        assert run.context_policy == {"scope": "frozen"}
        assert core.conn.execute(
            "SELECT count(*) FROM pipeline_run_targets WHERE pipeline_run_id = ?",
            (run.run_id,),
        ).fetchone()[0] == 2
        assert core.conn.execute(
            "SELECT count(*) FROM pipeline_run_idempotency WHERE idempotency_key = ?",
            ("start-key-1",),
        ).fetchone()[0] == 1

        core.repository.add_page(Page(
            page_id="page-3",
            chapter_id="chapter-p13",
            source_filename="3.png",
            source_order=3,
            sort_order=3,
            source_hash="hash-3",
            source_size_bytes=1,
            width=10,
            height=10,
            managed_original_ref="books/book-p13/chapters/chapter-p13/3.png",
        ))
        pipeline._snapshots.settings["mode"] = "changed"
        run.status = PipelineRunStatus.COMPLETED
        pipeline._store.put(run.run_id, run)

        replay, created = pipeline.accept_start_run(
            CommandType.TRANSLATE_ALL,
            scope,
            overrides={"settings": {"quality": "high"}},
            idempotency_key="start-key-1",
        )
        assert created is False
        assert replay.run_id == run.run_id
        assert replay.status is PipelineRunStatus.COMPLETED
        assert [target.page_id for target in replay.targets] == ["page-2", "page-1"]
        assert replay.settings_snapshot["mode"] == "frozen"

        with pytest.raises(PipelineError) as error:
            pipeline.accept_start_run(
                CommandType.TRANSLATE_ALL,
                scope,
                overrides={"settings": {"quality": "low"}},
                idempotency_key="start-key-1",
            )
        assert error.value.code == "IDEMPOTENCY_KEY_REUSED"
        assert pipeline._store.refresh(run.run_id).status is PipelineRunStatus.COMPLETED
        assert core.conn.execute(
            "SELECT count(*) FROM pipeline_runs WHERE run_id = ?", (run.run_id,)
        ).fetchone()[0] == 1

        data_root = core.data_root
        core.conn.close()
        core = assemble_production_core(data_root)
        replay, created = core.pipeline.accept_start_run(
            CommandType.TRANSLATE_ALL,
            scope,
            overrides={"settings": {"quality": "high"}},
            idempotency_key="start-key-1",
        )
        assert created is False
        assert replay.run_id == run.run_id
        assert replay.status is PipelineRunStatus.COMPLETED
        assert [target.page_id for target in replay.targets] == ["page-2", "page-1"]
    finally:
        core.conn.close()


def test_sqlite_acceptance_rolls_back_run_targets_and_key_together(tmp_path):
    core = _production_core(tmp_path)
    try:
        core.conn.execute(
            "CREATE TRIGGER reject_p13_key BEFORE INSERT ON pipeline_run_idempotency "
            "BEGIN SELECT RAISE(ABORT, 'injected acceptance failure'); END"
        )
        with pytest.raises(Exception, match="injected acceptance failure"):
            core.pipeline.accept_start_run(
                CommandType.TRANSLATE_ALL,
                _chapter_scope(),
                overrides={},
                idempotency_key="rollback-key",
            )

        assert core.conn.execute("SELECT count(*) FROM pipeline_runs").fetchone()[0] == 0
        assert core.conn.execute("SELECT count(*) FROM pipeline_run_targets").fetchone()[0] == 0
        assert core.conn.execute(
            "SELECT count(*) FROM pipeline_run_idempotency WHERE idempotency_key = ?",
            ("rollback-key",),
        ).fetchone()[0] == 0
    finally:
        core.conn.close()


def test_restart_sqlite_transaction_rolls_back_parent_child_and_key(tmp_path):
    core = _production_core(tmp_path)
    try:
        pipeline = core.pipeline
        parent = pipeline.create_run(CommandType.TRANSLATE_ALL, _chapter_scope())
        parent.status = PipelineRunStatus.INTERRUPTED
        pipeline._store.put(parent.run_id, parent)
        write_run = pipeline._store._write_run
        calls = 0

        def fail_after_child_write(run):
            nonlocal calls
            calls += 1
            write_run(run)
            if calls == 2:
                raise OSError("injected child write failure")

        pipeline._store._write_run = fail_after_child_write
        with pytest.raises(OSError, match="injected child write failure"):
            pipeline.control_run(
                parent.run_id, "restart", idempotency_key="restart-key"
            )
        pipeline._store._write_run = write_run

        persisted = pipeline._store.refresh(parent.run_id)
        assert persisted.status is PipelineRunStatus.INTERRUPTED
        assert persisted.interruption_disposition is None
        assert core.conn.execute(
            "SELECT count(*) FROM pipeline_runs WHERE source_run_id = ?",
            (parent.run_id,),
        ).fetchone()[0] == 0
        assert pipeline._store.get_idempotency("restart-key") is None

        result = pipeline.control_run(
            parent.run_id, "restart", idempotency_key="restart-key"
        )
        child = pipeline._store.refresh(result.new_run_id)
        assert child.source_run_id == parent.run_id
        assert child.retry_reason == "restart_after_interruption"
        assert pipeline._store.refresh(parent.run_id).interruption_disposition == "restarted"
        replay = pipeline.control_run(
            parent.run_id, "restart", idempotency_key="restart-key"
        )
        assert replay.new_run_id == child.run_id
    finally:
        core.conn.close()


def test_retry_failed_targets_is_durable_idempotent_and_uses_source_order(tmp_path):
    core = _production_core(tmp_path)
    try:
        pipeline = core.pipeline
        source = pipeline.create_run(CommandType.TRANSLATE_ALL, _chapter_scope())
        pipeline.plan_run(source.run_id)
        for task in source.tasks:
            task.status = PipelineTaskStatus.FAILED
            task.error_code = "PROVIDER_TIMEOUT"
        source.status = PipelineRunStatus.COMPLETED_WITH_FAILURES
        pipeline._store.put(source.run_id, source)

        child, created = pipeline.accept_retry_failed_targets(source.run_id, "retry-key")
        assert created is True
        assert child.source_run_id == source.run_id
        assert child.retry_reason == "retry_failed_targets"
        assert [target.page_id for target in child.targets] == ["page-2", "page-1"]
        replay, created = pipeline.accept_retry_failed_targets(source.run_id, "retry-key")
        assert created is False
        assert replay.run_id == child.run_id
        assert pipeline._store.refresh(source.run_id).status is PipelineRunStatus.COMPLETED_WITH_FAILURES

        data_root = core.data_root
        core.conn.close()
        core = assemble_production_core(data_root)
        replay, created = core.pipeline.accept_retry_failed_targets(source.run_id, "retry-key")
        assert created is False
        assert replay.run_id == child.run_id
    finally:
        core.conn.close()


def test_core_run_owner_uses_worker_thread_connection_and_blocks_direct_bypass(tmp_path):
    data_root = tmp_path / "data"
    core_a = _production_core(tmp_path)
    core_b = assemble_production_core(data_root)
    running, _ = core_a.pipeline.accept_start_run(
        CommandType.TRANSLATE_ALL,
        _chapter_scope(),
        overrides={},
        idempotency_key="startup-running",
    )
    running.status = PipelineRunStatus.RUNNING
    core_a.pipeline._store.put(running.run_id, running)
    paused, _ = core_a.pipeline.accept_start_run(
        CommandType.TRANSLATE_ALL,
        _chapter_scope(),
        overrides={},
        idempotency_key="startup-paused",
    )
    paused.status = PipelineRunStatus.PAUSED
    core_a.pipeline._store.put(paused.run_id, paused)
    server_a = CoreServiceServer(core_a)
    server_b = CoreServiceServer(core_b)
    try:
        server_a._start_run_scheduler()
        server_b._start_run_scheduler()
        assert server_a._run_owner is True
        assert server_b._run_owner is False
        assert core_a.pipeline.get_run_snapshot(running.run_id, fresh=True).status is PipelineRunStatus.INTERRUPTED
        assert core_a.pipeline.get_run_snapshot(paused.run_id, fresh=True).status is PipelineRunStatus.PAUSED

        deadline = time.monotonic() + 3
        while core_a.conn.registry_size() < 2 and time.monotonic() < deadline:
            time.sleep(0.01)
        assert core_a.conn.registry_size() >= 2

        with pytest.raises(PipelineError) as error:
            core_b.pipeline.execute_run("run-not-owned")
        assert error.value.code == "INVALID_RUN_TRANSITION"
        with pytest.raises(PipelineError) as error:
            core_b.pipeline.create_run(CommandType.TRANSLATE_ALL, _chapter_scope())
        assert error.value.code == "INVALID_RUN_TRANSITION"
    finally:
        server_b.close()
        server_a.close()
        core_b.conn.close()
        core_a.conn.close()


def test_kernel_scheduler_lease_excludes_a_second_process(tmp_path):
    lock_path = tmp_path / "library.db.run-owner.lock"
    script = (
        "import sys,time; from pathlib import Path; "
        "sys.path.insert(0, sys.argv[1]); "
        "from bootstrap.core_service import _RunSchedulerLease; "
        "lease=_RunSchedulerLease(Path(sys.argv[2])); "
        "assert lease.acquire(); print('ready', flush=True); "
        "sys.stdin.readline(); lease.release()"
    )
    child = subprocess.Popen(
        [sys.executable, "-c", script, str(SRC_ROOT), str(lock_path)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=os.environ.copy(),
    )
    try:
        assert child.stdout is not None
        assert child.stdout.readline().strip() == "ready"
        assert _RunSchedulerLease(lock_path).acquire() is False
    finally:
        if child.stdin is not None:
            child.stdin.write("release\n")
            child.stdin.flush()
        child.wait(timeout=5)

    lease = _RunSchedulerLease(lock_path)
    assert lease.acquire() is True
    lease.release()


def test_recovery_only_interrupts_running_and_continue_replays_open_step():
    executor = DeterministicStepExecutor()
    pipeline, store = _memory_pipeline(executor=executor)
    pending = pipeline.create_run(
        CommandType.OCR_REGION,
        PipelineScope(ScopeType.REGION, selected_ids=("region-1",)),
    )
    interrupted = pipeline.plan_run(
        pipeline.create_run(
            CommandType.OCR_REGION,
            PipelineScope(ScopeType.REGION, selected_ids=("region-1",)),
        ).run_id
    )
    task = interrupted.tasks[0]
    step = pipeline._record_step_attempt(
        interrupted, task, task.units[0], retry_no=0
    )
    interrupted.status = PipelineRunStatus.RUNNING
    store.put(interrupted.run_id, interrupted)

    assert pipeline.recover_running_runs() == (interrupted.run_id,)
    assert store.get(pending.run_id).status is PipelineRunStatus.PENDING
    recovered = store.get(interrupted.run_id)
    assert recovered.status is PipelineRunStatus.INTERRUPTED
    assert recovered.step_runs[0].status is StepRunStatus.INTERRUPTED

    pipeline.control_run(interrupted.run_id, "continue")
    assert store.get(interrupted.run_id).status is PipelineRunStatus.RUNNING
    assert pipeline.run_pending_once() is True
    assert pipeline.run_pending_once() is True
    resumed = store.get(interrupted.run_id)
    attempts = [item for item in resumed.step_runs if item.unit_id == step.unit_id]
    assert [item.retry_no for item in attempts] == [0, 1]
    assert attempts[0].status is StepRunStatus.INTERRUPTED
    assert attempts[1].status is StepRunStatus.COMPLETED


def test_continue_keeps_a_safely_committed_step_without_replaying_it():
    executor = DeterministicStepExecutor()
    pipeline, store = _memory_pipeline(executor=executor)
    run = pipeline.create_run(
        CommandType.TRANSLATE_ALL,
        PipelineScope(ScopeType.PAGE_SELECTION, selected_ids=("page-1",)),
    )
    pipeline.execute_run(run.run_id)
    completed_attempt_count = len(executor.calls)
    assert completed_attempt_count > 1
    run.status = PipelineRunStatus.RUNNING
    store.put(run.run_id, run)

    assert pipeline.recover_running_runs() == (run.run_id,)
    pipeline.control_run(run.run_id, "continue")

    assert store.get(run.run_id).status is PipelineRunStatus.COMPLETED
    assert len(executor.calls) == completed_attempt_count
    assert len(store.get(run.run_id).step_runs) == completed_attempt_count


def test_sqlite_step_commit_keeps_current_and_step_state_atomic(tmp_path):
    core = _production_core(tmp_path)
    try:
        region = core.editing.create_region(
            "page-1", RegionGeometry(bbox=BBox(1, 1, 5, 5))
        )
        run = core.pipeline.create_run(
            CommandType.OCR_REGION,
            PipelineScope(ScopeType.REGION, selected_ids=(region.region_id,)),
        )
        core.pipeline.plan_run(run.run_id)
        step = core.pipeline.record_step_attempt(run.tasks[0].task_id, "ocr")
        before = core.conn.execute(
            "SELECT current_revision_id FROM regions WHERE region_id = ?",
            (region.region_id,),
        ).fetchone()[0]
        store = core.pipeline._store
        write = store.write_in_current_transaction

        def fail_run_write(_run):
            raise OSError("injected commit-record failure")

        store.write_in_current_transaction = fail_run_write
        outcome = core.pipeline.commit_step_result(
            step.step_run_id,
            StepResult(
                target_id=region.region_id,
                step_type="ocr",
                outputs={"text": "temporary"},
            ),
        )
        store.write_in_current_transaction = write

        assert outcome.status == "failed"
        assert outcome.error_code == "DB_FAILED"
        assert core.conn.execute(
            "SELECT current_revision_id FROM regions WHERE region_id = ?",
            (region.region_id,),
        ).fetchone()[0] == before
        assert core.conn.execute(
            "SELECT count(*) FROM pipeline_stage_states WHERE target_type='region' "
            "AND target_id = ? AND stage='ocr'", (region.region_id,),
        ).fetchone()[0] == 0
        persisted = store.refresh(run.run_id)
        assert persisted.step_runs[0].status is StepRunStatus.FAILED
        assert persisted.step_runs[0].error_code == "DB_FAILED"
    finally:
        core.conn.close()


def test_projection_is_same_run_source_and_never_exposes_error_detail():
    pipeline, _ = _memory_pipeline(provider_bindings={
        "ocr": {"provider_id": "safe-provider", "model_id": "safe-model", "device": "cuda"}
    })
    run = pipeline.create_run(
        CommandType.OCR_REGION,
        PipelineScope(ScopeType.REGION, selected_ids=("region-1",)),
    )
    pipeline.plan_run(run.run_id)
    task = run.tasks[0]
    step = pipeline.record_step_attempt(task.task_id, "ocr", retry_no=2)
    step.status = StepRunStatus.FAILED
    step.error_code = "PROVIDER_TIMEOUT"
    step.error_detail = "C:\\private\\key.txt token=secret"
    task.status = PipelineTaskStatus.FAILED
    task.error_code = "PROVIDER_TIMEOUT"
    task.error_detail = step.error_detail
    run.status = PipelineRunStatus.COMPLETED_WITH_FAILURES

    projection = pipeline.get_task_projection(run.run_id)
    wire = CoreServiceServer._task_projection_to_wire(projection)
    task_wire = projection.tasks[0]
    step_wire = task_wire.steps[0]
    assert projection.rows[0].page_id == task_wire.page_id
    assert step_wire.retry_no == 2
    assert (step_wire.provider, step_wire.model, step_wire.device) == (
        "safe-provider", "safe-model", "cuda"
    )
    assert task_wire.error_message is None
    assert step_wire.error_message is None
    assert "secret" not in repr(projection)
    assert "C:\\private" not in repr(projection)
    assert wire["tasks"][0]["steps"][0]["retry_no"] == 2
    assert wire["tasks"][0]["steps"][0]["error_message"] is None
    assert "secret" not in json.dumps(wire)


def test_retry_policy_uses_two_bounded_retries_and_fail_closed_codes():
    calls = 0
    delays = []

    def transient_call():
        nonlocal calls
        calls += 1
        if calls < 3:
            raise ProviderTimeout("temporary")
        return "ok"

    outcome = run_with_retry(
        transient_call,
        RetryPolicy(),
        sleep=delays.append,
        provider_id="provider-a",
    )
    assert outcome.result == "ok"
    assert calls == 3
    assert delays == [1.0, 2.0]

    for error in (
        ProviderAuthenticationError("unauthorized"),
        ProviderInputError("invalid"),
        MissingCredential("missing"),
        LockBlocked("protected"),
    ):
        attempts = 0
        sleeps = []

        def non_retryable_call(error=error):
            nonlocal attempts
            attempts += 1
            raise error

        with pytest.raises(type(error)):
            run_with_retry(non_retryable_call, RetryPolicy(), sleep=sleeps.append)
        assert attempts == 1
        assert sleeps == []


def test_retry_after_is_not_capped_and_runtime_version_is_major_two():
    from infrastructure.providers.retry import _retry_after_seconds
    from infrastructure.providers.runtime import _RetryAfterTransport, _retry_policy

    assert _retry_after_seconds("7") == 7.0
    assert _retry_after_seconds("7200") == 7200.0
    assert _retry_after_seconds("nonsense") is None
    policy = _retry_policy({"providers": {"retry": {"max_attempts": 8}}})
    assert policy.max_attempts == 3
    assert policy.backoff_seconds == 1.0
    assert (PROTOCOL_MAJOR, PROTOCOL_MINOR) == (2, 3)

    class Transport:
        calls = 0

        def send(self, request, profile):
            del request, profile
            self.calls += 1
            response = TransportResponse(
                status=429 if self.calls == 1 else 200,
                headers={"Retry-After": "7"} if self.calls == 1 else {},
            )
            return TransportOutcome(response)

    transport = _RetryAfterTransport(Transport())
    delays = []

    def send_with_status_check():
        outcome = transport.send(None, None)
        if outcome.response.status == 429:
            raise ProviderRateLimited("rate limited")
        return outcome.response.status

    outcome = run_with_retry(
        send_with_status_check,
        RetryPolicy(retry_after_provider=transport.consume),
        sleep=delays.append,
    )
    assert outcome.result == 200
    assert delays == [7.0]


def test_event_sink_emits_only_after_lifecycle_state_changes():
    entered = Event()
    release = Event()
    executor = DeterministicStepExecutor(on_execute=lambda *_: (entered.set(), release.wait(2)))
    pipeline, _ = _memory_pipeline(executor=executor)
    events = []
    pipeline.set_event_sink(lambda kind, payload: events.append((kind, dict(payload))))
    run = pipeline.create_run(
        CommandType.OCR_REGION,
        PipelineScope(ScopeType.REGION, selected_ids=("region-1",)),
    )
    worker = Thread(target=lambda: pipeline.execute_run(run.run_id))
    worker.start()
    try:
        assert entered.wait(2)
        pipeline.control_run(run.run_id, "pause")
    finally:
        release.set()
        worker.join(timeout=3)
    assert not worker.is_alive()
    assert any(kind == "CurrentPageStepChanged" for kind, _ in events)
    assert any(kind == "RunPaused" for kind, _ in events)

    pipeline.control_run(run.run_id, "continue")
    assert pipeline.run_pending_once() is True
    assert any(kind == "RunCompleted" for kind, _ in events)

    failed_pipeline, _ = _memory_pipeline(
        executor=DeterministicStepExecutor(fail_on={("region-1", "ocr"): "PROVIDER_TIMEOUT"})
    )
    failed_events = []
    failed_pipeline.set_event_sink(lambda kind, payload: failed_events.append(kind))
    failed = failed_pipeline.create_run(
        CommandType.OCR_REGION,
        PipelineScope(ScopeType.REGION, selected_ids=("region-1",)),
    )
    failed_pipeline.execute_run(failed.run_id)
    assert "TaskFailed" in failed_events
    assert "RunCompleted" in failed_events


def test_start_run_wire_uses_key_separate_from_request_id_and_returns_snapshot(tmp_path):
    core = _production_core(tmp_path)
    server = CoreServiceServer(core, stdout=io.StringIO())

    def request(request_id, command, payload):
        return server.dispatch_request(json.dumps({
            "protocol": "new-manga.core",
            "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
            "request_id": request_id,
            "command": command,
            "payload": payload,
        }))[0]

    start = {
        "command": CommandType.TRANSLATE_ALL.value,
        "scope": {"kind": "chapter", "chapter_id": "chapter-p13"},
        "overrides": {},
        "idempotency_key": "wire-key",
    }
    try:
        first = request("request-a", "StartRun", start)
        second = request("request-b", "StartRun", start)
        assert first["error"] is None and second["error"] is None
        assert first["request_id"] == "request-a"
        assert second["request_id"] == "request-b"
        assert first["result"]["run_id"] == second["result"]["run_id"]

        snapshot = request(
            "request-c", "GetRunSnapshot", {"run_id": first["result"]["run_id"]}
        )
        assert snapshot["error"] is None
        assert snapshot["result"]["scope"] == start["scope"]
        assert [row["order"] for row in snapshot["result"]["targets"]] == [0, 1]

        conflict = request("request-d", "StartRun", {
            **start,
            "overrides": {"settings": {"quality": "different"}},
        })
        assert conflict["error"]["code"] == "IDEMPOTENCY_KEY_REUSED"
        assert conflict["error"]["message"] == "Idempotency key was used for a different request"
    finally:
        server.close()
        core.conn.close()


def test_task_projection_polling_is_rate_limited_but_reads_fresh_runs(tmp_path):
    core = _production_core(tmp_path)
    run, _ = core.pipeline.accept_start_run(
        CommandType.TRANSLATE_ALL,
        _chapter_scope(),
        overrides={},
        idempotency_key="projection-key",
    )
    server = CoreServiceServer(core, stdout=io.StringIO())
    original = core.pipeline.get_task_projection
    reads = []

    def tracked(run_id, *, fresh=False):
        reads.append(fresh)
        return original(run_id, fresh=fresh)

    core.pipeline.get_task_projection = tracked
    try:
        first = server._cached_task_projection(run.run_id)
        second = server._cached_task_projection(run.run_id)
        assert first == second
        assert reads == [True]
        server._emit_run_event("RunPaused", {"run_id": run.run_id, "status": "paused"})
        server._cached_task_projection(run.run_id)
        assert reads == [True, True]
    finally:
        server.close()
        core.conn.close()
