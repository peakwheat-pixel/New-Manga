# P09 图片与 PDF 导入 Core 契约

状态：P09 实现契约；只定义本 Task 的 Python Core 导入行为，不新增或修改 Tauri IPC/wire 语义。待独立 Review 与 Coordinator 集成。

## 首发范围

- 支持单张图片、显式选中的图片文件集合、被用户显式选择的文件夹，以及单个 PDF。
- 文件夹只读其直接子项，不递归；识别顺序沿用既有自然文件名排序。
- 图片扩展名沿用 `collect_image_files` 的既有集合：`.png`、`.jpg`、`.jpeg`、`.webp`、`.gif`、`.bmp`。
- PDF 按 PDF 原始页序转为 PNG Page；生产 raster 继续使用已装配的 PDFium adapter。
- 不提供 MOBI、缩略图、CBZ、网页或其他文档格式能力。

## 受控来源

调用方必须把用户在文件选择器中明确选择的绝对路径/目录交给 Core 的路径来源工厂。路径必须位于传入的显式选择根内；拒绝相对路径、`.`/`..` 段、不同盘符/UNC 根、无法规范化/不存在的路径，以及路径任意段上的 symlink、junction 或 Windows reparse point。目录只展开一级；发现链接项时整组拒绝，不能悄悄跳过。任何来源校验失败必须发生在读文件、写 Managed Storage 或写 SQLite 之前。读取使用只读打开；Core 不回写、移动或删除源文件。

来源路径工厂只属于 Python application/Core 内部接口。WebView 不传数据库、Managed Storage 或目标 OS 路径；如 React/Tauri 后续需要导入 IPC，必须另行授权并修订冻结 IPC 契约，本契约不暗含该授权。

## 记录与排序

每个导入成功的图片或 PDF 页对应一行 Page 和一份不可变 Managed Original：

- 图片 Managed Original 是源图逐字节副本；`source_hash` 是这些字节的 SHA-256。
- PDF Managed Original 是该 PDF 页渲染的 PNG；该 Page 的 `source_hash` 是 PNG 字节 SHA-256。PDF 原文件仅被读取，原文件 hash 用于验收源保护，不伪装成每页 PNG 的 hash。
- Page `source_filename` 保留输入源文件名；PDF 的同一 `source_filename` 可关联多个 Page。Managed Original 的显示名为 `<pdf-stem>-page-<1-based-page>.png`。
- `source_order` 按本次实际生成 Page 的图片选择/文档页序追加；`sort_order` 在初次导入时按同一顺序追加。之后的人工重排只改 `sort_order`，不能改 `source_order`。
- `width`/`height` 来自生产 decoder 或 PDF raster 的真实像素尺寸，禁止占位尺寸。

## 重复项策略（AC-IMPORT-005）

重复键为**Page 内容字节的 SHA-256**，作用域为目标 Chapter，并包括同批次先前成功导入的 Page。默认策略 `SKIP`：报告重复文件，不写 Page、不创建/覆盖 Managed Original。只有调用方显式指定 `IMPORT_AS_NEW` 才创建新的 Page ID 和新的不可变 Managed Original；不得静默替换既有 Page、源文件或原件。软删除的 Page 不算重复，但保留的 `source_order` 不可复用，遵循现有 `SqliteLibraryRepository` 语义。

## 提交与失败

遵守 [`verification/P09/commit-order-and-rollback.md`](../../verification/P09/commit-order-and-rollback.md)：来源/解码校验 → hash 去重 → 临时 Managed Copy 写入和 hash/大小复核 → 原子发布 Managed Original → SQLite Page 事务。Page 只有在已发布 Managed Original 存在且与 `source_hash` 一致后才提交。PDF 在复制前完整渲染校验所有页；加密、损坏、零页或任一页无法渲染时拒绝整份 PDF，零 Page、Managed Original 和临时产物。

Copy/DB 失败返回逐文件/逐页失败，不留下引用缺失原件的 Page。发布成功但 Page 提交前崩溃可留完整、不可见的孤儿 Managed Original；孤儿清理由受控 GC 负责，不能通过回写源文件补偿。取消发生在提交过程中时，已成功提交的 Page 保持完整，其余页列为 `pending`。

## 冻结边界

本契约不新增 SQLite schema、不增加第三方依赖、不增加 IPC command、不变更 `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`，也不实现 MOBI 或缩略图。当前核心 importer 仅供已装配的 Python Core 服务内部使用；React/Tauri 可达性需要单独冻结和授权。
