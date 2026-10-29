# 独立审查报告 · 主题域 L3 复审 r1（V11R-C-1 / C-2 / C-3-READY）

**审查者**：reviewer（独立、只读，未参与实现；本轮写操作仅本文件）。
**纪律**：pin 固定、不重跑 build/test（以 pin 内日志为准，未核项记 UNVERIFIED）、不采信 Owner 自述、只读代码/证据/doc。唯一一次脚本执行是 `rollback-theme-retire.ps1 -DryRun`（只读演练，未改文件/refs/settings；已核 tag 仍不存在、仓库无新增改动）。

**Pins（均核实为 main 祖先）**
- C-1 ThemeEngine：`09cd62710c31c1b05767192cca0409de69b9a972`（代码 head `daff73dbaefcd5ba960d8852d6cc2a6b0cfaac32`；Part B adapter `d8b953055`，main 合并 `907339511`）。
- C-2 Theme Studio：`206b37223e36faaec3121cfeb8ff199a9e34bfda`（parent `4366f3876`，基于 main `1e6a3c4ee`）。
- C-3-READY：`9acddc23f6f69959606f57f58f24921d0db5d730`（基线 main `c5037b65`，repoHead `7f6787b91`）。
- 参照：`doc/design/theming/THEME_ENGINE_LAYER.md`（FROZEN）、`THEME_STUDIO_SPEC.md`、`verification/V11R-C-1/{README,CONSUMER_GUIDE,INT_WIRING,DEVIATIONS}.md`、`verification/V11R-C-2/{README,compliance,INT_NOTES,DEVIATIONS}.md`、`verification/V11R-C-3-READY/*`、`verification/V11R-D-1/contrast-matrix.md`。

---

## 一、结论

| 对象 | 结论 | 是否可进入 C-3 执行 |
|---|---|---|
| **C-1 ThemeEngine** | **PASS** | **可以**（引擎侧零依赖前置成立） |
| **C-2 Theme Studio** | **PASS_WITH_ISSUES** | **不阻塞 C-3**（2 个 P2 须在 INT-1/L3 前修） |
| **C-3-READY** | **FAIL（小修后可复审，3 项）** | **暂不可以**：回滚 dry-run 机制/证据不成立（P1），对比度计数口径错误（P2），删除清单数字陈旧（P3） |

---

## 二、C-1 ThemeEngine（pin `09cd62710` / 代码 `daff73dba`）— **PASS**

### 2.1 已核实正确（关键项）
1. **Part B 适配器真实且边界干净**：`Service/DesignSystemThemeLayerSink.cs:26-166` 是 ThemeEngine 内**唯一**接触 Avalonia 的类型；`IThemeLayerSink`（`Service/ThemeLayerSink.cs:16-48`）为 Avalonia-free seam；`ThemeService`（`Service/ThemeService.cs`）通过 sink 转调 DS `ApplyThemeLayer`，自身不引用 `Application`/App。DS 侧 `DesignSystemThemeManager.ApplyThemeLayerCore`（`Theming/DesignSystemThemeManager.cs:390-425`）做白名单过滤、类型校验、`EnsureGlobalTokens` 后 `SwapPalette` 原子替换；失败保留原层并透传 `LastError`。
2. **headless 应用验收非空转**（`tests/.../DesignSystemThemeLayerSinkTests.cs`，11 例全 `[AvaloniaFact]`）：
   - `Theme_switch_keeps_the_window_instance_and_canvas_pixels:211-252`：真实 `Window.Show()`+`CaptureRenderedFrame()`，断言同一 `Content` 引用、`IsVisible` 保持、32×32 画布区域像素差=0，**同时**断言 `Nm.Color.Bg.Canvas` 资源确实变为主题值（正面控制存在，非恒真）。
   - `Repeated_theme_switches_do_not_duplicate_resource_providers:255-276`：5 次切换后 `MergedDictionaries` 数量不变。
   - `Sink_rejects_an_incomplete_layer...:71-90`、`...wrong_value_types...:91-106`：失败保持上一层。
   - `Service_apply_user_theme_updates_real_resources_and_persists:168-187`：真实 DS manager 的 `AppliedThemeLayerId` 变化 + 持久化记录。
