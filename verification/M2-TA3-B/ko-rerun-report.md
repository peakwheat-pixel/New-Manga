# M2-TA3-B2-KO-RERUN：ko qualification 重跑报告（用户裁决③）

- Task：[M2-TA3-B2-KO-RERUN](../../doc/tasks/M2-TA3-B2-KO-RERUN.md) · 分支 `agent/zcode/M2-TA3-B2-KO-RERUN` · worktree HEAD `87f61d8b`（含 M2-TASKS-PRIMARY-SFX-GATE 语义定稿）· 日期 2026-10-02
- 口径权威：[quality-thresholds.md](quality-thresholds.md)（双轨确定性：remote 链=相似度 Gate）· 首跑对照：[quality-report.md](quality-report.md)
- 判定权威：**用户本人**。本文全部数字为**方向性证据（directional）**，不外推生产结论。
- **r1 返修记录（2026-10-02，DSH review=approved 有条件，0×P0/P1 + 3×P2 + R4-R11 精度）**：本报告按 DSH r1 闭合清单完成文档修订——红线口径出处（R1，§1.2）、成本乘数改上界假设+敏感性+K11 Run1 异常登记（R2，§1.2/§6 N4）、判轨控件 `--determinism-track` fail-closed 落地（R3，runner+similarity 脚本+K11-similarity.json 判轨字段，数值逐位不变）、归因链/tiling 限定/计量口径/§7 量化/证据登记/精度修补（R4-R11，逐处就地标注）。**停跑决策与全部 Gate 判定不变**。
- 翻译 endpoint：DeepSeek remote（`deepseek-chat`，目标语言 zh）；key 仅经 `TA3B_TRANSLATE_API_KEY` 注入，全链路零明文入库（落盘前 `dump_json` scrub 先例沿用）。
- **执行环境事件（必须先读）**：run 期间遭遇 DeepSeek API 故障窗口（~115 分钟，见 §1.3）；并触发**翻译预算停跑纪律**（§1.2，红线口径与出处经 r1 R1 更正）——ko 全量 10 case 中 **7 case 停跑等裁决**，本报告交付=试算（K02）+ 最小对照集（K11/K19）+ 全量预算登记。

---

## 0. 执行摘要

