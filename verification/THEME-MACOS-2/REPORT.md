# THEME-MACOS-2 验证报告（macOS 风主题重做，独立分支）

- Task：`doc/tasks/THEME-MACOS-2.md`（team task-54）
- Branch / worktree：`task/THEME-MACOS-2-saber` / `G:/CODEX/New Manga.workspace/worktrees/THEME-MACOS-2-saber`
- Base：**`f1b89c5e5`**（Lead 裁决：接受以 main 修复态为 base；任务卡原记 `d2f66a19e`/指令 `84dd38978`）
- **未新建重复的 `macos-sonoma` 或新主题 id**：主线 `ThemePack.cs`（`4ea86e03a` 版本，含 7 packs + `macos-sonoma`）经核验已基本达标，本任务定位为「验证 + 补齐 + 出证据」，并把被 Lead 移出的主题测试恢复为自洽证据。
- 未 push / gc / prune；不伪造结果；未写真实 `%APPDATA%`；**未触碰 Lead 指定但被外部会话占用的冲突 worktree**。

## 0. 冲突处置（先说明）

Lead 指定的 `worktrees/THEME-MACOS-2` 在开始后被另一进程并发写入（未跟踪的 `ThemeLayoutsTests.cs`/`verification/THEME-MACOS-2/`、`ThemePack.cs` 被改回 9-pack layouts 版、`Pages.cs`/`MainWindow.axaml.cs`/`ThemeMacosTests.cs` 被替换）。我未在该目录 reset/删除/提交；已向 Lead 报告，获准以 **`f1b89c5e5`** 为 base 在独立 worktree `THEME-MACOS-2-saber`（branch `task/THEME-MACOS-2-saber`）继续。冲突目录留给 Lead 处置。

## 1. 结论

| AC | 结论 | 证据 |
|---|---|---|
| AC1 主题可见可切换 | **MET** | 设置页主题中心列出 7 个 pack（含「macOS 风」`macos-sonoma`，单行、中文名）；`ThemePacks.Default` 仍为 `saber-purple`；6 个既有 pack 的 AppBg/Accent/TextPrimary/单 token 集/字体栈不变；macOS 交通灯仅视觉（不改窗口行为）。证据：`headless/theme/pack.json`、`headless/theme/traffic-lights-visual-only.json`。 |
| AC2 Light/Dark 渲染 | **MET** | 同一 pack 内嵌 Light/Dark 两套 token+material（AppBg #F5F5F7/#1E1E1E、CardBg #FFFFFF/#2C2C2E、HeaderBg、Accent #007AFF/#0A84FF、MicaFallback 等）；**4 张真机截图**（书架/设置 × Light/Dark，像素采样与 token 一致）；另附 4 张 headless-Skia 渲染证据。证据：`real-app-*.png`、`real-app-screenshots-metadata.json`、`headless/screenshots/`。 |
| AC3 热切换 | **MET** | 48 次真实切换（macOS Light↔Dark + saber-purple/midnight/sakura 混合），**p95 = 10.456 ms**，max 15.830 ms，min 4.358 ms（阈值 100ms）。证据：`headless/theme/hot-switch-macos.json`。 |
| AC4 对比度 | **MET** | WCAG 2.x 相对亮度公式计算：正文 Light 15.457/16.830、Dark 15.311/12.800（≥4.5）；次要 Light 4.658/5.071、Dark 5.806/4.853（≥3.0）；NavActiveText Light 8.521 / Dark 9.290（≥4.5）。证据：`headless/theme/contrast.json`。 |
| AC5 字体许可 | **MET** | 仓库/App 内 **0 个字体二进制**（扫描 `apps/desktop-avalonia` 排除 bin/obj：ttf/otf/ttc/woff/woff2 均无）；macOS 栈仅系统族（Segoe UI Variable Text / Segoe UI / Microsoft YaHei UI / PingFang SC / Noto Sans CJK SC）+ Inter（SIL OFL 1.1，未随包）+ sans-serif 回退。证据：`headless/theme/font-audit.json`。 |
| AC6 回归 | **MET** | 干净 worktree `test.ps1` **243/243 passed, 0 skipped**（coreclient 61 / host 56 / app 126；base 232 + 主题 9 + 审计 2）；vitest **60 files / 567 tests**；pytest **0F / 2773P / 10S**（全绿，无新增失败）。 |
| AC7 门禁 | **MET** | `check.ps1 -TaskPath` PASS；24 条 64-hex pin；Handoff 含 Record Decision。 |

## 2. 现有 macos-sonoma 达标判定（Lead 要求明确回答）

**已达标，未新增/重复任何 pack 或 id。** 核验项：

