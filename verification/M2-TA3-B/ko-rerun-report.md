# M2-TA3-B2-KO-RERUN：ko qualification 重跑报告（用户裁决③）

- Task：[M2-TA3-B2-KO-RERUN](../../doc/tasks/M2-TA3-B2-KO-RERUN.md) · 分支 `agent/zcode/M2-TA3-B2-KO-RERUN` · worktree HEAD `87f61d8b`（含 M2-TASKS-PRIMARY-SFX-GATE 语义定稿）· 日期 2026-10-02
- 口径权威：[quality-thresholds.md](quality-thresholds.md)（双轨确定性：remote 链=相似度 Gate）· 首跑对照：[quality-report.md](quality-report.md)
- 判定权威：**用户本人**。本文全部数字为**方向性证据（directional）**，不外推生产结论。
- 翻译 endpoint：DeepSeek remote（`deepseek-chat`，目标语言 zh）；key 仅经 `TA3B_TRANSLATE_API_KEY` 注入，全链路零明文入库（落盘前 `dump_json` scrub 先例沿用）。
- **执行环境事件（必须先读）**：run 期间遭遇 DeepSeek API 故障窗口（~115 分钟，见 §1.3）；并触发任务纪律的**翻译预算红线**（§1.2）——ko 全量 10 case 中 **7 case 停跑等裁决**，本报告交付=试算（K02）+ 最小对照集（K11/K19）+ 全量预算登记。

---

## 0. 执行摘要

| AC | 结果 |
|---|---|
| AC1 重跑执行 | **部分执行（纪律停跑）**：K02 试算全链完成（93 region、export OK）+ K19（0 region，F4 fail-closed 维持）+ K11 最小对照集（主 pass + sfx 对照 + 确定性复跑）；**K01/K04/K05/K07/K08/K09/K10 共 7 case 停跑**——AC1 试算外推全量 **63 万–209 万 est token > 50 万红线**，按任务纪律停止并登记（[budget-register.json](phase2/ko-rerun/budget-register.json)），等用户裁决范围 |
| AC2 对照登记 | 逐 case 对照表见 §2：**K02 F1 解锁实证**（首跑 0 region → 重跑 93 region 全链 export OK）；K11 行为对照一致（2 个 OCR 空 region typed 失败同型复现）；K19 F4 口径未修、预期 fail-closed 维持；K01/K04/K05/K08（F1 系）与 K07/K09/K10（F2 系）的 unlock 实测待裁决后补 |
| AC3 评测更新 | ko G1 CER 重算 **n=6、median=0.0556、gate(≤0.20)=PASS，6 行 CER 值与首跑逐位一致**（OCR 层跨 run 确定性再证实，含 2 处 OCR 错误模式逐位复现）；SFX 主 pass n=1 translated=0（SKIP，同首跑）；**`sfx.policy=translate` 对照跑：配置语义验证成功（region.sfx_policy skip→translate 生产 settings 键生效），但 K11 唯一 sfx region OCR 空，SFX 翻译端到端仍不可达（素材缺口，非语义缺口）**；对白可读性工作表 ko 侧增量预填 n=15（K02 webtoon 12 + K11 P&C 3，ai_mean 4.31，3 请求） |
| AC4 确定性 | K11 相似度 Gate（remote 轨）：**FAIL——12/13 对逐位一致（median=1.0），1 对语义等价合法重译 min=0.4615 < 0.70 触发 min 腿**；归因=CALIB 局限 8 预言的"词面口径保守误报"形态首次实测（§4）。K02 复跑对照随预算停跑移交裁决。export sha 口径为 mock 轨，附报 |
| AC5 成本与纪律 | 实际消耗 ≈ **347 次成功请求 ≈ 20.4 万 est token**（两次 K02 全链 + K11×3 + 自评/探针；估算口径见 §1.1）——红线由"外推"触发而非实际消耗；key 零明文；src/tests/契约/首跑产物/thresholds/STATUS 零改动 |

