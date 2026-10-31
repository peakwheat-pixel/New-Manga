---
document_id: FEA-C01b-r1
kind: independent_review
task_id: FEA-C01b
round: 1
reviewer: c01b-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams fresh context task-8（DSH Lead 派发的独立上下文 teammate；未参与 FEA-C01b 草案撰写，未参与 AD-003 / ADJ-001 / FEA-01 撰写，未参与任何实现）"
reviewer_independent: true
reviewed_by_implementer: false
reviewed_document: doc/plan/FEA-C01b_STORAGE_CONTRACT_DRAFT.md
reviewed_sha256: fd496a858ec21200e805e80938c7a337d9fe3deaf3f0b7167636320c8b7ad695
reviewed_blob_sha256: fd496a858ec21200e805e80938c7a337d9fe3deaf3f0b7167636320c8b7ad695
reviewed_sha256_basis: "git cat-file blob HEAD:doc/plan/FEA-C01b_STORAGE_CONTRACT_DRAFT.md 的原始字节（LF，11891 B，0×CR）；与工作树字节完全一致，git diff 为空"
reviewed_head: 284708c3c
reviewed_head_full: 284708c3cb1c4cc69826ef87efe345d189d4ec14
reviewed_document_introduced_at: 491dfa0cc
repository: G:/CODEX/New Manga
source_branch: main
appointment: 无独立 Appointment 文件（本次复核由 DSH 以 Agent Teams task-8 直接派发；派发文本即任命范围）
verdict: changes_requested
p0_count: 1
p1_count: 7
p2_count: 6
captured_at: 2026-11-01T02:36:00+08:00
captured_by: c01b-reviewer
---

# 独立复核：FEA-C01b 存储契约（草案）第 1 轮

**本报告不是** ADR、契约冻结、Task 释放、实现验收或集成批准。它只固定被审草案的字节与仓库 head，给出「草案 ↔ AD-003 / ADJ-001 / 现行代码」的一致性判定与 findings。`verdict: changes_requested` 表示**按现状不得冻结**；本报告不代替 DSH 对 findings 的处置，也不代替 AD-003 / ADJ-001 自身的 `G-REVIEW` 收口。

被审对象：`doc/plan/FEA-C01b_STORAGE_CONTRACT_DRAFT.md`（状态 DRAFT / 未冻结），LF blob SHA-256 `fd496a85…b7ad695`（11891 B）。参照：AD-003（`ACCEPTED_ARCHITECTURE_AMENDMENT`）、ADJ-001（`FROZEN_SEMANTICS`）、方案 r4（`74a772167`，r8 `approved`）、FEA-01（C-01b 定义）、`src/**` 现行代码。

---

## 1. 结论

**verdict：`changes_requested`（P0 × 1 / P1 × 7 / P2 × 6）。**

三项主判定：

| 审查维度 | 结果 | 摘要 |
|---|---|---|
| 1. 无新增语义（逐条出处） | **有条件通过** | SC-01…SC-37 **37/37 均能在 AD-003 §3.x / ADJ-001 找到出处**，无凭空条款；但 **SC-01 的「验证」列比 AD-003 更严**（P0），另 3 条把不存在的实现写成现行/验证证据（P1）。 |
| 2. 无遗漏（逐节对账） | **不通过** | AD-003 §3.1–§3.7 共 33 条边界 **全覆盖**；§3.8 的 5 行只覆盖 3 行，**缺「二进制」行与「数据」行**（P1）。38 个边界单元覆盖 36（94.7%）。 |
| 3. 状态标注正确性 | **不通过** | 抽查 6 个关键点：`pages.managed_original_ref` 双读 ✅、`derived/` 可再生产物 ✅、`SourceAccessRegistry` 不存在 ✅、`DatabaseId` 不存在 ✅、`nmbak` 清单不含外部原件 ✅、`ImportPages` grant ≤300 秒/进程内 registry ✅；但追加抽查发现 **SC-19 应 [现行] 却标 [新增]**（P1）、**SC-03 [现行] 与 ADJ-001 §8 直接冲突**（P1）、**SC-08 的「容量预览」无实现**（P1）、**SC-06 的「守卫断言」不存在**（P1）。 |
| 4. 验证方式可执行 | **不通过** | 草案 §3 自设「[现行] 须给出文件/符号 + 回归测试」；实际 14 条 [现行] 条款的验证列 **0 条**给出文件/符号或测试入口（P1）。 |
| 5. 冻结条件是否足够 | **不足** | 缺 AD-003 自身 `G-REVIEW` 收口条件；AD-003 §6 明文规定其在 Codex 复审通过前「**不作为契约冻结依据**」（P1）。 |

