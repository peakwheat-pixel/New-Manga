# 裁决：P15-CORE-1 的 G23-Test 目标缺口（2026-10-17）

- **裁决人**：Coordinator dsh（epoch 6）。**触发**：P15-CORE-1 Owner（Codex）在实现前**失败关闭**并上报。
- **结论**：**阻塞成立**，Owner 处置**正确**（拒绝自选公网目标、拒绝伪造阶段结果、拒绝把 Proxy 主机冒充 TLS/HTTP 目标）。本裁决**驳回**"直接把 `provider_profile_id` 当既有可选参数实现"的简化处置，因为它在**缺省路径上会产生假阳性**。

## 1. 缺口事实（已核实）

[P15_SETTINGS_IPC_CONTRACT.md](../contracts/P15_SETTINGS_IPC_CONTRACT.md) **§5.2**：

- `TestNetworkProfile { network_profile_id, provider_profile_id? }`——`provider_profile_id` **可选**；
- L194-195：`status: passed | failed`——**没有第三种终态**；
- L202：`NotRunReason = … | provider_profile_not_selected | direct_mode`；
- L212：`status=failed` **必须**指向**唯一** `failed` 的阶段。

**推论**：当 `provider_profile_id` 缺省且模式为 Direct/System 时，**没有任何目标主机**可供 DNS/TCP/TLS/HTTP 探测 → 这些阶段只能 `not_run`/`not_applicable` → 因无失败阶段，**唯一可表示的 `status` 是 `passed`** → **契约迫使系统在"什么都没测"时报"通过"**。这是**契约缺陷**，而非实现者能力问题。

## 2. 裁决

**(A) 需要一次契约修订（新 Task `P15-C1-FU1`）**，二选一（我建议 **A1**）：

| 选项 | 内容 | 评价 |
|---|---|---|
| **A1（建议）** | **要求 `provider_profile_id` 必需**：`TestNetworkProfile { network_profile_id, provider_profile_id }`。目标恒为**该 Provider 的 endpoint**（经所选 Network Profile 的代理路径）→ 六阶段全部有确定语义（末阶段 ProviderAuth 本就需要 Provider） | 语义最干净、最安全（**无任意 URL**）、与设计"最后一阶段是 ProviderAuth"一致；缺省时按 §5 既有规则返回 `INVALID_REQUEST` |
| **A2** | 保留可选，但**新增第三终态** `status: passed \| failed \| not_testable`，并要求全 `not_run` 时降级为 `not_testable`（可配 `NotRunReason`） | 保留"仅测代理连通"的能力；但引入新终态需同步 UI 状态矩阵与 §9 投影 |

**(B) 明确禁止**：不得自选公网 URL、loopback 或假目标；不得把 Proxy 主机冒充 TLS/HTTP 目标；不得用伪造阶段结果满足 AC2。**这三条由本裁决固化为规则**。

**(C) 拆分 P15-CORE-1**（Owner 建议已采纳，因任务确实过大）：

| 子 Task | 范围 | 释放条件 |
|---|---|---|
| **P15-CORE-1A** | **G21 Provider 面**（profiles/bindings/run snapshot）+ **G24 覆盖解析**——语义完备、**不受本缺口影响** | 可**立即**释放（不必等契约修订） |
| **P15-CORE-1B** | **G22 凭据面**（`Bind/ClearProfileCredential`）+ **G23 Network Profile CRUD/默认/解析**（**不含 `settings_network_profiles_test`**） | 可**立即**释放 |
| **P15-CORE-1C** | `settings_network_profiles_test`（六阶段） | **必须等 `P15-C1-FU1` 关闭**（目标语义定案）后方可释放 |

## 3. 教训（新登记 BL-21）

我的**派发前置核对**只验证了"**命令是否存在**"，**未验证"每条命令的语义是否完备"** → 才让 Owner 在开工后才撞上缺口。**规则**：(1) 释放实现类 Task 前，必须对契约逐条做**语义完备性核对**（目标/输入/终态/失败语义是否闭合）；(2) 派发提示**必须要求 Owner 引用契约原文行号**来支撑"缺语义"的主张（本次 Owner 引用了 §5.2 与 L194/L202/L212，**正是这种引用让裁决可迅速、可靠**）；(3) Owner 侧"失败关闭 + 不伪造"的纪律**再次验证有效**。
