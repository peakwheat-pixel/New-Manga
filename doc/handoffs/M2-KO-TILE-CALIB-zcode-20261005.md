---
task_id: M2-KO-TILE-CALIB
author: ZCode
recipient: DeepSeek Harness（独立 Review，非作者）→ 编排会话代行 Codex（集成）
base_commit: 9258afc0
delivery_head: 49253b09
status: in_review
---

# Handoff：M2-KO-TILE-CALIB（KO 长条页推理口径校准实验：tile 切块 vs 整页 letterbox 对照+口径建议固化）

## 交付结果

分支 `agent/zcode/M2-KO-TILE-CALIB`（worktree
`G:/CODEX/New Manga.worktrees/M2-KO-TILE-CALIB-zcode`），基线 9258afc0，交付提交：

| commit | 内容 |
|---|---|
| b5038659 | 主口径四组矩阵 eval-matrix.json（chiqui7 letterbox 0/56 vs tile 56/56；v2b letterbox 0/56 vs tile 35/56 @conf0.5）——8 格经 recompute_matrix.py 从盘上产物复算相等 |
| 7617f5c3 | raw 明细 v2b/tile ov128（conf0.5 35/56 precision 0.3465 n_pred=101；conf0.2 43/56 precision 0.2019 n_pred=213——own-manga KO 长条页噪声方向性成立：pre-k01 2GT 换 23 preds） |
| a2bf8fbd | run-full.log 全量运行日志（逐页耗时：tile≈0.136s/tile CPU；权重 sha 断言行；逐组 MATRIX 行） |
| 22ea78bc / 1169489a / 4bd00843 | 裁量点变体 ov256/ov448 raw+矩阵（44/56、45/56 @0.5——三相位 56/44/45 确认相位方差主导，非重叠单调） |
| fada5d5f | preprocess-caliber-table.md 预处理逐字对照表（13 环节；两口径共享 dsfx._letterbox/_sfx_boxes 本体零第二实现；R1 复刻来源行号+复算核验记录） |
| 49253b09 | ko-caliber-proposal.md 口径提案（AC3：tile_690x1024_overlap128 冻结建议+页级 NMS 0.5+主口径 conf0.5+chiqui7 基线+T4 成本估计，零 src 提案级） |
| （本次 docs 提交） | AC4：calib-report.md + 本 Handoff + Task 回填（status=in_review） |

与 Acceptance Criteria 逐项对照（全部数字复算口径见
[calib-report.md](../../verification/M2-KO-TILE-CALIB/calib-report.md)）：

- **AC1 chiqui7 两口径对照（4 页 56 框 GT）：PASS，预期成立**。letterbox 整页
  conf≥0.5/0.2 均 **0/56（n_pred=0，零输出非低分）**；tile 690x1024 ov128
  conf≥0.5 **56/56 同源复现（见报告 GT 同源性限制段）（precision 0.8235，n_pred 68）**、conf≥0.2 56/56
  （precision 0.6667，n_pred 84）。逐页@0.5：pre-k08 27/27、pre-k09 24/24、
  pre-k01 2/2、pre-k02 3/3。**T2-V2 结构性发现（KO 长条页三方全 0/56）独立复现
  成立且定性为序列口径瓶颈非权重**。
- **AC2 v2b 同实验：PASS（如实）**。letterbox 双 conf 全 0/56（n_pred=0）；
  tile conf≥0.5 **35/56（recall 0.625，precision 0.3465，n_pred 101）**、
  conf≥0.2 43/56（precision 0.2019，n_pred 213）。逐页@0.5：pre-k08 14/27、
  pre-k09 17/24、pre-k01 2/2（23 preds 误检噪声明晰）、pre-k02 2/3。
  **own-manga KO 长条页噪声方向性成立**——V2B 不入切换候选，归 T3 扩标/DSH
  P3-7 处置。
