---
id: GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1
title: 七项历史运行身份的精确解释层实现（含用户数据保护补齐）
kind: feature
governance_version: 2
status: done
approval: user_authorization_20261022_dsh_coordinator_takeover
suggested_owner: dsh
owner: dsh
reviewer: antigravity
depends_on: [GOV-RESIDUAL-RUNTIME-IDENTITY-1]
base_commit: 8e31aaa1dff113e5f95ca7db5ece0de00126059a
branch: null
worktree: G:/CODEX/New Manga（主 checkout 交付；开发区为 linked worktree G:/CODEX/New Manga.workspace/worktrees/GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1）
integration_commit: 3264e0b61ea509ff1cd0db46be85567a0a0adb25
delivery_head: d4ac5452514f54147cff2bfd087ecf36305db947
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1
allowed_paths:
  - tools/governance/clean_workspace.py
  - tools/governance/residual-runtime-identity.json
  - tools/governance/tests/test_residual_runtime_identity.py
  - doc/tasks/GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1.md
  - doc/handoffs/GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - verification/GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1/
---

# GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1：七项历史运行身份的精确解释层实现

## 来源与目标

来源：`GOV-RESIDUAL-RUNTIME-IDENTITY-1`（r2 approved）的取证矩阵 `verification/GOV-RESIDUAL-RUNTIME-IDENTITY-1/matrix.md`。矩阵结论：7 项残余声明错误中，E6/E7 对应真实用户数据目录 `C:/Users/49745/AppData/Roaming/com.newmanga.m2rc1.desktop` 的 `catalog`/`data`/`derived`，当前 `hits=0` 完全无保护；其余五项（E1–E5）无现存资源、无保护缺口。

目标：新增一个**独立、字节绑定、精确到单条声明**的历史运行身份解释层，把 7 项声明映射为显式身份（E1–E3 `ALREADY_ABSENT` 非保护身份、E4 `NON_IDENTITY_RECORD`、E5 `NON_IDENTITY_PROSE`、E6/E7 `PRESERVE_ROOTS` 真实保护根），使生产扫描的 7 项 fatal 错误降为 0，同时：
- 不修改任何历史原件字节（`doc/tasks/P19.md`、两份 `resource-manifest.json`）；
- 不修改已批准的 `historical-evidence-interpretation.json`、`broad-root-preservation.json` 及其摘要/数量断言；
- 不降低 fail-closed：非绑定错误、policy 字节漂移、origin 字节漂移、目标存在性变化任一发生即失败；
- 保护集合只增不减：原有的 1934 个保护根必须仍是新集合的真子集，并新增 APPDATA 三个保护根。

## Acceptance Criteria

- [ ] AC1 新增 `tools/governance/residual-runtime-identity.json`（schema_version 1、purpose、approved_research、7 个 bindings），canonical JSON SHA-256 由硬编码常量 `RESIDUAL_RUNTIME_IDENTITY_DIGEST` 绑定；未跟踪、缺失、摘要不符、字段增减均 fail-closed。
- [ ] AC2 新增 `_apply_residual_runtime_identity(index, scanned)`，挂在 `_apply_historical_evidence_interpretation` 之后；逐项校验 origin 文件 raw SHA-256、字节长度、行号与行内容 SHA、错误身份（code/message/file/locator）唯一匹配；上游解释失败时拒绝叠加。
- [ ] AC3 身份落地：E1–E3 注册 `ALREADY_ABSENT` 非保护身份且断言目标不存在；E4/E5 不注册任何身份；E6/E7 为 `catalog`/`data`/`derived` 注册保护根（E6 `PRESERVE_REFERENCED`、E7 `PRESERVE_USER_DATA`）。
- [ ] AC4 每项原 fatal 错误替换为 `DECL_RESIDUAL_RUNTIME_PRESERVED` warning，内容含 policy、binding id、kind、origin、行号、raw sha256、declared text 与 provenance，可逐项审计。
- [ ] AC5 生产 `--audit-declarations` 的 **7 项历史错误身份降为 0**（不以绝对计数为断言，遵守 r2 口径条款）；EXIT 由 2 变 0；原保护根集合为新集合真子集；新增 APPDATA 三根；无 `.tmp*` 或 `%TEMP%` 展开。
- [ ] AC6 负例全部 fail-closed 且有测试：policy 摘要错误、policy 正文篡改、origin 字节漂移、`ALREADY_ABSENT` 目标复活、保护目标缺失、未绑定错误存在、保护集合回退。
- [ ] AC7 `python -B tools/governance/tests/test_residual_runtime_identity.py`、`pwsh -NoProfile -File tools/governance/check.ps1`、`git diff --check` 真实运行并记录命令与 EXIT；固定 head 交独立 Reviewer；集成复验后才 done。

