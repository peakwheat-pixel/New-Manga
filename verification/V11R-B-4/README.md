# V11R-B-4 · Studio · Batch 模式 — 实施与证据

- Owner：`ui-studio`；Branch：`v11r/ui-studio`；Worktree：`G:\CODEX\New Manga.workspace\worktrees\V11R-UI-STUDIO`
- 依赖：已 `git merge main`（含 V11R-A-2 `IRunController` `c452c28c8` 合并点）；本卡 Base = B-3 delivery head
- 任务卡：`doc/tasks/V11R-B-4.md`；规格：`V11R_SCREEN_SPECS.md §4`、`FUSION_SPEC §2.3/§3`、`DESIGN_SYSTEM.md §2.2/§6.3/§7`

## 1. 质量门（命令 + exit code）

| 动作 | 命令（`apps/desktop-avalonia`） | exit | 结果 |
|---|---|---|---|
| 构建 | `dotnet build NewManga.sln -warnaserror` | 0 | 0 warning / 0 error（`build.log`） |
| 测试 | `dotnet test NewManga.sln` | 0 | App **185 通过 / 5 跳过**（跳过均为 A-1/A-2 需要真实 sidecar 的既有无头集成测试）；DS 40；Host 39/21；CoreClient 39/22（`test.log`） |
| Studio 子集 | `dotnet test --filter V2Studio` | 0 | **29/29**（B-3 21 + B-4 8） |

## 2. 交付内容（AC1 布局）

| 区域 | 实现 | 文件 |
|---|---|---|
| Batch VM | `StudioBatchViewModel`：投影数据/动态阶段列/筛选/选择/动作/门禁/轮询/下钻 | `ViewModels/V2/Studio/StudioBatchViewModel.cs` |
| 真实数据适配 | `RunControllerRunDataSource`：`IRunController.GetTaskProjectionAsync` → Studio 投影；`step_flow` 动态列；`tasks[].steps` 提供逐页逐阶段状态；`controls` 原样透传 | `ViewModels/V2/Studio/StudioRunControllerDataSource.cs` |
| 阶段轨道 | 每阶段完成度/异常计数/门禁态；门禁警示（失败/阻塞未清零） | `Views/V2/Studio/Controls/StudioBatchControls.cs` |
| 状态矩阵 | 行=页、列=**投影 step_flow（动态，非硬编码 10）**、单元格 18×18；单选/Shift/框选/双击下钻；常驻图例 | 同上 |
| CountChips | 总/完成/失败/过期/待确认/阻塞；可用口径点击筛选（仅降透明，不重排）；缺失口径显示 `—` 并就地说明 | 同上 |
| Drawer | 360px 右侧详情：页事实 + 逐 step 状态/错误码 | 同上 |
| 批量动作条 | 全部/选中/当前页 × 翻译/重 OCR/重修复/重渲染；**作用域后缀常驻**；门禁未清 → 影响面确认 Modal，不静默执行 | 同上 |
| RunStrip 24px | Run 摘要 + 暂停/继续/停止/重试失败/恢复阻塞（可用性来自 Core `controls`） | 同上 |
| 轮询 | 可注入间隔（默认 750ms，500–1000 范围），仅 Batch 可见时轮询；无 push 时以 snapshot 为准 | 同上 |
| 双向下钻 | 矩阵 Enter/双击 → Page 定位该页该阶段；Page 流水线步骤点击 → 回 Batch 高亮列+页行；筛选/滚动/选择保留 | `Shell/V2/Studio/StudioWorkspaceView.axaml.cs` |
| Page 流水线带 | 改为**投影驱动动态阶段**（无投影时 10 个标准阶段显示「无投影数据」）；步骤点可点击下钻 | `StudioPageViewModel.cs` / `StudioBottomBands.cs` |
| 空态 | 无 Run → EmptyState +「开始处理」（走真实 `StartRunAsync`）；Host 无 Run 控制器时 NOT_WIRED 保留 | `StudioBatchControls.cs` |

## 3. AC 覆盖

