# GOV-DEBT-CLEANUP-2 集成核对与三项裁定

日期：2026-10-19  
裁定人：Codex / Lead / Architect / Integrator  
固定交付：base `75da8281b28c7c11f92518c63d4669b5cf3973e6` → delivery `e63d9324766db0d381bad24b3fc60a58048430e1`。本文件只记录核对与裁定，不执行集成、资源处置或 Task 状态写入。

## 1. 集成核对与状态判定

### Review 与 AC 核对

Review `doc/reviews/GOV-DEBT-CLEANUP-2-e63d9324766-antigravity-r1.md` 是有效独立 Review：Reviewer=Antigravity、Owner=DSH；reviewed_head 与 Task/Handoff 固定 delivery_head 完全一致，base 也一致。Review 记录实际运行逐行比对、自写脚本、git diff 与检查器源码核对；四项检查通过，P0=0。

| AC | 核对结果 |
|---|---|
| AC1 | 102 行逐行表；Review 报告与来源零差异。 |
| AC2 | 29 项逐项 DEFERRED；10 个未入库文件原状保留。 |
| AC3 | 记录 7000/64 批准值和现行 2500/35；未改预算/检查器。 |
| AC4 | 23 条 P02 pin：18 存在、5 缺失；未宣称主线集成。 |
| AC5 | 13 个 worktree 全部保留；dirty、不可达 HEAD 明列。 |
| AC6 | 6 个 Task 补表；P19-UI-FIX-1 原始 JSON/散文保留，未完成。 |
| AC7 | 61 项只有候选分类；没有唯一证据判定或 Canonical Evidence 登记，未完成。 |
| AC8 | 373 个未完成 AC / 69 个 Task 记录 KEEP_OPEN。 |
| AC9 | 全局和 Task 检查均 PASS (2 warnings)、exit 0；未运行 AC 探针/产品测试。 |

Handoff、固定 head、逐项证据和独立 Review 齐全。AC1–AC5、AC8、AC9 有相应记录；AC6 部分完成，AC7 未完成。Task 的 Canonical Evidence 仍是占位表，Resource Manifest 仍有待核实占位项，integration_commit=null。

### 终态与字段

**当前不进入终态；建议由 in_progress 更新为 approved，留在 Review 阶段等待 Codex 集成及 closeout。** 不设 done：AC6/AC7 未闭环，Canonical Evidence 与资源 closeout 未完成。也不设 closed_with_limitations：协作协议 §4 仅允许用户明确裁决或已批准目标架构取代旧 Task 时使用；用户批准预算、暂缓债务不等于批准关闭本 Task。

- canonical_evidence_status：`pending`，因 AC7 未裁定且表仍为占位。
- resource_closeout_status：`pending`，本 Task 的资源和引用/进程检查仍有占位。
- integration_commit：保持 `null`，本轮没有集成。
- 不勾选 AC6/AC7，不把限制性结论写成 PASS。

Plan 已有节点，改状态时只原行替换，不新增行，不超 35 行：

```markdown
|GOV-DEBT-CLEANUP-2|—|approved（AC6 的 P19-UI-FIX-1 格式债务；AC7 的 61 项归属未结）|
```

替换当前 `|GOV-DEBT-CLEANUP-2|—|in_progress|`。不登记 29 个暂缓 Task。STATUS 当前 Active Task 是 P20；本 Task 未终态，本轮不改 STATUS。

Task frontmatter 精确替换：

```yaml
status: in_progress
```

替换为：

```yaml
status: approved
```

其余 `integration_commit: null`、delivery_head 及两个 pending 字段保持原值。Closeout Record 写“尚未 closeout；adjudication 见 codex-integration-closeout-r3.md”，不填关闭日期。以上仅为交 DSH 后续落盘的指令，本轮未修改 doc 文件。

## 2. P19-UI-FIX-1 Manifest 格式债务（P1）

**裁定 D：另立检查器能力 Task，支持正文引用外部 JSON Manifest，并定义可验证的资源缺失语义；当前不转写原表，也不把已不存在标成 NOT_APPLICABLE。** 原 JSON 是既有 7 项资源及 closeout 计数的记录；直接只列现存资源会丢失历史资源状态，NOT_APPLICABLE 又会混淆“曾有但已不存在”和“从未适用”。

可执行判据：

