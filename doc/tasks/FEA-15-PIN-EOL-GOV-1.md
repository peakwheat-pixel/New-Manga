---
id: FEA-15-PIN-EOL-GOV-1
title: 证据 pin 行尾与跨 checkout 可复现性治理
kind: governance
governance_version: 3
status: approved
approval: ZCode 2026-11-11 裁决释放（独立 CLI 会话；[adjudication](../reviews/FEA-15-DIAG-ACL-1-zcode-adjudication-2026-11-11.md) §4）；本轮用户单次授权：只读治理阶段
suggested_owner: codex
owner: codex
reviewer: ZCode CLI Review（sess_1ff7ce49-fa46-4cb8-b7a7-d2efcb347fdc）；adjudicator（sess_8df67a95-be8f-4518-89fe-d71e950d9cff）
depends_on:
  - FEA-15-ACCEPT-1
base_commit: 4173961dfe1b65256cb06d7628cc813b0603caa3
branch: main
worktree: G:/CODEX/New Manga
integration_commit: d9c6360bb4cfcee970c0fe21f825e58b0d26df09
delivery_head: 996f9768985ee121767bd750d24b1cdfe74dd186
canonical_evidence_status: complete
resource_closeout_status: complete
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

- Gate：基线首败保留于 `gate-current.log`；修正后 `gate-final.log`（HEAD `996f9768…`）四项全 EXIT 0。集成验证在 clean main HEAD `d9c6360bb4cfcee970c0fe21f825e58b0d26df09` 重跑，default 与 TaskPath checks（各 4 warnings）、18 pins、API 1/79/6=86 均 EXIT 0；逐条 HEAD/时间/命令/结果在 `G:/CODEX/New Manga.workspace/agent-output/codex/FEA-15-PIN-EOL-GOV-1/gate-d9c6360-adjudication.log`。
- 观察命令：`git ls-files --eol`、`git cat-file blob <commit>:<path>`、隔离 checkout 复算；每个观察在 `checkout-matrix.json` 中带时间、HEAD、SHA-256 与 command exit codes。Linux fresh clone、renormalize simulation 与产品测试 `NOT_RUN`，原因见 `verification/FEA-15-PIN-EOL-GOV-1/README.md`。

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task workspace（矩阵 checkout） | G:/CODEX/New Manga.workspace/FEA-15-PIN-EOL-GOV-1/checkout-autocrlf-true；`checkout-autocrlf-false` | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/FEA-15-PIN-EOL-GOV-1 | `verification/FEA-15-PIN-EOL-GOV-1/resource-manifest.json` | 两 detached clone 均 HEAD=`948d73e0…`、status clean；manifest SHA-256 `fcdf911d…` @ `642088933…`；由 AC2 引用 |
| task workspace（补充 snapshot clone） | G:/CODEX/New Manga.workspace/FEA-15-PIN-EOL-GOV-1/snapshot-main-system-config | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/FEA-15-PIN-EOL-GOV-1/snapshot-main-system-config | `verification/FEA-15-PIN-EOL-GOV-1/resource-manifest.json` | branch `main`、HEAD=`c6f34d93…`；3 个补充 JSON 保持 modified 并原位保留；manifest SHA-256 `fcdf911d…` @ `642088933…` |
| agent-output（历史生成尝试与最终门禁） | G:/CODEX/New Manga.workspace/agent-output/codex/FEA-15-PIN-EOL-GOV-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/agent-output/codex/FEA-15-PIN-EOL-GOV-1 | `verification/FEA-15-PIN-EOL-GOV-1/resource-manifest.json` | 23 个日志/快照 hash 与大小均匹配（manifest SHA-256 `fcdf911d…` @ `642088933…`），含最终门禁日志；不清理/迁移 |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| pin-inventory | AC1 | `verification/FEA-15-PIN-EOL-GOV-1/pin-inventory.json` | `ef6253677a608f285e1c86a321712e45ae54cfef` | `1b369d621867d6a55aa866b22a2ea7160e188b2dd89efb1e69521a7a14c38ab5` | CANONICAL |
| checkout-matrix | AC2 | `verification/FEA-15-PIN-EOL-GOV-1/checkout-matrix.json` | `ef6253677a608f285e1c86a321712e45ae54cfef` | `e826f597cf606f92be6307f5ad8a4c2e3695892edb45e04a93e81bea19f61e6a` | CANONICAL |
| policy-analysis | AC3 | `verification/FEA-15-PIN-EOL-GOV-1/candidate-policy-analysis.md` | `ef6253677a608f285e1c86a321712e45ae54cfef` | `53f7f39eba91649d52a448fabf5ed678ca463d437a2bba7aa5e8990ccc96c05d` | CANONICAL |
| final-governance-gates | Gate | `verification/FEA-15-PIN-EOL-GOV-1/gate-final.log` | `996f9768985ee121767bd750d24b1cdfe74dd186` | `3f7869327f6713693af95fbc95e57699ff1f579b2f4881dcca314322d4c4aa45` | CANONICAL |
| zcode-review-r1 | Review | `doc/reviews/FEA-15-PIN-EOL-GOV-1-r1.md` | `d9c6360bb4cfcee970c0fe21f825e58b0d26df09` | `5fa78bffa000b1d07b1ba6f4f2d882e9e104881e4fc61956fb1822b0b6109f7d` | CANONICAL |
| zcode-adjudication | Closeout | `doc/reviews/FEA-15-PIN-EOL-GOV-1-adjudication-2026-11-11.md` | `642088933d2c3a027647a82099ad4016d3baade0` | `414c977e554e9d6cd148aac2e7ae8a0f4bb7a7923418892405d57248d4ead373` | CANONICAL |
| integration-gates-d9c6360 | Gate | `G:/CODEX/New Manga.workspace/agent-output/codex/FEA-15-PIN-EOL-GOV-1/gate-d9c6360-adjudication.log` | `-` | `37c2da16292f916696936796881bf2a4cf5653359f10e389aeebc4286b79c520` | SOURCE_PIN |
| matrix-inventory-script | AC2 support | `verification/FEA-15-PIN-EOL-GOV-1/checkout_matrix.py` | `642088933d2c3a027647a82099ad4016d3baade0` | `5afdd759a1349b49b6c156b31166a32a6b19984b6dc47a9f33b8749cc1d7075b` | CANONICAL |
| matrix-run-log | AC2 support | `verification/FEA-15-PIN-EOL-GOV-1/checkout-matrix-run.log` | `642088933d2c3a027647a82099ad4016d3baade0` | `a8d8b08f3fbbb1578b366189bd238cef0159ce25441abbd6afe4de026262799d` | CANONICAL |
| matrix-recovery-log | AC2 support | `verification/FEA-15-PIN-EOL-GOV-1/checkout-recovery.log` | `642088933d2c3a027647a82099ad4016d3baade0` | `4aa8dfa4b8b299b1aca9b9a28a485a7d2353667bdcc401ddde2ed89cc936917f` | CANONICAL |
| matrix-refresh-log | AC2 support | `verification/FEA-15-PIN-EOL-GOV-1/checkout-refresh.log` | `642088933d2c3a027647a82099ad4016d3baade0` | `ccccc202a9b710597418a90eb95b6d0ebdd7b81b765e2efd908b7f40ddf2cdf6` | CANONICAL |
| matrix-samples | AC2 support | `verification/FEA-15-PIN-EOL-GOV-1/checkout-samples.json` | `642088933d2c3a027647a82099ad4016d3baade0` | `6d5ce6b050f460555786194b05a3e345d67554bcef6057d38a2a392cf47f47df` | CANONICAL |
| matrix-setup-log | AC2 support | `verification/FEA-15-PIN-EOL-GOV-1/checkout-setup.log` | `642088933d2c3a027647a82099ad4016d3baade0` | `673b7108e8b3757254685a69972a98f5a9f6c1e7784435e1e6fd09ebb321dd51` | CANONICAL |
| initial-gate-log | Gate history | `verification/FEA-15-PIN-EOL-GOV-1/gate-baseline.log` | `642088933d2c3a027647a82099ad4016d3baade0` | `ca54918ae5666307031c4e4819437ec305453e24468f503904a29f3de7daf7a7` | CANONICAL |

