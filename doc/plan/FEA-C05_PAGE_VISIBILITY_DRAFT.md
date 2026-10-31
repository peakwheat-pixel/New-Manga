# FEA-C05 页可见性谓词（草案）

状态：**DRAFT / 未冻结 / 不释放实现 Task**
日期：2026-11-01
作者：DSH（Lead / Architect / Integrator）
依据：[FEA-01 契约清单](FEA-01_CONTRACT_DRAFT.md) 的 C-05、[FEA-00 方案 r4](../design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md)、[C-01b 存储契约](FEA-C01b_STORAGE_CONTRACT_DRAFT.md)（SC-01…SC-39）、代码现状（`src/infrastructure/sqlite/schema.py`）

**边界声明**：本文件是**草案**。它把「一页在什么时候算可见/可读」写成可验证谓词，供 C-01b 的 SC 条款与实现 Task 引用。不改代码、不改 M2-C1 冻结契约。

---

## 1. 问题

「页可见性」在现有实现里被多处分散判断（UI 读、导出、删除预览、Run 快照），没有单一谓词。Fluent 前端与引用源导入需要**同一套**判定，否则会出现「UI 看得到、导出看不到」或「删除预览说没有、实际有」。

## 2. 数据模型事实（`schema.py`）

| 表 | 关键列 | 与可见性的关系 |
|---|---|---|
| `pages` | `page_id, chapter_id, sort_order, deleted_at` | `deleted_at IS NULL` = 页本身未被软删 |
| `media_artifacts` | `artifact_id, page_id, artifact_type, current_revision_id` | `current_revision_id` 指向当前 revision |
| `artifact_revisions` | `artifact_revision_id, revision_no, managed_path, file_hash, integrity_status, is_pinned, pipeline_run_id, step_run_id, created_at` | `integrity_status='valid'` 是内容可读前提 |

## 3. 可见性谓词（冻结候选）

一页 `p` 在时刻 `t` **可见**，当且仅当同时满足：

```
V(p, t) ≡
  P1. p.deleted_at IS NULL                                    -- 页未被软删
∧ P2. ∃ a ∈ artifacts(p): a.artifact_type ∈ VISIBLE_TYPES        -- 存在**同一个** artifact
∧ P3. a.current_revision_id IS NOT NULL                         -- 该 artifact 有当前 revision
∧ P4. r = revision(a.current_revision_id)
     ∧ r.integrity_status = 'valid'                             -- 该 revision 内容完整（P2–P4 绑定同一个 a）
∧ P5. r.created_at <= t                                        -- 已落库（revision 是提交产物；见 §4）
∧ P6. active_runs(p) = ∅  ∨  所有 run.status ∉ ACTIVE_STATES   -- 无活跃 Run（见 §4）
```

其中 `VISIBLE_TYPES = {'original','thumbnail','clean','translated','render_preview','export'}`（`detection_overlay`/`mask`/`debug_*` 是中间产物，**不**构成可见性）。

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
- 语义区分：**可见**（能读）≠ **稳定**（可安全导出/可删除）。导出与删除预览要求 `V(p,t) ∧ 无在途 Run`。

## 5. 失败语义

| 情形 | 行为 |
|---|---|
| `current_revision_id` 指向的 revision 缺失 | 该页**不可见**（P4 不满足），记 `DATA_INTEGRITY_BROKEN`（内部诊断，不向 UI 暴露路径） |
| `integrity_status = 'unknown'`（schema 允许） | 该页**不可见**（P4 只接受 `valid`）；记 `DATA_INTEGRITY_UNKNOWN` |
| `integrity_status ∈ {'missing','corrupted'}` | 不可见；UI 显示「内容损坏」占位，不显示路径 |
| 在途 Run 存在 | 可见；导出/删除预览标注「有在途任务」 |
| `deleted_at` 非空 | 不可见（软删页） |

## 6. 与 C-01b 的接口

- C-01b SC-30/SC-31/SC-33 的删除语义**预期**引用本谓词（当前 SC 条文未涉可见性/内容摘要，属**后续细化**，不是既有条文）；删除预览的「内容摘要」建议用 `V(p,t)` 计数、不可见页不计入。
- 导出（FEA-14-EXPORT）也引用本谓词：只导出 `V(p,t) ∧ 无在途 Run` 的页。

## 7. 冻结条件

1. 独立复核通过（上下文独立）；
2. `VISIBLE_TYPES` 与 `active_runs` 语义经 C-01b/ADJ-001 确认；
3. `check.ps1` PASS。

## 8. 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-01 | 建立草案：数据模型事实、可见性谓词 V(p,t) + P1–P6、判别 SQL 参考、在途写判定、失败语义、与 C-01b 接口、冻结条件 | DSH |
