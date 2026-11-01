---
document_id: FEA-00A-IMPL-scope-r1
kind: independent_scope_review
reviewer: fea00a-scope-reviewer
reviewer_kind: subagent
reviewer_source: "DSH Agent Teams durable teammate `fea00a-scope-reviewer`（role=teammate，context=fresh，由 DSH（Lead）以独立上下文派发；子任务标识形式 = teammate target 名 + 本报告 frontmatter；未使用独立 CLI session ID，未参与该 Task 的任何实现/起草）"
reviewer_independent: true
reviewed_by_implementer: false
author: dsh-lead
base_commit: 419f891c0
reviewed_head: 419f891c0
reviewed_head_full: 419f891c0122f70bd811379a94d55905b309c2a3
repository: G:/CODEX/New Manga
scope: "FEA-00A-IMPL-1 范围冻结（写域、AC1–AC10、V1–V9、L-1/L-2/L-5 判定、禁止范围、指针一致性）；不构成实现验收（实现尚未开始）"
decision: changes_requested
verdict: changes_requested
p0_count: 0
p1_count: 3
p2_count: 10
checkps1: "默认（当前 Task doc/tasks/FEA-00A-IMPL-1.md）：PASS (2 warnings)，EXIT=0"
verifypins: "PIN AUDIT: PASS (all 15)，EXIT=0"
captured_at: 2026-11-01T21:30:29+08:00
captured_by: fea00a-scope-reviewer
---

# Review：FEA-00A-IMPL-1 范围冻结（base/reviewed_head = `419f891c0`）

**结论：`changes_requested`（P0 × 0 / P1 × 3 / P2 × 10）。**

本次复核**只针对范围冻结材料**（被审 head `419f891c0`），不评价实现（实现尚未开始），不构成实现验收；即使后续复核改为 `approved`，也不等于 Task 完成，仍需实现、独立实现复核、集成与 AC 证据闭环。

## 0. 复核对象、方法与环境

**被审材料（全部在 `419f891c0`）**

1. [`doc/tasks/FEA-00A-IMPL-1.md`](../tasks/FEA-00A-IMPL-1.md)（范围冻结卡：写域、AC1–AC10、V1–V9、L 判定、禁止范围）
2. [`doc/reviews/ADJ-2026-11-01-FEA-DECISIONS.md`](ADJ-2026-11-01-FEA-DECISIONS.md) 末尾「追加裁决 U-13」（D1–D4）
3. [`doc/plan/FEA-00A_PREP.md`](../plan/FEA-00A_PREP.md)（A1–A7、§4.1 token 契约、§4.2 staged 行清理归属、§5/§6、§7 D1–D4）
4. [`doc/STATUS.md`](../STATUS.md)、[`doc/REBASELINE_PLAN.md`](../REBASELINE_PLAN.md)、[`doc/TASK_LEDGER.md`](../TASK_LEDGER.md)（指针一致性）
5. 方案原文 [`doc/design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md`](../design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md) §15.5（`:905`–`:910`，FEA-00a 条目 `:907`）、§15.6 FEA-00a 行（`:919`）
6. 只读源码现状：`src/infrastructure/providers/step_writes.py`、`src/infrastructure/providers/handlers.py`、`src/infrastructure/sqlite/pipeline.py`、`src/application/tasks/service.py`（另加读 `src/infrastructure/sqlite/schema.py`、`connection.py`、`library.py`、`src/infrastructure/pipeline/assembly.py`、`src/bootstrap/core_assembly.py`、`src/domain/tasks/models.py`、`src/application/tasks/store.py`、`src/infrastructure/filesystem/managed_storage.py` 的相关段落作为判定证据）
7. 既有评估复核 [`doc/reviews/FEA-00A-PREP-r1.md`](FEA-00A-PREP-r1.md)（用于确认冻结稿是否落实其 C1–C4 前置）

**环境与辅助证据（只读）**

- `git rev-parse HEAD` = `419f891c0122f70bd811379a94d55905b309c2a3`；工作区 clean（`git status --short --branch` 仅 `## main`）；复核期间未 checkout、未改源码/卡/STATUS/PLAN/LEDGER、未 commit、未 push，仅写本报告。
- `git diff --stat 15aa7bf3b 419f891c0 -- src tests apps` **为空**；`git diff --stat 6b8469a80 419f891c0` 仅 5 个 `doc/**` 文件。→ 评估快照 `15aa7bf3b` 的源码/测试行号在 HEAD 有效；冻结提交未触代码。
- `pwsh -NoProfile -File tools/governance/check.ps1` → `Governance check: PASS (2 warnings)`，EXIT=0（当前 Task 即本卡；2 warnings = 11 个非终态 Task + STATUS 达预算 80%）。
- `pwsh -NoProfile -File tools/governance/verify_pins.ps1` → `PIN AUDIT: PASS (all 15)`，EXIT=0。
- 引用抽查：卡内 `../plan/FEA-00A_PREP.md`、`../reviews/FEA-00A-PREP-r1.md`、`../reviews/ADJ-2026-11-01-FEA-DECISIONS.md` 三个相对链接均存在（`check.ps1` PASS 亦覆盖当前 Task 相对引用）。
- 评估 G1–G7 的关键行号抽查属实：`step_writes.py:195–281`（`_persist`）、`schema.py:379–394`（候选表 DDL）、`pipeline.py:516–528`（候选写入）、`library.py:571`（purge 清理）；G7 的 8 个 blast-radius 文件实测为 `tests/core/test_bootstrap.py`、`tests/core/test_page_catalog_modes.py`、`tests/pipeline/test_regionless_rebinding.py`、`tests/providers/t111_support.py`、`tests/providers/test_detect_handler.py`、`tests/providers/test_full_chain.py`、`tests/providers/test_handlers_pipeline.py`、`tests/providers/test_retype_redetect_persistence.py`，与 `PREP:30` 清单逐名相符。

