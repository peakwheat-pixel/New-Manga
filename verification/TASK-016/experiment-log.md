# TASK-016 实验记录（verification）

- Task：TASK-016「OCR 与检测路线独立实验」（kind: experiment）
- Owner：DeepSeek Harness ／ Reviewer：Codex
- base_commit：`f9edd68845d4a1ee5d42d9fdcf1a304dc3fa2f86`
- 分支 / 工作区：`agent/deepseek/TASK-016-ocr-detection-experiment` ／ `G:/CODEX/New Manga.worktrees/TASK-016-deepseek`
- 实验产物目录：`experiments/TASK-016/`（新增：`run_experiment.py`、`results/probe.json`、`results/run-models.json`、`samples/`）

## 1. 环境（实测）

| 项 | 值 |
|---|---|
| OS | Windows 10.0.26200 x64（`platform.platform()` 输出见 `results/probe.json`） |
| Python | 3.12.3（`G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe`） |
| GPU | **NVIDIA GeForce RTX 5070 Ti, 16303 MiB**（`nvidia-smi` 可用） |
| 显示平台 | 与本实验无关（实验不加载 Qt） |
| 网络 | `pypi.org:443` 可达、`files.pythonhosted.org:443` 可达、**`huggingface.co:443` 超时不可达** |
| 已安装的 OCR/检测依赖 | **全部缺失** —— `numpy`/`PIL`/`cv2`/`torch`/`onnxruntime`/`paddleocr`/`rapidocr_onnxruntime`/`shapely` 经 `importlib.util.find_spec` 检查均为 `False` |
| 依赖变更 | **无**。本实验未安装任何包、未修改 `requirements*.txt`（该文件不在白名单内） |

> 依赖与权重不可得的**根因**：实验解释器未预装任何候选依赖，且本机 `huggingface.co` 不可达（manga-ocr、PaddleOCR、Phi-3.5-vision 权重均需从 HF 或其镜像获取）。因此**无法在本环境产出任何模型质量或性能数字**。

## 2. 执行命令与结果

所有命令均在 `G:/CODEX/New Manga.worktrees/TASK-016-deepseek` 下、以

```powershell
$env:PYTHONPATH='experiments/TASK-016'
$env:PYTHONDONTWRITEBYTECODE='1'
```

执行；解释器为上文 Python 3.12.3。

| # | 命令 | 退出码 | passed | skipped | 结果 |
|---|---|---|---|---|---|
| 1 | `python experiments/TASK-016/generate_samples.py --output-dir experiments/TASK-016/samples` | **0** | — | — | 生成 **5 个自制样本** + `manifest.json`（含参考文本、参考区域、Tile 原点、样本 SHA-256） |
| 2 | `python -m unittest experiments/TASK-016/test_protocol.py -v` | **0** | **4** | **0** | `OK`（协议自检全部通过） |
| 3 | `python experiments/TASK-016/run_experiment.py --manifest experiments/TASK-016/samples/manifest.json --output experiments/TASK-016/results/probe.json` | **0** | — | — | `counts = {"BLOCKED": 15}`（probe-only，不下载） |
| 4 | `python experiments/TASK-016/run_experiment.py --output experiments/TASK-016/results/run-models.json --run-models` | **0** | — | — | `counts = {"BLOCKED": 15}`（显式真跑，依赖仍缺失） |

**命令 2 的 skip 原因**：无 skip（`0 skipped`）。协议自检不依赖任何模型、网络或第三方包。

## 3. 样本（自制）

`generate_samples.py` 生成 5 个样本，manifest 记录参考文本 / 参考区域 / Tile 原点 / SHA-256：

| sample_id | kind |
|---|---|
| `jp-horizontal` | japanese-horizontal（日文横排） |
| `jp-vertical` | japanese-vertical（日文竖排） |
| `ko-horizontal` | korean-horizontal（韩文横排） |
| `art-text` | rotated-art-text（艺术字/旋转） |
| `long-tile` | long-image-tile-global-coordinate（长图 Tile 全局坐标） |

