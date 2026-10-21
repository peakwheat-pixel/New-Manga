---
id: GOV-NDJSON-NONDECL-IDENTITY-1
title: 两份P02 NDJSON证据的非声明身份与精确例外适用性核验
kind: research
governance_version: 3
status: ready
approval: user_continue_next_readonly_identity_verification_20261021
suggested_owner: Codex
owner: Codex
reviewer: DeepSeek Harness
depends_on: [GOV-DECLARATION-RESIDUAL-32-AUDIT-1]
base_commit: 50d784300ac74d6ded633685bfce201cdddb630a
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/GOV-NDJSON-NONDECL-IDENTITY-1
allowed_paths:
  - doc/tasks/GOV-NDJSON-NONDECL-IDENTITY-1.md
  - doc/handoffs/GOV-NDJSON-NONDECL-IDENTITY-1.md
  - verification/GOV-NDJSON-NONDECL-IDENTITY-1
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/tasks/README.md
  - doc/tasks/GIT-MAINLINE-CONVERGENCE-1.md
  - verification/GIT-MAINLINE-CONVERGENCE-1/checkpoint.md
---

# GOV-NDJSON-NONDECL-IDENTITY-1

## 来源与范围冻结

用户“继续下一步”授权执行已完成32项取证Handoff建议：仅核验R23/R24的NDJSON身份与现有path+raw SHA例外适用性。依赖独审927e06f8b、done；32项错误及父Task blocked/STATUS-r212禁令保留。scope.json冻结两原始路径/raw SHA及tracked状态。当前Codex epoch9，main tracked dirty=0，common dir须实测权威.git；不新建branch/worktree，98/136保持。

Codex串行文档写入main，DeepSeek固定commit独审。只读两日志及其直接格式/引用元数据、既有guard相关函数和实际例外清单；不运行旧collector、不通扫历史。机制负例可调用现有函数，以本Task workspace agent-output中候选清单作为显式json_exceptions输入，并在内存替换测试字节/枚举值；不得修改真实日志、工具、正式例外表。模拟32→30只能叫候选结果，正式审计仍应32；不自动使研究批准变成登记授权。

## Acceptance Criteria

- [ ] **AC1** 两日志raw SHA/Git状态、逐行JSON/完整消费、schema/kind种类和全部结构化声明身份键核验；如存在引用路径，区分日志指针与保护声明，不把格式有效当无声明。 <<NOT_RUN>>
- [ ] **AC2** 明确现有例外的精确path/hash/reason、加载/绕过时点和信任边界；候选匹配、不匹配路径、不匹配字节、无例外及变化后声明等负例有实际结果或明确NOT_RUN，不泛化坏JSON豁免。 <<NOT_RUN>>
- [ ] **AC3** 同数据快照正式32错误保留；候选若32→30只能移除R23/R24且旧保护集合不减少；原日志、正式例外表和guard字节/status前后不变。 <<NOT_RUN>>
- [ ] **AC4** 固定head独立DeepSeek Review、Codex裁定、Handoff/证据pin/保留资源核销和治理check完成；是否需后续写范围作出明确裁定。 <<NOT_RUN>>

## 禁止范围

不改原日志/历史Task/source/pin、guard/正式例外表、共享接口/Schema/依赖、用户文件/DB/模型/ACL/租约/会话；不执行collector、构建、安装、apply、清理/迁移/归档/GC/prune/push/强删/自动stash。不释放Legacy任务。候选清单仅workspace分析输入，现有保护不解除；正式登记或代码修复必须另冻Task/allowed_paths并独审。父Task只允许closeout进展元数据追加，不改其原AC/pin。

## 验证计划

PowerShell/Python -B；只读标准库诊断与现有guard函数调用，不新增产品或guard源码测试。候选及负例输入留workspace；不创建第二项目仓库，不修改/删除真实资源。pythonic内存输入模拟须明确标记，不能冒充真实改名/编辑。产品/构建测试NOT_RUN（无代码变更），不以之替代机制正反例。运行pwsh -NoProfile -File tools/governance/check.ps1。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | G:/CODEX/New Manga.workspace/agent-output/codex/GOV-NDJSON-NONDECL-IDENTITY-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/agent-output/codex/GOV-NDJSON-NONDECL-IDENTITY-1 | doc/tasks/GOV-NDJSON-NONDECL-IDENTITY-1.md | 候选输入/负例/原始派发输出保留，不写正式例外表 |
| worktree/task-env/dataset/model/build/temp/exchange | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | 无新建，不删除其它资源 |

## 运行记录

ready冻结后认领；Reviewer只读，审查期间Owner暂停被审文档写入。研究与候选输入不等于实际例外登记。Handoff/Review待交付。
