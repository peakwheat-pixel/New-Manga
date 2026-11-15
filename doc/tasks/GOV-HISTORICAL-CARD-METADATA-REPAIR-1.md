---
id: GOV-HISTORICAL-CARD-METADATA-REPAIR-1
title: 修复 6 张 gv3 历史卡的卡面元数据缺陷（使 check.ps1 -TaskPath 全 PASS）
kind: governance
governance_version: 3
status: done
suggested_owner: DSH
owner: DSH
reviewer: cardmeta-review（独立上下文子 agent，APPROVED_WITH_LIMITATIONS）
integration_commit: 25da646e0
canonical_evidence_status: complete
resource_closeout_status: complete
depends_on:
  - GOV-CHECKER-HISTORICAL-AC-EXEMPT-1
  - AC-CHECKBOX-AUTHORITY-1
approval: 用户 2026-11-15「全部授权、持续自动推进」；由 AC-CHECKBOX-AUTHORITY-1 的独立复核 ac-review-r1 的 P2-04 与该卡 §7.9 登记
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

- [x] **AC1 6 卡全 PASS**：`check.ps1 -TaskPath` 对 6 张卡均 PASS（此前 5 张 FAIL）。 <<MET>>
- [x] **AC2 改动面最小**：`git diff` 只涉及上述两表的行；AC 行、frontmatter `status`、正文结论零改动（独立复核 r1 逐行确认；另含防台账过期的 `doc/TASK_LEDGER.md`）。 <<MET>>
- [x] **AC3 登记真实**：每条新登记项的 path 实际存在；sha256 为 `git cat-file blob` 原始字节的 SHA-256，且能被 `check.ps1` 的 OR 判据（工作区/commit blob）接受（独立复核逐项验证 16 条全部一致）。 <<MET>>
- [x] **AC4 不引入假登记**：不把不存在或已清理的资源写成存在；`worktree/branch` 用真实路径而非散文（复核确认 `git worktree list` 存在、`merge-base --is-ancestor` 为真）。 <<MET>>
- [x] **AC5 不回归**：全局 `check.ps1` PASS(3 warnings)｜`verify_pins.ps1` 18/18｜`generate_api_inventory.py --check` 1/80/6=87。 <<MET>>
- [x] **AC6 证据与独立复核**：`verification/GOV-HISTORICAL-CARD-METADATA-REPAIR-1/` 含改动前后对照与 6 卡 PASS 输出；已交独立上下文复核 `cardmeta-review`，verdict **APPROVED_WITH_LIMITATIONS**（P0/P1/P2/P3 = 0/0/3/5），P2-01/02/03 已在收口时处置。 <<MET>>

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

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class | sha256_basis |
|---|---|---|---|---|---|---|
| EV-GHC-01 | AC1/AC2/AC4 证据总述 | verification/GOV-HISTORICAL-CARD-METADATA-REPAIR-1/README.md | 25da646e0 | 10c38735fe7d046efd4f2d8b34ce09d95f4dc392f3bf178a5ccbb34507822398 | CANONICAL | BLOB |
| EV-GHC-02 | AC1 6 卡 PASS 实测输出 | verification/GOV-HISTORICAL-CARD-METADATA-REPAIR-1/after.txt | 25da646e0 | 742be3f7a0feffd9e41e292f2804873d7078d6bfb263261f402f5644581db1e1 | CANONICAL | BLOB |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | verification/GOV-HISTORICAL-CARD-METADATA-REPAIR-1/ | NOT_APPLICABLE | — | — | 新增证据，无迁移/归档 |

## Closeout Record

- Closeout：2026-11-15，DSH；integration commit `25da646e0`。
- **结果**：6 张 gv3 历史终态卡 `check.ps1 -TaskPath` **全部 PASS**（修复前 5 张 FAIL）。
- **独立复核**：`cardmeta-review`（未参与实现）verdict **APPROVED_WITH_LIMITATIONS**
  （P0/P1/P2/P3 = 0/0/3/5）：6 卡实跑 PASS、改动面只在两表、16 条登记 sha 全部一致、未发现伪造。
  - P2-01（台账提交版与重算不一致）→ 收口时重跑 `task_ledger.py --write` 消除；
  - P2-02（README 改动面数字有误）→ 已更正为 9 文件 / 224+/10−；
  - P2-03（本卡非终态未登记 DAG）→ 由本卡标 `done` 消解（同 `GOV-CHECKER-HISTORICAL-AC-EXEMPT-1` 先例）；
  - P3-01（FEA-07 新 pin 在 `core.autocrlf=true` 全新检出下会失配）→ 已给该行补 commit `61e324e1d`，
    使 checker 可回退到 blob 校验（实测 `blob@61e324e1d` 的 sha = `2407dd2c…`）。
- **门禁**：`check.ps1` PASS (3 warnings)｜`verify_pins.ps1` PASS (18/18)｜
  `generate_api_inventory.py --check` OK (1/80/6=87)。
- **未关闭项（不淡化）**：
  1. `FEA-07-AC5-NATIVE-1` 的 `EV-AC5-P05` **ID 在卡内重复**（`DEFECTS.md` 与
     `evidence/physical-state-after-…` 共用）；本次只更新前者 sha，未改 ID，建议后续清理。
  2. `FEA-07` 仍有 4 warnings（`evidence_dir` 下 99 个文件未逐条登记，checker 只打印前 8 个）——
     该卡既有，非本次引入。
  3. 本修复只消除**检查器缺陷**，不代表这些历史卡有新证据；其 AC 的 `blocked` 项仍为 `blocked`。
  4. `MICA-FIX-1` 的 `sha256/manifest` 填的是资源本体（`solid.bmp`）而非独立 manifest 指纹
     （该 task-env 无 manifest 文件）；属可接受的最小实现，记录待规范化。