**未覆盖**：未运行产品测试（无实现可测）；未复算 `verify_pins` 之外的契约语义；未重审 PREP-r1 的其它结论；未访问用户数据、未触碰冻结契约字节。

---

## 1. D1–D4 映射完整性（检查点 1）

| 裁决 | 卡内落点 | 判定 | 说明 |
|---|---|---|---|
| **D1 = ②** region + artifact（`media_artifacts.current_revision_id`、`publish` 的 `artifact_revisions` 行/落盘文件） | AC6（卡 `:69`）、写域（卡 `:56` + `allowed_paths` `:30`–`:32`）、D1 行（卡 `:49`） | **覆盖，但有缺口** | AC6 三个对象都在：指针、`publish` 的 revision 行、落盘文件；`handlers.py:962` 调用点已点名且实测准确（`_commit_artifacts` 内 `adopt_current`，`handlers.py:943–967`）。缺：①`ArtifactStepWriter._artifact_id` 在 prepare 内 `INSERT INTO media_artifacts` 并 `commit()`（`step_writes.py:491–514`，commit 在 `:513`）不在 AC6/AC4 覆盖；②文件 staging 无协议/无断言（见 P1-2）。 |
| **D2 = ②** 允许改 `src/application/tasks/service.py`，必要时可重设计构件 | 写域 `src/application/tasks/**`（卡 `:32`、`:50`、`:56`）；AC9 登记（卡 `:72`） | **覆盖** | 与 ADJ U-13 `:61` 记录一致；AC9 要求 Handoff 逐项写「为什么必须改 / 不改的替代方案 / 影响面 / 回退方式」+ 构件重设计前后接口对照，满足用户条件。 |
| **D3 = ①** 复用 `step_result_candidates`、无 schema/迁移 | 卡 `:51`、`:59`、`:104`（禁改 schema.py/migrations）；AC2（`:65`）引用评估 §4.2 | **覆盖，但可执行性不足** | 复用对象、禁令、清理归属引用都在。但 §4.2 仅概念化（"超期"无定义、"abandoned 或删除"未定），且与 Run 全量重写级联冲突（P1-1、P2-1）。 |
| **D4 = L2 + 真实生产 assembly** | D4 行（`:52`）、AC8（`:71`）、V 矩阵（`:87–:97`） | **被弱化** | ADJ U-13 `:63` 明文「AC8；**V1–V9 全部真实 assembly**」，卡内 `:52`/`:71` 均写 **V1–V8**，V9（artifact）被排除出真实 assembly 要求，AC6 也未引用 V9 → **P1-3**。 |

**是否超出用户裁决**：AC/写域主体未超出 D1–D4；但 `allowed_paths` 的精度有两处越界嫌疑（把用户裁决记录与过宽的 `tests/**` 纳入实现写权，见 P2-6），不属于 AC 范围扩张但应在释放前收窄。

## 2. 写域 vs AC 自洽（检查点 2）

**覆盖到位**：`src/infrastructure/providers/**`（`step_writes.py`、`handlers.py:962` adopt 调用点）、`src/infrastructure/sqlite/pipeline.py`（`commit_step` seam）、`src/application/tasks/**`（D2 授权）、`tests/**`、`verification/FEA-00A-IMPL-1/**`（同时满足协议 §4.2 对 `evidence_dir` 的显式要求）、`doc/handoffs/FEA-00A-IMPL-*.md`（实现交接需要，已列入）。缺陷位置与写域对得上：`_persist`（`step_writes.py:195–281`）、`publish`（`:339–354`）、`adopt_current`（`:421–459`）、`commit_step`（`pipeline.py:742–800`）、失败分支（`service.py:730–789`）。

**缺口（P1-2 核心）**：D1=② 的 artifact 文件 staging 若要在 seam 内完成，最自然的接线点不在写域：

