---
task_id: FEA-DOC-RECONCILE-1
reviewer: 独立上下文 fresh subagent（DSH 派发；子 agent 会话 `674d334a-5f85-4364-a758-eab41cf3c6bd`；父会话 `session-c08ea2ac-cbcf-47ac-a7a9-0e15254b3fa5`）
reviewer_kind: subagent
review_round: r3
review_independence: 未参与该 Task 的实现、返修或证据生成；只读审查被审 head，未改任何被审文件
author: dsh-lead（DSH）
base_commit: 9b0683822
reviewed_head: c22aea60c
delivery_commit: d91dbe444
decision: approved
counts: 前两轮 22 项 finding 全部 FIXED（PARTIAL=0 / OPEN=0）；本轮新增 P0=0 / P1=0 / P2=0 / P3=5
---

# Review：FEA-DOC-RECONCILE-1（FEA 线文档对账）r3

## 审查者身份与来源

- 审查者：**独立上下文 fresh subagent**，子 agent 会话 `674d334a-5f85-4364-a758-eab41cf3c6bd`（父会话 `session-c08ea2ac-cbcf-47ac-a7a9-0e15254b3fa5`），**未参与**该 Task 的实现、r2/r3 返修或证据生成，仅只读被审 head。
- 被审 head：**`c22aea60c`**（r3 提交）；提交链 `9b0683822`（基线）→ `d91dbe444`（交付）→ `4d64bfdcb`（Handoff）→ `b6ada81e8`（r2 处置 r1）→ `c22aea60c`（被审）。
- 审查方式：**只读**。`git show` / `git diff` / `git ls-files` / `Get-FileHash` 读取字节；按任务要求只跑两个只读门禁（`check.ps1`、`verify_pins.ps1`，另含 `-TaskPath` 变体），未跑 pytest / dotnet 全量。
- 本报告为审查者唯一写入文件；未 commit、未改其他文件、未 push。

## 范围与结论

- 变更范围：`git diff --name-only 9b0683822..c22aea60c` 全部落在 `doc/**` 与 `verification/**`（12 文件，+382/−35）；`doc/plan/FEA-CONTRACT-FROZEN-*`、`doc/contracts/**`、`tools/`、`src/`、`apps/`、`tests/` **零改动**。
- **verdict：`approved`**。前两轮 22 项 finding 全部 FIXED；**P0 = 0 / P1 = 0**；无「对账结论不成立」的项——7 项对账事实与所引原始证据一致（含本轮补强的四表名可追溯与 GOV-11/D07 生命周期字段闭环）。
- 保留 5 项 P3（指针/记录精度类，不阻断集成，建议在 Task 关闭时随文修正）。

## 逐条判定：r1（`FEA-DOC-RECONCILE-1-r1.md`，head `4d64bfdcb`）

