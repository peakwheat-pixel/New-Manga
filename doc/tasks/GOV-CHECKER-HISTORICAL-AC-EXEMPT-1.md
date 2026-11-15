---
id: GOV-CHECKER-HISTORICAL-AC-EXEMPT-1
title: check.ps1 为历史终态卡的 §4.3.1 注释形式提供豁免（不削弱现行门禁）
kind: governance
governance_version: 3
status: in_progress
suggested_owner: DSH
owner: DSH
reviewer: null
depends_on:
  - AC-CHECKBOX-AUTHORITY-1
approval: 用户 2026-11-15「全部授权、持续自动推进」；独立复核 ac-review-r1 §P2-04 指出该缺口
base_commit: b8113e740
branch: main
worktree: G:/CODEX/New Manga
evidence_dir: verification/GOV-CHECKER-HISTORICAL-AC-EXEMPT-1
allowed_paths:
  - doc/tasks/GOV-CHECKER-HISTORICAL-AC-EXEMPT-1.md
  - doc/09_COLLABORATION.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - tools/governance/check.ps1
  - verification/GOV-CHECKER-HISTORICAL-AC-EXEMPT-1/**
---

# GOV-CHECKER-HISTORICAL-AC-EXEMPT-1：历史终态卡的 §4.3.1 豁免

## 来源

`AC-CHECKBOX-AUTHORITY-1` 完成后，`doc/09_COLLABORATION.md` §4.3.1 为存量卡引入行内 HTML 注释标注
（`<!-- verified|not-applicable|blocked: … -->`）。但 `tools/governance/check.ps1` 的 lifecycle v3 门禁
（`:921` 起）仍要求 AC 行末为 `<<MET|PARTIAL|BLOCKED|NOT_APPLICABLE>>`，导致 6 张
`governance_version: 3` 的历史终态卡在 `check.ps1 -TaskPath` 下全部 FAIL：

| 卡 | 报错 |
|---|---|
| `CHAPTER-MANUAL-SORT`、`FEA-04`、`GATE3-COVERAGE-MATRIX`、`RELEASE-PACKAGE-1`、`MICA-FIX-1` | AC 标记缺失 5–10 条 + 「DONE 不能保留未完成 AC」 |
| `FEA-07-AC5-NATIVE-1`（closed_with_limitations） | AC 标记缺失 5 条 |

该 FAIL 在 §4.3.1 引入前同样存在（当时无任何标记），**不是回归**；但 §4.3 与 §4.3.1 两套口径并存需要
显式豁免才能自洽（独立复核 `ac-review-r1` 的 P2-04）。

## 目标（一个可观察结果）

对**含 §4.3.1 HTML 注释且为 gv3 终态**的卡，`check.ps1 -TaskPath` 按 §4.3.1 口径校验并 PASS；
对**不含**该注释的 gv3 终态卡，仍按现行 §4.3 口径 FAIL（门禁不被削弱）。

## Acceptance Criteria

- [x] **AC1 识别与分派**：`check.ps1` 能判定「该卡使用 §4.3.1 HTML 注释形式」，且仅当 <<MET>>
      `governance_version: 3` 且 `status ∈ {done, closed_with_limitations}` 时启用豁免；其它情况一律走原 §4.3 逻辑。
- [x] **AC2 §4.3.1 校验规则**：豁免路径校验四件事——① 每个 AC 行都有三种注释之一；② `verified`/`not-applicable` <<MET>>
      必须 `[x]`、`blocked` 必须 `[ ]`；③ 注释原因非空；④ 裸 `[x]` 必须报错。
- [x] **AC3 DONE-未完成豁免**：豁免卡不再触发「DONE 不能保留未完成 Acceptance Criteria」（§4.3.1 明确允许 <<MET>>
      `blocked` 的 AC 保持 `[ ]`）；非豁免卡行为不变。
- [x] **AC4 6 卡 AC 门禁归零**：`check.ps1 -TaskPath` 对上述 6 张卡的 **AC 门禁相关错误**（`AC 状态标记缺失` 40 条 + `DONE 不能保留未完成 AC` 5 条 = **45 条**）归零，`GATE3-COVERAGE-MATRIX` 由 FAIL 变 PASS；其余 FAIL 若为各卡独立的既有缺陷（evidence_dir 未登记 / Resource manifest 待填 / Canonical 路径缺失 / SHA 不匹配）逐卡登记、不由本 Task 修复。 <<MET>>
- [x] **AC5 不削弱（反例实测）**：对**无 HTML 注释**的 gv3 终态卡（如 `ADJ-B-RESTART-HINT-1`） <<MET>>
      `-TaskPath` 仍 FAIL，证明门禁未被放宽。
- [x] **AC6 全局不回归**：`check.ps1` 全局 PASS 且 warning 数不变；`verify_pins.ps1` 18/18； <<MET>>
      `generate_api_inventory.py --check` `1/80/6=87`。
- [x] **AC7 文档同步**：`doc/09_COLLABORATION.md` §4.3.1「已知门禁边界」段更新为「本 Task 已消除该缺口， <<MET>>
      判据为 HTML 注释形式」。
- [x] **AC8 证据与独立复核**：`verification/GOV-CHECKER-HISTORICAL-AC-EXEMPT-1/` 含改动前后对照、
      反例输出、边界用例、四件套结果；已交独立上下文复核 `gcheck-review`（未参与实现），verdict
      `APPROVED_WITH_LIMITATIONS`（P0/P1/P2/P3 = 0/0/3/4），其 R-01…R-06 均已处置、R-07 由收口解决。 <<MET>>

## 允许修改范围

见 frontmatter `allowed_paths`。要点：只改 `check.ps1` 的 AC 门禁分支与其所需的辅助判定；
不改其它检查项、不降级任何既有报错。

## 禁止范围

- **不得**放宽对**当前活跃 Task**（`in_progress`/`in_review`/`approved`）的 §4.3 门禁。
- **不得**删除或绕过 §4.3 的 `<<...>>` 校验分支，只能新增分派。
- **不得**改任何历史卡的 AC、`status` 或注释内容。
- 不得改 pin、契约、`doc/tasks/` 下除本卡外的任何文件。

## 测试要求

| 场景 | 命令 | 期望 |
|---|---|---|
| 6 卡回归 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/<CARD>.md` × 6 | PASS（改动前 FAIL） |
| 反例 | `... -TaskPath doc/tasks/ADJ-B-RESTART-HINT-1.md` | 仍 FAIL（AC 标记缺失） |
| 全局 | `pwsh -NoProfile -File tools/governance/check.ps1` | PASS (3 warnings) |
| pins / inventory | `verify_pins.ps1` / `generate_api_inventory.py --check` | 18/18 / OK |

## 证据

`Canonical Evidence` 与 `Resource Manifest` 在完成后补入；结果写入
`verification/GOV-CHECKER-HISTORICAL-AC-EXEMPT-1/README.md`。
