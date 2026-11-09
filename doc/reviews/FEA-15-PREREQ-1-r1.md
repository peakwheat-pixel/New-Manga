---
task_id: FEA-15-PREREQ-1
reviewer: DSH 派发的独立上下文子 agent（parent session c08ea2ac-cbcf-47ac-a7a9-0e15254b3fa5，delegation depth 1；只读、未参与实现）
reviewer_kind: subagent
author: DSH（Lead / Integrator）
base_commit: 417d9c442
reviewed_head: 1c4eeaed4
delivery_commit: f7134ba83
decision: approved
---

# Review：FEA-15-PREREQ-1（r1）

## 范围与依据

- 仅审查 `417d9c442..f7134ba83`（实现）与 `1c4eeaed4`（in_review / Handoff / EV）两个提交；`1c4eeaed4` 为当前 HEAD，工作区干净。
- 依据：`doc/tasks/FEA-15-PREREQ-1.md` 的 AC1–AC4 与 `修复口径`、`doc/handoffs/FEA-15-PREREQ-1-f7134ba83.md`、`verification/FEA-15-PREREQ-1/**`。
- 实际 diff（`f7134ba83`）：2 个代码/测试文件 + 3 个生命周期指针（`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/TASK_LEDGER.md`）+ Task + 6 份 EV。
- 未审：`1c4eeaed4` 之外的后续提交、Host/Python 测试（不在本 Task 范围）。

## Standards

- 设计系统单一来源（[AGENTS.md](../../AGENTS.md) 产品边界 + `Nm.*` token 约定）：`ImmersiveReaderWindow` 由 `Brushes.Black` 改为 `DynamicResourceExtension("Nm.Color.Bg.Canvas")`，方向正确；键在 `Tokens.Dark/Light/HighContrast.axaml`、`NmKeys.g.cs`、`TokenMap.md` 中均存在，且 `App.axaml` 以 `ResourceInclude` 合并 `Tokens.Dark.axaml`，Window 级动态资源可解析。
- 无 P0/P1 硬性违规；未启用 formatter/linter 可覆盖项不重复报告。

## Spec

- AC1/AC2/AC3 忠实实现，测试语义为**加强**（17→18 + 新增去重断言），非弱化。
- AC4 的 “diff ⊆ allowed_paths” 表述与事实不符（见 R-001），属证据/口径问题而非代码问题。

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态/修订 commit |
|---|---|---|---|---|---|---|
| R-001 | P2 | `doc/tasks/FEA-15-PREREQ-1.md:54`（AC4） | AC4 声称 “diff ⊆ allowed_paths”，但 `f7134ba83` 还改 `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`，三者均不在 `allowed_paths`（第 20–26 行）。`tools/governance/check.ps1` 中无 `allowed_paths` 校验逻辑（`Select-String allowed_paths` 无命中），故该 AC 无自动化自证。内容本身是标准生命周期指针更新，风险低 | `git show --stat f7134ba83`；`git diff 417d9c442..f7134ba83 --stat`；`Select-String tools/governance/check.ps1 -Pattern allowed_paths` → 0 命中 | 在 `allowed_paths` 补 3 个指针文件（或改为“生命周期指针文件允许随 Task 更新”），并把 AC4 改写为可机械验证的表述；不建议事后改 EV 字节 | open |
| R-002 | P3 | `apps/desktop-avalonia/src/NewManga.App/Shell/V2/ImmersiveReaderWindow.cs:12-13,26` | 类 XML 注释仍写 “black background”，但 token 化后暗色画布为 `#0F1012`、亮色/高对比亮为 `#F4F3F0`；Task `out_of_scope` 的 “阅读器仍是全屏黑底” 在亮色主题下不再字面成立。与 legacy 阅读器一致（`ReaderWorkbenchPages.cs:749` → `LegacyChrome "ReaderBackground"` ⇒ `Nm.Color.Bg.Canvas`），故属口径/注释漂移 | `Tokens.Dark.axaml:13`（`#FF0F1012`）、`Tokens.Light.axaml:13`（`#FFF4F3F0`）；`git grep ReaderBackground` | 更新类注释与 Task `out_of_scope` 措辞为“采用设计系统画布色（暗色近黑）”；可补一条阅读器 Background 断言测试 | open |
| R-003 | P3 | `tests/NewManga.App.Tests/FluentPageTests.cs:135-138` | 去重断言语义比领域规则更严：`KeyMap.FindConflicts` 只在**作用域重叠**时判冲突（`KeyMap.cs:158-163`），而测试要求全表全局唯一，未来合法的跨作用域复用同一手势会被误判 RED；`Distinct()` 用 record 全量相等（未屏蔽 CapsLock/NumLock 位），与 `GesturesEqual`（`KeyMap.cs:165-168`）的掩码比较不一致。当前 18 条定义无重复，故不误报 | `KeyMap.cs:99-168`；测试实跑通过（2 passed） | 改为 `Assert.Empty(shell.ShellKeyMap.Conflicts)`（已覆盖同作用域重复且与领域规则一致），或复用掩码比较；全局唯一若为刻意约束，请在注释中写明理由 | open |
| R-004 | P3 | `ImmersiveReaderWindow.cs:1-3` | 新增 `using Avalonia.Markup.Xaml.MarkupExtensions;` 置于 `Avalonia.Controls` 之前（非字母序）；`using Avalonia.Media;` 在 `Brushes` 移除后已无使用者（`TreatWarningsAsErrors=true` 但未启用 IDE0005，故构建仍 0 警告） | `apps/desktop-avalonia/Directory.Build.props`（`TreatWarningsAsErrors=true`，无 `EnforceCodeStyleInBuild`）；本机 build 0 警告 | 删 `using Avalonia.Media;` 并调整 using 顺序 | open |
| R-005 | P3 | `verification/FEA-15-PREREQ-1/README.md:4`；`logs/mutation-literal-brush.log:2` | 证据表述小漂移：README 写批次 `fea-15-prereq-1-r2`，日志头为 `# batch: fea-15-prereq-1`；卡片 E5 写“恢复 `Brushes.Black`”，实际变异用 `Brushes.Green`（判别力更强，非缺陷）；复原后无独立复跑日志（Handoff 记“同上”），由本次复跑补证 | 上述文件内容；本次 `dotnet build` + 复跑 2 passed | 统一批次名；E5 措辞改为“恢复任意 literal brush”；复原证据建议单独入库 | open |

