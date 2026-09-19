---
task_id: TASK-057
reviewer: Qoder（非作者）
author: ZCode
base_commit: 50c4b1a
reviewed_head: b0e4cb1
decision: changes_requested
review_scope: 解冻前置切片（merge 头 0d15018 → 实现 2707ea8 → 文档 b0e4cb1）
---

# Review：TASK-057 解冻前置切片（Q-008 前置①② + R-003~R-006/N-002）

**一句话**：前置②（恒真断言）**已真正闭合**——我用作者同一件探针在 `0d15018` 复现 `TRUTHY-PASS`、在 `b0e4cb1` 复现 `DISCRIMINATING-FAIL`，新断言是真边界；TASK-061 复审留下的 R-005 / N-002 / R-003 / R-006 四条都落到位，全仓 942 passed / 0 skipped 我复跑 ×2 一致。**但前置①的门只盖住了四个 start 面中的一个**：`_restore_in_progress` 只在 `_start_run` 检查，`continueRun` / `_restart_or_abandon` / `retryFailedPages` 三处直接 `self._controller.start(...)`。我用真实 in-memory 服务跑到 PAUSED 态、闩置位后调 `continueRun` ⇒ **worker started = True**（不是读码推断）。而"rejects every start path"这句话现在写在四处交付物里，包括 `connection.py` 的 docstring。阻断批准的正是这一条：**门是本切片的验收物本身，且它存在的唯一目的是"接线之前必须先闭合"。** 第 6 项越界（`backup.py`）我**裁定接受**——它其实落在 TASK-057 原白名单 `src/infrastructure/sqlite/**` 内；反倒是真正超出 Task 白名单的 `src/ui/viewmodels/workbench/**` + `tests/workbench/**` 未登记。

（本报告自己的 findings 记为 R-001~R-007；凡指向前任复审的条目一律写作 `TASK-060 R-xxx` / `TASK-061 R-xxx`，避免跨任务串号。）

## 范围与依据

- 来源顺序：[TASK-057.md](../tasks/TASK-057.md)（AC①~⑥ + 允许/禁止范围 + 冻结交付记录）→ 前置三项的**原文**（[Q-008](POSTHOC-WINDOW-2026-09-19-Qoder.md)，我本人所写）→ TASK-061 的 R-003/R-004/R-005/R-006 与 N-002 的**原文**（[TASK-061 复审](TASK-061-067e432.md) Findings 与 disposition）→ [Handoff](../handoffs/TASK-057-unfreeze.md) 的逐条自述。
- diff 面（`git diff --numstat 0d15018..b0e4cb1 -- src tests`）：`sqlite/backup.py` 7/1、`sqlite/connection.py` 46/8、`workbench/run_controller.py` 19/0、`workbench/viewmodel.py` 37/0、`tests/core/test_connection_ownership.py` 65/2、`tests/storage/test_backup_restore.py` 15/1、`tests/workbench/test_restore_gate.py` 83/0（新）。`connection.py` 的 46/8 我逐行核过 **全是 docstring**（零语句改动）；`run_controller.py` 19/0 亦全为 docstring。**实现改动只有三处**：`backup.py` 一行、VM 闩 + `_start_run` 检查、测试。
- **受影响调用链**：`WorkbenchViewModel` 里能起 worker 的地方共 **4 处**（`viewmodel.py:700` 在 `_start_run` 内、`:784` continueRun、`:808` `_restart_or_abandon`、`:827` retryFailedPages）——只有第 1 处受闩保护；`RunController.start()` 自身只查 `is_running`（`run_controller.py:74-77`），无准入闩。生产接线：`git grep beginRestore\|endRestore -- src` ⇒ **仅定义处**（我的探针把这条命令的输出并入了日志）；`git grep any_in_transaction -- src` ⇒ 只有注释；`grep backup src/bootstrap/app.py` ⇒ **备份服务未注入装配**。故"restore 正在发生"今天在生产路径上不可达。
- 未审到：真机 GUI 会话、真实 sqlite 库上的 restore 与并发起跑的组合（本切片的门是 VM 层判定，我用 in-memory pipeline 度量准入；见验证表 R-3 的口径声明）；POSIX 平台分支。

