---
task_id: THEME-MACOS-1
author: macos-theme-owner
recipient: DeepSeek Harness
base_commit: 170878dc4
delivery_head: dd2408869
status: draft
---

# Handoff：THEME-MACOS-1

## 交付结果

- AC1 主题中心：新增第 7 套 pack `macos-sonoma`（中文名「macOS 风」），在设置页主题列表**只出现一次**（单 pack 内嵌 Light/Dark 双 token 集）；`ThemePacks.Default` 仍为 `saber-purple`，既有 6 套的 id/标签/顺序/token 值不变（回归断言 + `theme/pack.json`）。
- AC2 双模式：同一 pack 的 `Tokens/Materials`（Light）与新增可选 `DarkTokens/DarkMaterials`（Dark）逐 key 覆盖全部既有 token（14 个）+ 新增 `NavActiveText` + 3 个语义色 + 4 个 Materials；`ThemePackService.ApplyVariant/CurrentVariant` 提供可编程明暗入口，设置页「外观：浅色/深色」最小 UI；4 张 **真实 headless-Skia 渲染** 1280x820 PNG（书架/设置 × Light/Dark）含 AppBg 像素断言与中心像素断言。
- AC3 热切换：沿用 `S3ShellTests` 测量方式（`Apply`/`ApplyVariant` + `window.ApplyTheme()` + `RunJobs`），48 样本（8 cycles × 6 步：macOS Light↔Dark + saber-purple/midnight/sakura 互切），canonical 运行 **p95=14.729ms / max=20.56ms**（≤100ms；开发证据目录另一次 p95=12.039ms）。
- AC4 对比度：WCAG 相对亮度公式纯计算，正文 15.46/16.83（Light）、15.31/12.80（Dark）；次要文字 4.66/5.07、5.81/4.85；导航选中 8.52/9.29；全部 ≥ 门槛（正文 4.5 / 次要 3）。
- AC5 回归：`scripts/test.ps1` **234/234 passed, 0 skipped**（coreclient 61 / host 55 / app 118，含新增 ThemeMacosTests 9 项；`dotnet build -warnaserror` 0 warnings）；旧壳 vitest **60 files / 567 tests**；pytest **2773 passed / 0 failed / 10 skipped**（本任务零 Python 改动）。
- AC6 治理：本卡改 `in_review`，16 条 64-hex SHA-256 pin（E1-E16），`verification/THEME-MACOS-1/MANIFEST.json` 覆盖 272 个证据文件；`check.ps1 -TaskPath doc/tasks/THEME-MACOS-1.md` PASS。
- 变更路径（实现代码已由并行集成方提交于 `dd2408869`；本 Handoff/证据/卡/Plan/Ledger 为工作区未提交改动）：
  - `apps/desktop-avalonia/src/NewManga.Theme/ThemePack.cs`
  - `apps/desktop-avalonia/src/NewManga.App/Views/MainWindow.axaml`、`MainWindow.axaml.cs`
  - `apps/desktop-avalonia/src/NewManga.App/Views/Pages.cs`
  - `apps/desktop-avalonia/src/NewManga.App/Styles/AppStyles.axaml`
  - `apps/desktop-avalonia/src/NewManga.App/ViewModels/MainViewModels.cs`
  - `apps/desktop-avalonia/tests/NewManga.App.Tests/ThemeMacosTests.cs`（新增 9 测试）
  - `apps/desktop-avalonia/tests/NewManga.App.Tests/TestAppBuilder.cs`（headless→Skia headless）
  - `verification/THEME-MACOS-1/**`、`doc/tasks/THEME-MACOS-1.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 | `dotnet test tests/NewManga.App.Tests --filter ThemeMacos`；7 pack 结构/默认/顺序/ThemeList 条目 | .NET 9 / Avalonia 11.3.22 headless+Skia，HEAD `dd2408869` | PASS 9/9 | `verification/THEME-MACOS-1/theme/pack.json` |
| AC2 | headless Skia `CaptureRenderedFrame()` 4 张 + 像素/尺寸断言 | 同上 | PASS 4×1280x820；AppBg 采样比 0.57/0.10/0.09/0.55；distinct colors 204-325 | `verification/THEME-MACOS-1/screenshots/{bookshelf,settings}-{light,dark}.png`、`theme/screenshots.json` |
| AC3 | 48 次热切计时（≥30） | 同上 | PASS p95=14.729ms / max=20.56ms / min=4.792ms | `verification/THEME-MACOS-1/theme/hot-switch-macos.json` |
| AC4 | WCAG 相对亮度公式 | 纯计算 | PASS（10 组对比度全部达标） | `verification/THEME-MACOS-1/theme/contrast.json` |
| AC5 | `pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1 -EvidenceDirectory <repo>/verification/THEME-MACOS-1` | 全量 + sidecar fixture | PASS 234/234，0 skipped | `verification/THEME-MACOS-1/test/{summary.json,dotnet-test-Debug.log,results-*.trx}`、`build/dotnet-build-Debug.log` |
| AC5 | `cd apps/desktop/frontend; npx vitest run` | 旧壳前端 | PASS 60 files / 567 tests | `verification/THEME-MACOS-1/test/vitest.log` |
| AC5 | `python -m pytest -q` | Python 全量 | PASS 2773 passed / 0 failed / 10 skipped（零 Python 改动；首次探索运行含 3 个既有 flaky，重跑全绿） | `verification/THEME-MACOS-1/test/pytest.log` |
| AC6 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/THEME-MACOS-1.md` | 治理门禁 | PASS | 本卡 Canonical Evidence E1-E16、`verification/THEME-MACOS-1/MANIFEST.json` |

