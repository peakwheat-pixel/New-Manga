---
id: P02PRE-R1H-H2-RUN
title: H2 新时点只读 pre-run 采集与独立审查
kind: verification
governance_version: 2
status: done
dispatch_state: CODEX_H2_RUN_DONE
approval: user_autonomous_execution_authorization_20261013
suggested_owner: Codex /root
owner: Codex /root
reviewer: DeepSeek Harness
integrator: Codex /root
depends_on: [P02PRE-R1H-H2-COLLECTOR]
base_commit: 343895fb5f0329c0c07a7104ec321b698f967607
branch: main
worktree: G:/CODEX/New Manga
integration_commit: 06990b7993d042ae5e74ab479e291e494b622588
delivery_head: 1924fbb4fbff6044205e4f8b52adb6aaff879e2a
collector_delivery_commit: a4766131ba7962583a846117e123fb3376ca37de
source_integration_commit: 1924fbb4fbff6044205e4f8b52adb6aaff879e2a
collector_source_sha256: 69dbe8ffd57a4e182f6f79817d2351d519724f69188f2ea7840da187714edc61
collector_selftest_sha256: e7ad2b19508d8aae0943e4b42e6830d6fc16bec53b757b62d745c017645ad96c
run_id: h2-20261013-de77a42fccca4193925767ba4e414970
output_target: G:/CODEX/New Manga.workspace/agent-output/codex/P02PRE-R1H-H2-COLLECTOR/run-h2-20261013-de77a42fccca4193925767ba4e414970.json
preflight_status: PASS_READY_GATE
preflight_checks: 43/43
preflight_sha256: 1333b1e74e4a5a90752c744c151b812410a4ba2d22a842678991f8b104add929
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/P02PRE-R1H-H2-RUN
---

# H2 RUN：新时点只读采集

## 来源与释放条件

本 Task 对固定、已受审的 collector artifact 做一次只读验证；它不改写 H1 v2/P2-1 历史事实。H2 collector 的 R7 exact-head DSH Review 和 Codex adjudication 已批准，隔离集成及集成后 Parser/pure selftest 已通过。集成源码只读使用；root HEAD/index/main refs 保持冻结。

输入释放 Gate 已冻结：collector delivery commit a4766131ba7962583a846117e123fb3376ca37de、独立 DSH R7 source Review、Codex 20/20 post-pins、R7 adjudication、集成 commit 1924fbb4fbff6044205e4f8b52adb6aaff879e2a、collector/selftest SHA、唯一运行参数和输出目标、root/candidate/A6 refs/index/source pins 及运行前环境。详细结果见本 Task preflight freeze 和原始 JSON。该 Gate 不得由 Task 格式或聊天替代。

Owner 为 Codex，已按自治授权接领；Reviewer 为非作者 DeepSeek Harness。启动器自检通过，collector 已按唯一 RunId 调用一次并完成。DSH R3 与 Codex adjudication 已批准，证据已隔离集成，逐项资源 disposition 已完成；Task 当前留在 approved 集成窗口，待最后治理检查与指针切换。

## Frozen run inputs

- 唯一 RunId：h2-20261013-de77a42fccca4193925767ba4e414970。
- 唯一输出：G:/CODEX/New Manga.workspace/agent-output/codex/P02PRE-R1H-H2-COLLECTOR/run-h2-20261013-de77a42fccca4193925767ba4e414970.json；ready 时检查为 absent。
- 固定源码：G:/CODEX/New Manga.workspace/worktrees/P02PRE-R1H-H2-COLLECTOR-INTEGRATION/tools/p02/h1-raw-pre-run.ps1，集成 commit 1924fbb4fbff6044205e4f8b52adb6aaff879e2a，SHA-256 69dbe8ffd57a4e182f6f79817d2351d519724f69188f2ea7840da187714edc61。
- 固定启动：CWD G:/CODEX/New Manga；C:/Program Files/PowerShell/7/pwsh.exe，参数 -NoLogo -NoProfile -NonInteractive -File <上述源码> -RunId <冻结 ID>；ProcessStartInfo ArgumentList，UseShellExecute=false。
- 运行 raw stdout/stderr/OS exit/launch record 保存到 workspace 的 H2-RUN run-id 目录；任何失败 partial 保留，不重用 RunId、不重试。

