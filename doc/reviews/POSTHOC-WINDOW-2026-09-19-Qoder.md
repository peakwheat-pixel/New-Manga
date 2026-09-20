---
review: POSTHOC-WINDOW-2026-09-19
reviewer: Qoder（外部非作者；原 DSH 槽位经用户指示改派）
author: ZCode（全权窗口 T0→T1 内的 11 个切片）
window_t0: 51a71f3
reviewed_head: b7b1b7c
closure_head: ed21c8a
decision: uphold_with_findings
per_slice_overturn: [W1/TASK-048]
---

# 窗口 post-hoc 复审（Qoder）：ZCode 全权窗口 2026-09-19

**固定对象**：T0=`51a71f3` → 收口 `ed21c8a`（复审开工时 master 实际头 `b7b1b7c`，其后的 `0bb1e6c..b7b1b7c`
为文档/所有权变更，不影响被审树）；逐切片以交接包表内 `integration_commit` 为准。
**必读依据**：[POSTHOC-REVIEW-BRIEF-2026-09-19.md](../handoffs/POSTHOC-REVIEW-BRIEF-2026-09-19.md)、
[09 协作协议](../09_COLLABORATION.md) §1/§6、
[AGENTS.md](../../AGENTS.md)、[10 现状与差距](../10_CURRENT_STATE_AND_GAPS.md) §11。
**边界遵守**：全程只读——未改 `src/**`、`tests/**`、任何既入档 Review 正文、`doc/10_CURRENT_STATE_AND_GAPS.md`；
未回滚任何 merge；未 push；未改各 Task 状态。Reviewer 自有产物只在
[verification/POSTHOC-WINDOW-2026-09-19/Qoder/](../../verification/POSTHOC-WINDOW-2026-09-19/Qoder/)（本分支，未提交）。

**独立性**：Qoder 未实现窗口内任何切片；W0/TASK-046 我是 Reviewer（非作者）。窗口内 11 个集成的 Review
定性除 W0 外全为 `approved_subagent`（同体审查，按 §1 不构成独立批准），本报告即为该缺口的补位。

## 总结论

**`uphold_with_findings`——但 W1/TASK-048 单独判 `overturn`（推翻其 AC① 判定，不撤回 P0 修复本身）。**

- 10 个切片的**集成事实与生产树健康**维持：无 schema/依赖/QML 越界，无新增 `skip`/`xfail`，既有断言零放宽
  （`git log -p 51a71f3..0bb1e6c -- tests/` 净 `+2320/-7`，7 行删除全部是 TASK-054 的重命名替换），
  全仓 **911 passed / 0 skipped / 911 collected，exit 0**（我在 `b7b1b7c` 干净树上复跑 ×2），
  与交接包"openssl 可用口径 911/0"完全吻合；总数链条 848→851→854→873→878→886→892→895→904→908→911
  逐级增量与新增用例定义数一一对上。
- 推翻 W1 的理由不是"修复无效"——P0 端到端我独立复现了 10/10（下面 A 段）；理由是**其 AC① 自己要求的并发判据
  未被满足，且缺陷在仓库自己的证据里已被记为"flaky"而非缺陷**（`doc/STATUS.md:243`、
  `verification/TASK-056/revision-full-suite-run2.log:67,74`）。补采后主证据 Q-001 定级 **P0**（一次交错即可静默打死
  run 并留下 `running` 行）。按 §6.8「P0/P1 未解决不能批准」，
  W1 的 `done` 不能维持。处置建议：不回滚 `be558ca`，重开一个连接归属切片。

