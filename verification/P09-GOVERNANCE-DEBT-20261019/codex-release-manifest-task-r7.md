# GOV-RESOURCE-MANIFEST-JSON-1 释放裁定与落盘指令（r7）

日期：2026-10-19  
裁定人：Codex / Lead / Architect / Integrator

## 2.1 释放决定

**可以从 `proposed` 转为 `ready`。** `GOV-PLAN-BUDGET-1` 已集成并 closeout 为 `done`，前置依赖满足。Task A 与本 Task 共写 `tools/governance/check.ps1` 的冲突由严格串行顺序消除。

`base_commit` 固定为完整提交 `c131b1ae114d00c17e734a51f38263d92fe6f198`。这是 `GOV-PLAN-BUDGET-1` 的 integration commit，已包含预算为 `Bytes = 7000; Lines = 64` 的 checker。当前 HEAD `688d866d9` 是其后提交，虽也含 checker，但同时改变 Plan/Task；以 `c131b1ae1` 为基线可直接锚定依赖交付，避免把后续治理文档改动不必要地带入实现基线。基线应以完整 hash 而非短 hash 落盘。

Owner 为 DSH（`dsh`）；Reviewer 为 Antigravity。两者不同，Antigravity 按项目故障转移规则承担独立 Review；Codex 负责释放、主线集成及最终 Gate，不审查自己的实现。不得分配给已退出项目的 Qoder。

释放还需 Codex 将 Task、Plan DAG/READY 和 STATUS 指针按协作协议登记，并固定分支与 worktree。建议 Task `status: ready`，Plan 加一行 DAG 节点；Plan 当前 35 行，新增后 36 行，低于 64 行上限。STATUS 当前 Active Task 仍是 P20，不把本 Task 冒充唯一 Active Task；将其作为 READY/待派任务登记。实际落盘后运行全局及 `-TaskPath` 检查器核验权威指针。以下完整 Task 是建议直接落盘内容。

## 2.2 完整 Task 内容

````markdown
---
id: GOV-RESOURCE-MANIFEST-JSON-1
title: 治理检查器支持外部 JSON Resource Manifest
kind: governance
governance_version: 2
status: ready
approval: codex_release_2026-10-19_after_GOV-PLAN-BUDGET-1_integration; user_decision_2026-10-19_scheme_D
suggested_owner: dsh
owner: dsh
reviewer: Antigravity
depends_on:
  - GOV-PLAN-BUDGET-1
base_commit: c131b1ae114d00c17e734a51f38263d92fe6f198
branch: agent/deepseek/GOV-RESOURCE-MANIFEST-JSON-1
worktree: G:/CODEX/New Manga.workspace/worktrees/GOV-RESOURCE-MANIFEST-JSON-1
integration_commit: null
delivery_head: null
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
````

## 2.3 与 P19-UI-FIX-1 的衔接切分

**本 Task 不包含**“生成 P19-UI-FIX-1 兼容视图并重跑其 Task 检查”。它的写权限不含 `doc/tasks/P19-UI-FIX-1.md`，也不应借用宽泛路径授权。AC4/AC5 仅要求只读解析原 JSON、证明新检查器/schema 能保留并核对其 7 项与 closeout counts；原 JSON 保持原位原样。

在本 Task 完成并集成后，另立依赖 `GOV-RESOURCE-MANIFEST-JSON-1` 的窄范围后续 Task，专门写入 `doc/tasks/P19-UI-FIX-1.md` 的兼容视图，并用已集成检查器重跑 `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/P19-UI-FIX-1.md`。后续 Task 的 `allowed_paths` 才能明确包含 P19 Task 正文及其自身 evidence_dir；仍禁止改原 JSON 和历史记录。这样保留 r3 的“随后生成并重跑”要求，同时不扩大本 Task。

## 2.4 离线用例形式

