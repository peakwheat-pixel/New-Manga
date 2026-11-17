---
id: READER-F11-STYLE-SCOPE-1
title: F11 沉浸阅读窗丢失 shell 局部样式（顶/底带变画布色、模式 chip 失去选中高亮）
kind: fix
governance_version: 3
status: proposed
disposition: "条件 3 取证时由独立视觉裁定 visual-c3c 发现（D9）：ImmersiveReaderWindow 未引入 V2LocalStyles，导致同页同态下外壳与主窗口内阅读器不一致"
approval: DSH 2026-11-17（由条件 3 视觉裁定的 D9 触发；范围待冻结）
suggested_owner: DSH
owner: null
reviewer: null
depends_on:
  - MAINT-1-RELEASE-MONITOR
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
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

- [ ] **AC1 现状取证**：`V2LocalStyles.axaml` 仅被 `AppShellV2.axaml:16` 与 `ThemeStudioView.axaml:19` 引入；`ImmersiveReaderWindow` 由 `App.axaml.cs` 的 `WireImmersiveReader` 在代码里构造（无 XAML StyleInclude）⇒ `Border.topband` / `Border.statusband` / `Button.chip.on` 规则（`V2LocalStyles.axaml:53/58/110/118`）在沉浸窗不生效。 <<PARTIAL: 机制已定位，待判定是否有意设计>>
- [ ] **AC2 设计判断**：判定「沉浸态顶/底带应为画布色、chip 不带高亮」是**有意设计**还是**缺陷**；若有意，须给出书面依据（设计契约/PR）；若缺陷，进入 AC3。
- [ ] **AC3 修复（若为缺陷）**：让沉浸窗获得与主窗口一致的局部样式作用域；**不得**改公共样式契约或改其他页面的视觉。
- [ ] **AC4 回归**：同一页同一状态下重截 F11 与主窗口内阅读器，断言外壳一致（或按 AC2 的设计依据断言差异是预期的）；旧截图与新截图并排入证据。
- [ ] **AC5 不虚报**：不改变 Gate 条件判定；不宣称条件 3 因此变化。

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
