---
document_id: FEA-GOV-3-r2
kind: independent_review
task_id: FEA-GOV-3
round: 2
scope: very-narrow（只核 r1 的 1×P1 + 5×P2 处置、check.ps1 与是否引入新问题）
reviewer: c01b-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams durable teammate（按 lead 直接派发；未参与冻结包撰写，未参与 C-01b/C-02/C-03/C-11 草案撰写）"
reviewer_independent: true
reviewed_by_implementer: false
predecessor: FEA-GOV-3-review（r1：changes_requested，P0×0 / P1×1 / P2×5）
reviewed_head: 9e350dd6e
reviewed_head_full: 9e350dd6e
reviewed_head_note: "复核结束时 HEAD 前进到 feab2d57f（仅改 doc/handoffs/NIGHT-SHIFT-2026-11-01.md）；冻结包 blob 在 9e350dd6e 与 HEAD 相同（fe94b354b），无需复评"
reviewed_document: doc/plan/FEA-CONTRACT_FREEZE_PACKAGE.md
reviewed_sha256: d8c7d1c4020125b837fb51d543f5c437524652d9758b089ab00d067f777a45d2
reviewed_sha256_basis: "9e350dd6e 的 LF blob（89 行 / 6196 B）；与 HEAD 相同"
repository: G:/CODEX/New Manga
source_branch: main
verdict: changes_requested
p0_count: 0
p1_count: 2
p2_count: 3
checkps1: "PASS（3 warnings），EXIT=0，本次实跑"
captured_at: 2026-11-01T03:42:06+08:00
captured_by: c01b-reviewer
---

# 独立复核 r2（极窄面）：契约冻结包处置确认

**本报告不是** 冻结动作、不是用户裁决、也不是执行授权。本轮只核 r1 的 1×P1 + 5×P2 是否处置到位、`check.ps1` 是否 PASS、以及 v2 是否引入新问题。

## 1. 结论

**verdict：`changes_requested`（P0 × 0 / **P1 × 2** / P2 × 3）。**

**r1 的 P1-1 与三条 P2 已实质到位**：C-01b 条件② 已按「AD-003 半 ✅ / ADJ-001 半 ❌ 待补」并列写明，结论句改为「C-01b 差 **②b** 与 **③**」，阶段 2 已插入 **②b 动作**（注明 SC-30/31/33 依赖 ADJ-001）；回退表补了「部分回复」「仅剩 P2」两行并给出 `UNFREEZE` 记录载体；§3 收尾句改为「解锁用户侧条件、仍各自需复核」；C-02 行补了「仍受 C-01b 冻结约束」。`check.ps1` PASS。

但本次修订**新引入两条 P1**（都是小改即可修好）：

1. **FEA-00a 的排除理由与事实不符**（P1-2）：v2 写「**不建议** FEA-00a，因其是 SAFETY 线已覆盖的修复门」。实测：`G-SAFETY`（FEA-00a 的门）在 AD-003 §5 `:129` **仍 OPEN**；FEA-00a 所对应的 **F20 缺陷修复**在 FEA-00 r7 `:210` 与 r2 技术复核 `:82` 明确记为 **`NOT_RUN`（未修复）**；`src/infrastructure/providers/step_writes.py:207` `BEGIN IMMEDIATE` / `:270` `UPDATE regions SET text_json` 的 prepare 阶段提前写 live 结构仍在；SAFETY-1…12 各卡无该缺陷条目。排除**结论**可接受（FEA-00a 与双 UI 切换门关联、不宜作为首个实现 Task），但**理由必须改**。
2. **E-FREEZE-PKG pin 的 `commit` 列又没跟着换**（P1-3）：Task 卡 `doc/tasks/FEA-GOV-3.md:59` 现为 `commit=96265d879` + `sha256=d8c7d1c4…`；而 `96265d879` 处冻结包是 **v1**（`2881a895…`，84 行），`d8c7d1c4…` 是 **v2**（89 行，首见于 `9e350dd6e`）。该 (commit, sha256) 不可联合复核 —— 与 FEA-GOV-2 r2 P1-1 同一类问题再次出现；`check.ps1:661-678` 只校验格式与路径，会 PASS。

另 3 条 P2：阶段编号重复（阶段 2 新增步骤后未重排，出现两个「6」）、C-03 依赖 C-02 的冻结顺序仍未显式、FEA-04b 的用户取舍前置仍未提。

