# M2-KO-TILE-CALIB · KO 长条页推理口径校准实验报告（AC1-AC5）

Task：[doc/tasks/M2-KO-TILE-CALIB.md](../../doc/tasks/M2-KO-TILE-CALIB.md)（T3 前置，@用户裁决按推荐释放）。
分支 `agent/zcode/M2-KO-TILE-CALIB`，base `9258afc0`，worktree
`G:/CODEX/New Manga.worktrees/M2-KO-TILE-CALIB-zcode`。
运行：2026-10-05，venv=M2-SFX-FINETUNE-gpu-py312（onnxruntime 1.30.0，
CPUExecutionProvider——与生产 `detection_sfx.py:426` 逐字同 EP）。
脚本：experiments/M2-KO-TILE-CALIB/tile_calib.py（主口径+裁量点变体）、
recompute_matrix.py（复算核验）。**提案级零 src**——生产序列切换归 T4。

## 0. 结论摘要

- **预期成立**：tile 切块口径召回 0/56→**56/56**（chiqui7 现役权重，conf≥0.5
  同源复现、precision 0.8235≈1−代审拒绝率，见 §1 限制段）——KO 域瓶颈确证为**推理序列口径（tile vs
  letterbox）非模型权重**，T2-V2 结构性发现（三方全 0/56）独立复现成立且定性为
  **零输出非低分**（letterbox 双权重双 conf n_pred=0）。
- **口径建议**（AC3，详见 §6 与 [ko-caliber-proposal.md](ko-caliber-proposal.md)）：
  KO 域 Gate 评测冻结 `tile_690x1024_overlap128` 口径；基线权重=chiqui7 现役；
  v2b tile 35/56+precision 0.3465 双差（own-manga KO 长条页噪声方向性成立），
  不入切换候选，归 T3 扩标/DSH P3-7 处置。
- **生产切换成本**（提案级估计）：tile ≈ 8.9s/页 CPU（≈20× letterbox，GPU 可压）
  与 tile 序列层实施归 T4；本 Task 零 src。
- **作者侧复核（workflow 内）= PASS**：四项复核全部通过，未发现等价性缺陷、NMS 去重
  错误或零 src 违规（§8）。

## 1. 实验设置

### GT 同源性/循环性限制（DSH r1 P1-1，必读）

> **本实验的 GT（KO 4 页 56 框）本身派生于 chiqui7 在 tile ov128 口径下的扫描候选**（R2 正集
> sources=chiqui7-scan，human_review=false 经 AI 代审保留 56/弃 12）。因此：
> ① "chiqui7 tile ov128=56/56（同源复现，见 GT 同源性限制）（P 0.8235）"=**同源复现（自洽性证明）**，不是独立召回度量
> ——pred conf 与 GT conf 逐位相同是同权重同页图同口径的确定性必然；precision 0.8235≈1−代审拒绝率
> （12 个 pred 正是被代审 delete 的同一批框），不是独立误检率。
> ② "ov128 与 GT 采集相位一致"=**GT 在 ov128 网格上采集的必然相位**；变体（ov256=44/ov448=45）真正证明的是
> **tile 网格相位强烈调制召回**（真发现），不是 ov128 的独立优越性。
> ③ **核心结论锚定在 GT 无关事实上**：letterbox 双权重双 conf 全部 n_pred=0（零输出，绝对事实）
> vs tile n_pred=68/101——「瓶颈=推理序列口径非权重」独立成立，不依赖 GT。
> ④ "与 R1 采集口径同构"从理由移入**限制**：同构正是循环性本身。
> ⑤ **T3 采信前置（提请裁决）**：若 KO Gate 要度量模型质量而非采集一致性，需另建非 chiqui7 派生
> 的 KO GT 切片（哪怕少量人工核验框）——否则 V2B 35/56 与 chiqui7 56/56 之差无法区分「模型差」与「GT 偏」。


