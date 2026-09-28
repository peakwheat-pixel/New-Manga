---
id: DIAG-M2-REGIONLESS-LOCK-CHANGED-001
title: M2 regionless planner LOCK_CHANGED diagnosis
kind: research
status: ready
release_state: M2_REGIONLESS_LOCK_CHANGED_DIAGNOSTIC_RELEASED
approval: approved_by_user_2026-09-28_rebaseline_orchestration
execution_approval: approved_by_user_2026-09-28_rebaseline_orchestration
suggested_owner: DeepSeek Harness
owner: DeepSeek Harness
reviewer: Antigravity
integrator: Codex
depends_on: [M2-AC1]
base_commit: 5789b30b37dfbf79d9bca707b5fdaaa562ada707
branch: agent/deepseek/DIAG-M2-REGIONLESS-LOCK-CHANGED-001
worktree: G:/CODEX/New Manga.worktrees/DIAG-M2-REGIONLESS-LOCK-CHANGED-001-dsh
dispatch_state: AWAITING_EXTERNAL_DISPATCH
---

# DIAG-M2-REGIONLESS-LOCK-CHANGED-001

## 目标

在新架构 Python Core 的真实 SQLite 与 production Pipeline seam 上，稳定复现 regionless page 经 `detect → backfill → ocr` 后以 `LOCK_CHANGED` 结束的问题，固定根因、影响边界与最小修复范围。本 Task 只诊断，不修改产品代码。

M2-AC1 已于 `f162193b` 集成，但其样本预先创建 Region，没有覆盖 regionless 路径。Owner=DeepSeek Harness；非作者 Reviewer=Antigravity；Integrator=Codex。

## Acceptance Criteria

- [ ] **AC1 — 可复现：** 使用临时 SQLite、production Pipeline 装配和成功的确定性 detector/OCR，在 regionless page 上稳定复现最终 `LOCK_CHANGED`；保存可独立运行的复现脚本及先红日志。
- [ ] **AC2 — 状态链：** 记录 detect 前后 `PlanUnit.target_id/region_id/unit_id`、`StepRun.input_refs/lock_snapshot`、catalog current 状态及最终错误，证明错误发生的具体比较点。
- [ ] **AC3 — 反事实分析：** 说明 Region 创建后正确 snapshot/rebind 应发生的位置，并分析多 Region fan-out、终态计数和进程重启恢复的影响；不得用单 Region 特例掩盖这些语义。
- [ ] **AC4 — 修复建议：** 报告最小产品修复路径、需要修改的共享 seam、回归与负向测试矩阵、持久化/恢复风险；任何修复必须由后续 Task 单独释放。
- [ ] **AC5 — 证据纪律：** 所有命令记录 shell、解释器、固定 HEAD、EXIT；`FAIL`、`BLOCKED`、`NOT_RUN` 分开报告。提交 Handoff 并固定可供非作者 Review 的 delivery head。

## 允许修改范围

- `doc/tasks/DIAG-M2-REGIONLESS-LOCK-CHANGED-001.md`
- `doc/research/DIAG-M2-REGIONLESS-LOCK-CHANGED-001.md`
- `verification/DIAG-M2-REGIONLESS-LOCK-CHANGED-001/**`
- `doc/handoffs/DIAG-M2-REGIONLESS-LOCK-CHANGED-001-*.md`

## 禁止范围

- `src/**`、`apps/**`、`tests/**`、`doc/contracts/**`
- SQLite schema/migration、依赖或 lockfile、打包配置、Legacy PySide6/QML
- 任何产品修复、共享接口变更或对其他 M2 Acceptance Backlog 行的完成声明

若复现必须修改产品或测试代码，停止并在报告中给出理由，由 Codex 另行释放修复 Task。

## 验证命令

在固定 worktree 根目录执行；`$py` 必须解析为 `G:\CODEX\New Manga.task-envs\TASK-012-py312\Scripts\python.exe`。

```powershell
& $py verification/DIAG-M2-REGIONLESS-LOCK-CHANGED-001/reproduce.py
& $py -m pytest tests/providers/test_detect_handler.py tests/providers/test_bootstrap_providers.py -q
git diff --check 5789b30b37dfbf79d9bca707b5fdaaa562ada707..<delivery-head>
```

首条命令为本 Task 必须新增并执行的复现入口；第二条只读复跑既有受影响测试；第三条校验交付范围。环境不具备时标 `BLOCKED`，不得从静态阅读推断 PASS。

## 交付

- 诊断报告：`doc/research/DIAG-M2-REGIONLESS-LOCK-CHANGED-001.md`
- 原始日志与复现脚本：`verification/DIAG-M2-REGIONLESS-LOCK-CHANGED-001/`
- Handoff：`doc/handoffs/DIAG-M2-REGIONLESS-LOCK-CHANGED-001-<short-head>.md`
- 当前状态：`ready / AWAITING_EXTERNAL_DISPATCH`；branch/worktree 路径已冻结，待 Codex 或执行方从固定 base 创建。