| 项 | 结果 |
|---|---|
| 注册与默认 | `ThemePacks.All` = 6 legacy + `macos-sonoma`（7）；`Default.Id == "saber-purple"`；设置页单行「macOS 风」 |
| Light/Dark 双 token | `Tokens`/`Materials`（Light）+ `DarkTokens`/`DarkMaterials`（Dark），`SupportsVariants == true` |
| 既有 token 映射 | AppBg/HeaderBg/CardBg/CardBorder/TextPrimary/TextSecondary/Accent/AccentText/Chip*/SearchBg/Nav*/EmptyBg + HeaderGradient*/CardShadow/MicaFallback 全部有值（`pack.json` checks 全 true） |
| 设计规格 | Light #F5F5F7/#FFFFFF/#ECECEF/#1D1D1F/#6E6E73/#D2D2D7/#007AFF；Dark #1E1E1E/#2C2C2E/#252527/#F5F5F7/#98989D/#3A3A3C/#0A84FF；圆角 12/14/8/6 + 柔和阴影（Metrics）；交通灯仅视觉 |
| 缺口 | 无功能缺口；仅缺「可复核证据 + 回归测试在分支内自洽」——本任务已补齐 |

## 3. Record Decision

| 项 | 决定 | 依据 |
|---|---|---|
| base | 使用 `f1b89c5e5`（main 含 `4be1c3f4f` 构建修复：UI 文件回退 `4ea86e03a`、移除引用不存在成员的测试） | Lead 明确裁决接受；避免在冲突 worktree 继续 |
| 实现范围 | **不新增 pack/id**，只验证 main 已有 `macos-sonoma` | Lead 指示；避免两套同名主题 |
| 测试恢复 | 从 `4ea86e03a` 恢复 `ThemeMacosTests.cs`（9 项，AC1–AC5 + 热切换/对比度/截图/外观切换/交通灯/字体），在我的分支内自洽（build 绿 + 9/9 通过） | Lead 允许「恢复并改造」；该文件是 THEME-MACOS-1 的证据测试，删除后主线 232 基线不再覆盖 AC3/AC4；恢复后 243/243 |
| 新增审计测试 | `ThemeMacosAuditTests.cs`（2 项）：字体许可审计（扫描 0 字体文件 + 栈无 embedded URI）与交通灯仅视觉（装饰/可缩放/扩展客户区/尺寸不变） | AC5 与 AC1 的「仅视觉」约束需要可复核证据 |
| 真机截图方法 | 新增 `--theme` / `--variant` / `--page` 启动选项（仅选择已注册 pack/variant 与已有页面；缺省行为不变），每次启动一个真实 App 进程渲染后截图 | 目标机器指针自动化在 macOS 布局下不稳定（多次误击/导航竞态）；启动态注入是确定性、可复现的真机证据；已在代码注释与卡内记录 |
| 渲染顺序 | 主题/变体在 `MainWindow` 构造**之前**应用 | 该 shell 为 code-built 页面（构造时解析 brush）；先应用变体才能得到真实 Dark 渲染，否则会出现「深色 header + 浅色内容」的伪证据（已实测并纠正） |
| 截图范围 | 4 张真机（书架/设置 × Light/Dark）+ 4 张 headless-Skia 补充 | AC2 要求真机；headless 作为逐像素/可重复回归证据保留 |
| pytest | 报告 **0F/2773P/10S**（全绿） | base 已含 flaky 修复；不再沿用历史 3F 基线 |
| 并发 | 不触碰冲突 worktree；不 reset/stash/删他人目录；只显式 add 自己的文件 | 任务硬约束 + Lead 裁决 |

## 4. 实现摘要（相对 `f1b89c5e5`）

| 文件 | 改动 |
|---|---|
| `tests/NewManga.App.Tests/ThemeMacosTests.cs`（恢复） | 从 `4ea86e03a` 恢复 9 项主题测试（pack 注册/默认、Light/Dark token+material 逐项、热切换 p95、WCAG 对比度、字体栈/交通灯、外观切换、reduced motion、headless 截图、遗留 pack 回归）。 |
| `tests/NewManga.App.Tests/ThemeMacosAuditTests.cs`（新，2 项） | 字体许可审计（0 字体二进制 + 栈无 embedded URI + Inter/SIL OFL 说明）；交通灯仅视觉审计（SystemDecorations/CanResize/ExtendClientArea*/尺寸不变）。 |
| `src/NewManga.App/AppOptions.cs` | +`--theme` / `--variant` / `--page` 三个证据启动选项（缺省不改行为）。 |
| `src/NewManga.App/App.axaml.cs` | 启动时在构造 shell 前应用所选 pack/变体，再导航；缺省路径不变。 |
| `verification/THEME-MACOS-2/**` | 4 张真机截图 + 元数据 + headless 证据 + 测试日志 + 本报告。 |

未改 `ThemePack.cs` / 既有主题页 / Host / Core / 协议 / 旧���。

## 5. 验证证据

