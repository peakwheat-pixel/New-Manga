# FEA-09 逐文件 EV（I011 收敛后；零 PENDING）

- 生成时间：2026-11-03T16:54:29+00:00
- HEAD：`59ad0b9fed912c636bf5e6b46287a4554c95bdee`
- 口径：SHA-256 为工作树原始字节（不按 LF 归一）；`added_commit` = `git log --diff-filter=A`，`last_commit` = 最后一次修改该路径的提交。
- 唯一 ID：EV-001…顺序编号，无重复、无 PENDING；旧台账原字节保留在 `verification/FEA-09/history/EV-2026-11-03.md`（HISTORICAL 行）。
- 合成组件目录（`cache-component/`、`grant-component/`、`native-registry/`）由测试每次重新生成，已从版本控制移出并写入 `.gitignore`；不作为 canonical 证据。

| EV | 仓库路径 | bytes | 工作树 SHA-256 | added_commit | last_commit | 类别 |
|---|---|---:|---|---|---|---|
| EV-001 | `verification/FEA-09/AC-MATRIX.md` | 4302 | `8e3d06acc072f6ff6438fb2260bffb010bd1696998951967d8d1c9c716268959` | `3d308f449c979a6d6ee626f7db94fe4b0e171182` | `6a164253d1fa9ad801036d150c9bc981964689ca` | CANONICAL |
| EV-002 | `verification/FEA-09/history/EV-2026-11-03.md` | 29128 | `236e88d996fda4f06fb44055297e6a12657d71b5d90283cd08bc85f6464e9141` | `-` | `-` | HISTORICAL |
| EV-003 | `verification/FEA-09/ipc/fea09-real-ipc.json` | 1465 | `303dec898f6450c7807711182fd6d8a1912cc3675b00252971b29b45b658fba4` | `081cb2c39d9851487f701496e689f21151ad00e2` | `59ad0b9fed912c636bf5e6b46287a4554c95bdee` | IPC |
| EV-004 | `verification/FEA-09/ipc/fea09-real-ipc.wire.ndjson` | 4028 | `7bf8e1ae71aa3b0456f0c36be763a92db557911b2f8d4a8f41f1a55dcfff14f4` | `081cb2c39d9851487f701496e689f21151ad00e2` | `59ad0b9fed912c636bf5e6b46287a4554c95bdee` | IPC |
| EV-005 | `verification/FEA-09/logs/allowed-paths-audit.json` | 9436 | `abb3ab9cc50113225c05b21809ada6f542f1eea02b9e02f816a268992cde00db` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | LOG |
| EV-006 | `verification/FEA-09/logs/branch-final.log` | 178 | `4ceb96f076514a9d3e48080b61bb4223c14bd6f6ccb76d925e4631b52ba19808` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | LOG |
| EV-007 | `verification/FEA-09/logs/check-final-r2.log` | 728 | `025cf5ebcac8f90b2f31dc72cf99c6ccad35972b148218f82057fb28dc3498f7` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | LOG |
| EV-008 | `verification/FEA-09/logs/check-final-r3.log` | 728 | `501ab31d2621f0a9c8849475d5f370d73acf482846127ea82feb5d416b8a6d19` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | LOG |
| EV-009 | `verification/FEA-09/logs/check-final.log` | 836 | `02b7cc5510ba2a47b47e7c9544cb044d69f398dae870f1eed89e526f6edf5a09` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | LOG |
| EV-010 | `verification/FEA-09/logs/check-pre-handoff.log` | 728 | `f1f5b70315d5166ab1e066aade5dd3a0ae532c504da17a6271f004e336dbf061` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | LOG |
| EV-011 | `verification/FEA-09/logs/dotnet-build-delivery-checkpoint.log` | 3022 | `e77975194da87cea47a9d83b5fe1171187caa453c28502acd2866987cb5da47f` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | LOG |
| EV-012 | `verification/FEA-09/logs/dotnet-build-evidence-final.log` | 3022 | `40b3fe7b32cab4dded10185236cc787a0ffa3054d0025983e2af3fa74463e4a7` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | LOG |
| EV-013 | `verification/FEA-09/logs/dotnet-build-final.log` | 3022 | `e533f1568ea580012deee849c02e03bb6624da6456888f9bcbfe00cd80abea8e` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | LOG |
| EV-014 | `verification/FEA-09/logs/dotnet-full-r2-summary.json` | 15952 | `26ae0f59f43e017d9697aaf3d568217686b0cb888dd4f4c3af6bddf129381bf8` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | LOG |
| EV-015 | `verification/FEA-09/logs/dotnet-full-r2.log` | 27861 | `87cbbb297659ae37f62223883a41e094d3cbae95e8083a167a4f758d51b69278` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | LOG |
| EV-016 | `verification/FEA-09/logs/dotnet-full.log` | 23550 | `5ee4cb230963eeca40ef0d2eeb11f0739abba1e6dd55c024c1ce8a6ecebf00dc` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | LOG |
| EV-017 | `verification/FEA-09/logs/dotnet-phase-c-build-2.log` | 3022 | `9dedf50ebd02444ef2e92f91ec8b7d3ae1ccbb30d0966377e5ad886a4a6401fc` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | LOG |
| EV-018 | `verification/FEA-09/logs/dotnet-phase-c-build-tests.log` | 3022 | `bbb76c3db2bd7d818633e76685cf4d8a6f77efe47b5f328ec1393f97c1072874` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | LOG |
| EV-019 | `verification/FEA-09/logs/dotnet-phase-c-build.log` | 8137 | `3bc2d2511a62fac0c7288cdbd9e0d5e48980df03f29089fe13eaf71a5277d915` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | LOG |
| EV-020 | `verification/FEA-09/logs/dotnet-phase-c-no-restore.log` | 10528 | `73bde6bf0ef94a441784fdc7742f53d8ad2b0e5cdb2ee2df1bd8157b04911ea4` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | LOG |
| EV-021 | `verification/FEA-09/logs/dotnet-phase-c-tests.log` | 6841 | `547b067a33efb4e3cdd8f690df98f5f7107e4e114bc935de1ccbbee2fdb6a576` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | LOG |
| EV-022 | `verification/FEA-09/logs/dotnet-source-command-evidence-final.log` | 779 | `913c40ac251e1bcf914fd8bb607348d76330dab6246362e2ae3e6a91d46a2ad2` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | LOG |
| EV-023 | `verification/FEA-09/logs/dotnet-source-command-regression.log` | 779 | `166e12fac5265e7c45ac9e2db5371fc96b3b5d1ef71c6d966476288fae15fe5b` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | LOG |
| EV-024 | `verification/FEA-09/logs/dsh-i001-implementation.log` | 949 | `e210ecdc9bf2458d7e87b4f05f50852d3b8799252a5aa7ecbf933efcc665ff03` | `2931dbc0d04fa73aff461e5c639b5abc8aed54af` | `2931dbc0d04fa73aff461e5c639b5abc8aed54af` | LOG |
| EV-025 | `verification/FEA-09/logs/dsh-i005-core.log` | 1046 | `53c45aac82a26aa5368e660f68516d47553a1f75d00034503336be502617efbc` | `65c220fffb9960746b4385dbdef7972983a7b3ec` | `65c220fffb9960746b4385dbdef7972983a7b3ec` | LOG |
| EV-026 | `verification/FEA-09/logs/dsh-i005-host.log` | 1242 | `2d60087d054b92e5122ad97fc499febcc90452fd0ba8446efb3954c753770e6f` | `59ad0b9fed912c636bf5e6b46287a4554c95bdee` | `59ad0b9fed912c636bf5e6b46287a4554c95bdee` | LOG |
| EV-027 | `verification/FEA-09/logs/dsh-integration.md` | 3419 | `e8059872ae3778552d29c43fa5dc3bceffd667b9ea65e0dd5844cc157842b58b` | `7b7e4b16bcf4136f12f2468f6e76286f4173629b` | `7b7e4b16bcf4136f12f2468f6e76286f4173629b` | LOG |
| EV-028 | `verification/FEA-09/logs/dsh-real-ipc.log` | 1758 | `c8fe52008c246c8de58f49e0a47a5eef59adb53fdfa78cc58fd3d5039e6251f2` | `081cb2c39d9851487f701496e689f21151ad00e2` | `ab3f3131aeb1a6920e0f07066a0d8d2c493b7b76` | LOG |
| EV-029 | `verification/FEA-09/logs/dsh-referenced-resolve.log` | 3415 | `4494491a105e48d8dc9a47ccd0afa561c360d95079c42995d67b1cb075ff4fda` | `78bda22c53e1aa3e3170d65e1788393eb81b1e6b` | `3f2056555716c6880b1ddc10007a375f01e27568` | LOG |
| EV-030 | `verification/FEA-09/logs/dsh-review-batch1.log` | 2533 | `970298d1ca48e71a66b74fc5a3404d16cf692af5c36ec05ba4f18b9a822674d5` | `e8c7f6af21e58fadf4bdff2aa297f401b35ff46e` | `e8c7f6af21e58fadf4bdff2aa297f401b35ff46e` | LOG |
| EV-031 | `verification/FEA-09/logs/dsh-review-batch2.log` | 1767 | `812b56831bb6825115f31640edd7ed39eacdf65ef55f89d5f48b85e9aedbeb6a` | `b2c7a362d9c571d4229b1dccccbaf8163d5e6f02` | `b2c7a362d9c571d4229b1dccccbaf8163d5e6f02` | LOG |
| EV-032 | `verification/FEA-09/logs/dsh-review-batch3a.log` | 1599 | `3e3373b84406c905078d5fd5d974e9b4789a655f0fa73312d020b6e6cedffe7c` | `e3b6fe7f0d134be5e09a9c60b1ad56f3067b3b3b` | `e3b6fe7f0d134be5e09a9c60b1ad56f3067b3b3b` | LOG |
| EV-033 | `verification/FEA-09/logs/dsh-sharing-dualread.log` | 845 | `d82f08b22c0ebe068f9bad15e2c5a33b76149f0270a282604dad32c88b4b2408` | `79d97cff87bebb31036f5c91c06b55eafd675e40` | `79d97cff87bebb31036f5c91c06b55eafd675e40` | LOG |
| EV-034 | `verification/FEA-09/logs/dsh-unfreeze-chain.log` | 2652 | `a5d6f6f673ab6d41c2bfe0a09892da330ca2b5110730d96509b6dc6ac97f0238` | `566aa4e49c247d5609a5374e4974d8533b8a3c65` | `83015d684a7e0386d0aa55bf3dddd7f216029b69` | LOG |
| EV-035 | `verification/FEA-09/logs/fea06-png-audit.json` | 1327 | `78654537cdb1bc7b2c71cc7b78207cd5e866a76497ec5fcd752af127c7403d92` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | LOG |
| EV-036 | `verification/FEA-09/logs/git-stage-blocked.log` | 339 | `0b4e1049f1542754144fe32635df52a6638489c0005b097eb74ed15f8cc5a26c` | `bb87e62972afc685bcd700deefdeacda51061523` | `bb87e62972afc685bcd700deefdeacda51061523` | LOG |
| EV-037 | `verification/FEA-09/logs/git-stage-node-blocked.log` | 1160 | `40f892aada53c585eac43cc180f115d284f93ad78a820f30c3073bcb4b4220b3` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | LOG |
| EV-038 | `verification/FEA-09/logs/head-final.log` | 231 | `81737eb49324f39cf7e7dd948519e7387cc8082ba53498b986e7d5deb545f505` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | LOG |
| EV-039 | `verification/FEA-09/logs/password-audit.json` | 201 | `1b2d3d3959220a42336753f76c046769d7eaff682a0faf4f354a0fdf87a26453` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | LOG |
| EV-040 | `verification/FEA-09/logs/pins-final.log` | 625 | `b56ae26c32abb60490aaff86f69d444eed37cab6987d7456233000d00659b04d` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | LOG |
| EV-041 | `verification/FEA-09/logs/pins.log` | 769 | `ea2789d918e83380941e6dba97b438c0ae0fdaff0350ab5c1c93fb84d01ee31e` | `bb87e62972afc685bcd700deefdeacda51061523` | `bb87e62972afc685bcd700deefdeacda51061523` | LOG |
| EV-042 | `verification/FEA-09/logs/python-cache-component.log` | 1301 | `8a6e8c9fcb06034ee34f5d5ee49a1fc2a03590df2cd5e92d20fae686c5762d81` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | LOG |
| EV-043 | `verification/FEA-09/logs/python-components-delivery-checkpoint.log` | 2070 | `7d649578f8ea8bfa03858a6fae1faec4f20f3ce580c357deb2150ac448fe7dbe` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | LOG |
| EV-044 | `verification/FEA-09/logs/python-components-final.log` | 2070 | `ea9d6d5c77afcad3410439e676e854b51ebc6f514a9c502177bc79a1d36cbdae` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | LOG |
| EV-045 | `verification/FEA-09/logs/python-final-syntax.log` | 537 | `076c38ecc3d10c3b7736b47ee0bd35cd97c5aa70a5c0d1b6887fe1a05c158700` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | LOG |
| EV-046 | `verification/FEA-09/logs/python-grant-import.log` | 325 | `6c8c8b452c55dac3e078d6610820e33bb272bfb735aa26bb6bd0d01962aedf1a` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | LOG |
| EV-047 | `verification/FEA-09/logs/python-handle-identity-diagnostic.log` | 782 | `f2f64006bc81c61d5ecc31a03ad7edcf8a4e686c1b247cfece80b796cc87cfa8` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | LOG |
| EV-048 | `verification/FEA-09/logs/python-phase-c-baseline.log` | 321 | `1d6b284efbd6edd684a0af844aaa1d69e4b4a6b4ee6e29bfb388d729089283e8` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | LOG |
| EV-049 | `verification/FEA-09/logs/python-source-grant-component-r2.log` | 6742 | `1d208f97e71b72ea721a16365aa5e598e06de53f0adbb8ef3061b5c4ee8eb4c9` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | LOG |
| EV-050 | `verification/FEA-09/logs/python-source-grant-component-r3.log` | 1226 | `7354c95f0485ec1d49ec85877ecaaecbac2d0855219d6e0aef7e0066bdf90bd7` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | LOG |
| EV-051 | `verification/FEA-09/logs/python-source-grant-component.log` | 5243 | `324dbe84a4678f1bc3494b3a2346aefbef0892a603f6bc107fe5805a5a373756` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | LOG |
| EV-052 | `verification/FEA-09/logs/python-syntax.log` | 653 | `f58fed6adade37326bd137cec481da85d0a975f6c7927c6bf0890434911b830e` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | LOG |
| EV-053 | `verification/FEA-09/logs/python-test-dependencies.log` | 2862 | `78f6335d11a62c99178ef41f208aee53a0094d606a779d449c457477f840fc9a` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | LOG |
| EV-054 | `verification/FEA-09/logs/recovery-git-state.log` | 3203 | `7fd7db63bba26444bcdf7ab27567e0ee3a6b41eb8583af077d410027b8f9cb0f` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | LOG |
| EV-055 | `verification/FEA-09/logs/test-process-status.log` | 448 | `54d92d5d020d6ab69b0f64afeb0b580f0034e31d300cbdcb65379f58153c7faa` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | LOG |
| EV-056 | `verification/FEA-09/logs/wire-redacted.ndjson` | 4170 | `4434963e12df2d315784e19f6fbb116997bd49ff8323decdf1d0b6883fcebb3b` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | `65c220fffb9960746b4385dbdef7972983a7b3ec` | LOG |
| EV-057 | `verification/FEA-09/working-tree-files.json` | 4964 | `ab3c7707843eb61fd1aed0478953c14eed17b76a3878f039cb75eb09cb1d51b4` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | `995d80ca54fbd8dad8a27ae19ab69c7ef45813d8` | SUPPORTING |

