---
document_id: FEA-GOV-6-c05-c06-r2
kind: independent_review
task_id: FEA-GOV-6
round: 2
scope: narrow（只核 r1 的 5×P1 + 10×P2 处置、check.ps1 与是否引入新问题）
reviewer: c01b-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams durable teammate（task-19；独立上下文；未参与 C-05/C-06 撰写）"
reviewer_independent: true
reviewed_by_implementer: false
predecessor: FEA-GOV-6-c05-c06-review（r1：changes_requested，P0×0 / P1×5 / P2×10）
reviewed_head: 1a7ca2566
reviewed_head_full: 1a7ca25665ff6e96abe013673ea5954a6b1022e1
reviewed_head_note: "复核期间 HEAD 未前进（HEAD == reviewed_head == 1a7ca2566）"
reviewed_documents:
  - doc/plan/FEA-C05_PAGE_VISIBILITY_DRAFT.md
  - doc/plan/FEA-C06_SOURCE_AUTH_DRAFT.md
reviewed_sha256:
  FEA-C05_PAGE_VISIBILITY_DRAFT.md: f22988b0bf15d2a89559c71f70684198fe64bdbc1cdd31042918925c5c6f047c
  FEA-C06_SOURCE_AUTH_DRAFT.md: f9a78f8c4580f0f397c0c55f10dd0c9fc95d4d8cd59bdd5c39a1d25a357ef944
reviewed_sha256_basis: "HEAD 的 LF blob（C-05 88 行 / blob 87900986f；C-06 88 行 / blob 046cef07f）"
baseline: "doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md §3.2/§3.3/§3.5/§3.7 · doc/contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md §5 · doc/plan/FEA-C01b_STORAGE_CONTRACT_DRAFT.md SC-01/SC-07/SC-20/SC-21/SC-22/SC-30/SC-31/SC-33 · src/infrastructure/sqlite/schema.py · src/bootstrap/core_assembly.py"
repository: G:/CODEX/New Manga
source_branch: main
verdict: changes_requested
p0_count: 0
p1_count: 1
p2_count: 7
checkps1: "PASS（3 warnings），EXIT=0，本次实跑"
captured_at: 2026-11-01T04:19:50+08:00
captured_by: c01b-reviewer
---

# 独立复核 r2（窄面）：FEA-C05 / FEA-C06 v2 处置确认

**本报告不是** 冻结动作、不释放任何实现 Task，也不构成执行授权。本轮只核 r1 的 5×P1 + 10×P2 是否处置到位、`check.ps1` 是否 PASS、以及是否引入新问题。

## 1. 结论

**verdict：`changes_requested`（P0 × 0 / **P1 × 1** / P2 × 7）。**

r1 的 5 条 P1 **已闭环 4 条**（P1-1、P1-3、P1-4、P1-5），10 条 P2 **完全闭环 4 条**（P2-1/P2-2/P2-4/P2-6/P2-8 中计 5 项，见下表）：

