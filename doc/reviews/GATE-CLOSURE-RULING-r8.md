---
document_id: GATE-CLOSURE-RULING-r8
kind: independent_review
task_id: FEA-GOV-14
round: 8
scope: very-narrow（残留扫描、:96/:100 一致性、治理，共 3 处）
reviewer: c01b-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams durable teammate（独立上下文；未参与裁定 v6 与 C-08 修订）"
reviewer_independent: true
reviewed_by_implementer: false
predecessor: GATE-CLOSURE-RULING-r7（r7：changes_requested，P0×0 / P1×3 / P2×3）
reviewed_head: 0cd6d62e9
reviewed_head_full: 0cd6d62e97cd3c52eb1b78e0cd75faf0f0dd2056
reviewed_head_note: "复核期间 HEAD 未前进（HEAD == reviewed_head == 0cd6d62e9）"
reviewed_documents:
  - doc/plan/GATE-CLOSURE-RULING-2026-11-01.md（v6，139 行）
  - doc/plan/FEA-C08_RUN_SNAPSHOT_DRAFT.md（v4，87 行）
reviewed_sha256:
  doc/plan/GATE-CLOSURE-RULING-2026-11-01.md: 3d0c9a67ea0866d66d18bb407ff659ffeae25ec2ffeffc2dbeee026d02778dd5
  doc/plan/FEA-C08_RUN_SNAPSHOT_DRAFT.md: aa118d2829e9654509c92feb7d41ddeb6cc554b30e25f8504ff018a64a4499a9
reviewed_sha256_basis: "HEAD 的 LF blob（由 0cd6d62e9 引入/更新）"
baseline: "doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md §5.5 `:185-226` · §8 `:1097-1130`（`:1097`/`:1101` 保留源码、`:1119` retryable 证据规则、`:1122` 不冻结 taxonomy）· C-04b §2.3/§2.4"
repository: G:/CODEX/New Manga
source_branch: main
verdict: approved
p0_count: 0
p1_count: 0
p2_count: 3
p2_note: "3 条均为非阻断标注项（标题版本号、C-08 :77 措辞对齐、C-08 版本号未升），登记为 K-1…K-3"
checkps1: "PASS（3 warnings），EXIT=0，本次实跑"
captured_at: 2026-11-01T09:44:32+08:00
captured_by: c01b-reviewer
---

# 独立复核 r8（极窄面）：裁定 v6 + C-08

**本报告不是** 冻结动作、不释放任何 Task。本轮只核 3 处：残留、`:96`/`:100` 一致性、治理。

## 1. 结论

**verdict：`approved`（P0 × 0 / P1 × 0 / P2 × 3 非阻断）。**

**3 处全干净，r7 的 3 条 P1 都已真正落地：**

| # | 核对项 | 结果 |
|---|---|---|
| 1 | 残留扫描（`:97`「拒绝」/`:100`「observed 表追加」/ C-08 `:8`「不改冻结契约」） | **✅ 0 残留** |
| 2 | `:96` 与 `:100` 对 §8 落点的描述 | **✅ 完全一致**（都 = Proposed 小节 + `:1119` 例外） |
| 3 | `check.ps1` PASS、无 push | **✅**（PASS 3 warnings / EXIT=0；`origin/main..HEAD` = 214，未 push；工作树干净） |

**逐条对号**：

- **P1-1（`:97` 首句「拒绝」）→ ✅**：现文「未扩 M2-C1 时，3 个新码必须被 host 投影**降级为 `category=unknown`**（不是拒绝）」，与同段「明确写死为『降级』而非『拒绝』」一致 ✓；段内保留的「会被拒」「不是拒绝」都是**正确否定/描述性**用法，非旧话术。
- **P1-2（`:100` observed 表）→ ✅**：现文「§8 新增「Proposed（未观察）」小节 3 行（**不塞进 `:1109-1117` 的 observed 表**——那表是「已观察到」的记录，新码 0 命中，塞进去会造成假陈述）+ §8 `:1119` 的 retryable 证据规则例外（C-08 三码的 retryable 为**契约级提案值**，实现后由 Core 证据复核）」——与 `:96` 互洽 ✓。
- **P1-3（C-08 `:8`）→ ✅ 真的改了**：现文「本文件是**草案**——**本草案自身不修改任何文件、不改 schema**；其要求修改的 M2-C1 属**冻结契约**，字节修订由前置（b）的独立 Task 执行（见 §5），本草案只冻结『要加什么』」——与前置（b）不再字面矛盾 ✓；变更记录 `:87` 也已把 `P2×3` 更正为 **P2×5** ✓（P2-3 闭合）。

