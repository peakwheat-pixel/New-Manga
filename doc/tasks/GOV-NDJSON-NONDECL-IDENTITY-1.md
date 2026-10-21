---
id: GOV-NDJSON-NONDECL-IDENTITY-1
title: 两份P02 NDJSON证据的非声明身份与精确例外适用性核验
kind: research
governance_version: 3
status: done
approval: user_continue_next_readonly_identity_verification_20261021
suggested_owner: Codex
owner: Codex
reviewer: DeepSeek Harness
latest_review: verification/GOV-NDJSON-NONDECL-IDENTITY-1/deepseek-review-r2.md
reviewed_head: 54cfbadad00071c70268ca557b1efcecbae87bf8
depends_on: [GOV-DECLARATION-RESIDUAL-32-AUDIT-1]
base_commit: 50d784300ac74d6ded633685bfce201cdddb630a
branch: main
worktree: G:/CODEX/New Manga
integration_commit: 54cfbadad00071c70268ca557b1efcecbae87bf8
delivery_head: 4bab91982fd05db85764705fef9d45fe92485501
canonical_evidence_status: complete
resource_closeout_status: complete
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

- [x] **AC1** 两日志raw SHA/Git状态、逐行JSON/完整消费、schema/kind种类和全部结构化声明身份键核验；如存在引用路径，区分日志指针与保护声明，不把格式有效当无声明。 <<MET>>
- [x] **AC2** 明确现有例外的精确path/hash/reason、加载/绕过时点和信任边界；候选匹配、不匹配路径、不匹配字节、无例外及变化后声明等负例有实际结果或明确NOT_RUN，不泛化坏JSON豁免。 <<MET>>
- [x] **AC3** 同数据快照正式32错误保留；候选若32→30只能移除R23/R24且旧保护集合不减少；原日志、正式例外表和guard字节/status前后不变。 <<MET>>
- [x] **AC4** 固定head独立DeepSeek Review、Codex裁定、Handoff/证据pin/保留资源核销和治理check完成；是否需后续写范围作出明确裁定。 <<MET>>

## 禁止范围

不改原日志/历史Task/source/pin、guard/正式例外表、共享接口/Schema/依赖、用户文件/DB/模型/ACL/租约/会话；不执行collector、构建、安装、apply、清理/迁移/归档/GC/prune/push/强删/自动stash。不释放Legacy任务。候选清单仅workspace分析输入，现有保护不解除；正式登记或代码修复必须另冻Task/allowed_paths并独审。父Task只允许closeout进展元数据追加，不改其原AC/pin。

## 验证计划

