---
id: GOV-DECLARATION-RESIDUAL-32-AUDIT-1
title: 剩余32项声明只读取证与最小裁决矩阵
kind: research
governance_version: 3
status: done
approval: user_authorized_20261021_readonly_32_declarations_independent_dsh_review
suggested_owner: Codex
owner: Codex
reviewer: DeepSeek Harness
latest_review: verification/GOV-DECLARATION-RESIDUAL-32-AUDIT-1/deepseek-review-r2.md
reviewed_head: 927e06f8b25563afbc7acbcc25d19fe775d1ded6
depends_on: [GOV-PATH-HEADER-COMPAT-1]
base_commit: c0a9cb7962669cb4e987af51260f68850f4fe3b0
branch: main
worktree: G:/CODEX/New Manga
integration_commit: 927e06f8b25563afbc7acbcc25d19fe775d1ded6
delivery_head: e2b8d19ed47a5ecde53d53f7fa17be6a2e10c29f
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/GOV-DECLARATION-RESIDUAL-32-AUDIT-1
allowed_paths:
  - doc/tasks/GOV-DECLARATION-RESIDUAL-32-AUDIT-1.md
  - verification/GOV-DECLARATION-RESIDUAL-32-AUDIT-1
  - doc/handoffs/GOV-DECLARATION-RESIDUAL-32-AUDIT-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/tasks/README.md
  - doc/tasks/GIT-MAINLINE-CONVERGENCE-1.md
  - verification/GIT-MAINLINE-CONVERGENCE-1/checkpoint.md
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
- [x] **AC4** 固定head独立DeepSeek Review、Codex裁定、Handoff、证据pin和资源保留核销完成；治理check通过。 <<MET>>

## 禁止范围

历史Task/source/evidence/pin、原始JSON/日志/编码、所有工具源码、用户文件/DB/模型、租约和Agent应用会话数据不得改写；不改共享接口/Schema/依赖，不恢复Legacy任务。禁止apply/删除/迁移/归档/GC/prune/push/强删/自动stash/修改ACL。STATUS/r212与全部资源保护不变。研究建议不授权修复，更不授权清理；不得把32errors当32独立资源或直接按source+destination双计资源。

## 测试要求

Windows PowerShell/Python -B。只读source字节/引用核验、原错误身份比较、HEAD/status/common-dir/count前后核对；运行pwsh -NoProfile -File tools/governance/check.ps1。可执行clean_workspace.py --audit-declarations --out本Task agent-output，只读审计不是清理PASS。产品/解析器回归NOT_RUN（无代码变更）；无fixtures/构建/安装。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|



|EV-1|AC4|verification/GOV-DECLARATION-RESIDUAL-32-AUDIT-1/.gitattributes|706e67adf0027e1a8691265808595866ea07edf7|fcf93454a24425f223b13f85d9edea5b763ea54ae818b87b4b7975f6b69f4b4c|SOURCE_PIN|
|EV-2|AC1|verification/GOV-DECLARATION-RESIDUAL-32-AUDIT-1/scope.json|706e67adf0027e1a8691265808595866ea07edf7|890a2e7edee5d8290b80c1852fd3f40195d92f1d0c4794df987abe110a80c35d|CANONICAL|
|EV-3|AC1/AC2|verification/GOV-DECLARATION-RESIDUAL-32-AUDIT-1/source-facts.json|706e67adf0027e1a8691265808595866ea07edf7|bcc6cd03e37111c6883f90f6fe1963b74a5eca97eda54aa3ee5b9e9a416d426b|CANONICAL|
|EV-4|AC2|verification/GOV-DECLARATION-RESIDUAL-32-AUDIT-1/direct-reference-facts.json|706e67adf0027e1a8691265808595866ea07edf7|d5143da8284b645aa7175b8cf7e1a3eed319da1f02c01d700cdf44c3afbebcac|CANONICAL|
|EV-5|AC1/AC2|verification/GOV-DECLARATION-RESIDUAL-32-AUDIT-1/matrix.json|706e67adf0027e1a8691265808595866ea07edf7|568c26d85be8e29a2e6350e0e47e4e89dc4bcfb7cadb5e997150c899642bc51e|CANONICAL|
|EV-6|AC2|verification/GOV-DECLARATION-RESIDUAL-32-AUDIT-1/matrix.md|706e67adf0027e1a8691265808595866ea07edf7|0e518c8bd57bcd21616ab0fb6b1f117f722a5a1bcbfee60dc3967b3944ecdd7a|CANONICAL|
|EV-7|AC3|verification/GOV-DECLARATION-RESIDUAL-32-AUDIT-1/preservation-validation.json|706e67adf0027e1a8691265808595866ea07edf7|6ba3c267b31fd8f5266caf0e259c01f1db8de97d23b80ade4e7c57a5f9249dd8|CANONICAL|
|EV-8|AC1/AC2/AC3|verification/GOV-DECLARATION-RESIDUAL-32-AUDIT-1/report.md|706e67adf0027e1a8691265808595866ea07edf7|a87567f4eb2fa480786f0e3dd144c68f601d03b9b0b0a9976409293f1cdac0c7|CANONICAL|
|EV-9|AC4|verification/GOV-DECLARATION-RESIDUAL-32-AUDIT-1/deepseek-review-r1.md|706e67adf0027e1a8691265808595866ea07edf7|7cdbd6070066129b6c2075000e23b905cc63e4fbae3a6873813500c80d5c43f5|SOURCE_PIN|
|EV-10|AC4|verification/GOV-DECLARATION-RESIDUAL-32-AUDIT-1/checkpoint.md|706e67adf0027e1a8691265808595866ea07edf7|dea0a1dbd3bf20e1a68284cba59a29b979ef42b50d8cb708ead430096325f042|SOURCE_PIN|
|EV-11|AC4|verification/GOV-DECLARATION-RESIDUAL-32-AUDIT-1/deepseek-review-r2.md|706e67adf0027e1a8691265808595866ea07edf7|f1dc9a6d1b8bffb76cc39ea9298cfe43ecaa0f16bfa6cdf4b530e02a480df581|CANONICAL|
|EV-12|AC4|verification/GOV-DECLARATION-RESIDUAL-32-AUDIT-1/resource-closeout.json|706e67adf0027e1a8691265808595866ea07edf7|7a1645c021efaf91f76237bb122a1decdf4909a3e79546f2b08d710f13424c64|CANONICAL|
|EV-13|AC3/AC4|verification/GOV-DECLARATION-RESIDUAL-32-AUDIT-1/integration-validation.json|706e67adf0027e1a8691265808595866ea07edf7|a10f765771b1717739dee2cdbbfeb746d9758259fb1b99a7da4fcbab832bf552|CANONICAL|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | G:/CODEX/New Manga.workspace/agent-output/codex/GOV-DECLARATION-RESIDUAL-32-AUDIT-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/agent-output/codex/GOV-DECLARATION-RESIDUAL-32-AUDIT-1 | doc/tasks/GOV-DECLARATION-RESIDUAL-32-AUDIT-1.md | 本Task派发/原始日志保留；不删除 |
| worktree/task-env/dataset/model/artifact/temp/exchange | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | 不新建；复用主仓库串行文档写入 |

