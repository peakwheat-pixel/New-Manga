# V11R-B-3 · Studio · Page 模式 — 实施与证据

- Owner：`ui-studio`；Branch：`v11r/ui-studio`；Worktree：`G:\CODEX\New Manga.workspace\worktrees\V11R-UI-STUDIO`
- Base：`ba59a6c0d`（已 `git merge main` → `86bfec9b5`，含 V11R-D-1 M0 `819eea0d3`）
- Implementation commit：`4317624b1`
- 任务卡：`doc/tasks/V11R-B-3.md`；规格：`doc/plan/V11R_SCREEN_SPECS.md §0/§3`、`doc/plan/V11R_AVALONIA_CONTRACT.md`、`FUSION_SPEC §2.2/§2.3/§3`、`DESIGN_SYSTEM.md`

## 1. 质量门（命令 + exit code）

在 `apps/desktop-avalonia` 下执行：

| 动作 | 命令 | exit | 结果 |
|---|---|---|---|
| 构建 | `dotnet build NewManga.sln -warnaserror` | 0 | 0 warning / 0 error（`build.log`） |
| 测试 | `dotnet test NewManga.sln` | 0 | App 166 通过 / 2 跳过（既有跳过）；DS 24；Host 39/21 跳过；CoreClient 39/22 跳过（`test.log`） |
| Studio 子集 | `dotnet test --filter FullyQualifiedName~V2Studio` | 0 | 21/21 通过 |

跳过项均为此前已存在的环境型跳过（非本任务引入；见 `test.log` 中 SKIP 行）。

## 2. 交付内容（AC1 布局 / 结构）

| 区域 | 实现 | 文件 |
|---|---|---|
| Studio 承载 | `StudioWorkspaceView : UserControl`（模式条 + breadcrumb + 作用域 chip + Page/Batch 容器 + 键盘路由 + `LoadAndRenderAsync/Activate/Deactivate` 适配面） | `Shell/V2/Studio/StudioWorkspaceView.axaml(.cs)` |
| Page 组合 | `StudioPageWorkspace`：FilmStrip 56⇄200 ｜ CanvasViewport ｜ Inspector 40⇄320；底部 TrackStrip 四轨 28 + 流水线带 28⇄240；未保存 Modal 覆盖层 | `Views/V2/Studio/Controls/StudioPageWorkspace.cs` |
| 胶片条 | 真实页图缩略（Host 资源通道，≤60 页顺序加载）、序号、状态点、当前页 accent 左条、展开显示文件名/状态 | `StudioFilmStrip.cs` |
| 画布 | 86% 默认、滚轮锚点缩放、拖拽平移、适应窗口、页面/成品/分屏三态；成品/分屏为 NOT_WIRED 占位 | `StudioCanvasViewport.cs` |
| Region 覆盖 | 百分比坐标 × 页面像素 × 缩放；选中 accent（2px）/hover 半亮/锁定 ▮/失败 ✗；0 几何不绘制 | `StudioRegionOverlay.cs` |
| HUD 环 | 8 动作位 N..NW、`Tab`/`Shift+Tab` 循环（跳过禁用项）、`Enter` 执行、禁用 40% + tooltip | `StudioHudRingControl.cs` |
| 检查器 | 40px 图标条 ⇄ 320px；文本/样式/修复/锁定/历史 5 页签一次构建保活 | `StudioInspectorPanel.cs` |
| 底部 | 四轨（原图真实完成态；文本/修复/排版 = 状态待接入）、10 阶段点阵 + NOT_WIRED 头 + 展开列表 | `StudioBottomBands.cs` |
| 未保存 Modal | 保存/放弃/取消三出口；`Esc`=取消；保存写入走已接入 `set_region_type`；保存失败留在 Modal 并就地报错 | `StudioLeaveModal.cs` |
| 键盘 | `Tab`（有 Region 时 HUD / 无 Region 时模式切换）、`Enter`、`J/K`、`[ ]`、`+/-`、`0`、`Esc` 逐级；文本框聚焦让位 | `StudioKeyboard.cs` |
| 纯逻辑 | 坐标/缩放/平移、七态词汇、10 阶段、HUD 环、能力门、共享选择模型 | `ViewModels/V2/Studio/*.cs` |