| # | 项 | 结果 |
|---|---|---|
| 1 | C-05 P1-1：P5 改 `r.created_at` | **✅**（并注明 schema 无 `committed_at`） |
| 2 | C-05 P1-2：`active_runs` 改 ACTIVE_STATES + P6 改「无活跃 Run」 | **✗ 未闭环**（`ACTIVE_STATES` 已正确，但 **P6 仍留在 `V` 内**，与 §4「可见性不阻塞活跃 Run」及「稳定 = V ∧ 无活跃 Run」自相矛盾；且 P6 第二析取**恒真**）→ 见 P1 |
| 3 | C-05 P2-1：P2/P3/P4 绑定同一 artifact | **✅** |
| 4 | C-05 P2-2：SQL 加 `DISTINCT` | **✅** |
| 5 | C-05 P2-3：失败表补 revision 缺失 + `unknown` | **⚠️ 部分**（已补 `unknown`；**`current_revision_id IS NULL`（P3 不满足）仍缺**）→ K-1 |
| 6 | C-05 P2-4：C-01b 引用降级 | **✅**（已改「预期引用…属后续细化」） |
| 7 | C-05 P2-5：P1 含祖先软删、SQL JOIN chapters/books | **⚠️ 部分**（SQL 已 JOIN + 过滤 `c/b.deleted_at`；**谓词 P1 文本未同步**）→ K-2 |
| 8 | C-06 P1-3：identityFacts 含 digest + volume serial + file ID | **✅** |
| 9 | C-06 P1-4：scope 改 SourceId/version/entry/rendition + 预算 | **✅**（RequestSourceRead/VerifySourceRead 已同步修改） |
| 10 | C-06 P1-5：安全约束补四项 | **✅**（+越根 reparse/SC-22、读取预算、user-source 隔离/SC-20、外部写删收敛/§3.7） |
| 11 | C-06 P2-6：补 `ListSourceRoots` | **✅** |
| 12 | C-06 P2-7：`locator`/`roots[]` 语义 + 根内校验 | **⚠️ 部分**（locator/roots 已定义；**scope→authorizedRoots 的归属校验规则未写**）→ K-3 |
| 13 | C-06 P2-8：版本措辞改 v1.1 | **✅**（「v1 → v1.1；不改 major」） |
| 14 | C-06 P2-9：PD-05/PD-06 错配注明 | **⚠️ 部分**（注已加且引 AD-003 §3.7 正确；**正文 `:72` 仍写「删除授权（PD-05/PD-06）」**）→ K-4 |
| 15 | C-06 P2-10/P2-11：冻结条件 + 「直属会话」 | **⚠️ 部分**（冻结条件已补 C-01b/wire 批准；**§2.2「直属成员」未改**）→ K-5 |

另有 2 条新 P2：C-06 §2.1「不得出现在备份包外泄面」与 AD-003 §3.3「授权元数据默认包含（备份）」措辞冲突/歧义（K-6）；§4 称 SC-07 依赖本授权面（SC-07 是旧 managed 双读，不依赖）→ K-7。

---

## 2. 15 处核对明细

### C-05

#### 1（P1-1）P5 `created_at` —— ✅

- `:35`：`P5. r.created_at <= t  -- 已落库（revision 是提交产物；见 §4）`；§4 `:59` 补注「schema 无 `committed_at` 列」✓；全仓再搜 `committed_at` 无命中 ✓。

#### 2（P1-2）`active_runs`/P6 —— ✗ 未闭环

- ✅ 已改：§4 `:60` 「`ACTIVE_STATES = {'pending','running','paused','blocked','interrupted'}`（与 `core_assembly.py:171-181` 的非终态集合一致；`prepared` 不是 Run 状态，`committed` 也不是）」。
- ✗ 残留：谓词 `:36` 仍为 `P6. active_runs(p) = ∅ ∨ 所有 run.status ∉ ACTIVE_STATES`：
  1. `active_runs(p)` 已按定义限定 `status ∈ ACTIVE_STATES`（§4），故第二析取**恒真**，P6 实际等价于 `active_runs(p) = ∅`；
  2. 这与 §4 `:60`「可见性判定**不阻塞**这些 Run（页仍可见）」及 `:61`「导出与删除预览要求 `V(p,t) ∧ 无在途 Run`」**直接冲突**——按现谓词，有活跃 Run 的页**不可见**，但 §4 说仍可见；且「稳定」谓词会退化为冗余（V 已含无活跃 Run）；
  3. 判别 SQL（`:44-55`）不含活跃 Run 过滤 → **SQL 与谓词不等价**（SQL ⊊ 谓词）。
- 结论：**P1 未闭环**。修法（与 r1 建议一致）：把 P6 从 `V` 中**删除**，另立 `S(p,t) ≡ V(p,t) ∧ active_runs(p) = ∅`（稳定性谓词）；§4「可见 ≠ 稳定」与 C-05 §6 导出/删除预览都引用 `S`。

#### 3（P2-1）量词绑定 —— ✅

