# INFER-BASELINE-EP-1 实测报告：ORT-DML / ORT-CUDA / torch 三档推理基线

- Task: `INFER-BASELINE-EP-1`（kind=research，base_commit `c5aade851`）
- 测量时间：2026-10-27 03:48–04:55（Asia/Shanghai）
- 机器：Windows，**NVIDIA GeForce RTX 5070 Ti（16 GB，compute capability 12.0 / sm_120，驱动 616.92）**，
  Python 3.12.3（产品 `requirements.txt` 验证版本），无系统 CUDA Toolkit / cuDNN
- 数据：`fixtures/pages10/` 10 张真实漫画页（8 张 1350×1920 Manga109 风格 + 2 张 1200×1660
  Pepper&Carrot 日译页），每页 warm-up 1 次不计 + 计测 4 次取中位（再对 10 页取中位）
- 口径：warm-up 1 + ≥4 次计测、per-page median、再跨 10 页取 median；未做任何"显著提升"式表述
- 写范围：本目录 + `G:/CODEX/New Manga.workspace/task-envs/INFER-BASELINE-EP-1/**`；
  **未修改任何产品源码/配置/依赖清单**（`requirements*.txt`、`src/**`、`Cargo.toml` 零改动）

---

## 0. 结论（先行）

1. **默认 EP：DirectML（ORT-DML）。** 它不是"总是最快"，但它把两条检测链从 CPU 的
   ≈161–252 ms/页压到 **≈23–26 ms/页**，且**不需要 CUDA 运行时**、覆盖 NVIDIA/AMD/Intel，
   并与产品既有生产 pin（`onnxruntime-directml==1.24.4`）一致。
2. **CUDA 不是默认档的必要条件，但对两个模型是必要的**：`manga-ocr`（DML 97.87 ms vs CUDA 23.17 ms）
   与 `LaMa-fp32-512`（**DML 直接运行失败**，CUDA 76.92 ms）。
3. **PP-OCRv4 在 GPU 上反而更慢**：CPU 135.85 ms vs DML 250.92 ms vs CUDA 496.09 ms（动态 shape +
   逐框小批调用放大了 GPU 调度开销）→ OCR 默认留在 CPU EP，或改用批处理（本任务未测批处理，NOT_RUN）。
4. **"必须 torch 的模型"实测答案为：无。** RT-DETR-v2 已成功导出 ONNX（fixed，opset 17），
   CPU/DML/CUDA 三档均可加载运行，10/10 页检框数量与 torch 完全相同；manga-ocr 的 encoder/decoder
   ONNX 与 torch 输出**逐字符完全一致**；YOLO11s-seg / PP-OCRv4 / LaMa 本来就是 ONNX。
   torch 因此可退为**训练/导出期依赖**，不进主包。
5. 有一个**必须随包声明的许可后果**：现网 SFX 检测权重 `yolo11s-seg.onnx` 是 **AGPL-3.0**（ONNX
   metadata 自证），而本次候选的检测/OCR/修复权重均为 Apache-2.0；见 §5。

---

## 1. AC1 速度矩阵（暖机后 median ms/页；越小越好）

`—` = 该运行时无对应权重或未测。加粗 = 该模型最快档。

| 模型（类） | ORT-CPU | ORT-DML | ORT-CUDA | torch-CPU | torch-CUDA |
|---|---|---|---|---|---|
| **YOLO11s-seg 1024**（SFX 检测，AGPL-3.0） | 161.42 | **26.48**（6.10×） | 27.71（5.83×） | — | — |
| **RT-DETR-v2 640**（漫画检测，Apache-2.0）| 168.95¹ | **22.95**（7.36×¹） | 25.28（6.68×¹） | 251.78 | 40.82（6.17×） |
| **PP-OCRv4 det+rec**（OCR，Apache-2.0） | **135.85** | 250.92（0.54×） | 496.09（0.27×） | — | — |
| **manga-ocr**（OCR，Apache-2.0） | 72.52 | 97.87（0.74×） | **23.17**（3.13×） | 111.59 | 31.89（3.50×） |
| **LaMa fp32 512**（修复，Apache-2.0） | 1161.19 | **运行失败²** | **76.92**（15.10×） | — | — |
| **LaMa manga-dynamic 1024**（修复） | 3176.65 | 197.20（16.11×） | **137.79**（23.05×） | — | — |

