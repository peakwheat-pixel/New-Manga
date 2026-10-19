# GOV-EVIDENCE-DIR-SWEEP-1 Closeout 裁定（r22）

**审查日期**：2026-10-20  
**当前 checkout**：`G:/CODEX/New Manga`，branch `antigravity/P09-AC3-DELETE-HARDEN-1`  
**当前 HEAD**：`b25af8142`  
**审查对象**：交付 `c5cec3f63`；Antigravity Review r1 `APPROVED`，`reviewed_head: c5cec3f63`  
**范围**：裁定终态、证据/资源 closeout、集成字段、Plan/STATUS 与后续 Task；本报告不声称已正式更新 Task、Plan 或 STATUS。

## 结论摘要

1. **目标终态裁定为 `done`，不是 `closed_with_limitations`。** AC1–AC3、AC5 为 `MET`，AC4 的移动条件集合为空，故以有理由的 `NOT_APPLICABLE` 表示本 Task 内不产生移动要求。生命周期 v3 明确允许勾选的 `[x] + <<NOT_APPLICABLE: 原因>>`；这与达成 AC 的 `MET` 语义不同，但并不禁止 Task `done`。正式状态仍须等集成验证及 Canonical Evidence、Resource Manifest closeout 完成后再写入。
2. 两个来源 Task 余下的四个检查错误均不构成 Sweep 的 limitation：这是预先存在且已分派到 `GOV-PIN-LINEAGE-1`、`GOV-P15-MANIFEST-1` 的独立问题；`EXPORT-REVEAL-1` 的 AC4 `BLOCKED` 则是真实保留状态。Sweep 已完成自己只读盘点和登记修复目标，不应替来源 Task 改写状态。来源 Task 的错误须在各自专项验收，不可在本 Task 报成 PASS。
3. **方法论结论：有系统性差距，但不应把“每个文件都写一句理由”本身变成新门禁。** checker 报路径集合，不理解文件语义；AC2 已要求内容判据且本次履行得有价值，但只靠作者文字还不足以抵抗套话。建议让引用链、内容摘录/可定位行、判别命题和处置反事实形成可审阅的小型证据记录，由 Reviewer 抽样或重点复核高判别力项；checker 继续只管结构和引用完整性。
4. Plan 中节点可在正式 closeout 后改为 `done`，计数增加 1；当前 Plan 为 **3977 bytes / 46 lines**，远低于 7000/64 限额。STATUS 的 Active Task 是 P20，本次不应切换该指针；如更新治理摘要，只需在现有治理证据摘要中列明 Sweep 已完成、两个后续专项仍未释放/待释放，不需改运行状态。
5. **本次还不能把 `integration_commit` 填成 `b25af8142`。** 它是 Review 获批记录提交；可证明 Review 和 Task 元数据落盘，不能单独证明 Codex 已完成协议 §4 的集成后验证。继续保持 `null`，直到 Codex 验证当前 checkout 是否为受控集成目标并完成集成后验证；若确属原地集成，记录验证后的真实 HEAD，并在 Closeout 解释无 merge/cherry-pick 的原因。r21 与 checker 的约束冲突按同一口径解决，见 §3。

## 1. 终态与 AC

AC4 原文限定“仅 ARCHIVE 项”。AC2/AC3 的逐文件内容判定与引用核查得出 5 个未登记文件全部 `REGISTER`，没有 `ARCHIVE` 项，因此执行移动的前提集合为空。对空集合不执行移动是**不适用**，不是未完成、失败或阻塞；`NOT_APPLICABLE` 的理由具体且可由 triage/inventory 复核。协议 §4.3 将 `[x] + NOT_APPLICABLE` 列为合法状态，没有规定只有全部 `MET` 才能 `done`。因此，一个 AC 为有充分理由的 `NOT_APPLICABLE`，本身允许 Task 进入 `done`。

Review 已批准固定交付 head，AC 均有记录。AC4 不产生限制，另外四个来源 Task 检查错误也不属于本 Task 的目标或未完成 AC。所以目标终态是 `done`。不过这只是**终态 adjudication**：按 §4.1–4.2，必须先完成集成后验证、证据与资源收口、检查器 Gate；完成前 Task 仍停留在 `approved` / 集成窗口，不得提前改成 `done`。当前 Task 文件仍显示 `in_review`，需由 Codex 在正式 closeout 中依序完成生命周期字段回填。

