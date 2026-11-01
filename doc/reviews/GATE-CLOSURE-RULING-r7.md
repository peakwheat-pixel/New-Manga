---
document_id: GATE-CLOSURE-RULING-r7
kind: independent_review
task_id: FEA-GOV-14
round: 7
scope: very-narrow（host 白名单表述自洽、§8 例外说明、C-08 :8 改述，共 3 处）
reviewer: c01b-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams durable teammate（独立上下文；未参与裁定 v5 与 C-08 修订）"
reviewer_independent: true
reviewed_by_implementer: false
predecessor: GATE-CLOSURE-RULING-r6（r6：changes_requested，P0×0 / P1×2 / P2×5）
reviewed_head: 3f24ffd17
reviewed_head_full: 3f24ffd170727fa61bffde88437c5c095b3286cf
reviewed_head_note: "复核期间 HEAD 未前进（HEAD == reviewed_head == 3f24ffd17）"
reviewed_documents:
  - doc/plan/GATE-CLOSURE-RULING-2026-11-01.md（v5，138 行）
  - doc/plan/FEA-C08_RUN_SNAPSHOT_DRAFT.md（v4，87 行）
reviewed_sha256:
  doc/plan/GATE-CLOSURE-RULING-2026-11-01.md: 5dd4d9a984842ad762b36cb1106f3daaa2543528b220ab1824f9cc9bf34d5333
  doc/plan/FEA-C08_RUN_SNAPSHOT_DRAFT.md: d5f055247ad609e567dd562d7537fea1e5198fca6a12567ea7e6c16773673c22
reviewed_sha256_basis: "HEAD 的 LF blob（由 3f24ffd17 引入/更新）"
baseline: "doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md §5.5 `:185-226`（P13-C1 冻结）· §8 `:1097-1130`（PROPOSAL；`:1097`/`:1101` 保留源码、`:1119` retryable 证据规则、`:1122` 不冻结 taxonomy）· C-04b §2.3 `:64-86`、§2.4 `:88-92`"
repository: G:/CODEX/New Manga
source_branch: main
verdict: changes_requested
p0_count: 0
p1_count: 3
p2_count: 3
checkps1: "PASS（3 warnings），EXIT=0，本次实跑"
captured_at: 2026-11-01T09:42:34+08:00
captured_by: c01b-reviewer
---

# 独立复核 r7（极窄面）：host 白名单 + §8 例外 + C-08 边界声明

**本报告不是** 冻结动作、不释放任何 Task。本轮只核 3 处。

## 1. 结论

**verdict：`changes_requested`（P0 × 0 / **P1 × 3** / P2 × 3）。**

**核心方向已经对了**：`Core §8 不动 + host 投影层降级` 的框架、`不重写 code`、`负向对照改挂白名单`、C-08 `:77` 的同步表述，都与 r6 的要求一致 ✓；`拒绝`/`§5.5 增规则`/`Core 拒绝` 这类旧话术在实际规范句里基本清干净了 ✓。

**但还剩三处「自己和自己打架」/「说要改实际没改」**：

1. **`:97` 同一段内「拒绝」与「降级」并存**：首句「未扩 M2-C1 时，3 个新码必须被 host 投影**拒绝**」，后文又说「**明确写死为「降级」而非「拒绝」**」——同一负向对照有**两个互斥的验收结果**，独立 Task 的 AC 无法判定。
2. **`:96` 与 `:100` 的 §8 落点互相矛盾**：`:96` 已改为「§8 新增「Proposed（未观察）」小节 3 行」，但 `:100`（块② 定义处）仍写「**§8 `:1109-1117` 的观察/映射表追加 3 行**」——r6 的 P2-1 只改了一半。
3. **C-08 `:8` 实际未改**：仍是「本文件是**草案**，不改 schema、**不改冻结契约**」；Lead 说已改为「本草案自身不修改任何文件…」，变更记录 `:87` 也写「§1「不改冻结契约」改述为本草案自身不写文件」——**变更记录虚述**，且「不改冻结契约」与前置（b）要求改冻结的 M2-C1 仍字面矛盾。

