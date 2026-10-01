---
task_id: M2-SFX-DETECT-EVAL
author: ZCode
recipient: Codex（integrator 代行）；reviewer=DeepSeek Harness（非作者）
base_commit: a9b054e8
delivery_head: d5bfd1fe（implement=评估产物+报告；本 handoff 与 Task/STATUS 回填为其后的收尾 commit）
status: in_review
---

# Handoff：M2-SFX-DETECT-EVAL（SFX 拟声词检测能力评估，评估先行、生产零改动）

## 交付结果

三问评估完成（**全程 directional 口径**：单 AI 标注者、无正式 SFX GT、n=23 帧——本 handoff 与报告的任何数字都不得以「确认/达标」强度引用）：

1. **现状（ogkalu 基线）=不稳定且不可区分**。23 主样本帧（29 SFX 实例，分层采样：11 帧 C1 用户审定 + 12 帧盲区导向新增）上：conf≥0.5 帧级检出率 **12/23=52.2%**（检出且框住 10 + 检出但偏移 2）、conf≥0.25 **16/23=69.6%**、**硬盲区 7 帧**（0.25 仍零检出）。C1 证据全部复现（6 个检出盲区 FP + 4 个零检出帧）；新增量化：SFX 分数系统性贴着 0.5 阈值分布（싸—아 0.5475 / 빠걸 0.48 / 수악 0.28…），「检出 vs 零检出」本质是阈值切分；检出后无法路由（끼아아악 被标 text_bubble 等）。
2. **方案=有方向性可行信号，无即取即用候选**。5 候选登记：`chiqui7/yolo11-manga-seg`（HF MIT 标签，**唯一有独立 sfx 类** `{0:bubble,1:panel,2:sfx,3:text}`）在 **ogkalu 的 7 个硬盲区帧中 6 帧有 sfx 类真命中**（투두 0.95 / 콰직 0.76 / 철컹 0.82 / 빠직 0.95 / 송송 0.68 等，directional）；但类内混淆（하하/철컥철컥/뒤적뒤적→text）、手部误报（0.55）、训练数据未登记、**Ultralytics AGPL-3.0 权重许可主张 vs HF 标签冲突**四项缺口真实存在。`Kiuyha/Manga-Bubble-YOLO` **NO-GO**（ONNX 元数据单类 `{0:'text'}` 无 SFX——前提不成立；同 AGPL 冲突）；`cozy-creator/manga-sfx-detector` NO-GO（无许可/零来源链）；`dmMaze/comic-text-detector` NO-GO（T1.1.1 GPL-3.0 先例）。Manga109-s 许可传导**可满足**（商用 ML 结果允许+署名条件；数据集本体禁再分发）。
3. **集成路径=策略门已就绪、缺口在检测/分类**（只读核实：`RegionType.SFX` `src/domain/regions/entities.py` L25、`SfxPolicy` skip/translate/manual L48-53、`decide_sfx_translation` `src/application/translation/context/gate.py` L32-42）。三条路径草案：**A** 独立 SFX 检测器（盲区互补）/ **B** 现有检测器+后分类器（硬盲区救不回）/ **C** 用户手动标记（零模型风险兜底，UI 属 React Task）。**集成前条件 5 项**：正式 SFX GT 重标注+用户逐条审核、许可裁决（Ultralytics AGPL 争议=用户裁决项）、域验证扩展、另行释放 Task、类内混淆合并规则设计。

**产品裁决提醒**：「SFX 检测可行吗、用哪条路径」由用户基于报告裁决；本 Task 只提供方向性证据与路径草案。生产 `src/**`/requirements/contracts 零改动（AC5 专项 diff 核实）。

## 证据物（全部入库，weight 与预览除外——gitignored task-env 树）

| 证据物 | 位置 |
|---|---|
| 评估报告（唯一结论源） | `verification/M2-SFX-DETECT-EVAL/sfx-detect-eval-report.md` |
| 采样候选（44 单元，种子 20261001） | `experiments/M2-SFX-DETECT/sfx-sample-candidates.json` |
| ogkalu 采样推理（43 区域全检出，权重 sha pin） | `experiments/M2-SFX-DETECT/ogkalu-sfx-frames.json` |
| 视觉判定（23 主帧逐帧判定+依据+29 实例框；44 单元全量留档） | `experiments/M2-SFX-DETECT/sfx-spot-check-verdicts.json` |
| ONNX 推理（chiqui7/Kiuyha 23 帧 + 许可门发现） | `experiments/M2-SFX-DETECT/onnx-sfx-frames.json` |
| 跨模型几何对照（29 实例） | `experiments/M2-SFX-DETECT/onnx-sfx-comparison.json` |
| 脚本 ×5（C4 基座 import 复用零改动） | `experiments/M2-SFX-DETECT/{build_sfx_sample,eval_sfx_ogkalu,summarize_sfx_verdicts,eval_sfx_mangabubble,summarize_onnx_comparison}.py` |
| 预览（grid 锚定，不入库） | `task-envs/M2-SFX-DETECT/previews*/`（ogkalu 43 张 + onnx 23 张） |
| 权重（不入库，sha256 pin 于报告 §3.1） | `task-envs/M2-SFX-DETECT/weights/{yolo11s-seg,yolo26n}.onnx` |
| 释放证据 | `verification/M2-SFX-DETECT-EVAL/release-a9b054e8.md`（零改动） |

