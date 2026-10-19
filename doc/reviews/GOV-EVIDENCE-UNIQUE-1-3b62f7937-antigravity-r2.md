---
task_id: GOV-EVIDENCE-UNIQUE-1
reviewer: Antigravity
reviewed_head: 3b62f7937
verdict: CHANGES_REQUESTED
revision: 2
conversation_id: e52e71f2-db82-468d-ac30-fb95e0291f35
note: 复核第一轮修正，发现 4 处残留未清理 + Task 缺 Canonical Evidence 表；交付方已二次修正
---
# Task GOV-EVIDENCE-UNIQUE-1 审阅复核报告

- **复核对象**：[Task GOV-EVIDENCE-UNIQUE-1](file:///G:/CODEX/New%20Manga/doc/tasks/GOV-EVIDENCE-UNIQUE-1.md)
- **最新 Commit**：`c41a40a09`（*governance(GOV-EVIDENCE-UNIQUE-1): downgrade P15-HOST-2 AC5 per review - COVERED was 3 not 4*）
- **复核模式**：只读复核（未修改任何文件，未执行任何 Git 写命令）

---

## 一、四项复核逐条意见

### 1. 降级是否执行到位
- **判定行修正**：**已修改**。在 [ac2-coverage-batch3-and-summary.md](file:///G:/CODEX/New%20Manga/verification/GOV-EVIDENCE-UNIQUE-1/ac2-coverage-batch3-and-summary.md) 第 63 行，`P15-HOST-2` AC5 的判定已明确变更为 `PARTIAL（经 Review 修正）`。
- **汇总表自洽性**：**自洽**。13 个 Task 的分项汇总中，`P15-HOST-2` 列由 `(1, 1, 3, 1)` 调整为 `(0, 2, 3, 1)`。全量合计列相加：
  - `COVERED`: $1 + 1 + 1 = 3$ 项
  - `PARTIAL`: $2+1+3+0+3+1+0+0+1+2+0+1+3 = 17$ 项
  - `EVIDENCE_GAP`: $19$ 项；`NOT_APPLICABLE`: $42$ 项；总计 $83$ 项。
- **百分比吻合度**：**相符**。`COVERED`: $3 / 83 \approx 3.6\%$；`PARTIAL`: $17 / 83 \approx 20.5\%$。
- **全文残留排查**：⚠️ **发现多处未清理干净的旧表述残留**：
  1. **第 180–186 行**：标题虽改为“只有 3 个 AC 达到 `COVERED`”，但下方表格**第 185 行仍赫然保留着**：`| P15-HOST-2 AC5 | 三次 vitest 递进 + core 508 passed，最终依据可辨识 |`，表格实际仍为 4 行。
  2. **第 201 行**：仍写着 `19 vs 16。缺口比不完整更多。`，未同步更新为 `19 vs 17`。
  3. **第 215 行**：完成度声明中仍保留 `| 四个 COVERED 逐个给出理由 | 完成 |`。
  4. **第 223–225 行**：局限声明第 2 条完整保留了初版的陈述：*“P15-HOST-2 AC5 判 COVERED 是我的判断（AC5 未要求退出码）……这个判断需要 Review 复核。”*，未同步标注已被 Review 改判。

---

### 2. Handoff 是否同步，且是否与证据一致
- **数字同步**：[GOV-EVIDENCE-UNIQUE-1-3b62f7937.md](file:///G:/CODEX/New%20Manga/doc/handoffs/GOV-EVIDENCE-UNIQUE-1-3b62f7937.md) 第 53–54 行的表格数字已同步为 `COVERED 3 / 3.6%`、`PARTIAL 17 / 20.5%`。
- **一致性与残留**：⚠️ **Handoff 存在明显的局部修改残留**：
  1. **第 67 行**：在“只有 3 个 AC 达到 COVERED”的标题下，表格第 67 行**仍未删除** `| P15-HOST-2 | AC5 | ... |`，表格内仍有 4 项。
  2. **第 78 行**：小节标题仍为 `### 3. EVIDENCE_GAP（19）多于 PARTIAL（16）`，数字未更新。
  3. **第 85–93 行**：虽然标题被机械替换为“我的三个 COVERED 判断”，但下方正文第 87–93 行**依然原封不动地保留了此前为 P15-HOST-2 AC5 判 COVERED 辩护的整段话**（*“特别是 P15-HOST-2 AC5。我判 COVERED 的理由是……”*），未作对应清理。

---

### 3. 交付方是否留下了意见记录，而不是静默改写
- **结论**：**记录完整、准确，绝非静默改写**。
- **核验事实**：
  - 在 [ac2-coverage-batch3-and-summary.md](file:///G:/CODEX/New%20Manga/verification/GOV-EVIDENCE-UNIQUE-1/ac2-coverage-batch3-and-summary.md) 第 66–87 行专门新增了「修正说明（2026-10-20，经 Antigravity Review）」章节。
  - 完整载入了两条核心反驳意见：① 退出码属于双重标准；② 仅凭前端 vitest 递进与 core 全量摘要无法反推反例业务细节。
  - 交付方在 commit `c41a40a09` 的 commit message 中如实剖析了原因，并将完整的 Review 报告落盘归档为 [doc/reviews/GOV-EVIDENCE-UNIQUE-1-3b62f7937-antigravity-r1.md](file:///G:/CODEX/New%20Manga/doc/reviews/GOV-EVIDENCE-UNIQUE-1-3b62f7937-antigravity-r1.md)，改写过程具备完整的审计留痕。

---

### 4. 修正后是否还有别的 AC 判定需要同样检讨（独立审查意见）
逐一核验其余三个保留的 `COVERED` 以及相关 `PARTIAL` 样本，确认**是否存在同类错误（用测试量/文件存在推断覆盖，而非核对 AC 具体要求）**：

1. **`P15-CORE-1C` AC6**：
   - **核验**：AC6 要求对替身反例与完整回归执行并归档证据；候选文件 `pytest-core-focused.*` 正是针对该 Task 的 100 个专项反例与阶段测试套件，五件套（命令、环境、退出码 0、日志 100 passed、12 个制品 SHA-256 核验）完全闭合，且声明了“不声称真实网络连通性”。
   - **结论**：**成立，不存在同类推断错误**。
2. **`P19-UI-FIX-1` AC1**：
   - **核验**：AC1 要求 9 个分类按钮在 UIA 中表现为 `IsEnabled=False`、`IsOffscreen=False`、`Invoke blocked`。候选文件 `04-settings-uia-pass-exit-code-blank.txt` 逐行准确记录了这 9 个按钮的可观测状态，直接对应 AC 要求。
   - **结论**：**成立，不存在同类推断错误**。
3. **`FEAT-CREATE-4` AC1**：
   - **核验**：AC1 要求空书架下 `+ 新建作品` 可用、可输入创建、提交后书架出现作品。候选文件 `gui-uia-command-r5.log` 完整记录了每一步自动化动作及 `EMPTY_SHELF_CREATE_BOOK=PASS`、`CREATE_BOOK=PASS returned_book_visible=true` 与 `exit_code=0`。
   - **结论**：**成立，不存在同类推断错误**。
4. **其余 PARTIAL 抽查**：
   - `HOST-TTL-BOUNDARY-1` AC6、`P19-UI-FIX-2` AC3/AC4 等，均因缺少全套套件日志、退出码或一致性校验而被严格定为 `PARTIAL`，未见宽松放行。

**独立审查结论**：**其余三个 COVERED 经核对完全成立，未发现同类推断错误。**

---

## 二、治理检查实测

执行治理检查命令：
```powershell
pwsh -NoProfile -File tools/governance/check.ps1
# 结果：PASS (1 warnings: doc/STATUS.md 达到预算 80%)

pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/GOV-EVIDENCE-UNIQUE-1.md
# 结果：FAIL (1 errors, 2 warnings)
# 报错详情：
# WARN: doc/STATUS.md 已达到预算的 80%：3139 bytes / 30 lines
# WARN: evidence_dir 含未登记过程文件（归入 workspace 或列为 SOURCE_PIN）：...
# FAIL: 进入 REVIEW/DONE 的 lifecycle v2 Task 必须列出 canonical evidence。
```
- **检查结论**：Task 自身依然处于 **FAIL** 状态。Task 文件处于 `status: in_review`，但其 `## Canonical Evidence` 章节下仍未补齐 6 列证据登记表格。

---

## 三、问题分级与总体结论

### 问题分级
- **P1（治理检查阻断）**：[doc/tasks/GOV-EVIDENCE-UNIQUE-1.md](file:///G:/CODEX/New%20Manga/doc/tasks/GOV-EVIDENCE-UNIQUE-1.md) 未登记 `## Canonical Evidence` 表格，导致 `check.ps1 -TaskPath` 依然为 **FAIL**。
- **P2（文本清理不彻底）**：
  1. `ac2-coverage-batch3-and-summary.md` 行 185 与 Handoff 行 67 的列表表格中仍残留了 `P15-HOST-2 AC5` 这一行；
  2. Handoff 行 85–93 仍残留此前为 `P15-HOST-2 AC5` 辩护的正文陈述；
  3. 部分说明文字仍残留 `PARTIAL（16）` 或 `四个 COVERED`。

### 总体结论
**核心判定与逻辑改写已完全合规并闭环，但由于存在 P1 级治理检查未通过及 P2 级文本残留，暂不宜直接 closeout**。
建议由 Codex 在执行 Closeout 前统一执行小幅收口清洗。

---

## 推荐下一步

根据协作协议 §5.1，推荐交由 **Codex** 执行最终收口与关单：

```text
Recipient: Codex
Instruction:
对 Task GOV-EVIDENCE-UNIQUE-1 执行 Closeout 前的收口处理：
1. 清理文本残留：在 verification/GOV-EVIDENCE-UNIQUE-1/ac2-coverage-batch3-and-summary.md 和 doc/handoffs/GOV-EVIDENCE-UNIQUE-1-3b62f7937.md 中，删去表格中仍残留的 P15-HOST-2 AC5 行，并清理 Handoff 中过时的辩护文字与旧统计数；
2. 修复治理阻断：在 doc/tasks/GOV-EVIDENCE-UNIQUE-1.md 中补齐 ## Canonical Evidence 表格并更新元数据，确保 `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/GOV-EVIDENCE-UNIQUE-1.md` 达到 PASS；
3. 完成 Task 生命周期与 REBASELINE_PLAN / STATUS 状态关闭。
```
