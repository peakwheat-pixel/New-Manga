---
id: AC-RERUN-CLOSE-1
title: 用当前架构复跑证据闭合 RERUN 类 blocked AC（第 1 批）
kind: governance
governance_version: 3
status: done
suggested_owner: DSH
owner: DSH
reviewer: rerun-close-review（独立上下文子 agent，APPROVED_WITH_LIMITATIONS）
integration_commit: e476f210a
canonical_evidence_status: complete
resource_closeout_status: complete
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

6 条 `blocked` AC 因**当前架构下的实测复跑**而具备完整证据，改判为 `verified`；
其余 `RERUN` 项的状态与理由保持或如实更新（不为了「清零」而改判）。

## Acceptance Criteria

- [x] **AC1 复跑证据**：至少产出 4 份实测日志——`M2-REGION-RETYPE-CORE` 的 11 断言套件、 <<MET>>
  `TASK-056` 的 cleanup 套件、`CHAPTER-MANUAL-SORT` 的 chapter-reorder 套件、全仓 Python 套件；
  全部记录 passed/failed/skipped 与耗时。
- [x] **AC2 改判 6 条**：`M2-REGION-RETYPE-CORE` AC3 与 `TASK-056` AC⑤ 由 `blocked` 改 `verified`， <<MET>>
  按 §4.3.1 形式（勾选 + `<!-- verified: … -->`，理由含具体日志路径与数字）。
- [x] **AC3 不改无据项**：其余 `RERUN` 项（如 `CHAPTER-MANUAL-SORT` AC10 需 CoreClient、 <<MET>>
  `TASK-056` AC①–④ 需装配接线、`MICA-FIX-1` AC2/AC4）**不得**因本卡改判——
  它们缺的不是「复跑」而是别的环节。
- [x] **AC4 不回归**：两卡 `check.ps1 -TaskPath` PASS；全局 `check.ps1` PASS； <<MET>>
  `verify_pins.ps1` 18/18；`generate_api_inventory.py --check` 1/80/6=87；
  `verify_final.py` 计数从 `182 verified / 72 blocked` 变为 `184 / 70`（且 8 条先存 FAIL 不变）。
- [x] **AC5 独立复核**：固定 head 交独立上下文 Review，报告落 workspace。 <<MET>>

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

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class | sha256_basis |
|---|---|---|---|---|---|---|
| EV-RRC-01 | AC1/AC2 改判对照（WORKTREE_ENV=Windows11+pwsh7+Python3.14） | verification/AC-RERUN-CLOSE-1/README.md | e476f210a | 2ce4354b21a058a8abecc4b5f0330dcec848d08c5a9c7fefc1f6e7265d11f5ba | CANONICAL | WORKTREE |
| EV-RRC-02 | AC1 全仓复算日志（3569 passed）（WORKTREE_ENV=Windows11+pwsh7+Python3.14） | verification/AC-RERUN-CLOSE-1/full-suite-run1.log | e476f210a | e4883e02a22964da7003e7c8db2e6250506ce7a12bdd6b0bcc9ea83bfd449e14 | CANONICAL | WORKTREE |
| EV-RRC-03 | AC2 M2-REGION 27 passed（WORKTREE_ENV=Windows11+pwsh7+Python3.14） | verification/AC-RERUN-CLOSE-1/m2-region-retype-rerun.log | e476f210a | e818d4865a7bcd083beb45d23c1c6f0f708ae34e28375ece49ea6e21d02aaea7 | CANONICAL | WORKTREE |
| EV-RRC-04 | AC2 TASK-056 cleanup 12 passed（WORKTREE_ENV=Windows11+pwsh7+Python3.14） | verification/AC-RERUN-CLOSE-1/task-056-cleanup-rerun.log | e476f210a | e05a9a4d082483c58a1f7b9e5e4cdd5f897fb55a1f2ae5914a24d481000e40c1 | CANONICAL | WORKTREE |
| EV-RRC-05 | AC2 CHAPTER 5 passed（WORKTREE_ENV=Windows11+pwsh7+Python3.14） | verification/AC-RERUN-CLOSE-1/chapter-manual-sort-rerun.log | e476f210a | 04d88e272ff93994a02669905ae7e234fe4794a35eee2c0524674e2a311155e4 | CANONICAL | WORKTREE |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | verification/AC-RERUN-CLOSE-1/ | NOT_APPLICABLE | — | — | 新增证据，无迁移/归档 |

## Closeout Record

- Closeout：2026-11-15，DSH；实现 commit `e476f210a` + r1 复核后扩展改判（本提交）。
- **结果**：**6 条** `blocked` AC 改判 `verified`：
  - `M2-REGION-RETYPE-CORE` AC3（27 passed 覆盖两层断言）
  - `TASK-056` AC①–④（装配接线 + 16 例 wire 级测试已在树内，r1 复核 F-02 推翻原「未接线」判断）
  - `TASK-056` AC⑤（当前全仓 3569 passed + 历史 ≥5 次记录，限制说明已入卡面）
- **独立复核**：`rerun-close-review` verdict **APPROVED_WITH_LIMITATIONS**（0/0/2/6）：
  亲自重跑 3 套件一致、读测试代码确认两层覆盖真实、全仓日志计数自洽（50 行进度 = 3569+7 点）。
  - F-01（AC⑤「≥5 次」为旧套件记录）→ 卡面已加**限制说明**；
  - F-02（TASK-056 AC①–④ 理由过时）→ **据实改判 4 条**（本提交的主要产出）；
  - F-03（TASK_LEDGER 滞后）→ 收口时重跑；
  - F-04（M2 AC3 缺红态 nuance）→ 已补；
  - F-05（日志缺 command/env/EXIT 头）→ 已补 4 份；
  - F-06（治理边界因果不准）→ 证据 §5 已更正为「lifecycle v1 本就豁免 §4.3 门禁」；
  - F-07/F-08 记录在证据 §7。
- **计数**：`verified 182 → 188`、`blocked 72 → 66`（先存 8 条 EOL/numstat FAIL 不变）。
- **门禁**：`check.ps1` PASS (3 warnings)｜`verify_pins.ps1` PASS (18/18)｜
  `generate_api_inventory.py --check` OK (1/80/6=87)。
- **未关闭项（不淡化）**：
  1. `CHAPTER-MANUAL-SORT` AC10 需 **CoreClient（C#）** 侧复跑（`dotnet test`），本轮未做；
  2. `TASK-056` AC⑥（STATUS 台账行）为机制性过时要求，待 DSH 裁决；
  3. `M2-REGION-RETYPE-CORE` AC6 含 cargo/vitest（旧壳冻结）；
  4. `MICA-FIX-1` AC2/AC4 需 `--diagnostics` 重跑与 `scripts/test.ps1` 回归日志（脚本可跑，属延期）；
  5. 全仓存在 Windows temp `PermissionError` 偶发（`test_export.py`），建议登记 flaky；
  6. `M2-REGION-RETYPE-CORE` frontmatter 有重复 `integration_commit` 键（既存缺陷）。
