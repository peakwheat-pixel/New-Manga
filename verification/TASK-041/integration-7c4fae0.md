# TASK-041 集成验证（integration_commit `7c4fae0`）

**对象**：TASK-041「MOBI 导入路线（KF7 picture MOBI）」。Owner=`ZCode`、Reviewer=`Codex`（**非作者**，两轮）。

| 项 | 值 |
|---|---|
| 任务固定 base | `904fca1`（开工 fast-forward 至 `6ea3dd3`） |
| 首轮被审 head | `d114253`（实现 `3230f45`）；首轮 Review `doc/reviews/TASK-041-d114253.md` = **`changes_requested`**（R-001 P1、R-002 P2、R-003～R-007 P3） |
| 修订范围 | `d114253..237e623`（实现 `f752096`、文档 `237e623`） |
| 复审 | `doc/reviews/TASK-041-237e623.md` = **`approved`**（Review 提交 `3a26c32`） |
| 集成前分支合并 master | `4d925f3`（把 `3a26c32` 合入分支，无冲突） |
| **integration_commit** | **`7c4fae018c5690063beccd9b9b6d2de19e71ccde`**（`git merge --no-ff`，父提交 `3a26c32` + `4d925f3`） |
| 集成后 master | `7c4fae0` |

## 集成后验证（本机实测）

口径：**PowerShell + `G:/CODEX/New Manga.task-envs/TASK-012-py312`**、`PYTHONDONTWRITEBYTECODE=1`、`-p no:cacheprovider`；证据 [integration-postmerge-tests.txt](integration-postmerge-tests.txt)。

| 场景 | 命令 | 结果 |
|---|---|---|
| 定向 | `pytest tests/import_formats tests/library -q -rs -rf` | **PASS** 68 passed / 0 skipped，exit 0 |
| 全仓 | `pytest -q -rs` | **PASS** 825 passed / 6 skipped，exit 0 |

**6 条 skip 原因（逐条）**：全部为既有 `tests/network` 的 `openssl unavailable`——
`test_connection_tester.py:106`、`test_transport_tls.py:39`、`:47`、`:62`、`:69`、`:83`。
**无新增 skip/xfail、无删除文件、无断言放宽**（修订范围 `--diff-filter=D` 为空）。

**口径对照**：作者留证为同 venv、Git Bash 会话内启动 `powershell.exe`（继承 PATH → `openssl` 可用）⇒ `831 passed / 0 skipped`；本机直接启动 PowerShell ⇒ `825 passed / 6 skipped`。**总数一致（831 = 825 + 6）**，无屏蔽（首轮 Review 已就此接受 R-006 勘误）。

## 集成内容（相对 `3a26c32`）

- `requirements.txt`：仅 +1 行 `mobi==0.4.1`（唯一新增依赖；传递依赖 loguru / standard-imghdr / win32-setctime 由 pip 解析）
- `src/application/importing/documents/service.py`：`_is_mobi` 分派 + 可选 `mobi_raster`（`None` 时与 TASK-023 行为一致）+ 未注入文案改写
- `src/infrastructure/importing.py`：`MobiDocumentRaster`（KF7 页面收集 = `mobi7/Images` fullmatch `image%05d.<ext>`、record 号数值排序、cover/HD 排除、`mobi8/` typed fail-closed、`mobi` 仅适配器内 lazy import）
- `src/bootstrap/app.py`：装配一行 `mobi_raster=MobiDocumentRaster()`
- `tests/import_formats/test_mobi_import.py`：12 例（含注入树、KF8、mid-document 坏页、真实 import 守卫、受控根断言）
- 文档/证据：Handoff `doc/handoffs/TASK-041-3230f45.md`、`doc/tasks/TASK-041.md`、`doc/STATUS.md` 台账、`verification/TASK-041/**`

## 关闭关系与遗留

- **关闭**：**TASK-023 遗留①（MOBI 光栅化 `BLOCKED`）**——解锁条件（用户批准 MOBI 解析依赖）已达成，并由 TASK-041 交付并经两轮 Review + 集成验证。
- **新登记 `BLOCKED`**：**AZW3/KF8 导入**（双格式或 KF8-only 容器一律 typed `INVALID_DOCUMENT`）。解锁条件＝专门切片在**真实 AZW3 样本**上验证 KF8 树（双格式容器的 `mobi7/` 树属未验证降级转换，同样不信任）。
- **登记不阻塞（R-101，P3）**：同一 record 号配两个扩展名会被当成两页；真实 `mobi` 绑定对同一 record 只写一个文件，**当前不可达**。
- **仍未验证**：真实商业 DRM 样本（以合成加密容器替代，首轮已如实登记）；真机 GUI 导入流程（无 UI 入口 E2E 触点，`importDocumentsFromUrls` 的契约由 `tests/core/test_bootstrap.py` 覆盖）。
