---
task_id: FEA-DOC-RECONCILE-1
reviewer: 独立上下文 fresh subagent（DSH 派发；子 agent 会话 `ffb8966c-75c6-4e24-bf59-c279efc12f8e`；父会话 `session-c08ea2ac-cbcf-47ac-a7a9-0e15254b3fa5`）
reviewer_kind: subagent
review_independence: 未参与该 Task 的实现、返修、证据生成；只读审查，未改任何被审文件
author: dsh-lead（DSH）
base_commit: 9b0683822
reviewed_head: 4d64bfdcb
delivery_commit: d91dbe444
decision: changes_requested
counts: P0=0 / P1=2 / P2=4 / P3=3
---

# Review：FEA-DOC-RECONCILE-1（FEA 线文档对账）

## 审查者身份与来源

- 审查者：**独立上下文 fresh subagent**，子 agent 会话 `ffb8966c-75c6-4e24-bf59-c279efc12f8e`（父会话 `session-c08ea2ac-cbcf-47ac-a7a9-0e15254b3fa5`），**未参与**该 Task 的实现、返修或证据生成。
- 被审 head：`4d64bfdcb`（Handoff 提交）；对账实现提交 `d91dbe444`；基线 `9b0683822`。
- 审查方式：**只读**。用 `git show` / `git diff` / `git show <head>:<path>` 读取被审 head 的对象字节，`Select-String` 定位证据行；按任务要求**只跑** `tools/governance/check.ps1` 与 `tools/governance/verify_pins.ps1`，**未跑** pytest / dotnet 全量。
- 本报告为唯一写入文件；未 commit、未改其他文件、未 push。

## 范围与方法

核对 7 项对账事实（读原始证据文件的对应行，而非引用链）+ append-only 合规 + 预算与门禁。逐项结果见下表；findings 单列。

## 核对结果表（9 项）

| # | 核对项 | 结果 | 证据路径:行 |
|---|---|---|---|
| 1 | STATUS「四表 DDL 已冻」↔ C-15 / FEA-11-PREREQ-1 / `tests/fea11/test_v8_migration.py` | **PASS**（事实成立；口径可读性见 P2-02/P3-01） | `doc/plan/FEA-CONTRACT-FROZEN-C15.md:43,50-51`；`doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md:52-198`（v7 建 `source_entries`:115/`page_bindings`:146，`:50` 两表留 v8+）；`doc/tasks/FEA-11-PREREQ-1.md:45,65`；`doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md:33,56`；`tests/fea11/test_v8_migration.py:21-22,101` |
| 2 | PLAN `FEA-C11-PREREQ-1` 翻 done（集成 `b7018e19b`）↔ 卡 Closeout | **PASS** | `doc/REBASELINE_PLAN.md:10`；`doc/tasks/FEA-C11-PREREQ-1.md:6,16,80`；`git merge-base --is-ancestor b7018e19b HEAD` → YES |
| 3 | `FEA-GOV-11` done ↔ ADJ 裁决 R/U-04/U-05a/U-05b + 4 份 FROZEN | **PASS**（裁决与冻结件齐备；done 前置见 P1-01，AC3 证据见 P2-04） | `doc/reviews/ADJ-2026-11-01-FEA-DECISIONS.md:15,16,17,18`；`doc/plan/FEA-CONTRACT-FROZEN-C01b.md:31-39`、`-C02.md:34`、`-C03.md:35`、`-C11.md`（均存在） |
| 4 | `FEA-D07-UNBLOCK` AC8 `[x] <<MET>>` ↔ Gate 关闭 | **PASS**（保留口径见 P3-02） | `doc/tasks/FEA-D07-UNBLOCK.md:6,54,89`；`doc/plan/GATE-DELETE-CONTRACT-CLOSURE-2026-11-01.md:14,21,27-30,65` |
| 5 | IMMERSIVE 仅追加、`status` 仍 `closed_with_limitations` ↔ `FEA-07-V2-F11-1` done | **PASS** | `doc/tasks/FEA-07-IMMERSIVE-F11-1.md:128-131`（numstat +5/−0）；`doc/tasks/FEA-07-V2-F11-1.md:6,16,65`；`git merge-base --is-ancestor 5108c6640/f60b2ff50` → YES |
| 6 | `FEA-11-RUN-GRANT-2` 注记 ↔ front matter | **PASS** | `doc/tasks/FEA-11-RUN-GRANT-2.md:3`（title 含「proposed，待依赖」）、`:6,17`；`:145-147`（numstat +4/−0）；`018008989…` 为 HEAD 祖先 |
| 7 | `FEA-02-BRIDGE`「不独立释放」↔ 方案 §15.6 / `FEA-04.md:46` | **PARTIAL**（裁决已写，依据未落 PLAN → P2-03） | `doc/REBASELINE_PLAN.md:11`；`doc/design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md:922`；`doc/tasks/FEA-04.md:46` |
| 8 | append-only 合规（GOV-11/D07 仅 AC 勾选与标记、测试表 `NOT_RUN` 保留；IMMERSIVE/RG2 纯追加） | **PASS**（AC 文句未改；`NOT_RUN` 原样保留；但由此引出 P1-02） | `git diff --numstat 9b0683822..d91dbe444`：GOV-11 5/4、D07 3/2、IMMERSIVE 5/0、RG2 4/0；`doc/tasks/FEA-GOV-11.md:59-61`、`doc/tasks/FEA-D07-UNBLOCK.md:69` |
| 9 | 预算与门禁（`check.ps1` / `verify_pins.ps1`；STATUS/PLAN 字节行数） | **PASS**（3 warnings；pins 18/18；STATUS 2997 B/28 行、PLAN 6985 B/63 行）；台账复算不一致 → P2-01 | `check.ps1` → `PASS (3 warnings)`；`verify_pins.ps1` → `PIN AUDIT: PASS (all 18)`；`verification/FEA-DOC-RECONCILE-1/gates.log:5-6,9,22` |