**全链 Gate 现状（如实）**：ko 侧全链 Gate（pipeline_failures=0）**仍 FAIL**——构成：7 case 未跑（裁决待定）+ K02 Run2 46 region API 故障 typed 失败（environment）+ K11 2 region F3 同型 typed 失败（data，预期）+ K19 F4（口径，预期）。ja 侧 PASS 维持（本 Task 未触碰 ja，无变化依据）。

---

## 1. 试算与预算（AC1/AC5）

### 1.1 K02 试算实测（计量 proxy：`--meter-translation`，experiments 层透传包装，行为零变更）

生产 client 不暴露 endpoint usage（首跑已登记"token 量无计量证据"）；本 run 在 re-register 时为 provider 加了**透传计量代理**（`run_qualification.py` 内 `_MeteredTranslationProvider`），逐请求记录 target region 数与 `estimate_tokens`（`ports/translation/protocol.py` 项目既有 CJK-aware 估算器）口径的 input/output 估算。**全部为估算，非 endpoint 计量数据。**

| 项 | 实测 |
|---|---|
| K02 尺寸 / region 数 | 600×18401 / **93 region**（与 M2-DETECT-WEBTOON-TILING qualification 实测 93 一致，生产 conf 0.5） |
| Run1（页面级全链） | completed，1848.5s（detect TILING ~6s + 逐 region OCR/翻译/inpaint + 整页 render） |
| Run2（93 region 独立链） | completed_with_failures（46 region 失败，见 §1.3），3742.0s |
| export | OK（sha `b5e27061…`，5,069,825 B） |
| 计量请求数 | **140 次成功请求，且 `n_target_region_calls == requests == 140`——每次请求恰好 1 个 target region（Run1 亦逐 region 发请求，非整页批量）** |
| est tokens | input 77,314 + output 7,603 ≈ **84.9k/case（93 region 完整链估算上限 ≈ 186 请求 ≈ 113k）** |
| 单请求估算 | ≈ **607 est token**（input ≈552：system prompt + 1 region payload；output ≈54） |

### 1.2 全量外推与红线判定（停跑依据）

| 项 | 数字 |
|---|---|
| 已知 region 数 | K01=180、K02=93、K04=113、K05=62、K08=60（M2-DETECT-WEBTOON-TILING 实测，K02 本次同值复核）+ K11=13 + K19=0 |
| K07/K09/K10 | **无先例**（ALLOC 修复前 import 拒绝，从未被 detect 测过）；按已测密度区间估 120–400 region/页 |
| region 总量区间 | ≈ 881–1721 |
| 请求数模型 | ≈ 2 × region 数（Run1 一轮 + Run2 一轮，§1.1 实测结构）× 607 est token/请求 |
| **外推 est token** | **已知五页即 ≈ 63.2 万；含 K07/K09/K10 估计全量 ≈ 107 万–209 万** |

**判定：仅 TILING 已确认的五个 webtoon 页就超过任务纪律的 50 万 est token 红线 → 按 AC5 纪律停跑全量、登记等裁决。** 已执行的只是试算（K02）与最小对照集（K11/K19）。登记文件：[phase2/ko-rerun/budget-register.json](phase2/ko-rerun/budget-register.json)。

待裁决选项（供 §7 汇总）：①预算批准全量；②`--max-regions` 逃生阀明示抽样（R7 要求报告披露 region_target_count/region_runs_executed/抽样规则，Gate 口径随之变为抽样集）；③只跑 F2 系 3 case（K07/K09/K10，兼收 ALLOC 解锁确认）；④维持停跑。

### 1.3 DeepSeek API 故障窗口（environment，typed 如实登记）

