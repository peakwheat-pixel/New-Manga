# GOV-EOL-PIN-1 与 GOV-UNTRACKED-BACKLOG-1 合并 Closeout 裁定 r17

日期：2026-10-20  
裁定者：Codex（Lead / Architect / Integrator）  
主 checkout：G:\CODEX\New Manga  
branch：antigravity/P09-AC3-DELETE-HARDEN-1  
当前 HEAD：49ab52fc34109f9563818123a515ee7d99b25d2d

## 裁定摘要

- GOV-EOL-PIN-1 与 GOV-UNTRACKED-BACKLOG-1 的正确技术终态均为 **done**；没有依据使用 closed_with_limitations。
- EOL Task 的 Review 对固定交付 head 48f29726a 给出 APPROVED_AFTER_FIX，并明确核验了 Task 自身漏加规则的问题已修复。它构成 r16 要求的独立复核；Backlog 的跨 worktree CRLF P1 已解除，无需再做一次技术确认。
- 这不等于现有 Task 文件现在已满足 done 门槛：两份 Task 的 canonical_evidence_status 和 resource_closeout_status 仍为 pending，EOL 的 Resource Manifest 为空，Backlog 的 Resource Manifest 也未覆盖模板列举的每类资源。应先补齐表格和 Closeout Record，再更新状态与 Plan，并运行 Task-scoped checker。此轮只获准写本报告，故未改这些文件。
- 两份既有 Handoff 都已存在，无需另产 Handoff。它们是交付交接物；closeout 只需在 Task 中保持准确引用并完成资源核销。
- GOV-EVIDENCE-UNIQUE-1 的 GOV-DEBT-CLEANUP-2 依赖已满足，Plan 仍将其列为 READY。两项 closeout 完成后即可按冻结范围释放；该只读 Task 不需 worktree。
- 两次“审计者遗漏自己”属于可预测的自指审计失效模式，值得加一道轻量检查；见方法论部分。本轮不实现。

## 1. 两项 Task 的终态与 P1

### GOV-EOL-PIN-1

**终态裁定：done。** AC1–AC5 均勾选，独立 Review 已 APPROVED_AFTER_FIX。Task 原定目标（为被 pin 的 Backlog evidence 与 Handoff 固定 LF）已经完成，Review 还抓出并促成修复了 EOL Task 自身两个 pin 的行尾遗漏。其自身两个现有 pin 在当前 checkout 都与实际 SHA-256 相符，目标文件显示 i/lf w/lf，且 git check-attr 返回 text=set、eol=lf。

Review 的复核算完成：它审查的精确 head 是 48f29726a，报告先记录缺陷，之后给出 APPROVED_AFTER_FIX；Task 的两个现有 pin 在当前 checkout 匹配，且自身路径规则已生效。**不需要再等额外技术验证或第二位 Reviewer。** 仍待办的是常规 closeout 记录，而不是 P1 修复或 Review。

当前 Task frontmatter 的两个 closeout 状态仍是 pending，且 Resource Manifest 没有数据行，因此当前文件还不能直接宣称生命周期门槛已完成。Closeout 时应至少登记 .gitattributes、Task evidence 目录、无 worktree、无 task-env、无 dataset/model/test-material、无独立 artifact/temp/exchange，以及 agent-output（若确实没有则逐项记 NOT_APPLICABLE 并给依据）；将有引用的版本化规则/evidence 标为保留。补齐后再置 canonical_evidence_status: complete、resource_closeout_status: complete。Review 继续由 frontmatter 的当前 Review 指针和 reviewed_head 记录；无需把审查意见本身再作为一个被审查 Task 的 Canonical Evidence pin，以免引入递归 pin 链。

### GOV-UNTRACKED-BACKLOG-1

**终态裁定：done。** AC1–AC6 均勾选，Review 对固定 a2f411a68 为 APPROVED。r16 的阻断条件是“修复完成和复核前不宜转 done”；其后独立 EOL Task 已完成并获 APPROVED_AFTER_FIX，修复覆盖本 Task 的 5 份 evidence 与 Handoff；当前这些六项文件的 SHA-256 均与 Task 表中 pin 匹配，显示 i/lf w/lf、text=set、eol=lf。因此 **P1 已解除**。两份 Review 的时间顺序和内容显示复核已发生；不需要再追加一轮技术 Review。

