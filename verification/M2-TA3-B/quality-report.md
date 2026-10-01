# M2-TA3-B 阶段二质量报告：20-case 正式 qualification run（阈值实测 vs 提案对照）

- Task：[M2-TA3-B2](../../doc/tasks/M2-TA3-B2.md) · 分支 `agent/zcode/M2-TA3-B2` · 日期 2026-10-01
- 口径权威：[quality-thresholds.md](quality-thresholds.md)（阶段一冻结提案，用户可撤销）· 执行蓝图：[phase2-plan.md](phase2-plan.md)
- 判定权威：**用户本人**。本文全部 AI 预填/自动数字为**方向性证据（directional）**，不外推生产结论。
- 翻译 endpoint：用户裁决 (a) DeepSeek remote（`base_url=https://api.deepseek.com/v1`、`model=deepseek-chat`、目标语言 zh=§0 默认）；key 仅经环境变量 `TA3B_TRANSLATE_API_KEY` 注入，**全链路零明文入库**（记录 JSON 已程序化核验）。

---

## 0. 执行摘要

| AC | 结果 |
|---|---|
| AC1 全链 run | **执行完成，全链 Gate FAIL（如实登记）**：ja 10/10 case 全链 completed + export OK（56 region，48 翻译=56−8 SFX）；ko 1/10（K11）export OK 但 run2 携带 2 个 typed data 失败；ko 其余 9 case 全部 fail-closed 于两条**生产域缺口**（§4 发现 F1/F2）。`pipeline_failures=10`（构成附表见 §1.1a） |
| AC2 自动评测 | ko G1 自动子集 n=6，**CER 中位数 0.0556（提案 ≤0.20 → PASS，directional；剔除方向系统性偏低，见 §2.3）**；ja G1 **NOT_AUTOMATED**（无效对齐，见 §2.2）；SFX n=0<15 只登记分布；region_count=0 豁免条款按 R11 执行 |
| AC3 渲染确定性 | BJ02 **PASS，语义=Run1 页面级渲染产物两次独立 run 逐位一致**（机制说明：export 复制 Run1 落盘产物，Run2 不重渲染——§5）；K11 FAIL，根因=**Run1 内非确定环节（未逐层隔离；OCR 已排除）**；Run2 译文浮动（7/11 非空口径）为**独立的 remote 非确定性观察**，不进入 export；K01 无 export 产物（NOT_ACHIEVABLE，data） |
| AC4 对白可读性预填 | 工作表 n=**26**（ja15+ko11；ko 池受 §4-F1 级联限制不足 15，如实登记），DeepSeek 自评 `ai_draft` 预填 + owner 6-crop 抽检校准（方向一致、轻度偏高），**用户终审=唯一判定（后续步骤，非本 Task 关闭条件）**。**对 AC4 字面要求的双缺口**：n=26<30 + **SFX 示例=0（生产 SfxPolicy 默认 SKIP，SFX→translate 通路未满足前置，见 §3.1）** |
| AC5 文档精修 | r2 N1/N2/N4/N5/N6 已落地（commit `b7806dac`） |
| AC6 第 0 步探针 | **PASS**：profile 写入→binding→同 db re-assemble（vault 通路如实落地 `MISSING_CREDENTIAL`=r2-N4 预测的缺口实证）→env resolver re-register+invalidate→readiness `ready`→1 真实 region 翻译 0.45s（`verification/M2-TA3-B/phase2/translate-probe.json`）。**限定（r1 R13）：该 READY=endpoint-only descriptor 语义（探针 re-register 的 descriptor 只含 KIND_ENDPOINT 要求），不等价于生产描述符的 READY 语义（生产 vault 路径的 MISSING_CREDENTIAL 缺口仍然存在）** |

