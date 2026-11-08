---
id: FEA-06-RESIDUAL-3
title: Fluent 视觉/状态残项补做（5 格→4 格 + Tab/a11y 属性；原 RESIDUAL-2 BLOCKED 表重开）
kind: implementation
governance_version: 3
status: done
approval: 用户 2026-11-08 残余收口指令（R2）；独立 scope review `doc/reviews/FEA-06-RESIDUAL-3-scope-r1.md`（session `8389e539-…`，verdict **NOT_RECOMMENDED** → DSH 按其 §2/§5 5 项改写后冻结）；DSH 2026-11-08 裁决（`doc/reviews/ADJ-2026-11-RESIDUAL-WAIVER.md` §7.4）：UI-only、0 pin、窄口径 done
suggested_owner: dsh
owner: fea06-residual3-impl
reviewer: 独立上下文 fresh subagent（不得由实现会话/实例自审；r1 指派于实现交付后）
depends_on:
  - FEA-06-RESIDUAL-2
base_commit: 5cbec0e82
branch: null
worktree: null
integration_commit: ddc29ecb3
delivery_head: ddc29ecb3
canonical_evidence_status: complete
resource_closeout_status: complete
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

- [x] **AC-1（格 1：Run 投影两控制面）**：批量空态「开始处理」⇒ **恰好 1 次** `StartRunAsync`（`Command=translate_all` + chapter scope；`IdempotencyKey` 非空、重试复用同键）；随后 `GetTaskProjectionAsync` 轮询 ≥2 次；注入覆盖七状态的投影 ⇒ 矩阵逐格呈现对应文案（非仅颜色）；内容滚动后表头 `TranslatePoint` 屏幕 Y 不变（吸顶）；无投影时 `RunProjectionBar` 保持既有诚实空态（不得伪造进度）。 <<MET>>
- [x] **AC-2（格 5：Console 9 行）**：9 行逐字段等于注入投影（按上文顺序）；`暂停/停止/继续/重试` 的 `IsEnabled` **完全**取自 `TaskProjectionInfo.Controls`；禁用态点击产生 **0 帧** `ControlRunAsync`；`Counts` 缺失显示「—」而非 0。 <<MET>>
- [x] **AC-3（格 2：Reader 双页/滚动）**：双页模式对 `Pages[i]`/`Pages[i+1]` 各 1 次 `LoadImageAsync` 且 pageId 不同；末页只 1 次；滚动模式（`IsWebtoon`/`Layout=webtoon_vertical`）连续页可滚动且 `SaveReadingProgressAsync` 收到 `scrollOffsetY>0`；单页模式不回归。 <<MET>>
- [x] **AC-4（格 4：书架统计，自洽聚合口径）**：状态条 = `"{FilteredBooks.Count} / {Books.Count} 部作品"` + `ΣPageCount`（`PageCount==null` 显示「—」且不计入）；筛选后/空/只读三态各 1 断言；**源码断言零新增命令**（`HostCommandRegistry` 命令集合与卡前逐字节相同）。 <<MET>>
- [x] **AC-5（Tab 遍历 + a11y 属性/UIA 树，方案 a）**：A1 覆盖性遍历（三空间 `S⊇F(P)`、无连续重复；`TopLevel.KeyPress(Key.Tab)` + `FocusManager.GetFocusedElement()`）；A2 隐藏不入序；A3 `peer.GetName()` 非空且非类型名；A4 `GetAutomationControlType()` 白名单；A5 UIA 树每可交互节点有名 + 浮层开关焦点往返；Studio 断言 `Tab`=模式切换 + 页签条 `←/→` 生效（本卡实现）。 <<MET>>
- [x] **AC-6（证据/门禁/done 口径）**：默认零仓库写入（跑前后 `git status --porcelain -- verification` 相等；`verification/FEA-06/**`、`verification/FEA-06-RESIDUAL-2/**` 恒空）；opt-in `NEWMANGA_CAPTURE_RESIDUAL3_PNGS=1` 写 9 图 + inventory（SHA256/签署，**像素不作 AC**）；全量 `.NET ≥1705/0/98`、pytest `≥3390/10`、pins 18/18、`check.ps1` PASS、API `--check` EXIT 0；`git diff --stat` 不含 `Views/V2|ViewModels/V2|Shell/V2|Services|DesignSystem/Generated`；`FEA-06-RESIDUAL-2` append-only 关闭记录 + **显式「done 不覆盖 BLOCKED 表」** + 格 3 re-home 具名卡。 <<MET>>

