---
id: M2-SFX-TRAIN-V2
title: "SFX 训练 V2（T2-V2）：own-manga 冻结池接入（558 页/1738 框）+A/B 基座重训+同链路对照评测"
kind: feature
status: in_review
owner_claim: 2026-10-05 by zcode subagent @75148bc4（AC1）+ @093631d2（AC2）+ @ba94fa76（AC3；docs 收尾轮报告/Handoff/本回填随 docs 提交）
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

- [x] AC1 own-manga 接入+重切（pinned 传参+零重叠断言+901 页级数据集重建）
- [x] AC2 训练 V2 A/B 双版（官方/近域基座，同口径可对比）
- [x] AC3 导出冒烟+同链路对照评测（P2-1 整改+三方对比）
- [x] AC4 报告+Handoff+Task 回填（V1↔V2 同口径对比）
- [x] AC5 T3/T4 材料更新
- [x] AC6 零 src；own-manga 包与训练产物 gitignored 外部树；Git 只进摘要

## 允许修改范围

`experiments/M2-SFX-TRAIN-V2/**`（新建）、`verification/M2-SFX-TRAIN-V2/**`、本 Task/Handoff、`training_data/sfx-v1/train-v2/**`（gitignored）、`doc/reviews/M2-SFX-TRAIN-V2-*.md`。

## 禁止范围

`src/**`、`tests/**`、`doc/contracts/**`、`packaging/**`、`apps/**`、`doc/STATUS.md`、`experiments/M2-SFX-DATA-INFRA/**`（T1a 交付只读——pinned 走函数参数）、R1/R2/V1 数据与脚本本体（只读引用）、`own-manga-ingest/` 包（只读）、生产 pin、cases.json。

## 依赖、风险与阻塞

- depends_on 全 done。风险：①own-manga pseudo 418 页的标签噪声（AI 复核过滤后仍非人工级）——partial/pseudo 分层消融不做（V2 时间盒），噪声影响登记进边界；②own-manga 域偏移（用户自有 6 卷 vs BJ/KO 域）——考卷零重叠+域分布登记；③B 版近域基座不可得——skip 分支已定义；④训练时长 901 样本≈V1 的 2.6 倍（约 40min/版），两版+A/B 评测时间盒内可完成。
- 裁量点：v15 组改钉 val（ingest_notes 建议 3）——**V2 不做**（val 保持 KO 4 样本不动，近域 val 归 T3）；单类 nc=1 第三跑——仅当 A/B 完成且顺利。

## 交付与运行记录

