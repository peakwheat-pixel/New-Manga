---
id: M2-DETECT-WEBTOON-TILING
title: "webtoon 长条漫 ogkalu tiling 检测修复（建议 A 第二步：按 DIAG 冻结口径实施，解锁 ko 6 case）"
kind: feature
status: done  # DSH r1 PASS（0×P0/P1/P2 阻塞；9×P3/P4 建议登记紧邻 follow-up）→ 集成（次序首位）
approval: user_ruling_2026-10-01_three_followups_all
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权+自治授权）
depends_on: [M2-DETECT-WEBTOON-DIAG, M2-TA3-B2]
base_commit: f534c3e7
branch: agent/zcode/M2-DETECT-WEBTOON-TILING
worktree: G:/CODEX/New Manga.worktrees/M2-DETECT-WEBTOON-TILING-zcode
delivery_head: 29a7f5b5（implement=29a7f5b5 → handoff/Task 回填=文档 commit；分支 base=f99a6c55=批次 release，任务书 base_commit=f534c3e7 为授权时点）
tip_note: handoff=doc/handoffs/M2-DETECT-WEBTOON-TILING-29a7f5b5.md；落点=detection_manga.py 单文件（触发 h/w>4.0 严格、env NEWMANGA_DETECTOR_TILING_* 默认 1024/128/0.5、DIAG 步进切块+灰114 pad+共享纯过滤块界 clip+原点回映+conf 序贪心 NMS 严格大于删）；三套件 575+1skipped 0 failed=基线 530+1sk+新增 45；qualification GATE PASS（K01 180 region/193 框=DIAG 逐值、20.1s≤25s；K02 93/6.0s；K04 113/9.3s；K05 62；K08 60；690 对照 111 块 198 框同量级；K19=0 正确；BJ02=5 零变化）
---

# M2-DETECT-WEBTOON-TILING：长条漫 tiling 检测修复

## 背景（M2-DETECT-WEBTOON-DIAG 定案）

根因已定案：`detection_manga.py` `_detect_text_boxes` 把整页直传 `RTDetrImageProcessor`（size 640×640、无 letterbox），webtoon 长条漫（690×62133）垂直压缩 ~97× 致目标消失（raw max conf 0.204）。决定性证据：同页同权重同阈值 1024² 块级推理 → 193 个合并前文本框（NMS 数据已落盘：30/33 删框在重叠带、IoU mean 0.848）。修复=tiling+坐标回映（方案 A，契约零变更：DetectionRequest/Response 与 MERGE_* 输入不变）。

## 交付（AC）

1. **AC1 tiling 路径**：`detection_manga.py` 内部实现——触发条件按页面高宽比（如 h/w 超阈值启用 tiling，普通页走原路径**零行为变化**）；块尺寸/重叠/NMS IoU 参数**配置化**（env 先例 `NEWMANGA_SFX_CONF_THRESHOLD` 或 settings，Owner 勘察后选型留痕）；块级推理坐标回映+跨块 NMS 去重（DIAG 已验证参数：1024²、重叠 128px、NMS IoU 0.5 可作默认，配合 R5 建议）。
2. **AC2 测试**（先红后绿）：普通页路径零变化（既有检测测试不动全过）；长条漫触发判定单测；坐标回映正确性单测（合成框跨块）；跨块 NMS 去重单测；无权重环境 typed `PROVIDER_DEPENDENCY_MISSING` 保持。
3. **AC3 qualification（DIAG 冻结口径，逐条执行）**：`experiments/M2-DETECT-WEBTOON-TILING/qualify_tiling.py`——**5 张 webtoon_long_strip**（K01/K02/K04/K05/K08，路径见 case-selection.json）经生产 `provider.detect`：**Gate=每张 region 数>0**（生产 region 层级，非合并前文本框；预期同时报告合并后块数）；CPU 延迟预算 K01 ≤25s / K02 ≤10s / K04 ≤15s；**≥2 个阈值点候选数曲线**（0.5 与 0.4 或 0.25）；**690×690 原生尺度块对照组**（≈1.0× 重采样，块数~1.6×，验证分辨率假设）；K19（无字页）确认仍 0 候选（正确行为，本 Task 不修其 INVALID_INPUT 口径——F4 登记为相邻发现）。
4. **AC4 文档**：docstring（tiling 触发/参数/回映/NMS 语义）；Task frontmatter+AC 表回填；handoff（含 DSH review 指引）；发布形态影响评估（无新依赖→闭包/GATE 不涉及，登记确认）。

## 允许修改面

`src/infrastructure/providers/detection_manga.py`、`tests/`（detection 相关）、`experiments/M2-DETECT-WEBTOON-TILING/**`、`verification/M2-DETECT-WEBTOON-TILING/**`、Task/Handoff。

## 禁改面

`src/infrastructure/providers/detection_sfx.py`、`detection_doctr.py`、`src/ports/**`（DetectionRequest/Response 契约零变更）、`src/bootstrap/**`（如配置通道必须动装配则先在 handoff 登记移交集成方）、`doc/contracts/**`、`packaging/**`、`apps/**`、`experiments/M2-TA3-A|B|DETECT-WEBTOON-DIAG/**`（只读）、`doc/STATUS.md`。

## 纪律

- fail-closed 不放宽（tiling 内部失败 typed；普通页零变化）；conf 阈值 0.5 生产默认不变（qualification 的低阈值点仅为曲线数据）。
- 基线不回退：main 530+1skipped 0 failed。
- qualification 用真权重（pin 一致）、CPU 登记；M2-SFX-PROD-1 的 composite 包装不受影响（primary 检测语义增强）。