- `SqliteTargetCatalog.__init__(conn)` 只有连接（`pipeline.py:690–694`），由 `src/infrastructure/pipeline/assembly.py:36–37` 构造；该文件**不在** `allowed_paths`（且属 FEA-10 写域，方案 `:931`）。
- 真实生产 assembly 在 `src/bootstrap/core_assembly.py:1336–1341` 构造 `RegionStepWriter/ArtifactStepWriter` 并注入 handlers；该文件**不在** `allowed_paths`。
- 若构件重设计需要新增 storage port 方法（`src/ports/repositories/storage.py`）或 managed storage 行为（`src/infrastructure/filesystem/managed_storage.py`），同样不在写域。

**其它可能缺项（建议在释放前明确"不需要"或列入写域）**：`src/domain/tasks/models.py`（`StepResult`/`StepResultCandidate` 定义 `:348–356`、`:372–382`）；若 D2 的"重新设计构件"需要改这两个模型，则同样越界，且可能触发 L-2（见 P2-9）。

**写域过宽（P2-6）**：`doc/reviews/ADJ-2026-11-01-FEA-DECISIONS.md`（卡 `:28`）是用户裁决记录，不应给实现 Owner 写权；`tests/**`（`:33`）无收窄，与方案 §15.6 `:919`「`tests/` 内明确测试」不一致；`doc/reviews/FEA-00A-IMPL-*.md`（`:27`）是 Reviewer 产出，Owner 不应改。

## 3. 与评估 A1–A7 / §4.1 / §4.2 的一致性（检查点 3）

### 3.1 A1–A7 → AC1–AC7

| 断言 | AC | 判定 |
|---|---|---|
| A1 三处零变化（`PREP:40`） | AC1（卡 `:64`） | **覆盖**：7 类注入逐类列出（revision 冲突 / Lock / `STALE_RUN_SNAPSHOT` / DB 失败 / pause / cancel / prepare 后崩溃重启），三处对象与"与 prepare 前完全相同"都在；可参数化机械核验。 |
| A2 候选可诊断（`PREP:41`） | AC2（`:65`） | **部分覆盖**：失败候选字段（reason/status/base_revision_id/payload_json）可查，services 路径已存在（`service.py:764–786`，`StepResultCandidate` 默认 `status="pending"`，`models.py:372–382`）。但 prepared 行语义/清理归属只以"按评估 §4.2 落实"承载，未落成可机械断言，且与 Run 重写级联冲突（P1-1/P2-1）。 |
| A3 成功同事务（`PREP:42`） | AC3（`:66`） | **覆盖但观测手段未定**：同一事务可由 `commit_step` 内 `persist()` 与单次 commit 断言（`pipeline.py:794–796`、`service.py:744–750`）；"无可观察中间态"需固定观测方式（P2-8）。另：候选 resolved 同事务受 P1-1 级联影响。 |
| A4 prepare 不触 live（`PREP:43`） | AC4（`:67`） | **覆盖不完整**：grep 清单只列 `UPDATE regions`/`media_artifacts`/`INSERT region_revisions`，漏 artifact 侧 `INSERT INTO artifact_revisions`（`step_writes.py:364–393`）、`INSERT INTO media_artifacts`（`:499–513`）、`storage.publish`（`:350`）→ P2-2。token=真实 revision id 已写入（`:67`，§4.1 `PREP:64–72`），与 `models.py:355`、`store.py:215/236` 的快照语义一致。 |
| A5 重启可判定（`PREP:44`） | AC5（`:68`） | **受 P1-1 阻塞**：`prepared` 行在 `_write_run`（`pipeline.py:433` DELETE `pipeline_runs` + `schema.py:381–382` `ON DELETE CASCADE`）下会被级联删除，`recover_running_runs` 的 `_persist`（`service.py:1094–1110`）恰好触发；当前 AC5 的"重启后 prepared 行可识别"按现设计不可验证。 |
| A6 artifact（`PREP:45`） | AC6（`:69`） | **映射完整、机制缺失**：指针/行/文件三对象与 `handlers.py:962` 都在；但"文件同事务 adopt"对文件系统不成立，staging 位置/顺序/崩溃残留清理未定义（P1-2）；`_artifact_id` 行创建未覆盖（P2-2）。 |
| A7 §15.6 出口（`PREP:46`） | AC7（`:70`） | **覆盖**：①关闭新写入入口（结构断言）+②旧库只读核验、保留备份与候选、证据入 `verification/` 都在；②缺具体核验程序（P2-1 合并项）。 |

### 3.2 token 契约（§4.1）

- 卡 AC4 `:67` 明确 "token = prepare 预生成的真实 revision id"；§4.1（`PREP:64–72`）给出 uuid 生成、候选行为键、`revision_updates={"region": <id>}`、seam 按 id 找回并同事务插行/写 text/翻指针，依据是 `regions.current_revision_id` 与 `region_revisions` 的延迟复合 FK（`pipeline.py:769–771` 直接写指针值）与内存快照（`store.py:215/236`）。源码现状支持：`_persist` 已在写前生成 `revision_id = uuid.uuid4().hex`（`step_writes.py:204`），handler 已把 run/step 上下文传给 writer（`handlers.py:438–439`、`:524–525`）。→ **PASS**（安全冻结的一部分）。

