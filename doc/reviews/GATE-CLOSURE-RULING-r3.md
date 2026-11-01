---
document_id: GATE-CLOSURE-RULING-r3
kind: independent_review
task_id: FEA-GOV-14
round: 3
scope: narrow（裁定 v3 新增 §R-4 + C-08 前置（b）重写，共 4 处）
reviewer: c01b-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams durable teammate（独立上下文；未参与裁定 v3 与 C-08 修订）"
reviewer_independent: true
reviewed_by_implementer: false
predecessor: GATE-CLOSURE-RULING-r2（r2：approved，P0×0 / P1×0 / P2×6——其中 P2-5 指出「R-2′ 排除 C-08 无论证」，本轮补 R-4）
reviewed_head: cc2888d93
reviewed_head_full: cc2888d936f071ff7730ab6b8eb08443008829bc
reviewed_head_note: "复核期间 HEAD 未前进（HEAD == reviewed_head == cc2888d93）；task-29 不存在，按 Lead 指令直接执行、报告名不变"
reviewed_documents:
  - doc/plan/GATE-CLOSURE-RULING-2026-11-01.md（v3，132 行）
  - doc/plan/FEA-C08_RUN_SNAPSHOT_DRAFT.md（85 行，前置（b）重写）
reviewed_sha256:
  doc/plan/GATE-CLOSURE-RULING-2026-11-01.md: d48cbd2713b6218296357a4dbd4d682c9093430e2b4707b01d301b88f0c40b80
  doc/plan/FEA-C08_RUN_SNAPSHOT_DRAFT.md: a4eccc5a0190a08db41673b6acd4eeb37e0e520dcc41646e21b6d07669c2468f
reviewed_sha256_basis: "HEAD 的 LF blob（由 cc2888d93 引入/更新）"
baseline: "doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md（§5.10 `:568`、§5.11 `:678`、§5.11.3 `:742`、§5.11.5 `:774`、§5.12 `:807`、Run 命令面 `:125`/`:193`）· C-04b 冻结记录 · apps/desktop-avalonia/src + src 代码检索"
repository: G:/CODEX/New Manga
source_branch: main
verdict: changes_requested
p0_count: 0
p1_count: 2
p2_count: 5
checkps1: "PASS（3 warnings），EXIT=0，本次实跑"
captured_at: 2026-11-01T09:32:48+08:00
captured_by: c01b-reviewer
---

# 独立复核 r3（窄面）：裁定 v3 §R-4 + C-08 前置（b）

**本报告不是** 冻结动作、不释放任何 Task。本轮只核 4 处：R-4 论证独立性、C-08 前置（b）自洽、负向对照可行性、治理。

## 1. 结论

**verdict：`changes_requested`（P0 × 0 / **P1 × 2** / P2 × 5）。**

**做对的部分**：

- **R-4 确实不再自动沿用 R-2′**：`:91` 标题即写「**单独论证**，不自动沿用 R-2′」，`:100` 又单列「与 R-2′ 的区别」；R-4 自带 C-08 的具体内容（3 码 + 2 命令 + wire 版本）而不是一句「同 R-2′」✓。
- **负向对照前提成立**：`RUN_STALE_PREVIEW`/`RUN_PREVIEW_EXPIRED`/`RUN_SNAPSHOT_INCOMPLETE` 与 `PreparedRun`/`preparedDigest` 在 `src/**` + `apps/desktop-avalonia/src/**` **0 命中** → 「未扩 M2-C1 时 3 个新码必须被 host 投影拒绝」这个负向对照**可执行** ✓。
- **C-08 的 3 码与 §3 一致**：`RUN_STALE_PREVIEW`（`:43`）、`RUN_PREVIEW_EXPIRED`（`:58`）、`RUN_SNAPSHOT_INCOMPLETE`（`:64`），2 个新命令 `PrepareRun`/`AcceptRun`（`:41-42`）✓。
- **共用同一 Task 的理由方向对**：C-04b 与 C-08 都改 M2-C1 的同一批错误投影面，分两次改确有冲突/重复复核成本 ✓（但范围写法错，见 P1-A）。

**两条 P1**（都指向同一处事实：**C-08 的协议注册不在 M2-C1 §5.11.3/§5.11.5**）：

