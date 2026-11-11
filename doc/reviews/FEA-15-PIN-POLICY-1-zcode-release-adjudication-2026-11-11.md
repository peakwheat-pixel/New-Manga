---
task_id: FEA-15-PIN-POLICY-1
adjudicator: ZCode CLI (sess_236d9541-8358-45f0-9318-4844a86a767e)
adjudication_trace: a8e3c24f-9cf9-4f90-aee2-8673b711184c
corrigendum_trace: a6b88e1d-78f9-4433-9225-92aabb09f090
base_commit: 4efc592d12c25b8be33502f53c9270ad0597adfd
decision: RELEASE_SUCCESSOR_PIN_POLICY
---

# ZCode 裁决：释放 FEA-15-PIN-POLICY-1

## 裁决

用户已明确授权“持续推进、全部授权、自动计划、无需人工审批，裁决交给 ZCode”。ZCode 独立只读 CLI 会话据此裁定：释放 FEA-15-PIN-POLICY-1，范围限于 pin 基准口径裁定与迁移影响面方案；不释放 checker 修订，不执行任何 pin 迁移，不修改终态卡或冻结字节，不 push。

本裁决同时授权将 FEA-15-PIN-EOL-GOV-1 从 approved 置为 done，前提是其现有 Canonical Evidence 完整、所有 evidence_dir 文件登记、资源 closeout 完整且门禁通过；STATUS / PLAN 当前指针切至后继 Task。此为 adjudication #2 明列的“另行授权释放后继 Task”解锁条件，不修改本卡 AC 或历史 pin。

## 绑定事实与更正

- 裁决绑定仓库 main、clean HEAD 4efc592d12c25b8be33502f53c9270ad0597adfd。
- FEA-15-ACCEPT-1 已为 closed_with_limitations；pytest/.NET 失败、安装/真实 UI/真实库 NOT_RUN 与 r3 Review 均保留。不得将其当作 READY 重跑或改写。
- FEA-15-PIN-EOL-GOV-1 当前为 approved；其 adjudication #2 记录终态当前 Task 指针冲突，并明确将释放后继 pin 口径裁定 Task 列为解锁方式。
- 基线 inventory 的互斥分解为 WORKTREE=3,451、BLOB=327、MIXED=999、其他 573 行，合计 5,350；573 行由 INCONSISTENT=160、UNPINNED=293、UNRESOLVED_COMMIT=68、EXTERNAL_UNAVAILABLE=47、MISSING=3、COMPOSITE_PATH=2 组成。
- ZCode 初次答复将 INCONSISTENT=160 与其超集 573 并列。ZCode 后续勘误确认总数无误、原列法会重复计算 160；上述互斥分解为唯一正确引用口径。历史 candidate-policy-analysis.md 原字节不改。

## 路线与边界

选择 pin 口径裁定 Task，而不修改 checker：已有全集、观察矩阵和候选策略可支持先裁定；checker 变更会影响更广泛生命周期语义，须另做 §4.4 影响面核验，本轮不释放。R-001 由新 Task 裁定关闭、转交或保留条件。

FEA-15-PIN-POLICY-1 的正式字段、AC、allowed_paths 和 out_of_scope 以同提交 Task 卡为准。该卡仅允许裁定与实施影响面方案；若建议实施，须独立释放后续 Task 和 Review。复核者必须来自新建的上下文独立 ZCode Review session，不得与 Codex 实现会话相同。

## 门禁与未运行项

ZCode adjudication 与勘误 session 为只读，不运行项目测试、不修改文件、不提交。Codex 在裁决输入 HEAD 上另行实测治理门禁，并将在 Task 释放提交后再次复跑并留证。pytest/.NET、Linux fresh clone、renormalize simulation、pin 迁移、checker 修改、资源清理/迁移/归档均 NOT_RUN 或禁止，不得宣称通过。

全程不 push。最终 Task 结论由上下文独立 ZCode adjudication 给出；不需要额外人工批准。

## 下一步

按本裁决原子更新后继 Task、前置 Task 终态、STATUS、REBASELINE_PLAN 与生成式 TASK_LEDGER；跑 default / TaskPath / 18 pins / API gates。随后由 Codex 认领后继 Task 并按 AC1–AC3 执行。
