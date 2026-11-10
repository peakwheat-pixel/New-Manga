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
- [x] **AC4 无 AppData 写入**：测试前后真实 `%APPDATA%\NewManga` 的 `presentation-settings.json`/`themes\` 字节与 mtime 不变（复用既有 red-line 断言）。 <<MET（theme-settings.json 全量 sha256+size+mtime 基线前后不变，`logs/appdata-redline.log`）；指定 artefact `presentation-settings.json`/`themes\` 本机不存在 → 该两项 **NOT_RUN**，不冒充 PASS>>
- [x] **AC5 UI/逻辑分离 + 只读门禁 + a11y**：`SettingsViewModel` 可在无 Avalonia Application 的测试中构造（fake source）；组枚举/搜索命中（`字体`/`typography.ui`）/只读态；Host 只读时一致。 <<MET（投影行 a11y 名含解析族、`Focusable=true`；Host `WritesAllowed=false` 的字体组视图测试仍 NOT_RUN）>>
- [x] **AC6 边界与零契约变更**：`git diff --name-only` 不含 `doc/plan/**`、`doc/contracts/**`、`tools/governance/**`、`doc/tasks/FEA-13*`；`verify_pins` 18/18；`check.ps1`（默认 + `-TaskPath`）PASS；diff ⊆ 16 allowed_paths。 <<MET（r2 R2-004：`caee4c86a` 新增的渲染测试文件越界；P3 已把渲染测试并入 allowed 的 `SettingsTypographyPanelTests.cs` 并删除该文件，交付链 diff 重新落入 16 条 allowed_paths；主树 pins 18/18、check PASS、禁改目录 0）>>

## 证据计划（L2）

`verification/FEA-14-SET-1/`：README（AC 映射）、`logs/`（pytest 定向/App.Tests 全量/门禁）、字体回退矩阵探针、AppData 前后指纹、截图/预览说明。截图若无法在 CI 生成 → 记 NOT_RUN（不冒充 PASS）。

## 风险与回退

| 风险 | 处置 |
|---|---|
| 用户预期「设置页能选字体」 | 文案与 scope 明确「字体族属主题」；选择功能须 UNFREEZE（另立卡） |
| 字体探测慢/跨平台 | 纯函数 resolver + 注入 source；探测失败 → 缺失列表 + generic |
| AppData 写入 | 只读 + red-line 断言（AC4） |
| locale 小数格式（R2-002） | 资源数值 typed 化 + `InvariantCulture`；de-DE 测试覆盖 |
| face→size 映射漂移（R2-003） | 对齐 `ThemeTokenBaseline.LineHeightTiers`；真实资源断言 Data=12/Display=24 |
| 回退 | `git revert` 实现提交；零契约/schema 变更 |

## r1/r2 处置记录（2026-11-10）

- **r1 复审**（`doc/reviews/FEA-14-SET-1-r1.md`，对 `64c32fa47`）：changes_requested（P0=0/P1=2/P2=7/P3=6）。处置：R-001 完整字体栈（`FamilyNames`，非首族）、R-002 缩放/行高真实读取、R-003/004/005 渲染与资源/指纹判别力、R-006 a11y 名称、R-007 fallback 裁决、R-008 搜索不过滤、R-009/R-014 文档与卡面。
- **r2 复审**（`doc/reviews/FEA-14-SET-1-r2.md`，对 `caee4c86a`）：changes_requested（P0=0/P1=1/P2=6/P3=4）。R-001/R-008 CLOSED；处置如下：
  - R2-001（P1）真实资源路径：新增 `TheSourceProjectsTheRealThemeResources`（真实 `ResourceDictionary`：`FontFamily` + `double` → 3 行/完整栈/scale/lineHeight）。
  - R2-002 locale：资源数值按 `InvariantCulture` 格式化，de-DE 下不再丢行高；`TheSourceIsIndependentOfTheCurrentCulture` 覆盖。
  - R2-003 tier 对齐：face→size 遵循 `ThemeTokenBaseline.LineHeightTiers`（Data→`Nm.FontSize.Sm`=12、Display→`Nm.FontSize.Xxl`=24、Ui→`Nm.FontSize.Md`）。
  - R2-004 写域：`caee4c86a` 新增的渲染测试文件不在 allowed_paths；P3 已把渲染测试并入 allowed 的 `SettingsTypographyPanelTests.cs` 并删除该文件，交付链 diff 重新落入 16 条 allowed_paths。
  - R2-005/R2-007：AC3 改为真实资源对象 `Assert.Same` + Styles 引用序列 + 样例字体不外溢；渲染断言补 3 行/缩放/行高/样例/占位分支/a11y。
  - R2-006：AC4 以真实 `theme-settings.json` 的 sha256+size+mtime 基线为证据，指定 artefact 不存在 → 记 NOT_RUN（不冒充 PASS）。
  - R2-008 裁决记录：见下。R2-009 证据刷新：`verification/FEA-14-SET-1/` 已按本 head 重跑；R2-010：R-012 已由 P3 修复（组合根注入 + 单次读取）；R2-011 残余登记见下。
- **DSH 裁决（R-007 fallback 语义，2026-11-10）**：`Fallback=true` ⟺ 解析族之前**至少一个栈段缺失**（即首个请求族未被使用）；栈仅落到 generic 尾巴且无缺失段 → `Fallback=false`。该裁决定义同步到 scope AC2 口径、实现（`TypographyResolver.Resolve`）、测试与 `TypographyLine.Fallback` XML doc。
- **残余（不阻断，已登记）**：R-006 的 Host `WritesAllowed=false` 字体组视图测试、`SettingsField` 组件级 Tab 语义（组件不在本卡 allowed_paths）→ NOT_RUN；R2-011 的 R-015 样例「按 face 各一行」未做，改为标注「样例使用 `Nm.FontFamily.Ui` 实际字体」；R-011 单 generic 栈无单测（行为已正确）。

## 背景与切片口径（2026-11-10 更新）

- FEA 线 S5 原文为**七切片**（FEA-00 §12.2/§15.6：LIB/READ/EDIT/AI/FONT/SET/**EXPORT**）；`doc/plan/FEA-15-INTEGRATION-ACCEPTANCE.md` §3 与旧卡面写「六切片」并漏掉 EXPORT。
- 本卡是 **SET 视觉子集（设置页字体只读投影）**，不是真实 SET（托盘/退出协调/启动页/语言/通知/更新/诊断预览）——真实 SET 另立卡；EXPORT 是否纳入 S5 由 `FEA-14-S5-PREQ` 裁决（append-only errata，已 MET 的 AC 字节不动）。
- FEA-13（备份/恢复/迁移）已收口（SRC-6 完成于 2026-11-10）。

## 交付链与证据（2026-11-10）

- `64c32fa47`（首版+证据）→ `a0e59ac3b`（r1 处置）→ `caee4c86a`（r1 P2 判别力）→ `4b8f2831c`（P3 清理）→ `b0d5c7d6a`（r2 处置）。
- 证据索引：`verification/FEA-14-SET-1/README.md`；变异 patch 与重放脚本、AppData 红线脚本在 `verification/FEA-14-SET-1/{mutations,scripts}/`。
- 最终交付 head、全量测试/门禁日志与 `canonical_evidence_status` 在收口提交中刷新（`*-final.log`）。

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | `G:\CODEX\New Manga.workspace\worktrees\FEA-14-SET-1-p3`（detached，P3 + r2 修复的隔离构建树） | keep-until-closeout（收口后按 WORKSPACE_GOVERNANCE 移除；无独有未提交内容） | — | 无 | 仅用于构建/测试；最终证据不在 worktree |
| temp | `G:\CODEX\New Manga.workspace\temp\FEA-14-familynames-probe`、`...\temp\FEA-14-planning` | keep-evidence（仓外探针/规划，被证据或后续裁决引用） | — | 无 | 只读被测程序集，不污染仓库 |
| build | worktree `bin/obj`（可重建） | reclaimable | — | 无 | 不在仓库、不被证据引用 |
| user-data | `%APPDATA%\NewManga`（真实目录，只读访问） | read-only-observed | — | `logs/appdata-redline.log` 记录 sha256/size/mtime | 测试前后 `UNCHANGED`；未写入 |

## Closeout Record

- 2026-11-10：**进行中**。r1/r2 findings 已处置（见「r1/r2 处置记录」）；证据目录已按 r2 处置 head 刷新（定向 20 passed、变异 M1/M2 RED、AppData 指纹不变、IPC 0 命令、API inventory EXIT 0）。
- 待办：r3 独立复核（对 `b0d5c7d6a` 之后的新 head）→ 主树最终全量/门禁日志（`logs/*-final.log`）→ 填 `delivery_head`/`canonical_evidence_status`/`integration_commit` → STATUS/PLAN/ledger 切换。