## Acceptance Criteria

- [x] 输入 Gate 和 live 前置均实际核验；本 Task ready 后才调用已受审 collector 一次。
- [x] 每条 observation 保存实际 argv/method/input/CWD/UTC/stdout/stderr/OS exit 或 getter output/异常；15 项 provenance 与其余 pre-run 检查均有可解析 raw pointer，不借用旧 v2 observed。
- [x] 结果明确 NEW_TIME_EVIDENCE / CANNOT_SUBSTITUTE_V2_TIME_EVIDENCE；历史 v2 P2-1 OPEN 保留，不将新结果当 X6 S0。
- [x] 执行前后所有冻结原 source/protected file/root index/refs 不变；变更/未知/异常 fail-closed，wrapper exit 与 collector disposition 分列。
- [x] DSH 非作者结果 Review，Codex source pin pre/post 核验和逐项 adjudication；只有完整新的 PRE_RUN_PASS + 独立接受，才可重新裁决 H1 当前输入并释放独立 X6。
- [x] canonical evidence、资源 disposition、Handoff、checkpoint 和 governance check 完整；未集成前不得标 done。

## 允许修改范围

仅本 Task、verification/P02PRE-R1H-H2-RUN/ 下的新判别力 evidence/Review/adjudication/Handoff；Codex 定点维护 STATUS、Plan、Task README 和 H2 collector Task。Collector raw runtime output 只写上述唯一 workspace 文件。DSH 原始日志写 workspace/agent-output/codex/P02PRE-R1H-H2-RUN/ 的本 Task 子目录。

## 禁止范围

不改 collector 源码/原 v2/attempt1/A6，不执行 executor/File.Replace/ProcessObserver/Toolhelp/native profile API/Build/Cargo/AC/capture/Sandbox，不写 registry/ACL/profile，不访问 .tmp.driveupload。不删除/清理/覆盖任意既有 evidence/source/user data，不 stage/commit 他人 dirty 或改变 frozen root refs/index。动态进程闭包保持 REQUIRES_ACTIVE_TEST / NOT_RUN。readonly helper processes 不等于 executor 的 dynamic closure 通过。

## 测试要求

