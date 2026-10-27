---
id: NS-WIRE-B2
title: 剩余 NOT_SUPPORTED 命令接线（以 registry 实际 11 条为准）
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-27_goal_auto_except_recommended
suggested_owner: ui-stack-research
owner: ui-stack-research
reviewer: dsh
depends_on: []
base_commit: 27b5a4005
branch: task/NS-WIRE-B2
worktree: G:/CODEX/New Manga.workspace/worktrees/NS-WIRE-B2
integration_commit: null
delivery_head: dc87a67b3c1aae0fbe75b8ee7377e1f2bac97a1e
canonical_evidence_status: complete
resource_closeout_status: pending
evidence_dir: verification/NS-WIRE-B2
allowed_paths:
  - doc/tasks/NS-WIRE-B2.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/NS-WIRE-B2/**
  - G:/CODEX/New Manga.workspace/task-envs/NS-WIRE-B2/**
  - G:/CODEX/New Manga.workspace/worktrees/NS-WIRE-B2/**
---

# NS-WIRE-B2：剩余 NOT_SUPPORTED 命令接线

> 交付状态：**ready-for-integration**（实现 + 证据 + Handoff 完成；待 DSH 复核/集成；Owner 不自审）。
> 分支 `task/NS-WIRE-B2`（基于释放 HEAD `15b9b0441`），实现提交 `dc87a67b3`。
> 未改 Python Core 语义 / 未改 Host 契约 / 未改旧壳 / 未 push。

## 背景

命令面已达 **55 IMPLEMENTED / 11 NOT_SUPPORTED**（NS-WIRE-A1/B1、RUN-EXPORT、S4、GRANT 合计）。NS-RECLASSIFY-1 已证明多数旧 NS 是 S2 探针错误；剩余 11 条需逐条核实后接线。本 Task 收尾这 11 条。

## Acceptance Criteria

- [x] **AC1 清单**：从 `HostCommandRegistry`（`CommandParityContractTests` 断言 notSupported=11）导出当前 11 条 NS 清单，逐条标注 Core 路由/参数/返回/Core 是否已支持（参考 `verification/NS-RECLASSIFY-1/reclassification.json`）。→ **MET**：11 条逐条入表（`verification/NS-WIRE-B2/REPORT.md` §1 + 机器可读 `commands/ns-b2-inventory.json`，字段=命令/域/旧壳参数/Core 路由/minor/Core 入参/Core 返回/支持判定/结论）。交叉证据：冻结 sidecar 的同一份探针里 `ListRegionRevisions`（旧壳大写名）→`UNKNOWN_COMMAND`、`list_region_revisions`（规范名）→`TARGET_NOT_FOUND`，复现「大小写/假 id」判定（`parity/core-command-probe.json`）。 <<MET>>
- [x] **AC2 接线（可执行）**：9 条接入 dispatcher/domain service，对冻结 sidecar **真实执行**断言；`list_region_revisions` 路由探针已 ok:true 优先接。→ **MET**：9 条 = backup_restore、settings_provider_profiles_create/update/delete、settings_provider_bindings_set、settings_network_profiles_test、settings_network_profile_resolve、library_delete_books_permanently、list_region_revisions。全部先经 registry（route+minor）再经 dispatcher（旧壳签名翻译+边界校验），在冻结 `core_service.exe`（AC11 无标签副本）上**真实执行并断言返回投影**，逐条留存 Core 请求行；`list_region_revisions` 另用 S4 region fixture 的真实 `region_id` 得到 `current_revision_no≥1` + `is_current` 条目。`settings_network_profiles_test` 的 `status=passed` 由 Core 真实跑 6 段诊断 + 127.0.0.1 上的假 `/models` 端点达成（无外网）。另有 17 个非法参数用例 → 全 `INVALID_ARGUMENTS` 且 **Core 帧零增量**。证据：`commands/ns-b2-integration.json`、`commands/ns-b2-list-region-revisions.json`、`commands/ns-b2-invalid-arguments.json`；测试 `CommandWiringB2Tests`（5 项）。 <<MET>>
- [x] **AC3 真缺口**：Core 无等价命令或需 grant/翻译链的如实标 BLOCKED 并写明原因；不得把验证不了的标 IMPLEMENTED。→ **MET**：`credential_put` / `credential_clear` 标 BLOCKED，原因具名到代码位置：Core 路由存在（`BindProfileCredential` / `ClearProfileCredential`，NS-RECLASSIFY 探针已执行），但旧壳是「Host 本地 Windows 凭据存储 + 交互式凭据输入」两段式（`apps/desktop/src-tauri/src/settings_bridge.rs:288-332` / `:334-350`），Avalonia Host 无凭据管理器端口；只接 Core 半段会把无法解密的 ref 写进 profile 或误报 `missing` 而留下孤儿凭据 → 语义倒退，故不接。registry 原因文案升级为 `BLOCKED（NS-WIRE-B2 AC3）…`，并有测试断言该前缀与「凭据」字样，防回退。 <<MET>>
- [x] **AC4 parity/回归**：`extract-command-surface.py --check` 零漂移；`scripts/test.ps1` 全绿（≥177）；vitest 60/567；pytest 无新增确定性失败。→ **MET**：extract `--check` **PASS**（66 命令，域分布 resource 3 / workbench 12 / library 8 / settings 33 / region 6 / reader 4）；`test.ps1` **182/182 passed, 0 skipped**（coreclient 61 / host 46 / app 75）；vitest **60 files / 567 tests**；pytest **3F / 2764P / 9S**，失败集合与仓库既有基线（`verification/BOOK-FIXTURE-1/pytest.log` 等 10 份历史日志）**逐名一致**、0 新增（本 Task 未改任何 Python 文件）。parity：**55/11 → 64/2**，coverage 100%（66/66 有 owner）；计数断言在 3 个既有测试中同步，且新增「残留 NS 恰为 credential pair」集合断言。证据：`test/summary.json`、`test/dotnet-test-Debug.log`、`test/vitest.log`、`test/pytest.log`、`test/test.ps1.log`、`commands/parity-contract.json`。 <<MET>>
- [x] **AC5 门禁**：`check.ps1 -TaskPath` PASS；64-hex pin；Handoff + Record Decision。→ **MET**：`pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/NS-WIRE-B2.md` **PASS (3 warnings)**，3 条 warning 均为仓库既有预算/非终态提示；**12 条 64-hex pin**（见下表，并在 `core.autocrlf=true` 的新检出目录逐条复算 **0 mismatch**）；Handoff + Record Decision 见下文。为使 pin 可复现，`verification/NS-WIRE-B2/.gitattributes` 声明 `* -text`（字节精确存储，Git 不再改写行尾）。 <<MET>>

## Record Decision（摘要）

| 项 | 决定 |
|---|---|
| 批次范围 | 只接 registry 当前 11 条 NS；不碰 TRANSLATE/RACE 范围、不改 Core/Host 契约/旧壳 |
| 路由/minor | 沿用 NS-RECLASSIFY 成功探测：`backup.restore`、`list_region_revisions` = minor 3；六个 P15 settings 面 = minor 7；`PermanentlyDeleteBooks` = minor 10 |
| payload 翻译 | 以旧壳 Tauri 签名（`main.rs` / `settings_bridge.rs`）为准显式构造；必填缺失/类型错 → `INVALID_ARGUMENTS`（零 Core 帧）；可选参数仅在存在时发送；`network_profile_id` 保留显式 null；batch delete 兼容旧壳 `payload:{...}` 与内联两种形态 |
| 验证口径 | 真实请求冻结 core_service；**成功投影**才算实证；`INVALID_REQUEST` / `UNKNOWN_COMMAND` 不算实现；凭据对因 Host 端口缺失标 BLOCKED，不伪造、不标 IMPLEMENTED |
| 凭据对处置 | 保持 NOT_SUPPORTED + 具名 BLOCKED；解除条件=Host 凭据管理器端口（Windows Credential Manager/DPAPI + 交互式输入）移植后，把 `BindProfileCredential`/`ClearProfileCredential` 两段式补齐 |
| 与其它 Task 边界 | registry 冲突按「先落地者为准、后落地者 rebase」（与 NS-WIRE-B1 同规则） |

## 实现摘要（全部 `apps/desktop-avalonia/**`）

- `src/NewManga.CoreClient/Commands/HostCommandRegistry.cs`：9 条 `CoreBindings`；删除已失效的 `CoreRoute` 字典（唯一条目 `list_region_revisions` 已接线），新增 `BlockedReasons`（仅 2 条凭据命令）。
- `src/NewManga.CoreClient/Commands/HostCommandDispatcher.cs`：9 条 payload 翻译与边界校验；新增 batch delete 的严格键集校验（`book_ids`/`confirmed_book_ids`/`confirm_count`/`confirm_permanent_delete`）。
- `tests/NewManga.CoreClient.Tests/Commands/CommandWiringB2Tests.cs`（新，5 项）：registry/路由/minor + BLOCKED 原因断言；AC1 清单落盘；9 条真实执行（含请求行）；region fixture 真实 revision 历史；17 个非法参数零帧增量。
- `CommandParityContractTests.cs` / `CommandIntegrationTests.cs` / `CommandWiringB1Tests.cs`：实现计数与残留集合断言同步为 64/2。

## Canonical Evidence

> 计算环境：本工作树 `core.autocrlf=true`；`verification/NS-WIRE-B2/.gitattributes` 已声明 `* -text`，因此下列 sha256 在**任意 fresh checkout** 上字节一致（已在 `git worktree add --detach` 的新检出中逐条复算，0 mismatch）。

| evidence_id | AC/Gate | path（仓库相对路径） | commit | sha256 | class |
|---|---|---|---|---|---|
| B2-REPORT | AC1/AC2/AC3/AC5 | verification/NS-WIRE-B2/REPORT.md | dc87a67b3c1aae0fbe75b8ee7377e1f2bac97a1e | d578e3b1b8de28db69ee8f7083cd29ff602a411d4c5eacb75d5cbd11ff990dfe | CANONICAL |
| B2-INVENTORY | AC1 | verification/NS-WIRE-B2/commands/ns-b2-inventory.json | dc87a67b3c1aae0fbe75b8ee7377e1f2bac97a1e | b90cc3de98cdaeecbed08c120a8d82fd74e4f218f64854f9594248ea8e65c90c | CANONICAL |
| B2-INTEGRATION | AC1/AC2 | verification/NS-WIRE-B2/commands/ns-b2-integration.json | dc87a67b3c1aae0fbe75b8ee7377e1f2bac97a1e | 323b9af47947d72537dfd6a1206170cd075f1077ba6a57c04f33b9f032d007ff | CANONICAL |
| B2-REGION-REVISIONS | AC1/AC2 | verification/NS-WIRE-B2/commands/ns-b2-list-region-revisions.json | dc87a67b3c1aae0fbe75b8ee7377e1f2bac97a1e | 613c8a3cb9732d8fa2e8227224ca7b818e8a3016b95130d01aa4c5955ae8d07a | CANONICAL |
| B2-INVALID-ARGS | AC2 | verification/NS-WIRE-B2/commands/ns-b2-invalid-arguments.json | dc87a67b3c1aae0fbe75b8ee7377e1f2bac97a1e | 0a1956adc8161c14aa16b45d1d59bc3fd7453c5bd9ca3c82ea75f4eb0e0374cc | CANONICAL |
| B2-PARITY-CONTRACT | AC3/AC4 | verification/NS-WIRE-B2/commands/parity-contract.json | dc87a67b3c1aae0fbe75b8ee7377e1f2bac97a1e | 790481dd3eabcf749d1c586935dd19750745a45576e432b145b06b5e1a9e6ce2 | CANONICAL |
| B2-CORE-PROBE | AC1/AC4 | verification/NS-WIRE-B2/parity/core-command-probe.json | dc87a67b3c1aae0fbe75b8ee7377e1f2bac97a1e | b2952f05b15f887ad827f2bd1065bdab6492041d8500891107fa1e0dbe8a13d4 | CANONICAL |
| B2-TEST-SUMMARY | AC4 | verification/NS-WIRE-B2/test/summary.json | dc87a67b3c1aae0fbe75b8ee7377e1f2bac97a1e | c095b44cfe7a31748c8d45de074f0a85b9e988ab8623064fa4cf94c87ce01d19 | CANONICAL |
| B2-TEST-DOTNET-LOG | AC4 | verification/NS-WIRE-B2/test/dotnet-test-Debug.log | dc87a67b3c1aae0fbe75b8ee7377e1f2bac97a1e | 32f5d58b38d7e34e38b67e0191f2cc2d8752b2970b7f6e810c210bbcbfb31611 | CANONICAL |
| B2-TEST-PS1-LOG | AC4 | verification/NS-WIRE-B2/test/test.ps1.log | dc87a67b3c1aae0fbe75b8ee7377e1f2bac97a1e | 090834ad7afbc2a80595d76eddc3b95e211b0b1f5e8363834510fb016e15a54d | CANONICAL |
| B2-VITEST | AC4 | verification/NS-WIRE-B2/test/vitest.log | dc87a67b3c1aae0fbe75b8ee7377e1f2bac97a1e | c6a4365a1972f60ef56a5d67c7b39373c58e8e1efea3deaf54157a6b4771c7ef | CANONICAL |
| B2-PYTEST | AC4 | verification/NS-WIRE-B2/test/pytest.log | dc87a67b3c1aae0fbe75b8ee7377e1f2bac97a1e | 61bcd4d2af7c70e2cb1622e848f2516ba78fb64d95d9caf059940debfbb33a8c | CANONICAL |
| B2-EOL-ATTR | AC5 | verification/NS-WIRE-B2/.gitattributes | dc87a67b3c1aae0fbe75b8ee7377e1f2bac97a1e | b38afb028c424f88b0b4269b58acade65a92dcea8a658798a439c350b9e17b13 | SOURCE_PIN |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/NS-WIRE-B2 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/NS-WIRE-B2 | `evidence/`（test/commands/parity）+ `test-ps1.log` + `pins.txt` | 2026-10-27 收口时目录存在；pin 表引用其来源（已复制入仓库 `verification/NS-WIRE-B2/`）；未移动/未删除；关闭时由 DSH 复核 |
| worktree | G:/CODEX/New Manga.workspace/worktrees/NS-WIRE-B2 | PRESERVE_REFERENCED | 同左 | 分支 `task/NS-WIRE-B2` @ dc87a67b3 | 检出后交付；未 gc/prune；临时校验检出已用 `git worktree remove` 单独清理（非 prune） |

## Closeout Record

- Closeout date / DSH：待关闭时填写（owner 交付 `dc87a67b3`，待 DSH 集成验证与独立 Review）。
- canonical_evidence_status：`complete`（12 条 CANONICAL pin，指向 `dc87a67b3`）。
- resource_closeout_status：`pending`（task-env/worktree 保留引用，未清理）。
- 删除、迁移、归档数量/字节数：0（真实删除测试只在临时数据根内创建并删除测试书/备份）。
- 未关闭项及保留原因：`credential_put`/`credential_clear` BLOCKED（Host 凭据管理器端口缺失）；9 条新命令尚未接 UI 入口（本 Task 只做命令面）；`settings_network_profiles_test` 的真实公网可用性属产品验收；minor 仍硬编码（P15=7/DELETE=10），Core 协议升级需重跑 `probe-core-commands.ps1`；需独立 Review（owner ≠ reviewer）。
- 当前指针清理：本卡为唯一交付指针；`doc/STATUS.md` / `doc/REBASELINE_PLAN.md` / `doc/TASK_LEDGER.md` 由 DSH 在集成时统一收口（本 Task 未改动，避免与 Lead 并发编辑冲突）。

## Handoff

- 交付：分支 `task/NS-WIRE-B2` @ `dc87a67b3`（实现 + 5 项新测试 + 证据 + 本卡）。
- 复核入口：`verification/NS-WIRE-B2/REPORT.md`（AC1 11 条逐条表 + AC2/AC3/AC4 明细）、`verification/NS-WIRE-B2/test/summary.json`、`verification/NS-WIRE-B2/commands/ns-b2-*.json`。
- 复核建议命令：`pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1 -EvidenceDirectory G:/CODEX/New Manga.workspace/task-envs/NS-WIRE-B2/evidence`（需 AC11 无标签 sidecar 副本；本次 182/182）。
- 明确未做（留给后续 Task）：
  1. **Host 凭据管理器端口**（Windows Credential Manager / DPAPI + 交互式凭据输入）→ 之后 `credential_put`/`credential_clear` 可按两段式接线；
  2. Avalonia 设置页/工作台 UI 对这些新命令的入口；
  3. `settings_network_profiles_test` 的真实网络验收（本次只证明命令面与 Core 诊断链可用）；
  4. 版本控制：Core 协议 minor 升级后需重跑 `scripts/probe-core-commands.ps1` 并复核 64/2 计数。
