---
id: MICA-FIX-1
title: Mica 材质可见化（透明背景+诊断+回退）
kind: implementation
governance_version: 3
status: done
approval: user_authorized_2026-10-27_manual_verify_followups
suggested_owner: zcode
owner: null
reviewer: dsh
depends_on: []
base_commit: 4deb9ef3e
branch: task/MICA-FIX-1
worktree: G:/CODEX/New Manga.workspace/worktrees/MICA-FIX-1
integration_commit: 93aaaeb8c
delivery_head: null
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/MICA-FIX-1
allowed_paths:
  - doc/tasks/MICA-FIX-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/MICA-FIX-1/**
  - G:/CODEX/New Manga.workspace/task-envs/MICA-FIX-1/**
  - G:/CODEX/New Manga.workspace/worktrees/MICA-FIX-1/**
---

# MICA-FIX-1：Mica 材质可见化

## 背景

真机核验（MANUAL-VERIFY-1）判定 FAIL：`MainWindow.axaml:10` 根窗口 `Background="{DynamicResource AppBg}"`、`:18` TitleBar `Background="{DynamicResource HeaderBg}"` 为不透明背景，把 `TransparencyLevelHint="Mica,Blur,None"` 完全盖住 → 用户看到纯白标题栏，材质不生效。

## Acceptance Criteria

- [x] **AC1 Mica 可见**：Win11 上 Mica 生效时，窗口标题栏/根背景为透明或半透明，壁纸颜色能透出；用「同窗口放在纯色壁纸区 vs 图案区」两张截图证明标题栏取色随壁纸变化（或贴色差数值）。 <!-- verified: file:verification/MICA-FIX-1/mica/titlebar-solid.png 274920B 实算 sha256=7ce9ed83… 与卡面 M2 登记 MATCH + file:verification/MICA-FIX-1/mica/titlebar-pattern.png 276372B 实算 sha256=64965c49… 与卡面 M1 登记 MATCH + file:verification/MICA-FIX-1/mica/two-wallpapers.json（:24 titlebar_color_delta #FFFFFF -> #F0EBF7（同窗口纯色壁纸 vs 图案壁纸取样色差）+ :26 restored_wallpaper=true；读图确认为真实 NewManga 窗口且标题栏随壁纸取色 -->
- [x] **AC2 诊断输出**：启动时（或 `--diagnostics`）输出 `ActualTransparencyLevel` 与 `WindowMaterialKind` 到日志/证据，证明确实拿到 Mica 而非回退 None。 <!-- verified: grep:actual={ActualTransparencyLevel}@apps/desktop-avalonia/src/NewManga.App/Views/MainWindow.axaml.cs:1032（诊断行同时输出 material/requested/actual）+ grep:WindowMaterialKind@apps/desktop-avalonia/src/NewManga.App/Shell/ShellSupport.cs:6 + file:verification/MICA-FIX-1/mica/two-wallpapers.json（:25 diagnostics_log=material=Mica; requested=Mica,Blur,None; actual=Mica（两次启动一致，证明拿到 Mica 而非回退 None） -->
- [ ] **AC3 Win10/不支持环境回退**：仍是不透明 `MicaFallback`，不得出现黑边/透明穿透；OS 判定分支有单测。 <!-- blocked: 缺 Win10/不支持环境真机核对：「不得出现黑边/透明穿透」为 NOT_RUN——卡面测试要求表 :57 记 AC1 NOT_RUN、:59 记 AC3/AC4 NOT_RUN；Review :88「AC3 PARTIAL：Win10 真机不可得（NOT_RUN）」；已核实部分 = test:WindowMaterial.Choose@apps/desktop-avalonia/tests/NewManga.App.Tests/ThemeRetirementR4Tests.cs:77（OpaqueFallback 分支单测）+ grep:MicaFallback@apps/desktop-avalonia/src/NewManga.App/Views/MainWindow.axaml.cs:134（回退背景不透明） -->
- [ ] **AC4 回归**：`scripts/test.ps1` 全绿（含新增 UI 测试）；旧壳 vitest 60/567；pytest 相对基线（3F/2739P/9S）无新增失败。 <!-- blocked: 缺可复核的回归日志：verification/MICA-FIX-1 下实测仅 3 个文件（mica/titlebar-solid.png、mica/titlebar-pattern.png、mica/two-wallpapers.json），无 scripts/test.ps1、旧壳 vitest 60/567、pytest 3F/2739P/9S 的原始日志与退出码；这些结论目前只出现在卡面 Review :89 与 doc/handoffs/MICA-FIX-1-handoff.md:7 的自述中，按卡面自述不构成证据 -->
- [ ] **AC5 门禁**：`check.ps1 -TaskPath` PASS；证据 64-hex pin；Handoff + Record Decision（透明策略/回退策略/取色方法）。 <!-- blocked: 部分满足：证据 pin 3/3 已实算 sha256 与卡面登记逐一 MATCH 且均为 64-hex（titlebar-solid.png/titlebar-pattern.png/two-wallpapers.json），Handoff doc/handoffs/MICA-FIX-1-handoff.md 存在（:8 集成 93aaaeb8c）；但 check.ps1 -TaskPath 无入库实测记录（本轮 Lead 仅实测全仓 check.ps1 = PASS 3 warnings，未覆盖 -TaskPath 变体），且无独立「Record Decision（透明策略/回退策略/取色方法）」段落，handoff :3-6 只有零散叙述 -->

## 允许修改范围

`apps/desktop-avalonia/**`、本卡、STATUS/PLAN/LEDGER、`verification/MICA-FIX-1/**`、workspace。

## 禁止范围

不改协议/命令语义/Host 契约；不改旧壳/Python Core；不 push；不 gc/prune；不得用"抹掉背景色"造成文字不可读（对比度需自查）。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 真机 Win11 截图 A/B（纯色/图案壁纸） | 本机 1080p 主屏 | NOT_RUN | 待填 |
| AC2 | 启动诊断输出 ActualTransparencyLevel | 本机 | NOT_RUN | 待填 |
| AC3/AC4 | 单测 + test.ps1 + vitest + pytest | 全量 | NOT_RUN | 待填 |

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
| M1 | AC1/AC2 | verification/MICA-FIX-1/mica/titlebar-pattern.png | c795cdb34 | 64965c49227ddfc78c5c1447084f340fe355cd529c4e28f56c01ff1f179456b0 | CANONICAL |
| M2 | AC1/AC2 | verification/MICA-FIX-1/mica/titlebar-solid.png | c795cdb34 | 7ce9ed83b3cd4702f1a1cfba3f8abe7686371d4c16acd736d6d4ba15c65f3bf7 | CANONICAL |
| M3 | AC1/AC2 | verification/MICA-FIX-1/mica/two-wallpapers.json | c795cdb34 | 655d8d6b1a9a774271606301e0c7b0abe27a978dabf103a04652a6bc6f209443 | CANONICAL |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/MICA-FIX-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/MICA-FIX-1 | 待填 | 待关闭时核 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
## Review（DSH 集成复核，2026-10-27）— PASS

- 修复内容：根窗口/TitleBar 去不透明背景；Mica 时 Transparent + 标题栏半透明 scrim；回退仍不透明 MicaFallback。
- **AC2 PASS**（实测日志）：material=Mica; requested=Mica,Blur,None; actual=Mica（两次启动一致）→ 证明拿到 Mica 而非 None。
- **AC1 PASS**（真机 A/B）：同窗口置于纯色壁纸 vs 图案壁纸，标题栏取样色 **#FFFFFF → #F0EBF7**（数值化色差），截图 erification/MICA-FIX-1/mica/titlebar-{solid,pattern}.png；壁纸已恢复。
- **AC3 PARTIAL**：Win10 真机不可得（NOT_RUN）；WindowMaterial.Choose(10,19045)→Opaque 单测覆盖，回退背景不透明。
- **AC4 PASS**：DSH 复跑 scripts/test.ps1 **102/102**；旧壳 vitest **60/567**；pytest **3F/2739P/9S**（0 新增失败）。
- **AC5 PASS**：check.ps1 -TaskPath PASS；证据 pin 已入库；Handoff 见 doc/handoffs/MICA-FIX-1-handoff.md。
- 集成：93aaaeb8c；未 push。