- `:31-34`：P2 `∃ a ∈ artifacts(p): a.artifact_type ∈ VISIBLE_TYPES`；P3「**该 artifact** 有当前 revision」；P4 注明「P2–P4 绑定同一个 a」✓。

#### 4（P2-2）SQL `DISTINCT` —— ✅

- `:44`：`SELECT DISTINCT p.page_id` ✓。

#### 5（P2-3）失败表 —— ⚠️ 部分

- ✅ 已补 `integrity_status='unknown'` 行（不可见；记 `DATA_INTEGRITY_UNKNOWN`）。
- ✗ 仍缺 **`current_revision_id IS NULL`（P3 不满足）** 情形：现表只有「`current_revision_id` 指向的 revision 缺失（P4 不满足）」，而 schema 的 `media_artifacts.current_revision_id` 是**可空列**（`schema.py:72`），「有可见类型产物但从未有 revision」是真实状态 → K-1。

#### 6（P2-4）C-01b 引用降级 —— ✅

- `:72`：「C-01b SC-30/SC-31/SC-33 的删除语义**预期**引用本谓词（当前 SC 条文未涉可见性/内容摘要，属**后续细化**，不是既有条文）；删除预览的「内容摘要」**建议**用 `V(p,t)` 计数」✓。

#### 7（P2-5）祖先软删 —— ⚠️ 部分

- ✅ SQL：`JOIN chapters c … JOIN books b …` + `WHERE p.deleted_at IS NULL AND c.deleted_at IS NULL AND b.deleted_at IS NULL`（`:46-51`）。
- ✗ 谓词 `:30` 仍为 `P1. p.deleted_at IS NULL -- 页未被软删`，未含 `c.deleted_at`/`b.deleted_at` → **谓词 ≠ SQL**（SQL 比谓词严格）→ K-2。

### C-06

#### 8（P1-3）identityFacts —— ✅

- `:29`：`identityFacts` 必须含**内容 digest + volume serial + file ID**（AD-003 §3.2）；`size`/`mtime` 只作快速预筛、不单独构成身份 ✓。

#### 9（P1-4）grant scope —— ✅

- `:39`：`scope` 按 `SourceId / version / entry / rendition` 限定，**不是**裸 `paths[]`，附大小与解码预算，UI 不得任意 `ReadFile(path)` ✓。
- `:50-51`：`RequestSourceRead` `{registryId, generation, scope{sourceId, version, entry, rendition}, budget{maxBytes, maxDecodeBytes}}`；`VerifySourceRead` `{grantId, scope, identityFacts{digest, volumeSerial, fileId}}` ✓。

#### 10（P1-5）安全约束四项 —— ✅

- `:63-66` 新增 6–9 条：越根 reparse 拒绝（→ `SOURCE_ACCESS_DENIED`，引 C-01b SC-22）✓；读取预算（超限拒绝不截断）✓；`user-source` 不进 derived-cache grant（引 C-01b SC-20，核 SC-20 原文 `:74` 确为该语义）✓；外部写/删只收敛到 registry + 回收站桥（引 AD-003 §3.7）✓。

#### 11（P2-6）`ListSourceRoots` —— ✅

- `:49`：`ListSourceRoots` UI→Host `{}` → `{ entries: [{ registryId, locator, roots[], generation, createdAt, lastUsedAt }] }` ✓。

#### 12（P2-7）`locator`/`roots[]` 语义 —— ⚠️ 部分

- ✅ `:48`：`locator` = 用户选择的源展示名；`roots[]` = 授权根绝对路径列表，Host 校验规范化后互不包含 ✓。
- ✗ **未写 scope → `authorizedRoots` 的归属校验规则**：`RequestSourceRead` 已去掉 path 改 `scope{sourceId, version, entry, rendition}`，但「sourceId/entry 如何映射到某个授权根、Host 如何判定请求落在 roots 内」未定义 → K-3。

#### 13（P2-8）版本措辞 —— ✅

- `:56`：改为「wire v1 → 本组命令 v1.1；**不改 major**」✓。

#### 14（P2-9）PD-05/PD-06 错配 —— ⚠️ 部分

