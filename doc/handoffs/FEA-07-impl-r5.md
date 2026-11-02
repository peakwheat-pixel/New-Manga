# FEA-07 Handoff（impl-r5 复核处置完成 → r6 复核派发，2026-11-02）

> 本 handoff 引用精确 delivery commit，作为 r6 复核入口。事实以 Git/仓库文件为准。

## 1. 交付指针

| 项 | 值 |
|---|---|
| Task | `doc/tasks/FEA-07.md` — `in_progress` |
| base_commit | `cbfb7bbc92d489541a24290038eae2117f8aa1ce` |
| delivery_head（代码） | `4e8510d431ac82df54b82991d14975da5c27f9a0` |
| 被审文档 head | 本 handoff/证据提交（r6 派发时固定） |
| 证据目录 | `verification/FEA-07/` |
| 精确最终证据 | `verification/FEA-07/final-evidence.log`（head `4e8510d43`；SHA-256 `3021dbb0…`） |
| 证据索引 | `verification/FEA-07/evidence-index.md` |
| 全量测试 | **1134 passed / 0 failed / 57 skipped**（skip 直接原因 `NEWMANGA_CORECLIENT_SIDECAR_DIR` 未设置） |
| 治理 | build 0/0；check.ps1 PASS(3)；verify_pins 15/15；TokenGen 292 rows `--check` up-to-date；ThemeGen `--check` up-to-date |
| 性能（AC6/W-5） | 4 预热 + 20 单向切换（真实 p95 口径）：Release p50 96.50 / p95 248.42 / max 349.30 ms / 内存 +2528B / 句柄 0 → PASS；两次复测 p95 236.48/248.42 ms |
| 原生矩阵 | 双屏/拔屏/DPI 100/125/150/200% = **BLOCKED（D-1 无硬件）**，不得伪造 |

## 2. r5 findings 处置（本批）

| r5 ID | 级别 | 处置 | 落点 |
|---|---|---|---|
| R-020 | P1 | 稳定窗口承接 Fluent 全屏请求：`FrontendContentHost.ContentChanged` → `PresentationWindow` 只对可见 Fluent 树连接 `FullScreenRequested`→`WindowState`；隐藏树请求忽略；离开 Fluent 时 `ExitFullScreen()` + Normal；`FluentShellSurface` 增 `CurrentPageChanged`/`ExitFullScreen()`，离开 Reader 页时退出全屏。真实组合根测试覆盖按钮/F/Esc、切换前后、隐藏树 | `FrontendContentHost.cs`、`PresentationWindow.cs`、`FluentShellSurface.axaml.cs`、`PresentationHostCompositionTests.cs` |
| R-021 | P2 | 重复通知用例改为直接驱动生产通知处理入口（同值不触发 Changed 的生产事实），断言 draft 保留；新增 clean+Contrast 镜像用例 | `SettingsDraftSyncTests.cs` |
| R-007 | P2 | reviewer=impl-r5、delivery_head=`4e8510d43`、本 handoff、索引「r6 待派」 | 本文件 + Task 卡 + 索引 |
| R-009 | 措辞 | 性能摘要「20 次往返」→「20 次单向切换（10 次往返）」；同 head Release 复测 p95 236.48/248.42 ms | `performance-baseline.md` |

## 3. 测试与证据

- 新增/改写：`PresentationHostCompositionTests.FluentFullScreenRequests_DriveTheStableWindowState`（按钮/F/Esc/切换前后/隐藏树）、`SettingsDraftSyncTests`（生产通知入口 + clean Contrast）。
- 证据：`rework-r5-verification.log`（SHA `e773a93d…`）、`final-evidence.log`（`3021dbb0…`）、`performance-baseline-release.json`（SHA `8e031bec…`）、`performance-baseline.md`、`evidence-index.md`。

## 4. r6 复核派发（fresh Codex CLI，只读）

- CLI：`C:\Users\49745\AppData\Local\OpenAI\Codex\bin\22cfb1d302613eae\codex.exe`
- 模型配置：`-m gpt-6.1-sol -c 'model_reasoning_effort="high"'`
- 权限：`exec --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox -o <result.md> $prompt`
- 约束：只读；唯一允许写 `doc/reviews/FEA-07-impl-r6.md`；不得 commit/push；报告 front matter 记录 reviewer 身份/来源、reviewed_head、code_head、decision、counts；实跑 build/全量/两 `--check`/check/pins 并核对 Task pins 与 evidence-index SHA。
- 被审内容：`cbfb7bbc9..<r6 文档 head>`，代码判断以 `4e8510d43` 为准。

## 5. 剩余（r6 approved 后）

1. DSH 处置 r6 findings → 若 approved：DSH 集成验证（build/test/两 `--check`/check/pins/证据索引）→ Task `done`、integration_commit、canonical_evidence_status=complete、Closeout Record。
2. AC5 原生双屏/拔屏/DPI 矩阵按 D-1 residual/waiver 登记（不伪造证据）。
3. 之后按用户顺序推进 `FEA-06-RESIDUAL-1`（不插队）。
