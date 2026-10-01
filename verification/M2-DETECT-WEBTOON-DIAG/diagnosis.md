# M2-DETECT-WEBTOON-DIAG：ogkalu 对 webtoon 长条漫 0 候选——适配器级诊断报告

- Task: `M2-DETECT-WEBTOON-DIAG`（kind: diagnosis；owner: ZCode；reviewer: DeepSeek Harness 非作者）
- 分支 / worktree: `agent/zcode/M2-DETECT-WEBTOON-DIAG` @ `G:/CODEX/New Manga.worktrees/M2-DETECT-WEBTOON-DIAG-zcode`
- base: `8e0de8d0`；探针脚本: [diagnose_webtoon_detect.py](../../experiments/M2-DETECT-WEBTOON-DIAG/diagnose_webtoon_detect.py)
- raw 数据: [probe-results.json](probe-results.json)（探针 schema v2，含 AC1 可观测值、AC2 tile 实验全量数据、pre/post-NMS 全量框坐标与重叠带统计；v1 @ git `b311f52f` 可对比）
- 纪律声明: **零 `src/**`/`tests/**` 改动**；生产 provider 直接 import 构造；权重三文件 sha256 与生产 pin 全部匹配（probe-results.json `weights.all_pins_match=true`）；tile 图块仅驻留内存，无任何像素/权重入库。
- 结论性质: **directional**（n=3 整页探针 + n=1 页 tile 实验，CPU 单环境），不构成 qualification。

---

## 1. 判定（AC2）

> **判定：整页重缩放致目标消失（whole-page downscale destroys the targets）成立，置信度高。**
> ogkalu RT-DETR-v2 权重对 webtoon 内容本身有充分判别力；0 候选唯一来自生产推理路径把 690×62133 的整页无 padding 各向异性压缩到 640×640（垂直 ~97×），气泡/文字在垂直方向退化为亚像素结构，300 个 query 的 sigmoid 分数整体塌陷到 0.3 以下，在生产阈值 0.5 处为空集。同一页仅改送入单次推理的像素预算（1024×1024 块级推理，并由此消除各向异性拉伸）即从 **0 个 ≥0.5 文本框恢复到 193 个跨块去重文本框（合并前口径，conf max 0.967）**。

## 2. 证据链

### 2.1 生产路径结构（只读参考，非本任务改动）

`src/infrastructure/providers/detection_manga.py` 的 `_detect_text_boxes`（生产推理序列）把整页 RGB 直传 `processor(images=rgb, return_tensors="pt")`，**无任何 size 覆盖**。权重目录 `preprocessor_config.json`（sha256 pin 匹配）：

| 字段 | 值 | 含义 |
|---|---|---|
| `image_processor_type` | `RTDetrImageProcessor` | — |
| `size` | `{height: 640, width: 640}` | 重缩放目标 |
| `do_resize` | `true` | 启用 resize |
| `do_pad` / `pad_size` | `false` / `null` | **无 letterbox/padding 路径** → 各向异性拉伸 |

即任何输入都被无保比例地压到 640×640。该 config 无 `shortest_edge` 字段（`RTDetrImageProcessor` 走显式 `size` 路径）——r1 返修后探针 keep 白名单已收录该键，schema v2 JSON 的 `preprocessor_config` 中无此键即其不存在的直接证据（v1 白名单未含该键，当时只能推断、无法由 JSON 证明）。

### 2.2 AC1 可观测值：整页探针（K01/K02/K04 + BJ02 对照）

原始数字见 probe-results.json `pages.*`，摘录：

| 页 | 尺寸 W×H | 垂直压缩比 | provider region | raw score_max | raw ≥0.3 / ≥0.1 | 判读 |
|---|---|---|---|---|---|---|
| K01 | 690×62133 | **97.1×** | 0 | 0.2045 | 0 / 7 | 分数塌陷 |
| K02 | 600×18401 | 28.8× | 0 | 0.1666 | 0 / 4 | 分数塌陷 |
| K04 | 690×28156 | 44.0× | 0 | 0.2835 | 0 / 14 | 分数塌陷 |
| BJ02（对照） | 2946×4167 | 6.5× | **5**（bubble 丢弃 5） | **0.9721** | 10 / 14 | 正常 |

