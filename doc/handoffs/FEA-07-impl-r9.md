# FEA-07 Handoff（impl-r9 changes_requested 处置完成 → r10 复核派发，2026-11-02）

> 本 handoff 引用精确 delivery commit，作为 r10 复核入口。事实以 Git/仓库文件为准。

## 1. 交付指针

| 项 | 值 |
|---|---|
| Task | `doc/tasks/FEA-07.md` — `in_progress` |
| base_commit | `cbfb7bbc92d489541a24290038eae2117f8aa1ce` |
| delivery_head（代码） | `aedc7251c3cae49a12c8b6bc3f91c3e6dd53d3d0`（r9 仅文档修正，代码 head 不变） |
| 被审文档 head | 本 handoff/证据提交（r10 派发时固定） |
| 证据目录 | `verification/FEA-07/` |
| 精确最终证据 | `verification/FEA-07/final-evidence.log`（code head `aedc7251c`；SHA-256 `e8ed8f29…`） |
| 证据索引 | `verification/FEA-07/evidence-index.md` |
| 全量测试 | **1138 passed / 0 failed / 57 skipped**（skip 直接原因 `NEWMANGA_CORECLIENT_SIDECAR_DIR` 未设置） |
| 治理 | build 0/0；check.ps1 PASS(3)；verify_pins 15/15；TokenGen 292 rows `--check` up-to-date；ThemeGen `--check` up-to-date |
| 性能（AC6/W-5） | 4 预热 + 20 单向切换：Release p50 109.89 / p95 381.43 / max 383.05 ms / 内存 +456B / 句柄 +1 → PASS；两次复测 p95 361.52/381.43 ms |
| 原生矩阵 | 双屏/拔屏/DPI 100/125/150/200% = **BLOCKED（D-1 无硬件）**，不得伪造 |

## 2. r9 findings 处置（本批，纯文档）

| r9 ID | 级别 | 处置 |
|---|---|---|
| R-007 | P2 | Task reviewer 改为 impl-r9（已处置）、canonical `r10 approved`、索引「r10 待派」、handoff r8 的 r9 待派行补执行记录、新增本 handoff |
| R-009 | P2 | AC6 验收行 r7 旧数值改为当前 r8 记录 run（p50 109.89 / p95 381.43 / max 383.05；两次 361.52/381.43）；r7 实施记录原字节保留 |
| R-011 | P2 | `EV-FEA07-FINAL`/`EV-FEA07-PERF-MD` 的 commit 列 `aedc7251c` → `563f248c7`（实际包含当前 r8 文件的提交）；文件内部 code_head 保持 `aedc7251c`，不重写旧证据 |

## 3. 测试与证据

- 代码 head 未变：build 0/0、全量 **1138/0/57**、两生成物 up-to-date、check PASS(3)、pins 15/15 沿用 `rework-r8-verification.log` 与 `final-evidence.log`。
- 本批提交前重新校验：Task 21 项 pin 与实际 SHA 一致、索引 23 行一致、索引无自引用/控制字符 0。

## 4. r10 复核派发（fresh Codex CLI，只读）

- CLI：`C:\Users\49745\AppData\Local\OpenAI\Codex\bin\22cfb1d302613eae\codex.exe`
- 模型配置：`-m gpt-6.1-sol -c 'model_reasoning_effort="high"'`
- 权限：`exec --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox -o <result.md> $prompt`
- 约束：只读；唯一允许写 `doc/reviews/FEA-07-impl-r10.md`；不得 commit/push；报告 front matter 记录 reviewer 身份/来源、reviewed_head、code_head、decision、counts；实跑 build/全量/两 `--check`/check/pins 并核对 Task pins 与 evidence-index SHA。
- 重点：R-007/R-009/R-011 三项文档一致性是否闭环（Task/索引/handoff/证据 commit 定位与内部 code_head）、是否引入新的指针矛盾；`aedc7251c..<docs head>` 应只有 docs/evidence。

## 5. 剩余（r10 approved 后）

1. DSH 集成验证（build/test/两 `--check`/check/pins/证据索引）→ Task `done`、integration_commit=`aedc7251c`、canonical=complete、Closeout Record。
2. AC5 原生双屏/拔屏/DPI 矩阵按 D-1 residual/waiver 登记（不伪造证据）。
3. 之后按用户顺序推进 `FEA-06-RESIDUAL-1`（不插队）。