## 实现口径

1. 只改 `Views/Fluent/**`、`ViewModels/Fluent/**`、`tests/NewManga.App.Tests/**`、本卡/评审/handoff/证据与 PLAN/STATUS/ledger。
2. Run 投影：Fluent 自持意图键 + 1s 轮询（`DispatcherTimer` 必须在 detach/切前端停止并断言停止后不再发请求）；映射不引用 V2 类型。
3. 三处既有断言**改写而非删除**：`FluentPageTests.cs:171-173`、`FluentResidualBatchATests.cs:117-127`、`:559-594`（改为按类型/`AutomationProperties.Name` 定位，保留"无假数据"不变量）。
4. 提交显式 pathspec，禁 `git add -A`；含中文改动用 edit/Python UTF-8。

## 行文口径（红线）

- 不得写「FEA-06-RESIDUAL-2 全部关闭 / UI L1–L10 关闭 / 完全实现」；只写「4 格 + Tab/a11y 关闭；格 3 与原生项 re-home/NA」。
- `NOT_RUN` 不得写成 PASS；像素/快照不得作为 AC 判据。

## Canonical Evidence

> `commit`：实现文件填其所在提交；closeout 证据填 `-`（sha 见 handoff §31）。sha256 为工作树字节口径。

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-01 | AC-1/AC-2 | apps/desktop-avalonia/src/NewManga.App/ViewModels/Fluent/FluentRunProjection.cs | ddc29ecb3 | 35a60eeec31480a11d6853ae48179cbf287e1f68e2113b81163f8962ec8c39a6 | SOURCE_PIN |
| EV-02 | AC-1/AC-2/AC-5 | apps/desktop-avalonia/src/NewManga.App/ViewModels/Fluent/WorkbenchViewModel.cs | ddc29ecb3 | efc08a81a1777885eeb67eca6bd8dc29a990e35911fe7a573615c74698346256 | SOURCE_PIN |
| EV-03 | AC-3 | apps/desktop-avalonia/src/NewManga.App/ViewModels/Fluent/ReaderViewModel.cs | ddc29ecb3 | e27c1c8b06c0e6d08ce84e269906c2a2adbb7db52a88a97a92a5464ceaa8e955 | SOURCE_PIN |
| EV-04 | AC-4 | apps/desktop-avalonia/src/NewManga.App/ViewModels/Fluent/ShelfViewModel.cs | ddc29ecb3 | 0900a2e44fef213c559d8f7d56828e2afcb17657582330aac8001937efe3c799 | SOURCE_PIN |
| EV-05 | AC-1/AC-2/AC-5 | apps/desktop-avalonia/src/NewManga.App/Views/Fluent/WorkbenchPageView.cs | ddc29ecb3 | ce91937710efb5d27d67a4567cb08b38f82b8073fd7ca990709d99a1acad4957 | SOURCE_PIN |
| EV-06 | AC-3 | apps/desktop-avalonia/src/NewManga.App/Views/Fluent/ReaderPageView.cs | ddc29ecb3 | 9bc8da75f0df127d351b37f17f805508562c6123eb878f0c961a620e7cf1aa1c | SOURCE_PIN |
| EV-07 | AC-4 | apps/desktop-avalonia/src/NewManga.App/Views/Fluent/ShelfPageView.cs | ddc29ecb3 | f0c60befe0261e9eff6cbf7ff6ed8dc686f656a239406e4dd189f33e89d122c0 | SOURCE_PIN |
| EV-08 | AC-5 | apps/desktop-avalonia/src/NewManga.App/Views/Fluent/SettingsPageView.cs | ddc29ecb3 | 5d3e492f320e6379f3a0026746484a7786d13a4beaf274209a34d7851f6fee40 | SOURCE_PIN |
| EV-09 | AC-1…AC-5 | apps/desktop-avalonia/tests/NewManga.App.Tests/FluentResidual3Tests.cs | ddc29ecb3 | 2eb6ad1a0e31beb92fe286d0f4ef1ed57164c045f6fb6c374aec8271377232c6 | SOURCE_PIN |
| EV-10 | AC-6 | apps/desktop-avalonia/tests/NewManga.App.Tests/FluentResidual3VisualEvidenceTests.cs | ddc29ecb3 | 5d76100bb471119d604b8e52db898ce6a6b8399e0d9e93b446a591bb4cda0910 | SOURCE_PIN |
| EV-11 | AC-4（零新增命令基线） | verification/FEA-06-RESIDUAL-3/baseline/host-commands.txt | - | a701b982fe99499118d50fda8034e8a568e847f7e31e26c10a1413ba8b72e4cb | CANONICAL |
| EV-12 | limitations/口径 | verification/FEA-06-RESIDUAL-3/limitations.md | - | 5024c226ca74fe9c0916f1b1075af841e0a9fdefa1c84c834ceacee237b26f73 | CANONICAL |
| EV-13 | AC-6（证据总览） | verification/FEA-06-RESIDUAL-3/EV.md | - | 96a1ad9420680bd62861113c385c598394c88989704e19d92a5844141600ad81 | CANONICAL |
| EV-14 | AC-6（资源清单） | verification/FEA-06-RESIDUAL-3/RESOURCE-MANIFEST.json | - | 62aa7125d85cb9519bcc95406263925f0c717d1630e6870bda47719d010e2685 | CANONICAL |
| EV-15 | AC-6（视觉清单） | verification/FEA-06-RESIDUAL-3/visuals/inventory.md | - | 39011f26ba76e7749b35f79b17a10656083447e6a021a566d853514cbde7a502 | CANONICAL |
| EV-16 | AC-6（Lead 门禁日志） | verification/FEA-06-RESIDUAL-3/logs/gates-lead.log | - | 0d2dcd3cc50ba21cf246620df4f7a092dde9ea666a69d93d2afc1d50faa61e5f | CANONICAL |
| EV-17 | AC-6（Lead 门禁日志 r2） | verification/FEA-06-RESIDUAL-3/logs/gates-lead-r2.log | - | 0e775711cb442fe8f212f7c0b0290c0d70d23463ea070f7528762d770fd4639c | CANONICAL |
| EV-18 | AC-6（Lead 门禁日志 r3） | verification/FEA-06-RESIDUAL-3/logs/gates-lead-r3.log | - | c944ca31ffa0da540f4771653df8f3bd3a7bb456b2a7e94ab5fb9bbce1541725 | CANONICAL |
| EV-19 | AC-6（Lead 门禁日志 final） | verification/FEA-06-RESIDUAL-3/logs/gates-lead-final.log | - | dc242e807f2e9fc816de5b4126e096f856db81d99ce5e18179301bc755d84341 | CANONICAL |
| EV-20 | Review 链 r1 | doc/reviews/FEA-06-RESIDUAL-3-r1.md | - | 778ae993603fc3c021b65b45f9098ca863ab19b28e539be7144d7651ae6b1565 | CANONICAL |
| EV-21 | Review 链 r2 | doc/reviews/FEA-06-RESIDUAL-3-r2.md | - | f3af6e6b0027a545e413c233b940a06d62cf8454801a6f298d005d473d9c74b9 | CANONICAL |
| EV-22 | Review 链 r3 | doc/reviews/FEA-06-RESIDUAL-3-r3.md | - | fabc387649ab69f2c91e25fb5d20cdb438c533e45a682b0d628d6aec34189dff | CANONICAL |
| EV-23 | Review 链 r4（approved） | doc/reviews/FEA-06-RESIDUAL-3-r4.md | - | de7339106244c0a2875d9163dcb85c2f5d7e4387c2445e0df13664ec4d99bb59 | CANONICAL |
| EV-24 | 冻结面 | doc/reviews/FEA-06-RESIDUAL-3-scope-r1.md | - | c1c900c03f31984ae1ffedaf1e64cb7d7f8a5756e54a7aa2aaf500ff2ee9b1eb | CANONICAL |
| EV-25 | AC-6（像素不作 AC） | verification/FEA-06-RESIDUAL-3/visuals/01-shelf-default.png | - | 8016d8483547991fbad74c32d847c12a4aa556e36eda1fdc41ff69ca7e4d2e0e | CANONICAL |
| EV-26 | AC-6（像素不作 AC） | verification/FEA-06-RESIDUAL-3/visuals/02-shelf-readonly.png | - | fb8e4eb6d7fd91a858947c1b20fb2d13379c068be11963ec092cbb0db64a7ce3 | CANONICAL |
| EV-27 | AC-6（像素不作 AC） | verification/FEA-06-RESIDUAL-3/visuals/03-workbench-page.png | - | 7b91d5192b95b707afe7d8f534e55d3a58479919d6f07f62cc06be69af75f03f | CANONICAL |
| EV-28 | AC-6（像素不作 AC） | verification/FEA-06-RESIDUAL-3/visuals/04-workbench-batch-empty.png | - | 8316c81bedd4c0436821cf06d9a15b5ca81b9f849538ab67503a5b073f6bb01e | CANONICAL |
| EV-29 | AC-6（像素不作 AC） | verification/FEA-06-RESIDUAL-3/visuals/05-workbench-batch-matrix.png | - | 9fddecd24c9cf05f0a569b0754ab4d66c170d84bc5fb046c1a0f4668b65f54cc | CANONICAL |
| EV-30 | AC-6（像素不作 AC） | verification/FEA-06-RESIDUAL-3/visuals/06-console-nine-rows.png | - | ebc304e985597b838a098afe4afa47c2feba189b6382d65a1ca462c9a596e9ec | CANONICAL |
| EV-31 | AC-6（像素不作 AC） | verification/FEA-06-RESIDUAL-3/visuals/07-reader-single.png | - | b917ee56e85fc0be91bf938ab27bb821f8a954d650e035ecf12cfdb665886bb7 | CANONICAL |
| EV-32 | AC-6（像素不作 AC） | verification/FEA-06-RESIDUAL-3/visuals/08-reader-double.png | - | 2bf1c8a691f2a580d61b082167f8fd86b00aa2f54237cb232bda3e969f13991d | CANONICAL |
| EV-33 | AC-6（像素不作 AC） | verification/FEA-06-RESIDUAL-3/visuals/09-reader-webtoon.png | - | 3a2211a8b520c33f036132fb168a3e7ba723d9f7bd8aae81053a933f07b1a3ca | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | NOT_APPLICABLE（main；base `9429fc210`，impl `ddc29ecb3`） | NOT_APPLICABLE | — | — | 未创建 linked worktree |
| test-fixture | `tests/NewManga.App.Tests/**`（headless + in-memory fakes） | NOT_APPLICABLE | — | — | 无真实 IPC、无二进制 fixture |
| user-data | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 未触碰真实用户数据/AppData/外部卷 |
| tracked-side-effect | `verification/FEA-09/logs/wire-redacted.ndjson` | NOT_APPLICABLE | — | — | 既有副作用；每次全量后 `git checkout -- verification/FEA-09` |