成本（**estimated，非计量**，r1 R11）：翻译链 + 探针 + 评分自评**估计 93–104 次请求**（间接推导：Σ(1+region)=69 + 复跑集合 ≈20 + 探针 1 + 自评批 3；K07/K09/K10 import 失败 0 请求已扣除）；**token 量无计量证据**（产物无 usage 字段），Task 纪律的「数万 token 量级」口径无法核对，如实登记为未计量。未观察到重试风暴（全部失败为 fail-closed typed，重试仅走生产 retry 语义）；「runner/探针落盘每请求 usage」登记为后续 runner 增强候选（见 handoff 返修记录）。

---

## 1. 全链 run 结果（AC1）

生产 seam：`assemble_core_services`（Qt offscreen）→ Run1 `PAGE_SELECTION/TRANSLATE_ALL`（生产 planner 自动前置 detect=manga ogkalu + chiqui7 SFX）→ 每 region Run2 `RETRANSLATE_REGION_FULL`（**默认无截断**，R7；本 run 未使用 `--max-regions`）→ 生产单图 export。明细：`phase2/summaries/qual-<case>.json` ×20 + 汇总 `qual-report.json`；region crop/export PNG 落 Git 外 `task-envs/M2-TA3-B/phase2-pixels/`——该目录是**仓库树之外的兄弟目录**，Git 天然不可见（与 `.gitignore` 无关，r1 R8 修正原表述）；其复核前提由 `phase2/pixels-manifest.json` 固定（126 文件的相对路径+size+sha256，`experiments/M2-TA3-B/verify_exports.py` 生成），路径同时记录在各 summary 内。

### 1.1 per-case 状态

| case | lang | regions | translated | run1 | run2 | export | wall_s | 归因 |
|---|---|---|---|---|---|---|---|---|
| BJ02 | ja | 5 | 5 | completed | completed | OK | 161.5 | — |
| BJ03 | ja | 2 | 2 | completed | completed | OK | 109.6 | — |
| BJ04 | ja | 3 | 3 | completed | completed | OK | 107.4 | — |
| BJ05 | ja | 1 | 1 | completed | completed | OK | 88.0 | — |
| BJ06 | ja | 17 | 9 | completed | completed | OK | 263.6 | 8 个 sfx region 走生产 SKIP 门（协议内） |
| BJ08 | ja | 3 | 3 | completed | completed | OK | 99.9 | — |
| BJ10 | ja | 11 | 11 | completed | completed | OK | 315.8 | — |
| BJ11 | ja | 8 | 8 | completed | completed | OK | 228.1 | — |
| J46 | ja | 1 | 1 | completed | completed | OK | 20.9 | — |
| J47 | ja | 5 | 5 | completed | completed | OK | 60.0 | — |
| K01 | ko | 0 | 0 | completed_with_failures | SKIPPED | — | 2.8 | data/defect：detect 无候选（F1） |
| K02 | ko | 0 | 0 | 同上 | SKIPPED | — | 1.5 | F1 |
| K04 | ko | 0 | 0 | 同上 | SKIPPED | — | 1.9 | F1 |
| K05 | ko | 0 | 0 | 同上 | SKIPPED | — | 2.3 | F1 |
| K07 | ko | 0 | 0 | — | — | — | 0.1 | data：import 拒绝（F2；归因为**推断**——Qt `QImageReader` 内建 256MB 分配上限，原始 Qt 日志未归档，见 F2 行） |
| K08 | ko | 0 | 0 | 同 K01 | SKIPPED | — | 2.5 | F1 |
| K09 | ko | 0 | 0 | — | — | — | 0.1 | F2 |
| K10 | ko | 0 | 0 | — | — | — | 0.1 | F2 |
| K11 | ko | 13 | 11 | completed | completed_with_failures | OK | 89.4 | 2 个 OCR 空文本 region 的 `term_extract` typed INVALID_INPUT（F3，data） |
| K19 | ko | 0 | 0 | 同 K01 | SKIPPED | — | 1.0 | F1（页面实测 1200×1660，`qual-K19.json`；2481×3503 是 SVG canvas 口径、来源 `svg-gt-manifest.json`——两口径勿混）。该页所有语言 SVG 文本层为 0 元素=无字页，检出无候选是正确行为，但生产 step 状态为 failed/INVALID_INPUT——口径问题见 F4） |

