---
task_id: FEA-00A-IMPL-1
reviewer: fea00a-impl-reviewer
reviewer_kind: subagent
author: Codex（实现者，Handoff 署名；交付 commit 的 Git author 为 peakwheat-pixel）
base_commit: c7b9d59e6
reviewed_head: 007094517
decision: approved
p0: 0
p1: 0
p2: 12
---

# Review：FEA-00A-IMPL-1（实现复核 r1）

## 审查者身份与来源

| 项 | 内容 |
|---|---|
| Reviewer | `fea00a-impl-reviewer` |
| 来源 | DSH 以 **fresh 独立上下文** 派发的只读复核子 agent（会话/子任务名 `fea00a-impl-reviewer`，Team Lead = `lead`） |
| 独立性 | 未参与 FEA-00A-IMPL-1 的起草、实现或返修；未修改被审代码；只读被审 head |
| 日期 | 2026-11-01 |
| 被审对象 | worktree `G:\CODEX\New Manga.workspace\FEA-00A-IMPL-1`（branch `feat/fea-00a-impl`），`reviewed_head = 007094517`，前置基线 `c7b9d59e6` |
| 依据 | 范围冻结卡 `doc/tasks/FEA-00A-IMPL-1.md`（R-CAND-1…4 / R-ART-1…5 / R-SEAM-1…4、AC1–AC10、V1–V9）、`doc/plan/FEA-00A_PREP.md`、范围复核 scope-r1/r2/r3（r3 approved）、Handoff `doc/handoffs/FEA-00A-IMPL-951b74daa.md`、证据 `verification/FEA-00A-IMPL-1/**` |

审查环境事实：Windows + PowerShell 7.6.8；测试以 `uv run --no-project --cache-dir %TEMP%\...` 装入 `pytest==9.1.1 / pillow==12.3.0 / pypdfium2==5.13.0 / mobi==0.4.1 / numpy`，Python 3.14.6。所有测试在 `%TEMP%` 独立目录运行，附加 `-p no:cacheprovider` 与 `PYTHONDONTWRITEBYTECODE=1`；运行前后 `git -C <worktree> status --porcelain` 均为空，未污染仓库。

## 结论

**`approved`**：P0 = 0，P1 = 0，P2 = 12（见 Findings）。

实现与冻结卡的 R-CAND / R-ART / R-SEAM 主干一致，AC1–AC9 有可复现的真实测试支撑，证据数字与代码/测试真实对应（我独立复跑了 194 / 180 两组并核对 V1–V9 用例的真实 assembly 来源）。P2 项均为非阻断性一致性问题、范围/并发/性能边界或治理记录问题，可由 DSH 在集成与 closeout 时处置；其中 **R1-P2-01（R-SEAM-4 字面偏差）建议 DSH 在卡上追加裁决记录**，**R1-P2-08（治理记录与交付 head 不一致）应在集成时统一更新**。

## 逐项核查结果（对应派发单第 1–8 项）

### 1. 越界检查：通过（未越界）

命令与输出（worktree 内执行）：

```
git -C <wt> diff --stat c7b9d59e6..007094517
 39 files changed, 2224 insertions(+), 368 deletions(-)
git -C <wt> rev-list --count c7b9d59e6..007094517  ->  1
git -C <wt> branch --show-current                  ->  feat/fea-00a-impl
git -C <wt> status --porcelain=v1                  ->  （空，clean）
```

- 文件构成：`src/` 8 个、`tests/` 11 个、`doc/handoffs/FEA-00A-IMPL-951b74daa.md` 1 个、`verification/FEA-00A-IMPL-1/**` 19 个（全部文本，无二进制/大文件）。
- 逐项对照卡的 `allowed_paths`（`doc/tasks/FEA-00A-IMPL-1.md:21–41`）：8 个 src 文件分别落在 `src/infrastructure/sqlite/pipeline.py`、`src/infrastructure/providers/**`、`src/infrastructure/pipeline/assembly.py`、`src/bootstrap/core_assembly.py`、`src/ports/repositories/storage.py`、`src/application/tasks/**`（D2 授权）；11 个 tests 文件落在 `tests/core/**`、`tests/pipeline/**` 与卡内逐条列名的 `tests/providers/` 5 文件（`t111_support.py`、`test_detect_handler.py`、`test_full_chain.py`、`test_handlers_pipeline.py`、`test_retype_redetect_persistence.py`）；handoff 匹配 `doc/handoffs/FEA-00A-IMPL-*.md`；证据目录匹配 `verification/FEA-00A-IMPL-1/**`。**无越界文件。**
- 禁止面核查：`git diff --name-only` 中 **无** `schema.py`、无 `migrations`、无 `apps/**`、无 `doc/plan/**`（15 个冻结契约字节未改）、无 `doc/contracts/**`、无 `doc/reviews/**`、无 ADJ、无 `doc/STATUS.md` / `REBASELINE_PLAN` / `TASK_LEDGER`。`git -C <wt> grep "adopt_current" -- src tests` → `NONE`（被移除的旧 API 无残留引用）。
- 提交信息：`007094517 feat(fea-00a): 候选暂存与 seam 同事务提交（region + artifact 三处零变化）`，author `peakwheat-pixel`（与 Handoff 署名 Codex 的差异见 R1-P2-08）。

