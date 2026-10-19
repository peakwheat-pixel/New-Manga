---
task_id: GOV-DEBT-CLEANUP-2
reviewer: Antigravity
reviewed_head: 94c8dcdab
verdict: APPROVED_WITH_LIMITATIONS
revision: 2
conversation_id: 26a45b93-05e5-4f67-b1f4-a36c70fad5fb
note: 本 Review 抓出交付方一次错误的「更正」；交付方已撤销并记录（见 009d009e4）
---
针对 Task [`GOV-DEBT-CLEANUP-2`](file:///G:/CODEX/New%20Manga/doc/tasks/GOV-DEBT-CLEANUP-2.md)（固定 HEAD: `94c8dcdab`）的只读 Review 现已完成。以下为五项核对点的独立核验结果、总体结论与问题分级。

---

### 一、逐条五点核对

#### 1. AC 勾选状态是否诚实

- **核对结果**：
  - 查验 [`doc/tasks/GOV-DEBT-CLEANUP-2.md`](file:///G:/CODEX/New%20Manga/doc/tasks/GOV-DEBT-CLEANUP-2.md) 第 50–58 行：
    - `[x] AC1`、`[x] AC2`、`[x] AC3`、`[x] AC4`、`[x] AC5`、`[x] AC6`、`[x] AC8` 已勾选。
    - `[ ] AC7` 与 `[ ] AC9` 未勾选。
  - 与第 139–154 行的自审表格（AC7 记为“未达成（部分）”，AC9 记为“进行中”）完全一致。
- **AC7 未勾选是否恰当**：
  - **完全恰当，诚实反映了交付边界，绝不能勾选。**
  - AC7 原文严格要求：“对 61 项逐文件记录路径、候选分类、内容/AC 绑定核查、**是否唯一最终证据及处理结论**。只有证实文件是已释放 AC 的唯一最终证据时才可列入对应 Canonical Evidence”。
  - 证据文件 [`verification/GOV-DEBT-CLEANUP-2/ac7-evidence-dir-files.md`](file:///G:/CODEX/New%20Manga/verification/GOV-DEBT-CLEANUP-2/ac7-evidence-dir-files.md) 第 7–9 行明确声明：“*判定『唯一最终证据』需要逐文件阅读内容并对照 AC 原文，**本文件没有做这件事**。因此下列 61 项**全部保持候选分类**，没有任何一项被登记进 Canonical Evidence*”，且表格中全部 61 项的“唯一最终证据”一律填为“未验证”。
  - 交付方没有虚标通过，如实保留了 `[ ]`，符合诚实边界。

---

#### 2. AC1 与 AC4 的两处更正是否正确，以及是否还有第三处未发现

##### (1) AC1 统计核验（重大发现：交付方更正失误）
- **核验对象**：[`verification/GOV-DEBT-CLEANUP-2/ac1-sha-rows.md`](file:///G:/CODEX/New%20Manga/verification/GOV-DEBT-CLEANUP-2/ac1-sha-rows.md)
- **交付方声称**：早期记录 102 行（78/13/11），实测 105 行（79/14/12）。
- **独立实测结果**：**实际表格数据行自始至终就是 102 行（78 / 13 / 11）！早期记录是完全正确的，交付方的“更正”是一次统计乌龙（False Correction）！**
- **复现与证据**：
  - 逐行数据表区域（行 18 `## 逐行` 至行 262 `## 明确未做的事` 之间）内所有带行号的数据行：
    - `KEEP_HISTORIC_PIN`：**78 行**
    - `BLOCKED_ORIGIN_UNVERIFIED`：**13 行**
    - `BLOCKED_PRESERVE_DIRTY`：**11 行**
    - 合计：**102 行**（与来源事实 [`sha-mismatch-evidence-chain.md`](file:///G:/CODEX/New%20Manga/verification/P09-GOVERNANCE-DEBT-20261019/sha-mismatch-evidence-chain.md) 的 102 行数据完全一致）。
  - **交付方为什么会算出 105？**
    查验 `ac1-sha-rows.md` 第 284 行交付方自述的统计方法：“*对所有以 `|` 开头且含 `KEEP_HISTORIC_PIN` / `BLOCKED_*` 的行计数*”。
    该文件第 14–16 行存在一个说明表格：
    ```markdown
    | `KEEP_HISTORIC_PIN` | 78 | pin 在其 commit 上准确...
    | `BLOCKED_ORIGIN_UNVERIFIED` | 13 | pin 在其 commit 上即不符...
    | `BLOCKED_PRESERVE_DIRTY` | 11 | pin 不符且工作区有未提交修改...
    ```
    交付方的统计脚本使用了粗糙的正则匹配，**把这 3 行说明表头也当作数据行统计进去了**，导致每一类处置恰好多算了 1 行（78+1=79，13+1=14，11+1=12），合计 102+3=105！

##### (2) AC4 统计核验
- **核验对象**：[`doc/tasks/P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION.md`](file:///G:/CODEX/New%20Manga/doc/tasks/P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION.md) 与 [`verification/GOV-DEBT-CLEANUP-2/ac4-p02-ac3-pins.md`](file:///G:/CODEX/New%20Manga/verification/GOV-DEBT-CLEANUP-2/ac4-p02-ac3-pins.md)
- **交付方声称**：早期记录 23 条（18 存在 / 5 缺失），实测 25 条（21 存在 / 4 缺失），且 `doc/handoffs/P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION-R1.md` 存在。
- **独立实测结果**：**完全正确。**
  - 使用 `git cat-file -e 0af8980884e9d027042ef145cd966577d86b5bc5:<path>` 逐条执行：
    - 存在：**21 条**（包含被误记为缺失的 `doc/handoffs/P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION-R1.md`，exit code 为 0）。
    - 缺失：**4 条**（4 条均为 `verification/P02-NEW-TIME-BASELINE/` 下的父任务引用，exit code 非 0）。
    - 合计：**25 条**。

##### (3) 其他 AC 抽查
- **AC2（声称 29 项）**：[`ac2-deferred-tasks.md`](file:///G:/CODEX/New%20Manga/verification/GOV-DEBT-CLEANUP-2/ac2-deferred-tasks.md) 中数据行编号精确为 1 至 29，**实测 29 项**。
- **AC5（声称 13 项）**：[`ac5-worktree-preserve-list.md`](file:///G:/CODEX/New%20Manga/verification/GOV-DEBT-CLEANUP-2/ac5-worktree-preserve-list.md) 中数据行编号精确为 1 至 13，**实测 13 项**。
- **AC7（声称 61 项）**：[`ac7-evidence-dir-files.md`](file:///G:/CODEX/New%20Manga/verification/GOV-DEBT-CLEANUP-2/ac7-evidence-dir-files.md) 剔除各组表头后，实际文件项为 A 候选 10 项 + B 候选 49 项 + C 候选 2 项，**实测 61 项**。
- **AC8（声称 69 项）**：[`ac8-open-acs.md`](file:///G:/CODEX/New%20Manga/verification/GOV-DEBT-CLEANUP-2/ac8-open-acs.md) 汇总表格涵盖 69 个 Task，正文 `### ` 小节精确为 69 个，共记录 373 条未勾选 AC，**实测 69 项**。

##### (4) 是否有第三处未发现
经深入比对，发现另外两处隐藏问题：
1. **隐藏点 A（AC7 行数笔误）**：[`doc/tasks/GOV-DEBT-CLEANUP-2.md`](file:///G:/CODEX/New%20Manga/doc/tasks/GOV-DEBT-CLEANUP-2.md) 第 151 行自审表格中写有“分类完成（65 行）”，但实际文件条目数和汇总数均为 61 项，该“65 行”系包含了辅助行统计不严谨的小偏差。
2. **隐藏点 B（P02 AC3 任务文件本身的历史格式破损）**：在 [`doc/tasks/P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION.md`](file:///G:/CODEX/New%20Manga/doc/tasks/P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION.md) 的 Canonical Evidence 表第 100 行，存在一条格式破损记录：`1verification/P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION/zcode-owner-selftest-1.meta.json| ...`，首列缺少 `| evidence_id | AC/Gate |`。交付方仅提取了 25 条标准表格行，未将该破损行纳入统计（若修复格式实际为 26 条）。这属于历史遗留文本坏损，本次只读核验不修改原文件。

---

#### 3. `closed_with_limitations` 是否是恰当终态

- **协作协议条件依据（[`doc/09_COLLABORATION.md`](file:///G:/CODEX/New%20Manga/doc/09_COLLABORATION.md) §4 / §4.2）**：
  - `done`：要求“所有已释放 AC 通过，须有逐项 AC 达成证据”，且完成集成验证与资源核销。
  - `closed_with_limitations`：终态但不等于技术完成；用于用户明确裁决或受限关闭；“记录替代依据、closure evidence、未完成 AC/Finding 原始状态及分类，不得改写为 PASS；除新授权外不恢复实施”。
- **裁决结论**：**`closed_with_limitations` 是唯一恰当终态，绝不应记为 `done`，也不应退回打回。**
  - **为什么不能记 `done`**：AC7 明确未达成（未做逐项唯一最终证据核验），直接违反 `done` 准入门槛。
  - **为什么不应退回补齐 AC7**：AC7 要求对 61 个历史文件逐一阅读并对照已完成任务做唯一性裁决，属于极重的历史考古工作。当前 Task 的使命是固化只读事实、阻断盲目修改，61 个文件已被完整列入清单并安全保留在原位，未向主线引入伪造证据。将 AC7 作为未达成限制诚实记录，完全符合 `closed_with_limitations` 的定义。

---

#### 4. 「两处汇总错误」是否可以被接受为已处理（独立意见）

- **处理方式评估**：
  - 交付方坚持“**保留原数字、附显式更正表、不静默覆盖**”的证据学原则，在方法论上是值得肯定的，避免了破坏历史审计轨迹。
- **独立审查意见**：
  - **AC4 的更正完全有效**：确认为 25 项且修正了误记，处理充分。
  - **AC1 的“更正”是执行失误，但无需判定 Task 整体失败**：
    - 交付方在进行 AC1 更正时犯了教条主义错误——用不严谨的脚本把原本正确的 102 误判为 105，讽刺性地印证了其在第 167 行所写“*人工汇总产出证据，天然不可靠*”。
    - **但是，这不需要也不应该将 Task 判为失败打回**。因为 `ac1-sha-rows.md` 逐行数据表的核心价值在于 102 行 mismatch 的具体路径、commit、hash、不重钉的只读事实链是**真实无误**的；
    - 终态本身即为 `closed_with_limitations`。正确的处理路径是：**由 Reviewer 在 Review 记录中明确指出“AC1 数据行确为 102，交付方所谓 105 系统计脚本把说明表头误算进去导致的误修正”，作为 Limitation 随 closeout 一并归档，不要求交付方反复改写文件**。

---

#### 5. 治理状态检查

在当前工作区（HEAD: `94c8dcdab`）执行以下命令：

1. **Task 检查**：
   ```powershell
   pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/GOV-DEBT-CLEANUP-2.md
   ```
   **结果**：`Governance check: PASS (1 warnings)`（退出码 0）。
2. **全局治理检查**：
   ```powershell
   pwsh -NoProfile -File tools/governance/check.ps1
   ```
   **结果**：`Governance check: PASS (1 warnings)`（退出码 0）。

*(注：两项检查中的唯一 Warning 均为既有的 `doc/STATUS.md 已达到预算的 80%：3142 bytes / 27 lines`，无阻断性错误。)*

---

### 二、总体结论

**结论：建议通过评审（APPROVED_WITH_LIMITATIONS），可以进入 Codex closeout 阶段。**

- 本 Task 在固定 HEAD `94c8dcdab` 上满足进入 closeout 的全部前置条件：
  1. 治理检查全部 PASS；
  2. 10 份证据文件在原位安全固化，未触碰禁止路径，未执行物理删除或未授权移动；
  3. AC 状态反映诚实，交付方明确放弃了 `done`，自裁为 `closed_with_limitations`。
- 最终终态由 Codex 裁定为 **`closed_with_limitations`**。

---

### 三、问题分级

- **P0（阻断性缺陷）**：**0 项**。未发现破坏性操作、未发现伪造 PASS、未破坏治理检查器。
- **P1（重要缺陷，作为 Limitation 记入 Closeout Record）**：
  1. **AC1 存在反向虚假更正（False Correction）**：`ac1-sha-rows.md` 真实数据行为 102 行（78/13/11），交付方声称实测为 105 行系统计脚本误算了前文的 3 行说明表格所致。该事实必须在 Review 记录和 Closeout Record 中澄清，维持原始数据行的 102 事实。
  2. **AC7 记录行数笔误**：Task 主文件表述的“65 行”与实际文件条目“61 项”存在微小统计偏差。
- **P2（轻微观察/建议）**：
  1. `doc/tasks/P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION.md` 第 100 行存在历史文本破损，后续若有针对该 Task 的归档或清理再行单独处置。
  2. `doc/STATUS.md` 体量已接近预算（80%），Codex 在更新指针时应控制字数。

---

### 推荐下一步

**推荐下一步**：交由 **Codex** 进行最终集成与 Closeout 裁决。
- **可直接转发的指令**：
  > 请 Codex 审查并接管 Task `GOV-DEBT-CLEANUP-2` 的 closeout 流程：
  > 1. 参考 Antigravity 的独立 Review 结论（绑定 HEAD `94c8dcdab`）；
  > 2. 将 Task 终态确认为 `closed_with_limitations`（登记 AC7 未做唯一证据判定限制，并在 Closeout Record 中补充记录：AC1 真实数据行仍为 102 行，105 统计系交付方脚本误入表头）；
  > 3. 更新 `Resource Manifest` 与 `doc/STATUS.md`，完成该治理债务切片的归档。
