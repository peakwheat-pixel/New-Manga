---
document_id: FEA-00A-IMPL-scope-r3
kind: independent_scope_review
reviewer: fea00a-scope-reviewer
reviewer_kind: subagent
reviewer_source: "DSH Agent Teams durable teammate `fea00a-scope-reviewer`（role=teammate，context=fresh，第三轮沿用同一独立席位；子任务标识形式 = teammate target 名 + 本报告 frontmatter `document_id`；未使用独立 CLI session ID；未参与该 Task 的起草/实现/返修）"
reviewer_independent: true
reviewed_by_implementer: false
author: dsh-lead
base_commit: 3d95b03d6
reviewed_head: 3d95b03d6
reviewed_head_full: 3d95b03d62af10a5af03dd3e8956dab35045f0af
repository: G:/CODEX/New Manga
scope: "FEA-00A-IMPL-1 范围冻结 v3（r2 P1×2/P2×7 的处置核验、v3 新引入问题、指针/一致性）；不构成实现验收（实现尚未开始）"
decision: approved
verdict: approved
p0_count: 0
p1_count: 0
p2_count: 10
supersedes: FEA-00A-IMPL-scope-r2
checkps1: "默认（当前 Task doc/tasks/FEA-00A-IMPL-1.md）：PASS (2 warnings)，EXIT=0"
verifypins: "PIN AUDIT: PASS (all 15)，EXIT=0"
captured_at: 2026-11-01T21:50:34+08:00
captured_by: fea00a-scope-reviewer
---

# Review：FEA-00A-IMPL-1 范围冻结 v3（base/reviewed_head = `3d95b03d6`）

**结论：`approved`（P0 × 0 / P1 × 0 / P2 × 10，均为非阻断的精度/一致性问题）。**

- **r2-P1-1 已真正解决**：`R-CAND-2` 改为「禁止对 `pipeline_runs` 用 `DELETE` / `INSERT OR REPLACE`（改 `INSERT … ON CONFLICT(run_id) DO UPDATE`）；必须重建父行时先读三态候选、重建后按 `candidate_id` 去重回插」，三态（`prepared`/`resolved`/`abandoned`）均受保护；AC2/AC3/AC5 与 V1/V2/V5/V7 已同步。
- **r2-P1-2 已真正解决**：`R-ART-2` 已把 `publish` 移到「CAS 屏障与 DB 写之后、`COMMIT` 之前」；拒绝/暂停/取消全部先于 publish；`R-ART-3` 的补偿覆盖「任何非 `applied` 结果」并含孤儿清单；首 revision 的 `INSERT media_artifacts` 已在 seam 内（措辞有小误，见 r3-P2-2）。
- r2 的 7 条 P2 逐项有实质改动（3 条留有精度残项，已计入本报告 P2）；v3 未改源码/测试（`git diff 98fbccdf5 3d95b03d6 -- src tests apps` 为空），不引入实现层回归风险。
- 本次仍是**范围冻结复核**，不构成实现验收；`approved` 不等于 Task 完成。实现后仍需独立实现复核、AC 证据、集成与 closeout。**10 条 P2 不阻断 `ready`**；建议其中 4 条（r3-P2-1/2/3/4）在 `ready` 提交或实现首日顺手改文，其余在实现中按 Handoff 登记处理。

## 0. 复核对象、方法与环境

**被审**：`3d95b03d6`（父 `98fbccdf5`）。`git show --numstat`：仅 `doc/tasks/FEA-00A-IMPL-1.md`（+91/−89）与 `doc/reviews/FEA-00A-IMPL-scope-r2.md`（+174/−0，上一轮报告入库）。

**环境与辅助证据（只读）**

- `git rev-parse HEAD` = `3d95b03d62af10a5af03dd3e8956dab35045f0af`；工作区 clean（`## main`）；复核期间未改任何被审文件、未 commit、未 push，只新增本报告。
- `git diff --stat 98fbccdf5 3d95b03d6 -- src tests apps` **为空**；源码行号在本报告全部有效。
- `pwsh -NoProfile -File tools/governance/check.ps1` → `Governance check: PASS (2 warnings)`，EXIT=0；`verify_pins.ps1` → `PIN AUDIT: PASS (all 15)`，EXIT=0。
- 指针复核：`STATUS.md:7` = `proposed`；`REBASELINE_PLAN.md:14` = `proposed`、`:28` = `proposed`；`TASK_LEDGER.md` 未变（status 仍 `proposed`，计数一致）；`STATUS.md:15` = 15/15（r1 的 P2-5/P2-10 修复保持有效）。唯一滞后：`REBASELINE_PLAN.md:28` 仍写「范围冻结 **v2** 待独立复核」（v3 已提交）——非阻断，见 r3-P2-9。
- `doc/reviews/FEA-00A-IMPL-scope-r2.md` 已入库且内容与本席位 r2 输出一致；r2 自本报告起降为 `HISTORICAL`（按协议不回溯改写）。