## Closeout Record

- **Closeout date / DSH**：2026-11-08。
- **终态**：`done`；`integration_commit` = `delivery_head` = **`ddc29ecb3`**（实现 `a2b51c79d` + 三轮返修 `fc6712e94`/`5cabc1ebd`/`ddc29ecb3`）。
- **Review 链**：r1 CR（P1×2）→ r2 CR（P1×1）→ r3 CR（P1×1）→ **r4 approved（P0=0/P1=0/P2=0/P3=5）**；每轮 P1 均由变异实测判别并逐字节复原。
- **AC 定稿**：**AC-1…AC-6 全 MET**（AC-6 含 closeout 面）。
- **门禁**：build 0/0；全量 .NET **1731/0/98**；pytest **3390/10**；pins 18/18；check PASS；API EXIT 0；24 文件 ⊆ allowed_paths；禁止面零 diff；FEA-09 已恢复。
- **P3 登记**：R4-001…R4-005 → `FEA-06-RESIDUAL-5`（未建，随后续卡）；R3-R3-004 → L-R3-7；L-R3-1…L-R3-7 见 `limitations.md`。
- **行文**：不得写「FEA-06-RESIDUAL-2 全部关闭 / UI L1–L10 关闭 / 完全实现」；格 3 与原生项 `NOT_RUN`。
