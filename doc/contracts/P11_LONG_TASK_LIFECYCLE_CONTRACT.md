# P11 长任务生命周期契约

**状态：** 拟交付 P13 消费；本文件是 P11 范围内 durable acceptance、快照、控制、失败重试与崩溃恢复的唯一权威契约。  
**适用范围：** 新架构 Python Core 的 `PipelineRun` 生命周期。本文定义行为和消费者边界，不定义数据库 Schema、Tauri IPC wire format 或 UI 视觉实现。

本契约使用 MUST / MUST NOT 表示 P13 实现约束。所有产品行为均由下表所列正式来源映射；标为“P11 技术约束”的内容仅具体化 P08 已释放的持久接受、快照、控制与恢复目标，不改变命令含义或产品终态。

## 1. 需求映射表

| 来源与原要求 | 本契约条款 | 映射 |
|---|---|---|
| `doc/04_USER_FLOW.md` §11.1–§11.4：全部/选页/单页翻译、重新渲染、重新修复、重新 OCR 命令 | §2、§3.2 | 命令类型与已解析目标范围在接受时固定；不同命令仍遵守各自 planner 语义。 |
| `doc/04_USER_FLOW.md` §12：全部翻译沿用 OCR，不覆盖 Translation / Region Lock 与人工修改；本命令明确“不处理 Page Lock” | §3.3、§5.4 | Lock 行为保持命令特定，不把别的命令的 Lock 规则外推至全部翻译。 |
| `doc/04_USER_FLOW.md` §13：跳过已完成、已锁定、人工保护；处理未翻译、失败、缺失译文 | §3.3、§4.2、§5.4 | Skip 是计划结果，不得为重跑成功工作而覆盖已有成果。 |
| `doc/04_USER_FLOW.md` §14：重新 OCR 先定范围、检查 Lock，保留人工译文与已确认译文；OCR 变化提示下游可能失配 | §3.3、§5.4 | 接受时固定重 OCR 目标；提交仍校验 revision / Lock，不覆盖人工保护。 |
| `doc/04_USER_FLOW.md` §22：上下文窗口与写回范围分离 | §3.2–§3.3 | Context 可以只读覆盖邻页；输出只写入接受快照中的目标集。 |
| `doc/04_USER_FLOW.md` §30.1：Run 状态、Blocked、CompletedWithFailures、Interrupted 与失败页重试新建 Run | §4、§5.3 | 明确唯一状态机；失败页重试保留来源 Run 历史。 |
| `doc/04_USER_FLOW.md` §30.2、§51：异常退出后标记 Interrupted，用户选择 Continue / Restart / Abandon | §4.2、§6 | 恢复只从已持久化边界重建；三种动作语义分开。 |
| `doc/04_USER_FLOW.md` §30.3：固定进度面板、暂停安全边界、继续断点、停止不回滚、页面统计与 CompletedWithFailures | §4.2–§4.4、§6–§7 | Run 控制只更新权威 Run；已提交成果保留；P14 消费投影。 |
| `doc/04_USER_FLOW.md` §31：任务详情需显示范围、Step、Provider、Model、错误、重试次数与运行时间 | §7.2–§8 | P13 暴露可查询数据；P14 决定详情呈现。 |
| `doc/07_NON_FUNCTIONAL_REQUIREMENTS.md` §6：普通进度最多约 4 Hz，重要状态事件立即推送 | §7.3 | 百分比更新节流；暂停、失败、完成、当前 Page / Step 变化走事件更新。 |
| `doc/07_NON_FUNCTIONAL_REQUIREMENTS.md` §56：进度是投影，崩溃后由 Run / Task / StepRun / PageStageState 重建 | §6.1、§7.1 | UI 临时状态不得成为恢复真值。 |
| `doc/07_NON_FUNCTIONAL_REQUIREMENTS.md` §64：网络重试最多 2 次额外尝试，建议退避 1s、2s，优先遵守 Retry-After | §5.1 | 边界只作用于可重试网络操作；不擅自降低次数或裁剪 Retry-After。 |
| `doc/07_NON_FUNCTIONAL_REQUIREMENTS.md` §65：Authentication、InvalidInput、MissingCredential、Lock / ManualProtection 冲突默认不自动重试 | §5.1、§5.2 | 明确列为不可自动重试。 |
| `doc/07_NON_FUNCTIONAL_REQUIREMENTS.md` §66：可取消 Provider 合作取消；否则等待当前请求结束/超时并停止后续 Step | §4.3、§5.2 | Stop 不越过安全提交边界。 |
| `doc/08_ACCEPTANCE_CRITERIA.md` §26 / AC-CMD-001–004：复用有效 OCR、跳过已翻译、选择页冻结、单页命令不影响其他页 | §3.2–§3.3 | 接受时冻结命令与目标成员及顺序。 |
| `doc/08_ACCEPTANCE_CRITERIA.md` §27 / AC-PIPE-001–004：StepRun 可追踪、有效输出 Skip、stale 不算有效、遵守命令 prerequisite | §3.3、§5.3、§6.2 | 以已提交 revision 和冻结输入决定可复用 Step。 |
| `doc/08_ACCEPTANCE_CRITERIA.md` §28 / AC-PAUSE-001：Running 点击暂停后 UI ≤ 200 ms 显示“正在暂停” | §4.2、§7.2 | P13 持久化控制意图并返回确认；P14 负责 UI 时限和文案。 |
| `doc/08_ACCEPTANCE_CRITERIA.md` §28 / AC-PAUSE-002–003：不可中断 Step 可完成；不启动下一 Step；Continue 从首个未完成/stale Step 继续 | §4.2、§6.2 | 暂停在安全边界生效；有效成功 Step 不重跑。 |
| `doc/08_ACCEPTANCE_CRITERIA.md` §29 / AC-STOP-001–003：停止不回滚、不删除 Run History / Artifact / Revision，并取消尚未开始 Task | §4.3 | Stop 是取消剩余工作，不是删除或撤销已提交结果。 |
| `doc/08_ACCEPTANCE_CRITERIA.md` §30 / AC-CRASH-001–003：Running 恢复为 Interrupted；Continue 不重跑已完成 Step；未提交临时 Artifact 不成为 current | §6 | 只重放未安全提交工作，临时产物不得晋升为 current。 |
| `doc/08_ACCEPTANCE_CRITERIA.md` §31 / AC-RETRY-001–002：失败 Step 从失败点继续；失败页重试新建只含失败目标的 Run，保留旧历史 | §5.2–§5.3 | Step retry 与失败 Page retry 是不同层级。 |
| `doc/08_ACCEPTANCE_CRITERIA.md` §32 / AC-PROGRESS-001–007：固定面板、状态统计、Page 定位、失败联动、CompletedWithFailures、PageList 同源 | §7 | P13 提供单一权威投影；P14 实现面板及交互。 |
| `verification/P08/SCOPE_DRAFT.md` 第 34 行、§77：durable accepted / 快照 / 控制 / 恢复；自有契约，不写 runtime、不造第二调度器 | §2–§9 | P11 仅冻结契约与静态验证；本契约明确 P13 的单一 scheduler / task store 约束。 |
| `doc/contracts/TASK-002_MINIMUM_DATA_EXECUTION_CONTRACT.md` §6.1–§6.2：暂停安全点、Stop 竞态、Continue / Restart / Abandon、重试来源 | §4、§5.2–§5.3、§6 | 用于补足 D04 §30 / §51 已引用的竞态与动作细节。 |