当前 Backlog Task 的已有 Resource Manifest 记录了 backlog、CON、evidence dir 和 agent output，但模板还要求逐项覆盖 worktree、task-env、dataset/model/test-material、artifact、temp、exchange 等类别。不适用项须明确列成 NOT_APPLICABLE 并提供核实依据。该补齐是 closeout bookkeeping，不是新阻断。完成后将两项 closeout 状态置为 complete，再设 done。

closed_with_limitations 不适用于这两项：已释放 AC 均达成，Backlog P1 已修复且复核通过；不存在需要以 limitation 保留的失败 AC 或未解决 finding。

## 2. Head 三元组与 integration_commit

两个 Task 都直接在主 checkout 交付，没有独立来源 branch/worktree；因此来源 head 等于其固定交付 head。审查 head 保持 Review frontmatter 绑定值，不用当前主 checkout HEAD 替代。

| Task | reviewed_head | delivery_head | integration_source_head | integration_commit |
|---|---|---|---|---|
| GOV-EOL-PIN-1 | 48f29726a0b7f94d9829bd070457ad3d8f3e5884 | 48f29726a0b7f94d9829bd070457ad3d8f3e5884 | 48f29726a0b7f94d9829bd070457ad3d8f3e5884 | null（不适用；无独立 merge/cherry-pick/集成提交） |
| GOV-UNTRACKED-BACKLOG-1 | a2f411a6894c7de351173695519fd1b640cbdbc4 | a2f411a6894c7de351173695519fd1b640cbdbc4 | a2f411a6894c7de351173695519fd1b640cbdbc4 | null（按 r16 裁定；不适用） |

EOL 当前分支 HEAD 49ab52fc3 和 Backlog Review 提交 94efecc75 都是后续历史，不能回填为各自 delivery/integration head。Backlog Task 工作树目前有一项既存未提交修改：其 Handoff evidence 行的 introducing commit 从 474926c18 修正为包含该文件的 48f29726a。这项属于原工作区既存内容，本轮没有改动；Closeout 时应保留该正确修正并确保与被 pin 文件存在性一致。

## 3. Canonical Evidence 与 Resource Manifest 核对

### GOV-EOL-PIN-1

| 行 | 当前 pin | 当前文件核对 | 裁定 |
|---|---|---|---|
| EOL-AC1AC3 | verification/GOV-EOL-PIN-1/ac1-ac3-eol-fix.md，commit d19e74ab4，SHA-256 b34e336ddc76255513c07a6e21770d2cc82826adcd27eda1e1891d085dce4c0b | 实际 SHA-256 与 pin 相同；i/lf w/lf；text=set/eol=lf | 完整、有效 |
| EOL-HANDOFF | doc/handoffs/GOV-EOL-PIN-1-d19e74ab4.md，commit 48f29726a，SHA-256 9975fe1c0c37157719d35b8606fac879005ac102c897dca0997c40ccd94ebfb2 | 实际 SHA-256 与 pin 相同；i/lf w/lf；text=set/eol=lf | 完整、有效 |

Review 文件为 doc/reviews/GOV-EOL-PIN-1-48f29726a-antigravity-r1.md，由 commit 49ab52fc3 引入，实际 SHA-256 为 e10de48a0b317b00db7889234aafcb1cf745bd83c56fb3d16008a4550d7e1889；当前行尾为 i/lf w/mixed，且没有对应 text/eol 属性。**本裁定不要求把 Review 本身登记为 Canonical Evidence 行**：它是生命周期审查结论，已由 Task frontmatter 的 Review 指针、Review frontmatter 的精确 reviewed_head 和 verdict 记录；现有 Canonical Evidence 表已分别为 AC1–AC3、AC5（Handoff）提供证据。将审查报告也 pin 成待审 Task 的 Canonical Evidence 会形成自指 pin 链，超出“每个 AC/Gate 有当前证据项”的要求。若项目以后明确要求 pin Review 文件，应另定通用规则处理 w/mixed，不在本次 closeout 临时增加 .gitattributes 规则。