| W | Task | 结论 | 一句话依据 |
|---|---|---|---|
| W0 | TASK-046 | uphold | 外部非作者 Review 已 `approved`；残留 R-001(P2) 未落点、STATUS 引我的 R-004 数字用了草稿口径（Q-013） |
| W1 | TASK-048 | **overturn** | 单连接共享导致跨线程事务互毁：P0 修复本身 10/10 复现，但同一条连接上两线程互相回滚——实测 GUI 提交 ~0.09%/次抛未类型化 `OperationalError`，且 **10 轮 run 中 3 轮被静默打死、库行停留 `running`**；孤儿 Revision 与静默丢写均 10/10、7/7 确定性复现（Q-001 **P0**/Q-002） |
| W2 | TASK-049 | uphold_with_findings | typed fail-closed 真实；但收口只覆盖 `ocr` 链，且生产 `detector=None` ⇒ 落 Region 数仍为 0（Q-004） |
| W3 | TASK-050 | uphold_with_findings | 写面是真解锁；读面 AC① 属既有能力（base 的 `freeze()` 本就每 run 重读），其用例不判别（Q-005） |
| W4 | TASK-051 | uphold | 判别日志仅摘要（P3）；未见功能缺陷 |
| W5 | TASK-052 | uphold_with_findings | 最小 QML 面成立、无泄漏路径；但真正生产异常路径仍未被测试（R-001 勘误自认），3 处硬编码颜色入设计门（Q-011） |
| W6 | TASK-053 | uphold_with_findings | 重试守卫按 manifest 成员判定，两个失败方向都在（Q-007）；provenance 见「未覆盖风险」 |
| W7 | TASK-054 | uphold | 纯重命名，零残留，非数据迁移（`ImportReport` 从不落盘）；判别力声明 N/A 合法 |
| W8 | TASK-055 | uphold_with_findings | docstring 承诺"每个值过脱敏屏"，代码只屏 2/5 段，`recent_errors` 裸传（Q-006）；无任何修前判别日志（Q-009） |
| W9 | TASK-056 | uphold_with_findings | 白名单仅覆盖缓存面；解析后未复核 reparse point；`_is_safe` 与 trash 面不对称（Q-007） |
| W11 | TASK-058 | uphold_with_findings | drain 超时关闭连接的问题已由 TASK-060 的 `1195baf` 修复；其余证据与文档尾项另记（Q-011/Q-009） |
| W10 | TASK-057 | **不建议按现状集成** | `restore_backup` 无活动 run/并发写者门；且存在恒真断言（Q-008） |

## 规格轴（Spec：是否忠实实现来源）

来源顺序＝Task AC → 其引用条文 → STATUS 用户裁决；不用聊天记录推断。标注：
**[复现]**=Reviewer 亲自执行；**[读码]**=Reviewer 亲读代码核对；**[子代理]**=派发核查、Reviewer 未复核到同等深度；**[记录]**=仅有作者/归档 Review 的说法。

- **[推翻] W1 AC ①「方案须解释为何不产生并发写竞争，并给出并发的负向用例或论证」未满足**（复现＋读码）。
  详见 Findings Q-001 与「靶点 1 独立复跑」。作者的 AC① 四层论证的前三层经核对**为真**
  （`sqlite3.threadsafety==3` 实测；`RunController.start` 二次进入 raise（`run_controller.py:74-76`）；
  `_apply_pragmas` 确为 `journal_mode=WAL` + `busy_timeout=5000`，`connection.py:63-67`）；
  **断裂在第四层**——它只论证了"瓦片式全量重放可自愈"的 `pipeline_runs` 方向，
  没有覆盖 GUI 线程显式事务方向，而那才是丢写/孤儿行的来源。
- **[遗漏] W2**：AC①/② 字面达成（`detect` 已注册、无检测器时 typed `PROVIDER_NOT_CONFIGURED`，
  读码 `handlers.py:204-215`、`service.py:713-721`）。但 §11 P-2 记录的**症状**（"页级命令因无 Region 而失败"）
  仅对含 `ocr` 的命令闭合：门控条件是 `if region is None and "ocr" in steps`（`service.py:346`，读码），
  而 `_RERENDER=("render",)`、`_REINPAINT=("segment","mask_refine","inpaint")`（`service.py:93-94`）
  不含 `ocr`，其 handler 仍 `self._require_region(unit)`（`handlers.py:460,507,555,777`）⇒
  页级 `REINPAINT_ALL`/`RERENDER_ALL` 在无 Region 页上报同一条 `INVALID_INPUT`。
  作者注释（`service.py:354-357`）把这称为"region-free chains 不受门控"——是**有意的范围决定**而非疏漏，
  但 STATUS/doc 10 把 P-2 记为已闭环则超出该决定的实际覆盖面（Q-004）。
- **[部分完成] W3 AC①**「读面注入持久化默认值」：base `8bf8da3` 的 `SqliteSnapshotProvider.freeze()`
  **本就每次从 `pipeline_defaults` 重读**（`git show 8bf8da3:src/infrastructure/sqlite/pipeline.py` 第 813-823 行，读码），
  装配期注入不改变任何一次 run 看到的快照；真实增量是 AC② 写面（双树探针 `WRITE_FACE=unavailable→ok` 可信）。
  且 `test_assembly_seeds_run_snapshots_from_persisted_defaults` 不 import 任何新代码 ⇒ 在修前树同样通过，
  与该切片判别日志里"只有 1 个 ERROR、且不是这个文件"相互印证（Q-005）。
- **[夸大] W8**：`diagnostics.py` 的 docstring 与实现矛盾——见 Q-006（读码，逐行核）。
- **[范围蔓延]** 未发现。11 个切片的 per-commit `--stat` 均在各自 允许修改范围 内；
  无 schema/migration、无 `requirements.txt`、无 pipeline seam 本体改动；`src/ui/**` 只有 TASK-052 的
  一个工作台内 `Rectangle`（`WorkbenchView.qml:80-135`，子代理核查＋与 QML 一级页面纪律一致）。
