# M2-DETECTION-HYGIENE 集成记录（代行 Codex / 编排会话）

- 分支 `agent/zcode/M2-DETECTION-HYGIENE`；链：`24a89d7d` → `561a79cd`(implement，r1 被审头) → `02b6d2a2`(返修，r2 被审头) → `ed86cc46`(r2 P0 修复) + `52585b64`(事故登记，r3 核验) → `1747dc05`(finalize)
- Review 链：DSH r1 **有条件通过**（5×P2：R1 TILING 改声称替代实现/R2 BACKFILL 收窄零测试+降级理由被推翻/R3 重 raise strand 风险/R4 缺 raw pytest/R5 SETTINGS-IPC R7 前提为假）→ 返修 → DSH r2 **changes_requested（1×P0）**：**R1 lazy split 在 tip 零痕迹消失**——被红态归档的 checkout-恢复抹掉（BACKFILL R9 同款失败模式第二次发生）→ 修复+事故登记（流程修正：红态归档前先 commit+恢复后全工作区复核）→ DSH r3 **P0 closed**（`doc/reviews/M2-DETECTION-HYGIENE-{561a79cd-dsh-r1,02b6d2a2-dsh-r2,52585b64-dsh-r3}.md`）

## 正式结论

1. **TILING R1/R3**：`_tiling_trigger_ratio()` eager（触发判定必需，非法值 provider 级 fail-fast=SFX conf 同语义）+ `_tiling_config(trigger_ratio)` 参数化（几何旋钮 lazy 解析于 tiled 分支内——非法值只 fail webtoon 页，**普通页零变化行为恢复**）；空/空白 env typed 拒绝（never-silent-default）；+10 用例红→绿（行为级红态归档）。
2. **BACKFILL N1**：规划期 except 收窄 `{TARGET_DELETED,TARGET_NOT_FOUND}` 才跳过、其他重 raise；R3 包护（commit 路径 else 分支 PipelineError→_fail_step）闭合 strand 风险；桩测试按 DSH 配方重建（首读透传代理；实测语义：非白名单=DB_FAILED 码弱点登记的 typed 失败/TARGET_DELETED=全跳过终态 N2 形态）。
3. SETTINGS-IPC R7/R8=集成方 main 侧闭合（见 close commit）；R5/R6 登记不做。

## 集成运行时项

- pytest 三套件 **611+1skipped 0 failed**、cargo 46+1ig、vitest 49（fresh worktree 全环境搭建：sidecar+npm install+frontend build）
- 事故：checkout-restore 抹除修改第二次发生——流程修正已入 implementation.md