1. 外部 JSON 路径须唯一且位于仓库证据范围内；不擅自展开环境变量或 glob 简写。
2. 资源保留原 source、destination 表达式及 JSON 原值。可精确解析的路径逐项检查。
3. 检查器契约允许明确的 `ALREADY_ABSENT`（或语义等价状态），但仅在证据证明资源曾列入 Manifest、目标现在不存在、且无引用/进程时接受。它不得写成 `NOT_APPLICABLE`；不得伪造替代路径。
4. 花括号表达式只有可逆拆分并能与原 JSON 的 7 项及 closeout 计数逐一对应时才转换；不能对应则保留并标阻塞。
5. 另立 Task 修改检查器、固定 schema、增加有/无目标和错误引用的离线用例，由非作者 Review；随后再生成 P19-UI-FIX-1 的兼容视图并重跑其 Task 检查。原 JSON 与历史记录保留。

这不是授权改 check.ps1 的当前 Task；也不要求用户裁决 NOT_APPLICABLE 的合法性：本裁定明确不允许以该值代表已消失资源。

## 3. 61 个 evidence_dir 文件最终归属（P1）

**裁定：逐 Task、逐文件复核，统一按下述判据处理；不采用“过程产物一律迁出、目录只留 AC 直接证据”的批量移动规则。61 项目前原位保留，不删除、移动或归档。**

每项记录 Task/路径/hash、候选类、对应 AC 原文、内容中的命令/环境/结果/退出码（适用时）、既有引用与 Canonical Evidence：

- 只有直接证明已释放 AC、绑定固定 commit/hash 且确属唯一或当前最终结果，才列 `CANONICAL`。
- 不可变且为 AC 必要输入/来源的，才列 `SOURCE_PIN`，记录来源与 hash。
- 重复尝试、checkpoint、临时输出可不列 Canonical Evidence；“过程产物”不等于可删除。移动/归档前须证明已有等内容副本、核对所有引用、hash/数量并取得独立处置授权。
- `.gitattributes` / `.gitignore` 不登记为证据；只读确认用途，未获独立授权前原位保留、不改。
- 唯一性、AC 绑定或来源不明时标 `UNRESOLVED` / `PRESERVE_UNKNOWN`，不得降级、搬迁、删除。须先验证替代证据内容、hash 与引用，才能认定原件非唯一。

该规则把归属判定与物理处置分开，避免候选分类被误当成删除依据。

## 4. 预算维护 Task：完整 ready 内容

用户已批准 Plan 检查器预算从 2500 bytes / 35 lines 提至 7000 / 64。以下建议由 DSH 实施、Antigravity Review、Codex 集成。它只改两个数值，不授权登记 29 个暂缓 Task。

