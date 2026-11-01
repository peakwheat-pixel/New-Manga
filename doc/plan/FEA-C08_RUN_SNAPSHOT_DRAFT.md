# FEA-C08 Run 快照与已接受任务不可变（草案）

状态：**FROZEN v5 / 冻结于 2026-11-01（[冻结记录](FEA-CONTRACT-FROZEN-C08.md)）**
日期：2026-11-01
作者：DSH（Lead / Architect / Integrator）
依据：[FEA-01 契约清单](FEA-01_CONTRACT_DRAFT.md) 的 C-08、[FEA-00 方案 r4](../design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md) §10、代码现状（`src/infrastructure/sqlite/schema.py`、`src/application/tasks/service.py`）、[C-01b 存储契约](FEA-C01b_STORAGE_CONTRACT_DRAFT.md)

**边界声明**：本文件是**草案**——**本草案自身不修改任何文件、不改 schema**；其要求修改的 M2-C1 属**冻结契约**，字节修订由前置（b）的独立 Task 执行（见 §5），本草案只冻结「要加什么」。

---

## 1. 现状（schema 事实）

`pipeline_runs` 表（`schema.py:290-313`）已有快照列：

| 列 | 含义 |
|---|---|
| `requested_targets_json` | 请求目标（book/chapter/page/region） |
| `settings_snapshot_json` | 创建时的设置快照 |
| `provider_binding_snapshot_json` | 创建时的 provider 绑定 |
| `constraint_snapshot_ref` | 约束快照引用 |
| `context_policy_json` | 上下文策略 |
| `run_json` | 运行记录 |
| `status` / `pause_requested` / `cancel_requested` / `terminal_step_units` 等 | 运行状态 |

`pipeline_run_targets` 表（`:316+`）有 `snapshot_json`——**逐目标快照已存在**。

## 2. 缺口（C-08 要冻结的）

> **2026-11-01 补记**：下列缺口中的 SC-R06…SC-R09 四项为 D06 声明范围的补齐（[UNFREEZE 载体](../reviews/CONTRACT-UNFREEZE-C08-2026-11-01.md)）。

| 缺口 | 现状 | 影响 |
|---|---|---|
| **PreparedRun 抽象** | 无独立类型；`pipeline_runs` 行即「已接受任务」，但无「预览 → 接受」的两阶段语义 | 预览时展示的摘要与提交后的实际执行**可能不一致** |
| **候选存储（candidate store）** | 无 | 预览后配置变化（换 provider/模型）会静默影响已接受任务 |
| **配置变化不改已接受任务** | 无显式校验 | §10 要求「配置变化不改已接受任务」，当前只在创建时快照，**未校验**执行期读的是快照还是最新配置 |
| **快照不含上下文页内容** | `TargetSnapshot` 无上下文页字段（AD-003 §4 已记） | 快照无法支撑「重放/审计」的完整上下文 |

## 3. 契约条款（冻结候选）

### SC-R01 PreparedRun 两阶段

- **预览阶段**（`PrepareRun`）：计算 `PreparedRun`（快照 + 摘要 + `preparedDigest`），**不写 DB、不触发执行**。
- **接受阶段**（`AcceptRun`）：校验 `preparedDigest` 与当前状态一致 → 写入 `pipeline_runs`（含全部快照列）→ 返回 `runId`。
- **拒绝**：digest 不一致 / 目标变化 / 配置变化 → `RUN_STALE_PREVIEW`（`conflict` / `retryable=false`；零副作用，需重新预览）。
- **`preparedDigest` 算法**：对 `{requestedTargets, settingsSnapshot, providerBindingSnapshot, constraintSnapshotRef}` 做 canonical JSON（键排序、UTF-8、无空白）后 sha256；**输出格式与 C-04b 一致**：`sha256:<64 hex>`（小写带前缀）。

### SC-R02 快照不可变

- 已接受的 `pipeline_runs` 行的 `*_snapshot_json` **只增不改**：任何「更新快照」= 新 Run（`source_run_id` 指向原 Run）。
- 执行期**只读快照**，不读当前配置；读当前配置 → 违规。

