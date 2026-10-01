# M2-SFX-DETECT-EVAL — SFX 拟声词检测能力评估报告

- Task：[M2-SFX-DETECT-EVAL](../../doc/tasks/M2-SFX-DETECT-EVAL.md) · 分支 `agent/zcode/M2-SFX-DETECT-EVAL` · base=`a9b054e8`（delivery base=`02bf68a0`）· 日期 2026-10-01
- Owner=ZCode · Reviewer=DeepSeek Harness（非作者）· Integrator=代行 Codex
- **证据强度裁定（全程适用）**：本报告全部真实世界解读为**方向性证据（directional evidence）**——单一 AI 标注者（agent 视觉预判，grid 预览锚定）、无正式 SFX GT、样本量 23 帧；凡「检出率」「可行」均为方向性表述，**不构成「确认/达标」级结论**。「SFX 检测可行吗、用哪个方案」的裁决权在用户（本 Task 为评估先行，生产零改动）。
- 生产面零改动：`src/**`、`requirements.txt`、contracts、`apps/**`、`packaging/**` 本 Task 未触碰（AC5 专项 diff 核实）。

## 0. 三个问题的结论速览（directional）

| 问题 | 结论（方向性） |
|---|---|
| ①SFX 检测现状（ogkalu 基线） | **不稳定且不可区分**：23 帧主样本上，conf≥0.5 口径 SFX 检出率 **12/23（52.2%）**（检出且框住 10 + 检出但偏移 2）；放宽到 harvest 0.25 为 **16/23（69.6%）**；**7 帧连 0.25 都零检出**。与 C1 既有证据方向一致且完全复现。检出后无法区分 SFX（混入 text_free/text_bubble）。 |
| ②有没有可行的 SFX 检测方案 | **有方向性可行信号，但无即取即用的候选**：唯一带独立 SFX 类的已核实候选 `chiqui7/yolo11-manga-seg`（MIT 标签）在 ogkalu 的 7 个零检出帧中 6 帧有 sfx 类真命中（含 콰직 0.76/투두 0.95/철컹 0.82/빠직 0.95 等高分），硬盲区互补显著；但类内混淆（하하/철컥철컥/뒤적뒤적 归 text）、误报（手部 0.55）、训练数据未登记、Ultralytics AGPL 权重许可争议四项缺口真实存在。`Kiuyha/Manga-Bubble-YOLO` **NO-GO**（类别面单类无 SFX + 许可冲突）。 |
| ③怎么接进产品 | 策略门已就绪（`RegionType.SFX` + `SfxPolicy` + `decide_sfx_translation`），**缺口只在检测/分类**。三条路径（A 独立 SFX 检测器 / B 现有检测器+后分类 / C 用户手动标记）+ 五项集成前条件（§4.4）。任何集成须凭本报告另行释放 Task。 |

## 1. 候选调研登记（AC1，2026-10-01）

