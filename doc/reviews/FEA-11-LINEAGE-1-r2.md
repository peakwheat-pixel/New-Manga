---
task_id: FEA-11-LINEAGE-1
reviewer: 独立上下文 fresh subagent（DSH 派发；未参与实现/返修）
reviewer_kind: subagent
base_commit: 81c28d305
reviewed_head: 3c40f7020
decision: changes_requested
---

# Review：FEA-11-LINEAGE-1（r2）

> 审查者：DSH 派发的独立上下文 fresh subagent（本会话），未参与本任务任何实现或返修；只读审查。
> 审查对象：`3c40f7020`（main），`base_commit=81c28d305`；期间 Lead 并发的 FEA-12 docs 提交 `86bc87e1e` 按派发说明排除，但同一范围内 r1 生命周期的 `ef35fc035`/`035468a81` 一并核对。
> 冻结依据：`doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md` §7.1/§8；`doc/reviews/FEA-11-r7-acceptance.md`；任务卡内 DSH 2026-11-05 四点 r2 裁决；上一轮 `doc/reviews/FEA-11-LINEAGE-1-r1.md`。

## 结论

**changes_requested：P0=0 / P1=1 / P2=3 / P3=5。**

- **P1-01（阻断）**：DSH 裁决 ③ 的「page-scope Run 过滤旧坐标 region」只在 `SqliteTargetCatalog.expand` 的 `TargetSnapshot.regions` 上生效；Run 执行链的 `detect` handler 仍用 page-id-only repository 读取**全部** live region（含 lineage-hidden 旧 region），把它们作为 `region_ids` 输出，随后 `_backfill_detected_regions` 调 `_catalog.current()` 触发 lineage guard，异常未被白名单捕获，被 `commit_step` 的宽泛 `except Exception` 吞成 `db_failed` → 步骤/任务以 `DB_FAILED` 失败。结果：**changed/unverified 同步页无法执行 page-scope 重新检测类 Run**（`REOCR_ALL`、`TRANSLATE_ALL` 等），与裁决 ③「过滤后在新图 region 集合上继续」及 C-17 §7.1「page_id-only repository 不得成为旁路」不符，且无测试覆盖。r2 的「L1 已闭环」「Run page-scope 过滤」表述因此不成立。
- **P2-01**：Run 候选提交的 typed lineage 分支实际不可达（`current()` 先抛 `PipelineError`，`except LineageVerificationError` 收不到），post-prepare 切换被映射为 `DB_FAILED` 且 prepared candidate 被 abandoned，与 C-17 §7.1 交错表「结果留 candidate」及代码自身意图不符（零写安全成立）。
- **P2-02**：r2 新增行为的关键判别性测试缺失：draft apply 的 typed 拒绝、batch/reorder/merge 写入侧防洗白拒绝、backfill 失败不阻断装配、page render skip code/reports 断言。审查者已用仓外探针独立证明前两类行为正确，但仓库内无对应证据。
- **P2-03**：`allowed_paths` 与卡面陈述不一致——Scope Review 声称 `doc/TASK_LEDGER.md`「已按 DSH 窄批登记进本卡」，但 frontmatter `allowed_paths` 无此项；该文件在范围内被 r1 生命周期提交 `ef35fc035`、`035468a81` 改动（r2 提交未再改）。r1 P1-3 只闭合了 4/5。

其余 5 项为 P3（见 Findings）。AC1/AC3 判 MET；**AC2 判 PARTIAL**（page-scope Run 执行链缺口；另有 typed 测试空档）。

## 范围与依据