| 项 | 值 | 证据 |
|---|---|---|
| GT | R2 final manifest（val+test）KO 4 页 **56 框**：pre-k08（690×51971，1:75，27 框）、pre-k09（690×100480，1:146，24 框）、pre-k01（690×62133，1:90，2 框）、pre-k02（600×18401，1:31，3 框）；逐页图像 sha256 对 manifest 断言通过 | eval-matrix.json `gt_source` |
| 权重① | chiqui7 现役 `M2-SFX-DETECT/weights/yolo11s-seg.onnx`，sha256 `d87389af…646` **== 生产 pin，零重指**；imgsz=1024（metadata_parsed） | run-full.log:2；`detection_sfx.py:110-112` |
| 权重② | v2b best.onnx（T2-V2 产物，只读引用），sha256 `944e8114…18d` 前缀断言；进程内重指 pin，finally 恢复（`tile_calib.py:374`、`:381-382`、`:443-444`，eval_v2.py:179 先例） | run-full.log:3 |
| 口径 A | **letterbox 整页**=生产序列原样 `SfxDetectionProvider.detect`（letterbox 1024/类无关 NMS 0.7/sfx 过滤/CPUExecutionProvider） | preprocess-caliber-table.md §1 |
| 口径 B | **tile 切块**=R1 `scan_mode=tile_690x1024_overlap128` 复刻：tile 宽=页宽原生无缩放、高 1024、重叠 128（步长 896、末尾补 `page_h-1024` 锚点保证覆盖页底）；每 tile 生产序列本体推理（`dsfx._letterbox`+`_sfx_boxes`，零第二实现）；页级跨 tile IoU 0.5 conf 降序贪心 NMS（R1 `_dedup_boxes` 逐字） | tile_calib.py:288-289（调函数本体）、:188-198（tile_ys）、:163-185（dedup_boxes）；R1 stage1_preannotate.py:156-157/:172-191/:238-258 |
| 匹配 | box IoU≥0.5、pred conf 降序贪心、每 GT 至多一预测（eval_v2.py:68-97 `match_gt` 逐字复刻；IOU_MATCH=0.5 `:47`、CONFS=(0.5,0.2) `:46`） | preprocess-caliber-table.md §4 |
| tile 数/页 | pre-k01=70、pre-k02=21、pre-k08=58、pre-k09=112（共 261/（权重×conf）） | run-full.log:4-7 |

wording 纪律：n=4 页 directional 评测，统计功效低，结论禁用「显著」；0 也如实。

## 2. 主口径四组召回矩阵（AC1+AC2）

GT=56 框；IoU≥0.5 conf 降序贪心；**8 格均经 recompute_matrix.py 从盘上 raw JSON
复算相等**（§5；独立复核另用自己的匹配实现复算亦逐格相等，§8-②）。

| 权重 | 口径 | conf≥0.5（生产冻结） | conf≥0.2（宽松） |
|---|---|---|---|
| chiqui7 现役（pin d87389af…） | letterbox 整页 | **0/56**（n_pred=0） | **0/56**（n_pred=0） |
| chiqui7 现役 | tile 690x1024 ov128 | **56/56**（recall 1.0，precision 0.8235，n_pred 68） | 56/56（precision 0.6667，n_pred 84） |
| v2b（944e8114…） | letterbox 整页 | **0/56**（n_pred=0） | **0/56**（n_pred=0） |
| v2b | tile 690x1024 ov128 | **35/56**（recall 0.625，precision 0.3465，n_pred 101） | 43/56（recall 0.7679，precision 0.2019，n_pred 213） |

逐页分解（conf≥0.5；matched/GT、preds=页级 NMS 后框数，自盘上 raw JSON
`per_sample` 逐页读出）：

| 页 | 尺寸（aspect） | GT | chiqui7 tile | v2b tile |
|---|---|---|---|---|
| pre-k08 | 690×51971（1:75） | 27 | **27/27**（30 preds） | 14/27（23 preds） |
| pre-k09 | 690×100480（1:146） | 24 | **24/24**（28 preds） | 17/24（50 preds） |
| pre-k01 | 690×62133（1:90） | 2 | **2/2**（2 preds） | 2/2（**23 preds**，误检噪声明晰） |
| pre-k02 | 600×18401（1:31） | 3 | **3/3**（8 preds） | 2/3（5 preds） |