## 允许修改范围

- `tools/governance/clean_workspace.py`：新增 policy 路径常量、摘要常量、加载/校验/应用函数，并在 `scan_repo_declarations` 末尾挂接；不改任何既有解析、判定、错误码语义。
- `tools/governance/residual-runtime-identity.json`（新增）。
- `tools/governance/tests/test_residual_runtime_identity.py`（新增）。
- 本 Task、本 Task Handoff、`verification/GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1/`。
- 权威导航：`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`。

## 禁止范围

- 不修改 `doc/tasks/P19.md`、`verification/ENV-BUNDLE-1-FU1/resource-manifest.json`、`verification/P19-UI-FIX-1/resource-manifest.json` 或任何历史原件字节。
- 不修改 `historical-evidence-interpretation.json`、`broad-root-preservation.json`、`non-declaration-json-exceptions.json`、`resource-manifest.schema.json` 及其摘要常量与数量断言。
- 不全局忽略任何错误码；不按 `%TEMP%`/`%APPDATA%` 变量名整体豁免；不新增按前缀/正则忽略通道；不展开任何通配符。
- 不做任何真实删除、迁移、归档、GC、prune、push、reset、stash；不解除 r212；不缩小既有保护集合；不动用户未提交内容。
- 不修改产品代码、Schema、共享契约或依赖；不合并 Legacy 分支。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1–AC4、AC6 | `python -B tools/governance/tests/test_residual_runtime_identity.py` | Python 3.14.6 / main | NOT_RUN | 待填 |
| AC5 | `python -B tools/governance/clean_workspace.py --audit-declarations --out <workspace>` | Python 3.14.6 / main | NOT_RUN | 待填 |
| AC7 | `pwsh -NoProfile -File tools/governance/check.ps1`；`git diff --check` | pwsh 7.6.6 | NOT_RUN | 待填 |

## 依赖、风险与阻塞

- 硬依赖：`GOV-RESIDUAL-RUNTIME-IDENTITY-1`（r2 approved）。矩阵与历史展开值是本 Task 唯一数据来源。
- 风险 1：新增阶段与既有两个阶段的顺序耦合。缓解：挂在最后，只对精确匹配的 7 条生效，其余一律 fail-closed。
- 风险 2：`ALREADY_ABSENT` 目标复活后不应继续保持「不存在」断言。缓解：加载时断言目标确实不存在，存在即 `RESIDUAL_TARGET_PRESENT`。
- 风险 3：linked worktree 无法运行完整 audit（HIE policy 依赖主仓 untracked 的 P22 原件，worktree 中不存在）。缓解：交付在主 checkout 完成与验证；linked worktree 仅保留为开发记录（`codex/gov-residual-runtime-identity-impl-1`，PRESERVE_REFERENCED）。
- 风险 4：本次交付自身文档若含被审计拒绝的写法会重演自指错误（r1 R-002）。缓解：交付前以「7 项历史错误身份降为 0」为断言，并对本 Task 文档执行一次 audit 纳入证据。
- 阻塞：无。

## 交付与运行记录

- Handoff：doc/handoffs/GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1.md。
- 2026-10-22 / dsh / base 8e31aaa1d：实现完成。生产声明审计 7 项历史错误降为 0（2639/1936/7/285 → 2648/1939/0/292，exit 2→0）；保护集合旧 1936 根为新 1939 根真子集，新增 APPDATA catalog/data/derived 三根；无通配或环境变量展开；新增 12/12 测试与既有治理测试全绿；治理检查 PASS(2 warnings)、git diff --check exit 0。真实资源操作 0/0/0。

