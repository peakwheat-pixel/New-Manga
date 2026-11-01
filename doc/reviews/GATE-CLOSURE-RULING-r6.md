---
document_id: GATE-CLOSURE-RULING-r6
kind: independent_review
task_id: FEA-GOV-14
round: 6
scope: very-narrow（allowedRunErrorCodes 白名单、§8 观察表追加、两码新属性，共 3 处）
reviewer: c01b-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams durable teammate（独立上下文；未参与裁定 v4 与 C-08 修订）"
reviewer_independent: true
reviewed_by_implementer: false
predecessor: GATE-CLOSURE-RULING-r5（r5：changes_requested，P0×0 / P1×2 / P2×2——其中 P1-B 指出 Run 线负向对照不可执行）
reviewed_head: df0b2f830
reviewed_head_full: df0b2f83009b17f0a355fd28e33f6183fc20477f
reviewed_head_note: "复核期间 HEAD 未前进（HEAD == reviewed_head == df0b2f830）"
reviewed_documents:
  - doc/plan/GATE-CLOSURE-RULING-2026-11-01.md（v4，137 行）
  - doc/plan/FEA-C08_RUN_SNAPSHOT_DRAFT.md（86 行）
reviewed_sha256:
  doc/plan/GATE-CLOSURE-RULING-2026-11-01.md: a9c206165392f1ecba2e3482aec436eb335d243d677bd2ebb3abd0e90bf9dc5d
  doc/plan/FEA-C08_RUN_SNAPSHOT_DRAFT.md: 04e7ce7c4648b357521da7e77f1c98a95cbce602f1c39a9d5b132b2ce1676362
reviewed_sha256_basis: "HEAD 的 LF blob（由 df0b2f830 引入/更新）"
baseline: "doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md §5.5 `:185-226`（P13-C1 冻结）· §8 `:1097-1130`（PROPOSAL；`:1097`「不得丢掉源 code」、`:1101`「未知时保留原始字符串」、`:1119` retryable 证据规则、`:1122`「不冻结 taxonomy」）· §5.11.5 `:774-803` · C-04b §2.3 码表 `:64-86`、§2.4 投影扩展 `:88-92`"
repository: G:/CODEX/New Manga
source_branch: main
verdict: changes_requested
p0_count: 0
p1_count: 2
p2_count: 5
checkps1: "PASS（3 warnings），EXIT=0，本次实跑"
captured_at: 2026-11-01T09:39:58+08:00
captured_by: c01b-reviewer
---

# 独立复核 r6（极窄面）：白名单机制 + §8 表 + 码属性

**本报告不是** 冻结动作、不释放任何 Task。本轮只核 3 处：白名单校验点、§8 观察表追加、两码新属性。

## 1. 结论

**verdict：`changes_requested`（P0 × 0 / **P1 × 2** / P2 × 5）。**

**方向对了**：裁定 v4 `:97` 已如实写下「Run 线当前没有这个机制」（§8 `code` 自由字符串、`:1122` 不冻结 taxonomy、未注册码会透传），并明确块② 必须**同时新增校验点**——这正是 r5 P1-B 的落点 ✓。两码属性也已对齐 C-04b ✓。

**但「拒绝并降级为 `unknown`」这个写法有两个硬问题**：

1. **与 §8 明文冲突**：§8 `:1097`「**不得丢掉源 code**。原始 `code` 保持 Core 原值」、`:1101`「未知时**保留原始字符串**」——「降级为 `unknown`」= 改写/丢弃源码，**与这两句直接相反**；且把规则挂在「§5.5」（Core wire 层）逻辑不成立（Core 是码源，不能「拒绝自己未注册的码」）。
2. **「不冻结 taxonomy」将变不实**：§8 `:1122` 明写不冻结 `ErrorEnvelope` taxonomy、`:1119` 说 `retryable` 默认 `unknown` 除非有证据；块② 引入 Run 线封闭白名单 + 给 3 个**未被观察到**的码写死 retryable 后，这两句就不再成立，而块② 只写「§8 观察表追加 3 行」，**没有说要修订这两句**。

