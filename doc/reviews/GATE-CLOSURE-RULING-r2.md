---
document_id: GATE-CLOSURE-RULING-r2
kind: independent_review
task_id: FEA-GOV-13
round: 2
scope: very-narrow（只核 task-25 的 P1×2 处置 + 6 处核对 + 残留扫描）
reviewer: c01b-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams durable teammate task-26（独立上下文；未参与 v2 裁定与 C-04b/C-06 修订）"
reviewer_independent: true
reviewed_by_implementer: false
predecessor: GATE-CLOSURE-RULING-review（r1：changes_requested，P0×0 / P1×2 / P2×5）
reviewed_head: 1a6c8e489
reviewed_head_full: 1a6c8e4896a6000e35e9a76363da84b3f43aefc9
reviewed_head_note: "复核期间 HEAD 未前进（HEAD == reviewed_head == 1a6c8e489）"
reviewed_documents:
  - doc/plan/GATE-CLOSURE-RULING-2026-11-01.md（v2，121 行）
  - doc/plan/FEA-C04b_DELETE_PROTOCOL_DRAFT.md（129 行，v5）
  - doc/plan/FEA-C06_SOURCE_AUTH_DRAFT.md（88 行）
reviewed_sha256:
  doc/plan/GATE-CLOSURE-RULING-2026-11-01.md: 01ec4fb65fffa186357d679eef2cb667172d1404e0c51ae7dc9c822d28b11fbf
  doc/plan/FEA-C04b_DELETE_PROTOCOL_DRAFT.md: e0d5b1b7c6fc13ffc660cc27109ba4aaf8fae8bc29888d4160f55ad948eca634
  doc/plan/FEA-C06_SOURCE_AUTH_DRAFT.md: 5a193e9b54fa17ef6dcefdf9b8f73204dcc4354aa4e9a16c6fcc275eb5a8545c
reviewed_sha256_basis: "HEAD 的 LF blob（由 1a6c8e489 引入/更新）"
baseline: "doc/design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md §13.2 `:762-771` · ADJ-001 `:10`/`:92`/`§9 :128` · AD-003 §5 `:128` · doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md §5.11.5 `:774-803` · FEA-C09 `:66`（条件表）"
repository: G:/CODEX/New Manga
source_branch: main
verdict: approved
p0_count: 0
p1_count: 0
p2_count: 6
p2_note: "6 条均为非阻断（裁定 v2 的两处文字残留、C-04b 变更记录顺序、C-06 缺 v4 变更记录、C-06 分担归属不精确、v2 前版自链接），不影响 6 处判定的正确性"
checkps1: "PASS（3 warnings），EXIT=0，本次实跑"
captured_at: 2026-11-01T08:48:18+08:00
captured_by: c01b-reviewer
---

# 独立复核 r2（极窄面）：Gate 阻塞口径裁定 v2 + C-04b/C-06 修订

**本报告不是** 冻结动作、不释放任何 Task，也不构成执行授权。本轮只核 r1 的 2 条 P1 处置、6 处指定项，并按任务要求**抓残留旧口径**。

## 1. 结论

**verdict：`approved`（P0 × 0 / P1 × 0 / P2 × 6 非阻断）。**

**两条 P1 已按 r1 的替代路径正确落地**——这是我本轮最关心的部分：

