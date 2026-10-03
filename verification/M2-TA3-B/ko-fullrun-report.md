# M2-TA3-B3-KO-FULLRUN 全量报告（ko 8 case 全链）

- Task：[M2-TA3-B3-KO-FULLRUN](../../doc/tasks/M2-TA3-B3-KO-FULLRUN.md) · 分支 `agent/zcode/M2-TA3-B3-KO-FULLRUN` · worktree HEAD 见 Task 回填 · 日期 2026-10-02/03
- 口径权威：[quality-thresholds.md](quality-thresholds.md)（双轨确定性：remote 链=相似度 Gate）· 前序对照：[ko-rerun-report.md](ko-rerun-report.md)、[quality-report.md](phase2/quality-report.md 相对 phase2 前缀见 §8)
- 判定权威：**用户本人**。本文全部数字为**方向性证据（directional）**，不外推生产结论。
- 翻译 endpoint：DeepSeek remote（`deepseek-chat`，目标语言 zh）；key 仅经 `TA3B_TRANSLATE_API_KEY` 注入（driver 从 key 文件读入进程 env），全链路零明文入库（`dump_json` scrub 先例沿用；本文无 key 内容）。
- 证据根：`verification/M2-TA3-B/phase2/ko-fullrun/`（summaries / budget-ledger.json / determinism/）；像素与日志在仓库外 `G:/CODEX/New Manga.task-envs/M2-TA3-B/ko-fullrun-{pixels,logs}/`。

## 0. 执行摘要

**用户裁决（2026-10-02 §7 七项）中的项 1（全量）与项 2（K02 干净重跑）已全量执行完毕**：9 个 runner pass（8 case 主 pass + K02 rerun + similarity）全部落盘，**8/8 case 全链 export OK**——首跑时这 8 页全部为 0 region 或未到达（F1/F2 缺口），本轮为该批 ko webtoon 页**首次真实全链数据**。累计计量 **950,954 est tokens = 上界 2,200,000 的 43.2%**（预算模型上界 vs 实测见 §8），未触预算熔断。

**F1/F2 关闭确认（AC2）**：
- **F1（webtoon 检测 0 候选）关闭**：detect 5/5 与 TILING qualification 先例逐 case 同值（K01=180/K02=93/K04=113/K05=62/K08=60，§3 表）+ 全链 8/8 组合证据。
- **F2（大图导入）关闭**：K07/K09/K10 页级全链实测（362MB/277MB/278MB rgb32 import OK → detect → export OK），三者为此前从未被 detect 测过的页。

**相似度 Gate（remote 轨）**：K02 干净重跑 93 对全非空，**median=1.0（达标）但 min=0.0 → FAIL**；42/93 对 variant，最差对为语义等价合法重译（「헉뜰아」→「呃啊」/「吓我一跳」）——与 KO-RERUN K11 的 0.4615 同型（词面口径对短文本语义等价重译的保守误报），按用户裁决 §7.6-③ 口径登记 known-limitation、Gate 维持 FAIL 记录按 directional 接受（§5）。

**执行环境事件（必须先读，§1）**：本 run 跨越两次已登记的执行事故——①**invalid-env 无效轮**（唤醒续接进程丢失 OCR venv `PYTHONPATH`，6 case 产出 OCR 全 `PROVIDER_DEPENDENCY_MISSING` 的静默无效 summary，已归档并清除 ledger 污染条目，driver 硬化后重跑）；②**双 driver 并行**（原初 driver 未死 + 重启产生同秒双副本，进程审计后收敛为原初 driver A 独跑）。最终有效数据全部来自**原初 driver A**（好环境实证：K04/K05/K08 轮 + 其后续队列）。两事故的完整证据链见 §1 与 worktree commit `cd76cac0`/`7aee808d`。

## 1. 执行环境事件（时间线与证据）

### 1.1 invalid-env 无效轮（2026-10-02 UTC 04:17–04:29）

