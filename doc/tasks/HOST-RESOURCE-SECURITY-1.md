---
id: HOST-RESOURCE-SECURITY-1
title: S5-B 资源安全等价 harness（D4-1/3/5/6）+ digest 预算重测 + tile 契约冻结
kind: implementation
governance_version: 3
status: done
approval: user_authorized_2026-10-26_ad002_autonomy
suggested_owner: antigravity
owner: avalonia-spike
reviewer: dsh
depends_on: [HOST-TILE-CHANNEL-1]
base_commit: 09d7e76c1
branch: task/HOST-RESOURCE-SECURITY-1
worktree: G:/CODEX/New Manga.workspace/worktrees/HOST-RESOURCE-SECURITY-1
integration_commit: 744eccb61
delivery_head: 4a1dbe96fced6223426b2be7747282550d07e5e8
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/HOST-RESOURCE-SECURITY-1
allowed_paths:
  - doc/tasks/HOST-RESOURCE-SECURITY-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/HOST-RESOURCE-SECURITY-1/**
  - G:/CODEX/New Manga.workspace/task-envs/HOST-RESOURCE-SECURITY-1/**
  - G:/CODEX/New Manga.workspace/worktrees/HOST-RESOURCE-SECURITY-1/**
---

# HOST-RESOURCE-SECURITY-1：S5-B 安全等价 harness

## 来源

S5 拆分（`LEGACY-SHELL-REMOVAL-1` BLOCKED 段）、[ADR-0002](../design/ADR-0002_RESOURCE_CHANNEL_SECURITY_V2.md) D4；S5-A 已交付 tile 通道与 D4-2/4 基础（集成 `09d7e76c1`）。

## Acceptance Criteria

- [x] **AC1 D4-1 等长原地重写**：同一页被等长改写 → 必然拒绝（不得依赖 mtime）；测试含"改写后同 size、同 mtime 粒度"场景。 <<MET>>
- [x] **AC2 D4-3 越界/escape**：越界路径、junction、reparse point、UNC/符号链接逃逸全部拒绝（issue 与 read 两处）。 <<MET>>
- [x] **AC3 D4-5 身份变化**：文件被替换（同路径新文件）→ `TileIdentityMismatch`；volume/file index 变更检测。 <<MET>>
- [x] **AC4 D4-6 大页性能**：单页冷加载 **≤60ms**、**digest 开销占页加载预算 ≤10%**（按 G5 口径重测，不沿用 5.39× 缓存口径）。 <<MET>>
- [x] **AC5 tile 契约**：冻结 Core→Host 的 tile 生成与 per-tile digest 下发契约（文档 + 契约测试；Core 侧改动若需则只在新的独立 Task，本卡不改 Core）。 <<MET>>
- [x] **AC6 门禁**：`check.ps1 -TaskPath` PASS；`scripts/test.ps1` 全绿；vitest 60/567；pytest 基线不变；证据 64-hex pin；Handoff + Record Decision。 <<MET>>

## 允许修改范围

`apps/desktop-avalonia/**`（测试/harness 可加、生产代码只改安全缺陷）、本卡、STATUS/PLAN/LEDGER、`verification/HOST-RESOURCE-SECURITY-1/**`、workspace。只读：ADR-0002、S5-A Handoff、旧 Rust 通道（语义参考）。

## 禁止范围

不改旧壳（S5-C 才归档）、不改 Python Core、不 push、不 gc/prune、不为过测放宽校验/伪造数字。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 等长改写（同 size/mtime 粒度） | 无标签副本 | NOT_RUN | 待填 |
| AC2 | 越界/junction/reparse/UNC 负例 | 同上 | NOT_RUN | 待填 |
| AC3 | 替换同路径文件 | 同上 | NOT_RUN | 待填 |
| AC4 | 大页冷加载 + digest 占比 | 真实页夹具 | NOT_RUN | 待填 |
| AC5/AC6 | 契约测试 + 全量门禁 | 全量 | NOT_RUN | 待填 |

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| E1-d4-1 | AC1 | verification/HOST-RESOURCE-SECURITY-1/security/d4-1-equal-length-rewrite.json | 4a1dbe96fced6223426b2be7747282550d07e5e8 | c024f4f52017e4d69cb850f7ec7dd9adcee38d709e31d6a68d79c26cea8a1c54 | CANONICAL |
| E2-d4-3-issue | AC2 | verification/HOST-RESOURCE-SECURITY-1/security/d4-3-escape-issue.json | 4a1dbe96fced6223426b2be7747282550d07e5e8 | 0d73a58855f58a236c8fdfc55eb65980b892834d35f5986a330fd5a44e64cbe5 | CANONICAL |
| E3-d4-3-read | AC2 | verification/HOST-RESOURCE-SECURITY-1/security/d4-3-escape-read.json | 4a1dbe96fced6223426b2be7747282550d07e5e8 | 769595e14c14fb8bec973390cab60059eb985faf0328d7fd4c4ffe64c8217a0c | CANONICAL |
| E4-d4-5 | AC3 | verification/HOST-RESOURCE-SECURITY-1/security/d4-5-identity-change.json | 4a1dbe96fced6223426b2be7747282550d07e5e8 | 69c6eacfea26e6712335da42b85fdf938e1f098fc2807210b9e059eaedfe76f8 | CANONICAL |
| E5-d4-6 | AC4 | verification/HOST-RESOURCE-SECURITY-1/performance/d4-6-page-budget.json | 4a1dbe96fced6223426b2be7747282550d07e5e8 | 611a1686b20fec66cc384e05d35fa2a238741ea1feb310b5bb4f8cf3443f167f | CANONICAL |
| E6-contract | AC5 | verification/HOST-RESOURCE-SECURITY-1/contract/tile-contract.json | 4a1dbe96fced6223426b2be7747282550d07e5e8 | 1e94efe36e24b8ed656491882b104714b4c6414ecd20985843663d42dc93950d | CANONICAL |
| E7-manifest | 全 AC | verification/HOST-RESOURCE-SECURITY-1/MANIFEST.json | 4a1dbe96fced6223426b2be7747282550d07e5e8 | 3b833b9f6dc645fc525b8f5dc3a9e4ba4ee75e528b17e1331a9cc666f75dba84 | CANONICAL |
| P1-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/commands/chinese-roundtrip.json | 744eccb61 | bbd6ee9d4ccf9ac6d3e1bd5c8d845a69c7845cd76e54e983874778185e95f130 | SOURCE_PIN |
| P2-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/commands/domain-services.json | 744eccb61 | c00ef5b8ce38b89f7e4711ccb543d087732d16419b995bafa4db3d66d9b76b7a | SOURCE_PIN |
| P3-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/commands/integration-results.json | 744eccb61 | 7aa5464c72c67d4a632e3fb69ab1633157cb618575dfc002355fee6cf05c6b72 | SOURCE_PIN |
| P4-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/commands/not-supported-typed-errors.json | 744eccb61 | 3ee273a43241e135e1fed39713cfd0aa9051618074d19b15ead1d03b1f43c4c6 | SOURCE_PIN |
| P5-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/commands/parity-contract.json | 744eccb61 | 1a188fd7af08bde50dace142f22ac4e5208bec466458b129b6c4e679f6aec962 | SOURCE_PIN |
| P6-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/commands/wiring.json | 744eccb61 | 1b5a31590d0c993533d4912df6587689b15ed658631ce70e39badeae4f1bc1d8 | SOURCE_PIN |
| P7-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/diagnostics/missing-exe.json | 744eccb61 | 4594512db61c9500844d52d13c3b289c0322cdfed7dc471e8f3a1eac425391dd | SOURCE_PIN |
| P8-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/diagnostics/request-timeout.json | 744eccb61 | d92e4e444d02eda85d8f361a1d140e43d818429a18ea7c3244dc82df40d76269 | SOURCE_PIN |
| P9-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/diagnostics/spawn-failed.json | 744eccb61 | d328eb1713bbede1e76649b4474c555dfbde7c72e00736d1828a2118afc6760b | SOURCE_PIN |
| P10-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/diagnostics/startup-timeout.json | 744eccb61 | 95a65b02f59bd9d5259d3fe0f81839c99d6ba872c7461c0710eff8c9e2d4dbf7 | SOURCE_PIN |
| P11-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/host/runtime-chinese-roundtrip.json | 744eccb61 | 344024d1ddb450ab1e3e32b328208c909b4405def1077f867f458e04c7151b28 | SOURCE_PIN |
| P12-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/host/runtime-missing-sidecar.json | 744eccb61 | 294565828007d46dca8cba7ce0f2705cf89cb7e20f55d45e3dbb0c68420ae74e | SOURCE_PIN |
| P13-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/host/runtime-readonly.json | 744eccb61 | 855710ca4f5b6c4e61e705f50c735781ec1b496fd93ff15bb35f8b5c8f954790 | SOURCE_PIN |
| P14-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/host/second-instance.json | 744eccb61 | 53cc851a3c31129dfddc38b460eba1a6652a078578658265218e167368d07581 | SOURCE_PIN |
| P15-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/host-logs/runtime-legacy-running/core_service.stderr.log | 744eccb61 | f702ef6e38cb703f4f0789d4b304cacf02806ba1d329b00a26a5d3d59cd179ea | SOURCE_PIN |
| P16-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/host-logs/runtime-legacy-running/host_bridge.stderr.log | 744eccb61 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| P17-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/host-logs/runtime-legacy-running/host.log | 744eccb61 | 3cf72d4e89f7c251633eae1b5fb31a2a4f5f07372d3e59345053b5f47ff3fd30 | SOURCE_PIN |
| P18-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/host-logs/runtime-legacy-running/wire/core-service.ndjson | 744eccb61 | 84000be64bce8efdaf991886365a59baddc978bfffd47c4fa074294f66aabcb2 | SOURCE_PIN |
| P19-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/host-logs/runtime-legacy-running/wire/host-bridge.ndjson | 744eccb61 | 8782bba7b0321a768f05d1fc3b3c91098887b43ee5e870bdcd9ca7f9d216ecbf | SOURCE_PIN |
| P20-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/host-logs/runtime-missing-sidecar/host.log | 744eccb61 | 68144eea627a736e6c5a499ba6e1f5bfe5daee3769718b4133c16b37fc2e3e12 | SOURCE_PIN |
| P21-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/host-logs/runtime-parity-roundtrip/core_service.stderr.log | 744eccb61 | fbd1154011782e268174167e2d8cf81ff09ef70bbad21fbecdf6a6dae41481ea | SOURCE_PIN |
| P22-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/host-logs/runtime-parity-roundtrip/host_bridge.stderr.log | 744eccb61 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| P23-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/host-logs/runtime-parity-roundtrip/host.log | 744eccb61 | 647759077ad3a266c380532dc5244003222e1b29e30f419344c0c4f06ea23b7b | SOURCE_PIN |
| P24-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/host-logs/runtime-parity-roundtrip/wire/core-service.ndjson | 744eccb61 | ad4304a0fce5a35f497c642a5e4d77db506c9f067df1d3ac2f0c07be3a68d54c | SOURCE_PIN |
| P25-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/host-logs/runtime-parity-roundtrip/wire/host-bridge.ndjson | 744eccb61 | c3690c69f460511f21d1348bbef075b8de01443da1b5d464b2f6572e299b130e | SOURCE_PIN |
| P26-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/host-logs/runtime-readonly/core_service.stderr.log | 744eccb61 | 4e862c748cd410bf319750e32c31a88b7575f2f4d744ab1a14e782fc8f9a5113 | SOURCE_PIN |
| P27-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/host-logs/runtime-readonly/host_bridge.stderr.log | 744eccb61 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| P28-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/host-logs/runtime-readonly/host.log | 744eccb61 | 6d450427523860c7a3f049635ff5de9647d1926181ba0f451c78d600dad556e1 | SOURCE_PIN |
| P29-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/host-logs/runtime-readonly/wire/core-service.ndjson | 744eccb61 | a6849ba4313630ec6330eef56e146aad90067317ccd45a102eb492ce1430710a | SOURCE_PIN |
| P30-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/host-logs/runtime-readonly/wire/host-bridge.ndjson | 744eccb61 | e3dabfceeb91e185bce4cbbf2477214dc4bac2c00fc1919d8daaf525e2b6bca2 | SOURCE_PIN |
| P31-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/host-logs/runtime-second-instance/host.log | 744eccb61 | c02354b6245b90eb48015eb29db58991ddd596ba8af4fd187a3013b40f98cc20 | SOURCE_PIN |
| P32-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/legacy-shell/detected.json | 744eccb61 | ef3eef3a7290544b9325c06d228a9ba8153d34756fecafb411b5ff6c6c711d93 | SOURCE_PIN |
| P33-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/legacy-shell/runtime-readonly.json | 744eccb61 | ef4301465315daf4a7edef6d70b66512fbcba9db5277c8cecc549fc59fdd468f | SOURCE_PIN |
| P34-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/logs/bridge-errors/host_bridge.stderr.log | 744eccb61 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| P35-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/logs/bridge-lifecycle/host_bridge.stderr.log | 744eccb61 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| P36-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/logs/bridge-wire/host_bridge.stderr.log | 744eccb61 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| P37-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/logs/commands-chinese/core_service.stderr.log | 744eccb61 | 8d3f38c830a1795d7c4b858d245dd98b81429d634d9b0cc2c7f2411bf05a5f49 | SOURCE_PIN |
| P38-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/logs/commands-chinese/host_bridge.stderr.log | 744eccb61 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| P39-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/logs/commands-domains/core_service.stderr.log | 744eccb61 | ac59af24b99f14486b0cbfad58f350e8758d66ef49b2c0707637ebebde9b95c9 | SOURCE_PIN |
| P40-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/logs/commands-domains/host_bridge.stderr.log | 744eccb61 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| P41-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/logs/commands-integration/core_service.stderr.log | 744eccb61 | 13758dc60b1bf839f1114f9bdf9992eb896e7c7c0ecb801d5842c3a8b5182ed9 | SOURCE_PIN |
| P42-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/logs/commands-integration/host_bridge.stderr.log | 744eccb61 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| P43-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/logs/commands-not-supported/core_service.stderr.log | 744eccb61 | 2d636765f523b61d24a62725617f1c4813c5c1afe694257974e9359ba13d8510 | SOURCE_PIN |
| P44-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/logs/commands-not-supported/host_bridge.stderr.log | 744eccb61 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| P45-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/logs/core-chinese/core_service.stderr.log | 744eccb61 | d400ace417d37219f0de9d1df5655b7efa1a9a4e1a16ff01a3878e83c987c5c9 | SOURCE_PIN |
| P46-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/logs/core-ping/core_service.stderr.log | 744eccb61 | 196208d94df8e3d9dfb88d7166fc53974cb0b478f0c4727511a656d1890f538d | SOURCE_PIN |
| P47-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/logs/core-raw-utf8/core_service.stderr.log | 744eccb61 | 9d3cd66b29a40e3ad1cef4096564ed60c69d5f7a811ec0cdde2465d4d985ac6b | SOURCE_PIN |
| P48-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/logs/core-wire-shape/core_service.stderr.log | 744eccb61 | b4896db4e44d5525e0c72fb6d3fc53869d55f01b5e169987e069b379459b581a | SOURCE_PIN |
| P49-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/logs/failure-request-timeout/fake.stderr.log | 744eccb61 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| P50-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/logs/failure-startup-timeout/core_service.stderr.log | 744eccb61 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| P51-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/parity/core-command-probe.json | 744eccb61 | 4ddf92c092d72e1bbbc5abeaece9608268fc430c20b628a98c87a8949701cad5 | SOURCE_PIN |
| P52-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/performance/fit.json | 744eccb61 | d0d1eee723ad39ac837403de6569a2aa32434ab8c348a32d370a3d26e76db017 | SOURCE_PIN |
| P53-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/performance/one-to-one.json | 744eccb61 | 34b49b321f9b03d777cfcffe1de65268e22b2c927eedb8137ceee00581cd8607 | SOURCE_PIN |
| P54-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/performance/page-turn.json | 744eccb61 | 7cd3d3bb908a2804577f1706159f7f7c4c2acad5c5fd3ed1ee1c5fdf69cf8b00 | SOURCE_PIN |
| P55-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/performance/tile-read.json | 744eccb61 | fb3333381a94e7bc5282b53bda98dff9f45197f703ce513f965edb5027b785cc | SOURCE_PIN |
| P56-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/performance/webtoon.json | 744eccb61 | 888ec0f0007d3cef9d2bfa173969861ca7c4211f53b15a01028bedf60b29d4b6 | SOURCE_PIN |
| P57-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/security/cache-revoke.json | 744eccb61 | c78ce2c60a6367e71c0b1fe50f62f38680ba87ac5247e57b24135aeab8fd4b85 | SOURCE_PIN |
| P58-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/security/containment.json | 744eccb61 | ed8f0e892677c75023e166e30139695a841e8ecda8a39f3ab5a080b033b85108 | SOURCE_PIN |
| P59-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/security/equal-length-rewrite.json | 744eccb61 | 7de064cad61e7ddbd311d4a6fecfab842b96bfef50f4bd1b26d2eedf9680c0e3 | SOURCE_PIN |
| P60-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/security/expiry.json | 744eccb61 | a6ffe77b083ea4621284c3c801113c4b39d33ba8b00e5a5516f5b1979607a5ae | SOURCE_PIN |
| P61-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/security/identity-change.json | 744eccb61 | 2ba0ac96ca6dd3e7b72a50a68720d8732ff6cb93af5ec94e0bc4e4f6ce4fe466 | SOURCE_PIN |
| P62-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/security/issue-read-revoke.json | 744eccb61 | cee8225e1e6c2a333573390d35c1de748ab8d9aea9fa9509fad67591c4051a46 | SOURCE_PIN |
| P63-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/security/reader-tile-channel.json | 744eccb61 | ced059e492ef93a27dfa515e7749d0fd8245f790bef56d21a5c2dce04c19d1ee | SOURCE_PIN |
| P64-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/security/tampered-tile.json | 744eccb61 | 07f6b456e92da5d9c23b3bd70af5b75c7881364a59cb7ade271c67802e54e8e5 | SOURCE_PIN |
| P65-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/security/workbench-tamper.json | 744eccb61 | ec0eaf79d61fb897734f23d9812b4b6f146ef64eca3a73d27141c9631ef0a88c | SOURCE_PIN |
| P66-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/test/dotnet-test-Debug.log | 744eccb61 | e97abf33af8baaa07231b5eab83cf7c9412b3baec76e11f16271735b2263b41b | SOURCE_PIN |
| P67-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/test/pytest-baseline.log | 744eccb61 | 1beed4645c2c09ec94e0174d5a7993765da31b3308ead18d728df450dbfe2996 | SOURCE_PIN |
| P68-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/test/results-app.trx | 744eccb61 | 3cbefdccdb2dae796d645acd548ca69b14a906e3ee4ff598735625c4f319c063 | SOURCE_PIN |
| P69-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/test/results-coreclient.trx | 744eccb61 | 02b34c11550b333dcbc6ee3acc408799960717ff47ad5538bb79d4880df9db5f | SOURCE_PIN |
| P70-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/test/results-host.trx | 744eccb61 | 4a41ed221973d04f1103264158b93721aab895d031397a7f7a97f203579a4a7d | SOURCE_PIN |
| P71-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/test/summary.json | 744eccb61 | 0c920fc40437a9f73092e133028f2a77ff14a263f4b5f094b7a22b64deb6fa96 | SOURCE_PIN |
| P72-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/test/vitest-baseline.log | 744eccb61 | eea1d0afa9116859db3bbce337710f85845c9d480e8a39c3d5a7dea8fe0aba3d | SOURCE_PIN |
| P73-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/theme/hot-switch.json | 744eccb61 | f91504fcb4153b8f08c77612f4d8e39bd61394ea38a65ebdc667c7932934dbca | SOURCE_PIN |
| P74-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/wire/bridge-errors.ndjson | 744eccb61 | 2418910b0d2de16c99cce86a8d3b713252df2fec21fe4f06d87d0dcb773381ca | SOURCE_PIN |
| P75-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/wire/bridge-lifecycle.ndjson | 744eccb61 | 72b0042d85e7813cf84f95b11d7fa68e31003c483600a170eff50596fef58666 | SOURCE_PIN |
| P76-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/wire/bridge-wire.ndjson | 744eccb61 | 45ee4acd23d712491a02337131781d96ab1f00d0da188295a10992e810b10ad0 | SOURCE_PIN |
| P77-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/wire/commands-chinese-core-service.ndjson | 744eccb61 | 9451b4531d8c6632e5d521c395b17e195df06b222578cb8743c13339dccfed93 | SOURCE_PIN |
| P78-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/wire/commands-chinese-host-bridge.ndjson | 744eccb61 | 14febcc6404aba334eb1209c9c1f403a32925ed747f4e585953e93e95fd277d2 | SOURCE_PIN |
| P79-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/wire/commands-domains-core-service.ndjson | 744eccb61 | 53f8de16c492957281f0732b265d1a96ddb6dc8b106358df0231fbe3343ddd2d | SOURCE_PIN |
| P80-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/wire/commands-domains-host-bridge.ndjson | 744eccb61 | ea9ad3f9f3bd03aa532f39bf33a33fade2806fab8503e24edf3e823c9749e152 | SOURCE_PIN |
| P81-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/wire/commands-integration-core-service.ndjson | 744eccb61 | 594fb6b45d333c08590b07c972d708a625593fa36b6f12041d2ab63f9e762f48 | SOURCE_PIN |
| P82-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/wire/commands-integration-host-bridge.ndjson | 744eccb61 | 8be2b4601ebc4316ee4be0aac8c032b430c335617d6d674bf0a84cdab6cd376c | SOURCE_PIN |
| P83-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/wire/commands-not-supported-core-service.ndjson | 744eccb61 | 7659259a143824a5c9b62d7dd09d418b9be5a62cd7508a8b94d09cb3bf1094e4 | SOURCE_PIN |
| P84-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/wire/commands-not-supported-host-bridge.ndjson | 744eccb61 | 76557b5600ed9b4326bb8f2b3afae4c4b4c163e814e2073ed6f154c53ce7629f | SOURCE_PIN |
| P85-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/wire/core-chinese-roundtrip.json | 744eccb61 | 68faa1fd8e5e8b5b17c67675cdcdfcb2952797bdb56cc1a4105449c42aa88852 | SOURCE_PIN |
| P86-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/wire/core-chinese.ndjson | 744eccb61 | 45aa5599f989541f1bed472a1a88e0bbaa0ef235b6f54dc0bb66fbb66897e851 | SOURCE_PIN |
| P87-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/wire/core-ping.json | 744eccb61 | d4a407afbf3a5cc782e26d86b030cf913a16ae8116a73788a535d89adc3f3a1d | SOURCE_PIN |
| P88-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/wire/core-ping.ndjson | 744eccb61 | 52e942063e707edbc2c40ef506e2caab63212804e35ba40175a073babcf9362c | SOURCE_PIN |
| P89-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/wire/core-raw-utf8-negative.json | 744eccb61 | 611962501be106ce97c22a0c6cc3ac7c157d7c691c1378eb44b25834d64ca084 | SOURCE_PIN |
| P90-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/wire/core-raw-utf8.ndjson | 744eccb61 | 7dc64f645c38c28d093cb5ccef0c6ebc0a7aae6181378b7e758cfe62695dfeac | SOURCE_PIN |
| P91-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/wire/core-wire-shape.json | 744eccb61 | caecc8c0b996a4a6742230a8b63cdc7e2c0e2fe1ee0e09ff92d65b54bbc3d0e7 | SOURCE_PIN |
| P92-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/wire/core-wire-shape.ndjson | 744eccb61 | 127ba3dbce1a17ef44a2dde085f6b6718005ecd44036f629c07ad0180856e467 | SOURCE_PIN |
| P93-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/wire/host-bridge-errors.json | 744eccb61 | c683db28bc0e5b6c64083795f13ed617389b68a1b637417c0bafb3539b225e4f | SOURCE_PIN |
| P94-src | AC6 | verification/HOST-RESOURCE-SECURITY-1/wire/host-bridge-lifecycle.json | 744eccb61 | fa02daec36a252c564ccf96cecb04442777ec337711cc881e3e5994aed74b514 | SOURCE_PIN |
## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/HOST-RESOURCE-SECURITY-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/HOST-RESOURCE-SECURITY-1 | 待填 | 待关闭时核 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pinned`（E1–E7，commit 4a1dbe96fced6223426b2be7747282550d07e5e8）。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
## Review（DSH 集成复核，2026-10-27）— PASS

- 单命令验收：scripts/test.ps1 → **101/101**；vitest 60/567、pytest 基线不变。
- D4 四项实测复核采信（证据 pin + 可复跑）：等长改写且 mtime 复原 → TileDigestMismatch（alidation_uses_mtime=false）；issue+read 两处 dotdot/UNC/junction/symlink → 拒绝；同 size 替换 → TileIdentityMismatch；8×256KiB 冷读+digest **2.259ms**、digest **1.33% of 60ms 预算**（G5 口径，未沿用缓存口径）。
- tile 契约已冻结（TILE-CHANNEL-CONTRACT-V1.md，Host 侧结构 + 版本化入口）。
- 遗留转后续：Core 侧 tile 生成/per-tile digest 下发 → CORE-TILE-EMIT-1；真机磁盘冷读/IME/安装 smoke → S5-D；旧壳归档 → S5-C（前置=本卡+S5-D）。
- 集成：744eccb61；范围仅 pps/desktop-avalonia/** + 证据 + 文档。
