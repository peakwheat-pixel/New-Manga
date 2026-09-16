# TASK-016：OCR 与检测路线研究与实验记录

> 状态：`As-Is` 实验记录；固定基线 `f9edd68845d4a1ee5d42d9fdcf1a304dc3fa2f86`。本文件不把实验结果升级为产品需求，也不替代 Codex 的独立 Review。

## 1. 研究范围与来源

检验三类候选：日漫日文 OCR、PaddleOCR Korean（检测 + 识别）和 OpenAI-compatible Vision（检测/识别 JSON 输出）。版本和许可信息截至 2026-09-16 以官方一手来源为准：

| 路线 | 候选 / 版本 | 许可证事实 | 适配边界 | 官方来源 |
|---|---|---|---|---|
| 日漫 OCR | `manga-ocr` v0.1.16，`kha-white/manga-ocr@v0.1.16` | 仓库页面标为 Apache-2.0；模型权重未下载，权重独立许可仍需随实际文件核对 | 识别路线，适合已有 Region crop；本身不提供检测框 | [仓库 README](https://github.com/kha-white/manga-ocr)、[v0.1.16 release](https://github.com/kha-white/manga-ocr/releases/tag/v0.1.16) |
| 韩文 OCR/检测 | PaddleOCR v3.7.0，`korean_PP-OCRv5_mobile_rec` | PaddleOCR 项目/pyproject 标为 Apache License 2.0；韩文模型权重的下载条款需在实际下载时单独留档 | 共同前置检测器 + 韩文/英文识别；模型输出含 polygon 与 score | [v3.7.0 release](https://github.com/PaddlePaddle/PaddleOCR/releases/tag/v3.7.0)、[官方 C++ OCR 文档（韩文模型）](https://github.com/PaddlePaddle/PaddleOCR/blob/main/docs/version3.x/inference_deployment/local_inference/cpp/OCR.md)、[pyproject license](https://github.com/PaddlePaddle/PaddleOCR/blob/main/pyproject.toml) |
| OpenAI-compatible Vision | `microsoft/Phi-3.5-vision-instruct` + vLLM v0.29.0 | Phi 模型为 MIT；vLLM 为 Apache-2.0；二者许可分别保存 | 通过 `/v1/chat/completions` 请求图片和结构化 polygon；不自动赋予 RegionID | [Phi 模型卡](https://huggingface.co/microsoft/Phi-3.5-vision-instruct)、[Phi LICENSE](https://huggingface.co/microsoft/Phi-3.5-vision-instruct/blob/main/LICENSE)、[vLLM v0.29.0](https://github.com/vllm-project/vllm/releases/tag/v0.29.0)、[vLLM OpenAI-compatible server](https://docs.vllm.ai/en/latest/serving/online_serving/openai_compatible_server/) |
| OpenAI-compatible Vision | `Qwen/Qwen2.5-VL-7B-Instruct` + vLLM v0.29.0 | Hugging Face 模型卡显示 `apache-2.0`；模型仓库同时提供 Qwen LICENSE AGREEMENT，实际再分发必须以随权重文件提供的协议为准，需法务复核 | 可请求多语种视觉文字与坐标；输出 schema/坐标仍需 harness 校验 | [Qwen 模型卡](https://huggingface.co/Qwen/Qwen2.5-VL-7B-Instruct)、[Qwen LICENSE](https://huggingface.co/Qwen/Qwen2.5-VL-7B-Instruct/blob/main/LICENSE)、[Qwen 官方仓库](https://github.com/QwenLM-corp/Qwen2.5-VL) |

官方材料支持候选的能力/许可声明，不构成对本项目准确率、速度或商用合规的保证。vLLM 官方文档明确提供 OpenAI-compatible Chat API；`Phi-3.5-vision-instruct` 是其多模态示例之一。

## 2. 实验环境与前提

| 项 | 实测值 |
|---|---|
| 被测基线 | `f9edd68845d4a1ee5d42d9fdcf1a304dc3fa2f86` |
| OS / 架构 | Windows 11 `10.0.26200` / AMD64 |
| Python | 3.12.3（`G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe`） |
| GPU | NVIDIA GeForce RTX 5070 Ti，16303 MiB，driver 616.92；探测时已用 4094 MiB |
| Qt 平台 | `QT_QPA_PLATFORM` 未设置（`None`）；样本使用 PySide6 6.11.2 生成 |
| 已安装 Provider 依赖 | `manga_ocr`、Pillow、torch、transformers、paddleocr`、`paddle`、onnxruntime、openai` 均未发现 |
| 模型权重 Hash | `NOT_AVAILABLE`；没有下载权重 |
| API | 未发现 `TASK016_OPENAI_BASE_URL`/`OPENAI_BASE_URL` 与对应 model 配置；未发出网络请求 |

GPU 存在不等于本次具备可运行模型；缺少依赖、权重或端点时按验收要求标记 `BLOCKED/NOT_RUN`。

## 3. 自制样本与 Hash

样本由 `experiments/TASK-016/generate_samples.py` 通过 Windows Qt 字体栅格化生成，不含第三方漫画素材。人工标注只用于误差比较和坐标映射，不是产品阈值。

| sample_id | 覆盖场景 | 尺寸 | 参考 Region 数 | SHA-256 |
|---|---|---:|---:|---|
| `jp-horizontal` | 日文横排 | 800×260 | 1 | `fe18507633d389bbbad0dbbe163c192cedc7509a4ad0418b557e3fa9e68f1bfb` |
| `jp-vertical` | 日文竖排 | 420×620 | 1 | `bda605e03b715fcbca25dd3492b6ca83d0e6d63bc49468da3e3933128d014f66` |
| `ko-horizontal` | 韩文横排 | 800×260 | 1 | `8700cbb9e9bc13af23f70e19c52ae292147a67ce0ddb33939289f9bf62fb9c36` |
| `art-text` | 旋转、描边/艺术字 | 900×420 | 1 | `109704b18c4917cb068e38f9e9f213fe81389bd36f1cd6c6175c977b00ceaada` |
| `long-tile` | 长图 Tile 全局坐标 | 900×1900 | 4 | `c560a0c2fca88503a72a99e775b3e25ada7b114918868379ac38247b6cc979d1` |

manifest SHA-256：`5e988b9b65d85ef87d947cbd1a9f74b18af3e4c9fb676a5ae82022c8d5fe4cf3`。

`long-tile` 的 Tile origin 为 `[0,0]`、`[0,600]`、`[0,1200]`、`[0,1800]`，Tile 高度分别为 700、700、700、100，存在 100 像素重叠。示例 `long-02` 的 Tile-local 点 `[80,160]` 映射为 page-global `[80,760]`。

## 4. 输出协议与已执行实验

实验 harness 的统一记录字段为 `sample_id`、`region_id`、`text`、`polygon`、`reading_order`、`coordinate_space`、`latency_ms`、RSS/VRAM。它仅是实验协议：

- PaddleOCR 作为检测 + 识别候选；其 polygon 初始视作 page 坐标，原始顺序保留并单独记录。
- Manga-OCR 是 recognition-only 候选；没有 detector 时仅允许单 Region crop，不伪造检测结果。
- Vision 路线要求 JSON polygon，但 harness 对模型返回使用 `unmapped-*` 临时标识；不会把模型猜测当作业务 RegionID。
- 只有显式配置的 fallback 才允许进入 fallback 分支；无配置时为 `BLOCKED`。
- Tile-local polygon 必须加 Tile origin 才能进入 `page-global`；输入为空、origin 错误和未知坐标空间会失败。

### 协议自检

命令：

```powershell
$env:PYTHONPATH='experiments/TASK-016'
$env:PYTHONDONTWRITEBYTECODE='1'
G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe -m unittest discover -s experiments/TASK-016 -p 'test_*.py' -v
```

结果：退出码 0，`4 passed, 0 skipped`。覆盖单 Region ID 保留、Tile 全局坐标、稳定阅读顺序和无配置 fallback 阻断。

### Provider 缺依赖/端点探测

命令：

```powershell
$env:PYTHONPATH='experiments/TASK-016'
$env:PYTHONDONTWRITEBYTECODE='1'
G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe experiments/TASK-016/run_experiment.py `
  --manifest experiments/TASK-016/samples/manifest.json `
  --output experiments/TASK-016/results/probe.json
```

结果：退出码 0；15 条记录全部 `BLOCKED`，并保持 `recognition_errors=NOT_RUN`、`coordinate_order=NOT_RUN`、耗时/RAM/VRAM 为 `NOT_RUN/null`、模型 Hash 为 `NOT_AVAILABLE`。

| Provider | 样本数 | 状态 | 原因 |
|---|---:|---|---|
| manga-ocr | 5 | BLOCKED | 缺少 `manga_ocr` |
| PaddleOCR Korean | 5 | BLOCKED | 缺少 `paddleocr` 和/或 `paddle` |
| OpenAI-compatible Vision | 5 | BLOCKED | 缺少 endpoint/model 配置 |

显式 `--run-models` 复核同样退出码 0，15 条均为 `BLOCKED`（没有安装、下载或联网副作用）；该输出保存为 `experiments/TASK-016/results/model-run-blocked.json`，SHA-256 为 `7a8b0afd78a5bab6e714caf88d40864297416fd52340e2483980aeda6a61be0e`。

因此本轮没有可诚实报告的识别错误率、坐标误差、阅读顺序错误、延迟、RAM 或 VRAM 质量数据；这些项目不是零，也不是 PASS，而是 `NOT_RUN`。`probe.json` SHA-256 为 `bd33d38fd62ce3e268c168eaa22f5bfe1b352839bbb4d26a60dbd820bde18ee4`。

## 5. 低质量与失败 fallback

`art-text` 和 `long-tile` 已作为输入样本生成，但没有模型运行条件，故低质量/艺术字/长图 OCR 质量均为 `NOT_RUN`。harness 已验证无配置路线时不静默切换、不生成伪造文本；模型初始化/请求异常会落到 `FAIL`，缺依赖/缺配置落到 `BLOCKED`。这只证明实验控制流，不证明任何 Provider 的 OCR 质量。

## 6. 初步建议与限制

1. 日文方向优先把 Manga-OCR 作为单 Region recognition 候选，把检测交给独立 detector；必须在安装并 hash 实际权重后再测横/竖排、低质量和艺术字。
2. 韩文方向优先验证 PaddleOCR 的 Korean recognition model 与 detector 输出，重点检查多框排序、韩文/英文混排和 Tile 坐标。
3. Vision 方向先用 Phi 路线做协议可行性实验；Qwen 路线要先记录随权重提供的 Qwen LICENSE AGREEMENT，不能只依赖模型卡的 `apache-2.0` 标签。
4. 需要在隔离实验环境取得 Provider 依赖、模型权重 Hash 或合法 endpoint 后，重跑同一 manifest；性能应记录预热、运行次数、P95、RSS 和 VRAM，模型质量应按人工标注计算文本/框/顺序误差。

以上是实验候选和证据边界，不是 OCR Provider 选型定案，也不自动修改任何产品需求或生产接口。

## 附：candidate metadata 一律为 unverified（Review R-003）

本文件与前序章节中出现的**任何版本号、许可名称或模型标识**，均属 **unverified candidate metadata**：
它们来自仓库文档的既有记述或候选表，**未经本环境联网核实**。本实验环境 `huggingface.co` 不可达、
未安装任何候选依赖，因此：

- 版本号（如 `manga-ocr 0.1.16`、`PaddleOCR 3.7.0`、`vLLM 0.29.0`）**不作为事实断言**；
- 许可（如 Apache-2.0 / MIT）**仅为上游自述**，且**模型权重条款可能与代码许可不同**，不得据此做合规决策；
- `experiments/TASK-016/run_experiment.py` 的 `CANDIDATES` 表已把每条记录标为 `metadata_status: "UNVERIFIED"`，
  并在 `version`/`license` 字段前加 `UNVERIFIED —` 前缀；
- 权威确认需在有网络的环境完成，并单独核实**权重**的授权条款。