### 2. R-CAND 实现：通过

- **R-CAND-2（父行禁止 DELETE / INSERT OR REPLACE）**：`_write_run` 已改为 UPSERT——`src/infrastructure/sqlite/pipeline.py:454–499`，`INSERT INTO pipeline_runs … ON CONFLICT(run_id) DO UPDATE SET …` 位于 `:463`。对照 base（`git show c7b9d59e6:src/infrastructure/sqlite/pipeline.py` 第 433 行）原为 `DELETE FROM pipeline_runs WHERE run_id = ?`，已消除。
- **三态行存续**：写子图前先快照该 run 的全部候选（`pipeline.py:443–452`），随后只重建子表（`pipeline_run_targets` / `pipeline_tasks` / `step_runs` / `step_result_candidates`，`:503–514`），再按 `candidate_id` 回插，`run.candidates` 同 id 优先（`:566–598`）。回插全部发生在同一事务内，失败即整体 rollback，不存在"删了没回插"的中间提交。
- **四条路径适用**：成功 persist → `service.py:758–764` → `write_in_current_transaction` → `_write_run`；seam 失败 → `service.py:801–823`（新增 pending 诊断候选后 `_persist`）；`recover_running_runs` → `service.py:1139–1156`（走 `_persist`）；`control_run` pause/stop → `service.py` 内 `_persist`（pause 分支与 stop 分支）。断言证据：`tests/core/test_fea00a_pipeline_seam.py:154–162`（V1 断言同一步 `abandoned` + `pending` 双行、2 个不同 candidate_id、prepared 行 `resolved_at` 非空——这是对 R-CAND-2 的判别性用例：旧 `DELETE` 会级联删掉 abandoned 行）；`:404–407`（V8 断言 `resolved` + `abandoned` 各 1 且 revision 行不交叉）。
- **R-CAND-4（启动清扫与计数）**：`cleanup_staged_candidates` 在 `pipeline.py:1202–1320`，返回 `{"abandoned_prepared", "discarded_temps", "removed_orphans", "orphaned_paths", "errors"}`（`:1211`、`:1300–1317`）；`PipelineService._run_startup_cleanup` 在 `service.py:221–226`，由 `recover_running_runs`（`:1141`）与首次执行（`:894`）触发，结果暴露为 `startup_cleanup_result`（`:217–219`）。断言证据：`test_fea00a_pipeline_seam.py:305`（重启后 `abandoned_prepared == 1`）、`:329–330`（artifact 重启后 `abandoned_prepared == 1` 且 `removed_orphans == 1`）。
- **三态状态机**：`prepared` 仅在 prepare 产生（`step_writes.py:239–250` region、`:368–385` artifact）；seam 成功在同事务置 `resolved`（`pipeline.py:977–983`，带 `WHERE status='prepared'` 幂等守卫）；拒绝/中止在**独立事务**置 `abandoned`（`_reject_prepared`，`:1150–1163`）；启动清扫把残留 `prepared` 置 `abandoned`（`:1303–1317`）。未新增候选硬删路径：全仓 `DELETE FROM step_result_candidates` 仅 `library.py:571`（既有页面清理）与 `pipeline.py:513`（同事务快照/回插），`DELETE FROM pipeline_runs` 仅既有 `purge_targetless_runs`（`pipeline.py:1578`，R-CAND-3 明示例外）。

### 3. R-ART 实现：通过

