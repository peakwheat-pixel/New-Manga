# M2-KO-TILE-CALIB · KO 域 Gate 评测口径提案（AC3，提案级零 src）

状态：实验数据支撑的口径建议，供 T3 正式 Gate 采信；**生产序列切换本身归 T4，
本提案零 src 不动生产代码**。
依据：experiments/M2-KO-TILE-CALIB/tile_calib.py 全量四组 + 裁量点变体两组
（2026-10-05 运行，raw/ 明细与 run-full.log 在库；预处理等价性证据见
同目录 preprocess-caliber-table.md）。

## 1. 实验矩阵（主口径：tile_690x1024_overlap128）

GT：R2 final manifest KO 4 页（pre-k01/k02/k08/k09）56 框；匹配 IoU≥0.5
conf 降序贪心；数字经 recompute_matrix.py 从盘上产物独立复算（8 格全 ==）。

| 权重 | 口径 | conf≥0.5（生产冻结） | conf≥0.2（宽松） |
|---|---|---|---|
| chiqui7 现役（pin d87389af…） | letterbox 整页 | **0/56**（n_pred=0） | **0/56**（n_pred=0） |
| chiqui7 现役 | tile 690x1024 ov128 | **56/56**（recall 1.0，precision 0.8235，n_pred 68） | 56/56（precision 0.6667，n_pred 84） |
| v2b（944e8114…） | letterbox 整页 | **0/56**（n_pred=0） | **0/56**（n_pred=0） |
| v2b | tile 690x1024 ov128 | **35/56**（recall 0.625，precision 0.3465，n_pred 101） | 43/56（recall 0.7679，precision 0.2019，n_pred 213） |

逐页分解（conf≥0.5）：

| 页 | 尺寸（aspect） | GT | chiqui7 tile | v2b tile |
|---|---|---|---|---|
| pre-k08 | 690×51971（1:75） | 27 | 27/27（30 preds） | 14/27（23 preds） |
| pre-k09 | 690×100480（1:146） | 24 | 24/24（28 preds） | 17/24（50 preds） |
| pre-k01 | 690×62133（1:90） | 2 | 2/2（2 preds） | 2/2（23 preds） |
| pre-k02 | 600×18401（1:31） | 3 | 3/3（8 preds） | 2/3（5 preds） |

结构性发现复现：letterbox 口径**双权重、双 conf 全部 n_pred=0**（不是低分，
是零输出）——整页 letterbox 1024 下 690 宽页缩至 ~14px 宽，SFX 类零响应。
T2-V2 结构性发现（三方全 0/56）在本实验独立复现成立。

## 2. 裁量点变体（合同裁量点：主实验顺利加跑，已登记）

chiqui7×tile 三组重叠（conf≥0.5）：

| overlap | 步长 | tiles/4页 | recall | precision | n_pred |
|---|---|---|---|---|---|
| **128（主/R1 先例）** | 896 | 261 | **56/56** | 0.8235 | 68 |
| 256 | 768 | ~345 | 44/56 | 0.6286 | 70 |
| 448 | 576 | ~445 | 45/56 | 0.6164 | 73 |

发现：**tile 口径存在相位方差**——56 框无一高于 676px 高（每框都可完整落入
单 tile，几何覆盖不是瓶颈），但框在 tile 内的相对位置随锚点网格变化，网络
上下文响应随之波动（极端例：pre-k01 两框仅 ~55px 高、任意重叠下必完整落格，
ov128 检出 conf≥0.5 双框、ov256 同框检出消失）。「重叠越大召回越高」不成立。
wording 纪律：n=4 页 directional，禁用「显著」。

## 3. 提案正文（供 T3 KO 域 Gate 评测口径）

### GT 同源性/循环性限制（DSH r1 P1-1，必读）

> **本实验的 GT（KO 4 页 56 框）本身派生于 chiqui7 在 tile ov128 口径下的扫描候选**（R2 正集
> sources=chiqui7-scan，human_review=false 经 AI 代审保留 56/弃 12）。因此：
> ① "chiqui7 tile ov128=56/56 满召回（P 0.8235）"=**同源复现（自洽性证明）**，不是独立召回度量
> ——pred conf 与 GT conf 逐位相同是同权重同页图同口径的确定性必然；precision 0.8235≈1−代审拒绝率
> （12 个 pred 正是被代审 delete 的同一批框），不是独立误检率。
> ② "ov128 实测最优"=**GT 在 ov128 网格上采集的必然相位**；变体（ov256=44/ov448=45）真正证明的是
> **tile 网格相位强烈调制召回**（真发现），不是 ov128 的独立优越性。
> ③ **核心结论锚定在 GT 无关事实上**：letterbox 双权重双 conf 全部 n_pred=0（零输出，绝对事实）
> vs tile n_pred=68/101——「瓶颈=推理序列口径非权重」独立成立，不依赖 GT。
> ④ "与 R1 采集口径同构"从理由移入**限制**：同构正是循环性本身。
> ⑤ **T3 采信前置（提请裁决）**：若 KO Gate 要度量模型质量而非采集一致性，需另建非 chiqui7 派生
> 的 KO GT 切片（哪怕少量人工核验框）——否则 V2B 35/56 与 chiqui7 56/56 之差无法区分「模型差」与「GT 偏」。


