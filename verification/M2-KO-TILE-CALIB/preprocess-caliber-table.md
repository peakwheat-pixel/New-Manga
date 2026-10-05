# M2-KO-TILE-CALIB 预处理逐字对照表

Task 合同（doc/tasks/M2-KO-TILE-CALIB.md）风险条款：tile 切块推理的预处理必须与
生产序列逐字一致（letterbox/归一化/阈值语义），否则实验不等价。本表登记两口径
逐环节对照与实现来源；结论：**两口径共享同一生产代码路径，无第二实现**。

生成：experiments/M2-KO-TILE-CALIB/tile_calib.py（1af31e4f+变体参数）
运行：2026-10-05，venv=M2-SFX-FINETUNE-gpu-py312（onnxruntime 1.30.0，
CPUExecutionProvider——与生产 `detection_sfx.py:426` 逐字同 EP）

## 1. 逐环节对照

| # | 环节 | 生产序列（letterbox 口径） | tile 口径 | 一致性证据 |
|---|------|---------------------------|-----------|-----------|
| 1 | RGB 顺序 | PIL `convert("RGB")` → numpy HxWx3 uint8 | 同左（同一 `load_gt_pages` 装载，页与 tile 同源） | tile_calib.py `load_gt_pages`；tile crop 自同一 `rgb` 对象 |
| 2 | letterbox 尺度 | `min(size/w, size/h)`，round 取整 | **同函数本体**：`dsfx._letterbox(numpy, np_tile, imgsz)`；tile 690/600×1024 → scale=1.0（原生无缩放） | 复用 `src/infrastructure/providers/detection_sfx.py:516-532` 函数本体，零复刻 |
| 3 | resize 算子 | PIL BILINEAR（非 cv2） | 同左（scale=1.0 时 resize 恒等） | 同上（函数本体） |
| 4 | paste 语义 | **top-left** paste 到 114 灰布（非 Ultralytics 居中） | 同左；tile 右侧 334px（690 宽）/424px（600 宽）为 114 灰 | 同上（函数本体） |
| 5 | 归一化 | `/255` float32，CHW（transpose(2,0,1)[None]） | 同左 | 同上（函数本体） |
| 6 | 输入名/imgsz | `session.run(None, {"images": inp})`；imgsz=1024（metadata_parsed） | 同左（同一 session）；两权重 metadata imgsz 均 1024 (metadata_parsed) | 运行日志 `[tile-calib] engine chiqui7/v2b: imgsz=1024 (metadata_parsed)` |
| 7 | conf 语义 | cls_scores **post-sigmoid 无激活**（eval 实证），argmax/max | 同函数本体 `dsfx._sfx_boxes(...)` | 复用 `detection_sfx.py:535-589` 函数本体 |
| 8 | conf 过滤时机 | **NMS 之前**（conf<threshold 不进 NMS 竞争集；每口径独立完整推理） | 同左（`_sfx_boxes(session, inp, scale, conf, ...)` 传入同口径 conf） | 生产语义保持；沿 eval_v2.py:197-201 per-conf provider 先例 |
| 9 | NMS | 类无关 IoU 0.7 over ALL classes（类感知过滤会改变存活集） | 同左（tile 内） | 同上（函数本体 `_nms`） |
| 10 | sfx 类过滤 | NMS **之后**取 sfx（id=2） | 同左 | 同上（函数本体） |
| 11 | 坐标映射 | /scale + clip 到页界；退化框跳过 | 同左（clip 到 tile 界）+ **y+y0 平移回页坐标**（R1 先例逐字） | `detection_sfx.py:603-625` + tile_calib.py `run_tile_caliber`（映射 `b[1]+y0/b[3]+y0`，沿 R1 stage1_preannotate.py:257-258） |
| 12 | 权重供应链 | `_build_engine` sha256 先验断言 pin 再加载 | chiqui7=pin 原样零重指（sha `d87389af…` 逐字核对）；v2b=进程内重指 pin（sha `944e8114…` 前缀断言），**src 零改动**（eval_v2.py:179 先例） | 运行日志两行 sha 断言；`_build_engine` 断言路径 `detection_sfx.py:416-417` |
| 13 | **唯一差异** | 整页成像：690×51971 letterbox 1024 → scale≈0.0197，**页宽缩至 ~14px**（亚像素化） | tile 成像：690×1024 tile → **scale=1.0 原生分辨率** | 本实验的测量对象本身（对照变量），非预处理偏差 |

## 2. tile 几何（R1 复刻来源）

| 参数 | 值 | 来源 |
|---|---|---|
| tile 宽 | =页宽原生（690/600），无缩放 | R1 stage1_preannotate.py:239（`tile_w = page_w`） |
| tile 高 | 1024 | R1 stage1_preannotate.py:156（`K_TILE_H = 1024`） |
| 重叠（主口径） | 128（步长 896） | R1 stage1_preannotate.py:157（`K_TILE_OVERLAP = 128`） |
| 末尾补锚点 | `page_h - 1024`（当 `ys[-1]+1024 < page_h`） | R1 stage1_preannotate.py:243-244 |
| y 映射 | `y + y0` 平移 | R1 stage1_preannotate.py:257-258 |
| 页级跨 tile NMS | IoU 0.5，conf 降序贪心 | R1 `_dedup_boxes`（stage1_preannotate.py:172-191）逐字复刻进 tile_calib.py `dedup_boxes`（不跨 worktree import，来源行号已在代码注释登记） |

tile 数/页（本实验 4 页）：pre-k01=70、pre-k02=21、pre-k08=58、pre-k09=112（共 261/（权重×conf））。

## 3. 与 R1 scan 口径的登记差异（非等价性缺陷，是口径选择）

R1 scan（素材线采集）走 conf_scan_diag `run_inference`（conf floor **0.01** +
NMS 后保留全类框，采集形态）；本实验 tile 内沿用**生产 conf 语义**（conf≥口径值
先过滤再 NMS，0.5/0.2 双口径各自独立完整推理）——与 eval_v2.py 的 letterbox
评测语义严格同构，保证「tile vs letterbox」唯一差异=成像口径本身。故本实验
数字与 R1 密度扫描数字不可直比（采集口径），与 eval_v2.py KO 数字同构可比。

## 4. 匹配口径（与 V2 评测逐字同构）

- conf≥0.5（生产冻结）/≥0.2（宽松）双口径；
- box IoU≥0.5、pred conf 降序贪心、每 GT 至多一预测（eval_v2.py:68-97 `match_gt` 逐字复刻）；
- GT=R2 final manifest.{val,test}.json KO 4 页 56 框，逐页图像 sha256 对 manifest 断言。

## 5. 数字复算核验（验收判据「数字从盘上产物复算」）

experiments/M2-KO-TILE-CALIB/recompute_matrix.py：从 R2 manifest GT + 4 个
raw JSON preds **独立重实现**匹配算法（不 import tile_calib.py），8 格全部
`== eval-matrix.json`（运行输出 ALL 8 CELLS RECOMPUTED == eval-matrix.json）。
