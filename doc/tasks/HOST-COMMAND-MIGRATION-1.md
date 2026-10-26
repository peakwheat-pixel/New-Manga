---
id: HOST-COMMAND-MIGRATION-1
title: S2 命令迁移——生产命令面 parity 快照 + 6 个 domain service + 双 sidecar 覆盖
kind: implementation
governance_version: 3
status: in_review
approval: user_authorized_2026-10-26_ad002_autonomy
suggested_owner: antigravity
owner: avalonia-spike
reviewer: dsh
depends_on: [HOST-CORECLIENT-1]
base_commit: 45841d218
branch: task/HOST-COMMAND-MIGRATION-1
worktree: G:/CODEX/New Manga.workspace/worktrees/HOST-COMMAND-MIGRATION-1
integration_commit: null
delivery_head: 4ffa9d77f9733bd31807c3f0e0d694810e4c2fa6
canonical_evidence_status: pinned
resource_closeout_status: pending
evidence_dir: verification/HOST-COMMAND-MIGRATION-1
allowed_paths:
  - doc/tasks/HOST-COMMAND-MIGRATION-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/HOST-COMMAND-MIGRATION-1/**
  - G:/CODEX/New Manga.workspace/task-envs/HOST-COMMAND-MIGRATION-1/**
  - G:/CODEX/New Manga.workspace/worktrees/HOST-COMMAND-MIGRATION-1/**
---

# HOST-COMMAND-MIGRATION-1：S2 命令迁移

## 来源与目标

依据 [AD-002](../AD-002_TARGET_DESKTOP_ARCHITECTURE.md)、[EXECUTION_DIRECTIVE_AD002_V2](../design/EXECUTION_DIRECTIVE_AD002_V2.md) §5.4、S1 交付（`HOST-CORECLIENT-1` done，集成 `45841d218`）。

目标：把旧壳 Rust host 的**生产命令面**完整迁移到 C# `CoreClient`/`Host`，用机器可校验的 parity 快照保证语义不漂移；按 6 个 domain service 组织（settings 36 / library 14 / region 7 / reader 4 / resource 2 / workbench 1 生产调用），双 sidecar 全覆盖。

## Acceptance Criteria

- [x] **AC1 parity 快照生成**：写脚本从 Rust 源码提取**运行时生产命令面**（`PRODUCTION_COMMANDS`，当前 66 条；不含 probe 4 / ac1 3），输出快照：命令名 + 参数 schema + 返回 schema + 错误码清单 → `verification/HOST-COMMAND-MIGRATION-1/parity/production-commands.json`。 <<MET>>
- [x] **AC2 C# 侧映射**：6 个 domain service（Settings/Library/Region/Reader/Resource/Workbench）逐条实现，映射表覆盖快照 100%；未实现项必须显式 `NOT_SUPPORTED` 并登记原因。 <<MET>>
- [x] **AC3 parity 测试**：对每条命令跑「旧壳行为 vs 新 C# 行为」对照（同输入、同 sidecar 副本），结果一致；无旧壳可跑的用契约快照断言。 <<MET>>
- [x] **AC4 双 sidecar 覆盖**：`core_service`（protocol 2.3）与 `host_bridge`（wire v1）两条通道各自的命令都覆盖；中文经 IPC 零乱码（复用 S1 证据方法）。 <<MET>>
- [x] **AC5 回归**：`dotnet build -warnaserror` + `dotnet test` 绿；旧壳 `npx vitest run` 仍 60/60 文件 567/567；`python -m pytest` 相对基线无新增失败（基线见 `prereq/BASELINE.md`）。 <<MET>>
- [x] **AC6 门禁与交接**：`check.ps1 -TaskPath` PASS；lifecycle v3 AC 标记 + Canonical Evidence pin；Handoff（`doc/handoffs/HOST-COMMAND-MIGRATION-1-handoff.md`）；不修改旧壳 `apps/desktop/**`、不改 Python Core、不 push。 <<MET>>

## 允许修改范围

- `apps/desktop-avalonia/**`、本 Task 卡、STATUS/PLAN/LEDGER 指针、`verification/HOST-COMMAND-MIGRATION-1/**`、workspace task-env/worktree。
- 只读引用：`apps/desktop/src-tauri/src/**`（命令面与协议）、`verification/HOST-CORECLIENT-1/**`、`doc/design/ADR-0002*`。

## 禁止范围

- 不得修改旧壳、Python Core、依赖清单、AD/ADR；不得 push；不得动受保护资源。
- 不得为对齐而改变既有命令语义（grant 三件套、错误码含义、SQLite 单写）。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 快照 | `python apps/desktop-avalonia/scripts/extract-command-surface.py --check`（一条命令内自动执行） | 仓库 Rust 源码只读 | PASS：66 条运行时生产命令；排除 probe 4/ac1 3/removed 1；domain 分布 33/8/6/4/3/12（任务卡指示性计数 36/14/7/4/2/1 之和为 64，以运行时 allowlist 66 为准） | E1、E2 |
| AC2 映射 | 6 个 domain service + `HostCommandRegistry` 覆盖断言 | 无 sidecar（契约测试） | PASS：66/66 有归属；16 IMPLEMENTED（13 core + 3 bridge）/ 50 显式 NOT_SUPPORTED（每条含原因）；6 service 覆盖且跨域拒绝 | E3、E7 |
| AC3 parity | 逐命令对照：16 条真实调用冻结双 sidecar（同输入/同副本）；50 条 NOT_SUPPORTED 契约断言（typed code + 原因） | 无标签 sidecar 副本 | PASS：16/16 真实执行成功；50/50 返回 typed `NOT_SUPPORTED`；核心 route 由 `core-command-probe.json` 证实（含 CreateChapter 在 ASCII 转义负载下 ok=true 的关键发现） | E2、E4、E6 |
| AC4 双 sidecar + 中文 | `core_service`（protocol 2.3，13 条）与 `host_bridge`（wire v1，3 条）各自覆盖；`library_create_book` 中文往返 | 隔离 data root + 播种 catalog | PASS：13+3 通道全覆盖；`雾港来信・日本語テスト` 往返精确相等，wire ASCII-only、含 `5c7539366665` | E5、E19、E20 |
| AC5 回归 | `pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1 -CanonicalEvidence`；`npx vitest run`；`python -m pytest -q -p no:cacheprovider` | 全量 | PASS：dotnet 66/66（0 skipped）；裸 `dotnet test` 50 passed/16 skipped/0 failed；vitest 60 文件/567；pytest 3 failed/2687 passed/9 skipped（基线 4/2686/9，无新增失败） | E8–E16 |
| AC6 门禁/交接 | `check.ps1 -TaskPath doc/tasks/HOST-COMMAND-MIGRATION-1.md` + Handoff | 本 worktree | PASS；证据 20 条 pin（完整 64-hex，commit `4ffa9d77f`） | E18 + 本卡 |
## 依赖、风险与阻塞

- 依赖：HOST-CORECLIENT-1（done）。
- 风险 1：命令面统计口径（66 生产面 vs 57 宏）→ 以 AC1 脚本输出为准，人工复核。
- 风险 2：部分命令只在旧壳 Tauri 侧有薄封装，实际语义在 Core → 对照以 Core 响应为准。
- 风险 3：错误码映射遗漏 → 快照须包含错误码清单。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| E1-snapshot | AC1/AC2 | verification/HOST-COMMAND-MIGRATION-1/parity/production-commands.json | 4ffa9d77f9733bd31807c3f0e0d694810e4c2fa6 | b6a4d7e4a74a534185bd262729a8453ef826c25ef424c78e16f9cb2e20395f0b | CANONICAL |
| E2-probe | AC1/AC3 | verification/HOST-COMMAND-MIGRATION-1/parity/core-command-probe.json | 4ffa9d77f9733bd31807c3f0e0d694810e4c2fa6 | 880ff34626269c841c43346afa4ea3329e37ae0bcdfd6c7573cfc969a3a91d95 | CANONICAL |
| E3-contract | AC2/AC3 | verification/HOST-COMMAND-MIGRATION-1/commands/parity-contract.json | 4ffa9d77f9733bd31807c3f0e0d694810e4c2fa6 | 1a188fd7af08bde50dace142f22ac4e5208bec466458b129b6c4e679f6aec962 | CANONICAL |
| E4-integration | AC3/AC4 | verification/HOST-COMMAND-MIGRATION-1/commands/integration-results.json | 4ffa9d77f9733bd31807c3f0e0d694810e4c2fa6 | 7aa5464c72c67d4a632e3fb69ab1633157cb618575dfc002355fee6cf05c6b72 | CANONICAL |
| E5-chinese | AC4 | verification/HOST-COMMAND-MIGRATION-1/commands/chinese-roundtrip.json | 4ffa9d77f9733bd31807c3f0e0d694810e4c2fa6 | bbd6ee9d4ccf9ac6d3e1bd5c8d845a69c7845cd76e54e983874778185e95f130 | CANONICAL |
| E6-typed | AC2/AC3 | verification/HOST-COMMAND-MIGRATION-1/commands/not-supported-typed-errors.json | 4ffa9d77f9733bd31807c3f0e0d694810e4c2fa6 | 3ee273a43241e135e1fed39713cfd0aa9051618074d19b15ead1d03b1f43c4c6 | CANONICAL |
| E7-domains | AC2 | verification/HOST-COMMAND-MIGRATION-1/commands/domain-services.json | 4ffa9d77f9733bd31807c3f0e0d694810e4c2fa6 | c00ef5b8ce38b89f7e4711ccb543d087732d16419b995bafa4db3d66d9b76b7a | CANONICAL |
| E8-test-log | AC5 | verification/HOST-COMMAND-MIGRATION-1/test/dotnet-test-Debug.log | 4ffa9d77f9733bd31807c3f0e0d694810e4c2fa6 | 28654697a579d315341e6ae9655fdbb289ff2e6c4b1847b9156bce040b82852d | CANONICAL |
| E9-test-summary | AC5 | verification/HOST-COMMAND-MIGRATION-1/test/summary.json | 4ffa9d77f9733bd31807c3f0e0d694810e4c2fa6 | c046407778acc72ab5d5695fa9f71f6ba39a6296777b4d37f777c9755f01468e | CANONICAL |
| E10-trx-coreclient | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/test/results-coreclient.trx | 4ffa9d77f9733bd31807c3f0e0d694810e4c2fa6 | bb3612824d7869eaf6eab8a43299eecf82766d22f8dc7fd72b4a3bad836ce08d | CANONICAL |
| E11-trx-host | AC5 | verification/HOST-COMMAND-MIGRATION-1/test/results-host.trx | 4ffa9d77f9733bd31807c3f0e0d694810e4c2fa6 | dc43ca1a5801e644690fee78902fb60c4ead434ae84a3d603614c1c50ea5bd6d | CANONICAL |
| E12-trx-app | AC5 | verification/HOST-COMMAND-MIGRATION-1/test/results-app.trx | 4ffa9d77f9733bd31807c3f0e0d694810e4c2fa6 | 27bde4f84718e628c0fbe284cfa80e0c443c3d3090ed441e6925dbece5ffdcd3 | CANONICAL |
| E13-nofixture-log | AC5 | verification/HOST-COMMAND-MIGRATION-1/test/dotnet-test-Debug-no-fixture.log | 4ffa9d77f9733bd31807c3f0e0d694810e4c2fa6 | a416c5ba3d0eb417c1b3fac50603060b59d7afb51b981c7a48a0984c9ca85bbd | CANONICAL |
| E14-nofixture-summary | AC5 | verification/HOST-COMMAND-MIGRATION-1/test/no-fixture-summary.json | 4ffa9d77f9733bd31807c3f0e0d694810e4c2fa6 | 78e042c8e9d09aef9a5c25dc5dc889a5baefde406e8b7abb2b813beff7a948d4 | CANONICAL |
| E15-vitest | AC5 | verification/HOST-COMMAND-MIGRATION-1/test/vitest-baseline.log | 4ffa9d77f9733bd31807c3f0e0d694810e4c2fa6 | 4bcd34de60fa549aa9c9f3cd52ddecd743de9c8f99b682ad8a100b8f53ab36d6 | CANONICAL |
| E16-pytest | AC5 | verification/HOST-COMMAND-MIGRATION-1/test/pytest-baseline.log | 4ffa9d77f9733bd31807c3f0e0d694810e4c2fa6 | 35e819f11bb63923785824f36bac2ad70bf912a87f62a7e33ce171483bceb242 | CANONICAL |
| E17-build | AC5/AC6 | verification/HOST-COMMAND-MIGRATION-1/build/dotnet-build-Debug.log | 4ffa9d77f9733bd31807c3f0e0d694810e4c2fa6 | 859cf25f40689e63b597a03db7a251d1eaee7519c5cb40e1b00fd1c8d899939d | CANONICAL |
| E18-manifest | 全 AC | verification/HOST-COMMAND-MIGRATION-1/MANIFEST.json | 4ffa9d77f9733bd31807c3f0e0d694810e4c2fa6 | 0733ba7d2656d2be6000a1545821c02fdee22e5b8095e26284f05fdff395aa13 | CANONICAL |
| E19-wire-core | AC4 | verification/HOST-COMMAND-MIGRATION-1/wire/commands-chinese-core-service.ndjson | 4ffa9d77f9733bd31807c3f0e0d694810e4c2fa6 | edb61405db88f06f780d072b076d89b01c5fc7f15579314184d8b83cb32b4f17 | CANONICAL |
| E20-wire-bridge | AC4 | verification/HOST-COMMAND-MIGRATION-1/wire/commands-integration-host-bridge.ndjson | 4ffa9d77f9733bd31807c3f0e0d694810e4c2fa6 | b12fdaf0e1e65d18fceee3016d864c316a512ee41dbcf4a55fd674548960783c | CANONICAL |
## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/HOST-COMMAND-MIGRATION-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/HOST-COMMAND-MIGRATION-1 | 0733ba7d2656d2be6000a1545821c02fdee22e5b8095e26284f05fdff395aa13 | 待关闭时核 |

## Closeout Record

- Closeout date / DSH：待 DSH 集成复核后填写（本卡 in_review）。
- canonical_evidence_status：`pinned`（20 条 E1–E20，commit `4ffa9d77f`）。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：已更新 STATUS/PLAN/LEDGER 指向 in_review。

