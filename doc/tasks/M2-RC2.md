---
id: M2-RC2
title: Resource Channel Command Surface and Sidecar Boundary Hardening
kind: implementation
status: in_progress
release_state: RESOURCE_CHANNEL_COMMAND_SURFACE_RELEASED
approval: approved_by_user_2026-09-27
execution_approval: approved_by_user_2026-09-27_explicit_task_release
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness
depends_on: [M2-RC1]
base_commit: 22a2c2bf9a70d8c3b81edcdbe0e1ef146db556e5
branch: agent/zcode/M2-RC2-resource-channel-hardening
worktree: C:/Users/49745/.codex/worktrees/m2-rc2-zcode/New Manga
integration_commit: null
---

# M2-RC2 — Resource Channel Command Surface and Sidecar Boundary Hardening

## 来源与目标

承接 [M2-RC1 Handoff](../handoffs/M2-RC1-FIX-702b02b0.md) 与 DSH `accepted_deferral`：F-03（收敛 Tauri command 暴露面；capability、ACL/CSP 拒绝未授权调用；由 Python Core/SQLite 持有 catalog authority）及 F-05（提供 Python Core resource channel 的独立 sidecar 入口，避免 `src.infrastructure` 包级传递导入）。目标是落实并验证这两条边界，不扩大到产品级安全或打包就绪声明。

## Acceptance Criteria

- [ ] **RC2-AC1 命令面收敛（F-03）**：列出并测试 `register_catalog`、`probe_*`、`ttl_override` 的生产暴露面；在 Tauri command allowlist、capability、ACL/CSP 与 Core 权威边界下，WebView 不得提交 OS 路径、任意 TTL 或可伪造的 catalog 状态；catalog 生命周期由 Core/SQLite 管理。提供授权与拒绝矩阵及日志证据。
- [ ] **RC2-AC2 独立 sidecar 入口（F-05）**：resource-channel sidecar 可由最小独立入口启动，避免导入 `src.infrastructure` 包时的无关传递依赖；提供 headless/import 边界测试并记录实际加载模块。
- [ ] **RC2-AC3 诚实 Gate 与证据**：交付授权/拒绝测试、sidecar 隔离证据、原始日志和 Handoff；将 S1-B3/B5/B6/B8 状态保持如实（未验证项为 `UNVERIFIED`/`NOT_RUN`），不宣称产品级安全、安装或打包就绪；Handoff 明确列出仍需独立验证的条件。

## 允许修改范围（Codex 于 2026-09-27 释放时冻结）

- `apps/desktop/src-tauri/**`：仅 resource-channel command 注册/allowlist、capability、ACL/CSP 与对应测试；不改打包配置或 release 面。
- `apps/desktop/frontend/**`：仅本 Task 的 invoke allow/deny 消费端测试与必要的 command 接线。
- `src/application/resource_channel/**`、`src/infrastructure/resource_channel/**`：仅 Core/SQLite catalog authority 与独立 sidecar 入口所需改动。
- `src/infrastructure/__init__.py`：仅当隔离测试证明必要时允许修改；Owner 须先在 Task/Handoff 留下证据与具体改动理由。
- `tests/m2_resource_channel/**`、`verification/M2-RC2/**`、本 Task 与一份 `doc/handoffs/M2-RC2-*.md`。
- `doc/reviews/M2-RC2-<reviewed-head>.md`：仅由非作者 DeepSeek Harness 编写；Codex 负责总索引、Roadmap、STATUS 和 Task 索引状态导航。

## 禁止范围

不修改共享 Contract、SQLite schema/migrations、Legacy QML、用户源文件、根目录依赖/锁文件或打包发布面；不以此 Task 关闭 S1-B3/B5/B6/B8，也不作产品级安全声明。超出上述允许路径须先暂停并由 Codex 另行授权；不因测试或文档便利而扩展修改面。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| RC2-AC1 Python/Core | `python -m pytest tests/m2_resource_channel -q`（含新增 catalog authority 与 bridge 拒绝用例） | Windows；项目 Python 环境；仅合成资源 | RC2 AC `NOT_RUN`（尚无实现）；释放基线 `PASS`（43 passed） | [baseline log](../../verification/M2-RC2/release-validation-22a2c2bf.md)；Owner 原始日志 / Handoff |
| RC2-AC1 Tauri/Rust | `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --locked`（含 command allow/deny 与 capability 边界用例） | Windows；Rust/Cargo 工具链 | RC2 AC `NOT_RUN`（尚无实现）；释放基线 `PASS`（12 passed） | [baseline log](../../verification/M2-RC2/release-validation-22a2c2bf.md)；Owner 原始日志 / Handoff |
| RC2-AC1 frontend | `npm test --prefix apps/desktop/frontend -- --run`（含 WebView invoke allow/deny 矩阵） | Node/npm；仅合成资源 | RC2 AC `NOT_RUN`（尚无实现）；释放基线 `PASS`（8 passed） | [baseline log](../../verification/M2-RC2/release-validation-22a2c2bf.md)；Owner 原始日志 / Handoff |
| RC2-AC1/2 E2E 与隔离 | `python verification/M2-RC2/run_e2e.py`（此 runner 为本 Task 交付项；通过真实 sidecar 启动验证拒绝边界并记录加载模块） | Windows + WebView2；项目 Python/Rust/Node 环境；仅合成资源 | `BLOCKED`（RC2 runner 尚未交付；命令未能启动 E2E）；RC2 AC `NOT_RUN` | [baseline log](../../verification/M2-RC2/release-validation-22a2c2bf.md)；`verification/M2-RC2/**` 原始日志及模块跟踪 |
| RC2-AC3 honest gates | 对照 S1-B3/B5/B6/B8 状态、Handoff 与 Reviewer 独立 Review | 完成 Owner 交付后 | NOT_RUN（Owner 尚未交付） | Handoff / Review |

## 依赖、风险与阻塞

硬依赖：[M2-RC1](M2-RC1.md) 集成完成。F-03 的具体 command/capability 边界与 catalog 持久化形态须在释放 Task 时明确；任何 Schema 变化须另行裁决。S1-B3/B8 的产品级安全边界继续有效。

## 交付与运行记录

- 状态：`ready / RESOURCE_CHANNEL_COMMAND_SURFACE_RELEASED`；Owner=ZCode，Reviewer=DeepSeek Harness（非作者），Codex Integrator。
- 来源：M2-RC1 F-03/F-05 `accepted_deferral`；依赖 M2-RC1=`done`；用户于 2026-09-27 明确授权本 Task 单独释放。
- 固定实现基线、branch/worktree 和启动核验见 [release-22a2c2bf](../../verification/M2-RC2/release-22a2c2bf.md)。Task 文件只由 Owner 从记录的 release commit 取入实现分支，再提交 `ready`→`in_progress` 认领；不要把 release 治理提交并入实现历史。
