# M2-REGION-OVERLAP-ARBITRATION：region 创建跨 provider 重叠仲裁 — 仲裁报告（r2，DSH r1 返修版）

- Task：[M2-REGION-OVERLAP-ARBITRATION](../../doc/tasks/M2-REGION-OVERLAP-ARBITRATION.md) · 分支 `agent/zcode/M2-REGION-OVERLAP-ARBITRATION` · base=`eb7cd15e`（claim=`8c74d170`，实现主体=`b27c826f`，r1 交付=`4d8aaee0`，本版=r2 返修）· 日期 2026-10-04
- Owner=ZCode · Reviewer=DeepSeek Harness（非作者；r1=`changes_requested` 0×P0/3×P1/5×P2/4×P3/4×P4，逐条处置见文末 §9「DSH r1 闭合对照」）· Integrator=编排会话代行 Codex（用户全权授权+自治授权）
- **r2 修订声明**：DSH r1 确认不可达性论证物理成立（0.8862/0.870/0.728/0.5501/0.4903 手算溯源吻合）、实现工艺与范围纪律良好（AC1/AC4/AC5 PASS）；争议在合同层——编排方 2026-10-04 裁决采纳选项 (a)：**AC2 正式修订为「结构性不可达登记 + 近重复双检出形态级闭环」**（依据：①上游 DOMAIN-EXT-DIAG 本就把重叠仲裁定位为「召回修复的配套件」，用户裁决③授权语境一致；②DSH 确认实现工艺高，关闭重置浪费；③BJ13 自动化闭合显式挂到 sfx 召回恢复 Task 依赖链）。Owner 在 claim/实施时未预提交该范围修订请求属程序瑕疵，登记于 §9，不再追责。r2 新增：KO 域 10 case detect 层证据（P1-2）、第二道门量化评估（P2-2）、其余 P2/P3/P4 逐条处置。
- **证据强度裁定（全程适用）**：全部结论为 **directional**——阈值校准基于既有 raw（qual-BJ06/BJ13/BJ14/BJ15 生产 run + DOMAIN-EXT-DIAG L1 扫描 + E2E 相交枚举）+ 本 Task 真实 rerun（BJ13/14/15/BJ06 + KO 10 case，ogkalu+chiqui7 生产双 provider，权重 sha256 pin 校验通过）；绿态闭环含合成 sfx 候选口径（现状权重对 BJ 域 sfx 零召回，DOMAIN-EXT-DIAG 已判定为域外根因，禁改面）。单 AI 标注者参照框（±10-20px）沿用上游口径。

## 0. 结论速览

| AC | 判定 | 一行结论 |
|---|---|---|
| AC1 仲裁语义提案 | **PASS（DSH r1 确认）** | 层位=provider 拼接层（composite）；度量=bbox IoU；规则=sfx 候选驱动的 directional 改标（`sfx-`→`sfx-arb-<原label>`）；冻结阈值 **0.90**；env `NEWMANGA_SFX_ARBITRATION[_IOU]` typed 旋钮 |
| AC2 红绿判别 | **DELIVERED（按 2026-10-04 编排裁决 (a) 修订口径）** | ①结构性不可达登记：BJ13 红态真实对位（manga-1/manga-3=qual region#1/#3 乱译路径），现状权重下 sfx 通道零候选、召回恢复后参照框口径重叠 0.49-0.55 仍在 0.90 域外——双层不可达 typed 可诊断，本仲裁在召回恢复前对 BJ13 形态 **no-op**（显式挂 sfx 召回恢复 Task 依赖链）；②近重复双检出形态级闭环：0.90+ 形态的实现路径验证（代码级，合成口径 3/3 改标落 RegionType.SFX）；**真实 0.90+ 形态至今 0 观测**（本 Task 全部真实样本面：BJ 4 页 22 sfx×25 primary 候选对 + KO 10 case，合计 0 对 ≥0.90） |
| AC3 零变化回归 | **DELIVERED（KO 补证后完整）** | BJ06 仲裁 off/on 候选逐位一致（17=17，bit-identical=True）+ **KO 10 case off/on 全部逐位一致**（合计 1034 候选；sfx×primary 相交对最高 IoU=0.1325（K11 唯一 sfx 检出样本），全族 0 对 ≥0.90——P1-2，无 STOP 条件）；真实 rerun 与 qual-BJ06 生产基线对位；BJ13/14/15 计数对位；pytest 三套件 **627 passed + 1 skipped，0 failed，EXIT=0**（r2 重跑确认，日志显式落 EXIT 码）；cargo/vitest 零改动面（集成方复跑） |
| AC4 边界与 fail-closed | **PASS（DSH r1 确认）** | 双 env 空值/非法值 fail-fast `ValueError` naming the variable（TILING 先例，detect 入口解析，非法时 primary 不运行）；默认冻结（on + 0.90）并记录依据；不可达形态 typed 可诊断（`sfx_arbitration_partial_overlap` / `sfx_candidates=0`） |
| AC5 契约边界 | **PASS（DSH r1 确认）** | `doc/contracts/**`、RegionInput wire shape、handlers `region_creator` 签名、core_assembly 分发矩阵全部零改动；detect options 新键经消费方审计确认非 wire（§3.4）；改标仅复用既有 `startswith("sfx-")` label 契约 |

**必须被 Review 与后续 Task 承认的结构性结论（本 Task 的核心定案）**：**纯几何重叠信号在 BJ06 域内对照与 BJ13 误路由 case 之间反向不可分离**——域内 sfx×speech 候选最高 IoU **0.886**（BJ06「！！！」双检出对）、误路由 case 仅 **0.490-0.550**；「误路由 case 高、域内 case 低」的分离前提在既有 raw 数据上**不成立**。因此任何能捕获 BJ13 形态的重叠阈值必先改标 BJ06 真对白（违反 AC3 域内零变化）。冻结默认 0.90 是证据支持的唯一安全域（域内最高之上），其语义是「双 provider 对同一物体的近重复双检出 → 类型仲裁归 sfx」，**不是** BJ13 误路由的自动化修复——后者的闭合依赖 sfx 召回恢复（域外根因，另行 Task）+ 未来形态的重叠量，已按 AC2/AC4 要求如实登记为 typed 可诊断的不可达面，未伪造覆盖。

