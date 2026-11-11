---
task_id: FEA-15-PIN-POLICY-1
reviewer: ZCode CLI 独立上下文
review_session_id: sess_08fc30ae-10e9-48c5-8029-c3adb02fe9a5
review_mode: plan（只读）
reviewed_base: 4efc592d12c25b8be33502f53c9270ad0597adfd
reviewed_head: 359d09dffc489c8762727cf69b778cba6f432843
reviewed_followup_head: d26c43c76576b0f514530874fc9cb04f016674e6
conclusion: ACCEPT
---

# 独立 Review 报告：FEA-15-PIN-POLICY-1

## 审查身份与范围

- Reviewer：全新 ZCode CLI 会话 `sess_08fc30ae-10e9-48c5-8029-c3adb02fe9a5`，`--mode plan`。未参与 Task 释放、实现、返修或此前 adjudication；未复用释放会话 `sess_236d9541-8358-45f0-9318-4844a86a767e`。
- `reviewed_base`：`4efc592d12c25b8be33502f53c9270ad0597adfd`。
- `reviewed_head`：`359d09dffc489c8762727cf69b778cba6f432843`；同时检查了其后到 pinbackfill head `d26c43c76576b0f514530874fc9cb04f016674e6` 的四个提交。
- 核对 `main`、工作树 clean、Task 卡、STATUS、Plan、Handoff、ruling、impact plan、README、checkpoint、运行日志及 Canonical Evidence 表。

## 审查限制

该会话处于 `plan` mode，Bash 被拦截；因此未独立运行 SHA-256 复算、`git ls-tree` commit 包含性验证或逐提交文件级 diff，也未运行会改写证据的生成器或项目门禁。报告不把这些事项冒充 PASS。ZCode 检查了路径存在性、文档交叉引用、提交 reflog、运行日志，并以生成日志和 delta JSON 中自记录 SHA 交叉核对部分 pin。

## 结论

**ACCEPT**，附 3 项非阻断观察。本报告不构成最终政策 adjudication。AC1、AC3 保持 `PARTIAL`，AC2 为 `MET`；最终裁决须由另一个新 ZCode CLI session 作出。

## AC 分项

### AC1：全集增量刷新与正式裁定 — 支持 `PARTIAL`

- Inventory 为 `5,376` 行（585 张 Task 卡、5,358 条 Task pin、18 条 frozen pin）；互斥 basis 为 `3,467 + 327 + 1,009 + 573 = 5,376`。
- Delta 为 `+26 / -0 / changed 0`；增量由上游 Task 24 行与本 Task release 2 行组成，basis 差 `WORKTREE +16 / MIXED +10`。JSON、run log、ruling、impact plan、README 与 Handoff 一致。
- Inventory/delta/matrix 日志含输入/生成 HEAD、命令与 `EXIT=0`；日志中的 inventory、delta、matrix 输出 SHA 与卡面 pin 相符。
- Ruling 列出事实、推论、未知、反证条件、暂停门槛，并明确属于提案而非生效政策。AC1 保持 `PARTIAL` 正确，因最终裁决未完成。

### AC2：实施影响面方案（不含实施）— 支持 `MET`

- Impact plan 覆盖 5,376 行全集、互斥 basis/异常分类、4 类代表/边界样本、r194 predicate matrix、isolated clone dry-run、回退/停止规则及 successor Task 边界草案。
- Matrix 是 inventory predicate model，不是逐行执行 `check.ps1`；`4,803` match / `573` nonpass，`573 = 293 + 280`，`280 = 160 + 68 + 47 + 3 + 2`。
- 样本覆盖 BLOB text、WORKTREE text、MIXED_EOL text、BINARY PNG，与 matrix JSON 路径及 hash 一致。Clone dry-run 为 `NOT_RUN`；没有创建或释放 successor Task。

### AC3：登记、复核与治理门禁 — 支持 `PARTIAL`

- 三份 gate log（release、inventory delivery、review delivery）均记有 default/current/prior TaskPath、18 pins、API 五项命令，全部 `EXIT=0`，各 3 条 warning。
- 18 pins 为 `PASS (all 18)`；API `1/79/6 = 86`，并记有 `OK: rendered counts match FEA-C07 doc`。
- STATUS 当前指针为本 Task `in_review`，与 Task 卡/Plan 一致；AC3 保持 `PARTIAL`，直到最终 adjudication 完成。

## 发现（按严重度排序）

| # | 严重度 | 位置 | 观察 | 建议 |
|---|---|---|---|---|
| 1 | P3 | Task Canonical Evidence；`delivery-gates-359d09d.log` | 最后一份 gate log 生成于有 4 个治理文档改动的工作树；随后 `e0250928`、`d26c43c7` 又更新 Handoff/Task 卡。当时 pinbackfill 后 clean HEAD 尚无独立 gate 通过日志。AC3 没有宣称此步已完成，不构成虚报。 | 在 closeout 前于 pinbackfill clean HEAD 或之后的 clean HEAD 重跑并留证。 |
| 2 | P3 | Handoff 的 `e9f7bb1` 验证环境描述与 `delivery-gates-e9f7bb1.log` | Handoff 使用“clean main HEAD”的宽泛措辞；日志实际记录 6 个生成输出为 untracked。tracked clean 与整个 worktree clean 应区分。 | 后续描述写明 tracked clean 且 6 个生成输出 untracked 在场。 |
| 3 | P4 | `pin-inventory-preliminary-run-da4a60b.log` | 该日志为执行者事后回溯整理，已自披露来源；它是 `SOURCE_PIN` 过程快照，已被 delivery 版 supersede。 | 无需返修；数据引用以 delivery 版为准。 |

## 重点项核对

- Inventory `5,376` 与 delta `+26/-0/changed 0`：各载体一致。
- r194 modeled matrix 与逐行 checker 的界限：表述一致。
- Legacy `class` parser limitation：已披露；复制的上游 parser 未修改，历史非标准 `class_counts` 不作为语义分类依据。
- 四类样本：matrix JSON、run log、impact plan 对应一致。
- R-001：保持 open P2；提案为保留并转交后续 Task，不改旧 hash，不将观察解释为 corruption。
- Clone dry-run、pytest/.NET、Linux fresh clone、renormalize、pin migration、checker/template change：保持 `NOT_RUN` 或禁止，未被记为 PASS。
- 未发现实施 checker/template、历史 pin 迁移、renormalize、资源清理或 push。
- 本 Review 无法独立复算全部 Canonical Evidence SHA/commit 包含性，受上述 `plan` mode 限制。

## 最终裁决要求

AC1 四项提案须由**另一个全新 ZCode session** adjudicate；不得复用本 Review session。正式裁决前不要将 ruling 提案当作生效政策，也不要据此实施 checker/template 或历史 pin 迁移。