**这些是自制的合成样本，不代表真实漫画分布**，也不构成任何质量阈值；manifest 的 `manifest_sha256` 记录在 `results/probe.json` 中。**模型 Hash：`NOT_AVAILABLE`**——本环境没有任何模型权重文件，因此不存在可记录的模型哈希（记录字段 `model_sha256` 在每条结果中均为 `NOT_AVAILABLE`，未以样本哈希冒充）。

## 4. 候选 × 样本矩阵（3 × 5 = 15 条记录，全部 BLOCKED）

| 候选 | 版本（按实现内的候选表） | 许可（按实现内的候选表） | 本环境状态 |
|---|---|---|---|
| `manga-ocr` | 0.1.16 / `kha-white/manga-ocr@v0.1.16` | Apache-2.0（仓库） | **BLOCKED** —— `missing dependency: manga_ocr` |
| `paddleocr-korean` | PaddleOCR 3.7.0 / `korean_PP-OCRv5_mobile_rec` | 代码 Apache-2.0；**权重条款需另行核实** | **BLOCKED** —— `missing dependency: paddleocr and/or paddle` |
| `openai-compatible-vision` | Phi-3.5-vision-instruct / vLLM 0.29.0 | MIT（模型）+ Apache-2.0（vLLM） | **BLOCKED** —— `missing endpoint/model configuration` |

**BLOCKED 原因只有这 3 类**，逐条记录在 `results/probe.json` 的 `records[].reason`；每条记录同时携带 `recognition_errors = "NOT_RUN"`、`coordinate_order = "NOT_RUN"`、`fallback = "BLOCKED: no explicitly configured fallback route"`、`metrics.*` 全为 `None`。

> **未以 Mock 冒充模型质量**：harness 在缺少依赖/端点时**拒绝**输出任何识别文本、延迟或显存数字；`--run-models` 与 probe-only 都只产出 `BLOCKED`，不产生假的 `PASS`。

## 5. 已实际验证的部分（不依赖模型，可回归）

| 能力 | 实现 | 证据 |
|---|---|---|
| Tile-local → page-global 坐标映射 | `protocol.tile_polygon_to_global` | `test_protocol.py` 通过；含 `[100,600]` 原点算术断言 |
| 单 Region 结果保留原始 `region_id` 并落到 page-global | `protocol.map_region_result` | 通过（`r-17`、`long-02` 两例） |
| 阅读顺序稳定（同序按 `region_id` 决胜） | `protocol.order_results` | 通过 |
| 失败 fallback 只允许**已配置**路由 | `protocol.fallback_status` | 通过（空配置集 → `BLOCKED`，不发明路由） |
| 环境/依赖探测与逐样本 BLOCKED/NOT_RUN | `run_experiment.py` | `results/probe.json` |

## 6. NOT_RUN / BLOCKED / N/A 清单

| 项 | 状态 | 原因 |
|---|---|---|
| 三种候选的**识别错误率**（真机） | **BLOCKED** | 依赖缺失 + 权重不可下载（HF 不可达） |
| **坐标/顺序**的模型输出比对 | **BLOCKED** | 无模型输出；协议侧已用合成数据验证 |
| **耗时 / RAM / VRAM**（模型推理） | **BLOCKED** | 无模型可跑；GPU 存在但无推理栈 |
| **样本质量**（真实漫画样本） | **NOT_RUN** | 无授权真实样本；仅自制合成样本 |
| **失败 fallback** 的真实行为 | **BLOCKED** | 依赖其组成候选；协议层已验证"只允许已配置路由" |
| **长图 Tile** 的模型侧全局坐标 | **BLOCKED**（模型）/ **PASS**（协议） | 模型不可用；Tile→global 算术已验证 |
| 版本/许可的**权威确认** | **NOT_RUN** | 需在有网络的环境核实（尤其**模型权重**条款，可能不同于代码许可） |
| 生产集成验证 | **N/A** | 实验不代表产品集成；TASK-016 不修改 `src/` |

