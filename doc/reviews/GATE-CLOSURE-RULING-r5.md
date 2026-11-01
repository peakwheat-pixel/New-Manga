---
document_id: GATE-CLOSURE-RULING-r5
kind: independent_review
task_id: FEA-GOV-14
round: 5
scope: very-narrow（块② 落点、3 码 category/retryable、治理，共 3 处）
reviewer: c01b-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams durable teammate（独立上下文；未参与裁定 v3 与 C-08 修订）"
reviewer_independent: true
reviewed_by_implementer: false
predecessor: GATE-CLOSURE-RULING-r4（r4：changes_requested，P0×0 / P1×1 / P2×4）
reviewed_head: 7e6f996db
reviewed_head_full: 7e6f996dbcbd1cafaa1a8b1e17ed897698c37a24
reviewed_head_note: "复核期间 HEAD 未前进（HEAD == reviewed_head == 7e6f996db）"
reviewed_documents:
  - doc/plan/GATE-CLOSURE-RULING-2026-11-01.md（v3，136 行）
  - doc/plan/FEA-C08_RUN_SNAPSHOT_DRAFT.md（86 行）
reviewed_sha256:
  doc/plan/GATE-CLOSURE-RULING-2026-11-01.md: b33b0626a96f8de709a8beed25ad6abbb1cdb7fd4648b39b325e86b6c9b1a960
  doc/plan/FEA-C08_RUN_SNAPSHOT_DRAFT.md: 4020292b644698446c235937562a7a76acd4e93cd646afecdc7606d0b9143773
reviewed_sha256_basis: "HEAD 的 LF blob（由 fe4b95aed + 7e6f996db 引入/更新）"
baseline: "doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md §5.5 `:185-226`（P13-C1 冻结）· §8 Error envelope `:1095-1130`（PROPOSAL）· §5.11.5 `:774-803`（封闭错误投影）· C-04b §2.3 码表"
repository: G:/CODEX/New Manga
source_branch: main
verdict: changes_requested
p0_count: 0
p1_count: 2
p2_count: 2
checkps1: "PASS（3 warnings），EXIT=0，本次实跑"
captured_at: 2026-11-01T09:37:47+08:00
captured_by: c01b-reviewer
---

# 独立复核 r5（极窄面）：块② 落点 + 3 码属性

**本报告不是** 冻结动作、不释放任何 Task。本轮只核 3 处：块② 落点、3 码 category/retryable、治理。

## 1. 结论

**verdict：`changes_requested`（P0 × 0 / **P1 × 2** / P2 × 2）。**

**命令表落点已改对**：块② 现在写「§5.5（P13-C1 冻结）命令表追加 `PrepareRun`/`AcceptRun` 两行」——与 M2-C1 `:189-196` 的表格结构吻合 ✓；`:101` 的论证也改对了（§5.11 = 删除、§5.5 = Run wire surface，必须扩展 §5.5）✓；C-08 `:77` 同步 ✓；「两块均为冻结章节修订、按 M2-C1 修订流程」✓。

**但「3 码进 §8 ErrorEnvelope 的允许码集合」这个落点不存在**，而且它牵出一个更实质的问题：**负向对照在 Run 线上不可执行**。

| 核对项 | 结果 |
|---|---|
| 1. 块② 落点是否准确 | **⚠ 部分**：§5.5 命令表 ✓；「§8 允许码集合」**不存在** → **P1-A**；连带「3 码被 host 投影拒绝」不可行 → **P1-B** |
| 2. 3 码 category/retryable 是否合理 | **⚠ 部分**：`RUN_STALE_PREVIEW`=conflict/false ✓；另两码与同类码不一致 → P2-1/P2-2 |
| 3. 治理 | **✅**（`check.ps1` PASS、未 push、工作树干净） |

---

## 2. 3 处核对明细

### 1（块② 落点）—— §5.5 ✓ / §8 ✗

