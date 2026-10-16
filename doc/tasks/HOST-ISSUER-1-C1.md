---
id: HOST-ISSUER-1-C1
title: host→Core grant 注册通道契约（host-only 注册/撤销 wire 与 session 绑定）
kind: design
governance_version: 2
status: ready
approval: coordinator_release_20261016_resolution_for_host_issuer_blocker
suggested_owner: Codex
owner: null
reviewer: null
depends_on: [P09-FU2, P16]
base_commit: 2eaa3241295e1f483eabf640289a4bea4126370c
branch: codex/HOST-ISSUER-1-C1-grant-registration-contract
worktree: G:/CODEX/New Manga.workspace/worktrees/HOST-ISSUER-1-C1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/HOST-ISSUER-1-C1
---

# HOST-ISSUER-1-C1：host→Core grant 注册通道契约

## 来源与目标

- 来源：**HOST-ISSUER-1 的 `BLOCKED_WAITING_EXTERNAL_DECISION`**
  （`verification/HOST-ISSUER-1/blocker-assessment.md`，Owner 实现 head：无；分支 `codex/HOST-ISSUER-1-tauri-ref-issuer`）。
  Owner 以**代码事实**证明：可信 host **没有任何通道**把 grant 注册进**运行中的** Core。
- **缺口事实（Owner 实证，Coordinator 已复核）**：
  1. `src/bootstrap/core_service.py` 的 `_register_export_target` / `_revoke_export_target` / `_register_import_source` /
     `_revoke_import_source` 是 **live `CoreServiceServer` 的私有方法**，**未出现在 dispatcher 路由**中；
  2. Core JSON-RPC 已路由 `ImportPages` / `StartExport`，但**没有**注册/撤销命令；
  3. `src/bootstrap/core_assembly.py` 为**该 Core 实例**在内存中构造 import/export grant registry；
     第二个进程或既有 `host_bridge` sidecar **无法填充 live registry**；
  4. `apps/desktop/src-tauri/src/core_bridge.rs` 只与 resource-channel sidecar 通信（`ping/issue/resolve/touch/revoke/...`），
     **不持有** Import/Export grant registry；
  5. 把注册暴露为 **WebView 可调用**命令会**破坏** §10.3/§10.4 的受信 host 边界。
- **契约状态**：`M2-C1` §11 明确把 `Runtime serialization library, Tauri command names, process supervision,
  **auth/permission handshake**` 标为 **`UNKNOWN / NOT_IN_SCOPE`** —— 本 Task 正是要**冻结这项遗留**。
- 目标：冻结一个**窄范围、host-only** 的 grant 注册/撤销 wire 与 session 绑定语义，
  使 HOST-ISSUER-1 能实现"用户选择 → host 签发 → 注册受信 grant → 注入 Core → Core 校验并消费"。
  本 Task **只做契约设计**，不实现 runtime、不改产品代码。

## Acceptance Criteria

- [ ] AC1 **host-only 注册/撤销命令的 wire**：定义注册（导入来源 / 导出目标）与撤销命令的
  request/result 与错误面；命令**仅存在于 host↔Core 通道**，**MUST NOT** 由 WebView/React 调用；
  在 wire 层显式表达"host-only"（例如 host session 凭证/通道限定），并说明 Core 如何**拒绝**非 host 调用。
- [ ] AC2 **session 绑定与失效语义**：定义 grant 与 Core session 的绑定；Core 重启/关闭、host session 失效或轮换时
  grant 的**失效**语义；以及撤销（revoke）的即时性要求。
- [ ] AC3 **与 §10.3/§10.4 的 ref 语义一致**：注册产生的 grant 与既有 `ImportSourceRef`（§10.4）/
  `ExportTargetRef`（§10.3）**严格对应**；**不得**新增或改变 ref 字段；不得改变既有 `REF_*` 拒绝码语义。
- [ ] AC4 **错误面完整且可判定**：重复注册、未知 grant、session 不符、scope 越界、过期/已撤销等均有稳定错误；
  拒绝时**零副作用**（不得写入库、不得写目标文件）。
- [ ] AC5 **§12 授权边界**：明确授权**实现该通道所必需的 Core 侧最小改动**（窄 allowlist），
  并排除 React/WebView、Tauri command 面向 WebView 的暴露、Schema/migration、依赖与其他产品行为。
- [ ] AC6 **覆盖对照**：产出与 HOST-ISSUER-1 的 AC1–AC7、以及 §10.3/§10.4、§5.6 的逐条对照，
  证明新 wire **足以**让 host 完成签发与注入，且**不发明产品行为**。
