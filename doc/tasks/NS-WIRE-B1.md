---
id: NS-WIRE-B1
title: 高置信 NS 命令接线（18 条）
kind: implementation
governance_version: 3
status: done
approval: user_authorized_2026-10-27_ns_b1_grant
suggested_owner: saber-ui-spec
owner: saber-ui-spec
reviewer: dsh
depends_on: []
base_commit: b993e68bb
branch: task/NS-WIRE-B1
worktree: G:/CODEX/New Manga.workspace/worktrees/NS-WIRE-B1
integration_commit: 6b47f377f
delivery_head: 2644214eba730373a191a576d4979010642c70e1
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/NS-WIRE-B1
allowed_paths:
  - doc/tasks/NS-WIRE-B1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/NS-WIRE-B1/**
  - G:/CODEX/New Manga.workspace/task-envs/NS-WIRE-B1/**
  - G:/CODEX/New Manga.workspace/worktrees/NS-WIRE-B1/**
---

# NS-WIRE-B1：高置信 NS 命令接线（第一批 18 条）

> 交付状态：**ready-for-integration**（实现 `2644214eb` + 证据 + Handoff 已完成；待 DSH 复核/集成；Owner 不自审）。
> 说明：DSH 指定分支基于当前 HEAD `b993e68bb`（卡面原记 `45efe7f00` 已被后续合并推进）；批次清单 19 条中 6 条已由 RUN-EXPORT-E2E-1 接线，本轮**实际新增接线 13 条**，registry 33/33 → **46/20**。

## 背景

NS-RECLASSIFY-1 重探测证明 42 条 NOT_SUPPORTED 中 35 条实际可执行（24 high / 11 medium）。本批接线 **high 置信中不与其它 Task 重叠的命令**。

## 范围（卡面 19 条，来源 `verification/NS-RECLASSIFY-1/reclassification.json`）

backup_delete、cleanup_retry_pending、library_control_run、library_delete_book_permanently、library_get_run_snapshot、library_get_task_projection、library_resume_blocked_run、library_retry_failed_targets、library_start_run、plugins_audit_list、plugins_set_plugin_enabled、settings_network_profile_default_clear、settings_network_profile_default_set、settings_network_profiles_create、settings_network_profiles_delete、settings_network_profiles_update、settings_provider_bindings_clear、settings_provider_bindings_resolve、settings_provider_run_snapshot_get。

**排除**：region 4 + reader 2（S4-CMD-BATCH-1 负责）、import/export 5 + 2 shell 动作（GRANT-ISSUER-1 负责）、medium 11 条（后续批次）。

## Acceptance Criteria

- [x] **AC1 逐条**：按 `reclassification.json` 的 `core_command`/`face`/probe payload，在 C# `HostCommandRegistry`/dispatcher 接线；每条对冻结 sidecar **真实执行**断言（成功或 typed 域错误均算实证）。→ **MET**：13 条新增接线逐条落到 registry+dispatcher；C# 全链路真实执行 13/13（11 success + 2 typed 域错误）；独立 wire 探针 17 probes（含 2 版本控制）全过。已 IMPLEMENTED 的 6 条（RUN-EXPORT-E2E-1）未重复改动。证据：`probe-results.json`、`commands/ns-b1-integration.json`。
- [x] **AC2 契约**：参数边界校验（INVALID_ARGUMENTS）+ Core 业务错误码透传；P15 settings minor=7、Create minor=8、DELETE 面 minor=10（避免踩 NS-RECLASSIFY 记录的版本坑）。→ **MET**：15 个非法参数用例全 `INVALID_ARGUMENTS` 且 Core 帧数 0 增量；wire 探针证明 P15 minor 7 成功/3 拒、DELETE minor 10 成功/3 拒、CREATE minor 8 成功；`PLUGIN_NOT_FOUND`/`TARGET_NOT_FOUND` 等 typed 码原样透传。证据：`commands/ns-b1-invalid-arguments.json`、`probe-results.json`。
- [x] **AC3 parity**：`extract-command-surface.py --check` 零漂移；快照 18 条 NOT_SUPPORTED→IMPLEMENTED；证据 `verification/NS-WIRE-B1/**`（含逐条 probe-result）。→ **MET**：extract `--check` PASS（66 命令/域分布不变）；parity 契约 **implemented 46 / not_supported 20 / coverage 100**；本批 changed_commands 13 条（其余 6 条已由 RUN-EXPORT-E2E-1 记录）。证据：`extract-command-surface-check.log`、`commands/parity-contract.json`、`parity-update.json`、`probe-results.json`。
- [x] **AC4 回归**：`scripts/test.ps1` 全绿（含新增）；vitest 60/567；pytest 相对基线（3F/2746P/9S）无新增失败。→ **MET**：test.ps1 **161/161 passed, 0 skipped**（coreclient 44 / host 42 / app 75）；vitest **60 files / 567 tests**；pytest **3F/2746P/9S**（与基线一致）。证据：`test/summary.json`、`test/dotnet-test-Debug.log`、`test/vitest.log`、`test/pytest.log`。
- [x] **AC5 门禁**：`check.ps1 -TaskPath` PASS；64-hex pin；Handoff + Record Decision（分批策略/与 S4/C 批边界）。→ **MET**：`pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/NS-WIRE-B1.md` PASS；13 条 Canonical Evidence pin；`doc/handoffs/NS-WIRE-B1-handoff.md`（含 Record Decision）。

## Record Decision（摘要，完整版在 Handoff）

| 项 | 决定 |
|---|---|
| 批次范围 | 只接当前 HEAD 仍为 NOT_SUPPORTED 的 13 条；RUN-EXPORT-E2E-1 已实现的 6 条不重复改 |
| 与其它 Task 边界 | 不碰 S4-CMD-BATCH-1（region/reader 6 条）与 GRANT-ISSUER-1（import/export + shell 动作）；registry 冲突=先落地者为准、后落地者 rebase |
| 路由/minor | 使用 NS-RECLASSIFY 成功探测的 minor：backup/cleanup/plugin 面 3；P15 settings 面 7；DELETE 面 10；CREATE 面 8（控制项） |
| payload 翻译 | dispatcher 按旧壳 Tauri 签名显式构造；必填校验→`INVALID_ARGUMENTS`（零 Core 帧）；可选参数仅存在时发送；`proxy_endpoint` 保留显式 null；delete 兼容旧壳单参数 `payload:{...}` 与内联 |
| 验证口径 | 真实请求冻结 core_service；success 与 typed 域错误均算实证；`INVALID_REQUEST`/`UNKNOWN_COMMAND` 不算实现 |

## 实现摘要（全部 `apps/desktop-avalonia/**`）

- `HostCommandRegistry.cs`：13 条 CoreBindings（route+minor），实现集文档 46/20。
- `HostCommandDispatcher.cs`：13 条 payload 翻译与边界校验；新增 `WriteNullableString`/`WriteOptionalBool`/`WriteOptionalInt`/`OptionalObject`。
- `CommandWiringB1Tests.cs`（新，4 项）：registry 断言、13 条真实执行（含请求行证据）、15 个非法参数零帧增量。
- `CommandParityContractTests.cs` / `CommandIntegrationTests.cs`：实现计数 46/20 与域服务计数更新。
- `verification/NS-WIRE-B1/tools/probe-b1.py`（新）：独立 wire 级探针（含版本控制）。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| B1-TEST-SUMMARY | AC4 | verification/NS-WIRE-B1/test/summary.json | 2644214eba730373a191a576d4979010642c70e1 | 49586894c48939bdf1ec7d5d792993c61163ac8590ab3bcd235d6c7b17471f2d | CANONICAL |
| B1-TEST-LOG | AC4 | verification/NS-WIRE-B1/test/dotnet-test-Debug.log | 2644214eba730373a191a576d4979010642c70e1 | 7dd16a46e5b2572eb299f244db25a490d479ac67d0b80050a3a2cb65b70faccd | CANONICAL |
| B1-VITEST | AC4 | verification/NS-WIRE-B1/test/vitest.log | 2644214eba730373a191a576d4979010642c70e1 | 5bee660c7881f9f014ed2123e3e8510c080d47111e7b50dca9f968aa9ea27693 | CANONICAL |
| B1-PYTEST | AC4 | verification/NS-WIRE-B1/test/pytest.log | 2644214eba730373a191a576d4979010642c70e1 | 4e504eb0ef53cca9f423bd12eff0f4a503009ccacb9a0d5175bf8009c39a6c0b | CANONICAL |
| B1-TEST-PS1-LOG | AC4 | verification/NS-WIRE-B1/test/test.ps1-final.log | 2644214eba730373a191a576d4979010642c70e1 | 739ea0b019ae3ffbaf0be9b326a3a62229f727eb1bf2358ff72b911c87fcdc76 | CANONICAL |
| B1-PARITY-CONTRACT | AC3 | verification/NS-WIRE-B1/commands/parity-contract.json | 2644214eba730373a191a576d4979010642c70e1 | 84f7cf17d3469c7e2a5cd9d13767f46f96a8e1f71ba08837c38fdab8ea357eb1 | CANONICAL |
| B1-INTEGRATION | AC1/AC2 | verification/NS-WIRE-B1/commands/ns-b1-integration.json | 2644214eba730373a191a576d4979010642c70e1 | 1ca8f956b661c793e823079ba088d67e2e54f4875b60efaa395a93ed0afa98d7 | CANONICAL |
| B1-INVALID-ARGS | AC2 | verification/NS-WIRE-B1/commands/ns-b1-invalid-arguments.json | 2644214eba730373a191a576d4979010642c70e1 | fec4ebcb4378744e7891b4067845cbb12a406b0c83b143c53a39073b37c19209 | CANONICAL |
| B1-PROBE | AC1/AC2/AC3 | verification/NS-WIRE-B1/probe-results.json | 2644214eba730373a191a576d4979010642c70e1 | 5e8c2d287d55807b6e138914bc36d066a2c4ca2441983505ff49dff8b1eca9cf | CANONICAL |
| B1-PARITY-UPDATE | AC3 | verification/NS-WIRE-B1/parity-update.json | 2644214eba730373a191a576d4979010642c70e1 | 80579eed6ce201b18ea198f4dc47d4c4d4e7e5cc89bbd72c143f81f805c53783 | CANONICAL |
| B1-EXTRACT-CHECK | AC3 | verification/NS-WIRE-B1/extract-command-surface-check.log | 2644214eba730373a191a576d4979010642c70e1 | 820f6d456abeab98d52599b5fffdfa051b58369b8a108e8860b1fde4f6db82fe | CANONICAL |
| B1-PROBE-SOURCE | AC1/AC2 | verification/NS-WIRE-B1/tools/probe-b1.py | 2644214eba730373a191a576d4979010642c70e1 | 72789950d231436485b9ca0639d475d1ce05f53c34dc9c77bf0541f2ac34847b | SOURCE_PIN |
| B1-REPORT | AC5 | verification/NS-WIRE-B1/REPORT.md | 2644214eba730373a191a576d4979010642c70e1 | 62c1dce4e9c319a510777be481222f0739a1e6308e73816048a58ca99b2ffcd5 | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/NS-WIRE-B1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/NS-WIRE-B1 | `evidence/`（test/commands/logs）；不含构建产物 | 2026-10-27 本卡收口时目录存在；`test/summary.json` 与 parity 证据引用其路径；未移动/未删除；关闭时由 DSH 复核 |

## Closeout Record

- Closeout date / DSH：待关闭时填写（owner 交付 `2644214eb`，待 DSH 集成验证与独立 Review）。
- canonical_evidence_status：`complete`（13 条 pin：12 CANONICAL + 1 SOURCE_PIN，指向 delivery_head）。
- resource_closeout_status：`pending`（task-env 保留引用，未清理）。
- 删除、迁移、归档数量/字节数：0（本任务未删除任何文件；真实删除测试只在临时数据根创建并删除测试书）。
- 未关闭项及保留原因：剩余 20 条 NOT_SUPPORTED（medium 11 + 其它 Task 范围 9）；本批只做 Host 命令面，未接 Avalonia 设置页 UI 入口（后续 UI Task）；minor 硬编码依赖冻结 core_service 2.3，Core 协议升级需重跑版本控制探针；与 GRANT-ISSUER-1 / S4-CMD-BATCH-1 的 registry 冲突按先落地者为准 rebase；需独立 Review。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
## Review（DSH 集成复核，2026-10-27）— PASS

- **实际接线 13 条**（清单 19 条中 6 条已由 RUN-EXPORT-E2E-1 接线，未重复改）：backup_delete、cleanup_retry_pending、plugins_audit_list、plugins_set_plugin_enabled、library_delete_book_permanently、settings_network_profile_default_clear/set、settings_network_profiles_create/delete/update、settings_provider_bindings_clear/resolve、settings_provider_run_snapshot_get。
- 13 条全部对冻结 core_service 真实执行：**11 success + 2 typed 域错误**（PLUGIN_NOT_FOUND/TARGET_NOT_FOUND，证明 handler 在跑）；每条请求行（minor 可见）入证据。
- 版本坑按证据落地：P15=minor 7、DELETE=minor 10、CREATE=minor 8；错误 minor 被 INVALID_REQUEST 拒（独立探针）。
- 参数边界 15 个非法用例全 INVALID_ARGUMENTS 且 **0 Core 帧**；delete 兼容旧壳 payload:{...} 与内联两种调用。
- parity：xtract-command-surface.py --check PASS 零漂移；契约 **33/33 → 46 IMPLEMENTED / 20 NOT_SUPPORTED**（13 条 changed，coverage 100）。
- 回归：DSH 复跑 scripts/test.ps1 见执行记录（实现方报 161/161：44/42/75）；vitest 60/567；pytest 3F/2746P/9S 无新增。
- AC5：check.ps1 -TaskPath PASS；13 条 64-hex pin；Handoff + Record Decision（minor/参数边界策略）。
- 遗留（记录不阻塞）：剩余 20 条 NS（medium 11 + 其它 Task 9）；Avalonia 设置页 UI 入口未接（后续 UI Task）；minor 硬编码随 Core 升级需重跑 probe-b1.py。
- 集成：6b47f377f。