来源 Task 的剩余错误分类如下：

| Task | 剩余问题 | 归属与对 Sweep 的影响 |
|---|---|---|
| `EXPORT-REVEAL-1` | M2-C1 contract pin SHA 失配 | 时间性 lineage，归 `GOV-PIN-LINEAGE-1`；非 Sweep limitation |
| `EXPORT-REVEAL-1` | AC4-③ `BLOCKED` 被检查器报未完成 AC | 如实保留的产品验证限制；非 Sweep 造成，也不由 Sweep 清除 |
| `P15` | `SettingsPage.test.tsx` pin SHA 失配 | 后续变更 lineage，归 `GOV-PIN-LINEAGE-1`；非 Sweep limitation |
| `P15` | `verification/P15/resource-manifest.json` 缺失 | 归 `GOV-P15-MANIFEST-1`；非 Sweep limitation |

## 2. 方法论裁定：路径报错与内容判定

是，二者之间存在结构性差距：`evidence_dir 含未登记文件` 只回答“哪些路径没有表项”，不回答文件是否支持 AC、是否证明失败、是否被 closeout 字面引用，也不回答删除/归档会造成什么事实损失。只机械照单登记虽然可能消除 checker 错误，却无法解释登记是否正确；本次读内容后发现两份 `EXIT_CODE=101` 的失败记录，其中 P15 日志又被 Closeout 明确点名为“证据诚实性（正向记录）”，正好说明内容审查能识别 checker 不表达的证据价值。

AC2 已要求以实际内容为判据，故本 Task 的要求足以约束这次交付；它不是自动执行或内容理解机制，不能据此推论以后每次都会正确执行。缩小差距的低成本做法是保持逐文件 adjudication，但让每个**未登记/拟处置项**至少有以下可复核链条：

1. 路径与 hash、实际内容中的短摘录或稳定行/字段定位（失败日志记录退出码及关键错误；成功日志记录结果计数及退出码）；
2. 该内容支持/反驳的具体 AC、Review 或 Closeout 命题及其引用位置；
3. `REGISTER` / `ARCHIVE` / `PRESERVE_UNKNOWN` / `DUPLICATE` 判定，以及若移动或不登记会丢失/重复/破坏什么信息；
4. 对 `ARCHIVE` 另附全仓引用核查和可恢复性依据；对 `REGISTER` 标明落入的 evidence id 与 `CANONICAL`/`SOURCE_PIN` 适用理由。

不要要求所有已登记文件重复写一段空泛“有判别力”理由，也不需要让 checker 判断自然语言是否有意义。避免形式主义的关键是让理由**可证伪且可反查**：内容定位必须能打开原件核验；命题须指向具体 AC/Review/Closeout 行；失败记录的存在要能解释为什么它不是成功日志的重复；Reviewer 对所有拟归档项及高风险失败/反例项重点核对，并抽查普通 REGISTER 项。套话没有内容定位、主张映射或可检验后果时即视为没有给出依据。checker 可以在未来验证每个 disposition 是否有引用字段、evidence id 是否存在、ARCHIVE 是否填引用检查，但语义判断仍由独立 Reviewer/Codex 承担。

## 3. Head、集成字段与 checker 矛盾的统一口径

| 字段 | 本 Task 裁定 | 依据 |
|---|---|---|
| `delivery_head` | `c5cec3f637a36b9caec0f90c5ae9b5474cbe2ba0` | Handoff 的交付 head；包含 AC1–AC4 交付、证据登记及交付记录，是 Review 所审的交付内容。Task frontmatter 仍写 `24fcfae13...`，正式 closeout 时须按固定 Review 对象校正。 |
| `reviewed_head` | `c5cec3f637a36b9caec0f90c5ae9b5474cbe2ba0` | Review frontmatter 明载 `reviewed_head: c5cec3f63`，批准只绑定该 head。 |
| `integration_source_head` | `c5cec3f637a36b9caec0f90c5ae9b5474cbe2ba0` | 被接收的交付来源 head；不要拿 Review 元数据提交替代来源 head。 |
| `integration_commit` | **当前保持 `null`；正式验证后填真实值** | 当前 HEAD `b25af8142` 是 Review 获批记录提交，父提交 `23336a1a7` 已保存 Review pin；它不是单凭提交标题即可成立的集成事实。当前提交链证明 `c5cec3f63` 是其祖先，但尚无本 closeout 执行的集成后验证。 |

