---
id: M2-SFX-BJ13-RECALL-1
title: "BJ13 召回恢复链：v2b 生产链 BJ13/14/15 sfx 召回实测（探针零 src）→召回恢复则仲裁阈值域重审切片，未恢复则剩余选项登记交裁决"
kind: feature
status: done
integration: merge ec460508（收口见 STATUS；DSH r2 approved 0×新 P0/P1/P2）
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权）
approval: user_2026-10-06「释放：Workbench React 页（依赖已就绪）、UI-MITIGATION 实现（blocked 已解除）、BJ13 召回恢复链」三件之一（候选 C；合同锚点=M2-REGION-OVERLAP-ARBITRATION :60 依赖链注记）
depends_on: [M2-REGION-OVERLAP-ARBITRATION, M2-SFX-GPU-EP-1]
base_commit: 2a1a9f73
branch: agent/zcode/M2-SFX-BJ13-RECALL-1
worktree: G:/CODEX/New Manga.worktrees/M2-SFX-BJ13-RECALL-1-zcode
review_events: [r1 2026-10-06 DSH 非作者 approved_with_conditions（0×P0/P1；1×P2+5×P3+7×P4；核心事实层独立重算成立；返修见执行记录 r1 返修段；报告=doc/reviews/M2-SFX-BJ13-RECALL-1-e6b4684c-dsh-r1.md）,
 r2 2026-10-06 DSH 非作者 approved（r1 三项条件 C1/C2/C3+顺笔 P3-1/P3-5/P4-3..7 全闭+P4-1/2 登记核验；r1fix 同形态逐位互证独立核验成立；0×新 P0/P1/P2；报告=doc/reviews/M2-SFX-BJ13-RECALL-1-04d5f621-dsh-r2.md）]
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

- **AC1 召回实测（第一交付，「先验证」）**：在当前 v2b 生产链（letterbox、conf 0.5、NEWMANGA_SFX_EP 默认 dml，等价生产装配语义）对 BJ13/BJ14/BJ15 + 域内对照 BJ06 跑 sfx 检测实测：用 DOMAIN-EXT-DIAG L1/L3 探针先例（`experiments/M2-SFX-DETECT-DOMAIN-EXT-DIAG/**` 脚本形态，零 src），记录每页 sfx 通道候选数/conf/与参照框 IoU；BJ13 参照框=DOMAIN-EXT-DIAG raw `l1-fullpage-conf-scan.json` 两处 approx（(2210,240,2560,1000)/(420,2560,760,3400)）；判定标准=「召回恢复是否发生」三态结论（恢复/部分恢复/未恢复）逐页登记。BJ13/14/15 页面与 v2b 权重在 gitignored 外部树（v2b 权重在 task-envs；页图在 peer worktree `test_assets/comic_golden_suite/日漫_JA/01_black_jack_official/`——该目录由其 `.gitignore:26` 忽略；如实登记路径，零入库；措辞按 DSH r1 P4-5 修正）。
- **AC2 分支 A——召回恢复（全或部分）**：按登记义务执行仲裁阈值域重审切片：BJ13 新形态的 sfx×primary 重叠量 vs 0.90 冻结域、重审条件（内含形/0.85+ 对）核对、`NEWMANGA_SFX_ARBITRATION[_IOU]` 旋钮是否需要重校准的提案（**提案交集成/用户裁决，不自行改冻结域**）；若改标链路被触发走既有 `sfx-arb-` 前缀→RegionType.SFX→SfxPolicy 门链路（登记即可，不实施产品改动）。
- **AC3 分支 B——召回未恢复**：登记剩余选项交用户裁决，不新发明方案：①BJ13 补标（须先翻案 R1 delete 裁决/裁决 challenge 语义=用户裁决点）；②R3-MISS 同款 ai-direct 补画形态扩展至 BJ13/14/15（BJ36/37 0 框先例已登记）；③维持现状（损害兜底=UI-MITIGATION 实现+`sfx-policy=skip` 既有面）。各选项登记成本/收益与推荐序。
- **AC4 回归与纪律**：零 src 或最小 src；若触 src，冻结回归锚逐位不破：BJ06 8 region、KO 10 case 仲裁 off/on 逐位、KO tile 35/56+npd 48/135 parity、三套件 1840+1sk+1 failed 等量递增；`git diff --check` EXIT=0（工作区口径）。
- **AC5 文档**：探针实验报告（`verification/M2-SFX-BJ13-RECALL-1/recall-report.md`）+raw 证据+Task 回填+Handoff；分支结论显式登记（AC2 或 AC3 路径）。

