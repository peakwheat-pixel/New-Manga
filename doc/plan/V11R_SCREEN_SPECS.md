# V11R 新 UI/UX · Avalonia 屏幕实施规格 v1

状态：`FROZEN`（2026-10-30，DSH）。上游：`doc/design/redesign-v1/40-fusion/FUSION_SPEC.md`（结构权威）+ `DESIGN_SYSTEM.md` + `tokens.json`（视觉权威）+ `20-directions/*/index.html`（视觉原型）。
本文件只补 **Avalonia 落地映射**（用哪些真实 API/数据、文件归属、每屏验收），不重新定义视觉。

---

## 0. 通用规则

- 全部新界面在 `apps/desktop-avalonia/src/NewManga.App/{Views/V2,ViewModels/V2,Shell/V2}/`；旧 `Views/*.cs` 不改。
- 数据只经 `IHostController`（现有 36 方法 + 本程序新增 `CreateChapterAsync`/`IRunController`）与 `NewManga.DesignSystem`；禁止 ViewModel 直连 CoreClient/DB/文件系统。
- **Mock 必须显式**：未接入真实 API 的控件必须显示"能力待接入"标记，不得伪造数据成功。
- 状态七态统一用 `StatusGlyph` + `Nm.Color.Status.*`；禁止自造。
- 每屏必须实现 `idle/loading/ready/empty/error/partial`（DESIGN_SYSTEM §7）；错误就地 + 可重试。
- 上下文不丢失：切换空间/模式不重建 ViewModel，不重置滚动与选择。
- 键盘：见契约 §6.3；每屏必须支持全键盘可达、焦点可见、`Esc` 逐级退出。

## 1. Shell（`ui-shell`）

| 项 | 规格 |
|---|---|
| 文件 | `Shell/V2/AppShellV2.axaml(.cs)`、`Shell/V2/ShellState.cs`、`Shell/V2/KeyMap.cs`、`Shell/V2/CommandPalette*.cs`、`Views/V2/Shell/{TopBand,SpaceTabs,Breadcrumb,ScopeSelector,AttentionMenu,StatusBand,V2WorkspaceHost}.axaml` |
| 布局 | Row0 `TopBand` 36px（SpaceTabs · Breadcrumb · 模式切换 · ScopeSelector · AttentionMenu · 命令 · 主题）；Row1 空间内容（`*`）；Row2 `StatusBand` 24–28px（有 Run 时才显形） |
| 状态源 | `ShellState`：CurrentSpace、StudioMode、Selection(book/chapter/page/region/multiPage)、每空间 Scroll/Filter、表面栈（ThemeStudio/ReaderOverlay） |
| 命令面板 | `Ctrl+K`：命令列表带「空间 · 模式 · 作用域」标签 + 键位；模糊搜索；`↑↓` 选择 `Enter` 执行 `Esc` 关闭回焦 |
| 跳转 | `Ctrl+P`：作品/章节/页/Region 模糊跳转 + 深链接 `?space=&mode=&page=&region=`（供截图验证） |
| 验收 | 三空间切换保留 selection/滚动；`Tab` 切 Studio 模式保留；命令面板覆盖全部已实现动作；`F1` 速查；窗口 1600/1280/1024 三档不崩 |

## 2. Library 空间（`ui-shell`）

| 项 | 规格 |
|---|---|
| 文件 | `Views/V2/Library/**`、`ViewModels/V2/Library/**` |
| 数据 | `RefreshBooksAsync`、`ListChaptersAsync`、`ListChapterPagesAsync`、`CreateChapterAsync`(新)、`ImportFilesAsync`、`ImportFolderAsync`、`LoadReaderBookAsync`、`GetTranslatedPageIdsAsync`、`SaveReadingProgressAsync` |
| 布局 | 顶部：搜索（中文/拼音首字母）+ 排序 + 筛选 Chip；主体：`PageGrid` 封面网格（≥1600 四列，1280 三列）；右栏：驻留详情面板（作品元信息/章节账本/页数/进度/操作）；多选批量条（删除/导出/标记） |
| 导入 | `ImportDock`：文件/文件夹 → 目标章节 → 进度（每文件状态）→ 部分失败可重试/跳过；**无章节时提供"新建章节"就地入口**（关闭审计 F011 断点） |
| 回收站 | 独立筛选视图；恢复/永久删除需二次确认（数量 + 书名清单） |
| 阅读浮层 | `ShellSurface.ReaderOverlay`：分页 RTL/LTR、Webtoon 纵向；进度双模态（页码 + 百分比）；`Esc` 退出；不改主界面状态 |
| 验收 | 空库→新建书→新建章节→导入 2 页→重启可见（E2E-01 的 UI 段）；搜索/筛选正确；回收站真实；阅读浮层可退出且进度保存 |