## 1. AC1：仲裁语义提案与证据定案

### 1.1 层位选型：provider 拼接层（`detection_sfx.py` composite）

| 候选层位 | 判定 | 理由 |
|---|---|---|
| **(a) provider 拼接层**（`MangaSfxParallelDetectionProvider.detect`，拼接前） | **选定** | ①两端信号（primary 候选全集 + sfx 候选全集）只在此层同时可见；②handlers/core_assembly 是 provider 无关层，只见匿名 `provider_label` 字符串与逐候选流，在此仲裁需从 label 前缀反推 provider 归属并把逐候选循环改造为两遍——语义扭曲更大；③零契约面：`RegionCandidate`/`region_creator` 签名/wire 不动，仅 composite 输出的候选 tuple 与 options 尾部变化；④行为面局部化：单 provider 路径零改动，sfx typed 降级路径在仲裁之前 return 天然不受影响；⑤provenance options 已有 composite 登记先例（`sfx_provider`/`sfx_candidates`），仲裁统计顺路 |
| (b) region 创建层（handlers/core_assembly） | 否 | 见上 ②；且 `_create_detected_region` 是单候选闭包，跨候选重叠语义无现成挂点 |

### 1.2 重叠度量：bbox IoU

与上游证据同口径（E2E `sfx-detect-diagnosis.json` 的 IoU 列、DOMAIN-EXT-DIAG 相交枚举），阈值数字可直接溯源；bbox 取 `min/max(polygon)`，与 core_assembly `RegionGeometry` 的 bbox 口径一致——仲裁看到的就是 region 将被创建的几何。

### 1.3 规则：sfx 候选驱动的 directional 改标

- 任一 primary 候选与任一 sfx 候选 bbox IoU ≥ 阈值 → 该 primary 候选 `provider_label` 改为 `sfx-arb-<原label>`（如 `sfx-arb-manga-3`）；polygon/reading_order/confidence **逐字保留**（改标是类型决定，不是重检出）。
- 改标落点：`sfx-arb-` 前缀天然满足 core_assembly `_detected_region_type` 的 `startswith("sfx-")` 契约 → `RegionType.SFX` → 既有 SfxPolicy 门（默认 SKIP）自动接管——**core_assembly 零改动**，分发矩阵以新增参数化行锚定（`tests/core/test_sfx_assembly.py::test_detected_region_type_matrix` 的 `("sfx-arb-manga-3", RegionType.SFX)` 行；`startswith` 语义在 base `eb7cd15e` 上即成立）。
- 方向性：只有 sfx 候选触发改标（sfx provider 是 SFX 专用信号）；sfx 候选本身永不改标/抑制。多个 sfx 候选命中取最大 IoU 判定；一个 sfx 候选可改标多个 primary 候选（0.90 域内极端保守，无配对唯一性需求）。

### 1.3.1 「同位置双 SFX region」选型论证与已知副作用（P2-3）

仲裁改标后，同一位移将有 `sfx-arb-manga-N`（原 primary 几何）与 `sfx-M`（chiqui7 候选）**两个 RegionType.SFX region 并存**（口径 B 演示 3+4=7）。**为何不抑制其一**：

1. **零损害**：两者都进 SfxPolicy 门（skip 默认下都不翻译、不渲染译文）——不存在乱译/双重译文损害；SFX region 不进对话链，reading_order 语义不受影响。
2. **最小行为变更**：抑制（删除/跳过候选）是候选集语义的新增行为面，超出裁决③授权的「改标/抑制」中最小必要项——改标已闭合损害通道，抑制只省一个 SKIP 态 region。
3. **零观测**：真实 0.90+ 双检出形态至今 0 观测（§2.2），为 0 观测样本引入删除语义属行为面膨胀。
4. **可逆性**：改标保留全部几何/顺序/置信（审计面完整），抑制不可逆。

**已知副作用（登记）**：触发时 region 计数 +1/次；Workbench region 列表将显示两个空间重叠的 SFX region（均 SKIP 态）；OCR 阶段两个 region 各跑一次 OCR（少量算力浪费，结果不进翻译链）。**未来去重切片候选**：对 `IoU≥0.9 的 sfx×sfx-arb 对`抑制其一（沿 detect 层 class-agnostic NMS 先例），须与 UI 缓解 Task 的 region 列表设计对齐后另行释放。

### 1.3.2 margin 薄弱性、内含形敏感性与不确定度（P2-4/P3-4，登记项）

冻结 0.90 的域内安全性**必须如实标注为观测经验而非几何保证**：

- **margin 极薄**：域内最高对距阈值仅 0.0135（rerun 候选口径 0.90−0.8865）/ 0.0138（qual region 口径 0.90−0.8862）——两口径本身差 0.0003，即 margin 的第三位小数已不跨口径稳定。
- **内含形敏感性**：域内观测已存在完全包含形——BJ06 sfx#7 完全位于 speech#2 内（sfx_coverage=1.0），IoU=面积比 0.870。内含形的 IoU 上界是大小比 → 1.0：当 primary 候选仅比 sfx 候选大约 3% 时 IoU≈0.97>0.90，**任何有限阈值都会被「大小接近的内含形」击穿**。0.90 对内含形不提供结构性安全。
- **不确定度传播**：BJ06 校准对是模型输出对模型输出（同权重确定性复现，无目检不确定度）；但 BJ 系参照框对（0.490/0.550/0.123/0.429）带 ±10-20px 目检不确定度，其 IoU 摆幅量级 ±0.03-0.05——**大于上述任何 margin**。因此「误路由读数与域内读数之间存在可用分离带」的论证（无论把分离带算作 0.009 还是 0.0138）在参照框不确定度内被**量化否决**：分离带的几何意义不成立，0.90 的安全性唯一支撑=①当前观测样本无一越界 + ②AC3 经验回归（BJ06/KO off/on 逐位一致）。阈值域重审条件（挂召回恢复 Task）：内含形出现、或任何 0.85+ 对出现时必须重审。