- **现象**：6 个 case（K07/K09/K10/K01/K02/K02.rerun）summary 全部落盘但 OCR 非空率 0/958、翻译 0 请求、export FAIL；单 case wall 仅 24–265s（有效轮 ~16s/region OCR vs 无效轮 ~1s/region 空跑）。
- **第一现场**：归档副本的 `run1.steps` 首条 = `ocr / failed / PROVIDER_DEPENDENCY_MISSING / "module 'paddleocr' is not installed (provider=paddleocr-korean)"`——runner 主 venv（T1.1.1-impl-py312）不含 paddleocr，paddleocr 3.7.0 + paddle 3.3.1 在专用 OCR venv（`M2-TA3-B-ocr`），原初轮靠**启动 shell 的 `PYTHONPATH`** 注入。
- **根因**：熔断唤醒续接的新 shell 无 `PYTHONPATH` → `_lazy_import("paddleocr")` typed 失败 → 空 OCR 文本被链路继续消费；driver 把 `exit=1` 视为「pipeline failures, EXPECTED, must NOT abort」（driver 文档原话），一错到底跑完 6 case。
- **处置**：6 份无效 summary + 坏轮 `qual-report.json`/`rerun-compare.json` 移入 `summaries/invalid-env-2026-10-02-ocr-dep-missing/`（`run1.steps` 错误码在案）；budget-ledger 六条全零条目删除（`invalidated_entries_note` 登记）。
- **硬化（worktree `cd76cac0`）**：driver 增 `runner_env()`（OCR site-packages 注入写成代码内不变量，不再依赖启动 shell）+ `ocr_stack_ok()` 启动自检（fail-fast exit 2，烧 case 前拦截）。
- **有效轮的判别基线**（供 Reviewer 复核）：引擎初始化日志（PaddleOCR `Creating model: PP-OCRv5_server_det` + `korean_PP-OCRv5_mobile_rec`）+ OCR 速度（~16s/region）+ `run1.steps` 无 OCR 依赖失败。本轮全部有效 summary 满足三条。

### 1.2 双 driver 并行（2026-10-02 UTC 03:42 起伏，05:56–06:18 处置）

- 进程审计发现：原初 driver A（UTC 00:10 启动，好环境）**从未死**——阻塞在 K07 runner 上（OCR venv python，真实推理）；§1.1 的无效轮是**第三个**短命唤醒续接者所写；编排会话 05:56 的硬化重启产生**同秒两个 driver 副本**，与 driver A 的队列必然同 case 撞车（summary 写冲突 + DeepSeek 双倍调用）。
- **处置**：终止副本两棵进程树，driver A 独跑至完成；副本写下的假 K07 ledger 条目删除（worktree `7aee808d`）。driver A 队列 K07→K09→K10→K01→K02 main→K02 rerun→similarity 于 2026-10-03 07:34:35Z 全部完成（`driver-result.json` status=DONE，坏轮同名残留已改名 `driver-result.invalid-env-leg.json` 归档）。

### 1.3 endpoint 可用性

本轮 probe 每阶段首试即 OK，无 KO-RERUN 式 115 分钟故障窗；K10 单 region 翻译 typed 失败（§4.2）为孤例，fail-closed 保空正确。

## 2. 全量矩阵与逐 case 对照（AC1/AC2）

计量口径：`--meter-translation` 透传 proxy（estimate_tokens，CJK-aware；production retry 不落计量——ko-rerun-report §1.3 r1 R6 口径沿用）。

| case | 页尺寸（px 高） | detect | OCR 非空 | 翻译非空 | export | 请求 | est tokens | run1/run2 |
|---|---|---|---|---|---|---|---|---|
| K01 | 62,133 | 180 | 179/180 | 179 | OK | 304 | 183,622 | **failed**/completed_with_failures |
| K02 | 18,401 | 93 | 93/93 | 93 | OK | 186 | 112,878 | completed/completed |
| K02.rerun | 18,401 | 93 | 93/93 | 93 | OK | 186 | 112,848 | completed/completed |
| K04 | 28,156 | 113 | 109/113 | 109 | OK | 111 | 67,384 | completed_with_failures ×2 |
| K05 | 46,000 | 62 | 62/62 | 62 | OK | 124 | 77,005 | completed/completed |
| K07 | 131,289 | 247 | 226/247 | 226 | OK | 235 | 140,588 | completed_with_failures ×2 |
| K08 | 51,971 | 60 | 56/60 | 56 | OK | 61 | 36,658 | completed_with_failures ×2 |
| K09 | 100,480 | 119 | 115/119 | 115 | OK | 206 | 125,692 | completed_with_failures ×2 |
| K10 | 100,674 | 147 | 141/147 | 140 | OK | 155 | 94,279 | completed_with_failures ×2 |

