---
id: HOST-CORE-1
title: Core 侧 HostControl handler 实现（host-only session 握手与 grant 注册/撤销路由）
kind: feature
governance_version: 2
status: ready
approval: coordinator_release_20261016_core_hostcontrol_handler
suggested_owner: Codex
owner: null
reviewer: null
depends_on: [HOST-ISSUER-1-C1, P09-FU2, P16]
base_commit: dd1cda8bdc27638c970356fb3a4dbc49f35c81e2
branch: codex/HOST-CORE-1-hostcontrol-handler
worktree: G:/CODEX/New Manga.workspace/worktrees/HOST-CORE-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/HOST-CORE-1
---

# HOST-CORE-1：Core 侧 HostControl handler 实现

## 来源与目标

- 来源：**HOST-ISSUER-1 的第二次阻塞**（Owner 于 2026-10-16 实证）+ **契约 §12 的既有授权**。
- **缺口事实（已核验）**：
  1. `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` **rev 2.3 §12** 原文：
     "**§12 仅授权最小 Core handler/session 改动与 `tests/core/**`**，**本次不实现 runtime**"
     —— 即前置契约 `HOST-ISSUER-1-C1` **授权**了 Core 侧实现，但**未实现**它；
  2. `src/bootstrap/core_service.py` 对 `HostControl` / `OpenHostSession` / `HOST_ONLY_REQUIRED` 的命中数为 **0**
     —— **没有接收路由**，HostControl 请求当前会被当作未知命令（`UNKNOWN_COMMAND`）拒绝；
  3. 私有 seam **已存在**：`_register_export_target`(L1491) / `_revoke_export_target`(L1509) /
     `_register_import_source`(L1515) / `_revoke_import_source`(L1551)；
  4. Rust 侧 `library_bridge.rs` 仍发送 protocol `1.4` 的**普通请求**，无法承载 HostControl。
- 目标：在 Core 侧实现 §5.7 冻结的 **HostControl** 接收面与 session 语义，并把注册/撤销**路由到既有私有 seam**，
  从而使 **HOST-ISSUER-1**（Rust 侧签发）有可对接的 live Core 接收端。
- **Coordinator 自述（透明记录）**：本 Task 的缺失源于 Coordinator 在恢复 HOST-ISSUER-1 时的**规划疏漏**
  （只确认"契约已冻结"，未确认"handler 已实现"）与 prompt 错误（把 `src/**` 误写为只读，而 §12 明确授权 Core 改动）。
  本 Task 即为纠正该疏漏。

## Acceptance Criteria

- [ ] AC1 **HostControl 接收面**：实现 §5.7 的独立 `HostControl` envelope 接收与解析（经 Tauri host **direct-child stdio** 通道），
      **不进入** §3 普通 application `Request<T>` command catalog；字段与 §5.7 定义**严格一致**。
- [ ] AC2 **session 握手与失效**：实现 `OpenHostSession` 与 `CloseHostSession`；
      Core 为每个进程生成新的 `core_session_id`；校验 host 持有的 `host_session_credential` 与 `host_session_id`；
      **关闭/轮换即撤销该 session 的 grants**；Core 重启丢弃进程内 registry（与 §5.7 一致）。
- [ ] AC3 **注册/撤销路由到既有私有 seam**：`RegisterImportSource` / `RevokeImportSource` /
      `RegisterExportTarget` / `RevokeExportTarget` 路由到既有 `_register_*` / `_revoke_*` 方法；
      **不得**改变 `ImportSourceRef` / `ExportTargetRef` 的字段、签名输入或既有 `REF_*` 语义（§10.3/§10.4 不变）。
- [ ] AC4 **三拒绝码**：普通 JSON-RPC 调用 host-only 操作 → **`HOST_ONLY_REQUIRED`**（validation）；
      credential 缺失/错误或 session 已关闭 → **`HOST_SESSION_INVALID`**（conflict）；
      `core_session_id` 不符 → **`CORE_SESSION_MISMATCH`**（conflict）；
      三者均**"拒绝；不调用 seam"**（须有可证伪的负向断言）。
- [ ] AC5 **普通 dispatcher 不承认 host-only 命令**：给出**负向证据**证明这些命令**不在**普通 JSON-RPC 路由中。
- [ ] AC6 **范围锁定（严格）**：变更**仅限** `src/bootstrap/core_service.py` 与 `tests/core/**`
      （如确需 `core_assembly.py` 的装配改动，须在证据中单列理由）；
      **不得**改 Schema/migration、依赖、其他 Python 模块、`apps/**` 或契约。
