# 三个 Task 记录不一致裁定（r39）

日期：2026-10-20  
裁定人：Codex（Lead / Architect / Integrator）  
范围：仅裁定 `M2-SFX-ANNOTATE-R2`、`M2-SFX-SYNTH-BG-AUTO`、`M2-TA2B` 与“AC 全勾”探针信号。不修改 Task、Plan、STATUS、工具或既有证据；仅新增本文件；未执行 Git 写命令，未调用 `coordinator-lease.py`。

## 裁定摘要

| Task | 应有状态 | 裁定 |
|---|---|---|
| `M2-SFX-ANNOTATE-R2` | `done` | 六项 AC 已闭合；AC5 明文允许 challenge 空集的登记/交裁决分支。提交所说的两个用户裁决是后续 T2 训练释放条件，不是本 Task 尚未完成的 AC。现有 `in_review` 是未回填的生命周期记录。 |
| `M2-SFX-SYNTH-BG-AUTO` | `done` | AC5 要求真实 ChatGPT 冒烟；Task 测试表已记真实生成两张图并 PASS，后续证据/收口提交和 `da645b4ea` 均记全 AC 完成。AC 标题括号是执行前待办状态说明，不能脱离其后更新的测试结果解读为仍未执行。 |
| `M2-TA2B` | `done`（重写版） | 文件头的旧 Manga109 方案仍留着 `proposed` / `owner: null` / `branch: null`，但同一文件明确记载用户取消该方案并重写；重写版 AC 由 ZCode 实施、审查并集成。探针读到的是旧 frontmatter，不是当前任务记录。需整理重复 frontmatter，保留旧方案为历史记录。 |

**方法论裁定：AC 全勾不可靠，不能作为“最可处置”优先级或状态推断的充分依据。** 它至多是需要核实的信号。勾选是 Task 文档内的声明；它不自证 AC 的语义已满足、证据仍有效、没有后续相反信息，也不保证探针读到的是同一个 Task 版本/记录。

## 1. `M2-SFX-ANNOTATE-R2`

### 状态

**应为 `done`。** 现状 `in_review` 与已记录完成证据不符，建议由 Coordinator 按 Task 生命周期流程更正状态与收口记录。当前授权范围只允许写本裁定，故本轮不修改 Task frontmatter。

### 依据

Task 的“验收判据”把 AC5 写为：“五 manifest 指纹一致+names 双通道 PASS+BJ 正集 ≥1 页+challenge 非空（或 BJ13 判定仍=delete 时如实登记并交编排裁决）”。Acceptance Criteria 的 AC5 勾选说明已记录五 manifest 指纹一致、names 双通道 PASS、BJ 正集 5 页 11 框，并明确 challenge 仍空集：本轮范围没有 BJ13/14/15，BJ13 未翻案，按允许分支登记 `lock.challenge_note` 与 `challenge.json note`，交编排裁决。其余 AC1–AC4、AC6 也各自写明交付/验证结果，六条均勾选。

提交 `a85d885322a1efda785308b710b719d1c55c1b7e` 的主题是 `close(M2-SFX-ANNOTATE-R2): done @merge 84f952b3`，并记录 DSH 条件闭合、素材指标、BJ 正集、challenge 空集明许分支、integration commit 回填和 STATUS/PLAN 收口。用户给出的祖先核实结果（`84f952b3` 是治理主线祖先）与 Task 中 `integration_commit` 一致，支持交付已进入主线。

该提交尾部“**T2 训练释放待用户两裁决点（量级确认+challenge 空集处置）**”属于后续训练 Task 的释放门槛。它不推翻 AC5 已明许的 challenge 空集登记分支，也没有在本 Task AC 中列为未完成的训练工作。因此不能据此把本 Task 留在 `in_review`。

### 更正责任与缺项

由 Coordinator 在获准修改 Task 时，把状态改为 `done`，在收口记录中引用 `a85d8853`、集成祖先 `84f952b3`，并保留“待两项用户裁决”的后续 T2 条件及指向。**没有缺少决定本 Task 完成状态的证据。**

