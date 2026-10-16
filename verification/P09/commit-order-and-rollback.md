# P09 Managed Copy 提交顺序与回滚语义

状态：实现前设计；按本文顺序实现，未经核验不得越过前置阶段。

## 数据提交顺序

1. **验证来源，不产生持久副作用。** 只接受 Core 收到的显式选择项；先校验路径为绝对路径、无 `.`/`..` 穿越、无盘符/UNC 逃逸、所有路径段无 symlink/junction/reparse point。文件夹只枚举本层支持的图片，不递归。整批来源验证通过后才读取数据；读源只使用 `rb`。
2. **验证输入并固定字节。** 图片完整解码校验并取得真实宽高；PDF 先打开并按原始页序渲染、校验全部页面，再开始任何 Managed Copy 或 Page 写入。加密、损坏、零页 PDF 在此阶段拒绝，数据库和 Managed Storage 均保持无该文件的产物。来源只读；hash 对本次读取的字节计算。
3. **检测重复。** 在复制前按 Page 内容 SHA-256 与该 Chapter 的活动 Page 集比较。默认 `SKIP`；仅显式指定 `IMPORT_AS_NEW` 才另建 Page。不得复用或覆盖既有 Managed Original。
4. **先完成 Managed Copy。** 每页先写隔离的 managed temp，校验 temp 的 SHA-256/大小，再以同卷原子发布到不可变 `original/` 路径。只有发布成功且 Store 返回引用后才可构造/提交 Page。
5. **最后提交 Page。** SQLite Page 行记录 `source_filename`、递增且不可由拖拽改变的 `source_order`、初始当前 `sort_order`、Managed Original 的 SHA-256、字节数及 decoder 的真实 `width`/`height`。Page 插入使用现有 repository 事务。

## 中断点与恢复语义

| 中断点 | 数据库 Page | Managed Original | 临时文件 | 结果 |
|---|---|---|---|---|
| 来源校验、读取或解码前/中 | 无 | 无 | 无 | 文件失败；不触碰源文件 |
| temp 写入或校验中 | 无 | 无 | 最多有未发布 temp | 报 `COPY_FAILED`；不得调用 Page sink |
| temp 原子发布完成、Page 插入前 | 无 | 可能有完整孤儿副本 | 无 | 可见 Page 为零；孤儿不会形成指向缺失文件的 Page |
| Page SQLite 事务中/插入失败 | 无已提交 Page | 可能有完整孤儿副本 | 无 | SQLite 回滚；不产生坏 Page |
| Page 事务成功后 | 有 | 必须已存在且 hash/大小匹配 | 无 | 导入成功 |

AC4 的不变量为：`Page 行已提交 ⇒ Managed Original 已先原子发布，且内容与 Page.source_hash 一致`。当前允许的持久化接口没有跨文件系统与 SQLite 的共同事务；因此发布后、Page 提交前崩溃可能留下不可见的完整孤儿 Original，但永远不能留下“有 Page、无 Original”或半个最终文件。孤儿清理由后续受控 GC 负责，本 Task 不改 Managed Storage 基础设施。

批次按 Page 独立提交：单张图片或 PDF 的 Copy 失败不会回滚此前已完整提交的其他 Page；失败页不写 Page，后续未处理页列入 `pending`。PDF 的解析/渲染预检是文件级屏障，所以 PDF 解密、结构损坏或任一页渲染失败时，失败文件在首个 Copy 前退出，不留下 Page、Managed Original 或 temp。

## 实现与证据顺序

1. 先加路径/decoder/PDF 预检的隔离单测，确认拒绝路径零副作用、损坏 PDF 文件级零半成品。
2. 再接生产 Core decoder 与受控路径来源；运行对应定向测试。
3. 再执行 Managed Copy→Page 的故障注入测试，逐项检查 SQLite、`original/`、`temp/` 和源 hash。
4. 再验证重复、Unicode、PDF 页序/尺寸和现有 import/library/storage 回归。
5. 保存原始命令、stdout、stderr 与退出码，再整理逐 AC 证据。实现遇到需要新增 IPC 命令、变更 wire 语义或修改冻结契约时立即停止该部分并登记 `BLOCKED_WAITING_EXTERNAL_DECISION`。

## 范围

首发仅图片/文件夹与 PDF。MOBI 解析器和缩略图均不接入或新增；现有冻结 IPC 契约不变。Tauri/Rust 仅在现有导入 wire 能承载本行为时才接线；若不存在该 wire，不新增命令。
