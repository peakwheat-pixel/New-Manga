# SHA-256 不匹配的逐行证据链

**依据**：`codex-debt-ruling.md` §1。裁定原文要点：三种行尾 hash 都不匹配**只证明字节不同，
不证明谁对**；只有证据链能说明「当前文件是后来经授权选作该 AC 的证据」才可判 pin 过时。
**本表只提供判据所需事实，分类与处置归 Codex。**

`state` 列含义：

| state | 含义 | 对裁定的意义 |
|---|---|---|
| `pin_matches_at_commit` | pin 与该 commit 里该文件的内容一致 | pin 写下时是准确的；**当前文件后来变了**，需查这次变化是否获授权 |
| `pin_differs_at_commit` | pin 与该 commit 里的内容也不一致 | pin 从一开始就不对（或 pin 取自其它版本），**pin 本身不可信** |
| `file_absent_at_pinned_commit` | pin 的 commit 里没有这个文件 | 该行 pin 无效（与 §8 那 52 行同类问题） |
| `no_commit_pin` | 该行没有 commit pin，只有 sha | 无法据此回溯历史，需看 sha 来源记录 |

共 **102** 行（文件存在且 hash 与 pin 不符）。

## 汇总

| state | 行数 |
|---|---:|
| `pin_matches_at_commit` | 78 |
| `pin_differs_at_commit` | 24 |

### 与「工作区是否等于 HEAD」交叉

这一列把「pin 写错」和「文件被改」分开，是裁定 §1 最需要的东西：

| state | 工作区 = HEAD | 行数 | 推论 |
|---|---|---:|---|
| `pin_matches_at_commit` | yes | 78 | pin 写下时准确，且工作区与 HEAD 一致 —— 文件是在后续**正常提交**中演进的，pin 确实过时 |
| `pin_differs_at_commit` | yes | 13 | pin 与该 commit 的内容不符，而工作区与 HEAD 一致 —— pin 从一开始就不对（或取自别处），文件本身未被改动 |
| `pin_differs_at_commit` | **no** | 11 | pin 不符**且**工作区有未提交修改 —— 两项问题叠加，需优先排查 |

## ENV-BUNDLE-1（2 行）

| 行 | path | pin 的 commit | 当前 hash | pin | 该 commit 处 hash | 工作区=HEAD | state |
|---:|---|---|---|---|---|---|---|
| 135 | `main.rs` | c6fda8a09c1a | `f8fd657c12e4…` | `21972b00bdcf…` | `21972b00bdcf…` | yes | `pin_matches_at_commit` |
| 136 | `library_bridge.rs` | c6fda8a09c1a | `d4825b8a7f91…` | `7599fd78c3c5…` | `7599fd78c3c5…` | yes | `pin_matches_at_commit` |

## EXPORT-REVEAL-1（1 行）

| 行 | path | pin 的 commit | 当前 hash | pin | 该 commit 处 hash | 工作区=HEAD | state |
|---:|---|---|---|---|---|---|---|
| 119 | `M2-C1_TYPED_IPC_CONTRACT.md` | b1e4d87d4929 | `e4704e075595…` | `7d95a873a7e2…` | `7d95a873a7e2…` | yes | `pin_matches_at_commit` |

## FEAT-IMPORT-MULTI-1（2 行）

| 行 | path | pin 的 commit | 当前 hash | pin | 该 commit 处 hash | 工作区=HEAD | state |
|---:|---|---|---|---|---|---|---|
| 77 | `main.rs` | 8b1a1da1774d | `f8fd657c12e4…` | `b9d74da3f483…` | `b9d74da3f483…` | yes | `pin_matches_at_commit` |
| 78 | `library_bridge.rs` | 8b1a1da1774d | `d4825b8a7f91…` | `3a21e06c0a68…` | `3a21e06c0a68…` | yes | `pin_matches_at_commit` |

## HOST-CORE-1（1 行）

| 行 | path | pin 的 commit | 当前 hash | pin | 该 commit 处 hash | 工作区=HEAD | state |
|---:|---|---|---|---|---|---|---|
| 128 | `M2-C1_TYPED_IPC_CONTRACT.md` | 97c2d559c615 | `e4704e075595…` | `6a2f38e0b170…` | `6a2f38e0b170…` | yes | `pin_matches_at_commit` |

## HOST-ISSUER-1（6 行）