## 纪律与限制

- 允许路径：`experiments/M2-SFX-BJ13-RECALL-1/**`、`verification/M2-SFX-BJ13-RECALL-1/**`、`doc/tasks/M2-SFX-BJ13-RECALL-1.md`、`doc/handoffs/`、`tests/**`（仅当触 src 时配套）。
- 禁改：`src/**` 生产代码（探针实验零 src；若实测证明必须触 src，停等交集成裁决后再扩授权）、冻结阈值域（0.90 IoU/conf 0.5/tile 路由谓词——重校准是提案不是实施）、`doc/contracts/**`、`doc/STATUS.md`/`doc/REBASELINE_PLAN.md`（集成方收口面）、M2-REGION-OVERLAP-ARBITRATION 历史证据文件。
- 权重/页图零入库（权重在 gitignored task-envs；页图在 peer worktree `test_assets/comic_golden_suite/日漫_JA/01_black_jack_official/`，该目录 `.gitignore:26` 忽略——零入库结论不变，DSH r1 P4-5；探针证据只记路径+sha256）；实验脚本沿 DOMAIN-EXT-DIAG 先例形态（直接调 provider 类，不 mock）。
- 实测结论措辞纪律：逐口径核对自家数字（DML↔CPU 漂移窗口 ≤2e-06 既有登记；跨形态禁写「位级可复现」）。

## 执行记录（ZCode 2026-10-06，status in_review 停写）

