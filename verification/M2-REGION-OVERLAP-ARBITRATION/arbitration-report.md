# M2-REGION-OVERLAP-ARBITRATION：region 创建跨 provider 重叠仲裁 — 仲裁报告（r1）

- Task：[M2-REGION-OVERLAP-ARBITRATION](../../doc/tasks/M2-REGION-OVERLAP-ARBITRATION.md) · 分支 `agent/zcode/M2-REGION-OVERLAP-ARBITRATION` · base=`eb7cd15e`（claim=`8c74d170`，实现主体=`b27c826f`）· 日期 2026-10-03
- Owner=ZCode · Reviewer=DeepSeek Harness（非作者）· Integrator=编排会话代行 Codex（用户全权授权+自治授权）
- 授权：用户裁决 2026-10-04「按推荐」裁决③（重叠仲裁契约授权）
- **证据强度裁定（全程适用）**：全部结论为 **directional**——阈值校准基于既有 raw（qual-BJ06/BJ13/BJ14/BJ15 生产 run + DOMAIN-EXT-DIAG L1 扫描 + E2E 相交枚举）+ 本 Task 一次真实 rerun（BJ13/14/15/BJ06 四页，ogkalu+chiqui7 生产双 provider，权重 sha256 pin 校验通过）；绿态闭环含合成 sfx 候选口径（现状权重对 BJ 域 sfx 零召回，DOMAIN-EXT-DIAG 已判定为域外根因，禁改面）。单 AI 标注者参照框（±10-20px）沿用上游口径。

## 0. 结论速览

| AC | 判定 | 一行结论 |
|---|---|---|
| AC1 仲裁语义提案 | **DELIVERED（证据定案）** | 层位=provider 拼接层（composite）；度量=bbox IoU；规则=sfx 候选驱动的 directional 改标（`sfx-`→`sfx-arb-<原label>`）；冻结阈值 **0.90**；env `NEWMANGA_SFX_ARBITRATION[_IOU]` typed 旋钮 |
| AC2 红绿判别 | **DELIVERED（红态真实 rerun + 绿态合成口径，不可达面如实登记）** | BJ13 红态真实对位（manga-1/manga-3=qual region#1/#3 乱译路径）；现状权重下仲裁不可达（sfx 通道零候选）；召回恢复近重复形态（口径 B）3/3 改标落 RegionType.SFX；BJ13 参照框口径（A）partial 0.5501 诊断不迁移；BJ14/15 不可达如实登记 |
| AC3 零变化回归 | **DELIVERED** | BJ06 仲裁 off/on 候选集合逐位一致（17=17，bit-identical=True）；真实 rerun 与 qual-BJ06 生产基线 17 region（9 speech+8 sfx）对位；BJ13/14/15 计数对位 4/6/7；pytest 三套件 **627 passed + 1 skipped，0 failed，EXIT=0**（基线 611+1sk + 本 Task 16 新用例 = 628，精确吻合）；cargo/vitest 零改动面（集成方复跑） |
| AC4 边界与 fail-closed | **DELIVERED** | 双 env 空值/非法值 fail-fast `ValueError` naming the variable（TILING 先例，detect 入口解析，非法时 primary 不运行）；默认冻结（on + 0.90）并记录依据；不可达形态 typed 可诊断（`sfx_arbitration_partial_overlap` / `sfx_candidates=0`） |
| AC5 契约边界 | **DELIVERED（零 wire 变化）** | `doc/contracts/**`、RegionInput wire shape、handlers `region_creator` 签名、core_assembly 分发矩阵全部零改动；改标仅复用既有 `startswith("sfx-")` label 契约（分发矩阵新增 `sfx-arb-` 行锚定，行为在 base 上已成立） |

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

### 2.2 绿态（合成召回恢复口径，真实候选集零推理重放）

| 口径 | 注入 | 结果 | 判定 |
|---|---|---|---|
| **口径 A：目检参照框 = 召回恢复的 sfx 候选** | 2 个参照框 sfx 候选 | 不改标；`sfx_arbitration_partial_overlap=0.5501` 诊断登记 | **诚实不可达（第二层：即便召回恢复，0.49-0.55 仍在保守域外）**——不伪造覆盖 |
| **口径 B：近重复双检出（0.90 域的设计目标形态）** | 3 个与 manga 候选 ~0.95 缩放共位的 sfx 候选（IoU≥0.9） | `sfx-arb-manga-1/2/3` 全部改标（relabels=3）；生产分发函数逐候选判定 `region_type="sfx"` ×3 | **绿态闭环**：改标 → RegionType.SFX → SfxPolicy 门接管，原 SPEECH 乱译路径在该形态下不再发生 |