| 行 | path | pin 的 commit | 当前 hash | pin | 该 commit 处 hash | 工作区=HEAD | state |
|---:|---|---|---|---|---|---|---|
| 268 | `host_issuer.rs` | 2ad590a31ac2 | `00b1b7a3821f…` | `ef1ab4ef4b6a…` | `ef1ab4ef4b6a…` | yes | `pin_matches_at_commit` |
| 269 | `library_bridge.rs` | 2ad590a31ac2 | `d4825b8a7f91…` | `7599fd78c3c5…` | `7599fd78c3c5…` | yes | `pin_matches_at_commit` |
| 270 | `main.rs` | 2ad590a31ac2 | `f8fd657c12e4…` | `21972b00bdcf…` | `21972b00bdcf…` | yes | `pin_matches_at_commit` |
| 271 | `build.rs` | 2ad590a31ac2 | `371dc9117d84…` | `c2b80e6dd708…` | `c2b80e6dd708…` | yes | `pin_matches_at_commit` |
| 272 | `m2rc1-commands.json` | 2ad590a31ac2 | `39298d98f5e5…` | `4db32b0d0ae2…` | `4db32b0d0ae2…` | yes | `pin_matches_at_commit` |
| 273 | `M2-C1_TYPED_IPC_CONTRACT.md` | 8a990a345c91 | `e4704e075595…` | `6a2f38e0b170…` | `6a2f38e0b170…` | yes | `pin_matches_at_commit` |

## HOST-ISSUER-1-C1（2 行）

| 行 | path | pin 的 commit | 当前 hash | pin | 该 commit 处 hash | 工作区=HEAD | state |
|---:|---|---|---|---|---|---|---|
| 106 | `M2-C1_TYPED_IPC_CONTRACT.md` | af6fa705de54 | `e4704e075595…` | `6a2f38e0b170…` | `6a2f38e0b170…` | yes | `pin_matches_at_commit` |
| 111 | `HOST-ISSUER-1.md` | 6a5051dcafa5 | `85bddd6c1e99…` | `d4926c93627b…` | `25b58cac8f04…` | yes | `pin_differs_at_commit` |

## HOST-TTL-BOUNDARY-1（3 行）

| 行 | path | pin 的 commit | 当前 hash | pin | 该 commit 处 hash | 工作区=HEAD | state |
|---:|---|---|---|---|---|---|---|
| 147 | `ac6-rust-concurrency-diagnostic-6284f6f.jsonl` | a4bc60dca0f3 | `170384aaaf3b…` | `67d01f0661a1…` | `2ed7d937e8ad…` | yes | `pin_differs_at_commit` |
| 154 | `ac6-export-rust-concurrency-diagnostic-7fbce30.jsonl` | fdf974645f4d | `99c1da564bf0…` | `1fc9e10c1aff…` | `f7518ce74924…` | yes | `pin_differs_at_commit` |
| 157 | `M2-C1_TYPED_IPC_CONTRACT.md` | af6fa705de54 | `e4704e075595…` | `6a2f38e0b170…` | `6a2f38e0b170…` | yes | `pin_matches_at_commit` |

## P09（1 行）

| 行 | path | pin 的 commit | 当前 hash | pin | 该 commit 处 hash | 工作区=HEAD | state |
|---:|---|---|---|---|---|---|---|
| 128 | `AC3-source-hashes.json` | 8ab617f2e996 | `56e40a827c20…` | `6c2018642ae5…` | `6c2018642ae5…` | yes | `pin_matches_at_commit` |

## P09-AC3-DELETE-1（1 行）

| 行 | path | pin 的 commit | 当前 hash | pin | 该 commit 处 hash | 工作区=HEAD | state |
|---:|---|---|---|---|---|---|---|
| 149 | `M2-C1_TYPED_IPC_CONTRACT.md` | 694de50789de | `e4704e075595…` | `f954c2fda2fb…` | `f954c2fda2fb…` | yes | `pin_matches_at_commit` |

## P09-AC3-DELETE-HARDEN-1（2 行）

| 行 | path | pin 的 commit | 当前 hash | pin | 该 commit 处 hash | 工作区=HEAD | state |
|---:|---|---|---|---|---|---|---|
| 133 | `library.py` | a73bf6b10b76 | `cf06fa8d0135…` | `abfab663f2b2…` | `2243c80e99d9…` | yes | `pin_differs_at_commit` |
| 134 | `core_service.py` | 51bd814d11f6 | `3417c8cd85d6…` | `e3ffba1e0e6b…` | `e3ffba1e0e6b…` | yes | `pin_matches_at_commit` |