| 候选 | 许可 | 类别面 | 训练域/数据 | 权重形态 | 契约适配度 | 结论 |
|---|---|---|---|---|---|---|
| ogkalu/comic-text-and-bubble-detector（现役） | Apache-2.0（C4 已核实） | 0=bubble/1=text_bubble/2=text_free，**无 SFX 类** | ~11k manga/webtoon/manhua/western | safetensors RT-DETR-v2 | 现役已接入 | **现状基线**（AC2） |
| Kiuyha/Manga-Bubble-YOLO | HF 标签 apache-2.0；**ONNX 元数据 license=「AGPL-3.0 License (ultralytics.com/license)」冲突** | ONNX 元数据 `names={0:'text'}`——**单类，无 SFX 类**（模型卡仅报 Text/bubble） | Manga109-s ~3k + Mangadex EN/VI ~3k（共 5,595 图，数据集未公开） | ONNX (1,300,6) end2end / PT | 需 Ultralytics 运行时生态 | **NO-GO 登记**：①类别面不满足「检出后标记 SFX」前提；②Ultralytics AGPL 权重许可主张与 HF 标签冲突（同 T1.1.1 CTD 谨慎口径）。仅作 text 类参考评测（§3.3） |
| chiqui7/yolo11-manga-seg | HF 标签 MIT；**ONNX 元数据 license=AGPL-3.0（同上冲突）** | `names={0:'bubble',1:'panel',2:'sfx',3:'text'}`——**唯一核实存在独立 sfx 类** | **未登记**（卡片无数据来源/数量——风险项） | ONNX seg（1024px rect） | 检测输出可映射 region_type | **EVAL**（AC3 主评候选） |
| cozy-creator/manga-sfx-detector | **无 license 声明**（HF 卡无 tag 无条款） | 未列类（自称 SFX 专用 YOLOv8） | 未登记；配套数据集 cozy-creator/YOLO-manga-sfx（详情未核） | PT（需 ultralytics） | 无来源链 | **NO-GO 登记**：无许可+零下载+零指标+零信息，不满足「真实来源+许可链」产品标准（同 T1.1.1 口径）；未评估 |
| dmMaze/comic-text-detector（含 mayocream HF 镜像） | **GPL-3.0**（GitHub LICENSE + HF 镜像双证） | — | — | — | — | **NO-GO**（沿用先例，不评估）：T1.1.1 裁定「上游 LICENSE GPL-3.0；指向的 comictextdetector.pt.onnx 权重无独立 license statement；当前产品分发策略不接受这条许可证/权重来源链」（`doc/tasks/T1.1.1.md` §Verdict L45-48，一手来源链接 L55-57） |

**许可门核心发现（Ultralytics 权重许可争议）**：两个 Ultralytics 训练的候选（Kiuyha/chiqui7）的 ONNX 元数据均携带 `license: "AGPL-3.0 License (https://ultralytics.com/license)"`，而其 HF 仓库标签分别为 apache-2.0 / MIT。Ultralytics 对「用其软件训练的权重」主张 AGPL-3.0（其官方 licensing 立场），模型作者的单方 Apache/MIT 重贴标签在法律上存疑。**本 Task 只做内部分发无关的评估（合法）**；任何权重随产品分发的集成行为（m2ac5 打包）在此争议解决前构成许可风险，与 T1.1.1 对 GPL 链的谨慎口径同向。此裁决（接受争议风险 / 购买 Ultralytics 企业许可 / 改用非 Ultralytics 训练的模型）= **用户裁决项**，本报告不代替裁决。

**Manga109-s 数据集许可传导（释放侦察第 2 项的关闭）**：hal-utokyo/Manga109-s 为自定义许可 + gated 申请制；条款允许「将 ML/图像处理实验的结果（含预训练模型）用于商用」，条件=显著标注数据集来源与致谢；禁止数据集本体再分发、禁止把数据集图像随结果出售。→ **传导结论：可满足（署名条件）**，释放时担心的「禁商用传导」不成立；对 Kiuyha 候选而言真正的否决项是类别面（无 SFX 类）与 Ultralytics AGPL 争议，而非 Manga109-s。

## 2. Q1 现状基线：ogkalu 的 SFX 检出抽检（AC2）

### 2.1 样本方法（登记）

- 候选池 44 单元（`experiments/M2-SFX-DETECT/sfx-sample-candidates.json`，种子 20261001）：**A 层** 11 帧=C1 用户已审定的 SFX 帧（6 检出盲区 FP + 5 零检出，框来自 `spot-audit-sample.json` 审定证据）；**B 层** 19 单元=C1 未抽检的 block 层 FP 框按 case 配额随机（ogkalu 检出落在未标注真实文字上的位置——SFX 高发区）；**C 层** 14 区域=C1 未抽检的零检出区域按 case 配额随机。
- 视觉确认：agent 逐帧读 grid 预览（100px 网格锚定），确认含拟声词 SFX 的帧进入主样本；非 SFX 单元带理由跳过（旁白/海报/对白/手写注/章节标题/幻觉/无文字等）。**主样本 23 帧、29 个 SFX 实例**（`sfx-spot-check-verdicts.json`，含逐帧依据与全部 ogkalu 检出坐标）。21 个候选单元跳过（含 2 个补充观察：K06_R038「!!」特效符号低置信检出 0.30、K09_R112 单字 swoosh 不确定——均不入主样本）。
- 推理：ogkalu 生产同一权重（sha256 `037930a8…`，与 C4 冻结一致）+ 同一推理路径（import C4 基座 `detect_text_boxes`），harvest 阈值 0.25（0.5=主口径，0.25-0.5=敏感性证据）。