| 核对项 | 结果 |
|---|---|
| 1. `allowedRunErrorCodes` 校验点是否站得住 | **⚠ 部分**：方向 ✓；但「Core 层降级为 unknown」与 §8 冲突、层次不成立 → **P1-1**；§8 taxonomy 声明未同步修订 → **P1-2** |
| 2. §8 `:1109-1117` 追加 3 行是否可行 | **⚠ 结构可行、语义不符**：该表是「**已观察到**的错误表达」（confidence 列写 "Source code observed"），3 个新码 `src`+`apps` **0 命中**，放进去会变成假陈述 → P2-1 |
| 3. 两码新属性是否与 C-04b 一致 | **✅ 一致**（见 §2-3） |

---

## 2. 3 处核对明细

### 1（白名单校验点）—— 方向 ✓，两处 P1

**做对的**：v4 `:97` 坦白了 Run 线没有拒绝机制，并把「新增校验点」列为块② 的**交付项**，负向对照改挂白名单 ✓；C-08 `:77` 同步写「未扩 M2-C1 时 3 个新码必须被 host 的 `allowedRunErrorCodes` 白名单拒绝/降级」✓。

**P1-1（与 §8 冲突 + 层次混淆）**：

- §8 `:1097`：「以下为 **PROPOSAL**；**不得丢掉源 code**。`category` 是传输层粗分类，**原始 `code` 保持 Core 原值**。」
- §8 `:1101`：`code: string, # 源稳定 code；**未知时保留原始字符串**`。
- 「**降级为 `unknown`**」= 改写/丢弃源码 → 与上面两句**直接相反**。
- 层次：§5.5 是 **Core** wire 规范；Core 是错误码的**源**，要求 Core「拒绝/降级自己未注册的码」自相矛盾（码由 Core 产生，白名单也在 Core 侧就没有「未注册」这一说）。正确落点是 **host 投影层**（与 `allowedRunErrorCodes` 的位置一致）。
- **修法**：改成单一行为、明确层次——
  > Core **保留源码**（§8 不变）；**host 投影层**维护 `allowedRunErrorCodes`：未注册的 `RUN_*` → `category=unknown` + 固定安全短消息，**不重写 `code`**、不得作为 UI 分支依据（可记录原始码用于诊断）。
  > 若确要「拒绝」，则应由 host 在投影前**丢弃该命令的响应**并返回通用错误——但这会在 UI 表现为「请求失败」，与「未知码降级显示」不同，二选一后写死。

**P1-2（§8 taxonomy 声明未同步修订）**：

- §8 `:1122`：「本节仍为 `PROPOSAL`……**不冻结** `ErrorEnvelope` taxonomy」；`:1119`：「`retryable` defaults to `unknown` unless Core has an evidence-backed decision」。
- 块② 引入 Run 线封闭白名单、并给 3 个**未观察**码写死 `retryable` → 改完后 §8 这两句**部分不成立**，M2-C1 内部自相矛盾。
- **修法**：块② 增加一项「§8 `:1119`/`:1122` 追加**例外说明**」：Run 线错误码集合由 §5.5 的 `allowedRunErrorCodes` 约束（其它命令仍为开放 taxonomy）；并说明这是对 §8 PROPOSAL 的**显式修订**（不是静默追加 3 行）。可参照 C-04b §2.4 的写法（`:88-92`「新增码**必须同步扩展**两处封闭联合，否则 host 投影会拒绝」）——那是「同步修订」的先例。

**关于「是不是又一次 UNFREEZE 级改动」**：机制上不是问题——块② 已写「按 M2-C1 自身的修订/复核流程（含版本记录）」✓；但**性质变了**：块② 从「追加码」（增量）变成「新增白名单机制 + 修订 §8 taxonomy 声明」（语义级），工作量/风险明显大于块①（追加 2 行 + 2 ErrorView 联合）。R-4 仍用「同构」框架叙述，未标出这个不对称 → P2-2。

### 2（§8 :1109-1117 追加 3 行）—— 结构可行、语义不符

- 表结构 `Source code/example | Proposed category | Mapping confidence`（`:1111-1117`）**能容纳** 3 行 ✓。
- **但**：`:1109` 的引导句是「**已观察到的**错误表达：……」，表的 confidence 列逐行写「Source code observed / stable in Core」——3 个新码在 `src/**`+`apps/**` **0 命中**（未观察），写进该表会让「已观察到」变成**假陈述**，confidence 也无法如实填。
- 同节 `:1124-1128` 还有一张「命令级实现观察」表（同样只记录现状），也不适合放新码。
- **修法（P2-1）**：(a) 在 §8 新增独立小节「**Proposed（未观察；随 Core protocol 2.12 引入）**」放 3 行；或 (b) 把表扩为 `Observed | Proposed` 两栏并加 `source_status` 列；同时为这 3 行提供 `:1119` retryable 规则的例外说明（与 P1-2 合并处理）。

