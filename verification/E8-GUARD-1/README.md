# E8-GUARD-1：类别级绑定守卫（独立复核要求的最高优先级项）

基线 `9d6751bdd`。执行 `doc/reviews/E8-INDEPENDENT-REVIEW-1.md` 指出的**最高优先级测试缺口**：

> `StartupDiagnosticsTests` 只断言特定行存在，**不检查 `[Binding]`**；应加"startup.log 不含 `[Binding]`"
> （或 headless 组合零绑定错误）断言。

## 1. 加在哪、为什么

加在 `StartupDiagnosticsTests.RealProcessLaunchMatrix_ExitZeroAndDiagnosableStartupLog`
（`FEA07StartupProcessFact`，opt-in `NEWMANGA_FEA07_STARTUP_PROCESS=1`）。

**为什么不是新建 headless 测试**：本项目**没有**现成的 Avalonia 绑定错误捕获设施
（`Avalonia.Headless` 已引入但没有 logger sink 封装）；而该测试**本来就跑真实 App 进程**
（4 个 case，每个有独立 `--log-dir`），是**最忠实**的位置 —— 它检查的是**真实二进制**写出的**真实日志**。

## 2. 两处改动

### 2.1 `--exit-after` 2500 → 15000

**原因**：2500ms **不足以**让 V2 shell 构建到 Studio 控件（HUD ring 是页级控件）。
守卫必须能**看见**绑定错误才可能抓到它 —— 一个永远看不到错误的守卫是假测试。

### 2.2 守卫断言（**收窄到失败特征**）

```csharp
Assert.DoesNotContain(
    "Could not find a matching property accessor",
    log,
    StringComparison.Ordinal);
```

**为什么不是断言裸 `[Binding]`**：第一次实现就是那么写的，**立刻红了** —— 因为
`ReaderOverlay` 有一条 `[Binding] ... 'Value is null'`（`CurrentPage == null` 时的**预期空态读数**，
见 `verification/E8-RESIDUAL-1/README.md`）。

**这正是"断言噪音而非缺陷"的陷阱。** 收窄到 `Could not find a matching property accessor`
（= **解析失败**：DataContext 错 / 缺 `Source` / 成员改名）后，既覆盖 E-8 的整类缺陷，
又不把合法的空态读数当成失败。

## 3. 判别力（实测）

| 实验 | 结果 |
|---|---|
| 正常 | **1 passed**（65 s，4 个真实 App case） |
| **去掉 `StudioHudRingControl:47` 的 `{ Source = captured }`** | **FAIL**：`Assert.DoesNotContain() Failure: Sub-string found`（**16 s 就失败**，因为第一个 case 就命中） |
| 恢复 | **1 passed**，`PROBE` 计数 0 |

## 4. 回归

无夹具 `App.Tests` 全量：**954 / 0 / 11 / 965**（skip 仍 11，0 failed）。

## 5. 边界（诚实）

- 该守卫是 **opt-in**（`NEWMANGA_FEA07_STARTUP_PROCESS=1`），**默认不跑**。
  这意味着**日常 CI 不会自动防住**该类回归 —— 但它是**目前唯一**能验证真实二进制日志的手段，
  且比"新建一个默认跑的 headless 假测试"忠实得多。
- 未加 `ActiveTabLabel` 与 `StudioLeaveModal` 的独立测试：
  复核已指出前者**文本断言在绑定坏掉时仍绿**（`:217` 有命令式同步），后者**去掉 `Source` 后仍绿**（本就工作）。
  **加了也是假测试**，故不加；改由本守卫的类别覆盖兜底。
