# V11R-D-1 I3 处置表（r3 终审）

- 分支：`v11r/d1-i3`；基线 main `b5f7d88fc`（已含 C-3 退役）
- 结论：**r3 P1 CLOSED，P2×5 + P3 CLOSED**；全量测试 0 fail。

| # | r3 发现 | 处置 | 证据 |
|---|---|---|---|
| P1 | 状态对比度承诺未满足：徽标只测 Bg.Panel；dark blocked 合成到 raised ≈4.26:1 | **方案 (a) 提高状态前景令牌**：标准盘 dark 7 + light 7、HC dark 4 + light 1 最小上调，使 panel/raised/overlay 三类合成背景全部 ≥4.5:1（带渲染余量）；statusMuted 不变；DECISION_LOG §7 | `badge-surface-tests.log`（3 surfaces × 9 状态 × dark/light × standard/HC 全绿）；`contrast-matrix.log`（0 行/0 对）；`contrast-matrix.json` |
| P2-1 | ApplyPalette 从 provider 栈复制非颜色键时会把 ReducedMotion 的 Slow=0 持久化到主题层 | ApplyPalette 继承路径新增 `includeOverlays:false`，跳过 contrast/density/motion overlay（`IsOverlayProvider`）；补“开 ReducedMotion→ApplyPalette→关→Slow 恢复 220ms”测试 | `ThemeManagerI2Tests.ApplyPalette_does_not_copy_transient_reduced_motion_values`；`focus-provider-tests.log` |
| P2-2 | VisualEvidenceTests:52 恒真断言 | 改为切换前后比较 `window.Content` 引用与首个 visual root 引用，且窗口仍可见 | `VisualEvidenceTests.cs`；`test.log` |
| P2-3 | I2 README 写 6 行/6 对、矩阵 md 实为 6 行/7 对 | I2 README 改为实测 6 行/7 对并列出 7 对；注明 I3 后矩阵为 0/0；矩阵由脚本重算 | `verification/V11R-D-1/I2/README.md`；`contrast-matrix.log` |
| P2-4 | FocusRing 可见性未计入描边；订阅泄漏未测 | ScrollViewer 裁剪判定计入 stroke 四边（窗口边界仍由窗口裁剪）；EffectiveViewportChanged 已订阅并用于重算；新增 25 次 enable/focus 循环后仅一个 ring、禁用后无可见 ring 的泄漏测试 | `FocusRing.cs`；`FocusRingBehaviourTests.Repeated_enable_and_focus_cycles_do_not_leak_rings_or_handlers` |
| P2-5 | Task allowed_paths 与实际改动不一致 | 更新 `doc/tasks/V11R-D-1.md`：补 App.axaml/App.axaml.cs/csproj、MyThemesSectionView.axaml、ThemeEngine 测试、tokens/DECISION_LOG、verification/V11R-C-3-READY，并加“范围说明”记录越界理由 | `doc/tasks/V11R-D-1.md` |
| P3 | provider 排序测试只断言 global<palette | 新增 `Every_overlay_provider_sits_after_the_palette_in_the_fixed_order`：按 distinct 值定位 global/palette/contrast/density/motion，断言 global<palette<contrast<density<motion | `focus-provider-tests.log`（6/6） |

## 验证

- `dotnet build NewManga.sln -warnaserror`：0 warning / 0 error（`build.log`）
- `dotnet test NewManga.sln --no-build`：**0 fail**（App 274+7skip、ThemeEngine 235、DS 85、Host 49+28skip、CoreClient 116+25skip）（`test.log`）
- token/theme 生成器 `--check`：byte-for-byte up to date（`token-gen-check.log`、`theme-gen-check.log`）
- L3 矩阵：标准盘未达标 **0 行 / 0 对**（`contrast-matrix.log` / `contrast-matrix.json`）
