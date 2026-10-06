# M2-SFX-TILE-WIDTH-CALIB-1 逐宽校准报告（width-calib-report）

- Task: [M2-SFX-TILE-WIDTH-CALIB-1](../../doc/tasks/M2-SFX-TILE-WIDTH-CALIB-1.md)（branch `agent/zcode/M2-SFX-TILE-WIDTH-CALIB-1`，base `d298ecd0`）
- 生成: 2026-10-06，Owner=ZCode
- 权重: v2b 生产 pin `944e8114…` 原样零重指（sha 先验断言；本 Task 无权重变更）
- 环境: venv `T1.1.1-impl-py312`（Python 3.12.3 + onnxruntime-directml 1.24.4，DmlExecutionProvider，RTX 5070 Ti；GPU 档，禁 CPU tile 口径）
- 素材盘点: [INPUTS.md](../../experiments/M2-SFX-TILE-WIDTH-CALIB-1/INPUTS.md)——真实素材零「宽≠600/690 长条页」，评测集按 Task 合同两条授权路径补样
- 评测脚本: `experiments/M2-SFX-TILE-WIDTH-CALIB-1/prepare_pages.py` + `eval_tile_width.py`；raw 明细 `raw/width-eval.json`、运行 log `raw/eval-run.log`

## 1. 评测口径

- **生产代码路径**：`SfxDetectionProvider.detect`（本 worktree `src/infrastructure/providers/detection_sfx.py`），tile 面=默认 env（`NEWMANGA_SFX_TILE` 缺省=冻结 on），letterbox 面=`NEWMANGA_SFX_TILE=off`；每次 detect 后断言 `sfx_route` 符合预期（域内 tile 面=tile、off 面=letterbox、域外档=letterbox）。
- **匹配**：`eval_gate_t3.py` `match_gt` 逐字（conf 降序贪心、IoU≥0.5、GT/pred 一一配对）；主口径 conf 0.5（生产门）+ 参考 conf 0.2（KO-TILE-CALIB 双口径先例）。
- **锚点自检（硬断言）**：原生 W690/W600 档 tile conf 0.5 必须逐页复现 T5 parity raw（`pre-k08 14/27`、`pre-k09 17/24`、`pre-k02 2/3`）——本轮全部 MATCH，harness 测的就是生产序列。
- **评测集**：10 宽度档 14 页（INPUTS.md §2）：原生锚点（真实 GT 51+3 框）、重采样变体 640/480/320/800/1024（重采样派生 GT，相似变换精确+插值损失声明）、程序合成 384/560/680（合成精确 GT 46-49 框/页，块/页宽比与 KO GT 中位对齐）。

## 2. 逐宽表现表（AC2/AC3 核心证据）

conf 0.5 主口径（tile 耗时=该档全部页 wall 计测和；ms/tile=provider 毫秒/tile 数）：

| 宽度档 | GT 类型 | GT 框 | tile matched (recall) | tile n_pred (precision) | letterbox matched | tile 耗时 | letterbox 耗时 | ms/tile |
|---|---|---|---|---|---|---|---|---|
| W690（原生锚点） | 真实 | 51 | **31 (0.608)** | 73 (0.425) | 0/51 | 2.86s/2页 | 0.36s | 16.3-17.7 |
| W600（原生锚点） | 真实 | 3 | **2 (0.667)** | 5 (0.400) | 0/3 | 0.37s | 0.06s | 17.4 |
| W640 | 重采样派生 | 51 | **33 (0.647)** | 79 (0.418) | 0/51 | 2.71s/2页 | 0.36s | 16.9-17.5 |
| W480 | 重采样派生 | 51 | **35 (0.686)** | 75 (0.467) | 0/51 | 2.02s/2页 | 0.19s | 16.8-17.0 |
| W320 | 重采样派生 | 51 | **35 (0.686)** | 59 (0.593) | 0/51 | 1.31s/2页 | 0.11s | 16.4-16.6 |
| SYNTH-384 | 合成精确 | 49 | 12 (0.245) | 13 (0.923) | 0/49 | 0.77s | 0.07s | 16.8 |
| SYNTH-560 | 合成精确 | 46 | 12 (0.261) | 13 (0.923) | 0/46 | 0.85s | 0.10s | 18.4 |
| SYNTH-680 | 合成精确 | 46 | 18 (0.391) | 22 (0.818) | 0/46 | 0.83s | 0.10s | 17.9 |
| W800（域外，宽>690） | 重采样派生 | 27 | 不路由（谓词 w>690→letterbox，运行断言过） | — | 0/27 | — | 0.18s | — |
| W1024（域外，宽>690） | 重采样派生 | 27 | 不路由（同上） | — | 0/27 | — | 0.31s | — |

