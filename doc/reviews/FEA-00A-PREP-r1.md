---
task_id: task-16
document_id: FEA-00A-PREP-r1
kind: independent_review
reviewer: c01b-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams durable teammate task-16"
reviewer_independent: true
reviewed_by_implementer: false
author: dsh-lead（DSH 主会话，Lead / Architect / Integrator）
base_commit: 15aa7bf3b
reviewed_head: 3debf6b1b
reviewed_head_full: 3debf6b1b51d4620f7543874c94b69f86adfe1b5
reviewed_head_note: "复核期间 HEAD 未前进（== 3debf6b1b）；工作区 clean。被审文件 `doc/plan/FEA-00A_PREP.md` sha256 = 2d8ee1f4ca592a2dba0c8a345973ddad3e8c2149a97951b2308d529ae302de62，与卡内 E-PREP-DOC 声明一致；快照 15aa7bf3b 的 `src/**`、`tests/**` 与 HEAD 相同（`git diff 15aa7bf3b HEAD -- src tests` 为空），故行号核对对该快照有效"
repository: G:/CODEX/New Manga
scope: "FEA-00a 只读评估（G1–G7 缺口证据、§15.5 验收精确化 A1–A6、最小写域、V1–V8 矩阵、D1–D4 决策项、FEA-03 现状）；核对重点是证据真实性与「最小写域是否可直接冻结」"
decision: approved
verdict: approved
p0_count: 0
p1_count: 0
p2_count: 6
evidence_verdicts:
  G1: 属实（行号与语义均精确）
  G2: 属实
  G3: 属实（指针）；但 D1=② 时 artifact 的 `publish` 已提交 revision 行+文件，见 P2-002
  G4: 属实（DDL 列名/迁移 v5/写入点/清理点全部对上）
  G5: 属实
  G6: 属实
  G7: 属实（8 个文件，清单逐名相符）
  F20_citation: 属实（方案 `:66` F20 行，引 `step_writes.py:195`）
  A1_A6: 与 §15.5/§12.1 等价（A3 的「receipt」= persist 回调内 step/run 状态写入，已核实）；缺 §15.6 出口两项，见 P2-006
write_scope_verdict: >-
  方向成立：无需 schema/迁移（候选表 DDL 无 status CHECK、payload_json/base_revision_id/status 够用），
  region 路径无需改 `service.py`（前提 token = 预生成真实 revision id，见 P2-001）；`handlers.py` 可能 0 改动（P2-005）。
  三个必须在冻结前写清的约束：token 契约、staged 失败行的清理归属、D1=② 时 artifact 行/文件一并 staging。
checkps1: "主仓库默认：PASS（2 warnings），EXIT=0；`-TaskPath doc/tasks/FEA-00A-PREP-1.md`：PASS（2 warnings），EXIT=0"
verifypins: "PASS (all 15)，EXIT=0（本提交只改文档，未触冻结契约字节）"
d1_d4_ruling: >-
  D1=②（含 artifact）方向正确但范围必须扩到 `publish` 的 revision 行/文件（P2-002）；D2=① 成立（前提 P2-001）；
  D3=① 可成立但需补 token/清理约束，建议并列 ③「文件 staging」（§15.5 原文允许「staging 表/文件」，且无迁移、无 service.py 改动）；D4=L2 与 §15.6 一致。
approval_conditions: >-
  C1（文档侧，必做）：§4/§61 补 token 契约「token = prepare 预生成的真实 revision_id」+ 依据（`pipeline.py:769–771` 延迟复合 FK、
  `src/application/tasks/store.py:215/236` 并入快照 current_revisions）；
  C2（文档侧，必做）：D3=① 时写明 staged 失败行的处置与清理归属（重复候选的两行语义、stale `prepared` 扫除点）；
  C3（文档侧，D1=② 时必做）：G3/A6 扩到 `ArtifactStepWriter.publish` 的 `artifact_revisions` 行与落盘文件；
  C4（卡侧，必做）：`evidence_snapshot: 15aa7bf3b`（卡 `base_commit: 135479270` 与之不同）；FEA-00a 实现卡 AC 补 §15.6 出口两条（关闭新写入入口/旧库只读核验、保留备份与候选）。