- **结构性发现独立复现（零输出非低分）**：letterbox 口径双权重、双 conf 全部
  n_pred=0——不是低分被阈值切掉，是零输出。整页 letterbox 1024 下 690 宽页缩至
  ~14px 宽（scale≈0.0197），SFX 类零响应。T2-V2「三方全 0/56」的根因定性由此
  实验确证：**序列口径瓶颈，非权重**。
- **v2b tile 双差**：35/56 召回低于 chiqui7 同源复现召回（口径差非独立性能差），precision 0.3465 亦远低
  （pre-k01 极端例：2 GT 换 23 preds）——**own-manga 训练数据中 KO 长条页噪声
  对 tile 口径的影响方向性成立**（AC2 观察点），与 T2-V2 遗留的 DSH P3-7
  （训练集内 6 页 KO 长条页标签噪声）处置议题一致，归 T3 扩标轮处置。V2B 不因
  本实验进入切换候选。

## 3. 裁量点变体（合同裁量点：主实验顺利加跑，已登记）

chiqui7×tile 三组重叠（conf≥0.5；eval-matrix-ov{256,448}.json）：

| overlap | 步长 | recall | precision | n_pred |
|---|---|---|---|---|
| **128（主/R1 先例）** | 896 | **56/56** | 0.8235 | 68 |
| 256 | 768 | 44/56 | 0.6286 | 70 |
| 448 | 576 | 45/56 | 0.6164 | 73 |

发现：**tile 口径存在相位方差**——GT 框最高 676px、ov128/ov448 下无跨 tile 切断（ov256 几何切断：pre-k08 #20）问题（每框都
可完整落入单 tile，几何覆盖不是瓶颈），但框在 tile 内的相对位置随锚点网格变化，
网络上下文响应随之波动。极端例（盘上 raw 复核）：pre-k01 两框仅 ~55px 高、任意
重叠下必完整落格，ov128 检出 conf≥0.5 双框（2/2），ov256 同框检出消失
（0/2，preds=0）。三相位 56/44/45 亦否证「重叠越大召回越高」的单调假设。
**ov128 与 GT 采集相位一致**，且与 R1 素材线采集口径一致。

## 4. 预处理等价性对照（AC 合同风险条款落实）

逐字对照表：[preprocess-caliber-table.md](preprocess-caliber-table.md)（13 环节）。
结论：**两口径共享同一生产代码路径，无第二实现**。要点：

- tile 口径直接调用 `dsfx._letterbox`/`dsfx._sfx_boxes` 函数本体
  （`tile_calib.py:288-289`，零复刻），与生产 provider.detect 序列
  （detection_sfx.py:290-310：`_build_engine`→`_letterbox`→`_sfx_boxes(conf)`）
  同构；每 conf 独立完整推理（tile_calib.py:401-414）符合生产 conf 语义
  （conf 过滤先于类无关 NMS 0.7，sfx 类后过滤，/scale 映射+clip）。
- tile 几何与 R1 素材线逐字同构：K_TILE_H/K_TILE_OVERLAP（stage1_preannotate.py:156-157）、
  `_dedup_boxes`（:172-191）、tile 几何+y+y0 平移（:238-258）。
- 环节 13（成像口径差异 scale 0.0197 vs 1.0）如实登记为**实验测量对象本身**
  （对照变量），非预处理偏差。
- 与 R1 scan 口径的已知差异（采集 conf floor 0.01 vs 生产 conf 语义）已在对照表
  §3 登记：本实验数字与 R1 密度扫描数字不可直比，与 eval_v2.py KO 数字同构可比。

## 5. 数字复算核验（验收判据「数字从盘上产物复算」）

experiments/M2-KO-TILE-CALIB/recompute_matrix.py：从 R2 manifest GT + 盘上 raw
JSON preds **独立重实现**匹配算法（不 import tile_calib.py），8 格全部
`== eval-matrix.json`（运行输出 `ALL 8 CELLS RECOMPUTED == eval-matrix.json`）。
独立复核（§8-②）另用复核者自己的匹配实现从盘上 raw JSON 复算 8 格，逐格相等。

