# FEA-08 能力矩阵（卷类型 × 输入类别）

| 卷类型 | 输入类别 | H4 稳定读取 | H5 回收 | H6 精确匹配 | 证据 |
|---|---|---|---|---|---|
| NTFS-local | 单图 | PASS | PASS | PASS | measured |
| NTFS-local | 文件夹 | PASS | PASS | PASS | measured |
| NTFS-local | ZIP | PASS | PASS | PASS | measured |
| NTFS-local | CBZ | PASS | PASS | PASS | measured |
| NTFS-local | PDF | PASS | PASS | PASS | measured |
| USB-FAT32/exFAT | 单图 | LIMITED(mocked) | LIMITED(mocked) | LIMITED(mocked) | mocked |
| USB-FAT32/exFAT | 文件夹 | LIMITED(mocked) | LIMITED(mocked) | LIMITED(mocked) | mocked |
| USB-FAT32/exFAT | ZIP | LIMITED(mocked) | LIMITED(mocked) | LIMITED(mocked) | mocked |
| USB-FAT32/exFAT | CBZ | LIMITED(mocked) | LIMITED(mocked) | LIMITED(mocked) | mocked |
| USB-FAT32/exFAT | PDF | LIMITED(mocked) | LIMITED(mocked) | LIMITED(mocked) | mocked |
| SMB-network | 单图 | LIMITED(mocked) | LIMITED(mocked) | LIMITED(mocked) | mocked |
| SMB-network | 文件夹 | LIMITED(mocked) | LIMITED(mocked) | LIMITED(mocked) | mocked |
| SMB-network | ZIP | LIMITED(mocked) | LIMITED(mocked) | LIMITED(mocked) | mocked |
| SMB-network | CBZ | LIMITED(mocked) | LIMITED(mocked) | LIMITED(mocked) | mocked |
| SMB-network | PDF | LIMITED(mocked) | LIMITED(mocked) | LIMITED(mocked) | mocked |
| Cloud-placeholder | 单图 | LIMITED(inferred) | UNAVAILABLE(inferred) | LIMITED(inferred) | inferred |
| Cloud-placeholder | 文件夹 | LIMITED(inferred) | UNAVAILABLE(inferred) | LIMITED(inferred) | inferred |
| Cloud-placeholder | ZIP | LIMITED(inferred) | UNAVAILABLE(inferred) | LIMITED(inferred) | inferred |
| Cloud-placeholder | CBZ | LIMITED(inferred) | UNAVAILABLE(inferred) | LIMITED(inferred) | inferred |
| Cloud-placeholder | PDF | LIMITED(inferred) | UNAVAILABLE(inferred) | LIMITED(inferred) | inferred |

## 需新增（生产化要点）

- **生产 SourceReadLease（Host 侧）**：默认 strict 共享（不授 FILE_SHARE_WRITE）；tolerant 仅在拒绝 mmap 写者的环境可用
- **mmap 盲区缓解**：identity+size+mtime 对映射写失明（实测）；需 USN/change journal 或双读校验，或保持 strict-only
- **WindowsRecycleBridge**：IFileOperation + 逐项 OperationId receipt/journal（:512）；失败分支按 R4/R5/R6/R9 原型语义实现；批量必须逐项事实核对（SHFileOperation 短路）
- **$RECYCLE.BIN receipt 解析**：Win11 $I v2 = 24B 头 + uint32 路径长度(含尾 null) + UTF-16 路径（实测格式）
- **AES ZIP 支持**：标准库不支持（M13 实测 NotImplementedError）→ 生产需 pyzipper(MIT) 或仅支持 ZipCrypto（产品裁决）
- **PDF 渲染引擎**：pypdfium2（PDFium BSD/Apache-2.0）实测可用且确定；PyMuPDF AGPL-3.0 仅研究用，不进生产闭包
- **USB/SMB/云卷**：LIMITED(mocked/inferred)：须真机实测后升级矩阵

状态计数：{"PASS": 15, "LIMITED(mocked)": 30, "LIMITED(inferred)": 10, "UNAVAILABLE(inferred)": 5}