**关键量化**：条款 37 条；[现行] 13 + [现行→退役] 1、[新增] 22、[未实现] 1；AD-003 §3 边界单元 38 → 覆盖 36；有出处 37/37；无出处 0。

---

## 2. 逐节对账表（AD-003 §3.1–§3.8）

| AD-003 节 | 边界条目 | 对应条款 | 覆盖 | 备注 |
|---|---|---|---|---|
| §3.1 旧 Managed Copy | 3 | SC-07 / SC-08 / SC-09 | **3/3 ✅** | 文本一致；SC-08 的「容量预览」无实现（F-05） |
| §3.2 新引用导入 | 5（第 1 条拆 2 款） | SC-01+SC-02（第1条）/ SC-03 / SC-04 / SC-05 / SC-06 | **5/5 ✅** | SC-01 验证加码（F-01 P0）；SC-03、SC-06 状态不成立（F-03/F-04） |
| §3.3 备份 | 5 | SC-10 / SC-11 / SC-12 / SC-13 / SC-14 | **5/5 ✅** | SC-12 状态混合（F-14） |
| §3.4 迁移 | 5 | SC-15 / SC-16 / SC-17 / SC-18 / SC-19 | **5/5 ✅** | SC-19 状态错（F-02） |
| §3.5 资源信任根 | 5 | SC-20 / SC-21 / SC-22 / SC-23 / SC-24 | **5/5 ✅** | SC-24 标记越界（F-09） |
| §3.6 外部变化 | 5 | SC-25 / SC-26 / SC-27 / SC-28 / SC-29 | **5/5 ✅** | SC-27 无落点/验证（F-13） |
| §3.7 删除授权 | 5 | SC-30 / SC-31 / SC-32 / SC-33 / SC-34 | **5/5 ✅** | SC-30 验证引用不当（F-08） |
| §3.8 回退 | 5 行 | SC-35（功能开关）/ SC-36（UI）/ **（二进制：缺）** / SC-37（Schema）/ **（数据：缺）** | **3/5 ❌** | 见 F-06（P1） |
| **合计** | **38** | SC-01…SC-37（37 条） | **36/38** | 缺口 2 = §3.8「二进制」行、「数据」行 |

对账口径说明：按 AD-003 §3 的**列表项**（bullet）与 §3.8 的**表格行**计为一个边界单元；SC-01/SC-02 共同覆盖 §3.2 第 1 条，故 37 条条款覆盖 36 个单元。

---

## 3. 逐条出处表（SC-01…SC-37）

「出处」列给出 AD-003/ADJ-001 的对应条目；「判定」列只判**文本是否与出处一致**（状态与验证的正确性见 §4/§5）。

| 条款 | 出处 | 判定 |
|---|---|---|
| SC-01 | AD-003 §3.2 第 1 条前句 | 文本一致；**验证列加码 → F-01 P0** |
| SC-02 | AD-003 §3.2 第 1 条后句（含「至少含」） | 一致 |
| SC-03 | AD-003 §3.2 第 2 条 | 文本一致；**状态不成立 → F-03** |
| SC-04 | AD-003 §3.2 第 3 条 | 一致 |
| SC-05 | AD-003 §3.2 第 4 条 | 一致 |
| SC-06 | AD-003 §3.2 第 5 条 | 文本一致；**状态/验证不成立 → F-04** |
| SC-07 | AD-003 §3.1 第 1 条 | 一致 |
| SC-08 | AD-003 §3.1 第 2 条 | 文本一致；**「容量预览」无实现 → F-05** |
| SC-09 | AD-003 §3.1 第 3 条 | 一致 |
| SC-10 | AD-003 §3.3 第 1 条（含数据类别枚举） | 一致（枚举逐项对齐） |
| SC-11 | AD-003 §3.3 第 2 条 | 一致 |
| SC-12 | AD-003 §3.3 第 3 条 | 文本一致；**状态混合 → F-14** |
| SC-13 | AD-003 §3.3 第 4 条（含括号内五步顺序） | 一致（步骤顺序未变） |
| SC-14 | AD-003 §3.3 第 5 条 | 一致 |
| SC-15 | AD-003 §3.4 第 1 条 | 一致 |
| SC-16 | AD-003 §3.4 第 2 条 | 一致 |
| SC-17 | AD-003 §3.4 第 3 条 | 一致 |
| SC-18 | AD-003 §3.4 第 4 条 | 一致；**漏「回填前身份 unknown」→ F-11** |
| SC-19 | AD-003 §3.4 第 5 条 | 文本一致；**状态错 → F-02** |
| SC-20 | AD-003 §3.5 第 1 条 | 一致 |
| SC-21 | AD-003 §3.5 第 2 条 | 一致（三要素「≤300 秒/直属成员/进程内 registry」逐项保留） |
| SC-22 | AD-003 §3.5 第 3 条 | 一致 |
| SC-23 | AD-003 §3.5 第 4 条 | 一致 |
| SC-24 | AD-003 §3.5 第 5 条 | 文本一致；**标记不在图例内 → F-09** |
| SC-25 | AD-003 §3.6 第 1 条 | 一致 |
| SC-26 | AD-003 §3.6 第 2 条 | 一致 |
| SC-27 | AD-003 §3.6 第 3 条 | 一致；**无落点/验证 → F-13** |
| SC-28 | AD-003 §3.6 第 4 条 | 一致 |
| SC-29 | AD-003 §3.6 第 5 条 | 一致 |
| SC-30 | AD-003 §3.7 第 1 条 + ADJ-001 §3（A/B/C 流程） | 文本一致；**验证引用不当 → F-08** |
| SC-31 | AD-003 §3.7 第 2 条 | 一致（六步顺序与失败保留口径均未变） |
| SC-32 | AD-003 §3.7 第 3 条 | 一致 |
| SC-33 | AD-003 §3.7 第 4 条 + ADJ-001 PD-08 | 一致（fail-closed 三条件逐项对齐） |
| SC-34 | AD-003 §3.7 第 5 条 | 一致 |
| SC-35 | AD-003 §3.8 行 1 | 一致；**漏「拟议」限定 → F-12** |
| SC-36 | AD-003 §3.8 行 2 | 一致 |
| SC-37 | AD-003 §3.8 行 4 | 一致（「无无损自动降级承诺」保留） |
| — | — | **无出处条款：0 条** |

