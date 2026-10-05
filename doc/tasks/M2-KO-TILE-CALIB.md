---
id: M2-KO-TILE-CALIB
title: "KO 长条页推理口径校准实验（T3 前置）：tile 切块 vs 整页 letterbox 对照+口径建议固化"
kind: experiment
status: ready
owner_claim: —
approval: user_ruling_2026-10-05_按推荐_T3释放
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权）
depends_on: [M2-SFX-TRAIN-V2]
base_commit: 9258afc0
branch: agent/zcode/M2-KO-TILE-CALIB
worktree: G:/CODEX/New Manga.worktrees/M2-KO-TILE-CALIB-zcode
review_events: []
created: 2026-10-05
---

# Task: M2-KO-TILE-CALIB — KO 长条页推理口径校准实验

## 背景与目标

T2-V2（done @merge `784e585b`）结构性发现：KO 长条 webtoon 页（690×51971~100480 与 600×18401，aspect 1:31~1:146）在整页 letterbox 1024 下 SFX 亚像素化，**三方全 0/56 含现役 chiqui7**——瓶颈=推理序列口径（tile 切块 vs letterbox）非模型权重。DSH r1 独立旁证：R1 KO 扫描器 `scan_mode=tile_690x1024_overlap128`（原生分辨率切块）与 V2 生产序列（整页 letterbox）物理成像不同。

本 Task 用对照实验量化该差异并固化 KO 域口径建议（供 T3 正式 Gate 采信；生产序列切换本身归 T4）。

## 交付物

- **AC1 口径对照实验（chiqui7 现役权重）**：实验脚本（experiments/M2-KO-TILE-CALIB/）对 KO 4 页（pre-k01/k02/k08/k09，GT 56 框）跑两口径：①整页 letterbox（生产序列复刻，基线=已知 0/56）；②**tile 切块**（沿 R1 `scan_mode=tile_690x1024_overlap128`：690 宽原生无缩放、tile 高 1024、重叠 128；每 tile 推理→框映射回原页坐标系→跨 tile NMS 去重——R1 stage1_preannotate.py 有现成实现可复制适配）。权重=生产 pin d87389af（M2-SFX-DETECT/weights/yolo11s-seg.onnx），conf≥0.5/0.2 双口径，IoU≥0.5 匹配。**预期** tile 口径召回显著高于 letterbox（0/56→非零）——预期不成立也如实登记。
- **AC2 V2 权重同实验**：v2b best.onnx（944e8114，T2-V2 产物，只读引用 `G:/CODEX/New Manga.worktrees/M2-SFX-TRAIN-V2-zcode/training_data/sfx-v1/train-v2/weights/v2b/best.onnx`）同两口径——观察 own-manga 训练数据中的 KO 长条页噪声对 tile 口径的影响。
- **AC3 口径建议固化**：报告给 KO 域 Gate 评测口径提案（tile 参数/合并策略/阈值口径+理由），及生产序列适配的成本估计（仅建议，**零 src 不动生产代码**——切换归 T4）。
- **AC4 报告+Handoff+Task 回填**。

## 验收判据

AC1/AC2：两权重×两口径=4 组召回数字+逐框明细 JSON；数字从盘上产物复算。
AC3：口径建议有实验数据支撑（不凭直觉）；零 src 实证。
AC4：三文档齐。

## Acceptance Criteria

- [ ] AC1 chiqui7 两口径对照实验（4 页 56 框 GT）
- [ ] AC2 v2b 同实验
- [ ] AC3 KO 口径建议固化（提案级，供 T3）
- [ ] AC4 报告+Handoff+Task 回填
- [ ] AC5 零 src；产物 gitignored 或摘要入 Git

## 允许修改范围

`experiments/M2-KO-TILE-CALIB/**`（新建）、`verification/M2-KO-TILE-CALIB/**`、本 Task/Handoff、`training_data/sfx-v1/ko-tile-calib/**`（gitignored 中间产物）、`doc/reviews/M2-KO-TILE-CALIB-*.md`。

## 禁止范围

`src/**`、`tests/**`、`doc/contracts/**`、`packaging/**`、`apps/**`、`doc/STATUS.md`、生产 pin、R1/R2/V1/V2 数据与脚本本体（只读引用）、cases.json。

## 依赖、风险与阻塞

- depends_on：M2-SFX-TRAIN-V2 done。
- 风险：①tile 切块推理的预处理必须与生产序列逐字一致（letterbox/归一化/阈值语义），否则实验不等价——沿 R1 实现复刻并在报告登记预处理对照；②长条页 tile 数量大（51971/896≈58 tiles/页），推理耗时可控（onnxruntime CPU/GPU 均可）。
- 裁量点：tile 参数变体（如重叠 256）仅当主实验顺利时加跑一组（登记即可）。

## 交付与运行记录

-（待 Owner 回填）