- Review：待独立 Reviewer（Antigravity）审查固定 head；本表在交付提交 `d4ac5452514f54147cff2bfd087ecf36305db947` 上回填。
- 实际测试：待填。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-01 | AC3/AC5 | verification/GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1/protection-delta.json | `d4ac5452514f54147cff2bfd087ecf36305db947` | `98b08f0863b004571817bb9497d4c8af5c8240fe1fac387e61322d3b60406123` | CANONICAL |
| EV-02 | AC7 | verification/GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1/verification-log.txt | `d4ac5452514f54147cff2bfd087ecf36305db947` | `7cdb25e85659b7368206930ae23b128ddf3ed9fee633170a34f26680aa69b849` | CANONICAL |
| EV-03 | AC5 | verification/GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1/raw/audit-baseline/declaration-audit.json | `d4ac5452514f54147cff2bfd087ecf36305db947` | `f4c77a86de9f269aa8bcce7a1b3b452a958eebdf7f0068b4f9c8f9afb77fd01f` | CANONICAL |
| EV-04 | AC5 | verification/GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1/raw/audit-resolved/declaration-audit.json | `d4ac5452514f54147cff2bfd087ecf36305db947` | `060637cc68ce4298a9dc7635cc3ba1e6240aa86c7590884a88cc0d227ccaf984` | CANONICAL |
| EV-05 | AC1 | tools/governance/residual-runtime-identity.json | `d4ac5452514f54147cff2bfd087ecf36305db947` | `2ce5cc2ef67725ed68efbaac908abc51bbc0115d4ec752d33047820fe07dc384` | CANONICAL |
| EV-06 | AC2/AC3 | tools/governance/clean_workspace.py | `d4ac5452514f54147cff2bfd087ecf36305db947` | `a9b329597ebd81941de6e1de0b0941b7b7bb582745326c62304dcca942d1b295` | CANONICAL |
| EV-07 | AC1-AC6 | tools/governance/tests/test_residual_runtime_identity.py | `d4ac5452514f54147cff2bfd087ecf36305db947` | `03cd671d9ebd05b36fd67719269b19264e6c62400ec21aa2446630e41f06a7c2` | CANONICAL |
| EV-08 | Review | verification/GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1/raw/agy-review-run1.json | `3264e0b61ea509ff1cd0db46be85567a0a0adb25` | `384f9ffeb9b003713c1b1a58db4333edfdabf08f9b398797331bcfdf819dde77` | SOURCE_PIN |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga | PRESERVE_REFERENCED | 同路径 | doc/tasks/GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1.md | 主 checkout，交付与验证在此 |
| worktree | G:/CODEX/New Manga.workspace/worktrees/GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1 | PRESERVE_REFERENCED | 同路径 | doc/handoffs/GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1.md | 开发记录 worktree，分支 `codex/gov-residual-runtime-identity-impl-1`；按 r212 禁令保留，不合并、不删除 |
| agent-output | G:/CODEX/New Manga.workspace/temp/GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1 | PRESERVE_REFERENCED | 同路径 | verification/GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1/ | 运行日志与中间产物 |
| task-env/dataset/model/test-material | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 本 Task 不使用隔离环境、模型、数据集或测试物料 |

## Closeout Record

- Closeout date / dsh：2026-10-22。
- canonical_evidence_status：`complete`（EV-01..EV-07 pin 到交付 `d4ac54525`；EV-08 为 Review 原始 JSON 的 SOURCE_PIN）。
- resource_closeout_status：`complete`。
- 删除、迁移、归档数量/字节数：0 / 0 / 0；GC/prune/push/reset/stash 均 0。
- 未关闭项及保留原因：无未关闭交付项。Antigravity 唯一 P2 观察（历史遗留 ResourceWarning）不阻塞且已标记 CLOSED。
- 集成复验（`3264e0b61`）：audit 0 errors / 1945 保护根 / EXIT 0；check PASS；diff-check 0；Review approved；见 `verification/GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1/integration/`。
- 当前指针清理：STATUS / Rebaseline Plan / Task Ledger 已同步；本 Task 之后无 READY 节点。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：0 / 0 / 0。
- 未关闭项及保留原因：待填写。
- 当前指针清理：待关闭时同步。
