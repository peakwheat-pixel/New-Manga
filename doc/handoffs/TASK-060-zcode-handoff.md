---
task_id: TASK-060
author: ZCode
recipient: Qoder
base_commit: a2b23ad
delivery_head: dc254fa
status: draft
---

# Handoff：TASK-060（SQLite 连接与事务归属收口）

> Reviewer 改派（2026-09-19，用户指示）：`Qoder`（非作者；Q-001 探针/报告作者）替代 Codex 做 Review；集成与 STATUS 收口仍由 Codex 执行。

## 交付结果

基线 master `a2b23ad`，分支 `agent/zcode/TASK-060-sqlite-ownership`（worktree `G:/CODEX/New Manga.worktrees/TASK-060-zcode`），delivery head `dc254fa`，4 个实现/测试 commit：

| commit | 内容 |
|---|---|
| `1195baf` | 主实现：per-thread 连接归属 + typed BEGIN + drain-aware close + 单一永不清理谓词 |
| `8e71151` | 判别用例交错方案改为纯 `commit()`（双树判别成立） |
| `851edcf` | 修正判别 fixture 违反 CHECK 约束导致假阳性（origin/review_state 合法值） |
| `dc254fa` | AC④ e2e + AC⑥ drain 契约用例；VM `shutdown(wait_ms)` 转发并 cancel PAUSED run |

### AC 逐项对照

- **AC①（归属模型 + 判别力）**：选 **per-thread 连接 facade**（取舍见 [TASK-060.md](../tasks/TASK-060.md) 交付记录：改动集中连接层、repository 零改动、交叉事务在结构上不可能、WAL 读写并发保留；放弃单写者串行化——队列/延迟改动面不成比例）。核心改动：`src/infrastructure/sqlite/connection.py` 重写为 `ThreadRoutedConnection`（`threading.local` 每线程惰性建真连接；registry + 锁统一 `close()`；`check_same_thread=False` 仅保留给 facade 跨线程关 worker 连接；`profile={"query_only": False}` 闭包使每条新连接——含 `TOO_NEW` 后重建的——都带 query_only）。模块 docstring 同步重写，废弃 TASK-048 的 "bounded/self-healed" 论述。判别用例 `tests/core/test_connection_ownership.py`：修前 `a2b23ad` detached 树 **2 failed ×2**、修后 2 passed。
- **AC②（写者成功 ⇒ 独立连接读回）**：per-thread 连接下写者 commit 即发布到自己的连接，WAL 下独立新连接立即可见。判别用例 2（`test_writer_success_survives_the_other_threads_rollback`）：writer `with conn:` 写 books、error 线程 rollback，judge 独立连接断言 rows==1；修前共享连接下 error 线程 rollback 会把 writer 的行一起回滚（rows==0，Q-001 D3 机理）→ 修前失败。e2e 层（AC④ 文件）每 50 个抽样写经 judge 独立连接读回。
- **AC③（交错下无孤儿 Revision）**：`test_interleaved_commit_cannot_orphan_a_revision`——writer `BEGIN IMMEDIATE` + INSERT `region_revisions`（origin='user'、review_state='confirmed'）→ other 线程**纯 `commit()`**（无 DML）→ writer rollback → judge 独立连接断言 orphans==0。修前 other 的 commit 发布 writer 半途事务（orphan 行，Q-001 D2 机理）；修后 other 的 commit 是自己连接上的 no-op。确定性：修前 ×2 稳定 failed、修后 10 轮稳定 passed。交错方案迭代史见 `8e71151`/`851edcf`（两写事务重叠修后死锁；DML 在 B commit 前修前变 autocommit 无判别；纯 commit 方案双树判别成立；CHECK 违规值会静默吞线程异常造成假阳性）。
- **AC④（不再静默打死 run）**：`tests/workbench/test_gui_write_during_run.py`——真实 `assemble_services` + 8 页 + 真 `RunController`，GUI 线程显式（`BEGIN IMMEDIATE`…`commit`）与隐式（repository `create_book`）两种事务形态与 TRANSLATE_ALL run 交错至终态；断言 crashed 空、run 终态且落库、抽样写独立连接读回。docstring 声明：本用例判别力在修前是概率性的（确定性判别在 connection_ownership），定位是修后端到端稳定契约。
- **AC⑤（BEGIN IMMEDIATE 入 typed 通道）**：`src/infrastructure/sqlite/regions.py` `commit_region_revision` 与 `src/infrastructure/sqlite/artifacts.py` `_commit_in_transaction` 的 `conn.execute("BEGIN IMMEDIATE")` 移入 try（Q-002 注释），sqlite 原生异常经既有外层映射为 typed（artifacts 外层 `:174` 映射 DB_FAILED）。
- **AC⑥（超时不得 close）**：`run_controller.py` 拆两层——`_reap_worker(wait_ms) -> bool`（纯线程清理；超时 return False 不强杀）与 `shutdown(wait_ms=5000) -> bool`（cancel 活动 run 后 reap）；`_on_finished`/`_on_crashed` 改用 `_reap_worker`（run 自身终态不 cancel，PAUSED 保持可恢复）。`viewmodel.shutdown(wait_ms)`：对 VM 持有的非终态 run 先写 `cancel_requested`（**PAUSED 的 worker 已退出、controller 不再持有该对象——cancel 必须写在 VM 层**，Q-003）。`bootstrap/app.py::_shutdown_services`：`drained = services.workbench.shutdown()`，仅 drained 才 `services.conn.close()`；未排空时 stderr 报告 `shutdown: workbench drain timed out; connection left open (worker thread still writing)` 并保持连接打开（WAL crash-safe + 下次启动 `recover_running_runs` 兜底）。契约用例 `tests/workbench/test_drain_shutdown.py` 4 例（live run True / wait_ms=0 False 后真 drain True / PAUSED cancel / bootstrap 超时跳 close + stderr）。
- **AC⑦（单一"永不清理"谓词）**：策略层 `src/application/maintenance/cleanup.py::is_safe_relative_path(relative_path, *, prefixes)`（组件检查 `..`/`.` + 前缀白名单；`prefixes=()` = 仅组件检查的业务面）为唯一权威谓词；物理层 `managed_storage.remove_managed` 在既有根内检查**之后**追加组件守卫（保持 `../` 走原 "escapes the managed root" 通道，不改变异常语义）；`tile_cache_sweep.list_cache_files` 对候选 `resolve()` 后复核仍在缓存根内（reparse point 不上报）；`trash.py` 重试守卫改行存活判定 `_batch_pages_still_alive`（batch id 匹配 → `get_pages_by_ids`；id 不可恢复（rebuilt 前缀）→ `list_live_managed_refs`，**软删行也算活**）；`_record_pending(add=…, remove=…)` 合并语义替代整键覆盖。一致性用例：`TestQ007SingleNeverCleanPredicate`（3 例）+ `TestQ007RowLivenessGuard`（1 例）。
- **AC⑧（flaky 撤回后收口）**：定向串跑 10/10 轮全绿（含 `test_worker_run_and_main_thread_access_coexist`），逐次留证。
- **AC⑨（证据口径）**：见下表；每份日志带 EXIT 码 + shell/venv 头；collected 922 = 911 基线 + 11 新增用例；未新增 skip/xfail、未放宽既有断言。
- **AC⑩**：本 Handoff 即交付；Review 待 Qoder（非作者），集成/STATUS 收口待 Codex。