| r1 finding | 处置 | 说明 |
|---|---|---|
| **P1-1** C-01b ② 漏 ADJ-001 | **✅ 已处置** | ② 并列「AD-003 半 ✅ / ADJ-001 半 ❌ 待补」；结论改「差 ②b + ③」；阶段 2 新增 step 3「②b 动作」，step 5 记录「ADJ-001 依赖声明」，step 6 补「删除语义实现仍受 G-DELETE-CONTRACT 阻塞」 |
| P2-1 C-03 无正式条件条文 | **⚠️ 部分** | 注记已到位 ✅（`① 独立复核` 行内注明「本表 ①–③ 为归纳，冻结前须在 C-03 内补正式冻结条件条文」）；**C-03 依赖 C-02 已冻结的顺序仍未显式**（见 P2-1 残余） |
| P2-2 阶段 4 候选 | **✗ 未到位（且改错）** | 已说明 FEA-00a 与 FEA-04b，但 FEA-00a 理由与事实不符（升 P1-2）；FEA-04b 的「有关用户取舍」前置仍未提 |
| P2-3 回退表 | **✅ 已处置** | 新增「用户只回部分项」「仅剩 P2 未处置」两行；`UNFREEZE` 载体 = `doc/reviews/CONTRACT-UNFREEZE-<DATE>.md`（旧 hash / 原因 / 新版本 hash / 影响面） |
| P2-4 §3 收尾句 | **✅ 已处置** | 「即可**解锁全部用户侧条件**；四份契约仍各自需要独立复核通过后才能冻结」 |
| P2-5 C-02 阻塞映射 | **✅ 已处置** | C-02 ② 现状列补「且 C-02 冻结仍受 C-01b 冻结约束（同一批执行，C-01b 先）」 |

---

## 2. 6 项核对明细

### 2.1（P1-1）C-01b 条件② 拆分、结论句、阶段 2 动作 —— ✅

- 核对表（`:26`）：「② AD-003 `G-REVIEW` 收口 **+ ADJ-001 `G-DELETE-CONTRACT` 依赖注明** ｜ AD-003 半 ✅ `SATISFIED`；**ADJ-001 半 ❌ 待补**：`G-DELETE-CONTRACT` 仍 `OPEN`，C-01b 的 SC-30/31/33 冻结时须注明「依赖 ADJ-001 的 PD 语义」｜ 若漏注：Source/删除线实现会被误读为已具备删除语义」✓ 与 C-01b §4 `:123` 复合条件完全对应（ADJ-001 `:128` 仍 `OPEN`，本轮复核）。
- 结论（`:39`）：「C-01b 差 **②b（ADJ-001 依赖注明）** 与 **③（用户 AD-002 口径）**」✓。
- 阶段 2：「3. **②b 动作**：在 C-01b 冻结记录中注明『SC-30/31/33 依赖 ADJ-001 的 PD 语义，`G-DELETE-CONTRACT: OPEN`；删除线实现仍受该 Gate 阻塞』」✓；step 5 记录「ADJ-001 依赖声明」✓；step 6 补删除语义受阻声明 ✓。

### 2.2（P2-1）C-03 条件性质 —— ⚠️ 部分

- 已到位：C-03 ① 行注明「C-03 §3 写的是『冻结前置与判据』而非『冻结条件』，本表 ①–③ 为依据其判据归纳，**冻结前须在 C-03 内补正式冻结条件条文**」✓。
- **残余**：C-03 的实际冻结前置「C-02 已冻结」只写在 C-02 §6 `:124`（「C-03（外观持久化）可在本单之上冻结」），核对表与阶段 3 仍未显式列出该顺序（阶段 3 step 6 仍是「按复核结论逐份冻结」）→ P2-1。

### 2.3（P2-2）阶段 4 候选 —— ✗（理由错误，升 P1-2）

- 现状（`:70`）：「建议 **FEA-01 稳定端口冻结**——它不受 Source/删除 Gate 阻塞；或 **FEA-04b 四页设计**——无生产写域；**不建议** FEA-00a，因其是 SAFETY 线已覆盖的修复门」。
- FEA-00a 的理由不成立（见 P1-2 证据）；FEA-04b 依赖「FEA-00 与有关用户取舍」（方案 `:643`），出口要求「四页设计经用户确认、独立评审与 DSH 冻结」（方案 `:925`）——仍未提示该前置 → P2-2 残余。

### 2.4（P2-3）回退表 —— ✅

- 新增两行：「用户只回部分项 → 只冻结已满足条件的草案；其余保持 `DRAFT`，不阻塞已满足项」「仅剩 P2 未处置 → 可冻结，但须在冻结记录中把 P2 登记为『已知限制』」✓；`UNFREEZE` 载体写明 `doc/reviews/CONTRACT-UNFREEZE-<DATE>.md`（记录旧 hash、原因、新版本 hash、影响面）✓ 可执行。
- 提示（非 finding）：`doc/reviews/CONTRACT-UNFREEZE-<DATE>.md` 目前不在任何 Task 的 `allowed_paths` 内，真正执行 `UNFREEZE` 时需另开治理 Task 或先扩 allowed_paths。

