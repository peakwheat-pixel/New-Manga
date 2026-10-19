# GOV-SOURCE-RECORDS-1 Closeout 裁定 r20

- 日期：2026-10-20
- 裁定者：Codex（Lead / Architect / Integrator）
- checkout：`G:\CODEX\New Manga`
- branch / HEAD：`antigravity/P09-AC3-DELETE-HARDEN-1` / `071fb2158`
- 本文件是本次唯一写入；不改 Task、Plan、STATUS、来源 Task、工具或既有 verification。

## 裁定摘要

1. **本 Task 的技术终态应为 `done`。** AC 5/5 达成，独立 Review 对精确 head 给出 `APPROVED`。两个对象 Task 仍有检查错误，是既有证据/资源登记缺陷，不是本 Task 的未完成 AC，也不是把本 Task 改成 `closed_with_limitations` 的理由。
2. 既有 pin 若因后续合法修改而失配，**保留原历史 pin**，不把当前文件内容伪装成原交付时的证据。对同机制的另外 5 个已完成 Task 采用同一规则；逐项核实后用追加记录说明演进，只有当前 Gate 需要证明当前内容时才新增当前版本证据。
3. 对三个后续治理问题分别立项：跨 Task 的历史 pin lineage；来源 evidence_dir 文件盘点/登记；P15 resource manifest 恢复。不得在本 Task 中修这些问题。
4. Task 当前仍未正式 closeout：仓库里的 frontmatter 仍为 `in_review`、`delivery_head: d8ad739d2…`、`canonical_evidence_status: pending`、`resource_closeout_status: pending`、`integration_commit: null`。用户提供的 `delivery_head: cc373560c` 与工作树内容不一致；完成正式状态回填前必须按下文 head 定义统一该字段。此报告本身不声称那些受限文件已修改。

## 2.1 终态：`done`，不采用 `closed_with_limitations`

本 Task 的目标是把两个来源 Task 已有证据所支持的 AC 状态如实回填。其 AC1–AC5 均已完成，独立 Review `doc/reviews/GOV-SOURCE-RECORDS-1-cc373560c-antigravity-r1.md` 为 `APPROVED`，且 Review 明确逐项核对了 12 个补勾及 AC4 保持未勾的理由。`EXPORT-REVEAL-1` AC4 的子项③ `BLOCKED` 被保留为未勾；这不是本 Task 未完成，而是本 Task 正确执行了 AC2/AC3 的约束。

对象 Task 检查仍红，不构成本 Task 的 limitation：检查错误描述的是它们自己的历史证据 pin、目录登记和资源清单。它们在本 Task 开始前已经存在，交付方用基线/改后对比验证、Reviewer 独立复核；本 Task 又明确禁止改这些对象文件或证据。把对象 Task 的既存缺陷算作本 Task 的未完成工作，会错误扩大本 Task 的验收范围，也会把“记录维护达成”与“修复历史证据治理债”混成一个目标。应把缺陷作为后续治理事项处理，不降低本 Task 已达成 AC 的终态。

`done` 是**终态裁定**，不是当前 frontmatter 已经完成状态变更的陈述。按协作协议 §4.1–4.2，正式落地仍需补齐本 Task 自身的 evidence/resource closeout、Plan 行、head/integration 字段并通过只读治理检查；现有授权只允许本报告，因此本次没有代写这些文件。

## 2.2 对象 Task 既有治理缺陷的处置

### Evidence pin 失配：保留原 pin，附加 lineage 说明

两处已知失配都发生在 pin 所指文件提交之后：M2-C1 契约后来演进至 rev 2.11；`SettingsPage.test.tsx` 后来由 `528c6289c` 修改。原 pin 表达的是特定 Task 交付时、特定提交中的字节事实。重算并覆盖原值会把“后来内容”替换成“当时证据”，破坏历史可追溯性，因此不得这样做。

对这两项及**另外 5 个受同机制影响的已 done Task**，默认处置统一为：保留原 evidence_id、原 commit、原 SHA-256；追加清晰的 pin lineage / supersession 说明，记录后续变更提交及现有内容不再匹配的原因。若当前 Gate 确实需要当前版本作为证据，另增一个新 evidence_id，标明当前路径、当前 commit、当前字节 SHA 和其支持的当前 AC/Gate；不覆写历史行。专项范围应逐项列出并验证 6 个 Task 的实际 pin，不得对所有旧 SHA 做批量重算，也不得仅凭文件当前状态推断其历史。

### evidence_dir 未登记文件：逐文件判别，保留有价值证据并闭环

对 `EXPORT-REVEAL-1` 与 `P15` 的目录做只读清单和引用核对。能证明 AC、Review 或交付结论的有效证据应在对应 Task 的证据登记中补列；仅属冗余尝试/过程日志且无现行引用的文件，确认原始路径、hash、引用和可恢复性后，移入相应 Task 的 workspace archive 并保留来源映射。任何被当前文档引用、无法判断或可能含独有信息的文件先原位保留，不得为让 checker 变绿而盲目移动或删除。该工作须在单独 Task 中完成，因为两目录的逐文件证据价值和迁移安全性要分别核实。