3. **R-21 口径正确**：`Models/ThemeTokenKeys.cs:36-56` 的 `Colors` 直接引用 DS `PaletteColorKeys`（35，排除 `Nm.Color.Scrim`），`ThemeLayer` 直接引用 `ThemeLayerRequiredKeys`（59）；`ThemeInvariantColorKeys = [NmKeys.Color.Scrim]`。DS 侧 `PaletteColorKeys`（`DesignSystemThemeManager.cs:94-98`）显式排除 Scrim；`EnsureGlobalTokens` 保证全局不变量键在换肤前存在。回归锚点齐：`ThemePaletteComposerTests:21-36,95-107`（59 键逐键相等、Scrim 不在层内）、`ThemeValidatorTests:61-70`（未知色仅 warning）、`ThemeContractTests:106-125`（主题不变量排除）。
4. **零依赖断言真实**（C-3 前置）：`DependencyBoundaryTests`（79 行）用反射断言引擎程序集不引用 `NewManga.Theme`、不引用 App/Host/CoreClient、仅含 `NewManga.DesignSystem`；成员/类型集合不含 `ThemePack/ThemePackService/LayoutKind/NavPlacement/...`；`LayoutProfile` 存在。`NewManga.ThemeEngine.csproj` 仅 `Avalonia` 包 + `NewManga.DesignSystem` 工程引用。
5. **证据可对账**：`git-head.txt` 记录 code head=`daff73dba`、Part A/B 合并点；`build.log` 0 warning/0 error EXIT=0；`dotnet-test-themeengine.log` 203/203；`dotnet-test-full.log` 0 失败（App 232/6、DS 67、Host 42/24、CoreClient 42/25）；`generator-check.log` 逐字节 up-to-date。
6. **诚实登记**：README §5 与 D-18 明确 `NOT_RUN`（Windows 实机、系统跟随端到端、屏幕阅读器、Trim/AOT、真实 %APPDATA%、真实主题样本），未把 headless 结论冒充实机验收。

### 2.2 P3（不阻塞）
| # | 位置 | 问题 | 建议 |
|---|---|---|---|
| C1-P3-1 | `verification/V11R-C-1/DEVIATIONS.md` D-14 末段 | 仍写「seam 缺口：main 当前 DS 只有 `ApplyPalette`；待 `ApplyThemeLayer(ResourceDictionary,string)` 合入后…」，与同文件 D-17「Part B 真实适配器已完成」矛盾（DS seam 已存在并被 Part B 使用） | 删除/改写 D-14 该段为「已被 D-17 取代」 |
| C1-P3-2 | `doc/tasks/V11R-C-1.md` | 任务卡仍 `status: ready`、`owner: null`、`delivery_head: null`，AC 仍是 UI 模板 AC1–AC7（C-1 是 10 子系统引擎，README §3 才是真实 AC 映射） | Lead 按 §4 生命周期回填 delivery/integration/evidence pin 与真实 AC 映射 |
| C1-P3-3 | `ThemeService.cs:602,640` | `_lastIssues = [.._lastIssues, ..issues]` 在预览/系统跟随路径**累加不清理**，长会话内存增长；`:308-333` `ResetToDefaultAsync` 无条件 `RaiseChanged()`（即使无变化） | 预览路径只保留最新 issues；Reset 比较前后设置再决定是否通知 |
| C1-P3-4 | `ThemeService.cs:647-661` | `TrySave` 用 `SaveAsync().GetAwaiter().GetResult()`（同步阻塞）。当前 store 为本地小文件且 `ConfigureAwait(false)`，INT_WIRING §4#6 已注明；若未来换真异步持久化可能在 UI 线程死锁 | 保持现状可接受；在 `IThemePersistence` 文档写明「必须完成式、不得回投 UI 上下文」 |
| C1-P3-5 | `DesignSystemThemeLayerSink.cs:63,76,94,147,152` | sink 把 `exception.Message` 拼进 `LastError`（理论上可能携带路径）。目前 DS/宿主消息不含路径，且 UI 未直接显示 sink 文案 | UI 侧仍应只显示 typed code（与 B-2 的 D-10 口径一致） |

---

## 三、C-2 Theme Studio（pin `206b37223`）— **PASS_WITH_ISSUES**

