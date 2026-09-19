---
task_id: TASK-061
author: ZCode
recipient: Qoder
base_commit: 6cb0afb
delivery_head: 032dc3a
status: draft
---

# Handoff：TASK-061（连接注册表驱逐与 remove_managed 解析一致性）

## 交付结果

基线 master `6cb0afb`（= Task base `cc4d966` 之后的 master 头，`git diff cc4d966..6cb0afb -- src tests` 为空），分支 `agent/zcode/TASK-061-connection-eviction`（worktree `G:/CODEX/New Manga.worktrees/TASK-061-zcode`），实现 head `032dc3a`，其前 `cbf64f1` 为 in_progress 文档 commit。

### AC 逐项对照

- **AC①（驱逐 + 判别力）**：`connection.py` 的 thread-local 槽位同时持可弱引用的 **lease 哨兵**（`_ConnectionLease`）；lease 的 weakref 回调做驱逐（registry 弹槽 + `conn.close()`）。**并发安全论证（结构性，非时序性）**：回调只能在该线程的 thread-local 被销毁后触发——CPython 引用计数保证触发时除回调闭包（回调内 close 用）外无任何代码可再拿到该连接，因此"不得在另一线程仍持有该连接时回收"自动成立；与 `close()`（drain 后全关）无竞争窗口：drain 成功 ⇒ worker 线程已终止 ⇒ 其驱逐回调已完成；drain 超时 ⇒ `_shutdown_services` 不调 close（TASK-060 Q-003 语义）。三项机制 spike（记录于 `cbf64f1`）：①QThread 线程死亡**会**回收其 `threading.local` 值（sentinel weakref 归零实测）；②`_DummyThread` 死后残留 `threading.enumerate()` ⇒ 死线程扫描不可用；③`sqlite3.Connection` 不可弱引用 ⇒ 必须哨兵代理。**修前/修后对照（artefact）**：修前 4 run registry=[2,3,4,5] 单调增长（e2e 失败文本即机理）；修后=[1,1,1,1]、open ≤2（`tests/workbench/test_connection_eviction.py`）。
- **AC②（解析一致性 + 判别力）**：`remove_managed` 新增第三层守卫——沿**未解析**路径逐级 `lstat`，任一级为 reparse point（Windows `FILE_ATTRIBUTE_REPARSE_POINT` / POSIX `S_ISLNK`）→ `ImmutablePathViolation`（typed）。判别用例 `TestR010ReparseWalk`（按 Qoder 复审上移一级）：`mklink /J` 根内 **book 级**目录 junction（`books/book-twin → books/book-1`）→ 另一 chapter 的受保护原件（ref `books/book-twin/chapters/chapter-1/original/keep.png`），修前删除成功（取证脚本实证目标消失）、修后 typed 拒绝且**目标存活**。声明限制：仅覆盖目录 junction 形态（`mklink /J` 无需特权）；文件符号链接需开发者模式/特权，未覆盖；POSIX symlink 走 `S_ISLNK` 分支在本机未实测。
- **AC③（R-011）**：死条件 `"." in PurePosixPath(...).parts` 删除——词法守卫改读原始 `replace("\\","/").split("/")` 段：`.`/`..`/中段空串均 typed 拒绝。判别用例 ×2（`TestR011DotSegmentIsAlive`）：`books/./keep.png` 与 `books//keep2.png`，修前词法干净、文件被删；修后拒绝且文件存活。`PurePosixPath` import 已移除（不再使用）。
- **AC④（供 TASK-057 前置①引用）**：新增 `ThreadRoutedConnection.any_in_transaction()`——聚合"是否还有任何已注册连接在事务中"，直读注册连接**不建新连**（用例断言 registry_size 在聚合读前后不变，钉死 R-004 的"读属性即建连"坑）。**TASK-057 前置①应引用的断言**：`workbench.shutdown() is True and not services.conn.any_in_transaction()` ⇒ drained 且无其他写者。（`release_current_thread_connection()` 亦已提供——仅调用线程自己可释放，供后续切片在安全点显式调用。）
- **AC⑤（不回归）**：全仓 5/5 次 **930 passed / 0 skipped**，collected 930 = 923（master `6cb0afb` 基线）+ 7 新增用例；四目录回归 178 passed。无新增 skip/xfail、无断言放宽。
- **AC⑥（证据口径，协议 §6 第 12 条）**：判别力全部为 artefact（3 份修前日志入库，见下表）；每份日志带 EXIT 码 + shell/venv/commit/env 头。
- **AC⑦**：本 Handoff 即交付；Review/集成/STATUS 收口待 Qoder（Review）与 Codex（集成）。

## 验证证据