## 2. `M2-SFX-SYNTH-BG-AUTO`

### 状态

**应为 `done`。** 当前 Task frontmatter 为 `in_review`，应由 Coordinator 按生命周期流程回填为 `done`。仅凭本轮允许范围，本裁定不直接更改状态。

### AC5 含义及是否满足

AC5 不是只要求 mock 单测。原文写：“**真实冒烟=manual 待人工登录后代跑**”，随后规定浏览器交互层用 Protocol/mock 隔离单测，并明确“**真实 ChatGPT 冒烟标 `slow`/manual 由集成方代跑留证**”。所以真实冒烟是 AC5 的要求；括号记录的是当时执行方式/待办条件，不是把真实冒烟从验收要求中豁免。

同一 Task 的测试表随后将“AC5 真实冒烟”列为 `PASS`，记录“用户人工登录→集成方代跑：bg_001/002 落盘 2289/2947KB、src 互异、EXIT=0”，证据为 `smoke-run.log + bg-index-smoke.json`。因此根据 Task 自身记录，AC5 的待办已经完成。勾选与 AC5 最终结果相符，矛盾来自只读标题括号而忽略后续测试结果。

提交 `5907ce596` 的主题为“真实冒烟留证 — AC5 闭合, Task done”；`3a0ce5f70` 的主题为“真实冒烟留证收口 — Task done（全 AC 闭合）”；`da645b4ea` 将 Plan 中状态改为 `done`，提交主题也明确写“全 AC 闭合含真实冒烟留证”。后续 `312de425b` 只把 `status: in_review（…真实冒烟 manual 待用户登录后代跑）` 中的注释放到独立注释行，提交说明称状态/结论未改。这不是撤销真实冒烟证据或重开 AC5 的决定。

### 更正责任与缺项

由 Coordinator 把 Task 状态从 `in_review` 收口为 `done`；可顺手将 AC5 括号改成已完成事实，避免把历史待办误读为当前阻塞，但这项正文编辑需遵守对应 Task 生命周期授权。当前指定来源中没有缺失 AC5 完成证据的迹象。

## 3. `M2-TA2B`

### 状态与文档结构

**当前应承认的实施结果是重写版 `done`，不是原 Manga109 版 `proposed`。** 但这个文件保留了两份相同 Task ID 的 frontmatter：

- 文件开头的 Manga109 方案记录 `status: proposed`、`approval: pending_official_manga109_access`、`owner: null`、`branch: null`、`integration_commit: fae0d8f6…`。
- 随后的变更存档明言用户于 2026-09-30 永久取消 Manga109 前置并改用开放素材池；第二份 frontmatter 将任务改为开放素材池，记 `status: done`、`owner: ZCode`、分支 `agent/zcode/M2-TA2B-OPEN-ASSETS`。
- 重写版 AC1–AC8 全勾；交付记录写 ZCode 实现 `704df9bc`，Handoff 路径为 `doc/handoffs/M2-TA2B-704df9b.md`。本文件在 `integration_commit`、旧/新方案生命周期标记上仍有不一致，需按历史与现行记录规范化。
- `doc/REBASELINE_PLAN.md` 及 `doc/STATUS.md` 均记录 M2-TA2B `done`、integration=`fae0d8f6`。这也说明“8/8 AC”对应后来实施的重写版，而非开头那个从未 release 的 Manga109 方案。

因此“无 owner 却有人完成 8/8”是探针把不同版本的记录拼成一行造成的误报：初始 `proposed` 确实没有授权开工；用户取消并改写方案后，新的工作有 owner、branch、交付与集成记录。不能把它判为未批准实施，也不能凭这个证据把旧 Manga109 方案标成已完成。

### 更正责任与缺项

