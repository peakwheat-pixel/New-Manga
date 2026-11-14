# L-F1-3-PERF-4：wire 层并发正确性（**有结果**）+ 时序判据（**未测出**）

基线 `ce17e3756`。前三张卡（PERF-1/2/3）测的是**磁盘并发**，且**三次都因页缓存失效**。
本卡换判据：测 **wire 层**的并发行为。

## 1. 为什么换判据

`CoreServiceClient._pipeGate` 是 **`SemaphoreSlim(1, 1)`**（`CoreServiceClient.cs:426`），
即**管线被刻意串行化**（`CORE-PIPE-EXCLUSIVE-1`），目的是消除 E-6 那类**响应错配**。

所以产品层面该问的不是"磁盘并发多少 MB/s"，而是：
1. **并发请求时，响应会不会串到别人身上？**（正确性 —— 这才是用户会遇到的）
2. **并发墙钟是否 ≈ N × 单请求延迟？**（串行化是否生效）

## 2. 方法

新增 `tools/perf/wire_serialisation_probe.py`：spawn 真实 `bootstrap.core_service`，
走 **stdin/stdout JSON-RPC**（与 `tests/core/test_core_service.py` 同一通路），
用 **`core.ping`**（无夹具、无磁盘、无模型）发 **40** 个请求：

- **串行**：40 个依次发，累积每次往返延迟；
- **并发**：40 个线程同时发（写 stdin 与读 stdout 各自加锁以保证帧完整）；
- **每个响应必须带自己请求的 `request_id`** —— 任一错配即记为失败。

## 3. 结果

```
requests=40 command=core.ping
SERIAL   wall_s=0.001 median_ms=0.02 p95_ms=0.04
CONCUR   wall_s=0.005 median_ms=0.06 p95_ms=0.10
expected_concurrent_if_serial_s=0.001
concurrent_vs_expected_serial_ratio=5.35
CORRECTNESS=PASS (every response carried its own request_id)
```

## 4. 解读（**必须分清哪条成立、哪条不成立**）

### ✅ 成立：**并发下无响应错配**

40 个并发请求，**40 个响应全部匹配自己的 `request_id`**，零错配。
这是 E-6 类缺陷在**当前实现**下的**直接反证**，也是本卡**最有价值的结论**。

### ❌ 不成立：**时序判据没有测出结论**

`core.ping` 单次往返只有 **0.02 ms**，比线程调度与锁开销还小。
并发墙钟（5 ms）反而**大于**"N × 单请求"（1 ms），`ratio=5.35` ——
这个数字反映的是**锁竞争与线程调度开销**，**不是串行化**。

⇒ **`VERDICT=SERIALISED` 这一行是本脚本的机械输出，不能当结论引用。**
要测时序判据，必须换**有实际工作量的命令**（例如一次小 `list_books` 或一次真实 scan），
让单请求延迟显著大于调度噪声（建议 ≥10 ms）。

## 5. `L-F1-3` 最终口径

| 子项 | 状态 |
|---|---|
| 大文件 | ✅ 已测（1.3 GB / 1.74 s，PERF-1） |
| 占用文件锁 | ✅ 已测（typed `PermissionError`，PERF-2） |
| 磁盘并发扩展性 | ❌ **本机受页缓存限制，无法有效测**（PERF-3） |
| **wire 层并发正确性（无错配）** | ✅ **已测**（40 并发，零错配） |
| wire 层时序串行化判据 | ⚠️ **未测出**（`core.ping` 太轻，需换重命令） |

**建议**：`L-F1-3` 的核心风险（并发错配 = E-6 类）**已被直接验证为不发生**；
若 DSH 接受"以 wire 层正确性替代磁盘并发吞吐作为 `L-F1-3` 的验收判据"，
则本项**可以关闭**；否则仍需一台内存小于夹具的设备来测真实磁盘并发。

## 6. 本轮我的错误（已登记）

脚本里 `repo_root = Path(__file__).resolve().parents[1]` **算错了层级**
（`tools/perf/x.py` 的 `parents[1]` 是 `tools/`，不是仓库根），
导致 `ModuleNotFoundError: No module named 'bootstrap'`。改用 `parents[2]` 后正常。

**这是第 10 次"先写后验证"** —— 我写路径时没有先确认文件所在深度。