- ✅ `:74` 已加注：「ADJ-001 的 PD-05 = 事务边界、PD-06 = 失败回滚；删除**授权**在 AD-003 §3.7（`:95`）/PD-02/PD-03」✓（条款归属正确）。
- ✗ 正文 `:72` 仍写「C-04b：删除授权（PD-05/PD-06）与本授权面独立」→ 正文与注矛盾，应直接改正文 → K-4。

#### 15（P2-10/P2-11）冻结条件 + 「直属会话」 —— ⚠️ 部分

- ✅ §5 已 5 条：独立复核 / **C-01b 已冻结**（SC-21/SC-22 由本草案落地）/ `G-CONTRACT` 关闭 / **wire 版本由 DSH 批准（v1.1 minor）** / `check.ps1` PASS ✓。
- ✗ §2.2 `:42` 仍写「旧 `ImportPages` 一次性 grant 保持原语义（≤300 秒、**直属成员**、进程内）」→ 未改「直属会话（单 session 绑定）」→ K-5。

### 2.16 `check.ps1` 与数据安全 —— ✅

- **`check.ps1` 实跑**：`Governance check: PASS (3 warnings)`，EXIT=0（warning 为既有：7 个非终态 Task、`STATUS.md` 2878 B / 80%、`REBASELINE_PLAN.md` 6563 B / 80%）；运行后 `git status` 为空 ✓。
- **提交面**：`1a7ca2566` 只改 C-05（+14/−11）、C-06（+17/−8）与 r1 报告（+214）；`git diff --stat 85a8a612a..HEAD -- src apps` 为空；**未 push**（`1a7ca2566` 非 `origin/main` 祖先）✓。
- 被审字节：C-05 @ `1a7ca2566` `f22988b0…`（88 行）、C-06 `f9a78f8c…`（88 行）。

---

## 3. Findings

### P1

#### P1-1（未闭环）— P6「无活跃 Run」仍在 `V` 内，与 §4 及判别 SQL 自相矛盾

- 位置：C-05 `:36`（P6）、`:60-61`（§4）、`:44-55`（SQL）。
- 问题：
  1. P6 第二析取 `所有 run.status ∉ ACTIVE_STATES` 在 `active_runs(p)` 的定义下**恒真**；
  2. P6 实际等价 `active_runs(p)=∅`，而 §4 明说「可见性判定**不阻塞**这些 Run（页仍可见）」「稳定 = V ∧ 无在途 Run」→ 谓词与 §4 冲突；
  3. SQL 无活跃 Run 过滤 → 判别 SQL 与谓词不等价。
- 影响：冻结后「可见」与「稳定」无法区分（导出/删除预览的「有活跃 Run 警告」失去意义），且测试按谓词与 SQL 会得到不同结果集。
- 建议：删除 `V` 中的 P6；定义 `S(p,t) ≡ V(p,t) ∧ active_runs(p) = ∅`；§4/§6 的「导出/删除预览」引用 `S`，SQL 保持只表达 `V`（另给 `S` 的参考 SQL）。

### P2

#### K-1 — C-05 失败表仍缺 `current_revision_id IS NULL`（P3 不满足）

- 位置：C-05 `:63-70`。`media_artifacts.current_revision_id` 可空（`schema.py:72`）；现表只有「指向的 revision 缺失（P4）」与 `unknown`，缺「从未有 revision」。建议补一行（不可见；不记 DATA_INTEGRITY_BROKEN，记「无内容」）。

#### K-2 — C-05 谓词 P1 未含祖先软删，与 SQL 不一致

- 位置：C-05 `:30` vs `:46-51`。建议 P1 改为 `p.deleted_at IS NULL ∧ c.deleted_at IS NULL ∧ b.deleted_at IS NULL`，与 SQL 对齐。

#### K-3 — C-06 缺 scope → `authorizedRoots` 的归属校验规则