### 3.3 prepared 行 / 失败候选的语义与清理归属（§4.2）

- §4.2（`PREP:74–80`）定义了 prepared=未 seam 暂存、失败候选=seam 拒绝后的诊断记录，以及两个扫除点（run 启动清理超期 prepared；`commit_step` 失败分支置 `abandoned` 或删除 + `resolved_at`）。
- 卡 AC2 仅引用"按评估 §4.2 落实"，没有把状态机/阈值/扫除点写成断言；且与源码实际持久化模型冲突：Run 每次 `_persist` 会 `DELETE FROM pipeline_runs`（`pipeline.py:433`）→ FK 级联（`schema.py:381–382`、`:523–524`，`connection.py:319` `foreign_keys=ON`）删除全部候选行，再按 `run.candidates` 重建（`pipeline.py:516–528`）。因此 prepare 直插的 `prepared` 行会在：(a) 成功 seam 的 `persist`（`service.py:744–750` → `pipeline.py:794–796`）；(b) seam 失败后的 `_persist`（`service.py:764–786`）；(c) 重启 `recover_running_runs` 的 `_persist`（`service.py:1094–1110`）；(d) 并发 `control_run` 的 pause/stop `_persist`（`service.py:1011–1012`、`:1023–1027`）被级联删除。→ **P1-1 + P2-1**。

### 3.4 V1–V9 覆盖

- 7 类注入：V1（revision 冲突）、V2（Lock）、V3（`STALE_RUN_SNAPSHOT`，`pipeline.py:647`）、V4（DB 失败）、V5（pause/cancel）、V6（崩溃+重启）、V7（成功）、V8（并发）、V9（artifact）——**结构上齐全**，与 §15.5 条目对齐。
- 但 V9 未纳入"真实 assembly"要求（P1-3）；V5 的 pause/cancel 注入点在现有生产路径没有 seam 前检查（`service.py:900–960` 只在 unit 边界；`commit_step_result` `:730–790` 不检查），且并发 pause 的 `_persist` 本身会级联删除 prepared 行 → V5 的"候选保留可诊断"按现设计不成立（P2-4）。

## 4. L-1 / L-2 / L-5 判定（检查点 4）

| 保留项 | 判定 | 复核意见 |
|---|---|---|
| **L-1** 四表 DDL 未冻 | **NOT_APPLICABLE 成立** | L-1 指 `source_entries` / `page_bindings` / `source_sync_plans` / `source_operations` 四表（[FEA-C11_IMPL_PREREQS](../plan/FEA-C11_IMPL_PREREQS.md) `:24`），本卡复用既有 `step_result_candidates`（DDL 见 `schema.py:379–394`、v5 重建 `:521–539`，`status` 无 CHECK），且 D3 明文禁改 `schema.py`/migrations（卡 `:51`、`:104`）。再触发条件方向对，但未覆盖"给候选表加列/CHECK/索引"（P2-9）。 |
| **L-2** M2-C1 字节修订 | **NOT_APPLICABLE 成立** | 不新增/修改 wire 码表与白名单；`StepResult.revision_updates` 既有（`models.py:355`）；失败码沿用 `INPUT_REVISION_CHANGED`/`LOCK_CHANGED`/`DB_FAILED`/`TARGET_NOT_FOUND`（`service.py:764–789`）。再触发条件未覆盖"构件重设计使 prepared/候选状态进入 Host 投影或 StepResult 的 wire 可见语义"（P2-9）。 |
| **L-5** 整库恢复独占锁 | **NOT_APPLICABLE 成立** | 不触备份/恢复/维护互斥；AC7② 是"旧库只读核验"，只读不触发 SC-17。建议在 AC7② 明确"保留备份"= 不删除既有备份（不创建/不恢复），以免误触 L-5（P2-9）。 |

卡内 `:83` 已引用 `FEA-C11_IMPL_PREREQS §0` 禁则（"不适用不等于豁免"）✓。

## 5. AC 可验证性与诚实性（检查点 5）