| AC | 结果 |
|---|---|
| AC1 重跑执行 | **部分执行（纪律停跑）**：K02 试算全链完成（93 region、export OK）+ K19（0 region，F4 fail-closed 维持）+ K11 最小对照集（主 pass + sfx 对照 + 确定性复跑）；**K01/K04/K05/K07/K08/K09/K10 共 7 case 停跑**——AC1 试算外推全量 **63 万–209 万 est token**，远超现行仓库纪律「预估总 token 数万 token 量级、超预期即停并登记」（phase2-plan.md:192）与编排会话停跑指令（外推 >50 万即停，出处登记见 §1.2 r1 R1），按纪律停止并登记（[budget-register.json](phase2/ko-rerun/budget-register.json)），等用户裁决范围 |
| AC2 对照登记 | 逐 case 对照表见 §2：**K02 F1 解锁实证**（首跑 0 region → 重跑 93 region 全链 export OK）；K11 行为对照一致（2 个 OCR 空 region typed 失败同型复现）；K19 F4 口径未修、预期 fail-closed 维持；K01/K04/K05/K08（F1 系）与 K07/K09/K10（F2 系）的 unlock 实测待裁决后补 |
| AC3 评测更新 | ko G1 CER 重算 **n=6、median=0.0556、gate(≤0.20)=PASS，6 行 CER 值与首跑逐位一致**（OCR 层跨 run 确定性再证实，含 2 处 OCR 错误模式逐位复现）；SFX 主 pass n=1 translated=0（SKIP，同首跑）；**`sfx.policy=translate` 对照跑：配置语义验证成功（region.sfx_policy skip→translate 生产 settings 键生效），但 K11 唯一 sfx region OCR 空，SFX 翻译端到端仍不可达（素材缺口，非语义缺口）**；对白可读性工作表 ko 侧增量预填 n=15（K02 webtoon 12 + K11 P&C 3，ai_mean 4.31，3 请求） |
| AC4 确定性 | K11 相似度 Gate（remote 轨，判轨经 r1 R3 落地的 `--determinism-track` 控件校验）：**FAIL——raw 口径 11/13 对逐位一致 + 1 对仅空白差（normalized 口径 12/13，median=1.0；r1 R9 口径注），1 对语义等价合法重译 min=0.4615 < 0.70 触发 min 腿**；归因=CALIB 局限 8 预言的"词面口径保守误报"形态首次实测（§4，判定依据见该节 r1 R11）。K02 复跑对照随预算停跑移交裁决。export sha 口径为 mock 轨，附报 |
| AC5 成本与纪律 | **估计**消耗 ≈ 347 次成功 `translate()` 调用 ≈ 20.4 万 est token（=计量 proxy 实测 197 次 ≈119k + 未计量的 attempt-1 估算 ~140 次 ~85k + 自评 3 请求 + 探针 ~7 次；attempt-1 被宿主强杀、其成功调用未落计量——口径见 §1.1 与 budget-register，r1 R6/R9 更正）——停跑由"外推"触发而非实际消耗；key 零明文；src/tests/契约/首跑产物/thresholds/STATUS 零改动 |

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
| 计量调用数 | **140 次成功 `translate()` 调用（r1 R6 口径更正：HTTP 请求数 ≥ 该值——production retry 在 provider 之外，失败尝试与重发 input 不落计量，默认 max_attempts=2；attempt_count 未落盘为计量盲点），且 `n_target_region_calls == requests == 140`——每次请求恰好 1 个 target region（K02 的 Run1 逐 region 发请求：93 步 translate 与 93 region 一一对应，非整页批量）** |
| est tokens | input 77,314 + output 7,603 ≈ **84.9k/case（93 region 完整链估算上限 ≈ 186 请求 ≈ 113k，按 §1.2 的 2× 上界假设）** |
| 单请求估算 | ≈ **607 est token**（input ≈552：system prompt + 1 region payload；output ≈54） |

### 1.2 全量外推与红线判定（停跑依据）

| 项 | 数字 |
|---|---|
| 已知 region 数 | K01=180、K02=93、K04=113、K05=62、K08=60（M2-DETECT-WEBTOON-TILING 实测，K02 本次同值复核）+ K11=13 + K19=0 |
| K07/K09/K10 | **无先例**（ALLOC 修复前 import 拒绝，从未被 detect 测过）；按已测密度区间估 120–400 region/页 |
| region 总量区间 | ≈ 881–1721 |
| 请求数模型 | ≈ 2 × region 数（Run1 一轮 + Run2 一轮）× 607 est token/请求——**上界假设（"两轮逐 region 全覆盖"的投影），非实测常数（r1 R2 更正）**：K02 实测 140 调用/93 region=1.51×（Run2 被 46 失败截断）、K11 实测 19/13=1.46×，且 K11 三个 pass 的 Run1 均仅 8 次调用（< region 数，机制未解释——§6 N4 异常登记） |
| **外推 est token** | **已知 region（五 webtoon 页 + K11 = 521 region）按 2× 上界 ≈ 63.2 万；仅五 webtoon 页（508 region）≈ 61.7 万（r1 R9 归属更正）；含 K07/K09/K10 估计全量 ≈ 107 万–209 万**。敏感性（r1 R2）：按 K02 自身实测乘数 140/93≈1.51× → 已知 region ≈ 47.6 万（低于 50 万）——「仅已知页即超线」的表态在乘数上不稳健；含 K07/K09/K10 时 881–1721 region 在 1.46–2× 任一乘数下均超线，**停跑结论不变** |

