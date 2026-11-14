# E9-PATH-CARRIER-STUDY-1：修复载体可行性核实（Codex 的 4 条前置条件）

基线 `419d74887`。Codex 被要求裁决"A（journal）vs B（Core plan）"，但**它诚实拒绝**：
其所有命令因 Windows 740 无法启动，**未读到任何代码**，故只给出"倾向 A"的**有条件**意见，
并列出 4 项必须由 DSH 补齐的代码证据。

本卡**补齐这 4 项**。

## 1. `AuthorizationJson` 载体与写入点

| 项 | 结论 |
|---|---|
| 存储载体 | Core SQLite 的 journal 表列 `authorization_json TEXT NOT NULL CHECK (length(authorization_json)>1)`（`src/infrastructure/sqlite/schema.py:808`）—— **Host 内部持久化**，非 wire |
| 写入点 1 | `SourceOperationCoordinator.Authorize():153`（`AuthorizationJson = authorizationJson`） |
| 写入点 2 | `SourceOperationCoordinator.cs:425`（`MintRecoveryGrantsAsync` 重签后回写） |
| 写入点 3 | `SourceOperationCoordinator.cs:658` |
| 生产源头 | `HostAuthorizationMinter.Mint()` 构造字典：`operation_id` / `request_digest` / `authorization_digest` / `authorizations[]` / `host_receipt_id` / `authorized_at` |
| 消费者（读） | `ReadAuthorizationBaselines`（只取外层 `authorized_at` + 内层 `authorizations[].registry_id/identity_digest/generation`）；`Fea11HostAuthTests` / `Fea11HostAuthIpcTests` 多处读整个 JSON 做相等/不等对比 |

## 2. 摘要边界（★ 有发现）

| 摘要 | 计算范围 | 加外层字段会变吗 |
|---|---|---|
| `RequestDigest` | `sha256({operation_id, plan_id, plan_digest, kind})`（`HostAuthorizationMinter.cs:82-88`） | **不会** |
| `minted.AuthorizationDigest` | `sha256(canonical(authorizations[]))`（`:89`） | **不会**（外层字段不在范围内） |
| **`Authorize()` 存的 `AuthorizationDigest`** | **`Sha256Hex(整个 authorizationJson)`**（`SourceOperationCoordinator.cs:152`） | **会变** |

**⇒ 两个写入点对 `AuthorizationDigest` 用了不同的定义**（`:425` 用 `minted.AuthorizationDigest`，
`:152` 用整 JSON 的 sha256）。这是既有不一致，本卡不修，但它**决定了 A 的实施方式**。

**好消息**：全仓**没有任何 `AuthorizationDigest` 的校验点**（只写入，无比较/断言），
已用 grep 确认（除赋值与构造外无其它引用）。

## 3. `JournalEntry.Kind` 取值

`Kind` 存在（`JournalEntry.Kind`），并与 `plan_id`/`plan_digest` 一起参与 `RequestDigest`。
**但**：Codex 指出"即使 Kind 编码了 resync/relink/repoint，它也只能决定恢复分支，
不能证明某条历史记录实际保存了路径" —— **本卡认同**，未据此设计。

## 4. 结论：A 可行，但必须绕开 `:152` 的整-JSON 摘要

方案 A（在 `authorizationJson` 的外层长期记录容器路径）**技术上可行**，但需满足：

1. **新字段不得进入 `Authorize()` 的 `Sha256Hex(整个 JSON)` 范围** —— 否则既有记录的
   `AuthorizationDigest` 语义会被静默改变。可做法：**在 Auth 阶段之后（recovery 回写时）才写入**
   该字段，或**单独存一列**而不是塞进 `authorizationJson`。
2. 读取必须容忍缺失（老记录无该字段 → 保持 typed 拒绝）。
3. **folder 语义不变**。

**因此本卡不建议直接照 A 的"塞进 AuthorizationJson"版本实施** —— 更小风险的等价方案是
**journal 表新增独立列**（如 `container_path TEXT NULL`），它完全不碰任何既有 JSON 摘要与消费者。

## 5. 未做

- **未实施任何代码改动**（本卡只做可行性核实）。
- 未验证 CBZ/PDF/image 恢复是否有其它阻塞点。
- 带 opt-in 三类基线仍 **12 passed / 1 failed**；条件 3 仍不判 MET。