合计：detect 1,248 region；OCR 非空 1,070/1,112（96.2%）；翻译非空 1,069；export 9/9 OK；请求 1,568；**950,954 est tokens**。

### 逐 case 对照（vs 首跑 / KO-RERUN / TILING 先例）

| case | 首跑（TA3-B2） | KO-RERUN（停跑轮） | TILING GATE 先例 | 本轮 | 结论 |
|---|---|---|---|---|---|
| K01 | 0 region（F1） | 未跑（预算停等） | 180 | **180，全链 export OK** | 同值复核 ✓ |
| K02 | 0 region（F1） | 93 region，Run2 46 region API 故障 typed | 93 | **93（main+rerun 双 pass 全绿）** | 同值复核 ✓；KO-RERUN 的 environment 失败形态不再存在 |
| K04 | 0 region（F1） | 未跑 | 113 | **113，全链 export OK** | 同值复核 ✓ |
| K05 | 0 region（F1） | 未跑 | 62 | **62，全链 export OK** | 同值复核 ✓ |
| K08 | 0 region（F1） | 未跑 | 60 | **60，全链 export OK** | 同值复核 ✓ |
| K07 | detect 未到达（F2） | 未跑 | **无先例** | **247，全链 export OK** | 首次检测实测 |
| K09 | detect 未到达（F2） | 未跑 | **无先例** | **119，全链 export OK** | 首次检测实测 |
| K10 | detect 未到达（F2） | 未跑 | **无先例** | **147，全链 export OK** | 首次检测实测 |
| K11 | 13 region（唯一普通页） | KO-RERUN 已跑（13/11 翻译/相似度 FAIL 0.4615） | — | **不在名单，沿用 KO-RERUN 结果**（任务书 AC1 明文） | 不变 |
| K19 | F4 口径错位 | F4 维持登记 | — | 不在名单，F4 维持 | 不变 |

- detect 5/5 与 TILING 先例**逐 case 同值**（生产同权重同 conf 0.5）：跨 run 检测确定性再证实。
- 首跑归因表更新：F1 系四页（K01/K04/K05/K08）+K02 由「data×检测域缺口」变为**页级全链实测关闭**；F2 系三页（K07/K09/K10）由「import 拒绝（Qt 256MB 上限推断）」变为**页级全链实测关闭**。

### K01 run1=FAILED 登记（归因待查，不阻塞）

K01 run1 的 step 表全绿（125 translate/125 mask_refine/125 inpaint/125 ocr/125 segment/125 color/125 term_extract/124 render 全 completed，detect 1）但 pipeline 终态 FAILED（`defect:run1-PipelineRunStatus.FAILED`）；run2 completed_with_failures、export OK。**与已知 F3 同型（空 OCR region term_extract INVALID_INPUT）不同**——K01 无失败 step 却 run=FAILED，归因未定（planner 聚合层嫌疑）；case 级产物（export/crops/译文）完整，登记为待查缺陷，不影响 F1/F2 关闭与 Gate 结构判定。

## 3. F1/F2 关闭确认（AC2）

- **F1 关闭 = detect 5/5 + 全链 8/8 组合证据**（用户裁决「3 按推荐」采 KO-RERUN §2 组合口径）：detect 层五页与 TILING qualification 逐 case 同值（独立 Task GATE PASS 先例）×本轮五页全链 export OK；K02 另有干净双 pass。
- **F2 关闭 = K07/K09/K10 页级全链实测**（用户裁决「1 全量」的自然结果）：三页 import OK（362/277/278MB，ALLOC 2047MiB 口径下）→ detect 247/119/147 → OCR/翻译/渲染 → export OK。KO-RERUN §7.4 的「页级必要性」裁决点就此闭合。

## 4. 评测更新（AC3）

### 4.1 ko G1 CER：NOT_AUTOMATED（如实）

