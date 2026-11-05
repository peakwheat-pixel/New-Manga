---
task_id: FEA-11-AC4-GAPS-1
reviewer: dsh-fea11-ac4-gaps1-r1（fresh subagent，独立上下文）
reviewer_kind: subagent
review_session_id: 5040f5f1-21c0-4fa0-bb26-dc7668383496
parent_agent_id: session-8db9dae5-49df-4d09-ac62-696f0805a95c
base_commit: 51e139eff
reviewed_head: 2d9a4a219
decision: approved
---

# Review r1：FEA-11-AC4-GAPS-1（AC11-4 证据收口，test-only）

> **审查身份**：独立上下文 fresh subagent，未参与 FEA-11-AC4-GAPS-1 的实现、证据制作、门禁运行或任何返修。会话 `5040f5f1-21c0-4fa0-bb26-dc7668383496`，父会话 `session-8db9dae5-49df-4d09-ac62-696f0805a95c`。`reviewer_kind=subagent`。
> **审查范围**：`base_commit=51e139eff` → `reviewed_head=2d9a4a219`。重点为本卡两个提交 `95815ff7a`（实现：两个测试文件）与 `2d9a4a219`（卡/Handoff/证据）。`eb1e48a62`（Lead 指针转 in_review）与 `d8049fe6e`（FEA-12-CORE closeout）是 base 后的 Lead 文档提交，按范围裁决不计入本卡 allowed_paths 结论；`744daa51b` 更早，不在本卡范围。
> **审查方式**：只读仓库（全程未改受跟踪文件、未 commit/push/stash）；全部复跑、变异、探针与报告写在仓外 `G:\CODEX\New Manga.workspace\FEA-11\review-ac4-gaps-1\`。开始时 `HEAD=2d9a4a219`、`git status --porcelain` 为空；结束时 `HEAD` 不变、工作树仍 clean。

## 0. 结论摘要

**P0=0，P1=0，P2=2（非阻断，closeout 前文字/证据粒度更正），P3=6。decision: approved。**

本卡按 ZCode SCOPE-ADJ-2026-11-05 C 节与卡内冻结口径 1–5 交付了 AC11-4 剩余缺口（并发 apply / DB 失败 / 第三区域 BaseRevision / G4–G11 漂移矩阵 + 16 表零写比较集），且是**真实的判别性测试**，不是空转：

- **AC1** 三条证据（same-op 原 receipt、different-op typed、双独立 stack/连接同一文件 DB）全部实跑通过；我把 `_replay_or_conflict` 的 replay 返回改为 `None`（仓外副本）后 `test_concurrent_same_operation_returns_the_original_receipt_once` **精确变红**（第二个 apply 抛 typed 冲突，`accepted=true` 断言失败）。
- **AC2** 事务中途与最后一步两次 `RAISE(ABORT)` 注入都得到 16 表逐行相等快照 + 重试成功；AC2-c 经**生产装配 + host-control dispatch** 得到 wire 级 `SOURCE_SYNC_STORAGE_FAILED`（`internal`/`retryable=true`、不回显注入文本），并用同一 trigger 下直接 service 调用抛原始 `sqlite3.IntegrityError` 证明注入点在 `BEGIN IMMEDIATE`..`COMMIT` 内、不在 post-commit `_bind_operation_grant`。我把 `except BaseException` 的 `rollback()` 去掉后 AC2-a **精确变红**（快照检出 p1 新 binding / operation / publication 脏写）。
- **AC3** 双分支（`STALE_BASE_REVISION` vs `SOURCE_PLAN_STALE(cause=manual)`）均实跑通过；我删掉 `_migrate_revisions` 的 current 检查后 AC3-a 变红（`DID NOT RAISE SourceImportError`），删掉 `manual_digest` CAS 后 AC3-b/G9 manual 变红。
- **AC4** G4–G11 全部有独立测试，统一 `_full_snapshot` 覆盖卡内冻结口径 4 的 **16 张表**（逐项核对一致）。G9 manual/protection/draft/Run 与 G10 都断言漂移打在**最后一个 base**——我把 `_verify_cas` 的 bases 循环改成 `[:1]` 后 G9 manual 与 G10 **双双变红**，证明该断言有判别力。
- **AC5** 门禁与范围全部可独立复跑：`pytest tests/fea11` **88 passed**；全量 **3183 passed / 10 skipped**；`check.ps1 -TaskPath` 与默认 `check.ps1` 均 **PASS (3 warnings)**；`verify_pins.ps1` **18/18 PASS**；`git diff --name-only 51e139eff..HEAD -- src/ doc/plan doc/contracts apps` **空**。`.NET` 如实 **NOT_RUN**（0 C# 变更），未写 PASS。
- **范围/纪律**：两个卡内 commit 只落在 `allowed_paths`；0 `src/**`/契约/schema/依赖/STATUS/PLAN/LEDGER/reviews 改动；未 push（`origin/main..HEAD=926`、`HEAD..origin/main=0`，HEAD 非 origin/main 祖先）；工作树 clean。
- **证据真实性**：卡面 Canonical Evidence 的 13 个 sha256 pin **全部复算一致**；`baseline-full-pytest.log`（3164/10）与 `full-pytest.log`（3183/10）是两份不同字节的真实日志；88/3183/10、gates、pins、0 diff 均与实跑一致。

**AC 建议判定**：**AC1–AC5 全部 MET**（AC5 由 PARTIAL 恢复 MET，前提是本 Review 被 Lead 采纳）；**AC11-4 可判定 MET**（本卡已补齐 r7 L-5 三项 + G4–G11；G12 按 C-17 §6.2 明文非缺口）。

**closeout 前建议**（非阻断）：更正卡面 AC1-b 判别力一句（与实现者自检/Handoff §5 矛盾，见 P2-1）、补/删 EV 的并发 ×5 循环声明（见 P2-2）；另 6 条 P3 为证据日期/占位符/哈希算法/命令笔误/口径注记，可在 closeout 一并处理。

## 1. 审查对象与独立性

- 开始时 `HEAD=2d9a4a2194510190c9d7288e020b9ae78dc41ced`，与 `reviewed_head` 一致；`git status --porcelain` 为空。
- 本卡提交只有两个：
  - `95815ff7a`（实现）：`tests/fea11/test_source_sync.py` +1240/−1（18 个新用例 + 本地装置）、`tests/fea11/test_source_sync_storage.py` +237（1 个用例）；**无** `src/**`、契约、schema、依赖、conftest 改动。
  - `2d9a4a219`（交付）：`doc/tasks/FEA-11-AC4-GAPS-1.md`、`doc/handoffs/FEA-11-AC4-GAPS-1-handoff.md`、`verification/FEA-11-AC4-GAPS-1/**`（15 files）；全部在 allowed_paths。
- 与 base 之间的其余差异（`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`、`doc/tasks/FEA-12-CORE.md`、`doc/reviews/FEA-12-CORE-r4.md`、`doc/handoffs/FEA-12-CORE-core-py.md`、`verification/FEA-12-CORE/**`）来自 Lead 的 `d8049fe6e`/`eb1e48a62`，按范围裁决不计入本卡。
- 唯一既有代码改动是 95815ff7a 把 `_seed_two_page_source(conn, scratch_dir)` 改为带 `*, legacy_v7_evidence=True` 的签名；默认值保留原行为，既有 69 个 fea11 用例全绿，未改 `conftest.py`。

## 2. AC 判定

| AC | 判定 | 依据（独立复跑/审读） |
|---|---|---|
| **AC1** 并发 apply | **MET** | `test_concurrent_same_operation_returns_the_original_receipt_once`（两响应 `accepted=true`/`state=core-committed`/同 `operation_id`+`request_digest`；`source_operations` 每 plan 恰 1 行；p1 两代、p2 tombstone 一行、总 3 行、publication 1）；`test_concurrent_different_operations_leave_one_commit_and_one_refusal`（恰 1 成功，败方 typed ∈ {`SOURCE_OPERATION_CONFLICT`,`SOURCE_PLAN_STALE`} 且非 `sqlite3.Error`；重放败方请求零写）；`test_two_connection_stacks_commit_exactly_once_on_one_file_db`（`tmp_path` 文件 DB + FK/WAL/busy_timeout=5000、两独立 registry/store/stack、等价 grant 基线断言、恰一次提交、无 `database is locked`、败方重放零写）。三条均为同实例/双栈真实线程，屏障编排、无 sleep；并发三例连续 5 次独立复跑 3 passed ×5。AC1-c 装置是 service seam 防御证据（L1），卡面已如实标注，未宣称 IPC 并发。AC1-d 跨实例 same-op replay 按 Out 不写断言，正确。 |
| **AC2** DB 失败注入 | **MET** | AC2-a/B：真实 `CREATE TRIGGER ... RAISE(ABORT)`；AC2-a 在 p1 已发布后命中 p2 binding INSERT，AC2-b 命中 `commit_operation` 的 `host-authorized→core-committed` UPDATE；两者 apply 抛原始 `sqlite3.Error`（非 typed 业务拒绝），16 表快照与失败前逐行相等，plan 仍 `confirmed`/`applied_at IS NULL`，0 operation/0 publication，移除 trigger 后新 `operation_id` 重试成功。AC2-c：`assemble_production_core(tmp_path)` + `CoreServiceServer.dispatch_request` host-control `ResyncSource`，envelope `code=SOURCE_SYNC_STORAGE_FAILED`/`category=internal`/`retryable=true`/`result=None`，`injected`/`RAISE` 不出现在响应 JSON；16 表零写；同 trigger 下 direct service 调用抛 `sqlite3.IntegrityError`（证明注入点严格在 BEGIN IMMEDIATE..COMMIT，而非 post-commit `_bind_operation_grant`）；移除 trigger 后 wire 重试成功。 |
| **AC3** 第三区域双分支 | **MET** | AC3-a：3 region current r1/r2/r3 + rg3 历史 r3old，plan `migrate_revision_ids=[r1,r2,r3old]` → `STALE_BASE_REVISION`（≠`INVALID_REQUEST`），前两项迁移 + binding + captured_v7 lineage 全部回滚（regions=3、region_revisions=4、lineage=0、rg3 current 仍 r3、16 表相等）；AC3-b：confirm 后 rg3 current → r3new（同 region 新 revision 行），→ `SOURCE_PLAN_STALE(cause=manual)` 且断言**不是** `STALE_BASE_REVISION`、零写、plan confirmed。L2 口径（AC3-a 是非 conforming Host 防御 seam，现实漂移由 AC3-b CAS 拦截）已如实登记。 |
| **AC4** G4–G11 漂移矩阵 + 全表零写 | **MET** | 11 条独立测试 + 统一比较集：G4 `FILE_IDENTITY_CHANGED`；G4b `stale(source)`；G5 `stale(binding)`；G6 `stale(decision)`（plan 仍 stale/decision）；G7 `stale(authorization)`；G8 `SOURCE_GRANT_REVOKED`；G9 manual/protection/draft/Run 均 `stale(manual)`；G10 多项目末项 `stale(binding)` 且两项目零写。每条拒绝均 `_full_snapshot` 前后逐行相等 + `not sqlite3.Error` + plan 状态不被提前提交。G9/G10 断言 `scan["bases"][-1]` 为漂移页（G9=p2、G10=p3），**确实打在最后 base**。`_SNAPSHOT_TABLES` 与卡内冻结口径 4 的 16 表**逐项一致**（pages, page_bindings, source_locations, source_versions, source_entries, source_sync_plans, source_operations, source_binding_publications, source_revision_lineage, regions, region_revisions, reading_progress, step_result_candidates, pipeline_runs, pipeline_run_targets, rendition_cache）。 |
| **AC5** 证据/范围/门禁 | **MET（本 Review 采纳后）** | 独立复跑：fea11 88 passed；全量 3183 passed/10 skipped（与证据一致，基线 3164/10，+19，无新增 skip）；check.ps1 -TaskPath 与默认均 PASS (3 warnings)；verify_pins 18/18；0 域外 diff；.NET NOT_RUN 如实登记（未写 PASS）。新增测试 19（test_source_sync.py +18、test_source_sync_storage.py +1）经 `git show 95815ff7a` 逐函数核对。本 Review 已实际运行新增测试并完成 8 项变异/对照探针，满足卡面 AC5 对独立 Review 的硬要求。 |
| **AC11-4**（跨卡口径） | **可支撑 MET** | AC11-4 正文要求的三类代次、并发 apply、源/绑定/范围/决定/授权漂移、授权撤销/失联、第三区域 BaseRevision、DB 失败、stale 零写比较集，本卡均有判别性证据；r7 L-5 三项（并发/DB 失败/第三区域）已补齐；G12 按 C-17 §6.2 明文非缺口。建议 Lead 在 FEA-11 验收记录中把 AC11-4 标 MET 并注明由本卡承接 L-5（本卡未自行宣告，符合卡面）。 |

## 3. 独立复跑

环境：Windows / PowerShell 7.6.8 / Python 3.14.6 / pytest 9.1.1（与 Handoff 声明一致；`python --version` 实跑确认）。所有命令在 `G:\CODEX\New Manga` 主工作树 `HEAD=2d9a4a219` 上执行。

| # | 命令 | 结果 | 证据 |
|---|---|---|---|
| 1 | `python -m pytest tests/fea11 -q -p no:cacheprovider` | **88 passed, 8 warnings in 2.34s** | EXIT 0；输出与 `logs/fea11-tests.log` 一致（8 warnings 均为既有 `test_source_scan.py` 的 usefixtures 警告） |
| 2 | `python -m pytest tests/fea11/test_source_sync.py tests/fea11/test_source_sync_storage.py -q -p no:cacheprovider` | **28 passed** | EXIT 0（副本基线亦 28 passed） |
| 3 | 并发三例 ×5 独立进程 | **3 passed ×5**（run1–run5 均 0.30–0.33s） | 仓外 `concurrency-5x.log`；无 `database is locked`、无 flake |
| 4 | `python -m pytest tests -q -p no:warnings --tb=no` | **3183 passed, 10 skipped in 240.59s (0:04:00)** | EXIT 0；仓外 `full-pytest-review.log`；与 `logs/full-pytest.log`（3183/10, 236.23s）一致，计数完全相同 |
| 5 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-11-AC4-GAPS-1.md` | **PASS (3 warnings)** | EXIT 0；3 warnings = 14 非终态 Task / STATUS 80% / PLAN 80%，与卡面"登记后最终复核 3 warnings"一致（gates.log 记的是登记前 4 warnings，见 P3-1） |
| 6 | `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS (3 warnings)** | EXIT 0 |
| 7 | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PIN AUDIT: PASS (all 18)** | EXIT 0；C14/C15/C16/C17/FEA01 逐项 OK |
| 8 | `git diff --name-only 51e139eff..HEAD -- src/ doc/plan doc/contracts apps` | **空** | EXIT 0 |
| 9 | `git status --porcelain` / `git rev-parse HEAD` | **空 / 2d9a4a219** | 审查前后一致 |

## 4. 变异反证（独立、仓外副本）

装置：`G:\CODEX\New Manga.workspace\FEA-11\review-ac4-gaps-1\mut\`——把 reviewed head 的 `src/` 与 `tests/fea11/`（conftest + 两个测试文件）复制到仓外，`mutate.py` 从主仓原文件重新复制后再做单一字符串替换；**仓库从未被修改**（每次探针后 `git status` 仍为空）。脚本与日志：`mutate.py`、`mutation-probes-review.log`。

| 探针 | 变异（仓外副本） | 目标用例 | 观察 | 期望/结论 |
|---|---|---|---|---|
| P1 | 删除 `service.py` `_verify_cas` 的 `manual_digest` CAS（保留 regions 投影） | `test_drift_manual_revision_is_plan_stale_manual` | **FAILED：`DID NOT RAISE SourceImportError`** | **RED ✓**（AC4/G9 manual 判别） |
| P2 | 删除 `_migrate_revisions` 的 `region["current_revision_id"] != revision_id` 检查 | `test_third_region_stale_migrate_revision_aborts_the_whole_batch` | **FAILED：`DID NOT RAISE SourceImportError`** | **RED ✓**（AC3-a 判别） |
| P3 | `_verify_cas` 的 `for base in body["bases"]` → `[:1]`（只查第一个 base） | `test_drift_manual_revision_*` + `test_multi_project_final_item_*` | **2 FAILED（均 DID NOT RAISE）** | **RED ✓**（证明 G9/G10 的"最后 base"断言有判别力；只查首个 base 会漏检） |
| P4 | `_verify_cas` reference-set 拒绝前脏写 `UPDATE pages ... p1` + `except BaseException` 改 `conn.commit()` | `test_drift_reference_set_is_plan_stale_binding` | **FAILED：`zero-write baseline drifted ... "pages": 3→3 rows, sort_order 1→8`** | **RED ✓**（16 表快照能检出拒绝路径的脏写；错误码断言本身仍会通过） |
| P5 | P4 + 把 `_SNAPSHOT_TABLES` 的 `"pages"` 删除（改坏比较集） | 同 P4 | **PASSED（1 passed）** | **对照 ✓**：同一脏写下，比较集缺 pages 即**漏检**——证明 G11 的 16 表清单是判别要素，实现者没有用缩水比较集冒充 |
| P6 | `_replay_or_conflict` 的 `return self._dispatch_dto(existing)` → `return None`（移除 same-op replay） | `test_concurrent_same_operation_returns_the_original_receipt_once` | **FAILED（第二个响应非 accepted=true，AssertionError）** | **RED ✓**（AC1-a 的 replay 语义有判别力；与实现者自检 `probe_replay_removed` 一致） |
| P7 | 删除 `apply` 的 `existing_plan_op` 预检 | `test_concurrent_different_operations_leave_one_commit_and_one_refusal` | **PASSED（1 passed）**；败方仍是 `SOURCE_PLAN_STALE`（plan-state CAS 在事务内拦截） | **遮蔽确认 ✓**：卡面 AC1-b 所说"未检查预检会撞 UNIQUE"不成立；该用例的 `not isinstance(sqlite3.Error)` 是**前向防御**断言，真正判别是恰一次提交 + typed 闭集 + 16 表零写。与 `logs/mutation-probes.log`/Handoff §5 的如实登记一致（见 P2-1） |
| P8 | 删除 `_apply_transaction` 的 `except BaseException: conn.rollback()` | `test_mid_transaction_storage_failure_rolls_back_the_whole_batch` | **FAILED：快照检出 p1 新 binding / source_locations / source_versions / entries / operation / publication 全部脏写** | **RED ✓**（AC2-a 回滚断言有判别力） |

结论：8 项探针中 **6 项 RED + 2 项有意义的对照/遮蔽确认**；AC1/AC2/AC3/AC4 与 G11 比较集都至少有一条独立变异能打红对应测试。"被更强 CAS 遮蔽的 2 项"（实现者自检的 conflict-precheck / double-guard）**没有被写成 RED**：实现者日志标 MASKED / 无 sqlite error，EV 表格写"被更强 CAS 遮蔽（如实登记）"，我的 P7 独立复现亦为 PASS（遮蔽），口径如实。

## 5. 证据真实性核对

1. **sha256 pin 复算**：卡面 Canonical Evidence 表 13 个带 sha256 的条目（AC-MATRIX/EV/RESOURCE/DELIVERY/changed-files/baseline/fea11-tests/gaps1-tests/full-pytest/mutation-probes/scope-diff/dotnet-not-run/gates）**全部与工作树字节一致（0 mismatch）**；`tests/fea11/test_source_sync.py`、`test_source_sync_storage.py` 两项在表中以 `-` 表示未 pin（指向 `95815ff7a`），与卡面写法一致。
2. **日志与实跑一致**：`logs/fea11-tests.log` = 88 passed / 8 warnings（与独立复跑逐字一致）；`logs/fea11-gaps1-tests.log` = 28 passed；`logs/full-pytest.log` = 3183 passed / 10 skipped；`logs/baseline-full-pytest.log` = 3164 passed / 10 skipped（与 full 日志**不同哈希**，不是复制品）；`logs/gates.log` 的 5 条命令（check×2/pins/0-diff/fea11/28/full/NOT_RUN）与卡面/EV 表格一致。
3. **gates.log 的 SOURCE_PIN/CANONICAL**：卡面 Canonical Evidence 已登记 `EV-FEA11GAPS1-GATES`（CANONICAL）与 PROBE/BASELINE（SOURCE_PIN）；`check.ps1` 的"evidence_dir 含未登记过程文件（gates.log）"警告在登记后消失（独立复跑 3 warnings 中已无该项），与卡面"登记后最终复核 3 warnings"自洽。
4. **变异记录如实**：`logs/mutation-probes.log` 3 项 RED（replay/per-item commit/manual+protection CAS）+ 2 项遮蔽（conflict precheck / double guard），EV §4 与 Handoff §5 均已如实说明；独立 P7 复现了第一项遮蔽，未见"把遮蔽写成 RED"。
5. **16 表比较集**：测试文件 `_SNAPSHOT_TABLES` 与卡内冻结口径 4 逐项一致；P5 证明其表清单是判别要素而非装饰。
6. **证据目录/隔离根**：`verification/FEA-11-AC4-GAPS-1/**` 与卡面引用一致；仓外隔离根 `G:\CODEX\New Manga.workspace\FEA-11-AC4-GAPS-1\` 被 RESOURCE-MANIFEST 登记为 `PRESERVE_REFERENCED`，未复用/复写 FEA-11 tracked 证据。

## 6. 范围与纪律

- **allowed_paths**：`95815ff7a` 只改 `tests/fea11/test_source_sync.py`、`tests/fea11/test_source_sync_storage.py`；`2d9a4a219` 只改 `doc/tasks/FEA-11-AC4-GAPS-1.md`、`doc/handoffs/FEA-11-AC4-GAPS-1-handoff.md`、`verification/FEA-11-AC4-GAPS-1/**`。均在本卡 allowed_paths 内。
- **0 域外 diff**：`git diff --name-only 51e139eff..2d9a4a219 -- src/ doc/plan doc/contracts apps` 为空；无 schema/migration/依赖/命令表/错误闭集改动；`tests/fea11/conftest.py`、`tests/core/**` 未改。
- **Lead 文档隔离**：base 后的 `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`、FEA-12-CORE 文档与证据均由 `d8049fe6e`/`eb1e48a62` 引入（Lead 提交，出版本卡范围）；本卡两 commit 未触碰。
- **未 push**：`git rev-list --count origin/main..HEAD = 926`，`HEAD..origin/main = 0`，`2d9a4a219` 不是 `origin/main` 祖先；main 无 upstream。未创建 linked worktree（`git worktree list` 无本卡新增项）。
- **工作树**：审查开始/结束 `git status --porcelain` 均空；未 commit/stash/push。

## 7. Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| R1-01 | **P2** | `doc/tasks/FEA-11-AC4-GAPS-1.md:82`（AC1-b 判别力句） | 卡面写"若第二事务在 `take_confirmed` 前未检查 `existing_plan_op`，会撞 UNIQUE 抛未包装 `IntegrityError`"，但独立变异 P7 证明：移除预检后仍被事务内 plan-state CAS 拦截为 `SOURCE_PLAN_STALE`，**不会撞 UNIQUE**。该句与实现者自检 `logs/mutation-probes.log`、Handoff §5"被更强 CAS 遮蔽"及 EV §4 矛盾，属判别力描述夸大（不影响 AC1 结论：测试仍覆盖 typed 闭集 + 恰一次提交 + 16 表零写）。 | 仓外 `mutation-probes-review.log` P7：`1 passed`；败方 `SOURCE_PLAN_STALE` | 把 AC1-b 判别力句改为："预检被事务内 plan-state/reference-set CAS 遮蔽；`not isinstance(sqlite3.Error)` 是前向防御断言；真正判别是恰一次提交 + 失败方 typed 闭集 + 16 表零写。"无需改测试/实现 | open（非阻断，closeout 前文字更正） |
| R1-02 | **P2** | `verification/FEA-11-AC4-GAPS-1/EV.md:16,35`；`AC-MATRIX.md` AC5 行 | EV §1 第 3 行声明"×5 → 28 passed ×5（并发稳定性）"，日志列写"本 EV §3"；但 EV §3 只有散文声明，`logs/fea11-gaps1-tests.log` 仅 2 行（单次 28 passed），没有 5 次循环的 artefact。按 Q-009 证据纪律，这属于"以散文代替判别力 artefact"。 | 独立复跑并发三例 ×5 均 3 passed（`concurrency-5x.log`），证明稳定性事实成立，但 Owner 证据粒度不足 | 二选一：① 把 5 次循环输出补入 `logs/` 并重算 pin；② 把 EV 改为"Reviewer 独立复跑 5 次通过"并删除无 artefact 的 ×5 声明 | open（非阻断） |
| R1-03 | P3 | `logs/gates.log:2` | 日志头 `date: 2026-11-05`，条目时间戳为 `2026-11-06T00:10:21+08:00`；两条 check 记录为 4 warnings（含 gates.log 自身未登记项），卡面所称"登记后最终复核 3 warnings"未入库。 | 独立复跑 check.ps1 两种均 PASS (3 warnings) | closeout 时在 EV/gates 追加一条最终复核记录（或注明 Review 已独立复核） | open |
| R1-04 | P3 | `verification/FEA-11-AC4-GAPS-1/DELIVERY-MANIFEST.json:10` | `evidence_commit: "SELF（本文件所在提交…）"` 是占位符而非具体 commit，削弱可追溯性。 | `git show --stat 2d9a4a219` | closeout 时填 `2d9a4a219`（或最终证据提交） | open |
| R1-05 | P3 | `RESOURCE-MANIFEST.json:20` | 仓外临时根的 `sha256` 未说明算法/输入（目录哈希不可按文件 sha256 复算），无法独立验证。 | 无 | 改为"目录文件清单 + 各文件 sha256"或注明哈希算法 | open |
| R1-06 | P3 | `logs/dotnet-not-run.md:4` | 理由命令写作 `git diff --name-only 51e139eff..HEAD -- apps docs`，未包含 `src/`（C# 均位于 `apps/`，结论不受影响）；建议与卡面/门禁命令保持同一口径。 | 卡面/scope-diff 用 `-- src/ doc/plan doc/contracts apps` | 统一为 `-- apps`（C#）或卡面同款命令 | open |
| R1-07 | P3 | `changed-files.txt:43` | §3"明确未触碰 doc/STATUS.md、doc/REBASELINE_PLAN.md、doc/TASK_LEDGER.md、doc/reviews/**"与 `logs/scope-diff.log` 的 all-diff 列出这些文件并存（差异由 Lead 的 `d8049fe6e`/`eb1e48a62` 引入）。建议注明"差异来自 Lead 提交，本卡未触碰"，避免读者误判 Owner 越界。 | `logs/scope-diff.log:4-14` | 加一行来源注记 | open |
| R1-08 | P3 | `AC-MATRIX.md` AC1-b/AC1-c 行 | "失败前快照 = 失败后快照（确定性复探）"措辞不精确：并发失败瞬间无法取快照，实际是"winner 结算后重放败方请求零写"。 | 测试 `test_concurrent_different_operations...:1153-1161`、`test_two_connection_stacks...:1267-1277` | 改为"并发结算后重放失败方请求零写" | open |

**P0/P1：无。** 无阻断项；R1-01/R1-02 建议在 closeout 前一并处理（不影响 approved）。

## 8. 架构/验证两面结论与残余风险

- **Architecture**：本卡 test-only，0 `src/**`/契约/schema/依赖变更，分层与依赖方向无影响；测试直接使用生产 `SourceSyncStore`/`SourceReadGrantRegistry`/`build_source_sync_stack`/`ThreadRoutedConnection`/`assemble_production_core`，AC2-c 走真实 host-control dispatch（进程内，非真实 IPC，属 FEA-11 L-9/Out）。无拒绝审计 receipt 写入（C-17 §6.2）。
- **Verification**：88 / 3183/10 / 28 / 5×3 并发 / check×2 PASS / pins 18/18 / 0 diff / 8 项变异探针全部实跑，结果见 §3–§4。
- **残余风险（L1–L4 如实，全部保留）**：
  - L1：生产 Core 请求循环单线程；AC1-c 是 service seam 防御证据，非端到端 IPC 并发；AC1-a/AC1-b 同实例受 `RLock` 串行化，本质是"串行 replay/冲突"而非并行竞争。
  - L2：`STALE_BASE_REVISION` 只在非 conforming plan 下可达；现实漂移由 `SOURCE_PLAN_STALE(cause=manual)` 拦截。
  - L3：`_bind_operation_grant`（COMMIT 之后）失败不在回滚证据内，是 post-commit 残余风险；AC2-c 已显式避免用该点冒充回滚。
  - L4：DB 失败用 SQLite trigger 模拟，不等于真实磁盘满/IO 错误；commit-time IO 失败未模拟。
  - 补充：AC1-c 的 `_materialize_target_version` 预写目标版本以绕开每栈隔离的 live-scan cache，属 seam 装置的一部分（已标注 L1）；G11 快照是辅助断言，主判别来自错误码/行数；P5 证明若比较集缺表会漏检，当前 16 表完整。
- **G12**：拒绝审计按 C-17 §6.2 明文禁止，**非缺口**，不登记 limitation（口径正确）。

## 9. closeout 建议

1. **decision**：`approved`（P0=0/P1=0；R1-01/R1-02 为 P2 非阻断，建议随 closeout 文字更新；R1-03–08 为 P3）。
2. **AC5 定稿**：把 `doc/tasks/FEA-11-AC4-GAPS-1.md` 的 AC5 改为 `[x] ... <<MET>>`，理由写"独立上下文 Review r1（`5040f5f1-21c0-4fa0-bb26-dc7668383496`，reviewer_kind=subagent）已实际运行新增测试并完成 8 项负向/变异探针；fea11 88、全量 3183/10、check×2 PASS、pins 18/18、0 域外 diff；`.NET` NOT_RUN（0 C# 变更）"。
3. **AC11-4**：判定 **MET**，在 FEA-11 卡/验收记录注明"由 FEA-11-AC4-GAPS-1 承接 r7 L-5 与 G4–G11"，并保留 G12 非缺口说明；FEA-11 AC11-4 的其余子项（三类代次、单 plan/多项目原子单元）已由 FEA-11 既有交付覆盖。
4. **delivery_head**：建议 closeout 取 **`2d9a4a219`**（含卡/Handoff/证据的最终交付提交），并在卡面同时保留实现 head `95815ff7a`；若 Lead 坚持本卡既定"delivery_head 仅指向实现提交"口径，则保留 `95815ff7a`，在 Closeout Record/证据表写明交付提交 `2d9a4a219`。两种写法都需 card/Handoff/证据三处一致。
5. **resource_closeout_status**：仓外隔离根按 `PRESERVE_REFERENCED` 处理（无删除/迁移）；若删除，先确认 EV §4 引用可归档并更新 RESOURCE-MANIFEST。`closeout_counts` 保持 0。
6. **Review 落盘**：Lead 将本报告落到 `doc/reviews/FEA-11-AC4-GAPS-1-r1.md`（含 frontmatter `reviewer_kind: subagent`、session/parent id）；更新 `TASK_LEDGER`/`STATUS`/`REBASELINE_PLAN` 指针（Lead 专属）。
7. **可选**：closeout 时把 R1-01/R1-02 的文字更新与 `evidence_commit` 回填一并提交；无需额外判别性测试（现有测试已足够）。

## 10. 返回 decision 与摘要

**decision: approved。** P0=0、P1=0、P2=2（卡面 AC1-b 判别力句与自检/Handoff 矛盾；EV 并发 ×5 无 artefact，均为非阻断文字/证据粒度问题）、P3=6。AC1–AC4 MET，AC5 经本 Review 恢复 MET，AC11-4 可判定 MET（由 Lead 定稿）。独立复跑：fea11 **88 passed**、全量 **3183 passed/10 skipped**、并发三例 ×5 全绿、`check.ps1` 两种 **PASS (3 warnings)**、`verify_pins` **18/18 PASS**、0 域外 diff；`.NET` 如实 NOT_RUN。变异反证 8 项：6 项 RED（replay 移除→AC1-a、manual CAS 移除→G9、migrate current 移除→AC3-a、bases 只查首个→G9/G10、回滚移除→AC2-a、reference-set 脏写→G11 快照）＋2 项有意义的对照/遮蔽确认（弱化 16 表比较集→漏检；移除 conflict 预检→被 plan-state CAS 遮蔽，与实现者自检如实登记一致）。卡面 13 个 sha256 pin 全部复算一致；两个卡内 commit 均在 allowed_paths；未 push；工作树 clean。建议 closeout：AC5 恢复 MET、AC11-4 MET、delivery_head 取 `2d9a4a219`（或保留 `95815ff7a` 并记录交付提交），R1-01/R1-02 随 closeout 文字更新。
