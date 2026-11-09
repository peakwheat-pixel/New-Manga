---
task_id: FEA-DOC-RECONCILE-1
reviewer: 独立上下文 fresh subagent（DSH 派发；子 agent 会话 `640e5d74-f5bd-4d07-899f-5448c6e6f31b`；父会话 `session-c08ea2ac-cbcf-47ac-a7a9-0e15254b3fa5`）
reviewer_kind: subagent
author: dsh-lead（DSH）
base_commit: 9b0683822
reviewed_head: 4d64bfdcb
decision: changes_requested
---

# Review：FEA-DOC-RECONCILE-1（FEA 线文档对账）r1

## 审查者身份与来源

- 审查者：**独立上下文 fresh subagent**，未参与该 Task 的实现、返修或证据生成；仅只读被审 head 的仓库内容。
- 子 agent 会话：`640e5d74-f5bd-4d07-899f-5448c6e6f31b`；派发方（父）会话：`session-c08ea2ac-cbcf-47ac-a7a9-0e15254b3fa5`；`reviewer_kind: subagent`。
- 仓库：`G:\CODEX\New Manga`，分支 `main`。
- 审查对象：`git diff 9b0683822..d91dbe444 -- doc/ verification/`（9 文件，+175/−23）与 Handoff 提交 `4d64bfdcb`；被审 head **`4d64bfdcb`**（交付 `d91dbe444`，基线 `9b0683822`）。
- 审查时工作树：干净（`git status --short` 为空）；本报告是审查者唯一新增文件，未 commit、未改被审文件。

## 结论

**`changes_requested`**；**P0 = 0 / P1 = 1 / P2 = 4 / P3 = 8**。

7 项对账中，第 1（DDL 口径事实）、2、3（GOV-11 关闭主体）、4、5、6 项的事实与所引原始证据一致；**第 7 项（FEA-02-BRIDGE）的书面交付不成立**：AC7 要求「PLAN 写明不独立释放**及依据**」，而 PLAN 内唯一 BRIDGE 文本是本卡 DAG 行内的结论性括注，无依据、无独立行；且「无缺口」超出所引证据（所引 `FEA-04.md:46` 原文说的是 Host 生命周期/`ExitCoordinator` **未实施**）。另有 3 项机械/口径问题须修：`TASK_LEDGER` 三项分项数字在交付 head 上不成立、GOV-11 AC3 子句「测试表不再 `NOT_RUN`」与事实相反、STATUS 的 DDL 口径与 AD-003 等权威文档仍冲突且未登记残余。

「0 源码 / 0 契约字节 / 0 pin 重算」经复核成立（diff 只触及 `doc/**`、`verification/**`；`doc/plan/FEA-CONTRACT-FROZEN-*`、`doc/contracts/**` 零改动；`verify_pins` 18/18）。门禁与预算均复核为 PASS。

## Findings

