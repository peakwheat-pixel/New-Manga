# M2-TA3-B 各阶段质量阈值定义（阶段一提案版）

- Task：[M2-TA3-B](../../doc/tasks/M2-TA3-B.md) 阶段一 AC1 · 分支 `agent/zcode/M2-TA3-B` · 日期 2026-10-01
- 文档性质：**PROPOSAL（提案）**——各阈值数值由本 Task（acting Codex 裁决权限）登记提案，**用户可撤销**；阶段二实测后按实测分布校准，校准仍由用户裁决确认。
- 判定权威（人工抽检部分）：**用户本人**。流程沿用 C1 先例（[c1-spot-audit-report.md](../M2-DOCTR-QUAL/spot-audit/c1-spot-audit-report.md) §2）：**AI 初判预填 → 用户逐条人工审核 → 正式工作表为唯一判定来源**。证据强度上限=**方向性证据（directional evidence）**——单标注者 + AI 预填锚定未测量，本文档全部真实世界解读按此强度表述，不得在引用时升格为独立双盲结论。
- 范围：产品核心链路 detect→OCR→translate→inpaint→render/export 的分阶段质量口径与阈值。detect 已被 C4/C1 深度验收，本 Task **不重复验收**（§1 只定义 pipeline 冒烟健全性）。

## 0. 通用约定

| 项 | 定义 |
|---|---|
| CER（字符错误率） | `CER = edit_distance(gt, hyp) / max(len(gt), 1)`，region 级逐条计算；edit distance 为 Levenshtein 距离（字符级） |
| 文本归一化 | 计算 CER 前：去除全部空白字符（含全角空格/换行）；统一省略号与长音符（`…`≡`...`、`ー` 不与 `-` 互转）；不区分大小写（拉丁字符）；不做其他语义归一化 |
| region 级 vs 页级 | 主判定一律 **region 级**（一个检出 region 一条 CER）；页级分布仅作附报（中位数/P90/最大值） |
| 汇总统计 | 每语言报告：region 数、CER 中位数、P90、`CER=0` 占比（完全正确率）、`CER≤0.5` 占比；Gate 判定用**中位数**（对单 region 灾难性失败不敏感，避免小样本均值被长尾支配） |
| GT（ground truth）来源 | 分三类，见 §2.2；正式 GT 一律以**用户审核后**的工作表为准（C1 模式） |
| 证据强度 | 全部人工判定=方向性证据；自动指标（CER/哈希）在固定输入下为确定性事实 |
| 目标语言 | translate 评测的目标语言默认 **zh（简体中文）**；此为默认值登记，阶段二启动前用户可改（裁决点 T-4） |

---

## 1. detect（引用冻结口径，不重复验收）

### 口径定义

检测质量以 C4/C1 冻结口径为唯一权威，本 Task 零重复验收：

| 指标（冻结口径） | 冻结值 | 权威出处 |
|---|---|---|
| block_coverage Recall | 882/917 = **0.9618** | C4 报告（`verification/M2-DOCTR-QUAL/qualification/c4-manga-domain-report.md` §5/§7.2） |
| MeanCov | **0.9965** | 同上 |
| severe（漏检大块率） | **0.0** | 同上 |
| Precision（受污染下界） | 882/990 = **0.8909** | 同上；C1 抽检校准=下界方向一致（盲区 FP 25/幻觉 4，n_eff=29） |
| C1 人工校准 | 0 例真实对白漏检（A1/A2 全查域 8/8）；切分粒度与装饰图案误检为已知限制 | [c1-spot-audit-report.md](../M2-DOCTR-QUAL/spot-audit/c1-spot-audit-report.md) §3/§5 |

### 本 Task 的 detect 冒烟健全性（非质量验收）

阶段二 20 case 正式 run 中，detect 只做**健全性门槛**：

| 项 | 提案阈值 | 说明 |
|---|---|---|
| detect step 状态 | `completed` | step_runs 表内无 failed/exception |
| region 产出 | `region_count ≥ 1` | 文字极少的页面（如 BJ01 封面）可能合法产出 0 region——此时记 `data:no-regions-detected` attribution（TA3-A 先例），**不判 FAIL**，但该 case 的 OCR/translate 阶段自动 SKIP 并如实登记 |

### 用户裁决点

- D-1：无（全部引用冻结口径，无新提案数值）。

---

## 2. OCR（本 Task 主判定）

### 2.1 口径定义