### 2.2 主样本判定汇总（directional）

| 判定（帧级） | n | 帧 |
|---|---|---|
| 检出且框住（conf≥0.5 框覆盖 SFX） | 10 | 저벅저벅 0.80 / 푸흡 0.85 / 하하 0.57 / 싸—아 0.5475 / 뒤적뒤적 0.93 / 화—— 0.46* / 쭈아앙~ 0.75 / 철컥철컥 0.73 / 뒤적뒤적₂ 0.69 / 끼아아악 0.80 |
| 检出但偏移（conf≥0.5 只盖部分） | 2 | 덜컹（덜 0.62 检出、컹 零检出）/ 뙇环（0.2651 低框只盖左弧） |
| 检出但低置信（仅 0.25-0.5 带） | 4 | 끌끌.. 0.33 / 빠걸×3 0.34-0.48 / Rrrrr 0.30 / 수악 0.28 |
| 未检出（0.25 仍零） | 7 | 빠악 / 콰직 / 투두 / 칼칼×2 / 철컹 / 빠직+아 / 송송+삐직삐직 |

\* 화—— 的 ogkalu raw 框 conf=0.4625（harvest 0.25 带）；帧级判「检出」依据 C4 正式运行的 block 层 FP 框（conf 0.772，`frames-export.json` B 层证据）——同一 SFX 在 raw/block 两粒度的 conf 差异本身就是粒度不稳定证据，见 `sfx-spot-check-verdicts.json` 逐帧依据。

- **帧级 SFX 检出率（directional）：conf≥0.5 口径 12/23=52.2%；conf≥0.25 口径 16/23=69.6%；硬盲区（0.25 零检出）7/23=30.4%。**
- **帧内额外观察 10 条**（`extras`，不计入主判定）：ogkalu 在已检出 SFX 的帧里仍漏掉同帧其他 SFX（걸들左、빠─、컹、꼬르륵、꺘약、?! 等）+1 处拳头幻觉框（0.40）——「不稳定」在帧内粒度同样成立。
- **阈值边缘不稳定（运行级证据）**：싸—아 0.5475、빠걸 0.4812、Rrrrr 0.2952-0.45、수악 0.2775-0.32 全部贴着 0.5 主阈分布——C1 的「6 检出 FP + 4 零检出」切分本质是阈值切分，不是能力切分。
- **检出≠可区分**：ogkalu 把 끼아아악 标为 text_bubble、뒤적뒤적 标为 text_bubb（类间混淆），SFX 检出后无任何元数据可路由到 `region_type=sfx`。

### 2.3 与 C1/C4 既有证据的一致性

A 层 11 帧（C1 用户审定）**全部复现 C1 结论**：6 个检出盲区 FP 的检出框坐标与 C1 审定框重合（저벅저벅/푸흡/하하/싸—아/덜컹/뒤적뒤적）；4 个 D 层零检出帧在 conf≥0.5 下仍为零检出（其中 빠걸×3、끌끌 在 0.25 带出现低置信框——把 C1 的「零检出」精确化为「阈值下零检出」）；A1-U06（끌끌.. 伪 GT 框）一致。两次运行权重 hash 相同（`037930a8…`），无权重漂移。本抽检对 C1 证据是**扩充而非修正**：新增 B/C 层 12 个 SFX 帧（C1 抽检未覆盖），方向与 C1 判定的「盲区集中在 SFX 类」一致。

