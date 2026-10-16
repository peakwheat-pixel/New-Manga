---
task_id: HOST-CORE-1
title: Core 侧 HostControl handler 实现
reviewer: dsh（项目权威 Reviewer，`.orchestrator/tasks/HOST-CORE-1-role.json`；role_exclusion 已排除 owner=codex）
owner: codex
base_commit: ed79b76f9191f0a5ebb6932a53a992a33a274041
declared_delivery_head: ff42c670122a95c5edd43b6374e4e42bf42731cb
reviewed_head: c97b2d125bd765bdfae3ec93bc440a7ba6d595c2
review_worktree: G:/CODEX/New Manga.workspace/worktrees/HOST-CORE-1
date: 2026-10-16
mode: 只读审查 + 独立 Git/实现/测试日志复核；未修改被审分支或主仓任何文件
object_binding: VERIFIED
severity: 补上被授权但从未实现的 Core host-only 接收端（§11 原 handshake 项）
decision: approved
---

# HOST-CORE-1 独立 Review（R1）

## 0. 复核结果（未采信自述）

| 项 | 方式 | 结果 |
|---|---|---|
| 变更范围 | `git diff --name-only ed79b76f..HEAD` | **17 个路径，全部在授权范围** |
| **未碰 `apps/**`（Rust/Tauri）** | 过滤 `^(apps\|packaging)/` | **空** ✅（Rust 侧属 HOST-ISSUER-1） |
| **未碰 `doc/contracts/**`** | 过滤 `doc/contracts/` | **空** ✅ |
| 越界路径 | 反向过滤授权集合 | **空** ✅ |
| worktree / 主仓 | `git status` | worktree **clean**；主仓 **19 项 dirty 未变** |
| 完整测试集 | 独立读原始日志 | `tests/core`：**395 passed / 0 failed / exit_code=0** |
| 既有测试改动性质 | 读 diff | **仅协议版本断言** `{major:2,minor:2}`→`{major:2,minor:3}`、`(2,2)`→`(2,3)`；**未削弱断言** |
| 实现结构 | 读 `src/bootstrap/core_service.py` | 见 §1 |

## 1. AC 逐项结论

| AC | 判定 | 依据（抽查代码 + 证据） |
|---|---|---|
| AC1 HostControl 接收面 | **接受** | `_HOST_CONTROL_COMMANDS` 为**独立命令集**（L186-187：`OpenHostSession`/`RegisterImportSource`/`RevokeImportSource`/`RegisterExportTarget`/`RevokeExportTarget`/`CloseHostSession`），与普通 `Request<T>` catalog **分离**；HostControl 请求字段为 `host_session_id`/`host_session_credential`/`command`/`payload`（L785），与 §5.7 一致 |
| AC2 session 握手与失效 | **接受** | `_host_session_credential` 状态（L649/770/777）；`OpenHostSession` 严格校验 payload 键集合（L816）与 credential（L819）；`CloseHostSession`（L843）；证据含 **`CloseHostSession` 后 grant 立即 `REF_REVOKED`** 与**真实子进程重启后 session ID 变化、旧 ref → `REF_UNKNOWN_ID`** |
| AC3 路由到既有私有 seam | **接受** | `RegisterImportSource`→`_register_import_source`（L870 起）等四个注册/撤销路由到既有 seam；**ref 字段与 `REF_*` 语义未改**（diff 未触及 §10.3/§10.4 相关面） |
| **AC4 三拒绝码（安全 Gate）** | **接受（重点）** | 见 §2 |
| AC5 dispatcher 不承认 host-only 命令 | **接受** | `test_host_only_commands_are_not_in_the_json_rpc_dispatcher` 对**全部六个**命令经普通 JSON-RPC 调用均返回 `HOST_ONLY_REQUIRED` 且 `result: null`（非成功路由）；另有 `command not in _HOST_CONTROL_COMMANDS - {…}` 的白名单收紧（L852） |
| AC6 范围锁定 | **接受** | 见 §0 三项过滤，全部为空；未触及 `core_assembly.py`（无需装配改动的判定合理） |
| AC7 测试与原始日志 | **接受** | 新增 `tests/core/test_host_control.py`；含拒绝零副作用、session 失效即时性、dispatcher 负向；原始日志归档且 exit 0 |
| AC8 Review + 集成 | **Review 由本文件闭合；集成由 Coordinator 执行** | Task 保持 `in_review` |

