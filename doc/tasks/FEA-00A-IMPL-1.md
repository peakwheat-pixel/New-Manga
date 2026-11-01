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
  - tests/core/**
  - tests/pipeline/**
  - tests/providers/t111_support.py
  - tests/providers/test_detect_handler.py
  - tests/providers/test_full_chain.py
  - tests/providers/test_handlers_pipeline.py
  - tests/providers/test_retype_redetect_persistence.py
  - verification/FEA-00A-IMPL-1/**
---

# FEA-00a 数据安全修复（范围冻结 v3，待独立复核）

## 来源

1. 方案 §15.5 硬验收；§15.6 FEA-00a 行。
2. 只读评估 [`FEA-00A_PREP.md`](../plan/FEA-00A_PREP.md)（G1–G7、A1–A7、§4.1、§4.2、V1–V8）+ 复核 [`FEA-00A-PREP-r1`](../reviews/FEA-00A-PREP-r1.md) `approved`。
3. **用户 2026-11-01 裁决 D1–D4**（[ADJ U-13](../reviews/ADJ-2026-11-01-FEA-DECISIONS.md)）。
4. 范围冻结复核：[r1](../reviews/FEA-00A-IMPL-scope-r1.md) `changes_requested`（P1×3/P2×10）→ v2（`98fbccdf5`）→ [r2](../reviews/FEA-00A-IMPL-scope-r2.md) `changes_requested`（P1×2/P2×7）→ 本版 v3 逐条处置。

## 用户裁决落盘

| # | 用户裁决 | 本卡落点 |
|---|---|---|
| **D1** | ② region + artifact 一起修 | AC6、R-ART-1…5、V9 |
| **D2** | ② 允许改 `src/application/tasks/service.py`，必要时可重新设计构件 | 写域 `src/application/tasks/**`；AC9 登记 |
| **D3** | ① 复用 `step_result_candidates`，无 schema/迁移 | 禁改 `schema.py`/migrations；R-CAND-1…4 |
| **D4** | L2 自动化 + 真实生产 assembly（V1–V9） | AC8；AC6 绑定 V9 |

## 已冻结的设计规则

### R-CAND：候选行在 Run 重写下的存续（处置 r2-P1-1）

事实：`_write_run` 当前 `DELETE FROM pipeline_runs WHERE run_id = ?`（`pipeline.py:433`），候选行经 FK 级联删除（`schema.py` 候选表定义），随后只按 `run.candidates` 重建（`pipeline.py:516–528`）——`prepared`、`resolved`、`abandoned` 三态行都会被删。

- **R-CAND-1（唯一真相）**：`step_result_candidates` 中 `prepared`/`resolved`/`abandoned` 三态行是 prepare→seam 生命周期的唯一持久真相；`PipelineRun.candidates` 只承载 seam 拒绝后的诊断候选。
- **R-CAND-2（禁止删除父行）**：`_write_run` **不得**对 `pipeline_runs` 使用 `DELETE` 或 `INSERT OR REPLACE`（两者都会触发候选级联删除）；必须改为 `INSERT … ON CONFLICT(run_id) DO UPDATE`（UPSERT）。若某父行（含 `step_runs`）确实必须重建，须在同一事务内先读出该 `run_id` 下三态候选行，重建后按 `candidate_id` 去重回插（`run.candidates` 已有的 id 优先）。四条路径（成功 persist / seam 失败 `_persist` / `recover_running_runs` / `control_run` pause-stop）全部适用。`pipeline.py:1058` 的既有清理语句不属本规则范围，但不得新增删除父行的路径。
- **R-CAND-3（状态机与保留）**：`prepared` 仅在 prepare 阶段产生；seam 成功 → 同事务置 `resolved`（`resolved_at` 非空）；seam 拒绝/中止 → **独立事务**置 `abandoned`（`resolved_at` 非空）。任何路径不得硬删三态行；既有清理路径（`library.purge` 页面清理、`pipeline.py` 的 `purge_targetless_runs`）除外，**不得为本次修复新增删除路径**。
- **R-CAND-4（启动清扫与双行语义）**：run 启动（含 `recover_running_runs`）时，把该 run 下仍为 `prepared` 的行置 `abandoned` 并记录计数；同一步允许并存「1 行 abandoned（prepare 暂存）」+「1 行 pending（seam 拒绝诊断）」，诊断查询必须按 `status` 区分并可分别断言。

### R-ART：artifact staging 协议（处置 r2-P1-2 与相关 P2）

事实：`ManagedStorage` 有 `write_temp/verify_temp/publish/discard_temp/remove_managed`（`managed_storage.py:98–126`）；`ArtifactStepWriter.prepare_revision`（`step_writes.py:304`）当前在 prepare 内 `publish`（`:350`）并 `_artifact_id` 插入 `media_artifacts` 后提交（`:491–514`）；`SqliteTargetCatalog.__init__(conn)` 只有连接（`pipeline.py:690–694`），由 `src/infrastructure/pipeline/assembly.py:36–37` 构造，生产装配在 `src/bootstrap/core_assembly.py:1336–1341`、`:1377`。

- **R-ART-1（prepare 只暂存）**：`ArtifactStepWriter.prepare_revision` 在 prepare 阶段只 `write_temp` + `verify_temp`；**不得** `publish`、**不得** `INSERT artifact_revisions`、**不得** `INSERT/UPDATE media_artifacts`（`_artifact_id` 的 prepare 期 `INSERT media_artifacts` 必须移除或延后到 seam）。prepared 候选 `payload_json` 冻结字段：`temp_handle`、`relative_path`、`artifact_type`、`page_id`、`artifact_id`（若已存在）、`book_id`、`chapter_id`、`base_revision_id`、`sha256`、`size`、`mime_type`（NOT NULL 必填）、`content_format`；**不得虚构 `media_artifacts` 不存在的 `revision_no` 列**（该列只属于 `artifact_revisions`，由 seam 按表结构写入）；返回 `revision_updates={artifact_type: <预生成真实 revision id>}`。
- **R-ART-2（seam 顺序，消除孤儿文件）**：`commit_step` 的 artifact 分支：①`BEGIN IMMEDIATE` → ②按 token 找回 prepared 候选并校验 `base_revision_id`/`sha256`/`size` → ③`R-SEAM-1` 的 pause/cancel 检查 → ④DB 写：按 `(page_id, artifact_type)` 查 `media_artifacts`，无行则 `INSERT`（`current_revision_id=NULL`）；`INSERT artifact_revisions`（按 schema 必填列，含 `revision_no`）；CAS `UPDATE media_artifacts SET current_revision_id=…`；写 `stage_updates`；调用 `persist()`；候选置 `resolved` → ⑤**commit 之前** `storage.publish(temp_handle, relative_path)`（幂等：目标已存在且 sha256 相同视为已发布）→ ⑥`COMMIT`。
  拒绝路径（revision/lock/stale/pause/cancel）全部发生在 publish 之前 → 不产生孤儿文件。父行改 UPSERT 后，`run_targets`/`tasks` 等既有子表按原逻辑重建（这些子表不含候选行）；候选行受 R-CAND-2 保护。
- **R-ART-3（失败补偿与清扫）**：任何非 `applied` 结果：`discard_temp`（未 publish 时）；若 publish 已发生而后续失败 → `storage.remove_managed(relative_path)` 补偿，失败则把孤儿路径写入证据清单。启动清扫：`prepared` 的 artifact 候选 → 校验并 `discard_temp` 后置 `abandoned`；无 `artifact_revisions` 引用的最终文件 → `remove_managed`。清扫实现放 `pipeline.py`，由 `PipelineService` 启动路径调用（`src/application/tasks/service.py` 在写域内）。
- **R-ART-4（storage 注入与 None 语义）**：允许 `SqliteTargetCatalog(conn, storage=None)`；`storage=None` 表示**不启用 artifact staging**，仅用于既有测试的双实例保持旧语义；**生产装配（`core_assembly.py`）必须传入 `ManagedStorage`**；若 `storage=None` 却遇到 artifact 候选 → 返回明确失败（`db_failed`），不得静默 publish。接线改动须 Handoff 逐行列理由与回退；不改既有业务行为。
- **R-ART-5（接线边界）**：`src/infrastructure/pipeline/assembly.py`、`src/bootstrap/core_assembly.py` 只做最小接线（构造参数传递 + 注入）；`src/ports/repositories/storage.py` 仅在既有端口缺方法时最小新增。不得重构组合根或改变公开签名。

### R-SEAM：seam 判定与观测（处置 r1-P2-4/8 与 r2-P2）

- **R-SEAM-1（pause/cancel 在 seam 内判定）**：`commit_step` 增加 pause/cancel 判定入口（入参标志或回调，实现方式由实现者选定但须写入 Handoff）；判定位置在 `BEGIN IMMEDIATE` 之后、任何 live 写与 publish 之前；命中则 `rollback` 返回 `paused`/`cancelled` 结果，随后**独立事务**把对应 prepared 行置 `abandoned`（不得在已回滚的事务内写）。
- **R-SEAM-2（AC3 观测方法）**：固定三选二——①`sqlite3.Connection.set_trace_callback` 断言语句序列与单次 `COMMIT`；②独立只读连接在提交前读不到新值；③WAL 下提交前另开连接一致性读。至少 ①+②。
- **R-SEAM-3（真实生产 assembly 定义）**：唯一入口 = `src/bootstrap/core_assembly.py:assemble_core_services`（:944）构造的 `RegionStepWriter/ArtifactStepWriter`（:1340–1341）+ `build_production_pipeline`（:1377）装配的 `PipelineService`。允许生产配置中既有的 `mock_local_providers=True`（本地 provider 替身），**禁止** fake executor / InMemory catalog / 测试专用 pipeline 替代。
- **R-SEAM-4（分支键守卫）**：`commit_step` 现有「region 场景 `revision_updates` 键必须为 `region`」守卫（`pipeline.py:763–766`）改为按 `target_type` 分派：`REGION` 分支保持原样；`PAGE` 分支接受 `{artifact_type: revision_id}`（artifact 归属 page，`TargetType` 无 ARTIFACT 值）；未知 target_type/键返回 `db_failed`。

## 范围（写域）

- **实现**：`src/infrastructure/providers/**`、`src/infrastructure/sqlite/pipeline.py`、`src/infrastructure/pipeline/assembly.py` 与 `src/bootstrap/core_assembly.py`（仅 R-ART-4/5 接线）、`src/ports/repositories/storage.py`（仅缺方法时最小新增）、`src/application/tasks/**`（D2）。
- **测试**：`tests/core/**`、`tests/pipeline/**`（含新增测试文件，须在 Handoff 逐项列出路径与用例）、G7 的 `tests/providers/` 5 个文件（`t111_support.py`、`test_detect_handler.py`、`test_full_chain.py`、`test_handlers_pipeline.py`、`test_retype_redetect_persistence.py`）。
- **证据**：`verification/FEA-00A-IMPL-1/**`。
- **治理**：本卡、`STATUS`、`REBASELINE_PLAN`、`TASK_LEDGER`、`doc/checkpoints/**`、`doc/handoffs/FEA-00A-IMPL-*.md`。
- **审阅产出不属 Owner 写域**：`doc/reviews/**`（独立 Reviewer/DSH 写）；用户裁决记录（ADJ）亦不在写域。
- **不改**：`schema.py`/migrations、`apps/**`、冻结契约字节（15 pin）、`G-DELETE-IMPL`、其它 Task、用户数据；不新增依赖、不改构建配置、不 push。

## 验收标准（冻结版）

- [ ] **AC1 三处零变化**：revision 冲突 / Lock 冲突 / `STALE_RUN_SNAPSHOT` / DB 失败 / pause / cancel / prepare 后崩溃重启 7 类注入下，`regions.text_json`、`regions.current_revision_id`、`region_revisions` 行数与 prepare 前完全相同（A1、V1–V6；pause/cancel 按 R-SEAM-1）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC2 候选可诊断且三态可存续**：失败候选字段正确；`prepared→resolved/abandoned` 状态机与 `resolved_at` 按 R-CAND-3；R-CAND-2 四条路径下三态候选行数与 `candidate_id` 集合不变（UPSERT 或回插）；R-CAND-4 启动清扫计数；同一步 abandoned+pending 双行可分别断言（A2、§4.2）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC3 成功同事务**：revision 行 + `text_json` + 指针 CAS + 候选 `resolved` 在同一事务提交；按 R-SEAM-2 双证据断言无中间可观察态（A3、V7）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC4 prepare 不触 live（含 artifact 写面）**：结构/grep 断言 prepare 路径不存在 `UPDATE/INSERT regions`、`INSERT region_revisions`、`UPDATE media_artifacts`、`INSERT media_artifacts`、`INSERT artifact_revisions`、`storage.publish`；token = 预生成真实 revision id（A4、§4.1、R-ART-1）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC5 重启可判定**：prepare 后崩溃/重启 live 三处不变；`prepared` 行可识别（R-CAND-2/4），清扫后为 `abandoned` 且计数可核（A5、V6）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC6（D1=②）artifact 三对象零变化**：失败注入下 `media_artifacts.current_revision_id`、`artifact_revisions` 行数、最终文件均无新增可见产物且无孤儿文件；成功时按 R-ART-2 顺序完成文件 promotion 与 DB 落定，`sha256`/`size`/指针/行/文件一致；首 revision 的 `INSERT media_artifacts` 在 seam 内完成；崩溃后按 R-ART-3 可清扫（A6、**V9 从真实生产 assembly 执行**）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC7 §15.6 出口**：①结构断言覆盖 prepare 无 live 写（同 AC4 清单）；②旧库只读核验程序固定：只读打开既有 DB → 查三处一致性（text_json 与 current_revision 对应、region_revisions 计数）→ 候选表可读 → 输出核验清单；保留既有备份与候选，**不创建/不恢复备份**（A7，不触 L-5）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC8 回归与真实 assembly（V1–V9）**：G7 8 文件逐项表格（测试名/修前/修后/判定/理由），`t111_support.py` 单列"适配而非 outcome 对照"；V1–V9 全部经 R-SEAM-3 入口执行（D4）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC9 D2=② 改动登记**：若改 `src/application/tasks/**`，Handoff 逐项写「为什么必须改 / 不改的替代方案 / 影响面 / 回退方式」；构件重设计附前后接口对照。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC10 独立复核**：范围冻结复核 r3 `doc/reviews/FEA-00A-IMPL-scope-r3.md` 判 `approved`（P0/P1=0）；实现复核 `doc/reviews/FEA-00A-IMPL-r1.md` 判 `approved`。 <<PARTIAL: r1/r2 为 changes_requested、v3 已处置；r3 待派发；实现复核在交付后>>

## L 前置适用性判定

| 保留项 | 判定 | 再触发条件 |
|---|---|---|
| **L-1** | **NOT_APPLICABLE**（复用既有候选表，不加列/CHECK/索引/迁移） | 改 `schema.py`/migrations、给候选表加列/CHECK/索引、新增暂存表 → `blocked` |
| **L-2** | **NOT_APPLICABLE**（不新增/改 wire 码与白名单，沿用既有错误码与 `revision_updates`） | 引入新错误码/改白名单，或构件重设计使 prepared/候选状态进入 Host 投影或 `StepResult` wire 可见语义 → `blocked` |
| **L-5** | **NOT_APPLICABLE**（AC7② 只读；不创建/不恢复/不删备份） | 触及备份创建/恢复/维护互斥 → `blocked` |

> `doc/plan/FEA-C11_IMPL_PREREQS.md` §0：不适用不等于豁免。

## 测试矩阵（V1–V9 全部经真实生产 assembly）

| # | 注入 | 期望 |
|---|---|---|
| V1 | revision 冲突 | AC1 + AC2；三态行存续；无 live 写 |
| V2 | Lock 冲突 | AC1 + AC2 |
| V3 | `STALE_RUN_SNAPSHOT` | AC1；Run 不半写 |
| V4 | DB 失败 | AC1；整体回滚；文件补偿 |
| V5 | pause/cancel（R-SEAM-1 注入） | AC1；候选独立事务置 `abandoned` |
| V6 | 崩溃 + 重启 | AC1 + AC5；启动清扫计数 |
| V7 | 成功 | AC3（trace + 独立连接） |
| V8 | 并发同 region | V1 语义 + 不互相污染 |
| V9 | artifact 指针/行/文件 | AC6；失败零推进且无孤儿；成功三者一致 |

## 复核处置对账（r1 → v2 → v3）

| Finding | 处置 |
|---|---|
| r1-P1-1 → r2-P1-1 | R-CAND-2 改为「禁止 DELETE/INSERT OR REPLACE 父行，改 UPSERT；必须重建时先保留三态行按 candidate_id 回插」；AC2/AC3/AC5 与 V1/V2/V5/V7 断言同步 |
| r1-P1-2 → r2-P1-2 | R-ART-2 改为 publish 在 CAS 屏障与 DB 写之后、COMMIT 之前；拒绝路径全部先于 publish；R-ART-3 覆盖任何非 applied |
| r1-P1-3 | 已解决（v2 起 V1–V9、AC6 绑定 V9） |
| r2-P2-1 | R-ART-2④ 补首 revision `INSERT media_artifacts`（`current_revision_id=NULL`, `revision_no=1`） |
| r2-P2-2 | R-ART-1 冻结 payload 字段清单；实现按 schema 必填列核对并在 Handoff 登记 |
| r2-P2-3 | R-SEAM-4 分支键守卫按 `target_type` 分派 |
| r2-P2-4 | R-ART-3 指定清扫实现位置（`pipeline.py`）与调用方（`PipelineService` 启动路径） |
| r2-P2-5 | 统一方法名 `ArtifactStepWriter.prepare_revision` |
| r2-P2-6 | R-ART-4 明确 `storage=None` 语义与生产必传 |
| r2-P2-7 | R-SEAM-1 明确"独立事务置 abandoned"，不在已回滚事务内写 |
| r2-P2-8 | R-SEAM-3 澄清允许 `mock_local_providers=True`，禁止 fake executor/catalog |
| r2-P2-9 | 写域补 `tests/core/**`（`assemble_core_services` 影响面在 `test_bootstrap.py`） |
| r2-P2-10 | 新增测试文件位置限定 `tests/core/**`、`tests/pipeline/**` 并要求 Handoff 登记 |
| r2-P2-11 | R-CAND-4 增加同一步 abandoned+pending 双行可分别断言 |

## 禁止范围

- 不改冻结契约字节（15 pin）；不改 `G-DELETE-IMPL`；不动用户数据；不 push。
- 不改 schema / 不建迁移 / 不加列索引 CHECK。
- 不顺手修 FEA-03/FEA-10 其它功能；不释放其它实现 Task。
- 不以 fake executor / InMemory catalog / 测试专用 pipeline 替代真实生产 assembly。
- 不在 `apps/**`、`doc/reviews/**`、ADJ 上写入。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| - | - | - | `-` | `-` | CANONICAL |

## Resource Manifest

实现尚未开始：仓库内无 worktree、无构建产物；开始后按 `Workspace Governance` 在 `G:\CODEX\New Manga.workspace\` 建 task-env 并在本表补齐逐项处置。

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| doc-task | - | NOT_APPLICABLE | - | - | 范围冻结阶段；未访问用户数据 |
| build/temp（未来） | - | PENDING | ..\New Manga.workspace\ | - | 实现开始前补齐具体路径与处置 |

## Closeout Record

- 2026-11-01：`proposed`（评估完成，等用户拍板）。
- 2026-11-01：用户裁决 D1–D4 落盘（ADJ U-13），冻结范围 v1（`419f891c0`）。
- 2026-11-01：范围复核 r1 `changes_requested`（P1×3/P2×10）→ v2（`98fbccdf5`）逐条处置。
- 2026-11-01：范围复核 r2 `changes_requested`（P1×2/P2×7）→ 本版 v3 处置（R-CAND-2 改 UPSERT/三态保留；R-ART-2 publish 后移；r2 的 P2×7 细分 11 项全部处理）。
- 2026-11-01：范围复核 **r3 `approved`**（P0=0 / P1=0 / P2×10 非阻断）；按 r3 建议修正 4 条改文项（R-SEAM-4 的 `PAGE` 分支、payload 字段与 `media_artifacts` 列、R-ART-2 的 `stage_updates`/`persist` 顺序、R-CAND-3 例外口径）。
- 2026-11-01：`ready` 交 Codex 实现；`base_commit` 更新为修订后的冻结提交（见 frontmatter）。
- 2026-11-01：`proposed`，派独立复核 r3 审查 v3；**复核通过前不 `ready`、不派实现**。`base_commit` 于 `ready` 时更新为最终冻结 head。
