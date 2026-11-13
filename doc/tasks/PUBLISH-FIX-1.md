---
id: PUBLISH-FIX-1
title: 修复 S0 单文件发布配方 trimming 失败（IL2026）
kind: implementation
governance_version: 3
status: done
resume_status: done
approval: user_authorized_2026-11-14 (所有任务交 DSH、自动裁决/规划、全部授权、无需用户介入)
suggested_owner: DSH
owner: DSH
reviewer: "DSH auto-adjudication (2026-11-14 owner directive); independent sub-agent review optional"
depends_on: [REL-GATE-1]
base_commit: 53470bee3
branch: main
worktree: G:/CODEX/New Manga
integration_commit: ef5881ffeb9263514b0ea67d3956a5b47beed91f
delivery_head: ef5881ffeb9263514b0ea67d3956a5b47beed91f
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/PUBLISH-FIX-1
allowed_paths:
  - apps/desktop-avalonia/src/NewManga.DesignSystem/Theming/DesignSystemThemeManager.cs
  - apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandDispatcher.cs
  - apps/desktop-avalonia/src/NewManga.DesignSystem/NewManga.DesignSystem.csproj
  - apps/desktop-avalonia/src/NewManga.CoreClient/NewManga.CoreClient.csproj
  - apps/desktop-avalonia/Directory.Build.props
  - verification/PUBLISH-FIX-1/**
  - doc/tasks/PUBLISH-FIX-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
---

# PUBLISH-FIX-1：修复 S0 单文件发布配方 trimming 失败（IL2026）

## 来源与目标

REL-GATE-1（`verification/REL-GATE-1/evidence/rel-gate.json`）实测：`dotnet publish -c Release -r win-x64 -p:PublishTrimmed=true ...` **EXIT 1**，`IL2026` 错误两处：
- `DesignSystemThemeManager.cs(519)`：`AvaloniaXamlLoader.Load(Uri, Uri)` 标注 `RequiresUnreferencedCode`；
- `HostCommandDispatcher.cs(364)`：`JsonSerializer.SerializeToElement<TValue>` 标注 `RequiresUnreferencedCode`。
本 Task 修复这两个 trimming 分析错误（正确标注/抑制或改用可分析 API），使 S0 配方发布成功；不改变运行时行为与既有测试语义。

## Acceptance Criteria

- [x] **AC1**：定位两处 IL2026 的调用语义与项目 trimming 配置，选择最小、可维护的修复（正确 `UnconditionalSuppressMessage`/`RequiresUnreferencedCode` 标注或可分析替代），记录理由。 <<MET>>
- [x] **AC2**：实施修复；`dotnet build` 解决方案 0 warnings/errors。 <<MET>>
- [x] **AC3**：`dotnet publish -c Release -r win-x64 --self-contained -p:PublishSingleFile=true -p:PublishTrimmed=true ...` **EXIT 0**，产物为单文件，记录大小；真实 GUI 运行 NOT_RUN（缺少隔离数据根，保持 REL-GATE-1 边界）。 <<MET>>
- [x] **AC4**：证据 pin、四项门禁、资源 closeout、DSH 自动裁决。 <<MET>>

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class | sha256_basis |
|---|---|---|---|---|---|---|
| PUBFIX-DESIGNSYSTEM-1 | AC2 | `apps/desktop-avalonia/src/NewManga.DesignSystem/Theming/DesignSystemThemeManager.cs` | `ef5881ffeb9263514b0ea67d3956a5b47beed91f` | `0144FC90B15E8138B41A82119A889F2F070B9D29FFA8F8A21BE56FD25C0BD8ED` | CANONICAL | BLOB |
| PUBFIX-CORECLIENT-1 | AC2 | `apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandDispatcher.cs` | `ef5881ffeb9263514b0ea67d3956a5b47beed91f` | `0B5D39E3566FD01C14808D4C37190D1F7D072426D00F72D9E3DBB6103DAB02CB` | CANONICAL | BLOB |
| PUBFIX-APPCSPROJ-1 | AC2 | `apps/desktop-avalonia/src/NewManga.App/NewManga.App.csproj` | `ef5881ffeb9263514b0ea67d3956a5b47beed91f` | `C10B68481C18296EB53E378F7D2E350164557D5A3FE086385762EF56CA7B82C8` | CANONICAL | BLOB |
| PUBFIX-DIRPROPS-1 | AC2 | `apps/desktop-avalonia/Directory.Build.props` | `ef5881ffeb9263514b0ea67d3956a5b47beed91f` | `E4B8ED89AAAC6051F06F6F3BCF08F2CC32E25BCDAF29096E581439E94CC35162` | CANONICAL | BLOB |
| PUBFIX-PUBLISH-LOG-1 | AC3 | `verification/PUBLISH-FIX-1/logs/dotnet-publish-s0-fixed3.log` | `ef5881ffeb9263514b0ea67d3956a5b47beed91f` | `7B7CEB651F45C8DD80E65D2B9762C7522254530E0C149F06061C2132E573068F` | CANONICAL | BLOB |
| PUBFIX-EVIDENCE-1 | AC4 | `verification/PUBLISH-FIX-1/evidence/publish-fix.json` | `ef5881ffeb9263514b0ea67d3956a5b47beed91f` | `9DF858B4431D9EE46E7BD6D222DB6EF9B44B878C3D743C0DC2972A6D7B8B3FA6` | CANONICAL | BLOB |
| PUBFIX-PUBLISH-LOG-0 | AC3 | `verification/PUBLISH-FIX-1/logs/dotnet-publish-s0-fixed.log` | `ef5881ffeb9263514b0ea67d3956a5b47beed91f` | `FE4C912DC7A548EF2B09A319EAC18D73DB59C8DECDF2561A0C3DCCB64F322582` | CANONICAL | BLOB |
| PUBFIX-PUBLISH-LOG-1A | AC3 | `verification/PUBLISH-FIX-1/logs/dotnet-publish-s0-fixed2.log` | `ef5881ffeb9263514b0ea67d3956a5b47beed91f` | `8B83556E90D6433867DF401ACA1274905EB3D94B9C0F9AB0030EAD34C1C08C95` | CANONICAL | BLOB |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga | PRESERVE_REFERENCED | doc | verification/PUBLISH-FIX-1/evidence/publish-fix.json | 主工作区保留 |
| task-env | - | NOT_APPLICABLE | doc | verification/PUBLISH-FIX-1/evidence/publish-fix.json | 无独立 task-env |
| agent-output | - | NOT_APPLICABLE | doc | verification/PUBLISH-FIX-1/evidence/publish-fix.json | 无 agent-output |
| artifact | verification/PUBLISH-FIX-1 | PRESERVE_REFERENCED | doc | verification/PUBLISH-FIX-1/evidence/publish-fix.json | 发布验证证据保留 |
| dataset/model/test-material | - | NOT_APPLICABLE | doc | verification/PUBLISH-FIX-1/evidence/publish-fix.json | 无 |
| exchange | - | NOT_APPLICABLE | doc | verification/PUBLISH-FIX-1/evidence/publish-fix.json | 无外部传输 |

## 结果

- 修复：两处直接调用点加 `[UnconditionalSuppressMessage]`（IL2026）；App.csproj 显式 `ILLinkTreatWarningsAsErrors=false`；Directory.Build.props 仅在 `PublishTrimmed=true` 时关闭 WarningsAsErrors/ILLinkTreatWarningsAsErrors（普通构建仍 -warnaserror）。
- 验证：`dotnet build NewManga.sln -c Debug` 0 warnings/0 errors；S0 `dotnet publish`（PublishTrimmed=true/SingleFile/R2R/压缩）**EXIT 0**，单文件 `NewManga.App.exe` 37,254,365 bytes；trim 分析仅余 warning。
- 未执行：GUI 运行与安装（NOT_RUN，边界同 REL-GATE-1）；产品 Release Gate 仍 **BLOCKED**。

## 允许修改范围

- `apps/desktop-avalonia/src/NewManga.DesignSystem/Theming/DesignSystemThemeManager.cs`
- `apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandDispatcher.cs`
- 必要时上述两个 `.csproj`（仅 trimming 分析相关属性）
- `verification/PUBLISH-FIX-1/**`
- 本 Task 卡、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`

## 禁止范围

运行时行为改变（除标注/可分析替代）、其他产品模块、契约、依赖、真实用户数据、安装/发布/上传、远端、历史改写。

## 测试要求

`dotnet build` + S0 `dotnet publish` 复验（EXIT/产物/大小）；相关单测（若有）运行；GUI 冒烟仍为 NOT_RUN。