**反向检查（草案是否比 AD-003 更松？）**：除 SC-18/SC-35 两处限定词丢失（P2）与 §3.8 两行未覆盖（P1）外，未发现条款把 AD-003 的强制性要求弱化。**加码检查**：见 F-01（SC-01 验证列）。

---

## 4. Findings

### P0

#### F-01 (P0) — SC-01 的验收口径比 AD-003 更严，且与 SC-02/SC-06 及实测数据冲突

- 位置：草案 `:29`（SC-01 行，「实现落点 / 验证」列）。
- 事实：SC-01 条款文本与 AD-003 §3.2 第 1 条一致（「不创建**永久**全尺寸输入副本」）；但验证列写成「以『导入后 `derived/` **无全尺寸复制**』为验收（大小分布 + 引用计数）」。AD-003 同条明确把 `derived/`、缩略图、PDF raster、ZIP 解码页、tile 定为「**有上限的可再生产物**」，仅禁止「**永久**全尺寸**输入**副本」。
- 冲突证据：
  1. 现行 `derived/pages/page-original-<page_id>.<ext>` 就是全尺寸页副本（`core_service.py:3234` 确定性键、`render_preview.py:115 publish_original`），是阅读器供字节的唯一产物；
  2. 实测数据：`derived/` 170 文件 / 100,435,214 B，其中 169 张 `page-original-*.jpg` / 100,434,899 B，与 managed 根**等量**（`verification/REALUSE-DATA-SAFETY-6/ac2-derived-conclusion.md` §3 表）；
  3. 草案 SC-02 自己允许 `derived/` 存在有上限可再生产物，SC-06 又禁止以「消除双份」为由删除现有 `derived/`/managed 文件（AD-003 §3.2 第 5 条）。按 SC-01 的验证列执行，会与 SC-02、SC-06 及 AD-003 §3.2 第 5 条同时冲突。
- 影响：这是**唯一可能驱动破坏性改动的条款**。若实现 Task 以该 AC 验收，最省事的达成方式是删除/禁止全尺寸 derived 页副本 —— 正是 AD-003 §3.2 第 5 条与 SAFETY-6 AC2 结论共同禁止的动作（`ac2-derived-conclusion.md` §1 结论 3、§5「无生产代码改动」）。
- 建议（供 DSH 处置，不构成我的裁决）：把验证列改写为可满足且不越权的判据，例如「导入后 `derived/` 不含对**源容器整体的全尺寸复制**；页级产物须满足 SC-02 的上限与 cache key 约束；且**不得**删除既有 `derived/`/managed 文件（SC-06）」。

### P1

#### F-02 (P1) — SC-19 状态与验证均与现行代码相反（应为 [现行]）