PowerShell/Python -B；只读标准库诊断与现有guard函数调用，不新增产品或guard源码测试。候选及负例输入留workspace；不创建第二项目仓库，不修改/删除真实资源。pythonic内存输入模拟须明确标记，不能冒充真实改名/编辑。产品/构建测试NOT_RUN（无代码变更），不以之替代机制正反例。运行pwsh -NoProfile -File tools/governance/check.ps1。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
|EV-1|AC1/AC2/AC3/AC4|verification/GOV-NDJSON-NONDECL-IDENTITY-1/.gitattributes|488ab6cbec7774df8c0c3b2e8a9e169750a92101|cb96a500d3bdb6d5602a449af7f58a3e21155e9e72bbbc1684c8002c3982bd8f|SOURCE_PIN|
|EV-2|AC1/AC2/AC3/AC4|verification/GOV-NDJSON-NONDECL-IDENTITY-1/checkpoint.md|488ab6cbec7774df8c0c3b2e8a9e169750a92101|8e497737ca6eb0cdf163a7787830c542cd554292f8788401e13e060ee5e63101|SOURCE_PIN|
|EV-3|AC1/AC2/AC3/AC4|verification/GOV-NDJSON-NONDECL-IDENTITY-1/identity-proof.json|488ab6cbec7774df8c0c3b2e8a9e169750a92101|07c82d93d1d8e407fa9ebce02dcc224ae17fff13e6cb6d1ac1a889c34b55f88c|CANONICAL|
|EV-4|AC1/AC2/AC3/AC4|verification/GOV-NDJSON-NONDECL-IDENTITY-1/manifest-provenance.json|488ab6cbec7774df8c0c3b2e8a9e169750a92101|0361cfbd12937b3dae8442b2bd58041d255f906a974ad12aedc53da56d3919e1|CANONICAL|
|EV-5|AC1/AC2/AC3/AC4|verification/GOV-NDJSON-NONDECL-IDENTITY-1/mechanism-proof.json|488ab6cbec7774df8c0c3b2e8a9e169750a92101|15f80f52a14362f1951312cd6c09d838d67210bbaf3657996dda941a5fb5e80a|CANONICAL|
|EV-6|AC1/AC2/AC3/AC4|verification/GOV-NDJSON-NONDECL-IDENTITY-1/probe-first-attempt.json|488ab6cbec7774df8c0c3b2e8a9e169750a92101|cf213021dec5b1b5c7928a221a7cfc6868b047e3bc4f52af006f799ed9dcf2f1|SOURCE_PIN|
|EV-7|AC1/AC2/AC3/AC4|verification/GOV-NDJSON-NONDECL-IDENTITY-1/probe-run.log|488ab6cbec7774df8c0c3b2e8a9e169750a92101|6e67271a07d0cfec2a0b518c75f3fa2dfc2742a3637075bb1beac70958a485e5|SOURCE_PIN|
|EV-8|AC1/AC2/AC3/AC4|verification/GOV-NDJSON-NONDECL-IDENTITY-1/probe-source.py.txt|488ab6cbec7774df8c0c3b2e8a9e169750a92101|6482b10b4626600236fdfedfa31f079abec43084a85676edcd40d69396c96bd5|SOURCE_PIN|
|EV-9|AC1/AC2/AC3/AC4|verification/GOV-NDJSON-NONDECL-IDENTITY-1/report.md|4bab91982fd05db85764705fef9d45fe92485501|49e3bd6af2f7edec0751741c239e8e9cbaca26f16d319d9d1cef4418b564c501|CANONICAL|
|EV-10|AC1/AC2/AC3/AC4|verification/GOV-NDJSON-NONDECL-IDENTITY-1/scope.json|488ab6cbec7774df8c0c3b2e8a9e169750a92101|2cba2846d3f7fc52f2a5781535f8728adacb6845b04072a3975d6884f5710aa6|CANONICAL|
|EV-11|AC4|verification/GOV-NDJSON-NONDECL-IDENTITY-1/deepseek-review-r1.md|4bab91982fd05db85764705fef9d45fe92485501|c6e1688d788e3975804f3c24e3807691a303e9e99861f1831cb251a5c767a107|SOURCE_PIN|
|EV-12|AC4|verification/GOV-NDJSON-NONDECL-IDENTITY-1/table-registration-proof.json|4bab91982fd05db85764705fef9d45fe92485501|c9c0684ba297dba15f9e6e6811d28cbfce7f66227a5594a613d923b32ae2fc55|SOURCE_PIN|
|EV-13|AC4|verification/GOV-NDJSON-NONDECL-IDENTITY-1/checkpoint-r2.md|4bab91982fd05db85764705fef9d45fe92485501|3f1ea3dec7250dbaaf1bb589c7583b0434c8b16e40d0e98534a7fe6a6158bb60|SOURCE_PIN|
|EV-14|AC3/AC4|verification/GOV-NDJSON-NONDECL-IDENTITY-1/deepseek-review-r2.md|2b291ecd0a9cea03ed672faea49224064c6f5f07|794794b2dbc9c09536bdfbffba1203c1e336b7cecd506a22565d6782c00e2efc|CANONICAL|
|EV-15|AC3/AC4|verification/GOV-NDJSON-NONDECL-IDENTITY-1/closeout-validation.json|2b291ecd0a9cea03ed672faea49224064c6f5f07|9601b015e2d5863fd2d3a4498fb27503d86c2732780935a4e92a7e720de5e1c6|CANONICAL|
|EV-16|AC3/AC4|verification/GOV-NDJSON-NONDECL-IDENTITY-1/resource-closeout.json|2b291ecd0a9cea03ed672faea49224064c6f5f07|c0b526512b1c6a21256740dcdf3f36b85b81ad7442b4e1e55db19f489a209489|CANONICAL|
|EV-17|AC3/AC4|verification/GOV-NDJSON-NONDECL-IDENTITY-1/closeout-record.md|2b291ecd0a9cea03ed672faea49224064c6f5f07|62a9ff82de4e3b8d6bb26343da62faf9b1c4b71719b776ac7d00163639ac60b0|CANONICAL|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | G:/CODEX/New Manga.workspace/agent-output/codex/GOV-NDJSON-NONDECL-IDENTITY-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/agent-output/codex/GOV-NDJSON-NONDECL-IDENTITY-1 | doc/tasks/GOV-NDJSON-NONDECL-IDENTITY-1.md | 候选输入/负例/原始派发输出保留，不写正式例外表 |
| worktree/task-env/dataset/model/build/temp/exchange | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | 无新建，不删除其它资源 |
| original-evidence-log | G:/CODEX/New Manga/verification/P02-NEW-TIME-BASELINE/run-baseline-20261014T0430CST-ac3fix.json | PRESERVE_REFERENCED | G:/CODEX/New Manga/verification/P02-NEW-TIME-BASELINE/run-baseline-20261014T0430CST-ac3fix.json | bdabb170f9a415dd42855a0978fe557cae4ca1df97466ca143750b1ae288f7a1 | 原始证据保持原路径/字节；R23未跟踪不提交，R24跟踪不改写；候选例外不解除保留 |
| original-evidence-log | G:/CODEX/New Manga/verification/P02-NEW-TIME-BASELINE/run-baseline-20261014T0915CST-p02-admission-r2.json | PRESERVE_REFERENCED | G:/CODEX/New Manga/verification/P02-NEW-TIME-BASELINE/run-baseline-20261014T0915CST-p02-admission-r2.json | caac6afde8d479cabcd839e2b74fdd86a1ecd8b59e5e8c88100a552382a9458e | 原始证据保持原路径/字节；R23未跟踪不提交，R24跟踪不改写；候选例外不解除保留 |

