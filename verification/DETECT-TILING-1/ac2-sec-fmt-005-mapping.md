# AC2：`SEC-FMT-005` 四项要求逐项映射

**产出**: 2026-10-20 · **对应**: `DETECT-TILING-1` AC2
**前提**：r35 裁定「`SEC-FMT-005` 明文允许『分块**或**适当限制最大处理尺寸』」，
所以本 Task 走拒绝路线不违反它。**但必须逐项映射并给证据。**

## 一、`SEC-FMT-005` 原文

`verification/ARCH-DOC-REBASELINE/ac6-p08-fmt-traceability.md` L41：

> | **SEC-FMT-005** | 单图尺寸超过 10000x20000 的极端 Webtoon 图像文件 |
> 内存管理器检查可用物理内存，分块处理或适当限制最大处理尺寸，
> 提供清晰内存警告，防止程序 OOM | **WEBP / PNG** |

**拆成四项要求**：

| # | 原文要求 |
|---|---|
| ① | **内存管理器检查可用物理内存** |
| ② | **分块处理**或**适当限制最大处理尺寸** |
| ③ | **提供清晰内存警告** |
| ④ | **防止程序 OOM** |

**注意适用范围是 `WEBP / PNG`。**

## 二、逐项映射结果

**核实方法**：在 `src/**` 全文搜索 `GlobalMemoryStatus` / `available_memory` /
`psutil.virtual_memory` / `MEMORYSTATUSEX` / `free_memory` / `MemoryError` / `OOM`。

### ① 检查可用物理内存 —— **未实现**

**搜索 `src/**` 的结果：零命中。**

**`core.detect` 用的是固定常量 `MAX_DETECT_PIXELS = 32 MiB ÷ 3 = 11,184,810`，
与「当前机器有多少可用内存」完全无关。**

**判定：`NOT_IMPLEMENTED`。**

**这是四项里唯一的硬缺口。** 一个固定阈值在 8 GB 机器和 64 GB 机器上行为相同。

### ② 分块或限制最大处理尺寸 —— **已实现（走「限制」分支）**

`src/bootstrap/core_service.py`：

```python
MAX_DETECT_PAGE_BYTES = 32 * 1024 * 1024      # 编码文件上限
MAX_DETECT_PIXELS = MAX_DETECT_PAGE_BYTES // 3  # 解码像素上限 = 11,184,810
...
if image.width * image.height > MAX_DETECT_PIXELS:
    raise DetectRequestError(...)
```

**判定：`MET`（限制分支）。**

**且实测证明限制发生在像素解码之前**（`07e414773` 的两条测试 +
`stageA-remeasurement-20261020.md` 的同源对照 141.7 MB vs 479.8 MB）。

### ③ 提供清晰内存警告 —— **部分实现**

**现状**：超限时抛 `DetectRequestError`，消息为：

```
core.detect page is too large to process safely: 690x62133 = 42871770 px
exceeds the 11184810 px limit (3.83x over). The page was rejected before any
pixel decoding, so no page-sized buffer was allocated. Reduce the page to at
most 11184810 pixels (about 3344x3344) and retry, or split a tall page into
several shorter images.
```

**判定：`PARTIAL`。**

**理由**：
- ✅ 说明了实际尺寸、上限、超出倍数、可操作目标、替代方案
- ❌ **它是 typed error（拒绝），不是 `warning`**
- ❌ **消息里没有提到内存量**（因为 ① 未实现，没有内存数据可引用）
- ❌ **它是请求级错误，不产生用户可见的「警告」**

**若 ① 实现，③ 可以顺带满足**（消息里可以写「当前可用 X MB，本页需 Y MB」）。

### ④ 防止程序 OOM —— **部分实现**

**判定：`PARTIAL`。**

**已有的**：
- 像素上限**在解码前**拒绝 → 阻断了「一张巨图直接撑爆进程」这条路径
- provider 内的 OOM 有隔离机制（`errors.py` L180 `ProviderError` AC-GPU-001：
  「never crash the app」）

**缺的**：
- **`core.detect` 本身没有 `MemoryError` 捕获**——若 `image.convert()` 期间
  恰好 OOM，异常会向上冒泡，不是 typed 拒绝
- **没有「接近上限但未超」的渐进保护**（例如 11.1 M px 的 RGBA 页满幅 42.7 MB，
  放行后仍可能在大内存压力下失败）

## 三、一个必须单独指出的覆盖缺口：WEBP

**`SEC-FMT-005` 的适用范围是 `WEBP / PNG`。**

**而 `core.detect` 的格式白名单是**：

```python
_DETECT_PAGE_FORMATS = frozenset({"PNG", "JPEG"})
```

**所以 WEBP 根本进不了 `core.detect`——它在格式白名单处就被拒绝，
不会走到像素检查。**

**这在效果上是「更强的防御」**（根本不处理该格式），
**但在 `SEC-FMT-005` 的字面要求下，是「WEBP 这一半没有被该路径覆盖」。**

**判定：WEBP 部分 `NOT_APPLICABLE_TO_THIS_PATH`。**

**这不等于 `SEC-FMT-005` 在 WEBP 上满足**——只是这个 handler 不处理 WEBP。
**WEBP 的导入路径是另一条代码，不在本 Task 范围内。**

## 四、汇总

| 要求 | 判定 | 说明 |
|---|---|---|
| ① 可用物理内存检查 | **`NOT_IMPLEMENTED`** | 全文搜索零命中 |
| ② 分块或限制 | **`MET`**（限制分支）| 实测证明拒绝先于解码 |
| ③ 清晰内存警告 | **`PARTIAL`** | 消息清晰，但不是 warning，且无内存量 |
| ④ 防止 OOM | **`PARTIAL`** | 前置拦截有；`MemoryError` 未捕获 |
| WEBP 覆盖 | **`NOT_APPLICABLE_TO_THIS_PATH`** | 白名单只收 PNG/JPEG |

**所以 `SEC-FMT-005` 在本 Task 范围内是 `PARTIAL`，不是 `MET`。**

**按 AC2 自己的话：「未覆盖全项只能登记 `PARTIAL`，不得声称 `SEC-FMT-005` 已满足」。**

## 五、这不构成「本 Task 做错了」

**r35 的判断是对的**：`SEC-FMT-005` 允许走「限制」分支，而本 Task 确实实现了限制。

**但「允许走限制分支」不等于「限制分支自动满足全部四项」。**

**① 要求检查可用物理内存——这一条与「分块还是限制」的选择无关，是独立的。**
**它是原本就不存在的，不是被这次改向取消的。**

**所以它是一个本来就有的缺口，本 Task 只是把它显式登记出来。**

**建议**：① 应该另立 Task（例如 `DETECT-MEMORY-GUARD-1`），
因为实现它需要决定「可用内存怎么测、阈值怎么定、不同机器行为如何」——**那是设计决策。**

## 六、明确未做

- **未实现任何代码**（本文件是映射，不是实现）。
- **未改 `DETECT-TILING-1` 的 AC2 判定**——它仍是 `[ ]`，本文件是它的证据。
- **未核实 WEBP 的导入路径**是否另行满足 `SEC-FMT-005`——**那是另一个 Task 的范围。**
- **未测「大内存压力下的行为」**（需要构造受控的内存紧张环境）。