## Spec（可选视角）：executed

- **前置②（Q-008）达成**：`assert not (managed_root/"user-side").exists() or True` 的恒真尾巴删除，并补第二条真边界（`user_source.parent` 逐文件清点 == `['art.tiff']`）。判别力**双翻转我独立复现**（同一探针、两棵树）。
- **前置①（Q-008 / R-004）部分完成**：可判定形式（TASK-061 已给）+ VM 闩到位 ✔，但"闩住期间不再有写者被放进库"这一实质**只在 4 个面中的 1 个成立**（R-001，实测）。且闩无释放保障（R-002）：一旦置位，除显式 `endRestore()` 外无任何解除路径。
- **TASK-061 R-005 达成**：`test_any_in_transaction_sees_the_other_threads_write` 断言"他线程 `BEGIN IMMEDIATE` 时聚合 True 且本线程 False"——正是我上一轮 M1 代测的那个方向，用例形态（Event 强制交错 + `finally` rollback）与既有手法一致。修前该 API 缺失 ⇒ 判别为 AttributeError（可接受；聚合"退化为 per-thread 读"时的红，我按读码判定为真红：第一断言即 `is True`）。
- **TASK-061 R-003/R-006/N-002 达成**：措辞收窄准确（"through the facade"、"escaped raw handle 属 caller 违约、evict 后用即 `ProgrammingError`"），`open_connection_count` 的跨线程 `SELECT 1` 例外写进模块 docstring 与方法 docstring 两处；`barrier.wait(5)` + 断言返回值正是我建议的形状。
- **来源未要求但已改**：`backup.py`（见 R-003 裁定）。**范围声明有误**：Handoff 的「白名单核对」把 `src/ui/viewmodels/workbench/**` 与 `tests/workbench/**` 列为已核对项，但 TASK-057 的 允许修改范围 只有 `src/application/**`、`src/infrastructure/sqlite/**`、`tests/storage/**`、`tests/core/**`（见本报告 R-003）。

## Standards（可选视角）：executed

`AGENTS.md`「修改共享接口…先在 Task 中由 Codex 明确范围」：`viewmodel.py` 新增两个 public Slot 级方法（`beginRestore`/`endRestore`）属共享 VM 接口，Task 白名单未含 VM ⇒ 需追认（本报告 R-003）。§6.12：**本切片自己的 8 份日志**（`pre-fix-probes/` 5 份 + `unfreeze-full-suite-run{1,2,3}.log`）全部带 shell/venv/env 头 + EXIT ✔（含保留不删的误收集版本 `pre-fix-q008-truthy-run1.log`，"3 passed"）；冻结交付那轮的 `full-suite-run{1..5}.log` 同样带环境头，`run6/7` 只有 `EXIT=` 无环境头（属 Q-009 明文化之前的遗留，不计入本切片）；差值口径见 R-005。

baseline smell：possible **Duplicated Code / Message Chains** —— 闩检查以"每个调用点各查一次"的形式散布（实际只查了一处），咽喉点防护应落在 `RunController.start()`；possible **Speculative Generality** —— `beginRestore`/`endRestore` 生产 0 调用点（作者已在 §风险与遗留声明 restore 未接线，判定为"门等接线"而非投机，但要求接线切片的 AC 显式包含它，见建议）。

## Architecture

**结论：本切片的方向（把准入责任从"聚合谓词"移到"VM 闩"）是对的，但移动没做完。** 三点技术判断：