**依据**：v3 卡（`doc/tasks/FEA-00A-IMPL-1.md`）、ADJ U-13（`doc/reviews/ADJ-2026-11-01-FEA-DECISIONS.md:56–65`）、评估（`doc/plan/FEA-00A_PREP.md`）、方案 §15.5 `:905–:910` / §15.6 `:912–:919`（尤其 `:914`「下表路径…不是实际写权」）、协作协议 §3/§4/§6；源码现状（`pipeline.py`、`service.py`、`store.py`、`schema.py`、`models.py`、`step_writes.py`、`handlers.py`、`managed_storage.py`、`src/ports/repositories/storage.py`、`assembly.py`、`core_assembly.py`）；`tests/core/**`（57 个 py 文件）、`tests/pipeline/**`（9 个）与 `tests/m2_acceptance/`、`tests/infrastructure/` 的 `assemble_core_services` 使用面。

## 1. r2 的 2 条 P1 是否真正解决

### 1.1 r2-P1-1（三态候选 vs `_write_run` 级联）→ **已解决**

**规则核验**（卡）：

- `R-CAND-1`（卡 `:68`）：三态行为 prepare→seam 生命周期的唯一持久真相，`PipelineRun.candidates` 只承载 seam 拒绝后的诊断候选。
- `R-CAND-2`（卡 `:69`）：明确「**不得**对 `pipeline_runs` 使用 `DELETE` 或 `INSERT OR REPLACE`（两者都会触发候选级联删除）；必须改为 `INSERT … ON CONFLICT(run_id) DO UPDATE`（UPSERT）。若某父行（含 `step_runs`）确实必须重建，须在同一事务内先读出该 `run_id` 下三态候选行，重建后按 `candidate_id` 去重回插（`run.candidates` 已有的 id 优先）。四条路径（成功 persist / seam 失败 `_persist` / `recover_running_runs` / `control_run` pause-stop）全部适用。`pipeline.py:1058` 的既有清理语句不属本规则范围，但不得新增删除父行的路径。」
- `R-CAND-3`（卡 `:70`）：状态机 + `resolved_at` + 「任何路径不得硬删三态行（唯一例外 `library.purge`）」。
- `R-CAND-4`（卡 `:71`）：启动清扫 + 计数 + 同一步 `abandoned`+`pending` 双行可分别断言。

**断言同步核验**：

- AC2（卡 `:103`）：「R-CAND-2 四条路径下三态候选行数与 `candidate_id` 集合不变（UPSERT 或回插）；R-CAND-4 启动清扫计数；同一步 abandoned+pending 双行可分别断言」——已从 v2 的「只断言 prepared」升级为**三态集合断言**，可机械核验（`SELECT status, candidate_id` 集合比对）。
- AC3（卡 `:104`）：resolved 同事务 + R-SEAM-2 双证据；AC5（卡 `:106`）：R-CAND-2/4 + 清扫后 `abandoned` 计数。
- V1（卡 `:127`）「三态行存续」、V2（`:128`）、V5（`:131`）「候选独立事务置 `abandoned`」、V7（`:133`）trace+独立连接——均已同步。

**机制可行性复核**：改为 UPSERT 后候选不再被父行级联删除；四条路径（成功 `service.py:744–750`→`pipeline.py:794–796`；失败 `service.py:764–786`；重启 `service.py:1094–1110`；pause/stop `service.py:1008–1012`/`:1023–1027`）的候选存续从「靠回插」变为「靠不删父行」，R-CAND-2 的「必须重建时再读/回插」覆盖了 `step_runs` 级重建场景。**r2-P1-1 的根因已消解。**

**其它删除三态行的路径**（r2 复核要求）：

- `library.purge`（`library.py:571` 删除候选）+ `DELETE FROM step_runs`（`:574–576`）——R-CAND-3 已列为唯一例外，属既有语义（页删除），**接受**。
- `SqliteRunLedgerMaintenance.purge_targetless_runs`（`pipeline.py:1054–1064`，`DELETE FROM pipeline_runs WHERE NOT EXISTS(targets) AND status NOT IN ('running','paused')`；类 docstring `:1036–1038` 明说级联含 `step_result_candidates`）——会删除 target-less 且非活动 run 的三态候选。R-CAND-2 已点名「`pipeline.py:1058` 不属本规则范围」，但 R-CAND-3 写「**唯一**例外 `library.purge`」与之不一致（见 r3-P2-4）。该方法作为公开维护端口存在（`src/application/maintenance/ports.py:87–99`，测试 `tests/storage/test_run_files_leak.py:222–305` 直接调用；生产 bootstrap 当前未见调用点）。**不构成 P1**（既有代码、非本卡新增、且为本卡所不涉）；但文档例外清单需改。

### 1.2 r2-P1-2（artifact 文件 staging 无闭环）→ **已解决**