- 位置：草案 `:62`（SC-19 行）。
- 事实：草案标 `[新增]`，验证「Schema version 检查」。现行代码**已实现**「新 Schema 被旧二进制打开时拒写/只读」：
  - `open_database` 对 `stored > latest_known` 以 `PRAGMA query_only` 只读打开并返回 `SchemaState.TOO_NEW, writable=False`（AC-DB-005）；
  - `MigrationRunner.apply_pending` 在写前抛 `SchemaTooNewError` 且不触碰 DB（`src/infrastructure/sqlite/migrator.py:69-80`，异常定义 `connection.py:60`）；
  - 回归测试存在：`tests/storage/test_schema_migration.py:100`、`tests/storage/test_backup_restore.py:589`（`SCHEMA_TOO_NEW`）；
  - 能力清单记为**已实现**：`doc/design/redesign-v1/00-facts/01_CAPABILITY_INVENTORY.md:429`（CAP-MAINT-04）。
- 影响：冻结后若按 [新增] 处置，实现 Task 会重复实现既有能力，并丢掉既有回归保护；契约「只做确认」的定位被破坏。
- 建议：改标 `[现行]`，验证列指向上述符号与两个测试；若认为 AD-003 §3.4 第 5 条还要求「不得只读继续运行」以外的更强语义，须先把差异显式写进条款，否则视为加码。

#### F-03 (P1) — SC-03 的 [现行] 与 ADJ-001 §8 记录的现状冲突

- 位置：草案 `:31`（SC-03 行，「[现行]（需核对清理路径白名单）」，验证「Trash/GC 过滤器；验证：受保护 revision 不被 GC 命中」）。
- 事实：
  1. 「缓存清理不碰非缓存」为现行事实，但机制是**前缀白名单**：`cleanup.py:41 CACHE_SAFE_PREFIXES = ("cache/",)`，且 `cleanup.py:13-20` 明写 current/pinned revision 与业务行、Lock、任务可恢复数据「structurally」不可清理；
  2. 但「受保护 revision 不被 Trash/GC 命中」**不是**现行事实：ADJ-001 §8 明确记录「B 流程的统一保护 preflight **未实现**（现状为三套异构机制：cache 前缀白名单 / **页级无保护 purge** / book 级 6 项预检）」；
  3. 代码印证：`src/infrastructure/sqlite/library.py:518 purge_pages` → `DELETE FROM pages`（`:613`），**无任何 Lock / pin / current 检查**；`src/application/maintenance/trash.py:196-226 purge_batch` 只做「记 pending → 删行 → 删 managed 文件」。全库 `library.py` 内 `is_pinned`/pinned 命中数为 0。
- 影响：该条款的 [现行] 标签把 ADJ-001 已登记的未实现保护写成了已具备；验证列又把举证挂到恰恰**无保护**的 Trash purge 路径上。
- 建议：拆两条 —— ①「缓存清理只作用于白名单前缀」（[现行]，证据 `cleanup.py:13-20,41`）；②「受保护 revision/Lock/current 不被自动清理命中」（[新增]，来源 ADJ-001 PD-10、AD-003 §1 决定 #4），实现前保持 `BLOCKED`。

#### F-04 (P1) — SC-06 引用的「守卫断言」不存在

- 位置：草案 `:34`（SC-06 行，`[现行]`，落点/验证「守卫断言」）。
- 事实：`src/**` 中没有任何拒绝删除 `derived/`/managed 活页副本的守卫断言（对 `SAFETY-6`/「双份」等关键词的检索仅命中 `core_service.py:476` 一条无关注释）；`verification/REALUSE-DATA-SAFETY-6/ac2-derived-conclusion.md` §5 明记「**无生产代码改动**（AC2 为结论型）」。
- 影响：该条款当前是**被动满足**（代码里没有删除动作），不是"有守卫"；标 [现行] + 声称有守卫会让冻结把不存在的保护当成回归基线。
- 建议：要么改标 [新增] 并在实现 Task 内加守卫（拒绝以「消除双份」为由删除），要么把验证改为可执行的事实陈述：「静态核对：`src/**` 中不存在删除 `derived/` 活页或 managed 原件的路径（除 catalog 孤儿/死行清理与 retired 预览回收，且二者均以 catalog/sha256 校验）」，并引用 `render_preview.py:158,235`。

#### F-05 (P1) — SC-08 的「容量预览」无实现

- 位置：草案 `:41`（SC-08 行，`[现行]（备份清单需补）`，验证「备份清单 + 容量预览；SAFETY-6 AC2 的 managed==derived 证据」）。
- 事实：`nmbak` 备份**已包含** managed 副本 —— `nmbak.py:204-224` 同时取 `revision_refs` 与 `page_original_refs`（后者即 `pages.managed_original_ref`），manifest 记录 `page_original_count/size`；但 `NmbakBackupService` 只有 `create/list/restore`（`nmbak.py:174,142,270`），**没有**任何备份前容量/预估/缺失项预览 API（`src/**` 检索无 backup capacity/estimate 实现）。
- 影响：条款一半现行、一半未实现，却统一标 [现行]；冻结后「容量预览单列」无人承接。
- 建议：拆为「managed 副本必须进备份清单」（[现行]，证据 `nmbak.py:197-226`、`verification/REALUSE-DATA-SAFETY-1`）+「备份/容量预览须单列」（[新增]，AD-003 §3.1 第 2 条后半）。

