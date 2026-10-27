---
id: THEME-MACOS-2
title: macOS 风主题重做（独立分支）
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-28_goal_all_authorized
suggested_owner: saber-ui-spec
owner: saber-ui-spec
reviewer: dsh
depends_on: []
base_commit: f1b89c5e5
branch: task/THEME-MACOS-2-saber
worktree: G:/CODEX/New Manga.workspace/worktrees/THEME-MACOS-2-saber
integration_commit: null
delivery_head: bfaec8f54fb7d817959b04d8f97c1f954a2d0465
canonical_evidence_status: complete
resource_closeout_status: pending
evidence_dir: verification/THEME-MACOS-2
allowed_paths:
  - doc/tasks/THEME-MACOS-2.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/src/NewManga.Theme/**; apps/desktop-avalonia/src/NewManga.App/**; apps/desktop-avalonia/tests/**
  - verification/THEME-MACOS-2/**
  - G:/CODEX/New Manga.workspace/task-envs/THEME-MACOS-2/**
  - G:/CODEX/New Manga.workspace/worktrees/THEME-MACOS-2-saber/**
---

# THEME-MACOS-2：macOS 风主题重做

> 交付状态：**ready-for-integration**（实现/证据 `bfaec8f54` + Handoff 已完成；待 DSH 复核/集成；Owner 不自审）。
> **base**：任务卡原记 `d2f66a19e`/指令 `84dd38978`；Lead 依据 main `4be1c3f4f` 构建修复态裁决使用 **`f1b89c5e5`**，并在独立 worktree `THEME-MACOS-2-saber` 继续（Lead 指定的 `THEME-MACOS-2` 目录被外部会话并发写入，未由我触碰）。
> **范围**：核验后主线已有 `macos-sonoma`（7 packs、默认 `saber-purple`、Light/Dark 双 token 齐全）→ 按 Lead 指示**不新增 pack/id**；本任务为「验证 + 补齐 + 出证据」。

## Acceptance Criteria

- [x] **AC1 主题可见可切换**：`macos-sonoma`（「macOS 风」）在设置页主题列表；`ThemePacks.Default` 仍 `saber-purple`；既有主题不回归。→ **MET**：7 packs、macOS 单行中文、default 不变、6 个 legacy pack 的 token/字体/单 token 集不变；交通灯仅视觉（装饰/缩放/客户区不变，审计测试）。证据：`headless/theme/pack.json`、`headless/theme/traffic-lights-visual-only.json`。
- [x] **AC2 Light/Dark 渲染**：同一 pack 内嵌两套 token；真机截图 4 张（书架/设置 × Light/Dark）。→ **MET**：Light/Dark token+material 全部映射且与冻结规格一致；4 张真机截图（AppBg 像素采样 `#F5F5F7` / `#1E1E1E`）+ 4 张 headless-Skia 补充。证据：`real-app-*.png`、`real-app-screenshots-metadata.json`、`headless/screenshots/`。
- [x] **AC3 热切换**：p95 ≤100ms（给数字）。→ **MET**：48 次真实切换，**p95 = 10.456 ms**（max 15.830 / min 4.358）。证据：`headless/theme/hot-switch-macos.json`。
- [x] **AC4 对比度**：正文 ≥4.5:1、次要 ≥3:1（给计算）。→ **MET**：Light 正文 15.457/16.830、Dark 正文 15.311/12.800；次要 Light 4.658/5.071、Dark 5.806/4.853；nav-active 8.521/9.290。证据：`headless/theme/contrast.json`。
- [x] **AC5 字体许可**：仅 OFL 等兼容，不随包商业/系统字体。→ **MET**：0 个字体二进制；栈仅系统族 + Inter（SIL OFL 1.1，未随包）+ sans-serif。证据：`headless/theme/font-audit.json`。
- [x] **AC6 回归**：干净 worktree test.ps1 全绿（≥241）；vitest 60/567；pytest 无新增失败。→ **MET**：test.ps1 **243/243**（61/56/126，0 skipped）；vitest **60/567**；pytest **0F/2773P/10S**。
- [x] **AC7 门禁**：check.ps1 -TaskPath PASS；64-hex pin；Handoff + Record Decision。→ **MET**：check PASS；25 条 pin；Handoff 含 Record Decision。

## Record Decision（摘要，完整版在 Handoff / REPORT）

| 项 | 决定 |
|---|---|
| base | `f1b89c5e5`（main，含 Lead `4be1c3f4f` 构建修复）；Lead 裁决接受 |
| 冲突 worktree | 未 reset/删/提交；改为独立 `THEME-MACOS-2-saber`；冲突目录留 Lead 处置 |
| 实现范围 | **不新增 pack/id**；验证 + 补齐证据；`ThemePack.cs` 未改 |
| 测试 | 从 `4ea86e03a` 恢复 `ThemeMacosTests`（9 项）；新增 `ThemeMacosAuditTests`（2 项：字体许可、交通灯仅视觉） |
| 真机证据 | 新增 `--theme/--variant/--page` 启动证据选项（缺省不变）+ 构造前应用变体，得到确定性 Light/Dark 真机 4 图 |
| pytest | 0F/2773P/10S（base 已含 flaky 修复） |

## 实现摘要（相对 `f1b89c5e5`）

- `tests/NewManga.App.Tests/ThemeMacosTests.cs`：恢复自 `4ea86e03a` 的 9 项主题测试（注册/默认、Light+Dark token 逐项、对比度、热切换 p95、外观切换、reduced motion、字体栈/交通灯、headless 截图、legacy 回归）。
- `tests/NewManga.App.Tests/ThemeMacosAuditTests.cs`（新）：字体许可审计 + 交通灯仅视觉审计。
- `src/NewManga.App/AppOptions.cs` / `App.axaml.cs`：`--theme` / `--variant` / `--page` 证据启动选项；构造 shell 前应用 pack/变体（缺省行为不变）。
- `verification/THEME-MACOS-2/**`：真机 4 图 + 元数据 + headless 证据 + 测试日志 + REPORT。

## Canonical Evidence（25 条）

| evidence_id | AC/Gate | path | sha256 |
|---|---|---|---|
| TM2-REAL-BOOKSHELF-LIGHT | AC2 | verification/THEME-MACOS-2/real-app-bookshelf-light.png | 2602a93e9e9871ff984e9e774f3f39cf997091f174b97bf24ae70346bae449f3 |
| TM2-REAL-BOOKSHELF-DARK | AC2 | verification/THEME-MACOS-2/real-app-bookshelf-dark.png | 4ba22fc8b849010378722860908bc682380f9b0e7395de79dbce3675f03e598d |
| TM2-REAL-SETTINGS-LIGHT | AC2 | verification/THEME-MACOS-2/real-app-settings-light.png | 0871fa07d999711879eabbe07ab2cf199b477d1ff4703198005951769eabea84 |
| TM2-REAL-SETTINGS-DARK | AC2 | verification/THEME-MACOS-2/real-app-settings-dark.png | 217e3e227e8c545494292153673e48abe91118c896af81af7699fdb5a35e6f86 |
| TM2-REAL-META | AC2 | verification/THEME-MACOS-2/real-app-screenshots-metadata.json | f548539a0f0b44e3e62ef84f959a3ad89178aace693b5f28caed4d0a5ccbee91 |
| TM2-PACK | AC1/AC2 | verification/THEME-MACOS-2/headless/theme/pack.json | 830ea52a9cc5c920889c4566928bce0576a9379e9aa33d9b33533cd8482e2c13 |
| TM2-CONTRAST | AC4 | verification/THEME-MACOS-2/headless/theme/contrast.json | 314567fa26f9152704973455f6c51d9d9d689350979389449235e4cbe828d110 |
| TM2-HOTSWITCH | AC3 | verification/THEME-MACOS-2/headless/theme/hot-switch-macos.json | b8ef6a1f80db7e51cc833e90804cf14e0e14bc996f88c891baef2b910dda0260 |
| TM2-FONT-AUDIT | AC5 | verification/THEME-MACOS-2/headless/theme/font-audit.json | 220f4930e68e47dfc12fa44f3e3c3165d0ec702720c1cf8e84de7968d6b7413d |
| TM2-TRAFFIC-LIGHTS | AC1 | verification/THEME-MACOS-2/headless/theme/traffic-lights-visual-only.json | ca2ab6d9ffc198e82e3af889454ba8d38ef17535370f3371dec0159086e50713 |
| TM2-HEADLESS-SHOTS-META | AC2 | verification/THEME-MACOS-2/headless/theme/screenshots.json | dd8fdfa7ace27a3d35d34c33838d07872fa6a2bd9d40a0418590d6d59fd102d7 |
| TM2-HEADLESS-BOOKSHELF-LIGHT | AC2 | verification/THEME-MACOS-2/headless/screenshots/bookshelf-light.png | 0bd028aed8bcfc548009e1469bfff4cafc25a564285deeb60b442eeb3ac8870e |
| TM2-HEADLESS-BOOKSHELF-DARK | AC2 | verification/THEME-MACOS-2/headless/screenshots/bookshelf-dark.png | 5e866fee694f71734d933e917e3f8c544bb56a9829f48a18de6704ec95995843 |
| TM2-HEADLESS-SETTINGS-LIGHT | AC2 | verification/THEME-MACOS-2/headless/screenshots/settings-light.png | 92b2e8e6ab35e2b949230242e3f839c12b26a407af7ea15fd9e22a50d580a081 |
| TM2-HEADLESS-SETTINGS-DARK | AC2 | verification/THEME-MACOS-2/headless/screenshots/settings-dark.png | 4474de4b1e35f0088c8e15c8e4fbe5155e098b585e6c4f89012697f6accb60c0 |
| TM2-TEST-SUMMARY | AC6 | verification/THEME-MACOS-2/test/summary.json | 701b99795df32dc03136f5ff4be0b55556c58f19c85e2d834dfa9bdcfc57bb00 |
| TM2-TEST-LOG | AC6 | verification/THEME-MACOS-2/test/dotnet-test-Debug.log | fa3f2e4ae89bebc0908236faadcfaa62b47e8de52a8b578ba51ed71cd1d38dea |
| TM2-TEST-PS1-LOG | AC6 | verification/THEME-MACOS-2/test/test.ps1-final.log | f393f0bdf417b0cdb06955be2252b40c3b35aa7d33107234dbd9b2cffee842cb |
| TM2-TRX-APP | AC6 | verification/THEME-MACOS-2/test/results-app.trx | b7f1285ad21340fd3e7ec3f2120c96a9fc7a87e776f9904e8053b7f894912f88 |
| TM2-TRX-CORECLIENT | AC6 | verification/THEME-MACOS-2/test/results-coreclient.trx | 1c69125e08d7a31366de1df63e1f6d73da5684eb98b0c7ab25fd397b851fc868 |
| TM2-TRX-HOST | AC6 | verification/THEME-MACOS-2/test/results-host.trx | a244f158667837f09240976c34ab8b9d062750fa19fca3ae690d5ed9d9153192 |
| TM2-VITEST | AC6 | verification/THEME-MACOS-2/test/vitest.log | 22dfebfa395436842899f84fccba76da70cc79e7c0db9a6d575a41432e1798a4 |
| TM2-PYTEST | AC6 | verification/THEME-MACOS-2/test/pytest.log | 2bd17e72613c1f06fa95b64eb790006afdf0e45b69bfe7e02e515d5b71b0ba0f |
| TM2-HOTSWITCH-LEGACY | AC3 | verification/THEME-MACOS-2/headless/theme/hot-switch.json | 8cd1e65c6bd3524ae14be818d0cfc4951737563ca3743c945fe84cf66c22dcd3 |
| TM2-REPORT | AC7 | verification/THEME-MACOS-2/REPORT.md | 41573336878999cb42a52c06738ba90dcab1670638002b38685b4a147422604b |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/THEME-MACOS-2 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/THEME-MACOS-2 | `evidence-saber/`（测试/截图证据）+ `real-app-data-root/`（隔离数据根）+ `app-logs-shot*` | 2026-10-28 收口时存在；JSON/pins 引用其路径；未移动/未删除；关闭时由 DSH 复核 |
| conflict worktree | G:/CODEX/New Manga.workspace/worktrees/THEME-MACOS-2 | PRESERVE_QUARANTINED | （不由本任务处置） | 外部会话 WIP | 未触碰/未清理；由 Lead 决定归档或删除 |

## Closeout Record

- Closeout date / DSH：待关闭时填写（owner 交付 `bfaec8f54`，待 DSH 复核/集成/独立 Review）。
- canonical_evidence_status：`complete`（25 条 CANONICAL pin，指向 delivery_head）。
- resource_closeout_status：`pending`（task-env 保留引用；冲突 worktree 隔离待 Lead 处置）。
- 删除、迁移、归档数量/字节数：0（本任务未删除任何文件；真实 `%APPDATA%` 未写）。
- 未关闭项：冲突 worktree 处置；launchpad/split 布局不在本卡范围；主题测试源出外部会话但已由我逐项跑通；截图启动证据 hook 可在合入时移除；需独立 Review。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