| ID | 级别 | 判定 | 一行依据 |
|---|---|---|---|
| REC-01 | P1 | **FIXED** | 卡 `:67` AC7 改为「PLAN 记结论，依据登记于本卡 §对账清单 #7」（r1 建议的处置②）；`:57` 已载方案 §15.6 `:922`、`FEA-04.md:46` 与 grep 结果，`FEA-07.md:298`/`FEA-07-RESIDUAL-2.md:50` 实测存在且支持结论 |
| REC-02 | P2 | **FIXED** | `doc/TASK_LEDGER.md:14-16` 现为 `559 tracked / 0 untracked / 13 non-terminal tracked`；`git ls-files doc/tasks/*.md`=560 减脚本排除的 `README.md`=559；按状态枚举复算非终态=13；`check.ps1` 复算 PASS |
| REC-03 | P2 | **FIXED** | 卡 `:63` AC3 现文「测试表 `NOT_RUN` 原样保留（append-only，不据此判 PASS）」，与 GOV-11 Closeout 一致；GOV-11 测试表三行 `NOT_RUN` 未被改写 |
| REC-04 | P2 | **FIXED** | `doc/STATUS.md:11` 现写「四表 DDL 已冻 = L-1 前置已满足（C-15 schema v7 + C-17 v1.1 schema v8；L-2…L-9 保留）」；AD-003 `:128` 与 `FEA-C11_IMPL_PREREQS.md:24` 已登记为卡 §残余 R-1/R-2（未越权改 AD-003） |
| REC-05 | P2 | **FIXED** | 卡 `#7` 改引 `FEA-07.md:298`（AC2 `ExitCoordinator`）与 `FEA-07-RESIDUAL-2.md:50`（AC-R4a-2），二者原文经核；`FEA-04.md:46` 已准确表述为「未实施，仅支持本卡不依赖」；「无缺口」表述已删除 |
| REC-06 | P3 | **FIXED** | D07 Closeout 第二条追加「D07 行 7 = ⚠ 部分，由 L-5 明文认定」并声明「不表示四表 DDL 因此冻结」（`FEA-D07-UNBLOCK.md:90`） |
| REC-07 | P3 | **FIXED** | `doc/REBASELINE_PLAN.md:52`「完成」行含「（Owner c04b-impl）」 |
| REC-08 | P3 | **FIXED** | GOV-11 Closeout 追加「证据更正」：AC3 主证据 = `FEA-02-CORE`（集成 `135479270`），`FEA-01-FREEZE-1` 降为前置 |
| REC-09 | P3 | **FIXED** | `STATUS:11` 与卡 `#1` 统一为「C-15 schema v7 / C-17 v1.1 schema v8」，并列出四表名；`FEA-CONTRACT-FROZEN-C17.md:20` 实测为「v8 / C-17 v1.1」 |
| REC-10 | P3 | **FIXED** | IMMERSIVE「对账补充」末条加限定「物理 2K/4K 仅指本卡 legacy 壳；v2 壳 2K 已由 `EV-V2F-05` 复验」 |
| REC-11 | P3 | **FIXED** | 卡 §残余 R-4 已登记预算风险；实测 STATUS 3026 B/28 行、PLAN 6994 B/63 行（余 6 B/1 行），仍属结构性风险（见剩余风险） |
| REC-12 | P3 | **FIXED** | 卡 `allowed_paths:31` 已含 `doc/handoffs/FEA-DOC-RECONCILE-1-*.md` |
| REC-13 | P3 | **FIXED** | `gates-2.log` / `gates-3.log` 均含 shell 头（`shell: 7.6.8 / Core`）、逐命令 `EXIT=`、预算实测；旧 `gates.log` 原字节保留为 HISTORICAL |

## 逐条判定：第二审查者（`FEA-DOC-RECONCILE-1-review.md`，head `4d64bfdcb`）

| ID | 级别 | 判定 | 一行依据 |
|---|---|---|---|
| P1-01 | P1 | **FIXED** | GOV-11/D07 `integration_commit`/`delivery_head`=`b6ada81e8`，`canonical_evidence_status`/`resource_closeout_status`=`complete`，CE 表 5+2 行填实且 8 个 sha256 与当前字节全部一致；GOV-11 `reviewer` 非 null。指针精度残留见 N-R3-01/04 |
| P1-02 | P1 | **FIXED** | 同 REC-03：卡 `:63` 已改为 append-only 口径，不再含可被证伪的「不再 `NOT_RUN`」 |
| P2-01 | P2 | **FIXED** | 台账 559/0/13 在 `c22aea60c` 可复现（见 REC-02）；`task_ledger.py` 仅排除 `README.md`（`tools/governance/task_ledger.py:81-83`），复算吻合 |
| P2-02 | P2 | **FIXED** | 卡 `#1` 已列四表名：v7 `source_entries`/`page_bindings`（C-15 `:115/:146`）、v8 `source_sync_plans`/`source_operations`（C-17 `:33/:56`），并如实标注 v8「并增」`source_binding_publications`/`source_revision_lineage`（C-17 `:86/:100`）；AD-003 冲突登记为 R-1 |
| P2-03 | P2 | **FIXED** | 同 REC-01：依据已落卡 `#7`，PLAN 行保留结论（预算只余 6 B，不在 PLAN 扩写，与 r1 允许的处置②一致） |
| P2-04 | P2 | **FIXED** | 同 REC-08：GOV-11 Closeout「证据更正」已把 AC3 主证据改为 `FEA-02-CORE` |
| P3-01 | P3 | **FIXED** | 同 REC-09：`STATUS:11` 已改为「C-15 schema v7 + C-17 v1.1 schema v8」，不再把契约 ID 当 schema 版本 |
| P3-02 | P3 | **FIXED** | 同 REC-06：D07 Closeout 已披露行 7「部分」与 L-5 认定 |
| P3-03 | P3 | **FIXED** | 同 REC-11：预算约束已登记 R-4；实测仍未越限（见门禁表） |