## 验证证据

环境（全部证据同一 shell + 同一 venv）：PowerShell 5.1（`powershell.exe -NoProfile`）、venv `G:\CODEX\New Manga.task-envs\TASK-012-py312\Scripts\python.exe`（Python 3.12.3）、`PYTHONDONTWRITEBYTECODE=1`、`-p no:cacheprovider`、未设 `QT_QPA_PLATFORM`。每份日志头部记录 repo@commit/shell/venv/env/pytest 参数/日期，尾部记录 EXIT 码。

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC①③ 判别（修前） | 修前树（`git worktree … --detach a2b23ad`，新用例文件复制入树未提交）跑 `tests/core/test_connection_ownership.py` ×2 | PowerShell + TASK-012-py312 @ **a2b23ad**（pre-fix） | **FAIL（预期）×2**，2 failed，EXIT=1 | `verification/TASK-060/prefix-discrimination/connection-ownership-run{1,2}.log` |
| AC⑦ 判别（修前） | 同上树跑 `TestQ007SingleNeverCleanPredicate` + `TestQ007RowLivenessGuard` | 同上 @ **a2b23ad** | **3 failed / 1 passed（预期）**，EXIT=1 | `verification/TASK-060/prefix-discrimination/q007-guards-run1.log` |
| AC①②③ 修后判别 | `pytest tests/core/test_connection_ownership.py` | 同上 @ dc254fa | PASS（含在下列各轮中） | 同下 |
| AC⑧ 稳定性 | 定向串跑：connection_ownership + `test_run_thread_e2e.py::test_worker_run_and_main_thread_access_coexist` + `test_gui_write_during_run.py` + `test_drain_shutdown.py`，×10 轮 | 同上 @ dc254fa | **10/10 轮 8 passed，EXIT=0** | `verification/TASK-060/stability-runs/targeted-run{1..10}.log` |
| AC⑨ 全仓 | `python -m pytest -q -p no:cacheprovider`（全仓），×5 次 | 同上 @ dc254fa | **5/5 次 922 passed / 0 skipped，EXIT=0** | `verification/TASK-060/full-suite/full-suite-run{1..5}.log` |