## 纪律自检（AC5，全过）

- `git diff --name-only 02bf68a0..HEAD` = `doc/tasks/M2-SFX-DETECT-EVAL.md` + `experiments/M2-SFX-DETECT/**`（10 文件）+ `verification/M2-SFX-DETECT-EVAL/sfx-detect-eval-report.md`；禁改路径（src/requirements/contracts/apps/packaging）触碰 **0**。
- `git diff --check 02bf68a0..HEAD` **EXIT=0**；工作树 porcelain **0**。
- 权重零 tracked（`git ls-files` 无 onnx/pt/safetensors/bin）；C1/C4 产物零改动（只读引用）。
- pytest 三套件（主 venv `T1.1.1-impl-py312`）：providers **291 passed + 1 skipped** / m2_acceptance **35 passed** / core **111 passed** = **437+1skipped 0 failed**（基数与 M2-PROD-DETECT-3 后 main 基线一致）。
- 环境披露：C4 GPU venv（`task-envs/M2-DOCTR-QUAL-C4-gpu-py312`）内新装 `onnxruntime` 1.30.0（CPU provider，评估专用，不影响生产 requirements）。

## 已知限制（Review 重点；引用时不得省略）

1. directional 口径（单 AI 标注者、锚定未测量、SFX 框为 grid 锚定视觉估计）。
2. n=23 帧/29 实例、KO webtoon 10 case 内、采样盲区导向（A 层 SFX 富集）——检出率**不是**全页随机口径。
3. chiqui7 训练数据未登记；conf 分布宽（0.27-0.97），阈值敏感性大。
4. onnxruntime CPU 与潜在生产 GPU 路径数值差异未测。
5. 许可结论基于 HF 卡/ONNX 元数据/官方许可页的一手文本，非法律意见；Ultralytics AGPL 权重主张为**争议项**，集成前须用户裁决。

## 下一任务建议（§5.1 字段）

> 下一任务建议不等于任务释放；是否推进、走哪条路径由用户裁决（报告 §4.4 集成前条件）。

1. **Task**：用户裁决项（非新 Task 释放）——阅读 `verification/M2-SFX-DETECT-EVAL/sfx-detect-eval-report.md` 后裁决：①是否接受「SFX 检测方向可行」的 directional 结论进入下一阶段；②许可路径三选一（接受 Ultralytics AGPL 风险 / 企业许可 / 非 Ultralytics 模型或自训）；③选择集成路径 A/B/C 或维持现状（路径 C 与 A/B 可叠加）。若用户裁决继续：候选 Task 形态=「SFX 正式 GT 重标注（用户审核流程，C1 先例）」或「SFX 检测集成（检测+分类+契约扩展，须 Codex 范围裁决）」，均须先由 Codex 在 STATUS 登记 proposed→ready。
2. **Agent**：GT 重标注流程=ZCode（汇总脚本+流程）+用户（判定权威），Reviewer=DSH；集成 Task=Codex 契约裁决+ZCode/Antigravity 实现；路径 C 的 UI=Qoder。
3. **Recovery point**：本 Task 分支 `agent/zcode/M2-SFX-DETECT-EVAL`（worktree `G:/CODEX/New Manga.worktrees/M2-SFX-EVAL-zcode`），base=`a9b054e8`，delivery_head=`d5bfd1fe`（+收尾 commit）；未 push、未 merge，待 DSH Review 与代行 Codex 集成。
4. **Scope**：评估类 Task 已收口；任何后续 Task 的允许路径由 Codex 释放时登记（检测集成必然涉及共享契约/Schema，需明确授权）。
5. **Deliverables**：如上证据物表；无生产代码交付（生产零改动为本 Task 的验收项而非缺口）。
6. **Verification**：Review 复核命令见报告 §6（全部可复制复跑）；纪律四项命令见上文自检节。
7. **Forwardable instruction**（若用户裁决进入 GT 重标注）：「Task=SFX 正式 GT 重标注（候选），Owner=ZCode，Reviewer=DSH，base=集成后 main，worktree 待 Codex 创建；范围=标注协议+worksheet+汇总脚本+用户审核流程（C1 阶段二先例），SFX 框以本报告 29 实例视觉框为起点在完整 case 集上重标注；禁止 src/contracts 改动；验收=用户逐条审核完成+汇总脚本 EXIT=0+方向性报告。」

## Review 提醒

- 报告 §3.3 的 chiqui7 类内混淆与误报清单、§5 Known limitations 7 项、§0 结论速览的强度措辞（「方向性可行信号」而非「可行」）是本次 Review 的核心校验点。
- 复算入口：报告 §6 五条命令逐一可复跑；`summarize_sfx_verdicts.py` 内嵌视觉判定表逐条可核对（预览在 task-env 树）。
