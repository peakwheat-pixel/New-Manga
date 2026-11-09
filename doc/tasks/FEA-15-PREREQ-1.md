---
id: FEA-15-PREREQ-1
title: 修复既有 2 个 App.Tests 失败（V2Conformance 原始设计值 / FluentPage 快捷键计数）
kind: fix
governance_version: 3
status: in_review
approval: DSH 自裁 2026-11-09（FEA-15 集成验收前置：全量 .NET 必须绿；两项为既有回归，非本线引入）
suggested_owner: dsh
owner: dsh
reviewer: 待指派（必须独立上下文）
depends_on: []
base_commit: 417d9c442
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-15-PREREQ-1
allowed_paths:
  - doc/tasks/FEA-15-PREREQ-1.md
  - doc/reviews/FEA-15-PREREQ-1-*.md
  - doc/handoffs/FEA-15-PREREQ-1-*.md
  - verification/FEA-15-PREREQ-1/**
  - apps/desktop-avalonia/src/NewManga.App/Shell/V2/ImmersiveReaderWindow.cs
  - apps/desktop-avalonia/tests/NewManga.App.Tests/FluentPageTests.cs
out_of_scope:
  - 不改产品行为（阅读器仍是全屏黑底；快捷键集合不变）
  - 不改测试判据的语义（只把过期期望值与真实定义对齐）
  - 不改主题资源定义、不改契约/pins
---

# FEA-15-PREREQ-1：修复既有 2 个 App.Tests 失败

## 现象（base `417d9c442` 复现）

| 测试 | 失败信息 |
|---|---|
| `V2ConformanceTests.AppCSharp_OutsideShellLayout_HasNoRawDesignValues` | `["Shell/V2/ImmersiveReaderWindow.cs: literal brush/c…"]`（`Background = Brushes.Black;`） |
| `FluentPageTests.FluentShell_BreakpointsA11yShortcutsAndReducedMotion_AreExplicit` | `Assert.Equal(17, HasGesture 数量)` 实际 **18** |

两者均为既有回归（非 FEA-13 引入），是 FEA-15 集成验收（全量 .NET 绿）的硬前置。

## 修复口径

1. **ImmersiveReaderWindow**：`Background = Brushes.Black;` → 通过 `SetResourceReference(BackgroundProperty, "Nm.Color.Bg.Canvas")` 使用设计系统 token；阅读器视觉不变（画布色）。
2. **FluentPageTests**：期望值 17 → 与真实定义一致（18），并在测试注释中记录：18 个 gesture 是当前 ShellKeyMap 的权威数量；同时断言 gesture 无重复键（防止未来重复注册）。

## Acceptance Criteria

- [x] **AC1 V2Conformance**：`V2ConformanceTests.AppCSharp_OutsideShellLayout_HasNoRawDesignValues` 通过（无 literal brush/colour）。 <<MET>>
- [x] **AC2 FluentPage**：快捷键断言与真实定义一致且无重复 gesture 键。 <<MET>>
- [x] **AC3 构建与全量**：`dotnet build` 0/0；App.Tests 全量通过（原 2 失败消除，无新增失败）。 <<MET>>
- [x] **AC4 门禁**：`check.ps1`（默认 + `-TaskPath`）PASS；pins 18/18；diff ⊆ allowed_paths。 <<MET>>

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-P1-README | AC1–AC4 | `verification/FEA-15-PREREQ-1/README.md` | `-` | `d88f5e492c966d77e712e2c40b3971cdfd194c188ae90ad4b0e160180f1a116c` | CANONICAL |
| EV-P1-TWO | AC1,AC2 | `verification/FEA-15-PREREQ-1/logs/dotnet-test-two.log` | `-` | `2039e2dedd16c5c188b94ef5b99e105ca482ba1945f0af84917286072b465411` | CANONICAL |
| EV-P1-FULL | AC3 | `verification/FEA-15-PREREQ-1/logs/dotnet-test-app-full.log` | `-` | `72e7e13a2b2151254d3e8ade9f762098af6e6398efb1cc064e0ccb2d7b7fd4ef` | CANONICAL |
| EV-P1-BUILD | AC3 | `verification/FEA-15-PREREQ-1/logs/dotnet-build.log` | `-` | `069650a69ccfdb95aa6d9ecbf079c510fa3f198d0710e7ae4eb4189680a6d402` | CANONICAL |
| EV-P1-MUT1 | 变异判别 | `verification/FEA-15-PREREQ-1/logs/mutation-literal-brush.log` | `-` | `460234602fdf047c5e86dc018439f2b0ab9b6221292b582ff3b355f478734df6` | CANONICAL |
| EV-P1-MUT2 | 变异判别 | `verification/FEA-15-PREREQ-1/logs/mutation-stale-count.log` | `-` | `06ab870b0bb85689f753d3d0c6fe5775af2e3a0864c6708708915555ea239399` | CANONICAL |
## 证据计划

| # | 命令/步骤 | 判别 |
|---|---|---|
| E1 | `dotnet test NewManga.App.Tests --filter "V2ConformanceTests.AppCSharp_OutsideShellLayout_HasNoRawDesignValues\|FluentPageTests.FluentShell_BreakpointsA11yShortcutsAndReducedMotion_AreExplicit"` | 2 passed |
| E2 | `dotnet test NewManga.App.Tests`（全量） | 0 failed（原 2 个已消除） |
| E3 | `dotnet build NewManga.sln` | 0 警告 / 0 错误 |
| E4 | `check.ps1`、`verify_pins` | PASS / 18/18 |
| E5 | 变异（恢复 `Brushes.Black` / 断言改回 17） | 对应测试 RED |

## 风险与回退

- 阅读器背景若资源键缺失 → 回退为 `Brushes.Black`（但需同时修测试豁免；不采用）。
- 快捷键数量若未来再变 → 测试需显式更新（本次已在注释说明）。

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | NOT_APPLICABLE（main；base `417d9c442`） | NOT_APPLICABLE | — | — | 未创建 worktree |
| temp | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 无 |
| build | `apps/desktop-avalonia/**/bin,obj` | NOT_APPLICABLE | — | — | 既有 ignore |
| user-data | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 未访问真实库 |

## Closeout Record

- 待独立 Review 通过后由 DSH 填写。