四点测量自洽性（排除探针伪影）：

1. **模型输入形状**：四页（含 K01 的 62133px 原始高度）的 `model_input_shape` 均为 `[1,3,640,640]`——整页重缩放是物理事实，不是假设。
2. **输出管线正常**：`logits_shape=[1,300,3]`，K01 在 ≥0.01 有 143 个 query——模型"看到了什么"但远不构成检出；这是重缩放伪影的典型形态，而非输入 decode 崩溃（否则应为全零/异常）。（r1 更正：v1 版此处曾引 `counts_ge["0.0"]=300` 佐证"全部有非零分数"——sigmoid 输出恒 ≥0，该计数恒真、无证据价值，已删除。）
3. **手工归约与官方后处理交叉一致**：探针用 sigmoid→per-query max 的全分布与 `post_process_object_detection(threshold=0.5)` 双路统计，`official_post_process_ge_0_5` 与手工 ≥0.5 计数在四页全部相等（webtoon 页 0=0，BJ02 10=10）——测量方法自洽。（r1 注：webtoon 三页为 0=0 平凡相等——阈值 0.5 处本无检出，非平凡核对仅 BJ02 10=10 一页；塌陷页的归约正确性由 BJ02 的非零路径背书，属间接证据。）
4. **对照页自检通过**：BJ02 同探针、同权重、同阈值路径检出 10 个 ≥0.5（provider 文本类过滤后 5 region，conf 0.937–0.972）——探针本身在常规页行为正常（AC1 自检条件）。

同页 docTR 对照（背景证据，非本任务产出）：TA3-A `verification/M2-TA3-A/summaries/smoke-K01.json`，detector=`doctr-fast_base-pinned`，`region_count=15`，`source_sha256=600ca755…` 与本探针 K01 逐字节同页。（注：15 是 docTR 路径**生产合并后 region 数**，与本实验的合并前文本框计数层级不同，见 §2.3。）

### 2.3 AC2 块级实验（tiling 可行性的直接证据）

设计：K01 裁成 1024×1024 块（任务书 AC2 指定）、垂直重叠 128px（**实验自选**——任务书只规定 1024×1024、未规定重叠带宽；理由=RT-DETR stride 32 的整数倍，占块高 12.5%）；宽 690<1024 右侧以常量灰 114 pad 到方形（惯例检测填充值，无上游引用；pad 无文字内容，回映后按"中心点落入 pad 区"丢弃）；每块走与生产逐字节相同的推理序列（同 processor、同 pin 权重、同阈值 0.5、同文本类过滤 `(1,2)`；**不含**生产 `cluster_words_into_blocks` 合并步）；块内检出按 `y+origin` 回映到页坐标，页级做置信度序贪心 NMS（IoU≤0.5）去重。r1 返修（schema v2）已把 pre/post-NMS 全量框坐标、NMS 删除决策与重叠带统计落盘并 CPU 复跑：226/193 及全部四页分布精确复现（elapsed 19793→19811 ms）。

结果（probe-results.json `pages.K01.tile_experiment`）：