## 3. Studio · Page 模式（`ui-studio`）

| 项 | 规格 |
|---|---|
| 文件 | `Views/V2/Studio/**`、`ViewModels/V2/Studio/**`、`Shell/V2/Studio/**` |
| 布局 | 左 `FilmStrip` 56↔200px；中 `CanvasViewport`+`PageSurface`+`RegionOverlay`（页面/成品/分屏三态，`SegmentedControl` 切换）；右 `Inspector` 40↔320px（文本/样式/修复/锁定/历史 5 页签）；底部 `TrackStrip` 四轨 + 流水线带 28↔240px |
| 画布 | 86% 默认缩放、滚轮缩放、拖拽平移、适应窗口；Region 百分比坐标覆盖；`HUDRing` 8 动作（`Tab` 循环 `Enter` 执行）；选中描边 accent、hover 半亮、锁定 ▮ 角标、失败 ✗ 角标 |
| 编辑 | 文本四级（ocr/machine/edited/final）可视化来源；人工译文写 Core（`V11R-F0-1` 命令）；锁定四把锁；Revision 列表预览/恢复；未保存更改离开前 Modal 三出口 |
| 数据 | `LoadPageRegionsAsync`、`ReadPageImageAsync`、`SetRegionTypeAsync`、`RestoreRegionRevisionAsync`、`RerenderPageAsync`、`ListRegionRevisionsAsync` + `V11R-F0-1` 写命令 |
| 降级 | `V11R-F0-1` 未合入前：编辑按钮显示 disabled + "能力待接入"，只读呈现可用（不得做假保存） |
| 验收 | 真实页图显示；Region 框与真实坐标吻合（百分比换算单测）；改类型/改文本/几何写后刷新 revision 增加且重启可复现；撤销/重做与 Revision 区分清楚 |

## 4. Studio · Batch 模式（`ui-studio`）

| 项 | 规格 |
|---|---|
| 布局 | 顶部 `StageRail`（阶段完成度 + 异常计数 + 门禁警示）；主区 `StatusMatrix`（行=页，列=10 阶段，单元格 18×18，框选/Shift 多选/双击下钻）；上方 `CountChips`（总/完成/失败/过期/待确认/阻塞，点击即筛选）；右侧 `Drawer` 360px 详情；底部 `RunStrip` 24px 控制（暂停/继续/停止/重试失败/恢复阻塞） |
| 数据 | `V11R-A-2` `IRunController`：Start/Control/Resume/Snapshot/TaskProjection/RetryFailed；轮询 500–1000ms（可注入），无 push 时以 snapshot 为准 |
| 批量动作 | 全部/选中/单页 × 翻译/重 OCR/重修复/重渲染；作用域后缀常驻（"翻译选中 3 页"） |
| 门禁 | 未确认/过期/失败未清零时的批量动作给出提示与影响面，不静默执行 |
| 降级 | 无活动 Run 时显示 `EmptyState` + 主操作"开始处理"；未接 Run 时（A-2 未合入）显示 NOT_WIRED 标记 |
| 验收 | 矩阵状态与 `GetTaskProjection` 投影一致（不得自造）；框选 3 页后切 Page 模式作用域仍为该 3 页；Run 控制四动作真实调用并反映状态；失败重试只重跑失败目标 |

## 5. Console 空间（`ui-shell`）

