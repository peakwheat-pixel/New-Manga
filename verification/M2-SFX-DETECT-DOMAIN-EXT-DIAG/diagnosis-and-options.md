# M2-SFX-DETECT-DOMAIN-EXT-DIAG：BJ 域 SFX 检测缺口诊断与扩展方案评估报告（r2）

- Task：[M2-SFX-DETECT-DOMAIN-EXT-DIAG](../../doc/tasks/M2-SFX-DETECT-DOMAIN-EXT-DIAG.md) · 分支 `agent/zcode/M2-SFX-DETECT-DOMAIN-EXT-DIAG` · base=`497621df`（claim=`303d7e14`，交付主体=`87a8bc34`）· 日期 2026-10-03
- **r2 修订声明**：DSH r1（2026-10-03，Reviewer=DeepSeek Harness 非作者）verdict=`changes_requested`（0×P0，1×P1+4×P2+3×P3+3×P4）——主根因判语、五方案评估、AC3 排序、结构性发现均被确认成立且未越权；本版为纯文字/数字返修（11 条全部闭合，逐条处置见文末 §8「DSH r1 闭合对照」），零实验重跑，`experiments/**` 与 `raw/**` 零触碰。
- Owner=ZCode · Reviewer=DeepSeek Harness（非作者，r1=`changes_requested`，本版逐条处置）· Integrator=编排会话代行 Codex（用户全权授权+自治授权）
- **证据强度裁定（全程适用）**：全部结论为 **directional**——单模型（chiqui7 ONNX pinned）+ 3 盲区页（7 目检 SFX 实例）+ 1 域内对照页（BJ06，8 生产 sfx region）；无 SFX GT、单 AI 标注者目检参照框；方案成本估计为静态分析+既有证据推导，未跑任何训练/集成实验。沿 [M2-SFX-DETECT-EVAL](../M2-SFX-DETECT-EVAL/sfx-detect-eval-report.md) 与 [M2-SFX-E2E-MATERIAL](../M2-SFX-E2E-MATERIAL/sfx-e2e-report.md) 的证据强度口径。
- 生产面零改动：`src/**`、`tests/**`、`doc/contracts/**`、`packaging/**`、`apps/**`、`doc/STATUS.md`、既有 Task 产物（SFX-E2E/KO-RERUN/TILING）零 diff；实验脚本仅 import 生产代码（只读），raw 输出全部落 `raw/`。

## 0. 结论速览

| 项 | 结论 |
|---|---|
| 假设 (a) 域外（chiqui7 训练域不含 BJ 毛笔竖排形态） | **DETERMINED — 成立（主根因）**：L3 最强形态下 7/7 参照框 sfx 类分数仅 0.0000–0.0109（域内对照 BJ06 为 0.72–0.94，相差 2–3 个数量级）；L1 raw pre-NMS 参照框内最高 sfx 分数 BJ13 ref1=0.0855 / ref2=0.0043 / BJ14=0.0001 / BJ15=0.0000 |
| 假设 (b) 类别映射歧义（sfx 被判 text/panel） | **DETERMINED — 分层成立**：「SFX 像素被 text 类高 conf 捡走」成立（BJ13 text 0.744/0.844；L3 crop 中 BJ13 ref2 text 0.735、BJ14 text 0.87–0.90）；「sfx 信号存在但被 argmax 竞争压制（可差异化阈值救）」**不成立**——sfx 分数比同框 text 分数低 1–2 个数量级，非贴阈竞争 |
| 假设 (c) 预处理（分辨率/letterbox）对大型竖排字不利 | **DETERMINED — 不成立**：L2 tile（1.67× 有效分辨率）与 L3 crop（3.5–5.4×）均不恢复 sfx 信号；BJ13-15 参照框在 letterbox 空间（61–86×135–206 px）**大于** BJ06 域内正例（21–84×25–131 px）；chiqui7 letterbox 为等比缩放，无 WEBTOON-DIAG 的各向异性机理（「目标太大」替代假设未单独排除，明示见 §2.5——不影响本判语） |
| 结构性新发现 | 生产 region 创建**无跨 provider 重叠仲裁**（`src/bootstrap/core_assembly.py` `_create_detected_region` 按候选独立建 region，`sfx-` 前缀→SFX、`manga-`→SPEECH）：**任何提升 chiqui7 召回的方案（①②③）都不会自动消除「SFX 误路由 speech→乱译→渲染」损害**——speech region 仍并存走对话链。误路由闭合需另行设计重叠仲裁（DETECT-EVAL §4.4 条件 5 的具体化，共享契约面，须 Codex 范围裁决） |
| AC3 推荐 | ①类敏感阈值：**否决（实验无效）**；④路由：**不推荐独立立项**；②后分类器：**条件性次优**（只救 BJ13/14，BJ15 结构性无载体）；③fine-tune：**自动化覆盖的对症路径但前置条件重（条件式）**；⑤维持现状+产品侧缓解：**短期首选**。完整排序见 §5 |

## 1. 证据基础（输入登记）

