# GOV-P15-MANIFEST-1 Closeout 裁定 r23

- 日期：2026-10-20
- 裁定者：Codex（Lead / Architect / Integrator）
- checkout：`G:\CODEX\New Manga`
- branch / HEAD：`antigravity/P09-AC3-DELETE-HARDEN-1` / `e66927a312c184292774e64e70cd54d6ae7dc75e`
- 本报告是本次唯一写入；不回填 Task、Plan、STATUS 或既有 evidence。
- 裁定基于 Task、恢复材料、Handoff、三轮 Review、r20–r22、Plan、STATUS、协作协议与 checker 当前实现。凡与现场文件不一致的题面摘要，以下列明并以现场为准。

## 结论摘要

1. **目标终态是 `done`，不是 `closed_with_limitations`。** 4/4 AC 已达成，r3 Review `APPROVED`。manifest 是明确标注来历的重建件，原件从未入库且无从比对，这个已披露的事实不构成未完成 AC 或 limitation。P15 剩余的 `SettingsPage.test.tsx` 历史 pin 错误属于 `GOV-PIN-LINEAGE-1`，不是本 Task 的限制。
2. **但当前尚未满足正式 `done` 条件。** Task 文件仍为 `in_review`，`integration_commit`、canonical evidence closeout、resource closeout 仍为 pending；协作协议要求 Codex 集成、集成后验证和 closeout 后才能设 `done`。先进入/记录 `approved` 集成窗口，完成真实集成验证后再设终态。若查明没有可诚实记录的集成事实，不能伪造 hash 来过 checker；保持 `approved`，另行裁定协议与 checker 的冲突。
3. 本仓库 Task 文件的实际 Owner 是 `codex`，题面说 `dsh`；Handoff 作者是 dsh。正式 closeout 前应依据实际认领/交付记录核准 Owner，不可只抄题面或延续错误 frontmatter。计划中的 `GOV-PIN-LINEAGE-1` Owner 建议依 r21/r22 轮换为 **Antigravity**、Reviewer 为 **DSH**（释放时确认可用性）；不是继续默认由 dsh 实现。
4. 实际 Plan 行当前是 `proposed`，不是题面说的 `in_progress`。Plan 当前 3999 bytes / 46 lines，done 计数 40；仅在 Task 正式 `done` 后把该计数加到 41。STATUS 的 Active Task 仍为 P20，无需改运行指针。

## 1. 终态：`done`，不是 `closed_with_limitations`

AC1–AC4 均为 `[x] + <<MET>>`。r3 Review 对 `2f9d549d5` 给出 `APPROVED`，并核实资源登记和 pin 闭环。恢复属性已在 `restored_by` / `restoration_basis` 明示：这是按原 Task 记录与现场核验恢复的 manifest，不声称是未入库原件，也不声称能与原件逐字比对。可审计的恢复件可以完整满足“恢复缺失清单”这一目标；是否原样复原不是 AC，且原件不可得不代表恢复依据不可核。

P15 的一条历史 pin 报错发生于另一个 Task 的文件后续演进。它在本 Task 开始前已存在，且本 Task 只要求恢复 manifest；r3 确认 manifest 缺失错误已消除。按 r20/r21/r22 的范围原则，不能把对象 Task 的既有治理债转成此 Task 的 limitation。故目标终态为 `done`。以上是终态 adjudication，**不是**声称当前 lifecycle 字段已经关闭。

## 2. “文本沉默”与物理事实

### 2.1 独立裁定

Review 的纠正成立。第一版的推理把“来源可追溯”误读成“只能记录旧文本逐字声称的项目”。对历史声称必须保留来源边界，但这不允许把当前实测事实藏起来。资源确实存在且被实测为指向主仓库的 Junction；记录它们是当前物理盘点，不是声称 P15 原文曾列出它们。区分二者的正当办法是标明实测依据和检查时间，而不是仅从原文没写推出资源不存在。