- 需求：任务卡 AC1/AC2/AC3 + r2 DSH 四点裁决 + C-17 §7.1（lineage 同事务写入、same_content 读边、changed 切断、page-id-only repository 不得成为旁路）+ §8（局部错误闭集仅 C-17 命令投影，旧命令不重映射）+ r7 硬约束（LINEAGE-1 完成前读路径不得消费同步新 binding）。
- diff：`git diff 81c28d305..3c40f7020 --name-only` 共 24 文件；排除 FEA-12 docs（`86bc87e1e`：`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/TASK_LEDGER.md`(部分)、`doc/reviews/ADJ-2026-11-05-FEA-12-SCOPE.md`、`doc/tasks/FEA-12-*.md`）后，全部落在卡内 `allowed_paths`（`doc/TASK_LEDGER.md` 见 P2-03）。产品代码 18 文件、测试 3 文件、证据 2 文件。
- 未审到/不可验证：真实 UI/IPC 端到端、真实用户库升级、.NET 全量（本卡 Python-only，见门禁）；历史 gate 运行时的 clean worktree 只能由日志佐证。

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| R2-01 | P1 | `src/infrastructure/providers/handlers.py:344-355`；`src/application/tasks/service.py:566-595,1411,1435-1446`；`src/infrastructure/sqlite/pipeline.py:874,1030-1038,1552`；`src/bootstrap/core_service.py:304`（`_page_or_error` 过滤） | **page-scope Run 过滤在 detect 复用处失效**。changed/unverified 同步页上 `expand` 的 page target `regions=()` → planner 计划 `detect`（`_plan_region` 对 `region is None and "ocr" in steps` 前置 detect）→ `handle_detect` 用 `deps.regions.list_regions(page_id)`（page-id-only，含 hidden）非空 → 复用旧 region id 输出 → `_backfill_detected_regions` 对每个 id 调 `_catalog.current()` → `_ensure_lineage_readable` 抛 `PipelineError(LINEAGE_*)` → 只白名单 `TARGET_DELETED/TARGET_NOT_FOUND`，重抛 → `commit_step` 宽泛 except → `db_failed` → 步骤 `DB_FAILED`。用户影响：changed 页无法用 page-scope 重跑 OCR/翻译（`REOCR_ALL`/`TRANSLATE_ALL`），与裁决 ③ 及卡面矩阵「page-scope 过滤」矛盾；也违反 C-17 §7.1「page_id-only repository 不得成为旁路」。 | 代码链逐行核对；审查者探针 `verify_detect_reuse.py`：cut 后 `_catalog.current("rg1")` 抛 `PipelineError code=LINEAGE_BINDING_CHANGED`（仓外日志 `probe-detect-current.log`）。现有测试仅 `expand` 断言 `regions==()`（`test_source_lineage_native.py:858-861`），无 Run 执行链测试。 | detect 复用必须使用 lineage 可见集合（把 guard/facts 注入 handler deps，或从 Run target snapshot 读可见 region id）；全 hidden 时应在**新图**上执行检测；region-requiring 的 page 步骤（render/inpaint）在过滤后空格集应计划为 no-op/terminal 或 plan 期 typed 拒绝。`handlers.py`/`tasks/service.py` 不在本卡 allowed_paths，需 DSH 窄批或后续卡。判别性测试：cut 页 + hidden region + stub detector 跑 `REOCR_ALL`，断言 detect 输出不含 hidden id、检测到新 region、run 完成、hidden region 无新 revision/lineage；再跑 `RERENDER_ALL` 断言干净终态或 typed 拒绝而非 `DB_FAILED`。 | open |
| R2-02 | P2 | `src/infrastructure/sqlite/pipeline.py:874,1030-1038,1552`；`src/application/tasks/service.py:925-952` | **Run 候选提交的 typed lineage 分支不可达**。`commit_step` 先 `current(target_id)`；对 region target 该调用进入 `_region_or_error` 的 `_ensure_lineage_readable`，切换后抛 `PipelineError(LINEAGE_*)`（`pipeline.py:1552`）；`except LineageVerificationError`（1030）收不到，落 `except Exception` → `_reject_prepared("db_failed", repr(error))` → `commit_step_result` 得 `DB_FAILED`，prepared candidate 被标记 abandoned，未走 925 行保留 candidate 的 `input_revision_changed` 分支。零写安全成立，但 C-17 §7.1 交错行「结果留 candidate，不改已接受快照」未满足，且新增的 typed 分支是死代码。 | 审查者探针 `verify_run_candidate.py`（仓外）：B1 上 prepare OCR candidate → 切 changed B2 → `commit_step_result` 返回 `failed/DB_FAILED`，detail=`PipelineError('LINEAGE_BINDING_CHANGED: ...')`；revision/lineage/current 全部未变（zero write）。 | 在 `commit_step` 显式捕获 lineage 码的 `PipelineError` 并路由到 `_reject_prepared("input_revision_changed", error.code, ...)`（保留 candidate；旧命令面仍为 conflict，不重映射 C-17 §8）；或让 `current()` 的 lineage 拒绝以 `LineageVerificationError` 类型进入 1030 分支。判别性测试：prepare→switch→commit，断言非 committed、step error 为既有 conflict 语义且 detail 含 LINEAGE 码、无新 revision/lineage、candidate 被保留而非 abandoned。 | open |
| R2-03 | P2 | `tests/fea11/test_source_lineage_native.py:317-357,431-457,465-606,685-710,721-872`；`tests/fea11/test_source_lineage_assembly.py:171-307` | **r2 新增行为缺判别性测试**：(a) draft apply 在 cut binding 上的 typed 拒绝（`DraftError` + 零写）无测试，仅 happy path；(b) batch/reorder/merge/split 写入侧防洗白拒绝无测试（`_commit_region_batch` 的 `ensure_writable` 仅 happy path 被间接覆盖）；(c) backfill 失败不阻断装配（`core_assembly.py:1216-1221` 的 except）无测试；(d) page render 的 skip code/reports 与 `handle_rerender_page` 的 LINEAGE 映射无断言。 | 审查者探针 `verify_lineage_guard.py` 12/12 PASS：reorder batch 拒绝、draft apply 抛 `DraftError(LINEAGE_BINDING_CHANGED)`、restore 拒绝，均零写、无新 lineage；但这是仓外证据，不在仓库测试内。(c)(d) 仅代码走查。 | 补 4 个最小测试（draft-refusal、batch-refusal、backfill-failure、render reports）；backfill-failure 用 monkeypatch 令 `backfill_legacy_unverified_lineage` 抛错并断言 `assemble_core_services` 仍成功且 stderr 有告警。 | open |
| R2-04 | P2 | `doc/tasks/FEA-11-LINEAGE-1.md:37,56`；`doc/TASK_LEDGER.md`（`ef35fc035`、`035468a81`） | **文档与 allowed_paths 不一致**：卡面 line 56 称 `doc/TASK_LEDGER.md`「已按 DSH 窄批登记进本卡」，但 frontmatter `allowed_paths` 未列该路径；且该文件在审查范围内被两个 r1 生命周期提交修改（r2 提交 `501fe80c8..3c40f7020` 未再改）。裁决要求/证据链本身不受影响（Lead 维护的生命周期簿记），但 r1 P1-3 的「登记进 allowed_paths」在文字上不成立。 | `git log --oneline 81c28d305..3c40f7020 -- doc/TASK_LEDGER.md` 显示 `ef35fc035`、`035468a81`；`git log --oneline 501fe80c8..3c40f7020 -- doc/TASK_LEDGER.md` 为空；frontmatter 21-42 行无该余项。 | 把 `doc/TASK_LEDGER.md` 补进 allowed_paths（并注明由 Lead 维护），或删除/改写卡面该句；二者取一，保持 r1 P1-3 记录一致。 | open |
| R2-05 | P3 | `src/application/sources/lineage.py:124-135,160-180`；`src/infrastructure/sqlite/source_sync.py:922-942` | 守卫只按 `revision_id` 取 lineage，未校验 lineage 行的 `region_id`/page 归属（§7.1「并验证 region/revision/page 归属」）。当前所有生产调用点都从同一 region 行的 current 指针取 revision，无实际旁路；但数据损坏/未来新调用点缺少防御。 | 代码走查；lineage facts 查询未取 `region_id`。 | 在 `RevisionLineageStanding` 增加 `region_id`，`_code_for` 断言 `standing.region_id == region_id`，并补一个损坏数据拒绝测试。 | open |
| R2-06 | P3 | `src/bootstrap/core_service.py:2466-2471,2722,2845,2977`；`src/bootstrap/core_service.py:2458-2461` | 诊断/校验层面的不完美：(a) `list_page_region_texts` 显式 `region_ids` 中 hidden region 在过滤后落入 `TARGET_NOT_FOUND`，与「未知/已删」不可区分（stderr 有计数，符合 DSH 裁决下限，但 UI 语义会误导）；(b) reorder 要求 `ordered_region_ids` 等于**全部** live id（含 hidden），mixed 页上 UI 看不到 hidden id 故无法重排；create 的 cap 也含 hidden。均为非数据安全问题。 | 代码走查；现有测试未覆盖 mixed 页 reorder。 | 可在后续把 reorder/merge 校验改到可见集合（或显式返回 typed 诊断），并让 text 读面区分 `LINEAGE_*_HIDDEN`。 | open |
| R2-07 | P3 | `src/infrastructure/sqlite/pipeline.py:1554-1576` | `freeze_context` 仍直接读相邻页全部 region 的 `ocr_text` 作为上下文，未过 lineage guard；仅文本上下文、无坐标产物，不构成 AC11-5 坐标泄漏，但属 §7.1「Run 读取当前区域」的未过滤读路径。 | 代码走查。 | 在后续把 context 页也按 guard 过滤（或 DSH 明确 context 不属于「当前区域读」）。 | open |
| R2-08 | P3 | `apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandRegistry.cs:30-39,113-133` | Host 的 `AllowedRunErrorCodes` 未注册 `LINEAGE_BINDING_CHANGED`/`LINEAGE_UNVERIFIED`；`library_start_run` 等会把新码投影为 `category=unknown`、固定 generic message（不抛错、仍 fail-closed）。Core 侧 typed 已产生，但桌面端看不到 conflict 语义。`apps/**` 不在本卡 allowed_paths。 | 代码走查（.NET 未跑，见门禁）。 | 若 UI 需要正确提示，另开 Host 窄批把两码加入 Run allow-list，并补 .NET 投影测试；否则记录为已知集成限制。 | open |
| R2-09 | P3 | `verification/FEA-11-LINEAGE-1/logs/gates-r2.log:1-8`；`doc/tasks/FEA-11-LINEAGE-1.md:112-115` | 证据卫生：EV-0/EV-1 的 `sha256` 均为 `-`，`canonical_evidence_status: pending`、`delivery_head: null`（集成前预期）；gate 日志无显式 shell/venv 头（有解释器/日期/head）。r1 P2 的「证据卫生」仅部分处理。 | 文件核对。 | 集成时补 sha256 与 delivery_head；日志头补 shell 行。 | open |

