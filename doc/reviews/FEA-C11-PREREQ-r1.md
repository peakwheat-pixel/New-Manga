---
task_id: task-12
document_id: FEA-C11-PREREQ-r1
kind: independent_review
reviewer: c01b-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams durable teammate task-12"
reviewer_independent: true
reviewed_by_implementer: false
author: dsh-lead（DSH 主会话，Lead / Architect / Integrator）
base_commit: 170b384e2
reviewed_head: b7018e19b
reviewed_head_full: b7018e19badb3c5c30411f910bb6ac59123266e
reviewed_head_note: "复核期间 HEAD 未前进（HEAD == reviewed_head == b7018e19badb3c5c30411f910bb6ac59123266e）；工作区 clean"
repository: G:/CODEX/New Manga
source_branch: main
scope: "U-09 前置登记（FEA-C11-PREREQ-1）+ C-10 收口一致性：L-1/L-2/L-5 登记准确性、归属候选合理性、不豁免/不释放表述、未越界、checker/pins"
decision: approved
verdict: approved
p0_count: 0
p1_count: 0
p2_count: 5
approval_conditions: >-
  C1（必须）：把 `FEA-C11-PREREQ-1` 置 `approved` 前，须给 AC1/AC2/AC3 行末加 `<<MET>>`（AC3 依据本报告），并给 Canonical Evidence 加至少 1 条真实行；
  否则 `check.ps1 -TaskPath` 会 FAIL（我实测 4 条真实错误：canonical evidence 缺失 + AC1/AC2/AC3 标记缺失）。此为收口机械项，不改变登记内容，故列为本批准的绑定条件而非 P1。
  C2（建议）：同批处置 P2-001/002/003（引用与 AC 补全）与 P2-004（ledger 重生成）。
checkps1: "PASS（2 warnings），EXIT=0；默认与 -TaskPath doc/tasks/FEA-C11-PREREQ-1.md 两路一致（WARN：10 非终态、STATUS 3162 B）"
verifypins: "PASS (all 14)，EXIT=0；14 份冻结契约字节 0 改动"
c10_closeout: "与冻结事实一致（done / integration_commit 170b384e2 / delivery_head 170b384e2 / E-C10-FROZEN 与 E-C10-DRAFT 均指向 ec8fd862…）"
same_defect_check: >-
  本次无 P0/P1。P2-001 是「引用章节/条目张冠李戴」，与我 r4 对 C-10 的 P1-002（引用不实）同类但**程度不同**：
  那里引用指向**不存在/无内容**的记录（自证），这里的引用**指向真实存在但不同编号体系的条目**，内容本身正确，故 P2。
independence_note: >-
  本复核与被审产出为不同上下文（DSH 主会话 vs 独立 teammate），不构成自审；未参与该 Task 的实现/返修，未修改任何被审文件（仅写本报告）。
captured_at: 2026-11-01T19:03:21+08:00
captured_by: c01b-reviewer
---

# Review：U-09 前置登记（FEA-C11-PREREQ-1）r1

## 范围与依据

本 Review 只对 `base_commit: 170b384e2` → `reviewed_head: b7018e19b` 有效。复核全程 HEAD 未前进、工作区 clean。