EOL Resource Manifest **不完整**：当前只有说明，没有表格数据行。Closeout 应补全已列举资源类别的处置记录：.gitattributes、证据目录及 Handoff 为被引用内容并保留；worktree 为空（未创建）、task-env、dataset/model/test-material、额外 artifact/temp、agent-output、exchange 等按实际核实结果标 NOT_APPLICABLE 或明确 disposition。Review 作为生命周期记录，不另列为派生资源。

### GOV-UNTRACKED-BACKLOG-1

现有六项 Canonical Evidence（五项验证文件及 Handoff）均已逐项计算当前 SHA-256，与 Task 表登记值一致；六项均为 i/lf w/lf，属性为 text=set/eol=lf。对应已登记值如下：

- ac1-ac3-composition-and-references.md: a86b42336085345e0d27edf5664061aac53d4337caf98e0b23a80ca62d883e6a
- ac1-ac3-inventory.json: 4ec0cf8b8f4fed0eb9169a00a3eb948c54cd52f6f07c4093bf30e2165efff1db
- ac2-anomalous-entries.md: 9b8a87549371cd17a77812c7e1c80df1de067b2c2074c1ab7050a0fccb1f827b
- ac3-references.json: e4dd2cb52db29825d6e241cf4b1510f74e348eb30da6c7372a05cf30585df3dc
- ac4-worktree-mirror-guide.md: 9611a6c0be6a9d91d58a060003f1338c51e7ef7aeb7561f23f3d1e36b50b8945
- Handoff GOV-UNTRACKED-BACKLOG-1-60970cf9d.md: bd978b7d2865dde1865260ce147fb4e71a9115a4e54680829701ff5d06eefed6

Backlog Review doc/reviews/GOV-UNTRACKED-BACKLOG-1-a2f411a68-antigravity-r1.md 的 SHA-256 为 df8935f39501e0e3cf01c058a966aacf653eac9f5bb81c0c17ffa63872d5e326，由 94efecc75 引入；同样作为生命周期 Review 指针，不要求另加 Canonical Evidence 行。

Backlog Resource Manifest 有四行，能支撑既有保留结论，但未完整覆盖模板列举的全部 resource_type，故 resource_closeout_status 目前不能据此设为 complete。应保留 backlog、CON、evidence dir 的现有 disposition，保留 agent-output 的 N/A 记录，并补 worktree、task-env、dataset/model/test-material、artifact、temp、exchange 的逐项结论和核实依据。核销无需删除或移动任何用户文件。

本轮执行了两个 Task-scoped checker：GOV-EOL-PIN-1 与 GOV-UNTRACKED-BACKLOG-1 均 PASS (1 warnings)；warning 是 STATUS 体量提醒。Checker PASS 不证明 Resource Manifest 的语义完整性，不能代替上述 closeout 核销。全局检查结果用户提供为 PASS。

## 4. Plan / STATUS

Plan 当前经读取为 **3426 bytes / 41 lines**，仍在 7000 bytes / 64 lines 上限内。两个节点的完整替换行如下：

    |GOV-UNTRACKED-BACKLOG-1|—|done（1591 个未入库文件的分类与边界化；只读盘点，不删不移；含 CON 与长句名异常条目；AC1–AC6 达成；跨 worktree LF 风险由 GOV-EOL-PIN-1 修复并复核；closeout r17）|
    |GOV-EOL-PIN-1|GOV-UNTRACKED-BACKLOG-1|done（为 hash-pinned evidence 与 Handoff 固定 LF；AC1–AC5 达成；自身 pin 已复核；closeout r17）|

若两项都从当前非终态转为 done，Plan 尾部 READY 常数不变：仍是 ARCH-DOC-REBASELINE、P20、GOV-EVIDENCE-UNIQUE-1 三项；done 计数从 34 增为 36。应只替换计数，不改变 READY 列表。

STATUS.md 无需改动：r15 后它不复制 Plan 的节点状态；本轮两个治理 Task 都不是 STATUS「当前 Task」P20，也不改变 Gate 与保留项。其当前 Task 与 Gate 内容不需为本次 closeout 更新。

