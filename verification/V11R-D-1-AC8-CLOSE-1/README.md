# V11R-D-1 AC8（reduced-motion）核证 — 证据（r2 后修订）

Task：`V11R-D-1-AC8-CLOSE-1`（Owner：DSH）｜基线 `37c4cf0b3`｜实现 `d01a2babd` + r1 返修 `654cd3e97`

> 本文件经 r2 复核（P2-1/P3-3）修订：初版把默认壳写成 `App.axaml.cs:233` 的 `FluentShellSurface`
> **是错的**（该行仅 `--presentation-host=true` 可达）；并曾以 AD-002 为退役依据（实际指 Tauri 壳）。
> 下列内容为修正后的口径。

## 1. 结论：AC8 按「受支持产品界面」口径成立

`V11R-D-1` AC8 =「reduced-motion 生效；焦点环 2px accent（outline，不用阴影）；对比度符合 DESIGN_SYSTEM §2.3」。

| 受支持界面 | 入口 | reduced-motion 核证 |
|---|---|---|
| **默认壳 `builtin.current-v2`** | `AppOptions.cs:83` `DefaultShellId = "v2"`；`FrontendSelector.cs:9` 标为 fail-safe default；启动分支 `App.axaml.cs:148-161`（`IsFluent ? Fluent : CreateV2Shell`） | **项目侧 0 处动画声明** ⇒ 无动画可禁，用户结果「无运动」已达成 |
| **第二界面 `builtin.fluent`** | `App.axaml.cs:161` `FluentShell` | **完整实现 + 测试**（见 §2） |
| 旧壳 `--shell=legacy` | `AppOptions.cs:265-273` | **不满足**（`AppStyles.axaml` `Border.nm-bookcard` 固定 0.12s，D-12）；依 **FEA-00:25** 不在受支持界面范围 |

**`--presentation-host` 默认 false**（`AppOptions.cs:51-54`），所以 `App.axaml.cs:233` 的 `FluentShellSurface`
不是默认路径 —— 这是初版的错误，已在 r1 修正。

## 2. 默认壳（V2）的「无动画」核证

```
grep -r 'Transition|Animation|Duration|MotionTimings|MotionMode' apps/desktop-avalonia/src/NewManga.App/Shell/V2
  → 0 命中（24 文件）
扩展 Views/V2/**（85 文件）→ 0 命中；V2LocalStyles.axaml → 0 命中
```

**推理**：无项目侧动画 ⇒ 无物可禁 ⇒ 用户可见结果（无运动）已达成，且强于「动画被禁」。

**限定（r2 P3-2，如实记录）**：
- 只证明**项目侧声明为 0**，不覆盖 `FluentTheme` 框架内置动画；
- Theme Studio 使用框架 `ToggleSwitch`，DS 自注 Fluent 模板保留 knob 动画（`Controls.Selection.axaml:3-5`），
  `KnobTransitions` 仅注释无实现 ⇒ **框架 knob 动画不受 reduce，两壳同样，属先存**；
- **无护栏**：未来 V2 加动画会静默回退（建议后续加 lint/测试）。

## 3. Fluent 壳的 reduced-motion 链路（逐环节）

| 环节 | 位置 |
|---|---|
| 解析 | `MotionResolver.cs:76-89` |
| 时长归零 | `MotionTimings.cs:62-65`（reduce ⇒ `FeedbackHoverMilliseconds = 0`） |
| 页过渡/浮层/工具条/装饰 | `FluentShellSurface.axaml.cs:744-759` + 各页 `ConfigureMotion` |
| 按钮/badge 过渡 | `FluentMotionScope.cs:26-39` |
| class 信号 | `FluentShellSurface.axaml.cs:714-742`（`motion-reduced`/`motion-feedback`/`motion-navigation`） |
| 主题侧 | 同文件 `:729` `ThemeManager?.SetReducedMotion(...)` |

> r2 P3-3 更正：`FluentMotionScope` 只覆盖 Button/badge；页过渡/浮层/工具条/装饰由
> `FluentShellSurface.axaml.cs:744-759` 与各页 `ConfigureMotion` 承载。

## 4. 测试实证

