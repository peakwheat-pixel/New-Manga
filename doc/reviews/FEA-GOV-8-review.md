---
document_id: FEA-GOV-8-review
kind: independent_review
task_id: FEA-GOV-8
reviewer: c01b-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams durable teammate task-21（独立上下文；未参与冻结矩阵撰写）"
reviewer_independent: true
reviewed_by_implementer: false
reviewed_head: 7080085bb
reviewed_head_full: 7080085bba7ad5839e9955b4c6e01297854b3a43
reviewed_head_note: "任务预期 reviewed_head 为 eb0f4bbff；复核时 HEAD 前进到 7080085bb（night-shift handoff），冻结矩阵 blob 未变（仍为 eb0f4bbff 引入的 bc202f83…）"
reviewed_document: doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md
reviewed_sha256: bc202f83b63385a0adaa15fa61275f3345074c963be410a50549cd2933e769c2
reviewed_sha256_basis: "HEAD 的 LF blob（79 行；由 eb0f4bbff 引入）"
baseline: "各草案冻结条件节（C-01b §4 / C-02 §6 / C-03 §4 / C-04b §5 / C-05 §7 / C-06 §5 / C-08 §5 / C-09 §4 / C-11 §8 / C-12 §6）· doc/plan/FEA-CONTRACT_FREEZE_PACKAGE.md · doc/contracts/ADJ-001（§9 Gate）· doc/AD-003（§5 Gate）· doc/plan/FEA-01_CONTRACT_DRAFT.md · doc/plan/FEA-C07_API_INVENTORY.md"
repository: G:/CODEX/New Manga
source_branch: main
verdict: changes_requested
p0_count: 0
p1_count: 1
p2_count: 7
checkps1: "PASS（3 warnings），EXIT=0，本次实跑"
captured_at: 2026-11-01T04:31:14+08:00
captured_by: c01b-reviewer
---

# 独立复核：FEA 契约冻结准备总表（冻结矩阵）

**本报告不是** 冻结动作、不释放任何 Task，也不构成执行授权。本轮把矩阵的 11 行 × 4 列逐条对照各草案的「冻结条件」节，并核对 8 步顺序、5 个 Gate、与 FREEZE_PACKAGE 的一致性。

## 1. 结论

**verdict：`changes_requested`（P0 × 0 / **P1 × 1** / P2 × 7）。**

矩阵的**骨架是对的**：11 行契约 + C-10 行、8 步顺序（第 0 步用户裁决 → C-01b → C-05/C-12 → C-02 → C-03/C-11 → C-06/C-04b → C-08 → C-09 → C-07）、5 个 Gate 影响面、与 FREEZE_PACKAGE 的四阶段序列**不冲突**（矩阵更细：PACKAGE 的「C-01b 最先 / C-02→C-03、C-11 依赖 C-01b 或 C-02」与矩阵第 1/3/4 步一致）；C-05 与 C-12 互不引用对方条件，**并行确实无相互阻塞** ✓；C-07 的「已生成（54 成员）」与 `FEA-C07_API_INVENTORY.md:22`「合计 54」一致 ✓。

但总表第 1 行（**C-01b，最先冻结的那行**）的冻结条件文本**损坏且与 C-01b §4 不符**，是 1 条 P1：

> 现文：`①用户回 `R`（AD-002 口径）②步骤 ②b（ADJ-001 依赖注明）③用户 ③`
> C-01b §4 实文：①独立复核（r1–r5 已跑，r5 `approved`）②**AD-003 的 `G-REVIEW` 收口** + ADJ-001 `G-DELETE-CONTRACT` OPEN（SC-30/31/33 冻结前须注明依赖）③**用户确认 AD-002 责任表与哨兵口径修订** ④`check.ps1` PASS

「②步骤 ②b」「③用户 ③」是不可读残句；「AD-003 G-REVIEW 收口」与「check.ps1」两项缺失（前者虽是 SATISFIED，但矩阵应如实列出）。按现文，执行者无法勾选该行条件。

7 条 P2 中 4 条是**行与草案不一致**（C-02 依赖、C-04b 的 D04/D07、C-05 依赖与顺序矛盾、C-12 漏核心条件）、1 条计数口径（10 vs 12）、1 条 Gate 关闭条件漏 D06、1 条 C-10 状态与依赖错。