| 场景 | 计划命令/前提 | 实际结果 | 证据 |
|---|---|---|---|
| 输入与 live preflight | 固定 PS7.6.6，只读 freeze-preflight r1 | PASS_READY_GATE；43/43；collector NOT_RUN | verification/P02PRE-R1H-H2-RUN/preflight-freeze-r1.md |
| one-shot launcher selfcheck | PS7.6.6 Parser + 12 assert checks；不执行 collector | PASS：0 Parser errors；12 PASS / 0 FAIL / 0 SKIP | workspace run-id/launcher-selfcheck.stdout.log |
| 新时点 pre-run | 固定 PS7.6.6；唯一 RunId/源码/argv；本 Task 已 in_progress | PASS；唯一调用完成，COLLECTED_NEW_TIME_EVIDENCE；launcher/collector exit 0 | verification/P02PRE-R1H-H2-RUN/runtime-verification-r2.md |
| raw mapping/原件不变 | 验证 80 条 NDJSON、78 条 observation、55 checks 与 JSON Pointer、hash/refs pre/post | PASS；55/55 checks 与 pointers；root HEAD/main/index、source hashes、integration worktree clean | verification/P02PRE-R1H-H2-RUN/runtime-verification-r2.json |
| 独立结果 Review | 固定 artifact pins 后 DSH exact-head review | PASS；R2/R3 APPROVED_STATIC_CONTENT；P3-1/P3-2 resolved；Codex逐项 adjudication APPROVED | verification/P02PRE-R1H-H2-RUN/dsh-result-review-r3.md 与 codex-adjudication-r1.md |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| h2-r7-review | source review | verification/P02PRE-R1H-H2-COLLECTOR/dsh-source-review-r7.md | - | b3ff51a9fd499a1eb0067846cc8b83f03e5759f23cfe1468d9f547325f9be233 | SOURCE_PIN |
| h2-r7-post-pins | source review inputs | verification/P02PRE-R1H-H2-COLLECTOR/source-review-r7-input-verification.json | - | e5a7057f0f9e5caea48cad48941333285b598a7b10f1340c30efba51fc5b1a3d | SOURCE_PIN |
| h2-r7-adjudication | Codex source adjudication | verification/P02PRE-R1H-H2-COLLECTOR/source-review-r7-adjudication.md | - | c0d5236f6937ac518d8d862975a050ca86a62b980ed58a4c39ae6081e27150ce | SOURCE_PIN |
| h2-integration-report | isolated integration | verification/P02PRE-R1H-H2-COLLECTOR/integration-verification-r7.md | - | 13939aea005629c591974fa07befd08c34e9f716eee19bd85eea04a6789c1a7d | SOURCE_PIN |
| h2-integration-meta | integration raw metadata | G:/CODEX/New Manga.workspace/agent-output/codex/P02PRE-R1H-H2-COLLECTOR/repair-r7/integration-check/integration-verification.json | - | f61ede35d44fc2e6c7efaaaa4a79869fee4034edff443cc9c8c2cb9873c83bde | SOURCE_PIN |
| h2-collector-source | frozen collector | G:/CODEX/New Manga.workspace/worktrees/P02PRE-R1H-H2-COLLECTOR-INTEGRATION/tools/p02/h1-raw-pre-run.ps1 | - | 69dbe8ffd57a4e182f6f79817d2351d519724f69188f2ea7840da187714edc61 | SOURCE_PIN |
| h2-selftest-source | source pure selftest | G:/CODEX/New Manga.workspace/worktrees/P02PRE-R1H-H2-COLLECTOR-INTEGRATION/tools/p02/h1-raw-pre-run-selftest.ps1 | - | e7ad2b19508d8aae0943e4b42e6830d6fc16bec53b757b62d745c017645ad96c | SOURCE_PIN |
| h2-preflight-json | frozen raw preflight | G:/CODEX/New Manga.workspace/agent-output/codex/P02PRE-R1H-H2-RUN/preflight2-h2-20261013-de77a42fccca4193925767ba4e414970/preflight.json | - | 1333b1e74e4a5a90752c744c151b812410a4ba2d22a842678991f8b104add929 | SOURCE_PIN |
| h2-preflight-script | preflight script | G:/CODEX/New Manga.workspace/agent-output/codex/P02PRE-R1H-H2-RUN/preflight2-h2-20261013-de77a42fccca4193925767ba4e414970/freeze-preflight.ps1 | - | 38f50803b16169746243e5673ac9bcb8a55fb10d7d2d24bb8418a7d08e46b223 | SOURCE_PIN |
| h2-preflight-stdout | preflight stdout | G:/CODEX/New Manga.workspace/agent-output/codex/P02PRE-R1H-H2-RUN/preflight2-h2-20261013-de77a42fccca4193925767ba4e414970/preflight.stdout.log | - | 649e4d66f61e16ed7f0bc7207e7148c4de8e78baf6f790e7581be7eb40dc060a | SOURCE_PIN |
| h2-root-status | root status raw bytes | G:/CODEX/New Manga.workspace/agent-output/codex/P02PRE-R1H-H2-RUN/preflight2-h2-20261013-de77a42fccca4193925767ba4e414970/root-status.stdout.bin | - | aaaaf307a4fb0835a76526cdd80f911a65a7a214adc6fb722b5b91b79de20e85 | SOURCE_PIN |
| h2-candidate-status | candidate status raw bytes | G:/CODEX/New Manga.workspace/agent-output/codex/P02PRE-R1H-H2-RUN/preflight2-h2-20261013-de77a42fccca4193925767ba4e414970/candidate-status.stdout.bin | - | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| h2-a6-status | A6 status raw bytes | G:/CODEX/New Manga.workspace/agent-output/codex/P02PRE-R1H-H2-RUN/preflight2-h2-20261013-de77a42fccca4193925767ba4e414970/a6-status.stdout.bin | - | 3f422059515c896b0633087f3e6a052e18f4de8c556e38e5cdd5ccc06b6de083 | SOURCE_PIN |
| h2-preflight-freeze | canonical preflight freeze | verification/P02PRE-R1H-H2-RUN/preflight-freeze-r1.md | - | da04e54a2a6acf48025625a1d9a090d53caef975ffc565032cccf76a95790373 | CANONICAL |
| h2-live-launcher | one-shot binary-capture launcher | G:/CODEX/New Manga.workspace/agent-output/codex/P02PRE-R1H-H2-RUN/run-h2-20261013-de77a42fccca4193925767ba4e414970/launch-once.ps1 | - | c9a5b77d3585cc4613c2dafa18d6251e185b025b0ddfef0397bbdc135b1d179d | SOURCE_PIN |
| h2-launcher-selfcheck | launcher Parser/assert selfcheck | G:/CODEX/New Manga.workspace/agent-output/codex/P02PRE-R1H-H2-RUN/run-h2-20261013-de77a42fccca4193925767ba4e414970/launcher-selfcheck.ps1 | - | 49a7e96d849324024a972b8bf2882b8f45553045008e19476a21f2e1fd6ddaec | SOURCE_PIN |
| h2-launcher-precheck-failure | pre-launch failure evidence | G:/CODEX/New Manga.workspace/agent-output/codex/P02PRE-R1H-H2-RUN/run-h2-20261013-de77a42fccca4193925767ba4e414970/launcher-precheck-failure-001.md | - | 89585d9ad42c71be71efe7c68197bd7b3ae7f5a4b3207790b47059befe41d55b | SOURCE_PIN |
| h2-launcher-selfcheck-log | launcher selfcheck result | G:/CODEX/New Manga.workspace/agent-output/codex/P02PRE-R1H-H2-RUN/run-h2-20261013-de77a42fccca4193925767ba4e414970/launcher-selfcheck.stdout.log | - | ebd8f504aa135b7fc6140b5d3b5e701b4ee8a39cc908775144278487573b389c | SOURCE_PIN |
| h2-run-checkpoint | terminal closeout checkpoint | verification/P02PRE-R1H-H2-RUN/checkpoint.md | 06990b7993d042ae5e74ab479e291e494b622588 | 8e4befd238b269afe5e1f2c98560aaed46cad17819e7fe213e61925f9167b0de | CANONICAL |

