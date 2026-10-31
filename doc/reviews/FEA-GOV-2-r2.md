---
document_id: FEA-GOV-2-r2
kind: independent_review
task_id: FEA-GOV-2
round: 2
scope: narrow（只核 r1 findings 处置 + 是否引入新问题）
reviewer: c01b-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams durable teammate（本轮按 lead 直接派发执行；未参与 AD-002 修订提案撰写、未参与 FEA-GOV-1 撰写）"
reviewer_independent: true
reviewed_by_implementer: false
predecessor: FEA-GOV-2-review（r1：changes_requested，P0×0 / P1×1 / P2×5）
reviewed_head: 26feb784e
reviewed_head_full: 26feb784efc572fb7078a7ad4554b92f0986f5b9
reviewed_head_note: "复核期间 main 前进到 85b78dce8（仅改 doc/handoffs/NIGHT-SHIFT-2026-11-01.md +3 行）；已核对提案 / Task 卡 / AD-003 三文件在 26feb784e 与 HEAD 的 Git blob 完全相同，判定对 reviewed_head 有效"
reviewed_document: doc/plan/FEA-AD002_AMENDMENT_PROPOSAL.md
reviewed_sha256: 5255dfa837cc54711d560b725f247bed0ed52ab0c9276c0056ec8f5a6e1c310b
reviewed_sha256_basis: "26feb784e 的 LF blob（85 行）；git blob a328aee40b"
repository: G:/CODEX/New Manga
source_branch: main
verdict: changes_requested
p0_count: 0
p1_count: 2
p2_count: 4
captured_at: 2026-11-01T03:31:48+08:00
captured_by: c01b-reviewer
---

# 独立复核 r2：AD-002 责任表与哨兵口径修订提案 v2（窄面）

**本报告不是** 用户裁决、不是对 AD-002 的修改，也不构成执行授权。本轮为**极窄面**复核：只判断 r1 的 1×P1 + 5×P2 是否处置完毕、以及 v2 是否引入新问题。

## 1. 结论

**verdict：`changes_requested`（P0 × 0 / **P1 × 2** / P2 × 4）。**

**提案正文的处置基本到位**：v2 已把推荐案改为 **D 零字节**（不改 AD-002 任何字节），§4.1 如实写明 A 案的实测代价，段内「§7 继续成立」的全称句已限定为「§7 ② 继续成立」，P2-2/P2-3/P2-4 逐条落到文字上。**方向与内容可以接受**。

两条 P1 **都不是架构语义问题，而是证据/留痕问题**，且都很小：

1. **E-PROPOSAL pin 的 `commit` 列没跟着换**（sha256 已更新为 v2，commit 仍是 v1 的 `da20bd87a`）→ 该 (commit, sha256) 组合**不可联合复核**；`check.ps1` 只校验字段格式/路径存在，**只有评审能发现**（P1-1）。
2. 本提交 `26feb784e` **越过 FEA-GOV-2 的 `allowed_paths`** 修改了 `doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md`（§6 状态行，1 行），且**未在 AD-003 §8 变更记录留痕** → 已收口 ADR 的字节链（被审 `0940a41b` → 收口 `712d3c9d` → 现 `dd4032b7`）不可追溯（P1-2）。改动内容本身是正确的（正是 r1 观察项），只需要补留痕与授权面说明。

