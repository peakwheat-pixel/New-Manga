# E-7 并发项 — 现状精确核实（2026-11-16，DSH）

**目的**：`PIPE-EXCLUSIVE-TRANSPORT-1` 卡面把 AC1/AC2/AC4/AC5 标为 `[~]`（PARTIAL/NOT MET），
多份后续文档据此宣称「E-7 仍有 5 项开放、并发安全不可宣称」。本文件**逐项读代码核实**，
判断哪些已修、哪些只是架构未统一（功能无缺陷）、哪些真开放。

**方法**：只读代码 + 交叉对照卡面与测试；**不**凭 grep 关键词下结论（本轮已因此误判两次）。

---

## 1. E-7 五项逐项核实

| # | 卡面/文档的表述 | 代码实测 | 判定 |
|---|---|---|---|
| a | `HostBridgeClient` 同型无锁管道 | `Bridge/HostBridgeClient.cs:269`（`SendRawAsync`）与 `:292`（`SendAsync`）**均** `using var lease = await _process.AcquireExchangeLeaseAsync(...)` | **已修** |
| b | `SendRawAsync` 锁外 | `CoreServiceClient.cs:2386` `await _pipeGate.WaitAsync(...)` → `:2396` `_pipeGate.Release()` | **已修** |
| c | 独占未下沉传输层 | `Transport/SidecarProcess.cs:34` `_exchangeGate`(SemaphoreSlim(1,1))、`:40-43` `AcquireExchangeLeaseAsync` 暴露 lease；**但** `CoreServiceClient` 仍用私有 `_pipeGate`（`:426`），未改用 lease | **部分**：传输层已有原语且 Fluent 侧已用；Core 侧未统一 |
| d | 无 `request_id` 时 fail-open | `CoreServiceClient.cs:2385` 注释明写「request_id (if any), so we do not validate the id here」—— `SendRawAsync` 路径**故意不校验** | **仍开，但属设计**（负向证据 hook） |
| e | 错配后无重同步（R-002） | `CoreServiceClient.cs:2400-2411` 错配时**抛 `SidecarException`**；无「丢弃直到匹配 id」逻辑 | **仍开**（真缺口） |

### 关键澄清：`ExchangeAsync` 本身不加锁

`SidecarProcess.ExchangeAsync`（`:219`）**不做** `_exchangeGate.WaitAsync` —— 独占必须由调用方持 lease 实现。
⇒ 两个客户端目前是**各自加锁**：Fluent 侧用传输层 lease（a/b 已修），Core 侧用私有 `_pipeGate`（b 已修）。
**功能上都有保护**；差别只在「新调用方若忘记加锁会撕裂」这一架构风险。

---

## 2. 真实剩余工作（按价值排序）

| 优先级 | 项 | 性质 | 建议 |
|---|---|---|---|
| **P1** | **e：R-002 重同步** | 真缺口：id 错配抛异常后，pipe 里可能残留旧响应，下一次 `ExchangeAsync` 会读到它 → **后续所有调用错位** | 在 lease 范围内实现「丢弃直到匹配 id 或 poison session」 |
| P2 | c：Core 侧改用传输层 lease | 架构一致性，功能无缺陷 | 把 `_pipeGate` 换成 `AcquireExchangeLeaseAsync`，删重复锁 |
| P3 | d：`SendRawAsync` fail-open | **设计如此**（负向证据 hook，明确不校验） | 不改；但应在文档中写明「非生产路径」 |

---

## 3. 对既有文档的更正

- `PIPE-EXCLUSIVE-TRANSPORT-1` 卡面 AC1 写「`CoreServiceClient` 仍用 `_pipeGate`，未统一」—— **仍成立**（c）；
  但 AC2 写「core 侧两处仍直调 `ExchangeAsync`」—— 若指 `SendRawAsync`，其**已在 `_pipeGate` 内**（b 已修）。
- 多份文档（含 `RELEASE-GATE-DISPOSITION` §3）沿用「E-7 仍有 5 项开放」的表述 —— **不准确**：
  实际是 **1 项真缺口（e）+ 1 项架构未统一（c）+ 1 项设计如此（d）**。

---

## 4. 本轮的自我更正记录

本轮我先用 `grep "SemaphoreSlim|lock"` 查 `HostBridgeClient`，无命中便判「无锁」——
实际上它用的是 `AcquireExchangeLeaseAsync`（lease 模式，不经 `lock` 关键字）。
**这是我第 4 次因「只搜关键词就读到一半」而误判**（前三次：`0x00` 映射、默认壳、手工绕过 `package.ps1`）。
已在本文件开头把方法改为「读完整实现」。

## 5. 下一轮建议

实现 **e（R-002 重同步）**：这是唯一真正的并发安全缺口，也是「并发安全不可宣称」的直接来源。
范围建议：
- 在 `SidecarProcess` 提供 `DrainUntilAsync(int expectedId)` 或等价物；
- `CoreServiceClient` 在 id 错配时先尝试丢弃到匹配 id（有上限），失败再 poison；
- 测试：构造「迟到的旧响应」场景，断言后续调用仍取到正确响应。