更一般地，**“文本没写”只证明该文本没有陈述，不证明事实不存在。** 治理记录应把三类信息分开：原始记录明确声称什么、现在实测观察到什么、仍未知/无法回溯什么；结论分别 pin 到来源或现场检查，推论不得伪装成历史记录。缺项应触发查证，而不是自动补值或自动判不存在。

本例与 AC 漏勾、pin 后续失配、文件只在两个权威之一存在，属于同一上位问题：**记录与被记录对象/当前事实可能漂移**；但它们不是同一种具体故障，修复方法不同：

| 现象 | 事实类型 | 正确处理 |
|---|---|---|
| Junction 未写入旧 Task | 当前物理资源未被旧文本枚举 | 实测、注明来源与时间，补入当前清单 |
| AC 已完成但漏勾 | 状态表述不完整 | 用证据核实并修正 checkbox/状态门禁 |
| pin 指向旧字节 | 历史快照与当前文件时间不同 | 保留历史 pin，追加 lineage；需要当前证据时新增 pin |
| 文件只存在于两个权威之一 | 权威副本/引用链不一致 | 对照两边及 commit，判断缺失、未同步或错误引用 |

所以可共享“主动核对记录与对象”的原则，不能用“文本不完整就按实测覆盖历史”作为通用修复。历史 pin 尤其不能因当前文件不同而重算覆盖。

### 2.2 Manifest 中记录自身错误是否成规范

不应把“在生产清单里完整复述作者犯错过程”定成规范。当前 notes 约 20 行，解释了重要的判断变化，但 manifest 的核心职责是资源及出处；这段反思已在 Review r1/r2/r3、writeup 和本 closeout 中有更合适的审计载体。规范应要求清单记录**足够的 provenance 与可复核事实**，例如 `restored_by`、`restoration_basis`、现场检查结果；若错误改变 disposition 或留下风险，保留一条简短理由并链接审查记录即可。这样既不抹去纠错轨迹，也避免每个产物变成过程日记。当前 notes 无须为本 Task 关闭而删改，后续类似工件不必照搬约 20 行写法。

## 3. Head 字段与 `integration_commit`

| 字段 | 裁定 | 语义 |
|---|---|---|
| `reviewed_head` | `2f9d549d5578a50893eabb4572394b4e212f0d87` | r3 Review frontmatter 固定审查对象。批准只绑定此 head。 |
| `delivery_head` | `2f9d549d5578a50893eabb4572394b4e212f0d87` | 最后一次实质交付、也是 Review 对象。`68e696306` 落盘 r3 Review / AC4 记录，`e66927a31` 又为 r3 Review pin 记入引入 commit；两者都是审查后记账，不应回写成被审交付 head。 |
| `integration_source_head` | `2f9d549d5578a50893eabb4572394b4e212f0d87` | Codex 接收的已批准交付源 head。不能用 Review 元数据提交替代交付源。 |
| `integration_commit` | 当前 `null`；完成真实集成及集成后验证后填实际 commit，否则继续为 `null` | 只表示 Codex 集成完成点，不是“最新提交”、Review 落盘提交或方便 checker 通过的占位字段。 |

r3 所谓“不要让 `delivery_head` 追 HEAD”与 Task 当前 `delivery_head: 68e696306` 确有不一致；应以固定 Review 对象 `2f9d549d5` 为准。更新 Task metadata 不会重审交付内容；若改变实质内容则必须形成新 delivery head 并重新 Review。

统一沿用 r21/r22 修正后的口径：真实发生的 Codex 集成及验证 head 才是 `integration_commit`。若已确认 approved source head 在受控集成目标内，Codex 应核实来源包含关系并完成协作协议 §4 的集成后验证；若为原地集成而无 merge/cherry-pick，记录验证完成的真实 HEAD，并说明该路径。普通 Review/closeout 提交本身不自动构成集成。若没有集成且没有验证，不得冒称 `done`。**无需在 checker 为“无集成的 done”开合法表达**：协议定义 `done` 必须先集成，null 应留在 `approved` 集成窗口；只有流程确实允许无集成而 done 时，才需另行修改协议与 checker，目前没有该需求。