**判定（r1 R1 口径更正）**：全量外推（含 K07/K09/K10 的 107 万–209 万 est token；区间下界即超出"数万量级"纪律一个数量级以上）→ 按 AC5 纪律停跑全量、登记等裁决。已执行的只是试算（K02）与最小对照集（K11/K19）。登记文件：[phase2/ko-rerun/budget-register.json](phase2/ko-rerun/budget-register.json)。

**红线口径出处（r1 R1 如实登记，集成方/用户裁决项）**：首版报告把「50 万 est token」称为"任务纪律红线"——**任务书原文并无该数值**（AC5 只写"预估请求数/先行一个 case 试算后再全量"）。仓库现行成本纪律是 phase2-plan.md:192「预估总 token **数万 token 量级，超预期即停并登记**」（该行自述 r2 N6 曾把口径写成"数十万以内"被判越界改写并回退）；「50 万」实为**编排会话下达的停跑指令数值，无任务书或用户裁决原文背书**。两种口径下停跑决策均成立（本次外推对两种口径都远超线）；「50 万是否追认为新口径」列为 §7 裁决项——若用户认可需落文（Task 纪律或 phase2-plan 修订，集成方执行），否则以 phase2-plan.md:192 为准。

待裁决选项（供 §7 汇总）：①预算批准全量；②`--max-regions` 逃生阀明示抽样（R7 要求报告披露 region_target_count/region_runs_executed/抽样规则，Gate 口径随之变为抽样集）；③只跑 F2 系 3 case（K07/K09/K10，兼收 ALLOC 解锁确认）；④维持停跑。

### 1.3 DeepSeek API 故障窗口（environment，typed 如实登记）

- **观测**：K02 Run2 第 ~47 region 起 translate step 连续 `PROVIDER_TIMEOUT`（stage=http）；独立最小请求探针两次复现（180s 读超时 / 90s 无响应），故障窗 ≈ 115 分钟（**UTC 19:30Z–21:27Z**；r1 R9 更正：首版误标 +0800——K02 summary 计量窗实测 18:42:13Z–20:15:25Z，探针 20:40Z/21:05Z，恢复 21:27Z）。
- **行为**：生产 fail-closed 语义全程正确——45 次 `PROVIDER_TIMEOUT` + 1 次 `PROVIDER_INVALID_OUTPUT` 全部 typed 登记进 `qual-K02.json` 的 run2.per_region，无静默降级、无重试风暴（retry 走生产语义）。**计量口径注（r1 R6）**：计量 proxy 记录的是成功 `translate()` 调用；production retry（默认 max_attempts=2）在 provider 之外，故障窗 46 region 计 ≈92 次尝试未落计量、token 估算亦未计重发 input——"无重试风暴"的量级证据=46 region typed 失败 ×≈2 次尝试/~115 分钟窗口，方向保守（低估 → 红线更早触发）。
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

> **K11 run1 状态变化注（r1 R4 归因链更正）**：首跑 run1=completed（同样的 2 个空 OCR region 未计入 run 状态），本 run run1=completed_with_failures。这不是回归：本 run 跑在语义定稿 HEAD（87f61d8b）上，归因是 **BACKFILL→PRIMARY 两步定稿链**——region 链账目统一（空 OCR 失败计入 run 终态）先由 M2-TASKS-BACKFILL-MULTIREGION R1 完成（region_ids[1:] fan-out 到 `_plan_region`），PRIMARY 再把 primary region 纳入同一 live-Region 路径并**整体退役页级决策链**（handoff `M2-TASKS-PRIMARY-SFX-GATE-19bf234a.md`）。直接指纹：首跑 run1 步表为页级 9 步（`phase2/summaries/qual-K11.json`），本 run 为 region 级 ~66 步且含 1 条空 OCR region 的失败 term_extract（`ko-rerun/summaries/qual-K11.json`）；run 终态计算路径见 `src/application/tasks/service.py:1054` 与 `src/application/tasks/projection.py:336`。零 src 改动下的观测，登记为"语义定稿后的预期行为差异"。

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

