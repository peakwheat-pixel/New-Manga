---
document_id: FEA-00A-IMPL-scope-r2
kind: independent_scope_review
reviewer: fea00a-scope-reviewer
reviewer_kind: subagent
reviewer_source: "DSH Agent Teams durable teammate `fea00a-scope-reviewer`（role=teammate，context=fresh，第二轮沿用同一独立席位；子任务标识形式 = teammate target 名 + 本报告 frontmatter `document_id`；未使用独立 CLI session ID；未参与该 Task 的起草/实现/返修）"
reviewer_independent: true
reviewed_by_implementer: false
author: dsh-lead
base_commit: 98fbccdf5
reviewed_head: 98fbccdf5
reviewed_head_full: 98fbccdf5646c5095bddaf6439415b5193f80af4
repository: G:/CODEX/New Manga
scope: "FEA-00A-IMPL-1 范围冻结 v2（r1 P1×3/P2×10 的处置核验、v2 新引入问题、指针一致性）；不构成实现验收（实现尚未开始）"
decision: changes_requested
verdict: changes_requested
p0_count: 0
p1_count: 2
p2_count: 7
supersedes: FEA-00A-IMPL-scope-r1
checkps1: "默认（当前 Task doc/tasks/FEA-00A-IMPL-1.md）：PASS (2 warnings)，EXIT=0"
verifypins: "PIN AUDIT: PASS (all 15)，EXIT=0"
captured_at: 2026-11-01T21:40:22+08:00
captured_by: fea00a-scope-reviewer
---

# Review：FEA-00A-IMPL-1 范围冻结 v2（base/reviewed_head = `98fbccdf5`）

**结论：`changes_requested`（P0 × 0 / P1 × 2 / P2 × 7）。**

- r1 的 **P1-3 已真正解决**；**P1-1、P1-2 只解决了主要部分，仍各留一个可导致 AC 不可通过的设计缺口**（详见 r2-P1-1 / r2-P1-2）。
- r1 的 **10 条 P2 已逐项落实**（对账表与正文一致），但 v2 新引入若干精度/一致性问题（7 条 P2）。
- 本次仍只复核**范围冻结**：不评价实现（实现未开始），`approved` 也不等于 Task 完成；实现后仍需独立实现复核、AC 证据、集成与 closeout。

## 0. 复核对象、方法与环境

**被审**：`98fbccdf5`（父 `419f891c0`）。该提交只改 4 个文件（`git show --numstat`）：`doc/tasks/FEA-00A-IMPL-1.md`（+107/−51）、`doc/REBASELINE_PLAN.md`（+1/−1）、`doc/STATUS.md`（+1/−1）、`doc/reviews/FEA-00A-IMPL-scope-r1.md`（+202/−0，即上一轮报告入库）。

**环境与辅助证据（只读）**

- `git rev-parse HEAD` = `98fbccdf5646c5095bddaf6439415b5193f80af4`；工作区 clean（`git status --short --branch` 仅 `## main`）；复核期间未 checkout、未改任何被审文件、未 commit、未 push，只新增本报告。
- `git diff --stat 419f891c0 98fbccdf5 -- src tests apps` **为空** → v2 未改源码/测试；本报告引用的源码行号在 `419f891c0` 与 HEAD 均有效。
- `pwsh -NoProfile -File tools/governance/check.ps1` → `Governance check: PASS (2 warnings)`，EXIT=0（当前 Task 即本卡；warnings = 11 个非终态 Task + STATUS 达预算 80%）。
- `pwsh -NoProfile -File tools/governance/verify_pins.ps1` → `PIN AUDIT: PASS (all 15)`，EXIT=0。
- 已提交的 r1 报告内容与本席位 r1 输出一致（`git show 98fbccdf5:doc/reviews/FEA-00A-IMPL-scope-r1.md` 抽查头部与结论一致；r1 自本报告起降为 `HISTORICAL`，按协议不回溯改写）。

**依据**：v2 卡（`doc/tasks/FEA-00A-IMPL-1.md`）、ADJ U-13（`doc/reviews/ADJ-2026-11-01-FEA-DECISIONS.md:56–65`）、评估（`doc/plan/FEA-00A_PREP.md`）、方案 §15.5（`:905`–`:910`）/§15.6（`:912`–`:919`，尤其 `:914` 的「下表路径…不是实际写权」）、协作协议 §3/§4/§6；源码现状（`step_writes.py`、`handlers.py`、`pipeline.py`、`service.py`、`store.py`、`schema.py`、`connection.py`、`managed_storage.py`、`src/ports/repositories/storage.py`、`src/infrastructure/pipeline/assembly.py`、`src/bootstrap/core_assembly.py`）。

## 1. r1 的 3 条 P1 是否真正解决

### 1.1 P1-1（候选承载 vs Run 全量重写级联）→ **部分解决，仍有 P1**

**已做对的部分**：

