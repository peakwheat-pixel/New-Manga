# FEA-07 Handoff（impl-r3 复核处置完成 → r4 复核派发，2026-11-02）

> 本 handoff 引用精确 delivery commit，替代标题仍为 impl-r1 的旧 handoff 作为 r4 复核入口。事实以 Git/仓库文件为准。

## 1. 交付指针

| 项 | 值 |
|---|---|
| Task | `doc/tasks/FEA-07.md` — `in_progress` |
| base_commit | `cbfb7bbc92d489541a24290038eae2117f8aa1ce` |
| delivery_head（代码） | `100d487ffb55518e98be5219d750ab85c8a71d2b` |
| 复核被审文档 head | 本 handoff/证据提交（r4 派发时固定） |
| 证据目录 | `verification/FEA-07/` |
| 精确最终证据 | `verification/FEA-07/final-evidence.log`（head `100d487ff`；SHA-256 `478b097f…`） |
| 证据索引 | `verification/FEA-07/evidence-index.md`（不列自身 SHA、无控制字符） |
| 全量测试 | **1119 passed / 0 failed / 57 skipped** |
| 治理 | build 0/0；check.ps1 PASS(3)；verify_pins 15/15；TokenGen 292 rows `--check` up-to-date；ThemeGen `--check` up-to-date |
| 性能（AC6/W-5） | Release p50 102.29 / p95 496.30 / max 496.30 ms / 内存 +7088B / 句柄 0 → PASS（三次复测 496.30/575.64/712.28 ms） |
| 原生矩阵 | 双屏/拔屏/DPI 100/125/150/200% = **BLOCKED（D-1 无硬件）**，不得伪造 |

## 2. r3 findings 处置（本批）

| r3 ID | 级别 | 处置 | 落点 |
|---|---|---|---|
| R-001 | P1 | 真实 staging 门禁：隐藏 staging 宿主挂 live visual tree → 真实布局几何（删除 fallback）→ 真实 `Loaded` 事件 → `RequestAnimationFrame` 帧渲染 → 才 commit；失败清理 staging + 回滚。补 staging 可见性/有效与零几何/Loaded 门禁失败回滚/生产内容树状态保留测试 | `PresentationWindow.cs`、`FrontendHostCoordinator.cs`、`PresentationWindowTests.cs`、`PresentationHostCompositionTests.cs` |
| R-002 | P1 | `allContentProvider` 聚合全部缓存内容树 `IPresentationExitState` 阻断关闭；`AppShellV2.ThemeStudioDraftProvider` + `WireThemeStudio` 注入 `HasDraft`；补隐藏树/生产树/provider 关闭测试 | `PresentationWindow.cs`、`App.axaml.cs`、`AppShellV2.axaml.cs`、`PresentationHostCompositionTests.cs` |
| R-007 | P1 | reviewer=impl-r3、delivery_head=`100d487ff`、本 handoff、canonical=pending（r4 approved 后 complete） | 本文件 + Task 卡 |
| R-009 | P2 | 性能数值统一为 R-001 后新 baseline（旧 344.93/429.47 更正并说明不可直接比较） | Task 卡 AC6/证据、`performance-baseline.md` |
| R-016 | P2 | 证据索引重生成（0 控制字符、无自引用 SHA） | `evidence-index.md` |
| 附带 | P1/A01 | 前端切换只改 `theme.frontendId` 时保留 Fluent 未应用 Settings draft（不静默丢失） | `FluentPageViewModels.cs`（`SettingsViewModel.ApplyCoordinatorSettings`） |

## 3. 测试与证据

- 新增/改写：`PresentationWindowTests`（staging 挂树、几何、Loaded 失败、隐藏缓存树关闭）、`PresentationHostCompositionTests`（真实树 50 往返 + Fluent draft/V2 session 状态、隐藏生产树 + Theme Studio draft 关闭阻断）、`FrontendHostCoordinatorTests`（改为真实窗口双槽）、`PerformanceBaselineTests`（Show 后测量真实门禁路径）。
- 证据：`rework-r3-part2-verification.log`（SHA `aacf4ce2…`）、`final-evidence.log`（`478b097f…`）、`performance-baseline-release.json`（SHA `03c12a4d…`）、`performance-baseline.md`、`evidence-index.md`。

## 4. r4 复核派发（fresh Codex CLI，只读）

- CLI：`C:\Users\49745\AppData\Local\OpenAI\Codex\bin\22cfb1d302613eae\codex.exe`
- 模型配置：`-m gpt-6.1-sol -c 'model_reasoning_effort="high"'`（用户 2026-11-02 指示；`-high` 是参数不是模型 ID）
- 权限：`exec --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox -o <result.md> $prompt`
- 约束：只读；唯一允许写 `doc/reviews/FEA-07-impl-r4.md`；不得 commit/push；报告 front matter 记录 reviewer 身份/来源、reviewed_head、code_head、decision、counts；必须实跑 build/全量 test/两 `--check`/check.ps1/verify_pins 并逐项核对 Task canonical pins 与 evidence-index SHA。
- 被审内容：`cbfb7bbc9..<r4 文档 head>`，代码判断以 `100d487ff` 为准。

## 5. 剩余（r4 approved 后）

1. DSH 处置 r4 findings → 若 approved：DSH 集成验证（build/test/两 `--check`/check/pins/证据索引）→ 更新 Task status=`done`、integration_commit、canonical_evidence_status=complete、Closeout Record。
2. AC5 原生双屏/拔屏/DPI 矩阵按 D-1 residual/waiver 登记（不伪造证据）。
3. 之后按用户顺序推进 `FEA-06-RESIDUAL-1`（不插队）。
