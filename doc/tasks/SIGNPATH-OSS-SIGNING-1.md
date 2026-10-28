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
delivery_head: 1ab7f904aeb084fdcdefd74209e8b344b12209ab
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
- 2026-10-28 事实核对（只读，详见 `verification/SIGNPATH-OSS-SIGNING-1/facts.json`）：
  - GitHub 公开仓库：`https://github.com/peakwheat-pixel/New-Manga`（`private=false`、`fork=false`、`default_branch=main`、`created=2026-09-24`、`size≈28 MB`、`pushed_at=2026-10-26`、star/fork=0）。
  - **默认分支 `main` 为旧内容**（`src/tests/doc/verification/wiki`，无 `apps/`），根目录**无 LICENSE / README / .github/workflows**；GitHub API `license=null`。
  - `clean-snapshot-20261026` 分支含 `apps/ packaging/ src/ tests/ tools/`，但根目录同样**无 LICENSE/NOTICE**（`raw.githubusercontent…/LICENSE` → 404）。
  - 本地 main（HEAD `8fcba8a89`）含完整 `LICENSE`（GPL-3.0-or-later）、`NOTICE.md`、`THIRD_PARTY_LICENSES.md`、`LICENSE-AGPL-3.0.txt`、`packaging/release/SHA256SUMS`，但**未 push**；无 CI workflow。
  - 签名线 [V1-RELEASE-SIGNING-1](V1-RELEASE-SIGNING-1.md)：自签名流水线已验证（RFC3161 时间戳可用），真实签名 `WAIVED`（用户接受未签名 v1）。SignPath 免费 OSS 签名是当前唯一零成本的正规签名路径。
- 目标：产出一套可直接使用的申请材料：英文申请草案（覆盖 SignPath Foundation 表单字段）、中文前置整改清单（含硬阻塞项与顺序）、可审阅的 GitHub Actions 构建+签名集成草案、根 README（申请与发布页需要），全部标注占位符与未验证项。

## Acceptance Criteria

- [x] **AC1 事实核对**：以 GitHub API + 本地 git 实测生成 `verification/SIGNPATH-OSS-SIGNING-1/facts.json`（仓库公开性/默认分支/许可缺失/CI 缺失/产物与 sha256/测试基线/签名现状/隐私事实），每条含来源与时间；不得按记忆或旧文档填写。证据：facts.json + 采集方法说明。<<MET>>
- [x] **AC2 英文申请材料**：`doc/release/SIGNPATH-APPLICATION.md` 覆盖 SignPath Foundation 申请所需字段：project name、repository URL、license、project description（做什么/技术栈/页面/隐私模型）、build & release process（现状 + 计划中的 CI，含公开构建的依赖与权重策略）、artifacts to be signed（`NewManga-<ver>-setup.exe`，可选 sidecar exe）、integrity verification（SHA256SUMS + verify-release.ps1）、why code signing is needed（SmartScreen/用户信任/零预算）、project maturity（0.1.0、258/258、真机证据路径、star/fork=0 与仓库创建时间）、maintainer contact **占位符**、无恶意/无自动更新声明、发布策略。英文准确、无夸大、不虚构下载量/用户数、不宣称“完全不上传任何数据”。证据：文档 + 关键词自检。<<MET>>
- [x] **AC3 中文前置清单**：`doc/release/SIGNPATH-APPLICATION-CHECKLIST.md` 列出申请前必须由用户完成的整改项（默认分支补 LICENSE/README、把干净源码推到默认分支或指定审核分支、GitHub Actions 可复现构建、注册 SignPath 账号与 Foundation 申请、配置 project slug/artifact config/token、发布 GitHub Release 与 SHA256SUMS），标注 P0/P1/P2、硬阻塞、CI 依赖与 `-SkipWeights` 事实、涉及凭据的操作（不得由 Agent 代持 token）、触发方式（手动 Run/sign 输入）与风险（不得公开私有素材/模型/密钥）。<<MET>>
- [x] **AC4 CI 草案与 README**：`.github/workflows/build-release.yml`（Windows runner：checkout → 安装 dev 依赖 → pytest → `build_sidecar.ps1 -PythonExe python -SkipWeights` → `package.ps1` 构建 base stage → `build-installer.ps1` 出 setup.exe → 生成 base-only SHA256SUMS → 上传 setup/base zip/清单；SignPath 签名步骤以 `sign` 输入控制、token 仅注入 env、默认禁用且不伪造签名）；根 `README.md`（英文简介 + 中文要点 + 准确隐私表述：默认本地、远程 Provider 可选告知、架构/前置/构建/测试/发布/许可/未签名说明）。不运行 CI、不 push。<<MET>>
- [x] **AC5 门禁**：`check.ps1 -TaskPath` PASS；`extract-command-surface.py --check` PASS（66）；`scripts/test.ps1` 全绿（产品代码零改动，引用隔离复跑 258/258 + 日期）；64-hex evidence pin；Handoff。证据：check-governance.json、extract-command-surface.log、跨 Task 引用 RELEASE-VERIFY-1 test summary、pin 表。**声明：未真实申请、未签名、未 push。**<<MET>>

