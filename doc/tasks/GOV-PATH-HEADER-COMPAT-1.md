---
id: GOV-PATH-HEADER-COMPAT-1
title: 固定模板路径列表头兼容，保留所有 fail-closed 门槛
kind: governance-hardening
governance_version: 3
status: done
approval: codex_scoped_technical_followup_user_boundary_continuation_20261021
suggested_owner: Codex
owner: Codex
reviewer: DeepSeek Harness
latest_review: verification/GOV-PATH-HEADER-COMPAT-1/deepseek-review-r2.md
reviewed_head: 78fc0cba26d0f52f3bb86014076039c0212dd4f0
depends_on: [WORKSPACE-DECLARATION-REMEDIATION-1]
base_commit: e7cbcada6d1a5c01f9c55e888e30c3efba20e1ff
branch: codex/gov-path-header-compat-1
worktree: G:/CODEX/New Manga.workspace/worktrees/GOV-PATH-HEADER-COMPAT-1
integration_commit: 9cae94142a51ee104dea19714568d3fe2b89dad0
delivery_head: 78fc0cba26d0f52f3bb86014076039c0212dd4f0
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/GOV-PATH-HEADER-COMPAT-1
allowed_paths:
  - tools/governance/clean_workspace.py
  - tools/governance/tests/test_path_header_compat.py
  - doc/tasks/GOV-PATH-HEADER-COMPAT-1.md
  - verification/GOV-PATH-HEADER-COMPAT-1
  - doc/handoffs/GOV-PATH-HEADER-COMPAT-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/tasks/README.md
created: 2026-10-21
---

# GOV-PATH-HEADER-COMPAT-1

## 来源与范围冻结

创建时来源基线为 frontmatter 的 base_commit（e7cbcada6）；实际工作树及审查 diff 基线为 93c4eb2ca。两者之间仅本 Task 的释放与认领元数据，无产品代码差异。

用户要求先明确保护与独有支线边界，再由Codex继续，并保留现有清理禁令。Codex技术裁定见 verification/GIT-MAINLINE-CONVERGENCE-1/boundary-adjudication.md（边界证据 e7cbcada6）。全部现有分支/工作树继续保留；P14/P22仅作为未来只读评估候选；不释放任何产品实现或处置窗口。

本Task仅改变共享保护解析器对**一个完整固定表头字面量**的兼容策略：把模板已有的 `path（仓库相对路径或绝对路径）` 识别为 `path`，同时在重复身份列检查使用同一归一化。原规则的English-only限制在本Task精确范围内由Codex明确修订，不能据此扩展任意中文/模糊别名。重复列、缺列、malformed表、未知disposition、JSON损坏、不可读、模糊/环境路径仍fail-closed。

内存模拟（非实现批准）为77→32 errors，保护根1277→1687，旧集合子集成立，新增410根。已完成相关影响全集与边界核验，满足协议§4.4；真实实现仍需同快照复测与独立Review。只使用既有stdlib，无新依赖/契约/Schema/API变更；旧Task/证据/pin文件不编辑。

## Acceptance Criteria

- [x] **AC1** 完整固定别名和原始path列都识别，真实Canonical Evidence行被保护。 <<MET>>
- [x] **AC2** alias+path、alias+alias重复列拒绝；其它说明/别名/缺列/malformed不接受或保持原判定，未知disposition等安全门槛不变。 <<MET>>
- [x] **AC3** 同一main数据快照用原实现和候选实现审计，45个schema错误消解、其余32保留，原保护根不丢失，新增根可复算；不调用apply。 <<MET>>
- [x] **AC4** 既有声明/安全回归和incident replay通过，记录shell/interpreter/EXIT与skips；固定head独立Review。 <<MET>>
- [x] **AC5** Codex集成后复验、Handoff与资源清册闭环；父Task继续blocked，不解除禁令、不宣称只有main。 <<MET>>

## 禁止范围

不修改历史Task、原始evidence/pin/JSON例外清单；不扩大列名/路径/JSON/disposition语义；不apply、不删/迁移/归档真实资源，不强删分支、不GC/prune/push/reset/stash。新Task工作树/分支与所有派生产物保留，不能为了收口绕过父禁令。只允许既有测试在本Task隔离temp内创建及清理测试自有夹具；不得触碰真实用户资源，不能对canonical repo执行删除工具apply。

## 测试要求

