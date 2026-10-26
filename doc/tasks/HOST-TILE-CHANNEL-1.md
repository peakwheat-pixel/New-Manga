---
id: HOST-TILE-CHANNEL-1
title: S5-A Host tile 通道 + per-tile SHA-256 + ≤1s 授权缓存 + containment
kind: implementation
governance_version: 3
status: done
approval: user_authorized_2026-10-26_ad002_autonomy
suggested_owner: antigravity
owner: avalonia-spike
reviewer: dsh
depends_on: [UI-WORKBENCH-READER-1]
base_commit: 2885861fa
branch: task/HOST-TILE-CHANNEL-1
worktree: G:/CODEX/New Manga.workspace/worktrees/HOST-TILE-CHANNEL-1
integration_commit: 09d7e76c1
delivery_head: c8ab135d10f0232d6717ff4471f7e568f099f613
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/HOST-TILE-CHANNEL-1
allowed_paths:
  - doc/tasks/HOST-TILE-CHANNEL-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/HOST-TILE-CHANNEL-1/**
  - G:/CODEX/New Manga.workspace/task-envs/HOST-TILE-CHANNEL-1/**
  - G:/CODEX/New Manga.workspace/worktrees/HOST-TILE-CHANNEL-1/**
---

# HOST-TILE-CHANNEL-1：S5-A tile 通道与最小安全面

## 来源

S5 拆分（见 `LEGACY-SHELL-REMOVAL-1` BLOCKED 段）、[ADR-0002](../design/ADR-0002_RESOURCE_CHANNEL_SECURITY_V2.md) D1–D4。目标：在新 C# Host 内实现 tile 资源通道与**最小**安全面，先覆盖 D4-2（revoke/expiry/1s 缓存失效）与 D4-4（篡改 tile 保尺寸拒绝），供 S5-B 做完整 D4 harness。

## Acceptance Criteria

- [x] **AC1 tile 通道**：Host 提供 `tile` 服务：issue（返回不透明句柄 + size + identity + per-tile digest 清单）→ read（按 tile 读，返回字节 + 校验）→ revoke；UI 不接触 OS 路径/digest。 <<MET>>
- [x] **AC2 授权缓存**：授权状态查询带 ≤1s TTL 缓存；revoke 必须能**打断缓存**（事件驱动失效）；expiry 生效。 <<MET>>
- [x] **AC3 containment**：从已打开句柄重导最终路径并校验在允许根内；越界/junction/reparse 拒绝（为 S5-B 提供基础，测试覆盖最小集）。 <<MET>>
- [x] **AC4 内容完整性**：per-tile SHA-256 校验；**等长原地重写必拒**；篡改 tile 保尺寸 → 拒绝（typed error）。 <<MET>>
- [x] **AC5 接线与回归**：阅读器/工作台改用 tile 通道（可保留旧 fixture 兜底开关）；`scripts/test.ps1` 全绿；旧壳 vitest 60/567、pytest 基线不变。 <<MET>>
- [x] **AC6 门禁**：`check.ps1 -TaskPath` PASS；证据 64-hex pin；Handoff + Record Decision（缓存失效语义、digest 计算时机、误差边界）。 <<MET>>

## 允许修改范围

`apps/desktop-avalonia/**`、本卡、STATUS/PLAN/LEDGER 指针、`verification/HOST-TILE-CHANNEL-1/**`、workspace。只读：ADR-0002、S2/S3/S4 Handoff、旧 Rust `resource_protocol.rs`（只读参考）。

## 禁止范围

不得改动/删除旧壳 `apps/desktop/**`（S5-C 才归档）；不改 Python Core；不 push；不 gc/prune；不得跳过 digest 校验。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1/AC2 | issue→read→revoke + 缓存打断 ≤1s | 无标签副本 | NOT_RUN | 待填 |
| AC3 | 越界/junction/reparse 负例 | 同上 | NOT_RUN | 待填 |
| AC4 | 等长重写/篡改保尺寸负例 | 同上 | NOT_RUN | 待填 |
| AC5/AC6 | `scripts/test.ps1` + check.ps1 | 全量 | NOT_RUN | 待填 |

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| E1-issue-read-revoke | AC1 | verification/HOST-TILE-CHANNEL-1/security/issue-read-revoke.json | c8ab135d10f0232d6717ff4471f7e568f099f613 | 79b3fe4f03a133f2d4e80b4ec2d801d2315d0ccabffd99ddf95f040f4dfc12b4 | CANONICAL |
| E2-cache-revoke | AC2 | verification/HOST-TILE-CHANNEL-1/security/cache-revoke.json | c8ab135d10f0232d6717ff4471f7e568f099f613 | ed698acbd558105ffae35e61ea6a5afeb61834ed4d81b09fe4a078aec7ff85d2 | CANONICAL |
| E3-expiry | AC2 | verification/HOST-TILE-CHANNEL-1/security/expiry.json | c8ab135d10f0232d6717ff4471f7e568f099f613 | 90515e49f26cdef3c634c5d7242a4c9a0c0c90a5de007e4bbad16ec21bdb9f07 | CANONICAL |
| E4-containment | AC3 | verification/HOST-TILE-CHANNEL-1/security/containment.json | c8ab135d10f0232d6717ff4471f7e568f099f613 | 5aebde7aec847deb4eb8f4e7626bf6efd262b9fc59a9ca198ffd3689e83279f9 | CANONICAL |
| E5-equal-length-rewrite | AC4 | verification/HOST-TILE-CHANNEL-1/security/equal-length-rewrite.json | c8ab135d10f0232d6717ff4471f7e568f099f613 | a66ebed787579ffeb17da723c5e7b1f02b2eaf6026bdcf2fbb0409bf4495f6d9 | CANONICAL |
| E6-tampered-tile | AC4 | verification/HOST-TILE-CHANNEL-1/security/tampered-tile.json | c8ab135d10f0232d6717ff4471f7e568f099f613 | 90d59d30365d428e089fdae4cf836415239d8ba1e5cff5d37bc94e0c46c663e6 | CANONICAL |
| E7-identity-change | AC4 | verification/HOST-TILE-CHANNEL-1/security/identity-change.json | c8ab135d10f0232d6717ff4471f7e568f099f613 | f704845118f7bf16f5b7c4520a4038d1585e1b8208ee764466213f0e1cde6a05 | CANONICAL |
| E8-ui-reader | AC5 | verification/HOST-TILE-CHANNEL-1/security/reader-tile-channel.json | c8ab135d10f0232d6717ff4471f7e568f099f613 | ae94bfb0b9b96851e2149f2889c2085e94fe1c57ba9a7255ea7d804c60e8594e | CANONICAL |
| E9-ui-workbench | AC5 | verification/HOST-TILE-CHANNEL-1/security/workbench-tamper.json | c8ab135d10f0232d6717ff4471f7e568f099f613 | fd3baeb60e04d2848092a6c86eb3046b010fdfc6d091644c8f330a8c38c89c53 | CANONICAL |
| E10-perf | AC1/AC5 | verification/HOST-TILE-CHANNEL-1/performance/tile-read.json | c8ab135d10f0232d6717ff4471f7e568f099f613 | 4511c508d188cefb19be52aa287c866b7145ccbb48eed508cf5af9e41b962afe | CANONICAL |
| E11-manifest | 全 AC | verification/HOST-TILE-CHANNEL-1/MANIFEST.json | c8ab135d10f0232d6717ff4471f7e568f099f613 | d8f5cd008228e62884f3f4921e6383469163ec360a8d751ebf06c177eb6b11d1 | CANONICAL |
| T1-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/commands/chinese-roundtrip.json | 09d7e76c1 | bbd6ee9d4ccf9ac6d3e1bd5c8d845a69c7845cd76e54e983874778185e95f130 | SOURCE_PIN |
| T2-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/commands/domain-services.json | 09d7e76c1 | c00ef5b8ce38b89f7e4711ccb543d087732d16419b995bafa4db3d66d9b76b7a | SOURCE_PIN |
| T3-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/commands/integration-results.json | 09d7e76c1 | 7aa5464c72c67d4a632e3fb69ab1633157cb618575dfc002355fee6cf05c6b72 | SOURCE_PIN |
| T4-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/commands/not-supported-typed-errors.json | 09d7e76c1 | 3ee273a43241e135e1fed39713cfd0aa9051618074d19b15ead1d03b1f43c4c6 | SOURCE_PIN |
| T5-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/commands/parity-contract.json | 09d7e76c1 | 1a188fd7af08bde50dace142f22ac4e5208bec466458b129b6c4e679f6aec962 | SOURCE_PIN |
| T6-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/commands/wiring.json | 09d7e76c1 | 1b5a31590d0c993533d4912df6587689b15ed658631ce70e39badeae4f1bc1d8 | SOURCE_PIN |
| T7-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/diagnostics/missing-exe.json | 09d7e76c1 | 4594512db61c9500844d52d13c3b289c0322cdfed7dc471e8f3a1eac425391dd | SOURCE_PIN |
| T8-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/diagnostics/request-timeout.json | 09d7e76c1 | d92e4e444d02eda85d8f361a1d140e43d818429a18ea7c3244dc82df40d76269 | SOURCE_PIN |
| T9-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/diagnostics/spawn-failed.json | 09d7e76c1 | d328eb1713bbede1e76649b4474c555dfbde7c72e00736d1828a2118afc6760b | SOURCE_PIN |
| T10-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/diagnostics/startup-timeout.json | 09d7e76c1 | 95a65b02f59bd9d5259d3fe0f81839c99d6ba872c7461c0710eff8c9e2d4dbf7 | SOURCE_PIN |
| T11-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/host/runtime-chinese-roundtrip.json | 09d7e76c1 | 344024d1ddb450ab1e3e32b328208c909b4405def1077f867f458e04c7151b28 | SOURCE_PIN |
| T12-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/host/runtime-missing-sidecar.json | 09d7e76c1 | 294565828007d46dca8cba7ce0f2705cf89cb7e20f55d45e3dbb0c68420ae74e | SOURCE_PIN |
| T13-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/host/runtime-readonly.json | 09d7e76c1 | 855710ca4f5b6c4e61e705f50c735781ec1b496fd93ff15bb35f8b5c8f954790 | SOURCE_PIN |
| T14-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/host/second-instance.json | 09d7e76c1 | 289794b87aec7bd366044d484b8b672324d5681815ab16a1f0c5418772d25031 | SOURCE_PIN |
| T15-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/host-logs/runtime-legacy-running/core_service.stderr.log | 09d7e76c1 | ab47370e092cca34510557b0c807baf09de229548854a10d582a430a360214d8 | SOURCE_PIN |
| T16-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/host-logs/runtime-legacy-running/host_bridge.stderr.log | 09d7e76c1 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| T17-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/host-logs/runtime-legacy-running/host.log | 09d7e76c1 | adfc842824b84ef0ece28868766cd271e61c90bbdd1ccef09c80a6bfaad66327 | SOURCE_PIN |
| T18-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/host-logs/runtime-legacy-running/wire/core-service.ndjson | 09d7e76c1 | e278642707bacea3c49456b85df1d3c94036f7c9811f0b91b822ae332cb315bb | SOURCE_PIN |
| T19-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/host-logs/runtime-legacy-running/wire/host-bridge.ndjson | 09d7e76c1 | 3b3a44092e27d754751bc234a3b2cc36e274b97ff771dc73d4641b67a6d45342 | SOURCE_PIN |
| T20-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/host-logs/runtime-missing-sidecar/host.log | 09d7e76c1 | 4f9a81bf575eea2408df2b66797ee478d7115ea48512f1d6bf0564b6b76ebda3 | SOURCE_PIN |
| T21-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/host-logs/runtime-parity-roundtrip/core_service.stderr.log | 09d7e76c1 | aaec93d0f1096d188ddfd5e192f4ef4049f104e435d753dad3444bc2cf3f4086 | SOURCE_PIN |
| T22-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/host-logs/runtime-parity-roundtrip/host_bridge.stderr.log | 09d7e76c1 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| T23-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/host-logs/runtime-parity-roundtrip/host.log | 09d7e76c1 | 83c7c3c67bb00cc8c9987211e61eba77d78ba016e93d36604e5f7de0a75810c6 | SOURCE_PIN |
| T24-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/host-logs/runtime-parity-roundtrip/wire/core-service.ndjson | 09d7e76c1 | cc8a5b11c8ffc7abcc0b0ddf783efa5e78fb15885ce28356c4242fe1666b138e | SOURCE_PIN |
| T25-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/host-logs/runtime-parity-roundtrip/wire/host-bridge.ndjson | 09d7e76c1 | 82cebb2477859084a2633285c62af5dddef5fae626449775acc7b6a265a2697f | SOURCE_PIN |
| T26-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/host-logs/runtime-readonly/core_service.stderr.log | 09d7e76c1 | a0cf8f8bbaa2ed04c8a14cc2ac8f7e93d78988cca4c41b663dbe5f5bc7ef6374 | SOURCE_PIN |
| T27-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/host-logs/runtime-readonly/host_bridge.stderr.log | 09d7e76c1 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| T28-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/host-logs/runtime-readonly/host.log | 09d7e76c1 | 63a367090e5a03efa7fcbec62f1ace875c885e17f45844e140ec2843097bb235 | SOURCE_PIN |
| T29-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/host-logs/runtime-readonly/wire/core-service.ndjson | 09d7e76c1 | ad27894b22c8d828e762756f9f939b5646229539db1b1586ca2527436ff4f1b8 | SOURCE_PIN |
| T30-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/host-logs/runtime-readonly/wire/host-bridge.ndjson | 09d7e76c1 | 2e4967c82b4613a9a412aac9b9b28aa40473f215469e02758c4fc925c7228f4f | SOURCE_PIN |
| T31-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/host-logs/runtime-second-instance/host.log | 09d7e76c1 | b811ccdf3158d176b69e431edbf6107f937a332180e98a3bc5f8fbb5532ad682 | SOURCE_PIN |
| T32-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/legacy-shell/detected.json | 09d7e76c1 | 5ef8d209eeb18b7a2d18087d562b317c5e9dd27ee131208dd3fc7356934c90b8 | SOURCE_PIN |
| T33-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/legacy-shell/runtime-readonly.json | 09d7e76c1 | ef4301465315daf4a7edef6d70b66512fbcba9db5277c8cecc549fc59fdd468f | SOURCE_PIN |
| T34-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/logs/bridge-errors/host_bridge.stderr.log | 09d7e76c1 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| T35-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/logs/bridge-lifecycle/host_bridge.stderr.log | 09d7e76c1 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| T36-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/logs/bridge-wire/host_bridge.stderr.log | 09d7e76c1 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| T37-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/logs/commands-chinese/core_service.stderr.log | 09d7e76c1 | d3b7ac2fb019f0967c8d088a22ec660b0e600e025180ab882664820a9d70cd76 | SOURCE_PIN |
| T38-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/logs/commands-chinese/host_bridge.stderr.log | 09d7e76c1 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| T39-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/logs/commands-domains/core_service.stderr.log | 09d7e76c1 | bc691314586afab3c6f932cf59520461ec8ef4e8443541657205ecaf30fd2a8b | SOURCE_PIN |
| T40-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/logs/commands-domains/host_bridge.stderr.log | 09d7e76c1 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| T41-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/logs/commands-integration/core_service.stderr.log | 09d7e76c1 | 55579dc3f14fbf187b15db11c868390766757937738093e82465c457c3ce8b0b | SOURCE_PIN |
| T42-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/logs/commands-integration/host_bridge.stderr.log | 09d7e76c1 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| T43-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/logs/commands-not-supported/core_service.stderr.log | 09d7e76c1 | 9bfb69f1c373993d81d15d4ed5e3c4a03f7f590e251dfecb5c3bf0b06ffd952c | SOURCE_PIN |
| T44-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/logs/commands-not-supported/host_bridge.stderr.log | 09d7e76c1 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| T45-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/logs/core-chinese/core_service.stderr.log | 09d7e76c1 | c516f8683b19575629ff7abb1799fe3fff19b5b3fb14dba1a24e45c2b14dad34 | SOURCE_PIN |
| T46-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/logs/core-ping/core_service.stderr.log | 09d7e76c1 | 73d5b396cf1ec01dc72e1b6419b894caf148b26d2015c954d36fbbf5ad4b68a8 | SOURCE_PIN |
| T47-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/logs/core-raw-utf8/core_service.stderr.log | 09d7e76c1 | e5efd409bbd3a43fb4dbecdb18173cd0fbc1a634341792ab956fcdf52c8109c1 | SOURCE_PIN |
| T48-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/logs/core-wire-shape/core_service.stderr.log | 09d7e76c1 | 5068a7ada9fc850fd0e796236f004afbc328f5c66c712ce96247bdeebaee344b | SOURCE_PIN |
| T49-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/logs/failure-request-timeout/fake.stderr.log | 09d7e76c1 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| T50-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/logs/failure-startup-timeout/core_service.stderr.log | 09d7e76c1 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| T51-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/parity/core-command-probe.json | 09d7e76c1 | f0610758c4b23fe54b3d276f95828e89383d2d6bd8c13b1c510a30635c9cf88b | SOURCE_PIN |
| T52-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/performance/fit.json | 09d7e76c1 | d0d1eee723ad39ac837403de6569a2aa32434ab8c348a32d370a3d26e76db017 | SOURCE_PIN |
| T53-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/performance/one-to-one.json | 09d7e76c1 | 34b49b321f9b03d777cfcffe1de65268e22b2c927eedb8137ceee00581cd8607 | SOURCE_PIN |
| T54-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/performance/page-turn.json | 09d7e76c1 | c5fa7b0a240ce3d57825df96b80276fd58c99f7106dba26ad700faf0511a3f1b | SOURCE_PIN |
| T55-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/performance/webtoon.json | 09d7e76c1 | dae69956fbc81ab622040054b5a396e44335eb27b1e732f8765fdd181f2fbd92 | SOURCE_PIN |
| T56-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/security/performance/tile-read.json | 09d7e76c1 | c4c3a0f90c4017a72df6b374afd16a05cac8f6bf1420b08c41331a0af4925642 | SOURCE_PIN |
| T57-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/test/dotnet-test-Debug.log | 09d7e76c1 | dcb7e31be2821164a303c1d72eca8c59885891c9384b1dcdb62a9e5a23d2b480 | SOURCE_PIN |
| T58-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/test/pytest-baseline.log | 09d7e76c1 | a9299b7e4230e5469826dd30d034123747548af6cf8520fe70b922b3e387ca14 | SOURCE_PIN |
| T59-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/test/results-app.trx | 09d7e76c1 | edfd9a308e074f236a37f9285c495acc357af67a6aee30d13860f218edcec53c | SOURCE_PIN |
| T60-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/test/results-coreclient.trx | 09d7e76c1 | 19f0dfe1db79862b7f915005baf0dfa3791a93c3701e39c1b482aab1560908ee | SOURCE_PIN |
| T61-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/test/results-host.trx | 09d7e76c1 | 75e5882d1322309d7c1da3a1b66a61a357c7dfbd44b961477bd6d19bf0f81620 | SOURCE_PIN |
| T62-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/test/summary.json | 09d7e76c1 | 1acd7855551a77e81e3c16b70ccc758f0786b2e658aa0e34e97f1e7aa4b17382 | SOURCE_PIN |
| T63-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/test/vitest-baseline.log | 09d7e76c1 | 76e771b1be4522bb57a611c80feabb8ef9d909aed894be44015ce9e0d2bd461d | SOURCE_PIN |
| T64-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/theme/hot-switch.json | 09d7e76c1 | 1a060b4a3de0ad5311f2f84c90d08ab623b0aedb0dbaf8e562c0b493e4084e4a | SOURCE_PIN |
| T65-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/wire/bridge-errors.ndjson | 09d7e76c1 | b9f285d262508b1f590a461689674872711fa2aab7adaec37bab2b239cb85e89 | SOURCE_PIN |
| T66-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/wire/bridge-lifecycle.ndjson | 09d7e76c1 | c02522a03848ac5c1303ebae31884c23a5859627240cf33ecd002608a17cfee2 | SOURCE_PIN |
| T67-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/wire/bridge-wire.ndjson | 09d7e76c1 | ebb57348a89ed5132af22eef6f19135ac4e6e2c74df1e348c15041b630e07bb9 | SOURCE_PIN |
| T68-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/wire/commands-chinese-core-service.ndjson | 09d7e76c1 | 25f9dbd82788b693d7af4ae8df379c7b9bf872c6b32638c125c9b06a247877c0 | SOURCE_PIN |
| T69-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/wire/commands-chinese-host-bridge.ndjson | 09d7e76c1 | 5ab4253edbb1dd6b0b52446e347acc49288dc6985dd8997e0929fae91f374055 | SOURCE_PIN |
| T70-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/wire/commands-domains-core-service.ndjson | 09d7e76c1 | 1f3d46e0dfbf1f45d951fec1eb6aac97ecfdad9c0e7ae3e8f6e6a30bcca9d913 | SOURCE_PIN |
| T71-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/wire/commands-domains-host-bridge.ndjson | 09d7e76c1 | 219cc74f5e890a3f0c3aa07e700d5e4512b72479be3045a06b2f6dcb8008ed3a | SOURCE_PIN |
| T72-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/wire/commands-integration-core-service.ndjson | 09d7e76c1 | 5fca2ef6eb03758159fb4594c9f1476a1d2a853018134f4b180980e84217dfe0 | SOURCE_PIN |
| T73-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/wire/commands-integration-host-bridge.ndjson | 09d7e76c1 | d0cb6f1f55e5ed2849eccb93e0697e8d86e66ed47cd342a232846c8e5d5211e2 | SOURCE_PIN |
| T74-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/wire/commands-not-supported-core-service.ndjson | 09d7e76c1 | 7dd4952921a7a4dbd072b65dca2b40ac4c0161adf12bbc57acb36a6308ea099c | SOURCE_PIN |
| T75-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/wire/commands-not-supported-host-bridge.ndjson | 09d7e76c1 | 945e9392ac367b8cb779678eb7e09facbbf065dacf5b99bead0d1d11a3d2bc64 | SOURCE_PIN |
| T76-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/wire/core-chinese-roundtrip.json | 09d7e76c1 | ea6dcd5029a602746937ad85bce616305f733ad185eae517b23589a4ebe17444 | SOURCE_PIN |
| T77-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/wire/core-chinese.ndjson | 09d7e76c1 | 949d0a8933daefb31f68932a65397e4d1f29c1c37b39449a7e1b3056150da407 | SOURCE_PIN |
| T78-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/wire/core-ping.json | 09d7e76c1 | 87514e22c35ffbae9461eb3db9d3065d5a52de38b27ee31ae055e8662f24b68e | SOURCE_PIN |
| T79-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/wire/core-ping.ndjson | 09d7e76c1 | 1f720c1050d1e375135328676f22712c8c260e755cab0ede68a46d4017cfef70 | SOURCE_PIN |
| T80-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/wire/core-raw-utf8-negative.json | 09d7e76c1 | 611962501be106ce97c22a0c6cc3ac7c157d7c691c1378eb44b25834d64ca084 | SOURCE_PIN |
| T81-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/wire/core-raw-utf8.ndjson | 09d7e76c1 | d3d1f7e273c63abbbf0077a7df24f8e7a52aa48e88d0b7801d1ea2f5ae0b3989 | SOURCE_PIN |
| T82-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/wire/core-wire-shape.json | 09d7e76c1 | c1f1af0ae3845f81e04f59f61fd72800943c057dbf559cd339cfb05788afa6a5 | SOURCE_PIN |
| T83-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/wire/core-wire-shape.ndjson | 09d7e76c1 | cafa0e93b5f300877963e347f2d04f01f51d2a4a241af41e971115c7b0c4546b | SOURCE_PIN |
| T84-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/wire/host-bridge-errors.json | 09d7e76c1 | 0d020691850a9ce4d19eac4791d3f4489c6ddeb5d443f5526c72f00488c360a6 | SOURCE_PIN |
| T85-src | AC5/AC6 | verification/HOST-TILE-CHANNEL-1/wire/host-bridge-lifecycle.json | 09d7e76c1 | e3df7fa40b08d940e4644f9176980ee64fb1d09a66f0b16c6c63bfd85fa6a98b | SOURCE_PIN |
## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/HOST-TILE-CHANNEL-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/HOST-TILE-CHANNEL-1 | d8f5cd008228e62884f3f4921e6383469163ec360a8d751ebf06c177eb6b11d1 | 待关闭时核 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pinned`（E1–E11，commit c8ab135d1）。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
## Review（DSH 集成复核，2026-10-27）— PASS

- 单命令验收：scripts/test.ps1 → **95/95 passed / 0 skipped**；vitest 60/567、pytest 3F/2687P/9S 基线不变。
- 四个数字采信（可复跑脚本 + 证据 pin）：revoke 时延 **0.071ms**、缓存命中 0.667、篡改保尺寸 → TileDigestMismatch、等长重写 → TileDigestMismatch；附加 4MiB 冷读+摘要 **2.523ms**、identity 替换 → TileIdentityMismatch。
- 实现方未放宽校验、未动旧壳/Core，范围仅 pps/desktop-avalonia/** + 证据 + 文档。
- **遗留转 S5-B**：digest 开销比 5.39×（缓存口径，非 G5 ≤10%）→ 按"页加载预算内占比"重测；Core 侧 tile 生成/digest 下发契约待冻结；真机 smoke/IME 留 S5-D。
- 集成： 9d7e76c1。