| r1 finding | 等级 | 处置 | 说明 |
|---|---|---|---|
| **P1-1** A 案 §7 断言不完整 | P1 | **✅ 已处置** | 改推荐 D；§4.1 写明 A 案代价；段内改为「§7 ② 继续成立；§7 ① 与 §2:28 配方需扩展为去两段追加区」 |
| P2-1 缺 D 零字节案 | P2 | **✅ 已处置** | §3 补 D 行，做法/字节影响=无/风险/评价齐全且准确 |
| P2-2 §4 ① 漏「自动」 | P2 | **✅ 已处置** | 已改「**不自动**迁移、**不自动**删除；用户显式盘点后可释放，见 AD-003 §3.1 第 3 条」 |
| P2-3 清单分支/`A` 歧义 | P2 | **✅ 已处置** | C1 改为「D / A / B」选择；C2/C4 均有分支；`R` = 全部按推荐；C1 影响列已披露 A 案代价 |
| P2-4 §6 缺 check.ps1/numstat | P2 | **✅ 已处置** | D 路径与 A/B 路径均补 `check.ps1` 复跑；A 案补 `--numstat = 6 0` 与 `:8-11` 横幅区 0 变化 |
| P2-5 Task 卡 AC1 表述 | P2 | **⚠️ 部分** | AC1 已改写为四案 + 推荐 D + A 案代价 ✅；**AC2 仍写「支持 `A` 一键回复」**（提案已改 `R`）→ 新 P2-2 |

---

## 2. r1 findings 逐条核对（明细）

### P1-1（原唯一阻断项）— ✅ 已处置

| r1 要求 | v2 实际 | 判定 |
|---|---|---|
| 改推荐 D 零字节 | §3 `:37` 新增 D 行「**D（R-1 复核推荐）零字节**：不改 AD-002；由用户裁决 + C-01b 条款（SC-07/SC-01）确立解释口径」；§4 `:41` 开头即「**D 案（推荐）**：不改 AD-002 任何字节」；C1 `:62` 推荐 = **D**；§6 `:71` 单列「**若选 D（推荐）**：不改 AD-002 任何字节」 | ✅ |
| §4.1 如实写明 A 案代价 | `:54-56` 新增 §4.1：「A 案会在 AD-002 `:31` 后新增**第二处**追加区，使 AD-003 已冻结的两句描述失真…若选 A，必须同步登记『§2:28 复原配方改为去两段追加区』，并按 AD-003 §7 ③ 重做 AD-002 的三口径陈述（需 AD-003 再修订/再 pin）」 | ✅ 准确（与 r1 P1-1 的推断一致） |
| 删/限定段内「§7 继续成立」全称句 | `:49` 现文：「追加不改写任何原有行，**§7 ② 继续成立**；但 §7 ① 与 §2:28 的『去横幅即原 blob』配方需扩展为『去两段追加区』——见 §4.1」 | ✅ 已限定并给出指针 |

> 核对：提案仍保留 A 案的 6 行 diff 文本（`:43-50`）作为「若选 A」的备选，属于合理的方案完整性，不是回退推荐 ✓。

### P2-1 — ✅ 已处置（有残留标签，见新 P2-1）

- §3 表新增 D 行，字节影响「**无**」、风险「无（解释不落在被引用文档正文）」、评价「**更推荐**：完全规避 A 案的 §2:28/§7① 配方漂移（见 §4.1）」 —— 与 r1 建议一致 ✓。
- **残留**：A 行的方案名仍是「**A（推荐）纯追加**」（`:34`），而 D 行是「更推荐」、C1 推荐 D → 同一表格里出现两个「推荐」，见新 P2-1。

### P2-2 — ✅ 已处置

- `:46` 现文：「① 既有 Managed Copy 数据**继续**按既有读取路径工作（**不自动**迁移、**不自动**删除；用户显式盘点后可释放，见 AD-003 §3.1 第 3 条）」—— 与 AD-003 §3.1 第 1/3 条完全对齐 ✓。

### P2-3 — ✅ 已处置

- `R` 简写：`:67`「直接回 `R` = 全部按推荐（即 C1=D、C3=是、C2/C4 无需回答）」✓ 无歧义（不再用 `A`）。
- 分支：C2 `:63`「选『是』→ DSH 需重开 AD-003 修订 Task；选『否』→ 回退到 D」；C4 `:65`「选『否』→ 该句删除，契约歧义改由 C-01b SC-01 单独承担」✓。
- C1 影响列 `:62` 已披露 A 案代价（「选 A 则必须接受 §4.1 的配方扩展并重做 AD-003 三口径；选 B 则 §7 ② 也失效」）✓。

### P2-4 — ✅ 已处置

