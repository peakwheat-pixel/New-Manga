---
task: L-F1-3
adjudicator: zcode (subagent agent-5, independent context)
adjudicated_head: 31f4ab505
verdict: CONDITIONALLY_UPHELD
date: 2026-11-15
---

# L-F1-3 判据替代裁决（zcode）

## 裁决：**有条件成立**（条件为记录性动作，不要求新测量）

**问题**：`L-F1-3` 能否以「wire 层并发正确性（零错配）」替代「磁盘并发吞吐」作为验收判据并关闭？

**答**：可以，但须按下列 4 条留痕。

## 裁决者自己核实的代码事实（非采信 DSH 叙述）

- `CoreServiceClient.cs:426`：`_pipeGate = new SemaphoreSlim(1, 1)`；`:422-425` 注释明确要求
  **所有命令整周期持 gate（写 + 读 + event-frame skipping）**。
- **三对 Wait/Release 覆盖全部通道**：`SendHostControlAsync` `:696/:722`、`SendRawAsync` `:2386/:2396`、
  `SendAsync` `:2428/:2455`。全文件 `_process` 的 wire 交换点仅 `:700/:706`、`:2390`、`:2431/:2440`，
  **全部在 gate 内，无 gate 外交换**。
- **`SendRawAsync` 的 hook 绕过（E-7 window 2）修复完整**：`:2383-2396` 已进 gate。
- **附加两道防线**：`SidecarProcess.cs:40-55` transport 层 `_exchangeGate` 租约（单帧原子）；
  `CoreServiceClient.cs:2403-2415` `EnsureResponseBelongsToRequest` 运行时 id 校验兜底（E-6 教训固化）。
- `HostBridgeClient.cs:105` 是**独立 spawn 的进程/pipe**，不共用 core pipe，**不是绕过点**。

⇒ **`_pipeGate` 全通路无绕过，三道防线属实。**

## 判据成立的理由（三条，须书面留痕）

1. **串行化是设计**：`_pipeGate(1,1)` 刻意串行（`CORE-PIPE-EXCLUSIVE-1`），
   「并发吞吐 > 串行」**才是缺陷**；「≈ 串行」是**预期**。⇒ **磁盘并发吞吐不是本产品的验收指标。**
2. **错配已实证为零**：40 并发请求、40 个响应全部匹配自己的 `request_id`（`L-F1-3-PERF-4`）。
   这才是 `L-F1-3` 并发风险的**真实载体**（E-6 类）。
3. **冷磁盘本机不可测**：RAM 31.6 GB ≫ 夹具 1.6 GB，数据全在页缓存；测冷磁盘需 <1.6 GB 内存的设备（不现实）。

## 关闭条件（4 条，全部为记录性动作）

1. **书面记录判据替代的三条理由**（上节），并引用 `verification/L-F1-3-PERF-1..4/`、
   `tools/perf/wire_serialisation_probe.py`、基线链 `344c4e83c → ce17e3756`。
2. **残余未测项明确登记为未测，不得改口径**：
   - 冷缓存磁盘并发扩展性 —— **未测**；
   - wire 时序判据（重命令版，单请求 ≥10 ms）—— **未测出**；
   - 跨盘 / HDD 对照 —— **未测**。
   **并注明重测触发条件**：**未来架构若改为多 pipe / 并行通道，本替代判据自动失效，必须重测。**
3. **写明 PERF-4 的证据覆盖面**：探针是 **Python 直连 `bootstrap.core_service`** 的端到端通路；
   **C# 客户端侧靠代码结构事实**（gate + lease + id 校验）支撑，**不是 40 并发实跑** ——
   避免后人误读为"C# 侧也做了并发压测"。
4. 走 `tools/governance/check.ps1` + STATUS/PLAN 同步收口。

## 虚报风险评估：**无虚报**

- `PERF-1` §4 **自declares**「并发未做、不得判关闭」；
- `PERF-2` §3 **主动作废** 2.8x 数字；
- `PERF-3` §3 论证数据仍无效并登记第 9 次教训；
- `PERF-4` §4 明写 `VERDICT=SERIALISED` 是机械输出**不可引用**、时序判据标「未测出」。

**已测 / 不可用 / 未测出 边界清晰，且两次自我纠正均有留痕。**

## 一句话结论

`_pipeGate` 全通路无绕过、hook 修复完整、三道防线属实 ——
以「wire 层并发零错配」替代「磁盘并发吞吐」关闭 `L-F1-3` **成立**，但须按上述 4 条留痕，
**残余未测项保持未测口径**。
