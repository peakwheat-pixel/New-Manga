---
id: UI-SHELL-THEME-1
title: S3 主窗 + 主题中心 + 书架（Saber 参考）+ 设置骨架
kind: implementation
governance_version: 3
status: done
approval: user_authorized_2026-10-26_ad002_autonomy
suggested_owner: zcode
owner: avalonia-spike
reviewer: dsh
depends_on: [HOST-CORECLIENT-1]
base_commit: 5a11fa7d9
branch: task/UI-SHELL-THEME-1
worktree: G:/CODEX/New Manga.workspace/worktrees/UI-SHELL-THEME-1
integration_commit: 657d36817
delivery_head: 28cd1324ca835a90694393ed95749407836da544
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/UI-SHELL-THEME-1
allowed_paths:
  - doc/tasks/UI-SHELL-THEME-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/UI-SHELL-THEME-1/**
  - G:/CODEX/New Manga.workspace/task-envs/UI-SHELL-THEME-1/**
  - G:/CODEX/New Manga.workspace/worktrees/UI-SHELL-THEME-1/**
---

# UI-SHELL-THEME-1：S3 主窗 + 主题中心 + 书架 + 设置骨架

## 来源与目标

AD-002 §3/§4、`ui-spec/SABER_UI_SPEC.md` + `tokens-saber-purple.json`（已交付）、ADR-0001（布局/共存）、S1/S2 已完成。目标：新壳具备可用的四页骨架，主题中心可运行时热切换，书架按 Saber **参考规格**（非 1:1）实现，并为 S4 工作台/阅读器留出插槽。

## Acceptance Criteria

- [x] **AC1 主窗与导航**：沉浸式标题栏（Win11 Mica / Win10 回退不透明）、四页导航壳（书架/工作台/阅读器/设置）、单实例、启动不阻塞（不等待 Core 完成首帧）、无控制台。 <<MET>>
- [x] **AC2 主题中心**：ThemePack = `manifest.json + tokens.json + controlthemes.xaml + materials.json + motion.json + icons/`；内置 ≥6 套（含 Saber Purple 默认 + light/dark）；**3 套热切 P95 ≤100ms**、不重启、截图差分无色残留、reduced-motion 归零。 <<MET>>
- [x] **AC3 书架页**（Saber 参考）：紫渐变顶栏、1400 居中、标题+三动作、白卡搜索+标签 chip、封面 3:4 书卡网格（列数在 VM 计算，Avalonia 无 auto-fill）、hover「查看详情」、详情/新建入口、空态/无结果态。 <<MET>>
- [x] **AC4 设置骨架**：分区导航 + 已接线 settings 命令的展示/编辑；S2 的 50 条 NS 中「书架/设置所需」子集逐批接线（列出清单与完成数）。 <<MET>>
- [x] **AC5 质量门禁**：`scripts/test.ps1` 全绿（含 UI headless 测试）；旧壳 `npx vitest run` 仍 60/60 文件 567/567；换肤/导航/书卡交互有测试；无控制台；键盘焦点可达；`check.ps1 -TaskPath` PASS；证据 pin 64-hex。 <<MET>>
- [x] **AC6 交接**：Handoff `doc/handoffs/UI-SHELL-THEME-1-handoff.md`；Record Decision（主题服务设计、NS 接线批次、字体策略=仅系统栈）。 <<MET>>

## 允许修改范围

`apps/desktop-avalonia/**`、本卡、STATUS/PLAN/LEDGER 指针、`verification/UI-SHELL-THEME-1/**`、workspace。只读：`ui-spec/**`、`doc/AD-002*`、`doc/design/ADR-*`、`doc/design/EXECUTION_DIRECTIVE_AD002_V2.md`。

## 禁止范围

不改旧壳 `apps/desktop/**`、不改 Python Core、不改 AD/ADR、不 push、不 1:1 复刻 Saber 截图、不随包商业/系统字体（仅系统字体栈）、不 gc/prune。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | headless 启动不阻塞 + WindowMaterial 判据 + 四页导航/键盘焦点 | .NET9/Avalonia 11.3.22 | PASS：首帧早于 Host ready；Win11→Mica / Win10→不透明回退；4 按钮可聚焦切换 | E6/E7 |
| AC2 | 6 packs 结构断言 + 3 套×10 次热切 + reduced-motion | 同上 | PASS：**p95 2.215ms**（≤100ms，spike 3.74ms 为基准）；ThemeDictionaries Light/Dark；无色残留；reduced-motion 全 0 | E1 |
| AC3/AC4 | headless UI + 真 sidecar 命令（经 dispatcher） | 无标签 sidecar 副本 | PASS：列数 VM 计算(1400→7)、搜索/标签/空态/无结果/详情/新建；接线 13 已实现命令 + 8 条 NS 批次登记(S3-A/B/C) | E2/E3/E4/E5 |
| AC5/AC6 | `scripts/test.ps1 -CanonicalEvidence`；`npx vitest run`；`check.ps1 -TaskPath` | 全量 | PASS：dotnet **74/74**、裸跑 58 passed/16 skipped、vitest 60/567；check PASS；证据 pin 64-hex | E3/E8–E11 |
## 依赖、风险与阻塞

- 依赖：HOST-CORECLIENT-1（done）；S2 的 NS 清单（Handoff 已列）。
- 风险 1：主题热切与 Mica 合成冲突（spike 已验证可行，需回归）；风险 2：书卡网格列数计算与 DPI；风险 3：NS 命令接线遗漏导致页面空态误判。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| E1-theme-hot-switch | AC2 | verification/UI-SHELL-THEME-1/theme/hot-switch.json | 28cd1324ca835a90694393ed95749407836da544 | 399baf37b7744df5ff0595289516e4c15ac74546d78994f658b25726dcad0f55 | CANONICAL |
| E2-wiring | AC4 | verification/UI-SHELL-THEME-1/commands/wiring.json | 28cd1324ca835a90694393ed95749407836da544 | 1b5a31590d0c993533d4912df6587689b15ed658631ce70e39badeae4f1bc1d8 | CANONICAL |
| E3-test-log | AC5 | verification/UI-SHELL-THEME-1/test/dotnet-test-Debug.log | 28cd1324ca835a90694393ed95749407836da544 | 202bcd9dd6db35748ad7c428ed1f546a145e5e1e7151cc3a33f86c17b67d61f3 | CANONICAL |
| E4-test-summary | AC5 | verification/UI-SHELL-THEME-1/test/summary.json | 28cd1324ca835a90694393ed95749407836da544 | 4cf9f2ccd95afcef4f28c363e5e668b01ec9e68e09736f381eb306a2cc9832d5 | CANONICAL |
| E5-trx-app | AC1/AC2/AC3/AC4 | verification/UI-SHELL-THEME-1/test/results-app.trx | 28cd1324ca835a90694393ed95749407836da544 | 19767d821cfa9aedba0ee8d8805fb8bfdd4d13be328c04db1535cd0f5c126579 | CANONICAL |
| E6-trx-core | AC3/AC4 | verification/UI-SHELL-THEME-1/test/results-coreclient.trx | 28cd1324ca835a90694393ed95749407836da544 | 946dee1feb74005ff15f494ea665713156ec61ac118c18e179f42f57f25c14a3 | CANONICAL |
| E7-trx-host | AC1 | verification/UI-SHELL-THEME-1/test/results-host.trx | 28cd1324ca835a90694393ed95749407836da544 | 2ee4ffa876db32c9609a14e25ecd27a4e48497de312638a931a5fa4b3da9ca50 | CANONICAL |
| E8-build | AC5 | verification/UI-SHELL-THEME-1/build/dotnet-build-Debug.log | 28cd1324ca835a90694393ed95749407836da544 | 5a362c057b3c62a65cebf610272722e8adb5a353d321fa6d887f7ad51b1c4a59 | CANONICAL |
| E9-vitest | AC5 | verification/UI-SHELL-THEME-1/test/vitest-baseline.log | 28cd1324ca835a90694393ed95749407836da544 | 9ebf78cd82d7d3b45a7e9a5472c0841d050ae4f3e5ced4857247a4adecce1360 | CANONICAL |
| E10-probe | AC3/AC4 | verification/UI-SHELL-THEME-1/parity/core-command-probe.json | 28cd1324ca835a90694393ed95749407836da544 | 5557e3cf987f7dee80ffa26a4a6ec2c9576102c2e00ae9fc786ff437cd9970c0 | CANONICAL |
| E11-manifest | 全 AC | verification/UI-SHELL-THEME-1/MANIFEST.json | 28cd1324ca835a90694393ed95749407836da544 | 1d622ac6d000d10b8155d11cffeaeda497793cc5f1d6443c2434bc152e13654b | CANONICAL |
| M1-src | AC4/AC5 | verification/UI-SHELL-THEME-1/commands/chinese-roundtrip.json | 657d36817 | bbd6ee9d4ccf9ac6d3e1bd5c8d845a69c7845cd76e54e983874778185e95f130 | SOURCE_PIN |
| M2-src | AC4/AC5 | verification/UI-SHELL-THEME-1/commands/domain-services.json | 657d36817 | c00ef5b8ce38b89f7e4711ccb543d087732d16419b995bafa4db3d66d9b76b7a | SOURCE_PIN |
| M3-src | AC4/AC5 | verification/UI-SHELL-THEME-1/commands/integration-results.json | 657d36817 | 7aa5464c72c67d4a632e3fb69ab1633157cb618575dfc002355fee6cf05c6b72 | SOURCE_PIN |
| M4-src | AC4/AC5 | verification/UI-SHELL-THEME-1/commands/not-supported-typed-errors.json | 657d36817 | 3ee273a43241e135e1fed39713cfd0aa9051618074d19b15ead1d03b1f43c4c6 | SOURCE_PIN |
| M5-src | AC4/AC5 | verification/UI-SHELL-THEME-1/commands/parity-contract.json | 657d36817 | 1a188fd7af08bde50dace142f22ac4e5208bec466458b129b6c4e679f6aec962 | SOURCE_PIN |
| M6-src | AC4/AC5 | verification/UI-SHELL-THEME-1/diagnostics/missing-exe.json | 657d36817 | 4594512db61c9500844d52d13c3b289c0322cdfed7dc471e8f3a1eac425391dd | SOURCE_PIN |
| M7-src | AC4/AC5 | verification/UI-SHELL-THEME-1/diagnostics/request-timeout.json | 657d36817 | d92e4e444d02eda85d8f361a1d140e43d818429a18ea7c3244dc82df40d76269 | SOURCE_PIN |
| M8-src | AC4/AC5 | verification/UI-SHELL-THEME-1/diagnostics/spawn-failed.json | 657d36817 | d328eb1713bbede1e76649b4474c555dfbde7c72e00736d1828a2118afc6760b | SOURCE_PIN |
| M9-src | AC4/AC5 | verification/UI-SHELL-THEME-1/diagnostics/startup-timeout.json | 657d36817 | 95a65b02f59bd9d5259d3fe0f81839c99d6ba872c7461c0710eff8c9e2d4dbf7 | SOURCE_PIN |
| M10-src | AC4/AC5 | verification/UI-SHELL-THEME-1/host/runtime-chinese-roundtrip.json | 657d36817 | 344024d1ddb450ab1e3e32b328208c909b4405def1077f867f458e04c7151b28 | SOURCE_PIN |
| M11-src | AC4/AC5 | verification/UI-SHELL-THEME-1/host/runtime-missing-sidecar.json | 657d36817 | 294565828007d46dca8cba7ce0f2705cf89cb7e20f55d45e3dbb0c68420ae74e | SOURCE_PIN |
| M12-src | AC4/AC5 | verification/UI-SHELL-THEME-1/host/runtime-readonly.json | 657d36817 | 855710ca4f5b6c4e61e705f50c735781ec1b496fd93ff15bb35f8b5c8f954790 | SOURCE_PIN |
| M13-src | AC4/AC5 | verification/UI-SHELL-THEME-1/host/second-instance.json | 657d36817 | 0ae8bbfcfaa510a10f42733386bf84337c2edeaf89f98641db16dd926d7c8594 | SOURCE_PIN |
| M14-src | AC4/AC5 | verification/UI-SHELL-THEME-1/host-logs/runtime-legacy-running/core_service.stderr.log | 657d36817 | 96b7ece81334916ef4f0aad359637618b6e1e0ce1224c4c84319051487165681 | SOURCE_PIN |
| M15-src | AC4/AC5 | verification/UI-SHELL-THEME-1/host-logs/runtime-legacy-running/host_bridge.stderr.log | 657d36817 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| M16-src | AC4/AC5 | verification/UI-SHELL-THEME-1/host-logs/runtime-legacy-running/host.log | 657d36817 | e3893dde09cf3f6accefc8eb30063c529f6d4b119b2d34de2ad39a3701c1263e | SOURCE_PIN |
| M17-src | AC4/AC5 | verification/UI-SHELL-THEME-1/host-logs/runtime-legacy-running/wire/core-service.ndjson | 657d36817 | bceca66c04cd3f4867cbd559cd3b3ca93170ba5ca48c5de1605219c4075b16fc | SOURCE_PIN |
| M18-src | AC4/AC5 | verification/UI-SHELL-THEME-1/host-logs/runtime-legacy-running/wire/host-bridge.ndjson | 657d36817 | a2dd3836b06e2323d83e602d6c758b768d57203d4a698adb96e2d63d4f648737 | SOURCE_PIN |
| M19-src | AC4/AC5 | verification/UI-SHELL-THEME-1/host-logs/runtime-missing-sidecar/host.log | 657d36817 | d4a35cdc95aab8ef93989b780e2f547d1d279020071f8bec8d54d9f17db8c12d | SOURCE_PIN |
| M20-src | AC4/AC5 | verification/UI-SHELL-THEME-1/host-logs/runtime-parity-roundtrip/core_service.stderr.log | 657d36817 | 4928498218e9b1d01e8ab3a8f72e9c5b10848507bbe6fd80d1b4e004ac7a2fc4 | SOURCE_PIN |
| M21-src | AC4/AC5 | verification/UI-SHELL-THEME-1/host-logs/runtime-parity-roundtrip/host_bridge.stderr.log | 657d36817 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| M22-src | AC4/AC5 | verification/UI-SHELL-THEME-1/host-logs/runtime-parity-roundtrip/host.log | 657d36817 | 29038763ec977dfe542e46ab505c3e681347cfdbb22d8039d5cfebf80ba3a747 | SOURCE_PIN |
| M23-src | AC4/AC5 | verification/UI-SHELL-THEME-1/host-logs/runtime-parity-roundtrip/wire/core-service.ndjson | 657d36817 | bf421260f41c3634f24f080384010254353cffe918ce981a546654c4516986a1 | SOURCE_PIN |
| M24-src | AC4/AC5 | verification/UI-SHELL-THEME-1/host-logs/runtime-parity-roundtrip/wire/host-bridge.ndjson | 657d36817 | 60d0e2bbb2bb6b9aa95432b38d44c751c8cf41965eb5af4fea51c8211988c1dc | SOURCE_PIN |
| M25-src | AC4/AC5 | verification/UI-SHELL-THEME-1/host-logs/runtime-readonly/core_service.stderr.log | 657d36817 | 60057949108885096c31a8230491e5c6965ebb924f295763f5e871477987dead | SOURCE_PIN |
| M26-src | AC4/AC5 | verification/UI-SHELL-THEME-1/host-logs/runtime-readonly/host_bridge.stderr.log | 657d36817 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| M27-src | AC4/AC5 | verification/UI-SHELL-THEME-1/host-logs/runtime-readonly/host.log | 657d36817 | 7a990ddcf6b8e2de776537ea1d89d1ba468c8cdafbf089da1fd37b50e74e3119 | SOURCE_PIN |
| M28-src | AC4/AC5 | verification/UI-SHELL-THEME-1/host-logs/runtime-readonly/wire/core-service.ndjson | 657d36817 | 433484291f6964421d3c72225302f43606a835dd75d8301bde8abb9fec03080a | SOURCE_PIN |
| M29-src | AC4/AC5 | verification/UI-SHELL-THEME-1/host-logs/runtime-readonly/wire/host-bridge.ndjson | 657d36817 | f8411cdf8b159638884f6f77a211ff0314d4c4b2d5ed3a02bcffe07d2cd5beb3 | SOURCE_PIN |
| M30-src | AC4/AC5 | verification/UI-SHELL-THEME-1/host-logs/runtime-second-instance/host.log | 657d36817 | 9f138f0b71e3cfc9b123c0128f15552105b7ef7c74091686793ee1d0b2dce4d7 | SOURCE_PIN |
| M31-src | AC4/AC5 | verification/UI-SHELL-THEME-1/legacy-shell/detected.json | 657d36817 | 4d5523255a4ca0c8b54a2afa54e1a804cc93492f88131b30250a7dfb7afeec76 | SOURCE_PIN |
| M32-src | AC4/AC5 | verification/UI-SHELL-THEME-1/legacy-shell/runtime-readonly.json | 657d36817 | ef4301465315daf4a7edef6d70b66512fbcba9db5277c8cecc549fc59fdd468f | SOURCE_PIN |
| M33-src | AC4/AC5 | verification/UI-SHELL-THEME-1/logs/bridge-errors/host_bridge.stderr.log | 657d36817 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| M34-src | AC4/AC5 | verification/UI-SHELL-THEME-1/logs/bridge-lifecycle/host_bridge.stderr.log | 657d36817 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| M35-src | AC4/AC5 | verification/UI-SHELL-THEME-1/logs/bridge-wire/host_bridge.stderr.log | 657d36817 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| M36-src | AC4/AC5 | verification/UI-SHELL-THEME-1/logs/commands-chinese/core_service.stderr.log | 657d36817 | 3723e02423fffe1c49d1528d1c82d3802fd63ceb7f4445d6ba659c47b96359a1 | SOURCE_PIN |
| M37-src | AC4/AC5 | verification/UI-SHELL-THEME-1/logs/commands-chinese/host_bridge.stderr.log | 657d36817 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| M38-src | AC4/AC5 | verification/UI-SHELL-THEME-1/logs/commands-domains/core_service.stderr.log | 657d36817 | 45fe727e1afd56f12c3fb5ddb1fedd9112f11e72800d6e96da377ade6472e09d | SOURCE_PIN |
| M39-src | AC4/AC5 | verification/UI-SHELL-THEME-1/logs/commands-domains/host_bridge.stderr.log | 657d36817 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| M40-src | AC4/AC5 | verification/UI-SHELL-THEME-1/logs/commands-integration/core_service.stderr.log | 657d36817 | f02a1efff062fb6aa1ed6e134532cdff383bf7a40856dfee6f56786917d48543 | SOURCE_PIN |
| M41-src | AC4/AC5 | verification/UI-SHELL-THEME-1/logs/commands-integration/host_bridge.stderr.log | 657d36817 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| M42-src | AC4/AC5 | verification/UI-SHELL-THEME-1/logs/commands-not-supported/core_service.stderr.log | 657d36817 | 13a101dab8fa2ad96368738a63c9c765cdd3287f0c1af9798838f8dc857805cc | SOURCE_PIN |
| M43-src | AC4/AC5 | verification/UI-SHELL-THEME-1/logs/commands-not-supported/host_bridge.stderr.log | 657d36817 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| M44-src | AC4/AC5 | verification/UI-SHELL-THEME-1/logs/core-chinese/core_service.stderr.log | 657d36817 | 6565081e6710f0710fb5ae306ff04df36d2fb7c7299d31822dbcb02402583652 | SOURCE_PIN |
| M45-src | AC4/AC5 | verification/UI-SHELL-THEME-1/logs/core-ping/core_service.stderr.log | 657d36817 | 0e8cb3a2eb04122ce1b7abae2a644c58eaccc1f52322b94876e8e6da2c8a3af3 | SOURCE_PIN |
| M46-src | AC4/AC5 | verification/UI-SHELL-THEME-1/logs/core-raw-utf8/core_service.stderr.log | 657d36817 | 367e1b0d334400707768b60e6c40a5dbf44a35bdd5ed881feb7ac3eed8be4738 | SOURCE_PIN |
| M47-src | AC4/AC5 | verification/UI-SHELL-THEME-1/logs/core-wire-shape/core_service.stderr.log | 657d36817 | dc942e96f561a74e5b7a5994c8ea126ae96c9a0ff8e1f6a11b0ffb3f15af2ae1 | SOURCE_PIN |
| M48-src | AC4/AC5 | verification/UI-SHELL-THEME-1/logs/failure-request-timeout/fake.stderr.log | 657d36817 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| M49-src | AC4/AC5 | verification/UI-SHELL-THEME-1/logs/failure-startup-timeout/core_service.stderr.log | 657d36817 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| M50-src | AC4/AC5 | verification/UI-SHELL-THEME-1/wire/bridge-errors.ndjson | 657d36817 | 960d8866ef3cc87b79a549ae868f9a8e0dec455ba0e72da752526b2affbe885d | SOURCE_PIN |
| M51-src | AC4/AC5 | verification/UI-SHELL-THEME-1/wire/bridge-lifecycle.ndjson | 657d36817 | 89563585214f36533f953e0c27b61e769c57140d8dbd0ee3843a865c3f6770b0 | SOURCE_PIN |
| M52-src | AC4/AC5 | verification/UI-SHELL-THEME-1/wire/bridge-wire.ndjson | 657d36817 | 9a99ce071b16b209db7c2fc254380118e137271f80b752e315f6f262125df175 | SOURCE_PIN |
| M53-src | AC4/AC5 | verification/UI-SHELL-THEME-1/wire/commands-chinese-core-service.ndjson | 657d36817 | d14233e62c746ce8955fd84240b0e90d72970738ad8a786dd3e6d59a437aa314 | SOURCE_PIN |
| M54-src | AC4/AC5 | verification/UI-SHELL-THEME-1/wire/commands-chinese-host-bridge.ndjson | 657d36817 | 651c11788e79e59b65b3ff962c7ffba718e0a0c7c4d6729ea157a13e86858f2c | SOURCE_PIN |
| M55-src | AC4/AC5 | verification/UI-SHELL-THEME-1/wire/commands-domains-core-service.ndjson | 657d36817 | ba68360e4d7c5871eab6b4a49c1feb75d21fd2bd2e5a892a0c963adb2673d001 | SOURCE_PIN |
| M56-src | AC4/AC5 | verification/UI-SHELL-THEME-1/wire/commands-domains-host-bridge.ndjson | 657d36817 | 0b3c7c107699fcf32a888f080aea8e4010e7f2fa14f1e2ac8be960214a8acf89 | SOURCE_PIN |
| M57-src | AC4/AC5 | verification/UI-SHELL-THEME-1/wire/commands-integration-core-service.ndjson | 657d36817 | 14423961b298eb9349e138902fabff87f720217a37254e62dd14983834a86df6 | SOURCE_PIN |
| M58-src | AC4/AC5 | verification/UI-SHELL-THEME-1/wire/commands-integration-host-bridge.ndjson | 657d36817 | c6b8b4ae64fbff2b848658cbf305e0f054a664cc3264252dfd8fedc661dda8a4 | SOURCE_PIN |
| M59-src | AC4/AC5 | verification/UI-SHELL-THEME-1/wire/commands-not-supported-core-service.ndjson | 657d36817 | 7e236e64099e8699d7fc61995b6a8c53c3bde5af5d9ff9747b115985f3e3bd0f | SOURCE_PIN |
| M60-src | AC4/AC5 | verification/UI-SHELL-THEME-1/wire/commands-not-supported-host-bridge.ndjson | 657d36817 | c6612d122e771b7b421019a3aa701ef6391475e7c76ba0f080b0ef159817a9a0 | SOURCE_PIN |
| M61-src | AC4/AC5 | verification/UI-SHELL-THEME-1/wire/core-chinese-roundtrip.json | 657d36817 | a2c15b142615e6cb3cc92e0404052eb3b32de583b792662c508cc4361b929f97 | SOURCE_PIN |
| M62-src | AC4/AC5 | verification/UI-SHELL-THEME-1/wire/core-chinese.ndjson | 657d36817 | f1ce6c8c085e510742cd570eb71850fc43dd74d5922cb358c17358aab9625716 | SOURCE_PIN |
| M63-src | AC4/AC5 | verification/UI-SHELL-THEME-1/wire/core-ping.json | 657d36817 | b40d4d0d8f1928a8670dc6ffdfb82c11ded1667ce726b0fda55742c4f1f56b4b | SOURCE_PIN |
| M64-src | AC4/AC5 | verification/UI-SHELL-THEME-1/wire/core-ping.ndjson | 657d36817 | ca7c45b05cc3a9f58e1168827c6d8b6df6b81b204cb41bc2bd5e6cdf7c8970e4 | SOURCE_PIN |
| M65-src | AC4/AC5 | verification/UI-SHELL-THEME-1/wire/core-raw-utf8-negative.json | 657d36817 | 611962501be106ce97c22a0c6cc3ac7c157d7c691c1378eb44b25834d64ca084 | SOURCE_PIN |
| M66-src | AC4/AC5 | verification/UI-SHELL-THEME-1/wire/core-raw-utf8.ndjson | 657d36817 | 6d661dc93419482ef7b10ff6ed08b081accf21a9e22eb4aa717f45845bc43065 | SOURCE_PIN |
| M67-src | AC4/AC5 | verification/UI-SHELL-THEME-1/wire/core-wire-shape.json | 657d36817 | 8992aaa6124a7f2b40be1eae955964d9496c23a977d5644e880650c23c19dc1c | SOURCE_PIN |
| M68-src | AC4/AC5 | verification/UI-SHELL-THEME-1/wire/core-wire-shape.ndjson | 657d36817 | 17f086387cc1db07b9f04e8f7054b78a8e39219ce1a6a9ba235e1579c3ca47a8 | SOURCE_PIN |
| M69-src | AC4/AC5 | verification/UI-SHELL-THEME-1/wire/host-bridge-errors.json | 657d36817 | e845d29777d0080795121748aebd2732f6f141f3feaaaf536c81fe2b41386c3e | SOURCE_PIN |
| M70-src | AC4/AC5 | verification/UI-SHELL-THEME-1/wire/host-bridge-lifecycle.json | 657d36817 | bda6cd395953070b764be54cc57ba3344571f348ae9abbb12e85fb2a5b0e21ba | SOURCE_PIN |
## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/UI-SHELL-THEME-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/UI-SHELL-THEME-1 | 1d622ac6d000d10b8155d11cffeaeda497793cc5f1d6443c2434bc152e13654b | 待关闭时核 |

## Closeout Record

- Closeout date / DSH：待 DSH 复核后填写（in_review）。
- canonical_evidence_status：`pinned`（E1–E11，commit 28cd1324ca）。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：已更新 STATUS/PLAN/LEDGER。
## Review（DSH 集成复核，2026-10-27）— PASS（附范围裁决）

- 单命令验收（不带 -CanonicalEvidence）：scripts/test.ps1 → **74/74 passed / 0 skipped**；裸跑 58 passed/16 skipped 有原因。
- AC2 实测：6 套 ThemePack、3 套×10 次热切 **p95 2.215ms**（≤100ms 门禁，优于 spike 3.74ms）；reduced-motion 归零；色残留断言通过。
- AC3：书卡列数 VM 计算（1400→7）、空态/无结果态、hover/详情入口齐全（headless UI 断言）。
- AC4 范围裁决：13 条命令接线 + S2 的 50 NS 中登记 **8 条 PLANNED**（S3-A/B/C，0/8 完成）——本卡以"骨架 + 台账 + 页面标注原因"收口，8 条 NS 接线随 S4/S5 批次推进，不阻塞 S4。
- 遗留：真机 Mica/无控制台未重新 publish 验证（打包参数同 S1/S2，S5 安装包 Gate 统一复验）；截图证据以资源色差分替代 Skia 截图（可接受）。
- 集成：657d36817；范围仅 pps/desktop-avalonia/** + 证据 + 文档 + 一处 S2 证据目录纠偏（与 closeout 逐字节一致）。
