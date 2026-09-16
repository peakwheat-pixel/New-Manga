# TASK-012 Codex 集成验证

日期：2026-09-16（Asia/Shanghai）
base_commit：`2cceb1e734c5079870662b7a28da316e46444810`
reviewed_head：`ca5848b746210564a2503e8c5f59e0a2118e56a1`
implementation_merge：`b324d4b09c6f755c37c8df75b5a1c566e882ce8f`
review_report_commit：`084db6000f4505f95c6451df8bc5aadefd93f5ff`
integration_commit：`78987c8fe5df5650bf7f674d6a9b79afbc48a5ab`

## 集成方式

在 `master` 上按协作协议 §6.6 串行保留两个 `--no-ff` merge commit：先合并作者交付 `e6fe52a`（包含固定被审 head `ca5848b` 及 Handoff），再合并 approved Review `084db60`。未合并其他分支，未修改被审 `src/`/`tests/` 语义。

时间线说明：`78987c8` 之后、TASK-012 文档收口之前，主线已有直连提交 `4e05e59`（TASK-010 的 Qt smoke/pytest 隔离与证据）。该提交不是本次 TASK-012 操作创建或合并的内容；本次验证运行在包含它的最终主线上。

## 主线复验

环境：Windows `win32 10.0.26200`，Python 3.12.3，PySide6 6.11.2，pytest 9.1.1；解释器 `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe`；未设置 `QT_QPA_PLATFORM`，使用默认 Windows Qt 平台。

| 命令 | 结果 | 退出码 |
|---|---|---|
| `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe -m pytest tests/ui_shell -v` | **46 passed** | 0 |
| `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe -m pytest tests -q -rs` | **368 passed, 6 skipped** | 0 |
| `git diff --check 2cceb1e ca5848b --` | 待集成前固定 head 检查无输出（Review 证据）；本次集成未改被审文件 | 0 |

6 个 skip 均为既有网络 TLS 用例，原因均为 `openssl unavailable`；不计入 passed。TASK-012 固定 reviewed head 的独立复验口径为 `290 passed, 6 skipped`，已在作者证据中更正。

## AC 与范围

- AC-1～AC-3：由固定 `ca5848b` 的作者测试与独立 Review 覆盖。
- AC-4：本次两个 merge commit、Handoff、Review、固定结果和本记录均已入库；因此四条 TASK-012 AC 可勾选。
- 未执行项继续保持：入口启动与 DPI 截图 `NOT_RUN/BLOCKED`（依赖独立 TASK-030）；键盘全量矩阵 `NOT_RUN`；原生 FileDialog 交互 `NOT_RUN`；工作台/阅读器/设置真实内容 `N/A`。
- 未修改 TASK-012 被审 `src/`/`tests/` 语义；未修改 `src/domain`、Schema、依赖清单、AGENTS；未释放 TASK-013/TASK-015 或其他冻结任务。

## 依赖核实与范围裁决

在当前主线 `78987c8` 核实：`src/application/importing/images/ports.py` 只有 `ImageDecoder`、`ManagedCopyStore` Protocol；Qt `QImage` 解码器仅存在于 `tests/library/helpers.py`，生产 `src/infrastructure` 无 `ImageDecoder.decode`；`src/infrastructure/filesystem/managed_storage.py` 公开 `write_temp`/`publish` 等方法但无 `store_original`。SQLite `open_database`、`MigrationRunner`、`SqliteLibraryRepository` 已存在。

据此批准建立但不释放独立 [TASK-030](../../doc/tasks/TASK-030.md)：Owner=`ZCode`，Reviewer=`DeepSeek Harness`，base=`78987c8`，允许的生产路径仅为 `src/ui/qml/Main.qml` 与 `src/bootstrap/app.py`，验收门槛为真实生产装配、Windows 默认 Qt 入口启动、100%/150%/200% DPI 截图和导入链的源文件保护/Managed Copy/DB 提交证据。因生产 Qt 解码与 Managed Copy 适配器未就绪，TASK-030 当前 `BLOCKED`；不以测试 fake 或空实现解除阻塞。
