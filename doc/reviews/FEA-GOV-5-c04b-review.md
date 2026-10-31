---
document_id: FEA-GOV-5-c04b-review
kind: independent_review
task_id: FEA-GOV-5
reviewer: c01b-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams durable teammate task-18（独立上下文；未参与 C-04b 草案撰写，未参与 ADJ-001 / M2-C1 / C-01b 撰写）"
reviewer_independent: true
reviewed_by_implementer: false
reviewed_head: 59342d6bf
reviewed_head_full: 59342d6bfb4e03edaefe9c33d5a8d6432b0df9fc
reviewed_head_note: "复核期间 HEAD 未前进（HEAD == reviewed_head == 59342d6bf）"
reviewed_document: doc/plan/FEA-C04b_DELETE_PROTOCOL_DRAFT.md
reviewed_sha256: 2105800cf76b375d9f09dd38315fce1ce65b437db984d7b0cfac33e720e6bbdf
reviewed_sha256_basis: "HEAD 的 LF blob（78 行，blob 1c8efaa44）；与 reviewed_head 相同"
baseline: "doc/contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md §5（PD-01–PD-10）/§6.1–§6.3 · doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md §5.11.1–§5.11.5 · doc/plan/FEA-C01b_STORAGE_CONTRACT_DRAFT.md SC-30/31/33"
repository: G:/CODEX/New Manga
source_branch: main
verdict: changes_requested
p0_count: 0
p1_count: 5
p2_count: 4
checkps1: "PASS（3 warnings），EXIT=0，本次实跑"
captured_at: 2026-11-01T04:06:24+08:00
captured_by: c01b-reviewer
---

# 独立复核：FEA-C04b 删除协议字段与码表（草案）

**本报告不是** 冻结动作、不构成对 ADJ-001 / M2-C1 的修改，也不构成执行授权。本轮把 C-04b 的三个新增（`PreviewPermanentDeleteBooks` / `inventory_digest` / 两个错误码）逐项对照 ADJ-001 §5–§6 与 M2-C1 §5.11，核对现状表、码表、closed shape、安全投影、版本与冻结条件。

## 1. 结论

**verdict：`changes_requested`（P0 × 0 / **P1 × 5** / P2 × 4）。**

草案的**方向与 ADJ-001 §6 提案一致**：新增只读预览命令名与出参骨架（清单 + `inventoryDigest` + `computedAt`）✓；确认命令「追加 `inventory_digest` + 保留 `confirm_permanent_delete: true` 语义 + fail-closed 不降级软删」✓；两个新错误码的名称/category/retryable 与 ADJ-001 §6.3 逐字一致 ✓；版本按 minor 递增（2.10 → 2.11）并声明旧 Core 返回 `PROTOCOL_VERSION_UNSUPPORTED` ✓；与 C-01b SC-30/31/33 的引用与「C-01b 先、C-04b 后」的冻结顺序 ✓。

但一旦与 M2-C1 §5.11 的**现行冻结文本**对齐，有 5 条 P1 属于**事实/契约不符**（不是措辞问题）：

| # | P1 | 一句话 |
|---|---|---|
| P1-1 | `bookIds` **上限 200** | M2-C1 §5.11.1 `:691-692` 明确 `BookId[1..20]`、§5.11.2 `:733`「1..20 上限」，且 §5.11.3 有 `BOOK_DELETE_BATCH_LIMIT_EXCEEDED` 按 20 判定 —— 200 与冻结契约冲突 10 倍 |
| P1-2 | 现状错误表与冻结码表**不完整** | §5.11.3 实有 12 行码（含 `BOOK_DELETE_CLEANUP_PENDING`/`BOOK_DELETE_BATCH_CLEANUP_PENDING`/`BOOK_DELETE_BATCH_PREFLIGHT_FAILED`/`BOOK_DELETE_BATCH_LIMIT_EXCEEDED`/`BOOK_DELETE_BATCH_WHOLE_LIBRARY`/`UNKNOWN`/`CORE_UNAVAILABLE`），C-04b 只列 6 码 → PD-07 重试与 PD-09 逐项状态**没有码** |
| P1-3 | 预览出参**漏 PD-01 三项** | 缺「人工修改区域数」「活动草稿页数」「将被删除 managed/派生文件数**与字节量**」；而 PD-02 要求确认文案明示「人工修改…的具体内容与数量」→ 无法满足 |
| P1-4 | 未区分**单条/批量**命令形状 | PD-02 明写「按命令形状分别绑定，不得混用」：单条 `{book_id, confirm_permanent_delete:true}`、批量 `{book_ids, confirmed_book_ids, confirm_count, confirm_permanent_delete:true}`（§5.11.1 `:685-695`）；C-04b 只写「现有删除命令」 |
| P1-5 | §5.11.5 两个 `ErrorView` 的 code 联合**未同步扩展** | 新码不在 `PermanentlyDeleteBook(s)ErrorView` 的允许集合内（`:779-799`），且 §5.11.5 明文「错误码必须在 §5.11.3 集合内」→ host 无法投影新码 |

