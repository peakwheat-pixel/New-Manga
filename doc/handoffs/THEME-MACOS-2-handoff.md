---
task_id: THEME-MACOS-2
author: saber-ui-spec (DSH team)
recipient: DeepSeek Harness
base_commit: f1b89c5e5
delivery_head: bfaec8f54fb7d817959b04d8f97c1f954a2d0465
status: ready-for-integration
---

# Handoff：THEME-MACOS-2（macOS 风主题重做，独立分支）

## 交付结果

实现/证据提交 **`bfaec8f54fb7d817959b04d8f97c1f954a2d0465`**（branch `task/THEME-MACOS-2-saber`，worktree `G:/CODEX/New Manga.workspace/worktrees/THEME-MACOS-2-saber`）；本 Handoff 与任务卡 pin 在后续文档提交记录。

- **base**：`f1b89c5e5`（Lead 裁决：main 含 `4be1c3f4f` 构建修复，接受为 base；原卡/指令 base 为 `d2f66a19e`/`84dd38978`）。
- **冲突处置**：Lead 指定的 `worktrees/THEME-MACOS-2` 被外部会话并发写入（未跟踪 `ThemeLayoutsTests.cs`、`verification/THEME-MACOS-2/`、`ThemePack.cs` 被改回 9-pack layouts 版等）。我**未 reset/未删除/未提交**该目录，已报告 Lead 并获准改在独立 worktree 继续；冲突目录留 Lead 处置。
- **范围判定（Lead 要求）**：核验后 main 的 `macos-sonoma` **已达标**（7 packs、默认 `saber-purple`、Light/Dark 双 token/material 齐全、既有 token 全映射）→ **未新增/重复任何 pack 或 id**；本任务 = 验证 + 补齐（测试/审计/真机证据）+ 出证据。
- 未改 `ThemePack.cs`、Core、协议、Host 契约、旧壳；未 push / gc / prune；未写真实 `%APPDATA%`；不伪造结果。

| AC | 结论 | 说明 |
|---|---|---|
| AC1 主题可见可切换 | **MET** | 设置页主题中心 7 packs，`macos-sonoma`「macOS 风」单行；默认仍 `saber-purple`；6 个既有 pack token/字体/单 token 集不变；交通灯仅视觉（审计）。 |
| AC2 Light/Dark 渲染 | **MET** | 双 token+material 全部按冻结规格映射；**4 张真机截图**（书架/设置 × Light/Dark，AppBg 像素 `#F5F5F7`/`#1E1E1E`）；+4 张 headless-Skia 补充。 |
| AC3 热切换 | **MET** | 48 samples：**p95 = 10.456 ms**，max 15.830 ms，min 4.358 ms（≤100ms）。 |
| AC4 对比度 | **MET** | 正文 Light 15.457/16.830、Dark 15.311/12.800；次要 Light 4.658/5.071、Dark 5.806/4.853；nav-active 8.521/9.290。 |
| AC5 字体许可 | **MET** | 0 字体二进制；栈仅系统族 + Inter（SIL OFL 1.1，未随包）+ sans-serif。 |
| AC6 回归 | **MET** | test.ps1 **243/243**（61/56/126，0 skipped）；vitest **60/567**；pytest **0F/2773P/10S**。 |
| AC7 门禁 | **MET** | check.ps1 -TaskPath PASS；25 条 64-hex pin；本 Handoff 含 Record Decision。 |

## Record Decision

