# FEA-09 UNFREEZE r15 独立复核（ZCode；Codex 额度耗尽后的授权故障转移）

- Reviewer：ZCode 独立会话（GLM-5.3），session `sess_1f1d2a34-8d15-4e48-add5-5b32af8ff1a3`；未参与 FEA-09 实现、I001 裁决、r1–r14 起草或 r15 修订。
- 只读：未修改仓库/文件、未 commit/push。
- reviewed_head：`a7f6363003573dd42d65033b2a84dff5d6c3e2d9`；被审 r15 提案为未跟踪工作树文件（1,552 bytes）。
- 结论：**approved（P0=0 / P1=0 / P2=1）**；P2 仅为 r14-review 归档缺失（已在 DSH 侧补归档）。
- Codex 本日额度耗尽（重置于 2026-11-04 03:33），按用户长期授权故障转移候选仅 ZCode，故由 ZCode 执行本次独立复核。

---
Plan mode 拦截了组合命令；指纹复算非必需（HEAD 以 git 快照 `a7f636300` 为准，SHA-256 留 DSH 归档时执行）。证据已充分，输出审查报告。

---

# FEA-09 UNFREEZE r15 独立复核报告

**审查者**：ZCode 独立会话（GLM-5.3），未参与 FEA-09 实现、I001 裁决、r1–r14 起草及 r15 修订。**只读**：未修改任何文件、未 commit/push。审查对象 = 未跟踪工作树文件 `doc/reviews/FEA-09-UNFREEZE-r15-amendments.md`（1,552 bytes）；HEAD 依会话 git 快照 `a7f636300`（r13-review 同 head）。已读：r15/r14/r13-review、M2-C1 §6.3、C-05 v1.1、C-15、C-16、impl-design。

## 1. R14-001：**CLOSED**

r15 替换文本对照 M2-C1 §6.3（权威行号）逐项核实：

| R14-001 要求 | r15 文本 | M2-C1 依据 | 判定 |
|---|---|---|---|
| 非负有限 number | 「非负有限数值（number）」 | L935/L948 `scroll_offset_y: number`（对照 L917–919 明确标 `integer` 的字段，number 为有意区分）；L956 拒 negative/non-finite | ✅ |
| 页高范围沿用 §6.3 | 「有限、非负、页高范围沿用既有校验，不额外要求整数」 | L955「within the one logical Page」+ L956 拒「offset outside the Page height」；r15 纯引用、零新增校验 | ✅ |
| 不取整不归一化 | 头部「不归一化、不取整」+「不额外要求整数」+ 不变量「不引入 0..1 归一化、不取整」 | r14「非负整数」确与 M2-C1 冲突（已保存合法小数 offset 被 §6.3 接受却在 r14 文本下无法原值恢复）；r15 修正 | ✅ |
| 合法保存值原值恢复 | 「保存 scroll_offset_y 原值（含合法小数，不取整）」 | L956「Reopening the chapter with `resume` reads that persisted page/coordinate」 | ✅ |
| 替代页 0 唯一且兼容 | 不可读/已移出/回绕/beginning/无进度五路径统一 `{替代可读页, 0}`；分页恒 0 | L955「Paged chapters … `scroll_offset_y=0`」；路径枚举完整、无歧义分支 | ✅ |

「r15 = r14 仅一处替换」**成立**：diff 全部变化（整数→number、加不取整、单位→单位与校验）均属 R14-001 修正面，无范围扩大；R13-002 锚点块未触碰——r14 的 `(sort_order, page_id)` 完整二元组 0-based 插入比较**独立再确认**满足 r13-review R13-002 最小修订，本轮不重新打开。

## 2. 剩余外部可观察 P1：**无**；1×P2（证据链，非契约语义）

**P2-1**：r15 依据字段引用的 `FEA-09-UNFREEZE-r14-review.md` 在 `doc/reviews/` **不存在**（ENOENT；r12-review 曾同样缺失后补归档），其「P0=0/P1=1/P2=0、reviewed_head `a7f636300`、r14 SHA-256 `afb924d2…`」无法独立核实；本报告按委托口径给定的 R14-001 要求评判。处置：沿 r12 先例，**冻结流程内原字节补归档 r14-review**。

## 3. 结论

P1=0，**approved 可进入冻结**，路径确认可行：语义修订提交（C-05/C-15/C-16）→ 三指纹/old-new blob → 已提交字节复核 → 仅元数据冻结（FROZEN/矩阵/载体 §8/旧 pin）→ check + 17 pins。「M2-C1 无字节变更登记」成立——r15 为既有 §6.3 语义引用而非修订。P2-1 补归档纳入该流程完成后闭合。

未运行项：pytest/.NET/build/真实 IPC/DPAPI/迁移/竞态/泄漏/check.ps1/verify_pins 全部 **NOT_RUN**（文档级审查；r15/r14 SHA-256 亦未复算，留 DSH 归档时执行）。

**verdict: approved**（P0=0 / P1=0 / P2=1）

---

**推荐下一步**：由 **DSH** 原字节归档本报告与 r14-review，随后按 r15 §冻结路径执行语义提交与重冻（P2=1 不阻断 P0/P1=0 门槛）。

---
归档时间：2026-11-03T15:52:25.9728781+00:00（DSH）；ZCode traceId：f811bdd4-0059-453e-bc31-d41089b6952c；turnId：turn_f5935b87-d5e4-4b3a-92cc-782afeef75c4。