P3 另记（不单列）：r1 P2 的风格项仍有残留——`_commit` 仍用 `**extra`、`_lineage_for`/`_lineage_by_region` 无返回注解、`drafts/service` 的局部 import 与 InMemory `del lineage` 仍在、`list_region_revisions` 未过滤（AC 未要求，但卡面 line 92 把它列入 typed 映射，实际该命令不会抛 lineage 错误，属表述过宽）。均不影响正确性。

## r1 Findings 核销表

| r1 | 判定 | 核销证据 |
|---|---|---|
| **P0-1** 6 类写路径 + 存量 backfill + 守卫区分 | **已修复**（本卡主要目标） | 写路径：`regions.py:295-304`（单 revision）、`:495-521`（batch，含 merge/split 源 region）、`:686-717`（`_insert_revision` 同事务 `insert_lineage`）、`:166-187`（`add_revision`）；`service.py:451-475`/`538-568`/`1493-1505`（`_commit`、`_commit_user_or_raise`、restore）；`drafts.py:476-509`（draft apply）；`pipeline.py:1050-1090`（Run candidate）。全库仅 3 个 `INSERT INTO region_revisions` 写者，均已覆盖（`git grep` 复核，见验证表）。backfill：`source_sync.py:387-424` + `core_assembly.py:1197-1221`（只覆盖有 publication 的页、anti-join、NULL 归属、幂等、失败不阻断）。守卫区分：`lineage.py:160-180`（无 lineage/legacy → UNVERIFIED；binding 不同且 same_content 不可达 → BINDING_CHANGED）。测试：`test_source_lineage_native.py:248-357,431-457,685-710`；审查者探针 12/12。**残留**：page-scope Run 执行链（R2-01）与 Run commit typed 投影（R2-02）。 |
| **P1-1** same_content 多跳读边 | **已修复** | `SourceSyncLineageFacts.same_content_reachable`（`source_sync.py:944-961`）沿 publication.previous 仅走 same_content；`test_same_content_chain_is_readable_multi_hop`（native:465-494）两跳；matrix `p-same`。 |
| **P1-2** typed 错误码 + 入口覆盖 | **基本修复，留 P2/P1** | 应用层码 `lineage.py:40-41`；旧命令面 conflict/retryable=false（`core_service.py:904-929,878-879,3279-3298,5100-5123`）；入口：ListRegions/文本读过滤（`:2387,2461,588-605`）、export（`:4708-4745`）、page render skip+计数（`rendering/service.py:204-219,471-505`；`core_service.py:3305-3321`）、单 region rerender BLOCKED（`rendering/service.py:339-356`）、编辑 typed（dispatch catch）、Run region-scope typed（`pipeline.py:1439-1459`）、draft 映射（`drafts.py:504-509`）。**缺口**：Run commit 死分支（R2-02）；page-scope Run detect 复用（R2-01）；draft-refusal 等测试缺失（R2-03）。 |
| **P1-3** allowed_paths 窄批 | **部分修复（4/5）** | ports/service/core_assembly/native 测试已入列；TASK_LEDGER 见 R2-04。 |
| **P1-4** opt-in/fail-open | **按 DSH 裁决替代并闭环** | 裁决 ① 限定作用域；生产唯一装配 `core_assembly.py:1140-1154,1477-1497,1604-1605,1768` 始终注入；装配测试断言同一 guard identity（assembly:171-183）；`None` 仅保留给单元构造。无生产 fail-open 构造点（`git grep SqliteRegionRepository(` 仅 assembly 一处）。 |
| **P1-5** 真实 SQLite + 装配级测试 | **已修复** | native 测试全用真实 `:memory:` v8 + 生产类，无 fake repo/`__new__`（`grep` 复核；唯一 `__new__` 在无关 `test_source_resolve.py:42`）；assembly 测试用真实 `assemble_core_services` + `CoreServiceServer`。 |
| **P2（7 项）** | **5 项已处理/部分处理** | 协议参数已声明（ports:34-40,99-123）；`_commit_batch_or_raise` 显式参数、去 `type: ignore`（service:492-530）；复用 `insert_lineage`（regions:709、pipeline:1084）；`RevisionLineage` provenance Literal（ports:137+）；page 级 1 次 + 批量 1 次查询（lineage:201-227）；剩余风格项见 R2-09 附注。 |

