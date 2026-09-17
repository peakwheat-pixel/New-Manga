# TASK-018 研究记录：Mask / Inpainting 路线独立实验

> **性质**：`As-Is` 实验记录（TASK-018 白名单内）。不是产品需求、不是生产 Router 契约，也不替代 Codex 的独立 Review。**生产 Router 属 TASK-019，本 Task 只提出有实测依据的条件建议**。
> 固定基线：`dce95acbb57a3494cb0f9d8d2d42e27d164176bb`；实验在 `agent/deepseek/TASK-018-mask-inpainting-experiment` 的 `9ee17189` 起点上进行。

## 1. 本环境的硬约束（先说清楚，避免误读后文）

| 项 | 实测 |
|---|---|
| OS / Python | Windows `10.0.26200` / Python 3.12.3（`G:/CODEX/New Manga.task-envs/TASK-012-py312`） |
| GPU | **NVIDIA GeForce RTX 5070 Ti, 16303 MiB**（`nvidia-smi` 可用） |
| `torch` | **未安装** |
| `diffusers` | **未安装** |
| `onnxruntime` | **未安装** |
| `numpy` / `PIL` / `cv2` | **均未安装** |
| `PySide6` | **6.11.2 可用**（本实验的图像 I/O 全部走 `QImage`） |
| 权重下载 | 受限于本环境网络策略，**未下载任何模型权重**；因此**模型 Hash 一律 `NOT_AVAILABLE`** |

**结论**：五条候选路线中，**只有不依赖模型的基线可以在本环境真实执行**。这正是 AC-1 要求的"未能测试项明确保留未知"。

## 2. 五条候选路线的实际可用范围

| 路线 | 类型 | 规模档 | 依赖 | 本环境可运行 | 备注 |
|---|---|---|---|---|---|
| **Simple Fill** | 基线（非模型） | `none` | 无 | **✅ MEASURED**（5/5 样例） | 常量色填充；**唯一在所有五类样例上残字为 0 的路线** |
| **Edge bleed** | 基线（**非模型**） | `none` | 无 | **✅ MEASURED**（5/5 样例） | **正交邻居均值扩散**（实现见 `mask_protocol.edge_bleed_fill`；交付数据中的 `route_label` 写作 "nearest-neighbour"，属历史命名，含义以本条为准，见 §9 R-004）；仅作**结构对照**，**不是**学习型修复，不得当作模型结果 |
| **Manga LaMa** | 学习型 | `medium` | `torch` + HF 权重 | **⛔ BLOCKED** | 漫画专用 LaMa 权重；缺 `torch` 且权重不可下载 |
| **AOT-GAN** | 学习型 | `medium` | `torch` + 权重 | **⛔ BLOCKED** | 缺 `torch` 且无权重文件 |
| **BrushNet / PowerPaint** | 学习型 | `large` | `torch` + `diffusers` + 权重 | **⛔ BLOCKED** | 扩散式；依赖与权重均缺；**权重体积未核实**（未下载、未实测） |
| **FLUX**（inpaint/fill） | 学习型 | `very-large` | `torch` + `diffusers` + 权重 | **⛔ BLOCKED** | `very-large` 只是本 Task 的规模档定性描述，**无实测资源数字** |

**未验证的大型模型一律未设为默认**：`default_eligible` 仅 `simple-fill` 与 `edge-bleed` 为 `True`；四条学习型路线全部为 `False`（见 `results/experiment.json` 的 `routes`）。

**学习型路线不写入任何资源数字**（2026-09-17 集成收口）：本报告不为它们给出权重体积、显存、内存或耗时数值。`results/experiment.json` 的 `routes[*].requirements` 键名仍带历史体积标注（如 `10GB+`），那只是缺失依赖的标签、**不是实测值**，待 §9 的解锁条件一并清理（R-006）。

## 3. 固定五类样例

样例由 `generate_samples.py` 以 PySide6 `QImage`/`QPainter` 生成（本环境无 PIL/numpy），尺寸统一 320×320，人工标注**目标框**（Mask 必须覆盖）与**保护框**（修复不得触碰）：