未运行：真机 Mica/Windows 11 视觉 smoke（本任务只要求 headless 渲染证据）；`NOT_RUN` 不写成通过。

## Record Decision

1. **双 variant 模型（向后兼容扩展）**：`ThemePack` 仍是同一 record，新增可选 `DarkTokens`/`DarkMaterials`（null/空 = 复用 Tokens/Materials，旧 6 套行为逐字节等价）、`Metrics`（默认 12/12/8/6 且无阴影）、`FontFamily`（默认旧字体栈）、按 pack 的 `Motion`。`ThemePackService.Apply` 语义不变；新增 `ApplyVariant(Application, ThemeVariant)` / `CurrentVariant`，`BuildVariant` 仅在 Dark 有覆盖时取 Dark token、否则回退 Light token；`NavActiveText` 旧 pack 回退 `AccentText`，因此 6 套旧主题视觉零变化。macOS Light/Dark 必须同 pack（列表仍 7 项）是用户冻结约束。
2. **设置页外观切换**：「主题中心」卡片内 ThemeList 下新增「外观：浅色/深色」行，仅当前 pack `SupportsVariants` 时显示；主题按钮点击与 variant 切换均刷新选中态/外观行（`ApplyTheme` 自查），保持 `SettingsPage(vm, onThemeApplied, controller)` 构造签名与 `ThemeList.ItemCount` 兼容。
3. **字体**：`AppStyles.axaml` 的 Window `FontFamily` 改为 `{DynamicResource AppFontFamily}`；pack 提供字体栈字符串，服务发布**解析后的 `FontFamily` 资源**（DynamicResource 不做 string→FontFamily 转换，字符串资源会抛 `InvalidCastException`）。旧 6 套沿用原栈，macOS 用 `Segoe UI Variable Text, Inter, Segoe UI, ...`；不随包任何字体文件。
4. **标题栏交通灯**：`MainWindow.axaml` TitleBar 左侧 3 个固定色 Ellipse（#FF5F57/#FEBC2E/#28C840），`IsHitTestVisible=false` 且不改 `OnTitleBarPressed/BeginMoveDrag`；仅 macOS pack 显示，并用 `HeaderBg` token 给标题条上色（旧 pack 不设背景，避免 Mica/旧视觉回归）。
5. **Metrics（圆角/阴影）**：macOS pack 定义 CornerWindow 12 / CornerCard 14 / CornerButton 8 / CornerSmall 6，`CardShadowFor(variant)` 返回 Light `0 1 3 0 #14000000` / Dark `0 1 3 0 #66000000`；设置页主题卡读 `CornerCard`+`BoxShadow`，主题/外观按钮读 `CornerButton/CornerSmall`，旧 pack 默认值使视觉不变。
6. **截图与证据路线**：`TestAppBuilder` 由 headless no-op drawing 改为 `UseSkia() + UseHeadlessDrawing=false`，测试内 `CaptureRenderedFrame()` 出真实 PNG；每个 variant 先应用主题再**新建主窗**渲染（代码构建页面在构造期解析 token，与既有原地切换行为一致），断言 PNG 尺寸/大小/`AppBg` 像素比例/书架中心像素/颜色多样性，防空白与占位。证据统一落 `verification/THEME-MACOS-1/**`，`MANIFEST.json` 逐文件 sha256 + AC 映射；本工作区并行 agent 并发跑测试时既有 SQLite shm / 全局 mutex flaky 各出现 1 次，空载重跑全绿。