## AC 逐条判定

- **AC1（同事务 native lineage；B1/R1→B2、same_content、changed 有测试）→ MET**。三条 INSERT 写者全部同事务登记；service/draft/Run/add_revision/restore 全接；原生测试覆盖 5 连写、reorder、draft、Run、add_revision、回滚无孤儿；探针独立证明 batch/draft/restore 拒绝零写。`<<MET>>` 有实体证据。
- **AC2（ListRegions/渲染/导出/Run/编辑入口守卫、same_content 放行、过滤带诊断计数）→ PARTIAL**。各读面守卫与计数均存在且有测试（list/export/render/单 region/edit/region-scope Run）；但 **page-scope Run 执行链**在全 hidden 页复用了 hidden region（R2-01），导致 run 以 `DB_FAILED` 失败，裁决 ③ 的「过滤后继续」未达成；draft 拒绝、batch 拒绝、page render reports 的测试缺失。把 AC2 标 `<<MET>>` 属**过度声明**，应改 PARTIAL 或在 r3 修复后恢复 MET。
- **AC3（AC11-5 旧坐标对新图不可见 + 回归）→ MET**。assembly 测试在 cut 后断言 list/export 为空、edit 拒绝 `LINEAGE_BINDING_CHANGED` 且 current 未变（assembly:271-306）；native 测试断言单 region/页面渲染隐藏与 typed BLOCKED、legacy_unverified 隐藏；真实 v8 DB + 装配链路，不是散文证据。