- **R-ART-1（prepare 只暂存）**：`ArtifactStepWriter.prepare_revision`（`src/infrastructure/providers/step_writes.py:277–404`）只 `storage.write_temp`（`:322`）+ `storage.verify_temp`（`:325`）；**无** `publish`、**无** `INSERT/UPDATE media_artifacts`、**无** `INSERT artifact_revisions`（我用 `git diff … -- src/ | grep` 与 AC4 静态测试双向核对，见 `tests/pipeline/test_fea00a_source_boundaries.py:22–33`）。候选 payload 冻结字段齐全（`:332–353`）：`temp_handle/relative_path/artifact_type/page_id/book_id/chapter_id/base_revision_id/sha256/size/mime_type/content_format`，`artifact_id` 仅在已存在时写入（`:354–355`），**未虚构 `revision_no`**（`PreparedArtifact.revision_no = None`，`:397`；边界测试 `test_fea00a_source_boundaries.py:48` 断言）；`mime_type` 为必填并显式校验（`:301–302`）。返回 `revision_updates` 由 handler 用预生成真实 revision id 组成（`handlers.py:943–956`）。region 侧 `_persist` 只写 prepared 候选（`step_writes.py:178–254`），不再写 `region_revisions` / `regions.text_json`（与 base diff 对照确认）。
- **R-ART-2（seam 顺序）**：`SqliteTargetCatalog.commit_step`（`pipeline.py:816–996`）实际顺序为 ①`BEGIN IMMEDIATE`（`:833`）→ ②按 token 找回并校验 prepared 候选（`:837–920`，含 `base_revision_id`/`temp` 存在性/`storage` 非空）→ ③pause/cancel 判定（`:938–953`）→ ④DB 写：`_write_region_candidate`（`:998–1030`，插 `region_revisions` + 同一条 UPDATE 写 `text_json` 与指针 CAS）与 `_write_artifact_candidate`（`:1032–1088`，首 revision `INSERT media_artifacts(current_revision_id=NULL)` → `INSERT artifact_revisions`（含 `revision_no`）→ 指针 CAS）→ `stage_updates`（`:968–974`）→ `persist()`（`:975–976`）→ 候选置 `resolved`（`:977–983`）→ ⑤publish（`:984–990`，`_publish_idempotent`：目标已存在且 sha256/size 相同视为已发布）→ ⑥`COMMIT`（`:991`）。与卡内 R-ART-2 顺序逐项吻合；V9 用 trace 断言 `begin < artifact < revision < pointer < stage < resolved < publish < commit`（`test_fea00a_pipeline_seam.py:508–518`），并在 publish 回调内断言"事务仍打开、候选已 resolved"（`:495–499`）。
- **拒绝路径先于 publish**：revision/lock/stale/pause/cancel/存不存在/未知键等全部在 `:867–953` 返回 `_reject_prepared`，早于 `:955` 的 DB 写与 `:984` 的 publish；V9 失败分支断言 `media_artifacts=0`、`artifact_revisions=0`、temp 与最终文件均不存在、`orphaned_paths == []`（`:474–484`）。
- **R-ART-3（失败补偿与清扫）**：`_reject_prepared`（`pipeline.py:1132–1166`）先回滚（`:1135–1136`），对已 publish 的路径在回滚后确认无 `artifact_revisions` 引用再 `remove_managed` 补偿（`:1138–1147`，失败写入 `orphaned_paths`），随后 `discard_temp`（`_discard_candidate_temps`，`:1168–1200`，含 temp 目录逃逸/符号链接防护），最后独立事务置 `abandoned`（`:1150–1163`）。启动清扫对 prepared artifact 候选校验并 `discard_temp`、对无 revision 引用的最终文件 `remove_managed`（`:1233–1298`）。注入验证：V4（publish 后延迟 FK 失败 → 回滚 + 文件补偿，`:250–260`）、V9（publish 抛错 → 零推进，`:474–484`）、V6-artifact（崩溃重启清扫，`:310–332`）。
- **R-ART-4（storage 注入 / None fail-closed）**：`SqliteTargetCatalog.__init__(conn, storage=None)`（`:763–768`）；`storage=None` 遇 artifact 候选明确返回 `db_failed` 而非静默 publish（`:921–924`），且候选 `abandoned`、temp 保留并记入 `orphaned_paths`（test `:412–441` 断言 `temp` 存在、`orphaned_paths` 含该路径、后续带 storage 的清扫 `discarded_temps == 1`）；生产装配 `core_assembly.py:1377–1381` 始终传入 `storage`（`build_production_pipeline(..., storage=storage)`），`assembly.py:31/40` 只做参数最小透传。
- **R-ART-5（接线边界）**：`src/ports/repositories/storage.py` 仅新增既有 `ManagedStorage` 已实现的 `remove_managed` 端口方法（diff `:50–53`）；`assembly.py` / `core_assembly.py` 仅新增参数与注入，未重构组合根、未改公开签名（`build_production_pipeline` 新增带默认值关键字参数）。

### 4. R-SEAM：通过（含 1 项字面偏差，见 R1-P2-01）

- **R-SEAM-1**：pause/cancel 判定位于 `BEGIN IMMEDIATE`（`:833`）之后、`:955` 的 live 写与 `:984` 的 publish 之前（`:938–953`；其中 `:938–945` 还额外读取 `pipeline_runs.pause_requested/cancel_requested` 持久列，覆盖跨步骤的并发控制请求）；命中后 `rollback`（`:1135–1136`）并由**独立事务**置 `abandoned`（`:1152–1160`）。V5 断言 `outcome.status`、region 三值不变、候选 `abandoned`、Run/Step 状态映射（`paused/interrupted`、`cancelled/cancelled`）且 `not core.conn.in_transaction`（`test_fea00a_pipeline_seam.py:269–288`）。
- **R-SEAM-2（AC3 双证据）**：V7（`:335–384`）同时使用 ①`sqlite3.Connection.set_trace_callback`（断言语句序：插 revision < 写 live text/指针 < 候选 resolved < 单次 `commit`，`:364–372`）与 ②独立 `mode=ro` + `query_only=ON` 连接（在 COMMIT 时刻读到旧值、提交后读到新 pointer，`:342–345`、`:353–357`、`:373–379`）；满足卡内"至少 ①+②"。
- **R-SEAM-3（真实生产 assembly）**：新增测试全部经 `assemble_core_services`（`test_fea00a_pipeline_seam.py:31–42`），其中 `core.pipeline` 来自 `build_production_pipeline`（`core_assembly.py:1377–1381`、返回 `CoreServices(pipeline=pipeline)` `:1473–1486`）；仅使用卡内允许的 `mock_local_providers=True`（`core_assembly.py:1136`，只向 provider registry 注册 mock 检测/OCR/翻译替身，不替换 executor/catalog/pipeline），**无** fake executor / InMemory catalog / 测试专用 pipeline。V1–V9 实际跑通即证明链路为 `PipelineService → ProductionStepExecutor → ProductionHandlers → 真实 writer → SqliteTargetCatalog.commit_step → SQLite`。
- **R-SEAM-4（分支键守卫按 target_type 分派）**：`:855–870`——未知 `target_type` → `db_failed`（`:857–860`）；`REGION` 允许键集 `{"region", *ARTIFACT_TYPE_DIRS}`（`:863`）；`PAGE` 只允许 artifact 键（`:865`）；未知键 → `db_failed`（`:867–870`）。**偏差**：REGION 分支未"保持原样"（base 为 `key != "region"` 全拒，`git show c7b9d59e6:…:764`），现允许 artifact 键——这是必要的（现有 mask / mask_refine / inpaint clean 等 artifact handler 本来就是 Region-scoped，见 `handlers.py:943–956` 改前改后与 `apply` 逻辑），否则所有 region-scoped artifact 步骤会退化为 `db_failed`。V9 正是以 REGION 作用域覆盖该路径。见 R1-P2-01。

