---
id: FEA-15-PIN-POLICY-1
title: 证据 pin 基准口径裁定与迁移影响面方案（裁定阶段，不含实施）
kind: governance
governance_version: 3
status: in_review
approval: ZCode 2026-11-11 裁决释放（独立 CLI session sess_236d9541-8358-45f0-9318-4844a86a767e；doc/reviews/FEA-15-PIN-POLICY-1-zcode-release-adjudication-2026-11-11.md）；用户已授权持续推进、全部授权、自动计划及 ZCode 裁决
suggested_owner: codex
owner: codex
reviewer: ZCode 独立 CLI Review（即将新建上下文；session ID 在 Review 报告与本卡回填）
depends_on:
  - FEA-15-PIN-EOL-GOV-1
base_commit: 4efc592d12c25b8be33502f53c9270ad0597adfd
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: 359d09dffc489c8762727cf69b778cba6f432843
canonical_evidence_status: complete
resource_closeout_status: pending
evidence_dir: verification/FEA-15-PIN-POLICY-1
allowed_paths:
  - doc/tasks/FEA-15-PIN-POLICY-1.md
  - doc/reviews/FEA-15-PIN-POLICY-1-*.md
  - doc/handoffs/FEA-15-PIN-POLICY-1-*.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - verification/FEA-15-PIN-POLICY-1/**
out_of_scope:
  - 禁止修改 .gitattributes、renormalize、历史 evidence/pin、冻结契约或 FROZEN 记录、源码、Schema、依赖
  - 禁止修改 check.ps1、verify_pins.ps1、task_ledger.py 的代码或校验语义；r194 只作口径裁定
  - 禁止实施 pin 迁移、历史 pin 改写、renormalize dry-run；若裁定提出实施，必须另开 Task 并独立授权与 Review
  - 禁止重开或改写 FEA-15-ACCEPT-1、FEA-15-DIAG-ACL-1、FEA-15-PIN-EOL-GOV-1
  - 禁止清理、迁移或归档资源；禁止 push
  - 禁止用历史比例 27/30、187/300 推断全集；以当前实测 pin inventory 为准
---

# FEA-15-PIN-POLICY-1：证据 pin 基准口径裁定与迁移影响面方案

## 来源与目标

依赖 FEA-15-PIN-EOL-GOV-1 的全量只读盘点、跨 checkout 观察矩阵和候选策略分析。其基线 inventory 于 HEAD 948d73e0629869e560df9a2b2d8a357cec67027f 记录 5,350 行：WORKTREE=3,451、BLOB=327、MIXED=999、另外 573 行不属于这三类；其中 573 行细分为 INCONSISTENT=160、UNPINNED=293、UNRESOLVED_COMMIT=68、EXTERNAL_UNAVAILABLE=47、MISSING=3、COMPOSITE_PATH=2。各类别互斥，总计 5,350。原候选分析中的并列句式将 160 子集与 573 并列；本 Task 不修改历史文件，后续裁定只按互斥口径引用。

目标是在不改任何历史 pin、契约或校验器的前提下，对新 pin 缺省基准、既有 pin 分类原则、check.ps1 r194 双基准语义以及 R-001 作出有核验依据的裁定，并冻结任何后续实施所需的影响面方案。本卡只授权裁定和方案，不授权实施。

## Acceptance Criteria

- [ ] **AC1 全集增量刷新与正式裁定**：交付 inventory `5,376` 行，baseline delta `+26 / -0 / changed 0`；裁定提案、事实/推论/未知/反证/暂停门槛均已写入。最终政策仍待 ZCode adjudication。 <<PARTIAL: ZCode 独立 Review 与最终 adjudication 尚未完成>>
- [x] **AC2 实施影响面方案（不含实施）**：影响全集、互斥 basis/异常分类、4 种代表与边界样本、固定 r194 predicate matrix、dry-run/rollback 方案和 successor Task 边界已登记；矩阵为 inventory predicate 模型而非逐行执行 checker，clone dry-run 依要求保持 NOT_RUN。 <<MET>>
- [ ] **AC3 登记、复核与治理门禁**：delivery/review head `359d09dffc489c8762727cf69b778cba6f432843` 的 default/current/prior TaskPath、18 pins、API gate 均为 EXIT 0；复核日志记录当时 HEAD 与 dirty docs 状态，Handoff 已提交；独立 Review 与最终 adjudication 尚未完成。 <<PARTIAL: ZCode 独立 Review 与最终 adjudication pending>>

AC 状态语法按 doc/09_COLLABORATION.md §4.3；进入 in_review 前所有 AC 必须具备合法且与勾选一致的 <<MET>>、<<PARTIAL: 原因>> 或 <<BLOCKED: 原因>> 标记。

## 允许修改范围

仅可修改 frontmatter allowed_paths 中的 Task、Review/Handoff、STATUS/Plan/Ledger 指针与本 Task 的 verification/FEA-15-PIN-POLICY-1/ 证据。任何新的共享校验器、契约、Schema、依赖、源码或历史 pin 变更均不在本范围。

## 测试要求

| 场景/AC | 计划命令或步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | `python verification/FEA-15-PIN-POLICY-1/pin_inventory.py`；`python verification/FEA-15-PIN-POLICY-1/pin_inventory_delta.py` | `main`，delivery measurement HEAD `e9f7bb1b48c885cb329848d2d3591e145ff3d229` | `5,376` 行；delta `+26 / -0 / changed 0`；两命令 `EXIT=0`。正式裁定仍 PARTIAL。 | `pin-inventory.json`、`pin-inventory-delta.json`、对应 run logs、`pin-basis-ruling.md` |
| AC2 | `python verification/FEA-15-PIN-POLICY-1/pin_r194_matrix.py`；制定 future isolated-clone dry-run | inventory fixed at delivery HEAD；当前 Task 不创建 clone | modeled predicate `4,803` match / `573` nonpass；matrix 命令 `EXIT=0`。Dry-run `NOT_RUN`，实现不在本卡范围。 | `pin-r194-baseline-matrix.json`、run log、`pin-basis-impact-plan.md` |
| AC3 | `pwsh -NoProfile -File tools/governance/check.ps1`；加 `-TaskPath doc/tasks/FEA-15-PIN-POLICY-1.md`；prior TaskPath；`pwsh -NoProfile -File tools/governance/verify_pins.ps1`；`python tools/generate_api_inventory.py --check` | `main`，review delivery HEAD `359d09d...` | default/current/prior checks PASS (各 3 warnings)，18 pins PASS `18/18`，API `1/79/6=86`；5 commands 均 `EXIT=0`。Review/adjudication `NOT_RUN`。日志记录 generation HEAD `359d09d...` 与当时 dirty docs。 | `delivery-gates-359d09d.log`、Handoff；Review 与 adjudication 待补 |

## 依赖、风险与阻塞

硬依赖 FEA-15-PIN-EOL-GOV-1 已 done。AC1 只能以当前实测全集裁定；机器观察不单独证明 pin 损坏或授权迁移。若影响全集、受影响样本或基线错误矩阵无法界定，停止提出实施策略并记录 BLOCKED。

## 交付与运行记录

- Handoff：[`FEA-15-PIN-POLICY-1-e9f7bb1.md`](../handoffs/FEA-15-PIN-POLICY-1-e9f7bb1.md)，review delivery head `359d09d...`。
- Review：ZCode 新独立 CLI Review session；当前卡提交后新建，session ID 与结论写入 Review 报告并回填。
- 最终裁决者：ZCode 独立上下文 adjudication；必须使用与 Review 不同的 session。
- 任何 NOT_RUN 保留原状态；完成本卡不代表后续迁移实施获授权。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class |
|---|---|---|---|---|---|
| release-adjudication | Release authority | doc/reviews/FEA-15-PIN-POLICY-1-zcode-release-adjudication-2026-11-11.md | 0730335f835306a19d283f06dbc0164134a9e04e | 3912a32cdd434d7d6df8a61be3d758600adc92d27f0e6c00cd4c4791a57b2092 | CANONICAL |
| release-gates | AC3 release gates | verification/FEA-15-PIN-POLICY-1/release-gates-0730335.log | be4efb395a5dcf5fb03f51e48813b7c046f0d469 | 18258a64e59ed4387b85c07c5598ebf681f429a0e1edb5dc39f18afbe0e2682e | CANONICAL |
| final-ruling-proposal | AC1 ruling proposal | verification/FEA-15-PIN-POLICY-1/pin-basis-ruling.md | 359d09dffc489c8762727cf69b778cba6f432843 | 625a8fd59389796878b2113f97861ac8749e973536a3fc8fc47c32a418837d9c | CANONICAL |
| impact-plan | AC2 implementation impact plan | verification/FEA-15-PIN-POLICY-1/pin-basis-impact-plan.md | 359d09dffc489c8762727cf69b778cba6f432843 | 05cb2582d56ab11f1de8ad30d4a6b6ff41632b1655c5e6e2a68a526f94cd3699 | CANONICAL |
| final-inventory | AC1 delivery-head inventory | verification/FEA-15-PIN-POLICY-1/pin-inventory.json | 19ccd9b60f319c632ee034db38b235364e594da6 | e38b7d2279177ea701fc7e7e10afa7f8ef3bbe4414cecbb81529a2c8feecef56 | CANONICAL |
| inventory-run-log | AC1 inventory command and EXIT | verification/FEA-15-PIN-POLICY-1/pin-inventory-run.log | 19ccd9b60f319c632ee034db38b235364e594da6 | 353ce82aeecb60b816800878dd1ed895b4eb48c6fe4391319ec9ecdfc0e5ea5f | CANONICAL |
| baseline-delta | AC1 baseline delta | verification/FEA-15-PIN-POLICY-1/pin-inventory-delta.json | 19ccd9b60f319c632ee034db38b235364e594da6 | 27ab6ac6f3e1c2213d6bfcd6acec11d16c94f1025a1e02abb0465bb90c523323 | CANONICAL |
| baseline-delta-run | AC1 delta command and EXIT | verification/FEA-15-PIN-POLICY-1/pin-inventory-delta-run.log | 19ccd9b60f319c632ee034db38b235364e594da6 | 58175c83926f88d260d50dd1848444b89ca7dbed29f73e0f03bf962c38dbade6 | CANONICAL |
| r194-matrix | AC2 modeled r194 predicate matrix | verification/FEA-15-PIN-POLICY-1/pin-r194-baseline-matrix.json | 19ccd9b60f319c632ee034db38b235364e594da6 | a3ec66dd8b834f702db1b4a951997818d1b54e39a78dc0f8fcc26bc0db5bf832 | CANONICAL |
| r194-matrix-run | AC2 matrix command and EXIT | verification/FEA-15-PIN-POLICY-1/pin-r194-baseline-matrix-run.log | 19ccd9b60f319c632ee034db38b235364e594da6 | 4a2e251388f47dc410c0a712062d4eefdc3353b3e2d68f1e6ac4ec7c43c1c170 | CANONICAL |
| delivery-gates-inventory-head | AC3 initial inventory-head gate snapshot | verification/FEA-15-PIN-POLICY-1/delivery-gates-e9f7bb1.log | 19ccd9b60f319c632ee034db38b235364e594da6 | 80ed09fc2f6d72dcce78cd0721a754b07f708df7e5f4cfcede232d780161ea6b | CANONICAL |
| delivery-gates-final-review | AC3 final review-head governance gates | verification/FEA-15-PIN-POLICY-1/delivery-gates-359d09d.log | 89bb3fb27facee036c7a4402bb545c30478dea19 | 11531b0d524b7905caf9263c8d96e7baaa4b89ff003e5ffeed6867de8255a689 | CANONICAL |
| handoff | AC3 Handoff | doc/handoffs/FEA-15-PIN-POLICY-1-e9f7bb1.md | e02509282ce8e535f6cfd22a07c2b4e29023f963 | 38b166a26faf7d6d351466dfad6352582d63ea93f5e0532cb733aebe49d8d341 | CANONICAL |
| inventory-generator | AC1 inventory generator source | verification/FEA-15-PIN-POLICY-1/pin_inventory.py | da4a60baafba18281f156330b9ed1646045edb6d | 11e39fac240080a6f4ad10164aff35d2033742746a8f5c011042656b9948e7d7 | SOURCE_PIN |
| delta-generator | AC1 delta generator source | verification/FEA-15-PIN-POLICY-1/pin_inventory_delta.py | 1d48d9b13698e9b4d7e2549b26fc7795b957cb65 | 86312df973c7ed161cc0dc63cedf77211a59d5c985a5c6ac394cfdc9e295f9b0 | SOURCE_PIN |
| matrix-generator | AC2 matrix generator source | verification/FEA-15-PIN-POLICY-1/pin_r194_matrix.py | e9f7bb1b48c885cb329848d2d3591e145ff3d229 | 8239d1361f998c466d44fbf6ced189ee4ab3b4e61066fdf89397924527c6e7ff | SOURCE_PIN |
| preliminary-inventory | Process snapshot superseded by delivery inventory | verification/FEA-15-PIN-POLICY-1/pin-inventory-preliminary-da4a60b.json | 1d48d9b13698e9b4d7e2549b26fc7795b957cb65 | 43bd14469cb2e747fb058ea609a4f1da1744f597fe713487c4efb973fe97e66a | SOURCE_PIN |
| preliminary-inventory-run | Process snapshot generation log | verification/FEA-15-PIN-POLICY-1/pin-inventory-preliminary-run-da4a60b.log | 1d48d9b13698e9b4d7e2549b26fc7795b957cb65 | 213c0ab4362f2ae5ff119383804a7b592a83ad1fcfd37fecf8016d0304b1e2f2 | SOURCE_PIN |
| preliminary-delta | Process delta snapshot superseded by delivery delta | verification/FEA-15-PIN-POLICY-1/pin-inventory-preliminary-delta-da4a60b.json | 2ee6a5a024aede32a61e7907a865879eac7c8d70 | 0a2c3170915f8fad48ef643712e056488954ba825108cdbd59a38c22ce4f5e83 | SOURCE_PIN |
| preliminary-delta-run | Process delta generation log | verification/FEA-15-PIN-POLICY-1/pin-inventory-preliminary-delta-run-da4a60b.log | 2ee6a5a024aede32a61e7907a865879eac7c8d70 | 0a5cd6fafe94291efd5b8b50ae00b57b0ab1cb43471287f9234bc49524a966c5 | SOURCE_PIN |
| preliminary-matrix | Process matrix snapshot superseded by delivery matrix | verification/FEA-15-PIN-POLICY-1/pin-r194-preliminary-matrix-da4a60b.json | e9f7bb1b48c885cb329848d2d3591e145ff3d229 | c45574a2ce7cb28d8a6829e9429195cc53284e845e1fc0302eb590a633bf50da | SOURCE_PIN |
| preliminary-matrix-run | Process matrix generation log | verification/FEA-15-PIN-POLICY-1/pin-r194-preliminary-matrix-run-da4a60b.log | e9f7bb1b48c885cb329848d2d3591e145ff3d229 | 77ac1bceffd0ca6e2256504f411db667227732fac4005aecd309b9d118176bce | SOURCE_PIN |
| runtime-cache-delta-pyc | Generated Python import cache | verification/FEA-15-PIN-POLICY-1/__pycache__/pin_inventory_delta.cpython-314.pyc | - | dda056fa4642fa931fa7c0149171d1e6eab90adb017cbe531b84c44105533f42 | SOURCE_PIN |
| runtime-cache-matrix-pyc | Generated Python import cache | verification/FEA-15-PIN-POLICY-1/__pycache__/pin_r194_matrix.cpython-314.pyc | - | dff6adae289c6554ac074164b01adfb7a12c3280af81dec6daef950c38f6d41e | SOURCE_PIN |
| task-readme | Evidence directory index | verification/FEA-15-PIN-POLICY-1/README.md | 359d09dffc489c8762727cf69b778cba6f432843 | 0bed83904bb9915b759670795646c65dd9f1b6981bf75b37275bc94decd099e2 | SOURCE_PIN |
| rolling-checkpoint | Current Task recovery checkpoint | verification/FEA-15-PIN-POLICY-1/checkpoint.md | 359d09dffc489c8762727cf69b778cba6f432843 | 744e2909041bf0ee08769bfa5f33cce692a893da03bdd45c8a4190888a630eba | SOURCE_PIN |

## Resource Manifest

本 Task 不创建额外 checkout、task-env、dataset、model、安装包或 exchange；只使用已有 main worktree。所有新增判别证据写入本卡 evidence_dir，过程文件保留并在 closeout 明确登记。

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga | PRESERVE_REFERENCED | G:/CODEX/New Manga | main branch | Existing repository; no new worktree |
| task-env | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | No isolated environment created |
| dataset/model/test-material | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | No external test material used |
| artifact | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | No installer or build artifact created |
| temp | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | No external temporary files created |
| agent-output | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | No external agent output directory created |
| exchange | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | No exchange created |

## Closeout Record

- Closeout date / adjudicator：待 Review 与最终裁决时填写。
- canonical_evidence_status：complete。
- resource_closeout_status：pending。
- 删除、迁移、归档数量/字节数：0；本卡禁止资源清理。
- 未关闭项及保留原因：AC1 最终裁定、独立 Review、ZCode adjudication 待完成；R-001 保持 open P2，提案转交后续单独释放 Task。
- 当前指针清理：完成时更新 STATUS / Plan / Task Ledger；rolling checkpoint 随执行更新。
