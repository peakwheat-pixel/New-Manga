---
id: GOV-NDJSON-EXCEPTION-CONFIG-1
title: 当前例外配置迁移与两固定NDJSON精确登记
kind: governance-hardening
governance_version: 3
status: in_review
approval: user_auto_advance_20261021_scoped_configuration_implementation
suggested_owner: Codex
owner: Codex
reviewer: DeepSeek Harness
depends_on: [GOV-EVIDENCE-TABLE-REGISTRATION-FIX-1, GOV-NDJSON-NONDECL-IDENTITY-1]
base_commit: bbc9532b8ff7326b985e8f3f828bccd040c0d583
branch: codex/gov-ndjson-exception-config-1
worktree: G:/CODEX/New Manga.workspace/worktrees/GOV-NDJSON-EXCEPTION-CONFIG-1
integration_commit: null
delivery_head: 7fd00e8b4a1ec53440aac64b4d44566761579cd6
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/GOV-NDJSON-EXCEPTION-CONFIG-1
allowed_paths:
  - tools/governance/clean_workspace.py
  - tools/governance/non-declaration-json-exceptions.json
  - doc/tasks/GOV-NDJSON-EXCEPTION-CONFIG-1.md
  - verification/GOV-NDJSON-EXCEPTION-CONFIG-1
  - doc/handoffs/GOV-NDJSON-EXCEPTION-CONFIG-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/tasks/README.md
  - verification/GIT-MAINLINE-CONVERGENCE-1/checkpoint.md
---

# GOV-NDJSON-EXCEPTION-CONFIG-1

## 冻结范围

用户自动推进；依赖51pin表格修正已独审edbd1a492并done、两NDJSON身份/信任边界研究独审54cfbadad并done。只新建tools/governance/non-declaration-json-exceptions.json，完整复制旧67个记录再加scope两固定path/raw SHA/reason；只切换clean_workspace.py的DEFAULT_JSON_EXCEPTION_MANIFEST字符串。旧表是历史Canonical Evidence，原文件/旧Task/pins和两日志原样保留，不迁移、不修改旧证据、不改解析逻辑/Schema/依赖。3调用入口共用guard的默认配置，冻结覆盖共享影响。精确登记不是通用坏JSON/NDJSON忽略，内容或hash漂移即拒绝，不自动重签。

Codex分支/worktree隔离实现，main唯一集成主线，DeepSeek非作者固定head独审后Codex集成复验。R23未跟踪原日志仅在canonical main读取，不能复制/提交。main治理用epoch9 gate，worktree自有Task副本同步不复制/分叉租约。新增分支/worktree按现有禁令保留，预计99heads/137worktrees，不能为数量达标删除。

## Acceptance Criteria

- [x] **AC1** 新69项原67逐项完全相同、无丢失/重复/泛化，新增2条与独审原始字节匹配；历史表Git pin/磁盘CRLF及两日志原字节不变。 <<MET>>
- [x] **AC2** 代码仅默认常量变化；同canonical数据实际默认32→30恰移两JSON_PARSE，剩30完整身份相同、保护集合不减少；三入口共享当前默认。 <<MET>>
- [ ] **AC3** 错path/hash/字节漂移拒绝和合法声明解析验证、29声明+80安全回归、双事故回放通过，独立固定head Review。 <<PARTIAL: 回归/负例/双回放通过，独立Review待完成>>
- [ ] **AC4** Codex主线集成复验默认30、治理check/实际pin注册与资源原位保留核销/Handoff完整；父blocked、保护及清理禁令不解除。 <<PARTIAL: 独审通过后才执行main集成复验与核销>>

## 测试与禁止

