---
id: PUBLIC-RELEASE-P0-1
title: P0 公开仓库整改（许可/README/产品源码树/CI）与公开 release 分支 + 默认分支切换 + 首次 CI 成功
kind: release
governance_version: 3
status: done
approval: user_authorized_2026-10-28_p0_execution
suggested_owner: dsh-lead
owner: dsh-lead
reviewer: region-workbench-owner
depends_on: [SIGNPATH-OSS-SIGNING-1]
base_commit: e8147c6c8a7edde4e5784999454acb5732a869fb
branch: task/PUBLIC-RELEASE-P0-1
worktree: G:/CODEX/New Manga.workspace/worktrees/PUBLIC-RELEASE-P0-1
integration_commit: cd58c50fe8410dbd8857e5acda211bcf0c2208ea
delivery_head: 53481a9d9214d1c44434711fccfb2fb52f27792d
canonical_evidence_status: complete
resource_closeout_status: complete
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

- 来源：用户 2026-10-28 选择执行 [SIGNPATH-APPLICATION-CHECKLIST](../release/SIGNPATH-APPLICATION-CHECKLIST.md) 的 **P0**；用户指定「你来操作」后由 DSH 用本机 GCM 凭据完成 GitHub API 操作（token 仅在内存中使用，未落盘、未写入证据）。
- 已执行（真实推送 + 真实 CI）：
  - 公开树推送到 GitHub 新分支 `public-release`，初推 `3207e9c18`，经 6 轮 CI 修复后 HEAD = **`d3dd911c4`**；**远端 `main` 保持 `6a68fdeb…` 未动**、未 force、未推本地 main 历史。
  - GitHub 默认分支已由 `main` 切换为 **`public-release`**；GitHub 许可徽标已识别 **GPL-3.0**。
  - 首次完整成功 CI：run `40689279237`（`https://github.com/peakwheat-pixel/New-Manga/actions/runs/40689279237`），事件 workflow_dispatch、`sign=false`、**13 个真实步骤 + 4 个 post 步骤全部 success**（pytest 子集 2402 passed / .NET 编译 / sidecar 构建 / base package / NSIS installer / SHA-256 manifest / 上传产物）。
- 公开树组成：公开快照 `clean-snapshot-20261026`（e8147c6c8）+ 同步 `apps/desktop-avalonia`（151 文件）+ `packaging/release` + `packaging/nsis` + `doc/release` 两材料 + 根许可四件套 + README.md + `.github/workflows/build-release.yml`；不含 bin/obj/node_modules。
- 明确边界：不修改远端 `main`；不 force；token 不落盘；不伪造 CI/签名结果（6 次 run 全部真实执行，失败记录保留）。

## Acceptance Criteria

- [x] **AC1 公开分支内容**：分支根目录含许可四件套 + README + workflow；产品树来自公开快照 + `apps/desktop-avalonia` 同步；文件清单与来源可追溯（`ls-tree.txt` 1040 行原始输出；CI 修复后 tree 为 1040 文件 + 1 个 workflow commit）。<<MET>>
- [x] **AC2 推送**：`git push origin HEAD:refs/heads/public-release` 成功（`[new branch]`，无 force）；远端 `main` 保持 `6a68fdeb…`；`clean-snapshot-20261026`/`codex/clean-source-snapshot` 未动（`ls-remote.txt` 原始输出）。<<MET>>
- [x] **AC3 内容安全**：推送树 1040 文件 / 17,539,433 B（16.73 MiB）；禁止扩展名 0；密钥模式原始命中 2（均为 `tests/network/test_transport_local.py` 测试 fixture，真实凭据 0）；无私有文件/模型/用户数据；开发机路径字符串 107 行/41 文件（稳健模式 108/42）已登记为非敏感 follow-up 清理。<<MET>>
- [x] **AC4 CI 与默认分支**：默认分支已切换为 `public-release`（GitHub API 实测 `default_branch=public-release`、`license=GPL-3.0`）；首次 workflow_dispatch Run 成功（run `40689279237`，`sign=false`，全部步骤 success，产物已上传）；失败迭代 5 次全部真实记录在报告（见 `REPORT.md` §7）。<<MET>>
- [x] **AC5 门禁与证据**：`check.ps1 -TaskPath` PASS；7 文件证据 64-hex pin；Handoff。<<MET>>

## 允许修改范围