## P09-FU2（2 行）

| 行 | path | pin 的 commit | 当前 hash | pin | 该 commit 处 hash | 工作区=HEAD | state |
|---:|---|---|---|---|---|---|---|
| 121 | `M2-C1_TYPED_IPC_CONTRACT.md` | 9fe6ac5cd116 | `e4704e075595…` | `b8cadc27572a…` | `b8cadc27572a…` | yes | `pin_matches_at_commit` |
| 123 | `P09.md` | 9fe6ac5cd116 | `7ad1634e7560…` | `289a6c0b5bb8…` | `8de16d26faff…` | yes | `pin_differs_at_commit` |

## P12-C1（3 行）

| 行 | path | pin 的 commit | 当前 hash | pin | 该 commit 处 hash | 工作区=HEAD | state |
|---:|---|---|---|---|---|---|---|
| 113 | `M2-C1_TYPED_IPC_CONTRACT.md` | 919ca24731f5 | `e4704e075595…` | `b8cadc27572a…` | `b8cadc27572a…` | yes | `pin_matches_at_commit` |
| 119 | `P09.md` | 58e70f0bba62 | `7ad1634e7560…` | `289a6c0b5bb8…` | `8de16d26faff…` | yes | `pin_differs_at_commit` |
| 124 | `library.py` | dc254fa93ca0 | `cf06fa8d0135…` | `61c9c7d810fd…` | `61c9c7d810fd…` | yes | `pin_matches_at_commit` |

## P13-C1（6 行）

| 行 | path | pin 的 commit | 当前 hash | pin | 该 commit 处 hash | 工作区=HEAD | state |
|---:|---|---|---|---|---|---|---|
| 112 | `M2-C1_TYPED_IPC_CONTRACT.md` | ed79a2b778e1 | `e4704e075595…` | `e29d1acf861f…` | `e29d1acf861f…` | yes | `pin_matches_at_commit` |
| 121 | `P13.md` | c33033dc02c4 | `7253c844fdf1…` | `de74d3498717…` | `f74718c93204…` | yes | `pin_differs_at_commit` |
| 122 | `service.py` | c33033dc02c4 | `daeb84ce31cd…` | `05c0db8d92ae…` | `05c0db8d92ae…` | yes | `pin_matches_at_commit` |
| 123 | `store.py` | c33033dc02c4 | `da3c1848d628…` | `0e08d2e5aa25…` | `0e08d2e5aa25…` | yes | `pin_matches_at_commit` |
| 124 | `projection.py` | c33033dc02c4 | `da331e426b47…` | `1027d4b527de…` | `1027d4b527de…` | yes | `pin_matches_at_commit` |
| 125 | `core_service.py` | c33033dc02c4 | `3417c8cd85d6…` | `96ba2291d092…` | `96ba2291d092…` | yes | `pin_matches_at_commit` |

## P15（1 行）

| 行 | path | pin 的 commit | 当前 hash | pin | 该 commit 处 hash | 工作区=HEAD | state |
|---:|---|---|---|---|---|---|---|
| 94 | `SettingsPage.test.tsx` | e5f1a719bdaf | `39cb97551be3…` | `4f6c8fe623f8…` | `4f6c8fe623f8…` | yes | `pin_matches_at_commit` |

## P15-C1（1 行）

| 行 | path | pin 的 commit | 当前 hash | pin | 该 commit 处 hash | 工作区=HEAD | state |
|---:|---|---|---|---|---|---|---|
| 89 | `P15_SETTINGS_IPC_CONTRACT.md` | 8d083ee186ee | `8ed67053433b…` | `1238400ca8a7…` | `1238400ca8a7…` | yes | `pin_matches_at_commit` |

## P15-C1-FU1（2 行）

| 行 | path | pin 的 commit | 当前 hash | pin | 该 commit 处 hash | 工作区=HEAD | state |
|---:|---|---|---|---|---|---|---|
| 72 | `P15_SETTINGS_IPC_CONTRACT.md` | eeae29831b4f | `8ed67053433b…` | `b6b29246c01c…` | `b6b29246c01c…` | yes | `pin_matches_at_commit` |
| 76 | `M2-C1_TYPED_IPC_CONTRACT.md` | 82ce23bd50e4 | `e4704e075595…` | `b85b23fd4d78…` | `b85b23fd4d78…` | yes | `pin_matches_at_commit` |