- **靶点 6（W0 定性偏差）**：我的 `approved` 系用户直接改派的外部非作者 Review，效力高于窗口内
  `approved_subagent`，与窗口条款"Qoder 窗口期不参与"的先后关系应由 Codex 一句话裁定入档；
  本报告采 same reading：**外部改派优先**，故 W0 无需重做，但需把这一裁定写进 STATUS，避免后续 Qoder Review 被质疑（Q-013）。

## 标准轴（Standards：是否符合仓库已记录标准 + smell 判断）

**硬性项（引用条款）**：
1. [复现] **口径纪律**——交接包与多数 Task 要求"同一 shell + 同一 venv、退出码与 passed/skipped 分列、
   不设 `QT_QPA_PLATFORM`"。实测证据面：`verification/TASK-048|049|050|051|052|054|058` 的
   `full-suite-*.log` **一律没有 EXIT 行**（2 行尾巴，无 shell/venv 头），而 Handoff/Task 却写"exit 0 ×5"；
   `verification/TASK-053|055|056` 的日志首行自证 `shell: git-bash`，与
   `verification/ZCODE-WINDOW-2026-09-19/window-report.md:58`「全程 PowerShell」直接冲突。
   → 结论**不可由 artefact 复核**（Q-009）。我自己按合规口径跑的 911/0 ×2 见 `full-suite-run{1,2}.log`。
2. [读码] **"聊天记录不是项目事实来源"**——`H/TASK-053-delivery.md:34`、`H/TASK-055-7f13e53.md:33`
   以"会话记录"充当相邻套件证据；`TASK-053/055` 的守卫移除必失败结论只有散文（Q-009）。
3. [读码] **不得放宽/删除既有断言**：TASK-057 分支含一条恒真断言
   `assert not (… / "user-side").exists() or True`（`git show 50c4b1a:tests/storage/test_backup_restore.py:116`），
   它是 AC③"永不写用户目录"的唯一断言支撑——形式存在、内容无效（Q-008，未集成故不入台账）。
4. [读码] **fail-closed / 可诊断失败纪律**被 W1 打破：`regions.py:210` 的 `BEGIN IMMEDIATE` 在 `try` 之外，
   并发下抛**裸** `sqlite3.OperationalError`，不经 typed 通道（Q-002，实测）。

**Smell 判断（非硬违规）**：
- `possible Duplicated Code`：`app.py:392-433`（`_load_pipeline_defaults`）与 `app.py:435-449`
  （`_load_pipeline_settings`）两套并行的 provider_runtime 读取（[子代理]，与 Task 风险注记"须复用既有形状"相悖）。
- `possible Dark Contract`：`app.py:698` `save=lambda **kwargs: SqlitePipelineStore(conn, **kwargs)`
  把"构造"与"写库"绑在一起且无类型契约（[子代理]）。
- `possible Feature Envy / 不对称防御`：`cleanup.py:184-195` `_is_safe` 只护缓存面，
  trash/purge 走 `remove_managed` 的根包含检查（`managed_storage.py:116-131`），同一"永不清理"边界两套实现（Q-007）。

## Architecture 轴

分层与依赖方向未被窗口破坏（UI→Application→Domain/Ports→Infrastructure 单向；QML 不触库/文件；
无新依赖；凭证边界仍走 `_redact`）。窗口暴露的是**架构级不变式缺失**：TASK-048 选"一个共享连接"，
但没有配套的**单写者/事务归属契约**——`SqlitePipelineStore`、`SqliteTargetCatalog.commit_step`、
`SqliteRegionRepository`、`SqliteLibraryRepository` 各自在自己的对象上开/交/回滚**同一个连接的事务**，
`with self._conn:`（`pipeline.py:398`、`library.py:109`）与 `BEGIN IMMEDIATE`（`pipeline.py:578`、
`regions.py:210`、`step_writes.py:207,358,435`）互不知情。TASK-058 的退出 drain（Q-003）与
TASK-057 的 restore（Q-008）都在同一条不变式之上，应合并为一次收口：
**每线程独立连接，或显式串行化 + typed 错误 + 事务归属单点**。

## Verification 轴

### 靶点 1：W1 TASK-048 独立复跑（本报告的主证据）

探针 [w1_thread_collision_probe.py](../../verification/POSTHOC-WINDOW-2026-09-19/Qoder/w1_thread_collision_probe.py)
×10 次（日志 `w1-thread-collision-run{1..10}.log`：run1-4 初采，run5-10 为同一脚本的补采、
增加了"打印 run 崩溃文本"一行），真实 `assemble_services` + 真实 SQLite +
真实 `RunController`(QThread) + 完整 `TRANSLATE_ALL`：

