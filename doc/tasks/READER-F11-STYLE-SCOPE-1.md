---
id: READER-F11-STYLE-SCOPE-1
title: F11 沉浸阅读窗丢失 shell 局部样式（顶/底带变画布色、模式 chip 失去选中高亮）
kind: fix
governance_version: 3
status: closed_with_limitations
disposition: "条件 3 取证时由独立视觉裁定 visual-c3c 发现（D9）：ImmersiveReaderWindow 未引入 V2LocalStyles，导致同页同态下外壳与主窗口内阅读器不一致"
approval: DSH 2026-11-17（由条件 3 视觉裁定的 D9 触发；范围待冻结）
suggested_owner: DSH
owner: DSH
reviewer: reviewer-f11s（DSH 子 agent，独立上下文，未参与实现；2026-11-17 收口复核）
depends_on:
  - MAINT-1-RELEASE-MONITOR
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: 9581336ae
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/READER-F11-STYLE-SCOPE-1
allowed_paths:
  - doc/tasks/READER-F11-STYLE-SCOPE-1.md
  - doc/reviews/READER-F11-STYLE-SCOPE-1-*.md
  - doc/reviews/MAINT-1-GATE-CONDITION-3-VISUAL-ADJUDICATION-2026-11-17.md
  - doc/REBASELINE_PLAN.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - verification/READER-F11-STYLE-SCOPE-1/**
  - apps/desktop-avalonia/src/NewManga.App/Shell/V2/ImmersiveReaderWindow.cs
---

# READER-F11-STYLE-SCOPE-1：F11 沉浸阅读窗丢失 shell 局部样式

## 来源与目标

2026-11-17 为关闭 Release Gate 条件 3 做真实窗口取证时，独立视觉裁定 `visual-c3c`
（`doc/reviews/MAINT-1-GATE-CONDITION-3-VISUAL-ADJUDICATION-2026-11-17.md` 第三次裁定，D9）发现：

- `V2LocalStyles` 只被 `AppShellV2.axaml` 引入，`ImmersiveReaderWindow`（`App.axaml.cs:516` 处 `new ImmersiveReaderWindow(shell.ViewModel.Library.Reader)`）**未引入**；
- 结果：F11 沉浸窗里 **顶带/底带由白色变画布底色**、**模式 chip（分页 / Webtoon 纵向 / RTL）失去选中高亮**；
- 两帧（主窗口内阅读器 vs F11）**页面重叠区 2,296,160 px 差异 0**，差异**只在**外壳 ⇒ 不是内容问题，是样式作用域问题。

**一个可观察交付结果**：F11 沉浸窗与主窗口内阅读器在**同一页同一状态**下，顶/底带与 chip 选中态的**视觉表现一致**（或有明确、书面的"沉浸态本就不同"设计依据）。

## Acceptance Criteria

- [x] **AC1 现状取证**：`V2LocalStyles.axaml` 仅被 `AppShellV2.axaml:16` 与 `ThemeStudioView.axaml:19` 引入；`ImmersiveReaderWindow` 由 `App.axaml.cs` 的 `WireImmersiveReader` 在代码里构造（无 XAML StyleInclude）⇒ `Border.topband` / `Border.statusband` / `Button.chip.on` 规则（`V2LocalStyles.axaml:53/58/110/118`）在沉浸窗不生效。 <<MET>>
- [x] **AC2 设计判断**：判定「沉浸态顶/底带应为画布色、chip 不带高亮」是**有意设计**还是**缺陷**；若有意，须给出书面依据（设计契约/PR）；若缺陷，进入 AC3。 <<MET>>
- [x] **AC3 修复（若为缺陷）**：让沉浸窗获得与主窗口一致的局部样式作用域；**不得**改公共样式契约或改其他页面的视觉。 <<MET>>
- [x] **AC4 回归**：同一页同一状态下重截 F11 与主窗口内阅读器，断言外壳一致（或按 AC2 的设计依据断言差异是预期的）；旧截图与新截图并排入证据。 <<MET>>
- [x] **AC5 不虚报**：不改变 Gate 条件判定；不宣称条件 3 因此变化。 <<MET>>

## 允许修改范围

- 本卡、`doc/reviews/READER-F11-STYLE-SCOPE-1-*.md`、`verification/READER-F11-STYLE-SCOPE-1/**`。
- 实现时仅允许改 `ImmersiveReaderWindow` 的样式作用域引入（精确文件在 AC1 确认后写入卡面）；**不得**改 `V2LocalStyles` 的内容或其它页。

## 禁止范围

- 不得改共享样式契约、设计 token、其他空间视觉。
- 不得为"看起来一致"而删除主窗口的样式引入。
- 不得把本卡当作条件 3 / 条件 4 的证据。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 读源码 + 复现 | 无 | NOT_RUN | 无 |
| AC2 | 设计依据核对 | 设计文档 | NOT_RUN | 无 |
| AC4 | F11 与主窗口同页对照截图 | 真实窗口 | NOT_RUN | 无 |

## 依赖、风险与阻塞

- 依赖 `MAINT-1-RELEASE-MONITOR`（条件 3 取证产生该发现）。
- **风险 R1**：可能本就有意（沉浸态更"干净"）；若确认有意，本卡以 `closed_with_limitations` 收口并记录设计依据，**不强行改 UI**。
- **风险 R2**：改动沉浸窗的样式作用域可能影响性能或主题切换，需重跑主题相关测试。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无（须独立上下文）。
- 实际测试：尚无。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) | sha256_basis |
|---|---|---|---|---|---|---|
| EV-F11S-01 | AC1/AC3/AC4 修复与像素对照 | verification/READER-F11-STYLE-SCOPE-1/README.md | 9581336ae | fefeba92a5e2ea3d2f4f73332133d6c6a77f6d1e4aacb9ec58a7142e9f7504db | CANONICAL | BLOB |
| EV-F11S-02 | AC4 修复后 F11 整屏 | verification/READER-F11-STYLE-SCOPE-1/rf11s-01-after-f11.jpg | 9581336ae | bd9751dc4b835caa9b1d4f5e77a86ccbe693af3b6b8eca9f64016b310fd98be3 | CANONICAL | BLOB |
| EV-F11S-03 | AC4 修复后主窗口内阅读器 | verification/READER-F11-STYLE-SCOPE-1/rf11s-02-after-inwindow.jpg | 9581336ae | b7f6bbce33ea7b0c3feaf2b175f787aaef23c84658c30e9f947edc52c5a82dc7 | CANONICAL | BLOB |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | verification/READER-F11-STYLE-SCOPE-1/ | NOT_APPLICABLE | — | — | 2 张截图 + README 已登记于 Canonical Evidence；无迁移/归档/删除 |
| agent-output | verification/READER-F11-STYLE-SCOPE-1/ | NOT_APPLICABLE | — | — | 证据目录只有 3 个文件（1 README + 2 JPG），全部已登记；Debug 构建产物在 `src/**/bin`（.gitignore 覆盖），不属于交付物，未迁移未删除 |

## Closeout Record（2026-11-17，DSH）

- canonical_evidence_status：`complete`；resource_closeout_status：`complete`；删除/迁移/归档：**0**。
- **AC2 设计判断**：判为**缺陷**而非有意设计 —— 依据：沉浸窗与主窗口用的是**同一个 `ReaderOverlay` 控件**，
  顶/底带与模式 chip 的语义类（`topband`/`statusband`/`chip.on`）本就为该控件定义；同一控件在两处外观不一致，且 chip 丢失选中态会让用户无法辨认当前模式。
  没有找到任何"沉浸态应去掉这些样式"的设计依据文件。
- **AC3 修复**：`ImmersiveReaderWindow` 构造时加 `V2LocalStyles.axaml` 的 `StyleInclude`；**未改**该样式表内容、未改其它页面。
- **AC4 判别力**：修复前顶/底带 `(244,243,240)`（画布色）→ 修复后 `(255,255,255)`（Panel 白）；chip 恢复 Accent 高亮；画布与进度轨道线不变。
- **限制**：
  1. 证据来自 **Debug 构建**；**已发布产物（stage/setup.exe）仍是修复前行为** —— 需重新 publish + 打包才进安装包（不在本卡范围）。
  2. 未覆盖深色主题下同组对照、分页模式下的 chip 高亮、缩放/DPI。
  3. 本次修复使条件 3 的 `c3-06` 截图成为"修复前状态"；条件 3 结论不受影响（全屏/无边框/内容渲染仍成立）。
- **边界**：不改变任何 Gate 判定；`Technical Gate=NOT_SATISFIED` 不变。