| sample_id | kind | 场景 | 目标框 |
|---|---|---|---|
| `s1-white-background` | white-background | 白底黑框 + 粗体文字 | (96,128,224,176) |
| `s2-line-art` | line-art | 密集斜线线稿 + 文字压线 | (104,136,216,168) |
| `s3-screentone` | screentone | 规则网点半调 + 文字 | (96,128,224,176) |
| `s4-gradient` | gradient | 水平灰阶渐变 + 文字 | (96,128,224,176) |
| `s5-structure-crossing` | structure-crossing | 面板框 + 速度线穿越文字区 | (92,124,228,180) |

每个样例的 SHA-256、目标框与保护框见 `experiments/TASK-018/samples/manifest.json`。

**Mask 策略**：raw Mask = 目标框；final Mask = raw 经参数化精修（`dilate_radius=2`，其余见 §5）。**raw 与 final Mask 均被保留并记录**（面积、包围盒、`final_covers_raw`），满足 AC-3 的"保留原始/最终 Mask"。

## 4. 实测结果（`--repeat 3`，全部为真实执行）

耗时为该路线 3 次重复的 **min/max**；`ink` 为修复前 Mask 内的暗像素数；`residual` 为修复后仍是暗像素的数量（**残字的像素统计代理，不是视觉质量判定**）；`viol` 为 **final Mask 外被改动的像素数**（必须为 0；该判据的覆盖范围严格包含 `samples/manifest.json` 声明的保护框，但 harness 目前未按保护框逐个断言——原表述“保护框内被改动的像素数”已按 Review R-001 更正，见 §9）；`rss` 为进程峰值工作集。

| 样例 | 路线 | min ms | max ms | ink(前) | residual(后) | viol | peak RSS MB |
|---|---|---:|---:|---:|---:|---:|---:|
| white-background | simple-fill | 2.268 | 2.897 | 519 | **0** | **0** | 45.45 |
| white-background | edge-bleed | 39.022 | 42.519 | 519 | 519 | **0** | 49.39 |
| line-art | simple-fill | 2.248 | 2.354 | 2010 | **0** | **0** | 53.96 |
| line-art | edge-bleed | 31.533 | 38.321 | 2010 | 1932 | **0** | 56.79 |
| screentone | simple-fill | 2.255 | 2.311 | 1794 | **0** | **0** | 56.79 |
| screentone | edge-bleed | 38.039 | 39.391 | 1794 | 1410 | **0** | 56.79 |
| gradient | simple-fill | 2.369 | 2.525 | 570 | **0** | **0** | 56.79 |
| gradient | edge-bleed | 39.816 | 42.333 | 570 | 570 | **0** | 57.7 |
| structure-crossing | simple-fill | 2.286 | 2.465 | 2958 | **0** | **0** | 57.7 |
| structure-crossing | edge-bleed | 42.198 | 45.518 | 2958 | 2031 | **0** | 57.7 |

### Mask 内实际改写覆盖（Codex 集成复核，2026-09-17）

上表的 `residual` 只统计 Mask 内剩余暗像素，无法说明路线**是否真的改写了 Mask 内部**。Codex 在独立 Review 中用交付的样例 PNG 与输出 PNG 逐像素比对（final Mask＝目标框膨胀 2 px，与 harness 一致）复核得到：

| 样例 | simple-fill 改写 / Mask | edge-bleed 改写 / Mask | edge-bleed 未触及 |
|---|---:|---:|---:|
| white-background | 673 / 6864 | **0** / 6864 | 6864（产物与样例逐像素相同） |
| line-art | 2091 / 4176 | 1100 / 4176 | 3076 |
| screentone | 1911 / 6864 | 528 / 6864 | 6336 |
| gradient | 6864 / 6864 | 1994 / 6864 | 4870 |
| structure-crossing | 3082 / 8400 | 1504 / 8400 | 6896 |

`edge_bleed_iterations=8` 对 52～56 px 高的 Mask 只能覆盖边界环，因此 **edge-bleed 的 `residual` 主要来自“从未被改写的原始像素”**，不等于“修复失败”。两条基线的覆盖**不对等**，不可据此排序。复核方法可原样重算（逐像素比对样例与 `results/*__*.png`）；本表数值登记于集成提交 `4d189ce` 的 Review 记录与 [实验日志](../../verification/TASK-018/experiment-log.md)。