| 输入 | 位置 | 本报告使用 |
|---|---|---|
| 误路由损害形态原始记录 | `verification/M2-SFX-E2E-MATERIAL/sfx-e2e-report.md` §3.2 | 7 目检 SFX 实例、0 sfx 命中、BJ13 speech region #1/#3 乱译进渲染、text 框 conf 0.744/0.844 IoU 0.452/0.544 |
| 相交框枚举（conf≥0.25 全类） | `verification/M2-SFX-E2E-MATERIAL/sfx-detect-diagnosis.json` | AC1 起点：0.25 带下 BJ14/15 sfx 类 0 框、归属未定 |
| DETECT-EVAL §4.4 裁决清单 | `verification/M2-SFX-DETECT-EVAL/sfx-detect-eval-report.md` | AC2 评估框架（七项集成前条件）、chiqui7 KO 域表现（sfx 类 11/29、类内混淆、训练数据未登记） |
| KO-RERUN | `verification/M2-TA3-B/ko-rerun-report.md` | KO 域对照：K11 唯一 sfx region OCR 空（素材缺口，与 BJ 检测缺口独立） |
| WEBTOON-DIAG | `verification/M2-DETECT-WEBTOON-DIAG/diagnosis.md` | 预处理假设的机理参照（ogkalu/RT-DETR 各向异性重缩放——chiqui7 等比 letterbox 不适用该结论） |
| 生产 provider（只读） | `src/infrastructure/providers/detection_sfx.py` | 推理序列复放基线：letterbox 1024 metadata_parsed、等比缩放+左上贴图、post-sigmoid、conf filter→全类 NMS IoU 0.7→sfx 类 |
| region 创建语义（只读） | `src/bootstrap/core_assembly.py`（`_create_detected_region`，L1013-1049） | label 前缀分发 region_type、无跨 provider 重叠仲裁 |
| BJ06 生产 sfx region（域内对照） | `verification/M2-SFX-E2E-MATERIAL/bj06-run/summaries/qual-BJ06.json` | 8 个 sfx region bbox（源像素 87×103 至 340×534） |
| BJ13 生产 region | `verification/M2-SFX-E2E-MATERIAL/new-assets-run/summaries/qual-BJ13.json` | 3 speech + 1 sfx（T 恤印花）；speech ffed29e8 (2124,258,370,1013) / de83b0c4 (472,2668,308,1002) 与目检 SFX 位置对位 |
| 权重 | `G:/CODEX/New Manga.task-envs/M2-SFX-DETECT/weights/yolo11s-seg.onnx`（sha256 `d87389af…`，HF rev `7f5f5c04`） | 实验引擎（`SFX_WEIGHTS_DEFAULT`，`experiments/M2-TA3-B/run_qualification.py:92`） |

页面图像位置（gitignored，只读引用）：BJ13/14/15 = `M2-SFX-E2E-MATERIAL-zcode` worktree、BJ06 = `M2-TA2B-OPEN-ASSETS-zcode` worktree（路径已记录于 raw JSON `page` 字段）。

## 2. 实验（AC4 零 src 佐证）

### 2.1 设计

工具：`experiments/M2-SFX-DETECT-DOMAIN-EXT-DIAG/conf_scan_diag.py`（新写，仅 import 生产 `_build_engine/_letterbox/_map_back/_nms`，零 src 改动）。三层证据设计：

| 层 | 形态 | 判定目标 |
|---|---|---|
| L1 整页 conf 扫描 | 生产序列复放（conf filter→全类 NMS IoU 0.7），conf 档 0.01/0.05/0.10/0.15/0.20/0.25/0.30/0.40/0.50，4 页（BJ06 对照+BJ13/14/15），全类 dump+**每框 4 类分数向量**。分档实现注记（DSH r1 P4-1）：每页只做一次 conf≥0.01 的 filter→NMS，各档结果=同一 conf≥0.01 全集 NMS 后按 conf 重筛；与「逐档 filter→NMS」的等价性依赖 `_nms` 贪心按 conf 降序（`src/infrastructure/providers/detection_sfx.py:469-477`，`np.argsort(scores)[::-1]`——高 conf 候选先处理，低 conf 候选不可能抑制高 conf 候选），故 §2.2「0.50 档 8 个 sfx 框=生产 run 的 8 个 sfx region」成立 | 阈值切分 vs 无信号；text/panel 在 SFX 位置的分数形态 |
| L2 60% tile | 每页 4 tile（TL/TR/BL/BR，相邻 40% 重叠），各 letterbox 1024 → 等效整页 ~1.67× 分辨率（=page_h/tile_h=1/0.6），conf 0.01 | 分辨率恢复实验（WEBTOON-DIAG 探针形态；chiqui7 等比 letterbox 下只探分辨率、无各向异性） |
| L3 参照框 crop | 每参照框外扩 20% 裁剪（等效 3.5–5.4× 分辨率，=page_h/crop_h=1/0.282–1/0.185，与 L2 同公式），conf 0.01 | 最强形态下「该形状本身是否被认作 sfx」 |
| 附加 | L1 的 raw pre-NMS 查询：letterbox 空间中心落入参照框的全部候选（conf≥0.01）及 4 类分数 | NMS 前的干净「此处是否存在任何 sfx 信号」探针 |