- **AC3 口径建议固化：PASS（提案级零 src）**。KO 域 Gate 评测冻结
  `tile_690x1024_overlap128`（tile 宽=页宽原生无缩放/高 1024/重叠 128 步长
  896/页底补锚点）；tile 内生产序列逐字；页级跨 tile IoU 0.5 conf 降序贪心
  NMS；主口径 conf≥0.5、0.2 仅诊断；基线权重=chiqui7 现役；letterbox 双权重
  全 0/56 仅作对照口径并行登记。裁量点变体（ov256=44/56、ov448=45/56）证实
  **相位方差主导**（GT 框最高 676px ov128/ov448 下无跨 tile 切断（ov256 存在几何切断：pre-k08 #20 h=675.8）；pre-k01 两框 ~55px 高完整
  落格却在 ov256 零检出），ov128 与 GT 采集相位一致（变体证明相位敏感）。生产切换成本估计 ~8.9s/页 CPU
  （≈20× letterbox，GPU 可压）与 tile 序列层实施归 T4。
- **AC4 报告+Handoff+Task 回填：PASS（本轮 docs 提交）**。
- **AC5 零 src；产物摘要入 Git：PASS**。15 文件全在 Task 允许面（doc/tasks/
  +experiments 2 脚本+verification 5 摘要/报告+7 raw）；`-- src/ training_data/`
  空 diff；gitignored 中间产物在 `training_data/sfx-v1/ko-tile-calib/` 不入 Git。

**作者侧复核（workflow 内；正式 Review=DSH r1/r2 见 doc/reviews/）= PASS**（四项复核全部实测通过，未发现等价性缺陷、NMS 去重
错误或零 src 违规；含 1 项过程假差异如实登记——系复核脚本初版丢失 y+y0 平移，
修正后 bit-exact 复现。见 calib-report.md §8）。

## 验证证据

环境：Windows；运行 venv=M2-SFX-FINETUNE-gpu-py312（onnxruntime 1.30.0，
CPUExecutionProvider——与生产 detection_sfx.py:426 同 EP）；被测 commit=b5038659
（主矩阵）→49253b09（提案）。

| AC/场景 | 实际命令/步骤 | 结果 | 日志/产物 |
|---|---|---|---|
| AC1+AC2 全量四组 | `python experiments/M2-KO-TILE-CALIB/tile_calib.py`（GT/权重 sha 断言内置 fail-fast；log:2 chiqui7==pin、:3 v2b 前缀断言） | PASS（letterbox 0/56×4 格；chiqui7 tile 56/56；v2b tile 35/56@0.5） | raw/run-full.log、raw/eval-*.json、eval-matrix.json |
| AC3 裁量点变体 | 同脚本 `--overlap 256` / `--overlap 448`（chiqui7×tile） | PASS（44/56、45/56@0.5；相位方差证据） | raw/eval-chiqui7-tile-ov{256,448}.json、eval-matrix-ov{256,448}.json |
| 数字复算 | `python experiments/M2-KO-TILE-CALIB/recompute_matrix.py`（独立重实现匹配，不 import tile_calib.py） | PASS（`ALL 8 CELLS RECOMPUTED == eval-matrix.json`） | calib-report.md §5 |
| 预处理等价性 | 逐字对照表 13 环节（生产行号逐一核对；复核①再次全量核实） | PASS | preprocess-caliber-table.md；calib-report.md §8-① |
| NMS 去重抽算 | 复核独立 dedup 重跑 pre-k08 conf0.5（31→30 框 bit-exact） | PASS（唯一被压框 conf 0.5607 vs 保留 0.8229 IoU=0.6168 语义正确） | calib-report.md §8-③ |
| AC5 零 src | `git diff --name-only 9258afc0..HEAD`（15 文件允许面）；`git diff 9258afc0..HEAD -- src/ training_data/`（空）；`git status --porcelain src/`（干净） | PASS | calib-report.md §8-④ |

未运行项：生产序列 tile 口径落地（归 T4，本 Task 提案级零 src）；宽≠690/600 的
KO 页 tile 参数化用例（GT 页集仅 690/600 宽，归 T4 扩充）；GPU EP 耗时实测
（成本估计仅 CPU 实测 0.136s/tile 外推，GPU 压缩幅度未测）；own-manga KO 噪声
消融验证（归 T3 扩标轮处置）。

