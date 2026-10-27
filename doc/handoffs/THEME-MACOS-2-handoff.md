---
task_id: THEME-MACOS-2
author: macos-layout-owner
recipient: DeepSeek Harness
base_commit: d2f66a19e
delivery_head: null
status: draft
---

# Handoff：THEME-MACOS-2（三套不同界面布局的 macOS 风主题）

## 交付结果

在独立 worktree `G:/CODEX/New Manga.workspace/worktrees/THEME-MACOS-2`（branch `task/THEME-MACOS-2`，HEAD `84dd38978`，改动未提交、由 Lead 统一提交）内完成三套 macOS 风主题布局：

- **AC1 主题可见可切换**：`ThemePacks.All` 现为 9 套（6 旧 + 3 mac）；新增 `macos-launchpad`「macOS 启动台」与 `macos-split`「macOS 分栏」，连同既有 `macos-sonoma`「macOS 风」共三套 mac 主题，设置页主题列表各出现一次；`ThemePacks.Default` 仍为 `saber-purple`；旧 6 套 id/标签/顺序/token 均不变。
- **AC2/AC9 12 张真实截图**：`verification/THEME-MACOS-2/screenshots/` 下 12 张 1280×820 headless-Skia PNG（`{sonoma|launchpad|split}-{bookshelf|settings}-{light|dark}.png`），含尺寸/字节/AppBg 采样比/颜色多样性/16×10 结构指纹断言；三套布局 pairwise 结构差异 45–115/160 格（阈值 10），Light/Dark 逐对互异。sonoma 4 张 PNG 与 THEME-MACOS-1 canonical 截图**逐字节相同**（如 `sonoma-bookshelf-light.png` sha256 `0bd028ae…870e` = THEME-MACOS-1 `bookshelf-light.png`）→ 旧视觉零回归的最强证据。
- **AC3 热切换**：canonical 运行 `layout/hot-switch.json` 记录布局切换 36 样本 **p95=20.151ms / max=23.565ms / min=11.01ms**；同布局 Light/Dark 36 样本 **p95=14.155ms / max=14.695ms**，两者 ≤100ms。
- **AC4 对比度**：三套 mac pack 的 Light/Dark 全 token 组 WCAG 断言（正文 ≥4.5、次要 ≥3、导航选中 ≥4.5）全部通过，随 `theme/contrast.json`。
- **AC5 字体许可**：无随包字体；mac 三套沿用 THEME-MACOS-1 的系统字体栈 token（`Segoe UI Variable Text, Inter, Segoe UI, …`），`AppStyles.axaml` 用 `DynamicResource AppFontFamily`。
- **AC6 回归**：`scripts/test.ps1` **247/247 passed, 0 failed, 0 skipped**（coreclient 61 / host 56 / app 130；新增 ThemeLayoutsTests 6 + 既有 ThemeMacosTests 9 全绿，`dotnet build -warnaserror` 0 warning）；旧壳 `npx vitest run` **60 files / 567 tests** 全过；`python -m pytest -q` **2773 passed, 10 skipped, 0 failed**（本任务零 Python 改动）。
- **AC7 治理**：本卡改 `in_review`，Canonical Evidence 27 行 64-hex SHA-256 pin（`-` commit 列，工作区文件 pin），`verification/THEME-MACOS-2/MANIFEST.json` 覆盖 294 个证据文件并含 AC 映射；`check.ps1 -TaskPath doc/tasks/THEME-MACOS-2.md` PASS。
- **AC8 三套布局**：`LayoutKind/LayoutProfile/LayoutProfiles` 落在 Theme 模块，`ThemePack.Layout` 默认 Sonoma；`MainWindow` XAML 预置 `TitleBar/NavPanel`、底部 `DockHost/DockNavPanel`、左侧 `SidebarHost/SidebarNavPanel` 三态宿主，`ApplyLayout()` 移动同一批 nav 按钮（不重建）并驱动两页布局；Split 布局把交通灯/品牌块移入 Sidebar 顶部；`PageHost` 在 Dock 布局下预留 Dock 带（120px）。`BookshelfPage.ApplyLayout` 三结构（Sonoma 树/Launchpad 168×220 定高瓦片+1200 居中/260 列表+右侧网格），`SettingsPage.ApplyLayout` 三结构（双栏/900 单列/分区目录+右侧分区，Split 内切换只改可见性）。切换路径：`SettingsPage.SelectTheme` → `ThemePackService.Apply` → `MainWindow.OnThemeApplied` 检测 `Layout.Kind` 变化 → `ApplyLayout`；同 Layout 切 variant 只换 token。

