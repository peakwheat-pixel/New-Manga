---
id: GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1
title: 五项历史证据精确解释与原子保全实现
kind: implementation
governance_version: 3
status: changes_requested
approval: user_next_step_20261022
suggested_owner: Codex
owner: Codex
reviewer: DeepSeek Harness
depends_on: [GOV-HISTORICAL-EVIDENCE-INTERPRETATION-DESIGN-1]
base_commit: cc6387d660d6970c4e71c996f479e9e7c6af8674
branch: codex/gov-historical-evidence-interpretation-impl-1
worktree: G:/CODEX/New Manga.workspace/worktrees/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1
integration_commit: null
delivery_head: c4c44d4978c68879aed83537926ff184cd9ebb54
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
|EV-1|AC1/AC2/AC3/AC4|verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1/.gitattributes|c4c44d4978c68879aed83537926ff184cd9ebb54|705fd4d6451a31d36b3df7de96f83f30ac976c9b4a6d1e51671d8e2f33e2d0da|CANONICAL|
|EV-2|AC1/AC2/AC3/AC4|verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1/broad18.log|c4c44d4978c68879aed83537926ff184cd9ebb54|476ecdaadf4168603afdec48d525811c53339e5c3029bf47f397b3866baa2e85|CANONICAL|
|EV-3|AC1/AC2/AC3/AC4|verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1/candidate-audit.log|c4c44d4978c68879aed83537926ff184cd9ebb54|3b6bf0b3db4cb62c4baa0724da71a696ff4f83958f4e03617720a2547b8f64a2|CANONICAL|
|EV-4|AC1/AC2/AC3/AC4|verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1/candidate-clean.log|c4c44d4978c68879aed83537926ff184cd9ebb54|c90ffdbced9d296bf903cccf2be01772cca518e2bf0dc6df1945a8d3804c2989|CANONICAL|
|EV-5|AC1/AC2/AC3/AC4|verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1/candidate-effect.json|c4c44d4978c68879aed83537926ff184cd9ebb54|e4a806f360c3d4055bff9b2a18f44903f8bc81ce6ff085078a5d0b39aaa58893|CANONICAL|
|EV-6|AC1/AC2/AC3/AC4|verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1/candidate-remove.log|c4c44d4978c68879aed83537926ff184cd9ebb54|2a6332e2ae755dddc7b9888ba8f6204b8702dd3502088e50d8c8b3303669ada7|CANONICAL|
|EV-7|AC1/AC2/AC3/AC4|verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1/checkpoint.md|c4c44d4978c68879aed83537926ff184cd9ebb54|fb5d566e39abffe479dfbc789c014d181a59df18bec4d65e3c65246841306d48|CANONICAL|
|EV-8|AC1/AC2/AC3/AC4|verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1/clean-workspace-refused.json|c4c44d4978c68879aed83537926ff184cd9ebb54|d09fbe9a706a3c7c446ba08aeffb4e2127f60af9f12d70c0558490cd39b43fda|CANONICAL|
|EV-9|AC1/AC2/AC3/AC4|verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1/declaration-audit.json|c4c44d4978c68879aed83537926ff184cd9ebb54|f64f1b4ea59b821fd78a38d475aacf752eea22e55f6a71b2937fe54677fad4e0|CANONICAL|
|EV-10|AC1/AC2/AC3/AC4|verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1/declaration29.log|c4c44d4978c68879aed83537926ff184cd9ebb54|f2a79a50063aff42625d1f8024188b0901dab2e3e0d638b93cbd0468d604827a|CANONICAL|
|EV-11|AC1/AC2/AC3/AC4|verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1/execution.json|c4c44d4978c68879aed83537926ff184cd9ebb54|1df1e9b7bd66119e71db2067d5100a70042cf318e58c82c90e59c5b7cc1caa26|CANONICAL|
|EV-12|AC1/AC2/AC3/AC4|verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1/hardening80.log|c4c44d4978c68879aed83537926ff184cd9ebb54|97369d2758c1e3925ff3bce9eca2f150d0356be2f95978c032a0ea1e4a560fd3|CANONICAL|
|EV-13|AC1/AC2/AC3/AC4|verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1/incident-replay-clean.json|c4c44d4978c68879aed83537926ff184cd9ebb54|2d6c7073661f5ee5919076ddaf62aab3cc241db7187b6e851f9a868b6321151e|CANONICAL|
|EV-14|AC1/AC2/AC3/AC4|verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1/incident-replay-remove.json|c4c44d4978c68879aed83537926ff184cd9ebb54|71ee3cb80897076a50a8303664a75938e1e3c3b2697bad94f7f1a09b10303c89|CANONICAL|
|EV-15|AC1/AC2/AC3/AC4|verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1/new18.log|c4c44d4978c68879aed83537926ff184cd9ebb54|15ad054f9c18a4f22e5dcb56aadae92b36bdd7b42b055bc8950ce6d61aed98b4|CANONICAL|
|EV-16|AC1/AC2/AC3/AC4|verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1/replay-clean.log|c4c44d4978c68879aed83537926ff184cd9ebb54|505b0e9ce42b4f4818ce46620236293efc2a5ef4a6d342e793fef365644061de|CANONICAL|
|EV-17|AC1/AC2/AC3/AC4|verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1/replay-remove.log|c4c44d4978c68879aed83537926ff184cd9ebb54|a7cd2348cee14f881e3f08fc22b7c488ddb6b38f72ac3814aeea2748b7e09a11|CANONICAL|
|EV-18|AC1/AC2/AC3/AC4|verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1/report.md|c4c44d4978c68879aed83537926ff184cd9ebb54|92ef53f84f8d949e2dcf22655ae701071e9dc200f9412f9251e15eff22e4ef95|CANONICAL|
|EV-19|AC1/AC2/AC3/AC4|verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1/tests/test_historical_evidence.py|c4c44d4978c68879aed83537926ff184cd9ebb54|e38b8afe188f356aa9e28a754b0adbd3b3b81ff6bc5b3640acbfcc34a74f6b79|CANONICAL|
|EV-20|AC1/AC2/AC3/AC4|verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1/verify_effect.py|c4c44d4978c68879aed83537926ff184cd9ebb54|7325951fe184b4dbd64da01a5a4fc68b7ac5dbbb93ed8d82c768985414ed4e9f|CANONICAL|
|EV-21|AC1/AC2/AC3/AC4|verification/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1/worktree-removal-refused.json|c4c44d4978c68879aed83537926ff184cd9ebb54|bb1e48fc6369946a5970ae51ed2642b2fb82bea46f1444b973b5fda020da7863|CANONICAL|

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
