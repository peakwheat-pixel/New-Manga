# TASK-018 验证记录（verification）

- Task：TASK-018「Mask / Inpainting 路线独立实验」（kind: experiment）
- Owner：DeepSeek Harness ／ Reviewer：Codex
- 固定 base：`dce95acbb57a3494cb0f9d8d2d42e27d164176bb`
- 起始 head：`9ee17189817ede5564866049e01139b9608f63a7`
- 分支 / 工作区：`agent/deepseek/TASK-018-mask-inpainting-experiment` ／ `G:/CODEX/New Manga.worktrees/TASK-018-deepseek`
- 产物目录：`experiments/TASK-018/`

## 1. 环境（实测）

| 项 | 值 |
|---|---|
| OS | Windows `10.0.26200`（x64） |
| Python | 3.12.3（`G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe`） |
| PySide6 | 6.11.2（**本实验的唯一第三方依赖**） |
| GPU | **NVIDIA GeForce RTX 5070 Ti, 16303 MiB**；`nvidia-smi` 可用 |
| 缺失依赖 | `torch`、`diffusers`、`onnxruntime`、`numpy`、`PIL`、`cv2` **全部未安装** |
| 权重下载 | **未下载任何模型权重**；无网络取权重的路径 |
| 依赖清单变更 | **无**（`requirements*.txt` 未在允许范围内，也未修改） |
| `QT_QPA_PLATFORM` | 未设置（默认 Windows Qt）；样例渲染需要 `QGuiApplication`，已在脚本内自建 |

## 2. 执行命令与结果（全部退出码 0）

所有命令在 `G:/CODEX/New Manga.worktrees/TASK-018-deepseek` 下执行，
前缀 `$env:PYTHONPATH='experiments/TASK-018'`、`$env:PYTHONDONTWRITEBYTECODE='1'`。

| # | 命令 | 退出码 | passed | skipped | 结果 |
|---|---|---|---:|---:|---|
| 1 | `python experiments/TASK-018/generate_samples.py` | **0** | — | — | 生成 **5** 个样例 + `manifest.json`（含 SHA-256、目标框、保护框） |
| 2 | `python -m unittest experiments/TASK-018/test_mask_protocol.py -v` | **0** | **12** | **0** | `OK` |
| 3 | `python experiments/TASK-018/run_experiment.py --repeat 3` | **0** | — | — | `{"MEASURED": 10, "BLOCKED": 20}` |

**skip 原因**：命令 2 为 **`0 skipped`**（协议自检为纯 Python，不依赖模型/网络/第三方库）。命令 1、3 为进程执行，无测试项。

**中途修正（已修复，非遗留）**：

| 现象 | 根因 | 处置 |
|---|---|---|
| 命令 1 首次以退出码 `0xC0000409`（`STATUS_STACK_BUFFER_OVERRUN`）崩溃 | 创建 `QPainter` 时没有活动的 `QGuiApplication` | 在 `generate_samples.py` 中自建并复用 `QGuiApplication` |
| 峰值 RSS 首次记录为 `None` | `ctypes.windll.psapi.GetProcessMemoryInfo` 在本平台返回 **0**（失败） | 改用 `kernel32.K32GetProcessMemoryInfo`（实测返回 1）；仍失败时返回 `None` 而非 0 |

## 3. 样例与 Hash

| sample_id | kind | 尺寸 | manifest 中的 SHA-256（前 16 位） |
|---|---|---|---|
| `s1-white-background` | white-background | 320×320 | 见 `samples/manifest.json` |
| `s2-line-art` | line-art | 320×320 | 同上 |
| `s3-screentone` | screentone | 320×320 | 同上 |
| `s4-gradient` | gradient | 320×320 | 同上 |
| `s5-structure-crossing` | structure-crossing | 320×320 | 同上 |

完整 SHA-256、目标框、保护框在 `experiments/TASK-018/samples/manifest.json`；实验报告另存 `manifest_sha256`。
**模型 Hash：`NOT_AVAILABLE`**（未下载任何权重，未用样例哈希顶替）。

## 4. 参数与重复次数