## 4. 两张表

### 4.1 Canonical Evidence

现场 Task 有 4 行（不是 5 行）：`P15M-RESTORED`、`P15M-WRITEUP`、`P15M-HANDOFF`、`P15M-REVIEW-R3`。按产物种类及 AC 覆盖，当前集合足以支撑 AC1–AC4：writeup 支撑来源核实/现场检查，manifest 是 AC3 结果，Handoff 记录交付，r3 是当前最终独立结论。

r1/r2 是已经被 r2/r3 后续结论取代的历史 Review。它们的报告和发现应保留，且 r3 已审查相关闭环；不必把每轮 Review 都列成 Canonical Evidence 当前 pin。若 Task 的审计导航希望显式列出完整审查链，可在 closeout note 列出 r1/r2 路径；不要把旧的 `CHANGES_REQUESTED` 误当当前批准证据。正式关闭前仍须验证现有四行 commit 与 SHA pin，并纠正任何错误的 evidence row；本裁定不声称当前检查已在本轮重跑。

### 4.2 Resource Manifest

Task 现有 8 行由 7 个 `NOT_APPLICABLE` 类别和 `evidence_dir` 构成；作为本 Task 的派生资源核销，在本任务只恢复一个版本化 JSON 清单、无单独 task worktree/临时资源的范围内是恰当的。新建的 `verification/P15/resource-manifest.json` 是本 Task 的**交付证据**，已由 `P15M-RESTORED` 登记；它不是本 Task 的新 worktree、临时资源或额外 evidence_dir 内容，因此不应再把它重复登记成 Resource Manifest 资源。它属于 P15 manifest 自己描述的目标清单，而不是其中新增的一项 P15 资源。

## 5. Plan / STATUS

现场 `doc/REBASELINE_PLAN.md` 当前节点为 `proposed`，需记录这个与题面 `in_progress` 的差异。r3 已批准，但 Task frontmatter 仍是 `in_review`，且尚无已证实 integration closeout。正式同步审查状态时，应至少将 Plan 从 `proposed` 改为以下完整行：

```markdown
|GOV-P15-MANIFEST-1|GOV-SOURCE-RECORDS-1|approved（AC 4/4 MET；Antigravity Review r3 APPROVED；等待 Codex 集成、集成后验证及 evidence/resource closeout）|
```

完成真实集成验证和 closeout 后，再替换为终态行：

```markdown
|GOV-P15-MANIFEST-1|GOV-SOURCE-RECORDS-1|done（AC 4/4 MET；重建 P15 Resource Manifest，worktree + 3 个实测 junction；Antigravity Review r3 APPROVED；SettingsPage.test.tsx 历史 pin 由 GOV-PIN-LINEAGE-1 承接）|
```

须等 Task 正式 `done` 才采用上面终态行并将 done 计数从 40 增为 41。Plan 当前 3999 bytes / 46 lines，替换同一行不增加行数，仍在 7000 bytes / 64 lines 上限内。当前可将 Plan 行同步为 `approved / integration pending`，但不能提前标 done。STATUS 当前 Active Task 是 P20，无本 Task 的 Active/rolling-checkpoint 指针；不改 STATUS。若正式 closeout 选择更新 STATUS 的治理摘要，只能增补准确状态，不得改 Active Task 或把 P15 的残留 pin 错报成已清除。

## 6. `GOV-PIN-LINEAGE-1` 与 pin 一致性门禁