计划：python -B -m unittest discover -s tools/governance/tests -p test_path_header_compat.py；既有29声明测试与80安全测试；真实只读before/after审计；incident replay。TMP/TEMP隔离 G:/CODEX/New Manga.workspace/temp/GOV-PATH-HEADER-COMPAT-1。实际命令、结果与skip理由按执行追加。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
|EV-1|AC1/AC2|verification/GOV-PATH-HEADER-COMPAT-1/new-tests.log|9f59537f989299c4ee6f41993134aa69d6cfbc12|d6d3a0bd38fc02f22fb40ef68ba328cfb6b86406f324d2bef3540372fa382344|CANONICAL|
|EV-2|AC2/AC4|verification/GOV-PATH-HEADER-COMPAT-1/declaration-tests.log|9f59537f989299c4ee6f41993134aa69d6cfbc12|6acac17af39688b225c56ef2923f196cf748d8202a26db25d9cd0847dbd0e4c1|CANONICAL|
|EV-3|AC2/AC4|verification/GOV-PATH-HEADER-COMPAT-1/hardening-tests.log|9f59537f989299c4ee6f41993134aa69d6cfbc12|aba565751ae78fa020c488bb469d2c90dcc6906d1a0c2ababeb72ca655204da5|CANONICAL|
|EV-4|AC3|verification/GOV-PATH-HEADER-COMPAT-1/real-comparison.json|9f59537f989299c4ee6f41993134aa69d6cfbc12|df0824fce7ae4b2e30ddf32bf16a1be73333ec00fd621c85be53131a4fc43937|CANONICAL|
|EV-5|AC1/AC2|verification/GOV-PATH-HEADER-COMPAT-1/baseline-discriminator.log|9f59537f989299c4ee6f41993134aa69d6cfbc12|0b8e8fa819b1af22e30c153e53adc07c12c5ea8bd5000c6cbd63a57527d31548|CANONICAL|
|EV-6|AC4|verification/GOV-PATH-HEADER-COMPAT-1/incident-replay-clean-workspace.json|9f59537f989299c4ee6f41993134aa69d6cfbc12|cbcfcd1b78d0c0eeffb6322e8b67ce1c2dce3ec070fac7b0d2a0177f4cbf19fb|CANONICAL|
|EV-7|AC4|verification/GOV-PATH-HEADER-COMPAT-1/incident-replay-remove-worktrees.json|9f59537f989299c4ee6f41993134aa69d6cfbc12|63f296b126ba1d13edf44694bd3936f1f060a517d597aa1ba8a2b08d9c3fbaac|CANONICAL|
|EV-8|AC4|verification/GOV-PATH-HEADER-COMPAT-1/replay-clean-executed.log|9f59537f989299c4ee6f41993134aa69d6cfbc12|33de0b51fc7ae4f7b7896029bb0772cea520505ffb74e6e5d388dbbfb5dfc6f8|SOURCE_PIN|
|EV-9|AC4|verification/GOV-PATH-HEADER-COMPAT-1/replay-worktrees-executed.log|9f59537f989299c4ee6f41993134aa69d6cfbc12|54155be6a1a23a8b6a7e92b5d2b1c277ae022ed6e52b4ae067ca600511b29b3e|SOURCE_PIN|
|EV-10|AC4|verification/GOV-PATH-HEADER-COMPAT-1/replay-clean.log|9f59537f989299c4ee6f41993134aa69d6cfbc12|aece49f317b301935566f8f3ee3e6426d0c708adfe6052e81cf69743a614b8dd|SOURCE_PIN|
|EV-11|AC1/AC2/AC3/AC4|verification/GOV-PATH-HEADER-COMPAT-1/report.md|9f59537f989299c4ee6f41993134aa69d6cfbc12|5521c7826f770070ffa24d80c3e5dcd4cb55a1bb09fcf29c29a18d6f263b512d|CANONICAL|
|EV-12|AC5|verification/GOV-PATH-HEADER-COMPAT-1/.gitattributes|9ea78f1aac5c4f9838745d4ef8e3b0aa988fbc26|a00748782874dff77c1533a093b13c8cdeb02afb5d9280446b2fd22548185a28|SOURCE_PIN|

|EV-13|AC4|verification/GOV-PATH-HEADER-COMPAT-1/deepseek-review-r2.md|167552efcaf01a883e9a01fea815c8c814868d6a|afc5fe4e76a89e6abdc59955e71c110e22710353a5b8159c8ab3ca40220b5895|CANONICAL|
|EV-14|AC4|verification/GOV-PATH-HEADER-COMPAT-1/review-r2-owner-verification.json|167552efcaf01a883e9a01fea815c8c814868d6a|e85a6be3f8ac4c36e9e156114344101763dc4a7a38fe39fcaffabcc829293c9a|SOURCE_PIN|
|EV-15|AC5|verification/GOV-PATH-HEADER-COMPAT-1/postintegration-validation.json|63446b22eb9b2d349218b2d238fd2ddc525a8d0f|05c2da38159a12a03e0e7e4c635aba2d9de3bef0a80b3fc5980fb3df4a109e58|CANONICAL|
|EV-16|AC3/AC5|verification/GOV-PATH-HEADER-COMPAT-1/postintegration-declaration-audit.json|63446b22eb9b2d349218b2d238fd2ddc525a8d0f|96e8451431edd8a72b02030a12917a16b6c9c014663581550cf43dc9a3470e27|CANONICAL|
|EV-17|AC5|verification/GOV-PATH-HEADER-COMPAT-1/resource-closeout.json|63446b22eb9b2d349218b2d238fd2ddc525a8d0f|0908b9ebc77049a41cc93815de53640823396bc84f10b1b1409bda5b314fdcb1|CANONICAL|