## 6. 口径建议（AC3，提案级）

正文与理由详见 [ko-caliber-proposal.md](ko-caliber-proposal.md)。要点：

1. **成像口径**：KO 长条页（宽≤690、aspect>1:20 量级）Gate 评测冻结
   `tile_<页宽>x1024_overlap128`（tile 宽=页宽原生无缩放/高 1024/重叠 128 步长
   896/页底补锚点）——唯一实测非零召回口径；ov128 三相位与 GT 采集相位一致且与 R1 采集
   口径同构。
2. **tile 内序列**：生产序列本体逐字（预处理对照表证明共享代码路径）——Gate
   数字与生产序列在预处理与成像口径上同构，T4 切换时须新造页级合并层，并非零换算。
3. **页级合并**：跨 tile IoU 0.5 conf 降序贪心 NMS（R1 `_dedup_boxes` 逐字）；
   实测削减温和（chiqui7@0.5 四页 raw 70→68）无误并 GT 迹象。
4. **阈值**：Gate 主口径 conf≥0.5（生产冻结），conf≥0.2 仅诊断——chiqui7 tile
   在 0.5 已同源满召回且 precision 最高（0.8235），放宽到 0.2 召回零增益纯增误检
   （68→84）；以 0.2 数字评 Gate 会奖励高误检配置（v2b precision 崩至 0.2019）。
5. **基线权重**：KO Gate 基线=chiqui7 现役（tile 56/56（同源复现，见 GT 同源性限制） precision 0.82
   ——KO 瓶颈确证为序列口径非权重）；letterbox 双权重全 0/56 仅作对照口径并行
   登记；V2B tile 35/56+precision 0.35 双差不入切换候选（own-manga KO 长条页
   噪声方向性成立，归 T3 扩标/DSH P3-7 处置）。

## 7. 生产适配成本估计（提案级；切换实施归 T4）

| 项 | 估计 | 依据 |
|---|---|---|
| 单页推理成本 | tile ≈ 0.136s/tile（CPU 实测，4 页 261 tiles）→ 690 宽 webtoon ~65 tiles/页 ≈ **8.9s/页**；letterbox 基线 0.3-0.5s/页 → **约 20×**；GPU EP 可再压 | run-full.log 逐页耗时 |
| 代码面 | 新增 tile 序列层（SfxDetectionProvider 外的切片/合并包装，provider 本体与 pin 断言零改动）；配置沿 TILING env fail-fast 纪律（`NEWMANGA_SFX_TILE_*`） | detection_sfx.py 组装层先例 |
| 内存 | 整页 RGB 解码峰值 ~208MB/页（690×100480）保留；推理张量仅 1024²/ tile，与 letterbox 同量级 | tile_calib 运行参数 |
| 契约面 | DetectionRequest/ports、sha pin 断言路径、SfxPolicy/merge 链零改动 | preprocess-caliber-table.md §1 |
| 已知风险 | ①相位方差（44-56/56 波动，T4 落地若 Gate 复测偏离 56/56 先查相位）；②tile 数随页高线性增长（~1 tile/896px）；③宽≠690/600 的 KO 页参数化待 T4 用例扩充（GT 页集仅 690/600 宽） | §3；GT 页集 |

## 8. 独立复核（非作者，2026-10-05）= PASS

四项复核全部通过，未发现等价性缺陷、NMS 去重错误或零 src 违规。逐项证据：

### ① 预处理等价性——逐字对照表核实：属实