**Canonical Evidence 逐条复核**：卡内 7 条 EV 的 sha256 与工作树（复核时为 `4d64bfdcb` 内容）**逐条一致**（`doc/STATUS.md` `db73b523…`、`doc/REBASELINE_PLAN.md` `816e6e1d…`、`FEA-GOV-11.md` `ace80357…`、`FEA-D07-UNBLOCK.md` `32386b2c…`、`FEA-07-IMMERSIVE-F11-1.md` `3fa51ead…`、`FEA-11-RUN-GRANT-2.md` `83d15cbd…`、`gates.log` `c5fcd1f7…`）。

## Findings

### P0（0）

无。未发现冻结契约/pin/源码字节被改动（交付 diff 仅 `doc/**` + `verification/**`），`verify_pins` 18/18，7 条 EV 哈希全对；对账的**事实内核**（四表 DDL 已冻、C11 已集成、Gate 已关、GOV-11 输入齐备、BRIDGE 不独立释放）均成立。

### P1（2）

**P1-01｜两张被翻 `done` 的卡未满足 `done` 前置（生命周期硬规则）**
- 文件:行：`doc/tasks/FEA-GOV-11.md:6,16,17,18,19`（另 `:10` `reviewer: null`）；`doc/tasks/FEA-D07-UNBLOCK.md:6,16,17,18,19`。
- 问题：`status` 已置 `done`，但 `canonical_evidence_status: pending`、`resource_closeout_status: pending`、`integration_commit: null`、`delivery_head: null` 全部保持原样（GOV-11 且无 reviewer）。仓库内其它 `done` 治理卡均为 `complete/complete` + 有 `integration_commit`（`FEA-01-FREEZE-1.md:16-20`、`FEA-GOV-10.md:16-20`、`FEA-C11-PREREQ-1.md:16-20`、`FEA-11-PREREQ-1.md:16-20`）。
- 依据：`doc/09_COLLABORATION.md:77`（`done` 仅可在集成、验证与 closeout 全部通过后设置）、`:97`（**`done` 前完成 `canonical_evidence_status: complete` 与 `resource_closeout_status: complete`**）。`check.ps1` 只校验标记存在/自洽（`doc/09_COLLABORATION.md:149-156`），不覆盖本项，故门禁绿不代表合规。
- 影响：交付的两条终态记录自带「未完成证据/未核销资源」的矛盾标注；本轮任务本身是治理对账，该矛盾直接削弱其结论可引用性。
- 建议：任选其一并在卡内写明——(a) 置 `complete` 并把集成提交记为 `d91dbe444`（这两张卡本轮无独立 evidence_dir 产物，需说明依据）；(b) 不强推 `done`，改 `approved` / `closed_with_limitations` 并在 Closeout 写清「AC 已核、生命周期 formalities 未闭合」；同步补 `reviewer`（GOV-11）或记明豁免理由。