- **ja = manga-ocr**（`src/infrastructure/providers/ocr_local.py` `MangaOcrProvider`，`manga-ocr-base`，`needs_detection=False`：只接收 region crop，不自行检出框）。
- **ko = PaddleOCR**（`PaddleKoreanOcrProvider`，`lang="korean"`，`needs_detection=True`：接收 region crop，引擎内部可再切行）。
- 逐 region 对照 CER（§0 定义），GT 来源三分（§2.2）。
- region crop 来源=生产 detect 检出框（阶段二 runner 从 `SqliteRegionRepository` 导出 bbox 后裁剪）——OCR 质量测量**含检测切分的前置影响**，这正是真实产品链路的口径；检测切分本身的质量不在此重复归因（引用 C1 已知限制：模型偏细粒度切分）。

### 2.2 GT 来源设计（三类，按优先级）

| 类 | 适用 case | 来源 | 可信度 |
|---|---|---|---|
| G1 原生文本层 | ja：J46/J47（E20P06/E20P07——P&C 官方声明仅这两页含 partial SVG text layer）；ko：K11-K25 全部（ep04+ep20 语言包） | 官方 lang-pack ZIP 内 SVG text layer。本 Task 侦察实测：ep04/ep20 语言包 zip 内 `.svg` 成员计数各 472（会话内 zip namelist 计数，未入证据物）——**正式计数与逐页文本提取以阶段二第 3 步 G1 提取脚本的落盘清单为准**（R8）。**【阶段二正式计数修正注（r1 R10）】已落盘 `phase2/ocr/svg-gt-manifest.json`：ep20=352、ep04=472——上句「各 472」实为 ko ep04 侧口径，勿再引用**。**ko G1 对齐披露（r2 N1）**：权威目录对 K11-K25 **全部 15 页**记 `svg_text_layer_present_unaligned`（manifest K11/K19 同值）——SVG 文本存在但**无 bbox 对齐**，逐 region GT 需人工对齐（对齐键=bbox 人工指认，§2.4 第 2 条）；Gate 4（ko G1 CER）的 GT 强度=人工对齐后的子集、对齐工作量据此登记，无法自动对齐的部分在阶段二按 `NOT_AUTOMATED` 如实登记 | ja=高（原生，非人工誊录；SVG 文本=排版源文本，与页面渲染字形可能有空格/换行差异——归一化规则（§0）吸收）；ko=中（原生文本但未对齐，GT 强度受人工对齐质量约束，见左列披露） |
| G2 AI 预判 GT（C1 模式） | BJ01-BJ12（无任何文本 GT）、webtoon K01-K10（dataset 仅 cleaned/mask/conf 辅助标注，**无文本转写**）；**并扩展覆盖 G1 四 case（J46/J47/K11/K19）的同 region 双源对照**（R1） | GLM 视觉直读 region crop 预填 `ocr-gt-ai-draft.csv` → 用户逐条审核 → 正式 `ocr-gt.csv` | 中（方向性证据，C1 §2 强度裁定适用） |
| G3 双源交叉 | **G2 预填扩展到 G1 四 case 后**，J46/J47/K11/K19 中同一 region 同时具备 SVG 原生文本与人工誊录两源，逐 region 对照；不一致处人工仲裁，一致率作为人工 GT 流程质量的旁证指标（R1 采纳建议①）。**ko 侧前提（r2 N1）**：K11/K19 的 SVG 侧为 present-but-unaligned，逐 region 配对依赖 §2.4 的人工 bbox 对齐先行完成；对齐未成立（NOT_AUTOMATED）的 region 不进入 G3 交叉，如实登记 | 同 crop 双源（SVG 提取 vs 用户审核誊录） | 最高，量小（预计 <50 region，为无推导估计），全部登记 |

**设计要点**：G2 的 AI 预判**必须**先于用户审核生成并整体存档（`labeling-worksheet-ai-draft.csv` 先例），用户审核记录采纳/修订（`[AI]` / `[人工修订]` rationale 前缀先例）。**禁止**生成未经用户逐条审核的"最终 GT"。

### 2.3 提案阈值（用户可撤销）

