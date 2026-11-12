# AUDIT-03 漫画库、导入及项目管理

日期：2026-11-13  
阶段结果：FAIL（发现已确认的路径发布边界缺陷；不代表本 Task Release Gate 结论）  
产品基线：10e4ee013835605800d3830fb960ae8d3aa04167  
定向测试生成 HEAD：8071caccae1a7885fb41b95889cbdc0e80eeb963  
路径探针生成 HEAD：934c81017cadf20e96fd2ee60bfa247086638be6

本报告按原始审计清单逐项核对。所有动态素材和文件系统操作都位于 pytest 临时目录；没有访问、复制或展示真实漫画与用户文件，也没有修改产品源码、原始测试、契约、schema 或依赖。

## 结论摘要

当前代码有两条图片导入路径：

1. Avalonia FEA-09 ReferencedSource 路径：ImportDockViewModel 调用 HostController 的引用导入计划/开始接口，经 Host SourceImportCoordinator 和只读 source grant 读取原始文件；Core 保存引用和页记录，不复制源图。AD-003 将 ReferencedSource 定为新导入默认行为，既有 Managed Copy 数据继续读取。
2. Managed Copy 兼容路径：HostController.ImportFilesAsync / ImportFolderAsync → HostGrantCoordinator.ImportAsync → Core ImportPages → ImportImagesUseCase 与 ManagedCopyStoreAdapter。此路径仍写受管副本，因此继续受文件系统发布安全边界约束。

AUDIT-03 定向 Core 回归 87 passed / EXIT 0；ReferencedSource 回归 77 passed / EXIT 0。它们验证 Python Core 与授权/wire 模块的合成测试，不是 Avalonia 真实 GUI 或打包应用的端到端实测。

隔离复跑 test_managed_publish_follows_directory_junction 确认 ManagedFileStorage.publish 可经 managed/books 下的目录 junction 将新生成 revision bytes 写到 managed root 之外。该 probe 只创建新文件；final_path.exists() 仍阻止覆盖目标已存在的文件。此结果已作为 SEG-B-PROBES-001 登记，既有只读 triage 定为 Medium / High confidence；本轮没有重新定级或重复建项。该确认使 AUDIT-03 记为 FAIL。修复源码超出当前 Task allowed_paths，需另开实现 Task。

## 方法与证据

- 代码和测试定位：核对当前 Avalonia Host/UI、Python Core 导入路径、AD-002/AD-003、原始 AUDIT-03 条目及对应测试。不把旧壳/UI 测试推作当前产品证据。
- 产品源码边界：audit03-static-20261112T200836Z.log / JSON 记录生成 HEAD、基线比较、当前改动路径和 EXIT。git diff --quiet 10e4ee013835605800d3830fb960ae8d3aa04167 8071caccae1a7885fb41b95889cbdc0e80eeb963 -- src apps tests 为 EXIT 0；采集时当前工作树变更均在 allowed_paths，工作树 git diff --check EXIT 0。
- 活动 Core 组：tests/library/test_import_images.py、test_import_sources.py、test_page_order.py、test_sqlite_library.py、test_book_crud.py、test_chapters.py、test_production_adapters.py、test_p09_managed_copy_safety.py、tests/storage/test_managed_storage.py、tests/import_formats/test_decode_format_matrix.py；87 passed，EXIT 0。完整 argv、cwd、started_utc、生成 HEAD、elapsed、EXIT 见 audit03-core-import-20261112T200824899900Z.log 和 evidence JSON。
- ReferencedSource 组：tests/fea09/test_import_source.py、test_referenced_flow.py、test_referenced_resolve.py、test_referenced_scanner.py、test_referenced_wire.py、test_referenced_sharing.py、test_read_paths.py；77 passed，EXIT 0。完整记录见 audit03-referenced-import-20261112T200824899900Z.log 和 evidence JSON。
- 路径边界探针：audit-probes-segment-b-20261112T195906381034Z.log / JSON，整体 EXIT 1（2 passed / 1 failed）。test_managed_publish_follows_directory_junction 实测 defect_confirmed=true、publish_wrote_outside_managed=true；该测试 PASSED 的含义是缺陷被复现。磁盘写失败探针也确认既有 SEG-B-PROBES-002；它属于 AUDIT-08/11，不计入 AUDIT-03。test_nmbak_restore_can_overwrite_outside_managed_root 未复现越界覆盖，因 BACKUP_CORRUPT 被拒绝而 FAILED；这是防线已验证，不是产品回归。
- 收集器试跑：最初把多个目录放入同一 pytest 进程，因不同目录同名 conftest.py 导入冲突而 EXIT 2，未开始测试；日志 audit03-import-project-20261112T195723565045Z.log 如实保留。将 Core 与 FEA-09 分组后，两组均 EXIT 0。
- 非当前架构试跑：一次中间版本还运行 tests/m2_acceptance/test_acceptance_loop.py，6 passed；该模块使用 PySide/QML 历史 harness，依 AGENTS.md 不属于当前 Avalonia 产品证据，未纳入本报告结论，也已从最终 AUDIT-03 runner 移除。其日志仅作过程记录，不得解释成桌面应用重启 PASS。
- 静态采集器首次把 10e4 基线至当前 HEAD 的历史改动集误当成本 Task 的工作树范围，并因历史证据中已有 whitespace 命中而 EXIT 1。修订后使用工作树差异检查：最终捕获显示产品 diff EXIT 0、20 条当前工作树路径均在 allowed_paths、whitespace EXIT 0。提交范围的 281 条路径含既有提交；其中 14 条 FEA-11-HOST-AUTH-4 文档/verification 路径是本 Task 之前的提交，不是本 Task 工作树修改。

