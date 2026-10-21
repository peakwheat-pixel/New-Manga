---
id: GOV-NONRESOURCE-MANIFEST-FORMAT-1
title: 六个历史Task非资源说明表格的有界格式修正
kind: governance
governance_version: 3
status: done
approval: user_auto_advance_20261021_scoped_six_manifest_rows
suggested_owner: Codex
owner: Codex
reviewer: DeepSeek Harness
latest_review: verification/GOV-NONRESOURCE-MANIFEST-FORMAT-1/review-dsh.md
reviewed_head: 2573375dcc55b95d202ad2b6cdfee90d3f07c525
depends_on: [GOV-NDJSON-EXCEPTION-CONFIG-1]
base_commit: 54ff86fb200a8446aa0135aeb90fb0cac9ea7963
branch: main
worktree: G:/CODEX/New Manga
integration_commit: 2573375dcc55b95d202ad2b6cdfee90d3f07c525
delivery_head: 4c415d8ea
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/GOV-NONRESOURCE-MANIFEST-FORMAT-1
allowed_paths:
  - doc/tasks/GOV-NONRESOURCE-MANIFEST-FORMAT-1.md
  - verification/GOV-NONRESOURCE-MANIFEST-FORMAT-1
  - doc/handoffs/GOV-NONRESOURCE-MANIFEST-FORMAT-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/tasks/README.md
  - verification/GIT-MAINLINE-CONVERGENCE-1/checkpoint.md
  - doc/tasks/GOV-DEBT-CLEANUP-2.md
  - doc/tasks/P09-AC3-DELETE-1.md
  - doc/tasks/P09-AC3-DELETE-HARDEN-1.md
  - doc/tasks/P09-MANAGED-READ-ROOT-TRUST-1.md
  - doc/tasks/P20-AC4-FPS-1.md
  - doc/tasks/P20-CLOSE-BOUND-HARDEN-1.md
---

# GOV-NONRESOURCE-MANIFEST-FORMAT-1

## 冻结范围

用户自动推进，依赖配置Task已独审85a393dc4并集成9d21f8fb8。仅六个source_facts列出的历史Task各一行Resource Manifest：一个七列行合并末两个说明列；五个NOT_APPLICABLE行将非资源source_path说明移入末说明列，source用“-”。原文字全部保留，不重开旧Task、不改其状态/AC/Review/Canonical Evidence/pin值，不改source证据/代码/用户文件，不解除保护或改变资源处置。

先只读直接207pin；早期预检36+5不明包含大小写、外部pin/注释路径和commit-only误判，精确结果以本Task复算为准。19项CURRENT_RAW_VALID_HISTORICAL_DIFFERENT是既有身份限制：当前原始字节匹配，但固定commit blob不匹配，不能声称历史blob已验证或重签；只允许不触及这些资产/pin值的格式行变更。它们的历史身份修复保持BLOCKED。本Task不关闭旧limitation。DeepSeek若判此边界不成立则停止集成。

## Acceptance Criteria

- [x] **AC1** 六个Task各一行格式变化，原文字、状态、AC、Review和207pin字段不变；所有直接原文件前后字节保全。 <<MET>>
- [x] **AC2** 同数据默认30→24，仅移六指定错误，其余24完整身份相等，保护集合不减少；六单表parser错误归零。 <<MET>>
- [x] **AC3** 207pin逐项给出实际blob/raw/EOL/commit-only/外部身份及既有限制；不将原始hash相等误称blob相等。 <<MET>>
- [x] **AC4** DeepSeek固定提交独审，Codex集成复验、真实pin注册、治理check与资源核销/Handoff完整。 <<MET>>

## 禁止与验证