## 运行记录

ready冻结后认领；Reviewer只读，审查期间Owner暂停被审文档写入。研究与候选输入不等于实际例外登记。Handoff/Review待交付。

两原始日志显式列为本Task保留证据：非声明分类只讨论保护解析Schema，不取消其历史证据价值或内部引用；不因候选例外而允许删除日志或其引用对象。

## 交付记录

证据488ab6cbec7774df8c0c3b2e8a9e169750a92101：NDJSON共6/64值、种类1/4/1及1/62/1，实际当前声明parser均0；6候选/负例EXIT0，正式默认32身份完整保留，候选仅消两项32→30、原保护集合不减，98heads/136worktrees。正式表是旧Canonical Evidence；磁盘CRLF与历史Git blob hash区分，禁止原地更新。未来最小写范围为新当前配置+默认常量，未释放。审查期间暂停被审文档写入。

## R1独审

DSH session-d43a0051-1d57-4657-a4c3-fabe4adcbb5d，EXIT0，changes_requested固定3ff9dba39694751a72fd1a67380757041cd7dc08。主体身份、6cases、默认32/候选30、旧表pin边界已独立重算通过；阻断为本Task Canonical Evidence表空行导致10行pin未被guard注册。只修自有表格结构/恢复指针，不改guard或源。

R1精确修正：证据表及原日志Manifest现在连续，实际parser已验证；原9份未变EV内容/commit/SHA保持不动，仅本Task report更正其旧保护快照说明后更新自身新版本pin。旧checkpoint.md原字节不动、保留历史SOURCE_PIN，当前恢复点改为新checkpoint-r2.md。新增R1原文/注册证明/当前checkpoint已登记。未修改原日志/guard/正式表或已关闭Task。

## R2批准

DSH session-d43a0051-1d57-4657-a4c3-fabe4adcbb5d，R1/R2 EXIT0；R2 approved固定54cfbadad00071c70268ca557b1efcecbae87bf8，实际13pins/原日志保留2、默认32身份完整保留、1704旧保护根全部在1718集合内。仅本只读研究和本Task格式/恢复指针修正获批；两后续Task均未释放。

## 终态核销

2026-10-21 Codex：R2批准固定54cfbadad；本Task done。AC1-3证据与R1独立实测、AC4 R2实际保护注册/原pin复算/治理检查/Handoff/保留资源闭环。17项自有证据全部登记；保持连续Markdown表，不以check PASS代替实际注册。原13项证据文件不改字节，新4项收口证据追加。两旧checkpoint都是已冻结历史SOURCE_PIN；STATUS恢复父Task当前checkpoint。0正式例外登记、0删除/迁移/归档，98heads/136worktrees，正式32错误与清理禁令保留。下一优先GOV-EVIDENCE-TABLE-REGISTRATION-FIX-1尚未释放，后续配置迁移也未释放。

最终实际核验（PowerShell/Python -B）：17条pin原始磁盘=Git blob=SHA一致；本Task实际parser注册17 EVIDENCE_PIN、2原日志PRESERVE_REFERENCED、0错误；默认32完整错误身份保留，R2的1718保护根全部保留并增为1722（新增4收口pin）。子Task及默认父Task governance check均PASS/2 warnings/EXIT0，diff-check EXIT0。原始收口输出在workspace本Task final-registration-validation.json；不是仅检查Markdown行数。产品/构建NOT_RUN，无配置/guard实现或正式例外登记变化。
