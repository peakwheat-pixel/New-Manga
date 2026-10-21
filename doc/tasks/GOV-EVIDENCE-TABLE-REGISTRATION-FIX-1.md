---
id: GOV-EVIDENCE-TABLE-REGISTRATION-FIX-1
title: 三个治理Task证据表连续性与实际保护注册修正
kind: governance
governance_version: 3
status: in_progress
approval: user_auto_advance_20261021_scoped_mechanical_metadata_fix
suggested_owner: Codex
owner: Codex
reviewer: DeepSeek Harness
depends_on: [GOV-NDJSON-NONDECL-IDENTITY-1]
base_commit: f72dd96ee51f21cc24472b05cceaf488060b679a
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: 244d08e4eb5bb7aee1b6b54d0198093bcd16b48c
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/GOV-EVIDENCE-TABLE-REGISTRATION-FIX-1
allowed_paths:
  - doc/tasks/GOV-EVIDENCE-TABLE-REGISTRATION-FIX-1.md
  - verification/GOV-EVIDENCE-TABLE-REGISTRATION-FIX-1
  - doc/handoffs/GOV-EVIDENCE-TABLE-REGISTRATION-FIX-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/tasks/README.md
  - verification/GIT-MAINLINE-CONVERGENCE-1/checkpoint.md
  - doc/tasks/GIT-MAINLINE-CONVERGENCE-1.md
  - doc/tasks/GOV-PATH-HEADER-COMPAT-1.md
  - doc/tasks/GOV-DECLARATION-RESIDUAL-32-AUDIT-1.md
---

# GOV-EVIDENCE-TABLE-REGISTRATION-FIX-1

## 冻结范围

用户授权自动推进，承接已独审54cfbadad建议。仅3个scope.json目标Canonical Evidence章节内删除阻断表格的空行；其它非空行、path/commit/SHA/class、原status/AC/Review/integration/delivery均保持原样。51条pin已preflight按raw disk/blob/hash验证；实际注册9/12/0与19/19/13不符。原Task不重开、不重新批准旧实现。Codex main串行文档修正，无新branch/worktree；DeepSeek固定head独审。父Task blocked/32errors及STATUS/r212禁令保留。

## Acceptance Criteria

- [x] **AC1** 逐Task原51pin raw磁盘/blob/SHA全部有效，记录原表行数/实际注册/状态。 <<MET>>
- [x] **AC2** 仅移除3章节内空行，所有非空行序列/元数据/51 pin值不变；实际注册19/19/13，0 parser errors。 <<MET>>
- [x] **AC3** 默认32错误完整身份不变，旧保护集合只增不减；原被pin文件/guard/正式表/用户与未跟踪内容不动；98/136不变。 <<MET>>
- [ ] **AC4** 独立固定head Review、Codex集成/保留资源核销、证据注册与治理check完成，后续自动推进仍独立冻结范围。 <<PARTIAL: 等待固定head独立Review与核销>>

## 禁止与验证

不改51个目标证据字节或重签原pin，不改guard/正式例外表/架构/Schema/依赖，不读全历史/其它worktree，不清理/迁移/归档/GC/prune/push/reset/stash/改ACL。异常源pin/归属即保留并阻塞该项。验证使用实际parse_markdown_declarations、scan_repo_declarations及raw字节；产品测试NOT_RUN（纯文档格式），不新增镜像测试。运行pwsh -NoProfile -File tools/governance/check.ps1。既有终态Task状态不动，不把修正当重开。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
|EV-1|AC1/AC2/AC3/AC4|verification/GOV-EVIDENCE-TABLE-REGISTRATION-FIX-1/.gitattributes|dcfb553dccea858d0a5ae6fb8951265b4dd868bb|6c3ea912d1baf7bd93fe33a6c9f3653e83125326ee99b637594e6b3418c6b7d8|CANONICAL|
|EV-2|AC1/AC2/AC3/AC4|verification/GOV-EVIDENCE-TABLE-REGISTRATION-FIX-1/checkpoint.md|dcfb553dccea858d0a5ae6fb8951265b4dd868bb|db3b66c54967a76f271fef70f16ba6b20e244c565d6a9dbdf2ad8629fa219bbe|CANONICAL|
|EV-3|AC1/AC2/AC3/AC4|verification/GOV-EVIDENCE-TABLE-REGISTRATION-FIX-1/registration-proof.json|dcfb553dccea858d0a5ae6fb8951265b4dd868bb|69ab5ed13c4b6d5c585ab79c4bcf68283b7fb744dfd3ae98d435bc0223f9ce3c|CANONICAL|
|EV-4|AC1/AC2/AC3/AC4|verification/GOV-EVIDENCE-TABLE-REGISTRATION-FIX-1/report.md|dcfb553dccea858d0a5ae6fb8951265b4dd868bb|d9ebabf6a9920c9a2836923bbb726baf5ff423efae856eac62c1ab3612a54d89|CANONICAL|
|EV-5|AC1/AC2/AC3/AC4|verification/GOV-EVIDENCE-TABLE-REGISTRATION-FIX-1/scope.json|dcfb553dccea858d0a5ae6fb8951265b4dd868bb|f1c30a4d5cac296e1738b2878bb78709757c0bd24a569cbff9a4ccbfca69bcb5|CANONICAL|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | G:/CODEX/New Manga.workspace/agent-output/codex/GOV-EVIDENCE-TABLE-REGISTRATION-FIX-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/agent-output/codex/GOV-EVIDENCE-TABLE-REGISTRATION-FIX-1 | doc/tasks/GOV-EVIDENCE-TABLE-REGISTRATION-FIX-1.md | 本Task原始核验/Review输出保留，不清理 |
| worktree/env/build/temp/exchange | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | 不新建，98/136保持 |

R1独审changes_requested（fa18dc2c6）：实现/51pin/实际注册/旧保护子集均通过；需解释before重建34而实测32的差异。暂停集成后续配置，独立定位两额外错误。

定位结果：R1的两条额外JSON_PARSE来自将base不存在的本Task scope.json/registration-proof.json保留在HEAD枚举并返回空字节。不存在文件不等于空JSON。正确重建将HEAD新增文件从Git枚举中排除，再对原有变更文件回填base字节，固定当前未跟踪快照，结果base32/head32完全同身份，base1722为head1758子集；三个base文件分别注册9/12/0且0error。详before-reconstruction-proof.json，原实现/51pin/registration-proof不改。关于用户/未跟踪内容，只声明本Task未执行越界写入；未做全体逐字节基线，不能由Git证明全体未变。
