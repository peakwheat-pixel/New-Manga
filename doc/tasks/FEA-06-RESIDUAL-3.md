---
id: FEA-06-RESIDUAL-3
title: Fluent 视觉/状态残项补做（5 格→4 格 + Tab/a11y 属性；原 RESIDUAL-2 BLOCKED 表重开）
kind: implementation
governance_version: 3
status: ready
approval: 用户 2026-11-08 残余收口指令（R2）；独立 scope review `doc/reviews/FEA-06-RESIDUAL-3-scope-r1.md`（session `8389e539-…`，verdict **NOT_RECOMMENDED** → DSH 按其 §2/§5 5 项改写后冻结）；DSH 2026-11-08 裁决（`doc/reviews/ADJ-2026-11-RESIDUAL-WAIVER.md` §7.4）：UI-only、0 pin、窄口径 done
suggested_owner: dsh
owner: fea06-residual3-impl
reviewer: 独立上下文 fresh subagent（不得由实现会话/实例自审；r1 指派于实现交付后）
depends_on:
  - FEA-06-RESIDUAL-2
base_commit: 5cbec0e82
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-06-RESIDUAL-3
allowed_paths:
  - doc/tasks/FEA-06-RESIDUAL-3.md
  - doc/tasks/FEA-06-RESIDUAL-2.md
  - doc/reviews/FEA-06-RESIDUAL-3-*.md
  - doc/handoffs/FEA-06-RESIDUAL-3-*.md
  - verification/FEA-06-RESIDUAL-3/**
  - doc/REBASELINE_PLAN.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/src/NewManga.App/Views/Fluent/**
  - apps/desktop-avalonia/src/NewManga.App/ViewModels/Fluent/**
  - apps/desktop-avalonia/tests/NewManga.App.Tests/**
out_of_scope:
  - **0 pin 硬边界**：`Services/IHostController.cs`、`Services/RunContracts.cs`（API inventory/C-07 抽取面）、`Shell/V2/**`、`ViewModels/V2/**`、`Views/V2/**`、`Services/FrontendHostCoordinator.cs`、`FrontendSelector.cs`、`NewManga.DesignSystem/Generated/**`、`doc/design/**`、`doc/plan/**`、`doc/contracts/**`
  - 不引用 V2 映射（`StudioRunControllerDataSource`/`IRunDataSource`/`StudioRunProjection`）；Fluent 侧自建映射
  - **格 3「RegionBox 冲突态（查看对照）」→ re-home `FEA-06-RESIDUAL-4`**（需新命令过 `IHostController`，C-07 additive → 违反 0 pin）
  - 原生 a11y 行为（Narrator/屏幕阅读器）、200% DPI 像素、原生桌面截图 → `NOT_APPLICABLE`（原生交互未执行，保留 `NOT_RUN`）
  - 真实用户数据/AppData/外部卷；L3/L4 真机走查（`NOT_RUN`）
---

# FEA-06-RESIDUAL-3：Fluent 视觉/状态残项补做（0 pin，UI-only）

> **状态 `ready`**（base `5cbec0e82`；0 pin）。目标：把 `FEA-06-RESIDUAL-2` 的 6 行 BLOCKED 表**重开**——4 格 + Tab/a11y 属性在本卡做完；**格 3 与原生项走 re-home/NA**。
> **术语落表（评审要求，必须逐字使用）**：
> - **七状态**（批量矩阵行）：`Queued / Running / Done / Failed / Blocked / Stale / Skipped`。
> - **9 行**（工作台状态表，按序）：`RunId / RunStatus / OverallProgress / CurrentPageId / CurrentStepType / Completed / Failed / Skipped / Blocked`（全部取自 `TaskProjectionInfo`）。
> - **Tab 口径（DSH 裁决=评审方案 a）**：`Library/Reader/Settings` 三空间做**完整焦点遍历**；`Studio` 空间断言「`Tab` = 模式切换（`03-accessibility.md:13` 优先）」+「页签条聚焦时 `←/→` 切页签」（后者本卡补实现）。**不改全局 Tab 绑定**。

## 缺陷/缺口（base `5cbec0e82`，评审已核）

- 格 1：`WorkbenchPageView.cs:279-308` 批量矩阵为占位（硬编码「批量 Run 投影…端口尚未接入」）；吸顶表头未实现；`RunProjectionBar` 未绑投影。
- 格 2：`ReaderPageView.cs:67` 只有单页 `_pageImage`；`:99/:173` 只翻布尔，不加载第二页；`Layout`（`ReaderViewModel.cs:66`）未被消费。
- 格 4：`ShelfViewModel.cs:151` 只有计数，无 `Σ PageCount` 聚合。
- 格 5：`WorkbenchPageView.cs:292-318` 控制台 9 行为占位。
- a11y：Fluent 无 UIA 树/名称断言；工作台页签条无 `←/→`。
- **格 3（RegionBox 冲突态）**：无数据面（`RegionSummary` 无冲突字段；`list_page_region_texts` 未过 `IHostController`）→ 见 Out。

## Acceptance Criteria（冻结）

- [ ] **AC-1（格 1：Run 投影两控制面）**：批量空态「开始处理」⇒ **恰好 1 次** `StartRunAsync`（`Command=translate_all` + chapter scope；`IdempotencyKey` 非空、重试复用同键）；随后 `GetTaskProjectionAsync` 轮询 ≥2 次；注入覆盖七状态的投影 ⇒ 矩阵逐格呈现对应文案（非仅颜色）；内容滚动后表头 `TranslatePoint` 屏幕 Y 不变（吸顶）；无投影时 `RunProjectionBar` 保持既有诚实空态（不得伪造进度）。 <<MET>>
- [ ] **AC-2（格 5：Console 9 行）**：9 行逐字段等于注入投影（按上文顺序）；`暂停/停止/继续/重试` 的 `IsEnabled` **完全**取自 `TaskProjectionInfo.Controls`；禁用态点击产生 **0 帧** `ControlRunAsync`；`Counts` 缺失显示「—」而非 0。 <<MET>>
- [ ] **AC-3（格 2：Reader 双页/滚动）**：双页模式对 `Pages[i]`/`Pages[i+1]` 各 1 次 `LoadImageAsync` 且 pageId 不同；末页只 1 次；滚动模式（`IsWebtoon`/`Layout=webtoon_vertical`）连续页可滚动且 `SaveReadingProgressAsync` 收到 `scrollOffsetY>0`；单页模式不回归。 <<MET>>
- [ ] **AC-4（格 4：书架统计，自洽聚合口径）**：状态条 = `"{FilteredBooks.Count} / {Books.Count} 部作品"` + `ΣPageCount`（`PageCount==null` 显示「—」且不计入）；筛选后/空/只读三态各 1 断言；**源码断言零新增命令**（`HostCommandRegistry` 命令集合与卡前逐字节相同）。 <<MET>>
- [ ] **AC-5（Tab 遍历 + a11y 属性/UIA 树，方案 a）**：A1 覆盖性遍历（三空间 `S⊇F(P)`、无连续重复；`TopLevel.KeyPress(Key.Tab)` + `FocusManager.GetFocusedElement()`）；A2 隐藏不入序；A3 `peer.GetName()` 非空且非类型名；A4 `GetAutomationControlType()` 白名单；A5 UIA 树每可交互节点有名 + 浮层开关焦点往返；Studio 断言 `Tab`=模式切换 + 页签条 `←/→` 生效（本卡实现）。 <<MET>>
- [ ] **AC-6（证据/门禁/done 口径）**：默认零仓库写入（跑前后 `git status --porcelain -- verification` 相等；`verification/FEA-06/**`、`verification/FEA-06-RESIDUAL-2/**` 恒空）；opt-in `NEWMANGA_CAPTURE_RESIDUAL3_PNGS=1` 写 9 图 + inventory（SHA256/签署，**像素不作 AC**）；全量 `.NET ≥1705/0/98`、pytest `≥3390/10`、pins 18/18、`check.ps1` PASS、API `--check` EXIT 0；`git diff --stat` 不含 `Views/V2|ViewModels/V2|Shell/V2|Services|DesignSystem/Generated`；`FEA-06-RESIDUAL-2` append-only 关闭记录 + **显式「done 不覆盖 BLOCKED 表」** + 格 3 re-home 具名卡。 <<MET>>

## 实现口径

1. 只改 `Views/Fluent/**`、`ViewModels/Fluent/**`、`tests/NewManga.App.Tests/**`、本卡/评审/handoff/证据与 PLAN/STATUS/ledger。
2. Run 投影：Fluent 自持意图键 + 1s 轮询（`DispatcherTimer` 必须在 detach/切前端停止并断言停止后不再发请求）；映射不引用 V2 类型。
3. 三处既有断言**改写而非删除**：`FluentPageTests.cs:171-173`、`FluentResidualBatchATests.cs:117-127`、`:559-594`（改为按类型/`AutomationProperties.Name` 定位，保留"无假数据"不变量）。
4. 提交显式 pathspec，禁 `git add -A`；含中文改动用 edit/Python UTF-8。

## 行文口径（红线）

- 不得写「FEA-06-RESIDUAL-2 全部关闭 / UI L1–L10 关闭 / 完全实现」；只写「4 格 + Tab/a11y 关闭；格 3 与原生项 re-home/NA」。
- `NOT_RUN` 不得写成 PASS；像素/快照不得作为 AC 判据。
