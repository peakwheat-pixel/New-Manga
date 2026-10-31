---
document_id: FEA-GOV-6-c05-c06-review
kind: independent_review
task_id: FEA-GOV-6
reviewer: c01b-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams durable teammate task-19（独立上下文；未参与 C-05/C-06 撰写，未参与 AD-003/ADJ-001/C-01b 撰写）"
reviewer_independent: true
reviewed_by_implementer: false
reviewed_head: 85a8a612a
reviewed_head_full: 85a8a612a3dcafcb906ae6cab7fadcdf945471da
reviewed_head_note: "task-19 卡原 pin 4d7bcd101；C-05/C-06 两文件 blob 在 4d7bcd101 与 85a8a612a 完全相同（C-05 48dbb5ebc、C-06 2b59fdb0d），故按最新 HEAD 85a8a612a 复核，结论对两个 head 均有效"
reviewed_documents:
  - doc/plan/FEA-C05_PAGE_VISIBILITY_DRAFT.md
  - doc/plan/FEA-C06_SOURCE_AUTH_DRAFT.md
reviewed_sha256:
  FEA-C05_PAGE_VISIBILITY_DRAFT.md: 8d24b4f464b888561bbae80bceb994cfdc481202a65172ffb243bbb21c117673
  FEA-C06_SOURCE_AUTH_DRAFT.md: 9d8b395ecfbad6649211240748364bbd0e141ec7493c5dbabfe633fbc501be89
reviewed_sha256_basis: "HEAD 的 LF blob（C-05 85 行 / blob 48dbb5ebc；C-06 79 行 / blob 2b59fdb0d）"
baseline: "doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md §3.2/§3.5/§3.7 · doc/contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md §5（PD-01…PD-10）· doc/plan/FEA-C01b_STORAGE_CONTRACT_DRAFT.md SC-01/SC-07/SC-21/SC-22/SC-30/SC-31/SC-33 · src/infrastructure/sqlite/schema.py · src/bootstrap/core_assembly.py · src/infrastructure/resource_channel/import_source_refs.py"
repository: G:/CODEX/New Manga
source_branch: main
verdict: changes_requested
p0_count: 0
p1_count: 5
p2_count: 10
checkps1: "PASS（3 warnings），EXIT=0，本次实跑"
captured_at: 2026-11-01T04:17:29+08:00
captured_by: c01b-reviewer
---

# 独立复核：FEA-C05 页可见性谓词 / FEA-C06 授权面（草案）

**本报告不是** 冻结动作、不释放任何实现 Task，也不构成执行授权。本轮把 C-05 的谓词/SQL/失败语义与 C-06 的 registry/grant/命令面，逐项对照 `schema.py`、`core_assembly.py`、`import_source_refs.py`、AD-003 §3.2/§3.5/§3.7、ADJ-001 PD 语义与 C-01b 的 SC 条款。

## 1. 结论

**verdict：`changes_requested`（P0 × 0 / **P1 × 5** / P2 × 10）。**

两份草案的**方向都对**（C-05 补上「单一可见性谓词」这个真实缺口；C-06 把 AD-003 §3.5 的独立授权面落成 registry + grant + 4 命令），且**引用的现状事实多数准确**：

- C-05 的数据模型（`pages`/`media_artifacts`/`artifact_revisions` 关键列）与 `schema.py:54-106` 一致；`VISIBLE_TYPES` 与 `media_artifacts.artifact_type` 的 CHECK 集合**完全吻合**（6 个可见类型 + `detection_overlay`/`mask`/`debug_ocr`/`debug_detection` 排除）✓。
- C-06 的行号引用准确：`import_source_refs.py:153`（`expires_at <= now or expires_at > now + 300` → ≤300 秒）、`:108`（进程内 registry `self._grants`）、`:192-203`（session 绑定 + 写入）✓；`SourceAccessRegistry` 在 `src/` **0 命中** ✓；grant「三件套 = identity / size / digest」与 `_facts`（`volume_serial`/`file_index`/`size`/`sha256`，`:345-350`）一致 ✓。