环境：`G:/CODEX/New Manga.task-envs/M2-TA3-B-ocr/Scripts/python.exe`（onnxruntime 1.30.0 CPU，与生产 lightweight 栈一致）；weights sha256 校验由 `_build_engine` 强制（pinned 值匹配后加载）。

### 2.2 L1 结果（整页 conf 扫描）

**BJ06（域内对照）**——chiqui7 对 BJ06 的 sfx 信号强且稳定：

| conf 档 | sfx 框数 | 备注 |
|---|---|---|
| 0.50 | 8 | =生产 run 的 8 个 sfx region |
| 0.05–0.40 | 8 | 无阈值切分迹象 |
| 0.01 | 9 | +1 个 conf 0.0114 弱框（wh 122×164，不在生产 region 内） |

生产 8 框 conf **0.721–0.9355**，分数向量干净（sfx 0.72–0.94，text ≤0.0051）。

**BJ13/14/15（盲区页）**——sfx 类对目检 SFX 位置无信号，且不是阈值问题：

| 页 | conf≥0.01 全类框 | 参照框处 sfx 信号（raw pre-NMS 最高） | 参照框处 NMS 后紧贴混淆框 |
|---|---|---|---|
| BJ13 | 9（sfx 1=T 恤印花 0.8222，与参照框不相交） | ref1：16 候选，最高 sfx **0.0855**（同框 text 0.5195）；ref2：19 候选，最高 sfx **0.0043**。两列口径注记（DSH r1 P4-3）：pre-NMS 候选（如 text 0.5195）与右侧 NMS 后保留框（text 0.7436）**不是同一候选对象**，两侧数字不得互推 | text conf 0.7436（sfx 0.0004）/ 0.8437（sfx 0.0010）+ panel 大框（平凡覆盖） |
| BJ14 | 18（sfx **0**） | ref1：**0 候选**；ref2：**0 候选**；ref3：≥20 候选（探针上限 20，按 sfx 降序截断；最高 sfx 0.0001 为截断前首位，判定不受影响——DSH r1 P2-4） | ref2/ref3 bubble+text 并存（与 E2E 诊断一致）；ref1 仅 panel |
| BJ15 | 27（sfx **0**） | ref1：**0 候选**；ref2：3 候选，最高 sfx **0.0000** | 仅 panel 大框（IoU 0.056/0.075，平凡覆盖） |

要点：①BJ14 ref1/ref2、BJ15 ref1 的 letterbox 空间中心区**连 conf≥0.01 的任何类别候选都没有**——比「被判 text」更彻底的盲；②BJ13 参照框处 sfx 分数峰值 0.0855 与同框 text 0.5195 相差 6 倍，与 BJ06 域内形态（sfx 0.72+ 支配）完全不同——**不是贴阈竞争，是通道近乎无响应**；③对照 BJ06，0.01–0.50 扫描不改变任何判定（域内稳定、域外零信号），「类敏感阈值」方案对 BJ 盲区无效的直接证据。

### 2.3 L2 结果（60% tile，~1.67× 有效分辨率）

BJ13/14/15 各 4 tile、conf 0.01：tile 层 sfx 类偶有检出（BJ13 BL/BR 共 3 框、BJ15 TR 1 框），**均不落在任何参照框位置**（BJ13 参照框处 best sfx 0.0001–0.0002；BJ14 0.0000–0.0003；BJ15 0.0000——DSH r1 P3-1 更正：0.0003 属 BJ14 而非 BJ13）。1.67× 分辨率不恢复 sfx 信号。

### 2.4 L3 结果（参照框 crop，最强形态）

7/7 参照框 crop（外扩 20%，等效分辨率 3.5–5.4×）下 **sfx 类 0 检出**：

| 参照框 | crop_h/page_h | best sfx 分数 | 模型实际判定（crop 内最高 conf 框） |
|---|---|---|---|
| BJ13 ref1 | 0.255 | 0.0074 | bubble 0.6533 + text 0.1296 |
| BJ13 ref2 | 0.282 | 0.0109 | **text 0.735**（sfx 0.0109） |
| BJ14 ref1 | 0.218 | 0.0008 | panel 0.9167 |
| BJ14 ref2 | 0.222 | 0.0000 | **bubble 0.9151 + text 0.9046（并存）**（DSH r1 P2-3 更正：最高 conf 框是 bubble，text 第二） |
| BJ14 ref3 | 0.215 | 0.0041 | bubble 0.9113 + **text 0.8707** |
| BJ15 ref1 | 0.202 | 0.0001 | bubble 0.0164（近零） |
| BJ15 ref2 | 0.185 | 0.0000 | **0 框** |

（列头口径：`crop_h/page_h` 为 raw JSON `effective_scale_vs_fullpage` 字段原值=crop 相对页面的占比；**等效分辨率倍数=page_h/crop_h=1/0.185–1/0.282≈3.5–5.4×**，与 L2 的 1/0.6=1.67× 同公式——DSH r1 P2-1。）

画面里几乎只剩单个 SFX 时，模型仍把它判为 text/bubble/panel 或干脆无检出——「给足像素模型就认得出」不成立。**该形状本身在 chiqui7 的 sfx 语义之外**。

### 2.5 尺寸对照（预处理假设的独立检验）

letterbox 空间（scale=1024/4167≈0.2457）下的目标尺寸：

