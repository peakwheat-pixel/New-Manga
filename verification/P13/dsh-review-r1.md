---
task_id: P13
title: 后台恢复（Run 接线 → 控制 → 恢复）
reviewer: dsh（项目权威 Reviewer，`.orchestrator/tasks/P13-role.json`；role_exclusion 已排除 owner=codex）
owner: codex
base_commit: 11d14c4d42472e1fd0af4af80d5526f2215325c7
declared_delivery_head: 78b0d439a819f55c8e7a97ad2a09d9e066a08a80
reviewed_head: 8056ee63e0b1b5a25b64ef9e85bb8e8e54282dba
review_worktree: G:/CODEX/New Manga.workspace/worktrees/P13-RUN-RUNTIME
date: 2026-10-16
mode: 只读审查 + 独立 Git/测试日志/实现抽查复核；未修改被审分支或主仓任何文件
object_binding: VERIFIED
scale: 大规模变更（25 路径，含协议 major bump、新 SQLite 账本表、16 个新增用例）
decision: approved
---

# P13 独立 Review（R1）

## 0. 复核结果（未采信自述）

| 项 | 方式 | 结果 |
|---|---|---|
| 变更范围 | `git diff --name-only 11d14c4d..HEAD` | **25 个路径，全部在授权范围** |
| **冻结契约完好** | 过滤 `M2-C1_TYPED_IPC_CONTRACT`/`P11_LONG_TASK` | **两者均未被修改** ✅ |
| 越界路径 | 反向过滤 allowlist | **空** ✅（未动 P14 UI、未改其他模块、未加依赖） |
| worktree / 主仓 | `git status` | worktree **clean**；主仓 **19 项 dirty 未变** |
| 完整测试集 | 独立读原始日志 | `tests/core`：**340 passed / 0 failed，exit 0**；P13 定向：**79 passed，exit 0** |
| AC4 判别 | 读 before / after / sqlite 日志 | before **4 failed exit 1** → after **4 passed exit 0**；SQLite restart 回滚用例 **1 passed exit 0** |
| SQLite 变更性质 | diff 过滤 `SCHEMA_VERSION` + 读 `migration-boundary.md` | **未改 schema version**；为 additive 幂等 `CREATE TABLE IF NOT EXISTS` |

## 1. AC 逐项结论

| AC | 判定 | 依据（抽查） |
|---|---|---|
| AC1 durable 幂等 | **接受** | 实现含 `_require_idempotency_key`/`_request_fingerprint`/`_scope_fingerprint`；测试 `test_sqlite_start_acceptance_is_atomic_idempotent_and_freezes_targets`、`test_sqlite_acceptance_rolls_back_run_targets_and_key_together`、`test_start_run_wire_uses_key_separate_from_request_id_and_returns_snapshot`（**key 与 `request_id` 分离**，符合契约 §3.1/§4） |
| AC2 快照与目标冻结 | **接受** | 同上用例断言接受时冻结目标顺序；`p11-section-matrix-20261016.md` 逐节对照 |
| AC3 唯一 scheduler owner | **接受** | 实现含 `require_scheduler_owner`/`set_scheduler_owner`/`_ensure_scheduler_owner`（非 owner 写入抛 `INVALID_RUN_TRANSITION`）；测试 `test_core_run_owner_uses_worker_thread_connection_and_blocks_direct_bypass`、**`test_kernel_scheduler_lease_excludes_a_second_process`**（复用 GC-2 内核租约先例做跨进程互斥） |
| AC4 控制转换（4 项破坏性修正） | **接受** | 四项判别用例 `test_pending_pause_is_rejected_without_mutation` / `test_blocked_stop_reaches_cancelled_terminal_state` / `test_restart_failure_does_not_leave_child_without_parent_disposition` / `test_retry_failed_targets_requires_completed_with_failures`：改前 4 failed → 改后 4 passed；`restart` 另有真实 SQLite 事务回滚用例 |
| AC5 重试边界 | **接受** | `test_retry_policy_uses_two_bounded_retries_and_fail_closed_codes`、**`test_retry_after_is_not_capped_and_runtime_version_is_major_two`**（退避/上限/不截断 `Retry-After` + 协议 major） |
| AC6 启动恢复 | **接受** | `test_recovery_only_interrupts_running_and_continue_replays_open_step`、`test_continue_keeps_a_safely_committed_step_without_replaying_it`、`test_sqlite_step_commit_keeps_current_and_step_state_atomic` |
| AC7 投影与事件 | **接受** | `test_projection_is_same_run_source_and_never_exposes_error_detail`（**不泄露 error detail**，符合契约 §6.1 安全约束）、`test_event_sink_emits_only_after_lifecycle_state_changes`（仅在持久状态变更后 emit）、`test_task_projection_polling_is_rate_limited_but_reads_fresh_runs`（节流但读新值） |
| AC8 范围锁定 | **接受** | 见 §0 范围核验 |
| AC9 Review + 集成 | **Review 由本文件闭合；集成由 Coordinator 执行** | Task 保持 `in_review` |