**6/6 行 GT/OCR 文本与 CER 值逐位一致**（仅 region_id uuid 每 run 再生）——PaddleOCR wrapper（`enable_mkldnn=False`）跨 run 确定性再证实，且两处 OCR 字符错误（밑→믿、륵→르）逐位复现，支持首跑 F5"OCR 层已排除"的归因继续有效。**口径限定（r1 R5）**：K11 页面 1200×1660（h/w=1.383）**未触发 TILING 阈值 4.0**，与首跑走同一条 detect/OCR 路径，逐位一致属同路径复现的预期结果；**tiling 路径的 OCR 稳定性本 run 未覆盖**（K02 有 TILING 实测但无 GT），本行不能引用为"TILING 语义下 OCR 稳定"的证据。首跑 §2.3 的全部限定（下偏统计量、 당근아? 系 3 行同串、n=6 directional）**原样沿用**。

### 3.2 SFX translation 统计

- 主 pass（生产默认 SKIP）：ko 侧 SFX region n=1（K11），`skip_policy/sfx_skip`，translated=0——与首跑口径一致，R13 n<15 只登记分布。
- **`sfx.policy=translate` 对照跑（AC3 加分项，SFX-ENTRY+PRIMARY 语义实战首验）**：
  - 通路：runner 新增 `--sfx-policy`（生产 settings 键 `settings["sfx"]["policy"]`，经 `save_settings_section` 写入 → close → **同 db re-assemble**（core_assembly 装配时读取语义，AC6 探针同序）→ region 创建时携带 policy）。
  - **配置语义验证成功**：sfx region 的 `sfx_policy` 字段实测 `skip`（主 pass）→ `translate`（对照 pass），生产 gate 按 `decide_sfx_translation` 语义**推断放行**进入正常翻译流（r1 R9 措辞更正：放行为推断——该 region OCR 为空、term_extract 先于 translate typed 失败，run 中不存在该 region 的 translate step、sfx 摘要 final_source=none；"放行"由配置生效 + 失败链位置证实，无 translate step 实证）——SFX-TRANSLATE-ENTRY 的装配语义在真实 run 中首次走通。
  - **端到端仍不可达（素材缺口）**：K11 唯一 sfx region 的 OCR 输出为空（首跑 F3 已登记该 region 无可识别文本），term_extract 先于 translate typed `INVALID_INPUT`——policy 放行后无源文本可翻。**结论：SFX 翻译语义无缺陷，但 ko 侧现有素材不存在"有 OCR 文本的 sfx region"；端到端 SFX 译文验证需要 ja BJ06 类素材（8 个有文本 sfx region，ja 范围外）或新素材，登记为裁决信息。**
  - 产物：[phase2/ko-rerun/summaries-sfx/qual-K11.sfx-translate.json](phase2/ko-rerun/summaries-sfx/qual-K11.sfx-translate.json)（独立 out-dir/pixel-root，不与主 pass 混淆）。

### 3.3 对白可读性工作表 ko 侧增量预填

- 首跑 ko 池受 F1 级联限制仅 11 条（K11）；本 run K02 解锁后 ko webtoon 译文池 93 条。
- 增量预填 **n=15**（K02 分层抽 12 + K11 抽 3），DeepSeek 自评（同 build_worksheets.py 锚点与 prompt，批 5 → 3 请求）：`ai_region_score` 均值 **4.31**（range 2.0–5.0——存在低分样本，自评有区分度，非全 5 锚定）。
- 产物：[phase2/ko-rerun/translate/dialogue-readability-ko-increment.csv](phase2/ko-rerun/translate/dialogue-readability-ko-increment.csv)。**ai_draft=自评预填，用户终审=唯一判定**（C1 模式）；首跑 n=26 工作表不动（禁改）。