**实测提交（9 文件 +248/−20）**：`doc/plan/FEA-C11_IMPL_PREREQS.md`（新 31 行）、`doc/tasks/FEA-C11-PREREQ-1.md`（新 76 行）、`doc/tasks/FEA-C10-DRAFT.md`（done 收口 +11/−11）、`doc/plan/FEA-CONTRACT-FROZEN-C10.md`（§1B ⑧ + R4b 留痕 +8/−8）、`doc/reviews/FEA-C10-r4b.md`（我上一轮报告入库 116 行）、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`、`doc/checkpoints/AUTONOMOUS-2026-11-01.md`。**无 `apps/`、`src/`、`tests/`、`tools/` 改动，无用户数据。**

**依据**：用户追加裁决 **U-09**（ADJ「追加裁决」）；保留项原文 **[Gate 裁定 §3](plan/GATE-DELETE-CONTRACT-CLOSURE-2026-11-01.md)（`:38`–`:48`）**；[C-09 冻结记录 §5](plan/FEA-CONTRACT-FROZEN-C09.md)（`:68`–`:70`）；[G-CONTRACT 裁定 §3.3](plan/GATE-CONTRACT-CLOSURE-2026-11-01.md)（`:48`–`:54`，四表 DDL 载体）；方案 §15.6 候选表（`:912`–`:940`）；C-11 冻结契约（只读）。

## Architecture

1. **三项登记齐全且判据可执行**：L-1（四表 DDL）、L-2（M2-C1 字节修订）、L-5（整库恢复独占锁）各有「归属候选 → 前置 → 必须 AC → 证据计划」四列，且每列都有可核对对象（schema pin / 迁移测试、wire 2.12 + 白名单负向对照、fail-closed + 恢复演练含崩溃注入）。**内容与裁定 §3 的 L-1/L-2/L-5 语义一致**（逐条比对见 V-P-3…V-P-5）。
2. **归属候选合理**：L-1 → `FEA-03`/`FEA-02-CORE`/`FEA-13`；L-2 → `FEA-12-CORE`/`FEA-10`/`FEA-13`；L-5 → `FEA-13`/`FEA-12-CORE` —— 三者均落在方案 §15.6 对应的 write_scopes（application/domain/sqlite/ApplicationCore/bootstrap/maintenance/tasks）内，**无越界归属、无遗漏关键候选**。
3. **禁则到位**：「不构成豁免、不构成实现释放；`G-DELETE-IMPL` 仍 OPEN；候选须用户确认；前置未满足不得进入 `in_progress`；不改任何冻结契约字节」——文首状态行、§0 禁则、卡「禁止范围」三处一致，且卡内明写「不写入 C-11 草案」。
4. **C-10 收口与冻结事实一致**：卡 `done` + `integration_commit/delivery_head: 170b384e2`；`E-C10-DRAFT` 已改为冻结字节（commit `170b384e2` / sha `ec8fd862…`）并新增 `E-C10-FROZEN`；Closeout 记「冻结由用户 U-11 授权，超出 AC3 原边界」；`FROZEN-C10` 补了我 R4b 的两条 P2（§1B 第 ⑧ 项 T7、R4b 结论留痕）。
5. **未越界**：14 份 pin 14/14、`doc/plan/` 受 pin 契约 0 改动、无代码改动；`STATUS:7` 已指向非终态 Task（不会触发 `check.ps1:633`）。
6. **5 条 P2（非阻断）**：来源引用章节/条目张冠李戴（P2-001）；L-2 摘要与 AC 漏 C-08 块②的两项（P2-002）；L-5 AC 未覆盖裁定要求的 4 步序列（P2-003）；ledger 的 tracked/untracked 计数陈旧（P2-004）；置 `approved` 的机械前置未完成 + checkpoint 行 7 状态词与卡不一致（P2-005）。

## Verification（逐项，含真实输出）

环境：Windows，`pwsh -NoProfile`，HEAD = `b7018e19b…`，工作区 clean。

| # | 场景 | 实际执行 | 结果 | 证据 |
|---|---|---|---|---|
| V-P-1 | 提交范围 | `git show --name-status` | **PASS** | 9 文件，全为 `doc/**`；`apps/`/`src/`/`tests/`/`tools/` diff 为空 |
| V-P-2 | **三项 × 四列齐备** | 读 `FEA-C11_IMPL_PREREQS.md:15`–`:19` | **PASS** | 表头 6 列（保留项/内容/归属/前置/AC/证据计划）；L-1/L-2/L-5 三行六列全非空，**无「待定」「TBD」** |
| V-P-3 | **L-1 与裁定原文** | 裁定 `:41` ↔ 登记 `:17` | **PASS（内容）/ 引用不精确** | 裁定：「四张表（`source_entries`/`page_bindings`/`source_sync_plans`/`source_operations`）的 DDL 未冻结 → 保留为 Source 线生产实现前置；承载方式与时点见 G-CONTRACT 裁定 §3.3」；登记：「四表 DDL 未冻结；生产实现前置」✓ 语义一致；但**未引** G-CONTRACT §3.3 与 C-14 冻结记录 §5 L-1（见 P2-001） |
| V-P-4 | **L-2 与裁定原文** | 裁定 `:42` ↔ 登记 `:18` | **部分（缺 2 项，见 P2-002）** | 裁定列 4 项：`PrepareRun`/`AcceptRun` + 3 码、`§8 Proposed（未观察）` 小节、`allowedRunErrorCodes` 白名单（C-08 块②）、`TRASH_*` 3 码（C-09 SC-B06）；登记摘要只覆盖后两项 |
| V-P-5 | **L-5 与裁定原文** | 裁定 `:40` ↔ 登记 `:19` | **部分（AC 缺序列，见 P2-003）** | 裁定：「整库恢复**按迁移处理**，实现时**必须持 SC-17 独占维护锁**（停所有写者/Run/lease、staging、校验、commit marker 后才切换）」；登记 AC 覆盖 fail-closed / 恢复后可写 / 崩溃后可判定，**未覆盖 4 步序列** |
| V-P-6 | **归属合理性（§15.6）** | 逐候选核对 write_scopes | **PASS** | `FEA-03` = `src/application/`+`src/domain/`+`src/infrastructure/sqlite/`+ApplicationCore+tests；`FEA-02-CORE` = ApplicationCore；`FEA-13` = sqlite/bootstrap/Host 备份桥；`FEA-12-CORE` = maintenance/sqlite/core_service/managed_storage；`FEA-10` = tasks/pipeline/providers + CoreClient/Host。**三项归属全部落在对应 write_scopes** |
| V-P-7 | 不豁免 / 不释放 | 读文档`:3`/`:9`–`:11`、卡`:36`/`:46`–`:50` | **PASS** | 「本文档**不构成**对 L-1…L-9 的豁免、**不构成**实现 Task 释放；`G-DELETE-IMPL` 仍 **OPEN**」；「前置未满足时…不得进入 `in_progress`」；卡「禁止范围」三条 |
| V-P-8 | 与 C-11 冻结关系 | 读文档§2 `:25`、卡`:49` | **PASS** | 「本登记与 C-11（已冻结的候选表补列契约）**互补**：C-11 管表列口径，本文档管实现前强制前置与 AC」；卡「不改 C-11 冻结契约正文（本文档为独立登记，不写入 C-11 草案）」 |
| V-P-9 | **14 pins** | `verify_pins.ps1` | **PASS** | `PIN AUDIT: PASS (all 14)`，EXIT=0；14 份契约字节 0 改动 |
| V-P-10 | **两路 checker** | 默认 + `-TaskPath doc/tasks/FEA-C11-PREREQ-1.md` | **PASS** | `PASS (2 warnings)` EXIT=0 ×2（WARN：10 非终态、STATUS **3162 B**） |
| V-P-11 | **C-10 卡与冻结事实** | 读卡 `:6`/`:15`–`:18`/`:71`–`:75`/`:97` | **PASS** | `status: done`、`integration_commit: 170b384e2`、`delivery_head: 170b384e2`；`E-C10-DRAFT` 与 `E-C10-FROZEN` 均为 `170b384e2` / `ec8fd862…`；Closeout 记「C-10 已按用户 U-11 冻结…AC3 原文写「本 Task 不冻结 C-10」…」边界说明 |
| V-P-12 | FROZEN-C10 补记（我 R4b 的两条 P2） | 读 `:30` /「复核安排」行 | **PASS** | ⑧「**T7 判据补强**（注明断言输入为视口 DIP 位移而非图像坐标位移）——该项在 R4b 复核中被指出为 §1B 原披露遗漏（R4b-P2-001）」；「R4b 结论：`approved`…冻结提交时 §10 第 2 项所写…为**预告**，本行即为其成立留痕（R4b-P2-002）」 |
| V-P-13 | **ledger 计数** | 磁盘直数 vs ledger | **部分（P2-004）** | 磁盘：terminal **473** / non-terminal **10** / no-status **1** / total **484** —— ledger 三项**全对** ✓；但 `tracked 483`/`untracked 1`/`non-terminal tracked 9` 与实测 `484 / 0 / 10` 不符（生成于 `git add` 之前） |
| V-P-14 | STATUS / PLAN / checkpoint | 读三处 | **部分（P2-005b）** | STATUS:7 = `FEA-C11-PREREQ-1 in_progress`（上一 Task C-10 done）✓；PLAN `:10`/`:11`/`:24` ✓；**checkpoint 行 7 写 `in_review` 而卡为 `in_progress`** ✗ |
| V-P-15 | **置 `approved` 机械可行性（TEMP 模拟）** | 复制卡改 `status: approved` → `check.ps1 -TaskPath` | **FAIL（4 条真实错误）** | `FAIL: 进入 REVIEW/DONE 的 lifecycle v2 Task 必须列出 canonical evidence.`；`FAIL: AC 状态标记缺失或非法…：AC1`/`AC2`/`AC3`（另一条 `失效的本地引用` 为 TEMP 路径伪错误）→ 见 P2-005a + 绑定条件 C1 |
| V-P-16 | 复核期间状态完整性 | `git rev-parse HEAD` / `git status --porcelain` | **PASS** | HEAD 全程未变；工作区仅新增本报告；模拟在 `$env:TEMP`，跑完即删 |

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态 |
|---|---|---|---|---|---|---|
| PREREQ-P2-001 | **P2** | `doc/plan/FEA-C11_IMPL_PREREQS.md:5`（来源行） | 两处引用不精确：①保留项 L-1…L-9 在 Gate 裁定的 **§3（`:38`–`:48`）**，不是 §4（§4 是 Errata 表）；②「C-09 冻结记录 §5（L-1/L-2）」中的 **C-09 §5 L-1 是「K-5 外部记账残留」**（`:68`，内容对应裁定的 **L-3**），**不是四表 DDL**；只有 C-09 §5 的 L-2（M2-C1）与裁定 L-2 是同一项。影响：读者按此行去 C-09 §5 找 L-1 会读到完全不同的条目，登记溯源被削弱 | V-P-3；裁定 `:38`–`:48`；C-09 §5 `:68`–`:69` | 来源行改为：「保留项：Gate 裁定 **§3**（`:38`–`:48`）L-1/L-2/L-5；四表 DDL 另见 **G-CONTRACT 裁定 §3.3** 与 C-14 冻结记录 §5 L-1；M2-C1 另见 **C-09 §5 L-2**」 | open |
| PREREQ-P2-002 | **P2** | `doc/plan/FEA-C11_IMPL_PREREQS.md:18`（L-2 行「内容」与 AC 列） | 摘要只写「`TRASH_*` 3 码与 Run 错误码白名单（C-09 SC-B06）」，**漏裁定 L-2 明确列出的 `PrepareRun`/`AcceptRun` + 3 码 与 `§8 Proposed（未观察）` 小节（C-08 块②）**；且「（C-09 SC-B06）」放在整句末尾，易被读成整条都出自 C-09。影响：若实现 Task 只按本条 AC 收口，可能漏掉 M2-C1 的两个 wire 命令与 §8 小节（前置行虽写「M2-C1 字节修订 Task 完成」，但 AC 是候选卡的实际验收口径） | V-P-4；裁定 `:42` | L-2 内容改为四项全列（`PrepareRun`/`AcceptRun` + 3 码、`§8 Proposed` 小节、`allowedRunErrorCodes` 白名单 = C-08 块②、`TRASH_*` 3 码 = C-09 SC-B06），AC 补「wire 2.12 含两命令 + §8 小节标记为已观察」 | open |
| PREREQ-P2-003 | **P2** | `doc/plan/FEA-C11_IMPL_PREREQS.md:19`（L-5 AC 列） | 裁定 L-5 的实质义务是「**按迁移处理**、持 SC-17 独占维护锁，且**停所有写者/Run/lease → staging → 校验 → commit marker 后才切换**」；登记 AC 只覆盖 fail-closed / 恢复后可写 / 崩溃后可判定，**未把 4 步切换序列写成可断言项**。影响：候选 Task 可能实现"加锁"却漏掉 staging/校验/marker 顺序，恢复中途失败留下半切换状态 | V-P-5；裁定 `:40` | AC 增补：①写信者/Run/lease 全部停止（可观察：恢复期间写入被拒且有原因）②staging 目标路径与校验步骤 ③**commit marker 落盘后才切换**（崩溃注入：marker 前崩溃 → 原库仍可读；marker 后崩溃 → 恢复可续） | open |
| PREREQ-P2-004 | **P2** | `doc/TASK_LEDGER.md:14`–`:16` | ledger 的 tracked/untracked 拆分陈旧：`task files tracked by git 483` / `untracked (drafts) 1` / `non-terminal tracked 9`，实测 **484 / 0 / 10**（新卡已在同一提交入库）。`task files 484` 与状态表（473/10/1）本身正确，故仅是"生成时机早于 `git add`" | V-P-13；`git ls-files doc/tasks/*.md` = 485（484 卡 + README），untracked = 0 | 重新运行 `python tools/governance/task_ledger.py --write` 并核对 settled 值 `484 / 0 / 10`；或在该节注明"生成于入库前" | open |
| PREREQ-P2-005 | **P2（含绑定条件 C1）** | `doc/tasks/FEA-C11-PREREQ-1.md:42`–`:44`（AC 无标记）、`:61`–`:63`（Canonical Evidence 仅占位）；`doc/checkpoints/AUTONOMOUS-2026-11-01.md:27`（行 7） | ①**置 `approved` 会立刻 FAIL**：AC1/AC2/AC3 行末缺 `<<MET>>`（`check.ps1:828`–`:830`），且 Canonical Evidence 只有 `| - | … |` 占位行（"进入 REVIEW/DONE 的 lifecycle v2 Task 必须列出 canonical evidence"）；②checkpoint 行 7 写 `in_review`，卡实为 `in_progress` | V-P-15（实测 4 条真实错误 + 1 条 TEMP 伪错误）；V-P-14 | 置 `approved` 前：AC1/AC2/AC3 加 `<<MET>>`（AC3 依据本报告）；Canonical Evidence 加真实行，例如 `E-PREREQ-DOC \| AC1 \| doc/plan/FEA-C11_IMPL_PREREQS.md \| b7018e19b \| 78d011a332be57f3d185971748aadbae437a28e33c29db2869835d1f1978dce9 \| CANONICAL`；checkpoint 行 7 改 `in_progress`/复核中措辞 | open |

**P0：0。P1：0。** 5 条 P2 全部非阻断；仅 P2-005 附带绑定条件 C1。

> 关于 P2-005 为何不判 P1：卡当前 `in_progress` 与 checker 要求**一致**（默认路 PASS），失败只在"置 approved"之后出现，且是该状态必须补的常规收口标记、由 Lead 的标准流程必然触发并自检；与 WRAP-1 R1 的 P1（Manifest 词表非法属**内容错误**、且要求突破既定范围）性质不同。故列 P2 + 绑定条件。

## 对 Lead 5 项核对要求的答复

1. **L-1/L-2/L-5 登记一致性**：**内容一致**（V-P-3…V-P-5 逐条比对裁定 §3 原文）；**引用不精确**——裁定的保留项在 **§3 不是 §4**，且「C-09 §5 L-1」是 K-5 残留（对应裁定 L-3）而非四表 DDL（P2-001）。属**引用问题、非内容错误**。
2. **归属候选是否合理**：**合理**。三项归属全部落在方案 §15.6 的对应 write_scopes；无越界、无关键候选遗漏（V-P-6）。附带说明：L-1 的 DDL 承载建议以 G-CONTRACT §3.3 为口径（该裁定明确「四表 DDL 仍未冻结，是 Source 线任何生产实现的前置」，且 AD-003 `:117` 承诺 D05 范围冻结），登记的前置表述与之不冲突。
3. **不豁免/不释放/不写入 C-11 正文**：**表述到位**。文档状态行 + §0 禁则 + 卡「禁止范围」三处一致；`G-DELETE-IMPL` 仍 OPEN（STATUS:11）；C-11 互补关系已写明（V-P-7/V-P-8）。
4. **C-10 收口一致性**：**一致**。`done` / `integration_commit: 170b384e2` / `delivery_head: 170b384e2`；`E-C10-FROZEN`（`ec8fd862…`）与更新后的 `E-C10-DRAFT` 同指冻结字节；Closeout 明确「冻结由用户 U-11 授权，超出 AC3 原边界」；`FROZEN-C10` 已补我 R4b 的两条 P2（V-P-11/V-P-12）。
5. **未越界**：**未越界**。9 文件全为文档；14 pins 14/14；`doc/plan/` 受 pin 契约 0 改动；无代码、无用户数据、未 push；`STATUS:7` 指向非终态 Task。

## 结论与后续

**decision：`approved`**（P0 × 0 / P1 × 0 / P2 × 5，全部非阻断）。

**绑定条件 C1（置 `approved` 前必须做）**：AC1/AC2/AC3 行末补 `<<MET>>`（AC3 依据本报告 P0/P1 = 0），Canonical Evidence 增加至少 1 条真实行（示例见 P2-005）。**做完这两项后无需再送审**——我已在 r4b 记录清单里给出可核验值（`b7018e19b` / `78d011a3…`）。

**建议同批（非阻断）**：P2-001（来源引用改正）、P2-002（L-2 四项全列）、P2-003（L-5 AC 补 4 步序列）、P2-004（ledger 重生成）、P2-005b（checkpoint 行 7 措辞）。这四条都不影响本批准结论；建议在置 `approved` 的同一次提交里顺手完成，避免把"引用不精确"带进下一阶段。

**边界**：本报告不构成实现授权（`G-DELETE-IMPL` 仍 OPEN；候选须用户确认）、不构成 push 授权、不构成对冻结契约的任何修改；`FEA-C11_IMPL_PREREQS.md` 是登记文档（非契约、不冻结、不 pin）。

—— 报告结束（`decision: approved`；P0/P1 = 0；P2×5；置 `approved` 附绑定条件 C1）。