- D 路径 `:71`：「不改 AD-002 任何字节；只更新 `doc/00_INDEX.md` 的 AD-002 行注解与 C-01b 冻结条件 ③ 为满足，然后 `check.ps1` 复跑」✓。
- A/B 路径 `:80` 新增 step 6：「运行 `pwsh -NoProfile -File tools/governance/check.ps1` 复跑（改动权威面后为必需）；A 案须 `git diff --numstat` 为 `6 0` 且 `:8-11` 横幅区 0 变化」✓。

### P2-5 — ⚠️ 部分处置

- **AC1 ✅**：Task 卡 `doc/tasks/FEA-GOV-2.md:40` 已改写为「① 四案对比（D 零字节 / A 纯追加 / B 改 `:28` / C 改哨兵），含字节影响与风险；② 推荐案（r1 复核后改为 **D 零字节**…）；③ 若选 A 的精确 diff 与已知代价（§4.1 的 AD-003 §2:28/§7① 配方漂移）」—— 与推荐方案一致 ✓。
- **AC2 ❌ 未同步**：同文件 `:41` 仍写「C1–C4 四条，每条含推荐与影响，**支持 `A` 一键回复**」，而提案已改为 `R` → 新 P2-2。

---

## 3. Findings

### P1

#### P1-1 — E-PROPOSAL 证据 pin 的 `commit` 列未随 v2 更新，(commit, sha256) 不可联合复核

- 位置：`doc/tasks/FEA-GOV-2.md:60`（Canonical Evidence 行）。
- 现文：`| E-PROPOSAL | AC1/AC2 | doc/plan/FEA-AD002_AMENDMENT_PROPOSAL.md | da20bd87a | 5255dfa8… | CANONICAL |`
- 实测：
  - `26feb784e:doc/plan/FEA-AD002_AMENDMENT_PROPOSAL.md` 的 LF blob SHA-256 = `5255dfa837cc54711d560b725f247bed0ed52ab0c9276c0056ec8f5a6e1c310b`（85 行，blob `a328aee40b`）= pin 的 sha256 ✓；
  - `da20bd87a:doc/plan/FEA-AD002_AMENDMENT_PROPOSAL.md` 的 sha256 = `621b55c656fe6ffa26b16d05b5aed72082e4dbc960891f8fac058ec8641f7e80`（v1，60 行）≠ pin 的 sha256。
  → 按 pin 的 (commit=`da20bd87a`, sha256=`5255dfa8…`) 去取字节，**取不到**该 sha256 对应的文件；证据链在当前 reviewed_head 处不可复核。
- 惯例佐证：v1 的 pin 是先写 `(见提交)` 占位、再由 `d58f8a781`（"回填 FEA-GOV-2 pin commit"）改为 `da20bd87a` 的 —— 即 `commit` 列的语义就是「包含该 sha256 字节的提交」。v2 只改了 sha256，漏了回填。
- 为何评审必须拦：`check.ps1:661-678` 只校验 evidence 行的列数、路径存在、`class` 合法、`commit` 格式（`^[0-9a-fA-F]{7,40}$`）与「至少一个 pin」——**不校验 commit 与 sha256 是否互相吻合**，机械检查会 PASS。
- 建议：把 `commit` 回填为 `26feb784e`（或下一步提交后再回填，沿用 v1 的「回填 pin commit」惯例），并在 Closeout 前确保 pin 的 (commit, sha256) 可被第三方 `git cat-file` + SHA-256 复算通过。

#### P1-2 — 提交越过 allowed_paths 修改已收口 ADR（AD-003 §6），且未在 AD-003 §8 留痕

