---
task_id: P13-C1
title: Runtime IPC 契约修订
reviewer: dsh（项目权威 Reviewer，`.orchestrator/tasks/P13-C1-role.json`；role_exclusion 已排除 owner=codex）
owner: codex
base_commit: c33033dc02c4373d3a3a35333a2c7aeac03c7ce6
declared_delivery_head: ed79a2b778e13e8aa892014eb16a38be4e27fdf7
reviewed_head: 7dde1f6c41dbd70bf99a61dac8bf3c40833a35f5
review_worktree: G:/CODEX/New Manga.workspace/worktrees/P13-C1-RUNTIME-IPC
date: 2026-10-16
mode: 只读审查 + 独立 Git/契约 diff 复核；未修改被审分支或主仓任何文件
object_binding: VERIFIED
severity: 冻结契约的 major 破坏性修订（protocol 1 → 2）
decision: approved
---

# P13-C1 独立 Review（R1）—— 冻结 IPC 契约 rev 2.0

## 0. 复核结果（未采信自述）

| 项 | 方式 | 结果 |
|---|---|---|
| 变更范围 | `git diff --name-only c33033dc..HEAD` | **7 个路径，全部在授权范围** |
| **P11 契约完好** | 过滤 `P11_LONG_TASK` | **未被修改** ✅（P11 是输入，不是产物） |
| **产品实现零改动** | 过滤 `^(src\|apps\|packaging)/` | **空** ✅ —— 本 Task 只改契约与证据 |
| 契约 diff 规模 | `git diff --stat` | `M2-C1_TYPED_IPC_CONTRACT.md` +112/−28（适度） |
| worktree / 主仓 | `git status` | worktree **clean**；主仓 **19 项 dirty 未变** |
| 契约实质 | 逐段读 diff | 见 §1（含 §3.1/§3.2/§4/§5/§5.5/§6.1/§6.2/§12） |

## 1. 契约修订的逐项审查

| 关注点 | 审查结论 |
|---|---|
| **幂等键表达**（AC1） | §3.1 新增 `IdempotencyKey` 类型别名，**显式独立于 `request_id`**、不规定 UUID 编码；§4 明确写「`request_id` **不得**充当幂等键」；§5.5 规定 `StartRun`/`RetryFailedTargets` 必填、`ControlRun(restart)` 必填、其他动作**不得**传入。**完全满足要求** |
| **fingerprint 定义** | §5.5 明确 fingerprint 依 P11 §2.1：含操作类型/规范化 scope/来源 Run/`overrides`，**不含**首次接受时才读取的 Revision/Lock/settings/Provider/constraint/context 或展开结果。与 P11 §2.1 一致 |
| **控制面**（AC2） | §5.5 给出 **8 个 Run 状态 × 合法/必须拒绝 × 状态结果**的完整矩阵，逐条对应 P11 §4.2/§4.5；含 `Interrupted disposition=restarted` 只允许同键重放的边界。错误码映射明确：`INVALID_REQUEST`(validation) / `INVALID_RUN_TRANSITION`(conflict) / `TARGET_NOT_FOUND`(not_found) / `IDEMPOTENCY_KEY_REUSED`(conflict) |
| **查询与投影**（AC3） | §5.5 冻结 `GetRunSnapshot` / `GetTaskProjection` / `RetryFailedTargets`；§6.1 由 PROPOSAL 转 **FROZEN** 并补齐 `tasks`/`steps`、`retry_no`（零起始）、Provider/Model/Device。关键约束：**无真值时必须 `null`，不得从当前全局设置推断或伪造**；错误只允许 §8 安全短消息，**不得直出 error_detail/异常栈/路径/secret**；`RunSnapshot` 不得暴露凭据或本地绝对路径 ✅ |
| **事件面**（AC4） | §6.2 冻结 4 类最小事件（`TaskFailed`/`RunPaused`/`RunCompleted`/`CurrentPageStepChanged`），并明确：共用既有 JSONL stdout 流、Response 以 `request_id` 配对、Event 以 `event_id` 识别、Event 可与响应交错、**stdout 只承载协议行**。**明确不承诺送达/顺序/序号/重放/保留**，断线恢复必须重查快照 ✅（诚实，不夸大） |
| **授权边界**（AC5） | §12 改为**明确授权 Python IPC Runtime**，且**严格限定在 P13 Task 已冻结的 allowlist 内**（含 2026-10-16 扩展的 `sqlite/pipeline.py` 与 provider retry/runtime）；显式排除 React/WebView、Tauri/Rust、QML、额外产品行为、其他 Schema/迁移路径、第三方依赖；并声明**不代表 runtime 已实现** ✅ |
| **版本与兼容** | §3.2 说明为何必须 major 1→2（新增**必填**字段 + 单一输出流新增异步事件，major 1 接收端无法安全忽略），并**如实声明当前生产 Core 仍为 major 1 / minor 6** —— 契约目标与实现状态的落差被显式记录，未伪报 |
| **不发明产品行为**（AC6/AC7） | §5.5 末尾明确「只暴露 P11 已冻结操作，不新增用户可见动作/目标类型/策略/状态」；覆盖对照表 `p11-d08-coverage.md` 称 D08 五组 18 条均有 wire carrier 或明确责任边界，且 **`AC-PAUSE-001` 的 UI 时限与 `AC-PROGRESS-001` 的固定布局仍归 UI 验收**，不冒充 wire 保证 |