## 7. 边界声明

- 未修改 `src/`、`tests/`、Schema/migration、共享 Protocol、`requirements*.txt`、`AGENTS.md`、其他 Task 或任何冻结 Task（含 TASK-015）。
- 未 push、未合并任何分支。
- `run_experiment.py` 默认**不联网、不下载、不安装**；`--run-models` 也只在依赖与端点**已就绪**时才会发起真实推理，本环境两者皆无。
- 本记录中的候选版本/许可抄自已实现内的候选表（`run_experiment.py` 的 `CANDIDATES`），**未经本环境联网核实**；调研结论另见 `doc/research/TASK-016.md`。

---

# 附：Review R-001~R-004 / S-001 修订证据（第二轮）

本轮修订对应 Codex 的独立 Review findings。命令、退出码与结果如下（环境同上：Windows 10.0.26200 / Python 3.12.3 / 默认 Windows 平台）。

| # | 命令 | 退出码 | passed | skipped | 结果 |
|---|---|---|---|---|---|
| 5 | `python -m unittest experiments/TASK-016/test_protocol.py -v` | **0** | **5** | **0** | `OK`（原 4 项 + 新增 R-002 的 fallback 收窄与非法配置测试） |
| 6 | `python experiments/TASK-016/run_experiment.py --output experiments/TASK-016/results/probe.json` | **0** | — | — | `{"BLOCKED": 30}`（**6 候选 × 5 样本**；新增 3 个检测器候选） |

**skip 原因**：无 skip（命令 5 为 `0 skipped`）。

## 逐项处置

| ID | 处置 | 证据 |
|---|---|---|
| **R-001** | 检测器候选纳入一等公民：`detector-dbnet` / `detector-ctd` / `detector-yolo` 进入 `CANDIDATES`（带 `stage: "detection"`），由 `_run_detector()` 显式 probe 并 `BLOCKED`；报告新增 `verification_matrix`（3 行，逐阶段声明"几何协议已覆盖 / 真实运行 BLOCKED / 需要范围裁决"）。**范围裁决请求**：YOLO 家族在 `doc/01:255` 被明确标为"本仓库无此文件"，无可用实现来源，需 Codex 裁决是否保留该候选 | `results/probe.json` 的 `verification_matrix`、`records[].provider`（6 个）、`_run_detector` 的两个 `_blocked` 分支 |
| **R-002** | `fallback_status()` 收窄：必须由调用方**点名**路由且该名称**在配置集内**才返回 `FALLBACK_CONFIGURED`；空集、未点名、点名不在集内一律 `BLOCKED`。新增 `validate_route_configuration()` 报告非法配置；新增 2 项测试（4 类断言 + 空配置/空白项） | `protocol.py`、`test_protocol.py::test_fallback_requires_an_explicitly_configured_route` / `::test_invalid_route_configuration_is_reported`；报告中 `fallback_configuration = {valid: False, problems: ["no fallback route configured"]}` |
| **R-003** | 候选元数据统一标为 **unverified candidate metadata**：`CANDIDATES` 每条带 `metadata_status: "UNVERIFIED"`，`version`/`license` 前加 `UNVERIFIED —` 前缀；`doc/research/TASK-016.md` 追加专门声明 | 报告中 `records[].candidate.metadata_status` 全为 `UNVERIFIED`；`doc/research/TASK-016.md` 末节 |
| **R-004** | 统一哨兵 `MODEL_SHA256_UNAVAILABLE = "NOT_AVAILABLE"`：`_base_result` 与 `_blocked` 均只写该常量，**不再读取 `TASK016_MODEL_SHA256` 环境变量**，样本哈希只出现在 `sample_sha256`，绝不进入 `model_sha256`；报告顶层亦输出 `model_sha256_sentinel` | `run_experiment.py`；报告中 `model_sha256` 取值集合 = `["NOT_AVAILABLE"]` |
| **S-001** | `doc/tasks/TASK-016.md` 的「交付与运行记录」已改为指向本轮实际交付（Handoff / Review / 实验结果），并追加本轮修订状态 | `doc/tasks/TASK-016.md` |