| 段 | 测量 | 结果 |
|---|---|---|
| A | P0 复现（uphold 检查） | **10/10 轮**段 A `crashed=0 finished=['completed_with_failures']`，独立连接回读 `db_status=completed_with_failures` ⇒ **P0 修复为真**；`sqlite3.threadsafety=3` 前提为真 |
| B | 真实 run 执行期间，GUI 线程连续真实 Region 提交（20s/轮） | ①GUI 侧：10 轮 `attempts` 合计 17527，`raised` 合计 15（每轮 0/1/2/3 不等），全部为**裸** `sqlite3.OperationalError: cannot start a transaction within a transaction` ⇒ 生产可达率 ≈0.09%/次保存。②**worker 侧更糟**：10 轮中 **3 轮 run 被打死**（run4/7/8）：`crashed=1 finished=[] db_status=running`，即 AC③ 声称已消除的"run 停留 `running`"从共享事务回滚这条路径复现。崩溃文本（run5-10 补采才打印）：run7 `cannot commit - no transaction is active`（GUI 的 `rollback()` 吃掉 worker 未提交的事务）、run8 `cannot start a transaction within a transaction`（GUI 的 BEGIN 落在 worker 事务内，`pipeline.py:578` 自身 `BEGIN IMMEDIATE` 失败）。③run7/run8 的 GUI `raised=0`⇒**用户侧零报错、run 静默死亡**，与 §11 P-1 修复前的"静默"体验同型 |
| C | 对照：同一 GUI 循环、无 worker | 10 轮 `attempts 1213–1255`，`raised=0`（逐轮均 0）⇒ 异常只归因于共享连接并发 |
| D1 | 强制调度：worker 持 `with conn:`（`pipeline.py:398` 形状），GUI 调 `commit_region_revision` | `OperationalError`（`regions.py:210` 在 `try` 之外 ⇒ 不经 typed 通道，直达 VM） |
| D2 | GUI 事务进行中被对端 `with conn:` 提交，随后 GUI `rollback()`（`regions.py:272-275`） | **孤儿 revision 行=1**，10/10 轮全部命中（确定性，非时序运气）；若"rolling back entirely"（`regions.py:7`）成立应为 0 ⇒ 不可变历史被写入半途 Revision |
| D3 | GUI 在 `with conn:` 内写 `books`，worker 错误路径 `self._conn.rollback()`（`pipeline.py:621-622`） | 写者**返回成功**、落盘行数 **0**（该段自 run4 起存在于脚本，run4-10 共 7/7 命中）⇒ 静默丢用户写；这正是 `verification/TASK-056/revision-full-suite-run2.log:67,74` 里 `test_run_thread_e2e.py:177 assert book_rows >= 1 + len(created)` 失败的机理，也解释其为何"单跑恒过、全仓偶发" |
| E | 完整性回读 | `integrity_check=ok`、`foreign_key_check` 0 行、指针无悬空/无错指、状态与当前 revision 一致（含 run4/7/8 三个崩溃轮）⇒ **非破坏性**：丢的是"这一次编辑"或"这一次 run"，不是库 |

作者的并发负向用例（`test_worker_run_and_main_thread_access_coexist`）之所以拦不住这一切：它的 GUI 流是
`create_book` 单语句 `with conn:`，**从不走显式 `BEGIN IMMEDIATE` 路径**，也不校验"返回成功⇒落盘"。
其归档 Review 已把该用例的时序强度记为 R-2 P3——问题在**共享事务归属**被记成了测试强度问题。

### 独立复跑 vs 复用窗口内证据（交接包要求分列）

**Reviewer 独立复跑**：全仓 ×2 @`b7b1b7c`（911 passed/0 skipped/911 collected/EXIT 0，
`full-suite-run{1,2}.log`）；W1 探针 ×10（上表）；TASK-058 drain/close 与 TASK-055 脱敏屏与
W2 门控范围与 W3 `freeze` 历史——**逐行读码核对**（引用处即证据）；总数链条与各切片证据文件清单——逐项目录核对。
**复用窗口内证据（未复跑）**：W2–W11 各自的修前判别日志、定向计数、双树探针输出、
`verification/TASK-053|055|056` 的 git-bash 运行、`flaky-diagnostic.log` 的单跑 ×6；
W6/W9 的清理面代码路径细节（`trash.py:216-249`、`cleanup.py:134-153`、`tile_cache_sweep.py:31-38`、
`managed_storage.py:116-131`）由派发核查支撑，**Reviewer 未独立复跑到同等深度**（见「未覆盖风险」）。
**未复跑**：真机 UI、真实 provider 端到端、W4/W5/W7 的定向套件（仅核对其日志文本）。

## Findings