- **观测**：K02 Run2 第 ~47 region 起 translate step 连续 `PROVIDER_TIMEOUT`（stage=http）；独立最小请求探针两次复现（180s 读超时 / 90s 无响应），故障窗 ≈ 115 分钟（2026-10-01 ~19:30–21:27 +0800）。
- **行为**：生产 fail-closed 语义全程正确——45 次 `PROVIDER_TIMEOUT` + 1 次 `PROVIDER_INVALID_OUTPUT` 全部 typed 登记进 `qual-K02.json` 的 run2.per_region，无静默降级、无重试风暴（retry 走生产语义）。
- **恢复**：21:27Z driver 探针 OK；K11 最小对照集在恢复窗口内完成（21:33–21:37Z）。
- **对 K02 summary 的影响**：46/93 region 的 Run2 独立链携带 environment 失败；**这些 region 的译文并未丢失**（Run1 已完成的批量译文在 DB final 状态，`n_translated=93/93`），失败只影响"region 级重翻链"的 coverage。**是否在裁决后干净重跑 K02（+186 请求 ≈ 113k est token）移交 §7。**

---

## 2. 逐 case 对照登记（AC2）

| case | 首跑（M2-TA3-B2） | 本 run | 对照结论 |
|---|---|---|---|
| K01 | F1：detect 0 候选 | **未重跑（预算裁决）** | TILING GATE 先例 180 region（`M2-DETECT-WEBTOON-TILING/qualification-results.json`，生产同权重同 conf）；unlock 实测待裁决 |
| **K02** | F1：detect 0 候选 | **93 region，Run1 completed，export OK**（Run2 46 region API 故障 typed） | **F1 解锁实证**：ogkalu+TILING 对 600×18401 webtoon 长条漫产出 93 region（与 TILING qualification 同值），全链推进到 export 成功。首跑归因 F1（data×检测域缺口）就此关闭（该页级） |
| K04 | F1 | 未重跑（预算裁决） | TILING GATE 先例 113 region |
| K05 | F1 | 未重跑（预算裁决） | TILING GATE 先例 62 region |
| K07 | F2：import 拒绝（Qt 256MB 上限推断） | 未重跑（预算裁决） | **ALLOC 解锁无先例数据**（该页从未被 detect 测过）——K07/K09/K10 是 F2 关闭确认的唯一途径，裁决选项③的直接对象 |
| K08 | F1 | 未重跑（预算裁决） | TILING GATE 先例 60 region |
| K09 | F2 | 未重跑（预算裁决） | 同 K07 |
| K10 | F2 | 未重跑（预算裁决） | 同 K07 |
| **K11** | 13 region、11 翻译、2 空 OCR region term_extract typed INVALID_INPUT（F3）、export OK、run1=completed | 13 region、11 翻译、**2 空 OCR region typed INVALID_INPUT 同型复现**、export OK、**run1=completed_with_failures**（见下注） | 行为对照一致；CER 6 行逐位复现（§3.1）；相似度 Gate 见 §4 |
| **K19** | F1+无字页：detect 无候选是正确行为但 step=failed/INVALID_INPUT（F4 口径错位） | 同型复现：detect EMPTY、run2 SKIPPED（data）、run1 COMPLETED_WITH_FAILURES（`INVALID_INPUT: detector returned no candidates`）、wall 8.15s | **F4 口径未修，预期 fail-closed 维持**（本 Task 禁改 src/thresholds，如实再登记） |

> **K11 run1 状态变化注**：首跑 run1=completed（同样的 2 个空 OCR region 未计入 run 状态），本 run run1=completed_with_failures。这不是回归：本 run 跑在 M2-TASKS-PRIMARY-SFX-GATE 集成后的语义定稿 HEAD（87f61d8b）上——Run1 页面链对空 OCR region 的 term_extract 现在 typed 失败并**计入 run 终态**，与 Run2 region 链口径一致化（PRIMARY Task 的 terminal accounting unified 语义）。零 src 改动下的观测，登记为"语义定稿后的预期行为差异"。

---

## 3. 评测更新（AC3）

### 3.1 ko G1 CER 重算（K11 SVG GT 对齐，沿用 measure_cer.py 既有脚本逻辑）

产物：[phase2/ko-rerun/ocr/cer-regions.csv](phase2/ko-rerun/ocr/cer-regions.csv)（106 行）+ `cer-summary.json` + `svg-alignment-trace.json`。

