---
id: SIGNPATH-OSS-SIGNING-1
title: SignPath Foundation 免费 OSS 代码签名申请材料（英文草案 + 前置清单 + CI 草案）
kind: planning
governance_version: 3
status: in_review
approval: user_authorized_2026-10-28_signpath_draft
suggested_owner: dsh-lead
owner: dsh-lead
reviewer: region-workbench-owner
depends_on: [RELEASE-VERIFY-1, V1-RELEASE-SIGNING-1]
base_commit: 8fcba8a89632502754acfdda61803c3398fcd2f2
branch: task/SIGNPATH-OSS-SIGNING-1
worktree: G:/CODEX/New Manga.workspace/worktrees/SIGNPATH-OSS-SIGNING-1
integration_commit: null
delivery_head: 340867cd807f900e28c831c38f29168c93f5c1b5
canonical_evidence_status: complete
resource_closeout_status: pending
evidence_dir: verification/SIGNPATH-OSS-SIGNING-1
allowed_paths:
  - doc/tasks/SIGNPATH-OSS-SIGNING-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/release/**
  - README.md
  - .github/workflows/**
  - verification/SIGNPATH-OSS-SIGNING-1/**
  - G:/CODEX/New Manga.workspace/task-envs/SIGNPATH-OSS-SIGNING-1/**
  - G:/CODEX/New Manga.workspace/worktrees/SIGNPATH-OSS-SIGNING-1/**
---

# SIGNPATH-OSS-SIGNING-1：SignPath Foundation 免费 OSS 签名申请材料

## 来源与目标

- 来源：用户 2026-10-28 明确「没有证书，买不起」，随后选择方案 A：**起草 SignPath Foundation 免费 OSS 代码签名申请材料**。本卡只产出材料与整改前置，不提交真实申请、不签名、不 push。
- 2026-10-28 事实核对（DSH 只读核实，详见 `verification/SIGNPATH-OSS-SIGNING-1/facts.json`）：
  - GitHub 公开仓库：`https://github.com/peakwheat-pixel/New-Manga`（`private=false`、`fork=false`、`default_branch=main`、`size≈28 MB`、`pushed_at=2026-10-26`）。
  - **默认分支 `main` 为旧内容**（`src/tests/doc/verification/wiki`，无 `apps/`），根目录**无 LICENSE / README / .github/workflows**；GitHub API `license=null`。
  - `clean-snapshot-20261026` 分支含 `apps/ packaging/ src/ tests/ tools/`，但根目录同样**无 LICENSE/NOTICE**（`raw.githubusercontent…/LICENSE` → 404）。
  - 本地 main（HEAD `8fcba8a89`）含完整 `LICENSE`（GPL-3.0-or-later）、`NOTICE.md`、`THIRD_PARTY_LICENSES.md`、`LICENSE-AGPL-3.0.txt`、`packaging/release/SHA256SUMS`，但**未 push**；无 CI workflow。
  - 签名线 [V1-RELEASE-SIGNING-1](V1-RELEASE-SIGNING-1.md)：自签名流水线已验证（RFC3161 时间戳可用），真实签名 `WAIVED`（用户接受未签名 v1）。SignPath 免费 OSS 签名是当前唯一零成本的正规签名路径。
- 目标：产出一套可直接使用的申请材料：英文申请草案（覆盖 SignPath Foundation 表单字段）、中文前置整改清单（含硬阻塞项与顺序）、可审阅的 GitHub Actions 构建+签名集成草案、根 README（申请与发布页需要），全部标注占位符与未验证项。

## Acceptance Criteria

- [x] **AC1 事实核对**：以 GitHub API + 本地 git 实测生成 `verification/SIGNPATH-OSS-SIGNING-1/facts.json`（仓库公开性/默认分支/许可缺失/CI 缺失/产物与 sha256/测试基线/签名现状），每条含来源与时间；不得按记忆或旧文档填写。证据：facts.json + 采集命令说明。<<MET>>
- [x] **AC2 英文申请材料**：`doc/release/SIGNPATH-APPLICATION.md` 覆盖 SignPath Foundation 申请所需字段：project name、repository URL、license、project description（做什么/技术栈/页面）、build & release process（现状 + 计划中的 CI）、artifacts to be signed（`NewManga-<ver>-setup.exe`，可选 sidecar exe）、integrity verification（SHA256SUMS + verify-release.ps1）、why code signing is needed（SmartScreen/用户信任/零预算）、project maturity（0.1.0、258/258、真机）、maintainer contact **占位符**、无恶意/无自动更新声明。英文准确、无夸大、不虚构下载量/用户数。证据：文档 + 关键词自检。<<MET>>
- [x] **AC3 中文前置清单**：`doc/release/SIGNPATH-APPLICATION-CHECKLIST.md` 列出申请前必须由用户完成的整改项（默认分支补 LICENSE/README、把干净源码推到默认分支或指定审核分支、GitHub Actions 可复现构建、注册 SignPath 账号与 Foundation 申请、配置 project slug/artifact config/token、发布 GitHub Release 与 SHA256SUMS），标注 P0/P1/P2、硬阻塞、涉及凭据的操作（不得由 Agent 代持 token）与风险（不得公开私有素材/模型/密钥）。<<MET>>
- [x] **AC4 CI 草案与 README**：`.github/workflows/build-release.yml`（Windows runner：checkout → 测试 → `package.ps1` 构建 base stage → `build-installer.ps1` 出 setup.exe → 上传 artifact；SignPath signing steps 以注释+条件占位，明确需要 secrets `SIGNPATH_API_TOKEN`/`SIGNPATH_ORGANIZATION_ID`/`SIGNPATH_PROJECT_SLUG`/`SIGNPATH_SIGNING_POLICY_SLUG`，未配置时跳过且不伪造签名）；根 `README.md`（英文简介 + 中文要点：架构/前置/构建/测试/发布/许可/未签名说明）。不运行 CI、不 push。<<MET>>
- [x] **AC5 门禁**：`check.ps1 -TaskPath` PASS；`extract-command-surface.py --check` PASS（66）；`scripts/test.ps1` 全绿（产品代码零改动，引用隔离复跑 258/258 + 日期）；64-hex evidence pin；Handoff。证据：logs/summary/pin。**声明：未真实申请、未签名、未 push。**<<MET>>

## 允许修改范围

`doc/release/**`（新）、根 `README.md`（新）、`.github/workflows/**`（新）、本卡、STATUS/PLAN/LEDGER、`verification/SIGNPATH-OSS-SIGNING-1/**`、自己的 Handoff、worktree 与 task-env。

## 禁止范围

不改产品源码/Core/旧壳/冻结契约；**不 push、不执行真实 GitHub Actions、不代持任何 token/密钥、不提交申请、不做签名**；不删除/移动现有文档；不把模型权重或私有素材写入仓库；不伪造 CI 运行结果或签名状态。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | GitHub API（`web_fetch`）+ `git ls-remote` + 本地 git/哈希 → facts.json | 网络只读 + 本地 git | **PASS**：仓库 public/default=main/license=null；main 与 clean-snapshot 根均无 LICENSE/README；无 CI；产物 sha256 与测试基线已记录 | `facts.json` |
| AC2/AC3/AC4 | 文档/工作流静态审阅 + 关键词/链接自检 | 仓库 | **PASS**：`yaml.safe_load` OK（jobs=build，12 steps）；占位符 5 类；相对链接 0 missing；未虚构数据 | `REPORT.md` §3 |
| AC5 | `extract-command-surface.py --check`、`scripts/test.ps1`、`check.ps1 -TaskPath` | 仓库 | 命令面 PASS（66）；测试基线 258/258（2026-10-28，产品零改动）；check 见本卡 Review 前门禁 | 见 Canonical Evidence |

## 依赖、风险与阻塞

- 硬依赖：`RELEASE-VERIFY-1`（SHA256SUMS/校验脚本，`done`）；`V1-RELEASE-SIGNING-1`（签名线与自签名流水线证据，`in_review`）。
- 风险：①申请是否通过取决于 SignPath 审核（本卡不承诺通过）；②公开仓库当前许可/CI/README 缺失，属于**申请前硬阻塞**（清单 P0）；③用户个人信息/联系方式需用户本人填（Agent 不代填）；④GitHub Actions 与 SignPath 集成需要用户账号与 secrets，Agent 不得代持。
- 阻塞解除标准：用户按 CHECKLIST 完成 P0/P1 并提交申请；审核通过后由签名线实施真实签名（不在本卡）。

## 交付与运行记录

- Handoff：[SIGNPATH-OSS-SIGNING-1-handoff.md](../handoffs/SIGNPATH-OSS-SIGNING-1-handoff.md)
- Review：待独立审阅（Reviewer=`region-workbench-owner`；Owner=`dsh-lead`，不同人）。
- 实现/证据提交：`340867cd807f900e28c831c38f29168c93f5c1b5`（材料 4 件 + facts/REPORT；`delivery_head`）。
- 明确未做：未 push、未创建 GitHub Release、未运行 CI、未调用 SignPath API、未签名。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| facts | AC1 | verification/SIGNPATH-OSS-SIGNING-1/facts.json | 340867cd807f900e28c831c38f29168c93f5c1b5 | 8de66d2bac537da7c860d73f3e7233f3fcba93f8d0bdcba894162f066e5e2e7d | CANONICAL |
| report | AC1–AC5 | verification/SIGNPATH-OSS-SIGNING-1/REPORT.md | 340867cd807f900e28c831c38f29168c93f5c1b5 | d5ae3e62b6dfcd7f531f95b15e278ecee959e61826e6a763f7f797ca12b7e52d | CANONICAL |
| application-en | AC2 | doc/release/SIGNPATH-APPLICATION.md | 340867cd807f900e28c831c38f29168c93f5c1b5 | 247860b09762d0f5d27d5cf15c1a029f9ef18242c9943a7cf47545c24e2ce30b | CANONICAL |
| checklist-zh | AC3 | doc/release/SIGNPATH-APPLICATION-CHECKLIST.md | 340867cd807f900e28c831c38f29168c93f5c1b5 | ab24fe019b0283f81762a0974c4b9bbae174bd1bd3143744505ab7cfd7d17fa2 | CANONICAL |
| ci-draft | AC4 | .github/workflows/build-release.yml | 340867cd807f900e28c831c38f29168c93f5c1b5 | dc70308bdc784bf65ba895d98b119b4442ee751c50e300480600ce4e4519a419 | SOURCE_PIN |
| readme | AC4 | README.md | 340867cd807f900e28c831c38f29168c93f5c1b5 | 372f2d91d1bea31fe46ed145722cc3106b95e432189c7297642f9b91c6732103 | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/SIGNPATH-OSS-SIGNING-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/SIGNPATH-OSS-SIGNING-1 | verification/SIGNPATH-OSS-SIGNING-1/facts.json | 交付后按 Worktree Safety Inventory 复核；未 push |
| task-env | G:/CODEX/New Manga.workspace/task-envs/SIGNPATH-OSS-SIGNING-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/SIGNPATH-OSS-SIGNING-1 | 8de66d2bac537da7c860d73f3e7233f3fcba93f8d0bdcba894162f066e5e2e7d | facts 采集脚本与 sed 日志只写此处（目录资源，hash 为 facts.json 指纹） |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`complete`（6 项 64-hex pin）。
- resource_closeout_status：`pending`（worktree/task-env 保留至集成）。
- 删除、迁移、归档数量/字节数：0。
- 未关闭项及保留原因：材料为草案，申请与签名由用户在 SignPath 审核通过后执行（不在本卡）；V1-RELEASE-SIGNING-1 保持 in_review。
- 当前指针清理：交付时更新 STATUS/PLAN/LEDGER。
