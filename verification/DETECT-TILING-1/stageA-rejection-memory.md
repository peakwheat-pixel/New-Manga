# 阶段 A：预解码安全拒绝的实测证据

**产出**: 2026-10-20 · **对应**: `DETECT-TILING-1` 的 AC1 与 AC4（部分）
**结论**: **拒绝路径确实不触发整图解码——峰值 37.3 MB 对满幅 163.5 MB。**

## 一、代码改动

`src/bootstrap/core_service.py` 的 `handle_detect`，原错误信息：

```
core.detect page exceeds the pixel limit (690x62133 = 42871770 px > 11184810 px)
```

**改为**：

```
core.detect page is too large to process safely: 690x62133 = 42871770 px
exceeds the 11184810 px limit (3.83x over). The page was rejected before any
pixel decoding, so no page-sized buffer was allocated. Reduce the page to at
most 11184810 pixels (about 3344x3344) and retry, or split a tall page into
several shorter images.
```

**新增四件事**：

| 增加 | 内容 |
|---|---|
| 超出倍数 | `3.83x over` |
| 拒绝时机说明 | `rejected before any pixel decoding` |
| **可操作目标** | `at most 11184810 pixels (about 3344x3344)` |
| **替代方案** | `split a tall page into several shorter images` |

**代码位置不变**：仍在 `image.convert("RGB")` 之前（`core_service.py` L1408 区域），
**所以拒绝时机没有改变，只是消息变准确了。**

## 二、内存实测

**样本**：`690×62133 = 42,871,770 px`，PNG，**mode = RGBA**

| 项 | 值 |
|---|---:|
| 文件大小 | 20.0 MB |
| 满幅 RGB24 缓冲 | **122.7 MB** |
| 满幅 RGBA 缓冲 | **163.5 MB** |
| 打开后峰值增量 | **37.3 MB** |
| **拒绝时峰值增量** | **37.3 MB** |

**结论**：**拒绝发生在 `Image.open` 之后、`convert()` 之前，
峰值增量 37.3 MB 远小于满幅 RGBA 的 163.5 MB（约 23%）。**

**所以「拒绝不触发整图分配」这一条**，实测成立。

**37.3 MB 的来源**：把 20 MB 的编码文件读入内存（`encoded = f.read()`）
加上 Pillow 的头部/元数据解析。**这是必要的开销，不是像素缓冲。**

### 测量方法（沿用阶段 1 的四项更正）

```
- 不用 tracemalloc（Pillow 在 C 层分配）
- 每个样本独立子进程（PeakWorkingSetSize 不回落）
- SetProcessWorkingSetSize 从 kernel32
- GetProcessMemoryInfo 显式声明 argtypes
```

**四个坑的共同症状都是「全 0」，见阶段 1 的 `failure_chain`。**

## 三、AC4 的一个真实缺口：**没有超限的 JPEG 样本**

**AC4 要求「至少覆盖一个 PNG 与一个 JPEG」。**

**实测 `test-materials` 的 34 个 JPEG 中，没有任何一个超过 `MAX_DETECT_PIXELS`。**

**所以「JPEG 超限样本」不存在，无法按要求覆盖。**

**这不是可以糊过去的**——`DETECT-TILING-1` 的 AC4 原文写的是
「至少覆盖一个 PNG 与一个 JPEG」，**这一条目前只能登记 `PARTIAL`。**

**可能的处置**（需裁定）：

| 选项 | 说明 |
|---|---|
| **A. 用合成 JPEG** | 生成一张超限 JPEG（编码可控），只验证拒绝路径不验证真实内容 |
| **B. 把 AC4 改为「PNG 必测，JPEG 有则测」** | 承认样本现实 |
| **C. 在 `test-materials` 里补一张超限 JPEG** | 需要新素材，且触及许可 |

**我未选。这是 AC 措辞问题，应由 Codex 裁定。**

## 四、阶段 A 完成度

| AC | 状态 |
|---|---|
| **AC1**（预解码安全拒绝 + 内存证据） | **代码已改、实测已做** —— 但**测试未补**、**Handoff 未写** |
| **AC4**（实测证据） | **PNG 完成**；**JPEG 部分不可得** → `PARTIAL` |
| AC2（`SEC-FMT-005` 映射） | 未做 |
| AC3（阈值缺陷登记） | 未做 |
| AC5（回归 + 独立审查） | 未做 |

**所以阶段 A 只完成了 AC1 的代码与实测部分。**

## 五、明确未做

- **未补单元测试**（AC1 应该有测试证明错误信息包含新字段）。
- **未跑既有 `core.detect` 测试**（AC5）。
- **未写 Handoff**。
- **未提交**（代码改动还在工作区）。
- **未改任何常量值**（AC3 明确禁止）。

## 六、产物

- `src/bootstrap/core_service.py`（已改，未提交）
- `verification/DETECT-TILING-1/stageA-rejection-memory.json`
- 本文件

## 勘误（2026-10-20 追加）

**本文件 §四、§五 的陈述在提交时已过时，特此更正：**

| 本文件原写 | 实际 |
|---|---|
| §四「测试未补」 | **已补**：`test_detect_oversized_rejected_before_any_pixel_decode` 与 `test_detect_within_cap_does_reach_convert`（commit `07e414773`）|
| §四「Handoff 未写」 | **已写**：`doc/handoffs/DETECT-TILING-1-dsh-stageA-20261020.md` |
| §五「未提交」 | **已提交**：`843cfe705`（产品改动）|

**§二的内存数字已被后续重测取代，见 `stageA-remeasurement-20261020.md`：**

| 项 | 本文件原值 | 重测值（口径已修） |
|---|---:|---:|
| PNG 拒绝峰值 | 37.3 MB | **141.7 MB** |
| JPEG 拒绝峰值 | 19.5 MB | **53.2 MB** |

**37.3 MB / 19.5 MB 是 `SetProcessWorkingSetSize` trim 基线后的读数，基线偏低，已撤回。**
**原因与修复见 `stageA-remeasurement-20261020.md` §一（ZCode Review P2-2）。**

**本文件保留原值不删**——它是当时真实测量的记录，但任何引用本文件 §二数字的地方都必须改用重测值。