## Closeout Record

- 2026-11-11：ZCode 裁决登记 proposed；未释放、未实施。
- 2026-11-11：ZCode 独立 CLI 会话复核 DIAG-ACL-1 终态后裁决释放（[adjudication](../reviews/FEA-15-DIAG-ACL-1-zcode-adjudication-2026-11-11.md) §4）：status→ready，范围冻结为只读盘点（AC1–AC3），base=`1e58398aa07467004c1b329bb52095f63bcb78d4`；待 Owner 认领。
- 2026-11-11：Codex 在释放提交 `4173961dfe1b65256cb06d7628cc813b0603caa3` 认领并进入 `in_progress`；Owner=`codex`，Reviewer 预指定为新 ZCode 独立 CLI Review 会话；实现与 Review 会话必须分离。
- 2026-11-11：计数核对发现首版把 `doc/tasks/README.md` 算作 Task 卡；生成器现排除索引并从 HEAD 读取 Task/冻结来源。c6 探索 checkout 保留为补充快照；当前主线快照更新为 `948d73e0…`。此前 `18e1bd2…` 的 Handoff 因首版计数过时保留为历史记录。
- 2026-11-11：修正后 AC1–AC3 证据固定于 `ef625367…`；`gate-final.log` 在 `996f9768…` 记录两项 governance check、18 pins、API 全部 EXIT 0。修订 Handoff [FEA-15-PIN-EOL-GOV-1-996f976.md](../handoffs/FEA-15-PIN-EOL-GOV-1-996f976.md)，SHA-256 `6d29c8bcfadf3ed8bd0a611dd6cce4b874f001cc05e4c9e82e99ff4082954b2e`，commit `f70cb325abf481b9f0513ccddec620c810fdfaf3`。Canonical Evidence 4 项已回填，Task→`in_review`；delivery_head=`996f9768985ee121767bd750d24b1cdfe74dd186`，等待新 ZCode CLI Review。
- 2026-11-11：ZCode 独立 Review `sess_1ff7ce49-fa46-4cb8-b7a7-d2efcb347fdc` 对 delivery head `996f9768…` 作 `approved`；Architecture / Verification PASS，R-001 为 open P2 non-blocking。Review 报告 SHA-256 `5fa78bff…`，commit `d9c6360bb4cfcee970c0fe21f825e58b0d26df09`。
- 2026-11-11：ZCode adjudication `sess_8df67a95-be8f-4518-89fe-d71e950d9cff` 接受 r1 与 R-001 非阻断遗留；Task `in_review→approved`，要求集成验证、资源 closeout 后才能 `done`。裁决报告 SHA-256 `414c977e…`，commit `642088933d2c3a027647a82099ad4016d3baade0`。用户已授权 ZCode 裁决、Codex 继续执行。
- 2026-11-11：于干净 `main` HEAD=`d9c6360bb4cfcee970c0fe21f825e58b0d26df09` 实际运行四项集成门禁，时间 `13:43:55–13:43:57 +08:00`，default/TaskPath checks 各 PASS（4 warnings），pins 18/18 PASS，API 1/79/6=86；均 EXIT 0。日志在外部 agent-output，SHA-256 `37c2da16292f916696936796881bf2a4cf5653359f10e389aeebc4286b79c520`，资源清单 23/23 文件哈希核验一致。验证 head 作为 `integration_commit`；无 merge / push。
- 2026-11-11：R-001 保持 open P2 non-blocking；其 WORKTREE 基准限制与产品 pytest/.NET、Linux fresh clone、renormalize simulation `NOT_RUN` 均保留。资源 Manifest 三项均 `PRESERVE_REFERENCED`，资源检查完成，0 删除/迁移/归档。Task 已按 ZCode 裁决进入 `approved`；终态关闭因默认治理门禁要求 STATUS 有非终态当前 Task 指针，而本范围不能释放后继 Task，待 ZCode 对该状态约束裁决。