1. **成像口径：KO 长条页（宽≤690、aspect>1:20 量级）Gate 评测采 tile 口径
   `tile_<页宽>x1024_overlap128`**，冻结参数：tile 宽=页宽原生无缩放、
   tile 高 1024、重叠 128（步长 896）、末尾补 `page_h-1024` 锚点保证覆盖页底
   （与 R1 素材线采集口径完全同构）。理由：唯一实测非零召回口径；chiqui7
   现役权重该口径 56/56 满召回——KO 域瓶颈确证为序列口径非权重（T2-V2 假设
   的实验确证）；ov128 为三相位实测最优（56/44/45）且与 R1 采集口径一致，
   Gate 数字与训练数据采集口径同构。
2. **tile 内序列：生产序列本体逐字**（letterbox 1024/top-left paste 114 灰/
   BILINEAR、/255 float32 CHW、conf 过滤先于类无关 NMS 0.7、sfx 类后过滤、
   /scale 映射+clip）。理由：预处理对照表（preprocess-caliber-table.md）证明
   两口径共享同一代码路径；Gate 数字因此与生产序列语义严格同构，T4 切换时
   无口径换算。
3. **页级合并：跨 tile IoU 0.5 conf 降序贪心 NMS**（R1 `_dedup_boxes` 逐字）。
   理由：实测削减温和（chiqui7@0.5 四页 raw 70→68，v2b 109→101），无误并
   GT 迹象（chiqui7 满召回不受影响）；沿 R1 先例阈值，不新造参数。
4. **阈值：Gate 主口径 conf≥0.5（生产冻结），conf≥0.2 仅作诊断参考**。
   理由：chiqui7 tile 在 0.5 已满召回且 precision 最高（0.8235）；放宽到 0.2
   召回零增益（56/56 不变）纯增误检（68→84）。v2b 放宽有召回增益
   （35→43）但 precision 崩至 0.2019——以 0.2 数字评 Gate 会奖励高误检配置。
5. **权重口径：KO Gate 基线=chiqui7 现役（tile 口径 56/56）**；v2b tile
   35/56 + precision 0.3465 双差，**own-manga 训练数据 KO 长条页噪声对 tile
   口径的影响方向性成立**（AC2 观察点：极端页 pre-k01 2 GT 换 23 preds），
   与 T2-V2 遗留的 DSH P3-7（训练集内 6 页 KO 长条页标签噪声）处置议题一致，
   归 T3 扩标轮处置。V2B 不因本实验进入切换候选。

## 4. 生产适配成本估计（零 src 提案级；切换实施归 T4）

| 项 | 估计 | 依据 |
|---|---|---|
| 代码面 | 新增 tile 序列层（SfxDetectionProvider 外的切片/合并包装，provider 本体与 pin 断言零改动）；配置沿 TILING env fail-fast 纪律（`NEWMANGA_SFX_TILE_*`） | detection_sfx.py 组装层先例（MangaSfxParallelDetectionProvider）；provider 纯函数边界干净 |
| 单页推理成本 | tile ≈ 0.136s/tile（CPU 实测稳定，4 页 261 tiles）→ 690 宽 webtoon ~65 tiles/页 ≈ **8.9s/页**；letterbox 基线 0.3-0.5s/页 → **约 20×**；GPU EP 可再压。绝对值语境：KO 超长条页内容量本为普通页数十倍 | run-full.log 逐页耗时 |
| 内存 | 整页 RGB 解码峰值 ~208MB/页（690×100480）保留（crop 源），推理张量仅 1024²（~12MB/ tile），与 letterbox 同量级 | tile_calib 运行参数 |
| 校验/契约面 | DetectionRequest/ports 契约零改动；sha pin 断言路径零改动；SfxPolicy/merge 链零改动 | preprocess-caliber-table.md §1 |
| 已知风险 | ①相位方差：同页不同锚点相位召回波动 44-56/56（§2），T4 落地时若 Gate 复测偏离 56/56 需先查相位；②tile 数随页高线性增长（~1 tile/896px），超长页成本线性可控；③宽≠690/600 的 KO 页参数化待 T4 用例扩充 | 本实验 §2；GT 页集仅 690/600 宽 |

## 5. 证据清单（均在库）

- 脚本：experiments/M2-KO-TILE-CALIB/tile_calib.py（1af31e4f+变体参数 commit）、
  recompute_matrix.py（复算核验，8 格 ==）
- 明细：verification/M2-KO-TILE-CALIB/raw/eval-{chiqui7,v2b}-{letterbox,tile}.json
  （主口径 4 份，逐框 preds+匹配对+tile 统计）、
  eval-chiqui7-tile-ov{256,448}.json（裁量点变体）、run-full.log（运行日志含逐页耗时）
- 矩阵：eval-matrix.json（主）+ eval-matrix-ov{256,448}.json（变体）
- 预处理等价性：preprocess-caliber-table.md