### SC-R03 配置变化不影响已接受任务

- 用户在预览后修改 provider/模型/参数：**不影响**已接受任务的快照；新 Run 用新配置。
- 校验：`AcceptRun` 时 `preparedDigest` 覆盖「目标 + 设置 + provider 绑定 + 约束」四元组。

### SC-R04 候选存储

- `candidate store`（Host 侧，临时）保存 `PreparedRun` 直到接受或过期（建议 ≤ 10 分钟）；过期 → `RUN_PREVIEW_EXPIRED`（`conflict` / `retryable=false`；需重新 prepare 并生成新 preview）。
- 候选**不落 Core DB**（避免污染运行时数据）。

### SC-R05 快照完整性

- `settings_snapshot_json`/`provider_binding_snapshot_json` 必须是**完整**的可重放值（不是引用指针）。
- 缺失/不完整 → `AcceptRun` 拒绝（`RUN_SNAPSHOT_INCOMPLETE`，`unavailable` / `retryable=true`）。

### SC-R06 控制 pending 状态（D06 声明范围）

**引用 M2-C1 `:213`（控制状态矩阵 Running 行，不复写）**：`Running` 状态下 `pause`/`stop` **先持久化请求**，当前不可安全中断的 Step 可完成，到安全边界后不再开始下一步。

**Run 侧不变量（本契约新增）**：

1. **「控制请求已持久化」≠「状态已改变」**：`ControlRun` 成功返回只证明请求被 Core 接受并持久化，**不证明** Run 已进入 `paused`/`cancelled`。
2. **UI 不得早于 Core 持久化的 `status` 显示 `paused`/`cancelled`**：受理后、状态变更前，**控制受理 ≠ 状态改变**（M2-C1 `:203` 的 `ControlResult.status` 仍可为 `running`；P11 §4.1 `:97`：`pause_requested`/`stop_requested` 是持久化的控制意图，**不是**额外的 Run 状态）。具体过渡态呈现由 UI 契约/实现决定，本契约不规定视觉形式。
3. **状态变更的唯一权威**是 Core 的 Run 状态持久化（与 SC-R07 的权威源一致）。

**验证**：发出 `pause` → 断言 `ControlResult.status` 仍可为 `running`；UI 断言显示过渡态；到安全边界后再查 → 断言 `status="paused"`。

### SC-R07 真实完成口径（D06 声明范围）

**权威持久状态**：Run 的完成状态只以 **Core 持久化的 Run/Task/StepRun 数据**为准（M2-C1 `:137`「同步响应表示接受，不表示长任务完成」；`:902`/`:1060`「事件不是状态真值」）。

**完成判定**：

**所有终态的共同不变量**：`status ∈ {completed, completed_with_failures, failed, cancelled}` **且** `counts.processing = 0` **且** `counts.waiting = 0`（不再有活动工作）。

**逐终态的附加判据**（字段用 M2-C1 §6.1 冻结的 `TaskProjection.counts: {total, completed, failed, skipped, blocked, waiting, processing}`，`:834`）：

| 终态 | 附加判据 |
|---|---|
| `completed` | `counts.failed = 0` 且 `counts.blocked = 0` |
| `completed_with_failures` | `counts.failed > 0` 且 `counts.blocked = 0` |
| `failed` / `cancelled` | **不要求**满足 total 等式——可能有未开始/未处理目标（M2-C1 `:221`：cancelled 时未开始 Task 转 cancelled）；只要求共同不变量。**`waiting=0` 的依据**：P11 `:111` 只规定 Run 级 fatal → Failed，未规定未开始 Task 的处置，故本契约把「无 waiting/processing」作为**额外要求**——终态下不应再有排队工作 |

**不得**用 `targets.length` 与计数相加作等式：`skipped` 是计划结果（P11 `:14`），`blocked`/`waiting`/`processing` 各有语义，简单相加会误判。

**明文的否定**：

- **`RunAccepted` 不证明完成**——它只证明「接受」；
- **事件不是状态真值**——事件可能丢失/乱序/重复，UI 必须能靠重读状态恢复；
- **`GetTaskProjection` 的统计与 `RunSnapshot.status` 必须同源**。

