# FEA-C05 页可见性谓词（草案）

状态：**UNFREEZE v1.2 候审（2026-11-04；按 r15 approved 提交语义修订，待已提交字节独立复核后重冻）**（已冻结历史：v1.1 FROZEN 2026-11-03、v1.0 FROZEN 2026-11-01；载体待建 `CONTRACT-UNFREEZE-2026-11-04.md`；冻结记录将更新 [FEA-CONTRACT-FROZEN-C05](FEA-CONTRACT-FROZEN-C05.md)）
日期：2026-11-01（v1.0）；2026-11-03（v1.1 UNFREEZE）；2026-11-04（v1.2 UNFREEZE）
作者：DSH（Lead / Architect / Integrator）
依据：[FEA-01 契约清单](FEA-01_CONTRACT_DRAFT.md) 的 C-05、[FEA-00 方案 r4](../design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md)、[C-01b 存储契约](FEA-C01b_STORAGE_CONTRACT_DRAFT.md)（SC-01…SC-39）、代码现状（`src/infrastructure/sqlite/schema.py`）；v1.2 依据：实现 Review r1 R1-I001 + 独立裁决（方案 B）+ UNFREEZE r15 approved（`../reviews/FEA-09-UNFREEZE-r15-review.md`）

**边界声明**：本文件是**草案**。它把「一页在什么时候算可见/可读」写成可验证谓词，供 C-01b 的 SC 条款与实现 Task 引用。不改代码、不改 M2-C1 冻结契约。

---

## 1. 问题

「页可见性」在现有实现里被多处分散判断（UI 读、导出、删除预览、Run 快照），没有单一谓词。Fluent 前端与引用源导入需要**同一套**判定，否则会出现「UI 看得到、导出看不到」或「删除预览说没有、实际有」。

## 2. 数据模型事实（`schema.py`）

| 表 | 关键列 | 与可见性的关系 |
|---|---|---|
| `pages` | `page_id, chapter_id, sort_order, deleted_at` | `deleted_at IS NULL` = 页本身未被软删 |
| `pages`（v1.1 / C-15 v7） | `source_mode ∈ {managed, referenced}`、`integrity_status ∈ {incomplete, complete}` | referenced 页不依赖 artifact/revision；完整性由 C-15 §4.1 `is_complete_page` 定义 |
| `media_artifacts` | `artifact_id, page_id, artifact_type, current_revision_id` | `current_revision_id` 指向当前 revision（managed/derived 分支） |
| `artifact_revisions` | `artifact_revision_id, revision_no, managed_path, file_hash, integrity_status, is_pinned, pipeline_run_id, step_run_id, created_at` | `integrity_status='valid'` 是内容可读前提（managed/derived 分支） |

## 3. 可见性谓词（冻结候选）

一页 `p` 在时刻 `t` **可见**，当且仅当同时满足：

```
V(p, t) ≡
  P1. p.deleted_at IS NULL ∧ c.deleted_at IS NULL ∧ b.deleted_at IS NULL   -- 页/章节/书均未软删
∧ P2. ∃ a ∈ artifacts(p): a.artifact_type ∈ VISIBLE_TYPES        -- 存在**同一个** artifact
∧ P3. a.current_revision_id IS NOT NULL                         -- 该 artifact 有当前 revision
∧ P4. r = revision(a.current_revision_id)
     ∧ r.integrity_status = 'valid'                             -- 该 revision 内容完整（P2–P4 绑定同一个 a）
∧ P5. r.created_at <= t                                        -- 已落库（revision 是提交产物；见 §4）
```

其中 `c` = chapter、`b` = book（软删可发生在任一级）。

**稳定性谓词**（导出/删除预览用，独立于可见性）：

```
S(p, t) ≡ V(p, t) ∧ active_runs(p) = ∅
```

其中 `active_runs(p)` = 该页上有 `pipeline_run_id`/`step_run_id` 且 `run.status ∈ ACTIVE_STATES = {pending, running, paused, blocked, interrupted}` 的 Run（与 `core_assembly.py:171-181` 一致；`prepared`/`committed` 不是 Run 状态）。