对照表 preprocess-caliber-table.md 引用的全部生产行号逐一核对无误：
SFX_NMS_IOU=0.7（src/infrastructure/providers/detection_sfx.py:121）、
SFX_CLASS_ID=2（:138）、CPUExecutionProvider（:426）、`_build_engine` sha 先验
断言（:391 起，断言体 :416-421）、`_letterbox`（:516，min-scale/round/PIL
BILINEAR/top-left paste 114 灰/255 float32/CHW）、`_sfx_boxes`（:535，conf
post-sigmoid 无激活→conf 过滤先于类无关 NMS 0.7→sfx 类后过滤→/scale+clip+
退化跳过）、`_nms`（:592）、`_map_back`（:603）；eval_v2.py 的 match_gt 贪心
匹配（:68-97）、IOU_MATCH=0.5（:47）、CONFS=(0.5,0.2)（:46）、进程内重指 pin
先例（:179）、per-conf provider 先例（:197-201）。tile 口径 tile_calib.py:288-289
直接调用 dsfx._letterbox/dsfx._sfx_boxes 函数本体（零第二实现），与生产
provider.detect 序列（detection_sfx.py:290-310）同构；每 conf 独立完整推理
（tile_calib.py:401-414）符合生产 conf 语义。R1 复刻来源属实：
K_TILE_H/K_TILE_OVERLAP（experiments/M2-SFX-ANNOTATE-R1/stage1_preannotate.py:156-157）、
`_dedup_boxes`（:172-191）、tile 几何+y+y0 平移（:238-258）与 tile_calib.py
tile_ys（:188-198）/run_tile_caliber（:263-303）/dedup_boxes（:163-185）逐字同构。

### ② pre-k08 tile 口径召回独立重算：27/27 复现

独立复核脚本（写于 %TEMP%，未进仓库，**不 import tile_calib.py**，仅只读 import
生产 detection_sfx）：GT 独立装载自 R2 final manifest（pre-k08 27 框，690×51971，
图像 sha256 与 manifest 断言通过）；chiqui7 权重 sha256==生产 pin d87389af… 断言
通过后经生产 `_build_engine` 加载（imgsz=1024 metadata_parsed）。独立实现 tile
几何（宽=页宽、高 1024、步长 896、末尾补页底）得 58 tiles == raw JSON
n_tiles=58；逐 tile 生产序列推理得 pre-NMS 31 框 == tile_stats.sfx_raw=31；
独立贪心匹配（IoU≥0.5 conf 降序）重算召回 27/27 == raw JSON matched=27/27。
纯盘上 preds（30 框）独立匹配重算亦 27/27。顺带从盘上 raw JSON 用复核者自己的
匹配实现独立复算**全部 8 格矩阵**，与 eval-matrix.json 逐格相等（chiqui7
letterbox 0/56×2、chiqui7 tile 56/56 conf0.5+56/56 conf0.2、v2b letterbox
0/56×2、v2b tile 35/56 conf0.5+43/56 conf0.2）——未依赖作者的
recompute_matrix.py，独立性更强。

### ③ 跨 tile NMS 去重正确性抽算（pre-k08 conf0.5）：正确

计数自洽：4 页×2 conf 的 sfx_raw 全部 == per_tile 逐块 sfx_raw 之和，
after_nms ≤ sfx_raw。重跑验证：31 框经独立 dedup（conf 降序贪心 IoU≥0.5，与 R1
`_dedup_boxes` 逐字同构）后 30 框，与盘上 raw JSON preds 逐框对照
max_coord_delta=0.0000px、max_conf_delta=0.000000、mismatch=0
（**bit-exact**，同机同 CPUExecutionProvider 确定性复现）。被压掉的唯一 1 框
正向语义：conf=0.5607（tile y0=14336）与保留框 conf=0.8229（同 tile）
IoU=0.6168≥0.5 → 保高 conf 压低 conf，去重语义正确。另：tile 映射回页坐标后 y
无需再 clip——`_map_back` 已 clip 到 tile 内 [0,th]，y+y0≤y1≤page_h，数学上
不可能越界，非缺陷。

### ④ 零 src + 生产 pin 不动：成立

