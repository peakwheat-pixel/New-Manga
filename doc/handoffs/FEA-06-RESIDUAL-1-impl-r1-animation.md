---
task_id: FEA-06-RESIDUAL-1
author: Codex CLI（fresh 实现会话；非 Reviewer）
recipient: DeepSeek Harness
base_commit: e4b5a0e887e64e8e810a46e483c1a74daac0a4ee
delivery_head: 033c8b4b9d285b5717d7c2697587c36c80bd41b1
status: delivered
---

# Handoff：FEA-06-RESIDUAL-1 impl-r1 剩余动画

## 交付结果

本次仅完成用户明确释放的 R1-001 三项剩余动画：浮层退出 160ms、按钮 pressed 90ms、状态圆点/badge 出现 150ms。实现提交为 `033c8b4b9d285b5717d7c2697587c36c80bd41b1`，消息 `fix(fea-06-residual-1): R1-001 补齐退出与反馈动画及可控帧测试`。本 Handoff 与验证日志在后续文档提交中追加；未 push。

三项均真实消费 `MotionTimingProfile` 的对应参数。reduce 或对应分类关闭时为 0ms，同步应用终值；未修改 Core、契约、schema、依赖、生成物、冻结设计、Current V2、组合根、FrontendSelector 或 FEA-07 稳定窗口 seam。没有创建或关闭 Task，也没有改写既有 Review、Task/STATUS/Plan、checkpoint 或旧 PNG。

变更文件（均位于允许路径）：

| 文件（`apps/desktop-avalonia/` 下） | 行为 |
|---|---|
| `src/NewManga.App/Views/Fluent/FluentFrameAnimation.cs` | internal 可注入帧时钟；生产使用单调 Stopwatch 时间和 `TopLevel.RequestAnimationFrame`，无 DispatcherTimer/后台轮询；generation 取消旧帧，detach 收敛终值。测试仅替换帧源，沿用生产插值与完成逻辑。 |
| `src/NewManga.App/Views/Fluent/FluentFeedbackMotion.cs` | `Button.IsPressed` 驱动 90ms 缩放至 0.98，释放复原；带 `fluent-feedback-badge` 类的圆点出现时 150ms 淡入、缩放 0.9→1。只写 RenderTransform/Opacity，不改变尺寸、位置或语义状态。弱表保存每控件实例，避免重复订阅。 |
| `src/NewManga.App/Views/Fluent/FluentShellSurface.axaml.cs` | 退出使用解析后的 160ms 和冻结 `SplineEasing(.4,0,1,1)`；host 保留至透明完成，焦点立即返还、停止命中测试；逻辑 Esc 不等待视觉退出。快速重开取消旧退出，reduce/关导航分类立即收敛。反馈配置覆盖 logical/visual tree、缓存页和新命令行，原生 pointer/key 事件前为动态按钮接入 pressed。 |
| `src/NewManga.App/Views/Fluent/SettingsPageView.cs` | 设置未保存圆点标记为 feedback badge；原可见性、文案、语义色与自动化名称不变。 |
| `src/NewManga.App/Views/Fluent/WorkbenchPageView.cs` | 同样标记译文未保存圆点；检查器标题保持挂载，重绘只重建标题之后的内容，防止真实 Draft 编辑立即打断圆点动画。最终树结构、布局和业务行为等价。 |
| `tests/NewManga.App.Tests/FluentAnimationCompletionTests.cs` | 新增 16 个用例，断言真实有效属性、精确边界、真实 Space/Mouse 输入、真实 Draft 编辑、分类独立、reduce、快速重开、detach 与生产渲染帧源。 |
| `tests/NewManga.App.Tests/ManualFluentMotionClock.cs` | 测试用 internal 帧源，`Advance(ms)` 同步推进生产动画；没有测试专用完成分支。 |
| `tests/NewManga.App.Tests/FluentCommandPaletteFocusTests.cs` | 只增加时钟注入与退出后的 `Advance(160)`/RunJobs，保留全部原断言。 |
| `tests/NewManga.App.Tests/FluentResidualSettingsLeaveTests.cs` | 同上，仅为原 R1-005 用例推进退出时钟，保留全部原断言。 |

## 验证证据