- 位置：`26feb784e` 的 `doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md`（`index 712d3c9d1..dd4032b70`，`@@ -137,7 +137,7 @@`，1 行）。
- 事实：
  1. 改动内容 = §6 `:140` 的状态行，由「状态 `ADDRESSED_PENDING_R2`：在 Codex 对新 hash 复审通过前…」改为「状态 **`SATISFIED`（2026-11-01）**：r2 独立复核通过…」——**内容正确**，正是 r1 报告 §4「观察」指出的遗留矛盾。
  2. **但**：`doc/tasks/FEA-GOV-2.md:21-27` 的 `allowed_paths` 不含 `doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md`（该项在 `doc/tasks/FEA-GOV-1.md` 的 allowed_paths 内，而 FEA-GOV-1 已完成）；本提交把它作为 FEA-GOV-2 的一部分提交，写域越界。
  3. **AD-003 §8 变更记录没有对应行**：现有末两行是 `:155`（2026-11-01 G-REVIEW 收口，属更早一次改动 `0940a41b`→`712d3c9d`）与 `:156`（2026-10-31 r2）；本次 `712d3c9d`→`dd4032b7` 无记录。
  4. AD-003 被审 hash 链现为：FEA-GOV-1 复核 `0940a41b` → G-REVIEW 收口 `712d3c9d` → 现 `dd4032b7`；第三方若按 FEA-GOV-1 报告 pin 复核会得到不匹配，且无从得知最后一次改动是什么。
- 影响：已收口（`G-REVIEW: SATISFIED`）的冻结 ADR 出现**未登记的字节变更**；虽不影响 AD-002/C-01b 的任何结论，但削弱本项目最看重的字节可追溯性，且这类漂移会累积。
- 建议（三小步，可一次提交完成）：
  1. AD-003 §8 补一行：`| 2026-11-01 | §6 状态行收尾修正（ADDRESSED_PENDING_R2 → SATISFIED 的重复陈述对齐），不涉语义 | [FEA-GOV-2 r1](../reviews/FEA-GOV-2-review.md) §4 观察 | `；
  2. FEA-GOV-2 卡 Closeout 记录该改动的性质（跨 Task 治理修复）+ 在 `allowed_paths` 补 `doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md`（或注明「经 DSH 事后授权」）；
  3. 在 AD-003 或 FEA-GOV-1 报告附近登记新被审 hash（`dd4032b7`）并说明「本次仅状态行、语义未变」，使 hash 链可读。

### P2

#### P2-1 — §3 的 A 行仍标「（推荐）」，与 D「更推荐」+ C1 推荐 D 冲突

- 位置：提案 `:34`（`| **A（推荐）纯追加** |`）↔ `:37`（D 行「更推荐」）↔ `:62`（C1 推荐 = D）。
- 影响：用户只会扫表头与「推荐」字样，同一表格里两个「推荐」会让 C1 的推荐值显得自相矛盾。
- 建议：A 行改为「**A 备选（原推荐）纯追加**」或「A 纯追加（v1 推荐，现降为备选）」。

#### P2-2 — Task 卡 AC2 仍写「支持 `A` 一键回复」，提案已改为 `R`

- 位置：`doc/tasks/FEA-GOV-2.md:41` ↔ 提案 `:67`。
- 建议：同步为「支持 `R` 一键回复（全部按推荐）」。

#### P2-3 — Task 卡 `allowed_paths` 缺 `doc/reviews/FEA-GOV-2-*.md`

- 位置：`doc/tasks/FEA-GOV-2.md:21-27`。
- 事实：本 Task 已产出 `doc/reviews/FEA-GOV-2-review.md`（r1）与 `doc/reviews/FEA-GOV-2-r2.md`（本报告），且 `26feb784e` 已把 r1 报告纳入提交；但 `allowed_paths` 未列 `doc/reviews/FEA-GOV-2-*.md`。对照：`doc/tasks/FEA-GOV-1.md` 的 allowed_paths 有 `doc/reviews/FEA-GOV-1-*.md`。
- 建议：补该行，避免 Review 产物在账面上属「越界写」。

#### P2-4 — D 案执行留痕未写明：用户裁决载体 + C-01b 条件③「修订」措辞