### 1.4 阈值校准（BJ13/14/15 + BJ06 既有 raw + 本 Task 真实 rerun）

| 数据面 | 口径 | IoU | 对 0.90 域的含义 |
|---|---|---|---|
| BJ06 域内：sfx region × speech region（qual-BJ06，8×9=72 对） | 生产 region bbox | 3 对相交：**0.8862**（sfx 2eeaa2c4 × speech 5b76a907，「！！！」双检出）/ 0.870 / 0.728 | **域内最高 0.8862——0.90 必须在其上**（AC3 域内零变化的结构下界） |
| BJ06 域内：真实 rerun 候选（本 Task，chiqui7 sfx × ogkalu block） | composite 候选 bbox | 3 对相交，最高 **0.8865** | 同上，不触发（`sfx_arbitration_partial_overlap=0.8865` 诊断登记） |
| BJ13 误路由：ogkalu text region × 目检参照框（qual-BJ13 + E2E 诊断） | 生产 region bbox | **0.490 / 0.550**（本 Task rerun 实测 0.4902/0.5501）；E2E 诊断口径 0.452/0.544 | 低于 0.90 域——**如实登记不可达**（第二层） |
| BJ14：ogkalu speech × 参照框（rerun 实测） | composite 候选 bbox | ref2 **0.123** / ref3 **0.4287** / ref1 0 | 不可达；且现状 sfx=0 候选（第一层不可达） |
| BJ15：ogkalu speech × 参照框（rerun 实测） | composite 候选 bbox | ref1/ref2 与全部 7 候选 **零相交** | **结构性无载体**：仲裁两端永不相交 |
| chiqui7 text 框 × ogkalu speech（l1 raw，BJ06 vs BJ13，被评估并否决的替代信号） | chiqui7 全类框 | BJ06 域内 0.241-0.821 vs BJ13 0.830-0.927 | 带交叠 + 语义不通（双 text 一致不构成 sfx 证据），否决 |

**校准结论**：域内对照（0.886）与误路由 case（0.490-0.550）**反向不可分离**；Task 风险①（阈值过激误伤真对白）被数据证实为现实约束而非理论风险。冻结 0.90 = 域内最高 0.8862 之上的保守域；「捕获 BJ13」的激进域只能以 env 显式覆盖进入（`NEWMANGA_SFX_ARBITRATION_IOU`），默认不携带该风险。

**跨口径比较性质（P2-5，登记）**：本报告并列引用三种框源口径——qual 生产 region bbox（0.8862/0.490/0.550）、本 Task rerun 候选 bbox（0.8865/0.4902/0.5501）、E2E 诊断 chiqui7 text 框（0.452/0.544）。同一物理对在不同框源/量化下的读数差 0.0003-0.06；量级结论（误路由 ~0.5 << 域内 ~0.89）跨口径稳定，但**任何第二位小数级的阈值精调论证不得跨口径引用数字**（如以 region 口径的 0.8862 论证候选口径的 0.90 安全性时，必须承认两口径间存在未建模的 0.0003 级漂移）。

### 1.5 env 旋钮（AC4，TILING 先例）

| env | 默认 | 合法域 | 非法行为 |
|---|---|---|---|
| `NEWMANGA_SFX_ARBITRATION` | `on` | `on\|off`（strip+lower 归一） | 空/未知值 → `ValueError` naming the variable |
| `NEWMANGA_SFX_ARBITRATION_IOU` | `0.9` | `(0, 1]` | 空/非数字/越界 → `ValueError` naming the variable |

- fail-fast 位置：composite `detect` **入口**、primary 推理**之前**——非法配置不产生半检出页（专用探针测试锚定 primary 未被调用）。
- `off` 语义：回到 pre-arbitration 拼接行为（BJ06 off/on 逐位一致实验即其证明）。
- 空值拒绝沿 TILING r1 R3 never-silent-default 纪律（`""` 走同一 typed 路径）。

### 1.6 不可达形态的 typed 诊断（AC4）

detect options 尾部新增审计字段（provenance 面，非 wire）：

- `sfx_arbitration` = `on`/`off`（恒登记）；
- `sfx_arbitration_threshold`（on 且双端非空时登记）；
- `sfx_arbitration_relabels` = 改标数（仅非零时登记）；
- `sfx_arbitration_partial_overlap` = 当零改标且存在 `0 < IoU < 阈值` 相交时的最大 IoU（4 位小数）——「有重叠信号、落在保守域外」的 typed 可诊断形态；
- sfx 零候选时既有 `sfx_candidates=0` 字段即第一层不可达的诊断面。

BJ13 真实 rerun 的诊断读数：`sfx_candidates=1`（T 恤印花）且 `partial_overlap` 缺席——sfx 框与全部 manga 候选**零相交**（比「部分重叠未达阈」更彻底的信号缺失，与 DOMAIN-EXT-DIAG「sfx 通道对 BJ13 参照框零响应」一致）；口径 A（参照框注入）读数 `partial_overlap=0.5501`。

## 2. AC2：红绿判别

### 2.1 红态（真实 rerun，ogkalu+chiqui7 生产双 provider，sha256 pin 校验通过）

BJ13 真实 detect：primary=3 block 候选 + sfx=1 候选（T 恤印花 0.8222）：

- `manga-1` bbox (2124.1, 257.5, 2493.9, 1270.9) = qual-BJ13 region#1 `ffed29e8`（OCR「いやー、」→「哎呀——」乱译路径）；
- `manga-3` bbox (471.8, 2668.2, 780.1, 3669.6) = qual-BJ13 region#3 `de83b0c4`（「Ｗｉｆｉｘ」乱译路径）；
- 候选计数 4 = 生产基线 4 region（3 speech + 1 sfx）逐位对位。