| 项 | 值 |
|---|---|
| `--repeat` | **3**（每条可运行路线对每个样例重复 3 次） |
| `dilate_radius` | 2 |
| `feather_radius` | 0 |
| `min_region_pixels` | 1 |
| `keep_largest_component` | false |
| `fill_colour` | (255, 255, 255) |
| `edge_bleed_iterations` | 8 |
| Mask 保留 | **raw 与 final 均保留**（面积、包围盒、`final_covers_raw`、`mask_sha256`） |
| 输出图 | 每条 MEASURED 记录一个 PNG + `output_sha256`（共 10 张） |

## 5. 实测汇总

| 样例 | simple-fill min/max ms | edge-bleed min/max ms | 保护违规 |
|---|---|---|---|
| white-background | 2.268 / 2.897 | 39.022 / 42.519 | **0 / 0** |
| line-art | 2.248 / 2.354 | 31.533 / 38.321 | **0 / 0** |
| screentone | 2.255 / 2.311 | 38.039 / 39.391 | **0 / 0** |
| gradient | 2.369 / 2.525 | 39.816 / 42.333 | **0 / 0** |
| structure-crossing | 2.286 / 2.465 | 42.198 / 45.518 | **0 / 0** |

- **峰值 RSS**：45.45–57.70 MB；**显存峰值 `null`**（基线为 CPU 路径，不做 GPU 分配）。
- **残字（像素统计代理）**：simple-fill 全为 **0**（构造性结果，**不代表质量达标**）；edge-bleed 为 519–2031。
- **默认资格**：`default_eligible = ["edge-bleed", "simple-fill"]`；四条学习型路线全为 `False`。

## 6. 测试计划要求的覆盖情况

| 计划项 | 状态 | 证据 |
|---|---|---|
| 实际实验入口、样例 Hash、硬件、参数、重复次数 | **已完成** | 本文 §1/§3/§4；`results/experiment.json` |
| 输出图与失败样例归档 | **已完成（部分）** | 10 张输出图已入库；**学习型路线无失败样例可归档**（它们在构造前即 `BLOCKED`） |
| **非目标像素/Region 保护** | **已完成** | `protected_pixels()` 对每条 MEASURED 记录返回空列表（10/10）。该函数的判据是 **final Mask 外像素变更数**，其覆盖范围严格包含 `samples/manifest.json` 声明的 `protected_boxes`，但 harness 目前未按保护框逐个断言（Review R-001，报告已更正口径） |
| **缺模型行为** | **已完成** | 4 条学习型路线 × 5 样例 = 20 条 `BLOCKED`，均带具体原因，**不产生伪造图或数字** |
| **OOM 行为** | **NOT_RUN（无法触发）** | 唯一可运行路线为 CPU 常量填充/扩散，峰值 58 MB；无法构造真实 OOM。学习型路线的 OOM 行为随其 BLOCKED 一并未知 |
| 无硬件路线标 BLOCKED | **已完成** | `manga-lama`、`aot`、`brushnet-powerpaint`、`flux` |
| 模型/视觉/性能结果不由 Mock 代替 | **已完成** | 无任何 Mock；学习型路线的质量与性能字段保持 `null`/`NOT_RUN` |

## 7. NOT_RUN / BLOCKED / N/A 清单

| 项 | 状态 | 原因 |
|---|---|---|
| Manga LaMa / AOT / BrushNet-PowerPaint / FLUX 修复质量 | **BLOCKED** | 缺 `torch`/`diffusers` 与权重，权重不可下载 |
| 上述路线的耗时 / 内存 / **显存**峰值 | **BLOCKED** | 同上；**未用基线数字代替** |
| 上述路线的残字与背景/边框损伤 | **BLOCKED** | 同上；**未用 Mock 代替** |
| Mask **内部**的结构损伤量化 | **NOT_RUN** | 现有指标只统计暗像素；需要结构连续性指标或人工目视，而**当前模型不支持图像输入**，故不给出目视结论 |
| 真实 OOM | **NOT_RUN** | 无法在 CPU 基线上触发 |
| 真实（非自制）漫画样例 | **NOT_RUN** | 仅使用自制合成样例 |
| 生产 Router 实现 | **N/A** | 属 **TASK-019**；本 Task **不扩展到 TASK-019**，只提出建议 |
| 生产集成验证 | **N/A** | 实验不代表产品集成；本 Task 不修改 `src/` |
| 路线门控的环境探测 | **未实现（Review R-002）** | `ROUTES[*].requirements` 是静态常量，`_route_status()` 只读常量、不做 `find_spec`/权重探测；`routes[*].runnable_here`/`blocked_reason` **不是环境证据**，不得被 TASK-019 或后续重跑引用 |
| 越界输出目录 | **不支持（Review R-003）** | `--output-dir` 必须位于 `experiments/TASK-018` 之内；越界会抛 `ValueError`、退出码 1 并留下部分产物。重跑请改用整目录副本 |
| 未实现路线 fail-closed 门控 | **未实现（Review R-007）** | 非 `simple-fill` 路线若被判为 runnable，会回落到 `edge_bleed_fill` 并被写成 `MEASURED`。当前仅因门控恒为静态 `False` 而不可达；补真实探测前必须先修 |
| edge-bleed 的 Mask 内覆盖 | **已复核（2026-09-17）** | 8 次迭代只覆盖边界环：改写量 0/6864（white-background）、1100/4176、528/6864、1994/6864、1504/8400；`residual` 主要来自未触及的原始像素。详见研究报告 §4 新增小节 |

