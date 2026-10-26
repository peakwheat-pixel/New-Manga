---
id: HOST-COMMAND-MIGRATION-1
title: S2 命令迁移——生产命令面 parity 快照 + 6 个 domain service + 双 sidecar 覆盖
kind: implementation
governance_version: 3
status: done
approval: user_authorized_2026-10-26_ad002_autonomy
suggested_owner: antigravity
owner: avalonia-spike
reviewer: dsh
depends_on: [HOST-CORECLIENT-1]
base_commit: 45841d218
branch: task/HOST-COMMAND-MIGRATION-1
worktree: G:/CODEX/New Manga.workspace/worktrees/HOST-COMMAND-MIGRATION-1
integration_commit: 5a11fa7d9
delivery_head: 4ffa9d77f9733bd31807c3f0e0d694810e4c2fa6
canonical_evidence_status: complete
resource_closeout_status: complete
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
| E10-trx-coreclient | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/test/results-coreclient.trx | 4ffa9d77f9733bd31807c3f0e0d694810e4c2fa6 | 60dd8b6776cd775e7a4ee481c3b9fafc380acc867bbb356298f2304fa23601c0 | CANONICAL |
| E11-trx-host | AC5 | verification/HOST-COMMAND-MIGRATION-1/test/results-host.trx | 4ffa9d77f9733bd31807c3f0e0d694810e4c2fa6 | 464cf5651842bfbb2f98a9042a4d6de10f778ed221747d5513aa4e40e15a1eef | CANONICAL |
| E12-trx-app | AC5 | verification/HOST-COMMAND-MIGRATION-1/test/results-app.trx | 4ffa9d77f9733bd31807c3f0e0d694810e4c2fa6 | 9ef2cf8bbfc53ac102fe49a4fe76ac3d57579842029808ac8484f19951430eeb | CANONICAL |
| E13-nofixture-log | AC5 | verification/HOST-COMMAND-MIGRATION-1/test/dotnet-test-Debug-no-fixture.log | 4ffa9d77f9733bd31807c3f0e0d694810e4c2fa6 | a416c5ba3d0eb417c1b3fac50603060b59d7afb51b981c7a48a0984c9ca85bbd | CANONICAL |
| E14-nofixture-summary | AC5 | verification/HOST-COMMAND-MIGRATION-1/test/no-fixture-summary.json | 4ffa9d77f9733bd31807c3f0e0d694810e4c2fa6 | 78e042c8e9d09aef9a5c25dc5dc889a5baefde406e8b7abb2b813beff7a948d4 | CANONICAL |
| E15-vitest | AC5 | verification/HOST-COMMAND-MIGRATION-1/test/vitest-baseline.log | 4ffa9d77f9733bd31807c3f0e0d694810e4c2fa6 | 4bcd34de60fa549aa9c9f3cd52ddecd743de9c8f99b682ad8a100b8f53ab36d6 | CANONICAL |
| E16-pytest | AC5 | verification/HOST-COMMAND-MIGRATION-1/test/pytest-baseline.log | 4ffa9d77f9733bd31807c3f0e0d694810e4c2fa6 | 35e819f11bb63923785824f36bac2ad70bf912a87f62a7e33ce171483bceb242 | CANONICAL |
| E17-build | AC5/AC6 | verification/HOST-COMMAND-MIGRATION-1/build/dotnet-build-Debug.log | 4ffa9d77f9733bd31807c3f0e0d694810e4c2fa6 | 859cf25f40689e63b597a03db7a251d1eaee7519c5cb40e1b00fd1c8d899939d | CANONICAL |
| E18-manifest | 全 AC | verification/HOST-COMMAND-MIGRATION-1/MANIFEST.json | 4ffa9d77f9733bd31807c3f0e0d694810e4c2fa6 | 0733ba7d2656d2be6000a1545821c02fdee22e5b8095e26284f05fdff395aa13 | CANONICAL |
| E19-wire-core | AC4 | verification/HOST-COMMAND-MIGRATION-1/wire/commands-chinese-core-service.ndjson | 4ffa9d77f9733bd31807c3f0e0d694810e4c2fa6 | edb61405db88f06f780d072b076d89b01c5fc7f15579314184d8b83cb32b4f17 | CANONICAL |
| E20-wire-bridge | AC4 | verification/HOST-COMMAND-MIGRATION-1/wire/commands-integration-host-bridge.ndjson | 4ffa9d77f9733bd31807c3f0e0d694810e4c2fa6 | b12fdaf0e1e65d18fceee3016d864c316a512ee41dbcf4a55fd674548960783c | CANONICAL |
| S1-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/diagnostics/missing-exe.json | 5a11fa7d9 | 4594512db61c9500844d52d13c3b289c0322cdfed7dc471e8f3a1eac425391dd | SOURCE_PIN |
| S2-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/diagnostics/request-timeout.json | 5a11fa7d9 | d92e4e444d02eda85d8f361a1d140e43d818429a18ea7c3244dc82df40d76269 | SOURCE_PIN |
| S3-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/diagnostics/spawn-failed.json | 5a11fa7d9 | d328eb1713bbede1e76649b4474c555dfbde7c72e00736d1828a2118afc6760b | SOURCE_PIN |
| S4-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/diagnostics/startup-timeout.json | 5a11fa7d9 | 95a65b02f59bd9d5259d3fe0f81839c99d6ba872c7461c0710eff8c9e2d4dbf7 | SOURCE_PIN |
| S5-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/host/runtime-chinese-roundtrip.json | 5a11fa7d9 | 344024d1ddb450ab1e3e32b328208c909b4405def1077f867f458e04c7151b28 | SOURCE_PIN |
| S6-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/host/runtime-missing-sidecar.json | 5a11fa7d9 | 294565828007d46dca8cba7ce0f2705cf89cb7e20f55d45e3dbb0c68420ae74e | SOURCE_PIN |
| S7-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/host/runtime-readonly.json | 5a11fa7d9 | 855710ca4f5b6c4e61e705f50c735781ec1b496fd93ff15bb35f8b5c8f954790 | SOURCE_PIN |
| S8-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/host/second-instance.json | 5a11fa7d9 | cf7c9d7b208fe832f7d181f1a71f70226f4f2f000f956001c4df47068392054a | SOURCE_PIN |
| S9-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/host-logs/runtime-legacy-running/core_service.stderr.log | 5a11fa7d9 | bb6be73dfec0c9ddcddc14c9718886794cd19c190faa3edce78d77aecd15a324 | SOURCE_PIN |
| S10-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/host-logs/runtime-legacy-running/host_bridge.stderr.log | 5a11fa7d9 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| S11-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/host-logs/runtime-legacy-running/host.log | 5a11fa7d9 | 7b7df0bd1d964c8206286f2aff5e373d0fd37fa6aa319744b266d82bb3534098 | SOURCE_PIN |
| S12-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/host-logs/runtime-legacy-running/wire/core-service.ndjson | 5a11fa7d9 | e6055fdd2cb93d879d71a0e28076221f63788f170fbf34b5ff54a15c814f080a | SOURCE_PIN |
| S13-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/host-logs/runtime-legacy-running/wire/host-bridge.ndjson | 5a11fa7d9 | c16e3c1b3cba00a341d8bdd7dbda6753cc6c09f1c170e0bc9850cdfbbf518455 | SOURCE_PIN |
| S14-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/host-logs/runtime-missing-sidecar/host.log | 5a11fa7d9 | 2c7f99c8095825cc9a2cd2390475bc6b98b11aedb2db94bedfafa0d64c37b606 | SOURCE_PIN |
| S15-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/host-logs/runtime-parity-roundtrip/core_service.stderr.log | 5a11fa7d9 | 8382c95c22dd0e88e76c3b067abfc901426989e7b880c92783b2b2e934b562e4 | SOURCE_PIN |
| S16-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/host-logs/runtime-parity-roundtrip/host_bridge.stderr.log | 5a11fa7d9 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| S17-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/host-logs/runtime-parity-roundtrip/host.log | 5a11fa7d9 | 5a1a795fcb1a68e61abbedf93ec1afbbe21f1cf1fa83317b4aefde3519017911 | SOURCE_PIN |
| S18-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/host-logs/runtime-parity-roundtrip/wire/core-service.ndjson | 5a11fa7d9 | 6a8d7d9118f59b1e3e5b0f33180f24607d840aa1e1c543f743e51863ca30bd37 | SOURCE_PIN |
| S19-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/host-logs/runtime-parity-roundtrip/wire/host-bridge.ndjson | 5a11fa7d9 | 777a1f7b0428f8006be071230dfe95a7645c97f768d1cc6b08e9b3d241b96f20 | SOURCE_PIN |
| S20-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/host-logs/runtime-readonly/core_service.stderr.log | 5a11fa7d9 | 71ac9684655db3bba4a724b76b9346938c0ebef53ec4eb352cb049efafae5103 | SOURCE_PIN |
| S21-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/host-logs/runtime-readonly/host_bridge.stderr.log | 5a11fa7d9 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| S22-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/host-logs/runtime-readonly/host.log | 5a11fa7d9 | 82e4075cfee1634d85ea6f98912d6dd048e3e8b9d45da06dba1cd1b9b54f48cb | SOURCE_PIN |
| S23-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/host-logs/runtime-readonly/wire/core-service.ndjson | 5a11fa7d9 | f5930f833306e19a77612638b8a6c379593e010a15902f43320a6f2cf23dc5e3 | SOURCE_PIN |
| S24-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/host-logs/runtime-readonly/wire/host-bridge.ndjson | 5a11fa7d9 | df6f523209022952a9f5f6d5cf8e927cc3816e89f35b7b3a2d09a7c78f482bf2 | SOURCE_PIN |
| S25-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/host-logs/runtime-second-instance/host.log | 5a11fa7d9 | 5672c1df112f8be19dc3107d5856016e011ca91b6d731bb0c1008dc0dce3621b | SOURCE_PIN |
| S26-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/legacy-shell/detected.json | 5a11fa7d9 | c299985daca0a101768e0d08e187773aa231b74c57f3d9a8e8ccdc1972273719 | SOURCE_PIN |
| S27-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/legacy-shell/runtime-readonly.json | 5a11fa7d9 | ef4301465315daf4a7edef6d70b66512fbcba9db5277c8cecc549fc59fdd468f | SOURCE_PIN |
| S28-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/logs/bridge-errors/host_bridge.stderr.log | 5a11fa7d9 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| S29-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/logs/bridge-lifecycle/host_bridge.stderr.log | 5a11fa7d9 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| S30-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/logs/bridge-wire/host_bridge.stderr.log | 5a11fa7d9 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| S31-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/logs/commands-chinese/core_service.stderr.log | 5a11fa7d9 | b3c72a70ee9fd7635600fd39dd4b58c78727b8b446dfd69974cc63ef8990361f | SOURCE_PIN |
| S32-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/logs/commands-chinese/host_bridge.stderr.log | 5a11fa7d9 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| S33-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/logs/commands-domains/core_service.stderr.log | 5a11fa7d9 | a78562375e86fcc85a9b80bfdec9f95734b1a78362da5f10b008f7944e065943 | SOURCE_PIN |
| S34-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/logs/commands-domains/host_bridge.stderr.log | 5a11fa7d9 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| S35-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/logs/commands-integration/core_service.stderr.log | 5a11fa7d9 | af57ea97378a9d98f57b336c94623e03e4061817f3871c874dfc6d71e39d0851 | SOURCE_PIN |
| S36-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/logs/commands-integration/host_bridge.stderr.log | 5a11fa7d9 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| S37-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/logs/commands-not-supported/core_service.stderr.log | 5a11fa7d9 | 79596e60680f479d5d7227a8725f5b4f58e63679952ac8267d2b6f87c3a1a680 | SOURCE_PIN |
| S38-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/logs/commands-not-supported/host_bridge.stderr.log | 5a11fa7d9 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| S39-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/logs/core-chinese/core_service.stderr.log | 5a11fa7d9 | e3321f6cfc63821a7bee55d0a2d33e1c5c8d6270dd3fd3c5a16a6be12c1b5951 | SOURCE_PIN |
| S40-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/logs/core-ping/core_service.stderr.log | 5a11fa7d9 | d605bb058794b1b3c91bb93097ae4c2306460e372aa6ed6567e35934ffe7576f | SOURCE_PIN |
| S41-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/logs/core-raw-utf8/core_service.stderr.log | 5a11fa7d9 | 8169f8194c6a4fa8b1c5af43285790b78402ef3a06a892f858dd5b1716d87c43 | SOURCE_PIN |
| S42-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/logs/core-wire-shape/core_service.stderr.log | 5a11fa7d9 | 449bdfbc61b0d1e0282165b46b8d1c2bed41d2ebfdf68d277ad32ab2dd39f436 | SOURCE_PIN |
| S43-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/logs/failure-request-timeout/fake.stderr.log | 5a11fa7d9 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| S44-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/logs/failure-startup-timeout/core_service.stderr.log | 5a11fa7d9 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| S45-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/wire/bridge-errors.ndjson | 5a11fa7d9 | 051e6a7ba70f30ed40a624039c87298004801818d21ea74c73550b427c97747c | SOURCE_PIN |
| S46-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/wire/bridge-lifecycle.ndjson | 5a11fa7d9 | 33837dc6f204fc7f5138e4156c65d62b5ca9ade47b891489da6ede66dd4e27b5 | SOURCE_PIN |
| S47-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/wire/bridge-wire.ndjson | 5a11fa7d9 | dffa1966f1097156d9a58163c8c6832ffc7110332f6e9ad6cae00ee47c7024f9 | SOURCE_PIN |
| S48-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/wire/commands-chinese-host-bridge.ndjson | 5a11fa7d9 | ec3fade901ce20425998475d0befa2a15f646b27321d923e4b3ab0812352aa65 | SOURCE_PIN |
| S49-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/wire/commands-domains-core-service.ndjson | 5a11fa7d9 | 4cfa5ffc4531a0ef9bd8df1630c498f4b1b6ccf742723deb94d35865918d3266 | SOURCE_PIN |
| S50-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/wire/commands-domains-host-bridge.ndjson | 5a11fa7d9 | e292edc642276f2beaafa9cf8d9a0a0210915b3a41ce8408b907e4bed9a6253d | SOURCE_PIN |
| S51-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/wire/commands-integration-core-service.ndjson | 5a11fa7d9 | d960788caa74852e8c5fce26555ca69151bb652917473fbea44d17f96c1fe7fc | SOURCE_PIN |
| S52-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/wire/commands-not-supported-core-service.ndjson | 5a11fa7d9 | 90f4bf19d585506b3e3eff7f83200d319807613abc1abc94e6990225ea149c79 | SOURCE_PIN |
| S53-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/wire/commands-not-supported-host-bridge.ndjson | 5a11fa7d9 | 306952fd009753ed54b61c97f43da1bf49be955994591d7b5404c425a57cc5df | SOURCE_PIN |
| S54-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/wire/core-chinese-roundtrip.json | 5a11fa7d9 | 8113d041846ab195584f1ab8d52de14fec468f6ed57ce31bafd4998104bdcddf | SOURCE_PIN |
| S55-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/wire/core-chinese.ndjson | 5a11fa7d9 | 4087c0e4c7fcfd7f76da250140c0196a395023f6af225c7eb44df0c21e6b31f7 | SOURCE_PIN |
| S56-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/wire/core-ping.json | 5a11fa7d9 | 3e0f18892a8869a4ca5d2db7594f295c02a0bd7e0625e5baef8c9d6fd9616e11 | SOURCE_PIN |
| S57-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/wire/core-ping.ndjson | 5a11fa7d9 | 727f9263d28c8c1fcef7db20ff12ddab381add909dcc063e4e71cf5ef1e5d7a8 | SOURCE_PIN |
| S58-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/wire/core-raw-utf8-negative.json | 5a11fa7d9 | 611962501be106ce97c22a0c6cc3ac7c157d7c691c1378eb44b25834d64ca084 | SOURCE_PIN |
| S59-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/wire/core-raw-utf8.ndjson | 5a11fa7d9 | d0e975ccaf2d3bd686bf2db25149d66bd5309d5d38c7ab10720362420b81cbf7 | SOURCE_PIN |
| S60-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/wire/core-wire-shape.json | 5a11fa7d9 | 92ca695a77d5a47c10249c0137095da24d6f49f0d2ce00ef634c06ebaf9d5fd8 | SOURCE_PIN |
| S61-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/wire/core-wire-shape.ndjson | 5a11fa7d9 | 618e1e397a48d453106948339e64b5e952df17fe8f5c406415ac6b9d4deae423 | SOURCE_PIN |
| S62-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/wire/host-bridge-errors.json | 5a11fa7d9 | cfbd8e466399167855d037a1f852d90ec885d6272923a934976a8fbbd2faa770 | SOURCE_PIN |
| S63-src | AC2/AC5 | verification/HOST-COMMAND-MIGRATION-1/wire/host-bridge-lifecycle.json | 5a11fa7d9 | 850e8940f9b80f14911f66050b35b262eccb6989d2a9bb35a61104bd60f46045 | SOURCE_PIN |
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
## Review（DSH 集成复核，2026-10-27）— PASS（附范围裁决）

- 单命令验收：scripts/test.ps1 → **66/66 passed / 0 skipped**；裸跑 50 passed/16 skipped 均有原因。
- parity：快照 66 条 100% 有归属（16 实现 + 50 显式 NOT_SUPPORTED 带逐条原因）；实现项 16/16 对冻结 sidecar 真实执行通过；中文往返与 5c75 转义证据有效；--check 防漂移。
- 口径纠偏：命令面以**运行时 PRODUCTION_COMMANDS（66）**为准，任务卡内 36/14/7/4/2/1 的指示性求和（64）作废，已记入 Handoff。
- **范围裁决（DSH）**：S2 以"快照 100% 归属 + 16 条真实接线"收口，50 条 NS 按类分批进 S3/S4（settings/plugins/backup/cleanup → region/reader 写 → Run/Export）；S3 任务卡必须为书架/设置页所需命令列出 NS 清单并逐批接线。
- 集成：5a11fa7d9；范围仅 pps/desktop-avalonia/** + 证据 + 文档；未改旧壳/Python Core。
