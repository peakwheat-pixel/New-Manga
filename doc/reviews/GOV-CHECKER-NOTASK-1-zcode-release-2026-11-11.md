---
task_id: GOV-CHECKER-NOTASK-1
decision: RELEASE_SCOPE_WITH_BASELINE_PREREQUISITE
adjudicator: ZCode CLI
session_id: sess_ed894fec-18b7-40b8-9e6d-f927d8f2f031
decision_turn_id: turn_57466df8-0198-4e35-bf66-0b7c788510bb
input_head: 0201dc9612faa9eea9104b8e0568414e4a7bad5a
---

# ZCode 后续治理任务释放裁决

2026-11-11，独立 ZCode plan 会话经续接给出本裁决；首轮仅报告已完成事实核验，未给出结论。决策轮 CLI `EXIT=0`。本记录由 Codex 根据该会话回复整理。

释放唯一任务 `GOV-CHECKER-NOTASK-1`，kind `governance`，Owner `codex`，依赖已完成的 `FEA-15-PIN-POLICY-1`，基线为上述 HEAD。目标是使 default `check.ps1` 识别 STATUS 中明确的无当前 Task 声明，输出 warning 且正常完成其他检查。缺失或歧义的声明不得被当作空窗放行。隔离场景放在 `G:/CODEX/New Manga.workspace/GOV-CHECKER-NOTASK-1/`。

允许修改 `tools/governance/check.ps1` 的空窗分支，以及本 Task 卡、Review、Handoff、`verification/GOV-CHECKER-NOTASK-1/**`、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md` 和由工具生成的 `doc/TASK_LEDGER.md`。不得修改其他 checker 判定语义、`-TaskPath`、终态指针拒绝、integration_commit、ledger、READY、预算或 r194 双基准语义；不得修改其他治理工具、模板、`.gitattributes`、历史 pin、冻结契约、产品源码、Schema 或依赖；禁止资源清理和 push。

验收包括：

1. 当前明确空窗声明下 default 检查 EXIT 0，并记录两条原有错误消失。
2. 终态指针、不存在路径、缺失当前 Task 行仍失败；合法非终态指针与原行为一致；显式 `-TaskPath` 对 done 且 integration_commit pending 的失败语义不变。构造放宽为任意解析失败均放行的变异，证明缺失行反例会错误变绿，再逐字节恢复并验证反例复红、正例仍绿，记录 hash 和 EXIT。
3. 收口后空窗 default、本卡 `-TaskPath`、18 pins 和 API inventory 均 EXIT 0；更新 STATUS、Plan、Ledger 和 Closeout Record。各场景留生成 HEAD、命令和 EXIT；Canonical Evidence 使用 BLOB 基准。

语义变更实施之前，依照 `doc/09_COLLABORATION.md` §4.4 定义影响全集、对代表和边界样本实测并保存基线错误矩阵；核验不足时不得把本裁决当成实现放行。独立 Review 必须由未参与实现的独立上下文执行并检查变异判别；最终裁决使用不同的独立 ZCode 会话。

`FEA-15-PIN-BASIS-ENFORCE-1`（R-001）暂不释放，待本卡收口后再作为候选；验收遗留诊断属于新产品迭代范围取舍，暂不释放。`NEW-MANGA-V1-FULL-AUDIT` 仍 blocked。若无法在不放松既有检查的前提下实现反例矩阵，停止并保留现有 `-TaskPath` workaround。
