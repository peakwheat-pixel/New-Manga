---
task_id: FEA-13-RESTORE-4
reviewer: 独立上下文子 agent（由 parent session-c08ea2ac-cbcf-47ac-a7a9-0e15254b3fa5 派发；未参与实现/返修，只读被审 head）
reviewer_kind: subagent
author: dsh
base_commit: 0dc4ff85f
reviewed_head: fcccf4604（r1 报告 0db250882；r2 返修 fcccf4604）
decision: approve
---

# Review r2：FEA-13-RESTORE-4（r1 changes_requested → 返修复审）

## 范围

- 被审：`git diff 0db250882..fcccf4604`（11 文件，+240/-82）。生产码仅 `restore_plan.py` 与 `core_service.py`；余为测试、卡、EV 日志。
- 依据：`doc/tasks/FEA-13-RESTORE-4.md` §Review 处置（r1 的 R4-001…R4-013 → 本报告 R4-001…R4-008 + P3-1…P3-5）、r1 报告、ADJ 裁决、README/EV。
- 未审（沿用登记）：真实进程 kill 崩溃注入、Host/UI 端到端、跨机恢复。本轮无 C# diff。
- 只读：未改生产码/测试/契约/pins，未 commit/push；除本报告外工作区 clean。

## 门禁复跑（本会话）

| 命令 | 结果 | EXIT |
|---|---|---|
| `python -m pytest tests/storage/test_nmbak_merge_restore.py tests/core/test_core_restore_plan.py tests/storage/test_nmbak_backup.py -q` | **35 passed**（3.91s） | 0 |
| `dotnet build apps/desktop-avalonia/NewManga.sln -c Debug --nologo` | 0 警告 / 0 错误 | 0 |
| `check.ps1 -TaskPath doc/tasks/FEA-13-RESTORE-4.md` | PASS（3 warnings：12 非终态 Task / STATUS 80% / REBASELINE 80%） | 0 |
| `verify_pins.ps1` | PIN AUDIT: PASS (all 18) | 0 |
| EV 6 条 sha256 逐条 `Get-FileHash` | **6/6 与当前字节一致**（README `632efc5f…`、SUITE `68668e88…`、BUILD `3a6cbfe7…`、MUT1 `095c5901…`、MUT2 `c1bac687…`、MUT3 `6eed5bce…`） | — |
| `git status --short` | 仅本报告未跟踪；其余 clean | — |

- EV suite 日志自身命令为 9 文件批次 → **96 passed**；本会话按要求复跑 3 文件 → 35 passed，两者不冲突。
- 变异日志：MUT1 杀 `test_defer_ignores_use_backup_entries`、MUT2 杀 `test_write_commands_fail_closed…`（`cleanup.run`）、MUT3 杀 `test_merge_restore_refuses_a_package_from_another_database`，均 `1 failed / 6 passed`、EXIT 1，与 README 一致。

## 逐条判定

| ID | 判定 | 核实要点 |
|---|---|---|
| R4-001 跨库/run 门禁 | **PARTIAL** | `_merge_restore` 先 `_verify_package(_resolve(id))` → `database_id` 与 `_current_database_id()` 比对（缺失任一侧则跳过，与 overwrite 同口径），随后 `_is_run_active()` → `BACKUP_RESTORE_BUSY`；两码均已在 §3.4 映射表。装配 `is_run_active=lambda: _has_active_run(conn)`（core_assembly:1935）。跨库新增 core 用例已 RED 判别；**`BACKUP_RESTORE_BUSY` 分支无用例**（处置要求“两条 RED 用例”），仅代码可证。 |
| R4-002 L-5 门 | **PARTIAL** | dispatch 门仍在（`:7847`，改为 `_restore_lock_exempt`）；**新增 pipeline 命令入口门**：`_dispatch_run_command` 在所有 Prepare/Accept/Start/Control/Resume/Retry 之前检查 `_restore_maintenance_active` → `PipelineError("RESTORE_IN_PROGRESS")`。残留：①该新门无测试（MUT2 只杀 dispatch 门）；②调度线程 `_run_scheduler_loop → run_pending_once()` 仍未检查同一 flag（处置③）；真实风险由入口 `_is_run_active` 间接闭合（窗口内无法新建 run，活跃 run 会先被拒）；③处置④“串行 serve 下门语义/跨进程由 Host 单连接保证”说明未登记入 README/卡。 |
| R4-003 mode 参与判定/校验时机 | **FIXED** | `apply_restore` 入口先校验 `mode ∈ {defer,use_backup}` 再 ATTACH/BEGIN（任何写之前）；`selected = mode=="use_backup" and …`；`test_defer_ignores_use_backup_entries` 证明 defer+entries 不覆盖（MUT1 可杀）。 |
| R4-004 managed 层可见 | **FIXED** | `plan_restore(..., managed_root=service._managed_root, backup_entries=context["managed_entries"])`，wire 计划现含 managed 项；apply 仍 deferred（按处置登记）。 |
| R4-005 marker/顺序 | **FIXED** | plan 先算、marker 后写（消除 UnboundLocal），`staging`/`committed` 均含 `plan_digest`（sha256(items)，summary 为其纯函数，等价）与 `package_sha256`，`committed` 含 `applied` 计数；崩溃用例仍成立并通过。启动期清理登记于 README（处置允许）。 |
| R4-006 过期拒绝 | **FIXED** | `expected_package_sha256` 与 `context["package_sha256"]` 比对 → `NmbakBackupError("RESTORE_PLAN_STALE")`（category=conflict, retryable=False），位于 staging/写库之前；新用例断言该码且 live `title=="BEFORE"`（零写）。 |
| R4-007 列名映射 | **FIXED** | `_replace_row` 用 `dict(zip(backup_columns, row))` 按列名取值、按 live 列名组参；备份缺列时 `KeyError` 被 per-item `except` 捕获 → 该项 fail-closed，不静默错位。 |
| R4-008 undo fsync | **FIXED** | `_preserve_row` 改为 `open→write→flush→os.fsync`；异常上抛 → 该项记入 `failed` 且不覆盖。目录 fsync 未做（处置未要求）。 |
| P3-1 AC1 mtime/7 表 | **PARTIAL** | 快照新增 `package_mtime` 与 `managed_mtime` 且 `assert after == before`，mtime 已断言；DB 行快照仍只 books/pages（7 表未扩）。 |
| P3-2 ADJ 入 allowed_paths | **FIXED** | 卡 `allowed_paths` 增 `doc/reviews/ADJ-2026-11-09-FEA13-RESTORE-MODEL.md`；本轮 11 个改动文件全部 ⊆ allowed_paths。 |
| P3-3 L-5 豁免分级 | **PARTIAL** | 改为 `_restore_lock_exempt`：`core.ping`、`backup.create`、`*.list` 放行；`backup.delete` 已移出。但处置要求 `*.get` 同级放行，`settings.get` 仍被阻断（无 `.get` 后缀分支）。测试改断言 `cleanup.run` 被拒，读放行路径无用例。 |
| P3-4 staging 语义/残留 | **FIXED** | README 明确 staging 为“复制+校验的提交凭据（应用走 ATTACH 原包）”，启动期清理登记后续。 |
| P3-5 C#/wire 登记 | **PARTIAL** | README 残余已登记“C# 未加 `PlanRestoreAsync`/`RestoreAsync(mode)`，wire 字段已支持”；但处置承诺的 C# 骨架未实现（allowed_paths 已含 C# 文件，本轮无 C# diff）。 |

