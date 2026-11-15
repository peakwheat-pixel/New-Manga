# E-9 已知限制登记（非冻结契约）

**状态：已由 ZCode 裁决采纳（2026-11-15）；本文件是登记入口，不是契约本体。**

## 为什么单独建文件而不是改 C-17

`doc/plan/FEA-CONTRACT-FROZEN-C17.md` 是**冻结契约且被 pin 覆盖**
（其附录 §"v1.2 UNFREEZE 重冻记录" 写明 `verify_pins` 三指纹与 `truth 17 OK + C17 OK = 18/18`，
工作树字节 `cdeee4872e29b56c7d67de65dabd6ca9b31006eecde61d99b83e29fe5a4fc96c`，58134 bytes）。

**改它需要走正式 UNFREEZE 流程**（新载体 + 独立字节复核 + 三指纹重算），
而本限制**不需要改契约语义**：契约定义的是"恢复需要容器路径"，产品只是**暂时无法提供该路径**。
故登记于此，并在 C-17 与 E-9 finding 之间建立引用。

## 限制本体（按 ZCode 核实的真实口径）

**非 folder 来源（`zip` / `cbz` / `pdf` / `image`）的 source **sync 完成链不可用**。**

具体：
- `SourceOperationCoordinator.AcknowledgeAsync` 与 `RecoverAsync` **都走同一次 fresh re-mint**；
- 该 re-mint 需要容器路径，而 **journal / plan materialization / apply payload 六个入口全都没有它**
  （证据：`verification/E9-PATH-AVAILABILITY-1/README.md`）；
- 因此 Host **typed 拒绝**，错误码 **`SOURCE_PLAN_UNAVAILABLE`**；
- 后果：ACK 失败 → gate 停 pending（`source_sync.py:150`）→ **新 binding 不可读**。

**`sourceKind == "folder"` 不受影响**（root 目录恰好就是容器）。

### 表述纪律

**不得**写成"仅崩溃恢复不可用" —— 那**低估**了影响面：**正常 ACK 同样不可用**。
ZCode 明确核实过 `AcknowledgeAsync:468` 与 `RecoverAsync:581` 是同一路径。

## 数据安全边界（ZCode 保留给用户的第二点）

**只挡"读门打开"，无业务数据损坏**：apply 阶段已 `core-committed`，
源文件、旧 binding 的 `verified_digest`、旧 entry digest 均不变（由
`E9-KNOWN-LIMITATION-TESTS-1` 的三条新增断言固定住）。

## 解锁条件

实现 **mint-time 路径映射**（ZCode 登记的后续 Task 候选）：

- 在 `SourceReadCoordinator.IssueLockedAsync` 处（它**手中已有真实容器路径**）持久化
  **Host 侧 DPAPI 映射** `registry_id → container_path`；
- 恢复时取候选路径，**身份仍经 `IssueAsync` 的全量物理 facts 验证**（路径失效 = typed 失败，fail-closed 保留）；
- **不动 wire / Python Core / apply payload**；但属**新增持久授权材料**，需契约小节 + 安全审查；
- 落地后**回退本限制**（并新增"非 folder 恢复成功"的正向测试）。

## 被这条限制挡住的测试

**已按裁决改造（断言 typed 拒绝）**：

- `Fea11Residual4AIpcTests.ProductionDispatcherFullSyncChain_NewKeyOldDigestConserved`
  （opt-in `NEWMANGA_FEA11_IPC=1`）—— 改为断言 typed 拒绝，标记 `KNOWN-LIMITATION-E9`。

**★ 2026-11-15 补登（`GATE3-MATRIX-EXTEND-1` 实测发现，此前未登记）**：

在 `NEWMANGA_FEA11_IPC=1` 下实测 Host.Tests 为 **8 failed / 360 passed / 31 skipped / 399**，
其中**两个失败**的直接原因是 E-9，但**从未登记在本文件**：

| 测试 | 实测失败原因 |
|---|---|
| `Fea11HostAuthIpcTests.Ack_SendsAFreshAuthorization_ThenOpensTheGateExactlyOnce` | `SourceAccessException : SOURCE_PLAN_UNAVAILABLE` |
| `Fea11HostAuthIpcTests.Recovery_UsesAFreshAuthorization_AfterAWrongDigestRefusal` | `SourceAccessException : SOURCE_PLAN_UNAVAILABLE` |

**处置口径**：这两个测试**尚未按裁决改造**，仍是**原始的"应当成功"断言**，因此在 E-9 下必然失败。
**不得**为了让它们变绿而放宽断言或改 skip。
可选动作（需裁决）：按与 `ProductionDispatcherFullSyncChain` 相同的方式改为断言 typed 拒绝，
标记 `KNOWN-LIMITATION-E9`；**或**保持红并计入"E-9 未登记影响"清单。

### ★ 更正（2026-11-15，`FEA11-CRASH-STATE-1` 实测）—— 两种场景必须分开写

此前把 `CrashPoint_Park` / `CrashPoint_Recover` 都归因为"缺 `NEWMANGA_FEA11_CRASH_STATE` 环境变量"。
**这个说法只对一种场景成立**。实测后必须分成两栏：

| 场景 | `CrashPoint_Park` | `CrashPoint_Recover` | 归因 |
|---|---|---|---|
| **全量 `dotnet test`（未设 `CRASH_STATE`）** | **fail**（`Assert`："NEWMANGA_FEA11_CRASH_STATE is required"） | **fail**（同上） | **环境**（两个都是测试自身的前置断言失败） |
| **真实驱动 `crash-ack.ps1`（驱动自己设 `CRASH_STATE`）** | **通过** —— 跑到 `core-committed` 并被成功 kill | **FAIL：`SourceAccessException : SOURCE_PLAN_UNAVAILABLE`** | **E-9**（`RecoverAsync` → `MintRecoveryGrantsAsync`） |

**驱动实测输出**（`verification/FEA-11-HOST-AUTH-3/tools/crash-ack.ps1`，301 行：park → kill 整棵进程树 → recover）：

```
NewManga.Host.Sources.SourceAccessException : SOURCE_PLAN_UNAVAILABLE
  at SourceOperationCoordinator.MintRecoveryGrantsAsync(...)
  at SourceOperationCoordinator.RecoverAsync(...)
  at Fea11HostAuthIpcTests.CrashPoint_Recover()
CRASH_POINT=NOT_SATISFIED recover_exit=1
EXIT=12
```

**结论**：
- 全量套件里的 2 个 fail **确实是环境**（前置断言），**不是** E-9；
- **但 `CrashPoint_Recover` 一旦在正确环境下真跑，就会撞上 E-9** ⇒ **它必须计入"被 E-9 挡住的测试"**（此前漏记）。
- **不得**为变绿而放宽断言；E-9 解锁后该驱动应能达到 `CRASH_POINT=SATISFIED`。

**另注**：`crash-ack.ps1` 的文件头注释（2026-11-09）写着
"depends on the gated tests ... which are NOT implemented yet -> this driver currently reports NOT_RUN"
—— **该注释已过时**：两个测试都已实现，驱动能真实执行到 recover 阶段（只是在 E-9 下 recover 必然被拒）。
