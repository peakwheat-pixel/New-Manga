# M2-DETECT-WEBTOON-DIAG：ogkalu 对 webtoon 长条漫 0 候选——适配器级诊断报告

- Task: `M2-DETECT-WEBTOON-DIAG`（kind: diagnosis；owner: ZCode；reviewer: DeepSeek Harness 非作者）
- 分支 / worktree: `agent/zcode/M2-DETECT-WEBTOON-DIAG` @ `G:/CODEX/New Manga.worktrees/M2-DETECT-WEBTOON-DIAG-zcode`
- base: `8e0de8d0`；探针脚本: [diagnose_webtoon_detect.py](../../experiments/M2-DETECT-WEBTOON-DIAG/diagnose_webtoon_detect.py)
- raw 数据: [probe-results.json](probe-results.json)（探针 schema v1，含 AC1 可观测值与 AC2 tile 实验全量数据）
- 纪律声明: **零 `src/**`/`tests/**` 改动**；生产 provider 直接 import 构造；权重三文件 sha256 与生产 pin 全部匹配（probe-results.json `weights.all_pins_match=true`）；tile 图块仅驻留内存，无任何像素/权重入库。
- 结论性质: **directional**（n=3 整页探针 + n=1 页 tile 实验，CPU 单环境），不构成 qualification。

---

## 1. 判定（AC2）

> **判定：整页重缩放致目标消失（whole-page downscale destroys the targets）成立，置信度高。**
> ogkalu RT-DETR-v2 权重对 webtoon 内容本身有充分判别力；0 候选唯一来自生产推理路径把 690×62133 的整页无 padding 各向异性压缩到 640×640（垂直 ~97×），气泡/文字在垂直方向退化为亚像素结构，300 个 query 的 sigmoid 分数整体塌陷到 0.3 以下，在生产阈值 0.5 处为空集。同一页仅改输入空间分辨率（1024×1024 块级推理）即从 **0 检出恢复到 193 个去重检出（conf max 0.967）**。

## 2. 证据链

### 2.1 生产路径结构（只读参考，非本任务改动）

`src/infrastructure/providers/detection_manga.py` 的 `_detect_text_boxes`（生产推理序列）把整页 RGB 直传 `processor(images=rgb, return_tensors="pt")`，**无任何 size 覆盖**。权重目录 `preprocessor_config.json`（sha256 pin 匹配）：

| 字段 | 值 | 含义 |
|---|---|---|
| `image_processor_type` | `RTDetrImageProcessor` | — |
| `size` | `{height: 640, width: 640}` | 重缩放目标 |
| `do_resize` | `true` | 启用 resize |
| `do_pad` / `pad_size` | `false` / `null` | **无 letterbox/padding 路径** → 各向异性拉伸 |

即任何输入都被无保比例地压到 640×640。无 `shortest_edge` 字段（该 config 走显式 `size` 路径），探针已按原样记录。

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
2. **输出管线正常**：`logits_shape=[1,300,3]`，300 个 query 全部有非零分数（`counts_ge["0.0"]=300`）。K01 在 ≥0.01 有 143 个 query——模型"看到了什么"但远不构成检出；这是重缩放伪影的典型形态，而非输入 decode 崩溃（否则应为全零/异常）。
3. **手工归约与官方后处理交叉一致**：探针用 sigmoid→per-query max 的全分布与 `post_process_object_detection(threshold=0.5)` 双路统计，`official_post_process_ge_0_5` 与手工 ≥0.5 计数在四页全部相等（webtoon 页 0=0，BJ02 10=10）——测量方法自洽。
4. **对照页自检通过**：BJ02 同探针、同权重、同阈值路径检出 10 个 ≥0.5（provider 文本类过滤后 5 region，conf 0.937–0.972）——探针本身在常规页行为正常（AC1 自检条件）。

同页 docTR 对照（背景证据，非本任务产出）：TA3-A `verification/M2-TA3-A/summaries/smoke-K01.json`，detector=`doctr-fast_base-pinned`，`region_count=15`，`source_sha256=600ca755…` 与本探针 K01 逐字节同页。

### 2.3 AC2 块级实验（tiling 可行性的直接证据）

设计：K01 裁成 1024×1024 块、垂直重叠 128px（12.5%，落在任务书 10–20% 带内，且为 RT-DETR stride 32 的整数倍）；宽 690<1024 右侧以常量灰 114 pad 到方形（pad 无文字内容，回映后按"中心点落入 pad 区"丢弃）；每块走与生产逐字节相同的推理序列（同 processor、同 pin 权重、同阈值 0.5、同文本类过滤 `(1,2)`）；块内检出按 `y+origin` 回映到页坐标，页级做置信度序贪心 NMS（IoU≤0.5）去重。

结果（probe-results.json `pages.K01.tile_experiment`）：

| 指标 | 值 |
|---|---|
| 块数 | 70（含尾块 crop_h=309） |
| 总耗时（CPU，含推理+回映+NMS） | 19793 ms（≈283 ms/块，与单页 273–297 ms 先例一致） |
| 原始检出 → 回映 → 去重 | 226 → 226（pad 区丢弃 0） → **193** |
| 去重后 conf | max **0.9666** / mean 0.8503 / min 0.5009 |
| 去重后几何 | median box 144.1×53.6 px；y 范围 **156.7–62008.9**（覆盖全页 62133px） |
| 逐块分布 | 70/70 块全部有 ≥1 检出（0 检出的块：无）；单块检出 1–18 个 |