approval_note: >-
  6 条 P2 全部为「文档措辞/约束补写」级别，均不改本 Task 写域、不触代码、不阻塞用户对 D1–D4 的拍板；
  因此判 approved，但 C1–C4 需在把本评估转为实现卡范围冻结材料之前完成（否则 scope freeze 会缺 token 契约与清理归属）。
independence_note: >-
  本复核与被审产出为不同上下文（DSH 主会话写文档，我作为独立 teammate 只读核对源码/测试/文档）；未修改任何被审文件、未 commit、未 push。
captured_at: 2026-11-01T20:53:38+08:00
captured_by: c01b-reviewer
---

# Review：FEA-00a 数据安全评估（快照 15aa7bf3b）

## 范围与依据

被审：`3debf6b1b`（父 `15aa7bf3b`），5 个文件全部为文档：`doc/plan/FEA-00A_PREP.md`（新增 137 行）、`doc/tasks/FEA-00A-PREP-1.md`、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`。**无代码、无测试、无冻结契约、无用户数据改动。**

**依据**：方案 §15.5（`:905`–`:908`，FEA-00a 条目在 `:907`）、§15.6（`:919` FEA-00a 行）、§12.1（`:639` FEA-00a 行）、§2 F20（`:66`）；仓库快照 `15aa7bf3b` 的 `src/**`、`tests/**`；`doc/contracts/` 冻结契约与 pins。

## A. G1–G7 证据逐条核对（行号 + 语义）

| # | 文档主张 | 我的实测（快照 `15aa7bf3b`） | 结论 |
|---|---|---|---|
| G1 | `_persist` 在 seam 前插 `region_revisions` + 写 live `text_json` 并 commit；指针留 seam | `step_writes.py:195–281`：`BEGIN IMMEDIATE :207`；guard `:219–231`；`INSERT INTO region_revisions :248–266`；注释 `:267–268`「the *pointer* stays behind」；`UPDATE regions SET text_json :269–276`；`commit :277`；`rollback :279`。行号与语义**逐字对上** | **属实** |
| G2 | seam 失败无补偿；失败码 `input_revision_changed`/`lock_changed`/`db_failed`/`target_not_found`；service 侧冲突→candidate+FAILED、DB 失败→`_fail_step` | `pipeline.py:742–800`：失败仅 `self._conn.rollback()`（`:756/:759/:766/:775/:785`）回滚**本次 seam 事务**，prepare 已提交的副作用不回滚；`service.py:752–789`：`:764–786` 冲突分支写 candidate+FAILED，`:788–789` db/target→`_fail_step` | **属实** |
| G3 | `adopt_current` 在 handler 内 CAS 并提交 `media_artifacts.current_revision_id`，seam 前指针已推进；调用点 `handlers.py:599/647/733` | `step_writes.py:421–459`：`BEGIN IMMEDIATE :435`、CAS `:445–450`、`UPDATE media_artifacts :451–455`、`commit :456`；`handlers.py:962` 调用 `self.deps.artifacts.adopt_current(...)`，`:599/:647/:733` 返回 `revision_updates=updates` | **属实**（但见 P2-002：`publish` 也已在 prepare 提交 revision 行+文件） |
| G4 | `step_result_candidates` 表已存在、列名如述、当前只用于 seam 拒绝后诊断；写入 `pipeline.py:516–528`、清理由 `library.py:571` | DDL `schema.py:379–396` 列名**完全一致**（status/schema 无 CHECK）；v5 迁移 `:521–539`；写入 `pipeline.py:516–528`（12 列 INSERT）；清理 `library.py:571` `DELETE FROM step_result_candidates WHERE page_id IN (...)` | **属实** |
| G5 | 零写测试只覆盖几何保存 `test_region_db_failure.py:100–140`；guard 测试 `test_region_transactional_guards.py:153–175`；seam 测试无失败零变化断言 | 前两处逐行核对相符（`:100–140` 两个几何零写测试；`:153–175` delete/pin guard 单事务测试）；`tests/pipeline/test_pipeline_production_seam.py`（333 行）测试为 round-trip/recovery/defaults 类，**无** prepare+seam 失败的三处零变化断言 | **属实** |
| G6 | pause/cancel/崩溃无 staging | 表清单无 staging 表（`pipeline_stage_states` 是阶段进度不是数据暂存）；`service.py:900–911` pause 只置 `PAUSED`，无暂存 | **属实** |
| G7 | 8 个测试文件直接用 `RegionStepWriter`/`adopt_current` | 实测 `Group-Object Path` = **8 个文件**，名称与文档清单**逐名相符**（test_bootstrap / test_page_catalog_modes / test_regionless_rebinding / t111_support / test_detect_handler / test_full_chain / test_handlers_pipeline / test_retype_redetect_persistence） | **属实** |

**引用核对**：F20 = 方案 `:66` ✓（该行引 `step_writes.py:195`，与 G1 同源）；§15.5 `:905`–`:908` ✓（FEA-00a 条目 `:907` 原文即「修复 F20 的 `RegionStepWriter._persist` 在 seam 前提交 live `text_json`；candidate 存在独立 staging 表/文件；失败/取消清理不得触及 live；生产 assembly」）；§15.6 `:919` ✓（写域 = `src/infrastructure/providers/`、`src/infrastructure/sqlite/pipeline.py`、`tests/` 内明确测试；L2 高风险；出口「关闭新写入入口；旧库只读核验，保留备份与候选」）；§12.1 `:639` ✓（出口「text、指针、revision 行数零变化；生产 assembly 验证」）。

## B. A1–A6 是否等价 §15.5

| 断言 | 与权威文本对照 | 判定 |
|---|---|---|
| A1 三处零变化 | = §12.1 `:639` 出口「text、指针、revision 行数零变化」+ §15.5 失败/取消清理不得触及 live | **等价** |
| A2 候选可诊断 | = §15.6 出口「保留备份与候选」+ 现有诊断候选语义 | **等价** |
| A3 成功同事务（含 Run receipt） | 实测 `commit_step` 在事务内 `UPDATE` 指针（`:768–782`）后 `persist()`（`:794–796`）；service 的 `persist_committed_step`（`:744–750`）在其中写 step 状态/output + `write_in_current_transaction(run)` → **receipt 与数据同一事务成立** | **等价**（建议实现卡把 receipt 明确为「step_run.status/output + run 状态写入」） |
| A4 prepare 只读 live | = §15.5「失败/取消清理不得触及 live」的强化写法 | **等价（更强，可接受）** |
| A5 重启可判定 | = §15.5 的「重启」要求；但缺"谁清理 stale `prepared`"（P2-003） | **基本等价，缺清理归属** |
| A6（若纳入）artifact | 覆盖指针零变化；若 D1=②，还需覆盖 `publish` 的 revision 行/文件（P2-002） | **部分等价（D1=② 时需扩）** |

**缺口**：§15.6 FEA-00a 出口的两条（「关闭新写入入口」「旧库只读核验，保留备份与候选」）未出现在 A1–A6 或 AC 建议中 → P2-006。

「生产 assembly」要求已在文档 §5 末行写明（`:73`）✓，与 §15.5 一致。

## C. 最小写域可行性（用户重点问：复用候选表是否真不需要 schema/迁移与 service.py 改动）

**① 无 schema/迁移：成立。** `step_result_candidates` 的 `status TEXT NOT NULL` **无 CHECK 约束**（`schema.py:390`），`payload_json`/`base_revision_id`/`resolved_at` 结构够用；NOT NULL 的 `pipeline_run_id`/`step_run_id`/`page_id`/`target_id`/`result_kind`/`reason` 都能在 provider 侧拿到：`Region.page_id` 存在（`src/domain/regions/entities.py:233`），handlers 已把 `source_run_id=run.run_id`、`source_step_run_id=step_run.step_run_id` 传给 `_persist`（`handlers.py:438–439`、`:524–525`）→ 两列 FK 可写。**不需要 schema 变更或迁移** ✓。

**② 无 service.py 改动：可实现，但有一条未写明的硬约束（P2-001）。** `StepResult.revision_updates` 是 `Mapping[str, str]`（`models.py:355`），它有两个既有语义：
- 生产 seam 把它直接写进 `regions.current_revision_id`（`pipeline.py:769–771`），而 `regions.current_revision_id` 与 `region_revisions(region_id, current_revision_id)` 有**延迟复合 FK**（`schema.py` 注释 `:224` 起）；
- 内存 catalog 把它并入 `current_revisions` 快照（`src/application/tasks/store.py:215`、`:236`）。
两者都假定值是**真实 revision id**。因此「token 走 `revision_updates`」只有在 **token 本身就是 prepare 预生成的真实 revision id** 时才成立：prepare 先生成 `uuid` 作为新 revision id → 候选行以该 id 为键（或 `payload_json` 里带它）→ `revision_updates={"region": <new revision id>}` → seam 用该 id 找回候选，**同事务**插 `region_revisions`（用同一个 id）+ 写 text + 翻指针，FK 在提交时自然满足。这样：无 service.py 改动 ✓、无 store.py 改动 ✓、并发（V8）靠 id 唯一性 ✓。
反之若实现成任意 opaque 串（如 `"candidate:..."`），`store.py` 的快照 `current_revisions` 会被污染、`pipeline.py` 的 FK 会拒写 → 必返修。文档只写了「token 走 `revision_updates`」，没写这条约束 → 必须补（C1）。

**③ 本文未列出的必要改动点：**
- **staged 失败行的处置/清理归属**：prepare 插 `status='prepared'` 行；seam 失败时 `service.py:764–786` **再插一条 pending 候选** → 同一步两份候选；`library.py:571` 只在页面 purge 时删。A5「可清理/重试」需要明确的扫除点（建议放在 `pipeline.py` 的 run 启动/`commit_step` 失败路径，仍在 §15.6 写域内）→ P2-003/C2。**这是写域内可解决的设计点，不构成写域扩张。**
- **D1=② 时 artifact 的 staging 范围**：`ArtifactStepWriter.publish` 已在 prepare 阶段 `BEGIN IMMEDIATE`（`:358`）→ `INSERT INTO artifact_revisions`（`:365`）→ `commit`（`:394`），并已把 payload 落盘；失败会留孤儿 revision 行与文件，不只指针（`adopt_current`）。文档 G3/A6 只覆盖指针 → P2-002/C3。
- **handlers.py 未必需要改**：region 路径的 run/step 上下文、`revision_updates` 返回通道都已具备（`:438–439`、`:524–525`、`:458`、`:548`）；只有 D1=②（artifact 的 `adopt_current` 调用点 `:962`）才需要动 handlers。建议把 §4 表里「handlers.py 必要（局部）」改成「视 D1」→ P2-005（精度问题，不影响可行性）。

## D. D1–D4 推荐是否合理

| 项 | 文档推荐 | 我的判定 |
|---|---|---|
| D1 artifact 是否一并修 | ②（一并修） | **同意方向**；但范围须扩到 `publish` 的 revision 行/文件（P2-002），且 handlers `:962` 调用点进写域 |
| D2 是否允许改 service.py | ①（不允许） | **同意**，且技术上成立——前提是 P2-001 的 token 契约（否则会被迫改 service.py/store.py） |
| D3 候选承载 | ①（复用候选表） | **可成立**，但需补 P2-001/P2-003 的约束；**建议并列选项 ③「文件 staging」**：§15.5 原文即「staging 表**/文件**」，文件 staging 无迁移、无 service.py 改动，且天然避免「prepared 行与诊断行重复」；代价是崩溃残留文件需清理规则 |
| D4 验证等级 | L2 + 生产 assembly | **同意**（§15.6 即 L2 高风险） |