## P15-C1-FU2（1 行）

| 行 | path | pin 的 commit | 当前 hash | pin | 该 commit 处 hash | 工作区=HEAD | state |
|---:|---|---|---|---|---|---|---|
| 55 | `P15-HOST-1.md` | ac430e2c732e | `1a64ab846f6a…` | `30d6dada3fe1…` | `30d6dada3fe1…` | yes | `pin_matches_at_commit` |

## P15-CORE-1A（6 行）

| 行 | path | pin 的 commit | 当前 hash | pin | 该 commit 处 hash | 工作区=HEAD | state |
|---:|---|---|---|---|---|---|---|
| 67 | `P15_SETTINGS_IPC_CONTRACT.md` | b1f4d08c79ad | `8ed67053433b…` | `b6b29246c01c…` | `cff5dad0ff5e…` | yes | `pin_differs_at_commit` |
| 70 | `settings_commands.py` | 9232802c08b9 | `17bc0f75e933…` | `a9b1ad574b8d…` | `a9b1ad574b8d…` | yes | `pin_matches_at_commit` |
| 71 | `core_service.py` | 9232802c08b9 | `3417c8cd85d6…` | `33ddb0f83b8d…` | `15a01e5ff901…` | yes | `pin_differs_at_commit` |
| 72 | `core_assembly.py` | 9232802c08b9 | `ee09ef05c0f6…` | `95b3267166f3…` | `95b3267166f3…` | yes | `pin_matches_at_commit` |
| 73 | `service.py` | 9232802c08b9 | `daeb84ce31cd…` | `efaa266ad2ad…` | `efaa266ad2ad…` | yes | `pin_matches_at_commit` |
| 75 | `json_profile_stores.py` | 9232802c08b9 | `b191a9e02a88…` | `47b15a0dfd6b…` | `47b15a0dfd6b…` | yes | `pin_matches_at_commit` |

## P15-CORE-1B（5 行）

| 行 | path | pin 的 commit | 当前 hash | pin | 该 commit 处 hash | 工作区=HEAD | state |
|---:|---|---|---|---|---|---|---|
| 66 | `P15_SETTINGS_IPC_CONTRACT.md` | c279659117db | `8ed67053433b…` | `b6b29246c01c…` | `b6b29246c01c…` | yes | `pin_matches_at_commit` |
| 68 | `main.rs` | c279659117db | `f8fd657c12e4…` | `2a6852c425e6…` | `2a6852c425e6…` | yes | `pin_matches_at_commit` |
| 69 | `settings_commands.py` | 6cf3c8209905 | `17bc0f75e933…` | `c26173e9440d…` | `c26173e9440d…` | yes | `pin_matches_at_commit` |
| 70 | `core_service.py` | 6cf3c8209905 | `3417c8cd85d6…` | `4d5c08a061a5…` | `4d5c08a061a5…` | yes | `pin_matches_at_commit` |
| 72 | `core_assembly.py` | 6cf3c8209905 | `ee09ef05c0f6…` | `95b3267166f3…` | `95b3267166f3…` | yes | `pin_matches_at_commit` |

## P15-CORE-1C（2 行）

| 行 | path | pin 的 commit | 当前 hash | pin | 该 commit 处 hash | 工作区=HEAD | state |
|---:|---|---|---|---|---|---|---|
| 66 | `core_service.py` | 52b0974ade02 | `3417c8cd85d6…` | `f0cae3d2286b…` | `f0cae3d2286b…` | yes | `pin_matches_at_commit` |
| 76 | `P15_SETTINGS_IPC_CONTRACT.md` | 5f5431b8718b | `8ed67053433b…` | `b6b29246c01c…` | `b6b29246c01c…` | yes | `pin_matches_at_commit` |

## P16（1 行）

| 行 | path | pin 的 commit | 当前 hash | pin | 该 commit 处 hash | 工作区=HEAD | state |
|---:|---|---|---|---|---|---|---|
| 141 | `M2-C1_TYPED_IPC_CONTRACT.md` | 093430c75a46 | `e4704e075595…` | `91308343d868…` | `91308343d868…` | yes | `pin_matches_at_commit` |

## P16-C1（1 行）

