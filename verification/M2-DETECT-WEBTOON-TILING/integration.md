# M2-DETECT-WEBTOON-TILING 集成记录（代行 Codex / 编排会话）

- 分支 `agent/zcode/M2-DETECT-WEBTOON-TILING`；链：3-followup release `f99a6c55` → `29a7f5b5`(implement) → `36b61c3a`(docs)
- Review：DSH r1 **PASS（0×P0/P1/P2 阻塞项）**——逐条声称静态全部成立；DSH 独立复算：块数公式手算 K01=70/K02=21/K04=32/K05=52/K08=58 与 JSON 全部一致；**clip 等价性的经验核验比 Owner 论证更强**（DIAG 全量 226 框 x1 max 674.4<690、y1 max 62055.8<62133，无框跨界，唯一贴边 tile68 y1 超 crop 上界 0.3px=浮点舍入）；全 diff 仅 5 行删除、既有测试零删除；红绿 44F/29P→73P 自洽（`doc/reviews/M2-DETECT-WEBTOON-TILING-29a7f5b5-dsh-r1.md`，sha256 `82dc2f40…526`）

## 修复内容（正式）

- `detection_manga.py` tiling 路径：触发 height/width>4.0（严格大于；webtoon 实测 30.7-90.0 vs 普通页 ≤1.41，两侧 ~20× 余量）；env `NEWMANGA_DETECTOR_TILING_{TRIGGER_RATIO,TILE_SIZE,OVERLAP,NMS_IOU}` 默认 4.0/1024/128/0.5（非法值 fail-fast）；精确步进切块→灰 114 pad→同 engine 逐块推理→共享纯过滤块界 clip→+原点回映→conf 序贪心 NMS（严格大于删）；options provenance tiling/tiling_tiles/text_boxes_pre_merge
- qualification **GATE PASS**：5/5 长条漫页生产 region>0（K01 180/K02 93/K04 113/K05 62/K08 60；K01 193 框与 DIAG 逐值复现；MERGE 合并率仅 1.6-7.2% 无第二层问题）；延迟 K01 20.1s≤25s/K02 6.0/K04 9.3 全达预算；阈值曲线 0.5→0.4 无爆炸；690×690 对照同量级（+2.6%）；K19=0（正确）；BJ02=5 region 零变化
- 测试：+45 条（红 44F→绿 73P）；三套件 575+1skipped 0 failed（主 venv 基线 530+1sk）；粒度登记：ogkalu tiling 框=气泡文本块级（K01 180 region 远细于 docTR 同页 15 合并后）——留产品观测；F4（无字页 INVALID_INPUT 口径）维持登记不修

## DSH 9×P3/P4 登记为紧邻 follow-up（不阻塞集成）

R1 `_tiling_config()` 裸 ValueError 打破「普通页零变化」（env 非法值在普通页也 raise）；R2 clip vs 中心点丢弃等价论证补强（DSH 经验核验已补强）；R3 空/空白 env 静默回落默认 vs never-silent-default；R4 fail-fast 矩阵补联合路径+nan/inf；R5 2D 横向切块无真实页证据；R6 20.1s/页的 UI/IPC 超时与进度面影响登记；R7 qualification 审计项；R8 「逐字节未动」表述精确化（可执行语句零 diff+docstring 更新）；R9 红态复现方法+私有符号耦合。**R1/R3 为几行代码加固候选**，归 next detection hygiene slice。

## 集成运行时项

- git 层：Owner 自检 porcelain 干净/diff --check EXIT=0/7 允许面文件（DSH 静态核对一致）
- post-merge 三套件：src 单文件改动+新测试，merge 后复跑登记于 close commit