| 项 | 规格 |
|---|---|
| 文件 | `Views/V2/Console/**`、`ViewModels/V2/Console/**` |
| 分区 | ①任务与队列 ②Provider 与凭据 ③网络与代理 ④模型与设备（DirectML/CPU）⑤缓存与版本清理 ⑥备份与恢复（.nmbak）⑦插件与 Hooks ⑧诊断与日志 ⑨外观（入口到 ThemeStudio） |
| 数据 | `ListProviderProfilesAsync`/`SaveProviderProfileAsync`/`DeleteProviderProfileAsync`、`ListNetworkProfilesAsync`/`Save`/`Delete`/`SetNetworkDefaultAsync`/`TestNetworkProfileAsync`/`ResolveNetworkProfileAsync`、`SetProviderBindingAsync`/`ClearProviderBindingAsync`/`ResolveProviderBindingAsync`、`ListCredentialTargetsAsync`/`PutCredentialAsync`/`ClearCredentialAsync`、导出历史/揭示目录 |
| 安全 | 凭据只显示"已保存/未保存"，永不回显 secret；错误文本不含路径/secret；危险动作（清缓存/删备份/永久删除）二次确认 |
| 降级 | 未接入 API 的区块显示 `AlertBanner` "能力待接入"，不做假开关 |
| 验收 | 至少 Provider/网络/凭据/设备/备份 5 区可用真实 IPC；危险确认可取消；密钥无泄漏 |

## 6. Theme Studio（`ui-shell` 或专派）

| 项 | 规格 |
|---|---|
| 文件 | `Views/V2/ThemeStudio/**`、`ViewModels/V2/ThemeStudio/**`、`Shell/V2/ThemeStudio/**` |
| 布局 | 全窗表面（覆盖空间内容，保留 TopBand 返回）；左栏 7 分区；主区随分区变化；右栏预览摘要（当前主题/外观/密度/布局 + 应用/取消/恢复默认） |
| 分区 | ①**主题库**：卡片网格（名称/作者/明暗支持/标签），搜索、分类、筛选（明/暗/高对比）；②**预览**：书架/工作台/阅读器三张真实控件渲染（非图片），明暗 + 高对比 + 密度切换；③**我的主题**：已安装/收藏/自定义，导入、卸载、导出；④**编辑器**：配色（语义色组编辑 + 对比度实时校验）、字体（族/字号缩放）、圆角、背景/材质、阴影（V1 仅 none/raised）、动效；⑤**外观**：浅色/深色/系统跟随/高对比/减少动效/跟随系统强调色；⑥**导入导出**：拖入 `.nmtheme`/JSON、格式校验结果（错误逐条）、导出当前主题；⑦**恢复默认**：确认后重置 |
| 行为 | 所有更改先走 `IThemePreviewEngine` 会话（实时预览，右栏"应用"提交）；取消完整回滚；预览期间不重建主界面、不改画布像素、不丢未保存编辑；主题包非法时显示 issue 并回退默认不崩溃 |
| 数据 | `IThemeService`/`IThemeRegistry`/`IThemePreviewEngine`/`IThemeValidator`（契约 §4） |
| 验收 | 7 分区齐全；切换主题即时反映到书架/工作台/阅读器预览；应用后全局生效且重启保持；取消后完全恢复；导入非法包有逐条错误且不崩溃；旧主题 ID 迁移到默认；高对比与减少动效生效 |

## 7. 交付顺序与依赖

```
V11R-D-1 (M0 骨架) ──▶ V11R-B-1 Shell+Library ──▶ V11R-B-2 Console ──▶ V11R-C-2 Theme Studio
                    ├──▶ V11R-B-3 Studio Page（需 A-2 + F0-1）
                    └──▶ V11R-B-4 Studio Batch（需 A-2）
```
每屏完成即 L1 验证（构建 + 单测 + 截图），整屏组完成后 L2，M2/M3 里程碑 L3 独立审查。

## 8. 文件归属（避免并行冲突）

| 目录 | Owner |
|---|---|
| `Views/V2/Shell/**`、`Views/V2/Library/**`、`Views/V2/Console/**`、`Views/V2/ThemeStudio/**`、`ViewModels/V2/{Shell,Library,Console,ThemeStudio}/**`、`Shell/V2/{AppShellV2,ShellState,KeyMap,CommandPalette}.cs` | `ui-shell` |
| `Views/V2/Studio/**`、`ViewModels/V2/Studio/**`、`Shell/V2/Studio/**` | `ui-studio` |
| 公共控件（≥2 屏使用） | 先本地后上收 `NewManga.DesignSystem.Controls`（由 `design-platform` 上收，见契约 §3.2） |
| `MainWindow.axaml` 切换承载 `AppShellV2` | 仅 `V11R-INT-1`（DSH） |