1. **不新增主题 id**：Lead 指示「若 main 的 macos-sonoma 基本达标则只验证/补齐」。逐项核验（注册顺序/默认/双 token/全部必需 key/规格色/圆角/阴影/字体栈）均通过，故只补证据，不引入第二套同名主题。
2. **测试恢复**：main 的 `4be1c3f4f` 删除了 `ThemeMacosTests.cs`（因引用了 layouts 版不存在的成员），导致 AC3/AC4/截图/外观切换在主线上无回归覆盖。我按 Lead 允许从 `4ea86e03a` 恢复该 9 项测试，并在 `f1b89c5e5`（7-pack）上逐项跑通（9/9）。
3. **新增审计测试**（`ThemeMacosAuditTests`）：字体许可（扫描 `apps/desktop-avalonia` 排除 bin/obj 的字体二进制 = 0；字体栈无 `avares://`/字体扩展名；Inter 记为 OFL 参考）；交通灯仅视觉（切换前后 `SystemDecorations`/`CanResize`/`ExtendClientArea*`/窗口尺寸均不变）。
4. **真机截图方法**：macOS 布局下指针自动化多次误击/导航竞态（已实测失败与一次异常退出），改用新增的 `--theme` / `--variant` / `--page` 启动证据选项：每张截图一个真实 App 进程，启动即处于目标主题/变体/页面；缺省无该选项时行为完全不变。
5. **渲染顺序修正**：主题/变体在 `MainWindow` 构造**之前**应用。该 shell 的页面是 code-built（构造时解析 brush）；先构造再切变体会得到「深色 header + 浅色内容」的伪 Dark，已实测并纠正为真实 Dark 渲染。
6. **pytest 基线**：base 已合入 flaky 修复，本分支 **0F/2773P/10S 全绿**；不再沿用历史 3F 基线。
7. **并发边界**：只显式 `git add` 本任务文件；不 `git add -A`；不触碰他人 worktree/未提交内容。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境 | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 注册/默认 | `MacosPack_IsRegistered_WithChineseLabel_AndDefaultIsUnchanged` | Avalonia Headless 11.3.22 | 7 packs；default saber-purple；macOS 单行中文；legacy 单 token 集 | `headless/theme/pack.json` |
| AC1 交通灯 | `MacosTrafficLights_AreVisualOnly_AndDoNotChangeWindowBehaviour` | 同上 | 仅可见性切换；装饰/缩放/客户区/尺寸不变 | `headless/theme/traffic-lights-visual-only.json` |
| AC2 token 逐项 | `MacosPack_LightAndDarkMatchFrozenSpec_EveryTokenAndMaterial` | 同上 | Light/Dark 全部 token+material 与规格一致；Corner 14/8/6/12 | `headless/theme/pack.json`、`test/dotnet-test-Debug.log` |
| AC2 真机 4 图 | 4 个独立 Debug App 进程（隔离数据根 + 冻结 sidecar；`--theme=macos-sonoma --variant=light|dark --page=settings|bookshelf`）→ 窗口截图 | Windows 10.0.26300；1440×920（1278×818） | 背景采样 `#F5F5F7` / `#1E1E1E`；交通灯出现；既有主题可切回 | `real-app-bookshelf-light.png`、`real-app-bookshelf-dark.png`、`real-app-settings-light.png`、`real-app-settings-dark.png`、`real-app-screenshots-metadata.json` |
| AC2 headless 4 图 | `MacosScreenshots_RenderFourRealFrames_WithVariantBackgrounds` | Headless+Skia 1280×820 | 4 帧非空白（distinct colors 204–325），Light/Dark 背景不同 | `headless/screenshots/*.png`、`headless/theme/screenshots.json` |
| AC3 热切换 | `HotSwitch_MacosLightDarkAndLegacyPacks_P95Under100ms` | Headless 真实窗口 | 48 samples；p95 10.456ms；max 15.830ms | `headless/theme/hot-switch-macos.json` |
| AC4 对比度 | `MacosContrast_MeetsWcag_ForBodyAndSecondaryText` | WCAG 2.x 计算 | 全部通过（正文 ≥12.8，次要 ≥4.65，nav ≥8.52） | `headless/theme/contrast.json` |
| AC5 字体 | `MacosFontStack_ShipsNoFontBinary_AndIsSystemOrOflFallbackOnly` | 仓库扫描 + 无 UI | 0 字体二进制；无 embedded URI | `headless/theme/font-audit.json` |
| AC6 全量 | `pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1 -EvidenceDirectory <task-env>/evidence-saber` | 干净 worktree | **243/243**（61/56/126），0 skipped | `test/summary.json`、`test/dotnet-test-Debug.log`、`test/results-*.trx` |
| AC6 vitest / pytest | `npm test`（主仓）/ `PYTHONPATH=src python -m pytest -q`（worktree） | 旧壳/Python 未改 | 60 files / 567 tests；0F/2773P/10S | `test/vitest.log`、`test/pytest.log` |
| AC7 治理 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/THEME-MACOS-2.md` | 本卡 + 文档提交 | PASS | 任务卡 pin |

## 接收方式

- 分支/worktree：`task/THEME-MACOS-2-saber` / `G:/CODEX/New Manga.workspace/worktrees/THEME-MACOS-2-saber`；delivery head `bfaec8f54`。
- 复现：`verification/THEME-MACOS-2/REPORT.md §7`。
- 前置：真机截图需桌面会话 + `RELEASE-REPACK-3` 冻结 sidecar + 隔离数据根；token 数值验证只需 headless。
- 需要 DSH 做：独立 Review（Owner 不自审）→ 重跑 test.ps1（243/243；注意其它 Agent 的 NewManga.App 占用全局互斥体时 LegacyShellRealTests 会假失败）→ 处理冲突 worktree（`worktrees/THEME-MACOS-2` 的未跟踪 WIP）→ 集成 → closeout。
- 合入提示：`--theme/--variant/--page` 仅为截图证据 hook，若产品不需要可在合入时单独移除（截图已存档）；`ThemeMacosTests.cs` 断言与 7-pack 实现绑定，改动 pack 需同步。

## 下一任务建议（必填）

- Task ID / 标题：**无必须由我立即释放的实现任务**；可选后续（由 DSH 裁决）：
  1. `THEME-MACOS-LAYOUTS-2`（若仍需要）：launchpad/split 布局重做——但那属于被移除的 WIP，需新卡与新证据，不在本卡范围；
  2. `THEME-SWITCH-PERSIST-1`：主题/变体选择持久化（当前每次启动回默认，需产品裁决）。
- 推荐 Agent / Reviewer：UI 后续 = saber-ui-spec；Reviewer = 未参与实现者（DSH 排班）。
- 推荐原因与前置依赖：macOS 主题已可用且有证据；布局扩展与持久化都超出本卡 AC，需 DSH 决定是否立项。
- Recovery point：仓库 `G:/CODEX/New Manga`；delivery head `bfaec8f54`；base `f1b89c5e5`。
- 允许修改路径：`apps/desktop-avalonia/**`、新任务卡、STATUS/PLAN/LEDGER、`verification/<新任务>/**`。
- 禁止范围：不改 Core 语义/协议/Host 契约/旧壳；不触碰他人 worktree/未提交内容；不 push/gc/prune。
- 交付物：后续实现 + headless/真机证据 + 报告 + Handoff。
- 验证命令与完成 Gate：test.ps1 全绿（≥243）、vitest 60/567、pytest 无新增失败、`check.ps1 -TaskPath` PASS、64-hex pin、独立 Review。
- 可直接转发给 Agent 的指令：

```text
作为独立 Reviewer（未参与实现），复核 THEME-MACOS-2（delivery bfaec8f54，walkthrough 见 doc/handoffs/THEME-MACOS-2-handoff.md 与 verification/THEME-MACOS-2/REPORT.md）。
只读：不要修改代码。
1) 核对 AC1–AC7 与 25 条 pin（sha256 与文件一致）；
2) 确认未新增 pack/id：ThemePacks.All = 6 legacy + macos-sonoma；默认 saber-purple；Light/Dark token/material 逐项与 doc 冻结规格一致；
3) 抽查 hot-switch（p95 10.456ms）、contrast（正文/次要/nav 全部通过）、font-audit（0 字体二进制）、traffic-lights 审计（装饰/缩放/客户区不变）；
4) 查看 4 张真机截图（real-app-bookshelf/settings × light/dark，背景 #F5F5F7/#1E1E1E）与 metadata；
5) 重跑 pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1（应 243/243；注意其它 Agent 的 NewManga.App 占用全局互斥体时 LegacyShellRealTests 会假失败）与 dotnet test --filter FullyQualifiedName~ThemeMacos（应 11/11）；
6) 确认 base=f1b89c5e5、未触碰冲突 worktree、未 push、未改 Core/协议/Host 契约/旧壳。
给出 PASS / 有条件 PASS / 返修 结论与具体证据行。
```

## 风险与遗留

1. **冲突 worktree**：`worktrees/THEME-MACOS-2` 仍含外部会话 WIP（未跟踪 `ThemeLayoutsTests.cs`/`verification/THEME-MACOS-2/`+ 9-pack 版文件），本任务未清理，需 Lead 处置后再删除/归档。
2. **主题测试来源**：`ThemeMacosTests.cs` 源出 THEME-MACOS-1 外部会话（从 `4ea86e03a` 恢复），我已独立跑通；它不是在我分支上手写的，Reviewer 应视为恢复的回归测试。
3. **未包含 launchpad/split**：main 修复已移除布局 profile 实验；本卡只覆盖 `macos-sonoma`。
4. **p95 环境**：headless 真实 Avalonia 渲染循环测量，不是目标机人工计时。
5. **证据 hook**：`--theme/--variant/--page` 是新增 CLI（缺省不变）；如产品不需要可在合入时移除。
6. **运行中切换 Light/Dark** 只刷新资源驱动面（既有 code-built 页面行为）；真机 Dark 用启动态，如实记录。
7. 需独立 Review（Owner 不得自审）。