**做对的**：§5.5 命令表 `:189-196` 现有 6 条命令（`StartRun`/`ControlRun`/`ResumeBlockedRun`/`GetRunSnapshot`/`GetTaskProjection`/`RetryFailedTargets`），追加 `PrepareRun`/`AcceptRun` 两行**结构上正确** ✓；「不是 per-command ErrorView、§5.11.5 是删除专属」的判断也正确 ✓。

**P1-A：「§8 `ErrorEnvelope` 的允许码集合」不存在**。M2-C1 实核：

- §8 标题下第一句（`:1097`）：「以下为 **PROPOSAL**；不得丢掉源 code」；
- `ErrorEnvelope` 定义（`:1100-1106`）：`code: **string**, # 源稳定 code；**未知时保留原始字符串**`——**自由字符串，不是枚举/封闭联合**；
- `:1119`：「`retryable` defaults to `unknown` unless Core has an evidence-backed decision」；
- `:1122`：「本节仍为 `PROPOSAL`……**不冻结** `ErrorEnvelope` taxonomy」；
- `:1130`：「以上值是命令级实现现状，**不能推广为同一 code 的全局映射**」。

→ §8 **没有任何「允许码集合」**（全文检索 `允许码|白名单|封闭` 也只命中 §5.9.2 的路径白名单与 rev 说明，与 ErrorEnvelope 码集合无关）。因此「3 码进 §8 允许集合」是**第三次落在不存在的结构上**（前两次是「新增章节」「新 ErrorView」）。
**修法**：把「进 §8 允许集合」改为——
- 在 **§5.5 的错误语义段**（`:223` 附近，`INVALID_RUN_TRANSITION` 所在处）列 3 个新码的语义/类别/可重试性；**和/或**
- 在 **§8 的「已观察到的错误表达 / 映射表」**（`:1109-1117`）追加 3 行（该表是 PROPOSAL 的观察记录，不是白名单）；
- 若要「拒绝未注册码」，必须**新增**一个校验点（见 P1-B），而不是假定 §8 会拒绝。

**P1-B：负向对照在 Run 线上不可执行**。R-4 `:97` 与 C-08 `:77` 都要求「未扩 M2-C1 时，3 个新码必须被 **host 投影拒绝**」。但：

- 删除线能拒绝是因为 §5.11.5 是**封闭联合**（`PermanentlyDeleteBook(s)ErrorView.code` 枚举）；
- Run 线走 §8 通用 `ErrorEnvelope`，`code` 为自由字符串且「**未知时保留原始字符串**」（`:1101`）→ 未注册的 `RUN_*` 码**会原样透传**，不会被拒；
- 后果：一旦实现者提前让 `AcceptRun` 返回 `RUN_STALE_PREVIEW`，host/UI 会收到一个未注册码并原样显示/记录——**正是负向对照想防的「新码被硬启」**，但当前机制挡不住。

**修法（二选一，推荐 A）**：
- **A（推荐）**：块② 明确为 Run 线**新增一个码白名单校验点**（例如 host 侧 Run 投影的 `allowedRunErrorCodes`，或 §5.5 增「Run 错误码必须 ∈ §5.5 集合，未知码 → `unknown`/`INVALID_REQUEST`」的封闭规则），然后把负向对照重述为「**未扩 M2-C1 时新码被该白名单拒绝（而非按 §8 透传）**」；
- **B**：承认 Run 线无法封闭，把负向对照改为「命令未注册时拒绝 + 码 passthrough 但 UI 不得按未知码分支」，并在 R-4 写清该差异（与 R-3 对 C-04b 的「旧端 fail-closed」表述分开）。

### 2（3 码 category/retryable）—— ⚠ 部分