红态判定：**乱译路径在**——两个误路由候选以 `manga-` 前缀进 `_detected_region_type` → SPEECH → 对话链；且现状权重下 sfx 通道对两处 SFX 字形零候选（唯一 sfx 框与全部 manga 候选零相交）→ **重叠仲裁现状不可达（第一层：触发器缺失）**。

### 2.2 形态级闭环（实现路径验证，代码级）+ 绿态成立条件

按编排裁决 (a)，本节是 **0.90+ 近重复双检出形态的实现路径验证（代码级）**，不是真实世界发生的观测——**真实 0.90+ 形态至今 0 观测**（本 Task 全部真实样本面 = BJ 4 页 22 个 sfx 候选 × 25 个 primary 候选的全部候选对 + KO 10 case 全族，合计 0 对 IoU≥0.90，§3.2）。合成 sfx 候选口径验证的是「该形态一旦出现（例如召回恢复 Task 之后），仲裁的改标-分发-门控链路正确闭合」：

| 口径 | 注入 | 结果 | 判定 |
|---|---|---|---|
| **口径 A：目检参照框 = 召回恢复的 sfx 候选**（BJ13 形态的假想召回世界） | 2 个参照框 sfx 候选（conf 0.99） | 不改标；`sfx_arbitration_partial_overlap=0.5501` 诊断登记 | **诚实不可达（第二层：即便召回恢复，0.49-0.55 仍在保守域外）**——不伪造覆盖 |
| **口径 B：近重复双检出（0.90 域的设计目标形态）** | 3 个与 manga 候选 ~0.95 缩放共位的 sfx 候选（IoU≥0.9，conf 0.99） | `sfx-arb-manga-1/2/3` 全部改标（relabels=3）；生产分发函数逐候选判定 `region_type="sfx"` ×3 | **形态级闭环（实现路径验证）**：改标 → RegionType.SFX → SfxPolicy 门接管 |

**绿态成立条件与残余限定（P2-1）**：改标进 SFX 门后的「不再乱译」语义以 **`sfx.policy=skip`（产品默认）为前提**——SKIP 下该 region 不翻译、不渲染译文（`decide_sfx_translation`：sfx+skip→SKIP，DETECT-EVAL §4.1）；策略门对配置的消费有生产实测背书：qual-BJ06 在 `translate` 配置下 8 个 sfx region 全部进入 SFX 翻译链（`translate_details` region_type=sfx ×8，`sfx_policy: "translate"`）。**限定**：若用户配置 `sfx.policy=translate`，被改标的 BJ13 形态会进 SFX 翻译链——「毛笔 SFX 文本被翻译并渲染」的残余损害与域内 BJ06 现状形态一致（用户已接受的产品语义），但其翻译质量未评估（SFX 翻译链属禁改面）；skip 默认下无此残余。

单元级先红后绿：15 个仲裁用例（14 红 + 1 个现状锚点绿）在实现前 14 failed/1 passed（`raw/red-phase-arbitration-tests.log`，pytest EXIT=1），实现后全部转绿（b27c826f）；另有 1 行分发矩阵参数化锚定，合计 16 新增（P4-3 口径）。

### 2.3 BJ14/BJ15 登记（不夸大）

- **BJ14**（bubble 主导 + text 并存形态）：rerun primary=6 + sfx=0（=qual 基线 6 speech）。sfx 通道全盲 → 第一层不可达；对位参照框的重叠 0.123（manga-3）/0.4287（manga-4）→ 即便召回恢复也在 0.90 域外 → 第二层不可达。bubble 主导形态在本仲裁语义下**不获得覆盖**（ogkalu 端无类面、重叠量不足，如实登记）。
- **BJ15**（结构性无载体）：rerun primary=7 + sfx=0；两个参照框与全部 7 个 ogkalu 候选**零相交**——仲裁两端永不相交，结构性不可达（与 AC2 预期登记一致）。

## 3. AC3：零变化回归

### 3.1 BJ06 detect 集合逐位对照

- composite 仲裁 **off vs on**：17 候选 = 17 候选，label/polygon/reading_order/confidence 全字段 **bit-identical=True**（options 仅 `sfx_arbitration` 登记值 on/off 之差，`raw/bj06-on-off-candidates.json` 全量落盘）。
- 真实 rerun（on）与 qual-BJ06 生产基线对位：**17 候选 = 17 region**（9 speech + 8 sfx）；8 个 sfx 候选 bbox 与 qual-BJ06 的 8 个 sfx region 对位；域内 sfx×primary 最大 IoU 0.8865 < 0.90（3 对相交全部安全）。
- BJ13/14/15 rerun 计数与 qual 基线对位：4/6/7 = 4/6/7。

### 3.2 KO 域证据（r2 P1-2）

DSH r1 要求的 KO qualification 家族（M2-TA3-B case-selection 的 10 个 KO case：K01 K02 K04 K05 K07 K08 K09 K10 K11 K19）detect 层全量扫描：production composite（ogkalu+chiqui7）每 case **off/on 各一次真实推理**（K01-K10 webtoon 长条走生产 tiling 路径，合计 ~700 tiles×2；K11/K19 paged）。**结果：10/10 off/on 候选指纹逐位一致（bit-identical=True）；全族 sfx×primary 相交对最高 IoU = 0.1325；0 对 ≥0.90——无 STOP 条件**。合计 1034 候选（off/on 各 1034），sfx 候选仅 1 个（K11，Pepper&Carrot 页），该 sfx 候选与同页 12 个 primary 候选的最高相交 IoU=0.1325——远低于 0.90 域（KO 域唯一的有 sfx 检出样本，其重叠形态落在保守域外，与 BJ13 同为部分重叠形）。

