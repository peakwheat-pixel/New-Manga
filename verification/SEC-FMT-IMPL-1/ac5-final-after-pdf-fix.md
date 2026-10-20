# AC5 终局：外部验证器结果（PDF 修复后重跑）

**产出**: 2026-10-20 · **对应**: `SEC-FMT-IMPL-1` AC5
**前提**：`PDF-STREAM-FIX-1` 已修 content stream 缺陷（`5a0e9aed1`）。
**本文件是修复后重跑 AC5 探针的结果，并澄清一个此前的误判。**

## 一、重跑结果

```
=== exporting ===
  cbz  completed     1135 bytes  ac5.cbz
  pdf  completed     8812 bytes  ac5.pdf

=== verifying CBZ with 7-Zip ===
  list exit=0 test exit=0 ok=True entries=4 comicinfo=True
     0001_001.png
     0002_002.png
     0003_003.png
     ComicInfo.xml

=== verifying PDF with PyMuPDF ===
  opened ok=True pages=3 sizes=[[600.0,900.0],[610.0,900.0],[620.0,900.0]] images=3

=== rendering PDF with Chrome headless ===
  exit=0 rendered=False png_bytes=0
```

## 二、三项结果

| 验证器 | 结果 | 判定 |
|---|---|---|
| **7-Zip**（独立 ZIP） | `list`/`test` 均 exit=0，4 条目含 `ComicInfo.xml` | **通过** |
| **PyMuPDF**（独立 PDF） | **zlib 错误消失**，3 页、尺寸正确、3 张图 | **通过** |
| **Chrome headless** | `rendered=False png_bytes=0` | **工具限制，非缺陷** |

## 三、Chrome 的失败已澄清：是工具限制

**修复前我把 Chrome 的 0 字节 PNG 当作「与 PDF 缺陷一致的第二证据」。**

**修复后它仍然是 0 字节，所以我必须查：是 PDF 还有问题，还是 Chrome 本身不行？**

**实验**：用 **PyMuPDF 自己生成一个已知良好的 PDF**（纯红矩形，662 字节），
**用同样的 Chrome 命令截图**：

```
--headless      exit=0 rendered=False bytes=0
--headless=new  exit=0 rendered=False bytes=0
```

**一个确定良好的 PDF 也渲染不出。**

**所以：Chrome headless 不能截图 PDF。**

**这是 Chrome 的已知行为**——PDF 查看器是内置插件，
headless 模式下 `--screenshot` 不渲染插件内容。

**因此**：

- **修复前**：Chrome 的失败**不是** PDF 缺陷的证据
- **修复后**：Chrome 的失败**也不是**残留缺陷的证据

**它在两次里都只是「这个工具做不了这件事」。**

## 四、我需要更正一处

**`ac5-findings.md` §三 写过**：

> **两个独立实现（MuPDF 和 Chrome）都指出问题，这不像误报。**

**这句话在「MuPDF 指出问题」上是对的，在「Chrome 也指出问题」上是错的。**

**Chrome 从来没有指出过任何问题——它只是渲染不出任何 PDF，包括好的。**

**我当时的推理是**：「两个工具都失败 → 更可信」。

**而实际上是**：「一个工具失败（真信号）+ 一个工具根本不能做这件事（假信号）」。

**它们看起来一样，因为在两次实验里 Chrome 的输出完全相同。**

## 五、教训

**一个验证器的「失败」有两种含义**：

| 含义 | 如何区分 |
|---|---|
| **被测对象有问题** | 用一个**已知良好**的输入跑同一验证器 |
| **验证器做不了这件事** | 同上 |

**区分方法只有一个：负对照（known-good control）。**

**我在 AC5 里对**被测对象**做了对照（有合成输入、有真实输入），
但**没有对**验证器**做对照。**

**而 Chrome 这条就是那样漏掉的。**

## 六、最终判定

| 项 | 判定 |
|---|---|
| CBZ 经 7-Zip 验证 | **通过** |
| PDF 经 PyMuPDF 验证 | **通过（修复后）** |
| PDF 经 Chrome 渲染 | **不可验证（工具限制）** |

**所以 AC5 的实质要求（「用一个外部验证器打开导出的 CBZ 与 PDF」）已经达成：**
**ZIP 用 7-Zip，PDF 用 PyMuPDF，两者都是独立实现。**

**但限制必须登记**：

| # | 限制 |
|---|---|
| **L1** | **未用专用漫画阅读器验证 CBZ**（本机未安装）|
| **L2** | **未用桌面 PDF 阅读器验证**（Acrobat/SumatraPDF/Foxit 均未安装）|
| **L3** | **Chrome headless 不能渲染 PDF**，所以不是可用验证器 |
| **L4** | **未验证「在别的机器上打开」** |
| **L5** | **验证器是独立实现，但不是用户视角** |

## 七、明确未做

- **未安装专用阅读器**（可能需要用户授权）
- **未请用户在其设备上验证**（那才是真正的用户视角）
- **未修正 `ac5-findings.md` 的原文**——**保留它作为「当时怎么想的」的记录，
  本文件是更正**。这是个有意的选择：改掉原文会让更正失去对照。