- **AC1 数据准备轮（2026-10-05，@75148bc4）**：own-manga 冻结池接入（558/558 validate 0 错误，入册包只读引用）+train-v2 重切（零 src）。pinned 走 assign_splits 函数参数（densho810/vol05→challenge+own-manga 六组/synthetic→train，**不改 T1a splits.py 交付物**）；train 901 页/2304 框（19 R2 真实+324 合成+558 own-manga[partial 140/pseudo 418]）·val 4/53·test 2/5·challenge 2/5 与合同期望全数命中；fingerprint `345deeb7…0e63`（seed=20261004）复现一致；组隔离 20 组 0 违例、R2 非 vol05 组 349/349 零漂移（moved 恰=pre-bj17/pre-bj18）；考卷零重叠三层断言 0 交集；names 双通道+ultralytics 扫描 PASS（901/4/2/2）；合同括号 629 框笔误如实登记（V1 实测 566+1738=2304）。证据：prepare-summary.json+manifest.train-v2.json（gitignored 树）。
- **AC2 训练轮（2026-10-05，@093631d2）**：A/B 双版完整（非 skip）。A 版 v2a=官方 yolo11s-seg.pt（sha `1caa81c0…` 先验匹配）109/150 早停 best@79、1816.4s；B 版 v2b=按 T0 preflight-report.md:69 指路 HF 下载 anonimkaq4 yolo11s_1024_b8 validation-best.pt（81,340,348B sha `1f0fd609…`，license:other 未审计留证快照入 raw，Transferred 555/561 换头留痕）75/150 早停、1312.0s；两版同口径（imgsz1024/batch8/epochs150/patience30/seed20261004/device0）、OOM=0 无减半重试；两版 best fitness 持平级（A 0.02083/B 0.02052），val 仅 KO 4 页 53 框噪声大不下结论。**ISSUE-A 双口径登记错位如实登记（中级）**：TRAIN_RESULT_JSON best_epoch=49=wrapper box-fitness（train_v2.py:145）argmax（mAP50(B) 0.03111），被评 best.pt 实为 ultralytics mask-fitness 保存的 epoch45（该行 mAP50(B)=0.02786）——非数字造假，后续文档标注双口径。两份训练 log（2.16MB/1.49MB）入 verification raw；runs gitignored。
- **AC3 评测轮（2026-10-05，@ba94fa76）**：两版导出冒烟 EXIT=0（SHA 门先证后指：两版直载均 PROVIDER_FAILED 正确拒跑→进程内重指全链过；names 逐字/imgsz 解析/(1,40,21504)；v2a onnx `27d162e9…`/v2b onnx `944e8114…`；零 src，pin d87389af 零改动）+P2-1 整改落地三方同链路评测：chiqui7 同链路独立复跑（生产 pin 权重原样加载走同一 SfxDetectionProvider 序列，非预标注引用；GT 与 V1 同批 8 页 63 框断言通过；循环性特别核查四重证据链裁定整改成立）。**BJ 考卷 v2a 4/5@0.5（P0.80）·v2b 5/5@0.5（P1.0 零误检，超 chiqui7 复跑 P0.8333）vs V1 基线 0/5@0.5·1/5@0.2——V1→V2 directional 大幅改善**；KO crop 页 2/2 全中（V1 0/2）；**KO 长条页 4 样本 56 框三方全 0/56=结构性发现**（690×51971~100480 长条 webtoon 整页 letterbox 1024 亚像素化，现役模型同序列亦零召回；V1 预标注口径 56/56 系切块扫描采集不可直比；瓶颈在推理序列口径归 T3/T4）。全 63 框 v2a 6/63、v2b 7/63、chiqui7 复跑 5/63。杂注：export-smoke-v2.json v2b 段 production_pin 字段=v2a 重指残留（cosmetic，门语义由两次 sha_gate.fired 实证）。
- **文档收尾轮（2026-10-05，docs 提交）**：`verification/M2-SFX-TRAIN-V2/train-v2-report.md`（全部关键数字从盘上产物复算/重读确认）+ `doc/handoffs/M2-SFX-TRAIN-V2-zcode-20261005.md` + 本 Task 回填（status=in_review，AC1-AC6 勾选）。
- **独立复核（非作者）= PASS**：四项复核全部实测通过（重切全量重算/训练真实性盘上重算/评测复算 BJ17 三方逐框 IoU/零 src 实证）；附 1 项中级（ISSUE-A 双口径登记错位，已在 AC2/报告 §2.3 如实登记）+2 项低级（ISSUE-B：gitignored 树 export-summary.json 文件名与内容不符不影响 Git 证据链；B 版基座 README 类别顺序澄清）；循环性特别核查裁定 P2-1 整改成立（chiqui7 复跑 BJ 6 框与 worksheet 候选逐值相同系同权重+同页图+同整页 letterbox 序列的确定性输出，eval_v2.py 无预标注池读取路径+KO 复跑 n_pred=0 反证+复核轮独立复跑逐值复现）。全部结论基于复核轮本轮独立执行的重算与命令。
- 报告：[verification/M2-SFX-TRAIN-V2/train-v2-report.md](../../verification/M2-SFX-TRAIN-V2/train-v2-report.md)；Handoff：[doc/handoffs/M2-SFX-TRAIN-V2-zcode-20261005.md](../handoffs/M2-SFX-TRAIN-V2-zcode-20261005.md)；摘要：verification/M2-SFX-TRAIN-V2/prepare-summary.json；raw：train-v2{a,b}-log.txt/export-smoke-v2.json/eval-{v2a,v2b,chiqui7-rerun,comparison}.json/b-base-{readme-snapshot.md,args.yaml,snapshot-metadata.json}。
- **T3/T4 材料刷新（交编排/用户裁决，不随本 Task 释放）**：T3——考卷可达性已证（BJ 0/5→4/5·5/5 directional）但 BJ 深度扩标仍为主要瓶颈假设（own-manga 不覆盖毛笔竖排形态）；**KO 门必须先解决推理序列口径**（整页 letterbox 下任何权重均 0/56，切块/tiling 实验为 KO 域 Gate 前置建议）；P2-1 复跑口径固化为 T3 基线口径；A/B 结论=近域基座方向值得保留。T4——v2b 为 directional 优选候选（onnx `944e8114…`）；pin 替换语义具体化（SFX_WEIGHTS_SHA256 单值替换+SFX_HF_REPO/REVISION 来源字段处置+license:other 审计前置+KO 域切换影响双向为零+回退=恢复 d87389af）；切换本身=T4 用户裁决点——报告 §7。

## Review

-（待 DSH review 轮回填；独立复核结论见「交付与运行记录」，正式 review 文档落 doc/reviews/M2-SFX-TRAIN-V2-*.md）
