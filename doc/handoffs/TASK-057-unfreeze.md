---
task_id: TASK-057
author: ZCode
recipient: Codex（集成）；Qoder（Reviewer，非作者）
base_commit: 50c4b1a
delivery_head: 2707ea8
status: delivered
---

# Handoff：TASK-057 解冻前置切片（Q-008 前置②③ + R-004/R-005）

来源：Qoder 对 TASK-057 冻结交付的 Review（维持冻结 + 三项前置，`doc/reviews/POSTHOC-WINDOW-2026-09-19-Qoder.md` Q-008）与 TASK-061 Review 中「R-004 + R-005 并入 TASK-057 立案」的处置（`doc/reviews/TASK-061-067e432.md`）。开工指令：固定 base=`50c4b1a`（冻结交付头），开工 merge master `49f45f6`（→ merge 头 `0d15018`），Reviewer=Qoder（非作者）。

## 交付结果

1. **Q-008 前置②——恒真断言删除并补真实边界断言**：`tests/storage/test_backup_restore.py` `test_backup_does_not_touch_user_source` 原断言 `assert not (managed_root/"user-side").exists() or True` 的恒真尾巴已删，替换为两条真实 AC③ 边界：managed root 内无 user-side 影子目录；user-side 源目录逐文件清点（只有 `art.tiff`，逐字节幸存断言保留）。修前判别证据：模拟回归（user-side 影子写进 managed root）下修前断言仍 PASS——`verification/TASK-057/pre-fix-probes/pre-fix-q008-truthy-run2.log`（TRUTHY-PASS = 零判别力实锤）；修后同探针 FAIL——`post-fix-q008-truthy-run1.log`（DISCRIMINATING-FAIL = 判别力成立）。
2. **Q-008 前置①/R-004——三件式 restore 门**：
   - **VM 侧闩**（`src/ui/viewmodels/workbench/viewmodel.py`）：新增 `beginRestore() -> bool`（有活动 run 时拒绝并返回 False）/ `endRestore()`；`_start_run` 开头检查 `_restore_in_progress`，闩置位期间所有 start 路径（`startTranslateAll` / `startTranslateUntranslated` / `startTranslateSelected` / `startRegionCommand` 经由 `_start_chapter_command`/`_start_run`）被拒，typed 错误面（`commandErrorText`，stage=run）输出「恢复进行中，不能启动任务」。
   - **docstring 前提**：`RunController.start()` 写明唯一写者前提——「the worker started here is the **only non-GUI writer** to the shared database」，以及 restore 门的组合语义（shutdown True + not any_in_transaction + VM 闩）；`RunController.shutdown()` 标注为门第一件；`connection.py` `any_in_transaction()` 补 R-004 核心约束——该谓词是**检查时点的快照而非准入闸门**（门后 `start()` 的新写者对它不可见；空闲活线程恒读 False），restore 期间必须由 VM 闩兜底。
   - **测试**：`tests/workbench/test_restore_gate.py` 新 3 例（活动 run 时 beginRestore 拒绝；闩置位期间全部 start 路径拒绝且无 run 产生、错误面可断言；endRestore 释放后正常启动）。修前判别证据：修前树 `vm.beginRestore` 不存在（AttributeError，startRun 无任何拒绝路径）——`pre-fix-r004-latch-run1.log`；修后 POST-FIX（闩拒绝 + 释放）——`post-fix-r004-latch-run1.log`。
3. **R-005 聚合方向判别用例**：`tests/core/test_connection_ownership.py` `TestR004AggregatedWriterView` 新增 `test_any_in_transaction_sees_the_other_threads_write`——另一线程持 `BEGIN IMMEDIATE` + INSERT 停在事务中（Event 强制交错），GUI 侧断言 `any_in_transaction() is True` 且 `conn.in_transaction is False` 且 registry 不增；聚合退化 per-thread 读时第一断言即红。文件既有 Event 交错手法，rollback 在 finally 兜底。
4. **R-003/R-006 docstring 收窄**（`src/infrastructure/sqlite/connection.py`，仅 docstring）：`_ConnectionLease`/`_evict` 的「no code path can reach the connection」收窄为「no code path **through the facade**」，并把「cursor/真连接句柄不得跨线程或超出生存期逃逸存活（逃逸句柄 evict 后用即 ProgrammingError）」写成显式调用约束；模块 docstring 与 `open_connection_count()` 写明 R-006 例外——该观察接口对**其他线程的已注册连接**执行只读 `SELECT 1` 探测（无副作用、不开不关不提交）。`release_current_thread_connection()` 生产 0 调用点，保持现状未动。
5. **N-002**：`tests/core/test_connection_ownership.py` `test_a_dead_threads_connection_is_evicted` 两处 `barrier.wait()` 改 `barrier.wait(5)` 并断言返回（worker 在屏障前死亡时主线程不再永久阻塞）。
6. **backup.py 最小 facade 适配（越界登记，交 Reviewer 裁定）**：merge master 后 `restore_backup` 在 `backup.py:171` 抛 `TypeError: backup() argument 'target' must be sqlite3.Connection, not ThreadRoutedConnection`——TASK-060/061 引入的 ThreadRoutedConnection 与冻结交付（基于裸连接模型）的集成裂缝，merge 后基线 2 failed。修复为 1 行：`source.backup(self._conn)` → `source.backup(self._conn._current())`（取调用线程真连接；facade 不是 sqlite3.Connection，restore 门保证该连接空闲、满足 backup API 要求）+ 注释。**授权依据**：开工指令允许列表未列 `backup.py`，但 TASK-057 原始 Task 白名单明确含 `src/infrastructure/sqlite/**`（备份/恢复相关），且本切片的验收口径（判别力/集成可用）在 2 failed 下不成立；不改恢复语义、无 Schema/依赖变化。**请 Qoder/Codex 对此越界作裁定**；若裁不接受，回退该行将使 restore 用例重新失败（裂缝留待装配切片）。