| AC | 可机械核验的断言 | 判定 |
|---|---|---|
| AC1 三处零变化 | 7 类注入 × 三处（text/pointer/行数）与 prepare 前快照比对 | **可核验**（若 V5 注入方式固定，P2-4） |
| AC2 候选可诊断 + 清理归属 | 失败候选字段查询可核验；prepared 行状态机/扫除点为引用式描述 | **部分可核验**（P1-1/P2-1） |
| AC3 成功同事务 | 单事务断言可做；"无中间可观察态"缺观测方法 | **部分可核验**（P2-8；候选 resolved 受 P1-1 影响） |
| AC4 prepare 不触 live | grep/结构断言可做；但禁写清单不含 artifact 写面 | **部分可核验**（P2-2） |
| AC5 重启可判定 | 崩溃+重启测试可做；prepared 行存续性受级联破坏 | **当前不可达**（P1-1） |
| AC6 artifact 零变化 | 指针/行/文件三对象齐；文件 staging 无协议、无断言 | **部分可核验**（P1-2；`_artifact_id` 缺 P2-2） |
| AC7 §15.6 出口 | ①结构断言可做；②旧库只读核验程序未固定 | **部分可核验**（P2-1 合并项） |
| AC8 回归 + 真实 assembly | 8 文件对照可做；"真实生产 assembly"未定义入口；其中 `tests/providers/t111_support.py` 是 helper 无 outcome（`PREP:30` 清单） | **部分可核验**（P1-3、P2-3） |
| AC9 D2 改动登记 | Handoff 文档检查 | **可核验** |
| AC10 独立复核 | 两份 Review 报告 + P0/P1 计数 | **可核验** |

**诚实性**：10 条 AC 全部为 `[ ]` + 非空 `<<PARTIAL: 原因>>`，无 `MET`、无"未执行标通过"；`canonical_evidence_status: pending`、证据表空表——符合未释放 Task 的诚实状态。lifecycle v3 规则（协议 §4.3）下 `[ ]`+`PARTIAL` 组合合法，且 `proposed` 尚不触发 in_review 门禁；当前标记方式**合规、诚实**。

**空洞风险（必须收口）**：AC6 的"落盘文件"、AC2 的"prepared 清理归属"、AC7② 的"旧库只读核验"、AC8 的"真实生产 assembly"四处存在"实现后可被标 MET、但无法机械否证"的风险；P1/P2 处置前不能把本卡视为可执行冻结。

## 6. 边界与禁止范围（检查点 6）

- 明确禁止：冻结契约字节（15 份 pin，卡 `:59`/`:103`）、`G-DELETE-IMPL` 状态、用户数据、push、schema/迁移、FEA-03/FEA-10 其它功能、fake executor/桩（卡 `:59`–`:60`、`:103`–`:106`）——**覆盖完整**。
- 机械旁证：`verify_pins.ps1` 15/15 PASS；冻结提交 `git show 419f891c0 --stat` 仅 5 个 `doc/**`，未触冻结契约/代码；`git diff 6b8469a80 419f891c0` 无 `src/**`、`tests/**`、`apps/**`。
- 需补：`allowed_paths` 把 `doc/reviews/ADJ-2026-11-01-FEA-DECISIONS.md` 纳入实现写权（P2-6）；AC7②"保留备份"与 L-5 的口径澄清（P2-9）。

## 7. 指针一致性（检查点 7）

| 位置 | 内容 | 与卡 `status: proposed`（卡 `:6`）一致？ |
|---|---|---|
| `STATUS.md:7` | 当前 Task = FEA-00A-IMPL-1 `proposed`；下一候选写"本卡范围复核通过 → `ready` 交 Codex" | **一致**（条件式表述，无"已释放"） |
| `REBASELINE_PLAN.md:14` | 表格行 = **proposed**（范围冻结稿完成…待复核 → ready 交 Codex） | **一致** |
| `REBASELINE_PLAN.md:28` | 当前 DAG 摘要 = **in_review**（"范围已冻结、待独立复核"） | **不一致 → P2-5**（`in_review` 是 lifecycle v3 的 REVIEW 阶段状态；构成"看似已释放/已进入审查态"的表述） |
| `REBASELINE_PLAN.md:26` | READY 节点：无 | 一致 |
| `TASK_LEDGER.md:30` / `:46` | `proposed` 计数 2；`FEA-00A-IMPL-1` = `proposed`（own row） | **一致**（LEDGER 为 t_ledger 脚本生成，未手改） |
| 卡 `:126`–`:127` | 冻结记录 + "未释放" + 复核通过前不 ready/不派实现 | 一致、诚实 |

另：`STATUS.md:15` 写 "verify_pins.ps1 13/13 PASS"，与同文件 `:12`「14 份契约 + FEA-01 已全部冻结」及实测 **15/15** 不符——历史遗留、非本卡引入，但 STATUS 是被审材料之一，建议一并纠正（P2-10）。

`check.ps1` 默认运行 PASS(2 warnings)，**未捕获** `REBASELINE_PLAN:28` 的 `in_review` 表述；说明该不一致需要人工修正而非机器门禁兜底。

## 8. 可执行性判断（检查点 8）

**结论：现状不足以让 Codex 直接开始实现；需先处置 3 条 P1（其中 P1-1、P1-2 相互关联），并收口 P2 精度项后，本范围冻结才具备可执行性。**

