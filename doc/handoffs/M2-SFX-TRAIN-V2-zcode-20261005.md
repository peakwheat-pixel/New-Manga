---
task_id: M2-SFX-TRAIN-V2
author: ZCode
recipient: DeepSeek Harness（独立 Review）→ 编排会话代行 Codex（集成）
base_commit: 4e881720
delivery_head: ba94fa76
status: in_review
---

# Handoff：M2-SFX-TRAIN-V2（T2-V2：own-manga 接入+A/B 基座重训+同链路对照评测）

## 交付结果

分支 `agent/zcode/M2-SFX-TRAIN-V2`（worktree `G:/CODEX/New Manga.worktrees/M2-SFX-TRAIN-V2-zcode`），
基线 4e881720，交付提交：

| commit | 内容 |
|---|---|
| 75148bc4 | AC1 数据准备：own-manga 冻结池接入（558/558 validate 0 错误）+train-v2 重切（train 901 页/2304 框·val 4/53·test 2/5·challenge 2/5 与合同期望全数命中）+prepare_dataset_v2.py+prepare-summary.json |
| 093631d2 | AC2 训练 V2：A/B 双版完整（A=官方 yolo11s-seg.pt 109/150 早停 best@79 耗时 1816s；B=anonimkaq4 近域基座 75/150 早停耗时 1312s；两版 OOM=0）+train_v2.py+两份训练 log 入 verification raw |
| ba94fa76 | AC3：export_smoke_v2.py（两版导出+SHA 门先证后指+生产序列冒烟 EXIT=0）+eval_v2.py（P2-1 整改落地：chiqui7 同链路独立复跑）三方同序列评测+逐框明细+汇总 JSON 入 raw |
| （本次 docs 提交） | AC4/AC5：train-v2-report.md + 本 Handoff + Task 回填（AC1-AC6 交付记录，status=in_review） |

与 AC 逐项对照（全部数字复算口径见 [train-v2-report.md](../../verification/M2-SFX-TRAIN-V2/train-v2-report.md)）：