- v2 新增 `R-CAND-1…4`（卡 `:69`–`:72`）：唯一真相（`prepared` 行为 prepare 阶段唯一持久真相，`run.candidates` 只表诊断候选）、`_write_run` 在 `DELETE` 前读取并在重建后原样回插、状态机 `prepared→resolved/abandoned`（`resolved_at` 非空、不硬删）、run 启动/`recover_running_runs` 清扫。方向与 r1 建议一致，且 AC2/AC3/AC5 已改写为状态机与四条路径断言（卡 `:101`、`:102`、`:104`）。
- 我核对了该方案在现有实现上的**可行性主干**：`run.step_runs` 经 `run_json` 往返（`pipeline.py:344`/`:372`），`_write_run` 重建时先插 `step_runs`（`:490–503`）再插 `run.candidates`（`:516–528`），所以把 `prepared` 行「先读、后回插」在 FK 上成立；读取与回插需在同一事务内（`write_in_current_transaction` 要求已开启事务，`pipeline.py:410–414`；`put_many` 自开事务 `:416–427`），也成立。**R-CAND-2 的机制本身可行。**

**未解决的部分（r2-P1-1）**：R-CAND-2 的读取过滤条件是 `status='prepared'`（卡 `:70`），而 R-CAND-3 要求「任何路径不得删除 prepared 行；硬删只允许 `library.purge`」（卡 `:71`）。一旦候选被置为 `resolved`/`abandoned`，它就不再满足过滤条件，而 `_write_run` 每次都会：

1. `DELETE FROM pipeline_runs WHERE run_id = ?`（`pipeline.py:433`）→ `step_result_candidates` 受 `ON DELETE CASCADE`（`schema.py:381–382`、`:523–524`；`connection.py:319` `foreign_keys=ON`）被清空；
2. 只回插 `run.candidates`（`pipeline.py:516–528`）与「读取时仍为 `prepared`」的行。

因此**已转换的候选行会在下一次 `_write_run` 被删除**：

- **成功路径**：seam 把候选置 `resolved` 后，`execute_run` 的收尾 `_aggregate_run` + `_persist`（`service.py:977–978`）会再跑一次 `_write_run` → resolved 行被删；若后续还有 unit，`_record_step_attempt` 的 `_persist`（`service.py:723–727`）同样会删。AC3 的「候选 resolved 同事务提交」在事务内成立，但 V7 的持久断言与 AC2 的状态机查询在运行结束后将查不到 resolved 行。
- **失败路径**：`commit_step_result` 的冲突分支先 `_persist`（`service.py:785`），随后 `execute_run` 收尾再 `_persist`（`:977–978`）；无论 `abandoned` 标记放在这次 `_persist` 之前还是之后，下一次 `_write_run` 都会把它删掉（前置→本次 persist 删；后置→收尾 persist 删）。V1/V2「prepared 行存续」与 V5「候选置 `abandoned` 可诊断」（卡 `:125`、`:129`）在 run 结束后不能成立。
- **清扫路径**：R-CAND-4 把 `prepared` 置 `abandoned` 后，后续 `_persist` 同样会删；AC5「清扫后为 `abandoned` 且计数可核」（卡 `:104`）只能在两次持久化之间的窗口核验，不可稳定复现。

→ 因此 **AC2（状态机与四条路径断言）与 AC3/V7、V1/V2/V5 的持久断言按 v2 文本仍不可通过**。r1-P1-1 的根因（候选行生命周期 vs `_write_run` 级联）只解决了「尚未转换的 prepared 行」，没有解决「已转换行」。修复建议：把 R-CAND-2 的保留范围改为「`run_id` 下所有不在 `run.candidates` 中的候选行（或明确 `prepared ∪ resolved ∪ abandoned`），按 `candidate_id` 去重回插」，并同步 AC2/AC3/AC5 与 V1/V2/V5/V7 的断言；R-CAND-3 的「不得硬删」随之由该规则真正实现。

### 1.2 P1-2（artifact 文件 staging 无闭环）→ **部分解决，仍有 P1**

**已做对的部分**：

- v2 新增 `R-ART-1…4`（卡 `:78`–`:81`）：prepare 只 `write_temp`、staging 信息入候选 payload、seam 先 publish 后 DB、失败补偿与清扫、写域扩到 `src/infrastructure/pipeline/assembly.py`/`src/bootstrap/core_assembly.py`/`src/ports/repositories/storage.py`（仅接线）。AC6 已绑定 V9（卡 `:105`），AC4/AC7① 的禁写清单已扩到 `INSERT media_artifacts`/`INSERT artifact_revisions`/`storage.publish`（卡 `:103`、`:106`），并明确 `_artifact_id` 的 INSERT 延后到 seam。方向与 r1 建议一致。
- 写域已覆盖 R-ART-4 所需接线点（`allowed_paths` 卡 `:30`–`:32`），协议主干（temp → 校验 → publish → DB）在现有 `ManagedFileStorage`（`write_temp` `:98–105`、`verify_temp` `:112–113`、`publish` `:115–124`、`discard_temp` `:107–110`、`remove_managed` `:126+`）上可实现。

**未解决的部分（r2-P1-2）**：R-ART-2 规定「**先** `storage.publish` → **再** `BEGIN IMMEDIATE` 做 DB（插行、CAS、候选 resolved）」（卡 `:79`），而 R-ART-3 的补偿只覆盖「**DB 事务失败** → `remove_managed` 补偿」，对「seam 拒绝/暂停/取消」只要求 `discard_temp` 并置 `abandoned`（卡 `:80`）。这会产生**无法回收的最终文件**：