- 固定用例和测试驱动放在 `tools/governance/tests/fixtures/resource-manifest/`；逐次运行的完整结果放在 `verification/GOV-RESOURCE-MANIFEST-JSON-1/`。fixtures 是版本化测试输入，不是真实 `doc/tasks/` 内容。
- 检查器从 `$PSScriptRoot` 推导 repo root，且全局检查硬编码读取 `doc/tasks/`。测试驱动应在系统临时目录构造合成 repo root，放入检查器所需的最小文档树及合成 Task/Manifest，再把当前被测 `check.ps1` 复制到合成 root 的 `tools/governance/` 下执行。临时目录使用独立名称并在用例结束后安全清理；测试保存输入副本、输出和 exit code 到 Task evidence。绝不能把 fixture Task 放入主仓真实 `doc/tasks/`。
- **无需**增加“指定 repoRoot 之外 fixture 根”的生产参数，也无需创建临时 Git worktree。复制检查器可让现有 `$PSScriptRoot` 规则自然指向合成 root，避免改变 checker 的生产入口或使用真实 Task 树；测试只读/写其自身临时目录。若当前实现有无法隔离的行为，先报告并由 Codex裁定，不得默默读取真实 Task。

## Plan 登记

在当前 35 行 Plan 增加且只增加以下一行 DAG 节点（当前预算允许至 64 行）：

```markdown
|GOV-RESOURCE-MANIFEST-JSON-1|GOV-PLAN-BUDGET-1|ready（外部 JSON Resource Manifest 检查器；后续兼容视图 Task 单独释放）|
```

把原 READY 声明精确替换为以下写法，保留其余 READY 项：

```markdown
READY 节点：ARCH-DOC-REBASELINE、P20、GOV-RESOURCE-MANIFEST-JSON-1。in_review：HARDEN-2。done：**34 项**。
```

STATUS 由 Codex 登记 READY/待派指针，保持 P20 为唯一当前 Active Task。此 Task 不因写入 Plan 即视为 DSH 已认领；只有 DSH 确认并按协议切换为 `in_progress` 后才开始实现。

## DSH 落盘与执行顺序

1. **Codex 释放准备：**核对 `GOV-PLAN-BUDGET-1` 已 done；将以上 Task 全文写入 `doc/tasks/GOV-RESOURCE-MANIFEST-JSON-1.md`，填入指定完整 base/owner/reviewer/branch/worktree；在 Plan 增加唯一 DAG 行并更新 READY 声明；在 STATUS 登记 READY/待派任务但保留 P20 Active。此处不改 P19 Task 或 JSON。
2. **Codex Gate：**运行 `pwsh -NoProfile -File tools/governance/check.ps1` 及 `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/GOV-RESOURCE-MANIFEST-JSON-1.md`，确认权威指针和预算检查结果；修复登记错误后才把释放交给 DSH。Task 文件变为 `ready` 不等同于写入前置步骤已完成。
3. **DSH 认领：**确认共享仓库/linked worktree、分支、完整 base commit 和工作区状态；不覆盖任何既有 dirty/untracked 内容。认领后将 Task 置 `in_progress`，在获准路径内实现 checker、schema、离线测试与证据。
4. **DSH 验证与交付：**按 AC1–AC5 顺序执行离线用例；对 P19 JSON 只读核对 7 项/counts；保存逐例结果、Handoff，并固定 `delivery_head`。不得编辑 P19 Task/JSON、Plan/STATUS（Codex 生命周期指针除外）、其它 Task 或 pins，不删除/迁移资源。
5. **Antigravity Review：**审查固定 delivery head 与证据，Reviewer 不得为作者；发现问题回到 `in_progress` 修订并以新 head 重审。
6. **Codex 集成与 closeout：**批准 Review 后串行集成，运行全局与 TaskPath 检查，逐项核对 Resource Manifest 和 evidence pins。所有 AC、集成验证及 closeout 均完成后才置 `done`。
7. **后续兼容视图：**本 Task done 后，再由 Codex另立 P19 兼容视图/Task 检查 Task；不在本 Task 中扩展 `allowed_paths`。

## 本次产物写入前后 Git 状态

- 写入前 `git status --porcelain`：1234 条；按 UTF-8 行文本计算 SHA-256：`dfbb95ad3066a43d637194f47758a0299ef09777aa6ccd10c74581ec174b824e`。
- 写入后：待本次单文件写入后立即重采样并记录。由于原工作区已有大量 dirty/untracked 内容，比较应确认原有条目保持不变，只有本文件的新增/修改状态可归因于本次操作；不清理或重写其它条目。
- 本轮不运行 AC 探针，不调用 `coordinator-lease.py`，不执行任何 Git 写命令。