| 审查项 | 判定 |
|---|---|
| 1. 准确性（11 行 vs 各草案冻结条件） | **不通过**（P1-1：C-01b 行损坏；P2：C-02/C-04b/C-05/C-12 四行不一致） |
| 2. 顺序可执行性（无环、无先冻后依赖） | **部分**（8 步无环；C-02 的「依赖 C-01b」非必需；C-05 依赖列与顺序自相矛盾；C-05∥C-12 无相互阻塞 ✓） |
| 3. Gate 清单（5 个） | **部分**（影响面准确；`G-DELETE-CONTRACT` 关闭条件漏 D06） |
| 4. 与 FREEZE_PACKAGE 一致性 | **通过**（PACKAGE 四阶段与矩阵步骤不冲突，矩阵更细） |
| 5. 遗漏（已批准/未起草标注） | **部分**（C-07「已生成/未复核」诚实 ✓；C-10 应为「部分」而非「未起草」，且依赖列无依据） |
| 6. 数据安全 | **通过**（仅文档、无用户数据、未 push；`check.ps1` PASS(3 warnings) EXIT=0） |

---

## 2. Findings

### P1

#### P1-1 — 总表第 1 行（C-01b）冻结条件文本损坏、缺关键前置

- 位置：矩阵 `:16`（第 1 行「冻结条件（差什么）」列）。
- 现文：「①用户回 `R`（AD-002 口径）②步骤 ②b（ADJ-001 依赖注明）③用户 ③」。
- 对照 C-01b §4（`:120-127`）：
  1. 本草案经**独立复核**确认与 AD-003/ADJ-001 一致、无新增语义（r1–r5 已跑，r5 `approved`）；
  2. **AD-003 自身的 `G-REVIEW` 收口**（AD-003 §6 明文：复审通过前不作为契约冻结依据）；ADJ-001 的 `G-DELETE-CONTRACT` 仍 OPEN，SC-30/31/33 冻结前须注明依赖；
  3. **用户确认 AD-002 的责任表与哨兵口径修订**（`Managed Copy` 行 + 顶部横幅归口）——即矩阵所说的「用户回 `R`」；
  4. `check.ps1` PASS。
- 问题：
  1. 「②步骤 ②b」「③用户 ③」为残句，不可执行；
  2. 缺「AD-003 `G-REVIEW` 收口」与「`check.ps1` PASS」两项（前者 AD-003 §5 `:131` 已 **SATISFIED**，应如实写「已满足」）；
  3. ①↔③ 的顺序映射把「独立复核」省略（虽已完成，但冻结时仍应勾选）。
- 建议：按 C-01b §4 四条重写该行，例如「①独立复核 ✅（r5 approved）②AD-003 `G-REVIEW` ✅（SATISFIED）+ ADJ-001 依赖注明（G-DELETE-CONTRACT OPEN）③用户确认 AD-002 责任表/哨兵口径（`R`）④`check.ps1` PASS」。

### P2

#### P2-1 — C-02 行的「依赖 C-01b」无依据

- 位置：`:17`（第 2 行）。
- 证据：C-02 §6（`:129-135`）的冻结条件只有「独立复核 / **U-04** / `check.ps1`」，与 C-01b 无依赖关系；矩阵却把 C-02 排在第 3 步（C-01b 之后）。
- 建议：依赖列改「无（与 C-01b 独立）」；顺序上 C-02 可在第 0 步之后与 C-05/C-12 并行（不阻塞其他步骤）。

#### P2-2 — C-04b 行的「③D04/D07」不在其冻结条件节

- 位置：`:19`（第 4 行）。
- 证据：C-04b §5（`:114-121`）6 条为 独立复核 / C-01b 已冻结 / `G-DELETE-CONTRACT` 关闭 / DSH 批准 2.11 / M2-C1 §5.11.3+§5.11.5 扩展独立 Task / `check.ps1`——**无 D04/D07 项**；D04/D07 出自 ADJ-001 §6.3（`:92`「最终码表由 D04/D07 冻结」）与 §9（`:128`「D04-D07 冻结」）。
- 建议：在 C-04b §5 补一行「ADJ-001 D04/D07（码表）裁决」，或矩阵该格注明「（ADJ-001 §6.3 码表裁决）」。

