# AC3 可执行性标注：测试属性分类统计
head: fb9921604
timestamp: 2026-11-16T03:12:26+08:00

范围：apps/desktop-avalonia/tests/**/*.cs（318 个文件）

| 属性 | 数量 | 判定类别 |
|---|---:|---|
| [AvaloniaFact] | 601 | headless 可跑（需 Avalonia headless） |
| [Fact] | 980 | 纯逻辑 |
| [SidecarFact] | 30 | 需真实 sidecar（无夹具时 SKIP） |
| [Theory] | 76 | 纯逻辑（参数化） |
| [AvaloniaTheory] | 20 | headless 可跑（参数化） |
| **合计** | **1707** | — |

## 统计方法
对每个 .cs 文件统计 [AvaloniaFact / [Fact / [SidecarFact / [Theory / [AvaloniaTheory 出现次数并求和。
注：[AvaloniaFact] 与 [Fact] 不互相包含，[SidecarFact] 亦不含 [Fact 子串，故无重复计数。

## 对 AC3 的意义
AC3 要求「明确区分 [AvaloniaFact]（headless 可跑）、[Fact]（纯逻辑）、[SidecarFact]（需真实 sidecar）」。
本节给出全量分类数字，可直接对应矩阵里的每一格。
