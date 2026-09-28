---
id: DIAG-M2-REGIONLESS-LOCK-CHANGED-001
title: M2 regionless planner LOCK_CHANGED diagnosis
kind: research
status: done
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
delivery_head: 7a03ac5f9677c359c6e13c007d77d46e604e8df0
review: doc/reviews/DIAG-M2-REGIONLESS-LOCK-CHANGED-001-7a03ac5f.md (approved)
integration_merge: b5ac097f98d9c06e2548c69d7361d475c0f13388
dispatch_state: INTEGRATED
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
- 当前状态：`done / INTEGRATED`。Owner=DeepSeek Harness 以文本交付静态诊断（headless 沙箱无 shell、无法写 worktree，环境错误逐字节记录于 dispatch 存档），集成方（ZCode 代行 Codex，用户授权 2026-09-28）按 M2-C2 先例原字节 import 落盘并代跑验证命令：`reproduce.py` 判定 `DEFECT_REPRODUCED`（8/8 checks PASS、EXIT=0，先红达成）、既有受影响 pytest 9 passed EXIT=0、`git diff --check` EXIT=0；delivery head=`7a03ac5f9677c359c6e13c007d77d46e604e8df0`（Owner branch 单 commit import，base=5789b30b）。Antigravity 非作者 Review=[approved](../reviews/DIAG-M2-REGIONLESS-LOCK-CHANGED-001-7a03ac5f.md)（四轴 executed、AC1–AC5 全 PASS、0×P0/P1/P2、2×P3 观察、独立复跑一致）。Codex（代行）集成 merge=`b5ac097f98d9c06e2548c69d7361d475c0f13388`（parents `1103f3d1`+`7a03ac5f`，8 文件纯新增无冲突），集成 head 复跑 reproduce 8/8 PASS、pytest 9 passed 均 EXIT 0；记录：[integration-b5ac097f](../../verification/DIAG-M2-REGIONLESS-LOCK-CHANGED-001/integration-b5ac097f/integration.md)。诊断结论：根因=`_backfill_detected_regions` 只重绑 `region_id` 未重绑 `target_id`（`src/application/tasks/service.py:921-946`），OCR 守卫以 `None` 比对 Region 真实 current revision ⇒ `LOCK_CHANGED`（`step_writes.py:219-231`）；修复仅限该函数同时重绑两 id 且不改 `unit_id`，须另立 Task 释放（M2-P1 候选）。