但有 **5 条 P1** 属于「谓词/授权面会与代码或冻结契约冲突」的实质问题：

| # | P1 | 一句话 |
|---|---|---|
| P1-1（C-05） | P5 引用**不存在的列** `r.committed_at` | `schema.py`/`src` 全仓无 `committed_at`；SQL 与 §4 都用 `created_at` → 谓词不可实现 |
| P1-2（C-05） | `active_runs` 状态集合与实现不符、P6 恒真且与 §4 矛盾 | 代码非终态集合是 `(pending, running, paused, blocked, interrupted)`（`core_assembly.py:171-181`）；`'prepared'` 是 export 的 `hooks_prepared`、`'committed'` 不是 Run 状态 → 漏判 paused/blocked/interrupted |
| P1-3（C-06） | `identityFacts` 与 AD-003 §3.2 不一致 | AD-003 要求源身份含**内容 digest + volume serial + file ID**，且「不得仅凭路径、mtime 或 size 断言同一文件」；草案只列 `size, mtime, fileId?` |
| P1-4（C-06） | grant 读取面用裸 `paths[]` | AD-003 §3.5 要求「读取面按 **SourceId/version/entry/rendition** 限定，带大小与解码预算；UI 不得获得任意 `ReadFile(path)`」 |
| P1-5（C-06） | 安全约束缺 AD-003 §3.5 / C-01b SC-22 的四项硬约束 | 越根符号链接/junction 不跟随（reparse 拒绝）、读取预算、`user-source` 不得进 derived-cache grant、外部写/删只收敛到 registry + 回收站桥 |

10 条 P2 为谓词量词/SQL 等价性/失败语义补全、C-01b 引用准确性、祖先软删、C-06 命令面补全与条款归因。

| C-05 审查项 | 判定 |
|---|---|
| 1. 数据模型准确性 | **通过**（三表关键列与 `schema.py` 一致；`VISIBLE_TYPES` 与 CHECK 完全吻合） |
| 2. 谓词正确性（P1–P6） | **不通过**（P1-1 不存在的列；P1-2 P6 恒真/矛盾；P2-1 量词不明） |
| 3. 判别 SQL | **部分**（可执行；但 `committed_at` 与谓词不一致、无 `DISTINCT`/`EXISTS` 会重复返回） |
| 4. 在途写判定 | **不通过**（P1-2：`active_runs` 状态集合与代码不符；「可见 ≠ 稳定」的区分方向正确但落点错） |
| 5. 失败语义 | **部分**（缺 `current_revision_id IS NULL` 与 `integrity_status='unknown'` 两类） |
| 6. 与 C-01b 接口 | **部分**（SC-30/31/33 条文并不涉及可见性；「内容摘要用 V(p,t) 计数」是新增语义） |

| C-06 审查项 | 判定 |
|---|---|
| 1. 与 AD-003/ADJ-001 一致 | **不通过**（P1-3 identity、P1-4 读取面；P2-9 把 PD-05/PD-06 当「删除授权」引用） |
| 2. 与现有实现（ImportPages 一次性 grant） | **通过**（≤300 秒/进程内 registry/ImportPages 范围均与代码一致；「直属成员」措辞见 P2-11） |
| 3. 安全约束 5 条 | **不通过**（缺 AD-003 §3.5/SC-22 的四项硬约束 → P1-5） |
| 4. 命令形状 4 条 | **部分**（缺 list；`locator/roots` 语义未定义；`paths[]` 见 P1-4） |
| 5. 冻结条件 | **部分**（缺「C-01b 已冻结」与 wire 版本批准 → P2-10） |

---

## 2. C-05 findings

### P1

#### P1-1 — P5 引用不存在的列 `r.committed_at`