K01–K10 在 `phase2/ocr/` **无 SVG GT 物**（现仅 J46/J47/K11/K19 四件）；任务书 AC3 预留口径生效——无自动对齐可能的页**如实 NOT_AUTOMATED**，不构造伪 GT。ko G1 CER 权威值维持 KO-RERUN 的 K11 对齐结果（n=6、median=0.0556、gate ≤0.20 PASS，6 行与首跑逐位一致）；K01–K10 的质量证据由相似度轨（§5）+OCR/翻译覆盖度（§2）承载。

### 4.2 OCR/翻译覆盖度增量（directional）

- OCR 非空率 96.2%（1,070/1,112）；42 个空 OCR region 全部 typed 走 F3 同型路径（空 OCR → term_extract INVALID_INPUT 计入 run 终态——语义定稿链预期行为，ko-rerun-report §2 注先例）。
- 翻译非空 1,069/1,070；唯一例外 K10 一个 region（`집이 엄청\n고급스럽네`）translate typed 失败保空（fail-closed 正确）。
- SFX：生产默认 `sfx.policy` 缺省 → SKIP 口径（与首跑/KO-RERUN 同），本轮无 SFX 增量（SFX 端到端由 M2-SFX-E2E-MATERIAL 承载并已闭环）。

## 5. 确定性复跑（K02 干净版相似度 Gate，remote 轨）

- 判轨：两 pass 绑定均为 remote DeepSeek（`determinism_track` 字段双向校验一致，`--determinism-track remote` 显式记录）；export sha 口径（mock 轨）附报：两次 sha 不同（`rerun-compare.json` match=false，remote 轨下预期）。
- 结果（[K02-similarity.json](phase2/ko-fullrun/determinism/K02-similarity.json)）：93 对全非空（n≥1 覆盖前置满足）；**median=1.0（≥0.95 达标）；min=0.0（<0.70）→ Gate=FAIL**。51/93 逐位一致，42/93 variant，p10=0.5433。
- **形态归因**：最差对全部为语义等价的合法重译——「헉뜰아」（感叹词）→「呃啊」/「吓我一跳」（normalized 0.0；字符级零重叠但语义等价）、「이작고소동한걸 주는데??」→ 两译法措辞重构（0.2308）等。与 KO-RERUN K11 的 0.4615 同型：**词面（字符 Levenshtein）口径对短文本语义等价重译系统性保守误报**（CALIB 局限 8 预言的形态，本轮获得 n=93 的大样本再证实；42 个 variant 中语义等价重译与轻度措辞浮动混合，逐对登记在 pairs[]）。
- **口径处置（用户裁决 §7.6-③，2026-10-02）**：Gate 维持 FAIL 记录、按 directional 接受；known-limitation 注落 `quality-thresholds.md` §5（本轮追加）；语义度量为候选待校准集方向（本 93 对可入校准集），引入需新 Task。
- 定价参考：K02.rerun 与 K02 的计量近乎同值（112,848 vs 112,878），干净数据根下 run 间成本稳定。

## 6. 运行时特性（新登记，优化候选证据）

**逐 region 全链耗时 ∝ 页高（~1ms/像素行，R²≈0.99）**：run2 s/region 实测 K04=29（28,156px）、K05=48（46,000）、K08=49（51,971）、K10=106（100,674）、K09=110（100,480）、K07=129（131,289）。逐 region fan-out（BACKFILL 语义定稿后）每 region 的渲染合成/画布操作/IO 都作用于整页画布（本组 webtoon 页 277–362MB RGB32），成本 O(页高) 而非 O(region)；叠加 OCR（mkldnn off 正确性代价 ~16s/region）与 DeepSeek 往返。**优化候选**（非本 Task 范围）：region 渲染局部贴图化。另：K09 run1 出现 86s/region 异常窗（同页型 K10 仅 12s/region），API 往返波动单 case 可达小时级，登记为观测。

## 7. 全链 Gate 现状（如实）