| 行 | path | pin 的 commit | 当前 hash | pin | 该 commit 处 hash | 工作区=HEAD | state |
|---:|---|---|---|---|---|---|---|
| 123 | `M2-C1_TYPED_IPC_CONTRACT.md` | 196f50d45bc5 | `e4704e075595…` | `91308343d868…` | `91308343d868…` | yes | `pin_matches_at_commit` |

## P17（2 行）

| 行 | path | pin 的 commit | 当前 hash | pin | 该 commit 处 hash | 工作区=HEAD | state |
|---:|---|---|---|---|---|---|---|
| 108 | `pytest.log` | 55b9ff3f88dd | `fcc99dba03a6…` | `cc92ade6d2a7…` | `e9323e15d25e…` | yes | `pin_differs_at_commit` |
| 110 | `cargo-packaged.log` | 55b9ff3f88dd | `23a52dabe17e…` | `f4d61723d54a…` | `ffdc75cd28eb…` | yes | `pin_differs_at_commit` |

## P19-UI-FIX-1（2 行）

| 行 | path | pin 的 commit | 当前 hash | pin | 该 commit 处 hash | 工作区=HEAD | state |
|---:|---|---|---|---|---|---|---|
| 68 | `frontend-npm-test-final.log` | 5dd4b2af0a0c | `b13792aa4486…` | `2f6bd61d4acd…` | `d2dcf5a1e6e1…` | yes | `pin_differs_at_commit` |
| 69 | `frontend-npm-build-final.log` | 5dd4b2af0a0c | `a796ef6fde2a…` | `80c9e7ebc60d…` | `10f73f56a5d0…` | yes | `pin_differs_at_commit` |

## P20-CLOSE-BOUND-1（42 行）