**验证**：①构造 `counts.failed>0` 但 `status=completed` 的投影 → 断言判定为非法态；②构造 `status=cancelled` 且 `counts.processing>0` → 断言非法态；③**重启后**调 `GetRunSnapshot` → 断言仍返回同一终态与同一 `counts`；④断网重连 → 断言 UI 靠重读状态恢复而非依赖事件。

### SC-R08 retry 的快照来源（D06 声明范围）

**必须区分两种情形**：

| 情形 | 键 | 是否新建 Run | 快照来源 |
|---|---|---|---|
| **同键重放** | 同一 `idempotency_key` | **否** | **不重新取快照**（M2-C1 `:200`：同键重放返回该 Run 当前状态） |
| **新建失败目标重试** | 新 `idempotency_key` | **是**（`RetryFailedTargets`） | 见下 |

**新 Run 的快照来源（明确回答）**：

- **目标集合**：**复用**源 Run 的失败 Page 集合（M2-C1 `:206`），写 `source_run_id` + `retry_reason="retry_failed_targets"`；
- **冻结上下文**（当前 Revision / Lock / settings / Provider / constraint / context）：**重新读取并冻结**——fingerprint 明确**不含**这些（M2-C1 `:202`）；
- **结论**：retry **复用「目标集合」但不复用「冻结上下文」**；源 Run 的历史与快照**不变**（`:206`）。

**对照 P11 §3.3**：新 Run 是**独立的 Run**，不是源 Run 的延续；`source_run_id` 只是溯源标记，不构成状态继承。

**验证**：对 `completed_with_failures` 的 Run 发起 retry → 断言新 Run 有 `source_run_id`、目标是失败 Page 子集、其 `Targets` 的 Revision 是**接受时重新读取**的；同键重放 → 断言返回原 `run_id` 且未新建。

### SC-R09 断线 receipt（D06 声明范围）

**已有基础（M2-C1 `:200`，不复写）**：事务提交后响应丢失时，**同键重放须找回原 Run**。

**补充三件事**：

1. **覆盖范围**：仅对带 `idempotency_key` 的操作有效——`StartRun`、`RetryFailedTargets`、`ControlRun(action="restart")`（M2-C1 `:201`）。其余 `ControlRun` 动作与 `ResumeBlockedRun` **不得**传入该字段，因此不提供 receipt 找回能力。
2. **查询方式**：**同键重放**是唯一找回入口；**不新增**「按 request 查询」的专用命令。
3. **生命周期**：`idempotency_key` 记录**随 Run History 保留**（M2-C1 `:201`），不因 Run 结束而清理。

**明文的否定**：

- **`request_id` 不能充当去重键**——M2-C1 `:138` 明文「`request_id` 只做单次请求/响应关联，**不得**充当幂等键」；去重必须用调用方生成的 `idempotency_key`；
- **同键异 fingerprint** → `IDEMPOTENCY_KEY_REUSED`（M2-C1 `:201`/`:223`），该键不得被复用为不同操作；
- **不得**用「时间窗口」近似去重（重启后时间基准不可靠）。

**验证**：注入「提交成功但响应丢失」→ 同键重放 → 断言找回原 `run_id`、无第二个 Run；`request_id` 相同但 `idempotency_key` 不同 → 断言这是**两个不同操作**。

## 4. 与 C-01b / C-05 / C-04b 的接口

- **C-01b**：Run 快照在 **SC-10b/SC-13**（备份覆盖清单/恢复索引）；本草案的 SC-R02/SC-R05 是对其的细化，不是新语义。
- **C-05**：Run 的 `active_runs` 判定引用 **`ACTIVE_STATES = {pending, running, paused, blocked, interrupted}`**（与 C-05 v3 及 `core_assembly.py:171-181` 一致；`prepared`/`committed` 不是 Run 状态）。
- **C-04b**：删除保护要求「无活跃 Run」——按 `ACTIVE_STATES` 判定（`prepared` 是 export 的 `hooks_prepared` 字段，不是 Run 状态；删除阻塞只看 Run 的非终态集合）。