- BJ06 域内正例（8 框）：21–84 宽 × 25–131 高；
- BJ13-15 参照框（7 框）：61–86 宽 × 135–206 高。

盲区目标**不小于**域内正例（反而系统性更大）——「目标太小在 1024 letterbox 下消失」不成立。L3 crop 形态下目标占模型输入高约 **71%**（参照框高/外扩后 crop 高=1/1.4，上下各外扩 20%；DSH r1 P2-2 更正：r1 版误读 raw 字段把 crop_h/page_h 当成了目标占比）——比域内正例更大，「尺度过大」在 crop 形态下更极端；L3 的 7/7 零检出因此说明「形状语义×尺度」的联合形态处于训练分布外。**必须明示的残余开放项：「目标太大」作为单独的替代假设未被本次实验单独排除**——L3 同时改变了目标占比与像素预算两个变量，没有「同占比、更高分辨率」的对照形态。该开放项不影响主根因判语：无论「形状域外」还是「尺度过大」，处置指向一致（域内标注/训练=方案③），且 (c) 的预处理机理（像素预算不足/各向异性）已由 L2（1.67× 不恢复）与等比 letterbox 独立排除。chiqui7 letterbox 为等比缩放+左上贴图（`detection_sfx.py` `_letterbox`），不存在 WEBTOON-DIAG 的各向异性压缩机理（该先例是 ogkalu/RT-DETR 690×62133→640×640 的 97× 垂直压缩，形态完全不同，不可套用）。

## 3. AC1：三假设定判（证据汇总与根因分层）

### 假设 (a) 域外：chiqui7 训练域不含 BJ 毛笔竖排形态 —— **DETERMINED：成立（主根因）**

- L3（最强形态）：7/7 参照框 sfx 分数 0.0000–0.0109（§2.4）；域内对照同管线 sfx 分数 0.72–0.94（§2.2）——相差 2–3 个数量级。
- L1 raw pre-NMS：参照框内 sfx 分数峰值 BJ13 ref1 0.0855 / ref2 0.0043 / BJ14 ref3 0.0001 / 其余 0.0000（§2.2）。
- 与 DETECT-EVAL Known limitations 4（chiqui7 训练数据未登记→域适配不可预判）方向一致：KO webtoon 域 sfx 类 11/29 有真实信号，BJ 毛笔竖排形态是训练分布之外的失效模式。
- 附着证据：KO 域同一模型对**竖排大字** sfx 有过类内不稳定记录（뒤적뒤적 两行斜排判 sfx 0.93、竖排大字判 text 0.92，DETECT-EVAL §3.3）——竖排毛笔形态本身已是模型的边界形态，BJ 的更大尺度毛笔字彻底滑出。

### 假设 (b) 类别映射歧义：sfx 被判 text/panel —— **DETERMINED：分层成立（症状层成立，机制层否定）**

- **成立的部分（症状层）**：SFX 像素确被其他类高 conf 捡走——BJ13 两个参照框的紧贴 text 框 conf 0.7436/0.8437（IoU 0.452/0.544，E2E r1 R2 口径）；L3 crop 中 BJ13 ref2 判 text 0.735、BJ14 ref2/ref3 判 text 0.9046/0.8707（§2.4）。产品侧的误路由损害（SFX→speech 乱译进渲染）与该症状同源：检出的 speech/text region 占据 SFX 位置（BJ13 生产 run region ffed29e8/de83b0c4 与目检 SFX 逐点对位，`qual-BJ13.json`）。
- **否定的部分（机制层）**：「sfx 信号存在、只是 argmax 竞争输给 text、可用差异化阈值救回」**不成立**——同框分数对比 text 0.7436 vs sfx 0.0004（BJ13 ref1）、text 0.8437 vs sfx 0.0010（ref2）、text 0.735 vs sfx 0.0109（L3）；raw pre-NMS 峰值 sfx 0.0855 距任何可用阈值都有数量级距离。**竞争没有发生**：sfx 通道对这批像素近乎零响应。
- **BJ15 的进一步分层**：仅 panel 大框平凡覆盖（IoU 0.056/0.075）、raw 查询 ref1 为 0 候选——BJ15 连「被 text 捡走」的紧贴载体都没有，是比 BJ13 更深的盲。

### 假设 (c) 预处理（分辨率/letterbox）对大型竖排字不利 —— **DETERMINED：不成立**

- L2（1.67×）与 L3（3.5–5.4×）分辨率提升均不恢复 sfx 信号（§2.3/§2.4）——与 WEBTOON-DIAG「0→193 恢复」的分辨率根因形态完全相反。
- 尺寸对照：盲区目标在模型输入空间不小于域内正例（§2.5）。
- 机理排除：等比 letterbox，无各向异性（§2.5）。
- 保留注记：L2/L3 均为单次单形态探针，未穷举 imgsz 本身（ONNX 输入形状固定 1024，无法变 imgsz 直接验证）；但 L3 的 crop 形态已覆盖「像素预算充足」的判定需求，残余不确定性不影响判语。另一残余开放项（DSH r1 P2-2）：**「目标太大」替代假设未被单独排除**——L3 crop 下目标占输入高 ~71%（更大而非更小，§2.5），L3 零检出说明「形状语义×尺度」联合形态处于训练分布外；该形态不属预处理机理（管线无各向异性、像素预算已 3.5–5.4×），处置指向与 (a) 域外一致（域内标注/训练=方案③），不影响本判语。

