---
id: M2-SETTINGS-UI-SFX-POLICY
title: "React 设置页接入 sfx.policy 配置（SFX-ENTRY 后续；UI 协议说明：最小键接入，视觉审查可后补 Qoder）"
kind: feature
status: ready
approval: user_ruling_2026-10-01_three_followups_all
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权+自治授权）
depends_on: [M2-SFX-TRANSLATE-ENTRY]
base_commit: f534c3e7
branch: agent/zcode/M2-SETTINGS-UI-SFX-POLICY
worktree: G:/CODEX/New Manga.worktrees/M2-SETTINGS-UI-SFX-POLICY-zcode
---

# M2-SETTINGS-UI-SFX-POLICY：设置页 SFX 策略键接入

## 背景（M2-SFX-TRANSLATE-ENTRY 后续候选）

`settings["sfx"]["policy"]`（skip/translate/manual，默认 skip）已生产可用（M2-SFX-TRANSLATE-ENTRY），但无 UI 写入面——当前只能脚本 `save_settings_section("sfx", ...)` 写入。本 Task 在既有设置页接入该键。

**UI 协议说明**：协作协议新架构 UI/UX 主责=Qoder；本 Task 定位为**既有设置页的最小键接入**（无新视觉/交互设计——复用既有控件模式），Owner=ZCode 实施；如需视觉/交互升级可后续另派 Qoder 审查。

## 交付（AC）

1. **AC1 IPC 通道勘察**：设置页现有设置读写如何走 Tauri IPC（通用 settings get/update 命令？还是逐键命令？）——若已有通用通道直接复用（零契约变更）；若需新命令=**触冻结契约，即停登记移交集成方**（handoff BLOCKED_ON_CONTRACT）。
2. **AC2 UI**：设置页适当分区（翻译/检测相关组）加 SFX 策略选择控件（三值 select/radio，默认 skip 显示当前生效值）；保存走既有保存流；生效语义提示（"保存后下次重新打开手稿生效/对新建 region 生效"——按 SFX-ENTRY r1 R1 登记的作用域如实提示）。
3. **AC3 测试**：前端组件测试（vitest——渲染/三值切换/保存调用参数）；IPC 通道若扩展则 Rust/TS 侧对齐测试；Python 侧零改动预期（键已可用）。
4. **AC4 文档**：Task/Handoff 回填；UI 截图或组件快照登记。

## 允许修改面

`apps/desktop/frontend/src/**`（设置页+组件）、`apps/desktop/frontend/tests/**` 或既有测试位、`src-tauri/**`（仅当勘察证明既有通道不可复用且**不触冻结契约**——否则停）、`verification/M2-SETTINGS-UI-SFX-POLICY/**`、Task/Handoff。

## 禁改面

`doc/contracts/**`（触契约即停登记）、`src/**`（Python 侧零改动预期）、`src-tauri` 的既有命令语义、`packaging/**`、`doc/STATUS.md`。

## 纪律

- 基线不回退：vitest 既有全绿+cargo 零需求（若未动 Rust）；main 530+1skipped 0 failed。
- 设计语言跟随既有设置页（不发明新控件风格）；保存失败/非法值的前端处理跟随既有模式。
