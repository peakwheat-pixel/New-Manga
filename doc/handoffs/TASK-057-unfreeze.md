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

## 返修记录（review `TASK-057-b0e4cb1`，R-001~R-006 闭合，base=`b0e4cb1` 补一 commit）

来源：Qoder Review `doc/reviews/TASK-057-b0e4cb1.md`（changes_requested）。核心结论（R-001，实测）：`_restore_in_progress` 只在 `_start_run` 检查，`continueRun`/`_restart_or_abandon`/`retryFailedPages` 三处直呼 `controller.start` —— PAUSED + 闩置位 + `continueRun` ⇒ worker started=True。返修把闩从 VM 单点移到**唯一 worker 出生地**：

1. **R-001 closed——闩落咽喉点**：`run_controller.py` 新增 `RestoreLatchClosedError(RuntimeError)`、`RunController.set_restore_latch(bool)`、`admission_closed` 属性；`start()` **顶部**（先于 `is_running` 检查）置位即抛。VM 侧 `beginRestore/endRestore` 转调 `controller.set_restore_latch`（`_restore_in_progress` 保留为 VM 镜像）；新增 `_start_pending_worker(run)` 统一 `continueRun`/`_restart_or_abandon`/`retryFailedPages` 三面的出生调用（`RestoreLatchClosedError` → typed 错误面「恢复进行中，不能启动任务」stage=run，无 worker 出生）；`_start_run` 的前置检查**保留**（必须先于 `create_run`/`plan_run` 写拒绝，控制器闩是其下的第二层网）。`grep` 核对：`controller.start` 全 VM 仅剩 `_start_pending_worker` 内 1 处。
2. **R-002 closed——`restoreGate()` 上下文管理器**（viewmodel.py）：进入失败抛 `RuntimeError`；主体正常/异常均 finally `endRestore`——失败的恢复不会把工作台永久锁死。
3. **R-001/R-002 测试——门测试 3→9 条**（`tests/workbench/test_restore_gate.py`）：四面真枚举（`startTranslateAll`/`startTranslateUntranslated` 直调；`continueRun` 走**全真 PAUSED 链路** start→pause→drain→闩→continue，`control_run` 真 PAUSED→PENDING 后出生被闩拦；`restartRun`/`retryFailedPages` 按 Reviewer 探针 MODE B 手法 stub service 控制层返回真 PENDING run——内存栈无失败工作可继承、真 planner 会把 fresh plan 成 COMPLETED，故生产语义的 PENDING fresh 只能经 stub 供给）+ 每面断言「无 worker 出生 + 错误面命中」；另加 gate 异常释放、gate 活动 run 入口拒绝两条。**判别证据**：同一 9 条在 b0e4cb1 上 **6 挂 3 过**（continue/restart/retry 三面均 "a run worker was born while the restore latch was engaged"=R-001 现行复现；`admission_closed`/`restoreGate` 两条 AttributeError=咽喉点缺失）——`verification/TASK-057/review-b0e4cb1/gate-fix-discrim-b0e4cb1-run1.log`（逐测试单进程，QThread 硬崩即 worker 真出生的物理证据，exit=127）。
4. **R-004 closed——三处 docstring 真话化**：`run_controller.py` `start()`/`shutdown()`（唯一写者前提改述为咽喉点事实）、`viewmodel.py` 门注释、`connection.py` `any_in_transaction()`（原「rejects every start path」过强表述改为指向 `RunController.set_restore_latch` 咽喉点；快照非准入闸门约束保留）。仅 docstring，零行为。
5. **R-006 closed——判别探针翻转进 EXIT**：`probe_q008_truthy.py` 删恒真尾巴 `assert caught in (True, False)` 改 `assert caught, ...`（pytest 运行器下 `raise SystemExit(0)` 会被判 FAILED/EXIT=1，实测核对后用语义等价的 assert 翻转：判别对象失效⇒EXIT=1、判别力成立⇒EXIT=0）；`probe_r004_latch.py` 修前 AttributeError 分支 `SystemExit(0)`→`SystemExit(1)`。**双树判别**：`0d15018`（`or True` 在、闩不存在）双 EXIT=1——`review-b0e4cb1/probes-r006-flip-discrim-0d15018-run1.log`；b0e4cb1/修复树双 EXIT=0——`review-b0e4cb1/probes-r006-flip-on-b0e4cb1-still-pass-run1.log`。
6. **R-003/R-005/R-007 无代码动作**：R-003 白名单追认归 Codex（本切片不改）；R-005 以实测差值链闭合（见下）；R-007（AC⑤ 次数口径）随返修验证一并满足——本轮全仓 ×1 记录于下表，AC⑤ 的 ≥5 次逐次记录仍以解冻切片 3×942 + 冻结交付 4×912 为累积台账。

**942 差值实证（R-005）**——各锚点 `pytest tests -q --collect-only` 实测（0 skipped 口径下 collected=passed）：`49f45f6`（merge 合入的 master 头，纯 docs 差异至 `17401dd`）= **930** → merge 头 `0d15018` = **938** = 930 + 8（TASK-057 冻结交付 `c5515fb` 的 storage 新套件首次随 merge 进入全仓）→ 解冻切片 `2707ea8`/`b0e4cb1` = **942** = 938 + 4（R-005 聚合方向判别用例 1 + restore 门用例 3）→ 返修树 = **948** = 942 + 6（门测试 3→9）。

