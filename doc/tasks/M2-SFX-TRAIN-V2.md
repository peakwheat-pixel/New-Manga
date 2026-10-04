---
id: M2-SFX-TRAIN-V2
title: "SFX 训练 V2（T2-V2）：own-manga 冻结池接入（558 页/1738 框）+A/B 基座重训+同链路对照评测"
kind: feature
status: ready
owner_claim: —
approval: user_directive_2026-10-05_ownmanga接入指令
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权）
depends_on: [M2-SFX-TRAIN-V1, M2-SFX-ANNOTATE-R2, M2-SFX-DATA-INFRA]
base_commit: 4e881720
branch: agent/zcode/M2-SFX-TRAIN-V2
worktree: G:/CODEX/New Manga.worktrees/M2-SFX-TRAIN-V2-zcode
review_events: []
created: 2026-10-05
---

# Task: M2-SFX-TRAIN-V2 — own-manga 接入 + V2 重训

## 背景与目标

V1（done @merge `35cb3db0`）实证管线全通但模型欠拟合（BJ challenge 0/5、KO 0/56），首要假设=真实正样本饥渴。素材线会话（2026-10-05 交接）交付 own-manga 冻结池 T1a 入册包，用户指令按 `ingest_notes.md` 步骤 1-3 接入并重训。

**入册包**（外部树 `G:/CODEX/New Manga.task-envs/sfx-synth-exp/own-manga-ingest/`，只读引用）：
- `own_manga_manifest_records.json`：558 页级样本+1738 框（partial 140/pseudo 418），六组 `own-manga/{v01:125,v02s:103,v12:88,v13:105,v15:53,v16:84}`，`SampleRecord.validate()` 558/558 零错误，`from_dict` 直吃；页图在盘（material_root 指 `sfx-synth-exp/`）。
- 许可=`source=user-own-manga` 备案（2026-10-04 用户裁决覆盖）；chiqui7 同源性边界如实（毛笔竖排漏检类型不被本包覆盖）。
- 隔离纪律：训练运行期间不改已集成 manifest；本包独立文件。

## 交付物（阶段化）

- **AC1 接入+重切**：准备脚本（experiments/M2-SFX-TRAIN-V2/prepare_dataset_v2.py，沿 V1 prepare 模式）——①底册=R2 final 351（只读引用 R2 树）+own-manga 558 records（`SampleRecord.from_dict` 逐条+全量 validate 0 错误断言）②组级指派：`challenge=densho810/vol05`（沿 V1 考卷不变）、`own-manga/六组 → train`（assign_splits `pinned=` 参数传参，**不改 T1a splits.py 交付物**）、`synthetic → train` 沿先例、其余 assign_splits 算法（seed=20261004）③考卷零重叠断言（own-manga 与 densho810 异源+页 sha256 无交集）④YOLO seg 树重建 `${T2}/training_data/sfx-v1/train-v2/dataset/`（names 双通道+challenge 键可扫描+label 逐样本框数断言）。**期望** train≈901 页级/约 2304 框（343+558；629+1738 框），val 4/test 2/challenge 2 不变——以实测为准。
- **AC2 训练 V2（A/B 两版）**：**A 版=官方 yolo11s-seg.pt**（V1 同款，sha 1caa81c0 在盘）；**B 版=近域基座 anonimkaq4 manga yolo11s-seg .pt**（T0 preflight 登记 preflight-report.md:69,129——按其指路找权重；找不到或加载失败则 B 版 skip 并如实登记，不阻塞）。共同口径：imgsz 1024/batch 8/epochs 150/patience 30/seed 20261004/device 0（沿 V1）；数据=train-v2 dataset；runs 落 train-v2/runs/{v2a,v2b}/（gitignored）+log 入 verification raw。可增杠杆裁量（登记即可）：单类 nc=1 变体**仅当** A/B 两版完后时间可行为之（可选第三跑，优先级最低）。
- **AC3 导出+评测（同 V1 管线+对照整改）**：两版 best→ONNX→`_build_engine` 进程内冒烟（零 src 沿 V1）；评测按 **DSH r1 P2-1 整改**——chiqui7 对照改**同链路独立复跑**（用生产现役权重 `M2-SFX-DETECT/weights/yolo11s-seg.onnx`（pin d87389af）对考卷两页+KO val/test 页跑生产推理序列，conf≥0.5/0.2 双口径，**不再用预标注池当基线**）；报告新模型 A/B vs chiqui7（独立复跑口径）vs V1 基线三方对比。
- **AC4 报告**：train-v2-report.md（数据/训练曲线/评测三方对比/V1↔V2 同口径对比——V1 的 train-log 与 eval JSON 在 Git 内可直接引用；诚实边界：own-manga 框坐标=模型输出未手工收紧/chiqui7 同源性/BJ 主攻形态不在本包覆盖内）；Handoff；Task 回填 in_review。
- **AC5 T3/T4 材料更新**：按 V2 结果刷新 T3（Gate 前置）与 T4（生产切换）呈报——若 V2 显著改善（directional），T4 条件清单加「V2 权重替换 pin 的具体语义」。

## 验收判据

AC1：validate 0 错误+指纹复现+组隔离 0 违例+考卷零重叠断言+names 双通道。
AC2：A 版 EXIT=0 完整；B 版或 skip 或完整（均登记）；权重 sha256 登记。
AC3：冒烟 EXIT=0 零 src；评测含同链路 chiqui7 复跑对照（P2-1 整改落地实证）；三方数字如实。
AC4/AC5：文档齐+对比口径一致（同考卷同阈值同 IoU）。

## Acceptance Criteria

- [ ] AC1 own-manga 接入+重切（pinned 传参+零重叠断言+901 页级数据集重建）
- [ ] AC2 训练 V2 A/B 双版（官方/近域基座，同口径可对比）
- [ ] AC3 导出冒烟+同链路对照评测（P2-1 整改+三方对比）
- [ ] AC4 报告+Handoff+Task 回填（V1↔V2 同口径对比）
- [ ] AC5 T3/T4 材料更新
- [ ] AC6 零 src；own-manga 包与训练产物 gitignored 外部树；Git 只进摘要

## 允许修改范围

`experiments/M2-SFX-TRAIN-V2/**`（新建）、`verification/M2-SFX-TRAIN-V2/**`、本 Task/Handoff、`training_data/sfx-v1/train-v2/**`（gitignored）、`doc/reviews/M2-SFX-TRAIN-V2-*.md`。

## 禁止范围

`src/**`、`tests/**`、`doc/contracts/**`、`packaging/**`、`apps/**`、`doc/STATUS.md`、`experiments/M2-SFX-DATA-INFRA/**`（T1a 交付只读——pinned 走函数参数）、R1/R2/V1 数据与脚本本体（只读引用）、`own-manga-ingest/` 包（只读）、生产 pin、cases.json。

## 依赖、风险与阻塞

- depends_on 全 done。风险：①own-manga pseudo 418 页的标签噪声（AI 复核过滤后仍非人工级）——partial/pseudo 分层消融不做（V2 时间盒），噪声影响登记进边界；②own-manga 域偏移（用户自有 6 卷 vs BJ/KO 域）——考卷零重叠+域分布登记；③B 版近域基座不可得——skip 分支已定义；④训练时长 901 样本≈V1 的 2.6 倍（约 40min/版），两版+A/B 评测时间盒内可完成。
- 裁量点：v15 组改钉 val（ingest_notes 建议 3）——**V2 不做**（val 保持 KO 4 样本不动，近域 val 归 T3）；单类 nc=1 第三跑——仅当 A/B 完成且顺利。

## 交付与运行记录

-（待 Owner 回填）