---

## 4. render/export 确定性（AC4，remote 轨相似度 Gate）

- **轨道判定**：本 run translate 绑定为 remote DeepSeek → 按 thresholds §5 双轨规则走**相似度 Gate**（reading_order 对齐、normalized 相似度、median≥0.95 且 min≥0.70、空对规则、非空对 n≥1 覆盖前置）。export sha256 字节口径属 mock/deterministic 轨，本 run 仅附报。**r1 R3 控件落地**：§5 尾注要求的 `--determinism-track remote|mock` 显式记录 + 声明与 provider 绑定不一致时 fail-closed 报错，已实现于 `run_qualification.py`（装配前校验，干跑验证 exit 2）与 `ko_rerun_similarity.py`（计分前按两份 summary 的 provider 绑定校验，双轨不一致/unknown 均拒绝）；首跑时以 JSON 散文 note 替代、无 fail-closed（DSH r1 登记的缺口就此闭合），[K11-similarity.json](phase2/ko-rerun/determinism/K11-similarity.json) 已带 `determinism_track` 判轨字段重新落盘（全部数值逐位不变）。
- **执行**：K11 主 pass vs `--rerun-check` 复跑（同环境两次独立 run，间隔 ~2 分钟）；对齐校验全过（13 reading_order 集合相等 + 逐对 bbox 逐字段一致 + translate_details 全覆盖）。产物：[phase2/ko-rerun/determinism/K11-similarity.json](phase2/ko-rerun/determinism/K11-similarity.json)（脚本 `experiments/M2-TA3-B/ko_rerun_similarity.py`，方法复刻 CALIB 先例）。

| 项 | 实测 |
|---|---|
| 对数 / 非空对 | 13 / 11 |
| 逐位一致对（raw 口径，r1 R9 更正） | **11/13**——ro10 两版仅空白差（raw=0.9474 / normalized=1.0 被空白规范化吸收；JSON 逐对附 raw，CALIB 局限 5 口径）；normalized=1.0 口径为 12/13（median=1.0，`stats.n_variant=1` 即该口径） |
| 浮动对 | 1（reading_order=5，speech）：「没想到会做到这种地步」vs「我本以为没必要做到这种地步」，normalized **0.4615**（raw 同值） |
| Gate 判定 | **FAIL**（min 0.4615 < 0.70；median 腿 1.0 ≥ 0.95 不触发） |
| export sha | 两次不一致（附报；Run1 层非确定环节，首跑 F5 根因未隔离，本 run 无新证据） |

**归因（如实，不代裁）**：该浮动对是**语义等价的合法重译**（同义改写，非字符噪声、非漏译）。**判定依据（r1 R11 落盘）**：Owner 对源文「이렇게까지는 할필요없을줄 알았는데」逐句对照两版译文——「没想到会做到这种地步」与「我本以为没必要做到这种地步」均完整传达"（我）本以为没必要做到这种程度"语义，差异仅在语气与自谦显隐，无字符噪声、无漏译要素；判定人=本 Task Owner（ZCode，单标注者 directional 自评），**无独立第二审**——两版原文见 [K11-similarity.json](phase2/ko-rerun/determinism/K11-similarity.json) reading_order=5 对，列入 §7 裁决附件供用户复核。——这正是 M2-QUAL-DETERM-CALIB 局限 8 预言的"词面口径固有误报方向"（保守 FAIL）：字符级相似度把合法重译判为不稳定，而同义改写恰是 remote 采样漂移的主形态。**这是该误报形态的首次自然实测**（CALIB 的 18 对全是 1 编辑差）。其余 12/13 对 normalized 逐位一致（raw 口径 11/13+1 空白差）+ OCR 层 6/6 行逐位一致，说明本次 run 对的**采样稳定性量级与 CALIB 观测一致**。是否需要为"语义等价重译"修订 Gate 口径（语义度量/回译对照），属 thresholds 用户裁决事项，本报告不代裁。

