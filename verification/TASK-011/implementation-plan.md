# Command Scheduler and Resumable Progress Implementation Plan

> **For agentic workers:** This plan is being executed inline on the fixed TASK-011 branch; no other Task is started.

**Goal:** Deliver the smallest deterministic command planner, scheduler, control surface, optimistic write guard, retry/recovery flow, and progress projection required by TASK-011 without changing shared Schema or Ports.

**Architecture:** Keep domain task records immutable where snapshots matter. Put the in-memory target/store seam and application orchestration inside the TASK-011 whitelist; injected catalog and step executor protocols make the behavior testable without inventing a database migration or bootstrap assembly. Every step records its start references and lock snapshot, then commits only after a second guard check.

**Tech Stack:** Python 3.12 standard library dataclasses, enums, typing Protocols, deepcopy, and pytest deterministic fakes.

**Spec:** `doc/contracts/TASK-002_MINIMUM_DATA_EXECUTION_CONTRACT.md`, `doc/06_TRANSLATION_PIPELINE.md`, and `doc/tasks/TASK-011.md`.

## Global Constraints

- Only edit `src/domain/tasks/**`, `src/application/tasks/**`, `src/application/translation/pipeline/**`, `tests/pipeline/**`, `doc/tasks/TASK-011.md`, `doc/handoffs/TASK-011-*.md`, and `verification/TASK-011/**`.
- Do not edit Schema/migrations, shared `src/ports/**`, bootstrap, dependency files, other Tasks, AGENTS, or frozen Tasks.
- Preserve source/Revision/Lock safety; context is read-only and only primary targets may be written.
- Report `passed` and `skipped` separately; every skip has a reason.

---

### Task 1: Define immutable task records and command vocabulary

**Files:**
- Create: `src/domain/tasks/models.py`
- Create: `src/domain/tasks/__init__.py`
- Test: `tests/pipeline/test_models.py`

**Interfaces:**
- Produces `CommandType`, `ScopeType`, `PipelineRunStatus`, `PipelineTaskStatus`, `StepRunStatus`, `PlanDecision`, `StageState`, `PipelineScope`, `TargetSnapshot`, `RunTarget`, `PipelineRun`, `PipelineTask`, `StepRun`, `StepResult`, `StepResultCandidate`, and progress DTOs.

- [x] **Step 1: Write failing model tests** for command catalog coverage, immutable snapshots, and terminal/progress status semantics.
- [x] **Step 2: Run `python -m pytest tests/pipeline/test_models.py -v` and observe the expected import failure.
- [x] **Step 3: Implement the smallest dataclasses/enums with defensive deep copies and tuple-backed collections.
- [x] **Step 4: Re-run the model tests and verify they pass.

### Task 2: Build an injectable in-memory target/store seam

**Files:**
- Create: `src/application/tasks/store.py`
- Create: `src/application/tasks/__init__.py`
- Test: `tests/pipeline/test_store.py`

**Interfaces:**
- Produces `TargetCatalog`, `SnapshotProvider`, `PipelineStore`, `InMemoryTargetCatalog`, `InMemorySnapshotProvider`, and `InMemoryPipelineStore`.

- [x] **Step 1: Write failing tests** for Book/Chapter/Page/Region expansion, deleted/empty target rejection, snapshot isolation, target mutation, and shared-store recovery.
- [x] **Step 2: Run `python -m pytest tests/pipeline/test_store.py -v` and verify failure is caused by missing store interfaces.
- [x] **Step 3: Implement only the catalog/store operations needed by the application service; keep all state in process and do not add schema code.
- [x] **Step 4: Re-run the store tests and verify they pass.

### Task 3: Implement planner, scheduler, controls, guards, retry, and progress

**Files:**
- Create: `src/application/tasks/service.py`
- Create: `src/application/translation/pipeline/__init__.py`
- Create: `src/application/translation/pipeline/executor.py`
- Test: `tests/pipeline/test_pipeline.py`

**Interfaces:**
- Produces `PipelineService`, `DeterministicStepExecutor`, `StepExecutor`, and the TASK-002 operations `create_run`, `plan_run`, `record_step_attempt`, `commit_step_result`, `control_run`, `retry_failed_targets`, `recover_running_runs`, and `get_task_progress`.

- [x] **Step 1: Write failing tests** for every command DAG, prerequisite reuse/stale rules, lock/SFX policy, provider blocking, deterministic success/failure, per-step guard conflicts, output mapping mismatch, pause/stop, crash Continue/Restart/Abandon, failed-page retry, and page progress.
- [x] **Step 2: Run focused tests and confirm the missing service failure.
- [x] **Step 3: Implement the minimal serial scheduler with one safe boundary between StepRuns, no background threads, and explicit resource limits.
- [x] **Step 4: Run focused tests, fix only production behavior, and verify all requested contract vectors pass.

### Task 4: Record evidence and handoff

**Files:**
- Modify: `doc/tasks/TASK-011.md`
- Create: `doc/handoffs/TASK-011-<short-head>.md`
- Create: `verification/TASK-011/tests-<short-head>.txt`

- [x] **Step 1: Run `python -m pytest tests/pipeline -v` on Windows with the repository Python 3.12 environment.
- [x] **Step 2: Record exact command, OS/runtime, exit code, separate passed/skipped counts, and skip reasons.
- [ ] **Step 3: Update only TASK-011 metadata and Handoff with the implementation commit and evidence links; leave `integration_commit` null until independent Review and Codex integration.
- [ ] **Step 4: Run `git diff --check` and verify changed paths are inside the whitelist.
