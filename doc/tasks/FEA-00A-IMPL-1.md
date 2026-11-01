---
id: FEA-00A-IMPL-1
title: FEA-00a 数据安全修复（prepare 与 seam 分离；region + artifact 零变化）
kind: implementation
governance_version: 3
status: proposed
approval: user_ruling_2026-11-01_D1_D4
suggested_owner: codex
owner: codex
reviewer: c01b-reviewer
depends_on:
  - FEA-00A-PREP-1
base_commit: 419f891c0
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-00A-IMPL-1
allowed_paths:
  - doc/tasks/FEA-00A-IMPL-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/checkpoints/**
  - doc/handoffs/FEA-00A-IMPL-*.md
  - src/infrastructure/providers/**
  - src/infrastructure/sqlite/pipeline.py
  - src/infrastructure/pipeline/assembly.py
  - src/bootstrap/core_assembly.py
  - src/ports/repositories/storage.py
  - src/application/tasks/**
  - tests/core/test_bootstrap.py
  - tests/core/test_page_catalog_modes.py
  - tests/pipeline/test_regionless_rebinding.py
  - tests/providers/t111_support.py
  - tests/providers/test_detect_handler.py
  - tests/providers/test_full_chain.py
  - tests/providers/test_handlers_pipeline.py
  - tests/providers/test_retype_redetect_persistence.py
  - verification/FEA-00A-IMPL-1/**
---

# FEA-00a 数据安全修复（范围冻结 v2，待独立复核）

## 来源

1. 方案 §15.5 硬验收（seam 失败/冲突/暂停/取消/崩溃时 `regions.text_json`、`current_revision_id`、`region_revisions` 行数三处零变化）；§15.6 FEA-00a 行。
2. 只读评估 [`FEA-00A_PREP.md`](../plan/FEA-00A_PREP.md)（G1–G7、A1–A7、§4.1 token 契约、§4.2 清理归属、V1–V8）+ 复核 [`FEA-00A-PREP-r1`](../reviews/FEA-00A-PREP-r1.md) `approved`。
3. **用户 2026-11-01 裁决 D1–D4**（[ADJ U-13](../reviews/ADJ-2026-11-01-FEA-DECISIONS.md)）。
4. **范围冻结复核 r1** [`FEA-00A-IMPL-scope-r1`](../reviews/FEA-00A-IMPL-scope-r1.md) `changes_requested`（P0=0 / P1=3 / P2=10）；本版逐条处置，见「复核处置对账」。

## 用户裁决落盘

| # | 用户裁决 | 本卡落点 |
|---|---|---|
| **D1** | ② 一起修：region + artifact（`media_artifacts.current_revision_id`、`publish` 的 `artifact_revisions` 行/落盘文件） | AC6、R-ART-1…4、V9 |
| **D2** | ② 允许改 `src/application/tasks/service.py`；必要情况下可重新设计构件 | 写域 `src/application/tasks/**`；AC9 逐项登记 |
| **D3** | ① 复用 `step_result_candidates`（无 schema/迁移） | 禁改 `schema.py`/migrations；R-CAND-1…4 |
| **D4** | L2 自动化 + 真实生产 assembly 跑一遍（V1–V9） | AC8；AC6 绑定 V9 |

## 已冻结的设计规则（实现必须按此，不得自创第二套）

### R-CAND：候选承载与 Run 全量重写的保留规则（处置 P1-1）

现状事实：`SqlitePipelineStore._write_run` 每次 `DELETE FROM pipeline_runs`（`pipeline.py:433`），`step_result_candidates` 受 `ON DELETE CASCADE`（`schema.py:381–382`、`:523–524`；`connection.py:319` `foreign_keys=ON`），随后只按 `run.candidates` 重建（`pipeline.py:516–528`）。因此 prepare 直插的 `prepared` 行会在成功 seam、seam 失败、重启恢复、并发 pause/stop 四条路径被级联删除。

- **R-CAND-1（唯一真相）**：`step_result_candidates` 中 `status='prepared'` 的行是 prepare 阶段暂存数据的**唯一持久真相**；`PipelineRun.candidates` 只表示 seam 拒绝后的诊断候选，不得作为 prepared 行的来源。
- **R-CAND-2（重写保留）**：`_write_run` 必须在 `DELETE FROM pipeline_runs` **之前**读取该 `run_id` 下 `status='prepared'` 的全部列，并在重建 `run.candidates` 之后、提交之前**原样回插**（`candidate_id`、`payload_json`、`created_at`、`reason` 不得改写）。四条路径（成功 persist / 失败 `_persist` / `recover_running_runs` / `control_run` pause-stop）全部适用，不得例外。
- **R-CAND-3（状态机）**：`prepared` → seam 成功时同事务置 `resolved`（`resolved_at` 非空）→ seam 拒绝/中止时置 `abandoned`（`resolved_at` 非空，**不硬删**）。任何路径不得删除 prepared 行；硬删只允许 `library.purge` 的既有页面清理路径。
- **R-CAND-4（启动清扫）**：run 启动（含 `recover_running_runs`）时，把该 run 下仍为 `prepared` 的行统一置 `abandoned`（记录 `resolved_at`），并在证据中给出计数；不得把旧 attempt 的 prepared 行带入新 attempt。

### R-ART：artifact 文件 staging 协议（处置 P1-2；文件不可与 DB 同事务，故冻结顺序协议）

现状事实：`ManagedStorage` 已有 `write_temp(content)→temp_handle`、`verify_temp(handle)`、`publish(temp_handle, relative_path)`、`discard_temp(handle)`、`remove_managed(relative_path)`（`src/infrastructure/filesystem/managed_storage.py:98–126`）。`SqliteTargetCatalog.__init__(conn)` 只有连接（`pipeline.py:690–694`），由 `src/infrastructure/pipeline/assembly.py:36–37` 构造；生产 assembly 在 `src/bootstrap/core_assembly.py:1336–1341`、`:1377`。

- **R-ART-1（prepare 只暂存）**：`ArtifactStepWriter.publish` 在 prepare 阶段只 `write_temp`；**不得** `publish` 到最终路径、**不得** `INSERT artifact_revisions`、**不得** `INSERT/UPDATE media_artifacts`。staging 信息（`temp_handle`、`relative_path`、`artifact_type`、`page_id`、`base_revision_id`、`sha256`、`size`）写入 prepared 候选 `payload_json`；返回 `revision_updates={artifact_type: <预生成真实 artifact revision id>}`。
- **R-ART-2（seam 顺序）**：`commit_step` 的 artifact 分支按 token 找回 prepared 候选 → 校验 `base_revision_id` 与当前一致、`verify_temp` 的 sha256/size 一致 → **先** `storage.publish(temp_handle, relative_path)`（幂等：目标已存在且 sha256 相同视为已发布）→ **再** `BEGIN IMMEDIATE` 做 DB（插 `artifact_revisions` 行、CAS `media_artifacts.current_revision_id`、候选 `resolved`）→ commit。
- **R-ART-3（失败补偿与清扫）**：DB 事务失败 → `storage.remove_managed(relative_path)` 补偿（失败则记录孤儿文件清单入证据）；seam 拒绝/暂停/取消 → `discard_temp` 并置候选 `abandoned`。run 启动清扫：`prepared` 的 artifact 候选 → 校验并 `discard_temp`；无 `artifact_revisions` 引用的最终文件 → `remove_managed`。
- **R-ART-4（接线边界）**：为让 seam 访问 storage，允许在 `src/infrastructure/pipeline/assembly.py`、`src/bootstrap/core_assembly.py` 做**最小接线**（`SqliteTargetCatalog(conn, storage=None)`；默认 `None` 必须保持旧行为逐字节不变），并在 `src/ports/repositories/storage.py` **仅在既有端口缺方法时**做最小新增。全部接线改动须在 Handoff 逐行列出理由与回退；**不改任何既有业务行为**。

### R-SEAM：seam 判定与观测（处置 P2-4、P2-8）

- **R-SEAM-1**：`commit_step` 在 `BEGIN IMMEDIATE` 之后、任何 live 写之前先检查 pause/cancel 标志；命中则 `rollback` 并返回 `paused`/`cancelled` 类结果，同时置 prepared 候选 `abandoned`。
- **R-SEAM-2**：AC3 的「无中间可观察态」固定观测方式：①`sqlite3.Connection.set_trace_callback` 断言语句序列与**单次** `COMMIT`；②独立只读连接在事务提交前查不到新值；③WAL 模式下在提交前另开连接做一致性读。三者至少 ①+②。
- **R-SEAM-3**：真实生产 assembly 唯一定义 = `src/bootstrap/core_assembly.py:assemble_core_services`（:944）构造的 `RegionStepWriter/ArtifactStepWriter`（:1340–1341）+ `build_production_pipeline`（:1377）装配的 `PipelineService`；V1–V9 必须经此入口执行，禁止 fake executor/double。

## 范围（写域）

- **实现（唯一）**：`src/infrastructure/providers/**`（`step_writes.py` region/artifact 写面、`handlers.py` adopt 调用点与上下文）、`src/infrastructure/sqlite/pipeline.py`（`_write_run` 保留规则 + `commit_step` seam + 清扫）、`src/infrastructure/pipeline/assembly.py` 与 `src/bootstrap/core_assembly.py`（**仅 R-ART-4 最小接线**）、`src/ports/repositories/storage.py`（仅缺方法时最小新增）、`src/application/tasks/**`（D2 授权）。
- **测试（收窄）**：G7 的 8 个文件 `tests/core/test_bootstrap.py`、`tests/core/test_page_catalog_modes.py`、`tests/pipeline/test_regionless_rebinding.py`、`tests/providers/t111_support.py`、`tests/providers/test_detect_handler.py`、`tests/providers/test_full_chain.py`、`tests/providers/test_handlers_pipeline.py`、`tests/providers/test_retype_redetect_persistence.py`，以及本卡新增测试文件（须在 Handoff 逐项列出路径与用例）。新增测试文件超出上述 8 个时，须先在本卡登记路径。
- **证据**：`verification/FEA-00A-IMPL-1/**`（含 V1–V9 日志、真实 assembly 执行脚本、旧库只读核验记录）。
- **治理**：本卡、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`、`doc/checkpoints/**`、`doc/handoffs/FEA-00A-IMPL-*.md`。
- **审阅产出不属 Owner 写域**：`doc/reviews/**` 由独立 Reviewer / DSH 写，Owner 不得改；用户裁决记录（ADJ）同样不在写域。
- **不改**：`schema.py`/migrations（D3=①）、Avalonia 侧 `apps/**`、冻结契约字节（15 份 pin）、`G-DELETE-IMPL`、其它 Task、用户数据；不新增依赖、不改构建配置、不 push。

## 验收标准（冻结版）

- [ ] **AC1 三处零变化**：revision 冲突 / Lock 冲突 / `STALE_RUN_SNAPSHOT` / DB 失败 / pause / cancel / prepare 后崩溃重启 7 类注入下，`regions.text_json`、`regions.current_revision_id`、`region_revisions` 行数与 prepare 前完全相同（A1、V1–V6）；pause/cancel 按 R-SEAM-1 注入。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC2 候选可诊断且状态机可核验**：失败候选在 `step_result_candidates` 可按 `pipeline_run_id`/`status` 查询，`reason`/`status`/`base_revision_id`/`payload_json` 字段值正确；`prepared`→`resolved`/`abandoned` 状态机与 `resolved_at` 按 R-CAND-3 断言；R-CAND-2 四条路径各自的 prepared 行存续断言、R-CAND-4 启动清扫计数断言（A2、§4.2）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC3 成功同事务**：revision 行 + `text_json` + 指针 CAS + 候选 `resolved` 在同一事务提交；按 R-SEAM-2 的 trace + 独立连接双证据断言无中间可观察态（A3、V7）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC4 prepare 不触 live（含 artifact 写面）**：结构/grep 断言 prepare 路径不存在：`UPDATE/INSERT regions`、`INSERT region_revisions`、`UPDATE media_artifacts`、`INSERT media_artifacts`、`INSERT artifact_revisions`、`storage.publish`（`_artifact_id` 的 `INSERT media_artifacts` 必须延后到 seam）；token = prepare 预生成的真实 revision id（A4、§4.1、R-ART-1）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC5 重启可判定**：prepare 后崩溃/重启，live 三处不变；`prepared` 行可识别（R-CAND-2/R-CAND-4），清扫后为 `abandoned` 且计数可核（A5、V6）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC6（D1=②）artifact 三对象零变化**：失败注入下 `media_artifacts.current_revision_id` 不变、`artifact_revisions` 行数不变、staging/final 文件无新增可见产物；成功时按 R-ART-2 顺序完成文件 promotion 与 DB 同事务落定，`sha256`/`size`/指针/行/文件一致；崩溃后按 R-ART-3 可清扫（A6、V9，**V9 必须从真实生产 assembly 执行**）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC7 §15.6 出口**：①结构断言覆盖 prepare 路径无 live 写（同 AC4 清单）；②旧库只读核验程序固定：只读打开既有 DB → 查询三处一致性（text_json 与 current_revision 对应关系、region_revisions 计数）→ 候选表可读 → 输出核验清单；**保留既有备份与候选，不创建/不恢复备份**（A7，不触 L-5）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC8 回归与真实 assembly（V1–V9）**：G7 8 文件逐项给出「测试名 / 修前 outcome / 修后 outcome / 判定（保持 live 语义或有意变更）/ 理由」表格；`tests/providers/t111_support.py` 单列「适配而非 outcome 对照」；**V1–V9 全部从 R-SEAM-3 定义的真实生产 assembly 执行**（D4）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC9 D2=② 改动登记**：若改动 `src/application/tasks/**`，Handoff 逐项写「为什么必须改 / 不改的替代方案 / 影响面 / 回退方式」；构件重设计须附前后接口对照。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC10 独立复核**：范围冻结复核 r2 `doc/reviews/FEA-00A-IMPL-scope-r2.md` 判 `approved`（P0/P1=0）；实现复核 `doc/reviews/FEA-00A-IMPL-r1.md` 判 `approved`（P0/P1=0）。 <<PARTIAL: r1 为 changes_requested，已处置；r2 待派发；实现复核在交付后>>

## L 前置适用性判定（按实际写域）

| 保留项 | 是否触及 | 判定 | 再触发条件 |
|---|---|---|---|
| **L-1** 四表 DDL 未冻 | 否——复用既有 `step_result_candidates`，不加列/CHECK/索引/迁移 | **NOT_APPLICABLE** | 若改 `schema.py`/migrations，或**给候选表加列/CHECK/索引**，或新增暂存表 → `blocked`，先完成 L-1 前置 |
| **L-2** M2-C1 字节修订 | 否——不新增/改 wire 码表与白名单；沿用既有 `INPUT_REVISION_CHANGED`/`LOCK_CHANGED`/`DB_FAILED`/`TARGET_NOT_FOUND` 与 `StepResult.revision_updates` | **NOT_APPLICABLE** | 若引入新错误码/改白名单，或**构件重设计使 prepared/候选状态进入 Host 投影或 `StepResult` 的 wire 可见语义** → `blocked`，先完成 M2-C1 独立字节修订 |
| **L-5** 整库恢复独占锁 | 否——AC7② 只做旧库**只读**核验；不创建、不恢复、不删除备份 | **NOT_APPLICABLE** | 若触及备份创建/恢复/维护互斥（含 AC7② 越界为恢复）→ `blocked`，按 L-5 四步序列补 AC |

> `doc/plan/FEA-C11_IMPL_PREREQS.md` §0：不适用不等于豁免。

## 测试矩阵（冻结版；全部 planned，V1–V9 从真实 assembly 执行）

| # | 注入 | 期望 | 证据 |
|---|---|---|---|
| V1 | seam 前 revision 冲突（`input_revision_changed`） | AC1 + AC2；无 live 写；prepared 行存续（R-CAND-2） | `verification/FEA-00A-IMPL-1/` |
| V2 | Lock 冲突（`lock_changed`） | AC1 + AC2 | 同上 |
| V3 | `STALE_RUN_SNAPSHOT` | AC1；Run 不半写 | 同上 |
| V4 | DB 失败（seam 事务抛错） | AC1；整体回滚；artifact 文件补偿（R-ART-3） | 同上 |
| V5 | pause / cancel（commit_step 前设标志，R-SEAM-1） | AC1；候选置 `abandoned` 可诊断 | 同上 |
| V6 | prepare 后进程崩溃 + 重启 | AC1 + AC5；启动清扫计数 | 同上 |
| V7 | 成功路径 | AC3；trace + 独立连接双证据 | 同上 |
| V8 | 并发：两个 prepare 同 region | V1 语义 + 不互相污染 | 同上 |
| V9 | artifact 指针/行/文件（D1=②） | AC6；先 publish 后 DB；失败零推进；崩溃清扫 | 同上 |

计划命令：`python -m pytest <8 文件 + 新增> -q` + 真实 assembly 执行脚本；结果分列 passed/failed/skipped 并逐项记 skip 原因。

## 复核处置对账（r1 → 本版）

| Finding | 处置 |
|---|---|
| P1-1 | 新增 R-CAND-1…4；AC2/AC3/AC5 落成状态机与四条路径断言 |
| P1-2 | 新增 R-ART-1…4（临时文件协议 + 扩写域仅接线）；AC6/V9 绑定文件级断言 |
| P1-3 | D4 行、AC8 改 **V1–V9**；AC6 显式绑定 V9 |
| P2-1 | AC2 落成状态机/扫除点断言；AC7② 固定只读核验程序 |
| P2-2 | AC4/AC7① 禁写清单补 `INSERT media_artifacts`、`INSERT artifact_revisions`、`storage.publish`；`_artifact_id` 延后到 seam |
| P2-3 | AC8 定义真实 assembly = R-SEAM-3 入口；逐文件表格格式；`t111_support.py` 单列 |
| P2-4 | R-SEAM-1 固定 pause/cancel 在 `commit_step` 内的判定；V5 对应 |
| P2-5 | `REBASELINE_PLAN:28` 已改为 `proposed` |
| P2-6 | 移除 ADJ 与 `doc/reviews/**` 写权；`tests/**` 收窄为 G7 8 文件 + 登记新增 |
| P2-7 | `base_commit` 更新为范围冻结提交 `419f891c0`；`ready` 时再更新为最终冻结 head |
| P2-8 | R-SEAM-2 固定三选二观测证据 |
| P2-9 | L-1/L-2/L-5 再触发条件补全（候选表加列/索引、wire 可见语义、只读不创建备份） |
| P2-10 | `STATUS:15` 13/13 → 15/15 |

## 禁止范围

- 不改冻结契约字节（15 份 pin）；不改 `G-DELETE-IMPL`；不动用户数据；不 push。
- 不改 schema / 不建迁移（D3=①）；不加列/索引/CHECK。
- 不顺手修 FEA-03/FEA-10 的其它功能；不释放其它实现 Task。
- 不以 fake executor / double 替代真实生产 assembly。
- 不在 `apps/**`、`doc/reviews/**`、用户裁决记录上写入。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| - | - | - | `-` | `-` | CANONICAL |

## Resource Manifest

实现尚未开始：仓库内无 worktree、无构建产物；实现开始后按 `Workspace Governance` 在 `G:\CODEX\New Manga.workspace\` 建 task-env 并在本表补齐逐项处置。

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| doc-task | - | NOT_APPLICABLE | - | - | 范围冻结阶段；未访问用户数据 |
| build/temp（未来） | - | PENDING | ..\New Manga.workspace\ | - | 实现开始前补齐具体路径与处置 |

## Closeout Record

- 2026-11-01：`proposed`（评估完成，等用户拍板）。
- 2026-11-01：用户裁决 D1–D4 落盘（ADJ U-13），DSH 冻结范围 v1（`419f891c0`）。
- 2026-11-01：独立范围复核 r1 `changes_requested`（P0=0 / P1=3 / P2=10）；本版 v2 逐条处置并在「复核处置对账」登记；**未释放**。
- 2026-11-01：置 `proposed`，派上下文独立复核 r2 审查本冻结 v2；**复核通过前不 `ready`、不派实现**。