## 并发作者改动说明

本轮修订时工作区已存在**另一位作者**的未提交改动（未提交内容归原作者所有，已保留未覆盖）：
`run_experiment.py` 的 manga-ocr **Region polygon 裁切**（识别前先 crop，替代整图输入）、`doc/research/TASK-016.md` 的重写、
新增的 `verification/TASK-016/author-verification.md` 与 `results/model-run-blocked.json`、以及 `doc/tasks/TASK-016.md` 的部分更新。
本次提交同时包含这些改动与本轮的 R-001~R-004 修订；合并方向以"保留并发改动 + 补齐 findings"为准。

---

# 附：Review R-002/R-003/R-005~R-009 修订证据（第三轮）

环境：Windows 10.0.26200 / Python 3.12.3（`G:/CODEX/New Manga.task-envs/TASK-012-py312`）/ `PYTHONPATH=experiments/TASK-016` / `PYTHONDONTWRITEBYTECODE=1` / `QT_QPA_PLATFORM` 未设置（本实验不加载 Qt）。

| # | 命令 | 退出码 | passed | skipped | 结果 |
|---|---|---|---:|---:|---|
| 7 | `python -m unittest experiments/TASK-016/test_protocol.py -v` | **0** | **5** | **0** | `OK` |
| 8 | `python experiments/TASK-016/run_experiment.py --output experiments/TASK-016/results/probe.json` | **0** | — | — | `{"BLOCKED": 30}`（6 候选 × 5 样本），**不联网、不下载** |
| 9 | `python experiments/TASK-016/run_experiment.py --output experiments/TASK-016/results/run-models.json --run-models` | **0** | — | — | `{"BLOCKED": 30}`；离线开关已强制 |
| 10 | `python experiments/TASK-016/run_experiment.py --output experiments/TASK-016/results/model-run-blocked.json --run-models` | **0** | — | — | `{"BLOCKED": 30}`，与命令 9 同代码同模式（内容一致） |

**skip 原因**：命令 7 为 `0 skipped`。命令 8~10 为探测进程，无测试项。

## 固定结果的一致性（R-006）与 SHA-256（R-007）

| 文件 | schema | 候选数 | 记录数 | 状态分布 | `blocked_with_metrics` | SHA-256 |
|---|---|---:|---:|---|---:|---|
| `results/probe.json` | `task016-experiment-result-v2` | 6 | 30 | `{BLOCKED: 30}` | **0** | `b3c30a8bca68d7d8466ffa7246e2b13fcd2a73173a397977e915a67ab2c91e2a` |
| `results/run-models.json` | `task016-experiment-result-v2` | 6 | 30 | `{BLOCKED: 30}` | **0** | `5986fc158edb154a37d38e4ef10390d05bf92476084aa309988eb6f4cf4421bd` |
| `results/model-run-blocked.json` | `task016-experiment-result-v2` | 6 | 30 | `{BLOCKED: 30}` | **0** | `5986fc158edb154a37d38e4ef10390d05bf92476084aa309988eb6f4cf4421bd` |

`run-models.json` 与 `model-run-blocked.json` 由**同一代码、同一模式**生成，故内容与 SHA 一致；前者为权威名，后者保留以兼容既有引用。三份结果均满足：质量/性能字段为 `NOT_RUN`/`null`、`model_sha256 = NOT_AVAILABLE`、`fallback` 为唯一的可审计判定。

