# P13 外部决策阻塞

状态：`BLOCKED_WAITING_EXTERNAL_DECISION`  
基线：`6cf045b853a892880fc06ab8c42632311a99a941`  
检查日期：2026-10-16

P13 不能在当前允许修改路径和冻结 IPC 边界内完整落到生产 Core。以下是代码/契约事实，不是推测：

1. **AC1 与生产入口：幂等键缺少合法 wire 输入。** P11 §2.1 要求 StartRun 调用方提供 `idempotency_key`。冻结的 `M2-C1_TYPED_IPC_CONTRACT.md` §5 StartRun 输入只有 `{command, scope, overrides?}`，没有幂等键；§12 说明该契约本身不授权 Python IPC Runtime。`CoreServiceServer.dispatch_request` 当前没有 StartRun/ControlRun/GetRunSnapshot/GetTaskProjection/RetryFailedTargets handler。增加命令或把 key 塞进既有字段会新增/改变 wire 语义，违反用户设定的 AC8 和“立即停止”约束。不能将 `request_id` 偷换成幂等键：请求关联 ID 不是 P11 所需的跨超时重放 key。

2. **AC1/AC4(c)：生产 Store 没有相应原子操作，且实现文件不在 allowlist。** `SqlitePipelineStore.put` 在单个 SQLite 事务中写一个 Run 与其 targets/tasks/steps，但无持久 idempotency-key 查重接口，也无多 Run 原子写接口。Restart 需一次性写 parent 的 `interruption_disposition` 与 child Run 来源；现有 `PipelineService.control_run` 是两次 `put`。实现可靠事务需修改生产 adapter `src/infrastructure/sqlite/pipeline.py`（可能还需 Schema/migration），而 P13 明确只允许 `src/application/tasks/**`、`src/bootstrap/core_service.py`、`src/bootstrap/core_assembly.py`。不能在 application 层复制 SQL、建立影子 store 或绕过 PipelineStore。

3. **AC3/AC6：生产 Core 没有 Run scheduler worker/ownership gate。** `core_assembly.py` 在装配时直接调用 `pipeline.recover_running_runs()`；当前 `PipelineService` 可被多个实例构造，SQLite connection 本身不提供 scheduler owner lease。此次部分改动只用单个 PipelineService 实例内的非阻塞锁拒绝并行 `execute_run`，不能证明跨实例/进程的唯一 owner，也不能提供 Start/Control/Recovery 的统一 Core 调度入口。接上产品入口需要第 1 项的 Runtime 命令授权；另需明确 SQLite owner 获取与释放的获准 seam。

4. **AC5：规定的重试策略在 allowlist 外。** 现有 Provider retry 在 `src/infrastructure/providers/retry.py` / `runtime.py`：policy 的 `max_attempts` 包含首次调用，默认 2（因此仅 1 次额外尝试），没有 P11 所需 1s/2s 两级退避和 `Retry-After` 支持；settings 还可覆盖该值。P11 要求最多 2 次额外尝试并优先遵守未截断的 `Retry-After`。在 scheduler 任意重跑 `StepExecutionError` 会违反错误分类和每次 attempt 的 StepRun 要求；正确 provider 层修改文件不在本 Task allowlist。

5. **AC7：Core 查询/事件面不存在。** `build_projection` 是现有 application 只读投影，但 Core stdio 没有 Run 查询或控制入口，也没有 Run 状态事件用于重要状态立即刷新。仅有 service 投影无法交付 P11 §7.2–§7.3 的生产 Core consumer seam。增加 wire 命令/event 会触及被冻结的 IPC 合同。

## 已完成且保留的授权范围切片

- AC4(a)：Pending.pause 拒绝且无副作用。
- AC4(b)：Blocked.stop 取消尚未开始 Task 并提交 Cancelled。
- AC4(d)：仅 CompletedWithFailures 可 RetryFailedTargets。
- 完整 Run control 非法动作矩阵、Blocked replan 状态门，以及单个 `PipelineService` 同时仅允许一个 `execute_run` owner 的判别测试。
- 没有修改 IPC 契约、SQLite adapter/schema、Provider retry、旧 UI、用户数据或主仓。

## 恢复条件

由 Coordinator/用户另行裁决以下一项或多项后重新认领：

- 为 StartRun 幂等键与 Run control/query/event surface 冻结 wire 行为并授权相应 IPC runtime 修改；或提供不改变 wire 的受授权 Core 内部调用方方案。
- 将 `src/infrastructure/sqlite/pipeline.py`（以及如确需的 migrations）加入 P13 的最小修改范围，允许同一 PipelineStore 实现 durable idempotency 与 Restart 多 Run 原子写。
- 将 provider/network retry adapter 的必要文件加入 P13 allowlist，或将 P11 retry 落地另立有依赖的 Task。
- 明确唯一 scheduler owner 的获取/释放机制，并允许生产 Core 入口/worker seam 的实现与验证。

在恢复条件满足前，不得声称 P13 或 AC1–AC9 完成，不得更改 frozen IPC wire、绕过 `PipelineStore`、扩展未授权目录或将本部分修复合并进主线。
