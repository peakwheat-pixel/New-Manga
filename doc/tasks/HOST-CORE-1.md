---
id: HOST-CORE-1
title: Core 侧 HostControl handler 实现（host-only session 握手与 grant 注册/撤销路由）
kind: feature
governance_version: 2
status: done
approval: coordinator_release_20261016_core_hostcontrol_handler
suggested_owner: Codex
owner: codex
reviewer: dsh
depends_on: [HOST-ISSUER-1-C1, P09-FU2, P16]
base_commit: ed79b76f9191f0a5ebb6932a53a992a33a274041
branch: codex/HOST-CORE-1-hostcontrol-handler
worktree: G:/CODEX/New Manga.workspace/worktrees/HOST-CORE-1
integration_commit: 67ee4a585af33875ccf0d0992863612c7b147e2d
delivery_head: c97b2d125bd765bdfae3ec93bc440a7ba6d595c2
canonical_evidence_status: complete
resource_closeout_status: complete
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

- [x] AC1 **HostControl 接收面**：实现 §5.7 的独立 `HostControl` envelope 接收与解析（经 Tauri host **direct-child stdio** 通道），
      **不进入** §3 普通 application `Request<T>` command catalog；字段与 §5.7 定义**严格一致**。
- [x] AC2 **session 握手与失效**：实现 `OpenHostSession` 与 `CloseHostSession`；
      Core 为每个进程生成新的 `core_session_id`；校验 host 持有的 `host_session_credential` 与 `host_session_id`；
      **关闭/轮换即撤销该 session 的 grants**；Core 重启丢弃进程内 registry（与 §5.7 一致）。
- [x] AC3 **注册/撤销路由到既有私有 seam**：`RegisterImportSource` / `RevokeImportSource` /
      `RegisterExportTarget` / `RevokeExportTarget` 路由到既有 `_register_*` / `_revoke_*` 方法；
      **不得**改变 `ImportSourceRef` / `ExportTargetRef` 的字段、签名输入或既有 `REF_*` 语义（§10.3/§10.4 不变）。
- [x] AC4 **三拒绝码**：普通 JSON-RPC 调用 host-only 操作 → **`HOST_ONLY_REQUIRED`**（validation）；
      credential 缺失/错误或 session 已关闭 → **`HOST_SESSION_INVALID`**（conflict）；
      `core_session_id` 不符 → **`CORE_SESSION_MISMATCH`**（conflict）；
      三者均**"拒绝；不调用 seam"**（须有可证伪的负向断言）。
- [x] AC5 **普通 dispatcher 不承认 host-only 命令**：给出**负向证据**证明这些命令**不在**普通 JSON-RPC 路由中。
- [x] AC6 **范围锁定（严格）**：变更**仅限** `src/bootstrap/core_service.py` 与 `tests/core/**`
      （如确需 `core_assembly.py` 的装配改动，须在证据中单列理由）；
      **不得**改 Schema/migration、依赖、其他 Python 模块、`apps/**` 或契约。
- [x] AC7 **测试**：在 `tests/core/**` 新增/扩展用例覆盖 AC1–AC5，含**拒绝零副作用**与**session 失效后 grant 立即失效**的断言；
      归档**原始日志与退出码**。
