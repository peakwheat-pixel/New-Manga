---
id: GOV-RESIDUAL-RUNTIME-IDENTITY-1
title: 七项剩余历史运行身份的只读取证与裁决边界
kind: research
governance_version: 2
status: in_review
approval: user_authorization_20261022_dsh_coordinator_takeover
suggested_owner: dsh
owner: dsh
reviewer: zcode
depends_on: [GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1]
base_commit: 43a7d73c850f669cc2595343a1747a661c277f2e
branch: null
worktree: G:/CODEX/New Manga（只读研究；仅在 main 写本 Task、自身 evidence 与权威导航）
integration_commit: null
delivery_head: bb04c78d4b39e93e07712b2d056a2691810c0c58
canonical_evidence_status: complete
resource_closeout_status: pending
evidence_dir: verification/GOV-RESIDUAL-RUNTIME-IDENTITY-1
allowed_paths:
  - doc/tasks/GOV-RESIDUAL-RUNTIME-IDENTITY-1.md
  - doc/handoffs/GOV-RESIDUAL-RUNTIME-IDENTITY-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - verification/GOV-RESIDUAL-RUNTIME-IDENTITY-1/
---

# GOV-RESIDUAL-RUNTIME-IDENTITY-1：七项剩余历史运行身份的只读取证与裁决边界

## 来源与目标

来源：`doc/REBASELINE_PLAN.md` 中 `GIT-MAINLINE-CONVERGENCE-1` 的 7 项残余声明错误；`doc/reviews/WORKSPACE-DECLARATION-REMEDIATION-1-66e597282-codex-r1.md` 第 4 节逐条裁定这七项「保留 fatal，另立 Task 裁定」，并明确要求逐项确认目标、不按变量名整体豁免、解析到具体规范路径并记录依据；`doc/handoffs/GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1.md` 的后续候选七字段。

目标：在不修改任何历史原件字节、不改变解析器 fail-closed 语义、不进行任何真实资源处置的前提下，对当前 `main` 的 7 项残余声明错误逐项固定完整身份，取证其历史运行环境展开值、引用与归属，判定是否存在仍需保护的真实资源与保护缺口，并给出「技术可解决 / 需用户裁决」分类及最小裁决清单。交付一个可被后续实施 Task 直接消费的逐项矩阵。

## Acceptance Criteria

- [ ] AC1 七项错误以 `python -B tools/governance/clean_workspace.py --audit-declarations` 在生产 `main` 实跑复现，完整身份（code/message/file/locator）、原文行、归属 Task 逐项固定，且计数与 exit code 记录真实命令与 EXIT。
- [ ] AC2 每项涉及的历史 `%TEMP%`/`%APPDATA%` 展开值给出可核验来源证据，并显式区分 FACT / INFERENCE / UNKNOWN；不得用当前环境变量值直接推断历史值。字节级交叉校验（当前文件 SHA-256 与历史记录比对）逐项给出相等/不等结论。
- [ ] AC3 每项的错误归属、引用链（Task/Review/Handoff/证据）与「可证明的实际路径」记录；实际路径存在性以只读文件系统检查结论为准。
- [ ] AC4 用只读保护评估证明每一项的「现存真实资源」与「保护缺口」结论；保护评估不改解析器、不修改仓库，脚本随证据入库可复现。
- [ ] AC5 交付逐项矩阵：事实/推论/未知、是否需要保护、是否可由技术方案解决、需用户裁决对象与最小裁决；本 Task 不实施清理、不改原件、不改解析器语义。
- [ ] AC6 `pwsh -NoProfile -File tools/governance/check.ps1` 与 `git diff --check` 真实运行并记录 EXIT；固定 head 交独立 Reviewer；集成复验后才可 done。

## 允许修改范围

- 本 Task：`doc/tasks/GOV-RESIDUAL-RUNTIME-IDENTITY-1.md`。
- 本 Task Handoff：`doc/handoffs/GOV-RESIDUAL-RUNTIME-IDENTITY-1.md`。
- 本 Task 证据：`verification/GOV-RESIDUAL-RUNTIME-IDENTITY-1/`（含 `raw/`、只读探针脚本）。
- 权威导航同步：`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`（由 `tools/governance/task_ledger.py --write` 生成）。
- 临时产物仅在 `G:/CODEX/New Manga.workspace/temp/GOV-RESIDUAL-RUNTIME-IDENTITY-1/`，不进入 Git。

## 禁止范围