## 2. Durable acceptance 与幂等

### 2.1 请求键

每个会创建新 Run 的操作（`StartRun`、Interrupted Run 的 `restart`、`RetryFailedTargets`）MUST 携带调用方生成的 `idempotency_key`。此键在同一个 Core 数据库内唯一并随 Run History 保留；调用方在 IPC 超时、断线或响应丢失后重发时 MUST 复用原键。相同内容但不同键表示用户有意创建另一 Run。该规则落实 P08 `SCOPE_DRAFT` 第 34 行的 durable accepted 目标，不将“命令内容相同”误作去重依据。

随键保存一个规范化 `request_fingerprint`，其输入为操作类型、规范化 scope（含显式选中目标及顺序）、来源 Run（适用时）与用户提供的执行选项。它不包含调用时可能变化的当前 revision、Lock、settings、Provider、目标展开结果；这些内容只在首次成功接受时读取并冻结。RetryFailedTargets 的 fingerprint 包含来源 Run 与其冻结的失败 Page 集合；Restart 的 fingerprint 包含被处置的 Interrupted Run。

| 请求情况 | 结果 |
|---|---|
| 新键 | 尝试一次原子接受。 |
| 已有键且 fingerprint 相同 | 返回原 `run_id` 与其当前状态；不创建 Run、不重新展开目标、不重取快照。Restart / RetryFailedTargets 重放返回同一个子 Run。 |
| 已有键但 fingerprint 不同 | 拒绝 `IDEMPOTENCY_KEY_REUSED`；不得改写原 Run 或快照。 |
| 新键、相同命令与 scope | 创建独立 Run。 |

