---
id: M2-SFX-BJ13-RECALL-1
title: "BJ13 召回恢复链：v2b 生产链 BJ13/14/15 sfx 召回实测（探针零 src）→召回恢复则仲裁阈值域重审切片，未恢复则剩余选项登记交裁决"
kind: feature
status: in_review
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

## 执行记录（ZCode 2026-10-06，status in_review 停写）

- commit 链：claim `0f175b89` → impl（探针脚本）`47df4dbc` → verify（raw+报告）`d95bbdfe` → docs（本回填+Handoff，tip 见分支头）。base=`2a1a9f73`，分支 `agent/zcode/M2-SFX-BJ13-RECALL-1`。
- AC1 **PASS**：v2b 生产链语义（letterbox、conf 0.5、NMS 0.7、EP=dml 实测生效、权重 pin `944e8114…` 强制校验）四页实测完成。三态：**BJ13 部分恢复（信号面）**（参照框 conf≥0.5 零检出；低 conf 信号 ref1 0.3727/IoU 0.5235 = 基线 4.4x、ref2 0.1796/IoU 0.5584 = 基线 42x；页面级 1 个 conf 0.8914 sfx 候选=Slipknot 印刷字非参照框）；**BJ14 未恢复**（全 rung 零）；**BJ15 未恢复**（参照框零；页面级孤立候选 0.5118 仅注记）；**BJ06 对照 5/8 region 命中**（与 T4 G7 v2b 臂逐框亚像素一致 5=5；chiqui7 为 8/8，回退为 T4 已登记形态）。判定标准 X 值（IoU≥0.1 恢复线/≥10x 或 conf≥0.2 部分恢复线）为 Owner 裁量，理由登记于 recall-report §2。
- AC2 **履行（部分恢复触发）**：BJ13 真实形态 sfx×primary **max IoU=0.0**（Slipknot sfx 检出无 primary 对手，3 manga 全不相交）——0.90 冻结域无对象，比历史合成口径 0.490/0.550 更远离；重审条件语境读法未触发（BJ13 无内含形/无 0.85+ 对），字面全域读法的 BJ06 0.8732/内含形 0.7576 均为 chiqui7 时代已观测形态（0.8865/0.870）非新事实；**提案=维持 0.90 冻结域不变**（报告 §3.3，交裁决不实施）；`sfx-arb-` 改标链路本次零触发（已登记）。
- AC3 **登记**：三选项成本收益+推荐序 ③维持现状 → ②ai-direct 补画扩展 → ①BJ13 补标（报告 §4，交用户裁决）。
- AC4 **零 src**：`src/**`/`tests/**` 零字节变化；冻结回归锚代码面未触碰，不跑全量 pytest 的理由登记（报告 §5）；`git diff --check` EXIT=0。
- AC5 **PASS**：`verification/M2-SFX-BJ13-RECALL-1/recall-report.md` + `raw/recall-probe.{json,-run.log}` + 本回填 + `doc/handoffs/M2-SFX-BJ13-RECALL-1-zcode-20261006.md`。
- 新增事实登记（历史口径修正）：①chiqui7 在 BJ13 并非页面级零检出——仲裁 rerun raw `sfx-1`（conf 0.8222）即 Slipknot 印刷字检出，v2b 同位 conf 0.8914、跨权重框 IoU 0.9444（两代权重域内一致性正面证据）；DOMAIN-EXT-DIAG「零响应」仅在两个目检拟声词参照框口径成立。②v2b 在四页 bubble/panel/text 通道 conf≥0.01 全零（仅 sfx 类候选）——与 G7 v2b 臂形态一致，登记为 v2b 已知形态。
- 环境：venv `G:/CODEX/New Manga.task-envs/M2-SFX-T5-TILE-gpu`（onnxruntime 1.24.4 DML，imgsz=1024 由 v2b metadata 驱动）；primary 候选复用 2026-10-03 仲裁 rerun（ogkalu 三文件 sha256 当次重验与 pin 一致，漂移即 exit 3）；DML 单形态，跨形态措辞按 ≤2e-06 漂移窗口纪律执行。
- 遗留/裁量：判定标准 X 值、BJ15 孤立候选处置、G7 EP 形态未登记的对位口径注记、Slipknot 目检为 Owner 观测——均见 recall-report §2/§6（Known limitations 不得省略引用）。