### 5. 证据真实性：通过（重点核验，未发现伪造 PASS）

| 证据 | 声明 | 我的独立核验 | 判定 |
|---|---|---|---|
| `final-pytest-log.txt` | 14 文件 `194 passed`，EXIT 0 | 原命令复跑 → `194 passed in 16.05s`，EXIT=0 | 真实 |
| `production-assembly-v1-v9.log` | 11 passed, 1 deselected | 全文件复跑 12 passed（含 deselect 的 storage=None 用例），`-k test_v` 过滤数量与声明一致 | 真实 |
| `ac8-outcome-comparison.md` / `baseline-test-log.md` | 修前 180 passed（仅存批次总数，未存逐文件） | 用 `git archive c7b9d59e6 src tests pytest.ini` 导出**基线快照到 %TEMP%** 后原命令复跑 → `180 passed in 17.54s`；且 180 + 14（新增两文件 12+2 项）= 194 与修后数字自洽 | 真实 |
| `ac8-post-per-file-log.txt` / `*-results.json` | 12 文件逐文件全通过 | 我复跑了其中 8 文件 → `94 passed`，与证据逐文件计数之和（23+3+7+24+8+4+24+1=94）**完全一致**；`core-assembly-impact-results.json` 5 文件计数（8/40/19/19/7）与文件内输出一致 | 真实 |
| V1–V9 来源 | "经 assemble_core_services + build_production_pipeline 真实执行，无 fake executor" | 逐行核对测试代码（`:31–42`、`:71–109`）与装配代码（`core_assembly.py:1377–1381/1473–1486`、`assembly.py:31/40`），确认 `.pipeline`/`.conn`/`.storage` 均来自生产装配；`ProductionStepExecutor` 未被替换 | 真实 |
| AC8 表格完整性 | 逐文件、helper 单列 | `ac8-outcome-comparison.md:5–93` 为 7 个 outcome 文件逐测试名 87 行；`:95–97` 把 `t111_support.py` 单列为"非 outcome 对照"；`:99–109` 另列 core_assembly 接线影响面 5 文件；符合"G7 8 文件（7 outcomes + helper）"口径 | 真实 |
| `governance-checks.txt`（pin FAIL） | 官方脚本 FAIL 15/15；CRLF→LF 归一化后 15/15 与 pin 一致 | 我独立重算 15 个契约文件：原始字节 0/15 匹配，`CRLF→LF` 归一化后 **15/15 完全匹配**，无未匹配项（C01b 原始文件 CRLF 计数 140，`core.autocrlf=true`） | 真实（FAIL 为环境行尾所致，且**未**被写成 PASS） |
| AC7② | 只在一次性 fixture 上跑通，用户旧库 NOT_RUN | `legacy-db-audit-record.md` / `legacy-db-audit-result.json` / Handoff 表 `:26` 均如实标 PARTIAL/NOT_RUN；审计脚本 `mode=ro` + `PRAGMA query_only=ON`、不创建/恢复/复制备份，且比较逻辑与 `Region.snapshot_state()` 的 `text` 块格式一致 | 真实（PARTIAL 如实） |

未发现"未执行却写 PASS"；唯一一处为 Handoff 中 `status: blocked`、"无 commit"的措辞已与真实 head 不一致（属交付记录问题，见 R1-P2-08），但不构成对代码/测试的虚假声明。

### 6. 测试可复现：通过（我实际运行，结果与证据一致）

（命令在 worktree 根目录执行，输出摘要如下；完整 EXIT 均为 0）