**结论**：R-4 的机制面（host 投影层白名单 + 不重写 code + 负向对照挂白名单）与表述面（§8 Proposed 小节 + `:1119`/`:1122` 例外）都已自洽，负向对照可执行、零新错误码、不改 Core §8。**建议进入 C-08 冻结流程**（U-03 已裁决、C-05/C-04b 已冻结、前置（b）为释放前置——现有冻结条件均已满足或已降级为释放前置）。

---

## 2. 3 处核对明细

### 1（残留扫描）—— ✅

- 裁定 `:97`：首句已是「降级为 `category=unknown`（不是拒绝）」✓；无「必须被拒绝」旧表述。
- 裁定 `:100`：已无「observed 表追加 3 行」；改为「Proposed（未观察）小节 + 不塞进 observed 表 + `:1119` retryable 例外」✓。
- C-08 `:8`：已无「不改冻结契约」；改述为「本草案自身不修改任何文件、不改 schema；M2-C1 属冻结契约，字节修订由前置（b）独立 Task 执行」✓。
- 全文其余 `拒绝` 命中：C-08 `:43`/`:64`（AcceptRun 的拒绝语义，正确语境）、裁定 `:73`（**C-04b 删除线**负向对照「新码必须被 host 投影拒绝」——删除线有封闭 ErrorView，这里正确，非残留）✓。

### 2（`:96` 与 `:100` 一致性）—— ✅

| 项 | `:96`（R-4 第 2 点） | `:100`（块② 定义） |
|---|---|---|
| §5.5 命令表追加 2 行 | ✓ | ✓ |
| 3 码进 §5.5 错误语义段 | ✓ | ✓ |
| §8 Proposed（未观察）小节 3 行 | ✓ | ✓（并注明不塞进 observed 表） |
| §8 例外说明 | `:1119`/`:1122` | `:1119`（retryable 证据规则例外） |
| host `allowedRunErrorCodes` | ✓ | —（在 `:97` 详述） |
| wire minor 2.12 | ✓ | ✓ |

两处描述**无矛盾**（`:100` 是 `:96` 的细化；`:96` 的 `:1122` taxonomy 例外在 `:100` 未重复，但 `:96` 仍是权威清单）✓。

### 3（治理）—— ✅

- `check.ps1` 实跑 `PASS (3 warnings)`，EXIT=0；`origin/main..HEAD` = 214（未 push）✓；工作树干净 ✓。
- 被审 blob：裁定 `3d0c9a67…`（139 行）、C-08 `aa118d28…`（87 行）。

---

## 3. 新增问题（P2 × 3，非阻断）

| # | 位置 | 问题 | 建议 |
|---|---|---|---|
| **K-1** | 裁定 `:1` | 标题仍写「· **v3**」，状态 `:3` 已是 **v6**（本轮 P2-2 只改了状态行，标题未改） | 标题改 v6 |
| **K-2** | C-08 `:77` | §8 例外只写「taxonomy 例外说明」，未写 `:1119` 的 retryable 证据规则例外（与裁定 `:96`/`:100` 的合称略不对齐） | 改为「§8 taxonomy + `:1119` retryable 证据规则例外」 |
| **K-3** | C-08 `:87` | 文件在 r7 又改过一次（`:8` 改述），但变更记录仍标 v4、未升 v5（该改述描述已写在 v4 行内，可接受） | 可在 v4 行标注「含 r6/r7 两次处置」，或升 v5 |

三条均不影响可执行性，**不构成冻结阻断**，建议在冻结提交时顺手处理。

---

## 4. 独立性声明（简）

- 以 `c01b-reviewer`（Agent Teams durable teammate）身份出具 r8，独立上下文；本裁定的 r1–r7 复核亦由我出具（如实披露）。未参与裁定 v6 / C-08 撰写与实现。
- 本轮只读：唯一写入为新建本报告；未修改任何文件；未 commit/push；命令为只读 `check.ps1` 与 `git`/`Get-Content`/`Select-String`。`reviewed_head == HEAD == 0cd6d62e9`。

---

## 5. NOT_RUN

- 未运行程序/pytest（§8 语义、残留扫描均为静态原文/检索结论）。
- 未核 host 侧是否已有 `allowedRunErrorCodes` 类实现（按 M2-C1 文本与裁定描述判断）。
- 未核 §8 在 Core/Tauri 两侧实现。
- 未核 M2-C1 自身冻结记录/UNFREEZE 载体。
- 未核 C-08 冻结提交本身（本轮只核裁定 + C-08 文本）。

—— 报告结束（`verdict: approved`，P0×0 / P1×0 / P2×3；3 处全 ✅）。