### 返修验证证据（工作树在 `b0e4cb1` 之上，提交前采集；同一 Git Bash + TASK-012-py312，PYTHONDONTWRITEBYTECODE=1、QT_QPA_PLATFORM 未设）

| 场景 | 命令 | 结果 | 日志 |
|---|---|---|---|
| Reviewer 探针复跑（非作者，只读复用 qoder-review worktree 探针，ROOT 传本树） | `t057_gate_probe.py <TASK-057-zcode>` | **A.1 PAUSED continueRun 真链路 worker=False+错误面命中；MODE B 三面全 False+错误面命中**（A.0 两面维持 False；A.2/A.3 非闩错误面为内存栈语义，Reviewer 探针自带 MODE B 覆盖该两面） | `review-b0e4cb1/probe-gate-fix-zcode-run1.log` |
| 门测试判别（修前） | b0e4cb1 archive + 9 条门测试 | 6/9 挂（三面 worker 出生 + 2 AttributeError + gate 缺失） | `review-b0e4cb1/gate-fix-discrim-b0e4cb1-run1.log` |
| 探针 R-006 翻转（修前 `0d15018`） | archive 0d15018 + 翻转后探针 | q008 TRUTHY-PASS→EXIT=1；r004 AttributeError→EXIT=1 | `review-b0e4cb1/probes-r006-flip-discrim-0d15018-run1.log` |
| 探针 R-006 翻转（修复树） | 复跑翻转后探针 | q008 DISCRIMINATING-FAIL→EXIT=0；r004 POST-FIX→EXIT=0 | `pre-fix-probes/post-fix-probes-r006-flip-run1.log` |
| 定向（门 + connection ownership/eviction） | `pytest tests/workbench/test_restore_gate.py tests/core/test_connection_ownership.py tests/workbench/test_connection_eviction.py -q` | **16 passed, EXIT=0** | `review-b0e4cb1/targeted-gate-ownership-fix-run1.log` |
| 不回归 | `pytest tests -q -p no:cacheprovider` ×1 | **948 passed, EXIT=0**（942+6；无 skipped、无新增 skip/xfail） | `review-b0e4cb1/full-suite-fix-run1.log` |

白名单核对（返修 commit）：`src/ui/viewmodels/workbench/**`（2 文件）、`src/infrastructure/sqlite/connection.py`（仅 docstring）、`tests/workbench/test_restore_gate.py`、`verification/TASK-057/**`（探针 2 文件 + 日志）、`doc/tasks/TASK-057.md`、`doc/handoffs/TASK-057-unfreeze.md`；零 Schema/依赖/QML、未动 backup.py（R-001 裁定接受项保持原样）、未动 STATUS、无放宽既有断言（门测试只增不删）、无新增 skip/xfail、不 push。

## 接收方式（返修后）

- 分支 `agent/zcode/TASK-057-backup-restore`，worktree `G:/CODEX/New Manga.worktrees/TASK-057-zcode`；delivery_head=`2707ea8`（解冻切片实现）+ handoff docs（`b0e4cb1`）+ **返修 commit（base=`b0e4cb1` 之上的单一 commit，即本文件的提交 HEAD；代码+测试+判别日志+本文档同 commit）**。
- 复现：`pytest tests -q -p no:cacheprovider -rs`；四面判别复跑 `t057_gate_probe.py <本 worktree>`（Reviewer 探针，A.1/MODE B 应全 False+错误面命中）；探针翻转双树判别见返修记录第 5 条（`run-prefix.sh`/`run-postfix.sh` 仍可复跑，脚本名是当初采集时点的历史语义）。
- Reviewer（Qoder）复审入口：`doc/reviews/TASK-057-b0e4cb1.md` 的 R-001~R-007 → 返修记录逐条 disposition；重点核对：① `RunController.start()` 咽喉点闩与 `_start_pending_worker` 三面收敛 ② 门测试四面枚举的判别力（b0e4cb1 上 6/9 挂）③ A.1 真链路 continueRun 面。原切片第 6 项越界（backup.py）已经 Reviewer `b0e4cb1` 裁定接受，不再开放。

## 风险与遗留

- **backup.py 依赖 `facade._current()`（私有方法）**：过渡态适配；装配切片可把「调用线程真连接」收敛为 facade 公开 unwrap 接口后回归改名。
- **R-007(i)/R-008/N-003/N-004 未闭**：不在本切片授权范围（归 TASK-062 复审残留微切片）。
- **既有声明不变**：`pre_restore` 备份记录随覆盖消失（回滚凭据=文件+sidecar）；一致性报告只读不修；**生产接线 NOT_RUN**（bootstrap 未注入 backup 服务，装配切片统一）。
- **回退**：`git revert 2707ea8`（恢复至 `0d15018`；restore 用例将回到 2 failed 裂缝态）。返修 commit 的回退 = revert 该 commit 本身（回到 `b0e4cb1`，门只盖 1/4 start 面——不可单独回退源文件而保留测试）。