| # | 命令 | 我的结果 | 与证据对照 |
|---|---|---|---|
| A | `python -m pytest tests/core/test_fea00a_pipeline_seam.py tests/pipeline/test_fea00a_source_boundaries.py -q` | `14 passed in 8.11s`，EXIT=0 | seam 文件 12 项 + 边界 2 项，与 `production-assembly-v1-v9.log`（11+1 deselected）及 `prepare-boundary-checks.log`（2 passed）一致 |
| B | `python -m pytest tests/core/test_bootstrap.py tests/core/test_page_catalog_modes.py tests/pipeline/test_pipeline_production_seam.py tests/pipeline/test_regionless_rebinding.py tests/providers/test_detect_handler.py tests/providers/test_full_chain.py tests/providers/test_handlers_pipeline.py tests/providers/test_retype_redetect_persistence.py -q` | `94 passed in 14.77s`，EXIT=0 | 与证据逐文件计数之和 94 完全一致 |
| C | 证据 `final-pytest-log.txt` 的 14 文件原命令 | `194 passed in 16.05s`，EXIT=0 | 与证据 194 一致 |
| D | 基线快照（`git archive c7b9d59e6`）+ 12 文件基线命令 | `180 passed in 17.54s`，EXIT=0 | 与 AC8 修前 180 一致 |

`skipped` 实测为 0（A/B/C/D 均无 skip 行）；stderr 中的 QML `TypeError: Cannot read property …` 噪声在全局解释器环境下同样出现，与本变更无关，且不影响用例结果（测试自身只断言退出码与产物）。运行后 `git -C <wt> status --porcelain` 为空（仅 pytest/`__pycache__` 被 .gitignore 忽略），未污染仓库。

### 7. AC 诚实性：通过

- **AC7 如实标 PARTIAL**（未核验真实旧库），未把 fixture 结果冒充旧库证据；Handoff `:26`、`legacy-db-audit-record.md`、`baseline` 与证据口径一致。**AC7 在集成时不应按 PASS 关闭**，需 DSH 决定是否要求用户旧库样本（R1-P2-10）。
- AC1 的 7 类注入与断言齐全：V1 revision 冲突、V2 Lock 冲突、V3 `STALE_RUN_SNAPSHOT`、V4 DB 失败（延迟 FK）、V5 pause/cancel（2 参数）、V6 崩溃重启（2 路径）——全部断言 `text_json`/`current_revision_id`/`region_revisions` 计数前后一致（`_region_snapshot`，`:112–121`）。
- AC2/AC3/AC4/AC5/AC6 均有对应已执行用例（见第 2–4 项），AC8 有逐文件表格与真实跑数，AC9 在 Handoff `:48–55` 逐文件登记（`service.py`/`store.py`，四列齐全）。AC10 由本 Review 满足（待 DSH 登记）。
- 空证据检查：`verification/FEA-00A-IMPL-1/` 每个文件都有对应实际命令/输出或 JSON 结果，未发现空壳文件或占位文本。

### 8. 代码质量：基本通过（P2 边界事项见 Findings）

- **事务边界**：写事务统一用 `BEGIN IMMEDIATE`（commit_step `:833`、`_reject_prepared` 独立事务 `:1152`、启动清扫 `:1303`、store `put_many/accept/accept_restart`）；seam 内所有 live 写 + `persist()` + publish 归属单一事务，异常路径一律 `rollback` 后进独立事务写 `abandoned`；`_reject_prepared` 显式处理"仍在事务内"情况（`:1135–1136`）。
- **幂等**：publish 幂等（`_publish_idempotent` `:1106–1130`）；候选状态迁移带 `WHERE status='prepared'`（`:980–983`、`:1156–1159`、`:1307–1311`）；`_write_run` UPSERT + 候选按 id 去重回插；`accept` / `accept_restart` 的 idempotency 语义未改。
- **并发**：V8 覆盖"同 region 两候选一胜一败、revision 行不交叉"；但该用例是**同一连接双线程**（`test…:396–401`），并非跨连接并发，且 `_reject_prepared` 的 `rollback()` 是连接级——见 R1-P2-05。
- **SQL 安全**：新增/修改语句全部参数化；`git diff … -- src/` 中无 f-string SQL（我以 `execute(f"` 扫描，无命中）；动态标识符仅来自 `ARTIFACT_TYPE_DIRS` 常量与内部枚举，无用户输入拼接。清理侧另有 temp 目录逃逸与符号链接防护（`_discard_candidate_temps` `:1183–1195`，孤儿扫描跳过 symlink `:1276–1281`）。
- **遗留调试代码**：`src/` 新增行无 `print(`/`TODO`/`FIXME`/`pdb`；测试侧有 1 处未使用变量（R1-P2-06）。
- **既存行为**：`adopt_current` 移除后无引用（grep NONE），其唯一语义（artifact 指针 CAS）已由 seam 在同一事务内完成（`_write_artifact_candidate:1081–1087`），并额外保证"行/指针/文件"三者一致；artifact handler 现在必须传 `pipeline_run_id/step_run_id`（`step_writes.py:296–300`），三处生产调用均已补（`handlers.py:580–581`、`:630–631`、`:717–718`）；region writer 同样要求 run/step id（`step_writes.py:187–192`），生产调用已补（`handlers.py:438–439`、`:524–526`）。
- **测试改动是适配而非弱化**：`test_pipeline_production_seam.py` 从"直连 catalog 手插 revision"改为"真实 writer + 真实 pipeline"并**新增**候选 `resolved` 断言（`:99–136`）；`test_handlers_pipeline.py` 补 run/step id 后**新增**"prepare 不写 live、候选为 prepared"断言（`:800–830`）；`test_bootstrap.py` / `test_page_catalog_modes.py` 只是用 `_seed_artifact_for_reader_test` 替代已移除的 `adopt_current` 夹具（`test_bootstrap.py:44–78`）；其余 4 个 provider 文件仅是 `storage=` 注入（各 +1 行）。未发现断言被删除或被削弱、未发现 skip/xfail 掩盖。

