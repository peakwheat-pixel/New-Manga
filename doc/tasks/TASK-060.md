---
id: TASK-060
title: SQLite 连接与事务归属收口（W1 后置复审推翻后的重开切片）
kind: bugfix
status: done
approval: approved_by_user
suggested_owner: ZCode
owner: ZCode
reviewer: Qoder
depends_on: [TASK-048, TASK-058]
base_commit: 9522f2df66a79b82bb2419bc99f84ef39694e513
branch: agent/zcode/TASK-060-sqlite-ownership
worktree: G:/CODEX/New Manga.worktrees/TASK-060-zcode
integration_commit: e7de64dd4f8057adde25b259cef987780d48ca74
---

# TASK-060：SQLite 连接与事务归属收口

**READY（2026-09-19，用户依 Qoder 后置复审报告重开）**：Owner=`ZCode`、Reviewer=`Qoder`（**非作者**；2026-09-19 用户改派，原指派 Codex——Qoder 是 Q-001 探针与后置复审报告的作者，由其验证修复最对口；集成仍由 Codex 执行）、base=9522f2d。开工先 `git merge master`。

## 来源与固定对象

- **被推翻的切片**：W1 [TASK-048](TASK-048.md)，integration **`be558ca`**（**不回滚该 merge**）。
- **裁决依据**：[POSTHOC-WINDOW-2026-09-19-Qoder](../reviews/POSTHOC-WINDOW-2026-09-19-Qoder.md)（`uphold_with_findings` 总论，**W1 单片 `overturn`**）与其 Findings **Q-001（P0）/ Q-002（P2）/ Q-003（P2）/ Q-007（P2）**。
- **主证据**：[verification/POSTHOC-WINDOW-2026-09-19/Qoder/](../../verification/POSTHOC-WINDOW-2026-09-19/Qoder/)——`w1_thread_collision_probe.py` + `w1-thread-collision-run{1..10}.log`（真实 `assemble_services` + 真实 SQLite + 真实 `RunController`(QThread) + 完整 `TRANSLATE_ALL`）。
- **代码内自认**：`src/infrastructure/sqlite/connection.py:28-35` 的 docstring 已写明"两线程共享同一事务 ⇒ 主线程 commit 可落在 worker 的 `with conn:` 内、发布 mid-batch 快照"，并把后果描述为"bounded/self-healed"——本切片就是把这条**归属缺陷**真正收口。

## 目标

把连接与事务的**归属**收敛到单一所有者（**每线程独立连接** 或 **单写者串行化**，二选一并说明取舍），使"两线程各自 commit/rollback 同一事务"在结构上不可能；并顺带收口与其同族的超时关闭竞态与清理面护栏。

## Acceptance Criteria

- [x] **AC ①（归属模型 + 判别力）**：给出模型（per-thread 连接 or 单写者串行化）与理由；新用例在**修前**（`be558ca` 或 `9522f2d`）失败、修后通过（判别力留证）。
- [x] **AC ②（写者返回成功 ⇒ 独立连接可读回该行）**：任何写路径返回成功后，**用一条独立的新连接**必须能读回该行（含 GUI 侧写与 worker 侧 `_persist`）；不得出现"返回成功但落盘 0 行"（Q-001 D3 的机理）。
- [x] **AC ③（交错下无孤儿 Revision）**：在强制交错下，**不可变历史不得出现半途 Revision**（不得出现"revision 行已落、其承载对象未落"或反向）；必须给出重复执行的确定性证据（Q-001 D2 的机理）。
- [x] **AC ④（不再静默打死 run）**：交错下 worker run 不得被静默打死并留下 `running` 行；失败必须经 typed 通道可见（Q-001 ④ 的机理）。
- [x] **AC ⑤（`BEGIN IMMEDIATE` 入 typed 通道）**：`src/infrastructure/sqlite/regions.py` 的 `BEGIN IMMEDIATE`（`:210` 附近）纳入 `try` 并映射为 typed 可诊断失败，不得让 sqlite 原生异常穿透到 VM/QML（Q-002）。
- [x] **AC ⑥（超时不得 close）**：`run_controller.py:104-109` 的 `shutdown()` 超时早退后，`_shutdown_services`（`src/bootstrap/app.py:909-910`）**不得**在 worker 仍在写同一连接时无条件 `conn.close()`；要么先完成排空，要么 detach/延后关闭，并把"未排空"写进 diagnostics；`PAUSED` 分支同样要请求停止（Q-003）。
- [x] **AC ⑦（单一"永不清理"谓词）**：`src/application/maintenance/cleanup.py`、`src/infrastructure/filesystem/managed_storage.py`、`tile_cache_sweep.py`、`trash.py` 的护栏收敛为**一个**权威谓词（"解析后前缀 + 行存活 + 每面复用"），并补一致性用例；至少覆盖 Q-007 的 ①（`_is_safe` 只护缓存面）、②（缓存清扫不复核 reparse point）、③（重试守卫按 manifest 成员而非行存活）、④（`retry_pending_cleanups` 不重过 `_is_safe`）、⑤（`_record_pending([])` 整键弹出）。
- [x] **AC ⑧（撤回 flaky 定性）**：`doc/STATUS.md` 的 flaky 条目（`test_worker_run_and_main_thread_access_coexist`）由本切片收口（已由 Codex 先行撤回并指向 Q-001，见该行）；修后该用例应在 ≥10 轮全仓/定向串跑中稳定通过（逐次留证）。
- [x] **AC ⑨（证据口径）**：每份日志必须带 **EXIT 码** 与 **shell/venv 头**（同一 shell + 同一 venv、`PYTHONDONTWRITEBYTECODE=1`、`-p no:cacheprovider`、**不得设 `QT_QPA_PLATFORM`**）；全仓 ≥5 次逐次记录，**不得跌破 911 collected / 0 skipped（openssl 可用口径；本机 PowerShell 口径为 905 passed / 6 skipped，总数必须仍为 911）**；不得新增 `skip`/`xfail`、不得放宽既有断言（Q-009 的口径要求）。
- [x] **AC ⑩** Handoff + `verification/TASK-060/**` + **非作者** Review + 集成；集成后置 TASK-048 为 `done`（或按评审结论收口）并在 STATUS 记录。

