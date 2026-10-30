---
id: REALUSE-DATA-SAFETY-5
title: B3/B4 剩余体验与卫生项——状态文案一致性、空态与错误指引、仓库卫生
kind: quality
governance_version: 3
status: in_review
approval: user_authorized_2026-10-30_self_audit_remaining_batches
suggested_owner: dsh
owner: dsh-lead
reviewer: antigravity-headless
depends_on:
  - REALUSE-DATA-SAFETY-4
base_commit: 5c9c2d08d
branch: task/REALUSE-DATA-SAFETY-5
worktree: G:/CODEX/New Manga.workspace/worktrees/REALUSE-DATA-SAFETY-5
integration_commit: null
delivery_head: PENDING
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

- [ ] **AC1 B3 剩余项逐条核对**：对 MA-09/11/14~20 每一条给出「仍成立 / 已消失 / 性质改变」的判定与依据（文件:行 或 测试），仍成立的按批次修完。 <<PARTIAL: 已核对 9 条中的 8 条（MA-20 的脚本不在仓库，无法核对），修掉 5 条（MA-14/15/16/17/18），剩 4 条按判定留给后续：MA-09（进度刷新未接）、MA-11（迁移策略需用户裁决）、MA-19（derived 副本涉及资源通道设计）、MA-20（脚本归属待确认）。核对表与依据已写进 DEFECTS.md 复核记录。本批不把「未修」说成「已修」>>
- [x] **AC2 B4 卫生项**：MA-21/22 处理完成，或在 Task 中明确记录为何不值得做。 <<NOT_APPLICABLE: DEFECTS.md 实际只到 MA-20，MA-21/22 从未存在（B4 批次表记账错误）；已把编号越界与 B4 的真实内容一并记入 DEFECTS.md 复核记录>>
- [x] **AC3 不新增未登记行为**：不得借机扩大范围；任何新发现记入 DEFECTS.md 而不是直接实现。 <<MET>>

## 禁止范围

- 不改用户数据；不新增依赖；不 push 远端；不伪造能力。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 核对 | 逐条读代码 + `git log` | a5c08bfb0 | 8/9 条判定完成（1 条脚本不在仓库）；详见 DEFECTS.md 复核记录 | `DEFECTS.md` |
| AC1 MA-14 | `dotnet test --filter AppOptionsCliRobustnessTests` | net9.0 | PASS（+11 用例：7 个合法页面、3 个非法页面、2 个变体、1 个非法变体） | `AppOptionsCliRobustnessTests.cs` |
| AC1 MA-17 | `dotnet test --filter StartRunReadOnly|StartRunNotReady` | net9.0 | PASS 2/2 | `V2StudioBatchTests.cs` |
| AC1 MA-18 | `dotnet test --filter FirstRunBackup_IgnoresCorePackages` | net9.0 | PASS（Core `.nmbak` 不再抑制首次备份，新备份后缀 `.sqlite-backup`） | `HostUnitTests.cs` |
| AC1 MA-15/16 | 人工核对文案与 README | — | PASS（含候选位置与修复步骤；README 0.1.1 与实际能力一致） | `SidecarException.cs` / `README.md` |
| AC2 | 人工核对编号边界 | — | N/A（编号不存在） | `DEFECTS.md` |
| AC3 | 人工核对 diff + DEFECTS.md 新增记录 | — | PASS（新发现只记录未实现） | `DEFECTS.md` |

## Canonical Evidence

进入独立审查前逐项填写（当前为空）。

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| E-AC1-CLI | AC1 | `apps/desktop-avalonia/src/NewManga.App/AppOptions.cs` | `PENDING` | `-` | CANONICAL |
| E-AC1-CLI-TEST | AC1 | `apps/desktop-avalonia/tests/NewManga.App.Tests/AppOptionsCliRobustnessTests.cs` | `PENDING` | `-` | CANONICAL |
| E-AC1-BATCH | AC1 | `apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Studio/StudioBatchViewModel.cs` | `PENDING` | `-` | CANONICAL |
| E-AC1-BACKUP | AC1 | `apps/desktop-avalonia/src/NewManga.Host/DataSafety.cs` | `PENDING` | `-` | CANONICAL |
| E-AC1-DOCS | AC1 | `README.md` | `PENDING` | `-` | CANONICAL |
| E-AC3-RECORD | AC3 | `DEFECTS.md`（仓外 G:/CODEX/New Manga.workspace/tmp/self-audit） | `PENDING` | `-` | SUPPORTING |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/REALUSE-DATA-SAFETY-5 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/REALUSE-DATA-SAFETY-5 | doc/handoffs/REALUSE-DATA-SAFETY-5-handoff.md | 前五批 worktree 全部保留 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