| 指标 | 首跑 | 本 run |
|---|---|---|
| 自动子集 n | 6 | 6 |
| CER median | 0.0556 | **0.0556** |
| P90 / CER=0 占比 | 0.3333 / 50% | 0.3333 / 50% |
| gate(≤0.20) | PASS（directional） | **PASS（directional）** |
| 排除行 | 7（含 1 条 CER=1.0 真失败） | 7（同口径） |

**6/6 行 GT/OCR 文本与 CER 值逐位一致**（仅 region_id uuid 每 run 再生）——PaddleOCR wrapper（`enable_mkldnn=False`）跨 run 确定性在 TILING+新语义链下再次证实，且两处 OCR 字符错误（밑→믿、륵→르）逐位复现，支持首跑 F5"OCR 层已排除"的归因继续有效。首跑 §2.3 的全部限定（下偏统计量、 당근아? 系 3 行同串、n=6 directional）**原样沿用**。

### 3.2 SFX translation 统计

- 主 pass（生产默认 SKIP）：ko 侧 SFX region n=1（K11），`skip_policy/sfx_skip`，translated=0——与首跑口径一致，R13 n<15 只登记分布。
- **`sfx.policy=translate` 对照跑（AC3 加分项，SFX-ENTRY+PRIMARY 语义实战首验）**：
  - 通路：runner 新增 `--sfx-policy`（生产 settings 键 `settings["sfx"]["policy"]`，经 `save_settings_section` 写入 → close → **同 db re-assemble**（core_assembly 装配时读取语义，AC6 探针同序）→ region 创建时携带 policy）。
  - **配置语义验证成功**：sfx region 的 `sfx_policy` 字段实测 `skip`（主 pass）→ `translate`（对照 pass），生产 gate 按 `decide_sfx_translation` 放行进入正常翻译流——SFX-TRANSLATE-ENTRY 的装配语义在真实 run 中首次走通。
  - **端到端仍不可达（素材缺口）**：K11 唯一 sfx region 的 OCR 输出为空（首跑 F3 已登记该 region 无可识别文本），term_extract 先于 translate typed `INVALID_INPUT`——policy 放行后无源文本可翻。**结论：SFX 翻译语义无缺陷，但 ko 侧现有素材不存在"有 OCR 文本的 sfx region"；端到端 SFX 译文验证需要 ja BJ06 类素材（8 个有文本 sfx region，ja 范围外）或新素材，登记为裁决信息。**
  - 产物：[phase2/ko-rerun/summaries-sfx/qual-K11.sfx-translate.json](phase2/ko-rerun/summaries-sfx/qual-K11.sfx-translate.json)（独立 out-dir/pixel-root，不与主 pass 混淆）。

### 3.3 对白可读性工作表 ko 侧增量预填

- 首跑 ko 池受 F1 级联限制仅 11 条（K11）；本 run K02 解锁后 ko webtoon 译文池 93 条。
- 增量预填 **n=15**（K02 分层抽 12 + K11 抽 3），DeepSeek 自评（同 build_worksheets.py 锚点与 prompt，批 5 → 3 请求）：`ai_region_score` 均值 **4.31**（range 2.0–5.0——存在低分样本，自评有区分度，非全 5 锚定）。
- 产物：[phase2/ko-rerun/translate/dialogue-readability-ko-increment.csv](phase2/ko-rerun/translate/dialogue-readability-ko-increment.csv)。**ai_draft=自评预填，用户终审=唯一判定**（C1 模式）；首跑 n=26 工作表不动（禁改）。

---

## 4. render/export 确定性（AC4，remote 轨相似度 Gate）

- **轨道判定**：本 run translate 绑定为 remote DeepSeek → 按 thresholds §5 双轨规则走**相似度 Gate**（reading_order 对齐、normalized 相似度、median≥0.95 且 min≥0.70、空对规则、非空对 n≥1 覆盖前置）。export sha256 字节口径属 mock/deterministic 轨，本 run 仅附报。
- **执行**：K11 主 pass vs `--rerun-check` 复跑（同环境两次独立 run，间隔 ~2 分钟）；对齐校验全过（13 reading_order 集合相等 + 逐对 bbox 逐字段一致 + translate_details 全覆盖）。产物：[phase2/ko-rerun/determinism/K11-similarity.json](phase2/ko-rerun/determinism/K11-similarity.json)（脚本 `experiments/M2-TA3-B/ko_rerun_similarity.py`，方法复刻 CALIB 先例）。

