---
id: FEA-14-SET-1
title: FEA-14 切片 1：设置/字体面板（可切换前端架构线 S5 收口切片）
kind: implementation
governance_version: 3
status: done
approval: **scope review r1（`doc/reviews/FEA-14-SET-1-scope-r1.md`）**：卡面「字体选择+持久化」= NEEDS_UNFREEZE；DSH 2026-11-10 采纳 **§1.6 窄化口径**（字体组 = 只读投影 + 回退解析 + 本地样例预览，零写入/零新持久化/零契约字节）→ **READY-TO-FREEZE**，按本卡冻结实施。
suggested_owner: zcode
owner: dsh
reviewer: r3 独立复核（`doc/reviews/FEA-14-SET-1-r3.md`，approved：P0/P1/P2=0；P3=6 残余已登记）
depends_on:
  - FEA-13-SRC-6
base_commit: c4e40509b
branch: null
worktree: null
integration_commit: c543b51cc
delivery_head: c543b51cc
canonical_evidence_status: complete
resource_closeout_status: complete
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

# FEA-14-SET-1：设置/字体面板（字体只读投影）

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
- [x] **AC6 边界与零契约变更**：`git diff --name-only` 不含 `doc/plan/**`、`doc/contracts/**`、`tools/governance/**`、`doc/tasks/FEA-13*`；`verify_pins` 18/18；`check.ps1`（默认 + `-TaskPath`）PASS；diff ⊆ 16 allowed_paths。 <<MET>>

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

