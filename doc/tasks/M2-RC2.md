---
id: M2-RC2
title: Resource Channel Command Surface and Sidecar Boundary Hardening
kind: implementation
status: proposed
release_state: NOT_RELEASED
approval: pending_user_review
execution_approval: not_authorized
suggested_owner: ZCode
owner: null
reviewer: null
depends_on: [M2-RC1]
base_commit: null
branch: null
worktree: null
integration_commit: null
---

# M2-RC2 — Resource Channel Command Surface and Sidecar Boundary Hardening

## 来源与目标

承接 [M2-RC1 Handoff](../handoffs/M2-RC1-FIX-702b02b0.md) 与 DSH `accepted_deferral`：F-03（命令面收敛、capability/ACL/CSP 与 catalog authority 回到 Core/SQLite）及 F-05（为 Python Core resource channel 提供独立 sidecar 入口，避免 `src.infrastructure` 包级传递导入）。目标是先冻结安全边界和可观察的隔离行为，再为后续单独授权实现作准备；登记本 Task 不代表执行授权。

## Acceptance Criteria

- [ ] **RC2-AC1 命令面收敛（F-03）**：确认 `register_catalog`、`probe_*`、`ttl_override` 的生产暴露面；在 Tauri capability、ACL/CSP 与 Core 权威边界下，WebView 不得提交 OS 路径、任意 TTL 或可伪造的 catalog 状态；catalog 生命周期由 Core/SQLite 管理。提供可判别的授权与拒绝测试。
- [ ] **RC2-AC2 独立 sidecar 入口（F-05）**：resource-channel sidecar 可由最小独立入口启动，避免导入 `src.infrastructure` 包时的无关传递依赖；提供 headless/import 边界测试并记录实际加载模块。
- [ ] **RC2-AC3 诚实 Gate 与证据**：覆盖新增命令/sidecar 边界回归；将 S1-B3/B5/B6/B8 未验证项保持 `UNVERIFIED`/`NOT_RUN`，不宣称产品级安全、安装或打包就绪；Handoff 明确列出仍需独立验证的条件。

## 允许修改范围（拟议；释放时由 Codex 冻结）

- `apps/desktop/src-tauri/**`：仅命令注册、capability、ACL/CSP 与对应测试。
- `src/application/resource_channel/**`、`src/infrastructure/resource_channel/**`：仅 catalog 所有权和 sidecar 接线所需改动。
- `src/infrastructure/__init__.py`：仅在隔离入口证明确有必要时，由 Codex 在释放时明确授权。
- `tests/m2_resource_channel/**`、`verification/M2-RC2/**`、本 Task 与正式 Handoff。

## 禁止范围

不修改共享 Contract、SQLite schema/migrations、Legacy QML、用户源文件、根依赖/锁文件或打包发布面；不以此 Task 关闭 S1-B3/B5/B6/B8，也不作产品级安全声明。当前 `proposed / NOT_RELEASED`，须经 Codex 单独冻结 base、授权路径、分支/worktree、Reviewer 与测试 Gate 后才可执行。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| RC2-AC1 command boundary | 按释放时冻结的 Tauri/Core 集成测试 + WebView invoke deny/allow 矩阵 | Windows；仅合成资源 | NOT_RUN（未释放） | 无 |
| RC2-AC2 sidecar isolation | 独立进程启动/导入跟踪与 resource-channel focused suite | 固定 released tree | NOT_RUN（未释放） | 无 |
| RC2-AC3 honest gates | 对照 S1-B3/B5/B6/B8 状态及 Handoff | Review 后 | NOT_RUN（未释放） | 无 |

## 依赖、风险与阻塞

硬依赖：[M2-RC1](M2-RC1.md) 集成完成。F-03 的具体 command/capability 边界与 catalog 持久化形态须在释放 Task 时明确；任何 Schema 变化须另行裁决。S1-B3/B8 的产品级安全边界继续有效。

## 交付与运行记录

- 状态：`proposed / NOT_RELEASED`；Owner 建议 ZCode，Reviewer 建议 DeepSeek Harness（非作者），Codex Integrator。
- 来源：M2-RC1 F-03/F-05 `accepted_deferral`；本提案不构成 branch/worktree 或实现授权。