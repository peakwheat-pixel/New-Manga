# FEA-00a 数据安全修复评估 + 下一实现候选建议（FEA-03 前置）

**评估快照**：`main` = `15aa7bf3b`（2026-11-01）
**作者**：DSH（Lead / Architect / Integrator）
**性质**：**只读评估**（不改代码、不释放实现卡、不改冻结契约/Gate）。结论供用户确认实现范围；`G-DELETE-IMPL` 仍 OPEN。
**依据**：方案 §15.5（`:905`–`:908`）、§15.6（`:919`/`:923`）、§12.1 候选依赖（`:639`–`:641`）；C-11 前置登记 `doc/plan/FEA-C11_IMPL_PREREQS.md`；FEA-00 F20（`:66`）。

---

## 1. 结论摘要

1. **F20 缺陷在快照代码上成立**：`RegionStepWriter._persist` 在 pipeline seam **之前**就提交了 live `regions.text_json` 与 `region_revisions` 行，只把 `current_revision_id` 留给 seam；seam 失败时**前两处已变更且无补偿** → 违反 §15.5「三处零变化」。
2. **同类第二处**：`ArtifactStepWriter.adopt_current` 在 handler 内先提交 `media_artifacts.current_revision_id`，seam 失败时同样留下已推进的指针。§15.5 只点名 region；**是否纳入 FEA-00a 需用户/DSH 定**（见 §7 D2）。
3. **修复可不改 schema、不改 `src/application/tasks/service.py`**：复用既有 `step_result_candidates` 表做 pre-seam 候选（`payload_json` + `base_revision_id` + `status` 恰好够用），seam 在 `commit_step` 内一次性落 revision 行 + text + 指针 + 解决候选。**写域可保持在方案给定的 `src/infrastructure/providers/` + `src/infrastructure/sqlite/pipeline.py` + `tests/`**，无需扩到 FEA-10 的 `src/application/tasks/`。
4. **L-1/L-2/L-5 对 FEA-00a 均不适用**（无 Source 四表 DDL、无 wire 码/白名单、无整库恢复），且复用既有表 → **不引入迁移**；再触发条件见 §6。
5. **建议顺序**：`FEA-00a`（数据安全门）先于 `FEA-03`；`FEA-03` 在快照中**完全无 draft journal / edit token / commit receipt / protection epoch 实现**，属新设计，写域跨 `src/application/`、`src/domain/`、`src/infrastructure/sqlite/`、`NewManga.ApplicationCore`。

---

## 2. F20 现状与缺口证据（只读核对）

| # | 缺口 | 证据（快照 `15aa7bf3b`） |
|---|---|---|
| **G1** | **prepare 阶段已写 live**：`_persist` 插入 `region_revisions` 行并 `UPDATE regions SET text_json`，然后 `commit()`；`current_revision_id` 留待 seam | `src/infrastructure/providers/step_writes.py:195`–`:281`（插入行 `:248`–`:266`、写 text `:269`–`:276`、提交 `:277`；注释 `:267`–`:268` 自述「pointer stays behind」） |
| **G2** | **seam 失败无补偿**：`commit_step` 只在同一事务内翻指针/写 stage/persist；失败返回 `input_revision_changed` / `lock_changed` / `db_failed` / `target_not_found`，但 prepare 的副作用已提交，**不回滚** | seam 实现 `src/infrastructure/sqlite/pipeline.py:742`–`:799`；失败分支消费 `src/application/tasks/service.py:752`–`:789`（冲突→记录 candidate + FAILED `:764`–`:786`；DB 失败→`_fail_step` `:788`–`:789`） |
| **G3** | **artifact 同类缺陷**：`adopt_current` 在 handler 事务内 CAS 并提交 `media_artifacts.current_revision_id`，seam 之前指针已推进；且 `publish` 已在 prepare 提交 `artifact_revisions` 行与落盘文件 | `step_writes.py:421`–`:459`（提交 `:456`；`publish` 写行/文件 `:358`/`:365`/`:394`）；handler 调用 `handlers.py:962`（adopt），`:599`/`:647`/`:733` 返回 `revision_updates=updates` |
| **G4** | **候选暂存表已存在但未用于 pre-seam**：`step_result_candidates(candidate_id, pipeline_run_id, step_run_id, target_id, page_id, region_id, result_kind, base_revision_id, payload_json, reason, status, created_at, resolved_at)` 仅用于 seam 拒绝后的诊断记录 | schema `src/infrastructure/sqlite/schema.py:379`–`:396`（v5 `:521`）；写入点 `pipeline.py:516`–`:528`；清理由 `library.py:571` |
| **G5** | **测试缺口**：现行测试只覆盖「几何保存 DB 失败零写」「seam guard 单事务」，**没有**断言「provider prepare + seam 失败 → 三处零变化」 | 零写测试 `tests/core/test_region_db_failure.py:100`–`:140`；guard 测试 `tests/core/test_region_transactional_guards.py:153`–`:175`；seam 测试 `tests/pipeline/test_pipeline_production_seam.py` 无失败零变化断言 |
| **G6** | **pause/cancel/崩溃**：prepare 之后无 staging，副作用即 live；进程崩溃/DB 重开后无法区分「已 prepare 未 seam」与「已 seam」 | 与 G1/G2 同源；无 staging 目录/表可查（除 G4 的候选表） |
| **G7** | **blast radius 可数**：直接使用 `RegionStepWriter` / `adopt_current` 的测试 **8 个文件**（`test_bootstrap.py`、`test_page_catalog_modes.py`、`test_regionless_rebinding.py`、`t111_support.py`、`test_detect_handler.py`、`test_full_chain.py`、`test_handlers_pipeline.py`、`test_retype_redetect_persistence.py`）→ 修复会牵动既有测试预期，必须逐项核对「是否本应保持 live 语义」 | `rg` 统计（快照） |

