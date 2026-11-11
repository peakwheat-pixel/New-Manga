---
id: FEA-15-PIN-EOL-GOV-1
title: 证据 pin 行尾与跨 checkout 可复现性治理
kind: governance
governance_version: 3
status: in_review
approval: ZCode 2026-11-11 裁决释放（独立 CLI 会话；[adjudication](../reviews/FEA-15-DIAG-ACL-1-zcode-adjudication-2026-11-11.md) §4）；本轮用户单次授权：只读治理阶段
suggested_owner: codex
owner: codex
reviewer: ZCode（全新独立 CLI Review 会话；不得复用裁决释放会话 sess_abdb4288-4a4f-49c1-8097-6edbb6e3866f；派发后回填 session ID）
depends_on:
  - FEA-15-ACCEPT-1
base_commit: 4173961dfe1b65256cb06d7628cc813b0603caa3
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: 996f9768985ee121767bd750d24b1cdfe74dd186
canonical_evidence_status: complete
resource_closeout_status: pending
evidence_dir: verification/FEA-15-PIN-EOL-GOV-1
allowed_paths:
  - doc/tasks/FEA-15-PIN-EOL-GOV-1.md
  - doc/reviews/FEA-15-PIN-EOL-GOV-1-*.md
  - doc/handoffs/FEA-15-PIN-EOL-GOV-1-*.md
  - verification/FEA-15-PIN-EOL-GOV-1/**
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
out_of_scope:
  - 禁止修改 .gitattributes、checker/verify_pins/task_ledger 检查语义、任何历史证据或 pin、冻结契约与 FROZEN 记录（含 C-07）、源代码、Schema、依赖
  - .gitattributes/renormalize/历史 pin 处置的实施必须另开 Task 并经独立授权与独立 Review（§4.4：盘点未完成不得改 .gitattributes）
  - 禁止 push、禁止清理/迁移/归档任何资源；不得以历史 27/30 或 187/300 数目推断当前全集
---

# FEA-15-PIN-EOL-GOV-1：证据 pin 口径治理（只读盘点阶段）

来源：`doc/reviews/FEA-15-ACCEPT-1-r1.md` P2-1 与 r2 P3-A（30 条 pin 中 27 条工作区口径，含 SRC-25）、`doc/reviews/FEA-15-DIAG-ACL-1-zcode-adjudication-2026-11-11.md` §4 释放裁决。根因已定位：`.gitattributes` 对 `verification/**` 无 eol 规则，`core.autocrlf=true` 来自系统级配置；仓库已有 SEC-FIX-PATH-ECHO-1 / P19-UI-MANIFEST-VIEW-1 / GOV-EOL-PIN-1（FEA-08 blob/LF 口径）先例。`check.ps1` r194 条款现行接受双基准，属 §4.4 语义核验前置适用面。

本阶段为**只读治理盘点**：完成全集盘点、跨 checkout 观察矩阵与候选策略分析；口径裁定与任何实施不在本 Task。

## Acceptance Criteria

- [x] **AC1 全集盘点**：在快照 `948d73e0629869e560df9a2b2d8a357cec67027f` 实测全部 versioned 证据 pin（584 张 Task 卡 Canonical Evidence 表 + 18 条契约 FROZEN 记录），逐条登记来源、pin、工作区 SHA-256、blob SHA-256、基准分类与 eol/attribute 状态；产出机器可复核清单。未从历史比例推断全集。 <<MET>>
- [x] **AC2 跨 checkout 观察矩阵**：对 BLOB、WORKTREE、mixed eol、binary 各选样本，在 main worktree 与隔离 checkout `core.autocrlf=true/false` 下复算；共 12 个观察，记录命令 EXIT、HEAD、时点与 PASS/FAIL。另保留一个早期 clean snapshot checkout 作补充，不计入最终矩阵。 <<MET>>
- [x] **AC3 基线证据与候选策略分析**：分析含 FEA-08 blob/LF 先例、`check.ps1` r194 双基准语义、renormalize 影响面及历史 pin 处置选项；事实/推论/未知项/反证条件/暂停门槛分列。只提出候选项，未选策略或实施。 <<MET>>

## 测试计划

- Gate（基线两轮见 `gate-baseline.log` 与 `gate-post-evidence.log`；首次失败保留于 `gate-current.log`，修正预算/READY 哨兵后的 PASS 记录于 `gate-final.log`）：`pwsh -NoProfile -File tools/governance/check.ps1`（default）与 `-TaskPath doc/tasks/FEA-15-PIN-EOL-GOV-1.md`；`pwsh -NoProfile -File tools/governance/verify_pins.ps1`（18/18）；`python tools/generate_api_inventory.py --check`（1/79/6=86）。卡面最终 pin 回填后另作最终复跑并记录于外部 agent-output。
- 观察命令：`git ls-files --eol`、`git cat-file blob <commit>:<path>`、隔离 checkout 复算；每个观察在 `checkout-matrix.json` 中带时间、HEAD、SHA-256 与 command exit codes。Linux fresh clone、renormalize simulation 与产品测试 `NOT_RUN`，原因见 `verification/FEA-15-PIN-EOL-GOV-1/README.md`。

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task workspace（矩阵 checkout） | G:/CODEX/New Manga.workspace/FEA-15-PIN-EOL-GOV-1/checkout-autocrlf-true；`checkout-autocrlf-false` | PRESERVE_REFERENCED | 同源路径（保留） | `resource-manifest.json` SHA-256 `fd2f4aebf0099563a82a43dcfa976678772d63b4256843e086c2a6e41e125820`; commit `ef6253677a608f285e1c86a321712e45ae54cfef` | 两 clone 均 HEAD=`948d73e0…`、20,778 tracked files、status clean；由 AC2 引用 |
| task workspace（补充 snapshot clone） | G:/CODEX/New Manga.workspace/FEA-15-PIN-EOL-GOV-1/snapshot-main-system-config | PRESERVE_REFERENCED | 同源路径（保留） | 同一 `resource-manifest.json` 记录 clone 状态及 3 个生成 JSON 的 SHA-256 | branch `main`、HEAD=`c6f34d93…`；保留早期 checkout 对照与输出，不作最终 AC1/AC2 结论 |
| agent-output（历史生成尝试） | G:/CODEX/New Manga.workspace/agent-output/codex/FEA-15-PIN-EOL-GOV-1 | PRESERVE_REFERENCED | 同源路径（保留） | 同一 `resource-manifest.json` 逐文件记录 22 个日志/基线快照 SHA-256 | 含早期失败与成功尝试；保留原路径，无清理/迁移 |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| pin-inventory | AC1 | `verification/FEA-15-PIN-EOL-GOV-1/pin-inventory.json` | `ef6253677a608f285e1c86a321712e45ae54cfef` | `1b369d621867d6a55aa866b22a2ea7160e188b2dd89efb1e69521a7a14c38ab5` | CANONICAL |
| checkout-matrix | AC2 | `verification/FEA-15-PIN-EOL-GOV-1/checkout-matrix.json` | `ef6253677a608f285e1c86a321712e45ae54cfef` | `e826f597cf606f92be6307f5ad8a4c2e3695892edb45e04a93e81bea19f61e6a` | CANONICAL |
| policy-analysis | AC3 | `verification/FEA-15-PIN-EOL-GOV-1/candidate-policy-analysis.md` | `ef6253677a608f285e1c86a321712e45ae54cfef` | `53f7f39eba91649d52a448fabf5ed678ca463d437a2bba7aa5e8990ccc96c05d` | CANONICAL |
| final-governance-gates | Gate | `verification/FEA-15-PIN-EOL-GOV-1/gate-final.log` | `996f9768985ee121767bd750d24b1cdfe74dd186` | `3f7869327f6713693af95fbc95e57699ff1f579b2f4881dcca314322d4c4aa45` | CANONICAL |

## Closeout Record

- 2026-11-11：ZCode 裁决登记 proposed；未释放、未实施。
- 2026-11-11：ZCode 独立 CLI 会话复核 DIAG-ACL-1 终态后裁决释放（[adjudication](../reviews/FEA-15-DIAG-ACL-1-zcode-adjudication-2026-11-11.md) §4）：status→ready，范围冻结为只读盘点（AC1–AC3），base=`1e58398aa07467004c1b329bb52095f63bcb78d4`；待 Owner 认领。
- 2026-11-11：Codex 在释放提交 `4173961dfe1b65256cb06d7628cc813b0603caa3` 认领并进入 `in_progress`；Owner=`codex`，Reviewer 预指定为新 ZCode 独立 CLI Review 会话；实现与 Review 会话必须分离。
- 2026-11-11：计数核对发现首版把 `doc/tasks/README.md` 算作 Task 卡；生成器现排除索引并从 HEAD 读取 Task/冻结来源。c6 探索 checkout 保留为补充快照；当前主线快照更新为 `948d73e0…`。此前 `18e1bd2…` 的 Handoff 因首版计数过时保留为历史记录。
- 2026-11-11：修正后 AC1–AC3 证据固定于 `ef625367…`；`gate-final.log` 在 `996f9768…` 记录两项 governance check、18 pins、API 全部 EXIT 0。修订 Handoff [FEA-15-PIN-EOL-GOV-1-996f976.md](../handoffs/FEA-15-PIN-EOL-GOV-1-996f976.md)，SHA-256 `6d29c8bcfadf3ed8bd0a611dd6cce4b874f001cc05e4c9e82e99ff4082954b2e`，commit `f70cb325abf481b9f0513ccddec620c810fdfaf3`。Canonical Evidence 4 项已回填，Task→`in_review`；delivery_head=`996f9768985ee121767bd750d24b1cdfe74dd186`，等待新 ZCode CLI Review。