- `64c32fa47`（首版+证据）→ `a0e59ac3b`（r1 处置）→ `caee4c86a`（r1 P2 判别力）→ `4b8f2831c`（P3 清理）→ `b0d5c7d6a`（r2 处置）→ `128469abd`/`396e31efe`（主树最终证据）→ **`c543b51cc`（r3 处置 + r3 报告；delivery_head / integration_commit）**。
- 证据索引：`verification/FEA-14-SET-1/README.md`；变异 patch 与重放脚本、AppData 红线脚本在 `verification/FEA-14-SET-1/{mutations,scripts}/`。
- 最终证据（交付树）：`logs/dotnet-app-tests-final.log`（858/0/11）、`logs/dotnet-typography-final.log`（定向 41/0）、`logs/gates-check-final.log`、`logs/gates-pins-final.log`（18/18）、`logs/api-inventory.log`（EXIT 0）、`logs/appdata-redline.log`（UNCHANGED）、`logs/ipc-replay.log`（0 命令）、`logs/mutations-replay.log`（M1/M2 RED）。

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | `G:\CODEX\New Manga.workspace\worktrees\FEA-14-SET-1-p3`（detached，P3 + r2/r3 修复的隔离构建树） | NOT_APPLICABLE | — | — | 保留原位：提交已全部快进进入 main，无独有提交，按 WORKTREE_SAFETY_INVENTORY 暂不删除；仅用于构建/测试 |
| temp | `G:\CODEX\New Manga.workspace\temp\FEA-14-familynames-probe`、`...\temp\FEA-14-planning` | NOT_APPLICABLE | — | — | 仓外探针/规划（被证据引用），保留原位；只读被测程序集，不污染仓库 |
| build | — | NOT_APPLICABLE | — | 无 | 不在仓库、不被证据引用 |
| user-data | C:/Users/49745/AppData/Roaming/NewManga | PRESERVE_USER_DATA | — | `logs/appdata-redline.log` 记录 sha256/size/mtime | 测试前后 `UNCHANGED`；未写入 |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-S1-001 | AC1-AC6 | `verification/FEA-14-SET-1/logs/api-inventory.log` | `-` | `502cadb0bd166737f248c3ef689d55ad1a6013a94f58e4768578857bae7191d0` | CANONICAL |
| EV-S1-002 | AC1-AC6 | `verification/FEA-14-SET-1/logs/appdata-redline.log` | `-` | `5b7173df930fe6075d493c379c045947f9554d3d7ba7607a7c3dddaf875fd525` | CANONICAL |
| EV-S1-003 | AC1-AC6 | `verification/FEA-14-SET-1/logs/dotnet-app-tests-final.log` | `-` | `782b2f6dbae878b3b21a188eb344dbe05e87953124c5b9914a68ec4ee4053210` | CANONICAL |
| EV-S1-004 | AC1-AC6 | `verification/FEA-14-SET-1/logs/dotnet-app-tests.log` | `-` | `0b42dbf9b43e72f3e4ceecae6749644fa0a9f26148b5d327e92cc9f6645a55b0` | CANONICAL |
| EV-S1-005 | AC1-AC6 | `verification/FEA-14-SET-1/logs/dotnet-typography-final.log` | `-` | `e9ced2ecbf3f64f91255b42546371e8fc677161155255f47b27fbe96fbb306da` | CANONICAL |
| EV-S1-006 | AC1-AC6 | `verification/FEA-14-SET-1/logs/dotnet-typography-tests.log` | `-` | `62dac1b081567814a8f457d18a5f8f1e1d65901cb6a3f5f8a3f6cff9c8d895e3` | CANONICAL |
| EV-S1-007 | AC1-AC6 | `verification/FEA-14-SET-1/logs/gates-check-final.log` | `-` | `421cb0d718d02c2b1d3442c3fa2dc905025978c5110d52225ed7d197fad9c182` | CANONICAL |
| EV-S1-008 | AC1-AC6 | `verification/FEA-14-SET-1/logs/gates-check.log` | `-` | `f5ef05444fdf2aacecda340db9174405e49ab8537b33b7380c5cf86bc7728a2b` | CANONICAL |
| EV-S1-009 | AC1-AC6 | `verification/FEA-14-SET-1/logs/gates-pins-final.log` | `-` | `e646914996589ad17e738de240c919428bdff7de2024fcf9dcd7be099e8c1dcb` | CANONICAL |
| EV-S1-010 | AC1-AC6 | `verification/FEA-14-SET-1/logs/gates-pins.log` | `-` | `fc54e273bc5595af004e551764954786936b58348208ec31b00266c7d1dc9b0b` | CANONICAL |
| EV-S1-011 | AC1-AC6 | `verification/FEA-14-SET-1/logs/ipc-replay.log` | `-` | `a6d70d7a0cfda5952b72b85356b3cb85cd187ce0f5274dbfcd093f6556e11c91` | CANONICAL |
| EV-S1-012 | AC1-AC6 | `verification/FEA-14-SET-1/logs/mutations-replay.log` | `-` | `eb98a4d87fd7d0b6c1e57b01d7fdfc3ab51507c378ba2953af5d784e64c8ad55` | CANONICAL |
| EV-S1-013 | AC1-AC6 | `verification/FEA-14-SET-1/logs/typography-fallback.log` | `-` | `a13a164e5ef52dd8e1a9fe3c70a8889cdaf14b7749d8da557f1101b187c88eb8` | CANONICAL |
| EV-S1-014 | AC1-AC6 | `verification/FEA-14-SET-1/mutations/M1-missing-not-recorded.log` | `-` | `c835da386e5894209b8e02e202abeac52dd7c001ac9ec19ef438bba96e879893` | CANONICAL |
| EV-S1-015 | AC1-AC6 | `verification/FEA-14-SET-1/mutations/M1-missing-not-recorded.patch` | `-` | `ec3e8afbe0226fc3eb919b1779a0d903919d7979383cf12ee6964ca5c1481e25` | CANONICAL |
| EV-S1-016 | AC1-AC6 | `verification/FEA-14-SET-1/mutations/M2-stack-head-not-resolved.log` | `-` | `e79ad086725f624d1abf42e34202edf125e88820bb0c74c1f116afa49ca70a91` | CANONICAL |
| EV-S1-017 | AC1-AC6 | `verification/FEA-14-SET-1/mutations/M2-stack-head-not-resolved.patch` | `-` | `497ba55cf22dd8fe60c11fb8c44d370df2eb4866406b58462275846131552c07` | CANONICAL |
| EV-S1-018 | AC1-AC6 | `verification/FEA-14-SET-1/mutations/replay-mutations.ps1` | `-` | `22bb7fbde547672a0b80405b78edceaa977bce19cdc28fd96561cd356ad80f48` | CANONICAL |
| EV-S1-019 | AC1-AC6 | `verification/FEA-14-SET-1/README.md` | `-` | `40f6e4144e780c7e4a6a05d29708b52d36456cdfd6c0870213c053d06da144d3` | CANONICAL |
| EV-S1-020 | AC1-AC6 | `verification/FEA-14-SET-1/scripts/appdata-redline.ps1` | `-` | `bd843c5d7750e95eaa22c4f42f262e8611bb060a968a2a3d9df3c07587215138` | CANONICAL |

## Closeout Record

- 结论：**完成**（2026-11-10）。3 轮独立复核：r1 changes_requested（P1=2）→ r2 changes_requested（P1=1）→ **r3 approved（P0/P1/P2=0；P3=6 均为文档/证据精度与已登记残余）**。
- 交付证据：AC1–AC6 逐项见卡面与 `verification/FEA-14-SET-1/README.md`；交付树全量 App.Tests **858/0/11**、定向 **41/0**、`verify_pins` **18/18**、`check.ps1`（默认 + `-TaskPath`）PASS、API inventory EXIT 0、变异 M1/M2 RED、AppData 指纹 UNCHANGED、IPC 0 命令。
- 残余 limitation（不阻断，已登记）：Host `WritesAllowed=false` 字体组视图测试 = NOT_RUN；真实 Tab 遍历 = NOT_RUN；样例按 face 各一行未做（改为标注 Ui 面）；单 generic 栈无单测（行为已正确）；真实 UI 截图 / 真实用户主题包经 ThemeService 应用后投影 / `%APPDATA%\NewManga` 指定 artefact = NOT_RUN（本机不存在）；R3-003 共享 `Application.Initialize(Dark)` 不在测试内还原（全量绿，属顺序依赖风险提示）。
- 零契约字节（C-03/C-02/P15/C-07 未改）；18 pins 全绿；未 push（本次无 push 授权动作）。