## 接收方式

- 分支 `agent/zcode/M2-KO-TILE-CALIB`，worktree
  `G:/CODEX/New Manga.worktrees/M2-KO-TILE-CALIB-zcode`，base 9258afc0，
  delivery_head 49253b09（docs head 随本提交更新于 Task 回填）。
- 复现：`python experiments/M2-KO-TILE-CALIB/tile_calib.py`
  （venv=M2-SFX-FINETUNE-gpu-py312）；权重 chiqui7=
  `G:/CODEX/New Manga.task-envs/M2-SFX-DETECT/weights/yolo11s-seg.onnx`
  （pin d87389af…）、v2b 只读引用
  `G:/CODEX/New Manga.worktrees/M2-SFX-TRAIN-V2-zcode/training_data/sfx-v1/train-v2/weights/v2b/best.onnx`
  （944e8114…）；GT=R2 final manifest（只读）。
- Reviewer 具体检查入口：calib-report.md §2（矩阵+逐页）、§3（相位方差）、
  §4+§8-①（预处理等价）、§5+§8-②（数字复算）、§8-③（NMS bit-exact）、
  §8-④（零 src+pin 不动）、ko-caliber-proposal.md（口径建议正文）。

## 下一任务建议（必填）

- **Task ID / 标题**：M2-KO-TILE-CALIB 的独立 Review 收口与集成（编排会话代行
  Codex）：review 通过后 merge 进 main 并回填 STATUS/PLAN；**无新实现 Task 待
  释放**——本 Task 为 T3 前置实验，正式 T3（BJ 扩标+KO Gate 评测）与 T4（生产
  tile 序列层落地）均待用户/编排裁决后释放。
- **推荐 Agent / Reviewer**：Codex（集成）；DeepSeek Harness（独立 Review，非
  作者——复核轮已 PASS，正式 review 轮确认口径建议与 T3/T4 归属即可）。
- **推荐原因与前置依赖**：AC1-AC5 全交付+独立复核 PASS，满足进 review/integration
  条件；AC3 口径建议供 T3 KO 域 Gate 正式采信（Gate 数字与训练数据采集口径同构）。
- **Recovery point**：仓库 `G:/CODEX/New Manga`；branch/worktree
  `agent/zcode/M2-KO-TILE-CALIB` @
  `G:/CODEX/New Manga.worktrees/M2-KO-TILE-CALIB-zcode`；base=9258afc0、
  delivery_head=49253b09（docs head 以本提交为准）。worktree 已存在。
- **允许修改路径**：集成轮限于 doc/tasks/M2-KO-TILE-CALIB.md（review_events/
  integration_commit/status=done）、doc/STATUS.md、doc/REBASELINE_PLAN.md
  （编排授权）、doc/reviews/M2-KO-TILE-CALIB-*.md（reviewer 落盘）。
- **禁止范围与新增授权条件**：`src/**`（tile 序列层落地=T4 专属新 Task，须
  Codex 范围授权）；R1/R2/V2 数据与脚本本体只读；cases.json 不动；
  `training_data/sfx-v1/ko-tile-calib/` 中间产物不入 Git。
- **交付物**：review 文档（doc/reviews/）+集成 merge commit+STATUS/PLAN 收口。
- **验证命令、环境与完成 Gate**：`git diff 9258afc0..<merge> -- src/
  training_data/` 为空；`git show <merge>:src/infrastructure/providers/detection_sfx.py | grep d87389af`
  pin 在位；`python experiments/M2-KO-TILE-CALIB/recompute_matrix.py` 复算 8 格
  相等（venv=M2-SFX-FINETUNE-gpu-py312）；Gate=DSH review 结论+集成验证通过。
