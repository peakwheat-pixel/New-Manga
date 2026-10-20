# P1 产品缺陷：PDF 内容流声明了 FlateDecode 但未压缩

**发现于**: `SEC-FMT-IMPL-1` AC5 的外部验证（Round 150）
**定位并确认**: Round 151
**严重度**: **P1**（所有导出的 PDF 都受影响）

## 一、缺陷

**`src/infrastructure/export/qt_free.py` L97**：

```python
content_id = add(_stream(b"", "".join(content).encode("ascii")))
```

**`_stream`（L244–L246）**：

```python
def _stream(dictionary: bytes, payload: bytes) -> bytes:
    prefix = b"<< " + dictionary + b" /Filter /FlateDecode /Length " + str(len(payload)).encode() + b" >>\nstream"
    return prefix + payload + b"\nendstream"
```

**`_stream` **无条件**添加 `/Filter /FlateDecode`，但它不压缩 payload——它假定调用者已压缩。**

**所有其它调用点传的是 `zlib.compress(...)`。**

**而 L97 传的是 `"".join(content).encode("ascii")` —— 未压缩的明文。**

## 二、证据

### 2.1 逐流解压

**用 `_compose_pdf` 生成 3 页 PDF（2449 字节），解析出 9 个流**：

| # | 类型 | 声明长度 | 实际字节 | 首 2 字节 | 解压 |
|---|---|---:|---:|---|---|
| 1 | mask (Gray) | 27 | 27 | `789c` | **OK → 5400 B** |
| 2 | image (RGB) | 44 | 44 | `789c` | **OK → 16200 B** |
| **3** | **content** | **29** | **28** | **`7120`** | **FAIL: incorrect header check** |
| 4 | mask | 28 | 28 | `789c` | OK → 5490 B |
| 5 | image | 44 | 44 | `789c` | OK → 16470 B |
| **6** | **content** | **29** | **28** | **`7120`** | **FAIL** |
| 7 | mask | 29 | 29 | `789c` | OK → 5580 B |
| 8 | image | 44 | 44 | `789c` | OK → 16740 B |
| **9** | **content** | **29** | **28** | **`7120`** | **FAIL** |

**`7120` = `q ` —— 正是 content stream 的明文开头。**

**`789c` 是 zlib 的标准头。**

**所以：图像流和 mask 流都是正确压缩的；只有 content stream 未压缩却声明了压缩。**

### 2.2 修复验证

**临时 patch `_stream`，让空字典时**不**加 `/Filter`**：

```python
def patched(dictionary, payload):
    if dictionary == b"":
        return (b"<< /Length " + str(len(payload)).encode() + b" >>\nstream"
                + payload + b"\nendstream")
    return orig(dictionary, payload)
```

**结果**：

| 版本 | 页数 | **MuPDF zlib 错误** | 字节数 |
|---|---:|---:|---:|
| before | 2 | **2**（每页一个）| 1707 |
| **after** | 2 | **0** | 1661 |

**错误数从「每页一个」变成 0。诊断确认。**

## 三、影响

### 3.1 所有导出的 PDF

**L97 是**唯一的** content stream 生成点，且每页都走。**

**所以每一个经由 `QtFreePdfComposer` 导出的 PDF 都有这个问题。**

### 3.2 但「看起来能用」

**MuPDF 报告**：

```
opened ok=True  pages=3  sizes=[[600,900],[610,900],[620,900]]  images=3
```

**`page_count` 正确、尺寸正确、`get_images()` 返回 3 张图、`get_pixmap()` 不抛异常。**

**所以：一个只检查「能不能打开」的验证会通过。**

**而 Chrome headless 渲染产出 0 字节 PNG。**

### 3.3 为什么 Chrome 失败而 MuPDF 不抛

**MuPDF 把 zlib 错误当成 warning（stderr），继续渲染——
图像本身是好的，坏的只是画在页面上的那条指令流。**

**而 content stream 承载 `/Im0 Do` 这条「把图像画上去」的指令。**

**所以 content stream 解压失败 → 图像没被画上去 → 页面是空白的。**

**Chrome 的「0 字节 PNG」与这个一致，但本轮没有直接看到 Chrome 的空白页面，这一条是推断。**

## 四、这不是 `SEC-FMT` 的范畴

**这个缺陷不属于任何 `SEC-FMT-001..005`：**

| SEC-FMT | 关注 | 本缺陷 |
|---|---|---|
| 001 | Zip Slip | 无关 |
| 002 | XXE | 无关 |
| 003 | 伪装图像 | 无关 |
| 004 | 长路径 | 无关 |
| 005 | 超大页 OOM | 无关 |

**它是「导出文件的内部格式正确性」，属于一般的 PDF 生成缺陷。**

**所以它需要自己的 Task，不能挂在 `SEC-FMT-IMPL-1` 下。**

## 五、建议的修复

**三条路，从最小到最正确**：

| 方案 | 改动 | 评价 |
|---|---|---|
| **A** | L97 改成 `_stream(b"", zlib.compress("".join(content).encode("ascii")))` | **一行**，与其它调用点一致 |
| **B** | `_stream` 增加 `compressed: bool = True` 参数，L97 传 `False` | 显式，但要改函数签名 |
| **C** | L97 之前就把 content 压缩，`_stream` 不变 | 同 A，但更绕 |

**我建议 A**：它与所有其它调用点的用法一致（传压缩后的 payload），
**且不改变 `_stream` 的契约——`_stream` 的契约就是「你给压缩数据，我加 Filter 声明」。**

**而当前 L97 违反了那个契约。**

## 六、修复必须带测试

**只改一行不够。需要**：

1. **每个 stream 都能被 `zlib.decompress`**（单元级）
2. **MuPDF 打开时不产生 zlib 错误**（集成级）——**但 MuPDF 的 warning 走 stderr，需要捕获**
3. **渲染出的页面不是空白**（端到端）——**这一条最难，但最能证明修复有效**

**第 3 条的必要性**：`page_count` 和 `get_images()` 在本缺陷存在时都正常，
**所以它们不能作为「修复有效」的证据。**

## 七、明确未做

- **未修复代码**（本文件是记录；修复需要自己的 Task）
- **未验证 Chrome 的 0 字节 PNG 与 content stream 的因果关系**（§3.3 是推断）
- **未测「修复后 Chrome 能渲染」**
- **未检查 `.rs` 侧是否有相同模式**
- **未检查其它导出格式（CBZ/ZIP/SINGLE_IMAGE/TEXT）是否受影响**——
  本缺陷在 `qt_free.py`，只影响 PDF 路径

## 八、这个缺陷是怎么被发现的

**不是被测试发现的。**

**`SEC-FMT-IMPL-1` 的 AC1–AC4 有 29 个测试全部通过。
项目自己的导出测试也通过。**

**它是被「用 MuPDF 打开导出的 PDF」发现的——一个外部实现。**

**而 MuPDF 的报错走的是 stderr，不是异常。**

**所以即使有人写了一个「用 MuPDF 打开」的测试，若只用 try/except 包住，也不会发现。**
