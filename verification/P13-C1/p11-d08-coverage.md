# P13-C1 P11 / D08 Wire 覆盖对照

- 基线：`c33033dc02c4373d3a3a35333a2c7aeac03c7ce6`
- 契约：`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` rev `2.0`，§3、§4、§5.5、§6.2、§11、§12
- 行为来源：`doc/contracts/P11_LONG_TASK_LIFECYCLE_CONTRACT.md` 与 `doc/08_ACCEPTANCE_CRITERIA.md`
- 结论口径：本表验证 wire 能承载已冻结行为，不代表 runtime、UI、Schema 或任一 D08 验收已实现/通过。

## P11 逻辑接口与生命周期

| P11 来源 / 逻辑接口 | 新 wire 元素 | 覆盖关系与边界 |
|---|---|---|
| §2.1–§2.2 durable acceptance / `StartRun` | `StartRun {command, scope, overrides?, idempotency_key}` → `RunAccepted` | 必填 caller key；fingerprint 与同键重放/冲突语义冻结；事务提交后才返回 accepted，覆盖 Run、目标快照与执行快照。 |
| §3.1 `ControlPipelineRun` | `ControlRun {run_id, action, idempotency_key?}` → `ControlResult` | pause/continue/stop/restart/abandon 逐项映射；只给 restart 要求 key；响应包含原 Run 权威状态，restart 另回 child ID/status。 |
| §3.1 `ResumeBlockedRun` | `ResumeBlockedRun {run_id}` → `ControlResult` | 条件解除且成功重新规划才回到 pending；条件未满足拒绝且无副作用。保持为单独逻辑操作，不塞进五个 `ControlRun` action。 |
| §3.1 `RetryFailedTargets` | `RetryFailedTargets {run_id, idempotency_key}` → `RunAccepted` | key 必填；仅 CompletedWithFailures 且有失败 Page 时新建 Run；只含原 Run 冻结失败 Page，源 Run 不变。 |
| §3.1 `GetRun` / progress query | `GetRunSnapshot {run_id}` → `RunSnapshot`；`GetTaskProjection {run_id}` → `TaskProjection` | 明确拆成权威 Run 快照与只读投影；前者列出接受时有序 targets，后者保持 §6.1 字段。 |
| §3.2 command/scope/目标集合冻结 | StartRun acceptance + `RunSnapshot.targets` | scope、command 与接受时目标不因后续 selection 变化；不提供扩大/缩小既有 Run 的 wire 命令。 |
| §3.3 Run / Page Task / StepRun 区分 | Run 快照、TaskProjection、RetryFailedTargets | Run 是批次；Page Task/Step 状态进入只读投影；重试失败 Page 创建 linked 新 Run，单 Step 网络重试仍留在原 Run/Task。 |
| §4.2 全部合法转换；§4.5 非法拒绝 | `ControlRun`、`ResumeBlockedRun`；§5.5 全状态矩阵 | 每一合法 action 及所有状态拒绝均在契约表列出；状态非法统一 `INVALID_RUN_TRANSITION`，不得产生副作用。scheduler start/recovery 留在 Core 内部。 |
| §5.3 用户重试失败 Page | `RetryFailedTargets` + idempotency key | 新 Run 只含失败 Page，带 source/retry metadata；原 Run、StepRun、错误与成功成果不改写。 |
| §6 崩溃恢复 / Continue / Restart / Abandon | Core startup recovery；`GetRunSnapshot`；`ControlRun` | 恢复扫描不是外部命令；仅在旧 scheduler owner 已退出后将 Running 标 Interrupted。快照查询与三种处置 wire 分开；Continue 沿原快照，Restart 创建新 Run，Abandon 不创建 Run。 |
| §7.1 唯一 scheduler | 上述 Run commands 进入 Core `PipelineService` / 单一 `PipelineStore` seam | wire 不暴露 executor、并行 worker 或影子队列；§12 授权受 P13 allowlist 与单一 owner 约束。 |
| §7.2 TaskProgress / PageList 同源 | `GetTaskProjection` + §6.1 `TaskProjection` | counts、rows、current Page/Step、errors 与 controls 从同一权威 Run/Task 数据生成；投影只读，UI 不自行重算。 |
| §7.3 刷新与重要事件 | `RunProgressChanged`；`TaskFailed`、`RunPaused`、`RunCompleted`、`CurrentPageStepChanged` | 普通进度仍约 4 Hz；四类重要状态在对应持久变化提交后立即推送。事件仅作提示，快照仍是真值；不增加 replay/order 保证。 |