### 2.2 “已接受”的唯一判定点

Run **仅在以下数据作为一个持久化事务成功提交后才算 Accepted**：

1. `run_id`、`idempotency_key`、`request_fingerprint`、命令、规范化 scope 与初始 `Pending` 状态；Restart 还须在同一事务记录原 Run 的 `interruption_disposition=restarted`；
2. 完整、固定顺序的目标成员列表（等价于 `RunTarget`，包括目标身份与接受时的目标快照）；
3. 影响执行的 settings、Provider binding、constraint reference、context policy 快照。

接受应答 MUST 在事务提交后发出，并返回同一 `run_id`。仅在内存队列登记、仅返回 HTTP/IPC 成功但未提交 Run 与快照、或只保存未解析的 UI selection 均不算 Accepted。事务提交失败时返回可诊断错误，不得返回 Accepted。进程在提交后、应答前崩溃时，重发同一键必须找回该 Run。

持久化含义是：事务提交成功后，关闭并重新打开同一 Core 数据库仍能读取同一个 Run、键、目标集合与执行快照。生产实现 MUST 使用 `PipelineStore` 的持久化适配器；仅有 `InMemoryPipelineStore` 不满足本条。数据库 Schema / IPC wire format 的调整不属于 P11。

### 2.3 快照和保护边界

- 接受快照固定命令目标、目标顺序、选项、settings、Provider binding、constraint reference 与 context policy；后续 UI selection 变化不得扩大或缩小该 Run 的目标范围（D04 §22；D08 AC-CMD-003）。
- 上下文输入可只读地包含目标外的相邻 Page；所有写回仍严格限制在接受的目标 Page / Region（D04 §22）。
- `Continue` 使用原 Run 的接受快照；`Restart` 是新 Run，以原叶子目标为范围、重新解析当前 Region / Lock / Settings / Provider / Constraint 并重新规划（TASK-002 合同 §6.2）。
- 每个 Step 提交仍须校验其输入 revision 与 Lock；人工修改、Lock、current/pinned Revision 和已提交 Artifact 不能被生命周期重放覆盖（D04 §12–§14；D08 AC-PIPE-003、AC-STOP-001、AC-CRASH-003）。

## 3. 命令与 Run 边界

### 3.1 逻辑接口面

P13 至少须提供以下逻辑操作；具体 IPC 名称、DTO 和 Schema 由其正式 Task 冻结：

| 操作 | 输入要点 | 成功结果 |
|---|---|---|
| `StartRun` | `idempotency_key`、command、scope、options | durable Accepted 的 `run_id` 与状态。 |
| `ControlPipelineRun` | `run_id`、action=`pause\|continue\|stop\|restart\|abandon`；`restart` 携带 `idempotency_key` | durable 控制回执、原/新 `run_id`（适用时）与权威状态。 |
| `ResumeBlockedRun` | `run_id` | 仅条件解除并重规划成功后，使原 Run 回到 `Pending`。 |
| `RetryFailedTargets` | `run_id`、`idempotency_key` | 新 Run 的 `run_id`；原 Run 不变。 |
| `GetRun` / progress query | `run_id` | 从权威 Run / Task / StepRun 重建的状态与进度投影。 |

### 3.2 目标与命令固定

Run 接受后，其 command、scope、目标集合和顺序不可由 UI 后续 selection 修改。Planner 继续执行 D04 §11–§14 的既有语义：翻译复用有效 OCR；跳过已完成 / 锁定 / 人工保护目标；重新 OCR 只按其专门命令处理，并保留人工译文与确认译文。命令 prerequisite、Skip 与 stale 判定满足 D08 §26–§27。D04 §12 “全部翻译不处理 Page Lock”仍只适用于该命令，不被泛化。

### 3.3 目标层级