## 历史/已删除证据（不能用作当前交付证据）

| 仓库路径 | 旧台账 pin | 处置 |
|---|---|---|
| `verification/FEA-09/EV.md` | `PENDING（未提交）` | 仅存在于 git 历史（合成/临时证据，未纳入 canonical） |
| `verification/FEA-09/cache-component/038c6e60d5c34cb198148311770e9605/derived/source-renditions/231ac80e5b5234abe2999d585dedb8d409d55e6af97aad9afe18ddb21564ce29.bin` | `PENDING（未提交）` | 仅存在于 git 历史（合成/临时证据，未纳入 canonical） |
| `verification/FEA-09/cache-component/038c6e60d5c34cb198148311770e9605/derived/source-renditions/370efd26c279ec64a615cd1fd3314a9fb438e3310bb6b5748def9cf7725ed472.bin` | `PENDING（未提交）` | 仅存在于 git 历史（合成/临时证据，未纳入 canonical） |
| `verification/FEA-09/cache-component/038c6e60d5c34cb198148311770e9605/derived/source-renditions/c885528757122a553241699befef82b98cbf3f7b6ae0693d78f040174a8c027e.bin` | `PENDING（未提交）` | 仅存在于 git 历史（合成/临时证据，未纳入 canonical） |
| `verification/FEA-09/cache-component/038c6e60d5c34cb198148311770e9605/derived/source-renditions/d463a9283ef8c044436a44e35d66e191138313a01e8cc7ad116844c43ddf15ef.bin` | `PENDING（未提交）` | 仅存在于 git 历史（合成/临时证据，未纳入 canonical） |
| `verification/FEA-09/cache-component/5c0cb19c34ae4490abc59712ff08f5a2/derived/source-renditions/64e2d4f86906e597a997db02039297c31358753784a04189699319bf076f40e3.bin` | `PENDING（未提交）` | 仅存在于 git 历史（合成/临时证据，未纳入 canonical） |
| `verification/FEA-09/cache-component/5ea4d5b5710a4cfe8f27598424379e48/derived/source-renditions/8091648e485a277d9020e1d13429e01a67270a8e7c207073d5fccd916b92a640.bin` | `PENDING（未提交）` | 仅存在于 git 历史（合成/临时证据，未纳入 canonical） |
| `verification/FEA-09/cache-component/6aa06606bedb4d77b9b3916d837b7077/derived/source-renditions/64e2d4f86906e597a997db02039297c31358753784a04189699319bf076f40e3.bin` | `PENDING（未提交）` | 仅存在于 git 历史（合成/临时证据，未纳入 canonical） |
| `verification/FEA-09/cache-component/928cc857d3a44dd18f36c0d256cee6ba/derived/source-renditions/231ac80e5b5234abe2999d585dedb8d409d55e6af97aad9afe18ddb21564ce29.bin` | `PENDING（未提交）` | 仅存在于 git 历史（合成/临时证据，未纳入 canonical） |
| `verification/FEA-09/cache-component/928cc857d3a44dd18f36c0d256cee6ba/derived/source-renditions/370efd26c279ec64a615cd1fd3314a9fb438e3310bb6b5748def9cf7725ed472.bin` | `PENDING（未提交）` | 仅存在于 git 历史（合成/临时证据，未纳入 canonical） |
| `verification/FEA-09/cache-component/928cc857d3a44dd18f36c0d256cee6ba/derived/source-renditions/c885528757122a553241699befef82b98cbf3f7b6ae0693d78f040174a8c027e.bin` | `PENDING（未提交）` | 仅存在于 git 历史（合成/临时证据，未纳入 canonical） |
| `verification/FEA-09/cache-component/928cc857d3a44dd18f36c0d256cee6ba/derived/source-renditions/d463a9283ef8c044436a44e35d66e191138313a01e8cc7ad116844c43ddf15ef.bin` | `PENDING（未提交）` | 仅存在于 git 历史（合成/临时证据，未纳入 canonical） |
| `verification/FEA-09/cache-component/e674022e06dd48b79980685c0e1ea1c0/derived/source-renditions/231ac80e5b5234abe2999d585dedb8d409d55e6af97aad9afe18ddb21564ce29.bin` | `PENDING（未提交）` | 仅存在于 git 历史（合成/临时证据，未纳入 canonical） |
| `verification/FEA-09/cache-component/e674022e06dd48b79980685c0e1ea1c0/derived/source-renditions/370efd26c279ec64a615cd1fd3314a9fb438e3310bb6b5748def9cf7725ed472.bin` | `PENDING（未提交）` | 仅存在于 git 历史（合成/临时证据，未纳入 canonical） |
| `verification/FEA-09/cache-component/e674022e06dd48b79980685c0e1ea1c0/derived/source-renditions/c885528757122a553241699befef82b98cbf3f7b6ae0693d78f040174a8c027e.bin` | `PENDING（未提交）` | 仅存在于 git 历史（合成/临时证据，未纳入 canonical） |
| `verification/FEA-09/cache-component/e674022e06dd48b79980685c0e1ea1c0/derived/source-renditions/d463a9283ef8c044436a44e35d66e191138313a01e8cc7ad116844c43ddf15ef.bin` | `PENDING（未提交）` | 仅存在于 git 历史（合成/临时证据，未纳入 canonical） |
| `verification/FEA-09/cache-component/e7918174c4a24ec6b6e2ace1c759b77b/derived/source-renditions/8091648e485a277d9020e1d13429e01a67270a8e7c207073d5fccd916b92a640.bin` | `PENDING（未提交）` | 仅存在于 git 历史（合成/临时证据，未纳入 canonical） |
| `verification/FEA-09/cache-component/e9a5314d12dd4a9d8201faef5fe9222a/derived/source-renditions/64e2d4f86906e597a997db02039297c31358753784a04189699319bf076f40e3.bin` | `PENDING（未提交）` | 仅存在于 git 历史（合成/临时证据，未纳入 canonical） |
| `verification/FEA-09/cache-component/ea53696ea7f246c986c2e36ec14a6790/derived/source-renditions/8091648e485a277d9020e1d13429e01a67270a8e7c207073d5fccd916b92a640.bin` | `PENDING（未提交）` | 仅存在于 git 历史（合成/临时证据，未纳入 canonical） |
| `verification/FEA-09/grant-component/02e0aea25f2b49f6aab4e824611a66e5/source.bin` | `PENDING（未提交）` | 仅存在于 git 历史（合成/临时证据，未纳入 canonical） |
| `verification/FEA-09/grant-component/0a42c6406f4241d2b06211e721fa2ed1/source.bin` | `PENDING（未提交）` | 仅存在于 git 历史（合成/临时证据，未纳入 canonical） |
| `verification/FEA-09/grant-component/17c7c9581d1b457daeb81ea0b993e6d6/replaced.bin` | `PENDING（未提交）` | 仅存在于 git 历史（合成/临时证据，未纳入 canonical） |
| `verification/FEA-09/grant-component/17c7c9581d1b457daeb81ea0b993e6d6/source.bin` | `PENDING（未提交）` | 仅存在于 git 历史（合成/临时证据，未纳入 canonical） |
| `verification/FEA-09/grant-component/1b6f1eaa37704700911a8b73d454b8bf/source.bin` | `PENDING（未提交）` | 仅存在于 git 历史（合成/临时证据，未纳入 canonical） |
| `verification/FEA-09/grant-component/238606562535479784893736962eaed0/source.bin` | `PENDING（未提交）` | 仅存在于 git 历史（合成/临时证据，未纳入 canonical） |
| `verification/FEA-09/grant-component/252fd7f67cf64f35ad9f4dd307e4b427/source.bin` | `PENDING（未提交）` | 仅存在于 git 历史（合成/临时证据，未纳入 canonical） |
| `verification/FEA-09/grant-component/3b8fd00834624b75b02f444b9daba657/source.bin` | `PENDING（未提交）` | 仅存在于 git 历史（合成/临时证据，未纳入 canonical） |
| `verification/FEA-09/grant-component/565cf01473c54ce19554c7d2cac7ab59/source.bin` | `PENDING（未提交）` | 仅存在于 git 历史（合成/临时证据，未纳入 canonical） |
| `verification/FEA-09/grant-component/601b1c83e90e4e2a8009aa95db2e54e6/source.bin` | `PENDING（未提交）` | 仅存在于 git 历史（合成/临时证据，未纳入 canonical） |
| `verification/FEA-09/grant-component/66862c1d6b8a4119bb848aba1117b90c/source.bin` | `PENDING（未提交）` | 仅存在于 git 历史（合成/临时证据，未纳入 canonical） |
| `verification/FEA-09/grant-component/7b51f33ff111438bbf5cb136e3338e85/source.bin` | `PENDING（未提交）` | 仅存在于 git 历史（合成/临时证据，未纳入 canonical） |
| `verification/FEA-09/grant-component/7e6abe898ef940c891a473f5522af4ac/replaced.bin` | `PENDING（未提交）` | 仅存在于 git 历史（合成/临时证据，未纳入 canonical） |
| `verification/FEA-09/grant-component/7e6abe898ef940c891a473f5522af4ac/source.bin` | `PENDING（未提交）` | 仅存在于 git 历史（合成/临时证据，未纳入 canonical） |
| `verification/FEA-09/grant-component/88dd86b0e8b644edbf73c1cf70a29bf4/source.bin` | `PENDING（未提交）` | 仅存在于 git 历史（合成/临时证据，未纳入 canonical） |
| `verification/FEA-09/grant-component/9b129a9fed1a4cecb5b0df752ba9a301/replaced.bin` | `PENDING（未提交）` | 仅存在于 git 历史（合成/临时证据，未纳入 canonical） |
| `verification/FEA-09/grant-component/9b129a9fed1a4cecb5b0df752ba9a301/source.bin` | `PENDING（未提交）` | 仅存在于 git 历史（合成/临时证据，未纳入 canonical） |
| `verification/FEA-09/grant-component/a247c78e40f74b849da1c0fd939a059d/source.bin` | `PENDING（未提交）` | 仅存在于 git 历史（合成/临时证据，未纳入 canonical） |
| `verification/FEA-09/grant-component/a4b7a7099f4b4341aa5fe0ccf807b8e3/source.bin` | `PENDING（未提交）` | 仅存在于 git 历史（合成/临时证据，未纳入 canonical） |
| `verification/FEA-09/grant-component/baa80667c5f44c4c875d119661638c97/source.bin` | `PENDING（未提交）` | 仅存在于 git 历史（合成/临时证据，未纳入 canonical） |
| `verification/FEA-09/grant-component/badc237a0b4446c68246e81e3fb797b0/source.bin` | `PENDING（未提交）` | 仅存在于 git 历史（合成/临时证据，未纳入 canonical） |
| `verification/FEA-09/grant-component/ce5d77217a6e40fb87a8bf640aa3e4ec/source.bin` | `PENDING（未提交）` | 仅存在于 git 历史（合成/临时证据，未纳入 canonical） |
| `verification/FEA-09/grant-component/d80376ce84034ed3aeb33fcfd5c9295c/source.bin` | `PENDING（未提交）` | 仅存在于 git 历史（合成/临时证据，未纳入 canonical） |
| `verification/FEA-09/grant-component/d9c9666fabe64e9fbcfd0471444192c5/source.bin` | `PENDING（未提交）` | 仅存在于 git 历史（合成/临时证据，未纳入 canonical） |
| `verification/FEA-09/grant-component/e0c098beaef44debbd2b2f6d7b6811df/source.bin` | `PENDING（未提交）` | 仅存在于 git 历史（合成/临时证据，未纳入 canonical） |
| `verification/FEA-09/grant-component/e0ce256a342143c3b55ca9498b4ad0de/source.bin` | `PENDING（未提交）` | 仅存在于 git 历史（合成/临时证据，未纳入 canonical） |
| `verification/FEA-09/grant-component/e5dad58703204e5a857dc685048589ec/source.bin` | `PENDING（未提交）` | 仅存在于 git 历史（合成/临时证据，未纳入 canonical） |
| `verification/FEA-09/grant-component/ff9e4640bec54003921ea70a2f69c8fa/source.bin` | `PENDING（未提交）` | 仅存在于 git 历史（合成/临时证据，未纳入 canonical） |
| `verification/FEA-09/native-registry/4d91633ce3db4c1d9007c3ca3cd846c4/synthetic-source/page.txt` | `PENDING（未提交）` | 仅存在于 git 历史（合成/临时证据，未纳入 canonical） |
| `verification/FEA-09/native-registry/4fac051ab40b45c6896dc3a6b9715cf8/synthetic-source/page.txt` | `PENDING（未提交）` | 仅存在于 git 历史（合成/临时证据，未纳入 canonical） |
| `verification/FEA-09/native-registry/7822489190664193a4a52ef899785a61/synthetic-source/page.txt` | `PENDING（未提交）` | 仅存在于 git 历史（合成/临时证据，未纳入 canonical） |

## 合成目录去跟踪记录

- 本次从索引移除的合成证据文件数：0（测试生成，可重建）。
- 决策：合成 UUID 路径不进入 canonical EV；保留测试源码与运行日志作为证据来源。

## 未运行/限制

- 本台账是文件级证据索引，不证明 AC 达成；AC 状态见 `AC-MATRIX.md`。
- 真实 IPC/DPAPI/迁移/竞态等运行项以其日志与测试记录为准；未运行项不得据此宣称通过。