设计系统：**不重定义** DS 标准控件/文本/表面样式；仅保留 Studio 专属几何/状态类（`StudioTheme.axaml`）。本任务使用的 `Nm.*` 键与 Classes 清单见 `design-system-usage.md`（40 个 token、10 个 DS Classes、51 个 Studio 本地类）。

## 3. AC 覆盖

| AC | 证据 |
|---|---|
| AC1 布局/组件/数据源；无 Mock 冒充 | `page-load.json`、`artifacts/page-mode-1600x1000.png`、`not-wired.json`；读链断言：`ListChapterPagesAsync → LoadPageRegionsAsync → ReadPageImageAsync → LoadRegionRevisionsAsync` |
| AC2 上下文保留 | `context-retention.json`：Page⇄Batch 切换后同一 VM/同一 PageWorkspace 实例，zoom/offset/region/tab/多选页全部保留 |
| AC3 六态 | `states.json` + `artifacts/state-{empty,error,partial}.png`；loading 骨架由 `PageImageNote`/骨架保留、无整页 spinner |
| AC4 无裸值/全 token | `build.log` 0 warning；`design-system-usage.md`；Studio 样式表全部 `{DynamicResource Nm.*}`；无阴影/渐变/模糊；圆角 ≤3px |
| AC5 键盘/焦点/IME | `hud-keyboard.json`（Tab 循环 HUD、无 Region 时 Tab 切模式、Enter 执行、Esc 逐级）；`leave-modal.json`（Esc=取消） |
| AC6 单测 + 截图 | 21 个 Studio 测试（10 纯逻辑 + 11 headless UI）；截图 14 张（见下） |
| AC7 证据 | 本目录：`build.log`、`test.log`、`*.json`、`artifacts/*.png`、`design-system-usage.md` |

### 截图清单（`artifacts/`）

- `page-mode-1600x1000.png`（Page 模式基准 1600×1000，86%）
- `page-mode-1280x800.png`（1280×800：胶片条 56、检查器默认收起 40）
- `page-mode-1024x700-inspector-overlay.png`（<1280：检查器覆盖式抽屉，画布不挤压）
- `inspector-text|style|repair|locks|history.png`（5 页签各一张）
- `region-badges.png`（选中/hover/锁定 ▮/失败 ✗ 四态同框）
- `state-empty|error|partial.png`（空/错误/部分）
- `leave-modal.png`、`wired-writes.png`
- `theme-canvas-before.png` / `theme-canvas-after.png`（Dark→Light 主题切换前后，页面图像素裁剪；`theme-diff.txt` = `diffPixels=0`）

## 4. NOT_WIRED 清单（本构建显式降级，绝不假成功）

来自 `not-wired.json`（由 `StudioPageViewModel.BuildNotWiredInventory()` 生成）：

- **写命令（V11R-F0-1 未合入）**：`CreateRegion`、`DeleteRegion`、`MoveRegion`、`ResizeRegion`、`MergeRegions`、`SplitRegion`、`ReorderRegions`、`SaveEditedTranslation`、`SaveFinalTranslation`、`ConfirmFinal`、`LockPage/Region/Translation/Inpaint`、`PinRevision` → 控件可见、`IsEnabled=false`、tooltip=`能力待接入（V11R-F0-1 写面未合入）`。
- **读面缺失**：`IRegionTextSource`（四级文本各 tier 只显示结构与来源 + `能力待接入`，无假文本）、`IRegionFlagSource`（四把锁/失败角标无产品数据源；控件状态由测试夹具驱动并在 `region-badges.json` 注明）、成品/分屏页资源读取（`PageSurface.Final/Split` 占位）。
- **Run/投影（V11R-A-2 未合入）**：`IRunDataSource` = `NotWiredRunDataSource`；流水线带显示 `流水线投影未接入 · NOT_WIRED`，10 个阶段点全为「无投影数据」，不显示任何伪造进度。
- **Batch 模式**：本任务交付占位空态（`NOT_WIRED` + 禁用「开始处理」）；矩阵/阶段轨道/CountChips/Drawer/RunStrip 属 **V11R-B-4**。

