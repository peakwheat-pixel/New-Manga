---
id: FEA-15-PIN-POLICY-1
title: 证据 pin 基准口径裁定与迁移影响面方案（裁定阶段，不含实施）
kind: governance
governance_version: 3
status: in_progress
approval: ZCode 2026-11-11 裁决释放（独立 CLI session sess_236d9541-8358-45f0-9318-4844a86a767e；doc/reviews/FEA-15-PIN-POLICY-1-zcode-release-adjudication-2026-11-11.md）；用户已授权持续推进、全部授权、自动计划及 ZCode 裁决
suggested_owner: codex
owner: codex
reviewer: ZCode 独立 CLI Review（执行时新建上下文；session ID 记入报告；不得使用实现会话）
depends_on:
  - FEA-15-PIN-EOL-GOV-1
base_commit: 4efc592d12c25b8be33502f53c9270ad0597adfd
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
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

- [ ] **AC1 全集增量刷新与正式裁定**：以 verification/FEA-15-PIN-EOL-GOV-1/pin-inventory.json 为基线，增量盘点基线快照至本 Task 交付 HEAD 之间新增或变化的 versioned evidence pin，生成覆盖交付 HEAD 的机器可复核全集与增量差异。产出 verification/FEA-15-PIN-POLICY-1/pin-basis-ruling.md，裁定：①新增 pin 默认 basis 及文本/二元文件规则；②既有全集分类处置原则；③check.ps1 r194 双基准语义的存续或收敛口径；④R-001 的关闭、转交或保留条件。各项分列事实、推论、未知项、反证条件、暂停门槛。引用基线时按互斥计数 3,451 + 327 + 999 + 573 = 5,350，并列明 573 的六类构成。交付前 AC1 任一子项未裁定则标 <<PARTIAL: 缺失子项>>，证据不足则标 <<BLOCKED: 具体原因>>，不得标 MET。
- [ ] **AC2 实施影响面方案（不含实施）**：若 AC1 提出的策略需要改 .gitattributes、checker 语义或历史 pin，产出实施 Task 冻结输入：受影响文件/pin 实测全集、代表与边界样本（含 binary 和 mixed-EOL）、固定 pre-change 基线错误矩阵、隔离 clone dry-run 方案、回退方案及实施 Task 边界草案。影响面不完整时标 <<PARTIAL: 缺失范围>>；若裁定维持现状且无需实施，记录依据、反证条件并明确无需实施 Task。dry-run 不在本卡执行，始终 NOT_RUN。
- [ ] **AC3 登记、复核与治理门禁**：R-001 处置登记在本卡 Closeout 和 evidence README；在交付 HEAD 实跑 default 与 -TaskPath governance check、18 pins 和 API inventory，逐条记录 HEAD、时点、命令、输出摘要及 EXIT。交付 Handoff 与 Canonical Evidence pin 完整；独立上下文 Reviewer 复核精确 delivery head；ZCode 作最终 adjudication。产品 pytest/.NET、Linux fresh clone、renormalize simulation 与任何迁移保持 NOT_RUN，不得写成 PASS。

AC 状态语法按 doc/09_COLLABORATION.md §4.3；进入 in_review 前所有 AC 必须具备合法且与勾选一致的 <<MET>>、<<PARTIAL: 原因>> 或 <<BLOCKED: 原因>> 标记。

## 允许修改范围

仅可修改 frontmatter allowed_paths 中的 Task、Review/Handoff、STATUS/Plan/Ledger 指针与本 Task 的 verification/FEA-15-PIN-POLICY-1/ 证据。任何新的共享校验器、契约、Schema、依赖、源码或历史 pin 变更均不在本范围。

## 测试要求

| 场景/AC | 计划命令或步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 复制并限定使用只读 inventory 生成器，盘点当前 tracked Task/FROZEN pin；与基线按来源/ID/path/commit 对比 | main 主树，固定 HEAD | NOT_RUN | 新 inventory 与运行日志 |
| AC2 | 对照现有 12 观察矩阵与完整 pin 差异制定影响集、边界样本和错误矩阵方案 | 不运行 clone 或 renormalize | NOT_RUN | pin-basis-ruling.md |
| AC3 | pwsh -NoProfile -File tools/governance/check.ps1；同命令加 -TaskPath doc/tasks/FEA-15-PIN-POLICY-1.md；pwsh -NoProfile -File tools/governance/verify_pins.ps1；python tools/generate_api_inventory.py --check | delivery HEAD | NOT_RUN | verification/FEA-15-PIN-POLICY-1/ |

## 依赖、风险与阻塞

硬依赖 FEA-15-PIN-EOL-GOV-1 已 done。AC1 只能以当前实测全集裁定；机器观察不单独证明 pin 损坏或授权迁移。若影响全集、受影响样本或基线错误矩阵无法界定，停止提出实施策略并记录 BLOCKED。

## 交付与运行记录

- Handoff：尚无。
- Review：ZCode 新独立 CLI Review session；ID 待 Review 委任时记录。
- 最终裁决者：ZCode 独立上下文 adjudication。
- 任何 NOT_RUN 保留原状态；完成本卡不代表后续迁移实施获授权。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (CANONICAL / SOURCE_PIN) |
|---|---|---|---|---|---|
| release-adjudication | Release authority | doc/reviews/FEA-15-PIN-POLICY-1-zcode-release-adjudication-2026-11-11.md | 0730335f835306a19d283f06dbc0164134a9e04e | 3912a32cdd434d7d6df8a61be3d758600adc92d27f0e6c00cd4c4791a57b2092 | CANONICAL |
| release-gates | AC3 release baseline | verification/FEA-15-PIN-POLICY-1/release-gates-0730335.log | be4efb395a5dcf5fb03f51e48813b7c046f0d469 | 18258a64e59ed4387b85c07c5598ebf681f429a0e1edb5dc39f18afbe0e2682e | CANONICAL |


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
- canonical_evidence_status：pending。
- resource_closeout_status：pending。
- 删除、迁移、归档数量/字节数：0；本卡禁止资源清理。
- 未关闭项及保留原因：AC 执行、Review、ZCode adjudication 待完成。
- 当前指针清理：完成时更新 STATUS / Plan / Task Ledger；rolling checkpoint 随执行更新。
