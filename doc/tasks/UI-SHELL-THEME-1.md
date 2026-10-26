---
id: UI-SHELL-THEME-1
title: S3 主窗 + 主题中心 + 书架（Saber 参考）+ 设置骨架
kind: implementation
governance_version: 3
status: in_review
approval: user_authorized_2026-10-26_ad002_autonomy
suggested_owner: zcode
owner: avalonia-spike
reviewer: dsh
depends_on: [HOST-CORECLIENT-1]
base_commit: 5a11fa7d9
branch: task/UI-SHELL-THEME-1
worktree: G:/CODEX/New Manga.workspace/worktrees/UI-SHELL-THEME-1
integration_commit: null
delivery_head: 28cd1324ca835a90694393ed95749407836da544
canonical_evidence_status: pinned
resource_closeout_status: pending
evidence_dir: verification/UI-SHELL-THEME-1
allowed_paths:
  - doc/tasks/UI-SHELL-THEME-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/UI-SHELL-THEME-1/**
  - G:/CODEX/New Manga.workspace/task-envs/UI-SHELL-THEME-1/**
  - G:/CODEX/New Manga.workspace/worktrees/UI-SHELL-THEME-1/**
---

# UI-SHELL-THEME-1：S3 主窗 + 主题中心 + 书架 + 设置骨架

## 来源与目标

AD-002 §3/§4、`ui-spec/SABER_UI_SPEC.md` + `tokens-saber-purple.json`（已交付）、ADR-0001（布局/共存）、S1/S2 已完成。目标：新壳具备可用的四页骨架，主题中心可运行时热切换，书架按 Saber **参考规格**（非 1:1）实现，并为 S4 工作台/阅读器留出插槽。

## Acceptance Criteria

- [x] **AC1 主窗与导航**：沉浸式标题栏（Win11 Mica / Win10 回退不透明）、四页导航壳（书架/工作台/阅读器/设置）、单实例、启动不阻塞（不等待 Core 完成首帧）、无控制台。 <<MET>>
- [x] **AC2 主题中心**：ThemePack = `manifest.json + tokens.json + controlthemes.xaml + materials.json + motion.json + icons/`；内置 ≥6 套（含 Saber Purple 默认 + light/dark）；**3 套热切 P95 ≤100ms**、不重启、截图差分无色残留、reduced-motion 归零。 <<MET>>
- [x] **AC3 书架页**（Saber 参考）：紫渐变顶栏、1400 居中、标题+三动作、白卡搜索+标签 chip、封面 3:4 书卡网格（列数在 VM 计算，Avalonia 无 auto-fill）、hover「查看详情」、详情/新建入口、空态/无结果态。 <<MET>>
- [x] **AC4 设置骨架**：分区导航 + 已接线 settings 命令的展示/编辑；S2 的 50 条 NS 中「书架/设置所需」子集逐批接线（列出清单与完成数）。 <<MET>>
- [x] **AC5 质量门禁**：`scripts/test.ps1` 全绿（含 UI headless 测试）；旧壳 `npx vitest run` 仍 60/60 文件 567/567；换肤/导航/书卡交互有测试；无控制台；键盘焦点可达；`check.ps1 -TaskPath` PASS；证据 pin 64-hex。 <<MET>>
- [x] **AC6 交接**：Handoff `doc/handoffs/UI-SHELL-THEME-1-handoff.md`；Record Decision（主题服务设计、NS 接线批次、字体策略=仅系统栈）。 <<MET>>

## 允许修改范围

`apps/desktop-avalonia/**`、本卡、STATUS/PLAN/LEDGER 指针、`verification/UI-SHELL-THEME-1/**`、workspace。只读：`ui-spec/**`、`doc/AD-002*`、`doc/design/ADR-*`、`doc/design/EXECUTION_DIRECTIVE_AD002_V2.md`。

## 禁止范围

不改旧壳 `apps/desktop/**`、不改 Python Core、不改 AD/ADR、不 push、不 1:1 复刻 Saber 截图、不随包商业/系统字体（仅系统字体栈）、不 gc/prune。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | headless 启动不阻塞 + WindowMaterial 判据 + 四页导航/键盘焦点 | .NET9/Avalonia 11.3.22 | PASS：首帧早于 Host ready；Win11→Mica / Win10→不透明回退；4 按钮可聚焦切换 | E6/E7 |
| AC2 | 6 packs 结构断言 + 3 套×10 次热切 + reduced-motion | 同上 | PASS：**p95 2.215ms**（≤100ms，spike 3.74ms 为基准）；ThemeDictionaries Light/Dark；无色残留；reduced-motion 全 0 | E1 |
| AC3/AC4 | headless UI + 真 sidecar 命令（经 dispatcher） | 无标签 sidecar 副本 | PASS：列数 VM 计算(1400→7)、搜索/标签/空态/无结果/详情/新建；接线 13 已实现命令 + 8 条 NS 批次登记(S3-A/B/C) | E2/E3/E4/E5 |
| AC5/AC6 | `scripts/test.ps1 -CanonicalEvidence`；`npx vitest run`；`check.ps1 -TaskPath` | 全量 | PASS：dotnet **74/74**、裸跑 58 passed/16 skipped、vitest 60/567；check PASS；证据 pin 64-hex | E3/E8–E11 |
## 依赖、风险与阻塞

- 依赖：HOST-CORECLIENT-1（done）；S2 的 NS 清单（Handoff 已列）。
- 风险 1：主题热切与 Mica 合成冲突（spike 已验证可行，需回归）；风险 2：书卡网格列数计算与 DPI；风险 3：NS 命令接线遗漏导致页面空态误判。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| E1-theme-hot-switch | AC2 | verification/UI-SHELL-THEME-1/theme/hot-switch.json | 28cd1324ca835a90694393ed95749407836da544 | 399baf37b7744df5ff0595289516e4c15ac74546d78994f658b25726dcad0f55 | CANONICAL |
| E2-wiring | AC4 | verification/UI-SHELL-THEME-1/commands/wiring.json | 28cd1324ca835a90694393ed95749407836da544 | 1b5a31590d0c993533d4912df6587689b15ed658631ce70e39badeae4f1bc1d8 | CANONICAL |
| E3-test-log | AC5 | verification/UI-SHELL-THEME-1/test/dotnet-test-Debug.log | 28cd1324ca835a90694393ed95749407836da544 | 202bcd9dd6db35748ad7c428ed1f546a145e5e1e7151cc3a33f86c17b67d61f3 | CANONICAL |
| E4-test-summary | AC5 | verification/UI-SHELL-THEME-1/test/summary.json | 28cd1324ca835a90694393ed95749407836da544 | 4cf9f2ccd95afcef4f28c363e5e668b01ec9e68e09736f381eb306a2cc9832d5 | CANONICAL |
| E5-trx-app | AC1/AC2/AC3/AC4 | verification/UI-SHELL-THEME-1/test/results-app.trx | 28cd1324ca835a90694393ed95749407836da544 | 9ab7cd9f200bd9502e09d1364737fa095491bf40da0995367f24d809b5f54d6c | CANONICAL |
| E6-trx-core | AC3/AC4 | verification/UI-SHELL-THEME-1/test/results-coreclient.trx | 28cd1324ca835a90694393ed95749407836da544 | bbfb1fb1055747e750b239645a9e8be4b71f4c74754fc88bc1e09aef90f05b10 | CANONICAL |
| E7-trx-host | AC1 | verification/UI-SHELL-THEME-1/test/results-host.trx | 28cd1324ca835a90694393ed95749407836da544 | bdea4b9dbf39067e28fcb8513b8eef9cb4328074809fdfee2a8e34e3a71286b7 | CANONICAL |
| E8-build | AC5 | verification/UI-SHELL-THEME-1/build/dotnet-build-Debug.log | 28cd1324ca835a90694393ed95749407836da544 | 5a362c057b3c62a65cebf610272722e8adb5a353d321fa6d887f7ad51b1c4a59 | CANONICAL |
| E9-vitest | AC5 | verification/UI-SHELL-THEME-1/test/vitest-baseline.log | 28cd1324ca835a90694393ed95749407836da544 | 9ebf78cd82d7d3b45a7e9a5472c0841d050ae4f3e5ced4857247a4adecce1360 | CANONICAL |
| E10-probe | AC3/AC4 | verification/UI-SHELL-THEME-1/parity/core-command-probe.json | 28cd1324ca835a90694393ed95749407836da544 | 5557e3cf987f7dee80ffa26a4a6ec2c9576102c2e00ae9fc786ff437cd9970c0 | CANONICAL |
| E11-manifest | 全 AC | verification/UI-SHELL-THEME-1/MANIFEST.json | 28cd1324ca835a90694393ed95749407836da544 | 1d622ac6d000d10b8155d11cffeaeda497793cc5f1d6443c2434bc152e13654b | CANONICAL |
## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/UI-SHELL-THEME-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/UI-SHELL-THEME-1 | 1d622ac6d000d10b8155d11cffeaeda497793cc5f1d6443c2434bc152e13654b | 待关闭时核 |

## Closeout Record

- Closeout date / DSH：待 DSH 复核后填写（in_review）。
- canonical_evidence_status：`pinned`（E1–E11，commit 28cd1324ca）。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：已更新 STATUS/PLAN/LEDGER。