## 允许修改范围

`doc/release/**`（新）、根 `README.md`（新）、`.github/workflows/**`（新）、本卡、STATUS/PLAN/LEDGER、`verification/SIGNPATH-OSS-SIGNING-1/**`、自己的 Handoff、worktree 与 task-env。

## 禁止范围

不改产品源码/Core/旧壳/冻结契约；**不 push、不执行真实 GitHub Actions、不代持任何 token/密钥、不提交申请、不做签名**；不删除/移动现有文档；不把模型权重或私有素材写入仓库；不伪造 CI 运行结果或签名状态。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | GitHub API（`web_fetch`）+ `git ls-remote` + 本地 git/哈希 → facts.json | 网络只读 + 本地 git | **PASS**：仓库 public/default=main/license=null；main 与 clean-snapshot 根均无 LICENSE/README；无 CI；产物 sha256 与测试基线已记录；隐私事实按 `privacy.py` 记录 | `facts.json` |
| AC2/AC3/AC4 | 文档/工作流静态审阅 + 关键词/链接自检 + 独立审阅 | 仓库 | **PASS（Rev2）**：`yaml.safe_load` OK（jobs=build，12 steps）；占位符 4 类；相对链接 0 missing；不虚构；隐私表述按代码事实修正；CI 依赖/权重/清单可执行性修正 | `REPORT.md` §3/§7 |
| AC5 | `extract-command-surface.py --check`、`scripts/test.ps1`、`check.ps1 -TaskPath` | 仓库 | 命令面 PASS（66）；测试基线 258/258（2026-10-28，产品零改动）；check PASS（见 check-governance.json） | `check-governance.json`、`logs/extract-command-surface.log` |

## 依赖、风险与阻塞

- 硬依赖：`RELEASE-VERIFY-1`（SHA256SUMS/校验脚本，`done`）；`V1-RELEASE-SIGNING-1`（签名线与自签名流水线证据，`in_review`）。
- 风险：①申请是否通过取决于 SignPath 审核（本卡不承诺通过；仓库 star/fork=0、尚无公开 release）；②公开仓库当前许可/CI/README/源码树缺失，属于**申请前硬阻塞**（清单 P0）；③用户个人信息/联系方式需用户本人填（Agent 不代填）；④GitHub Actions 与 SignPath 集成需要用户账号与 secrets，Agent 不得代持；⑤`secrets` 不能用于 `if:`，启用方式已按 `sign` 输入设计。
- 阻塞解除标准：用户按 CHECKLIST 完成 P0/P1 并提交申请；审核通过后由签名线实施真实签名（不在本卡）。

## 交付与运行记录