## Findings

| ID | 级别 | 位置 | 问题 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| R1-P2-01 | P2 | `src/infrastructure/sqlite/pipeline.py:862–870` | 与冻结文本 R-SEAM-4 字面不一致：卡要求"REGION 分支保持原样（键必须为 region）"，实现允许 `{"region"} ∪ ARTIFACT_TYPE_DIRS`。 | `git show c7b9d59e6:…pipeline.py:764` 原守卫为 `key != "region"` 全拒；`handlers.py:943–956` 证明 mask/mask_refine/clean 等 artifact 步骤是 Region-scoped，若按字面实现会全部 `db_failed` | 实现选择保留既有行为属合理；请 DSH 在卡上追加 r1 裁决/范围冻结 v4 修正 R-SEAM-4 措辞（"REGION 分支保持区域键 + 允许 page-owned artifact 键"），并保留 V9 作为该分支的验收证据 | open（待 DSH 裁决） |
| R1-P2-02 | P2 | `src/infrastructure/sqlite/pipeline.py:1262–1298` | 启动清扫按"整个 `books/**` 非 original 产物目录 + 无 `artifact_revisions` 引用"删除文件，范围大于本 Task 候选，且无 dry-run / 上限 / 分目录豁免。 | 我核对了当前所有 managed 写入路径：`importing.py:274–287`（original，被排除）、`sqlite/artifacts.py:131–162`（入库）、`step_writes.py`（本 Task，入库）、`render_preview.py`（独立 derived_root，不受影响）；当前代码内未见"合法但不入库"的写入者，故风险主要是历史遗留/未来特性产物被清 | 在 Task 或后续 Task 记录该清扫范围裁决；建议加"仅清理本 Task 候选相关目录/记录计数与清单日志"或至少保留 `orphaned_paths` 清单可审计（现已具备后者） | open（集成时确认） |
| R1-P2-03 | P2 | `src/application/tasks/service.py:213–226`、`:894`、`:1141` | 启动清扫是"首次执行/首次 recover 时惰性触发"，`_startup_cleanup_done` 无锁；若同一进程内多线程启动不同 Run，理论上可与他人在途 prepared 候选竞争。 | `check_same_thread=False`（`connection.py:347`）意味着同连接可跨线程使用；`_run_startup_cleanup` 只读 `if done: return` 无同步原语 | 生产当前单 Run 顺序执行为主，风险低；建议把清扫移到装配/恢复的独占路径，或加锁并显式声明"每进程仅一次" | open |
| R1-P2-04 | P2 | `src/infrastructure/sqlite/pipeline.py:566–598` | 回插候选按 `step_run_id` 直接 INSERT，若该 step 已不在重建后的 `run.step_runs` 中，FK（`step_result_candidates.step_run_id → step_runs ON DELETE CASCADE`）会抛 IntegrityError，使整次 `_write_run` 失败（run 无法持久化）。 | 现状流程（prepare→seam 同调用内完成、restart 走新 run_id、recover 不改 step 集合）难以触发；无测试覆盖该组合 | 建议回插前过滤/隔离 step 不存在的候选（或捕获后降级为候选清理并计数），并补一条"候选 step 被重规划移除"的用例 | open |
| R1-P2-05 | P2 | `tests/core/test_fea00a_pipeline_seam.py:387–409`；`src/infrastructure/sqlite/pipeline.py:1135–1136` | V8 的"并发"是同一连接双线程：败者多半走 `BEGIN IMMEDIATE` 冲突 → `db_failed` 分支，而非真实跨连接 revision 冲突；且 `_reject_prepared` 的 `rollback()` 是连接级，可能回滚另一线程的在途事务。测试结果依赖时序。 | 我复跑通过，但机制如左；V3 已演示可用第二连接（`sqlite3.connect(..., timeout=10)`）做真实并发 | 建议 V8 改为第二连接并发（或补充跨连接用例），并让 `_reject_prepared` 只在"本事务确由本调用开启"时才 rollback（或用 SAVEPOINT） | open |
| R1-P2-06 | P2 | `tests/core/test_fea00a_pipeline_seam.py:196–199` | V3 遗留未使用变量 `second` / `mirror_store`（创建了第二连接与 store 却未使用），属调试残留。 | 该函数只在 `finally` 中 `second.close()`，`mirror_store` 从未引用 | 删除或改为真实并发/独立读取用法 | open |
| R1-P2-07 | P2 | `tests/core/test_fea00a_pipeline_seam.py:412–441`；`doc/handoffs/FEA-00A-IMPL-951b74daa.md:26`、`:78` | `storage=None` 用例是在真实装配**之后**把 `_catalog._storage` 置空，未覆盖"以 `build_production_pipeline(storage=None)` 构造"的路径；Handoff "storage=None 用例通过真实 assembly 单独执行"的表述强于实际覆盖。 | 测试第 420 行 `core.pipeline._catalog._storage = None`；无 `build_production_pipeline(..., storage=None)` 的构造断言 | 补一条构造即 `storage=None` 的装配/失败路径用例，或把 Handoff 措辞改为"装配后置空 catalog storage"；R-ART-4 的"None fail-closed"核心语义已被覆盖，故非阻断 | open |
| R1-P2-08 | P2 | `doc/tasks/FEA-00A-IMPL-1.md`（head 版本 YAML）；`doc/handoffs/FEA-00A-IMPL-951b74daa.md:6–12`；提交体 | 治理记录与交付不一致：卡仍 `status: ready`、`delivery_head: null`、`branch/worktree: null`、AC1–AC10 注记仍为"<<PARTIAL: 范围冻结；实现未开始>>"、`reviewer: c01b-reviewer`；Handoff `status: blocked`/`delivery_head: null` 且正文称"没有实现 commit"；提交体写 `doc/handoffs/FEA-00A-IMPL-uncommitted.md`，实际文件为 `-951b74daa.md`；commit author 为 `peakwheat-pixel` 而 Handoff author 为 Codex。 | `git -C <wt> show HEAD:doc/tasks/FEA-00A-IMPL-1.md` 前 20 行；`git -C <wt> ls-tree -r --name-only HEAD -- doc/handoffs`；`git log --format='%an'` | 该差异属"提交受阻原记录 + 后续提交"的产物，非代码缺陷；请 DSH 在集成/closeout 统一更新卡（delivery_head、branch/worktree、AC 证据指针、reviewer）、Handoff 元数据与提交体命名，并在集成提交中注明 Git author 身份 | open（DSH 处置） |
| R1-P2-09 | P2 | `verification/FEA-00A-IMPL-1/ac8-outcome-comparison.md:111` | 同一文件内数字不一致：该行写"与完整 **193** 项汇总有重叠"，而 `final-pytest-log.txt` 与其它证据为 **194**。 | 对比 `:3`（194 passed）与 `:111`（193 项） | 更正为 194（或说明差异来源） | open |
| R1-P2-10 | P2 | `verification/FEA-00A-IMPL-1/legacy-db-audit-*.{md,json}`；`doc/tasks/FEA-00A-IMPL-1.md:108` | AC7② 真实旧库仍 NOT_RUN，只验证了脚本流程（fixture）。证据已如实标 PARTIAL，但 AC7 在集成时不能按 PASS 关闭。 | Handoff `:26`、`legacy-db-audit-record.md`、审计结果 JSON 的 fixture 路径 | DSH 在集成时决定：接受 PARTIAL 并记录限制，或要求用户提供旧库副本后补跑（脚本已固定可复用） | open（DSH 处置） |
| R1-P2-11 | P2 | `src/infrastructure/sqlite/pipeline.py:1090–1104`、`:984–991` | 大 artifact 在**写事务内**做 `verify_temp`/sha256 校验与 publish，写锁持有时间随文件大小线性增长；Handoff 已披露"未做规模化基准"，但无上限保护。 | 代码路径如左；`v9-artifact-timing.log` 仅 0.40s 小文件 | 建议后续任务对 seam 内校验做基准，必要时把 sha256 结果随 prepared 候选缓存（payload 已有 sha256/size，只需校验文件未被替换），或对超大 artifact 设阈值 | open（非本 Task 范围） |
| R1-P2-12 | P2 | `src/application/tasks/service.py:825–826`、`:989–991` | `db_failed` 中出现 `STALE_RUN_SNAPSHOT` 走字符串匹配；stale 分支不更新 Step/Run 状态（保持 RUNNING）直接返回刷新后的 Run，语义依赖后续 recover 收口，未在卡/Handoff 中写明。 | 代码如左；V3 只断言 `status == "stale"` 与 region 不变，未断言 Step/Run 持久状态 | 建议 seam 返回结构化状态（而非在 detail 里匹配错误码），并在卡/文档记录"stale 时不写回旧快照，Step 留 RUNNING 交由 recover 处理"的语义 | open |

