---
id: GOV-HISTORICAL-CARD-METADATA-REPAIR-1
title: 修复 6 张 gv3 历史卡的卡面元数据缺陷（使 check.ps1 -TaskPath 全 PASS）
kind: governance
governance_version: 3
status: in_progress
suggested_owner: DSH
owner: DSH
reviewer: null
depends_on:
  - GOV-CHECKER-HISTORICAL-AC-EXEMPT-1
  - AC-CHECKBOX-AUTHORITY-1
approval: 用户 2026-11-15「全部授权、持续自动推进」；由独立复核 ac-review-r1 的 P2-04 与任务卡 §7.9 登记
base_commit: ed8b56c9f
branch: main
worktree: G:/CODEX/New Manga
evidence_dir: verification/GOV-HISTORICAL-CARD-METADATA-REPAIR-1
allowed_paths:
  - doc/tasks/GOV-HISTORICAL-CARD-METADATA-REPAIR-1.md
  - doc/tasks/CHAPTER-MANUAL-SORT.md
  - doc/tasks/FEA-04.md
  - doc/tasks/FEA-07-AC5-NATIVE-1.md
  - doc/tasks/MICA-FIX-1.md
  - doc/tasks/RELEASE-PACKAGE-1.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - verification/GOV-HISTORICAL-CARD-METADATA-REPAIR-1/**
---

# GOV-HISTORICAL-CARD-METADATA-REPAIR-1：历史卡元数据缺陷修复

## 来源

`GOV-CHECKER-HISTORICAL-AC-EXEMPT-1` 消除了 6 张 gv3 历史终态卡的 **AC 门禁**错误后，
`check.ps1 -TaskPath` 仍因**卡面元数据**缺陷 FAIL（`GATE3-COVERAGE-MATRIX` 除外）：

| 卡 | 缺陷 |
|---|---|
| `CHAPTER-MANUAL-SORT` | `evidence_dir` 含 2 个未登记文件（`four-pieces.log`、`pending-host-cache-test.cs.txt`） |
| `FEA-04` | ① `E-SCOPE` 路径 `doc/reviews/FEA-04-scope-r1/r2/r3.md` 不存在（实为 3 个独立文件）；② `evidence_dir` 含 11 个未登记日志；③ `worktree/branch` 的 `sha256/manifest` 列是散文而非路径 |
| `RELEASE-PACKAGE-1` | `task-env` 的 `sha256/manifest` = 「待填」 |
| `MICA-FIX-1` | 同上 |
| `FEA-07-AC5-NATIVE-1` | `DEFECTS.md` 的 sha256 与当前 blob 不匹配（`be905e0c…` vs `2407dd2c…`） |

## 目标（一个可观察结果）

6 张卡的 `check.ps1 -TaskPath` 全部 **PASS**；且只改 `Canonical Evidence` / `Resource Manifest` 两张表，
**不动 AC 正文、`status`、结论与其它章节**。

## Acceptance Criteria

- [ ] **AC1 6 卡全 PASS**：`check.ps1 -TaskPath` 对 6 张卡均 PASS（此前 5 张 FAIL）。
- [ ] **AC2 改动面最小**：`git diff` 只涉及上述两表的行；AC 行、frontmatter `status`、正文结论零改动。
- [ ] **AC3 登记真实**：每条新登记项的 path 实际存在；sha256 为 `git cat-file blob` 原始字节的 SHA-256，
      且能被 `check.ps1` 的 OR 判据（工作区/commit blob）接受。
- [ ] **AC4 不引入假登记**：不把不存在或已清理的资源写成存在；`worktree/branch` 用真实路径而非散文。
- [ ] **AC5 不回归**：全局 `check.ps1` PASS(3 warnings)｜`verify_pins.ps1` 18/18｜
      `generate_api_inventory.py --check` 1/80/6=87。
- [ ] **AC6 证据与独立复核**：`verification/GOV-HISTORICAL-CARD-METADATA-REPAIR-1/` 含改动前后对照
      与 6 卡 PASS 输出；固定 head 交独立上下文 Review。

## 允许修改范围

见 frontmatter `allowed_paths`。要点：**只改 5 张卡的 `Canonical Evidence` / `Resource Manifest` 表**。

## 禁止范围

- 不得改任何 AC 行、`status`、`verdict`/结论、Handoff 与 Review 记录；
- 不得改 `verification/**` 下的证据文件本身（只登记，不改内容）；
- 不得为通过检查而伪造资源存在性（不存在就如实写不存在或改 disposition）；
- 不得改其它卡。

## 测试要求

| 场景 | 命令 | 期望 |
|---|---|---|
| 6 卡 | `check.ps1 -TaskPath doc/tasks/<CARD>.md` ×6 | 全 PASS |
| 全局 | `check.ps1` | PASS (3 warnings) |
| pins / inventory | `verify_pins.ps1` / `generate_api_inventory.py --check` | 18/18 / OK |
| 改动面 | `git diff --stat` | 仅 5 个卡文件 + 本卡 + 证据 |

## 证据

结果与逐项对照写入 `verification/GOV-HISTORICAL-CARD-METADATA-REPAIR-1/`。
