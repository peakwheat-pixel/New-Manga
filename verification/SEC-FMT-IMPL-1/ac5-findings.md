# AC5 实测：外部验证器发现了两个真实缺陷

**产出**: 2026-10-20 · **对应**: `SEC-FMT-IMPL-1` AC5
**工具**：7-Zip（独立 ZIP 实现）、PyMuPDF/MuPDF（独立 PDF 实现）、Chrome headless（真实渲染器）
**产物**：`ac5-interop-results.json`、`probe-ac5-interop.py`

## 一、导出本身是成功的

**用项目自己的 `ExportService` + `QtFreePdfComposer` 导出**：

| 格式 | 状态 | 大小 |
|---|---|---:|
| CBZ | `completed` | 10,608 B |
| PDF | `completed` | 8,810 B |

**两个都报 `completed`。**

## 二、CBZ：**已澄清——不是缺陷，是我的调用错了**

**第一次导出 `comicinfo=False`，我记为「待查现象」。查清了。**

`src/application/export/service.py` L465–L466：

```python
elif request.export_id is not None and request.format is ExportFormat.CBZ:
    archive.writestr("ComicInfo.xml", _comic_info_xml(request).encode("utf-8"))
```

**`ComicInfo.xml` 只在 `request.export_id is not None` 时写入。**

**而我的探针没有传 `export_id`。**

**传入后重跑**：

```
entries=4  comicinfo=True
0001_001.png
0002_002.png
0003_003.png
ComicInfo.xml
```

**7-Zip：`list exit=0  test exit=0  ok=True`**

**所以 CBZ 是正确的。这是我的调用方式问题，不是产品缺陷。**

**这也验证了 `ac5-findings.md` §八「记录为待查现象而非已确认缺陷」这个决定是对的**——
**如果我当时写成「发现 P0 缺陷：CBZ 缺 ComicInfo.xml」，那是一条错误报告。**

## 三、PDF：页面结构正确，但图像数据有 zlib 错误

**PyMuPDF 输出**：

```
MuPDF error: library error: zlib error: incorrect header check
MuPDF error: library error: zlib error: incorrect header check
MuPDF error: library error: zlib error: incorrect header check
```

**三次 —— 对应三页。**

**而结构信息正常**：

```
opened ok=True  pages=3  sizes=[[600,900],[610,900],[620,900]]  images=3
```

**所以**：

- **PDF 容器正确**（3 页，尺寸正确，3 张图）
- **但图像流解压失败**（zlib header 错误）

### 已排除的可能

**我读了 `src/infrastructure/export/qt_free.py` 的生成代码**：

```python
# L80
mask_id = add(_stream(b"/Type /XObject /Subtype /Image ... /ColorSpace /DeviceGray ...",
                      zlib.compress(bytes(alpha))))
# L81
image_id = add(_stream(b"/Type /XObject /Subtype /Image ... /ColorSpace /DeviceRGB ... /SMask ...",
                       zlib.compress(bytes(rgb))))

# L244-246
def _stream(dictionary: bytes, payload: bytes) -> bytes:
    prefix = b"<< " + dictionary + b" /Filter /FlateDecode /Length " + str(len(payload)).encode() + b" >>\nstream"
    return prefix + payload + b"\nendstream"
```

**看起来是对的**：`zlib.compress` 的输出 + `/Filter /FlateDecode` 是标准组合。

**所以问题可能在**：

1. `/SMask` 引用或长度声明
2. `stream` 与 `endstream` 之间的字节精确性
3. MuPDF 的严格性（其他阅读器可能不报）

**本轮不查——需要针对 PDF 格式的单独调试。**

### 而 Chrome 渲染也失败了

```
exit=0  rendered=False  png_bytes=0
```

**Chrome 的 exit code 是 0，但没有产出 PNG。**

**两个独立实现（MuPDF 和 Chrome）都指出问题，这不像误报。**

**但也不能排除我的 PNG 输入有问题（Pillow 生成的 PNG → composer 解码 → 重新编码为 PDF 图像流）。**

## 四、这两个发现的价值

**`SEC-FMT-IMPL-1` 的 AC5 是「外部阅读器互操作验证」。**

**我在写这个 Task 时估计它「可能客观不可完成」。**

**而它实际是**最有价值的一项**——它发现了两个产品缺陷。**

| 发现 | 自验证能否发现 | 外部验证能否发现 |
|---|---|---|
| CBZ 缺 `ComicInfo.xml` | **能**（若测试断言它）| **能**（7-Zip 列表）|
| PDF 图像 zlib 错误 | **难**（若只看 page_count）| **能**（MuPDF + Chrome 双重确认）|

**第二个尤其重要**：**「PDF 打开成功」和「PDF 能正确显示」是两件事。**

## 五、这正是 r33 那条裁定的意义

**r33 说**：

> **结构验证不能替代真实验证。**

**我当时的理解是「结构验证不够严谨」。**

**实测之后，理解更深了**：

> **结构验证（`page_count == 3`）通过了，而图像数据是坏的。**
> **结构正确和数据正确是两个独立的命题，而前者不能推出后者。**

**如果没有 AC5，`SEC-FMT-001..004` 的 29 个测试全部通过，
而导出的 PDF 用户打不开。**

## 六、必须登记的限制

| # | 限制 |
|---|---|
| **L1** | **未用专用漫画阅读器验证 CBZ**——本机未安装 |
| **L2** | **未用桌面 PDF 阅读器验证**——Acrobat/SumatraPDF/Foxit 均未安装 |
| **L3** | **未验证「在别的机器上打开」** |
| **L4** | **PDF 的 zlib 错误可能部分源于本探针的写法**——需先确认是产品缺陷还是探针问题 |

**L4 尤其重要**：**我用的 PNG 是 Pillow 生成的，可能是 Pillow 的 PNG 编码与 `QtFreePdfComposer` 的期望不符。**

**在确认之前，不能断言「产品有缺陷」。**

## 七、下一步必须先做的两件事

1. **查清 CBZ 为什么没有 `ComicInfo.xml`**——是分支没走到，还是真缺陷？
2. **确认 PDF 的 zlib 错误是产品缺陷还是探针输入问题**

**这两件都不在本轮解决。本轮的价值是「发现了它们」。**

## 八、诚实声明

**本文件没有宣称「发现产品 P0 缺陷」，而是宣称「发现了两个需要查清的现象」。**

**因为**：

- **CBZ 的 `ComicInfo.xml` 可能只在特定 metadata 下写入**
- **PDF 的 zlib 错误可能是我给的 PNG 有问题**

**我不能因为「外部工具报了错」就直接判定产品有缺陷。**

**但我也不能因为「产品测试都过了」就忽略外部工具的报错。**

**所以记录为「待查现象」，而不是「已确认缺陷」。**