**统计：FIXED 22 / PARTIAL 0 / OPEN 0。**

## 本轮新增 findings（均为 P3，不阻断）

| ID | 级别 | 文件:行 | 问题 | 复现证据 | 建议 |
|---|---|---|---|---|---|
| N-R3-01 | P3 | `doc/tasks/FEA-GOV-11.md:10` | `reviewer` 引 `doc/reviews/FEA-DOC-RECONCILE-1-r{1,2}.md`，**`-r2.md` 不存在**（实际第二份独立 Review 是 `FEA-DOC-RECONCILE-1-review.md`）；另 `evidence_dir: verification/FEA-GOV-11` 与 `verification/FEA-D07-UNBLOCK` 目录不存在（既有状态） | `Test-Path doc/reviews/FEA-DOC-RECONCILE-1-r2.md` = False；`Test-Path verification/FEA-GOV-11` = False | 关闭时把 reviewer 指针改为 `-r1.md` + `-review.md`（+本次 `-r3.md`），并对 `evidence_dir` 加「无独立产物，依据 CE 表」注记 |
| N-R3-02 | P3 | 卡 `:83-84`、`:87` | AC8 证据列仍指历史 `gates.log`（当前入口应为 `gates-3.log`）；AC9 表只登记 r1，未登记第二份独立 Review（head `4d64bfdcb`，P0=0/P1=2）与本次 r3 | 卡文与 `doc/reviews/FEA-DOC-RECONCILE-1-review.md` 存在性 | 关闭前补登第二份 Review 行并把 AC8 证据格更新为 `gates-3.log`（历史行保留） |
| N-R3-03 | P3 | `verification/FEA-DOC-RECONCILE-1/gates-3.log:3` | r3 日志标 `HEAD=b6ada81e8`（提交前工作树），未见 `PRE_COMMIT_HEAD`/working-tree 标注；`gates-2.log` 有 `PRE_COMMIT_HEAD=4d64bfdcb` 先例 | 日志头部；日志生成 17:49:24、提交 17:49:49 | 下次日志写 `PRE_COMMIT_HEAD=<父提交> + 工作树含 r3 改动`，或在提交后补一条「已复跑」记录；本轮已在 `c22aea60c` 复跑 PASS，实质不受影响 |
| N-R3-04 | P3 | `FEA-GOV-11.md:16-17`、`FEA-D07-UNBLOCK.md:16-17` | `integration_commit`/`delivery_head = b6ada81e8`，但两卡最终 done 态（front matter + CE 表）在 `c22aea60c` 才落盘：`git show b6ada81e8:doc/tasks/FEA-GOV-11.md` 仍为 `reviewer: null` / `pending` / 空 CE 表 | 上述 `git show` 输出与 `b6ada81e8..c22aea60c` diff | 按仓库先例（`delivery_head` 不随后续文档修正前进，如 `FEA-07-V2-F11-1`）不阻断；建议改为 `c22aea60c` 或注明「收口记录头」 |
| N-R3-05 | P3 | 卡 `allowed_paths:20-32` | 实现侧在 `b6ada81e8`/`c22aea60c` 提交了 `doc/reviews/FEA-DOC-RECONCILE-1-{r1,review}.md`，但 allowed_paths 只有 handoffs、无 `doc/reviews/**`（`out_of_scope` 仅禁改既有字节） | `git show --stat b6ada81e8` / `c22aea60c`；卡 allowed_paths | 补 `doc/reviews/FEA-DOC-RECONCILE-1-*.md` 或在协作协议统一「Review 报告由审查者写入、实现侧仅提交」的写域口径 |

## 门禁与预算（实测于 `c22aea60c`，工作树干净）

| 场景 | 命令 | 结果 | EXIT | 证据 |
|---|---|---|---|---|
| 治理门禁 | `pwsh -NoProfile -File tools/governance/check.ps1` | `Governance check: PASS (3 warnings)`；warnings = 13 非终态、STATUS 80%、PLAN 80% | **0** | 本报告复跑；与 `gates-3.log:3-11` 一致 |
| 治理门禁（单卡） | `... check.ps1 -TaskPath doc/tasks/FEA-DOC-RECONCILE-1.md` | `PASS (3 warnings)` | **0** | 同上 |
| 契约 pin | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | `PIN AUDIT: PASS (all 18)` | **0** | 本报告复跑；与 `gates-3.log:13-33` 一致 |
| 预算 | `Get-Item` 字节 / `Get-Content` 行数 | STATUS **3026 B / 28 行**（≤3200/45）；PLAN **6994 B / 63 行**（≤7000/64） | — | PASS；PLAN 仅余 6 B/1 行 |