| 项 | 实测 |
|---|---|
| 对数 / 非空对 | 13 / 11 |
| 逐位一致对 | **12/13**（median=1.0） |
| 浮动对 | 1（reading_order=5，speech）：「没想到会做到这种地步」vs「我本以为没必要做到这种地步」，normalized **0.4615** |
| Gate 判定 | **FAIL**（min 0.4615 < 0.70；median 腿 1.0 ≥ 0.95 不触发） |
| export sha | 两次不一致（附报；Run1 层非确定环节，首跑 F5 根因未隔离，本 run 无新证据） |

**归因（如实，不代裁）**：该浮动对是**语义等价的合法重译**（同义改写，非字符噪声、非漏译）——正是 M2-QUAL-DETERM-CALIB 局限 8 预言的"词面口径固有误报方向"（保守 FAIL）：字符级相似度把合法重译判为不稳定，而同义改写恰是 remote 采样漂移的主形态。**这是该误报形态的首次自然实测**（CALIB 的 18 对全是 1 编辑差）。其余 12/13 对逐位一致 + OCR 层 6/6 行逐位一致，说明本次 run 对的**采样稳定性量级与 CALIB 观测一致**。是否需要为"语义等价重译"修订 Gate 口径（语义度量/回译对照），属 thresholds 用户裁决事项，本报告不代裁。

- **K02 相似度复跑对照**：随预算停跑移交（任务书允许"K11 或 K02"，K11 已执行；K02 若在裁决后重跑可顺带补 ko webtoon 家族的 Gate 覆盖——CALIB 已登记该家族盲区）。

---

## 5. 全链 Gate 现状（如实汇总）

| 层 | 现状 |
|---|---|
| ja 侧 | **PASS 维持**（首跑 10/10；本 Task 未触碰 ja，无变化依据） |
| ko detect | F1 解锁实证（K02 93 region）；K01/K04/K05/K08 有 TILING GATE 先例、页级实测待裁决；K19 无字页 0 候选为正确行为，F4 口径（step=failed vs 豁免）未修维持 |
| ko import | F2 系 3 case（K07/K09/K10）本 run 未实测——ALLOC 解锁的页级确认随裁决 |
| ko OCR | K11 G1 自动子集 median 0.0556 PASS（directional，限定沿用）；OCR 层跨 run 确定性再证实 |
| ko translate | K02 93/93 final 状态有译文（Run1 层完整）；Run2 独立重翻链受 API 故障 46 region typed 失败（environment）；SFX policy 语义走通、素材缺口登记 |
| ko render/export | K02/K11×2（主+sfx 对照）+K11.rerun export 全部 OK |
| 全链 Gate（pipeline_failures=0） | **FAIL（如实）**：7 case 未跑 + K02 environment 失败 + K11 F3 同型（data 预期）+ K19 F4（口径预期） |

---

## 6. 缺陷与新发现登记（typed）