**离线开关实测**（`--run-models` 的两份）：`{"HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1", "HF_DATASETS_OFFLINE": "1"}`；默认 probe 模式不强制（`null`），因为其不进入任何模型构造器。

## 逐项处置（第二轮 findings）

| ID | 处置 | 证据 |
|---|---|---|
| **R-002** | 失败路径统一门控：新增 `_fallback_gate()`，`_run_manga_ocr`/`_run_paddle`/`_run_openai_compatible` 的异常分支与 `_blocked()` 全部写同一判定；空配置/未点名一律 `BLOCKED: no explicitly configured and named fallback route`，仅当 `TASK016_FALLBACK_ROUTE` 已配置且被点名时才 `FALLBACK_CONFIGURED` | 三份结果中 `fallback` 取值集合均为 `["BLOCKED: no explicitly configured and named fallback route"]` |
| **R-003** | `doc/research/TASK-016.md` 的表**前**加入 `⚠ UNVERIFIED CANDIDATE METADATA` 声明，**表头**直接标 `（UNVERIFIED）`，使脱离附录阅读也不会误认为已核实 | 该文件第 1 节 |
| **R-005** | 模型运行前置门槛：`enforce_offline()` 强制 `HF_HUB_OFFLINE`/`TRANSFORMERS_OFFLINE`/`HF_DATASETS_OFFLINE=1`；`local_weight_gate()` 要求 `TASK016_*_WEIGHTS`/`*_MODEL_DIR` 指向**真实存在的本地路径**（并计算其内容 digest 作为 `model_sha256`），缺失即在**构造器之前**返回 `BLOCKED` | 离线开关实测见上；`_run_manga_ocr`/`_run_paddle` 均先调用 gate 再 import/构造 |
| **R-006** | 三份固定结果全部按最新代码重生成（命令 8~10） | 上表：均为 v2 / 6 候选 / 30 记录 |
| **R-007** | 重新计算并同步三份结果的 SHA-256 | 上表 SHA 列 |
| **R-008** | `doc/tasks/TASK-016.md`：正文状态表述改为历史（"当前状态以 frontmatter 为准"），补入实际 Handoff/Review 链接，末尾只保留一条**当前状态** | 该文件「交付与运行记录」与末尾「当前状态（唯一）」 |
| **R-009** | `_blocked()` 将 `metrics` 全量清零；`_run_detector()` 的前置门槛位于**任何资源采样之前**，detector 路径不再调用 `_memory_mb()`/`_vram_mb()` | 三份结果 `blocked_with_metrics = 0` |
| **R-001 残留（detector-yolo）** | 明确为 `DOCUMENTATION_ONLY — no implementation source in this repository`，写入 `CANDIDATES` 与 `verification_matrix.scope_decision`；请 Codex 裁决是否保留 | `run_experiment.py` 的 `CANDIDATES`/`VERIFICATION_MATRIX` |

---

# 附：Review R-005 修订证据（第四轮：强制离线覆盖）

## 缺陷

上一轮 `enforce_offline()` 使用 `os.environ.setdefault(name, "1")`。**`setdefault` 不会覆盖已存在的值**：若调用方预置 `HF_HUB_OFFLINE=0`，该值会被保留，Provider 库仍可能访问网络，而实验记录却声称处于离线状态——即"记录的意图"与"实际生效的值"可能不一致。

## 修复

`enforce_offline()` 改为**无条件赋值** `os.environ[name] = "1"`，并从环境中**读回**构成返回映射，使证据记录的是**强制后的真实值**，而不是调用方的意图。权重侧仍保留 R-005 的本地门槛：`local_weight_gate()` 必须找到真实存在的本地权重路径（并计算其 digest 作为 `model_sha256`），否则在 **import/构造之前** 返回 `BLOCKED`。

## 验证（全部退出码 0）