4 条 P2 为语义补全与形式问题（`BOOK_DELETE_CONFLICT` 漏 PD-08 共享引用条件、category/retryable 列应替代表述「HTTP 语义」、冻结条件缺 C-01b 前置与 DSH 批准、`inventoryDigest` 格式未定义）。

| 审查项 | 判定 |
|---|---|
| 1. 与 ADJ-001 一致性 | **不通过** —— 三个新增方向正确；但 PD-01 披露项缺 3 项（P1-3）、命令形状未按 PD-02 分别绑定（P1-4）、`BOOK_DELETE_CONFLICT` 漏 PD-08 条件（P2-1） |
| 2. 与 M2-C1 兼容性 | **不通过** —— 上限 200≠20（P1-1）、码表不完整（P1-2）、投影联合未扩（P1-5）；`confirm_permanent_delete` 语义保持 ✓、两个新码 retryable 与 ADJ-001 §6.3 一致 ✓ |
| 3. 协议版本 | **通过** —— `2.10 → 2.11` minor 递增合理；旧 Core `PROTOCOL_VERSION_UNSUPPORTED` 与 ADJ-001 §6.2、§5.11.3 `:757` 一致 |
| 4. 安全投影 | **部分** —— 「只返回 bookId、无路径/明文」原则正确 ✓；但 §5.11.5 的 code 联合与 batch item 白名单未更新（P1-5）、`category` 映射未给出（P2-2） |
| 5. closed shape | **部分** —— digest 缺失/格式错 → `INVALID_REQUEST`、不匹配 → `STALE_PREVIEW`、零副作用 ✓ 明确；但上限错（P1-1）、单条/批量形状未列（P1-4）、digest 格式未定义（P2-4） |
| 6. 与 C-01b 接口 | **通过** —— SC-30/SC-31/SC-33 在 C-01b `:94-97` 存在且 C-04b 引用关系正确；「C-01b 先（语义）、C-04b 后（协议）」顺序合理；建议 §5 增列前置（P2-3） |
| 7. 数据安全 | **通过** —— 仅文档；无用户数据；未 push；`check.ps1` PASS(3 warnings) EXIT=0 |

---

## 2. 逐项核对

### 2.1 与 ADJ-001 §6.1 新增能力（`PreviewPermanentDeleteBooks` / `inventory_digest`）

- §6.1 表格三行：①「影响清单预览」新增**只读**命令（如 `PreviewPermanentDeleteBooks`），closed shape 入参（同目标集合），返回清单 + `inventoryDigest` + `computedAt`，零副作用/不缓存/不预解锁；②「确认绑定」现有删除命令增加 `inventory_digest` 并纳入 closed shape 校验（`INVALID_REQUEST` 或新 `BOOK_DELETE_STALE_PREVIEW`）；③「分阶段状态」`confirm_permanent_delete: true` 语义保持、新字段为追加。
- C-04b 对应：§2.1 命令名 ✓、出参三件套 ✓、只读语义 ✓；§2.2 追加字段 + closed shape 校验 + 不匹配 `STALE_PREVIEW` + `confirm_permanent_delete` 不变 ✓ → **方向逐项对上**。
- 缺口：入参「同目标集合」在 §6.1 中指的是**与删除命令一致的目标集合**（单条 `book_id` / 批量 `book_ids`），C-04b 只给 `{ bookIds: string[] }` 一种形状，未说明单条删除是否也有对应预览形状或统一走数组（P1-4）。

### 2.2 与 ADJ-001 §5 PD-01/PD-02/PD-08 的语义覆盖