ja 侧 10/10 全链通过（`pipeline_completed=true`）；ko 侧 9 case 失败 + K11 携带 2 个 region 级 typed 失败 → **全链 Gate（pipeline_failures=0）FAIL**。所有失败均为 fail-closed typed（无静默降级、无 paper-over），复现信息见 §4。

### 1.1a `pipeline_failures=10` 的构成（r1 R6 附表）

`failures=10` 是 **case 级失败计数 + AC3 复跑集合级计数**的合计（`run_qualification.py:764-765,851-852`；r1 时行号 725-726/795-796，R2/R13 插入后偏移），不是 10 个区域级失败。逐条构成：

| # | 计数单位 | 归因 |
|---|---|---|
| 1-6 | K01 / K02 / K04 / K05 / K08 / K19（主 pass case 级） | F1：ogkalu 对 webtoon 长条漫 0 候选（`data:no-regions-detected`；K01 即 AC3 的 NOT_ACHIEVABLE） |
| 7-9 | K07 / K09 / K10（主 pass case 级） | F2：Qt import 拒绝（`environment:import-failed`） |
| 10 | AC3 复跑集合计数（集合级布尔，非逐 case） | 复跑集合 `all(match)=false`：K11.rerun export 哈希不一致 + K01.rerun 双侧无 export（两个 `match=false` 合并计 1 次） |

另注：K11 主 pass `run2=completed_with_failures`（2 个 OCR 空文本 region 的 typed INVALID_INPUT，F3 data）使其 `pipeline_completed=false` 如实登记于 `qual-report.json`；`failures=10` 的上述口径以该文件 note（consolidated re-summary）为准。

### 1.2 与阶段一冒烟事实的一致性

- `enable_mkldnn=False` 固定在 wrapper 内，ko OCR 全程无 PIR/oneDNN 崩溃（阶段一发现 1 保持有效）。
- webtoon 长图未整图直喂 PaddleOCR（阶段一发现 2 教训写死于 runner 注释）——本 run 的长图失败全部发生在**上游**（detect/import），与该教训一致。
- PaddleOCR bytes 静默缺口经双侧 wrapper 绕行成功：K11 13/13 region OCR 完成、0 异常（阶段一发现 3 的绕行路线有效；`src/` 零改动，修复 Task 建议维持阶段一登记）。

---

## 2. OCR 质量实测（AC2）

### 2.1 阈值对照总表

| # | 阶段 | 提案 Gate | 实测 | 判定 |
|---|---|---|---|---|
| 2 | OCR ja G1 | CER 中位数 ≤0.10 | **无有效自动样本**：J46 唯一 region 命中 4 个 SVG 元素中的 3 个（`MANUAL_REVIEW:3-svg-elements`，多元素拼接 GT 非真值，r1 R5 修正原「混入 4 个元素」表述）；J47 命中行 GT/OCR char_overlap≈0.167 <0.3（SUSPECT）→ 全部标 `MANUAL_REVIEW`/`SUSPECT_MISMATCH`，不进自动 CER | **NOT_AUTOMATED**（§2.2） |
| 4 | OCR ko G1 | CER 中位数 ≤0.20 | K11 自动子集 **n=6、median=0.0556、P90=0.3333、CER=0 占比 50%**（对齐抽验 4/4 正确） | **PASS（directional，n 小须携带）** |
| 3/5 | ja/ko 全量（G1+G2） | ≤0.15 / ≤0.25 | G2 人工 GT 未生成（用户审核属后续步骤）；`cer-regions.csv` 已按 `G2:pending_human_worksheet` 留 50 行待审 | 未测（脚本与数据就绪） |
| 6 | 人工抽检 n=30 | 方法设计 | 骨架 28 行（ja15+ko13；ko 池受 F1 限制）+ `ai_draft` 列待预填/终审 | 后续步骤 |

明细：`phase2/ocr/cer-regions.csv`（69 行）· `phase2/ocr/cer-summary.json` · 对齐轨迹 `phase2/ocr/svg-alignment-trace.json`。

