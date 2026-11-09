---
id: FEA-14-SET-1
title: FEA-14 切片 1：设置/字体面板（可切换前端架构线 S5 收口切片）
kind: implementation
governance_version: 3
status: in_progress
approval: **scope review r1（`doc/reviews/FEA-14-SET-1-scope-r1.md`）**：卡面「字体选择+持久化」= NEEDS_UNFREEZE；DSH 2026-11-10 采纳 **§1.6 窄化口径**（字体组 = 只读投影 + 回退解析 + 本地样例预览，零写入/零新持久化/零契约字节）→ **READY-TO-FREEZE**，按本卡冻结实施。
suggested_owner: zcode
owner: dsh
reviewer: null
depends_on:
  - FEA-13-SRC-6
base_commit: c4e40509b
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-14-SET-1
allowed_paths:
  - doc/tasks/FEA-14-SET-1.md
  - doc/reviews/FEA-14-SET-1-*.md
  - doc/handoffs/FEA-14-SET-1-*.md
  - verification/FEA-14-SET-1/**
  - apps/desktop-avalonia/src/NewManga.App/Services/TypographySnapshot.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/AvaloniaTypographySource.cs
  - apps/desktop-avalonia/src/NewManga.App/ViewModels/Fluent/SettingsViewModel.cs
  - apps/desktop-avalonia/src/NewManga.App/Views/Fluent/SettingsPageView.cs
  - apps/desktop-avalonia/src/NewManga.App/Views/Fluent/FluentShellSurface.axaml.cs
  - apps/desktop-avalonia/tests/NewManga.App.Tests/TypographyResolverTests.cs
  - apps/desktop-avalonia/tests/NewManga.App.Tests/SettingsTypographyPanelTests.cs
  - apps/desktop-avalonia/tests/NewManga.App.Tests/SettingsDraftSyncTests.cs
  - apps/desktop-avalonia/tests/NewManga.App.Tests/FluentResidualSettingsLeaveTests.cs
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
out_of_scope:
  - **只读投影**：不做字体写入/持久化（字体族属视觉主题，Theme Studio 是唯一编辑者；写入需 UNFREEZE）
  - 不新增 Core/IPC 命令、不改 `IHostController`、不改 `Application.Styles`/全局资源
  - 不改冻结契约字节与 18 pins（C-03/C-02/P15/C-07 零字节）
  - 不实现持久化重启读回（该口径下不存在新字段）
---

# FEA-14-SET-1：设置/字体面板（占位）

## Scope 冻结（2026-11-10，DSH；依据 `doc/reviews/FEA-14-SET-1-scope-r1.md`）

**裁决**：scope r1 判定卡面「字体选择+持久化」需 UNFREEZE（C-03 §2.1/2.2/3 + C-02 V-06/V-07 载体）；DSH 采纳 **§1.6 窄化口径** → `READY-TO-FREEZE`，**零契约变更、零新持久化、零新 wire**。

**范围（4 条）**：

1. 读取当前视觉主题的 `Nm.FontFamily.Ui/Data/Display` 与字号缩放/行高预设（只读 token 投影）
2. 每条字体栈**回退解析**：逐段判断本机是否安装（`FontManager.Current` / `TryGetGlyphTypeface`），输出「实际使用族 + 缺失段列表」，全缺失显示栈尾 generic
3. **本地样例预览**（中文/拉丁/数字各一行），字体只设在样例控件上，**不写**全局资源
4. 明确文案「字体族属于视觉主题；切换主题见『外观』组」——不放假按钮

**命令面**：零新增（只读；无 IPC/Core 改动）；`verify_pins` 18/18。

**口径裁决（DSH 2026-11-10）**：scope r1 指出卡面旧范围（字体选择+持久化）与 FEA-00 §705/§706、FEA-15:28「SET 不涉契约字节」不一致。DSH 采纳 **§1.6 窄化口径**：SET = 设置页外观/**字体只读投影**（回退解析+本地预览），**不提供字体选择/持久化**（那需要 C-03/C-02 UNFREEZE，另立卡）；与 FEA-15:28 一致。字体写者仍只有 Theme Studio（Fluent 无 Theme Studio 属已知 limitation，登记不阻塞）。

## Acceptance Criteria（6 条，依 scope r1 §3）

- [x] **AC1 投影正确性**：注入 `ITypographySource` 已知快照 → 「字体」组渲染 3 行（token key / 主题栈原文 / 解析实际族 + 缩放/行高）；source 返回 null/Unavailable → 稳定占位态。 <<MET>>
- [x] **AC2 回退解析纯函数矩阵**：`TypographyResolver.Resolve(["Missing A","Installed B","sans-serif"])` → `resolved="Installed B"`、`missing=["Missing A"]`、`fallback` 标记正确；全缺失 → generic。 <<MET>>
- [x] **AC3 零全局副作用**：渲染/切换前后 `Application.Current.Resources[NmKeys.FontFamily.*]` 与 `Application.Styles` 引用/值不变；样例控件自定义字体不外溢。 <<MET>>
- [x] **AC4 无 AppData 写入**：测试前后真实 `%APPDATA%\NewManga` 的 `presentation-settings.json`/`themes\` 字节与 mtime 不变（复用既有 red-line 断言）。 <<MET>>
- [x] **AC5 UI/逻辑分离 + 只读门禁 + a11y**：`SettingsViewModel` 可在无 Avalonia Application 的测试中构造（fake source）；组枚举/搜索命中（`字体`/`typography.ui`）/只读态；Host 只读时一致。 <<MET>>
- [x] **AC6 边界与零契约变更**：`git diff --name-only` 不含 `doc/plan/**`、`doc/contracts/**`、`tools/governance/**`、`doc/tasks/FEA-13*`；`verify_pins` 18/18；`check.ps1`（默认 + `-TaskPath`）PASS；diff ⊆ 16 paths。 <<MET>>

## 证据计划（L2）

`verification/FEA-14-SET-1/`：README（AC 映射）、`logs/`（pytest 定向/App.Tests 全量/门禁）、字体回退矩阵探针、AppData 前后指纹、截图/预览说明。截图若无法在 CI 生成 → 记 NOT_RUN（不冒充 PASS）。

## 风险与回退

| 风险 | 处置 |
|---|---|
| 用户预期「设置页能选字体」 | 文案与 scope 明确「字体族属主题」；选择功能须 UNFREEZE（另立卡） |
| 字体探测慢/跨平台 | 纯函数 resolver + 注入 source；探测失败 → 缺失列表 + generic |
| AppData 写入 | 只读 + red-line 断言（AC4） |
| 回退 | `git revert` 实现提交；零契约/schema 变更 |

## 背景

FEA 线 S5 剩余六切片（SET/FONT/LIB/READ/EDIT/AI）尚未建卡；本卡为**第一切片占位**，用于 DAG 推进与范围冻结入口。FEA-13（备份/恢复/迁移）已收口（SRC-6 完成于 2026-11-10）。

## 预估范围（待 scope review）

| 项 | 预估 |
|---|---|
| 设置面板 | Fluent 风格设置页与既有 settings IPC 面的对齐（C-03/P15） |
| 字体 | 字体选择/预览与 Theme Studio 的边界 |
| 契约 | 若需新命令/字段 → 先 scope 裁决（可能触发 UNFREEZE） |
| 证据 | 截图基线 + 交互测试 + 门禁 |

## Acceptance Criteria

- 已冻结并按窄化口径实现（字体组只读投影；r1 findings 处置中）。

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | NOT_APPLICABLE（proposed 占位） | NOT_APPLICABLE | — | — | 未创建 worktree |
| temp | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 无 |
| build | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 无构建 |
| user-data | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 未访问真实数据 |

## Closeout Record

- 未开始（proposed）。