后续 Task 沿用一条规则：`integration_commit` 只记真实 Codex 集成完成点，不得以“checker 要求字段非空”为理由伪造。若独立来源 head 经核实已在受控集成目标中，Codex 应执行 §4 要求的集成后验证，再将实际验证完成 HEAD 记为 integration commit，并说明原地集成、无 merge/cherry-pick 的事实。若尚未完成集成/验证，则保持 `null` 和 `approved`，不得宣布 `done`。

当前 `tools/governance/check.ps1` 明确规定 `done` 必须有 `integration_commit`（L338–343），而 r21 已裁定未证实集成时应保留 `null`。二者在“不能证明集成但要求 done”的情形存在流程矛盾。统一处理不是把 Review commit 冒充 integration commit：先按上述真实事件原则完成/验证原地集成；若实际没有任何可诚实记录的 integration event，则保持 `approved`，并在后续由 Codex 单独裁定 checker/协议字段契约如何对齐后再终结，不能在本 Task closeout 中掩盖矛盾。后续三个治理 Task 的释放/实现均不得照抄虚构 hash；若 PIN-LINEAGE 要修改同一 checker，须把冲突作为范围冻结前的显式设计决策。

## 4. Canonical Evidence 与 Resource Manifest

Canonical Evidence 的 4 行在**产物种类**上完整：清单 JSON、逐文件 triage、Handoff、独立 Review 均有登记，能覆盖 AC1–AC5。正式关闭前仍应核对 Handoff/Review 的路径、包含该文件的 commit、磁盘 hash 与实际文件一致，并修正 Task 内过时的 `delivery_head` / Owner / 状态元数据（Owner 以 Handoff 实际认领记录核实，不以题面覆盖文件证据）。Review 行当前误 pin 到 `23336a1a7`：`git log -- <Review>` 显示该文件首次出现于 `b25af8142`，且磁盘 SHA-256 与表内一致；Task 检查实测报 `Evidence commit 不含所 pin 文件`。正式 closeout 应将 Review 行 commit 改为实际引入它的 `b25af8142`，再重跑 Task 检查。登记种类完整不等于 pin 正确或 lifecycle 字段 complete。

Resource Manifest 的 7 个 `NOT_APPLICABLE` 类别符合“没有相应独立派生资源/移动”的事实；没有执行移动，因此无需虚构迁移记录。但现有 `evidence_dir` 行只引用 triage 文件 hash，却描述为“2 份证据”，它并未表达 inventory JSON、Handoff、Review 各自的保留路径与引用/文件数核销。故该 Manifest 的处置方向 `PRESERVE_REFERENCED` 正确，**目前作为正式 closeout 清单不完整**。完成 `resource_closeout_status: complete` 前，应把本 Task 实际证据目录和 Handoff/Review 按文件或明确的 manifest 清单核销，记录精确路径、commit/hash、保留位置及引用检查；确认 0 移动、0 归档，并说明七类 N/A 的范围。现有 8 行不能因“本 Task 没移动文件”就自动视为完整。

## 5. Plan / STATUS

正式 closeout 且集成/证据/资源 Gate 通过后，Plan 中节点建议替换为以下**完整行**（把占位符替换为届时查明的真实 integration commit；不得原样写占位符）：

```markdown
|GOV-EVIDENCE-DIR-SWEEP-1|GOV-SOURCE-RECORDS-1|done（集成 <实际 integration_commit>；AC 4/5 MET、AC4 NOT_APPLICABLE；Antigravity Review r1 APPROVED；5 个未登记文件按内容全部 REGISTER，0 个 ARCHIVE/移动；来源 Task 遗留问题由 PIN-LINEAGE-1 / P15-MANIFEST-1 承接）|
```

“AC 4/5 MET”指四项 MET，剩余 AC4 有理由的 NOT_APPLICABLE；不是声称 5 项都是 MET。当前 Plan 46 行、3977 bytes，增加这一替换行不增加行数，也远低于 64 行 / 7000 bytes。Task 正式置为 done 时，Plan 的 done 计数应增加 1；当前 Plan 没有可见的显式 done 总数，若摘要/统计另有计数则一并 +1 并按实际节点重算。