其中 `VISIBLE_TYPES = {'original','thumbnail','clean','translated','render_preview','export'}`（`detection_overlay`/`mask`/`debug_*` 是中间产物，**不**构成可见性）。

### 3.1 模式分派、managed 等价 witness 与 referenced 页分支（v1.2 UNFREEZE）

**总可见性按 `source_mode` 分派，不得让两种模型互相穿透**：

```text
V(p,t) ≡
  (pages.source_mode = 'managed'    ∧ V_managed(p,t))
∨ (pages.source_mode = 'referenced' ∧ V_ref(p,t))

V_managed(p,t) ≡ V_artifact(p,t) ∨ V_copy_original(p,t)

V_artifact(p,t) = §3 原 P1–P5（artifact/revision 条件；不受 pages 尺寸/完整性/created_at 约束）
V_copy_original(p,t) =
  P1 ∧ pages.source_mode='managed' ∧ pages.integrity_status='complete'
  ∧ pages.source_hash IS NOT NULL ∧ pages.managed_original_ref IS NOT NULL
  ∧ pages.width > 0 ∧ pages.height > 0 ∧ pages.created_at <= t
V_ref(p,t) = 现有 referenced 分支（P1∧P7∧P8∧P5，字节不变）
```

- `V_artifact(p,t)` = §3 原 P1–P5，**字节与语义均不变**；**仅当** `source_mode='managed'` 时适用。**不要求** `pages.integrity_status`（artifact/revision 自身的 integrity 仍是内容可读前提）。
- `V_copy_original(p,t)`：既有 Managed Copy 表示（Page 的 `managed_original_ref` 即 immutable original）作为 managed 的第二 witness；正常导入不要求创建 ORIGINAL artifact 行，也**不得**为凑 witness 批量补造 artifact/revision。
- `V_ref(p,t)`（referenced 页不使用 artifact/revision）：

```text
P1. p.deleted_at IS NULL ∧ c.deleted_at IS NULL ∧ b.deleted_at IS NULL
P7. pages.source_mode = 'referenced' ∧ pages.integrity_status = 'complete'
    ∧ pages.source_hash IS NOT NULL ∧ pages.width > 0 ∧ pages.height > 0
P8. ∃ b ∈ page_bindings:
      b.page_id = p.page_id ∧ b.status = 'healthy'
      ∧ b.verified_digest = e.content_digest
      ∧ (b.source_id, b.accepted_source_version, b.entry_id) 指向存在且同 source 的 entry/version
P5. p.created_at <= t
```

- **witness 独立性（冻结）**：任一合格 witness 使 `V` 真；一个 witness 失败**不否定**另一个（坏 artifact 不否定合格 copy，坏 copy 不否定合格 artifact）。`V` 真**不**保证 `R`（可读）；`R` 失败必须 typed 返回，**不得**静默丢弃/隐藏 V 行。页面尺寸/时间只约束 copy witness；revision 时间只约束 artifact witness；父级软删否定两个 witness。
- 稳定性不变：`S(p,t) = V(p,t) ∧ active_runs(p)=∅`。
- **资源选择（属 R，不属 V）**：managed 读取优先当前 `original` artifact 的 `integrity_status='valid'` current revision；否则回退 `pages.managed_original_ref`；两者都经受管根校验；缺失/越根/不可读 → typed 失败，**不得**回退任意路径，也不得因 R 失败隐藏 V。
- **冻结反例矩阵**：

| # | artifact witness | copy witness | 期望 |
|---|---|---|---|
| 1 | 合格 original revision | 列不完整 | V 真；投影可按 original 回填；R 可读当且仅当文件存在/受管根通过/读取成功 |
| 2 | 无 | copy 完整（含正尺寸） | V 真；R 可读当且仅当 Managed Copy 文件存在且受管根通过 |
| 3 | 合格非 original（thumbnail/clean 等） | 失败 | V 真；投影须保留该行（`original_available=false`，不得丢弃）；R typed 失败 |
| 4 | 失败/无 | 失败 | V 假（半写、零/负尺寸、`created_at>t`、父级软删等） |
| 5 | 失效 artifact | copy 成功 | V 真（witness 独立） |
| 6 | 两 witness 均成功 | 成功 | V 真；同页去重，不重复页 |
| 7 | revision 未来/非 valid/NULL/dangling/非 VISIBLE_TYPES | 失败 | artifact witness 失败；copy 独立判定（两失败才 V 假） |
| 8 | referenced 页存在 artifact | — | 不得经 managed 分支穿透 |