## 验证

| 场景 | 命令或手工步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| 目标 2 用例（复核，`--no-build`） | `dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj --no-build --nologo --filter "...V2ConformanceTests.AppCSharp_OutsideShellLayout_HasNoRawDesignValues\|...FluentPageTests.FluentShell_BreakpointsA11yShortcutsAndReducedMotion_AreExplicit"` | HEAD `1c4eeaed4` / pwsh 7.x / .NET 9 | PASS（2 passed / 0 failed），EXIT=0 | 本次会话输出 |
| 测试项目重新构建 | `dotnet build apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj --nologo -v:q` | 同上 | PASS（0 警告 / 0 错误），BUILD_EXIT=0 | 本次会话输出；对应 `logs/dotnet-build.log`（0/0，EXIT=0） |
| 目标 2 用例（重建后复跑） | 同上 filter，`--no-build` | 同上 | PASS（2 passed），TEST_EXIT=0 | 本次会话输出 |
| 阅读器行为回归 | `dotnet test ... --filter "FullyQualifiedName~V2ImmersiveReaderTests"` | 同上 | PASS（3 passed / 0 failed），EXIT=0 | 本次会话输出 |
| App.Tests 全量 | `dotnet test NewManga.App.Tests`（作者执行，5m7s） | `f7134ba83` | PASS（838 passed / 0 failed / 11 skipped），0 failed 承接 AC3 | `logs/dotnet-test-app-full.log`（sha256 已核）；**未由本次复核全量重跑**（时间预算），数字取自信任 EV |
| 门禁 A | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-15-PREREQ-1.md` | HEAD | PASS（3 warnings：12 非终态 Task / STATUS 80% / REBASELINE 80%），EXIT_CHECK=0 | 本次会话输出 |
| 门禁 B | `pwsh -NoProfile -File tools/governance/check.ps1` | HEAD | PASS（3 warnings），EXIT_DEFAULT=0 | 本次会话输出 |
| 门禁 C | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | HEAD | PASS，`PIN AUDIT: PASS (all 18)`，EXIT_PINS=0 | 本次会话输出 |
| EV 字节一致性 | 6 个 EV 逐个 `Get-FileHash -Algorithm SHA256` 与卡片表格比对 | HEAD | PASS 6/6（README `d88f5e4…`、TWO `2039e2d…`、FULL `72e7e13…`、BUILD `069650a…`、MUT1 `4602346…`、MUT2 `06ab870…`） | 本次会话输出 |
| 原始设计值扫描 | 对 `ImmersiveReaderWindow.cs` 匹配 `Brushes\.|#[0-9A-Fa-f]{6}|SolidColorBrush|Colors\.` | `1c4eeaed4` | PASS（0 命中）；`V2ConformanceTests.cs` 豁免表未被本次改动（`git diff` 空） | 本次会话输出 |
| 18 的权威性 | 静态计数 `ShellCommands.cs` 的 `Definitions` 区段：`G(Key.` 18 处 + `new ShellKeyGesture(Key.F11)` 1 处 = 19 个 gesture 实例，其中 1 条命令持有 2 个（`{ G(Key.F5), G(Key.F, Ctrl+Shift) }`）⇒ 带手势命令数 = 18，实例无重复 | HEAD | PASS（与测试断言 18 及新增去重断言一致） | 本次会话输出 |
| 工作区 | `git status --short` | HEAD | PASS（本报告落盘前为空；落盘后仅本文件） | 本次会话输出 |

## 结论与复审

- **Architecture：PASS**——无新增依赖、无分层越界、无契约/主题定义改动；背景改为设计系统 token，符合单一来源约束；资源键有效且与主题字典一致；全屏 / `SystemDecorations.None` / Esc-F11 关闭逻辑零改动（diff 仅背景行 + 注释 + using），`V2ImmersiveReaderTests` 3/3 绿。
- **Verification：PASS**——AC1（V2Conformance 绿、无 literal brush/colour、豁免表未动）、AC2（18 为真实权威值、去重断言成立、测试语义加强）、AC3（build 0/0、目标 2 用例 2/2、全量 838/0/11）均成立；AC4 两个门禁与 pins 18/18 通过，但其 “diff ⊆ allowed_paths” 的自述不准确，见 R-001。
- **判定：approved（可交 DSH 集成）**。无 P0/P1，无 P2 阻断项（唯一 P2 为证据/口径，建议在关闭 Task 前修 `allowed_paths` 或 AC4 措辞，不必回退代码）。
- 剩余风险：亮色主题下沉浸阅读器背景随画布变浅（R-002，与 legacy 一致）；全量套件数字本轮未独立重跑（依赖 canonical EV）。