| 指标 | 值 |
|---|---|
| 块数 | 70（含尾块 crop_h=309） |
| 总耗时（CPU，含推理+回映+NMS） | 19811 ms（v1 复跑前 19793 ms；≈283 ms/块） |
| 原始检出 → 回映 → 去重（**合并前文本框口径**） | 226 → 226（pad 区丢弃 0） → **193**（NMS 删除 33，逐框决策已落盘） |
| 去重后 conf | max **0.9666** / mean 0.8503 / min 0.5009 |
| 去重后几何 | median box 144.1×53.6 px；y 范围 **156.7–62008.9**（覆盖全页 62133px） |
| 逐块分布 | 70/70 块全部有 ≥1 检出（0 检出的块：无）；单块检出 1–18 个 |
| 重叠带 vs 非重叠带（r1 v2 新增） | 带面积占比 14.2%；pre-NMS 框密度带内 12.64 vs 带外 4.05 /百万像素（≈3.1×）；IoU>0.5 对 35（跨块 30 / 同块 5 / 双中心在带外仅 3） |
| NMS 删除 33 框构成（r1 v2 新增） | 中心在带内 30/33；由相邻块 keeper 删除 28/33；删除 IoU 0.522–1.000（mean 0.848） |

判读：

- **0 → 193 的恢复（合并前文本框口径）是根因的直接反证**。模型、权重 pin、阈值、文本类过滤、后处理序列全部不变，唯一被改变的是送入单次推理的像素预算（1024×1024 块 → 640×640，压缩 1.6×，与模型训练分布相称），并由此顺带消除了整页输入的各向异性拉伸——本实验**不区分**「像素预算」与「宽高比/各向异性」二者的相对贡献（r1 更正措辞；对方案 A 的有效性无影响，但论证方案 C 时需注意 size 覆盖仍带各向异性）。若 0 候选源于权重/阈值/通道/decode 问题，块级不可能恢复出高置信度、全页覆盖、尺寸合理的检出。另注意计量层级：193 是 tile 路径的**合并前**跨块去重文本框数（生产 `cluster_words_into_blocks` 未在 tile 路径执行），生产 region/候选为**合并后**块数、应显著小于 193；与整页对照的「0」在两个层级上同为 0（raw ≥0.5 文本框 = 0、provider region = 0），层级差异不影响定性结论。
- 193（合并前文本框）vs docTR 15（生产合并后 region）：**层级不同，不是矛盾**。TA3-A smoke 的 15 是 docTR 路径经同一生产合并管线后的 region 数（`smoke-K01.json` `region_count`，框为 618×619/654×740 量级的块，非"文本行级计数"——r1 更正 v1 的粒度表述）；ogkalu 的 193 是合并前文本框，且其中含气泡内文字块与自由文本（类 1/2）、亦可能含少量注释/拟声词框。真正的产品取舍需修复 Task 用同一层级（生产 region）对比，本诊断不裁。
- NMS 去重 226→193（-14.6%）的构成已由 schema v2 全量坐标落盘后**复算落地**（`pre_nms_boxes`/`post_nms_boxes`/`nms_removed`/`overlap_band_stats`）：被删 33 框中 30 个中心在重叠带、28 个由相邻块 keeper 删除、删除 IoU 0.522–1.000（mean 0.848，样例：tile 30 框 `[391.3, 27800.1, 600.8, 27892.3, 0.949]` 与 tile 31 keeper `[392.0, 27799.7, 600.2, 27892.4, 0.9534]` IoU 0.9878——教科书式跨块重复检出）；pre-NMS 全量 IoU>0.5 对共 35 对（跨块 30 / 同块 5 / 双中心均在带外仅 3 对），带（面积占比 14.2%）内 pre-NMS 密度 12.64 vs 带外 4.05 /百万像素（≈3.1×，符合"同目标被相邻两块各检一次"而非"处处有框"）；kept 集合由 NMS 构造性保证两两 IoU≤0.5。重复对总量 35/226（≈15%）未见重复爆炸；跨块截断的框（一个气泡被块边界切开）在全量 post-NMS 坐标中未观察到病态输出（无超长/退化框），但 directional。

### 2.4 排除的备择假设