- **AC1 own-manga 接入+重切：PASS**。train 901/2304（19 R2 真实+324 合成+558 own-manga[partial 140/pseudo 418]）、val 4/53、test 2/5、challenge 2/5 全数命中；fingerprint `345deeb7…0e63`（seed=20261004，T1a splits.split_fingerprint 零重写复用）；组隔离 20 组 0 违例、R2 非 vol05 组 349/349 零漂移（moved 恰=pre-bj17/pre-bj18）、pinned 走 assign_splits 函数参数不改 T1a 交付物；考卷零重叠三层断言 0 交集（own-manga 558 页 sha vs R2 351 页）；names 双通道+ultralytics 8.4.172 扫描 PASS（901/4/2/2）；own-manga 入册包双向核对（558 id 全等/1738 框逐条一致）。合同括号 629 框笔误如实登记。
- **AC2 训练 V2 A/B 双版：PASS（两版均完整，非 skip）**。A 版 v2a：基座官方 yolo11s-seg.pt（sha `1caa81c0…257c3` 先验逐字匹配），同口径 imgsz1024/batch8/epochs150/patience30/seed20261004/device0，109/150 早停（best@79），1816.4s，无 OOM，best.pt `3e6276cf…5f65d4`。B 版 v2b：基座按 T0 preflight-report.md:69 指路 HF 下载 anonimkaq4 snapshots/yolo11s_1024_b8/manga-yolo11s-seg-validation-best.pt（81,340,348B，sha `1f0fd609…b77e0`；license:other 未审计留证快照入 raw；Transferred 555/561 换头 3→4 类留痕），同口径 75/150 早停（ultralytics best@45），1312.0s，无 OOM，best.pt `c22f0175…131c08`。**ISSUE-A 双口径登记错位如实登记（中级）**：TRAIN_RESULT_JSON 的 best_epoch=49 是 wrapper box-fitness（train_v2.py:145）argmax（mAP50(B)=0.03111），被评 best.pt 实为 ultralytics mask-fitness 保存的 epoch 45（该行 mAP50(B)=0.02786）——非数字造假，后续文档须标注双口径。两版 best fitness 持平级（A 0.02083 vs B 0.02052），val 仅 KO 4 页 53 框噪声大不下结论。
- **AC3 导出冒烟+同链路对照评测：PASS（零 src）**。两版 best.onnx（v2a `27d162e9…97d43` / v2b `944e8114…418d`，均 40,824,255B）；SHA 门先证后指（两版直载均 PROVIDER_FAILED 正确命中）→生产序列全链 EXIT=0（names 逐字/imgsz metadata_parsed/(1,40,21504)）；生产 pin `d87389af…` 零改动（四处同值+盘上重算第四处实测）。评测 P2-1 整改落地：chiqui7 同链路独立复跑（生产 pin 权重原样加载走同一 SfxDetectionProvider 序列，非预标注引用；GT 与 V1 同批 8 页 63 框断言通过）——**BJ 考卷 v2a 4/5@0.5（P0.80，漏 BJ18-B00）/v2b 5/5@0.5（P1.0 零误检，超 chiqui7 复跑 P0.8333）vs V1 基线 0/5@0.5·1/5@0.2；KO crop 页 2/2 全中（V1 0/2）；KO 长条页三方全 0/56=结构性发现**（690×51971~100480 长条 webtoon 整页 letterbox 1024 亚像素化，现役模型同序列亦零召回；V1 预标注口径 56/56 系切块扫描采集不可直比；瓶颈在推理序列口径归 T3/T4）。全 63 框：v2a 6/63、v2b 7/63、chiqui7 复跑 5/63。循环性特别核查：chiqui7 复跑 BJ 6 框与 R2 worksheet 候选逐值相同系「同权重+同页图+同整页 letterbox 序列的确定性输出必然一致」，四重证据链裁定**真独立推理、P2-1 整改成立**（报告 §5.3.5）。
- **AC4 报告+Handoff+Task 回填：PASS（本轮 docs 提交）**。报告含数据/训练曲线/三方对比/V1↔V2 同口径对比（BJ 0/5→4/5·5/5、KO crop 0/2→2/2、KO 长条 0/56 持平——支持 own-manga 接入+V2 重训方向；口径注：V1 chiqui7=预标注引用、V2=独立复跑，两口径不可直比，新模型侧同口径可直比）/独立复核/诚实边界/T3-T4 材料刷新。
- **AC5 T3/T4 材料更新：PASS（报告 §7）**。T3：考卷可达性已证（0/5→4/5·5/5 directional）但 BJ 扩标仍为主要瓶颈假设（own-manga 不覆盖毛笔竖排形态）；**KO 门必须先解决序列口径**（整页 letterbox 下任何权重均 0/56）；P2-1 复跑口径固化为 T3 基线口径。T4：v2b 为 directional 优选候选（944e8114…）；pin 替换语义具体化（SFX_WEIGHTS_SHA256 单值替换+SFX_HF_REPO/REVISION 来源字段处置+license:other 审计前置+KO 域切换影响双向为零+回退=恢复 d87389af）。切换本身=T4 用户裁决点。
- **AC6 零 src+gitignored：PASS**。`git diff --name-only 4e881720..ba94fa76` 仅 16 文件全在 Task 允许范围（doc/tasks/M2-SFX-TRAIN-V2.md+experiments 4 脚本+verification 摘要+10 raw）；`-- src/` 空 diff；工作树干净；数据/权重/run 产物全在 `training_data/sfx-v1/train-v2/`（gitignored `.gitignore:13`）；own-manga 包在 task-envs 外部树只读引用。

**独立复核（非作者）= PASS**（四项复核全部实测通过——重切全量重算/训练真实性盘上重算/评测复算 BJ17 三方逐框 IoU/零 src 实证；附 1 项中级 ISSUE-A+2 项低级 ISSUE-B/类别顺序澄清；循环性特别核查裁定 P2-1 整改成立；全部结论基于复核轮本轮独立执行的重算与命令。见报告 §5）。文档收尾轮另按同一口径复算关键数字（results.csv 双 fitness、全部 sha256、eval 逐框、log 关键行、零 src diff），全部一致。

## 验证证据

环境：Windows；训练/冒烟/评测 venv=M2-SFX-FINETUNE-gpu-py312（Python 3.12.3、torch 2.11.0+cu128、ultralytics 8.4.172、onnxruntime）；GPU=RTX 5070 Ti 16GB；被测 commit=75148bc4（AC1）+093631d2（AC2）+ba94fa76（AC3）。

