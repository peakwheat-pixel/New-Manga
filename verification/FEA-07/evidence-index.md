# FEA-07 证据索引（自动生成）

- 生成时间: 2026-11-02 21:03:49 +08:00
- 代码 head: aedc7251c3cae49a12c8b6bc3f91c3e6dd53d3d0 (r8 返修提交；r9/r10 仅文档修正)
- 全量测试: **1138 passed / 0 failed / 57 skipped**（skip 直接原因: sidecar env 未设置）
- 治理: check.ps1 PASS(3); verify_pins.ps1 PASS 15/15
- 生成物: TokenGen --check 292 rows up-to-date; ThemeGen --check up-to-date
- 性能: Release p50 109.89 / p95 381.43 / max(UI freeze upper bound) 383.05 ms / memory +456B / handles +1 => W-5 PASS（4 预热 + 20 单向切换；两次复测 p95 361.52/381.43 ms）
- 复核: scope-r1/r2 approved; impl-r1–r5/r7/r8/r9/r10 changes_requested 均已处置; impl-r6 approved; 当前 Appointment=impl-r11 复核中
- 原生双屏/拔屏/DPI 矩阵: BLOCKED (D-1 无硬件)

说明: 本文件不列自身 SHA; 外部 pin 以 Task EV-FEA07-* 与 final-evidence.log 为准。

## 证据文件与 SHA-256

| 文件 | 路径 | sha256 |
|---|---|---|
| final-evidence.log | verification/FEA-07/final-evidence.log | e8ed8f2934ae33a0d062c0a52e0c96fa59940e0d9ab9243a6f408584e8e43785 |
| generators-check.log | verification/FEA-07/generators-check.log | c14b314350fdb2fd9d88cfa9df4cd5f46e236d3f41964c25ca1252545b48c921 |
| performance-baseline-debug.json | verification/FEA-07/performance-baseline-debug.json | b9d094be8b22f2fdd34cca4b8bb42ebf5a51bfa234310e9945197ce441224ae1 |
| performance-baseline-release.json | verification/FEA-07/performance-baseline-release.json | 2ab2f5cfd7241238ca7676890db00b8a292548bb020eae9bbb8bcf7717ee20b7 |
| performance-baseline.md | verification/FEA-07/performance-baseline.md | d6b87c5a99868d90619354c1f71f0616669f5f6ac92a0d39cee44a586f85b458 |
| rework-part1-verification.log | verification/FEA-07/rework-part1-verification.log | 27fa7ab94a645317723ae83332e8e25f2c6480cf9d50f1680466334c5c14298a |
| rework-part2-verification.log | verification/FEA-07/rework-part2-verification.log | 725ec7f6e4d6295f386d0bb08a65771158536fc7fa02e7a4f640a713f38eaa01 |
| rework-r3-part1-verification.log | verification/FEA-07/rework-r3-part1-verification.log | c6eefffef4fa6a2f9d7e0afa1b91f2ddff8110da2aa2b3c965293095c4e696a9 |
| rework-r3-part2-verification.log | verification/FEA-07/rework-r3-part2-verification.log | aacf4ce239fb978d614dc4d958454fde084ed219d9d806940a7225743aaf3b28 |
| rework-r4-verification.log | verification/FEA-07/rework-r4-verification.log | f0cb74032c50e3b24fede26b59d053beef07f9a8a337fd7ec52bacd27c5a4c3b |
| rework-r5-verification.log | verification/FEA-07/rework-r5-verification.log | e773a93def145d258ff09f8cb02ae9783823e7588e06443de28ba3381a3619b9 |
| rework-r6-verification.log | verification/FEA-07/rework-r6-verification.log | 322475cb618a71cf1f69e3422908a4d2b435ac53567462ffe1ba2309b01c5ae9 |
| rework-r7-verification.log | verification/FEA-07/rework-r7-verification.log | 9e4e04bd57bd9eadc238dd334b4cd502817fcfd2c7e8ac4904534b6c586e1144 |
| rework-r8-verification.log | verification/FEA-07/rework-r8-verification.log | b739ac7c1f4c782e981a06b0ad01afa58ea12d64b38487998aeaa89c6504784a |
| slice-1-verification.log | verification/FEA-07/slice-1-verification.log | a63982423ba6e79f96f76bacc27049a2bba18506fdf9411c13df0c5f13dac78d |
| slice-2-verification.log | verification/FEA-07/slice-2-verification.log | 55fd5e5fb1c5a9a146e3cda5e5a8087ebff4beeee9a5c480e81d539d6bbfe771 |
| slice-2b-verification.log | verification/FEA-07/slice-2b-verification.log | 2c281f288af106ed5391eea065aaac25f8f6543063a5aecab0f7ec11a4cee88b |
| slice-2c-part1-verification.log | verification/FEA-07/slice-2c-part1-verification.log | d835a23daf53d64d90fbe026f3307570b74df6778a7f1c50f61e60cfe63ee7f1 |
| slice-2c-part2-verification.log | verification/FEA-07/slice-2c-part2-verification.log | 7b848ca1a773e82e0b1faa1ee3e1a7f2d54f8ca49f2e0b3faaa80702ecb75973 |
| slice-3-verification.log | verification/FEA-07/slice-3-verification.log | bb11ca80e77ad3345a7410c5b0b8a7818a2df0f2ce329460d4007cc9e1886b26 |
| slice-4-verification.log | verification/FEA-07/slice-4-verification.log | 3197f8b536114bfd7c78c45ab362bf85a62edd0b370363cce03a30ec204b4ed0 |
| slice-5-verification.log | verification/FEA-07/slice-5-verification.log | 098d9991a0d0c7303ce7c6093b45179c4b16ccbf7516583a655257b906478ed9 |
| slice-6-gapclosing-verification.log | verification/FEA-07/slice-6-gapclosing-verification.log | 29e10eff99acb7beee864e316c0171d09f196ef51fa41a4c7e5ea73c3ffe3230 |

