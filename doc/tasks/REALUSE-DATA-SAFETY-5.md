---
id: REALUSE-DATA-SAFETY-5
title: B3/B4 剩余体验与卫生项——状态文案一致性、空态与错误指引、仓库卫生
kind: quality
governance_version: 3
status: ready
approval: user_authorized_2026-10-30_self_audit_remaining_batches
suggested_owner: dsh
owner: null
reviewer: null
depends_on:
  - REALUSE-DATA-SAFETY-4
base_commit: 5c9c2d08d
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/REALUSE-DATA-SAFETY-5
allowed_paths:
  - doc/tasks/REALUSE-DATA-SAFETY-5.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/handoffs/REALUSE-DATA-SAFETY-5-handoff.md
  - doc/reviews/REALUSE-DATA-SAFETY-5-*.md
  - apps/desktop-avalonia/src/NewManga.App/**
  - apps/desktop-avalonia/src/NewManga.Host/**
  - apps/desktop-avalonia/tests/**
  - verification/REALUSE-DATA-SAFETY-5/**
---

# REALUSE-DATA-SAFETY-5：B3/B4 剩余项

## 来源

真实使用自查（`G:\CODEX\New Manga.workspace\tmp\self-audit\DEFECTS.md`）里尚未处理完的批次：

- **B3 状态与体验**：MA-09、MA-11、MA-14 ~ MA-20（MA-04/MA-05 已由 REALUSE-DATA-SAFETY-2 修复；MA-06 已由 REALUSE-DATA-SAFETY-4 处理）。
- **B4 卫生**：MA-21、MA-22。

具体缺陷内容以 DEFECTS.md 为准，本卡不复制第二份定义。

## 范围

按 DEFECTS.md 逐条核对，**只修仍然成立的问题**：在前三批修复之后，部分条目可能已经自然消失或性质改变，裁掉已解决的，替换为真实存在的。

## 验收标准

- [ ] **AC1 B3 剩余项逐条核对**：对 MA-09/11/14~20 每一条给出「仍成立 / 已消失 / 性质改变」的判定与依据（文件:行 或 测试），仍成立的按批次修完。 <<PARTIAL: 待实现>>
- [ ] **AC2 B4 卫生项**：MA-21/22 处理完成，或在 Task 中明确记录为何不值得做。 <<PARTIAL: 待实现>>
- [ ] **AC3 不新增未登记行为**：不得借机扩大范围；任何新发现记入 DEFECTS.md 而不是直接实现。 <<PARTIAL: 待实现>>

## 禁止范围

- 不改用户数据；不新增依赖；不 push 远端；不伪造能力。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 逐条核对 + 对应测试 | net9.0 | NOT_RUN | 待补 |
| AC2 | 同上 | net9.0 | NOT_RUN | 待补 |
| AC3 | 人工核对 diff | — | NOT_RUN | 待补 |

## Canonical Evidence

进入独立审查前逐项填写（当前为空）。

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| - | - | - | `-` | `-` | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4 | doc/handoffs/REALUSE-DATA-SAFETY-4-handoff.md | 前四批 worktree 保留；本 Task 尚未开 worktree |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
