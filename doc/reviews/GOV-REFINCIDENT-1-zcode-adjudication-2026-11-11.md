---
task_id: GOV-REFINCIDENT-1
adjudicator: ZCode 独立只读 Integrator
session_id: sess_937b1456-117c-4a3d-b28b-2da4e53abff6
decision_turn_id: turn_dd82ea95-18e9-4833-ab37-a3f97b0c7e88
addendum_turn_id: turn_a401f222-dd5c-493e-b25e-c552d8575375
reviewed_head: 5c53ba08780a169d01aa8c5d602c48ca74c71a83
decision: ACCEPT_REVIEW_CONDITIONAL_CLOSEOUT
---

# GOV-REFINCIDENT-1 独立终裁与补充裁决

2026-11-11，未参与实现、释放或 Review 的 ZCode 独立会话采信 `sess_f5cc4af4-be6c-451d-9fad-4a68c4d460f7` 的 ACCEPT，CLI 两轮均 EXIT 0。本记录由 Codex 根据返回整理。Review 之后的 `1fa6677` 和 `5c53ba0` 为 P3 澄清与 pin 回填；Integrator 复核其范围后允许对被审内容沿用 ACCEPT。

P3-1 配置来源澄清和 P3-2 中间快照登记均 CLOSED。AC1–AC3 的 MET 采信：原件 BLOB 保全、44 项前后对照及 8 项关键 hash、只读调查、根因假设及未实施建议均有证据；USN query/read 因非管理员保持 NOT_RUN。根因约束为 `root_cause_unknown_with_evidence`；Kernel-Power 41、NTFS 98 与 Get-Volume 为时间关联或瞬时状态，不证明事故原因。

原件混合换行导致该原始文件在默认 `git diff --check` 中报告 CRLF 尾随空白 EXIT 2，为已登记 limitation；不得为此改写原件或扩展为其他文件豁免。主 worktree、仓外事故目录和 investigation 均保留，不清理；R-001 仍 open P2。

## 收口顺序（补充裁决优先）

1. A：本裁决单独提交；以 A 的实际 commit 与 BLOB SHA 记录裁决 pin，并作为直接 main 交付的 `integration_commit`（独立审查和终裁采信点）。
2. 构造 dirty 终态候选，仅用于验证：Task done、AC4 候选 MET、证据和资源状态 complete；STATUS **原位替换**为 `- 当前 Task：无（GOV-REFINCIDENT-1 已收口）。`，既有刚收口行保留；Plan done/ACTIVE 无，Ledger 重生成。原先“移除当前 Task 行”提议作废。空窗 default、本卡 TaskPath、pins、API 四项实测 EXIT 0 后才可提交候选 B；未通过不得提交或声称完成。
3. clean B 复跑四项，完整日志含 HEAD、状态、命令和 EXIT，作为单独证据提交 C。C 后按用户门禁纪律复跑 default/TaskPath/pins：新日志尚未登记，done TaskPath 预期 EXIT 1，须在仓外如实记载；不得称 PASS。
4. D：Task 卡以真实 C commit 和日志 BLOB SHA 回填 Canonical Evidence，记录 A/B/C 和暂态；D 本身不自引用。clean D 复跑四项，均 EXIT 0 才完成收口；最终输出保存在仓外或回复。失败须如实处理，不得留下未验证的 done 假象。

STATUS ≤3200 bytes/45 行，Plan ≤7000 bytes/64 行，超限只精简现行文案，不改阈值或删除权威指针；四项命令的 warning 不等于 FAIL。任何无法在已授权范围闭合的失败须保留现场。禁止改原始事故文件、历史日志、Git 配置和工具、清理 dangling、提权或 push。

## 本会话未实测

plan 模式未重跑 git、PowerShell、Python、BLOB hash、44 项清单和四项门禁；这些采信独立 Review 与已提交日志，收口时仍须由执行者实测。空窗主树 gate 在终裁时为 NOT_RUN，不能预记 PASS。