| 行 | path | pin 的 commit | 当前 hash | pin | 该 commit 处 hash | 工作区=HEAD | state |
|---:|---|---|---|---|---|---|---|
| 99 | `library_bridge.rs` | 835f4bb17df5 | `d4825b8a7f91…` | `137627011322…` | `137627011322…` | yes | `pin_matches_at_commit` |
| 100 | `concurrency-lock-audit.md` | 835f4bb17df5 | `65bdaf65c846…` | `ae3c77608100…` | `ae3c77608100…` | yes | `pin_matches_at_commit` |
| 112 | `run-desktop-close-verification.ps1` | 835f4bb17df5 | `a0043b6deb2a…` | `ac83b01696a5…` | `ac83b01696a5…` | yes | `pin_matches_at_commit` |
| 113 | `test-ac1-overlay-bound.ps1` | 835f4bb17df5 | `23c6fd71c34d…` | `96da0aea7d8f…` | `96da0aea7d8f…` | yes | `pin_matches_at_commit` |
| 127 | `library_bridge.rs` | 5021f039ffb0 | `d4825b8a7f91…` | `1b971be36998…` | `1b971be36998…` | yes | `pin_matches_at_commit` |
| 128 | `ac1-overlay-bound.stdout.log` | 5021f039ffb0 | `326143e82a36…` | `23e21acc93ad…` | `e846eb7f9d65…` | **no** | `pin_differs_at_commit` |
| 130 | `ac1-overlay-bound.meta.json` | 5021f039ffb0 | `e1787e411800…` | `5110ee61d4d9…` | `5110ee61d4d9…` | yes | `pin_matches_at_commit` |
| 131 | `ac1-overlay-bound.stderr.log` | 5021f039ffb0 | `7b8fec9631a6…` | `6cc77fe9cb7e…` | `6cc77fe9cb7e…` | yes | `pin_matches_at_commit` |
| 132 | `ac1-shutdown-writes.stdout.log` | 5021f039ffb0 | `c0215e864b95…` | `43a6c224e53f…` | `17567c764af4…` | **no** | `pin_differs_at_commit` |
| 134 | `ac1-shutdown-writes.meta.json` | 5021f039ffb0 | `2d10347d35df…` | `496a472ce102…` | `496a472ce102…` | yes | `pin_matches_at_commit` |
| 135 | `ac1-shutdown-writes.stderr.log` | 5021f039ffb0 | `47568d8e3a57…` | `732cb3180356…` | `732cb3180356…` | yes | `pin_matches_at_commit` |
| 136 | `ac2-process-tree-audit.log` | 5021f039ffb0 | `a2203a7e20fb…` | `142335992cb5…` | `142335992cb5…` | yes | `pin_matches_at_commit` |
| 138 | `ac2-process-tree-audit.meta.json` | 2ad0000a2649 | `0f64a90991e9…` | `f8379c2a7cf6…` | `f8379c2a7cf6…` | yes | `pin_matches_at_commit` |
| 139 | `ac3-resilient-channel.stdout.log` | 5021f039ffb0 | `6a4e1a8d1669…` | `26f240b8cfcf…` | `c2bb774c0f8c…` | **no** | `pin_differs_at_commit` |
| 141 | `ac3-resilient-channel.meta.json` | 5021f039ffb0 | `612b9b25cdf3…` | `10eaff6e2b94…` | `10eaff6e2b94…` | yes | `pin_matches_at_commit` |
| 142 | `ac3-resilient-channel.stderr.log` | 5021f039ffb0 | `732cb3180356…` | `88dfdbd6bd65…` | `88dfdbd6bd65…` | yes | `pin_matches_at_commit` |
| 143 | `ac3-stdio-channel-drop.stdout.log` | 5021f039ffb0 | `1ed09b2acccd…` | `b122646bb55f…` | `d3776b8cc398…` | **no** | `pin_differs_at_commit` |
| 145 | `ac3-stdio-channel-drop.meta.json` | 5021f039ffb0 | `d5e4fab6e928…` | `8d046b2c24bb…` | `8d046b2c24bb…` | yes | `pin_matches_at_commit` |
| 146 | `ac3-stdio-channel-drop.stderr.log` | 5021f039ffb0 | `47568d8e3a57…` | `cf8b9c2ef661…` | `cf8b9c2ef661…` | yes | `pin_matches_at_commit` |
| 147 | `concurrency-lock-audit.md` | 5021f039ffb0 | `65bdaf65c846…` | `607036d77e4b…` | `607036d77e4b…` | yes | `pin_matches_at_commit` |
| 148 | `ac4-wait-timeout-or-kill.stdout.log` | 5021f039ffb0 | `3c29317bdcd5…` | `ac3d32ce443e…` | `42484427d767…` | **no** | `pin_differs_at_commit` |
| 150 | `ac4-wait-timeout-or-kill.meta.json` | 5021f039ffb0 | `efacde57e43f…` | `fbceedc3a77f…` | `fbceedc3a77f…` | yes | `pin_matches_at_commit` |
| 151 | `ac4-wait-timeout-or-kill.stderr.log` | 5021f039ffb0 | `47568d8e3a57…` | `708c181b553c…` | `708c181b553c…` | yes | `pin_matches_at_commit` |
| 152 | `ac4-reader-guard.stdout.log` | 5021f039ffb0 | `2b93e1dfd2c9…` | `77ed707523c9…` | `1cec8bd2990b…` | **no** | `pin_differs_at_commit` |
| 154 | `ac4-reader-guard.meta.json` | 5021f039ffb0 | `7fcd5aa21b9b…` | `3be8c4f02162…` | `3be8c4f02162…` | yes | `pin_matches_at_commit` |
| 155 | `ac4-reader-guard.stderr.log` | 5021f039ffb0 | `88dfdbd6bd65…` | `f67efd8862bc…` | `f67efd8862bc…` | yes | `pin_matches_at_commit` |
| 156 | `ac4-poisoned-child-lock.stdout.log` | 5021f039ffb0 | `eec452b399e4…` | `ae0b34d977df…` | `c6003f8a5dcd…` | **no** | `pin_differs_at_commit` |
| 158 | `ac4-poisoned-child-lock.meta.json` | 5021f039ffb0 | `ae283df3b6f7…` | `6734f5809baf…` | `6734f5809baf…` | yes | `pin_matches_at_commit` |
| 159 | `ac4-poisoned-child-lock.stderr.log` | 5021f039ffb0 | `cf8b9c2ef661…` | `88dfdbd6bd65…` | `88dfdbd6bd65…` | yes | `pin_matches_at_commit` |
| 160 | `ac4-child-lock-contention.stdout.log` | 5021f039ffb0 | `1b88d8bcd628…` | `92ec58d49cf3…` | `a18299204c15…` | **no** | `pin_differs_at_commit` |
| 162 | `ac4-child-lock-contention.meta.json` | 5021f039ffb0 | `b5c19d205fab…` | `b619e97f4b8f…` | `b619e97f4b8f…` | yes | `pin_matches_at_commit` |
| 163 | `ac4-child-lock-contention.stderr.log` | 5021f039ffb0 | `c3dc286ca19d…` | `3c066d26b93a…` | `3c066d26b93a…` | yes | `pin_matches_at_commit` |
| 164 | `ac4-pending-lock-contention.stdout.log` | 5021f039ffb0 | `3bf6f5326bd7…` | `607627a3d7a5…` | `8556c4ef43a9…` | **no** | `pin_differs_at_commit` |
| 166 | `ac4-pending-lock-contention.meta.json` | 5021f039ffb0 | `57324fc87579…` | `25955d72fd0d…` | `25955d72fd0d…` | yes | `pin_matches_at_commit` |
| 167 | `ac4-pending-lock-contention.stderr.log` | 5021f039ffb0 | `3034a8c9a689…` | `08ab0d2aec93…` | `08ab0d2aec93…` | yes | `pin_matches_at_commit` |
| 168 | `ac4-writer-pipe-overflow.stdout.log` | 5021f039ffb0 | `6f97780efcbb…` | `c1a44d20e4c3…` | `93667fdd4e42…` | **no** | `pin_differs_at_commit` |
| 170 | `ac4-writer-pipe-overflow.meta.json` | 5021f039ffb0 | `695301a5e653…` | `4a8a153840ef…` | `4a8a153840ef…` | yes | `pin_matches_at_commit` |
| 171 | `ac4-writer-pipe-overflow.stderr.log` | 5021f039ffb0 | `cf8b9c2ef661…` | `88dfdbd6bd65…` | `88dfdbd6bd65…` | yes | `pin_matches_at_commit` |
| 172 | `ac4-inner-lock-contention.stdout.log` | 2ad0000a2649 | `d9942f1bf91e…` | `9e78719e791f…` | `708e59763d65…` | **no** | `pin_differs_at_commit` |
| 174 | `ac4-inner-lock-contention.meta.json` | 2ad0000a2649 | `a8670a7af7c1…` | `d6355ac31d7e…` | `d6355ac31d7e…` | yes | `pin_matches_at_commit` |
| 176 | `run-desktop-close-verification.ps1` | 5021f039ffb0 | `a0043b6deb2a…` | `f3f45a17147e…` | `f3f45a17147e…` | yes | `pin_matches_at_commit` |
| 179 | `test-ac1-overlay-bound.ps1` | 5021f039ffb0 | `23c6fd71c34d…` | `e55093bc83e4…` | `e55093bc83e4…` | yes | `pin_matches_at_commit` |