**规则核验**（卡）：

- `R-ART-2`（卡 `:78`–`:79`）顺序：①`BEGIN IMMEDIATE` → ②按 token 找回 prepared 候选并校验 `base_revision_id`/`sha256`/`size` → ③`R-SEAM-1` 的 pause/cancel 检查 → ④DB 写（首 revision 的 `INSERT media_artifacts`、`INSERT artifact_revisions`、CAS `media_artifacts.current_revision_id`、候选置 `resolved`）→ ⑤**commit 之前** `storage.publish(temp_handle, relative_path)`（幂等）→ ⑥`COMMIT`。并明写「拒绝路径（revision/lock/stale/pause/cancel）全部发生在 publish 之前 → 不产生孤儿文件」。
- `R-ART-3`（卡 `:80`）：任何非 `applied` 结果 → 未 publish 时 `discard_temp`；publish 已发生而后续失败 → `remove_managed` 补偿 + 孤儿路径入证据清单；启动清扫（prepared artifact 候选 → 校验/discard → `abandoned`；无 `artifact_revisions` 引用的最终文件 → `remove_managed`）；清扫实现放 `pipeline.py`、由 `PipelineService` 启动路径调用。
- `R-ART-4`（卡 `:81`）：`storage=None` = 不启用 artifact staging；生产 `core_assembly.py` 必须传 `ManagedStorage`；`storage=None` 遇 artifact 候选 → 明确失败（`db_failed`），不得静默 publish。
- `R-ART-5`（卡 `:82`）：接线仅最小改动，不重构组合根/公开签名。

**验收同步核验**：AC6（卡 `:107`）已含「失败注入下 `media_artifacts.current_revision_id`、`artifact_revisions` 行数、最终文件均无新增可见产物**且无孤儿文件**；成功时按 R-ART-2 顺序…首 revision 的 `INSERT media_artifacts` 在 seam 内完成；崩溃后按 R-ART-3 可清扫（A6，**V9 从真实生产 assembly 执行**）」；V9（卡 `:135`）「失败零推进且无孤儿；成功三者一致」。r2-P1-2 的两大缺口（拒绝路径孤儿、首 revision 建行）均已在规则与 AC 层面闭合。

**残余精度问题**（不构成 P1，见 §4）：首 revision 建行的字段清单有误（`media_artifacts` 无 `revision_no` 列）、payload 冻结字段仍缺 `mime_type`（NOT NULL）等、`persist()`/`stage_updates` 未写进 R-ART-2 顺序、清扫的 storage 接线与幂等校验机制未固定。

## 2. r2 的 7 条 P2 是否逐项落实

> 说明：v3 卡「复核处置对账」表（`:139`–`:154`）把 r2 的 P2×7 重新编号为 `r2-P2-1…11`；下表「r2 report ID」列使用 **r2 报告原 ID（`P2-1…P2-7`）**，按**内容**逐项对照——7 条均有实质改动，其中 3 条留有精度残项（已在本报告 P2 内结转）。

| r2 report ID | v3 对账表 ID | 正文核验 | 判定 |
|---|---|---|---|
| P2-1（R-ART 协议六项衔接） | r2-P2-1…5 | ①首 revision `INSERT media_artifacts`（卡 `:78` ④）✓；②payload 冻结字段（卡 `:77`）✓（但缺 `mime_type` 等，见 r3-P2-2）；③分支键守卫（卡 `:89` R-SEAM-4）✓（但写法有 `ARTIFACT` target_type 错误，见 r3-P2-1）；④清扫位置/调用方（卡 `:80`）✓（storage 接线未写，r3-P2-5）；⑤方法名统一为 `prepare_revision`（卡 `:77`）✓；⑥**幂等校验机制仍未固定**（R-ART-2⑤ 仅写「目标已存在且 sha256 相同」，端口无读最终文件哈希的方法；`src/ports/repositories/storage.py:21–52`）→ **残留**。 | **部分落实**（①–⑤ ✓；⑥残留） |
| P2-2（`storage=None` 矛盾） | r2-P2-6 | R-ART-4（卡 `:81`）：`storage=None` = 不启用 staging；生产必传；artifact 候选 → `db_failed`，不得静默 publish ✓。措辞「仅用于既有测试的双实例保持旧语义」与 R-ART-1 的无条件 staging 仍有字面矛盾（r3-P2-6）。 | **已落实**（措辞残项） |
| P2-3（R-SEAM-1 rollback/接口/结果映射） | r2-P2-7 | R-SEAM-1（卡 `:86`）：判定位置 `BEGIN` 后、live 写与 publish 前；命中 `rollback` 返回 `paused`/`cancelled`，随后**独立事务**置 `abandoned`（明确不得在已回滚事务内写）✓；接口「入参标志或回调，实现方式由实现者选定但须写入 Handoff」✓。但 `paused`/`cancelled` 结果到 `service.commit_step_result` 的映射（现有 else → `DB_FAILED`/`TARGET_NOT_FOUND`，`service.py:788–789`）与 Run/Step 状态未定义 → **残留**（r3-P2-10）。 | **部分落实**（映射残留） |
| P2-4（mock/double 口径） | r2-P2-8 | R-SEAM-3（卡 `:88`）：允许生产配置中既有 `mock_local_providers=True`（本地 provider 替身），**禁止** fake executor / InMemory catalog / 测试专用 pipeline 替代 ✓。 | **已落实** |
| P2-5（写域扩张 + core_assembly 影响面） | r2-P2-9 | `allowed_paths` 补 `tests/core/**`、`tests/pipeline/**`（卡 `:34–35`），scope 正文（`:94`）同步 ✓（blast radius 部分覆盖）；但**未记录** §15.6 建议写权行的扩张理由、与 FEA-10 写域重叠（方案 `:931`）声明；`tests/m2_acceptance/` 4 文件、`tests/infrastructure/test_plugin_sandbox.py`、`tests/providers/test_detection_manga.py` 等 `assemble_core_services` 使用面仍不在写域且 AC8 未要求其回归证据 → **残留**（r3-P2-8）。 | **部分落实** |
| P2-6（新增测试文件不在 allowed_paths） | r2-P2-10 | 写域改为 `tests/core/**`、`tests/pipeline/**`（含新增测试文件），Handoff 逐项登记要求保留（卡 `:94`、AC8 `:109`）✓。 | **已落实**（目录放宽本身产生 P2，见 r3-P2-7） |
| P2-7（同一步 abandoned+pending 双行语义） | r2-P2-11 | R-CAND-4（卡 `:71`）：「同一步允许并存『1 行 abandoned』+『1 行 pending』，诊断查询必须按 `status` 区分并可分别断言」；AC2（`:103`）同步 ✓。 | **已落实** |