STATUS 当前 Active Task 为 P20，Sweep 不持有 Active/rolling checkpoint 指针，因此**不需要改 Active Task 或运行状态**。可在正式 closeout 后将“本轮治理证据摘要”最小更新为 Sweep 已完成，且 `GOV-P15-MANIFEST-1`、`GOV-PIN-LINEAGE-1` 仍为 proposed/待按释放 Gate 启动；不得将来源 Task 问题写作已清除。Plan 状态更新才是 DAG 权威变更。

## 6. 剩余专项顺序与 Owner

**先释放 `GOV-P15-MANIFEST-1`，再释放 `GOV-PIN-LINEAGE-1`。** P15 manifest 是独立、边界清楚的恢复任务；PIN-LINEAGE 需要改 `tools/governance/check.ps1`，且将共用刚完成 AC-GATE 的 v3 门禁代码。先完成 manifest 可减少并行变更面，并让 lineage Task 的 base 建立在较稳定的治理 checkout 上。当前两个节点均为 `proposed`；本报告只推荐顺序，不代表 Task 已经释放或可立即开工。

PIN-LINEAGE 与 AC-GATE 会编辑同一文件，存在真实冲突风险。释放前 Codex 应冻结单一 Task 的文件所有权和精确 base/head；确认 AC-GATE 变更已集成且工作区无相关 dirty 内容；为 lineage 划定最小 diff，禁止覆盖/回退既有 v3 行为；保留并运行 AC-GATE 原有 12 个 fixture，再对 7 个受影响历史 Task、两个本次来源 Task 和全局治理检查作回归；由非实现者独立 Review，并审查 diff 确认未改写历史 pin、未放宽状态门禁。checker 的 integration_commit 矛盾也应先在 Task 范围中明确处理，不准顺手扩大修改。

不建议继续由 DSH 承担 Owner：题面记录其已连续负责 10 个治理 Task，轮换有助于降低单点负载。按项目角色，建议 **Antigravity 做 Owner、DSH 做独立 Reviewer**（前提是释放时确认 Agent 可用）；若 Antigravity 不可用，依项目故障转移顺序评估 ZCode，但 PIN-LINEAGE 的共享 checker 改动必须由 Codex 冻结契约与集成边界。Owner 与 Reviewer 必须不同，Qoder 不参与。

## 7. 本报告写入前后工作区状态

写入前按 `git status --porcelain` 保存的工作区状态包含大量既存修改和未跟踪文件；本任务不触碰它们。该状态包含 `M .qoder-credits/report.json`、既存 `.orchestrator/`、`archive/`、`doc/`、`verification/` 等未跟踪路径，以及大量其他历史产物；它们均非本报告产生，不能清理或归因于本次。

写入前已执行并查看 `git status --porcelain`；写入后重新执行该命令，输出共 **1238 行**。与写入前捕获的状态逐项核对，唯一新增项为 `?? verification/P09-GOVERNANCE-DEBT-20261019/codex-closeout-sweep-r22.md`；原有 `.qoder-credits/report.json` 修改及既存未跟踪路径均保留。前置命令未单独输出行数，故不报告推算的前置总数。未执行任何 Git 写命令。

**检查器实测（写入后）**：`pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/GOV-EVIDENCE-DIR-SWEEP-1.md` 为 `FAIL (1 errors, 1 warnings)`，错误是上述 Review evidence commit 不含 pin 文件；warning 为 STATUS 预算 3139 bytes / 30 lines。全局 `pwsh -NoProfile -File tools/governance/check.ps1` 为 `PASS (1 warnings)`，同一 STATUS 预算 warning。故题面所述 Task 检查 PASS 与当前 checkout 的实际结果不一致，正式 closeout 必须先修复受限 Task 中的 Review commit pin 并复验；本次授权仅写本报告，未修该 pin。

## 下一步

当前下一步是 Codex 按 §3–5 完成 Sweep 的 Task 元数据、证据/资源 closeout 及集成验证，运行 Task 级与全局治理检查，通过后将 Plan 节点置 `done`。随后按 §6 先释放 `GOV-P15-MANIFEST-1`，建议 Owner Antigravity、Reviewer DSH，并在释放 Task 中冻结真实 base、worktree、allowed paths、可复核字段和完成 Gate。