## E. FEA-03 现状核对

`src/**` 与 `apps/desktop-avalonia/src/**` 检索 `draft_journal`/`edit_token`/`commit_receipt`/`protection_epoch` 及其中文变体（draft journal / edit token / commit receipt / protection epoch）**全部 0 命中** → 文档「快照中完全无实现、属新设计」**属实**。写域与 §15.6 `:923`（FEA-03 行：`src/application/`、`src/domain/`、`src/infrastructure/sqlite/`、`NewManga.ApplicationCore`、tests）逐项一致 ✓；前置判断（新表→迁移契约判断、L-2 若引入 draft ACK 码、L-5 不适用）与 §15.6 出口一致 ✓。

## F. 边界与治理

| # | 检查 | 实测 | 结论 |
|---|---|---|---|
| F1 | 只含文档 | `git show --name-status 3debf6b1b` = 5 个 `doc/**` 文件；无 `src/**`、`tests/**`、`apps/**`、`doc/contracts/**` 改动 | **PASS** |
| F2 | 冻结字节 | `verify_pins.ps1` → `PIN AUDIT: PASS (all 15)`，EXIT=0 | **PASS** |
| F3 | 治理 | `check.ps1` 默认 PASS(2 warnings)/EXIT=0；`-TaskPath doc/tasks/FEA-00A-PREP-1.md` PASS(2 warnings)/EXIT=0 | **PASS** |
| F4 | 无"未执行标通过" | 卡 `in_review`、AC1–AC3 `<<MET>>`（有文档+核对事实支撑）、AC4 `[ ] <<BLOCKED: 待独立复核>>`；Closeout 明写"AC4 待独立复核" | **PASS（诚实）** |
| F5 | 指针一致性 | STATUS `:7` = 当前 Task `FEA-00A-PREP-1 in_review`、`:11` = 下一候选 `FEA-00a`/`FEA-03` 待用户确认；PLAN 行 `proposed`→`in_review`；LEDGER 计数同步（`in_review` 2→3、`proposed` 2→1） | **PASS** |