- commit 链：claim `0f175b89` → impl（探针脚本）`47df4dbc` → verify（raw+报告）`d95bbdfe` → docs（本回填+Handoff，tip 见分支头）。base=`2a1a9f73`，分支 `agent/zcode/M2-SFX-BJ13-RECALL-1`。
- AC1 **PASS**：v2b 生产链语义（letterbox、conf 0.5、NMS 0.7、EP=dml 实测生效、权重 pin `944e8114…` 强制校验）四页实测完成。三态：**BJ13 部分恢复（信号面）**（参照框 conf≥0.5 零检出；低 conf 信号 ref1 0.3727/IoU 0.5235 = 基线 4.4x、ref2 0.1796/IoU 0.5584 = 基线 42x；页面级 1 个 conf 0.8914 sfx 候选=Slipknot 印刷字非参照框）；**BJ14 未恢复**（全 rung 零）；**BJ15 未恢复**（参照框零；页面级孤立候选 0.5118 仅注记）；**BJ06 对照 5/8 region 命中**（与 T4 G7 v2b 臂逐框亚像素一致 5=5；chiqui7 为 8/8，回退为 T4 已登记形态）。判定标准 X 值（IoU≥0.1 恢复线/≥10x 或 conf≥0.2 部分恢复线）为 Owner 裁量，理由登记于 recall-report §2。
- AC2 **履行（部分恢复触发）**：BJ13 真实形态 sfx×primary **max IoU=0.0**（Slipknot sfx 检出无 primary 对手，3 manga 全不相交）——0.90 冻结域无对象，比历史合成口径 0.490/0.550 更远离；重审条件语境读法未触发（BJ13 无内含形/无 0.85+ 对），字面全域读法的 BJ06 0.8732/内含形 0.7576 均为 chiqui7 时代已观测形态（0.8865/0.870）非新事实；**提案=维持 0.90 冻结域不变**（报告 §3.3，交裁决不实施）；`sfx-arb-` 改标链路本次零触发（已登记）。
- AC3 **登记**：三选项成本收益+推荐序 ③维持现状 → ②ai-direct 补画扩展 → ①BJ13 补标（报告 §4，交用户裁决）。
- AC4 **零 src**：`src/**`/`tests/**` 零字节变化；冻结回归锚代码面未触碰，不跑全量 pytest 的理由登记（报告 §5）；`git diff --check` EXIT=0。
- AC5 **PASS**：`verification/M2-SFX-BJ13-RECALL-1/recall-report.md` + `raw/recall-probe.{json,-run.log}` + `raw/recall-probe-run-r1fix.log` + `raw/r1fix/recall-probe.json`（r1fix 重跑互证） + 本回填 + `doc/handoffs/M2-SFX-BJ13-RECALL-1-zcode-20261006.md`。
- 新增事实登记（历史口径修正）：①chiqui7 在 BJ13 并非页面级零检出——仲裁 rerun raw `sfx-1`（conf 0.8222）即 Slipknot 印刷字检出，v2b 同位 conf 0.8914、跨权重框 IoU 0.9444（两代权重在该区——DOMAIN-EXT-DIAG 判定域外页 BJ13——判定一致的正面证据，措辞按 DSH r1 P4-3 修正）；DOMAIN-EXT-DIAG「零响应」仅在两个目检拟声词参照框口径成立。②v2b 在四页 bubble/panel/text 通道 conf≥0.01 全零（仅 sfx 类候选）——与 G7 v2b 臂形态一致，登记为 v2b 已知形态。
- 环境：venv `G:/CODEX/New Manga.task-envs/M2-SFX-T5-TILE-gpu`（onnxruntime 1.24.4 DML，imgsz=1024 由 v2b metadata 驱动）；primary 候选复用 2026-10-03 仲裁 rerun（ogkalu 三文件 sha256 当次重验与 pin 一致，漂移即 exit 3）；DML 单形态，跨形态措辞按 ≤2e-06 漂移窗口纪律执行。
- 遗留/裁量：判定标准 X 值、BJ15 孤立候选处置、G7 EP 形态未登记的对位口径注记、Slipknot 目检为 Owner 观测——均见 recall-report §2/§6（Known limitations 不得省略引用）。
- base_commit 对账（DSH r1 P3-4，集成裁决=统一 2a1a9f73）：frontmatter 原 `3a65150b`（Task 文件创建时的释放登记 tip）更正为 `2a1a9f73`（实际 worktree 起点；释放链 `630c3f51`→`2a1a9f73` 两 commit 均零代码面，回填注记自本轮起移至本段正文）。

### r1 返修段（DSH 非作者 2026-10-06：approved_with_conditions，0×P0/P1、1×P2+5×P3+7×P4；全部文本级闭合，零检测数字变化）

