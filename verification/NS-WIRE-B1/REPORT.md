# NS-WIRE-B1 验证报告（高置信 NOT_SUPPORTED 命令接线第一批）

- Task: `doc/tasks/NS-WIRE-B1.md`（team task-31）
- Branch / worktree: `task/NS-WIRE-B1` / `G:/CODEX/New Manga.workspace/worktrees/NS-WIRE-B1`
- Base: `b993e68bb`（DSH 指定的当前 HEAD；卡面 `45efe7f00` 已被后续合并推进，按 DSH 指令以 HEAD 为准）
- 未 push；未改 Python Core；未改旧壳；未改协议/Host 契约语义；未抢 S4-CMD-BATCH-1（region/reader 6 条）与 GRANT-ISSUER-1 的范围。

## 1. 结论

| AC | 结论 | 证据 |
|---|---|---|
| AC1 逐条接线 | **MET** | 批次清单 19 条中 **6 条已由 RUN-EXPORT-E2E-1 接线**（`library_start_run`/`library_control_run`/`library_resume_blocked_run`/`library_get_run_snapshot`/`library_get_task_projection`/`library_retry_failed_targets`），本轮**实际新增接线 13 条**，逐条按 `reclassification.json` 的 `core_command`/`face`/probe payload/minor 落到 `HostCommandRegistry` + `HostCommandDispatcher`；13 条全部对冻结 sidecar 真实执行（11 条 success + 2 条 typed 域错误 `PLUGIN_NOT_FOUND`/`TARGET_NOT_FOUND` 证明 handler 运行）。见 §3/§4。 |
| AC2 契约/边界 | **MET** | 参数边界在 dispatcher 层校验（`INVALID_ARGUMENTS`）：15 个非法用例全部在**任何 Core 帧发出前**被拒（`core_frames_before == core_frames_after`）；Core 业务错误码原样透传（`PLUGIN_NOT_FOUND`/`TARGET_NOT_FOUND`/`INVALID_REQUEST` 等）。版本坑用独立 wire 探针验证：P15 settings 面 **minor 7** 成功、minor 3 被 `INVALID_REQUEST` 拒绝；DELETE 面 **minor 10** 成功、minor 3 被拒；CREATE 面 minor 8（控制探针）。 |
| AC3 parity | **MET** | `extract-command-surface.py --check` **PASS 零漂移**（66 命令/域分布不变）；parity 契约 `implemented 46 / not_supported 20 / coverage 100 / every_command_has_owner=true`；`parity-update.json` 记录 before 33/33 → after 46/20 与 13 条 changed_commands；逐条 wire probe `probe-results.json`（17 probes：11 success + 2 typed domain + 2 version controls + 2 控制探针）。 |
| AC4 回归 | **MET** | `scripts/test.ps1` **TEST PASS 161/161, 0 skipped**（coreclient 44 / host 42 / app 75）；旧壳 vitest **60 files / 567 tests passed**；pytest **3 failed / 2746 passed / 9 skipped**（与基线 3F/2746P/9S 完全一致，0 新增）。 |
| AC5 门禁 | **MET** | `check.ps1 -TaskPath` PASS；14 条 64-hex pin；`doc/handoffs/NS-WIRE-B1-handoff.md` 含 Record Decision。 |

## 2. Record Decision：分批策略 / 边界 / 版本与 payload 规则

| 项 | 决定 | 依据 |
|---|---|---|
| 批次范围 | 只接 DSH 清单里**当前 HEAD 仍为 NOT_SUPPORTED** 的 13 条；已 IMPLEMENTED 的 6 条不重复改（避免与 RUN-EXPORT-E2E-1 冲突） | HEAD `b993e68bb` 的 `HostCommandRegistry` CoreBindings；卡面 19 条清单 |
| 与其它 Task 边界 | 不碰 region/reader 6 条（S4-CMD-BATCH-1）、不碰 import/export 5 + 2 shell 动作（GRANT-ISSUER-1）；registry 冲突策略=先落地者为准、后落地者 rebase（本卡 Handoff 已注明） | 卡面「禁止范围」「并发」 |
| 路由/minor | 逐条使用 `verification/NS-RECLASSIFY-1/reclassification.json` 中**成功探测**的 `protocol_minor`：backup/cleanup/plugin/run 面 minor 3；P15 settings 面 minor 7；`PermanentlyDeleteBook` minor 10；CREATE 面 minor 8（控制项） | `probe-results.json` + 本卡 §3 版本控制探针 |
| payload 翻译 | 按旧壳 Tauri 签名在 dispatcher 显式构造 payload（不是简单透传）：必填参数缺失/类型错误 → `INVALID_ARGUMENTS`；可选参数只在存在时发送；可空字符串（`proxy_endpoint`）保留显式 `null`；`library_delete_book_permanently` 兼容旧壳 `payload:{book_id,confirm_permanent_delete}` 单参数与内联两种调用 | `HostCommandDispatcher.WriteCorePayload` + `CommandWiringB1Tests` |
| 验证口径 | 「真实执行」= 对冻结 core_service 发出真实请求；success 与 typed 域错误（not_found/conflict）都算实证；`INVALID_REQUEST`/`UNKNOWN_COMMAND` 不算实现，必须修复后重测 | 沿用 NS-RECLASSIFY 口径 |
| 回归 | 不改 Python Core；pytest 仅作为基线监控 | 卡面禁止范围 |