- **P1-1 → R-1′ 正确**：v2 `:51-66` 明确「**不关闭任何 Gate**」（`:53`），§4 状态表 `:99` 写「`G-DELETE-CONTRACT` / `G-CONTRACT` | **保持 OPEN** | 状态真实」；C-04b 条件③（`:118`）与 C-06 条件③（`:80`）都改成「**不再构成阻塞**」而非「关闭」，并且都写明「Gate 保持 OPEN、本单冻结不改变 Gate 状态」✓。**C-09 不会提前解锁**：其条件（`FEA-C09_DELETE_BACKUP_MIGRATION_DRAFT.md:66`）仍写「`G-DELETE-CONTRACT` 关闭（删除语义）+ `G-CONTRACT` 关闭」——两 Gate 既保持 OPEN，该条件不满足 ✓。
- **P1-2 → R-2′ 正确**：C-04b §2.4 的「冻结顺序」句（`:99`）已改为「C-04b 冻结只冻**结构与码表**；M2-C1 §5.11.3 表 + 两个 ErrorView 的**字节修订**由**独立 Task**（**不得并入任何删除实现 Task**）在**释放任何删除实现之前**完成并复核；复核须含**负向对照**：未扩展 M2-C1 时新码必须被 host 投影拒绝」✓；条件⑤（`:120`）同步 ✓；§4（`:112`）已改为「`G-DELETE-CONTRACT` **不阻塞本单**」，旧句「须在 Gate 关闭后冻结」已删 ✓。
- **残留扫描（任务重点）**：我在 C-04b 全文检索 `Gate 关闭 / 关闭后 / 先扩 / 最后 C-04b / 紧接 / 实现前置`——**没有旧口径残留**（命中的 `:97`/`:99`/`:120`/`:128` 均为新文本或变更记录中的「已删」描述）✓。**但**在别处抓到 1 处同类残留（v2 `:30` 仍用现在时描述「条件③要求关闭」）+ 5 处文字/记录类瑕疵，见 §3。

| # | 核对项 | 结果 |
|---|---|---|
| 1 | P1-1：R-1′ 不关闭 Gate；两契约条件③改「不阻塞」；C-09 不提前解锁 | **✅ 到位** |
| 2 | P1-2：C-04b §2.4 冻结顺序 + 独立性 + 残留扫描 | **✅ 到位（C-04b 无残留）** |
| 3 | v2 是否残留 v1 错误主张（投影/同步关闭/机制上无法生效） | **✅ 无主张残留**（仅历史对照） |
| 4 | C-04b §5 ③⑤ 与 §2.4 三处口径自洽 | **✅ 自洽** |
| 5 | C-06 条件③「D05 授权面子集」表述 | **部分准确**（子集判断成立；分担归属不精确 → P2-5） |
| 6 | `check.ps1` PASS / 无 push / 工作树干净 | **✅ 通过** |

---

## 2. 6 处核对明细

### 1（P1-1）R-1′ 不关闭 Gate —— ✅

- v2 `:53`：「**不关闭任何 Gate**」；`:56`「C-04b 冻结**不改变 Gate 状态**」；`:59`「**Gate 保持 OPEN** 直至这些落地」；`:99` 状态表两 Gate 均「保持 OPEN」；`:101-103` 还补了「Gate 真正的关闭条件」（D04–D07 每包都有冻结契约或经裁定豁免）——这正是 r1 P1-1 要求的显式重定义 ✓。
- C-04b `:118`（条件③）：「`G-DELETE-CONTRACT` **对 C-04b 不再构成阻塞**（本单只承载 D07；D04/D06 承载契约未冻前 Gate 保持 OPEN，本单冻结不改变 Gate 状态——见裁定 R-1′）」✓。
- C-06 `:80`（条件③）：「`G-CONTRACT` **对 C-06 不再构成阻塞**（本单承载 D05 的授权面子集…Gate 保持 OPEN 直至这些落地——见 R-1′）」✓。
- **C-09 未提前解锁**：`FEA-C09…:66` 仍要求两个 Gate 关闭（该条在条件表中编号为 3，任务描述称「条件②」——编号差异，实质相同）✓。

### 2（P1-2）R-2′ + 残留扫描 —— ✅（C-04b 无残留）

- C-04b `:99` 新冻结顺序句：结构+码表先冻；字节修订由独立 Task、不得并入实现 Task、释放删除实现前完成、含负向对照 ✓。
- C-04b `:120` 条件⑤：「扩展**方案**已冻结在本单 §2.4；**字节修订**由独立 Task 在释放删除实现前完成并复核（含负向对照）」✓。
- C-04b `:112` §4：「…`G-DELETE-CONTRACT` **不阻塞本单**（见 §5 条件③，本单只承载 D07）」——旧句「且 C-04b 须在 `G-DELETE-CONTRACT` 关闭后冻结」已删 ✓。
- **残留扫描结果**：`Select-String` 按 `Gate 关闭|关闭后|先扩|最后 C-04b|紧接|实现前置|5\.11\.3 表` 全文件检索，仅命中：
  - `:97`（§2.4 扩展点表的「§5.11.3 表」行，正常）；
  - `:99` / `:120`（新文本）；
  - `:128`（变更记录 v5 行，描述「§4 删『须在 Gate 关闭后冻结』」——历史记录，正常）。
  → **C-04b 内无旧口径残留** ✓。

