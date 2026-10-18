# AC6 / AC7：不回归验证与 SHA 校验

日期：2026-10-19 · 执行者：dsh（Coordinator, epoch 8）· 基准 head：`3b4d52766`

---

## AC6：九项回归（R4 Review 同款命令）

对 `apps/desktop/src-tauri` 逐条执行 `cargo test --bin m2rc1-desktop <name>`：

| # | 覆盖项 | 测试名 | 结果 |
|---|---|---|---|
| 1 | R-008 心跳恢复 | `resilient_channel_heartbeat_detects_unresponsive_child_and_recovers` | ok, 1 passed |
| 2 | R-008 心跳上限 | `resilient_channel_heartbeat_unresponsive_child_caps_retries_and_reaches_fatal` | ok, 1 passed |
| 3 | R-003 拆环与 reap | `resilient_channel_shutdown_breaks_cycle_and_reaps_child_process` | ok, 1 passed |
| 4 | R-006 错误呈现（`MAX_RETRIES=3`） | `resilient_channel_caps_retries_and_emits_fatal_after_three_failures` | ok, 1 passed |
| 5 | stdio drop | `stdio_channel_drop_with_unresponsive_session_completes_in_bounded_time` | ok, 1 passed |
| 6 | resilient drop | `resilient_channel_drop_with_in_flight_unresponsive_call_terminates_in_bounded_time` | ok, 1 passed |
| 7 | 外部 kill 后有界且零孤儿 | `resilient_channel_drop_after_external_kill_with_in_flight_call_is_bounded_and_zero_orphan` | ok, 1 passed |
| 8 | shutdown writes（有会话） | `shutdown_writes_protocol_shutdown_messages_with_session_to_sidecar_stdin` | ok, 1 passed |
| 9 | shutdown writes（无会话） | `shutdown_writes_core_shutdown_to_sidecar_stdin_without_session` | ok, 1 passed |

**合计：9 / 9 PASS，0 FAIL。**

九项全部为 `1 passed; 0 failed; 162 filtered out`，即每项都真实执行且在**本次返修之后**仍然通过 —— AC1/AC2/AC3 对 `library_bridge.rs` 的改动（共享槽 holder、有界退避、4 处收敛为 1 个 helper）**未破坏任何既有生命周期语义**。

## AC7：SHA 与 `sha256` 校验

### 7.1 本 Task 的提交（40 位 SHA，经 `git cat-file -e` 可验）

| 短 SHA | 内容 |
|---|---|
| `b7e63a49b` | AC3：共享槽 holder，绝不丢失句柄 |
| `40d933700` | AC1：连续锁超时注入用例 |
| `580bb0d65` | AC2：饱和语义明确 + 有界退避 + 注入用例 |
| `3b4d52766` | AC4：审计表按真实语义重写 |

上述 SHA 均由 `git rev-parse` / `git log` 直接取得，**非人工构造**。

### 7.2 `sha256` 一律按磁盘真实字节实算

本仓库为 **CRLF 检出**，因此所有 `sha256` 必须对**磁盘字节**计算，不得对 `git show` 的 blob（LF 归一化后）计算。凡在本 Task 证据中登记 `sha256` 者，均以 `Get-FileHash -Algorithm SHA256` 对工作区文件直接读取。

### 7.3 本次未登记新 `sha256` 的原因

AC6 是**运行验证**（子进程输出为证据），AC7 是**指针校验**，二者都不产生需要新 pin 的文件。故本节只声明校验方法，不新增 pin —— 避免制造无证据价值的哈希条目。

## 边界与未完成项

- **AC5 未执行、未记 PASS**：AC5 要求 `P20-CLOSE-BOUND-1` 的 AC7 **真实交互桌面直跑**，且 Task 明文规定「本 Task 只负责脚本正确性，**不得自行记 PASS**」。该 AC 需由人在交互桌面上运行 `verification/P20-CLOSE-BOUND-1/run-desktop-close-verification.ps1`。**本文件不为其提供任何 PASS 依据。**
- **环境依赖的既有失败**：`packaged_sidecar_tests` 12 项与 `same_channel_concurrent_round_trips_keep_response_ownership` 因 `M2RC1_PYTHON` 未设置 / sidecar 未构建而失败，属**环境依赖**，与本次改动无关（该现象在 AC1 之前即存在，形态不变）。
