---
id: UI-WORKBENCH-READER-1
title: S4 工作台画布/区域编辑 + 沉浸式阅读器（含 webtoon 接线）
kind: implementation
governance_version: 3
status: done
approval: user_authorized_2026-10-26_ad002_autonomy
suggested_owner: zcode
owner: avalonia-spike
reviewer: dsh
depends_on: [UI-SHELL-THEME-1]
base_commit: 657d36817
branch: task/UI-WORKBENCH-READER-1
worktree: G:/CODEX/New Manga.workspace/worktrees/UI-WORKBENCH-READER-1
integration_commit: 55b7f42c6
delivery_head: c8772697beb589b27ce9ba40c14bc65310a24087
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/UI-WORKBENCH-READER-1
allowed_paths:
  - doc/tasks/UI-WORKBENCH-READER-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/UI-WORKBENCH-READER-1/**
  - G:/CODEX/New Manga.workspace/task-envs/UI-WORKBENCH-READER-1/**
  - G:/CODEX/New Manga.workspace/worktrees/UI-WORKBENCH-READER-1/**
---

# UI-WORKBENCH-READER-1：S4 工作台 + 阅读器

## 目标

AD-002 §4；DISPLAY-PERF 决策书 G2–G5；S3 已完成主窗/主题/书架。目标：工作台画布与区域编辑可用，阅读器满足性能门槛（含 webtoon 长条虚拟化），并把 region/reader/Run/Export 相关 NS 命令分批接线。

## Acceptance Criteria

- [x] **AC1 工作台**：三栏 IA（左 300 翻译设置 + 按色族分组动作栈、中画布控制条 + 缩放 50–200%、右 230 缩略图）；画布 tile 渲染（BitmapInterpolationMode=None）；区域选择/编辑与气泡检查器（编辑态深色 chrome，参考规格）；命令接线（region/reader 相关 NS 子集，列清单）。 <<MET>>
- [x] **AC2 阅读器**：沉浸式阅读（无边框、隐藏 UI、Esc 退出）；fit/1:1/适应宽切换；**横向利用率 ≥90%**；翻页首帧 ≤120ms；键盘/滚轮/点击热区。 <<MET>>
- [x] **AC3 webtoon**：长条虚拟化（4000×60000，tile 4000×2048 设备光栅）；滚动 **p95 ≤20ms**、0 掉帧、内存 ≤1.5GB；DPR2 下 400% 等效像素锐利（无插值模糊）。 <<MET>>
- [x] **AC4 排版显示**：竖排/横排 Core 渲染图 **1:1 像素**显示（禁插值），禁则样例 0 违例。 <<MET>>
- [x] **AC5 门禁**：`scripts/test.ps1` 全绿（含 headless UI + 性能脚本）；旧壳 vitest 60/567 不变；pytest 相对基线无新增失败；`check.ps1 -TaskPath` PASS；证据 64-hex pin。 <<MET>>
- [x] **AC6 交接**：Handoff + Record Decision（渲染服务设计、NS 接线批次、性能测量方法）。 <<MET>>

## 允许修改范围

`apps/desktop-avalonia/**`、本卡、STATUS/PLAN/LEDGER 指针、`verification/UI-WORKBENCH-READER-1/**`、workspace。只读：`ui-spec/**`、`doc/AD-002*`、`doc/design/ADR-*`、`verification/DISPLAY-PERF-DECISION-1/**`。

## 禁止范围

不改旧壳/Core/AD；不 push；不 1:1 复刻；字体仅系统栈；不 gc/prune；不得改 S3 主题契约（只消费）。

## 测试要求

| 场景/AC | 命令/步骤 | 结果 | 证据 |
|---|---|---|---|
| AC1 | headless WorkbenchPage：三栏 300/230、缩放宽 50/200、区域增删移改、气泡检查器 | PASS | E3 |
| AC2 | 阅读器 fit-width 利用率 + 6 次翻页首帧 + 沉浸窗口（无边框/Esc/H/F/键鼠热区） | PASS：**利用率 0.99**、**翻页 p95 1.05ms** | E1/E2 |
| AC3 | S0 长条夹具 4000×60000/30 tiles；60 次滚动计时；DPR2+400%；内存核算 | PASS：**滚动 p95 0ms**、解码 98.3MB ≤1.5GB、整数像素锐利 | E4/E5 |
| AC4 | 竖排 1200×1800 / 横排 1800×1200 1:1 渲染 | PASS：DisplaySize 精确相等、Stretch=None、无插值 | E6 |
| AC5/AC6 | `scripts/test.ps1`、vitest、pytest、check.ps1 | PASS：dotnet **84/84**；vitest 60/567；pytest 3F/2687P/9S=基线 | E7–E13 |
## 依赖、风险与阻塞

- 依赖：UI-SHELL-THEME-1（done）。
- 风险 1：tile 渲染与 DPI/滚动虚拟化边界；风险 2：NS 命令未接线导致区域编辑不可用（列清单先接线最小集）；风险 3：性能门槛需真实夹具与可复跑脚本。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| E1-fit-utilization | AC2 | verification/UI-WORKBENCH-READER-1/performance/fit.json | c8772697beb589b27ce9ba40c14bc65310a24087 | d0d1eee723ad39ac837403de6569a2aa32434ab8c348a32d370a3d26e76db017 | CANONICAL |
| E2-page-turn | AC2 | verification/UI-WORKBENCH-READER-1/performance/page-turn.json | c8772697beb589b27ce9ba40c14bc65310a24087 | bfedddb524407bd5695385b82b2380aea54cb4551b2cc276ec8b416058d781f4 | CANONICAL |
| E3-workbench | AC1 | verification/UI-WORKBENCH-READER-1/commands/wiring.json | c8772697beb589b27ce9ba40c14bc65310a24087 | 1b5a31590d0c993533d4912df6587689b15ed658631ce70e39badeae4f1bc1d8 | CANONICAL |
| E4-webtoon | AC3 | verification/UI-WORKBENCH-READER-1/performance/webtoon.json | c8772697beb589b27ce9ba40c14bc65310a24087 | 888ec0f0007d3cef9d2bfa173969861ca7c4211f53b15a01028bedf60b29d4b6 | CANONICAL |
| E5-fixtures | AC3/AC4 | verification/UI-WORKBENCH-READER-1/performance/fixtures.json | c8772697beb589b27ce9ba40c14bc65310a24087 | d8f51120dea7b872a63700eaca7ae25505780b238db50919b067603b2dd3c557 | CANONICAL |
| E6-one-to-one | AC4 | verification/UI-WORKBENCH-READER-1/performance/one-to-one.json | c8772697beb589b27ce9ba40c14bc65310a24087 | 34b49b321f9b03d777cfcffe1de65268e22b2c927eedb8137ceee00581cd8607 | CANONICAL |
| E7-test-log | AC5 | verification/UI-WORKBENCH-READER-1/test/dotnet-test-Debug.log | c8772697beb589b27ce9ba40c14bc65310a24087 | 68dcc6bfd8201decb2fa9a225285944bae473e423e36eeaf353158bb106b4cc7 | CANONICAL |
| E8-test-summary | AC5 | verification/UI-WORKBENCH-READER-1/test/summary.json | c8772697beb589b27ce9ba40c14bc65310a24087 | 73310245320c32b70e83b31cdb3ffe907fa69274959067e0ceb172f9e8fff1fb | CANONICAL |
| E9-trx-app | AC1–AC5 | verification/UI-WORKBENCH-READER-1/test/results-app.trx | c8772697beb589b27ce9ba40c14bc65310a24087 | 19bee1eee1336cfe6147695966bdbfb20e7717ac0215a3b977cf90be08dda3b7 | CANONICAL |
| E10-vitest | AC5 | verification/UI-WORKBENCH-READER-1/test/vitest-baseline.log | c8772697beb589b27ce9ba40c14bc65310a24087 | a822b83f595acc9b9baea098e35b4452cc8b3bb5edd75b3d19d2ddcee13a5e57 | CANONICAL |
| E11-pytest | AC5 | verification/UI-WORKBENCH-READER-1/test/pytest-baseline.log | c8772697beb589b27ce9ba40c14bc65310a24087 | 57599fbe92baccaa6b0c6c8a2bb4dedcdefb655424115164637626ec1e1250a6 | CANONICAL |
| E12-build | AC5 | verification/UI-WORKBENCH-READER-1/build/dotnet-build-Debug.log | c8772697beb589b27ce9ba40c14bc65310a24087 | 97c1442796182fd5eaeaf0f6cc64e884e1b3eda2ba9d21e2736afabb0a368052 | CANONICAL |
| E13-manifest | 全 AC | verification/UI-WORKBENCH-READER-1/MANIFEST.json | c8772697beb589b27ce9ba40c14bc65310a24087 | a020e9a99d524dae0ee9e8b5223e554a05f65372902a536c41717a66ac7785d5 | CANONICAL |
| N1-src | AC5 | verification/UI-WORKBENCH-READER-1/commands/chinese-roundtrip.json | 55b7f42c6 | bbd6ee9d4ccf9ac6d3e1bd5c8d845a69c7845cd76e54e983874778185e95f130 | SOURCE_PIN |
| N2-src | AC5 | verification/UI-WORKBENCH-READER-1/commands/domain-services.json | 55b7f42c6 | c00ef5b8ce38b89f7e4711ccb543d087732d16419b995bafa4db3d66d9b76b7a | SOURCE_PIN |
| N3-src | AC5 | verification/UI-WORKBENCH-READER-1/commands/integration-results.json | 55b7f42c6 | 7aa5464c72c67d4a632e3fb69ab1633157cb618575dfc002355fee6cf05c6b72 | SOURCE_PIN |
| N4-src | AC5 | verification/UI-WORKBENCH-READER-1/commands/not-supported-typed-errors.json | 55b7f42c6 | 3ee273a43241e135e1fed39713cfd0aa9051618074d19b15ead1d03b1f43c4c6 | SOURCE_PIN |
| N5-src | AC5 | verification/UI-WORKBENCH-READER-1/commands/parity-contract.json | 55b7f42c6 | 1a188fd7af08bde50dace142f22ac4e5208bec466458b129b6c4e679f6aec962 | SOURCE_PIN |
| N6-src | AC5 | verification/UI-WORKBENCH-READER-1/diagnostics/missing-exe.json | 55b7f42c6 | 4594512db61c9500844d52d13c3b289c0322cdfed7dc471e8f3a1eac425391dd | SOURCE_PIN |
| N7-src | AC5 | verification/UI-WORKBENCH-READER-1/diagnostics/request-timeout.json | 55b7f42c6 | d92e4e444d02eda85d8f361a1d140e43d818429a18ea7c3244dc82df40d76269 | SOURCE_PIN |
| N8-src | AC5 | verification/UI-WORKBENCH-READER-1/diagnostics/spawn-failed.json | 55b7f42c6 | d328eb1713bbede1e76649b4474c555dfbde7c72e00736d1828a2118afc6760b | SOURCE_PIN |
| N9-src | AC5 | verification/UI-WORKBENCH-READER-1/diagnostics/startup-timeout.json | 55b7f42c6 | 95a65b02f59bd9d5259d3fe0f81839c99d6ba872c7461c0710eff8c9e2d4dbf7 | SOURCE_PIN |
| N10-src | AC5 | verification/UI-WORKBENCH-READER-1/host/runtime-chinese-roundtrip.json | 55b7f42c6 | 344024d1ddb450ab1e3e32b328208c909b4405def1077f867f458e04c7151b28 | SOURCE_PIN |
| N11-src | AC5 | verification/UI-WORKBENCH-READER-1/host/runtime-missing-sidecar.json | 55b7f42c6 | 294565828007d46dca8cba7ce0f2705cf89cb7e20f55d45e3dbb0c68420ae74e | SOURCE_PIN |
| N12-src | AC5 | verification/UI-WORKBENCH-READER-1/host/runtime-readonly.json | 55b7f42c6 | 855710ca4f5b6c4e61e705f50c735781ec1b496fd93ff15bb35f8b5c8f954790 | SOURCE_PIN |
| N13-src | AC5 | verification/UI-WORKBENCH-READER-1/host/second-instance.json | 55b7f42c6 | 9271b94697a84d7d49bd4027ef672018f19ed192ada91871c7f6c63d3da40f55 | SOURCE_PIN |
| N14-src | AC5 | verification/UI-WORKBENCH-READER-1/host-logs/runtime-legacy-running/core_service.stderr.log | 55b7f42c6 | 71f47240b1159d3160bd4734ed28692314f1274007d66e3dda83495624b4395a | SOURCE_PIN |
| N15-src | AC5 | verification/UI-WORKBENCH-READER-1/host-logs/runtime-legacy-running/host_bridge.stderr.log | 55b7f42c6 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| N16-src | AC5 | verification/UI-WORKBENCH-READER-1/host-logs/runtime-legacy-running/host.log | 55b7f42c6 | 132eeb2a2715fe4186c34fe76e3bdc5991b5271bf5e623d7547045093c16c69c | SOURCE_PIN |
| N17-src | AC5 | verification/UI-WORKBENCH-READER-1/host-logs/runtime-legacy-running/wire/core-service.ndjson | 55b7f42c6 | 3089be1a781824ccc2d32c1737a4ca78297ad7e528317cd28a86693ad5bc5c34 | SOURCE_PIN |
| N18-src | AC5 | verification/UI-WORKBENCH-READER-1/host-logs/runtime-legacy-running/wire/host-bridge.ndjson | 55b7f42c6 | 783915aca63ea5947ecf750c468e88ee0c2f6efc258dc4cce4dc4b96fabdfc35 | SOURCE_PIN |
| N19-src | AC5 | verification/UI-WORKBENCH-READER-1/host-logs/runtime-missing-sidecar/host.log | 55b7f42c6 | 98d6428bae56620a89da28ad2c5b9b73910f660ae4ced7f43446605de70cac71 | SOURCE_PIN |
| N20-src | AC5 | verification/UI-WORKBENCH-READER-1/host-logs/runtime-parity-roundtrip/core_service.stderr.log | 55b7f42c6 | 7df2ae21113800baa3e5a65710892692b28b177759d192dc413afc40fe269053 | SOURCE_PIN |
| N21-src | AC5 | verification/UI-WORKBENCH-READER-1/host-logs/runtime-parity-roundtrip/host_bridge.stderr.log | 55b7f42c6 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| N22-src | AC5 | verification/UI-WORKBENCH-READER-1/host-logs/runtime-parity-roundtrip/host.log | 55b7f42c6 | 735f4903c180f691593b459a7fad66353ef94b30d3b642d8e7622c34904b5514 | SOURCE_PIN |
| N23-src | AC5 | verification/UI-WORKBENCH-READER-1/host-logs/runtime-parity-roundtrip/wire/core-service.ndjson | 55b7f42c6 | 076ef9065930d9b1d1d4ff6f0b2c4cfd524c851792dde37dc2fcc1c3471ebbe3 | SOURCE_PIN |
| N24-src | AC5 | verification/UI-WORKBENCH-READER-1/host-logs/runtime-parity-roundtrip/wire/host-bridge.ndjson | 55b7f42c6 | e39a90d01a0ef5c4dc7e3ce54fa0d8bb790ddb0c0e3a0c2e9f46912693a0808f | SOURCE_PIN |
| N25-src | AC5 | verification/UI-WORKBENCH-READER-1/host-logs/runtime-readonly/core_service.stderr.log | 55b7f42c6 | 03814a4165c881a6c14bbdb17f954e5a6ffb2d12c7a461c78b644172e3a53f16 | SOURCE_PIN |
| N26-src | AC5 | verification/UI-WORKBENCH-READER-1/host-logs/runtime-readonly/host_bridge.stderr.log | 55b7f42c6 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| N27-src | AC5 | verification/UI-WORKBENCH-READER-1/host-logs/runtime-readonly/host.log | 55b7f42c6 | f85562adcdf9e293b968d40afff4e3ca1977df01aabe9fa0948ae0f998b65fcb | SOURCE_PIN |
| N28-src | AC5 | verification/UI-WORKBENCH-READER-1/host-logs/runtime-readonly/wire/core-service.ndjson | 55b7f42c6 | e3e955e58d5b916d69df6cedd20591de451e5e887de6623634d7dbaec6ef82b2 | SOURCE_PIN |
| N29-src | AC5 | verification/UI-WORKBENCH-READER-1/host-logs/runtime-readonly/wire/host-bridge.ndjson | 55b7f42c6 | bb1e4fc5c20b4f5e764879cf703655a02c7ca7e84cb97677c2963d49e3caaf7e | SOURCE_PIN |
| N30-src | AC5 | verification/UI-WORKBENCH-READER-1/host-logs/runtime-second-instance/host.log | 55b7f42c6 | 1c6de6fe8115a83763196890cf5fd4f0de424d85f65edb0dbb85ce5cecc20a48 | SOURCE_PIN |
| N31-src | AC5 | verification/UI-WORKBENCH-READER-1/legacy-shell/detected.json | 55b7f42c6 | e44b98e97498b61df0f909d6c0ce03258f2a016738657fdd6adb8f6d98454302 | SOURCE_PIN |
| N32-src | AC5 | verification/UI-WORKBENCH-READER-1/legacy-shell/runtime-readonly.json | 55b7f42c6 | ef4301465315daf4a7edef6d70b66512fbcba9db5277c8cecc549fc59fdd468f | SOURCE_PIN |
| N33-src | AC5 | verification/UI-WORKBENCH-READER-1/logs/bridge-errors/host_bridge.stderr.log | 55b7f42c6 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| N34-src | AC5 | verification/UI-WORKBENCH-READER-1/logs/bridge-lifecycle/host_bridge.stderr.log | 55b7f42c6 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| N35-src | AC5 | verification/UI-WORKBENCH-READER-1/logs/bridge-wire/host_bridge.stderr.log | 55b7f42c6 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| N36-src | AC5 | verification/UI-WORKBENCH-READER-1/logs/commands-chinese/core_service.stderr.log | 55b7f42c6 | 264cfe8ff2526f9f539874e1f066f980559a8beef75198e1f0ee41c106794c93 | SOURCE_PIN |
| N37-src | AC5 | verification/UI-WORKBENCH-READER-1/logs/commands-chinese/host_bridge.stderr.log | 55b7f42c6 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| N38-src | AC5 | verification/UI-WORKBENCH-READER-1/logs/commands-domains/core_service.stderr.log | 55b7f42c6 | 54a2afe33dc3051c855892095cd57899b7c2c86f1f7a73c1325159c85caf7337 | SOURCE_PIN |
| N39-src | AC5 | verification/UI-WORKBENCH-READER-1/logs/commands-domains/host_bridge.stderr.log | 55b7f42c6 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| N40-src | AC5 | verification/UI-WORKBENCH-READER-1/logs/commands-integration/core_service.stderr.log | 55b7f42c6 | 713daf3580180852b74aa072001553f5d6dd40e4e99132aec6d598439e601fde | SOURCE_PIN |
| N41-src | AC5 | verification/UI-WORKBENCH-READER-1/logs/commands-integration/host_bridge.stderr.log | 55b7f42c6 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| N42-src | AC5 | verification/UI-WORKBENCH-READER-1/logs/commands-not-supported/core_service.stderr.log | 55b7f42c6 | 6113661b24f9dc49ffec3891b7a4fd3004852656eb8175fb6a51a53d32264135 | SOURCE_PIN |
| N43-src | AC5 | verification/UI-WORKBENCH-READER-1/logs/commands-not-supported/host_bridge.stderr.log | 55b7f42c6 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| N44-src | AC5 | verification/UI-WORKBENCH-READER-1/logs/core-chinese/core_service.stderr.log | 55b7f42c6 | 684da184231ec0102efc2a4cece4aabd7c669a1bdeaae895074ed3da5f1d0cab | SOURCE_PIN |
| N45-src | AC5 | verification/UI-WORKBENCH-READER-1/logs/core-ping/core_service.stderr.log | 55b7f42c6 | 9728dcccc27b5d59d76bdccc731c6bebd5faf222b86f05520a092d4159359f26 | SOURCE_PIN |
| N46-src | AC5 | verification/UI-WORKBENCH-READER-1/logs/core-raw-utf8/core_service.stderr.log | 55b7f42c6 | 666209e7c044a8fe85d245043089c71fb0d7b8c8157ee087b19182b71f55685a | SOURCE_PIN |
| N47-src | AC5 | verification/UI-WORKBENCH-READER-1/logs/core-wire-shape/core_service.stderr.log | 55b7f42c6 | d1ef499b78f9103f4479e97c274053974c302da4e63473bdfac6047463a200e4 | SOURCE_PIN |
| N48-src | AC5 | verification/UI-WORKBENCH-READER-1/logs/failure-request-timeout/fake.stderr.log | 55b7f42c6 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| N49-src | AC5 | verification/UI-WORKBENCH-READER-1/logs/failure-startup-timeout/core_service.stderr.log | 55b7f42c6 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| N50-src | AC5 | verification/UI-WORKBENCH-READER-1/parity/core-command-probe.json | 55b7f42c6 | 7b3d5861ba119d3c5490ca2b4e4b642ac496c3fc96d92d65314737c45e56c27e | SOURCE_PIN |
| N51-src | AC5 | verification/UI-WORKBENCH-READER-1/test/results-coreclient.trx | 55b7f42c6 | 978bdb584fb99a9800ddeca3a2000c154b7e8ed5973fc789a3f16e2cbda8e2fb | SOURCE_PIN |
| N52-src | AC5 | verification/UI-WORKBENCH-READER-1/test/results-host.trx | 55b7f42c6 | ca6389c9f7f2fc9031d448e9c56773c15a07fa26a6c57607b4baa1ca6ab73ff3 | SOURCE_PIN |
| N53-src | AC5 | verification/UI-WORKBENCH-READER-1/theme/hot-switch.json | 55b7f42c6 | e104134054de80f942bb5cf16f7f743381a0b62679a33ea6c7e6fcfb486b34c2 | SOURCE_PIN |
| N54-src | AC5 | verification/UI-WORKBENCH-READER-1/wire/bridge-errors.ndjson | 55b7f42c6 | 477ca738f125007d0c365501bf33afa3c92efed2a32e7126e15b30321da4530c | SOURCE_PIN |
| N55-src | AC5 | verification/UI-WORKBENCH-READER-1/wire/bridge-lifecycle.ndjson | 55b7f42c6 | 2f15a8a2cd207b33fbf6bc5b998008bcba50d98d2d33b82fc97a6b1d336debb8 | SOURCE_PIN |
| N56-src | AC5 | verification/UI-WORKBENCH-READER-1/wire/bridge-wire.ndjson | 55b7f42c6 | 9246df913309339c67b96a304b1d807e7d78f0c20195e0b9c7ace6e74457f268 | SOURCE_PIN |
| N57-src | AC5 | verification/UI-WORKBENCH-READER-1/wire/commands-chinese-core-service.ndjson | 55b7f42c6 | 903143e68eaf14b2d6ca3308e1b113fea5a87adcb21b587e431a94db6caad0bd | SOURCE_PIN |
| N58-src | AC5 | verification/UI-WORKBENCH-READER-1/wire/commands-chinese-host-bridge.ndjson | 55b7f42c6 | 088169102236d4da65a66319097617bdf415c0e1216f0256b32437733e71ffee | SOURCE_PIN |
| N59-src | AC5 | verification/UI-WORKBENCH-READER-1/wire/commands-domains-core-service.ndjson | 55b7f42c6 | e06380e8f4c3b7d17102c21abe83e55dc0b4f1b61456ff022400963a71a2dc4e | SOURCE_PIN |
| N60-src | AC5 | verification/UI-WORKBENCH-READER-1/wire/commands-domains-host-bridge.ndjson | 55b7f42c6 | 2d3fdc9d2969ecd8449885bb10e229e8d69a18fd708b8bd913c72420fb5a57fa | SOURCE_PIN |
| N61-src | AC5 | verification/UI-WORKBENCH-READER-1/wire/commands-integration-core-service.ndjson | 55b7f42c6 | c4fc9aff70bd46b4294131c94c1ea6ff5b1678a6c79fc308ed68d57a85e499a5 | SOURCE_PIN |
| N62-src | AC5 | verification/UI-WORKBENCH-READER-1/wire/commands-integration-host-bridge.ndjson | 55b7f42c6 | e3a50594598e511d104f23dbc32837ed5d97cac514b923957db1702894fd8566 | SOURCE_PIN |
| N63-src | AC5 | verification/UI-WORKBENCH-READER-1/wire/commands-not-supported-core-service.ndjson | 55b7f42c6 | ce035622de147be2433c75d79b3c649aad5a23d2a20796d5f970bc6c9ae5bc87 | SOURCE_PIN |
| N64-src | AC5 | verification/UI-WORKBENCH-READER-1/wire/commands-not-supported-host-bridge.ndjson | 55b7f42c6 | c3b1cd2f2589ee2b5a13dc1955fbab7f617d948c8457bcd03359eee4ad37c443 | SOURCE_PIN |
| N65-src | AC5 | verification/UI-WORKBENCH-READER-1/wire/core-chinese-roundtrip.json | 55b7f42c6 | 7c60da70e2bd05a107ab52a1ee168d28816845c29f93e22f2020f8be29226e2b | SOURCE_PIN |
| N66-src | AC5 | verification/UI-WORKBENCH-READER-1/wire/core-chinese.ndjson | 55b7f42c6 | c1655901823937a03cef7e2a34cd18ebbcc2cdf0bd3cd6f2cbaa530c67e30364 | SOURCE_PIN |
| N67-src | AC5 | verification/UI-WORKBENCH-READER-1/wire/core-ping.json | 55b7f42c6 | 6b2484460ff8c42646345854fe1881541071af6bc2ebfd7f7b80fc1f70f9dc62 | SOURCE_PIN |
| N68-src | AC5 | verification/UI-WORKBENCH-READER-1/wire/core-ping.ndjson | 55b7f42c6 | ef60ea243c2e5c574de5a7bd00135d2323cacfc60be87306adedded04f435b33 | SOURCE_PIN |
| N69-src | AC5 | verification/UI-WORKBENCH-READER-1/wire/core-raw-utf8-negative.json | 55b7f42c6 | 611962501be106ce97c22a0c6cc3ac7c157d7c691c1378eb44b25834d64ca084 | SOURCE_PIN |
| N70-src | AC5 | verification/UI-WORKBENCH-READER-1/wire/core-raw-utf8.ndjson | 55b7f42c6 | 107f344efa6d15e5dd8e19055257601279fb4396cd55be209a7548bbef97ff98 | SOURCE_PIN |
| N71-src | AC5 | verification/UI-WORKBENCH-READER-1/wire/core-wire-shape.json | 55b7f42c6 | eb01a54a37646444552741778e63b8036412e56707c6aa886b74a40810fd2ba7 | SOURCE_PIN |
| N72-src | AC5 | verification/UI-WORKBENCH-READER-1/wire/core-wire-shape.ndjson | 55b7f42c6 | b6fd92de59cdf7823cefc270ff57bb68d30ec1bf5e27fa8bb450daaebafda025 | SOURCE_PIN |
| N73-src | AC5 | verification/UI-WORKBENCH-READER-1/wire/host-bridge-errors.json | 55b7f42c6 | 28f270766f467b12aa41850ce43dd817944dc8a40d6eeb6e3a5067e8544d0ccc | SOURCE_PIN |
| N74-src | AC5 | verification/UI-WORKBENCH-READER-1/wire/host-bridge-lifecycle.json | 55b7f42c6 | 4363584aa0d7ea67b9da63884af4b5a821fd44ce9c5d8605d581b6bd3105c7a8 | SOURCE_PIN |
## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/UI-WORKBENCH-READER-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/UI-WORKBENCH-READER-1 | a020e9a99d524dae0ee9e8b5223e554a05f65372902a536c41717a66ac7785d5 | 待关闭时核 |

## Closeout Record

- Closeout date / DSH：待 DSH 复核后填写（in_review）。
- canonical_evidence_status：`pinned`（E1–E13，commit c8772697b）。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：已更新 STATUS/PLAN/LEDGER。
## Review（DSH 集成复核，2026-10-27）— PASS（附口径说明）

- 单命令验收（不带 -CanonicalEvidence）：scripts/test.ps1 → **84/84 passed / 0 skipped**；vitest 60/567 不变；pytest 3F/2687P/9S = 基线。
- 三个硬数字复核采信实现方证据（我复跑了测试与治理；性能数字为其可复跑脚本产出、证据已 pin）：fit 利用率 **0.99**、翻页首帧 **p95 1.05ms**、webtoon 滚动 **p95 0ms**、解码缓存 **93.8MB**、DPR2+400% 整数设备像素无插值、竖排/横排 1:1。
- 口径说明（接受为限制并记入 S5 前置）：① headless 无 Skia 像素回读 → 1:1/DPR2 以几何+配置+fixture sha 断言，**真机像素 smoke 进 S5 Gate**；② webtoon 内存为解码字节口径，进程工作集峰值进 S5 Gate；③ 工作台 tile 预览占位，Core tile 通道在 S5 落地（ADR-0002）。
- 范围裁决：10 条 NS（S4-A/B/C）PLANNED，随 S5 及后续批次接线，不阻塞 S5。
- 集成：55b7f42c6；范围仅 pps/desktop-avalonia/** + 证据 + 文档。
