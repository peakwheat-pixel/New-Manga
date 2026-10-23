---
task_id: PLUGIN-RUNTIME-1
kind: implementation
status: in_progress
owner: 待指派（非本 Task 实现者）
reviewer: reviewer-settings-a（非实现者）
created: 2026-10-23
base_commit: c793442946801bea7ab53799683cecc76260f672
depends_on: SETTINGS-OPEN-C-3-PLUGIN（done）
authorization: 用户授权 2026-10-23「授权 PLUGIN-RUNTIME-1，按建议值 D1–D6」
allowed_paths:
  - src/infrastructure/plugins/**
  - src/application/plugins/**
  - src/bootstrap/core_assembly.py
  - src/bootstrap/core_service.py
  - apps/desktop/src-tauri/src/**
  - apps/desktop/src-tauri/build.rs
  - apps/desktop/src-tauri/capabilities/**
  - apps/desktop/src-tauri/permissions/**
  - apps/desktop/src-tauri/gen/**
  - apps/desktop/frontend/src/settings/**
  - tests/**
  - doc/tasks/PLUGIN-RUNTIME-1.md
  - doc/handoffs/**
  - verification/PLUGIN-RUNTIME-1/**
---

# PLUGIN-RUNTIME-1 — 本地插件运行时（首发 `permissions: []`）

## 状态

**in_progress**（用户 2026-10-23 授权，D1–D6 按建议值）。实现期间设置页 `Plugin/Hooks` 的只读占位保持到运行时接线完成，不提前开放假控件；wire/控件只随真实运行能力落地。

## 目标

按 `doc/design/SETTINGS_SECTION_C_SCHEMAS.md` §4.1–§4.4（冻结）实现本地目录插件的最小运行时：

1. **本地目录插件发现**：插件根 `%LOCALAPPDATA%/New Manga/plugins/<plugin_id>/`（以 `app_data_dir` 解析，不写死）；只读扫描，不写插件文件；不做应用内安装器/市场/在线分发/自动更新。
2. **manifest v1 校验**：按 §4.2 冻结字段（`id`/`name`/`version`/`entry`/`hooks`/`permissions` 必填，`min_app_version`/`description` 可选）；`id` 必须等于目录名；`entry` 仅 `.py` 且必须存在；未知 Hook/未知权限/类型错 → **fail-closed 不加载** + `plugin_load_rejected` 审计。
3. **默认禁用**：`plugins.enabled = false` 为全局总开关且**默认关**；已发现插件默认 `disabled`；启用后只调用其声明的 Hook。
4. **`permissions: []` 首发**：本期只加载无权限插件（无文件/网络/模型访问）；带权限插件一律拒绝加载（即使 manifest 声明），未来批次另行放开。
5. **审计表**：`plugin_events`（加载/拒绝/启用/禁用/调用/错误），只追加、可查询；schema 变更走正常迁移（record-only 迁移预计 v+1）。
6. **Hook 契约冻结**：§4.4 六组 Hook（`before_detect` / `after_detect` / `before_ocr` / `after_ocr` / `before_export` / `after_export`）的 versioned JSON schema 落位；Hook 异常不改变主链路状态。
7. **崩溃隔离**：Hook 在独立子进程执行，超时/崩溃 = 该次 Hook 跳过 + `plugin_error` 审计 + 主链路继续。
8. **UI**：设置页 `Plugin/Hooks` 从只读占位升级为管理面（已安装列表、启用/禁用、打开插件目录、拒绝原因），**不得**出现无运行时功能的假控件。

## 关键裁决点（实施前必须确认）

| # | 裁决点 | 决策（2026-10-23 用户授权，按建议值） | 影响 |
|---|---|---|---|
| D1 | 隔离模型 | 每个 Hook 调用起独立 Python 子进程（与 Core 同解释器），stdin/stdout JSON 单次请求-响应，硬超时（如 10s） | 决定进程管理、超时、崩溃语义 |
| D2 | `plugin_events` schema | `event_id/plugin_id/event_type/occurred_at/detail_json`，`event_type ∈ {load_rejected, enabled, disabled, hook_invoked, plugin_error}` | 决定迁移 v+1 与审计查询 API |
| D3 | Hook 入参/出参 schema | versioned JSON（`schema_ref` + `payload`），`before_*` 可返回 override，`after_*` 只读 | 决定 core service 接线点 |
| D4 | 插件根解析 | `app_data_dir()/plugins`（dev preview 与生产各自解析） | 决定测试夹具与路径守卫 |
| D5 | 启用状态存储 | `settings.plugins.enabled` 布尔（默认 false）+ 逐插件启用状态（DB 或 settings 键） | 决定 settings section 与 wire |
| D6 | UI 是否本期开放 | 是：列表 + 开关 + 打开目录；无运行时功能的按钮一律不出现 | 决定前端工作与测试面 |

## 验收（AC，授权后实施）

- [x] **AC1 发现/校验**：合法 manifest 列出；未知 Hook/权限/字段/入口缺失/`id`≠目录名 → 拒绝加载 + `plugin_load_rejected` 审计。
- [x] **AC2 默认禁用**：`plugins.enabled=false` 时任何 Hook 都不调用；启用后仅声明的 Hook 被调用。
- [x] **AC3 隔离**：Hook 崩溃/超时不影响主链路，记录 `plugin_error`；同一 Run 继续。
- [x] **AC4 审计**：加载/拒绝/启用/禁用/调用/错误均可查询（`plugin_events`）。
- [x] **AC5 UI**：设置页管理面真实操作（列表/启用/禁用/打开目录），无假控件；`permissions: []` 外插件显示拒绝原因且不可启用。
- [x] **AC6 证据**：固定 commit、原始日志、独立非实现者 Review、GUI 烟测（安装示例插件 → 启用 → 触发一次 Hook → 审计可查 → 崩溃插件不影响主链路）。

## 明确不做

- 带权限插件（`files_read`/`files_write`/`network`/`model`）的加载与权限授予；
- 插件市场/在线分发/自动更新/应用内安装器；
- 插件直接访问 DB/Repository/任意路径；
- 更改 P15 白名单之外的新 write section（启用状态若走 settings 需在裁决 D5 中明确键集）。

## 测试要求（授权后填）

| 场景/AC | 计划命令 | 实际结果 | 证据 |
|---|---|---|---|
| AC1/AC2 Core | `python -m pytest tests/infrastructure/test_plugin_runtime.py -q` | PASS（17 passed：manifest 拒绝矩阵、发现、默认禁用、全局/逐插件开关） | core-pytest-targeted.log |
| AC3 隔离 | 同上（崩溃/超时用例） | PASS（真实子进程：崩溃 → `plugin_error`；超时 1s → `PLUGIN_HOOK_TIMEOUT`；主流程不抛） | core-pytest-targeted.log |
| AC4 审计 | 同上 + `tests/core/test_core_plugin_wire.py` | PASS（`audit_list` 最新优先、limit 校验、wire `plugins.audit_list`） | core-pytest-targeted.log |
| AC5 UI | `npx vitest run src/settings/PluginSettingsPanel.test.tsx src/settings/SettingsPage.test.tsx` | PASS（8 panel 用例 + settings 页；全量 45 files / 434 tests） | ui-test-frontend.log |
| 烟测 | dev preview：预置插件 → 面板发现/拒绝 → 全局启用 → 插件启用 → 审计 | PASS（12 开；拒绝原因可见；审计 4 条） | gui-smoke.md + screenshots/01 |

## Canonical Evidence

|evidence_id|ac|path|commit|sha256|status|
|---|---|---|---|---|---|
|EV-PLUGIN-RUNTIME-1-CORE-PYTEST-TARGETED|AC1-AC6|verification/PLUGIN-RUNTIME-1/core-pytest-targeted.log|a80cfd0bb83752534e138b0db7d04bfb2d2782a6|2ea3e66b3fe49aea4478f57f861d3d7b1bcd2612d0368fdbc0354fd332b8e07d|CANONICAL|
|EV-PLUGIN-RUNTIME-1-CORE-PYTEST|AC1-AC6|verification/PLUGIN-RUNTIME-1/core-pytest.log|a80cfd0bb83752534e138b0db7d04bfb2d2782a6|45c3899f3048ae6103b09aae566dfccfe2da1066b79ac552c09a4272acc8a601|CANONICAL|
|EV-PLUGIN-RUNTIME-1-GUI-SMOKE|AC1-AC6|verification/PLUGIN-RUNTIME-1/gui-smoke.md|a80cfd0bb83752534e138b0db7d04bfb2d2782a6|75010534c76375a6c74bddbdef6c3192613d75e06c767e3f432fffe049e06cfc|CANONICAL|
|EV-PLUGIN-RUNTIME-1-01-PLUGIN-PANEL-ENABLED|AC1-AC6|verification/PLUGIN-RUNTIME-1/screenshots/01-plugin-panel-enabled.png|a80cfd0bb83752534e138b0db7d04bfb2d2782a6|5cbb6485a148b70531b2fb82ea0bb3329d1edefd240908a7495f0cbd3f3a9aa0|CANONICAL|
|EV-PLUGIN-RUNTIME-1-UI-TEST-FRONTEND|AC1-AC6|verification/PLUGIN-RUNTIME-1/ui-test-frontend.log|a80cfd0bb83752534e138b0db7d04bfb2d2782a6|b50b9e5d93ba124477a6e562949602706dfa85ca05239f1b5c8996f8c7646db4|CANONICAL|
|EV-PLUGIN-RUNTIME-1-UI-TSC|AC1-AC6|verification/PLUGIN-RUNTIME-1/ui-tsc.log|a80cfd0bb83752534e138b0db7d04bfb2d2782a6|b40133c5e8d29e47805108247a1e80f91c940b340f79cdd243ce68dd6f0e8e81|CANONICAL|
|EV-PLUGIN-RUNTIME-1-WIRE-CARGO-TEST-SERIAL|AC1-AC6|verification/PLUGIN-RUNTIME-1/wire-cargo-test-serial.log|a80cfd0bb83752534e138b0db7d04bfb2d2782a6|bb18aaba968ced00051b5ff7793690332497da2d43270c4ed178daa906fb739b|CANONICAL|

## 交付与运行记录

- 2026-10-23：按指令预创建提案。
- 2026-10-23：用户授权「PLUGIN-RUNTIME-1，按建议值 D1–D6」；转 `in_progress` 并启动实现（D1 子进程隔离 10s 超时 / D2 `plugin_events` 迁移 / D3 versioned JSON hook / D4 `app_data_dir()/plugins` / D5 `plugins.enabled` + 逐插件状态 / D6 UI 本期开放管理面）。
- 2026-10-23（实现）：Core 新增 `src/infrastructure/plugins/`（manifest v1 校验 fail-closed、`_hook_runner.py` 隔离子进程入口、`PluginService` 发现/状态/审计/`run_hook`）；迁移 **v6**（`plugin_state` + `plugin_events` 两空表）；`core_assembly` 装配 `<data_root>/plugins`；`core_service` 新增 4 个应用层命令（`plugins.list/set_enabled/set_plugin_enabled/audit_list`，minor 保持 3）。Rust trait/Mock/Resilient/Stdio 4 方法 + 5 个 production 命令（含 opener 打开的 `plugins_open_directory`），`PRODUCTION_COMMANDS` 61→66、build.rs ACL、capabilities、allowlist 过滤、表面测试同步。前端 `SettingsClient` 5 方法 + `PluginSettingsPanel`（默认关全局开关/逐插件启停/拒绝原因/审计/打开目录）+ `SettingsPage` 12/12 开放。
- 2026-10-23（测试）：定向 24 passed；全量 2633 passed / 3 既有失败（detector 权重缺失 + workbench 时序 flaky，与本改动无关；新增迁移 v6 后同步更新了 schema/restore/packaging 测试中的版本硬编码）；cargo 153 passed；前端 45 files / 434 tests；tsc 0；GUI 烟测 PASS。

## Closeout Record

- Closeout：未开始（proposed）。
- canonical_evidence_status：pending；resource_closeout_status：pending。
- 删除/迁移/归档：0。
- 当前指针清理：本 Task 仅在 REBASELINE_PLAN 以 `proposed` 登记；授权前不进入 STATUS/ACTIVE。