## 5. 冻结条件

1. 独立复核通过；
2. C-01b 已冻结（顺序：C-01b 先）；
3. **前置（a）**：C-05 与 C-04b 已冻结（§4 依赖它们的 active_runs 与删除保护口径）；
4. **前置（b）**：协议注册——**方案**已冻结在本草案 **§3**（SC-R01/R04/R05）；**M2-C1 字节修订**（**§5.5 命令表追加 `PrepareRun`/`AcceptRun` + 3 个新码进 §5.5 错误语义段 + §8 新增「Proposed（未观察）」小节 3 行 + §8 taxonomy 例外 + `:1119` retryable 证据规则例外**；**host 投影层新增 `allowedRunErrorCodes` 白名单**（Core §8 不改；未注册码 → `category=unknown` + 安全短消息、**不重写 `code`**）；wire minor **2.12**，DSH 批准）由**独立 Task** 在**释放任何 Run 实现之前**完成并复核，与 C-04b 共用 Task 的**块②**（见 [裁定 v3](GATE-CLOSURE-RULING-2026-11-01.md) **R-4**）；复核须含**负向对照**：未扩 M2-C1 时 3 个新码必须被 **host 的 `allowedRunErrorCodes` 白名单降级**为 `category=unknown`（不重写 `code`、不作 UI 分支依据）；注意 §8 的 `ErrorEnvelope.code` 是自由字符串、无白名单时会透传，所以**白名单本身是块② 的交付项**；
5. `check.ps1` PASS。

## 6. 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-01 | **v7（r11 P2）**：SC-R07 补「`failed`/`cancelled` 的 `waiting=0` 依据」句（P11 `:111` 未规定未开始 Task 处置，故为 C-08 额外要求）；pin 按改后字节重算 | DSH |
| 2026-11-01 | **v6（处置 FEA-C08-r9 的 P1×2 + P2×5）**：P1-1 **SC-R07 完成判定重写**——改用 §6.1 冻结的 `counts.{total,completed,failed,skipped,blocked,waiting,processing}`（M2-C1 `:834`），共同不变量 `processing=0 && waiting=0`，逐终态附加判据，**取消** `targets.length = succeeded + failed`（`succeeded` 字段不存在、且漏 skipped/blocked）；cancelled/failed 不要求 total 等式；补「重启后仍为终态」验证。P1-2 版本同步 v4→v5。P2-1 行号改 `:213`/`:202`；P2-2 过渡态措辞；P2-3 `request_id` 引 `:138` + `IDEMPOTENCY_KEY_REUSED` | DSH |
| 2026-11-01 | **v5（FEA-D06-GAP）**：新增 **SC-R06 控制 pending 状态**、**SC-R07 真实完成口径**、**SC-R08 retry 快照来源**、**SC-R09 断线 receipt**四项，补齐 D06 六项声明范围；走 [UNFREEZE 载体](../reviews/CONTRACT-UNFREEZE-C08-2026-11-01.md) | DSH |
| 2026-11-01 | 建立草案：schema 事实、4 项缺口、SC-R01…SC-R05 五条、与三份契约接口、冻结条件 | DSH |
| 2026-11-01 | v2：处置 FEA-GOV-7 r1（P1-1 接口口径 + P2×3） | DSH |
| 2026-11-01 | **v3（处置裁定 r3/r4）**：前置（b）落点改为**扩展 M2-C1 §5.5**（追加 2 命令 + 3 码进 §5.5 与 §8 ErrorEnvelope，不是新建章节/ErrorView）；引用 §2→§3；3 码补 category/retryable；wire minor **2.12** DSH 批准；冻结条件重排 | DSH |
| 2026-11-01 | **v4（处置裁定 r6/r7 的 P1×5 + P2×8）**：前置（b）白名单改挂 **host 投影层**（Core §8 不改、「降级」写死）；§8 落点改「Proposed（未观察）」小节 + taxonomy 例外说明；§1 「不改冻结契约」改述为本草案自身不写文件 | DSH |