## 3. Q2 候选域评测（AC3）

### 3.1 权重与推理（登记）

| 模型 | 权重 | sha256（pin） | 推理 |
|---|---|---|---|
| chiqui7/yolo11s-seg | `task-envs/M2-SFX-DETECT/weights/yolo11s-seg.onnx`（HF revision `7f5f5c04`，41.2MB） | `d87389af4350954143a216bcfe40fd2ad93312cb136534e6073c9c740d98b646` | onnxruntime 1.30.0 CPU，letterbox 1024，无 ultralytics 包；导出分数为 post-sigmoid（实证核对：raw 0-0.956），NMS IoU 0.7 |
| Kiuyha yolo26n | `task-envs/M2-SFX-DETECT/weights/yolo26n.onnx`（HF revision `fb64650`，6.1MB） | `b45c2e12cf0c3c1d2abfbbb9123c9f96f040f2ac36a0842382ecd9d859c851c7` | 同上，letterbox 1280，end2end (1,300,6) |

权重在 gitignore 的 task-env 树，不入库（AC5 核实）。环境变更披露：C4 GPU venv 内新装 `onnxruntime`（CPU provider）。

### 3.2 对照结果（23 帧 / 29 实例，几何口径 = 检出框对 agent SFX 估计框的 coverage；directional）

| 模型/类 | 实例级 overlap≥0.5 | 实例级 overlap≥0.3 | 帧级（≥1 实例 overlap≥0.5） | conf≥0.5 且 overlap≥0.5 |
|---|---|---|---|---|
| ogkalu（text 类任一，现状） | **18/29** | 19/29 | — | 12/23 帧（AC2 主口径） |
| chiqui7 **sfx 类** | **11/29** | 16/29 | **9/23** | 7/29 实例 / **5/23 帧** |
| Kiuyha text 类 | 7/29 | 9/29 | — | — |

几何口径是**保守下界**：sfx 类的多个真命中框只盖 SFX 的一部分（多字母/环形排布 SFX 按字母分别成框），按整体 SFX 框算 coverage 被低估——视觉核对（23 张 ONNX 预览逐帧读）确认的实际覆盖面大于几何数字（例：뙇环 7 个字母级 sfx 框 0.31-0.93，几何只计 0.32）。

### 3.3 视觉核对要点（agent directional 判读，逐帧预览在 `task-envs/M2-SFX-DETECT/previews-onnx/`）