| 核对项 | 结果 |
|---|---|
| 1. host 白名单表述是否彻底自洽 | **⚠ 部分**：主体 ✓；`:97`「拒绝」残留 → **P1-1**；`:100` 旧落点 → **P1-2** |
| 2. §8 例外说明是否覆盖 P1-2 | **⚠ 部分**：`:1122`（taxonomy）已覆盖 ✓；`:1119`（retryable 证据规则）未覆盖 → P2-1 |
| 3. C-08 `:8` 改述后是否与前置（b）矛盾 | **❌ 未改**：原文仍在 → **P1-3**（含变更记录虚述） |

---

## 2. 3 处核对明细

### 1（host 白名单表述自洽）—— 主体 ✓，两处 P1

**已改对的**：

- 裁定 `:96`：「**且新增 host 投影层 `allowedRunErrorCodes` 白名单**」✓；
- 裁定 `:97`：「Core 侧保持 §8 现状（`:1097`「不得丢掉源 code」、`:1101`「未知时保留原始字符串」**不变**）；host 投影层：未注册的 `RUN_*` → `category=unknown` + 固定安全短消息，**不重写 `code`**、不得作为 UI 分支依据」✓；
- C-08 `:77`：「host 投影层新增 `allowedRunErrorCodes` 白名单（Core §8 不改；未注册码 → `category=unknown` + 安全短消息、**不重写 `code`**）」✓；
- 全文检索：无「§5.5 增规则」「Core 拒绝」残留；`拒绝` 的其余命中都在正确语境（C-08 的 AcceptRun 拒绝语义、C-04b 的删除负向对照）✓。

**P1-1（`:97` 首句残留「拒绝」）**：

> 3. 复核须含**负向对照**：未扩 M2-C1 时，3 个新码必须被 host 投影**拒绝**。……（后文）**明确写死为「降级」而非「拒绝」**（拒绝会让 host 无法展示任何信息）。

- 同一段出现两个互斥结果：**拒绝**（无响应/通用错）vs **降级**（`category=unknown` + 安全短消息 + 保留源码）。
- 后果：该独立 Task 的 AC 若照抄首句，用「拒绝」验收会**必然失败**；若照抄后句，又会与首句冲突——负向对照（R-4 第 3 点）无法落地。
- **修法**：首句改为「未扩 M2-C1 时，3 个新码必须被 host 投影**降级**（`category=unknown` + 安全短消息，**不重写 `code`**）」。

**P1-2（`:100` 未随 `:96` 更新）**：

- `:96`：块② 清单 =「§5.5 命令表追加 2 行 + 3 码进 §5.5 错误语义段 + **§8 新增「Proposed（未观察）」小节 3 行** + §8 例外说明 + host 白名单」；
- `:100`：块② 定义仍 =「3 个 `RUN_*` 码写进 §5.5 错误语义段 + **§8 `:1109-1117` 的观察/映射表追加 3 行**（该表是 PROPOSAL 观察记录、不是白名单）」。
- 两处**落点不同**（新小节 vs observed 表），实现者无法判断照哪处执行；r6 P2-1 的核心诉求（未观察码不要塞进「已观察到」表）在 `:100` 处失效。
- **修法**：`:100` 改为「§8 新增「Proposed（未观察）」小节 3 行（不要塞进 `:1109-1117` 的 observed 表）」。

### 2（§8 例外说明覆盖度）—— ⚠ 部分

