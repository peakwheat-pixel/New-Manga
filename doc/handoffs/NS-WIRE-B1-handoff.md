---
task_id: NS-WIRE-B1
author: saber-ui-spec (DSH team)
recipient: DeepSeek Harness
base_commit: b993e68bb
delivery_head: 2644214eba730373a191a576d4979010642c70e1
status: ready-for-integration
---

# Handoff：NS-WIRE-B1（高置信 NS 命令接线：13 条新增）

## 交付结果

实现提交 **`2644214eba730373a191a576d4979010642c70e1`**（branch `task/NS-WIRE-B1`，worktree `G:/CODEX/New Manga.workspace/worktrees/NS-WIRE-B1`，base 当前 HEAD `b993e68bb`；卡面原 base `45efe7f00` 已被后续合并推进，按 DSH 指令以 HEAD 为准）；本 Handoff 与任务卡 pin 在后续文档提交中记录。未 push、未改 Python Core/旧壳/协议语义、未改 Host 契约语义。

| AC | 结论 | 说明 |
|---|---|---|
| AC1 逐条 | **MET** | 批次清单 19 条中 6 条已由 RUN-EXPORT-E2E-1 接线（未重复改），本轮新增 **13 条**；C# 全链路真实执行 13/13（11 success + 2 typed 域错误），独立 wire 探针 17 probes。 |
| AC2 契约 | **MET** | 15 个非法参数全 `INVALID_ARGUMENTS` 且 0 Core 帧；P15=minor 7 / DELETE=minor 10 / CREATE=minor 8 由版本控制探针证明；typed Core 错误原样透传。 |
| AC3 parity | **MET** | `extract-command-surface.py --check` PASS 零漂移；parity 契约 46 IMPLEMENTED / 20 NOT_SUPPORTED / coverage 100；`parity-update.json` 记录 before 33/33 → after 46/20 与 13 条 changed_commands。 |
| AC4 回归 | **MET** | test.ps1 **161/161**（44/42/75）；vitest **60/567**；pytest **3F/2746P/9S**（基线一致，0 新增）。 |
| AC5 门禁 | **MET** | `check.ps1 -TaskPath` PASS；13 条 64-hex pin；本 Handoff 含 Record Decision。 |

## Record Decision（分批策略 / 边界 / 版本与 payload 规则）

1. **分批策略**：只接 DSH 清单中当前 HEAD 仍为 `NOT_SUPPORTED` 的 13 条。批次清单 19 条中 `library_start_run`/`library_control_run`/`library_resume_blocked_run`/`library_get_run_snapshot`/`library_get_task_projection`/`library_retry_failed_targets` 已由 RUN-EXPORT-E2E-1 接线（registry 24→33），本卡不重复改动、不重建其证据。
2. **与其它 Task 边界**：不接 region/reader 6 条（S4-CMD-BATCH-1）、不接 import/export 5 + 2 shell 动作（GRANT-ISSUER-1）。registry 冲突策略：以先落地者为准，后落地者 rebase；本卡改动集中在 `HostCommandRegistry.CoreBindings` 尾部 + `HostCommandDispatcher.WriteCorePayload` 尾部，冲突面小。
3. **路由与 minor**：逐条使用 `verification/NS-RECLASSIFY-1/reclassification.json` 中成功探测的 `protocol_minor`：backup/cleanup/plugin 面 **3**、P15 settings 面 **7**、`PermanentlyDeleteBook` **10**、`CreateBook` **8**（控制探针）。版本控制探针证明错误 minor 会被 `INVALID_REQUEST` 拒绝，避免「payload 对但版本错」的假实现。
4. **payload 翻译**：按旧壳 Tauri 签名在 dispatcher 显式构造（不是简单透传）。必填参数缺失/类型错误 → `INVALID_ARGUMENTS`，在**任何 Core 帧发出前**拒绝；可选参数只在存在时发送；`proxy_endpoint` 保留显式 JSON null；`library_delete_book_permanently` 兼容旧壳单参数 `payload:{book_id,confirm_permanent_delete}` 与内联两种调用风格；Core 业务错误码（`PLUGIN_NOT_FOUND`/`TARGET_NOT_FOUND`/`INVALID_REQUEST` 等）原样透传。
5. **验证口径**：真实请求冻结 `core_service.exe`；success 与 typed 域错误（not_found/conflict）都算实证；`INVALID_REQUEST`/`UNKNOWN_COMMAND`/`PROTOCOL_VERSION_UNSUPPORTED` 不算实现，必须修正 payload/minor 后重测。
6. **回归边界**：未改 Python Core、未改旧壳；pytest 仅作基线监控，不因本卡改动而调整。