**P1-02｜对账卡 AC3 的自设条件未满足却判 `<<MET>>`**
- 文件:行：`doc/tasks/FEA-DOC-RECONCILE-1.md:62`（AC3）↔ `doc/tasks/FEA-GOV-11.md:59-61`。
- 问题：AC3 原文要求「AC1–AC3 标 `<<MET>>` 并引裁决记录；`status: done`；**测试表不再 `NOT_RUN`**」，判词 `<<MET>>`；但被审 head 上 GOV-11 测试表三行仍为 `NOT_RUN`（`:59/:60/:61`，证据列仍「待补」）。同一提交的 Closeout 又自述「测试表 `NOT_RUN` 为 2026-11-01 当时记录，原字节保留」——append-only 处置本身合理，但 AC 文句与交付事实相反，属可机械核对的过度声明。
- 依据：被审 head 字节（`git show 4d64bfdcb:doc/tasks/FEA-GOV-11.md:55-61`）；`verification/FEA-DOC-RECONCILE-1/gates.log` 不覆盖此条。
- 建议：改 AC3 文句为「测试表 `NOT_RUN` 按 append-only 原字节保留，本期不作 PASS 依据」并重判（仍可 MET），或在 AC3 加 deviated 说明；不要保留「不再 NOT_RUN」这一可被证伪的条件。

### P2（4）

**P2-01｜交付的 TASK_LEDGER 在其自身 head 上不可复现**
- 文件:行：`doc/TASK_LEDGER.md:14-16`（`task files tracked by git 558` / `untracked 1` / `non-terminal tracked 12`）。
- 问题：`python -X utf8 tools/governance/task_ledger.py` 在交付 head 复算为 **559 / 0 / 13**。台账按「`git add` 之前」的工作树生成，提交后 `FEA-DOC-RECONCILE-1.md` 已 tracked，故三格数字与交付字节不符。
- 依据：`doc/TASK_LEDGER.md:3` 明示「Generated by `task_ledger.py --write` … Do not edit by hand」；`tools/governance/check.ps1:202-237` 只比 `task files` 与 `non-terminal` 两格，未覆盖 tracked/untracked 三格，故门禁无法发现。
- 影响：一张专门用于「可复算」的台账在交付点不可复算，正是本轮要消灭的缺陷类型；AC8「ledger 重生成 PASS」只在提交前成立。
- 建议：提交后重跑 `--write` 并复跑 `check.ps1`，把两次输出一并入 `gates.log`；或在台账生成步骤后加「提交后重生成」的确定性说明。

**P2-02｜「四表 DDL 已冻」与现行架构权威文档直接冲突，且四表名未在任何本轮产物中落地**
- 文件:行：`doc/STATUS.md:11` ↔ `doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md:128`。
- 问题：STATUS 现称「四表 DDL 已冻（C-15 v7 + FEA-11-PREREQ-1 v8+）」，而 STATUS 自己引为「存储」权威的 AD-003 `:128` 仍写「**边界：四表 DDL 仍未冻结，属 Source 生产实现前置**；未冻结前…**禁止释放 FEA-09/11/12/13 实现**」（FEA-09/11/12 均已 done，该行本就陈旧）。此外本轮产物**没有一处列出四个表名**；仓库内唯一并列四表名的 `doc/plan/GATE-DELETE-CONTRACT-CLOSURE-2026-11-01.md:41`、`doc/plan/FEA-C11_IMPL_PREREQS.md:24`、`doc/plan/FEA-CONTRACT-FROZEN-C14.md:64` 全部仍写「未冻结」，读者按 AC1「四个表名/版本可追溯」去追，会落到三份写着「未冻结」的文件上。
- 依据：C-15 v7 建 `source_entries`/`page_bindings`（`FEA-C15_SOURCE_STORAGE_DRAFT.md:115,146`），C-17 v1.1 v8 建 `source_sync_plans`/`source_operations`（`FEA-C17_SOURCE_SYNC_DRAFT.md:33,56`）；四表名单见 `GATE-DELETE-…:41`。
- 建议：在本卡 Closeout 明列「四表 = `source_entries`/`page_bindings`（C-15 v7）+ `source_sync_plans`/`source_operations`（C-17 v1.1 / schema v8）」并写 L-1 已满足；把 AD-003 `:128` 与三份「未冻结」旧口径登记为 limitation + 后续处置（AD-003 为**现行**权威文档，非历史裁定，宜走 dated errata 追加注记，不改冻结契约字节）。