### 变更路径（worktree 内）

- `apps/desktop-avalonia/src/NewManga.Theme/ThemePack.cs`：`LayoutKind/NavPlacement/ShelfStyle/SettingsStyle/LayoutProfile/LayoutProfiles`、`ThemePack.Layout`、`ThemePacks.MacOsLaunchpad/MacOsSplit`（共享 Sonoma 双 token + `SidebarBg/DockBg` 及 fallback）、`IsMacOsPack`。
- `apps/desktop-avalonia/src/NewManga.App/Views/MainWindow.axaml` + `MainWindow.axaml.cs`：三态宿主、`ApplyLayout/OnThemeApplied`、nav 视觉三态、品牌块迁移、`PageHost` Dock 预留、`DockHostControl/SidebarHostControl/DockNavPanelControl/SidebarNavPanelControl/BodyHostControl/CurrentLayout`。
- `apps/desktop-avalonia/src/NewManga.App/Views/Pages.cs`：BookshelfPage 三布局 `ApplyLayout` + `SplitBookList` + `StatusLine`；SettingsPage 三布局 `ApplyLayout` + `SplitSectionButtons/SelectedSplitSection` + `_themeButtons` 按 pack 去重。
- `apps/desktop-avalonia/tests/NewManga.App.Tests/ThemeLayoutsTests.cs`（新增 6 测试）；`ThemeMacosTests.cs` 的 pack 计数 7→9（语义不变）。
- `verification/THEME-MACOS-2/**`（layout/*.json、screenshots/*.png、test/**、MANIFEST.json）、本 Handoff、任务卡、Plan、Ledger。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1/AC8 | `dotnet test tests/NewManga.App.Tests --filter "ThemeLayouts|ThemeMacos"` | .NET 9 / Avalonia 11.3.22 headless+Skia，worktree HEAD `84dd38978` + 未提交改动 | PASS 15/15（ThemeLayouts 6 + ThemeMacos 9） | `verification/THEME-MACOS-2/layout/profiles.json`、`layout/switching.json` |
| AC2/AC9 | headless Skia `CaptureRenderedFrame()` 12 张 + 尺寸/AppBg/结构指纹断言 | 同上 | PASS 12×1280×820；AppBg 采样比 0.09–0.73；distinct colors 167–329；pairwise 45–115/160 | `verification/THEME-MACOS-2/screenshots/*.png`、`layout/screenshots.json` |
| AC3 | 布局切换 36 样本 + variant 36 样本（Apply + OnThemeApplied + RunJobs） | 同上 | PASS p95=20.151ms / 14.155ms（≤100ms） | `verification/THEME-MACOS-2/layout/hot-switch.json` |
| AC4 | WCAG 2.x 相对亮度公式，三套 × Light/Dark × 5 组 | 纯计算 | PASS（全部 ≥ 门槛） | `verification/THEME-MACOS-2/theme/contrast.json` |
| AC5 | 字体栈 token 检查 + 无字体二进制 | 同上 | PASS | `theme/pack.json` |
| AC6 | `pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1 -EvidenceDirectory <worktree>/verification/THEME-MACOS-2` | 全量 + sidecar fixture | PASS 247/247，0 skipped | `test/summary.json`、`test/dotnet-test-Debug.log`、`test/results-*.trx` |
| AC6 | `cd apps/desktop/frontend; npx vitest run` | 旧壳前端 | PASS 60 files / 567 tests | `test/vitest.log` |
| AC6 | `python -m pytest -q` | Python 全量 | PASS 2773 passed / 10 skipped / 0 failed（205.64s） | `test/pytest.log` |
| AC7 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/THEME-MACOS-2.md` | 治理门禁 | PASS（见任务卡实际记录） | 本卡 Canonical Evidence + `MANIFEST.json`（294 files, 15.45MB） |

未运行：真机 Mica/Windows 11 人工视觉 smoke 由 Lead/其他分支覆盖；headless 无 Mica，`NOT_RUN` 不写成通过。

## Record Decision

1. **布局属于主题（LayoutProfile 模型）**：`ThemePack` 仍是同一 record，新增可选 `Layout`（默认 `LayoutProfiles.Sonoma`）→ 旧 6 套零改动。`LayoutProfile` 携带 `Kind + Nav + Shelf + Settings + DockHeight/SidebarWidth/ShelfListWidth/SettingsNavWidth/LaunchpadCardWidth/LaunchpadCardHeight/ContentMaxWidth/SettingsMaxWidth`，并派生 `UsesDock/UsesSidebar/LaunchpadBottomInset`。三套 mac pack 共享 THEME-MACOS-1 的颜色/度量/动效/字体契约，只微调页面/侧栏/Dock 背景（WCAG 通过）。**不按 pack id 硬编码布局**，壳只读 `ThemePackService.Current.Layout`。
2. **壳层三态导航宿主**：XAML 预置 `NavPanel`（标题栏中央）/`DockHost+DockNavPanel`（底部悬浮圆角胶囊，`ColumnSpan=2`、Bottom 居中）/`SidebarHost+SidebarNavPanel`（左列 220，`BodyHost` 列 0 在非 Split 时为 0 宽）。`ApplyLayout()` 先 `(Parent as Panel).Children.Remove` 再入目标宿主（Avalonia 单父限制），四个按钮实例与 Click 不变，`Navigate/CurrentPage/F11/OnTitleBarPressed/BeginMoveDrag` 语义不变；Split 时把「交通灯 + Logo + 品牌」整块移入 Sidebar 顶部（`MoveBrandToSidebar/MoveBrandToTitleBar`），保证 mac 三布局都显示交通灯。
3. **书架页三结构复用同一 ViewModel**：三个布局根（`_sonomaRoot/_launchpadRoot/_splitRoot`）在构造期建好固定槽位，`ApplyLayout` 只把同一批共享控件（Header/SearchCard/ContentGrid/DetailPanel/StatusRow/ImportPanel）在槽位间迁移；`BookGrid.ItemTemplate` 按布局重设（Launchpad 168×220 定高瓦片、封面 150、圆角 16；Sonoma/Split 保持 170×226 原卡）。Sonoma 树保持 THEME-MACOS-1 原样（既有断言：`Header` 位于 root 第 0 行槽位、1400 视口 7 列、TagChips/Empty/NoResults 等成员不变）。Split 增加左侧 260px 书列表（封面小图 + 标题 + 标签，点击开详情、双击进阅读器），右侧搜索/网格/详情 overlay。
4. **设置页三结构**：Sonoma 保持 320px 主题卡 + 右侧卡片列；Launchpad 单列居中（MaxWidth 900，主题卡 + 凭证/Provider/网络/绑定/环境/数据/登记依序）；Split 左侧分区目录（主题/凭证/Provider/网络/绑定/登记，240px）+ 右侧只显示当前分区，**切换仅改可见性**、section 控件实例复用；三种布局都保留 `ThemeList/ThemeButtons/AppearanceRow/Light|DarkVariantButton/NsList/Credentials/ProviderProfiles/NetworkProfiles/Bindings/ThemeCard` 等公开成员与主题/外观切换行为。
5. **切换路径与性能**：`SettingsPage.SelectTheme` → `ThemePackService.Apply` → `MainWindow.OnThemeApplied()` 检测 `Layout.Kind` 变化 → `ApplyLayout()`（壳 + 两页 + `PageHost` Dock 预留）→ `ApplyTheme()`；同 Layout 的 `SwitchVariant` 只换 token 不重建布局（`LayoutAndVariantHotSwitch_P95Under100ms` 里对每次 variant 切换断言 `CurrentLayout` 不变）。布局重建只做 re-parent + 一次模板重设，canonical p95=20.151ms，无需预构建/可见性缓存方案。
6. **兼容与边界**：Dock/侧栏背景新增 `SidebarBg/DockBg` token，旧 pack 缺省时 `BuildVariant` 回退到 `NavBg/CardBg`（不出现 Magenta）；`PageHost` 在 Dock 布局下预留 `LaunchpadBottomInset=120`，避免 Dock 覆盖设置页/书架页内容（自测截图发现后修复）。`NavActiveText` 旧 pack 仍回退 `AccentText`。修复布局切换导致 `ItemsControl` 重建容器、`_themeButtons` 重复累积（实测 18→9）的 bug。无 Core/Host/协议/旧壳改动、无字体二进制、未 push。
7. **证据隔离**：全部新证据写 worktree `verification/THEME-MACOS-2/**`（MANIFEST 294 文件逐文件 sha256 + AC 映射），未触碰 `verification/THEME-MACOS-1/**`。

## 接收方式

- 仓库/worktree：`G:/CODEX/New Manga.workspace/worktrees/THEME-MACOS-2`，branch `task/THEME-MACOS-2`，HEAD `84dd38978`；实现/测试/证据/文档为工作区未提交改动，由 Lead 按卡 `allowed_paths` 显式 add 后提交，本任务不 push。
- 复跑：`pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1 -EvidenceDirectory <worktree 绝对路径>/verification/THEME-MACOS-2`（必须绝对路径）；`cd apps/desktop/frontend; npx vitest run`（该 worktree 首次需 `npm ci`）；`python -m pytest -q`；`pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/THEME-MACOS-2.md`。
- 前置：Windows 11 / .NET SDK 9；sidecar 副本 `G:/CODEX/New Manga.workspace/task-envs/HOST-CORECLIENT-1/sidecar-copy`；BOOK-FIXTURE/region fixture（test.ps1 自检）。
- 接收者检查：`test/summary.json` 247/247；`layout/hot-switch.json` 两个 p95；12 张 PNG 肉眼核对三布局（Dock 不遮挡内容、Launchpad 卡片 168×220、Split 侧栏+列表）；`git diff --stat` 只含本卡允许路径；`check.ps1 -TaskPath` PASS。

## 下一任务建议

- Task ID / 标题：无新增实现任务；由 Lead 对 THEME-MACOS-2 指派独立 Review（owner≠reviewer）并决定集成提交。
- 推荐 Agent / Reviewer：Reviewer=DSH（本卡已登记）；如需独立复核可选未参与实现的 ZCode/Antigravity/Codex。
- 推荐原因与前置依赖：AC1–AC9 全 MET，证据与 MANIFEST 齐全，只需复核 12 张截图/两个 p95/证据 pin。
- Recovery point：worktree `THEME-MACOS-2`，base `d2f66a19e`，当前 HEAD `84dd38978` + 未提交改动；未 push。
- 允许修改路径：无（Review 只读）。
- 禁止范围与新增授权条件：不改 Python Core/Host/协议/旧壳、不改旧 6 套 token/默认主题、不 push/gc/prune/reset/stash。
- 交付物：Review 结论 + Lead 集成提交。
- 验证命令、环境与完成 Gate：`test.ps1` 0 failed；`check.ps1 -TaskPath doc/tasks/THEME-MACOS-2.md` PASS。
- 可直接转发给 Agent 的指令：`只读复核 THEME-MACOS-2：核对 verification/THEME-MACOS-2/layout/{profiles,hot-switch,screenshots}.json、screenshots/ 12 张 PNG、test/summary.json；运行 check.ps1 -TaskPath doc/tasks/THEME-MACOS-2.md；不修改源码/证据、不 push。`

## 风险与遗留

- **工作区未提交**：实现/证据/文档均在 worktree 工作区，交付依赖 Lead 显式 add；`delivery_head` 待 Lead 提交后回填。
- **截图渲染口径**：代码构建页面在构造期解析 token，截图由「先 Apply pack(+variant) 再新建 MainWindow」的真实路径产出；同 Layout 原地换 variant 只重绘资源驱动面（THEME-MACOS-1 既有行为），未在本卡扩大为整页 DynamicResource 改造。
- **Launchpad 卡片布局**：定高 168×220 瓦片在 UniformGrid 中左对齐（与 Sonoma 网格一致），未做「整行居中」的 WrapPanel 排布；如需更贴近 macOS Launchpad 的居中式排布，另立任务。
- **可见性**：headless 无 Mica/真机阴影差异；真机 smoke 由 Lead/其他分支覆盖。
- **并发事故**：主树曾被并行 agent `git add -A` 吞掉中间态并回退，本 worktree 内已重新落盘、验证并取证；无 git 写操作残留（未 commit/push）。回退方法：删除三套 mac pack 的 LayoutProfile 与 Views 增量即可回到单 Sonoma 布局基线；本任务未删除文件。
