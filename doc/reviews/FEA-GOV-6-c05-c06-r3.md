---
document_id: FEA-GOV-6-c05-c06-r3
kind: independent_review
task_id: FEA-GOV-6
round: 3
scope: very-narrow（只核 r2 的 1×P1 + 7×P2 处置、check.ps1 与是否引入新问题）
reviewer: c01b-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams durable teammate（task-19；独立上下文；未参与 C-05/C-06 撰写）"
reviewer_independent: true
reviewed_by_implementer: false
predecessor: FEA-GOV-6-c05-c06-r2（changes_requested：P0×0 / P1×1 / P2×7）
reviewed_head: 0b553d3ae
reviewed_head_full: 0b553d3aee7fd2f3ec408ebd24c577999108ff27
reviewed_head_note: "复核期间 HEAD 未前进（HEAD == reviewed_head == 0b553d3ae）"
reviewed_documents:
  - doc/plan/FEA-C05_PAGE_VISIBILITY_DRAFT.md
  - doc/plan/FEA-C06_SOURCE_AUTH_DRAFT.md
reviewed_sha256:
  FEA-C05_PAGE_VISIBILITY_DRAFT.md: 710f9c090fb28b4d7b83c782e24618c0eef5a921741902a1740e3562dfe3538b
  FEA-C06_SOURCE_AUTH_DRAFT.md: 25b1990249ac6ad4779904900221c01c09ae9dd12de317afbe2bd758f188032d
reviewed_sha256_basis: "HEAD 的 LF blob（C-05 96 行 / blob 9e62f306a；C-06 88 行 / blob 075e702ac）"
baseline: "doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md §3.2/§3.3/§3.5/§3.7 · doc/contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md §5 · doc/plan/FEA-C01b_STORAGE_CONTRACT_DRAFT.md SC-01/SC-07/SC-20/SC-21/SC-22 · src/bootstrap/core_assembly.py · src/infrastructure/sqlite/schema.py"
repository: G:/CODEX/New Manga
source_branch: main
verdict: approved
p0_count: 0
p1_count: 0
p2_count: 4
p2_note: "4 条均为非阻断（谓词 P1 未含祖先软删、§4 未引用 S、§2.2 仍写「直属成员」、§3 代码块结构被插入破坏），登记为 K-1/K-2/K-3/K-4"
checkps1: "PASS（3 warnings），EXIT=0，本次实跑"
captured_at: 2026-11-01T04:21:48+08:00
captured_by: c01b-reviewer
---

# 独立复核 r3（极窄面）：FEA-C05 / FEA-C06 稳定性谓词与授权面确认

**本报告不是** 冻结动作、不释放任何实现 Task，也不构成执行授权。本轮只核 r2 的 1×P1 + 7×P2 是否处置到位、`check.ps1` 是否 PASS、以及是否引入新问题。

## 1. 结论

**verdict：`approved`（P0 × 0 / P1 × 0 / P2 × 4 非阻断）。**

r2 的唯一 P1 **已闭环**：`P6` 已从 `V(p,t)` 的合取项**移出**，§3 另立稳定性谓词

```
S(p, t) ≡ V(p, t) ∧ active_runs(p) = ∅
```

`active_runs(p)` 明确为 `ACTIVE_STATES = {pending, running, paused, blocked, interrupted}`（与 `core_assembly.py:171-181` 一致，`prepared`/`committed` 已排除）；§6 删除预览已改为用 `S(p,t)` 计数；判别 SQL 不含活跃 Run 过滤，与 `V` 一致（S 的 SQL 可另给参考）✓。

7 条 P2 中 **5 条完全闭环**（P2-3 失败表补 `current_revision_id NULL` + `unknown`；P2-7 `VerifySourceRead` 归属校验；P2-9 §4 条款归因改正；K-6 持久化行改为「随备份纳入（AD-003 §3.3）、备份包内加密、不得在备份包之外泄露」；K-7 SC-01 依赖 / SC-07 不依赖）；**2 条部分**（P2-5 谓词 P1 未同步祖先软删；P2-10/11 冻结条件已补但「直属成员」未改）。

另有 2 条新 P2（均为编辑/结构问题）：§4 仍在写 `V ∧ 无在途 Run` 而没用新符号 `S`；§3 的代码块结构被本次插入破坏（fenced block 边界错位）。

