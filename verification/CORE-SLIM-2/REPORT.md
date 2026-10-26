# CORE-SLIM-2 报告：检测链 ONNX 化 / torch 裁剪

- Task: `doc/tasks/CORE-SLIM-2.md`；依赖 `INFER-BASELINE-EP-1`（实测基线）
- Branch: `task/CORE-SLIM-2`（worktree `G:/CODEX/New Manga.workspace/worktrees/CORE-SLIM-2`）
- Base: `21960f4cb`（含 CORE-SLIM-1 集成 `4b0d5f0eb` + INFER 基线集成 `1b91d93a9`）
- 未 push（按卡禁止）。

## 0. 结论（AC 逐条）

| AC | 判定 | 一句话证据 |
|---|---|---|
| AC1 可行性（方案 + 精度/速度） | **MET** | 方案 = fixed-shape ONNX（RT-DETR opset17 + manga-ocr enc/dec）+ ORT DirectML；精度（跨运行时）= 候选数 10/10 相同、recall 1.0、meanIoU 1.0、OCR 逐字符 10/10；速度 = 263.14 → 61.47 ms/页（DML） |
| AC2 实现（改 ORT + torch 可选回退） | **MET** | 新增 `onnx_sessions` / `detection_manga_onnx` / `ocr_manga_onnx`；默认路径 ONNX，`NEWMANGA_DETECTOR_BACKEND=torch` / `NEWMANGA_OCR_BACKEND=torch` 保留旧适配器（不随包） |
| AC3 体积 ≤700MB | **MET** | Core 运行时（不含模型）**970.1 → 186.3 MiB**，余量 513.7 MiB；闭包 torch 栈 0 命中（`size-report.md`） |
| AC4 回归 | **MET** | pytest `3F/2739P/9S`（失败集合=基线 3 项，0 新增）；`scripts/test.ps1` **102/102 passed, 0 skipped**；10/10 页检测一致性（见 AC1） |
| AC5 门禁 | **MET** | `check.ps1 -TaskPath` PASS；64-hex pin；Handoff + Record Decision |

## 1. AC1 可行性：迁移方案

### 1.1 方案（依据 `verification/INFER-BASELINE-EP-1/REPORT.md`）

- **检测（RT-DETR-v2）**：把 `ogkalu/comic-text-and-bubble-detector` 导出为 **fixed-shape ONNX**
  （opset 17，输入 `pixel_values [1,3,640,640]` fp32，输出 `logits [1,300,3]` + `pred_boxes [1,300,4]`）。
  预处理 = resize 640×640 BILINEAR + `1/255`（checkpoint `do_normalize:false`）；后处理 =
  sigmoid → 每 query 最大类 → 阈值 0.5 → cxcywh 归一化坐标 × 页面尺寸 → 绝对 xyxy。
  之后复用**完全相同的**纯后处理过滤与冻结 word-to-block 合并（`_text_boxes_from_results` /
  `cluster_words_into_blocks` 导入，不复制），并把 webtoon 长条 tiling 路径原样保留。
- **OCR（manga-ocr）**：shipped 的 encoder/decoder ONNX（ViT 224×224 + 逐 token 解码），
  解码循环留在 Python（greedy argmax、`[CLS]` 起始、`[SEP]` 停止、上限 24、特殊 token 过滤），
  与 INFER 基线验证过的循环逐字一致。
- **执行提供者（EP）策略**：默认 `NEWMANGA_DETECTOR_DEVICE=auto` → DirectML（安装
  `onnxruntime-directml` 时）否则 CPU；显式 `cuda` 在只有 DML 的轮子上是 typed `PROVIDER_UNAVAILABLE`；
  **EP 静默回退被硬断言**（`onnx_sessions.create_session` 校验 `session.get_providers()`，与基线
  `EP_NOT_ACTIVE` 同规则）。OCR 默认 CPU（基线：DML 97.87ms vs CUDA 23.17ms，且主包无 CUDA 轮子）。
- **模型分发**：两个 ONNX 产物 + vocab/config 由 `build_sidecar.ps1` 按 SHA-256 pin 拷入
  `<bundle>/models/detector/` 与 `<bundle>/models/ocr/manga-ocr-onnx/`（模型计入 models 预算，不计 Core 运行时）。

### 1.2 精度对比（同一批 10 页，torch 参考 = 生产 torch 适配器）