## 5. 下一 Task：GOV-EVIDENCE-UNIQUE-1

- 依赖 GOV-DEBT-CLEANUP-2 当前在 Plan 中为 closed_with_limitations，且 GOV-EVIDENCE-UNIQUE-1 已明确 READY。该依赖节点已有 closure evidence，依赖条件已满足；它未完成的最终唯一证据判定由当前 Task 承接，不继承或改写为 PASS。
- 在两个 closeout 文档更新并通过 Task checker 后，可立即释放/派发 GOV-EVIDENCE-UNIQUE-1。由于其范围是只读判定 61 个 evidence 文件，不建 worktree；需先冻结并登记精确 61 文件清单、base/head、Owner/独立 Reviewer、只读 allowed_paths、五项 AC 的逐项证据格式和不得修改 pin 的约束。核对运行器不会写文件，再按正常协调流程释放。
- 建议 Owner：DeepSeek Harness；独立 Reviewer：Antigravity。Qoder 不参与本项目任务分配。

可直接转发的准备/释放指令：

> DeepSeek Harness：在 GOV-EVIDENCE-UNIQUE-1 现有 READY 范围内，先冻结 61 个输入文件清单、只读操作步骤、逐项唯一性判定标准及五项 AC 的证据结构；确认不改任何 pin、Task、Plan、STATUS 或输入文件，不创建 worktree。登记真实 base/head 与 allowed_paths 后开始执行。Antigravity 对精确 head 作独立 Review。先核实本裁定所列两个前置 Task 已在 Task 文件与 Plan 完成 closeout；不要把 GOV-DEBT-CLEANUP-2 的未完成 AC 改写为 PASS。

## 6. 自指检查方法论

两次事件不是偶发的个体疏忽，而是**可预测的治理失效模式**：检查者把目标规则应用于被审对象，却将自己的交付物隐式排除在被检查集合之外。汇总审计会复制未实测数字；行尾治理会保护此前 evidence 而漏掉本 Task 自己的 evidence/Handoff。只要求“仔细一点”不能稳定消除这个结构性盲区。

值得在协作协议或 checker 层加一道轻量自指检查。最小可行形式：

1. Task 明确列出“纳入检查的自身产物”字段，至少包含本 Task 的 verification、Handoff 和本次交付引用的 evidence；规则覆盖范围不得只由前序 Task 或输入清单生成。
2. 关闭前执行一个自指断言：将同一检查规则运行于“目标集合 + 当前 Task 自身产物集合”，并把两集合与实际检查清单对照。聚合数量则从冻结的逐文件 manifest 重算，保留机器输出与汇总值的差异检查。
3. Checker 可先只做确定性覆盖检查（例如 Canonical Evidence 路径是否被当前任务声明的行尾/哈希规则覆盖、报表计数是否等于其逐项 manifest 数量）；语义判断仍由独立 Reviewer/Codex 完成。

此项为方法论裁定，不是本轮授权的实现范围。

## 7. Git 状态差异与写入边界

写入本报告前，git status --porcelain --untracked-files=all 共 **1594 行**：**2 项 tracked modifications**（.qoder-credits/report.json、doc/tasks/GOV-UNTRACKED-BACKLOG-1.md）和 **1592 项 untracked**。doc/tasks/GOV-UNTRACKED-BACKLOG-1.md 的既存修改是 Handoff evidence introducing commit 的修正（474926c18 → 48f29726a）。

本报告写入后再次执行同一状态命令；除本文件成为唯一新增 untracked 路径外，其余状态应完全相同。实际前后差异附记于本节末尾。

本轮仅写本报告；未改 doc/**、tools/**、src/**、tests/**、.gitattributes 或任何既存 verification 文件；未调用 coordinator-lease.py，未执行 Git 写命令，未移动/删除仓外文件。

### 实测前后状态

- 写入前：1594 行（2 tracked modification，1592 untracked）。
- 写入后：1595 行（2 tracked modification，1593 untracked）。
- 新增状态行：?? verification/P09-GOVERNANCE-DEBT-20261019/codex-closeout-eol-and-backlog-r17.md
- 消失状态行：无
- 结论：仅新增本报告；其他既存状态不变。