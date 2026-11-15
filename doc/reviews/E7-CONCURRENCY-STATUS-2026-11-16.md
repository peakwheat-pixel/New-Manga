# E-7 并发安全 — 状态更新（2026-11-16，第 2 版）

- 作者：DSH（Lead / Integrator）
- 取代：`doc/reviews/E7-CONCURRENCY-STATUS-2026-11-16.md`（第 1 版，五项"全部仍开"）
- 基线：`dd5dc1519`
- 范围：只陈述**已落盘的事实与证据**；不关闭 E-7 本项以外的任何 Gate

## 1. 五项逐项终态

先给结论：**五项全部有处置**。下表每行的「动态证据」列都指**能实际执行、且经变异验证有判别力**的测试。

| # | 原问题（`PIPE-EXCLUSIVE-TRANSPORT-1.md:123-129` 原文） | 处置 | 卡 | 动态证据 |
|---|---|---|---|---|
| 1 | `CoreServiceClient` 仍用 `_pipeGate`，未改用传输层租约；`ExchangeAsync` 仍 `public` | **已修**：删除 `_pipeGate`（3 处改为 `AcquireExchangeLeaseAsync`）；`ExchangeAsync` **两个重载**都降 `internal` | `E7-1-UNIFY-LEASE-1` | 全量并发用例（`SidecarCancellationPoisonTests` 3 + `SidecarShutdownRaceTests` 4） |
| 2a | 无 `request_id` 时 fail-open（core 侧） | **已修**：`BelongsToRequest` 改严格相等；`EnsureResponseBelongsToRequest` 复用同一谓词 | `E7-2-FAILCLOSED-1` | `FakeCoreServiceIntegrationTests` 5 条（含两条 poison，**各经变异验证**） |
| 2b | bridge 仅校验数字 id（bridge 侧） | **已修**：`ParseResponse` 三段式严格判据（缺失/非 Int32/错配）；生产调用点 `_process.Poison()` | `BRIDGE-ID-FAILCLOSED-1` + `BRIDGE-FAKE-HARNESS-1` | `FakeBridgeHostIntegrationTests` 3 条（**变异验证：删 Poison ⇒ 2 红**） |
| 3 | id 错配后无重同步（R-002），流中可能残留一帧 | **已修**：有界重同步（上限 16 帧）+ 超限 poison；两处调用点都改 | `R002-RESYNC-1` | `R002ResyncTests` 4 条 + 生产链 2 条 |
| 4 | 取消（`CancellationToken`）后流状态可能永久失步（R-005） | **已修**：两个 poison 站点都改为「取消 ⇒ poison ⇒ 重抛 OCE」 | `R005-CANCEL-POISON-1` | `SidecarCancellationPoisonTests` 3 条 |
| 5 | `Dispose`/`StopAsync` 在租约外，在途命令会得 `ProcessExited` | **已核证**：**未改代码**（风险确认为可接受）；固化为 4 条回归 | `E7-5-SHUTDOWN-RACE-1` | `SidecarShutdownRaceTests` 4 条 |

### 判定依据的强度（逐项标注，不混用）

- **「已修」** = 改动落盘 + 有会变红的测试（多数经**变异验证**：故意破坏后测试变红）；
- **「已核证」** = 未改代码，但行为被测试钉住，且**删掉保护会变红**；
- 第 2a/2b 的 poison 接线、第 3 的重同步边界，都做了**变异测试**（把接线改 no-op ⇒ 测试红）。

## 2. 「并发安全」现在可以怎么表述

### 可以说的（有证据）

> 共享 stdin/stdout 管道的**独占**由传输层租约（`SidecarProcess.AcquireExchangeLeaseAsync`）保证，
> 且 `ExchangeAsync` 已降为 `internal`，程序集外无法绕过。
> 错误响应的**归属**在 core 与 bridge 两侧都 fail-closed（严格 id 匹配 + 有界重同步 + 超限 poison）。
> 取消与关停路径产生的是**typed `SidecarException`**，不会泄漏 BCL 异常。
> 上述每一条都有能变红的测试；三处 `poison` 接线各自经变异验证。

### 不能说的（仍然不成立）

- ❌ 「并发安全已完全达成」—— 仍有下列残余；
- ❌ 「E-7 本项可以关闭」—— 本报告不是关闭依据，只是状态更新；
- ❌ 「单测通过 ⇒ 真实 sidecar 下也安全」—— 见残余 3。

## 3. 残余清单（按风险排序，如实保留）

| # | 残余 | 风险 | 说明 |
|---|---|---|---|
| 1 | `AcquireExchangeLeaseAsync` / `ReadNextResponseLineAsync` 仍 `public` | 中 | `E7-1` 只点名 `ExchangeAsync`；这两个仍可被程序集外调用，租约可被外部持有 |
| 2 | `tools/perf/wire_serialisation_probe.py:12` 仍把已删除的 `CoreServiceClient._pipeGate` 当串行判据 | 低 | 只影响探针说明文字，不影响产品行为；不在任何卡的 `allowed_paths` 内 |
| 3 | **未见真实 sidecar 下的长稳压测** | **中** | 所有并发结论都来自假夹具与单测；793MB 真实 sidecar 的竞态窗口未测 |
| 4 | bridge 侧仍缺的边界：error 信封先于 id 校验、匹配 id 的业务错误**不** poison、握手期非法 id ⇒ `HandshakeFailed`、raw + error 仍 `BridgeException`、**请求计数**证明次调未写入 | 低-中 | 裁决 §4 要求，`BRIDGE-FAKE-HARNESS-1` 未做 |
| 5 | 假 bridge 用 `DerivedRoot` 路径末段编码场景 | 低 | 若未来 `DerivedRoot` 变成真实目录扫描，约定会失效 |
| 6 | `E7-5` 的「stop 进行中新交换」当前靠 `HasExited` + 两处宽 catch **偶然正确**，无显式状态保证 | 低 | 建议的显式 `_stopping` 守卫未做 |

## 4. 本轮的方法学教训（值得后续复用）

这十几轮里反复出现同一类失效，现已固化为可执行纪律：

| 纪律 | 触发它的错误 |
|---|---|
| **变异测试是判据，不是补充**：任何「测试已覆盖 X」的声明，必须能回答「把 X 弄坏，它红吗？」 | 多次写出"能过但抓不住回归"的测试 |
| **`--no-incremental` 不传给 `ProjectReference` 子项目**：变异/恢复后必须**逐项目**显式重建 | 两次因旧 DLL 误判（一次 bridge 旧 exe，一次把"必然失败"当成 flaky） |
| **往 `evidence_dir` 加文件必须同时登记 EV 行** | 本会话第 5 次；最后用自动扫描脚本收干净 |
| **读到否定式约束（「不能只做 X」）要问"还必须做什么"**，不是"那 X 可以不做" | 误读 Codex 裁决 §5.3，被 r1 判 CHANGES_REQUESTED |
| **改 A 时回头看依赖 A 的 B** | 卡内未关闭项自相矛盾、跨三张卡的过期表述 |
| **对一条不稳定的测试，先说"我不确定"再决定"撤回/修"** | 把变异残留当 flaky，撤回了本该保留的测试（本轮已修正） |

## 5. 本报告不做什么

- 不关闭 `E-7`（本项由 `PIPE-EXCLUSIVE-TRANSPORT-1` 的限定条承接）；
- 不改变 Release Gate；
- 不宣称残余 3（真实 sidecar 长稳压测）已覆盖 —— 那是需要真实夹具与更长运行时间的工作。