| 指标 | torch（生产适配器，CPU） | ONNX（CPU EP） | ONNX（DirectML EP） |
|---|---|---|---|
| 候选（合并后 block）总数 | 57 | 57 | 57 |
| 页级候选数完全一致 | — | **10/10** | **10/10** |
| 合并前 text box 数完全一致 | — | **10/10** | — |
| 框匹配 recall @IoU0.5 | — | **1.0** | — |
| 平均 IoU | — | **1.0** | — |
| 每页 median 耗时 | 263.14 ms | 203.45 ms | **61.47 ms** |

### 1.3 OCR 一致性

| 指标 | torch 参考（greedy 循环，CPU） | 产品 ONNX |
|---|---|---|
| 逐字符完全一致页数 | — | **10/10** |
| 每页 median 耗时 | 121.78 ms | 109.7 ms |

> 参考侧说明：torch 参考直接使用 INFER 基线验证过的 greedy 循环（kha-white/manga-ocr-base 权重）；
> 两侧都应用 `skip_special_tokens` 语义。绝对精度（vs 人工 GT）沿用 INFER 基线 §6 的 NOT_RUN 结论：
> 本机样本与 COO/Manga109 标注页数不匹配，无法对齐 GT，不冒充绝对准确率。

## 2. AC2 实现

### 2.1 新增/修改（源码，`src/**`）

| 文件 | 内容 |
|---|---|
| `src/infrastructure/providers/onnx_sessions.py`（新） | 共享 ORT 会话策略：EP 解析（cpu/dml/cuda/auto）、模型存在性检查、**EP 激活硬断言**、typed 错误 |
| `src/infrastructure/providers/detection_manga_onnx.py`（新） | `MangaDetectionOnnxProvider`：fixed-640 预处理、sigmoid/阈值/cxcywh 后处理、共享过滤与合并、tiling、SHA-256 pin、`backend=onnx` 审计 options |
| `src/infrastructure/providers/ocr_manga_onnx.py`（新） | `MangaOcrOnnxProvider` + `_MangaOcrOnnxEngine`：encoder/decoder ORT 会话、Python 解码循环、vocab/generation_config、SHA-256 pin、OCR 默认 CPU |
| `src/infrastructure/providers/runtime.py` | manga-ocr 注册改为按 `NEWMANGA_OCR_BACKEND`（默认 `onnx`，`torch` 保留旧描述符；非法值 fail-fast） |
| `src/bootstrap/core_assembly.py` | 检测后端选择：默认 `manga`=ONNX（`manga-onnx` 别名）、`torch`=旧适配器、`doctr` 不变；ONNX 后端默认 device=`auto`；权重解析共享 DETECT-2 lookup（文件语义，兼容目录 override） |

**未改**：stdio 协议/命令语义、Host 契约、`ports/**`、torch 适配器实现（`detection_manga.py` 零改动）、
`detection_doctr.py`、SFX 链。旧 torch 适配器只作为**可选回退**（`NEWMANGA_*_BACKEND=torch`），
不进入发布闭包（spec 显式 exclude + 负向断言）。

### 2.2 打包（`packaging/**`）

- `core_sidecar.spec`：`EXCLUDED` 新增 torch/torchvision/transformers/doctr + 其传递依赖
  （cv2/scipy/h5py/shapely/tokenizers/huggingface_hub/hf_xet/safetensors/networkx/mpmath/onnx）；
  `ML_HIDDENIMPORTS` 改为 `onnxruntime/PIL.Image/numpy`；closure 断言改为**正断言**（onnxruntime 必须存在、
  onnxruntime pyd + DirectML.dll 必须存在）+ **负断言**（torch/torchvision/transformers/doctr 一旦回流即构建失败）。
- `build_sidecar.ps1`：`Copy-MangaWeights`（torch 三件套）替换为 `Copy-MangaDetectorOnnx` +
  `Copy-MangaOcrOnnx`（逐文件 SHA-256 pin 校验，失败即构建失败）。
- `requirements.txt`：torch/torchvision/transformers/doctr/safetensors 明确标注为**可选开发/回退依赖**
  （发布闭包含 0 torch；dev venv 仍可跑旧适配器与 parity harness）。

## 3. AC3 体积

