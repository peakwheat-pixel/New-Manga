# 全部工作树逐项清册

观测时点为 main=56272e40b（工作树分析时），不是当前 HEAD；后续只有主工作树 HEAD 因本 Task 治理提交推进。观察结果不是删除清单。D=全部原位保留；保护来源、精确 status 文件名与 ignored 根见 worktree-analysis.json。ignored 按根分组，未逐文件计算 hash；有内容的一律不删除。进程占用未逐路径证实为空。

|路径|HEAD|分支/Detached|tracked 改动|untracked 文件|ignored 根数|独有提交|保护命中|实际处置|
|---|---|---|---:|---:|---:|---:|---:|---|
|G:/CODEX/New Manga|56272e40b4492dd9c9006ae230a8d44ae66fb0fd|main|0|1600|121|0|1134|D；原位保留|
|C:/Users/49745/.codex/worktrees/M2-C1-dsh-review-7de1cd2-r2|b2377288680569dbee4e2299fd7dfae4de067c54|review/deepseek/M2-C1-zcode-7de1cd2-r2|0|8|0|0|1|D；原位保留|
|C:/Users/49745/.codex/worktrees/m2-i2-review-a4705a9/New Manga|a4705a9f473d0e8d9087068edc4bec572d90439a|Detached|0|5|71|0|1|D；原位保留|
|C:/Users/49745/.codex/worktrees/P02-current-prestart-review-dsh-r1|e6227e0b0b2c205105c8bc22ee49132d9da779e7|Detached|0|4|0|0|1|D；原位保留|
|C:/Users/49745/.codex/worktrees/P02-current-prestart-review-dsh-r2|9bd1999c76ff65994d6e7bca44ba568553fe26ec|Detached|0|6|0|0|1|D；原位保留|
|C:/Users/49745/.codex/worktrees/P02-current-prestart-review-dsh-r3|322526fcde650ea9dcfde4a14f828afeb8808ead|Detached|0|5|0|0|1|D；原位保留|
|C:/Users/49745/.codex/worktrees/P02-current-prestart-review-dsh-r4|6ffa2a9c5375d21bb905f4d6adbccb9124ed531b|Detached|0|5|0|0|1|D；原位保留|
|C:/Users/49745/.codex/worktrees/P02-current-prestart-review-dsh-r5|68bafd3741f376bfab297b8ced911191e96bd424|Detached|0|3|0|0|1|D；原位保留|
|C:/Users/49745/.codex/worktrees/P02-current-prestart-review-dsh-r5-followup|999e6adfc229698344c0cbf9bfb6d636fe73fb7c|Detached|0|3|0|0|1|D；原位保留|
|C:/Users/49745/.codex/worktrees/p02-d27-review-repair-review|c328691af582ff782c9d41dda60494dec990c6a6|Detached|1|0|0|1|1|D；原位保留|
|C:/Users/49745/.codex/worktrees/P02-preflight-r4-083d2b47-review-dsh|083d2b47f7051c2dedd0d9ae4346ae1affab6c1b|review/deepseek/P02-preflight-r4-083d2b47|0|3|0|0|1|D；原位保留|
|C:/Users/49745/.codex/worktrees/P02-preflight-r6-c85a041c-review-dsh|c85a041c514f3c0dd1c355a2d09f064dbc64e749|review/deepseek/P02-preflight-r6-c85a041c|0|1|0|0|1|D；原位保留|
|C:/Users/49745/.codex/worktrees/p02-r2-docs-closeout-review/New Manga|4d5a0864495d9482ad162d05588b4921aaece3ac|Detached|0|7|0|0|1|D；原位保留|
|C:/Users/49745/.codex/worktrees/p02-r2-docs-fixes-review|f366124ecb6194ff9ea4ee0d6c684ccb2b781a07|Detached|0|7|0|0|1|D；原位保留|
|C:/Users/49745/.codex/worktrees/p02pre-r1h-r6-exec-a6-antigravity/New Manga|343895fb5f0329c0c07a7104ec321b698f967607|agent/antigravity/P02PRE-R1H-R6-EXEC-A6|0|3|0|0|1|D；原位保留|
|C:/Users/49745/.codex/worktrees/p04-prod-command-concurrency-review|751abae2277e975eddacc385a423bcd796334f97|Detached|0|7|0|0|1|D；原位保留|
|C:/Users/49745/AppData/Local/Temp/diag002-s2-2jWfPm|d268a17082028fb445e2ac3bbb71f265961a2af2|Detached|2804|0|44|0|0|D；原位保留|
|C:/Users/49745/AppData/Local/Temp/diag002-s2v4-FTf6BC|d268a17082028fb445e2ac3bbb71f265961a2af2|Detached|2804|0|44|0|0|D；原位保留|
|C:/Users/49745/AppData/Local/Temp/diag002-s2v5-WJGAfi|d268a17082028fb445e2ac3bbb71f265961a2af2|Detached|2804|0|44|0|0|D；原位保留|
|G:/CODEX/New Manga/.agents/worktrees/GOV-PLAN-BUDGET-1|126af54e7ed478bb3a0470ac32b931a6509acd14|GOV-PLAN-BUDGET-1|0|51|0|0|12|D；原位保留|
|G:/CODEX/New Manga/.agents/worktrees/GOV-RESOURCE-MANIFEST-JSON-1|a2ca297f1b5775a0d5fb5fc8efcc2281bc4013c2|GOV-RESOURCE-MANIFEST-JSON-1|0|51|0|0|12|D；原位保留|
|G:/CODEX/New Manga/.agents/worktrees/GOV-RESOURCE-MANIFEST-SAME-LOCATION-1|0a2c45d5ea41df351e0f529a9b2d46c0784a1e7b|GOV-RESOURCE-MANIFEST-SAME-LOCATION-1|0|20|1|0|13|D；原位保留|
|G:/CODEX/New Manga/.agents/worktrees/P19-UI-MANIFEST-VIEW-1|3e316830c26366fc313027357de91092a96e0cd4|P19-UI-MANIFEST-VIEW-1|1|51|0|0|12|D；原位保留|
|G:/CODEX/New Manga.workspace/GOV-PIN-LINEAGE-1/worktree|60d47991baea777996313d2cf1a335c136fb1ba0|Detached|0|0|0|2|2|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/ARCH-DOC-REBASELINE|702081442d44f74310f7ae9ae7cc412479f0766a|codex/arch-doc-rebaseline|0|0|0|0|1|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/ENV-BUNDLE-1|5a23c503789ffecc4215a5ec96fc250faacbad06|codex/ENV-BUNDLE-1-sidecar-rebuild|0|0|48|0|6|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/ENV-BUNDLE-1-FU1|77f760e5fae2a913c397cd5503886897b00cf0db|codex/ENV-BUNDLE-1-FU1-packaged-acceptance|0|0|48|0|8|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/EVENTS-FWD-1|5f1d9870ea87361255589719cd66fa392238504f|agent/antigravity/EVENTS-FWD-1|0|0|63|0|5|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/EXPORT-IPC-1|fee223e36bfc28fe8c75cdc7f260933f8c49d6f6|agent/antigravity/EXPORT-IPC-1|0|0|62|0|5|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/EXPORT-REVEAL-1|13ac5b30f61a82194d21f7def4472398067c3d26|codex/EXPORT-REVEAL-1|0|1|62|0|8|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/FEAT-CREATE-1|c96958172de8f8a3f3563da43a9fef09ac4447ba|Detached|0|0|0|3|2|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/FEAT-CREATE-2|8202f24117ee7ab3ec48d0bb6b7a45d4bca1f2d7|Detached|0|0|0|0|2|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/FEAT-CREATE-3|f15d085e6063bff51116bbf474dc04571ac41288|codex/FEAT-CREATE-3|0|1|61|0|1|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/FEAT-CREATE-4|f2c66ff262299f20292d8ca92cf8c2a28abce75b|Detached|0|0|0|0|2|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/FEAT-IMPORT-MULTI-1|6caddf38e8c917c9013164ba32056056de07bff3|codex/FEAT-IMPORT-MULTI-1|0|242|86|0|1|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/HOST-CORE-1|c97b2d125bd765bdfae3ec93bc440a7ba6d595c2|codex/HOST-CORE-1-hostcontrol-handler|0|0|60|0|3|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/HOST-ISSUER-1|deb2dfc0b863e75aa0fcb0f843127947031d6865|codex/HOST-ISSUER-1-tauri-ref-issuer|0|0|47|0|6|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/HOST-ISSUER-1-C1|13cc2bb5440b9d4bfb9e01266b9045079de84e65|codex/HOST-ISSUER-1-C1-grant-registration-contract|0|0|0|0|3|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/HOST-TTL-BOUNDARY-1|fdf974645f4d3fdcabacbda5a8bf1b1678572398|codex/HOST-TTL-BOUNDARY-1-grant-ttl|0|0|61|0|4|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-BASELINE|7ab5b7d0574041f2ca9fa1424ca5b440ff298aaf|agent/zcode/P02-NEW-TIME-BASELINE|0|88|0|60|3|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION|10c35daed241aa3717b248da14c1b9b959ff1fba|agent/zcode/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION|0|3|0|31|8|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION|0af8980884e9d027042ef145cd966577d86b5bc5|agent/zcode/P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION|0|0|0|78|3|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION|14da1e814931e1e32ebc1f76a12bc3685b63646e|agent/zcode/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION|0|0|0|43|2|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6|49d2a2f9c56462f5602b00ad4b824c5381abb1ab|agent/zcode/P02-NEW-TIME-X6|0|0|0|0|15|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-AC1-AC7-ANTIGRAVITY|4abb8d288e005dc58e3270b12389d33cd7a52ac1|agent/antigravity/P02-NEW-TIME-X6-AC1-AC7|0|3|0|0|4|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-AC1-AC7-INTEGRATION|0dcc94f3591b2837c91a6b3aa5b6dcce6c23aa64|codex/p02-mainline-closeout-20261015|0|0|0|0|5|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-BUILD-CARGO|708ac7938c72fbcccd0d68c7ca60635552cbcaaf|agent/antigravity/P02-NEW-TIME-X6-BUILD-CARGO|24|1|47|0|5|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-BUILD-CARGO-DSH-REVIEW|708ac7938c72fbcccd0d68c7ca60635552cbcaaf|Detached|0|0|0|0|1|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-POSTRUN-REVIEW|2f38141d6c8e56bd66b483114b107dead88fdb6d|agent/codex/P02-NEW-TIME-X6-POSTRUN-REVIEW|4|198|0|0|4|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/P02PRE-R1H-FORENSIC-RECOVERY-INTEGRATION|4569093db896b019cfab401e35b66ed4bcea673d|agent/codex/P02PRE-R1H-FORENSIC-RECOVERY-INTEGRATION|0|0|0|3|1|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/P02PRE-R1H-H1-CURRENT-INPUT-REVIEW|a6f33f7be1fc13cca64539ecaaa4bd9528a0184e|agent/codex/P02PRE-R1H-H1-CURRENT-INPUT-REVIEW|0|0|0|4|2|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/P02PRE-R1H-H2-COLLECTOR|4a90d820a5d58a54cbc190665fbd87d563bc19af|agent/zcode/P02PRE-R1H-H2-COLLECTOR|2|0|0|4|7|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/P02PRE-R1H-H2-COLLECTOR-ANTIGRAVITY-R3|c763efa27db0f10949a52416f1374e88173a31e2|agent/antigravity/P02PRE-R1H-H2-COLLECTOR-R3|0|0|0|15|5|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/P02PRE-R1H-H2-COLLECTOR-INTEGRATION|1924fbb4fbff6044205e4f8b52adb6aaff879e2a|Detached|0|0|0|16|7|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/P02PRE-R1H-H2-RUN-INTEGRATION|06990b7993d042ae5e74ab479e291e494b622588|agent/codex/P02PRE-R1H-H2-RUN-INTEGRATION|0|0|0|3|2|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE|23bec747df77e67e93ec1fa9fd859d077219e941|agent/codex/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE|0|0|0|18|1|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/P06-GC-DISTRIBUTION-MIGRATION|4ed493a3f766ec126ab549b0d29f6d3886f9fdf6|codex/P06-gc-distribution-migration-evidence|0|0|47|0|3|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/P09-FU1-DECODER-TEST|c15cb9589917aaecc8e54fb8b4ef0152619a0d6b|codex/P09-FU1-decoder-test-baseline|0|0|60|0|3|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/P09-FU2-IMPORT-IPC-RUNTIME|73b52e86aebbbab3854b870990d8de513d3e7ee1|codex/P09-FU2-import-ipc-runtime|0|0|60|0|3|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/P09-IMPORT-CORE|54d40e6686ba2006f8506b519d00672ee75adfeb|codex/P09-import-core|0|0|22|0|3|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/P09-MANAGED-READ-ROOT-TRUST-1|9f5560bc1d169e803bb853c94b6c3d2619263f68|dsh/P09-MANAGED-READ-ROOT-TRUST-1|0|0|69|0|1|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/P10-CREDENTIAL-CONFIG-CONTRACT|fa20602debb2d5f16f315bbed4180eae6f8821c5|codex/P10-credential-config-contract|0|0|0|0|3|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/P11-LONG-TASK-LIFECYCLE-CONTRACT|c7922ae1c62f4cac8721a2730fc19c7c973c7e83|codex/P11-long-task-lifecycle-contract|0|0|0|0|3|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/P12|98f3055f1ace0c27096ba73efc65d6d0e8156589|agent/antigravity/P12-bookshelf-ui|0|0|3|0|4|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/P12-C1-IMPORT-IPC|e325e007231beb866d3bd2656bc081e9424acc15|codex/P12-C1-import-ipc-contract|0|0|0|0|3|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/P13-C1-RUNTIME-IPC|7dde1f6c41dbd70bf99a61dac8bf3c40833a35f5|codex/P13-C1-runtime-ipc-contract|0|0|0|0|3|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/P13-RUN-RUNTIME|8056ee63e0b1b5a25b64ef9e85bb8e8e54282dba|codex/P13-run-runtime-control-recovery|0|0|58|0|3|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/P14|41c3206942730536bc9b41e871f23ad9b3de3f1d|codex/P14|3|1|62|2|5|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/P14-review|ee1d1e287c0825c885d3182246af3433a33cc97b|Detached|39|1|62|0|0|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/P15|ee19898fcd328d7231c7c3ac0a0bf4a5fa5d7024|zcode/P15|0|2|63|0|6|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/P15-C1|9c0200e88f36761f6ee108ab5a838d1d7dabf378|antigravity/P15-C1|0|0|2|0|5|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/P15-C1-FU1|9b0a2459058504c63fd3b688286d25cb02498954|codex/P15-C1-FU1|0|0|0|0|3|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/P15-C1-FU2|0aa01eddcd751adf9c4d2e3894f4cce9ec657909|codex/P15-C1-FU2|0|0|0|2|3|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/P15-CORE-1|c399b1ae21e946650ca2d57df7642316f77402ed|codex/P15-CORE-1|1|6|61|0|3|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/P15-CORE-1A|99641c41f180abba6536715599a1809c1f620e94|codex/P15-CORE-1A|0|0|60|0|3|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/P15-CORE-1B|075bcbad88dedaf2cad33822ae7742e944079915|codex/P15-CORE-1B|0|0|60|0|3|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/P15-CORE-1C|faa37493d8448ec793835bc58baf851cb1a246f1|codex/P15-CORE-1C|0|3026|67|0|1|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/P15-HOST-1|f80678bbd2314e6548b63585e658d2de2d6c17b5|codex/P15-HOST-1|0|0|85|0|1|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/P15-HOST-2|4e88bc4d413c38b467541c03a0886550b498826b|codex/P15-HOST-2|54|3705|99|0|1|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/P15-review|ee19898fcd328d7231c7c3ac0a0bf4a5fa5d7024|Detached|39|1|62|0|0|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/P16-C1-READER-EXPORT-IPC|356a9fe07f67dd8b0c376d3b6c02c151b4c06f15|codex/P16-C1-reader-export-ipc-contract|0|0|0|0|3|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/P16-READER-EXPORT-CORE|316d79eceb7723d89670f5072bb2f71996e85610|codex/P16-reader-export-core|0|0|59|0|3|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/P17|55b9ff3f88dd98859c7ef816e2dbd00d7b84d97c|agent/antigravity/P17|0|0|63|0|3|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/P18-JA-KO-QUALITY|34d81c96a66fbde17e4eb44bc058ab993483922f|codex/P18-ja-ko-quality-qualification|0|0|0|0|3|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/P19-BOOT-1|e4aff85bc87fa36f8656710315add6ec52c5ce15|codex/P19-BOOT-1|0|0|130|0|4|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/P19-UI-FIX-1|00c5e87dad36d591e7c63c37db720c6a09eefca4|codex/P19-UI-FIX-1|0|0|50|0|2|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/P19-UI-FIX-2|541aabb1e88a18e7ed6fb82afc971bc0bcff6c9c|Detached|0|0|0|0|2|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/P19-UI-FIX-3|9e152b6312e75be5e7381b6a6be021aa7e6a9060|codex/P19-UI-FIX-3|1|1|2|0|0|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/P22-REBASE-1|5181facbb095be8c7a45924b699d4e3a481aeb50|codex/p22-rebase-1|24|1|2|0|10|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/PROJECT-ROADMAP-REBASELINE|000cbfe9909c3eb566fd4d077c77199ce4d7c86e|codex/project-roadmap-rebaseline|23|9|0|1|0|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/PROJECT-ROADMAP-RELEASE-REVIEW|a43c6b9fed681e7cb123123eeb6b5ccb7fd4d4b6|Detached|0|0|0|0|2|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/READER-IPC-1|6aadc70de76b5464e1069a857385714b1184825c|codex/READER-IPC-1|0|1|61|0|5|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/RUN-IPC-1|de3caf93adf44fdda226a5f9ad013cbe7739e0f4|agent/dsh/RUN-IPC-1|25|1|61|0|5|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/RUN-IPC-1-review|be14d721c3596655e4ce053e24371a244e598197|Detached|0|1|61|0|0|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/SEC-FIX-PATH-ECHO-1|6efbfcf063131795dd4bfa0bc227e7a7c94fc444|codex/SEC-FIX-PATH-ECHO-1|0|97|62|0|0|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/UI-DESIGN-1|920151a9cd8bb715466be22b2417f2fee74b67a3|agent/zcode/UI-DESIGN-1|0|0|0|0|3|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-CLEANUP-TOOL-HARDENING-1|1dc8a89445207e47a28a330610a925fa8514bf3b|dsh/WORKSPACE-CLEANUP-TOOL-HARDENING-1|0|0|0|0|0|D；原位保留|
|G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-DECLARATION-REMEDIATION-1|f3d8cb27b196472d12f979c29788ad3966ab026f|dsh/WORKSPACE-DECLARATION-REMEDIATION-1|0|0|0|0|1|D；原位保留|
|G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode|0fadc330a6daa42de6c78be52feaae26ce6724ea|agent/zcode/M2-DERIVED-GC-2|24|0|82|0|1|D；原位保留|
|G:/CODEX/New Manga.worktrees/M2-AC5-BUILD-FRESH-CHECKOUT-zcode|ed8a6ea64efe92957b1306bcfbaeca22ff223b57|agent/zcode/M2-AC5-BUILD-FRESH-CHECKOUT|14|0|46|0|1|D；原位保留|
|G:/CODEX/New Manga.worktrees/M2-C1-deepseek-review-7d908a5|e6fc3a59b913f2aef1ab8c7a77ff47df0cd114a1|review/deepseek/M2-C1-typed-ipc-7d908a5|0|7|0|4|1|D；原位保留|
|G:/CODEX/New Manga.worktrees/M2-C1-dsh-review-7de1cd2|b2377288680569dbee4e2299fd7dfae4de067c54|review/deepseek/M2-C1-zcode-7de1cd2|0|5|0|0|1|D；原位保留|
|G:/CODEX/New Manga.worktrees/M2-C1-qoder-review-7de1cd2|0d73983a5e1f37f104c76d8bd4c70c6f98fa36f5|review/qoder/M2-C1-zcode-7de1cd2|0|2|0|0|1|D；原位保留|
|G:/CODEX/New Manga.worktrees/M2-C2-zcode|c18f273ad5a7768c6ae1726610da1ac27aa958d3|agent/zcode/M2-C2-typed-ipc-contract-revision|0|2|0|0|1|D；原位保留|
|G:/CODEX/New Manga.worktrees/M2-FIX-DIGEST-SEEK-2GIB-zcode|8a1bc1e856e41aef62a9ad355138a426975c59c0|agent/zcode/M2-FIX-DIGEST-SEEK-2GIB|14|0|46|0|1|D；原位保留|
|G:/CODEX/New Manga.worktrees/M2-I2-review-0d6acc7|0d6acc7d985a0a96f5a27c2f25b7b2afcd66e716|Detached|0|5|71|0|1|D；原位保留|
|G:/CODEX/New Manga.worktrees/M2-SETTINGS-IPC-CHANNEL-zcode|8a28c797b414453df8c3bb14d1cdc4bbf199a93b|agent/zcode/M2-SETTINGS-IPC-CHANNEL|6|0|64|0|1|D；原位保留|
|G:/CODEX/New Manga.worktrees/P01-c8-review-dsh|91ab1ef8ddaa1d00b0b34880a103937b4831590d|Detached|0|5|0|0|1|D；原位保留|
|G:/CODEX/New Manga.worktrees/P01-c9-review-antigravity|7645577ab374b581eb7081fd57675c32793249f5|Detached|0|5|0|0|1|D；原位保留|
|G:/CODEX/New Manga.worktrees/P01-closeout-review-antigravity|51bc01fec2652c0e2bc39bb119f8dd7ca3c294cb|Detached|0|12|0|0|1|D；原位保留|
|G:/CODEX/New Manga.worktrees/P02-hook-cache-isolation-plan-codex|ceca2446da88df23a719f40868cc89e1481ccb2c|codex/P02-hook-cache-isolation-plan|3|7|0|7|1|D；原位保留|
|G:/CODEX/New Manga.worktrees/P02-real-webview-harness-antigravity|89413f45a601966eb40d7af7abea65cbdfc754b3|Detached|0|0|0|0|3|D；原位保留|
|G:/CODEX/New Manga.worktrees/P02-real-webview-harness-zcode|e1948466082b3cadbfde1da53b791319e359a10b|agent/zcode/P02-real-webview-harness|24|2633|64|0|1|D；原位保留|
|G:/CODEX/New Manga.worktrees/P02-stage-a-validation-172eee84-failureprobe|172eee84240e101186b12f1aa09e8a2f9ec92d68|Detached|3|0|0|0|1|D；原位保留|
|G:/CODEX/New Manga.worktrees/P02-stage-a-validation-172eee84-full|172eee84240e101186b12f1aa09e8a2f9ec92d68|Detached|8|0|0|0|1|D；原位保留|
|G:/CODEX/New Manga.worktrees/P02-stage-a-validation-172eee84-probe|172eee84240e101186b12f1aa09e8a2f9ec92d68|Detached|5|0|0|0|1|D；原位保留|
|G:/CODEX/New Manga.worktrees/P02-stage-a-validation-38672473-exact|38672473f93971a4681aef682e5635e64b0bd896|Detached|9|0|0|0|1|D；原位保留|
|G:/CODEX/New Manga.worktrees/P02-stage-a-validation-38959ba99-exact|38959ba99b84f771aba7010b53b9b47ecdc75488|Detached|9|0|1|0|1|D；原位保留|
|G:/CODEX/New Manga.worktrees/P02-stage-a-validation-5fa8a41f|5fa8a41f1fbda56dd88fb3a87e1604fd0a14a59e|Detached|5|0|0|0|1|D；原位保留|
|G:/CODEX/New Manga.worktrees/P02-stage-a-validation-9b82e97b|9b82e97b8aadc5b6b8710e03b5128a608697f56e|Detached|5|0|0|0|1|D；原位保留|
|G:/CODEX/New Manga.worktrees/P02-stage-a-validation-cc1bd750-full|cc1bd7505f3fc48079db7ea2719040e77a8c58dd|Detached|7|0|0|0|1|D；原位保留|
|G:/CODEX/New Manga.worktrees/P02-stage-a-validation-cc1bd750-probe|cc1bd7505f3fc48079db7ea2719040e77a8c58dd|Detached|4|0|0|0|1|D；原位保留|
|G:/CODEX/New Manga.worktrees/P03-dsh-review-6d84b48|6d84b480d5996d6374192bbbba07807848b8ebde|review/deepseek/P03-packaged-sfx-entry-6d84b48|0|1|0|0|1|D；原位保留|
|G:/CODEX/New Manga.worktrees/P03-packaged-sfx-entry-antigravity|85482c5b001d452953c3ed797ce3c4ed64cae4e3|agent/antigravity/P03-packaged-sfx-entry|0|3|52|0|1|D；原位保留|
|G:/CODEX/New Manga.worktrees/P03-review-prep-85482c5b|552464238a69ad2cea63cff18abe98f412dbae87|codex/P03-integration-4c04459|0|22|52|0|1|D；原位保留|
|G:/CODEX/New Manga.worktrees/P22-roundtrip-serialization-antigravity|4a707db80499f11e93cee163a9a10bf6392b1a92|agent/antigravity/P22-roundtrip-serialization|0|57|0|10|1|D；原位保留|
|G:/CODEX/New Manga.worktrees/PAGE-NAV-1|7bec3589eb6a01882e8f681c9b9a5b69e9e88821|zcode/page-nav-projection-1|0|2|82|0|1|D；原位保留|
|G:/CODEX/New Manga.worktrees/RC4-domain-commands|6a7b4c3d691ed89bff8513b9ac409ee5ef5267e8|codex/rc4-domain-commands|0|1|82|0|1|D；原位保留|
|G:/CODEX/New Manga.worktrees/RC4-integration|0a7e0d5be97b273cc3093a59da11008f20bae89f|codex/rc4-integration|21|0|82|0|1|D；原位保留|
|G:/CODEX/New Manga.worktrees/RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-dsh-r1|0ea16b832dcf32297d8c73df2ccdcf764c694368|review/deepseek/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-r1|0|4|0|0|1|D；原位保留|
|G:/CODEX/New Manga.worktrees/RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-dsh-r2|daab1996b99c7036108bc505cc3db29b744fdf9d|review/deepseek/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-r2|0|3|0|1|1|D；原位保留|
|G:/CODEX/New Manga.worktrees/T2.2.1-zcode|df637df1f9d6e8468bc73d6ff585bbf55e8e9a64|agent/zcode/T2.2.1-reader-workbench-polish|0|1|70|1|1|D；原位保留|
|G:/CODEX/New Manga.worktrees/T3.2.1-zcode-repair-13|13ae23f65e963cf1d5aea19634572627e5e709db|agent/zcode/T3.2.1-repair-13|0|3|57|64|1|D；原位保留|
|G:/CODEX/New Manga.worktrees/TASK-024-zcode|86072c30a9587d5eced3daa14c555409d6917e6c|agent/zcode/TASK-024-extension-boundaries-design|1|0|55|0|1|D；原位保留|
|G:/CODEX/New Manga.worktrees/TASK-046-zcode|60cebc060752d4c68b15288c7602841d0e6f7db4|agent/zcode/TASK-046-decode-rewind-cost|1|2|0|0|1|D；原位保留|