| ID | 级别 | 文件:行 | 问题 | 依据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| REC-01 | P1 | `doc/tasks/FEA-DOC-RECONCILE-1.md:66`（AC7）、`:56`（清单 #7）；`doc/REBASELINE_PLAN.md:11` | AC7 要求「PLAN 写明不独立释放**及依据**，不留悬空节点」，但 PLAN 全库仅 1 处 BRIDGE 文本——本卡 DAG 行内括注「含 FEA-02-BRIDGE 裁决=不独立释放」，**无依据引用、无独立节点行**；依据（方案 §15.6、`FEA-04.md:46`、`FEA-07-RESIDUAL-2`）只写在 Task 卡内。AC7 仍标 `<<MET>>` | `git grep -n BRIDGE -- doc/REBASELINE_PLAN.md` 命中仅 `:11`；卡 `:56` 依据列仅存在于卡内 | 二选一：①在 PLAN 以等价字节替换补齐「不独立释放 + 依据（方案 `:922`、`FEA-04:46`、`FEA-07` AC2）」并腾出预算；②把 AC7 改写为「PLAN 记结论、依据登记在卡/常驻文档」并同步 Handoff，不再声称 PLAN 载依据 | open |
| REC-02 | P2 | `doc/TASK_LEDGER.md:14-16` | 交付 head 上三项分项数字不成立：ledger 写 `tracked 558 / untracked 1 / non-terminal tracked 12`。脚本在 `git add` 之前运行，提交后 `doc/tasks` 的 559 个 Task 全部被 git 跟踪 | HEAD 复跑 `python tools/governance/task_ledger.py`：`task files 559 (tracked 559, untracked drafts 0)`、`non-terminal 13 (tracked 13)`；`git status --short -- doc/tasks` 为空。卡 `:84`/Handoff `:36` 声称「ledger 重生成 PASS」 | 提交后重跑 `--write` 并以修正提交更新三行；注意 `check.ps1:224-235` 只比较 `task files`/`non-terminal` 两个总数，**无法发现分项漂移** | open |
| REC-03 | P2 | `doc/tasks/FEA-DOC-RECONCILE-1.md:62`；`doc/tasks/FEA-GOV-11.md:59-61`、`:78` | AC3 第三子句「测试表不再 `NOT_RUN`」与事实相反：GOV-11 测试表三行仍为 `NOT_RUN`（`:59-61`），Closeout（`:78`）明确写「测试表 `NOT_RUN` 为当时记录，原字节保留」。整条 AC3 仍标 `<<MET>>` | GOV-11 测试表未改动（diff 仅 status 行、3 条 AC、Closeout）；GOV-11 Closeout 自述保留 | 把 AC3 子句改为「测试表 `NOT_RUN` 保留（append-only），不据此判 PASS」，与 Closeout 一致后保持 MET | open |
| REC-04 | P2 | `doc/STATUS.md:11`；`doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md:128`；`doc/plan/FEA-C11_IMPL_PREREQS.md:24`；`doc/plan/GATE-DELETE-CONTRACT-CLOSURE-2026-11-01.md:41` | ①同一行内「L-1…L-9 保留」与「四表 DDL 已冻」并列，而 L-1 的定义正是「四表 DDL 未冻结」（Gate `:41`），读者无法判断 L-1 是否已解除。②`00_INDEX` 登记为 CURRENT/ARCHITECTURE 的 AD-003 `:128` 仍写「**边界：四表 DDL 仍未冻结，属 Source 生产实现前置**」；FEA-C11_IMPL_PREREQS `:24` 仍写「DDL 未冻结」。③全仓无 L-1 解除/满足记录，卡与 Handoff 也未把 AD-003 等过期口径登记为残余或 follow-up（allowed_paths 未含 AD-003） | 上述行文；`git grep -n "L-1"` 在 STATUS/PLAN/checkpoint/Task 中无「已解除/已满足」记录 | 在 STATUS 或卡内写明「L-1 前置已由 C-15（schema v7）+ C-17 v1.1（schema v8）满足」；把 AD-003 `:128`、FEA-C11_IMPL_PREREQS `:24` 的 errata 作为显式残余登记进本卡 Closeout/Handoff 下一任务（不得以越权改 AD-003 代替登记） | open |
| REC-05 | P2 | `doc/tasks/FEA-DOC-RECONCILE-1.md:56`；`doc/tasks/FEA-04.md:46`；`doc/design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md:910,922`；`doc/tasks/FEA-07.md:298`；`doc/tasks/FEA-07-RESIDUAL-2.md:3,50` | 「由现有装配与 **FEA-05/06**/07 生命周期断言覆盖，无缺口」：①`git grep 生命周期断言 -- doc/tasks` 仅命中 `FEA-07-RESIDUAL-2` 与 `FEA-07`（AC2），**FEA-05/06 无该断言**，卡内依据列也未引 FEA-05/06；②被引的 `FEA-04.md:46` 原文为「其 Host 生命周期/`ExitCoordinator` 部分**未实施**……BRIDGE 原义未被本卡声称已交付」，只支持「FEA-04 不依赖」，不支持「无缺口」；③真正覆盖者是 FEA-07 的 `ExitCoordinator`（AC2 `:298`）与 RESIDUAL-2 AC-R4a-2（`:50`），未被引；④Handoff `:65` 写「若后续发现退出协调缺口需另立卡」，与「无缺口」不一致 | 上述行文与 grep 结果 | 引用 FEA-07 `:298` + RESIDUAL-2 `:50` 作为覆盖证据，把结论改为「不独立释放；退出协调由 FEA-07 已交付的 `ExitCoordinator` 覆盖，残余风险另卡」 | open |
| REC-06 | P3 | `doc/tasks/FEA-D07-UNBLOCK.md:89`；`doc/plan/GATE-DELETE-CONTRACT-CLOSURE-2026-11-01.md:30`、`:39-40` | Closeout 写「D04–D07 四包条款级承载经 r3 approved 复核」「AC1–AC8 全部 MET」，未披露 Gate 裁定中 **D07 行 7 为「⚠ 部分」**、由保留项 **L-5 明文认定**关闭，也未写「不因此冻结 DDL/不构成实现」。AC8 原文「全部覆盖」与裁定「部分」并存 | Gate `:30` 表格；Gate `:39-40` L-5 认定；`FEA-D04D07-COVERAGE-r3.md:20,37` | Closeout 补一句 L-5 / D07 行 7 口径，避免读者把「全部覆盖」读成逐项无保留 | open |
| REC-07 | P3 | `doc/handoffs/FEA-DOC-RECONCILE-1-d91dbe444.md:19`；`doc/REBASELINE_PLAN.md:52`；diff `9b0683822..d91dbe444` | Handoff 称把 C-04b 注记并入「完成」行「信息未丢」，但被删行末的 **`Owner c04b-impl`** 未保留，「信息未丢」不准确 | diff 删除行：`（C-04b v1.2 done 26aa0ca4a；R-1 代码修复 0 pin，Owner c04b-impl）`；新 `:52` 无该署名 | 补回 Owner 署名，或把措辞改为「内容已并入，Owner 署名未保留」 | open |
| REC-08 | P3 | `doc/tasks/FEA-GOV-11.md:78`；`doc/reviews/ADJ-2026-11-01-FEA-DECISIONS.md:77`；`doc/tasks/FEA-02-CORE.md:6,16`；`doc/tasks/FEA-01-FREEZE-1.md:6,16` | AC3「释放第一个实现候选」主归因写 `FEA-01-FREEZE-1`（集成 `bf1c8eb00`）。按 U-12，首个**实现候选**是 `FEA-02-CORE`（独立 Review、集成 `135479270`）；`FEA-01-FREEZE-1` 是冻结链末环（治理 Task）。结论可由「及其后续实现线」兜住，但主证据不精确 | ADJ `:77` U-12；两卡 front matter | 主证据改为 `FEA-02-CORE`（done + 集成 + 独立 Review），`FEA-01-FREEZE-1` 记为前置 | open |
| REC-09 | P3 | `doc/STATUS.md:11`；`doc/plan/FEA-CONTRACT-FROZEN-C15.md:15`；`doc/plan/FEA-CONTRACT-FROZEN-C17.md:20`；`doc/tasks/FEA-11-PREREQ-1.md:45`；`tests/fea11/test_v8_migration.py:18-23` | 版本记法混用契约版本/任务名与 schema 版本：「C-15 v7」中 C-15 契约版本实为 **v1.5**；v8 的承载契约是 **C-17 v1.1**，不是 FEA-11-PREREQ-1 卡；v8 实际创建 **4 表**（`source_sync_plans`/`source_operations`/`source_binding_publications`/`source_revision_lineage`），而 PREREQ `:45` 只列 2 表；STATUS 未写四表名，「表名/版本可追溯」需跨 3 文档 + 1 源码测试。另 PLAN `:12` 仍写「C-17 v1.0 FROZEN」（现状 v1.1，属改动前既有文本） | 上述行文与测试常量 | 写成「C-15（schema v7）+ C-17 v1.1（schema v8）」并链到四表名（如 `FEA-C11_IMPL_PREREQS.md:24`） | open |
| REC-10 | P3 | `doc/tasks/FEA-07-IMMERSIVE-F11-1.md:133`；`doc/tasks/FEA-07-V2-F11-1.md:65,72` | 补充称「其余 limitation（物理 2K/4K 未验证……）不变」，但 V2-F11-1 已在 **AOC 2560×1440（2K）主屏物理复验**（`EV-V2F-05`）；未限定「本卡 legacy 壳」，易被读成 2K 全线未验证 | V2-F11-1 卡 `:58`、`:65`、`:72` | 加限定「（本卡 legacy 壳；v2 壳 2K 已由 `EV-V2F-05` 复验）」 | open |
| REC-11 | P3 | `doc/REBASELINE_PLAN.md`（6985 B / 63 行，上限 7000 B / 64 行）；`verification/FEA-DOC-RECONCILE-1/gates.log:8`；Handoff `:67` | 加入本卡 DAG 行后仅剩 **15 bytes / 1 行** 余量，下一次 DAG 变更必须先压缩；本轮已为此删一行 C-04b 注记（见 REC-07）。预算检查只发 WARN 不发 FAIL（`check.ps1:620-621`），可用余量却已近零 | 实测字节/行数与门禁 WARN；Handoff 自认 | 把「完成：」长段迁至 checkpoint/台账，为 DAG 保留结构余量 | open |
| REC-12 | P3 | `doc/tasks/FEA-DOC-RECONCILE-1.md:24-36`（allowed_paths）；`4d64bfdcb` | 被审 head 的 Handoff 提交写入 `doc/handoffs/FEA-DOC-RECONCILE-1-d91dbe444.md`，**不在本卡 allowed_paths** 内（卡内无 `doc/handoffs/**`）。仓内约定不一致（`doc/tasks` 中对 `doc/handoffs` 的引用约 726 处，部分任务显式列入写域） | `git show --stat 4d64bfdcb`；卡 allowed_paths | allowed_paths 增 `doc/handoffs/FEA-DOC-RECONCILE-1-*.md`，或在协作协议统一「Handoff 不属写域」以避免逐卡歧义 | open |
| REC-13 | P3 | `verification/FEA-DOC-RECONCILE-1/gates.log:1-32`；`doc/templates/REVIEW.md`（证据纪律 Q-009） | AC8 的 canonical 运行日志**无 EXIT 码、无 shell/PowerShell/venv 头**，`verify_pins` 只留 tail；复跑结果与日志一致（PASS），但不满足仓库记录的运行日志纪律。相较 `FEA-C11-PREREQ-1`、`FEA-D07-UNBLOCK`、`FEA-GOV-10` 等无 `verification/` 目录的先例，本轮已有原始日志属改进，但仍非合规 | 日志全文；模板证据纪律段 | 追加一份带 EXIT 与 shell 头的日志（不改旧字节），并在卡内注明新日志为当前入口 | open |

