---
id: M2-SFX-TRAIN-V1
title: "SFX 训练 V1（T2）：A′ 路线首训——challenge 划拨重切+yolo11s-seg 微调+导出冒烟+directional 评测"
kind: feature
status: ready
owner_claim: —
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

- [ ] AC1 challenge 划拨重切（vol05 组整组+组隔离 0 违例+names 双通道+challenge 键可扫描）
- [ ] AC2 训练 V1（A′ 基座+seed 冻结+曲线完整）
- [ ] AC3 导出+生产序列冒烟（零 src+_build_engine 重指+BJ17 推理演示）
- [ ] AC4 directional 评测（BJ challenge 双口径召回+chiqui7 对照+KO 不回退检查）
- [ ] AC5 报告+Handoff+Task 回填+T3/T4 呈报材料
- [ ] AC6 零 src；训练数据/权重 gitignored 外部树；Git 只进摘要

## 允许修改范围

`experiments/M2-SFX-TRAIN-V1/**`（新建）、`verification/M2-SFX-TRAIN-V1/**`、本 Task/Handoff、`training_data/sfx-v1/train-v1/**`（gitignored：数据集/权重/ONNX/训练 run 产物）。

## 禁止范围

`src/**`、`tests/**`、`doc/contracts/**`、`packaging/**`、`apps/**`、`doc/STATUS.md`、R1/R2 数据本体与脚本（只读引用）、cases.json（本轮不动素材登记）、生产权重 pin（detection_sfx.py SHA 门零改动）。

## 依赖、风险与阻塞

- depends_on 全 done。风险：①小数据过拟合（345 样本）——早停+与 V2 对比口径登记；②seg 分支在小样本上 mask 质量可能差——评测以 box 召回为主、seg 定性；③GPU 显存/驱动波动——沿 T0 实测 b8 安全；④val/test KO 功效低——directional 措辞纪律。
- 裁量点：challenge 组选择等价替换须登记理由；epochs/早停参数微调登记。

## 交付与运行记录

-（待 Owner 回填）