| h2-launcher-selfcheck-failure | failed launcher selfcheck evidence | G:/CODEX/New Manga.workspace/agent-output/codex/P02PRE-R1H-H2-RUN/run-h2-20261013-de77a42fccca4193925767ba4e414970/launcher-selfcheck-failure-001.md | - | b0fff9cd23ef7e35b6438f7fb91cf5236f2a2882c055bc59446b6837173b0ef9 | SOURCE_PIN |

| h2-launcher-precheck-failure-002 | pre-launch failure evidence | G:/CODEX/New Manga.workspace/agent-output/codex/P02PRE-R1H-H2-RUN/run-h2-20261013-de77a42fccca4193925767ba4e414970/launcher-precheck-failure-002.md | - | 92ddc876d66fe864da6f244a30cc255bbf57314f49a7c8094ac67e0cbd96bea3 | SOURCE_PIN |

| h2-launcher-precheck-failure-003 | pre-launch failure evidence | G:/CODEX/New Manga.workspace/agent-output/codex/P02PRE-R1H-H2-RUN/run-h2-20261013-de77a42fccca4193925767ba4e414970/launcher-precheck-failure-003.md | - | 8d55327e92211f4e5b897481409307d1489b18f3ce5e0f85544622fcec52e7f1 | SOURCE_PIN |

