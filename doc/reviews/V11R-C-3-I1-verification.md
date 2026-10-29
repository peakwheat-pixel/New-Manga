# V11R-C-3-I1 窄验证（只核 7 项遗留 P2）

**验证者**：reviewer（独立、只读，未参与实现；本次写操作仅本文件）。
**Pin**：`4d65f8aea3d2f9335b41df63396b67b5565491e5`（C-3-I1 修复提交，父 `7bfb11033`）；增量 `git diff 7bfb11033..4d65f8aea`（30 文件，范围与 7 项一致，无范围外代码改动）。合并解析参考 main `4374dfeae`。
**纪律**：只核这 7 项，不重审 R1–R6 历史；未重跑 dotnet build/test / 未重跑 R6 smoke（以 pin 内代码、测试与证据为准，未核项注明）；未改代码/证据。

---

## 逐项结果

| # | 项目 | 结果 | 依据（一句） |
|---|---|---|---|
| 1 | 旧壳外观切换同步 DS palette（`MainWindow`/`CycleTheme`/设置页 → `SetAppearance`，断言 dark/light 解析值变化） | **CLOSED** | `MainWindow` 新增共享 `DesignSystemThemeManager`（`MainWindow.axaml.cs:26,50-58`）；`CycleTheme:543-550` → `ApplyAppearance:560-585` 同时设 `RequestedThemeVariant` 并 `_themeManager.SetAppearance(...)`，`OnThemeApplied:588-592` 兜底再同步；设置页 `Pages.SwitchVariant:1337-1345` 经 `_onThemeApplied`（`MainWindow:115` 传入 `OnThemeApplied`）走同一路径；`LegacyAppearanceSyncTests` 两例分别断言 `manager.Appearance==Light/Dark`、`Nm.Color.Bg.App` 解析值等于对应 variant 值、且渲染帧 SHA-256 发生变化（top-bar 与设置页两条路径）。生产入口 `App.axaml.cs:145-146` 把 `_designSystemTheme` 注入 legacy `MainWindow`。 |
| 2 | `--theme` 迁移 appearance/density 真的应用，`--variant` 优先 | **CLOSED** | 新增 `Services/LegacyStartupTheme.Resolve(themeId, variant)`：显式 variant 优先，否则取 `LegacyThemeMigration` 迁移后的 appearance/density（`saber-light→Light`、`saber-purple→Dark`、`macos-launchpad→Compact`、`newmanga-default→null`、未知→Dark 恢复）；`App.axaml.cs` 用它得到 `startupTheme`，`Initialize(startupAppearance)` + `SetDensity(startupDensity)` 真正喂给 DS（pin 版 `startupAppearance = startupTheme.Appearance`；main `4374dfeae:App.axaml.cs:41` 已按 Lead 裁定改为 `StartupAppearance(options) ?? startupTheme.Appearance`，`StartupAppearance:138-143` 只解析 `--variant`，与 helper 内部优先级一致）。`LegacyStartupThemeTests` 5 例覆盖上述映射与「显式 variant 胜出」。 |
| 3 | R4 替代断言补新壳等价覆盖（`R4-ASSERTION-MAP.md`），无「只测旧壳」空洞 | **PARTIAL** | 映射表逐行给出旧→v2 对应，且新增 `ThemeRetirementR4Tests.V2_shell_starts_with_first_frame_and_shares_the_design_system_manager`（`AppShellV2.CreateRoot` 真实 v2 根、StartGate 未放行仍可见+内容已挂载、`manager.SetAppearance(Light)` 后 `Nm.Color.Bg.App` 解析值变化、`Content` 引用不变）与 `V2_shell_window_material_uses_the_same_os_fallback_policy`（v2 `TransparencyLevelHint` 按 `WindowMaterial.ForCurrentOs()`）两例；v2 的 Theme Studio 入口在 pin 已真实接线（`App.axaml.cs:99-102` `CreateProduction`+`RegisterSurfaceWorkspace`），映射表该行不再是空头承诺。**残余空洞**：R4 中「窗口 chrome 只做视觉、不改窗口行为」一行只有 legacy `MainWindow` 断言（`SystemDecorations`/`CanResize`，`ThemeRetirementR4Tests:57-67`），v2 `CreateRoot` 虽未覆盖这两项（`AppShellV2.axaml.cs:90-118` 只设 Title/尺寸/Background/材质），但**没有 v2 侧 `SystemDecorations`/`CanResize` 断言**——该行仍是「只测旧壳」（P3，建议补 2 个断言即可）。 |
| 4 | R6 干净树重跑、`R6-v2-host.log`/文件清单齐全、两个 shell 正常退出码（非 harness kill） | **NOT_CLOSED** | 三处证据均缺失或不符：①`verification/V11R-C-3/R6-report-clean.md` **在 pin 与整个仓库任何 ref 中都不存在**（`git log --all -- "*R6-report-clean*"` 为空；pin→main 的 `verification/V11R-C-3` 无任何新增；只有 `README.md`/`C3-I1-DISPOSITION.md` 引用它）；②`R6-v2-host.log` 不存在（只有 `R6-host-startup.log`，内容为 `single-instance acquired: C3R6-legacy` 的 **legacy** 运行，以及 `R6-legacy-host.log`）；③`R6-startup-smoke.log` 仍是旧运行（03:49），两个 shell 均 `terminated_by_harness_after_verification=true`，**无退出码**，`R6-report.md` 原文仍写「启动后由 harness 终止」；④「干净树」无证据：`final/dependency-graph.executed.json` 为 `workingTreeDirty=true`（03:34 执行态），`final/contrast-matrix.executed.json` 无 dirty 字段，R6 日志均早于 I1（04:18）。注：pin 中 `AppOptions.ExitAfterMs`/`--exit-after-ms` 已存在且 `App.axaml.cs:69-78` 会定时优雅关窗，因此**修复成本很低**（重跑 smoke 即可），属证据未交付而非能力缺失。 |
| 5 | `V11R-C-3-READY/*` 原始字节已还原，C-3 证据只写 `verification/V11R-C-3/**` | **CLOSED** | 以 `b5f7d88fc`（C-3 执行前基线，含 `0a89e2074` 的 READY 窄复审修复）对比：`git diff b5f7d88fc 4d65f8aea -- verification/V11R-C-3-READY` **为空**（12 文件逐字节还原；与 r1 审查的 `9acddc23f` 有 6 文件差异，系窄复审修复，属预期基线前移）；被覆盖的 6 个执行态副本完整保存在 `verification/V11R-C-3/final/*.executed.*`；两个工具默认输出已改到 C-3 执行证据路径（`build-dependency-graph.ps1` `OutputDirectory=verification/V11R-C-3`；`contrast-matrix.ps1` `DataPath=verification/V11R-C-3/contrast-matrix.json`），`task` 字段改为 `V11R-C-3` 并新增 `workingTreeDirty`。注：`contrast-matrix.ps1` 仍写共享交付物 `verification/V11R-D-1/contrast-matrix.md`（D-1 的 L3 矩阵本身，非 READY 包），属预期。 |
| 6 | `LegacyChrome` 硬编码 fallback → 令牌或显式 fallback 常量/例外 | **CLOSED** | 6 个 fallback 画笔改为显式中性常量（`#202020/#101010/#E0E0E0/#A0A0A0/#C8A060`）并注释「仅在 DS 资源缺失时使用，DS 存在时 `Resource()` 优先」；`LegacyMetrics` 的 12/8/6 圆角改为具名兼容常量，并在 `verification/V11R-C-3/DEVIATIONS.md` D-C3-1 登记为契约 §2.4 例外（说明 DS radius.sm/md=2/3px 无法等价、随旧壳删除而消失）。 |
| 7 | FocusRing 测试补可观测订阅/回调断言（D-1 r4 的 P2） | **CLOSED** | `FocusRing` 新增 internal `IsSubscribedFor`/`PositionCallCountFor`（`InternalsVisibleTo=NewManga.DesignSystem.Tests`，`FocusRing.cs:34-41,294-299`，`Position` 计数 `:149-152`）；测试在 25 轮 enable/disable 中逐次断言订阅存在/释放，再断言 focus 使 `PositionCallCount` 增长、禁用后再 focus 不增长，并保留最终唯一 ring 断言（`FocusRingBehaviourTests` diff）。不再依赖「最终只剩一个 ring」的间接证据。 |