- 位置：C-05 `:35`（`P5. r.committed_at <= t`）、`:57`（§4 却写「`r.created_at` 是 revision 落库时间」）、`:51`（SQL 用 `r.created_at`）。
- 证据：`schema.py:81-105` 的 `artifact_revisions` 只有 `created_at`（`:102`），无 `committed_at`；全仓 `src/**` 与 `schema.py` 搜 `committed_at` **0 命中**。
- 影响：谓词文本引用了不存在的列，实现者只能按 SQL/§4 猜 `created_at`；冻结后若按谓词建测试会失败。
- 建议：P5 改为 `r.created_at <= t`（并注明「revision 落库即提交」），或先做 schema 变更（不建议，属新增列）。

#### P1-2 — `active_runs(p)` 的状态集合与实现不符；P6 恒真且与 §4 自相矛盾

- 位置：C-05 `:36`（P6）、`:58`（§4「`active_runs(p)` = … `run.status ∈ {'running','prepared'}`」「可见性判定**不阻塞**它们」）。
- 证据：
  - 代码的唯一「非终态 Run」判定是 `src/bootstrap/core_assembly.py:171-181`：`SELECT 1 FROM pipeline_runs WHERE status IN ('pending', 'running', 'paused', 'blocked', 'interrupted')` —— 集合里**没有 `'prepared'`/`'committed'`**；
  - `'prepared'` 仅出现在 export 的 `hooks_prepared` 字段（`src/application/export/service.py:183/246`），不是 Run 状态；
  - `pipeline_runs.status` 无 CHECK 枚举（`schema.py:299` 仅 `TEXT NOT NULL`），故「committed」不是任何已登记状态。
- 影响：
  1. 按现定义，**paused/blocked/interrupted** 的在途 Run 不会进入 `active_runs` → §4 的「导出/删除预览须标注有在途任务」会漏报，属于数据安全相关缺口；
  2. P6 写成 `∀ run ∈ active_runs(p): run.status ∉ {'committed'}`，而 `active_runs` 已被限定为 running/prepared ⇒ **P6 恒真**（无判别力）；同时 §4 明说「可见性判定不阻塞在途 Run」，把 P6 放进 `V` 与 §4 直接矛盾。
- 建议：
  1. `active_runs(p)` 改为「该页为 `pipeline_run_targets` 目标（`target_type='page'`）且 `pipeline_runs.status ∈ {pending, running, paused, blocked, interrupted}` 的 Run」——这才是「尚未产出 revision 的在途 Run」也能检出的口径（现定义依赖 `artifact_revisions.pipeline_run_id/step_run_id`，只看得见已写过 revision 的 Run）；
  2. 从 `V(p,t)` 中**删除 P6**，改为独立的稳定性谓词：`S(p,t) ≡ V(p,t) ∧ ¬∃run ∈ active_runs(p)`；§4 的「可见 ≠ 稳定」用 `S` 表达，导出/删除预览引用 `S`。

### P2

#### P2-1 — P2/P3/P4 的量词不严谨（是否同一 `a`）

- 位置：C-05 `:31-34`。P2 是 `∃ a ∈ artifacts(p)`，而 P3/P4 写 `a.current_revision_id` / `revision(a.current_revision_id)`——是否要求同一个 `a` 未写明。SQL 的内连接语义是「同一个 a 同时满足」，建议谓词显式写成 `∃ a ( a.artifact_type ∈ VISIBLE_TYPES ∧ a.current_revision_id ≠ NULL ∧ r=revision(a.current_revision_id) ∧ r.integrity_status='valid' ∧ r.created_at ≤ t )`。

#### P2-2 — 判别 SQL 缺少 `DISTINCT`/`EXISTS`，会重复返回页

