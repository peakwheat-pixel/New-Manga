# TASK-018 修订切片取证：`d7c10d4`

> **更正（2026-09-17，集成收口，Review R-101）**：本文件 §1 与 §3 中"纯标准库""无第三方依赖"的表述**不准确**——`experiments/TASK-018/test_route_gating.py` 通过 `import run_experiment` 间接依赖 PySide6（该模块用 PySide6 做图像 I/O），只是测试代码本身只用标准库。权威说明见 [实验日志](experiment-log.md) §7.2 与 [`doc/reviews/TASK-018-5063315.md`](../../doc/reviews/TASK-018-5063315.md)。其余结论不受影响。

- Task：TASK-018「Mask / Inpainting 路线独立实验」后续修订切片
- Owner：DeepSeek Harness ／ Reviewer：Codex（**非作者，独立 Review 由 Codex 执行**）
- 固定 base：`8c63f9b19f6daf065847aefce01bda578332cd6b`（= 修订前分支 head，**已与 master 同步**，无需再次 merge）
- 修订 delivery head：`d7c10d4dfc64dced97a23a7b4db6b7f169a8567b`
- 分支 / 工作区：`agent/deepseek/TASK-018-mask-inpainting-experiment` ／ `G:/CODEX/New Manga.worktrees/TASK-018-deepseek`
- **已集成基线不受影响**：集成 merge `4d189ce`（被审 head `6c33e7f`）**不因本切片失效**；本切片是在其之上的**增量修复**，未改写任何已集成提交。

## 1. 修订范围（相对 base `8c63f9b`）

| 文件 | 变化 |
|---|---|
| `experiments/TASK-018/run_experiment.py` | 门控/探测/越界/标签/保护框（R-002/R-003/R-006/R-007/R-001） |
| `experiments/TASK-018/test_route_gating.py` | **新增**（161 行，纯标准库，13 例） |
| `experiments/TASK-018/results/experiment.json` | 按新代码重生成（`schema` → `task018-experiment-v2`） |
| `doc/tasks/TASK-018.md` | 状态与运行记录 |

**`test_mask_protocol.py` 未被改动**（原有 12 例一字未动，见 §3）。
`git diff --check 8c63f9b d7c10d4` → **退出码 0**；允许范围内 **4/4**，禁止路径命中 **0**（未触碰 `doc/STATUS.md`、`doc/00_INDEX.md`、`doc/12_ROADMAP.md`、`doc/tasks/README.md`、`src/`、`tests/`、`AGENTS.md`）。

## 2. 逐项处置

### R-007 fail-closed（潜在缺陷，已消除）

**问题**：`_evaluate_baseline` 对任何非 `simple-fill` 路线回落到 `edge_bleed_fill`。一旦某学习型路线被判为 runnable，就会**用错误的实现产出看似有效的 MEASURED 结果和输出图**。

**修复**：
- 新增显式映射 `FILLERS = {"simple-fill": …, "edge-bleed": …}`，`_evaluate_route()` 只经该映射分发；
- 未登记路线**直接 `raise KeyError`**，绝不替换实现；
- `route_gate()` **先判可实现性、再判依赖**：`implementation is None` → `blocked_stage="not_implemented"`，**依赖状态无关**。

**证据**（§4 反例）：把 `manga-lama`/`flux` 的全部描述符临时强制为 `satisfied` 后运行，10 条记录**全部 `BLOCKED` / `blocked_stage=not_implemented`**，`png_written = []`，`any_measured = False`。

### R-002 真实探测（静态常量 → 环境探测）

**问题**：`requirements` 全是字面 `False`，`_route_status()` 只读常量，`runnable_here` 不是环境证据。

**修复**：
- `requirements` 改为**可探测描述符**：`{"type":"module","name":…}` 经 `importlib.util.find_spec` 探测；`{"type":"weight","env":…,"label":…}` 经**环境变量指向的本地文件是否存在**探测；
- 每条记录带 `requirement_probes`（含 `probe` 方法名与 `env_var_set`）；
- 顶层 `routes[*].gate` 给出 `runnable` / `blocked_stage` / `missing`；
- 记录区分 **`blocked_stage = "dependency"`** 与 **`"not_implemented"`**。

**证据**：本环境 20 条 BLOCKED 全为 `not_implemented`（依赖探测并非阻断原因，因为实现根本不存在）；`test_route_gating.py` 的 `ProbingTests` 另有 4 例覆盖 module 存在/缺失、weight 环境变量存在/缺失，以及"实现存在但探测失败 → `dependency`"的合成路线。

### R-003 越界输出目录（崩溃 → 可记录）

**问题**：`--output-dir` 指向实验根之外时 `relative_to` 抛 `ValueError`，退出码 1 并留下部分产物。

**修复**：新增 `_display_path()`，`relative_to` 失败时**回退绝对路径**并返回 `inside_experiment_root=False`；报告顶层记录 `output_dir` / `output_dir_in_experiment_root`，每条 MEASURED 记录另记 `output_image_in_experiment_root`。

**证据**（§4 越界取证）：写入 `%TEMP%/task018-outofroot`，**退出码 0**，产物正常；记录 `output_dir = C:/Users/.../task018-outofroot`、`in_root = False`、`sample output_image = …（绝对路径）`、`output_image_in_experiment_root = False`。