单元级先红后绿：14 个仲裁测试在实现前全红（`raw/red-phase-arbitration-tests.log`，pytest EXIT=1），实现后转绿（b27c826f）。

### 2.3 BJ14/BJ15 登记（不夸大）

- **BJ14**（bubble 主导 + text 并存形态）：rerun primary=6 + sfx=0（=qual 基线 6 speech）。sfx 通道全盲 → 第一层不可达；对位参照框的重叠 0.123（manga-3）/0.4287（manga-4）→ 即便召回恢复也在 0.90 域外 → 第二层不可达。bubble 主导形态在本仲裁语义下**不获得覆盖**（ogkalu 端无类面、重叠量不足，如实登记）。
- **BJ15**（结构性无载体）：rerun primary=7 + sfx=0；两个参照框与全部 7 个 ogkalu 候选**零相交**——仲裁两端永不相交，结构性不可达（与 AC2 预期登记一致）。

## 3. AC3：零变化回归

### 3.1 BJ06 detect 集合逐位对照

- composite 仲裁 **off vs on**：17 候选 = 17 候选，label/polygon/reading_order/confidence 全字段 **bit-identical=True**（options 仅 `sfx_arbitration` 登记值 on/off 之差，`raw/bj06-on-off-candidates.json` 全量落盘）。
- 真实 rerun（on）与 qual-BJ06 生产基线对位：**17 候选 = 17 region**（9 speech + 8 sfx）；8 个 sfx 候选 bbox 与 qual-BJ06 的 8 个 sfx region 对位；域内 sfx×primary 最大 IoU 0.8865 < 0.90（3 对相交全部安全）。
- BJ13/14/15 rerun 计数与 qual 基线对位：4/6/7 = 4/6/7。

### 3.2 pytest 三套件

| 套件 | 命令 | 环境 | 结果 |
|---|---|---|---|
| providers + core + m2_acceptance | `<venv>/Scripts/python.exe -m pytest tests/providers tests/core tests/m2_acceptance -q -p no:cacheprovider -rs` | `G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312`（依赖矩阵全齐：pytest/numpy/PIL/cv2/onnxruntime/torch-CUDA不可用/PySide6） | **627 passed, 1 skipped, 0 failed, EXIT=0**（`raw/pytest-three-suites.log`） |
| 全量 tests/ | 同 venv，`-m pytest tests -q -p no:cacheprovider -rs` | 同上 | 1731 passed, 1 skipped, **1 failed**（`raw/pytest-full-suite.log`）——唯一失败 `tests/m2_test_assets/test_catalog.py::test_manifest_has_unique_cases_and_exact_taxonomy` 断言本地 gitignored 素材 manifest 的 case 计数 97 vs 实际 100，纯本地素材状态（前序素材 Task 在本机注册过新增 case），与本 Task 改动面（`detection_sfx.py` + `tests/providers|core`）零交集，且该目录不属于三套件基线口径 |