## 3. v3 新引入问题的可行性核验（重点项）

### 3.1 父行改 UPSERT 对既有 `_write_run` / `_check_write_revision` / 缓存的影响

- **对 `_check_write_revision`/缓存无影响**：`_check_write_revision` 使用进程内 `_write_revision` 计数（`pipeline.py:632–651`），与 SQL 层 DELETE/UPSERT 无关；`_write_run` 结束后照旧更新缓存（`:529–530` 附近由调用方 `put_many`/`write_in_current_transaction` 更新）。
- **对 `_write_run` 子表路径有实质影响**：现有 `_write_run` 依赖「父行 DELETE → FK 级联清空全部子行 → 重新 INSERT」（`pipeline.py:433` 之后依次 INSERT targets/tasks/steps/refs/candidates，`:466–528`，**没有任何子表 DELETE**）。若只把父行改为 UPSERT，子行仍在库，随即 INSERT 会触发主键/唯一冲突。必须二选一：(a) 子表全部改 UPSERT；或 (b) 先读三态候选 → 显式删除子表（`pipeline_run_targets`/`pipeline_tasks`/`step_runs`，注意三者删除都会经 FK 级联到三态候选）→ 重建 → 回插三态。R-CAND-2 只写到「父行（含 step_runs）」，未写子表处理，也未覆盖 `run_targets`/`pipeline_tasks` 级联链 → **需在实现前补一句明确规则**（r3-P2-3）。**不构成 P1**：规则给的不变量（三态不删/回插）足够达成 AC2，且实现者在 `pipeline.py` 内有明确可行路径。
- 结论：UPSERT 是正确方向；**实现复杂度高于 v2 描述**，需按上述补全子表语义。

### 3.2 事务内 publish 的锁时长与 SQLite 语义

- 语义上可行：`BEGIN IMMEDIATE` 获取 RESERVED 写锁，`storage.publish` 的 `mkdir`/`os.replace` 与 SQLite 锁互不冲突；COMMIT 在 WAL 下不阻塞读者。拒绝路径已全部前置到 publish 之前（R-ART-2 ②③④），崩溃窗口由 R-ART-3 的启动清扫 + 三态候选覆盖。
- 风险：R-ART-2② 的「校验 `sha256`/`size`」若在事务内对大文件重新全量哈希，会拉长写锁并阻塞其它写者（`busy_timeout=5000`，多 worker/pause 并发场景）；R-ART-2⑤ 若走「目标已存在则比对 sha256」，也需读文件哈希。建议把「事务内只比对 prepare 已记录的 sha/size、不重复全量哈希；publish 仅做 `os.replace`」写进规则（r3-P2-3），并在 V9/Handoff 记录时长或超时口径。**非阻断**（常规 mask/clean 体量下短时锁可接受）。

### 3.3 `storage=None` 与生产必传是否自洽

