# FEA-06 Canonical Evidence Index

- Base commit: `3c7f311d88b24bde462a61690e15d2c66f8c4683`.
- Implementation head: recorded in `doc/tasks/FEA-06.md` after the implementation commit.
- Full regression: **1030 passed / 0 failed / 57 skipped**. Skip cause: missing `NEWMANGA_CORECLIENT_SIDECAR_DIR`; see `verification/FEA-06/skip-analysis.md`.
- Headless page and navigation evidence is simulated; it does not establish native desktop visual behavior. See `verification/FEA-06/uiux/task-result.json` (`PARTIAL`).
- Test suite changes: 8 added Fluent tests relative to the 1022/0/57 baseline; no existing tests removed or skipped by this task.

| Evidence path | Bytes | SHA-256 |
|---|---:|---|
| `verification/FEA-06/build.log` | 2593 | `a7d6f89bb743f1bd40d46c185344c85d9c6fb2c5bea6940cccebaa38d632ffa0` |
| `verification/FEA-06/component-registry.md` | 6249 | `a629145df96cdca76ca3703e8852d865810cc5077959115ae2854b02c267fff4` |
| `verification/FEA-06/design-system-component-tests.log` | 652 | `5e3532f3b2af9efd01de8a75716f826c10d521a4797cb5ff568d708f52704838` |
| `verification/FEA-06/full-test.log` | 17432 | `be5fda55f2e55135bd5c81f902f9d2bf4b1d6aa10d78abc95b4451222890ad21` |
| `verification/FEA-06/governance-check.log` | 479 | `1141042fda8bdff7f268927511cd243da838b1e13eab4aff08d60fbf5f0b982f` |
| `verification/FEA-06/page-tests.log` | 589 | `1cd942044a0ab41326c9dedc9b9c6f3f1aa99e2f04059a92a14000b959a4439c` |
| `verification/FEA-06/scope-audit.md` | 2604 | `cec04b8135b13549f8c0114b43fe1259b00e5e335538cddccd6166cd8da90ea0` |
| `verification/FEA-06/screens/reader.png` | 25376 | `26e7a47a240cce5698396dd06ec9c4eac7e53ce1e7dbf69c1ce9a1f773f08374` |
| `verification/FEA-06/screens/settings.png` | 52957 | `73ab84ad2807534ef39b186c74bea144bcf8e92f057d54ecc61b584c52b282cd` |
| `verification/FEA-06/screens/shelf.png` | 31018 | `018af624d300e053b7276b702f7908e00426d432808eec810a6c8a4797f72c3f` |
| `verification/FEA-06/screens/workbench.png` | 25711 | `4ea215345178215fb9e677dc71e0cae10bd2cad7251165752ae7cfb259d6ab41` |
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
