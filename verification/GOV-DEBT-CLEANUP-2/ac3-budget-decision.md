# AC3 — Plan 预算扩容：裁决记录与「未执行」确认

**Task**: GOV-DEBT-CLEANUP-2 · **AC**: AC3 · **性质**: 记录裁决，不执行修改

## 用户裁决（唯一来源）

`verification/P09-GOVERNANCE-DEBT-20261019/user-decisions-20261019.md` 裁决 1：

> 批准提高到 **7000 bytes / 64 lines**。

适用范围：仅 `tools/governance/check.ps1` 中对 `doc/REBASELINE_PLAN.md` 的两个预算数值
（`Bytes` 与 `Lines`）。不放宽其它任何规则，不改其它文件预算。

## 当前实际规则（本 Task 未改）

| 项 | 值 |
|---|---|
| 检查器中的预算常量 | `Bytes = 2500; Lines = 35` |
| Plan 当前实际 | 2373 bytes / 35 lines |
| 用户批准的目标 | `7000 bytes / 64 lines` |

## 「本 Task 未执行」的确认

- 本 Task **没有**修改 `tools/governance/check.ps1`。
- 本 Task **没有**修改 `doc/REBASELINE_PLAN.md` 的任何预算数值。
- 本 AC **没有**改变 29 个非终态 Task 的登记状态：它们仍全部未登记（见 `ac2-deferred-tasks.md`）。

`git log -- tools/governance/check.ps1`（最近 3 条，证明本 Task 期间无改动）：

- （该文件无提交历史）

## 后续动作归属

按 `codex-release-decision.md` §「预算检查器修改的拆分决定」，实际修改
`check.ps1` 两个数值属于**全局治理检查器策略变更**，已拆为独立的后续治理文档维护 Task。
本 Task 只记录裁决与目标值，不执行修改。

采集时点 HEAD：`3c592220c`。