**NOT_RUN / 边界声明**：

- reparse-point 用例（`test_reparse_point_named_like_a_tile_is_not_reported`）**修前即通过**：pathlib `glob()` 单层模式不进入 junction，Qoder Q-007② 所述"清扫不复核 reparse point"在现有遍历方式下不可达；本次的 `resolve()` 复核是纵深防御，该用例定位是**回归保护**（防未来遍历改型），不是判别用例——已在日志 note 与修前判别结果中如实记录。
- 未在真实多进程/进程崩溃场景验证 WAL recover（`recover_running_runs` 的既有覆盖不属本切片）；`_shutdown_services` 未排空路径的运行时行为由单测 stub 验证（`calls==[]` + stderr），未做手工退出实测。

**既有测试适配（非放宽，两处，均语义增强）**：

1. `tests/workbench/test_shutdown_drain.py`：stub 适配 `shutdown() -> bool` 新契约（修前 `shutdown()` 无返回值，TASK-058 用例断言的是排空行为本身；现契约返回 drained 布尔，stub 需返回布尔）。
2. `tests/storage/test_run_files_leak.py::test_retry_is_idempotent_when_files_are_already_gone`：setup 补 `repository.purge_pages(("p2",))`——该用例模拟"行已删、文件已清"的幂等重试，但原 setup 只删了文件没删行，与新的行存活守卫语义冲突（行仍在 ⇒ 守卫正确地跳过）。修的是 setup 与模拟场景的一致性，断言未动。

## 接收方式

- 分支 `agent/zcode/TASK-060-sqlite-ownership`（worktree `G:/CODEX/New Manga.worktrees/TASK-060-zcode`），base `a2b23ad`，head `dc254fa`；未 push。
- 复现（PowerShell）：
  ```powershell
  cd 'G:\CODEX\New Manga.worktrees\TASK-060-zcode'
  $env:PYTHONDONTWRITEBYTECODE='1'
  & 'G:\CODEX\New Manga.task-envs\TASK-012-py312\Scripts\python.exe' -m pytest tests/core/test_connection_ownership.py tests/workbench/test_gui_write_during_run.py tests/workbench/test_drain_shutdown.py -q -p no:cacheprovider
  ```
- Review 建议重点（Qoder）：
  1. `connection.py` 的 `ThreadRoutedConnection` 归属模型是否可作为 TASK-057（备份/恢复）前置①"活动 run/并发写者门"的结构基础（`shutdown() -> bool` 的 drained 契约即其依赖的排空语义）；
  2. `viewmodel.shutdown` 在 VM 层 cancel PAUSED run 的归属划分（controller 已不持有该对象）；
  3. `list_live_managed_refs` "软删行也算活"的语义（行存在即被引用；purge 后才消失）；
  4. 判别用例的交错方案（纯 `commit()` 无 DML）与 fixture 合法值（CHECK 约束）。

## 风险与遗留

- per-thread 连接下跨线程写锁竞争由 `busy_timeout=5000` 兜底：极端并发下写路径可能抛 typed `database is locked`（可诊断，不再共享事务交错）。实测 TRANSLATE_ALL × GUI 交错 10 轮无一次触发；若未来出现高频双写者，可再评估串行化队列（本切片明确不引入）。
- `shutdown` 未排空时连接保持打开：进程退出时 OS 关闭句柄，WAL 由下次启动 `recover_running_runs` 收敛；run 内容可能停在半途（与既有 crash 语义一致，不新增数据损失面）。
- Q-007② 的 reparse-point 漏洞在现有遍历下本就不可达（见 NOT_RUN 声明）；若未来 sweeper 改为 `rglob`/跟随链接的遍历，`resolve()` 复核与回归保护用例生效。
- 关联：集成后按 TASK-060 AC⑩ 置 [TASK-048](../tasks/TASK-048.md) 为 `done`（或按评审结论收口）并在 STATUS 记录；TASK-057 的三项前置中①由本切片提供结构基础，②③仍待其自行补齐。