## D08 五组 AC

| D08 AC | Wire carrier | 覆盖结论及保留边界 |
|---|---|---|
| `AC-PAUSE-001` | `ControlRun(pause)` → `ControlResult` | 可报告已持久化请求与当下权威状态；≤200 ms“正在暂停”是 P14 UI 呈现目标，调用方可在 IPC 往返期间显示本地 pending，wire 不宣称单独满足时限。阈值不变。 |
| `AC-PAUSE-002` | `ControlRun(pause)`、`RunPaused`、snapshot | 事件只在安全边界后的 paused 状态提交后发送；当前 Step 可完成、不得留下半 Commit，完全沿 P11。 |
| `AC-PAUSE-003` | `ControlRun(continue)`、snapshot/projection | Continue 使用原接受快照，从首个未完成/stale Step 继续；已成功且有效 Step 不重跑。 |
| `AC-STOP-001` | `ControlRun(stop)` → `ControlResult` | stop 只停止剩余工作，不提供 Delete/Rollback；Run 与已提交结果由 P11 保护并可从 Core 状态读取。 |
| `AC-STOP-002` | `ControlRun(stop)` + `TaskProjection` | Pending stop 转 Cancelled，未启动 Task 转 cancelled；不新增 Page 状态词或 UI glyph。 |
| `AC-STOP-003` | `ControlRun(stop)` + `GetRunSnapshot` | Stop wire 无删除历史/Artifact/Revision 的动作；持久对象存在性仍由 P11/Core 数据保护与其既有读取验收验证，本契约不新增 Artifact 查询。 |
| `AC-CRASH-001` | Core startup recovery + `GetRunSnapshot` | owner 退出确认后 Running → Interrupted；重连/重启后可读权威状态，不从 UI timeout 猜测崩溃。 |
| `AC-CRASH-002` | `ControlRun(continue)` + snapshot | 沿原快照继续，已完成 Step 不重复，未安全提交 Step 可重跑。 |
| `AC-CRASH-003` | `GetRunSnapshot` / projection；P11 §6.3 write boundary | IPC 不提供临时产物晋升入口；current ArtifactRevision 只由 Core 安全提交边界决定。临时文件清理/DB 原子性仍是 P13 runtime 验收。 |
| `AC-RETRY-001` | `GetTaskProjection` / snapshot | 同 Run 的失败状态与上游有效 Step 可投影；P11 §5.1–§5.2 限制网络重试并复用有效上游，不增加 wire 重跑命令。 |
| `AC-RETRY-002` | `RetryFailedTargets` + key；新 Run snapshot | 新建只含失败 Page 的 Run，原 Run 历史保留；同键重放返回既有 child，异 fingerprint 拒绝。 |
| `AC-PROGRESS-001` | 不依赖新增 wire | 固定底部 `TaskProgressPanel` 是 P14 UI 要求；新 wire 不改变 UI 布局或以弹窗替代。 |
| `AC-PROGRESS-002` | `GetTaskProjection` | 投影字段承载任务名、百分比、Step、Page、完成/失败/阻塞/跳过/等待统计与 controls。 |
| `AC-PROGRESS-003` | `current_page_id` + `CurrentPageStepChanged` | 提供 PageList 定位所需当前 Page ID；滚动动作仍由 P14。 |
| `AC-PROGRESS-004` | `rows[].status/error_code`、failed count | 提供失败 Page 集合供 UI 筛选；筛选交互仍由 P14。 |
| `AC-PROGRESS-005` | `rows[].status`、completed/skipped counts | 提供已完成/跳过 Page 集合；展示与筛选交互仍由 P14。 |
| `AC-PROGRESS-006` | `run_status` + `RunCompleted` | `completed_with_failures` 单独可表达，成功 Page 不被聚合为全体失败。 |
| `AC-PROGRESS-007` | `TaskProjection.rows` | panel 与 PageList 明确要求消费同一个 projection/source，避免 completed/running 双重显示。 |

## 覆盖结论

D08 五组共 18 条 AC 均有 wire carrier 或明确的 P14 UI/Core 持久化责任边界；其中 UI-only 的 `AC-PAUSE-001` 时限和 `AC-PROGRESS-001` 固定布局不被谎称为 IPC 能保证。契约没有新增用户可见操作或降低阈值。以上是静态契约对照，不是运行验证；P13 的 runtime 与全部产品验收仍待实现和测试。