## 本轮新增的 13 条（route / minor / 真实执行结果）

| NS 命令 | Core route | minor | 基座数据根真实执行 |
|---|---|---|---|
| backup_delete | backup.delete | 3 | success `{removed:true}`（先 backup_create 取真实 id） |
| cleanup_retry_pending | cleanup.retry_pending | 3 | success（CleanupOutcome） |
| plugins_audit_list | plugins.audit_list | 3 | success（audit ledger） |
| plugins_set_plugin_enabled | plugins.set_plugin_enabled | 3 | typed `PLUGIN_NOT_FOUND`（handler 运行） |
| library_delete_book_permanently | PermanentlyDeleteBook | 10 | success（临时根建书→真删除，`deleted:true`） |
| settings_network_profile_default_clear | 同名 | 7 | success `{network_profile_id:null}` |
| settings_network_profile_default_set | 同名 | 7 | success（回显 id） |
| settings_network_profiles_create | 同名 | 7 | success（返回 profile） |
| settings_network_profiles_delete | 同名 | 7 | success `{deleted:true}` |
| settings_network_profiles_update | 同名 | 7 | success（返回更新后 profile） |
| settings_provider_bindings_clear | 同名 | 7 | success `{cleared:true}` |
| settings_provider_bindings_resolve | 同名 | 7 | success（binding resolution view） |
| settings_provider_run_snapshot_get | 同名 | 7 | typed `TARGET_NOT_FOUND`（handler 运行） |

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 C# 全链路 | `test.ps1` 内 `CommandWiringB1Tests.B1Commands_ExecuteAgainstFrozenCore` | 冻结 core_service（AC11 无标签副本） | 13/13 执行；每条含 `request_line`（minor 可见） | `commands/ns-b1-integration.json` |
| AC1 独立 wire | `python verification/NS-WIRE-B1/tools/probe-b1.py --sidecar <AC11 副本>` | 冻结 core_service，独立临时数据根 | 17 probes：11 success + 2 typed 域错误 + 2 版本控制 + 2 控制探针 | `probe-results.json` |
| AC2 边界 | `CommandWiringB1Tests.B1Commands_RejectInvalidArgumentsBeforeAnyCoreFrame` | 同上 | 15 用例全 `INVALID_ARGUMENTS`；`core_frames_before == core_frames_after` | `commands/ns-b1-invalid-arguments.json` |
| AC3 零漂移 | `python apps/desktop-avalonia/scripts/extract-command-surface.py --check` | `b993e68bb` + 本卡 | PASS（66 命令，域分布不变） | `extract-command-surface-check.log` |
| AC3 parity | `CommandParityContractTests` | 同上 | 46 IMPLEMENTED / 20 NOT_SUPPORTED / coverage 100 | `commands/parity-contract.json`、`parity-update.json` |
| AC4 全量 | `pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1 -EvidenceDirectory <task-env>/evidence` | Windows 10.0.26300 | **161/161**（44/42/75） | `test/summary.json`、`test/dotnet-test-Debug.log`、`test/results-*.trx` |
| AC4 vitest / pytest | `npm test`（主仓）/ `PYTHONPATH=src python -m pytest -q`（worktree） | 旧壳/Python 未改 | 60 files / 567 tests；3F/2746P/9S | `test/vitest.log`、`test/pytest.log` |
| AC5 治理 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/NS-WIRE-B1.md` | 本卡 + 文档提交 | PASS | 任务卡 pin |

## 接收方式

- 分支/worktree：`task/NS-WIRE-B1` / `G:/CODEX/New Manga.workspace/worktrees/NS-WIRE-B1`；delivery head `2644214eb`。
- 复现：见 `verification/NS-WIRE-B1/REPORT.md §7`（test.ps1 / extract --check / probe-b1.py）。
- 真机/真实 sidecar 前置：AC11 无标签 sidecar 副本（本卡使用 `G:/CODEX/New Manga.workspace/task-envs/HOST-CORECLIENT-1/sidecar-copy`，sha256 由 probe 记录）；不碰用户真实 `%APPDATA%`。
- 需要 DSH 做：独立 Review（Owner 不自审）→ 运行 test.ps1 复核 → 合入/集成（注意 GRANT-ISSUER-1 / S4-CMD-BATCH-1 的 registry 并发冲突，先落地者为准、后落地者 rebase）→ closeout。

## 下一任务建议（必填）

- Task ID / 标题：**无新增实现任务需由我立即释放**；本批之后剩余 20 条 NOT_SUPPORTED（medium 11 + 其它 Task 范围 9）。
- 推荐 Agent / Reviewer：集成 = DSH；独立 Reviewer = 未参与实现的 Codex / ZCode / Antigravity（按 DSH 排班）。
- 推荐原因与前置依赖：NS-WIRE-B1 已把 13 条 high 置信命令落地为 IMPLEMENTED；下一批「medium 11 条」需要 DSH 先按 NS-RECLASSIFY evidence 判断是否值得接线（部分可能属 host-local 语义），并避免与 GRANT-ISSUER-1 / S4-CMD-BATCH-1 冲突；本卡不派生。
- Recovery point：仓库 `G:/CODEX/New Manga`；delivery head `2644214eb`；base `b993e68bb`。
- 允许修改路径：`apps/desktop-avalonia/**`、`doc/tasks/NS-WIRE-B1.md`、STATUS/PLAN/LEDGER、`verification/NS-WIRE-B1/**`、workspace task-env。
- 禁止范围：不改 Python Core 语义、不改 Host 契约/旧壳、不 push、不 gc/prune、不抢 S4/GRANT 范围。
- 交付物：本卡实现 + 证据 + Handoff 已完成；DSH 集成验证结论与 closeout 记录。
- 验证命令与完成 Gate：`test.ps1` 161/161、vitest 60/567、pytest 3F/2746P/9S、`extract-command-surface.py --check` PASS、`check.ps1 -TaskPath` PASS、13 条 pin、独立 Review 通过。
- 可直接转发给 Agent 的指令：

```text
作为独立 Reviewer（未参与实现），复核 NS-WIRE-B1（delivery 2644214eb，walkthrough 见 doc/handoffs/NS-WIRE-B1-handoff.md 与 verification/NS-WIRE-B1/REPORT.md）。
只读：不要修改代码。核对 AC1–AC5 与 13 条 pin（sha256 与文件一致）；重跑 pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1（应 161/161，注意其它 Agent 的 NewManga.App 占用全局互斥体时 LegacyShellRealTests 会假失败）、python apps/desktop-avalonia/scripts/extract-command-surface.py --check（应 PASS）、check.ps1 -TaskPath doc/tasks/NS-WIRE-B1.md（应 PASS）；抽查 13 条命令的 minor（P15=7 / DELETE=10 / CREATE=8）、dispatcher 的 INVALID_ARGUMENTS 边界与 delete 双调用兼容、以及 parity 契约 46/20；给出 PASS / 有条件 PASS / 返修 结论与具体证据行。
```

## 风险与遗留

1. 剩余 **20 条 NOT_SUPPORTED**：medium 11 条未释放批次；region/reader 6 条（S4-CMD-BATCH-1）、import/export 5 + shell 动作（GRANT-ISSUER-1）属其它 Task。
2. **UI 入口未接**：本卡只做 Host/registry 命令面；settings/plugins/backup 这些面在 Avalonia 设置页的表单/按钮接入需后续 UI Task。
3. **minor 硬编码**：P15=7 / DELETE=10 / CREATE=8 依赖冻结 core_service 2.3 的实际语义；Core 协议升级需重跑 `probe-b1.py` 并更新 `CoreBindings`。
4. **删除面**：`PermanentlyDeleteBook`（minor 10）是真删除；真实执行只在临时数据根建书→删除，未触碰 BOOK-FIXTURE/用户数据；UI 接入需沿用二次确认语义。
5. **并发冲突**：GRANT-ISSUER-1 / S4-CMD-BATCH-1 同时改 registry；若其它分支先合入，按「先落地者为准」rebase 并重跑 test.ps1。
6. 需独立 Review（Owner 不得自审）。
