---
document_id: FEA-C13-r4
kind: independent_review
task_id: FEA-C13
round: 4
scope: very-narrow（只核 r3 的 P1×1 + P2×5 处置，共 6 处）
reviewer: c01b-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams durable teammate（独立上下文；未参与 C-13 v4 修订）"
reviewer_independent: true
reviewed_by_implementer: false
predecessor: FEA-C13-r3（r3：changes_requested，P0×0 / P1×1 / P2×5）
reviewed_head: 4c69a27ba
reviewed_head_full: 4c69a27baee6afad42a564527f2ead071d1a10a0
reviewed_head_note: "复核期间 HEAD 未前进（HEAD == reviewed_head == 4c69a27ba）"
reviewed_document: doc/plan/FEA-C13_DRAFT_PROTECTION_DRAFT.md（v4，219 行）
reviewed_sha256: 419ff1ebe02158b82ce5b034b9a51451c0a5a7a8856babed689eea9ef41e4fd8
reviewed_sha256_basis: "HEAD 的 LF blob（由 0ba30640b + 4c69a27ba 引入/更新）"
baseline: "src/application/editing/ports.py `:37-63`（RegionCommitStatus/RegionLockSnapshot）· src/application/editing/service.py `:128-129`/`:150-162`/`:233-245` · src/infrastructure/sqlite/schema.py `:256-257`（origin CHECK）· C-04b 冻结记录 §4A · C-08 · C-05"
repository: G:/CODEX/New Manga
source_branch: main
verdict: approved
p0_count: 0
p1_count: 0
p2_count: 4
p2_note: "4 条均为非阻断小项（origin 缺 file:line 指针、:89 裸 candidate 残留、『与 LOCK_CHANGED 对齐』措辞略强、§7 C-04b 行未提 SC-D12），登记为 K-1…K-4"
checkps1: "PASS（3 warnings），EXIT=0，本次实跑"
captured_at: 2026-11-01T09:13:03+08:00
captured_by: c01b-reviewer
---

# 独立复核 r4（极窄面）：C-13 v4

**本报告不是** 冻结动作、不释放任何 Task。本轮只核 r3 的 1×P1 + 5×P2，共 6 处。

## 1. 结论

**verdict：`approved`（P0 × 0 / P1 × 0 / P2 × 4 非阻断）。**

**r3 的 P1 与 5 条 P2 主体全部到位**，我逐条实核：

| # | 项 | 结果 |
|---|---|---|
| 1 | `:94` 不再要求改 C-04b | **✅**（改为「导出实现 Task 的 AC 承载；删除侧需提示须先走 `CONTRACT-UNFREEZE-<DATE>.md` 修订 C-04b（**本契约不改 C-04b**）」） |
| 2 | digest 公式只剩三锁 + manual 位 | **✅**（`:167-171` 只有 `region_locked‖translation_locked‖inpaint_locked‖manualFlagIn(text_json)`；`:174` 明写「**不含** `current_revision_id`/`updated_at`」；全文检索无公式内残留） |
| 3 | 「无假阳性」与 SC-D08 自洽、无重复拒绝 | **✅ 基本成立**（保护位才进 digest；修订漂移交 SC-D08 `BaseRevisionId` + 既有 `InputRevisionChanged`/`STALE_BASE_REVISION`）——措辞小瑕见 P2-3 |
| 4 | `origin` 取值域落在 SC-D07 | **⚠ 部分**（取值域已补且与 `schema.py:256-257` 的 CHECK 四值一致 ✓；但**文内无 `schema.py:256-257` 指针** → P2-1） |
| 5 | 章节顺序（`## 6A` 在 `## 6` 之后、SC-D12 在 SC-D11 之后） | **✅**（`:147` §6 → `:149` SC-D11 → `:158` §6A → `:160` SC-D12，物理顺序正确） |
| 6 | `check.ps1` PASS、无 push | **✅**（PASS 3 warnings / EXIT=0；`origin/main..HEAD` = 205，未 push；工作树干净） |

4 条 P2 均为**措辞/指针级**：`origin` 缺 `schema.py:256-257` 的 file:line（K-1）、`:89` 仍有一处裸 `candidate`（K-2）、「语义与既有 `LOCK_CHANGED` 对齐」略强（K-3，因 manual 位不在 `RegionLockSnapshot` 内）、§7 的 C-04b 行未提 SC-D12（K-4）。均不影响契约可执行性。

---

## 2. 6 处核对明细

### 1（P1）`:94` 不再要求改 C-04b —— ✅

- 现文（`:94`）：「…该要求由**导出实现 Task 的 AC** 承载；删除侧若也需要提示，须先走 `CONTRACT-UNFREEZE-<DATE>.md` 修订 C-04b（**本契约不改 C-04b**）。」
- 核对：不再出现「写入 C-04b 的 preflight 契约」；对 C-04b 的改动被**显式路由到 UNFREEZE 载体**，与冻结记录 `:17` 的规则一致 ✓。全文其余 C-04b 引用（`:162`/`:184-185`/`:195`）均为「不涉及/不改/已知局限登记」，无改动要求 ✓。

### 2（P2-4）digest 公式收敛 —— ✅

- 公式（`:166-171`）：
  ```
  protectionDigest(regionId) = sha256(
      region_locked ‖ translation_locked ‖ inpaint_locked
      ‖ manualFlagIn(text_json)
  )
  ```