| case | tiling/tiles | off 候选 | on 候选 | 逐位一致 | sfx 候选 | sfx×primary 最高 IoU |
|---|---|---|---|---|---|---|
| K11 | off | 13 | 13 | True | 1 | 0.1325 |
| K19 | off | 0 | 0 | True | 0 | 0 |
| K01 | on/70 | 180 | 180 | True | 0 | 0 |
| K02 | on/21 | 93 | 93 | True | 0 | 0 |
| K04 | on/32 | 113 | 113 | True | 0 | 0 |
| K05 | on/52 | 62 | 62 | True | 0 | 0 |
| K07 | on/147 | 247 | 247 | True | 0 | 0 |
| K08 | on/58 | 60 | 60 | True | 0 | 0 |
| K09 | on/112 | 119 | 119 | True | 0 | 0 |
| K10 | on/113 | 147 | 147 | True | 0 | 0 |

（页面经 `experiments/M2-TA3-B/case-selection.json` 的 `page_path` 解析，主仓库旧路径回退 open-assets worktree 同尾路径并经 `page_sha256` 校验；逐 case 明细落 `raw/ko-scan/<case>.json`，运行日志 `raw/ko-scan-run.log`。K11 的存在把 KO 口径从「构造性恒等（sfx 全零）」升级为「真实 sfx 检出下的逐位一致 + 重叠上界实测 0.1325」。与 DETECT-EVAL「sfx 类 11/29 实例 @0.5」的差异：评测样本是人工框选的 SFX 实例帧，qualification 选取的 10 页 SFX 密度低——KO 域更高 SFX 密度页的 sfx×primary 重叠分布仍为开放项，登记为 KO 口径已知边界。）

### 3.3 第二道门量化评估（r2 P2-2，只评估不实施）

DSH r1 询问的第二道门「仅当 `sfx conf ≥ primary conf` 时才改标」与纯 IoU 门的差异，用本 Task 全部观测/合成对量化（conf 为生产 provider 原始输出值）：

| 相交对 | IoU | sfx conf | primary conf | sfx≥primary？ |
|---|---|---|---|---|
| BJ06 sfx-3 × manga-9（「！！！」双检出对） | 0.8864 | 0.9156 | 0.5379 | 是 |
| BJ06 sfx-7 × manga-2 | 0.8683 | 0.8170 | 0.6845 | 是 |
| BJ06 sfx-5 × manga-8 | 0.7270 | 0.9131 | 0.6049 | 是 |
| BJ13 口径 B 合成对 ×3（sfx-near1/2/3 conf 0.99） | ≥0.90 | 0.99 | 0.8636/0.8786/0.8173 | 是 ×3 |

**结论**：conf 门在现有全部 6 个对上 **6/6 通过——与纯 IoU 门零行为差异**，对域内安全（BJ06 3 对即使将来达 0.90 也会被 conf 门放行）与绿态闭环（口径 B 全通过）都**不提供任何增量保护**。「sfx conf < primary conf」的区分形态在观测中不存在（chiqui7 的 sfx 通道响应在其检出对象上恒高，0.72-0.94）。实施第二道门=纯行为面膨胀（当前无区分样本），**登记为未来切片候选**：仅当召回恢复 Task 后出现「sfx conf 弱于 primary conf 的 0.90+ 对」的新形态时再评估。

### 3.4 detect options 新键消费方审计（r2 P3-2，非 wire 证明）

`sfx_arbitration*` 键的完整数据流：

1. composite `detect` 构造 options 元组（`detection_sfx.py`）→ `DetectionResult.options`；
2. `handlers.handle_detect`：`provenance = detection.provenance()`（`handlers.py:285`，options 进入 provenance dict）→ `StepResult(outputs={"region_ids": ..., "detection": provenance})`（`handlers.py:308`）；
3. 持久化：`application/tasks/service.py:649` `step_run.output = result.outputs` → SQLite `step_runs.output_json`（审计行内 JSON，`schema.py:341`）；
4. **功能性读取方唯一**：`application/tasks/service.py:988` `result.outputs.get("region_ids")`——只读 `region_ids` 键；`detection` 子树（含全部 `sfx_arbitration*` 键）无任何代码路径消费；
5. IPC/契约面：`src-tauri/**` 无 step_runs/detect-options 读取；`doc/contracts/**` 无 step_runs 或 detect options 的 wire 契约（grep 零命中）。

审计结论：新键是 SQLite 审计行的死数据（audit-only），非 wire、非 IPC、非任何步骤间协议——AC5 零契约变化成立。

### 3.5 pytest 三套件（r2 重跑，显式 EXIT 码）

r2 对 src（P4-1 重命名）与 experiments（P4-2/P4-4）改动后全量重跑，日志首行显式落 pytest 退出码：

| 套件 | 命令 | 环境 | 结果 |
|---|---|---|---|
| 受影响面（P4-1 复验） | `python -m pytest tests/providers/test_detection_sfx.py -q -p no:cacheprovider` | 系统 python 3.14 | **38 passed**（含 15 仲裁用例） |
| providers + core + m2_acceptance | `"G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe" -m pytest tests/providers tests/core tests/m2_acceptance -q -p no:cacheprovider -rs`（bash `echo EXIT=$?` 显式落日志首行） | `G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312`（依赖矩阵全齐：pytest/numpy/PIL/cv2/onnxruntime/torch-CUDA不可用/PySide6） | **627 passed, 1 skipped, 0 failed, EXIT=0**（`raw/pytest-three-suites-r2.log`，首行 `EXIT=0`） |
| 全量 tests/ | 同 venv，`-m pytest tests -q -p no:cacheprovider -rs` | 同上 | 1731 passed, 1 skipped, **1 failed, EXIT=1**（`raw/pytest-full-suite-r2.log`）——唯一失败 `tests/m2_test_assets/test_catalog.py::test_manifest_has_unique_cases_and_exact_taxonomy` 断言本地 gitignored 素材 manifest 的 case 计数 97 vs 实际 100，纯本地素材状态（前序素材 Task 在本机注册过新增 case），与本 Task 改动面（`detection_sfx.py` + `tests/providers|core`）零交集，且该目录不属于三套件基线口径 |