见 `verification/CORE-SLIM-2/size-report.md`。核心数字：Core 运行时 **970.1 → 186.3 MiB**（−783.8），
`models/` 642.3 MiB（ONNX RT-DETR 163.7 + SFX 38.9 + manga-ocr 439.6），整包 828.6 MiB，
闭包内 torch 栈 0 命中、Qt 0 命中。

## 4. AC4 回归

| 门 | 结果 | 证据 |
|---|---|---|
| `python -m pytest -q` | **3 failed, 2739 passed, 9 skipped**（基线 3F/2710P/9S；失败集合与基线相同：`tests/providers/test_detection_manga_real.py` 2 项 weights-missing 环境失败 + `tests/workbench/test_workbench_viewmodel.py` 1 项基线 flaky；**无新增失败**，新增 CORE-SLIM-2 用例 29 项） | `verification/CORE-SLIM-2/pytest-after.log` |
| `apps/desktop-avalonia/scripts/test.ps1` | **TEST PASS (Debug): 102/102 passed, 0 skipped**（对新构建无标签 sidecar 副本） | `verification/CORE-SLIM-2/scripts-test.log` |
| 检测样例与 S2/S4 口径一致 | 10/10 页候选数一致、recall 1.0、meanIoU 1.0（S2/S4 以候选/框为口径） | `verification/CORE-SLIM-2/parity.json` |
| 冻结闭包能力 smoke | **7/7 PASS**（catalog_loader 播种、core_service protocol 2.3 ping、acceptance_bridge 导入/管线/阅读/导出、sfx_detect_probe 启动） | `verification/CORE-SLIM-2/capability-smoke.json` |

## 5. AC5 门禁

- `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/CORE-SLIM-2.md` → PASS（见 Handoff）。
- Canonical Evidence 64-hex pin 见任务卡（commit 指向实现+证据提交）。
- Handoff：`doc/handoffs/CORE-SLIM-2-handoff.md`（含 Record Decision）。

## 6. NOT_RUN / 风险 / 遗留

| # | 项 | 状态 | 说明 |
|---|---|---|---|
| 1 | 绝对精度（检测 vs 人工 GT / OCR vs 人工转录） | NOT_RUN | 与 INFER 基线 §6 同一环境限制（样本页数与标注不匹配），本 Task 只做跨运行时一致性，不冒充绝对精度 |
| 2 | ORT 三档（CUDA/TensorRT）复测 | NOT_RUN | 主包只发 `onnxruntime-directml`（1.24.4）；CUDA 档沿用 INFER 基线结论（manga-ocr CUDA 23.17ms，需可选 onnxruntime-gpu + CUDA 12.8） |
| 3 | manga-ocr KV-cache 增量解码 | NOT_RUN | shipped ONNX 无 past_key_values；解码循环 24 步上限，OCR 延迟已在基线可接受区间 |
| 4 | 动态 shape RT-DETR ONNX | NOT_RUN（不采用） | 基线确认 ORT 无法加载动态图；本 Task 只发 fixed 163.7MB 图 |
| 5 | 冻结 exe 内的**真实模型**检测 smoke | 部分覆盖 | 冻结闭包经 `sfx_detect_probe` 证明 ORT/DML 可用、`core_service` 证明 torch-free 启动；ONNX 检测/OCR 的模型级验证在 dev 环境（`parity.py`，与生产同一份 provider 代码/模型）——打包后模型路径与 pin 由 `bundle-after.json` 的 `modelFiles` + 文件 hash 证明 |
| 6 | `python/` 插件运行时与 `playwright` | 与 CORE-SLIM-1 相同 | `playwright` 未进 build venv（既有一致边界，非本 Task 回归）；`mobi` 仍为惰性 import 边界 |
| 7 | 设备管理器 GPU 探测 | 已知边界 | `devices/manager.py` 仍以 torch 探测 CUDA；打包闭包无 torch → 报告“无 GPU 运行时”（不影响 DML EP：ONNX provider 直接按 ORT EP 选择，不依赖该探测）。后续可用 ORT EP 探测替换 |

## 7. 证据索引

`verification/CORE-SLIM-2/{REPORT.md,size-report.md,parity.json,bundle-before.json,bundle-after.json,capability-smoke.json,build.log,pytest-after.log,scripts-test.log,tools/}`；
上游：`verification/INFER-BASELINE-EP-1/REPORT.md`、`verification/CORE-SLIM-1/ac2/bundle-after.json`。