```markdown
---
id: GOV-PLAN-BUDGET-1
title: Plan 预算上限扩容
kind: governance
governance_version: 2
status: ready
approval: user_decision_1_2026-10-19; codex_scope_release_integration-closeout-r3
suggested_owner: dsh
owner: dsh
reviewer: Antigravity
depends_on: []
base_commit: 释放时填写当前集成基线
branch: agent/deepseek/GOV-PLAN-BUDGET-1
worktree: G:/CODEX/New Manga.workspace/worktrees/GOV-PLAN-BUDGET-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/GOV-PLAN-BUDGET-1
allowed_paths:
  - tools/governance/
  - doc/tasks/GOV-PLAN-BUDGET-1.md
  - doc/REBASELINE_PLAN.md
  - doc/STATUS.md
  - doc/handoffs/
  - doc/reviews/
  - verification/GOV-PLAN-BUDGET-1/
---

# GOV-PLAN-BUDGET-1：Plan 预算上限扩容

## 来源与目标

依据 `verification/P09-GOVERNANCE-DEBT-20261019/user-decisions-20261019.md` 裁决 1，将 `tools/governance/check.ps1` 中仅针对 `doc/REBASELINE_PLAN.md` 的上限由 2500 bytes / 35 lines 调为 7000 bytes / 64 lines。预算扩容不代表登记或释放任何 Task。

## Acceptance Criteria

- [ ] **AC1 — 精确修改。** 仅改该 Plan 对应的 Bytes=7000、Lines=64。其它检查规则、预算、错误条件和提示逻辑不变。
- [ ] **AC2 — 范围。** 变更限本 Task、实现预算的必要 `tools/governance/` 文件、生命周期登记所需 Plan/STATUS、Handoff/Review 与本 evidence_dir。不得登记/修改 29 个暂缓 Task，不改变 DAG 节点集合。
- [ ] **AC3 — 边界验证。** 离线验证 7000 bytes / 64 lines 内通过，任一边界超出时按既有失败/警告规则处理；保存输入、命令、环境、stdout/stderr、退出码。
- [ ] **AC4 — 治理检查。** 执行 `pwsh -NoProfile -File tools/governance/check.ps1` 及 `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/GOV-PLAN-BUDGET-1.md`，保存完整结果，不以预算通过推断其它债务消除。
- [ ] **AC5 — Review 与 closeout。** 固定 base/delivery head 和 Handoff，由 Antigravity 独立 Review；Codex核对差异、集成后验证及资源 Manifest。全部 AC 有证据且两种 closeout 完成后才可设 `done`。

## 允许修改范围

仅 frontmatter `allowed_paths`。Plan/STATUS 生命周期指针仅由 Codex维护；Owner 不得改动暂缓 Task。

## 禁止范围与不做事项

- 不改两个常量以外的检查器逻辑、错误条件、默认值或其它文件预算。
- 不登记/修改 29 个暂缓 Task，不改产品代码、测试、Schema、依赖或共享接口。
- 不运行 AC 探针/产品测试，不清理或移动仓外资源；未获 Codex closeout 裁定前保留 worktree 与 agent 输出。

## 测试与验证计划

| AC | 步骤 | 结果 | 证据 |
|---|---|---|---|
| AC1 | 静态 diff 核对两个常量 | NOT_RUN | `verification/GOV-PLAN-BUDGET-1/` |
| AC3 | 离线边界验证：阈值内、bytes 超界、lines 超界 | NOT_RUN | 同上 |
| AC4 | 两条治理检查命令并保存完整输出 | NOT_RUN | 同上 |
| AC5 | 固定 head 的 Review 与 Codex closeout | NOT_RUN | Handoff / Review |

## 依赖、风险与阻塞

- 授权依据：用户裁决文件裁决 1。
- 扩容只增加容量，不决定 Task 去留、状态、Owner 或 DAG 节点。
- 如需触及其它检查器逻辑，停止并请求范围裁决。

## 交付与运行记录

Owner DSH；Reviewer Antigravity；Codex集成。所有报告绑定精确 base/delivery/reviewed head。NOT_RUN/BLOCKED 不得写成通过。

## Canonical Evidence

进入 `in_review` 前逐项登记 AC1–AC5 的当前证据路径、commit/hash 和分类。

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| 待交付 | AC1–AC5 | `verification/GOV-PLAN-BUDGET-1/` | 待填 | 待填 | 待定 |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task worktree | 释放后据实记录 | `PRESERVE_UNKNOWN` | 原路径 | 待记录 | 待检查 |
| agent-output / exchange | 据实记录；无则核实后填 `NOT_APPLICABLE` | 据实记录 | 原路径 | 待记录 | 待检查 |

## Closeout Record

- Closeout date / Codex：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：未授权前为 0。
- 未关闭项及保留原因：逐项记录；无则填写“无”。
- 当前指针清理：Codex在终态时更新 Plan / STATUS / Task 导航并运行 Task 检查。
```

**释放门槛：** 以上为完整 ready 草案，不等同于已经登记或可自行开工。Codex正式释放前须按 §4 固定真实 `base_commit`、核对依赖/授权并登记 Plan/STATUS。Plan 目前 35/35 行，登记须改写现有行或待预算 Task 实施后完成；不得添加 Plan 行。29 个暂缓 Task 不因本 Task 解锁。

## 5. 仍需用户裁决

1. 是否明确批准本 Task 以 `closed_with_limitations` 终结。未批准前维持 Review 阶段 `approved`。若批准，限制必须逐条记录：①AC6 的 P19-UI-FIX-1 JSON 格式与检查器不兼容，格式债务未完成；②AC7 的 61 项唯一最终证据归属未核实、均未登记 Canonical Evidence；③相关证据/资源均未迁移或清理。不得把这些未完成项记 PASS。
2. 是否释放 Manifest 检查器兼容 Task、61 项逐 Task 复核 Task，仍按各自冻结范围走生命周期。本文件不等同于登记/释放。
3. 29 个暂缓 Task 维持原用户裁决，不因预算 Task 自动登记。

## 6. git status 对比

写入前 `git status --porcelain`：1236 条；UTF-8 行文本 SHA-256：`094d17cc07e95b13a1043330421a3f75c7c9ba478a4fbb651231bf1f7c46824a`。写入后状态待记录；采样结果只用于与该基线比较。本轮不执行任何 Git 写命令。
