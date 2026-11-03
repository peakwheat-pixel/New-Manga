# FEA-08 能力矩阵（卷类型 × 输入类别；NTFS 行状态由 h4/h5/h6 结果 + 语义断言推导）

每格格式：`状态（证据来源）`；证据来源 = measured / mocked / inferred。
F08I2-004：每个卷分支显式赋值 H4/H5/H6 各自来源；F08I2-005：NTFS 行由逐场景语义断言推导，断言失败即降级。

| 卷类型 | 输入类别 | H4 稳定读取 | H5 回收 | H6 精确匹配 | H4 现状 | H5 现状 | H6 现状 |
|---|---|---|---|---|---|---|---|
| NTFS-local | 单图 | PASS(strict) / UNAVAILABLE(mmap-blind)（measured） | PASS（measured） | PASS（measured） | S1-S7/S5c strict 链 + S4 unavailable + S5a/b 盲区实测（volume-level, format-agnostic 合 | R1(文件)/R2/R3(目录) 实测；R4-R6b/R9 全分支 measured | 内容层能力（卷无关）：M1/M4/M6 exact（bytes/规范像素 digest）；重编码/CMYK→candidate（M2/M7）；GIF 首帧 ex |
| NTFS-local | 文件夹 | LIMITED(inferred: volume-level, format-agnostic)（inferred） | PASS（measured） | PASS（measured） | 卷级 measured（format-agnostic）：H4 为句柄/卷语义，未逐格式实验；strict/tolerant 结论同单图像格 | R1(文件)/R2/R3(目录) 实测；R4-R6b/R9 全分支 measured | 内容层能力（卷无关）：M8/M9 membership+成员 digest diff；重命名仅候选；重复同图独立 occurrence |
| NTFS-local | ZIP | LIMITED(inferred: volume-level, format-agnostic)（inferred） | LIMITED(inferred: volume-level, format-agnostic)（inferred） | PASS(Non-AES) / LIMITED(pyzipper)(AES)（measured） | 卷级 measured（format-agnostic）：H4 为句柄/卷语义，未逐格式实验；strict/tolerant 结论同单图像格 | 卷级 measured（format-agnostic）：回收 API 对路径操作，未逐格式实验 | 内容层能力（卷无关）：M10 容器重编码 exact（成员 digest）；M12 重复名歧义→candidate；M13 ZipCrypto 带密 exact |
| NTFS-local | CBZ | LIMITED(inferred: volume-level, format-agnostic)（inferred） | LIMITED(inferred: volume-level, format-agnostic)（inferred） | PASS（measured） | 卷级 measured（format-agnostic）：H4 为句柄/卷语义，未逐格式实验；strict/tolerant 结论同单图像格 | 卷级 measured（format-agnostic）：回收 API 对路径操作，未逐格式实验 | 内容层能力（卷无关）：M11 CBZ 与 ZIP 同构 exact |
| NTFS-local | PDF | LIMITED(inferred: volume-level, format-agnostic)（inferred） | LIMITED(inferred: volume-level, format-agnostic)（inferred） | PASS（measured） | 卷级 measured（format-agnostic）：H4 为句柄/卷语义，未逐格式实验；strict/tolerant 结论同单图像格 | 卷级 measured（format-agnostic）：回收 API 对路径操作，未逐格式实验 | 内容层能力（卷无关）：M14 重生成 exact（页渲染 digest+内容流 digest，参数记录）；M15 加密 PDF 带密 exact（独立密文两路径 |
| USB-FAT32/exFAT | 单图 | LIMITED(mocked)（mocked） | LIMITED(mocked)（mocked） | LIMITED(mocked)（mocked） | 未实测（无硬件） | 未实测（无硬件） | 能力同 NTFS 行（内容层），该卷上未 measured |
| USB-FAT32/exFAT | 文件夹 | LIMITED(mocked)（mocked） | LIMITED(mocked)（mocked） | LIMITED(mocked)（mocked） | 未实测（无硬件） | 未实测（无硬件） | 能力同 NTFS 行（内容层），该卷上未 measured |
| USB-FAT32/exFAT | ZIP | LIMITED(mocked)（mocked） | LIMITED(mocked)（mocked） | LIMITED(mocked)（mocked） | 未实测（无硬件） | 未实测（无硬件） | 能力同 NTFS 行（内容层），该卷上未 measured |
| USB-FAT32/exFAT | CBZ | LIMITED(mocked)（mocked） | LIMITED(mocked)（mocked） | LIMITED(mocked)（mocked） | 未实测（无硬件） | 未实测（无硬件） | 能力同 NTFS 行（内容层），该卷上未 measured |
| USB-FAT32/exFAT | PDF | LIMITED(mocked)（mocked） | LIMITED(mocked)（mocked） | LIMITED(mocked)（mocked） | 未实测（无硬件） | 未实测（无硬件） | 能力同 NTFS 行（内容层），该卷上未 measured |
| SMB-network | 单图 | LIMITED(mocked)（mocked） | LIMITED(mocked)（mocked） | LIMITED(mocked)（mocked） | 未实测（无硬件） | 未实测（无硬件） | 能力同 NTFS 行（内容层），该卷上未 measured |
| SMB-network | 文件夹 | LIMITED(mocked)（mocked） | LIMITED(mocked)（mocked） | LIMITED(mocked)（mocked） | 未实测（无硬件） | 未实测（无硬件） | 能力同 NTFS 行（内容层），该卷上未 measured |
| SMB-network | ZIP | LIMITED(mocked)（mocked） | LIMITED(mocked)（mocked） | LIMITED(mocked)（mocked） | 未实测（无硬件） | 未实测（无硬件） | 能力同 NTFS 行（内容层），该卷上未 measured |
| SMB-network | CBZ | LIMITED(mocked)（mocked） | LIMITED(mocked)（mocked） | LIMITED(mocked)（mocked） | 未实测（无硬件） | 未实测（无硬件） | 能力同 NTFS 行（内容层），该卷上未 measured |
| SMB-network | PDF | LIMITED(mocked)（mocked） | LIMITED(mocked)（mocked） | LIMITED(mocked)（mocked） | 未实测（无硬件） | 未实测（无硬件） | 能力同 NTFS 行（内容层），该卷上未 measured |
| Cloud-placeholder | 单图 | LIMITED(inferred)（inferred） | UNAVAILABLE(inferred)（inferred） | LIMITED(inferred)（inferred） | 未实测（按 API 文档推断） | 未实测；生产默认禁用 D 流程 | 能力同 NTFS 行（内容层），该卷上可达性未测 |
| Cloud-placeholder | 文件夹 | LIMITED(inferred)（inferred） | UNAVAILABLE(inferred)（inferred） | LIMITED(inferred)（inferred） | 未实测（按 API 文档推断） | 未实测；生产默认禁用 D 流程 | 能力同 NTFS 行（内容层），该卷上可达性未测 |
| Cloud-placeholder | ZIP | LIMITED(inferred)（inferred） | UNAVAILABLE(inferred)（inferred） | LIMITED(inferred)（inferred） | 未实测（按 API 文档推断） | 未实测；生产默认禁用 D 流程 | 能力同 NTFS 行（内容层），该卷上可达性未测 |
| Cloud-placeholder | CBZ | LIMITED(inferred)（inferred） | UNAVAILABLE(inferred)（inferred） | LIMITED(inferred)（inferred） | 未实测（按 API 文档推断） | 未实测；生产默认禁用 D 流程 | 能力同 NTFS 行（内容层），该卷上可达性未测 |
| Cloud-placeholder | PDF | LIMITED(inferred)（inferred） | UNAVAILABLE(inferred)（inferred） | LIMITED(inferred)（inferred） | 未实测（按 API 文档推断） | 未实测；生产默认禁用 D 流程 | 能力同 NTFS 行（内容层），该卷上可达性未测 |

