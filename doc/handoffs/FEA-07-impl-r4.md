# FEA-07 Handoff（impl-r4 复核处置完成 → r5 复核派发，2026-11-02）

> 本 handoff 引用精确 delivery commit，作为 r5 复核入口。事实以 Git/仓库文件为准。

## 1. 交付指针

| 项 | 值 |
|---|---|
| Task | `doc/tasks/FEA-07.md` — `in_progress` |
| base_commit | `cbfb7bbc92d489541a24290038eae2117f8aa1ce` |
| delivery_head（代码） | `b328f3488615fcad10e455e6f1196e6622cbb889` |
| 被审文档 head | 本 handoff/证据提交（r5 派发时固定） |
| 证据目录 | `verification/FEA-07/` |
| 精确最终证据 | `verification/FEA-07/final-evidence.log`（head `b328f3488`；SHA-256 `06975fc7…`） |
| 证据索引 | `verification/FEA-07/evidence-index.md` |
| 全量测试 | **1132 passed / 0 failed / 57 skipped**（+13 tests；skip 直接原因 `NEWMANGA_CORECLIENT_SIDECAR_DIR` 未设置） |
| 治理 | build 0/0；check.ps1 PASS(3)；verify_pins 15/15；TokenGen 292 rows `--check` up-to-date；ThemeGen `--check` up-to-date |
| 性能（AC6/W-5） | 4 预热 + 20 测量（真实 p95 口径）：Release p50 106.46 / p95 313.95 / max 331.89 ms / 内存 +10592B / 句柄 0 → PASS；四次复测 p95 292.92/295.41/295.59/313.95 ms |
| 原生矩阵 | 双屏/拔屏/DPI 100/125/150/200% = **BLOCKED（D-1 无硬件）**，不得伪造 |

## 2. r4 findings 处置（本批）

| r4 ID | 级别 | 处置 | 落点 |
|---|---|---|---|
| R-017 | P1 | `SettingsViewModel` 以 old/new canonical 快照判断「仅 frontendId 变化」，仅该情形保留未应用 draft；其它外部变更镜像唯一写者；重复同值通知不覆盖 dirty draft。7 例新测试 | `FluentPageViewModels.cs`、`SettingsDraftSyncTests.cs` |
| R-002 | P1（验证） | 生产 provider 不覆写：真实注册 ThemeStudioViewModel 制造 unapplied draft → `AppShellV2.HasUnsavedEdits` true → 关闭被阻断 → 真实 Cancel 后放行 → 移除 provider 反向验证 | `PresentationHostCompositionTests.cs` |
| R-013 | P1（判别力） | 确定性屏障：首请求 finalize 处持门暂停 → 第二请求断言未完成 → 首请求失败回滚 → 第二请求作为真实 V2→Fluent 切换在补偿后成功 | `FrontendHostCoordinatorTests.cs` |
| R-018 | P2 | 事务 finally 解绑 Loaded 订阅；反射断言成功/失败后活动订阅为 0 | `FrontendHostCoordinator.cs`、`FrontendHostCoordinatorTests.cs` |
| R-019 | P2 | 新增 `IPresentationInputState`；staging 期间停用 TopLevel 键处理、commit 启用、回滚恢复；真实键路由测试 + 协调器激活序列 + 生产切换测试 | `IPresentationInputState.cs`、`AppShellV2.axaml.cs`、`FrontendHostCoordinator.cs`、`PresentationInputRoutingTests.cs` |
| R-007 | P2（文案） | reviewer=impl-r4、delivery_head=`b328f3488`、本 handoff、索引「r5 待派」、skip 原因更正 | 本文件 + Task 卡 + 索引 |
| R-009 | P2（性能口径） | 12 样本→4 预热+20 测量，p95 成为真实 p95；W-5 门槛不变；四次 Release 复测均 PASS | `PerformanceBaselineTests.cs`、`performance-baseline.md` |

## 3. 测试与证据

- 新增：`SettingsDraftSyncTests`（7）、`PresentationInputRoutingTests`（2）；改写：`FrontendHostCoordinatorTests`（并发屏障/订阅/激活）、`PresentationHostCompositionTests`（真实 draft、隐藏树、状态保留 + 共享 memento 清理）、`PerformanceBaselineTests`（4+20 口径）。
- 稳定性：presentation 相关 23 测试连续 5 次全绿（修掉了共享 `CurrentFrontend` memento 导致的空间顺序依赖）。
- 证据：`rework-r4-verification.log`（SHA `f0cb7403…`）、`final-evidence.log`（`06975fc7…`）、`performance-baseline-release.json`（SHA `1aa295ff…`）、`performance-baseline.md`、`evidence-index.md`。

## 4. r5 复核派发（fresh Codex CLI，只读）

- CLI：`C:\Users\49745\AppData\Local\OpenAI\Codex\bin\22cfb1d302613eae\codex.exe`
- 模型配置：`-m gpt-6.1-sol -c 'model_reasoning_effort="high"'`
- 权限：`exec --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox -o <result.md> $prompt`
- 约束：只读；唯一允许写 `doc/reviews/FEA-07-impl-r5.md`；不得 commit/push；报告 front matter 记录 reviewer 身份/来源、reviewed_head、code_head、decision、counts；实跑 build/全量/两 `--check`/check/pins 并核对 Task pins 与 evidence-index SHA。
- 被审内容：`cbfb7bbc9..<r5 文档 head>`，代码判断以 `b328f3488` 为准。

## 5. 剩余（r5 approved 后）

1. DSH 处置 r5 findings → 若 approved：DSH 集成验证（build/test/两 `--check`/check/pins/证据索引）→ Task `done`、integration_commit、canonical_evidence_status=complete、Closeout Record。
2. AC5 原生双屏/拔屏/DPI 矩阵按 D-1 residual/waiver 登记（不伪造证据）。
3. 之后按用户顺序推进 `FEA-06-RESIDUAL-1`（不插队）。
