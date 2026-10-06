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

conf 0.2 参考口径（tile 面 recall：W690 0.765 / W640 0.706 / W480 0.725 / W320 0.706 / SYNTH 0.327-0.522；letterbox 面全部 0 候选）——与 conf 0.5 主口径方向一致，无新增宽度相关信号。

## 3. 观察（directional）

1. **域内各宽度档 tile 召回与已校准的 690 档同量级**：重采样 640/480/320 = 0.647/0.686/0.686，不低于原生 690 的 0.608；precision 同量级（0.42-0.59 vs 0.425）。窄页 tile 的 letterbox 放大倍率更高（1024/320=3.2× vs 1024/690=1.48×），实测未随宽度变窄出现 recall 断崖。
2. **letterbox 面全域 0 候选**（10 档 × conf 0.5/0.2 全零，含原生锚点）——T2-V2 发现的「长条页整页 letterbox SFX 亚像素化」结构性事实在所有宽度档逐宽复现；tile 路由的存在价值在全部已测宽度保持。
3. **合成档绝对 recall 低（0.245-0.391）但 precision 高（0.818-0.923）**——INPUTS.md §3 已声明的字形域偏移（楷体化印刷拟声词 vs 真实手写/艺术字 KO SFX）预期内；其档内宽度对比（384/560 均 12 matched、680 档 18）统计功效低，不据此做宽度方向结论。合成档回答的问题是机械面：非 KO 来源、宽≤690 的长条页默认路由 tile（§3④ 跨域激活面）在 GPU 档实测 ~0.8s/页、tile:letterbox 耗时比 ~8-12×。
4. **域外档（W800/W1024）letterbox 0/27**——宽>690 长条页维持 pre-T5 letterbox 行为（结构性零检出），是既有登记事实的逐宽复现，非新劣化；路由谓词两侧行为与冻结口径语义一致。
5. **耗时**：tile ms/tile 全档稳定在 16.3-18.4ms（DML），页级耗时随 tile 数（页高）线性；GPU 档 tile:letterbox ≈ 8-12×（T5 deploy-report 的 ≈20× 为 CPU 档口径，两者口径不同如实并记）。

## 4. 运行过程如实登记

- 运行期脚本 bug 两处，均在证据写盘前修复并完整重跑：①锚点自检条件误把重采样页（`source` 同名 `pre-kXX`）当原生锚点断言（首次运行止步于 W640 前，无测量写盘）；②域外档打印行引用不存在的 tile face（第二次运行域内 11 页已测完但 JSON 未写盘）。最终一轮 14 页完整跑完写盘。
- 跨进程稳定性旁证：第 2/3 轮运行域内 11 页逐行 matched/n_pred 完全一致（`raw/eval-run.log` 为最终轮）。
- 三轮运行均复现的常量事实：原生锚点= T5 parity 逐页数字；letterbox 面全域 0。

## 5. AC3 三选一结论（硬门）

## **(a) 维持现状** —— 冻结阈值参数（`SFX_TILE_ROUTE_MAX_PAGE_W=690`、`SFX_TILE_ROUTE_MIN_ASPECT=8.0`、`SFX_TILE_HEIGHT=1024`、`SFX_TILE_OVERLAP=128`、`SFX_TILE_NMS_IOU=0.5`）在宽 320-680 的未校准宽度上表现与已校准的 600/690 档同量级，无任何宽度档出现支持阈值修订的劣化证据。

一句证据：域内全部重采样/合成宽度档 tile conf 0.5 召回 0.245-0.686（真实内容重采样档 0.647-0.686，不低于原生 690 档 0.608）且 letterbox 面 10 档全零候选、原生锚点逐页复现 T5 parity——没有一档出现「tile 优势消失」或「recall 断崖」的信号，缺口以本 Task 证据关闭，**零 src 变更合法 done**。

约束与限制（directional 声明，如实）：本结论统计功效低（每档 1-2 页、W600 仅 3 框、合成档字形域偏移、重采样档混合宽度与有效分辨率两因素），仅支持「未校准宽度上无可观察劣化、无需修订」的 directional 判定，不构成对更极端宽度（<320 或接近 690 的其他值）或非 webtoon 域长条页的保证；后续若出现真实「宽≠600/690」KO 页 GT（如新 case 入库），按本 Task 脚本增量补测即可。

## 6. 证据文件

| 文件 | 内容 |
|---|---|
| `raw/width-eval.json` | 逐档逐页逐口径明细（matched/recall/precision/pairs/tile_count/elapsed_ms/ms_per_tile/sfx_route/锚点标记） |
| `raw/eval-run.log` | 最终轮完整运行 log（warm-up/逐页行/汇总表） |
| `experiments/M2-SFX-TILE-WIDTH-CALIB-1/INPUTS.md` | 素材盘点+选样+GT 类型+自锚风险声明 |
| `experiments/M2-SFX-TILE-WIDTH-CALIB-1/prepare_pages.py` | 页图生成（重采样+合成，外部树 `G:/CODEX/New Manga.task-envs/M2-SFX-TILE-WIDTH-CALIB-1/`，不入 Git） |
| `experiments/M2-SFX-TILE-WIDTH-CALIB-1/eval_tile_width.py` | 评测脚本（生产路径/蓝本口径/sha 断言/锚点自检） |
