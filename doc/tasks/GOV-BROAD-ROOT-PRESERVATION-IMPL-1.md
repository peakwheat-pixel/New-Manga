---
id: GOV-BROAD-ROOT-PRESERVATION-IMPL-1
title: 五个广域根整体保护的精确运行策略实现
kind: governance-hardening
governance_version: 3
status: in_progress
approval: user_next_step_20261021_scoped_reviewed_design_implementation
suggested_owner: Codex
owner: Codex
reviewer: DeepSeek Harness
depends_on: [GOV-BROAD-ROOT-PRESERVATION-DESIGN-1]
base_commit: 40343a8b2efe85cb6927f278be9e1e16fa439726
branch: codex/gov-broad-root-preservation-impl-1
worktree: G:/CODEX/New Manga.workspace/worktrees/GOV-BROAD-ROOT-PRESERVATION-IMPL-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/GOV-BROAD-ROOT-PRESERVATION-IMPL-1
allowed_paths:
  - tools/governance/clean_workspace.py
  - tools/governance/broad-root-preservation.json
  - verification/GOV-BROAD-ROOT-PRESERVATION-IMPL-1
  - doc/tasks/GOV-BROAD-ROOT-PRESERVATION-IMPL-1.md
  - doc/handoffs/GOV-BROAD-ROOT-PRESERVATION-IMPL-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/tasks/README.md
  - verification/GIT-MAINLINE-CONVERGENCE-1/checkpoint.md
---

# GOV-BROAD-ROOT-PRESERVATION-IMPL-1

## 冻结范围与授权

用户“下一步”启动已独审设计的实现；依赖设计done、R3 232e3a589/source e33a51b4d。只改共享scanner收口与新增运行策略，自己的新测试复用旧RepoFixture（只读）。严格按设计schema与T01-T18；通用路径/身份/Markdown/JSON拒绝、69例外、三个消费者原实现不改。用户5广域根继续整体保护，旧两Task/原SHA/pin不变；父blocked/r212禁令不解除。

单独Task分支/worktree隔离，当前99/137，创建后预计100/138且按禁令保留。main治理权威由epoch9 gate串行维护；不复制租约。候选真实审计必须以canonical main数据（含未跟踪源）为准；仅可镜像本Task新增policy及自有证据到main，先track供候选tracked检查，main旧guard在合并前仍24，不能声称已集成。工作树自身历史文件换行或缺未跟踪源不用于替代canonical真值。

## Acceptance Criteria

- [ ] **AC1** 运行策略严格schema/六记录五根/裁决与源raw/行/role/错误对/realpath精确验证，tracked存在条件，未知/漂移fatal；旧源与69例外不变。 <<PARTIAL: 已冻结，尚未实现>>
- [ ] **AC2** 隔离index/scanned原子发布，新增12Declaration/5根/12warnings，恰24→12且其它12完整身份/旧保护保全；EVIDENCE_PIN/prose/JSON/直连不继承许可，三入口共用。 <<PARTIAL: 尚未实现>>
- [ ] **AC3** T01-T18实际正反/异常注入/三入口覆盖，29+80回归0skip及双15REJECT/0deleted/0violations，独立固定head DeepSeek Review。 <<PARTIAL: 尚未运行>>
- [ ] **AC4** Codex main集成复验、实际EV注册/raw-blob-pin、check/diff/Handoff/资源原位核销完整，正式其它12继续fail-closed，100/138（创建后）全部保留。 <<PARTIAL: 独审集成后才核销>>

## 测试边界与禁止

Python -B/PYTHONDONTWRITEBYTECODE=1/UTF8；TMP/TEMP仅本Taskworkspace/agent-output/test-temp，允许测试创建并自清其独占合成fixture（含隔离git init/fixture提交），禁止对真实资源执行apply/删除/迁移/归档/GC/prune/push/reset/stash/ACL/安装/Legacy。新增运行policy测试时必须tracked；无Git scanner继续fatal。只读旧29/80 tests和事故ledger，不运行会重写旧pin的历史探针。产品/构建NOT_RUN（治理工具）。发现范围外消费者缺陷只能记录，不夹带修。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/GOV-BROAD-ROOT-PRESERVATION-IMPL-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/GOV-BROAD-ROOT-PRESERVATION-IMPL-1 | doc/tasks/GOV-BROAD-ROOT-PRESERVATION-IMPL-1.md | Codex冻结后创建，原位保留，禁止移除 |
| agent-output | G:/CODEX/New Manga.workspace/agent-output/codex/GOV-BROAD-ROOT-PRESERVATION-IMPL-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/agent-output/codex/GOV-BROAD-ROOT-PRESERVATION-IMPL-1 | doc/tasks/GOV-BROAD-ROOT-PRESERVATION-IMPL-1.md | 日志/候选/测试根保留，仅自有合成fixture允许自清 |
| other env/build | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | 无新建 |