### 3（v1 错误主张残留）—— ✅ 无主张残留

- 「投影」：仅 `:17`（「host 投影未接线」——UI 投影的本义，非 v1 主张）与 `:112`（「v1 的『投影』结论被误当事实 | 本 v2 已删」）——均为合法用法/历史对照 ✓。
- 「同步关闭」：仅 `:15`（v1 主张对照行）与 `:47`（「v1 的『同步关闭』是…错误」）✓。
- 「机制上无法生效」：仅 `:17`（v1 主张对照行）✓。
- 结论：**v2 正文无 v1 错误主张的当代表述** ✓。

### 4（C-04b 三处自洽）—— ✅

- §2.4 `:99`（结构/码表先冻；字节修订独立 Task + 负向对照 + 释放前）↔ 条件③ `:118`（Gate 不阻塞、不改状态）↔ 条件⑤ `:120`（方案已冻、字节修订为释放前置）——三处指同一件事、无互相矛盾 ✓。

### 5（C-06 条件③「D05 授权面子集」）—— 部分准确（P2-5）

- 「子集」判断成立：C-06 §2 覆盖 `SourceAccessRegistry`（持久身份/授权分离）、`source-read` grant（scope=SourceId/version/entry/rendition、有效期 ≤300s）、4 条命令、5 条安全约束——确属 D05（`:768`）「持久身份与授权分离 / scope·version / 授权面」的子集 ✓。
- 「分担」归属部分不成立：
  - **lease**：AD-003 `:89/:93` 与 C-01b `SC-25/SC-29/SC-31` 均以「稳定读取 lease + digest」承载 ✓（C-01b 已冻结）；
  - **缓存边界/资源上限**：C-06 §2.2 的 `budget{maxBytes, maxDecodeBytes}` 就是它，**不应**列为「由 C-01b、C-09 分担」；
  - **重定位/同步、容器页映射**：在 C-01b / C-09 全文检索**未见承载条款**（AD-003 `:133` 仅把它们列为「G-CONTRACT 关闭前 blocked」的 Source 线事项）→ 归给「C-01b、C-09 等」缺证据。

### 6（治理）—— ✅

- `check.ps1` 实跑：`Governance check: PASS (3 warnings)`，EXIT=0（warning 既有：7 非终态 Task、`STATUS.md` 3185 B / 33 行、`REBASELINE_PLAN.md` 6598 B / 57 行）。
- `origin/main..HEAD` = 199 提交（**未 push**）✓；工作树干净（本轮唯一写入为新建本报告）✓。

---

## 3. 新增问题（P2 × 6，均非阻断）

#### P2-1 — v2 `:21` 标题残留越南语「còn」

- 位置：v2 `:21`「## 1. 问题（**còn** 成立）」。
- 建议：改为「（仍成立）」或「（继续成立）」。

#### P2-2 — v2 `:30` 用现在时描述已修订的「条件③要求关闭」（残留旧口径）

- 位置：v2 `:30`「而 C-04b 的条件③要求 `G-DELETE-CONTRACT` 关闭、C-06 的条件③要求 `G-CONTRACT` 关闭。」
- 事实：同一提交里 C-04b `:118` 与 C-06 `:80` 已被改为「不再构成阻塞」——该句现在时读起来像当前仍要求关闭，与修订后的契约矛盾。
- 建议：改为「**修订前**，C-04b 的条件③要求…；C-06 的条件③要求…（本 v2 已改为『不阻塞』）」。

#### P2-3 — C-04b 变更记录顺序错乱（v5 在 v2 之前）

- 位置：`FEA-C04b_DELETE_PROTOCOL_DRAFT.md` `:127` 建立、`:128` v5、`:129` v2。
- 问题：v5 被插在 v2 之前，时间序倒置；读者按行读会先看到最新变更。
- 建议：把 `:128` 的 v5 行移到表尾（`:129` 之后），恢复 建立 → v2 → v5 顺序。