- 基线口径：611 passed + 1 skipped（Task 合同基线）；本次 627+1 = 628 collected，差 **+16 恰为本 Task 新增用例**（P4-3 口径：15 个仲裁用例 = 14 红 + 1 现状锚点绿（实现前即 passed 的降级路径锚点），含 7 组 env 参数化；另有 1 个 `sfx-arb-` 分发矩阵参数化行）——零既有用例回退。
- env off 回退路径复验（r2 附带）：KO 扫描（§3.2）每 case 的 off 跑即 `NEWMANGA_SFX_ARBITRATION=off` 下的真实 composite 行为，10/10 与 on 逐位一致——回退语义在 r2 再次实证（BJ06 双跑之外新增 10 case）。
- 环境注记：`T1.1.1-gpu-py312`（带 CUDA torch）跑同三套件为 6 failed/619 passed——6 个失败逐名与分类（P3-3）：
  | # | 失败测试 | 原因分类 |
  |---|---|---|
  | 1 | `tests/providers/test_bootstrap_providers.py::test_production_stack_starts_without_heavy_runtimes` | 环境依赖面：该 venv 装有 manga-ocr 等 heavy 依赖 → provider registry 状态非 `missing_dependency`，断言（按「无 heavy runtime」环境写定）失效 |
  | 2 | `tests/providers/test_detection_sfx.py::test_real_weights_reproduce_eval_payload[rgb24]` | 环境依赖面：venv 缺 onnxruntime（REAL_SKIP 守卫只查权重/帧文件存在，不查 runtime 可导入），真实推理无法启动 |
  | 3 | `tests/providers/test_detection_sfx.py::test_real_weights_reproduce_eval_payload[rgb32]` | 同上 |
  | 4 | `tests/providers/test_detection_sfx.py::test_real_weights_blank_page_structurally_valid` | 同上 |
  | 5 | `tests/providers/test_devices.py::test_gpu_is_unavailable_without_a_runtime_but_reported_not_invented` | 环境依赖面：venv 的 torch 带 CUDA → `gpu_info` 非 `unavailable`，「无 GPU runtime」断言失效 |
  | 6 | `tests/providers/test_devices.py::test_cpu_fallback_only_when_the_provider_declares_it` | 同上（`plan()` 依赖同一 gpu_info 状态） |
  六者全部为 **venv 依赖面与测试环境假设不匹配**，与本 Task 改动零因果（同一 venv 在 base `eb7cd15e` 上同样失败——失败面测试文件均不在本 Task diff 内）。collect 差异解释：系统 python 3.14 缺 PySide6 → 4 个 import `bootstrap.app`（顶层 `from PySide6.QtCore import ...`）的 core 测试文件**收集期** ImportError（`test_page_catalog_modes/test_pipeline_defaults_assembly/test_pipeline_defaults_service/test_transport_credential_assembly`）；两个 py312 venv 有 PySide6 → 收集成功。判定以 T1.1.1-impl-py312 EXIT=0 为准。
- cargo/vitest：本 Task 零 Rust/前端改动面（`git diff --stat` 仅 `src/infrastructure/providers/detection_sfx.py` + `tests/**` + experiments/verification 本 Task 目录），声明零改动面，集成方复跑。

## 4. AC4：边界与 fail-closed（实现证据）

- 空/非法 env typed 拒绝：7 组参数化用例（两 env 的空串/未知词/非数字/0/1.5/负数）+「primary 未被调用」探针用例，全部绿。
- 默认值冻结与依据：§1.4（BJ06 域内最高 0.8862 之上的保守域）。
- 不可达形态 typed 可诊断：§1.6 四字段 + BJ13/口径 A 的实际读数。

## 5. AC5：契约边界

- `doc/contracts/**` 零 diff；RegionInput/provider 契约零变化——仲裁在 core 内部 detect 链（composite 输出侧），IPC wire shape 不变。
- handlers `region_creator` 五参签名、core_assembly `_create_detected_region` 闭包、`_detected_region_type` 分发矩阵逻辑全部零改动（仅测试矩阵加锚定行）。
- **未触发停等**：实现全程未触碰契约面，无需契约修订请求。

## 6. 与 M2-SFX-MISROUTE-UI-MITIGATION 的对齐注记（接口预留，Task 风险②）

- 本仲裁只产生**确定态改标**（`sfx-arb-` → RegionType.SFX → SfxPolicy 门），不新增 region 级「疑似」字段（零契约面纪律）；UI 缓解 Task 的「改标后确定态」形态与本 Task 输出兼容。
- 「改标前疑似警示」所需的数据基础本 Task **无产出**——保守域外的不可达形态（含 BJ13 真实形态）只有 detect options 审计字段（`sfx_arbitration_partial_overlap` 等），不在 region 级契约上。UI 侧「疑似警示」若需 region 级信号，属未来契约修订候选（沿该 Task AC3 的登记路径），本 Task 不 widening。
- 建议编排/Codex 将本注记转写入 M2-SFX-MISROUTE-UI-MITIGATION Task 文件（其文件属他人 Task 产物，本 Task 不直接改写）。

## 7. 证据物索引