禁止修改六行以外原Task字节、旧证据/JSON/pin/源代码/用户文件，禁止Legacy执行、安装、网络、真实清理/迁移/归档/GC/prune/push/reset/stash。沿main串行治理，不新增worktree。检查原始字节diff、guard实际parser/全审计、直接pin哈希和git diff --check；不重复109工具回归（未改工具逻辑）。独立Review不允许批准清理或父done。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
|EV-1|AC1/AC2/AC3/AC4|verification/GOV-NONRESOURCE-MANIFEST-FORMAT-1/.gitattributes|9ca7cee6ad9c3dcf9ea1d7b8d65ef3e66917e169|705fd4d6451a31d36b3df7de96f83f30ac976c9b4a6d1e51671d8e2f33e2d0da|CANONICAL|
|EV-2|AC1/AC2/AC3/AC4|verification/GOV-NONRESOURCE-MANIFEST-FORMAT-1/checkpoint.md|9ca7cee6ad9c3dcf9ea1d7b8d65ef3e66917e169|502548ba7be6cfc09eb4a10d3c6a03f6babd6d0854f366c28d94589dc3bcb0fd|CANONICAL|
|EV-3|AC1/AC2/AC3/AC4|verification/GOV-NONRESOURCE-MANIFEST-FORMAT-1/format-proof.json|9ca7cee6ad9c3dcf9ea1d7b8d65ef3e66917e169|e1b669ea3820e6a99f5d9f14be484e4947a1e59426a5cb2343f77f1ed7739ebd|CANONICAL|
|EV-4|AC1/AC2/AC3/AC4|verification/GOV-NONRESOURCE-MANIFEST-FORMAT-1/report.md|9ca7cee6ad9c3dcf9ea1d7b8d65ef3e66917e169|1924c7c1d90197ace606148bdda63c833e8ff6ce342479d5822adc1fb33c80f0|CANONICAL|
|EV-5|AC4|verification/GOV-NONRESOURCE-MANIFEST-FORMAT-1/review-dsh.md|0893de2b50fec385c5d0c5a8ff20d3b6633b53da|00b8a7a1b44cfae9b20234a64f73ee79eb8a9d1f240624187e2f8532c83db7a4|CANONICAL|
|EV-6|AC4|verification/GOV-NONRESOURCE-MANIFEST-FORMAT-1/integration-validation.json|0893de2b50fec385c5d0c5a8ff20d3b6633b53da|f16b849c5a3560d93d4bd4738ced3914bd04195882f5057826d0b876823c86a0|CANONICAL|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | G:/CODEX/New Manga.workspace/agent-output/codex/GOV-NONRESOURCE-MANIFEST-FORMAT-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/agent-output/codex/GOV-NONRESOURCE-MANIFEST-FORMAT-1 | doc/tasks/GOV-NONRESOURCE-MANIFEST-FORMAT-1.md | 派生预览/取证/审查日志全部保留，无删除授权 |
| worktree/env/build | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | main串行文档治理，无新建 |

## Closeout Record

2026-10-21 / Codex：DeepSeek固定2573375dcc55b95d202ad2b6cdfee90d3f07c525 approved（delivery4c415d8ea），main串行集成复验同点：30→24，declarations2449→2455，protected1785→1787，新增2根/无移除。proof1781→1783为自有EV登记前快照，不能混称实时值。4原EV实际注册且raw=blob=pin；207原文件前后未改，不等于207pin都等于raw：195pin/raw相等、10行尾差异、2commit-only；19历史blob不等项继续BLOCKED。P09Managed raw混合CRLF与Git LF不同，内容diff只有冻结行。默认CLI exit2/24、check PASS2warnings、diff-check PASS。109工具回归未重复（无工具修改）；产品/构建NOT_RUN。

resource_closeout_status=complete：本Taskagent-output/派生预览/Review原位PRESERVE_REFERENCED，未新增worktree/env；DSH已exit0。99heads/137worktrees，0删除/迁移/归档/GC/prune/push，父blocked及STATUS/r212禁令保留。下一仅可另冻余24项只读裁决汇总，由Codex负责、DeepSeek独审；指令见本Task Handoff。
