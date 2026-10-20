# 阶段 1：Pillow 解码内存实测

**产出**: 2026-10-20 · **对应**: `DETECT-TILING-1` AC1 的前置调研
**问题**：r34 指出「只对 Pillow `Image` 做 `crop()` 后逐 tile `convert()`
**不自动证明全图解码内存有界**」。**本文件回答这个问题。**

## 一、结论先行

**r34 的担心成立。`crop()` + `convert()` 不保证有界解码。**

**最大样本 `690×131289 = 90.6 M px` 上，裁一个 1×1 像素再 `convert()`，
峰值内存仍增加 324.4 MB。**

**所以「切块」这个动作本身不省内存——省内存必须靠别的机制（见 §四）。**

## 二、实测方法（含四次失败的更正）

**最终方法**：每次测量用**独立子进程**，显式声明 ctypes `argtypes`，
通过 `GetProcessMemoryInfo` 读 Working Set 与 Peak Working Set，
测量前先 `SetProcessWorkingSetSize(-1,-1)` 把工作集压回水位。

**在这之前我失败过四次，每次都得到全 0：**

| # | 方法 | 为什么错 |
|---|---|---|
| 1 | `tracemalloc` | 只跟踪 Python 堆，**Pillow 在 C 层分配** |
| 2 | 单进程 `PeakWorkingSetSize` | **峰值不会回落**，第一次之后永远是 0 |
| 3 | `psapi.SetProcessWorkingSetSize` | **该函数在 `kernel32`**，不是 `psapi` |
| 4 | 未声明 `argtypes` 的 `GetProcessMemoryInfo` | **`HANDLE` 被截断，调用返回 `False`**——我三版都读了 0 而**从未检查返回值** |

**第 4 条是最隐蔽的**：一个返回失败的系统调用，其输出结构与「内存没增长」完全一样。

## 三、实测数据

### 样本 A：`600×18401 = 11,040,600 px`（不超限，对照）
物理满幅 RGB24 应为 **31.6 MB**

| 模式 | ws_delta | **peak_increase** |
|---|---:|---:|
| `open_only` | 8.5 MB | **0.0 MB** |
| `crop_1x1_convert` | 51.3 MB | **19.1 MB** |
| `crop_half_convert` | 51.1 MB | 61.1 MB |
| `convert_full` | 50.9 MB | 60.7 MB |
| `tobytes_full` | 51.2 MB | 124.0 MB |

### 样本 B：`690×100674 = 69,465,060 px`（6.2× 超限）
物理满幅 RGB24 应为 **198.7 MB**

| 模式 | ws_delta | **peak_increase** |
|---|---:|---:|
| `open_only` | 8.6 MB | **0.0 MB** |
| `crop_1x1_convert` | 75.8 MB | **43.6 MB** |
| `crop_half_convert` | 76.5 MB | 209.9 MB |
| `convert_full` | 75.5 MB | 309.3 MB |
| `tobytes_full` | 76.7 MB | **707.2 MB** |

### 样本 C：`690×131289 = 90,589,410 px`（8.1× 超限）
物理满幅 RGB24 应为 **259.2 MB**

| 模式 | ws_delta | **peak_increase** |
|---|---:|---:|
| `open_only` | 9.2 MB | **0.0 MB** |
| **`crop_1x1_convert`** | **356.6 MB** | **324.4 MB** |
| `crop_half_convert` | 356.0 MB | 670.6 MB |
| `convert_full` | 356.5 MB | 670.8 MB |
| `tobytes_full` | 357.5 MB | **1,189.4 MB** |

## 四、三条可推导的事实

### 4.1 `Image.open` 确实是惰性的

三个样本的 `open_only` 峰值增量**都是 0.0 MB**。
**所以「打开」不分配像素缓冲。**

### 4.2 但任何像素访问都会触发解码

**`crop_1x1_convert`（裁 1×1 像素）在样本 C 上峰值 324.4 MB。**

**一个 1×1 像素的裁剪，代价与整图解码相当。**

**这直接否证了「切小块就省内存」的直觉。**

### 4.3 解码代价不是统一的，与图像编码有关

| 样本 | `crop_1x1_convert` 峰值 | 满幅 RGB24 |
|---|---:|---:|
| A（11.0 M px）| **19.1 MB** | 31.6 MB |
| B（69.5 M px）| **43.6 MB** | 198.7 MB |
| C（90.6 M px）| **324.4 MB** | 259.2 MB |

**样本 B 的解码峰值（43.6 MB）只有其满幅的 22%，
而样本 C 的（324.4 MB）超过了满幅（259.2 MB）。**

**所以 Pillow 对不同 PNG 的解码策略不同**——可能取决于是否分块存储、
颜色位深、行过滤器等。**不能用「面积 × 3」推算。**

## 五、这对 `DETECT-TILING-1` 的实现意味着什么

**AC1 的要求（「先实测选定解码方式的峰值内存行为」）不仅必要，而且刚刚产出了否定结果。**

**所以实现方案必须改**。可能的方向：

| 方向 | 说明 | 未验证 |
|---|---|---|
| **A. 用 `Image.reduce()` / 缩略图路径** | 但会损失小字，且 `width/height` 一致性校验会拒绝 | 未测峰值 |
| **B. 用 `PIL.ImageFile` 的低层 tile 读取** | PNG 分块编码可能有 `tile` 接口 | **未测** |
| **C. 换解码器**（如 `pyvips` / `libvips`） | 真正的流式/分块解码 | **引入新依赖，需授权** |
| **D. 在大分配前按像素数硬拒绝** | 最保守：`crop` 也不做，直接按 `MAX_DETECT_PIXELS` 拒绝 | **等于现状，不解问题** |

**我没有选。这是设计决策，应在阶段 2 由 Codex 裁定。**

**但有一条可以现在就确定**：
**`crop()` + `convert()` 这条路被实测否决了，不能作为 AC1 的实现基础。**

## 六、产物

- `verification/DETECT-TILING-1/decoder-memory-probe.json`（完整数据，含失败链条记录）
- 本文件

## 七、明确未做

- **未修改任何产品代码。**
- 未修改 `DETECT-TILING-1.md`（AC1 的措辞需要按本结论更新，待裁定）。
- 未测方向 A/B/C（见 §五）——那是阶段 2 的范围。