¹ RT-DETR 的 ORT-CPU 基准是**本任务自行导出的 ONNX**（168.95 ms）；torch-CPU 原始框架为 251.78 ms。
倍率按同表内该行 CPU 基准计算：DML/ONNX-CPU = 7.36×，DML/torch-CPU = 10.97×。
² `lama_fp32.onnx`（512）在 DML 上 session 可建但 run 抛
`DmlFusedConv … 80070057 参数错误`（FFC `convl2l/Conv`+`Relu` 融合）；同一模型 CUDA 正常。
同一 DML 对 **dynamic 1024 变体**可跑（197.20 ms）→ DML 对 LaMa 的支持是**形状相关且不可靠**。
完整错误原文见 `dml-lama-probe.json`。

**矩阵怎么读（决策相关）**
- 检测链（两条）：GPU 收益最大且 DML≈CUDA（26.5 vs 27.7；23.0 vs 25.3）→ **DML 足够**。
- OCR 链：慢在"多次小张量调用 + 动态 shape"，不是算力不足 → 减慢 0.3–0.7×。
- 修复链：算力密集、纯卷积+FFT → CUDA 收益最大（15–23×）；DML 只有在 1024 动态变体上可用。

### 1.1 启动成本（冷进程，ms）

| 运行时 | import | 会话/模型构建 | 首帧 | 备注 |
|---|---|---|---|---|
| ORT-CPU | 66–89 | 78（yolo）/ 170–434（OCR）/ 5790–6860（LaMa） | ≈稳态 | 导入很轻；LaMa 图优化很重 |
| ORT-DML | 73–76 | 419–918（OCR/RT-DETR）/ **721（yolo）** / 4473–4488（LaMa） | ≈稳态 | DML 初始化本身 0.4–0.7 s |
| ORT-CUDA | 75–89 | 203（yolo）/ 292–697（OCR/RT-DETR）/ 3024–4479（LaMa） | ≈稳态 | 需 CUDA 12.8+cuDNN 9 |
| **torch-CPU / CUDA** | **1292–1313** | **2823–3321**（`from_pretrained`） | — | 冷启动比 ORT 多 **≈4.1–4.6 s** |

### 1.2 体积（MB）

| 资产 | 体积 |
|---|---|
| `yolo11s-seg.onnx` | 38.93 |
| RT-DETR-v2 原始 safetensors（torch 路线） | 171.54 |
| **RT-DETR-v2 导出 ONNX（fixed，本任务产出）** | **163.68** |
| `ch_PP-OCRv4_det + rec` | 4.53 + 10.35 = 14.88 |
| manga-ocr ONNX `encoder + decoder` | 327.54 + 112.04 = 439.58 |
| `lama_fp32` / `lama-manga-dynamic` | 198.41 / 196.74 |
| venv: `ort-dml`（含 DML 运行时） | 362.60 |
| venv: `ort-cuda`（含 CUDA EP 运行时） | 639.50 |
| venv: `torch-cuda` | **4709.80** |
| CUDA 12.8 + cuDNN 9 DLL（torch 轮子内，11 个 dll） | 1656.50 |

---

## 2. AC2 ONNX 导出可行性（逐候选，含失败原文）