- **K02 相似度复跑对照**：随预算停跑移交（任务书允许"K11 或 K02"，K11 已执行；K02 若在裁决后重跑可顺带补 ko webtoon 家族的 Gate 覆盖——CALIB 已登记该家族盲区）。

---

## 5. 全链 Gate 现状（如实汇总）

| 层 | 现状 |
|---|---|
| ja 侧 | **PASS 维持**（首跑 10/10；本 Task 未触碰 ja，无变化依据） |
| ko detect | F1 解锁实证（K02 93 region）；K01/K04/K05/K08 有 TILING GATE 先例、页级实测待裁决；K19 无字页 0 候选为正确行为，F4 口径（step=failed vs 豁免）未修维持 |
| ko import | F2 系 3 case（K07/K09/K10）本 run 未实测——ALLOC 解锁的页级确认随裁决 |
| ko OCR | K11 G1 自动子集 median 0.0556 PASS（directional，限定沿用）；OCR 层跨 run 确定性再证实（K11 未触发 tiling、与首跑同路径——§3.1 限定） |
| ko translate | K02 93/93 final 状态有译文（Run1 层完整）；Run2 独立重翻链受 API 故障 46 region typed 失败（environment）；SFX policy 语义走通、素材缺口登记 |
| ko render/export | K02/K11×2（主+sfx 对照）+K11.rerun export 全部 OK |
| 全链 Gate（pipeline_failures=0） | **FAIL（如实）**：7 case 未跑 + K02 environment 失败 + K11 F3 同型（data 预期）+ K19 F4（口径预期） |

---

## 6. 缺陷与新发现登记（typed）

| # | 归因 | 发现 | 证据 |
|---|---|---|---|
| N1 | environment | DeepSeek API 故障窗 ≈115 分钟：45×PROVIDER_TIMEOUT + 1×PROVIDER_INVALID_OUTPUT，全部 typed fail-closed、无重试风暴；恢复后链路正常 | `qual-K02.json` run2.per_region；budget-register.json api_outage_window |
| N2 | 纪律（非缺陷） | 全量外推 63 万–209 万 est token，超现行纪律（phase2-plan.md:192「数万 token 量级」）与编排会话停跑指令（>50 万即停，出处见 §1.2 r1 R1）→ 7 case 停跑等裁决 | §1.2 + budget-register.json |
| N3 | 观测（语义定稿预期） | K11 run1 状态 completed → completed_with_failures（r1 R4 归因链更正：BACKFILL R1 账目统一 → PRIMARY primary 纳入/页级决策链退役的定稿链语义——空 OCR region 失败计入 Run1 终态，与 Run2 口径一致化；终态路径 `service.py:1054`/`projection.py:336`） | §2 注 + 两代 qual-K11.json 对比（run1 步表页级 9 步 → region 级 ~66 步指纹） |
| N4 | 观测（请求结构，r1 R2 修订） | 生产翻译链每次请求恰 1 个 target region（K02 实测 140/140 实证）；「全链请求数 ≈2×region 数」**为上界假设、非实测常数**：K02 实测 1.51×（Run2 截断）、K11 实测 1.46×。**异常登记（open）**：K11 三个 pass 的 Run1 均仅 8 次调用（13 region/11 有文本；去重后仍 9 个不同文本，duplicate-text 不能完全解释），Run1 何时少于 region 数的机制未解释 | K02 计量 140/140 + K11 计量 19/13（`qual-K11.json` translation_metering）+ 三 pass run1 步表均恰 8 个 translate step |
| N5 | 观测（Gate 口径） | 相似度 Gate 的"合法重译误报"形态首次自然实测（K11 1/13 对，min 0.4615）；词面口径保守误报方向与 CALIB 局限 8 一致 | §4 + K11-similarity.json |
| N6 | 素材缺口（非语义缺陷） | sfx.policy=translate 生产语义走通（gate 放行为语义推断，r1 R9），但 ko 唯一 sfx region OCR 空，端到端 SFX 译文不可达；需有文本 sfx region 素材 | §3.2 + summaries-sfx/ |
| N7 | environment（harness） | ZCode 后台 Bash 任务 ~58 分钟被宿主强杀（exit 137）：首次 K02 尝试在 Run2 ~80/93 处被杀、summary 未落盘（scratch 残留 Temp，未清理）；改用独立 detached 进程后完成。**证据位置（r1 R8）**：`ko-rerun-logs/K02-rerun-attempt*.log` 与 `K11-driver-result.json` 在 `…task-envs/M2-TA3-B/ko-rerun-logs`——**仓库外，本仓库内仅本行登记、不可复核**（时间线可核部分在 budget-register.json api_outage_window） | 本行登记（仓库内）+ 仓库外日志 |
| N8 | 观测（产物结构，r1 R8） | `summaries/qual-report.json` 是 runner 每次调用的**覆盖型**输出：现内容=最后一次调用（K11 rerun-check pass）的 K11 skipped 条目 + failures=2，**不是** K02+K11+K19 的 run 级 roll-up（首跑该文件曾是汇总件，易误读）；run 级视图以 §2 对照表 + 各 `qual-*.json` 为准 | `ko-rerun/summaries/qual-report.json` 内容对照 |