| ID | 级别 | 切片 / 文件:行 | 触发与影响 | 复现证据 | 建议 | 处置 |
|---|---|---|---|---|---|---|
| Q-001 | **P0**（初判 P1，补采后上调，见自检） | W1 `src/infrastructure/sqlite/connection.py:90` + `regions.py:210` + `pipeline.py:398,621-622` + `library.py:109` | 单连接跨线程共享后，两线程各自 commit/rollback 同一事务：实测 ①GUI 保存 15/17527（≈0.09%）抛裸 `OperationalError`（编辑失败）；②D2 半途 Revision 被对端提交⇒不可变历史出现孤儿行；③D3 GUI 写返回成功但落盘 0 行⇒**静默丢失用户编辑**；④B 段 10 轮中 3 轮 worker run 被同一次交错打死且行停留 `running`（run7/8 崩溃时 GUI 侧 `raised=0`⇒**全程零报错的静默失败**）——AC② "不再出现跨线程异常"与 AC③ "run 不再停留 `running`" 在共享连接路径上均不成立。升 P0 的理由：一次交错即致命，故命中概率随 run 时长与编辑频次单调上升（20s 窗口已 3/10），生产上分钟级 `TRANSLATE_ALL` + 人工编辑≈必然；这正是 §11 P-1 立案的 P0 类目。仓库自身证据 `verification/TASK-056/revision-full-suite-run2.log:67,74`（`test_run_thread_e2e.py:177` 失败）即 ③ 的自然命中，却被 `doc/STATUS.md:243` 记为"时序浮动/flaky（open，TASK-048 面）" | [复现] `w1-thread-collision-run{1..10}.log`：B/C/D1/D2/E 全 10 轮，D3 自 run4 起 7 轮；run5-10 附 run 崩溃文本 | 重开切片：每线程独立连接（或 thread-local）+ 单一写者串行化；把 `BEGIN IMMEDIATE` 收进 typed 失败通道；用"写者返回成功⇒独立连接可读回该行"作 AC；同时撤销 flaky 定性 | **open → 建议推翻 W1 的 `done`（不回滚 merge）** |
| Q-002 | P2 | W1 `src/infrastructure/sqlite/regions.py:210`（对照 `:272-275` 的 `except: rollback()`） | `BEGIN IMMEDIATE` 位于 `try` 之外⇒并发时 sqlite 原生异常穿透 `RegionEditingService` 到 VM/QML，违反项目"typed、可诊断、不静默"纪律；且失败发生在任何写入之前⇒D1 路径本身不损坏数据（与 Q-001 的 ②③ 区分） | [复现] 探针 D1；[读码] 行号 | 与 Q-001 同切片修：`BEGIN` 入 try + 映射为 typed `DB_FAILED`/可诊断码 | open |
| Q-003 | P2 | W11 `src/ui/viewmodels/workbench/run_controller.py:104-109` + `src/bootstrap/app.py:909-910` | `wait(5000)` 超时后 `shutdown()` **早退**（线程仍活、`_active_run` 保留、`_thread` 未清），而 `_shutdown_services` 无条件 `services.conn.close()`⇒在 worker 仍在写同一连接时关闭连接；`app.py:904-905` docstring 自称"drain 必须在 close 前完成"，与代码矛盾；全程无日志无提示 | [读码] 两文件行号；5s 是墙钟预算而非边界（`thread.quit()` 不能打断 `_Worker.execute`）；TASK-060 真装配复验见 `1195baf` | 超时后不得 close 的生产缺陷已由 TASK-060 修复；后续诊断记录另由 F-007 跟进 | **closed@`1195baf`（TASK-060）** |
| Q-004 | P2 | W2 `src/application/tasks/service.py:346,93-94`；`handlers.py:460,507,555,777`；`bootstrap/app.py`（`detector=None`，`e94d5af` 注释 541-547） | §11 P-2 的收口**只对含 `ocr` 的命令成立**；页级 `REINPAINT_ALL`/`RERENDER_ALL` 在无 Region 页上仍报 `INVALID_INPUT "requires a Region target"`；且生产无检测器⇒"检测→落 Region"实际产出恒为 0（作者已在代码注释声明） | [读码]＋[记录]（`region-post-fix-run1.txt:2-3` `detect->failed PROVIDER_NOT_CONFIGURED`） | 在 doc 10 / STATUS 把 P-2 改写为"**接缝已闭、生产仍惰性**（无检测器、无 UI 调用者）"，并把两条 region-free 链列入缺口；不改代码不算缺陷 | open（记录更正） |
| Q-005 | P2 | W3 AC①；`tests/core/test_pipeline_defaults_assembly.py:68-107`；`discriminating-new-tests-vs-prefix.log` | 读面注入并非新增能力：base `8bf8da3` 的 `freeze()` 已每 run 重读 `pipeline_defaults`（第 813-823 行）；该用例不 import 任何新代码⇒在修前树同样通过；AC① 却按"已达成"勾选 | [读码] 双树 `git show` 对照；[记录] 判别日志仅 1 个 ERROR | AC① 措辞改为"沿用既有每-run 重读"，实得收益记在 AC②；或补一条真正判别的断言 | open |
| Q-006 | P2 | W8 `src/application/maintenance/diagnostics.py:75`（+`:113-115` 声明）对 `:117,124,129,133` 与 `:119-122` | docstring 承诺"每个值入报前过脱敏屏"，实现只对 `settings_summary`、`environment_paths` 调 `redact_value`；`app_version/platform_python/database_path` 与 `recent_errors.message` 裸传，且合成键 `"{occurred_at} {source}"` 结构上不可能命中 `_SENSITIVE_KEY`；测试用良性 `"a.png"` 掩盖（`tests/diagnostics/test_report.py:159`） | [读码] 逐行对照 | 要么把 `recent_errors` 也过屏（并补一条含路径/令牌子串的用例），要么删掉该不变式措辞；诊断包会外发，宜按隐私面处理 | open |
| Q-007 | P2 | W9/W6 `cleanup.py:134-153,180-195`、`tile_cache_sweep.py:31-38`、`managed_storage.py:116-131`、`trash.py:216-249,314-318` | 清理面三处不对称/开环：①`_is_safe` 只护缓存面，trash/purge 仅"解析后落在根内"，故任何被篡改的 `managed_path` 可删同根其他页的受保护原件；②缓存清扫不复核解析后的 reparse point（可指向根内 pinned/current revision 文件）；③重试守卫按 **manifest 成员** 而非**行存活**判定⇒既可能"永远跳过本该重试的批次"，也可能对 `rebuilt:*` 批次 fail-open；④`retry_pending_cleanups` 不重过 `_is_safe`；⑤`_record_pending([])` 会整键弹出⇒瞬时空清单丢弃重试列表 | [子代理] 读码；Reviewer 未独立复跑（见「未覆盖风险」） | 单一"永不清理"谓词（解析后前缀 + 行存活 + 每面复用）；补一条守卫移除即失败的判别日志（当前只有散文，见 Q-009） | open（交 Codex 分派；建议与 Q-001/Q-003 并一次"写路径与破坏面收口"切片） |
| Q-008 | P1（阻断集成，非台账缺陷） | W10 `src/infrastructure/sqlite/backup.py:107-184`、`tests/storage/test_backup_restore.py:116` | 未集成分支：`restore_backup` 以 SQLite backup API **整库覆盖**活库，却无活动 run / 并发写者 / 打开 trash 的任何前置检查（同一作者对更弱的 `purge_targetless_runs` 写了 `_ACTIVE_STATUSES=("running","paused")` 守卫，`pipeline.py:856-878`）⇒在 TASK-048 的活线程模型上会摧毁任务可恢复性与备份点之后的人工修改；AC③ 唯一断言为恒真 `… or True`；AC⑤ 计数自相矛盾（表列 run1/2/3/6/7 而 run4/5 也是 912/0，却记"有效绿 4 次"）；AC⑥ 无 Review | [复现] `git show 50c4b1a` 两处文本；[子代理] 其余 | **维持冻结**；集成前需：活动写者门（或显式先 drain/关闭）、删除恒真断言并补真实边界断言、归档一份修前判别日志 | open |
| Q-009 | P2（系统性·证据纪律） | `verification/TASK-048/049/050/051/052/054/058/full-suite-*.log`；`window-report.md:58`；`H/TASK-053-delivery.md:34`、`H/TASK-055-7f13e53.md:33`、`H/TASK-056-delivery.md` | ①多数全仓日志只有 2 行尾巴且**无 EXIT**，却声称"exit 0 ×5"⇒不可复核；②"全程 PowerShell"与日志自证 `shell: git-bash` 冲突；③W6/W9 的"守卫移除必失败"只有散文、W8 **完全没有**修前判别件（仅 N passed）；③W3 "定向 273" 无 artefact（只有复核 `review-rerun-core.log` 的 30 passed）；④以"会话记录"充当证据，与 AGENTS.md 首条相悖 | [复现] 目录与文本逐份核对（另见 Reviewer `full-suite-run{1,2}.log` 为合规样本：含 COLLECTED/EXIT） | 重采 W1–W5、W11 的逐次日志（带 EXIT 与 shell/venv 头）；W6/W9 补真实判别件；把"artefact 缺失即记 NOT_RUN，不得以散文或 `N passed` 代判别"写进窗口章程 | open |
| Q-010 | P3 | `doc/STATUS.md:243` flaky 台账 | 把 Q-001 的确定性机理记为"并发用例时序浮动、单跑 ×6 全过"⇒方向反了：单跑过是因为调度窗口不出现 | [复现] D3 确定性复现 | 该条改指向 Q-001，勿再以 flaky 结案 | open |
| Q-011 | P3 | W5/W7/W8/W11 文档与 QML 细节 | `WorkbenchView.qml:57,80-135` 3 处硬编码颜色绕过 token 系统（喂给 TASK-047/059 设计门）；`TASK-054.md`/`TASK-055.md` 的 AC 勾选框在 `status: done` 下仍为 `[ ]`；`TASK-058.md` 仍引 `src/workbench/run_controller.py:96`（真实路径 `src/ui/viewmodels/workbench/run_controller.py`），此前“已更正”的记账在此撤回；`56a429e`/`7f13e53` 各把误名空文件提交进实现提交（后一提交删除） | [读码]/[子代理] | 随后续 docs+tests 小切片清理 | open（不阻断） |
| Q-012 | Info | 本报告自身 | 窗口条款"Qoder 窗口期不参与"与用户逐次改派的关系（与我在 TASK-046 Review 登记的 R-005 同源），需 Codex 一句裁定入档 | [读码] `51a71f3` AGENTS.md 临时条款 | 裁定"外部非作者 Review 优先于窗口排除条款" | open |