| # | 归因 | 发现 | 证据 |
|---|---|---|---|
| N1 | environment | DeepSeek API 故障窗 ≈115 分钟：45×PROVIDER_TIMEOUT + 1×PROVIDER_INVALID_OUTPUT，全部 typed fail-closed、无重试风暴；恢复后链路正常 | `qual-K02.json` run2.per_region；budget-register.json api_outage_window |
| N2 | 纪律（非缺陷） | 全量外推 63 万–209 万 est token > 50 万红线 → 7 case 停跑等裁决 | §1.2 + budget-register.json |
| N3 | 观测（语义定稿预期） | K11 run1 状态 completed → completed_with_failures（PRIMARY terminal accounting 统一后空 OCR region 失败计入 Run1 终态，与 Run2 口径一致化） | §2 注 + 两代 qual-K11.json 对比 |
| N4 | 观测（请求结构） | 生产翻译链每次 HTTP 请求恰 1 个 target region（Run1 亦然）→ 全链请求数 ≈2×region 数；成本模型据此建立 | K02 计量 requests==n_target_region_calls==140 |
| N5 | 观测（Gate 口径） | 相似度 Gate 的"合法重译误报"形态首次自然实测（K11 1/13 对，min 0.4615）；词面口径保守误报方向与 CALIB 局限 8 一致 | §4 + K11-similarity.json |
| N6 | 素材缺口（非语义缺陷） | sfx.policy=translate 生产语义走通，但 ko 唯一 sfx region OCR 空，端到端 SFX 译文不可达；需有文本 sfx region 素材 | §3.2 + summaries-sfx/ |
| N7 | environment（harness） | ZCode 后台 Bash 任务 ~58 分钟被宿主强杀（exit 137）：首次 K02 尝试在 Run2 ~80/93 处被杀、summary 未落盘（scratch 残留 Temp，未清理）；改用独立 detached 进程后完成 | ko-rerun-logs/K02-rerun-attempt*.log |

## 7. 待裁决清单（移交用户/编排）

1. **7 个停跑 case 的范围与预算**（§1.2 选项①–④；K07/K09/K10 兼收 F2/ALLOC 关闭确认）。
2. **是否干净重跑 K02**（+186 请求 ≈113k est token）：当前 K02 summary 的 Run2 带 46 region environment 失败；干净版可同时补 ko webtoon 家族相似度 Gate 覆盖与 AC1 完整 pipeline_failures=0 样本。
3. **相似度 Gate 对"合法重译误报"的口径处理**（维持现阈值保守误报 / 引入语义度量 / 登记 known-limitation）——thresholds 用户裁决事项。
4. K11 `sfx.policy=translate` 端到端素材路线（ja BJ06 或新素材，非 ko 范围）。

## 8. 复现命令

```bash
# env（key 零明文，仅环境变量）
export TA3B_TRANSLATE_API_KEY="$(cat 'G:/CODEX/New Manga.task-envs/M2-TA3-B/deepseek.key')"
export QT_QPA_PLATFORM=offscreen
PY="G:/CODEX/New Manga.task-envs/M2-TA3-B-ocr/Scripts/python.exe"   # 融合 venv 方案 A（env-manifest.txt 先例）

# AC1 试算（K02，含计量；TILING env 未设=默认 4.0/1024/128/0.5）
"$PY" experiments/M2-TA3-B/run_qualification.py --case K02 \
  --out-dir verification/M2-TA3-B/phase2/ko-rerun/summaries \
  --pixel-root "G:/CODEX/New Manga.task-envs/M2-TA3-B/ko-rerun-pixels" --meter-translation

# K11 最小对照集（driver 自动轮询 API 恢复后依序执行）
"$PY" experiments/M2-TA3-B/ko_rerun_k11_driver.py
#   = K11 主 pass → K11 --sfx-policy translate 对照（独立 out-dir/pixel-root）
#     → K11 --rerun-check（相似度第二遍）→ ko_rerun_similarity.py --case K11

# AC3 评测
"$PY" experiments/M2-TA3-B/measure_cer.py \
  --summaries-dir verification/M2-TA3-B/phase2/ko-rerun/summaries \
  --ocr-dir verification/M2-TA3-B/phase2/ko-rerun/ocr
"$PY" experiments/M2-TA3-B/ko_rerun_readability_increment.py   # ko 侧增量预填（3 请求）
```

> 长 run 纪律：本机 ZCode 后台 Bash ~58 分钟强杀（N7），长 case 须用 detached 进程（`Start-Process -WindowStyle Hidden`）+ 落盘轮询；runner 断点续跑语义（summary 存在即 skip）不变。

---

*方向性证据声明：单标注者 + AI 预填锚定未测量；全部数字不得引用为生产结论。判定权威=用户本人。*