- PD-01（`:58`）要求逐项计算并**不得写入任何状态**：人工修改区域数、锁定区域数（有效锁定并集）、current Revision、pinned Revision **数与列表**、受保护 artifact 数、活动草稿页数、非终态 Run/Task（同时作为 `BOOK_BUSY` 阻断项）、**将被删除的 managed/派生文件数与字节量**、其他项目对该源的引用数。
  C-04b `DeletePreviewItem` 覆盖：`lockCount` ✓、`currentRevisionId` ✓、`pinnedRevisionIds[]` ✓、`activeRunIds[]` ✓、`artifacts` ✓、`sharedFileRefs[].otherProjectCount` ✓；
  **缺**：人工修改区域数、活动草稿页数、managed/派生文件数**与字节量**（`contentSummary.chapters/pages/artifacts` 不映射字节量）→ P1-3。
- PD-02（`:59-62`）：「按命令形状分别绑定，不得混用」——单条命令**禁止**引入 `book_ids`/`confirmed_book_ids`/`confirm_count`；批量沿用 `{book_ids, confirmed_book_ids, confirm_count}` 有序绑定 + `inventory_digest`；确认文案必须明示「将删除人工修改/锁定/固定版本」**的具体内容与数量**。C-04b 未分形状、未提有序绑定与 `confirm_count` → P1-4；且「人工修改」数量缺字段（P1-3 联动）。
- PD-08（`:68`）：**可安全拆分**的共享引用不是阻断条件；「无法安全拆分 / 关系图、归属不一致 / 存在未列明目标外引用」时 fail-closed（M2-C1 `:752` 对应 `BOOK_DELETE_CONFLICT`）。C-04b §2.3 把 `BOOK_DELETE_CONFLICT` 的触发条件写成「保护阻止（Lock/current/pinned/active Run）」，漏共享引用/归属类冲突 → P2-1。

### 2.3 与 M2-C1 §5.11 的兼容性

- **现行错误表（P1-2）**：§5.11.3（`:742-758`）实际包含：`INVALID_REQUEST`、`DUPLICATE_BOOK_ID`、`BOOK_DELETE_BATCH_LIMIT_EXCEEDED`、`BOOK_DELETE_BATCH_WHOLE_LIBRARY`、`BOOK_DELETE_BATCH_PREFLIGHT_FAILED`（item code：`BOOK_NOT_FOUND`/`BOOK_BUSY`/`BOOK_DELETE_CONFLICT`）、`BOOK_DELETE_FAILED`、`BOOK_DELETE_CLEANUP_PENDING`、`BOOK_DELETE_BATCH_CLEANUP_PENDING`、`PROTOCOL_VERSION_UNSUPPORTED`、`UNKNOWN`、`CORE_UNAVAILABLE`；§5.11.5 又给出两个 `ErrorView` 的 code 联合（`:779-799`）。
  C-04b §1 现状表只列 5 个码（`INVALID_REQUEST`/`DUPLICATE_BOOK_ID`/`BOOK_BUSY`/`BOOK_DELETE_CONFLICT`/`BOOK_DELETE_FAILED`），其中 `BOOK_BUSY`/`BOOK_DELETE_CONFLICT` 在批量命令里是 **item code** 而非顶层码；§2.3 冻结码表也只 6 行（2 新 + 4 沿用 + `BOOK_NOT_FOUND` = 6），缺 6 类码（批量 3 + cleanup 2 + `UNKNOWN`/`CORE_UNAVAILABLE`）→ 若照此冻结，`cleanup_pending` 重试（PD-07）与逐项状态（PD-09）无码可用。
- **上限（P1-1）**：§5.11.1 `book_ids: BookId[1..20]`、`confirmed_book_ids: BookId[1..20]`（`:691-692`）；`:723`「批量 `book_ids` 必须有 1..20 项、ID 唯一并保持调用方顺序」；§5.11.2 `:733`「1..20 上限…超过上限立即拒绝」；§5.11.3 `:748` `BOOK_DELETE_BATCH_LIMIT_EXCEEDED`。C-04b 写「上限 **200**」→ 与冻结契约冲突。
- **`confirm_permanent_delete` 语义**：C-04b §2.2「含义不变」✓ 与 §6.1 第三行、§5.11.1 一致 ✓。
- **两个新码**：§2.3 `BOOK_DELETE_STALE_PREVIEW`（conflict/false）、`BOOK_DELETE_PROTECTION_INVENTORY_UNAVAILABLE`（internal/unavailable/true）与 ADJ-001 §6.3 逐字一致 ✓（category 二义问题见 P2-2）。
- **§5.11.5 安全投影（P1-5）**：`:802` 明文「错误码必须在 §5.11.3 集合内」`host 不得透传任意 details/文本/路径/stderr`；新增 2 码必须先扩 `PermanentlyDeleteBookErrorView` / `PermanentlyDeleteBooksErrorView` 的 code 联合与 batch `items` 的 item code 白名单，C-04b 未提。