1. **闩必须落在咽喉点。** `RunController.start()` 是唯一的 worker 出生地，VM 里四个调用面全部经过它。把检查放在 VM 的三个方法里（现在只放了一个）等于把不变量交给"未来别再加第五个 start 面"这个愿望。修法小且可核：`RunController` 加 `_admission_closed` + `set_restore_latch(bool)`，`start()` 在置位时抛 typed 错误（VM 侧 `_record_command_error` 已有现成错误面），VM 的 `beginRestore/endRestore` 只转调它；新增判别用例改为对**四个面各调一次**断言"无 worker 出生"。这样 R-001 与它的复发被同一件事消灭。
2. **闩要有自关保障。** 现状：`beginRestore()` 置位 → 若恢复主体抛异常，无人解除 ⇒ 工作台永久拒绝所有受保护路径（我实测 `_restore_in_progress=True` 且 `startTranslateUntranslated` 仍被拒）。作者把 `endRestore` 写成显式调用是合理的最小面，但一个"永久锁死整个任务面板"的失败模式不该只靠调用纪律。建议 `restoreGate()` 上下文管理器（`__enter__` 返回是否成功、`__exit__` 必解除），并在接线切片 AC 里写"restore 必须经 gate 对象"。
3. **backup.py 适配（第 6 项）技术上站得住。** `source.backup(dest)` 的方向正确（把备份文件覆盖进活库），目标取**调用线程**的真连接符合 facade 模型，1 行 + 注释、无 Schema/依赖变化。作者自报"依赖私有方法 `_current()` 是过渡态"我认同：装配切片应在 facade 上给一个公开 unwrap（例如 `connection_for_current_thread()`），把三处 `._current()` 用法收敛。**同时必须记账的是**：同一行代码在 master 上同样坏（`git show 0e25764:src/infrastructure/sqlite/backup.py` 的 `:50/:171` 同形态），而 **master 的测试树里没有任何 backup 用例**（`git ls-tree -r 0e25764 tests | grep -i backup` 为空）⇒ 这是 TASK-060 归属改造留下的**潜伏运行时缺陷**，只有本分支的冻结用例第一次照到它。我自己在 TASK-060 复审时核了连接归属、事务交错、drain，**没有跑过 backup/restore 面**（当时它只存在于冻结分支，master 无覆盖）——这条盲点写进本报告，避免下一个读者以为"master 一直是绿的"。

## 交付方指定的重点答复