判读：

- **0 → 193 的恢复是根因的直接反证**。模型、权重 pin、阈值、文本类过滤、后处理序列全部不变，唯一变量是输入的空间分辨率（1024×1024 块 → 640×640，压缩 1.6×，与模型训练分布相称）。若 0 候选源于权重/阈值/通道/decode 问题，块级不可能恢复出高置信度、全页覆盖、尺寸合理的检出。
- 193 vs docTR 15：**粒度不同，不是矛盾**。ogkalu 检出含气泡内文字块与自由文本（类 1/2），docTR fast_base 输出文本行级候选；193 中亦可能含少量注释/拟声词框。产品取舍（气泡级 vs 行级）留给修复 Task 的 qualification 判定，本诊断不裁。
- NMS 去重比 226→193（-14.6%）与 128px 重叠带占块高比例（12.5%）相称，未见重复爆炸；跨块截断的框（一个气泡被块边界切开）在本实验中未观察到病态输出（无超长/退化框进入 sample），但 directional。

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
| 风险 | ① 重叠带重复与跨块截断框——NMS IoU 0.5 实测有效（226→193），边界 case 需单测；② 性能：CPU ≈19.8s/70 块/页，块数随页高线性增长（生产 273ms/页先例变为秒级，超长页需预期管理或并发/降块策略）；③ pad 伪检出实测为 0，中心点过滤足够 |
| 成本 | 中：一个 provider 内纯函数级改动 + 参数配置 + 单测 + ko 6 case 重跑 qualification 关闭 F1 |

### 方案 B：per-layout 路由到 docTR

`layout_type=webtoon_long_strip` 的页不走 ogkalu，直接采用 docTR 检测候选。

| 维度 | 评估 |
|---|---|
| 改动面 | detect 编排/assembly 层路由分支；若两 provider 输出语义差异大，需契约侧确认 |
| 证据 | docTR fast_base 对 K01 同页 15 候选（TA3-A），独立于本诊断成立 |
| 风险 | ① **粒度语义**：docTR 文本行级（15）vs ogkalu 气泡/文本块级（块级 193），下游 OCR 裁切、翻译分块、MERGE 假设需重新核对；② 双模型 conf 语义不可比；③ 路由键必须绑定 `layout_type` 而非 family，防误伤 |
| 成本 | 路由本身低，但下游语义对齐 + 重跑 qualification 的成本未知 |

### 方案 C：processor size 覆盖（不推荐）

构造 processor 时覆盖 `size`（如 640×1280）。

**判定：证据不支持，排除。** 62133px 页即使调到 1280/1920 仍压缩 49×/32×，远超 BJ02 正常检出的 6.5× 分布；本实验 raw max 0.204 证明模型在 640×640 对该内容无响应，**没有任何证据表明更大 size 能恢复**，且非训练分辨率的 RT-DETR 行为无证据、显存/耗时随面积增长、运行时参数覆盖使 preprocessor sha256 pin 的语义复杂化。作为修法它的前提（目标在较大 size 下可见）恰好是未经验证的部分。

### 推荐排序与后续

1. **方案 A**：直接实测证据 + 改动面收敛 + 契约零变更；修复 Task 以 A 为主线，验收 = ko 6 case（K01/K02/K04/K05/K08/K19）重跑 qualification 关闭 F1。
2. **方案 B**：作为对比基线保留；若 A 的块级粒度在 qualification 中暴露产品问题（如注释框过多），再评估路由。
3. **方案 C**：排除。

## 4. 局限性

- directional：tile 实验仅 K01 一页（任务书 AC2 指定范围）；K02/K04 仅整页探针。三页整页分数塌陷形态一致，外推可信但未逐页块级验证。
- CPU 单环境（torch 2.14.0+cpu，transformers 5.17.0，Python 3.12.3，设备已登记 probe-results.json `environment`）；GPU 下绝对耗时不同，机制结论不受影响。
- 块级 193 检出**没有 ground truth**：本诊断证明"信号恢复"，不证明"193 个全部正确"。精度/召回留给修复 Task 的 qualification。
- 探针为一次性实验脚本，重跑会覆盖 probe-results.json（时间戳与逐项数字以本报告引用的 JSON 版本为准）。

## 5. 证据文件索引

| 文件 | 内容 |
|---|---|
| `experiments/M2-DETECT-WEBTOON-DIAG/diagnose_webtoon_detect.py` | 探针脚本（AC1+AC2），生产 provider 直接构造，sha256 pin 强制校验 |
| `verification/M2-DETECT-WEBTOON-DIAG/probe-results.json` | 全量 raw 数据：四页可观测值 + K01 70 块逐块检出/conf + 去重统计 + 40 个样例框 |
| `verification/M2-TA3-A/summaries/smoke-K01.json` | docTR 同页 15 候选对照（只读引用） |
| `src/infrastructure/providers/detection_manga.py` `_detect_text_boxes` | 生产推理序列（只读参考，未改动） |
