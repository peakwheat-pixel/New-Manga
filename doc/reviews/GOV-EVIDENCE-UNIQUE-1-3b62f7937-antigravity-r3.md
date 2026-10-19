---
task_id: GOV-EVIDENCE-UNIQUE-1
reviewer: Antigravity
reviewed_head: 3b62f7937
verdict: CHANGES_REQUESTED
revision: 3
conversation_id: e52e71f2-db82-468d-ac30-fb95e0291f35
note: 第三轮复核抓出 2 处表格残留；交付方按行精确删除并验证 TOTAL RESIDUAL = 0
---
# Task GOV-EVIDENCE-UNIQUE-1 审阅复核报告（第 3 轮）

- **复核对象**：[Task GOV-EVIDENCE-UNIQUE-1](file:///G:/CODEX/New%20Manga/doc/tasks/GOV-EVIDENCE-UNIQUE-1.md)
- **最新 Commit**：`0a9e809e2`（*governance(GOV-EVIDENCE-UNIQUE-1): finish the downgrade - my first fix was half-applied*）
- **复核模式**：只读复核（未修改任何文件，未执行任何 Git 写命令）

---

## 一、四项核对逐条结论

### 1. 四处残留是否清除：⚠️ 仅清除 2 处，核心表格仍残留 2 处

逐行检索文件实际内容，核实结果如下：

| 文件 | 检查项 | 实测状态 | 精确位置与现状说明 |
|---|---|---|---|
| `verification/GOV-EVIDENCE-UNIQUE-1/ac2-coverage-batch3-and-summary.md` | 表格中的 `P15-HOST-2 AC5` 行 | ❌ **未清除（残留）** | **第 185 行**：<br>`\| `P15-HOST-2` AC5 \| 三次 vitest 递进 + core 508 passed，最终依据可辨识 \|`<br>（标题已改为“只有 3 个”，但下方表格实际仍为 4 行） |
| 同上 | 局限声明中辩护且需复核的话 | ✅ **已清除并显式标注** | **第 223–226 行**已改为：<br>`2. ~~`P15-HOST-2` AC5 判 `COVERED`~~ —— **该判定已被 Review 推翻，现在为 `PARTIAL`**。……此局限已消解，但作为教训保留。` |
| `doc/handoffs/GOV-EVIDENCE-UNIQUE-1-3b62f7937.md` | 表格中的该行 | ❌ **未清除（残留）** | **第 67 行**：<br>`\| `P15-HOST-2` \| AC5 \| 三次 vitest 递进 + core 508 passed，最终依据可辨识 \|`<br>（标题已改为“只有 3 个”，但下方表格实际仍为 4 行） |
| 同上 | §1 下为 AC5 辩护的陈述 | ✅ **已改写** | **第 82–89 行**原辩护段落已删除，改写为客观说明：<br>`（原为四个，`P15-HOST-2` AC5 已因 Review 反馈降为 `PARTIAL`。）`，辩护词已消除。 |

> **补充发现的相关残留**：
> 1. [ac2-coverage-batch3-and-summary.md](file:///G:/CODEX/New%20Manga/verification/GOV-EVIDENCE-UNIQUE-1/ac2-coverage-batch3-and-summary.md) **第 201 行**：仍写着 `19 vs 16。**缺口比不完整更多。**`（PARTIAL 实际已更新为 17）。
> 2. 同上 **第 215 行**：完成度声明中仍写着 `\| 四个 `COVERED` 逐个给出理由 \| **完成** \|`。
> 3. [GOV-EVIDENCE-UNIQUE-1-3b62f7937.md](file:///G:/CODEX/New%20Manga/doc/handoffs/GOV-EVIDENCE-UNIQUE-1-3b62f7937.md) **第 78 行**：小节标题仍为 `### 3. `EVIDENCE_GAP`（19）多于 `PARTIAL`（16）`。

---

### 2. 数字是否全部自洽：✅ 主体数字自洽，未见“4 个 COVERED”断言

- **汇总表行相加**：[ac2-coverage-batch3-and-summary.md](file:///G:/CODEX/New%20Manga/verification/GOV-EVIDENCE-UNIQUE-1/ac2-coverage-batch3-and-summary.md) 13 个 Task 的分项判定数字（第 140–156 行）行相加完全自洽：
  $$\text{COVERED}: 3, \quad \text{PARTIAL}: 17, \quad \text{EVIDENCE\_GAP}: 19, \quad \text{NOT\_APPLICABLE}: 42, \quad \text{总计}: 83$$
- **百分比吻合度**：完全吻合：$3/83 = 3.6\%$、$17/83 = 20.5\%$、$19/83 = 22.9\%$、$42/83 = 50.6\%$。
- **Handoff 数字一致性**：Handoff 顶部的枚举结果表已更新为 `3 / 17 / 19 / 42`，与证据文件统计一致。
- **旧断言排查**：全文未再检索到 `4 个 COVERED` 或 `4.8%` 的有效断言语句（仅在上述第 185 行/第 67 行表格行残留，以及第 215 行汉字“四个 COVERED”）。

---

### 3. Canonical Evidence 表是否合规且正确：✅ 完全合规且校验一致

在 [GOV-EVIDENCE-UNIQUE-1.md](file:///G:/CODEX/New%20Manga/doc/tasks/GOV-EVIDENCE-UNIQUE-1.md) 第 104–114 行补充了 `## Canonical Evidence` 表：
- **格式规范**：完整包含 6 列（`evidence_id | AC/Gate | path | commit | sha256 | class`）。
- **SHA-256 独立计算校验**：对表中登记的全部 9 行文件，逐一通过 `Get-FileHash -Algorithm SHA256` 独立计算磁盘实际哈希并比对，**9 项全部 100% 精确匹配**：
  1. `EVID-AC1-FREEZE`: `a339dd41c030d1af2ea3e1a52a550d85dbecd042ec8d29c9a56ffb636d3e7f5e`（PASS）
  2. `EVID-AC1`: `2942b273afb820c7edc1cd85cf8856633263a32afd78d41e9aa299523abfbcfa`（PASS）
  3. `EVID-AC1-JSON`: `ac54944b703d0fccc37d4b17a90b260280ec664b5493e5b87e79de47dbdcee2f`（PASS）
  4. `EVID-AC2-MAP`: `09450278df57ad7b24e2da249a1bb7dd074e9e5581b7735d3f4761946b04df8f`（PASS）
  5. `EVID-AC2-B1`: `926e6675e6c99e48a4f9a0ddca3c1e6846048cf7f22d1425856367439b043059`（PASS）
  6. `EVID-AC2-B2`: `82c9523862aed6071e6e3bdeb8b979c3c50697811e6f9cfefff7fed9b5644241`（PASS）
  7. `EVID-AC2-B3`: `31b4d15fce8c6eae6427921df2d4e4e74326437f49d452a994438cabe2e5f898`（PASS）
  8. `EVID-AC3`: `89d92ef4084d88cfd63ade5ea4f836719b00788b6b0bbb3313db77f87c7d581c`（PASS）
  9. `EVID-REVIEW`: `a9abc01e6514ddf786476dc369467a29afd787898a07de063f467781da7c83ed`（PASS）
- **完整性**：9 项证据覆盖 AC1–AC4 与独立 Review，提交 pin 统一指向包含提交 `c41a40a09`，无重复项。

---

### 4. 检查器结果：✅ 全部 PASS

运行官方治理检查脚本：
1. **Task 检查**：
   ```powershell
   pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/GOV-EVIDENCE-UNIQUE-1.md
   # 输出：
   # WARN: doc/STATUS.md 已达到预算的 80%：3139 bytes / 30 lines
   # WARN: evidence_dir 含未登记过程文件（归入 workspace 或列为 SOURCE_PIN）：...
   # Governance check: PASS (2 warnings)
   ```
2. **全局检查**：
   ```powershell
   pwsh -NoProfile -File tools/governance/check.ps1
   # 输出：Governance check: PASS (1 warnings)
   ```
- **结论**：此前阻断的 `FAIL: 进入 REVIEW/DONE 的 lifecycle v2 Task 必须列出 canonical evidence` 已彻底解除，两项检查均为 **PASS（0 errors）**。

---

## 二、残留问题的精确位置与原文

由于交付方在 commit `0a9e809e2` 中漏删了两个核心表格行及关联数字，在此逐条列出精确位置与原文：

### 残留 1：证据汇总文件表格第 185 行
- **文件**：[verification/GOV-EVIDENCE-UNIQUE-1/ac2-coverage-batch3-and-summary.md](file:///G:/CODEX/New%20Manga/verification/GOV-EVIDENCE-UNIQUE-1/ac2-coverage-batch3-and-summary.md)
- **位置**：第 185 行（位于 `### 1. 只有 3 个 AC 达到 COVERED` 表格中）
- **原文**：
  ```markdown
  | `P15-HOST-2` AC5 | 三次 vitest 递进 + core 508 passed，最终依据可辨识 |
  ```
- **修复方式**：删除该行，使表格与标题声明的 3 项保持一致。

### 残留 2：Handoff 交付文件表格第 67 行
- **文件**：[doc/handoffs/GOV-EVIDENCE-UNIQUE-1-3b62f7937.md](file:///G:/CODEX/New%20Manga/doc/handoffs/GOV-EVIDENCE-UNIQUE-1-3b62f7937.md)
- **位置**：第 67 行（位于 `### 1. 只有 3 个 AC 达到 COVERED` 表格中）
- **原文**：
  ```markdown
  | `P15-HOST-2` | AC5 | 三次 vitest 递进 + core 508 passed，最终依据可辨识 |
  ```
- **修复方式**：删除该行。

### 残留 3：说明文本中旧统计数字（16 项）
- **文件与行号**：
  1. [doc/handoffs/GOV-EVIDENCE-UNIQUE-1-3b62f7937.md](file:///G:/CODEX/New%20Manga/doc/handoffs/GOV-EVIDENCE-UNIQUE-1-3b62f7937.md) **第 78 行**：
     原文：`### 3. EVIDENCE_GAP（19）多于 PARTIAL（16）` $\rightarrow$ 应更新为 `PARTIAL（17）`
  2. [verification/GOV-EVIDENCE-UNIQUE-1/ac2-coverage-batch3-and-summary.md](file:///G:/CODEX/New%20Manga/verification/GOV-EVIDENCE-UNIQUE-1/ac2-coverage-batch3-and-summary.md) **第 201 行**：
     原文：`19 vs 16。缺口比不完整更多。` $\rightarrow$ 应更新为 `19 vs 17`
  3. 同上文件 **第 215 行**：
     原文：`| 四个 COVERED 逐个给出理由 | 完成 |` $\rightarrow$ 应更新为 `三个 COVERED`

---

## 三、总体结论

### **CHANGES_REQUESTED**

**说明**：虽然治理检查（AC5）已由 FAIL 修复为 PASS，且证据 Hash 完全吻合，但交付方在声称“已全部修好并校验为 0 残留”的 commit `0a9e809e2` 中，**关键表格内的 `P15-HOST-2 AC5` 行在两个文件中均未被删除**（表格仍显示 4 行，直接与标题“只有 3 个”冲突）。鉴于表格作为交付判定结论的严肃性，必须在 closeout 前将上述两处表格行及旧数字清理完毕。

---

## 推荐下一步

根据协作协议 §5.1，推荐由 **Codex** 或交付方执行极小幅度的行删除修复后直接 Closeout：

```text
Recipient: Codex
Instruction:
对 Task GOV-EVIDENCE-UNIQUE-1 执行文本残留清洗并完成 Closeout：
1. 删去表格残留行：
   - verification/GOV-EVIDENCE-UNIQUE-1/ac2-coverage-batch3-and-summary.md 第 185 行
   - doc/handoffs/GOV-EVIDENCE-UNIQUE-1-3b62f7937.md 第 67 行
2. 同步文本数字：将上述两文件中的「PARTIAL（16）」更新为「PARTIAL（17）」，「四个 COVERED」更新为「三个 COVERED」；
3. 文本清洗后无需再次流转 Review，直接批准并执行 Task Closeout。
```