### 汇总判语（一行 each）

- **(a) 域外 = DETERMINED 成立（主根因）**；**(b) 类别映射歧义 = DETERMINED 分层（SFX 像素被其他类捡走=成立；sfx 信号被压制可阈值救=否定）**；**(c) 预处理 = DETERMINED 不成立**。E2E r1 R2 遗留的「panel/text 混淆归属未定」由本实验收敛（DSH r1 P1-1 更正：BJ14 并非 text 主导）：**BJ13 的紧贴混淆候选=text**（与 ko 域形态同型）；**BJ14=bubble 主导＋text 并存**（紧贴候选 IoU：ref2 bubble 0.122 > panel 0.094 > text 0.086，ref3 bubble 0.399 > text 0.274 > panel 0.126，上游 `sfx-detect-diagnosis.json`）；panel 大框在 BJ13/14/15 均为平凡覆盖（IoU 0.013–0.126），不构成独立根因。

## 4. AC2：五方案评估（只评估不实施）

评估基线：BJ 盲区 = BJ13-15 毛笔竖排形态（7 实例）；损害双通道 =「漏检无 sfx region」+「误路由 speech 乱译渲染」（后者与 SfxPolicy 无关）。C4 条件式先例：`verification/M2-DOCTR-QUAL/qualification/c4-manga-domain-report.md` §7.1（「冻结口径内无剩余收益→不释放 fine-tune 主线」的条件式裁决形态）。

### ① 后分类器（对 text/panel 检出框跑 SFX 二分类小模型）

| 维度 | 评估 |
|---|---|
| 改动面 | detect 后处理新增分类步 + 分类器资产；**且必须配合 region 创建的重叠仲裁**（speech→sfx 改标）才能闭合误路由——后者是 region 语义/契约面变更 |
| 成本 | SFX 二分类 GT（BJ 域正例：官方免费 3 卷约 600 页中人工框选；KO 侧 29 实例可复用）+ 训练 Task + 评估 Task；推理成本轻量（分类器 << 检测器） |
| 预期收益 | **只救 BJ13/14 形态**：BJ13 两个参照框有紧贴 text 框（0.744/0.844）可送分类；BJ14 ref2/ref3 有 bubble/text 部分相交框。**BJ15 结构性救不了**：参照框处无紧贴 text/bubble 载体（仅 panel 大框平凡覆盖，对 panel 大框跑分类=整页级误报面，裁剪子区域则引入未解的子窗口问题） |
| 风险 | 分类器自身域外风险（训练集若不含 BJ 毛笔形态则同样失效——本实验的教训直接传导）；panel 大框分类语义混乱；重叠仲裁的 region 语义变更是共享契约面 |
| SfxPolicy 交互 | 命中改标后 policy 门生效：SKIP 默认下该 region 不翻译（静默无译文，但不再乱译）；translate 下进 SFX 翻译链（BJ06 已实证闭环）；**manual 与 skip 同判 SKIP**（`decide_sfx_translation`：sfx+skip/manual→SKIP，DETECT-EVAL §4.1——DSH r1 P4-2）。注意 SKIP 默认下**原 speech region 若未被仲裁掉，乱译损害仍在** |

### ② 类敏感阈值（sfx/text 差异化 conf）

| 维度 | 评估 |
|---|---|
| 改动面 | 最小（conf filter 按类差异化，`detection_sfx.py` 单参数族扩展；env 已有 `NEWMANGA_SFX_CONF_THRESHOLD` 先例） |
| 成本 | 近零（静态） |
| 预期收益 | **对 BJ 盲区无效（本实验直接否决）**：conf 0.5→0.01 九档扫描，BJ14/15 参照框处 sfx 类框数恒 0、BJ13 参照框处亦 0（唯一 sfx 框是 T 恤印花误报）；raw pre-NMS sfx 峰值 0.0855 仍需阈值 <0.09 才能吃到，且该框 argmax=text、生产序列下先被 conf filter 以 text 身份处理——差异化阈值救不出一个 argmax 都不是 sfx 的框 |
| 风险 | 负收益：0.01–0.09 带会放进 BJ06 的 0.0114 弱框等误报；对误报 T 恤印花型（0.8222）无任何抑制 |
| SfxPolicy 交互 | sfx 候选误报增加 → SKIP 下并存 region 增多（无损害但噪声）；translate 下误报进翻译链；manual 与 skip 同判 SKIP（同①，DSH r1 P4-2） |

### ③ chiqui7 fine-tune（BJ 域标注，沿 C4 条件式先例）

