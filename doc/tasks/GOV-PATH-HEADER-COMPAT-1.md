---
id: GOV-PATH-HEADER-COMPAT-1
title: 固定模板路径列表头兼容，保留所有 fail-closed 门槛
kind: governance-hardening
governance_version: 3
status: in_review
approval: codex_scoped_technical_followup_user_boundary_continuation_20261021
suggested_owner: Codex
owner: Codex
reviewer: DeepSeek Harness
depends_on: [WORKSPACE-DECLARATION-REMEDIATION-1]
base_commit: e7cbcada6d1a5c01f9c55e888e30c3efba20e1ff
branch: codex/gov-path-header-compat-1
worktree: G:/CODEX/New Manga.workspace/worktrees/GOV-PATH-HEADER-COMPAT-1
integration_commit: null
delivery_head: 9f59537f989299c4ee6f41993134aa69d6cfbc12
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/GOV-PATH-HEADER-COMPAT-1
allowed_paths:
  - tools/governance/clean_workspace.py
  - tools/governance/tests/test_path_header_compat.py
  - doc/tasks/GOV-PATH-HEADER-COMPAT-1.md
  - verification/GOV-PATH-HEADER-COMPAT-1
  - doc/handoffs/GOV-PATH-HEADER-COMPAT-1.md
  - doc/STATUS.md
  - doc/REe7cbcada6d1a5c01f9c55e888e30c3efba20e1ffLINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/tasks/README.md
created: 2026-10-21
---

# GOV-PATH-HEADER-COMPAT-1

## 来源与范围冻结

用户要求先明确保护与独有支线边界，再由Codex继续，并保留现有清理禁令。Codex技术裁定见 verification/GIT-MAINLINE-CONVERGENCE-1/boundary-adjudication.md（边界证据 e7cbcada6）。全部现有分支/工作树继续保留；P14/P22仅作为未来只读评估候选；不释放任何产品实现或处置窗口。

本Task仅改变共享保护解析器对**一个完整固定表头字面量**的兼容策略：把模板已有的 `path（仓库相对路径或绝对路径）` 识别为 `path`，同时在重复身份列检查使用同一归一化。原规则的English-only限制在本Task精确范围内由Codex明确修订，不能据此扩展任意中文/模糊别名。重复列、缺列、malformed表、未知disposition、JSON损坏、不可读、模糊/环境路径仍fail-closed。

内存模拟（非实现批准）为77→32 errors，保护根1277→1687，旧集合子集成立，新增410根。已完成相关影响全集与边界核验，满足协议§4.4；真实实现仍需同快照复测与独立Review。只使用既有stdlib，无新依赖/契约/Schema/API变更；旧Task/证据/pin文件不编辑。

## Acceptance Criteria

- [x] **AC1** 完整固定别名和原始path列都识别，真实Canonical Evidence行被保护。 <<MET>>
- [x] **AC2** alias+path、alias+alias重复列拒绝；其它说明/别名/缺列/malformed不接受或保持原判定，未知disposition等安全门槛不变。 <<MET>>
- [x] **AC3** 同一main数据快照用原实现和候选实现审计，45个schema错误消解、其余32保留，原保护根不丢失，新增根可复算；不调用apply。 <<MET>>
- [ ] **AC4** 既有声明/安全回归和incident replay通过，记录shell/interpreter/EXIT与skips；固定head独立Review。 <<PARTIAL: 5+29+80测试和双事故回放通过，等待独立Review>>
- [ ] **AC5** Codex集成后复验、Handoff与资源清册闭环；父Task继续blocked，不解除禁令、不宣称只有main。 <<PARTIAL: 固定交付待独审与Codex集成；资源保留>>

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
|EV-12|AC5|verification/GOV-PATH-HEADER-COMPAT-1/.gitattributes|9f59537f989299c4ee6f41993134aa69d6cfbc12|a79691a93b46e49ce460c26ef22afcc03d6eca1e63bf2edbc20e96159510f6c9|SOURCE_PIN|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/GOV-PATH-HEADER-COMPAT-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/GOV-PATH-HEADER-COMPAT-1 | doc/tasks/GOV-PATH-HEADER-COMPAT-1.md | 待释放后创建；父禁令有效，不删除 |
| agent-output | G:/CODEX/New Manga.workspace/agent-output/codex/GOV-PATH-HEADER-COMPAT-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/agent-output/codex/GOV-PATH-HEADER-COMPAT-1 | doc/tasks/GOV-PATH-HEADER-COMPAT-1.md | 本Task日志/原始对照，保留 |
| temp | G:/CODEX/New Manga.workspace/temp/GOV-PATH-HEADER-COMPAT-1 | PRESERVE_UNKNOWN | G:/CODEX/New Manga.workspace/temp/GOV-PATH-HEADER-COMPAT-1 | doc/tasks/GOV-PATH-HEADER-COMPAT-1.md | 仅自有测试夹具；结束残余保留，不清理真实项目资源 |

## 运行记录

先ready冻结，再Owner认领。Handoff/Review尚无；只释放本精确技术前置，不改变完整收敛Task的blocked状态。

## 交付记录

固定实现与证据 9f59537f989299c4ee6f41993134aa69d6cfbc12；5新增+29声明+80安全测试通过、0skip；baseline判别预期exit1；双incident replay各15/15拒绝、0删除；同快照77→32，1280旧根全部保留并新增410。源helper/code未在main实施。工作树已创建且按清理禁令保留；临时测试自有夹具由test cleanup回收，剩余temp根保留。Handoff在Review/集成后追加。
