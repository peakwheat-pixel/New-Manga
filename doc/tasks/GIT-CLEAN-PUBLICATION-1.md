---
id: GIT-CLEAN-PUBLICATION-1
title: 不含私有素材的独立源码快照准备
kind: governance
governance_version: 3
status: in_review
approval: user_approved_next_step_2026-10-24
suggested_owner: Codex
owner: Codex
reviewer: Antigravity
depends_on: []
base_commit: 349e61faff5f93067af5d4ce2d9e394e0d665b8c
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: e34a90d001cce1fa966aec7d2b032bb5ad1cf148
canonical_evidence_status: complete
resource_closeout_status: pending
evidence_dir: verification/GIT-CLEAN-PUBLICATION-1
allowed_paths:
  - verification/GIT-CLEAN-PUBLICATION-1/**
  - doc/tasks/GIT-CLEAN-PUBLICATION-1.md
  - doc/tasks/NEW-MANGA-V1-FULL-AUDIT.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-PUBLICATION-1/**
---

# GIT-CLEAN-PUBLICATION-1

## 来源与目标

用户确认169页漫画“我自己的，但是不传播”，随后对“准备独立干净源码快照、保留原main与证据”的推荐回复“下一步”。Codex据此释放本地快照准备，不授权上传。来源报告：`audit/V1-FULL-AUDIT/reports/MATERIAL_DISPOSITION_OPTIONS.md`、`MATERIAL_CLEARANCE.md`；禁止上传指纹：`audit/V1-FULL-AUDIT/evidence/push-material-disposition.json`。

目标是可检查的独立源码仓库与固定交付SHA，源commit保持不变；不把普通分支/删除末端文件误当成历史隔离。完整审计未关闭，暂移交至blocked，resume_status=in_progress；本Task不替代审计或产品发布验收。DSH r1 已独立审查，decision=blocked；不虚构批准。当前处置见 `verification/GIT-CLEAN-PUBLICATION-DIAG-1/RESULT.md`。

## Acceptance Criteria

- [x] **AC1**：724个源文件、6个生成夹具文件与逐文件源/导出指纹清单已核验。 <<MET>>
- [x] **AC2**：338个禁止对象缺失，素材/历史/日志排除及凭据命中裁定可核查。 <<MET>>
- [x] **AC3**：候选独立单一根提交、无remote、原main/index与P04指纹不变。 <<MET>>
- [ ] **AC4**：前端435通过/构建通过，Rust串行153通过/1忽略/12过滤；Core771通过/3失败。 <<BLOCKED: Core三组参数失败且旧icacls错误码未知，默认并发registry失败复现，packaged以诊断记录为准>>
- [ ] **AC5**：固定SHA、Handoff及冻结证据已形成。 <<PARTIAL: DSH r1独立Review为blocked，补充证据不等于批准push或Task完成>>

## 允许修改范围

只写frontmatter范围。源代码从固定commit读取，主仓业务代码、共享Schema/契约/依赖不修改。导出白名单：src常规源码（Legacy文件仅保留参考，不诊断/运行Legacy GUI）、apps/desktop前端及Tauri源码/配置（不含e2e运行脚本）、tests的Python源码、packaging/m2ac5构建源码及所需包装工具、requirements/pytest配置。逐文件拒绝symlink、非UTF-8/NUL二进制；唯一二进制例外为项目图标 `apps/desktop/src-tauri/icons/icon.ico`，首次引入 `991097d770435377d68615ad0fd12503e16bb842`，记录完整指纹和来源，不把它混同漫画素材。

导出仅新增中文README、来源manifest与忽略规则，不修改产品行为/接口/锁定依赖。原有文档的历史证据不整包导出；源码内历史参考说明不被伪造成在新仓可读取。依赖仅从已安装工具或离线缓存恢复，不获取私有漫画/模型，不调用远程API。新仓不配置remote。

Codex范围细化（2026-10-24）：首版本地候选 `9ee673f9a776583531e21853e00670d4c9d3f65e` 保留不推送。第二版使用独立 `source-export-r2`，不改写首版历史；仅在导出的 `packaging/m2ac5/README.md`、`tests/core/test_core_detect.py` 中将个人目录字面量49745替换为USER，并同时记录源/导出双hash与变换原因。Rust测试编译直接依赖5个TASK-016样本，追加导出其自制生成器（固定源commit），在第二版目录重新生成PNG/manifest，仅允许这些已追溯的合成夹具，不复制原私有素材/图片symlink。生成器仅作离屏fixture绘制，不运行Legacy产品。生成器及每个输出均纳入来源清单和禁止素材检查；该适配不修改共享契约、生产源码或锁定依赖。

第三版修正导出依赖闭包：Rust并发测试运行时还读取 `verification/P04/deterministic_concurrent_sidecar.py`，追加逐文件源码例外（不是P04日志/数据的目录例外）。`source-export-r3` 使用新的独立根提交，前两版均保留；简化变换标签不携带个人目录值，并忽略新产生的jsonl/log。同一进程registry测试并行失败已有记录，追加串行对照；不重复同条件失败超过2次，不修主仓生产代码。Core的3项Hook失败记录为沙箱无法授予python.exe访问，不改系统Python ACL来刷绿。

第四版补齐真实优先测试入口：`library_bridge.rs` 优先加载 `verification/P22-REBASE-1/deterministic_concurrent_sidecar.py`；P04仅为旧fallback，单独导出会等待第二个串行请求。追加P22同名纯测试源码的逐文件例外，最终候选用 `source-export-r4` 独立根提交；前3版保留。已核实并只停止第三版的Task自有P04子进程（PID/父PID/命令行/创建时间核对，日志在本Task），不终止原主控/其他进程。未修改Rust生产代码或测试逻辑。

## 禁止范围

禁止push、远端/default branch/release变更、force、main历史改写、stash/reset/clean/GC/prune；禁止清理素材/refs/worktree、访问真实用户数据库、复制原仓ignored构建/模型产物充当导出构建。`.tmp.driveupload`、verification/audit/archive、session/agent缓存、test_assets、datasets/models、数据库/图片/压缩包均不按目录盲导出。生成构建产物不得进入快照commit。

## 测试要求

计划：`python -B verification/GIT-CLEAN-PUBLICATION-1/prepare_snapshot.py` 负责导出/安全自检；导出frontend目录离线npm ci、npm test、npm run build；导出根目录 `python -B -m pytest tests/core -q -rs`；导出Tauri目录 `cargo test --locked --offline`，显式dev-preview模式且独立CARGO_TARGET_DIR。计划命令尚未执行，实际argv/env/exit写证据；完整安装包、真实模型/GUI不在本次可宣称PASS范围。

## Canonical Evidence

Canonical evidence已固定为仓外SHA pin，不伪造主仓commit；候选delivery_head属于独立artifact仓库，不是main集成提交。

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-SOURCE | AC1 | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-PUBLICATION-1/source-export-r4/SOURCE_MANIFEST.json | - | be511fdb668ea9239ff1acdac6b2d52a74d57917e947339155bd76087a071d6a | SOURCE_PIN |
| EV-GRAPH | AC1/AC2/AC3 | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-PUBLICATION-1/review-package/validation.json | - | 40d812e737f169b3dd9b915179fadf467cb120876833b64fc0553f1255c46d0e | CANONICAL |
| EV-SELECT | AC1/AC2 | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-PUBLICATION-1/review-package/selection.json | - | 406a8945347a5dd8ade834261ce0d967eb213aba6ad759a4b582ecc011e00eb2 | SOURCE_PIN |
| EV-EXPORT | AC1/AC2/AC3 | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-PUBLICATION-1/review-package/prepare_snapshot.py | - | a9d7b71a367c51add3fea0894056ee7c52c41d1353c87e711aaab9fed4f03014 | SOURCE_PIN |
| EV-R4 | AC4 | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-PUBLICATION-1/review-package/checks-r4.json | - | 65733bec9122f26452ee594c003cece891672c616463dca3ee25e7abfc3ae417 | CANONICAL |
| EV-RUST | AC4 | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-PUBLICATION-1/review-package/rust-tests-r4-serial.log | - | ab66e07c335a43a38b17ce945976d694dae7358861a9361d45327e6443616db7 | CANONICAL |
| EV-CORE | AC4 | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-PUBLICATION-1/review-package/core-checks-r2.json | - | 5b6db7169948050d1d8079fe34a1e080b5b4d982d2b24dd8ad32038cd65d02a6 | CANONICAL |
| EV-CORE-LOG | AC4 | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-PUBLICATION-1/review-package/core-tests-r2.log | - | 0215d7e9e12cd08e898e16bd7c41d32fe7ac13c6a5700154777b8049cab8605f | SOURCE_PIN |
| EV-FRONTEND | AC4 | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-PUBLICATION-1/review-package/frontend-tests-r3.log | - | 56f025c20e8a85aff29e827be7a1e07bf9919ca2082b6445d3758b8d82cc49da | SOURCE_PIN |

| SRC-01 | Review/source | G:/CODEX/New Manga/verification/GIT-CLEAN-PUBLICATION-1/checkpoint.md | - | 0418afe62d547b1afd4d9100ef5506f562521667bf4cfe66a2d43f7c0f529d5d | SOURCE_PIN |
| SRC-02 | Review/source | G:/CODEX/New Manga/verification/GIT-CLEAN-PUBLICATION-1/checks-r3.json | - | 59247ea0c5f7b21f9a9a039e7767946c8b303820569b46e3b330be909af67ec7 | SOURCE_PIN |
| SRC-03 | Review/source | G:/CODEX/New Manga/verification/GIT-CLEAN-PUBLICATION-1/checks-r4.json | - | 65733bec9122f26452ee594c003cece891672c616463dca3ee25e7abfc3ae417 | SOURCE_PIN |
| SRC-04 | Review/source | G:/CODEX/New Manga/verification/GIT-CLEAN-PUBLICATION-1/core-checks-r2.json | - | 5b6db7169948050d1d8079fe34a1e080b5b4d982d2b24dd8ad32038cd65d02a6 | SOURCE_PIN |
| SRC-05 | Review/source | G:/CODEX/New Manga/verification/GIT-CLEAN-PUBLICATION-1/core-checks.json | - | 66bcf01555b5d9be412f1ef69d6614bdd4b22cd44e548b660f979f5dbaa21ef3 | SOURCE_PIN |
| SRC-06 | Review/source | G:/CODEX/New Manga/verification/GIT-CLEAN-PUBLICATION-1/core-tests-isolated-deps.log | - | 2ab2873b1f9bcb64811a7e29d85fad4f6cd46a6dbfe81fb4d127a39596101c82 | SOURCE_PIN |
| SRC-07 | Review/source | G:/CODEX/New Manga/verification/GIT-CLEAN-PUBLICATION-1/core-tests-r2.log | - | 0215d7e9e12cd08e898e16bd7c41d32fe7ac13c6a5700154777b8049cab8605f | SOURCE_PIN |
| SRC-08 | Review/source | G:/CODEX/New Manga/verification/GIT-CLEAN-PUBLICATION-1/core-tests.log | - | 88a36904f9fdb613496a7f8e6bed2e6eb0fcdeaecd033c88443bafdec76b05e2 | SOURCE_PIN |
| SRC-09 | Review/source | G:/CODEX/New Manga/verification/GIT-CLEAN-PUBLICATION-1/dsh-review-r1.md | - | a14f1438e487bc5e773793fdce18a9adcc76b362866e4e129304becb1187d136 | SOURCE_PIN |
| SRC-10 | Review/source | G:/CODEX/New Manga/verification/GIT-CLEAN-PUBLICATION-1/frontend-build-r2.log | - | c9114ff5f88d3b7d861b80b80ae91c81703f5ed73b68dc9b2c1d20ff8a506b25 | SOURCE_PIN |
| SRC-11 | Review/source | G:/CODEX/New Manga/verification/GIT-CLEAN-PUBLICATION-1/frontend-build-r3.log | - | 2ab5d52982cb4d017b09e094d04ebe09d15cfd7b69bbc1c94ee9a36431f4c284 | SOURCE_PIN |
| SRC-12 | Review/source | G:/CODEX/New Manga/verification/GIT-CLEAN-PUBLICATION-1/frontend-build-r4.log | - | f728f352316ba54fa3245d629c67a2879aaadc1714ccbe60fd2dbebfb0f9041b | SOURCE_PIN |
| SRC-13 | Review/source | G:/CODEX/New Manga/verification/GIT-CLEAN-PUBLICATION-1/frontend-build.log | - | c3d181b262bc1580e68c445983cbc5e0594b75c0dad400657b026c256646c86e | SOURCE_PIN |
| SRC-14 | Review/source | G:/CODEX/New Manga/verification/GIT-CLEAN-PUBLICATION-1/frontend-checks-r2.json | - | be0c06f916d4d6dc12dceeb0f46f7a887dbe20b3de510316cc8bbbca8999dd18 | SOURCE_PIN |
| SRC-15 | Review/source | G:/CODEX/New Manga/verification/GIT-CLEAN-PUBLICATION-1/frontend-checks.json | - | e44c735c55d2e36d55a49797b8fc80376407d35a0429a35e850c4b4f20686981 | SOURCE_PIN |
| SRC-16 | Review/source | G:/CODEX/New Manga/verification/GIT-CLEAN-PUBLICATION-1/frontend-tests-r2.log | - | 715522972328da29381abc502923521f7f0fb1de2633b86b0ef37cfbf5944dea | SOURCE_PIN |
| SRC-17 | Review/source | G:/CODEX/New Manga/verification/GIT-CLEAN-PUBLICATION-1/frontend-tests-r3.log | - | 56f025c20e8a85aff29e827be7a1e07bf9919ca2082b6445d3758b8d82cc49da | SOURCE_PIN |
| SRC-18 | Review/source | G:/CODEX/New Manga/verification/GIT-CLEAN-PUBLICATION-1/frontend-tests.log | - | 9def8b098ff437ddb6b9c167c580bc77c66bed40029496becb8e65a15c85f057 | SOURCE_PIN |
| SRC-19 | Review/source | G:/CODEX/New Manga/verification/GIT-CLEAN-PUBLICATION-1/HANDOFF.md | - | ca788a28a3f402ddb494d7ae9f00a37a77f7140b397f538c08973cae20108344 | SOURCE_PIN |
| SRC-20 | Review/source | G:/CODEX/New Manga/verification/GIT-CLEAN-PUBLICATION-1/npm-ci-r2.log | - | 207c06c4116a69bb1cfc5932bad0319bac8bf9d8b6809d9415d9ec07e89e3278 | SOURCE_PIN |
| SRC-21 | Review/source | G:/CODEX/New Manga/verification/GIT-CLEAN-PUBLICATION-1/npm-ci-r3.log | - | 207c06c4116a69bb1cfc5932bad0319bac8bf9d8b6809d9415d9ec07e89e3278 | SOURCE_PIN |
| SRC-22 | Review/source | G:/CODEX/New Manga/verification/GIT-CLEAN-PUBLICATION-1/npm-ci-r4.log | - | 207c06c4116a69bb1cfc5932bad0319bac8bf9d8b6809d9415d9ec07e89e3278 | SOURCE_PIN |
| SRC-23 | Review/source | G:/CODEX/New Manga/verification/GIT-CLEAN-PUBLICATION-1/npm-ci.log | - | 9ab62c76016dd6f41d53f75c75d95b7d50910b14088f680a558aabe5954a9d2d | SOURCE_PIN |
| SRC-24 | Review/source | G:/CODEX/New Manga/verification/GIT-CLEAN-PUBLICATION-1/prepare_snapshot.py | - | a9d7b71a367c51add3fea0894056ee7c52c41d1353c87e711aaab9fed4f03014 | SOURCE_PIN |
| SRC-25 | Review/source | G:/CODEX/New Manga/verification/GIT-CLEAN-PUBLICATION-1/RESULT.md | - | 913db9447ba2022d3f004948a85341f36f8fbf088e1f1155097705b692b64558 | SOURCE_PIN |
| SRC-26 | Review/source | G:/CODEX/New Manga/verification/GIT-CLEAN-PUBLICATION-1/rust-checks-r2-serial.json | - | 3be9e49333a9b57d2c96ae845df7e398f7c396971f49b450d18d41df496d6070 | SOURCE_PIN |
| SRC-27 | Review/source | G:/CODEX/New Manga/verification/GIT-CLEAN-PUBLICATION-1/rust-checks-r2.json | - | 5fdd1533889a5fce2b95996c263343f447615f4c8d5173682b9f7f1e1f9356b2 | SOURCE_PIN |
| SRC-28 | Review/source | G:/CODEX/New Manga/verification/GIT-CLEAN-PUBLICATION-1/rust-checks.json | - | 3fb4574aaa814ef2951352089bfe73960f22e9af5c8a35701ae6d7f40d0cf317 | SOURCE_PIN |
| SRC-29 | Review/source | G:/CODEX/New Manga/verification/GIT-CLEAN-PUBLICATION-1/rust-tests-r2-serial.log | - | 615eac60f647477370f566027a0f402b2349e93f35a1e1bf47cc8fa6d5f44515 | SOURCE_PIN |
| SRC-30 | Review/source | G:/CODEX/New Manga/verification/GIT-CLEAN-PUBLICATION-1/rust-tests-r2.log | - | 1f4e47e73ca02912ee8c852c1d660a755d1d163637aa8ab087cc7b9cc4642825 | SOURCE_PIN |
| SRC-31 | Review/source | G:/CODEX/New Manga/verification/GIT-CLEAN-PUBLICATION-1/rust-tests-r3-serial.log | - | 4c4c3b3c7a1655d3f15c8c860c9f7714c4b1d3b3b96683545e1957206ac95887 | SOURCE_PIN |
| SRC-32 | Review/source | G:/CODEX/New Manga/verification/GIT-CLEAN-PUBLICATION-1/rust-tests-r4-serial.log | - | ab66e07c335a43a38b17ce945976d694dae7358861a9361d45327e6443616db7 | SOURCE_PIN |
| SRC-33 | Review/source | G:/CODEX/New Manga/verification/GIT-CLEAN-PUBLICATION-1/rust-tests.log | - | 35a4f72ea3cdeab75c2e0ccd3e72f1812ada0ceabba972ddb94f749146c6b4be | SOURCE_PIN |
| SRC-34 | Review/source | G:/CODEX/New Manga/verification/GIT-CLEAN-PUBLICATION-1/selection.json | - | 406a8945347a5dd8ade834261ce0d967eb213aba6ad759a4b582ecc011e00eb2 | SOURCE_PIN |
| SRC-35 | Review/source | G:/CODEX/New Manga/verification/GIT-CLEAN-PUBLICATION-1/snapshot.json | - | 3ee7f9f28e4b0b4ac41859763fdafb5787fbdd8b2708f90a8274b2c64da8f377 | SOURCE_PIN |
| SRC-36 | Review/source | G:/CODEX/New Manga/verification/GIT-CLEAN-PUBLICATION-1/stopped-test-fixture-r3.json | - | 01233e3af9eab5ff759b7c93d9e750b80788d4a8b2200d7e8368f59aabd5f194 | SOURCE_PIN |
| SRC-37 | Review/source | G:/CODEX/New Manga/verification/GIT-CLEAN-PUBLICATION-1/validation.json | - | 40d812e737f169b3dd9b915179fadf467cb120876833b64fc0553f1255c46d0e | SOURCE_PIN |
| SUP-38 | R-002/R-003/R-004 | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-PUBLICATION-1/review-package-r2/PACKAGE_MANIFEST.json | - | 17a774a5f143f1ab03612fcf30ca94d2e11d392dd97e1640c868d9f6cffd1210 | SOURCE_PIN |
| SUP-39 | R-002/R-003/R-004 | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-PUBLICATION-1/review-package-r2/forbidden-object-fingerprints.json | - | de7f98c103c22d399505042835aa0c6ca045491f00f5fe55affc1b4607bba31e | SOURCE_PIN |
| SUP-40 | R-002/R-003/R-004 | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-PUBLICATION-DIAG-1/core-r2-source-pins.json | - | bc75333218d1d7dfbd87aabafbccc4892acb39e0a6d04dd735cf26990f859ff8 | SOURCE_PIN |
| DB-41 | R-002 | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-PUBLICATION-DIAG-1/core-r2-source-pins/test_export_hook_effective_opt0/library.db | - | cafc7f9a04445771b6e765f9c583363630de1cb472378abd09b5b93510573c7f | SOURCE_PIN |
| DB-42 | R-002 | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-PUBLICATION-DIAG-1/core-r2-source-pins/test_export_hook_effective_opt1/library.db | - | 56c79f8cbadd0bba0536ef364370e0231556c555b7aad3dbbb548f5a59387c18 | SOURCE_PIN |
| DB-43 | R-002 | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-PUBLICATION-DIAG-1/core-r2-source-pins/test_export_hook_effective_opt2/library.db | - | 768e32e2c609a34af907bc452ea91e2902e06a69b18ac6acd81f33c5ed5ac180 | SOURCE_PIN |

| DISP-01 | diagnostic-approved/parent-upgrade | G:/CODEX/New Manga/verification/GIT-CLEAN-PUBLICATION-DIAG-1/dsh-review-r1.md | - | b80481ec426421c2e950f4a2c9e95cff135452ed8ec3a9e0b7b2995cd8cfb67d | SOURCE_PIN |
| DISP-02 | diagnostic-approved/parent-upgrade | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-PUBLICATION-DIAG-1/review-disposition-r1/PRIOR_PINS.json | - | 97b7811295bb92c129999cec90226deca93751f812ef15d1735f561c9f0ce7e4 | SOURCE_PIN |
| DISP-03 | diagnostic-approved/parent-upgrade | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-PUBLICATION-DIAG-1/review-disposition-r1/REVIEW_EXECUTION.json | - | e0f02d6fd9c528b334eb8c1dddb17c1403be64dfea61ccd5e0e25f5897b7c1dc | SOURCE_PIN |
| DISP-04 | diagnostic-approved/parent-upgrade | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-PUBLICATION-DIAG-1/review-disposition-r1/PACKAGE_MANIFEST.json | - | 72092bf793753dbdd19aa1fb6967ffddc17e6cfc6ba75458efbfd6de79ae0cea | SOURCE_PIN |

| DISP-05 | disposition-validation | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-PUBLICATION-DIAG-1/review-disposition-r1/VALIDATION.json | - | 50e7b3ff2118368d63a5accb105893747629f9833a94b2a6959255a3e2c23920 | SOURCE_PIN |

| PUSH-01 | push-gate/Appointment | G:/CODEX/New Manga/verification/GIT-CLEAN-PUBLICATION-1/APPOINTMENT-push-r1.md | - | ada2adad570632154a505ac8ca9086b5b113cb54a31e4919709216dc02d407bf | SOURCE_PIN |
| PUSH-02 | push-gate/Review | G:/CODEX/New Manga/verification/GIT-CLEAN-PUBLICATION-1/antigravity-review-push-r1.md | - | 144d9761f90f257bef9686f435af59c398f305ad015760540c38c7fe5b9dc852 | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga | PRESERVE_REFERENCED | — | 固定源commit | 只写治理/本Task证据，不删除 |
| task-env | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-PUBLICATION-1 | PRESERVE_REFERENCED | — | 待生成 | 使用治理规定task-envs，取代早期方案的拟议task-env单数路径 |
| artifact | 上述task-env/source-export | PRESERVE_REFERENCED | — | 待生成manifest与独立commit | 独立Git仓库，非linked worktree；候选分支codex/clean-source-snapshot |
| dataset/model/test-material | 既有169个JPEG及其外层blob | PRESERVE_USER_DATA | — | 原审计禁止上传清单 | 只读取指纹，不复制素材，不删除 |
| temp/build | 上述task-env中的缓存/输出 | PRESERVE_REFERENCED | — | 待测试记录 | 不自动清理 |
| agent-output/exchange | — | NOT_APPLICABLE | — | — | 无派发或外部传输 |

## Rolling checkpoint

`verification/GIT-CLEAN-PUBLICATION-1/checkpoint.md`（创建后为当前恢复入口）。DSH r1 blocked、产品发布未批准；本Task完成本地候选也不自动授权push。


## 交付记录

2026-10-24：最终候选root `e34a90d001cce1fa966aec7d2b032bb5ad1cf148`，实际仓库 `G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-PUBLICATION-1/source-export-r4`，733个tracked文件；源main没有新commit。结果/Handoff为 `verification/GIT-CLEAN-PUBLICATION-1/RESULT.md`、`HANDOFF.md`。独立Review已完成且blocked，软件验证保留阻断；只进入in_review，不置done、不push。4个本地候选/缓存/隔离数据/review-package均PRESERVE_REFERENCED，资源closeout pending，不清理。

## DSH r1 处置（2026-10-24）

最新 Review：`verification/GIT-CLEAN-PUBLICATION-1/dsh-review-r1.md`，reviewed_head=e34a90d001cce1fa966aec7d2b032bb5ad1cf148，decision=blocked；Task 保持 in_review。Codex 另释 `doc/tasks/GIT-CLEAN-PUBLICATION-DIAG-1.md`，不改源 main、父候选或旧 Review。新补充冻结权威为 workspace/review-package-r2/PACKAGE_MANIFEST.json；旧 9 项 pins 全部保留。下表补充 SOURCE_PIN 包括仓内原始过程文件（仅作来源）、DB 冻结副本与补充包，解决双份口径；不得将 local-only 证据包当源码发布。

R-001 默认并发已复现 151 passed / 2 failed / 1 ignored / 12 filtered；四个 registry 测试各自单进程通过。测试共享污染成立，产品并发饱和风险未排除，父 AC4 仍 BLOCKED。R-002 三个 DB/plugin_error 已冻结；旧 icacls returncode/stderr UNKNOWN，新诊断补丁只在独立 head fed1a9c 生效并重新 Appointment，未集成。R-003/4 补齐指纹与缺失日志，R-005 旧日志采用明确标注的事后 envelope（缺环境信息仍 UNRECORDED），新日志即时记录实际 EXIT。R-006 明示 r2/r3 串行均 152 passed/1 failed/1 ignored/12 filtered、exit101，r4 才 153/0/1/12、exit0。详见诊断 RESULT；packaged 必须先冻结 sidecar 才能执行。父候选不变，当前不申请以新父 head 复审、不 push、不 done。

## DIAG r1 approved 后的父升级门槛

DSH在 `verification/GIT-CLEAN-PUBLICATION-DIAG-1/dsh-review-r1.md` 只批准诊断fed；本Task保持in_review、父r1 blocked、AC4 BLOCKED、AC5 PARTIAL，不改delivery_head=e34，不集成fed，不push、不done。

| 必补项 | Owner处置/证据 | 父升级Gate |
|---|---|---|
| DIAG Review R-01（非父R-001） | 六份早期运行器未冻结且缺tracked_changes；当前RESULT/追加manifest声明未知版本SHA与证据限制，不补造 | 新父Appointment Reviewer确认限制可接受或要求新变量证据前，不升级 |
| DIAG Review R-02 | DIAG-50→本表DB-41、DIAG-51→DB-42、DIAG-52→DB-43；三库SHA再经DIAG-53→本表SUP-38→旧包core-db条目覆盖；42项freeze不含DB | 交叉链必须随新父审查包提供，不因诊断批准省略 |
| DIAG Review R-03 | 首轮packaged-tests.json/log的head不可用于绑定；只用probe+fixed-head+postcheck绑定e34 | 禁止自动选首轮为canonical；升级后packaged证据不得从旧e34移植 |

交叉引用机器表、R-04–R-13说明及旧包指纹见 `G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-PUBLICATION-DIAG-1/review-disposition-r1/PACKAGE_MANIFEST.json`。原review-package-r2/PACKAGE_MANIFEST.json仍为SUP-38的原SHA，不原位扩写。包内三叙述文档是冻结时旧快照，当前披露由父目录与DIAG RESULT追加段给出。

Rust修复与压力验证已另冻READY；Core新环境V2–V5定义未给出，另登记proposed，不盲跑、不改ACL。任何父新head须重新Appointment（精确base/head、Owner/Reviewer、当前证据包/以上交叉链和唯一Review写路径），当前尚无新父head与新父Appointment，不沿用父blocked或诊断approved作为升级批准。

## 2026-10-25 DSH 接管与 push-gate Appointment

用户裁决由 DSH 接任 Lead / Architect / Integrator 并拥有最终 push 权限（见 `doc/GOVERNANCE_TAKEOVER_2026-10-25.md`）。本 Task 的 Owner/实现作者仍为 Codex；当前 Reviewer 改派 **Antigravity**，对固定候选 head `e34a90d001cce1fa966aec7d2b032bb5ad1cf148` 执行 **push-gate 独立审查**，只写 `verification/GIT-CLEAN-PUBLICATION-1/antigravity-review-push-r1.md`。此前 `dsh-review-r1.md` 的 blocked 结论保持原字节与历史效力，不因新 Appointment 改写。

审查性质：**不是产品发布验收**。该 head 是独立、无父提交、无 remote 的干净源码快照；本次审查只判断既定 push 条件是否满足：材料隔离/来源可追溯、构建与测试证据可复核且限制如实披露、目标 ref 未被占用、可安全普通 push 到 `origin` 新分支。产品发布 Gate（Core 环境 ACL 限制、Rust 容量饱和、安装包/签名/真实 GUI）仍不通过，AC4 保持 BLOCKED、AC5 保持 PARTIAL；不得把 blocked/失败证据改写为通过。

Push 边界：目标为 `origin` 新分支，不 push `main`、不设置上游、不 force、不覆盖远端 `main`；169 个私有 JPEG 及其 338 个禁止对象不得出现在推送对象中。审查通过后由 DSH 执行 push 并记录远端、目标分支、commit、命令与远端 SHA 核验；审查若 blocked，DSH 停止 push 并向用户给出具体可裁决问题。

### 源 main 基线口径（2026-10-25）

DSH 接管基线提交 `a3c936f68748047aee41c4c60d732adc5bdf55f7`（仅 `AGENTS.md`、协作协议、模板与本接管记录等 10 个治理/文档文件）使 `main` 从 `349e61faff5f93067af5d4ce2d9e394e0d665b8c` 前进 1 个 commit；`349e61f` 是其直接 parent 且仍为祖先，源码、验证证据与 338 禁止对象指纹零改动。本 Task 的 AC3「原 main/index 与 P04 指纹不变」按候选冻结时点与候选来源口径理解：候选固定源 commit 仍是 `349e61f`，接管治理提交不进入候选、不改变候选对象库；不把该治理提交改写为候选内容或产品变更，也不回退 `main`。`index` 在接管提交后为空（`git diff --cached` 无输出）。

## Push-gate 独立审查与执行记录（2026-10-25）

- **Appointment**：`verification/GIT-CLEAN-PUBLICATION-1/APPOINTMENT-push-r1.md`；Reviewer=Antigravity（非作者、非 DSH），固定 `base_commit=349e61faf`、`reviewed_head=e34a90d0`。
- **独立 Review**：`verification/GIT-CLEAN-PUBLICATION-1/antigravity-review-push-r1.md`，decision=**approved（仅 push-gate）**，0 P0 / 0 P1 / 2 P2 / 2 P3。F-001 交付介质限制与 F-002 产品级 Gate 未关闭均接受为边界；F-003/F-004 closed。旧 DSH r1 blocked 保留原字节与历史效力。
- **DSH 处置**：接受上述 push-gate approved；不把 AC4 BLOCKED、AC5 PARTIAL、Rust AC3 BLOCKED、产品发布 Gate 或父 Task 状态改写为通过；Task 保持 `in_review`，不置 done。
- **实际 push**：从候选独立仓执行普通 push，目标 `origin` 新分支，命令
  `git -C <source-export-r4> push --no-follow-tags https://github.com/peakwheat-pixel/New-Manga.git e34a90d001cce1fa966aec7d2b032bb5ad1cf148:refs/heads/codex/clean-source-snapshot`，exit 0。
- **远端核验**：`git ls-remote --heads origin` →
  `e34a90d001cce1fa966aec7d2b032bb5ad1cf148 refs/heads/codex/clean-source-snapshot`；
  `refs/heads/main` 保持 `6a68fdeb92d8a1c7903166a8076d6260bf8fa79a` 不变。未使用 force、未推送 `main`、未设置上游、未传播私有素材。
- **记录文件**：`doc/PUSH_RECORD_2026-10-25.md`。

## 2026-10-26 实际发布记录（DSH 执行，用户明确授权）

- **授权**：用户 2026-10-26 同意 push 裁决，并在「推 main / 推干净快照 / 先看清单」三选中明确选择 **只推干净源码快照**。
- **口径**：新建分支推送，**不动 `main`、不动既有 `codex/clean-source-snapshot`、不 force push**。
- **方法**：`git archive --format=tar --output=... main -- <白名单路径>` 导出 → 独立 `git init` + 单提交 → `git push origin HEAD:refs/heads/clean-snapshot-20261026`。
- **导出白名单**：`apps/` `src/` `tests/` `packaging/` `test_assets/` `pytest.ini` `requirements.txt` `requirements-dev.txt` `.gitignore` `.gitattributes` `tools/dev` `tools/p02` `tools/smoke`。
- **剔除**：`verification/`(9306 files) `doc/`(1158) `docs/` `audit/` `wiki/` `archive/` `experiments/` `.orchestrator/` `.codewiki/` `.codex/` `.dsh/` `.gemini/` `.qoder/` `.workbuddy/` `.qoder-credits/` `.tmp.driveupload/`(2148) `AGENTS.md` `GOAL.md` `tools/governance`。
- **快照内容**：875 个文件 / 15.3 MB；顶层 = apps(283) src(243) tests(226) test_assets(81) packaging(18) tools(14) + 5 个根配置文件。
- **推送结果**：`clean-snapshot-20261026` = `892b9469e2fc2fe494ff4c469d1e54e94dcef571`，`push exit=0`，7 秒；远端 `ls-remote` 回读一致。
- **推送前验证**（在快照目录内独立跑，非借用 main 的结论）：
  - `git ls-files` = 875
  - `tsc --noEmit` → **exit 0**
  - `vitest run` → **567 passed**
  - 禁区泄漏检查：`verification/doc/audit/wiki/archive/experiments/.orchestrator/.codex/.dsh/.gemini/.qoder/.workbuddy/.codewiki/.tmp.driveupload/AGENTS.md/GOAL.md/tools/governance` **全部不存在**
- **未公开内容确认**：远端 `main` 仍为 `6a68fdeb9`（1788 files），`codex/clean-source-snapshot` 仍为 `e34a90d00`，本地 `main`(14002 files 含全部治理材料) **未推送**。
- **构建快照本地副本**：`G:/CODEX/New Manga.workspace/publish/clean-snapshot-20261026`（可复现此分支）。
- **本卡 AC4/AC5 状态不受影响**：它描述的是「推 main 的发布 Gate」，本次走的是快照分支口径，不等于本卡通过。