| 维度 | 评估 |
|---|---|
| 改动面 | 检测层（权重资产替换/追加）；生产代码零改动（sha256 pin 更新为流程面）；同样建议配合重叠仲裁闭合误路由 |
| 成本 | **最高**：BJ 域 SFX 框标注（正例数百级才稳，官方免费 3 卷可标注但要人工逐页）+ 训练基础设施（Ultralytics 生态）+ 训练/评估/回归 Task 链；训练数据登记义务（chiqui7 原训练集未登记，衍生训练需从零建立来源链） |
| 预期收益 | **自动化覆盖的对症路径**：本实验判定的主根因是域外——fine-tune 是唯一直接修复 sfx 通道对 BJ 形态响应的方案；L3 的 crop 形态可直接转为增强/训练素材裁片 |
| 风险 | ①Ultralytics AGPL 权重争议在**衍生训练权重**下更尖锐（AGPL 传导主张覆盖 fine-tune 产物，比直接分发原权重的争议更难辩护）——用户裁决前置；②灾难性遗忘：BJ06 域内 0.72+ 信号可能退化，回归基线必须冻结（BJ06 8 region + KO 域 11/29 双口径）；③标注质量依赖人工目检（无 GT 体系） |
| SfxPolicy 交互 | 无直接交互（检测层修复）；召回提升后 SKIP/translate/manual 语义照常（manual 与 skip 同判 SKIP——DSH r1 P4-2） |

### ④ 路由（BJ 家族 detect 走 docTR+后处理）

| 维度 | 评估 |
|---|---|
| 改动面 | route_policy 分支（provider 路由是装配/契约面）+ docTR 检测路径 + 后处理合成 region |
| 成本 | 中：路由分支维护 + BJ 家族行为分歧的测试面 + docTR 词/行级粒度到 region 粒度的语义桥接 |
| 预期收益 | **未验证且存疑**：docTR 对 BJ 毛笔竖排 SFX 的检出能力没有任何评估记录；C4 基线报告反登记 docTR 在 KO 域对 SFX 的形态是「误检源」（`verification/M2-DOCTR-QUAL/baseline-summary.md` §6 gap ①：SFX/人脸误检）——检出≠可用 |
| 风险 | 把「检出后判 sfx」问题原样带回（docTR 无 SFX 类，后处理仍需①的分类器）→ 方案④实质是①的次形态叠加路由成本；BJ 家族单独路由造成双管线行为分歧 |
| SfxPolicy 交互 | docTR 检出的 SFX 若仍标 text/speech → 对话链乱译照旧，与现状损害相同；若后处理改标 sfx，policy 门语义同①（manual 与 skip 同判 SKIP——DSH r1 P4-2） |

### ⑤ 维持现状 + 产品侧缓解

| 维度 | 评估 |
|---|---|
| 改动面 | 产品/UI 层（React/Tauri，Qoder 主责）：(a) region 手动改标 region_type=sfx 的入口（DETECT-EVAL 路径 C，SfxPolicy 门即时生效，`decide_sfx_translation` 只看 region_type）；(b) speech region 的「疑似 SFX」标记/警示（启发式或纯人工） |
| 成本 | 最低（零模型、零检测层改动）；UI Task 属既有人机面 |
| 预期收益 | **不恢复自动化召回**；但把已实证的损害形态（「误路由→乱译→静默进渲染」）变为「可发现/可修正」——是**唯一直接处置误路由损害**的短期方案（①②③在不配合重叠仲裁时都不触碰 speech 侧损害） |
| 风险 | 无自动化收益；用户负担（逐页人工）；「疑似 SFX」启发式若做自动化误标本身有误报面 |
| SfxPolicy 交互 | 手动改标后 policy 门语义立即生效：SKIP（默认）与 manual（与 skip 同判 SKIP，`decide_sfx_translation`——DSH r1 P4-2）=停止乱译改静默、translate=进 SFX 翻译链——产品语义完全复用 |

### 交叉要点（对所有实施型方案生效）

- **重叠仲裁缺口**：`_create_detected_region` 按候选独立建 region、无跨 provider 重叠去重（`src/bootstrap/core_assembly.py` L1013-1049）——chiqui7 召回修复（①②③任一）后，SFX 位置将同时存在 sfx region 与 ogkalu speech region，**乱译渲染损害不消失**。重叠仲裁（sfx 框覆盖 speech region 时改标/抑制）属 region 创建语义变更=共享契约面，须 Codex 明确范围后方可进实施 Task（即 DETECT-EVAL §4.4 条件 5「sfx 类与 text 类框的合并去重规则」的具体化）。
- **BJ06 双跑注记**：chiqui7 已在生产并行位（`MangaSfxParallelDetectionProvider`），②③的阈值/权重变更会影响所有已接入家族（KO/JA），回归口径必须同时覆盖 KO 域（DETECT-EVAL 23 帧/29 实例基线）与 JA BJ06（8 region 基线）。

## 5. AC3：裁决建议（移交用户/编排）

### 排序（推荐 → 不推荐）