conf 0.2 参考口径（tile 面 recall：W690 0.765 / W640 0.706 / W480 0.725 / W320 0.706 / SYNTH 0.327-0.522；letterbox 面全部 0 候选）。**口径依赖如实登记（DSH r1 P2-2）**：「原生 vs 重采样」排序随 conf 口径翻转——conf 0.5 主口径下重采样档 ≥ 原生 690 档（0.647-0.686 vs 0.608），conf 0.2 下原生档反高（0.765 vs 0.706-0.725）；两口径一致的是 ①640/480/320 三档之间无单调劣化趋势、②tile ≫ letterbox 结构性优势（letterbox 全零），**而非「重采样 ≥ 原生」**；§3.1 相关句仅在 conf 0.5 主口径下成立。

## 3. 观察（directional）

1. **域内各宽度档 tile 召回与已校准的 690 档同量级**：重采样 640/480/320 = 0.647/0.686/0.686，不低于原生 690 的 0.608；precision 同量级（0.42-0.59 vs 0.425）。窄页 tile 的 letterbox 放大倍率更高（1024/320=3.2× vs 1024/690=1.48×），实测未随宽度变窄出现 recall 断崖。
2. **letterbox 面全域 0 候选**（10 档 × conf 0.5/0.2 全零，含原生锚点）——T2-V2 发现的「长条页整页 letterbox SFX 亚像素化」结构性事实在所有宽度档逐宽复现；tile 路由的存在价值在全部已测宽度保持。
3. **合成档绝对 recall 低（0.245-0.391）但 precision 高（0.818-0.923）**——INPUTS.md §3 已声明的字形域偏移（楷体化印刷拟声词 vs 真实手写/艺术字 KO SFX）预期内；其档内宽度对比（384/560 均 12 matched、680 档 18）统计功效低，不据此做宽度方向结论。合成档回答的问题是机械面：非 KO 来源、宽≤690 的长条页默认路由 tile（§3④ 跨域激活面）在 GPU 档实测 ms/tile 16.3-18.4ms（页级 ~0.8s/页，随 tile 数/页高线性）、tile:letterbox 耗时比 ~6.5-12×。
4. **域外档（W800/W1024）letterbox 0/27**——宽>690 长条页维持 pre-T5 letterbox 行为（结构性零检出），是既有登记事实的逐宽复现，非新劣化；路由谓词两侧行为与冻结口径语义一致。
5. **耗时**：tile ms/tile 全档稳定在 16.3-18.4ms（DML），页级耗时随 tile 数（页高）线性；GPU 档 tile:letterbox ≈ 6.5-12×（逐档：W600 6.5×/W640 7.5×/W690 8.0×/W480 10.7×/W320 11.6×/SYNTH 8.0-10.9×；T5 deploy-report 的 ≈20× 为 CPU 档口径，两者口径不同如实并记）。

## 4. 运行过程如实登记

- 运行期脚本 bug 两处，均在证据写盘前修复并完整重跑：①锚点自检条件误把重采样页（`source` 同名 `pre-kXX`）当原生锚点断言（首次运行止步于 W640 前，无测量写盘）；②域外档打印行引用不存在的 tile face（第二次运行域内 11 页已测完但 JSON 未写盘）。最终一轮 14 页完整跑完写盘。
- 跨轮一致性（DSH r1 P3-7 后收紧）：修复中断两轮未写盘，「域内逐行一致」仅为运行控制台观察、未入库，**不作为证据主张**；仓内证据=最终轮 14 页完整 `raw/eval-run.log` + `raw/width-eval.json`。
- 三轮运行均复现的常量事实：原生锚点= T5 parity 逐页数字；letterbox 面全域 0。

## 5. AC3 三选一结论（硬门）

## **(a) 维持现状** —— 冻结阈值参数（`SFX_TILE_ROUTE_MAX_PAGE_W=690`、`SFX_TILE_ROUTE_MIN_ASPECT=8.0`、`SFX_TILE_HEIGHT=1024`、`SFX_TILE_OVERLAP=128`、`SFX_TILE_NMS_IOU=0.5`）在宽 320-680 的未校准宽度上，**真实内容重采样档（640/480/320，conf 0.5 主口径）与已校准的 600/690 档同量级**（合成档 recall 绝对值低 0.245-0.391，系字形域偏移声明内，单列机械面/耗时面证据），无任何宽度档出现支持阈值修订的劣化证据。

