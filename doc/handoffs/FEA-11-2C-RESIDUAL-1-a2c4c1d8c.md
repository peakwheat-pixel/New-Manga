---
task_id: FEA-11-2C-RESIDUAL-1
author: DSH（Lead / Integrator）
recipient: 独立上下文 Reviewer
base_commit: ac64cb134
delivery_head: a2c4c1d8c
status: delivered
---

# Handoff：FEA-11-2C-RESIDUAL-1（预算超限分支保留 typed stop）

## 交付结果

`RunGrantRenewal` 的 POST-ROUND 预算分支按 outcome 分流：typed/terminal stop 原样保留（不再被改写为 `RENEWAL_ROUND_BUDGET_EXCEEDED`），成功轮次仍计数并降级为 typed budget skip，内部 budget skip 保留自身 code。实现提交 **`a2c4c1d8c`**（base `ac64cb134`）。

| 变更 | 内容 |
|---|---|
| `apps/desktop-avalonia/src/NewManga.Host/Sources/RunGrantRenewal.cs` | 预算超限分支：`Renewed` → 计数 + skip；Stop 类 → `Stop` 原样；`SkippedBudget` → 保留 code；其它 → 通用 skip |
| `apps/desktop-avalonia/tests/NewManga.Host.Tests/RunGrantRenewalTests.cs` | 新增 3 例：typed stop / terminal stop / 内部 skip（均超预算） |
| `verification/FEA-11-2C-RESIDUAL-1/**` | README + 变异 RED 日志 + 绿日志 + 全量日志 + 构建日志 |

## 验证证据

| AC/场景 | 命令/步骤 | 结果 | 证据 |
|---|---|---|---|
| AC1–AC3 | `dotnet test ... --filter "FullyQualifiedName~RunGrantRenewalTests"` | **22 passed / 0 failed**（新增 3 例通过） | `logs/renewal-tests-green.log` |
| AC4 变异 | 移除预算分支内 Stop 优先判断 → 复跑 `RoundOverBudget` | **2 failed / 2 passed**（typed + terminal RED） | `logs/mutation-red.log` |
| AC4 还原 | 还原（sha256 `6dadcbcd09402058…`）→ 复跑 | 22/22 passed | `logs/renewal-tests-green.log` |
| AC5 build | `dotnet build NewManga.sln -c Debug` | 0 warning / 0 error | `logs/build.log` |
| AC5 全量 | `dotnet test NewManga.sln --no-build` | Host.Tests **305/0/72**；其余项目全绿；App.Tests 836/2/11/849（既有 2 失败）；合计 **1802/2/107** | `logs/full-solution.log` |
| AC5 治理 | `check.ps1`（默认 + `-TaskPath`）、`verify_pins` | PASS（3 warnings）/ 18/18 | 卡/Handoff 引用 |

未运行：pytest（本卡零 Python diff）；真实 IPC（不需要）。

## 接收方式

- 分支 `main`；base `ac64cb134` → 实现 `a2c4c1d8c`；本 Handoff 在后续文档提交中引用实现 head。
- 复核命令：`git show --stat a2c4c1d8c`；`git diff ac64cb134..a2c4c1d8c -- apps/desktop-avalonia/src/NewManga.Host/Sources/RunGrantRenewal.cs`；按 README 复跑定向测试与变异。
- 关键检查点：预算分支的优先级是否与卡 §修复口径一致；既有 `Renewal_RoundOverBudget_SkipsTheRoundAndKeepsTracking`（Renewed 路径）是否仍绿。

## 下一任务建议

`FEA-11-HOST-AUTH-3`（proposed，C-17 崩溃恢复 grant 语义）或 `FEA-13` 建卡（备份/恢复/迁移），由 DSH 按 DAG 裁决。

## 风险与遗留

- 无契约/wire 变更；回退 = `git revert a2c4c1d8c`。
- 全量跑后 `verification/FEA-09/logs/wire-redacted.ndjson` 既有副作用已恢复。
- `FEA-12-UI-RESIDUAL-2` 的 P3-01（ShowList 守卫判别力）未并入本卡（另案）。