### 3（两码新属性 vs C-04b）—— ✅ 一致

| C-08 码 | 新属性 | C-04b 同类码 | 一致性 |
|---|---|---|---|
| `RUN_STALE_PREVIEW` | `conflict` / `retryable=false`（`:43`） | `BOOK_DELETE_STALE_PREVIEW` = `conflict` / `false`（C-04b `:85`） | ✅ |
| `RUN_PREVIEW_EXPIRED` | `conflict` / `retryable=false`（`:58`） | 同上（「需重新预览」类） | ✅ |
| `RUN_SNAPSHOT_INCOMPLETE` | `unavailable` / `retryable=true`（`:64`） | `BOOK_DELETE_PROTECTION_INVENTORY_UNAVAILABLE` = `unavailable` / `true`（C-04b `:86`） | ✅ |

两处修正均已到位（r5 的 P2-1/P2-2 闭合）✓。

---

## 3. 新增问题

### P1（2 条，见 §2-1）

- **P1-1**：「§5.5 增『未注册 `RUN_*` → 拒绝并降级为 `unknown`』」与 §8 `:1097`「不得丢掉源 code」/`:1101`「未知时保留原始字符串」冲突，且层次不成立（Core 是码源）。修法：改为 **host 投影层白名单 + 保留源码**（category=unknown、安全消息、不进 UI 分支）。
- **P1-2**：块② 引入 Run 线封闭白名单后，§8 `:1119`/`:1122` 的表述将不实；块② 必须显式加「§8 例外说明/修订」一项，否则 M2-C1 内部矛盾。

### P2（5 条）

1. **P2-1** §8 `:1109-1117` 是「已观察到的错误表达」表，3 个新码未观察 → 建议新增「Proposed（未观察）」小节或加 `source_status` 列，勿混入 observed 表。
2. **P2-2** 块② 比块① 多一个**机制级交付**（新增白名单 + §8 声明修订），R-4 仍以「同构」叙述、未标不对称；建议在 R-4 与共用 Task 的 AC/风险里把块①/块② 的分量与依赖分开写。
3. **P2-3** C-08 §6 变更记录缺本轮（r5 处置：白名单 + §8 落点）行；v3 行已被超越。
4. **P2-4** 裁定标题 `:1` 仍写「· **v3**」（状态 `:3` 已是 v4）——标题与状态不一致。
5. **P2-5** C-08 `:8` 边界声明「本文件是**草案**，不改 schema、**不改冻结契约**」与前置（b）要求改 M2-C1（冻结契约）字面矛盾 → 建议改为「本草案自身不修改任何文件；M2-C1 的字节修订由前置（b）的独立 Task 执行」。

---

## 4. 独立性声明（简）

- 以 `c01b-reviewer`（Agent Teams durable teammate）身份出具 r6，独立上下文；本裁定的 r1–r5 复核亦由我出具（如实披露）。未参与裁定 v4 / C-08 撰写与实现。
- 本轮只读：唯一写入为新建本报告；未修改任何文件；未 commit/push；命令为只读 `check.ps1` 与 `git`/`Get-Content`/`Select-String` 取证。`reviewed_head == HEAD == df0b2f830`。

---

## 5. NOT_RUN

- 未运行程序/pytest（§8 语义、码属性均为静态原文结论）。
- 未核 host 侧是否已有 `allowedRunErrorCodes` 类机制（本轮按 M2-C1 文本与裁定描述判断）。
- 未核 M2-C1 §8 在 Core/Tauri 两侧的实际实现（只核合同文本）。
- 未核 M2-C1 自身冻结记录/UNFREEZE 载体（只核 revision history 与 §5.5/§8 文本）。
- 未核 U-03 裁决与冻结矩阵/STATUS 对 C-08 的登记。

—— 报告结束（`verdict: changes_requested`，P0×0 / P1×2 / P2×5；3 处：2 ⚠ + 1 ✅）。