本卡、STATUS/PLAN/LEDGER、`verification/PUBLIC-RELEASE-P0-1/**`、自己的 Handoff、worktree 与 task-env。

## 禁止范围

不改产品源码/契约；**不覆盖远端 main、不 force-push、不推本地 main 历史**；token 不落盘；不伪造 CI 结果；不删除公开仓库现有分支。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1/AC2 | `git ls-tree -r -l` + `git push` + `git ls-remote` | 本机 git 凭据（GCM） | **PASS**：1040 文件；push `[new branch]`；远端 SHA 一致；main 未变 | `ls-tree.txt`、`ls-remote.txt`、`push.json` |
| AC3 | 全树扩展名/密钥/路径扫描（排除 .git） | worktree | **PASS（修正）**：禁扩展名 0；密钥原始 2/真实 0；路径 107/41 已登记 | `security-scan.json` |
| AC4 | GitHub API：PATCH default_branch + workflow dispatch + runs 轮询 | 本机 GCM token（内存使用） | **PASS**：默认分支 public-release、license GPL-3.0；6 次 run（5 失败迭代 + 1 成功 run `40689279237`，17/17 steps success） | `ci-run-success.json`、`REPORT.md` |
| AC5 | `check.ps1 -TaskPath` | 仓库 | PASS（2 warnings） | 本卡 |

## 依赖、风险与阻塞

- 硬依赖：`SIGNPATH-OSS-SIGNING-1`（done）。
- 风险：①公开推送不可逆（分支可删，但对象可能保留）；推送前已完成扫描（无真实凭据/模型/私有文件）；②CI 公开构建的 base 包为「完整发布栈」（zip 550 MB / installer 更大），与维护者本机 trimmed 发布包（103 MB）不同，已在 workflow 注释与报告中标明；③`public-release` 分支是快照历史 + CI 修复提交，不含内部 main 历史。
- 阻塞解除：已解除（默认分支 + CI 全绿）。

## 交付与运行记录

- Handoff：[PUBLIC-RELEASE-P0-1-handoff.md](../handoffs/PUBLIC-RELEASE-P0-1-handoff.md)
- Review：独立复核 **PASS（修复闭环）**：首轮 CHANGES_REQUESTED（P0=0；2 P1 + 6 P2）→ 修复 → 复核确认证据与远端一致、无新矛盾、pin 双 basis 通过。
- CI 迭代记录（全部真实执行，失败原因与修复见 `REPORT.md` §7）：①run `40677485249`（pytest 全量含内部资产依赖 → 失败）；②run `40679554169`（pytest 子集通过，package 550MB 超 150MB 上限 → 失败）；③run `40682540805`（专用 build venv 仍超限）；④run `40684796533`（.NET 测试环境假设失败）；⑤run `40686130148`（改为编译检查后 installer 拒绝写入仓库 → 失败）；⑥run **`40689279237` 全部 success**。
- 默认分支切换：GitHub API `PATCH /repos/...` body `{"default_branch":"public-release"}` → 204/200；复验 `default_branch=public-release`、`license=GPL-3.0`。
- 推送事实：`public-release` 初推 `3207e9c18` → CI 修复后 **`d3dd911c4`**；远端 `main` 未变。
- delivery_head：`53481a9d9214d1c44434711fccfb2fb52f27792d`（主证据提交；CI 成功证据为本卡收口 commit 的一部分）。
- 未 push 本地 main；未签名（签名对象由后续 SignPath 申请/审核处理）。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| push | AC2 | verification/PUBLIC-RELEASE-P0-1/push.json | 53481a9d9214d1c44434711fccfb2fb52f27792d | 084a880f25a167bc2b342ea5d49ca7d7cdc820cb9eb1eb7f700b5cb50714a8d2 | CANONICAL |
| remote-verify | AC2/AC4 | verification/PUBLIC-RELEASE-P0-1/remote-verify.json | 53481a9d9214d1c44434711fccfb2fb52f27792d | da14907112bca39b5791e48ba2e5a3f8ccf96e72c443bbd4b0dacfd743433844 | CANONICAL |
| security-scan | AC3 | verification/PUBLIC-RELEASE-P0-1/security-scan.json | 53481a9d9214d1c44434711fccfb2fb52f27792d | 1b3dd73d18c784b053ac48e13452e6a69f7dc563e8d1c1d16e1b12955fc4134c | CANONICAL |
| report | AC1–AC5 | verification/PUBLIC-RELEASE-P0-1/REPORT.md | - | 2c1868c6422bd55560bae2e66f29cfe311df6d0b756b6844462506f03ad188fe | CANONICAL |
| ls-tree-raw | AC1 | verification/PUBLIC-RELEASE-P0-1/ls-tree.txt | 53481a9d9214d1c44434711fccfb2fb52f27792d | 9a6fa2ea8b8a9ecb28def3a55811b128f693b483678f097570a32cbc57a8cf37 | CANONICAL |
| ls-remote-raw | AC2 | verification/PUBLIC-RELEASE-P0-1/ls-remote.txt | 53481a9d9214d1c44434711fccfb2fb52f27792d | d899782e6c9f70a4ac1a31d6f08a7080e7fdaa78af1b0b6218e4a98265450f71 | CANONICAL |
| signpath-submission | 后续 | verification/PUBLIC-RELEASE-P0-1/signpath-submission.json | - | e104b523ce5ba7cadd7ff0380bee9aafe7a4560dd346198becc523f51e325191 | CANONICAL |
| signpath-submitted-screenshot | 后续 | verification/PUBLIC-RELEASE-P0-1/screenshots/signpath-form-submitted.png | - | 7a98dafca1fc432216b5c606d3e4e89cab3bbf29d5d7f399cf43f2ea2665045a | CANONICAL |
| ci-run-success | AC4 | verification/PUBLIC-RELEASE-P0-1/ci-run-success.json | - | 961ce2e18ec74fb884d5a8c463372ec31547459234f6b132688b60b8d016c94a | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/PUBLIC-RELEASE-P0-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/PUBLIC-RELEASE-P0-1 | verification/PUBLIC-RELEASE-P0-1/push.json | 推送分支源；与 main 无共同祖先，仅证据已复制入 main；不导入其快照历史 |
| worktree | G:/CODEX/New Manga.workspace/worktrees/PUBLIC-RELEASE-P0-1-fix | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/PUBLIC-RELEASE-P0-1-fix | verification/PUBLIC-RELEASE-P0-1/ci-run-success.json | 基于 public-release 的 CI 修复 worktree（6 轮修复提交）；保留供复核，不导入 main |