### 2.5（P2-4）§3 收尾句 —— ✅

- `:50`：「一次回 `R / U04=A / U05a=A / U05b=否` 即可**解锁全部用户侧条件**；四份契约仍各自需要独立复核通过后才能冻结（其中 C-02/C-03/C-11 的复核尚未进行）」✓ 不再暗示「回复即冻结」。

### 2.6（P2-5）C-02 阻塞映射 —— ✅

- C-02 ② 现状列补「且 C-02 冻结仍受 C-01b 冻结约束（同一批执行，C-01b 先）」✓。

### 2.7 新问题 + `check.ps1`

- 新增：P1-2（FEA-00a 错误理由）、P1-3（pin commit 未回填）、P2-6（阶段编号重复）。
- **`check.ps1` 实跑**：`Governance check: PASS (3 warnings)`，EXIT=0；3 条 warning 为既有（7 个非终态 Task、STATUS 2934 B / 80%、REBASELINE_PLAN 6544 B / 80%）；运行后 `git status` 为空 ✓。
- 提交面：`9e350dd6e` 只改 `doc/TASK_LEDGER.md`、冻结包、`doc/reviews/FEA-GOV-3-review.md`、`doc/tasks/FEA-GOV-3.md` —— 无 `src/**`、`apps/**`、无用户数据 ✓；无 push（本地领先 origin/main）✓。

---

## 3. Findings

### P1

#### P1-2（新）— 阶段 4 对 FEA-00a 的排除理由与事实不符：「SAFETY 线已覆盖的修复门」不成立

- 位置：冻结包 `:70`（阶段 4 第 9 步）。
- 反证（四项，均可复核）：
  1. **门仍开着**：`doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md:129` — `| G-SAFETY（FEA-00a 既有 Core 提前写缺陷修复） | **OPEN** | 与双 UI 切换门关联，独立于本决策 |`；
  2. **修复仍 `NOT_RUN`**：`doc/reviews/FEA-00-dsh-r7.md:210`「F20 既有数据安全缺陷成立：`src/infrastructure/providers/step_writes.py:207` `BEGIN IMMEDIATE` → `:248-266` `INSERT region_re…`」、`doc/reviews/FEA-00-dsh-r2-technical-recheck.md:82`「F-07 / FEA-00a | **未修复**（`NOT_RUN`）」；
  3. **代码结构仍在**：`src/infrastructure/providers/step_writes.py:207` `self.conn.execute("BEGIN IMMEDIATE")`、`:270` `UPDATE regions SET text_json = ?…`（prepare 阶段提前写 live `text_json`）；
  4. **SAFETY 线未覆盖该缺陷**：`REALUSE-DATA-SAFETY-1…12` 各卡标题与 AC 分别覆盖命名空间迁移自愈/真实备份、Provider 可用性引导/启动自检、Console 分区接线、B3/B4 卫生、进度刷新/旧库迁移/derived/安装脚本、以及 6 轮 Review 收尾；**无一条**涉及 `RegionStepWriter` / `step_writes` / F20 / prepare 提前写 live（grep 已确认）。
- 影响：这是发给用户的准备稿，若用户据此认为 FEA-00a「已覆盖」，则该门可能长期不排期；而 `G-SAFETY` 与双 UI 切换门（FEA-07）关联，**该缺陷不在任何既有 Task 的实现范围内**。排除**结论**本身可接受（FEA-00a 与切换门关联，不宜作为首个实现 Task），但理由必须纠正，否则等于在冻结包里写了一条与冻结决策记录（AD-003）相悖的事实。
- 建议（一行改写）：「**不建议** FEA-00a 作为首个实现 Task——它的门是 **`G-SAFETY: OPEN`**（AD-003 §5 `:129`），对应 F20 的 prepare 提前写 live `text_json` 仍未修复（`NOT_RUN`，FEA-00 r7 `:210`），且与双 UI 切换门（FEA-07）关联，应在其前置位置单独排期」。

#### P1-3（新，重复类缺陷）— E-FREEZE-PKG pin 的 `commit` 列未随 v2 更新，(commit, sha256) 不可联合复核

- 位置：`doc/tasks/FEA-GOV-3.md:59`（Canonical Evidence 行）。
- 现状：`| E-FREEZE-PKG | AC1/AC2 | doc/plan/FEA-CONTRACT_FREEZE_PACKAGE.md | 96265d879 | d8c7d1c4…45d2 | CANONICAL |`
- 实测（本轮逐版本复算）：
  - `96265d879:…` → 4768 B / 84 行 / sha256 `2881a8953a89…557b58a`（**v1**）；
  - `9e350dd6e:…` → 6196 B / 89 行 / sha256 `d8c7d1c40201…77a45d2`（**v2**，= pin 的 sha256）；
  - HEAD 与 `9e350dd6e` 相同。
  → pin 的 (commit=`96265d879`, sha256=`d8c7d1c4…`) 组合取不到对应字节；证据链在 reviewed_head 处不可复核。
