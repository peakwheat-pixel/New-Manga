# 阶段 A 重测：绝对内存值 + 同源对照（回应 ZCode Review P2-1 / P2-2）

**产出**: 2026-10-20 · **触发**: `dsh-stageA-zcode-review.md` 的 P2-1 与 P2-2

## 一、P2-2 是真缺陷，已查明并修复

**ZCode 指出**：

> stageA JSON 中 `ws_increase_at_rejection_mb: 63.3` **大于**
> `peak_increase_at_rejection_mb: 37.3`，而阶段 1 各表中 ws_delta 普遍**小于** peak_increase
> —— 两组探针的基线定义未记录。

**核实：确实矛盾。当前工作集不可能超过峰值工作集。**

**根因**：上一版在读文件**之前**调用了 `SetProcessWorkingSetSize(-1,-1)`：

- 它把**当前**工作集 trim 低（`ws0` 变小）
- 但**峰值计数器不动**（`pk0` 仍是历史高点）
- **所以 `ws1-ws0` 与 `pk1-pk0` 是从两个不同原点量的**

**修复**：改为记录**绝对值**（`ws_mb` / `peak_mb` 每个检查点都记），
不再需要读者相信两个增量的可比性。**同时加了一条不变量自检：任何检查点上 `ws > peak` 就打警告。**

**本次运行没有任何不变量违规。**

## 二、P2-1：加了同源对照（这是关键改进）

**ZCode 指出**：上一版「满幅 163.5 MB」是**算术推算**，不是实测；
**缺一个同一样本走完整解码路径的对照**。

**本次每个样本都跑两条路**：`reject`（走 `handle_detect` 的拒绝）
与 `full_decode`（故意 `convert()` + `tobytes()`）。

### PNG `690×62133 = 42,871,770 px`（RGBA，满幅算术值 163.5 MB）

| 检查点 | Working Set | Peak Working Set |
|---|---:|---:|
| baseline（读文件前） | 70.4 MB | 70.4 MB |
| after_read | 70.4 MB | 70.4 MB |
| after_convert | 235.0 MB | 398.5 MB |
| after_tobytes | 357.5 MB | **479.8 MB** |

**reject 路径**：

| 检查点 | Working Set | Peak Working Set |
|---|---:|---:|
| baseline | 70.3 MB | 70.3 MB |
| after_read | 96.2 MB | 122.2 MB |
| **at_rejection** | **96.9 MB** | **141.7 MB** |

**结论**：**拒绝峰值 141.7 MB vs 解码峰值 479.8 MB —— 3.4 倍差距。**
**同一个样本、同一份文档内自证的对照。**

### JPEG `5000×4000 = 20,000,000 px`（合成，RGB，满幅 57.2 MB）

| 路径 | Peak Working Set |
|---|---:|
| **reject** | **53.2 MB** |
| **full_decode** | **242.2 MB** |

**4.6 倍差距。**

## 三、一个必须更正的旧数字

**上一版报告写「拒绝时峰值 37.3 MB」。**

**那个 37.3 MB 是在 trim 之后量的，基线偏低，因此低估了真实峰值。**

**正确值是 141.7 MB（PNG）与 53.2 MB（JPEG）。**

**这不是精度问题，是口径错误**——trim 掉的页面会被操作系统换出再换入，
而 `PeakWorkingSetSize` 记录的是历史最高点，两者不同源。

**旧数字并不支持「拒绝很便宜」这个更弱的结论吗？**
**不——141.7 vs 479.8（3.4×）依然支持。但 37.3 那个数不成立，必须撤回。**

## 四、控制组：**我的归因是错的**（ZCode r2 的 N-1）

**本文件初稿写**：对照页 `600×18401`「仍然被拒绝……原因：编码字节数超过 `MAX_DETECT_PAGE_BYTES`（32 MiB）」，并称这是「有价值的意外」——字节上限也在正确拒绝。

**这是错的。ZCode r2 查了我自己的 JSON：**

```
label     : CONTROL undersize
file_mb   : 1.6            <-- 1.6 MB 不可能触发 32 MiB 的字节门
pixels    : 11040600  vs limit 11184810   <-- 也不超像素门
rejected  : True
error_type: AttributeError
message   : 'CoreServiceServer' object has no attribute '_core'
```

**所以那不是产品拒绝，是我的探针崩溃。**

**根因**：探针用 `CoreServiceServer.__new__(CoreServiceServer)` 绕过 `__init__`，于是 `self._core` 不存在。崩溃点在 `getattr(self._core, "detector", None)`，**晚于** `convert()`（L1432）与 `tobytes()`（L1440）。

**这个错误为什么严重**：被字节门拒绝会抛 `DetectRequestError`（typed INVALID_REQUEST），**不可能抛 `AttributeError`**。而且 1.6 MB 与 32 MiB 相差 20 倍——**只要看一眼同一份 JSON 就站不住，而我把它写成了「有价值的意外」。**

### 这次崩溃反而给了一个真实数据

**因为崩溃发生在解码之后**，那一行的 `peak_mb: 204.8` **实际上是一个不超限页（11,040,600 px，满幅 RGBA 42.1 MB）走完整解码的真实峰值**。

| 检查点 | Working Set | Peak Working Set |
|---|---:|---:|
| baseline | 52.5 MB | 52.5 MB |
| after_read | 54.6 MB | 56.8 MB |
| at_rejection（实为解码完成） | 56.0 MB | **204.8 MB** |

**这是本 Task 唯一一次「不超限页走完整解码路径」的实测**，**但它仍然不是「正常页通过 `handle_detect` 产出 region」的对照**（崩溃发生在 provider 调用之前）。

**所以那个缺口仍然存在，如实登记，不因这次数据而算作已补。**

### 字节门的正确性不依赖这份证据

字节上限已有既有单测覆盖（`test_detect_oversized_payload_rejected_before_decode`、`test_detect_decoded_length_guard_backs_the_text_guard`）。**不需要这个假证据背书。**

> **时点快照声明**：本节是写入时点的状态记录，**不代表终态**。
> **终态以 `doc/tasks/DETECT-TILING-1.md` 的「终态处置表」为准。**

## 五、剩余未处置的 Review 项

| 项 | 状态 |
|---|---|
| **P1-1** 测试不守「拒绝先于解码」 | **未修**（需 monkeypatch `Image.convert`）|
| **P1-2(a)** Task 内 `PARTIAL` 与「已收口」并存 | **未修** |
| **P1-2(b)** `EV-DT1-JPEG` pin 指向 `843cfe705`，实际为 `783434e5b` | **未修** |
| **P1-2(c)** sha256 列全为 `(worktree)`，合成 JPEG 无 sha256 | **未修** |
| **P1-2(d)** AC4 改用合成 JPEG 属验收口径变更，需追认 | **未处置** |
| **P2-1** 同源对照 | **已做**（本文件 §二）|
| **P2-2** 指标口径 | **已做**（本文件 §一）|
| **P2-3** stageA md 自述过时 | **未修** |
| **P2-4** 弱断言 `"over" in message` | **未修** |

**所以本 Task 仍不得进入 `done`。**

## 六、产物

- `verification/DETECT-TILING-1/stageA-rejection-memory.json`（已重写为绝对値 + 双路径对照）
- 本文件