| h2-runtime-output | one-shot collector raw NDJSON | G:/CODEX/New Manga.workspace/agent-output/codex/P02PRE-R1H-H2-COLLECTOR/run-h2-20261013-de77a42fccca4193925767ba4e414970.json | - | 32cd72b710857bb0f19eb92d2c01f2ff6aa13778f10836965c8619ebbf5a2179 | SOURCE_PIN |
| h2-runtime-launch-result | binary launch result metadata | G:/CODEX/New Manga.workspace/agent-output/codex/P02PRE-R1H-H2-RUN/run-h2-20261013-de77a42fccca4193925767ba4e414970/launch-result.json | - | 228fe9e6b35d630b0732e0ad27b0495fbcb39d2ce07d4c8ebfa6ca0032883262 | SOURCE_PIN |
| h2-runtime-stdout | collector raw stdout | G:/CODEX/New Manga.workspace/agent-output/codex/P02PRE-R1H-H2-RUN/run-h2-20261013-de77a42fccca4193925767ba4e414970/collector.stdout.bin | - | 8a6d80eadd27af3ebc6198edabda79c76ef849a392e44302ff0b4d5b24ea3814 | SOURCE_PIN |
| h2-runtime-stderr | collector raw stderr | G:/CODEX/New Manga.workspace/agent-output/codex/P02PRE-R1H-H2-RUN/run-h2-20261013-de77a42fccca4193925767ba4e414970/collector.stderr.bin | - | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| h2-runtime-exit | collector OS exit marker | G:/CODEX/New Manga.workspace/agent-output/codex/P02PRE-R1H-H2-RUN/run-h2-20261013-de77a42fccca4193925767ba4e414970/collector.exit | - | 13bf7b3039c63bf5a50491fa3cfd8eb4e699d1ba1436315aef9cbe5711530354 | SOURCE_PIN |
| h2-runtime-verification-r1 | prior Codex post-run assertions (superseded summary label only) | verification/P02PRE-R1H-H2-RUN/runtime-verification-r1.json | - | 30845dd99832d4a774dd5104633bd5de3f9c436231e1981702426125e5189566 | SOURCE_PIN |
| h2-runtime-report-r1 | prior runtime report | verification/P02PRE-R1H-H2-RUN/runtime-verification-r1.md | - | c107fd99cf154ed0c911d3985eaaf103cfd60080a85aab71ec7b4d6c3f8a2297 | SOURCE_PIN |
| h2-run-handoff-r1 | prior Codex handoff | verification/P02PRE-R1H-H2-RUN/codex-handoff-r1.md | - | b41496e100c92ab1fb9518022d84a9a194b167ef3749eb762b81f5b182c8b4c3 | SOURCE_PIN |

| h2-runtime-verification | current Codex post-run assertions | verification/P02PRE-R1H-H2-RUN/runtime-verification-r2.json | - | ef97ce90c9ed7c9ab693930bfc9c15ce220dbe921a916112cbbd951689c130e3 | CANONICAL |
| h2-runtime-report | current runtime result summary | verification/P02PRE-R1H-H2-RUN/runtime-verification-r2.md | - | f4a1a2cc67b92585c41a8b78890e7583324c9704a50f2477fca319d6905129a0 | CANONICAL |
| h2-result-review-r1 | nonauthor DSH result Review R1 (BLOCKED; historical) | verification/P02PRE-R1H-H2-RUN/dsh-result-review-r1.md | - | db1707cb23bc3d54fe83ed686eff210b70c85d326a73e36a26b34fb51686aa92 | SOURCE_PIN |
| h2-result-review-r1-post-pins | Codex R1 review input post-pins | verification/P02PRE-R1H-H2-RUN/result-review-r1-post-pins.json | - | 958ff3b97c28d0686af966a48f6e10f4fe89308fda00175ef726af64428aacd3 | SOURCE_PIN |
| h2-result-review-r1-manifest | frozen R1 review input manifest | G:/CODEX/New Manga.workspace/agent-output/codex/P02PRE-R1H-H2-RUN/run-h2-20261013-de77a42fccca4193925767ba4e414970/result-review-r1/review-inputs-r1.json | - | a045e128fb30f6b85eb9b76133e574622a99f2ab74dd19430bb6719fd547bd4e | SOURCE_PIN |
| h2-result-review-r2-request | focused R2 review request | G:/CODEX/New Manga.workspace/agent-output/codex/P02PRE-R1H-H2-RUN/run-h2-20261013-de77a42fccca4193925767ba4e414970/result-review-r2/review-request-r2.md | - | efcd1aa437d1e5fc7bbcab5e2c5d06bc9d5d5a2b7abcc4cf2a05c72dc8e3d09d | SOURCE_PIN |
| h2-result-review-r2-manifest | frozen R2 review input manifest | G:/CODEX/New Manga.workspace/agent-output/codex/P02PRE-R1H-H2-RUN/run-h2-20261013-de77a42fccca4193925767ba4e414970/result-review-r2/review-inputs-r2.json | - | 445be97928347ee504b7fa6d64cdd3134c35b0313e0b2f6114bffd45a5280478 | SOURCE_PIN |