- 位置：C-05 `:43-53`。`JOIN media_artifacts a … JOIN artifact_revisions r` 对同一页的多个合格 artifact 会产出多行，与「返回页集合」不等价。建议改为 `WHERE EXISTS (SELECT 1 FROM media_artifacts a JOIN artifact_revisions r …)` 或 `SELECT DISTINCT p.page_id`。

#### P2-3 — 失败语义缺两类情形

- 位置：C-05 `:63-68`。缺：① `current_revision_id IS NULL`（P3 不满足，即「有 type 但无 revision」）；② `integrity_status='unknown'`（`schema.py:92` 的 CHECK 允许 `unknown`，现表只列 missing/corrupted）。建议补两行（不可见；UI 不显示路径）。

#### P2-4 — §6 与 C-01b 的引用不实，「内容摘要用 V(p,t) 计数」是新增语义

- 位置：C-05 `:72`。
- 证据：C-01b `:94-97` 的 SC-30（应用内删除不触点原文件）、SC-31（原文件删除是独立流程）、SC-33（共享源不阻断）条文**均不涉及可见性或内容摘要**；ADJ-001 PD-01 的影响清单口径也没有「按页可见性过滤」的要求。
- 建议：§6 改为「本谓词预期被后续 SC 条款（导出/删除预览）引用」并注明「按可见页计数」属 C-05 新增细化、需在 C-01b/ADJ-001 侧确认（已列入 §7 冻结条件②，但 §6 的措辞应同步降级）。

#### P2-5 — P1 只看 `pages.deleted_at`，忽略祖先软删

- 位置：C-05 `:30`。`books.deleted_at`（`schema.py:40`）与 `chapters.deleted_at`（`:50`）存在；若回收站只标 book/chapter 的 `deleted_at`，其下 page 的 `deleted_at` 仍为 NULL，现谓词会把**已进回收站书籍的页**判为可见。建议 `V(p,t)` 加上「`p.deleted_at IS NULL ∧ chapter.deleted_at IS NULL ∧ book.deleted_at IS NULL`」（或明确只用于「书内页可见性」并注明调用方需先过滤 book）。

---

## 3. C-06 findings

### P1

#### P1-3 — `identityFacts{size, mtime, fileId?}` 与 AD-003 §3.2 的源身份要求不一致

- 位置：C-06 `:29`（registry 条目字段）。
- 证据：AD-003 §3.2 `:59`：「新导入的源身份包含：**内容 digest**、授权、来源 lineage、**Windows volume serial + file ID**（同机身份）；**不得仅凭路径、mtime 或 size** 断言同一文件」；现有一次性 grant 的 facts 也已是 `volume_serial`/`file_index`/`size`/`sha256`（`import_source_refs.py:345-350`）。
- 影响：按现草案登记，`identityFacts` 缺内容 digest 与 volume serial，且把 `mtime`、`size` 列为身份要素——恰好是 AD-003 明说不能单独依赖的两项；源被替换后可能被误判为同一文件（fail-open 风险）。
- 建议：`identityFacts` 改为 `{ volumeSerial, fileId, size, sha256, mtime? }`（`sha256` 与 `volumeSerial`/`fileId` 为必需，`mtime` 仅作辅助），并注明「不得仅凭 size/mtime 判定同一文件（AD-003 §3.2）」。

#### P1-4 — grant 的读取面用裸 `paths[]`，与 AD-003 §3.5 的「按 SourceId/version/entry/rendition 限定」冲突

- 位置：C-06 `:39`（grant `scope{ paths[] }`）、`:50`（`RequestSourceRead` 入参 `paths[]`）、`:51`（`VerifySourceRead` 入参 `path`）。
- 证据：AD-003 §3.5 `:84`：「读取面按 **SourceId/version/entry/rendition** 限定，带大小与解码预算；**UI 不得获得任意 `ReadFile(path)`**」。
- 影响：以裸路径为授权/校验单位，等于把「任意路径读取」重新引入授权面；`VerifySourceRead` 用 `path` 校验也无法表达「ZIP/CBZ 内部 entry」与「rendition」维度。
- 建议：`source-read` grant 的 scope 改为 `{ sourceId, sourceVersion, entries[] | entrySet, rendition }`（路径只作为 Host 内部解析产物，不进入 Core 可见的授权字段）；`RequestSourceRead` 用 source/version/entry 申请，`VerifySourceRead` 用 `{ grantId, sourceId, sourceVersion, entry, identity }`。