- **chiqui7 sfx 类的真命中（含 ogkalu 硬盲区）**：투두 0.95（ogkalu 零检出）、콰직 0.76（零检出）、철컹 0.82（零检出）、빠직 0.95 + 아 0.96（零检出）、송송 0.68 + 삐직삐직 0.78（零检出）、끌끌.. 0.88（ogkalu 仅 0.33）、꼬르륵 0.97（零检出）、빠악 0.30（零检出，部分）、빠─ 0.31（零检出）、걸들右 0.87、싸—아 0.39、뒤적뒤적 0.93、뙇环多字母、수악 0.32、끼아아악 0.27。**ogkalu 的 7 个硬盲区帧中 6 个被 chiqui7 sfx 类覆盖**（唯一无 sfx 类命中的硬盲区帧：K01_R069 粉色 칼칼；小字 빠걸×3 属低置信档而非硬盲区——ogkalu 0.25 带检出 0.34-0.48，chiqui7/Kiuyha 对其全零）。
- **chiqui7 的类内混淆（sfx 类漏、text/bubble/panel 类捡走）**：하하→text 0.94、철컥철컥→text 0.95、뒤적뒤적(K07_R121)→text 0.92、쭈아앙~→text 0.94、화——→text 0.94、저벅저벅→text 0.81、푸흡→text 0.94（同帧另有 bubble 类框）、덜컹→text。**即 chiqui7 单独使用也会把这些 SFX 当普通文本放行**——「检出后路由到 sfx 类型」在它身上同样不完整。同一拟声词在不同版式下类判定不稳定：뒤적뒤적 在 K07_R123（两行斜排）判 sfx 0.93、在 K07_R121（竖排大字）判 text 0.92。
- **chiqui7 sfx 类误报**：K09_R071 手部 sfx 框 0.55（明确误报）；?! 特效符号被判 sfx（0.70，归类视产品定义而定）。
- **Kiuyha（单 text 类）**：对 SFX 像素的检出明显弱于 ogkalu（7/29 vs 18/29；有命中的 SFX：하하 0.73 / 끌끌 0.39 / 쭈아앙 0.88 / 철컥철컥 0.90 / 뒤적뒤적 0.59 / Rrrrr 0.54 / 끼아아악 0.74；투두/콰직/철컹/덜컹/싸—아/빠악/빠걸×3/푸흡/칼칼/뙇环/수악/빠직/송송/삐직삐직 零命中）——其「end2end 1280」管线对风格化 SFX 的召回不足，且**无类别面可言**。NO-GO 结论域评测佐证。
- **共同盲区（≥0.5 口径）**：빠걸×3（ogkalu 仅在 0.25 带低置信检出 0.34-0.48，chiqui7/Kiuyha 全零）、칼칼（三模型全零，唯一 ≥0.25 口径的共同盲区）、투두/콰직/철컹/빠직/송송（ogkalu 全零但 chiqui7 sfx 类命中）——提示任何单一模型的 SFX 召回都有残余盲区，集成设计需保留人工兜底（路径 C）。

### 3.4 方案对照结论（directional）

1. 「SFX 检测」在 KO webtoon 域**存在有真实信号的方案**：chiqui7 的 sfx 类证明了独立 SFX 检测类在该域可训练、可命中 ogkalu 的硬盲区（方向性）。
2. 但**没有任何候选可直接接入**：chiqui7 有四项缺口（AGPL 权重许可争议 / 训练数据未登记 / 类内混淆 / 单标注者级验证）；Kiuyha 类别面不成立；cozy 无许可链；CTD 有 GPL 先例。
3. ogkalu 现状（检出但不区分 + 阈值不稳定）+ chiqui7 类候选（互补盲区但混淆）共同指向：**单一模型无法同时满足「检出」与「区分为 SFX」**，产品集成必须设计为「检测 + 分类/路由」两层（§4）。

## 4. Q3 集成路径草案（AC4；只读核实 src/，零改动）

### 4.1 产品面现状（已核实，只读）

- `RegionType` 枚举含 `SFX = "sfx"`（`src/domain/regions/entities.py` L20-28，D03 §6.2）。
- `SfxPolicy`：`skip`（Task 默认）/`translate`/`manual`（`entities.py` L48-53；`src/domain/tasks/models.py` L186 `sfx_policy: str = SfxPolicy.SKIP.value`）。
- 策略门 `decide_sfx_translation(region_type, sfx_policy)`（`src/application/translation/context/gate.py` L32-42）：非 sfx → 翻译；sfx+translate → 翻译；sfx+skip/manual → SKIP（附 SFX_SKIP_REASON）。渲染服务（`application/rendering/service.py` L553）与任务服务均走同一实现。
- **缺口确认：策略门就绪，缺口在「把检出的 region 标记为 `region_type=sfx`」的检测/分类层**（与释放侦察事实一致）。

### 4.2 路径草案