| 候选 | 固定 shape | 动态 shape | opset | 结论 |
|---|---|---|---|---|
| **YOLO11s-seg**（现网 SFX） | 已是 ONNX `[1,3,1024,1024]` | 未测（仓库无 `.pt` 训练权重，无法重导） | 18 | **上游已导出**；动态 shape NOT_RUN（无源权重） |
| **RT-DETR-v2**（ogkalu，Apache） | ✅ 163.68 MB，导出 3.4 s | ✅ 163.8 MB，导出 3.3 s | **17** | **可导出**。但**动态图 ORT 不可用**：CPU `NOT_IMPLEMENTED: Cos(7)`、DML `transformer_memcpy: Provider type for Cos node … is not set`；**fixed 图 CPU/DML/CUDA 三档全部可加载**。→ **随包发 fixed**，batch 固定 1。导出一致性：logits maxAbs=1.46e-4、boxes maxAbs=2.10e-5；10/10 页检框数量与 torch 相同。 |
| **PP-OCRv4 det+rec** | 已是 ONNX（dynamic 维度内建） | 内建 | 12 | **上游已导出**（Paddle2ONNX），无需重导 |
| **manga-ocr**（encoder-decoder） | ✅ encoder 327.4 MB / decoder 112.0 MB，导出 2.2 s / 0.8 s | ✅ 动态轴同样成功 | **14** | **部分可行**：encoder/decoder 两张图可导出且与 torch **逐字符 100% 一致**（10/10 页，CPU 与 CUDA 均是）；但 **`generate()` 整图导出失败**：`RuntimeError: 0 INTERNAL ASSERT FAILED … alias_analysis.cpp:629 … no op for aten::full`。→ **不能"一个 ONNX 文件 = 一次 OCR"**，必须在 Python 里实现贪心解码循环。另：随包第三方导出（mayocream）**无 KV cache**，每 token 重跑完整 decoder（本次实测 24 步上限），torch 侧 `use_cache=True` 可用 → 增量解码是后续优化点，不是导出阻断。 |
| **LaMa** | 已是 ONNX（512 fixed, opset 17；manga-dynamic opset 18） | 已是 ONNX | 17 / 18 | **上游已导出**；无源权重，重导 NOT_RUN |

**AC2 总结**：三类模型全部走到了 ONNX 形态；唯一"半途"的是 encoder-decoder 结构的 manga-ocr
（图可导出、整调用不可导出，需要 Python 侧解码循环），这与业界对该架构的常规处理一致。

---

## 3. AC1 精度（同一模型跨 EP/跨运行时一致性，非"模型本身准确率"）

模型权重是给定的，因此本任务测的是**换 EP 后答案是否变化**（参考 = 同一模型 CPU 运行）：

| 用例 | 指标 | 结果 |
|---|---|---|
| YOLO11s-seg DML | 框 IoU@0.5 匹配 / 召回 / 精确率 / 平均 IoU | 8/8 匹配，recall **1.0**，precision **1.0**，meanIoU **1.0** |
| YOLO11s-seg CUDA | 同上 | 8/8 匹配，recall 1.0，precision 1.0，meanIoU **0.9963** |
| PP-OCRv4 DML | det 框召回 / 文本完全一致 / 字符准确率 | det recall **1.0**；179/179 行**完全一致**；charAcc **1.0** |
| PP-OCRv4 CUDA | 同上 | det recall 1.0；文本完全一致 **0.9832**（176/179）；charAcc **0.9860** |
| LaMa dynamic DML | PSNR / SSIM（vs CPU 输出） | **109.89 dB** / **1.000000** |
| LaMa dynamic CUDA | 同上 | 71.98 dB / 0.999995 |
| LaMa fixed512 CUDA | 同上 | 19.02 dB / 0.999977；逐页 maxAbsDiff 4.41–10.27（0–1 像素域）→ **局部数值离群，非结构性偏差**（SSIM≈1），仍建议发 DML 不可用时优先 dynamic 变体 |
| **manga-ocr：torch vs ONNX** | 文本完全一致 / 字符准确率 | CPU: **10/10 完全一致，charAcc 1.0**；CUDA: **10/10 完全一致，charAcc 1.0** |
| **RT-DETR：torch vs 自导 ONNX** | 检框数量 / 导出期张量差 | 10/10 页框数完全相同（7,1,2,15,11,14,14,3,17,12）；logits maxAbs 1.46e-4、boxes maxAbs 2.10e-5 |

原始：`parity.json`（每页明细）、`bench-matrix.json`（每次运行原始 runsMs）、`export-*.json`。

---

## 4. AC3 决策矩阵与建议

### 4.1 模型 × EP 决策矩阵

