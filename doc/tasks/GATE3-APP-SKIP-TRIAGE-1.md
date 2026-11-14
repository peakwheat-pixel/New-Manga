---
id: GATE3-APP-SKIP-TRIAGE-1
title: App 4 个 with-fixture skip 归因 —— 2 个只是开关没开
kind: evidence
governance_version: 3
status: done
disposition: "实测：4 个 skip 里 2 个只需 opt-in 变量即可真实执行（已 passed），2 个需外部崩溃注入"
approval: DSH 2026-11-15
suggested_owner: DSH
owner: DSH
reviewer: null
depends_on:
  - E9-LIMITATION-DOC-1
base_commit: 6cc62dd01
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/GATE3-APP-SKIP-TRIAGE-1
allowed_paths:
  - doc/tasks/GATE3-APP-SKIP-TRIAGE-1.md
  - doc/reviews/GATE3-APP-SKIP-TRIAGE-1-*.md
  - doc/reviews/MAINT-1-GATE-CONDITION-3-MATRIX-2026-11-15.md
  - doc/REBASELINE_PLAN.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - doc/checkpoints/GOAL-PROGRESS-2026-11-02.md
  - verification/GATE3-APP-SKIP-TRIAGE-1/**
---

# GATE3-APP-SKIP-TRIAGE-1

## 结论

**4 个 with-fixture skip 里，2 个只是"opt-in 开关没开"，不是"跑不了"。**

| 测试 | 门禁 | 开开关后 |
|---|---|---|
| `RealProcessLaunchMatrix_…` | `NEWMANGA_FEA07_STARTUP_PROCESS=1` | **passed** |
| `Gated_HotSwitch_…` | `NEWMANGA_FEA07_PERF=1` | **passed**（21 s） |
| `Park_…` | `NEWMANGA_FEA07_CRASH=1` + `PHASE=park` + **`CRASH_ROOT`** | **failed**（需外部崩溃注入） |
| `Recover_…` | 同上 phase=recover | 未单独跑（同机制，**推断**） |

## 与 Host 44 个同型

大量 skip 是 **opt-in 门禁**，不是能力缺失。这与 `GATE3-HOST-SKIP-TRIAGE-1` 的结论一致。

## 未做

- 未把门禁改常开（那是 CI/产品策略；Perf 单测 21 s，开常开会显著拉长默认套件）。
- `Recover_…` 未单独实测。
- 基线未变化（953/0/11 无夹具、957/0/4 带夹具）。条件 3 仍不判 MET。