| h2-result-review-r2 | nonauthor DSH result Review R2 (APPROVED_STATIC_CONTENT; P3-2 title finding) | verification/P02PRE-R1H-H2-RUN/dsh-result-review-r2.md | - | f5bfcf3014d3d66d64122e0313d7af2f1b0c2ef3beb642ca6a647a71ef7d41ff | SOURCE_PIN |
| h2-result-review-r2-post-pins | Codex R2 review input post-pins | verification/P02PRE-R1H-H2-RUN/result-review-r2-post-pins.json | - | ce706a63cfdc41581a0aed271e78fbd6d62ee3506f88f324f4191e770f089dce | SOURCE_PIN |
| h2-result-review-r3-request | focused R3 review request | G:/CODEX/New Manga.workspace/agent-output/codex/P02PRE-R1H-H2-RUN/run-h2-20261013-de77a42fccca4193925767ba4e414970/result-review-r3/review-request-r3.md | - | e9f53799a89940ad31a7cabcd0996168c5a90528771c2f2cd05d0e75c8c25c13 | SOURCE_PIN |
| h2-result-review-r3-manifest | frozen R3 review input manifest | G:/CODEX/New Manga.workspace/agent-output/codex/P02PRE-R1H-H2-RUN/run-h2-20261013-de77a42fccca4193925767ba4e414970/result-review-r3/review-inputs-r3.json | - | 1824d3bcdc4a9bb402e4ce91beae53f8d4343252fbc07dcf506f170a25341529 | SOURCE_PIN |

| h2-result-review-r3 | nonauthor DSH result Review R3 (APPROVED_STATIC_CONTENT; 0 findings) | verification/P02PRE-R1H-H2-RUN/dsh-result-review-r3.md | - | 8995028a950e082465fcae293e33028b85fa6a549f90292a943ed04ed21291a2 | SOURCE_PIN |
| h2-result-review-r3-post-pins | Codex R3 review input post-pins | verification/P02PRE-R1H-H2-RUN/result-review-r3-post-pins.json | - | 73dbd38bdece76e84d366ccdcf75038cdfd2d18e610e1387df37cae2357b90ad | SOURCE_PIN |
| h2-codex-adjudication-r1 | Codex exact-result adjudication | verification/P02PRE-R1H-H2-RUN/codex-adjudication-r1.md | - | 259d980bfafff0b654725b648db636a5d234704f8a826994f20a358aa93bba2e | CANONICAL |
| h2-codex-adjudication-r1-pins | Codex final raw/pin verification | verification/P02PRE-R1H-H2-RUN/codex-adjudication-r1-input-verification.json | - | efaa288cbc366e8a0e9e17ef8b4590b5a2ba53887ffe31c0a63254f0925e1154 | CANONICAL |
| h2-result-review-r3-request | focused R3 review request | G:/CODEX/New Manga.workspace/agent-output/codex/P02PRE-R1H-H2-RUN/run-h2-20261013-de77a42fccca4193925767ba4e414970/result-review-r3/review-request-r3.md | - | e9f53799a89940ad31a7cabcd0996168c5a90528771c2f2cd05d0e75c8c25c13 | SOURCE_PIN |
| h2-result-review-r3-manifest | frozen R3 review input manifest | G:/CODEX/New Manga.workspace/agent-output/codex/P02PRE-R1H-H2-RUN/run-h2-20261013-de77a42fccca4193925767ba4e414970/result-review-r3/review-inputs-r3.json | - | 1824d3bcdc4a9bb402e4ce91beae53f8d4343252fbc07dcf506f170a25341529 | SOURCE_PIN |