## §9 项事实核对结果

| # | 核对项 | 结论 | 原始证据路径:行 |
|---|---|---|---|
| 1 | STATUS「四表 DDL 已冻（C-15 v7 + FEA-11-PREREQ-1 v8+）」与 C-15 冻结记录、FEA-11-PREREQ-1（AC-P1 MET）、`tests/fea11/test_v8_migration.py` 一致 | PASS | `doc/STATUS.md:11`；`doc/plan/FEA-CONTRACT-FROZEN-C15.md:43,50`（v7 DDL 实测、DDL 前置由本契约落地）、`:56`（不冻结 FEA-11/12/13 表结构）；`doc/tasks/FEA-11-PREREQ-1.md:45`（v8+ 两表）、`:65`（AC-P1 MET）；`tests/fea11/test_v8_migration.py:1-23`；`doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md:33,56,86,100`；`src/infrastructure/sqlite/schema.py:757-871` |
| 2 | `FEA-C11-PREREQ-1` 行改 `done`（集成 `b7018e19b`）与卡 Closeout 一致，且该 commit 是 main 祖先 | PASS | `doc/REBASELINE_PLAN.md:10`；`doc/tasks/FEA-C11-PREREQ-1.md:6,16,80`；`git merge-base --is-ancestor b7018e19b HEAD` = 0（亦为 `9b0683822` 祖先，`git cat-file -t` = commit） |
| 3 | `FEA-GOV-11` 关闭为 `done` 有据（ADJ 裁决 R / U-04 / U-05a / U-05b；C-01b/C-02/C-03/C-11 冻结记录；AC3 由后续实现线覆盖） | PASS | `doc/reviews/ADJ-2026-11-01-FEA-DECISIONS.md:15-18,74`；`doc/plan/FEA-CONTRACT-FROZEN-C01b.md:35-40`（`:38` 即 R 裁决）、`-C02.md:34`、`-C03.md:35`、`-C11.md:4-15`（均存在）；`doc/tasks/FEA-02-CORE.md:6,16`、`FEA-01-FREEZE-1.md:16`（`bf1c8eb00` 为 HEAD 祖先）；`doc/plan/FEA-C11_TASK_TABLE_ALIGNMENT_DRAFT.md:83-91`（§7 流程） |
| 4 | `FEA-D07-UNBLOCK` AC8 改 `[x] <<MET>>` 有据（Gate 裁定确实关闭 `G-DELETE-CONTRACT`） | PASS | `doc/tasks/FEA-D07-UNBLOCK.md:54,89`；`doc/plan/GATE-DELETE-CONTRACT-CLOSURE-2026-11-01.md:14,20-21,30`；`doc/reviews/FEA-D04D07-COVERAGE-r3.md:20,37` |
| 5 | `FEA-07-IMMERSIVE-F11-1` 的 append-only 补充与 `FEA-07-V2-F11-1`（done、2560×1440 复验）一致；status 仍为 `closed_with_limitations` | PASS | `doc/tasks/FEA-07-IMMERSIVE-F11-1.md:6,126,130-133`；`doc/tasks/FEA-07-V2-F11-1.md:6,19,58,65,72,79`；`f60b2ff50` 在 `9b0683822` 祖先链上 |
| 6 | `FEA-11-RUN-GRANT-2` 注记准确（status 确为 done、`integration_commit` 值正确） | PASS | `doc/tasks/FEA-11-RUN-GRANT-2.md:3,6,16,146-148`；`git cat-file -t 0180089894b2286d8ff6a94289b84dd318871d18` = commit 且为 HEAD 祖先 |
| 7 | `FEA-02-BRIDGE`「不独立释放」裁决有据（方案 §15.6、`FEA-04.md:46`、`FEA-07-RESIDUAL-2` 生命周期断言） | **FAIL** | `doc/REBASELINE_PLAN.md:11`（唯一 BRIDGE 文本，无依据）；`doc/tasks/FEA-04.md:46`（原文为「Host 生命周期/`ExitCoordinator` 部分**未实施**」）；`doc/design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md:910,922`（§15.5/§15.6 候选）；`doc/tasks/FEA-07-RESIDUAL-2.md:3,50`；`git grep 生命周期断言 -- doc/tasks` 仅命中 RESIDUAL-2 与 FEA-07 → 见 REC-01/REC-05 |
| 8 | append-only 合规：GOV-11/D07 只改 AC 勾选/标记（原 AC 文本未改）并保留测试表 `NOT_RUN`；IMMERSIVE/RUN-GRANT-2 为纯追加 | PASS | numstat：GOV-11 5/4，D07 3/2，IMMERSIVE 5/0，RUN-GRANT-2 4/0；`doc/tasks/FEA-GOV-11.md:47-49,59-61`；`doc/tasks/FEA-D07-UNBLOCK.md:54,69`（AC 文本逐字未变，仅 `[ ]→[x]`、`<<PARTIAL…>>→<<MET>>`） |
| 9 | 预算与门禁：STATUS ≤3200 B/45 行、PLAN ≤7000 B/64 行；`check.ps1` PASS、`verify_pins` 18/18；工作树除本报告外无未提交改动 | PASS | `doc/STATUS.md` = 2997 B/28 行；`doc/REBASELINE_PLAN.md` = 6985 B/63 行；`check.ps1` → `Governance check: PASS (3 warnings)`，EXIT=0；`verify_pins.ps1` → `PIN AUDIT: PASS (all 18)`，EXIT=0；`git status --short` 写报告前为空，写报告后仅 `?? doc/reviews/FEA-DOC-RECONCILE-1-r1.md` |