### 3.1 已核实正确（关键项）
1. **真用生产服务，非 STUB**：`ThemeEngineThemeStudioService.CreateProduction`（`ViewModels/V2/ThemeStudio/ThemeEngineThemeStudioService.cs:71-93`）构造真实 `ThemeRegistry`+`ThemeSettingsStore`+`DesignSystemThemeLayerSink`+`ThemeService`（`isSandbox:false, persistsToDisk:true`）。`V2ThemeStudioTests` 与 `V2ThemeStudioScreenshotTests` 的 production 路径均走它（`CreateProductionService()`），`StubThemeStudioService` 只用于 fixture/沙箱（README §5 STUB-1 一致）；沙箱卡片在 UI 上明确标 `STUB`（截图 `studio-library-dark.png` 三张 fixture 卡可见 `STUB …` + `stub · fixture`）。
2. **应用/取消/回滚真实**：`CancelPreviewAsync→CancelSession`、`ApplyAsync`（InstallDraft→`_session.Commit()`→`ThemeService.ApplyAsync`→持久化）。测试断言真实副作用：`CancelPreview_RollsBackAppliedThemeAndPalette:153-182` 断言 `manager.AppliedPaletteId` 预览时=fixture、取消后回 `newmanga-default`；`PreviewSession_DoesNotPersistUntilApply:185-217` 断言预览期设置文件**字节不变**、应用后磁盘含新 id、**新 store 重新 Load 得同一 id**（重启保持）；`EditorDraft_Apply_PersistsAsUserTheme:258-293` 断言草稿另存为 `custom-*` 用户主题并写盘。
3. **编辑器草稿不碰应用级资源**：`PreviewDocument` 只设 `_localDraft`（`IsDraftPackageScoped=true`），测试断言 `manager.AppliedPaletteId` 不变、取消后草稿调色板清空（`:220-256`）。
4. **7 分区真实可用**：`ThemeStudioViewModel` 状态机 + 7 个 SectionView（AXAML 均有真实控件与绑定）；左栏 7 项（截图可见：主题库/预览/我的主题/主题编辑/外观/导入导出/恢复默认）、右栏摘要（当前主题/外观/对比度校验/持久化/GAP-3 说明/取消/应用）；24 张真渲染帧（99–252KB，`screens.json` 含 SHA-256/主背景/64 格签名/来源），我抽查 `studio-library-dark.png` 为真实 UI（非占位）。
5. **对比度审计用引擎公式**：`StudioContrastAuditor` 复用引擎 `ThemeContrast.Ratio`；测试 `ContrastAudit_UsesTheEngineFormula_AndFlagsFailures`；右栏 4 行数值+「通过/未通过」文字（截图 14.19:1/7.14:1/7.38:1/4.69:1 与「13 项全部通过」）。
6. **合规与诚实登记**：ThemeStudio XAML 我独立扫描 `(Margin|Padding|Width|Height|Spacing|CornerRadius|FontSize)="数字"`/`#XXX`/`BoxShadow|Gradient|Blur` → **0 命中**（仅注释文本命中），`V2ConformanceTests.V2XamlFiles` 覆盖全部 `Views/V2`+`Shell/V2` AXAML（含 ThemeStudio）；CONFORMANCE-1 的 `BorderThickness="0"` 已删除。GAP-3/NOT_WIRED-1/2/3/DEV-1/2/3 全部明示，未伪造；`FollowSystemAccent` 仅在作用域调色板生效且 UI 标注「（仅作用域）」（截图可见）与代码一致（`ThemeEngineThemeStudioService.cs:381-392`）。
7. **证据可对账**：`build.log` 0W/0E `BUILD_EXIT=0`；`test.log` 0 失败（App 294/6、ThemeEngine 229、DS 67、Host 42/24、CoreClient 42/25，`TEST_EXIT=0`）；测试计数与静态清点一致（23 `[AvaloniaFact]` + 2 个 Theory 的 11 个 case + 2 截图 = 36，README「36/36」成立）。