1. **P1-A（R-4 第 4 点 + C-08 前置(b) 的 M2-C1 范围错误）**：两处都写「共用 Task 的范围 = M2-C1 **§5.11.3 表 + ErrorView 联合**（C-04b 的 2 码 + C-08 的 3 码 + 2 个 ErrorView）」。但 M2-C1 实核：§5.11 是「**项目级作品永久删除**」（`:678`，冻结；Core protocol 2.10），§5.11.3 是删除错误语义（`:742`）、§5.11.5 是删除错误投影/`PermanentlyDeleteBook(s)ErrorView`（`:774`）；**M2-C1 全文无 `PrepareRun`/`AcceptRun`**（大小写不敏感检索 0 命中），Run 命令面只有 `StartRun`/`ControlRun`/`ResumeBlockedRun`/`GetRunSnapshot`/`GetTaskProjection`/`RetryFailedTargets`（`:193` 附近）。→ C-08 的 3 个 `RUN_*` 码与 2 个新命令**不属于删除章节**，需要的是**新增 Run 命令章节 + 新 ErrorView**，不是「在 §5.11.3 追加两行」。
2. **P1-B（C-08 `:77` 的「§2」引用错位）**：前置（b）写「**方案**已冻结在本草案 **§2**」——但 C-08 §2 是「缺口（C-08 要冻结的）」四行表（PreparedRun 抽象 / candidate store / 配置变化 / 快照上下文），**没有** 3 码与 2 命令；它们在 **§3 的 `SC-R01`/`SC-R04`/`SC-R05`**。对照组：C-04b 的对应表述是「方案已冻结在 C-04b **§2.4**」，而 §2.4 确实列了 4 个扩展点 + 2 码——C-08 这里是引用错位。

| 核对项 | 结果 |
|---|---|
| 1. R-4 论证是否独立成立 / 共用 Task 是否合理 | **⚠ 部分**（同构与内容具体 ✓；「理由自带」偏弱 + 范围写错 → P1-A；耦合风险未治理 → P2-2） |
| 2. C-08 前置（b）是否自洽 | **⚠ 部分**（3 码/2 命令与 §3 一致 ✓；「§2」错位 → P1-B；排版/变更记录 → P2-4/P2-5） |
| 3. 负向对照是否可执行 | **✅**（5 个标识符 0 命中，前提成立） |
| 4. 治理 | **✅**（`check.ps1` PASS；未 push；工作树干净） |

---

## 2. 4 处核对明细

### 1（R-4 论证独立性）—— ⚠ 部分

- **成立的**：R-4 `:93` 明确「与 C-04b 条件⑤**同构**：都是『新增命令/错误码的协议注册须由独立 Task 完成』」；`:95-98` 给出 C-08 具体项（3 码、2 命令、独立 Task、负向对照、共用 Task）；`:100` 明确与 R-2′ 的区别。**形式上确实是单独论证，不是「因为 C-04b 所以 C-08」** ✓。
- **不足**：
  1. `:100`「理由是本条自带（同为『协议注册』模式、同样的负向对照要求、共用同一 M2-C1 修订 Task）」——三条理由**仍是模式复用**（同构 + 同要求 + 同文件），缺 C-08 **特有**的失败模式分析。例如：`preparedDigest` 的 canonical JSON 是否需要在字节层定义（否则跨端重算不一致）；Run 命令面既有 major 2.0 约束（M2-C1 `:125`：P13-C1 曾因 `StartRun.idempotency_key` 必填性把 Run 命令面升到 major 2.0）对新命令 = minor 的影响；`candidate store` 不落 Core DB（C-08 `:59`）与协议注册的关系。
  2. **共用 Task 的范围写法与 M2-C1 实际结构不符**（P1-A）。
  3. **耦合风险未治理**（P2-2）：一个 Task 同时改删除章节与新增 Run 章节，一方延期/返修会互相阻塞；`:119-121` 风险表只提「扩展被无限推迟」，未提「共用 Task 耦合/范围过大」。

### 2（C-08 前置（b）自洽）—— ⚠ 部分

- **对齐的**：3 码名称与 §3 逐字一致 ✓；「M2-C1 字节修订由独立 Task 在释放 Run 实现前完成 + 负向对照」与 R-4 一致 ✓；「与 C-04b 共用同一 Task」与 R-4 `:98` 一致 ✓。
- **P1-B**：「方案已冻结在本草案 **§2**」→ 应为 **§3**（`SC-R01`/`SC-R04`/`SC-R05`），或新增「协议注册清单」小节。
- **P2-4**：冻结条件排版断裂——`1.` → `- 前置（a）` → `2.` → `- 前置（b）` → `3.`（有序/无序混排，编号跳行），建议重排为 5 项有序列表。
- **P2-5**：`变更记录` 只有「建立」「v2」两行，**本次（(b) 重写）未记录**；另外裁定文件标题 `:1`/状态 `:3` 仍写 **v2**，与变更记录 v3 行不一致。

### 3（负向对照可行性）—— ✅

- 检索 `RUN_STALE_PREVIEW|RUN_PREVIEW_EXPIRED|RUN_SNAPSHOT_INCOMPLETE|PreparedRun|preparedDigest` 于 `src/**`、`apps/desktop-avalonia/src/**`（排除 target/node_modules/bin/obj）→ **0 命中** ✓。
- 与 C-04b 的情形同构：当前没有实现，负向对照只能在「host 投影实现后、M2-C1 未扩时」执行——**需要该独立 Task 的 AC 承载**（R-4 `:97` 已写）✓。