- **参考投影形状（v1.2，实现可扩展但不得丢失 V 行）**：可完整构造时为既有 `Page`；仅 artifact witness 且缺导入列时，以只读投影暴露（最少：`page_id/chapter_id/source_mode/sort_order`、witness、`original_available`、可用时的 `source_hash/managed_original_ref/width/height/integrity_status`；空值 NULL，绝不用 thumbnail/clean hash 冒充源 hash）；投影禁止写回/伪造 provenance。

### 3.2 三谓词拆分（v1.1 UNFREEZE 追加；v1.2 更新 V）

C-05 明确区分，不得混用：

| 谓词 | 定义 | 用途 |
|---|---|---|
| `is_complete_page(p)` | 数据完整性（**不看** deleted/时间/资源）：managed = `source_hash/managed_original_ref/width>0/height>0` 非空且 `integrity_status='complete'`；referenced = P7 ∧ P8。 | 迁移守恒、缓存/计数、重导入判重 |
| `V(p,t)` | 数据库可见性：§3.1 的模式分派（managed = `V_artifact ∨ V_copy_original`；referenced = P1∧P7∧P8∧P5） | reader/导出/删除预览的数据库投影 |
| `R(p,t)` | 当前可读性：`V(p,t)` ∧ 资源授权有效（managed：original revision 或 Managed Copy 经受管根校验；referenced：C-16 有效 source-read grant + identity 匹配） | 实际读取/解析；`V` 为真不代表此刻可读，读取失败必须 typed |

**失败语义（v1.2 更新行）**：

| 情形 | 行为 |
|---|---|
| managed artifact witness 的 `current_revision_id` NULL/缺失/非 valid/非 VISIBLE_TYPES | 该 artifact **不是 witness**；copy witness 独立判定；两者皆否 → 不可见（内部诊断码沿用） |
| managed copy witness 不完整（半写/零尺寸/页时间未来/父级软删） | copy witness 失败；artifact witness 独立判定；两者皆否 → 不可见 |
| `V_managed` 为真但 original 资源不可得（仅非 original artifact witness） | 行必须仍可观察（只读投影，`original_available=false`）；`R` 返回 typed 失败；不得丢弃/显示空页/回退路径 |
| referenced 页 `integrity_status='incomplete'` 或 binding 非 healthy | 不可见（P7/P8 不满足）；行保留、可诊断/可恢复；记内部 `DATA_INTEGRITY_INCOMPLETE` |
| referenced 页 `V` 为真但 Host 授权撤销/失联/identity 漂移 | 数据库投影仍可见；读取返回 `SOURCE_ACCESS_DENIED`/`SOURCE_GRANT_REVOKED`/`FILE_IDENTITY_CHANGED` typed；不得显示空页或回退路径读 |
| 旧 managed 页缺受管文件 | `is_complete_page` 仍按数据列判定；`V` 按 copy/artifact witness 判定；读取/导出按既有失败语义；迁移期由 C-15 §1 资源守恒阻断切入口 |

**判别 SQL（参考实现，非冻结 SQL）**：

```sql
SELECT DISTINCT p.page_id
FROM pages p
JOIN chapters c ON c.chapter_id = p.chapter_id
JOIN books b ON b.book_id = c.book_id
JOIN media_artifacts a ON a.page_id = p.page_id
JOIN artifact_revisions r ON r.artifact_revision_id = a.current_revision_id
WHERE p.deleted_at IS NULL AND c.deleted_at IS NULL AND b.deleted_at IS NULL
  AND a.artifact_type IN ('original','thumbnail','clean','translated','render_preview','export')
  AND r.integrity_status = 'valid'
  AND r.created_at <= :t
ORDER BY p.chapter_id, p.sort_order;
```

## 4. 「在途写」的判定（P5/P6）