| # | 命令 | 退出码 | passed | skipped | 结果 |
|---|---|---|---:|---:|---|
| 11 | `python -m unittest experiments/TASK-016/test_protocol.py -v` | **0** | **5** | **0** | `OK` |
| 12 | `python experiments/TASK-016/run_experiment.py --output experiments/TASK-016/results/probe.json` | **0** | — | — | `{"BLOCKED": 30}` |
| 13 | `… --output experiments/TASK-016/results/run-models.json --run-models` | **0** | — | — | `{"BLOCKED": 30}`；`offline_environment` 三值均为 `1` |
| 14 | `… --output experiments/TASK-016/results/model-run-blocked.json --run-models` | **0** | — | — | `{"BLOCKED": 30}`；同上（与 13 同代码同模式） |
| **15** | **反例**：先预置 `HF_HUB_OFFLINE=0`、`TRANSFORMERS_OFFLINE=0`、`HF_DATASETS_OFFLINE=0`，再执行 `--run-models` 输出到仓库外临时文件 | **0** | — | — | `offline_environment = {"HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1", "HF_DATASETS_OFFLINE": "1"}`，**全部为 1**（断言通过） |

**skip 原因**：命令 11 为 `0 skipped`（协议测试不依赖模型/网络/第三方包）；命令 12~15 为探测进程，无测试项。

## 三份固定结果（内容未变，SHA 与上一轮一致）

| 文件 | schema | 候选 | 记录 | 状态 | `blocked_with_metrics` | `offline_environment` | SHA-256 |
|---|---|---:|---:|---|---:|---|---|
| `results/probe.json` | `task016-experiment-result-v2` | 6 | 30 | `{BLOCKED: 30}` | **0** | `null`（probe 模式不进入构造器，故不强制） | `b3c30a8bca68d7d8466ffa7246e2b13fcd2a73173a397977e915a67ab2c91e2a` |
| `results/run-models.json` | 同上 | 6 | 30 | `{BLOCKED: 30}` | **0** | `{HF_HUB_OFFLINE: "1", TRANSFORMERS_OFFLINE: "1", HF_DATASETS_OFFLINE: "1"}` | `5986fc158edb154a37d38e4ef10390d05bf92476084aa309988eb6f4cf4421bd` |
| `results/model-run-blocked.json` | 同上 | 6 | 30 | `{BLOCKED: 30}` | **0** | 同上 | `5986fc158edb154a37d38e4ef10390d05bf92476084aa309988eb6f4cf4421bd` |

`detector-yolo` 维持 `DOCUMENTATION_ONLY — no implementation source in this repository`（本轮未改动该项）。

## 范围检查

- `git diff --check`（工作区与暂存区）均退出码 **0**；白名单越界 **0**。
- 未修改生产 `src/`、`tests/`、Schema/migration、依赖清单、AGENTS、其他 Task 或任何冻结 Task；未 push、未合并。

## 9. Codex 集成后复验（`integration_commit=9bf85f5`）

集成验证明细见 [integration-9bf85f5](integration-9bf85f5.md)。在 Windows 默认 Qt 环境（`QT_QPA_PLATFORM` 为空，未设置 offscreen）执行：协议测试 **5 passed / 0 skipped**；默认 probe **30 BLOCKED**；`--run-models` **30 BLOCKED**、`blocked_with_metrics=0`、`HF_HUB_OFFLINE/TRANSFORMERS_OFFLINE/HF_DATASETS_OFFLINE=1,1,1`；预置三项为 `0` 的反例重跑仍得到 **1,1,1**。探测命令无测试项，`passed/skipped` 记为 N/A，skip 原因为 N/A。

真实 OCR/检测质量、错误率、坐标/顺序误差及耗时/RAM/VRAM 仍为 `BLOCKED`/`NOT_RUN`；未以 Mock 代替。`detector-yolo` 的范围裁决为保留 `DOCUMENTATION_ONLY` 文档候选，不表示已有生产实现。