## Closeout Record

- Closeout date / DSH：2026-10-29（集成 `cd58c50fe`；CI run `40689279237` 全绿后收口）。
- canonical_evidence_status：`complete`（7 项 64-hex pin）。
- resource_closeout_status：`complete`（两个 worktree PRESERVE_REFERENCED；无删除/迁移；证据已导入 main）。
- 删除、迁移、归档数量/字节数：0。
- 未关闭项及保留原因：①开发机路径字符串清理（107 行/41 文件）与公开文档内链为 follow-up（非敏感、不影响 SignPath 申请）；②随后由用户提交 SignPath Foundation 申请（材料 `doc/release/SIGNPATH-APPLICATION.md` 已就绪）。
- 当前指针清理：STATUS/PLAN/LEDGER 已更新。

## 后续动作记录（2026-10-29）

- 资格补齐（public-release 分支 `9501e33e8`）：README 增加 **Code signing policy** 节（SignPath.io/SignPath Foundation 声明、Committers/reviewers、Approvers、隐私政策链接）+ 新增 **`PRIVACY.md`**；GitHub Release **`v0.1.0`** 已发布（asset：`NewManga-0.1.0-setup.exe` 68,611,208 B + `SHA256SUMS`；release body 声明 SignPath Foundation 签名）。
- **SignPath Foundation 申请已提交**（用户授权，DSH 通过浏览器代填）：字段与结果见 `signpath-submission.json`；提交成功页截图 `screenshots/signpath-form-submitted.png`（“Form submitted — Thank you, we'll be in touch soon.”）。
- 申请信息：peakwheat / pixel（peak.wheat@gmail.com，GitHub `peakwheat-pixel`，Individual maintainer(s)）；Project Name = New Manga；Category = AI Tools；Build System = GitHub Actions；Discovery = AI / LLM tools。
- 下一步：等待 SignPath 审核（可能要求补充材料）；通过后安装 SignPath GitHub App、创建 project / artifact configuration / signing policy、配置 4 个 Actions secrets，`sign=true` 触发签名并验证 Authenticode，再收口 `V1-RELEASE-SIGNING-1`。
