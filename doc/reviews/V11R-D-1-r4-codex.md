## 结论：PASS_WITH_ISSUES

固定 pin 的状态徽标测试覆盖了 **3 个表面 × 9 个状态 × 4 种主题模式**。它从渲染帧采样徽标像素、校验合成背景，再分别计算图标与文字的对比度，门槛均为 ≥4.5:1；日志记录测试通过。`statusMuted` 未变，矩阵脚本日志、JSON 与矩阵文档一致显示 **0 行 / 0 对未达标**。令牌与主题生成器的 `--check` 日志也都报告生成物与来源逐字节一致。

| r3 项 | 结论 | 证据 |
|---|---|---|
| P1 状态对比度 | **CLOSED** | [BadgeCompositeContrastTests.cs:25](/G:/CODEX/New%20Manga/apps/desktop-avalonia/tests/NewManga.DesignSystem.Tests/BadgeCompositeContrastTests.cs:25)、[I3 DISPOSITION:8](/G:/CODEX/New%20Manga/verification/V11R-D-1/I3/DISPOSITION.md:8)、[contrast-matrix.log:3](/G:/CODEX/New%20Manga/verification/V11R-D-1/I3/contrast-matrix.log:3) |
| P2-1 ApplyPalette 排除 overlays 与 ReducedMotion 回归测试 | **CLOSED** | [DesignSystemThemeManager.cs:722](/G:/CODEX/New%20Manga/apps/desktop-avalonia/src/NewManga.DesignSystem/Theming/DesignSystemThemeManager.cs:722)、[ThemeManagerI2Tests.cs:138](/G:/CODEX/New%20Manga/apps/desktop-avalonia/tests/NewManga.DesignSystem.Tests/ThemeManagerI2Tests.cs:138) |
| P2-2 VisualEvidence 恒真断言 | **CLOSED** | [VisualEvidenceTests.cs:50](/G:/CODEX/New%20Manga/apps/desktop-avalonia/tests/NewManga.DesignSystem.Tests/VisualEvidenceTests.cs:50) |
| P2-3 I2 README 计数 | **CLOSED** | [I2 README:25](/G:/CODEX/New%20Manga/verification/V11R-D-1/I2/README.md:25)、[I3 DISPOSITION:11](/G:/CODEX/New%20Manga/verification/V11R-D-1/I3/DISPOSITION.md:11) |
| P2-4 FocusRing 裁剪与泄漏测试 | **PARTIAL** | 描边裁剪及视口重算已实现：[FocusRing.cs:149](/G:/CODEX/New%20Manga/apps/desktop-avalonia/src/NewManga.DesignSystem/Theming/FocusRing.cs:149)。循环测试只断言最终仅有一个 ring、禁用后无可见 ring，**没有直接检查事件订阅数**：[FocusRingBehaviourTests.cs:85](/G:/CODEX/New%20Manga/apps/desktop-avalonia/tests/NewManga.DesignSystem.Tests/FocusRingBehaviourTests.cs:85) |
| P2-5 Task `allowed_paths` 与范围说明 | **CLOSED** | [V11R-D-1.md:20](/G:/CODEX/New%20Manga/doc/tasks/V11R-D-1.md:20)、[V11R-D-1.md:70](/G:/CODEX/New%20Manga/doc/tasks/V11R-D-1.md:70) |
| P3 provider 顺序 | **CLOSED** | [ThemeManagerI2Tests.cs:160](/G:/CODEX/New%20Manga/apps/desktop-avalonia/tests/NewManga.DesignSystem.Tests/ThemeManagerI2Tests.cs:160)：断言 `global<palette<contrast<density<motion` |

**新问题（P2）**：FocusRing 测试名称声称覆盖 handler 泄漏，但实际断言无法区分“订阅已释放”和“隐藏的重复 handler 仍留存”。应补能观察订阅/回调次数的断言，或收窄测试名称与处置结论。

状态色调整未发现新的 P1/P2 用途冲突：`statusMuted` 保持不变；矩阵重新计算与生成器检查的记录相互吻合。ThemeEngine 对边缘表面的 warning 断言也检查了默认主题 warning 集合为空，并保留低对比输入的独立错误测试：[ThemeValidatorTests.cs:275](/G:/CODEX/New%20Manga/apps/desktop-avalonia/tests/NewManga.ThemeEngine.Tests/ThemeValidatorTests.cs:275)。

## 收口与基线建议

**D-1 目前不建议标为 `done` 或 `closed_with_limitations`，也不建议作为正式 UI 冻结基线。** 这轮窄复核除上述测试缺口外，Task 卡仍记录 `status: in_progress`、`integration_commit: null`、`canonical_evidence_status: pending` 和 `resource_closeout_status: pending`：[V11R-D-1.md:1](/G:/CODEX/New%20Manga/doc/tasks/V11R-D-1.md:1)。r3 报告指定路径在当前仓库缺失；本次以 I3 处置表和固定 pin 证据核查，未据此重审历史。

推荐下一步：由 DSH 处理 FocusRing handler 泄漏测试缺口并完成 D-1 Task 生命周期字段及证据 pin 的收口核验，再决定是否冻结 UI 基线。