## 3. 本轮实际接线的 13 条（含真实执行结果）

| # | NS 命令 | Core route | minor | 真实执行结果 | face |
|---|---|---|---|---|---|
| 1 | `backup_delete` | `backup.delete` | 3 | success `{removed:true}`（先 `backup_create` 取真实 id） | S3-C backup |
| 2 | `cleanup_retry_pending` | `cleanup.retry_pending` | 3 | success（CleanupOutcome） | S3-C cleanup |
| 3 | `plugins_audit_list` | `plugins.audit_list` | 3 | success（audit ledger，`limit=5`） | PLUGIN-RUNTIME-1 |
| 4 | `plugins_set_plugin_enabled` | `plugins.set_plugin_enabled` | 3 | typed `PLUGIN_NOT_FOUND`（handler 运行证明） | PLUGIN-RUNTIME-1 |
| 5 | `library_delete_book_permanently` | `PermanentlyDeleteBook` | **10** | success（真实建书→永久删除 `deleted:true`） | DELETE 面 |
| 6 | `settings_network_profile_default_clear` | 同名 | **7** | success `{network_profile_id:null}` | P15 network |
| 7 | `settings_network_profile_default_set` | 同名 | **7** | success（回显 profile id） | P15 network |
| 8 | `settings_network_profiles_create` | 同名 | **7** | success（返回 profile） | P15 network |
| 9 | `settings_network_profiles_delete` | 同名 | **7** | success `{deleted:true}` | P15 network |
| 10 | `settings_network_profiles_update` | 同名 | **7** | success（返回更新后 profile） | P15 network |
| 11 | `settings_provider_bindings_clear` | 同名 | **7** | success `{cleared:true}` | P15 provider |
| 12 | `settings_provider_bindings_resolve` | 同名 | **7** | success（binding resolution view） | P15 provider |
| 13 | `settings_provider_run_snapshot_get` | 同名 | **7** | typed `TARGET_NOT_FOUND`（handler 运行证明） | P15 provider |

已 IMPLEMENTED、本轮**未改动**的 6 条：`library_start_run`、`library_control_run`、`library_resume_blocked_run`、`library_get_run_snapshot`、`library_get_task_projection`、`library_retry_failed_targets`（RUN-EXPORT-E2E-1 已接线）。

## 4. 实现摘要（全部 `apps/desktop-avalonia/**`）

| 文件 | 改动 |
|---|---|
| `src/NewManga.CoreClient/Commands/HostCommandRegistry.cs` | 13 条 `CoreBindings`（route + minor）；类文档实现集说明更新为 46/20。 |
| `src/NewManga.CoreClient/Commands/HostCommandDispatcher.cs` | 13 条 payload 翻译与参数边界校验；新增 `WriteNullableString`/`WriteOptionalBool`/`WriteOptionalInt`/`OptionalObject` 辅助。 |
| `tests/NewManga.CoreClient.Tests/Commands/CommandWiringB1Tests.cs`（新，4 项） | registry 路由/minor 断言；真实执行 13 条（含两条 typed 域错误）并记录每条请求行（协议 minor 可见）；15 个非法参数用例全部 `INVALID_ARGUMENTS` 且 Core 帧数为 0 增量（AC2 证据）。 |
| `tests/NewManga.CoreClient.Tests/Commands/CommandParityContractTests.cs` | 实现/未实现计数 33/33 → 46/20。 |
| `tests/NewManga.CoreClient.Tests/Commands/CommandIntegrationTests.cs` | 域服务实现计数 33 → 46；NOT_SUPPORTED 类型错误数 33 → 20。 |
| `verification/NS-WIRE-B1/tools/probe-b1.py`（新） | 独立 wire 级探针：对冻结 `core_service.exe` 发 17 次请求（13 条接线 + 2 控制探针 + 2 版本控制），输出请求行/响应/basis。 |

