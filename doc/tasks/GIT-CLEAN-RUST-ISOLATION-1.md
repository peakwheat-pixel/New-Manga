---
id: GIT-CLEAN-RUST-ISOLATION-1
title: Rust测试隔离修复与真实多channel饱和验证
kind: implementation
governance_version: 3
status: in_review
approval: codex_scope_released_user_review_disposition_2026-10-24
suggested_owner: ZCode
owner: ZCode
reviewer: ZCode
depends_on: []
base_commit: e34a90d001cce1fa966aec7d2b032bb5ad1cf148
branch: codex/git-clean-rust-isolation-r2
worktree: G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/source-r2
integration_commit: null
delivery_head: 1829a38a41587a0d680001a40d206886afb0911d
canonical_evidence_status: complete
resource_closeout_status: pending
evidence_dir: verification/GIT-CLEAN-RUST-ISOLATION-1
allowed_paths:
  - doc/tasks/GIT-CLEAN-RUST-ISOLATION-1.md
  - verification/GIT-CLEAN-RUST-ISOLATION-1/**
  - G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/**
---

# GIT-CLEAN-RUST-ISOLATION-1

## 来源与目标

用户要求裁定后续范围；依据 DIAG-1 的 DSH r1 approved（仅诊断）和父 Review R-001。Codex 决定另冻并释放本 Task，交 ZCode 实现、DSH 独审，不改变父候选或 main。无产品契约/依赖变更。DIAG 审查是只读取证输入，无需将诊断补丁先集成；故 depends_on 为空。

## Acceptance Criteria

- [ ] **AC1**：registry隔离修订与全使用者清点已交付，编译/生产check通过。 <<PARTIAL: DSH r2确认主要隔离/资源真实性；R006异常清理及R2-F02..05仍待补>>
- [x] **AC2**：r2固定1829a38默认并发完整source两次连续153 passed/0 failed/6 ignored/12 filtered，exit0。 <<MET>>
- [ ] **AC3**：真实多channel公平响应、容量、取消/关停与回收验证。 <<BLOCKED: r2四个Core场景通过，fault20真实write超时及资源回收通过，但peak0未达32，容量接受/拒绝路径未验证>>
- [x] **AC4**：r2固定head/源码与运行器SHA、真实日志、新Appointment及独审执行已完成（DSH blocked，不等于技术通过或集成）。 <<MET>>

## 允许修改范围

仅隔离副本 `apps/desktop/src-tauri/src/` 内测试隔离guard、cfg(test)模块及新压力测试；其测试侧car/运行器置本Task verification或workspace。先清点 library_bridge/core_bridge/main 等间接Drop/reap调用，不只给四个显式测试加锁。生产接口、registry实现与MAX不变；若发现必须修改生产逻辑，停止该部分并交Codex另冻修复范围。不得以整体测试串行、单线程registry、增大MAX或忽略失败来刷绿。

## 测试要求（冻结场景，planned）

1. 独立目录离线恢复/构建frontend；Rust源码来自本副本，数据/APPDATA/LOCALAPPDATA/TEMP/TMP隔离。构建缓存可共享，但每次披露并记录重新编译输入。日志头即时保存运行器文件SHA、argv/cwd、精确head、git diff HEAD断言exit和输出、env白名单、venv、unset项；尾部保存真实EXIT。
2. `cargo test --locked --offline -- --skip packaged_sidecar_tests::`，默认并发；两个连续通过运行之间不改代码/输入。相同失败最多两次；失败后先裁定新变量，不能循环重跑。
3. 压力用独立进程运行，冻结1/8/20个真实 `StdioLibraryChannel`，启动真实Python Core侧car、临时DB与测试生成输入；每channel唯一请求ID、至少一次成功往返。分别测试正常关停、并发取消/关停，以及故障注入令真实管道I/O阻塞后走生产reaper/holder。故障注入须明确标记，不能把确定性假侧car当真实Core。
4. 每个场景墙钟上限120s，清理预算30s；记录每channel请求完成/延迟、最大registry数<=32、接受/拒绝handle的归属、测试自有PID/管道/线程最终回收和剩余数。必须实际触及容量边界；无法触及则该场景BLOCKED，不把“20个channel已启动”当饱和证据。不能只断言全局平均成功而漏掉饿死channel。超时仅清理核实归属的自有子进程。
5. 新增压力测试与默认套件区别标记，不能因isolated通过改写全套结论。packaged若再次运行，先从新head构建并冻结sidecar，旧e34的12通过不能移植为新head通过。

## 禁止范围与阻塞

不push、不done、不改源main/父e34/fed/旧证据/系统ACL，不删素材/refs/worktree、不GC/prune，不借旧ignored bundle或真实用户库，不改共享契约/Schema/依赖，不运行Legacy GUI。无可用Core依赖时保留真实压力BLOCKED，不能降级冒充。

## Canonical Evidence

当前证据以CODEX_VALIDATION.md和workspace/review-package-r1为准。ZCode原始PARTIAL/BLOCKED阶段副本保留；未运行ps1仅作来源，不冒充执行证据。

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-001 | AC1/AC2/AC3/AC4 | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/review-package-r1/PACKAGE_MANIFEST.json | - | b5fe398dc27ac0656ec51958c8bc430d832c23a07e4edc7d05ae910ffeee4a41 | CANONICAL |
| EV-002 | current/source | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/codex-validation-r1/child-lock-isolated-r1.json | - | a373db0347a8e4aec69bf1e5c310af4b6188d5bd1a710c258a5c816bf6b5d8a1 | SOURCE_PIN |
| EV-003 | current/source | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/codex-validation-r1/child-lock-isolated-r1.log | - | 5ce365cc18102c2fe7b2dcc6906484bbe0ff1f4a82104e76f2b987b425e6547e | SOURCE_PIN |
| EV-004 | current/source | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/codex-validation-r1/compile-r1.json | - | 9e1f316666632bc5143c4d133ea62f51facc2869d41cc8374639b381ffc9db63 | SOURCE_PIN |
| EV-005 | current/source | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/codex-validation-r1/compile-r1.log | - | 58834fb8175114de32aaeca0a1215ff8b14044fd3e93e204d6706638f3e209d0 | SOURCE_PIN |
| EV-006 | current/source | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/codex-validation-r1/compile-r2.json | - | 7bbb4b5314ac1e52beea12a6935dce2b6811ab93bb5574416d721714480c7ebd | SOURCE_PIN |
| EV-007 | current/source | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/codex-validation-r1/compile-r2.log | - | 02c0edd0235383e0358738908454f428ebbf20d930cd687d6c7382cae78a79cd | SOURCE_PIN |
| EV-008 | current/source | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/codex-validation-r1/fixed-head.json | - | aba55f0057281b2599d428055c9ccc39ff939e3b7bd9f564a597ba8f7d0c895e | SOURCE_PIN |
| EV-009 | current/source | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/codex-validation-r1/production-check-r1.json | - | 8e2111e46971b958430e3545b39e9d2b0cdb134245f7de574d4724a30993fa29 | SOURCE_PIN |
| EV-010 | current/source | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/codex-validation-r1/production-check-r1.log | - | d9d6cb53654ac19dd0547a57cf8d4019ad65a2bc6192a6a87f7adb08a91b819a | SOURCE_PIN |
| EV-011 | current/source | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/codex-validation-r1/source-r1.json | - | 5e5a04a37ece327d8369df98d0adc2f6318e6c1bb1187e7b4269403d12b06dc2 | SOURCE_PIN |
| EV-012 | current/source | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/codex-validation-r1/source-r1.log | - | 1be31937be2eb68398282c2b4ac7bcffef7f35038822f0c15ceac8e96bc2cee8 | SOURCE_PIN |
| EV-013 | current/source | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/codex-validation-r1/source-r2.json | - | 4bd0b2a268261bc9959b7fe1a806246b2f2b2b82d34c73b4606f9b06b762b204 | SOURCE_PIN |
| EV-014 | current/source | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/codex-validation-r1/source-r2.log | - | f280840290f70166be6d4232ab5ef07c87cd6f02906b5e009082b4053a3527a5 | SOURCE_PIN |
| EV-015 | current/source | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/codex-validation-r1/stress-cancel-20.json | - | 4dcbd3e7553af9df84467c9bdc69ee5fc4f142afa82904894c64e5bfe25ebaab | SOURCE_PIN |
| EV-016 | current/source | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/codex-validation-r1/stress-cancel-20.log | - | 6facbff939761559ded3f4f3e9501086eed8b6f9c5c619f36ac151365266cb1a | SOURCE_PIN |
| EV-017 | current/source | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/codex-validation-r1/stress-fault-20.json | - | 95ad0acf6bc1dbadd846dec3aa731392d8378bd94731a9dd4a9694b67240721b | SOURCE_PIN |
| EV-018 | current/source | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/codex-validation-r1/stress-fault-20.log | - | 612ce71c917a005daca1d46d3310428c57c52a086e2d28772f68924ff6368f67 | SOURCE_PIN |
| EV-019 | current/source | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/codex-validation-r1/stress-real-1.json | - | 2e4a910bb00668aaa133567fec4bce84b28537d1df226b314b3fe2a4acd1afac | SOURCE_PIN |
| EV-020 | current/source | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/codex-validation-r1/stress-real-1.log | - | 0887fbaf2685748d52c16667a47988d3fb01184cbabaae94abbd7c3d69215cc6 | SOURCE_PIN |
| EV-021 | current/source | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/codex-validation-r1/stress-real-20.json | - | a2ff7de6ea50b3e0c158bb7503883c96baeef5934213d7ee3224cd07ef7e6524 | SOURCE_PIN |
| EV-022 | current/source | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/codex-validation-r1/stress-real-20.log | - | 20ceddd77a70b850c5f1f12ea14f7b158e37c93b56378263efa44b444f6cbc91 | SOURCE_PIN |
| EV-023 | current/source | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/codex-validation-r1/stress-real-8.json | - | c2f340d21c330b73a1a848b4a86440f847c26b5c5235ac35b3af1ea6e22f33bd | SOURCE_PIN |
| EV-024 | current/source | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/codex-validation-r1/stress-real-8.log | - | d2f38c0e0c9ffd4bfdb49516e1c27c31b98d8c75ca453a90f7c77193ed71fac5 | SOURCE_PIN |
| EV-025 | current/source | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/codex-prerequisites-r1/frontend-build-dirty.diff | - | 4f5386a41372bed0ebfbae04facb8c869ae96cc9f607dff36ebb6db93fa8a443 | SOURCE_PIN |
| EV-026 | current/source | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/codex-prerequisites-r1/frontend-build.json | - | 5deaf8dde05dfe7260863834620cb183f2e8719a3109942743bfad62828c8fa2 | SOURCE_PIN |
| EV-027 | current/source | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/codex-prerequisites-r1/frontend-build.log | - | 8411f68325d77fed333b10b48953641e6552e695e44f93b36a48b408b7c25648 | SOURCE_PIN |
| EV-028 | current/source | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/codex-prerequisites-r1/npm-ci-dirty.diff | - | 4f5386a41372bed0ebfbae04facb8c869ae96cc9f607dff36ebb6db93fa8a443 | SOURCE_PIN |
| EV-029 | current/source | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/codex-prerequisites-r1/npm-ci.json | - | 5a9542bb51fce5b2ccde76fee474cfd62959ed6aa5ec04c93ed61f3fc55a7c6c | SOURCE_PIN |
| EV-030 | current/source | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/codex-prerequisites-r1/npm-ci.log | - | 4013a267e1badf859b47038d0843ac9ab5d494eee05684333dfbf3979f7654b2 | SOURCE_PIN |
| EV-031 | current/source | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/dispatch-zcode-r1/exit.json | - | b2df215b692b041777a7f987fdea2afed0570379ba7d455ea298516ee1ebe380 | SOURCE_PIN |
| EV-032 | current/source | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/dispatch-zcode-r1/launch.json | - | df1406bbeb5b2f7b0560195b50d44302111f48207999adb16b9fd8a59dd80475 | SOURCE_PIN |
| EV-033 | current/source | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/dispatch-zcode-r1/parsed-result.json | - | da23b6050357ebca6488b918d32408aca770a2c4b9ebe48f3bbce9b2b87584ff | SOURCE_PIN |
| EV-034 | current/source | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/dispatch-zcode-r1/prompt.txt | - | 01e96b06ab164164309a4fa19ec6810325ade333e525effc6415df0fbda25514 | SOURCE_PIN |
| EV-035 | current/source | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/dispatch-zcode-r1/stderr.log | - | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| EV-036 | current/source | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/dispatch-zcode-r1/stdout.log | - | ca0e35ed9c255078772a659b21c5389de71119cc9c6ca077c7f2359630c0c7e2 | SOURCE_PIN |
| EV-037 | current/source | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/runner/run-rust-default-parallel.ps1 | - | fbb8acb202f4e13c888c1f0212ff0e9b6eb6b1d3e2753e646f931864ac5c9b45 | SOURCE_PIN |
| EV-038 | current/source | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/runner/run-stress-scenarios.ps1 | - | 004539673d7030825fa48476f6f6e33ffe1a82272c07b4da5fa1150082780fe1 | SOURCE_PIN |
| EV-039 | current/source | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/codex_verify.py | - | 5c1ebf56fef30782308960bb28dc766eb659d2521fda25615f1f21132bd2f299 | SOURCE_PIN |
| EV-040 | current/source | G:/CODEX/New Manga/verification/GIT-CLEAN-RUST-ISOLATION-1/APPOINTMENT.md | - | ff79bfaa88e19fa6604f6733f48b4765e300efb47a3d681c60486b4ca44dff49 | SOURCE_PIN |
| EV-041 | current/source | G:/CODEX/New Manga/verification/GIT-CLEAN-RUST-ISOLATION-1/checkpoint.md | - | 25fedcc04c409648a009e7d7cf1fe592e13eea03a1a73388cb6fde54e4d655d4 | SOURCE_PIN |
| EV-042 | current/source | G:/CODEX/New Manga/verification/GIT-CLEAN-RUST-ISOLATION-1/CODEX_VALIDATION.md | - | bb2eed3e5b87e945bdc197e629d1be320c4a461d9ce8b346e7b74d0699c0e2ba | SOURCE_PIN |
| EV-043 | current/source | G:/CODEX/New Manga/verification/GIT-CLEAN-RUST-ISOLATION-1/HANDOFF.md | - | 93aac1b153f16de335655eb203a04aadf4018ea47d4ea92f0ea04d80636c5e70 | SOURCE_PIN |
| EV-044 | current/source | G:/CODEX/New Manga/verification/GIT-CLEAN-RUST-ISOLATION-1/RESULT.md | - | 9265a78e3e3f4a4a2ea1b9c4f9018fe3ce5c4791dccab3634bb83476ec008402 | SOURCE_PIN |
| EV-045 | current/source | G:/CODEX/New Manga/verification/GIT-CLEAN-RUST-ISOLATION-1/worktree-diff-vs-e34.patch | - | aea75d5201142535880516e8168905316920f905eb04b2e475cd6e63113db483 | SOURCE_PIN |
| EV-046 | current/source | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/source/apps/desktop/src-tauri/src/library_bridge.rs | - | c01363e96f2579dea0061d8956ab8d96c6002a7d9b31b3d8a854426dba8f66bf | SOURCE_PIN |
| EV-047 | current/source | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/source/apps/desktop/src-tauri/src/main.rs | - | b315e632e51befc7311ddb58fb513d6e6f400f9e84d1d0737d0a0e74404764cd | SOURCE_PIN |
| EV-048 | current/source | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/source/apps/desktop/src-tauri/src/multichannel_stress_tests.rs | - | 66387712c974018745b4a16fc4d0d2a3df09bd90718df48d6d66c068876707b1 | SOURCE_PIN |
| EV-049 | current/source | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/codex-validation-r1/SUMMARY.json | - | 905d4f0b65af1f4269da12bf1ed2500f88f77da88e21137d435d3355146dd82c | SOURCE_PIN |
| EV-050 | current/source | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/review-package-r1/zcode-delivery/APPOINTMENT.md | - | ff79bfaa88e19fa6604f6733f48b4765e300efb47a3d681c60486b4ca44dff49 | SOURCE_PIN |
| EV-051 | current/source | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/review-package-r1/zcode-delivery/checkpoint.md | - | c3ad76862f962199d6d2d304a0dd2f5019bfeb3997a503ab51d4ad10665ccc20 | SOURCE_PIN |
| EV-052 | current/source | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/review-package-r1/zcode-delivery/HANDOFF.md | - | 1da784195d13217219664be5d318dea62566caefa865aef79a807fa92a07df78 | SOURCE_PIN |
| EV-053 | current/source | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/review-package-r1/zcode-delivery/RESULT.md | - | fecade9457683da70a7de8f3e998f3942b409b8e02a7362b0e2980000bc02038 | SOURCE_PIN |
| EV-054 | current/source | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/review-package-r1/zcode-delivery/TASK-before-codex-validation.md | - | 4b66703034cef9917868aeda0b856b67dc248daaabc25076fc0135a47662f3b9 | SOURCE_PIN |
| EV-055 | current/source | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/review-package-r1/zcode-delivery/worktree-diff-vs-e34.patch | - | aea75d5201142535880516e8168905316920f905eb04b2e475cd6e63113db483 | SOURCE_PIN |
| EV-056 | current/source | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/review-package-r1/change-from-base.patch | - | dbbb8a3c6b033261f7b45c8be85b523208a6211ddeb5e2c80454aa125116d31e | SOURCE_PIN |

| EV-057 | r2/revision-gate | G:/CODEX/New Manga/verification/GIT-CLEAN-RUST-ISOLATION-1/r2/SCOPE.md | - | d4c861b1ef95ebd81f583f9d8c1acdf609d28fad5388161753cc7df608507d1a | CANONICAL |
| EV-058 | r2/revision-gate | G:/CODEX/New Manga/verification/GIT-CLEAN-RUST-ISOLATION-1/dsh-review-r1.md | - | 5d1c43e6d1c18f3d7f855012b05d5b516d54dca81463b36a916188276c6b8cc8 | SOURCE_PIN |

| EV-059 | r2/AC1-AC4 | G:/CODEX/New Manga/verification/GIT-CLEAN-RUST-ISOLATION-1/r2/CODEX_VALIDATION.md | - | 04705702e9f5731a854a8b27f7dd84f1853688e9ceb6a788284239c9ee88dfca | CANONICAL |
| EV-060 | r2/AC1-AC4 | G:/CODEX/New Manga/verification/GIT-CLEAN-RUST-ISOLATION-1/r2/APPOINTMENT.md | - | 673e3eea6c8b56aa6b63ae39e2175526b52bebb613da3dffc3d08a896b6603d3 | CANONICAL |

| EV-061 | r2/frozen-package | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/review-package-r2/PACKAGE_MANIFEST.json | - | 05fef6a99f419d9d4efcd203f78aa02871801dbe9216ed23e26d2350f8de3f58 | CANONICAL |

| EV-062 | r2/source | G:/CODEX/New Manga/verification/GIT-CLEAN-RUST-ISOLATION-1/r2/checkpoint-current.md | - | d47a3f585811ea9895e427c2c8e7ae865d184e4427917abe723eebe8f9888a8c | SOURCE_PIN |
| EV-063 | r2/source | G:/CODEX/New Manga/verification/GIT-CLEAN-RUST-ISOLATION-1/r2/checkpoint.md | - | 59d2ed736b423ceeb9c26913c54117a2ae2dd2f70a155a0b15a774d4a64073cd | SOURCE_PIN |
| EV-064 | r2/source | G:/CODEX/New Manga/verification/GIT-CLEAN-RUST-ISOLATION-1/r2/HANDOFF.md | - | 90c3a0bc0ecf1a51c2af84bb19b1abd6eb12c9cb50195dd12f0e7ffed60a6246 | SOURCE_PIN |
| EV-065 | r2/source | G:/CODEX/New Manga/verification/GIT-CLEAN-RUST-ISOLATION-1/r2/RECEIVER_NOTES.md | - | 6ae59c20f9ff5f8999410426ec27593ccd6c16c629b4f94a8e2e045a9e97d2c4 | SOURCE_PIN |
| EV-066 | r2/source | G:/CODEX/New Manga/verification/GIT-CLEAN-RUST-ISOLATION-1/r2/RESULT.md | - | dfa6cf79ec1dfbef0a0419afa4ae1e04795683d56e0a93a01361209cafb055a7 | SOURCE_PIN |

| EV-067 | r2/review-disposition | G:/CODEX/New Manga/verification/GIT-CLEAN-RUST-ISOLATION-1/r2/dsh-review-r2.md | - | a0bba91a300baa3543ceb9e7140c94d93e7860ae999c36b2d1ef7b21a8ac3829 | CANONICAL |
| EV-068 | r2/review-disposition | G:/CODEX/New Manga/verification/GIT-CLEAN-RUST-ISOLATION-1/r2/DISPOSITION.md | - | d76248800cac9941cb0e4db00961cdb1c5ec024037e6f454890dd42a41d7ef28 | CANONICAL |
| EV-069 | r2/review-disposition | G:/CODEX/New Manga/verification/GIT-CLEAN-RUST-ISOLATION-1/r2/checkpoint-review.md | - | 5278bf0e184068f07d5cfa5e7b86908559ff879f2e9273a9f193f82d8749e068 | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| isolated-repo/build/temp | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1 | PRESERVE_REFERENCED | — | e34基线 | 独立仓库，无远端；禁止清理 |
| source/evidence | 父e34与DIAG fed及冻结包 | PRESERVE_REFERENCED | — | 原Task pins | 仅只读，不是集成依赖 |
| user-data/exchange | — | NOT_APPLICABLE | — | — | 不用私有素材，未派发 |

## 交付与运行记录

READY待Owner认领，未运行测试、未派发。交付本Task RESULT/HANDOFF、实际新head和证据表。新head产生后必须新建 `verification/GIT-CLEAN-RUST-ISOLATION-1/APPOINTMENT.md` 绑定精确base/head、DSH和唯一Review写路径；当前尚无可任命的交付head，不伪造Appointment已执行。

可直接转发给 ZCode：在 G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/source，branch codex/git-clean-rust-isolation-1，base/current head均e34a90d001cce1fa966aec7d2b032bb5ad1cf148，按本Task AC1–4仅修cfg(test)隔离并新增真实Core多channel饱和验证。先盘点所有registry间接调用，保持生产MAX32及回收语义；默认并发完整source套件两次通过，真实1/8/20channel场景按冻结指标记录，失败/未触及饱和如实BLOCKED。只写允许路径，提交新head、RESULT/HANDOFF/日志和SHA；交Codex重新Appointment DSH独审。不改源main、父候选、系统ACL、契约/依赖，不push、不done、不自行集成，不改他人内容。

2026-10-24 用户裁决：本Task由Antigravity改派ZCode，suggested_owner/owner均为ZCode；Reviewer仍DeepSeek Harness。冻结范围、base/branch/worktree与验收Gate不变，仍ready、未认领/未派发。旧诊断说明或冻结包中的Antigravity是改派前建议，当前归属以本Task和STATUS为准；不改旧证据字节。

2026-10-24 auto派发运行记录：ZCode CLI 0.17.0，mode=edit，原始输出在workspace/dispatch-zcode-r1；Owner已在 `verification/GIT-CLEAN-RUST-ISOLATION-1/checkpoint.md` 确认认领，Task进入in_progress。历史READY/未派发描述保留为当时记录，当前运行状态以本段和STATUS为准；未获新head或测试结果，不虚构成功。

2026-10-24 ZCode PARTIAL/BLOCKED 交付记录（详情见 `verification/GIT-CLEAN-RUST-ISOLATION-1/RESULT.md` 与 HANDOFF.md）：
- AC1 清点+cfg(test) 隔离实现完成（生产语义零变化：cfg(not(test)) inline 回同一全局 static，MAX=32/锁/背压/holder 不变；仅 4 个 registry 语义测试经 TEST_REGISTRY_EXCLUSIVE 互斥+owner 线程 override 隔离，其余 ~150 测试并发不变，未整体串行、未 skip）。AC3 五场景 `#[ignore]` 压力代码+两个 canonical 运行器交付（workspace runner/）。
- **执行权限阻塞（不可处理）**：该 CLI 会话 Bash 层无 permission client，cargo/python/npm 执行、git add/commit、mkdir/rm、输出重定向全部拒绝（精确请求在 RESULT §2）；按用户指令记录并停止相应部分，未绕过。故 AC1 编译/套件验证、AC2 两次默认并发、AC3 执行、AC4 新 head 全部 BLOCKED；packaged/frontend 构建 NOT_RUN（不继承 e34 旧 12 passed）。
- 交付绑定：实现仓库工作树文件 SHA256（RESULT §8；canonical_evidence RUSTISO-01..05）；无新 head，不创建 APPOINTMENT。遗留 untracked 探针 `source/.git-probe-tmp.md`（rm 被拒，建议 Codex 提交前删除）。
- 待 Codex：有执行权限会话删探针→编译验证→`git add`（library_bridge.rs/main.rs/multichannel_stress_tests.rs）+commit 新 head→回填 delivery_head→新 head 上执行 RUSTISO-04/05 运行器（AC2/AC3）→回填计数与指标→重新 Appointment DSH 独审。相同失败上限 2 次；需改生产逻辑即停另冻。

## Codex当前交付与新Appointment

本Task已固定3b035365682db0965bbde4b0a6113e3e000ae7e7并进入in_review，技术Gate仍BLOCKED，非产品批准。当前CODEX_VALIDATION.md取代历史Owner未执行描述。APPOINTMENT.md任命DSH只写dsh-review-r1.md；子进程/源码/HEAD保护与实际测试按冻结包核验。探针未删除未暂存。源main/父e34不变，不push、不done、不改系统ACL。

## r2 当前修订

DSH r1 decision=blocked，R-001..007均open。依据用户继续auto，Codex释放[r2 SCOPE](../../verification/GIT-CLEAN-RUST-ISOLATION-1/r2/SCOPE.md)，沿用ZCode Owner，进入in_progress；r2新副本/分支见frontmatter，起点3b03536，累计base仍e34。旧delivery_head3b03536与EV-001..056仅为r1证据，不指代r2通过；原文件不改字节。当前恢复点：[r2 checkpoint](../../verification/GIT-CLEAN-RUST-ISOLATION-1/r2/checkpoint.md)；最新独审仍[dsh-review-r1](../../verification/GIT-CLEAN-RUST-ISOLATION-1/dsh-review-r1.md)。新head后新Appointment，不修改生产预算。

2026-10-24 ZCode r2 认领与交付记录（R001–R007 逐项处理见 [r2/RESULT.md §一](../../verification/GIT-CLEAN-RUST-ISOLATION-1/r2/RESULT.md)；交接步骤见 [r2/HANDOFF.md](../../verification/GIT-CLEAN-RUST-ISOLATION-1/r2/HANDOFF.md)）：
- r2 工作树修订完成（本会话仍无 Bash permission client，未编译/未运行/未 commit，Codex 代跑）：`source-r2` 的 `library_bridge.rs`（R004 holder 经 thread-local 继承同受测 registry+ac1 持锁 spawn/等待证明/同 registry 注册/收尾 reap 断言；R005 with_unreaped_registry fail-closed+槽安装清除验证；R006 Arc 所有权替代 Box::leak+guard drop 显式 reap 账本；R001 child_lock msc 握手+600ms 持锁+fallback 分支判别断言；R007 kill_and_wait_for_test）与 `multichannel_stress_tests.rs`（R003 ChildIdentity/tasklist PID 消失/线程账本/names 归属；R002 错误包络+阻塞相位证据+pre-drop joined 标志+peak>=32 保留；R007 取消/Drop 分立断言）；main.rs 未改（SHA=3b）。新运行器 `workspace/r2-runner/`（未执行）。生产 MAX/锁/背压/holder/taskkill 预算零变化；同 registry/静默 fallback/Box::leak 三缺口关闭。
- r2 无新 head（git 写被拒，待 Codex 编译验证后 commit）；AC2/AC3 执行与 packaged 均待 Codex，本轮不预写任何通过结论；fault 饱和按机制分析预计仍 BLOCKED（纯真实管道阻塞被生产 cancel/kill 双解除设计在 join 窗口内回收，机制说明内嵌于测试文档与 r2/RESULT）。
- 待 Codex：编译（--no-run）→最小修（若有）→commit 新 head→回填 delivery_head→新 head 上跑 r2-runner 两脚本（AC2 两次默认并发+AC3 五场景；child_lock 判别单测可选）→回填 r2/RESULT 七项表与 Task 证据（建议 R2-xx 新 EV id）→新 Appointment DSH。同条件失败上限 2；显示生产时序问题即停另冻。

## r2 固定交付与复审

2026-10-25：当前delivery head为1829a38，状态in_review。ZCode CLI最终exit1/HTTP429但保留文件交付；Codex接收修正、编译及12次实际运行详见[r2 CODEX_VALIDATION](../../verification/GIT-CLEAN-RUST-ISOLATION-1/r2/CODEX_VALIDATION.md)。当前恢复点：[r2 checkpoint-current](../../verification/GIT-CLEAN-RUST-ISOLATION-1/r2/checkpoint-current.md)。新[r2 Appointment](../../verification/GIT-CLEAN-RUST-ISOLATION-1/r2/APPOINTMENT.md)只允许DSH写r2/dsh-review-r2.md；独审尚未执行。r1全部原始证据保留。AC2满足不代表AC3或父候选可升级；不改生产预算，不push/done/main/ACL。

## r2 最新独审裁决

2026-10-25：DSH同session复审CLI exit0，有效[dsh-review-r2](../../verification/GIT-CLEAN-RUST-ISOLATION-1/r2/dsh-review-r2.md)，decision=blocked，绑定1829a38。最新处置：[DISPOSITION](../../verification/GIT-CLEAN-RUST-ISOLATION-1/r2/DISPOSITION.md)；当前恢复点：[checkpoint-review](../../verification/GIT-CLEAN-RUST-ISOLATION-1/r2/checkpoint-review.md)。R001/003核心/004/005核心/007关闭；R002/006 partial，R2-F01..05登记open。AC3仍未达32，不approved/集成/父升级；Task保持in_review，无当前实施。下一切片建议先另冻test-only设计，READY仍无；不推定需改生产，不改AC/旧证据。此前“待独审”文字为历史时点，本段为最新结论。

AC4仅指交付绑定与独审已执行的程序性AC，证据EV-059..061/067；2026-10-25依真实执行标MET，不表示Review批准、AC3通过或Task done。

## 2026-10-25 DSH 接管后的处置

DSH 接任 Lead / Architect / Integrator（见 `doc/GOVERNANCE_TAKEOVER_2026-10-25.md`）。本 Task 的 Owner/实现作者仍为 ZCode；当前 Reviewer 改派 **ZCode**（同日再次改派，见下节「Reviewer 二次改派」）。DSH r1/r2 两份 Review、r2/DISPOSITION、测试日志、包与源码字节全部保持原样，不改写为通过。

当前事实不变：delivery head `1829a38a41587a0d680001a40d206886afb0911d`；默认并发两次 153 passed/0 failed/6 ignored/12 filtered；AC1 PARTIAL、AC3 BLOCKED（真实 32 饱和未达，peak 0/32），R2-F01..05 中部分 open。Task 保持 `in_review`，无当前实施。本 Task 不是干净快照 push 的前置 Gate；其 blocked 结论保留，不能作为产品并发安全或父候选升级的批准。任何新 head 必须按新 Appointment 由非作者独立审查后再进入 DSH 集成裁决；重复失败遵守同一失败上限 2 次，不新增无边界的压力门槛。

## Reviewer 二次改派（2026-10-25）

- **改派**：frontmatter `reviewer` 由 `Antigravity` 改为 `ZCode`；同时修正上两节中指向 Antigravity 的 Appointment 描述。STATUS 与 REBASELINE_PLAN 同步。
- **依据**：用户 2026-10-25 明令本项目**停用 Antigravity / agy**。保留 `Reviewer=Antigravity` 会造成指向已停用 Agent 的死指针，后续任何 Appointment 都会卡死。
- **遗留冲突（如实登记，不隐瞒）**：本 Task 的 `owner` 同为 `ZCode`，与协作协议「Owner 与 Reviewer 必须不同」冲突。因此本次改派**只是清除死指针**，不构成对 ZCode 自审的授权：
  - 本 Task 在本轮不复活、不产生新 head、不进行任何 ZCode 自审；
  - 若将来复活，独立审查必须由**未参与该 head 实现**的 Agent 执行（候选：Codex，或按协作协议记 `reviewer_unavailable` 并等待可用 Reviewer），并在新 `APPOINTMENT.md` 中重新绑定精确 base/head 与唯一 Review 写路径；
  - 备选方案「改 Owner 为 Codex、Reviewer 留 ZCode」未被采用：那会把一个 blocked 的环境线 Task 重新拉回实施队列，与本轮"绕开环境线、聚焦产品收口"的优先级相反。