### 可以直接读出的结论

1. **非目标像素保护 100% 达成**：10 条实测记录的保护违规全部为 **0**，说明实验侧的 Mask 门控（"只重写 Mask 内像素"）在基线上被严格执行并可回归验证。
2. **Simple Fill 的残字为 0，但这不是质量结论**：常量白填充必然把暗像素清零（`residual=0` 是**构造性结果**）。它在**白底**样例上确实有效（背景本就是白色），但在**线稿、网点、渐变、结构穿越**四类样例上，它同样会把目标框内的**线稿/网点/渐变/边框结构一并抹成白块**——残字指标看不见这一点，因此**不能仅凭 `residual=0` 判定 Simple Fill 可用**。这正是必须记录"背景/边框损伤"的原因。
3. **Edge bleed 的 residual 反而更高，但主因是覆盖不足、不是修复失败**：8 次迭代只能改写 Mask 边界环（改写量见上一节；white-background 上甚至为 0），未触及的原始像素继续被计入 `residual`（line-art 1932、structure-crossing 2031）。它确实会把邻域颜色扩散进边界环，且同样不延续结构——**结构穿越样例最能暴露这一点**。两条基线覆盖不对等，本表不能用于给它们排序。
4. **耗时量级**：基线在 320×320、Mask 约 6k–10k 像素下为 **~2 ms（simple-fill）** 与 **~32–46 ms（edge-bleed）**；峰值工作集约 **45–58 MB**，且**全部为 CPU 路径，无 GPU 分配**（`vram_peak_mb = null`）。

### 明确无法给出的结论

- **四条学习型路线的修复质量、残字、背景/边框损伤、耗时与显存峰值**：**全部 `BLOCKED`**，原因是缺依赖与权重。**未以任何 Mock 或基线结果冒充**。
- **"哪种路线更好"**：在只有基线可跑的前提下，**本实验不足以对学习型路线排序**。任何"Manga LaMa 优于 AOT"之类的说法都不属于本实验的结论。
- **背景/边框损伤的量化**：目前只有"保护框违规=0"这一**结构性**保证；Mask **内部**的线稿/网点/结构损伤**没有被量化**（残字统计只测暗像素）。这是本实验最明显的证据缺口，已在 §7 登记。

## 5. 参数与可复现性

`results/experiment.json` 中每条记录都携带完整参数快照：

| 参数 | 值 | 说明 |
|---|---|---|
| `dilate_radius` | 2 | final Mask = raw Mask 膨胀 2 px |
| `feather_radius` | 0 | 未启用羽化（基线无渐变混合需求） |
| `min_region_pixels` | 1 | 不丢弃小区块 |
| `keep_largest_component` | false | 保留全部连通块 |
| `fill_colour` | (255,255,255) | Simple Fill 常量色 |
| `edge_bleed_iterations` | 8 | edge bleed 迭代次数 |

每条记录另存 `raw_mask_area` / `final_mask_area` / `raw_mask_bbox` / `final_mask_bbox` / `final_covers_raw`，以及 `mask_sha256`（Mask 记录的规范化 JSON 摘要）；输出图另有 `output_sha256`。

## 6. Router / fallback / 资源要求建议（依据实测，供 TASK-019 决策）

> 以下是**实验证据支持的候选条件**，不是已批准的生产契约。生产 Router 由 TASK-019 实现。