PowerShell/Python -B/PYTHONDONTWRITEBYTECODE=1。29声明测试与80安全回归只读旧测试源码，TMP/TEMP隔离G:/CODEX/New Manga.workspace/agent-output/codex/GOV-NDJSON-EXCEPTION-CONFIG-1/test-temp，仅允许测试创建/自清其自有合成fixture，禁止触碰真实资源；不复制项目为第二真仓库。双事故回放各15REJECT/0删除/0违规；机制有界内存/候选测试留本Task输出，不重跑会改旧pin的历史探针。产品/构建NOT_RUN（治理配置）。不新增测试源码；如必要另冻路径。governance check仅canonical main，不用缺少未跟踪草稿的worktree充当治理真值。禁止apply/真实删除/迁移/归档/GC/prune/push/reset/stash/ACL/安装/旧collector/Legacy任务。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
|EV-1|AC1/AC2/AC3/AC4|verification/GOV-NDJSON-EXCEPTION-CONFIG-1/.gitattributes|b9a879c735b499dee9663e323976b0efd0544c98|6c3ea912d1baf7bd93fe33a6c9f3653e83125326ee99b637594e6b3418c6b7d8|CANONICAL|
|EV-2|AC1/AC2/AC3/AC4|verification/GOV-NDJSON-EXCEPTION-CONFIG-1/candidate-default-audit.json|b9a879c735b499dee9663e323976b0efd0544c98|2396181c42aa2c193fcd60d9dbd061e9db3f0073dd9c454c8be4111d0f579b06|CANONICAL|
|EV-3|AC1/AC2/AC3/AC4|verification/GOV-NDJSON-EXCEPTION-CONFIG-1/candidate-default-audit.log|b9a879c735b499dee9663e323976b0efd0544c98|fda7f664c40783c39722cbe2d86583814a3bedf1616d71579b0307f4bc4e40b2|CANONICAL|
|EV-4|AC1/AC2/AC3/AC4|verification/GOV-NDJSON-EXCEPTION-CONFIG-1/checkpoint.md|b9a879c735b499dee9663e323976b0efd0544c98|e6714f047b6517dbe8509c5279b80474b5058abb2bcb5a803ed12d99cf6993c6|CANONICAL|
|EV-5|AC1/AC2/AC3/AC4|verification/GOV-NDJSON-EXCEPTION-CONFIG-1/configuration-proof.json|b9a879c735b499dee9663e323976b0efd0544c98|2ec9d0922ea71f795fda8e22c1e002025475d413b716353e9d20eb34002f7d82|CANONICAL|
|EV-6|AC1/AC2/AC3/AC4|verification/GOV-NDJSON-EXCEPTION-CONFIG-1/declaration-tests.log|b9a879c735b499dee9663e323976b0efd0544c98|14e2a2aa3bb0513f9450481d7b2603fab132c4db94123825600ec9eca10152be|CANONICAL|
|EV-7|AC1/AC2/AC3/AC4|verification/GOV-NDJSON-EXCEPTION-CONFIG-1/hardening-tests.log|b9a879c735b499dee9663e323976b0efd0544c98|9ae4a59974d0126a9b44bdc60ce8e054c07d5f4a5b0d2c7365c9669bf95f281c|CANONICAL|
|EV-8|AC1/AC2/AC3/AC4|verification/GOV-NDJSON-EXCEPTION-CONFIG-1/incident-replay-clean-workspace.json|b9a879c735b499dee9663e323976b0efd0544c98|97e9495aaabc8cae865e8506d8dc97e86afe6ec986c33421214c6d866d0bf5d7|CANONICAL|
|EV-9|AC1/AC2/AC3/AC4|verification/GOV-NDJSON-EXCEPTION-CONFIG-1/incident-replay-remove-worktrees.json|b9a879c735b499dee9663e323976b0efd0544c98|1c556efe2f061261e14e77d4998210e662781b68cfbca09ed4983590a6909c7c|CANONICAL|
|EV-10|AC1/AC2/AC3/AC4|verification/GOV-NDJSON-EXCEPTION-CONFIG-1/replay-clean_workspace.log|b9a879c735b499dee9663e323976b0efd0544c98|13e8329db01c3254716435518c28b79a37342593eebc8fe9cb23a9c2f869d0e3|CANONICAL|
|EV-11|AC1/AC2/AC3/AC4|verification/GOV-NDJSON-EXCEPTION-CONFIG-1/replay-remove_worktrees.log|b9a879c735b499dee9663e323976b0efd0544c98|0314d145a5a753c62447d0da3fb516b8f840a0e842ff44c326ea6626fe7a3c5f|CANONICAL|
|EV-12|AC1/AC2/AC3/AC4|verification/GOV-NDJSON-EXCEPTION-CONFIG-1/report.md|b9a879c735b499dee9663e323976b0efd0544c98|9402dbc294ec088c25949d3ef8ce16dcd57ec691571b10e91c30e6816f991129|CANONICAL|
|EV-13|AC1/AC2/AC3/AC4|verification/GOV-NDJSON-EXCEPTION-CONFIG-1/scope.json|b9a879c735b499dee9663e323976b0efd0544c98|118fe670782171311e4478ea78d3449cb5dacd05bf7c76b38f535107fdd3f603|CANONICAL|
|EV-14|AC1/AC2/AC3/AC4|verification/GOV-NDJSON-EXCEPTION-CONFIG-1/test-execution.json|b9a879c735b499dee9663e323976b0efd0544c98|f1a2a57e66406ffc5f7432ebc331f297cfea3743e362ed27ecf666e3d3b362f1|CANONICAL|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/GOV-NDJSON-EXCEPTION-CONFIG-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/GOV-NDJSON-EXCEPTION-CONFIG-1 | doc/tasks/GOV-NDJSON-EXCEPTION-CONFIG-1.md | 冻结后创建，分支/worktree按禁令保留 |
| agent-output | G:/CODEX/New Manga.workspace/agent-output/codex/GOV-NDJSON-EXCEPTION-CONFIG-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/agent-output/codex/GOV-NDJSON-EXCEPTION-CONFIG-1 | doc/tasks/GOV-NDJSON-EXCEPTION-CONFIG-1.md | 日志/候选/test-temp保留；仅fixture可自清所有临时目录 |
| other env/build/exchange | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | 无新建，禁止清理真实资源 |

## 交付记录

实际worktree/review diff基线98993fe10，frontmatter来源bbc9532b8；其间仅本Task冻结/认领metadata，guard/旧表内容相同。实现7fd00e8b4，证据b9a879c735b499dee9663e323976b0efd0544c98。69项旧67逐项相同、guard AST仅默认常量变化；同canonical main含R23数据实际32→30，原保护不减；错path/hash/字节漂移拒绝、合法声明解析，29+80回归0skip、双回放15REJECT/0删除/0违规。独审前main尚未合并代码，仍正式32。owner Task副本同步worktree，canonical元数据由main gate串行写，不复制runtime租约。99heads/137worktrees全部保留。