## 接收方式

- 仓库 `G:/CODEX/New Manga`，实际 HEAD `dd2408869`（实现代码所在 commit）；本 Handoff 与 `doc/tasks/THEME-MACOS-1.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`、`verification/THEME-MACOS-1/**` 为工作区未提交改动，由 DSH 复核后决定集成提交。
- 复跑：`pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1 -EvidenceDirectory <abs>/verification/THEME-MACOS-1`（相对路径会因脚本 Push-Location 解析到错误目录，请用绝对路径）；`cd apps/desktop/frontend; npx vitest run`；`python -m pytest -q`。
- 前置：Windows 11 / .NET SDK 9；无标签 sidecar 副本 `G:/CODEX/New Manga.workspace/task-envs/HOST-CORECLIENT-1/sidecar-copy`；BOOK-FIXTURE/region fixture 已存在（test.ps1 自检）。
- 接收者检查：`ThemeMacosTests` 9/9；`test/summary.json` 234/234；4 张截图肉眼核对（交通灯/浅深色/设置页外观行）；`apps/desktop/**`、`src/**` 无 diff；`check.ps1 -TaskPath` PASS。

## 下一任务建议

- Task ID / 标题：无新增实现任务；由 Lead 对 THEME-MACOS-1 指派独立 Review（owner≠reviewer）并决定集成提交。
- 推荐 Agent / Reviewer：Reviewer=dsh（本卡 front matter 已登记）；如需独立复核，可选未参与实现的 ZCode/Antigravity/Codex。
- 推荐原因与前置依赖：实现与证据已齐（AC1-AC6 全 MET），只需独立复核 4 张截图与证据 pin 即可裁决。
- Recovery point：仓库 `G:/CODEX/New Manga`，base `170878dc4`，实现 commit `dd2408869`；未创建 worktree。
- 允许修改路径：无（Review 只读）；Review 结论写入 `doc/reviews/THEME-MACOS-1.md` 需由 DSH 或指派 Reviewer 按治理规则创建。
- 禁止范围与新增授权条件：不改 Python Core/Host/协议/旧壳、不改既有 6 套 token、不 push/gc/prune/reset。
- 交付物：Review 结论 + 集成提交（由 DSH）。
- 验证命令、环境与完成 Gate：`pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/THEME-MACOS-1.md` PASS；`test.ps1` 0 failed。
- 可直接转发给 Agent 的指令：`只读复核 THEME-MACOS-1：核对 verification/THEME-MACOS-1/theme/{pack,hot-switch-macos,contrast}.json、screenshots/*.png（4 张 1280x820）与 test/summary.json；运行 check.ps1 -TaskPath doc/tasks/THEME-MACOS-1.md；不要修改源码或证据，不 push。`

## 风险与遗留

- **并发窗口**：同一工作区多个 agent 并行跑 `test.ps1` 时，既有 `RunBindingFixTests`（SQLite `-shm` 复制竞争）与 `LegacyShellRealTests`（全局 mutex）各出现过 1 次失败，空载重跑 234/234 全绿；与本任务改动无关，但复核时建议空载复跑。
- **原地切换的已知边界**：代码构建页面的子卡片保留构造期颜色（既有主题中心原地切换的既有行为）；macOS 的 4 张 variant 截图由「先应用 variant 再构造主窗」的真实路径产出。若后续要求原地整页换肤，应另立 Task 做页面级 DynamicResource 改造，不在本卡范围内扩大。
- **相对路径陷阱**：`test.ps1 -EvidenceDirectory` 必须传绝对路径（脚本在 `Push-Location` 前用相对路径创建目录、之后 Tee-Object 解析会落到 `apps/desktop-avalonia/` 下），已在 Handoff 与复核命令中标注。
- **未做真机 smoke**：Mica/Windows 11 实际观感未截图（headless 无 Mica）；如需真机验收由 RELEASE-SMOKE-1/RELEASE-REPACK-3 覆盖。
- 回退方法：删除 `macos-sonoma` pack 项与 Views/Styles/ViewModel 的增量改动即可回到 6 套主题基线；本任务未删除任何文件。
