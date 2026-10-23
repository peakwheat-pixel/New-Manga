---
task_id: PLUGIN-RUNTIME-1
kind: implementation
status: proposed
owner: 待指派（非本 Task 实现者）
reviewer: reviewer-settings-a（非实现者）
created: 2026-10-23
base_commit: c793442946801bea7ab53799683cecc76260f672
depends_on: SETTINGS-OPEN-C-3-PLUGIN（done）
authorization: 待用户/Codex 明确授权（本文件仅提案，未授权前不实施、不新增 wire/控件）
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

**proposed（未释放）**。本 Task 由指令要求预先创建；在用户/Codex 明确授权前：

- 不实施任何运行时代码；
- 不新增 Tauri/Core/wire 命令；
- 不开放任何插件控件（设置页 `Plugin/Hooks` 保持 `settings-disabled-section-plugins` 只读占位，见 `SETTINGS-OPEN-C-3-PLUGIN`）。

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

| # | 裁决点 | 建议值 | 影响 |
|---|---|---|---|
| D1 | 隔离模型 | 每个 Hook 调用起独立 Python 子进程（与 Core 同解释器），stdin/stdout JSON 单次请求-响应，硬超时（如 10s） | 决定进程管理、超时、崩溃语义 |
| D2 | `plugin_events` schema | `event_id/plugin_id/event_type/occurred_at/detail_json`，`event_type ∈ {load_rejected, enabled, disabled, hook_invoked, plugin_error}` | 决定迁移 v+1 与审计查询 API |
| D3 | Hook 入参/出参 schema | versioned JSON（`schema_ref` + `payload`），`before_*` 可返回 override，`after_*` 只读 | 决定 core service 接线点 |
| D4 | 插件根解析 | `app_data_dir()/plugins`（dev preview 与生产各自解析） | 决定测试夹具与路径守卫 |
| D5 | 启用状态存储 | `settings.plugins.enabled` 布尔（默认 false）+ 逐插件启用状态（DB 或 settings 键） | 决定 settings section 与 wire |
| D6 | UI 是否本期开放 | 是：列表 + 开关 + 打开目录；无运行时功能的按钮一律不出现 | 决定前端工作与测试面 |

## 验收（AC，授权后实施）

- [ ] **AC1 发现/校验**：合法 manifest 列出；未知 Hook/权限/字段/入口缺失/`id`≠目录名 → 拒绝加载 + `plugin_load_rejected` 审计。
- [ ] **AC2 默认禁用**：`plugins.enabled=false` 时任何 Hook 都不调用；启用后仅声明的 Hook 被调用。
- [ ] **AC3 隔离**：Hook 崩溃/超时不影响主链路，记录 `plugin_error`；同一 Run 继续。
- [ ] **AC4 审计**：加载/拒绝/启用/禁用/调用/错误均可查询（`plugin_events`）。
- [ ] **AC5 UI**：设置页管理面真实操作（列表/启用/禁用/打开目录），无假控件；`permissions: []` 外插件显示拒绝原因且不可启用。
- [ ] **AC6 证据**：固定 commit、原始日志、独立非实现者 Review、GUI 烟测（安装示例插件 → 启用 → 触发一次 Hook → 审计可查 → 崩溃插件不影响主链路）。

## 明确不做

- 带权限插件（`files_read`/`files_write`/`network`/`model`）的加载与权限授予；
- 插件市场/在线分发/自动更新/应用内安装器；
- 插件直接访问 DB/Repository/任意路径；
- 更改 P15 白名单之外的新 write section（启用状态若走 settings 需在裁决 D5 中明确键集）。

## 测试要求（授权后填）

| 场景/AC | 计划命令 | 实际结果 | 证据 |
|---|---|---|---|
| AC1/AC2 Core | `python -m pytest tests/infrastructure/test_plugin_runtime.py -q` | 待填 | 待填 |
| AC3 隔离 | 同上（崩溃/超时用例） | 待填 | 待填 |
| AC4 审计 | 同上 + wire 查询 | 待填 | 待填 |
| AC5 UI | `npx vitest run src/settings/PluginSettingsPanel.test.tsx` | 待填 | 待填 |
| 烟测 | dev preview：安装示例插件 → 启用 → Hook → 审计 | 待填 | 待填 |

## Canonical Evidence

|evidence_id|ac|path|commit|sha256|status|
|---|---|---|---|---|---|
|EV-PLUGIN-RUNTIME-1-PENDING|AC1-AC6|PENDING|PENDING|PENDING|CANONICAL|

## 交付与运行记录

- 2026-10-23：按指令预创建提案；**等待用户/Codex 授权**后转 `ready` 并指派实现者。

## Closeout Record

- Closeout：未开始（proposed）。
- canonical_evidence_status：pending；resource_closeout_status：pending。
- 删除/迁移/归档：0。
- 当前指针清理：本 Task 仅在 REBASELINE_PLAN 以 `proposed` 登记；授权前不进入 STATUS/ACTIVE。
