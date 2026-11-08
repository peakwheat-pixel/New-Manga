# FEA-06-RESIDUAL-3 scope review r1（独立上下文只读子代理）

| 项 | 值 |
|---|---|
| 审查者 | 独立上下文 fresh subagent（session `8389e539-…`；未参与本卡起草；DSH 落盘） |
| 被审 head | `5cbec0e82`（main，clean） |
| 被审对象 | R2 草案（5 个 BLOCKED 依赖格 + Tab 遍历 + a11y；见 `RESIDUAL-CLOSEOUT-PLAN` §11 与 `ADJ-2026-11-RESIDUAL-WAIVER` W-06/W-07） |
| 结论 | **`NOT_RECOMMENDED`（按现文本）；按 §2/§5 的 5 项改写后 → `READY-TO-FREEZE`** |
| 落盘 | 正文由该子代理产出，DSH 落盘并按其建议冻结（见卡面与 `ADJ` §7.4） |

## 1. 5 个依赖格逐格核实（关键结论）

| 格 | 独立核实 | 判定 |
|---|---|---|
| **1. BatchMatrix 七状态/吸顶 + RunProjectionBar** | 端口存在：`RunContracts.cs:282-342`（`TaskProjectionInfo`）、`:385` `GetRunSnapshotAsync`、`:388` `GetTaskProjectionAsync`、`:375` `ControlRunAsync`；`Fluent WorkbenchViewModel` 已持 `IHostController`（`:11,31`）。**但契约无 list-runs 命令**（`RunStatusMonitor.cs:29-37`）→ Fluent 必须自己 `StartRunAsync` 并自持意图键（**行为新增**，非纯视觉） | **已解除（端口层）** |
| **2. ReaderPage 双页第二图/滚动** | 端口存在且**早于 FEA-09**（`ReaderLibrary.cs:9-48`、`IHostController.cs:161-168`、`:104-114`）；实际交付方是 `READER-LIBRARY-WIRE-1` AC4 / `READER-PROGRESS-1`；视图侧 `ReaderPageView.cs:67` 只有单 `_pageImage`，`:99/:173` 只翻布尔 | **已解除（纯 UI）** |
| **3. RegionBox 冲突态（「查看对照」）** | **不可解除**：`RegionSummary` 无冲突字段（`CoreServiceClient.cs:172-178`）；`list_page_region_texts` 未过 `IHostController`（`RegionTextProjection.cs:224-281` 仅测试用）；术语冲突面 NOT_WIRED（`StudioTermsViewModel.cs:36-62`）；**Current V2 也没有**。补数据需改 `IHostController.cs` → 撞 API inventory/C-07 pin → **违反 0 pin** | **未解除 → 降级 re-home** |
| **4. 书架满态统计** | **依赖误归**：FEA-12 四卡是删除/回收站线；冻结命令表无 statistics 命令（`HostCommandRegistry.cs:151-232`；Python 0 命中）。可用数据仅既有投影：`BookSummary.PageCount`（Core 真算）+ `Books.Count`；Fluent 已显示计数（`ShelfViewModel.cs:151`） | **改口径：不新增端口，自洽聚合** |
| **5. Console 投影/9 行** | 端口同格 1；"9 行"是**工作台 9 行状态表**（`FluentResidualBatchATests.cs:559` `I13_WorkbenchNineRowSkeleton`，`:578` 行 2、`:588` 行 9），仓库**无定义表** | **已解除（端口层）→ 卡面须落表** |

## 2. Fluent 侧缺口与最小 allowed_paths

- 必须改：`Views/Fluent/WorkbenchPageView.cs`（格 1/5 + 页签条 ←/→）、`ViewModels/Fluent/WorkbenchViewModel.cs`（StartRun + 意图键 + 1s 轮询 + counts/controls）、`Views/Fluent/ReaderPageView.cs` + `ViewModels/Fluent/ReaderViewModel.cs`、`Views/Fluent/ShelfPageView.cs` + `ViewModels/Fluent/ShelfViewModel.cs`、（建议）新增 `ViewModels/Fluent/FluentRunProjection.cs`、`tests/NewManga.App.Tests/**`、`verification/FEA-06-RESIDUAL-3/**`。
- **allowed_paths 必须收窄为 `Views/Fluent/**` + `ViewModels/Fluent/**`**（`Views/**` 会踩 `Views/V2/**`，与 RESIDUAL-2 的 "不改 Current V2/组合根" 禁令冲突）。
- **0 pin 硬边界**：`Services/IHostController.cs`、`Services/RunContracts.cs`、`Shell/V2/**`、`ViewModels/V2/**`、`Views/V2/**`、`Services/FrontendHostCoordinator.cs`、`FrontendSelector.cs`、`NewManga.DesignSystem/Generated/**`、`doc/design/**`。
- 不引用 V2 映射（`StudioRunControllerDataSource`/`IRunDataSource`）；Fluent 自建 ~20 行映射（可复用 `DesignSystem.Controls.StatusCatalog`）。

## 3. Tab 遍历 + a11y（含设计冲突裁决点）