## Findings

| ID | 级别 | 位置 | 问题 | 证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| PREP-P2-001 | **P2（非阻断；冻结前必补）** | `FEA-00A_PREP.md:54`/`:57`/§4 | 「token 走 `StepResult.revision_updates`、不改 service.py」未写明 token **必须是预生成的真实 revision id**；若实现为 opaque 串，`store.py:215/236` 的快照 `current_revisions` 被污染、`pipeline.py:769–771` 的延迟复合 FK 会拒写 | 本文 C-② | 补一句契约：「prepare 生成新 `revision_id`（uuid）→ 候选行以之为键 → `revision_updates={"region": <该 id>}` → seam 按 id 找回候选并同事务插行/写 text/翻指针」 | open |
| PREP-P2-002 | P2（D1=② 时必补） | 文档 `:26`（G3）、`:45`（A6） | 只覆盖 `adopt_current` 指针；`ArtifactStepWriter.publish` 在 prepare 已提交 `artifact_revisions` 行（`step_writes.py:358/365/394`）并落盘 payload → 失败会留孤儿 revision 行/文件 | 本文 A 表 G3 行 + `:358–394` | D1=② 时 staging 范围写明「artifact revision 行与文件同样在 seam 内落定，或明确『不可变行允许保留』」并进 AC | open |
| PREP-P2-003 | P2（非阻断；冻结前必补） | 文档 `:86`（V5/V6/A5） | 「候选可识别为未完成并可清理/重试」无清理归属：prepare 的 `prepared` 行 + service 失败路径新插的 pending 行会让同一步出现两份候选，且 `prepared` 行只在页面 purge 时删（`library.py:571`） | 本文 C-③ | 指定扫除点（建议 `pipeline.py` run 启动或 `commit_step` 失败分支）与两行候选的语义（prepared=待 seam、pending=已诊断） | open |
| PREP-P2-004 | P2（非阻断） | 卡 `:13` `base_commit: 135479270` | 评估快照是 `15aa7bf3b`（其后的 checkpoint 提交），卡却写 `135479270`（FEA-02-CORE 集成提交）；代码字节相同，但「评估基于哪个快照」在卡内不可判 | `git log`：`15aa7bf3b` 父 = `135479270` | 卡内加 `evidence_snapshot: 15aa7bf3b`（或直接把 `base_commit` 写快照） | open |
| PREP-P2-005 | P2（非阻断；精度） | 文档 `:54`（§4 表 handlers 行） | 把 `handlers.py` 列为「必要（局部）」偏保守：region 路径的 run/step 上下文与 `revision_updates` 返回通道已具备，D1=① 时可能 0 改动 | `handlers.py:438–439/:524–525/:458/:548` | 改为「视 D1：① 可能 0 改动；② 需改 `:962` adopt 调用点」 | open |
| PREP-P2-006 | P2（非阻断；A1–A6 覆盖缺口） | 文档 §3/§5 | A1–A6 未覆盖 §15.6 FEA-00a 出口的两条：「关闭新写入入口」「旧库只读核验，保留备份与候选」 | 方案 `:919` 出口列 | 在 FEA-00a 实现卡 AC 补一条（发布/门禁层面：新写入入口关闭后的只读核验与备份保留） | open |