#### F-06 (P1) — 遗漏 AD-003 §3.8 的「二进制」行与「数据」行

- 位置：草案 §2.8（`:94-100`）只覆盖 §3.8 的行 1（功能开关→SC-35）、行 2（UI→SC-36）、行 4（Schema→SC-37）。
- 缺失内容（AD-003 `:109`、`:111` 原文）：
  - 行 3 **二进制**：「已验证兼容的旧 UI/Host 配新 Core → 必须通过能力与格式 Gate，**不得任意混配**」；
  - 行 5 **数据**：「旧 Managed 副本与应用内人工数据**始终可读**；**不回退**引用模式已产生的引用页；只可标缺失或经明确转换」。
- 影响：行 5 是用户可感知的**回退保证**（引用页不得被静默回退、人工数据始终可读），缺失会使 §3.8 的回退面在契约里只剩「开关/UI/Schema」三层，二进制混配禁令与数据可读保证无法被下游 AC 引用；行 3 是 Release 层面唯一的混配门禁。
- 建议：补 SC-38（二进制 Gate）、SC-39（数据可读与不回退），或把行 3/5 并入 SC-37 并显式引用。

#### F-07 (P1) — 冻结条件缺 AD-003 自身 `G-REVIEW` 收口

- 位置：草案 §4（`:112-118`）三个冻结条件：独立复核 / 用户确认 AD-002 责任表与哨兵口径 / `check.ps1` PASS。
- 事实：
  1. AD-003 §5（`:131`）`G-REVIEW = ADDRESSED_PENDING_R2`；§6（`:140`）明文：「在 Codex 对新 hash 复审通过前，本文件**只作为决策记录生效，不作为契约冻结依据**；契约冻结仍需 DSH 在 D05 显式裁定」；
  2. `doc/reviews/` 中**没有** AD-003 的独立 Review 产物（`*AD-003*` 命中 0），其 `G-REVIEW` 至今未收口；
  3. 同类缺口已被 FEA-00 r8 记为 R8-09（P2）：「引用 AD-003/ADJ-001 作为已记录/已冻结依据时，未提及其自身 `G-REVIEW: ADDRESSED_PENDING_R2`」。
- 影响：草案全部 37 条的语义来源都是 AD-003，而 AD-003 自述「不作为契约冻结依据」。若按草案 §4 冻结，等于用一份未收口 `G-REVIEW` 的文档作为冻结依据，冻结效力自始存在缺口。
- 建议：冻结条件补第 4 条 ——「AD-003 `G-REVIEW` 收口（Codex 对 AD-003 新 hash 复审通过）**或** 用户明确裁决以 AD-003 为冻结依据」；并在 §4 注明 ADJ-001 `G-DELETE-SEMANTICS: SATISFIED` 只覆盖语义层、`G-DELETE-CONTRACT` 仍 OPEN。

#### F-08 (P1) — [现行] 条款的验证列普遍不满足草案 §3 自设标准

- 位置：草案 §3（`:106-110`）自设「[现行]：回归测试 + 代码路径静态核对（**指出文件/符号**）；不得只凭『设计如此』」；实际条款表验证列。
- 事实：14 条 [现行]（含 SC-24）中，**0 条**给出文件/符号或测试入口，全部是动作名：SC-07「读路径回归测试」、SC-09「清理入口只有显式任务」、SC-14「恢复流程回归」、SC-15「迁移入口只有显式操作」、SC-16「守卫」、SC-17「迁移流程」、SC-20「资源通道回归（不许放宽）」、SC-24「权限面核对」、SC-36「界面切换」等。其中 SC-30（`:88`）引用「ADJ-001 PD-01–PD-10；SAFETY-6/7/8 已有并发与预览相关修复」作为证据，而 ADJ-001 §8 明记 PD-01–PD-10 全部**未实现**、`§5.11` 之外的新增能力均为提案；SAFETY-6/7/8 与「应用内删除不触点原文件」无直接关系（真正依据是 `M2-C1 §5.11.4` 与 `library.py:1069-1101` 只删 DB 行与受管文件）。
- 影响：验证列不可执行，则冻结后无法区分「已确认的现行行为」与「作者判断」，[现行] 标签失去可审计性 —— 这正是 F-02/F-03/F-04/F-05 四类错误能同时存在的原因。
- 建议：对每条 [现行] 补「文件:行 + 测试文件/用例名」；无测试的写明「静态核对：<符号>，无负向测试」并登记为缺口，不得留空。

### P2

