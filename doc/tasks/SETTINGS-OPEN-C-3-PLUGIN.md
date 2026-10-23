---
task_id: SETTINGS-OPEN-C-3-PLUGIN
kind: implementation
status: in_review
owner: 待指派（非本 Task 实现者）
reviewer: reviewer-settings-a（非实现者）
created: 2026-10-23
base_commit: 657c18d4a046c34de4e38885b9f5703a613c9d3d
depends_on: SETTINGS-OPEN-C-2-BACKUP（done）
allowed_paths:
  - apps/desktop/frontend/src/settings/**
  - doc/tasks/SETTINGS-OPEN-C-3-PLUGIN.md
  - doc/handoffs/**
  - verification/SETTINGS-OPEN-C-3-PLUGIN/**
---

# SETTINGS-OPEN-C-3-PLUGIN — Plugin/Hooks 无运行时只读面

## 目标

按 `doc/design/SETTINGS_SECTION_C_SCHEMAS.md` §4.5 交付最后一个设置分区的**无实现前只读面**：`plugins` 分类继续保持"未开放"（nav 按钮 disabled + "未开放"徽标），但面板占位文案从通用的"等待 section schema 冻结"改为 §4.5 冻结的专用只读说明，明确"插件系统尚未实现：当前版本未安装插件运行时……"。

**不实现插件运行时、不加载/审计/启用任何插件、不新增 wire/Tauri/Core 命令**；设计 §4.6 AC5 明确"本设计交付即满足；C-3 实现前不得出现可点控件"。

## 范围

1. `SettingsPage.tsx`：`plugins` 仍 `open: false`，`DisabledSection` 支持按分区传入专属 reason/title（当前统一文案是"等待 section schema 冻结"）。
2. 新增只读面板或扩展 `DisabledSection`：显示 §4.5 原文只读说明，**无任何按钮**（无"打开插件目录/启用/重载"——无运行时=假控件）。
3. `SettingsPage.test.tsx` / 相关测试：断言 plugins 仍 disabled + 文案为 §4.5 文案（而非"等待 section schema 冻结"）；11 开 1 关不变。
4. 不触碰 P15 白名单、不新增 settings section 写路径、不改 `permissions: []` 语义。

## 验收（AC）

- [x] **AC1 未开放保持**：`plugins` nav 按钮 `disabled`、aria-label/title 含"未开放"，`SETTINGS_CATEGORIES` 中 `open: false` 不变（11 开 1 关）。
- [x] **AC2 只读说明**：面板显示 §4.5 冻结文案（"插件系统尚未实现：当前版本未安装插件运行时……"），无任何可点控件（无 enable/reload/open-dir）。
- [x] **AC3 无新面**：无新增 Tauri 命令/`PRODUCTION_COMMANDS`/HostControl/`settings_update_section` 写路径；`plugins` 不出现在 `settings_get` 冻结键集。
- [x] **AC4 测试**：Vitest 断言 disabled + 文案 + 无按钮；全量前端测试与 tsc 通过；GUI 烟测（设置页 → Plugin/Hooks 显示只读说明）。
- [x] **AC5 证据**：固定 commit、原始日志、独立非实现者 Review、`verification/SETTINGS-OPEN-C-3-PLUGIN/**`。

## 测试要求

| 场景/AC | 计划命令 | 实际结果 | 证据 |
|---|---|---|---|
| AC1/AC3 前端 | `npx vitest run src/settings/SettingsPage.test.tsx src/settings/DisabledSection.test.tsx` | PASS（19 passed：plugins disabled + §4.5 文案 + 无按钮） | ui-test-frontend.log（节选） |
| AC4 全量 | `npx vitest run` + `tsc --noEmit` | PASS（44 files / **426 tests**；tsc exit 0） | ui-test-frontend.log、ui-tsc.log |
| 烟测 | dev preview：设置 → Plugin/Hooks | PASS（11 开 1 关；nav 可访问名 `Plugin/Hooks，未开放：插件系统尚未实现`；面板不可达/无控件） | gui-smoke.md + screenshots/01 |

## Canonical Evidence

|evidence_id|ac|path|commit|sha256|status|
|---|---|---|---|---|---|
|EV-C3-GUI-SMOKE|AC1-AC5|verification/SETTINGS-OPEN-C-3-PLUGIN/gui-smoke.md|85128cd2a3437442fde65c5991a0c07fe7a7ba86|804492415c38c37202cbb229858bdd2ecfe3b9917ede341fc903900b112ad833|CANONICAL|
|EV-C3-REVIEW-R1|AC1-AC5|verification/SETTINGS-OPEN-C-3-PLUGIN/review-r1.md|85128cd2a3437442fde65c5991a0c07fe7a7ba86|26dbc016a0ae49d43554169198c7a1161b3280d34cb9f47d579b9e2187cc44ab|CANONICAL|
|EV-C3-01-SETTINGS-PLUGIN-CLOSED|AC1-AC5|verification/SETTINGS-OPEN-C-3-PLUGIN/screenshots/01-settings-plugin-closed.png|85128cd2a3437442fde65c5991a0c07fe7a7ba86|c3aae4637847107bb906dd08c8c29dcc3e1ff1a4199e325b19bb4a2d33154d9f|CANONICAL|
|EV-C3-UI-TEST-FRONTEND|AC1-AC5|verification/SETTINGS-OPEN-C-3-PLUGIN/ui-test-frontend.log|85128cd2a3437442fde65c5991a0c07fe7a7ba86|a868df26ad47eaa0987230aaf491841a6c8c9d227bd4dd81931e351de990ccb6|CANONICAL|
|EV-C3-UI-TSC|AC1-AC5|verification/SETTINGS-OPEN-C-3-PLUGIN/ui-tsc.log|85128cd2a3437442fde65c5991a0c07fe7a7ba86|d7a344e783651d4d3a6f3bc9e7d24ddd5e6c6ecdb7881de7e82e98c21adcc5b6|CANONICAL|

## 交付与运行记录

- 2026-10-23：C-2 关闭后释放；启动实现。
- 2026-10-23（Review r1 处置）：Task/STATUS/LEDGER 统一 `in_review`；§4.5 文案改为**逐字单段**（新增 `DisabledSection.body`，plugin 面板以完整原文渲染，通用「该分区暂不可编辑…」句不再插入；测试用 `toBe` 精确断言）；全量测试文件数修正 44；Closeout 文案更新。GUI 边界：plugins 面板不可达，完整文案仅由组件测试验证（gui-smoke 已写明）。
- 2026-10-23（实现）：`DisabledSection` 增 `description`/`showPlaceholderControl`（plugin 面不渲染任何控件）；`SettingsPage` 常量 `PLUGIN_SECTION_REASON`/`PLUGIN_SECTION_DESCRIPTION`（§4.5 原文）、nav 与占位面板改用专属 reason；新增 `DisabledSection.test.tsx`（2 用例：冻结文案 + 无按钮 / 通用面保留 disabled 控件），`SettingsPage.test.tsx` 断言 plugins 文案。

## Closeout Record

- Closeout：待 Review approved 后 closeout（r1 生命周期/文案处置后复审）。
- canonical_evidence_status：pending；resource_closeout_status：pending。
- 删除/迁移/归档：0。
- 当前指针清理：STATUS/REBASELINE/LEDGER 登记本 Task。