- **region 路径本身是具体的**：token 契约（§4.1）、候选表复用（D3）、seam 同事务（AC3）与写域（providers/、pipeline.py、application/tasks/）自洽——按现冻结文本，region 路径大概率可在写域内实现。
- **P1-1（阻断）**：D3=① 选定的承载在"Run 全量重写"模型下不成立——prepared 行会被 `_write_run` 的 `DELETE FROM pipeline_runs` + FK 级联在成功/失败/重启/并发 pause 四条路径上删除；AC2/AC3/AC5 与 §4.2 的扫除点按现文不可实现/不可验证。必须在卡内固定 `_write_run` 对 prepared 行的保留/重建规则（`pipeline.py` 在写域内，可行）以及 prepared 行的唯一真相来源。
- **P1-2（阻断）**：D1=② 的 artifact 落盘文件 staging 没有可执行闭环：文件无法与 DB "同事务"；卡内未规定 staging 位置/顺序/失败与崩溃残留清理；seam（`SqliteTargetCatalog(conn)`）没有 storage 句柄，最自然的接线点 `src/infrastructure/pipeline/assembly.py` 与 `src/bootstrap/core_assembly.py` 不在写域。必须在"扩写域（限定仅接线）"与"冻结一个写在域内的替代协议（temp 写入、seam 内只做 DB、文件 promotion + 崩溃清扫规则）"之间二选一并写进卡。
- **P1-3（阻断）**：D4 被弱化为 V1–V8；ADJ `:63` 为 V1–V9。改一行即可，但属用户裁决忠实度问题，必须先改。
- 修完 P1 后，P2-1/2/3/4/6/7/8/9 是把 AC/写域/指针打磨到"Codex 无需再猜"的收口项；P2-5/P2-10 是文档一致性问题。
- **最危险的组合**：P1-1 与 P1-2 同时存在时，artifact 场景的 staged 信息（temp 路径/managed 路径）如果放进 `step_result_candidates.payload_json`，也会被级联删除（prepared 行消失），导致崩溃后无法清扫/恢复——因此两条必须一起解，不能只改 AC 措辞。

---

## Findings