| 模型 | 默认 EP | 可选包 EP | 进主包？ | 理由（数字见 §1） |
|---|---|---|---|---|
| YOLO11s-seg（SFX 检测，AGPL） | **DML** | CPU 回退 | ✅（38.93 MB） | DML 26.48 ms，CPU 161.42 ms；检测是每页必跑路径 |
| RT-DETR-v2 ONNX（漫画检测，Apache） | **DML** | CUDA | ✅（163.68 MB） | DML 22.95 ms；torch 路线 251.78（CPU）/40.82（CUDA），ONNX 全面更优 |
| PP-OCRv4 det+rec | **CPU** | DML/CUDA（需批处理优化） | ✅（14.88 MB） | CPU 135.85 ms 比 DML 250.92 / CUDA 496.09 更快；体积小、无 GPU 依赖 |
| manga-ocr | **CUDA**（无 CUDA 时 CPU） | CPU（72.52 ms） | ✅（439.58 MB） | CUDA 23.17 ms；DML 97.87 ms 比 CPU 还慢 → DML 不应作为其默认 |
| LaMa manga-dynamic | **CUDA**（无 CUDA 时 CPU，DML 可用但不稳） | DML 197.20 ms | ✅（196.74 MB） | CUDA 137.79 ms；`lama_fp32` 在 DML 上运行失败 → 主包若只带一个 LaMa，带 dynamic |

### 4.2 建议（可直接执行）

- **主包默认 EP = DirectML**（`onnxruntime-directml`，沿用现网 pin 1.24.4 或将随 ORT 版本升级重测）。
  理由：检测链 0.6–1.0 折时间、无需 CUDA 运行时、硬件覆盖面最大、与既有生产路径一致。
- **主包内容（≤2 GB 预算）**：
  `onnxruntime-directml` 运行时 362.60 MB + 模型 38.93 + 163.68 + 14.88 + 439.58 + 196.74 =
  **≈ 1216.4 MB（1.19 GiB）**，落在 ≤2 GB 内，余量 ≈0.8 GB 留给音效/字体/翻译提示等。
  → 主包即可提供：SFX 检测（DML）、漫画检测（DML）、OCR（CPU）、manga-ocr（CPU 回退）、修复（CPU 回退）。
- **可选高性能包（≤8 GB 预算）**：`onnxruntime-gpu` 639.50 MB + CUDA 12.8/cuDNN 9 运行时
  1656.50 MB + 可选 torch-cuda 4709.80 MB（若保留训练/调试能力）→ 仅 ORT 部分 **≈2.30 GB**，
  含 torch **≈7.01 GB**，均在 ≤8 GB 内。提供：manga-ocr CUDA（23.17 ms）、LaMa CUDA（137.79 ms）。
- **必须 torch 的模型：无。** 全部候选均有可用 ONNX；torch 仅作为**训练/导出期**依赖
  （`transformers` 仅用于导出 RT-DETR/manga-ocr）。前提：随包发**本任务导出的 RT-DETR fixed ONNX**
  与 **manga-ocr encoder/decoder ONNX**，并把 ONNX 的 sha256 钉进模型清单。
  ⚠ 导出环境是 transformers **5.21.0**，产品 pin 为 **5.17.0**：建议**只钉 ONNX 产物 + sha256**，
  不要求产品运行时复现导出（如要在 5.17.0 下重导，需复核 fixed 图仍可在 ORT 三档加载）。
- **不要做的事**：不要默认把 OCR 放到 GPU（更慢）；不要把 `lama_fp32`(512) 放进 DML 主路径（运行失败）；
  不要依赖动态 shape 的 RT-DETR ONNX（ORT 不可加载）。

---

## 5. AC5 许可核查（一手来源 + 与 GPL-3.0 产品分发的关系）