- 仅三锁 + manual 位 ✓；`:174` 明写「**不含** `current_revision_id`/`updated_at`——修订漂移由 SC-D08 的 `BaseRevisionId` 校验与既有 `InputRevisionChanged`/`STALE_BASE_REVISION` 承担」✓。
- 全文残留检索：`current_revision_id` 仅出现在 schema 现状行（`:18`，表结构事实）、SC-D06/07/08 的语义描述（`:89`/`:92`/`:101`/`:103`/`:105`）与 `:174` 的**排除说明**——**公式内 0 残留** ✓；`updated_at` 仅 `:174` 的排除说明 ✓；`假阳性`/`fail-safe` 旧表述已无（`:181` 改为「无假阳性」）✓。

### 3（P2-5）「无假阳性」自洽性 —— ✅（措辞小瑕）

- `:181`：「摘要**只含保护状态位** → **无假阳性**（普通保存、流水线落 revision、改类型都不影响 digest）；保护本身变化才拒绝」。
- 与 SC-D08（`:110` 事务内校验 `BaseRevisionId` → `STALE_BASE_REVISION`）**不重复**：digest 管保护状态位、base 校验管修订漂移，职责分离 ✓——这正是 r3 P2-4/P2-5 要求的收敛。
- **唯一小瑕**：「语义与既有 `LOCK_CHANGED` 对齐」：既有 `RegionLockSnapshot`（`ports.py:56-63`）只含三把**区域级锁**，不含 `manualFlagIn(text_json)`；manual 位单独变化时复用 `LOCK_CHANGED` 属「语义近似」而非完全对齐 → P2-3。

### 4（P2-1）`origin` 取值域 —— ⚠ 部分

- 现状（`:102`）：「…必须携带 `{candidateId, RegionId, BaseRevisionId, origin}`，其中 `origin` ∈ {`machine`,`user`,`imported`,`restored`}（**与 `region_revisions.origin` 的 CHECK 约束一致，以该约束为唯一真源**）」。
- 核对：取值域四值与 `schema.py:256-257` 的 `CHECK (origin IN ('machine','user','imported','restored'))` **完全一致** ✓，落在 SC-D07 ✓。
- 缺口：**没有写 `schema.py:256-257` 这个 file:line 指针**（Lead 描述「指向 `schema.py:256-257` 的 CHECK」）→ P2-1（补一行即可）。

### 5（P2-3）章节顺序 —— ✅

- `## 6`（`:147`）→ `### SC-D11`（`:149`）→ `## 6A`（`:158`）→ `### SC-D12`（`:160`）——SC-D12 **物理上排在 SC-D11 之后** ✓；`6A` 命名在 `6` 之后 ✓（`6A` 插在 §6 与 §7 之间，编号可接受）。

### 6（治理）—— ✅

- `check.ps1` 实跑：`Governance check: PASS (3 warnings)`，EXIT=0（warning 既有：7 非终态 Task、`STATUS.md` 3185 B / 33 行、`REBASELINE_PLAN.md` 6598 B / 57 行）。
- `unpushed = 205`（未 push）✓；`git status` 干净 ✓；被审 blob `419ff1eb…`（219 行）。

---

## 3. 新增问题（P2 × 4，非阻断）

| # | 位置 | 问题 | 建议 |
|---|---|---|---|
| **K-1** | `:102` | `origin` 有取值域但**无 `schema.py:256-257` 指针**（与 Lead 描述不符） | 补「（`schema.py:256-257` 的 CHECK）」 |
| **K-2** | `:89` | 仍写「先成为 candidate」（裸 candidate 未清；`:88` 已改为「`status=active` 的 Draft」） | 改为「先成为 `RegionCandidate`」 |
| **K-3** | `:181` | 「语义与既有 `LOCK_CHANGED` 对齐」略强（manual 位不在 `RegionLockSnapshot` 内） | 改为「保护位变化（含 manual 位）复用 `LOCK_CHANGED` 状态；扩展点见实现 Task」 |
| **K-4** | `:195`（§7 C-04b 行） | 只写「SC-D09/SC-D10 是保护语义的编辑层落地」，未提 SC-D12 | 补「SC-D12 为编辑层保护摘要，不接入删除 preflight」 |

以上 4 条不影响 SC-D12 的可执行性（digest 输入、拒绝路径、验证用例都已定义），可在冻结前顺手修；**不构成阻断**。

---

## 4. 独立性声明

- 我以 `c01b-reviewer`（Agent Teams **durable teammate**）身份出具 r4，`reviewer_kind: subagent`，独立上下文；r1–r3 亦由我出具（如实披露）。
- **未参与** C-13 v4 修订（作者 = DSH）、未参与 `src/**` 实现。
- 本轮**只读**：唯一写入为新建本报告；未修改任何文件；未 `git add`/`commit`/`push`；执行的命令为只读 `check.ps1` 与 `git`/`Get-Content`/`Select-String` 取证。
- **工作树状态记录**：报告落盘前 `git status --porcelain` 为空；`reviewed_head == HEAD == 4c69a27ba`。

---

## 5. NOT_RUN

- 未运行程序/pytest（digest 公式、锁路径均为静态源码结论）。
- 未验证 SC-D08 的 apply 实现（计划态）与 SC-D12 的运行时性能（逐 Region sha256）。
- 未穷举 `manualFlagIn(text_json)` 在所有写入路径的镜像一致性（只核 `service.py:128-129` 的合并逻辑）。
- 未核 C-04b 冻结记录 §4A 之外章节（本轮已确认 pin `694ce5bc…` 一致）。
- 未核 U-03 裁决与冻结矩阵/STATUS 对 C-13 v4 的登记。

—— 报告结束（`verdict: approved`，P0×0 / P1×0 / P2×4；6 处：4 ✅ + 2 ⚠（均 P2））。