1. **默认路线应为无关模型的确定性基线**：实测中 `simple-fill` 与 `edge-bleed` 是唯一可运行、可重复、CPU-only 且零违规的路线。建议把它们作为**保底能力**（保底不等于"质量达标"）。
2. **简单的背景判定可以显著缩小问题范围**：白底样例上 Simple Fill 的 `residual=0` 说明**当目标框内背景近似纯色时，常量填充是足够的**。建议 Router 的第一个判据是"Mask 内背景方差/是否纯色"，纯色 → 常量填充；否则 → 需要学习型修复或结构化基线。
3. **结构敏感场景必须走专用路线**：`structure-crossing` 是基线表现最差的样例（edge-bleed residual 2031，且两条基线都会切断边框/速度线）。建议把"Mask 是否与已知结构（面板框、长直线）相交"作为**升级到学习型路线的必要条件**，而不是可选优化。
4. **fallback 链**：建议 `学习型路线 → 结构化基线 → Simple Fill`，并且**仅在资源可用时才尝试学习型**；任一环节不可用时必须在结果中留下 `BLOCKED` 记录，**不得静默降级后声称已修复**。这与 AC-2"记录背景/边框损伤"的要求一致。
5. **资源要求**：本环境实测基线峰值 RSS **≤ 58 MB**、CPU 耗时 **≤ 46 ms/320×320**。**学习型路线的显存/内存需求在本环境完全未测**（`BLOCKED`），因此**不得**为它们写入任何资源数字；TASK-019 若需要，必须先在实际具备依赖与权重的环境重跑本实验。
6. **未验证的大型模型不得设为默认**：`flux`、`brushnet-powerpaint` 的规模档为 `very-large`/`large`，本实验**没有任何一条可用证据**支持它们作为默认；在获得实测数据前它们只能是"候选"。

## 7. 未知与未验证项（明确保留）

| 项 | 状态 | 原因 |
|---|---|---|
| Manga LaMa / AOT / BrushNet-PowerPaint / FLUX 的修复质量 | **BLOCKED** | 缺 `torch`/`diffusers` 与权重，且权重不可下载 |
| 上述路线的耗时、内存与**显存**峰值 | **BLOCKED** | 同因；**未用基线数字代替** |
| 上述路线的残字与背景/边框损伤 | **BLOCKED** | 同因；**未用 Mock 代替** |
| Mask **内部**的结构损伤量化（线稿/网点/渐变/边框是否被正确延续） | **NOT_RUN** | 现有残字指标只统计暗像素；需要专门的"结构连续性"指标或人工目视，**本环境无图像判读能力**（当前模型不支持图像输入），故不给出目视结论 |
| OOM 行为 | **NOT_RUN（无法触发）** | 唯一可运行的路线是 CPU 常量填充/扩散，峰值 58 MB，**无法构造真实 OOM**；学习型路线的 OOM 行为随其 `BLOCKED` 一并未知 |
| 缺模型行为 | **已验证** | 四条学习型路线在缺依赖/权重时被记录为 `BLOCKED` 并带具体原因，**不产生任何伪造图或数字** |
| 模型版本与 Hash | **NOT_AVAILABLE** | 未下载任何权重 |
| 真实漫画样例（非自制） | **NOT_RUN** | 仅使用自制合成样例 |

## 8. 复现方式

```powershell
$env:PYTHONPATH='experiments/TASK-018'
$env:PYTHONDONTWRITEBYTECODE='1'

# 1) 生成固定样例 + manifest（含 SHA-256、目标框、保护框）
python experiments/TASK-018/generate_samples.py

# 2) 协议与不变量自检（12 例，无依赖）
python -m unittest experiments/TASK-018/test_mask_protocol.py -v

# 3) 五路线 × 五样例实验（每条可运行路线重复 3 次）
python experiments/TASK-018/run_experiment.py --repeat 3
```

`--route simple-fill` 等可只跑单条路线；`--repeat N` 控制重复次数。

## 9. Review 后修订与未关闭项（2026-09-17，Codex 集成收口）

独立 Review（[`doc/reviews/TASK-018-6c33e7f.md`](../reviews/TASK-018-6c33e7f.md)，decision=`approved`）对固定 `delivery_head=6c33e7f` 提出 7 条 findings。在本报告范围内的处置如下；未关闭项同时登记在 [实验日志](../../verification/TASK-018/experiment-log.md)。

