---
id: M2-SFX-TRAIN-V1
title: "SFX 训练 V1（T2）：A′ 路线首训——challenge 划拨重切+yolo11s-seg 微调+导出冒烟+directional 评测"
kind: feature
status: in_review
owner_claim: 2026-10-04 by zcode subagent @45ae05a4（AC1）+ @5fe62a91（AC2）+ @c89c85e2（AC3/AC4；docs 收尾轮报告/Handoff/本回填随 docs 提交）
approval: user_ruling_2026-10-04_按推荐_直接训V1+划拨challenge
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权）
depends_on: [M2-SFX-ANNOTATE-R2, M2-SFX-DATA-INFRA, M2-SFX-FINETUNE-PREFLIGHT]
base_commit: a85d8853
branch: agent/zcode/M2-SFX-TRAIN-V1
worktree: G:/CODEX/New Manga.worktrees/M2-SFX-TRAIN-V1-zcode
review_events: []
created: 2026-10-04
---

# Task: M2-SFX-TRAIN-V1 — SFX 训练 V1（T2，A′ 路线首训）

## 背景与目标

T1b-R2（done @merge `84f952b3`）交付了首个含 BJ 毛笔竖排正样本的训练集（train 345/571=324 合成+21 真实；BJ 正集 5 页 11 框）。用户裁决（2026-10-04「按推荐」）：

1. **①(a) 直接训 V1**：训练便宜（分钟级），先训一版验证训练管线端到端+看 KO 域指标不回退与 BJ 域定性改善；BJ 深度靠后续扩标轮补。
2. **②(a) 划拨 challenge**：BJ16-25 判定页整组划出训练集作挑战评测集，解决 challenge 空集（G1 BJ 门考卷）。

**V1 定位=管线验证+directional 评测，不是正式 G1-G8 Gate**（那是 T3，待 BJ 深度扩标后）。

## 裁决落地参数

- **challenge 划拨=densho810/vol05 整组**（组不跨集硬约束）：BJ17（vol05_p0167，竖排假名 2 框，主攻形态）+BJ18（vol05_p0065，粗毛笔 3 框）= **5 框考卷**；train 留 densho810/vol01（BJ16×3+BJ22 零框负证据）+vol03（BJ23×2+BJ24×1）=6 框真实正样本。理由：考卷必须覆盖主攻形态（竖排）；train 影响由 324 合成兜底。
- Owner 有等价裁量权（如 vol03 组），但**必须在报告登记选组理由+形态分布对照**。

## 交付物（阶段化）

- **AC1 数据准备（challenge 划拨重切）**：准备脚本（experiments/M2-SFX-TRAIN-V1/）读 R2 manifest（只读引用 `G:/CODEX/New Manga.worktrees/M2-SFX-ANNOTATE-R2-zcode/training_data/sfx-v1/annotate-r2/preannotate/manifest.r2.json`，82 样本）+R2 synthetic manifest（324）→ 重新 assign_splits：`densho810/vol05` 组→challenge、seed=20261004 冻结沿 R1/R2 口径、组隔离 0 违例断言、names 逐字=SFX_CLASS_MAP 双通道校验、dataset.yaml 本轮 challenge 非空可写 challenge 键（断言 ultralytics 可扫描）。产物 `training_data/sfx-v1/train-v1/dataset/`（gitignored）+摘要（Git 内）。**期望**：train≈343（19 真实+324 合成）/val 4/test 2/challenge 2 页 5 框——以脚本实测为准如实登记。
- **AC2 训练 V1**：Ultralytics 官方 `yolo11s-seg.pt` 基座（AGPL，用户许可降权备案覆盖），训练参数沿 T0 实测口径（imgsz 沿 T0 冒烟、batch≤8 显存 7488MiB 内、epochs 100-150+早停 patience、seed=20261004 冻结、单 GPU）。环境 venv=M2-SFX-FINETUNE-gpu-py312。训练曲线/最终指标（box/seg mAP50/PR）落 verification。**小数据预期管理**：345 样本训练 mAP 数字本身不作门判定，只作 V1↔V2 对比基线。
- **AC3 导出+生产序列冒烟（零 src）**：best.pt→ONNX 导出（T0 已验证链路）→沿 T0 方式 `_build_engine` 进程内重指冒烟（SHA 门先证在位；**不改 src/、不换生产 pin**——生产切换是 T4 用户裁决）。冒烟 EXIT=0+对 BJ17 页做一次真实推理演示（新模型在主攻形态上的原始输出）。
- **AC4 directional 评测**：
  - **BJ challenge（主考卷）**：新模型对 BJ17/BJ18 两页 5 框 GT 的召回（conf≥0.50 沿生产冻结口径+conf 0.2 宽松口径各报一版；IoU≥0.5 匹配）；**对照组=chiqui7 现役模型同页同口径**（R2 预标注 conf≥0.2 的检出已存在可直接引用）。
  - **KO 不回退**：val（4 样本 53 框）+test（2 样本 5 框）上新模型 vs chiqui7 同口径对比——**统计功效低，仅 directional**，结论措辞禁用"显著"。
  - 结论模板：BJ 召回 X/5（chiqui7 Y/5）+KO 差值——如实报数含失败形态。