## 独立验证证据

| 场景 | 命令/步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| 写路径独立 grep | `git grep -n "INSERT INTO region_revisions" -- src`；`git grep -n "source_revision_lineage" -- src`；`SqliteRegionRepository(` 构造点 | 3c40f7020 | 3 个 revision 写者（pipeline:1072、regions:690、source_sync:846）全部有同事务 lineage；lineage 仅 `insert_lineage` + backfill 两个 INSERT；生产仓储仅 assembly 一处构造 | 本报告；日志仓外 |
| 写侧防洗白探针 | 仓外 `verify_lineage_guard.py`：B1 native → changed B2；single/batch/draft/restore 写入 | 3c40f7020 工作树（Python 与 head 一致） | **12/12 PASS**：全部 `LINEAGE_BINDING_CHANGED`、零新 revision、无新 lineage | `G:\CODEX\New Manga.workspace\FEA-11\review-r2\probe-writepaths.log` |
| Run candidate 防洗白探针 | 仓外 `verify_run_candidate.py`：prepare OCR candidate → changed 切换 → commit | 同上 | 零写 PASS，但 outcome=`failed/DB_FAILED`（detail 含 LINEAGE 码）→ R2-02 证据 | `...\probe-run-candidate.log` |
| page-scope Run 执行链 | 仓外 `verify_detect_reuse.py`：cut 后 `_catalog.current(hidden)` | 同上 | 抛 `PipelineError code=LINEAGE_BINDING_CHANGED`；`_backfill_detected_regions` 不白名单该码 → `commit_step` 宽泛 except → DB_FAILED（R2-01） | `...\probe-detect-current.log` |
| 诊断矩阵 | `pytest ...test_mixed_library_scope_matrix... ...test_source_lineage_assembly.py -s` | 同上 | 4 passed；stderr 复现 `lineage_hidden` 与 `refused` 计数，matrix 五行与卡面一致 | `...\gate3-matrix.log` |
| 真实 SQLite/装配 | 全量 fea11、assembly 测试 | 同上 | 62 passed（含 3 装配级） | `...\gate1-fea11.log` |