## 7. 待裁决清单（移交用户/编排；r1 R7：逐项补成本/覆盖/Gate 后果，F1/F2 拆独立决策点）

> **裁决记录回填（2026-10-03，M2-TA3-B3-KO-FULLRUN 交付时）**：用户七项裁决（2026-10-02）已全部下达并执行完毕，逐项结论如下（执行证据见 [ko-fullrun-report.md](ko-fullrun-report.md)）：
> - **项 1 = 裁决「1 全量」（选项①）**：220 万 est token 上界获用户背书（case 级豁免记录落 budget-ledger `CEILING_BASIS`）；实测 950,954（43.2%），8/8 case 全链 export OK。
> - **项 2 = 裁决「2 重跑」**：K02 干净重跑完成（双 pass 全绿，首例 ko webtoon pipeline_failures=0 样本如预言产生）。
> - **项 3 = 裁决「3 按推荐」**：F1 关闭采组合口径（detect 5/5 + 全链 8/8），已在 ko-fullrun-report §3 落地关闭。
> - **项 4 = 裁决「4 按推荐」+「SFX 素材全权」**：F2 页级实测由项 1 全量自然覆盖（K07/K09/K10 export OK，F2 关闭）；SFX 素材路线另行释放为 M2-SFX-E2E-MATERIAL 并已闭环。
> - **项 5 = 裁决「5 按推荐」**：50 万红线追认为编排口径（与 phase2-plan.md:192 并行登记）；本次全量运行受 220 万 case 级豁免上界约束（用户背书）。
> - **项 6 = 裁决「6 同意」（选项③）**：known-limitation 登记落地 `quality-thresholds.md` §5（2026-10-03 注）；K02 干净重跑 93 对形态（min=0.0 合法重译）再证实，Gate 维持 FAIL 按 directional 接受。
> - **项 7 = 裁决「7 按推荐」**：SFX 端到端素材路线由 M2-SFX-E2E-MATERIAL 执行（BJ06 ja 先行端到端闭环 + densho810 vol03 素材入池），ko 侧 0 增量。