## 允许修改范围

- `src/infrastructure/sqlite/**`（连接归属；**不得改 Schema/migration**）
- `src/application/tasks/**`
- `src/ui/viewmodels/workbench/run_controller.py`
- `src/bootstrap/app.py`（仅超时/关闭时序）
- `src/application/maintenance/**`（cleanup 谓词；`cleanup.py` 实际在此）
- `src/infrastructure/filesystem/managed_storage.py`
- `tests/storage/**`、`tests/workbench/**`、`tests/maintenance/**`（cleanup 用例实际在此）、`tests/core/**`
- 本 Task、Handoff、`verification/TASK-060/**`、`doc/STATUS.md`（台账行）

## 禁止范围

- 不得改 Schema/migration、`requirements.txt`、`src/ui/qml/**`、`AGENTS.md`、其他 Task；不得回滚 `be558ca`；不得放宽断言/新增 skip；不 push。

## 依赖、风险与阻塞

- 依赖：TASK-048（被推翻的实现）、TASK-058（退出排空，Q-003 涉及它的关闭时序）。
- **与 TASK-057 的次序**：TASK-057（备份/恢复）**维持冻结**，其集成的**三项前置**（Q-008）＝① 活动 run/并发写者门（或显式先 drain/关闭）、② 删除恒真断言并补真实边界断言、③ 归档修前判别日志——**本切片是①的结构前提**，即 TASK-060 先于 TASK-057 集成。
- 风险：per-thread 连接会改变事务可见性语义（WAL 下跨连接可见性、`BEGIN IMMEDIATE` 的锁等待）；单写者串行化会引入队列与延迟——两条路线都要在 Task 内写明取舍与实测。

## 交付与运行记录

