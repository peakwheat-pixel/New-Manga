<!-- codex session: 01a15283-8f1c-7843-a64c-bcbf5d88a532 | reviewed_head: 7ffc9e2cf -->

# P09-AC3-DELETE-HARDEN-1 R14

- `reviewed_head`: `7ffc9e2cf874f19f1ba3bbf9b398ba7437a3ff6a`
- `decision`: `changes_requested`
- `findings`: 2

## 矛盾与状态口径

1. **AC 状态仍未统一。** Task 将 AC11 的测试结果记为 `PASS`，正式 Handoff 却记为 `PARTIAL`；理由是 P09 AC3 仍为 `BLOCKED`。Task 还称 AC4 以外的 AC 均已关闭，但 AC1/AC3 当前复审状态仍是 `PARTIAL`。这些说法只有在“Task AC 已满足”和“上游 P09 Gate 仍受限”分别表示不同范围时才能并存，现有文字没有标清这层区别。[Task](<G:/CODEX/New Manga/doc/tasks/P09-AC3-DELETE-HARDEN-1.md:84>) [正式 Handoff](<G:/CODEX/New Manga/doc/handoffs/P09-AC3-DELETE-HARDEN-1-1878f0b1.md:41>) [Closeout](<G:/CODEX/New Manga/doc/tasks/P09-AC3-DELETE-HARDEN-1.md:139>)

2. **Task 留有过期的“下一步”。** F-001 区块称该裁决记录“仍然生效；非历史叙事”，但其中的“下一步”仍是送 R2；当前 Review 指针已到 R13。若这是历史计划，应标注为历史并移入 history；若是当前指令，就与现有指针冲突。[Task](<G:/CODEX/New Manga/doc/tasks/P09-AC3-DELETE-HARDEN-1.md:99>) [Task](<G:/CODEX/New Manga/doc/tasks/P09-AC3-DELETE-HARDEN-1.md:165>)

我读取了 Task、正式 Handoff、证据索引 `HANDOFF.md`、`review-history.md`、`codex-review-r1.md` 至 `codex-review-r13.md`、`STATUS.md`，并核对了 `REBASELINE_PLAN.md`、协作协议 §4–5.1 和 P09 的 AC3 状态。R1–R13 各自绑定不同 `reviewed_head`，按协议属于各轮历史审查，不能把不同轮次的结论当成同一时点的冲突。

## Route B 能否关闭

**否。** Route B 的 AC4 转出方向明确，但当前 AC 状态口径仍未对齐，Task 还留有过期的下一步文字。P09 AC3 delete 子条件仍为 **`BLOCKED`**，我核对了 `STATUS.md` 和 P09 Task；本轮没有改变它。

验证通过：指定 probe 的注入触发，结果为 `ImmutablePathViolation`，外部文件存活（`SAFE`）；`python -m pytest tests/storage -q` 为 **86 passed**。

## 剩余状态副本与漂移风险

split 确实移除了证据索引中的 `status / owner / reviewer / head` 字段，但**没有消除重复状态这个根因**：

| 状态 | 仍有的副本 | 能否漂移 |
|---|---|---|
| `in_review` | 原四份相关文档中剩 3 份：Task、正式 Handoff、`STATUS`；`REBASELINE_PLAN` 还重复一份 | 能。Handoff 的 `status` 没标明是交付时快照 |
| `delivery_head` | Task frontmatter、Task Closeout、正式 Handoff，共 3 处 | 能，需分别维护 |
| AC4 `FAIL` / 转出与 P09 `BLOCKED` | Task、正式 Handoff、证据索引、`STATUS` 都重述相关状态 | 能；AC 状态冲突已见上文 |
| 当前 Review 指针 | Task 正文及 Closeout 重复 R13 指针；R13 报告保存对应审查记录 | 能，Task 内两处指针可不同步 |

所以 split **减少了一份显式生命周期状态副本，也缩短了 Task；但只缓解了症状，没有建立单一的当前状态来源**。

## 收敛情况

有局部进展：证据索引已明确自己不是交付件，AC1/AC3 的历史测试结果也标出了当前 `PARTIAL`。但 R8–R13 的数量 `4 → 2 → 4 → 1 → 2 → 3` 不单调下降，R14 仍有 2 个 findings。我的判断是：**个别表述在改善，整体尚未收敛；反复出现的底层问题仍是当前状态在多个文档中手工复制，历史内容也会留在当前状态段落里。**

推荐下一步：保持 `in_review / changes_requested`，由 Owner `dsh` 统一 AC1/AC3/AC11 的状态口径，标明 Handoff 的状态时点，并把 R2“下一步”移为历史记录或明确标注其时点；随后提交新 head，再做 R15 复审。目标文件没有工作区改动；我没有修改仓库文件。