白名单核对：`tests/**`（TASK-057 相关 3 文件）、`src/ui/viewmodels/workbench/**`（2 文件）、`src/infrastructure/sqlite/connection.py`（仅 docstring）、`verification/TASK-057/**`、`doc/tasks/TASK-057.md`、`doc/handoffs/TASK-057-*.md`；零 Schema/migration、零依赖、零 QML/AGENTS/其他 Task、未动 STATUS 台账；无放宽既有断言（恒真断言处为**加强**）、无新增 skip/xfail、不 push。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| 前置② 判别（修前） | `pytest verification/TASK-057/pre-fix-probes/probe_q008_truthy.py -q -s`（模拟回归：user-side 影子写进 managed root） | `0d15018`（merge 头，改动前）+ Git-Bash + TASK-012-py312，PYTHONDONTWRITEBYTECODE=1、QT_QPA_PLATFORM 未设 | **TRUTHY-PASS**：恒真断言在模拟回归下仍通过 ⇒ AC③ 零判别力实锤 | `pre-fix-probes/pre-fix-q008-truthy-run2.log`（run1 为误收集版本，保留不删） |
| 前置② 判别（修后） | 同一探针复跑 | `2707ea8` | **DISCRIMINATING-FAIL**：断言抓住模拟回归 ⇒ 判别力成立 | `pre-fix-probes/post-fix-q008-truthy-run1.log` |
| R-004 门判别（修前/修后） | `python probe_r004_latch.py`（闩存在性 + 闩置位拒绝 startRun + endRestore 释放） | 修前 `0d15018` / 修后 `2707ea8` | 修前 **AttributeError（无闩）**；修后 **POST-FIX：闩拒绝 + 正常释放** | `pre-fix-r004-latch-run1.log` / `post-fix-r004-latch-run1.log` |
| restore 语义修复 | `pytest tests/storage/test_backup_restore.py` | `2707ea8` | **8 passed**（merge 后原 2 failed 的 TypeError 已由第 6 项修复；覆盖语义/pre_restore/typed 全绿） | 会话记录，全量日志覆盖 |
| R-005/N-002/门 | `pytest tests/core/test_connection_ownership.py tests/workbench/test_restore_gate.py tests/workbench/test_connection_eviction.py` | `2707ea8` | **10 passed**（R-005 新例 + 门 3 例 + 既有全绿） | 会话记录，全量日志覆盖 |
| 不回归 | `pytest tests -q -p no:cacheprovider -rs` ×3 | `2707ea8`，Git-Bash + TASK-012-py312，PYTHONDONTWRITEBYTECODE=1、QT_QPA_PLATFORM 未设 | **3×942 passed, EXIT=0**（942 ≥ 930 基线；+4 = R-005 1 + 门 3；无 skipped、无新增 skip/xfail） | `verification/TASK-057/unfreeze-full-suite-run{1,2,3}.log` |

## 接收方式

- 分支 `agent/zcode/TASK-057-backup-restore`，worktree `G:/CODEX/New Manga.worktrees/TASK-057-zcode`；delivery_head=`2707ea8`（实现）+ 本文档提交。
- 复现：`pytest tests -q -p no:cacheprovider -rs`；判别复跑 `bash verification/TASK-057/pre-fix-probes/run-prefix.sh`（修前语义） / `run-postfix.sh`（修后语义）。
- Reviewer（Qoder）：重点裁定第 6 项越界；核对三件式门与 `any_in_transaction` docstring 的快照约束是否覆盖 Q-008 前置①的全部关切。

## 风险与遗留

- **backup.py 依赖 `facade._current()`（私有方法）**：过渡态适配；装配切片可把「调用线程真连接」收敛为 facade 公开 unwrap 接口后回归改名。
- **R-007(i)/R-008/N-003/N-004 未闭**：不在本切片授权范围（归 TASK-062 复审残留微切片）。
- **既有声明不变**：`pre_restore` 备份记录随覆盖消失（回滚凭据=文件+sidecar）；一致性报告只读不修；**生产接线 NOT_RUN**（bootstrap 未注入 backup 服务，装配切片统一）。
- **回退**：`git revert 2707ea8`（恢复至 `0d15018`；restore 用例将回到 2 failed 裂缝态）。