1. **第 6 项越界裁定：接受，且它本来就 authorized。** TASK-057 允许范围白纸黑字含 `src/infrastructure/sqlite/**`（备份/恢复相关），`backup.py` 在其内；作者的疑虑来自"开工指令未列"，但按 AGENTS.md 授权以 Task 文件为准。修复是解冻后跑通本 Task 自己 AC 的必要条件（我在 `0d15018` 独立复现 2 failed / 6 passed、`TypeError: backup() argument 'target' must be sqlite3.Connection, not ThreadRoutedConnection` at `backup.py:171`）。**两个附带条件**：①STATUS 集成行须写"master 亦带同一裂缝、无测试覆盖，本切片首照出"（别让台账读起来像分支自身的问题）；②装配切片把 `._current()` 换成公开 unwrap，且 `tests/storage/test_backup_restore.py` 必须随本 Task 集成进入 master 全仓（它已经是 942 的一部分，别在集成时掉出去）。
2. **三件式门是否覆盖 Q-008 前置①全部关切：不覆盖。** 件的①（drained）②（not any_in_transaction）都在，③（闩）不完整（R-001）且无自关保障（R-002）。另需一句前置①之外的实话：今天 `any_in_transaction` / `beginRestore` 生产 0 调用点，门是"可组合的零件"而不是"已生效的策略"——这正是它该在解冻前补齐的理由，不是缺陷。
3. **恒真断言修复：确认为真修复。** 除删除 `or True`，新增的第二条断言（源目录逐文件清点）把"备份器不写用户源目录"变成了可失败断言；模拟回归（往 managed root 写 `user-side`）在修后树上被抓住。
4. **TASK-061 R-005 用例与 N-002：接受。** 用例断言方向正确（聚合 True + 本线程 False + registry 不增）；N-002 两处 `barrier.wait(5)` 并断言返回值，与我建议一致。

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态 |
|---|---|---|---|---|---|---|
| R-001 | **P1（阻断）** | `src/ui/viewmodels/workbench/viewmodel.py:681-686`（唯一检查点）对 `:784`、`:808`、`:827`（三处无检查）；声称见 Handoff 第 2 项、`tests/workbench/test_restore_gate.py:5-7` 与用例名 `test_latched_restore_rejects_every_start_path`、`connection.py:238-239`、`run_controller.py:83` | restore 闩置位期间，`continueRun` / `restartRun` / `retryFailedPages` 仍可各起一个 worker ⇒ 恢复正在覆盖活库时写者被放进库，正是本门唯一要防的后果。**实测**（真实服务、真 QThread）：PAUSED run + `beginRestore() is True` + `continueRun()` ⇒ `worker started during restore? True`（无任何闩错误文本）；MODE B 把状态钉成 PENDING 后**三面全 True**。A.2/A.3 在 MODE A 未起 worker 只是因为 mock 状态机拒绝（错误文本 `RUN_NOT_INTERRUPTED` / `TARGET_NOT_FOUND`），**不是闩挡住了**。 shipped 用例的"every start path"只枚举了 `startTranslateAll`/`startTranslateUntranslated` 两个共享同一咽喉的方法 | [复现] `verification/TASK-057/review-b0e4cb1/probe-gate-b0e4cb1-run1.log`（MODE A.1 / MODE B / A.2 A.3 错误文本）；[读码] `grep -n "_controller\.start" viewmodel.py` 四处 | **把闩落到咽喉点**：`RunController` 持 `_admission_closed` + `set_restore_latch()`，`start()` 置位即拒（typed 错误经 VM 既有错误面），VM `beginRestore/endRestore` 只转调；判别用例改为对**四个面各调一次**并断言无 worker 出生。若坚持 VM 层修法，则三个面补同样的 `if self._restore_in_progress` + 各一条判别用例 | open |
| R-002 | P2 | `viewmodel.py:708-731` | 闩只有显式 `endRestore()` 一条解除路径：无 `try/finally`、无超时、无上下文管理器。恢复主体抛异常 ⇒ 工作台永久拒绝所有受保护 start 路径（今日不可达因无生产调用点；接线后即为不可自恢复的死锁） | [复现] 同探针 G5 段：`_restore_in_progress=True` 且 `startTranslateUntranslated` 继续被拒；[读码] `git grep beginRestore\|endRestore -- src` 仅定义处 | 提供 `restoreGate()` 上下文管理器（`__exit__` 必解除），并在接线切片 AC 里写"restore 必须经 gate 对象"；本切片可只加 context manager + 一条"抛异常后闩自动解除"的用例 | open |
| R-003 | P2（治理，非代码缺陷） | `doc/tasks/TASK-057.md` 允许修改范围 vs 实际改动；Handoff「白名单核对」段 | 授权方向**报反了**：登记的越界项 `backup.py` 其实**在** Task 白名单（`src/infrastructure/sqlite/**`）内；而真正不在白名单的 `src/ui/viewmodels/workbench/viewmodel.py`、`run_controller.py`、`tests/workbench/test_restore_gate.py`（Task 只列 `tests/storage`、`tests/core`）被 Handoff 当作已核对项列出。按 AGENTS.md「修改共享接口先在 Task 中由 Codex 明确范围」，需**追认**而非默认合法（改动本身由 AC 需要驱动，方向正确） | [记录] `sed -n '/## 允许修改范围/,/## 禁止范围/p' doc/tasks/TASK-057.md` 与 `git diff --numstat 0d15018..b0e4cb1 -- src tests` 逐行比对 | Codex 集成前在 Task 白名单补三行：`src/ui/viewmodels/workbench/**`、`tests/workbench/**`、`src/infrastructure/sqlite/backup.py`（若第 6 项裁定另有结论）；并把 Handoff 的白名单段改成"依据 = 开工指令 + Task 追认" | open（交 Codex 裁决；本裁定的实质结论见上一条答复 1） |
| R-004 | P3 | `connection.py:238-239`、`run_controller.py:83`、`viewmodel.py:115` 与 `:718` | **三处 docstring 把不成立的性质写成成立**："the workbench VM's restore latch … **rejects every start path** while the restore runs" / "every start path is rejected here"。修 R-001 时必须同步改掉，否则文档比代码更强 | [读码] 三处原文 + R-001 实测 | 措辞改"rejects start paths that hold the latch check"（VM 修法）或直接随咽喉点修法变为真话 | open |
| R-005 | P3（台账口径） | `doc/handoffs/TASK-057-unfreeze.md` 证据表"不回归"行；`doc/tasks/TASK-057.md` 最近状态行 | 「942 ≥ 930 基线；+4」在算术上不自洽：930 + 4 = 934。真构成 = **930（master `49f45f6`）+ 8（冻结交付的 restore 用例首次进入全仓）+ 4（本切片：门 3 + TASK-061 R-005 用例 1）**。§6.12 要求"不同口径须给总数与差值解释" ⇒ 差值解释缺 8 | [记录] 我实测 `--collect-only`：`0d15018` = **938**、`b0e4cb1` = **942**（`prefix-collect-count-run1.log`、`full-suite-run{1,2}.log`） | 两处补一句"942 = 938（merge 头）+ 4；938 = 930（master）+ 8（冻结 restore 用例首次入全仓）" | open |
| R-006 | P3（判别探针可机判性） | `verification/TASK-057/pre-fix-probes/probe_q008_truthy.py:51`、`probe_r004_latch.py`（修前主动 `SystemExit(0)`） | 双翻转的**判定只活在 stdout 文案**，两棵树 EXIT 都是 0 ⇒ artefact 在（§6.12 满足），但分支需靠 grep。讽刺点：`probe_q008_truthy.py` 末尾 `assert caught in (True, False)` 是一条**恒真断言**——本切片刚以"删恒真断言"为 AC，探针里又留了一条（作者就地注释了意图，属可接受的探针设计，但同类形态不得进 `tests/**`） | [记录] 我的两份复跑日志 `pre/post-q008-truthy-pytest-rerun2.log`（TRUTHY-PASS / DISCRIMINATING-FAIL，EXIT 均 0）；`prefix/postfix-r004-latch-rerun1.log` 同理 | 让"翻转"进 EXIT：判别对象失效时 `SystemExit(1)`（修前 0、修后 1 或反之），并删掉恒真尾巴改 `raise SystemExit(0)` | open（不阻断） |
| R-007 | P3（AC⑤次数口径） | `doc/tasks/TASK-057.md` AC⑤「≥5 次逐次记录」 | 本切片 ×3（作者，@`2707ea8`）+ 我 ×2（@`b0e4cb1`）= 5，但**跨两个 head 与两个 shell**（Git Bash / PowerShell）。若集成方按"整任务 AC⑤"验收，应在合并后的单一 head 上凑满 ≥5 次同口径 | [记录] 作者 `unfreeze-full-suite-run{1,2,3}.log`（EXIT=0）+ 我的 `full-suite-run{1,2}.log`（EXIT=0，942 passed / 0 skipped） | 集成时在新 master 上跑 ≥5 次并入库；或在本 Task 记录里写明 AC⑤ 的次数以"交付 head"计、集成 head 另计 | open |

