---
id: GOV-RESIDUAL-TEMPLATE-NUL-IDENTITY-1
title: 剩余模板与NUL五项只读身份核验
kind: research
governance_version: 3
status: in_progress
approval: user_auto_continue_next_task_20261022
suggested_owner: Codex
owner: Codex
reviewer: DeepSeek Harness
depends_on: [GOV-BROAD-ROOT-PRESERVATION-IMPL-1]
base_commit: 951b7c61f2d09e842fc170290a1327e6780acbc0
branch: codex/gov-residual-template-nul-identity-1
worktree: G:/CODEX/New Manga.workspace/worktrees/GOV-RESIDUAL-TEMPLATE-NUL-IDENTITY-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/GOV-RESIDUAL-TEMPLATE-NUL-IDENTITY-1
allowed_paths:
  - verification/GOV-RESIDUAL-TEMPLATE-NUL-IDENTITY-1
  - doc/tasks/GOV-RESIDUAL-TEMPLATE-NUL-IDENTITY-1.md
  - doc/handoffs/GOV-RESIDUAL-TEMPLATE-NUL-IDENTITY-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/tasks/README.md
  - verification/GIT-MAINLINE-CONVERGENCE-1/checkpoint.md
---

# GOV-RESIDUAL-TEMPLATE-NUL-IDENTITY-1

## 冻结来源、范围与目标

用户“自动继续下一步任务”（2026-10-22），来源已done实现Handoff、当前STATUS/Plan和父checkpoint；依赖R4 d5d21ff9f、集成a3bba87ce，当前基线951b7c61f。Owner Codex，Reviewer DeepSeek Harness非作者。只读当前12中的2模板错误（同一旧Review）和3含NUL文件，读取已引用32矩阵对应项及必要scanner/规则；交付精确原字节身份、语义/归属/引用与保护、保全解释选项和最小后续设计边界。研究完成不等于修复。

禁止改旧Review/NUL/历史源、旧Task/source pin/69例外/scanner/共享契约/Schema/依赖或产品代码；7历史运行身份保留BLOCKED，不猜TEMP/APPDATA，不扩大历史扫描。不执行apply/删除/迁移/归档/GC/prune/push/reset/stash/ACL/安装/Legacy。只写allowed_paths。原作者dirty/untracked/ignored原地保留。DeepSeek严格纯只读/内存，禁止fixture/权限探针/任何项目或TMP写入；不能枚举则NOT_RUN，不能绕过权限。

## Acceptance Criteria

- [ ] **AC1** 五项完整code/file/locator/message与当前12、多重集匹配；原raw SHA/编码/NUL位置/行定位、tracked/HEAD blob或untracked归属事实明确，不猜修复。 <<PARTIAL: 待读取证>>
- [ ] **AC2** 有界核实语义、来源链与当前引用/保护，给出保持原字节和旧pin的解释选项；未知与最小裁决、7历史身份保留，禁止把研究当例外配置或删除授权。 <<PARTIAL: 待研究>>
- [ ] **AC3** 同canonical数据前后12完整身份不变、旧保护集合不减、五源raw不变；所有EV raw/blob/pin与实际注册、check/diff实测，NOT_RUN分列。 <<PARTIAL: 待验证>>
- [ ] **AC4** 固定head DeepSeek独审通过，Codex正常集成/复验、资源原位保留核销，Task/STATUS/Plan/Handoff/恢复点一致。 <<PARTIAL: 待审集成>>

## 测试计划与限制

planned：Python -B读取原字节/JSON和必要Git只读查询、调用当前scan_repo_declarations同canonical数据并比较完整error/protected多重集；pwsh -NoProfile -File tools/governance/check.ps1；git diff --check。非实现，不创建合成fixture、不跑产品构建或旧127回归；NOT_RUN需注明与本只读研究无关。任何解码只在内存，不回写NUL源，不生成会被scanner当作新坏Markdown的副本。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/GOV-RESIDUAL-TEMPLATE-NUL-IDENTITY-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/GOV-RESIDUAL-TEMPLATE-NUL-IDENTITY-1 | doc/tasks/GOV-RESIDUAL-TEMPLATE-NUL-IDENTITY-1.md | 冻结后创建，原位保留，不删除 |
| agent-output | G:/CODEX/New Manga.workspace/agent-output/codex/GOV-RESIDUAL-TEMPLATE-NUL-IDENTITY-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/agent-output/codex/GOV-RESIDUAL-TEMPLATE-NUL-IDENTITY-1 | doc/tasks/GOV-RESIDUAL-TEMPLATE-NUL-IDENTITY-1.md | 只读运行日志/会话材料保留，无fixture/清理 |
| env/build/model | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | 无新建 |

## 运行与恢复

冻结时main951b7c61f，common G:/CODEX/New Manga/.git；Codex epoch9有效，无并发主控接管。当前100heads/138WT，任务资源创建后预计101/139，新增资源按r212原位保留，父blocked且尚未只剩main。新branch/worktree为冻结分配路径，创建后补实际base/HEAD。不得用worktree缺未跟踪源替代canonical事实；只将本Task新增证据镜像到main供check/真实注册，旧源不镜像改写。