| 语言 | 子集 | 提案 Gate | 依据 |
|---|---|---|---|
| ja（manga-ocr） | G1 原生 GT 子集 | region 级 **CER 中位数 ≤ 0.10** | manga-ocr 论文（Kaczmarczyk & Trzciński 2021，arXiv:2107.12922）公开报告 Manga109 测试上字符级准确率 ≈0.95（CER≈0.05）量级；原生 GT 剔除誊录噪声后，取论文量级 2 倍作为生产初版上限 |
| ja | 全量（G1+G2） | region 级 **CER 中位数 ≤ 0.15** | G2 人工 GT 引入誊录主观性（竖排断行/标点取舍），在全量子集上放宽一档 |
| ko（PaddleOCR） | G1 原生 GT 子集 | region 级 **CER 中位数 ≤ 0.20**（注，r2 N1：本行 GT=K11/K19 的 **present-but-unaligned** SVG 文本经人工 bbox 对齐后的子集，非"现成 GT"——对齐质量与覆盖直接进入本 Gate 的不确定度；对齐未成立的 region 按 NOT_AUTOMATED 剔除并登记）。**【阶段二实测同步（r1 R5）】首跑自动子集 n=6、median=0.0556——PASS 判定必须携带：①分母=§5 风险 2 排除规则后的幸存集（13 region 剔 7，排除明细与"若计分 CER"见 `cer-summary.json` excluded[]）；②剔除方向系统性偏低（被剔集含 1 条 CER=1.0 真 OCR 失败），0.0556 为**下偏统计量**；③6 行中 3 行为同一 4 字短串（有效独立文本 4 种）** | **无 manga/webtoon 域公开基准数字**（PP-OCRv5 公开评测为通用印刷场景）——此数值为初版提案而非证据推定，实测后校准 |
| ko | 全量（G1+G2） | region 级 **CER 中位数 ≤ 0.25** | 同上，再放宽一档容纳 webtoon 手写体气泡字 |

**依据链的诚实声明**：ja 两档有论文公开数字作锚（放宽理由=自产 region crop 的切分/竖排/字体分布与论文评测集差异）；ko 两档**没有**可引用的公开基线，数值纯属提案（登记为"初版猜测"），阶段二实测分布出来后由用户裁决是否调整——这正是"阈值由本 Task 提案、用户可撤销"契约的主场景。

**G1 子集外推限制（R2，引用本子集数字时必须携带）**：ja G1 子集仅 J46/J47 两页，文本类型为 `japanese_end_card_and_credits` / `dense_multilingual_credits`（P&C credits/结束卡与多语言版权文本）——**该子集的 CER 结论只对 P&C 风格排版与 credits 类文本成立，不得外推到对白气泡、竖排正文或手写体**；manga-ocr 论文锚（Manga109 对白域）与该子集文本类型不重合，锚定链只约束"引擎量级"而非子集代表性。ko G1（K11/K19=P&C kr 印刷体）对 ko 生产主域（webtoon 手写体气泡字）存在同构缺口，webtoon 域结论依赖 G2 人工 GT 子集（K01-K10）。

### 2.4 测量方法（阶段二执行）

1. 阶段二 runner 逐 case 导出每 region 的 `(case_id, region_id, region_type, bbox, ocr_provider, ocr_text)`；
2. GT 工作表（G1 脚本提取 SVG 文本 + G2 人工审核表）按 region 对齐（对齐键=bbox 人工指认，阶段二工作表含 crop 预览图）；
3. CER 计算脚本（阶段二交付，标准库实现 Levenshtein，不引入新依赖）输出 per-region CSV + 语言级汇总 JSON；
4. **CER 分母口径（R7）**：默认=**全部检出 region**（run_qualification.py 无截断时）；若某 case 启用 region 上限（§quality-thresholds 与 phase2-plan §2.1 的 `--max-regions` 逃生阀），则 Gate 按**明示抽样集**计算且质量报告必须披露 `region_target_count`/`region_runs_executed`/抽样规则，禁止把抽样集数字表述为"全量"；
5. 全部中间产物（crop 预览、ai-draft、正式 GT、CER 明细）入 `verification/M2-TA3-B/phase2/`（gitignore 像素、保留 CSV/JSON）。

### 2.5 人工抽检设计（OCR 补充校准）