| # | 核实项 | 结果 |
|---|---|---|
| 1 | C-05 P1：P6 移出 V + 另立 S + §4/§6 引用 S + V/SQL 一致 | **✅ 语义闭环**（P6 已移出、S 已定义、§6 已引用；§4 未引用 S → K-2；代码块结构 → K-4） |
| 2 | C-05 P2-3：失败表补 `current_revision_id` NULL + `unknown` | **✅** |
| 3 | C-05 P2-5：谓词 P1 含 `c/b.deleted_at` | **✗ 未到位**（SQL 已 join/过滤，谓词 P1 文本未改）→ K-1 |
| 4 | C-06 P2-7：`VerifySourceRead` 归属校验 | **✅**（出参补「`scope.sourceId/entry` 必须解析到某 `authorizedRoots` 内路径，映射在 Verify 时做，越根即拒绝」） |
| 5 | C-06 P2-9：§4 正文改「AD-003 §3.7 / PD-02/PD-03；PD-05=事务边界、PD-06=失败回滚」 | **✅** |
| 6 | C-06 P2-10/11：冻结条件 + 「直属会话」 | **⚠️ 部分**（冻结条件上轮已补；**§2.2 `:41` 仍写「直属成员」**）→ K-3 |
| 7 | C-06 K-6：持久化行「随备份纳入…备份包内加密…不得在备份包之外泄露」 | **✅** |
| 8 | C-06 K-7：SC-01 依赖 / SC-07 不依赖 | **✅** |
| 9 | 新问题 + `check.ps1` | 2 条新 P2（K-2/K-4）；**`check.ps1` 实跑 PASS(3 warnings) EXIT=0**；仅文档、未 push |

---

## 2. 8 处核对明细

### 2.1（P1）P6 移出 + 稳定性谓词 S —— ✅ 语义闭环

- §3（`:36-43`）：P6 行已删除，插入「**稳定性谓词**（导出/删除预览用，独立于可见性）：`S(p, t) ≡ V(p, t) ∧ active_runs(p) = ∅`」并说明 `active_runs(p)` 的 `ACTIVE_STATES` ✓。
- §4（`:66-68`）：P5 说明保留；`active_runs` 定义与 ACTIVE_STATES 一致；`prepared`/`committed` 明确不是 Run 状态 ✓。
- §6（`:83`）：删除预览「内容摘要」改为用 `S(p,t)`（稳定页）计数、不可见/不稳定页不计入 ✓。
- 判别 SQL（`:51-61`）只表达 `V`（无活跃 Run 过滤）✓，与谓词一致；S 的参考 SQL 未给（建议补，非阻断）。
- 遗留：§4 `:68` 仍写「导出与删除预览要求 `V(p,t) ∧ 无在途 Run`」——语义等价但未引用 `S`（K-2）。

### 2.2（P2-3）失败表 —— ✅

- `:74` 新增「`current_revision_id` 为 NULL | 该页**不可见**（P3 不满足；schema `:72` 允许 NULL）」✓；`:76` `integrity_status='unknown'` 行保留 ✓。

### 2.3（P2-5）谓词 P1 祖先软删 —— ✗ 未到位

- 谓词 `:30` 仍为 `P1. p.deleted_at IS NULL -- 页未被软删`；SQL `:53-57` 已 `JOIN chapters c / books b` 并过滤 `c.deleted_at IS NULL AND b.deleted_at IS NULL` → **谓词 ⊂ SQL**（SQL 比谓词严格），两者不等价 → K-1。

### 2.4（P2-7）`VerifySourceRead` 归属校验 —— ✅

- `:51` 出参列补：「**归属校验**：`scope.sourceId/entry` 必须解析到某 `authorizedRoots` 内的路径（映射在 Verify 时做，越根即拒绝）」✓ —— 补上了 r2 指出的 scope→root 映射与校验时机。

### 2.5（P2-9）§4 条款归因 —— ✅

- `:72` 已改为「删除授权（AD-003 §3.7 / PD-02/PD-03；注意 PD-05=事务边界、PD-06=失败回滚）与本授权面**独立**」✓；`:74` 的注保留（与正文一致，可合并，非阻断）。

### 2.6（P2-10/11）冻结条件 + 直属会话 —— ⚠️ 部分

- §5（`:82-86`）已 5 条：独立复核 / C-01b 已冻结 / `G-CONTRACT` 关闭 / wire 版本由 DSH 批准（v1.1 minor）/ `check.ps1` PASS ✓。
- ✗ §2.2 `:41` 仍写「旧 `ImportPages` 一次性 grant **保持原语义**（≤300 秒、**直属成员**、进程内）」→ 未改「直属会话（单 session 绑定）」→ K-3。