#### P2-3 — C-05 行「可与 C-01b 并行」与自身条件及顺序矛盾

- 位置：`:20`（第 5 行）与 `:36`（第 2 步）。
- 证据：C-05 §7 条件②「`VISIBLE_TYPES` 与 `active_runs` 语义**经 C-01b/ADJ-001 确认**」——需要 C-01b 的条款作为确认对象；矩阵却写「可与 C-01b 并行」，且顺序把 C-05 放在第 2 步（C-01b 冻结**之后**）。
- 建议：依赖列改「需 C-01b/ADJ-001 口径确认（C-01b 冻结后即可）」，与第 2 步一致。

#### P2-4 — C-12 行漏其核心冻结条件②

- 位置：`:26`（第 11 行）。
- 证据：C-12 §6（`:63-67`）3 条：①独立复核 ②**检查器现有断言与本文档 §2 表一致（可机械核对）** ③`check.ps1` PASS；矩阵只写「①独立复核（已做）」。
- 建议：补「②检查器断言与 §2 表一致（可机械核对）」。

#### P2-5 — 数量口径不一致（10 vs 11/12）

- 位置：`:8`（用途「10 份契约」）、`:72`（§5「10 份契约级」）、`:16-27`（总表 12 个数据行）。
- 证据：总表实含 **11 份已起草契约**（C-01b/C-02/C-03/C-04b/C-05/C-06/C-07/C-08/C-09/C-11/C-12）+ **C-10 未起草行** = 12 行。
- 建议：统一为「11 份已起草 + C-10 未起草（共 12 行）」。

#### P2-6 — Gate 表 `G-DELETE-CONTRACT` 关闭条件漏 D06

