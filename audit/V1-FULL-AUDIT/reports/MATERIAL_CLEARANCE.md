# 历史材料来源与数据库复核

日期：2026-10-24；执行者 Codex；Task `NEW-MANGA-V1-FULL-AUDIT` 仍为 `in_progress`。固定产品 HEAD `349e61faff5f93067af5d4ce2d9e394e0d665b8c`。当前结论：**BLOCKED_OWNER_NO_DISTRIBUTION**；用户明确素材不传播，因此禁止推送包含其字节的完整历史。前述来源核验保留，不作为上传许可或完整隐私清白证明。

## 本轮查明的事实

| 材料 | 结果 | 尚未满足的边界 |
|---|---|---|
| 4 个嵌入 PNG | SHA-256 与 `ed607b755` 的 T1.1.1 合成样本 manifest 全部精确匹配；生成脚本明确使用本地 Pillow/字体绘制合成页 | 证明生成来源，不替用户作所有分发权利承诺 |
| 169 个嵌入 JPEG | 169 个文件名集合、页数、1350×1920尺寸与 T1.1.1 商业日漫素材记录完全吻合 | 原数值记录无逐页hash；只能高度关联，未证明传播许可 |
| 12 份 M2-AC1 业务库 | 所有页的source_hash集合与固定HEAD的合成页生成器精确匹配，书名和页文件名也匹配 | 库内仍有12个导出路径；未检查删除页/WAL/全部自由文本语义 |
| 12 份 M2-AC1 catalog | 各有2条resource_catalog记录，与隔离验收catalog用途一致 | 来源用途不等于完整隐私验收 |
| 5 份 P18 业务库 | books/chapters/pages均为0行；非空内容仅schema_migrations/application_metadata/pipeline_defaults | 主文件状态不能证明原运行时WAL完整 |
| 5 份 P18 catalog | 仅preview_namespace含初始化记录，未见导入页面记录 | 含5个derived_root、5个catalog_root本地路径单元格 |

数据库总计34个不同blob；每个主文件的 `PRAGMA quick_check` 都是 `ok`。字段级扫描没有非空的已知secret字段，也没有新确认的凭据格式命中；URL/email格式标记均为0。路径标记共22个，不输出真实路径值。本轮未修改任何数据库表、真实用户数据或产品源码。

## 图像来源证据

合成样本来源 commit：`ed607b755`（完整SHA在 `push-material-inspection.json`）。原文件：

- `verification/T1.1.1/samples/manifest.json`
- `verification/T1.1.1/scripts/generate_samples.py`

4个文件为 `no-text.png`、`jp-horizontal.png`、`jp-vertical.png`、`la-horizontal.png`。本轮只读取历史代码与manifest，没有复跑历史产品或改写历史测试。字节精确匹配证据在机器报告中；不把代码许可、模型许可替代为漫画素材许可。

JPEG 来源线索：当前固定HEAD的 `verification/T1.1.1/author-verification.md` §6 写明用户提供的商业日漫卷册位于历史路径 `G:/CODEX/New Manga/material/17`，共169页JPG、1350×1920，且“版权像素不入库”；`verification/T1.1.1/real-material/results.json` 记录了169个页文件名。历史原路径目前不存在。当前registry也没有 `material/17` 来源记录；先前对解压内容的SHA-256精确比对没有匹配。

本轮逐个读取嵌入JPEG的图像头、核对字节SHA与上轮解压证据一致，未导出JPEG副本，未做图像OCR。所有169个名字与数值记录完全一致，尺寸也完全一致，但数值记录未保存页内容hash，所以结论严格为 `CORRELATED_NOT_HASH_PROVEN`。不凭文件名、尺寸或用户拥有本地副本推断其可上传。

`.tmp.driveupload` 在 `87f61d8b02c9b678e96b65798042ec3d83b9db87` 引入；它把压缩Git对象作为普通blob纳入主线，普通push会传输这些外层blob及其内嵌图像。当前旧说明与实际传播面之间存在差异，已在Task记录，旧证据原位保留。

## 方法与真实限制

命令：`python -B audit/V1-FULL-AUDIT/tests/inspect_push_materials.py`。

在已有嵌入tree基础上，按其commit的182个不同根tree继续读取本地对象库，共解析1449个tree；这些根的缺失tree数为0。169个JPEG仍无法通过这些根获得完整历史路径；它们在tree中的文件名与真实素材记录高度关联。另对一个JPEG做 `git log --all --find-object` 查询，当前refs下未返回来源提交；此结果不证明对象从未进入其他已归档/不可达历史，也不授权GC或清理。没有枚举或清理所有不可达对象。

SQLite WAL格式的主文件不能直接用内存deserialize读取，所以将Git原字节复制到：

`G:/CODEX/New Manga.workspace/task-env/NEW-MANGA-V1-FULL-AUDIT/push-materials/<blob>.sqlite`

采用exclusive-create，已有副本必须与原字节一致才复用，不覆盖异常文件。以 `mode=ro&immutable=1` 打开，再设 `query_only=ON`、`trusted_schema=OFF`；全部读取后复核SHA。自检包括合成数据库、损坏tree解析拒绝、JSON secret字段识别及只读写入拒绝。隔离副本保留，不做清理。

**没有**验证缺失WAL、回滚日志、删除记录/free pages、图像EXIF/OCR、所有编码凭据或全部自由文本的隐私语义。完整原始字节仍会随历史上传；22个本地路径标记的存在不能被“测试数据”标签消除。

M2-AC1样本仅执行已阅读的3个纯函数（经AST选取）及固定尺寸常量来生成确定性页hash，不导入启动完整Core或Qt产品，不访问用户漫画库。纯函数源文件hash记录在证据中。

## 处置建议与下一步

当前主线原位保留，不push、不删除、不改历史、不修改原有pins。3个分批候选全都包含临时对象引入提交，因此分批仍不能排除这些材料。

用户已回复：“我自己的，但是不传播”。当前裁决为本地持有/提供、禁止上传，不将这句话推断为著作权证明。169个JPEG及其压缩外层blob的禁止上传指纹见 `evidence/push-material-disposition.json`；原件、历史、refs和证据保留。不再等待传播许可来默认放行完整main。

推荐排除私有材料的独立源码快照分支；具体范围、保留规则和验证Gate已写入 [MATERIAL_DISPOSITION_OPTIONS](MATERIAL_DISPOSITION_OPTIONS.md)。该方案尚未释放；后续需要明确发布目标并冻结Task，不在当前审计中擅自重写main。

继续指令（Codex，现有审计恢复，不释放新实现）：工作区 `G:/CODEX/New Manga`、branch main，base/head `349e61faff5f93067af5d4ce2d9e394e0d665b8c`。先检查dirty和6个P04保护指纹，读取本报告和 `evidence/push-material-inspection.json`。只在当前Task allowed_paths内记录用户提供的来源/许可证据及对应SHA；若资料不足，保留本阻断并形成具名处置方案，禁止上传、删除、改写历史/registry/pins或业务实现。交付更新后的阻断矩阵、机器清单及checkpoint，复跑材料检查、自检和治理检查；独立Review与用户上传授权尚未满足，不得置done或宣称可push。固定审计交付后可由DeepSeek Harness负责独立复核，Owner与Reviewer不同；当前尚未派发。
