---
id: M2-SETTINGS-IPC-CHANNEL
title: "settings IPC 通道（settings_get/settings_update_section）：M2-C1 契约 rev + Rust 命令 + 前端接通（用户裁决①，SFX-UI 解除前提）"
kind: feature
status: done  # Owner 交付（实现+测试+契约 rev+handoff）；DSH 非作者 Review 与 Codex 集成收口后终态
approval: user_ruling_2026-10-02_three_confirmations
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权+自治授权）
depends_on: [M2-SETTINGS-UI-SFX-POLICY, M2-C1]
base_commit: f99a6c55
branch: agent/zcode/M2-SETTINGS-IPC-CHANNEL
worktree: G:/CODEX/New Manga.worktrees/M2-SETTINGS-IPC-CHANNEL-zcode
delivery_head: 45e15524（implement 单 commit；merge 4e432fe7 引入 depends_on 的 SFX-UI 交付；handoff/Task 回填=后续文档 commit）
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

## 交付记录（Owner 回填 2026-10-02，ZCode）

前置事实：SFX-UI 交付（`8c798aed` 实现 + `efad4b71` handoff，分支 `agent/zcode/M2-SETTINGS-UI-SFX-POLICY`）是本 Task `depends_on` 且 AC4 的接通对象，但未在本分支（fork 同为 `f99a6c55`）——以 merge `4e432fe7` 引入（零文件冲突，SFX-UI 改动面=纯前端 settings 新文件+App.tsx 2 行+verification，与本 Task 允许修改面零重叠）；AC4 在其交付物上做最小接通（命令名/逻辑/视觉零改动，仅注释与表面 pin 对齐）。

- [x] **AC1 契约修订**——`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` rev **1.2 → 1.3**：状态行版本+Revision history `1.3` 条目（用户裁决①引用）+§5 表 `GetSettings`/`SaveSettings` 行加 1.3 指针（transport-neutral 名保持 PROPOSAL）+新增 **§5.3 Product Tauri settings channel**（`settings_get`/`settings_update_section` wire shape：请求/响应/单节 null 通道/错误码=沿既有枚举 `INVALID_REQUEST`(validation)/`UNKNOWN`(internal)/`CORE_UNAVAILABLE`，零新码；写入端前置校验四条=sfx.policy 三值首例；宿主三处同步纪律）+§11 "Tauri command names" 行 1.3 注记。协议 envelope minor `1` → `2`（沿 M2-PROD-DETECT-3 core.detect 先例：向后兼容 widening，既有命令语义不变）。
- [x] **AC2 Python core 桥**——`src/bootstrap/core_service.py`：`PROTOCOL_MINOR` 1→2；新增 `settings.get`（全量 `{"settings": {...}}` / by-section `{"settings": {"<name>": <object|null>}}`，缺节=null 沿 1.2 frozen None 通道）与 `settings.update_section`（`{section, values}` → `save_settings_section` upsert → 返回更新后全量投影）两 handler+dispatch 分支；**写入端前置校验 typed fail-closed**（`SettingsRequestError` → `INVALID_REQUEST`，持久化之前）：section 非空 str、values 为 JSON object、`sfx.policy` 三值门（值域取自 domain `SfxPolicy` enum，防漂移）；`BindingValidationError` 兜底同映射；持久化失败 `UNKNOWN`(internal)。既有四命令 payload/result/错误码零变化。
- [x] **AC3 Rust 命令**——`apps/desktop/src-tauri`：`library_bridge.rs` `LibraryChannel` trait+Stdio（`round_trip("settings.get"/"settings.update_section")`，同一条既有 stdio 桥，零新传输）+Mock 三实现；`main.rs` 两命令（`settings_get(section: Option<String>)` / `settings_update_section(section, values)` → `.map_err(|e| e.code)` typed 映射）+`PRODUCTION_COMMANDS` 5→7+`SETTINGS_PRODUCTION_ONLY_COMMANDS`（probe/ac1 测试模式面保持冻结，沿 M2-IPC1 option-B 先例）+`generate_handler!` production 分支；allowlist 三处同步（常量/`generate_handler!`/`build.rs` app_manifest 12→14）+`capabilities/m2rc1-commands.json`（+`allow-settings-get`/`allow-settings-update-section`，description 修正为 14 命令口径）。
- [x] **AC4 前端接通**——`client.ts`/`client.test.ts`/`SettingsPanel.tsx`：命令名常量与 invoke 逻辑**零改动**（SFX-UI pin 逐字落地），仅 BLOCKED_ON_CONTRACT/PROPOSED 注释对齐为 RULED 落地口径；`resourceChannel/commandSurface.test.ts` 表面 pin 更新（`SETTINGS_PRODUCTION_ONLY_COMMANDS` 常量+production allow/probe deny CASE）；既有 48 vitest 中 47 条零修改、1 条 describe 名对齐。
- [x] **AC5 测试**——Python 新增 `tests/core/test_core_service_settings.py` **27 条**（全量/by-section 读取、unset=null≠`{}`、三值合法矩阵、非法 policy/形状 typed 拒绝+持久层未被改写的 R4 核心断言、ocr 透传、minor=2 pin）；既有 `test_core_service.py` 2 处+`test_core_detect.py` 2 处 minor 断言 1→2 后果同步（先例同款）。Rust 新增 2 条（mock 通道投影/typed 透传 + **真实 sidecar 端到端**：合法写→读回、非法值 INVALID_REQUEST 且旧值保留）。**三套件 602 passed + 1 skipped 0 failed**（基线 575+1sk + 27；解释器 `T1.1.1-impl-py312`，`PYTHONPATH=src`）；**cargo 46 passed + 1 ignored**（基线 44+1ig + 2）；**vitest 49 passed**（基线 48 + 1）；`tsc --noEmit` EXIT=0。
- [x] **AC6 文档**——本节+handoff `doc/handoffs/M2-SETTINGS-IPC-CHANNEL-45e15524.md`+`verification/M2-SETTINGS-IPC-CHANNEL/verification.md`。**SFX-UI 解除登记**：`M2-SETTINGS-UI-SFX-POLICY` 的 blocked_on_contract 解除前提（本 slice 释放+落地）已满足，解除登记（blocked_on_contract → 状态推进）由集成方在收口时按 PLAN 落（属 PLAN/STATUS 面，本 Task 禁改）。
- 纪律自检：`git status --porcelain` 干净（commit 后）、`git diff --check` EXIT=0；禁改面零触碰（其他契约文档、`packaging/**`、既有命令语义——core.ping/ListBooks/core.detect/core.shutdown 与资源通道命令 payload/result/错误码全部原样，minor bump 属 envelope 版本字段沿先例移动、`doc/STATUS.md`、SFX-UI 视觉/交互）。
