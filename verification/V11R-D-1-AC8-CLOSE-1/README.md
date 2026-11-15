# V11R-D-1 AC8（reduced-motion）核证 — 证据

Task：`V11R-D-1-AC8-CLOSE-1`（Owner：DSH）｜基线 `37c4cf0b3`

## 1. 调查：为什么原判定是「live gap」，实际是「旧壳残留」

`AC-BLOCKED-CLASSIFY-1` 依据 DEVIATIONS D-12 判为 `IMPL`（当前树 live gap），理由是
`App.axaml:20` include 的 `AppStyles.axaml` 有固定 `Border.nm-bookcard` `BrushTransition 0:0:0.12`。

深入读代码后：

1. `AppStyles.axaml`（37 行）的固定过渡只作用于 `Border.nm-bookcard`；
2. `Border.nm-bookcard` 由 `Views/Pages.cs:780` 添加，该文件用 `LegacyChrome.Brush(...)` 构建卡片
   ⇒ 属**旧壳构建路径**（`Views/Legacy/LegacyChrome.cs` 注释：one-release legacy shell, `--shell=legacy`）；
3. 产品默认入口是 `App.axaml.cs:233` 的 `new FluentShellSurface(...)`（新壳）；
4. 新壳有**完整**的 reduced-motion 链路（见 §2）。

⇒ `AppStyles.axaml` 的固定过渡影响的是**已退役的旧壳路径**，不是产品默认路径。

## 2. 新壳的 reduced-motion 实现点（机制核证）

| 环节 | 位置 | 行为 |
|---|---|---|
| 阈值解析 | `ViewModels/Fluent/MotionTimings.cs:62` | `FeedbackHoverMilliseconds: feedback && !reduce ? 120d : 0d` |
| 反馈过渡应用 | `Views/Fluent/FluentShellSurface.axaml.cs:790-820` | `ApplyFeedbackTransitions` 遍历当前与缓存的四个页面视图，对每个 `Button` 调 `FluentMotionScope.Apply` |
| 单按钮过渡 | `Services/FluentMotionScope.cs:28-32` | `button.Transitions = timings?.FeedbackHoverMilliseconds > 0 ? {...} : null` |
| class 信号 | `FluentShellSurface.axaml.cs:731-737` | `motion-navigation` / `motion-feedback` / `motion-decorative` / `motion-reduced` |
| 主题侧 | 同文件 `:729` | `ThemeManager?.SetReducedMotion(!resolution.Enabled)` |

## 3. 测试实证

```
dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj \
  --filter "FullyQualifiedName~MotionMatrixResidual|FullyQualifiedName~FluentMotionResidual|FullyQualifiedName~MotionTimings"

已通过! - 失败: 0，通过: 13，已跳过: 0，总计: 13 (net9.0)   耗时 24.3s
```

关键断言：
- `MotionMatrixResidualTests.cs:103` — `Assert.Equal(0d, reduceAll.FeedbackHoverMilliseconds)`
- `MotionMatrixResidualTests.cs:102` — `Assert.True(reduceAll.FeedbackColourOnly)`
- `FluentMotionResidualTests.cs:52` — `Assert.True(reduce.FeedbackColourOnly)`
- `FluentMotionResidualTests.cs:63` — full 模式下 `FeedbackHoverMilliseconds == 120d`

日志：`motion-tests.log`。

## 4. 改判与如实披露

AC8 由 `blocked` 改判 `verified`，注释同时写明：

> **旧壳残留**：`--shell=legacy` 路径下 `AppStyles.axaml` 的 `Border.nm-bookcard` 固定 0.12s
> `BrushTransition` 仍不响应 reduced-motion（DEVIATIONS D-12），但该壳已按 AD-002 退役、
> 不是产品默认路径。

**没有**声称「全应用无条件达成」。

## 5. 本轮未改代码（AC4）

`git diff --stat` 只含 2 个 `doc/tasks/*.md` + 本证据目录；`.cs` / `.axaml` 零改动。

## 6. 计数与不回归

```
verify_final.py（AC_BASE=0b517259e）：40/40 卡、260/260 AC、verified 190 / blocked 64 / NA 6
  （改判前 189 / 65）
check.ps1（全局）                → PASS (3 warnings)
verify_pins.ps1                  → PASS (all 18)
generate_api_inventory.py --check → OK (1/80/6=87)
```

## 7. 已知

`V11R-D-1` 的 `-TaskPath` 仍有 **4 条先存错误**（`EVIDENCE_BASIS_HEADER_INVALID`、缺 canonical evidence、
`evidence_dir` 含未登记文件、缺 Resource Manifest）——属该卡 `lifecycle v2` 的既有 frontmatter 缺陷，
与本次 AC8 改判无关；同类问题已由 `GOV-HISTORICAL-CARD-METADATA-REPAIR-1` 处置过 5 张 gv3 卡，
本卡不在其 `allowed_paths` 内。
