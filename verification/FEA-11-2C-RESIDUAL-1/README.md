# FEA-11-2C-RESIDUAL-1 证据索引

- Task：`FEA-11-2C-RESIDUAL-1`（2C 残余：预算超限分支不得吞掉 typed stop）
- Base：`ac64cb134`；依赖：`FEA-11-RUN-GRANT-2C`（done）
- 日期：2026-11-09

## 修复口径

`RunGrantRenewal` 的 POST-ROUND 预算分支改为按 outcome 分流（遵守 C-06/C-16 已冻语义，无 wire/契约变更）：

| outcome | 超预算结果 |
|---|---|
| `Renewed` | `_renewals++`，返回 `SkippedBudget(RENEWAL_ROUND_BUDGET_EXCEEDED)`（既有语义，含真实 mint 计数） |
| 任意 Stop 类 | **原 kind + typed code 原样返回**（不再被改写为 budget skip） |
| `SkippedBudget`（renew 内部已判预算） | 保留其自身 code |
| 其它 | 通用 `RENEWAL_ROUND_BUDGET_EXCEEDED` |

## 判别证据

| 断言 | 结果 | 证据 |
|---|---|---|
| 新增 3 用例：typed stop / terminal stop / 内部 skip | 全绿 | `logs/renewal-tests-green.log`（22/22 passed） |
| **变异判别**：移除预算分支内的 Stop 优先判断后复跑 | **2 failed / 2 passed**（typed + terminal 用例 RED） | `logs/mutation-red.log` |
| 还原修复（sha256 `6dadcbcd09402058…`）后复跑 | 22/22 passed | `logs/renewal-tests-green.log` |
| 全量 `NewManga.sln` | Host.Tests **305/0/72（+3）**、其余项目全绿；App.Tests 836/2/11/849（2 个既有失败，见 `FEA-07-RESIDUAL-4` DEFECTS）；合计 **1802 passed / 2 failed / 107 skipped** | `logs/full-solution.log` |
| build | 0 warning / 0 error | `logs/build.log` |
| 治理 | `check.ps1` 默认 + `-TaskPath` PASS；pins 18/18 | 见卡/Handoff |

## 说明

- 本轮 0 契约 pin、0 wire/DTO、0 预算常量改动；`out_of_scope` 零 diff。
- 全量跑后 `verification/FEA-09/logs/wire-redacted.ndjson` 既有副作用已 `git checkout` 恢复。
- `FEA-12-UI-RESIDUAL-2` 的 P3-01（ShowList 能力守卫判别力）为跨域事项，未并入本卡（另案）。
