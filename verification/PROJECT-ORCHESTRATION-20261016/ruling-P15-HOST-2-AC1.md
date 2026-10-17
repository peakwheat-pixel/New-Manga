# 裁决：P15-HOST-2 的 AC1（凭据入口命名与调用关系）2026-10-17

- **裁决人**：Coordinator dsh（epoch 6）。**触发**：P15-HOST-2 Owner 在 **AC1 硬门**处**正确停止并上报**（`f268588c7`，仅文档、未动产品代码/契约）。
- **结论**：**契约已唯一确定**，**无需契约修订**。歧义源于**未并读 §1/§2 的命令名映射表**与 §4.1 的消息形状，二者**一致且互不冲突**。

## 1. 依据（契约原文）

| 依据 | 原文要点 |
|---|---|
| **§1/§2 命令名映射表（L20-30）** | 表头明写"新增 **WebView→Tauri 命令名**固定如下"；列名为 `Tauri command` / `Core operation`。**L27 行**的 `Tauri command` 列为 **`credential_put` / `credential_clear`** |
| **§4.1（L109）** | "**WebView 只能调用以下无 Secret 的 production-only Host 命令**" |
| **§4.1（L111-117）** | `PutCredential { target, intent } -> { state: configured, masked_hint? }`；`ClearCredential { target } -> { state: missing }` —— **消息/DTO 形状** |
| **§4.1（L119）** | "`PutCredential` 由 Tauri Host 提供 **WebView 外**的 Host 所有安全输入面。Secret **不进入** React/WebView 内存、Tauri invoke payload、Core 普通 settings DTO、日志、事件或任何错误。用户取消只返回脱敏 `cancelled`" |
| **§3.2（L58）与 §1 表** | 同一约定旁证：PascalCase 为**消息类型**（`CreateProviderProfile`），snake_case 为 **Tauri 命令名**（`settings_provider_profiles_create`） |

## 2. 裁决（**可直接实现**）

1. **WebView 可达的 Tauri 命令名 = `credential_put` / `credential_clear`**（snake_case，按 §1/§2 L27 的 `Tauri command` 列；与其余 17 条设置命令同一命名面）。
   `PutCredential` / `ClearCredential` **是消息/DTO 类型名**，**不是** Tauri 命令名。
2. **请求/响应形状**：逐字按 §4.1（L112-117）——`credential_put` 请求 `{ target: CredentialTarget, intent: create | replace }`，响应 `{ state: configured, masked_hint?: string }`；`credential_clear` 请求 `{ target }`，响应 `{ state: missing }`。**两者 payload 均不含 Secret**。
3. **调用关系（L109 + L119 合并读法）**：
   - WebView **仅**以**无 Secret** 的 `credential_put`/`credential_clear` invoke 触发流程；
   - **Host 在 WebView 之外**提供 Host 所有的**安全输入面**采集一次性 Secret（不进入 WebView 内存或 invoke payload）；
   - Host 写入受保护 Credential Manager → 得到新 `CredentialRef` → **经受信 Host→Core 调用** `BindProfileCredential`（`credential_clear` 对应 `ClearProfileCredential`）；
   - Host 只向 WebView 返回 `configured`（可含允许的 masked hint）或**脱敏** `cancelled`；错误只走契约 **§9 封闭投影**。
4. **`BindProfileCredential` / `ClearProfileCredential` 恒为仅 Host→Core**：**不得**进入 `PRODUCTION_COMMANDS`、`command_allowlist` 或任何 WebView `generate_handler!`（P15-HOST-1 已建立此边界，本 Task **不得**破坏）。
5. **`intent` 状态匹配**（L121）：`create` 仅当状态 `missing`，`replace` 仅当 `configured`；不匹配 → `conflict` 且**保留原绑定**；每次调用**仅采集/提交一次**，重试须重开安全输入；Host 在 Credential Manager 调用后**清除临时明文缓冲**。
6. **AC4 计数**：本条新增 **2 条 WebView 命令** → `PRODUCTION_COMMANDS` 由 **47 → 49**；**probe 7 / AC1 6 冻结面不变**；ACL/permissions 按真实值更新（`generate_handler` production 块 49）。此数值须以**合并后真实值**为准并在测试中断言（**不得删除**既有断言）。
7. **AC3 凭据通道**：把 `bind/clear_profile_credential` 的 `unavailable("P15 credential channel is unavailable")` **失败关闭桩**接成真实可用；若 OS/依赖确实不可用 → **失败关闭 + 如实声明**，**不得**伪造成功。

## 3. 过程记录（正向）

Owner 在**命名/调用关系未定**时**停止并请求书面裁决**（而非自行发明 wire 或选择一种解释实现），完全符合"契约有歧义先上报"的纪律；其文档提交**未触碰**产品代码、契约、`STATUS`、`REBASELINE_PLAN` ✓。本裁决同时**驳回**"需要契约修订"的前提：**契约无需变更**，只需**把 §1 映射表与 §4.1 并读**。