### 2.4 协议版本

- 现行 §5.11 标题即「…冻结；Core protocol **2.10**」（`:678`），请求示例 `version: {major: 2, minor: 10}`（`:712`）。新增命令按 **minor 递增到 2.11** 合理 ✓；ADJ-001 §6.1 末句「必须按逐命令 minor 语义冻结并由 DSH 批准」✓ C-04b §2.1 写了版本与 `PROTOCOL_VERSION_UNSUPPORTED`，但未写「DSH 批准」环节（P2-3）。
- 旧 Core 返回 `PROTOCOL_VERSION_UNSUPPORTED` ✓ 与 ADJ-001 §6.2（`:86`）与 §5.11.3 `:757` 一致；「fail-closed、不忽略 digest、不回退软删」✓。

### 2.5 closed shape 与拒绝路径

- `inventoryDigest` 缺失/格式错 → `INVALID_REQUEST`；不匹配 → `BOOK_DELETE_STALE_PREVIEW`（零副作用）✓ 与 §6.1 一致。
- 缺口：①上限（P1-1）；②单条/批量形状（P1-4）；③`inventoryDigest` 的**格式**未定义（长度/字符集/算法/不透明标识），「格式错」无法判定 → P2-4；④`DeletePreviewItem.title` 与 PD-01 无对应项，建议注明为展示用非保护项（轻微，并入 P2-4）。

### 2.6 与 C-01b 接口

- C-01b `:94-97` 有 SC-30（应用内删除从不触点原文件）、SC-31（原始文件删除是独立流程）、SC-33（共享源不阻断删除、无法安全拆分 fail-closed）✓；C-04b §4「本草案是它们的协议层落地；C-01b 先（语义）、C-04b 后（协议字段），且 C-04b 须在 `G-DELETE-CONTRACT` 关闭后冻结」✓ 方向正确。
- 建议：§5 冻结条件补「C-01b 已冻结」与「DSH 批准逐命令 minor」（P2-3）；另 C-01b §4 条件② 允许「注明依赖后冻结」，而 C-04b 要求 gate 关闭——两者不冲突但建议 §4 写明该差异（可并入 P2-3）。

### 2.7 数据安全与治理

- 草案仅 1 次提交 `fc7505a96`，只新增 `doc/plan/FEA-C04b_DELETE_PROTOCOL_DRAFT.md`（其后至 HEAD 无 `src/**`/`apps/**` 改动）；无用户数据 ✓。
- **未 push**：`59342d6bf` 非 `origin/main` 祖先 ✓。
- **`check.ps1` 实跑**：`Governance check: PASS (3 warnings)`，EXIT=0（warning 为既有：7 个非终态 Task、`STATUS.md` 2911 B / 80%、`REBASELINE_PLAN.md` 6554 B / 80%）；运行后 `git status` 为空 ✓。
- 被审字节：C-04b @ `59342d6bf`，LF blob SHA-256 `2105800cf76b…20e6bbdf`（78 行）。

---

## 3. Findings

### P1

#### P1-1 — `bookIds` 上限写成 200，与 M2-C1 冻结的 `1..20` 冲突

- 位置：C-04b `:28`（§2.1 入参「非空、去重、上限 **200**」）。
- 证据：M2-C1 §5.11.1 `:691-692` `book_ids: BookId[1..20]`、`confirmed_book_ids: BookId[1..20]`；`:723`「批量 `book_ids` 必须有 1..20 项」；§5.11.2 `:733`「校验 closed shape、**1..20 上限**…超过上限立即拒绝」；§5.11.3 `:748` `BOOK_DELETE_BATCH_LIMIT_EXCEEDED` 按 20 判定。
- 影响：预览命令的上限与确认命令不一致（预览可 200、确认只能 20），会产生「预览成功但无法确认」的死路；且若按 200 冻结，`BOOK_DELETE_BATCH_LIMIT_EXCEEDED` 的判定值需改，等于改冻结契约。
- 建议：改为「1..20、ID 唯一、保持调用方顺序」（与 §5.11.1 一致），或明确「预览上限 = 确认上限 = 20」。

#### P1-2 — §1 现状错误表与 §2.3 冻结码表不完整，缺 PD-07/PD-09 所需码