- 位置：C-06 `:39`、`:50`。`RequestSourceRead` 改为 source/version/entry/rendition 后，Host 需要把 scope 映射到某个 registry + root 并判定在授权根内；现文未写该映射（例如 sourceId 是否登记于 registry、entry 与 root 的相对关系、越根 reparse 检查发生在映射时还是 Verify 时）。建议补一段「校验顺序：registry 存在 → generation 匹配 → scope 解析到 root → 越根/预算检查 → 签发 grant」。

#### K-4 — C-06 §4 正文仍写「删除授权（PD-05/PD-06）」

- 位置：C-06 `:72`。注（`:74`）已澄清条款归属，但正文未改；建议直接改为「删除授权（AD-003 §3.7 / ADJ-001 PD-02、PD-03）与本授权面独立」，并删除注或保留为引用。

#### K-5 — C-06 §2.2 仍写「直属成员」

- 位置：C-06 `:42`。代码语义是**首个 session 绑定**（`import_source_refs.py:192-196`），建议改「直属会话（单 session 绑定）」。

#### K-6（新）— C-06 §2.1「不得出现在备份包外泄面」与 AD-003 §3.3 冲突/歧义

- 位置：C-06 `:28`；AD-003 §3.3 `:65`：「应用内数据（…、**源引用与授权元数据**、恢复所需索引）**默认包含**」（在备份中）。
- 问题：若 C-06 意为「授权元数据不得进入备份」，则与 AD-003 冲突；若意为「备份中需加密/不得外泄」，需写明。
- 建议：改为「Host 私有存储；随备份时按 AD-003 §3.3 纳入（源引用与授权元数据默认包含），备份包内加密；不得在备份包之外泄露」。

#### K-7（新）— C-06 §4 称 SC-07 依赖本授权面，不准确

- 位置：C-06 `:70`。C-01b SC-07（`:45`）是「旧 Managed Copy 继续按既有读取路径工作，不自动迁移/删除」，不经过源读取授权面；SC-01（`:34`）的「新导入不复制」才依赖长期读取授权。建议改为「SC-01（不复制）依赖长期读取授权；SC-07（旧 managed 双读）不依赖」。

---

## 4. 独立性声明

- 我以 `c01b-reviewer`（Agent Teams **durable teammate**）身份出具 r2，`reviewer_kind: subagent`，独立上下文；r1 亦由我出具（如实披露）。
- **未参与** C-05/C-06 撰写（作者 = DSH）、未参与 AD-003 / ADJ-001 / C-01b 撰写，未参与 `src/**`、`apps/**` 任何实现。
- 本轮**只读**：唯一写入为新建本报告；未修改任何文件；未 `git add`/`commit`/`push`；未触碰真实数据根。唯一执行的命令为只读 `check.ps1`（运行后 `git status` 为空）与只读取证。
- P1 的判定**直接对照** `core_assembly.py:171-181`、C-05 §4 与 SQL 原文（未引用 r1 结论作为依据）；K-6 的依据为 AD-003 §3.3 `:65` 原文。
- **工作树状态记录**：报告落盘前 `git status --porcelain` 为空；`reviewed_head == HEAD == 1a7ca2566`；C-05 blob `87900986f`、C-06 blob `046cef07f`。

---

## 5. NOT_RUN

- 未运行 `pytest` / `dotnet test` / 任何构建；未执行 SQL（谓词/SQL 等价性为静态审阅）。
- 未执行任何冻结或代码改动（两份均为 DRAFT）。
- 未审计 C-01b 其余 SC 条款（只核 SC-01/SC-07/SC-20/SC-21/SC-22/SC-30/SC-31/SC-33 与两份草案的引用关系）。
- 未核 `pipeline_run_targets` 的路由细节（只核 `core_assembly.py:171-181` 的 ACTIVE_STATES 集合）。
- 未验证 `source-read` grant 与 `handle_resolver` 的集成可行性（无实现，属计划态）。
- 未核远端历史细节（仅核本地 main 未 push）。

—— 报告结束（`verdict: changes_requested`，P0×0 / P1×1 / P2×7；15 处核实：9 全到位 + 6 部分）。