## 交付记录（Owner 回填 2026-10-01，delivery_head=29a7f5b5）

- [x] **AC1 tiling 路径**——落点=`detection_manga.py` 单文件，契约零变更（DetectionRequest/Response 与 MERGE_* 输入不变）。**触发**：`height/max(width,1) > 4.0` 严格大于（边界不触发）；选型留痕=DIAG 实测 webtoon 页 h/w 30.7–90.0 vs 普通页 ≤1.41，阈值 4.0 两侧余量 ~20×；不触发页走**零 diff 原 `_detect_text_boxes`**（函数本体逐字节未动）。**参数配置化**：env `NEWMANGA_DETECTOR_TILING_TRIGGER_RATIO/_TILE_SIZE/_OVERLAP/_NMS_IOU`（沿 SFX conf env 先例），默认=DIAG 冻结值 4.0/1024/128/0.5；**选型=env 而非 settings**（settings 通道需动禁改面 `bootstrap/core_assembly.py`，env 读取内聚 provider 文件）；非法值 fail-fast（ValueError 含 env 名，解析/范围/overlap≥生效 tile 联合校验）。**实现**：`_tiling_tiles`（2D 重叠网格，DIAG 精确步进：K01→70 块、尾块 309px 逐值一致）→ `_pad_tile`（灰 114 方形 pad=DIAG）→ `_tile_inference`（**同 engine 逐块推理不重建**，target=padded 尺寸=DIAG）→ 共享纯过滤 `_text_boxes_from_results`（**块内 clip 到块界**；DIAG 以中心点丢 pad 带实现、其 pad 带零检出，两法数值等价）→ `+原点` 回映 → `_greedy_nms`（conf 序贪心、IoU 严格大于删/等于保留=DIAG）。detect options 新增 `tiling/tiling_tiles/text_boxes_pre_merge` provenance。
- [x] **AC2 测试（先红后绿）**——红态实证：实现前 73 collected 中 **44 failed / 29 passed**（缺 tiling 符号的机械失败）；绿态 **73 passed**。新增 32 函数（collected 45）：触发判定（K01/K02/K04 触发、BJ02 不触发、h/w==ratio 边界、width=0 防御）；env fail-fast 矩阵 14 条；块几何（K01 70 块 DIAG 逐值/单块页/整除无空尾/2D 网格/全覆盖）；回映；跨块 NMS（重叠带重复删低 conf、IoU=0.5 保留、keeper 恒高 conf、disjoint 不删）；块内 clip；bubble 跨块累计；NaN typed（R9 语义贯通）；普通页必走原路径+tiled 禁入（双向哨兵）；长条页缺权重仍 `PROVIDER_NOT_CONFIGURED`（fail-closed 顺序不变）。**既有测试零修改**：三套件 `tests/providers tests/core tests/m2_acceptance` = **575 passed + 1 skipped 0 failed**（基线 530+1sk+45；解释器 `T1.1.1-impl-py312`）。
- [x] **AC3 qualification**——`experiments/M2-DETECT-WEBTOON-TILING/qualify_tiling.py`，真权重（三文件 sha256 pin 全匹配）CPU 单环境，报告=`verification/M2-DETECT-WEBTOON-TILING/qualification-{results.json,report.md}`。**Gate PASS：K01=180 region（合并前 193 框=DIAG 逐值复现）/20 104ms≤25s；K02=93（97）/5 968ms≤10s；K04=113（117）/9 271ms≤15s；K05=62（64）/14 277ms；K08=60（61）/16 252ms**（K05/K08 无预算项，数字如实登记）。**阈值曲线 0.5 vs 0.4**：K01 193→214 框（region 180→191）、K02 97→103、K04 117→120、K05 64→65、K08 61→65——贴阈敏感=DIAG 预警形态、无爆炸、conf 生产 0.5 不变。**690×690 原生尺度对照**（K01）：111 块（≈1.6×）→ 198 框/177 region（+2.6%，同量级）——分辨率假设成立。**K19**：0 candidates、tiling=off（正确行为；F4 INVALID_INPUT 口径不修只登记）。**BJ02 对照**：region=5、tiling=off，与 DIAG 探针逐值一致=普通页零变化。
- [x] **AC4 文档**——docstring（模块级 tiling 语义段+各新函数：触发/参数/回映/NMS/pad 惯例出处/普通页零变化承诺）；handoff=`doc/handoffs/M2-DETECT-WEBTOON-TILING-29a7f5b5.md`（含 §DSH review 指引六条：零变化主张/NMS 语义/clip 等价论证/env fail-fast/红绿证据/qualification 复核）；**发布形态登记：无新依赖（标准库 os+既有 numpy/torch 调用）→ 闭包/GATE 不涉及，确认**。
- 纪律自检：`git diff --check` EXIT=0；禁改面（`detection_sfx.py`/`detection_doctr.py`/`src/ports/**`/`src/bootstrap/**`/`doc/contracts/**`/`packaging/**`/`apps/**`/`experiments/M2-TA3-*|DETECT-WEBTOON-DIAG/**`/`doc/STATUS.md`）零 diff（porcelain 仅 4 个允许面路径）。相邻发现只登记不修：①ogkalu 粒度细于 docTR（K01 180 vs 15 region，合并率 1.6–7.2%，非缺陷）；②F4 无字页 INVALID_INPUT 口径；③长条页 CPU 延迟（最坏 ≈20s，GPU/并发/降块=发布形态输入）。