| 项 | 设计 |
|---|---|
| n | **30 region**（ja 15 + ko 15），从 20 case 的 OCR 输出中按层抽取 |
| 分层 | 对白气泡（每语言 ≥6）/ SFX 或装饰文字（每语言 ≥2，检出则抽）/ 小字（`tiny_text` tag case，每语言 ≥2）/ 竖排（ja ≥3）/ 复杂背景（`complex_background` tag case，每语言 ≥2）；不足层如实登记 `n<配额` 并在其他层补齐，总 n 不变 |
| 判定 | 用户看 region crop 图 + OCR 输出，逐条判 `correct / partial / wrong`（partial=部分字符错误或断行错误但主体正确） |
| 工作表格式 | CSV，参照 C1：`unit_id,language,case_id,region_id,layer,crop_preview_file,ocr_output,verdict,rationale`（AI 预填 verdict 初稿列 `ai_draft` 一并存档） |
| 与 CER 的关系 | 人工抽检是 CER 的**方向性校准**（C1 模式：CER 由 G2 GT 计算存在锚定风险，抽检用未经预填视角复核）；两者结论冲突时以人工抽检为准登记矛盾 |

### 2.6 用户裁决点

- O-1：ko 阈值数值（≤0.20/≤0.25）为初版提案，实测后确认或调整。
- O-2：G2 审核工作量（预计 20 case × 平均 8-15 region 的 GT 审核一次 + 30 region 抽检一次）是否接受；不接受则缩为"G1 子集 CER + 30 region 抽检"降配方案（届时全量 CER 附报但无 Gate）。
- O-3：**ja/ko 两侧共享的 G1 代表性裁决点（R2 扩写）**。ja 侧：G1 子集仅 2 case（J46/J47=E20P06/E20P07），且文本类型为 credits/结束卡与多语言版权文本（非对白、非竖排正文）——G1 子集结论只对 P&C 风格排版/credits 文本成立，是否接受"该子集仅用于引擎量级校验、对白/竖排结论依赖 G2 人工 GT"；ko 侧同构：G1（K11/K19）为 P&C kr 印刷体，而 ko 生产主域是 webtoon 手写体气泡字——是否接受"ko G1 仅作 native 交叉源、webtoon 域 Gate 由 G2 子集承担"。**ko 附加披露（r2 N1）**：K11/K19 的 SVG GT 为 present-but-unaligned，ko G1 的逐 region 对齐是人工工作量且对齐质量进入 Gate 4 不确定度（§2.2/§2.3 已同步）。两问任一不接受时的替代=扩大 G2 人工 GT 审核量（回到 O-2 工作量）。20 case 选取已把 ja 两个 native GT case 全部纳入（见 [case-selection.json](../../experiments/M2-TA3-B/case-selection.json)）。

---

## 3. translate

### 3.1 口径 A：SFX 拟声词文化对等抽检（SFX-SEM-1 语义落地核对）

| 项 | 定义 |
|---|---|
| 对象 | 阶段二 run 中 `region_type=sfx` 且完成翻译的全部 region（20 case 内 SFX region 集中在 BJ06/BJ10 附近）。**最小样本量（R13）：n ≥ 15 才判 Gate；n < 15 时只登记分布与逐条判定，不判 Gate**（Gate 延后至素材扩充，是否接受此规则见裁决点 T-2） |
| 核对规则（SFX-SEM-1 system prompt 特化的直接落地） | ①文化对等：译文是目标语言自然拟声词/效果词，**不是源语音节转写**；②强度保留：译文表达的声响强度与原文相当；③简洁：译文 ≤6 字符（源更长则可放宽）；④无对等时=最短自然效果词 |
| 评分 3 档 | `cultural_equivalent`（4 项全满足）/ `acceptable`（对等但强度或简洁 1 项偏差）/ `fail`（音节转写、语义错误或 region_type 未按 SFX 语义处理） |
| 提案 Gate | `non-fail 占比 ≥ 70%`（directional 首版；fail 中"音节转写"出现即视为 prompt 特化未落地，单独计数强制登记） |
| 测量 | 评分表 CSV（`sfx_id,case_id,region_id,source_text,translated_text,verdict,fail_mode,rationale`），AI 预填 + 用户终审（C1 模式） |

### 3.2 口径 B：对白可读性人工评分（5 分制）