- 位置：提案 `:71`（§6 D 路径）↔ `doc/plan/FEA-C01b_STORAGE_CONTRACT_DRAFT.md:124`（条件③「用户确认 AD-002 的**责任表与哨兵口径**修订（`Managed Copy` 行 + 顶部横幅归口）」）。
- 事实：D 案**没有修订** AD-002 正文，只有用户对「零字节解释」的确认；而 C-01b 条件③ 的文字写的是「…修订」。若直接把它标为「满足」，账面上与条件③ 的表述不符；且用户 `R` 回复本身需要一个**裁决记录落点**（提案 §6 D 路径只写 INDEX 注解 + 条件③，未指定裁决记录的承载文件）。
- 建议：D 路径补两步——① 把用户的 D 确认（日期 + 结论）登记为一条裁决记录（建议落在 C-01b 依据链或单独治理记录，并写明「零字节、不改 AD-002」）；② 在 C-01b 冻结时把条件③ 表述改为「用户确认 AD-002 责任表口径（零字节解释方案）与哨兵口径」，或在 C-01b 冻结记录中注明该条件以零字节方式满足。

---

## 4. 观察（不计入 findings）

- AD-003 §8 的行序现为 `:154`（2026-10-31 初版）、`:155`（2026-11-01 收口）、`:156`（2026-10-31 r2）—— 11-01 行插在 10-31 r2 行之前，时间顺序不单调；建议下次编辑 AD-003 时把 11-01 行移到末尾（属排版，非语义）。
- 提案 v2 相对 v1 的增量：`+20 / −10`（`da20bd87a..26feb784e`），集中在 §3 表、§4/§4.1、§5 清单、§6 执行动作 —— 未触碰「问题」「硬约束」两节，与 r1 建议的范围一致 ✓。
- 提案 `:26`（硬约束 1）只描述「改写 `:28`/`:4` 会使 §7 声明失效」，未提「追加会削弱 §2:28 配方」；该点已由 §4.1 单独承接，逻辑闭环 ✓，无需重复。

---

## 5. 独立性声明

- 我以 `c01b-reviewer`（Agent Teams **durable teammate**）身份出具 r2，`reviewer_kind: subagent`，独立上下文；r1 亦由我出具（如实披露）。
- **未参与**该提案撰写（作者 = DSH）、未参与 AD-003 / AD-002 / ADJ-001 / 方案文本撰写、未参与 `src/**`、`apps/**` 任何实现。
- 本轮**只读**：唯一写入为新建本报告；未修改提案 / Task 卡 / AD-003 / AD-002 / STATUS / PLAN / INDEX；未 `git add`/`commit`/`push`；未触碰真实数据根。
- **工作树状态记录**：报告落盘前 `git status --porcelain` 为**空**；复核期间 main 由 `26feb784e` 前进到 `85b78dce8`（仅 `doc/handoffs/NIGHT-SHIFT-2026-11-01.md` +3 行），已核对提案 / Task 卡 / AD-003 在两者 blob **相同**。
- 所有事实均附可复核命令结果；r1 引用仅用于对照「原要求是什么」，本轮判定均重新取证（含 v1 pin 回填惯例、AD-003 diff、pin 的 commit↔sha 交叉复算）。

---

## 6. NOT_RUN

- 未运行 `pytest` / `dotnet test` / 任何构建。
- 未运行 `tools/governance/check.ps1`（只读其脚本以确认证据 pin 校验范围；PASS 须 DSH 执行）。
- 未执行提案 §6 的任何一步（提案未获用户确认，本轮只读）。
- 未验证 `origin` 远端历史细节（仅核本 Task 两提交：`26feb784e` 属本地未推送链，local ahead）。
- 未审 `doc/REBASELINE_PLAN.md` / `STATUS.md` 在本 Task 的改动是否与预算一致（不在本 r2 范围）。
- 未审 AD-003 的完整语义（其独立复核见 `doc/reviews/FEA-GOV-1-ad003-review.md`）；本轮只核本次 1 行改动与其留痕。

—— 报告结束（`verdict: changes_requested`，P0×0 / P1×2 / P2×4；r1 处置：P1 已处置 1/1，P2 已处置 4/5、部分 1）。