## 5. 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 真实执行（C# 全链路） | `dotnet test ... --filter FullyQualifiedName~CommandWiringB1Tests`（test.ps1 内跑） | 冻结 `core_service`（AC11 无标签副本）；fixture 空数据根 | 13/13 执行：11 success + 2 typed 域错误；每条含 `request_line`（minor 可见） | `commands/ns-b1-integration.json` |
| AC1 真实执行（独立 wire） | `python verification/NS-WIRE-B1/tools/probe-b1.py` | 冻结 `core_service.exe`（sha256 见 `probe-results.json`），独立临时数据根 | 17 probes；版本控制：P15 minor3 → `INVALID_REQUEST`、DELETE minor3 → `INVALID_REQUEST`；minor7/10 → success | `probe-results.json` |
| AC2 边界 | `CommandWiringB1Tests.B1Commands_RejectInvalidArgumentsBeforeAnyCoreFrame` | 同上 | 15 用例全 `INVALID_ARGUMENTS`；`core_frames_before == core_frames_after` | `commands/ns-b1-invalid-arguments.json` |
| AC3 零漂移 | `python apps/desktop-avalonia/scripts/extract-command-surface.py --check` | `b993e68bb` + 本卡改动 | **PASS**（66 命令，域分布不变） | `extract-command-surface-check.log` |
| AC3 parity | `CommandParityContractTests` 生成契约 | 同上 | implemented 46 / not_supported 20 / coverage 100 | `commands/parity-contract.json`、`parity-update.json` |
| AC4 全量 | `pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1 -EvidenceDirectory <task-env>/evidence` | Windows 10.0.26300 | **161/161**（44/42/75） | `test/summary.json`、`test/dotnet-test-Debug.log`、`test/results-*.trx` |
| AC4 vitest | `cd apps/desktop/frontend && npm test`（主仓；`git diff b993e68bb -- apps/desktop/frontend` 为空） | 旧壳未改 | **60 files / 567 tests** | `test/vitest.log` |
| AC4 pytest | `PYTHONPATH=src python -m pytest -q`（worktree，未改 Python） | 未改 Core | **3F/2746P/9S**（基线一致） | `test/pytest.log` |
| AC5 治理 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/NS-WIRE-B1.md` | 本卡 + 文档提交 | PASS | 任务卡 pin |

## 6. 遗留 / 未关闭项（记录不阻塞）

1. **剩余 20 条 NOT_SUPPORTED**：其中 medium 置信批次（11 条）尚未释放；另有 region/reader 6 条（S4-CMD-BATCH-1）、import/export 5 + shell 动作（GRANT-ISSUER-1）在其它 Task 范围，本卡不接。
2. **UI 入口未接**：本卡只做 Host/registry 命令面接线；settings/plugins/backup 的这些面在 Avalonia 设置页的按钮/表单接入属于后续 UI Task（当前设置页仅覆盖部分）。
3. **版本硬编码**：P15=7 / DELETE=10 / CREATE=8 依赖冻结 core_service 2.3 的实际 minor 语义；若后续 Core 协议 minor 提升，需重新跑版本控制探针并更新 `CoreBindings`（已留 `probe-b1.py` 可复跑）。
4. **删除面风险**：`PermanentlyDeleteBook`（minor 10）是真删除；真实执行只在临时数据根上建书→删除，未触碰 BOOK-FIXTURE 或用户数据；UI 接入时需沿用旧壳的二次确认语义（`confirm_permanent_delete` 布尔由调用方给出，Core 仍会校验）。
5. **并发**：GRANT-ISSUER-1 / S4-CMD-BATCH-1 同时改 registry；本卡基于 `b993e68bb` 落地，若其它分支先合入则按「先落地者为准」rebase（本卡改动集中在 CoreBindings 尾部 + dispatcher switch，冲突面小）。
6. 需独立 Review（Owner 不得自审）。

## 7. 复现

```pwsh
# 1) 回归（161 项）
pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1 -EvidenceDirectory G:\CODEX\New Manga.workspace\task-envs\NS-WIRE-B1\evidence

# 2) 零漂移
python apps/desktop-avalonia/scripts/extract-command-surface.py --check

# 3) 独立 wire 探针（需冻结 sidecar 无标签副本）
python verification/NS-WIRE-B1/tools/probe-b1.py --sidecar G:\CODEX\New Manga.workspace\task-envs\HOST-CORECLIENT-1\sidecar-copy
```