## 做得对的地方（不无依据地夸）

- W1 的端到端资产是**真的**：三条用例在修前树 3 failed 且失败文本就是跨线程异常本身
  （`discriminating-new-tests-vs-prefix.log`），无"仅钉既有行为"充数——这也是本报告能推翻它的的前提。
- 总数链条 848→911 逐级与新增用例定义数吻合，无 skip/xfail、无断言删除（仅 7 行重命名替换）；
  我在 `b7b1b7c` 复跑 911/0 ×2 与该链条一致。
- W6/W8/W9/W11 都在首轮被自家子对话判出 P1/P2 并**当轮返修**（`16340b5`、`c175657`、`15f977a`、`ebfc87a`），
  窗口内自查在多数切片上确实起了作用。
- W2/W3 的双树探针用真实 `assemble_services`，没有自造替身装配。

## 未覆盖风险（明确说没做到的）

1. **W6/W9/W10 的清理面细节**（Q-007、Q-008 的可达性）由派发核查支撑，我未独立写探针验证
   "`tile-x.png` 符号链接指向根内 revision 文件"与"篡改 `managed_path` 经 `remove_managed` 删除他人原件"两条路径；
   在集成前应由作者或 Codex 各跑一条判别用例，我不为未验证的部分背书。
2. **未复现 W2–W11 的任何全仓/定向运行**，其计数与 skip 列表为 artefact 读数＋我的文本核对，非我的执行。
3. 真机 QML 观感、`--screenshot` 栅格、真实超大商业页：仍如各 Task 声明未验证。
4. 两组数字口径不同，都不能直接搬到生产：GUI 侧 0.09% 是**每次保存**的命中率（只与本机的写入密度和调度相关，
   与真实用户的保存频率无直接换算关系）；worker 侧 3/10 是**20s 窗口**一轮的经验值，真实 `TRANSLATE_ALL`
   是分钟级、交错随时长累积 ⇒ "一次 run 内至少命中一次"的概率高于 3/10，而首版报告把这一面完全漏掉了。
   结论不依赖这些概率：该路径**没有任何互斥**，而后果（静默丢写、静默打死 run、孤儿 Revision）
   由 D2 10/10、D3 7/7、④ 3/10 的确定性/可重复命中支撑。

