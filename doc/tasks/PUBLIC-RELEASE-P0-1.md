---
id: PUBLIC-RELEASE-P0-1
title: P0 公开仓库整改（许可/README/产品源码树/CI 草案）与公开 release 分支推送
kind: release
governance_version: 3
status: ready
approval: user_authorized_2026-10-28_p0_execution
suggested_owner: dsh-lead
owner: dsh-lead
reviewer: region-workbench-owner
depends_on: [SIGNPATH-OSS-SIGNING-1]
base_commit: e8147c6c8a7edde4e5784999454acb5732a869fb
branch: task/PUBLIC-RELEASE-P0-1
worktree: G:/CODEX/New Manga.workspace/worktrees/PUBLIC-RELEASE-P0-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
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

- 来源：用户 2026-10-28 选择执行 [SIGNPATH-APPLICATION-CHECKLIST](../release/SIGNPATH-APPLICATION-CHECKLIST.md) 的 **P0**（公开仓库申请前整改），以解除 SignPath 申请的硬阻塞。
- 目标（P0-1 ~ P0-5）：
  1. P0-1/P0-2：在公开 release 分支根目录加入 `LICENSE`、`LICENSE-AGPL-3.0.txt`、`NOTICE.md`、`THIRD_PARTY_LICENSES.md`、`README.md`。
  2. P0-3：把当前产品源码树（基于已公开的 `clean-snapshot-20261026` 树：`apps/ packaging/ src/ tests/ tools/`）推为公开 release 分支 `public-release`，不覆盖远端 `main`、不 force。
  3. P0-4：分支内包含 `.github/workflows/build-release.yml`（CI 草案）；**workflow_dispatch 的 Run 需要 GitHub API 权限，本机 `gh` 未登录/无 token，由用户网页触发**（不得伪造运行结果）。
  4. P0-5：推送前复核算入内容不含模型权重/密钥/私有素材/历史敏感材料。
- 明确边界：不修改远端 `main`；不 force-push；不推本地 main 完整历史（含旧壳/私有材料）；不代持 GitHub token；不伪造 CI 运行结果。

## Acceptance Criteria

- [ ] **AC1 公开分支内容**：新分支根目录含许可四件套 + `README.md`（来自 main 已审核版本）+ `.github/workflows/build-release.yml`；产品树来自 `clean-snapshot-20261026`（公开历史）；文件清单与来源可追溯（`git ls-tree` 证据）。
- [ ] **AC2 推送**：`git push origin <branch>` 成功；远端引用可见（`git ls-remote` 证据）；远端 `main` SHA 不变（`6a68fdeb…`）；未 force、未推本地 main。
- [ ] **AC3 内容安全**：推送内容经 `git ls-files` 复核：无 `.onnx`/模型权重、`.pfx`/`.pem`/密钥、`.env`、task-env 路径、私有素材；仓库体积/文件数记录。
- [ ] **AC4 CI 与默认分支**：workflow 文件存在于推送分支且 YAML 可解析；**如实记录** `gh` 未认证、无法由 Agent 触发 workflow_dispatch 或切换默认分支，给出用户两步操作（设默认分支、网页 Run `sign=false`）。
- [ ] **AC5 门禁与证据**：`check.ps1 -TaskPath` PASS；证据（推送日志、ls-remote、ls-tree、安全检查、YAML 解析）64-hex pin；Handoff。

## 允许修改范围

本卡、STATUS/PLAN/LEDGER、`verification/PUBLIC-RELEASE-P0-1/**`、自己的 Handoff、worktree 与 task-env；**提交内容仅限**根目录许可四件套、`README.md`、`.github/workflows/**`（其余树来自公开快照分支，不增删）。

## 禁止范围

不改产品源码/契约；**不覆盖远端 main、不 force-push、不推本地 main 历史、不 push 私有材料**；不代持 token；不伪造 CI 结果；不删除公开仓库现有分支。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1/AC2 | `git ls-tree` + `git push origin HEAD:refs/heads/public-release` + `git ls-remote` | 本机 git 凭据（GCM） | NOT_RUN | planned |
| AC3 | `git ls-files` 模式扫描 + 体积统计 | worktree | NOT_RUN | planned |
| AC4 | `yaml.safe_load` + `gh auth status`（预期未登录） | 本机 | NOT_RUN | planned |
| AC5 | `check.ps1 -TaskPath` | 仓库 | NOT_RUN | planned |

## 依赖、风险与阻塞

- 硬依赖：`SIGNPATH-OSS-SIGNING-1`（done，材料已集成）。
- 风险：①公开推送不可逆（新分支可删除，但对象可能仍可见），推送前 P0-5 复核必须完成；②`gh` 未登录 → 默认分支切换与 workflow Run 必须用户操作（或提供 token 后由 Agent 重试）；③GitHub 网页设置的默认分支变更不影响远端 main 历史，可逆；④公开 CI 首次 Run 仍可能失败（本地无 runner 等价环境），失败按真实结果记录并迭代。
- 阻塞解除：用户完成"设默认分支 + 网页 Run（sign=false）"或提供 GH_TOKEN。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无。
- 实际测试：尚无。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/PUBLIC-RELEASE-P0-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/PUBLIC-RELEASE-P0-1 | verification/PUBLIC-RELEASE-P0-1/push.json | 推送后保留至集成；未覆盖 main |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：交付时更新 STATUS/PLAN/LEDGER。
