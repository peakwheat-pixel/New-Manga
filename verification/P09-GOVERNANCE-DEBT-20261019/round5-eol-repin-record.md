# Round-5 EOL re-pin audit record

**Purpose**: satisfy `codex-debt-ruling.md` §1 requirement that an LF/CRLF-only
pin correction keep the original value on record.

**Commit**: `72c813963` — `docs(tasks): re-pin evidence hashes that differed only by line endings`

**Proof used before changing anything**: for every row below,
`sha256(working-tree bytes) != pin` **but** `sha256(content with CRLF collapsed to LF) == pin`.
That equality proves the file content is unchanged and only the end-of-line
representation moved (`core.autocrlf=true` checks these out as CRLF while the pins were
taken from the Git blob, which stores LF). Rows where none of raw/LF/CRLF matched the
pin were classed `content_differs` and were **not** touched (those remain debt).

**Totals**: 78 rows across 13 tasks.

| Task | line | path | original pin (LF form, kept for audit) | new pin (working-tree bytes) |
|---|---:|---|---|---|
| ARCH-DOC-REBASELINE | 84 | `verification/ARCH-DOC-REBASELINE/source-pins.json` | `1200e967a03f7caad259244cc11e724b35f97e859120a4ef56dbfea54a01f977` | `75f7622d3fd946689746bbe71ff4f63a284c800f69d4eca5d32a761bba60c230` |
| ARCH-DOC-REBASELINE | 85 | `verification/ARCH-DOC-REBASELINE/ac1-coverage-and-sources.md` | `577695c0ea10684def679a0bd76dc7553d89fe78837095e13208536a2eb5fb7b` | `e767e5a8f7558d3657b1840ce8bac21e2f23bf1eb56ed7be39c4a07e4085d88e` |
| ARCH-DOC-REBASELINE | 86 | `verification/ARCH-DOC-REBASELINE/ac2-cross-document-consistency.md` | `a28c60c5b1d2b8f6e8285c229c96269748fde08fa1905b61ebb6f6b6fe5d8778` | `1b69f0836fed9f3c7cdcb0bb21bd95d441898a256cbd171eab069d29994cde21` |
| ARCH-DOC-REBASELINE | 87 | `verification/ARCH-DOC-REBASELINE/ac3-four-pages-and-deferred.md` | `94bcd0722e820f1778cce2b943725fda8908df5e2f37242c01aa79caf8d9dc12` | `4453f4ef27b08a13df518c714effc6b6efee6801e8240ab44b27ecb9a6e57ea6` |
| ARCH-DOC-REBASELINE | 88 | `verification/ARCH-DOC-REBASELINE/ac4-p18-quality-and-responsibility.md` | `d8bb1a38af31c3ed76e5f081680b07515ad184aa307e3d87afc75776d71cc87d` | `28b356628d8a086bf44a0f1a6fb0316ad52084d432e233436d827484b6dbf962` |
| ARCH-DOC-REBASELINE | 89 | `verification/ARCH-DOC-REBASELINE/ac5-p20-nfr-stack-rebaseline.md` | `bb29dc6fa2a154e8209987e7d4a6b2a259d081a0bb91147d36e62e64f4264044` | `a103c84746c722cd2041fbf4ec1bbaace4d4b6f57c3e1693abdcae188128343c` |
| ARCH-DOC-REBASELINE | 90 | `verification/ARCH-DOC-REBASELINE/ac6-p08-fmt-traceability.md` | `b0276a9c78f217a2398e4367a83783345058bf2a70b89e23fad23af8d0d20ede` | `48156cc15757d41d6edf419cd83c9228055a4152a98f0b92f25a212822b607a6` |
| ARCH-DOC-REBASELINE | 91 | `verification/ARCH-DOC-REBASELINE/rebaseline-summary.md` | `7703a92bea5cc55f516055ae29b66e8c1196533940e9dba6ea53cdd62614d4f5` | `6f93cd89ad212504682023694200765e08a6c3446f0aaec09472e4ea81c6c620` |
| ENV-BUNDLE-1-FU1 | 146 | `verification/ENV-BUNDLE-1-FU1/preflight.md` | `6e02a7f50aaf31046cf188a54ae89aeceb0c915a3d1973d9e9c6becc304282fd` | `a8db2f27b9e9a4e6092ebfbcd147b785ddad90df358e69eebd34d9370b98bcee` |
| ENV-BUNDLE-1-FU1 | 147 | `verification/ENV-BUNDLE-1-FU1/ac1-build-sidecar.log` | `f2468474be2a3a47cf7a6bd262d51e2956ed1c63e807cda41c1001f28aeedd96` | `deb890657f8992d5c2903dc28cfae4cd06af361a8f68df286d4796448dbf224f` |
| ENV-BUNDLE-1-FU1 | 148 | `verification/ENV-BUNDLE-1-FU1/ac1-npm-ci.log` | `52a079e5a738cf4780769c8d77089c791c00bf7940979ed12a0c0422681ce0ac` | `aa18fd4fc20e3d9432bea2b739b6d2d09f16e6732bcd248467c9080de5ac557a` |
| ENV-BUNDLE-1-FU1 | 149 | `verification/ENV-BUNDLE-1-FU1/ac1-frontend-build.log` | `c5cc5211dfbb9d73bf333aa3daa93ba1b0a3326c847fd9d79ac46096e387c2df` | `af0234cf360ff68a492ea2a6c1762cd167773bb196ea1803a0ec9251f16405b7` |
| ENV-BUNDLE-1-FU1 | 150 | `verification/ENV-BUNDLE-1-FU1/ac1-bundle-and-frontend-manifest.md` | `e0c9ac95e361ef1cc06f495461bc37e1de05b15feea308bda9ebea3761fb24dc` | `08792f6c3d43f860edbcad7ecf7fb50ec199e1a41086153e3ffe20578d6dcf3e` |
| ENV-BUNDLE-1-FU1 | 151 | `verification/ENV-BUNDLE-1-FU1/ac1-core-service-smoke.log` | `3c97b0c0e116bc4e235b3daf87ddfc10faa5f140a4db565ba455f1c8093fdb05` | `7b55358722ebda350272ea1e4c66a26d8952b96e47b14b38a796102321cb6bc2` |
| ENV-BUNDLE-1-FU1 | 152 | `verification/ENV-BUNDLE-1-FU1/ac2-ac3-combined-attempt.log` | `5dc4072a7da656ee48b66dc88011b734f7c72ccdbee51fc70c4ae4fdc25e39c8` | `ccc92d53500de46dc7ca51229cdd57fd0b9f426a1add886108481c7700d0e30e` |
| ENV-BUNDLE-1-FU1 | 153 | `verification/ENV-BUNDLE-1-FU1/ac2-packaged-tests-attempt-1-compile-failure.log` | `6210d9cbb17f5bd62e4b49fb93772fc61c9b530978cc24671c8116eac15f67d8` | `d9ff770dac1811a1361541fa8d43f22fafccd8e68c33b9878b0b30ae5d5707d8` |
| ENV-BUNDLE-1-FU1 | 154 | `verification/ENV-BUNDLE-1-FU1/ac2-packaged-six-tests.log` | `5eb49f5f0d3613d642f39313392570621181c315a06807137cc7bc535e647a86` | `686f3759a1a0ad671cc2e0eb0db447c34ee5e1c8b424fcabfe5ac6b78732c534` |
| ENV-BUNDLE-1-FU1 | 155 | `verification/ENV-BUNDLE-1-FU1/ac2-packaged-six-test-results.md` | `9fecee263ca3560eaab4174a554c5acadefb74359b94bc53f5e3b76356501c23` | `1cb6812ad6fad840440c6ceecc516cee9ef7668dcd961a17658d6d24da30d184` |
| ENV-BUNDLE-1-FU1 | 160 | `verification/ENV-BUNDLE-1-FU1/ac2-i1-startup-timeout-repair.md` | `31147f840e2a55e2342c0d0e2b6ff0dbaa36862a7316acd181ef795e4f5c379a` | `8303db1b8e2d56c09635e56cce00570ace3acf811ebc28fabbf018cb1938a8a6` |
| ENV-BUNDLE-1-FU1 | 161 | `doc/handoffs/ENV-BUNDLE-1-FU1-cffa9666f.md` | `8f65745ffc7c297d3dfb65145fe886359ee97096269f080b587788f7c79e72db` | `fb7c0569390f298dcb7596551c3ab2ca45a96fb768f127d8ad79fa43970aa28c` |
| ENV-BUNDLE-1-FU1 | 162 | `verification/ENV-BUNDLE-1-FU1/ac3-host-control-blocked.md` | `89a10430acbaab7f0d82d42307c1b988978d8c4c66b9cf1e4c0fa4c62138a158` | `851a00ea6aef2dcef14131c9c4fb3263713529444e239483543c2a568be9b10f` |
| ENV-BUNDLE-1-FU1 | 163 | `verification/ENV-BUNDLE-1-FU1/ac4-copy-sidecar-to-main.log` | `2759eb47c6b8438f50421bc13e81cacd20f57e2a7fa0ad7f4e1e302e608f3dce` | `4e829aa8a5220c598c803349fdf0ae43706cd03523aa1a2b8ea4462369185aa9` |
| ENV-BUNDLE-1-FU1 | 164 | `verification/ENV-BUNDLE-1-FU1/ac4-copy-frontend-to-main.log` | `ec8bdd321e2600f31cf3e5b652b59553d3af6acdd8e3d9bf04e7d55d2ac65f57` | `89c81b41c893a843cdaedf079215ccc9574c26d886a1bd6e40f0a4a5c9491290` |
| ENV-BUNDLE-1-FU1 | 165 | `verification/ENV-BUNDLE-1-FU1/ac4-main-core-smoke-after.log` | `1ec00efebcc249235135bdceb9ebdde8a7bdd2b82a617038b7aba0fa079240cc` | `b68283836227ae4b986ef50dda1504164d6a0d4abb3ae1c5c3a980dd2896b226` |
| ENV-BUNDLE-1-FU1 | 166 | `verification/ENV-BUNDLE-1-FU1/main-artifacts-after.md` | `b3f45be2f9fc7af05f3579cb68cf8cf365e9cbc1ab687bfcbf1b92b8967c8420` | `8fe9c77abd9ae8e8c925edbd192a053794a7042c58219f52aea61183ac681ddc` |
| ENV-BUNDLE-1-FU1 | 167 | `verification/ENV-BUNDLE-1-FU1/main-artifacts-before.md` | `04c8f25e2aa54761d181ef17dca08f0415c0104b84c998ef3f6aa2850823130e` | `51ad4588d8d01ad3d86327a2b4278576dd60bc9f710082f1ac2c0d80dcc0faad` |
| ENV-BUNDLE-1-FU1 | 168 | `verification/ENV-BUNDLE-1-FU1/ac5-generated-side-effects.md` | `fee724c5e2aace61625c9541a9adddd9b569e0743324d2560e4cc6f6a82a8bbb` | `4de5e2bdc9443220ed761aa7050d4fc755fff55cd3797309ac6630e1d9e3965e` |
| ENV-BUNDLE-1-FU1 | 169 | `verification/ENV-BUNDLE-1-FU1/main-head-before.txt` | `e54ddf4b34a7ab9ac63ae498a34c1d26af00e3fceed536806876aba61951b641` | `e32997c812dbc4dd89d4e29fee39abd751c31c0eb0644b9598c5a7381ab78504` |
| ENV-BUNDLE-1-FU1 | 170 | `verification/ENV-BUNDLE-1-FU1/main-head-after.txt` | `de0b5bf57e8e6c84cdde9350fe87c25bcd3a87af106c5dafb0caab0862970850` | `d02cbc633b5ce79900f18700e3e6d821f2c0962b7b3f363f32ab59a9bac43cbe` |
| ENV-BUNDLE-1-FU1 | 171 | `verification/ENV-BUNDLE-1-FU1/main-status-before.txt` | `a72d1076a20534021c50709972e760a66b7b65d220248284e518eb8f891d460a` | `d6038ae1367351e5d70068b67c32cf1d54c20f6fd25c416be50292e7179f1205` |
| ENV-BUNDLE-1-FU1 | 172 | `verification/ENV-BUNDLE-1-FU1/main-status-after.txt` | `a72d1076a20534021c50709972e760a66b7b65d220248284e518eb8f891d460a` | `d6038ae1367351e5d70068b67c32cf1d54c20f6fd25c416be50292e7179f1205` |
| ENV-BUNDLE-1-FU1 | 173 | `verification/ENV-BUNDLE-1-FU1/main-diff-fingerprint-before.txt` | `702c9eef86cd90e0c9cfd1f81a9389abc97adaf294193bfc736f9f30a0675ba5` | `84519bbb7138110056eaaff157c303aa2d3cbd1f19b430e1f9fd0d53864372d9` |
| ENV-BUNDLE-1-FU1 | 174 | `verification/ENV-BUNDLE-1-FU1/main-diff-fingerprint-after.txt` | `1a2a4b9b7e2d31cee65e24f38da7a4c95067baa6ec484f1cd8df6fbf2d5f572b` | `ae00688813600fafb94f00bccd63379700ee003de0838d17159ef69997e95f94` |
| ENV-BUNDLE-1-FU1 | 175 | `verification/ENV-BUNDLE-1-FU1/main-status-comparison.md` | `a8330fd416ca8fc3ad89e86915da9aa3f08a90d3d38e3aca1d9ff088e5ece640` | `e341ffba29055ea20c086c3e47f3288f2b789c0776c6b1a8fcb66caed596a16f` |
| ENV-BUNDLE-1-FU1 | 176 | `verification/ENV-BUNDLE-1-FU1/main-old-core-ping-before.log` | `23bb9dde73e3c8600295c0bd9e05f4c037f36451b524660a9c2a3a58ad3082f5` | `5b91331f5c562170b8b2fe6a4db206ed70f1a450aaff0d533630813bd520df20` |
| ENV-BUNDLE-1-FU1 | 177 | `verification/ENV-BUNDLE-1-FU1/resource-manifest.json` | `60729b5bc76ba32691b0f89cadfcd736f4e3b103e536f68d75f767a86cba3fc3` | `2c90839bd8fb97273d45103f2b368726baaef3d509de6cab8f3bde97f043508f` |
| FEAT-CREATE-3 | 56 | `verification/FEAT-CREATE-3/ac-results.md` | `26d18dfb18d1f50f186147bfd7177f3b3b62bd996c435f86f3c08afaad5e37c6` | `2bb3cfa6d102e9c683c589a7725476e1ce245b7583114cb41d4eb91c27bc8046` |
| FEAT-CREATE-3 | 63 | `doc/handoffs/FEAT-CREATE-3-89ec87027.md` | `2facd4b72084f21c5b292b5952766022579065f4fea9b2b42dc6350f5fc8480e` | `74783a075ebbf9e0141de6ea5eb054c677dd011b7be6ae47a9e00c899f958e0e` |
| FEAT-CREATE-4 | 58 | `verification/FEAT-CREATE-4/ac-results.md` | `6ef615ec7cc355aadd525151fa3bbaa367a856309ac21251338511a2def621f8` | `b4f807db302e284b679d34828a37316f0957d967c58eb36d25b4384cd1f9345e` |
| FEAT-CREATE-4 | 73 | `doc/handoffs/FEAT-CREATE-4-f10cde075.md` | `0276663a2b0aa6bdae7b3ab16bb742a929cf22ac964042825b407bbb398585b1` | `1828ff39f6dfa3302cbaf48a8ba9adad13a0c1e8b220e7c3b93e11109a0e3b2f` |
| FEAT-IMPORT-MULTI-1 | 79 | `apps/desktop/src-tauri/src/host_issuer.rs` | `2ad3739dcd4526a1cfc1b3786105c00ad798117857487c58c0ec3469e2ba5a68` | `00b1b7a3821f67c4c2ff3e1d27c94145469ba7777546f1ee28a9b1b3de2e4d3d` |
| FEAT-IMPORT-MULTI-1 | 102 | `verification/FEAT-IMPORT-MULTI-1/closeout-r1/checkpoint-r2.md` | `f3c3533df0157afd61b5d3f1d9909c127422c9ae70fb17a4975a33c98a873b31` | `8ad06d1f18cf104b158ff471b3c917bc6fbc93c038bd68f2b84ef1090e4d4e8b` |
| FEAT-IMPORT-MULTI-1 | 103 | `doc/handoffs/FEAT-IMPORT-MULTI-1-8b1a1da17.md` | `51e3385f26f32e64c904f6f3eaa85b58c678f566536335492cd72cd770db5b20` | `001908e9f2ad288876ef1a7fd40ea9d487f0160adc68da236bf18ad6919af0c1` |
| HOST-TTL-BOUNDARY-1 | 141 | `verification/HOST-TTL-BOUNDARY-1/ac1-contract-ruling.md` | `3786fd91b3512a32ad5293bcf8aa9f7e328c1ea3cb5f6b532bb0fa414c5de98a` | `6f37cd21c3c119ed75be37b7d8312d08088f214c05a9025da29413092d2c8d80` |
| P02-NEW-TIME-X6-AC1-AC7 | 149 | `verification/P02-NEW-TIME-X6-AC1-AC7/final-gate-a7/codex-verification.json` | `c246e299752768fb4675822ccc2204807df9da8884823255d185c4d7ed939e1d` | `ab123894aef6ea39ce462c7a18c34dfb20cb52675301cd26a4cb2df5ec69d700` |
| P02-NEW-TIME-X6-AC1-AC7 | 152 | `verification/P02-NEW-TIME-X6-AC1-AC7/final-gate-a7/convergence-input.json` | `5a86224c72d4132d8ad4e3d908aca1a4ea0a6eb10b43c77cedf5850541e9cd3d` | `7767c9e2012bb566cfc8fec2c49065bf8db95772c08f57d476ca259ed55012d6` |
| P02-NEW-TIME-X6-AC1-AC7 | 157 | `verification/P02-NEW-TIME-X6-AC1-AC7/final-gate-a7/gate-evidence-manifest.json` | `d334037061ab01ba4aed3da12e78392633817047e027157c11cf0fbf14967c8c` | `8e122f57f1317ec5629940b5a3393434e5105890cba16de43ec98499078b4a04` |
| P02-NEW-TIME-X6-AC1-AC7 | 158 | `verification/P02-NEW-TIME-X6-AC1-AC7/final-gate-a7/integration-adjudication.md` | `96cc982aa93d4d8ae984961d4e446ebf3a273bad5bc5a5360e30364082154f19` | `c0c2ddbbcd5080b942aea07938022a09f6d113a4a7cb0791d7e47dd89fe598d3` |
| P02-NEW-TIME-X6-AC1-AC7 | 162 | `verification/P02-NEW-TIME-X6-AC1-AC7/final-gate-a7/result-input.json` | `d6fd98e3afdcb21a0a14acae0675aeb6da51a8a0494ffb72451aaf4170060fc3` | `023e9243c275e5cdcc8150b4a420bef95ffbdd0c6e8279668b0303f5b43ed784` |
| P02-NEW-TIME-X6-AC1-AC7 | 164 | `verification/P02-NEW-TIME-X6-AC1-AC7/final-gate-a7/review-dispatch.json` | `2e26857fbed1a82e25732e8a300c2869aabc199ba94c465c1a6e71270e73be70` | `fda58d0bc27a29bd0e6898b2b4fcc224141f041361d01ce03d3e6060b0c651ac` |
| P02-NEW-TIME-X6-AC1-AC7 | 165 | `verification/P02-NEW-TIME-X6-AC1-AC7/final-gate-a7/revision-input.json` | `725c1b17e5341762f54a7ca54ad4f09778f8f71eb585782f4315c1306a60dd4c` | `bf47a7ddbe9e58e57ef4adccd613ecab012c264a53d8dbe45be85d20e1ab98b9` |
| P02-NEW-TIME-X6-AC1-AC7 | 167 | `verification/P02-NEW-TIME-X6-AC1-AC7/final-gate-a7/source-evidence-manifest.json` | `06a1cedfc53fc79607a9fcb99299ae0f9e3b0ba4df50d7dedc5a32c530698ac1` | `f904c15e8ab53a3b285d9b565b84e7deead39cea21e8fc278fff5473baddbf87` |
| P02-NEW-TIME-X6-BUILD-CARGO | 110 | `verification/P02-NEW-TIME-X6-BUILD-CARGO/source-manifest-r1.json` | `4e91a92291629c776f0b54a36e0805f0219f40778da4edb70b85e23b298b5e3b` | `1b4e31fbcb5a174ec85f78fecc32ba573fd2fa552eb528abc0ed4ae40ca59402` |
| P02-NEW-TIME-X6-BUILD-CARGO | 122 | `verification/P02-NEW-TIME-X6-BUILD-CARGO/codex-failover-adjudication-r1.md` | `5bd778c252b09e8d6fc2187280b240d5280c55bc906fe46794a5f221f2472eba` | `de5bd4d51fdf52e6f3305d7b7ead4b28a9a37102acc486e31389f35496539de7` |
| P17 | 111 | `verification/P17/boundary_audit.txt` | `2bb99d4b9775ebf6c3cc095882262af08c61d31410520421a1028e54e3e3aba9` | `74a38299602907ce701db827232a5f543221731da143690e041c47cee6a15a5d` |
| P17 | 112 | `verification/P17/behavioral_evidence.md` | `c49b5c2e853835c4f0ad191359d5ab76e62b09fb45d16166901da9c73c04d839` | `5e20481561eeaba1a6af92f8639d7574a6239fb73abf28d0dd3f7af4ce311587` |
| P17 | 113 | `verification/P17/resource-manifest.json` | `3af8f3ed49daab9099c98c5ccf6f8b648bc275471c17e3748bff793d24298fe8` | `02f69aa02f66f77da381a1eb862e3360adf20c5c95812584882079af5a992ba6` |
| P19-UI-FIX-1 | 77 | `verification/P19-UI-FIX-1/uia-before-after-comparison.md` | `50a115681b9e45ca500fe167e0fcd29583298c7da2269075c3a7b6c9d6d5309e` | `60aaa8a4c7de24389f476d416f6042618c20ecbfb79be86708642f65348e7e25` |
| P19-UI-FIX-1 | 78 | `verification/P19-UI-FIX-1/run-uia.ps1` | `908564083bd05b7ebe374e353a8d5784767bc23b92e1ff5e17e52ed030c4a092` | `2ef6e06bd122807c5fbae540ec77485f25bfbeec49b6ada7d6d26c8a302d4006` |
| P19-UI-FIX-1 | 79 | `verification/P19-UI-FIX-1/rebind-isolated-namespace.py` | `389dae0374c3801412ad971b5c54285308cfde878cb7e0c0874a52f1a9ff8a70` | `62c4a8e04235b0b18f5e8d8f825012e0b9a5e3aa87c92160d5fff186d23d03f8` |
| P19-UI-FIX-1 | 80 | `verification/P19-UI-FIX-1/resource-manifest.json` | `d40280e1653e75ccdff74979a4a58dffe7feae8de4402a06abac194241e61110` | `b0772d93ab8ed9182497a43e0761f0d4ccc5560768f806ba86eb8048905c4dc2` |
| P19-UI-FIX-1 | 81 | `doc/handoffs/P19-UI-FIX-1-f19275a.md` | `8c8c741f6ae8f95279dd4caaa8362737ae454eb0ce6b2038463ccdaac92a38f4` | `1721027f048942f61e1033e99fb7f4c950337c22561b30afd85c7ce72e6b88a5` |
| P19-UI-FIX-2 | 81 | `verification/P19-UI-FIX-2/uia-before-after-comparison.md` | `d5b496912c54a81832a00ac0db576119f4b7c6c6fd3cdafd83e21cb3f55c39d9` | `668f4e6b39b72ac1d80a0ceca7f66d018d84c0de0747dd830dbf71fde312b216` |
| P19-UI-FIX-2 | 82 | `verification/P19-UI-FIX-2/run-uia.ps1` | `ab896e295b81b558eb3b6f763fb89b89c1df43559e4d46667222fe4e9dfddf37` | `1e93214afae808be2738a5624482fd510ed1cb8d5d980d376d995da164e83180` |
| RES-P02-AC6-CDP-RECOVERY | 122 | `verification/P02-NEW-TIME-X6-AC1-AC7/final-gate-a7/codex-verification.json` | `c246e299752768fb4675822ccc2204807df9da8884823255d185c4d7ed939e1d` | `ab123894aef6ea39ce462c7a18c34dfb20cb52675301cd26a4cb2df5ec69d700` |
| RES-P02-AC6-CDP-RECOVERY | 125 | `verification/P02-NEW-TIME-X6-AC1-AC7/final-gate-a7/convergence-input.json` | `5a86224c72d4132d8ad4e3d908aca1a4ea0a6eb10b43c77cedf5850541e9cd3d` | `7767c9e2012bb566cfc8fec2c49065bf8db95772c08f57d476ca259ed55012d6` |
| RES-P02-AC6-CDP-RECOVERY | 130 | `verification/P02-NEW-TIME-X6-AC1-AC7/final-gate-a7/gate-evidence-manifest.json` | `d334037061ab01ba4aed3da12e78392633817047e027157c11cf0fbf14967c8c` | `8e122f57f1317ec5629940b5a3393434e5105890cba16de43ec98499078b4a04` |
| RES-P02-AC6-CDP-RECOVERY | 131 | `verification/P02-NEW-TIME-X6-AC1-AC7/final-gate-a7/integration-adjudication.md` | `96cc982aa93d4d8ae984961d4e446ebf3a273bad5bc5a5360e30364082154f19` | `c0c2ddbbcd5080b942aea07938022a09f6d113a4a7cb0791d7e47dd89fe598d3` |
| RES-P02-AC6-CDP-RECOVERY | 135 | `verification/P02-NEW-TIME-X6-AC1-AC7/final-gate-a7/result-input.json` | `d6fd98e3afdcb21a0a14acae0675aeb6da51a8a0494ffb72451aaf4170060fc3` | `023e9243c275e5cdcc8150b4a420bef95ffbdd0c6e8279668b0303f5b43ed784` |
| RES-P02-AC6-CDP-RECOVERY | 137 | `verification/P02-NEW-TIME-X6-AC1-AC7/final-gate-a7/review-dispatch.json` | `2e26857fbed1a82e25732e8a300c2869aabc199ba94c465c1a6e71270e73be70` | `fda58d0bc27a29bd0e6898b2b4fcc224141f041361d01ce03d3e6060b0c651ac` |
| RES-P02-AC6-CDP-RECOVERY | 138 | `verification/P02-NEW-TIME-X6-AC1-AC7/final-gate-a7/revision-input.json` | `725c1b17e5341762f54a7ca54ad4f09778f8f71eb585782f4315c1306a60dd4c` | `bf47a7ddbe9e58e57ef4adccd613ecab012c264a53d8dbe45be85d20e1ab98b9` |
| RES-P02-AC6-CDP-RECOVERY | 140 | `verification/P02-NEW-TIME-X6-AC1-AC7/final-gate-a7/source-evidence-manifest.json` | `06a1cedfc53fc79607a9fcb99299ae0f9e3b0ba4df50d7dedc5a32c530698ac1` | `f904c15e8ab53a3b285d9b565b84e7deead39cea21e8fc278fff5473baddbf87` |
| UI-DESIGN-1 | 178 | `doc/design/AD001_FOUR_PAGE_UI_BASELINE.md` | `374570b64b33c9004241cfa90e5ef4387b36571cbadb0faaff357aa86f845444` | `abcfdb39a1528485b6cc385fd6ef3cb7c645b2a4582de62135137f1385e51b7e` |
| UI-DESIGN-1 | 180 | `verification/UI-DESIGN-1/selfcheck.ps1` | `f36782d0a8c9fa72c539ac50490faaa1367016fc0b96e70e01816cb1d63629f8` | `24988a2270cfcfba6431d51b5b1e45b8d068965a692f1393b6210b6a50f4d7d8` |
| UI-DESIGN-1 | 181 | `verification/UI-DESIGN-1/selfcheck-BLOCKED.md` | `5acab6837ad218c936716b17aa00b13acfee9916bb8b2c46413da087c107439d` | `74904c636dde69de2a6482fdd89c82a8e6a77e1233db380b6d31c8b013aaa9c0` |
| UI-DESIGN-1 | 182 | `verification/UI-DESIGN-1/commit-BLOCKED.md` | `6dad99ffa8e47cf7c5a7f430b1b127b1c445f5fc8861b4a5c75ee679bd930f33` | `3d6923d9c01053c0ee5e451e8e0d49c508ffdc1f95f4e09a1f6185a639f3c455` |
| UI-DESIGN-1 | 183 | `verification/UI-DESIGN-1/selfcheck-output-owner-equivalent.txt` | `01fc76c66e00809565aa82c36789ba434fd316b22f0952a78e3964998e8d9567` | `93ad6e342afb278832fbd9617ff07a12269418ad279196d462cab92364256e47` |
| UI-DESIGN-1 | 184 | `verification/UI-DESIGN-1/resource-manifest.json` | `17074d92abb2c055416765cd9b90fe453fb4d9f774ef9450bb7e96b808820874` | `9f8ac1f5ed628a485abfe470c7d0706f45ce26c7b4ced12791573931816ec3ae` |

**Not covered here**: the 102 `content_differs` rows (real byte differences).
Per ruling §1 those need an evidence chain proving the current file was an authorized
replacement for that AC; absent that, they stay as integrity-unproven debt and the old
pin is not overwritten.