| 证据物 | 位置 |
|---|---|
| 实验脚本（BJ rerun + 合成口径 + 零变化对照） | `experiments/M2-REGION-OVERLAP-ARBITRATION/arbitrate_bj13.py` |
| 实验脚本（KO 10 case off/on 扫描，r2 P1-2） | `experiments/M2-REGION-OVERLAP-ARBITRATION/ko_iou_scan.py` |
| 四页 rerun 全候选 dump + 参照框对位 + 阈值校准读数 | `raw/arbitrate-pages.json` |
| 实验 manifest（权重/env 默认/合成口径/BJ06 零变化判定） | `raw/arbitrate-manifest.json` |
| BJ06 off/on 全候选指纹（逐位对照物） | `raw/bj06-on-off-candidates.json` |
| BJ/KO rerun 运行日志 | `raw/arbitrate-run.log`、`raw/ko-scan-run.log` |
| KO 逐 case 明细（r2 P1-2） | `raw/ko-scan/<case>.json` ×10、`raw/ko-scan/summary.json` |
| 红态测试日志（14 failed，实现前） | `raw/red-phase-arbitration-tests.log` |
| 三套件日志（r2 重跑，显式 EXIT=0） | `raw/pytest-three-suites-r2.log`；全量 `raw/pytest-full-suite-r2.log`；环境对照 `raw/pytest-t111-py312.log`、r1 版 `raw/pytest-three-suites.log`/`raw/pytest-full-suite.log` |
| 实现主体 | `src/infrastructure/providers/detection_sfx.py`（`_arbitration_config`/`_bbox_iou`/composite 仲裁段）@ `b27c826f`，r2 重命名收尾 commit |
| 测试 | `tests/providers/test_detection_sfx.py`（仲裁段）、`tests/core/test_sfx_assembly.py`（分发矩阵锚定行） |
| 上游证据输入（只读引用） | `verification/M2-SFX-E2E-MATERIAL/sfx-detect-diagnosis.json`、`bj06-run/summaries/qual-BJ06.json`、`new-assets-run/summaries/qual-BJ1{3,4,5}.json`、`verification/M2-SFX-DETECT-DOMAIN-EXT-DIAG/{diagnosis-and-options.md,raw/l1-fullpage-conf-scan.json}`、`experiments/M2-TA3-B/case-selection.json`（KO page_path 解析先例） |

复现（worktree 根目录；页面图像为 gitignored 只读引用，输出全落本 Task 目录）：

```bash
"G:/CODEX/New Manga.task-envs/M2-TA3-B-ocr/Scripts/python.exe" \
  experiments/M2-REGION-OVERLAP-ARBITRATION/arbitrate_bj13.py
# 期望：BJ13 primary=3 sfx=1 arb=on relabels=None partial=None；
# BJ14 6/0；BJ15 7/0；BJ06 9/8 partial=0.8865；BJ06 off/on identical=True
"G:/CODEX/New Manga.task-envs/M2-TA3-B-ocr/Scripts/python.exe" \
  experiments/M2-REGION-OVERLAP-ARBITRATION/ko_iou_scan.py
# 期望：10 case 全部 identical=True；K11 sfx=1 max_iou=0.1325；无 STOP 行
"G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe" \
  -m pytest tests/providers tests/core tests/m2_acceptance -q -p no:cacheprovider -rs
# 期望：627 passed, 1 skipped, EXIT=0
```

## 8. Known limitations（引用本报告时不得省略）

1. **directional**：真实 rerun BJ 4 页 + KO 10 case + 既有 raw 校准；无 SFX GT（参照框为目检近似框）；形态级闭环的 sfx 侧为合成候选（现状权重对 BJ 域 sfx 零召回是已判定的域外根因，非本 Task 范围）。
2. **仲裁对 BJ13 误路由现状不可达（双层，编排裁决 (a) 修订口径的核心登记）**：这是证据定案而非缺陷隐瞒——域内/域外重叠反向不可分离（§0 结构性结论）意味着**任何**几何重叠阈值都无法在零变化约束下闭合 BJ13；BJ13 的自动化闭合路径 = sfx 召回恢复（域外根因 Task）之后按未来形态重新校准（env 旋钮已预留，重校准是新证据切片）。本仲裁在召回恢复前对 BJ13 形态 no-op。
3. **0.90 域的语义与脆弱性**：语义是「近重复双检出的类型仲裁」；真实 0.90+ 形态至今 **0 观测**（BJ 4 页 + KO 10 case 全部真实候选对）。margin 仅 0.0135/0.0138 且内含形（IoU 理论上界 1.0）可击穿任何有限阈值、参照框不确定度传播 ±0.03-0.05 大于任何 margin（§1.3.2）——0.90 的安全性=观测经验+AC3 经验回归（BJ06+KO off/on 逐位一致），**非几何保证**；重审条件已挂召回恢复 Task。
4. 参照框近似性（±10-20px）影响 IoU 边缘读数（如 0.8865 vs 0.8862 的口径差、0.490 vs 0.452 的跨框源差），不影响量级判定（§1.4 跨口径登记）。
5. rerun 为 CPU 路径（ogkalu transformers/torch CPU + chiqui7 onnxruntime CPU），与生产 GPU 路径的数值差异未测（沿 DOMAIN-EXT-DIAG limitation 7 口径）；BJ06/KO rerun 与 qual 基线的对位为计数/结构对位 + 亚像素级 bbox 差。
6. `arbitrate-pages.json` 的 `reference_overlap[].best_primary_label` 在本 Task raw 中曾以 `0.0` 填充零相交行（r1 脚本），r2 脚本已改为显式 `null`（P4-4）；r1 raw 未重生成，读数以 `best_iou` 为准。
7. detect options 尾部新增 2-4 个审计键（`sfx_arbitration*`）——经消费方审计（§3.4）确认为 SQLite `step_runs.output_json` 审计面死数据，非 wire、非 IPC、无功能性读取方（AC5 口径内）。
8. KO 口径边界：10 个 qualification 页 SFX 密度低（sfx 候选仅 K11 一枚）；更高 SFX 密度 KO 页（DETECT-EVAL 评测样本型）的 sfx×primary 重叠分布未覆盖。
9. 全量 pytest 的 1 个环境性失败（本地素材计数，§3.5）在本机长期存在，与本 Task 零因果；处置建议见 Handoff 风险项。

## 9. DSH r1 闭合对照（r2 返修记录）

