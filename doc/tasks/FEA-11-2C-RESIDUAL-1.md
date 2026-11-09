---
id: FEA-11-2C-RESIDUAL-1
title: 2C 残余：预算超限分支不得吞掉 typed stop（RunGrantRenewal 停止优先序）+ 判别测试
kind: implementation
governance_version: 3
status: in_review
approval: DAG 指名候选（`REBASELINE_PLAN` 当前 DAG 末段「下一候选 2C-RESIDUAL-1（typed-stop）」）+ `FEA-11-RUN-GRANT-2C-r1.md` R2C-03（P3，保留为候选）；DSH 2026-11-09 范围冻结：只改 Host 停止分类优先序 + 判别测试，0 契约 pin（C-06/C-16 已冻，遵守型），0 wire 变更
suggested_owner: dsh
owner: dsh
reviewer: 待指派（必须独立上下文）
depends_on:
  - FEA-11-RUN-GRANT-2C
base_commit: ac64cb134
branch: null
worktree: null
integration_commit: null
delivery_head: a2c4c1d8c
canonical_evidence_status: complete
resource_closeout_status: pending
evidence_dir: verification/FEA-11-2C-RESIDUAL-1
allowed_paths:
  - doc/tasks/FEA-11-2C-RESIDUAL-1.md
  - doc/reviews/FEA-11-2C-RESIDUAL-1-*.md
  - doc/handoffs/FEA-11-2C-RESIDUAL-1-*.md
  - verification/FEA-11-2C-RESIDUAL-1/**
  - apps/desktop-avalonia/src/NewManga.Host/Sources/RunGrantRenewal.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/RunGrantRenewalTests.cs
out_of_scope:
  - 不改 C-06/C-16/C-17 冻结契约字节、18 pins、wire/DTO
  - 不改 `RunGrantRenewal` 的预算常量（Interval 240s / RoundBudget / MaxRenewals）与 options 校验
  - 不改 Core/Python、不改 FEA-12-UI 的 ShowList 守卫（另案）
  - 不 push
---

# FEA-11-2C-RESIDUAL-1：预算超限分支不得吞掉 typed stop

## 来源与缺陷

`FEA-11-RUN-GRANT-2C-r1.md` **R2C-03（P3）**：`RunGrantRenewal.cs` 的 POST-ROUND 预算分支先于停止语义判定，导致：

1. 一轮已返回 `StoppedTyped` / `StoppedTerminal` / `StoppedLivenessUnknown` 时，只要 elapsed 超预算，就被改写为 `SkippedBudget`（`RENEWAL_ROUND_BUDGET_EXCEEDED`），**吞掉更重要的 typed stop code**（诊断口径受损）；
2. 已成功 mint 的轮次在超预算路径下只做 `_renewals++` 后返回 skip，计数器语义可以接受，但**停止优先级**错误；
3. 单测只断言「超预算 → SkippedBudget」，未断言「超预算 + typed stop → 仍为 typed stop」。

## 修复口径（遵守型，无契约变更）

POST-ROUND 预算判定的优先级改为：

| outcome | 超预算时的结果 |
|---|---|
| `Renewed` | `_renewals++`，然后 `SkippedBudget`（既有行为，保留） |
| 任意 `Stop` 类（`StoppedTyped` / `StoppedTerminal` / `StoppedNotTracked` / `StoppedRoundsExhausted` / `StoppedLivenessUnknown`） | **`Stop` 原样返回，typed code 保留**（不写 `RENEWAL_ROUND_BUDGET_EXCEEDED`） |
| `SkippedBudget`（renew 内部已判预算） | 保留其自身 code 的 skip |
| 其它 | `SkippedBudget(RENEWAL_ROUND_BUDGET_EXCEEDED)` |

## Acceptance Criteria

- [x] **AC1 停止优先序**：超预算且 outcome 为 Stop 类时，返回原 kind 与 code；`status.Stops` +1、`BudgetSkips` 不因此 +1、`LastCode` 为 typed code。 <<MET>>
- [x] **AC2 成功轮计数**：超预算且 outcome 为 Renewed 时，仍 `Renewals` +1 且返回 `SkippedBudget`（既有语义不变）。 <<MET>>
- [x] **AC3 内部预算 skip 保留**：renew 已返回 `SkippedBudget` 且 code 非空时，超预算路径保留该 code（不覆盖为 `ROUND_BUDGET_EXCEEDED`）。 <<MET>>
- [x] **AC4 判别测试**：新增至少 3 个用例（typed stop / renewed / 内部 skip），且把修复改坏时至少 1 个用例 RED（变异判别已实测）。 <<MET>>
- [x] **AC5 门禁**：build 0/0；`NewManga.Host.Tests` 0 failed；全量 .NET 不新增失败；`check.ps1`（默认 + `-TaskPath`）PASS；pins 18/18；diff ⊆ allowed_paths。 <<MET>>

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-2C-README | AC1–AC5 | `verification/FEA-11-2C-RESIDUAL-1/README.md` | `-` | `349b524e3361c00458f8c1b499174b9cf0c8a24c85f95b4b0b53f7f1a86159f8` | CANONICAL |
| EV-2C-MUTATION | AC4 | `verification/FEA-11-2C-RESIDUAL-1/logs/mutation-red.log` | `-` | `f22c768c3bb95695e1bb14b38d07b124c8d5ab9967f0b62e41088192f6e3a405` | CANONICAL |
| EV-2C-GREEN | AC1,AC2,AC3 | `verification/FEA-11-2C-RESIDUAL-1/logs/renewal-tests-green.log` | `-` | `b796cf664f020f8e047e8a6cd3bfc88fc047142c541fb7328b8d052229ee4d2a` | CANONICAL |
| EV-2C-FULL | AC5 | `verification/FEA-11-2C-RESIDUAL-1/logs/full-solution.log` | `-` | `899a31c693b3f17bf4bd92ad5ed4c1feea48c24da1d1503516b2d44dd09cdc8d` | CANONICAL |
| EV-2C-BUILD | AC5 | `verification/FEA-11-2C-RESIDUAL-1/logs/build.log` | `-` | `76a55c39609f4a3ddd825765b6e3835c8e39cd5c87f9464563b8b176bb6c5879` | CANONICAL |
## 证据计划

| # | 命令 | 判别 |
|---|---|---|
| E1 | `dotnet build apps/desktop-avalonia/NewManga.sln -c Debug` | 0 warning / 0 error |
| E2 | `dotnet test ...NewManga.Host.Tests --no-build --filter "FullyQualifiedName~RunGrantRenewalTests"` | 0 failed；新增 3 例通过 |
| E3 | 变异：临时把修复改回旧序 → E2 至少 1 例 RED → 复原（sha256 一致） | 判别力 |
| E4 | 全量 `dotnet test NewManga.sln --no-build` | 不新增失败（既有 2 失败见 FEA-07-RESIDUAL-4 DEFECTS） |
| E5 | `check.ps1` 默认 + `-TaskPath`；`verify_pins` | PASS / 18/18 |

## 风险与回退

- 风险：改停止分类可能影响既有 `Renewal_RoundOverBudget_SkipsTheRoundAndKeepsTracking` 断言（Renewed 路径保持不变）→ 已按三条路径分别断言。
- 回退：单文件 + 测试，`git revert` 即可；无数据/契约影响。

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | NOT_APPLICABLE（main；base `ac64cb134`） | NOT_APPLICABLE | — | — | 未创建 worktree |
| temp | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 无 |
| build | `apps/desktop-avalonia/**/bin,obj` | NOT_APPLICABLE | — | — | 仓库既有 ignore |
| user-data | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 未访问 |

## Closeout Record

- 待独立 Review 通过后由 DSH 填写。