```
# command: dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj \
#   --filter "FullyQualifiedName~MotionMatrixResidual|FullyQualifiedName~FluentMotionResidual|FullyQualifiedName~MotionTimings" --nologo -v q
# env: Windows 11 / dotnet 9 / net9.0
# result: 13 passed / 0 failed / 0 skipped
# wall-clock: 24.3s（含 build；日志内「持续时间: 1 s」是测试执行时间）
# EXIT=0
```
更宽过滤 `Motion|Decorative|Reduced` = **55 passed / 0 failed**（r1/r2 复核各自复现）。

关键断言：
- `MotionMatrixResidualTests.cs:103` — `Assert.Equal(0d, reduceAll.FeedbackHoverMilliseconds)`
- `MotionMatrixResidualTests.cs:102` — `Assert.True(reduceAll.FeedbackColourOnly)`
- `FluentMotionResidualTests.cs:52` — `Assert.True(reduce.FeedbackColourOnly)`
- `FluentMotionResidualTests.cs:63` — full 下 `FeedbackHoverMilliseconds == 120d`

## 5. 焦点环与对比度（r2 实证，真验）

```
# command: dotnet test ...NewManga.DesignSystem.Tests.csproj \
#   --filter "FullyQualifiedName~ContrastToken|~FocusRingHighContrast|~ButtonTheme|~StandardControlsTheme"
→ 22 passed / 0 failed / EXIT=0（墙钟 8.2s 含 build）
```

- `ContrastTokenTests.cs:9-16` 头部明写 "**AC8 conformance** … DESIGN_SYSTEM §2.3 floors"；
  `:70-79` 断言焦点环 accent/panel **≥3:1**（对应 `DESIGN_SYSTEM.md:62`）；
- `FocusRingHighContrastTests.cs:19-20` 断言 2px 标准 / 3px 高对比；
- `ButtonThemeTests.cs:115-117` 断言 `BorderThickness == 2` + accent 色 + ring 在控件外侧
  （`:106-113` 是外框部分）；
- `StandardControlsThemeTests.cs:170` TextBox 外侧 2px 环。

## 6. 依据强度（r2 P3-1）

`FEA-00:25` 原文：「旧代码构建的 Avalonia `--shell=legacy` 只是已有诊断/发布回退入口，
**不自动成为第三个受支持界面**；Tauri/React 与 PySide6/QML 不进入新方案。」

**强度限定**：该文件是**方案层 PROPOSAL**（[建议] 级，r8 `approved`，非冻结契约）。
故「受支持界面 = `current-v2` + `fluent`」是**方案层一致口径**，不是冻结契约条文。

## 7. 不做的事（AC4）

本轮 `git diff 37c4cf0b3 654cd3e97` 无任何 `.cs` / `.axaml` 改动。

## 8. 计数与不回归

```
verify_final.py（AC_BASE=0b517259e）：40/40 卡、260/260 AC、190 verified / 64 blocked / NA 6
check.ps1（全局）                → PASS (3 warnings), EXIT=0
verify_pins.ps1                  → PASS (all 18), EXIT=0
generate_api_inventory.py --check → OK (1/80/6=87), EXIT=0
```

> **披露（r2 P3-4）**：`verify_final.py` 的 **EXIT=1** 来自 8 条**先存** `diff 增删` FAIL
> （`V11R-B-1…B-5`、`V11R-C-1`、`MICA-FIX-1`、`FEA-07-AC5-NATIVE-1`），非本轮引入；计数部分可信。

## 9. 已知

- AC8 **正文**（「reduced-motion 生效」）无条件表述，与注释的范围限定存在张力（r2 P2-2）；
  正文受 `verify_final`「AC 正文未被改动」约束不可改，张力由注释 + DEVIATIONS D-12 缓解。
- `V11R-D-1` 的 `-TaskPath` 仍有 **4 条先存错误**（`EVIDENCE_BASIS_HEADER_INVALID`、缺 canonical evidence、
  `evidence_dir` 含未登记文件、缺 Resource Manifest）—— 该卡 `lifecycle v2` 既有 frontmatter 缺陷，
  不在本卡 `allowed_paths` 内。
