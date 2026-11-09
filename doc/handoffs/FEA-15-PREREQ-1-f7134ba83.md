---
task_id: FEA-15-PREREQ-1
author: DSH（Lead / Integrator）
recipient: 独立上下文 Reviewer
base_commit: 417d9c442
delivery_head: f7134ba83
status: delivered
---

# Handoff：FEA-15-PREREQ-1（修复既有 2 个 App.Tests 失败）

## 交付结果

FEA-15 集成验收的前置测试债：两个既有失败（非 FEA-13 引入）已消除。实现提交 **`f7134ba83`**（base `417d9c442`）。

| 变更 | 内容 |
|---|---|
| `apps/.../Shell/V2/ImmersiveReaderWindow.cs` | `Background = Brushes.Black;` → `this[!BackgroundProperty] = new DynamicResourceExtension("Nm.Color.Bg.Canvas");`（设计系统 token；阅读器视觉不变） |
| `apps/.../tests/NewManga.App.Tests/FluentPageTests.cs` | 过期期望 17 → **18**（权威）；新增 gesture 去重断言（`SelectMany(Gestures).Distinct()`） |
| `verification/FEA-15-PREREQ-1/**` | README + 5 日志（命令头/EXIT） |

## 验证证据

| AC | 命令/步骤 | 结果 | 证据 |
|---|---|---|---|
| AC1,AC2 | 2 个目标测试 | **2 passed / 0 failed** | `logs/dotnet-test-two.log` |
| AC3 | App.Tests 全量 | **838 passed / 0 failed / 11 skipped**（原 2 失败消除） | `logs/dotnet-test-app-full.log` |
| AC3 | `dotnet build NewManga.sln` | **0 警告 / 0 错误** | `logs/dotnet-build.log` |
| 变异① | 恢复 `Background = Brushes.Green;` | V2Conformance **1 failed** | `logs/mutation-literal-brush.log` |
| 变异② | 断言改回 17 | FluentPage **1 failed** | `logs/mutation-stale-count.log` |
| 复原 | `-t:Rebuild` + 复跑 | 2 passed | 同上 |
| AC4 | `check.ps1`（默认 + `-TaskPath`）、`verify_pins` | PASS / 18/18 | 卡/Handoff |

## 关键检查点

- 阅读器是否仍为全屏画布底色（`Nm.Color.Bg.Canvas`），无 literal brush。
- 快捷键断言是否为 18 且无重复 gesture。
- App.Tests 全量是否 0 failed（原 2 个消除、无新增）。

## 风险与遗留

- 快捷键数量若再变需显式更新（注释已说明）。
- 本次只跑 App.Tests 全量；未跑 Host.Tests / 全 solution 测试（build 已覆盖全 solution）。FEA-15 集成验收时会跑全量。

## 下一任务建议

FEA-15 前置观察：STATUS 记录 `pytest 3395/10`（10 个 skipped 或 10 个未登记 flake？需在集成验收前核对）；随后进入 FEA-14 切片或 FEA-15 集成验收准备。
