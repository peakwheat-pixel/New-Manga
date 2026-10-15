---
id: P02-MAINLINE-INTEGRATION
title: P02 已审成果合入 main 与主线收口
kind: integration
governance_version: 2
status: done
approval: user_authorized_mainline_integration_20261015
owner: Codex
reviewer: DeepSeek Harness
integrator: Codex
depends_on: [P02-NEW-TIME-X6-AC1-AC7, RES-P02-AC6-CDP-RECOVERY]
base_commit: a9c3214b2d7806c2b8920897e5684c039ae14057
delivery_head: 9e3c5310d5652f5491f3dc11825d86c03dac22ee
reviewed_head: 738759cd3cbd2ca47177b95c64402b57c491ba40
review_decision: approved
integration_target: main
integration_commit: 9e3c5310d5652f5491f3dc11825d86c03dac22ee
integration_status: integrated
branch: main
worktree: G:/CODEX/New Manga
revisions: {implementation: 0, test: 0, evidence: 1}
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/P02-MAINLINE-INTEGRATION
---

# P02-MAINLINE-INTEGRATION

## 来源与冻结范围

用户 2026-10-15 明确授权 P02 已审成果合入 main 与主线收口。来源为 codex/p02-newtime-ac-integration-20261015 @ 9e3c5310；既有 DSH 内容 Review @ 4abb8d28 与 E Review @ 738759cd 均 APPROVED。Integrator 只核验固定交付与集成，沿用已有独立审查，不执行第二轮完整审计。

## Acceptance Criteria

- [x] 固定 9e3c5310 已审成果可从 main 到达；main 原 HEAD 为其祖先，只做快进合并。
- [x] 主 checkout 既有 dirty 内容与同名 untracked 副本逐路径保留；不提交用户内容，不 reset/clean/stash，不删除 worktree 或修理旧坏引用。
- [x] 在 main 对 102 项 source pins、19 项 Gate capsule 复验 PASS；原始运行数据、Review 与 I1/I2=2/2 不变。
- [x] 更新当前 Task/STATUS/Plan/索引与恢复点，P02 总入口按限定范围关闭；保留旧 H1/P2-1、13 项缺失、BC-AC5 PARTIAL 与产品 P3/P4，不宣称产品全面 PASS；治理检查通过。

## 允许修改范围

