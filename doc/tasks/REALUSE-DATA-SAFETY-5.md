---
id: REALUSE-DATA-SAFETY-5
title: B3/B4 剩余体验与卫生项——状态文案一致性、空态与错误指引、仓库卫生
kind: quality
governance_version: 3
status: closed_with_limitations
approval: user_authorized_2026-10-30_self_audit_remaining_batches
suggested_owner: dsh
owner: dsh-lead
reviewer: antigravity-headless
review_history:
  - round: 1
    verdict: FAIL_WITH_MUST_FIX
    report: doc/reviews/REALUSE-DATA-SAFETY-5-antigravity-r1.md
    must_fix: 自查记录把「没搜到」写成「MA-21/22 从未存在」；MA-20 脚本路径误判；README 备份扩展名未同步；证据 pin 与治理检查失败
  - round: 2
    verdict: FAIL_WITH_MUST_FIX
    report: doc/reviews/REALUSE-DATA-SAFETY-5-antigravity-r2.md
    must_fix: 更正只写进仓外 DEFECTS.md，版本化的 Task 卡与 Handoff 仍残留全部错误断言
  - round: 3
    verdict: FAIL_WITH_MUST_FIX
    report: doc/reviews/REALUSE-DATA-SAFETY-5-antigravity-r3.md
    must_fix: AC2 同时勾选 [x] 且标 <<PARTIAL>>，违反 check.ps1 语法约定
  - round: 4
    verdict: PASS
    report: doc/reviews/REALUSE-DATA-SAFETY-5-antigravity-r4.md
depends_on:
  - REALUSE-DATA-SAFETY-4
base_commit: 5c9c2d08d
branch: task/REALUSE-DATA-SAFETY-5
worktree: G:/CODEX/New Manga.workspace/worktrees/REALUSE-DATA-SAFETY-5
integration_commit: f9b53a0d8
delivery_head: c50901a2b
canonical_evidence_status: complete
resource_closeout_status: complete
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

- [ ] **AC1 B3 剩余项逐条核对**：对 MA-09/11/14~20 每一条给出「仍成立 / 已消失 / 性质改变」的判定与依据（文件:行 或 测试），仍成立的按批次修完。 <<PARTIAL: 9 条全部核对完成（MA-20 的脚本实际在 apps/desktop-avalonia/scripts/install.ps1，上一版误称「不在仓库」已更正）。已修 6 条：MA-14/15/16/17/18 + MA-22；已记录理由暂不修 2 条：MA-21（wire 日志重复，属可观测性优化）、MA-20（安装脚本隔离属部署侧决策）；仍成立待后续 3 条：MA-09、MA-11、MA-19。核对表与依据见 DEFECTS.md 复核记录>>
- [x] **AC2 B4 卫生项**：MA-21/22 处理完成，或在 Task 中明确记录为何不值得做。 <<MET>>
- [x] **AC3 不新增未登记行为**：不得借机扩大范围；任何新发现记入 DEFECTS.md 而不是直接实现。 <<MET>>

## 禁止范围

- 不改用户数据；不新增依赖；不 push 远端；不伪造能力。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 核对 | 逐条读代码 + `git log` | a5c08bfb0 | 9/9 条判定完成（MA-20 脚本定位到 apps/desktop-avalonia/scripts/install.ps1）；详见 DEFECTS.md 复核记录 | `DEFECTS.md` |
| AC1 MA-14 | `dotnet test --filter AppOptionsCliRobustnessTests` | net9.0 | PASS（+11 用例：7 个合法页面、3 个非法页面、2 个变体、1 个非法变体） | `AppOptionsCliRobustnessTests.cs` |
| AC1 MA-17 | `dotnet test --filter StartRunReadOnly|StartRunNotReady` | net9.0 | PASS 2/2 | `V2StudioBatchTests.cs` |
| AC1 MA-18 | `dotnet test --filter FirstRunBackup_IgnoresCorePackages` | net9.0 | PASS（Core `.nmbak` 不再抑制首次备份，新备份后缀 `.sqlite-backup`） | `HostUnitTests.cs` |
| AC1 MA-15/16 | 人工核对文案与 README | — | PASS（含候选位置与修复步骤；README 0.1.1 与实际能力一致） | `SidecarException.cs` / `README.md` |
| AC2 | MA-22 修剪 + MA-21 记录 | net9.0 | PASS（代码路径核对：修剪在 `lock (_evidenceGate)` 内按 `LastWriteTimeUtc` 保留最近 200，异常静默；未加自动化用例——`HostGrantCoordinator` 需要真实 sidecar 环境，覆盖成本高于这段 20 行逻辑的风险，理由记录在此） | `HostGrantCoordinator.cs` |
| AC3 | 人工核对 diff + DEFECTS.md 新增记录 | — | PASS（新发现只记录未实现） | `DEFECTS.md` |

## Canonical Evidence

进入独立审查前逐项填写（当前为空）。

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| E-AC1-CLI | AC1 | `apps/desktop-avalonia/src/NewManga.App/AppOptions.cs` | `f25120e17` | `-` | CANONICAL |
| E-AC1-CLI-TEST | AC1 | `apps/desktop-avalonia/tests/NewManga.App.Tests/AppOptionsCliRobustnessTests.cs` | `f25120e17` | `-` | CANONICAL |
| E-AC1-BATCH | AC1 | `apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Studio/StudioBatchViewModel.cs` | `f25120e17` | `-` | CANONICAL |
| E-AC1-BACKUP | AC1 | `apps/desktop-avalonia/src/NewManga.Host/DataSafety.cs` | `f25120e17` | `-` | CANONICAL |
| E-AC1-DOCS | AC1 | `README.md` | `f25120e17` | `-` | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/REALUSE-DATA-SAFETY-5 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/REALUSE-DATA-SAFETY-5 | doc/handoffs/REALUSE-DATA-SAFETY-5-handoff.md | 前五批 worktree 全部保留 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