#### F-09 (P2) — SC-24 使用未定义的状态标记 `[现行→退役]`

- 位置：草案 `:16-19`（图例只定义 [现行]/[新增]/[未实现] 三态）↔ `:72`（SC-24 标 `[现行→退役]`）。
- 影响：机械解析/统计口径不一致（本次统计按 [现行] 计入）。建议：改标 [现行] 并在正文注明「该前提在本决策下退役」，或把图例扩为四态并在全表统一。

#### F-10 (P2) — `[新增]` 与 `[未实现]` 判据重叠，且与 AD-003 §4 同句列举不一致

- 位置：草案 `:16-19` 图例 ↔ `:69`（SC-21 `[新增]`）、`:61`（SC-18 `[新增]`）、`:89`（SC-31 `[新增]`）↔ `:70`（SC-22 `[未实现]`）。
- 事实：AD-003 §4（`:118`）把 `SourceAccessRegistry`、`source-read` grant、递归授权根、ZIP/CBZ 解码器、页面完整性谓词、`DatabaseId` 回填、Windows 回收站桥**同句**列为「当前均无实现」；草案却把其中 4 项标 [新增]、2 项标 [未实现]，且图例中两态定义互相覆盖（都表示「当前没有」）。
- 建议：把判据改成可机械判定的单一维度（例如：AD-003 §4 列举 = [未实现]，§3 要求但 §4 未列举 = [新增]），并对全表重标。

#### F-11 (P2) — SC-18 漏 AD-003 的「回填前身份 unknown」限定

- 位置：草案 `:61` ↔ AD-003 `:76`（「旧库由迁移第一笔原子回填；**回填前身份 unknown**」）。
- 影响：丢掉的是可验证的状态语义（迁移未完成时 `DatabaseId` 必须表达 unknown 而非猜测值）。建议补入条款正文。

#### F-12 (P2) — SC-35 未记「flag 名为拟议、尚无 CLI 参数」，且未区分既有 `--shell=legacy` 入口

- 位置：草案 `:98`（SC-35）、`:99`（SC-36）↔ AD-003 `:113`（「Feature flag 名称…为**拟议**，尚无 CLI 参数」）。
- 事实：三个 flag 名在 `src/**` 中命中 0（仅文档出现），确属拟议；而 SC-36 声称的「UI 切回 Current 界面」在代码中的**实际**入口是既有的 `--shell=legacy`（`apps/desktop-avalonia/src/NewManga.App/AppOptions.cs:65-66`「one-release rollback path」）。
- 建议：SC-35 注明 flag 名为拟议；SC-36 指明现行载体是 `--shell=legacy`，并与 AD-003 §3.8 行 3 的兼容 Gate 关联。

#### F-13 (P2) — SC-27 标 [新增] 但无实现落点/验证

- 位置：草案 `:80`（SC-27 行落点/验证为「—」）↔ 草案 §3（`:109`）要求 [新增] 须有「实现 Task 的 AC + 负向对照」。
- 建议：补落点（同步状态机 / tombstone 表）与最小验证（缺失页保留 tombstone 后人工修改仍可读的负向对照），或与 SC-26 合并。

#### F-14 (P2) — SC-12 在 [现行] 条款中夹带未定方案

- 位置：草案 `:50`（「[现行]（需确认凭据条目不在清单）」+「跨机恢复凭据需另定加密/解锁方案」）。
- 事实：「不备份服务密钥」为现行事实（`nmbak.py:8-10,208-226` 的包成员只有 `library.db`、sidecar、`managed/`，无凭据条目），但后半句是**未定方案**。
- 建议：拆为 [现行]（凭据不在清单）+ [未定/待裁决]（跨机恢复凭据加密方案），避免冻结把未定方案记成现行语义。

---

## 5. 状态标注抽查结果（对照真实代码）

