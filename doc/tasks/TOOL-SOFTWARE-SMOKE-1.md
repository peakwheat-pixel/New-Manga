---
id: TOOL-SOFTWARE-SMOKE-1
title: 分层软件检查工具（替代手工 GUI 冒烟）
kind: implementation
governance_version: 3
status: in_progress
language: zh-CN
suggested_owner: dsh
owner: dsh（本会话 Lead）
reviewer: （待独立 Reviewer，非实现者）
depends_on: [PLUGIN-RUNTIME-PACKAGED-PYTHON-1]
base_commit: 6e3ce06f96bb48bc7a8de0a114c8391a9bc82014
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/TOOL-SOFTWARE-SMOKE-1
allowed_paths:
  - tools/smoke/**
  - tests/tools/**
  - verification/TOOL-SOFTWARE-SMOKE-1/**
  - doc/tasks/TOOL-SOFTWARE-SMOKE-1.md
  - doc/handoffs/**
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
authorization: 用户 2026-10-23 要求制作「插件/软件检查工具」替代手工 GUI 冒烟；本会话选定方案 D。
---

# TOOL-SOFTWARE-SMOKE-1：分层软件检查工具（替代手工 GUI 冒烟）

## 来源与目标

**来源。** 用户 2026-10-23 要求用可重复、无人值守、可断言、低 token 的检查工具替代手工 GUI 冒烟。
前置证据：`verification/GUI-SANDBOX-SMOKE-1/smoke-notes.md` 记录的四个痛点（启动慢、鼠标/截图 token 消耗、
GUI 内 Hook 需要检测权重、结论无法自动断言）；`GUI-PLUGIN-SANDBOX-SMOKE-1` 因此 paused。
用户在本会话明确要求「先仔细看项目代码」，并选定**方案 D：分层检查工具**（Core 沙箱 + 真实 Core wire +
前端 tsc/Vitest + 真实 bundle），因为其后续仍会修改 UI/UX，需要不依赖 GUI 的稳定契约层。

**目标。** 新增一个只读的检查工具（不修改生产代码与共享契约），一条命令完成四层检查，输出机器可读 JSON
与简体中文摘要，退出码可判定；覆盖插件面、沙箱面、wire 面、前端面、打包面；默认无 GUI、无鼠标、截图关闭；
可重复执行且不残留临时插件/进程。

**实现路径（拟议）。** `tools/smoke/**`（新增）+ `tests/tools/**`（新增），复用既有生产装配
`assemble_production_core`、`PluginService`、`AppContainerSandbox`、`bootstrap.core_service` stdio 协议、
真实 `core-sidecar` bundle 与前端现有 `tsc`/Vitest 工具链。`src/**`、`apps/**` 生产代码不改。

**预算（本机实测基线）。** AppContainer 16 例 26.3s；真实 Core 子进程插件命令链 0.45s；
前端全量 Vitest 435 tests 4.9s；`tsc --noEmit` 3.8s。目标单次全量 < 90s。

## Acceptance Criteria

- [ ] **AC1 一键入口与报告**：`python -m tools.smoke.plugins` 一条命令执行全部默认层；支持
  `--only` / `--skip` / `--list-checks` / `--json PATH` / `--keep-artifacts`；输出 JSON（schema 版本、
  每层/每检查项状态、稳定错误码、耗时）与中文摘要；退出码 0=全部 PASS（显式 skip 允许），
  1=存在 FAIL/BLOCKED，2=工具自身错误。
- [ ] **AC2 Core 沙箱层**：在真实 AppContainer + 独立临时数据根上断言——插件加载/拒绝
  （`PLUGIN_PERMISSIONS_UNSUPPORTED` 拒绝语义）、启用/禁用、权限徽标数据、审计事件
  （`load_ok`/`load_rejected`/`enabled`/`hook_invoked`/`plugin_error`）、根外读被拒、无权限插件网络栈被拒、
  `network` 权限插件被放行、超时 tree-kill、fail-closed（`PLUGIN_HOOK_UNAVAILABLE`）。
- [ ] **AC3 Wire 层**：启动真实 `python -m bootstrap.core_service` 子进程，按 Tauri/前端实际消费的
  JSON-lines 信封调用 `core.ping`、`plugins.list`、`plugins.set_enabled`、`plugins.set_plugin_enabled`、
  `plugins.audit_list`，断言默认关闭、状态往返、拒绝插件错误码（`PLUGIN_NOT_LOADED`/`PLUGIN_NOT_FOUND`）、
  审计事件与协议字段；该层不依赖 DOM/视觉，供后续 UI/UX 改动时守住后端契约。
- [ ] **AC4 前端层**：对 `apps/desktop/frontend` 执行 `tsc --noEmit` 与全量 Vitest，断言全部通过；
  UI/UX 改动后仍由现有测试与类型检查兜底，无需启动 GUI 或占用鼠标。npm/node_modules 缺失时记为
  BLOCKED（不得写成 PASS），可用 `--skip frontend` 显式跳过。
- [ ] **AC5 打包层**：断言真实 `apps/desktop/src-tauri/target/core-sidecar/core-sidecar/python/python.exe`
  存在、可在最小 PATH 下启动并导入 Hook 所需标准库、`_hook_interpreter()` 在模拟 frozen 布局下解析到该
  解释器，并在真实 AppContainer 中执行一个 Hook；可选 `--repack` 复用
  `packaging/m2ac5/verify_bundled_python.ps1` 做复制+启动+Hook 复验。
- [ ] **AC6 幂等、无残留与回归**：连续两次全量运行 PASS 且不修改仓库跟踪文件；临时目录默认清理、
  `--keep-artifacts` 可保留；运行后无残留 Hook/Core/npm 子进程；定向工具测试与
  `python -m pytest tests -q` 全量 PASS；`pwsh -NoProfile -File tools/governance/check.ps1` PASS；
  独立 Reviewer（非实现者）复审通过。
- [ ] **AC7 边界如实**：不修改 `src/**`、`apps/**` 生产代码与冻结 IPC 契约；不引入新依赖；
  不点击/拖拽 GUI、默认不截图、不做 NSIS/Tauri 安装包冒烟、不验证检测模型推理；文档明确标注这些非目标，
  以及 `GUI-PLUGIN-SANDBOX-SMOKE-1` 的恢复/关闭依据由 Lead 在 closeout 时决定、不在本 Task 自动改变其状态。

## 允许修改范围

- 新增 `tools/smoke/**`（检查工具本体；入口 `python -m tools.smoke.plugins`）。
- 新增 `tests/tools/**`（工具自身的定向测试；不替代验收性全量运行）。
- 新增 `verification/TOOL-SOFTWARE-SMOKE-1/**`（本 Task 证据）。
- 本 Task 文件、`doc/handoffs/**`、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`
  （仅 Lead 集成登记与指针维护）。

## 禁止范围

- 不修改 `src/**`、`apps/**`（含前端、Tauri/Rust、IPC 契约、Schema、依赖清单）。
- 不修改其它 Task、Review、历史证据；不删除任何既有文件；不清理/GC/prune worktree。
- 不做 GUI 交互自动化（点击/拖拽/窗口控制）、不做安装包端到端、不验证模型推理质量。
- 不触碰用户真实数据根；运行数据只落在独立临时目录与 workspace/证据目录。
- 不执行 `git push/merge/reset/stash`；不调用 `agy`/`antigravity-dispatch`。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1–AC5 验收 | `python -m tools.smoke.plugins --json verification/TOOL-SOFTWARE-SMOKE-1/smoke-report.json` | Windows；npm/node_modules 存在；真实 bundle 存在 | NOT_RUN | 待生成 |
| AC6 幂等 | 同命令连续运行两次，比较退出码与临时目录残留 | 同上 | NOT_RUN | 待生成 |
| AC6 定向 | `python -m pytest tests/tools -q` | Python 3.14 | NOT_RUN | 待生成 |
| AC6 回归 | `python -m pytest tests -q` | Python 3.14 | NOT_RUN | 待生成 |
| AC6 治理 | `pwsh -NoProfile -File tools/governance/check.ps1` | 仓库根 | NOT_RUN | 待生成 |

## 依赖、风险与阻塞

- **硬依赖**：`PLUGIN-RUNTIME-SANDBOX-2`、`PLUGIN-RUNTIME-CAPABILITY-1`、`PLUGIN-RUNTIME-PACKAGED-PYTHON-1`
  均已完成（approved），提供真实 AppContainer、network capability 与 bundle 解释器。
- **R1 环境耦合**：真实 AppContainer 要求 Windows 非受限账户（本机已实测 16 passed）；
  真实 bundle 不存在或前端 `node_modules` 缺失时，对应层记 BLOCKED 而非 PASS，可用 `--skip` 显式跳过。
- **R2 网络波动**：`network` 放行只断言「非 PermissionError」（成功/超时/拒绝连接均可接受），不做外网可用性断言。
- **R3 前端测试漂移**：未来改 UI/UX 会更新前端测试，工具只运行当前仓库测试；若测试文件被删除，前端层应给出
  明确 BLOCKED/FAIL，而不是静默跳过。
- **R4 AppContainer profile 残留**：profile 为 OS 级只读容器身份，工具不主动删除；临时插件目录与进程必须清理。
- **非阻塞**：`GUI-PLUGIN-SANDBOX-SMOKE-1` 保持 paused；本 Task 产出可作为 Lead 决定恢复/关闭的依据，但不在本 Task 自动处理。

## 交付与运行记录

- Handoff：尚无（实施完成后写 `doc/handoffs/TOOL-SOFTWARE-SMOKE-1-<short-head>.md`）。
- Review：尚无（完成后由独立 Reviewer 复审，非实现者）。
- 实际测试：尚无。
- 实施提交 / delivery_head：待实施后填写。

## Canonical Evidence

进入 `in_review` 前填写；证据目录 `verification/TOOL-SOFTWARE-SMOKE-1/`。

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|

## Closeout Record

- Closeout date / Codex：待关闭时填写。
- canonical_evidence_status：`pending` / `complete`。
- resource_closeout_status：`pending` / `complete`。
- 删除、迁移、归档数量/字节数：待关闭时填写；无操作填写 0。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：STATUS / Plan / Task 导航 / rolling checkpoint 已更新，或说明无需更新。