### 2.2 ja G1 NOT_AUTOMATED 的归因（N1 登记口径的执行）

阶段一 R2/O-3 已声明 ja G1 子集=credits/结束卡文本、代表性受限；本 run 实测进一步发现：**J46/J47 的 SVG credits 文本与 ogkalu detect 检出的 region（气泡对白）在空间上不重合**——自动几何对齐产出的"命中"实为文本族错配（J46 唯一 region 命中 4 元素中的 3 个=多元素拼接、按 §5 风险 2 禁止自动计分，r1 R5 修正原「混入 4 元素」表述；J47 命中行 GT=`あなたもPepper&Carrotのパトロンになりましょう…` vs OCR=`そういえば、`，char_overlap≈0.167<0.3、唯一共有字符「う」，r1 R5 修正原「重叠 0」表述）。按 thresholds §5 风险 2 预案，这类行**必须人工仲裁、禁止自动计分**。结论：ja G1 CER 在本 run 无有效自动样本，NOT_AUTOMATED 如实登记；G1 评测需用户人工 bbox 指认后重算（脚本已支持）。

### 2.3 ko G1 有效子集（directional）

对齐方法=flowRoot rect 几何变换求交（机械化版 N1 人工对齐）；多元素命中/空 OCR/低重叠行全部排除出自动分母。有效 6 行：

| region | GT | OCR | CER |
|---|---|---|---|
| eada0f25 | 당근아? | 당근아? | 0.000 |
| 1fd86809 | 당근아?! | 당근아?! | 0.000 |
| 91a52031 | 당근아?!!! | 당근아?!!! | 0.000 |
| 71a21be8 | 이렇게까지는할 필요 없을 줄알았는데.. | 이렇게까지는 할필요없을줄 알았는데 | 0.111 |
| 152ac05d | 어라? 침대 밑에도없네? | 어라? 침대 믿에도 니? | 0.273 |
| 789ed861 | 꼬르륵 | 꼬르를 | 0.333 |

owner 抽验（thresholds §5 风险 2 要求的抽样人工核对）：4 个 crop 图与 GT 逐一对照（당근아?/어라?침대밑에도없네?/이렇게까지는…/꼴륵 拟声词），**4/4 对齐正确**；152ac05d 与 789ed861 的 CER 来自真实 OCR 字符错误（밑→믿、륵→르），非对齐噪声。**ko G1 中位数 0.0556 ≤ 0.20 判 PASS**——但 n=6 且对齐人工复核仅抽样级，数字必须与"directional、样本极小"一起引用；O-1（ko 阈值确认）与 O-3（G1 代表性）仍待用户裁决。

**剔除规则的方向性披露（r1 R5）**：自动分母的排除规则（UNALIGNED / 多元素 / 空 OCR / char_overlap<0.3）**单向偏向低 CER**——`cer-summary.json` 的 `excluded[]`（13 行：ko 7 + ja 6）逐条登记了被剔行与"若计分的 CER"：ko 侧被剔行中 **K11:65069961 是真 OCR 失败（GT=`당근아!`、OCR 空、CER 恒 1.0）却被剔除**，另有多元素行 0.5/0.6897/1.0/0.45 可计（多元素 GT 为拼接非真值，只作上界参考）——**0.0556 是系统性下偏统计量，PASS 判定的方向性强度因此进一步受限**。且 6 个自动样本中 3 行为同一条 4 字短串（당근아? 系），有效独立文本仅 4 种。若把 ko 侧可计被剔行并入（仅作示意，多元素拼接 GT 使精确反事实不可算），中位数将升至 ≈0.33 量级、越过 0.20 提案线——**该 Gate 的真实状态是"方向性证据、强烈依赖剔除规则"，最终裁决权在 O-1/O-3**。

### 2.4 R8 正式计数（G1 提取落盘清单）

