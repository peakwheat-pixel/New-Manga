---
id: GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1
title: 五项历史证据精确解释与原子保全实现
kind: implementation
governance_version: 3
status: in_review
approval: user_next_step_20261022
suggested_owner: Codex
owner: Codex
reviewer: DeepSeek Harness
depends_on: [GOV-HISTORICAL-EVIDENCE-INTERPRETATION-DESIGN-1]
base_commit: cc6387d660d6970c4e71c996f479e9e7c6af8674
branch: codex/gov-historical-evidence-interpretation-impl-1
worktree: G:/CODEX/New Manga.workspace/worktrees/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1
integration_commit: null
delivery_head: bb769d273f18ff895c72244558645fed167a81f8
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1
allowed_paths:
  - tools/governance/clean_workspace.py
  - tools/governance/historical-evidence-interpretation.json
  - verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1
  - doc/tasks/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1.md
  - doc/handoffs/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/tasks/README.md
  - verification/GIT-MAINLINE-CONVERGENCE-1/checkpoint.md
---

# 五项历史证据精确解释与原子保全实现

## 来源与冻结范围

用户2026-10-22“下一步”承接已done设计R2 e6f400101/集成20dff6381。Codex实施共享scanner尾部及新policy，DeepSeek Harness固定head独审。冻结设计design.md、binding-specimen.json及R2；批准样本canonical SHA-256为3f4cae13b0848ed105b5ba59c7538c8456c991b1403596ca64b68b63381e4b7d。无通用忽略/生产开关；共享reader、三消费者、69例外、旧源/Task/Review/pin及产品代码不改。原四源逐字节保留，P22仍untracked，line227既有保护及末检不减，六旧探针不触碰。

前置broad有效性按六binding乘source/destination共12角色精确验证。Declaration六字段逐项等于root_abs/相应source_keep或DESTINATION_PIN/origin_file/parser_locator/root_normalized/root_real_expected；warning完整四字段等于现有helper构造的role/policy/origin/locator/root/source_keep消息。每项恰一次、marker集合恰12且五根受保护；两源总83声明不能用作12的替代。broad fatal原样返回，自己absent+untracked no-op，自己enabled但依赖no-op则DEPENDENCY_INACTIVE，原错全留。

允许自身E、新policy及本Task/Handoff镜像并track在canonical以供候选工具使用；正式代码合并前仍报告旧scanner12。允许仅在自有agent-output/test-temp内创建Git合成fixture并自清，递归删除前断言resolved目标严格位于该根；这是合成测试权限，不解除任何真实资源保护。每套测试独立TMP/TEMP，Python -B/UTF8。禁止reset/clean/强删/GC/prune/push/真实apply/迁移/归档/ACL/安装/Legacy；r212、五广域根及父blocked保持。

## Acceptance Criteria

- [x] **AC1** 精确policy与单共享尾部原子helper，四源五错及+6声明/+4warning；原字节/保护/其它错误不变。 <<MET>>
- [x] **AC2** T01–T18至少18新测试及旧127合计至少145 passed/0 skipped；双事故回放各15REJECT/0deleted/0violations。 <<MET>>
- [x] **AC3** 同canonical候选12→7，五完整错误移除/其余7身份不变，原保护子集及四源SHA保持；三合成CLI共享拒绝、正式清理继续拒绝。 <<MET>>
- [ ] **AC4** DeepSeek固定head独审、正常merge和main复验；EV raw/blob/pin及实际注册、check/diff、资源原位核销和权威导航一致。 <<PARTIAL: 待独审集成>>

## 验证计划