### 3.2 P2（须在 INT-1/L3 前修）
| # | 位置 | 问题 | 证据 | 建议 |
|---|---|---|---|---|
| **C2-P2-1** | `ViewModels/V2/ThemeStudio/ThemeStudioLibraryAndMyThemesViewModels.cs:17,20,28`；`ThemeStudioSectionItems.cs:148` | **C# 裸设计值 + 自述不实**：`MinCardWidth = 248`、`CardGap = 12`（注释自称「design-system space step 4」，即 `Nm.Space.S4`）、默认 `_cardWidth = 320`、卡 VM `_width = 320`（`Nm.Size.InspectorExpanded` 值）全部是 C# 字面几何；而 `verification/V11R-C-2/DEVIATIONS.md`「例外申请：无」与 README §6「生产 XAML/C# 中无裸间距」不成立。`V2ConformanceTests.AppCSharpFiles()` 的 `OwnedCSharpDirectories` **显式不含 ThemeStudio**（注释：归其 Owner 审查），因此无自动化门发现它 | 我按 conformance 同类正则独立扫描 ThemeStudio C# 得到上述 4 处 | 新增 `ThemeStudioMetrics`（与 ui-shell `ShellLayout`、ui-studio `StudioMetrics` 同构）运行期解析 `Nm.Size.TreeWidth/InspectorExpanded`、`Nm.Space.S4`；或按 §2.4 在 DEVIATIONS 逐项登记例外；并把 conformance 扫描扩到 `ViewModels/V2/ThemeStudio`（或新增 ThemeStudio 专属扫描测试） |
| **C2-P2-2** | `tests/.../V2ThemeStudioScreenshotTests.cs:198-249` + `verification/V11R-C-2/screens/pixel-hash.json` | **AC9「预览期画布像素不变」证据是恒真**：`RenderProbe` 把 `Border{Background=#123456, TextBlock Foreground=White}` **离线** `Measure/Arrange/Render(control)` 到独立 `RenderTargetBitmap`，未挂到应用资源/窗口样式树；探针颜色为字面值，任何主题/预览都不可能改变其像素 → `hash_before==hash_during==hash_after` 由构造保证，属 R-25 禁止的同义反复。且该测试**未断言**探针外「主题确实生效」（如 `manager.AppliedPaletteId`），JSON 里 `"passed": true` 还是字面量（非由比较派生），`method` 描述「a real preview session」也夸大 | `pixel-hash.json` 三个哈希完全相同、`applied_theme_before/after` 均 `newmanga-default`；测试体不涉及 `manager` 调色板断言 | 探针改为**挂在真实窗口内**的混合控件：一个使用 `{DynamicResource Nm.Color.Bg.Canvas}` 的 Border（断言预览期确实变为会话主题色）+ 一个 `WriteableBitmap` 画布（断言区域像素哈希不变）；`passed` 由比较结果写出；正向控制失败时测试应红 |
| — | 附 P3 | `rollback-preview` 帧只截图**从未比较**（只比较 before/after，`CellDifference<=3` 容忍 3/160 格），无法证明「预览确实改变过又回滚」 | `:119-143` | 断言 `preview` 与 `before` 至少 N 格不同（fixture 改字体/圆角，预期可见差异），否则 AC9 的「预览→取消」只证明「没变」 |

### 3.3 其余 P3
- `ThemeStudioViewModel` 的行为测试大量走 `CreateSandboxService()`（真实引擎+临时目录+`NullThemeLayerSink`），生产路径证据集中在 4 个 `CreateProductionService` 用例 + 截图；建议在 README 明确「行为=沙箱真引擎，应用级=production」的边界（当前 §4.1 基本写了，但 AC 表引用混用）。
- `Decode/GetPixel` 类图片比较仅在测试内使用，性能无碍。
- `INT_NOTES.md` 精确（含唯一 manager 约束、`CreateProduction` 签名、`ThemeStudioSurface` 入口）；`GAP-3` 需记入 C-1 follow-up 清单（避免只活在 C-2 文档里）。

---

## 四、C-3-READY（pin `9acddc23f`）— **FAIL（小修后可复审）**

### 4.1 P1（阻断 C-3 执行）
| # | 位置 | 问题 | 证据 | 建议 |
|---|---|---|---|---|
| **C3-P1** | `tools/v11r/rollback-theme-retire.ps1:70-77` + `verification/V11R-C-3-READY/rollback-dry-run.log`（4 行）+ `ROLLBACK_DRILL.md` §1/§2 | **回滚 dry-run 不可按文档执行、且证据不自洽**：①脚本在打印 Plan 之前就校验 tag，tag 不存在直接 `throw`（第 77 行），而脚本头与 ROLLBACK_DRILL 都把 `-DryRun` 排在 `-CreateTag` **之前** → 我实跑 `pwsh -File rollback-theme-retire.ps1 -DryRun` 得到 `exit=1, rollback tag 'v11r-pre-retire' does not exist; create it with -CreateTag before starting C-3`，**没有打印任何 Plan**；②交付的 `rollback-dry-run.log` 只有 `DRY RUN/repo/branch/dirty` 4 行、在 `dirty: True` 处截断，而 ROLLBACK_DRILL §1 引用的「L0 证据」块含 `tag : … (exists=False)` + 6 条动作（tag/备份/switch/build/grep/parse），**该块不在日志里**；③仓库当前确认无 `v11r-pre-retire` tag。→ 「L0 dry-run 已执行/通过」不成立；对高风险删除任务，回滚安全网的第一步未经验证 | 我实跑输出（未产生任何写操作：tag 仍不存在、`git status` 无新增） | 顺序修复：把 `-DryRun` 分支块移到 tag 存在性校验**之前**（DryRun 不要求 tag，打印 Plan 后 return）；然后重跑并把完整输出落为 `rollback-dry-run.log`（含 Plan/EXIT）；ROLLBACK_DRILL §1 的引用块与真实日志一致；R1 建 tag 后补一次「tag 存在」的 DryRun 证据 |