**正面（须一并记账）**：前置②是真修复且翻转可复现（不是我认可就算）；TASK-061 R-005 用例落在我上一轮指出的那个缺失方向上、形态与既有 Event 交错手法一致；TASK-061 N-002 按建议两处都改并断言返回值；TASK-061 R-003/R-006 的 docstring 收窄没有把不可达的东西写成保证（"escaped raw handle 属 caller 违约"这句是分寸感正确的写法）；越界项主动登记并给出回退后果；误收集的 `pre-fix-q008-truthy-run1.log` 保留不删并在表里注明；本切片 8 份日志全部带环境头 + EXIT；既有断言零放宽（唯一改动是加强）；无新增 skip/xfail。

## 验证

口径：PowerShell 5.1 + `TASK-012-py312`（3.12.3 CPython）+ `PYTHONDONTWRITEBYTECODE=1` + `PYTHONIOENCODING=utf-8` + `-p no:cacheprovider` + 未设 `QT_QPA_PLATFORM`。修前树 = `git worktree add --detach …/t057-prefix 0d15018` + 未提交的探针副本（与作者同一手法）。我的测量树 = `agent/qoder/TASK-057-review` @ `b0e4cb1`（作者分支 head 的原样检出，未改一字节）。

| # | 场景 | 命令/树 | 结果 | 证据 |
|---|---|---|---|---|
| R-1 | 全仓不回归（AC⑤口径） | `pytest tests -q -rs` ×2 @ b0e4cb1 | **PASS**：`942 passed / 0 skipped / EXIT=0`（两次，54.62s / 53.35s）；与作者 ×3 @2707ea8 同数 | `full-suite-run1.log`、`full-suite-run2.log` |
| R-2 | 定向（门 + 备份 + 连接归属 + 驱逐） | 四个测试文件合跑 @ b0e4cb1 | **PASS**：`18 passed / EXIT=0`（backup 8 + gate 3 + core 6 + eviction 1） | `targeted-post-fix-run1.log` |
| R-3 | 门完整性（**核心**） | `t057_gate_probe.py` @ b0e4cb1：真实 pipeline + 真 QThread；MODE A 用真状态（PAUSED / 终态），MODE B 把 run 钉成 PENDING 以隔离"闩挡住"与"mock 状态机不允许" | **FAIL**：A.0 两面拒（错误面 `[run] 恢复进行中，不能启动任务`）；**A.1 `continueRun` 在闩置位期间起 worker = True**；MODE B 三面全 True；A.2/A.3 未起是 `RUN_NOT_INTERRUPTED` / `TARGET_NOT_FOUND` 所致 | `probe-gate-b0e4cb1-run1.log` |
| R-4 | 闩自关保障 | 同探针 G5 段 + `git grep beginRestore\|endRestore -- src` | **FAIL（设计缺口）**：src 内 0 调用点（只打印定义行）；abandoned restore 后 `_restore_in_progress=True`、受保护路径永久拒绝 | 同上 |
| R-5 | 前置② 判别双翻转 | 作者探针 `verification/TASK-057/pre-fix-probes/probe_q008_truthy.py`（两棵树各自的已入库原件，我不另存副本）经 `pytest -q -s` 复跑 | **PASS**：`0d15018` ⇒ `TRUTHY-PASS`；`b0e4cb1` ⇒ `DISCRIMINATING-FAIL` | `pre-q008-truthy-pytest-rerun2.log`、`post-q008-truthy-pytest-rerun2.log` |
| R-6 | 门判别双翻转（作者探针） | `verification/TASK-057/pre-fix-probes/probe_r004_latch.py` 两棵树 | **PASS（但仅覆盖 `_start_run` 面）**：修前 `AttributeError: no attribute 'beginRestore'`；修后 拒绝 + 释放 | `prefix-r004-latch-rerun1.log`、`postfix-r004-latch-rerun1.log` |
| R-7 | 第 6 项越界的必要性 | `pytest tests/storage/test_backup_restore.py` @ `0d15018` | **PASS（裂缝真实存在）**：`2 failed, 6 passed / EXIT=1`，`TypeError: backup() argument 'target' must be sqlite3.Connection, not ThreadRoutedConnection` at `backup.py:171` | `prefix-backup-tests-run1.log` |
| R-8 | 收集数差值口径 | `pytest --collect-only -q` @ 两棵树 | **PASS**：`0d15018` = 938、`b0e4cb1` = 942 ⇒ 本切片 +4；master 930 → 938 的 +8 是冻结 restore 用例首次入全仓（R-005） | `prefix-collect-count-run1.log`、`full-suite-run1.log` |
| R-9 | 白名单与 src 改动性质 | `git diff --numstat 0d15018..b0e4cb1 -- src tests`；`git show 2707ea8 -- src/infrastructure/sqlite/connection.py`；Task 允许范围逐行比对 | **PARTIAL**：写集合可全对应到文件，但 VM 两面 + `tests/workbench` 不在 Task 白名单（R-003）；`connection.py`/`run_controller.py` 改动经逐行核对确为 docstring-only | 本报告 §范围与依据 |
| R-10 | master 潜伏面核对 | `git show 0e25764:src/infrastructure/sqlite/backup.py`；`git ls-tree -r 0e25764 tests \| grep -i backup` | **记录**：master 同一行同形态、**全仓零 backup 用例** ⇒ 已合并的 TASK-061/060 面上带着这条裂缝，本分支第一次照到 | 本报告 §Architecture 3 |
| R-11 | 未审 | 真机 GUI、真实 sqlite 库上 restore 与并发起跑的组合、POSIX 分支 | **NOT_RUN** | 无 |
| R-12 | docstring-only 改动的行为回归（TASK-061 尺子） | `verification/TASK-061/review-067e432/t061_review_probe.py` T1~T7 + `t061_second_writer_probe.py` M1~M5 @ b0e4cb1（两件脚本已随 TASK-061 复审入库，本树直接跑该路径，不在本轮证据里复制第二份） | **PASS**：T1 registry `[1]×8`（峰值含 2＝活 worker）、1920 线程 0 异常、open=1；`books` 级 junction typed refusal + 目标存活；T4 逃逸 cursor 仍 `ProgrammingError`（与新 docstring 的声明一致）；M3 walk 84 µs / 598 µs = 14%（与 TASK-061 轮同量级） | `ruler-t061-probe-b0e4cb1-run1.log`、`ruler-t061-second-probe-b0e4cb1-run1.log` |

