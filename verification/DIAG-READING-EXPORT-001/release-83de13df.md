# DIAG-READING-EXPORT-001 Release Record

- **Decision:** User asked Codex on 2026-09-27 to decide from the live Plan/STATUS and, if safe, register and release a bounded Task under collaboration protocol §5.1. Codex released this separate read-only diagnosis.
- **Task:** [DIAG-READING-EXPORT-001](../../doc/tasks/DIAG-READING-EXPORT-001.md)
- **Release state:** `ready / READ_ONLY_DIAGNOSTIC_RELEASED`
- **Owner / non-author Reviewer / Integrator:** DeepSeek Harness / Codex / Codex
- **Dependencies:** `[]`. This diagnostic is outside M2 and T3.2.1. No M2 successor or product implementation is released.
- **Fixed recovery point:** `main@83de13dfe0521125715c2e26da75b96a63103938`; Owner must preserve this start commit.
- **Registration/release commit:** `ceab572bf7b552f2e5f708193b4e8af7931badd2`; it records the Task as `ready`. The Owner copies only `doc/tasks/DIAG-READING-EXPORT-001.md` from this commit into the fixed-base worktree before claiming.
- **Owner branch/worktree:** `agent/deepseek/DIAG-READING-EXPORT-001-reading-export-flaky-diagnosis` / `C:/Users/49745/.codex/worktrees/diag-reading-export-001/New Manga`. Created clean at the fixed base before dispatch.
- **Allowed paths:** the Task status/record, its new diagnosis report and Handoff, and `verification/DIAG-READING-EXPORT-001/**` only.

## Scope and start gate

The Task diagnoses the historical `exportFinished`/`settleReadingTime`/SQLite connection-lifetime flaky. It does not authorize a repair, production code, test edits, dependencies, Schema, Domain Contract, M2-I1/I2, or T3.2.1 changes.

Before running tests, DeepSeek Harness must claim the Task on its fixed-base branch and freeze one supported project Python environment that imports PySide6. Record OS/shell, absolute Python and versions, pytest, PySide6/Qt, SQLite, `openssl`, and `QT_QPA_PLATFORM`. Keep that environment constant for all runs. If a supported PySide6 environment cannot be established, stop, record the evidence and mark the Task `blocked`; missing-dependency skips are not a pass.

## Frozen verification

The Task freezes a maximum of 15 independent pytest runs: full suite once, target file three times, target test five times, and the reader/export file pair three times in each collection order. Exact commands, run IDs and artifact requirements are in the Task. Save raw stdout/stderr and `EXIT` for every run; no retries beyond the matrix without a Codex scope decision. At most two isolated read-only probes may be used. Never edit production/test files or suppress an initial failure.

Completion Gate: report and evidence reconcile; run count is within the frozen matrix (or the environment gate has evidence-backed blocked status); no unauthorized path changed; DeepSeek Harness Handoff is complete; Codex performs non-author Review and integration. `NOT_RUN`, `BLOCKED`, skips and non-reproduction stay explicit.

## Recovery and dispatch instruction

Owner must not merge the governance/release commit into the fixed-base branch. Copy only `doc/tasks/DIAG-READING-EXPORT-001.md` from release commit `ceab572bf7b552f2e5f708193b4e8af7931badd2` into the Owner worktree, commit the `ready` → `in_progress` claim, and then perform the environment startup Gate. Do not run the test matrix before that claim.

> DeepSeek Harness：请执行 `DIAG-READING-EXPORT-001` 只读诊断。仓库为 `G:/CODEX/New Manga`，固定 `base/head=83de13dfe0521125715c2e26da75b96a63103938`；Owner branch=`agent/deepseek/DIAG-READING-EXPORT-001-reading-export-flaky-diagnosis`，worktree=`C:/Users/49745/.codex/worktrees/diag-reading-export-001/New Manga`。非作者 Reviewer 与 Integrator 均为 Codex，依赖为空。先只复制释放提交中的 `doc/tasks/DIAG-READING-EXPORT-001.md` 到该 worktree，将状态改为 `in_progress` 并提交 claim；不要合并释放提交，不要提前跑测试。先按 Task 冻结并检查同一支持 PySide6 的 Python 环境；无法满足则留证并标记 `blocked`。通过后，严格按 Task 中的 15-run 固定矩阵执行，原样保存每次 stdout/stderr/命令/EXIT，最多两个只读隔离探针。只允许修改该 Task 状态、报告 `doc/research/DIAG-READING-EXPORT-001.md`、自己的 Handoff 与 `verification/DIAG-READING-EXPORT-001/**`；禁止改生产代码、测试、依赖、Schema、Contract、M2 产品路径或 T3.2.1。交付诊断报告、`environment.txt`、`matrix.tsv`、逐次 `run-*.log` 和 Handoff，逐项说明根因假设、证伪探针、失败/skip/NOT_REPRODUCED/阻塞及风险。不得实现修复或将未验证项写成 PASS。

## Dispatch channel status

The Codex app exposes no active DeepSeek Harness connector or matching task thread to receive this instruction directly. The Task is registered and `ready`, with the complete forwardable instruction above; the instruction still needs delivery to DeepSeek Harness. No implementation or diagnostic run has started.
