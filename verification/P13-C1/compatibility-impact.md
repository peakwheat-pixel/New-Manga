# P13-C1 Runtime IPC 兼容性影响

- 修订基线：`c33033dc02c4373d3a3a35333a2c7aeac03c7ce6`
- 新契约：`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` rev `2.0`
- 当前代码事实：`src/bootstrap/core_service.py` 在基线为 `new-manga.core` major 1 / minor 6，按 major 校验；无 Run handlers、无异步事件输出。M2-C1 在基线的 proposal envelope 为 major 1.0，`StartRun` 无 `idempotency_key`。

## 破坏性变化

1. Run contract 从 major 1 升至 major 2。major 1 endpoint/client 按 §3.2 必须以 `PROTOCOL_VERSION_UNSUPPORTED` 拒绝不匹配版本；客户端与支持 Run Runtime 的 Core 必须一起升级到 major 2。
2. `StartRun.idempotency_key` 成为必填。旧 StartRun payload 不兼容；`request_id` 仅用于本次 request/response 关联，不能替代幂等键。Restart 与 RetryFailedTargets 同样要求调用方提供 key。
3. stdout JSONL 从“一条请求对应一条响应”扩展为可混合 Response 与异步 Event。旧客户端若把任意输出行都当作 response，会误读事件；major 2 客户端须按 `request_id` 分流响应并独立消费 Event。
4. Runtime 不提供 major 1/2 双协议回退，也没有协商/自动迁移语义。若后续决定部署期双版本并存，需单独修订契约并验证；本次不承诺此兼容模式。
5. Run command surface 仅在目标 major 2 内冻结：Restart 的 `ControlResult` 在 `new_run_id` 之外增加 `new_run_status`，同键重放返回 child Run 当前状态；`TaskProjection` 增加 `tasks[].steps[]` 错误/重试与可得执行详情。基线没有这些 Run handlers 或消费者，因此它们不是已有已部署字段的原位改型；major 1 consumer 仍须升级，major 2 consumer 按本次完整形状实现。

## 向后兼容范围

- 已有命令的 payload、result、错误码与业务语义保持不变；但 major 版本变化仍要求已有消费者升级 envelope/version。不存在“旧 major 客户端无需改动即可连接”的承诺。
- `new_run_status`、Task/Step 详情均属于此前未实现的 Run wire 面；未知 Provider / Model / Device 返回 `null`，Core 不得由当前全局设置猜测。错误消息服从 §8 安全短消息约束，不含 raw detail、栈、路径或 secret。
- 基线没有 React/Tauri ↔ Python Core 的 Run Runtime，也没有已实现的 Run consumers；因此无法声称存在已部署的 Run 客户端兼容性。当前 Core stdio 命令面仍是 1.6，rev 2.0 是目标契约而非代码现状。
- 兼容影响只在 Python IPC Runtime 范围内。React/Tauri/Rust、数据库 Schema、migration、依赖和产品代码均未由本次文档 Task 修改。

## 决策依据与实施门

协议 §3.2 把新增必填字段列为 major 变更；事件与 Response 共用 stdout 又改变了严格一请求一响应读取假设。为避免 major 1 consumer 静默忽略幂等键或误读事件，选择 major 2。该选择不新增产品行为，且满足 P11 durable acceptance。P13 实现 Task 须更新其 Core/client 版本使用、测试拒绝旧 major，并验证事件/response 混读；P13 Task 已冻结的 Python allowlist 与独立 Gate 继续生效。