### P15 缺失 `resource-manifest.json`：按可核实事实重建，不改成 `NOT_APPLICABLE`

P15 的已有 Resource Manifest 行明确记录真实 worktree 为 `PRESERVE_REFERENCED`，且 `resource-manifest.json` 被引用为 closeout 清单。因而资源并非不适用；把引用改为 `NOT_APPLICABLE` 会与既有事实矛盾。单独 Task 应优先从当前 Worktree Safety Inventory、Task/Review/Handoff 与留存 workspace 记录重建 manifest，并校验引用、路径、hash、处置和结果。只能填可核实字段；无法证实的字段明确标为未知/待核实并保留资源，不得编造历史快照。若 manifest 无法可靠重建，另作有证据的修订裁定并保留缺失事实，不得用 N/A 掩盖。

### 应拆成三个专项 Task

1. **历史 pin lineage 专项**：覆盖这两个已知 pin 和另外 5 个受影响的已 done Task；目标是保留原 pin 并追加版本演进关系。需要跨 Task 证据映射与独立 Review。
2. **来源 evidence_dir 盘点专项**：覆盖 `EXPORT-REVEAL-1` 与 `P15` 的未登记目录内容；逐文件分类，决定补登记或在引用安全后迁移。
3. **P15 Resource Manifest 恢复专项**：仅恢复/核验缺失 manifest 及其引用和 disposition。

这三项的对象、授权范围、证据和安全门槛不同；拆开能避免一次范围把历史证据改写、目录迁移和资源盘点混在一起。Task ID、Owner、Reviewer、base/worktree 尚未释放，故本裁定不臆造；后续需由 Codex 按项目流程建 Task、登记 Plan/STATUS 并冻结 allowed paths。

## 2.3 Head 三元组与 integration 字段

| 字段 | 裁定值 | 说明 |
|---|---|---|
| `reviewed_head` | `cc373560c` | Review frontmatter 的 `reviewed_head`，批准只绑定该精确 head。 |
| `delivery_head` | `cc373560c` | Handoff `doc/handoffs/GOV-SOURCE-RECORDS-1-d8ad739d2.md` 的 frontmatter 明载交付 head 为 `cc373560c…`；该值也对应固定交付及 Review 目标。**注意**：当前 Task frontmatter 却仍是 `d8ad739d2…`，这是仓库内事实冲突，closeout 时须更正为本裁定值，且不可将其说成已经更正。 |
| `integration_source_head` | `cc373560c` | Task 无独立分支/worktree，直接在主 checkout 执行；按来源 head 语义记录被接收的交付 head。 |
| `integration_commit` | `071fb2158` | 无 merge/cherry-pick。记录当前主线中 Review 通过并完成 AC1–AC5 勾选后的集成后 HEAD；不得称为 merge commit。 |

提交链可见 `cc373560c`（交付 Handoff）、`5ed5fde21`（handoff pin bookkeeping）、`7f9f5ae46`（落盘 APPROVED Review 并勾 AC5）、`071fb2158`（勾 AC1–AC4）。后两提交是 Review 后的 Task 文档/记录提交，不改变 Review 已审交付内容的身份。当前 `doc/tasks/GOV-SOURCE-RECORDS-1.md` 的 `delivery_head: d8ad739d2…` 与其自己的 Handoff/Review 及题面陈述不一致，属于正式 closeout 必须消除的 metadata inconsistency。

## 2.4 Canonical Evidence 与 Resource Manifest

### Canonical Evidence

现有 3 行 `SRC-AC1`、`SRC-AC2AC3`、`SRC-HANDOFF` 不足以完整闭环 AC5。应在正式 closeout 中至少补：

- 独立 Review 行：路径 `doc/reviews/GOV-SOURCE-RECORDS-1-cc373560c-antigravity-r1.md`，绑定 `reviewed_head: cc373560c`，记录该 Review 文件实际包含它的 commit 和磁盘 SHA-256，`AC/Gate = AC5`。
- 两个来源 Task 的变更证据：分别记录 `doc/tasks/EXPORT-REVEAL-1.md` 和 `doc/tasks/P15.md` 中 AC 行的已审变更。以含变更的实际 commit 与各文件 hash 固定证据，或登记能稳定复现的精确 diff artifact；`AC/Gate = AC1/AC2/AC3`。不能把当前整个 Task 文档的后续版本 hash 冒充当时 diff，也不能只引用 `git diff` 口头结果。

现有 `SRC-AC1` 与 `SRC-AC2AC3` 只覆盖逐 AC 判定和补勾结果说明，不替代两个来源文件本身的变更证据；`SRC-HANDOFF` 也不替代独立 Review。

### Resource Manifest