`phase2/ocr/svg-gt-manifest.json`：ja ep20 lang-pack zip 内 `.svg` 成员 **352**；ko ep04 zip **472**（阶段一侦察把 ep04 的 472 当成了两包通用数，ep20 实为 352——以本清单为准）。文本元素：J46=4（text）、J47=2（text）、K11=26（flowRoot，几何可自动对齐）、**K19=0（E20P01 在所有语言均为无文本 SVG——无字页）**。

---

## 3. translate 质量实测（AC2/AC4）

### 3.1 口径 A：SFX 文化对等（§3.1）

- 本 run SFX region 共 **9 个（8 BJ06 + 1 K11；r1 R6 修正原「全部在 BJ06」表述——K11:65069961 亦为 sfx region，即 OCR 空白的那个）**，全部被生产 `decide_sfx_translation` 门判 `skip_policy/sfx_skip`（生产 `SfxPolicy` 默认 SKIP，产品当前无改置入口——runner 未绕过生产语义）→ **自动翻译 SFX 样本 n=0**。
- 按 R13：n<15 只登记分布、不判 Gate。分布=空（0/9 翻译，9/9 生产 SKIP）。**SFX prompt 特化（SFX-SEM-1 落地核对）在本 run 中未被真实触发**——Gate 延后至素材扩充（thresholds §3.1 预案）；若要测 SFX 翻译语义，需产品先提供 SFX→translate 策略入口（登记为需求，见 §5）。
- 表：`phase2/translate/sfx-semantic-worksheet.csv`（空表+登记行）。

### 3.2 口径 B：对白可读性（§3.2，AC4）

- 工作表：`phase2/translate/dialogue-readability-worksheet.csv`，**n=26（ja 15 + ko 11）**。ko 配额（15）不足：ko 侧可评样本上限=K11 的 11 条译文（F1 级联效应），如实登记，不虚构样本。**对 AC4 字面要求的两个缺口（r1 R12 并列挂账）**：①n=26<30；②**BJ06/BJ10 SFX 示例=0——生产 SfxPolicy 默认 SKIP 使 SFX region 无译文，SFX→translate 通路未满足前置条件**（§3.1）。
- 三维 5 分制（忠实/流畅/语境，region 分=三维均值，锚点逐维独立）；`ai_draft` 列=**DeepSeek 自评预填**（自评锚定风险按 §3.2 声明）；owner 抽检校准 6 crop（4 ko 对齐 + 2 ja 译文）：自评方向一致、轻度偏高（BJ06:fb648685 忠实度 5 略高，owner 判 4）。**用户终审=唯一判定**——提案 Gate（中位数 ≥3.5 且 ≥3 占比 ≥80%）在本阶段不判定。
- 参考（非判定）：ai_draft 均值 ≈4.5（ja 15 条 3.0–5.0，ko 11 条 4.0–5.0）。

### 3.3 口径 C：回译一致性

跳过（§3.3 可选附报，不影响 Gate）。

---

## 4. 失败归因登记（三向归因，defect 级逐条复现）