- Git 原生 fast-forward 将固定已审 tree 合入本地 main；只在确认 index 无用户暂存后，按目标 Git blob 对同名冲突路径做 index-only 对齐，工作文件不改，merge 后 index 恢复干净。
- doc/STATUS.md、doc/REBASELINE_PLAN.md、doc/tasks/README.md、doc/tasks/P02.md、doc/tasks/P02-NEW-TIME-X6-AC1-AC7.md、doc/tasks/RES-P02-AC6-CDP-RECOVERY.md、本 Task；verification/P02-MAINLINE-INTEGRATION/**；工作区 agent-output/codex/P02-MAINLINE-INTEGRATION/**。
- 主控状态使用 epoch=3 guarded-write；新文档只做集成治理收口，保留冻结 AC 和原始证据。

## 禁止范围

不改产品源码、测试行为、依赖/Schema/契约/构建脚本；不运行 GUI/Build/X6/模型；不修改历史 Review/manifests；不 push、不删除 refs、不运行 gc/prune、不清理未知资源。

## 测试与恢复

两组隔离 Git fixture 已断言：原生 FF merge 能在 index-only 对齐已审 blob 后保留 dirty/untracked 同名内容，且最终无用户内容暂存。实际执行前保存 index 与逐文件保护快照；真实 merge 后按字节核验。原始命令/退出码/核验写入 Task evidence；失败先保留和恢复本轮 index-only 对齐，不动用户文件。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| MAIN-01 | Mainline / preservation / pins | verification/P02-MAINLINE-INTEGRATION/result/canonical-eol-materialization.json | - | d9b3e0769ff64c5b36cf953bbf388d29ea1f4a4ce5a87638ebd57892ca755659 | SOURCE_PIN |
| MAIN-02 | Mainline / preservation / pins | verification/P02-MAINLINE-INTEGRATION/result/fast-forward-preservation.json | - | 6ee11e093894394df3b1238db8bdf00a4a5bfb057b6071f3443c1274633b8f36 | SOURCE_PIN |
| MAIN-03 | Mainline / preservation / pins | verification/P02-MAINLINE-INTEGRATION/result/gate-pins-on-main.json | - | c3eeacb0fc6f682613c5240feaf22c8aba6bb9b720bfd965865d3b55e65b24bc | CANONICAL |
| MAIN-04 | Mainline / preservation / pins | verification/P02-MAINLINE-INTEGRATION/result/git-eol-initial-verify.json | - | bb9729ef0c10415f7e31dc77189e80b63c9ed712ccc1fa38ae37aa622ad7b328 | SOURCE_PIN |
| MAIN-05 | Mainline / preservation / pins | verification/P02-MAINLINE-INTEGRATION/result/mainline-report.md | - | 3987e1a27e87be26b24b37b7719df6b8b3182d660ad1666d9b60eb4381d3a5f1 | CANONICAL |
| MAIN-06 | Mainline / preservation / pins | verification/P02-MAINLINE-INTEGRATION/result/resource-retention.json | - | 5ba9de149b80c434102440f5a33f5bba6c9ad2d5b180f574f615ebcb0dbe3ca1 | SOURCE_PIN |
| MAIN-07 | Mainline / preservation / pins | verification/P02-MAINLINE-INTEGRATION/result/result-input.json | - | 023e9243c275e5cdcc8150b4a420bef95ffbdd0c6e8279668b0303f5b43ed784 | SOURCE_PIN |
| MAIN-08 | Mainline / preservation / pins | verification/P02-MAINLINE-INTEGRATION/result/result-output.json | - | c2c7473f861644e569092465fc799e25fb9c7365a85e57851823de589f4e50df | SOURCE_PIN |
| MAIN-09 | Mainline / preservation / pins | verification/P02-MAINLINE-INTEGRATION/result/revision-input.json | - | 1c62e3de0894f71eea865c07a6dfad9196b6d9fcf2bc978189a9ab2c53e7f898 | SOURCE_PIN |
| MAIN-10 | Mainline / preservation / pins | verification/P02-MAINLINE-INTEGRATION/result/revision-output.json | - | 7d40facc2c0fc94e7cc3d65c5afd2ca3fa4814c9f691877d0be4268d59389f6a | SOURCE_PIN |
| MAIN-11 | Mainline / preservation / pins | verification/P02-MAINLINE-INTEGRATION/result/source-pins-on-main.json | - | b59f3556f91be12be61dbeb9f44fc0bfec59d8348ba60b2610d6a1c384782e99 | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| primary_worktree | G:/CODEX/New Manga | PRESERVE_USER_DATA | G:/CODEX/New Manga | verification/P02-MAINLINE-INTEGRATION/result/resource-retention.json | 既有 dirty/untracked 未提交到 main；FF 保护 38 文件字节，index empty |
| reviewed_integration_and_closeout_worktree | G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-AC1-AC7-INTEGRATION | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-AC1-AC7-INTEGRATION | verification/P02-MAINLINE-INTEGRATION/result/resource-retention.json | 已审内容和 mainline closeout 候选；原 reviewed branch ref 保留 9e3c5310，当前工作分支 codex/p02-mainline-closeout-20261015 |
| backup_and_raw_output | G:/CODEX/New Manga.workspace/agent-output/codex/P02-MAINLINE-INTEGRATION | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/agent-output/codex/P02-MAINLINE-INTEGRATION | verification/P02-MAINLINE-INTEGRATION/result/resource-retention.json | index-before.bin、38 文件备份、UTF-8 dry-run、原生 merge 日志与换行前态原位保留 |
| git_fixture_selfchecks | G:/CODEX/New Manga.workspace/temp/P02-MAINLINE-INTEGRATION | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/temp/P02-MAINLINE-INTEGRATION | verification/P02-MAINLINE-INTEGRATION/result/resource-retention.json | 两组 assert selfcheck PASS，未删除 fixture |
| prior_task_envs_and_artifacts | G:/CODEX/New Manga.workspace/task-envs/P02-NEW-TIME-X6-AC1-AC7 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/P02-NEW-TIME-X6-AC1-AC7 | verification/P02-MAINLINE-INTEGRATION/result/resource-retention.json | 此前 7 类保留资源 manifest 继续有效；本轮无 GUI/模型/Build 使用或清理 |
| legacy_P02_worktree | G:/CODEX/New Manga.worktrees/P02-real-webview-harness-antigravity | PRESERVE_UNKNOWN | G:/CODEX/New Manga.worktrees/P02-real-webview-harness-antigravity | verification/P02-MAINLINE-INTEGRATION/result/resource-retention.json | 历史 P02 载体；未递归核实所有权/独有内容，因此原位保留，不删除或复用 |

## Closeout Record

- 2026-10-15 / Codex epoch 3；main 已原生 FF 到 9e3c5310，沿用独立审查，不重置既有 I1/I2=2/2。
- main source pins 102/102 PASS、Gate capsule 19/19 PASS；7 项 Git 新写出文本仅恢复已审 EOL，原 manifest/user bytes 不变。
- 用户内容：38/38 文件保护检查 PASS；untracked 保留；无用户内容暂存或提交；此前与当前资源全部保留，删除/迁移/归档 0。
- canonical_evidence_status / resource_closeout_status：complete / complete。
- Task/STATUS/Plan/索引与两个 DONE 子 Task canonical pointers 主线化；P02 历史总入口 closed_with_limitations，仅关闭本次授权路径，不把旧 H1、P2-1、BC-AC5 PARTIAL 或产品缺口升级为 PASS。
- 本轮新文档为 E/governance-only，官方 classify reviewer_needed=false；官方 result=ACCEPT。正式 mainline Closeout 文档与该 evidence 将由相同保护流程追加 FF 到 main；最终 head 见 STATUS/rolling checkpoint。
- 后续：无其它已释放 READY；无需下一步操作。