## 结论与处置

**总结论 `uphold_with_findings`，W1/TASK-048 单片 `overturn`。**

- 维持：W0、W2、W3、W4、W5、W6、W7、W8、W9、W11 的 `done`（各带上述 P2/P3 待处置项）。
- 推翻：W1/TASK-048——推翻的是"AC① 并发判据已满足"与 `approved_subagent` 的批准效力，
  **不是 P0 修复本身**；按边界"不回滚任何 merge、不删除已入档历史"，处置应为重开一个连接归属/事务归属切片
  （Q-001＋Q-002，顺带吸收 Q-003 与 Q-007 的"单一边界谓词"部分），并把 `doc/STATUS.md:243` 的 flaky 定性撤回（Q-010）。
- 维持冻结：W10/TASK-057 不得按现状集成（Q-008 三项前置）。
- 流程：Q-009 的证据纪律应写进窗口章程（下一窗口开工前），否则"×5 逐次"仍是不可复核的自述。

本报告只固定于 `reviewed_head=b7b1b7c`；此后 master 变化不延用本结论。

## 证据位置与落库状态（复核者必读）

本报告与其全部证据目前**只在 Qoder 的 Review worktree 的工作目录里，未提交、未 push**：

- 目录：`G:/CODEX/New Manga.worktrees/POSTHOC-WINDOW-2026-09-19-qoder`（分支 `agent/qoder/POSTHOC-WINDOW-2026-09-19`，base `b7b1b7c`）
- 报告：`doc/reviews/POSTHOC-WINDOW-2026-09-19-Qoder.md`
- 证据：`verification/POSTHOC-WINDOW-2026-09-19/Qoder/**`（`run_suite.ps1`、`w1_thread_collision_probe.py`、`full-suite-run{1,2}.log`、`w1-thread-collision-run*.log`）

