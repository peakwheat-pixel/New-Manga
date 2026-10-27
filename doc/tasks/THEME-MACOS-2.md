---
id: THEME-MACOS-2
title: macOS 风主题重做（独立分支，三套布局主题）
kind: implementation
governance_version: 3
status: in_review
approval: user_authorized_2026-10-28_goal_all_authorized
suggested_owner: saber-ui-spec
owner: macos-layout-owner
reviewer: dsh
depends_on: []
base_commit: d2f66a19e
branch: task/THEME-MACOS-2
worktree: G:/CODEX/New Manga.workspace/worktrees/THEME-MACOS-2
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/THEME-MACOS-2
allowed_paths:
  - doc/tasks/THEME-MACOS-2.md
  - doc/handoffs/THEME-MACOS-2-handoff.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/src/NewManga.Theme/**; apps/desktop-avalonia/src/NewManga.App/**; apps/desktop-avalonia/tests/**
  - verification/THEME-MACOS-2/**
  - G:/CODEX/New Manga.workspace/task-envs/THEME-MACOS-2/**
  - G:/CODEX/New Manga.workspace/worktrees/THEME-MACOS-2/**
---

# THEME-MACOS-2：macOS 风主题重做（独立分支，三套布局主题）

## 背景
`THEME-MACOS-1` 由外部会话直接在 main 工作树编辑，反复出现半成品提交导致构建红；该卡复核已暂缓。本任务在**独立分支**（worktree `G:/CODEX/New Manga.workspace/worktrees/THEME-MACOS-2`，branch `task/THEME-MACOS-2`）重做，避免并发污染。
按用户 2026-10-28 Goal（「完成三套不同界面布局的 mac 风格主题」），本卡在 THEME-MACOS-1 的 Sonoma 主题基础上扩展为**三套不同界面布局**：`macos-sonoma`（现有 Sonoma 布局）、`macos-launchpad`（底部 Dock + Launchpad 大图标网格 + 单列设置）、`macos-split`（左侧 Sidebar + 书列表/分栏设置）。实现代码从 `THEME-MACOS-LAYOUTS-1` 外部 WIP（`G:/CODEX/New Manga.workspace/task-envs/EXTERNAL-THEME-WIP-20261028/`）恢复，并在本 worktree 内补齐/验证（SettingsPage.ApplyLayout、StatusLine、BodyHostControl、ThemeMacosTests 计数、`_themeButtons` 去重、Dock 遮挡与 Launchpad 卡片定高两处视觉修复）。

## Acceptance Criteria
- [x] **AC1 主题可见可切换**：`macos-sonoma` / `macos-launchpad`「macOS 启动台」/ `macos-split`「macOS 分栏」三套 mac 主题各在设置页主题列表出现一次（`ThemePacks.All`=9）；`ThemePacks.Default` 仍为 `saber-purple`；旧 6 套 id/标签/顺序/token 不变（见 AC8）。 <<MET>>
- [x] **AC2 Light/Dark 渲染**：同一 pack 内嵌 Light/Dark 两套 token；真实渲染截图扩展为三套 × 书架/设置 × Light/Dark 共 12 张 1280×820（Avalonia headless+Skia `CaptureRenderedFrame()`，见 AC9）；sonoma 4 张与 THEME-MACOS-1 canonical 截图逐字节相同（零视觉回归）。 <<MET>>
- [x] **AC3 热切换**：布局切换 36 样本 p95=20.151ms（max=23.565ms），同布局 Light/Dark 36 样本 p95=14.155ms（max=14.695ms），均 ≤100ms（沿用 `Apply/ApplyVariant + OnThemeApplied + RunJobs` 机制）。 <<MET>>
- [x] **AC4 对比度**：三套 mac pack × Light/Dark ×（正文/卡片/次要文字/导航选中）WCAG 2.x 相对亮度全部达标（正文 ≥4.5、次要 ≥3、导航 ≥4.5），`theme/contrast.json`。 <<MET>>
- [x] **AC5 字体许可**：仅系统字体栈 token（无商业/系统字体随包、无字体二进制），`AppStyles.axaml` 经 `DynamicResource AppFontFamily` 桥接。 <<MET>>
- [x] **AC6 回归**：干净 worktree 上 `scripts/test.ps1` **247/247 passed / 0 failed / 0 skipped**（≥241；coreclient 61 / host 56 / app 130，`dotnet build -warnaserror` 0 warning）；旧壳 vitest **60 files / 567 tests**；pytest **2773 passed / 10 skipped / 0 failed**（零 Python 改动）。 <<MET>>
- [x] **AC7 门禁**：`check.ps1 -TaskPath doc/tasks/THEME-MACOS-2.md` PASS；Canonical Evidence 27 行 64-hex SHA-256 pin（commit 列 `-`，pin 工作区字节）；`MANIFEST.json` 覆盖 294 个证据文件 + AC 映射；Handoff 含 Record Decision。 <<MET>>
- [x] **AC8 三套布局**：三套 mac 主题分别携带 `LayoutProfile`（Sonoma=标题栏中央导航/1400 居中网格/双栏设置；Launchpad=底部悬浮 Dock/168×220 大图标网格/900 单列设置；Split=左侧 220 Sidebar/260 书列表+右侧内容/左侧分区目录+右侧分区内容）；切换主题后 `MainWindow` 导航宿主（TitleBar/DockHost/SidebarHost）、`BookshelfPage.CurrentLayout`、`SettingsPage.CurrentLayout` 结构断言通过；旧 6 套 Layout 仍为 Sonoma（`LayoutProfiles.Sonoma` 值相等）+ sonoma 截图逐字节回归；布局切换 p95=20.151ms ≤100ms。 <<MET>>
- [x] **AC9 截图与证据**：12 张真实 headless-Skia 截图（3 套 × Light/Dark × 书架/设置）1280×820 保存于 `verification/THEME-MACOS-2/screenshots/`；`layout/profiles.json`、`layout/hot-switch.json`、`layout/screenshots.json`、`MANIFEST.json` 齐全（AppBg 采样比 0.09–0.73，三布局 pairwise 结构差异 45–115/160 格）。 <<MET>>

## 允许修改范围
`apps/desktop-avalonia/src/NewManga.Theme/**`、主题所需最小 `src/NewManga.App/**`、`tests/**` 主题测试、`verification/THEME-MACOS-2/**`、本卡/Handoff/STATUS/PLAN/LEDGER、workspace。

## 关键约束
- **必须**在自己的 `git worktree`（`task/THEME-MACOS-2`）里工作；**禁止**在主工作树直接编辑/提交
- 只 `git add` 自己的显式路径；禁止 reset/stash/删他人 worktree

## 禁止范围

不改 Python Core 语义/协议/Host 契约/旧壳、不 push、不 gc/prune；不得伪造结果；**禁止 `git add -A`（主工作树有其它会话改动）**。

## 实际测试与运行记录

- 日期/环境：2026-10-28（Asia/Shanghai），Windows 11，.NET SDK 9，Avalonia 11.3.22（headless + Skia），Python 3（pytest 全量），Node/npm（旧壳 frontend）。
- worktree：`G:/CODEX/New Manga.workspace/worktrees/THEME-MACOS-2`，branch `task/THEME-MACOS-2`，base `d2f66a19e`，被测 HEAD `84dd38978` + 本卡工作区未提交改动（实现/测试/证据/文档，由 Lead 统一提交）。
- 构建：`dotnet build apps/desktop-avalonia/NewManga.sln -c Debug -warnaserror` → 0 warning / 0 error。
- 主题/布局测试：`dotnet test tests/NewManga.App.Tests --filter "ThemeLayouts|ThemeMacos"` → **15/15 passed**（ThemeLayoutsTests 6 + ThemeMacosTests 9）。
- 全量：`pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1 -EvidenceDirectory <worktree>/verification/THEME-MACOS-2` → **247/247 passed, 0 failed, 0 skipped**。
- 旧壳：`cd apps/desktop/frontend; npx vitest run` → **60 files / 567 tests passed**。
- Python：`python -m pytest -q` → **2773 passed, 10 skipped, 0 failed**（205.64s）。
- 性能：`layout/hot-switch.json` 布局 p95=20.151ms / variant p95=14.155ms（各 36 样本，阈值 100ms）。
- 截图：12 张 1280×820 见 `screenshots/`；`layout/screenshots.json` 记录 bytes/AppBg 采样比/颜色数/16×10 结构指纹与 pairwise 差异。
- NOT_RUN：真机 Mica/Windows 11 人工视觉 smoke（headless 无 Mica；由 Lead/其他分支覆盖，不写作通过）。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| E01 | AC1/AC8 | verification/THEME-MACOS-2/layout/profiles.json | - | 948037dc3fa1477dbaa552d8fadd7868fabfe03b4c3ec45efc4bdc2f22ac1d07 | CANONICAL |
| E02 | AC1/AC8 | verification/THEME-MACOS-2/layout/switching.json | - | 800a947081c09d1fc02bb4093fb43ff0ff5df9a500cf98b63334f47c5ba50c46 | CANONICAL |
| E03 | AC3/AC8 | verification/THEME-MACOS-2/layout/hot-switch.json | - | d715bc6a33e783fc3529f8c0aef75098f02423c9682dd60a85201715e7e0b451 | CANONICAL |
| E04 | AC2/AC9 | verification/THEME-MACOS-2/layout/screenshots.json | - | 6a1a659217ae2f0b63d024cde2628d318cb952b3406512363e66e701d0cc5879 | CANONICAL |
| E05 | AC2/AC9 | verification/THEME-MACOS-2/screenshots/sonoma-bookshelf-light.png | - | 0bd028aed8bcfc548009e1469bfff4cafc25a564285deeb60b442eeb3ac8870e | CANONICAL |
| E06 | AC2/AC9 | verification/THEME-MACOS-2/screenshots/sonoma-bookshelf-dark.png | - | 5e866fee694f71734d933e917e3f8c544bb56a9829f48a18de6704ec95995843 | CANONICAL |
| E07 | AC2/AC9 | verification/THEME-MACOS-2/screenshots/sonoma-settings-light.png | - | b09ebef19673516020afdc295a704b0acd72197a6cf92fc44dc7c4bc41d9a617 | CANONICAL |
| E08 | AC2/AC9 | verification/THEME-MACOS-2/screenshots/sonoma-settings-dark.png | - | 8ac587a3e5ebf5b3adc5c9fc69a10b08d2d301c2b0e0622d42a6cc854d8102f1 | CANONICAL |
| E09 | AC2/AC9 | verification/THEME-MACOS-2/screenshots/launchpad-bookshelf-light.png | - | 42f3a7a71db2adcee6522b034694090475cd8316f6edc2f98bc96243630ae6cb | CANONICAL |
| E10 | AC2/AC9 | verification/THEME-MACOS-2/screenshots/launchpad-bookshelf-dark.png | - | b695e49193b28dc32cf6f232c9e6c5787c35799286d339d8405448845c53f114 | CANONICAL |
| E11 | AC2/AC9 | verification/THEME-MACOS-2/screenshots/launchpad-settings-light.png | - | 9302f7972c002e1d59a446a9e7a85b305b99ab073d92d27a0def3bdb86cfa98c | CANONICAL |
| E12 | AC2/AC9 | verification/THEME-MACOS-2/screenshots/launchpad-settings-dark.png | - | 8f5874b55d3bffaed851dd47e31a929df5a3d32b6c2121ee008b92457c14e1f4 | CANONICAL |
| E13 | AC2/AC9 | verification/THEME-MACOS-2/screenshots/split-bookshelf-light.png | - | e894dc68707a3b209e91b0d81bf2f5536dc3b39bdf0fb2131389229f1419b0f9 | CANONICAL |
| E14 | AC2/AC9 | verification/THEME-MACOS-2/screenshots/split-bookshelf-dark.png | - | 6d90e430d8f61e50d29d8def44fbf06f79a8066f1d7de919522492cac6f34bc1 | CANONICAL |
| E15 | AC2/AC9 | verification/THEME-MACOS-2/screenshots/split-settings-light.png | - | dc3530428513a6179ca795846d9f49cc5ddbc6cc2711769f8e5651d666c08209 | CANONICAL |
| E16 | AC2/AC9 | verification/THEME-MACOS-2/screenshots/split-settings-dark.png | - | cc3fe732e315a7e1e17d50622d759a047be33dc5aba7ddb3f8f9ae81312b81a9 | CANONICAL |
| E17 | AC6 | verification/THEME-MACOS-2/test/summary.json | - | a37bcfd209e34f06597073f6ae3189e87daf89cf8c10833c5d9710582c62d7df | CANONICAL |
| E18 | AC6 | verification/THEME-MACOS-2/test/dotnet-test-Debug.log | - | aa8dd0265f0bc8ec0a5ccd2e62415a0bb07060ce17790a94f984b8508ec11844 | CANONICAL |
| E19 | AC6 | verification/THEME-MACOS-2/test/results-app.trx | - | 4702e3d1b2cd991cb977de3754bd85f198b0d340b7ea8895e9d0f8a11d60d738 | CANONICAL |
| E20 | AC6 | verification/THEME-MACOS-2/test/results-host.trx | - | 71b1961124f134939abcf7aab383e8052d725efcabf9245160bd8989221d247d | CANONICAL |
| E21 | AC6 | verification/THEME-MACOS-2/test/results-coreclient.trx | - | 912d842f7d7d975c2930dde70e0f096e8c13573d879359e151074de8dff84e80 | CANONICAL |
| E22 | AC6 | verification/THEME-MACOS-2/test/vitest.log | - | a061a3be89d24c218150ef1e2f93bf2f801b3610df072f03ab7ed2f8ae2a2ccf | CANONICAL |
| E23 | AC6 | verification/THEME-MACOS-2/test/pytest.log | - | 2d736da9c5b9b97de1be124d94491e3aa37e3b344a7b8216059b82b1208bfadd | CANONICAL |
| E24 | AC2/AC4 | verification/THEME-MACOS-2/theme/pack.json | - | a8cc4dfeb4a6a950e78c3a208ba47423aecfb35f2ff8fcfe401258be789efa7b | CANONICAL |
| E25 | AC2/AC4 | verification/THEME-MACOS-2/theme/screenshots.json | - | b0a874965b544976f23b57a6109dd5c435cdbb78a445b66001f80efadb8b9f13 | CANONICAL |
| E26 | AC6 | verification/THEME-MACOS-2/build/dotnet-build-Debug.log | - | 84dc6c5bbf0e3bda76198cf4cd2aade1140ff271175595fa36b8a401b2e8bf87 | CANONICAL |
| E27 | AC7 | verification/THEME-MACOS-2/MANIFEST.json | - | 57f0461115f5667dbe4384b50a048c51e322a6986d3498fff8ace8b08ff62a9f | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/THEME-MACOS-2 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/THEME-MACOS-2 | verification/THEME-MACOS-2/MANIFEST.json | worktree 与主树 plan/ledger 引用中；关闭时由 DSH 复核 |
| worktree | G:/CODEX/New Manga.workspace/worktrees/THEME-MACOS-2 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/THEME-MACOS-2 | branch task/THEME-MACOS-2 | 交付载体，关闭前不得删除 |
| 字体二进制 | NOT_APPLICABLE | NOT_APPLICABLE | - | - | 无随包字体（系统字体栈 token） |
| 其他 | NOT_APPLICABLE | NOT_APPLICABLE | - | - | 无 dataset/model/artifact/temp/exchange 新增 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`（证据已生成并 pin，待 DSH 复核后 complete）。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写（本任务未删除/迁移/归档文件）。
- 未关闭项及保留原因：实现/测试/证据/文档为 worktree 工作区未提交改动，待 Lead 显式 add 并提交；delivery_head 待回填。
- 当前指针清理：待 Lead 集成时更新 STATUS / Plan / Task 导航 / rolling checkpoint。