- **ko 侧 case 覆盖**：8/8 case export OK（首跑 0/8 可用；KO-RERUN 1/8 残缺）。ko 全链 Gate 按「pipeline_failures=0」严格口径：**K02/K02.rerun/K05 三 pass 全绿**（首例 ko webtoon 全绿样本，KO-RERUN §7.2 预言交付）；K04/K07/K08/K09/K10 的 run 终态含**预期内 typed 登记**（空 OCR region 的 F3 同型 term_extract INVALID_INPUT，覆盖度影响 0–4 region/case）；K01 另有 run1=FAILED 待归因缺陷（§2）。
- **ja 侧**：本 Task 未触碰，PASS 维持。
- **K19 F4**：口径未修，维持（不在名单）。
- **确定性 Gate（remote 轨）**：K02 干净重跑 FAIL（min 腿，合法重译形态，§5）——按裁决口径登记，非产品缺陷。

## 8. 预算与计量（AC5）

- **实测 950,954 est tokens = 用户批准上界 2,200,000 的 43.2%**；预算熔断未触发（`budget-ledger.json` stop=null）。上界口径：7-case 全量外推 ~2.09M + K02 干净重跑 ~113k（ko-rerun-report §7 项 1/2；case 级豁免记录落 `CEILING_BASIS`）。
- 实测成本密度 **853 est token/region**（950,954/1,115 主+rerun region），对上界模型 2×607=1,214/region：**实测为上界的 70%**——上界假设保守方向正确；请求数实测 1,568 ≈ 1.41×region 数（模型 2×，K02 双 pass 186=2×93 精确、K04 111≈0.98×113 下偏）。
- key 零明文：driver 从 key 文件读入 env、`dump_json` scrub 覆盖全部落盘物、本报告与 summaries/ledger 无 key 内容。

## 9. 复现命令

```bash
export TA3B_TRANSLATE_API_KEY="$(cat 'G:/CODEX/New Manga.task-envs/M2-TA3-B/deepseek.key')"
export QT_QPA_PLATFORM=offscreen
PY="G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe"   # driver/runner 主 venv；paddleocr 由 driver runner_env() 注入 OCR venv

# 全量 driver（断点续跑：summary+ledger 双在即 skip；启动即 OCR 栈自检 fail-fast）
"$PY" experiments/M2-TA3-B/ko_fullrun_driver.py

# 相似度（driver 末段自动执行；手动复跑）
"$PY" experiments/M2-TA3-B/ko_rerun_similarity.py --case K02 \
  --summaries-dir verification/M2-TA3-B/phase2/ko-fullrun/summaries \
  --out-dir verification/M2-TA3-B/phase2/ko-fullrun/determinism --determinism-track remote
```

> 长 run 纪律：单 case 最长 9h+（K07，含并行冲突期）；必须 detached 进程 + 落盘轮询。**重启 driver 前必须进程审计**（`Get-CimInstance Win32_Process | Where CommandLine -like '*KO-FULLRUN*'`）——无 log 输出≠进程死亡（§1.2 事故教训）。

## 10. AC 对照

| AC | 判定 | 依据 |
|---|---|---|
| AC1 全量补跑 | **PASS** | 9 pass 全落盘（§2 矩阵）；断点续跑/`--determinism-track remote`/region 无截断（`max_regions: null`）在案；K19/K11 边界按任务书 |
| AC2 对照与关闭确认 | **PASS** | §2 逐 case 三方对照表；§3 F1 detect 5/5+全链 8/8、F2 页级三页实测；Gate 新状态 §7 如实 |
| AC3 评测更新 | **PASS（CER 部分 NOT_AUTOMATED 如实登记）** | §4.1 K01–K10 无 SVG GT→NOT_AUTOMATED（AC3 预留口径）；§5 相似度 K02 干净版 93 对+形态清单追加；SFX/可读性增量按裁决由 SFX-E2E 承载 |
| AC4 known-limitation 落地 | **PASS** | `quality-thresholds.md` §5 追加 K02 93 对形态注；ko-rerun-report §7 逐项裁决记录回填（本批 commit） |
| AC5 纪律 | **PASS** | §8：950,954/2,200,000（43.2%）；逐 case 计量在案；key 零明文；src/tests/契约/packaging/apps/首跑/KO-RERUN 产物零改动（diff 面仅 ko-fullrun 证据+driver 硬化+本文档面，见 Task 回填） |
