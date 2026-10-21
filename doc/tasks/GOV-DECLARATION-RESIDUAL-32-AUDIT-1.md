---
id: GOV-DECLARATION-RESIDUAL-32-AUDIT-1
title: 剩余32项声明只读取证与最小裁决矩阵
kind: research
governance_version: 3
status: in_review
approval: user_authorized_20261021_readonly_32_declarations_independent_dsh_review
suggested_owner: Codex
owner: Codex
reviewer: DeepSeek Harness
depends_on: [GOV-PATH-HEADER-COMPAT-1]
base_commit: c0a9cb7962669cb4e987af51260f68850f4fe3b0
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: 22bd5e07af5710af2359827a45fdf658186f578d
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

- [x] **AC1** 精确32项一一对应原code/file/locator，按来源记录Git跟踪、原始字节hash、磁盘与base blob差异和可证实署名；不把猜测当归属。 <<MET>>
- [x] **AC2** 各项有原文/实际行号或JSON pointer、保护影响、最小建议及授权边界；语法/编码问题与处置裁决区分，未知仍保留。 <<MET>>
- [x] **AC3** 取证前后source原始字节与跟踪/未跟踪状态不变；32错误不消解、不忽略，声明审计exit2和原错误身份可复核；分支/工作树计数不变。 <<MET>>
- [ ] **AC4** 固定head独立DeepSeek Review、Codex裁定、Handoff、证据pin和资源保留核销完成；治理check通过。 <<PARTIAL: 取证证据已固定，等待独立Review与Codex核销>>

## 禁止范围

历史Task/source/evidence/pin、原始JSON/日志/编码、所有工具源码、用户文件/DB/模型、租约和Agent应用会话数据不得改写；不改共享接口/Schema/依赖，不恢复Legacy任务。禁止apply/删除/迁移/归档/GC/prune/push/强删/自动stash/修改ACL。STATUS/r212与全部资源保护不变。研究建议不授权修复，更不授权清理；不得把32errors当32独立资源或直接按source+destination双计资源。

## 测试要求

Windows PowerShell/Python -B。只读source字节/引用核验、原错误身份比较、HEAD/status/common-dir/count前后核对；运行pwsh -NoProfile -File tools/governance/check.ps1。可执行clean_workspace.py --audit-declarations --out本Task agent-output，只读审计不是清理PASS。产品/解析器回归NOT_RUN（无代码变更）；无fixtures/构建/安装。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|

|EV-1|AC4|verification/GOV-DECLARATION-RESIDUAL-32-AUDIT-1/.gitattributes|22bd5e07af5710af2359827a45fdf658186f578d|a79691a93b46e49ce460c26ef22afcc03d6eca1e63bf2edbc20e96159510f6c9|CANONICAL|
|EV-2|AC1|verification/GOV-DECLARATION-RESIDUAL-32-AUDIT-1/scope.json|22bd5e07af5710af2359827a45fdf658186f578d|890a2e7edee5d8290b80c1852fd3f40195d92f1d0c4794df987abe110a80c35d|CANONICAL|
|EV-3|AC1/AC2|verification/GOV-DECLARATION-RESIDUAL-32-AUDIT-1/source-facts.json|22bd5e07af5710af2359827a45fdf658186f578d|bcc6cd03e37111c6883f90f6fe1963b74a5eca97eda54aa3ee5b9e9a416d426b|CANONICAL|
|EV-4|AC2|verification/GOV-DECLARATION-RESIDUAL-32-AUDIT-1/direct-reference-facts.json|22bd5e07af5710af2359827a45fdf658186f578d|d5143da8284b645aa7175b8cf7e1a3eed319da1f02c01d700cdf44c3afbebcac|CANONICAL|
|EV-5|AC1/AC2|verification/GOV-DECLARATION-RESIDUAL-32-AUDIT-1/matrix.json|22bd5e07af5710af2359827a45fdf658186f578d|e905a64bdab13f3b846cd0306d82d1471f6a45321c191e948e614ca449258778|CANONICAL|
|EV-6|AC2|verification/GOV-DECLARATION-RESIDUAL-32-AUDIT-1/matrix.md|22bd5e07af5710af2359827a45fdf658186f578d|6fab40bbb0b2a6087c4c79fbf9bae04a84210603072aa19b02870cddafe36747|CANONICAL|
|EV-7|AC3|verification/GOV-DECLARATION-RESIDUAL-32-AUDIT-1/preservation-validation.json|22bd5e07af5710af2359827a45fdf658186f578d|4613e4aec8e31453cd574cbbe07d6c5b2bdbc1dff724f7be09d512204e9d7392|CANONICAL|
|EV-8|AC1/AC2/AC3|verification/GOV-DECLARATION-RESIDUAL-32-AUDIT-1/report.md|22bd5e07af5710af2359827a45fdf658186f578d|5755179129cf5c7484550f57506c4d74e881518454a8216dd22e4f533c2458e1|CANONICAL|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | G:/CODEX/New Manga.workspace/agent-output/codex/GOV-DECLARATION-RESIDUAL-32-AUDIT-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/agent-output/codex/GOV-DECLARATION-RESIDUAL-32-AUDIT-1 | doc/tasks/GOV-DECLARATION-RESIDUAL-32-AUDIT-1.md | 本Task派发/原始日志保留；不删除 |
| worktree/task-env/dataset/model/artifact/temp/exchange | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | 不新建；复用主仓库串行文档写入 |

## 运行记录

2026-10-21冻结ready；唯一Coordinator Codex epoch9，tracked dirty=0，common dir为权威仓库.git。历史未跟踪草稿原作者所有，不提交。后续精确证据与独审记录追加；不得自动启动修复。

## 交付记录

32项/17来源取证完成；六组为6/12/7/2/2/3。原raw SHA/status不变，原32完整错误身份多重集合不变，98heads/136worktrees；声明审计exit2为预期fail-closed，不写成清理PASS。初始观察对象导致4重复错误，已仅修本Task报告引用形式，原来源未变。固定证据 22bd5e07af5710af2359827a45fdf658186f578d；Handoff doc/handoffs/GOV-DECLARATION-RESIDUAL-32-AUDIT-1.md。DSH独审期间暂停写入被审文档；Reviewer只读，不申请租约/改ACL/修改任何文件。