### 4.2 P2
| # | 位置 | 问题 | 证据 | 建议 |
|---|---|---|---|---|
| **C3-P2** | `verification/V11R-C-3-READY/contrast-matrix.json`（`"failures": 8`）；`DELETION_BATCHES.md` §4 末行「8 行/14 对未达标明细」；`DEPENDENCY_GRAPH.md` 引用同矩阵 | **未达标计数口径错误**：我逐 pair 统计 JSON 得到 **8 个未达标行 / 15 个未达标 pair**（dark 7 pair、light 8 pair、高对比 0），而 JSON 顶层 `failures: 8` 只数「行」且无 pair 计数字段；文档写「14 对」与实际 15 对不符（Lead 消息中的「14 对」也源自该文档）。L3 矩阵本身是真实计算（我抽查 #E9EAEC/#0F1012≈15.8、#E8B264/#0F1012≈9.96 等与 WCAG 公式一致，✘ 标注在 md 中逐 pair 如实） | 我用 JSON 遍历 `themes[].rows[].pairs[]` 统计 | JSON 增加 `failing_pairs: 15`（或 `failures: {rows:8,pairs:15}`）并保留 `rows`/`pairs` 明细；DELETION_BATCHES/C-3 README 改为「8 行 / 15 对」 |

### 4.3 P3
| # | 位置 | 问题 | 建议 |
|---|---|---|---|
| C3-P3-1 | `DELETION_BATCHES.md` §4「依赖图：609 引用/65 文件已分类」；§1 C 类「78 处/28 文件」；`DEPENDENCY_GRAPH.md` §6 标题「78 处 / 28 文件」 | 三个数字均陈旧：实际 JSON/生成器为 **631 引用/68 文件**，`evidence-or-documentation` 为 **86 处/30 文件**（§1 表也是 86/30，与 §6 标题自相矛盾） | 以生成器输出为准统一（建议生成时自动替换这些数字，避免手抄） |
| C3-P3-2 | `DELETION_BATCHES.md` §2 末「其余映射均已存在于当前 main 测试中（基线 `907339511` 全绿）」 | 基线引用旧（实际基线 `c5037b65`，README/依赖图已更新） | 改基线号 |
| C3-P3-3 | `doc/tasks/V11R-C-3.md` | 任务卡仍 `status: ready`/`delivery_head: null`，`allowed_paths` 写 `verification/V11R-C-3/` 而 READY 证据在 `verification/V11R-C-3-READY/`；AC 仍是 UI 模板 AC1–AC7 | Lead 回填执行卡（与 DELETION_BATCHES 的 R1–R6 对应）与正确 evidence 路径 |

