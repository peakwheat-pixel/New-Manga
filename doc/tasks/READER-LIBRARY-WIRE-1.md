---
id: READER-LIBRARY-WIRE-1
title: 阅读器接真实书库 + 沉浸窗口入口（Esc/H/F 可达）
kind: implementation
governance_version: 3
status: proposed
approval: user_authorized_2026-10-27_manual_verify_followups
suggested_owner: antigravity
owner: null
reviewer: dsh
depends_on: [BOOK-FIXTURE-1]
base_commit: null
branch: task/READER-LIBRARY-WIRE-1
worktree: G:/CODEX/New Manga.workspace/worktrees/READER-LIBRARY-WIRE-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/READER-LIBRARY-WIRE-1
allowed_paths:
  - doc/tasks/READER-LIBRARY-WIRE-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/READER-LIBRARY-WIRE-1/**
  - G:/CODEX/New Manga.workspace/task-envs/READER-LIBRARY-WIRE-1/**
---

# READER-LIBRARY-WIRE-1：阅读器接真实书库 + 沉浸入口

## 背景（BOOK-FIXTURE-1 发现的真实产品缺口）

- `MainWindow.axaml.cs:66-72`：「阅读器」页绑定 `ReaderFixtureLocator.TypographyPaths()` 的固定 fixture，**不接 `ListBooks` 的真实书**。
- `ReaderWindow`（沉浸窗：Esc 退出 / H 隐藏 HUD / F 切 fit，`Views/ReaderWorkbenchPages.cs:449-487`）全仓**无任何 `new ReaderWindow(...)` 调用** → Esc/H/F 当前**用户不可达**。
- 因此真机核验第 3 项（webtoon 工作集）与第 5 项（沉浸 Esc/H）无法在产品内完成。

## Acceptance Criteria

- [x] **AC1 书库接线**：阅读器页从 Core `ListBooks`/`list_chapters`/`GetReaderProjection`（经 Host/CoreClient）取真实 book/chapter/pages 渲染；空库时显示空态（保留现有提示）。→ **MET**：`CoreServiceClient` 新增三命令读面；`HostRuntime.ReadPageImageAsync` 走既有资源通道（Core resolve → host_bridge issue/resolve → TileChannel 摘要校验）；真机截图 02 显示真实书 8 页；空态 + `NEWMANGA_READER_SOURCE=fixtures` 回退有 headless 测试。
- [x] **AC2 沉浸入口**：从阅读器页可打开沉浸窗（如双击页面/按钮/快捷键），沉浸窗按 Esc 退出、H 隐藏 HUD、F 切换 fit、方向键翻页，**均有自动化测试**（Avalonia.Headless 可断言 Window 创建/关闭与状态）。→ **MET**：工具栏「沉浸模式 (Esc/H/F)」按钮 + 双击 → `ReaderWindow`；真机 03/04/05（全屏→H 隐藏 HUD→Esc 关闭）；`ReaderLibraryTests` 8 项覆盖创建/Show/Esc 关闭/H/F/方向键。
- [x] **AC3 真机验证**：用 BOOK-FIXTURE-1 的数据根打开书 → 进入沉浸 → Esc 退出、H 隐藏 UI 各一次，截图 + 日志证据。→ **MET**：数据根 book `14340dd…`；截图 01–05；`live-evidence.json` + `runtime-logs/{host.log,wire/*}`（host.log `data_root=` 命中隔离根）。
- [x] **AC4 webtoon**：真实 8 页（1200×1660 webtoon_vertical）可滚动阅读；测量进程工作集峰值（目标 ≤1.5GB）并记录。→ **MET**：8 页 webtoon_vertical 全量渲染并滚动（截图 06）；工作集峰值 **395.1 MB ≤1536 MB**（`working-set-samples.json`，83 样本/22s）。
- [x] **AC5 回归**：`scripts/test.ps1` 全绿；旧壳 vitest 60/567；pytest 基线 3F/2739P/9S 无新增失败；`check.ps1 -TaskPath` PASS；64-hex pin；Handoff。→ **MET**：test.ps1 **110/110**；vitest **60/60 文件、567/567 用例**；pytest **3F/2739P/9S（0 新增）**；check.ps1 PASS；pin 见下；Handoff `doc/handoffs/READER-LIBRARY-WIRE-1-handoff.md`。

## 允许修改范围

`apps/desktop-avalonia/**`、本卡、STATUS/PLAN/LEDGER、`verification/READER-LIBRARY-WIRE-1/**`、workspace。

## 禁止范围

不改协议/Host 契约、不改 Python Core、不改旧壳、不 push、不 gc/prune、不删除 fixture 回退路径（保留可切换）。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1/AC2 | `dotnet test`（App headless）+ 真机点开阅读器/沉浸 | BOOK-FIXTURE 数据根 + 新发布件 | **PASS**：110/110；真机书页渲染、沉浸创建、Esc/H 截图 | `dotnet-all.log`、`screens/01..06`、`live-evidence.json` |
| AC3/AC4 | 真机启动 → 阅读器（8 页长滚动）→ 沉浸 → H → Esc；滚动 + 工作集采样 | Win11 + FINAL-VALIDATION-1 侧车 | **PASS**：Esc 关闭（窗口 2→1）、H 隐 HUD、滚动到后续页；峰值 395.1MB ≤1.5GB | `screens/03..06`、`working-set-samples.json`、`runtime-logs/` |
| AC5 | test.ps1 / vitest / pytest / check.ps1 | 全量 | **PASS**：110/110、60/567、3F/2739P/9S、治理 PASS | `dotnet-all.log`、`vitest.log`、`pytest.log` |

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| E-RLW-REPORT | AC1–AC5 | `verification/READER-LIBRARY-WIRE-1/REPORT.md` | `cd4500dcc` | `f9ec6f1e9153ee6f1d9c14d1585be19ec53469c20c0fbfb6a8c3922462e04c30` | CANONICAL |
| E-RLW-LIVE | AC1–AC4 | `verification/READER-LIBRARY-WIRE-1/live-evidence.json` | `cd4500dcc` | `67207233be1903f6ed12b1918527f4b0c296f624199a8308419392bd5e330e7f` | CANONICAL |
| E-RLW-MEM | AC4 | `verification/READER-LIBRARY-WIRE-1/working-set-samples.json` | `cd4500dcc` | `5a1ffd1dcc7b32eb11b6d258a1004965e3bf3a0c0143609380321c80e969943c` | CANONICAL |
| E-RLW-IMMERSIVE | AC2/AC3 | `verification/READER-LIBRARY-WIRE-1/screens/03-immersive.png` | `cd4500dcc` | `4796aa735dfb5dd586872d319d75a6712685c6b6f6581b0f80ee8dc166248bcb` | CANONICAL |
| E-RLW-HUD | AC2/AC3 | `verification/READER-LIBRARY-WIRE-1/screens/04-hud-hidden.png` | `cd4500dcc` | `eb118ff09ccf20e9bfd5856206a3017de3e0bc6b41e56758fdc6a1fd8d25d806` | CANONICAL |
| E-RLW-SCROLL | AC4 | `verification/READER-LIBRARY-WIRE-1/screens/06-webtoon-scrolled.png` | `cd4500dcc` | `ebb960f97878d919d642e69a5ec675c532df2447f07c938217026bae24d893b4` | CANONICAL |
| E-RLW-HOSTLOG | AC3 | `verification/READER-LIBRARY-WIRE-1/runtime-logs/host.log` | `cd4500dcc` | `3dda317ece18348dc6cf25e747c329435882b6d8d241ab9225cae019291e9777` | CANONICAL |
| E-RLW-DOTNET | AC5 | `verification/READER-LIBRARY-WIRE-1/dotnet-all.log` | `cd4500dcc` | `2827697e00d7ba920f4c655e81480abe38623a039560c1b5142359c15bf4cab3` | CANONICAL |
| E-RLW-VITEST | AC5 | `verification/READER-LIBRARY-WIRE-1/vitest.log` | `cd4500dcc` | `abfdebd690ce26f6d5a08f09810b62e741092913a4e0af059aa58ddcc903f3ad` | CANONICAL |
| E-RLW-PYTEST | AC5 | `verification/READER-LIBRARY-WIRE-1/pytest.log` | `cd4500dcc` | `cb26b43bb5e9e367c78ba990c52aa440c9ed88ed491f33c35a0125ffd66464af` | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/READER-LIBRARY-WIRE-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/READER-LIBRARY-WIRE-1 | `pkg/app/`（Release single-file + core-sidecar，本次真机发布件） | 真机证据引用；关闭时按裁决保留/清理 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