**结论**：F20 不是「最终 seam 少一个检查」，而是**prepare 的写事务与 seam 的提交事务分离**；只在 seam 加检查无法满足 §15.5。

---

## 3. §15.5 硬验收的精确含义（本评估采用）

| 断言 | 含义（可执行） |
|---|---|
| **A1 三处零变化** | seam **未成功**（resolve 失败或确认前中断）时，`regions.text_json`、`regions.current_revision_id`、`region_revisions` 行数三者与 prepare 前**完全相同** |
| **A2 候选可诊断** | 失败候选必须可查询（现有 `step_result_candidates` 行：`reason`/`status`/`payload_json`/`base_revision_id`），不因失败丢失 |
| **A3 成功路径同事务** | success 时 revision 行、text、指针、Run receipt 相关写入在**同一事务**提交（不存在中间可观察状态） |
| **A4 prepare 不触碰 live** | prepare 阶段对 `regions`/`media_artifacts` 仅允许**读**；任何 live 写只发生在 seam 事务内 |
| **A5 重启可判定** | prepare 后崩溃/重启：live 三处不变，候选可识别为「未完成」并可清理/重试，不出现半提交 |
| **A6（若纳入）artifact 指针** | `media_artifacts.current_revision_id` 同样遵守 A1/A4（指针只在 seam 事务内推进）。**D1=② 时还必须覆盖 `ArtifactStepWriter.publish` 在 prepare 提交的 `artifact_revisions` 行与落盘文件**（`step_writes.py:358`/`:365`/`:394`），即 staging 的不只是指针，还包括 revision 行与文件；成功时由 seam 事务统一 adopt（含 `handlers.py:962` 的 `adopt_current` 调用点）。 |
| **A7 §15.6 出口（R1-P2-006）** | ①**关闭新写入入口**：修复后 prepare 路径不再有 live 写（A4 断言 + grep 断言覆盖）；②**旧库只读核验**：对既有 DB 以只读方式核验三处一致性与候选可读，**保留备份与候选**不删除（证据留 `verification/`）。 |

---

## 4. 最小写域建议（FEA-00a）

| 文件 | 角色 | 必要性 |
|---|---|---|
| `src/infrastructure/providers/step_writes.py` | `RegionStepWriter._persist` 改为写 candidate；`ArtifactStepWriter` 若纳入则 `adopt_current` 改为 candidate | **核心** |
| `src/infrastructure/providers/handlers.py` | 局部：构造 candidate 所需 run/step 上下文（region 路径已具备 `:438`–`:439`、`:524`–`:525`、`:458`/`:548`，**可能 0 改动**）；**仅 D1=② 时**需改 `:962` 的 `adopt_current` 调用点 | 视 D1 |
| `src/infrastructure/sqlite/pipeline.py` | `commit_step`：解析 candidate token → 同事务插入 `region_revisions` + `UPDATE regions.text_json` + 指针 CAS + 标记 candidate resolved | **核心** |
| `tests/` 内明确测试 | 新增 §6 矩阵；修正 G7 中受影响的既有测试 | 必要 |
| `src/application/tasks/service.py` | **不需要改**（token 通过既有 `StepResult.revision_updates` 传递；失败 candidate 记录逻辑沿用） | — |

