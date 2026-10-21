---
id: GOV-NDJSON-EXCEPTION-CONFIG-1
title: 当前例外配置迁移与两固定NDJSON精确登记
kind: governance-hardening
governance_version: 3
status: in_progress
approval: user_auto_advance_20261021_scoped_configuration_implementation
suggested_owner: Codex
owner: Codex
reviewer: DeepSeek Harness
depends_on: [GOV-EVIDENCE-TABLE-REGISTRATION-FIX-1, GOV-NDJSON-NONDECL-IDENTITY-1]
base_commit: bbc9532b8ff7326b985e8f3f828bccd040c0d583
branch: codex/gov-ndjson-exception-config-1
worktree: G:/CODEX/New Manga.workspace/worktrees/GOV-NDJSON-EXCEPTION-CONFIG-1
integration_commit: null
delivery_head: null
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

- [ ] **AC1** 新69项原67逐项完全相同、无丢失/重复/泛化，新增2条与独审原始字节匹配；历史表Git pin/磁盘CRLF及两日志原字节不变。 <<NOT_RUN>>
- [ ] **AC2** 代码仅默认常量变化；同canonical数据实际默认32→30恰移两JSON_PARSE，剩30完整身份相同、保护集合不减少；三入口共享当前默认。 <<NOT_RUN>>
- [ ] **AC3** 错path/hash/字节漂移拒绝和合法声明解析验证、29声明+80安全回归、双事故回放通过，独立固定head Review。 <<NOT_RUN>>
- [ ] **AC4** Codex主线集成复验默认30、治理check/实际pin注册与资源原位保留核销/Handoff完整；父blocked、保护及清理禁令不解除。 <<NOT_RUN>>

## 测试与禁止

PowerShell/Python -B/PYTHONDONTWRITEBYTECODE=1。29声明测试与80安全回归只读旧测试源码，TMP/TEMP隔离G:/CODEX/New Manga.workspace/agent-output/codex/GOV-NDJSON-EXCEPTION-CONFIG-1/test-temp，仅允许测试创建/自清其自有合成fixture，禁止触碰真实资源；不复制项目为第二真仓库。双事故回放各15REJECT/0删除/0违规；机制有界内存/候选测试留本Task输出，不重跑会改旧pin的历史探针。产品/构建NOT_RUN（治理配置）。不新增测试源码；如必要另冻路径。governance check仅canonical main，不用缺少未跟踪草稿的worktree充当治理真值。禁止apply/真实删除/迁移/归档/GC/prune/push/reset/stash/ACL/安装/旧collector/Legacy任务。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/GOV-NDJSON-EXCEPTION-CONFIG-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/GOV-NDJSON-EXCEPTION-CONFIG-1 | doc/tasks/GOV-NDJSON-EXCEPTION-CONFIG-1.md | 冻结后创建，分支/worktree按禁令保留 |
| agent-output | G:/CODEX/New Manga.workspace/agent-output/codex/GOV-NDJSON-EXCEPTION-CONFIG-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/agent-output/codex/GOV-NDJSON-EXCEPTION-CONFIG-1 | doc/tasks/GOV-NDJSON-EXCEPTION-CONFIG-1.md | 日志/候选/test-temp保留；仅fixture可自清所有临时目录 |
| other env/build/exchange | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | 无新建，禁止清理真实资源 |