由 Coordinator 在获准整理该 Task 时，将旧版方案作为显式历史/取消记录保留，将唯一可解析的现行 frontmatter 对齐到重写版 `done`，并核对 `integration_commit` 与 Plan/STATUS 记录。不可只把文件第一个 `status` 从 `proposed` 改成 `done`，否则会把已经取消且未实施的 Manga109 范围错误写成完成。当前指定证据足以判定重写版 done；如需确认具体集成提交对象，缺的是 `fae0d8f6` 的目标提交/集成记录核对，不影响本裁定的范围区分。

## 4. 对“AC 全勾”探针判据的裁定

### 判据不成立为优先级

**“AC 全勾”不应继续叫“最可处置”，也不能单独用来建议关闭或更改状态。应降级为“需核实信号”。** 本轮案例分别展示：

1. 标注 Task 的 AC 全勾在语义审查后支持 `done`，但真正能支持结论的是 AC 验收分支原文、逐条完成说明、集成提交和后续 T2 的边界区分，而不是勾选数本身。
2. 合成底图 Task 的 AC5 标题含待办括号，但测试表与收口提交证明待办后来完成。仅搜寻 AC 行会漏掉其后证据；只看勾选则同样不能确认真实冒烟是否发生。
3. TA2B 说明探针的结构性误读：`frontmatter()` 只取文件中第一段 frontmatter，`ac_counts()` 却扫描整个文件的所有 AC 行。因此它把旧方案的 `proposed`/无 owner 元数据与重写版的 8/8 AC 组合在一起，形成并不存在的单一任务状态。

探针当前的 `classify()` 在 `ticked == total` 时直接把条目放入“all ACs ticked, status not updated”，并推断 closeout “likely never recorded”。这个推断会把记录错位、未核验证据和内容自相矛盾的情况混成一个高优先级类别。它与 r38 的边界（状态不证明活性、证据不直接替代裁定）不一致。

### 建议探针输出

将全勾改为独立布尔信号，例如 `all_ac_boxes_checked=true`，只用于检索，不参与“可处置程度”排序或自动结论。要提高可处置性，至少先输出并核实这些分开的信号：

- **记录结构有效性**：唯一 Task ID/frontmatter、AC 集合属于同一 Task 版本；检测重复 frontmatter、重复 ID、嵌套/多段 AC、无法识别的状态。
- **AC 证据可追溯性**：逐条 AC 是否引用具体验证/Review/交付证据；可机器检查路径存在与否，但“路径存在”不等于证据足以满足语义。
- **显式未完成/矛盾提示**：待人工、`manual`、`pending`、`BLOCKED`、`NOT_RUN`、未闭合条件与勾选并存；或正文出现“已完成”与“待执行”冲突。输出片段和行号供人工裁定，不自行判错或判完成。
- **集成/Review 交叉证据**：integration commit 是否可解析/可达、独立 Review 是否有结论、后续提交是否记载 AC 闭合或重开。缺少信号应写“未知”，不能当失败或成功。

探针的高优先级候选应定义为“有具体可复核的 closeout 线索、且没有未解决的证据冲突”，并明确这是**待人工裁定候选**而非结论。`AC 全勾`只作一个输入信号；在探针支持同一任务记录的版本边界、AC 与证据关联及矛盾检测前，不应称为最优判据。

本裁定不要求修改 `tools/governance/task_liveness.py`；方法论建议应由后续获授权的治理工作实施。

## 5. 当前边界与下一步

本裁定只给出生命周期结论，不改变任何 Task 状态或 Plan 授权。Coordinator 可将本文件作为后续 Task 生命周期修订的裁定依据；修改 `M2-TA2B` 前应先解决同文件双 frontmatter 的保留/规范化方式，不能做单字段机械替换。

推荐下一步：在授权的 Task 生命周期维护中，依本裁定分别收口前两项为 `done`，并将 `M2-TA2B` 整理为唯一现行记录加明确历史取消记录；另为探针改进建立有范围的治理 Task。当前任务完成且未授权上述文件修改：**无需下一步操作**。