- **AC5 报告与裁决呈报**：verification/M2-SFX-TRAIN-V1/train-v1-report.md（数据/训练/评测/诚实边界：BJ train 剩 6 框量级仍小、KO val 功效低、V1 不承诺 Gate）；Handoff（DSH 审查入口）；Task 回填；**T3/T4 呈报材料**（下一轮扩标候选：BJ conf<0.2 层 16 单元+44 张候选池页+Ko 扩标池 10 张；T4 生产切换条件清单）。

## 验收判据

AC1：重切指纹一致可复现+组隔离 0 违例+challenge 5 框逐框可溯源到 R2 判定链。
AC2：训练 EXIT=0+曲线完整+最终权重 sha256 登记。
AC3：ONNX 导出+`_build_engine` 冒烟 EXIT=0（零 src 实证）+BJ17 推理演示产物。
AC4：BJ challenge 召回数字（双口径）+chiqui7 对照+KO 差值，全部如实（0 也如实）。
AC5：三文档齐+T3/T4 呈报材料。

## Acceptance Criteria

- [x] AC1 challenge 划拨重切（vol05 组整组+组隔离 0 违例+names 双通道+challenge 键可扫描）——底册=R2 final 351 只读重切：densho810/vol05 组整组 train→challenge（pre-bj17 竖排主攻 2 框+pre-bj18 粗毛笔 3 框=5 框考卷，逐框溯源 R2 判定链 conf 0.8333–0.932 全 confirm、BJ17-B02 仲裁 delete 排除留痕核对），其余逐样本保持 R2 出厂 split；train 345→343（324 合成+19 真实，剩 BJ 6 框=BJ16×3+BJ23×2+BJ24×1）/val 4/53、test 2/5 逐样本不变；组隔离全量 351 group→split 重算 0 违例；names=SFX_CLASS_MAP 双通道 PASS（detection_sfx.py:137）+ultralytics 8.4.172 check_det_dataset 扫描 PASS（challenge 键在位 2 图可扫描）；指纹 badb0605…（seed=20261004 冻结，T1a 工具零重写复用）复现一致；label 351 全量与 R2 树逐字节一致+sha256 三方抽验 13 张（BJ 5 页必验）@45ae05a4
- [x] AC2 训练 V1（A′ 基座+seed 冻结+曲线完整）——官方 yolo11s-seg.pt 基座 sha256 1caa81c0…257c3（T0 指路在盘复用未下载，训练前自检通过）+kwargs 全沿 T0 口径（imgsz 1024/batch 8/workers 2/epochs 150/patience 30/seed 20261004/device 0）；EXIT=0 单次运行无 OOM（6.45G，T0 7488MiB 口径内，减半重试未触发）；实际 116/150 epochs patience=30 早停（best epoch 86）、耗时 868.8s @RTX 5070 Ti；best.pt（epoch 86，20,585,636 B）sha256 f212bfc6…26740 登记；results.csv 末行 box P 0.24725/R 0.03774/mAP50 0.00875/mAP50-95 0.00535（seg 同值）；final val（4 图 53 sfx）Box/Mask P 0.482/R 0.0189/mAP50 0.0158/mAP50-95 0.0123；小数据预期管理：数字仅作 V1↔V2 基线不作门判定，低数字如实登记不凑数 @5fe62a91
- [x] AC3 导出+生产序列冒烟（零 src+_build_engine 重指+BJ17 推理演示）——best.onnx fb60b460…329f6（40,824,255 B）；SHA 门先证在位（直载=PROVIDER_FAILED 正确命中）→进程内重指全链 EXIT=0（names metadata 逐字 SFX_CLASS_MAP+imgsz 1024 metadata_parsed+(1,40,21504) 张量+合成页双档 conf 结构合法）；零 src、生产 pin d87389af…（detection_sfx.py:110）零改动；BJ17 真实页推理演示落 raw/bj17-demo.json（conf 0.5=0 检出/conf 0.2=1 检出 0.2049）@c89c85e2
- [x] AC4 directional 评测（BJ challenge 双口径召回+chiqui7 对照+KO 不回退检查）——BJ challenge 考卷（5 框，IoU≥0.5 贪心）：新模型严格 conf≥0.50=0/5（0 检出，BJ17 竖排主攻形态零检出）/宽松 conf≥0.20=1/5（3 检出 P=0.333，唯一匹配 R2-BJ18-B00 IoU 0.606@conf 0.343）vs chiqui7 双口径 5/5（6 检出 P=0.833，唯一 FP=仲裁 delete 的 B02 气泡框）；KO 不回退：KO 页 4 样本 56 框新模型严格/宽松均 0/56（零检出）vs chiqui7 严格 56/56（P=0.824）/宽松 56/56（P=0.667），全 6 样本 58 框新模型宽松 0/58——**回退如实登记**；imp-ogkalu-* 2 样本（2 框）chiqui7 预标注不可得（预标注源=ogkalu rt-detr）如实登记；统计功效低禁用「显著」，结论与 343 样本+COCO 基座无 manga 先验+欠拟合（val R=0.019）一致 @c89c85e2
- [x] AC5 报告+Handoff+Task 回填+T3/T4 呈报材料——verification/M2-SFX-TRAIN-V1/train-v1-report.md（数据/训练/评测/DSH 独立复核 PASS 四项+3 条非阻塞观察项/诚实边界：BJ train 剩 6 框量级小+KO val 功效低 directional+V1 不承诺 G1-G8 Gate+AGPL 备案在案；§7=T3 前置 BJ 深度扩标候选（conf<0.2 层 16 单元+44 张 BJ 候选池页+10 张 KO 候选）与 T4 生产切换条件清单（含 best.onnx 与生产 pin 替换语义））+doc/handoffs/M2-SFX-TRAIN-V1-zcode-20261004.md（DSH 审查入口）+本 Task 回填（docs 提交）
- [x] AC6 零 src；训练数据/权重 gitignored 外部树；Git 只进摘要——git diff --name-status a85d8853..HEAD 仅 11 文件全在 Task 允许范围；`-- src/` 空 diff 0 提交；生产 pin d87389af… 在 HEAD/base/main 三处 git show 同值；dataset.yaml/best.pt/best.onnx 均命中 .gitignore:13 '/training_data/'（*.pt/*.onnx 8-10 行双保险）；Git 只进摘要+日志（DSH 独立复核四项 PASS 实证，报告 §5）

## 允许修改范围

`experiments/M2-SFX-TRAIN-V1/**`（新建）、`verification/M2-SFX-TRAIN-V1/**`、本 Task/Handoff、`training_data/sfx-v1/train-v1/**`（gitignored：数据集/权重/ONNX/训练 run 产物）。

## 禁止范围

`src/**`、`tests/**`、`doc/contracts/**`、`packaging/**`、`apps/**`、`doc/STATUS.md`、R1/R2 数据本体与脚本（只读引用）、cases.json（本轮不动素材登记）、生产权重 pin（detection_sfx.py SHA 门零改动）。

## 依赖、风险与阻塞

- depends_on 全 done。风险：①小数据过拟合（345 样本）——早停+与 V2 对比口径登记；②seg 分支在小样本上 mask 质量可能差——评测以 box 召回为主、seg 定性；③GPU 显存/驱动波动——沿 T0 实测 b8 安全；④val/test KO 功效低——directional 措辞纪律。
- 裁量点：challenge 组选择等价替换须登记理由；epochs/早停参数微调登记。

## 交付与运行记录

- **AC1 数据准备轮（2026-10-04，@45ae05a4）**：challenge 划拨重切+train-v1 数据集重建（零 src）。densho810/vol05 组整组 train→challenge（用户裁决 ②(a)），train 345→343/val 4/test 2/challenge 2 页 5 框；组隔离 0 违例、指纹 badb0605… 复现一致、names 双通道+ultralytics 扫描 PASS、label 351 全量与 R2 树逐字节一致；honest note：BJ22=pseudo 候选 2 框未入判定（非零框）/BJ25=pseudo 零框负证据，均不入 351。证据：prepare-summary.json+manifest.train-v1.json（artifacts sha256 e454429a…）。
- **AC2 训练轮（2026-10-04，@5fe62a91）**：yolo11s-seg 微调，116/150 epochs 早停（best epoch 86），868.8s @RTX 5070 Ti，EXIT=0 无 OOM；best.pt sha256 f212bfc6…26740；final val Box/Mask P 0.482/R 0.0189/mAP50 0.0158/mAP50-95 0.0123（results.csv 末行 P 0.24725/R 0.03774/mAP50 0.00875/mAP50-95 0.00535）；train-log.txt 923KB 全程 stdout 入 Git。数字仅作 V1↔V2 基线不作门判定。
- **AC3/AC4 评测轮（2026-10-04，@c89c85e2）**：ONNX 导出+SHA 门（PROVIDER_FAILED 正确命中）+进程内重指生产序列冒烟 EXIT=0（零 src，pin d87389af… 零改动）+BJ17 真实页演示；BJ challenge 考卷新模型 0/5（严格）·1/5（宽松）vs chiqui7 5/5 双口径；KO 页 4 样本 56 框新模型 0/56 双口径 vs chiqui7 56/56——回退如实登记，V1=管线验证，全面低于 chiqui7 现役为 343 样本小数据的预期结果。
- **文档收尾轮（2026-10-04，docs 提交）**：`verification/M2-SFX-TRAIN-V1/train-v1-report.md`（全部数字从盘上产物复算）+ `doc/handoffs/M2-SFX-TRAIN-V1-zcode-20261004.md` + 本 Task 回填（status=in_review，AC1-AC6 勾选）。
- **独立复核**：DSH = **PASS**（重切正确性/训练真实性/评测复算/零 src 实证四项全过；3 条非阻塞观察项：.bak 残留可清理、EXIT 证据在 export-smoke-v1.json 的脚本设计差异、本报告补齐 AC5 时点缺项）——见报告 §5。
- 报告：[verification/M2-SFX-TRAIN-V1/train-v1-report.md](../../verification/M2-SFX-TRAIN-V1/train-v1-report.md)；Handoff：[doc/handoffs/M2-SFX-TRAIN-V1-zcode-20261004.md](../handoffs/M2-SFX-TRAIN-V1-zcode-20261004.md)；摘要：verification/M2-SFX-TRAIN-V1/prepare-summary.json；raw：train-log.txt/export-smoke-v1.json/bj17-demo.json/eval-challenge.json/eval-kodelta.json。
- **T3/T4 呈报（交编排/用户裁决，不随本 Task 释放）**：T3 前置=BJ 深度扩标候选（conf<0.2 层 16 单元+44 张 BJ 候选池页+10 张 KO 候选；V1 失败形态佐证=竖排主攻形态零检出而粗毛笔有低置信响应，样本量为首要瓶颈）；T4=生产切换条件清单（质量门/正式 Gate/链路门/生产 pin 替换语义/AGPL 复核/用户裁决）——报告 §7。

## Review

-（待 DSH review 轮回填）