Run / Page Task / StepRun 是不同生命周期层级：Run 状态汇总批次；失败 Page 可作为新 Run 的输入；单 Step 网络重试留在原 Run / Task 中并新增 StepRun。D04 §22 的 context window 不是目标集，不能扩大输出 target。

## 4. 控制状态机

### 4.1 Run 状态

权威 Run 状态为：`Pending`、`Running`、`Paused`、`Blocked`、`Interrupted`、`Completed`、`CompletedWithFailures`、`Failed`、`Cancelled`。`pause_requested` / `stop_requested` 是持久化控制意图，不是额外 Run 状态；Step 的执行中状态不得伪装成 Run 已暂停或已取消。

### 4.2 全部合法状态转换

| 起始状态 | 合法触发 | 目标状态 / 结果 | 约束 |
|---|---|---|---|
| 新请求 | 首次 `StartRun` 持久化 | `Pending` | 只在 §2.2 数据提交后接受。 |
| `Pending` | scheduler 开始执行 | `Running` | 目标/命令来自已接受快照。 |
| `Pending` | planner 发现无可运行单元且存在可解除阻塞 | `Blocked` | 保留错误码与阻塞原因。 |
| `Pending` | `stop` | `Cancelled` | 尚未启动的 Task 转 `cancelled`。 |
| `Running` | 安全边界到达且 `pause_requested` | `Paused` | 当前不可安全中断 Step 可先完成，不开始下一 Step。 |
| `Running` | 当前剩余工作只因可解除条件受阻 | `Blocked` | 不将阻塞伪报成成功或失败。 |
| `Running` | 所有目标处理完成且无目标失败 | `Completed` | 有效 Skip 也视为已解决单元；不得无意义重跑。 |
| `Running` | 执行正常结束且存在目标级失败 | `CompletedWithFailures` | 成功成果保留；不把批次全体改为失败。 |
| `Running` | 不可恢复的 Run 级 fatal error | `Failed` | 普通 Page / Step 失败按上一行聚合，不升级为 Run 级失败。 |
| `Running` | `stop` 生效 | `Cancelled` | 停止当前 Run 的剩余工作；已提交成果保留。 |
| `Running` | 启动恢复确认旧 scheduler owner 已退出 | `Interrupted` | 只标记此前仍为 `Running` 的 Run。 |
| `Paused` | `continue` | `Running` | 从首个未完成 / stale Step 继续。 |
| `Paused` | `stop` | `Cancelled` | 取消未开始工作，不撤销已提交结果。 |
| `Blocked` | 条件解除并成功重新规划 | `Pending` | 原 Run 和已完成结果保留。 |
| `Blocked` | `stop` | `Cancelled` | 后续 Pending Task 转 cancelled。 |
| `Interrupted` 且无处置 disposition | `continue`，校验完成 | `Running` | 同一 Run、同一接受快照。 |
| `Interrupted` 且无处置 disposition | `abandon` | `Cancelled` | 原 Run 记录 abandonment；不回滚成果。 |
| `Interrupted` 且无处置 disposition | `restart` | 原 Run 保持 `Interrupted`；新 Run 为 `Pending` | 原 Run 记录 disposition=`restarted`；新 Run 记录来源。 |
| `CompletedWithFailures` | `RetryFailedTargets` | 原 Run 不变；新 Run 为 `Pending` | 新 Run 仅包含失败 Page，并记录 `source_run_id` 与 `retry_reason=retry_failed_targets`。 |

竞态裁决：Stop 与最后 Step / Run 聚合并发时按同一持久化事务的提交顺序决定唯一结果。若完成聚合先提交，Run 保持 `Completed` 或 `CompletedWithFailures`；否则取消剩余工作并提交 `Cancelled`。禁止出现双终态（TASK-002 合同 §6.1）。

### 4.3 暂停与停止确认

- `pause` 被接受时先持久化 `pause_requested`。Run 在安全边界到达前仍是 `Running`；UI 可显示“正在暂停”，不得提前显示 `Paused`。AC-PAUSE-001 的 ≤200 ms 是 P14 的呈现目标。
- 当前 Step 不支持合作暂停时允许完成；随后不启动新 Step，再提交 `Paused`。提交边界不得留下半个 current Artifact / Revision（D08 AC-PAUSE-002）。
- `stop` 被接受时先持久化 `stop_requested`。若当前 Provider 支持取消则合作取消；否则等待当前请求结束或超时，再停止后续 Step。成功后把尚未开始 Task 标记 cancelled。
- Stop 不是 Delete 或 Rollback。Run History、已提交 Revision / Artifact 与已完成 Page / Region 全部保留（D04 §30.3；D08 AC-STOP-001–003）。

