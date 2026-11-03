# FEA-09 逐文件 EV（工作树检查点）

当前 HEAD `f9a2fa8e077f21c93131237171a32e85f6942200`；本轮实现未提交。SHA-256 口径为工作树原始字节，不按 LF 归一。已有基线文件仅在与该 commit blob 逐字节相同时登记 commit；新增文件标 PENDING。canonical_evidence_status 保持 pending，不据此宣称 AC 完成。

| EV | 仓库路径 | bytes | 工作树 SHA-256 | Commit pin | 用途/判读限制 |
|---|---|---:|---|---|---|
| EV-001 | `verification/FEA-09/cache-component/038c6e60d5c34cb198148311770e9605/derived/source-renditions/231ac80e5b5234abe2999d585dedb8d409d55e6af97aad9afe18ddb21564ce29.bin` | 12 | `f24abc34b13fade76e805799f71187da6cd90b9cac373ae65ed57f143bd664e5` | PENDING（未提交） | 保留的合成组件输入/输出（不替代 IPC/UI） |
| EV-002 | `verification/FEA-09/cache-component/038c6e60d5c34cb198148311770e9605/derived/source-renditions/370efd26c279ec64a615cd1fd3314a9fb438e3310bb6b5748def9cf7725ed472.bin` | 1 | `2d711642b726b04401627ca9fbac32f5c8530fb1903cc4db02258717921a4881` | PENDING（未提交） | 保留的合成组件输入/输出（不替代 IPC/UI） |
| EV-003 | `verification/FEA-09/cache-component/038c6e60d5c34cb198148311770e9605/derived/source-renditions/c885528757122a553241699befef82b98cbf3f7b6ae0693d78f040174a8c027e.bin` | 1 | `2d711642b726b04401627ca9fbac32f5c8530fb1903cc4db02258717921a4881` | PENDING（未提交） | 保留的合成组件输入/输出（不替代 IPC/UI） |
| EV-004 | `verification/FEA-09/cache-component/038c6e60d5c34cb198148311770e9605/derived/source-renditions/d463a9283ef8c044436a44e35d66e191138313a01e8cc7ad116844c43ddf15ef.bin` | 1 | `2d711642b726b04401627ca9fbac32f5c8530fb1903cc4db02258717921a4881` | PENDING（未提交） | 保留的合成组件输入/输出（不替代 IPC/UI） |
| EV-005 | `verification/FEA-09/cache-component/5c0cb19c34ae4490abc59712ff08f5a2/derived/source-renditions/64e2d4f86906e597a997db02039297c31358753784a04189699319bf076f40e3.bin` | 11 | `913640e99975e47ca81709a606011b38342739cbab72a14360fa8c6dfe1c1f03` | PENDING（未提交） | 保留的合成组件输入/输出（不替代 IPC/UI） |
| EV-006 | `verification/FEA-09/cache-component/5ea4d5b5710a4cfe8f27598424379e48/derived/source-renditions/8091648e485a277d9020e1d13429e01a67270a8e7c207073d5fccd916b92a640.bin` | 8 | `3baf75ce884746c426cafdff7e0a3ed3a52b4d70fb6dbf94bc754be4273a868a` | PENDING（未提交） | 保留的合成组件输入/输出（不替代 IPC/UI） |
| EV-007 | `verification/FEA-09/cache-component/6aa06606bedb4d77b9b3916d837b7077/derived/source-renditions/64e2d4f86906e597a997db02039297c31358753784a04189699319bf076f40e3.bin` | 11 | `913640e99975e47ca81709a606011b38342739cbab72a14360fa8c6dfe1c1f03` | PENDING（未提交） | 保留的合成组件输入/输出（不替代 IPC/UI） |
| EV-008 | `verification/FEA-09/cache-component/928cc857d3a44dd18f36c0d256cee6ba/derived/source-renditions/231ac80e5b5234abe2999d585dedb8d409d55e6af97aad9afe18ddb21564ce29.bin` | 12 | `f24abc34b13fade76e805799f71187da6cd90b9cac373ae65ed57f143bd664e5` | PENDING（未提交） | 保留的合成组件输入/输出（不替代 IPC/UI） |
| EV-009 | `verification/FEA-09/cache-component/928cc857d3a44dd18f36c0d256cee6ba/derived/source-renditions/370efd26c279ec64a615cd1fd3314a9fb438e3310bb6b5748def9cf7725ed472.bin` | 1 | `2d711642b726b04401627ca9fbac32f5c8530fb1903cc4db02258717921a4881` | PENDING（未提交） | 保留的合成组件输入/输出（不替代 IPC/UI） |
| EV-010 | `verification/FEA-09/cache-component/928cc857d3a44dd18f36c0d256cee6ba/derived/source-renditions/c885528757122a553241699befef82b98cbf3f7b6ae0693d78f040174a8c027e.bin` | 1 | `2d711642b726b04401627ca9fbac32f5c8530fb1903cc4db02258717921a4881` | PENDING（未提交） | 保留的合成组件输入/输出（不替代 IPC/UI） |
| EV-011 | `verification/FEA-09/cache-component/928cc857d3a44dd18f36c0d256cee6ba/derived/source-renditions/d463a9283ef8c044436a44e35d66e191138313a01e8cc7ad116844c43ddf15ef.bin` | 1 | `2d711642b726b04401627ca9fbac32f5c8530fb1903cc4db02258717921a4881` | PENDING（未提交） | 保留的合成组件输入/输出（不替代 IPC/UI） |
| EV-012 | `verification/FEA-09/cache-component/e674022e06dd48b79980685c0e1ea1c0/derived/source-renditions/231ac80e5b5234abe2999d585dedb8d409d55e6af97aad9afe18ddb21564ce29.bin` | 12 | `f24abc34b13fade76e805799f71187da6cd90b9cac373ae65ed57f143bd664e5` | PENDING（未提交） | 保留的合成组件输入/输出（不替代 IPC/UI） |
| EV-013 | `verification/FEA-09/cache-component/e674022e06dd48b79980685c0e1ea1c0/derived/source-renditions/370efd26c279ec64a615cd1fd3314a9fb438e3310bb6b5748def9cf7725ed472.bin` | 1 | `2d711642b726b04401627ca9fbac32f5c8530fb1903cc4db02258717921a4881` | PENDING（未提交） | 保留的合成组件输入/输出（不替代 IPC/UI） |
| EV-014 | `verification/FEA-09/cache-component/e674022e06dd48b79980685c0e1ea1c0/derived/source-renditions/c885528757122a553241699befef82b98cbf3f7b6ae0693d78f040174a8c027e.bin` | 1 | `2d711642b726b04401627ca9fbac32f5c8530fb1903cc4db02258717921a4881` | PENDING（未提交） | 保留的合成组件输入/输出（不替代 IPC/UI） |
| EV-015 | `verification/FEA-09/cache-component/e674022e06dd48b79980685c0e1ea1c0/derived/source-renditions/d463a9283ef8c044436a44e35d66e191138313a01e8cc7ad116844c43ddf15ef.bin` | 1 | `2d711642b726b04401627ca9fbac32f5c8530fb1903cc4db02258717921a4881` | PENDING（未提交） | 保留的合成组件输入/输出（不替代 IPC/UI） |
| EV-016 | `verification/FEA-09/cache-component/e7918174c4a24ec6b6e2ace1c759b77b/derived/source-renditions/8091648e485a277d9020e1d13429e01a67270a8e7c207073d5fccd916b92a640.bin` | 8 | `3baf75ce884746c426cafdff7e0a3ed3a52b4d70fb6dbf94bc754be4273a868a` | PENDING（未提交） | 保留的合成组件输入/输出（不替代 IPC/UI） |
| EV-017 | `verification/FEA-09/cache-component/e9a5314d12dd4a9d8201faef5fe9222a/derived/source-renditions/64e2d4f86906e597a997db02039297c31358753784a04189699319bf076f40e3.bin` | 11 | `913640e99975e47ca81709a606011b38342739cbab72a14360fa8c6dfe1c1f03` | PENDING（未提交） | 保留的合成组件输入/输出（不替代 IPC/UI） |
| EV-018 | `verification/FEA-09/cache-component/ea53696ea7f246c986c2e36ec14a6790/derived/source-renditions/8091648e485a277d9020e1d13429e01a67270a8e7c207073d5fccd916b92a640.bin` | 8 | `3baf75ce884746c426cafdff7e0a3ed3a52b4d70fb6dbf94bc754be4273a868a` | PENDING（未提交） | 保留的合成组件输入/输出（不替代 IPC/UI） |
| EV-019 | `verification/FEA-09/grant-component/02e0aea25f2b49f6aab4e824611a66e5/source.bin` | 16 | `39631bb5e5dc9326b23f8c00bf43440a84ce711315c6b799de554c56aa04d133` | PENDING（未提交） | 保留的合成组件输入/输出（不替代 IPC/UI） |
| EV-020 | `verification/FEA-09/grant-component/0a42c6406f4241d2b06211e721fa2ed1/source.bin` | 16 | `39631bb5e5dc9326b23f8c00bf43440a84ce711315c6b799de554c56aa04d133` | PENDING（未提交） | 保留的合成组件输入/输出（不替代 IPC/UI） |
| EV-021 | `verification/FEA-09/grant-component/17c7c9581d1b457daeb81ea0b993e6d6/replaced.bin` | 16 | `39631bb5e5dc9326b23f8c00bf43440a84ce711315c6b799de554c56aa04d133` | PENDING（未提交） | 保留的合成组件输入/输出（不替代 IPC/UI） |
| EV-022 | `verification/FEA-09/grant-component/17c7c9581d1b457daeb81ea0b993e6d6/source.bin` | 16 | `39631bb5e5dc9326b23f8c00bf43440a84ce711315c6b799de554c56aa04d133` | PENDING（未提交） | 保留的合成组件输入/输出（不替代 IPC/UI） |
| EV-023 | `verification/FEA-09/grant-component/1b6f1eaa37704700911a8b73d454b8bf/source.bin` | 16 | `39631bb5e5dc9326b23f8c00bf43440a84ce711315c6b799de554c56aa04d133` | PENDING（未提交） | 保留的合成组件输入/输出（不替代 IPC/UI） |
| EV-024 | `verification/FEA-09/grant-component/238606562535479784893736962eaed0/source.bin` | 16 | `39631bb5e5dc9326b23f8c00bf43440a84ce711315c6b799de554c56aa04d133` | PENDING（未提交） | 保留的合成组件输入/输出（不替代 IPC/UI） |
| EV-025 | `verification/FEA-09/grant-component/252fd7f67cf64f35ad9f4dd307e4b427/source.bin` | 15 | `538a741c622733afe147819e939d82cc071edfbeb3eb49ed701a55975ac288b3` | PENDING（未提交） | 保留的合成组件输入/输出（不替代 IPC/UI） |
| EV-026 | `verification/FEA-09/grant-component/3b8fd00834624b75b02f444b9daba657/source.bin` | 16 | `39631bb5e5dc9326b23f8c00bf43440a84ce711315c6b799de554c56aa04d133` | PENDING（未提交） | 保留的合成组件输入/输出（不替代 IPC/UI） |
| EV-027 | `verification/FEA-09/grant-component/565cf01473c54ce19554c7d2cac7ab59/source.bin` | 16 | `39631bb5e5dc9326b23f8c00bf43440a84ce711315c6b799de554c56aa04d133` | PENDING（未提交） | 保留的合成组件输入/输出（不替代 IPC/UI） |
| EV-028 | `verification/FEA-09/grant-component/601b1c83e90e4e2a8009aa95db2e54e6/source.bin` | 16 | `39631bb5e5dc9326b23f8c00bf43440a84ce711315c6b799de554c56aa04d133` | PENDING（未提交） | 保留的合成组件输入/输出（不替代 IPC/UI） |
| EV-029 | `verification/FEA-09/grant-component/66862c1d6b8a4119bb848aba1117b90c/source.bin` | 16 | `39631bb5e5dc9326b23f8c00bf43440a84ce711315c6b799de554c56aa04d133` | PENDING（未提交） | 保留的合成组件输入/输出（不替代 IPC/UI） |
| EV-030 | `verification/FEA-09/grant-component/7b51f33ff111438bbf5cb136e3338e85/source.bin` | 16 | `39631bb5e5dc9326b23f8c00bf43440a84ce711315c6b799de554c56aa04d133` | PENDING（未提交） | 保留的合成组件输入/输出（不替代 IPC/UI） |
| EV-031 | `verification/FEA-09/grant-component/7e6abe898ef940c891a473f5522af4ac/replaced.bin` | 16 | `39631bb5e5dc9326b23f8c00bf43440a84ce711315c6b799de554c56aa04d133` | PENDING（未提交） | 保留的合成组件输入/输出（不替代 IPC/UI） |
| EV-032 | `verification/FEA-09/grant-component/7e6abe898ef940c891a473f5522af4ac/source.bin` | 16 | `39631bb5e5dc9326b23f8c00bf43440a84ce711315c6b799de554c56aa04d133` | PENDING（未提交） | 保留的合成组件输入/输出（不替代 IPC/UI） |
| EV-033 | `verification/FEA-09/grant-component/88dd86b0e8b644edbf73c1cf70a29bf4/source.bin` | 16 | `39631bb5e5dc9326b23f8c00bf43440a84ce711315c6b799de554c56aa04d133` | PENDING（未提交） | 保留的合成组件输入/输出（不替代 IPC/UI） |
| EV-034 | `verification/FEA-09/grant-component/9b129a9fed1a4cecb5b0df752ba9a301/replaced.bin` | 16 | `39631bb5e5dc9326b23f8c00bf43440a84ce711315c6b799de554c56aa04d133` | PENDING（未提交） | 保留的合成组件输入/输出（不替代 IPC/UI） |
| EV-035 | `verification/FEA-09/grant-component/9b129a9fed1a4cecb5b0df752ba9a301/source.bin` | 16 | `39631bb5e5dc9326b23f8c00bf43440a84ce711315c6b799de554c56aa04d133` | PENDING（未提交） | 保留的合成组件输入/输出（不替代 IPC/UI） |
| EV-036 | `verification/FEA-09/grant-component/a247c78e40f74b849da1c0fd939a059d/source.bin` | 16 | `39631bb5e5dc9326b23f8c00bf43440a84ce711315c6b799de554c56aa04d133` | PENDING（未提交） | 保留的合成组件输入/输出（不替代 IPC/UI） |
| EV-037 | `verification/FEA-09/grant-component/a4b7a7099f4b4341aa5fe0ccf807b8e3/source.bin` | 16 | `39631bb5e5dc9326b23f8c00bf43440a84ce711315c6b799de554c56aa04d133` | PENDING（未提交） | 保留的合成组件输入/输出（不替代 IPC/UI） |
| EV-038 | `verification/FEA-09/grant-component/baa80667c5f44c4c875d119661638c97/source.bin` | 15 | `538a741c622733afe147819e939d82cc071edfbeb3eb49ed701a55975ac288b3` | PENDING（未提交） | 保留的合成组件输入/输出（不替代 IPC/UI） |
| EV-039 | `verification/FEA-09/grant-component/badc237a0b4446c68246e81e3fb797b0/source.bin` | 15 | `538a741c622733afe147819e939d82cc071edfbeb3eb49ed701a55975ac288b3` | PENDING（未提交） | 保留的合成组件输入/输出（不替代 IPC/UI） |
| EV-040 | `verification/FEA-09/grant-component/ce5d77217a6e40fb87a8bf640aa3e4ec/source.bin` | 16 | `39631bb5e5dc9326b23f8c00bf43440a84ce711315c6b799de554c56aa04d133` | PENDING（未提交） | 保留的合成组件输入/输出（不替代 IPC/UI） |
| EV-041 | `verification/FEA-09/grant-component/d80376ce84034ed3aeb33fcfd5c9295c/source.bin` | 16 | `39631bb5e5dc9326b23f8c00bf43440a84ce711315c6b799de554c56aa04d133` | PENDING（未提交） | 保留的合成组件输入/输出（不替代 IPC/UI） |
| EV-042 | `verification/FEA-09/grant-component/d9c9666fabe64e9fbcfd0471444192c5/source.bin` | 15 | `538a741c622733afe147819e939d82cc071edfbeb3eb49ed701a55975ac288b3` | PENDING（未提交） | 保留的合成组件输入/输出（不替代 IPC/UI） |
| EV-043 | `verification/FEA-09/grant-component/e0c098beaef44debbd2b2f6d7b6811df/source.bin` | 16 | `39631bb5e5dc9326b23f8c00bf43440a84ce711315c6b799de554c56aa04d133` | PENDING（未提交） | 保留的合成组件输入/输出（不替代 IPC/UI） |
| EV-044 | `verification/FEA-09/grant-component/e0ce256a342143c3b55ca9498b4ad0de/source.bin` | 16 | `39631bb5e5dc9326b23f8c00bf43440a84ce711315c6b799de554c56aa04d133` | PENDING（未提交） | 保留的合成组件输入/输出（不替代 IPC/UI） |
| EV-045 | `verification/FEA-09/grant-component/e5dad58703204e5a857dc685048589ec/source.bin` | 16 | `39631bb5e5dc9326b23f8c00bf43440a84ce711315c6b799de554c56aa04d133` | PENDING（未提交） | 保留的合成组件输入/输出（不替代 IPC/UI） |
| EV-046 | `verification/FEA-09/grant-component/ff9e4640bec54003921ea70a2f69c8fa/source.bin` | 16 | `39631bb5e5dc9326b23f8c00bf43440a84ce711315c6b799de554c56aa04d133` | PENDING（未提交） | 保留的合成组件输入/输出（不替代 IPC/UI） |
| EV-047 | `verification/FEA-09/logs/allowed-paths-audit.json` | 9436 | `abb3ab9cc50113225c05b21809ada6f542f1eea02b9e02f816a268992cde00db` | PENDING（未提交） | 诊断/审计；按原始内容判读 |
| EV-048 | `verification/FEA-09/logs/branch-final.log` | 178 | `4ceb96f076514a9d3e48080b61bb4223c14bd6f6ccb76d925e4631b52ba19808` | PENDING（未提交） | 原始命令输出；EXIT=0 |
| EV-049 | `verification/FEA-09/logs/check-final-r2.log` | 728 | `025cf5ebcac8f90b2f31dc72cf99c6ccad35972b148218f82057fb28dc3498f7` | PENDING（未提交） | 原始命令输出；EXIT=0 |
| EV-050 | `verification/FEA-09/logs/check-final-r3.log` | 728 | `501ab31d2621f0a9c8849475d5f370d73acf482846127ea82feb5d416b8a6d19` | PENDING（未提交） | 原始命令输出；EXIT=0 |
| EV-051 | `verification/FEA-09/logs/check-final.log` | 836 | `02b7cc5510ba2a47b47e7c9544cb044d69f398dae870f1eed89e526f6edf5a09` | PENDING（未提交） | 原始命令输出；EXIT=1 |
| EV-052 | `verification/FEA-09/logs/check-pre-handoff.log` | 728 | `f1f5b70315d5166ab1e066aade5dd3a0ae532c504da17a6271f004e336dbf061` | PENDING（未提交） | 原始命令输出；EXIT=0 |
| EV-053 | `verification/FEA-09/logs/dotnet-build-delivery-checkpoint.log` | 3022 | `e77975194da87cea47a9d83b5fe1171187caa453c28502acd2866987cb5da47f` | PENDING（未提交） | 原始命令输出；EXIT=0 |
| EV-054 | `verification/FEA-09/logs/dotnet-build-evidence-final.log` | 3022 | `40b3fe7b32cab4dded10185236cc787a0ffa3054d0025983e2af3fa74463e4a7` | PENDING（未提交） | 原始命令输出；EXIT=0 |
| EV-055 | `verification/FEA-09/logs/dotnet-build-final.log` | 3022 | `e533f1568ea580012deee849c02e03bb6624da6456888f9bcbfe00cd80abea8e` | PENDING（未提交） | 原始命令输出；EXIT=0 |
| EV-056 | `verification/FEA-09/logs/dotnet-full-r2-summary.json` | 15952 | `26ae0f59f43e017d9697aaf3d568217686b0cb888dd4f4c3af6bddf129381bf8` | PENDING（未提交） | 诊断/审计；按原始内容判读 |
| EV-057 | `verification/FEA-09/logs/dotnet-full-r2.log` | 27861 | `87cbbb297659ae37f62223883a41e094d3cbae95e8083a167a4f758d51b69278` | PENDING（未提交） | 原始命令输出；EXIT=null |
| EV-058 | `verification/FEA-09/logs/dotnet-full.log` | 23550 | `5ee4cb230963eeca40ef0d2eeb11f0739abba1e6dd55c024c1ce8a6ecebf00dc` | PENDING（未提交） | 原始命令输出；EXIT=null |
| EV-059 | `verification/FEA-09/logs/dotnet-phase-c-build-2.log` | 3022 | `9dedf50ebd02444ef2e92f91ec8b7d3ae1ccbb30d0966377e5ad886a4a6401fc` | PENDING（未提交） | 原始命令输出；EXIT=0 |
| EV-060 | `verification/FEA-09/logs/dotnet-phase-c-build-tests.log` | 3022 | `bbb76c3db2bd7d818633e76685cf4d8a6f77efe47b5f328ec1393f97c1072874` | PENDING（未提交） | 原始命令输出；EXIT=0 |
| EV-061 | `verification/FEA-09/logs/dotnet-phase-c-build.log` | 8137 | `3bc2d2511a62fac0c7288cdbd9e0d5e48980df03f29089fe13eaf71a5277d915` | PENDING（未提交） | 原始命令输出；EXIT=1 |
| EV-062 | `verification/FEA-09/logs/dotnet-phase-c-no-restore.log` | 10528 | `73bde6bf0ef94a441784fdc7742f53d8ad2b0e5cdb2ee2df1bd8157b04911ea4` | PENDING（未提交） | 原始命令输出；EXIT=1 |
| EV-063 | `verification/FEA-09/logs/dotnet-phase-c-tests.log` | 6841 | `547b067a33efb4e3cdd8f690df98f5f7107e4e114bc935de1ccbbee2fdb6a576` | PENDING（未提交） | 原始命令输出；EXIT=1 |
| EV-064 | `verification/FEA-09/logs/dotnet-source-command-evidence-final.log` | 779 | `913c40ac251e1bcf914fd8bb607348d76330dab6246362e2ae3e6a91d46a2ad2` | PENDING（未提交） | 原始命令输出；EXIT=0 |
| EV-065 | `verification/FEA-09/logs/dotnet-source-command-regression.log` | 779 | `166e12fac5265e7c45ac9e2db5371fc96b3b5d1ef71c6d966476288fae15fe5b` | PENDING（未提交） | 原始命令输出；EXIT=0 |
| EV-066 | `verification/FEA-09/logs/fea06-png-audit.json` | 1327 | `78654537cdb1bc7b2c71cc7b78207cd5e866a76497ec5fcd752af127c7403d92` | PENDING（未提交） | 诊断/审计；按原始内容判读 |
| EV-067 | `verification/FEA-09/logs/git-stage-blocked.log` | 339 | `0b4e1049f1542754144fe32635df52a6638489c0005b097eb74ed15f8cc5a26c` | f9a2fa8e077f21c93131237171a32e85f6942200 | 原始命令输出；EXIT=128 |
| EV-068 | `verification/FEA-09/logs/git-stage-node-blocked.log` | 1160 | `40f892aada53c585eac43cc180f115d284f93ad78a820f30c3073bcb4b4220b3` | PENDING（未提交） | 诊断/审计；按原始内容判读 |
| EV-069 | `verification/FEA-09/logs/head-final.log` | 231 | `81737eb49324f39cf7e7dd948519e7387cc8082ba53498b986e7d5deb545f505` | PENDING（未提交） | 原始命令输出；EXIT=0 |
| EV-070 | `verification/FEA-09/logs/password-audit.json` | 201 | `1b2d3d3959220a42336753f76c046769d7eaff682a0faf4f354a0fdf87a26453` | PENDING（未提交） | 诊断/审计；按原始内容判读 |
| EV-071 | `verification/FEA-09/logs/pins-final.log` | 625 | `b56ae26c32abb60490aaff86f69d444eed37cab6987d7456233000d00659b04d` | PENDING（未提交） | 原始命令输出；EXIT=0 |
| EV-072 | `verification/FEA-09/logs/pins.log` | 769 | `ea2789d918e83380941e6dba97b438c0ae0fdaff0350ab5c1c93fb84d01ee31e` | PENDING（未提交） | 原始命令输出；EXIT=0 |
| EV-073 | `verification/FEA-09/logs/python-cache-component.log` | 1301 | `8a6e8c9fcb06034ee34f5d5ee49a1fc2a03590df2cd5e92d20fae686c5762d81` | PENDING（未提交） | 原始命令输出；EXIT=0 |
| EV-074 | `verification/FEA-09/logs/python-components-delivery-checkpoint.log` | 2070 | `7d649578f8ea8bfa03858a6fae1faec4f20f3ce580c357deb2150ac448fe7dbe` | PENDING（未提交） | 原始命令输出；EXIT=0 |
| EV-075 | `verification/FEA-09/logs/python-components-final.log` | 2070 | `ea9d6d5c77afcad3410439e676e854b51ebc6f514a9c502177bc79a1d36cbdae` | PENDING（未提交） | 原始命令输出；EXIT=0 |
| EV-076 | `verification/FEA-09/logs/python-final-syntax.log` | 537 | `076c38ecc3d10c3b7736b47ee0bd35cd97c5aa70a5c0d1b6887fe1a05c158700` | PENDING（未提交） | 原始命令输出；EXIT=0 |
| EV-077 | `verification/FEA-09/logs/python-grant-import.log` | 325 | `6c8c8b452c55dac3e078d6610820e33bb272bfb735aa26bb6bd0d01962aedf1a` | PENDING（未提交） | 原始命令输出；EXIT=0 |
| EV-078 | `verification/FEA-09/logs/python-handle-identity-diagnostic.log` | 782 | `f2f64006bc81c61d5ecc31a03ad7edcf8a4e686c1b247cfece80b796cc87cfa8` | PENDING（未提交） | 原始命令输出；EXIT=0 |
| EV-079 | `verification/FEA-09/logs/python-phase-c-baseline.log` | 321 | `1d6b284efbd6edd684a0af844aaa1d69e4b4a6b4ee6e29bfb388d729089283e8` | PENDING（未提交） | 诊断/审计；按原始内容判读 |
| EV-080 | `verification/FEA-09/logs/python-source-grant-component-r2.log` | 6742 | `1d208f97e71b72ea721a16365aa5e598e06de53f0adbb8ef3061b5c4ee8eb4c9` | PENDING（未提交） | 原始命令输出；EXIT=1 |
| EV-081 | `verification/FEA-09/logs/python-source-grant-component-r3.log` | 1226 | `7354c95f0485ec1d49ec85877ecaaecbac2d0855219d6e0aef7e0066bdf90bd7` | PENDING（未提交） | 原始命令输出；EXIT=0 |
| EV-082 | `verification/FEA-09/logs/python-source-grant-component.log` | 5243 | `324dbe84a4678f1bc3494b3a2346aefbef0892a603f6bc107fe5805a5a373756` | PENDING（未提交） | 原始命令输出；EXIT=1 |
| EV-083 | `verification/FEA-09/logs/python-syntax.log` | 653 | `f58fed6adade37326bd137cec481da85d0a975f6c7927c6bf0890434911b830e` | PENDING（未提交） | 原始命令输出；EXIT=0 |
| EV-084 | `verification/FEA-09/logs/python-test-dependencies.log` | 2862 | `78f6335d11a62c99178ef41f208aee53a0094d606a779d449c457477f840fc9a` | PENDING（未提交） | 诊断/审计；按原始内容判读 |
| EV-085 | `verification/FEA-09/logs/recovery-git-state.log` | 3203 | `7fd7db63bba26444bcdf7ab27567e0ee3a6b41eb8583af077d410027b8f9cb0f` | PENDING（未提交） | 原始命令输出；EXIT=0 |
| EV-086 | `verification/FEA-09/logs/test-process-status.log` | 448 | `54d92d5d020d6ab69b0f64afeb0b580f0034e31d300cbdcb65379f58153c7faa` | PENDING（未提交） | 原始命令输出；EXIT=1 |
| EV-087 | `verification/FEA-09/logs/wire-redacted.ndjson` | 834 | `ff118a791b9361f2edb1f0d714a064c21e7bd35a2bb85c7d63082f49f72a2a8f` | PENDING（未提交） | 诊断/审计；按原始内容判读 |
| EV-088 | `verification/FEA-09/native-registry/4d91633ce3db4c1d9007c3ca3cd846c4/synthetic-source/page.txt` | 22 | `b2a5ce4fa952eac4169705f6cfbe8865d1a7149bd3909416186aa9f8297054a3` | PENDING（未提交） | 原生失败测试留下的合成输入；非成功 Registry 证据 |
| EV-089 | `verification/FEA-09/native-registry/4fac051ab40b45c6896dc3a6b9715cf8/synthetic-source/page.txt` | 22 | `b2a5ce4fa952eac4169705f6cfbe8865d1a7149bd3909416186aa9f8297054a3` | PENDING（未提交） | 原生失败测试留下的合成输入；非成功 Registry 证据 |
| EV-090 | `verification/FEA-09/native-registry/7822489190664193a4a52ef899785a61/synthetic-source/page.txt` | 22 | `b2a5ce4fa952eac4169705f6cfbe8865d1a7149bd3909416186aa9f8297054a3` | PENDING（未提交） | 原生失败测试留下的合成输入；非成功 Registry 证据 |
| EV-091 | `verification/FEA-09/working-tree-files.json` | 4964 | `ab3c7707843eb61fd1aed0478953c14eed17b76a3878f039cb75eb09cb1d51b4` | PENDING（未提交） | 工作树恢复清单 |

| EV-META | `verification/FEA-09/EV.md` | SELF | 自引用元数据不做自身 hash | PENDING（未提交） | 非产品验收证据；本清单不自行证明独审/提交/集成成功 |
| EV-090 | `verification/FEA-09/logs/dsh-referenced-resolve.log` | 3415 | `4494491a105e48d8dc9a47ccd0afa561c360d95079c42995d67b1cb075ff4fda` | `3f2056555716c6880b1ddc10007a375f01e27568` | CANONICAL：referenced 生产 resolve + 密码接线 + cache/预算（实现/测试/命令/结果）；不替代真实 IPC/V2 与独立 Review |