### 4.4 已核实正确（C-3-READY 的有效部分）
1. **依赖图可复现、数字准确**：我按脚本同样的 `git grep -n -E '\b(12 符号)\b'` + 排除项在 pin 上重跑，得到 **631 行 / 68 文件**，逐符号首匹配计数 `ThemePackService=238、ThemePacks=108、ThemePack=81、LayoutProfile=56、LayoutKind=54、ThemePackMetrics=19、ShelfStyle=18、LayoutProfiles=18、NavPlacement=17、SettingsStyle=13、MotionProfile=9`，与 `DEPENDENCY_GRAPH.md` **完全一致**；`dependency-graph.json` 的 `baseCommit=c5037b65`、`repoHead=7f6787b91`、`workingTreeDirty=false` 诚实区分基线/证据头；假阳性（P/Invoke `StructLayout(LayoutKind…)` ×19、新架构同名 `LayoutProfile`、保护性 `DependencyBoundaryTests` 引用）均有说明。
2. **新壳零旧依赖**：`apps/desktop-avalonia/src/NewManga.App/Shell/**` 对 12 旧符号引用 **0**（我独立 grep 复核），「C-3 只删旧 Views/旧 ViewModels/旧测试/NewManga.Theme，不触碰新壳」成立。
3. **迁移门测试真端到端（26/26）**：`LegacyThemeRetirementGateTests.cs` 26 例 = 表完整性 1 + 9 旧 ID 文件级端到端（旧文档形状 `theme`/`variant` 写入→真实 `ThemeSettingsStore.Load`→断言迁移 appearance/density/NOT 重复告警→`SaveAsync`→重新 Load 干净）+ 未知 ID（有/无 registry）2 + 空/缺失 3 + 旧键组合 1 + 首启 1 + 幂等 9；`migration-gate-tests.log` 26/26。
4. **删除批次可执行**：`DELETION_BATCHES.md` A（5 旧测试 + 旧项目/工程行/启动钩子）/B（10 个生产文件，逐文件迁移动作与前置）/C（证据 pin 保护）分类清晰；R1–R6 顺序、每步前置/验证/回滚点明确；5 条「需新增」断言被显式列为 R4 硬门（不满足不得删旧测试），这是**正确**的谨慎设计。
5. **日志**：`build.log` 0W/0E；`test.log` App 237/6 全绿；`themeengine-tests.log` 229/229。
6. **角色边界**：C-3-READY 只改测试/tools/证据（`43609ddbe` = 4 文件 947 行新增），未改 DS/ThemeEngine/App 产品代码；`README` 明确「C-3 执行时必须重跑依赖图，不能沿用旧 JSON」。

---

## 五、UNVERIFIED（只读/未重跑）
| 项 | 说明 |
|---|---|
| 三个 pin 的 build/test 日志真实性 | 未重跑（禁写 bin/obj）；只做「日志↔代码↔断言」一致性抽查，数字与代码/测试清点自洽 |
| C-1 真机/系统跟随/Trim-AOT/屏幕阅读器 | Owner 已登记 NOT_RUN；我亦无实机环境 |
| C-2 生产 UI 在真实 App 内可用 | INT-1 未接线（NOT_WIRED-2/3），当前仅 headless 窗口 + 生产服务；真机主题切换/文件选择器未验 |
| C-2 预览期画布像素 | 见 C2-P2-2：现有证据不可信，需按建议重构后就真实窗口复核 |
| C-3 回滚 L1/L2 | 文档自注 NOT_RUN；L0 见 C3-P1 |
| C-3 零引用门终态 | 只能在 C-3 执行时重跑判定；本次只验证 READY 包数字可复现 |
| Lead 消息「14 对未达标」 | 与实测 15 对不符（见 C3-P2） |

---

## 六、最终判断

### 各对象
- **C-1：PASS**。Part B 真实、R-21 正确、零依赖断言成立、证据可对账、NOT_RUN 诚实；P3 均不阻塞。可计入 M3 的主题引擎前置。
- **C-2：PASS_WITH_ISSUES**。真实引擎接线与应用/取消/回滚已是本域最强证据；但 AC4 自述（无裸值/无例外）与 AC9 像素证据两处不实，须修后才满足 L3 的「证据不靠字面量/同义反复」。
- **C-3-READY：FAIL（小修后复审）**。依赖图、迁移门、删除清单三件核心交付扎实且可复现；但**回滚安全网的 dry-run 机制与证据不成立（P1）**，对比度计数口径错误（P2），清单数字陈旧（P3）。

### 是否可进入 C-3（旧主题退役执行）
**暂不可**。建议先完成最小修复集（预计 0.5 天量级），再由 Lead 发起一次**窄复审**（只需重看 C-3-READY 三处 + 新 dry-run 日志，不必重审 C-1/C-2）：
1. **C3-P1**：DryRun 移到 tag 校验前 → 重跑生成完整 `rollback-dry-run.log`（含 Plan/EXIT）→ 更新 ROLLBACK_DRILL §1 引用；
2. **C3-P2**：对比度 JSON 增加 `failing_pairs` 并修正文档为「8 行/15 对」；
3. **C3-P3**：统一删除清单/依赖图数字（631/68、86/30）与基线号，回填 C-3 任务卡。

C-1 引擎侧前置**已满足**；C-2 的两个 P2 不阻塞 C-3 删除，但必须在 **INT-1/L3 验收前**修复（否则导入主题后 UI 布局值不受令牌控制、AC9 像素证据会被独立复审再次驳倒）。

**建议复审 pin**：C-3-READY 新 fix head（重生成证据后）；C-1/C-2 若开返修窗口，用各自新 fix head（C-2 必须含 ThemeStudioMetrics + 真实窗口像素探针）。