- **路径 A（独立 SFX 检测器）**：在文本检测之外并跑 SFX 专用模型（chiqui7 类候选形态）→ SFX 框与文本框合并去重（优先级：sfx 类框决定 region_type）→ region 标记 sfx → SfxPolicy 门生效。优点：盲区互补（§3.3）；缺点：双模型推理成本 + 许可/域风险全在新增模型侧。
- **路径 B（现有检测器 + 后分类器）**：ogkalu 检出（0.25 带 69.6% 帧覆盖）→ 对 text_free/text_bubble 框跑轻量 SFX 分类器（视觉特征/OCR 联合）→ 命中则改标 sfx。优点：复用现役检测与契约；缺点：ogkalu 的 7 个硬盲区帧救不回（漏检即无框可分类），且分类器是新训练资产（需 GT + 训练 Task）。
- **路径 C（用户手动标记）**：零模型改动——用户在工作台把任意 region 标为 sfx 类型，策略门即时生效（UI 属 React/Tauri Task，Qoder 主责）。优点：零许可/零域风险、确定性；缺点：无自动化。**与 A/B 不互斥，是 A/B 的兜底层。**
- 任何路径都需要 ADR 级决策（检测双跑的 IPC/契约扩展属共享契约变更，须 Codex 范围裁决）。

### 4.3 评估数据现状与正式 GT 缺口

本评估的 SFX 框是 agent 视觉估计（grid 锚定，逐帧入库可复核）；KO webtoon 伪 GT 体系（seg05 info.json）无 SFX 标注（C1 裁定：SFX 检测需另立任务，涉及伪 GT 体系重标注）。**正式集成前必须完成 SFX GT 重标注 + 用户逐条审核**（同 C1 阶段二流程），否则任何检出率数字都无法进入 Gate 口径。

### 4.4 集成前条件（全部满足才可释放集成 Task）

1. **正式 SFX GT 重标注 + 用户人工审核**（C1 流程先例；directional 数字不得作为集成 Gate）。
2. **许可裁决（用户）**：Ultralytics AGPL 权重主张 vs HF 标签冲突——接受风险 / 企业许可 / 非 Ultralytics 训练模型（或自训）三选一。
3. **域验证扩展**：本样本 23 帧 directional；正式验证需 ≥ 正式 GT 全集 + 分层口径（帧级/实例级/类内混淆率）。
4. **另行释放 Task**：集成（含契约扩展裁决）与 UI（路径 C 的手动标记入口）分别立项，Owner/Reviewer 按协作协议分配。
5. **类内混淆处理设计**：无论 A/B，需明确 sfx 类与 text 类框的合并去重规则（本文只登记问题，不冻结方案）。

## 5. Known limitations（如实列出，引用本报告时不得省略）

1. **directional 口径**：单 AI 标注者（agent）、无第二标注者、锚定效应未测量；SFX 框为视觉估计（grid 锚定，非标注工具输出）。
2. **n=23 帧 / 29 实例**，全部来自 KO webtoon 10 case 的既有评测切片；日漫/扫图/其他平台 webtoon 未覆盖，不外推。
3. **样本构成偏斜**：A 层 11 帧来自 C1 的 SFX 富集证据（过代表性），B/C 层为盲区导向采样——本设计的检出率**不是**全页随机口径的 SFX 检出率（后者需正式 GT）。
4. **chiqui7 训练数据未登记**：域适配结论只对「本样本」成立，无法从模型卡预判泛化。
5. **conf 分布宽且阈值敏感**：所有模型的 SFX 分数都贴着常用阈值分布（0.27-0.97 跨度），单点阈值比较（0.5 vs 0.25）结论差异大；本报告同时给出两档。
6. **onnxruntime CPU 推理**与潜在生产 GPU 路径的数值差异未测；Kiuyha end2end 导出的动态尺寸行为未做穷举。
7. **ogkalu 运行级波动**：与本抽检同权重的 C4 冻结结果在单帧上存在阈值边缘差异（싸—아 0.5475 恰好过线），跨硬件/版本的复现性未测。

## 6. 证据物与复现