**Canonical Evidence 复核（卡 `:103-111`）**：7 个 CANONICAL 的 sha256 与当前字节**全部一致**（STATUS `0f282ae5…`、PLAN `c61845d6…`、GOV-11 `c5ae480f…`、D07 `13ff3903…`、IMMERSIVE `4ea62822…`、RG2 `83d15cbd…`、gates-3.log `79fa4682…`）。卡内 HISTORICAL 实为 **2 条**（gates-2.log `d6626c58…`、gates.log `c5fcd1f7…`），二者也与当前字节一致（非必需）。另核 GOV-11/D07 新增 CE 的 8 个 sha256，全部一致。

## append-only 与历史报告完整性

- `doc/reviews/FEA-DOC-RECONCILE-1-r1.md` 仅由 `b6ada81e8` 一次引入，之后**无任何提交改写**（`git diff --stat b6ada81e8..HEAD -- <该文件>` 为空）。
- `doc/reviews/FEA-DOC-RECONCILE-1-review.md` 仅由 `c22aea60c` 引入（`git show --stat c22aea60c` 显示为 A），未被改写。
- 说明：`git diff 4d64bfdcb..c22aea60c -- doc/reviews/` 同时显示两份 Review 为 A，是因为 r1 在 `4d64bfdcb` 之后才随 `b6ada81e8` 入库；「不修 r1」的实质要求已满足（无修改提交）。
- GOV-11 在 `c22aea60c` 的 diff 仅触及 front matter 与 CE 表，AC 文句与测试表 `NOT_RUN` 未动；D07 同（仅 front matter + CE 表），REC-06 口径补充在 `b6ada81e8` 已追加。

## 剩余风险

1. **PLAN 预算仅余 6 B / 1 行**（6994/7000，63/64）：下一次 DAG 行变更必须先腾空间（卡 R-4 已登记）。
2. **对账结论的证据仍分散**：四表名已入卡，但 `doc/AD-003:128`、`doc/plan/FEA-C11_IMPL_PREREQS.md:24`、`doc/plan/FEA-CONTRACT-FROZEN-C14.md:64` 等旧「未冻结」口径未改，只登记为 R-1/R-2（受 allowed_paths 约束，属正确处置），后续 errata 卡需承接。
3. **GOV-11/D07 生命周期指针**（N-R3-01/04）为记录精度问题，不影响两卡关闭的事实成立（裁决/冻结/Gate 证据均经核）。
4. 未复核：`FEA-07-AC5-NATIVE-1`（用户显示设置未复位）、`FEA-06-RESIDUAL-1`，与卡声明一致保持未处理；未跑 pytest / dotnet 全量（本轮 0 源码改动）。
5. 本 Review 不构成集成批准之外的额外授权：findings 处置与 Task 关闭由 DSH 决定；本报告只对 `c22aea60c` 有效，head 变化后自动降为历史。

## 验证执行清单

| 场景 | 命令/步骤 | 结果 |
|---|---|---|
| 范围边界 | `git diff --name-status 4d64bfdcb..c22aea60c`；全链 `9b0683822..c22aea60c` 过滤非 `doc/`/`verification/` | 12 文件全在 doc/verification；非范围内 0 命中 |
| 历史报告完整性 | `git log --oneline -- <r1/review>`；`git diff --stat <引入commit>..HEAD -- <file>` | 各仅 1 次 create，无修改 |
| 生命周期字段 | `git show b6ada81e8:doc/tasks/FEA-GOV-11.md` 与当前字节对比 | 见 N-R3-04 |
| 证据哈希 | `Get-FileHash -Algorithm SHA256` 逐项（7 CANONICAL + 2 HISTORICAL + 8 卡内 CE） | 全部一致 |
| 台账复算 | `git ls-files doc/tasks/*.md`（560）减 `README.md`；按 `status:` 枚举非终态 | 559 tracked / 13 non-terminal，与 ledger 一致 |
| 门禁 | 上述三条 `pwsh` 命令 | PASS，EXIT=0 |