| ID | 级别 | 内容 | 处置 |
|---|---|---|---|
| R-001 | P2 | `viol` 被表述为“保护框内改动数”，实际是 final Mask 外改动数；`manifest.json` 的 `protected_boxes` 未被 harness 断言 | **本报告已更正口径**（§4 与本节）；保护框逐个断言留待 R-002 同一解锁条件 |
| R-002 | P2 | 路线门控是静态常量而非环境探测；`runnable_here`/`blocked_reason` 不可作为环境证据 | **deferred**：本环境缺依赖经独立复核为真，但机制不具探测性；解锁条件见下 |
| R-003 | P3 | `--output-dir` 指向实验根之外会 `ValueError` 退出码 1 并留下部分产物 | **deferred**；已在实验日志登记 |
| R-004 | P3 | “最近邻扩散”与实现（正交邻居均值）不符 | **本报告已更正口径**（§2）；交付数据中的 `route_label` 保持不变以免重生成 JSON |
| R-005 | P2 | edge-bleed 覆盖不足未被量化，`residual` 被归因为扩散 | **本报告已补复核数据并改写结论**（§4 新增小节与结论 3） |
| R-006 | P2 | 学习型路线的“数 GB / 10GB+ 权重”为未实测、无出处的数字 | **本报告已删除体积数字**（§2）；`experiment.json` 的 requirements 标签待 R-002 条件一并清理 |
| R-007 | P2（潜在、当前不可达） | `run_experiment.py:189-192` 对任何非 `simple-fill` 路线回落到 `edge_bleed_fill`：一旦按 R-002 改成真实探测，未实现的路线会被写成 `MEASURED` 并产出伪造成果 | **deferred**，且是**解锁前置条件**：补探测前必须先引入 fail-closed 的“已实现/未实现”门控 |

**解锁条件（本 Task 后续任何重跑之前必须满足）**：在具备 `torch`/权重或网络的环境重跑本实验前，先修 R-007（未实现路线必须 `BLOCKED`，不得回落到基线结果），再按 R-002 补真实探测并重新取证。学习型路线的质量、残字、损伤与资源在获得实测前仍是未知。

### 9.1 后续修订切片 `d7c10d4`（2026-09-17）：R-002/R-003/R-006/R-007 与 R-001 剩余项 → **fixed**

上一节登记的 deferred 项已在本切片关闭；**已集成基线 `4d189ce` 不因本切片失效**（增量修复，未改写已集成提交）。

| ID | 原状态 | 现状态 | 证据 |
|---|---|---|---|
| R-001（剩余项：保护框逐框断言） | 部分收口 | **fixed** | 新增 `protected_box_violations()`；`results/experiment.json` 中 **20 个保护框全部 `changed_pixels = 0`**（10 条 MEASURED × 2 框） |
| R-002（路线门控为静态常量） | deferred | **fixed** | `requirements` 改为可探测描述符（`module` → `importlib.util.find_spec`；`weight` → 环境变量指向的本地文件存在性）；记录含 `requirement_probes` 与 `blocked_stage`（`dependency` / `not_implemented`） |
| R-003（`--output-dir` 越界崩溃） | deferred | **fixed** | `_display_path()` 回退绝对路径；写入 `%TEMP%/task018-outofroot` 时**退出码 0**、产物正常、`output_dir_in_experiment_root = false` |
| R-006（未核实的体积标注） | deferred | **fixed** | 描述符键名与 `note` 中 `10GB+`/`数 GB` 全部移除；`size_class` 统一加 `(unmeasured tier)`；`results/experiment.json` 按新代码重生成（`schema = task018-experiment-v2`） |
| R-007（非 `simple-fill` 路线回落 `edge_bleed_fill`） | deferred（潜在） | **fixed** | 显式 `FILLERS` 映射；未登记路线 `raise KeyError`；`route_gate()` 先判可实现性 → `not_implemented`。**反例**：依赖全部强制 satisfied 后仍 10/10 `BLOCKED`、`png_written=[]`、`any_measured=False` |

验证：`test_mask_protocol.py` **12 passed / 0 skipped**（原有 12 例未改动）；新增 `test_route_gating.py` **13 passed / 0 skipped**；`run_experiment.py --repeat 3` → **10 MEASURED + 20 BLOCKED**、保护违规 0、保护框 20/20 全 0；连续两次运行的 `routes`/`manifest_sha256`/`mask_sha256`/`output_sha256`/`sample_sha256`/`parameters`/`mask`/`protected_box_violations` **完全一致**。详见 [revision-d7c10d4.md](../../verification/TASK-018/revision-d7c10d4.md)。

> **仍未解决（不变）**：四条学习型路线的质量/耗时/内存/显存为 **BLOCKED**（本切片未新增任何数字）；Mask 内部结构损伤量化、真实 OOM、真实漫画样例为 **NOT_RUN**。R-004 与 R-005 已在集成收口提交内以文档口径处理，本切片不再改动。
