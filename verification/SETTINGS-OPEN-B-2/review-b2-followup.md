# SETTINGS-OPEN-B-2 — Follow-up 复审（P1/P2 处置）

- Reviewer：`reviewer-settings-a`（非实现者）
- 复审头：**`3fdfcb3d21b36382f78691e8c7584f0e8df5eda8`**；B-2 代码交付头 `0e2e6233`；修复 commit `02f1752dc`
- 原 Review：[review-b2.md](review-b2.md)（`changes_requested`）
- 结论：**approved**（仅剩一个 P2 文档计数，非阻塞；建议关闭前顺手修正）。

## P1/P2 disposition

| 原 finding | 状态 | 核对 |
|---|---|---|
| P1-1 Task/Handoff base 与 wire/ui report 的 7d19164/“未提交”错误 | **fixed** | `doc/tasks/SETTINGS-OPEN-B-2.md:12`、Handoff `:5` base 已改 `81f8221`；`wire-report.md:5-6`/`ui-report.md:4,22,151` 已改为交付 `0e2e623`；`git rev-parse 0e2e623^` 确为 `81f8221` |
| P1-2 ui-report GUI NOT_RUN 与 gui-smoke PASS 矛盾；AC5 未拆清 | **fixed** | `ui-report.md:9,159` 已改为 preview/clean/empty PASS、pending/restart NOT_RUN；Task `:56` AC5 已勾选并拆清；`gui-smoke.md` 的 01..03 截图仍支持三态 |
| P2-1 失败 reason 透传 OSError 绝对路径 | **fixed** | `core_service.py:483-514` 将失败/跳过 reason 固定为 `remove failed` / `outside safe cache prefixes`，成功为 `""`；`test_core_cleanup_wire.py` 新增 reason 无 `\`/`/` 断言；独立 `pytest ...cleanup_wire` 28 passed |
| P2-2 evidence hash 行尾口径 | **fixed（口径记录）** | B-2 Task AC5 与 Handoff/Task 记录 worktree CRLF、check 双接受、clean 复核以计数为准 |
| P2-3 新命令未记入 typed IPC contract | **fixed** | `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:265` §5.3 增加 B-2 增量注记（三命令、投影、无路径 reason、CORE_UNAVAILABLE/INVALID_REQUEST、五处同步、probe/ac1 冻结） |

## 独立验证（HEAD 3fdfcb3d）

| 命令 | 结果 |
|---|---|
| `python -m pytest tests/core -q` | **752 passed, 1 warning, 42.81s，EXIT 0** |
| `python -m pytest tests/core/test_core_cleanup_wire.py -q` | **28 passed, 2.34s**；reason 已无路径 |
| `cargo test --locked --skip packaged_sidecar_tests --test-threads=1`（dev overlay + `M2RC1_PYTHON`） | **152 passed; 0 failed; 1 ignored; 12 filtered out; 27.45s，EXIT 0** |
| `npm --prefix apps/desktop/frontend test` | **41 files / 406 tests passed** |
| `tsc --noEmit` | exit 0 |
| `tools/governance/check.ps1` | **PASS (2 warnings)** |
| 证据表 | Task canonical **15 行**，含 `EV-B2-REVIEW-B2`，commit `02f1752` 含所 pin 文件；GUI 01..03 截图与 gui-smoke 一致 |

产品实现未变：Core 三命令仍走 application channel、不在 `_HOST_CONTROL_COMMANDS`；Tauri 五处清单/ACL 一致、probe/ac1 7/6 冻结；前端真实面板无假控件；CleanupService 安全前缀/remover/manifest 复用不变。GUI pending/restart 仍为 NOT_RUN，按 AC5 已明确记录，不阻塞本 Review。

## 剩余 P2（不阻塞）

- `doc/tasks/SETTINGS-OPEN-B-2.md:88` 与 `doc/handoffs/SETTINGS-OPEN-B-2-0e2e623.md:27` 仍写 Lead 验收 **1251 passed / 3 skipped**（旧的 B-1 dirty 口径）；AC5 已明确实际 clean 为 1253/3，建议改为 clean 1253/3 或删除该行，避免下一次 Owner 误读。
- `canonical_evidence_status/resource_closeout_status` 仍为 pending，关闭时收口即可；本 Follow-up 文件若作为正式复审证据，需 Lead 追加到 canonical evidence 并刷新 pin（不修改旧 `review-b2.md` 的已固定 hash）。