- 不修改 `doc/tasks/P19.md`、`verification/ENV-BUNDLE-1-FU1/resource-manifest.json`、`verification/P19-UI-FIX-1/resource-manifest.json` 或任何历史原件字节。
- 不修改 `tools/governance/clean_workspace.py`、`tools/governance/resource-manifest.schema.json`、`tools/governance/historical-evidence-interpretation.json`、`tools/governance/non-declaration-json-exceptions.json` 或任何解析器语义。
- 不进行真实删除、迁移、归档、GC、prune、push、reset、stash、ACL 变更；不解除 r212 禁令；不动五广域根、P22 untracked 内容、旧 pin、六个 DSH 旧探针。
- 不提交、覆盖、丢弃或移动任何用户未提交内容；不猜 `%TEMP%`/`%APPDATA%`/`%LOCALAPPDATA%` 历史位置。
- 不新增运行例外、不全局忽略任何错误码、不缩小既有保护集合。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | `python -B tools/governance/clean_workspace.py --audit-declarations --out <workspace>/temp/GOV-RESIDUAL-RUNTIME-IDENTITY-1/audit` | pwsh 7.6.6 / Python 3.14.6 / main `43a7d73c8` | PASS：2627 declarations / 1926 protected roots / 7 errors / 276 warnings，EXIT=2；7 项身份与既有记录逐字一致 | `raw/audit-run.log`、`raw/declaration-audit.json` |
| AC2 | 读取 tracked 证据记录 + 当前文件 `Get-FileHash` 交叉校验 | 只读 | PASS：`%TEMP%`、`%APPDATA%` 历史展开值均有独立 tracked 明文证据；3/4 关键文件字节相等，1 项 delta 已解释 | `historical-env-evidence.json` |
| AC3 | `Test-Path` / `git worktree list` / `git grep` 引用检索 | 只读 | PASS：逐项归属与实际路径存在性已固定 | `matrix.md` |
| AC4 | `python -B verification/GOV-RESIDUAL-RUNTIME-IDENTITY-1/probe-protected.py` | 只读，解析器仅 no-op `finalize` 用于取已建索引 | PASS：`%APPDATA%/…` 四路径 hits=0（缺口）；其余目标 hits>0 或无资源 | `raw/protection-evaluation.json` |
| AC5 | 人工汇总矩阵 | 只读 | PASS：7 项全部技术可解，0 项需用户裁决 | `matrix.md` |
| AC6 | `pwsh -NoProfile -File tools/governance/check.ps1`；`git diff --check` | main | 见 `verification-log.txt` | `verification-log.txt` |

## 依赖、风险与阻塞

- 硬依赖：`GOV-HISTORICAL-EVIDENCE-INTERPRETATION-IMPL-1`（done，集成 `457485207`），其已建立的历史证据解释机制与「原始字节保留 + 精确绑定」先例是本 Task 结论的前提。
- 风险 1：`probe-protected.py` 需 no-op `ProtectionIndex.finalize` 才能读取带 7 错误的索引；该 no-op 仅存在于本 Task 证据脚本，不写入生产代码，且脚本明确注释。已通过「不改解析器」约束隔离。
- 风险 2：`%TEMP%`/`%APPDATA%` 历史值若被后续证据推翻，字节交叉校验会失败；届时矩阵结论需重开。
- 未定契约：是否引入「历史运行身份解释层」及其配置形态由后续实施 Task 冻结；本 Task 不预先承诺实现细节。
- 阻塞：无。

## 交付与运行记录