DSH r1（2026-10-04，非作者）：verdict=`changes_requested`（0×P0；3×P1+5×P2+4×P3+4×P4）。DSH 确认：不可达性论证**物理成立**（0.8862/0.870/0.728/0.5501/0.4903 手算溯源吻合）、实现工艺与范围纪律良好（AC1/AC4/AC5 PASS、AC3 大部分 PASS）；争议集中在合同层。编排方裁决：P1-1 采纳选项 (a)（AC2 修订为「结构性不可达登记 + 近重复双检出形态级闭环」），其余按 DSH 建议执行。逐条处置（本版全部闭合，零实验重跑除 KO 新增扫描与三套件复验）：

| 编号 | DSH 发现 | 处置 | 落点 |
|---|---|---|---|
| P1-1 | AC2 交付表述超出裁决③授权语境（BJ13 红转绿在现状权重下物理不可达，合同层口径未预修订） | 采纳编排裁决 (a)：Task AC2 修订为「结构性不可达登记 + 近重复双检出形态级闭环」（标注裁决日期+两行依据）；「可观察交付」段同步改写；依赖链注记（召回恢复 Task 前 no-op）；§0 表述改实 | Task 文件 AC2/目标段/依赖段；本报告 §0/§2.2 |
| P1-2 | KO 域证据缺失（零变化回归仅 BJ06 单域） | **新增 KO 10 case detect 层 off/on 双真实推理扫描**：10/10 逐位一致、最高 IoU 0.1325（K11）、0 对 ≥0.90、无 STOP 条件 | 本报告 §3.2；`raw/ko-scan/`、`raw/ko-scan-run.log`；`experiments/M2-REGION-OVERLAP-ARBITRATION/ko_iou_scan.py`；Task 测试表新行 |
| P1-3 | 口径 B 表述近似「真实绿态」，需降级为代码级验证 + 真实发生面登记 | §2.2 改述「实现路径验证（代码级）」；登记「真实 0.90+ 形态至今 0 观测（BJ 4 页 22×25 候选对 + KO 10 case）」 | 本报告 §0/§2.2/§8.3 |
| P2-1 | 绿态「不再乱译」语义缺策略前提 | 登记绿态成立条件=`sfx.policy=skip`（默认）+ qual-BJ06 translate 配置下 8 sfx region 全走 SFX 翻译链的门消费实测 + translate 残余损害未评估限定 | 本报告 §2.2 |
| P2-2 | 第二道门（sfx conf ≥ primary conf）未评估 | **只评估不实施**：全部 6 个相交对（BJ06 真实 3 + BJ13 合成 3）的双方 conf 列表化，conf 门 6/6 通过=与纯 IoU 门零行为差异；未来切片候选登记 | 本报告 §3.3 |
| P2-3 | 「同位置双 SFX region」未论证 | 四点选型论证（零损害/最小行为面/零观测/可逆）+ 副作用登记（计数膨胀/UI 重叠展示/OCR 双跑）+ 未来去重切片候选 | 本报告 §1.3.1 |
| P2-4 | margin 0.0138 薄弱性与内含形敏感性未登记 | 登记 margin 两口径（0.0135/0.0138）、域内已观测完全包含形（IoU=面积比，上界 1.0 可击穿任何有限阈值） | 本报告 §1.3.2/§8.3 |
| P2-5 | 跨口径比较（qual/rerun/E2E 三框源）性质未标注 | 登记三口径读数差 0.0003-0.06、量级结论跨口径稳定、第二位小数级论证不得跨口径引用 | 本报告 §1.4 |
| P3-1 | 三套件日志未显式落 EXIT 码；src/experiments 改动后需复验 | r2 重跑（P4 改动后）显式落 `EXIT=0`；env off 回退复验=BJ06+KO 11 次真实 off 跑逐位一致 | 本报告 §3.5；`raw/pytest-three-suites-r2.log`、`raw/pytest-full-suite-r2.log` |
| P3-2 | options 新键缺消费方审计 | 五步数据流审计：唯一功能性读取=`outputs.get("region_ids")`；`detection` 子树仅落 `step_runs.output_json` 审计行；Tauri/契约零消费 → 非 wire | 本报告 §3.4 |
| P3-3 | T1.1.1-gpu-py312 的 6 失败未逐名解释 | 逐名表（6 项全部 venv 依赖面与测试假设不匹配，与本 Task 零因果）+ collect 差异解释（PySide6 缺失致 4 文件收集期失败） | 本报告 §3.5 |
| P3-4 | 分离带在参照框不确定度内的量化否决 | 量化登记：margin（0.0135/0.0138）与任何声称的分离带均 < 参照框 ±10-20px 不确定度传播（±0.03-0.05）→ 「安全分离带」论证否决；安全性唯一支撑=观测样本+AC3 经验回归 | 本报告 §1.3.2 |
| P4-1 | 局部变量 `arbitratedRoute` 命名不当 | 改 `arbitrated_candidates`（src），受影响测试重跑 38 passed | `detection_sfx.py`；§3.5 r2 复验 |
| P4-2 | experiments 死参数 `extra`、两口径共享可变实例 | 删 `extra` 存储；口径 A/B 各用独立 composite 实例 | `arbitrate_bj13.py` |
| P4-3 | 用例计数口径混乱（「14 个测试全红」与 degraded 现状锚点矛盾） | 统一为「15 用例（14 红 + 1 现状锚点绿）+1 分发矩阵行=16 新增」 | 本报告 §2.2/§3.5 |
| P4-4 | `best_primary_label` 零相交填 `0.0` | r2 脚本改显式 `null`；r1 raw 不重生成、读数口径登记 Known limitations 6 | `arbitrate_bj13.py`；本报告 §8.6 |

**程序瑕疵登记**：Owner 在 claim/实施时未就「AC2 的真实达成口径受域外根因约束」预提交范围修订请求（DSH r1 程序层依据 3）——由编排裁决 (a) 事后授权补正，登记不再追责。