| h2-run-handoff-r2 | current Codex Handoff R2 | verification/P02PRE-R1H-H2-RUN/codex-handoff-r2.md | e24abda53baff2807bc5a236c91ddbc403a44505 | 9329c9ad883268f8f766a1c4595ba8391e7231651d7348176d4d7cd8ae5a31d5 | CANONICAL |
| h2-resource-closeout | resource closeout manifest | verification/P02PRE-R1H-H2-RUN/resource-closeout-r1.json | e24abda53baff2807bc5a236c91ddbc403a44505 | 3bcce6f2d36721ad9ef73d8de6ada4544eb293cfc0f343903335b8704a39ab80 | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| root worktree | G:/CODEX/New Manga | PRESERVE_USER_DATA | G:/CODEX/New Manga | verification/P02PRE-R1H-H2-RUN/resource-closeout-r1.json | branch main, HEAD 343895fb; index SHA pinned; existing dirty/untracked content retained and not staged |
| integration source worktree | G:/CODEX/New Manga.workspace/worktrees/P02PRE-R1H-H2-COLLECTOR-INTEGRATION | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/P02PRE-R1H-H2-COLLECTOR-INTEGRATION | verification/P02PRE-R1H-H2-RUN/resource-closeout-r1.json | clean at 1924fbb; source and selftest pins retained |
| Antigravity owner worktree | G:/CODEX/New Manga.workspace/worktrees/P02PRE-R1H-H2-COLLECTOR-ANTIGRAVITY-R3 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/P02PRE-R1H-H2-COLLECTOR-ANTIGRAVITY-R3 | verification/P02PRE-R1H-H2-RUN/resource-closeout-r1.json | clean at c763efa; source Review evidence remains referenced |
| preflight attempt 1 artifact | G:/CODEX/New Manga.workspace/agent-output/codex/P02PRE-R1H-H2-RUN/preflight-h2-20261013-de77a42fccca4193925767ba4e414970 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/agent-output/codex/P02PRE-R1H-H2-RUN/preflight-h2-20261013-de77a42fccca4193925767ba4e414970 | verification/P02PRE-R1H-H2-RUN/resource-closeout-r1.json | retained wrapper serialization failure; proves collector was not called on attempt 1 |
| preflight attempt 2 artifact | G:/CODEX/New Manga.workspace/agent-output/codex/P02PRE-R1H-H2-RUN/preflight2-h2-20261013-de77a42fccca4193925767ba4e414970 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/agent-output/codex/P02PRE-R1H-H2-RUN/preflight2-h2-20261013-de77a42fccca4193925767ba4e414970 | verification/P02PRE-R1H-H2-RUN/resource-closeout-r1.json | retained preflight manifest SHA 1333b1e7; 43/43 checks passed |
| collector output | G:/CODEX/New Manga.workspace/agent-output/codex/P02PRE-R1H-H2-COLLECTOR/run-h2-20261013-de77a42fccca4193925767ba4e414970.json | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/agent-output/codex/P02PRE-R1H-H2-COLLECTOR/run-h2-20261013-de77a42fccca4193925767ba4e414970.json | 32cd72b710857bb0f19eb92d2c01f2ff6aa13778f10836965c8619ebbf5a2179 | 788,029-byte exact raw output retained; Review and evidence integration complete |
| raw launch logs and DSH review outputs | G:/CODEX/New Manga.workspace/agent-output/codex/P02PRE-R1H-H2-RUN/run-h2-20261013-de77a42fccca4193925767ba4e414970 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/agent-output/codex/P02PRE-R1H-H2-RUN/run-h2-20261013-de77a42fccca4193925767ba4e414970 | verification/P02PRE-R1H-H2-RUN/resource-closeout-r1.json | stdout/stderr/exit, three review rounds, prompts and input manifests retained and pinned |
| H2-RUN evidence integration worktree | G:/CODEX/New Manga.workspace/worktrees/P02PRE-R1H-H2-RUN-INTEGRATION | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/P02PRE-R1H-H2-RUN-INTEGRATION | verification/P02PRE-R1H-H2-RUN/resource-closeout-r1.json | clean at 06990b79; evidence, closeout and terminal checkpoint committed |
| task-env | NOT_APPLICABLE | NOT_APPLICABLE | - | - | no task-specific environment was created |
| dataset/model/test-material | NOT_APPLICABLE | NOT_APPLICABLE | - | - | no dataset, model weights, or separate test material was created |
| temp one-shot lock | G:/CODEX/New Manga.workspace/agent-output/codex/P02PRE-R1H-H2-RUN/run-h2-20261013-de77a42fccca4193925767ba4e414970/one-shot.lock | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/agent-output/codex/P02PRE-R1H-H2-RUN/run-h2-20261013-de77a42fccca4193925767ba4e414970/one-shot.lock | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | zero-byte lock retained; process query found no active collector |
| exchange | NOT_APPLICABLE | NOT_APPLICABLE | - | - | no separate exchange directory was created |
## Execution events