现有 8 行从**资源类别**看覆盖 7 个 `NOT_APPLICABLE` 类别及 `evidence_dir`，但不足以证明资源 closeout 完整：`evidence_dir` 行的 SHA 是单个 `ac1-tracing.md` 文件 hash，不能代表目录 manifest；已有 2 份目录证据、Handoff、Review 均是当前引用产物，需逐项说明保留/引用状态和可核验 hash/commit（可另用明确的 inventory manifest 行或引用逐项列出）。没有 worktree 是 `NOT_APPLICABLE`，不代表 Handoff、Review、证据目录也已被盘点。应将这些缺口随 closeout 登记，并将 `resource_closeout_status` 置 `complete` 前完成引用检查；无需搬动任何仍被引用的版本化文件。

## 2.5 Plan / STATUS

Plan 当前行为：

```text
|GOV-SOURCE-RECORDS-1|GOV-EVIDENCE-UNIQUE-1|in_progress（EXPORT-REVEAL-1 与 P15 的 AC 勾选记录维护；只改勾选框与注记）|
```

建议正式 closeout 时替换为：

```text
|GOV-SOURCE-RECORDS-1|GOV-EVIDENCE-UNIQUE-1|done（两来源 Task 共 13 个 AC 逐项溯源；12 项补勾、EXPORT-REVEAL-1 AC4 因子项③ BLOCKED 保持未勾；独立 Review APPROVED；closeout r20）|
```

Plan 仍为 3523 bytes / 41 lines，未触及 7000 bytes / 64 lines 上限。现有 done 计数 37，Task 进入 `done` 后应增至 **38**。`STATUS` 无需改：当前 Active Task 是 P20，本 Task 不是 Active 指针；本次不改变 Gate，也不需要把已关闭工作提升成当前 Task。若后续正式 closeout 流程发现 STATUS 有本 Task 的显式 Active/rolling-checkpoint 指针，再按协议清理；当前给定文件中没有这样的指针。

## 2.6 反复出现的自我检查失效

三个例子是**同一个更高层模式的重复，但不是同一种具体故障**：未实测摘要属于证据与结论不匹配；CRLF 导致 hash 错误属于字节/环境假设未在最终工作树验证；本 Task 自己 AC 漏勾属于交付状态清单未执行自检。现有事实不足以证明是有意“检查者豁免自己”；更准确的共同描述是：Agent 执行治理规则时，没有把该规则对自己的产出做成强制、可观察的提交前条件。前两次由 Reviewer 发现、第三次由 Owner 偶然发现，说明靠个人记忆、Reviewer 抽样或运气都不稳。

**建议在协作协议加入机械 AC gate，值得做。** 单靠“所有已完成 AC 必须勾选”不够机械，因为检查器无法从自由文本推知某项是否已完成。可采用最小结构约定：进入 `in_review` 时每个 AC 必须有显式 machine-readable 状态（如 `MET` / `PARTIAL` / `BLOCKED` / `NOT_RUN` / `UNKNOWN`）及证据引用；`MET` 必须勾选，其余状态必须未勾并有非空原因；进入 `done` 时所有 AC 必须是 `MET` 且已勾选。Checker 对状态与 checkbox 一致性、未勾注记、done 完整性作硬失败，并报告 AC 行号。语义证据是否足以支持 `MET` 仍由独立 Review/Codex 裁定，机械 gate 不冒充语义审查。

这样能直接拦住本 Task 的 4 个已完成 AC 未勾选问题，也能防止把阻塞项勾成完成；它不能独自发现“测试没有实际运行却写成 PASS”或错误的字节假设，仍需相应的执行记录/哈希验证 gate。建议另立协作协议与 checker 的小型治理 Task，不在本 closeout 中修改协议或工具。

## Closeout 顺序与范围

本裁定完成语义与终态判断。依当前“只写本文件”的授权，尚未回填 Task 的终态字段、Canonical Evidence、Resource Manifest 或 Plan，也未运行 closeout 后 checker。正式 `done` 落地时，Codex 需按本裁定解决 `delivery_head` 冲突，补充当前 Task 自身的 Review/diff 证据和资源引用登记，更新 Plan 并完成协议要求的只读 checker；不应因此把三个对象 Task 缺陷纳入本 Task 的 AC，也不应修改它们。

## 动手前后工作区状态

比较使用 `git status --porcelain --untracked-files=all`。动手前目标文件不存在，工作区共有 **1593 行**，UTF-8 编码后逐行 LF 拼接的 SHA-256 为 `265978a29be4caac8bbd29af5396e723263f4a92d8e829dba063804783e3756b`。写入后预期只新增本文件一条 `??` 状态；原有 1593 行及其顺序/内容应保持一致，总计 1594 行。实际写入后复核结果见 Codex 最终回复；任何其它状态变化均不归因于本次写入。

## 下一步建议

Task 终态裁定为 `done`，但在当前单文件写入授权下正式 lifecycle 更新未执行。下一步由 Codex 在获得对应文件写入范围后完成本 Task 自身 closeout（补全 head/evidence/resource 字段、按上文替换 Plan 行、运行 Task checker）。完成此 closeout 后，如需释放治理缺陷专项，应分别建立历史 pin lineage、两个 evidence_dir 盘点、P15 manifest 恢复 Task；目前都未释放，不能自动启动。