## 需新增（生产化要点）

- **生产 SourceReadLease（Host 侧）**：默认 strict 共享（不授 FILE_SHARE_WRITE）——硬约束；tolerant 仅在缓解 mmap 盲区（USN/双读）后可用
- **mmap 盲区缓解**：identity+size+mtime 对映射写失明（实测）；需 USN/change journal 或双读校验，或保持 strict-only
- **WindowsRecycleBridge**：IFileOperation + 逐项 OperationId receipt/journal（:512）；失败分支按 R4/R5/R6/R9 原型语义实现；批量必须逐项事实核对（SHFileOperation 短路）
- **$RECYCLE.BIN receipt 解析**：Win11 $I v2 = 24B 头 + uint32 路径长度(含尾 null) + UTF-16 路径（实测格式）
- **AES ZIP 支持**：标准库不支持（M13 实测 NotImplementedError）→ 生产需 pyzipper(MIT) 或仅支持 ZipCrypto（产品裁决）
- **PDF 渲染引擎**：pypdfium2（PDFium BSD/Apache-2.0）实测可用且确定；PyMuPDF AGPL-3.0 仅研究用，不进生产闭包
- **USB/SMB/云卷**：LIMITED(mocked/inferred)：须真机实测后升级矩阵

状态计数：{"PASS(strict) / UNAVAILABLE(mmap-blind)": 1, "PASS": 6, "LIMITED(inferred: volume-level, format-agnostic)": 7, "PASS(Non-AES) / LIMITED(pyzipper)(AES)": 1, "LIMITED(mocked)": 30, "LIMITED(inferred)": 10, "UNAVAILABLE(inferred)": 5}