> 未发现 P0（数据损坏/越界/伪造证据）或 P1（阻断性缺陷、关键验证缺失）。Findings 汇总：**P0 = 0，P1 = 0，P2 = 12**。

## 验证表

| 场景 | 命令或手工步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| 范围/边界 | `git -C <wt> diff --name-status c7b9d59e6..007094517`；逐项比对 `allowed_paths`；`git grep adopt_current` | worktree HEAD `007094517` | PASS（39 文件全在写域内；无 schema/migrations/apps/冻结契约/reviews 改动） | 本报告 §1 |
| R-CAND UPSERT | 代码阅读 + V1/V8 + V6 计数 | 同上 | PASS | `pipeline.py:454–598`、`test_fea00a_pipeline_seam.py:154–162`、`:404–407`、`:305`、`:329–330` |
| R-ART prepare/seam | 代码阅读 + AC4 静态边界 + V4/V6/V9 + trace 顺序 | 同上 | PASS | `step_writes.py:277–404`、`test_fea00a_source_boundaries.py:22–48`、`test_fea00a_pipeline_seam.py:221–262`、`:444–541` |
| R-SEAM | 代码阅读 + V5 + V7 + 分支守卫 | 同上 | PASS（含 R1-P2-01 字面偏差） | `pipeline.py:833–991`、`test_fea00a_pipeline_seam.py:269–288`、`:335–384` |
| 测试复现 A | `uv run --no-project … -m pytest tests/core/test_fea00a_pipeline_seam.py tests/pipeline/test_fea00a_source_boundaries.py -q` | Python 3.14.6 / pytest 9.1.1；临时 uv cache 于 `%TEMP%` | PASS：`14 passed`，EXIT=0 | 本次会话实际运行 |
| 测试复现 B | `… -m pytest tests/core/test_bootstrap.py tests/core/test_page_catalog_modes.py tests/pipeline/test_pipeline_production_seam.py tests/pipeline/test_regionless_rebinding.py tests/providers/test_detect_handler.py tests/providers/test_full_chain.py tests/providers/test_handlers_pipeline.py tests/providers/test_retype_redetect_persistence.py -q` | 同上 | PASS：`94 passed`，EXIT=0 | 本次会话实际运行 |
| 测试复现 C | `final-pytest-log.txt` 的 14 文件原命令 | 同上 | PASS：`194 passed`，EXIT=0 | 本次会话实际运行 |
| 修前基线复验 D | `git archive c7b9d59e6 src tests pytest.ini \| tar -x -C %TEMP%\fea00a-rev-base`，随后在该快照目录跑 12 文件基线命令 | 基线 `c7b9d59e6` 快照 | PASS：`180 passed`，EXIT=0 | 本次会话实际运行；与 AC8 修前 180 一致 |
| 冻结 pin 独立性 | 自行重算 15 个契约文件 raw 与 CRLF→LF 归一化 sha256，比对 `doc/plan/FEA-CONTRACT-FROZEN-*.md` | worktree（`core.autocrlf=true`） | raw 0/15、归一化 **15/15** 匹配（与证据"官方脚本 FAIL 15/15、归一化后一致"吻合） | 本次会话实际运行 |
| 工作区洁净 | `git -C <wt> status --porcelain=v1`（测试前后各一次） | 同上 | PASS（空） | 本次会话实际运行 |
| AC7② 真实旧库 | — | — | **NOT_RUN**（无用户旧库；证据已如实标 PARTIAL） | `legacy-db-audit-record.md` |
| 集成验证/发布验收 | — | — | **NOT_RUN**（不属本 Review 范围） | 本报告「边界声明」 |