**P0：0。P1：0。** 6 条 P2 全部为文档措辞/约束补写，不改写域、不触代码、不阻塞 D1–D4 拍板。

## 结论

**decision：`approved`**（P0 × 0 / P1 × 0 / P2 × 6，均非阻断，其中 C1–C4 需在冻结前补写）。

- **证据可信**：G1–G7 行号与语义逐条核对**全部属实**（含最关键的 G3「artifact 同类缺陷」与 G4「候选表可复用」）；F20/§15.5/§15.6/§12.1 引用全部对得上目标行；FEA-03「0 实现」也经独立检索确认。
- **A1–A6 与 §15.5 等价**（A3 的 receipt 已核实为同一事务；A5 缺清理归属、A6 在 D1=② 时需扩、§15.6 出口两条需补）。
- **最小写域方向成立**：无 schema/迁移、无 `service.py` 改动在「token = 预生成真实 revision id」前提下可实现；`handlers.py` 可能 0 改动。三个必须补的约束见 C1–C3。
- **D1=②/D2=①/D3=①/D4=L2** 方向均可接受；D3 建议并列「文件 staging」选项。

### DSH 下一步精确动作（把评估转为 FEA-00a 实现卡的范围冻结材料）

1. **先补文档**（同一提交可含卡）：C1 token 契约（§4/§61 各一段）、C2 清理归属、C3（D1=② 时）artifact 行/文件 staging、P2-005 措辞，P2-006 转成实现卡 AC；重新计算 `FEA-00A_PREP.md` sha256 并更新卡内 `E-PREP-DOC`。
2. **卡收口**：AC4 → `[x] <<MET>>`（依据本报告 `doc/reviews/FEA-00A-PREP-r1.md`，approved、P0/P1=0）；卡加 `evidence_snapshot: 15aa7bf3b`；补 `E-PREP-REVIEW` 证据行（path=本报告，commit=`-`，sha256=本报告哈希）；`canonical_evidence_status: complete`；置 `done`（`integration_commit`=本次收口提交或 `3debf6b1b`；文档类 Task 无代码集成）。
3. **用户拍板项**（建议一次问清，附我的推荐）：
   - **D1**：FEA-00a 是否含 artifact 指针/行（推荐 ②，但需接受 handlers `:962` 与 artifact staging 进写域）；
   - **D2**：是否允许改 `service.py`（推荐 ① 不允许，有 token 契约即可）；
   - **D3**：候选承载 ①候选表 / ③文件 staging（推荐 ① 并补清理规则；若想零语义耦合则 ③）；
   - **D4**：验证等级（推荐 L2 + 生产 assembly，与 §15.6 一致）。