- `publish` 的真实语义是 `os.replace(temp, final)`（`managed_storage.py:115–124`）：一旦执行，temp 已不存在，后续 `discard_temp` 是空操作（`:107–110`）。
- 拒绝类结果（`input_revision_changed`、`lock_changed`、`STALE_RUN_SNAPSHOT`）在现有结构中都是**返回状态而非抛异常**（`pipeline.py:755–760`、`:646–650`），不属于「DB 事务失败」，因此不会触发 `remove_managed` → 最终路径留下孤儿文件。
- pause/cancel 按 R-SEAM-1 在 `BEGIN IMMEDIATE` 之后、live 写之前检查（卡 `:85`），此时 publish 已经发生 → 同样留下孤儿文件，`discard_temp` 无效。
- 这与 AC6「失败注入下…staging/final 文件**无新增可见产物**」（卡 `:105`）和 V9「先 publish 后 DB；**失败零推进**」（卡 `:133`）直接矛盾；V9 自己写出的「先 publish 后 DB」+「失败零推进」在没有全路径补偿时不可同时成立。

→ r1-P1-2 的「文件无事务原子性」被 v2 的顺序协议部分处理，但**拒绝路径的补偿缺口**使 AC6/V9 不可通过。修复建议（二选一写进卡）：**A** 把 publish 移入 `BEGIN IMMEDIATE` 内、在 CAS 屏障通过之后（文件写+DB 写同事务窗口，任一失败 rollback + `remove_managed`；崩溃后由预备候选 + 启动清扫按「无 `artifact_revisions` 引用 → `remove_managed`」恢复；需确认持锁做短文件 IO 可接受）；**B** 保持「先 publish」，但把补偿扩为「任何非 `applied` 结果（含拒绝/暂停/取消/异常）都 `remove_managed`+`discard_temp`」，并让 R-ART-3 的启动清扫同时覆盖 `abandoned` 候选（否则暂停路径留下的最终文件无清扫依据）。

### 1.3 P1-3（D4 被弱化为 V1–V8）→ **已解决**

- D4 行已写 V1–V9（卡 `:61`：「L2 自动化 + 真实生产 assembly 跑一遍（V1–V9）」）。
- AC8 已写「**V1–V9 全部从 R-SEAM-3 定义的真实生产 assembly 执行**」（卡 `:107`）。
- AC6 已显式绑定 V9（卡 `:105`：「A6、V9，**V9 必须从真实生产 assembly 执行**」）。
- V 矩阵含 V9（卡 `:133`）。→ **P1-3 处置成立**。

## 2. r1 的 10 条 P2 是否逐项落实

> 说明：逐条对照了卡内「复核处置对账」表（`:137–153`）与正文/写域；结论是**表与正文一致，10 条均有实际改动**，但其中 4 条在正文中留有新的精度缺口（见 §4 新 findings）。

| r1 P2 | 对账表声明 | 正文核验 | 判定 |
|---|---|---|---|
| P2-1 | AC2 落成状态机/扫除点断言；AC7② 固定只读核验程序 | AC2 卡 `:101` 已含 `prepared→resolved/abandoned`+`resolved_at`+四条路径+清扫计数；AC7② 卡 `:106` 已写「只读打开→三处一致性→候选可读→清单；保留既有备份，不创建/不恢复」 | **已落实**（但持久性受 r2-P1-1 影响） |
| P2-2 | AC4/AC7① 禁写清单补 `INSERT media_artifacts`/`INSERT artifact_revisions`/`storage.publish`；`_artifact_id` 延后 seam | AC4 卡 `:103` 含全清单与「`_artifact_id` 的 `INSERT media_artifacts` 必须延后到 seam」；AC7① 卡 `:106`「同 AC4 清单」 | **已落实**（R-ART-2 协议缺建行步骤，见 r2-P2-1） |
| P2-3 | AC8 定义真实 assembly = R-SEAM-3；逐文件表格；`t111_support.py` 单列 | AC8 卡 `:107` 已写；R-SEAM-3 卡 `:87` 定义 `assemble_core_services`（`:944`）+ writers（`:1340–1341`）+ `build_production_pipeline`（`:1377`），行号实测准确 | **已落实**（mock provider 口径未澄清，见 r2-P2-4） |
| P2-4 | R-SEAM-1 固定 pause/cancel 判定；V5 对应 | R-SEAM-1 卡 `:85`；V5 卡 `:129` 已写「commit_step 前设标志，R-SEAM-1」 | **已落实**（rollback/置 abandoned 顺序矛盾，见 r2-P2-3） |
| P2-5 | `REBASELINE_PLAN:28` 改为 `proposed` | 实测 `REBASELINE_PLAN.md:28` 已改为 `**proposed**（范围冻结 v2 待独立复核）`（`git diff 419f891c0 98fbccdf5` 可见） | **已落实** |
| P2-6 | 移除 ADJ 与 `doc/reviews/**` 写权；`tests/**` 收窄为 8 文件+登记新增 | `allowed_paths`（卡 `:21–42`）已无 ADJ/`doc/reviews/**`；tests 明确列 G7 8 文件（`:34–41`）；scope 正文 `:92` 要求新增测试先在本卡登记；`:95` 明确 reviews/ADJ 非 Owner 写域 | **已落实**（新增测试路径未进 frontmatter，见 r2-P2-6） |
| P2-7 | `base_commit` 更新为 `419f891c0`；ready 时再更新最终冻结 head | 卡 `:13` = `419f891c0`；对账表 `:150` 记「ready 时再更新」 | **已落实**（r2 冻结 head 为 `98fbccdf5`，ready 时须再更新） |
| P2-8 | R-SEAM-2 固定三选二观测证据 | R-SEAM-2 卡 `:86`：trace 单 commit + 独立连接 + WAL 一致性读，至少 ①+②；AC3 卡 `:102` 引用 | **已落实** |
| P2-9 | L-1/L-2/L-5 再触发条件补全 | L 表卡 `:115`–`:117` 已含「候选表加列/CHECK/索引」、「prepared/候选状态进入 Host 投影或 wire 可见语义」、「只读不创建备份」 | **已落实** |
| P2-10 | `STATUS:15` 13/13 → 15/15 | 实测 `STATUS.md:15` 已改为「`verify_pins.ps1` **15/15** PASS（14 份契约 + FEA-01…）」，`git diff` 可见 | **已落实** |

