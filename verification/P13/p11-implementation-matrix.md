# P13 / P11 逐节实现对照表

| P11 条款 | 当前实现状态（base `6cf045b853a892880fc06ab8c42632311a99a941`） | P13 实现方案 | 判别测试 / 证据 |
|---|---|---|---|
| §2.1 请求键 | **缺口**：`PipelineService.create_run` 不接收或保存幂等键/fingerprint；重试和 restart 也不接受 key。 | 仅通过唯一 `PipelineStore` 提供请求键查重及同键冲突拒绝；不能把 UI 选择、settings 或当前 targets 混入 fingerprint。 | AC1：同键重放、异 fingerprint 拒绝、数据库重开后重放。 |
| §2.2 原子 durable acceptance | **部分满足**：生产 `SqlitePipelineStore.put` 在一个 SQLite 事务写 Run、RunTarget、快照；没有幂等索引/accept 接口；仅在事务提交后 `create_run` 返回。 | 将 key、fingerprint、Run、冻结目标和快照经同一 store 原子接受；提交失败不返回 Accepted。若现有 store 无法承载 key/唯一约束，停止越界实现并记 blocker。 | AC1：生产 SQLite 关闭/重开；同键相同/不同请求；事务故障注入。 |
| §2.3 快照与保护边界 | **部分满足**：接受时 `create_run` 展开并冻结目标/顺序、settings、Provider、constraint、context；step commit 校验 revision/Lock。Restart 重新解析，但未原子关联旧 Run。 | 保持快照边界；StartRun key replay 直接返回原 Run；不重展开、不覆盖 current/pinned 或人工成果。 | AC2：接受后改目标、settings、Provider/context，旧 Run 快照不变；恢复提交保护回归。 |
| §3.1 逻辑接口面 | **缺口**：`PipelineService` 有 create/control/recover/retry/progress；Core stdio/IPC 没有 P13 Run handlers。冻结 IPC 合同列有 StartRun/ControlRun 等逻辑面，但 StartRun 载荷未含 P11 key。 | 仅在不新增命令、不改变 wire 语义的前提下接现有 Core seam；不得私自补 IPC 字段。 | `tests/core` 对 Core 现有注册命令和 service seam 的定向断言；wire 变化需求记为 blocker。 |
| §3.2 命令/目标冻结 | **部分满足**：Run 保存 command、scope 和 ordered `RunTarget`；执行使用已保存 targets。 | 保持既有 planner 语义；所有接受重放均读取既有 Run，不再解析当前 scope。 | AC2 目标集/顺序冻结与同键 replay。 |
| §3.3 Run/Page Task/StepRun 边界 | **部分满足**：模型区分三层；Step retry、Run retry 的生产逻辑尚不完整。 | 控制 Run 不混同 Page 失败重试；网络 retry 只新增 StepRun attempt。 | AC5 单步 retry 计数和 failed target 新 Run 来源。 |
| §4.1 Run 状态 | **满足**：模型已有九个契约状态；控制意图单独存放。 | 保持状态枚举，修复非法控制边。 | §4.5 状态×action 拒绝矩阵。 |
| §4.2 合法转换 | **缺口**：Pending.pause 被允许；Blocked.stop 只设置 cancel 标记而不终结；Restart 两次独立持久化；RetryFailedTargets 未限制源 Run 状态。 | 修复状态门；Blocked stop 取消待执行 Task 并持久化 Cancelled；Restart 同一 store 事务；RetryFailedTargets 只对 CompletedWithFailures。 | AC4(a)–(d) 四个旧红新绿测试，逐项留存前后日志。 |
| §4.3 暂停/停止确认 | **部分满足**：Running pause 在执行安全边界持久生效；Pending stop 与 Paused stop 即时取消；Blocked stop 不终结。 | 不提前伪报 Paused；Blocked stop 直接终结剩余工作；不回滚已提交成果。 | AC4(b)、已有安全边界暂停/停止用例。 |
| §4.4 终态语义 | **部分满足**：服务拒绝若干终态操作，但 Restart/Retry 状态门不完备。 | 依表拒绝终态控制；失败 Page retry 创建 child Run，原 Run 历史不变。 | 全状态非法动作矩阵。 |
| §4.5 非法转换拒绝清单 | **缺口**：当前实现没有完整状态×action 防护，且 `Pending.pause`、Blocked stop 行为与契约冲突。 | 表驱动覆盖每种状态允许/拒绝的 control、recover、resume-blocked、retry；拒绝不产生持久副作用。 | AC4 全表参数化测试及 DB 前后快照比较。 |
| §5.1 自动网络重试 | **缺口/待核**：scheduler 将 `StepExecutionError`/任意异常直接记失败；P13 允许路径内尚未见通用、分类后的自动 retry。 | 只重试明确暂时性网络错误，最多额外 2 次，延迟 1s/2s，Retry-After 优先；保护/鉴权/输入错误不重试。 | AC5 可重试分类、最大尝试、退避、Retry-After 与排除类别。 |
| §5.2 失败与上游复用 | **部分满足**：Page 失败聚合为 CompletedWithFailures，保留其他成果；当前没有服务级自动 retry。 | 保持单 Page 失败隔离和有效上游结果，不将 Page 失败升级 Run fatal。 | AC5 多目标聚合；有效上游 Step 不重跑。 |
| §5.3 失败目标重试 | **缺口**：只校验是否有失败 Page，不校验 Run=`CompletedWithFailures`。 | 加状态门，只为失败 Page 创建 source-linked Run，并用 key 幂等。 | AC4(d)，并覆盖 Failed/Running/Blocked 等状态零副作用拒绝。 |
| §6.1 恢复判定/恢复点 | **部分满足**：启动调用 `recover_running_runs`，仅扫描持久 Running；当前调用先于可见的 scheduler ownership 检查。 | 在单一 owner 确认后扫描同一 store；Pending/Paused/Blocked/终态原样保留。 | AC6 SQLite 预置所有状态后重启扫描；所有权竞争测试。 |
| §6.2 Continue/Restart/Abandon | **部分满足**：三条服务路径存在；Continue 重用原 Run；Restart 当前两次 put；Abandon 持久 Cancelled/reason。 | 保持语义分离；Restart 原子写 parent disposition 与带来源 child。 | AC4(c)、AC6 三动作差分测试。 |
| §6.3 重放边界 | **部分满足/待核**：catalog revision/Lock 校验阻止陈旧提交；生产 Step commit 与 StepRun 状态是否同一可恢复事务需实测。 | 已提交有效 Step 不重放；未提交候选不得晋升 current；需要时只重放该 Step。 | AC6 故障注入：candidate/current/StepRun 一致性与恢复。 |
| §7.1 单一 scheduler ownership | **缺口**：PipelineService 是唯一 Run 状态写入口，但没有可验证的跨调用 owner/worker 生命周期；Core assembly 同步恢复后未接 P13 worker。 | 复用单一 PipelineService/Store；显式绑定 Core 线程与 SQLite 连接；不建影子队列/第二 Store。若需更改未授权 IPC 或基础设施路径则停止并记录 blocker。 | AC3 owner 竞争、线程/连接归属、store 唯一实例断言。 |
| §7.2 TaskProgress / PageList 同源 | **部分满足**：`build_projection` 与 service 从同一个 Run 构建投影；TaskProjection 有 Page rows/counts/controls；错误/retry/耗时详情数据有限。 | 继续只读派生 Run/Task/StepRun 投影；不在 Core/UI 另存进度。补齐现有真值可表达的详情字段。 | AC7 投影与同一 Run 的 PageList rows 对照、只读属性/controls。 |
| §7.3 刷新时效 | **缺口/待核**：application projection 是同步函数；Core 无 Run event 通道或 4 Hz 节流器。 | 只在现有 Core 可用事件面实现重要事件立即、普通进度 250 ms 上限；不新增冻结 IPC 事件。 | AC7 时钟注入的节流/重要事件用例；若需新增 wire event 记 blocker。 |
| §9 P13/P14 边界 | **待实现**：当前 Core 仅装配 PipelineService 并在启动恢复；没有 P13 Run runtime consumer seam；P14 UI 尚不存在于本 Task。 | 只交生产 Core lifecycle、控制和只读投影；不实现 React/Tauri UI、不改 D04/D08 或冻结 IPC。 | 范围扫描和 AC8 diff 检查。 |

## 基线与执行纪律

- Worktree：`G:/CODEX/New Manga.workspace/worktrees/P13-RUN-RUNTIME`
- Branch：`codex/P13-run-runtime-control-recovery`
- Base：`6cf045b853a892880fc06ab8c42632311a99a941`
- 表中“旧红新绿”测试必须先在未改生产代码的基线上执行并保存 exit code/日志；之后实现，再以同一用例验证通过。
- 主仓只读。若实现需要修改本表、P11、冻结 IPC、`src/infrastructure/**`、schema/migrations 或 P14 前端，均不得自行越界；记录具体 blocker 与解除条件。