- [x] AC8 **PARTIAL**：实现 head 已固定并有 Handoff；非作者 Review 与 Coordinator 集成尚为 `NOT_RUN`，Task 保持 `in_review`。

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
| AC1 envelope / AC3 seam 路由 | `G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe -m pytest tests/core -q` | Python 3.12.3；`ff42c670` | PASS：stdio 握手、四个 seam、ref 解析/撤销、两种规范 Base64URL credential | `verification/HOST-CORE-1/ac-matrix.md` |
| AC2 session 握手/失效 | Open/Close、EOF、真实 Core 子进程重启 | Python 3.12.3；`ff42c670` | PASS：关闭后 `REF_REVOKED`；重启后新 ID 与旧 ref `REF_UNKNOWN_ID` | `verification/HOST-CORE-1/ac2-session-lifecycle.md` |
| AC4 三拒绝码 | 逐类拒绝 + "未调用 seam" + SQLite/registry/文件快照 | Python 3.12.3；`ff42c670` | PASS：零副作用，exit 0 | `verification/HOST-CORE-1/ac4-denials.md` |
| AC5 dispatcher 不承认 | 六个 host-only command 通过普通 JSON-RPC 负向断言 | Python 3.12.3；`ff42c670` | PASS：逐项 `HOST_ONLY_REQUIRED` | `verification/HOST-CORE-1/ac5-dispatcher-negative.md` |
| AC7 全量回归 | `python -m pytest tests/core -q` | 指定 task-env Python 3.12.3；`ff42c670` | PASS：395 passed / 0 failed / 1 既有 warning；exit 0 | `verification/HOST-CORE-1/pytest-tests-core.log` |

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
- **Owner Reality Check**：用户指定本 worktree 实际基线 `ed79b76f9191f0a5ebb6932a53a992a33a274041`，执行前 HEAD 与其一致；Task 释放元数据的 `dd1cda8...` 未作为本分支基线，未执行 reset。
- **文档现状差异**：`doc/00_INDEX.md` 列出的 `tools/governance/check.ps1` 在本 worktree 不存在（仅有 `verification/PROJECT-ROADMAP-RELEASE/inputs/tools/governance/check.ps1` 历史输入）；本 Task 未声称运行该检查。
- 实现提交：`4af86abb374cfccf92de07d4e5b975dfbaf0dd2b`；Base64URL credential 互操作修正：`ff42c670122a95c5edd43b6374e4e42bf42731cb`；证据与 Handoff 提交：`97c2d559c6155375ce67da7da922d62a26971100`。
- Handoff：`doc/handoffs/HOST-CORE-1-codex-ff42c670.md`；当前 Task 状态 `in_review`。
- Review：指定 Reviewer `dsh`；非作者 Review 尚未运行（`NOT_RUN`）。
- Coordinator integration：尚未运行（`NOT_RUN`）；未 push、未 merge。
- 实际测试：Python 3.12.3 task-env，完整 Core suite **395 passed / 0 failed / exit 0**；唯一 warning 为既有 Pillow `Image.Image.getdata` deprecation。原始日志：`verification/HOST-CORE-1/pytest-tests-core.log`。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| HOSTCORE-AC-MATRIX | AC1–AC8 | `verification/HOST-CORE-1/ac-matrix.md` | `97c2d559c6155375ce67da7da922d62a26971100` | `4da5e5c508cead1f2c3c23bd7ee8164ea267876194331b86b0044e1c79e83a7e` | CANONICAL |
| HOSTCORE-AC2-SESSION | AC2 | `verification/HOST-CORE-1/ac2-session-lifecycle.md` | `97c2d559c6155375ce67da7da922d62a26971100` | `adf75e717c05260c548ad041c28e83cbf88c7550ceaeacb1b2c2a2301032c1fe` | CANONICAL |
| HOSTCORE-AC4-DENIALS | AC4 | `verification/HOST-CORE-1/ac4-denials.md` | `97c2d559c6155375ce67da7da922d62a26971100` | `f0c953d59ce7fff3a9c96634e39144902a8cea6ca31c71e641b9dcd5beb4dad8` | CANONICAL |
| HOSTCORE-AC5-DISPATCHER | AC5 | `verification/HOST-CORE-1/ac5-dispatcher-negative.md` | `97c2d559c6155375ce67da7da922d62a26971100` | `f2a8289d71e70a61ec15eea2e24a1b67e67099d7842c25e54f28b3825b8f5a96` | CANONICAL |
| HOSTCORE-CORE-SUITE | AC1–AC7 | `verification/HOST-CORE-1/pytest-tests-core.log` | `97c2d559c6155375ce67da7da922d62a26971100` | `96bec7d0fc2690ce51db0b5164380113955d1a9d8db396814c9b16e398f1f36b` | CANONICAL |
| HOSTCORE-TEST-SOURCE | AC1–AC5 | `tests/core/test_host_control.py` | `97c2d559c6155375ce67da7da922d62a26971100` | `7e4fc78cdfa34e9ff9b87b45e6448f326d4ed18a620adfe432859bf4f4fcf9c0` | CANONICAL |
| HOSTCORE-SCOPE | AC6 | `verification/HOST-CORE-1/scope-audit.md` | `97c2d559c6155375ce67da7da922d62a26971100` | `8c44349c14684e83cdc6f48b559ad2eb6d2332b8a38c5e91a6035f480152b7a7` | CANONICAL |
| HOSTCORE-HANDOFF | AC8 | `doc/handoffs/HOST-CORE-1-codex-ff42c670.md` | `97c2d559c6155375ce67da7da922d62a26971100` | `9f2eef0764c387fa2b69d4fb9a0332238936aede8548af71b3032a20e39032e8` | CANONICAL |
| HOSTCORE-RESOURCES | Resource | `verification/HOST-CORE-1/resource-manifest.json` | `97c2d559c6155375ce67da7da922d62a26971100` | `f7545186d829ddcc24787b2eb90f7b730888d4522a0eb679e4130dcd4f6be9fe` | CANONICAL |
| HOSTCORE-C1-PIN | §5.7 / §10.3 / §10.4 / §12 source | `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` | `97c2d559c6155375ce67da7da922d62a26971100` | `6a2f38e0b17062d9d4f1d6ee109b4353b745504a5a6b889148781eee84fa2062` | SOURCE_PIN |
| EVD-HOSTCORE1-REVIEW-R1 | AC8 | `verification/HOST-CORE-1/dsh-review-r1.md` | `237a662c701d98751f155a2b55f669eee51d8643` | `cd864e86b82047e7a1afba87c25f30fe08e7873eeef81dad6fc9e82490c6970e` | CANONICAL |