| 项 | 定义 |
|---|---|
| 对象 | n ≥ **30 region**（20 case 中完成翻译的 `speech`/`narration` region 按语言分层抽：ja 15 + ko 15；分层规则同 §2.5） |
| 维度（每 region 三维各 1-5 分，region 分=三维均值） | **忠实度 faithfulness**：译文语义与原文一致，无增删反转；**流畅度 fluency**：目标语（默认 zh）自然可读，无翻译腔硬伤；**语境适切 register**：符合漫画语境与说话人语气（敬语/语气词/省略处理得当） |
| 锚点定义（**锚点对每个维度独立适用，region 分=三维均值**——R12） | 每维共用一档 5 分制锚：5=专业出版级（该维无可挑剔）；4=少量瑕疵不影响理解；3=可读/可接受但有明显生硬或轻微不准；2=多处错误影响理解；1=不可用（该维失效，如忠实度 1=误译反转、流畅度 1=乱码不可读、语境 1=语气完全错位）。评分时三维独立打分，禁止先算均值再回填 |
| 提案 Gate | region 分**中位数 ≥ 3.5** 且 `region 分 ≥3 占比 ≥ 80%`（均基于三维均值） |
| 测量 | 评分表 CSV（`unit_id,language,case_id,region_id,source_text,translated_text,faithfulness,fluency,register,region_score,rationale`）；AI 预填评分 + 用户终审（C1 模式；锚定效应如实登记） |

### 3.3 口径 C：回译一致性（可选附报，不设 Gate）

- 阶段二如时间允许，对 §3.2 抽中的 region 追加回译（zh→源语言）对照，输出定性一致性附注；**不引入 BLEU/COMET 新依赖、不设数值 Gate**，仅作为 §3.2 忠实度维度的旁证附报。跳过不影响 Gate。

### 3.4 用户裁决点

- T-1：§3.1/§3.2 Gate 数值（70% / 3.5 / 80%）。
- T-2：SFX 最小样本量规则（R13：n≥15 才判 Gate，n<15 只登记分布、Gate 延后至素材扩充）是否接受。
- T-3：目标语言默认 zh 是否正确（见 §0）。
- T-4：translate 评测依赖阶段二启动（用户翻译 endpoint 二选一）——评测样本只能来自真实翻译产出，mock 译文不参与质量判定。

---

## 4. inpaint（SimpleFillProvider）

### 口径定义（如实界定上限）

- 生产默认 inpaint=`SimpleFillProvider`（simple fill route，基础填充）。**本 Task 不做去字质量验收**：SimpleFill 的设计上限=简单背景上可接受的文字区填充，复杂背景/网点/渐变处的填充痕迹是**预期行为**而非缺陷。
- 阶段二只做**定性抽检**：从 20 case 导出页中抽 10 个已填充 region（分层：纯色气泡底 ≥5 / 复杂背景 ≥3 / SFX ≥2），用户看导出图逐个判 `residue_visible: no / slight / yes`（原文字残影可辨=yes；填充痕迹可见但无残影=slight；干净=no）。

### 提案阈值

- **无数值 Gate**（定性登记 100% 记录）。理由：基础填充的质量上限已由 provider 选型决定，数值阈值只能产生"必然 FAIL 的伪发现"或"必然 PASS 的空转 Gate"，两者都无信息量。
- 如实登记义务：质量报告中必须写明"SimpleFill=基础填充，本环节验收的是执行正确性（region 被处理、产物可渲染），不是去字质量"。

### 用户裁决点

- I-1：未来如需真实去字质量验收，须先立 provider 升级 Task（学习型 inpaint），再立质量 Task——本 Task 只登记该路线需求，不承诺。

---

## 5. render/export（TA3-A 确定性框架引用）

| 项 | 提案阈值 | 依据 |
|---|---|---|
| export 状态 | 每 case `export status=OK` | TA3-A runner 既有 fail-closed 口径（`run_smoke.py` export 段） |
| 哈希一致性 | summary 记录的 `sha256` 与产物文件实算一致（复算脚本独立于 runner） | TA3-A AC4 确定性框架（export 哈希双向复算一致先例） |
| 确定性复跑 | **固定 3 case（BJ02/K01/K11，理由：覆盖 ja BJ 印刷漫 / ko webtoon / ko P&C 三家族，非抽样——R15）**同环境重跑，export 哈希逐位一致 **`superseded-pending`（r1 R9/R1）：remote 翻译下"字节逐位"口径待重新定义（候选=按 reading_order 对齐的译文相似度）——见 quality-report §5/F5 裁决点；重定义前本行勿作为执行口径引用** | TA3-A 已验证确定性；阶段二只需防回归。**阶段二实测（r1 R1）：该口径对 Run2 region 链是空转（export 只反映 Run1 渲染产物），且 Run1 内部即存在未隔离的非确定环节（K11 MISMATCH）** |
| 渲染产物 | 每 case 产出 `translated` render 且 reader_catalog 可解析（run2 完成的隐含条件） | 生产 seam |

