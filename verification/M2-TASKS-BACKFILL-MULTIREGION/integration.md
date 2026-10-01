# M2-TASKS-BACKFILL-MULTIREGION 集成记录（代行 Codex / 编排会话）

- 分支 `agent/zcode/M2-TASKS-BACKFILL-MULTIREGION`；链：3-followup release `f99a6c55` → `f541b2f4`(implement) → `fa866327`(docs，r1 被审头) → `95469952`(返修代码) + `7176b6dc`(证据，r2 被审头)
- Review 链：DSH r1 **有条件通过**（核心语义修复独立成立：_plan_region 复用对 region_ids[1:] 与恢复路径逐项等价、SFX gate plan 层声称成立、红态自洽；R1 本 Task 引入 P2=progress 账目缺口/R2 既有缺陷 P2=primary 不经 SFX gate；`doc/reviews/M2-TASKS-BACKFILL-MULTIREGION-f541b2f4-dsh-r1.md`）→ Owner 返修 R1-R7 全 closed（R1 真修+**断言有效性红态 terminal 12≠17 独立交叉验证**；R4 e2e 红态/R5 双侧基线归档）→ DSH r2 **`approved`（可集成）** 0×新 P0/P1/P2（`doc/reviews/M2-TASKS-BACKFILL-MULTIREGION-95469952-dsh-r2.md`）

## 修复内容（正式）

- backfill 逐 region 展开（与恢复路径 `_plan_region` 同语义同函数）：多 region 页非首 region 获得完整 PlanUnit 链；SFX gate 在 plan 层对每个 region 生效（manual/skip→SKIP_POLICY 不翻译，translate→同 run 翻译）；R1 terminal 账目同步（SKIP 终态 unit 计入 terminal，progress==1.0）；R3 规划期 current() 异常按 TARGET_DELETED 语义跳过
- 测试：+6（F1-F5+R1 断言）；红绿：红 6F/11P→绿；e2e 红态归档（base src 下 translate_policy 用例 FAILED '' != MOCK-SFX-TRANSLATED-TEXT）
- 集成方主 venv 双侧复跑：见 close commit 登记

## 集成方搬运项（本 commit 后在 main 执行）

1. R6 superseded-by 文字 → M2-SFX-TRANSLATE-ENTRY handoff（「backfill 已由本 Task 落地，'registered scheduling slice' 表述已被取代」）
2. R2 独立 Task 候选 → STATUS 后续释放候选（**裁决请求：单 region SFX 页是否对 primary 重决策**——DSH 反例=对调 reading_order 使 SFX 成 primary+policy=manual ⇒ 落 machine_translation 违反 D06 §85）
3. N1/N2（P4）登记：R3 catch 分支无测试+偏宽（建议收紧 error.code 集合+补测试）；「与恢复路径语义一致」在 width/height NULL 子例过宽