## 5. NOT_RUN / 已知偏差

1. **Batch 模式全量**：`V11R-B-4` 范围，本卡不交付。
2. **DS `StatusGlyph` 上收**：M0 未提供该自定义控件，Studio 本地 `StudioStates` 实现符号/色/标签三通道；符号与契约 §2.3 一致（`◦ ◐ ● ✗ ▲ ▨ – ○ ▮`）。上收后只需替换符号来源。
   - 偏差记录：`DESIGN_SYSTEM.md §2.2` 表格把 queued 写作 `·`，`AVALONIA_CONTRACT.md §2.3` 与 Lead 口径为 `◦`；本实现采用 **契约 §2.3 / `◦`**，`·` 仅保留为无数据占位的 `–` 语义之外不使用。
3. **ShellState / `IWorkspaceView` 接线**：由 `ui-shell` 与 `V11R-INT-1` 负责；本任务提供 `StudioSelection` 作为 Studio 侧唯一选择源 + `Activate/Deactivate/LoadAndRenderAsync` 适配面，未修改 `Shell/V2/{AppShellV2,ShellState,KeyMap}.cs` 与 `MainWindow.axaml`。
4. **十阶段列**：Core `GetTaskProjection.step_flow` 只携带 9 个 Core step（detect…render）；`save` 为产品级列（`CoreStepType=null`，投影中不存在时渲染「无投影数据」而非伪造状态）。B-4 矩阵按投影动态列实现。
5. **缩略图成本**：胶片条用 Host 资源通道逐页读取（≤60 页上限、顺序）；真实产品应改由 Host 提供缩略图命令（未在冻结面内），已在代码注释与风险中记录。
6. **Region 历史「预览」**：冻结读面只有元数据（类型/sfx/review/origin/时间），无内容快照；UI 只呈现元数据并在文案中声明「内容快照读取未接入」，不伪造预览内容。
7. **主题切换画布不变**：`theme-canvas-hash.json` + `theme-diff.txt`（`diffPixels=0`）证明 Dark→Light 后页面图像素完全一致；完整 C2 主题切换验收仍归 Theme Studio 任务。
8. **可见性**：本任务未新增/修改 `Services/**`、`CoreClient/**`、`NewManga.DesignSystem/**`、`NewManga.ThemeEngine/**`、其它 V2 目录、旧 `Views/**`；未 push。

## 6. 测试清单（21）

纯逻辑（`V2StudioMathTests`，10）：百分比↔像素往返/越界钳制、渲染缩放、轮盘锚点不变式、适应窗口与偏移钳制、七态符号/标签/令牌键/review+projection 映射、10 阶段 core-step 映射、HUD 8 位序 + 跳过禁用循环、能力门三接线 + tooltip、共享选择作用域。

Headless UI（`V2StudioPageTests`，11）：真实读链 + 1600 截图、1280/1024 响应式、5 页签切换不重建 + 逐页截图、降级零写调用、已接线写（类型/恢复/重渲染）、未保存 Modal 三出口、HUD 键盘、上下文保留、空/错/部分三态、四角标同框、主题切换画布像素哈希。

## 7. 复现

```powershell
# 证据会写入本目录（默认解析到仓库 verification/V11R-B-3）；
# 也可用环境变量重定向：$env:NEWMANGA_STUDIO_EVIDENCE_DIR="<dir>"
cd apps/desktop-avalonia
dotnet build NewManga.sln -warnaserror
dotnet test NewManga.sln
```

截图由 `Avalonia.Headless`（`UseHeadlessDrawing=false` + Skia）在 `[AvaloniaFact]` 内 `Window.CaptureRenderedFrame()` 生成真实像素，非占位图。
