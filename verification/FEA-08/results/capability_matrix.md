# FEA-08 能力矩阵（卷类型 × 输入类别；NTFS 行状态由 h4/h5/h6 结果推导，F08I1-008）

| 卷类型 | 输入类别 | H4 稳定读取 | H5 回收 | H6 精确匹配 | 证据 | 现状 | 需新增 |
|---|---|---|---|---|---|---|---|
| NTFS-local | 单图 | PASS(strict) / UNAVAILABLE(mmap-blind) | PASS | PASS | measured | S1-S7/S5c strict 链 + S4 unavailable + S5a/b 盲区实测（volume-leve | tolerant 共享如需启用：补 USN/change journal 或双读校验（mmap 盲区缓解） |
| NTFS-local | 文件夹 | LIMITED(inferred: volume-level, format-agnostic) | PASS | PASS | inferred | 卷级 measured（format-agnostic）：H4 为句柄/卷语义，未逐格式实验；strict/tolera | 如需逐格式 measured：补 per-format H4 场景；tolerant 同需 mmap 缓解 |
| NTFS-local | ZIP | LIMITED(inferred: volume-level, format-agnostic) | LIMITED(inferred: volume-level, format-agnostic) | PASS(Non-AES) / LIMITED(pyzipper)(AES) | inferred | 卷级 measured（format-agnostic）：H4 为句柄/卷语义，未逐格式实验；strict/tolera | 如需逐格式 measured：补 per-format H4 场景；tolerant 同需 mmap 缓解 |
| NTFS-local | CBZ | LIMITED(inferred: volume-level, format-agnostic) | LIMITED(inferred: volume-level, format-agnostic) | PASS | inferred | 卷级 measured（format-agnostic）：H4 为句柄/卷语义，未逐格式实验；strict/tolera | 如需逐格式 measured：补 per-format H4 场景；tolerant 同需 mmap 缓解 |
| NTFS-local | PDF | LIMITED(inferred: volume-level, format-agnostic) | LIMITED(inferred: volume-level, format-agnostic) | PASS | inferred | 卷级 measured（format-agnostic）：H4 为句柄/卷语义，未逐格式实验；strict/tolera | 如需逐格式 measured：补 per-format H4 场景；tolerant 同需 mmap 缓解 |
| USB-FAT32/exFAT | 单图 | LIMITED(mocked) | LIMITED(mocked) | LIMITED(mocked) | inferred | 未实测（无硬件） | 真机实测后升级 |
| USB-FAT32/exFAT | 文件夹 | LIMITED(mocked) | LIMITED(mocked) | LIMITED(mocked) | inferred | 未实测（无硬件） | 真机实测后升级 |
| USB-FAT32/exFAT | ZIP | LIMITED(mocked) | LIMITED(mocked) | LIMITED(mocked) | inferred | 未实测（无硬件） | 真机实测后升级 |
| USB-FAT32/exFAT | CBZ | LIMITED(mocked) | LIMITED(mocked) | LIMITED(mocked) | inferred | 未实测（无硬件） | 真机实测后升级 |
| USB-FAT32/exFAT | PDF | LIMITED(mocked) | LIMITED(mocked) | LIMITED(mocked) | inferred | 未实测（无硬件） | 真机实测后升级 |
| SMB-network | 单图 | LIMITED(mocked) | LIMITED(mocked) | LIMITED(mocked) | inferred | 未实测（无硬件） | 真机实测后升级 |
| SMB-network | 文件夹 | LIMITED(mocked) | LIMITED(mocked) | LIMITED(mocked) | inferred | 未实测（无硬件） | 真机实测后升级 |
| SMB-network | ZIP | LIMITED(mocked) | LIMITED(mocked) | LIMITED(mocked) | inferred | 未实测（无硬件） | 真机实测后升级 |
| SMB-network | CBZ | LIMITED(mocked) | LIMITED(mocked) | LIMITED(mocked) | inferred | 未实测（无硬件） | 真机实测后升级 |
| SMB-network | PDF | LIMITED(mocked) | LIMITED(mocked) | LIMITED(mocked) | inferred | 未实测（无硬件） | 真机实测后升级 |
| Cloud-placeholder | 单图 | LIMITED(inferred) | UNAVAILABLE(inferred) | LIMITED(inferred) | inferred | 未实测（按 API 文档推断） | hydration/断连语义专项 |
| Cloud-placeholder | 文件夹 | LIMITED(inferred) | UNAVAILABLE(inferred) | LIMITED(inferred) | inferred | 未实测（按 API 文档推断） | hydration/断连语义专项 |
| Cloud-placeholder | ZIP | LIMITED(inferred) | UNAVAILABLE(inferred) | LIMITED(inferred) | inferred | 未实测（按 API 文档推断） | hydration/断连语义专项 |
| Cloud-placeholder | CBZ | LIMITED(inferred) | UNAVAILABLE(inferred) | LIMITED(inferred) | inferred | 未实测（按 API 文档推断） | hydration/断连语义专项 |
| Cloud-placeholder | PDF | LIMITED(inferred) | UNAVAILABLE(inferred) | LIMITED(inferred) | inferred | 未实测（按 API 文档推断） | hydration/断连语义专项 |

## 需新增（生产化要点）

- **生产 SourceReadLease（Host 侧）**：默认 strict 共享（不授 FILE_SHARE_WRITE）——硬约束；tolerant 仅在缓解 mmap 盲区（USN/双读）后可用
- **mmap 盲区缓解**：identity+size+mtime 对映射写失明（实测）；需 USN/change journal 或双读校验，或保持 strict-only
- **WindowsRecycleBridge**：IFileOperation + 逐项 OperationId receipt/journal（:512）；失败分支按 R4/R5/R6/R9 原型语义实现；批量必须逐项事实核对（SHFileOperation 短路）
- **$RECYCLE.BIN receipt 解析**：Win11 $I v2 = 24B 头 + uint32 路径长度(含尾 null) + UTF-16 路径（实测格式）
- **AES ZIP 支持**：标准库不支持（M13 实测 NotImplementedError）→ 生产需 pyzipper(MIT) 或仅支持 ZipCrypto（产品裁决）
- **PDF 渲染引擎**：pypdfium2（PDFium BSD/Apache-2.0）实测可用且确定；PyMuPDF AGPL-3.0 仅研究用，不进生产闭包
- **USB/SMB/云卷**：LIMITED(mocked/inferred)：须真机实测后升级矩阵

状态计数：{"PASS(strict) / UNAVAILABLE(mmap-blind)": 1, "PASS": 6, "LIMITED(inferred: volume-level, format-agnostic)": 7, "PASS(Non-AES) / LIMITED(pyzipper)(AES)": 1, "LIMITED(mocked)": 30, "LIMITED(inferred)": 10, "UNAVAILABLE(inferred)": 5}
