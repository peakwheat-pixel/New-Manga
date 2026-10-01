---
id: M2-SETTINGS-UI-SFX-POLICY
title: "React 设置页接入 sfx.policy 配置（SFX-ENTRY 后续；UI 协议说明：最小键接入，视觉审查可后补 Qoder）"
kind: feature
status: blocked_on_contract  # AC1 判定=需新 Tauri 命令→触 M2-C1 冻结契约面，即停登记移交集成方；AC2/AC3 已 mock 通道先行落地（48 vitest 全绿）

approval: user_ruling_2026-10-01_three_followups_all
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权+自治授权）
depends_on: [M2-SFX-TRANSLATE-ENTRY]
base_commit: f534c3e7  # Task 授权基线；分支 fork=批次 release f99a6c55
branch: agent/zcode/M2-SETTINGS-UI-SFX-POLICY
worktree: G:/CODEX/New Manga.worktrees/M2-SETTINGS-UI-SFX-POLICY-zcode
delivery_head: 8c798aed（implement=8c798aed → handoff/Task 回填=本 commit；AC1=BLOCKED_ON_CONTRACT，Rust/Python/契约零 diff）
tip_note: handoff=doc/handoffs/M2-SETTINGS-UI-SFX-POLICY-8c798aed.md；勘察结论=生产 invoke 表面仅 5 命令（main.rs:557-563）无任何 settings 通道→需新命令触契约即停；UI=最小 Settings 区组件（设置页尚不存在的事实偏差已在案）；建议命令名 settings_get / settings_update_section 已 pin 进前端测试；解除阻断=集成方释放 settings IPC 通道 Task
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

## 交付记录（Owner 回填 2026-10-01，delivery_head=8c798aed）

- [x] **AC1 IPC 通道勘察（BLOCKED_ON_CONTRACT）**——生产 invoke 表面（`src-tauri/src/main.rs:557-563`）恰好 5 命令（`issue_resource_url`/`revoke_ref`/`revoke_resource_refs`/`core_ping`/`library_list_books`），probe/ac1 各有模式面；**任何模式无 settings 读/写命令**（无通用 get/update 也无逐键）。前端同样**无设置页**（App.tsx=RC2 宿主+LibraryPanel，任务书"既有设置页"假设与代码不符，已在案）。Python core 侧零改动可用（读 `PipelineDefaultsService.read().settings["sfx"]["policy"]` / 写 `save_settings_section("sfx", {policy})`，`pipeline_defaults.py:59/105`）。接通需新增 Tauri 命令（main.rs 三处手工 allowlist 同步+capabilities+前端 surface pin）→ **触 M2-C1 冻结契约面，按本任务书 AC1 规则即停**，`doc/contracts/**` 零触碰；建议命令名 `settings_get`/`settings_update_section` 与 wire shape 已登记进 handoff 供集成方裁决（前端常量+测试 pin，改名即漂移警报）。判定依据与建议形状见 handoff §AC1。
- [x] **AC2 UI（mock 通道先行，任务书许可范围）**——最小 Settings 区组件 `frontend/src/settings/SettingsPanel.tsx` 挂载于 App.tsx（LibraryPanel 旁；设置页不存在的事实偏差处置=最小骨架，未扩产品范围），"翻译与检测 (Translation & Detection)"分组内 SFX 策略三值 select（skip/translate/manual，复用 LibraryPanel 设计语言）+ 保存按钮（dirty 门控/保存中禁用）+ 当前生效值行（默认 skip 时标注"（默认）"，unset/非法折叠为默认，Core 仍 fail-fast 权威）+ 作用域提示原文：**"保存后重新打开应用生效；仅对此后新建检出的 region 生效（既有页面需重新检出）"**（事实源=M2-SFX-TRANSLATE-ENTRY r1 R1）。保存失败/加载失败=显式错误块（LibraryPanel 同款，无自动重试）。快照=`verification/M2-SETTINGS-UI-SFX-POLICY/settings-panel-ssr-snapshot.md`（六态 SSR）。
- [x] **AC3 测试**——vitest **48 passed 0 failed**（基线 5 文件 31 条全绿后新增 17：`settings/client.test.ts` 7 条=建议命令名 pin/payload 构造×3/投影映射含非法→默认/invoke 参数精确矩阵×3/类型化无重试错误；`settings/SettingsPanel.test.tsx` 10 条=三值 selected 渲染/unset→默认/作用域文案原文/无变化禁用/loading/load-error/2 条 createRoot 挂载流）。全 mock invoke 通道；`npx tsc --noEmit` EXIT=0。**Rust 零 diff（cargo 无需求）、Python 零改动**——与任务书预期一致。
- [x] **AC4 文档**——handoff=`doc/handoffs/M2-SETTINGS-UI-SFX-POLICY-8c798aed.md`（勘察结论+契约判定+复现命令+下一任务建议）；组件快照已登记（SSR 六态）；本 Task frontmatter/交付记录回填。
- 纪律：`git diff --check` EXIT=0；禁改面（`doc/contracts/**`、`src/**` Python、`src-tauri/**` 既有命令语义、`packaging/**`、`doc/STATUS.md`）零触碰；改动面=仅 `apps/desktop/frontend/src/**`+`verification/M2-SETTINGS-UI-SFX-POLICY/**`+Task/Handoff。
- **解除阻断路径**：集成方（Codex）裁决 settings IPC 通道（M2-C1 契约修订流程）→ 释放 settings 通道 Task（Rust 新命令+契约登记+前端命令名对齐）→ 本 Task UI/测试换真实通道即端到端。可直接转发指令见 handoff §下一任务建议。