**证据纪律（本报告自身）**：我产出的 14 份日志（本任务 12 份 + TASK-061 尺子复跑 2 份）一律带 shell/venv/env/HEAD 头 + `EXIT=`，runner 随证据入库。**我自己的两处缺陷保留不删**：①首轮我用 `run_probe.ps1` 直接把 `probe_q008_truthy.py` 当脚本跑（`python x.py`，非 `pytest`），两支日志（`prefix-q008-truthy-rerun1.log`、`postfix-q008-truthy-rerun1.log`）因此没有判定文案，属**无效取证**，已用 `pytest -s` 形态复跑为 rerun2；②探针首版 G5 的 `git grep` 用 `text=True` 触发 GBK 解码异常，已改为按字节读 + UTF-8 容错。**自我盲点登记**：我在 TASK-060 复审未跑 backup/restore 面（当时该套件在冻结分支、master 无覆盖），验证表 R-10 所记的潜伏形态因此逃过那一轮——解冻后的第一次复审必须把"冻结交付的套件是否已进入全仓"列为固定检查项。

## 结论与复审

**`changes_requested`**，一条硬的：**R-001（P1）**——本切片的验收物是"restore 期间的准入闩"，而实测证明它只盖住四个 worker 出生面中的一个，且"rejects every start path"被写进了 handoff、用例名与两处 docstring。按 §6.8 P0/P1 未解决不得批准。

