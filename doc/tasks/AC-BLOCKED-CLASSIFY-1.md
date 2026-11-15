---
id: AC-BLOCKED-CLASSIFY-1
title: 72 条 blocked AC 的可闭性分类 + HUMAN-REQUIRED 清单
kind: governance
governance_version: 3
status: in_progress
suggested_owner: DSH
owner: DSH
reviewer: null
depends_on:
  - AC-CHECKBOX-AUTHORITY-1
approval: 用户 2026-11-15「全部授权、持续自动推进」；目标 C「AC blocked 项中可归因闭合项」与目标 D「HUMAN-REQUIRED 清单」
base_commit: 73da5ab40
branch: main
worktree: G:/CODEX/New Manga
evidence_dir: verification/AC-BLOCKED-CLASSIFY-1
allowed_paths:
  - doc/tasks/AC-BLOCKED-CLASSIFY-1.md
  - doc/reviews/HUMAN-REQUIRED-2026-11-15.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - verification/AC-BLOCKED-CLASSIFY-1/**
---

# AC-BLOCKED-CLASSIFY-1：blocked 分类与 HUMAN-REQUIRED 清单

## 来源

`AC-CHECKBOX-AUTHORITY-1` 收口时 40 张卡共 **72 条 `blocked`** AC。目标 C 要求「AC blocked 项中
可归因闭合项」清零，目标 D 要求「剩余仅物理设备/人眼/外部账号类事项逐条登记为 HUMAN-REQUIRED
并附最小操作步骤」。本卡是这两项的前置：**先把 72 条分类清楚，再决定闭/不闭**。

## 目标（一个可观察结果）

72 条 `blocked` 全部归类，每类给出归因依据；其中真正需要人的 5 项整理成
`doc/reviews/HUMAN-REQUIRED-2026-11-15.md`，附最小操作步骤与预估耗时。

## Acceptance Criteria

- [ ] **AC1 全量分类**：72 条逐条归入 6 类（ARCHIVE / HUMAN / RERUN / DOC / IMPL / OTHER）之一，
      总数与 `verify_final.py` 的 `blocked=72` 一致。
- [ ] **AC2 可闭性判定**：对每类给出「可否由 Agent 闭合」的判定与依据（不笼统）。
- [ ] **AC3 HUMAN-REQUIRED 清单**：需人完成的事项逐条给出「为什么必须人做」+「最小操作步骤」+
      「预估耗时」；且与 `blocked` 明细不重叠、不遗漏。
- [ ] **AC4 判定零改动**：本轮**不改任何 AC 注释的 kind**（分类不改判定）；只新增分类文档与清单。
- [ ] **AC5 证据与不回归**：分类明细落 `verification/AC-BLOCKED-CLASSIFY-1/`；
      `check.ps1` PASS、`verify_pins` 18/18、`api_inventory` OK。

## 允许修改范围

见 frontmatter `allowed_paths`。要点：**本轮只新增文档，不动 72 条 AC 的注释**。

## 禁止范围

- 不得把 `blocked` 改成 `verified`/`not-applicable`（那是下一张卡的事，需逐条验证证据）；
- 不得修改 `doc/tasks/**` 下除本卡外的任何文件；
- 不得为凑数把「真实实现缺口」归入 HUMAN。

## 测试要求

| 场景 | 命令 | 期望 |
|---|---|---|
| blocked 计数一致 | `verify_final.py`（`AC_BASE=0b517259e`） | 40 卡 / 260 AC / 72 blocked |
| 分类总数 | 分类脚本 | 72 |
| 四件套 | check / pins / inventory | PASS / 18-18 / 87 |

## 证据

分类明细与清单依据写入 `verification/AC-BLOCKED-CLASSIFY-1/`。