**不新增 schema/迁移**（复用 `step_result_candidates`）；若最终决定不用该表而新建 staging 表 → 属 schema 变更，须先做迁移契约判断（见 §7 D3）。

**设计约束**：prepare 只允许写 candidate（`status='prepared'`），**不得**写 `regions`/`media_artifacts`；seam 事务同时完成「插 revision 行 + 写 text + 翻指针 + `status='resolved'`」，任一失败整体回滚（A3）。

### 4.1 token 契约（R1-P2-001，冻结前必写）

**token 必须是 prepare 预生成的真实 revision id**（`uuid.uuid4().hex`），不得用 opaque 串：

1. prepare 生成 `revision_id` → 候选行以该 id 为键写入 `step_result_candidates`（`payload_json` = 待提交快照，`base_revision_id` = 读取时的 `current_revision_id`，`status='prepared'`）；
2. handler 返回 `revision_updates={"region": <该 revision_id>}`（`StepResult.revision_updates` 是 `Mapping[str, str]`，`models.py:355`）；
3. seam 用该 id 找回候选，**同事务**插 `region_revisions` 行（同 id）、写 `regions.text_json`、CAS 翻 `current_revision_id`、置候选 `status='resolved'`。

**依据（为什么必须是真实 id）**：`regions.current_revision_id` 与 `region_revisions` 之间是**延迟复合 FK**（`pipeline.py:769`–`:771` 直接写指针值）；内存 catalog 会把 `revision_updates` 并入 `current_revisions` 快照（`src/application/tasks/store.py:215`、`:236`）。两处都假定值是可解析的真实 revision id；用 opaque token 会破坏 FK 与快照语义，并被迫改 `service.py`/`store.py`（违背 D2=①）。V8 并发的一致性由 revision id 唯一性保证。

### 4.2 staged 失败行的处置与清理归属（R1-P2-003，冻结前必写）

prepare 写入的 `status='prepared'` 行，与 seam 失败后 `service.py:764`–`:786` 再插入的 pending 候选行，会形成**同一步两份候选**；`prepared` 行当前只在页面 purge 时被删（`library.py:571`）。因此实现卡必须指定：

- **语义**：`prepared` = 未 seam 的暂存；失败候选 = seam 拒绝后的诊断记录；两者都以 `step_run_id` 关联，可在查询层区分（`status` 无 CHECK 约束，`schema.py:379`–`:396`）。
- **扫除点**（仍在本 Task 写域 `pipeline.py` 内，不扩写域）：①run 启动时清理该 run 下超期 `prepared` 行；②`commit_step` 失败分支将对应 `prepared` 行置 `status='abandoned'`（或删除）并记录 `resolved_at`。
- **重启可判定**（A5）：重启后 `prepared` 行可识别为未完成、可重试或清理，不出现半提交。

---

## 5. 数据保护断言（建议写入实现卡 AC）

- **AC-A1**：对 revision 冲突、Lock 冲突、`STALE_RUN_SNAPSHOT`、DB 失败、pause、cancel、prepare 后崩溃重启 7 类注入，断言三处零变化（逐类参数化）。
- **AC-A2**：失败候选可在 `step_result_candidates` 查询且 `reason/status/base_revision_id` 正确，payload 与本次 prepare 一致。
- **AC-A3**：成功路径断言三处同事务；不存在「text 已变而指针未变」的可观察中间态（用并发读/事务钩子或 WAL 快照断言）。
- **AC-A4**：静态/结构断言——`step_writes.py` prepare 路径不含对 `regions`/`media_artifacts` 的 `UPDATE`（可 grep 断言）。
- **AC-A5**：重启后断言 live 三处不变、候选可识别/清理；重试成功后三处与 receipt 一致。
- **AC-A6（若纳入 artifact）**：`media_artifacts.current_revision_id` 同样零变化。
- 全部断言从**真实生产 assembly**执行 prepare（§15.5 要求），不得用 fake executor 代跑。

---

## 6. 失败/重启验证矩阵（建议）

