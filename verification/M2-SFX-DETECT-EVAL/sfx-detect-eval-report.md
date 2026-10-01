# M2-SFX-DETECT-EVAL — SFX 拟声词检测能力评估报告（r2，DSH r1 R1-R14 处置后）

- Task：[M2-SFX-DETECT-EVAL](../../doc/tasks/M2-SFX-DETECT-EVAL.md) · 分支 `agent/zcode/M2-SFX-DETECT-EVAL` · base=`a9b054e8`（delivery base=`02bf68a0`；implement=`d5bfd1fe`、收尾=`d98bab7e`、**本 r2 报告所在返修 commit=delivery tip**，见 Task frontmatter）· 日期 2026-10-01
- Owner=ZCode · Reviewer=DeepSeek Harness（非作者，r1=`changes_requested`，1×P1+6×P2+6×P3/P4，本版逐条处置）· Integrator=代行 Codex
- **证据强度裁定（全程适用）**：本报告全部真实世界解读为**方向性证据（directional evidence）**——单一 AI 标注者（agent 视觉预判，grid 预览锚定）、无正式 SFX GT、样本量 23 帧；凡「检出率」「可行」均为方向性表述，**不构成「确认/达标」级结论**。「SFX 检测可行吗、用哪个方案」的裁决权在用户（本 Task 为评估先行，生产零改动）。
- **r1 修正声明（R1）**：r1 版 §3.2 的 ogkalu 列 18/29 含 11 个自比实例（参照框=ogkalu 自家检出框），已重建为三分 provenance + 非自比子集口径；**非自比公平口径下方向反转：ogkalu 7/18 vs chiqui7 sfx 类 11/29（非自比子集内 8/18）——现状检测器对 SFX 的独立检出能力弱于专用 sfx 类**。r1 的其他数字修正：≥0.3 列 14/7/18（r1 误写 16/9/19）、检出率拆 raw/block 双口径（R5）。
- 生产面零改动：`src/**`、`requirements.txt`、contracts、`apps/**`、`packaging/**` 未触碰；C1/C4 产物零改动（专项 diff 见 §6/Task AC5）。

## 0. 三个问题的结论速览（directional）

| 问题 | 结论（方向性） |
|---|---|
| ①SFX 检测现状（ogkalu 基线） | **不稳定且不可区分**：23 帧主样本上，帧级检出率 **raw 口径 11/23（47.8%）@conf0.5 / block 口径 12/23（52.2%）@conf0.5**（差异=`화——` 仅 C4 block 层框过阈，§2.2 脚注）；@0.25 两口径均 **16/23（69.6%）**；**7 帧连 0.25 都零检出**。与 C1 既有证据方向一致且完全复现。检出后无法区分 SFX（混入 text_free/text_bubble）。 |
| ②有没有可行的 SFX 检测方案 | **有方向性可行信号，且非自比公平口径下现状检测器对 SFX 的独立检出弱于专用 sfx 类（R1 修正后的方向）**：唯一带独立 SFX 类的已核实候选 `chiqui7/yolo11-manga-seg`（MIT 标签）sfx 类 instance 级 overlap≥0.5 **11/29**；ogkalu 去掉 11 个自比实例后仅 **7/18**（§3.2）。对 ogkalu 的 7 个硬盲区帧，sfx 类按「conf≥0.25 且 coverage>0（部分相交）」判据命中 **6/7**（콰직 conf=0.76/cov=0.46、투두 conf=0.95/cov=0.93、철컹 conf=0.82/cov=0.34、빠직 conf=0.95/cov=1.00 等；§3.3）；但类内混淆（하하/철컥철컥/뒤적뒤적 归 text）、误报（手部 conf=0.55）、训练数据未登记、Ultralytics AGPL 权重许可争议四项缺口真实存在。`Kiuyha/Manga-Bubble-YOLO` **NO-GO**（类别面单类无 SFX + 许可冲突）。 |
| ③怎么接进产品 | 策略门已就绪（`RegionType.SFX` + `SfxPolicy` + `decide_sfx_translation`），**缺口只在检测/分类**。三条路径（A 独立 SFX 检测器 / B 现有检测器+后分类 / C 用户手动标记）+ 七项集成前条件（§4.4）。任何集成须凭本报告另行释放 Task。 |