## 运行记录

2026-10-21冻结ready；唯一Coordinator Codex epoch9，tracked dirty=0，common dir为权威仓库.git。历史未跟踪草稿原作者所有，不提交。后续精确证据与独审记录追加；不得自动启动修复。

## 交付记录

32项/17来源取证完成；六组为6/12/7/2/2/3。原raw SHA/status不变，原32完整错误身份多重集合不变，98heads/136worktrees；声明审计exit2为预期fail-closed，不写成清理PASS。初始观察对象导致4重复错误，已仅修本Task报告引用形式，原来源未变。固定证据 22bd5e07af5710af2359827a45fdf658186f578d；Handoff doc/handoffs/GOV-DECLARATION-RESIDUAL-32-AUDIT-1.md。DSH独审期间暂停写入被审文档；Reviewer只读，不申请租约/改ACL/修改任何文件。

## R1独审

DSH session-15d4c9be-21a7-4f1c-afa3-e9cd29af81a1，EXIT0，changes_requested，reviewed_head=f6184f3babf473d639932016fba328224e5d7fe6。P1为R24跟踪属性泛化措辞和NDJSON种类计数措辞；P2为checkpoint登记、初审失败输出证据数量/完整身份列表、共享用户数据源措辞。仅本Task文档修正，不改source/guard/旧pin。Reviewer实际核验来源与多项事实；其审计输出目录WinError5受阻，未当作Reviewer审计PASS。

R1五项修正完成，证据固定e2b8d19ed47a5ecde53d53f7fa17be6a2e10c29f；当前10行证据表均按Git blob原bytes与磁盘SHA核验，不存在名为“Task8”的独立文件（旧提示指Task中8行pin）。checkpoint已登记SOURCE_PIN并冻结本次恢复快照；终态另记closeout。下一Review只核定新固定head，R1保持changes_requested历史原文。

## R2独审与精确closeout范围

DSH同一session复审EXIT0，approved固定927e06f8b25563afbc7acbcc25d19fe775d1ded6；独立复算10pins和完整32身份/hash，R1已核验17来源等通过未变diff复用。R2未运行声明审计，不冒称Reviewer实测。唯一非阻塞P2是R1原文Markdown双空格触发diff-check exit2；按Review建议仅两份原文文件使用本Task局部-whitespace保留字节，源码/其它文件规则不变。

Codex明确追加closeout元数据范围：父Task仅追加本研究完成事实与推荐下一步、父rolling checkpoint更新当前恢复点；不修改父原AC/pin/历史证据或扩大R2批准范围。两路径已列allowed_paths，不属于17个只读来源，不申请清理授权。

## Closeout Record

2026-10-21 Codex：研究内容在main串行交付，集成点为独审批准927e06f8b；所有AC已通过，证据完整登记13项。R1原文保持changes_requested，R2 approved仅本研究切片；尾部元数据不扩大批准。17原source和逐源Git状态不变；收口审计exit2，原32错误完整身份相等。agent-output全部原位保留，其余派生类NOT_APPLICABLE；0删除/迁移/归档，98heads/136worktrees。canonical_evidence_status/resource_closeout_status=complete，资源保留核销不等于可删除。STATUS/Plan/导航返回父Task blocked，下一拟议Task见Handoff，未释放。

最终元数据核验：Windows PowerShell/Python -B，13pins raw磁盘=Git blob=SHA一致；pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/GOV-DECLARATION-RESIDUAL-32-AUDIT-1.md 与默认父Task检查均PASS（2 warnings，EXIT0）；git diff --check（base..HEAD及工作区）EXIT0。完整原始输出保留本Task agent-output/final-governance-validation.json；未把NOT_RUN产品/工具测试写为PASS。