### 4.4 终态语义

`Completed`、`CompletedWithFailures`、`Failed`、`Cancelled` 是终态；不接受原 Run 上的继续、暂停、停止、重启或再次启动。失败 Page 重试是新 Run。`Paused`、`Blocked` 与 `Interrupted` 不是终态，分别只能按上表继续、解阻塞重规划或处置。`Interrupted` 的 Restart 不把原 Run 改为另一个状态。

### 4.5 非法转换拒绝清单

以下拒绝表穷尽 §3.1 用户操作与恢复操作在每个 Run 状态下的合法输入；非法请求返回 `INVALID_RUN_TRANSITION`（Run 不存在时沿用现有 `TARGET_NOT_FOUND`），且不得产生副作用。

| 当前状态 | 仅允许 | 必须拒绝 |
|---|---|---|
| `Pending` | scheduler start、`stop` | `pause`、`continue`、`restart`、`abandon`、`ResumeBlockedRun`、`RetryFailedTargets`、恢复扫描改写。 |
| `Running` | `pause`、`stop`；仅启动恢复可转 `Interrupted` | `continue`、`restart`、`abandon`、`ResumeBlockedRun`、`RetryFailedTargets`、第二次 scheduler start。 |
| `Paused` | `continue`、`stop` | 再次 `pause`、`restart`、`abandon`、`ResumeBlockedRun`、`RetryFailedTargets`、崩溃恢复改写。 |
| `Blocked` | `ResumeBlockedRun`、`stop` | `pause`、`continue`、`restart`、`abandon`、`RetryFailedTargets`、直接执行未重新规划的旧计划。 |
| `Interrupted` 且无处置 disposition | `continue`、`restart`、`abandon` | `pause`、`stop`、普通 scheduler start、`ResumeBlockedRun`、`RetryFailedTargets`。 |
| `Completed` | 无 | 全部控制、恢复、启动及失败目标重试。 |
| `CompletedWithFailures` | `RetryFailedTargets`（满足 §5.3） | 全部控制、恢复、原 Run 重启或再次执行。 |
| `Failed` | 无 | 全部控制、恢复、启动及失败目标重试；新尝试必须通过新的显式 StartRun。 |
| `Cancelled` | 无 | 全部控制、恢复、启动及失败目标重试；不得把已取消 Run 复活。 |

`Interrupted` 已有 `interruption_disposition=restarted` 时，除用原 `idempotency_key` 重放并取回既有 child Run 外，必须拒绝新的 Continue / Restart / Abandon；不得重复创建 restart child，也不得再显示处置动作（TASK-002 合同 §6.2）。所有状态另须拒绝：未知 action；scope / run id 与请求不符；以已有 `idempotency_key` 携带不同 fingerprint；解阻塞条件未满足；或绕过 §2.2 持久化接受。拒绝不得覆盖 Run、Task、StepRun、current Revision 或历史记录。

## 5. 失败与重试

### 5.1 自动网络重试

自动重试限于网络 / Provider 适配层明确分类为暂时性且可重试的单次操作；通用 scheduler 不得对任意 `StepExecutionError` 或任意未知异常盲目重跑。每个该操作最多 **2 次额外重试**（首次 + 2 Retry），推荐等待 1s、2s；若 Provider 返回 `Retry-After`，优先遵守其值。D07 §64 未给 Retry-After 上限，P13 不得自行添加截断值。

以下错误默认不自动重试：`ProviderAuthenticationError`、`ProxyAuthenticationError`、`InvalidInput`、`MissingCredential`、`LockBlocked`、`ManualProtectionConflict`（D07 §65）。输入 revision / Lock 冲突也必须先重新校验并保留候选结果，不能用自动 retry 覆盖人工变化（D08 AC-PIPE-003；TASK-002 合同 §6）。

自动网络重试留在原 Run 与 Task；每次真实 Step attempt 新增 `StepRun`，输入 revision、锁快照、settings 与 Provider binding 不变；不得改写先前失败 StepRun。

### 5.2 失败后的终态与上游复用