- **P5**：`r.created_at` 是 revision 落库时间（schema 无 `committed_at` 列）；在途写不会产生 revision 行（revision 是提交产物）——所以 P5 主要防「未来时间戳」的脏数据。
- **P6**：`active_runs(p)` = 该页上有 `pipeline_run_id`/`step_run_id` 且 `run.status ∈ ACTIVE_STATES` 的 Run。**ACTIVE_STATES = {'pending', 'running', 'paused', 'blocked', 'interrupted'}**（与 `core_assembly.py:171-181` 的非终态集合一致；`prepared` 不是 Run 状态，`committed` 也不是。可见性判定**不阻塞**这些 Run（页仍可见），但**导出/删除预览**必须把「有活跃 Run」作为**警告**。
- 语义区分：**可见**（能读）≠ **稳定**（可安全导出/可删除）。导出与删除预览要求 **`S(p,t)`**（= `V(p,t) ∧ active_runs(p)=∅`）。

## 5. 失败语义

> v1.2 注：下表的「不可见」仅描述 **artifact witness** 的失败；managed 页仍可能由 copy witness 判为可见。V 真而 R 失败按 §3.2 v1.2 行 typed 返回。

| 情形 | 行为 |
|---|---|
| `current_revision_id` 为 NULL | 该 artifact 不构成 witness（P3 不满足；schema `:72` 允许 NULL）；copy witness 独立判定 |
| `current_revision_id` 指向的 revision 缺失 | 该 artifact 不构成 witness（P4 不满足），记 `DATA_INTEGRITY_BROKEN`（内部诊断，不向 UI 暴露路径） |
| `integrity_status = 'unknown'`（schema 允许） | 该 revision 不构成 witness（P4 只接受 `valid`）；记 `DATA_INTEGRITY_UNKNOWN` |
| `integrity_status ∈ {'missing','corrupted'}` | 该 artifact 不构成 witness；UI 对 V 页按 R 失败呈现「内容损坏」占位，不显示路径 |
| 在途 Run 存在 | 可见；导出/删除预览标注「有在途任务」 |
| `deleted_at` 非空 | 不可见（软删页；否定两个 witness） |

## 6. 与 C-01b 的接口

- C-01b SC-30/SC-31/SC-33 的删除语义**预期**引用本谓词（当前 SC 条文未涉可见性/内容摘要，属**后续细化**，不是既有条文）；删除预览的「内容摘要」建议用 `S(p,t)`（稳定页）计数、不可见/不稳定页不计入。
- 导出（FEA-14-EXPORT）也引用本谓词：只导出 `V(p,t) ∧ 无在途 Run` 的页。

## 7. 冻结条件

1. 独立复核通过（上下文独立）；
2. `VISIBLE_TYPES` 与 `active_runs` 语义经 C-01b/ADJ-001 确认；
3. `check.ps1` PASS。

## 8. 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-01 | 建立草案：数据模型事实、可见性谓词 V(p,t) + P1–P6、判别 SQL 参考、在途写判定、失败语义、与 C-01b 接口、冻结条件 | DSH |
| 2026-11-03 | **v1.1 UNFREEZE**：新增 §3.1 referenced 页分支、§3.2 三谓词拆分（`is_complete_page`/`V`/`R`）与失败语义行；§2 增 `source_mode/integrity_status` 事实；保留 v1.0 managed/artifact 分支字节不变。载体 [CONTRACT-UNFREEZE-2026-11-03](../reviews/CONTRACT-UNFREEZE-2026-11-03.md)；待独立复核后重冻并重算 pin | DSH；FEA-09-PREREQ-1 契约复核 r1 R1-001 |
| 2026-11-04 | **v1.2 UNFREEZE**：§3.1 增加 `V_copy_original` 等价 witness、witness 独立性、V/R 分离、资源选择与反例矩阵 1–8、参考投影形状；§3.2 表/失败语义与 §5 注同步。依据实现 Review r1 R1-I001 + 独立裁决方案 B；UNFREEZE r15 approved（P0=0/P1=0，reviewer 链 r1–r15）；载体 `CONTRACT-UNFREEZE-2026-11-04.md`；已提交字节复核后重冻并重算 pin | DSH |