- **基本自洽**：R-ART-4 明确 `storage=None` 是「不启用 staging」的测试态，生产 `core_assembly.py` 必传 `ManagedStorage`；`storage=None` 遇 artifact 候选 → `db_failed`（fail-closed，不静默 publish）。9 个 G7/pipeline 测试构造 `build_production_pipeline` 时需改用带 storage 的调用（均在允许写域：6 个在 `tests/providers/` + 2 个在 `tests/core`/`tests/pipeline` 目录，新目录已放开）。
- **字面矛盾**：R-ART-4 说该态「保持旧语义」，但 R-ART-1 已让 prepare 无条件 staging，artifact 路径在 `storage=None` 下不再有旧语义（只会 `db_failed`）；应改为「非 artifact 路径语义不变；artifact 路径 fail-closed」并写明 fail-closed 时的 temp/候选清理（r3-P2-6）。
- **一个真实边角**：`SqliteTargetCatalog(conn, storage=None)` 时 commit_step 无 storage，无法 `discard_temp`——fail-closed 返回 `db_failed` 后 temp 文件残留、候选停留 `prepared`（等启动清扫）→ 需在 R-ART-3/4 明确该测试态的资源处置。

### 3.4 `tests/core/**`、`tests/pipeline/**` 放宽是否过度

- **过度**：`tests/core/**` 共 **57 个 py 文件**（含 `test_architecture.py`、`test_core_delete_commands.py`、`test_p13_*`、`test_settings_*` 等与本卡无关者），`tests/pipeline/**` 共 **9 个**（含 `test_models.py`、`test_pipeline.py`、`test_store.py`、`test_run_store_cache_race.py`）；`conftest.py` 也在写域内，改动可影响整目录。原需要的 G7 8 文件仅涉及其中少数。
- **需要的实际影响面**：`tests/core/` 内 5 个 `assemble_core_services` 使用者（`test_core_assembly.py`、`test_core_detect.py`、`test_bootstrap.py`、`test_sfx_assembly.py`、`test_sfx_policy_settings.py`）+ `tests/pipeline/test_pipeline_production_seam.py`、`tests/pipeline/test_regionless_rebinding.py`（若需适配 storage=None）+ 新增 V1–V9 测试。
- **未覆盖的影响面**：`tests/m2_acceptance/` 4 文件（`test_acceptance_loop.py:138`、`test_data_integrity.py:85`、`test_provider_fail_closed.py:81`、`test_reader_export_lineage_library_pagecount.py:146`）、`tests/infrastructure/test_plugin_sandbox.py:315`、`tests/providers/test_detection_manga.py:896` 也走 `assemble_core_services`（本次会加 storage 接线），却不在写域、AC8 也未要求其回归证据。
- 建议（r3-P2-7）：把 `tests/**` 收窄为「枚举受影响文件清单 + 新增测试路径」，或保留目录但要求 Handoff 逐项列出**所有**改动测试（不止新增），并在 AC8 增补「受 `core_assembly` 接线影响的测试集」只读回归结果（passed/failed/skipped）；若回归失败且需改那些文件 → 走范围变更。

### 3.5 写域扩到 `src/bootstrap/core_assembly.py` 是否越过 §15.6 FEA-00a 边界

- **不构成硬违规**：方案 §15.6 `:914` 明写「下表路径…为 DSH 冻结前建议，**不是实际写权**」；DSH 是范围冻结/写权授予人（AGENTS.md 2026-10-25），D1=② + D2=② 为「为让 seam 访问 storage 而在组合根做最小接线」提供了依据；R-ART-4/5 已限定最小接线、默认 None、Handoff 登记、不改既有行为。
- **仍缺记录**：卡内未写「相对 §15.6 FEA-00a 建议行的扩张理由」，也未声明与 FEA-10 写域（方案 `:931` 把 `src/infrastructure/pipeline/` 列入 FEA-10）的重叠（r3-P2-8）。建议在卡内（或 ADJ errata）补一段：FEA-10 未释放、本卡只做接线、后续 FEA-10 复核时不得视为既有改动。

### 3.6 其它一致性

- 生命周期 v3：`status: proposed`（卡 `:6`）、10 条 AC 全为 `[ ]` + 非空 `<<PARTIAL: 范围冻结；实现未开始>>`（卡 `:102`–`:111`）、`canonical_evidence_status: pending` → 合规、诚实；AC10 如实记录 r1/r2 `changes_requested` 与本轮待派发（`:111`）。
- 对账表编号/正文一致性：v3 把 r2 的 P2×7 重编号为 `r2-P2-1…11`，且 closeout 写「P2×11 全部处理」（卡 `:184`）；其中 r2-P2-1⑥（幂等机制）与 r2-P2-5①（§15.6 记录）无对应处置行；表 r2-P2-2 声称正文有「按 schema 必填列核对并在 Handoff 登记」，但 R-ART-1（`:77`）正文无此句 → r3-P2-9。
- `base_commit` 仍 `419f891c0`（卡 `:13`，closeout `:185` 承诺 ready 时更新为最终冻结 head）→ 本轮不构成 finding；`ready` 时应更新为 `3d95b03d6` 之后的实际冻结 head。

