# FEA-07 Handoff（impl-r6 approved + R-022 P2 修复 → r7 复核派发，2026-11-02）

> 本 handoff 引用精确 delivery commit，作为 r7 复核入口。事实以 Git/仓库文件为准。

## 1. 交付指针

| 项 | 值 |
|---|---|
| Task | `doc/tasks/FEA-07.md` — `in_progress` |
| base_commit | `cbfb7bbc92d489541a24290038eae2117f8aa1ce` |
| delivery_head（代码） | `5a495f80a208ccc17a34eededc21c91f6e18e720` |
| 被审文档 head | 本 handoff/证据提交（r7 派发时固定） |
| 证据目录 | `verification/FEA-07/` |
| 精确最终证据 | `verification/FEA-07/final-evidence.log`（head `5a495f80a`；SHA-256 `7fb048ab…`） |
| 证据索引 | `verification/FEA-07/evidence-index.md` |
| 全量测试 | **1135 passed / 0 failed / 57 skipped**（skip 直接原因 `NEWMANGA_CORECLIENT_SIDECAR_DIR` 未设置） |
| 治理 | build 0/0；check.ps1 PASS(3)；verify_pins 15/15；TokenGen 292 rows `--check` up-to-date；ThemeGen `--check` up-to-date |
| 性能（AC6/W-5） | 4 预热 + 20 单向切换（真实 p95 口径）：Release p50 88.42 / p95 261.38 / max 275.14 ms / 内存 +22496B / 句柄 +3 → PASS；两次复测 p95 292.65/261.38 ms |
| 原生矩阵 | 双屏/拔屏/DPI 100/125/150/200% = **BLOCKED（D-1 无硬件）**，不得伪造 |

## 2. r6 结论与处置

- `doc/reviews/FEA-07-impl-r6.md`：**approved**，P0=0 / P1=0 / P2=2（被审文档 `80b2203e5`/代码 `4e8510d43`）。R-020、R-021 闭环。
- **R-022（P2，已修复）**：全屏 Fluent→V2 切换在 Promote 时退出全屏，SaveAsync/finalize 失败回滚旧树后原全屏模式未恢复。修复：`PresentationWindow.SwitchFrontendAsync` 事务前快照 `WindowState` + Fluent reader 全屏状态，失败时与旧内容树一并恢复；成功路径保持原清理策略。新增 `PresentationWindowTests.FailedSwitch_RestoresTheOriginalFullScreenMode`，既有失败切换测试补 Normal 断言。
- **R-007（P2，已处置）**：reviewer=impl-r6（approved）、delivery_head=`5a495f80a`、本 handoff、索引「r7 待派」、canonical 保持 pending。

## 3. 测试与证据

- 全量 **1135/0/57**（+1 测试）；build 0/0；两生成物 up-to-date；check PASS(3)；pins 15/15。
- 证据：`rework-r6-verification.log`（SHA `322475cb…`）、`final-evidence.log`（`7fb048ab…`）、`performance-baseline-release.json`（SHA `a06e3cfd…`）、`performance-baseline.md`、`evidence-index.md`。

## 4. r7 复核派发（fresh Codex CLI，只读）

- CLI：`C:\Users\49745\AppData\Local\OpenAI\Codex\bin\22cfb1d302613eae\codex.exe`
- 模型配置：`-m gpt-6.1-sol -c 'model_reasoning_effort="high"'`
- 权限：`exec --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox -o <result.md> $prompt`
- 约束：只读；唯一允许写 `doc/reviews/FEA-07-impl-r7.md`；不得 commit/push；报告 front matter 记录 reviewer 身份/来源、reviewed_head、code_head、decision、counts；实跑 build/全量/两 `--check`/check/pins 并核对 Task pins 与 evidence-index SHA。
- 重点：R-022 修复正确性（窗口模式快照/恢复、成功路径清理不变、Normal/最大化不受影响、真实 Fluent 全屏失败回归），以及是否引入回归。
- 被审内容：`cbfb7bbc9..<r7 文档 head>`，代码判断以 `5a495f80a` 为准。

## 5. 剩余（r7 approved 后）

1. DSH 集成验证（build/test/两 `--check`/check/pins/证据索引）→ Task `done`、integration_commit=`5a495f80a`（如无新代码变更）、canonical=complete、Closeout Record。
2. AC5 原生双屏/拔屏/DPI 矩阵按 D-1 residual/waiver 登记（不伪造证据）；R-020/R-022 的 headless 全屏接线已在真实组合根覆盖。
3. 之后按用户顺序推进 `FEA-06-RESIDUAL-1`（不插队）。