| AC | 证据 |
|---|---|
| AC1 布局/组件/数据源；无 Mock | `matrix.json`（10 列投影 → 10 列；5 列投影 → 5 列，**非硬编码**）、`artifacts/batch-matrix-24x10-legend.png`、`artifacts/batch-mode-1600x1000.png`、`artifacts/batch-mode-1280x800.png`；全部状态来自 `FakeHostController.ScriptedTaskProjections`（即 `GetTaskProjection` 读面） |
| AC2 上下文保留/双向下钻 | `drilldown.json`：Batch→Page 定位 `(page, stage)`、Page→Batch 高亮 `render` 列 + 当前页行；filter/scroll 保持；选择经 `StudioSelection` 共享（Page 模式同作用域） |
| AC3 状态完备 | `empty-state.json`（无 Run 空态 + 开始处理真实 StartRun）；投影失败 → `Error`/`Partial` 状态保留上次投影；轮询合并见 `run-controls.json` |
| AC4 token/无裸值 | `build.log` 0 warning；`design-system-usage.md`（40 个 Nm token / 62 个 Studio 类；DS 标准控件样式未重定义） |
| AC5 键盘/焦点 | 矩阵单元格可聚焦、`Enter` 下钻、Shift+点击/拖拽框选；计数胶囊/动作按钮均为真实 Button（焦点环由 DS Button 主题提供） |
| AC6 单测 + 截图 | `V2StudioBatchTests` 8 个用例；截图 6 张（矩阵+图例、胶囊+选择、抽屉+门禁、空态、1600/1280） |
| AC7 证据 | 本目录 `build.log`、`test.log`、8 份 JSON、`artifacts/*.png`、`design-system-usage.md` |

### 截图清单（`artifacts/`）

- `batch-matrix-24x10-legend.png`（24 行 × 10 投影阶段 + 常驻图例）
- `batch-chips-selection.png`（CountChips + 作用域 chip + 选择态）
- `batch-drawer-gate.png`（Drawer 详情 + 门禁确认路径）
- `batch-empty-empty-state.png`（无 Run 空态 + 开始处理）
- `batch-mode-1600x1000.png` / `batch-mode-1280x800.png`（两档窗口真实渲染）

## 4. NOT_WIRED / NOT_RUN / 偏差

1. **NOT_WIRED 保留位**：`IRunDataSource` 的 `NotWiredRunDataSource` 仍存在，仅用于「Host 无 IRunController」的降级路径（`StudioBatchViewModel` 自行解析 `host as IRunController`）；当前真实 `HostController` 与 `NullHostController` 均实现 A-2 接口，因此正常路径一律走真实投影。`empty-state.json` 记录了该 seam 不可伪造成立的断言。
2. **过期 / 待确认口径**：`GetTaskProjection` 不提供 stale / review 计数（review 状态在 Region revision 面，属 F0-2+）。两个 CountChip 显示 `—` 且点击只给说明、不伪造筛选；**未被静默**。
3. **矩阵单元格缺失阶段**：投影 `step_flow` 不含的列不会出现；`tasks[].steps` 不含的阶段显示「无投影数据」（`–`），不猜测状态。
4. **框选实现**：指针按下 + 拖动进入单元格即按矩形选区（Shift 点击等价），无橡皮筋绘制（V1 接受；命中区域由单元格本身承担）。
5. **`RunControlAction.Restart` / `Abandon`**：按钮位仅按 Core `controls` 呈现（本卡未放重启/放弃按钮，避免与门禁/确认流程混淆；命令层已由 A-2 暴露，后续按 UX 裁决再加）。
6. **queued 符号**：按 Lead 裁决改为冻结 `DESIGN_SYSTEM.md §2.2` 的 `·`（B-3 的 `◦` 已回退，`V2StudioMathTests` 断言同步）。
7. **DS `StatusGlyph` 上收**：仍用本地 `StudioStates`（符号/色/标签三通道），上收后替换来源即可；矩阵/流水线带/图例/抽屉共用同一映射。
8. **测试写域**：新增 `tests/NewManga.App.Tests/V2StudioBatchTests.cs`（只增文件，未改 csproj/既有测试），已由 Lead 追认 B-3 同类口径，B-4 同例。
9. 未触碰：旧 Views、`Services/**`（A-2 文件归 core-bridge）、`CoreClient/**`、DS/ThemeEngine 内部、ui-shell 的 `Shell/V2/{AppShellV2,ShellState,KeyMap}.cs`、`MainWindow.axaml`；未 push。

## 5. 复现

```powershell
cd apps/desktop-avalonia
dotnet build NewManga.sln -warnaserror
dotnet test NewManga.sln
# 或仅 Studio：dotnet test tests/NewManga.App.Tests/NewManga.App.Tests.csproj --filter V2Studio
```

截图由 `Avalonia.Headless`（`UseHeadlessDrawing=false` + Skia）在 `[AvaloniaFact]` 内 `CaptureRenderedFrame()` 生成真实像素；投影由 `FakeHostController.ScriptedTaskProjections` 脚本化，语义与 Core `GetTaskProjection` 一致。

## I2/I3 后状态（最新）
- P1-A（增量矩阵/滚动保持）与 P1-B（作用域物化/不回落整章）均有自动化测试
- R-22 意图幂等键可观测 + Stop 二次确认 + SubmitInFlight 守卫均有测试
- gate.json impact_text 读真实 GateImpactText；drilldown scroll_kept 使用非 0 偏移；恒真断言已删
- 轮询由 Activate/Deactivate 驱动，Page 模式零读取为硬断言