## 4. Findings（v3，全部 P2，非阻断）

| ID | 级别 | 位置 | 问题（含证据） | 建议 |
|---|---|---|---|---|
| FEA00A-SR3-P2-1 | P2 | 卡 `:89`（R-SEAM-4）；`models.py:61–63`；`pipeline.py:763–766` | **R-SEAM-4 的「按 `target_type` 分派：REGION 分支保持原样；ARTIFACT 分支接受 `{artifact_type: revision_id}`」不可照字面实现**：`TargetType` 只有 `page`/`region`（`models.py:61–63`，无 ARTIFACT）；而 artifact 步骤（segment/mask_refine/inpaint）都挂在 REGION target 上（`handlers.py:943–967` `_commit_artifacts` 要求 `unit.region_id`），若「REGION 分支保持原样」则仍拒绝非 `region` 键（`pipeline.py:763–766`），与 R-ART-1「返回 `{artifact_type: id}`」及 AC4/AC6/D1 矛盾。 | 改为「REGION target：`region` 键走 region 指针 CAS；artifact_type 键走 `media_artifacts` 指针 CAS（用 target 的 `page_id`）；PAGE target 保持既有 artifact 分支；未知键 `db_failed`」——删除不存在的「ARTIFACT target_type」概念。 |
| FEA00A-SR3-P2-2 | P2 | 卡 `:77`（R-ART-1）、`:78`（R-ART-2④）；`schema.py:64–78`、`:81–105` | **媒体行/修订行的字段信息有误且不完整**：①`media_artifacts` 无 `revision_no` 列（`schema.py:64–78`），R-ART-2④ 的「若 `media_artifacts` 无行则 INSERT（current_revision_id=NULL，revision_no=1）」字段放错（`revision_no` 属 `artifact_revisions`，`:84` NOT NULL、`:103` UNIQUE(artifact_id, revision_no)）；②R-ART-1 冻结 payload（`temp_handle`/`relative_path`/`artifact_type`/`page_id`/`artifact_id`/`book_id`/`chapter_id`/`base_revision_id`/`revision_no`/`sha256`/`size`/`content_format`）缺 `mime_type`（`artifact_revisions.mime_type NOT NULL`，`:87`），也未含 `width`/`height`/`options_json`/`provenance_json`/`provider_profile_id`/`model_name`/`source_artifact_revision_id`（可空，但当前 prepare 均会写入，丢失即为行为差异）；`content_format` 语义未定义；③同页同类型首 revision 并发：prepare 不建行后，两个并发 prepare 可能各自生成 `artifact_id`，而 `media_artifacts` 对 `(page_id, artifact_type)` 无 UNIQUE 约束 → 两个 seam 可能插两行；seam 内应在事务内按 `(page_id, artifact_type)` 重新查询/插入并忽略候选 payload 的旧 `artifact_id`。 | 修正 R-ART-2④ 字段（`media_artifacts` 仅 artifact_id/book/chapter/page/type/current_revision_id=NULL/created_at/updated_at；`artifact_revisions.revision_no=1`）；R-ART-1 payload 补 `mime_type`/`width`/`height`/`options_json`/`provenance_json`/`provider_profile_id`/`model_name`/`source_artifact_revision_id`（或明示刻意丢弃及理由）；seam 内按 `(page_id, artifact_type)` 查重后建行。 |
| FEA00A-SR3-P2-3 | P2 | 卡 `:78`（R-ART-2）、`:69`（R-CAND-2）；`pipeline.py:787–796`、`:433`、`:466–528` | **两处实现前必须写清的机制**：①R-ART-2 顺序（①–⑥）未包含 `stage_updates` 写入（现 `pipeline.py:787–793`）与 `persist()`（`:794–796`，AC3/V7 要求 receipt 同事务）——需写明二者在 publish 前/后的位置；②父行改 UPSERT 后子表处理未写（见 §3.1）：现有 `_write_run` 依赖 `DELETE pipeline_runs` 的级联再 `INSERT` 全部子行（`:433` → `:466–528`），仅改父行会导致子行主键/唯一冲突；删除 `pipeline_run_targets`/`pipeline_tasks`/`step_runs` 都会级联到三态候选。 | R-ART-2 补「④b 写 stage_states 与 `persist()`（publish 前或后均可，但须在 COMMIT 前；且事务内不重复全量哈希）」；R-CAND-2 补「子表改 UPSERT，或先读三态 → 删除/重建（含 `pipeline_run_targets`/`pipeline_tasks`/`step_runs` 全链）→ 按 `candidate_id` 回插」。 |
| FEA00A-SR3-P2-4 | P2 | 卡 `:69`（R-CAND-2）、`:70`（R-CAND-3）；`pipeline.py:1054–1064`、`:1036–1038`；`library.py:571` | **删除例外清单不一致**：R-CAND-2 承认 `pipeline.py:1058` 的既有清理不属规则范围，但 R-CAND-3 写「唯一例外 `library.purge`」；`SqliteRunLedgerMaintenance.purge_targetless_runs`（`pipeline.py:1054–1064`）确实会删除 target-less 非活动 run 并级联删除其 `step_result_candidates`（类 docstring `:1036–1038` 明说），是公开维护端口（`src/application/maintenance/ports.py:87–99`；测试直接调用）。 | 将 R-CAND-3 的例外改为「既有例外：`library.purge`（页清理）与 `SqliteRunLedgerMaintenance.purge_targetless_runs`（既有维护端口，不改变其语义）；本卡不得新增第三条硬删路径」。 |
| FEA00A-SR3-P2-5 | P2 | 卡 `:80`（R-ART-3）、`:78`（R-ART-2⑤）；`src/ports/repositories/storage.py:21–52`；`service.py:1094–1110` | **清扫接线与幂等校验机制未固定**：①R-ART-3 说清扫放 `pipeline.py`、由 `PipelineService` 启动路径调用，但 `PipelineService` 当前无 storage 句柄（R-ART-4 只给 `SqliteTargetCatalog` 注入），未写 service 如何获取 storage/清扫器、调用点在 `recover_running_runs`（`service.py:1094–1110`）前还是后、以及须先于重规划；②清扫「无 `artifact_revisions` 引用的最终文件 → `remove_managed`」需明确扫描信息来源（建议只依据 `prepared` 候选 payload 的 `relative_path`，不做全树扫描），并覆盖 `library.purge` 删除候选后遗留的 temp 文件；③R-ART-2⑤ 幂等校验（目标已存在且 sha256 相同）需要读取最终文件哈希，端口无此方法；若新增端口方法，其实现点 `src/infrastructure/filesystem/managed_storage.py` 不在写域。 | 在 R-ART-3/4 写明：清扫器构造（conn+storage）与注入路径（`assembly.py`/`core_assembly.py` 允许接线）、调用点（`recover_running_runs` 之前）、扫描范围（候选 payload 的 relative_path）；幂等校验固定用既有 `infrastructure.filesystem.integrity.integrity_of` 或 `storage.verify_temp(绝对路径)`，不新增 `managed_storage.py` 改动。 |
| FEA00A-SR3-P2-6 | P2 | 卡 `:81`（R-ART-4）、`:77`（R-ART-1） | **`storage=None` 语义的字面矛盾与清理缺口**：「仅用于既有测试的双实例保持旧语义」与 R-ART-1 的「prepare 无条件 staging」矛盾——artifact 路径在 `storage=None` 下不再有旧语义，只会 `db_failed`；且该态无 storage 可 `discard_temp`/`remove_managed`，fail-closed 后 temp 残留与候选停 `prepared` 的处置未写。 | 改为「非 artifact 路径语义不变；artifact 路径 fail-closed：返回 `db_failed`、由 writer 侧 `discard_temp`、候选按 R-CAND-3 置 `abandoned`（或明确留待启动清扫）」；并列明必须传 storage 的调用方（生产 `core_assembly.py` + 6 个 `build_production_pipeline` 测试 + 新增 V1–V9 测试）。 |
| FEA00A-SR3-P2-7 | P2 | 卡 `:34–35`（`tests/core/**`、`tests/pipeline/**`）、`:94`（scope 正文）、`:109`（AC8） | **测试写域过宽、影响面未覆盖**：`tests/core/**` 57 个 py 文件（含 `test_architecture.py`、`test_settings_*`、`test_p13_*` 等无关文件）与 `tests/pipeline/**` 9 个文件被整体放开，`conftest.py` 亦可改；而真正需要改的仅是 8 个 G7 文件 + `assemble_core_services` 影响面的少数 core/pipeline 测试 + 新增 V1–V9 测试。反过来，`assemble_core_services` 还影响 `tests/m2_acceptance/` 4 文件、`tests/infrastructure/test_plugin_sandbox.py`、`tests/providers/test_detection_manga.py`（不在写域，AC8 亦未要求其回归证据）。 | 收窄为枚举受影响文件（`test_bootstrap.py`、`test_page_catalog_modes.py`、`test_core_assembly.py`、`test_core_detect.py`、`test_sfx_assembly.py`、`test_sfx_policy_settings.py`、`test_regionless_rebinding.py`、`test_pipeline_production_seam.py`、G7 的 5 个 providers 文件 + 新增测试路径）；Handoff 逐项列出**所有**改动测试；AC8 增补「core_assembly 接线影响面只读回归结果（passed/failed/skipped）」，失败按范围变更处理。 |
| FEA00A-SR3-P2-8 | P2 | 卡 `:30–32`、`:93–94`；方案 §15.6 `:914`、`:919`、`:931` | **§15.6 扩张理由与 FEA-10 写域重叠未记录**（r2-P2-5① 残留）：卡内写了 R-ART-4/5 的最小接线约束，但未说明「相对 §15.6 FEA-00a 建议行的扩张依据（D1=②/D2=② + §15.6 `:914` 非实际写权）」，也未声明与 FEA-10 写域（方案 `:931` 含 `src/infrastructure/pipeline/`）的重叠与「FEA-10 未释放、本卡只做接线」的约定。 | 在卡内（或 ADJ errata）补一段；后续 FEA-10 范围冻结时引用该约定，避免把本卡接线视为 FEA-10 既有改动。 |
| FEA00A-SR3-P2-9 | P2 | 卡 `:139–154`（对账表）、`:184`（closeout）；`REBASELINE_PLAN.md:28` | **对账/指针精度**：①v3 把 r2 的 P2×7 重编号为 `r2-P2-1…11`，closeout 写「P2×11 全部处理」，与 r2 报告实际 ID 不一致；r2-P2-1⑥（幂等机制）与 r2-P2-5①（§15.6 记录）无处置行；②表 r2-P2-2 声称正文有「按 schema 必填列核对并在 Handoff 登记」，R-ART-1（`:77`）正文无此句；③`REBASELINE_PLAN.md:28` 仍写「范围冻结 **v2** 待独立复核」（v3 已提交）。 | 对账表改为按 r2 原 ID（`P2-1…P2-7`）映射或加 `r2 原 ID → v3 ID` 列；补两条未处置项；补正文与表一致；`ready` 前把 PLAN:28 改为 v3/最终 head。 |
| FEA00A-SR3-P2-10 | P2 | 卡 `:86`（R-SEAM-1）、`:80`（R-ART-3）；`service.py:788–789`、`:760–790` | **seam 结果的 service 映射与 `db_failed` 候选状态未定义**：R-SEAM-1 新增 `paused`/`cancelled` 结果，但 `service.commit_step_result` 现有 else 分支把未知状态映射为 `DB_FAILED`/`TARGET_NOT_FOUND`（`service.py:788–789`），Run/Step 状态语义与 AC1/V5 期望未写；另外 R-CAND-3 说「seam 拒绝/中止 → 独立事务置 `abandoned`」，而 R-ART-3 只写补偿（discard/remove），未明确 `db_failed`（事务异常）路径也要置 `abandoned`（否则该次 attempt 的 prepared 行要等启动清扫才转态，V4/AC2 的口径不明确）。 | 在 R-SEAM-1/R-CAND-3 写明各 `commit_step` 结果（`applied`/拒绝/`paused`/`cancelled`/`db_failed`）对应的候选状态转换与 service 返回值/Run 状态；`db_failed` 用同一「独立事务置 `abandoned`」规则；在 AC9 登记 `service.py`/`pipeline.py` 的接口改动。 |