2026-10-13: proposed Task converted to ready after exact source, source Review/adjudication, isolated integration, 43/43 live preflight, unique RunId and absent output target were frozen. At that checkpoint the collector remained NOT_RUN; root HEAD/main/index and pre-existing user changes remained untouched.

2026-10-13T10:26:48Z: Owner Codex accepted H2-RUN and moved it from ready to in_progress. Inputs, RunId, output target, launcher SHA and selfcheck result remained frozen.

2026-10-13T10:33:57Z: Two pre-launch checks stopped before starting the collector. Their evidence was pinned; launcher selfcheck later passed 11/11 before the unique invocation.

2026-10-13T10:39:08Z: The sole collector invocation completed with launcher/collector exit 0 and disposition COLLECTED_NEW_TIME_EVIDENCE. The output contains 80 NDJSON records, 78 observations, 55/55 checks PASS and 55/55 JSON Pointers resolved.

2026-10-13T10:50:00Z: DSH R1 returned BLOCKED because its review environment could not execute commands and reported an ambiguous notRun count. Codex verified all 16 R1 pins and wrote a corrected R2 summary separating zero NOT_RUN checks from seven notRun scope categories.

2026-10-13T11:02:00Z: DSH R2 accepted the count correction and found a stale R1 title. Codex corrected the title and froze a focused R3 input set.

2026-10-13T11:10:00Z: DSH R3 approved the exact corrected artifact with zero findings. Codex verified the raw result and all three review pin sets, then adjudicated APPROVED.

2026-10-13T11:27:02Z: Codex verified the root HEAD/main/index, source and owner worktrees, H2 integration worktree, retained run paths, empty one-shot lock and absence of a matching active collector process. No cleanup was safe or needed: referenced evidence/worktrees and root user data are preserved. Resource closeout manifest, Handoff R2 and checkpoint were committed in the isolated integration branch. The Task remains approved until final governance checks and current-pointer transition pass.

## Closeout Record

- Closeout date / Codex: 2026-10-13 / Codex /root.
- canonical_evidence_status: complete.
- resource_closeout_status: complete.
- Deletion, migration and archive totals: 0 items / 0 bytes.
- Unclosed items: none. Referenced evidence/source worktrees and root user data remain preserved under explicit dispositions.
- Current pointer transition: STATUS/Plan/Task README now point to P02PRE-R1H-H1-CURRENT-INPUT-REVIEW (ready); H2-RUN checkpoint records terminal completion and remains linked from the completed Task.