**必须说清的另一半**：前置②（恒真断言）**已经**闭合；TASK-061 侧的 R-003/R-005/R-006/N-002 **已经**闭合、R-004 的前提已写进三处 docstring（但门本身不完整＝本报告 R-001）；第 6 项越界我裁定**接受**、全仓 942/0 两次复跑一致。也就是说**要改的只有闩的位置和一个上下文管理器**：把 `_restore_in_progress` 的判定移进 `RunController.start()`，`beginRestore/endRestore` 转调它，判别用例对四个面各测一次，顺手把三处过强 docstring 改成真话（R-004）与加 `restoreGate()`（R-002）。零 Schema、零接线影响、零既有断言放宽。

**给 Codex 的判断材料**：若你希望把 R-001/R-002 与本切片分离（例如先追认白名单、把门完整性并给装配切片），请在 STATUS 明确写"Q-008 前置①**未闭合**：闩只覆盖 1/4 start 面（Reviewer 实测 `continueRun` 起 worker）"，不要让"解冻前置切片已交付"读起来像前置①已成立。另需在同一行记验证表 R-10 的事实：master 带 `backup.py` 的 facade TypeError 且无测试覆盖，是 TASK-057 分支第一次照出它——这关系到我们怎么评价"TASK-060/061 集成后全仓仍绿"这句话。