#### P2-4 — C-06 缺 v4 变更记录（§5 ③ 已改但未记录）

- 位置：`FEA-C06_SOURCE_AUTH_DRAFT.md` §6 `:84-88`——变更记录**只有「建立草案」一行**；文件已被修订（§5 条件③ 改为「不阻塞」）但无对应行。
- 对比：C-04b 同批修订有 v5 行（`:128`），C-06 缺；任务说明称「变更记录 v4」与文件实际不符。
- 建议：补 v4（或相应版本号）行，记录「条件③ 改『G-CONTRACT 对 C-06 不再构成阻塞』（Gate 保持 OPEN，见裁定 R-1′）；D05 分担表述为授权面子集」。

#### P2-5 — C-06 条件③ 分担归属不精确（见 §2-5）

- 位置：`FEA-C06_SOURCE_AUTH_DRAFT.md:80`。
- 建议：把「重定位/同步、容器页映射」改为「**未起草/待分配的契约**」或指向具体条款；把「缓存边界」从分担列表移出（它由 C-06 自身 `budget` 承载）；lease 保留归 C-01b（SC-25/29/31）并写明条款号。

#### P2-6 — v2 `:7`「前版：[v1]」链接指向自身

- 位置：v2 `:7`「前版：[v1](GATE-CLOSURE-RULING-2026-11-01.md)」——该路径就是 v2 自身（v1 已被覆盖；`doc/plan/` 下只有这一份 `GATE-CLOSURE-*` 文件）。
- 建议：改为指向历史提交（如 `38e80d150` 的 blob/`git show`），或复制一份 v1 快照到 `doc/reviews/` 之外的归档位置并链接它；否则链接无效且易误读。

---

## 4. 残留项结论（任务重点的直接回答）

- **C-04b 内**：**无残留**——旧口径「须在 Gate 关闭后冻结」「先扩 M2-C1 再冻契约」「由紧接的实现 Task 承载」均已清除，`grep` 只命中新文本与变更记录中的历史描述 ✓。
- **C-06 内**：条件③ 已改 ✓；但**变更记录未同步**（P2-4）、**分担归属不精确**（P2-5）。
- **裁定 v2 内**：两处文字残留（P2-1「còn」、P2-2 现在时旧话术）+ 一处自链接（P2-6）。
- **C-09 内**：条件仍为「两 Gate 关闭」——这是**正确**的（Gate 保持 OPEN，故 C-09 仍 blocked，未提前解锁）✓，无需改。

---

## 5. 独立性声明

- 我以 `c01b-reviewer`（Agent Teams **durable teammate**，`task-26`）身份出具 r2 报告，`reviewer_kind: subagent`，独立上下文；r1 亦由我出具（如实披露）。
- **未参与** v2 裁定撰写、未参与 C-04b/C-06 本轮修订（作者 = DSH），未参与 `apps/**`、`src/**` 任何实现。
- 本轮**只读**：唯一写入为新建本报告；未修改任何文件；未 `git add`/`commit`/`push`；执行的命令为只读 `check.ps1`、`git`/`Get-Content`/`Select-String` 取证。
- **利益披露**：C-04b/C-06 的冻结条件正是本裁定修订对象，我继续对「是否真的解除阻塞而不再虚报 Gate」做保守核对（结论：正确）。
- **工作树状态记录**：报告落盘前 `git status --porcelain` 为空；`reviewed_head == HEAD == 1a6c8e489`。

---

## 6. NOT_RUN

- 未运行程序、未验证 host 投影/新码的运行时行为（无实现，属计划态）。
- 未核 ADJ-001/AD-003 的字节级原文是否在本轮被改动（按任务范围只核三份被审文件；三份 sha256 已记录）。
- 未核 C-08 的协议注册方案（R-2′ 明确排除）。
- 未核冻结矩阵与 STATUS 是否已同步本轮裁定（本轮范围外；建议 DSH 在冻结记录中引用本裁定）。
- 未核远端历史（仅核本地 `origin/main..HEAD` 未 push）。

—— 报告结束（`verdict: approved`，P0×0 / P1×0 / P2×6 非阻断；6 处核对：5 处到位 + 1 处部分，残留仅文字/记录类）。