- **硬事实**：`doc/design/fluent-v1/03-accessibility.md:13` 把无修饰 `Tab` 指派 `studio.mode.toggle`（仅 Studio）；`:42-46` 又规定四页 Tab 序。代码按前者（`ShellCommands.cs:63`、`FluentShellSurface.axaml.cs:157,304-327`）⇒ **工作台内 Tab 不通航**（设计级自相矛盾）。
- **DSH 裁决（采纳评审方案 a）**：A1 遍历只覆盖 Library / Reader / Settings；Studio 空间断言「`Tab` = 模式切换」+「页签条聚焦时 `←/→` 切页签」（后者当前未实现，本卡补，属 `Views/Fluent/**`）。**不**改全局 Tab 绑定（那会触 03 冻结 + FEA-07 输入路由）。
- 断言集（headless）：A1 覆盖性遍历（`TopLevel.KeyPress(Key.Tab)` + `FocusManager.GetFocusedElement()`，`S⊇F(P)`、无连续重复）；A2 隐藏不入序；A3 `peer.GetName()` 非空且非类型名；A4 `GetAutomationControlType()` 白名单；A5 UIA 树每可交互节点有名 + 浮层焦点往返。

## 4. 证据方案

- 默认**零仓库写入**（沿用 RESIDUAL-2 口径：跑前后 `git status --porcelain -- verification` 相等；`verification/FEA-06/**` 与 `verification/FEA-06-RESIDUAL-2/**` 恒空）。
- 显式开关 `NEWMANGA_CAPTURE_RESIDUAL3_PNGS=1`，只写 `verification/FEA-06-RESIDUAL-3/visuals/**`；**无既有 PNG 基线**（仓库无持久基线），故不破任何基线；**像素不作 AC 判据**（快照仅签署证据）。
- 逐图元数据沿用 `visual-inventory.md` 表头；约 9 张图。

## 5. 建议 AC（评审 6 条；DSH 采纳并编号 AC-1…AC-6）

- **AC-1**（格 1）：批量空态「开始处理」⇒ **恰好 1 次** `StartRunAsync`（`Command=translate_all` + chapter scope；`IdempotencyKey` 非空且重试复用同键）；`GetTaskProjectionAsync` 轮询 ≥2 次；注入 7 状态投影 ⇒ 矩阵逐格对应 `StatusKind` 文案；滚动后表头屏幕坐标不变（吸顶）；无投影时 `RunProjectionBar` 保持诚实空态。
- **AC-2**（格 5）：9 行表逐字段等于注入投影（RunId/RunStatus/OverallProgress/CurrentPageId/CurrentStepType/Completed/Failed/Skipped/Blocked）；`暂停/停止/继续/重试` `IsEnabled` 完全取自 `Controls`；禁用态点击 0 帧；`Counts` 缺失显示「—」。
- **AC-3**（格 2）：双页模式对 `Pages[i]` 与 `Pages[i+1]` 各 1 次 `LoadImageAsync` 且 pageId 不同；末页只 1 次；滚动模式连续页可滚动且 `SaveReadingProgressAsync` 收到 `scrollOffsetY>0`；单页不回归。
- **AC-4**（格 4，改写口径）：状态条 = `"{FilteredBooks.Count} / {Books.Count} 部作品"` + `Σ PageCount`（null→「—」且不计入）；筛选/空/只读三态；**源码断言零新增命令**（`HostCommandRegistry` 命令集合与卡前逐字相同）。
- **AC-5**（Tab + a11y）：按 §3 方案 a 的 A1–A5；补页签条 `←/→`；失败信息含控件路径。
- **AC-6**（证据/门禁/done 口径）：默认零写入；opt-in 9 图 + inventory（SHA256/签署）；全量 `.NET ≥1705/0/98`、pytest `≥3390/10`、pins 18/18、check PASS、API EXIT 0；`git diff --stat` 不含 `Views/V2|ViewModels/V2|Shell/V2|Services|DesignSystem/Generated`；`FEA-06-RESIDUAL-2` append-only 关闭记录 + **显式「done 不覆盖 BLOCKED 表」** + 未闭格（格 3）re-home 具名卡。

## 6. 风险（评审）

1. **三处既有断言必破**（必须改写不得删/弱化）：`FluentPageTests.cs:171-173`（`consoleContent.Children[1]` 索引断言）、`FluentResidualBatchATests.cs:117-127`（「端口尚未接入」文案）、`:559-594`（行 2/行 9 禁用占位）。
2. `Views/**` 误伤 V2 → allowed_paths 收窄 + AC-6 静态 diff 断言。
3. 意图键/幂等：空 key 会被本地拒绝（`RunContracts.cs:344-357`）→ Fluent 自持键、重试复用。
4. 轮询泄漏：`DispatcherTimer` 必须在 detach/切前端停止（RESIDUAL-1 曾因计时器泄漏返修），测试断言停止后不再发请求。
5. 术语不可判定：「七状态」「9 行」必须卡面落表（本卡已落）。
6. **done 门禁看不见 BLOCKED 表**（`check.ps1:814-851`）→ 关闭记录必须显式声明并逐格 before/after。
7. 基线：状态现为 `1705/0/98`（STATUS:20）> plan §11.4 的 1691/0/96 → 冻结重钉。