| # | 归因 | 发现 | 复现信息 | 修复候选 |
|---|---|---|---|---|
| F1 | **data × 产品检测域缺口** | manga ogkalu backend 对 webtoon 长条漫返回 0 候选：K01(690×62133)/K02(600×18401)/K04/K05/K08 页 import 成功但 detect step typed failed `INVALID_INPUT: detector returned no candidates`；K19(1200×1660 无字页；r1 R6 修正原 2481×3508 误写——那是 SVG canvas 口径) 同状态（检出无候选对无字页是正确行为，但生产 step 状态=failed 而非空成功，见 F4）。**与 TA3-A 的对照（r1 R3 改述）**：同一页面上 docTR 有候选（TA3-A 记录 K01=15、K02=7 region）、ogkalu 路径 0 候选——两轮 summary 的 `source_sha256` 同页实证（K01=`600ca755…`、K02 同型），是**同页不同 backend 检出能力**，不是"两 backend 页面形态域不同"；0 候选的**适配器级机制（整页重缩放 vs 分块等）尚无证据**（summary 只有 status/region_count=0），建议 A 实施前需先补 `n_text_raw`/`n_bubble`/送入 tensor 尺寸等适配器可观测值 | `python experiments/M2-TA3-B/run_qualification.py --case K01`（env 权重路径见 runner 头） | **Task 建议 A**：webtoon 长条漫分块检测（tile）或 per-family backend 路由（产品裁决）；**前置**：先补适配器可观测值再定机制归因；**口径注**：thresholds §1"detect step completed"口径与生产"no candidates=step failed"不一致，需 Codex 裁决统一 |
| F2 | **data × 依赖默认上限** | K07(690×131289)/K09(690×100480)/K10(690×100674) import typed 失败：归因为**推断口径（r1 R4）**——Qt `QImageReader` 内建 256MB 解码分配上限。推断依据=①尺寸边界（K07≈345.6MiB / K09≈264.5MiB / K10≈265.0MiB，均 >256MiB 上限；F1 五例全部 <256MiB 且 import OK）；②Qt `QImageReader` 内建默认上限（`importing.py:45-59` 无 allocation limit 设置点）。**原始 Qt 日志未归档**（summary per-file detail 为空串，run_qualification.py 在 per-file error/detail 皆空时产出空串），故本行不引用未归档的 Qt 原文；如需一级证据，复跑一次并把 importer 的 per-file error/detail 未截断落盘 | 复现命令同上 `--case K09`；尺寸链自洽见发现列 | **Task 建议 B**：导入器按页面形态调高/可配置 allocation limit（src 修改，须 Codex 释放） |
| F3 | data | K11 2 个 region（df871de5/65069961）OCR 输出空白（该 crop 无可识别文本），下游 `term_extract` step typed `INVALID_INPUT: region has no OCR text to extract terms from`（fail-closed 正确行为）；run2 因此 `completed_with_failures` | `qual-K11.json` run2.per_region（status!=completed 的 steps） | 无修复需求（typed fail-closed 正确）；体验层"空白 region 是否应进入 region 链"可作后续讨论 |
| F4 | 口径（非运行失败） | thresholds §1 预期"0 region 记 `data:no-regions-detected` 不判 FAIL"，但生产 detect 对无候选页面的 step 状态是 `failed/INVALID_INPUT`——**文档口径与生产 fail-closed 语义错位** | 同 F1 | thresholds §1 口径由 Codex/用户裁决修订（建议改为"detect step 无 defect 级错误且 region=0 时按 data 豁免"） |
| F5 | **确定性机制（AC3 根因，r1 R1 重写）** | **export 消费的是 Run1（页面级 TRANSLATE_ALL 链，含真实 detect+OCR+批量翻译+inpaint+render）渲染步骤落盘的产物；Run2（RETRANSLATE_REGION_FULL）只更新 DB 译文/revision，不触发重渲染**（集成方实算机制事实：`BJ02-translated.png` 与 `BJ02.rerun-translated.png` mtime 相差 25 分钟=两个独立写入的真实文件、sha256 逐位相同、而 `translated_revision_id` 不同）。由此：①BJ02「确定性 PASS」的真实语义=**Run1 页面级全链两次独立 run 逐位一致**（仍是有效证据，但**不是**「region 重翻→渲染→export」端到端确定性）；②K11 export 哈希不一致的根因在 **Run1 内部的非确定环节（未逐层隔离）**——export 只反映 Run1，OCR 层已排除（两次 run OCR 0/13 差异），候选=Run1 批量翻译/inpaint/渲染（scratch db 已清理，无法事后逐层隔离）；③**Run2 译文浮动（7/11 非空口径，DSH r1 修正原 7/13 混用分母）是独立的 remote 采样非确定性观察，不进入 export**。BJ02 自身亦证 remote 非确定：同 bbox/同 reading_order region 译文 `所谓强大`→`所谓强啊` | `qual-BJ02(.rerun).json` / `qual-K11(.rerun).json` + `rerun-compare.json`（r1 R2 重建为 3-case）；机制说明见 §5 | 产品无缺陷：revision 机制保证"同 revision 重渲染"确定；**"跨 run export 哈希逐位一致"作为确定性 Gate 在 remote 翻译下需重新定义（如按 reading_order 对齐的译文相似度而非字节逐位）——裁决点移交（§8/§9 F5）** |
| F6 | environment（已消解） | 首轮 K11 全部 region OCR typed 失败：生产 OCR 步骤 script 默认 `japanese`（`handlers.py` `settings.get("script", SCRIPT_JAPANESE)`），ko 页被 paddleocr-korean slot 拒绝 | 首轮 `qual-K11.json`（已重跑覆盖） | runner 修复：ko case 经生产通道 `save_settings_section("ocr", {"script": "korean"})`（`b7806dac` 之后的 runner 修订）；**登记**：ko case 必须设置该 settings 键，否则 typed fail |