| 排名 | 方案 | 建议形态 |
|---|---|---|
| 1 | **⑤ 维持现状 + 产品侧缓解** | **短期首选**：释放「region 手动改标 sfx + speech 疑似警示」UI 切片（Qoder 主责，另行 Task）。理由：零模型/零契约风险；直接处置已实证的乱译渲染损害；SfxPolicy 门语义现成。**「不实施检测侧变更」是合法选项**——BJ13-15 是评测素材（非用户数据流必经），若用户判定 BJ 域自动化覆盖非近期目标，⑤的轻量形态（甚至仅登记已知盲区）即可止损 |
| 2 | **③ chiqui7 fine-tune（条件式）** | 若用户要 BJ 域自动化覆盖，这是唯一对症路径（主根因=域外）。前置条件（全部满足才释放）：(a) Ultralytics AGPL 衍生权重许可裁决（用户）；(b) BJ 域 SFX GT 标注+人工审核（C1 流程先例）；(c) 冻结回归基线（BJ06 8 region + KO 29 实例双口径）；(d) 训练数据来源链登记。沿 C4 §7.1 条件式先例的裁决形态，但条件方向相反（C4=无收益不投入；本处=有明确收益、条件在成本与许可） |
| 3 | **① 后分类器（条件性次优）** | 仅在「接受 BJ15 盲区、只救 BJ13/14 形态」的次优目标下考虑；且必须与重叠仲裁设计同 Task 交付，否则损害不闭合。分类器训练集必须显式包含 BJ 毛笔形态（否则重演本实验的域外失效） |
| 4 | **④ 路由** | 不推荐独立立项：docTR 对 SFX 无类面、检出能力未验证（C4 反登记其为误检源），后处理仍回到①的分类问题；仅当未来 docTR 侧出现 SFX 能力证据时再议 |
| 5 | **② 类敏感阈值** | **否决（实验无效）**：九档扫描证明 sfx 通道对 BJ 盲区零信号，阈值不可救；负收益（弱误报放行）。不建议在任何形态下实施 |

### 移交裁决的三个具体问题

1. 是否接受「不实施」+ 仅做⑤的 UI 缓解（或完全维持现状仅登记盲区）？
2. 若走③：Ultralytics AGPL 衍生权重许可裁决（接受风险 / 企业许可 / 改用非 Ultralytics 基座模型自训——第三选项会引入新的模型选型评估 Task）。
3. 无论 ①/③：region 创建的重叠仲裁语义（sfx 框与 speech region 并存时的改标/抑制规则）属共享契约变更——是否授权 Codex 立契约裁决切片？

## 6. Known limitations（引用本报告时不得省略）

1. **directional**：3 盲区页 7 实例 + 1 对照页；无 SFX GT（参照框为 100dpi 目检 zoom 确认的近似框，同 E2E AC2 口径）；单 AI 标注者；未做多 seed（推理确定性由同权重单次前向保证，前向本身确定性）。
2. 参照框近似性：目检 approx bbox（±10-20px 级）影响 IoU/相交判定的边缘个案，不影响本报告的量级判定（sfx 分数 0.000x vs 0.72+ 的对比跨 2-3 个数量级）。
3. L2/L3 是单形态探针：未穷举 tile 布局/crop 外扩比例/imgsz（ONNX 固定 1024 输入不可变）；L3 结论「给足像素仍不识别」对 crop 外扩 20% 这一律成立；且 L3 同时改变目标占比（~71% 输入高，§2.5）与像素预算，「目标太大」替代假设未被单独排除（DSH r1 P2-2）——该开放项不影响域外主根因判语与 §5 方案排序（两条路径的处置指向一致）。
4. raw pre-NMS 查询的几何口径是「letterbox 空间中心点落入参照框」——覆盖框（如 panel 大框）中心在外不被计入；NMS 后相交口径已并列报告，两口径结论一致。
5. 方案成本为静态分析+既有证据推导（directional），未做任何训练/集成实验；收益估计以本实验的通道响应证据为界。
6. BJ06 对照的正例身份来自生产 run 检出（chiqui7 自证）——「BJ06 域内」的独立 GT 佐证不存在；若 BJ06 的 8 region 本身含误报，域内/域外对比的分母有残余不确定性（但 8 region 均通过 OCR+翻译+渲染全链且人工抽检方向正确，E2E §1.3）。
7. 环境差异：实验为 CPU（onnxruntime 1.30.0）+ 生产同源 letterbox 序列复放；与生产 GPU 路径（如有）的数值差异未测（同 DETECT-EVAL limitation 8）。

## 7. 证据物与复现

| 证据物 | 位置 |
|---|---|
| 实验工具 | `experiments/M2-SFX-DETECT-DOMAIN-EXT-DIAG/conf_scan_diag.py` |
| L1 整页 conf 扫描 raw | `verification/M2-SFX-DETECT-DOMAIN-EXT-DIAG/raw/l1-fullpage-conf-scan.json` |
| L2 tile 分辨率探针 raw | `verification/M2-SFX-DETECT-DOMAIN-EXT-DIAG/raw/l2-tiles-resolution-probe.json` |
| L3 参照框 crop raw | `verification/M2-SFX-DETECT-DOMAIN-EXT-DIAG/raw/l3-reference-crops.json` |
| 实验 manifest（权重/imgsz/档位） | `verification/M2-SFX-DETECT-DOMAIN-EXT-DIAG/raw/scan-manifest.json` |
| 本报告 | `verification/M2-SFX-DETECT-DOMAIN-EXT-DIAG/diagnosis-and-options.md` |

复现（worktree 根目录；只读引用 gitignored 页面图像，输出全落本 Task 目录）：