## 门禁复跑结果（只读；日志全部仓外）

| 门禁 | 命令 | 结果 | 证据 |
|---|---|---|---|
| fea11 | `C:/Python314/python.exe -m pytest tests/fea11 -q -p no:warnings -p no:cacheprovider --tb=no` | **62 passed**，EXIT 0 | `...\gate1-fea11.log` |
| 全量 pytest | `C:/Python314/python.exe -m pytest tests -q -p no:warnings -p no:cacheprovider --tb=no` | **3073 passed, 10 skipped**，EXIT 0（284s；基线 3060/10，+13 = native 9→19 + assembly 3） | `...\gate2-full-stdout.log` / `gate2-full-stderr.log` |
| 诊断矩阵 | 同上 `-s` 两测试 | **4 passed**，EXIT 0 | `...\gate3-matrix.log` |
| governance check | `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS (2 warnings)**：15 非终态 Task、REBASELINE_PLAN 80%；EXIT 0 | `...\gate4-check.log`、`gate4b-check-current.log` |
| frozen pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PIN AUDIT: PASS (all 18)**；C17 `86b89ff83c9a`、FEA01 `0370c18932b1` | `...\gate5-pins.log` |
| .NET | 未跑 | **NOT_RUN（合理）**：范围内 `apps/**` 零 diff（`git diff 81c28d305..3c40f7020 --name-only -- 'apps/**'` 为空），本卡 Python-only；但注意 R2-08 的 Host allow-list 集成点未由 .NET 测试覆盖 | 本报告 |
| 冻结契约/依赖/schema | `git diff 81c28d305..3c40f7020 --stat -- doc/contracts doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md pyproject.toml requirements*.txt src/infrastructure/sqlite/schema.py src/infrastructure/sqlite/migrator.py` | **空 diff**；`verification/FEA-09/**` 空 diff | 本报告 |
| push 状态 | `git rev-parse origin/main`（b1c1f5a5，早于 head）；无 upstream | 本地 head 未推送（无远端引用可证同一对象，结论为「未见 push 证据」） | 本报告 |

**门禁环境说明（诚实记录）**：审查开始（14:59）HEAD=`3c40f7020`；15:02:58 期间 Lead 并发提交 `c2b40c9f3`（FEA-11-HOST-AUTH-1 closeout，仅 docs/verification）落地，并伴随 FEA-12-PREREQ-1 的未提交 .NET/docs 工作。审查者复核 `git diff --name-only 3c40f7020 -- src tests` 为空，故上述 pytest 结果对 `reviewed_head` 的 Python 代码有效；check/pins 在含 `c2b40c9f3` 的工作树上仍 PASS（该提交不改契约/测试/产品代码）。审查者未 commit/stash/reset/checkout；测试未产生仓内文件（`-p no:cacheprovider`）。

## limitation 意见

- **L1（导出/Run/ListRegions/单区域渲染守卫）→ 不能判「已闭环」**：ListRegions/文本读/export/单 region/page render/编辑均有实现与证据，但 **page-scope Run 执行链**（R2-01）使「Run 过滤旧坐标 region」只在 expand 层成立、执行层以 DB_FAILED 失败。建议 r3 修复后改回「已闭环」；在修复前应把 L1 维持为「部分闭环」，不得写「无 deferral」。
- **L2（AC11-5 集成测试）→ 已闭环**：真实 v8 SQLite + 生产仓储 + assembly 级 wire 测试覆盖 native→changed 拒绝 / same_content（多跳）放行 / 无 lineage 诊断 / 回滚无孤儿 / draft、Run、restore、batch 登记（`native` 19 项 + `assembly` 3 项）。同意闭环。
- **L3（same_content 读边）→ 已闭环**：`same_content_reachable` 多跳 + changed/repoint/missing 切断 + 测试；`migrated`/legacy 语义正确。
- 残余 1（reader projection）：reader 只读整页 translated artifact，不消费 region 坐标，不构成 AC11-5 坐标泄漏；stale 整页图失效属 FEA-11 既有 stale 语义，建议另开卡，不阻塞本卡。
- 残余 2（非同步页 fail-open）：与 DSH 裁决 ① 一致，不判缺陷。
- 残余 3（run_source_guard 与 lineage guard 分层）：属实，不冲突。

## done / closed_with_limitations 意见

- 当前 **不可 done**：AC2 PARTIAL、P1-01 未解决；也不建议用 `closed_with_limitations` 掩盖——这是可实现的小范围修复，不是契约外 deferral。
- 建议 r3 最小返修：R2-01（page-scope Run detect/空集执行链 + 测试）、R2-02（commit_step 捕获 lineage 码的 PipelineError，保留 candidate + 测试）、R2-03 的 4 个测试、R2-04 的 allowed_paths 文字修正。修复并复跑门禁后，可判 AC2 MET → `done`；若 DSH 裁决把 page-scope Run 失败视为可接受限制，则必须把 L1 改回「部分闭环/限制」并登记后续卡，**不得**继续标 `<<MET>>`。
- 下一任务建议：`无需下一步操作`（本卡仍在 r2 返修闭环前，不释放新卡）。

## 自审声明

- 独立上下文 fresh subagent（DSH 派发），未参与 FEA-11-LINEAGE-1 的任何实现、返修或 r1 处置；本报告仅审查 `3c40f7020`（Python 工作树与该 head 一致）。
- 只读仓库：未 commit/push/stash/reset/checkout；未改仓库任何文件；所有测试/探针日志、pytest 缓存规避与报告均写在仓外 `G:\CODEX\New Manga.workspace\FEA-11\review-r2\`。审查期间仓内 `.NET`/FEA-12 的未提交改动与 `c2b40c9f3` 提交均为他人并发工作，非本审查者所为。
- 未触碰真实用户数据/AppData/外部卷/回收站；未引用聊天记录作为事实。
- 报告落盘路径为仓外（按派发指令）；任务卡 frontmatter 期望的 `doc/reviews/FEA-11-LINEAGE-1-r2.md` 由 Lead 在集成处置时落盘。
