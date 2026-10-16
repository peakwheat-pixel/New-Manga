# P16-C1 Reader / Export wire 覆盖对照

**状态：** contract design coverage complete；runtime/产品验收 `NOT_RUN`。

**冻结输入：** `doc/08_ACCEPTANCE_CRITERIA.md` 的 AC-READ、AC-EXPORT、AC-ART；`doc/04_USER_FLOW.md` §9、§33–37；`verification/P08/SCOPE_DRAFT.md` 第 33、40、82 行；`verification/ARCH-DOC-REBASELINE/ac6-p08-fmt-traceability.md` 的 FMT-01..05。

**契约：** `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` rev 2.1，§5、§6.3、§10.3、§12。

## D08 AC 逐条对照

| AC | 冻结要求 | Reader/Export wire 承载 | 覆盖结论与边界 |
|---|---|---|---|
| AC-READ-001 | Original / Translated 可切换 | `GetReaderProjection.mode` 与每页 `original` / `translated` 只读资源引用、artifact revision 与 SHA-256 | **可承载**。缺失译图用 null 明示，不由 wire 发明 fallback。 |
| AC-READ-002 | 两种模式分别保存进度 | `ReadingProgressSnapshot` 含 `book_id/chapter_id/mode`；`SaveReadingProgress` 与 `GetReaderProjection` 按 `(book, chapter, mode)` 读写 | **可承载**。Original/Translated 的 page、百分比、最后阅读时间、累计秒数互相独立。 |
| AC-READ-003 | RTL 翻页方向 | `ReaderProjection.layout=rtl`；页数组保留 canonical reading order | **可承载**。UI 按 RTL 从右向左呈现，不重排持久页顺序。 |
| AC-READ-004 | LTR 翻页方向 | `ReaderProjection.layout=ltr` | **可承载**。UI 按 LTR 从左向右呈现。 |
| AC-READ-005 | Webtoon 纵向阅读 | `layout=webtoon_vertical`、逻辑 Page 的 `height_px`、进度 `page_id + scroll_offset_y` | **可承载**。一张长图始终一张 Page；坐标以原图像素保存/恢复，临时 tile 不是 Page。关闭后保存、重开 resume；`beginning` 查询不覆盖已保存位置。 |
| AC-EXPORT-001 | 单图、ZIP、CBZ、PDF、文本 | `ExportFormat=png/zip/cbz/pdf/text`；用户 D1/D2 已将“单图”映射为 PNG；`format_options` 表达压缩、PDF 图层、文本表示 | **可承载**。PNG 单次一页；多页通过 ZIP/CBZ/PDF/文本容器输出。格式行为按 FMT-01..05，不增删格式。 |
| AC-EXPORT-002 | 记录类型、范围、时间、输出路径、状态 | `ExportHistoryEntry` 冻结 format、book/chapter/page scope 与顺序、时间、host-only `output_path`、status、hash、lineage；`GetExportHistory` 仅由可信 Tauri host 调用 | **可承载**。WebView 不接收路径；host 可按不透明 export ID 处理打开目录等动作。 |
| AC-EXPORT-003 | stale 必须提示；可先重渲染或明确继续旧版 | `StartExport.stale_policy=abort/continue_existing`；`EXPORT_STALE` 返回 affected Page IDs；继续时按请求重试并冻结精确旧 artifact revision/hash | **可承载**。abort 不创建 job；继续必须是明确选择，Core 不静默改用其他版本。 |
| AC-ART-001 | 临时写入→验证→正式路径→current pointer，完成后文件与 DB 一致 | `ReaderPageProjection`/`ExportPageLineage` 携带 artifact ID、revision 与已验证 SHA-256；Export 自身先 temp/hash verify，再 atomic publish 并持久化 ExportHistory | **P16 可承载并只读消费 current artifact**。AC-ART-001 的译图 current-pointer 事务仍属于产生该 artifact 的上游写路径；P16 不改 current pointer，也不替代其事务验收。 |
| AC-ART-002 | DB transaction 前中断不改变旧 current | 导出仅写授权目标、临时文件与 ExportHistory；源零写规则禁止修改已有 artifact 或 current pointer | **保护关系可承载**。P16 不执行 artifact current-pointer transaction；真实故障注入仍须由上游 artifact Runtime Gate 验证。 |
| AC-ART-003 | Current Artifact 有可验证 Hash | Reader projection 与 Export lineage 为每个输入 artifact 携带 SHA-256；导出完成后为整个输出文件记录 SHA-256 | **可承载**。输入 hash 用于来源核验，输出 hash 用于 ExportHistory 和完成结果核验。 |

## 五格式 traceability 对照

| 格式追踪项 | FMT 冻结要求 | P16 rev 2.1 表达 | 覆盖结论 |
|---|---|---|---|
| FMT-01 单图 | 高保真译图，原分辨率/色彩空间；单图输出 | `png`，恰一页；hash/lineage 固定输入 artifact；lossless 保持分辨率与色彩空间 | **可承载**。单图按用户 D1/D2 映射 PNG；不把未选入的 JPG/JPEG/WEBP/BMP 加入 P16 输出格式。 |
| FMT-02 ZIP | 章节/整本 ZIP、可调 standard/fast/store、清晰目录、只读 manifest | `zip` + 必填 `compression`；页条目按 `ordered_page_ids` 写入，manifest 随格式输出 | **可承载**。顺序/hash/源零写由 Export snapshot 与发布语义承载。 |
| FMT-03 CBZ | 标准 Comic Book ZIP，含可得译者/团队、语言、日期的 ComicInfo.xml | `cbz` 独立格式；Core 从权威 metadata 生成 ComicInfo.xml；页序与 lineage 冻结 | **可承载**。不从 UI 路径/token 获取 metadata，不伪造缺失值。 |
| FMT-04 PDF | 纯图片或双层可搜索 PDF；分页完整、嵌入字体 | `pdf_content=image_only/searchable_dual_layer`；输出按冻结页序；格式契约要求页完整并嵌入字体 | **可承载**。两种格式均可被同一 StartExport wire 表达。 |
| FMT-05 TXT/JSON/MD | OCR 转录 TXT、含坐标/原文/译文 JSON、Markdown 剧本；UTF-8；JSON schema 校验 | `text_representation=txt/json/markdown`；Core 按固定 Page/Artifact revision 解析文本与坐标；UTF-8，JSON 按 FMT schema 校验 | **可承载**。具体文件内 schema 继续以 FMT 追踪表/后续格式规范为准，不在 IPC 中重复定义。 |

## 授权边界一致性

`ImportSourceRef` 与 `ExportTargetRef` 均由 Tauri host 签发、不可由 WebView 构造、具 scope/过期、由 Core 验证并解析；Import 是可续期的只读来源引用，Export 是单个输出文件、300 秒过期、一次消费的写引用。Export 的 resolved capability 只能指向该目标和必要的临时 staging；源 Page、Managed Copy、译图、current/pinned Revision 均为零写对象。任何不属于当前 Tauri host session 的签名、过期/撤销/重放、scope/format 不匹配均 fail closed。

本表证明 rev 2.1 的 **wire 足以表达** D08 三组 AC 与 FMT-01..05 的输入、顺序、lineage、hash、stale、取消、目标授权及历史结果；不把设计覆盖写成 runtime PASS。FMT 长期追踪表中的安全测试、外部阅读器兼容性和性能要求仍按原 Gate 执行，P16-C1 未运行这些验收，也未降低阈值或改变责任归属。
