---
id: M2-SETTINGS-IPC-CHANNEL
title: "settings IPC 通道（settings_get/settings_update_section）：M2-C1 契约 rev + Rust 命令 + 前端接通（用户裁决①，SFX-UI 解除前提）"
kind: feature
status: ready
approval: user_ruling_2026-10-02_three_confirmations
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权+自治授权）
depends_on: [M2-SETTINGS-UI-SFX-POLICY, M2-C1]
base_commit: f99a6c55
branch: agent/zcode/M2-SETTINGS-IPC-CHANNEL
worktree: G:/CODEX/New Manga.worktrees/M2-SETTINGS-IPC-CHANNEL-zcode
---

# M2-SETTINGS-IPC-CHANNEL：settings 读写 IPC 通道

## 背景（用户裁决①；M2-SETTINGS-UI-SFX-POLICY 勘察定案）

产品 Tauri 侧无任何 settings 读写通道（生产模式仅 5 命令），设置页 UI 无法接通。用户裁决释放本 slice：新增 `settings_get`/`settings_update_section` 两命令（形状已 pin 于 SFX-UI handoff），全栈打通 React→Tauri→Python core→`PipelineDefaultsService`。

## 交付（AC）

1. **AC1 契约修订**：M2-C1 Typed IPC 契约 rev（版本号+状态行+Revision history，M2-C1 rev 1.1/1.2 先例格式）——登记两命令的 wire shape（请求/响应/错误码），遵循既有契约纪律（typed fail-closed、错误码枚举）。
2. **AC2 Python core 桥**：core 侧命令处理（settings_get 返回当前 settings 或指定节；settings_update_section 走 `PipelineDefaultsService.save_settings_section`——**值域校验前置**（M2-SFX-ENTRY r1 R4 教训：写入端零校验=启动阻断不可自愈；非法 section/值在写入前 typed 拒绝，至少 sfx.policy 三值校验落地为首个实例）。
3. **AC3 Rust 命令**：`src-tauri` 新增两命令（main.rs allowlist 三处同步+capabilities，沿 SFX-UI handoff pin 的形状）；错误映射 typed。
4. **AC4 前端接通**：SettingsClient 从 mock 换真实通道名（SFX-UI 已 pin `settings_get`/`settings_update_section`——即以此为准）；SettingsPanel 保存流接通；既有 17 测试适配（命令名不变则近零改动）。
5. **AC5 测试**：Rust 命令测试；Python 桥测试（含 sfx.policy 三值写入合法/非法 typed 拒绝）；前端 vitest 回归（48 全绿）；契约测试对齐（既有 commandSurface pin 更新）。
6. **AC6 文档**：契约 rev diff+Task/Handoff；SFX-UI 的 blocked_on_contract 解除登记（由集成方在收口时落）。

## 允许修改面

`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`（rev 修订）、`src-tauri/**`（命令+capabilities+测试）、`src/**`（core 命令处理桥——勘察后最小面，预期 application/settings 或既有 core_service 命令分发处）、`apps/desktop/frontend/src/**`（SettingsClient 接通）、`tests/**`、`verification/M2-SETTINGS-IPC-CHANNEL/**`、Task/Handoff。

## 禁改面

其他契约文档、`packaging/**`、既有命令语义、`doc/STATUS.md`、SFX-UI 交付组件的视觉/交互（只接通道不改设计）。

## 纪律

- 基线不回退：三套件 530+1skipped 0 failed / vitest 48 全绿 / cargo 既有全绿。
- 契约纪律：typed fail-closed、错误码不发明（沿既有枚举）、wire shape 与 SFX-UI pin 逐字一致（改名即漂移）。
- 触及其他冻结面即停登记。
