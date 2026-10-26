# AC5 许可核查：逐组件许可与 GPL-3.0 产品分发关系

核查时间：2026-10-27。一手来源：ONNX 内嵌 metadata、HuggingFace model card 的 `license` 元数据
（`https://huggingface.co/api/models/<repo>` 的 `cardData.license`，本任务直接查询）、PyPI 包元数据。

## 1. 权重

| 组件 | 用途 | 许可 | 一手来源 | 与 GPL-3.0 分发 |
|---|---|---|---|---|
| `yolo11s-seg.onnx`（现网 SFX 检测） | SFX/气泡/文字/分镜检测 | **AGPL-3.0** | ONNX `metadata_props`：`license = "AGPL-3.0 License (https://ultralytics.com/license)"`、`author = Ultralytics`、`version = 8.4.172` | **强 copyleft**。并入产品后，产品整体须按 **AGPL-3.0** 分发（含网络服务条款的传染性）。AGENTS.md 已确立该口径：「若集成 AGPL-3.0 组件如 Ultralytics，则整体按 AGPL-3.0 声明」。可保留；不可改为 GPL-3.0-only。 |
| `ogkalu/comic-text-and-bubble-detector`（RT-DETR-v2） | 漫画文字/气泡检测 | **Apache-2.0** | HF card metadata | 兼容（Apache-2.0 可并入 GPLv3 作品；其专利授权条款单向兼容） |
| `SWHL/RapidOCR` 分发的 `ch_PP-OCRv4_det_infer` / `ch_PP-OCRv4_rec_infer` | OCR 检测 + 识别 | **Apache-2.0** | HF card metadata（上游 PaddleOCR 同为 Apache-2.0） | 兼容 |
| `kha-white/manga-ocr-base` | 日文 OCR | **Apache-2.0** | HF card metadata | 兼容 |
| `mayocream/manga-ocr-onnx`（encoder/decoder ONNX 导出） | 日文 OCR（ONNX 形态） | **Apache-2.0** | HF card metadata | 兼容（导出者声明 Apache-2.0） |
| `Carve/LaMa-ONNX`（`lama_fp32.onnx`） | 修复 | **Apache-2.0** | HF card metadata | 兼容 |
| `ogkalu/lama-manga-onnx-dynamic`（`lama-manga-dynamic.onnx`） | 修复（漫画域） | **Apache-2.0** | HF card metadata | 兼容 |

## 2. 运行时与库

| 组件 | 许可 | 说明 |
|---|---|---|
| `onnxruntime` / `onnxruntime-directml` / `onnxruntime-gpu` | **MIT** | 兼容；`-directml` 轮子内含 DirectML（微软，MIT） |
| `torch` / `torchvision`（cu128 轮子） | **BSD-3-Clause**（代码） | 代码兼容。**但 cu128 轮子捆绑 NVIDIA CUDA/cuDNN 二进制（本任务实测 1656.5 MB / 11 个 dll）**，受 **NVIDIA 专有 EULA** 约束：不是开源许可，分发可选包时必须附 NVIDIA 许可文本，且**不得声称整包为纯开源**。 |
| `transformers` | **Apache-2.0** | 兼容（本任务只在导出期使用） |
| `numpy` / `pillow` / `opencv-python` | BSD / MIT-类（Pillow=HPND） / Apache-2.0 | 兼容 |
| `rapidocr_onnxruntime`（仅用于 CPU 参考 OCR，非产品路径） | Apache-2.0 | 兼容 |

## 3. 结论

1. **主包**（ORT-DML + YOLO11s-seg + RT-DETR-v2 ONNX + PP-OCRv4 + manga-ocr ONNX + LaMa）
   → 唯一强 license 项是 Ultralytics 的 **AGPL-3.0** ⇒ 产品按 **AGPL-3.0** 整体声明。
   其余全部 Apache-2.0/MIT ⇒ 无额外义务。
2. **可选 CUDA 包** → 额外引入 **NVIDIA 专有 CUDA/cuDNN 运行时**（经 torch 轮子或系统 CUDA），
   必须在安装包内附 NVIDIA EULA 文本，并在许可三件套中单独列出；不得再许可为 GPL/AGPL 代码。
   `onnxruntime-gpu` 自身仍是 MIT，专有部分只来自 CUDA/cuDNN 二进制。
3. **torch 不进主包**（本任务 §4 结论：无模型必须 torch）⇒ 主包可以保持"纯 Python 解释器 +
   Apache/MIT/AGPL 权重 + DirectML"，不携带任何 NVIDIA 专有二进制。
4. 若要进一步"去 AGPL"：需以 Apache-2.0 权重替代 `yolo11s-seg` 的 SFX 能力。本任务**未训练替代模型**
   （NOT_RUN）；RT-DETR-v2（Apache-2.0）已可覆盖 text/bubble/text_free 检测，但**不含 SFX 类别**，
   不能直接替代现网 SFX 路径。