**复审方式**：新 head 落一个 commit 后，我只复跑 `verification/TASK-057/review-b0e4cb1/t057_gate_probe.py`（期望 MODE A.1 与 MODE B 三面全为 `worker started during restore? False`、错误面出现）+ `tests/workbench/test_restore_gate.py` 与 `tests/core/test_connection_ownership.py` + 全仓 ×1（期望 collected ≥ 942，若按四面各加一条则 945/946），约 10 分钟内可出 `approved`。

## 证据位置与落库状态

本报告与我的全部证据在**我自己的 Review worktree**（`G:/CODEX/New Manga.worktrees/TASK-057-qoder-review`，分支 `agent/qoder/TASK-057-review`，base `b0e4cb1`；**已 commit 于该本地分支，未 push、未合入 master**）下：

- `doc/reviews/TASK-057-b0e4cb1.md`（本报告）
- `verification/TASK-057/review-b0e4cb1/`（17 个文件）：`t057_gate_probe.py`（我的门探针）、`run.ps1`、`run_probe.ps1`（带环境头 + `EXIT=` 的 runner），以及 14 份日志（含 TASK-061 尺子复跑 2 份）：`probe-gate-b0e4cb1-run1.log`、`full-suite-run{1,2}.log`、`targeted-post-fix-run1.log`、`pre/post-q008-truthy-pytest-rerun2.log`（有效）、`pre/postfix-q008-truthy-rerun1.log`（**无效取证，保留**）、`prefix/postfix-r004-latch-rerun1.log`、`prefix-backup-tests-run1.log`、`prefix-collect-count-run1.log`。

临时修前树 `C:/Users/49745/AppData/Local/Temp/t057-prefix`（@`0d15018`）不属于仓库，复核结束后 `git worktree remove`。在 master worktree 递归搜不到上述文件属正常（linked worktree 各有独立工作目录）；落库由 Codex 决定。

## 推荐下一步（可直接转发）

**ZCode：在 `agent/zcode/TASK-057-backup-restore` 上补一个 commit（只动闩的位置 + 用例 + docstring）**

- 工作路径 `G:\CODEX\New Manga.worktrees\TASK-057-zcode`；base `b0e4cb1`
- 必做（R-001/R-004）：`src/ui/viewmodels/workbench/run_controller.py` 的 `start()` 增准入闩（如 `set_restore_latch(bool)` + 置位即拒并给 typed 错误），`viewmodel.py` 的 `beginRestore/endRestore` 改为转调控制器、`_start_run` 里的检查改为依赖控制器判定；`tests/workbench/test_restore_gate.py` 把"every start path"变成**真枚举四面**（`startTranslateAll`/`startTranslateUntranslated` 之外补 `continueRun`(PAUSED)、`retryFailedPages`、`restartRun`），每面断言"无 worker 出生 + 错误面命中"；三处 docstring（`connection.py:238-239`、`run_controller.py:83`、`viewmodel.py:115` + `:718`）同步改为与实现一致
- 必做（R-002）：`restoreGate()` 上下文管理器（`__exit__` 必解除）+ 一条"恢复主体抛异常后闩已解除"的用例
- 建议（R-005/R-006）：Handoff/Task 补 942 的两段差值解释；两支判别探针把翻转做进 EXIT
- 允许：`src/ui/viewmodels/workbench/**`、`src/infrastructure/sqlite/connection.py`（仅 docstring）、`tests/workbench/**`、`tests/core/**`、`doc/tasks/TASK-057.md`、`doc/handoffs/TASK-057-unfreeze.md`、`verification/TASK-057/**`
- 禁止：改 Schema/`requirements.txt`/`src/ui/qml/**`/`AGENTS.md`/其他 Task；不得放宽既有断言或新增 skip/xfail；不 push；**不改 `backup.py` 的既有适配**（裁定已接受，unwrap 留装配切片）
- 待 Codex 追认（R-003）：Task 允许修改范围补 `src/ui/viewmodels/workbench/**` 与 `tests/workbench/**`
- 验证：Reviewer 复跑 `verification/TASK-057/review-b0e4cb1/t057_gate_probe.py`（期望 MODE A.1 / MODE B 四面全部 False）+ `tests/workbench/test_restore_gate.py` + 全仓 ×1