**结论**：10 条 P2 的对账表与正文一致，未发现「只改表不改正文」或「表与正文不一致」的情况；残留问题属于 v2 新引入的精度/一致性问题（§4），不属于原 10 条的未处置。

## 3. v2 是否引入新问题（重点项核验）

### 3.1 R-CAND-2 与 `_write_run` 现有实现的可行性

- **机制可行**：`_write_run` 每次在事务内 `DELETE FROM pipeline_runs`（`pipeline.py:433`）→ 级联清空候选 → 重建 run/targets/tasks/steps/candidates（`:466–528`）。在 `DELETE` 前 `SELECT`、在重建后 `INSERT`，并依赖 `run.step_runs` 已在 `run_json` 中（`pipeline.py:344`/`:372`，`_write_run` 先插 `step_runs` `:490–503`）重建 FK 目标，SQLite 语义上成立；读取/回插均在同一事务（`put_many` 自开事务 `:419`；`write_in_current_transaction` 要求调用方事务 `:410–414`）。
- **不可行/不完整处**：过滤条件只看 `status='prepared'`（卡 `:70`），与 R-CAND-3 的「不得硬删」自相矛盾（见 r2-P1-1）；另外 `_write_run` 重建时 `run.candidates` 用 `candidate_id` 主键插入（`:516–528`），若把「所有非 prepared 行」也纳入回插，必须排除 `run.candidates` 中已有的 `candidate_id`，否则主键冲突——v2 未写排除规则。
- **次序敏感**：seam 内「置 `resolved`」与 `persist()`（`pipeline.py:794–796` → `service.py:744–750` → `_write_run`）的先后决定该行是否被 R-CAND-2 捕获；v2 未固定次序。若按「先置 resolved 再 persist」实现，resolved 行在同一次 commit 内就会被删掉，AC3 直接失败。

### 3.2 R-ART 协议在 `commit_step` 现有事务/SQLite 语义下是否可实现

- **主干可实现**：`storage` 注入 catalog（R-ART-4 允许 `assembly.py`/`core_assembly.py` 接线）；`write_temp`/`verify_temp`/`publish`/`discard_temp`/`remove_managed` 均已在 `ManagedFileStorage` 存在（`managed_storage.py:98–126`）；`storage` 的端口缺 `remove_managed`，R-ART-4 允许在 `src/ports/repositories/storage.py` 最小新增（`ManagedFileStorage` 已有实现，不需改 `managed_storage.py`）。WAL + `BEGIN IMMEDIATE` 下「文件先落、DB 后写」的顺序在崩溃时可由预备候选 + 启动清扫恢复（前提是 r2-P1-2 的补偿/清扫缺口补齐）。
- **实质缺口**：①`publish` 在 `BEGIN` 前，拒绝/暂停/取消路径无 `remove_managed`（r2-P1-2）；②`R-ART-2` 的 DB 步骤只写「插 `artifact_revisions` 行、CAS `media_artifacts.current_revision_id`」，**缺首 revision 的 `media_artifacts` 建行**——而 AC4 明确要求 `_artifact_id` 的 `INSERT media_artifacts`（`step_writes.py:499–513`）延后到 seam；首 revision 时 CAS `UPDATE` 会命中 0 行（r2-P2-1）；③`R-ART-1` 的 payload 字段不足以重建 `artifact_revisions` 行（`step_writes.py:364–393` 的 20 列中缺 `artifact_id`/`revision_no`/`mime_type`/`width`/`height`/`options_json`/`provenance_json`/`provider_profile_id`/`model_name`/`source_artifact_revision_id`/`created_at`）（r2-P2-1）；④`commit_step` 的 Region 分支现在拒绝非 `"region"` 键（`pipeline.py:763–766`），而 R-ART-1 返回 `{artifact_type: id}`，必须改该守卫；v2 未写；⑤「run 启动清扫」在 `service.py`，但 service 没有 storage 句柄，v2 未指定清扫组件/接线（r2-P2-1）。

### 3.3 写域扩到 `src/bootstrap/core_assembly.py` 是否越过 §15.6 的 FEA-00a 边界

