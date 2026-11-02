# FEA-07 Handoff（impl-r8 changes_requested 处置完成 → r9 复核派发，2026-11-02）

> 本 handoff 引用精确 delivery commit，作为 r9 复核入口。事实以 Git/仓库文件为准。

## 1. 交付指针

| 项 | 值 |
|---|---|
| Task | `doc/tasks/FEA-07.md` — `in_progress` |
| base_commit | `cbfb7bbc92d489541a24290038eae2117f8aa1ce` |
| delivery_head（代码） | `aedc7251c3cae49a12c8b6bc3f91c3e6dd53d3d0` |
| 被审文档 head | 本 handoff/证据提交（r9 派发时固定） |
| 证据目录 | `verification/FEA-07/` |
| 精确最终证据 | `verification/FEA-07/final-evidence.log`（head `aedc7251c`；SHA-256 `e8ed8f29…`） |
| 证据索引 | `verification/FEA-07/evidence-index.md` |
| 全量测试 | **1138 passed / 0 failed / 57 skipped**（skip 直接原因 `NEWMANGA_CORECLIENT_SIDECAR_DIR` 未设置） |
| 治理 | build 0/0；check.ps1 PASS(3)；verify_pins 15/15；TokenGen 292 rows `--check` up-to-date；ThemeGen `--check` up-to-date |
| 性能（AC6/W-5） | 4 预热 + 20 单向切换：Release p50 109.89 / p95 381.43 / max 383.05 ms / 内存 +456B / 句柄 +1 → PASS；两次复测 p95 361.52/381.43 ms |
| 原生矩阵 | 双屏/拔屏/DPI 100/125/150/200% = **BLOCKED（D-1 无硬件）**，不得伪造 |

## 2. r8 findings 处置（本批）

| r8 ID | 级别 | 处置 | 落点 |
|---|---|---|---|
| R-023 残余 | P2 | 排队用例屏障前移到 **Promote 前**（旧树/窗口仍全屏时发起第二请求，并断言其未完成）；`FrontendHostCoordinator` 增 `beforeContentCommit` 诊断钩子、`PresentationWindow` 内部 ctor 透传 `beforeCommit`；**mutation 实测**：把窗口模式快照移回 gate 外（模拟旧实现）→ 用例 FAIL（Expected Normal / Actual FullScreen），恢复后 19/19 全绿 | `FrontendHostCoordinator.cs`、`PresentationWindow.cs`、`PresentationWindowTests.cs`、`rework-r8-verification.log` |
| R-007 | P2 | reviewer=impl-r8、delivery_head=`aedc7251c`、本 handoff、索引「r9 待派」、canonical pending；Task/索引 appointment 文案与 STATUS/PLAN/checkpoint 同步。**后续：r9 已于 2026-11-02 执行（changes_requested P0=0/P1=0/P2=3，见 `doc/reviews/FEA-07-impl-r9.md`），本 handoff 保留派发时字节** | 本文件 + Task 卡 + 索引 |

同时在 Task impl-r8 节修正了 r7 节对排队用例判别性的过宽表述，以 mutation 实测为准。

## 3. 测试与证据

- 全量 **1138/0/57**（测试改写、总数不变）；presentation 36 测试连续 2 次全绿；build 0/0；两生成物 up-to-date；check PASS(3)；pins 15/15。
- 证据：`rework-r8-verification.log`（SHA `b739ac7c…`）、`final-evidence.log`（`e8ed8f29…`）、`performance-baseline-release.json`（SHA `2ab2f5cf…`）、`performance-baseline.md`、`evidence-index.md`。

## 4. r9 复核派发（fresh Codex CLI，只读）

- CLI：`C:\Users\49745\AppData\Local\OpenAI\Codex\bin\22cfb1d302613eae\codex.exe`
- 模型配置：`-m gpt-6.1-sol -c 'model_reasoning_effort="high"'`
- 权限：`exec --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox -o <result.md> $prompt`
- 约束：只读；唯一允许写 `doc/reviews/FEA-07-impl-r9.md`；不得 commit/push；报告 front matter 记录 reviewer 身份/来源、reviewed_head、code_head、decision、counts；实跑 build/全量/两 `--check`/check/pins 并核对 Task pins 与 evidence-index SHA。
- 重点：R-023 排队用例判别力（Promote 前屏障 + mutation 证据）、r7 过宽表述已修正、R-007 文案同步；被审代码以 `aedc7251c` 为准。

## 5. 剩余（r9 approved 后）

1. DSH 集成验证（build/test/两 `--check`/check/pins/证据索引）→ Task `done`、integration_commit=`aedc7251c`（如无新代码变更）、canonical=complete、Closeout Record。
2. AC5 原生双屏/拔屏/DPI 矩阵按 D-1 residual/waiver 登记（不伪造证据）。
3. 之后按用户顺序推进 `FEA-06-RESIDUAL-1`（不插队）。