| ID | 级别 | 位置 | 问题（含证据） | 建议 |
|---|---|---|---|---|
| **FEA00A-SR-P1-1** | **P1** | 卡 `:51`/`:65`/`:66`/`:68`；`pipeline.py:433`、`:516–528`、`:794–796`；`schema.py:381–382`、`:523–524`；`connection.py:319`；`service.py:744–750`、`:764–786`、`:1008–1012`、`:1023–1027`、`:1094–1110`、`:1455–1458` | **D3=① 的候选承载与 Run 全量重写级联冲突。** 每次 `_write_run` 都 `DELETE FROM pipeline_runs`（`pipeline.py:433`），候选行受 `ON DELETE CASCADE`（`schema.py:381–382`/`:523–524`，`foreign_keys=ON` 于 `connection.py:319`）删除，随后只按 `run.candidates` 重建（`pipeline.py:516–528`）。prepare 直插的 `prepared` 行在 (a) 成功 seam 的 `persist`（`service.py:744–750` → `pipeline.py:794–796`）、(b) seam 失败后的 `_persist`（`service.py:764–786`）、(c) 重启 `recover_running_runs` 的 `_persist`（`service.py:1094–1110`）、(d) 并发 pause/stop 的 `_persist`（`service.py:1011–1012`、`:1023–1027`）被级联删除 → AC2 的 §4.2 扫除点/AC3 的"候选 resolved 同事务"/AC5 的"重启后 prepared 行可识别"按现文不可实现、不可验证。 | 在卡内固定：①`_write_run` 对非 `run.candidates` 的 `prepared` 行的保留/重建规则（`pipeline.py` 在写域内）；②prepared 行的唯一真相（DB 行 vs run JSON）；③把规则写成 AC2/AC3/AC5 的具体断言与 V1–V9 证据；④明确 pause/stop 并发路径不得静默删除 prepared 行。 |
| **FEA00A-SR-P1-2** | **P1** | 卡 `:56`、`:69`（AC6）、`:97`（V9）；`step_writes.py:339–354`、`:364–393`、`:421–459`；`pipeline.py:690–694`；`src/infrastructure/pipeline/assembly.py:36–37`；`src/bootstrap/core_assembly.py:1336–1341` | **D1=② 的 artifact 落盘文件 staging 无闭环。** ①文件系统无法与 DB "同事务"，AC6 "seam 成功时同事务 adopt" 对文件不成立；卡内未规定 staging 位置（现有 `managed_storage.write_temp` 的 `<root>/temp`）、提交顺序、失败/崩溃后残留文件的清理与判定；②seam `SqliteTargetCatalog(conn)` 无 storage 句柄，最自然的接线点 `assembly.py:36–37`、`core_assembly.py:1336–1341`（及可能的 `src/ports/repositories/storage.py`）不在 `allowed_paths`（`card:21–34`）→ 实现要么越界，要么自选未冻结的 hack 路径。 | 二选一并写进卡：**A** 把 `src/infrastructure/pipeline/assembly.py`（必要时 `src/bootstrap/core_assembly.py`、storage port）纳入写域，限定"仅注入/接线，不改行为"，交接登记；**B** 冻结写在域内的协议（prepare 只写 temp；seam 事务只写 DB；文件 promotion 由 `service.persist` 内完成并定义失败/崩溃清扫规则），并补文件级断言（失败：managed 路径 0 文件、artifact_revisions 行 0、temp 残留可判定；成功：行+指针+文件一致）。 |
| **FEA00A-SR-P1-3** | **P1** | 卡 `:52`（D4 行）、`:71`（AC8）、`:97`（V9）；ADJ `:63` | **D4 被弱化。** ADJ U-13 `:63` 明文「AC8；**V1–V9 全部真实 assembly**」，卡内 D4 行与 AC8 均写 **V1–V8**，V9（D1 新增的 artifact 验证）不要求从真实生产 assembly 执行；AC6 也未引用 V9。 | 卡 `:52`/`:71` 改为 **V1–V9**；AC6 显式绑定 V9（"V9 从真实生产 assembly 执行"）；V 矩阵 V9 证据与 AC6/AC8 双向引用。 |
| FEA00A-SR-P2-1 | P2 | 卡 `:65`（AC2）、`:70`（AC7②）；`PREP:74–80` | **AC2/AC7② 的判定口径未落成可机械断言。** AC2 仅"按评估 §4.2 落实"；§4.2 未定义"超期 prepared 行"阈值/判定时点，`abandoned`（或删除）二选一未定，`resolved_at` 未写进 AC；AC7② 的"旧库只读核验"没有给出核验程序/对象/证据格式。 | AC2 直接列出状态机与断言（prepared→resolved/abandoned、resolved_at 非空、失败候选字段断言、扫除时点与选项）；AC7② 固定核验程序（只读打开、三处一致性查询、候选可读性、备份与候选保留的证据清单）。 |
| FEA00A-SR-P2-2 | P2 | 卡 `:67`（AC4）、`:70`（AC7①）；`step_writes.py:350`、`:364–393`、`:491–514` | **结构禁写清单漏 artifact 写面，A4 未完全落到 AC。** AC4/AC7① 只列 `UPDATE regions`/`media_artifacts`/`INSERT region_revisions`；但 prepare 路径实际还会 `storage.publish`（`:350`）、`INSERT INTO artifact_revisions`（`:364–393`）、`INSERT INTO media_artifacts` 并 commit（`:491–514`，commit `:513`）。实现可通过 AC4 的 grep，却在 prepare 留下 artifact 行/文件（D1 场景下即违反 A4 "仅允许读"，且失败后残留空 artifact 行）。 | AC4 的禁写清单扩为：regions 的 UPDATE/INSERT、media_artifacts 的 UPDATE/INSERT、region_revisions/artifact_revisions 的 INSERT、`storage.publish`（或明确 DSH 决定 `_artifact_id` 行创建可提前，并让 V9 覆盖该行）。AC7① 同步。 |
| FEA00A-SR-P2-3 | P2 | 卡 `:71`（AC8）；`PREP:30`（G7 清单） | **"真实生产 assembly" 未定义入口，"8 文件 outcome 对照"无判定格式。** `bootstrap.core_assembly.assemble_core_services`（tests 实际使用）与 `infrastructure.pipeline.assembly.build_production_pipeline`（可接受 handlers 映射）都可被声称为 "production"；且 G7 清单中的 `tests/providers/t111_support.py` 是 helper（无 outcome）。 | 卡内点名唯一入口（含真实 handlers/writers/storage），并要求逐文件表格：测试名 / 修前 / 修后 / 判定（保持 live 语义或有意变更）/ 理由；`t111_support.py` 单列"适配而非 outcome 对照"。 |
| FEA00A-SR-P2-4 | P2 | 卡 `:93`（V5）；`service.py:900–960`、`:730–790`、`:1011–1012`、`:1023–1027` | **V5 的 pause/cancel 注入点在现有生产路径没有 seam 前检查。** `execute_run` 只在 unit 边界查 pause/cancel（`:900–960`），`commit_step_result`（`:730–790`）不检查；V5 无法从生产路径机械注入并判定"零变化"；并发 `control_run` 的 `_persist` 还会级联删除 prepared 行（`:1011–1012`/`:1023–1027`），使"候选保留可诊断"不成立。 | 卡内明确 seam 遇 pause/cancel 的行为（中止并放弃 prepared 候选，或明确 V5 通过"handler 返回后、调用 commit 前设标志"构造窗口），并写进 AC1/V5 证据与 P1-1 的保留规则。 |
| FEA00A-SR-P2-5 | P2 | `doc/REBASELINE_PLAN.md:28` | **当前 DAG 行写 `in_review`，与卡 `:6`、`STATUS:7`、`PLAN:14`、`LEDGER:46` 的 `proposed` 矛盾。** `in_review` 是 lifecycle v3 的 REVIEW 阶段状态（协议 §4），构成"看似已释放/已进入审查态"的表述；`check.ps1` 默认 PASS(2 warnings) **未捕获**。 | 改为 `proposed`（或 "proposed（范围冻结稿待复核）"），`ready` 时再更新。 |
| FEA00A-SR-P2-6 | P2 | 卡 `:21–34`（`allowed_paths`） | **写域精度问题。** (a) `:28` 含 `doc/reviews/ADJ-2026-11-01-FEA-DECISIONS.md`——用户裁决记录不应给实现 Owner 写权；(b) `:33` `tests/**` 过宽，与方案 §15.6 `:919`「`tests/` 内明确测试」不符；(c) `:27` `doc/reviews/FEA-00A-IMPL-*.md` 是 Reviewer 产出，Owner 不应改。 | 移除 ADJ；把 `tests/**` 收窄为 G7 的 8 个文件 + 本卡新增测试文件/真实 assembly 执行脚本的明确路径（或规定 Handoff 逐项列改动测试）；`doc/reviews/FEA-00A-IMPL-*.md` 注明仅 Reviewer/DSH 写。 |
| FEA00A-SR-P2-7 | P2 | 卡 `:13`（`base_commit: 6b8469a80`） | **base_commit 早于范围冻结提交 `419f891c0`。** 卡内 AC/写域在 `419f891c0` 才冻结；若以 `6b8469a80` 为 base，实现分支不含冻结卡，实现 Review 的 diff 也会包含冻结文档提交。 | `ready` 时把 `base_commit` 更新为 `419f891c0`（或集成后的 head），并让实现 Review 的 `base_commit` 与该值一致。 |
| FEA00A-SR-P2-8 | P2 | 卡 `:66`（AC3） | **"无中间可观察态"没有观测方法。** 同一事务可用单 commit/语句顺序断言，但"无可观察中间态"需要固定手段（sqlite trace callback、事务内并发读、WAL 快照）。 | AC3 固定断言方式（例如 trace 断言 `BEGIN IMMEDIATE → … → 单次 commit`，或独立连接在事务未提交时读不到新值），并写入 V7。 |
| FEA00A-SR-P2-9 | P2 | 卡 `:77–83`（L 表） | **L 再触发条件不完整。** (a) L-1 未列"给 `step_result_candidates` 加列/CHECK/索引"；(b) L-2 未列"构件重设计使 prepared/候选状态进入 Host 投影或 `StepResult` 的 wire 可见语义"（D2 允许重设计，但 L-2 只盯错误码/白名单）；(c) L-5 未澄清 AC7②"保留备份"仅指不删除既有备份（不创建/不恢复），存在误触 L-5 的解释空间。 | 补上述三条再触发条件；L-5 行同步写"AC7② 只读核验不创建/不恢复备份"。 |
| FEA00A-SR-P2-10 | P2 | `doc/STATUS.md:15`（历史遗留） | **`verify_pins.ps1 13/13 PASS` 与同文件 `:12`「14 份契约 + FEA-01 已全部冻结」及实测 15/15 不一致。** 非本卡引入，但 STATUS 是被审材料之一，且该口径可能误导冻结校验计数。 | 改为 15/15（或按实际 pin 数），与 `:12` 口径一致。 |