- **可直接转发给 Agent 的指令**（DSH 正式 review 轮）：
  > 对分支 `agent/zcode/M2-KO-TILE-CALIB`（base 9258afc0，delivery 49253b09，
  > docs head 见 Task）执行独立 review：①读
  > verification/M2-KO-TILE-CALIB/calib-report.md+ko-caliber-proposal.md+
  > preprocess-caliber-table.md+eval-matrix.json（+ov256/ov448）+raw/run-full.log；
  > ②抽查重算：`python experiments/M2-KO-TILE-CALIB/recompute_matrix.py`（8 格
  > ==）、raw JSON 逐页 matched/preds 抽页（pre-k08 tile conf0.5：27/27，
  > sfx_raw=31→page_nms 30）、`git diff 9258afc0..49253b09 -- src/
  > training_data/` 为空、生产 pin d87389af 在 detection_sfx.py:110-112 逐字
  > 在位、run-full.log:2-3 两行 sha 断言、v2b 重指 finally 恢复
  > （tile_calib.py:374/:381-382/:443-444）；③裁定四项：预处理等价性
  > （对照表 13 环节行号抽查）、矩阵数字与建议一致性（tile_690x1024_overlap128
  > 冻结+conf0.5 主口径+chiqui7 基线+v2b 不入候选）、零 src、AC3 提案与 T3/T4
  > 归属清晰；④结论落 doc/reviews/M2-KO-TILE-CALIB-<docs-head>-dsh-r1.md 并
  > 回填 Task review_events。已知登记：directional 禁用「显著」；相位方差
  > （ov128 与 GT 采集相位一致 56/44/45）已在提案 §2/报告 §3 如实登记；T4 成本为 CPU 实测
  > 外推（GPU 未测）。禁改 src/**。

如果没有安全且已授权的后续工作，填写“无需下一步操作”及原因，不创建占位 Task。

## 风险与遗留

- **directional 评测不作门判定**：n=4 页 56 框统计功效低，禁用「显著」；口径
  建议供 T3 Gate 采信，不构成生产切换依据（T4 用户裁决）。
- **相位方差**：tile 口径同页不同锚点相位召回波动 44-56/56；T4 落地时若 Gate
  复测偏离 56/56 需先查相位（ov128 与 R1 采集口径一致是当前最优防御）。
- **成本**：tile 口径 ~8.9s/页 CPU（≈20× letterbox）为 CPU 实测外推，GPU EP
  压缩幅度未实测；超长页 tile 数线性增长（~1 tile/896px）。
- **V2B 双差不入候选**：own-manga KO 长条页噪声方向性成立（pre-k01 2GT 换
  23 preds），处置归 T3 扩标轮/DSH P3-7；不得据本实验反转 T2-V2 的 BJ 考卷
  结论（域不同）。
- **回退方法**：纯 docs+experiments+verification 变更，零 src 零数据链回滚面；
  分支整体可弃置；gitignored 中间产物 `training_data/sfx-v1/ko-tile-calib/`
  可整体删除重生成（tile_calib.py 幂等重跑）。
- **关联 Task**：M2-SFX-TRAIN-V2（done @merge 784e585b，结构性发现来源+DSH
  P3-7 出处）、M2-SFX-ANNOTATE-R1（tile 几何与 _dedup_boxes 复刻来源）、
  M2-SFX-ANNOTATE-R2（GT final manifest 来源）、后续 T3（Gate 正式评测）、
  T4（生产 tile 序列层落地，用户裁决）。

## 实验附录（实验任务必填）

- **数据来源与许可**：GT=R2 final manifest.{val,test}.json KO 4 页 56 框
  （KO=peppercarrot CC-BY-4.0，沿 R1/R2 备案）；权重 chiqui7=生产 pin
  `d87389af…646`（HF 7f5f5c04，零重指）、v2b=T2-V2 产物 `944e8114…18d`
  （只读引用，基座许可边界沿 T2-V2 登记）。
- **数据 Hash**：GT 逐页图像 sha256 对 manifest 断言通过；权重 sha 见 run-full.log:2-3。
- **模型/权重版本与 Hash**：chiqui7 yolo11s-seg.onnx `d87389af4350954143a216bcfe40fd2ad93312cb136534e6073c9c740d98b646`
  （imgsz=1024 metadata_parsed）；v2b best.onnx
  `944e811410933ad6ff8d32446fcc9eef90fb463794e1874ce83035e83acd418d`
  （imgsz=1024 metadata_parsed）。生产 pin 零改动。
- **Provider/Runtime**：onnxruntime 1.30.0 CPUExecutionProvider（与生产
  detection_sfx.py:426 同 EP）；tile 内=生产序列本体（dsfx._letterbox+_sfx_boxes，
  类无关 NMS 0.7、sfx 过滤、conf 过滤先于 NMS）；页级合并=跨 tile IoU 0.5 conf
  降序贪心 NMS。
- **硬件**：CPU 推理（GPU EP 未用于本实验）；网络策略=零下载（权重全本地 sha 断言）。
- **参数**：tile 宽=页宽原生（690/600）、高 1024、重叠 128（步长 896）、末尾补
  `page_h-1024` 锚点；变体 overlap∈{256,448}；conf∈{0.5,0.2} 每 conf 独立完整
  推理；匹配 IoU≥0.5 conf 降序贪心每 GT 至多一预测。
- **运行次数**：主口径 1 次（无参运行=full）；变体各 1 次；复核独立重跑 pre-k08
  tile conf0.5 1 次（bit-exact 复现）。
- **原始结果**：raw/eval-{chiqui7,v2b}-{letterbox,tile}.json（逐框 preds+匹配
  对+tile_stats）、raw/eval-chiqui7-tile-ov{256,448}.json、run-full.log（逐页
  耗时：letterbox 0.3-0.5s/页、tile≈0.136s/tile，pre-k08 tile 7.9s/58 tiles）。
- **质量判断办法**：两口径预处理与成像口径唯一差异（另有 NMS 作用域+页级合并两层有意步骤）本身（预处理对照表 13 环节+共享函数
  本体）；匹配算法与 eval_v2.py 逐字同构；数字经 recompute_matrix.py+复核者独立
  实现双重从盘上复算。
- **失败样例**：letterbox 全零输出（结构性）；v2b tile 误检（pre-k01 23 preds
  vs 2 GT）；ov256 pre-k01 两框零检出（相位方差极端例）。
- **限制**：GT 页集仅 690/600 宽；directional n=4 页；与 R1 密度扫描数字不可
  直比（采集口径差异已登记）；GPU EP 未测。
- **建议**：T3 Gate 采信 ko-caliber-proposal.md 五条口径；T4 落地时先查相位
  方差再扩展页宽参数化；v2b 噪声归 T3 扩标处置。

## 交付链补充（P3-3）

- docs head=76bf2a94（r1 审查对象）；返修=r2 定点复审对象 3517ceda；后续 commit 见分支链尾。

## DSH r1 审查记录（2026-10-05，approved_with_conditions；P1-1/P2-1 返修见上）

- Verdict=approved_with_conditions（1×P1、1×P2、8×P3、4×P4）；全文落 doc/reviews/M2-KO-TILE-CALIB-76bf2a94-dsh-r1.md。
- **P1-1（核心，已闭）**：GT 同源性循环性——KO GT 源自 chiqui7 tile ov128 采集，「56/56 同源复现（见报告 GT 同源性限制段）/P 0.8235」降级为同源复现、「ov128 与 GT 采集相位一致」降级为相位一致；核心结论（letterbox n_pred=0 vs tile n_pred>0=口径瓶颈非权重）锚定 GT 无关事实独立成立；T3 若度量模型质量须另建非 chiqui7 派生 KO GT（提请 T3 裁决）。
- P2-1 复现命令已更正（无参运行）；P3-1/2/3/4/5/P4-1 已落报告 §9；P3-6 治理登记=编排 governance commit 01bfe108 已登记（本 worktree 不含 main 治理 commit，非缺口）；P3-7 署名已更正。
- **T4 材料补强（DSH 建议）**：冻结 ov128 两条硬约束=①overlap≥h_max（本 GT 675.8→≥676）②页级合并层（sfx-only 0.5）为 T4 新造需 fail-fast 纪律+保留 pre-NMS 框。
- 集成 Gate（DSH 无 shell 三项由集成方复跑）：git diff 9258afc0..<merge> -- src/ training_data/ 为空+pin d87389af 在位+recompute_matrix.py 8 格相等。