- **不构成硬违规**：方案 §15.6 明写「下表路径均 workspace-relative，为 DSH 冻结前建议，**不是实际写权**；每个任务另列 `doc/tasks/<ID>.md`…」（`:914`）。DSH 是范围冻结与写权授予的责任人（AGENTS.md 2026-10-25 裁决），D1=②（一起修 artifact）与 D2=②（允许改 `src/application/tasks/service.py`、必要时可重设计构件）为「为让 seam 访问 storage 而在组合根做最小接线」提供了依据；R-ART-4 也已限定「最小接线、默认 None 保持旧行为、Handoff 逐行列理由与回退、不改既有业务行为」。
- **但需要记录与约束**：①该卡未在卡内/ADJ 记录「相对 §15.6 FEA-00a 建议行的扩张理由」，也未声明与 FEA-10 的写域重叠（方案 `:931` 把 `src/infrastructure/pipeline/` 列入 FEA-10），建议在卡内补一段（或 ADJ errata）说明「FEA-10 尚未释放、本卡只做接线、后续 FEA-10 复核时不得视为既有改动」；②`src/bootstrap/core_assembly.py` 是整条生产装配，影响面大于 AC8 的 8 个测试文件（见 r2-P2-5）；③`R-ART-4` 的「默认 `None` 必须保持旧行为逐字节不变」与 R-ART-1 的「prepare 只 `write_temp`」存在矛盾（见 r2-P2-2）。

### 3.4 `allowed_paths` 收窄后是否仍可执行

- **基本可执行**：`src/application/tasks/**`（`service.py`、`store.py` 的 `TargetCatalog`/`InMemoryTargetCatalog` 协议）、`src/infrastructure/providers/**`、`src/infrastructure/sqlite/pipeline.py`、`src/infrastructure/pipeline/assembly.py`、`src/bootstrap/core_assembly.py`、`src/ports/repositories/storage.py` 已覆盖 R-CAND/R-ART/R-SEAM 的全部实现点；8 个 G7 测试文件已列；`verification/FEA-00A-IMPL-1/**` 可承载 V1–V9 日志与真实 assembly 脚本；`doc/handoffs/FEA-00A-IMPL-*.md` 已在写域。
- **仍缺/需澄清**：①**新增测试文件路径未写入 `allowed_paths`**（卡 `:92` 只要求「在本卡登记」，frontmatter 没有占位；按协议 §3.4 / §4.2，写权以 `allowed_paths` 为准）→ r2-P2-6；②若实现选择给 `ManagedFileStoragePort` 增加「校验已存在最终文件」的方法，其实现点在 `src/infrastructure/filesystem/managed_storage.py`（不在写域）；若选择在 `pipeline.py` 内用既有 `infrastructure.filesystem.integrity.integrity_of` 或 `storage.verify_temp(绝对路径)` 完成幂等校验，则不需扩写域——建议在卡内固定其一（r2-P2-1 的一部分）；③`src/domain/tasks/models.py` 未列入，但 R-CAND/R-ART 未要求改 `StepResult`/`StepResultCandidate` 结构，故不构成缺口；④`tests/pipeline/test_pipeline_production_seam.py` 未列入但用 `SqliteTargetCatalog(production_db)` 位置参数构造（`tests/pipeline/test_pipeline_production_seam.py:92/182/220`）——新增 `storage=None` 关键字默认值后兼容，且该文件不跑 artifact 步骤；⑤`build_production_pipeline` 的 6 个测试调用方（`test_regionless_rebinding.py:280`、`t111_support.py:253`、`test_detect_handler.py:155`、`test_full_chain.py:339`、`test_handlers_pipeline.py:257`、`test_retype_redetect_persistence.py:176`）均在 8 文件内，可适配传 storage（与 r2-P2-2 相关）。

### 3.5 指针一致性与文档口径

- `STATUS.md:7`：当前 Task = FEA-00A-IMPL-1 `proposed`，下一候选写「范围复核通过 → `ready` 交 Codex」→ **与卡一致**。
- `REBASELINE_PLAN.md:28`：**已改为 `proposed`**（v2 提交 diff 可见）→ r1-P2-5 已修。
- `REBASELINE_PLAN.md:14`：表格行 = `proposed` → 一致；`READY 节点：无`（`:26`）→ 一致。
- `TASK_LEDGER.md:30`/`:46`：`proposed` 计数 2、`FEA-00A-IMPL-1 = proposed` → 一致（v2 未改 status，ledger 无需重生成）。
- `STATUS.md:15`：**已改为 15/15** → r1-P2-10 已修。
- 卡 `:182`–`:183`：closeout 明写 r1 `changes_requested`、v2 逐条处置、**未释放**、复核通过前不 ready/不派实现 → 一致、诚实。
- `check.ps1` 实测 PASS（2 warnings），未捕获任何新的指针不一致；本报告核实仍有 1 处**措辞滞后**（非阻断）：`REBASELINE_PLAN.md:14` 仍写「范围冻结稿完成…待独立复核」，未提 v2/r2（内容仍准确，不构成 finding）。

### 3.6 生命周期 v3 与诚实性