`git status --short` 在 master worktree（`G:/CODEX/New Manga`）看不到它们：linked worktree 各有独立工作目录，
且这些文件从未进入任何 commit（`git ls-files verification/POSTHOC-WINDOW-2026-09-19/` 在两处都为空）。
**在他人分支上自行 commit 不属于 Reviewer 权限**，故落库由 Codex/ZCode 决定；本报告按 Q-009 的口径要求，
把"证据存在"与"证据已入库"分列，不以后者的缺失推翻前者的结论。

## 推荐下一步（可直接转发）

**Codex：据本报告重开"SQLite 连接与事务归属收口"切片**（这是唯一能同时了结 Q-001/Q-002/Q-003/Q-007 不对称防御的入口）。

- 固定对象：被审窗口 `51a71f3..b7b1b7c`；W1 integration `be558ca`；主证据 `verification/POSTHOC-WINDOW-2026-09-19/Qoder/w1-thread-collision-run{1..10}.log`（绝对位置见上节）
- 建议范围：`src/infrastructure/sqlite/**`（每线程连接或单写者串行化）、`src/application/tasks/**`、
  `src/ui/viewmodels/workbench/run_controller.py`（drain 超时不 close）、`src/infrastructure/filesystem/managed_storage.py`
  与 `src/application/maintenance/cleanup.py`（单一"永不清理"谓词）、`tests/storage/**`、`tests/workbench/**`；
  禁：Schema/migration、依赖清单、`src/ui/**` QML、`AGENTS.md`
- 交付物：代码＋测试＋**判别件**（AC 必须含"写者返回成功⇒独立连接可读回该行""两线程交错下无孤儿 Revision"
  "GUI 连续真实提交期间跑完整 run：`runCrashed` 次数为 0 且库行不停留 `running`"），
  运行日志带 EXIT 与 shell/venv 头
- 验证：全仓 `911 passed / 0 skipped / exit 0` 基线不得退化（口径同 `full-suite-run1.log`）；撤回 `doc/STATUS.md:243` 的 flaky 条目并改记 Q-001
- 若 Codex 选择维持 `approved_subagent` 的原判定（不重开），至少须先落 Q-009 的重采与 Q-004/Q-005 的记录更正，否则台账与实态继续背离。

## 本报告自身的自检（2026-09-19 补采后追加）

首版交付后据实记录四处缺陷，均已修正；其中第 1 项会改变定级，故单独列出：

1. **漏报主症状**：首版 B 段只写了"GUI 保存 ~0.1% 抛 `OperationalError`"，把 run4 已出现的
   `crashed=1 / db_status=running` 留在日志里未成文。原因是探针脚本当时只打印崩溃**计数**不打印**文本**，
   我未追问。补采 run5-10（脚本仅增加一行崩溃文本打印）后为 10 轮 3 次，并取得
   `cannot commit - no transaction is active`（run7）与 `cannot start a transaction within a transaction`（run8）
   两条机理文本，且这两轮 GUI 侧 `raised=0`。据此 Q-001 由 P1 **上调为 P0**，W1 的 overturn 依据从
   "AC① 判据未满足"扩到"AC②/AC③ 的既有勾选也不成立"。
2. **两处相对链接失效**：指向 `verification/POSTHOC-WINDOW-2026-09-19/Qoder/` 的 Markdown 链接少了一级 `../`。
   上一轮我自称"链接逐条核对通过"，实际是按仓库根拼路径核的，没有从 `doc/reviews/` 相对解析——核对方法本身错了。
3. **证据未落库**：交接包要求"日志入库"，首版只做到"日志在盘且未 commit"。这直接造成本次争议
   （在 master worktree 递归搜索找不到 `w1-thread-collision-run*.log`）。已补「证据位置与落库状态」一节，
   明确区分"证据存在"与"证据已入库"，并把落库决定权交回 Codex/ZCode。
4. **计数口径含脚本演进**：D3 段自 run4 起才存在，首版"B/C/D1/D2/D3/E 全表 ×4"的写法会让人以为 4 轮都有 D3。
   现按段分列（B/C/D1/D2/E 全 10 轮；D3 为 run4-10 的 7 轮）。