- **实现 commits（本分支）**：`1195baf`（主实现：per-thread 连接归属 + typed BEGIN + drain-aware close + 单一永不清理谓词）、其后测试修正 commit、`dc254fa`（AC④ e2e + AC⑥ drain 契约用例 + VM shutdown 转发 wait_ms 并 cancel PAUSED run）。基线 master=`a2b23ad`。
- **归属模型与取舍（AC①）**：选 **per-thread 连接 facade**（`ThreadRoutedConnection`：threading.local 每线程惰性建真连接，facade 转发 execute/cursor/commit/rollback/with/`__getattr__`；registry 统一 close）。理由：改动集中在连接层、repository/服务零改动、"两线程各自 commit/rollback 同一事务"在结构上不可能发生（每线程只有自己的事务）、WAL 保留读写并发（跨连接读已提交可见，写锁竞争由 busy_timeout=5000 兜底）。**放弃**单写者串行化：需要引入跨线程队列与延迟，改动面波及所有写路径，与本切片"归属收口"目标不成比例。
- **实际测试**（同一 shell + 同一 venv：PowerShell + `TASK-012-py312`，`PYTHONDONTWRITEBYTECODE=1`、`-p no:cacheprovider`、未设 `QT_QPA_PLATFORM`；每份日志带 EXIT + shell/venv 头）：
  - 判别力（修前树 `a2b23ad` detached）：`verification/TASK-060/prefix-discrimination/`——connection_ownership **2 failed ×2**（`connection-ownership-run{1,2}.log`，EXIT=1）；Q-007 护栏 3 failed / 1 passed（`q007-guards-run1.log`，EXIT=1；**reparse-point 用例修前即通过**——pathlib `glob()` 本就不跟随 junction，该用例定位是回归保护而非判别，见日志 note）。
  - AC⑧ 稳定性：`verification/TASK-060/stability-runs/targeted-run{1..10}.log`——定向串跑（connection_ownership + `test_worker_run_and_main_thread_access_coexist` + AC④ e2e + drain 契约）**10/10 轮 8 passed、EXIT=0**。
  - AC⑨ 全仓：`verification/TASK-060/full-suite/full-suite-run{1..5}.log`——**5/5 次 922 passed / 0 skipped、EXIT=0**；collected 922 = 911（master a2b23ad 基线，openssl 可用口径）+ **11 个本切片新增用例**，未跌破基线、未新增 skip/xfail、未放宽既有断言。
- **既有测试适配（非放宽）**：`tests/workbench/test_shutdown_drain.py` 的 stub 适配 `shutdown() -> bool` 新契约（修前返回 None）；`tests/storage/test_run_files_leak.py::test_retry_is_idempotent_when_files_are_already_gone` 的 setup 补 `purge_pages` 使"行已删"的模拟场景字面为真（否则与新行存活守卫冲突）。
- **R-001 返修（Qoder review b28c615，changes_requested → 已收口）**：`ManagedFileStorage.remove_managed` 的组件规则在 b28c615 上**只剩注释、检查代码缺失**——`books/.../original/../original/<neighbour>` resolve 后仍在根内，根内检查放行，篡改的 pending_purges 条目可删除根内邻居。返修在该单点补上真实组件守卫（`..`/`.` 组件与绝对路径一律 `ImmutablePathViolation`，trash 面零改动）；新增判别用例 `TestQ007TamperedEntryCannotDeleteNeighbours`（篡改条目 batch_id 不在 ledger、穿越字面不匹配任何 `managed_original_ref`，行存活守卫两路放行，唯物理守卫可挡）。证据 `verification/TASK-060/r001-fix/`：pre（b28c615 重演，managed_storage stash 回退）1 failed EXIT=1；post 全文件 10 passed EXIT=0；全仓 **923 passed / 0 skipped** EXIT=0（= 922 + 1 新用例）。
- **最近状态（当前，唯一）**：2026-09-19 实现完成、AC①~⑨ 证据齐备；Qoder review 的 R-001 已返修并留证，待 Qoder 复跑判别改判后由 Codex 集成（AC⑩）。

> **2026-09-19 集成收口（Codex）**：`git merge --no-ff` 于 **`%s`**（base `a2b23ad`，delivery `f7745e6`）。Review=[TASK-060-b28c615](../reviews/TASK-060-b28c615.md)，Reviewer=**Qoder（非作者；用户在切片进行中把 Reviewer 由 Codex 改派 Qoder；集成仍由 Codex 负责）**，`changes_requested`@`b28c615` → R-001 返修 → **`approved`@`f7745e6`**。**集成后全仓**：`pytest tests -q -rs` → **917 passed / 6 skipped / EXIT=0（共 923 collected）**——本机 PowerShell 口径 openssl 不可用，6 条为既有 `tests/network` TLS skip；**openssl 可用口径即 923 passed / 0 skipped，总数一致**。**集成时登记的三条 open 项（Reviewer 要求记账，非返工）**：① **R-003 白名单追认**（`src/ui/viewmodels/workbench/viewmodel.py`、`src/infrastructure/imaging/tile_cache_sweep.py`，均为 AC⑥/AC⑦ 的必要落点）；② **R-002 + R-010 + R-011 立案**为后续小切片（`connection.py` 每线程连接注册表**永不驱逐**——TASK-057 前置①正卡在此；`remove_managed` 的词法组件规则跑在 `.resolve()` 之后 ⇒ 根内 junction/符号链接可删同根受保护原件；`"." in parts` 死条件）；③ **AC⑧ flaky 收口完成**（十轮稳定 `verification/TASK-060/stability-runs/**`）、**TASK-048 复归 `done`**。