| # | 抽查点 | 草案标注 | 代码事实 | 判定 |
|---|---|---|---|---|
| 1 | `pages.managed_original_ref` 双读是否现行 | SC-07 [现行] | **现行**：读路径 `src/bootstrap/core_assembly.py:293,315,375-379`；解析/阅读 `core_service.py:1627,3207-3245`；导入写入 `core_service.py:763`（"Normal imports write their immutable source to Page.managed_original_ref"）；Host 侧 `derived-read-only`/`managed-read-only` 两个作用域根均可供字节（`resource_channel/dto.py:69 ALLOWED_SCOPE_CLASSES`；`handle_resolver.py:642-705` managed 根身份信任） | ✅ 正确 |
| 2 | `derived/` 是否按可再生产物处理 | SC-02 [新增] | **是**：确定性键 `page-original-{page_id}`（`core_service.py:3234`）、`publish_original` 逐字节发布（`render_preview.py:115-149`）、`render_preview.py:31` 探测缺失即重建、`collect_orphans` 只清无 catalog 行的文件与死行（`render_preview.py:158-229`）。但现行键**不含** decoder 版本/参数，故「cache key 至少含 SourceVersion/entry/decoder 版本/参数」确为 [新增] | ✅ 正确 |
| 3 | `SourceAccessRegistry` 是否存在 | SC-21 [新增] / SC-22 [未实现] | **不存在**：`src/**` 检索 `SourceAccessRegistry`、`source-read`/`source_read` 命中 0 | ✅ 正确 |
| 4 | `DatabaseId` 是否存在 | SC-18 [新增] | **不存在**：`src/**` 检索 `DatabaseId`/`database_id` 命中 0 | ✅ 正确 |
| 5 | `nmbak` 备份清单是否含外部原件 | SC-10 [新增] / SC-12 [现行] | **不含外部原件**：包成员固定为 `manifest.json` + `library.db` + `library.db.sidecar.json` + `managed/…`（`nmbak.py:3-10,50-53`），且模块文档明写「never touches user source files」；**含** `pages.managed_original_ref` 的 managed 副本（`nmbak.py:197-226`）。清单无凭据条目 | ✅ 基本正确（SC-08 例外见 F-05） |
| 6 | `ImportPages` grant 的 ≤300 秒 / 进程内 registry 语义 | SC-21 内嵌引用 | **吻合**：`import_source_refs.py:153`（`expires_at > now + 300` → `E_EXPIRED`）；`ImportSourceGrantRegistry._grants` 为进程内 `dict`（`:108`），单 session 绑定 + 拒重复 id（`:192-203`），解析后一次性消费（`:228-229`） | ✅ 正确 |
| 7 | 新 Schema 被旧二进制打开时拒写 | SC-19 **[新增]** | **已实现**：`connection.py:60` + `migrator.py:69-80`（`SchemaTooNewError`，不触库）+ `open_database` TOO_NEW 只读门；测试 `tests/storage/test_schema_migration.py:100`、`tests/storage/test_backup_restore.py:589`；能力清单 CAP-MAINT-04 记「已实现」 | ❌ **错误 → F-02 P1** |
| 8 | 受保护 revision 不被清理命中 | SC-03 **[现行]** | **未实现统一保护**：现行仅前缀白名单（`cleanup.py:41`）；页级 purge 无保护（`library.py:518,613`；`trash.py:196-226`）；ADJ-001 §8 明记 B 流程保护 preflight 未实现 | ❌ **错误 → F-03 P1** |
| 9 | 「守卫断言」阻止以消除双份为由删除 derived/managed | SC-06 [现行] | **无此守卫**：`src/**` 无相关断言；SAFETY-6 AC2 §5 明记无生产代码改动 | ❌ **错误 → F-04 P1** |

---

## 6. 验证方式可执行性评价（审查重点 4）

| 条款类别 | 草案要求的验证形式 | 实际是否可执行 |
|---|---|---|
| [现行]（14 条） | 回归测试 + 代码路径静态核对（指出文件/符号） | **不可执行**：0 条给出文件/符号或测试用例；4 条（SC-03/06/08/30）所引证据与事实相反或无关（F-03/F-04/F-05/F-08）。**可用于冻结的 [现行] 证据目前只有 0 条。** |
| [新增]（22 条） | 实现 Task AC + 负向对照，未实现前不得 MET | **部分可执行**：SC-18/19/25/26/28/29/31-35/37 有落点或可推导 AC；SC-27 落点为「—」（F-13）；SC-21/23/24 落点是能力名（C-06/Host 命令面）而非可验证断言。 |
| [未实现]（1 条） | 保持 `BLOCKED` 或标注能力缺位 | **可执行**：SC-22 已标注，且与 AD-003 §4 一致。 |

补充：草案 §3 表格的规则本身是对的，问题在于条款表未按该规则填写（F-08）。建议把验证列改造成可机械核对的引用（`文件:行` / `tests/…` 用例名），并在冻结时由检查器只做**存在性**校验（内容真伪仍须人工）。

---

## 7. 冻结条件评价（审查重点 5）