注：Task 文件自身不列入自身 hash 表，以避免自引用；每个 evidence commit 均为包含对应路径的真实 commit，SHA-256 按工作区文件值记录。

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/HOST-CORE-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/HOST-CORE-1 | `verification/HOST-CORE-1/resource-manifest.json` | 分支和 worktree 保留给 Reviewer / Coordinator；未删除、迁移或归档 |
| test-env | G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312 | PRESERVE_REFERENCED | G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312 | `verification/HOST-CORE-1/resource-manifest.json` | 只读调用现有 Python 3.12.3；未安装或更新依赖 |

## Closeout Record

- Closeout date / Coordinator：2026-10-16，dsh（epoch 5，lease `264c2000541748298000f93fb25a52de`）。
- canonical_evidence_status：`complete`；resource_closeout_status：`complete`（worktree `PRESERVE_REFERENCED`；0 删除 / 0 迁移 / 0 归档）。
- **结果**：Core 侧 **HostControl 接收端已实现**。实现 `4af86abb`（含 `ff42c670` 修复），归档 `c97b2d125`，集成 merge=`67ee4a58`；
  **`tests/core` 395 passed / 0 failed / exit 0**。
- **AC1**：`HostControl` 为**独立命令集**（`_HOST_CONTROL_COMMANDS`），请求形态为
  `host_session_id` / `host_session_credential` / `command` / `payload`，**不进入**普通 `Request<T>` catalog。
- **AC2**：`OpenHostSession` / `CloseHostSession` 与 `_host_session_credential` 生命周期；
  **关闭后 grant 立即 `REF_REVOKED`**；**真实子进程重启测试**验证 session ID 变化且旧 ref → `REF_UNKNOWN_ID`。
- **AC3**：四个注册/撤销命令路由到**既有私有 seam**；ref 字段与 `REF_*` 语义**未改**。
- **AC4（安全 Gate）**：三拒绝码 `HOST_ONLY_REQUIRED` / `HOST_SESSION_INVALID` / `CORE_SESSION_MISMATCH`
  每例均断言 **`calls == []`（未调用 seam）**，并叠加 **SQLite `total_changes`**、**registry grant ID 集合**、
  **隔离目录文件 SHA-256 快照**三者**不变**；响应 `result: null` 且**不泄露路径或 credential**。
- **AC5**：六个 host-only 命令经普通 JSON-RPC 调用**全部**返回 `HOST_ONLY_REQUIRED`，非成功路由；命令白名单另行收紧。
- **AC6**：17 路径全在 §12 授权内；**未碰** `apps/**`（Rust/Tauri）与 `doc/contracts/**`。
- **AC8 已闭合**：独立 Review=`237a662c`（`approved`，reviewed_head=`c97b2d125`）。
- **本 Task 的由来（透明备案）**：HOST-ISSUER-1 的**第二次阻塞**指出——C1 契约 §12 **只授权**"最小 Core handler/session 改动"却
  **从未实现**它，`core_service.py` 的 HostControl 命中数为 0。Owner 的判断**正确**；Coordinator 亦已备案自身
  **规划疏漏**（只确认"契约已冻结"、未确认"handler 已实现"）与 **prompt 约束错误**（误把 `src/**` 写为只读）。
- **遗留（Review F3/F4）**：本 Task 只交付 **Core 侧**；**Rust/Tauri 侧签发与真实联调属 HOST-ISSUER-1**（分支未集成），
  **不得**据此声称 host issuer 已端到端可用。
- **新登记债务（Review F2 → BL-12）**：**`tools/governance/check.ps1` 未被 Git 跟踪**，
  导致**任何 fresh worktree 都无法运行治理检查**（Owner 在 worktree 中正确地无法运行并如实说明）。
  该项削弱**所有** worktree 级 Task 的自检能力，建议尽快单独处置。
- 交付 head 冻结（Review F1）：Owner 申报 `delivery_head=ff42c670`（实现提交），实际 HEAD=`c97b2d125`；已冻结为实际值。
- 当前指针清理：`doc/STATUS.md` / `doc/REBASELINE_PLAN.md` 已同步为 HOST-CORE-1 `done`。