# AC6 实测运行记录（2026-10-20）

**任务项**：AC6 — P08-FMT PNG/ZIP/CBZ/PDF/文本转录长期验收追踪；
P16/P17 在消费对应格式契约前须此项完成。

**原状态**：`NOT_RUN`，理由（原文）：

> **未达成（NOT_RUN 原因）**：具体格式处理代码与自动化验证用例属于后续
> P16/P17 实施范畴，在新技术栈下当前全部客观标记为 NOT_RUN。

**本轮**：P16/P17 均已完成（`done`），因此补跑 AC6 所要求的格式验证。

## 一、5 大格式的导出往返：**实测通过**

**测试**：`tests/core/test_p16_reader_export.py::test_five_export_formats_preserve_order_hash_lineage_and_pdf_text`

**实测结果**：

```
$ python -m pytest "tests/core/test_p16_reader_export.py::test_five_export_formats_preserve_order_hash_lineage_and_pdf_text" -x -q
.                                                                        [100%]
1 passed in 3.43s
```

**该测试覆盖 10 个用例**（源码 L517–L528）：

| 用例 | 格式 | 选项 | 页序 |
|---|---|---|---|
| `png` | **PNG** | — | 单页 |
| `zip` | **ZIP** | `compression: standard` | 逆序两页 |
| `zip-fast` | ZIP | `compression: fast` | 逆序两页 |
| `zip-store` | ZIP | `compression: store` | 逆序两页 |
| `cbz` | **CBZ** | — | 逆序两页 |
| `pdf-image` | **PDF** | `pdf_content: image_only` | 逆序两页 |
| `pdf-text` | PDF | `pdf_content: searchable_dual_layer` | 单页 |
| `text` | **文本** | `text_representation: json` | 逆序两页 |
| `text-txt` | 文本 | `text_representation: txt` | 逆序两页 |
| `text-markdown` | 文本 | `text_representation: markdown` | 逆序两页 |

**测试名本身说明了断言面**：`preserve_order_hash_lineage_and_pdf_text`
——页序、哈希、血统（lineage）与 PDF 文本层。

**整个 P16 测试文件**：

```
$ python -m pytest "tests/core/test_p16_reader_export.py" -q
...................                                                      [100%]
19 passed in 4.72s
```

**19 / 19 通过。**

## 二、`SEC-FMT-001` ~ `SEC-FMT-005`：**未实现**

AC6 报告 §4 要求 P16 在实现导入解析前「必须通过 `SEC-FMT-001` 到
`SEC-FMT-005` 的全部安全测试」。五项定义（报告 L37–L41）：

| ID | 攻击面 | 要求的防御 |
|---|---|---|
| SEC-FMT-001 | Zip Slip（`../../Windows/System32`）| 识别非法相对路径，丢弃条目并记日志，限制在托管沙箱 |
| SEC-FMT-002 | XML 实体爆炸 / XXE（CBZ 描述文件）| 禁用 DTD/实体解析 |
| SEC-FMT-003 | 伪装成图片的无效二进制 | 魔数嗅探，报错隔离，不崩解码器 |
| SEC-FMT-004 | 超长路径 / 极端 Unicode 文件名 | 启用 `\\?\` 长路径前缀 |
| SEC-FMT-005 | 超大图（> 10000×20000）| 检查可用内存，分块或限尺寸，给出警告防 OOM |

**实测搜索**：`tests/**` 下按 `zip.bomb|zipbomb|path.traversal|SEC-FMT|malicious|quota`
全量搜索，**零命中**。

**所以这五项安全测试在代码库里不存在。**

**这不是 AC6 报告的问题**——报告明确写了「必须通过…的全部安全测试」，
是**实现方（P16/P17）没有实现**。

## 三、外部阅读器兼容性验证：**未做**

AC6 报告 §4 第 2 条要求：

> 导出的 CBZ 与 PDF 必须经过至少一种外部标准阅读器
> （如 Adobe Acrobat、CDisplayEx 等）的兼容性验证。

**实测**：`verification/P16/`、`verification/P17/` 下**无任何外部阅读器验证记录**。
本机也**未安装**此类阅读器（不擅自安装）。

## 四、因此 AC6 的真实状态

| AC6 的要求 | 状态 |
|---|---|
| P08-FMT 长期验收追踪表 | **已建立**（报告 §2）|
| 导入解析规范 | **已建立**（报告 §2）|
| 导出序列化规范 | **已建立**（报告 §2）|
| 安全防范矩阵（定义） | **已建立**（报告 §3，SEC-FMT-001~005）|
| **5 格式导出往返实测** | **通过**（本轮，10 用例 / 19 测试全绿）|
| **SEC-FMT-001~005 安全测试** | **未实现** |
| **外部阅读器兼容性验证** | **未做** |

**所以 AC6 不能判 MET。** 规范层面完备，实测层面只有「导出往返」这一半。

## 五、一个必须记录的发现

**AC6 报告说「P16/P17 在消费对应格式契约前须此项完成」。**
**而 P16/P17 都已 `done`。**

**所以要么**：
- P16/P17 在 AC6 未完成的情况下消费了格式契约（**违反前置 Gate**），
- **要么** AC6 的「完成」被理解成了「规范建立」而非「实测通过」。

**这是一个真实的治理分歧，不能由我单方面判定。**

**但可以指出**：`P16` 的 `ac-matrix.md` **把 AC6 报告当作证据引用**
（`P16-FMT-PIN`），即 P16 **确实把它当成了已完成的依赖**。
而在 `SEC-FMT-001~005` 未实现的情况下，这个「已完成」是不完整的。

## 六、明确未做

- **未修改** `ac6-p08-fmt-traceability.md`（Owner 交付物）。
- **未修改** AC6 的勾选状态。
- **未实现** `SEC-FMT-001~005` 的测试（那是实现工作，需立 Task）。
- **未安装**任何外部阅读器。
- 未修改 `tests/**`。

## 七、给裁定的两个问题

1. **AC6 的「完成」应理解为「规范建立」还是「实测通过」？**
   若是前者，AC6 早已达成，P16/P17 的消费合法。
   若是后者，**P16/P17 的 `done` 应被重新审视**。
2. **`SEC-FMT-001~005` 由谁实现、何时实现？**
   它们目前**不在任何 Task 的 AC 里**——只在 AC6 报告的规范章节里。
   **一个只存在于报告里的要求，没有执行者。**