**计数：FIXED 8 / PARTIAL 5 / OPEN 0。** OPEN 列表：空。

## AC 判定

| AC | 判定 | 要点 |
|---|---|---|
| AC1 只读预览 | MET | 前后行/managed 字节与 mtime/包 sha+mtime 全等；行覆盖 nit 见 P3-1。 |
| AC2 默认 defer | MET | 新用例 `test_defer_applies_backup_only_rows` 实证 5 表 add 被应用；defer+entries 不覆盖（R4-003）。 |
| AC3 UseBackup 保全 | MET | 先保全后覆盖、fsync、缺 undo 区逐项 fail-closed 且已测。 |
| AC4 过期拒绝 | MET | 非法 mode→`INVALID_REQUEST`；`RESTORE_PLAN_STALE` 有抛出点 + 零写用例。注：无 wire 预览命令在 apply 前回传 `package_sha256`（仅 apply 报告携带），端到端“预览→换包”仍只能由库层驱动。 |
| AC5 L-5 + staging/marker | MET | marker 载荷/状态机、崩溃后 `staging` 且 live 不变、锁释放、dispatch+pipeline 双门。 |
| AC6 门禁 | MET | pytest/build/check/pins/EV 6/6/diff⊆allowed_paths 全 PASS（见上表）。 |

## 新增 findings（无 P0/P1）

| ID | 级别 | 位置 | 问题 |
|---|---|---|---|
| N1 | P3 | `verification/FEA-13-RESTORE-4/README.md:24,29` | 文本两处写“91 passed”，而同目录 canonical suite 日志为 **96 passed**（sha 一致、日志为准）→ 证据叙述与字节不一致。 |
| N2 | P3 | `doc/tasks/FEA-13-RESTORE-4.md` 头 | `delivery_head` 仍 `f9ebce677`，而 r2 返修 `fcccf4604` 改了 src/tests；卡未记录 r2 head（`check.ps1` 仍 PASS，交 DSH closeout 更新）。 |
| N3 | P3 | `restore_plan.py`（COMMIT 之后） | 入口校验后仍残留一处 `if mode not in {...}: raise ValueError` 死代码（不可达）。 |
| N4 | P3 | 测试覆盖 | pipeline 入口门与 `BACKUP_RESTORE_BUSY` 门均无用例；MUT2 无法覆盖新门。 |
| N5 | P3 | `_merge_restore` | COMMIT 成功与写 `committed` marker 之间崩溃仍留“state=staging 但已提交”的歧义窗口（r1 R4-005 项，未登记到 README 残余）。 |
| N6 | P3 | wire | `_BACKUP_COMMANDS` 无预览命令，`package_sha256` 仅在 apply 报告返回 → stale 门要求调用方离线自带 digest。 |
| N7 | P3 | 卡 AC4 行 | 标记 `<<MET>>` 但仍保留旧注“端到端用例未做，登记 PARTIAL”，自相矛盾。 |

## 结论

- **decision: approve**。r1 的 2 个 P1 在代码层均已闭合（merge 与 overwrite 同口径的库身份/run 门禁；L-5 覆盖 dispatch + pipeline 双入口，活跃 run 由入口拒绝），6 个 P2 全部 FIXED，AC1–AC6 全 MET，门禁与 EV 6/6 可复现，工作区 clean。
- 未关闭项全部为 P3 级：R4-001/R4-002 的测试/登记缺口、P3-1/P3-3/P3-5 的残余、以及 N1–N7。建议 DSH 在 closeout 时一并更新 `delivery_head`、README 的 91→96、AC4 旧注与残余登记（无需再开返修轮）。
- 本轮门禁/变异数字只对 `fcccf4604` 有效。