## 8. 边界声明

- 仅修改 `experiments/TASK-018/**`、`doc/research/TASK-018.md`、`doc/tasks/TASK-018.md`、`doc/handoffs/TASK-018-*.md`、`verification/TASK-018/**`。
- **未修改**生产 `src/`、`tests/`、Schema/migration、共享接口、依赖清单、`AGENTS.md`、其他 Task 或任何冻结 Task；**未扩展到 TASK-019**。
- **未 push、未合并**任何分支。
- `edge-bleed` 是**非模型基线**，在报告与数据中始终标为 `learned_model: false`，**不得**被当作学习型修复结果引用。
- **未以 Mock 冒充**真实模型、视觉或性能结果。

## 9. 独立 Review 与集成（2026-09-17，Codex）

| 项目 | 值 |
|---|---|
| base commit | `dce95acbb57a3494cb0f9d8d2d42e27d164176bb` |
| start head | `9ee17189817ede5564866049e01139b9608f63a7` |
| reviewed head（delivery） | `6c33e7f237f63fd9b777335e72b84fe317cf866b` |
| 元数据 head | `ef6d1c382a5cee8b165217274a6c72db08716188` |
| Review 报告 | `doc/reviews/TASK-018-6c33e7f.md`（decision=`approved`，R-001～R-007） |
| implementation merge | `4d189ce`（merge commit，parents `461e639` + `ef6d1c3`） |
| integration commit | `4d189ce` |
| 集成后验证 | [integration-4d189ce.md](integration-4d189ce.md) |

集成后复验（master）：

| # | 命令 | 退出码 | passed | skipped | 结果 |
|---|---|---:|---:|---:|---|
| 1 | `PYTHONPATH=experiments/TASK-018 python -m unittest experiments/TASK-018/test_mask_protocol.py -v` | 0 | **12** | **0** | `OK`（与交付一致） |
| 2 | `run_experiment.py --repeat 3`（在 `%TEMP%` 副本中执行，避免改写仓库内 `results/experiment.json`） | 0 | — | — | `{"MEASURED": 10, "BLOCKED": 20}`；MEASURED 保护违规 10/10 全 0；确定性字段与交付 JSON 完全一致 |
| 3 | `python -m pytest -q -p no:cacheprovider`（集成后全仓套件） | 0 | **530** | **6** | 6 项 skip 全为 `openssl unavailable`；7 次运行中 6 次为该结果，另 1 次为 `1 failed, 529 passed, 6 skipped`（未捕获用例名，随后连续 4 次通过；TASK-018 不在 `testpaths = tests` 内，属已登记的低频 flaky，非本次集成引入） |

Findings 处置：R-001/R-004/R-005/R-006（报告部分）已在集成收口提交内以文档口径修正收口；R-002/R-003/R-006（`experiment.json` 标签）/R-007 为 **deferred**，限制见 §7，解锁条件见研究报告 §9。

**未解决项不得被当作通过**：R-002 的静态门控、R-003 的输出目录限制、R-007 的回落隐患在修复前持续有效；学习型路线的质量/性能仍为 `BLOCKED`，Mask 内部结构损伤仍为 `NOT_RUN`；两条基线只是保底能力，不代表质量达标。