> 第 7 项的判定说明：**裁决方向本身可接受**（无节点需要它、Host 生命周期维持既有装配、`ExitCoordinator` 已由 FEA-07 交付），但（a）AC7 要求的「PLAN 写明依据」未做到，（b）「无缺口」超出所引证据且与本卡自己的 Handoff 措辞冲突。故按「书面交付是否成立」判 FAIL。

## 验证（实际执行）

| 场景 | 命令或手工步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| HEAD 与工作树 | `git rev-parse HEAD`；`git status --short` | `G:\CODEX\New Manga`，`main` | HEAD=`4d64bfdcb`；写报告前工作树干净 | 本报告 |
| 改动边界 | `git diff --name-only 9b0683822..d91dbe444`；`... -- doc/plan doc/contracts tools src apps tests` | 同上 | 9 文件全部在 `doc/**`、`verification/**`；契约/源码/工具零改动 | 命令输出 |
| 契约 pin | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 同上 | `PIN AUDIT: PASS (all 18)`，EXIT=0 | 复跑输出 |
| 治理门禁 | `pwsh -NoProfile -File tools/governance/check.ps1` | 同上 | `Governance check: PASS (3 warnings)`，EXIT=0 | 复跑输出与 `verification/FEA-DOC-RECONCILE-1/gates.log:3-11` 一致 |
| 台账复算 | `python tools/governance/task_ledger.py`（只读汇总模式） | Python 3.14 | `task files 559 (tracked 559, untracked 0)`；`non-terminal 13 (tracked 13)`——与提交版 `558/1/12` 不符 | REC-02 |
| 证据 pin 复算 | `Get-FileHash -Algorithm SHA256` 逐项 | 同上 | 卡 `:91-97` 的 7 个 `EV-RECON-*` sha256 与当前字节**全部一致** | 逐项比对 |
| commit 祖先 | `git merge-base --is-ancestor` / `git cat-file -t` | 同上 | `b7018e19b`、`bf1c8eb00`、`018008989`、`f60b2ff50` 均为 HEAD 祖先 | 命令输出（exit 0） |
| 未运行项 | 真实构建 / pytest / .NET 全量 | — | NOT_RUN（本轮 0 源码改动，不适用） | Handoff `:40` 同口径 |

## 剩余风险与未审到的部分

- **未穷举全仓过期表述**：按 Task 范围只核了 7 项对账与 STATUS/PLAN/卡面；`doc/plan/FEA-CONTRACT-FROZEN-C17.md` 之外的「C-17 v1.0」字样（如 `doc/REBASELINE_PLAN.md:12`）、`doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md:133` 的「G-CONTRACT 关闭前保持 blocked」属改动前既有文本，未列入本轮 finding 计数，但属 REC-04 同类口径债。
- **Budget 余量**：PLAN 只剩 15 bytes / 1 行，任何后续 DAG 修正都会先撞预算；需在释放下一 Task 前处理。
- **未复核**：`FEA-07-AC5-NATIVE-1`、`FEA-06-RESIDUAL-1`（卡内声明超出范围，保持未处理，符合禁止范围）。
- 本 Review 不构成集成批准、不关闭 Task；findings 处置由 DSH 决定；审查者未参与实现，亦未修改任何被审文件。