**P0 = 0。P1 = 3（FEA00A-SR-P1-1/2/3）。P2 = 10。** P1 未解决前不能 `approved`；P1 处置后需对修订后的 head 重新复核（范围冻结复核，不是实现复核）。

---

## 结论与边界声明

1. **decision: `changes_requested`**。范围冻结的主体结构（写域、AC1–AC10、V1–V9、L 判定、禁止范围、诚实标记）方向正确，token 契约与 §15.6 出口已落位；但存在 3 条 P1：D3 候选承载与 Run 重写级联冲突（AC2/AC3/AC5 不可实现/不可验证）、D1=② artifact 文件 staging 无闭环且最自然接线点不在写域、D4 由 V1–V9 被弱化为 V1–V8。修完后再判。
2. **本次复核只针对范围冻结，不构成实现验收**；本报告不评价任何实现（实现尚未开始），`approved` 也不等于 Task 完成或可发布。实现后仍需独立实现复核（`doc/reviews/FEA-00A-IMPL-r1.md`）、AC 逐项证据、集成与 closeout。
3. **独立性**：本席位（`fea00a-scope-reviewer`）为 DSH（Lead）以 fresh 独立上下文派发的 Agent Teams teammate，未参与该 Task 的起草、实现或返修；只读被审 head，未修改任何被审文件（除本报告）、未 commit、未 push。
4. **建议的下一步（供 DSH）**：①按 P1-1/P1-2 在卡内补设计规则（或扩大写域并登记）；②改 V1–V9；③收口 P2 精度项与 PLAN:28；④重新派独立上下文复核本范围冻结；⑤复核 `approved` 且 P0/P1=0 后再 `ready` 交 Codex。

—— 报告结束（`decision: changes_requested`；P0×0 / P1×3 / P2×10）。