- Handoff：[SIGNPATH-OSS-SIGNING-1-handoff.md](../handoffs/SIGNPATH-OSS-SIGNING-1-handoff.md)
- Review：**独立审阅 CHANGES_REQUESTED → Rev2 已修复**（Reviewer=`region-workbench-owner`；Owner=`dsh-lead`，不同人）。3 个 P0（隐私表述、pin 可达性、CI 可执行性）+ 8 个 P1 + 9 个 P2，逐项修复记录见 `REPORT.md` §7 与文末 Rev2 记录；待 Reviewer 复核 Rev2。
- delivery_head：`1ab7f904aeb084fdcdefd74209e8b344b12209ab`（Rev2 材料 + 证据提交）。
- 明确未做：未 push、未创建 GitHub Release、未运行 CI、未调用 SignPath API、未签名。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| facts | AC1 | verification/SIGNPATH-OSS-SIGNING-1/facts.json | 1ab7f904aeb084fdcdefd74209e8b344b12209ab | ad17365336aa5d1bc3a62be18113aebced84def90c0943502f5b26d26c11976d | CANONICAL |
| report | AC1–AC5 | verification/SIGNPATH-OSS-SIGNING-1/REPORT.md | 1ab7f904aeb084fdcdefd74209e8b344b12209ab | 24f8a0f2cfadf4f1470a22bc1ea506a7d0313a5b2148f41f5188f02c52c54999 | CANONICAL |
| application-en | AC2 | doc/release/SIGNPATH-APPLICATION.md | 1ab7f904aeb084fdcdefd74209e8b344b12209ab | d517d2679040a783cdd4da60eeec3e50072c2eb97a8232ed9e901d8285173dfc | CANONICAL |
| checklist-zh | AC3 | doc/release/SIGNPATH-APPLICATION-CHECKLIST.md | 1ab7f904aeb084fdcdefd74209e8b344b12209ab | 22f05352063c1e4b3655d8d3b7b0a60eeec6120d731186e9128fc77d309f081c | CANONICAL |
| ci-draft | AC4 | .github/workflows/build-release.yml | 1ab7f904aeb084fdcdefd74209e8b344b12209ab | 4a6332d2f972ba1028daa49159d589419ea76c0a9a58e884470f0dc39ea7ac94 | SOURCE_PIN |
| readme | AC4 | README.md | 1ab7f904aeb084fdcdefd74209e8b344b12209ab | 04c7bc9b0431c61f23b3f76618591c56da433f03150ea60209550e9fde454a73 | CANONICAL |
| handoff | 交付 | doc/handoffs/SIGNPATH-OSS-SIGNING-1-handoff.md | 1ab7f904aeb084fdcdefd74209e8b344b12209ab | 4e0b1e72f9638d4af939ebbcfc7a35decb49aa7fb95b594c6a4ed3b8d764b350 | CANONICAL |
| command-surface-log | AC5 | verification/SIGNPATH-OSS-SIGNING-1/logs/extract-command-surface.log | 1ab7f904aeb084fdcdefd74209e8b344b12209ab | 820f6d456abeab98d52599b5fffdfa051b58369b8a108e8860b1fde4f6db82fe | SOURCE_PIN |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/SIGNPATH-OSS-SIGNING-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/SIGNPATH-OSS-SIGNING-1 | verification/SIGNPATH-OSS-SIGNING-1/facts.json | 交付后按 Worktree Safety Inventory 复核；未 push；无 task-env（本卡未产生需保留的仓外运行目录） |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`complete`（8 项 pin：6 CANONICAL + 2 SOURCE_PIN；check-governance 行在最终 gate 后补登）。
- resource_closeout_status：`pending`（worktree 保留至集成）。
- 删除、迁移、归档数量/字节数：0。
- 未关闭项及保留原因：材料为草案，申请与签名由用户在 SignPath 审核通过后执行（不在本卡）；V1-RELEASE-SIGNING-1 保持 in_review。
- 当前指针清理：交付时更新 STATUS/PLAN/LEDGER。

## Rev2 记录（独立审阅修复，2026-10-28）

- Reviewer（region-workbench-owner）结论：CHANGES_REQUESTED（3 P0 / 8 P1 / 9 P2）。
- 已修：P0-1 隐私表述（README + 申请 §2 + facts.privacy_fact）；P0-2 pin/交付 head 重打到 `1ab7f904a`（blob hash 不变）；P0-3 CI 草案（dev 依赖、`-SkipWeights`、base-only 清单、注释说明完整清单来源）；P1-1 字节口径；P1-2 README 中文要点；P1-3 Handoff 模板节；P1-4 删除不存在的 task-env 行；P1-5 `sign` 输入替代 `secrets` in `if:` + upload `id`；P1-6 手动 Run 触发口径；P1-7 门禁证据 pin；P2 项（PE32、four license/notice files、发行说明语言、证据路径、NSIS 3.x、根条目）已逐一修正。
- 待办：Reviewer 复核 Rev2 后给最终结论；随后 DSH 集成收口。
