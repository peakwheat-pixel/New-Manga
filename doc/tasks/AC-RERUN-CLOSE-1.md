---
id: AC-RERUN-CLOSE-1
title: 用当前架构复跑证据闭合 RERUN 类 blocked AC（第 1 批）
kind: governance
governance_version: 3
status: in_progress
suggested_owner: DSH
owner: DSH
reviewer: null
depends_on:
  - AC-BLOCKED-CLASSIFY-1
approval: 用户 2026-11-15「全部授权、持续自动推进」；目标 C「AC blocked 项中可归因闭合项」
base_commit: 35a9f6c8d
branch: main
worktree: G:/CODEX/New Manga
evidence_dir: verification/AC-RERUN-CLOSE-1
allowed_paths:
  - doc/tasks/AC-RERUN-CLOSE-1.md
  - doc/tasks/M2-REGION-RETYPE-CORE.md
  - doc/tasks/TASK-056.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - verification/AC-RERUN-CLOSE-1/**
---

# AC-RERUN-CLOSE-1：复跑闭合 RERUN 类 blocked（第 1 批）

## 来源

`AC-BLOCKED-CLASSIFY-1` 把 72 条 `blocked` 逐条判定为 7 类，其中 `RERUN` 10 条
（「需在当前架构下复跑或复算」）是成本最低的可闭项。本卡执行第 1 批：跑测试补证据，据实改判。

## 目标（一个可观察结果）

2 条 `blocked` AC 因**当前架构下的实测复跑**而具备完整证据，改判为 `verified`；
其余 `RERUN` 项的状态与理由保持或如实更新（不为了「清零」而改判）。

## Acceptance Criteria

- [ ] **AC1 复跑证据**：至少产出 4 份实测日志——`M2-REGION-RETYPE-CORE` 的 11 断言套件、
  `TASK-056` 的 cleanup 套件、`CHAPTER-MANUAL-SORT` 的 chapter-reorder 套件、全仓 Python 套件；
  全部记录 passed/failed/skipped 与耗时。
- [ ] **AC2 改判 2 条**：`M2-REGION-RETYPE-CORE` AC3 与 `TASK-056` AC⑤ 由 `blocked` 改 `verified`，
  按 §4.3.1 形式（勾选 + `<!-- verified: … -->`，理由含具体日志路径与数字）。
- [ ] **AC3 不改无据项**：其余 `RERUN` 项（如 `CHAPTER-MANUAL-SORT` AC10 需 CoreClient、
  `TASK-056` AC①–④ 需装配接线、`MICA-FIX-1` AC2/AC4）**不得**因本卡改判——
  它们缺的不是「复跑」而是别的环节。
- [ ] **AC4 不回归**：两卡 `check.ps1 -TaskPath` PASS；全局 `check.ps1` PASS；
  `verify_pins.ps1` 18/18；`generate_api_inventory.py --check` 1/80/6=87；
  `verify_final.py` 计数从 `182 verified / 72 blocked` 变为 `184 / 70`（且 8 条先存 FAIL 不变）。
- [ ] **AC5 独立复核**：固定 head 交独立上下文 Review，报告落 workspace。

## 允许修改范围

见 frontmatter `allowed_paths`。要点：**只改这 2 张卡的 AC 注释，不动其它 AC**。

## 禁止范围

- 不得改未具备完整证据的 AC（含 `RERUN` 其余项）；
- 不得修改任何 `verification/**` 下既有证据文件内容（只新增本卡日志）；
- 不得为改判而放宽判据或把「部分满足」当「满足」。

## 测试要求

| 场景 | 命令 | 期望 |
|---|---|---|
| M2-REGION 11 断言 | `pytest tests/editing/test_region_retype.py tests/providers/test_retype_redetect_persistence.py tests/pipeline/test_retype_candidate_persistence.py` | 27 passed / 0 failed |
| TASK-056 cleanup | `pytest tests/maintenance/test_cleanup.py` | 12 passed |
| CHAPTER-MANUAL-SORT | `pytest tests/storage/test_chapter_reorder_atomic.py` | 5 passed |
| 全仓基线 | `pytest tests/ -q` | 3569 passed / 0 failed / 10 skipped |
| 四件套 | check / pins / inventory | PASS / 18-18 / 87 |

## 证据

实测日志与改判对照写入 `verification/AC-RERUN-CLOSE-1/`。
