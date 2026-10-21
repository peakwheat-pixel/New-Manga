---
id: GOV-PATH-HEADER-COMPAT-1
title: 固定模板路径列表头兼容，保留所有 fail-closed 门槛
kind: governance-hardening
governance_version: 3
status: in_progress
approval: codex_scoped_technical_followup_user_boundary_continuation_20261021
suggested_owner: Codex
owner: Codex
reviewer: DeepSeek Harness
depends_on: [WORKSPACE-DECLARATION-REMEDIATION-1]
base_commit: e7cbcada6d1a5c01f9c55e888e30c3efba20e1ff
branch: codex/gov-path-header-compat-1
worktree: G:/CODEX/New Manga.workspace/worktrees/GOV-PATH-HEADER-COMPAT-1
integration_commit: null
delivery_head: null
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

- [ ] **AC1** 完整固定别名和原始path列都识别，真实Canonical Evidence行被保护。 <<BLOCKED: 待实施>>
- [ ] **AC2** alias+path、alias+alias重复列拒绝；其它说明/别名/缺列/malformed不接受或保持原判定，未知disposition等安全门槛不变。 <<BLOCKED: 待正反例回归>>
- [ ] **AC3** 同一main数据快照用原实现和候选实现审计，45个schema错误消解、其余32保留，原保护根不丢失，新增根可复算；不调用apply。 <<BLOCKED: 待真实对照>>
- [ ] **AC4** 既有声明/安全回归和incident replay通过，记录shell/interpreter/EXIT与skips；固定head独立Review。 <<BLOCKED: 待验证>>
- [ ] **AC5** Codex集成后复验、Handoff与资源清册闭环；父Task继续blocked，不解除禁令、不宣称只有main。 <<BLOCKED: 待集成>>

## 禁止范围

不修改历史Task、原始evidence/pin/JSON例外清单；不扩大列名/路径/JSON/disposition语义；不apply、不删/迁移/归档真实资源，不强删分支、不GC/prune/push/reset/stash。新Task工作树/分支与所有派生产物保留，不能为了收口绕过父禁令。只允许既有测试在本Task隔离temp内创建及清理测试自有夹具；不得触碰真实用户资源，不能对canonical repo执行删除工具apply。

## 测试要求

计划：python -B -m unittest discover -s tools/governance/tests -p test_path_header_compat.py；既有29声明测试与80安全测试；真实只读before/after审计；incident replay。TMP/TEMP隔离 G:/CODEX/New Manga.workspace/temp/GOV-PATH-HEADER-COMPAT-1。实际命令、结果与skip理由按执行追加。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/GOV-PATH-HEADER-COMPAT-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/GOV-PATH-HEADER-COMPAT-1 | doc/tasks/GOV-PATH-HEADER-COMPAT-1.md | 待释放后创建；父禁令有效，不删除 |
| agent-output | G:/CODEX/New Manga.workspace/agent-output/codex/GOV-PATH-HEADER-COMPAT-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/agent-output/codex/GOV-PATH-HEADER-COMPAT-1 | doc/tasks/GOV-PATH-HEADER-COMPAT-1.md | 本Task日志/原始对照，保留 |
| temp | G:/CODEX/New Manga.workspace/temp/GOV-PATH-HEADER-COMPAT-1 | PRESERVE_UNKNOWN | G:/CODEX/New Manga.workspace/temp/GOV-PATH-HEADER-COMPAT-1 | doc/tasks/GOV-PATH-HEADER-COMPAT-1.md | 仅自有测试夹具；结束残余保留，不清理真实项目资源 |

## 运行记录

先ready冻结，再Owner认领。Handoff/Review尚无；只释放本精确技术前置，不改变完整收敛Task的blocked状态。