- **P2-1（闭合）**：recall-report §1 chiqui7 基线 imgsz 「1280」更正为 **1024**（三项记录一致：DOMAIN-EXT-DIAG raw `l1-fullpage-conf-scan.json:3`、`sfx-detect-eval-report.md:67`、`switch-report.md:67`+`rollback-drill.json:16`）；顺笔补基线 CPU 形态（chiqui7，ORT 1.30.0）vs 本次 DML 声明，两代同 imgsz 使 4.4x/42x 无 letterbox 混杂（report §1/§5）。
- **P3-1（闭合）**：recall-report §4 补 tile 路由对 BJ13 不可适用（aspect 1.41 不满足宽≤690 且 aspect≥8.0 谓词，谓词属冻结域）——不列为选项。
- **P3-2（闭合）**：recall-report §6 加 limitation 6：BJ06 对照 8 region 为 chiqui7 自证清单（无独立 GT，沿 DOMAIN-EXT-DIAG 已登记限制）——「域内锚定」证明的是生产链等价性而非独立召回 GT。
- **P3-3（闭合）**：recall-report §1 补两点探针口径差异：①conf 过滤次序（probe 先 0.01 再分 rung vs 生产单次阈值；对 ≥0.5 子集数学等价，G7 逐框对位实证）；②probe 取模块常量 `SFX_CONF_THRESHOLD` 不读 `NEWMANGA_SFX_CONF_THRESHOLD` env（本 Task 未设该 env，实际一致）。
- **P3-4（闭合）**：见上「base_commit 对账」段。
- **P3-5（闭合）**：r1fix 重跑探针落 `verification/M2-SFX-BJ13-RECALL-1/raw/recall-probe-run-r1fix.log`（头部含 date/命令行/venv/Python/runtime/worktree，EP provenance 与 EXIT=0 在正文——N-3 措辞收窄）+ `raw/r1fix/recall-probe.json`（原 raw 零触碰）——与原 run json **全树逐位一致**（排除时间戳/耗时字段后 0 diff；四页读数 5/1/0/1、BJ06 max 0.8732、BJ13 ref1 峰值 0.3727 全部相同）。同形态 DML→DML run-to-run 确定性互证成立（同形态逐位，非跨形态声明）。
- **P4-1（登记不改动）**：probe `relabels` 按「相交对数」vs 生产按「primary 候选数」——当前四页全 0 无影响，口径注记已在 report §3 模拟段语义中隐含；如未来出现非零改标，以生产 `detection_sfx.py:1359-1368` 口径为准。
- **P4-2（登记不改动）**：probe 恒走 letterbox 未自证路由谓词——四页 page_w=2946>690 必为 letterbox，结论不受影响。
- **P4-3（闭合）**：「两代权重域内一致性」→「两代权重在该区（DOMAIN-EXT-DIAG 判定域外页 BJ13）判定一致」（report §2 + 本执行记录段）。
- **P4-4（闭合）**：report §2 BJ06 段「小框 87×103」限定为仅 b5b747d0 成立。
- **P4-5（闭合）**：Task AC1/纪律段与 Handoff 页图位置措辞更正为 peer worktree `test_assets/comic_golden_suite/日漫_JA/01_black_jack_official/`（该目录 `.gitignore:26` 忽略，零入库结论不变）。
- **P4-6（闭合，随 P2-1）**：report §5 补 4.4x/42x 属 CPU（chiqui7）↔ DML（v2b）跨形态比较的显式声明（量级远超 ≤2e-06 漂移窗口，结论不受影响；跨形态仍禁写位级可复现）。
- **P4-7（闭合）**：report §2 补登类别翻转证据：同像素 chiqui7 text 0.5195/sfx 0.0855 → v2b sfx 0.3727/text 0.0（sfx/text 排序翻转，比比值更直接支持域适应起效）。
- 返修 commit：`fix(review)`（本文件与 report/Handoff/r1fix 证据同 commit；hash 见 git log）。Task status 保持 in_review（返修后待 DSH r2 或集成方按 r1 条件闭合清单收口）。

### r2 定点复审（DSH 非作者 2026-10-06：**approved**，报告=doc/reviews/M2-SFX-BJ13-RECALL-1-04d5f621-dsh-r2.md）

- r1 三项集成条件 C1（=P2-1 imgsz 1024）/C2（=P3-4 base 对账）/C3（=P3-2+P3-3 登记）与顺笔 P3-1/P3-5/P4-3/4/5/6/7 逐条 CLOSED；P4-1/P4-2 登记核验成立；措辞纪律合规（同形态逐位互证未外溢跨形态）。
- r1fix 证据独立核验：ref/reflog 锚定 tip 04d5f621；两份 json 逐行比对仅 generated_at_utc/inference_s 两字段差；原 raw 零触碰经 mtime 序取证成立；fix 触碰面全在允许路径。
- 集成收口顺笔：N-1（证据清单枚举补 r1fix 两文件）/N-2（log:5 指代限定）/N-3（头部措辞收窄）三文案项随收口 commit 闭合；N-4/N-5/N-6 登记不动作。post-merge main 回归=1840 passed+1 skipped+1 failed（test_catalog 既有 BASELINE_FAILURE）与 merge 前基线逐项等量（零 src 符合预期；log=raw/main-regression-postmerge.log，跑 env=T1.1.1-impl-py312 venv）。AC2 提案（维持 0.90）与 AC3 推荐序（③②①）**双分支呈报用户裁决**（r2 §5.1，不由集成方代取其一）。
