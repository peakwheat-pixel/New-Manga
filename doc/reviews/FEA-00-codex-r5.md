---
document_id: FEA-00-codex-r5
kind: independent_review
reviewer: Codex
reviewer_kind: agent
reviewer_source: "Codex 独立复审会话 /root，2026-10-31"
base_commit: 504797ba71766f07d452cc6ddc276e01e5c2e888
reviewed_head: 1672f3c405ab8d420fa7c8854a565d212d1b0649
decision: changes_requested
---

# 结论

**`changes_requested`。** 三条指定验证和 13 场景矩阵均通过；独立构造的 CommonMark 边界样本仍复现两种误报，以及一个可让 code span 内的 sentinel 被接受的 HTML 交互问题。§4.4 的事前副本也不对应本次固定 base。

`git show --stat` 确认 commit 仅改两个指定文件，共 **229 insertions、15 deletions**。

## 固定指纹

| 对象 | SHA-256 |
|---|---|
| `check.ps1`（parent blob） | `13e08555e4d7f107623f1daaea325bb8c8f776fb88e75b2ec9b87e2e25bde5f5` |
| `test_architecture_assertions.py`（parent blob） | `4d639ba7bc15327ede458709ccb5810987749303f85cc622742b7a9187a63601` |
| `checker-before-r5.ps1` | `04d9373e4e9f4700eb35d12bcef75440de24042973c611bf2b2a5eefc62faf3e` |
| `test-before-r5.py` | `b4c26ba05c38bb7c1dd2603ea890411a10f6eafa03613020b8104a2f7c399d48` |
| 当前 `tools/governance/check.ps1` | `ab2cc3abd4595843e55288d72a5da9b3a70706f84e70c753d9d3971027c48cf9` |
| 当前 `test_architecture_assertions.py` | `16b1e9c5497dbafa70beebd3723d84fd5059e09a87ad86a590d2edc5a82027f2` |
| `pre-change-scope.md` | `5c09e253b35979b5a11cfe8cb85bd17c32d79c2a5fa57fcba60977bdcb10456a` |
| `baseline-matrix-before.log` | `89caca7edac92c380379f428012a0704eec831a8c394f4a70a89a1c02f3cc4af` |
| `final-matrix.log` | `0bbdfffa01c4cc40d8de55e3551001ea8dca0f50ea5c1cce7fb7d495dcb29e1b` |
| `r5-verification.md` | `c44d22e50e68f61ba67af56ad5b73b1d4969cddef2967e840a7505d2d6597f5e` |
| `r5_matrix.py` | `c32aed6dba7eb80313104501fc3851159119699ab2e93c00fe01d380ab97dc1f` |

## §4.4 核验

事前范围、两份矩阵日志和 r5 验证记录的哈希与记录中的值一致。旧矩阵记录 **13 场景、3 mismatch**；新矩阵记录 **13 场景、0 mismatch**。

但 `checker-before-r5.ps1` 和 `test-before-r5.py` 均与 parent blob **字节不一致，LF 归一后也不一致**。修复前检查器副本已含 `Hide-InlineCode`、`Hide-NonLinkContexts` 和 HTML code 状态处理；测试副本也包含同行、图片和 HTML 用例。因此该矩阵证明的是在这份较新副本上加入跨行修复的效果，不能代表被审 commit 相对 parent 的完整基线。

受影响集合核对结果：parent 的 `$staticFiles` 为 **14**，commit 后仍为 **14**；checker 实际报告 scope **15**。所以 `pre-change-scope.md:9` 所述“HEAD `504797ba7` 为 12 项、增至 14 项”不适用于本次固定 base。

## Standards

未发现书面标准违规或值得报告的 Fowler smell。Standards 轴审查结果：**0 findings**。

## Spec

发现 **1 条 P1、3 条 P2**：

1. **P1 — `tools/governance/check.ps1:415`：HTML 处理可使 code span 内 sentinel 被接受。**  
   用跨行双反引号包住替换后的 AD-003 sentinel，并在同一段落插入行内 `<pre>` 与其闭合标签。CommonMark 下这段仍是 code span 内容；但 `Get-AuthorityLines` 先按行识别 `<pre>`、隐藏中间行并切断段落，之后跨行 span 扫描无法配对。实测 checker 错误 **PASS / EXIT=0**。建议在按 HTML 标签处理前先按原始段落识别并屏蔽跨行 code span，并增加此组合负例。