重试耗尽或遇到不可自动重试错误时，将该 Step / Page 标记失败并保留错误详情。其他 Page 的工作可继续；正常聚合为 `CompletedWithFailures`，Run 级 fatal 才为 `Failed`。已成功且仍有效的上游 Step 不因下游失败重跑（D08 AC-RETRY-001）。

### 5.3 用户重试失败 Page

只有存在失败 Page 的 `CompletedWithFailures` Run 可执行 `RetryFailedTargets`。该操作新建 Run，仅包含原 Run 的失败 Page，保存 `source_run_id` 和 `retry_reason=retry_failed_targets`；原 Run、StepRun、错误与成果历史不可改写（D04 §30.1；D08 AC-RETRY-002）。Step 网络重试、Continue 与 Restart 均不得伪装成这类新 Run。

## 6. 崩溃恢复与幂等重放

### 6.1 判定条件与恢复点

启动恢复必须先取得唯一 scheduler ownership，再扫描同一持久化 store。只有在旧 scheduler owner 已确认退出、Run 持久状态仍为 `Running` 时，才把它和其中 `Running` 的 Task / StepRun 标为 `Interrupted`；不能因 UI 未收到进度、轮询超时或单一 Page 长时间无变化而推断崩溃。其他状态保持持久值：尚未启动的 Accepted `Pending` 继续留队，`Paused` 仍等待用户 Continue，`Blocked` 等待条件处理，终态不重开。

恢复真值由持久化的 Run、冻结目标 / settings / Provider / constraint / context 快照、Task、StepRun、输入 revision / Lock snapshot、已提交 ArtifactRevision 和 PageStageState 组成。UI 缓存或进度条不是恢复点（D07 §56）。

### 6.2 Continue / Restart / Abandon

- **Continue：** 同一 Run 使用原冻结快照；验证已提交 revision / Lock 与 Step 有效性，从第一个未完成或 stale Step 继续。已完成且仍有效的 Step 不重跑；stale 或未安全提交的 Step 才重跑（D08 AC-PAUSE-003、AC-CRASH-002；TASK-002 合同 §6.2）。
- **Restart：** 创建新 Run，沿用原叶子目标，但重新读取当前 Region、Lock、Settings、Provider、Constraint 并规划；新 Run 记录 `source_run_id` 与 `retry_reason=restart_after_interruption`。新 Run 的 durable acceptance 与旧 Run 的 `interruption_disposition=restarted` 必须原子提交。旧 Run 保持 `Interrupted`，不再显示重复处置动作；相同 `idempotency_key` 重放返回同一个 child Run（TASK-002 合同 §6.2）。
- **Abandon：** 原 Interrupted Run 转 `Cancelled`，记录 `termination_reason=abandoned_after_interruption`；不建新 Run、不回滚或删除已提交成果（TASK-002 合同 §6.2）。

### 6.3 重放边界

1. 若 `StepRun` 的提交已持久化且输出仍通过输入 revision / Lock 有效性校验，恢复不得再次执行该 Step。
2. 若 Step 结果未安全提交，恢复可以重新执行该 Step；不能承诺外部 Provider 调用 exactly-once。Provider 调用与本地提交之间崩溃时，允许发生重复外部计算 / 计费，但绝不允许把未提交临时产物当 current ArtifactRevision。
3. Step 完成标记与其 current Revision / Artifact 提交必须有可恢复的一致边界。Crash 后只能看到“都未提交”或“结果与完成记录一致”的状态，不能出现半 Commit（D08 AC-PAUSE-002、AC-CRASH-003）。
4. 重放使用原 Run 快照及原目标集；只有用户选择 Restart 才能重新解析当前设置与目标状态。
5. 同一 `idempotency_key` 的 StartRun 重放遵守 §2.1，不能创建第二个 Run。它不去重用户使用新 key 显式提交的相同命令。

## 7. 单一 scheduler、Task store 与进度投影

### 7.1 唯一所有权

`PipelineService` / `PipelineStore` 是唯一 Run 调度与生命周期写入权威。P13 可以把该调度入口放到一个 Core-owned worker 中运行；worker 是执行位置，不是第二 scheduler。UI、bridge、Step handler 或外围队列 MUST NOT 自行规划目标、推进 Run / Task / StepRun、绕过 store 直接更新 Run，或维护一份可独立恢复的影子队列。