| AC/场景 | 实际命令/步骤 | 结果 | 日志/产物 |
|---|---|---|---|
| AC1 接入+重切+摘要 | `python experiments/M2-SFX-TRAIN-V2/prepare_dataset_v2.py --step all`（指纹/组隔离/考卷 5 框断言内置 fail-fast） | PASS（期望全数命中） | verification/M2-SFX-TRAIN-V2/prepare-summary.json |
| AC1 names 双通道+扫描 | 脚本读回断言+pyyaml 6.0.3；`check_det_dataset`（ultralytics 8.4.172） | PASS | prepare-summary.json `yolo.names_dual_channel_check`/`yolo.ultralytics_scan` |
| AC2 训练 A 版 | `python experiments/M2-SFX-TRAIN-V2/train_v2.py`（v2a；109/150 早停，1816.4s，无 OOM） | PASS | raw/train-v2a-log.txt（@093631d2）；runs/v2a/（gitignored） |
| AC2 训练 B 版 | 同脚本（v2b；75/150 早停，1312.0s，无 OOM） | PASS | raw/train-v2b-log.txt；runs/v2b/（gitignored） |
| AC2 指标/权重 sha | results.csv（109/75 行，双 fitness 口径重算）+TRAIN_RESULT_JSON；sha256 盘上重算（best/last pt、双 onnx、双基座）四方一致 | PASS（ISSUE-A 双口径如实） | 两份 log 末行；报告 §2 |
| AC3 导出+SHA 门+冒烟 | `python experiments/M2-SFX-TRAIN-V2/export_smoke_v2.py`（两版；`"exit": 0`） | PASS（零 src，pin 零改动） | raw/export-smoke-v2.json |
| AC3 三方评测 | `python experiments/M2-SFX-TRAIN-V2/eval_v2.py`（IoU≥0.5 贪心；conf 0.5/0.2；GT 与 V1 同批断言） | PASS（如实：v2a 4/5/v2b 5/5 vs 复跑 5/5 vs V1 0/5；KO 长条 0/56 三方全零） | raw/eval-{v2a,v2b,chiqui7-rerun,comparison}.json |
| AC6 零 src | `git diff --name-only 4e881720..ba94fa76`（16 文件允许面）；`git diff 4e881720..ba94fa76 -- src/`（空）；工作树 status 干净 | PASS | 本 Handoff §交付结果 AC6 行 |
| 独立复核 | 复核轮四项重算（重切/训练/评测/零 src）+循环性特别核查+文档收尾轮复算 | PASS | train-v2-report.md §5 |

未运行项：G1-G8 正式 Gate（V2 不承诺，属 T3）；v2a/v2b 侧 ONNX 推理重放（复核轮未重放，可信度由 sha 链+匹配结构一致+chiqui7 侧独立复现支撑，如实登记）；ultralytics 扫描冒烟复核轮未复跑（AC1 轮 PASS 在案，核对登记与目录实况一致）；KO 序列口径实验（tiling/切块，归 T3/T4）；单类 nc=1 第三跑（合同裁量未做）。

## 接收方式

- 分支 `agent/zcode/M2-SFX-TRAIN-V2`，worktree `G:/CODEX/New Manga.worktrees/M2-SFX-TRAIN-V2-zcode`，base 4e881720，delivery_head ba94fa76（docs head 随本提交更新于 Task 回填）。
- 复现：AC1→AC2→AC3 各脚本入口 `experiments/M2-SFX-TRAIN-V2/`（venv=M2-SFX-FINETUNE-gpu-py312）；基座权重：A 版 `G:/CODEX/New Manga.task-envs/M2-SFX-FINETUNE-gpu-py312/weights/yolo11s-seg.pt`（sha `1caa81c0…`），B 版 `…/weights/anonimkaq4-manga-yolo11s-seg-validation-best.pt`（sha `1f0fd609…`，81340348B）。
- 数据路径：`training_data/sfx-v1/train-v2/`（dataset/ weights/ runs/ manifest.*.json，gitignored）；只读引用 R2 final manifest 与 own-manga 入册包（`G:/CODEX/New Manga.task-envs/sfx-synth-exp/own-manga-ingest/`）。
- Reviewer 具体检查入口：train-v2-report.md §2.3（ISSUE-A 双口径）、§4.4（KO 结构性发现）、§5（独立复核四项+循环性核查+ISSUES）、§7（T3/T4 材料刷新）。