- Handoff：`doc/handoffs/GOV-RESIDUAL-RUNTIME-IDENTITY-1.md`。
- Review：待独立 Reviewer（ZCode）对固定 head 审查（本次取交付提交 `bb04c78d4b39e93e07712b2d056a2691810c0c58`）。
- 实际测试：见「测试要求」表与 `verification-log.txt`。
- 2026-10-22 / dsh / base `43a7d73c8`：只读取证完成；7 项身份固定；唯一真实保护缺口为 `C:/Users/49745/AppData/Roaming/com.newmanga.m2rc1.desktop`（用户数据，hits=0）。真实资源操作 0。
- 交付提交 `bb04c78d4b39e93e07712b2d056a2691810c0c58`：Task + Handoff + 证据 + STATUS/Plan/Ledger 同点提交；随后转 `in_review` 等待独立 Review。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-01 | AC1 | verification/GOV-RESIDUAL-RUNTIME-IDENTITY-1/raw/audit-run.log | `bb04c78d4b39e93e07712b2d056a2691810c0c58` | `bb8d0c6b4fa854a87f5a80fb2674203ad81ef0e15b0bbe3530492e9b08c6366d` | CANONICAL |
| EV-02 | AC1 | verification/GOV-RESIDUAL-RUNTIME-IDENTITY-1/raw/declaration-audit.json | `bb04c78d4b39e93e07712b2d056a2691810c0c58` | `7d4b258a7f949782fe037d0c9501e4f2eff799affaf253934d094f71f1ac6ba9` | CANONICAL |
| EV-03 | AC2 | verification/GOV-RESIDUAL-RUNTIME-IDENTITY-1/historical-env-evidence.json | `bb04c78d4b39e93e07712b2d056a2691810c0c58` | `c1d08c392902ef5f1519ca5204da6598fc2fbb5e4ec52d131491b52f4313eaf9` | CANONICAL |
| EV-04 | AC3/AC5 | verification/GOV-RESIDUAL-RUNTIME-IDENTITY-1/matrix.md | `bb04c78d4b39e93e07712b2d056a2691810c0c58` | `41859b5cc7b30215ad8c7ccafc372e2effe19adbed53767321b9a2aa684cfb5f` | CANONICAL |
| EV-05 | AC4 | verification/GOV-RESIDUAL-RUNTIME-IDENTITY-1/raw/protection-evaluation.json | `bb04c78d4b39e93e07712b2d056a2691810c0c58` | `956999fa5761031d816e8b622593d8b0aea745cf2cd3a85658f937bddc56b380` | CANONICAL |
| EV-06 | AC4 | verification/GOV-RESIDUAL-RUNTIME-IDENTITY-1/probe-protected.py | `bb04c78d4b39e93e07712b2d056a2691810c0c58` | `8078c82cd8b1226a96e71d40beef32e1f25ed6f0a7ce6fd8829af74c19644770` | CANONICAL |
| EV-07 | AC6 | verification/GOV-RESIDUAL-RUNTIME-IDENTITY-1/verification-log.txt | `bb04c78d4b39e93e07712b2d056a2691810c0c58` | `332177d6dbc93671a1f79083275adee5622a97504f00ed40b2a6bdf1fc6ec0d7` | CANONICAL |

本表在交付提交 `bb04c78d4b39e93e07712b2d056a2691810c0c58` 上回填实际 raw sha256；`delivery_head` 指向同一交付提交。随后仅追加状态/Review 记录，不改变上述证据字节（BL-15：EV 不指向自引用 SHA）。

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | G:/CODEX/New Manga.workspace/temp/GOV-RESIDUAL-RUNTIME-IDENTITY-1 | PRESERVE_REFERENCED | 同路径 | verification/GOV-RESIDUAL-RUNTIME-IDENTITY-1/raw/audit-run.log | 只读研究临时产物；仓库内已有等价 canonical 副本；保留不删 |
| worktree | G:/CODEX/New Manga | PRESERVE_REFERENCED | 同路径 | doc/tasks/GOV-RESIDUAL-RUNTIME-IDENTITY-1.md | 本 Task 在 main 主 checkout 只读研究并仅写允许路径；未新建 branch/worktree |
| branch | refs/heads/main | PRESERVE_REFERENCED | 同路径 | doc/STATUS.md | 未创建新分支 |
| task-env/dataset/model/test-material | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 本 Task 不使用隔离环境、模型权重、数据集或测试物料 |
| temp（系统 Temp） | C:/Users/49745/AppData/Local/Temp/p19*（11 个现存目录，约 1.9 MiB） | PRESERVE_UNKNOWN | 同路径 | historical-env-evidence.json | 非本 Task 产生；仅登记，不删除不迁移；清理需另行授权 |

## Closeout Record

- Closeout date / dsh：待独立 Review 与集成复验后填写。
- canonical_evidence_status：`complete`（7 项 EV 固定到交付提交 `bb04c78d4b39e93e07712b2d056a2691810c0c58`，raw SHA-256 已回填）。
- resource_closeout_status：`pending`（无真实删除/迁移；四项资源均为保留或 NOT_APPLICABLE）。
- 删除、迁移、归档数量/字节数：0 / 0 / 0。
- 未关闭项及保留原因：7 项声明错误仍为 fatal（本 Task 只取证，不解除）；`C:/Users/49745/AppData/Roaming/com.newmanga.m2rc1.desktop` 保护缺口待实施 Task 补齐；11 个 `p19*` 系统 Temp 目录待用户授权后另议。
- 当前指针清理：STATUS / Rebaseline Plan / Task Ledger 已同步，或在本 Task done 时同步。