export 哈希独立复算（§5 口径，runner 之外）：**13 个 OK export（11 首跑 + BJ02.rerun/K11.rerun 两个复跑导出）sha256+size 全部一致**（`phase2/export/export-hash-recompute.json`，r1 R7 起生成脚本入库：`experiments/M2-TA3-B/verify_exports.py`，记录含像素相对路径）。

---

## 5. render/export 确定性（AC3，r1 R1 重写）

**机制前提（本节结论的解释框架）**：runner 的 export 段从 `reader_page.translated_path` 读取字节（`run_qualification.py` export 段）——该文件是 **Run1（页面级 TRANSLATE_ALL 链）渲染步骤落盘的产物**；后续的 region 级 Run2（RETRANSLATE_REGION_FULL）只更新 DB 译文/revision，**不触发页面重渲染**。因此 export PNG 反映的是 **Run1 渲染**，不是 Run2 的 region 译文（集成方实算机制事实：BJ02 两个 export PNG mtime 相差 25 分钟=两个独立写入的真实文件，sha256 逐位相同，而 `translated_revision_id` 分别为 `7f7626c0…`/`d7adba58…`）。

| case | 首跑 sha256 | 复跑 sha256 | 判定（r1 R1 修正语义） |
|---|---|---|---|
| BJ02 | 5c74a4f0…d5417 | 同左 | **PASS——语义=Run1 页面级全链（真实 detect+OCR+批量翻译+inpaint+render，含 remote 批量翻译）两次独立 run 逐位一致**。仍是有效证据，但**不是**「region 重翻→渲染→export」端到端确定性（Run2 不进入 export；同 bbox region 译文 `所谓强大`→`所谓强啊` 亦证 Run2 remote 非确定） |
| K11 | 2c5dee05…1b1a | 86ff9aa7…92da | FAIL——根因=**Run1 内部非确定环节（未逐层隔离）**：export 只反映 Run1，OCR 层已排除（两次 run OCR 0/13 差异），候选=Run1 批量翻译 / inpaint / 渲染（scratch db 已清理，无法事后逐层隔离）。**Run2 译文浮动（7/11 非空口径）是独立的 remote 非确定性观察，不进入 export、不构成对本次 FAIL 的解释** |
| K01 | —（无 export，F1） | — | **NOT_ACHIEVABLE（data）** |

**方法学事实（r1 R1 登记）**：region_id 每次 run 重新生成（同 bbox 两轮 uuid 不同，如 BJ02 `aa2bd2a2…`/`d90b0fca…`）——两次 run 的逐位比较只能按 **reading_order** 对齐（`rerun-compare.json` 已登记）；文本级对照亦按 reading_order 逐对进行。

结论（**r1 R1 撤销原表述**）：~~「TA3-A 确定性框架在输入确定前提下继续成立」~~——TA3-A 的确定性结论隐含"export 直接消费当轮渲染产物"的结构前提，本 run 的 runner 结构下字节级 export 对照对 Run2 region 链是**空转**，故该结论不能原样延续。本 run 能支撑的确定性陈述收窄为：①Run1 页面级渲染产物（BJ02）两次独立 run 逐位一致；②OCR 层（K11，paddle wrapper）两次 run 逐位一致；③remote 翻译（Run1 批量或 Run2 region 级）存在采样级非确定性。**"跨 run export 哈希逐位一致"作为确定性 Gate 在 remote 翻译下需重新定义（候选方向：按 reading_order 对齐的译文相似度阈值，而非字节逐位）——作为 F5 裁决点移交 Codex/用户（§8/§9），本报告不代裁**。R15 的"固定 3 case"中 ko webtoon 家族（K01）在本生产 detect 配置下无产物，该家族的确定性验证随 F1 修复后补测。