**P2-03｜AC7 要求「写明不独立释放及依据」，依据未落 PLAN**
- 文件:行：`doc/REBASELINE_PLAN.md:11`。
- 问题：PLAN 只在该行状态单元格里写「含 FEA-02-BRIDGE 裁决=不独立释放」，未写依据，也无 BRIDGE 节点行；素材本身齐备（方案 §15.6 `:922` 写域与生命周期断言、`doc/tasks/FEA-04.md:46` 明载 BRIDGE 收窄切片由 FEA-03 交付、Host 生命周期/`ExitCoordinator` 未实施且「本卡不依赖，按 R-STATE-4 维持既有装配」）。
- 依据：`doc/tasks/FEA-DOC-RECONCILE-1.md:66`（AC7）要求「PLAN 写明不独立释放**及依据**，不留悬空节点」。
- 影响：裁决寄居在一个 `in_progress` Task 的状态格里，Task 关闭后该裁决只剩卡内文字，未来读者无法从 DAG 侧核到依据。
- 建议：在 PLAN 或卡 Closeout 写「依据：方案 §15.6 `:922` + `FEA-04.md:46`（BRIDGE 收窄切片已由 FEA-03 `DraftBuffer.cs` 交付；Host 生命周期/ExitCoordinator 未实施，由 FEA-05/07 生命周期断言覆盖）」；预算只余 15 B，建议先腾空间（见 P3-03）。

**P2-04｜GOV-11 AC3 主证据指向的卡明文否定该 AC**
- 文件:行：`doc/tasks/FEA-GOV-11.md:78`（Closeout：`AC3 已由 FEA-01-FREEZE-1（集成 bf1c8eb00）…实际完成`）↔ `doc/tasks/FEA-01-FREEZE-1.md:52`（「**不释放实现 Task**：`FEA-02-CORE` 等候选须另建卡…」）、`:39`（U-12：首个实现候选选 `FEA-02-CORE`，当前明确前置是 FEA-01 未冻结）。
- 问题：AC3 是「释放第一个实现候选 → 建卡 → 派独立 Review」。被引证据卡自述**没有**释放实现候选，且把候选指认为 `FEA-02-CORE`。真实载体为 `doc/tasks/FEA-02-CORE.md`（`status: done`、`integration_commit: 135479270`，已核为 HEAD 祖先）。
- 建议：把 AC3 主证据改为 `FEA-02-CORE`（含其 scope review / 实现 review），`FEA-01-FREEZE-1` 只作为冻结链前置引用。

### P3（3）

**P3-01｜STATUS:11 混写契约 ID 与 schema 版本**
- `doc/STATUS.md:11` 的「C-15 v7」「FEA-11-PREREQ-1 v8+」：C-15 的冻结契约版本实为 **v1.5**（`doc/plan/FEA-CONTRACT-FROZEN-C15.md:15`），承载的是 **schema v7** 迁移；schema v8 的契约是 **C-17 v1.1**（`doc/plan/FEA-CONTRACT-FROZEN-C17.md:3,11`），Task 名才是 FEA-11-PREREQ-1。易被读成「C-15 契约 v7」。建议写「C-15（schema v7）+ C-17 v1.1（schema v8）」。