- 位置：C-04b `:16`（§1 现状）、`:45-54`（§2.3 码表）。
- 证据：M2-C1 §5.11.3 `:742-758` 的完整码集合（见 §2.3 上文）与 §5.11.5 `:779-799` 两个 `ErrorView`；ADJ-001 PD-07（`:67`，`cleanup_pending` 与显式重试、`BOOK_NOT_FOUND` 零副作用）、PD-09（`:69`，逐项 `deleted`/`cleanup_pending`/`not_started`）。
- 影响：C-04b 声称「冻结码表」，但缺 `BOOK_DELETE_CLEANUP_PENDING`、`BOOK_DELETE_BATCH_CLEANUP_PENDING`、`BOOK_DELETE_BATCH_PREFLIGHT_FAILED`、`BOOK_DELETE_BATCH_LIMIT_EXCEEDED`、`BOOK_DELETE_BATCH_WHOLE_LIBRARY`、`UNKNOWN`、`CORE_UNAVAILABLE`，且把 item code（`BOOK_BUSY`/`BOOK_DELETE_CONFLICT`）当成顶层码列在现状表；实现者按此冻结会无法表达「DB 已提交但文件待清理」（PD-07 的核心状态）。
- 建议：§1 现状表按 §5.11.3 逐行列出（顶层码 + item code 分开标注）；§2.3 码表补全到 §5.11.3 ∪ §6.3，并新增「码 → 单条/批量 → category/retryable」三列。

#### P1-3 — 预览出参漏 PD-01 三项（人工修改区域数、活动草稿页数、将被删除文件数与字节量）

- 位置：C-04b `:29-30`（`DeletePreviewItem`）。
- 证据：ADJ-001 PD-01（`:58`）逐项列出九类；PD-02（`:60-62`）要求确认文案明示「将删除**人工修改**/锁定/固定版本的具体内容与数量」。
- 影响：缺「人工修改区域数」→ 无法生成 PD-02 要求的确认文案；缺「活动草稿页数」与「文件数/字节量」→ 用户在确认前看不到删除规模；这三项恰好是 ADJ-001 §1「逐项披露保护内容」的实质内容。
- 建议：`DeletePreviewItem` 增补 `manualEditedRegionCount`、`activeDraftPageCount`、`cleanup: { managedFileCount, managedByteSize, derivedFileCount, derivedByteSize }`；并在 §2.2 注明「确认文案必须引用这些计数」（PD-02）。

#### P1-4 — 未区分单条/批量命令形状，违反 PD-02「按命令形状分别绑定，不得混用」

- 位置：C-04b `:34-41`（§2.2 只写「现有删除命令的字段扩展」）。
- 证据：ADJ-001 PD-02（`:59-61`）：单条沿用 `{book_id, confirm_permanent_delete:true}` 并追加 `inventory_digest`，**禁止**引入 `book_ids`/`confirmed_book_ids`/`confirm_count`；批量沿用 `{book_ids, confirmed_book_ids, confirm_count, confirm_permanent_delete:true}` 的有序绑定并追加 digest；M2-C1 §5.11.1 `:685-695` 给出两个 payload 形状。
- 影响：协议无法区分两条命令的 closed shape 校验规则；若统一按数组处理，会破坏 §5.11.1「单条命令绝不接受数组」的冻结约束。
- 建议：§2.2 分两小节：`PermanentlyDeleteBook`（单条：追加 `inventory_digest`，其余不变）与 `PermanentlyDeleteBooks`（批量：追加 `inventory_digest`，`book_ids`/`confirmed_book_ids`/`confirm_count` 有序绑定不变）；并明确预览命令对单条调用方也返回单元素清单。

#### P1-5 — §5.11.5 两个 `ErrorView` 的 code 联合与 item code 白名单未同步扩展，新码无法投影

- 位置：C-04b `:45-54`（§2.3 只给「安全投影：只返回 bookId，不返回路径/明文」）。
- 证据：M2-C1 §5.11.5 `:779-799` 给出 `PermanentlyDeleteBookErrorView` / `PermanentlyDeleteBooksErrorView` 的显式 code 联合；`:802`「错误码必须在 §5.11.3 集合内；host 不得透传任意 details/文本/路径/stderr」。
- 影响：不在联合中的新码无法由 host 投影返回（TypeScript/JSON schema 层会拒绝）；§5.11.3 表本身也需新增行，否则 §6.3 的候选码没有落点。
- 建议：§2.3 增列「M2-C1 需同步修订的位置」：§5.11.3 错误表新增 2 行、§5.11.5 两个 ErrorView 的 code 联合各加 2 项（`BOOK_DELETE_STALE_PREVIEW` 属单条+批量；`BOOK_DELETE_PROTECTION_INVENTORY_UNAVAILABLE` 属单条+批量），并说明 batch `items[].error_code` 白名单同样扩展。

