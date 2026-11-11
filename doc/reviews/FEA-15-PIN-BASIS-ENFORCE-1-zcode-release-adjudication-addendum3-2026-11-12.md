---
task_id: FEA-15-PIN-BASIS-ENFORCE-1
adjudicator: ZCode 独立只读 Integrator
session_id: sess_7b34d23e-ddaf-4ec5-bbb3-964edd74fc58
turn_id: turn_14d71565-8907-4cf0-8e20-fa98d38f2bed
decision: ACCEPT_DUAL_ENVIRONMENT_BASELINE_WITH_R0
---

# 释放 Addendum 3：分离历史基线与新 TaskPath 载体

2026-11-12，ZCode 在原独立只读 Integrator 会话中裁决 `FEA-15-PIN-BASIS-ENFORCE-1` 的 AC1 基线载体问题。ZCode CLI 0.17.1，恢复调用 `--mode plan --json --locale zh-CN`，EXIT 0。裁决为 **ADJUDICATION / ACCEPT**：A/B 双环境证据结构满足 AC1 的语义，不要求同一树同时承载基线前已存在的历史 Task 与新 Task 卡。

## 裁定

- **A：固定历史基线 clone**：以 `2df8db7a4d19b591e919ecc6e8f8651167800ef0` 为干净 detached HEAD，运行正式 inventory/delta、default、四个代表历史 TaskPath、18 pins、API 和边界样本矩阵。
- **B：新 TaskPath clone**：仅在 Task 注册及 AC1a 证据提交、pin 回填后冻结的 R0 HEAD 执行。R0 中必须实际存在本 Task 卡、STATUS 指针指向本 Task、Plan 登记本节点。`5d58c4bfd7ad461a8df71698baf867d751bf4793` 是 Task 注册前 HEAD，不得用其上不存在的 TaskPath 结果冒充 PASS。
- A/B 中 `tools/governance/**` 与 `doc/templates/**` 必须逐文件 blob 完全一致；并验证 R0 相对 `2df8db7…` 的差异只在释放允许范围内。不得只比较 `check.ps1`。
- B clone 只运行本 Task 的 `check.ps1 -TaskPath`（可按需要复核 default、18 pins、API），不得运行 inventory/delta 或 repro，不得写入任何仓内路径。
- 两个环境的 clean 状态、HEAD、Git/PowerShell/Python 版本、`core.autocrlf`、命令、时间和 EXIT 均须记录。只有 A/B 全部实际结果与一致性断言通过，才可送独立 ZCode 会话完成 AC1d；该会话必须不同于最终 Review 会话。

## 执行次序与停止门

1. 先落盘本 Addendum，再登记 Task 卡、STATUS、Plan 与 Ledger。
2. 在 A 完成 AC1a/AC1c 历史面实测并提交判别性证据；随后回填证据 pin，形成 clean R0。
3. 在 B 于 R0 复核允许差异集、治理工具/模板 blob 同一性及本 Task 文件级载体，然后只运行新 TaskPath 检查。
4. 若 Task/STATUS/Plan 任一不在 R0、任一治理工具/模板 blob 不一致、允许差异集外变化、运行环境/输入漂移，或 TaskPath EXIT 非 0，则基线无效，保留现场并交 ZCode 再裁决；不得解释为 PASS。

## 事实核验备注

ZCode 的 `plan` 模式阻止了该会话直接执行 Git 命令；其回复披露未能从 Git 级别核验 HEAD。Codex 已在本机独立实测：`git rev-parse HEAD` 返回 `5d58c4bfd7ad461a8df71698baf867d751bf4793`，`git status --porcelain` 为空、branch 为 `main`，命令 EXIT 0。文件级核验同样确认当前没有本 Task 卡，STATUS 仍为无当前 Task，因此 ZCode 对 `5d58c4bf` 属“注册前”载体的判断与仓库实态一致。
