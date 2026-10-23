---
task_id: SETTINGS-OPEN-C-3-PLUGIN
author: dsh (Lead, epoch 10)
recipient: Codex / 下一批次 Owner
base_commit: 657c18d4a046c34de4e38885b9f5703a613c9d3d
delivery_head: 5e82a42cabbe8927e98088c6f7e0d8002f15a339
status: in_review
---

# Handoff — SETTINGS-OPEN-C-3-PLUGIN（Plugin/Hooks 无运行时只读面）

## 1. 交付摘要

按 [SETTINGS_SECTION_C_SCHEMAS.md](../design/SETTINGS_SECTION_C_SCHEMAS.md) §4.5 交付最后一个设置分区的**无实现前只读面**，实现范围 `657c18d4..5e82a42c`：

- `DisabledSection.tsx`：新增 `description?: string` 与 `showPlaceholderControl?: boolean`（默认 `true`，既有分区行为不变）；plugins 面 `showPlaceholderControl={false}`，**不渲染任何控件**。
- `SettingsPage.tsx`：新增 `PLUGIN_SECTION_REASON = "插件系统尚未实现"` 与 `PLUGIN_SECTION_DESCRIPTION`（§4.5 原文：本地目录插件、manifest v1、Hook 默认禁用、崩溃隔离、审计；实现后管理已安装插件与权限）；nav 的 aria-label/title 与占位面板改用该 reason。`plugins` 仍 `open: false`（**11 开 1 关**）。
- 测试：`DisabledSection.test.tsx` 新增 2 用例（plugins 版冻结文案 + `querySelector("button") === null`；通用面保留 disabled 控件）；`SettingsPage.test.tsx` 断言 plugins 的 title/aria-label 为"插件系统尚未实现"。
- **未新增**任何 Tauri/Core/wire 命令、`PRODUCTION_COMMANDS`、P15 白名单或 `settings_update_section` 写路径；`plugins` 不出现在 `settings_get` 冻结键集。

## 2. 验证

| 命令 | 结果 |
|---|---|
| `npx vitest run src/settings/SettingsPage.test.tsx src/settings/DisabledSection.test.tsx` | PASS（19 passed） |
| `npx vitest run`（全量） | PASS（44 files / **426 tests**） |
| `tsc --noEmit` | exit 0 |
| GUI 烟测（dev preview） | PASS：设置页 11 开 1 关；`Plugin/Hooks` 可访问名 `Plugin/Hooks，未开放：插件系统尚未实现`；面板不可达、无控件 |

原始日志/截图：`verification/SETTINGS-OPEN-C-3-PLUGIN/**`（`ui-test-frontend.log`、`ui-tsc.log`、`gui-smoke.md`、`screenshots/01-settings-plugin-closed.png`）。

## 3. 未执行 / 明确非本 Task 范围

1. **插件运行时未实现**：加载/启用/禁用/审计/Hook 调用均不在本批；§4.6 AC1–AC4 属"插件系统实现 Task"，需另行裁决与授权。
2. 分区保持未开放（设计 §4.5 明确"保持未开放状态，按钮不开放"）；C-3 不把 plugins 变为可点分区。
3. 未改 `permissions: []` 语义、未引入插件目录选择/文件系统访问。

## 4. 推荐下一步

- C-3 关闭后，设置页 12 分类中 **11 开 1 关（Plugin 按设计保持只读未开放）**，设置分区批次 A/B/C 全部完成。
- 下一个自然候选：按 REBASELINE_PLAN 释放 **插件系统实现 Task**（需用户/Codex 明确授权运行时、进程隔离、审计表与 Hook 契约；设计 §4.1–§4.4 已冻结）。
