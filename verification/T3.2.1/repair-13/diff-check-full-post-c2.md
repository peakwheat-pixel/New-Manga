# F-1/F-3 evidence-only 修正后的完整 diff-check 补记（Review 条件 C2）

日期：2026-09-25（Asia/Shanghai）。分支 `agent/zcode/T3.2.1-repair-13`，
修正基点 = evidence head `66a13f8a5a56be63f72ceca47406262ed9cfaa9a`，
产品 delivery 保持 `aed009405fd523c52fa45e604afe40f01cef3d45` 不变。
本记录属 Task 登记的单一 evidence-only follow-up（C2），不触碰 Review 报告、
交付代码、测试与 AC 结论。

## 修正内容

- **F-1**：`screenshots/10-export-window-export-complete.png` 经 `git mv` 更名为
  `.jpg`（文件首字节 `ff d8 ff e0`，实为 JPEG/JFIF 字节；原名扩展名 `.png` 与字节
  不符）。仅更新 `local-verification.md` 与 `doc/handoffs/T3.2.1-REPAIR-13-aed0094.md`
  中指向该截图的链接；截图字节内容零改动（改名不改变 blob 内容）。
- **F-3**：清除三份判别 RED 日志的行尾空白（仅删除行尾空格/制表符，行内容与
  记录的命令输出序列不变）：
  `discriminating-pre-repair.log`（5 行）、`f13-2-pre-repair-red.log`（3 行）、
  `f13-4-pre-repair-red.log`（6 行），合计 12 处，与 Review 指出的完全一致。

## diff-check 记录

修正前（base `8738c41` → evidence `66a13f8`，完整）：

- 命令：`git diff --check 8738c41 66a13f8`
- 结果：**exit 2**，12 处 trailing whitespace，全部位于上述三份 RED 日志
  （`discriminating-pre-repair.log:31,68,93,96,107`、
  `f13-2-pre-repair-red.log:17,20,33`、`f13-4-pre-repair-red.log:16,19,25,29,44`）。
- 子集：`git diff --check 8738c41 66a13f8 -- src tests` = exit 0。

修正后（base `8738c41` → 本次修正的完整变更，即即将提交的工作区状态）：

- 命令：`git diff --check 8738c41`（不含路径限制，覆盖全部变更）
- 结果：**exit 0，无输出**。
- 子集：`git diff --check 8738c41 -- src tests` = exit 0。

本文件随同一 evidence-only commit 提交；提交后以
`git diff --check 8738c41 <new-evidence-head>` 复核提交树（内容与上列工作区
状态一致），结果在本 commit 的 Handoff/交付回报中引用。F-1/F-3 清理后，
完整 diff-check 不再存在非零项；`git diff --check` 仍仅是 whitespace 检查，
不构成完整审查结论，范围核对以 Review 报告与 Handoff 变更路径清单为准。
