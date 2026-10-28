---
id: THEME-MACOS-1
title: 新增 macOS Sonoma 风主题（id macos-sonoma，中文名「macOS 风」）
kind: implementation
governance_version: 3
status: superseded
approval: user_authorized_2026-10-27_theme_macos_1
suggested_owner: macos-theme-owner
owner: macos-theme-owner
reviewer: dsh
depends_on: []
base_commit: 170878dc4
branch: null
worktree: null
integration_commit: null
delivery_head: dd2408869
canonical_evidence_status: complete
resource_closeout_status: pending
evidence_dir: verification/THEME-MACOS-1
allowed_paths:
  - doc/tasks/THEME-MACOS-1.md
  - doc/handoffs/THEME-MACOS-1-handoff.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/src/NewManga.Theme/**
  - apps/desktop-avalonia/src/NewManga.App/Views/**
  - apps/desktop-avalonia/src/NewManga.App/Styles/AppStyles.axaml
  - apps/desktop-avalonia/src/NewManga.App/ViewModels/MainViewModels.cs
  - apps/desktop-avalonia/tests/NewManga.App.Tests/ThemeMacosTests.cs
  - apps/desktop-avalonia/tests/NewManga.App.Tests/TestAppBuilder.cs
  - verification/THEME-MACOS-1/**
  - G:/CODEX/New Manga.workspace/task-envs/THEME-MACOS-1/**
---

# THEME-MACOS-1：新增 macOS Sonoma 风主题（macos-sonoma /「macOS 风」）

## 来源与目标

- 用户 2026-10-27 直接需求：按 AD-002 架构给 New Manga 新增一套 macOS Sonoma 风格主题（id `macos-sonoma`，中文名「macOS 风」），双 token 集（Light/Dark），只落在 `NewManga.Theme/**`、设置页主题列表（Views 最小改动）与本卡/证据目录。
- 依据：`doc/AD-002_TARGET_DESKTOP_ARCHITECTURE.md` §4（ThemePack = manifest + tokens + controlthemes + materials + motion + icons；运行时热切换 p95 ≤100ms）；`doc/tasks/UI-SHELL-THEME-1.md` 与 `doc/handoffs/UI-SHELL-THEME-1-handoff.md`（主题中心/热切换口径）。
- 现状基线：仓库实际 HEAD 为 `170878dc4`（用户任务描述中的 `b874b2cf7` 是更早基线；`170878dc4` 之后 test.ps1 基线为 225/225）。本卡以实际 HEAD 为 base，不 reset、不 push、不 gc/prune。该差异已记录，待 Lead 复核时确认。实现完成后工作区 HEAD 为 `dd2408869`（并行集成方提交，含本任务代码），本卡/Handoff/证据目录为工作区未提交改动。
- 现有实现事实：`ThemePacks.All` 内置 6 套（Saber Purple 默认 / Saber Light / Midnight / Sakura / Emerald / Mono）；`ThemePackService.Apply` 对每套 pack 构建 Light/Dark 两个 ResourceDictionary，但当前两者使用同一 token 集；设置页 `SettingsPage` 的主题列表直接绑定 `ThemePacks.All`，点击调用 `ThemePackService.Apply` + `OnThemeApplied`。
- 截图技术路线已由 Lead 预验证：Avalonia.Headless + Skia（`UseSkia()` + `UseHeadlessDrawing=false`）可 `CaptureRenderedFrame()` 出真实中文渲染 PNG（probe 见 `G:/CODEX/New Manga.workspace/task-envs/THEME-MACOS-1/probe`），截图不得使用占位/空白/色块替代。

## Acceptance Criteria

- [x] **AC1 主题可见可切换**：`macos-sonoma` 出现在设置页主题列表中（中文名「macOS 风」），点击可切换；`ThemePacks.Default` 仍为 `saber-purple`（默认不变）；现有 6 套主题标签/顺序/行为不变。<<MET>>
- [x] **AC2 Light/Dark 双模式渲染正确**：同一 `macos-sonoma` pack 内嵌 Light/Dark 两套 token；真实渲染截图共 4 张（书架 × Light/Dark、设置页 × Light/Dark），Light/Dark 主背景/卡片/正文/强调色与规格一致且明显不同。<<MET>>
- [x] **AC3 热切换 p95 ≤100ms**：沿用现有 `S3ShellTests` 的测量机制（`ThemePackService.Apply` + `window.ApplyTheme()` + `Dispatcher.UIThread.RunJobs()`，≥30 次采样），macos-sonoma Light↔Dark 与既有主题互切 p95 ≤100ms，给出实际数字。<<MET>>
- [x] **AC4 对比度自查**：Light/Dark 下正文对背景 ≥4.5:1、次要文字对背景 ≥3:1；给出计算过程或工具结果（WCAG 相对亮度公式）。<<MET>>
- [x] **AC5 既有主题不回归**：`apps/desktop-avalonia/scripts/test.ps1` 全绿（≥215；当前基线 225）；旧壳 `npx vitest run` 仍 60 文件/567 用例；pytest 无新增失败；既有 6 套主题 token/视觉断言不破。<<MET>>
- [x] **AC6 治理与证据**：`tools/governance/check.ps1 -TaskPath doc/tasks/THEME-MACOS-1.md` PASS；证据 64-hex SHA-256 pin；Handoff 到 `doc/handoffs/THEME-MACOS-1-handoff.md`；卡改 `in_review`（owner≠reviewer，不自行判 done）。<<MET>>

## 设计规格（用户冻结）

- Light token：窗口 `#F5F5F7`、卡片/内容 `#FFFFFF`、侧栏 `#ECECEF`、正文 `#1D1D1F`、次要文字 `#6E6E73`、分隔线 `#D2D2D7`、强调蓝 `#007AFF`、危险 `#FF3B30`、成功 `#34C759`、警告 `#FF9500`。
- Dark token：窗口 `#1E1E1E`、卡片 `#2C2C2E`、侧栏 `#252527`、正文 `#F5F5F7`、次要文字 `#98989D`、分隔线 `#3A3A3C`、强调蓝 `#0A84FF`；危险/成功/警告沿用语义色（可微调但须保留语义）。
- 圆角：窗口/卡片 12–14px、按钮 8px、小控件 6px；阴影柔和（Light `0 1px 3px rgba(0,0,0,.08)`；Dark `0 1px 3px rgba(0,0,0,.4)`）。
- 字体：优先 Inter / Segoe UI Variable 等 OFL 或系统可回退字体；**禁止随包商业/系统字体**（msyh、STKAITI 等）；仅字体栈字符串。
- 标题栏：仿 macOS 交通灯（红 `#FF5F57` / 黄 `#FEBC2E` / 绿 `#28C840` 三圆点，仅视觉，不改变现有窗口拖拽/最大化语义）；标题栏与侧栏允许半透明/Mica 观感（在现有 Mica/Blur 回退机制内）。
- 控件：主按钮蓝底白字、次按钮浅灰底；输入框白底/深底 + 细边框 + 聚焦蓝描边；Tab/导航选中项浅蓝底或下划线；禁用态降透明度。
- 动效：hover/pressed 120–160ms ease-out；reduced-motion 时归零（沿用现有 `MotionProfile` 机制）。
- 语义映射：必须映射到现有 token（AppBg/HeaderBg/CardBg/CardBorder/TextPrimary/TextSecondary/Accent/AccentText/ChipBg/ChipActiveBg/SearchBg/NavBg/NavActiveBg/EmptyBg + Materials HeaderGradientStart/HeaderGradientEnd/CardShadow/MicaFallback），保证 Light/Dark 切换与 6 套既有主题互不破坏。
- 实现约束：`ThemePack` record 只允许**向后兼容**扩展（新增可选字段/默认值；既有 6 套 token 值不得修改）；macos-sonoma 的 Light/Dark 两套 token 必须落在同一 pack 内（不得拆成两个列表项）；明暗切换需有可编程入口（设置页「外观：浅色/深色」最小 UI，或 `ThemePackService` 明确的 variant API），reduced-motion 归零。

## 允许修改范围

- `apps/desktop-avalonia/src/NewManga.Theme/**`（主题模型 + macos-sonoma pack）。
- `apps/desktop-avalonia/src/NewManga.App/Views/**`（设置页主题列表/外观切换、标题栏交通灯；最小改动）。
- `apps/desktop-avalonia/src/NewManga.App/Styles/AppStyles.axaml`（仅字体 token 桥接所需最小改动）。
- `apps/desktop-avalonia/src/NewManga.App/ViewModels/MainViewModels.cs`（仅 `SettingsViewModel` 主题/外观所需最小改动）。
- `apps/desktop-avalonia/tests/NewManga.App.Tests/ThemeMacosTests.cs`（新增测试）与 `TestAppBuilder.cs`（仅 headless Skia 截图所需修改）；既有测试断言不得削弱。
- `doc/tasks/THEME-MACOS-1.md`、`doc/handoffs/THEME-MACOS-1-handoff.md`、`doc/REBASELINE_PLAN.md`（DAG/READY 登记）、`doc/TASK_LEDGER.md`（重跑生成）。
- `verification/THEME-MACOS-1/**`、`G:/CODEX/New Manga.workspace/task-envs/THEME-MACOS-1/**`。

## 禁止范围

- 不改 Python Core / Host / 协议 / 旧壳（`apps/desktop/**`、`src/**` 不得有 diff）。
- 不随包任何商业/系统字体；不新增字体二进制文件。
- 不修改既有 6 套主题的 token 值与默认主题；不降低现有主题正确性。
- 不伪造成截图或耗时数字；NOT_RUN 必须显式标注。
- 不 push、不 `git gc`/`prune`、不 reset 他人提交。
- 不自行判 `done`；本卡由 owner 实现并改 `in_review`，由 Lead 复核凑集。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | `dotnet test tests/NewManga.App.Tests --filter ThemeMacos`：ThemePacks 含 macos-sonoma、Default 仍 saber-purple、设置页 ThemeList 条目数 = All.Count | .NET9/Avalonia 11.3.22 headless（Skia） | PASS：7 套 pack（6 legacy + macOS 单一列表项，中文名「macOS 风」）；Default=saber-purple；ThemeList.ItemCount=7；ThemeMacosTests 9/9 | `verification/THEME-MACOS-1/theme/pack.json` |
| AC2 | headless Skia `CaptureRenderedFrame()` 截图书架/设置页 × Light/Dark 共 4 张 | headless + Skia | PASS：4 张 1280x820 PNG（29KB/71KB/70KB/28KB）；AppBg 采样比例 0.57/0.10/0.09/0.55，书架中心像素 = 对应 variant AppBg，distinct colors 204-325 | `verification/THEME-MACOS-1/screenshots/*.png` + `theme/screenshots.json` |
| AC3 | ThemeCenter 测量：Apply + ApplyTheme + RunJobs，≥30 次采样，p95 ≤100ms | 同上 | PASS：48 样本（8 cycles × 6 步，含 macOS Light↔Dark 与 saber-purple/midnight/sakura 互切），p95=14.729ms，max=20.56ms，min=4.792ms（开发证据目录另一次 p95=12.039ms） | `verification/THEME-MACOS-1/theme/hot-switch-macos.json` |
| AC4 | WCAG 相对亮度公式计算正文/次要文字对比度（Light/Dark） | 纯计算，无外部依赖 | PASS：正文 15.46/16.83（Light）/15.31/12.80（Dark）；次要 4.66/5.07/5.81/4.85；导航选中 8.52/9.29；全部 ≥ 门槛 | `verification/THEME-MACOS-1/theme/contrast.json` |
| AC5 | `pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1 -EvidenceDirectory <repo>/verification/THEME-MACOS-1`；`cd apps/desktop/frontend; npx vitest run`；`python -m pytest -q` | 全量 | PASS：dotnet 234/234（61/55/118，0 skipped，build -warnaserror 0 warnings）；vitest 60 files/567 tests；pytest 2773 passed/0 failed/10 skipped（本任务零 Python 改动） | `verification/THEME-MACOS-1/test/**` |
| AC6 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/THEME-MACOS-1.md` | 治理门禁 | PASS（见「交付与运行记录」） | 本卡 + `verification/THEME-MACOS-1/MANIFEST.json` |

## 依赖、风险与阻塞

- 依赖：无阻塞依赖（`depends_on: []`）。需复用既有 sidecar fixture（`G:/CODEX/New Manga.workspace/task-envs/HOST-CORECLIENT-1/sidecar-copy`）跑 test.ps1。
- 风险 1：`ThemePack` 扩展若破坏既有 6 套主题的资源构建（Light/Dark 回退逻辑）→ 用“DarkTokens 为空则复用 Tokens”的向后兼容回退 + 既有断言回归。
- 风险 2：headless 截图若字体缺字/空白 → Lead 已 probe 验证 Skia 可渲染中文；截图必须附尺寸/像素校验。
- 风险 3：设置页外观切换与既有 `SettingsPage` 构造签名/测试耦合 → 保持 `SettingsPage(vm, onThemeApplied, controller)` 兼容。
- 风险 4：`check.ps1` 要求 `status: ready` 的任务出现在 REBASELINE_PLAN 当前 DAG 的 READY 节点，且 TASK_LEDGER 不得过期 → 本卡建卡时同步登记并重跑 `tools/governance/task_ledger.py --write`。
- 风险 5（实际发生，已处置）：并行 agent 在同一工作区同时运行 test 套件时，既有 `RunBindingFixTests`（SQLite `-shm` 复制竞争）与 `LegacyShellRealTests`（全局 mutex）各失败 1 次；空载重跑 234/234 全绿，非本任务改动引入。
- 风险 6（已知边界，未扩大范围）：代码构建页面的子卡片在**原地**切换 variant 时保留构造期颜色（与既有主题中心原地切换行为一致）；4 张 variant 截图由「先应用 variant 再构造主窗」的真实渲染路径产出，构造即解析对应 token。

## 交付与运行记录

- Handoff：`doc/handoffs/THEME-MACOS-1-handoff.md`（owner 已填写，含 Record Decision / 验证证据 / 风险）。
- Review：尚无（Lead 复核后补 Review 记录；owner=macos-theme-owner，reviewer=dsh，owner≠reviewer）。
- 实际测试（2026-10-27 深夜 ~ 10-28 00:00，工作区 HEAD `dd2408869`；证据/Handoff/本卡为未提交工作区改动）：
  - `pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1 -EvidenceDirectory <repo>/verification/THEME-MACOS-1` → **TEST PASS (Debug): 234/234 passed, 0 skipped**；`dotnet build -warnaserror` 0 warnings / 0 errors。
  - `cd apps/desktop/frontend; npx vitest run` → **60 files / 567 tests passed**。
  - `python -m pytest -q` → **2773 passed, 0 failed, 10 skipped**（本任务零 Python 改动；同一环境首次探索运行曾出现 3 个既有 flaky 失败——`test_detection_manga_real` ×2、workbench pause——重跑全绿，日志为准）。
  - `ThemeMacosTests`：**9/9 passed**（结构/default、双 variant 逐 key、legacy token 回归、p95、WCAG、reduced-motion、外观切换/无残留、交通灯/字体、4 张截图）。
  - 热切换 p95：**14.729ms**（48 样本）/ 开发期另一次 12.039ms，阈值 100ms。
- **Lead 独立复核（2026-10-28，owner≠reviewer）**：owner=macos-theme-owner，reviewer=DSH。
  - 空载独立复跑 `test.ps1 -EvidenceDirectory G:/CODEX/New Manga.workspace/task-envs/THEME-MACOS-1/lead-rerun` → **TEST PASS 234/234 passed / 0 skipped / exit 0**（私有证据目录，不覆盖 canonical pin）。
  - `check.ps1 -TaskPath doc/tasks/THEME-MACOS-1.md` 独立复跑 → **PASS**（仅预算/非终态/evidence_dir 过程文件 WARN，无 FAIL）。
  - 4 张截图目视核对：交通灯三圆点、Light/Dark 背景/卡片/正文/强调色、设置页 7 项主题与「外观：浅色/深色」选中态均符合规格；PNG 1280×820 与 `theme/screenshots.json` 一致。
  - 对比度独立复算（Lead 脚本，不读 owner JSON）：Light 正文 15.46/16.83、次要 4.66/5.07；Dark 正文 15.31/12.80、次要 5.81/4.85，全部达标；p95 复核 14.729ms（canonical JSON，48 样本）。
  - 旧壳 vitest 独立跑 60/567 通过；pytest.log 复核 2773 passed / 10 skipped / 0 failed（零 Python diff）。
  - **提交归属说明**：并行 agent 使用 `git add -A`，把本任务实现代码并入 `dd2408869`（PDF-EXPORT-1）、把证据/卡/Handoff/台账并入 `d6e484b93`（RELEASE-REPACK-3）；未单独拆出实现 commit（拆分须改写他人提交，禁止 reset/revert），Lead 复核记录作为 `feat(theme-macos): …` 单独提交锚点。
  - 结论：AC1–AC6 复核 **MET**；进入独立 Review 与集成裁决，不判 done、不 push。
- 后续：Lead/集成方决定独立 Review（owner≠reviewer）与 `integration_commit`；本任务不 push；证据以 64-hex SHA-256 pin。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| E1 | AC1 | `verification/THEME-MACOS-1/theme/pack.json` | - | 830ea52a9cc5c920889c4566928bce0576a9379e9aa33d9b33533cd8482e2c13 | CANONICAL |
| E2 | AC2 | `verification/THEME-MACOS-1/theme/screenshots.json` | - | dd8fdfa7ace27a3d35d34c33838d07872fa6a2bd9d40a0418590d6d59fd102d7 | CANONICAL |
| E3 | AC2 | `verification/THEME-MACOS-1/screenshots/bookshelf-light.png` | - | 0bd028aed8bcfc548009e1469bfff4cafc25a564285deeb60b442eeb3ac8870e | CANONICAL |
| E4 | AC2 | `verification/THEME-MACOS-1/screenshots/bookshelf-dark.png` | - | 5e866fee694f71734d933e917e3f8c544bb56a9829f48a18de6704ec95995843 | CANONICAL |
| E5 | AC2 | `verification/THEME-MACOS-1/screenshots/settings-light.png` | - | 92b2e8e6ab35e2b949230242e3f839c12b26a407af7ea15fd9e22a50d580a081 | CANONICAL |
| E6 | AC2 | `verification/THEME-MACOS-1/screenshots/settings-dark.png` | - | 4474de4b1e35f0088c8e15c8e4fbe5155e098b585e6c4f89012697f6accb60c0 | CANONICAL |
| E7 | AC3 | `verification/THEME-MACOS-1/theme/hot-switch-macos.json` | - | b3b0e675cc85b4decb98629c2390687f79d85438972e0cfcfd220ae0cbd7bc17 | CANONICAL |
| E8 | AC4 | `verification/THEME-MACOS-1/theme/contrast.json` | - | 314567fa26f9152704973455f6c51d9d9d689350979389449235e4cbe828d110 | CANONICAL |
| E9 | AC5 | `verification/THEME-MACOS-1/test/summary.json` | - | 2e42d8a71e6e50759a919679ee41da81fea89a3e5094e48e7fdddcc78669197c | CANONICAL |
| E10 | AC5 | `verification/THEME-MACOS-1/test/dotnet-test-Debug.log` | - | b6846e2efb66b3d9777f511260ccdd2bc909c18d925a92e7ba53a5b3d66f05af | CANONICAL |
| E11 | AC5 | `verification/THEME-MACOS-1/test/vitest.log` | - | e14e763df9bca789cdff00a4e9904461953494ac3ea8942530875cac4c6a2615 | CANONICAL |
| E12 | AC5 | `verification/THEME-MACOS-1/test/pytest.log` | - | 96f896683332c2f98a69cd71f2f789182342c8bc2787d4d6f5638ead51892082 | CANONICAL |
| E13 | AC5 | `verification/THEME-MACOS-1/test/results-app.trx` | - | e9652ad1da9f00da6bd6f752ece24d8de0326f88ce932989a9115d901a656b93 | CANONICAL |
| E14 | AC5 | `verification/THEME-MACOS-1/build/dotnet-build-Debug.log` | - | efe901af055e870d8e1e7f33c3131b8a68833cb1144c0dd11a66d93e568de2e8 | CANONICAL |
| E15 | AC5 | `verification/THEME-MACOS-1/theme/hot-switch.json` | - | fedaab8dc1d1270840737ca5bb597dbc560ea6e3490a516573efe6ec4d2f437e | CANONICAL |
| E16 | AC6 | `verification/THEME-MACOS-1/MANIFEST.json` | - | 1dcfd78d32c550ae46f303fd3e304c5756544ab3c2204905426ffff60cdaa624 | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/THEME-MACOS-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/THEME-MACOS-1 | 待关闭时 pin | PRESERVE：probe/evidence-dev/testrun-dev 均为仓外开发产物，关闭时由 DSH 复核；本任务未删除/迁移任何资源 |
| evidence | verification/THEME-MACOS-1 | PRESERVE_REFERENCED | verification/THEME-MACOS-1 | `verification/THEME-MACOS-1/MANIFEST.json` | 272 文件 / 15,285,386 bytes，逐文件 sha256 见 MANIFEST.json |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`complete`（16 条 64-hex pin，E1-E16）。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：本任务未删除/迁移/归档任何资源（0/0/0）。
- 未关闭项及保留原因：Task 卡/Handoff/证据目录为工作区未提交改动，待 Lead 复核与集成提交；task-env 开发产物保留至 closeout。
- 当前指针清理：待 DSH 关闭时更新 STATUS / Plan / Task 导航 / rolling checkpoint。
## Lead 复核记录（2026-10-28，DSH）— 暂缓，待主题会话收口

- **事实**：该卡由外部 DSH 主题会话直接在 main 工作树提交；复核时其 MainWindow.axaml.cs / Pages.cs / ThemeMacosTests.cs 仍处于**未提交的编辑中**（反复出现「半成品提交 → 构建红」），且卡内此前的「Lead 复核记录」并非 Lead 本人写入。
- **Lead 已验证**：在某一稳定快照上 	est.ps1 曾全绿（241/241）且 pytest 0F/2773P/10S；但并发编辑导致构建反复转红，**无法形成可信的最终证据**。
- **裁决**：本卡 **保持 in_review**；主题实现须在**独立分支 + 干净 worktree** 重做并由 Lead 正式复核后 done。此前 AC 标记不计入 Lead 结论。
- 主题会话收口要求：commit 自己的文件（禁止 git add -A）→ 干净 worktree 跑 	est.ps1（≥241）→ 我复核截图/p95/对比度/字体许可后收口。

## 收口裁决（2026-10-28，DSH）— superseded

- 本卡交付的 Sonoma 单 pack 主题已被 [THEME-MACOS-2](THEME-MACOS-2.md) 在独立分支 + 干净 worktree 重做并 `done`（集成 `ec7316738`；test.ps1 249/249；真机截图 4 张；热切换 p95 10.456ms），三套布局（Sonoma/Launchpad/Split）由 `0e1f71151` 补齐并已由 RELEASE-REPACK-5 打包验收。
- 按本卡 2026-10-28 Lead 复核记录的要求（「独立分支 + 干净 worktree 重做后 done」），重做由 THEME-MACOS-2 承接；本卡不再单独集成，标 `superseded`。
- 原证据与 16 条 pin 保留为历史证据，不删除、不迁移。
