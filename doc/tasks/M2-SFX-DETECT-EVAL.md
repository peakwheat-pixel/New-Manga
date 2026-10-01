---
id: M2-SFX-DETECT-EVAL
title: "SFX 拟声词检测能力评估（用户产品裁决 2026-10-01 推进候选 2；评估先行纪律，生产零改动）"
kind: experiment
status: in_progress
approval: user_directive_2026-10-01_option2
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权+自治授权）
depends_on: [M2-PROD-DETECT-3]
base_commit: a9b054e8
branch: agent/zcode/M2-SFX-DETECT-EVAL
worktree: G:/CODEX/New Manga.worktrees/M2-SFX-EVAL-zcode
---

# M2-SFX-DETECT-EVAL：SFX 拟声词检测能力评估

## 来源与目标

- 来源：用户在 REBASELINE 第四轮盘点后从三个候选中裁决**「2. SFX 拟声词检测」**（2026-10-01）。C1 审计裁定：「SFX/屏幕小字检测若产品要支持需另立任务（涉及伪 GT 体系重标注，超出检测器范畴）」；现状=ogkalu 模型对 SFX 检出不稳定（抽检 6 个 SFX 检出计盲区 FP + 4 帧零检出），且检出后无法区分为 SFX。
- 目标：回答「**SFX 检测在本项目（KO webtoon 域）可行吗、用什么方案、怎么接进产品**」——产出可复核的评估报告，**生产 src/requirements/contracts 零改动**（评估先行纪律，同 C4 先例）。产品集成属后续 Task，须凭本报告另行释放。

## 释放侦察事实（已核实）

1. **产品面 SFX 策略门已存在**（Legacy TASK-032/035 done）：`region_type == sfx` 前置 + `SfxPolicy`（skip/manual/translate）+ `decide_sfx_translation` 判据——检出后只要 region 标记为 sfx 类型，管线差异化处理即生效。缺口在**检测/分类**，不在策略门。
2. **候选生态（2026-10-01 WebSearch 调研）**：
   - dmMaze/comic-text-detector：**GPL-3.0**（GitHub 与 HF 镜像 mayocream/comic-text-detector 双证）→ 沿用 T1.1.1 NO-GO 先例（除非用户推翻），登记不评估。
   - Kiuyha/Manga-Bubble-YOLO：HF ONNX 模型，训练于 hal-utokyo/Manga109-s（5,595 图），SFX 类存在性/许可待核查——**首要候选**。
   - ogkalu（现役生产模型）：无独立 SFX 类，text_free 类部分覆盖（现状基线）。
3. **域适配风险**：Manga109-s=日本印刷漫画，KO webtoon=韩漫长条——C4 教训（docTR 文档域权重在韩漫 FAIL）提示 SFX 模型的域表现是评估核心，不能只看模型卡。
4. **GT 现状**：KO webtoon GT 无 SFX 标注（盲区）；正式重标注超出本 Task（登记为集成前条件）。评估用 **directional 口径**（agent 视觉预判 + 双重抽检 + 证据公开，非正式判定——C1 授权先例的自治适配）。
5. C4 评测基座（`experiments/M2-DOCTR-QUAL/eval_detection_manga.py`）与 KO 素材/权重快照可复用（只读）。

## 设计决策（代理裁决）

1. **评估域=KO webtoon 素材**（生产域优先；Manga109-s 域对照仅作模型原生能力参考，不作为 PASS 依据）。
2. **许可门先行**：Manga-Bubble-YOLO 的 HF 模型卡许可 + Manga109-s 数据集许可传导核查——任一与生产使用冲突（如禁商用/禁再分发权重）即登记 NO-GO 转「仅现状基线+集成路径建议」的缩水交付（合法分支）。
3. **现状 SFX 抽检**：从 KO 素材抽样（≥20 帧含 SFX 的区域，agent 视觉预判标注 SFX 位置与 ogkalu 检出对照；directional 口径、样本与预判 JSON 全部入库可复核；正式用户审核登记为集成前条件）。
4. **生产零改动**：experiments/M2-SFX-DETECT/** + verification/M2-SFX-DETECT/** + Task/Handoff；新模型权重 gitignored 外部路径；隔离实验环境（可复用 C4 GPU venv 模式）。

## Acceptance Criteria

- [ ] AC1（候选调研报告）：≥3 候选登记（comic-text-detector NO-GO 证据链 / Manga-Bubble-YOLO / ogkalu 现状 + 如有其他补充）；每候选：许可/域/类别面/契约适配度/结论。
- [ ] AC2（现状基线）：ogkalu 在 KO 素材的 SFX 检出对照抽检（≥20 帧，样本+预判+检出坐标入库）；C1/C4 既有证据引用汇总。
- [ ] AC3（Manga-Bubble-YOLO 评估）：许可核查结论 → 通过则下载权重（sha256 登记）+ KO 素材推理（SFX 类输出）+ 与现状基线对照（检出数/位置合理性抽检）；NO-GO 则登记证据。
- [ ] AC4（评估报告）：可行性结论（directional 明示）+ 方案对照表 + **集成路径草案**（检测/分类 → region sfx 类型 → SfxPolicy 门；正式 GT 重标注与用户审核列为集成前条件）。
- [ ] AC5（纪律）：生产面零改动专项 diff；权重零入库；`git diff --check` EXIT=0。

## 允许/禁止

允许：`experiments/M2-SFX-DETECT/**`（新增）、`verification/M2-SFX-DETECT/**`、Task/Handoff。禁止：`src/**`、`requirements.txt`、contracts、`apps/**`、`packaging/**`、C4/C1 产物改动（只读引用）、权重入库。

## 依赖、风险与阻塞

- 依赖：M2-PROD-DETECT-3 done（评测基座与素材就绪）。
- 风险：①Manga-Bubble-YOLO 许可 NO-GO → 缩水交付分支；②韩漫域表现差 → 结论如实（「现状不可行」也是有效评估结论）；③SFX 预判无正式 GT → directional 口径全程明示。
- 阻塞：无。

## Claim 记录（Owner=ZCode，2026-10-01）

status ready→in_progress；base=`a9b054e8`（delivery base=`02bf68a0`，release 证据 `verification/M2-SFX-DETECT-EVAL/release-a9b054e8.md`）；branch=`agent/zcode/M2-SFX-DETECT-EVAL`，linked worktree `G:/CODEX/New Manga.worktrees/M2-SFX-EVAL-zcode`。范围按 AC1-AC5 冻结：`experiments/M2-SFX-DETECT/**`、`verification/M2-SFX-DETECT/**`、Task/Handoff；`src/**`、requirements、contracts、apps/**、packaging/** 零改动；C4/C1 产物只读；权重不入库。许可门先行：Manga-Bubble-YOLO 许可 NO-GO 即走缩水交付分支（仅现状基线+集成路径建议）。