4. **建 FEA-00a 实现卡（范围冻结材料）应含**：
   - 写域：`src/infrastructure/providers/step_writes.py`（+`handlers.py` 仅在 D1=② 时的 `:962`）、`src/infrastructure/sqlite/pipeline.py`、`tests/` 明确测试；L-1/L-2/L-5 = `NOT_APPLICABLE`（前提：不改 schema、不新增错误码白名单、不触恢复路径）。
   - AC：A1–A6 六条（A6 视 D1）+ §15.6 出口两条（P2-006）+ 「生产 assembly 执行 prepare」+ V1–V8 参数化（V8 并发）；测试必须断言三处零变化且从真实生产 assembly 出发。
   - 证据：TRX/日志 + `verify-boundaries` 类脚本（断言 prepare 路径无 `UPDATE regions`/`media_artifacts`）+ 8 个 blast-radius 测试文件的 result 对照（G7 清单已给）。
   - 前置：D1–D4 用户裁决；本评估 approved 后释放。
5. **不需要 UNFREEZE**（本次只改文档；冻结契约与 pins 15/15 未动）；**不需要改 Gate**（`G-DELETE-IMPL` 仍 OPEN，随 FEA-00a 释放单独裁决）。
6. **顺带**：STATUS `:11` 的下一候选表述已在位（`FEA-00a`/`FEA-03` 待用户确认）✓；FEA-00a 卡建立后记得同步 PLAN READY 节点与 ledger（ready 门禁见 `check.ps1:640–655`）。

—— 报告结束（`decision: approved`；G1–G7 全部属实；A1–A6 等价 §15.5；最小写域方向成立；P2×6 非阻断，C1–C4 冻结前补写）。
