# FEA-06 Canonical Evidence Index

- Base commit: `3c7f311d88b24bde462a61690e15d2c66f8c4683`.
- Implementation head: `7cf305fe2534272dc75295c4644661ddb73221af` (recorded in `doc/tasks/FEA-06.md`).
- Original full regression: **1030 passed / 0 failed / 57 skipped**. After impl-r1 and impl-r2: **1034 passed / 0 failed / 57 skipped**. Skip cause remains missing `NEWMANGA_CORECLIENT_SIDECAR_DIR`; see `verification/FEA-06/skip-analysis.md`.
- Headless page and navigation evidence is simulated; it does not establish native desktop visual behavior. See `verification/FEA-06/uiux/task-result.json` (`PARTIAL`).
- Test suite changes: 12 added Fluent tests relative to the 1022/0/57 baseline (8 initial + 4 impl-r1 rework); impl-r2 extends an existing headless test without changing the count. No existing tests removed or skipped by this task.

| Evidence path | Bytes | SHA-256 |
|---|---:|---|
| `verification/FEA-06/build.log` | 2593 | `a7d6f89bb743f1bd40d46c185344c85d9c6fb2c5bea6940cccebaa38d632ffa0` |
| `verification/FEA-06/component-registry.md` | 7355 | `5dd20bf012c3863bca5700febd896357ec2fe136cc44fcd7ed2e131bcfe58324` |
| `verification/FEA-06/design-system-component-tests.log` | 652 | `5e3532f3b2af9efd01de8a75716f826c10d521a4797cb5ff568d708f52704838` |
| `verification/FEA-06/full-test.log` | 17432 | `be5fda55f2e55135bd5c81f902f9d2bf4b1d6aa10d78abc95b4451222890ad21` |
| `verification/FEA-06/governance-check.log` | 479 | `1141042fda8bdff7f268927511cd243da838b1e13eab4aff08d60fbf5f0b982f` |
| `verification/FEA-06/page-tests.log` | 589 | `1cd942044a0ab41326c9dedc9b9c6f3f1aa99e2f04059a92a14000b959a4439c` |
| `verification/FEA-06/scope-audit.md` | 2604 | `cec04b8135b13549f8c0114b43fe1259b00e5e335538cddccd6166cd8da90ea0` |
| `verification/FEA-06/screens/reader.png` | 26733 | `8533c263c79bd53cefa68a21d2aabe6501556fd62218ebf653b528c9cbec78b2` |
| `verification/FEA-06/screens/settings.png` | 54085 | `fd30b166e30aec7a43e4d82ecd1fefb14dffef3bebe2f5f952e41d45e324a162` |
| `verification/FEA-06/screens/shelf.png` | 32737 | `307f8f6748522d1cdb3226135a3f733961744a3b2aa5d410f89aad3fde138b0a` |
| `verification/FEA-06/screens/workbench.png` | 28724 | `d5d878bbba9e47e2b59d9dd03816a370688a7afebec6d6e00016f262a46e2df5` |
| `verification/FEA-06/skip-analysis.md` | 725 | `acaf68b7b12ed9347a97e6aad6193d2411c6bb47f80e63e3c483fb2dc91d692a` |
| `verification/FEA-06/theme-gen.log` | 1256 | `ee2948527883acfe211eb47f881c63ba1f0511d7ca38d648902bc183a692651e` |
| `verification/FEA-06/token-gen.log` | 392 | `0cc5e6bbc598c2ed50a3f5557a7fca2f027540d599c1be48f13504ca08ca3977` |
| `verification/FEA-06/uiux/coverage-matrix.json` | 6463 | `a9d74fd319b806c823db7fb0ca19394f90a1258afa356fd264ad282ec37322c8` |
| `verification/FEA-06/uiux/evidence-manifest.json` | 11862 | `dd1db40b8b1bef9318039d683f4aface7c3f80612a1708482e8f7637bbabeb4b` |
| `verification/FEA-06/uiux/finalize.log` | 18828 | `bde655d84ede10046dae7df6c03e0b180b46e6cf6ce78b2274ad8e4ed43c1b88` |
| `verification/FEA-06/uiux/gate-results.json` | 8979 | `dcdf1daf2139d78113cde29135d56531142fcbda942ffbdbdcc80aa6aa080b09` |
| `verification/FEA-06/uiux/request.json` | 5175 | `74c0edac9e66c700f9b8bd0289ccc7591aeeb323ac231749c66c80c219ea4c19` |
| `verification/FEA-06/uiux/task-result.json` | 18404 | `cebe22f92c522074343ec4303f176c42bfe4c3a3e003f4673fc0502b96fb267f` |
| `verification/FEA-06/uiux/tool-logs.json` | 9270 | `8f32b1895125c37919ff9c83b8056d2e4974b101c9f6a1c916f84971ba7d971d` |
| `verification/FEA-06/verify-pins.log` | 426 | `cefc5376c8ea58cdd8297aa39674aff6aaaf31ac683dc446d16b2cbfb395a479` |

