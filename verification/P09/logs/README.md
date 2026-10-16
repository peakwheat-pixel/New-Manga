# P09 原始运行日志索引

首轮日志 `00`–`27` 是 Python 3.14.6 环境下的历史阻塞记录；它们原样保留，不作为最终 Gate。续接验证使用既有项目环境 `G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe`（Python 3.12.3、PySide6 6.11.2、pytest 9.1.1），未执行 `pip install`。

pytest 通过 `verification/P09/run_pytest_in_workspace.py` 启动：pytest cache provider 关闭；每个进程的 `tmp_path` 指向 `verification/P09/test-runs/run-<pid>/`，测试 DB、源图和 Managed Storage 均隔离于此。日志文件末尾记录对应退出码。用户要求保留原始证据，因此测试副本未清理。

## 最终 gate

| 日志 | 命令/用途 | 结果 |
|---|---|---|
| `05-path-source-tests-workspace-runner.txt` | `python -B verification/P09/run_pytest_in_workspace.py -q tests/library/test_import_sources.py` | 8 passed，exit 0；当时跑法随后发现需要每次生成独立目录。 |
| `07-path-source-tests-fixed.txt` | 同上，独立 run 目录修正后复跑 | 8 passed，exit 0。 |
| `08-p09-target-tests-fixed.txt` | `python -B verification/P09/run_pytest_in_workspace.py -q tests/import_formats tests/library tests/storage/test_managed_storage.py` | 51 passed、3 skipped、7 failed，exit 1；7 项因 `PySide6` 缺失。 |
| `10-managed-copy-safety-extended.txt` | `python -B verification/P09/run_pytest_in_workspace.py -q -s tests/library/test_p09_managed_copy_safety.py` | 6 passed，exit 0。 |
| `11-p09-full-target-tests.txt` | 完整目标集合：`tests/import_formats tests/library tests/storage/test_managed_storage.py` | 57 passed、3 skipped、7 failed，exit 1；7 个失败均是缺 `PySide6`。 |
| `12-p09-target-tests-without-qt-cases.txt` | 完整目标集合，`-k` 明确排除依赖 Qt raster 的 7 个测试 | 57 passed、3 skipped、7 deselected，exit 0。 |
| `14-runtime-dependencies.txt` | Python 版本、依赖可导入性、仓库锁定版本 | 原始输出；exit 0。 |
| `15-production-adapters-module-skip.txt` | `python -B verification/P09/run_pytest_in_workspace.py -q -rs tests/library/test_production_adapters.py` | 1 skipped，pytest exit 5（模块所有测试因 `PySide6` 缺失跳过）。 |
| `16-ac3-source-hash-evidence.txt` | 导出的源 hash 分阶段记录 | 四个已执行时点的 hash 完全一致。 |
| `18-ac7-pdf-negative-gates.txt` | 加密 PDF、渲染中途故障、损坏 PDF 三项定向 gate | 3 passed，exit 0。 |
| `19-ac8-mobi-scope-guard.txt` | `python -B verification/P09/run_pytest_in_workspace.py -q tests/import_formats/test_mobi_import.py` | 1 passed，exit 0。 |
| `20-python-ast-parse.txt` | `ast.parse` 检查全部 12 个变更 Python 文件 | 通过，exit 0。 |
| `21-diff-check.txt` | `git diff --check` | 通过，exit 0；Git 仅提示既有 `LF`/`CRLF` 自动转换。 |
| `22-p09-target-tests-final.txt` | 最终工作树复跑目标测试集合，`-k` 排除 7 个依赖 Qt raster 的测试 | 57 passed、3 skipped、7 deselected，exit 0。 |
| `23-path-source-tests-final.txt` | 路径来源用例最终复跑 | 8 passed，exit 0。 |
| `24-managed-copy-safety-final.txt` | Managed Copy、hash、Unicode、去重、损坏 PDF 最终复跑 | 6 passed，exit 0。 |
| `25-final-test-artifact-cleanup.txt` | 检查每个 pytest junction 的目标均在隔离测试根内后，清除测试副本 | 仅清理 `verification/P09/test-runs`，exit 0；保留 hash 和日志证据。 |
| `26-scope-and-head.txt` | base/head、branch、commit-range 和工作树改动路径 | 末尾完成后写入；包含要求的 `git diff --name-only <base>..HEAD` 空输出和工作树路径清单。 |
| `27-final-git-status.txt` | 用户要求的两个最终 `git status --porcelain` 命令 | 末尾完成后写入；主仓只读状态用于证明未改动。 |
| `29-ac1-production-core-decoder.txt` | 生产 Core 装配真实尺寸 + Managed Copy 元数据验收 | 1 passed，exit 0。 |
| `30-ac7-pdf-page-rendering.txt` | 未加密 PDF 按页真实 Qt/PDFium 渲染与导入 | 17 passed，exit 0。 |
| `31-ac3-workflow-source-hashes.txt` | `TRANSLATE_ALL` / `REINPAINT_REGION` / `RERENDER_SINGLE` 源 hash 检查初跑 | 1 passed，exit 0；后续加强了各步完成态断言。 |
| `32-p09-full-target-tests-py312.txt` | 指定三目录全量首跑，不排除 Qt 用例 | 1 failed，89 passed；missing-folder 原有异常契约回归，原始 traceback 保留。 |
| `33-path-collection-regression-fix.txt` | missing-folder 异常兼容回归 + 来源路径全套 | 9 passed，exit 0。 |
| `34-p09-full-target-tests-py312-final.txt` | 三目录全量复跑，不排除 Qt 用例 | 90 passed、0 skipped、0 failed，exit 0。 |
| `35-p09-safety-gates-py312.txt` | 来源约束、Managed Copy 故障注入、AC3、Unicode、去重和损坏 PDF safety suite | 15 passed，exit 0。 |
| `37-ac3-workflow-source-hashes-final.txt` | AC3 三项真实工作流，含 translation/inpaint/render 完成态断言 | 1 passed，exit 0。 |
| `36-scope-diff.txt` | 最终 `git diff --name-only <base>..HEAD` 范围输出 | 在固定 delivery head、Handoff 与 Review 后捕获。 |
| `38-p09-full-target-tests-py312-final.txt` | Task/Handoff 修改及 workflow 完成态断言后的三目录全量最终复跑 | 90 passed、0 skipped、0 failed，exit 0。 |
| `39-final-diff-check.txt` | 最终 `git diff --check` | exit 0；仅有既有 LF/CRLF 自动转换提示。 |
| `40-path-replacement-race.txt` | `tests/library/test_import_sources.py`；选中来源创建后被换为 symlink | 9 passed、0 skipped，exit 0；读取失败被归类，不读取链接目标、不写入 Store/DB。 |
| `41-p09-full-target-tests-py312-review-fix.txt` | 最新完整目标集 `tests/import_formats tests/library tests/storage/test_managed_storage.py`，不排除 Qt 用例 | 91 passed、0 skipped、0 failed，exit 0。 |
| `42-out-of-scope-legacy-stub-test.txt` | `tests/core/test_stub_decoder.py::test_production_stub_decoder_returns_valid_decoded_image` | 1 failed、exit 1：旧用例要求真实生产 decoder 将非法 `b"fake"` 解为 1×1。该路径不在 P09 授权范围，未修改。 |

## 首轮临时目录诊断

`00-path-tests-before-implementation.txt` 和 `01`–`04` 是实现前/pytest 临时目录诊断记录，包含未实现来源工厂导致的 collection failure，以及默认 `%TEMP%`、`--basetemp`、`TEMP` 重定向受当前沙箱拒绝的原始 traceback。它们是调试记录，不作为 AC 通过证据；后续 workspace runner 解决了临时目录阻塞。

`13-ac1-production-decoder-availability.txt` 与 `15-production-adapters-module-skip.txt` 记录首轮错误解释器下的依赖缺失；该阻塞在续接时通过用户指定的既有 Python 3.12 环境解除，最终 AC1/AC7 证据以 `29`、`30` 和 `34` 为准。