- 复现性：与 **FEA-GOV-2 r2 P1-1 完全同类**（当时也是「改了 sha256、漏了 commit」，由 `0e30a6d79` 修正）。`check.ps1:661-678` 只校验列数/路径/class/`commit` 格式/「至少一 pin」，**不校验 commit 与 sha256 是否吻合**，机械检查会 PASS，只有评审能拦。
- 建议：把 `commit` 改为 `9e350dd6e`（或在其后的回填提交中改为最终交付提交），Closeout 前用 `git cat-file blob <commit>:<path>` + SHA-256 复算一次。

### P2

#### P2-6（新）— 阶段编号重复：阶段 2 新增步骤后未重排，出现两个「6」

- 位置：冻结包 `:62`（阶段 2 第 6 步「关闭 C-01b 的冻结前置③…」）↔ `:65`（阶段 3 第 6 步「按复核结论逐份冻结…」）↔ `:70`（阶段 4 第 9 步）。
- 事实：v1 的编号为 1–2 / 3–5 / 6–8 / 9；v2 在阶段 2 插入一步后成为 3–6 / **6**–8 / 9 —— 两个「6」，且总序号错位（阶段 3 应为 7/8/9，阶段 4 应为 10）。
- 影响：纯编号问题，不影响语义；但执行清单被当作 checklist 逐项勾选时会产生歧义（「第 6 步」指哪一步）。
- 建议：重排为 3–6（阶段 2）/ 7–9（阶段 3）/ 10（阶段 4）。

#### P2-1（残余）— C-03 依赖「C-02 已冻结」的顺序仍未在核对表/阶段 3 显式

- 位置：冻结包 `:32-34`（C-03 行）、`:64-67`（阶段 3）。
- 依据：C-02 §6 `:124`「冻结后：C-02 关闭；**C-03（外观持久化）可在本单之上冻结**」。
- 建议：阶段 3 step 6 改为「C-02 先冻结，C-03 随后（C-03 以 C-02 为前置），C-11 最后」。

#### P2-2（残余）— FEA-04b 的「有关用户取舍」前置仍未提

- 位置：冻结包 `:70`。
- 依据：方案 `:643` FEA-04b 依赖「FEA-00 与**有关用户取舍**」；`:925` 出口要求「四页设计经**用户确认**、独立评审与 DSH 冻结」。
- 建议：在 FEA-04b 候选后补「需先完成 §13 相关用户取舍与用户确认」。

---

## 4. 独立性声明

- 我以 `c01b-reviewer`（Agent Teams **durable teammate**）身份出具 r2，`reviewer_kind: subagent`，独立上下文；r1 亦由我出具（如实披露）。
- **未参与**冻结包撰写（作者 = DSH）、未参与四份草案撰写、未参与 `src/**`、`apps/**` 任何实现。
- 本轮**只读**：唯一写入为新建本报告；未修改冻结包 / Task 卡 / 四份草案 / 状态表；未 `git add`/`commit`/`push`；未触碰真实数据根。唯一执行的命令为只读 `check.ps1`（运行后 `git status` 为空）与只读取证（`git cat-file`/`git diff`/`grep`）。
- 对 P1-2 的事实判定**独立取证**：未引用 r1 结论作为依据，而是重新核对 AD-003 §5、FEA-00 r7/r2-recheck、`step_writes.py` 代码与 SAFETY 卡清单。
- **工作树状态记录**：报告落盘前 `git status --porcelain` 为空；`reviewed_head = 9e350dd6e`（复核末 main 前进到 `feab2d57f`，仅改 night-shift handoff；冻结包 blob 相同）。

---

## 5. NOT_RUN

- 未运行 `pytest` / `dotnet test` / 任何构建（纯文档治理）。
- 未执行任何冻结动作（本稿为 PREPARED）。
- 未审 C-02/C-03/C-11 全文语义（本轮只核冻结条件段与包内表述）；未重审 C-01b 全文（见 r1–r5 报告）。
- 未验证 FEA-00a 的修复工作量与排期方案（只核「门未关 + 修复 NOT_RUN + 结构仍在」三项事实）。
- 未验证 `doc/reviews/CONTRACT-UNFREEZE-<DATE>.md` 路径的可用性/授权面（只指出其不在现有 allowed_paths）。
- 未核远端历史细节（仅核本地 main 未 push）。

—— 报告结束（`verdict: changes_requested`，P0×0 / P1×2 / P2×3；r1 处置：P1 已处置 1/1，P2 已处置 3/5、部分 1、未到位 1）。