这六次都是“改动对象 A 后，未同步检查所有引用 A 的 pin/metadata B”的变更闭环失效；可作为一个共同的变更后核对习惯。但具体分别涉及 Task checkbox、Review/Handoff commit、证据 SHA 和 delivery head，不是同一字段错误，也不应把所有解决方案塞进一条 checker 规则。

本次提出的两个条件已经被当前 `tools/governance/check.ps1` 实现：对当前 Task 的每个 Canonical Evidence 行，它验证所引 commit 中存在该路径，并对当前磁盘文件重算 SHA-256 与行内值比较。因此，**无须再加一个重复的 pin 一致性 checker 门禁**；实际风险是没有在交付/closeout 后运行现有 Task 检查，或没有把失败作为阻断处理。后续 Task 应把按要求运行 task-scoped checker 并保存结果作为 Review 前的交付步骤。checker 检查的是“commit 有该文件”与“当前文件 hash 等于 pin”，不证明自然语言证据足以支撑 AC，也不替代独立 Review。

`GOV-PIN-LINEAGE-1` 的主体仍应是 r20 已裁定的历史 pin lineage：保留原 evidence_id、commit、SHA，查清后续文件演进并追加 lineage；只有当前 Gate 需要时新增当前证据 pin。不要仅因 P15 的六次闭环失误就扩张该 Task 去重复实现已有校验器。若释放前发现 lineage 任务必须改变 checker 对历史失配的处理，则先在 Task 中冻结精确方案和回归范围；本次证据不支持另建同名重复门禁。

Owner/Reviewer：建议 Antigravity Owner、DSH 独立 Reviewer，遵循 r21/r22 轮换建议与角色分工；释放时确认可用性、固定真实 base/branch/worktree/allowed paths。若 Antigravity 不可用，依项目当前故障转移顺序评估 ZCode。此建议不是任务释放授权；当前 Plan 仍为 proposed，不能因本 closeout 报告自动开工。

## 7. 本次状态边界与下一步

本裁定没有修改 `doc/**`、`tools/**`、`src/**`、`tests/**`、`.gitattributes`、`doc/tasks/P15.md`、`verification/P15/resource-manifest.json`、`verification/GOV-P15-MANIFEST-1/` 或任何既有文件。Task 仍须由 Codex完成 metadata / evidence / resource closeout、真实 integration 后验证及权威检查；届时先核实 Owner 元数据、delivery head 和各 evidence pin，再决定何时改 `done`。若无法证明 integration，保持 `approved` 并单独处理 checker/协议契约，不得假造 `integration_commit`。

建议下一项治理工作仍为 `GOV-PIN-LINEAGE-1`，但**不自动释放**。释放前应先完成本 Task 正式 closeout并冻结 Task 的范围、当前 base/head、历史 pin 清单及 checker 方案；推荐 Owner=Antigravity、Reviewer=DSH。可转发指令：

> 请在 Codex 正式释放 `GOV-PIN-LINEAGE-1` 后，以 Task 中冻结的 base/head、worktree 与 allowed paths 执行历史 pin lineage 核验。逐条保留原 evidence_id、commit、SHA-256，不重算覆盖；核实后续改动提交和现有文件状态，追加可追溯 lineage，当前 Gate 确需当前内容时另增新 pin。先核实当前 checker 对历史失配的行为并在 Task 中冻结是否涉及 checker 修改；不得扩大范围或放宽既有 AC gate。提交 Task 约定的文件、证据及 Handoff，运行并记录 Task-scoped 与规定的全局治理检查，随后交由非实现者独立 Review。未有实际 Task/工作路径/固定 commit 前不要开始实现。

## 动手前工作区状态

执行写入前，`git status --porcelain` 共 1237 行，按 UTF-8 编码、LF 连接的状态文本 SHA-256 为 `5d38f7479a2e55b24ddebb282bce3a47a144d3607679f5d22ee1f47bebd92bfc`。目标 r23 文件当时不存在。该状态基线包含大量此前已有的 dirty/untracked 项，均不属于本次操作。