## 结论与复审

- **decision: `approved`**（P0 = 0 / P1 = 0 / P2 = 12）。被审 head `007094517` 的实现、测试与证据在本次审查范围内自洽、可复现，满足卡内 R-CAND-1…4、R-ART-1…5、R-SEAM-1…3 与 AC1–AC6、AC8、AC9 的实现要求；AC3 有 trace + 独立连接双证据；V1–V9 确从 `assemble_core_services` + `build_production_pipeline` 的真实生产装配执行。
- **范围内未完成的验收**：AC7 仅 PARTIAL（真实旧库 NOT_RUN，如实标注）；AC10 由本 Review 满足，待 DSH 登记。
- **复审要求**：若后续因 Findings 修改代码并产生新 head，请按同一 head 作增量复审（r2），不得沿用本报告作为新 head 的批准。R1-P2-01 需 DSH 以裁决/冻结文本修正的形式落盘，否则该分支守卫将长期处于"实现正确但文本不一致"状态。
- **建议 DSH 处置顺序**：①登记本 Review 与 reviewer；②更新 Task 卡/Handoff/提交体一致性（R1-P2-08）；③裁决 R-SEAM-4 文本（R1-P2-01）；④决定 AC7 处理口径（R1-P2-10）；⑤执行集成验证（含 pin 在正常行尾环境下的复核）；⑥closeout。
- **剩余风险**：启动清扫的删除范围（R1-P2-02）与 seam 内大文件校验的写锁时长（R1-P2-11）属需在集成/后续任务跟踪的运维级风险；同连接并发与候选回插 FK（R1-P2-04/05）属低概率健壮性风险。

## 边界声明

本 Review **只审查 FEA-00A-IMPL-1 的实现交付**（固定 head `007094517`，基线 `c7b9d59e6`），**不构成集成批准、合并批准或发布验收**。`approved` 仅表示该实现交付在本次审查范围内没有 P0/P1 阻断项，可以交 DSH 进行集成验证；集成验证、AC7 真实旧库核验、pin/治理记录处置、资源 closeout、Task 生命周期更新与最终推送仍由 DSH 负责并另行记录。本文件不修改被审代码、不改 worktree、不改卡/STATUS/PLAN/LEDGER/冻结契约与 pin。