| 备择假设 | 反证 |
|---|---|
| 权重/模型文件损坏 | 三文件 sha256 与生产 pin 全匹配；BJ02 正常检出 |
| conf 阈值过高 | webtoon 三页 raw max 0.167–0.284，降到 0.3 仍为 0 检出；且低分是重缩放伪影而非真目标 |
| 输入 decode/通道错误 | 同一 `rgb` 数组路径下 BJ02 检出正常；K01 sha256 与 TA3-B manifest 匹配（同一像素产出 0 候选证据） |
| provider 后处理过滤丢框 | 官方 post_process 在阈值处本就为 0（`official_post_process_ge_0_5=0`），无可过滤之物 |
| RT-DETR query 容量不足（300 query） | BJ02 仅用 10 个 query 即饱和；K01 塌陷分数分布在 143 个 query 上，与容量无关 |

## 3. 修法建议对比（AC3，只建议不实施）

### 方案 A：tiling + 坐标回映（provider 内部，推荐主线）

对超长页（建议触发条件：`height/max(width,1) > 阈值` 或 `height > 像素上限`，参数配置化）在 `MangaDetectionProvider` 内切块 → 逐块生产推理序列 → 坐标回映 → 页级 NMS → 输出绝对像素 text_boxes。

| 维度 | 评估 |
|---|---|
| 改动面 | `src/infrastructure/providers/detection_manga.py` 单文件内部；`DetectionRequest/Response` 契约、MERGE_* 合并管线输入（绝对像素 text_boxes）完全不变 |
| 证据 | 本任务已端到端实测（含 pad 丢弃、回映、NMS）：0→193 恢复，conf 分布健康 |
| 风险 | ① 重叠带重复与跨块截断框——NMS IoU 0.5 的去重构成已由 schema v2 全量坐标复算落地（33 删框：30 带内 / 28 跨块 keeper / IoU mean 0.848），边界 case 需单测；② 性能：CPU ≈19.8s/70 块/页，块数随页高线性增长（对照发布探针稳态 273ms/页 = M2-PROD-DETECT-2 `packaged-detect-probe-results.json` `PK-L3-real-inference.warm_avg_ms`——r1 更正出处：v1 误记为 M2-PROD-DETECT-1，该 Task envelope 为 315.6ms/页另一口径；本 JSON K01 整页 provider_detect 574ms / raw infer 297ms 同列），最坏页 ≈34× 于常规页，超长页需预期管理或并发/降块策略；③ pad 伪检出实测为 0，中心点过滤足够；④ qualification 建议（r1）：带 ≥2 阈值点的候选数曲线（min conf 0.5009 贴阈、193 框中 22 个 <0.6，检出数对阈值敏感）+ 690×690 原生尺度块对照（≈1.0× 重采样，代价块数 ~1.6×） |
| 成本 | 中：一个 provider 内纯函数级改动 + 参数配置 + 单测 + 5 张 webtoon_long_strip 重跑 qualification 关闭 F1（K19 归 F4 口径项，见下） |

### 方案 B：per-layout 路由到 docTR

`layout_type=webtoon_long_strip` 的页不走 ogkalu，直接采用 docTR 检测候选。

| 维度 | 评估 |
|---|---|
| 改动面 | detect 编排/assembly 层路由分支；若两 provider 输出语义差异大，需契约侧确认 |
| 证据 | docTR fast_base 对 K01 同页 15 候选（TA3-A），独立于本诊断成立 |
| 风险 | ① **层级语义**：docTR 路径输出生产合并后 region（15）vs ogkalu 合并前跨块去重文本框（193）——两者计量层级不同，产品对比须先归一到同一层级（生产 region）；下游 OCR 裁切、翻译分块、MERGE 假设需重新核对；② 双模型 conf 语义不可比；③ 路由键必须绑定 `layout_type` 而非 family，防误伤 |
| 成本 | 路由本身低，但下游语义对齐 + 重跑 qualification 的成本未知 |

### 方案 C：processor size 覆盖（不推荐）

构造 processor 时覆盖 `size`（如 640×1280）。