## 原始检查项矩阵

| 原始检查项 | 结果 | 证据与边界 |
|---|---|---|
| 日本漫画分页导入 | PASS（合成） | FEA-09 合成 ZIP/CBZ occurrence 与顺序测试通过；未使用真实日本漫画。 |
| 韩国 Webtoon 长条漫导入 | PASS（Core 解码面） | test_pillow_image_decoder_imports_webtoon_long_strip_beyond_qt_default_cap 使用合成 690×110000 PNG；章节 vertical 测试通过。未做 Avalonia GUI 整条导入与阅读实测。 |
| 单张与批量导入 | PASS（Core） | ImportImagesUseCase 单/多源与文件夹选择测试；FEA-09 单图、目录、ZIP/PDF flow 测试通过。 |
| 图片格式兼容 | PASS（所列合成矩阵） | decode_format_matrix 覆盖产品格式、GIF/WebP/TIFF 多帧、条件式 AVIF、无效字节与 PDF raster；ReferencedSource 扫描后缀和显式文件选择的格式范围不同，不能把 Core decoder 矩阵等同于 UI 文件选择矩阵。 |
| 非法或损坏图片 | PASS（合成） | Core decoder 与 ReferencedSource scanner 的 corrupt/unsupported 断言通过；真实损坏漫画未测。 |
| 重复文件 | PASS（合成） | Managed Copy hash duplicate skip/import_as_new、ReferencedSource 同内容/重试 natural-key 情境通过。 |
| 文件名特殊字符 | PASS（已覆盖子集） | 中文/日文/韩文、emoji、空格、括号等合成路径通过；Windows 禁用字符和所有保留设备名未逐项测试。 |
| Unicode 路径 | PASS（Core 合成） | 临时目录和文件名包含中文、日本语、한국어、emoji；Avalonia 原生选择器的真实 UI 路径未运行。 |
| 超大图片 | PASS（解码边界） | 690×110000 合成长图通过；超过声明像素/分配上限的输入 fail-closed 测试通过。未测真实大文件导入、峰值进程内存或 GUI 响应。 |
| 图片排序 | PASS（合成） | 直接子文件自然排序及 ZIP occurrence 排序通过；目录导入只枚举直接子项，不递归子目录。 |
| 项目创建、保存、打开与删除 | NOT_APPLICABLE（独立项目实体） | 当前目标架构以 book/chapter 组织书架与 SQLite 数据，没有发现独立项目文件/项目打开向导；FEA source 的 project_id 映射到 book_id。Core book/chapter CRUD 有合成覆盖，但不是“独立项目 UI”验收。V2 删除入口仍按 AD-003 标为 NOT_WIRED，未通过 UI 实测。 |
| Managed Copy 行为 | PASS（兼容路径） | ManagedCopyStoreAdapter 的字节/hash 验证、不可变发布、失败不落 Page 与清理 temp 测试通过。AD-003 已将新导入默认策略改为 ReferencedSource；该项只证明现存兼容行为。 |
| 原始文件保护 | PASS（普通路径合成） | Core 测试在常规路径下比较源 hash，并验证导入后源字节不变。该结论不替代真实用户目录验证；junction 情境在路径 containment 项失败。 |
| 项目移动和重启恢复 | NOT_TESTED（桌面项目层） | 活动 Core 有 test_service_restart_reuses_repository_state，证明服务重新装配后可读取同一 SQLite repository；没有 Avalonia 进程重启、数据根移动后重开或安装包重启证据。 |
| Managed publication 路径 containment | FAIL（已确认 finding） | SEG-B-PROBES-001：ManagedFileStorage.publish 没有 containment/reparse walk，managed/books junction 可把新 revision 写到隔离 root 外。现有 final_path.exists() 防止覆盖已有目标；真实用户目录、GC/归档及其他入口未测试。 |

## 代码位置

- 当前 FEA-09 UI 计划/确认：apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Library/ImportDockViewModel.cs:373,413；Host 接口 HostController.cs:1864,1912。
- Host 导入兼容路径：apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs:1760,1767；apps/desktop-avalonia/src/NewManga.Host/HostGrantCoordinator.cs:65-150。
- Core ImportPages handler 与 per-file dispatch：src/bootstrap/core_service.py:5936-6025；ManagedCopy use case：src/application/importing/images/service.py:39-116；adapter：src/infrastructure/importing.py:245-292。
- ReferencedSource scoped read/grant：src/infrastructure/resource_channel/import_source_refs.py:102-170,282-405；自然排序和 reparse 检查：src/application/importing/images/sorting.py:1-90。
- Managed root publication boundary：src/infrastructure/filesystem/managed_storage.py:115-124；对比同文件 remove_managed:126-204 已有 lexical/containment/reparse protections。

## 未运行与下一步

- Avalonia Host/App .NET 定向测试与真实 GUI：当前基线历史记录为 BLOCKED-TESTHOST-ACCESS（8/8 runner EXIT 1、TRX 0）；本轮未重复运行。
- 安装包、真实日本/韩国漫画、真实用户文件、项目目录迁移、数据根搬迁后启动、桌面进程异常重启：NOT_RUN。
- AUDIT-03 不生成新的 issue ID；沿用已 TRIAGED 的 SEG-B-PROBES-001。不得在当前 Task 修改 ManagedFileStorage 或其他产品代码；修复需要独立实现 Task。
- 下一项按专项序列转入 AUDIT-04；AUDIT-03 的 stage FAIL 不改变全 Task AC2/AC3/AC4 PARTIAL 或 Release Gate BLOCKED。