#### P1-5 — 安全约束缺 AD-003 §3.5 / C-01b SC-22 的四项硬约束

- 位置：C-06 `:57-61`（5 条约束）。
- 证据：AD-003 §3.5 `:81-85` + C-01b SC-22（`:76`）：
  1. 「授权根为显式边界：**不跟随越过根目录的符号链接/junction**」；
  2. 「读取面…**带大小与解码预算**」；
  3. 「`user-source` **不得进入 derived-cache grant**」（两条通道隔离）；
  4. 「旧『清理/删除只接触受管根内文件』结构前提退役：外部路径的**写/删权限只收敛到 `SourceAccessRegistry` + Windows 回收站桥**」。
- 影响：现 5 条只覆盖「一次性≠长期 / fail-closed / 无路径泄漏 / UI 不绕过 / 撤销即时」，**缺越根 reparse、读取预算与写/删边界**——这三项正是引用源的攻击面核心；且 C-06 未引用 C-01b SC-22。
- 建议：§3 扩为 8–9 条，补充上述四项（写明「registry 只管读；写/删走回收站桥；清理/重试路径继续只接受受管相对路径」），并在 §4 增引 SC-22。

### P2

#### P2-6 — 命令面缺「列出已授权根」

- 位置：C-06 `:46-52`（4 命令）。`RegisterSourceRoot` 返回 `registryId`，但重启后 UI 无法列出已有授权根（也就无法展示/撤销）；建议补 `ListSourceRoots`（UI→Host，`{} → { roots: [{ registryId, locator, authorizedRoots[], generation, lastUsedAt }] }`）或注明由 Host 设置页另开命令。

#### P2-7 — `RegisterSourceRoot` 的 `locator`/`roots[]` 语义未定义；`RequestSourceRead` 的根内校验规则未写

- 位置：C-06 `:48`、`:50`。`locator` 是不透明 id 还是路径？`roots[]` 是授权根边界（目录）还是具体文件？Host 如何判定 `RequestSourceRead` 的请求属于 `authorizedRoots`（前缀匹配、`Path.is_relative_to`、还是 reparse 安全解析）？建议逐项写明，并注明「UI 只传用户选择结果（picker token），不自行构造路径」。

#### P2-8 — 版本语义自相矛盾；「wire v1」出处未注明

- 位置：C-06 `:53`（「新增命令按 **minor** 递增（wire v1 → v2）」）。若 wire 的主版本是 1，则 `v1 → v2` 是 **major** 升级而非 minor；若指 minor，应写 `v1.0 → v1.1`。另：`dto.py` 只注「M2-RC1」，`resource_channel` 内未见显式 `wire v1` 版本常量，建议注明出处或改引 M2-C1 的 `{major:2, minor:10}` 口径。

#### P2-9 — §4 把 ADJ-001 PD-05/PD-06 当作「删除授权」引用，条款错配

- 位置：C-06 `:6`（依据行）、`:67`（「C-04b：删除授权（PD-05/PD-06）」）。
- 证据：ADJ-001 PD-05（`:65`）= **事务边界**（同一 `BEGIN IMMEDIATE` 内删除、清理清单持久化）；PD-06（`:66`）= **失败回滚**；「删除授权」在 AD-003 §3.7（`:95`）与 ADJ-001 PD-02/PD-03（专门确认/预览）。
- 建议：改引 AD-003 §3.7 + ADJ-001 PD-02/PD-03；「删除不撤销源读取授权、反之亦然」如保留，标注为 C-06 新增约束并列入 §5 待确认项。