- [ ] AC7 **测试**：在 `tests/core/**` 新增/扩展用例覆盖 AC1–AC5，含**拒绝零副作用**与**session 失效后 grant 立即失效**的断言；
      归档**原始日志与退出码**。
- [ ] AC8 固定 head 非作者 Review、Coordinator 集成；未跑项标 `NOT_RUN` / `BLOCKED`。

## 允许修改范围

- `src/bootstrap/core_service.py`
- `src/bootstrap/core_assembly.py`（**仅在**装配 host session/registry 所必需时；须单列理由）
- `tests/core/**`
- 本 Task（`doc/tasks/HOST-CORE-1.md`）、`doc/handoffs/HOST-CORE-1-*.md`、`verification/HOST-CORE-1/**`
- 只读引用：`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`（**§5.7 为实现依据**）、
  `doc/tasks/HOST-ISSUER-1.md`、`verification/HOST-ISSUER-1/**`、`verification/HOST-ISSUER-1-C1/**`、
  `verification/P09-FU2/**`、`verification/P16/**`。

写入仅限本 Task worktree `G:/CODEX/New Manga.workspace/worktrees/HOST-CORE-1`；**禁止原位覆盖主仓任何文件**。

## 禁止范围

- **不得修改** `doc/contracts/**`（rev 2.3 已冻结）；若发现契约不足 → **停止**并转 `BLOCKED_WAITING_EXTERNAL_DECISION`。
- **不得修改** `apps/**`（Tauri/Rust 侧属 HOST-ISSUER-1）、Schema/migration、第三方依赖。
- **不得**把 HostControl 暴露到 WebView 可调用面；**不得**把 host-only 命令加入普通 dispatcher 路由。
- 不改变 §10.3/§10.4 的 ref 字段与 `REF_*` 语义；不降低既有安全强度。
- 不触碰用户数据、主仓 dirty/untracked、既有 worktree；不 push、不 merge（集成由 Coordinator 执行）。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 envelope 解析 | `pytest tests/core -q` 定向用例 | task-env py312 | NOT_RUN | 无 |
| AC2 session 握手/失效 | Open/Close、轮换后 grants 失效 | task-env py312 | NOT_RUN | 无 |
| AC3 路由到既有 seam | 注册后既有 ref 可被消费；字段与 §10.3/§10.4 一致 | task-env py312 | NOT_RUN | 无 |
| AC4 三拒绝码 | 逐类拒绝 + "未调用 seam" + 零副作用 | task-env py312 | NOT_RUN | 无 |
| AC5 dispatcher 不承认 | 普通 JSON-RPC 调用这些命令 → 非成功路径的负向断言 | task-env py312 | NOT_RUN | 无 |
| AC7 回归 | `pytest tests/core -q` 全绿 | task-env py312 | NOT_RUN | 无 |

## 依赖、风险与阻塞

- `depends_on`：`HOST-ISSUER-1-C1`（`done`，§5.7 契约已集成）、P09-FU2（`done`，导入 seam 与 `user-source` scope）、P16（`done`，导出 seam）。
- 风险一（安全，最高）：**host-only 边界必须真的"不进入普通 dispatcher"**；若实现成"普通命令 + 权限位"，即违反 §5.7 与 §10.3/§10.4。
- 风险二（范围）：本 Task **不得**顺手改 Rust/Tauri 侧（那是 HOST-ISSUER-1），也不得改契约。
- 风险三（并发）：HOST-ISSUER-1 当前 `blocked` 且其分支未集成；本 Task 集成后 HOST-ISSUER-1 才能恢复（Coordinator 负责 merge 基线）。
- 阻塞：无预期。

## 交付与运行记录

- 2026-10-16 Coordinator 释放（dsh, epoch 5）：base=`dd1cda8bdc27638c970356fb3a4dbc49f35c81e2`；
  依据契约 §12 的既有授权 + HOST-ISSUER-1 的实证缺口（`core_service.py` 的 HostControl 命中数为 0）；
  **本 Task 同时纠正 Coordinator 在恢复 HOST-ISSUER-1 时的规划疏漏与 prompt 约束错误**；Owner 按 DIR-2 路由为 **codex**。
- Handoff：尚无。
- Review：尚无。
- 实际测试：尚无（全部 `NOT_RUN`）。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/HOST-CORE-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/HOST-CORE-1 | verification/HOST-CORE-1/resource-manifest.json | 拟议新增；由 Owner 认领时创建；closeout 时补写 manifest |

## Closeout Record

- Closeout date / Codex：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写；无操作填写 0。
- 未关闭项及保留原因：本 Task 全部 AC 尚未执行（`NOT_RUN`）。
- 当前指针清理：`STATUS` / `REBASELINE_PLAN` / 本 Task 导航在释放时同步。