|EV-18|AC4/AC5|verification/GOV-PATH-HEADER-COMPAT-1/deepseek-review.md|167552efcaf01a883e9a01fea815c8c814868d6a|81103ad29a9568ecd5f8957d7893f2f0bd27bcf2ce91329711ba9cf7b4355d15|SOURCE_PIN|
|EV-19|AC4/AC5|verification/GOV-PATH-HEADER-COMPAT-1/checkpoint.md|2f4727c821831ea5edd7b5bfcb0a1c1d9f1cf65e|aca1f19dd2a8b2d43a27a02add0c7940234115230c0feddcae58ba962e9ddbce|SOURCE_PIN|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/GOV-PATH-HEADER-COMPAT-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/GOV-PATH-HEADER-COMPAT-1 | doc/tasks/GOV-PATH-HEADER-COMPAT-1.md | 已创建，b26b60ca6，tracked/untracked状态空；父禁令有效，分支/工作树原位保留 |
| agent-output | G:/CODEX/New Manga.workspace/agent-output/codex/GOV-PATH-HEADER-COMPAT-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/agent-output/codex/GOV-PATH-HEADER-COMPAT-1 | doc/tasks/GOV-PATH-HEADER-COMPAT-1.md | 本Task日志/原始对照，保留 |
| temp | G:/CODEX/New Manga.workspace/temp/GOV-PATH-HEADER-COMPAT-1 | PRESERVE_UNKNOWN | G:/CODEX/New Manga.workspace/temp/GOV-PATH-HEADER-COMPAT-1 | doc/tasks/GOV-PATH-HEADER-COMPAT-1.md | 仅自有测试夹具；结束残余保留，不清理真实项目资源 |

## 运行记录

先ready冻结，再Owner认领。Handoff/Review尚无；只释放本精确技术前置，不改变完整收敛Task的blocked状态。

## 交付记录

固定实现与证据 9f59537f989299c4ee6f41993134aa69d6cfbc12；5新增+29声明+80安全测试通过、0skip；baseline判别预期exit1；双incident replay各15/15拒绝、0删除；同快照77→32，1280旧根全部保留并新增410。源helper/code未在main实施。工作树已创建且按清理禁令保留；临时测试自有夹具由test cleanup回收，剩余temp根保留。Handoff在Review/集成后追加。

原始判别失败日志含unittest固有尾随空格；仅对该日志设置局部-whitespace，保留原始输出，不更改源码或其它文件的检查规则。工作树Owner更新Task副本；canonical治理由main现有epoch9 gate串行同步，不复制/分叉runtime租约。

## Review 裁定与记录修正

DSH R2 session-90adda56-6155-4d06-95df-667579988499，EXIT0，approved 固定78fc0cba26d0f52f3bb86014076039c0212dd4f0；仅精确代码集成，不批准清理/父Task done。R1因工作树shell ACL受阻未批准，R2从canonical root完成Git检查；测试和12pin字节校验为Owner实测，独审未冒称重跑。

P2记录闭环：delivery_head更新为实际审查head；EV12源提交9ea78f1aa正确（git log -- .gitattributes可核验），1a958d770只修改Task的pin，并未修改属性文件，不伪造迁移来源。前置内存模拟1277→1687，实际冻结Task增加三个资源根后同快照实测1280→1690；两者旧根全部保留且均+410，不混用绝对快照值。

## 集成与终态核销

main集成 9cae94142a51ee104dea19714568d3fe2b89dad0，主线5测试exit0、diff-check exit0；声明审计exit2并保留32项致命错误，类别与原32项一致，保护根1702为新增证据后的快照。全部已释放AC通过；独审未授权资源清理。资源逐项保留已核销（resource-closeout.json）；不以删除作为done条件。Handoff：[交付及下一任务建议](../handoffs/GOV-PATH-HEADER-COMPAT-1.md)。父收敛继续blocked；98 heads/136 worktrees，尚未达到只剩main。

治理元数据检查曾报告台账14→13未刷新及终态目录2个未登记文件，已用既有task_ledger生成器刷新并为R1原文/冻结checkpoint登记SOURCE_PIN。台账不在租约helper的canonical受控目标集合，使用项目规定生成器，无扩大租约或修改scope。