planned：新Task tests unittest discover；前置broad18、declaration29、hardening80；双--replay-incident；candidate/main只读scan与CLI audit/refuse；check.ps1显式Task与默认、git diff --check。产品测试/全资源consolidate/句柄扫描NOT_RUN（无产品或真实处置）。DeepSeek零文件写/stdout，禁temp/probe/fixture/ACL；沙箱不能复跑fixture须记NOT_RUN，以Owner实际日志及独立内存验证审查。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
|EV-1|AC1/AC2/AC3/AC4|verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1/.gitattributes|bb769d273f18ff895c72244558645fed167a81f8|705fd4d6451a31d36b3df7de96f83f30ac976c9b4a6d1e51671d8e2f33e2d0da|CANONICAL|
|EV-2|AC1/AC2/AC3/AC4|verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1/broad18.log|bb769d273f18ff895c72244558645fed167a81f8|ac95fcba00eabf5d474301161664a92ffa984b5ff62b6fb06e93cf35e125ec37|CANONICAL|
|EV-3|AC1/AC2/AC3/AC4|verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1/candidate-audit.log|bb769d273f18ff895c72244558645fed167a81f8|ef15d8c4461428486d19d9c11717cb981578b4d6ff931a524c8cbf72fc166d99|CANONICAL|
|EV-4|AC1/AC2/AC3/AC4|verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1/candidate-clean.log|bb769d273f18ff895c72244558645fed167a81f8|c90ffdbced9d296bf903cccf2be01772cca518e2bf0dc6df1945a8d3804c2989|CANONICAL|
|EV-5|AC1/AC2/AC3/AC4|verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1/candidate-effect.json|bb769d273f18ff895c72244558645fed167a81f8|e4a806f360c3d4055bff9b2a18f44903f8bc81ce6ff085078a5d0b39aaa58893|CANONICAL|
|EV-6|AC1/AC2/AC3/AC4|verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1/candidate-remove.log|bb769d273f18ff895c72244558645fed167a81f8|2a6332e2ae755dddc7b9888ba8f6204b8702dd3502088e50d8c8b3303669ada7|CANONICAL|
|EV-7|AC1/AC2/AC3/AC4|verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1/checkpoint.md|bb769d273f18ff895c72244558645fed167a81f8|2493e68afe434d14cf56d11619ef35960c105b53ce0dd2fb04e8dd704b8e7cdb|CANONICAL|
|EV-8|AC1/AC2/AC3/AC4|verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1/clean-workspace-refused.json|bb769d273f18ff895c72244558645fed167a81f8|5ffadaeb729a542d66c3bbaebd831ef6a6046bc17406ca344057b7324f68a5e5|CANONICAL|
|EV-9|AC1/AC2/AC3/AC4|verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1/declaration-audit.json|bb769d273f18ff895c72244558645fed167a81f8|b0469f5383b8be86b78e184594746791629c8b0dbd7b0cbc54738b3ca4f0863e|CANONICAL|
|EV-10|AC1/AC2/AC3/AC4|verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1/declaration29.log|bb769d273f18ff895c72244558645fed167a81f8|ad7042580129b9d3abca3f480004c5d8a2ec8b7f4ba2d8b331ad2b2ad826ef29|CANONICAL|
|EV-11|AC1/AC2/AC3/AC4|verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1/deepseek-review-r1.md|bb769d273f18ff895c72244558645fed167a81f8|c77fe418c2485e88498fee7fb0b214f45c096890c737f5a4fe438ac200789f95|CANONICAL|
|EV-12|AC1/AC2/AC3/AC4|verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1/execution.json|bb769d273f18ff895c72244558645fed167a81f8|2b77a1bbdaf469a5330e5a7d83619c18eae513215c95e5ec9bf38c055d3ba94e|CANONICAL|
|EV-13|AC1/AC2/AC3/AC4|verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1/hardening80.log|bb769d273f18ff895c72244558645fed167a81f8|c1e8e8eb43a759cba42b93bbd491d4d6babc5c2b3926ec1deb6dc7833e954ceb|CANONICAL|
|EV-14|AC1/AC2/AC3/AC4|verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1/incident-replay-clean.json|bb769d273f18ff895c72244558645fed167a81f8|e602962625031a9c5840f6fdb8a6c1d82eb9b1936fd8e23f0224a4e291adf8e0|CANONICAL|
|EV-15|AC1/AC2/AC3/AC4|verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1/incident-replay-remove.json|bb769d273f18ff895c72244558645fed167a81f8|78400a8f097b7f57e7a718ba5b1c90661f666ea1974ff2f0c226a241cd1e1f4c|CANONICAL|
|EV-16|AC1/AC2/AC3/AC4|verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1/new18.log|bb769d273f18ff895c72244558645fed167a81f8|1a44e343d89eb4a454540ea7092f38d267f008b5ce8ea86bd9f7f1397f372ccf|CANONICAL|
|EV-17|AC1/AC2/AC3/AC4|verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1/r2-negative-control.json|bb769d273f18ff895c72244558645fed167a81f8|03c351a616f55822690fcbe69fc468c58d6f625cd6c245d335358e86c1f2a9a8|CANONICAL|
|EV-18|AC1/AC2/AC3/AC4|verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1/r2-validation.json|bb769d273f18ff895c72244558645fed167a81f8|76c73a9c61b481f0c99466921ef0866703c1745e62638ec3325ae5955166ea96|CANONICAL|
|EV-19|AC1/AC2/AC3/AC4|verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1/r2_negative_control.py|bb769d273f18ff895c72244558645fed167a81f8|67f51e08486b83bafe3ee2f1e64fb14df343b1cdf971befde340d0d74e24f0eb|CANONICAL|
|EV-20|AC1/AC2/AC3/AC4|verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1/replay-clean.log|bb769d273f18ff895c72244558645fed167a81f8|505b0e9ce42b4f4818ce46620236293efc2a5ef4a6d342e793fef365644061de|CANONICAL|
|EV-21|AC1/AC2/AC3/AC4|verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1/replay-remove.log|bb769d273f18ff895c72244558645fed167a81f8|a7cd2348cee14f881e3f08fc22b7c488ddb6b38f72ac3814aeea2748b7e09a11|CANONICAL|
|EV-22|AC1/AC2/AC3/AC4|verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1/report.md|bb769d273f18ff895c72244558645fed167a81f8|b6d3e69c1374fd8292a374869387dddf88c3309686db17ee8ce99aaa1f0b5a63|CANONICAL|
|EV-23|AC1/AC2/AC3/AC4|verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1/tests/test_historical_evidence.py|bb769d273f18ff895c72244558645fed167a81f8|6eb13c4ad1635f254326801c4e22b1026044f2b141d67b5fcc1e6ddf21815bf4|CANONICAL|
|EV-24|AC1/AC2/AC3/AC4|verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1/verify_effect.py|bb769d273f18ff895c72244558645fed167a81f8|7325951fe184b4dbd64da01a5a4fc68b7ac5dbbb93ed8d82c768985414ed4e9f|CANONICAL|
|EV-25|AC1/AC2/AC3/AC4|verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1/worktree-removal-refused.json|bb769d273f18ff895c72244558645fed167a81f8|33289f179246c74f71cb63080399b28405c860b172874373b8a6d93c21ee599b|CANONICAL|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1 | doc/tasks/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1.md | 本Task独占；原位保留 |
| agent-output/test-temp | G:/CODEX/New Manga.workspace/agent-output/codex/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/agent-output/codex/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1 | doc/tasks/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1.md | 日志保留；仅自有合成fixture可自清 |