2. **P2 — `tools/governance/check.ps1:349`：未识别转义反引号。**  
   在 AD-003 sentinel 前同段插入 `历史说明：\`literal`，然后保留有效 sentinel。CommonMark 中被反斜杠转义的反引号不是 code span opener；当前扫描器仍把它与 sentinel 值中的反引号配对，屏蔽 marker。隔离夹具实测预期 PASS、实际 **REJECT / EXIT=1**。建议按前置反斜杠奇偶识别转义，并覆盖正反例。

3. **P2 — `tools/governance/check.ps1:440`：段落切分只识别空行。**  
   在 sentinel 前插入未闭合反引号说明行，再插入无空行的 ATX 标题 `## 独立标题`，然后保留有效 sentinel。标题是 CommonMark 块边界，前一段的反引号不能跨标题配对；当前实现跨标题屏蔽 sentinel。隔离夹具实测预期 PASS、实际 **REJECT / EXIT=1**。建议识别相关块边界并增加正例。

4. **P2 — `G:\CODEX\New Manga.workspace\agent-output\dsh\FEA-00-R2-fix2\pre-change-scope.md:9`：基线与固定 base 不一致。**  
   该文件把 parent 描述为 12 个 static files，但 parent 实测为 14；修复前副本也不是 parent 快照。当前证据不足以说明整个 commit 相对 parent 的变化均由矩阵覆盖。建议将基线绑定到 parent，或明确记录矩阵只验证跨行增量并解释其余改动来源。

### 逐项复核

简单等长反引号串配对、只屏蔽跨行 span、保留同行 span 与换行的逻辑符合预期；CRLF 文档独立样本通过。fence、HTML 注释、独立 `<pre>/<code>`、同行 code、真实链接和跨行非权威正文场景均通过已有测试或矩阵。自由正文边界 R-04 未见扩大；跨行 code span 包裹首句链接、图片语法及 AD-002/AD-003 sentinel 的指定负例均被拒绝。HTML 与跨行 span 的组合仍有上述 P1 漏报。

## 验证命令与实际结果

| 命令 | 结果 |
|---|---|
| `pwsh -NoProfile -File tools/governance/check.ps1` | **EXIT=0**；`PASS (2 warnings)`；scope 15。warning 为 7 个非终态 Task，以及 `REBASELINE_PLAN.md` 6624 bytes / 58 lines。 |
| `python -B -m unittest discover -s tools/governance/tests -p test_architecture_assertions.py -v` | **EXIT=0**；16 tests，`OK`。 |
| `python -B -W ignore "G:/CODEX/New Manga.workspace/agent-output/dsh/FEA-00-R2-fix2/r5_matrix.py"` | **EXIT=0**；13 scenarios，0 mismatches。 |

自建隔离样本：CRLF authority 文档预期/实际 PASS；转义反引号与标题边界样本均为预期 PASS、实际 REJECT；跨行双反引号加行内 `<pre>` 的 sentinel 样本预期 REJECT、实际 PASS。夹具位于允许的 workspace 路径并已清理。

## 残余风险与 NOT_RUN

本次没有运行完整 CommonMark 规范测试套件；fence、注释、HTML 与其他 Markdown 块结构的更多组合仍未覆盖。产品功能与 DSH 集成验证不属于本次复审。

本次只读，未修改仓库文件。最后运行 `git status --porcelain`，结果仅有以下 7 个既有 untracked 文件，没有已修改的跟踪文件：

```text
?? doc/design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md
?? doc/design/FLUENT_MANGA_USER_CONCEPT_2026-10-30.md
?? doc/handoffs/FEA-00-codex-r2-remediation.md
?? doc/reviews/FEA-00-codex-r2.md
?? doc/reviews/FEA-00-codex-r3.md
?? doc/reviews/FEA-00-codex-r4-appointment.md
?? doc/reviews/FEA-00-codex-r4.md
```

本报告不代替 DSH Appointment 登记、集成验证或实现授权。建议 DSH 先处置上述 findings 并校正基线证据，再对修复后的固定 commit 安排独立复审。