## P20-ISOLATION-1（1 行）

| 行 | path | pin 的 commit | 当前 hash | pin | 该 commit 处 hash | 工作区=HEAD | state |
|---:|---|---|---|---|---|---|---|
| 76 | `library_bridge.rs` | e16f538f7f0c | `d4825b8a7f91…` | `f2bae7687bbc…` | `f2bae7687bbc…` | yes | `pin_matches_at_commit` |

## P22-REBASE-1（2 行）

| 行 | path | pin 的 commit | 当前 hash | pin | 该 commit 处 hash | 工作区=HEAD | state |
|---:|---|---|---|---|---|---|---|
| 144 | `library_bridge.rs` | 61c806c9e17d | `d4825b8a7f91…` | `bb0f4cabe31b…` | `bb0f4cabe31b…` | yes | `pin_matches_at_commit` |
| 146 | `library_bridge.rs` | 4e5c71d9f0a6 | `d4825b8a7f91…` | `bb0f4cabe31b…` | `bb0f4cabe31b…` | yes | `pin_matches_at_commit` |

## SEC-FIX-PATH-ECHO-1（1 行）

| 行 | path | pin 的 commit | 当前 hash | pin | 该 commit 处 hash | 工作区=HEAD | state |
|---:|---|---|---|---|---|---|---|
| 69 | `core_service.py` | 022f4d73773a | `3417c8cd85d6…` | `d51b60db4cc3…` | `d51b60db4cc3…` | yes | `pin_matches_at_commit` |

## 边界

- 本表**不判定**任何一行是「pin 过时」还是「文件被改」。
- 也不判断当前内容是否仍能支撑对应 AC —— 那是裁定 §1 要求 Codex 逐项确认的事。
- 本表不修改任何 pin、不重钉、不标记 SUPERSEDED。