## 运行记录

Reality Check：main cc6387d660d6970c4e71c996f479e9e7c6af8674 tracked clean，common G:/CODEX/New Manga/.git；Codex epoch9租约有效，RESUME_SAFE。来源base与实际创建base分记；当前102heads/140WT，创建后预计103/141。正式12错误；父blocked、尚未只剩main。

实际创建base d760caeb6；交付c4c44d4978c68879aed83537926ff184cd9ebb54；145 passed/0 skipped，双回放各15REJECT/0deleted/0violations，候选真实12→7/+6/+4且原1895保护根全集保持；正式main尚12。固定head待DeepSeek独审，未审核自己的实现。

## R1 裁决与修订范围冻结

DeepSeek R1 changes_requested固定090bed6f6，P1-1引用目录发布末检存在性/类型缺失，禁止merge。Codex在原共享seam范围修复：发布前对两个reference目录再次验证lexists+isdir，补T15验证后删除/替换为文件的全容器回滚；不增加声明或改变+6/+4。同时冻结前置broad当前已批准配置canonical SHA-256 0d19cd0fa0374b7970a128d7af845541efd4c86e14b158bd6185dbbc261708b3，在本helper内作依赖摘要校验；不改broad配置/helper、不缩小保护，不增加生产开关；合成fixture仅内存mock该常量。
R1 P2时点：1895为本Task EV登记前的原保护集合快照；21EV后实时保护1916，新增EV不会使原集合失保，后续计数随证据变化。line227契约仍是原完整Declaration/lexical与real保护+最终real身份复核；不追溯增加目录存在性/类型合同，也不赋予退出权限。两个新增reference目录是本Task明确存在/目录类型/real合同，必须末检。修订后全145/0、双回放与同数据候选复验，固定新head交DeepSeek R2。

R2交付bb769d273f18ff895c72244558645fed167a81f8；P1-1及P2处置见R1裁决/本轮report/negative-control，生产修订后完整145/0及双15/0/0已重跑，真实候选12→7保持；固定新head待DeepSeek R2，不合并未批准版本。