## 1. 候选调研登记（AC1，2026-10-01；许可一手证据=`license-evidence.md`）

许可核查的一手证据（HF API 原始 JSON 快照 sha256、Manga109-s 条款摘录、抓取时间 2026-10-01T03:09:21Z）入库于 [`license-evidence.md`](license-evidence.md)（DSH r1 R4；格式先例=C4 同名文件）；下表「许可」列均可溯源到该文件的 API 实证。

| 候选（URL） | 许可（一手证据） | 类别面 | 训练域/数据 | 权重形态 | 契约适配度 | 结论 |
|---|---|---|---|---|---|---|
| [ogkalu/comic-text-and-bubble-detector](https://huggingface.co/ogkalu/comic-text-and-bubble-detector)（现役） | Apache-2.0（C4 license-evidence 先例已核 API 快照） | 0=bubble/1=text_bubble/2=text_free，**无 SFX 类** | ~11k manga/webtoon/manhua/western | safetensors RT-DETR-v2 | 现役已接入 | **现状基线**（AC2） |
| [Kiuyha/Manga-Bubble-YOLO](https://huggingface.co/Kiuyha/Manga-Bubble-YOLO) | HF 标签 apache-2.0（API 实证 `license-evidence.md` §1）；**ONNX 元数据 license=「AGPL-3.0 License (ultralytics.com/license)」冲突** | ONNX 元数据 `names={0:'text'}`——**单类，无 SFX 类**（模型卡仅报 Text/bubble） | Manga109-s ~3k + Mangadex EN/VI ~3k（共 5,595 图，数据集未公开） | ONNX (1,300,6) end2end / PT | 需 Ultralytics 运行时生态 | **NO-GO 登记**：①类别面不满足「检出后标记 SFX」前提；②Ultralytics AGPL 权重许可主张与 HF 标签冲突（同 T1.1.1 CTD 谨慎口径）。仅作 text 类参考评测（§3.2） |
| [chiqui7/yolo11-manga-seg](https://huggingface.co/chiqui7/yolo11-manga-seg) | HF 标签 MIT（API 实证 §2）；**ONNX 元数据 license=AGPL-3.0（同上冲突）** | `names={0:'bubble',1:'panel',2:'sfx',3:'text'}`——**唯一核实存在独立 sfx 类** | **未登记**（卡片无数据来源/数量——风险项） | ONNX seg（1024px rect） | 检测输出可映射 region_type | **EVAL**（AC3 主评候选） |
| [cozy-creator/manga-sfx-detector](https://huggingface.co/cozy-creator/manga-sfx-detector) | **无许可声明**（API 实证 §3：tags 无 `license:` 项、`cardData.license=null`） | 未列类（自称 SFX 专用 YOLOv8） | 未登记；配套数据集 cozy-creator/YOLO-manga-sfx（详情未核） | PT（需 ultralytics） | 无来源链 | **NO-GO 登记**：无许可+零下载+零指标+零信息，不满足「真实来源+许可链」产品标准（同 T1.1.1 口径）；未评估 |
| [dmMaze/comic-text-detector](https://github.com/dmMaze/comic-text-detector)（含 mayocream HF 镜像） | **GPL-3.0**（GitHub LICENSE + HF 镜像双证） | — | — | — | — | **NO-GO**（沿用先例，不评估）：T1.1.1 裁定「上游 LICENSE GPL-3.0；指向的 comictextdetector.pt.onnx 权重无独立 license statement；当前产品分发策略不接受这条许可证/权重来源链」（`doc/tasks/T1.1.1.md` §Verdict L45-48，一手来源链接 L55-57） |

**许可门核心发现（Ultralytics 权重许可争议）**：两个 Ultralytics 训练的候选（Kiuyha/chiqui7）的 ONNX 元数据均携带 `license: "AGPL-3.0 License (https://ultralytics.com/license)"`，而其 HF 仓库标签分别为 apache-2.0 / MIT。Ultralytics 对「用其软件训练的权重」主张 AGPL-3.0（其官方 licensing 立场），模型作者的单方 Apache/MIT 重贴标签在法律上存疑。**本 Task 只做内部分发无关的评估（合法）**；任何权重随产品分发的集成行为（m2ac5 打包）在此争议解决前构成许可风险，与 T1.1.1 对 GPL 链的谨慎口径同向。此裁决（接受争议风险 / 购买 Ultralytics 企业许可 / 改用非 Ultralytics 训练的模型）= **用户裁决项**，本报告不代替裁决。

**Manga109-s 数据集许可传导（释放侦察第 2 项的关闭）**：hal-utokyo/Manga109-s 为自定义许可（"License: manga109-s"）+ gated 申请制（API 实证 `gated:auto`）；条款允许「将 ML/图像处理实验的结果（含预训练模型）用于商用」，义务=显著标注数据集来源与作者署名；禁止数据集本体再分发、禁止把数据集图像随结果出售（条款摘录见 `license-evidence.md` §4）。→ **传导结论：可满足（署名条件）**，释放时担心的「禁商用传导」不成立；对 Kiuyha 候选而言真正的否决项是类别面（无 SFX 类）与 Ultralytics AGPL 争议，而非 Manga109-s（「作者是否已履行署名义务不可证」登记为集成前尽调项）。

## 2. Q1 现状基线：ogkalu 的 SFX 检出抽检（AC2）

### 2.1 样本方法（登记）

- 候选池 44 单元（`experiments/M2-SFX-DETECT/sfx-sample-candidates.json`，种子 20261001）：**A 层** 11 帧=C1 用户已审定的 SFX 帧（6 检出盲区 FP + 5 零检出，框来自 `spot-audit-sample.json` 审定证据）；**B 层** 19 单元=C1 未抽检的 block 层 FP 框按 case 配额随机（ogkalu 检出落在未标注真实文字上的位置——SFX 高发区）；**C 层** 14 区域=C1 未抽检的零检出区域按 case 配额随机。
- 视觉确认：agent 逐帧读 grid 预览（100px 网格锚定），确认含拟声词 SFX 的帧进入主样本；非 SFX 单元带理由跳过（旁白/海报/对白/手写注/章节标题/幻觉/无文字等）。**主样本 23 帧、29 个 SFX 实例**（`sfx-spot-check-verdicts.json`，逐帧依据中 conf/cls 数字由脚本从 payload 自动取值生成，R6；44 单元全量留档）。候选单元处置：**19 个 skipped（非 SFX/幻觉/无文字）+ 2 个 supplementary（不入主样本的补充观察）**。
- 推理：ogkalu 生产同一权重（sha256 `037930a8…`，与 C4 冻结一致）+ 同一推理路径（import C4 基座 `detect_text_boxes`），harvest 阈值 0.25（0.5=主口径，0.25-0.5=敏感性证据）。

### 2.2 主样本判定汇总（directional）

| 判定（帧级） | n | 帧 |
|---|---|---|
| 检出且框住（conf≥0.5 框覆盖 SFX） | 10 | 저벅저벅 0.80 / 푸흡 0.85 / 하하 0.57 / 싸—아 0.5475 / 뒤적뒤적 0.93 / 화—— 0.46* / 쭈아앙~ 0.75 / 철컥철컥 0.73 / 뒤적뒤적₂ 0.69 / 끼아아악 0.80 |
| 检出但偏移（conf≥0.5 只盖部分） | 2 | 덜컹（덜 0.62 检出、컹 零检出）/ 뙇环（0.2651 低框只盖左弧） |
| 检出但低置信（仅 0.25-0.5 带） | 4 | 끌끌.. 0.33 / 빠걸×3 0.34-0.48 / Rrrrr 0.30 / 수악 0.28 |
| 未检出（0.25 仍零） | 7 | 빠악 / 콰직 / 투두 / 칼칼×2 / 철컹 / 빠직+아 / 송송+삐직삐직 |

\* 화—— 的 ogkalu raw 框 conf=0.4625（harvest 0.25 带）；帧级判「检出」依据 C4 正式运行的 block 层 FP 框（conf 0.772，`frames-export.json` B 层证据）——同一 SFX 在 raw/block 两粒度的 conf 差异本身就是粒度不稳定证据，见 `sfx-spot-check-verdicts.json` 逐帧依据（conf/cls 由脚本取值）。

- **帧级 SFX 检出率（directional，R5 双口径）**：**raw 口径 conf≥0.5 = 11/23（47.8%）**；**block 口径（C4 正式运行，`화——` 仅 block 层框过阈）= 12/23（52.2%）**；**@0.25 两口径均 16/23（69.6%）**；硬盲区（0.25 零检出）7/23=30.4%。headline 不再混用两层 conf；同帧 raw/block 差异本身登记为粒度不稳定证据。
- **帧内额外观察 10 条**（`extras`，不计入主判定；10 条**内含** 1 处拳头幻觉框 conf=0.40）：ogkalu 在已检出 SFX 的帧里仍漏掉同帧其他 SFX（걸들左、빠─、ㅋㅋㅋ、꼬르륵、꺘약、?! 等；`컹` 的零检出记录在 덜컹 主实例依据中而非 extras）——「不稳定」在帧内粒度同样成立。
- **阈值边缘不稳定（运行级证据）**：싸—아 0.5475、빠걸 0.4812、Rrrrr 0.2952-0.45、수악 0.2775-0.32 全部贴着 0.5 主阈分布——C1 的「6 检出 FP + 4 零检出」切分本质是阈值切分，不是能力切分。
- **检出≠可区分**：ogkalu 把 끼아아악 标为 text_bubble、뒤적뒤적 标为 text_bubb（类间混淆），SFX 检出后无任何元数据可路由到 `region_type=sfx`。

### 2.3 与 C1/C4 既有证据的一致性

A 层 11 帧（C1 用户审定）**全部复现 C1 结论**：6 个检出盲区 FP 的检出框坐标与 C1 审定框重合（저벅저벅/푸흡/하하/싸—아/덜컹/뒤적뒤적）；4 个 **D 层**零检出帧在 conf≥0.5 下仍为零检出（빠걸×3 在 0.25 带出现低置信框——把 C1 的「零检出」精确化为「阈值下零检出」）；**A1 层**의 A1-U06（끌끌.. 伪 GT 框，非 D 层）同样一致（0.25 带低置信框 conf=0.3279）。两次运行权重 hash 相同（`037930a8…`），无权重漂移。本抽检对 C1 证据是**扩充而非修正**：新增 B/C 层 12 个 SFX 帧（C1 抽检未覆盖），方向与 C1 判定的「盲区集中在 SFX 类」一致。

## 3. Q2 候选域评测（AC3）

### 3.1 权重与推理（登记）

| 模型 | 权重 | sha256（pin） | 推理 |
|---|---|---|---|
| chiqui7/yolo11s-seg | `task-envs/M2-SFX-DETECT/weights/yolo11s-seg.onnx`（HF revision `7f5f5c04`，41.2MB） | `d87389af4350954143a216bcfe40fd2ad93312cb136534e6073c9c740d98b646` | onnxruntime 1.30.0 CPU，letterbox 1024，无 ultralytics 包；导出分数为 post-sigmoid（实证核对：raw 0-0.956），NMS IoU 0.7 |
| Kiuyha yolo26n | `task-envs/M2-SFX-DETECT/weights/yolo26n.onnx`（HF revision `fb64650`，6.1MB） | `b45c2e12cf0c3c1d2abfbbb9123c9f96f040f2ac36a0842382ecd9d859c851c7` | 同上，letterbox 1280，end2end (1,300,6) |

权重在 gitignored task-env 树，不入库（AC5 核实；完整外部证据清单+sha256 见 `external-evidence-inventory.json`，R11）。**预处理与 Ultralytics 预训练管线的偏离（R8 披露）**：letterbox 左上贴图（Ultralytics 居中）、PIL BILINEAR（cv2 INTER_LINEAR）、NMS class-agnostic IoU 0.7（Ultralytics 默认 class-aware）；坐标映射自身自洽（左上贴图 ↔ 除以 scale 回映，DSH r1 目视抽验复核）；每区域 `onnx_metadata_imgsz` 与实际 `input_shape` 已记入 payload。环境变更披露：C4 GPU venv 内新装 `onnxruntime`（CPU provider）。

### 3.2 对照结果（23 帧 / 29 实例；R1 口径重建）

参照框（SFX 位置）三分 provenance（字段 `reference_box_provenance`，逐实例入库）：
- **ogkalu_self_prior（11 个）**：参照坐标=ogkalu 自家检出框（6 个 C1 审定盲区 FP 单元的审定框即 C4 运行检出框 + 5 个 B 层 FP prior）——**ogkalu 在这些实例上的 coverage 是自比，仅作参考并标注 self-referential，不入公平比较**；
- **c1_adjudicated（1 个）**：C1 审定但非 ogkalu 检出坐标（A1-U06 伪 GT 框）；
- **agent_estimated（17 个）**：agent 视觉估计（grid 锚定）。

| 口径 | ogkalu（text 类任一） | chiqui7 **sfx 类** | Kiuyha text 类 |
|---|---|---|---|
| 全量 29 实例 overlap≥0.5 | 18/29（**含 11 自比，self-referential 仅参考**） | **11/29** | 7/29 |
| 全量 29 实例 overlap≥0.3 | 18/29（self-referential） | 14/29 | 7/29 |
| **非自比子集 18 实例 overlap≥0.5（公平口径）** | **7/18** | **11/29 全量；非自比子集内 8/18** | 2/18 |
| 非自比子集 overlap≥0.3 | 7/18 | 11/18 | 2/18 |
| conf≥0.5 且 overlap≥0.5 | raw 口径 11/23 帧（§2.2） | 7/29 实例 / 5/23 帧 | — |

**公平口径结论（directional，方向较 r1 反转）**：去掉自比后，**ogkalu 对 SFX 的独立检出（7/18）弱于 chiqui7 的专用 sfx 类（子集内 8/18；全量 11/29）**——r1 版「ogkalu 18/29」的表观优势全部来自「检出框既当裁判又当选手」。

**几何口径声明（R12）**：coverage=intersection/SFX 面积是**单侧口径**（recall-like），不约束框精度——大框可平凡「覆盖」（`chiqui7_any_class` 列常被 panel 类页面级大框支配 coverage=1.0，**该列不用于任何结论**）；instance 级 `iou` 字段已补入对照 JSON 供精度侧检验。「保守下界」的说法只对「字母级碎框使 coverage 被低估」这一方向成立，反向（大框虚高）无约束——故 chiqui7 sfx 类的 11/29 同样可能含松框成分，视觉核对（23 张 ONNX 预览逐帧读）是必要的校准：实测 sfx 类框多数紧贴字面（투두 cov=0.93/IoU≈0.87 级），但环形排布 SFX 按字母分别成框会低估整体 coverage（例：뙇环多字母框 conf=0.31-0.93，整体 cov 只计 0.32）。

### 3.3 视觉核对要点（agent directional 判读；数字标注 conf=/cov=，R3）

判据显式化：**「硬盲区命中」= conf≥0.25 且 coverage>0（部分相交）**——不使用「覆盖/真命中」表述（coverage≥0.5 的严格口径下硬盲区命中为 4/7：빠악 cov=0.663、투두 cov=0.926、빠직 cov=1.00、송송 cov=0.506+삐직 cov=0.582；콰직 cov=0.461、철컹 cov=0.339 低于门槛、칼칼 cov=0.0）。

- **chiqui7 sfx 类对 ogkalu 硬盲区的部分相交（6/7 帧，按上述判据）**：투두 conf=0.95/cov=0.93（ogkalu 零检出）、콰직 conf=0.76/cov=0.46（零检出）、철컹 conf=0.82/cov=0.34（零检出）、빠직 conf=0.95/cov=1.00 + 아 conf=0.96/cov=0.56（零检出）、송송 conf=0.68/cov=0.51 + 삐직삐직 conf=0.78/cov=0.58（零检出）、빠악 conf=0.30/cov=0.66（零检出，部分相交）；唯一无 sfx 类相交的硬盲区帧=K01_R069 粉色 칼칼（conf/cov 均 0）。小字 빠걸×3 属低置信档而非硬盲区——ogkalu 0.25 带检出 conf=0.34-0.48，chiqui7/Kiuyha 对其全零。
- **chiqui7 sfx 类的其他命中（非硬盲区帧）**：끌끌.. conf=0.88/cov=0.77（ogkalu 仅 conf=0.33）、꼬르륵 conf=0.97（extras，ogkalu 零检出）、빠─ conf=0.31（extras，零检出）、걸들右 conf=0.87（extras）、싸—아 conf=0.39/cov=0.65、뒤적뒤적(K07_R123) conf=0.93/cov=0.76、뙇环多字母 conf=0.31-0.93、수악 conf=0.32/cov=0.90、끼아아악 conf=0.27/cov=0.89。
- **chiqui7 的类内混淆（sfx 类漏、text/bubble/panel 类捡走）**：하하→text conf=0.94、철컥철컥→text conf=0.95、뒤적뒤적(K07_R121)→text conf=0.92、쭈아앙~→text conf=0.94、화——→text conf=0.94、저벅저벅→text conf=0.81、푸흡→text conf=0.94（同帧另有 bubble 类框）、덜컹→text。**即 chiqui7 单独使用也会把这些 SFX 当普通文本放行**——「检出后路由到 sfx 类型」在它身上同样不完整。同一拟声词在不同版式下类判定不稳定：뒤적뒤적 在 K07_R123（两行斜排）判 sfx conf=0.93、在 K07_R121（竖排大字）判 text conf=0.92。
- **chiqui7 sfx 类误报**：K09_R071 手部 sfx 框 conf=0.55（明确误报）；?! 特效符号被判 sfx conf=0.70（归类视产品定义而定）。
- **Kiuyha（单 text 类）**：对 SFX 像素的检出明显弱于 ogkalu（7/29 vs 全量 18/29；有命中的 SFX：하하 conf=0.73/cov=0.73、끌끌 conf=0.39/cov=0.84、쭈아앙 conf=0.88/cov=0.55、철컥철컥 conf=0.90/cov=0.74、뒤적뒤적 conf=0.59/cov=0.71、Rrrrr conf=0.54/cov=0.71、끼아아악 conf=0.74/cov=0.93；투두/콰직/철컹/덜컹/싸—아/빠악/빠걸×3/푸흡/칼칼/뙇环/수악/빠직/송송/삐직삐직 零命中）——其「end2end 1280」管线对风格化 SFX 的召回不足，且**无类别面可言**。NO-GO 结论域评测佐证。
- **共同盲区（≥0.25 口径三模型全零）**：칼칼（K01_R069 粉色圆体）——唯一三模型共同盲区；빠걸×3 对 chiqui7/Kiuyha 全零（ogkalu 低置信带检出）。提示任何单一模型的 SFX 召回都有残余盲区，集成设计需保留人工兜底（路径 C）。

### 3.4 方案对照结论（directional）

1. 「SFX 检测」在 KO webtoon 域**存在有真实信号的方案**：chiqui7 的 sfx 类证明了独立 SFX 检测类在该域可训练、可在非自比公平口径下优于现状检测器对 SFX 的独立检出（7/18 vs 8/18 子集内；全量 11/29 vs 7/18，§3.2）。
2. 但**没有任何候选可直接接入**：chiqui7 有四项缺口（AGPL 权重许可争议 / 训练数据未登记 / 类内混淆 / 单标注者级验证）；Kiuyha 类别面不成立；cozy 无许可链；CTD 有 GPL 先例。
3. ogkalu 现状（对 SFX 独立检出 7/18、检出但不区分、阈值不稳定）+ chiqui7 类候选（互补盲区但混淆）共同指向：**单一模型无法同时满足「检出」与「区分为 SFX」**，产品集成必须设计为「检测 + 分类/路由」两层（§4）。

## 4. Q3 集成路径草案（AC4；只读核实 src/，零改动）

### 4.1 产品面现状（已核实，只读）

- `RegionType` 枚举含 `SFX = "sfx"`（`src/domain/regions/entities.py` L20-28，D03 §6.2）。
- `SfxPolicy`：`skip`（Task 默认）/`translate`/`manual`（`entities.py` L48-53；`src/domain/tasks/models.py` L186 `sfx_policy: str = SfxPolicy.SKIP.value`）。
- 策略门 `decide_sfx_translation(region_type, sfx_policy)`（`src/application/translation/context/gate.py` L32-42）：非 sfx → 翻译；sfx+translate → 翻译；sfx+skip/manual → SKIP（附 SFX_SKIP_REASON）。渲染服务（`application/rendering/service.py` L553）与任务服务均走同一实现。
- **缺口确认：策略门就绪，缺口在「把检出的 region 标记为 `region_type=sfx`」的检测/分类层**（与释放侦察事实一致）。

### 4.2 路径草案

- **路径 A（独立 SFX 检测器）**：在文本检测之外并跑 SFX 专用模型（chiqui7 类候选形态）→ SFX 框与文本框合并去重（优先级：sfx 类框决定 region_type）→ region 标记 sfx → SfxPolicy 门生效。优点：盲区互补（§3.3）+ 非自比口径下独立检出优于现状；缺点：双模型推理成本 + 分发体积 + 许可/域风险全在新增模型侧（量化见 §4.4 条件 6）。
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
6. **性能与分发体积评估（R13）**：路径 A 双跑成本未测——chiqui7 权重 +41.2MB（现役 manga 权重包 171MB 基础上的显著增量）、1024px 第二次推理延迟、NSIS 包体影响；须在集成 Task 内实测（CPU/GPU 双档）。
7. **SFX 阈值与口径冻结（R13）**：所有模型分数贴阈分布（0.27-0.97），集成前必须冻结 SFX 判定阈值、raw/block 口径与人工兜底触发规则（如 conf<high-confidence 区间的低置信 sfx 类框是否进入人工确认队列）。

## 5. Known limitations（如实列出，引用本报告时不得省略）

1. **directional 口径**：单 AI 标注者（agent）、无第二标注者、锚定效应未测量；SFX 框为视觉估计（grid 锚定，非标注工具输出）。
2. **n=23 帧 / 29 实例**，全部来自 KO webtoon 10 case 的既有评测切片；日漫/扫图/其他平台 webtoon 未覆盖，不外推。
3. **样本构成偏斜**：A 层 11 帧来自 C1 的 SFX 富集证据（过代表性），B/C 层为盲区导向采样——本设计的检出率**不是**全页随机口径的 SFX 检出率（后者需正式 GT）。
4. **chiqui7 训练数据未登记**：域适配结论只对「本样本」成立，无法从模型卡预判泛化。
5. **conf 分布宽且阈值敏感**：所有模型的 SFX 分数都贴着常用阈值分布（0.27-0.97 跨度），单点阈值比较（0.5 vs 0.25）结论差异大；本报告同时给出两档。
6. **coverage 单侧口径（R12）**：几何对照只约束 recall 方向，不约束框精度（大框平凡覆盖）；`chiqui7_any_class` 列被 panel 类页面级大框支配、不用于结论；IoU 已补记入对照 JSON 供精度侧检验，但本报告结论仍以 coverage+视觉核对联合为准。
7. **预处理偏离 Ultralytics 预训练管线（R8）**：letterbox 左上贴图（非居中）、PIL BILINEAR（非 cv2 INTER_LINEAR）、NMS class-agnostic（非 class-aware）——对 conf 的绝对值有未量化影响（坐标映射自洽已由 DSH 目视抽验与 payload 复算支持）；conf 应视为本管线下的相对证据。
8. **onnxruntime CPU 推理**与潜在生产 GPU 路径的数值差异未测；Kiuyha end2end 导出的动态尺寸行为未做穷举。
9. **ogkalu 运行级波动**：与本抽检同权重的 C4 冻结结果在单帧上存在阈值边缘差异（싸—아 0.5475 恰好过线），跨硬件/版本的复现性未测。

## 6. 证据物与复现

| 证据物 | 位置 | 说明 |
|---|---|---|
| 评估报告 | `verification/M2-SFX-DETECT-EVAL/sfx-detect-eval-report.md` | 本文件（r2） |
| **许可证据快照（R4）** | `verification/M2-SFX-DETECT-EVAL/license-evidence.md` | HF API 三候选快照 sha256 + Manga109-s 条款摘录 + 抓取时间 2026-10-01T03:09:21Z |
| **外部证据清单（R11）** | `verification/M2-SFX-DETECT-EVAL/external-evidence-inventory.json` | gitignored 外部树 86 文件 sha256（previews 66 张 / 权重 11 个 / manifest 2 / 许可原始快照 6 / venv 解释器 1）；**previews 缺失则逐帧判定不可独立复核**（脚本=`experiments/M2-SFX-DETECT/inventory_external_evidence.py` 可重生成） |
| 候选清单 | `experiments/M2-SFX-DETECT/sfx-sample-candidates.json` | 44 单元，种子 20261001，A/B/C 分层 |
| ogkalu 采样推理 | `experiments/M2-SFX-DETECT/ogkalu-sfx-frames.json` | 43 区域全部完成推理（其中 11 区域 harvest 0.25 仍零检出，R10），权重 sha pin |
| 视觉判定 | `experiments/M2-SFX-DETECT/sfx-spot-check-verdicts.json` | 23 主帧逐帧判定+依据（conf/cls 由脚本取值，R6）+29 实例框；44 单元全量留档；provenance 三分 |
| ONNX 推理 | `experiments/M2-SFX-DETECT/onnx-sfx-frames.json` | chiqui7/Kiuyha 23 帧；names 断言 + `onnx_metadata_imgsz`/`input_shape` 已记录（R8）；许可门发现随载荷登记 |
| 跨模型对照 | `experiments/M2-SFX-DETECT/onnx-sfx-comparison.json`（schema@2） | 29 实例几何对照：`reference_box_provenance` 三分 + **NON_SELF_subset**（R1）+ instance 级 iou（R12）+ ≥0.3 列（R2 修正 14/7/18） |
| 脚本 ×7 | `experiments/M2-SFX-DETECT/` | build_sfx_sample / eval_sfx_ogkalu / summarize_sfx_verdicts / eval_sfx_mangabubble / summarize_onnx_comparison / inventory_external_evidence（+C4 基座 import 复用零改动） |
| 预览（不入库） | `task-envs/M2-SFX-DETECT/previews*/` | grid 锚定，ogkalu 43 张 + onnx 23 张（sha256 见 inventory） |
| 释放证据 | `verification/M2-SFX-DETECT-EVAL/release-a9b054e8.md` | 零改动 |
| DSH r1 review | 外部路径 `task-envs/M2-SFX-DETECT-EVAL/dsh-review-r1.md` | changes_requested；R1-R14 本版逐条处置 |

复现（worktree 根目录；R5 口径提示——§2.2 帧级判定表内嵌于 `summarize_sfx_verdicts.py`，视觉判定行与 payload 取值行均可逐条核对）：

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

# AC2 判定汇总（视觉判定行+payload 取值行；provenance/verdicts 同源）
python experiments/M2-SFX-DETECT/summarize_sfx_verdicts.py \
  --candidates experiments/M2-SFX-DETECT/sfx-sample-candidates.json \
  --detections experiments/M2-SFX-DETECT/ogkalu-sfx-frames.json \
  --out experiments/M2-SFX-DETECT/sfx-spot-check-verdicts.json

# AC3 ONNX 对照（names 断言 + metadata 记录）
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

# R11 外部证据清单（可重生成）
python experiments/M2-SFX-DETECT/inventory_external_evidence.py \
  --worktree-root . --task-env "G:/CODEX/New Manga.task-envs" \
  --out verification/M2-SFX-DETECT-EVAL/external-evidence-inventory.json
```