### 2.7（K-6）持久化与备份 —— ✅

- `:28`：「Host 私有存储（不写 Core DB）；**随备份纳入**（AD-003 §3.3「源引用与授权元数据默认包含」），备份包内加密；**不得在备份包之外**泄露」✓ 与 AD-003 §3.3 `:65` 一致。

### 2.8（K-7）§4 SC-01/SC-07 —— ✅

- `:70`：「SC-01（新导入不复制）依赖长期读取授权；SC-07（旧 managed 双读）**不依赖**本授权面」✓ 与 C-01b `:34/:45` 条文一致。

### 2.9 新问题（2 条）

#### K-4 — C-05 §3 代码块结构被破坏（编辑问题，建议冻结前修）

- 位置：C-05 `:28-44`。当前结构为：`:28` 开 fenced block → `:29-35` V 的 P1–P5 → `:36` 空行 → `:37` 「**稳定性谓词**…」→ `:39` ```` ``` ```` → `:40` `S(p, t) ≡ …` → `:41` ```` ``` ```` → `:43` 「其中 `active_runs(p)`…」→ `:44` ```` ``` ````。
- 按 CommonMark：`:39` 的栅栏会**先关闭** V 的代码块，`:40` 的 `S` 行变成普通段落，`:41` 再开新块并把 `:43` 的说明渲染成代码 → §3 的渲染结果与作者意图不符（V 块内混入加粗文字、S 与说明错位）。
- 影响：仅渲染/可读性，语义可从上下文恢复；但该节是要冻结的核心谓词，建议冻结前修正为「V 块在 P5 后闭合 → S 独立块 → active_runs 说明放块外」。

#### K-2 — §4 未引用新符号 `S`

- 位置：C-05 `:68`「导出与删除预览要求 `V(p,t) ∧ 无在途 Run`」。语义等价于 S，但 §3 已把 S 定义为唯一表达，建议改为「要求 `S(p,t)`」，避免两套写法并存。

---

## 3. 已知限制（非阻断）

#### K-1 — 谓词 P1 未含祖先软删，与 SQL 不一致

- 位置：C-05 `:30` vs `:53-57`。建议 P1 改为 `p.deleted_at IS NULL ∧ c.deleted_at IS NULL ∧ b.deleted_at IS NULL`（或在 §3 注明「SQL 含 SQL 额外的祖先过滤，谓词用于页内可见性」）。

#### K-3 — C-06 §2.2「直属成员」

- 位置：C-06 `:41`。代码语义为首个 session 绑定（`import_source_refs.py:192-196`），建议改「直属会话（单 session 绑定）」。

（K-2、K-4 见 §2.9。）

---

## 4. 独立性声明

- 我以 `c01b-reviewer`（Agent Teams **durable teammate**）身份出具 r3，`reviewer_kind: subagent`，独立上下文；r1/r2 亦由我出具（如实披露）。
- **未参与** C-05/C-06 撰写（作者 = DSH）、未参与 AD-003 / ADJ-001 / C-01b 撰写，未参与 `src/**`、`apps/**` 任何实现。
- 本轮**只读**：唯一写入为新建本报告；未修改任何文件；未 `git add`/`commit`/`push`；未触碰真实数据根。唯一执行的命令为只读 `check.ps1`（运行后 `git status` 为空）与只读取证。
- P1 闭环判定直接对照 `core_assembly.py:171-181`、C-05 §3/§4/§6 原文与 SQL；未引用 r2 结论作为依据。
- **工作树状态记录**：报告落盘前 `git status --porcelain` 为空；`reviewed_head == HEAD == 0b553d3ae`；C-05 blob `9e62f306a`、C-06 blob `075e702ac`。

---

## 5. NOT_RUN

- 未运行 `pytest` / `dotnet test` / 任何构建；未执行 SQL（谓词/SQL 等价性为静态审阅）。
- 未执行任何冻结或代码改动（两份均为 DRAFT）。
- 未审计 C-01b 其余 SC 条款（只核 SC-01/SC-07/SC-20/SC-21/SC-22 与两份草案的引用关系）。
- 未核 S 的参考 SQL（本轮未要求，建议补，非阻断）。
- 未验证 `source-read` grant 与 `handle_resolver` 的集成可行性（无实现，属计划态）。
- 未核远端历史细节（仅核本地 main 未 push）。

—— 报告结束（`verdict: approved`，P0×0 / P1×0 / P2×4 非阻断；8 处核实：6 全到位 + 2 部分）。