| # | 注入 | 期望 |
|---|---|---|
| V1 | seam 前 revision 冲突（`input_revision_changed`） | A1 + A2；无 live 写 |
| V2 | Lock 冲突（`lock_changed`） | A1 + A2 |
| V3 | `STALE_RUN_SNAPSHOT`（`pipeline.py:646`） | A1；Run 不半写 |
| V4 | DB 失败（seam 事务抛错） | A1；整体回滚 |
| V5 | pause / cancel（prepare 后、seam 前） | A1；候选保留可诊断 |
| V6 | prepare 后进程崩溃 + 重启 | A1 + A5 |
| V7 | 成功路径 | A3；三处与 Run receipt 同事务一致 |
| V8 | 并发：两个 prepare 同 region，先到者成功、后到者冲突 | V1 语义 + 不互相污染 |

---

## 7. 待用户/DSH 决策项

| # | 决策 | 选项 | 影响 |
|---|---|---|---|
| **D1** | FEA-00a 是否同时覆盖 artifact 指针（G3） | ① 仅 region（严格按 §15.5 字面）② region + artifact（同类缺陷一并修） | ②更安全但改 `handlers.py` 中 adopt 调用点；①留同类缺陷 |
| **D2** | 是否允许改 `src/application/tasks/service.py` | ① 不允许（本文设计可避免）② 允许（可简化 token 解析） | 影响写域是否与 FEA-10 重叠 |
| **D3** | 候选承载 | ① 复用 `step_result_candidates`（无迁移，但需 §4.2 的清理归属）② 新建 staging 表（需迁移契约与 L-1 判断）③ **文件 staging**（§15.5 原文允许「staging 表/文件」，无迁移、无 schema 改动；代价是崩溃残留文件需清理规则） | ①最小；③最独立于 DB |
| **D4** | 验证等级 | L2 自动化（V1–V8）+ 生产 assembly；是否需要 L3 真机 | 时间/覆盖 |

**推荐**：D1=②（同类缺陷一并修，仍在本 Task 写域内）；D2=①；D3=①；D4=L2。

---

## 8. FEA-03（下一候选）评估

- **现状**：快照代码中**无** draft journal、edit token、commit receipt、protection epoch（`src/**` 检索 0 命中）→ 属**新设计**，不是补齐既有实现。
- **依赖**：`FEA-01`（已冻结）→ `FEA-00a`（本评估对象）→ `FEA-03`。
- **写域（方案 §15.6）**：`src/application/`、`src/domain/`、`src/infrastructure/sqlite/`、`apps/desktop-avalonia/src/NewManga.ApplicationCore/`、对应 tests；L2 高风险；出口「draft ACK、单 owner、独立 patch undo 与 revision restore」。
- **前置判断**：若 draft journal 需要新表 → 触发 schema/迁移契约判断（与 FEA-00a 的 D3 同源）；`L-2` 若引入 draft ACK 错误码/白名单 → 触发；`L-5` 不适用。
- **建议**：**FEA-00a 完成并独立复核后**，再对 FEA-03 单独做范围冻结（不在本卡内释放）。

---

## 9. 只在 README/卡内取证的命令（只读）

```powershell
git -C "G:/CODEX/New Manga" rev-parse --short HEAD           # 15aa7bf3b
# G1/G2：prepare 写 live + seam 失败分支
Select-String -Path src/infrastructure/providers/step_writes.py -Pattern '_persist|text_json|BEGIN IMMEDIATE'
Select-String -Path src/infrastructure/sqlite/pipeline.py -Pattern 'def commit_step|revision_updates|input_revision_changed'
Select-String -Path src/application/tasks/service.py -Pattern 'commit_step|CommitStepOutcome|candidate'
# G4：候选表
Select-String -Path src/infrastructure/sqlite/schema.py -Pattern 'step_result_candidates'
# G7：blast radius
Get-ChildItem -Recurse -Filter *.py -Path tests | Select-String -Pattern 'RegionStepWriter|adopt_current' | Group-Object Path
# 冻结校验
pwsh -NoProfile -File tools/governance/verify_pins.ps1          # 15/15
```

---

## 10. 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-01 | 建立：快照 `15aa7bf3b` 的 FEA-00a 缺口证据（G1–G7）、§15.5 验收精确化（A1–A6）、最小写域、失败/重启矩阵、D1–D4 决策项、FEA-03 现状与前置 | DSH |
| 2026-11-01 | 处置 R1（`FEA-00A-PREP-r1` approved，P2×6）：新增 §4.1 token 契约（真实 revision id + 依据）与 §4.2 staged 行清理归属；A6 扩到 `publish` 的 revision 行/文件 + `handlers.py:962`；新增 A7（§15.6 出口两条）；D3 并列文件 staging；G3 注明 `publish` 同源 | DSH |