## 2. 两个前置验证（Review F3/F5）的落实

- **F3 协议同步**：`PROTOCOL_MAJOR` 升至 2、minor 归 0；`core.ping` 断言 `{"major": 2, "minor": 0}`；
  `test_core_service.py` 的"不支持版本"用例**正确反转**为 **major 1 被 `PROTOCOL_VERSION_UNSUPPORTED` 拒绝**。
  这是协议 bump 的**必要副作用**，断言强度未降低（仍精确匹配版本、仍验证拒绝路径）。
- **F5 migration 边界**：`migration-boundary.md` 说明该表为 additive、幂等、由 adapter 自建、
  **不进入项目级 `MigrationRunner`、不 bump schema version**；既有 Run/目标快照/current Revision/Lock/Page 数据不改写；
  `run_id` 不设外键、历史与幂等账本一并保留。**边界清晰**。

## 3. Findings

| id | 级别 | 内容 | 处置 |
|---|---|---|---|
| **F1** | **P3（流程，同类第 5 次）** | `delivery_head` 申报 `78b0d439`（实现提交），实际 HEAD=`8056ee63`（Handoff/Task 指针提交） | closeout 冻结实际 HEAD；BL-7 再次确认（建议后续把 `delivery_head` 明确定义为分支终 HEAD） |
| **F2** | P3（验证边界） | Owner 明确声明**真实 Provider 网络**与**真实用户数据库回退**未验证（`NOT_RUN`） | 与 P11 契约 §10 一致（runtime/真实 Pipeline 验收留后续）；登记为待后续 Gate，不阻塞本次集成 |
| F3 | P3（设计说明） | `pipeline_run_idempotency` 表由 adapter 自建而非 `MigrationRunner` | 已在 `migration-boundary.md` 显式说明并给出理由；属获授权范围内的设计选择。建议 P20 发布前把"幂等账本在回退/备份恢复中必须保留"纳入发布检查清单 |
| F4 | P4 | 既有测试文件的改动面（6 个文件）虽为版本号必要更新，但混在同一提交中 | 可接受；本次已在 Review 中逐项确认其性质仅为协议版本 |

**无 P0/P1/P2 finding。**

## 4. 条件

- **C1**：Coordinator 集成时冻结实际被审 head `8056ee63e0b1b5a25b64ef9e85bb8e8e54282dba`。
- **C2**：P20 释放时须把「幂等账本 `pipeline_run_idempotency` 在备份/恢复与回退中必须保留」纳入发布检查清单（衔接 F3）。
- **C3**：`P13` 可标 `done`（AC1–AC9 全部闭合）；但 F2 的真实 Provider/真实库验证仍为后续 Gate，须在相应 Task 中执行，不得据此宣称产品级安全已验收。
- 实现本身无需返修。

## 5. 能力边界

- 本 Review 覆盖范围合规、测试证据真实性、AC 逐项实现抽查与 F3/F5 落实；**未重跑 340 用例**（原始日志已核验 exit 0）。
- 所有 Git / 日志 / 代码结论均由 Reviewer 在 live 环境实际执行。
- Reviewer 未修改被审分支、主仓或任何证据文件；未 push。