- `status: proposed`（卡 `:6`）、`approval: user_ruling_2026-11-01_D1_D4`（`:7`）、`canonical_evidence_status: pending`（`:18`）一致；10 条 AC 全为 `[ ]` + 非空 `<<PARTIAL: 范围冻结；实现未开始>>`（卡 `:100`–`:109`），无 `MET`、无未执行标通过 → 符合协议 §4.3，**诚实**。
- AC10 的 PARTIAL 原因写「r1 为 changes_requested，已处置；r2 待派发；实现复核在交付后」（`:109`）→ 准确；本 r2 报告出具后，若仍为 changes_requested，AC10 继续保持 PARTIAL（不能判 MET）。

## 4. Findings（v2）

| ID | 级别 | 位置 | 问题（含证据） | 建议 |
|---|---|---|---|---|
| **FEA00A-SR2-P1-1** | **P1** | 卡 `:70`（R-CAND-2）、`:71`（R-CAND-3）、`:101`（AC2）、`:102`（AC3）、`:104`（AC5）、`:125`/`:129`（V1/V5）；`pipeline.py:433`、`:516–528`；`schema.py:381–382`、`:523–524`；`connection.py:319`；`service.py:723–727`、`:744–750`、`:764–786`、`:977–978` | **R-CAND-2 的保留范围只覆盖 `status='prepared'`，已转换候选（`resolved`/`abandoned`）仍会在下一次 `_write_run` 被级联删除。** `_write_run` 每次 `DELETE FROM pipeline_runs`（`pipeline.py:433`）→ FK 级联清空候选（`schema.py:381–382`/`:523–524`，`foreign_keys=ON` 于 `connection.py:319`），只回插 `run.candidates`（`:516–528`）与读取时仍为 prepared 的行（卡 `:70`）。成功路径的收尾 `_persist`（`service.py:977–978`）会删 resolved 行；失败路径的收尾 `_persist`（同处）会删 abandoned 行；`_record_step_attempt` 的 `_persist`（`:723–727`）会在多 unit run 中提前删掉 resolved 行。→ 与 R-CAND-3「任何路径不得删除…不硬删」矛盾；AC2 状态机查询、AC3/V7 持久断言、V1/V2「prepared 行存续」、V5「候选置 abandoned 可诊断」按现文不可稳定通过。 | 将 R-CAND-2 改为：读取 `run_id` 下**所有**候选行，删除后回插「`run.candidates` 中的行（来自 run）+ 其余行（来自 DB，按 `candidate_id` 排除已回插者，原样含 `resolved_at`）」；或明确保留状态集合为 `prepared ∪ resolved ∪ abandoned`。同步 AC2/AC3/AC5 与 V1/V2/V5/V7 的断言；固定「置 resolved/abandoned 相对 `persist()` 的次序」（建议转换在 `_write_run` 之后，或干脆由保留规则消除次序敏感）。 |
| **FEA00A-SR2-P1-2** | **P1** | 卡 `:79`（R-ART-2）、`:80`（R-ART-3）、`:85`（R-SEAM-1）、`:105`（AC6）、`:133`（V9）；`managed_storage.py:107–110`、`:115–124`；`pipeline.py:755–760`、`:646–650` | **「先 publish 后 BEGIN」+ 仅对 DB 异常补偿 → 拒绝/暂停/取消路径留下已发布的最终文件。** `publish` 是 `os.replace(temp, final)`（`managed_storage.py:115–124`），之后 `discard_temp` 对已移动的 temp 是空操作（`:107–110`）；而 `input_revision_changed`/`lock_changed`/`STALE_RUN_SNAPSHOT` 都是**返回状态**（`pipeline.py:755–760`、`:646–650`）不是异常，pause/cancel 检查在 `BEGIN` 之后（卡 `:85`）——这些路径均不触发 R-ART-3 的「DB 事务失败 → `remove_managed`」。→ 最终路径残留孤儿文件，与 AC6「失败注入下…无新增可见产物」及 V9「失败零推进」矛盾（V9 自身的「先 publish 后 DB」与「失败零推进」在该补偿范围下不可同时成立）。 | 二选一：**A** 将 `publish` 移入 `BEGIN IMMEDIATE` 内、CAS 屏障通过之后（文件+DB 同窗口，失败统一 `remove_managed`；崩溃由 prepared 候选 + 启动清扫恢复）；**B** 保留先 publish，但 R-ART-3 的补偿改为「任何非 `applied` 结果（拒绝/暂停/取消/异常）均 `remove_managed`（若已发布）+ `discard_temp`（若仍存在）」，并让启动清扫同时覆盖 `abandoned` 候选的最终路径。 |
| FEA00A-SR2-P2-1 | P2 | 卡 `:78`（R-ART-1）、`:79`（R-ART-2）、`:80`（R-ART-3）、`:92`/`:103`；`step_writes.py:364–393`、`:491–514`、`:943–967`；`pipeline.py:763–766`；`src/ports/repositories/storage.py`（端口缺 `remove_managed`/最终文件校验） | **R-ART 协议与现有 `commit_step`/数据模型衔接不完整**：①seam 的 DB 步骤缺首 revision 的 `INSERT media_artifacts`（AC4 卡 `:103` 已要求 `_artifact_id` 延后到 seam，但 R-ART-2 `:79` 只列插 `artifact_revisions` 行与 CAS 指针；首 revision 时 CAS `UPDATE` 命中 0 行）；②R-ART-1 的 payload 字段（`temp_handle`/`relative_path`/`artifact_type`/`page_id`/`base_revision_id`/`sha256`/`size`）不足以重建 20 列的 `artifact_revisions`（缺 `artifact_id`/`revision_no`/`mime_type`/`width`/`height`/`options_json`/`provenance_json`/`provider_profile_id`/`model_name`/`source_artifact_revision_id`/`created_at`）；③Region 分支仍拒绝非 `"region"` 键（`pipeline.py:763–766`），需随 R-ART-1 的 `{artifact_type: id}` 改动，但卡未写；④「run 启动清扫」需要 storage，`service.py` 无 storage 句柄，卡未指定清扫组件/接线；⑤`ArtifactStepWriter.publish` 方法不存在（实为 `prepare_revision` 内的 `storage.publish`），术语需校正；⑥幂等校验「已存在且 sha256 相同」需要读取最终文件哈希的方法（端口无此方法；可复用 `integrity_of`/`verify_temp`，但卡未固定，若新增端口方法则实现点在写域外 `managed_storage.py`）。 | 把上述六点在 R-ART-1/2/3 内补全并固定（建行顺序、payload 完整字段清单、Region 分支的新键集合、清扫组件与 storage 接线、方法名、幂等校验实现位置），再交实现。 |
| FEA00A-SR2-P2-2 | P2 | 卡 `:81`（R-ART-4）、`:78`（R-ART-1）；`assembly.py:36–37`；`tests/...` 6 个 `build_production_pipeline` 调用方 | **R-ART-4「默认 `None` 必须保持旧行为逐字节不变」与 R-ART-1「prepare 只 `write_temp`」矛盾**：writer 改为无条件 staging 后，`SqliteTargetCatalog(conn, storage=None)` 无法再发布/落 `artifact_revisions`，旧 artifact 行为无法保留。6 个 `build_production_pipeline` 调用方（`test_regionless_rebinding.py:280`、`t111_support.py:253`、`test_detect_handler.py:155`、`test_full_chain.py:339`、`test_handlers_pipeline.py:257`、`test_retype_redetect_persistence.py:176`）默认不传 storage 且会跑 artifact 步骤，均在 8 文件内、可适配，但卡未说明 `storage=None` 的语义（fail-closed？显式异常？）。 | 明确「`storage=None` 时 artifact 步骤 fail-closed（显式错误，不静默回退旧行为）；所有会跑 artifact 的调用方必须传 storage，并在 Handoff 列出清单」；若坚持旧行为，需给出 writer 的双模式设计（目前未给）。 |
| FEA00A-SR2-P2-3 | P2 | 卡 `:85`（R-SEAM-1）；`store.py:56–65`（`TargetCatalog.commit_step` 协议）；`service.py:730–790` | **R-SEAM-1 的「rollback 并同时置 `abandoned`」自相矛盾**（rollback 会撤销同一事务内的 `abandoned` 更新），且未说明 pause/cancel 标志如何进入 `commit_step`（当前签名无 run/flags 参数，`store.py:56–65`、`pipeline.py:742–751`），也未定义新增结果状态（`paused`/`cancelled` 类）在 `service.commit_step_result` 的映射（现有 else 分支映射为 `DB_FAILED`/`TARGET_NOT_FOUND`，`:788–789`）。 | 写成「命中 pause/cancel → rollback → 用独立短事务置候选 `abandoned` → 返回 `paused`/`cancelled`」，并明确 `commit_step` 新参数（`pause_requested`/`cancel_requested` 或 run 快照）、`CatalogCommit` 新状态及 service/AC1/V5 的映射与 Run/Step 状态语义（AC9 登记 service.py 改动）。 |
| FEA00A-SR2-P2-4 | P2 | 卡 `:87`（R-SEAM-3）；`core_assembly.py:944–957`；既有 `mock_local_providers=True` 用法（`tests/core/test_core_detect.py:88`、`tests/m2_acceptance/test_data_integrity.py:93` 等） | **R-SEAM-3「禁止 fake executor/double」与既有验收口径冲突/未澄清**：`assemble_core_services` 需要 `image_decoder`/`font_catalog`/`layout_engine`/`compositor`/`source_styles` 适配器（`:944–957`），且 V1–V9 需要确定性的 provider 输出；现有 M2 验收用 `mock_local_providers=True`（真实 assembly + mock provider）。若「double」被解读为连 provider/适配器 mock 都禁止，V1–V9 在 CI 不可行。 | 明确口径：「`assemble_core_services(..., mock_local_providers=True)` 与测试适配器注入允许（provider/成像层），但 executor/handlers/writers/storage/seam 必须是生产实现，不得替换」；并写进 AC8/R-SEAM-3。 |
| FEA00A-SR2-P2-5 | P2 | 卡 `:30`–`:32`（写域扩项）、`:91`（范围正文）；方案 §15.6 `:914`、`:919`、`:931`；`tests/**` 中 `assemble_core_services` 的 10 个文件 | **写域扩到 `src/bootstrap/core_assembly.py` 的两项风险需登记**：①超出 §15.6 FEA-00a 建议路径行（`:919`），虽 §15.6 `:914` 明说表不是实际写权、DSH 有冻结权，但卡内未记录扩张理由，也未声明与 FEA-10 写域（`:931` 含 `src/infrastructure/pipeline/`）的重叠；②影响面大于 AC8 的 8 文件——`assemble_core_services` 还被 `tests/infrastructure/test_plugin_sandbox.py:315`、`tests/core/test_core_assembly.py:215`、`tests/core/test_core_detect.py:80`、`tests/m2_acceptance/` 4 文件（`:146`/`:138`/`:85`/`:81`）、`tests/providers/test_detection_manga.py:896`、`tests/core/test_sfx_assembly.py:68`、`tests/core/test_sfx_policy_settings.py:73` 使用，均不在 allowed_paths；若接线导致这些测试变化，Owner 无法修改。 | 在卡内补「相对 §15.6 建议行的扩张理由 + 与 FEA-10 的重叠声明（FEA-10 未释放，本卡只做接线）」；AC8 增加「受 `core_assembly` 接线影响的测试集只读执行结果（passed/failed/skipped 分列）」，失败时按范围变更程序处理。 |
| FEA00A-SR2-P2-6 | P2 | 卡 `:21–42`（`allowed_paths`）、`:92` | **新增测试文件（V1–V9 很可能需要新文件）未进入 `allowed_paths`**：正文要求「新增测试文件…须先在本卡登记路径」，但 frontmatter 只列 G7 的 8 个文件；按协议 §3.4/§4.2，写权以 `allowed_paths` 为准，正文登记不等于写权。 | 在 `ready` 前把 V1–V9 新增测试文件（及真实 assembly 执行脚本，若放 `tests/`）的精确路径写入 frontmatter `allowed_paths`；登记动作本身可随 `ready` 提交完成。 |
| FEA00A-SR2-P2-7 | P2 | 卡 `:69`（R-CAND-1）、`:71`（R-CAND-3）、`:101`（AC2）；`service.py:764–786` | **同一步骤「abandoned（prepared 转换）+ pending（诊断候选）」两行关系未落成断言**：失败路径 service 会再插入一条 `StepResultCandidate`（`service.py:769–780`，状态默认 `pending`），同时 R-CAND-3 保留原 prepared 行并置 `abandoned`；AC2 只断言状态机与字段，未定义「同一步两行的查询口径/不得互删/证据格式」，验证者可能只看到一行。 | 在 AC2 或 R-CAND-3 补一句：同一步骤允许两行（`abandoned` 暂存行 + `pending` 诊断行），以 `reason`/`status`/`resolved_at` 区分，二者均不得删除；V1/V2/V5 证据须同时列出两行。 |