#### P2-10 — §5 冻结条件缺「C-01b 已冻结」与 wire 版本批准

- 位置：C-06 `:71-73`。§4 说 SC-21/SC-22 由本草案落地，则 C-01b 应先冻结；另按 ADJ-001 §6.1「逐命令 minor 冻结须 DSH 批准」的同类要求，wire 版本升级应由 DSH 批准。建议补两条。

#### P2-11 — 「直属成员」措辞与代码语义不完全对应

- 位置：C-06 `:17`（「≤300 秒、直属成员、进程内 registry」）。代码实际是**首个 session 绑定**：`self._session_id` 为 None 时记录，否则不同 session 一律 `E_SCOPE_DENIED`（`import_source_refs.py:192-196`）。建议写「直属会话（单 session 绑定）」，避免被理解成 ACL 成员概念。

---

## 4. 共同项（数据安全 / 治理）

- 两份草案仅由 `728f76439` 一次提交引入（C-05 +85 行、C-06 +79 行，均为新增文档），其后至 HEAD 无 `src/**`/`apps/**` 改动 ✓。
- **未 push**：`85a8a612a` 非 `origin/main` 祖先 ✓。
- **`check.ps1` 实跑**：`Governance check: PASS (3 warnings)`，EXIT=0（warning 为既有：7 个非终态 Task、`STATUS.md` 2878 B / 80%、`REBASELINE_PLAN.md` 6563 B / 80%）；运行后 `git status` 为空 ✓。
- 被审字节：C-05 @ `85a8a612a` `8d24b4f4…`（85 行）、C-06 `9d8b395e…`（79 行）；两文件在 task-19 原 pin `4d7bcd101` 与 HEAD 相同 ✓。

---

## 5. 独立性声明

- 我以 `c01b-reviewer`（Agent Teams **durable teammate**，`task-19`）身份出具本报告，`reviewer_kind: subagent`，独立上下文。
- **未参与** C-05/C-06 撰写（作者 = DSH）、未参与 AD-003 / ADJ-001 / C-01b 撰写，未参与 `src/**`、`apps/**` 任何实现。
- 本轮**只读**：唯一写入为新建本报告；未修改任何文件；未 `git add`/`commit`/`push`；未触碰真实数据根。唯一执行的命令为只读 `check.ps1`（运行后 `git status` 为空）与只读取证（`git log`/`git cat-file`/`git hash-object` + 代码/文档阅读）。
- **利益披露**：我出具过 C-01b r1–r5、FEA-GOV-1~5 各报告；本轮对 `schema.py`、`core_assembly.py`、`import_source_refs.py`、AD-003、ADJ-001、C-01b 均**直接读取原文**，未引用既有报告结论。
- **工作树状态记录**：报告落盘前 `git status --porcelain` 为空；`reviewed_head == HEAD == 85a8a612a`；C-05 blob `48dbb5ebc`、C-06 blob `2b59fdb0d`。

---

## 6. NOT_RUN

- 未运行 `pytest` / `dotnet test` / 任何构建；未执行 SQL（判别 SQL 的等价性为静态审阅，未在真实库上跑）。
- 未执行任何冻结或代码改动（两份均为 DRAFT）。
- 未审计 C-01b 的其他 SC 条款（只核 SC-01/SC-07/SC-21/SC-22/SC-30/SC-31/SC-33 与两份草案的引用关系）。
- 未核 `pipeline_run_targets` 的完整使用面与 Run 终态集合的最终权威定义（只依据 `core_assembly.py:171-181` 的现有实现）。
- 未验证 `source-read` grant 与 `handle_resolver` 的集成可行性（无实现，属计划态）。
- 未核远端历史细节（仅核本地 main 未 push）。

—— 报告结束（`verdict: changes_requested`，P0×0 / P1×5 / P2×10）。