- [ ] AC7 **不越界**：除本契约文件外不改任何文件；不实现 runtime；不改 P11 / P13-C1 / P16-C1 / P12-C1 已冻结的 wire 语义。
- [ ] AC8 固定 head 非作者 Review、Coordinator 集成；未完成项标 `NOT_RUN`。

## 允许修改范围

- **唯一契约文件**：`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`（本 Task 的显式修订授权）。
- 本 Task（`doc/tasks/HOST-ISSUER-1-C1.md`）、`doc/handoffs/HOST-ISSUER-1-C1-*.md`、`verification/HOST-ISSUER-1-C1/**`。
- 只读引用：`doc/tasks/HOST-ISSUER-1.md`、`verification/HOST-ISSUER-1/**`、`doc/tasks/P09-FU2.md`、`doc/tasks/P16.md`、
  `src/bootstrap/core_service.py`、`src/bootstrap/core_assembly.py`、`src/infrastructure/resource_channel/**`、
  `apps/desktop/src-tauri/src/{core_bridge,library_bridge}.rs`、`doc/09_COLLABORATION.md`。
- 写入仅限本 Task worktree `G:/CODEX/New Manga.workspace/worktrees/HOST-ISSUER-1-C1`；禁止原位覆盖主仓任何文件。

## 禁止范围

- 不实现 runtime / 产品代码（`src/**`、`apps/**`、`packaging/**` 只读）；不改 Schema/migration；不新增依赖。
- **不得**设计任何"WebView 可调用注册命令"的方案（直接违反受信 host 边界）。
- 不修改 `P11_LONG_TASK_LIFECYCLE_CONTRACT.md`；不改变 P13-C1/P16-C1/P12-C1 已冻结 wire。
- 不触碰 Legacy、用户数据、主仓 dirty/untracked、既有 worktree；不 push、不 merge（集成由 Coordinator 执行）。
- 若注册通道的**产品级**语义需要取舍（例如 grant 上限、是否允许多来源同时注册），**停止**并转
  `BLOCKED_WAITING_EXTERNAL_DECISION`。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 host-only 边界 | 对照 §10.3/§10.4 与现状，核对"WebView 不可调用"如何被表达与拒绝 | 只读 | NOT_RUN | 无 |
| AC2 session 绑定 | 定义失效/轮换/关闭语义 | 只读 | NOT_RUN | 无 |
| AC3 ref 一致性 | 逐字段核对不新增/不改变 | 只读 | NOT_RUN | 无 |
| AC4 错误面 | 逐类错误与零副作用 | 只读 | NOT_RUN | 无 |
| AC5 授权边界 | 检查 §12 窄 allowlist | 只读 | NOT_RUN | 无 |
| AC6 覆盖充分性 | HOST-ISSUER-1 AC1–AC7 逐条映射 | 只读 | NOT_RUN | 无 |

## 依赖、风险与阻塞

- `depends_on`：P09-FU2（`done`，Core 侧 seam 与 `REF_*` 校验）、P16（`done`，`ExportTargetRef` Core 侧校验）。
- 风险一（安全，最高）：该通道一旦被 WebView 触达，**任何** grant 都可被伪造 → 必须设计为**host-only**并给出拒绝机制。
- 风险二（范围）：Core 侧改动必须**最小**（只补路由与 session 绑定），不得借机重构或扩大命令面。
- 风险三（并发写）：本 Task 与 **HOST-ISSUER-1** 都涉及 `core_service.py` 的**不同**改动面；
  HOST-ISSUER-1 当前 `blocked` 且未集成，**本 Task 完成并集成后**才恢复它（Coordinator 负责 merge 基线）。
- 阻塞：无预期。

## 交付与运行记录

- 2026-10-16 Coordinator 释放（dsh, epoch 5）：作为 **HOST-ISSUER-1 阻塞的 resolution**（同 P13-C1/P16-C1/P12-C1 模式）；
  base=`2eaa3241295e1f483eabf640289a4bea4126370c`；Owner 按 DIR-2 路由为 **codex**（契约/架构主责）。
- Handoff：尚无。
- Review：尚无。
- 实际测试：尚无（全部 `NOT_RUN`）。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/HOST-ISSUER-1-C1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/HOST-ISSUER-1-C1 | verification/HOST-ISSUER-1-C1/resource-manifest.json | 拟议新增；由 Owner 认领时创建；closeout 时补写 manifest |

## Closeout Record

- Closeout date / Codex：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写；无操作填写 0。
- 未关闭项及保留原因：本 Task 全部 AC 尚未执行（`NOT_RUN`）。
- 当前指针清理：`STATUS` / `REBASELINE_PLAN` / 本 Task 导航在释放时同步。