### 4（治理）—— ✅

- `check.ps1` 实跑：`Governance check: PASS (3 warnings)`，EXIT=0（既有 warning：7 非终态 Task、`STATUS.md` 3185 B / 33 行、`REBASELINE_PLAN.md` 6598 B / 57 行）。
- `origin/main..HEAD` = 208 提交（**未 push**）✓；工作树干净 ✓；被审 blob：裁定 `d48cbd27…`（132 行）、C-08 `a4eccc5a…`（85 行）。

---

## 3. 新增问题

### P1（2 条，见 §1）

- **P1-A**：R-4 `:98` + C-08 `:77` 的「M2-C1 **§5.11.3 表 + ErrorView 联合**」范围错误。修法：
  - 共用 Task 范围改写为两个不相交部分：**① C-04b 增量** = M2-C1 §5.11.3 表 + §5.11.5 两个删除 ErrorView 联合（2 码）；**② C-08 增量** = **新增 Run 命令章节**（`PrepareRun`/`AcceptRun`）+ **新增 Run 错误投影**（3 码）+ wire 版本声明；
  - 评估 Run 命令面的既有版本约束（M2-C1 `:125` 的 major 2.0 历史），确认新命令按 minor 递增；
  - R-4 `:98` 的「范围 = …」句与 C-08 `:77` 同步修改。
- **P1-B**：C-08 `:77`「方案已冻结在本草案 **§2**」→ 改 **§3**（`SC-R01`/`SC-R04`/`SC-R05`），或新增「§3A 协议注册清单」并在其中列 3 码 + 2 命令 + wire 版本。

### P2（5 条）

1. **P2-1**（R-4 论证）补 C-08 特有理由 2–3 条（preparedDigest 的 canonical JSON 字节级定义；Run 命令面 major 2.0 约束；candidate store 不落 Core DB 与协议注册的关系）。
2. **P2-2**（共用 Task 治理）`:119-121` 风险表补「共用 Task 耦合/范围过大」一行；建议明确「先 C-04b 后 C-08 两段提交、单一 owner、AC 按契约分包、范围上限」。
3. **P2-3**（wire 版本缺号）R-4 `:95` 说冻「`PrepareRun`/`AcceptRun` 的 wire 版本」，但**未给版本号与批准程序**（C-04b 有 R-3 批准 2.11 的先例）；建议明确 C-08 的 minor（如 **2.12**）与「由 DSH 批准」并写入 C-08 §5。
4. **P2-4**（C-08 排版）冻结条件 `1.`/`- 前置（a）`/`2.`/`- 前置（b）`/`3.` 混排 → 重排为 5 项有序列表。
5. **P2-5**（版本标注）C-08 变更记录缺本次 v3 行；裁定标题 `:1` 与状态 `:3` 仍写 **v2**（应与变更记录 v3 一致，改 v3）。

---

## 4. 独立性声明

- 我以 `c01b-reviewer`（Agent Teams **durable teammate**）身份出具 r3，`reviewer_kind: subagent`，独立上下文；本裁定的 r1/r2 复核亦由我出具（如实披露）。**task-29 不存在**，按 Lead 指令直接执行、报告名 `GATE-CLOSURE-RULING-r3.md`。
- **未参与** 裁定 v3 撰写（作者 = DSH）、未参与 C-08 修订、未参与 `src/**`/`apps/**` 实现。
- 本轮**只读**：唯一写入为新建本报告；未修改任何文件；未 `git add`/`commit`/`push`；执行的命令为只读 `check.ps1` 与 `git`/`Get-Content`/`Select-String` 取证。
- **利益披露**：r2 我在该裁定的 P2-5 指出「R-2′ 排除 C-08 无论证」，本轮 R-4 正是对该点的回应；我按同一标准复核，未因「回应了我的意见」而放宽。
- **工作树状态记录**：报告落盘前 `git status --porcelain` 为空；`reviewed_head == HEAD == cc2888d93`。

---

## 5. NOT_RUN

- 未运行程序/pytest（3 码 0 命中、M2-C1 章节结构均为静态检索结论）。
- 未核 M2-C1 §5 全章其余 Run 相关章节（只核 §5.10/§5.11/§5.12 标题与 Run 命令面行；未逐行核 §3/§4 的 Run 状态机）。
- 未核 C-08 的 preparedDigest canonical JSON 是否已有字节级定义（R-4 未要求，属 P2-1 建议）。
- 未核 C-04b 冻结记录对「共用 Task」的登记（本轮范围外）。
- 未核 U-03 裁决内容与冻结矩阵/STATUS 对 C-08 的登记。

—— 报告结束（`verdict: changes_requested`，P0×0 / P1×2 / P2×5；4 处：1 部分 + 1 部分 + 1 ✅ + 1 ✅）。