---

## 6. inpaint 定性抽检（§4，无数值 Gate）

`phase2/inpaint/inpaint-spot-check-worksheet.csv`：n=8（plain_balloon 5 + complex_background 3；SFX 层因生产 SKIP 无产物，如实登记）。SimpleFillProvider=基础填充，本环节只验执行正确性（region 被处理、产物可渲染）——全部 11 个 export PNG 可渲染且 reader_catalog 可解析（run2+export OK 的隐含条件）；残影判读（no/slight/yes）待用户。

---

## 7. 环境（R16）

单 venv 融合（§2.4 方案 A）：`task-envs/M2-TA3-B-ocr/`（隔离 OCR venv + 生产 requirements）。`pip check` EXIT=0；六项版本对照与偏差说明：`phase2/env-manifest.txt`（torch 2.14.1→2.14.0、transformers 5.18.0→5.17.0 对齐生产 pin；numpy 维持 paddle 系要求的 2.3.5；opencv 双包共存，`import cv2` 解析 5.0.0.93，paddle 3.3.1 端到端实测工作）。权重全部 Git 外（ogkalu 三文件快照目录 + chiqui7 onnx + HF/paddlex 缓存）。

---

## 8. 裁决点状态（引用阶段一编号）

| 裁决点 | 本 run 后的状态 |
|---|---|
| O-1（ko 阈值 ≤0.20/≤0.25） | ko G1 实测 median 0.0556 远低于提案 0.20——但 n=6 且 webtoon 主域（G2）无数据（F1），**不建议以本 run 数字调阈值**，待 F1 修复后补测再裁 |
| O-2（G2 审核工作量） | G2 待审 50 行已就绪（`cer-regions.csv` + crops），交用户决定是否审 |
| O-3（G1 代表性） | ja 侧获得实证：SVG credits 与 detect region 文本族**空间不重合**（§2.2）——"G1 仅作引擎量级校验"的裁决必要性上升 |
| T-1/T-2（translate Gate 数值/最小 n） | SFX n=0（生产 SKIP 语义），Gate 未触发；T-2 的"素材扩充"路径需先解决 SFX→translate 产品入口 |
| T-3（目标语言 zh） | 已按 zh 执行 |
| T-4（endpoint 选择） | 已裁决 (a) DeepSeek 并执行 |
| 新裁决点（建议） | F1/F2 修复 Task 的释放与优先级；F4 口径修订；**F5 确定性 Gate 口径重定义（r1 R1：字节逐位口径在 remote 翻译下失效——候选方向=按 reading_order 对齐的译文相似度阈值，需 Codex/用户裁决；重定义前 thresholds §5/§7 的对应条目按 superseded-pending 引用，见 quality-thresholds.md 交叉注）** |

---

## 9. 与修复候选 Task 的交接清单

1. **PaddleOCR 3.x 生产适配**（阶段一登记，本 run 继续有效）：输入契约 fail-closed/ndarray 化、输出形状 3.x→legacy、双 region bytes 行为判定。
2. **Task 建议 A（新）**：webtoon 长条漫检测支持（分块检测或 backend 路由）——影响 AC1 全链 Gate 的最大单因（6 case）。
3. **Task 建议 B（新）**：导入大图支持（QImageReader allocation limit 可配置）——影响 3 case。
4. （登记）SFX→translate 策略的产品入口（SFX 语义评测前置条件）。
5. （口径）F4 的 detect 冒烟口径修订 + F5 的确定性口径重定义（r1 R1：从"export 哈希逐位一致"改为 remote 翻译下的新口径，候选=reading_order 对齐译文相似度；重定义前按 superseded-pending 引用）。