**P0 = 0。P1 = 0。P2 = 10（FEA00A-SR3-P2-1…10，均非阻断）。**

## 5. 结论与边界声明

1. **decision: `approved`**（P0 × 0 / P1 × 0 / P2 × 10）。r2 的两条阻断项（三态候选级联、artifact 拒绝路径孤儿文件）已在规则与 AC 层面真正闭合；v3 未引入新的阻断项。10 条 P2 是精度/一致性问题，建议 r3-P2-1/2/3/4 在 `ready` 提交或实现首日顺手改文，其余按 Handoff 登记在实现中处理，均不阻断 `ready`/实现启动。
2. **本次复核只针对范围冻结，不构成实现验收**；`approved` 不等于 Task 完成或可发布。实现后仍需独立实现复核（`doc/reviews/FEA-00A-IMPL-r1.md`）、AC 逐项证据、集成与 closeout。
3. **独立性**：本席位（`fea00a-scope-reviewer`）为 DSH（Lead）以 fresh 独立上下文派发的 Agent Teams teammate（第三轮沿用同一独立席位），未参与该 Task 的起草、实现或返修；只读被审 head，未修改任何被审文件（除本报告）、未 commit、未 push。
4. **建议的下一步（供 DSH）**：①按 AC10 与本报告将范围冻结置 `approved` 并在 `ready` 提交中更新 `base_commit` 为最终冻结 head（当前卡内 `base_commit: 419f891c0`）；②在 `ready` 提交中顺手修正 r3-P2-1（R-SEAM-4 target_type 写法）、r3-P2-2（字段清单/`media_artifacts` 列）、r3-P2-3（R-ART-2 顺序与子表处理）、r3-P2-4（删除例外清单）；③其余 P2 在实现 Handoff/证据中处理；④`ready` 派 Codex 实现，完成后按 AC10 派独立实现复核。

—— 报告结束（`decision: approved`；P0×0 / P1×0 / P2×10；r2 处置：P1-1/P1-2 已解决，P2×7 已逐项落实并结转 3 条精度残项）。
