# GOV-AC-GATE-1 Closeout 裁定（r21）

**审查日期**：2026-10-20  
**当前 checkout**：\`G:/CODEX/New Manga\`，\`antigravity/P09-AC3-DELETE-HARDEN-1\`  
**当前 HEAD**：\`23f5d84b0007f4ba0bc9f192ad17a86efce8710b\`  
**本报告范围**：只裁定 Task closeout 与三个后续治理 Task；不回填 Task、Plan、STATUS 或代码。

## 结论摘要

1. **终态裁定：\`done\`。** 本 Task 目标是对新释放的 v3 Task 强制 AC 状态自洽。它不负责清算历史存量；协议已清楚记录该边界，并为存量建立三个独立 Task。Review r2 为 \`APPROVED\`，AC 6/6 为 \`MET\`。存量仍有 25 个历史 Task 未勾 AC，不构成本 Task 的 limitation。
2. **正式 lifecycle 尚未完成。** 目前 Task 文件仍为 \`in_review\`，\`integration_commit: null\`、\`canonical_evidence_status: pending\`、\`resource_closeout_status: pending\`。按协作协议 §4.1–4.2，Codex 完成集成后验证、证据/资源收口和权威检查前，不能把当前仓库状态描述为已正式 \`done\`。
3. 三个专项按 **GOV-EVIDENCE-DIR-SWEEP-1 → GOV-P15-MANIFEST-1 → GOV-PIN-LINEAGE-1** 顺序释放；先完成 GOV-AC-GATE-1 的正式集成和 closeout。建议后续专项 Owner 由 Antigravity 承担、DSH 独立 Review，以打断 DSH 连续承担九个治理 Task 的负载；每个 Task 仍须在释放时检查 Agent 可用性和冻结真实基线。
4. **head 裁定**：审查固定点是 \`bf088bb01\`；应将 \`delivery_head\` 校正到 \`bf088bb01\`，因为它含 r1 修复且是 r2 实际审查对象。当前 \`23f5d84b0\` 是审查通过后落盘 Review 与 AC6 的 HEAD，不应冒称为 delivery head。当前没有 Codex 集成提交，故 \`integration_commit\` 暂为空。

## 2.1 终态：\`done\`，不是 \`closed_with_limitations\`

这是一个窄范围但完整达成的规则变更：新建/释放的 \`governance_version: 3\` Task 获得机器检查；v1/v2 存量保持原样。AC1–AC6 均为 \`[x]\` + \`<<MET>>\`，Review r2 对固定 head \`bf088bb01\` 给出 \`APPROVED\`，并独立验证了 \`done + PARTIAL\` 被 gate 拒绝、\`done + NOT_APPLICABLE\` 不被误伤，以及 12/12 夹具结果。

25 个历史 Task 仍有未勾 AC，是**有意限定的兼容策略**，不是本 Task 没有完成其目标：本门禁明确“只阻止新增此类缺陷，不清算存量”；全量追溯会篡改历史证据/依赖链或令检查长期全红。历史债务另有三个 \`proposed\` 专项 Task 承接。因此不应把这项已明示的范围边界重复记为 limitation。只有在专项 Task 后来证明“阻止新增”也未实现或承诺的 v3 行为不可用，才重新评估本 Task 的结论。

**落地条件**：当前 Task frontmatter 仍是 \`in_review\` / pending 状态。Codex 应先完成下文的集成、证据与资源登记及检查，再把正式状态改成 \`done\`；本报告本身只是终态裁定，不声称元数据已落盘。

## 2.2 三个 proposed 专项 Task 的释放

三个 Task 文件均存在，Plan 当前列为 \`proposed\`。不要因本报告自动把它们改成 \`ready\`；先完成 AC-GATE closeout，然后逐一冻结 owner/reviewer、base、branch、worktree、allowed paths，并把运行指针登记到 STATUS。

### 顺序与范围

| 顺序 | Task | 释放条件与建议 |
|---|---|---|
| 1 | \`GOV-EVIDENCE-DIR-SWEEP-1\` | 先对 \`EXPORT-REVEAL-1\`、\`P15\` 两个目录逐文件清单与查引用。发现的有效证据能为后续 manifest/lineage 提供已核实事实。只有逐项证明无引用、可恢复后才能执行 AC4 移动。Task 文件里的 archive 目标目前出现疑似控制字符（呈现为 \`New Manga.workspace[BEL]rchive\`）；释放前必须修为字面路径 \`G:\\CODEX\\New Manga.workspace\\archive\\<task>\\\`，并校验文件实际字节没有控制字符。 |
| 2 | \`GOV-P15-MANIFEST-1\` | 依已有 P15 记录和 worktree 实况恢复 manifest；只能填可追溯字段，未知值保留未知，不得伪造或写 \`NOT_APPLICABLE\`。可在 Sweep 已确认 P15 证据目录内容后释放。 |
| 3 | \`GOV-PIN-LINEAGE-1\` | 核实七个 Task 的 pin、交付提交之后的路径变更、当前 hash，再追加 lineage；原 pin 和原 SHA 不得重算覆盖。先冻结 AC4 对检查器的选择。如果选择改 \`check.ps1\`（选项 a/b），将它视作共享治理基础设施变更，单独锁定允许范围并增加针对受影响旧 Task 与新 gate 的回归验证；若选项 c，则明确这些历史 Task 保持 checker error 的后果。 |

### Owner / Reviewer

建议将三项的初始建议 Owner 从连续承担九个治理 Task 的 DSH 轮换给 **Antigravity**，Reviewer 用 **DSH**；两者不得相同。Antigravity 负责一般编程和治理检查器修改，DSH 的独立核查经验适合证据溯源与复核。每次实际释放前仍要核实 Agent 的工作负载与能力；如无可用 Owner，则保持 \`proposed\`，不虚构认领。

这是 Owner 建议，不代表这些 Task 已释放。角色适配上，Sweep 和 P15 manifest 更偏只读证据盘点/恢复；若释放时确认 DSH 空闲且任务负载已轮换，可将其中一个 Owner 交给 DSH，但避免同一 Owner 同时持有多个 active Task。

### 释放前统一准备

- 当前三个 Task 的 \`base_commit\` 均为旧值 \`3539d8d75\`，不得照抄。AC-GATE 集成完成后，在包含该集成的实际 HEAD 上逐个做 Reality Check，核对目标文件、基线、任务依赖与已存在的 dirty/untracked 内容；linked worktree 放入 \`G:\\CODEX\\New Manga.workspace\\worktrees\\<TASK-ID>\\\`。
- 先将 Task 文本中的 \`proposed\` AC 补成准确、可验证的范围与交付物；尤其 PIN-LINEAGE 的“7 个 Task / 7 处”须由独立 inventory 确认，checker 方案须在修改前冻结。
- 所有三个 Task 都应绑定 AC-GATE closeout 后的基线；若后一个 Task 确实依赖前一个产物，应把实际 Task ID 写入依赖并串行释放，而不是只依赖口头顺序。
- **与本 Task 修改同一 \`tools/governance/check.ps1\` 的风险可控，但必须显式隔离。** AC-GATE 已落地后再以其集成 HEAD 为基线；PIN-LINEAGE 排在最后，避免并发改 checker。保留 AC-GATE 的现有夹具，变更后重跑它们和受影响的全局治理检查；Review 要检查新增分支没有绕过 v3 状态 gate，也没有改写历史 pin。

### 下一 Task 指令建议

完成 AC-GATE 正式 closeout 后，优先释放 \`GOV-EVIDENCE-DIR-SWEEP-1\`，Owner 建议 Antigravity、Reviewer DSH。释放前 Codex 应在 Task、Plan、STATUS 登记其精确 base、独立 worktree 和 allowed paths，并修复/核验 archive 目标路径的控制字符问题。Owner 只读盘点 \`EXPORT-REVEAL-1\` 与 \`P15\` 的 evidence 目录，逐文件记录路径、大小、SHA-256、内容依据、Canonical Evidence 登记情况及全仓引用；仅对已证明无引用且可恢复的项执行已授权移动。交付 inventory、判定表、引用核对、移动记录（如有）、Handoff 和固定 head；由 DSH 独立 Review。命令、skip/blocker 与完成 Gate 按释放 Task 写明，任何未核实项都不得写成 PASS。

## 2.3 head 三元组及 integration 字段

| 字段 | 建议值 | 理由 |
|---|---|---|
| \`delivery_head\` | \`bf088bb0140ebd177034805646c6bce3575b0881\` | \`d27d4e2e9\` 之后的该提交补上 r1 发现的 \`done + PARTIAL\` 自身门禁缺口；Review r2 实际固定审查此 head。故不应继续将旧的 \`fbf459f28\` 或中间 \`d27d4e2e9\` 当作最终交付 head。 |
| \`reviewed_head\` | \`bf088bb0140ebd177034805646c6bce3575b0881\` | Review r2 frontmatter/正文所载的精确对象。 |
| \`integration_source_head\` | \`bf088bb0140ebd177034805646c6bce3575b0881\` | Codex 集成时应以 Review 批准的源 head 为集成对象；若集成方法产生新提交，另记录 old→new 对应关系及验证 head。 |
| \`integration_commit\` | **当前为 null；正式集成后写真实值** | HEAD \`23f5d84b0\` 在本分支上，提交说明为 Review approved / AC6 落盘；它不是已证明的 Codex 集成提交。不得为了填字段把审查后的元数据提交冒称为集成提交。若 Codex 核实项目当前 checkout 本身就是受控集成目标，并按 §6 完成集成后验证，则记录实际集成完成 HEAD，并在 closeout 说明为何不产生 merge/cherry-pick。 |

提交链为：

\`\`\`text
fbf459f28  gate 初版
  → 489d7b1ba  Handoff
  → d3eedd735  pin 回填
  → d27d4e2e9  夹具证据移出仓库
  → bf088bb01  修复 done + PARTIAL 缺口（最终审查交付 head）
  → 23f5d84b0  落盘 r2 Review + 勾选 AC6（当前分支 HEAD）
\`\`\`

因此 delivery head 应跟随最终被 Review 的实现版本更新为 \`bf088bb01\`；其后的 \`23f5d84b0\` 是 closeout 元数据变化，应作为当前 HEAD/集成后记录看待，不能反向声称 Reviewer 审过它的代码。当前 Task 文件仍写 \`delivery_head: fbf459f28941f3760366d5f8e581f8e8ae79ce18\`、\`integration_commit: null\`，尚未与上述裁定同步；当前文件还写 \`owner: codex\`，而任务描述给出的 Owner 是 dsh。Codex 应在正式 closeout 时核对实际认领/交付记录后统一 Owner 元数据，不可仅凭题面或旧 frontmatter 猜改。

## 2.4 Canonical Evidence 与 Resource Manifest

### Canonical Evidence

当前五行覆盖协议、checker、夹具、writeup 和 Handoff；它们能证明实现与交付，但 **AC6 还应单独 pin 最新 Review r2**。建议补一行：

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| GATE-REVIEW-R2 | AC6 | \`doc/reviews/GOV-AC-GATE-1-bf088bb01-antigravity-r2.md\` | \`23f5d84b0\`（核对该 blob 所在 commit） | 正式回填时按该 commit 中的文件计算 | \`CANONICAL\` |

r1 是 \`CHANGES_REQUESTED\`，对理解缺口修复有历史价值，但 AC6 的最终批准由 r2 提供；无需把已 supersede 的 r1 作为当前批准证据。当前工作区可见并已跟踪 r2 文件；指定的 r1 文件在当前 checkout 中**未找到**，所以不要凭给定文件名虚构其 pin。若以后找到可核实的 r1 原件，可在历史记录中引用，不替代 r2。

另外，表中 \`GATE-FIXTURES\` 指向测试文件，不能独自证明“12/12”运行结果；应确保 \`GATE-WRITEUP\` 对应的运行结果在其正文明确记录（现有 writeup 仍描述 9 例初版，故须核对它是否包含 r2 的 12/12 结果）。若 12/12 仅存在于 Review r2，可由 r2 行支撑 AC6 的独立验证，同时为 AC4 增补可复核的结果证据或更新适当证据项；不得把未保存的运行日志宣称为已 pin。

### Resource Manifest / 基础设施保留

现有 8 行覆盖七类 N/A 资源和一个 \`evidence_dir\` 类别，但**不等于完整 closeout**：evidence_dir 行的 hash 是 writeup 单文件 hash，不是目录 inventory；Handoff 与 Review 也未作为独立产物核销。正式关闭前应逐项登记实际引用/保留结果和 hash/commit，并核实证据目录文件集合。

\`doc/09_COLLABORATION.md\` §4.3 与 \`tools/governance/check.ps1\` 是本 Task 改动的**治理基础设施**，必须在 closeout 里明确标为 **\`PRESERVE_REFERENCED\`**，目标仍为仓库原路径。前者是 v3 AC 规则权威来源；后者是执行规则的检查器，并被后续 Task/治理流程引用。不要把它们误归入临时 build/resource 而清理。建议在 Manifest 加两条 source/infrastructure 项，分别列实际提交/hash与引用检查结果；同时逐项核销 writeup、Handoff、Review 和 evidence_dir。保留不妨碍 done，但必须证明引用与保留位置。

## 2.5 Plan / STATUS

Plan 当前行仍为 \`proposed\`，尚未反映 Task 的 \`in_review\`。只有集成与 closeout 正式完成后，建议替换为：

\`\`\`markdown
|GOV-AC-GATE-1|GOV-SOURCE-RECORDS-1|done（集成 <实际 integration_commit>；AC 6/6 MET；Antigravity Review r2 APPROVED；v3 阻止新增，历史存量由三个专项处理）|
\`\`\`

不要将占位符写进 Plan；必须填 Codex 实际集成完成的 commit。Plan 现在是 42 行、3956 bytes，仍低于 64 行 / 7000 bytes 预算。正式置为 \`done\` 时，done 计数从 **38 增为 39**，并按实际 READY/in_review 集合重写摘要行。三个专项仍保持 \`proposed\`，直到分别完成释放 Gate。

**STATUS 应更新一条治理证据摘要，但不切换 Active Task。** 当前 Active Task 仍是 P20；不得因 AC-GATE 关闭将其替换。正式 closeout 后，把“GOV 三链均已集成”的概述更新为明确列出 AC-GATE 已完成、三个专项仍 proposed 的状态，并保持 P20 的唯一 Active 指针不变。若 STATUS 有预算约束，先实测后作最小改写。

## 2.6 方法论：机械门禁有效，但不能单独证明长期改善

本 Task 中 gate 两次抓到交付方的字段不一致，且第二次是在 Review 已批准、\`PARTIAL → MET\` 后忘记勾选时发生。F9 夹具此前已存在，说明这是一个真实、确定性、可自动检查的失误类别。对“状态标记/勾选一致性”这种局部机械不变量，门禁比要求人记住规则更可靠：它把遗漏变成提交/状态推进前可见的失败。

但两次命中仍来自一个 Task、同一位交付方和短观察窗口，无法证明长期发生率已经下降，也不能排除新规则刚发布带来的注意力效应。建议从首批 v3 Task 开始记录，每个 Task 在首次进入 \`in_review\` 时：

- AC 状态格式/勾选不一致被 checker 捕获的次数与受检 AC 数（每 100 个 AC 的捕获率）；
- Review 或集成后才发现的漏标/矛盾 AC 数（逃逸率）；
- 因规则误报而修正 checker 的次数、每次失败到修复的周期；
- 适用 v3 的 Task 总数、豁免/绕过次数。不能只报“检查通过”或失败次数，必须保留分母。

至少观察未来 **20 个 v3 Task**（若六个月后不足 20 个，明确样本不足并继续跟踪），比较早期与后期的 checker 捕获率和 Review 逃逸率。成功信号应是提交 Review 后的逃逸率下降且无绕过增长；捕获率初期上升可能表示 gate 正在发现旧式遗漏，不应被误判为退化。

**伪安全感风险仍然存在。** 协议写明“不能验证标记是否诚实”是必要的，但单独这一句不足以形成完整保障。绿色只说明格式自洽，不证明 \`MET\` 有事实支撑。应继续执行已有的 Canonical Evidence pin 校验、Reviewer 对照 AC 实读证据、Codex 集成后验证；每个 \`MET\` 都有明确 evidence 映射，运行结果带可复核命令/退出码/环境，缺证据写 \`NOT_RUN\` 或 blocker，不能由 checker PASS 推导语义完成。**本 gate 是一致性控制，不是证据真实性证明。**

## 本文件写入前后工作区状态

比较口径为 \`git status --porcelain --untracked-files=all\`。写入前共 **1593 行**；UTF-8、逐行 LF 拼接后的 SHA-256 为：

\`\`\`text
b5b01118610c8fec1f1c4178c7189735ccfe7fa3acd2d9ba908fd4b598640ac1
\`\`\`

其中已有一个 tracked 修改 \`M .qoder-credits/report.json\`，其余为既存 untracked 状态；本次不触碰这些内容。写入后应共 **1594 行**，且与写入前的 1593 行逐行相同，只额外出现：

\`\`\`text
?? verification/P09-GOVERNANCE-DEBT-20261019/codex-closeout-acgate-r21.md
\`\`\`

写入后实际比较结果在 Codex 最终回复中报告；若存在其他差异，不归因于本次写入。

## 下一步

当前可执行下一步是由 Codex 完成 \`GOV-AC-GATE-1\` 的正式集成与 closeout：更新准确 delivery/integration head、Review evidence、资源清单和状态；按协议运行 Task 级与全局只读治理检查。之后才释放 \`GOV-EVIDENCE-DIR-SWEEP-1\`，建议 Owner Antigravity、Reviewer DSH，按 §2.2 的具体范围与安全条件执行。