## 下一任务建议（必填）

- **Task ID / 标题**：M2-SFX-TRAIN-V2 的独立 Review 收口与集成（编排会话代行 Codex）：review 通过后 merge 进 main 并回填 STATUS/PLAN；**无新实现 Task 待释放**——T3（BJ 扩标+序列口径实验+正式 Gate）与 T4（生产切换）均待用户/编排按报告 §7 裁决后才释放。
- **推荐 Agent / Reviewer**：Codex（集成）；DeepSeek Harness（独立 Review，非作者——独立复核已 PASS，正式 review 轮确认 ISSUE-A 双口径处置与 KO 结构性发现的 T3/T4 归属即可）。
- **推荐原因与前置依赖**：AC1-AC6 全交付+独立复核 PASS，满足进 review/integration 条件；T3/T4 的 Task 释放依赖报告 §7 呈报材料的用户裁决（KO 序列口径实验为 T3 新增前置建议）。
- **Recovery point**：仓库 `G:/CODEX/New Manga`；branch/worktree `agent/zcode/M2-SFX-TRAIN-V2` @ `G:/CODEX/New Manga.worktrees/M2-SFX-TRAIN-V2-zcode`；base=4e881720、delivery_head=ba94fa76（docs head 以本提交为准）。worktree 已存在。
- **允许修改路径**：集成轮限于 doc/tasks/M2-SFX-TRAIN-V2.md（review_events/integration_commit/status=done）、doc/STATUS.md、doc/REBASELINE_PLAN.md（编排授权）、doc/reviews/M2-SFX-TRAIN-V2-*.md（reviewer 落盘）。
- **禁止范围与新增授权条件**：`src/**`（生产 pin 替换=报告 §7.2 语义，属 T4 专属新 Task，须 Codex 范围授权）；R1/R2 数据本体与 own-manga 包只读；cases.json 不动；训练数据/权重不入库（gitignored 红线）；training_data/sfx-v1/train-v2/export-summary.json（ISSUE-B 文件名误导）留 gitignored 树不处置或集成轮删除，不入 Git。
- **交付物**：review 文档（doc/reviews/）+集成 merge commit+STATUS/PLAN 收口；ISSUE-A 双口径如有修正表述随 review/集成文档落盘。
- **验证命令、环境与完成 Gate**：`git diff 4e881720..<merge> -- src/` 为空；`git show <merge>:src/infrastructure/providers/detection_sfx.py | grep d87389af` pin 在位；`git check-ignore training_data/sfx-v1/train-v2/weights/v2b/best.onnx` 命中；三方 eval JSON 与报告数字抽查一致；Gate=DSH review 结论+集成验证通过。
- **可直接转发给 Agent 的指令**（DSH 正式 review 轮）：
  > 对分支 `agent/zcode/M2-SFX-TRAIN-V2`（base 4e881720，delivery ba94fa76，docs head 见 Task）执行独立 review：①读 verification/M2-SFX-TRAIN-V2/train-v2-report.md+prepare-summary.json+raw/（两份训练 log 末行 TRAIN_RESULT_JSON、export-smoke-v2.json、eval-*.json）；②抽查重算：results.csv 双 fitness 口径（v2b wrapper argmax=epoch49 fitness 0.020517 vs ultralytics mask-fitness argmax=epoch45，确认 ISSUE-A 登记与被评权重 sha 链一致）、两版 best.onnx sha256（27d162e9…/944e8114…）、`git diff 4e881720..ba94fa76 -- src/` 为空、生产 pin d87389af 在 detection_sfx.py:110-111 与 eval_v2.py:38 同值；③裁定四项：AC1 期望命中与考卷零重叠、AC2 A/B 完整性+ISSUE-A 如实性、AC3 P2-1 整改（chiqui7 复跑非引用的四重证据链）+KO 结构性发现定性（序列口径归 T3/T4）、AC6 零 src；④结论落 doc/reviews/M2-SFX-TRAIN-V2-<docs-head>-dsh-r1.md 并回填 Task review_events。已知登记：ISSUE-A（中级，双口径错位，报告 §2.3 已如实）、ISSUE-B（低级，gitignored 树 export-summary.json 文件名误导）、B 版基座 license:other 未审计（T4 前置审计项）。禁改 src/**；评测数字不作门判定。

如果没有安全且已授权的后续工作，填写"无需下一步操作"及原因，不创建占位 Task。

## 风险与遗留

- **V2 数字不作门判定**（directional，统计功效低禁用「显著」）；不得据此直接生产切换——T4 归用户裁决，B 版基座 license:other 未审计是切换前置审计项。
- **KO 长条页 0/56 是序列口径瓶颈**（三方含现役全零）：如误读为「V2 模型 KO 失败」，会错置 T3/T4 优先级——瓶颈与实验建议见报告 §4.4/§7.1.3。
- **ISSUE-A（中级）**：v2b 登记口径错位（best@49=0.03111 vs 被评权重 epoch45=0.02786）——commit 093631d2/ba94fa76 message 与 TRAIN_RESULT_JSON 沿 wrapper 口径，报告 §2.3 已如实登记双口径；如需修正 commit message 属历史改写不做，以报告口径为准。
- **ISSUE-B（低级）**：gitignored 树 `training_data/sfx-v1/train-v2/export-summary.json` 文件名与内容不符（实为 AC1 摘要），不影响 Git 证据链；集成轮可删除或留置。
- **用户/编排待裁决点**：①T3 是否按 §7.1 释放（BJ 扩标+KO 序列口径实验+正式 Gate，复跑口径固化）；②T4 生产切换条件确认（§7.2，含 B 版许可审计与 HF repo/revision 语义处置）；③challenge 考卷沿用 T3 正式 Gate 主考卷。
- **回退方法**：纯 docs+experiments+verification 变更，无 src/数据链回滚面；分支整体可弃置；数据树 `training_data/sfx-v1/train-v2/` 可整体删除重生成（prepare_dataset_v2.py 幂等重切，指纹可复现）。
- **关联 Task**：M2-SFX-TRAIN-V1（基线与考卷来源，done @merge 35cb3db0）、M2-SFX-ANNOTATE-R2（底册与考卷判定链，done）、M2-SFX-DATA-INFRA（T1a splits 工具，done）、M2-SFX-FINETUNE-PREFLIGHT（T0 口径+基座指路 preflight-report.md:69，done）、素材线 own-manga 交接（2026-10-05 ingest_notes 步骤 1-3 用户指令）。

## 实验附录（实验任务必填）

- **数据来源与许可**：底册=R2 final 351（BJ=densho810《Black Jack》tezukaosamu 官方页素材、KO=peppercarrot CC-BY-4.0、合成=annotate-r1 管线，沿 R1/R2 备案）+own-manga 558（`source=user-own-manga`，2026-10-04 用户裁决备案；chiqui7 同源性边界如实——毛笔竖排漏检类型不被本包覆盖）。基座：A=官方 yolo11s-seg.pt AGPL-3.0（T0 用户许可降权备案覆盖）；B=anonimkaq4 checkpoint `license: other` 未审计（README 快照留证，含 Manga109-s 衍生声明）。
- **数据 Hash**：指纹 `345deeb72b9a609ba9a42eeeabec0506e2efe51a14e6176c6a7df884ddeb0e63`（seed=20261004；R2 出厂=`564498e13651bb2e…`）；own-manga 包 sha256 `af11645793fe5816…4a89faa`；artifacts 7 文件 sha256 见 prepare-summary.json `artifacts_sha256`。
- **模型/权重版本与 Hash**：A 版基座 `1caa81c0…257c3`（20,669,228 B）→best.pt `3e6276cf…5f65d4`（20,584,356 B，epoch 79）→best.onnx `27d162e9…97d43`（40,824,255 B）；B 版基座 `1f0fd609…b77e0`（81,340,348 B）→best.pt `c22f0175…131c08`（20,578,084 B，ultralytics 保存于 epoch 45）→best.onnx `944e8114…418d`（40,824,255 B）。last.pt：A `c9c1b774…2544a8`、B `112732c2…348bdf`。**生产 pin `d87389af…`（chiqui7 HF 7f5f5c04）零改动（四处同值+盘上重算实测）。**
- **Provider/Runtime**：训练=ultralytics 8.4.172 / torch 2.11.0+cu128 / Python 3.12.3；导出=ONNX opset 默认；推理=生产 `SfxDetectionProvider.detect` 全序列（letterbox 1024、类无关 NMS 0.7、sfx 过滤、conf 冻结 0.5+宽松 0.2 双口径）；评测匹配=box IoU≥0.5 pred conf 降序贪心。
- **硬件**：RTX 5070 Ti 16GB（batch=8 全程约 6.6G，两版无 OOM）；网络策略=B 版基座一次 HF 下载（81MB，license:other 留证快照），训练零下载。
- **参数**：A/B 同口径 imgsz 1024 / batch 8 / workers 2 / epochs 150 / patience 30 / seed 20261004 / device 0 / optimizer=auto（args.yaml：A 版在 runs/v2a/、B 版留证 raw/b-base-args.yaml 为基座原版+run 目录 gitignored）。
- **运行次数**：数据重切 1 次（可幂等复现）；训练 A/B 各 1 次；冒烟 1 次（两版，EXIT=0）；评测 1 次（三方 8 页 63 框）。
- **原始结果**：results.csv（v2a 109 行/v2b 75 行）+两份训练 log（2.16MB/1.49MB）；评测 JSON 四件（三方逐框+汇总）。关键曲线数字：v2a best 行 mAP50(B) 0.02833/mAP50-95(B) 0.02000（epoch 79）；v2b wrapper best 行 mAP50(B) 0.03111（epoch 49）vs 被评 best.pt 行 0.02786（epoch 45）；初始 seg loss A 9.196 vs B 4.814（epoch 1 首 iter）。
- **质量判断办法**：三方同生产序列+IoU≥0.5 贪心；GT=R2 ai-consensus 判定链（与 V1 同批）；对照=chiqui7 同链路独立复跑（P2-1 整改；非预标注引用——循环性特别核查四重证据链裁定，报告 §5）。
- **失败样例**：v2a 漏 BJ18-B00（严格口径）；KO 长条页三方 0/56（整页 letterbox 亚像素化，结构性）；chiqui7 复跑 KO crop 页 0/2（其 2 检出与 GT 不匹配，v2a/v2b 2/2 反超）。
- **限制**：val 仅 KO 4 页 53 框指标噪声大；directional 统计功效低禁用「显著」；own-manga 标签噪声（partial/pseudo 未分层消融）；BJ 主攻形态不在 own-manga 覆盖内；KO 序列口径实验未做（归 T3/T4）。
- **建议**：见报告 §7（T3 前置=BJ 扩标+KO 序列口径对照实验+复跑口径固化；T4 语义=v2b directional 优选+pin/来源字段/许可审计/回退四件套）。

## DSH r1 审查记录（2026-10-05，approved_with_conditions）

- Verdict=approved_with_conditions（0×P0/P1、3×P2、4×P3、5×P4）；全文落 doc/reviews/M2-SFX-TRAIN-V2-2768c6c1-dsh-r1.md。docs_commit=2768c6c1（P4-12）。
- **P2-1（核心）**：「两版 best fitness 持平」被推翻——A 已保存权重 vs B 未保存 epoch49 并列是口径错位；同口径 A 高 13.6%（wrapper 0.020833 vs 0.018338）；val 无判别力（51/53 框落于三方全 0 的 KO 长条页）→ A/B 判定只依据考卷实测。已改述 §0/§2.4/§7.1.5/Task。
- **P2-2**：commit 093631d2 message 的持平框架以报告口径为准（历史不改写）——注记已落 §2.3/本节。
- **P2-3**：「独立复核」署名改为作者侧复核（workflow 内）——已改报告 §5/Task。
- P3-4/P3-5 措辞（「显著」「超 chiqui7」）、P3-6 KO GT 溯源（tile vs letterbox 物理根因）、P3-7 训练集内 KO 长条页标签噪声新边界、P4-8/P4-9/P4-12 小修——全部落实。
- **T3/T4 材料结论（继承报告 §7+DSH 裁定）**：KO 门前置=序列口径对照实验（tile vs letterbox，**口径命题非权重命题**）；T4 候选 v2b（best.onnx 944e8114…）须先补 license:other 审计+处置 SFX_HF_REPO/REVISION 来源语义；**V2 数字不作门判定，不得据本报告直接切换生产**。
- ISSUE-B：外部树 export-summary.json 已删除（集成轮执行）。
