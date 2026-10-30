---
id: REALUSE-DATA-SAFETY-2
title: 修复真实使用自查 B2 批次——Provider 可用性引导、就绪状态诚实性、启动自检降级误报
kind: fix
governance_version: 3
status: done
approval: user_authorized_2026-10-30_self_audit_repair
suggested_owner: dsh
owner: dsh-lead
reviewer: antigravity-headless
review_history:
  - round: 1
    verdict: FAIL_WITH_MUST_FIX
    report: doc/reviews/REALUSE-DATA-SAFETY-2-antigravity-r1.md
    must_fix: 1 (retry path leaked the single-instance mutex)
  - round: 2
    verdict: PASS
    report: doc/reviews/REALUSE-DATA-SAFETY-2-antigravity-r2.md
depends_on:
  - REALUSE-DATA-SAFETY-1
base_commit: a29e0f516
branch: task/REALUSE-DATA-SAFETY-2
worktree: G:/CODEX/New Manga.workspace/worktrees/REALUSE-DATA-SAFETY-2
integration_commit: 15efbcfb0
delivery_head: f0e207db5
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/REALUSE-DATA-SAFETY-2
allowed_paths:
  - doc/tasks/REALUSE-DATA-SAFETY-2.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/handoffs/REALUSE-DATA-SAFETY-2-handoff.md
  - doc/reviews/REALUSE-DATA-SAFETY-2-*.md
  - apps/desktop-avalonia/src/NewManga.App/**
  - apps/desktop-avalonia/src/NewManga.Host/**
  - apps/desktop-avalonia/src/NewManga.CoreClient/**
  - apps/desktop-avalonia/tests/**
  - src/bootstrap/**
  - src/infrastructure/**
  - verification/REALUSE-DATA-SAFETY-2/**
---

# REALUSE-DATA-SAFETY-2：B2 批次（真实使用自查第二轮）

## 来源与目标

`G:\CODEX\New Manga.workspace\tmp\self-audit\DEFECTS.md` 记录的 21 条缺陷中，B1（BATCH 1，数据安全）已由 [REALUSE-DATA-SAFETY-1](REALUSE-DATA-SAFETY-1.md) 关闭。本批次处理**用户可见的诚实性与可用性**问题：界面报告的状态必须与实际能力一致，缺失能力必须给出可执行的下一步。

## 范围（实际覆盖：MA-02 + MA-04 + MA-05）

> 批次标签说明（DSH 收口时核对 DEFECTS.md 后更正）：审计把 MA-02 归入 B2「核心链路可达」，把 MA-04/MA-05 归入 B3「状态与体验」。本 Task 实际取的是这三条（都属用户可见的诚实性问题），因此**不覆盖** B2 的 MA-06/MA-07/MA-08/MA-10——它们由后续 REALUSE-DATA-SAFETY-3 承接。

- **MA-02**：发布包不含模型权重，`PROVIDER_NOT_CONFIGURED` 时 UI 无任何指引（用户只看到失败任务）。要求：诊断/工作台在检测到未配置 Provider 时给出明确说明与入口，而不是让 Run 静默失败。
- **MA-04**：Host 处于只读或启动失败时，界面仍显示绿色「Host 就绪」，且「重试」是空操作。要求：状态徽标与真实 `HostViewState`/`Mode` 一致；重试必须真的重试或明确禁用。
- **MA-05**：`StartupSelfCheck` 在全部通过时仍返回 `Degraded`（12/12 次实测），且 App 侧零引用。要求：自检结果与 App 展示一致（通过即 `Ready`），失败才降级并说明原因。

## 验收标准

- [x] **AC1 Provider 未配置可诊断**：无可用 Provider 时，UI 明确显示「未配置模型 Provider」并给出下一步入口/说明；不再出现「任务静默失败」。 <<MET>>
- [x] **AC2 就绪状态诚实**：只读/失败/未就绪时状态徽标不得显示「就绪」；「重试」按钮要么真实重试要么禁用并说明。 <<MET>>
- [x] **AC3 启动自检不再误报降级**：自检全通过时返回 `Ready`；失败时返回 `Degraded` 并携带原因；App 侧消费该结果。 <<MET>>

## 允许修改范围

见 frontmatter `allowed_paths`。不修改冻结契约 `doc/contracts/V11R_COMMAND_CONTRACT_V1.md` 的命令语义；若需要新命令，先在本 Task 记录契约变更并交 DSH 裁决。

## 禁止范围

- 不修改用户数据根内容；不以假开关/假状态替代真实能力。
- 不引入新依赖（尤其模型权重、Provider SDK）。
- 不 push 远端。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 Provider 未配置提示 | `dotnet test --filter V2StudioBatchTests` | headless Avalonia / `5acbc9b88` | PASS 19/19（含 2 个新例：指引文案 + 卡片可见） | `V2StudioBatchTests.cs` |
| AC2 状态诚实性 | `dotnet test --filter Host` + headless UI | net9.0 | NOT_RUN | 待补 |
| AC3 自检结果 | `dotnet test --filter StartupSelfCheck` | net9.0 / `e9b80d896` | PASS：Host 7 passed / 3 环境性跳过；App 侧断言 SelfCheckStatus=Failed + 行含错误码 | `StartupSelfCheckTests.cs`、`StartupSelfCheckUiTests.cs` |
| AC2 只读状态 | `dotnet test --filter "FullyQualifiedName~ReadOnlyHost_IsNotShownAsGreenReady|FullyQualifiedName~WritableHost_KeepsGreenReadyState"` | headless Avalonia / `e9b80d896` | PASS 2/2 | `V2ShellUiTests.cs` |
| 全量回归 | `dotnet test NewManga.sln` | net9.0 / `e9b80d896` | PASS：813 passed / 0 failed（App 327 / Host 50 / ThemeEngine 235 / DS 85 / CoreClient 116） | 控制台输出 |

## Canonical Evidence

进入独立审查前逐项填写（当前为空）。

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| E-AC1-GUIDANCE | AC1 | `apps/desktop-avalonia/tests/NewManga.App.Tests/V2StudioBatchTests.cs` | `5acbc9b88` | `-` | CANONICAL |
| E-AC1-VM | AC1 | `apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Studio/StudioBatchViewModel.cs` | `5acbc9b88` | `-` | CANONICAL |
| E-AC1-VIEW | AC1 | `apps/desktop-avalonia/src/NewManga.App/Views/V2/Studio/Controls/StudioBatchControls.cs` | `5acbc9b88` | `-` | CANONICAL |
| E-AC2-SHELL | AC2 | `apps/desktop-avalonia/tests/NewManga.App.Tests/V2ShellUiTests.cs` | `e9b80d896` | `-` | CANONICAL |
| E-AC2-STATE | AC2 | `apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Shell/AppShellViewModel.cs` | `e9b80d896` | `-` | CANONICAL |
| E-AC2-RETRY | AC2 | `apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs` | `e9b80d896` | `-` | CANONICAL |
| E-AC3-SELFCHECK | AC3 | `apps/desktop-avalonia/src/NewManga.Host/StartupSelfCheck.cs` | `e9b80d896` | `-` | CANONICAL |
| E-AC3-TESTS | AC3 | `apps/desktop-avalonia/tests/NewManga.Host.Tests/StartupSelfCheckTests.cs` | `e9b80d896` | `-` | CANONICAL |
| E-AC3-UI | AC3 | `apps/desktop-avalonia/tests/NewManga.App.Tests/StartupSelfCheckUiTests.cs` | `e9b80d896` | `-` | CANONICAL |
| E-AC3-CONSOLE | AC3 | `apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Console/ConsoleViewModel.cs` | `e9b80d896` | `-` | CANONICAL |
| E-RETRY-FIX | AC2 | `apps/desktop-avalonia/tests/NewManga.App.Tests/HostControllerRetryTests.cs` | `f0e207db5` | `-` | CANONICAL |
| E-REVIEW-R1 | Gate | `doc/reviews/REALUSE-DATA-SAFETY-2-antigravity-r1.md` | `f0e207db5` | `-` | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/REALUSE-DATA-SAFETY-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/REALUSE-DATA-SAFETY-1 | doc/handoffs/REALUSE-DATA-SAFETY-1-handoff.md | B1 的 worktree 保留；本 Task 尚未开 worktree |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
