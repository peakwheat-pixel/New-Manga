---
id: FEA-GOV-2
title: AD-002 责任表与哨兵口径修订提案（C-01b 冻结前置③）
kind: governance
governance_version: 3
status: ready
approval: follow_up_of_FEA-GOV-1_2026-11-01
suggested_owner: dsh
owner: null
reviewer: null
depends_on:
  - FEA-GOV-1
base_commit: pending
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-GOV-2
allowed_paths:
  - doc/tasks/FEA-GOV-2.md
  - doc/plan/FEA-AD002_AMENDMENT_PROPOSAL.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - verification/FEA-GOV-2/**
---

# FEA-GOV-2：AD-002 责任表与哨兵口径修订提案

## 来源

C-01b 冻结前置② 已由 FEA-GOV-1 解决（AD-003 `G-REVIEW: SATISFIED`）。前置③ 仍待用户确认：
[AD-002](../AD-002_TARGET_DESKTOP_ARCHITECTURE.md) 的 `:28` 责任表 `Managed Copy｜保持既有实现与验收` 行与 `:9-10` 顶部横幅，
需要把"新导入默认策略已被 AD-003 取代"从**横幅说明**升级为**责任表条文**（否则契约冻结时引用 AD-002 仍会读到旧默认）。

## 验收标准

- [ ] **AC1 修订提案**：在 `doc/plan/FEA-AD002_AMENDMENT_PROPOSAL.md` 给出 AD-002 的**最小修订 diff**——① `:28` 责任表行的新文本（保留旧数据双读、明确新导入=引用）；② 哨兵口径（`Managed Copy` 字样如何处理，与 AD-003 §2.1 一致）；③ 明确的字节保留声明（只改这两处，其余正文不动）。**提案不直接修改 AD-002**，等用户确认后由 DSH 执行。 <<PARTIAL: 待实现>>
- [ ] **AC2 确认清单**：列出冻结前置③需要用户回复的全部问题（逐条给推荐选项与影响），供晨报「待裁决」区使用。 <<PARTIAL: 待实现>>

## 禁止范围

- **不直接修改 AD-002**（Decision authority: User；提案获批后才改）；不改代码/用户数据；不 push。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 起草提案 + `check.ps1` | 文档 | NOT_RUN | 待补 |
| AC2 | 清单核对 | 文档 | NOT_RUN | 待补 |

## Canonical Evidence

进入独立审查前逐项填写（当前为空）。

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| - | - | - | `-` | `-` | CANONICAL |

## Resource Manifest

治理 Task：无 worktree、无临时产物；资源处置在收口时登记。

## Closeout Record

- Closeout date / DSH：待关闭时填写。