环境（全部证据同一 shell + 同一 venv）：PowerShell 5.1（`powershell.exe -NoProfile`）、venv `G:\CODEX\New Manga.task-envs\TASK-012-py312\Scripts\python.exe`（Python 3.12.3）、`PYTHONDONTWRITEBYTECODE=1`、`-p no:cacheprovider`、未设 `QT_QPA_PLATFORM`。

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC① e2e 判别（修前） | 修前树（`git worktree … --detach 6cb0afb`，`test_connection_eviction.py` 复制入树未提交）单跑 | 同上 @ **6cb0afb**（pre-fix） | **FAIL（预期）**：`registry grew with completed runs: [2, 3, 4, 5]`，EXIT=1 | `verification/TASK-061/prefix-discrimination/connection-eviction-prefix-run1.log` |
| AC①④ 单元判别（修前） | 同上树跑 `tests/core/test_connection_ownership.py`（整文件，含 try/finally 修复后的真退出验证） | 同上 @ 6cb0afb | **3 failed / 2 passed（预期），进程真退出（0.26s）**：`ThreadRoutedConnection` 无 `registry_size/release_current_thread_connection/any_in_transaction` | `verification/TASK-061/prefix-discrimination/connection-ownership-unit-prefix-run{1,2}.log`（run2 为 try/finally 修复后整文件取证，EXIT=1） |
| AC②③ 判别（修前） | 同上树跑 `tests/storage/test_managed_storage.py`；junction 用例已上移一级（books/book-twin → books/book-1），并另跑入库取证脚本展示「删除成功 + 目标消失」 | 同上 @ 6cb0afb | **3 failed（预期）**：junction 穿越未被拒绝且受保护原件确实消失（helper `exists: False`）、`.`/空段删除成功；既有 7 例 passed | `verification/TASK-061/prefix-discrimination/managed-storage-traverse-prefix-run1.log`、`managed-storage-bookjunction-prefix-run2.log`（pytest EXIT=1 / helper EXIT=0）、`bookjunction-prefix-evidence.py`（已入库可复核） |
| AC①②③④ 修后 | 上述三个测试文件全绿（含 lease 驱逐、junction 拒绝 + 目标存活、`.` 段拒绝、`any_in_transaction` 事务跟踪） | 同上 @ 032dc3a | PASS | 见全仓日志 + 定向命令可复跑 |
| AC⑤ 全仓 ×5 | `python -m pytest -q -p no:cacheprovider`（全仓） | 同上 @ 032dc3a | **5/5 次 930 passed / 0 skipped，EXIT=0** | `verification/TASK-061/full-suite/full-suite-run{1..5}.log` |

**NOT_RUN / 边界声明**：

- 文件符号链接（`mklink` 无参）与 POSIX symlink 未实测（前者需开发者模式/特权；后者本机为 Windows）——`_is_reparse_point` 的 `S_ISLNK` 分支按标准库语义实现，未在本机走通。
- `release_current_thread_connection()` 的**生产调用点未接线**：本切片白名单不含 `run_controller.py`/`viewmodel.py`，而生产 run 路径的驱逐靠 lease 回调（线程死亡自动触发）完成，已满足 AC① 的"注册表不随 run 数增长"；显式 release 当前仅测试与未来切片（TASK-057 的 drain 门）使用。若 Codex/Qoder 认为应在 `_reap_worker` 成功分支显式调用，属一行接线，需追加白名单后小 commit。
- 挂起归因更正（Qoder 复审指出，原「subprocess 沙箱瞬时问题」归因不实）：判别用例 `test_a_dead_threads_connection_is_evicted` 原先的 `release.set()` 未用 `try/finally` 包住——首个断言失败时 worker 永远停在 `release.wait()`，非 daemon 线程使 pytest 进程无法退出。已修（断言包进 `try`，`finally: release.set()`），修前树整文件跑实证真退出：`prefix-discrimination/connection-ownership-unit-prefix-run2.log`（3 failed / 2 passed in 0.26s，pytest EXIT=1，进程正常返回）。

**既有测试适配（非放宽）**：无既有用例改动；新增 7 用例全部为本切片判别/契约（core 3、storage 3、workbench 1）。

## 接收方式

- 分支 `agent/zcode/TASK-061-connection-eviction`（worktree `G:/CODEX/New Manga.worktrees/TASK-061-zcode`），base `6cb0afb`，head `032dc3a`；未 push。
- 复现（PowerShell）：
  ```powershell
  cd 'G:\CODEX\New Manga.worktrees\TASK-061-zcode'
  $env:PYTHONDONTWRITEBYTECODE='1'
  & 'G:\CODEX\New Manga.task-envs\TASK-012-py312\Scripts\python.exe' -m pytest tests/core/test_connection_ownership.py tests/storage/test_managed_storage.py tests/workbench/test_connection_eviction.py -q -p no:cacheprovider
  ```
- Review 建议重点：
  1. **驱逐并发安全论证**（AC①）：lease weakref 回调"只能在线程死后触发"的引用计数论证是否成立；`_evict` 与 `_current` 的 ident 复用互斥是否完备（`_current` 里 stale 槽 close 分支）。
  2. **`any_in_transaction` 的语义**（AC④）：TASK-057 前置①写法 `shutdown() is True and not any_in_transaction()` 是否足够作为"无其他写者"的可判定门（对照你 TASK-060 复审重点①的建议：facade 补 `any_in_transaction()` / `release_current_thread_connection()`——两者均已落）。
  3. **reparse walk 的覆盖面**（AC②）：junction 用例 + 未覆盖形态声明是否可接受；walk 的性能成本（每级 lstat）。
  4. **R-011 修法**：改真（原始段检查）而非删除，`PurePosixPath` import 一并移除——是否符合你对"删除或改真"的预期。

## 风险与遗留

- 驱逐时机 = 线程死亡（GC 时点）：run 结束到 QThread 完全退出之间连接仍打开（秒级窗口）；长会话内存画像从"随 run 数增长"变为"随**活跃**线程数增长"（≤ GUI+1）。
- `_current()` 的 stale 槽 close 分支（ident 复用）依赖"槽若残留必属死线程"——由驱逐回调保证；若回调因解释器关闭阶段未执行，`close()`（drain 后）兜底全关。
- 关联：TASK-057 前置①自此**可判定**（AC④ 断言）；其②③仍待其自行补齐。TASK-060 复审 R-002/R-010/R-011 全部闭合；R-004 的 docstring 澄清已顺带落在本切片白名单内文件（connection.py 类 docstring）。