同一时刻只允许一个 scheduler owner 消费和推进持久化 Run。所有 Start、Control、恢复与聚合都经同一调度入口与其 `PipelineStore`；SQLite connection 与 worker 生命周期由 P13 明确拥有。不得用第二个 scheduler、第二份 task store 或直接调用 executor 的方式并行绕过该所有权。这是 P08 `SCOPE_DRAFT` §77 的显式硬约束。

### 7.2 投影接口与消费者分工

P13 提供基于权威 Run 的只读 `TaskProgress` / `TaskProjection`：Run 总体进度、当前 Page / Step、完成 / 失败 / 跳过 / 阻塞 / 等待统计与原因、错误和 retry 元数据、状态可用的 controls。进度投影必须与 PageList 使用同一 Run 数据源（D08 AC-PROGRESS-002–007）。

P14 负责 React Workbench 固定 TaskProgressPanel、错误/详情区、按钮可用态、PageList 联动，以及 AC-PAUSE-001 的 ≤200 ms“正在暂停”反馈。P13 负责控制请求的持久化确认和权威状态变化，不负责 UI 文案、组件、动画或视觉实现。D04 §31 要展示的 Provider / Model / Device 等详情字段由 P13 暴露可得真值，P14 决定呈现方式。

### 7.3 投影刷新

普通百分比更新目标为最多约 4 Hz（250 ms 一次），重要状态事件（Task Failed、Run Paused、Run Completed、Current Page / Step Changed）允许立即推送；投影是重建的只读视图，不是业务真值（D07 §6、§56）。React 消费者沿用这些时效目标；不得因 legacy QML 名称而把旧 QML UI 实现引入 P11 / P13。

## 8. 现状对照

下表仅描述指定只读实现；“现存可复用”不等于 P11 授权修改，“拟议新增”交 P13 的独立 Task 实现。P11 未修改这些实现。

| 要求 / 实现位置 | 当前事实 | 分类与 P13 含义 |
|---|---|---|
| 调度与生命周期：`src/application/tasks/service.py` `PipelineService` | `create_run` 生成随机 Run ID、展开目标并冻结 settings / Provider / constraint / context / RunTarget；`plan_run`、`execute_run`、`control_run`、`recover_running_runs`、`retry_failed_targets` 已存在。 | **现存可复用**：使用此唯一入口作为 scheduler。**拟议新增**：`StartRun` 的 request key / fingerprint / 原子 durable acceptance，生产级恢复接线与控制确认。 |
| 单序列执行：`service.py` `ResourceLimits`、`execute_run` | 页与 Step 并发限制默认均为 1；调度器在安全边界检查 pause / cancel。 | **现存可复用**：已有串行调度语义。**拟议新增**：跨 Run 的唯一 owner / worker 与 process ownership 保证；不得另造调度器。 |
| 快照与写回保护：`src/application/tasks/store.py` `SnapshotProvider`、`TargetCatalog` | Protocol 提供 `freeze`、当前目标读取与比较 revision / Lock 的 `commit_step` seam；in-memory provider 深冻结 settings / Provider / context。 | **现存可复用**：冻结快照与 revision / Lock 提交接口。**拟议新增**：把完整接受数据与幂等记录作为 durable transaction 写入生产 store。 |
| Store：`store.py` `PipelineStore` / `InMemoryPipelineStore` | Protocol 只有 `put/get/list_ids`；默认实现是内存字典，不能跨进程恢复。 | **现存可复用**：`PipelineStore` 作为唯一权威抽象。**拟议新增**：生产持久化适配器承诺事务与唯一 idempotency key；内存实现不得冒充生产 durable acceptance。 |
| 生产装配：`src/infrastructure/pipeline/assembly.py` | `build_production_pipeline` 注入 `SqlitePipelineStore`、`SqliteSnapshotProvider`、`SqliteTargetCatalog` 与 `ProductionStepExecutor`。 | **现存可复用**：生产依赖注入路径。此只读核对未审查 `infrastructure.sqlite.pipeline` 的内部事务实现；P13 必须针对其验证 §2.2 与 §6.3。 |
| Step 执行边界：`src/application/translation/pipeline/executor.py` `StepExecutor`；`src/infrastructure/pipeline/executor.py` | StepExecutor 只运行 Step 并返回结果；Production executor 显式 dispatch handler，不拥有 Run 状态 / 目标排程。当前异常会映射为 Step failure；没有 D07 自动网络重试策略。 | **现存可复用**：Provider 工作与 scheduler 生命周期分层。**拟议新增**：明确可重试错误分类、D07 上限 / 退避与新的 StepRun 尝试；handler 不得调度下一步。 |
| Step commit 与恢复：`service.py` `commit_step_result`、`_persist`、`recover_running_runs` | 校验输入映射、revision / Lock 并经 catalog commit；生命周期边界调用 store `put`；恢复把 Running 的 Run / Task / StepRun 标 Interrupted。 | **现存可复用**：安全比较、candidate、状态恢复入口。**拟议新增**：P13 验证 Artifact 与 StepRun 完成记录的 crash 原子性、启动 owner 检查及同一事务边界。 |
| 进度：`src/application/tasks/projection.py` `build_projection`；`service.py` `get_task_progress` | 纯数据投影包含 Run 状态、百分比、Page 状态、当前 Page / Step、统计、阻塞原因和按状态启用的按钮；与 PageList 共用 Run。 | **现存可复用**：权威投影逻辑和同源规则。**拟议新增**：P13 将投影查询 / 事件接到新 Core bridge；P14 消费并实现刷新 / 交互目标。 |

