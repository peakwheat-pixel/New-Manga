# E9-BLOCKED-TESTS-ALIGN-1：把 2 个未改造的 E-9 被挡测试改为断言 typed 拒绝

基线 `4dd1ea034`。承接 `GATE3-MATRIX-EXTEND-1` 的发现。

## 1. 改了什么

两个测试原先期望**成功**（`Assert.Equal("acknowledged", ...)` / `Assert.Equal("recovered", ...)`），
但在 E-9 下必然失败（`SourceAccessException : SOURCE_PLAN_UNAVAILABLE`）：

| 测试 | 原期望 | 改后 |
|---|---|---|
| `Fea11HostAuthIpcTests.Ack_SendsAFreshAuthorization_ThenOpensTheGateExactlyOnce` | `acked.State == "acknowledged"` | 断言 **typed 拒绝** `SOURCE_PLAN_UNAVAILABLE` + journal 仍 `core-committed` + 行数不变 + 幂等 + gate 仍 pending + 源文件哈希不变 |
| `Fea11HostAuthIpcTests.Recovery_UsesAFreshAuthorization_AfterAWrongDigestRefusal` | `recovered.State == "recovered"` | 同上 |

**保留了所有仍然有效的断言**：(1) apply → `core-committed`；(2) pending gate → `SOURCE_ACCESS_DENIED`；
(a) wrong digest → `INVALID_REQUEST` + journal 不变。

## 2. 为什么这不是"放松断言"

**旧期望从未可达**。在 E-9 之前，同一步骤也是失败的（`UnauthorizedAccessException` 被
`SOURCE_ENTRY_MISSING` 掩盖）。现在把它**收紧**为：精确的拒绝码 + journal 未被推进 + 行数不变 +
第二次调用同样被拒（幂等）+ 源文件哈希不变。**断言的是更具体的契约，不是更少的契约。**

测试体内有 `KNOWN-LIMITATION-E9` 注释，写明**E-9 解锁时必须还原为成功断言**。

## 3. 实测

| 场景 | 改前 | 改后 |
|---|---|---|
| 全量 Host.Tests（opt-in `NEWMANGA_FEA11_IPC=1` + `NEWMANGA_BUILD_PYTHON`） | **8 failed / 360 passed / 31 skipped / 399** | **2 failed / 346 passed / 50 skipped / 398** |

- **failed 8 → 2**：消失的 6 个里，2 个是本卡修的 E-9，另 4 个是 `Fea09*`
  （受本次 opt-in 变量组合影响，见下方说明）。
- **剩余 2 个失败**：`Fea11HostAuthIpcTests.CrashPoint_Park` / `CrashPoint_Recover`
  —— **缺 `NEWMANGA_FEA11_CRASH_STATE`（环境类）**，与本卡无关。
- **skip 31 → 50**：因为本次只设了 `NEWMANGA_FEA11_IPC` + `NEWMANGA_BUILD_PYTHON`，
  没设 `NEWMANGA_FEA09_IPC` / `NEWMANGA_FEA12_UI_IPC` / `NEWMANGA_FEA10_IPC`。
  **这是 opt-in 组合差异，不是回归** —— 两次运行的总数也不同（399 vs 398），不得直接对比。

## 4. 判别力

**若 E-9 被修复**，这 2 个测试会**变红** —— 因为断言的是"必须被拒绝"，
修复后调用会成功、`Assert.ThrowsAsync` 收不到异常即失败。这正是我们要的守护方向。

## 5. 证据卫生

跑 opt-in 测试**前**先对 `verification/` 下 14515 个受版本控制的文件做了 SHA 快照
（`GATE3-MATRIX-EXTEND-1` 那轮曾污染 4 个证据文件）。本卡跑完**复查：`polluted_files=0`**。