环境：Windows NT 10.0.26300.0、PowerShell 7.6.8、.NET SDK 10.0.401；Debug/net9.0、Avalonia Headless + Skia。完整输出、每条命令 EXIT、逐程序集计数、57 条 skip 及原因、PNG SHA 与断言位置均在 [impl-r1-animation-verification.log](../../verification/FEA-06-RESIDUAL-1/impl-r1-animation-verification.log)。所有测试在与交付提交相同的源码/测试字节上执行，之后仅提交实现与文档。

| AC/场景 | 实际命令/步骤 | 被测版本 | 结果 |
|---|---|---|---|
| 构建 | `dotnet build apps\desktop-avalonia\NewManga.sln --nologo` | `033c8b4b9` 对应源码 | PASS；EXIT=0，0 警告/0 错误 |
| 全量回归 | `dotnet test apps\desktop-avalonia\NewManga.sln --no-build --settings apps\desktop-avalonia\tests\NewManga.runsettings --nologo` | 同上 | PASS；EXIT=0；**1213 passed / 0 failed / 57 skipped**，总数 1270；基线 1197/0/57，新增 16、未删除测试 |
| 时序稳定性 | App.Tests 定向筛选新增动画与两个原有用例（完整原样命令见日志 `STABILITY_RUN=1…3`） | 同上 | 连续 3 轮各 18/0/0，EXIT 均 0 |
| 治理 | `pwsh -NoProfile -File tools\governance\check.ps1` | 同上 + 新证据 | PASS；EXIT=0；3 个既有 warning |
| 冻结 pin | `pwsh -NoProfile -File tools\governance\verify_pins.ps1` | 同上 | PASS；EXIT=0；15/15 |
| 旧 PNG 字节 | `Get-FileHash -Algorithm SHA256 verification/FEA-06/screens/*.png` 对照冻结 pin | 同上 | 四张 SHA-256 均匹配，零漂移；未启用截图 opt-in |
| 修改范围 | `git diff --name-only e4b5a0e887e64e8e810a46e483c1a74daac0a4ee 033c8b4b9d285b5717d7c2697587c36c80bd41b1`；`git diff --check` | 同上 | 仅上述 9 个实现/测试文件；EXIT=0 |

断言入口均在 `FluentAnimationCompletionTests.cs`：

- 退出：第 61 行用可控帧验证 80ms ease-in 中间值、159ms host 仍可见、160ms 透明且隐藏，并在推进前验证立即返焦；第 388 行用生产 `RequestAnimationFrame` + `ForceRenderTimerTick()` + Stopwatch 验证实际隐藏时间 ≥160ms。生产帧源用例有 3s 失败上限，5ms 轮询不承担插值时序判定。
- pressed：第 125 行真实键盘/鼠标输入，45ms 为中间值、89ms 未结束、90ms ScaleX/Y=0.98；释放后 90ms 回到 1，布局 Bounds 不变。
- badge：第 159 行设置/工作台圆点 Opacity 0→1、Scale 0.9→1，75/149ms 中间值、150ms 完成、重新出现重播；第 201 行真实 Draft 编辑与反复 Render 仍完整运行 150ms，动态按钮同样消费 90ms。
- 降级与生命周期：第 93/262/295 行验证静态/运行中 reduce、Full+分类关闭、Navigation/Feedback 独立生效；第 328/349/369 行验证 detach、快速重开与第二次 Esc 不被退出动画延迟。

57 个 skip 均为既有 sidecar fixture 前置未满足（`NEWMANGA_CORECLIENT_SIDECAR_DIR` 未设置）；App=7、CoreClient=22、Host=28，逐项在日志列出。它们未计入通过数。本次没有原生真机视觉、200% DPI 或 a11y 矩阵验收（NOT_RUN），没有把 headless 结果解释为原生视觉验收通过。

## 接收方式

仓库/worktree：`G:\CODEX\New Manga`；branch：`main`；Git common directory：`.git`。恢复点为 base `e4b5a0e887e64e8e810a46e483c1a74daac0a4ee` → 实现 head `033c8b4b9d285b5717d7c2697587c36c80bd41b1`，另有随后追加的本 Handoff/日志文档提交。没有新增依赖、共享接口或 schema 变更，无迁移与资源删除。

