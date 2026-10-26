---
task_id: HOST-COMMAND-MIGRATION-1
author: avalonia-spike
recipient: DeepSeek Harness
base_commit: 45841d218
delivery_head: 4ffa9d77f9733bd31807c3f0e0d694810e4c2fa6
status: draft
---

# Handoff：HOST-COMMAND-MIGRATION-1

## 交付结果

S2 命令迁移在 `apps/desktop-avalonia/`（分支 `task/HOST-COMMAND-MIGRATION-1`，worktree base `ab53cd39d`，交付 `4ffa9d77f`）：

- **AC1 快照**：`apps/desktop-avalonia/scripts/extract-command-surface.py` 从 Rust 源码提取运行时生产命令面 → `verification/HOST-COMMAND-MIGRATION-1/parity/production-commands.json`。66 条（排除 probe 4 / ac1 3 / removed 1），逐条含 handler 位置、参数（名+类型）、返回类型、错误类型与函数体内大写错误码；`--check` 可在一条命令中验证「源码 ↔ 提交快照」零漂移。
- **AC2 映射**：`NewManga.CoreClient/Commands/` 新增 `HostCommandRegistry` + `HostCommandDescriptor` + `HostCommandDispatcher` + 6 个 domain service（Settings 33 / Library 8 / Region 6 / Reader 4 / Resource 3 / Workbench 12 = 66）。**16 IMPLEMENTED / 50 NOT_SUPPORTED**；未实现项每条都有可读原因（host-local Rust 逻辑未移植，或 Core 路由尚未在冻结 Core 上可用）。
- **AC3/AC4 parity**：16 条已实现命令全部对冻结双 sidecar 真实执行（13 条 `core_service` protocol 2.3 + 3 条 `host_bridge` wire v1）；50 条 NOT_SUPPORTED 以 typed 错误契约断言；`core-command-probe.json` 记录每条 Core 路由的实测响应（含 CreateChapter 只有在负载 ASCII 转义后才成功的 cp936 陷阱证据）。中文 `雾港来信・日本語テスト` 经 dispatcher 往返精确一致，wire ASCII-only 并保留 `5c7539366665` 原始 hex。
- **AC5 回归**：一条命令 66/66 passed / 0 skipped；裸 `dotnet test`（无 fixture env）50 passed / 16 skipped / 0 failed（skip 全带原因）；旧壳 vitest 60 文件 / 567 用例不变；pytest 3 failed / 2687 passed / 9 skipped（基线 4 failed / 2686 passed / 9 skipped，无新增失败）。
- **AC6**：`check.ps1 -TaskPath` PASS；20 条证据 pin（完整 64-hex，commit `4ffa9d77f`）。未改旧壳 `apps/desktop/**`、未改 Python Core `src/**`、未 push。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 快照 | `python apps/desktop-avalonia/scripts/extract-command-surface.py --check` | Rust 源码只读，交付分支 | PASS 66/66 | `parity/production-commands.json`（E1） |
| AC2/AC3 契约 | `test.ps1`（内含 contract tests） | .NET 9/Avalonia 11.3.22 | PASS 66/66 有归属；16 implemented / 50 NOT_SUPPORTED | `commands/parity-contract.json`、`commands/domain-services.json` |
| AC3 逐命令执行 | `test.ps1` → `CommandIntegrationTests` | AC11 无标签 sidecar 副本 + 隔离 data root | PASS 16/16 真实执行；50/50 typed NOT_SUPPORTED | `commands/integration-results.json`、`commands/not-supported-typed-errors.json` |
| AC4 中文/wire | 同上 `library_create_book` 中文往返 | 同上 | PASS：UTF-8 精确相等；ASCII-only；`5c7539366665` | `commands/chinese-roundtrip.json`、`wire/commands-chinese-core-service.ndjson` |
| AC4 bridge 通道 | issue/revoke_ref/revoke_resource_refs + resolve 校验 | catalog_loader 播种 res-1 | PASS：resolve 字段齐全，撤销后 `REF_REVOKED` | `wire/commands-integration-host-bridge.ndjson` |
| AC5 dotnet | `pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1 -CanonicalEvidence` | 全量 | PASS 66 passed / 0 skipped | `test/summary.json`、`test/results-*.trx` |
| AC5 裸跑 | `scripts/test-without-fixture.ps1` | 清空 fixture env | PASS 50 passed / 16 skipped / 0 failed | `test/no-fixture-summary.json` |
| AC5 旧壳 | `npx vitest run`（`apps/desktop/frontend`） | 旧前端依赖 | PASS 60 文件 / 567 用例 | `test/vitest-baseline.log` |
| AC5 pytest | `python -m pytest -q -p no:cacheprovider`（仓库根） | Python 3.14.6，`PYTHONDONTWRITEBYTECODE=1` | 3 failed / 2687 passed / 9 skipped（基线 4/2686/9） | `test/pytest-baseline.log` |
| AC6 治理 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/HOST-COMMAND-MIGRATION-1.md` | 本 worktree | PASS | 本卡 Canonical Evidence |

## 接收方式

- 仓库 `G:/CODEX/New Manga`；分支 `task/HOST-COMMAND-MIGRATION-1`；worktree `G:/CODEX/New Manga.workspace/worktrees/HOST-COMMAND-MIGRATION-1`；worktree base `ab53cd39d`；交付 `4ffa9d77f`（`delivery_head`）。
- 一条命令复跑：`pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1`（默认把证据写 workspace `task-envs/HOST-COMMAND-MIGRATION-1/evidence-rerun`，不会覆盖本卡 pin；仅 Owner 用 `-CanonicalEvidence` 重生成仓内证据）。DSH 复核请用**不带** `-CanonicalEvidence` 的命令。
- 单独复跑：`python apps/desktop-avalonia/scripts/extract-command-surface.py --check`；`pwsh -NoProfile -File apps/desktop-avalonia/scripts/probe-core-commands.ps1`（需 AC11 无标签副本）。
- 前置：Windows 11；.NET SDK 9；Python 3.14（AC1 提取器）；`G:/CODEX/New Manga.workspace/task-envs/HOST-CORECLIENT-1/sidecar-copy` 无标签 sidecar 副本。
- 接收者应检查：E1–E20 pin 是否仍匹配；`apps/desktop/**` 与 `src/**` 无 diff；旧壳 vitest 仍 60/567；`git diff --stat 45841d218..4ffa9d77f` 只含允许路径。

## Record Decision

1. **parity 口径**：以运行时 `command_allowlist(false,false)`（`PRODUCTION_COMMANDS`）为唯一标准 = 66 条；`#[tauri::command]` 宏计数（57/57+）包含 probe/ac1/内部命令，不作 parity 依据。任务卡分组计数（settings 36 / library 14 / region 7 / reader 4 / resource 2 / workbench 1）之和为 64 且与运行时 66 不一致，本实现按显式 domain 表覆盖全部 66 条：**Settings 33 / Library 8 / Region 6 / Reader 4 / Resource 3 / Workbench 12**。
2. **已实现判定**：只有「冻结 sidecar 实测可执行且测试可稳定断言」的命令才标 IMPLEMENTED（16 条）。未达标命令一律显式 NOT_SUPPORTED + 原因，不允许静默缺失。探测中 CreateChapter 最初因未转义负载返回 `UNKNOWN`，改为 `\uXXXX` 后 ok=true，故纳入实现——这是 cp936 陷阱的又一实证。
3. **Core 路由映射（implemented，protocol 2.3）**：`core_ping→core.ping(3)`、`library_list_books→ListBooks(3)`、`library_list_recycle_bin_books→ListRecycleBinBooks(3)`、`library_create_book→CreateBook(8)`、`create_chapter→CreateChapter(8)`、`list_chapters→list_chapters(3)`、`list_chapter_pages→list_chapter_pages(3)`、`list_regions→list_regions(3)`、`settings_get→settings.get(3)`、`backup_list→backup.list(3)`、`plugins_list→plugins.list(3)`、`cleanup_preview→cleanup.preview(3)`、`library_get_export_history→GetExportHistory(3)`。
4. **bridge 映射（implemented，wire v1）**：`issue_resource_url(resource_id,revision) → issue`，返回 `{id,size}` 授权句柄（不暴露 OS 路径）；`revoke_ref(opaque_id) → revoke`，返回 `{revoked:true}`；`revoke_resource_refs(resource_id) → revoke_resource`，返回 `{revoked_count}`。resolve 仍是 Host 内部能力（production 面没有 resolve 命令），测试用 `HostBridgeClient.ResolveAsync` 验证句柄语义。
5. **NOT_SUPPORTED 两类原因**：a) Core 路由存在但 S2 探测未通过/未验证（`create` 类只对已证实命令开闸；region 写命令因假 ID 返回 `TARGET_NOT_FOUND/INVALID_REQUEST`，reader projection 负载语义未定）；b) host-local Rust 逻辑未移植（设置持久化、凭证、插件运行时、备份恢复、清理执行、文件选择器、导入/导出、Run 编排、永久删除），按 AD-002 在后续 Slice 移植。
6. **中文零乱码**：复用 S1 方法（`Utf8Encoding(false)` + 非 ASCII 全 `\uXXXX` + 原始 hex 捕获）；S1 的 57 条测试原样保留并随一条命令运行。

## 下一任务建议（必填）

- Task ID / 标题：建议 `HOST-LOCAL-MIGRATION-1`（S3：host-local 命令面分批移植——settings/credentials/plugins/backup/cleanup 优先）。**待 DSH 释放**，本 Handoff 不创建占位 Task。
- 推荐 Agent / Reviewer：ZCode / DSH + 未参与实现者独立复核。
- 推荐原因与前置依赖：50 条 NOT_SUPPORTED 已按类归因，S3 可按「设置→插件→备份/清理→region/reader 写→Run/Export」分批推进；前置本 Task 复核通过。
- Recovery point：仓库 `G:/CODEX/New Manga`，branch `task/HOST-COMMAND-MIGRATION-1`，worktree `G:/CODEX/New Manga.workspace/worktrees/HOST-COMMAND-MIGRATION-1`，base `ab53cd39d`，head `4ffa9d77f`。
- 允许修改路径：`apps/desktop-avalonia/**`、`doc/tasks|handoffs`、`doc/STATUS|REBASELINE_PLAN|TASK_LEDGER`、`verification/HOST-LOCAL-MIGRATION-1/**`、workspace task-env。
- 禁止范围：禁改 `apps/desktop/**` 与 `src/**`；禁 push；不改依赖/AD。
- 交付物：host-local 命令实现或 Core 补齐、逐命令 parity 测试、中文 IPC 证据。
- 验证命令/完成 Gate：`scripts/test.ps1` 全绿（含新增测试）、`check.ps1 -TaskPath` PASS、旧壳 vitest 60/567、pytest 无新增失败。
- 可直接转发给 Agent 的指令：见 DSH 释放的 S3 Task 卡；转发时附本 Handoff Record Decision 1–6 作为 parity 契约。

## 风险与遗留

- **50 条 NOT_SUPPORTED**：是显式契约，不是遗漏；其中 region/reader 写命令的 Core 路由已从 Rust 源码确认（`list_region_revisions`/`rerender_page`/`resolve_page_resource`/`restore_region_revision` 等在冻结 Core 上返回 `TARGET_NOT_FOUND`，说明命令存在、S2 未接）；reader projection 的负载语义（mode/start_position 枚举）未定，需 S3 用真实 chapter 验证。
- **任务卡分组计数**与运行时 66 不一致（64 vs 66），已在 Record Decision 说明并用实际分布替换，不改变 AC 判定（按命令）。
- **resource 通道返回形态**：新 Host 返回 `{id,size}` 句柄而非 Rust 的 URL 字符串，属 AD-002「UI 不接触 OS 路径」的有意差异；如需旧形封装，S3 可在 Host 层加 URL 投影。
- **pytest**：本次 3 failed（`test_detection_manga_real` ×2、`test_workbench_viewmodel::test_pause_shows_optimistic_feedback_immediately`）均在既有 Python Core 面，仓库 `src/**` 本次零改动；基线只记录计数（4/2686/9），本次 3/2687/9，无新增失败类别。
- 回退：删除 `apps/desktop-avalonia/src/NewManga.CoreClient/Commands/**`、`tests/.../Commands/**`、两个脚本与 `verification/HOST-COMMAND-MIGRATION-1/**` 即回到 S1 行为。
