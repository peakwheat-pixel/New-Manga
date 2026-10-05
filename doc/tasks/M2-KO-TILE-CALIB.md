---
id: M2-KO-TILE-CALIB
title: "KO 长条页推理口径校准实验（T3 前置）：tile 切块 vs 整页 letterbox 对照+口径建议固化"
kind: experiment
status: in_review
owner_claim: ZCode 2026-10-05（AC1-AC5 全交付，delivery_head 49253b09，docs head 见交付记录）
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
delivery_commit: 76bf2a94（提案/报告）；返修链 3517ceda→本链尾
handoff: doc/handoffs/M2-KO-TILE-CALIB-zcode-20261005.md
report: verification/M2-KO-TILE-CALIB/calib-report.md
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

- [x] AC1 chiqui7 两口径对照实验（4 页 56 框 GT）——letterbox 0/56×2（n_pred=0 零输出）vs tile ov128 **56/56@0.5**（precision 0.8235）·56/56@0.2（0.6667）；预期成立
- [x] AC2 v2b 同实验——letterbox 0/56×2 vs tile **35/56@0.5**（precision 0.3465）·43/56@0.2（0.2019）；own-manga KO 长条页噪声方向性成立（pre-k01 2GT 换 23 preds），不入切换候选
- [x] AC3 KO 口径建议固化（提案级，供 T3）——ko-caliber-proposal.md：冻结 tile_690x1024_overlap128+生产序列逐字+页级 NMS 0.5+主口径 conf0.5+chiqui7 基线；裁量点变体 ov256/ov448（44/45 @0.5）证相位方差，ov128 实测最优；T4 成本 ~8.9s/页 CPU（≈20× letterbox，GPU 未测）
- [x] AC4 报告+Handoff+Task 回填——calib-report.md+handoff+本回填（docs 提交）
- [x] AC5 零 src；产物 gitignored 或摘要入 Git——15 文件全在允许面；`-- src/ training_data/` 空 diff；中间产物在 gitignored `training_data/sfx-v1/ko-tile-calib/`

## 允许修改范围

`experiments/M2-KO-TILE-CALIB/**`（新建）、`verification/M2-KO-TILE-CALIB/**`、本 Task/Handoff、`training_data/sfx-v1/ko-tile-calib/**`（gitignored 中间产物）、`doc/reviews/M2-KO-TILE-CALIB-*.md`。

## 禁止范围

`src/**`、`tests/**`、`doc/contracts/**`、`packaging/**`、`apps/**`、`doc/STATUS.md`、生产 pin、R1/R2/V1/V2 数据与脚本本体（只读引用）、cases.json。

## 依赖、风险与阻塞

- depends_on：M2-SFX-TRAIN-V2 done。
- 风险：①tile 切块推理的预处理必须与生产序列逐字一致（letterbox/归一化/阈值语义），否则实验不等价——沿 R1 实现复刻并在报告登记预处理对照；②长条页 tile 数量大（51971/896≈58 tiles/页），推理耗时可控（onnxruntime CPU/GPU 均可）。
- 裁量点：tile 参数变体（如重叠 256）仅当主实验顺利时加跑一组（登记即可）。

## 交付与运行记录

- **2026-10-05 Owner（ZCode）交付**，base `9258afc0`，delivery_head `49253b09`（docs head 随 docs 提交更新）。提交链：
  - `b5038659` eval-matrix.json 主口径四组矩阵（8 格经 recompute_matrix.py 复算相等）
  - `7617f5c3` raw 明细 v2b/tile ov128（35/56@0.5 precision 0.3465；43/56@0.2 precision 0.2019）
  - `a2bf8fbd` run-full.log（逐页耗时+sha 断言+MATRIX 行）
  - `22ea78bc`/`1169489a`/`4bd00843` 裁量点变体 ov256/ov448（44/56、45/56 @0.5——相位方差）
  - `fada5d5f` preprocess-caliber-table.md（13 环节逐字对照，两口径共享函数本体零第二实现）
  - `49253b09` ko-caliber-proposal.md（AC3 口径提案，零 src 提案级）
  - docs 提交：calib-report.md + doc/handoffs/M2-KO-TILE-CALIB-zcode-20261005.md + 本回填
- **核心数字**（GT=R2 final manifest KO 4 页 56 框；IoU≥0.5 conf 降序贪心；环境 venv=M2-SFX-FINETUNE-gpu-py312，onnxruntime 1.30.0 CPUExecutionProvider）：
  - chiqui7（pin d87389af… 零重指）：letterbox 0/56×2（**n_pred=0，零输出非低分**）；tile ov128 **56/56@0.5**（precision 0.8235，n_pred 68）·56/56@0.2（0.6667）。逐页@0.5：pre-k08 27/27、pre-k09 24/24、pre-k01 2/2、pre-k02 3/3。
  - v2b（944e8114…）：letterbox 0/56×2；tile **35/56@0.5**（recall 0.625，precision 0.3465，n_pred 101）·43/56@0.2（precision 0.2019，n_pred 213）。逐页@0.5：pre-k08 14/27、pre-k09 17/24、pre-k01 2/2（23 preds）、pre-k02 2/3。
  - 变体（chiqui7×tile@0.5）：ov256=44/56（precision 0.6286）、ov448=45/56（0.6164）——GT 框最高 676px 无跨 tile 切断，**相位方差主导**（pre-k01 两框 ~55px 高完整落格却在 ov256 零检出），ov128 实测最优。
- **结论**：预期成立（tile 0/56→56/56），**KO 瓶颈确证为序列口径非权重**；口径建议=Gate 冻结 tile_690x1024_overlap128+页级 NMS 0.5+主口径 conf0.5+chiqui7 基线；V2B 双差不入切换候选（own-manga KO 长条页噪声方向性成立，归 T3 扩标/DSH P3-7）；生产切换成本 ~8.9s/页 CPU（≈20× letterbox）与 tile 序列层实施归 T4（本提案零 src）。
- **独立复核（非作者）= PASS**：四项全部通过——①预处理对照表行号逐一核实；②pre-k08 tile 召回独立重算 27/27（不 import tile_calib.py 的独立脚本；58 tiles/sfx_raw=31/27-27 与盘上相等；另用独立匹配实现复算全部 8 格逐格相等）；③跨 tile NMS bit-exact（31→30 框 max_coord_delta=0.0000px，唯一被压框 IoU=0.6168 保高压低语义正确）；④零 src+pin 不动（15 文件允许面/空 diff/pin 逐字在位/finally 恢复）。过程假差异 1 项如实登记（复核脚本初版丢 y+y0 平移，修正后复现；不涉及盘上产物）。证据：calib-report.md §8。
- **Handoff**：[doc/handoffs/M2-KO-TILE-CALIB-zcode-20261005.md](../handoffs/M2-KO-TILE-CALIB-zcode-20261005.md)（recipient=DeepSeek Harness 独立 Review→编排代行 Codex 集成；下一任务建议=review 收口+merge，无新实现 Task 待释放）。
- **未运行项（如实）**：生产 tile 口径落地（T4）；GPU EP 耗时实测；宽≠690/600 页参数化（GT 页集仅 690/600 宽）；own-manga KO 噪声消融（T3 扩标处置）。
