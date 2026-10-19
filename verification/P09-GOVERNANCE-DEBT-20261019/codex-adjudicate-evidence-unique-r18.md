# Codex 裁定：GOV-EVIDENCE-UNIQUE-1 两个前提问题

- 裁定日期：2026-10-20
- 对象：`GOV-EVIDENCE-UNIQUE-1`，冻结 head `3c9ee0877`
- 本文件是本轮唯一新增文件；不改变任何来源 Task、Task 状态、AC 勾选、Canonical Evidence、pin 或历史结论。

## 一、Task 状态与 AC 全未勾选

### 裁定

1. `EXPORT-REVEAL-1` 和 `P15` 继续按各自 `status: done` 及 GOV-EVIDENCE-UNIQUE-1 已冻结的释放定义处理：两者的 13 个 AC 都属于本次核验的“已释放 AC”。冻结定义明确以来源 Task 的终态决定是否纳入；不能在本只读核验中另创“全部勾选才算释放”的口径。
2. 现有事实不足以据此重判两个来源 Task 的 `done`。空白 checklist 是明显的 Task 记录不一致，但不单独证明 AC 未满足。两份 Task 都有逐项测试/交付记录、Canonical Evidence 与 closeout 记录；`EXPORT-REVEAL-1` 明确保留真实 GUI 往返的 `BLOCKED` 限制，`P15` 明确声明 GUI e2e `NOT_RUN`。这些状态与 Task 对限制的如实披露相符，不能把“未运行 GUI”误读为未披露或通过。
3. 本 Task 不得代替来源 Owner 勾选 13 项，也不对它们作未经逐项审查的 PASS 认定。AC2 结果继续以 frozen rule 按 `status` 纳入；同时在结果和 limitation 中单列“done / 0 勾选”异常。若需修正来源 Task 的 checklist，由来源 Owner 按逐项证据回填 AC 结果，再由 Codex 复核；此为单独的来源文档维护，不是本 Task 的授权范围。来源 Owner 分别为 `EXPORT-REVEAL-1` 的 Codex、`P15` 的 ZCode。

### 对 GOV-DEBT-CLEANUP-2 的影响

不影响其已终结的 `closed_with_limitations` 判定。其 AC7 文件明确记载 61 项均只是候选、未逐项做唯一性核验、未登记任何证据；独立 Review 也确认 AC7 未达成且不得勾选。当前发现补充了来源状态记录异常，但没有推翻这些事实，也不能把 GOV-DEBT-CLEANUP-2 AC7 追溯改为通过或重开已关闭 Task。GOV-EVIDENCE-UNIQUE-1 后续形成的覆盖核验属于承接工作，不自动改变前一 Task 的终态或历史 AC。

依据：`verification/GOV-EVIDENCE-UNIQUE-1/ac1-input-freeze-and-criteria.md` §五；`doc/09_COLLABORATION.md` §4、§4.1；两来源 Task 的 AC、测试记录与 Closeout Record；`verification/GOV-DEBT-CLEANUP-2/ac7-evidence-dir-files.md`；`doc/reviews/GOV-DEBT-CLEANUP-2-94c8dcdab-antigravity-r2.md`。

## 二、目标应改为 AC 证据覆盖核验

### 裁定与授权

“唯一最终证据”不适合作为本 Task 的主要判定目标。证据可由日志、退出码、环境记录、交付说明等组成；一次 AC 也可能依赖多个测试面，候选集还包含不同尝试。唯一性不能推出充分性，单文件判定会把证据的组合结构压扁，也会把“没有一份文件独自证明 AC”误写成证据缺失。

**我明确授权把 GOV-EVIDENCE-UNIQUE-1 的目标改写为“AC 证据覆盖率核验”，并授权 Codex 在该 Task 内管理对五条 AC 的必要改写。**恢复执行前，Codex 应先把修订后的目标、AC、判定枚举及范围写入 Task，并按治理流程记录修订 head / 授权；当前 Owner 不得自行编辑已冻结 AC。此次裁定文件本身不修改 Task 或现有证据矩阵，原 61 项冻结输入与 8 份既有证据保持只读。

修订 AC 时遵循以下边界：

- **AC1**：对冻结的 61 项逐项记录路径、内容 Hash、存在性、内容类型、可能关联的来源 Task/AC、在证据组中的作用及限制；不能按文件名推断证明力。
- **AC2**：以每个已释放 AC 为单位，核实其 Canonical Evidence 与本次冻结候选的覆盖关系；允许一项 AC 对应多份互补证据，也允许一份证据支持多个 AC。分别标明证据集合及角色、是否充分、实际缺口和不确定性。不得把“存在候选”当成“AC 已满足”。
- **AC3**：保留现有只读保护，不改来源 Task、Review、Canonical Evidence/pin、61 项源文件或生产文件；本 Task 不补登记来源 pin、不处置文件。
- **AC4**：保留可复核交付、来源 commit/hash、Review 与 limitation 要求，但按 AC 覆盖结果报告，而不是要求每个 AC 恰有一份根证据。
- **AC5**：保留生命周期、Resource Manifest、集成字段及治理检查要求；任何 `BLOCKED`、`NOT_RUN`、`UNKNOWN` 均不得记为通过。

建议统一使用以下**结果枚举**：`COVERED`（证据组充分支持 AC 达成）、`PARTIAL`（有相关证据但 AC 要求未被完整覆盖）、`EVIDENCE_GAP`（候选范围内没有相关证据）、`UNKNOWN` / `BLOCKED`（材料缺失、不可访问或无法判断）、`NOT_RELEASED`、`NOT_APPLICABLE`。`COMPOSITE` 可保留为证据形态标签，描述“需多项材料共同覆盖”，不能作为充分性结果，也不能替代上述枚举。

测试/构建的多次尝试应保留其时间和结果关系；报告哪次是最终判定所依赖的结果，以及失败尝试是否被后续有效运行取代。命令、环境、日志、退出码等作为一组关联材料核验。若 AC 明确要求原始日志与退出码，只有日志而无可复核退出码时应记录为 `PARTIAL` 或 `UNKNOWN`，不能按文件数判为覆盖。

## 三、后续执行口径

GOV-EVIDENCE-UNIQUE-1 在 Codex 完成上述 Task/AC 修订前保持暂停于当前核验边界，不得将已有 `YES 1 / NO 5 / UNKNOWN 55` 的文件级矩阵包装为 AC 覆盖结论。修订后由现 Owner `dsh` 在原只读约束内继续逐项工作；Reviewer 仍按 Task 记录的独立审查安排执行。两份来源 Task 的 AC 勾选异常作为 limitation 保留，按 status 纳入覆盖矩阵，不因本次裁定自动勾选或重判状态。

## 四、工作区状态记录

按要求记录动手前后 `git status --porcelain` 摘要。工作区在写入前已存在大量由其他工作留下的修改与未跟踪项；未改动或清理这些内容。

| 时点 | porcelain 条目数 | 条目内容 SHA-256 | 目标文件 |
|---|---:|---|---|
| 写入前 | 1237 | `5d38f7479a2e55b24ddebb282bce3a47a144d3607679f5d22ee1f47bebd92bfc` | 不存在 |
| 写入后 | 1238 | `a32146956167dcaba94125815529af7602d3c4a34f4556a34cc496afb1eff5ee` | `?? verification/P09-GOVERNANCE-DEBT-20261019/codex-adjudicate-evidence-unique-r18.md` |

SHA-256 对 `git status --porcelain` 的完整输出按 UTF-8 编码并以 LF 连接后计算。写入后应仅比写入前多出本文件这一条状态记录；其他既存条目必须保持不变。