# E9-PATH-AVAILABILITY-1：容器路径在 journal 写入点是否可得 —— 结论：不可得

基线 `ed7c323fe`。回答 `E9-CARRIER-CORRECTION-1` 的待裁决问题 1。

## 结论

**在现有架构下，operation journal 的每一个写入点都拿不到容器路径。**

| 写入点 | 签名/上下文 | 有路径？ |
|---|---|---|
| `SourceOperationCoordinator.Begin` | `Begin(planId, planDigest, kind, requestDigest, operationId?, grantIds?)` | **无** |
| `SourceOperationCoordinator.Authorize` | `Authorize(operationId, authorizationJson, hostReceiptId)` | **无** |
| `SourceOperationCoordinator.MarkCommitted` | 只带 receipt | **无** |
| `HostOperationOrchestrator` 的 `payload`（apply 请求体） | 只读 `authorization` / `grant_ids`（`:74` `:215` `:234`） | **无** |
| `registryAuthorizations[]` | 只含 `registry_id` / `generation` / `identity_digest`（`:97-99` `:260-262`） | **无** |
| `HostAuthorizationMinter.Mint` | 只接收上述 authorizations | **无** |

**唯一知道容器路径的地方**是 `SourceReadCoordinator.IssueLockedAsync` 的 `sourcePath`
（`Registry.Authorize(registryId, generation, [path])`，`:564`），但那是**Run 授权链**，
与 **operation journal** 是两条独立的链，中间没有传递通道。

## 因此只剩两个选项

**选项 2（扩 Core）**：让 Core 的 scan target 或 plan materialization 增加容器路径。
- 成本：改 wire 契约 + Python Core + 消费端
- 语义疑点：Core 是**业务数据持久化权威**，Host 的容器路径属于 Host 侧授权材料；
  把它塞进 Core 是**跨职责**

**选项 3（接受现状为能力限制）**：保持 typed 拒绝，并在产品文档中明确
"zip/cbz/pdf/image 来源的崩溃恢复不受支持（仅 folder 支持）"。
- 成本：**零代码**，只需文档与 UI 提示
- 风险：用户可能在其来源崩溃后**无法恢复**，且只有 `SOURCE_PLAN_UNAVAILABLE` 这一句话

## DSH 的技术判断（不是产品裁决）

倾向**选项 3**：选项 2 的跨职责成本与收益不成比例（为 1 个恢复能力把 Host 授权材料搬进 Core）。

**但这属于产品取舍**（"是否限制 zip 来源的崩溃恢复能力"），按 goal 要求应派 codex/zcode 裁决；
上一轮 codex 因 Windows 740 无法读代码，**该裁决尚未作出**。

## 未做

- 未改代码。
- 未派新裁决（codex 上次不可用；zcode 候选未试）。
- 带 opt-in 三类基线仍 **12 passed / 1 failed**；条件 3 仍不判 MET。