| 组件 | 许可 | 来源（一手） | 与产品（GPL-3.0 分发）的关系 |
|---|---|---|---|
| `yolo11s-seg.onnx`（现网 SFX） | **AGPL-3.0** | ONNX `metadata_props.license` = `AGPL-3.0 License (https://ultralytics.com/license)`；作者 Ultralytics | **强 copyleft**：与 GPL-3.0 组合后整体须按 **AGPL-3.0** 分发（AGENTS.md 已写明该口径）。若想彻底回避，须换 Apache 检测权重（本任务未训练替代品，NOT_RUN） |
| RT-DETR-v2 `ogkalu/comic-text-and-bubble-detector` | **Apache-2.0** | HF model card metadata | 与 GPL-3.0 **兼容**（可并入 GPLv3 作品） |
| PaddleOCR PP-OCRv4 权重（`SWHL/RapidOCR` 分发） | **Apache-2.0** | HF card metadata（上游 PaddleOCR 亦 Apache-2.0） | 兼容 |
| `kha-white/manga-ocr-base` | **Apache-2.0** | HF card metadata | 兼容 |
| `mayocream/manga-ocr-onnx`（ONNX 导出） | **Apache-2.0** | HF card metadata | 兼容（导出者声明 Apache-2.0） |
| `Carve/LaMa-ONNX`、`ogkalu/lama-manga-onnx-dynamic` | **Apache-2.0** | HF card metadata | 兼容 |
| `onnxruntime` / `-directml` / `-gpu` | MIT | PyPI 元数据 | 兼容 |
| `torch` (+ `torchvision`) | BSD-3-Clause | PyPI 元数据 | 代码兼容；**但 cu128 轮子捆绑 NVIDIA CUDA/cuDNN（1.66 GB）受 NVIDIA 专有 EULA 约束，不是开源许可** → 可选包分发需附 NVIDIA 许可文本，且不得声称整包为纯开源 |
| `transformers` | Apache-2.0 | PyPI 元数据 | 兼容（仅导出期用） |

**许可结论**：主包（ORT-DML + Apache 权重 + 现网 AGPL YOLO）→ 产品仍须整体声明 **AGPL-3.0**；
可选 CUDA 包额外携带 **NVIDIA 专有运行时**，需单独许可声明。若未来决定"整包纯 GPL-3.0/AGPL-3.0 开源"，
唯一冲突项是 `yolo11s-seg`（AGPL，可接受）与 NVIDIA cuDNN/CUDA（专有，必须单独声明、不可再许可）。

---

## 6. NOT_RUN / BLOCKED（如实）

| # | 项 | 状态 | 原因 |
|---|---|---|---|
| 1 | YOLO11s-seg 动态 shape 重导出 | NOT_RUN | 仓库内无该模型的 `.pt` 训练权重（只有 ONNX 与不同代的 `yolo26n.pt`），无法重导 |
| 2 | PP-OCRv4 / LaMa 重新导出 | NOT_RUN | 同理无 Paddle/torch 源权重；已用的 ONNX 由上游导出，本任务只记录其 opset/shape 事实 |
| 3 | PP-OCR 批处理（rec 多框批推理） | NOT_RUN | 未实现批处理路径；这是 OCR 在 GPU 上反慢的最可能修复点，需单独任务 |
| 4 | MangaOCR 带 KV cache 的增量解码 | NOT_RUN | 随包第三方 ONNX 无 past_key_values 输入；重导带 cache 的 decoder 需要额外导出+验证工作 |
| 5 | 绝对精度（检测 IoU vs 人工 GT、OCR 字符准确率 vs 人工转录、修复 PSNR/SSIM vs 原图） | NOT_RUN | 样本目录内 `COO/Manga109Dialog` 标注与本机 10 页样本**页数不匹配**（XML 最多 152 页，样本卷 169 页），无法对齐 GT；本任务因此只测"跨 EP/跨运行时一致性"（见 §3），不冒充绝对精度 |
| 6 | TensorRT EP | NOT_RUN | `ort-cuda` 暴露 TensorrtExecutionProvider，但未安装 TensorRT 库；不在三档对比范围内 |
| 7 | 产品 pin 的 ORT 1.24.4 CUDA 版 | BLOCKED（环境） | `onnxruntime-gpu==1.24.4` 要求 **CUDA 13.x**，本机无 CUDA 13 运行时；实测采用 **1.22.0（CUDA 12.8 构建）** + torch cu128 的 CUDA/cuDNN DLL。若要严格对齐产品 pin，需要 CUDA 13 运行时（另装 ≈2–3 GB） |
| 8 | torch 2.12+cu130 与 Saber 对齐 | NOT_RUN | 本机装的是 torch 2.11.0+cu128；cu130 轮子未验证 |