`git diff --name-only 9258afc0..HEAD` 共 15 文件，全部位于 doc/tasks/、
experiments/M2-KO-TILE-CALIB/、verification/M2-KO-TILE-CALIB/；
`git diff 9258afc0..HEAD -- src/ training_data/` 输出 0 行；
`git status --porcelain src/` 干净，复核全程 worktree 保持 clean（结束前复验
0 改动）。生产 pin 未动：detection_sfx.py:110-112 `SFX_WEIGHTS_SHA256=
"d87389af…646"` 逐字在位；run-full.log:2 chiqui7 sha256==pin 断言、:3 v2b
sha256=944e8114… 前缀断言；v2b 进程内重指 pin（tile_calib.py:374）均以 finally
恢复原 pin（:381-382、:443-444），与 eval_v2.py:179 先例同形，src 零改动。
复核运行环境 onnxruntime 1.30.0 CPUExecutionProvider
（G:/CODEX/New Manga.task-envs/M2-SFX-FINETUNE-gpu-py312），与对照表登记一致。

### 复核过程说明（如实登记）

复核者自己的第二次 NMS 语义脚本初版丢失 y+y0 平移导致 kept=29 的假差异，系
**复核脚本错误而非产物错误**，修正平移后重跑得 kept=30 且与盘上一致；该过程
错误不涉及任何盘上产物。无未运行的 ask 指定检查项。

## 9. 诚实边界

> DSH r1 P3-5 证据缺口登记：raw 未存页级 NMS 前框坐标（仅计数），该步无法仅凭盘上产物复算（复核员以重跑推理验证）；后续实验落 pre-NMS 框。
> DSH r1 P3-1 限定：「ov128/ov448 下无跨 tile 切断（ov256 几何切断：pre-k08 #20）」仅对 ov128/ov448 成立——ov256 下 pre-k08 #20（h=675.8）几何切断+相位双重归因（结构保证需 overlap≥h_max≈676，ov128 仅保证 h≤128）。
> DSH r1 P3-2 更正：变体 tiles 数 ov256=304、ov448=404（此前误记 ~345/~445；成本估计不受影响）。
> 措辞限定（DSH r1 P3-4）：tile 与 letterbox 的「唯一差异」=**预处理与成像口径**；tile 化另有 NMS 作用域变化（类无关 0.7 整页→每 tile 内）与新增页级合并（sfx-only IoU 0.5）两层有意步骤，T4 须新造页级合并层。
> 署名更正（DSH r1 P3-7）：§8「作者侧复核（workflow 内）」=**作者侧复核（workflow 内）**；正式独立 Review 见 doc/reviews/M2-KO-TILE-CALIB-76bf2a94-dsh-r1.md。
> 数值精度（DSH r1 P4-1）：GT 框最高 675.8px。

- **directional 评测**：n=4 页 56 框，统计功效低，全部结论禁用「显著」；0 也
  如实登记。
- **GT 页集仅 690/600 宽**：宽≠690/600 的 KO 页 tile 参数化未覆盖，归 T4 用例
  扩充。
- **本实验为提案级**：口径建议供 T3 KO 域 Gate 采信，生产序列切换本身归 T4，
  本 Task 零 src 不动生产代码。
- **v2b 噪声方向性非定量归因**：own-manga KO 长条页标签噪声与 v2b 误检的因果
  强度未消融验证，处置归 T3 扩标轮/DSH P3-7。
- **与 R1 密度扫描数字不可直比**（采集口径 conf floor 0.01 vs 生产 conf 语义），
  见 preprocess-caliber-table.md §3。

## 10. 证据清单（均在库）

- 脚本：experiments/M2-KO-TILE-CALIB/tile_calib.py、recompute_matrix.py
- 主口径矩阵：verification/M2-KO-TILE-CALIB/eval-matrix.json；变体
  eval-matrix-ov{256,448}.json
- 逐框明细：raw/eval-{chiqui7,v2b}-{letterbox,tile}.json（含 preds/匹配对/
  tile_stats）、raw/eval-chiqui7-tile-ov{256,448}.json、raw/run-full.log
- 预处理对照：preprocess-caliber-table.md；口径提案：ko-caliber-proposal.md
- Handoff：doc/handoffs/M2-KO-TILE-CALIB-zcode-20261005.md