**判定：证据不支持，排除。** 62133px 页即使调到 1280/1920 仍压缩 49×/32×，远超 BJ02 正常检出的 6.5× 分布；本实验 raw max 0.204 证明模型在 640×640 对该内容无响应，**没有任何证据表明更大 size 能恢复**，且非训练分辨率的 RT-DETR 行为无证据、显存/耗时随面积增长、运行时参数覆盖使 preprocessor sha256 pin 的语义复杂化。作为修法它的前提（目标在较大 size 下可见）恰好是未经验证的部分。

### 推荐排序与后续

1. **方案 A**：直接实测证据 + 改动面收敛 + 契约零变更；修复 Task 以 A 为主线，验收 = **5 张 `webtoon_long_strip`（K01/K02/K04/K05/K08）**重跑 qualification，以生产 `provider.detect` region 数计量（region >0 且全链可用）并给出合并后块数对比，关闭 F1 的长条漫部分。**K19 不在 tiling 验收面**（r1 更正：v1 曾把 ko 六 case 一并写入验收）：K19 为 1200×1660 的 `paged_webcomic` 无字页（TA3-B `quality-report.md` F1/F4 附注），0 候选是正确行为，需修的是「无字页应空成功而生产 step=failed/INVALID_INPUT」的 F4 口径缺陷，与重缩放根因无关。
2. **方案 B**：作为对比基线保留；若 A 的块级粒度在 qualification 中暴露产品问题（如注释框过多），再评估路由。
3. **方案 C**：排除。

## 4. 局限性

- directional：tile 实验仅 K01 一页（任务书 AC2 指定范围）；K02/K04 仅整页探针；**F1 六 case 中 K05/K08 无任何探针数据**（整页与块级均未跑，六 case 判定的外推基于 3 页同形态塌陷；K19 与重缩放无关，见 §3 推荐排序）。
- 无 per-block 负对照：未跑纯空白/pad-only 块或 BJ02 同切法对照（现有弱负对照=右 pad 带 70 块 × 334×1024px 零检出 + BJ02 整页仅 10/300 query 检出）；无阈值敏感度分析：去重后 min conf 0.5009 贴阈，193 框中 22 个 <0.6（13 个 <0.55；tile 19 单块 18 框中 11 框 <0.6），检出数对阈值高度敏感——r1 v2 全量坐标落盘后该分布可从 JSON 直接复算，修复 Task qualification 应带 ≥2 阈值点候选数曲线（见 §3-A 风险④）。
- CPU 单环境（torch 2.14.0+cpu，transformers 5.17.0，Python 3.12.3，设备已登记 probe-results.json `environment`）；GPU 下绝对耗时不同，机制结论不受影响。
- 块级 193 检出**没有 ground truth**：本诊断证明"信号恢复"，不证明"193 个全部正确"。精度/召回留给修复 Task 的 qualification。
- 探针重跑会覆盖 probe-results.json：本报告引用 schema v2（`generated_at_utc=2026-10-01T14:09:30Z`，r1 返修复跑）；schema v1（`2026-10-01T11:43:32Z`）保留于 git `b311f52f`，四页可观测值与 226/193 在两次运行间完全一致。

## 5. 证据文件索引

| 文件 | 内容 |
|---|---|
| `experiments/M2-DETECT-WEBTOON-DIAG/diagnose_webtoon_detect.py` | 探针脚本（AC1+AC2），生产 provider 直接构造，sha256 pin 强制校验 |
| `verification/M2-DETECT-WEBTOON-DIAG/probe-results.json` | 全量 raw 数据（schema v2）：四页可观测值 + K01 70 块逐块检出/conf + 去重统计 + pre/post-NMS 全量框坐标 + NMS 删除决策 + 重叠带统计 |
| `verification/M2-TA3-A/summaries/smoke-K01.json` | docTR 同页 15 候选对照（只读引用） |
| `src/infrastructure/providers/detection_manga.py` `_detect_text_boxes` | 生产推理序列（只读参考，未改动） |