---

## 附加发现（不影响上述判定，供 Lead 决定是否要求补）

| 级别 | 内容 |
|---|---|
| P2（证据完整性） | **无 C-3-I1 的构建/测试日志**：`C3-I1-DISPOSITION.md` 声称 `dotnet build` 0W/0E、`dotnet test` 0 fail（含新增测试），但 pin 内 `verification/V11R-C-3/` 的 `R6-build.log`/`R6-test.log` 仍是 I1 之前（03:49，App 271/7）的执行，新增的 `LegacyAppearanceSyncTests`(2)/`LegacyStartupThemeTests`(5)/`ThemeRetirementR4Tests`(+2) 没有对应测试日志。我未重跑，无法确认这些新测试在 pin 上实际通过（代码/测试静态一致，但证据缺位）；D-1 I3 的 `FocusRingBehaviourTests` 变更同样无 post-I3 日志。建议随 R6 clean 重跑一并产出。 |
| P3 | `R6-report.md` 仍写「终态 `dependency-graph.json` 已写入 `verification/V11R-C-3-READY/`」与「由 harness 终止」，与 I1 的 READY 恢复/优雅退出承诺矛盾，未同步更新（与项 4 同源）。 |
| P3 | `R4-ASSERTION-MAP.md` 的 v2 主题入口行依赖 `App.axaml.cs` 的 Theme Studio 接线（pin 已有、代码正确），但该 App 级接线无自动化测试（headless 直接构造 `AppShellV2`）；可在 INT 验收时补一条 `--shell=v2` 启动 smoke 断言。 |
| P3 | `LegacyStartupThemeTests` 只测 helper 输出；`App.axaml.cs` 中 `Initialize(startupAppearance)`/`SetDensity` 的 App 级应用无测试（需真实 App 生命周期，成本高），以代码审查确认。 |

---

## 结论

- 7 项中：**CLOSED 5 项**（1/2/5/6/7）、**PARTIAL 1 项**（3，仅剩 v2 chrome decorations/CanResize 断言）、**NOT_CLOSED 1 项**（4，干净树 R6 证据/两份日志/退出码全部缺失）。
- 另有 P2：C-3-I1 自身无 post-fix build/test 日志。

**C-3 是否可 closed：否**（须先补项 4 的干净树 R6：`--exit-after-ms` 优雅退出、记录两个 shell 退出码与完整文件清单、`R6-v2-host.log`、`dirty=false`，并写回 `R6-report-clean.md` 与 README/DISPOSITION 引用；建议同时附 post-I1 build/test 日志）。**D-1 是否可 closed：可**（其 r4 唯一 P2 = FocusRing 可观测性断言已 CLOSED；D-1 的 I3 自证日志属其自身证据链，不影响本结论）。