**P3-02｜D07 Closeout 未披露 Gate 裁定里「D07 行 7 ⚠ 部分」**
- `doc/tasks/FEA-D07-UNBLOCK.md:89` 称「D04–D07 四包条款级承载经 r3 approved 复核」，而 `doc/plan/GATE-DELETE-CONTRACT-CLOSURE-2026-11-01.md:30` 明记 D07「前 6 项 ✅ / **行 7 ⚠ 部分**（见 L-5）」，`:39-40` 以 L-5 明文认定收口。AC8 文句要求「全部覆盖、不引入部分关闭」，故应写清「全部覆盖」是**按 L-5 认定口径**，不等于 D07 逐项无保留（也不等于四表 DDL 因此冻结，见该裁定 `:70`）。

**P3-03｜预算余量已近极限（非违规，仅记账）**
- STATUS 2997 B/28 行（预算 3200/45，93.7%）、PLAN 6985 B/63 行（预算 7000/64，**99.8%**），两者均触发 `check.ps1` 的 80% 警告（`gates.log:5-6`）。Handoff `:67` 已提示「下次加 DAG 行必须先腾空间」；建议把该预算约束写成下一轮的显式前置（P2-03 的补写也要先腾空间）。

## 「对账结论是否成立」

- **7 项对账事实本身成立**：四表 DDL 确已由 C-15 v7 + C-17 v1.1（schema v8）冻结；C11-PREREQ-1 确已集成 `b7018e19b`；GOV-11 的 4 项裁决输入确已落盘且 4 份冻结记录齐备；`G-DELETE-CONTRACT` 确已于 2026-11-01 关闭；IMMERSIVE 的 v2-壳 limitation 确已由 `FEA-07-V2-F11-1` 收口；RUN-GRANT-2 的 title 确为历史描述且 `status: done`；BRIDGE 不独立释放的**判断**与方案 §15.6 / `FEA-04:46` 一致。**无一项事实性对账结论被推翻。**
- **不成立的只有三处「表述/流程完备性」**：AC3 的自设条件（P1-02）、两张卡的 `done` 前置（P1-01）、PLAN 中 BRIDGE 依据（P2-03，AC7 判词「及依据」未兑现）。此外 P2-01 使 AC8 的「ledger 重生成 PASS」在提交点不成立，P2-02 使 AC1 的「四个表名可追溯」依赖跨文档推断。

## 附注与边界

1. **审后仓库状态变化**：本次复核完成期间，仓库出现新提交 `b6ada81e8`（`fix(fea-doc-reconcile-1): 处置 Review r1（REC-01…REC-13）…`），已改动 STATUS/PLAN/TASK_LEDGER/GOV-11/D07/对账卡/Handoff 等。**本报告结论只对 `4d64bfdcb` 负责**；上述 P1/P2 的判定均以 `git show 4d64bfdcb:<path>` 的字节为依据（其中 P1-01 在 `4d64bfdcb` 与 `d91dbe444` 两个对象上均可复现）。若 DSH 已在 `b6ada81e8` 处置，请在集成说明中逐条映射，不要用新 head 覆盖本报告的 P1-01/P1-02。
2. **工作区另有未跟踪的 `doc/reviews/FEA-DOC-RECONCILE-1-r1.md`**（他 agent/他轮产物，后已被 `b6ada81e8` 纳入）。按「未提交内容归原作者所有」，本审查者未读写其 findings 正文，本报告与其结论相互独立。
3. **未做**：全量 pytest / dotnet（本轮 0 源码改动）；未重算 18 pins 之外任何 pin；未改动被审文件、未 commit、未 push。
4. **门禁原始输出**：`check.ps1` → `Governance check: PASS (3 warnings)`；`verify_pins.ps1` → `PIN AUDIT: PASS (all 18)`。

## 建议的处置顺序

1. P1-01（两张卡生命周期字段）与 P1-02（AC3 文句）——一次提交改完，是 verdict 从 `changes_requested` 转 `approved` 的必要条件。
2. P2-01（提交后重建台账）、P2-03（BRIDGE 依据）与 P2-04（AC3 证据改指 FEA-02-CORE）——低成本、可在同一提交完成；改 PLAN 前先按 P3-03 腾预算。
3. P2-02（四表名 + AD-003 陈旧口径）——可在本卡 Closeout 写清并把 AD-003 处置登记为后续项；若要改 AD-003，须按「现行权威文档用 dated errata 追加注记、不改冻结契约字节」执行。
4. P3 三项随文修正即可，不阻断。