| 证据物 | 位置 | 说明 |
|---|---|---|
| 候选清单 | `experiments/M2-SFX-DETECT/sfx-sample-candidates.json` | 44 单元，种子 20261001，A/B/C 分层 |
| ogkalu 采样推理 | `experiments/M2-SFX-DETECT/ogkalu-sfx-frames.json` | 43 区域全检出（harvest 0.25），权重 sha pin |
| 视觉判定 | `experiments/M2-SFX-DETECT/sfx-spot-check-verdicts.json` | 23 主帧逐帧判定+依据+29 实例框；44 单元全量留档 |
| ONNX 推理 | `experiments/M2-SFX-DETECT/onnx-sfx-frames.json` | chiqui7/Kiuyha 23 帧，许可门发现随载荷登记 |
| 跨模型对照 | `experiments/M2-SFX-DETECT/onnx-sfx-comparison.json` | 29 实例几何对照 |
| 脚本 | `experiments/M2-SFX-DETECT/build_sfx_sample.py` / `eval_sfx_ogkalu.py` / `summarize_sfx_verdicts.py` / `eval_sfx_mangabubble.py` / `summarize_onnx_comparison.py` | 评测基座按 import 复用（零改动） |
| 预览（不入库） | `task-envs/M2-SFX-DETECT/previews*/` | grid 锚定，ogkalu 43 张 + onnx 23 张 |
| 释放证据 | `verification/M2-SFX-DETECT-EVAL/release-a9b054e8.md` | 零改动 |

复现（worktree 根目录）：

```bash
# AC2 采样
python experiments/M2-SFX-DETECT/build_sfx_sample.py \
  --frames-export verification/M2-DOCTR-QUAL/spot-audit/data/frames-export.json \
  --audit-sample verification/M2-DOCTR-QUAL/spot-audit/spot-audit-sample.json \
  --c4-results verification/M2-DOCTR-QUAL/qualification/results-formal-manga_rt_detr_v2-cuda-seg05.json \
  --manifest "G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-work/eval-manifest.full.seg05.json" \
  --out experiments/M2-SFX-DETECT/sfx-sample-candidates.json

# AC2 ogkalu 推理（GPU venv）
"G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4-gpu-py312/Scripts/python.exe" \
  experiments/M2-SFX-DETECT/eval_sfx_ogkalu.py \
  --candidates experiments/M2-SFX-DETECT/sfx-sample-candidates.json \
  --weights-dir "G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4/weights/ogkalu-comic-text-and-bubble-detector" \
  --device cuda --harvest-threshold 0.25 \
  --preview-dir "G:/CODEX/New Manga.task-envs/M2-SFX-DETECT/previews" \
  --out experiments/M2-SFX-DETECT/ogkalu-sfx-frames.json

# AC2 判定汇总（视觉判定表内嵌于脚本，逐条可核）
python experiments/M2-SFX-DETECT/summarize_sfx_verdicts.py \
  --candidates experiments/M2-SFX-DETECT/sfx-sample-candidates.json \
  --detections experiments/M2-SFX-DETECT/ogkalu-sfx-frames.json \
  --out experiments/M2-SFX-DETECT/sfx-spot-check-verdicts.json

# AC3 ONNX 对照
"G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4-gpu-py312/Scripts/python.exe" \
  experiments/M2-SFX-DETECT/eval_sfx_mangabubble.py \
  --verdicts experiments/M2-SFX-DETECT/sfx-spot-check-verdicts.json \
  --chiqui7 "G:/CODEX/New Manga.task-envs/M2-SFX-DETECT/weights/yolo11s-seg.onnx" \
  --kiuyha "G:/CODEX/New Manga.task-envs/M2-SFX-DETECT/weights/yolo26n.onnx" \
  --harvest-threshold 0.25 \
  --preview-dir "G:/CODEX/New Manga.task-envs/M2-SFX-DETECT/previews-onnx" \
  --out experiments/M2-SFX-DETECT/onnx-sfx-frames.json

python experiments/M2-SFX-DETECT/summarize_onnx_comparison.py \
  --verdicts experiments/M2-SFX-DETECT/sfx-spot-check-verdicts.json \
  --onnx experiments/M2-SFX-DETECT/onnx-sfx-frames.json \
  --ogkalu experiments/M2-SFX-DETECT/ogkalu-sfx-frames.json \
  --out experiments/M2-SFX-DETECT/onnx-sfx-comparison.json
```