- 基线口径：611 passed + 1 skipped（Task 合同基线）；本次 627+1 = 628 collected，差 **+16 恰为本 Task 新增用例**（15 个仲裁用例含 7 组 env 参数化 + 1 个 `sfx-arb-` 分发矩阵行）——零既有用例回退。
- 环境注记：`T1.1.1-gpu-py312`（带 CUDA torch）跑同三套件为 6 failed/619 passed——6 个失败全是该 venv 的依赖面与测试假设不匹配（GPU torch 存在使 `test_devices` 的 GPU-unavailable 断言失败、onnxruntime 缺失使 real-weights 面失败），非本 Task 改动引入（日志 `raw/pytest-t111-py312.log` 留档对照）；最终判定以 `T1.1.1-impl-py312`（无 CUDA）的 EXIT=0 为准。
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
| 实验脚本（真实 rerun + 合成口径 + 零变化对照） | `experiments/M2-REGION-OVERLAP-ARBITRATION/arbitrate_bj13.py` |
| 四页 rerun 全候选 dump + 参照框对位 + 阈值校准读数 | `raw/arbitrate-pages.json` |
| 实验 manifest（权重/env 默认/合成口径/BJ06 零变化判定） | `raw/arbitrate-manifest.json` |
| BJ06 off/on 全候选指纹（逐位对照物） | `raw/bj06-on-off-candidates.json` |
| 真实 rerun 运行日志 | `raw/arbitrate-run.log` |
| 红态测试日志（14 failed，实现前） | `raw/red-phase-arbitration-tests.log` |
| 三套件日志（627+1sk EXIT=0） | `raw/pytest-three-suites.log`；全量 `raw/pytest-full-suite.log`；环境对照 `raw/pytest-t111-py312.log` |
| 实现主体 | `src/infrastructure/providers/detection_sfx.py`（`_arbitration_config`/`_bbox_iou`/composite 仲裁段）@ `b27c826f` |
| 测试 | `tests/providers/test_detection_sfx.py`（仲裁段）、`tests/core/test_sfx_assembly.py`（分发矩阵锚定行） |
| 上游证据输入（只读引用） | `verification/M2-SFX-E2E-MATERIAL/sfx-detect-diagnosis.json`、`bj06-run/summaries/qual-BJ06.json`、`new-assets-run/summaries/qual-BJ1{3,4,5}.json`、`verification/M2-SFX-DETECT-DOMAIN-EXT-DIAG/{diagnosis-and-options.md,raw/l1-fullpage-conf-scan.json}` |

复现（worktree 根目录；页面图像为 gitignored 只读引用，输出全落本 Task 目录）：

```bash
"G:/CODEX/New Manga.task-envs/M2-TA3-B-ocr/Scripts/python.exe" \
  experiments/M2-REGION-OVERLAP-ARBITRATION/arbitrate_bj13.py
# 期望：BJ13 primary=3 sfx=1 arb=on relabels=None partial=None；
# BJ14 6/0；BJ15 7/0；BJ06 9/8 partial=0.8865；BJ06 off/on identical=True
"G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe" \
  -m pytest tests/providers tests/core tests/m2_acceptance -q -p no:cacheprovider -rs
# 期望：627 passed, 1 skipped, EXIT=0
```

## 8. Known limitations（引用本报告时不得省略）

1. **directional**：真实 rerun 4 页 + 既有 raw 校准；无 SFX GT（参照框为目检近似框）；绿态闭环的 sfx 侧为合成候选（现状权重对 BJ 域 sfx 零召回是已判定的域外根因，非本 Task 范围）。
2. **仲裁对 BJ13 误路由现状不可达**（双层）：这是证据定案而非缺陷隐瞒——域内/域外重叠反向不可分离（§0 结构性结论）意味着**任何**几何重叠阈值都无法在零变化约束下闭合 BJ13；BJ13 的自动化闭合路径 = sfx 召回恢复（域外根因 Task）之后按未来形态重新校准（env 旋钮已预留，重校准是新证据切片）。
3. 0.90 域的语义是「近重复双检出的类型仲裁」（当前唯一有真实发生面的形态：BJ06 域内 0.886 对在 0.90 之下不触发，故现状生产行为零变化）；「近重复双检出改标 sfx」在域内若未来出现 0.90+ 的对白/真 sfx 对，将按设计改标进 SfxPolicy 门（SKIP 默认，不渲染乱译，人工可逆）——该形态至今 0 观测。
4. 参照框近似性（±10-20px）影响 IoU 边缘读数（如 0.8865 vs 0.8862 的口径差），不影响量级判定。
5. rerun 为 CPU 路径（ogkalu transformers/torch CPU + chiqui7 onnxruntime CPU），与生产 GPU 路径的数值差异未测（沿 DOMAIN-EXT-DIAG limitation 7 口径）；BJ06 rerun 与 qual 基线的对位为计数/结构对位 + 亚像素级 bbox 差。
6. `arbitrate-pages.json` 的 `reference_overlap[].best_primary_label` 在零相交时填 `0.0` 而非 null（脚本 `best[0] and best[1]` 惯性），`best_iou` 数值为准；不影响任何判定。
7. detect options 尾部新增 2-4 个审计键（`sfx_arbitration*`）——provenance/审计面增益，非 wire 契约（AC5 口径内）；既有消费方按 dict 读取不受影响（三套件全绿佐证）。
