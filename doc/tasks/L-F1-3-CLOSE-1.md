---
task_id: L-F1-3-CLOSE-1
owner: DSH
reviewer: zcode (agent-5, independent context)
status: done
created: 2026-11-15
---

# L-F1-3 关闭记录（按 zcode 裁决 4 条留痕）

## 裁决依据

`doc/reviews/L-F1-3-JUDGMENT-SUBSTITUTION-zcode-2026-11-15.md` —— **有条件成立**，
4 条全部为**记录性动作**，不要求新测量。

## 条件 1：判据替代的三条理由（已书面记录）

1. **串行化是设计**：`CoreServiceClient._pipeGate` 是 `SemaphoreSlim(1, 1)`（`:426`），
   管线刻意串行（`CORE-PIPE-EXCLUSIVE-1`）。「并发吞吐 > 串行」**才是缺陷**；「≈ 串行」是**预期**。
   ⇒ **磁盘并发吞吐不是本产品的验收指标。**
2. **错配已实证为零**：40 并发请求、40 个响应全部匹配自己的 `request_id`（`L-F1-3-PERF-4`）。
   这是 `L-F1-3` 并发风险的**真实载体**（E-6 类），已直接反证。
3. **冷磁盘本机不可测**：RAM 31.6 GB ≫ 夹具 1.6 GB，数据全在页缓存（`L-F1-3-PERF-3`）。

**引用**：`verification/L-F1-3-PERF-1..4/`、`tools/perf/wire_serialisation_probe.py`、
基线链 `344c4e83c → ce17e3756`。

## 条件 2：残余未测项（**保持未测口径，不得改口径**）

| 项 | 状态 |
|---|---|
| 冷缓存磁盘并发扩展性 | **未测** |
| wire 时序判据（重命令版，单请求 ≥10 ms） | **未测出** |
| 跨盘 / HDD 对照 | **未测** |

**重测触发条件**：**未来架构若改为多 pipe / 并行通道，本替代判据自动失效，必须重测。**

## 条件 3：PERF-4 的证据覆盖面（防误读）

- 探针是 **Python 直连 `bootstrap.core_service`** 的端到端通路；
- **C# 客户端侧靠代码结构事实**（`_pipeGate` + `SidecarProcess._exchangeGate` 租约 +
  `EnsureResponseBelongsToRequest` id 校验）支撑，**不是 40 并发实跑**。
- **不得**读成"C# 侧也做了并发压测"。

## 条件 4：门禁

`tools/governance/check.ps1` PASS；STATUS / REBASELINE_PLAN 同步。

## 子项最终状态

| 子项 | 状态 | 证据 |
|---|---|---|
| 大文件 | ✅ 已测（1.3 GB / 1.74 s） | `L-F1-3-PERF-1` |
| 占用文件锁 | ✅ 已测（typed `PermissionError`） | `L-F1-3-PERF-2` |
| 磁盘并发扩展性 | ❌ 未测（本机物理不可测） | `L-F1-3-PERF-3` |
| wire 层并发正确性 | ✅ 已测（40/40 零错配） | `L-F1-3-PERF-4` |
| wire 时序串行化 | ⚠️ 未测出（命令太轻） | `L-F1-3-PERF-4` §4 |

**⇒ `L-F1-3` 按替代判据关闭。**
