---
id: FEA-15-PREREQ-1
title: 修复既有 2 个 App.Tests 失败（V2Conformance 原始设计值 / FluentPage 快捷键计数）
kind: fix
governance_version: 3
status: done
approval: DSH 自裁 2026-11-09（FEA-15 集成验收前置：全量 .NET 必须绿；两项为既有回归，非本线引入）
suggested_owner: dsh
owner: dsh
reviewer: 独立上下文子代理 r1（`doc/reviews/FEA-15-PREREQ-1-r1.md`：approved；非实现会话）
depends_on: []
base_commit: 417d9c442
branch: null
worktree: null
integration_commit: f7134ba83
delivery_head: f7134ba83
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/FEA-15-PREREQ-1
allowed_paths:
  - doc/tasks/FEA-15-PREREQ-1.md
  - doc/reviews/FEA-15-PREREQ-1-*.md
  - doc/handoffs/FEA-15-PREREQ-1-*.md
  - verification/FEA-15-PREREQ-1/**
  - apps/desktop-avalonia/src/NewManga.App/Shell/V2/ImmersiveReaderWindow.cs
  - apps/desktop-avalonia/tests/NewManga.App.Tests/FluentPageTests.cs
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
out_of_scope:
  - 不改产品行为（阅读器仍是设计系统画布底色、跟随主题 token；快捷键集合不变）
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
- [x] **AC4 门禁**：`check.ps1`（默认 + `-TaskPath`）PASS；pins 18/18；diff ⊆ allowed_paths（**含 DSH 生命周期指针三文件**：STATUS/REBASELINE_PLAN/TASK_LEDGER，R-001 处置）。 <<MET>>

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-P1-README | AC1–AC4 | `verification/FEA-15-PREREQ-1/README.md` | `-` | `efaf342dadcb557d66ef208be5d58e553078a2dd253cc3d8d568f2ffd90b7cb1` | CANONICAL |
| EV-P1-TWO | AC1,AC2 | `verification/FEA-15-PREREQ-1/logs/dotnet-test-two.log` | `-` | `57ddd03d75a5cf64d104aa66ef48560428b4e8cde65a05aa295b200e0de9faf4` | CANONICAL |
| EV-P1-FULL | AC3 | `verification/FEA-15-PREREQ-1/logs/dotnet-test-app-full.log` | `-` | `72e7e13a2b2151254d3e8ade9f762098af6e6398efb1cc064e0ccb2d7b7fd4ef` | CANONICAL |
| EV-P1-BUILD | AC3 | `verification/FEA-15-PREREQ-1/logs/dotnet-build.log` | `-` | `6a66acf545412b3012e0e71b6bbc8eb0788c5dabd4e98c312693c3ace357ac60` | CANONICAL |
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

## Closeout Record

- **2026-11-09 / DSH（关账）**：AC1–AC4 全部 MET；2 个既有 App.Tests 失败消除（V2Conformance / FluentPage），FEA-15 前置测试债清理完成。
- **Review**：r1 独立子代理 **approved**（P0=0/P1=0/P2=1/P3=4）→ 处置：R-001 allowed_paths 补治理指针 + AC4 措辞；R-002 注释/out_of_scope 口径；R-003 去重断言改域名规则 Assert.Empty(Conflicts)；R-004 死 using 删除 + using 排序；R-005 证据措辞对齐。
- **门禁**：目标 2 用例 **2 passed**（改后复跑）；V2ImmersiveReaderTests 3 passed；dotnet build 0/0；App.Tests 全量 **838 passed / 0 failed / 11 skipped**（改动仅为注释/using/断言，全量重跑取自信任 EV + 本次目标回归）；check.ps1 默认 + -TaskPath PASS；verify_pins 18/18。
- **变异**：literal brush 恢复 → V2Conformance RED；断言 17 → FluentPage RED；复原（-t:Rebuild）后 2 passed。
- **交付/集成**：实现 `f7134ba83`（`integration_commit`）；本收口提交含 R-001…R-005 处置与指针翻转。
- **边界**：0 契约字节、0 pin；diff ⊆ allowed_paths（含生命周期指针三文件）。