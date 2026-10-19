---
id: GOV-RESOURCE-MANIFEST-JSON-1
title: 治理检查器支持外部 JSON Resource Manifest
kind: governance
governance_version: 2
status: in_progress
approval: codex_release_2026-10-19_after_GOV-PLAN-BUDGET-1_integration; user_decision_2026-10-19_scheme_D
suggested_owner: dsh
owner: dsh
reviewer: Antigravity
depends_on:
  - GOV-PLAN-BUDGET-1
base_commit: c131b1ae114d00c17e734a51f38263d92fe6f198
branch: GOV-RESOURCE-MANIFEST-JSON-1
worktree: G:/CODEX/New Manga/.agents/worktrees/GOV-RESOURCE-MANIFEST-JSON-1
integration_commit: null
delivery_head: 5ee07c2583c3d0adaf4edc778c2907baef24c350
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/GOV-RESOURCE-MANIFEST-JSON-1
allowed_paths:
  - tools/governance/check.ps1
  - tools/governance/resource-manifest.schema.json
  - tools/governance/tests/**
  - doc/tasks/GOV-RESOURCE-MANIFEST-JSON-1.md
  - doc/REBASELINE_PLAN.md
  - doc/STATUS.md
  - doc/handoffs/
  - doc/reviews/
  - verification/GOV-RESOURCE-MANIFEST-JSON-1/
---

# GOV-RESOURCE-MANIFEST-JSON-1：检查器支持外部 JSON Resource Manifest

## 来源与目标

依据 `verification/P09-GOVERNANCE-DEBT-20261019/codex-integration-closeout-r3.md` §2 判据 1–5，扩展治理检查器，使 Task 的 Resource Manifest 正文可唯一引用仓库 `verification/**` 范围内的外部 JSON，并按固定 schema 验证资源和 closeout 记录。保留原 JSON、原始 source/destination 表达式和 JSON 原值；不把无法证明的事实猜成路径、状态或处置。

## Acceptance Criteria

- [ ] **AC1 — 外部引用唯一且受限。** 检查器仅接受 Resource Manifest 正文中的一个明确相对仓库路径引用；目标必须唯一、存在、为普通文件并位于仓库 `verification/**` 证据范围内。拒绝重复、缺失、绝对路径、越出仓库或 `verification/**`、符号链接逃逸、glob、环境变量、宏、URL 或其它未授权简写；不得展开或猜测这些表达式。离线正反例须断言错误引用被拒绝且不会读取引用范围外文件。
- [ ] **AC2 — schema 与原值保真。** 新增固定版本 `tools/governance/resource-manifest.schema.json`，明确必填字段、类型、枚举、未知字段处理及资源数组和 closeout 计数规则。解析时保留每项原始 JSON 值以及原始 `source_path`、`destination_path` 表达式；规范化/解析结果必须是独立字段，不得覆盖原值。对可精确解析的路径逐项检查其存在性、仓库边界及本 Task 已定义的引用/进程证据；不能精确解析的表达式保留原文并报告不可验证，不自行展开 `%APPDATA%`、花括号或其它简写。
- [ ] **AC3 — 已消失资源的严格语义。** 对现在不存在的目标，仅当证据同时证明该资源曾列入被引用 Manifest、目标当前确实不存在、且无引用及运行中进程时，检查器才接受明确的 `ALREADY_ABSENT` 状态（或 schema 中等价且固定的枚举）。缺任一条件都必须失败或阻塞；不得用 `NOT_APPLICABLE` 表示已消失资源，不得伪造替代路径。对确实适用但尚无证据的资源也不得降格为 `NOT_APPLICABLE`。
- [ ] **AC4 — 花括号表达式可逆对应。** 仅当花括号表达式可无损拆分、按原顺序逐字重组为原 JSON 值，并能与原 JSON 的 7 个资源项及 `closeout_counts` 每项逐一对应时，才允许生成解析视图。保留原表达式和原 JSON 值；歧义、缺项、重项、重组不一致或计数不一致时保留输入并失败/阻塞。针对 P19 原 JSON 的解析核对不得修改该 JSON，也不得将不满足条件的数据自动修补成通过。
- [ ] **AC5 — 离线验证、交付及独立 Review。** 在 `tools/governance/tests/` 增加固定 schema 与离线用例，覆盖有效唯一引用、已有目标、目标缺失及 `ALREADY_ABSENT` 三条件全满足/逐条件缺失、错误/重复/缺失/越界/绝对/不存在引用、env/glob/宏/符号链接逃逸、非法 JSON/schema、7 项及 closeout count 对应、花括号可逆往返和不可逆失败；每例保存期望结果、实际 stdout/stderr 与 exit code。测试无网络且不访问用户数据。测试以临时合成 repo root 运行检查器副本，确认真实 `doc/tasks/` 未被读取或改写；实现不得为测试增加任意 repoRoot 输入开关。DSH 固定 delivery head、Handoff 和证据；Antigravity 对精确 head 作独立 Review。Review 通过、AC 证据完整后由 Codex 集成并运行集成后治理检查；所有失败和未运行项如实记录，不能把 `BLOCKED`/`NOT_RUN` 写为通过。

## 允许修改范围

- `tools/governance/check.ps1`
- `tools/governance/resource-manifest.schema.json`
- `tools/governance/tests/**`
- `doc/tasks/GOV-RESOURCE-MANIFEST-JSON-1.md`
- 本 Task 的 `verification/GOV-RESOURCE-MANIFEST-JSON-1/**`
- 本 Task 的 Handoff 与 Review；Plan/STATUS 仅由 Codex 维护生命周期指针。

`allowed_paths` 明确包含检查器、固定 schema、测试、Task 和 evidence_dir。P19 兼容视图不在本 Task 写入范围。

## 禁止范围与不做事项

- 不改 `doc/tasks/P19-UI-FIX-1.md` 正文；生成其兼容视图及重跑该 Task 检查另立后续 Task。
- 不改 `verification/P19-UI-FIX-1/resource-manifest.json`，不改 P19 其它历史 evidence。
- 不改其它 Task，不重钉任何 evidence/source pin，不删除、移动或归档任何资源。
- 不把缺失资源写成 `NOT_APPLICABLE`，不伪造替代路径，不猜测或展开环境变量、glob、宏或不可逆花括号表达式。
- 不修改产品代码、共享接口、应用 schema 或依赖；不联网、不访问用户数据；不在真实 `doc/tasks/` 放测试 Task。
- 超出以上范围时暂停该部分并交 Codex裁定，不自行扩大 Task。

## 测试与验证计划

| AC | 计划步骤 | 环境 | 结果 | 证据 |
|---|---|---|---|---|
| AC1–AC4 | 临时合成 repo root 下执行成功及拒绝用例，保存每例输入/输出/exit code | 离线；临时目录；不读取真实 Task 树 | NOT_RUN | `verification/GOV-RESOURCE-MANIFEST-JSON-1/` |
| AC4 | 只读解析 P19 原 JSON，核对 7 个 resources、closeout_counts 与表达式保真 | 固定输入文件；不写 P19 文件 | NOT_RUN | 同上 |
| AC5 | 运行离线测试集；记录 shell、PowerShell 版本、命令、stdout/stderr、exit code | 离线；合成 repo root | NOT_RUN | 同上 |
| AC5 | 对固定 delivery head 执行 Antigravity 独立 Review；Codex 集成后运行全局及本 Task 检查 | 独立 Review；集成基线 | NOT_RUN | Handoff / Review / 同上 |

## 依赖、风险与阻塞

- 硬依赖 `GOV-PLAN-BUDGET-1`：已 `done`，集成提交 `c131b1ae114d00c17e734a51f38263d92fe6f198`。
- 固定 schema、解析规则或现有 P19 JSON 之间出现事实冲突时，保留原数据并报告阻塞；不得静默放宽 schema 或修补 JSON。
- `P19-UI-FIX-1` 兼容视图及该 Task 检查重跑属于后续独立 Task。

## 交付与运行记录

- Owner：DSH；Reviewer：Antigravity；Codex 负责范围裁定、集成与 closeout。
- Handoff：`doc/handoffs/GOV-RESOURCE-MANIFEST-JSON-1-<short-head>.md`。
- Review：`doc/reviews/GOV-RESOURCE-MANIFEST-JSON-1-<short-head>-antigravity-r1.md`。
- 报告绑定完整 `base_commit`、`delivery_head`、`reviewed_head`、命令、环境及退出码；`NOT_RUN`/`BLOCKED` 不得描述为 PASS。

## Canonical Evidence

进入 `in_review` 前，为每个已释放 AC/Gate 登记唯一当前证据、路径、含文件的 commit、SHA-256 和分类。

| evidence_id | AC/Gate | path | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| 待交付 | AC1–AC5 | `verification/GOV-RESOURCE-MANIFEST-JSON-1/` | 待填 | 待填 | 待定 |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task worktree | 释放后按实际路径记录 | `PRESERVE_UNKNOWN` | 原路径 | 待记录 | 待检查 |
| fixtures / agent-output / exchange | 据实逐项记录；仅经核实从未适用才可填 `NOT_APPLICABLE` | 据实填写 | 据实填写 | 待记录 | 待检查 |

## Closeout Record

- Closeout date / Codex：待关闭时填写。
- `canonical_evidence_status`: `pending`。
- `resource_closeout_status`: `pending`。
- 删除、迁移、归档数量/字节数：未另获授权前为 0。
- 未关闭项及保留原因：逐项记录；无则填写“无”。
- 当前指针清理：由 Codex 在终态时更新 Plan / STATUS / Task 导航并运行 Task 检查。