```bash
"G:/CODEX/New Manga.task-envs/M2-TA3-B-ocr/Scripts/python.exe" \
  experiments/M2-SFX-DETECT-DOMAIN-EXT-DIAG/conf_scan_diag.py
# 期望：engine OK imgsz=1024 (metadata_parsed)；L1 四页 ~0.2s/页；
# BJ06 @0.01 sfx=9；BJ13/14/15 参照框 sfx_box=False ×7；
# L2 tile 参照框 sfx_box=False ×7；L3 crop best_sfx ≤0.0109 ×7
```

## 8. DSH r1 闭合对照（r2 返修记录）

DSH r1：verdict=`changes_requested`（0×P0，1×P1 + 4×P2 + 3×P3 + 3×P4）。**主根因判语、五方案评估、AC3 排序、结构性发现均被确认成立且未越权，不需重跑实验**——本版为纯文字/数字返修，返修 commit 只触碰本报告、Task、Handoff 三个文件，`experiments/**` 与 `raw/**` 零改动。逐条处置：

| 编号 | 发现 | 处置 | 落点 |
|---|---|---|---|
| P1-1 | §3 收敛判语「BJ13/14 的紧贴混淆候选是 text」错误——BJ14 实为 bubble 主导（上游 `sfx-detect-diagnosis.json`：ref2 bubble IoU 0.122 > panel 0.094 > text 0.086；ref3 bubble 0.399 > text 0.274 > panel 0.126） | 改为「BJ13 的紧贴混淆候选=text（与 ko 域同型）；BJ14=bubble 主导＋text 并存（bubble IoU 0.122/0.399）；panel 大框在 BJ13/14/15 均为平凡覆盖（IoU 0.013–0.126）非独立根因」；同步 Task 交付记录与 Handoff 交付结果表 | 本报告 §3 汇总判语；Task 交付记录；Handoff AC1 行 |
| P2-1 | L3「等效 2.4–3.4×」错（误把 crop/page 占比当倍数） | 三处改 **3.5–5.4×**（=page_h/crop_h=1/0.282–1/0.185，与 L2 的 1/0.6=1.67× 同公式）；§2.4 表列头改 `crop_h/page_h` 并加公式注 | 本报告 §2.1/§2.4/§3(c)；Task 交付记录 |
| P2-2 | §2.5「crop 后目标只占输入高 ~19–28%」误读字段（那是 crop 高占页面高比例） | 改写：目标占模型输入高≈**71%**（1/1.4）——比域内正例更大，故「目标太小」不成立；「尺度过大」在 crop 下更极端；明示**「目标太大」替代假设未被单独排除**（L3 同时改占比与像素预算，无同占比对照）；不影响主根因「域外」 | 本报告 §2.5/§3(c)/§6 limitation 3 |
| P2-3 | §2.4 表 BJ14 ref2 行「text 0.9046」填错最高 conf 框 | 改「**bubble 0.9151 + text 0.9046（并存）**」（其余 6 行 DSH 已核对正确，不动） | 本报告 §2.4 表 |
| P2-4 | §2.2 表 BJ14 ref3「20 候选」恰为探针截断上限未标注 | 标注「≥20（探针上限 20，按 sfx 降序截断；最高 sfx 0.0001 为截断前首位，判定不受影响）」 | 本报告 §2.2 表 |
| P3-1 | §2.3「BJ13 参照框处 best sfx 0.0001–0.0003」错（0.0003 属 BJ14） | 改「BJ13 0.0001–0.0002；BJ14 0.0000–0.0003；BJ15 0.0000」 | 本报告 §2.3 |
| P3-2 | base 二义（Task frontmatter base_commit=24a89d7d vs claim @497621df） | Task 交付记录加基线口径注明：「任务基线=24a89d7d；claim 时仓头=497621df；本 Task 全部 diff 固定点=497621df」 | Task 交付记录 |
| P3-3 | Handoff 提交清单缺收尾 commit hash | Handoff 提交清单补返修主体 commit hash 与收尾 commit 说明；Task frontmatter 增 `rework_head` 与 reviewed 口径对齐 | Handoff 提交清单；Task frontmatter |
| P4-1 | §2.1 分档实现口径未注（脚本为一次推理多档重筛，非逐档 filter→NMS） | L1 行加注：分档实现=「同一 conf≥0.01 全集 NMS 后按 conf 重筛」，与「逐档 filter→NMS」的等价性依赖 `_nms` 贪心按 conf 降序（`detection_sfx.py:469-477` `np.argsort(scores)[::-1]`，高 conf 候选先处理、低 conf 候选不可能抑制高 conf 候选），故 §2.2「0.50 档 8=生产 run 8 个 sfx region」成立 | 本报告 §2.1 |
| P4-2 | §4 五方案「SfxPolicy 交互」行未显式覆盖 manual 值 | 五行全部补「manual 与 skip 同判 SKIP」（`decide_sfx_translation`：sfx+skip/manual→SKIP，DETECT-EVAL §4.1） | 本报告 §4 各方案 |
| P4-3 | raw pre-NMS「同框 text 0.5195」与 NMS 后保留框 text 0.7436 易被误读为同一候选 | 加注「pre-NMS 候选与 NMS 后保留框不是同一候选对象，两侧数字不得互推」 | 本报告 §2.2 表 |