| 草案条件 | 是否足够 | 说明 |
|---|---|---|
| ① 独立复核（本报告） | 部分 | 本报告为 r1，`changes_requested`；P0/P1 未闭环前不满足。 |
| ② 用户确认 AD-002 责任表与哨兵口径 | 成立 | AD-002 `:28`「Managed Copy｜保持既有实现与验收」行与 `:9-10` 顶部横幅确实待用户确认；`check.ps1:274-275` 双哨兵校验已实现（`c01c` 已冻结）。 |
| ③ `check.ps1` PASS | 成立（本次已核对） | 本轮实跑 `pwsh -NoProfile -File tools/governance/check.ps1` 结果 **PASS（3 warnings：7 个非终态 Task；STATUS 80% 预算；REBASELINE_PLAN 80% 预算）**。仅证明结构条件，符合草案自述。 |
| ④ AD-003 `G-REVIEW` 收口 | **缺失** | AD-003 §6 明文「不作为契约冻结依据」；见 F-07。**此项不补，冻结效力存在自始缺口。** |
| ⑤ ADJ-001 `G-DELETE-CONTRACT` 状态说明 | 缺失（建议） | ADJ-001 只 `G-DELETE-SEMANTICS: SATISFIED`；`G-DELETE-CONTRACT`/`G-DELETE-IMPL` 仍 OPEN。草案 §4 末句把 C-09 列为「可在本契约之上逐条冻结」，应注明其仍受 `G-DELETE-CONTRACT` 约束，避免被读成已解冻。 |

---

## 8. 独立性声明

- 我是 `c01b-reviewer`，由 DSH Lead 通过 Agent Teams（`task-8`）派发的**独立上下文** teammate（`reviewer_kind: subagent`），`reviewer_independent: true`。
- 我**未参与** FEA-C01b 存储契约草案的撰写、修订或任何形式的预审，未参与 AD-003 / ADJ-001 / FEA-01 / 方案文本的撰写，未参与 `src/**`、`apps/**` 的任何实现。
- 本次为**只读审查**：唯一写入是本报告 `doc/reviews/FEA-C01b-r1.md`（新建）；未修改草案、AD-003、ADJ-001、FEA-01、Task/STATUS/PLAN/INDEX；未 `git add`/`commit`/`push`；未触碰任何真实数据根，未运行会写入的脚本（仅执行只读的 `tools/governance/check.ps1`）。
- 我的判定不受被审作者影响；finds 的每条事实均附**可复核的路径与行号**，DSH 可逐条重跑。本报告不构成批准，findings 处置由 DSH 负责。

---

## 9. NOT_RUN

- 未运行 `pytest` 或任何生产测试；§5 的「已实现」判定基于代码路径静态核对与既有测试文件存在性（`tests/storage/test_schema_migration.py`、`tests/storage/test_backup_restore.py`），**未执行**这些测试。
- 未在真实数据根（`%APPDATA%\com.newmanga.desktop`）做任何读以外操作；`derived/` 体量数据引自既有证据 `verification/REALUSE-DATA-SAFETY-6/ac2-derived-realdata.json`，本轮未重新盘点。
- 未验证 UI/Host 侧运行行为（Host/V2 删除入口 ADJ-001 §7 已记 `NOT_WIRED`），未验证回收站桥（零实现）。
- 未审查 FEA-08/09/11/12/13 的实现范围与 AC（Source 线仍 `BLOCKED`）。
- 未对 AD-003/ADJ-001 自身做独立 Review（两者 `G-REVIEW: ADDRESSED_PENDING_R2`，不在本报告范围）。
- 未做草案与 AD-003 的 diff 级逐字比对（按语义单元对账），也未审 FEA-01 其余 C-02…C-12 条目。
- 未对 `doc/reviews/FEA-C01b-r1.md` 做 `check.ps1` 收录登记（`doc/00_INDEX.md` 属 DSH 单点更新面，本任务禁改）。

---

## 10. 处置建议（供 DSH，不构成裁决）

1. **先修 P0**：SC-01 验证列改写为「不含源容器整体全尺寸复制 + 页级产物受 SC-02 约束 + 不删除既有 `derived/`」，再冻结。
2. **状态重标**：SC-19 → [现行]（附 F-02 的符号与测试）；SC-03 拆「前缀白名单 [现行] / 保护 preflight [新增]」；SC-08 拆「managed 入清单 [现行] / 容量预览 [新增]」；SC-06 改 [新增] 或改验证为静态存在性核对。
3. **补两条条款**：§3.8 二进制 Gate、§3.8 数据可读与不回退（或并入 SC-37），使 §3.8 覆盖 5/5。
4. **冻结条件加一条**：AD-003 `G-REVIEW` 收口或用户裁决；并在 §4 说明 ADJ-001 `G-DELETE-CONTRACT` 仍 OPEN。
5. **[现行] 证据补齐**：14 条 [现行] 逐条补 `文件:行` 或测试用例名；无测试者登记为缺口。
6. **P2 清扫**：F-09（图例四态）、F-10（[新增]/[未实现] 判据）、F-11（unknown 限定）、F-12（flag 拟议 + `--shell=legacy`）、F-13（SC-27 落点）、F-14（SC-12 拆状态）。

—— 报告结束（`verdict: changes_requested`，P0×1 / P1×7 / P2×6）。