- **`RUN_STALE_PREVIEW` = `conflict` / `retryable=false`** ✓：与 C-04b 同类码 `BOOK_DELETE_STALE_PREVIEW`（conflict/retryable=false，需重新预览）一致；也与 §8 观察表 `INVALID_RUN_TRANSITION`=conflict 的约定一致 ✓。
- **`RUN_PREVIEW_EXPIRED` = `conflict` / `retryable=true`** — **P2-1**：C-04b 中「预览过期/需重做」是 `false`；`retryable=true` 意味着「原请求可重试成功」，而「过期」实际要求**重新 prepare（新请求）**。建议对齐为 `false`，或注明「`true` 指可重新 prepare，非原请求可重放」。
- **`RUN_SNAPSHOT_INCOMPLETE` = `internal` / `retryable=true`** — **P2-2**：C-04b 中同类「清单/数据不可用」用 **`unavailable`**（`BOOK_DELETE_PROTECTION_INVENTORY_UNAVAILABLE`=unavailable/true）；§8 观察表中 `MISSING_REQUIRED_INPUT`=**unavailable**/false、`ARTIFACT_WRITE_FAILED`=internal/false。快照缺失/不完整更接近 `unavailable`（数据不可用）或 `validation`（输入不足），**不是 `internal`**。建议改为 `unavailable`（保留 retryable=true）或说明为何定位为内部故障。

### 3（治理）—— ✅

- `check.ps1` 实跑：`Governance check: PASS (3 warnings)`，EXIT=0。
- `origin/main..HEAD` = 211 提交（**未 push**）✓；工作树干净 ✓；被审 blob：裁定 `b33b0626…`（136 行）、C-08 `4020292b…`（86 行）。
- r4 的 P2 已修：C-08 §6 变更记录顺序 ✓（建立→v2→v3）、裁定 §6 顺序 ✓（v1→v2→v3）、裁定 §4 C-08 行补「wire minor `2.12` DSH 批准」✓、3 码补属性 ✓。

---

## 3. 新增问题

### P1（2 条，见 §2-1）

- **P1-A**：块② 的「§8 `ErrorEnvelope` **允许码集合**」不存在（§8 是 PROPOSAL、`code` 自由字符串、未知保留原值）。修法：改指 §5.5 错误语义段 + §8 观察/映射表（或新增校验点）。
- **P1-B**：负向对照「未扩 M2-C1 时 3 个新码必须被 host 投影拒绝」在 Run 线上不可执行（§8 无封闭联合）。修法：A 新增 Run 码白名单校验点并把负向对照挂到它；B 承认 passthrough、改口径。

### P2（2 条）

1. **P2-1** `RUN_PREVIEW_EXPIRED` 的 `retryable=true` 与 C-04b 同类码（false）不一致；建议统一或注明语义。
2. **P2-2** `RUN_SNAPSHOT_INCOMPLETE` 的 `internal` 与 C-04b 同类码（unavailable）不一致；建议改 `unavailable` 或说明理由。

---

## 4. 独立性声明（简）

- 以 `c01b-reviewer`（Agent Teams durable teammate）身份出具 r5，独立上下文；本裁定的 r1–r4 复核亦由我出具（如实披露）。未参与裁定 v3 / C-08 撰写与实现。
- 本轮只读：唯一写入为新建本报告；未修改任何文件；未 commit/push；命令为只读 `check.ps1` 与 `git`/`Get-Content`/`Select-String` 取证。`reviewed_head == HEAD == 7e6f996db`。

---

## 5. NOT_RUN

- 未运行程序/pytest（§8 结构、码属性均为静态原文/检索结论）。
- 未核 §8 ErrorEnvelope 在 Core/Tauri 两侧的实际实现（只核 M2-C1 文本）。
- 未核 C-08 的 3 码在 Host 侧是否已有别的白名单机制（本轮只按 M2-C1 文本判断）。
- 未核 M2-C1 自身独立冻结记录/UNFREEZE 载体（只核 revision history 与 §5.5/§8 文本）。
- 未核 U-03 裁决与冻结矩阵/STATUS 对 C-08 的登记。

—— 报告结束（`verdict: changes_requested`，P0×0 / P1×2 / P2×2；3 处：2 ⚠ + 1 ✅）。
