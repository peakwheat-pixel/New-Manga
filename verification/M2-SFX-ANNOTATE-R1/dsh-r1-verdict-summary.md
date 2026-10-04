# M2-SFX-ANNOTATE-R1 DSH r1 结论纪要（2026-10-04）

> **证据性质披露**：DSH headless 会话内部经「三个只读复核子代理→主报告→补充说明」多轮输出，
> stdout 仅保留最终一条（补充说明+结论重申）；主报告全文未落盘、未随 stdout 保留。本纪要按
> stdout 原文如实转录，P3×8/P4×5 明细缺全文，由 DSH r2 复核时重列。审查对象 tip=49a6034c。

## Verdict

**approved_with_conditions**（0×P0、2×P1、3×P2、8×P3、5×P4）

## r1 原文（stdout 最终输出转录）

三个只读复核子代理（AC3 判定 / AC4-AC5 产物 / 工具纪律）现已全部收口，其结论与我先前签发的
Review 报告**逐条一致，无改判**。仅补充两处边界说明（不改 Verdict）：

1. **`consensus ∪ divergence == agy 全量 id` 属数学闭包，非穷举证明**：已证 |agy|=413、
   |consensus|=397、|divergence|=16、两集合互斥、16 个 divergence id 全在 agy，且 agy verdict
   多重集与重建完全吻合（297=294+3、113=103+10、3=0+3），因此 consensus 的 397 id 必落在 agy
   内——**前提是 agy 413 行 id 无重复**，该去重校验未做。原文报告已按此口径表述为「数学闭包
   成立，前提为无重复 id」，无需修正。
   【编排代验闭环（列注，非 r1 原文）2026-10-04：agy 413 行 id 唯一性校验 PASS（413/413 无重复），前提已钉死。】

2. **`units.json` 本体不可复算，806/413/分层数字由 `worksheet.json` 代理复算**：`units.json`
   是单行超大 JSON（read/grep 只能计到 1），报告的「806 / 413 / 262 / 124 / 7」实际来自同一
   语料的格式化副本 `worksheet.json`（含 `n_units: 806` + 逐单元 `ai_conf`/`review_tier`）。
   **结论不变**（两文件同源、闭环自洽），但报告该项精确表述应为「`units.json` 不可复算；由
   worksheet.json 代理复算得同值」。

## 结论重申（r1 原文）

**Verdict = approved_with_conditions**（0×P0、2×P1、3×P2、8×P3、5×P4）

- **C1（必闭）**：BJ 15/25、KO 10/15、BJ 正集 0、challenge 空 → 显式登记为「A′ 采纳输入条件
  未满足」并交用户/编排裁决（对照 `verification/M2-SFX-FINETUNE-PREFLIGHT/preflight-report.md:61`）。
- **C2（必闭）**：AC3「用户逐条审核→AI 代审」的用户裁决原文/ID 落档 +
  `doc/tasks/M2-SFX-ANNOTATE-R1.md:33` 判据正文修订。
- **C3–C5（P2）**：「独立复核」→「内部复算（同 workflow）」措辞边界；回放 5 页目的不一致登记；
  ai-consensus 证据强度上限声明。

**推荐下一步**：ZCode 在同 worktree 做纯文档/登记返修（零 src、不动数据本体与 experiments 逻辑），
完成后交 **DSH r2** 复核。

## 返修落实对照（Owner，2026-10-04）

| 条件 | 落实位置 |
|---|---|
| C1 | stage2-report.md §8.1 对照表+T2 处置选项 (a)/(b)/(c)；Task「标注量承诺」段注记 |
| C2 | 用户裁决原文落 Task AC3 修订注记+报告 §0（含停点裁定链 61fe5cd5→de1b7bf9） |
| C3 | 三文档全局「独立复核/独立复算」→「内部复算」+报告 rev3 行措辞澄清 |
| C4 | 报告 §8.1 末段「回放 5 页目的偏差」 |
| C5 | 报告 §0「ai-consensus 证据强度上限」 |
| 补充说明 1 | 编排代验 agy id 唯一性 PASS（上文括注） |
| 补充说明 2 | 口径已知悉；worksheet.json 代理复算在 r1 报告内已成立，无文档动作 |