## impl-r1 rework evidence

| Evidence path | Bytes | SHA-256 |
|---|---:|---|
| `verification/FEA-06/rework-build.log` | 2593 | `56581789d10b76aa06ec29e9e05268de879691dd2bb562ba61cb5441cabb5c21` |
| `verification/FEA-06/rework-design-system-tests.log` | 617 | `1ab974fb7cbec32ae2377830be759cd3d0a5f1b1760b027253d815347d6f5737` |
| `verification/FEA-06/rework-full-test-attempt1.log` | 18173 | `1547e6984fa27208a2d87b2c99a1d8b0e091d2add8afbc4e307f129f2677be22` |
| `verification/FEA-06/rework-full-test.log` | 17432 | `63c707807a6e1da0dc02dfe6aa56579e3e95eb9ab443fcf7e954e929b782e23e` |
| `verification/FEA-06/rework-governance-check.log` | 1170 | `07ebd871931f4aed985f8afcb1e7aeb53ed476501940d334a6a021c61e9cc8a9` |
| `verification/FEA-06/rework-page-tests.log` | 554 | `3fb25d527c432dc53f68b50acbec4ce6245f31d51e72401b81136c47ff03ca27` |
| `verification/FEA-06/rework-scope-audit.md` | 958 | `4e0696c8944e99156d9b23268201aed9fd075f6347a821a4c9778f63dcb874d0` |
| `verification/FEA-06/rework-task-ledger.log` | 1610 | `15c220f917421357be14c9cdf9065c5c543f96f8740a52bfb13614a580fd5248` |
| `verification/FEA-06/rework-theme-gen.log` | 1256 | `169b9fe70e730c0503ab12d4ee4a7f51684318d52aa23b2ab0ba3e1c10b024ee` |
| `verification/FEA-06/rework-token-gen.log` | 392 | `90b91fbde2c349ee51bb31fc0c68cf71ac63243f66dc19654a0f9b854df50753` |
| `verification/FEA-06/rework-verify-pins.log` | 426 | `d521d266606edec817ac419e0252fca4aeca39c1b06463bf87d1411e49929e05` |

## impl-r2 P2-R2-1 evidence

| Evidence path | Bytes | SHA-256 |
|---|---:|---|
| `apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/Controls.Fluent.axaml` | 21398 | `02a4a2cf851b82f39d16094a2a266214e3477877d4dbfb2143342175d3982c96` |
| `apps/desktop-avalonia/tests/NewManga.App.Tests/FluentPageTests.cs` | 12708 | `5c7fa89521418fbf518086e050f86f635f4e4f89bc498948fa32bc403bd1be72` |
| `verification/FEA-06/component-registry.md` | 7355 | `5dd20bf012c3863bca5700febd896357ec2fe136cc44fcd7ed2e131bcfe58324` |
| `verification/FEA-06/impl-r2-build.log` | 2586 | `30dc4310c5eb364b88678c5e65b69a0eecd8a65fa4ab8cee7e17beed2ea685cf` |
| `verification/FEA-06/impl-r2-check.log` | 472 | `437e103611d48b529cbfe3047c81a6a9299318294e44d2bcb9a69a6c295ed2a5` |
| `verification/FEA-06/impl-r2-fluent-tab-test-attempt1.log` | 1540 | `42932aabd87e116796678110570af9586933ee97e0235bdbf2ebb8e63d917ff8` |
| `verification/FEA-06/impl-r2-fluent-tab-test.log` | 1708 | `a7b451dd0872d893fe0f961d311cbb4282869d653a54a5c3c4f1aafe707e8b53` |
| `verification/FEA-06/impl-r2-full-test.log` | 17425 | `cce2834512d194b979464f71a9e1dbbf7724d0ecaab736c6105d6da00012e61a` |
| `verification/FEA-06/impl-r2-verify-pins.log` | 419 | `fe89637581edf5203f39d2e6bda7a240b69724e5f88c877016f74a93c7743930` |
| `verification/FEA-06/screens/workbench.png` | 28724 | `d5d878bbba9e47e2b59d9dd03816a370688a7afebec6d6e00016f262a46e2df5` |