| AC/场景 | 实际命令/步骤 | 环境 | 结果 | 产物 |
|---|---|---|---|---|
| AC1 注册/默认 | `MacosPack_IsRegistered_WithChineseLabel_AndDefaultIsUnchanged` | Avalonia Headless 11.3.22 | 7 packs；default saber-purple；macOS 单行中文；legacy 单 token 集 | `headless/theme/pack.json` |
| AC1 交通灯仅视觉 | `MacosTrafficLights_AreVisualOnly_AndDoNotChangeWindowBehaviour` | 同上 | 可见性切换，装饰/可缩放/扩展客户区/尺寸不变 | `headless/theme/traffic-lights-visual-only.json` |
| AC2 token 逐项 | `MacosPack_LightAndDarkMatchFrozenSpec_EveryTokenAndMaterial` | 同上 | Light/Dark 全部 token+material 与规格一致；Corner.Card 14/Button 8/Small 6/Window 12 | `headless/theme/pack.json`、测试日志 |
| AC2 真机 4 图 | 4 个独立 Debug App 进程（隔离数据根 + 冻结 sidecar）：`--theme=macos-sonoma --variant=light|dark --page=settings|bookshelf` → 窗口截图 | Windows 10.0.26300；1440×920（1278×818） | Light 背景 `#F5F5F7`、Dark 背景 `#1E1E1E`（像素采样与 token 一致）；交通灯出现；既有主题仍可切回 | `real-app-bookshelf-light.png`、`real-app-bookshelf-dark.png`、`real-app-settings-light.png`、`real-app-settings-dark.png`、`real-app-screenshots-metadata.json` |
| AC2 headless 4 图 | `MacosScreenshots_RenderFourRealFrames_WithVariantBackgrounds` | Headless+Skia，1280×820 | 4 帧非空白（distinct colors 204–325），Light/Dark 背景不同 | `headless/screenshots/*.png`、`headless/theme/screenshots.json` |
| AC3 热切换 | `HotSwitch_MacosLightDarkAndLegacyPacks_P95Under100ms` | Headless 真实窗口（1280×820） | 48 samples，p95 10.456ms ≤100，max 15.830ms | `headless/theme/hot-switch-macos.json` |
| AC4 对比度 | `MacosContrast_MeetsWcag_ForBodyAndSecondaryText` | 计算（WCAG 2.x） | 正文 ≥12.8、次要 ≥4.65、nav ≥8.52，全部通过 | `headless/theme/contrast.json` |
| AC5 字体 | `MacosFontStack_ShipsNoFontBinary_AndIsSystemOrOflFallbackOnly` | 扫描仓库 + 无 UI | 0 字体二进制；无 embedded URI；Inter 为 OFL 参考 | `headless/theme/font-audit.json` |
| AC6 全量 | `pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1 -EvidenceDirectory <task-env>/evidence-saber` | 干净 worktree | **243/243**（61/56/126），0 skipped | `test/summary.json`、`test/dotnet-test-Debug.log`、`test/results-*.trx` |
| AC6 vitest / pytest | `npm test`（主仓旧壳）/ `PYTHONPATH=src python -m pytest -q`（worktree） | 旧壳/Python 未改 | 60 files / 567 tests；**0F / 2773P / 10S** | `test/vitest.log`、`test/pytest.log` |
| AC7 治理 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/THEME-MACOS-2.md` | 本卡 + 文档提交 | PASS | 任务卡 pin |

## 6. 遗留 / 未关闭项

1. **冲突 worktree**：`worktrees/THEME-MACOS-2` 仍被外部进程占用/污染，未由我清理（不 reset/不删）；最终合入前建议 Lead 处置该目录并删除/归档其未跟踪 WIP。
2. **主题测试来源**：`ThemeMacosTests.cs` 由我按 Lead 允许从 `4ea86e03a` 恢复并逐项跑通；它源出外部会话，但断言与当前 7-pack 实现一致。任何后续对 pack 的改动会使这些断言失效，需要同步更新。
3. **未包含 launchpad/split 布局**：base 修复已把 `ThemePack.cs` 回退到 7-pack（去 layout）；本任务范围只到 `macos-sonoma`，未恢复那三个布局 pack 的 WIP。
4. **热切换测量环境**：p95 在 Avalonia Headless 真实渲染循环测得（真实 framework 路径），不是目标机人工按键计时；真机可交互性由 4 张截图证明。
5. **截图证据 hook**：为稳定出图新增 `--theme/--variant/--page`（缺省无影响）；若产品不需要该类选项，合入时可去掉（截图已存档）。
6. App 的 code-built 页面在「运行中」切换 Light/Dark 时只有资源驱动面刷新（既有行为）；真机 Dark 截图采用启动态（构造前应用），如实记录。
7. 需独立 Review（Owner 不自审）。

## 7. 复现

```pwsh
# 1) 干净 worktree 全量回归（243 项，含主题 9 + 审计 2）
pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1 `
  -EvidenceDirectory G:\CODEX\New Manga.workspace\task-envs\THEME-MACOS-2\evidence-saber

# 2) 主题测试
dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj `
  -c Debug --filter "FullyQualifiedName~ThemeMacos"

# 3) 真机 4 图（每张一个独立进程；隔离数据根 + 冻结 sidecar）
$exe='apps/desktop-avalonia/src/NewManga.App/bin/Debug/net9.0/NewManga.App.exe'
& $exe --data-root=<task-env>/real-app-data-root --sidecar-dir=<RELEASE-REPACK-3>/sidecar-base/core-sidecar `
  --theme=macos-sonoma --variant=light --page=settings --parity --width=1440 --height=920
# 将 --variant/--page 换成 dark/bookshelf 分别截图
```