> **本节 superseded-pending 注（r1 R9）**：§5 与 §7 中 render/export 的"确定性复跑=export 哈希逐位一致"条目在 remote 翻译（DeepSeek）链路下待重新定义（quality-report §5/F5，Codex/用户裁决点）。阈值**数值本身未改**；F4/F5 的口径修订仍在裁决流程中，本文档不做单方改写。

### 用户裁决点

- R-1：无（框架为 TA3-A 已验证引用）。

---

## 6. 全链（整级 Gate）

| 项 | 提案阈值 |
|---|---|
| pipeline_failures | **0**（TA3-A 口径：每 case run2 REGION 全链 completed + export OK；任何 case 失败即全链 Gate FAIL，fail-closed 不豁免） |
| 产物存在性 | 每 case：detect regions 导出存在、OCR 明细存在、translate 明细存在、export PNG 存在（四件齐）。**豁免条款（R11）：`attribution=data:no-regions-detected`（region_count=0）的 case 不适用"OCR/translate 明细存在"，其 SKIP 为协议内结果，不构成全链 Gate FAIL**（§1 口径的一致延伸） |
| 耗时记录 | per-case `wall_s` + per-stage `elapsed_s` 全量登记（不设阈值，供后续性能工作取数） |
| attribution 纪律 | 沿用 TA3-A 三向归因（environment/data/defect）；`defect` 归因条目必须在质量报告逐条列出并给出复现信息 |

---

## 7. 阈值提案总表（用户裁决清单）

| # | 阶段 | 提案 Gate | 性质 | 裁决点 |
|---|---|---|---|---|
| 1 | detect | 冻结口径引用 + region_count≥1 冒烟 | 引用（无新数值） | 无 |
| 2 | OCR ja G1 子集 | CER 中位数 ≤ 0.10 | 论文锚定提案 | O-3 |
| 3 | OCR ja 全量 | CER 中位数 ≤ 0.15 | 论文锚定提案 | O-1 |
| 4 | OCR ko G1 子集 | CER 中位数 ≤ 0.20（GT=K11/K19 present-but-unaligned SVG 经人工对齐后的子集，r2 N1；**实测首跑 n=6/median=0.0556 为下偏统计量，r1 R5，详见 §2.3 ko 行注**） | **初版猜测**（无公开基线） | O-1/O-3 |
| 5 | OCR ko 全量 | CER 中位数 ≤ 0.25 | **初版猜测** | O-1 |
| 6 | OCR 人工抽检 | n=30 分层、correct/partial/wrong 三档 | 方法设计 | O-2 |
| 6b | OCR CER 分母 | 默认=全部检出 region；启用 region 上限时=明示抽样集+报告披露（R7） | 口径定义 | 无 |
| 7 | translate SFX | **n≥15 才判 Gate**；non-fail ≥ 70%（音节转写单独强制登记）；n<15 只登记分布 | directional 首版 | T-1/T-2 |
| 8 | translate 对白 | 中位数 ≥ 3.5 且 ≥3 分占比 ≥ 80%（5 分制三维） | directional 首版 | T-1/T-3/T-4 |
| 9 | inpaint | 无数值 Gate，定性 100% 登记 | 上限如实界定 | I-1 |
| 10 | render/export | OK + 哈希复算 + 3 case 确定性复跑 **`superseded-pending`（r1 R9）：确定性逐位口径待 F5 裁决重定义，见 §5 注** | TA3-A 框架引用 | 无 |
| 11 | 全链 | pipeline_failures=0 + 四件产物存在性 + 耗时登记 | TA3-A 口径 | 无 |

**校准规则**：阶段二实测完成后，任何提案数值的调整（含"实测后 ko 阈值明显不合理的改判"）一律走用户裁决登记，不允许 owner 单方修改已裁决数值。

## 8. 与既有验收的关系

- detect 的 C4/C1 口径与本 Task 的关系是**引用**而非扩展：本 Task 不产生任何 detect 新指标。
- OCR/translate 的 CER 与评分体系是产品首次质量验收（manga-ocr/PaddleOCR 从未做过质量验收；SFX 翻译语义 SFX-SEM-1 只做了 directional 评估与契约冻结）。
- 本文档只定义口径与阈值；测量脚本、GT 工作表与实测数字全部属于阶段二（BLOCKED_ON_USER 翻译 endpoint 二选一，见 [phase2-plan.md](phase2-plan.md)）。