仓库权限说明（不影响结论）：`onnxruntime-gpu 1.31.1`（默认最新）**CUDA EP 静默回退 CPU**
（缺 `cublasLt64_13.dll`），本任务的 harness 因此**硬断言** EP 必须真正激活，否则该次结果作废——
这也是把"CUDA EP 未生效却报 GPU 数字"这一常见坑挡住的机制。

---

## 7. 可复跑（AC4）

全部脚本在 `G:/CODEX/New Manga.workspace/task-envs/INFER-BASELINE-EP-1/scripts/`，
venv 在 `.../venvs/{ort-dml,ort-cuda,torch-cuda,ocr-ref}`，原始 JSON/日志在 `.../results`、`.../logs`。

```powershell
$R = "G:\CODEX\New Manga.workspace\task-envs\INFER-BASELINE-EP-1"
# 0) 环境（PyPI 官方索引；互斥 ORT 轮子 → 4 个独立 venv）
pwsh -File "$R\scripts\setup-venvs.ps1"      # ort-dml / ort-cuda / torch-cuda / ocr-ref
pwsh -File "$R\scripts\download-models.ps1"  # 权重进 workspace，manifest 记 sha256
# 1) AC1 速度矩阵（yolo/ppocr/mangaocr/lama × cpu/dml/cuda）
pwsh -File "$R\scripts\run-matrix.ps1"
# 2) torch 基线（RT-DETR-v2 + manga-ocr，CPU/CUDA）
pwsh -File "$R\scripts\run-torch.ps1"
# 3) AC2 导出（RT-DETR fixed/dynamic、MangaOCR enc/dec/full-generate、已发布件事实）
$env:RTDETR_WEIGHTS = "G:\CODEX\New Manga\apps\desktop\src-tauri\target\release\resources\core-sidecar\models\detector\ogkalu-comic-text-and-bubble-detector"
$env:MANGAOCR_WEIGHTS = "$R\models\manga-ocr-base"
& "$R\venvs\torch-cuda\Scripts\python.exe" "$R\scripts\export_onnx.py" --target rtdetr   --out "$R\results\exports" --page "$R\fixtures\pages10\p01_manga_001.jpg"
& "$R\venvs\torch-cuda\Scripts\python.exe" "$R\scripts\export_onnx.py" --target mangaocr --out "$R\results\exports" --page "$R\fixtures\pages10\p01_manga_001.jpg"
# 4) 精度一致性 + 体积/启动
& "$R\venvs\ort-dml\Scripts\python.exe" "$R\scripts\parity2.py" --bench "$R\results" --dumps "$R\results\parity-runs" --out "$R\results\parity2.json"
pwsh -File "$R\scripts\sizes.ps1"
```

CUDA EP 运行前提（本任务实测组合，已写进 `run-matrix.ps1` 注释）：
`onnxruntime-gpu==1.22.0` + `PATH` 前置 `venvs\torch-cuda\Lib\site-packages\torch\lib`
（提供 CUDA 12.8 / cuDNN 9 DLL）；`onnxruntime-gpu>=1.31` 需 CUDA 13，本机不可用。

---

## 8. 证据索引（本目录）

| 文件 | 内容 |
|---|---|
| `bench-matrix.json` | 全部 19 次 bench 运行：per-page median/min/max、runsMs、import/会话/首帧成本、EP 实际激活列表 |
| `parity.json` | 跨 EP / 跨运行时一致性：逐页明细 + 汇总 + torch-vs-ONNX |
| `export-rtdetr.json` | RT-DETR fixed/dynamic 导出结果 + 张量级 parity |
| `export-mangaocr.json` | encoder/decoder 导出 + `generate()` 整图失败原文 + KV cache 事实 |
| `export-shipped.json` | 已发布 ONNX（YOLO/PP-OCR/LaMa）的 opset 与形状事实 |
| `sizes-and-startup.json` | 模型/依赖/CUDA DLL 体积 + 各 run 的 import/会话/首帧成本 |
| `dml-lama-probe.json` | LaMa 在 DML/CPU 上的失败原文（GBK 错误已解码） |
| `models-manifest.json` | 所有权重来源 URL + 字节数 + sha256 |
| `licenses.md` | 逐组件许可与 GPL-3.0 兼容结论（AC5） |
| `REPORT.md` | 本文件 |
