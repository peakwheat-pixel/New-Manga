---
id: M2-SFX-BJ13-RECALL-1
title: "BJ13 召回恢复链：v2b 生产链 BJ13/14/15 sfx 召回实测（探针零 src）→召回恢复则仲裁阈值域重审切片，未恢复则剩余选项登记交裁决"
kind: feature
status: ready
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权）
approval: user_2026-10-06「释放：Workbench React 页（依赖已就绪）、UI-MITIGATION 实现（blocked 已解除）、BJ13 召回恢复链」三件之一（候选 C；合同锚点=M2-REGION-OVERLAP-ARBITRATION :60 依赖链注记）
depends_on: [M2-REGION-OVERLAP-ARBITRATION, M2-SFX-GPU-EP-1]
base_commit: 3a65150b
branch: agent/zcode/M2-SFX-BJ13-RECALL-1
worktree: G:/CODEX/New Manga.worktrees/M2-SFX-BJ13-RECALL-1-zcode
review_events: []
created: 2026-10-06
---

# Task: M2-SFX-BJ13-RECALL-1 — BJ13 召回恢复链

## 背景与授权

用户 2026-10-06 释放三件中的候选 C。合同锚点（PLAN 无候选 C 行，以此为准）：M2-REGION-OVERLAP-ARBITRATION（done @merge `38e4e487`）Task :60 依赖链注记——「BJ13 的自动化闭合挂在未来的 sfx 召回恢复 Task（域外根因修复…）；**该 Task 释放时须按其召回后形态重审阈值域，env 旋钮已预留**」+ arbitration-report.md:56 重审条件（「内含形出现、或任何 0.85+ 对出现时必须重审」）+ :255（「BJ13 的自动化闭合路径 = sfx 召回恢复之后按未来形态重新校准（env 旋钮已预留，重校准是新证据切片）」）。

关键事实（2026-10-06 侦察实证）：
- BJ13（densho810 vol03_p0048，2946×4167 竖排毛笔页）：sfx 通道对参照框零响应（raw pre-NMS 峰值 0.0855/0.0043），像素被 text 类捡走（0.744/0.844）→ 误路由进对白链乱译。根因=域外（L3 crop 7/7 sfx 分数 0.0000-0.0109 vs 域内 BJ06 0.721-0.9355）。
- **域外根因的修复链已实际执行并切生产**：fine-tune 全链（T0→T1a→T1b-R1/R2/R3→T2 V1/V2→T3 Gate→T4 切 v2b @`cff4923e`）+tile 化+GPU DML。**但 BJ13 从未进入任何评测集**（T3 考卷=BJ17/18；BJ13 唯一 GT 判定=R1 delete 未翻案；challenge 空集）——「召回恢复是否已发生」在当前 v2b 生产链上**没有登记证据**。
- BJ13 路由判定：2946×4167 → `page_w>690` 且 aspect≈1.41<8.0 → **letterbox 路径**（tile 口径是 KO 长条页专用，`detection_sfx.py:556-562` 谓词）；生产装配 `core_assembly.py:973-985` composite 默认 ON。
- 仲裁旋钮已预留：`NEWMANGA_SFX_ARBITRATION[_IOU]` typed 旋钮+`sfx_arbitration_partial_overlap` 诊断码；BJ13 形态历史重叠读数 0.490-0.550（冻结域 0.90 之外）。

## 验收条件

- **AC1 召回实测（第一交付，「先验证」）**：在当前 v2b 生产链（letterbox、conf 0.5、NEWMANGA_SFX_EP 默认 dml，等价生产装配语义）对 BJ13/BJ14/BJ15 + 域内对照 BJ06 跑 sfx 检测实测：用 DOMAIN-EXT-DIAG L1/L3 探针先例（`experiments/M2-SFX-DETECT-DOMAIN-EXT-DIAG/**` 脚本形态，零 src），记录每页 sfx 通道候选数/conf/与参照框 IoU；BJ13 参照框=DOMAIN-EXT-DIAG raw `l1-fullpage-conf-scan.json` 两处 approx（(2210,240,2560,1000)/(420,2560,760,3400)）；判定标准=「召回恢复是否发生」三态结论（恢复/部分恢复/未恢复）逐页登记。BJ13/14/15 页面与 v2b 权重在 gitignored task-envs 外部树（如实登记路径，零入库）。
- **AC2 分支 A——召回恢复（全或部分）**：按登记义务执行仲裁阈值域重审切片：BJ13 新形态的 sfx×primary 重叠量 vs 0.90 冻结域、重审条件（内含形/0.85+ 对）核对、`NEWMANGA_SFX_ARBITRATION[_IOU]` 旋钮是否需要重校准的提案（**提案交集成/用户裁决，不自行改冻结域**）；若改标链路被触发走既有 `sfx-arb-` 前缀→RegionType.SFX→SfxPolicy 门链路（登记即可，不实施产品改动）。
- **AC3 分支 B——召回未恢复**：登记剩余选项交用户裁决，不新发明方案：①BJ13 补标（须先翻案 R1 delete 裁决/裁决 challenge 语义=用户裁决点）；②R3-MISS 同款 ai-direct 补画形态扩展至 BJ13/14/15（BJ36/37 0 框先例已登记）；③维持现状（损害兜底=UI-MITIGATION 实现+`sfx-policy=skip` 既有面）。各选项登记成本/收益与推荐序。
- **AC4 回归与纪律**：零 src 或最小 src；若触 src，冻结回归锚逐位不破：BJ06 8 region、KO 10 case 仲裁 off/on 逐位、KO tile 35/56+npd 48/135 parity、三套件 1840+1sk+1 failed 等量递增；`git diff --check` EXIT=0（工作区口径）。
- **AC5 文档**：探针实验报告（`verification/M2-SFX-BJ13-RECALL-1/recall-report.md`）+raw 证据+Task 回填+Handoff；分支结论显式登记（AC2 或 AC3 路径）。

## 纪律与限制

- 允许路径：`experiments/M2-SFX-BJ13-RECALL-1/**`、`verification/M2-SFX-BJ13-RECALL-1/**`、`doc/tasks/M2-SFX-BJ13-RECALL-1.md`、`doc/handoffs/`、`tests/**`（仅当触 src 时配套）。
- 禁改：`src/**` 生产代码（探针实验零 src；若实测证明必须触 src，停等交集成裁决后再扩授权）、冻结阈值域（0.90 IoU/conf 0.5/tile 路由谓词——重校准是提案不是实施）、`doc/contracts/**`、`doc/STATUS.md`/`doc/REBASELINE_PLAN.md`（集成方收口面）、M2-REGION-OVERLAP-ARBITRATION 历史证据文件。
- 权重/页图零入库（外部树 task-envs；探针证据只记路径+sha256）；实验脚本沿 DOMAIN-EXT-DIAG 先例形态（直接调 provider 类，不 mock）。
- 实测结论措辞纪律：逐口径核对自家数字（DML↔CPU 漂移窗口 ≤2e-06 既有登记；跨形态禁写「位级可复现」）。
