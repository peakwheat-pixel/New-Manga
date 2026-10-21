---
id: GOV-DECLARATION-RESIDUAL-32-AUDIT-1
title: 剩余32项声明只读取证与最小裁决矩阵
kind: research
governance_version: 3
status: ready
approval: user_authorized_20261021_readonly_32_declarations_independent_dsh_review
suggested_owner: Codex
owner: Codex
reviewer: DeepSeek Harness
depends_on: [GOV-PATH-HEADER-COMPAT-1]
base_commit: c0a9cb7962669cb4e987af51260f68850f4fe3b0
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/GOV-DECLARATION-RESIDUAL-32-AUDIT-1
allowed_paths:
  - doc/tasks/GOV-DECLARATION-RESIDUAL-32-AUDIT-1.md
  - verification/GOV-DECLARATION-RESIDUAL-32-AUDIT-1
  - doc/handoffs/GOV-DECLARATION-RESIDUAL-32-AUDIT-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/tasks/README.md
created: 2026-10-21
---

# GOV-DECLARATION-RESIDUAL-32-AUDIT-1

## 来源与范围冻结

用户明确授权Codex冻结剩余32项声明的只读取证任务，由DeepSeek独立审查。依赖已集成9cae94142、done；父GIT-MAINLINE-CONVERGENCE-1继续blocked。唯一输入为 verification/GOV-PATH-HEADER-COMPAT-1/postintegration-declaration-audit.json 的32条error，来源文件及原始locator逐项冻结于verification/GOV-DECLARATION-RESIDUAL-32-AUDIT-1/scope.json（17个来源文件）。不得用另一轮扫描扩大取证范围。

Codex在main串行写自身研究/治理文档；本Task不改代码，不新增branch/worktree，不使98 heads/136 worktrees增加。DeepSeek固定commit只读Review，Owner与Reviewer不同；审查期间Codex暂停对被审文档写入。仅对冻结source及其所列精确直接引用做有界读取，允许Git blob/历史单文件定位和只读文件指纹/编码检查，不递归扫描历史或其他工作树。

## Acceptance Criteria

- [ ] **AC1** 精确32项一一对应原code/file/locator，按来源记录Git跟踪、原始字节hash、磁盘与base blob差异和可证实署名；不把猜测当归属。 <<NOT_RUN>>
- [ ] **AC2** 各项有原文/实际行号或JSON pointer、保护影响、最小建议及授权边界；语法/编码问题与处置裁决区分，未知仍保留。 <<NOT_RUN>>
- [ ] **AC3** 取证前后source原始字节与跟踪/未跟踪状态不变；32错误不消解、不忽略，声明审计exit2和原错误身份可复核；分支/工作树计数不变。 <<NOT_RUN>>
- [ ] **AC4** 固定head独立DeepSeek Review、Codex裁定、Handoff、证据pin和资源保留核销完成；治理check通过。 <<NOT_RUN>>

## 禁止范围

历史Task/source/evidence/pin、原始JSON/日志/编码、所有工具源码、用户文件/DB/模型、租约和Agent应用会话数据不得改写；不改共享接口/Schema/依赖，不恢复Legacy任务。禁止apply/删除/迁移/归档/GC/prune/push/强删/自动stash/修改ACL。STATUS/r212与全部资源保护不变。研究建议不授权修复，更不授权清理；不得把32errors当32独立资源或直接按source+destination双计资源。

## 测试要求

Windows PowerShell/Python -B。只读source字节/引用核验、原错误身份比较、HEAD/status/common-dir/count前后核对；运行pwsh -NoProfile -File tools/governance/check.ps1。可执行clean_workspace.py --audit-declarations --out本Task agent-output，只读审计不是清理PASS。产品/解析器回归NOT_RUN（无代码变更）；无fixtures/构建/安装。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | G:/CODEX/New Manga.workspace/agent-output/codex/GOV-DECLARATION-RESIDUAL-32-AUDIT-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/agent-output/codex/GOV-DECLARATION-RESIDUAL-32-AUDIT-1 | doc/tasks/GOV-DECLARATION-RESIDUAL-32-AUDIT-1.md | 本Task派发/原始日志保留；不删除 |
| worktree/task-env/dataset/model/artifact/temp/exchange | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | 不新建；复用主仓库串行文档写入 |

## 运行记录

2026-10-21冻结ready；唯一Coordinator Codex epoch9，tracked dirty=0，common dir为权威仓库.git。历史未跟踪草稿原作者所有，不提交。后续精确证据与独审记录追加；不得自动启动修复。