## 2. AC4 安全 Gate 的独立复核（本 Review 核心）

Owner 声明：每个拒绝用例均断言 **`calls == []`**（**未调用任何 seam**），并同时检查
**SQLite `total_changes`**、**registry grant ID 集合**、**隔离目录文件 SHA-256 快照**三者未变化；响应 `result: null` 且**不泄露路径或 credential**。

覆盖：

| 拒绝码 | 触发 | 类别 |
|---|---|---|
| `HOST_ONLY_REQUIRED` | 普通 JSON-RPC 调用 host-only 操作 | validation |
| `HOST_SESSION_INVALID` | credential 缺失 / 错误 / session 已关闭 | conflict |
| `CORE_SESSION_MISMATCH` | `core_session_id` 不符 | conflict |

代码侧亦可见对应分支：L830（`CORE_SESSION_MISMATCH`）、L831-832 与 L841（`HOST_SESSION_INVALID`）。

**结论**：三拒绝码具备"**拒绝且不调用 seam**"的**可证伪负向断言**，且叠加数据不变性检查，达到本项目的安全证据标准。

## 3. Findings

| id | 级别 | 内容 | 处置 |
|---|---|---|---|
| **F1** | **P3（流程，同类第 11 次）** | `delivery_head` 申报 `ff42c670`（实现提交），实际 HEAD=`c97b2d125`（证据收尾提交） | closeout 冻结实际 HEAD；BL-7 再次确认 |
| **F2** | **P2（新登记债务）** | **`tools/governance/check.ps1` 未被 Git 跟踪**（`git ls-files` 报 pathspec 不匹配），因此**任何 fresh worktree 都无法运行治理检查** —— Owner 在 worktree 中正确地无法运行它并如实说明 | 登记为 **BL-12**：治理检查器应纳入版本控制，否则 worktree 级自检**结构性缺失**；建议尽快修正（影响所有后续 worktree Task 的自检能力） |
| **F3** | P2（下游依赖） | 本 Task 只交付 **Core 侧**接收端；**Rust/Tauri 侧签发与联调仍属 HOST-ISSUER-1**（其分支未集成） | HOST-ISSUER-1 恢复后须把新版 main 并入其分支并重跑其 AC |
| **F4** | P3（验证边界） | 未做真实 Rust↔Core 联调；`HOST-CORE-1` 的验证是 Core 侧 stdio 级 | 联调验收留 HOST-ISSUER-1；**不得**据此声称 host issuer 已端到端可用 |
| F5 | P4 | 既有测试随协议 minor 2→3 更新版本断言 | 必要副作用；已确认无削弱 |

**无 P0/P1 finding。**

## 4. 条件

- **C1**：Coordinator 集成时冻结实际被审 head `c97b2d125bd765bdfae3ec93bc440a7ba6d595c2`。
- **C2**：**HOST-ISSUER-1 恢复前置已满足**（Core 接收端已实现）；恢复时必须并入含本 Task 的 main 并重跑其 AC1–AC9（含 Rust 侧签发、ACL 四处同步）。
- **C3**：**BL-12** 应尽快单独处置（治理检查器未版本化），因为它削弱**所有** worktree 的自检能力。
- **C4**：F4 的真实联调验收不得被本 Task 的 Core 级证据替代。
- 实现本身无需返修。

## 5. 能力边界

- 本 Review 覆盖范围合规、实现结构抽查、AC4 负向断言与测试证据真实性；**未重跑** 395 用例（原始日志已核验 exit 0）。
- 所有 Git / 代码 / 日志结论均由 Reviewer 在 live 环境实际执行。
- Reviewer 未修改被审分支、主仓或任何证据文件；未 push。