### P2

#### P2-1 — `BOOK_DELETE_CONFLICT` 触发条件漏 PD-08 的共享引用/归属类失败

- 位置：C-04b `:49`。
- 证据：ADJ-001 PD-08（`:68`）与 M2-C1 §5.11.3 `:752`（「项目关系图、目标外引用、Managed/derived 归属或安全枚举**不一致**」→ `BOOK_DELETE_CONFLICT`）。
- 建议：触发条件改为「保护阻止（Lock/current/pinned/active Run）**或**共享关系/归属无法安全拆分、关系图不一致（PD-08）」。

#### P2-2 — 「HTTP 语义」列不适配 IPC 契约，缺 `category`/`retryable` 三元组

- 位置：C-04b `:45`（表头「HTTP 语义」）。
- 证据：M2-C1 §5.11.3 的 ErrorEnvelope 为 `code / category / retryable`；ADJ-001 §6.3 用 `internal/unavailable` 组合描述。
- 建议：列名改「category / retryable」，并把 `BOOK_DELETE_PROTECTION_INVENTORY_UNAVAILABLE` 的 category 明确为 `unavailable`（retryable=true）。

#### P2-3 — §5 冻结条件缺「C-01b 已冻结」与「DSH 批准逐命令 minor」

- 位置：C-04b `:67-72`。
- 证据：§4 声明顺序「C-01b 先（语义）」但 §5 四条未含该前置；ADJ-001 §6.1 末句「必须按逐命令 minor 语义冻结并由 **DSH 批准**」。
- 建议：§5 增列「C-01b 已冻结」「DSH 批准 2.11 minor 冻结」。

#### P2-4 — `inventoryDigest` 格式未定义（「格式错」不可判定）；`title` 字段用途未注明

- 位置：C-04b `:29`（`title`）、`:38`（digest 格式错 → `INVALID_REQUEST`）。
- 建议：定义 digest 形态（如「32–64 字符 base16/base64url 不透明串」或「算法 + 输入范围」），并注明 `title` 为展示用、不参与保护判定；`computedAt` 与 digest 的绑定关系（同一预览生成的同一快照）也建议写清。

---

## 4. 独立性声明

- 我以 `c01b-reviewer`（Agent Teams **durable teammate**，`task-18`）身份出具本报告，`reviewer_kind: subagent`，独立上下文。
- **未参与** C-04b 草案撰写（作者 = DSH）、未参与 ADJ-001 / M2-C1 / C-01b / C-02 / C-03 / C-11 撰写，未参与 `src/**`、`apps/**` 任何实现。
- **利益披露**：我出具过 C-01b r1–r5、FEA-GOV-1~4 各报告；本轮对 ADJ-001 §5/§6、M2-C1 §5.11、C-01b SC-30/31/33 均**直接读取原文**并逐字对照，未引用既有报告结论。
- 本轮**只读**：唯一写入为新建本报告；未修改 C-04b / ADJ-001 / M2-C1 / C-01b / Task 卡 / 状态表；未 `git add`/`commit`/`push`；未触碰真实数据根。唯一执行的命令为只读 `check.ps1`（运行后 `git status` 为空）。
- **工作树状态记录**：报告落盘前 `git status --porcelain` 为空；`reviewed_head == HEAD == 59342d6bf`；被审文件 blob `1c8efaa44`。

---

## 5. NOT_RUN

- 未运行 `pytest` / `dotnet test` / 任何构建（纯文档治理 Task）。
- 未执行任何冻结或代码改动（草案为 DRAFT；冻结须 `G-DELETE-CONTRACT` 关闭 + D04/D07 裁决 + 独立复核 + DSH 执行）。
- 未审计 M2-C1 §5.11 之外的协议面（§8 ErrorEnvelope、§6 projections 等只在涉及处引用）。
- 未核 ADJ-001 的 D05 裁定时间表与 `G-DELETE-CONTRACT` 关闭路径（只核现状 OPEN）。
- 未验证 `PreviewPermanentDeleteBooks` / `inventory_digest` 的 Core 实现可行性（当前无实现，属计划态）。
- 未核远端历史细节（仅核本地 main 未 push）。

—— 报告结束（`verdict: changes_requested`，P0×0 / P1×5 / P2×4）。
