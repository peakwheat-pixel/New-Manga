# P09 验收状态与限制

记录日期：2026-10-16
worktree：`G:/CODEX/New Manga.workspace/worktrees/P09-IMPORT-CORE`
branch：`codex/P09-import-core`
base：`d7fe920272d48eb4761347a5e18789dcbbdd05d6`

## 逐项状态

| AC | 状态 | 证据与判断 |
|---|---|---|
| AC1 | `完成` | 生产 Core 装配真实导入 17×23 PNG，断言 Page 尺寸、source filename/order/sort order/hash、Managed Original 与源字节一致；用例 1 passed。见 `logs/29-ac1-production-core-decoder.txt`。 |
| AC2 | `完成` | 受控来源测试覆盖显式选择、目录一级枚举、相对路径、`..`、盘符逃逸、symlink、junction、无副作用；追加来源被换成 symlink 的读取竞态验证，9 passed，0 skipped。见 `logs/40-path-replacement-race.txt`。 |
| AC3 | `BLOCKED` | 导入/隐藏/页面软删除/页面永久清理，以及实际 `TRANSLATE_ALL`、`REINPAINT_REGION`、`RERENDER_SINGLE` 后源 hash 全相等。项目级永久删除未实现：`LibraryService.delete_book` 只软删除；`TrashService.purge_batch` 只清理 Page 和 Managed Assets。不得把 Page purge 冒称项目永久删除。完整 hash 矩阵及代码定位见 `evidence/AC3-source-hashes.json`、`evidence/AC3-project-permanent-delete-availability.txt`，流程日志 `logs/37-ac3-workflow-source-hashes-final.txt`。 |
| AC4 | `完成` | Managed publish 半截写入故障、Page SQLite 插入故障均在真实生产 Core/SQLite/Managed Storage seam 注入；未产生 DB Page 指向缺失或半截 Original。见 `logs/35-p09-safety-gates-py312.txt`。 |
| AC5 | `完成` | 中文、日本語、한국어、Emoji、空格、括号路径通过 Core 导入与持久化。见 `test_unicode_folder_paths_import_all_supported_name_categories` 与 `logs/35-p09-safety-gates-py312.txt`。 |
| AC6 | `完成` | 同哈希不同文件名默认跳过；显式 `IMPORT_AS_NEW` 创建不同 Page 与 Managed Original，不静默覆盖。策略见 `doc/contracts/P09_IMPORT_CONTRACT.md`；运行见 `logs/35-p09-safety-gates-py312.txt`。 |
| AC7 | `完成` | PDFium + Qt 真实未加密 PDF 按页渲染/导入 17 passed，exit 0；加密、损坏和预检故障零半成品在模块及全目标集复验通过。见 `logs/30-ac7-pdf-page-rendering.txt`、`logs/41-p09-full-target-tests-py312-review-fix.txt`。 |
| AC8 | `完成` | 输入范围仅图片/文件夹 + PDF；生产组装没有 MOBI raster 注入，MOBI 测试只锁定拒绝，无缩略图实现。无新 IPC/冻结契约改动；最终范围清单见 `logs/36-scope-diff.txt`。 |
| AC9 | `BLOCKED` | 固定 head `87179691cbab8b97d30282c0d8d0b20d9d81122c` 的非作者 Review 已完成；初审 P2 均关闭，无剩余实现 finding。Coordinator 集成仍 `NOT_RUN`，禁止 push/merge。见 `review-8ab617f2e.md` 与对应 Handoff。 |

## 实际运行

- 环境：`G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe`，Python 3.12.3、PySide6 6.11.2、pytest 9.1.1；未安装依赖。
- 完整目标集：`$env:QT_QPA_PLATFORM='offscreen'; & 'G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe' -B verification/P09/run_pytest_in_workspace.py -q -rs tests/import_formats tests/library tests/storage/test_managed_storage.py` → `91 passed, 0 skipped, 0 failed`，exit 0。首轮 missing-folder 异常兼容回归见 `logs/32-p09-full-target-tests-py312.txt`；最新完整复跑见 `logs/41-p09-full-target-tests-py312-review-fix.txt`。
- 范围外旧测试核实：`tests/core/test_stub_decoder.py::test_production_stub_decoder_returns_valid_decoded_image` 当前 1 failed，因为测试把非法 `b"fake"` 输入交给真实 decoder 并要求 1×1；`tests/core/**` 不在 P09 修改授权内，原始输出见 `logs/42-out-of-scope-legacy-stub-test.txt`。该失败不计入上方指定目标集合结果。
- 生产尺寸、PDF 按页、AC3 工作流和安全 Gate 的具体命令、用例、exit code 见 `doc/tasks/P09.md` 的“测试要求”表及 `logs/`。

## 固定 head / 接续条件

- 实现 head：`87179691cbab8b97d30282c0d8d0b20d9d81122c`；Handoff 固定在 `doc/handoffs/P09-codex-87179691.md`。
- Review：旧 head `8ab617f` 的 `changes_requested` 两项已修订；修订 head 复审完成且无 open implementation finding。Coordinator 集成：`NOT_RUN`。
- Coordinator 集成：`NOT_RUN`；本 Task 不执行 merge/push。
- AC3 阻塞：需要一个获授权、能协调 Page/Book 数据与 Managed Assets 的项目级永久删除操作，之后在隔离目录重跑源 hash 检查。
- 暂不建议释放 P12，因为 P09 AC3 尚有阻塞，P12 依赖 P09。
