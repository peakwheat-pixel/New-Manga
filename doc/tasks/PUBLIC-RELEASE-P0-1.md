---
id: PUBLIC-RELEASE-P0-1
title: P0 公开仓库整改（许可/README/产品源码树/CI 草案）与公开 release 分支推送
kind: release
governance_version: 3
status: in_review
approval: user_authorized_2026-10-28_p0_execution
suggested_owner: dsh-lead
owner: dsh-lead
reviewer: region-workbench-owner
depends_on: [SIGNPATH-OSS-SIGNING-1]
base_commit: e8147c6c8a7edde4e5784999454acb5732a869fb
branch: task/PUBLIC-RELEASE-P0-1
worktree: G:/CODEX/New Manga.workspace/worktrees/PUBLIC-RELEASE-P0-1
integration_commit: null
delivery_head: 53481a9d9214d1c44434711fccfb2fb52f27792d
canonical_evidence_status: complete
resource_closeout_status: pending
evidence_dir: verification/PUBLIC-RELEASE-P0-1
allowed_paths:
  - doc/tasks/PUBLIC-RELEASE-P0-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/release/**
  - README.md
  - .github/workflows/**
  - verification/PUBLIC-RELEASE-P0-1/**
  - G:/CODEX/New Manga.workspace/task-envs/PUBLIC-RELEASE-P0-1/**
  - G:/CODEX/New Manga.workspace/worktrees/PUBLIC-RELEASE-P0-1/**
---

# PUBLIC-RELEASE-P0-1：P0 公开仓库整改与公开 release 分支推送

## 来源与目标

- 来源：用户 2026-10-28 选择执行 [SIGNPATH-APPLICATION-CHECKLIST](../release/SIGNPATH-APPLICATION-CHECKLIST.md) 的 **P0**。
- 已执行（真实推送）：公开树推送到 GitHub 新分支 `public-release` = `3207e9c18726c62a2692cf7c5d89fb85ea9fabec`；**未改远端 `main`、未 force、未推本地 main 历史**。
- 公开树组成：公开快照 `clean-snapshot-20261026`（e8147c6c8）+ 同步 `apps/desktop-avalonia`（151 文件）+ `packaging/release` + `packaging/nsis` + `doc/release` 两材料 + 根许可四件套 + README.md + `.github/workflows/build-release.yml`；不含 bin/obj/node_modules。
- 明确边界：不修改远端 `main`；不 force；不代持 token；不伪造 CI/签名结果。

## Acceptance Criteria

- [x] **AC1 公开分支内容**：分支根目录含许可四件套 + README + workflow；产品树来自公开快照 + `apps/desktop-avalonia` 同步；文件清单与来源可追溯（`ls-tree.txt` 1040 行原始输出）。<<MET>>
- [x] **AC2 推送**：`git push origin HEAD:refs/heads/public-release` 成功（`[new branch]`，无 force）；远端 `public-release` SHA = `3207e9c18…`；远端 `main` 保持 `6a68fdeb…`；`clean-snapshot-20261026`/`codex/clean-source-snapshot` 未动（`ls-remote.txt` 原始输出）。<<MET>>
- [x] **AC3 内容安全**：推送树 1040 文件 / 17,539,433 B（16.73 MiB）；禁止扩展名 0；密钥模式原始命中 2（均为 `tests/network/test_transport_local.py` 测试 fixture，真实凭据 0）；无私有文件/模型/用户数据；开发机路径字符串 107 行/41 文件（本次新增 61 行/28 文件）已登记为非敏感 follow-up 清理（修正后口径，见 `security-scan.json`）。<<MET>>
- [x] **AC4 CI 与默认分支（含用户动作）**：workflow 存在于 `public-release` 且 YAML 可解析（12 steps，raw 200）；**如实记录**首次 workflow_dispatch Run 与默认分支切换需用户操作：（1）Settings → Branches → 默认分支改为 `public-release`；（2）Actions → `build-release` → Run（`sign=false`）。本机 `gh` 未认证、无 `GH_TOKEN`，未伪造 Run。 <<PARTIAL: CI Run 与默认分支切换待用户两步（本机无 GitHub API 权限）>>
- [x] **AC5 门禁与证据**：`check.ps1 -TaskPath` PASS；6 文件证据 64-hex pin；Handoff。<<MET>>

## 允许修改范围

本卡、STATUS/PLAN/LEDGER、`verification/PUBLIC-RELEASE-P0-1/**`、自己的 Handoff、worktree 与 task-env。

## 禁止范围

不改产品源码/契约；**不覆盖远端 main、不 force-push、不推本地 main 历史**；不代持 token；不伪造 CI 结果；不删除公开仓库现有分支。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1/AC2 | `git ls-tree -r -l 3207e9c18` + `git push` + `git ls-remote` | 本机 git 凭据（GCM） | **PASS**：1040 文件；push `[new branch]`；远端 SHA 一致；main 未变 | `ls-tree.txt`、`ls-remote.txt`、`push.json` |
| AC3 | 全树扩展名/密钥/路径扫描（排除 .git） | worktree | **PASS（修正）**：禁扩展名 0；密钥原始 2/真实 0；路径 107 行/41 文件已登记 | `security-scan.json` |
| AC4 | raw 检查 + `yaml.safe_load` + `gh auth status` | 网络只读/本机 | **PARTIAL**：remote 200、YAML OK；CI Run/默认分支需用户（gh 未登录） | `remote-verify.json`、`REPORT.md` |
| AC5 | `check.ps1 -TaskPath` | 仓库 | PASS（2 warnings） | 本卡 |

## 依赖、风险与阻塞

- 硬依赖：`SIGNPATH-OSS-SIGNING-1`（done）。
- 风险：①公开推送不可逆（分支可删，但对象可能保留）；推送前已完成扫描（无真实凭据/模型/私有文件）；②`gh` 未登录 → 默认分支切换与首次 Run 需用户两步；③首次 Run 可能失败（本地/runner 差异），失败属预期迭代；④开发机路径字符串（107 行/41 文件）为非敏感 follow-up 清理（本卡 allowed_paths 不含那些既有脚本）。
- 阻塞解除：用户完成两步后，由本卡或后续 Task 复验并更新状态。

## 交付与运行记录

- Handoff：[PUBLIC-RELEASE-P0-1-handoff.md](../handoffs/PUBLIC-RELEASE-P0-1-handoff.md)
- Review：独立复核 **CHANGES_REQUESTED（P0=0；2 P1 + 6 P2）→ 已修复 P1-1/P1-2/P2-1/P2-2/P2-4/P2-5**；待 Reviewer 复核修复后给 PASS。
- 推送事实：`public-release` = `3207e9c18`（远端与本地一致）；远端 `main` 未变。
- delivery_head：`53481a9d9214d1c44434711fccfb2fb52f27792d`（证据提交；main 上的证据 commit，worktree 证据 commit 为 `1b456fb0d` 但无共同祖先，不予导入历史）。
- 未 push 本地 main；未运行 CI；未签名。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| push | AC2 | verification/PUBLIC-RELEASE-P0-1/push.json | 53481a9d9214d1c44434711fccfb2fb52f27792d | de13772af7e6d96251bfd368c09a85c4f14538ca7a8074650cf1bad4d0cefbd7 | CANONICAL |
| remote-verify | AC2/AC4 | verification/PUBLIC-RELEASE-P0-1/remote-verify.json | 53481a9d9214d1c44434711fccfb2fb52f27792d | 03dda2cfb5c80fa9b6e629e45a69c62af2d46b577645360f340d94d266264ed0 | CANONICAL |
| security-scan | AC3 | verification/PUBLIC-RELEASE-P0-1/security-scan.json | 53481a9d9214d1c44434711fccfb2fb52f27792d | 3259e79e32829f95c8579cabbba128749dac96edd0477b3735588b6e3cd61833 | CANONICAL |
| report | AC1–AC5 | verification/PUBLIC-RELEASE-P0-1/REPORT.md | 53481a9d9214d1c44434711fccfb2fb52f27792d | be93eef2198841382db47d71f4ddde075207149509ed166e7add07bf5c36b62b | CANONICAL |
| ls-tree-raw | AC1 | verification/PUBLIC-RELEASE-P0-1/ls-tree.txt | 53481a9d9214d1c44434711fccfb2fb52f27792d | 5888441db73ad8f9a5745f525ccec2056430d4ad883208bac6074a6a1d8e9ee8 | CANONICAL |
| ls-remote-raw | AC2 | verification/PUBLIC-RELEASE-P0-1/ls-remote.txt | 53481a9d9214d1c44434711fccfb2fb52f27792d | 05087f9230f3989e44ef0630cc605e3d3215cb6a09e2fa011117e6202a470461 | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/PUBLIC-RELEASE-P0-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/PUBLIC-RELEASE-P0-1 | verification/PUBLIC-RELEASE-P0-1/push.json | 推送分支源；与 main 无共同祖先，仅证据已复制入 main；不导入其快照历史 |

## Closeout Record

- Closeout date / DSH：待 Reviewer 复核修复后填写。
- canonical_evidence_status：`complete`（6 项 64-hex pin）。
- resource_closeout_status：`pending`（worktree 保留；证据已导入 main）。
- 删除、迁移、归档数量/字节数：0。
- 未关闭项及保留原因：默认分支切换与首次 CI Run 需用户 2 步（gh 未认证）；开发机路径字符串清理为 follow-up（P1-1 登记）。
- 当前指针清理：交付时更新 STATUS/PLAN/LEDGER。
