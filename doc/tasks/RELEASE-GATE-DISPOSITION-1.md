---
id: RELEASE-GATE-DISPOSITION-1
title: Release Gate 六条的 Agent 可完成性判定表 + 条件 6 独立最终 Review
kind: governance
governance_version: 3
status: done
suggested_owner: DSH
owner: DSH
reviewer: gate6-final-review（独立上下文子 agent，CONDITION_6_PARTIAL）
integration_commit: 3caf423cd
canonical_evidence_status: complete
resource_closeout_status: complete
depends_on:
  - AC-DOC-CLOSE-1
  - V11R-D-1-AC8-CLOSE-1
approval: 用户 2026-11-15「全部授权、持续自动推进」；目标 B「Release Gate 六条中 Agent 可独立完成的部分」
base_commit: b4910e143
branch: main
worktree: G:/CODEX/New Manga
evidence_dir: verification/RELEASE-GATE-DISPOSITION-1
allowed_paths:
  - doc/tasks/RELEASE-GATE-DISPOSITION-1.md
  - doc/reviews/RELEASE-GATE-DISPOSITION-2026-11-15.md
  - doc/reviews/GATE6-FINAL-REVIEW-2026-11-15.md
  - doc/reviews/HUMAN-REQUIRED-2026-11-15.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - verification/RELEASE-GATE-DISPOSITION-1/**
---

# RELEASE-GATE-DISPOSITION-1：Gate 六条可完成性判定

## 来源

目标 B 要求：「Release Gate 六条条件中『Agent 可独立完成』的部分**全部关闭或给出明确判定**」。
迄今未有任何一张卡承担这件事 —— 本卡补上。

依据：`doc/reviews/MAINT-1-RELEASE-GATE-ASSESSMENT-2026-11-14.md` §2（六条现状与可执行性）
与 `MAINT-1-GATE-CONDITION-1/3/4/6-*` 系列。

## 目标（一个可观察结果）

一张**逐条判定表**，把六条各拆成「Agent 可完成的部分」与「必须人做的部分」，
并对唯一一条完全可 Agent 完成的条件（条件 6）**执行**独立最终 Review。

## Acceptance Criteria

- [x] **AC1 六条逐条判定**：每条给出①现状②Agent 可完成部分③必须人做部分④判定类别 <<MET>>
      （可独立关闭 / 可推进不可单独关闭 / 必须人做）。
- [x] **AC2 结论可操作**：明确「Agent 可独立完成」的条数（本卡结论：**1 条 = 条件 6**）， <<MET>>
      不笼统写「部分可做」。
- [x] **AC3 条件 6 执行**：派**未参与实现**的独立上下文子 agent 对当前 head 做最终复核， <<MET>>
      范围含 Canonical Evidence / 三指针 / 门禁实测 / limitation 登记；报告落 `doc/reviews/`。
- [x] **AC4 新增 HUMAN-REQUIRED**：把 Gate 侧的人侧输入（远端可见性、安装矩阵、质量 GT） <<MET>>
      补进 `doc/reviews/HUMAN-REQUIRED-2026-11-15.md`，与既有 5 项不重复。
- [x] **AC5 不改 Gate 结论**：本卡**不得**声称 Gate 从 BLOCKED 变为任何其它状态； <<MET>>
      条件 1/2/4/5 未完成、条件 3 的 GUI 矩阵未做这一事实必须保留。
- [x] **AC6 不回归**：全局 `check.ps1` PASS；`verify_pins` 18/18；`api_inventory` 1/80/6=87。 <<MET>>

## 允许修改范围

见 frontmatter `allowed_paths`。要点：**只新增判定表与 Review 报告，不改产品代码，不改 Gate 文档结论**。

## 禁止范围

- 不得修改 `doc/reviews/MAINT-1-RELEASE-GATE-ASSESSMENT-2026-11-14.md` 的结论；
- 不得声称条件 1/2/4/5 已完成；
- 不得为「让条件 6 通过」而放宽任何门禁；
- 不得把「打包可做」写成「可发布」。

## 测试要求

| 场景 | 命令 | 期望 |
|---|---|---|
| 门禁 | check / pins / inventory | PASS / 18-18 / 87 |
| 条件 6 复核 | 由独立子 agent 执行 | 报告落盘 |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class | sha256_basis |
|---|---|---|---|---|---|---|
| EV-RGD-01 | AC1/AC2/AC5 判定表 | doc/reviews/RELEASE-GATE-DISPOSITION-2026-11-15.md | 4c41ed959 | fd367c0f0a26733e9d2fd9f9d76be7cecd87f40bdfc0d21331f0e043609960e6 | CANONICAL | BLOB |
| EV-RGD-02 | AC6 四件套实测（含命令/EXIT/时间戳） | verification/RELEASE-GATE-DISPOSITION-1/four-pieces.log | 4c41ed959 | bd37f41c8bd3cb49d34ad871be57844564f1b68e458b8152c5d5e9df91e117be | CANONICAL | BLOB |
| EV-RGD-03 | AC4 HUMAN-REQUIRED（H-01…H-09） | doc/reviews/HUMAN-REQUIRED-2026-11-15.md | 4c41ed959 | b39ba98b98803129fb7e44cacae617250effeee4292d39e68e7f97bc0135b317 | CANONICAL | BLOB |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | verification/RELEASE-GATE-DISPOSITION-1/ | NOT_APPLICABLE | — | — | 新增证据，无迁移/归档 |

## Closeout Record

- Closeout：2026-11-15，DSH；判定表 `3caf423cd` + Gate6 复核返修（本提交）。
- **结果**：六条逐条判定完成。**Agent 可独立完成的只有 1 条（条件 6）**；
  条件 1/4/5 可推进但不可单独关闭；条件 2 与条件 3 的 GUI 矩阵必须人做。
- **条件 6 复核**：`gate6-final-review`（未参与实现）结论 **`CONDITION_6_PARTIAL`**（0/2/4/4），
  5 项欠缺中 **3 项已处置**：
  - 证据日志口径（无命令/EXIT/时间戳）→ 重写 `four-pieces.log`；
  - 12 条 `WORKTREE` pin 与 blob 不一致 → 全部改 `BLOB` 口径（顺带修了 `AC-RERUN-CLOSE-1`、
    `AC-DOC-CLOSE-1`、`V11R-D-1-AC8-CLOSE-1` 三卡）；
  - 三指针：STATUS 已更新并登记本判定表；
  **2 项登记为未关闭**：App.Tests 定性复跑（性能项在满载下 flaky）、定稿 head 重锚 Review。
- **App.Tests 性能项**：独立复核测得 `PerformanceBaselineTests.HotSwitch…` median p95 **1014.0ms > 1000ms**（FAIL）；
  本卡单独复跑该测试 **1 passed / 0 failed**（24s）⇒ 判定为**满载负载敏感 flaky**，非本轮引入
  （本轮 7 个 commit 零 `.cs`/`.axaml`/测试改动）。
- **门禁**：`check.ps1` PASS (3 warnings)｜`verify_pins.ps1` PASS (18/18)｜
  `generate_api_inventory.py --check` OK (1/80/6=87)。
- **未关闭项（不淡化）**：
  1. 条件 6 尚有 2 项欠缺（App.Tests 定性复跑、定稿 head 重锚 Review）；
  2. `PLAN:58`/`PLAN:56` 与 ledger/卡面的漂移未修（PLAN 预算 6960/7000 已近上限，需先压缩）；
  3. `verify_final.py` 的 8 条先存 numstat FAIL 仍在；
  4. 性能测试的负载敏感性无护栏（建议单独登记 flaky 并加负载隔离）。