**P0 = 0。P1 = 2（FEA00A-SR2-P1-1/2）。P2 = 7（FEA00A-SR2-P2-1…7）。** r1 的 P1-3 与 10 条 P2 已解决；r2 的 P1 需在下一版冻结中真正补齐后才可 `approved`。

## 5. 结论与边界声明

1. **decision: `changes_requested`**。v2 对 r1 的处置总体是实质性的（新增 R-CAND/R-ART/R-SEAM 规则、AC 改写、写域重划、指针修正），P1-3 与 10 条 P2 均已有实际改动；但 P1-1/P1-2 的核心（候选行全生命周期保留、artifact 文件全失败路径补偿）仍各留一个可导致 AC2/AC3/AC5/AC6/V1/V2/V5/V7/V9 不可通过的设计缺口，且 7 条 P2 需收口。修完 P1（尤其把 R-CAND-2 的保留范围与 R-ART-3 的补偿范围写全）后，可对修订 head 再做一次独立上下文复核。
2. **本次复核只针对范围冻结**，不构成实现验收；本报告不评价任何实现（实现尚未开始），`approved` 也不等于 Task 完成或可发布。实现后仍需独立实现复核（`doc/reviews/FEA-00A-IMPL-r1.md`）、AC 逐项证据、集成与 closeout。
3. **独立性**：本席位（`fea00a-scope-reviewer`）为 DSH（Lead）以 fresh 独立上下文派发的 Agent Teams teammate（第二轮沿用同一独立席位），未参与该 Task 的起草、实现或返修；只读被审 head，未修改任何被审文件（除本报告）、未 commit、未 push。
4. **建议的下一步（供 DSH）**：①按 r2-P1-1 扩写 R-CAND-2（保留所有非 `run.candidates` 候选行）并同步 AC2/AC3/AC5/V 断言；②按 r2-P1-2 在「publish 移入事务内」与「全路径补偿+清扫」中二选一并写进 R-ART-2/3；③收口 r2-P2-1…7（建行/payload/守卫/清扫接线/`storage=None` 语义/`commit_step` 参数与结果状态/mock 口径/写域扩张记录/新增测试路径/双行语义）；④对 `98fbccdf5` 之后的新 head 重新派独立上下文复核；⑤复核 `approved` 且 P0/P1=0 后再 `ready` 交 Codex。

—— 报告结束（`decision: changes_requested`；P0×0 / P1×2 / P2×7；r1 处置：P1-3 已解决、P1-1/P1-2 部分解决、P2×10 已落实）。