自动复现：构建后对 `FluentAnimationCompletionTests` 使用 `--filter FullyQualifiedName~FluentAnimationCompletionTests`；完整命令及三轮稳定性运行见日志。交互复现：Fluent + full 打开命令面板后 Esc，应立即返焦、160ms 淡出；按住按钮应在 90ms 缩至 0.98；编辑设置或工作台译文应使圆点在 150ms 淡入并从 0.9 缩放到 1。改 reduce 或关闭相应分类后上述行为均瞬时。

本次用户明确要求 fresh Codex 实施这三项动画，覆盖历史 D-10 的旧实施者安排。既有 Task、Review 和 checkpoint 原字节保留；请 DSH 接收后处置当前指针、Review Appointment 与剩余原生验收口径。

## 下一任务建议（必填）

- Task / 标题：`FEA-06-RESIDUAL-1` 的 fresh impl-r2 独立上下文复核；启动条件为 DSH 接收本交付并冻结 reviewed_head。不是释放新的实现节点。
- Agent / Reviewer：DSH 指派新的 Codex 或 ZCode 会话；本实现会话不得自审。DSH 保留 finding 处置和最终集成责任。
- Recovery point：`G:\CODEX\New Manga`、`main`、同一 worktree；切片 base=`e4b5a0e887e64e8e810a46e483c1a74daac0a4ee`，实现 head=`033c8b4b9d285b5717d7c2697587c36c80bd41b1`；完整 Task 原 base=`82529a3d5864a39f362e414b67bca774d743f862`。若需独立 worktree，待 DSH 创建。
- Scope：只读被审源码/测试；写入范围由 DSH Appointment 冻结为新 Review 与新复核证据。禁止修改实现、Core、契约、schema、生成物、冻结设计、Current V2、组合根、FrontendSelector、FEA-07 seam 和既有证据，无共享接口/依赖变更授权。
- Deliverables：新 `doc/reviews/FEA-06-RESIDUAL-1-impl-r2.md`，记录精确 reviewed_head、上下文来源/会话 ID、R1-001…009 逐项结论与限制；复核证据路径由 DSH 冻结。
- Verification / Gate：重复上表四条必跑命令、三项边界与分类降级断言、旧 PNG 零漂移；不得少于 1213 passed，57 skip 单列原因；不能把 NOT_RUN 原生矩阵计为 PASS。上下文独立 Review + DSH finding 处置/集成验证通过后，才可推进 Task 生命周期。
- 可直接转发的指令：

> 在 `G:\CODEX\New Manga`（branch/main；worktree 同路径）以全新独立上下文只读复核 `FEA-06-RESIDUAL-1`。实现 head 固定 `033c8b4b9d285b5717d7c2697587c36c80bd41b1`，本切片 base `e4b5a0e887e64e8e810a46e483c1a74daac0a4ee`，完整 Task base `82529a3d5864a39f362e414b67bca774d743f862`。读取当前 Task/impl-r1、本 Handoff 与 `verification/FEA-06-RESIDUAL-1/impl-r1-animation-verification.log`，独立复核 R1-001…009，尤其退出160ms且立即返焦、pressed90ms、badge150ms、reduce/分类关闭瞬时以及真实生产帧推进。禁止参与返修或修改生产/冻结文件，仅在 DSH 冻结的 Review/新证据路径交付结论，Review 记录来源/会话ID。实跑本 Handoff 所列 build、全量 test、check.ps1、verify_pins.ps1 四条命令与 PNG SHA 核对，计数基线1213/0/57，skip/NOT_RUN 分列；交付 `doc/reviews/FEA-06-RESIDUAL-1-impl-r2.md`，不得 push，由 DSH 处置与集成。

## 风险与遗留

本切片三项实现无未完成项；项目 Task 尚未独立复核或集成关闭。新机制是有限帧动画，窗口/页面 detach 时收敛为终值，旧帧不再更新，未引入 DispatcherTimer。退出期间保留的 host 仅用于淡出，逻辑焦点与 Esc 已即时释放。无新增源文件访问、数据写入、数据删除、许可或依赖风险。

原生视觉验收仍交 DSH 按 Task 既有边界处置。本 Handoff 只报告实现自测，不签发独立 Review 或 Task DONE。回退可由 DSH 对实现提交执行普通 revert；不要恢复或覆盖旧证据字节。仓外辅助脚本在相邻 workspace 的 `agent-output/codex/FEA-06-RESIDUAL-1/animation-verify.ps1`，可重建；未做清理，不作为唯一证据。
