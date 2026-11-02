# FEA-07 Handoff（impl-r7 changes_requested 处置完成 → r8 复核派发，2026-11-02）

> 本 handoff 引用精确 delivery commit，作为 r8 复核入口。事实以 Git/仓库文件为准。

## 1. 交付指针

| 项 | 值 |
|---|---|
| Task | `doc/tasks/FEA-07.md` — `in_progress` |
| base_commit | `cbfb7bbc92d489541a24290038eae2117f8aa1ce` |
| delivery_head（代码） | `462141f57f7b00b34577dbf04d8415be7ab5fe95` |
| 被审文档 head | 本 handoff/证据提交（r8 派发时固定） |
| 证据目录 | `verification/FEA-07/` |
| 精确最终证据 | `verification/FEA-07/final-evidence.log`（head `462141f57`；SHA-256 `dbfb7666…`） |
| 证据索引 | `verification/FEA-07/evidence-index.md` |
| 全量测试 | **1138 passed / 0 failed / 57 skipped**（skip 直接原因 `NEWMANGA_CORECLIENT_SIDECAR_DIR` 未设置） |
| 治理 | build 0/0；check.ps1 PASS(3)；verify_pins 15/15；TokenGen 292 rows `--check` up-to-date；ThemeGen `--check` up-to-date |
| 性能（AC6/W-5） | 4 预热 + 20 单向切换：Release p50 99.28 / p95 374.09 / max 389.99 ms / 内存 -1616B / 句柄 0 → PASS；两次复测 p95 299.40/374.09 ms |
| 原生矩阵 | 双屏/拔屏/DPI 100/125/150/200% = **BLOCKED（D-1 无硬件）**，不得伪造 |

## 2. r7 findings 处置（本批）

| r7 ID | 级别 | 处置 | 落点 |
|---|---|---|---|
| R-022 残余 | P2 | 窗口模式快照/恢复移入协调器事务（新增 `IPresentationWindowModeTransaction`）；`SwitchAsync` 事务 finally dispose 未提交快照 → 失败/异常/取消均恢复，成功 `Commit()` 不触碰窗口；取消仍向上传播 | `FrontendHostCoordinator.cs`、`PresentationWindow.cs`、`IPresentationWindowModeTransaction.cs` |
| R-024 | P2 | 快照在 `_switchGate` 内、reject/no-op 校验之后，绑定本事务旧树；排队后拒绝的请求不再恢复陈旧模式 | 同上 |
| R-023 | P2 | 新增三个判别性测试：Promote 后 journal finalize 失败恢复、Promote 后取消恢复（OCE 传播）、排队拒绝不写陈旧模式；r6 head 无补偿实现下前两者会失败 | `PresentationWindowTests.cs` |
| R-007 | P2 | reviewer=impl-r7、delivery_head=`462141f57`、本 handoff、索引「r8 待派」、canonical pending | 本文件 + Task 卡 + 索引 |

## 3. 测试与证据

- 全量 **1138/0/57**（+3 测试）；presentation 相关 38 测试连续 3 次全绿；build 0/0；两生成物 up-to-date；check PASS(3)；pins 15/15。
- 证据：`rework-r7-verification.log`（SHA `9e4e04bd…`）、`final-evidence.log`（`dbfb7666…`）、`performance-baseline-release.json`（SHA `26eb150a…`）、`performance-baseline.md`、`evidence-index.md`。

## 4. r8 复核派发（fresh Codex CLI，只读）

- CLI：`C:\Users\49745\AppData\Local\OpenAI\Codex\bin\22cfb1d302613eae\codex.exe`
- 模型配置：`-m gpt-6.1-sol -c 'model_reasoning_effort="high"'`
- 权限：`exec --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox -o <result.md> $prompt`
- 约束：只读；唯一允许写 `doc/reviews/FEA-07-impl-r8.md`；不得 commit/push；报告 front matter 记录 reviewer 身份/来源、reviewed_head、code_head、decision、counts；实跑 build/全量/两 `--check`/check/pins 并核对 Task pins 与 evidence-index SHA。
- 重点：R-022 取消/失败补偿、R-024 门内快照、R-023 测试判别力与回归；被审代码以 `462141f57` 为准。

## 5. 剩余（r8 approved 后）

1. DSH 集成验证（build/test/两 `--check`/check/pins/证据索引）→ Task `done`、integration_commit=`462141f57`（如无新代码变更）、canonical=complete、Closeout Record。
2. AC5 原生双屏/拔屏/DPI 矩阵按 D-1 residual/waiver 登记（不伪造证据）。
3. 之后按用户顺序推进 `FEA-06-RESIDUAL-1`（不插队）。