一句证据：域内全部重采样/合成宽度档 tile conf 0.5 召回 0.245-0.686（真实内容重采样档 0.647-0.686，不低于原生 690 档 0.608）且 letterbox 面 10 档全零候选、原生锚点逐页复现 T5 parity——没有一档出现「tile 优势消失」或「recall 断崖」的信号，缺口以本 Task 证据关闭，**零 src 变更合法 done**。

约束与限制（directional 声明，如实；DSH r1 后扩充）：本结论统计功效低（每档 1-2 页、W600 仅 3 框、合成档字形域偏移、重采样档混合宽度与有效分辨率两因素），仅支持「未校准宽度上无可观察劣化、无需修订」的 directional 判定，不构成对更极端宽度（<320 或接近 690 的其他值）或非 webtoon 域长条页的保证；后续若出现真实「宽≠600/690」KO 页 GT（如新 case 入库），按本 Task 脚本增量补测即可。另登记（DSH r1 P3 采纳）：

- **排序翻转口径依赖（P2-2）**：§3.1/§5 的「重采样 ≥ 原生」仅 conf 0.5 主口径成立，conf 0.2 下翻转（§2 脚注）。
- **上限侧未测（P3-2）**：宽 700-1024 的 tile 面未跑（env `NEWMANGA_SFX_TILE_ROUTE_MAX_PAGE_W` 存在但未动用）——本证据**不能裁决「提高宽上限」类提案**，此类提案须另开 Task 用该 env 补测。
- **宽度阶梯非独立（P3-3）**：重采样 640/480/320/800/1024 复用同 2 张源页（pre-k08/k09），「逐宽」实为「逐缩放」（pseudo-replication，INPUTS §3.5）。
- **锚点硬断言覆盖面（P3-4）**：断言 matched/n_gt 两键；n_pred（23/50/5）与逐 pair 字段经 DSH r1 对照 T5 parity-v2b.json 确认逐字段一致，未纳入硬断言。
- **match_gt 返回字段（P3-5）**：匹配判定与蓝本逐字；返回值省略蓝本的 `gt_matched_flags`（本 Task 未消费）。
- **EP 键未落 raw（P3-6）**：JSON 未记录 device/sfx_ep 三键，GPU 档判定靠 ms/tile 16.3-18.4ms vs T5 CPU 档 ~160ms/tile 旁证；后续脚本宜落键自证。

## 6. 证据文件

| 文件 | 内容 |
|---|---|
| `raw/width-eval.json` | 逐档逐页逐口径明细（matched/recall/precision/pairs/tile_count/elapsed_ms/ms_per_tile/sfx_route/锚点标记） |
| `raw/eval-run.log` | 最终轮完整运行 log（warm-up/逐页行/汇总表） |
| `experiments/M2-SFX-TILE-WIDTH-CALIB-1/INPUTS.md` | 素材盘点+选样+GT 类型+自锚风险声明 |
| `experiments/M2-SFX-TILE-WIDTH-CALIB-1/prepare_pages.py` | 页图生成（重采样+合成，外部树 `G:/CODEX/New Manga.task-envs/M2-SFX-TILE-WIDTH-CALIB-1/`，不入 Git） |
| `experiments/M2-SFX-TILE-WIDTH-CALIB-1/eval_tile_width.py` | 评测脚本（生产路径/蓝本口径/sha 断言/锚点自检） |

## 7. DSH r1 处置登记（2026-10-06 集成返修，docs-only）

r1 终判 approved_with_conditions（0×P0/P1、2×P2、10×P3、7×P4）；报告 `doc/reviews/M2-SFX-TILE-WIDTH-CALIB-1-c01ef086-dsh-r1.md`（集成合并时导入 main）。处置：**P2-1**（base_commit 统一 d298ecd0，merge-base 实证）/ **P2-2**（conf 口径排序翻转登记，§2 脚注+§5）闭合；P3-1/3-7/3-8/3-9 文档数字与措辞修正；P3-2 脚本 docstring 对齐实际行为+§5 上限侧未测登记；P3-3 INPUTS §3.5+§5 限制登记；P3-4/P3-5/P3-6 限制注记；P3-10 脚本 env 恢复补 finally（**控制流对齐合同字面，无数字路径变化，raw 证据不重跑**——成功路径行为逐字节等价，amend 前脚本版本在 git 历史 c9887f81/6b90b80b 可溯）；P4-3/P4-7 INPUTS 补登；P4-1（域外档汇总零值伪面）/P4-2（prepare_pages 未断言 pre-k09=690）/P4-4（脚本内嵌 PROD_PIN_SHA 常量）/P4-5（generated_at_utc=构造时刻）/P4-6（except 仅 AssertionError）**接受现状注记**，评测数字零变化。