## 9. P13 / P14 消费边界

| 消费者 | 本契约交付面 | 不属于本 Task / 消费者责任 |
|---|---|---|
| P13 Runtime | `StartRun` 幂等与 durable acceptance；快照与目标冻结；唯一 scheduler / store ownership；ControlPipelineRun 合法转换；失败分类 / 重试；启动恢复；TaskProgress 权威投影。 | 本 Task 不接 Runtime、不执行 Pipeline、不修改 Schema、IPC、bootstrap、bridge、依赖或测试。P13 不得改变 D04 / D08 产品语义或新增第二 scheduler。 |
| P14 UI | 可消费的 Run / progress / control 投影语义；Pause request 与 Paused 状态区别；允许操作矩阵；失败 / 重试来源。 | 本 Task 不实现 React 组件、UI 文案 / 布局 / 动画 / 视觉，不验证真实 UI；AC-PAUSE-001 时限与 AC-PROGRESS 页面交互由 P14 验收。 |

消费者不得把 projection 当业务存储，不得绕过 PipelineStore，也不得从 UI selection 重建已经 Accepted 的 Run。

## 10. Verification 计划与结果

本 Task 的 verification 限于静态来源命中、条款一致性和指定只读实现核对。状态：

| 检查 | 本 Task 结果 | 证据 / 交接 |
|---|---|---|
| D04 §11–§14 / §22 / §30–§31 / §51 与 D07 / D08 来源命中、逐项映射 | `PASS`：来源章节锚点和 AC 编号已逐条核对并映射至 §1–§9。 | 本表与 §1；命令结果记于 `doc/tasks/P11.md`。 |
| 控制状态机、合法边及非法转换拒绝清单自洽 | `PASS`：状态与动作逐项对照 D04 §30.1 / §30.3、D08 AC-PAUSE / STOP / CRASH / RETRY、TASK-002 合同 §6。 | §4；仅为契约静态检查，不是 runtime 证明。 |
| 指定现状实现与符号核对 | `PASS`：逐项阅读 `service.py`、`store.py`、`projection.py`、translation executor、production executor / assembly，并在 §8 标明复用与新增。 | §8；SQLite adapter 内部原子性留给 P13 检查。 |
| 静态边界 / 来源一致性 | `PASS`：durable accepted、snapshot、控制状态与 P13 / P14 边界均有正式来源；未发现要求 P11 作额外用户级终态裁决的缺口。 | §1–§9。 |
| 数据库关闭 / 重开、durable acceptance 与幂等重放 runtime 验证 | `NOT_RUN` | P13 验收。 |
| Pause / Stop / 竞态 / crash / Continue / Restart / Abandon runtime 验证 | `NOT_RUN` | P13 验收。 |
| 真实 OCR / Translation / Inpaint Pipeline 执行与 retry 计费验证 | `NOT_RUN` | P13；不得以 deterministic executor 结果代替。 |
| React UI、Pause ≤200 ms、进度刷新 / PageList 同源验证 | `NOT_RUN` | P14 验收。 |

P11 没有运行 runtime、真实 Pipeline、UI、自动化测试或端到端命令；以上全部严格标为 `NOT_RUN` 并移交对应 Task。