1. **7 个停跑 case 的范围与预算**（§1.2 选项①–④）。成本/覆盖（按 §1.2 的 2× 上界模型，1.5× 敏感性见该节）：①预算批准全量 ≈107 万–209 万 est token（881–1721 region），覆盖=F1 系四页 + F2 系三页全部页级实测；②`--max-regions` 逃生阀明示抽样，成本随 N 线性、Gate 分母变为抽样集（R7 披露义务随之触发）；③仅 F2 系 K07/K09/K10 ≈44 万–146 万（估计 360–1200 region），兼收 ALLOC 解锁确认；④维持停跑=0 增量成本、覆盖不变。Gate 后果：①/②/③均可推进 ko 全链 Gate 的 case 覆盖，④维持 §5 FAIL 构成现状。
2. **是否干净重跑 K02**（+186 请求 ≈113k est token，2× 上界口径）：当前 K02 summary 的 Run2 带 46 region environment 失败。覆盖：ko webtoon 家族相似度 Gate（CALIB 登记的盲区家族）+ AC1 完整样本。Gate 后果：可产生首个 ko webtoon 全链 pipeline_failures=0 样本（现不存在）；不跑则 K02 维持 environment 失败登记。
3. **F1 关闭口径（独立决策点，r1 R7 拆出）**：是否仅凭 TILING detect 层 5/5（K01=180/K02=93/K04=113/K05=62/K08=60 region，独立 Task GATE PASS）+ K02 全链 1/5 关闭 F1，还是必须补 K01/K04/K05/K08 页级全链实测。若必须：四页合计 415 region，按 2× 上界 ≈ K01 218k + K04 137k + K05 75k + K08 73k ≈ **50.4 万 est token**（1.51× 敏感性 ≈ 37.9 万）。Gate 后果：前者 F1 就此关闭（detect 级+页级组合证据，本报告 §2 现表述）；后者追加四页全链行为证据后关闭。
4. **F2/ALLOC 页级必要性（独立决策点，r1 R7 拆出）**：ALLOC 解锁确认是否必须页级全链实测（=项 1③的 K07/K09/K10 ≈44 万–146 万），或可由 import 层轻量探针替代（新 Task 范围、非本 Task 面）。Gate 后果：前者 F2 关闭确认落页级；后者 F2 维持"import 层 PASS、页级未实测"的登记现状。
5. **红线口径追认（r1 R1，集成方/用户裁决项）**：「est token 外推 >50 万即停」为编排会话指令数值、无任务书/用户裁决原文背书；仓库现行纪律为 phase2-plan.md:192「数万 token 量级，超预期即停并登记」。若认可 50 万为新口径需落文（Task 纪律或 phase2-plan 修订，集成方执行）；否则以 phase2-plan.md:192 为准。本次停跑在两种口径下均成立。
6. **相似度 Gate 对"合法重译误报"的口径处理**（thresholds 用户裁决事项，r1 R7 补后果）：①维持现阈值=K11 类语义等价重译继续保守 FAIL（系统性误报、方向安全，现状）；②引入语义度量=需新 Task+校准（成本=新校准集与新阈值定义，本对可入校准集）；③登记 known-limitation=本次 Gate 维持 FAIL 记录、按 directional 接受。判定依据见 §4（r1 R11），供用户复核该对归类。
7. K11 `sfx.policy=translate` 端到端素材路线（ja BJ06 或新素材，非 ko 范围；ko 侧增量成本 0）。

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

> 产物索引（r1 R8）：`summaries/qual-report.json` 是 runner 每次调用的**覆盖型**输出，当前内容=最后一次调用（K11 rerun-check pass），**非** run 级 roll-up——run 级视图以 §2 对照表 + 各 `qual-*.json` 为准（N8）。判轨控件（r1 R3）零成本干跑：`"$PY" experiments/M2-TA3-B/run_qualification.py --case K02 --determinism-track mock` 应在装配前 fail-closed 退出（exit 2，FATAL 指出声明 remote 绑定矛盾）；`--determinism-track remote` 通过该检查。

---

*方向性证据声明：单标注者 + AI 预填锚定未测量；全部数字不得引用为生产结论。判定权威=用户本人。*