- 位置：`:55`。
- 证据：ADJ-001 §9 `:128`：「`G-DELETE-CONTRACT`（协议字段/码表/**D04-D07** 冻结）」；矩阵写「D04/D05/D07 裁决」，漏 D06。
- 建议：改「ADJ-001 的协议字段/码表冻结（D04–D07 裁决）」。

#### P2-7 — C-10 行状态与依赖不准

- 位置：`:27`（C-10 行）与 `:58`（U-03 行）。
- 证据：
  - FEA-01 `:59`：C-10 状态为「**部分**（追溯矩阵 / draft owner / 快捷键成立）」，缺手势阈值/可编辑态（R7-07）；矩阵写「未起草」。
  - FEA-01 C-10 的依赖列为「F-10、F-18、F-39、R7-07」，不是 C-03；矩阵依赖列写「C-03」无依据（C-03 是外观持久化）。
- 建议：状态改「部分（缺手势阈值/可编辑态，待 U-03）」；依赖改「F-10/F-18/F-39/R7-07（U-03）」。

---

## 3. 逐项核对明细（11 行 vs 各草案）

| 矩阵行 | 判定 |
|---|---|
| C-01b | **✗ P1-1**（文本损坏 + 缺 2 项；`R`、ADJ-001 依赖注明方向正确） |
| C-02 | **部分**（U-04 ✓；依赖「C-01b」无依据 → P2-1） |
| C-03 | **✅**（U-05a/b + C-02 先冻结，与 C-03 §4 ②③一致） |
| C-04b | **部分**（C-01b/G-DELETE/2.11/M2-C1 四项 ✓；多出 D04/D07 → P2-2） |
| C-05 | **部分**（条件 ✓；依赖/顺序矛盾 → P2-3） |
| C-06 | **✅**（C-01b/G-CONTRACT/wire v1.1 与 C-06 §5 一致） |
| C-07 | **✅**（已生成 54 成员与 `FEA-C07_API_INVENTORY.md:22` 一致；未复核诚实） |
| C-08 | **✅**（C-05/C-04b + C-01b + 协议注册，与 C-08 §5 前置一致） |
| C-09 | **✅**（C-01b + 两 Gate，与 C-09 §4 一致） |
| C-11 | **✅**（C-01b 或 C-02 至少其一，与 C-11 §8 一致） |
| C-12 | **部分**（漏条件② → P2-4） |
| C-10 | **部分**（状态/依赖 → P2-7） |

**顺序检查**：第 0 步（R + U-04 + U-05a/b）→ 1 C-01b → 2 C-05/C-12 → 3 C-02 → 4 C-03/C-11 → 5 C-06/C-04b → 6 C-08 → 7 C-09 → 8 C-07。
- 无环 ✓；C-03 在 C-02 后 ✓；C-08 在 C-05/C-04b 后 ✓；C-09 在 C-01b 后 ✓；C-11 在 C-01b/C-02 后 ✓。
- C-02 排第 3 步非必需（P2-1）；C-05 标「可与 C-01b 并行」但排第 2 步（P2-3）。
- **C-05 与 C-12 的无相互阻塞**：两者冻结条件互不引用，确认成立 ✓。

**Gate 清单**：`G-DELETE-CONTRACT`（影响 C-01b/C-04b/C-09 ✓，关闭条件漏 D06 → P2-6）；`G-CONTRACT`（C-06/C-09 ✓，AD-003 §5 `:128`）；`G-SAFETY`（FEA-00a 实现 ✓，AD-003 §5 `:129`）；U-03/U-04/U-05a/U-05b ✓；AD-002 口径 `R`（C-01b ✓）。

**与 FREEZE_PACKAGE 一致性**：PACKAGE 阶段 2「C-01b 冻结（最先）」、阶段 3「C-02 / C-03 / C-11 冻结（C-03 必须在 C-02 之后；C-11 依赖 C-01b/C-02 至少其一）」、阶段 4「释放第一个实现 Task」——矩阵第 1/3/4 步与之相符，且矩阵补充了 PACKAGE 未覆盖的 C-05/C-12/C-06/C-04b/C-08/C-09/C-07 步骤 → **不冲突** ✓。

---

## 4. 数据安全与治理

- 冻结矩阵由 `eb0f4bbff` 单次引入（+79 行），其后 HEAD 仅 night-shift handoff；`git diff --stat eb0f4bbff^..HEAD -- src apps` 为空 ✓。
- **未 push**：`eb0f4bbff` 非 `origin/main` 祖先 ✓。
- **`check.ps1` 实跑**：`Governance check: PASS (3 warnings)`，EXIT=0（warning 为既有：7 个非终态 Task、`STATUS.md` 2909 B / 31 行、`REBASELINE_PLAN.md` 6547 B / 57 行）；运行后 `git status` 为空 ✓。
- 被审字节：`doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md` @ `7080085bb`，LF blob SHA-256 `bc202f83b633…33e769c2`（79 行）。

---

## 5. 独立性声明

- 我以 `c01b-reviewer`（Agent Teams **durable teammate**，`task-21`）身份出具本报告，`reviewer_kind: subagent`，独立上下文。
- **未参与**冻结矩阵撰写（作者 = DSH）、未参与各草案与 AD-003/ADJ-001/FEA-01 撰写，未参与 `src/**`、`apps/**` 任何实现。
- 本轮**只读**：唯一写入为新建本报告；未修改任何文件；未 `git add`/`commit`/`push`；未触碰真实数据根。唯一执行的命令为只读 `check.ps1`（运行后 `git status` 为空）与只读取证。
- **利益披露**：我出具过 C-01b r1–r5、C-02/C-03/C-04b/C-05/C-06/C-08/C-09/C-11/C-12 的各轮复核（矩阵引用的 approved 状态即来自这些报告）；本轮对**各草案冻结条件节、FEA-01、ADJ-001 §9、AD-003 §5、C-07、FREEZE_PACKAGE** 均直接读取原文比对，未仅凭记忆。
- **工作树状态记录**：报告落盘前 `git status --porcelain` 为空；`reviewed_head = 7080085bb`（任务预期 eb0f4bbff；矩阵 blob 未变）。

---

## 6. NOT_RUN

- 未运行 `pytest` / `dotnet test` / 任何构建（纯文档治理）。
- 未执行任何冻结动作（矩阵为 DRAFT/待复核）。
- 未核 C-07 的 54 成员逐项正确性（只核总数与出处一致）。
- 未核 C-10 的具体交互内容（只核 FEA-01 的状态/依赖口径）。
- 未核 FREEZE_PACKAGE 全文（只核四阶段序列与顺序约束）。
- 未核远端历史细节（仅核本地 main 未 push）。

—— 报告结束（`verdict: changes_requested`，P0×0 / P1×1 / P2×7）。