- `:96` 已写「§8 `:1119`/`:1122` 的**例外说明**（**Run 线由 §5.5 白名单约束、其它命令仍开放 taxonomy**）」——点名覆盖了两行 ✓。
- **但内容只覆盖 `:1122`（taxonomy 冻结）**：「其它命令仍开放 taxonomy」对应的是 `:1122`「不冻结 `ErrorEnvelope` taxonomy」。
- `:1119` 是另一条规则：「`retryable` defaults to `unknown` unless Core has an **evidence-backed decision**」——C-08 给 3 个**未被观察到**的码写死 `retryable`（false/false/true），需要的是**「retryable 证据规则」的例外**：说明这些值是**契约级提案**、实现后由 Core 证据回填。现文没有这半句 → **P2-1**。
- **建议**：`:96` 的例外说明补齐为「§8 `:1122` 例外：Run 线 taxonomy 由 §5.5 白名单约束；§8 `:1119` 例外：C-08 三码的 `retryable` 为契约级提案值，实现后须以 Core 证据复核」。

### 3（C-08 `:8` 边界声明）—— ❌ 未改

- 实际原文（`:8`）：「**边界声明**：本文件是**草案**，不改 schema、**不改冻结契约**。」
- Lead 声称已改为「本草案自身不修改任何文件、不改 schema；M2-C1 字节修订由前置（b）独立 Task 执行」——**文件未变**（`git sha256` 与上一轮对比该段无变化；本回合 grep 直接命中原文）。
- C-08 变更记录 `:87` 却写「§1「不改冻结契约」改述为本草案自身不写文件」——**变更记录虚述**（声称做了、实际没做）。
- 矛盾仍在：前置（b）（`:77`）要求对**已冻结的 M2-C1** 做字节修订，而 `:8` 明写「不改冻结契约」→ 字面冲突。
- **修法**：把 `:8` 改为「**本草案自身**不修改任何文件、不改 schema；M2-C1 的字节修订由前置（b）的独立 Task 执行」；或明确「不改冻结契约」指的是本草案不直接改，并指向前置（b）。

---

## 3. 新增问题

### P1（3 条，见 §2）

- **P1-1** 裁定 `:97` 首句「必须被 host 投影**拒绝**」与同段「写死为**降级**而非拒绝」互斥 → 负向对照 AC 不可判定。
- **P1-2** 裁定 `:100` 的 §8 落点仍是「observed 表追加 3 行」，与 `:96` 的「新增 Proposed 小节」矛盾。
- **P1-3** C-08 `:8` 实际未改（仍写「不改冻结契约」），与前置（b）字面矛盾；变更记录 `:87` 虚述已改。

### P2（3 条）

1. **P2-1** `:96` 的 §8 例外说明只覆盖 `:1122`（taxonomy），未覆盖 `:1119`（retryable 证据规则）→ 建议补「C-08 三码 retryable 为契约级提案值，实现后由 Core 证据复核」。
2. **P2-2** 裁定标题 `:1` 仍写「· **v3**」，状态 `:3` 已是 **v5**（标题未随版本更新）。
3. **P2-3** C-08 变更记录 `:87` 写「处置裁定 r6 的 **P1×2 + P2×3**」，而 r6 实为 **P1×2 + P2×5**（计数不准；建议与报告一致）。

---

## 4. 独立性声明（简）

- 以 `c01b-reviewer`（Agent Teams durable teammate）身份出具 r7，独立上下文；本裁定的 r1–r6 复核亦由我出具（如实披露）。未参与裁定 v5 / C-08 撰写与实现。
- 本轮只读：唯一写入为新建本报告；未修改任何文件；未 commit/push；命令为只读 `check.ps1` 与 `git`/`Get-Content`/`Select-String`。`reviewed_head == HEAD == 3f24ffd17`。

---

## 5. NOT_RUN

- 未运行程序/pytest（§8 语义、例外说明均为静态原文结论）。
- 未核 host 侧是否已有 `allowedRunErrorCodes` 类实现（按 M2-C1 文本与裁定描述判断）。
- 未核 §8 在 Core/Tauri 两侧的实现。
- 未核 M2-C1 自身冻结记录/UNFREEZE 载体。
- 未核 U-03 裁决与冻结矩阵/STATUS 对 C-08 的登记。

—— 报告结束（`verdict: changes_requested`，P0×0 / P1×3 / P2×3；3 处：1 ⚠ + 1 ⚠ + 1 ❌）。