### R-006 数据标签（去掉未核实体积数字）

**问题**：`requirements` 键名含 `"flux weights (HF, 10GB+)"`，`note` 含"数 GB"，均属**未实测、无出处**的体积标注。

**修复**：键名改为描述符 `{"type":"weight","env":"TASK018_FLUX_WEIGHTS","label":"flux weights"}`；`note` 与 `size_class` 中的体积表述全部移除，`size_class` 一律加 `(unmeasured tier)` 后缀并明确其为**相对、未实测**档位。`test_route_gating.py::LabelTests` 用 2 例断言不含 `GB`/`数 GB`/`several` 等 token 且 `size_class` 均标 `unmeasured`。

**证据**：`results/experiment.json` 已按新代码**重新生成**（`schema = task018-experiment-v2`；`reason`/字段变化为**预期行为**）。

### R-001 剩余项（保护框逐框断言）

**问题**：`viol` 实际是 **final Mask 外**改动数，而 `manifest.json` 的 `protected_boxes` **从未被逐个断言**——AC-2 的保护证据不完整。

**修复**：新增 `protected_box_violations()`，对每个 `protected_boxes` 条目单独统计框内改动像素；每条 MEASURED 记录携带 `protected_box_violations`（含 `box` / `changed_pixels` / `violated`），并把 `protected_boxes` 一并写入记录。

**证据**：**20 个保护框（10 条 MEASURED × 2 框）全部 `changed_pixels = 0`**。

## 3. 验证结果（逐项命令、退出码、passed/skipped）

环境：Windows `10.0.26200`；`G:/CODEX/New Manga.task-envs/TASK-012-py312`（Python 3.12.3 / PySide6 6.11.2）；`$env:PYTHONPATH='experiments/TASK-018'`；`$env:PYTHONDONTWRITEBYTECODE='1'`；未设置 `QT_QPA_PLATFORM`。

| # | 命令 | 退出码 | passed | skipped | 结果 |
|---|---|---:|---:|---:|---|
| 1 | `python -m unittest experiments/TASK-018/test_mask_protocol.py` | **0** | **12** | **0** | `OK`（**原有 12 例未改动、未减少**） |
| 2 | `python -m unittest experiments/TASK-018/test_route_gating.py` | **0** | **13** | **0** | `OK`（新增，独立计数，不污染第 1 项） |
| 3 | `python experiments/TASK-018/run_experiment.py --repeat 3` | **0** | — | — | `{"MEASURED": 10, "BLOCKED": 20}` |
| 4 | `run_experiment.py --output-dir %TEMP%/task018-outofroot --repeat 1` | **0** | — | — | 越界**不崩溃**，产物正常，路径记为绝对 |
| 5 | `git diff --check 8c63f9b d7c10d4` | **0** | — | — | 无输出 |
| 6 | 允许范围检查 | — | — | — | 4/4 在内；禁止路径命中 **0** |

**skip 原因**：命令 1、2 均为 **`0 skipped`**（纯标准库/纯 Python，无模型、无网络、无第三方依赖）；命令 3、4 为进程执行，无测试项。

**保护证据**：`protected_violations` 合计 **0**（10/10 记录）；`protected_box_violations` 共 **20 框全为 0**。

**门控证据**：`blocked_stage = {"not_implemented": 20}`；`filler` 取值集合 = `{"simple_fill", "edge_bleed_fill"}`（显式映射，无回落）。

## 4. 确定性与反例取证

**确定性（连续两次 `--repeat 3`）**——用户指定的字段全部一致：

| 字段 | 一致 |
|---|---|
| `manifest_sha256` | ✅ |
| `routes`（含 `gate`/`requirement_probes`） | ✅ |
| 记录键集合 | ✅ |
| `mask_sha256` | ✅ |
| `output_sha256` | ✅ |
| `sample_sha256` | ✅ |
| `parameters` | ✅ |
| `mask` | ✅ |
| `protected_box_violations` | ✅ |

**反例（fail-closed，R-007）**：`rx.probe_requirement` 被临时替换为"永远 satisfied"（**不改 harness 文件**），随后对 `manga-lama` 与 `flux` 各跑 5 个样例：

| 观测 | 结果 |
|---|---|
| 记录状态 | **10/10 `BLOCKED`** |
| `blocked_stage` | **`not_implemented`（10/10）** |
| `output_image` | `None`（10/10） |
| 写入的 PNG | **`[]`** |
| 是否存在 MEASURED | **False** |

## 5. 未变与未解决

- **学习型路线（Manga LaMa / AOT / BrushNet-PowerPaint / FLUX）的质量、耗时、内存与显存**：仍为 **BLOCKED**，本切片**未新增**任何相关数字，也未用基线结果冒充。
- **Mask 内部结构损伤量化**、**真实 OOM**、**真实漫画样例**：仍为 **NOT_RUN**（原因同前次记录）。
- 本切片只修复 R-001（剩余项）/R-002/R-003/R-006/R-007；R-004（措辞）与 R-005（基线对照口径）已在集成收口提交内以文档口径处理，本切片不再改动。
- 未 push、未合并 master；未释放 TASK-019 或其他冻结 Task。
