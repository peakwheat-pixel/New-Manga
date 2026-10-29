# V11R-C-2-I1 窄验证（关闭主题域 L3 r1 的 C-2 遗留 2×P2）

**验证者**：reviewer（独立、只读，未参与实现；本次写操作仅本文件）。
**Pin**：`ed3a84cd7d5e6b662a96abadbc82fa853cf35a4d`（`fix(V11R-C-2-I1)`，父 `079bfb647`；已合入 main `b5f7d88fc`）；增量 `git diff 079bfb647..ed3a84cd7`（37 文件，含代码/测试/证据，无范围外产品改动）。
**前序**：`doc/reviews/V11R-THEME-L3-r1-independent.md` 中 C-2 = PASS_WITH_ISSUES（C2-P2-1 裸几何 + C2-P2-2 AC9 像素探针恒真）。
**纪律**：只核 Lead 指定的 3 项；未重跑 build/test（以 pin 内 `build.log`/`test.log` 为准）；用自写扫描独立复核 conformance 结论；未改代码/证据。

---

## 逐项结果

### 1. P2-1（ThemeStudio C# 裸几何 + conformance 覆盖）— **CLOSED**

**依据**：
- 新增 `ViewModels/V2/ThemeStudio/ThemeStudioMetrics.cs`（唯一令牌解析器，与 `Shell/V2/ShellLayout.cs` 同构）：`CardGap → Nm.Space.S4`、`CardWidthDefault → Nm.Size.InspectorExpanded`、`BreakpointFull/Compact → Nm.Size.Breakpoint.*`、`CardMinWidth` 由 `(Full − TreeWidth − InspectorExpanded − 2·S7 − 3·S4)/4` 纯令牌推导（≈249）、4/3/2 列数注明为 THEME_STUDIO_SPEC §3.1 冻结结构计数（非几何值）。
- VM 已全部改走解析器：`ThemeStudioLibraryAndMyThemesViewModels.cs` 的 `MinCardWidth`/`CardGap` 由 `const` 改为 `=> ThemeStudioMetrics.*`，`_cardWidth = ThemeStudioMetrics.CardWidthDefault`，`ColumnsForWidth` 委托解析器；`ThemeStudioSectionItems.cs` 的 `_width` 改为 `ThemeStudioMetrics.CardWidthDefault`。我用**更宽的**几何正则（`\w*(Width|Height|Gap|Size|Padding|Margin|Spacing|Corner|…)\w*\s*=\s*\d`，含 `= 数字` 赋值）扫描 `ViewModels/V2/ThemeStudio`+`Views/V2/ThemeStudio` 全部 C#：**0 命中**（旧值 `MinCardWidth=248`/`CardGap=12`/`_cardWidth=320`/`_width=320` 已不存在）。
- `V2ConformanceTests`：`OwnedCSharpDirectories` 已加入 `ViewModels/V2/ThemeStudio`、`Views/V2/ThemeStudio`（`:93-102`）；`CSharpAllowlist` 仅 `Shell/V2/ShellLayout.cs` + `ViewModels/V2/ThemeStudio/ThemeStudioMetrics.cs`，并有「每个 Owner 恰好一个令牌解析器」的理由注释（`:45-56`）；`\Studio\` 过滤保留（ui-studio 由自己的 `V2StudioConformanceTests` 负责）→ 实际扫描 **71 个 C#**（总量 75 − `Shell/V2/Studio` 2 个 − allowlist 2 个 = 71，与 compliance 一致）。
- 独立复核数字：V2 XAML **39 个**文件、C# **71 个**被扫描文件；用 conformance 的 7 条 C# 正则与 5 类 XAML 正则逐文件重跑 → **0 命中**（XAML 仅 `StudioTheme.axaml`/`ThemeStudioStyles.axaml` 注释文本命中 `shadow/gradient/blur` 字样，非真实值）。`compliance.md` 已更新为 39/71、§3 几何来源表、DEVIATIONS「例外申请：无」。

**P3（不阻塞）**：①conformance 的 `CSharpLayoutLiteral` 只匹配 `Width|Height|…\s*=>\s*\d`（表达式体），**不匹配字段/常量的 `= 数字` 赋值**——旧病 `public const double MinCardWidth = 248;` / `private double _cardWidth = 320;` 即使目录已纳入也不会被该正则抓到；本次修复是实打实移除了值，但「0 命中」本身不能证明干净（我是靠更宽正则复核的）。建议后续把该正则扩为 `\b\w*(Width|Height|Gap|Size|…)\w*\s*=(?!=)\s*\d`。②`verification/V11R-C-2/README.md` 头部的基线仍写 `907339511`（实际已基于 main `b5f7d88fc` 一带），属陈旧元数据。

### 2. P2-2（AC9 像素探针恒真）— **CLOSED**

**依据**：
- 测试已重写为 `V2ThemeStudioScreenshotTests.Preview_ChangesDynamicResourceProbe_ButLeavesCanvasPixelsUntouched_AndCancelRestores`（`:211-340`）：探针在**真实窗口**（1820×1000，左侧真实 `ThemeStudioView`，右侧混合探针条）内：
  - 正向控制：`Border` 通过 `{DynamicResource Nm.Color.Accent.Base}` 绑定（`:509-510`）；
  - 画布：`WriteableBitmap`（180×90）经 `Image` 呈现（`:512`，`CreateDocumentBitmap` 返回 `WriteableBitmap`）；
  - 区域用 `TranslatePoint × RenderScaling` 换算（`:545-554`），`CaptureProbe` 对强调色区/画布区/整帧分别做像素 SHA-256（`:556-587`），区域越界直接抛错（`:595-597`）。
- 断言链（无恒真）：切外观 → `Assert.NotEqual(baseline.AccentHash, light.AccentHash)` 且画布 `Assert.Equal`；切回暗 → 探针恢复；预览主题 → 探针变化 + `CellDifference(baseline, preview) >= 5`（显式守卫：预览若什么都没改变则测试红）；取消 → 探针/画布/整帧均恢复（`<=3` cells）；每步 `manager.AppliedPaletteId` 实测为 `newmanga-default → probe 主题 → newmanga-default`；最后 `checks.All(...)` 的 9 项布尔断言失败即红（`:280-295`）。
- `pixel-hash.json` 全部由比较派生：5 步（baseline/appearance-light/appearance-dark/preview/after-cancel）各含 accent/canvas/整帧 SHA-256；实测 accent `1D99…`（baseline）= `dark`、`0763…`（light）≠ baseline、`8541…`（preview）≠ baseline、`after-cancel=1D99…`；canvas 恒为 `BD57…`（5 步相同）；整帧 preview≠baseline 且 after-cancel=baseline；`passed:true` 由 `checks.All` 派生（非字面量），`full_frame_cell_difference_after_cancel:0`；5 张 `probe-*.png` 落盘。
- 反向验证逻辑：若探针不随主题变，`NotEqual` 失败；若画布随主题变，`Equal` 失败；若预览对窗口无影响，`>=5` 守卫失败——不存在"画布像素必不变"的先验恒真。

### 3. 顺带确认（P1 行高契约漂移）— **CLOSED**

**依据**：
- 契约一致性：`doc/plan/V11R_AVALONIA_CONTRACT.md:58,87` 规定 `Nm.LineHeight.*` 为乘数、语义别名（Body/Label/Meta/Data 等）**值必须等于 Tight(1.25)/Normal(1.45)/Loose(1.6) 之一**；`Generated/TokenMap.md:157-162` 的派生别名正是 Display/Title/Body/Label/Meta/Data = 1.25/1.25/1.45/1.25/1.25/1.25，`:293` 明确「绝对值在 `Nm.TextLineBox.*`，由 DS 派生」。
- 修复：`ThemePaletteComposer` 不再向别名键写 `baseSize×scale×designMultiplier×presetRatio` 的像素值，而是把 `designMultiplier×presetRatio` **量化到冻结乘数集**（并列取低档，与 DS 生成器对 Label/Meta/Data 的 1.25 结果一致）；DS `DesignSystemThemeManager` 的 `LineBoxDerivations` 用 `TextLineBox = fontSize × 别名乘数` 派生绝对值，并新增守卫：别名值非 double 或不在 `[1.0, 2.5]` → `ApplyThemeLayer` 返回 false、保留上一层、错误信息明确（`DesignSystemThemeManager.cs:558-600`）。这消除了「像素被再乘一次字号 → 行高 ~12×」的 P1。
- 回归测试 6 例（`tests/NewManga.ThemeEngine.Tests/LineHeightContractTests.cs`）：①合成层的别名值 ∈ 冻结乘数且 59 键无像素；②59 键完整性；③manager 拒绝像素别名（**ApplyThemeLayer 路径**，16.2 → false + 上一值 1.25 保持）；④`ApplyThemeLayer` 后 `TextLineBox.Body == round(fontSize×multiplier,2)`；⑤真实 `TextBlock` 在层应用后行盒有界；⑥`ThemeService.InitializeAsync` 初始化路径后行盒有界（**两条路径均已覆盖**）。日志：`build.log` 0 warning/0 error `BUILD_EXIT=0`；`test.log` 0 失败（App 305/7、ThemeEngine 235（较前 +6）、DS 82、Host 49/28、CoreClient 116/25）。

---

## UNVERIFIED / 边界
- 未重跑 `dotnet build/test`（纪律；以上计数取自 pin 内日志，未独立复现）。未重跑探针渲染（headless Skia 帧由日志/证据自证；截图与哈希自洽）。
- 行高「量化到 1.25/1.45/1.6」意味着 Label/Meta/Data 的原始设计比（1.35/1.35/1.3）在**别名键**上不再逐 tier 表达，绝对值随冻结乘数集派生——这是契约（§2.2/TokenMap）要求的口径，非本次回归；若产品视觉需要 tier 级差异，应在 DS 派生侧扩展 `TextLineBox` 取值表（另开任务）。
- C-3-I1 补充证据（`f679bf47b`：clean-tree R6、双 shell EXIT=0、`R6-v2-host.log`、v2 chrome 断言）不在本 pin 范围，我仅抽查其在 main 的存在与内容（见下），未做 C-3 复审。

---

## 结论

**C-2-I1 结论：PASS（3/3 项 CLOSED；仅 2 个 P3 元数据/扫描正则建议）。**

**C-2 是否可 closed：可**（主题域 L3 r1 对 C-2 的 2×P2 均实质关闭，且本次顺带确认的 P1 行高契约已按冻结契约收口）。

**主题域 L3 是否可签署：可**（C-1 = PASS；C-2 本轮 PASS；C-3 的前序 NOT_CLOSED 项已由 main `f679bf47b` 的 supplement 补齐——我抽查到 `R6-report-clean.md` 声明 `workingTreeDirty=false`、干净树 `dependency-graph` 145/56 仅剩 evidence/new-arch、对比度 `failures=0/failing_pairs=0`、`R6-clean-startup-smoke.log` 两壳 `EXIT=0`（`--exit-after 2500` 优雅关窗、无 kill）、`R6-clean-v2-host.log` 有完整 Host 会话、`R6-clean-file-manifest.txt` 齐全，并新增 `V2_shell_window_chrome_is_visual_only_and_keeps_real_window_behaviour` 覆盖 v2 `SystemDecorations/CanResize`——即 r1 报告的 C-3 P1/P2/P3 与 C-3-I1 项 4/项 3 残余均已闭环）。