## 2. Findings

| id | 级别 | 内容 | 处置 |
|---|---|---|---|
| **F1** | **P1（流程/权威）** | Owner 在自身会话内启用了子 Reviewer（`verification/P13-C1/review-ed79a2b7.md`，`APPROVED`）。**该内部 review 不替代项目要求的独立非作者 Review**（权威 Reviewer 由 router 定为 **dsh**）。与 P09 F1 同类 | 本 Review 为项目权威结论；内部自检报告保留为 Owner 证据，不计入项目 Review 链 |
| **F2** | **P2（记录一致性）** | Revisor 侧发现：`doc/tasks/P13.md` 声明的 `base_commit=f87d312c` 与 P13 worktree 实际起点 `6cf045b8` 不一致。**根因是 Coordinator（我）起草 P13 时的填写错误**：`f87d312c` 是起草时的 HEAD，而 worktree 是从 P13 的释放提交 `6cf045b8` 创建的 | 由 Coordinator 在恢复 P13 前修正 `doc/tasks/P13.md` 的 `base_commit`（并记录该修正）；不影响任何代码 |
| F3 | P2（实现落差） | 契约目标为 major **2.0**，而当前生产 Core 仍为 major **1 / minor 6** | P13 实现时必须同步 Core 的协议版本与 `PROTOCOL_VERSION_UNSUPPORTED` 行为；该落差已在契约内如实声明，非本次缺陷 |
| F4 | P3 | `RunProgressChanged` 保持 `UNKNOWN / PROPOSAL`（普通进度改由 `GetTaskProjection` 拉取，仅 4 类重要事件推送） | 与 P11 §7.3 的「4 Hz 普通刷新 + 重要事件立即」一致，设计合理；记录即可 |
| F5 | P4 | `migration` 被写入 P13 允许面（"含确需 migration"）但契约未细化其边界 | P13 若真需 migration，必须在其证据中单列并说明；不阻塞本次契约冻结 |

**无 P0 finding。**

## 3. 条件

- **C1**：Coordinator 集成时冻结实际被审 head `7dde1f6c41dbd70bf99a61dac8bf3c40833a35f5`。
- **C2**：集成后修正 `doc/tasks/P13.md` 的 `base_commit`（F2）并解除 P13 的 `blocked`（其两个恢复条件——wire 授权与 allowlist 扩展——现已同时满足）。
- **C3**：P13 恢复时必须验证 F3（Core 协议 major 同步）与 F5（migration 边界）。
- 契约内容本身无需返修。

## 4. 能力边界

- 本 Review 覆盖契约文本的正确性、边界与范围合规；**不代表**任何 runtime 已实现或可运行。
- 所有 Git / 契约结论均由 Reviewer 在 live 环境实际执行。
- Reviewer 未修改被审分支、主仓或任何证据文件；未 push。
