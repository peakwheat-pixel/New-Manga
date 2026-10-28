# THIRD_PARTY_LICENSES — New Manga

本文件登记直接依赖与随包资产的许可证。**发行前必须复核**；标 `[待核实]` 的项在对应发行 Gate 前必须补成一手结论。

## 1. 运行时依赖（Python Core）

| 组件 | 许可证（核实状态） | 说明 |
|---|---|---|
| onnxruntime / onnxruntime-directml | MIT | 推理引擎（DML EP 生产默认） |
| torch / torchvision | BSD-3-Clause | 检测链（CPU wheels；CUDA 版若引入需单独裁决） |
| transformers | Apache-2.0 | RT-DETR 等模型加载 |
| python-doctr | Apache-2.0 | 文本检测 |
| Pillow | HPND (Python Imaging Library License) | 渲染/图像 |
| opencv (cv2) | Apache-2.0 | 图像处理 |
| pypdfium2 | Apache-2.0 / BSD-3-Clause（组合） [待核实] | PDF 渲染 |
| PySide6 | **LGPL-3.0** | 当前仅用于 `QtImageDecoder`；AD-002 要求移除（S1） |
| numpy / scipy | BSD-3-Clause | 数值 |
| pydantic | MIT | 契约模型 |
| pytest 等测试依赖 | MIT | 不进发行包 |

## 2. 前端/宿主依赖

| 组件 | 许可证 | 说明 |
|---|---|---|
| Avalonia（目标栈） | MIT | 新 UI 框架 |
| .NET / WPF 相邻库 | MIT | 运行时 |
| React / Vite / TypeScript（旧壳，S5 退役） | MIT | 旧前端 |
| Tauri / wry（旧壳，S5 退役） | MIT / Apache-2.0 | 旧宿主 |

## 3. 模型权重（`models` 发行包随包分发；`base` 发行包不含）

`models` 变体把完整权重随包放在 `app/core-sidecar/models/`。以下为 REPACK-5 实测清单（路径相对 `models/`，字节/ sha256 与包内文件逐一核对；一手许可来源与抓取日期见 `verification/AGPL-RELEASE-1/weights-licenses.json`）：

| 文件 | 字节 | sha256 | 用途 | 许可证（核实状态） |
|---|---|---|---|---|
| `detector/yolo11s-seg.onnx` | 40,824,255 | `944e811410933ad6ff8d32446fcc9eef90fb463794e1874ce83035e83acd418d` | SFX 检测 | **AGPL-3.0（Ultralytics YOLO11s-seg）已核实** |
| `detector/rtdetr-v2-fixed.onnx` | 171,618,071 | `c7fb5af1a8982416b56955e621c1b10397730807956998066e2fbc132c77bbc3` | 文本/气泡检测 | Apache-2.0（HF 模型卡）**[待核实，不阻断本卡]** |
| `ocr/manga-ocr-onnx/encoder_model.onnx` | 343,454,249 | `15fa8155fe9bc1a7d25d9bb353debaa4def033d0174e907dbd2dd6d995def85f` | 日文 OCR | MangaOCR 上游 **[待核实，不阻断本卡]** |
| `ocr/manga-ocr-onnx/decoder_model.onnx` | 117,480,262 | `ef7765261e9d1cdc34d89356986c2bbc2a082897f753a89605ae80fdfa61f5e8` | 日文 OCR | 同上 **[待核实，不阻断本卡]** |
| `ocr/manga-ocr-onnx/{config,generation_config,preprocessor_config,special_tokens_map,tokenizer_config,vocab.*}` | 2–77 KB 级 | 见 `weights-licenses.json` | OCR 配置/词表（非权重） | 随上游 MangaOCR **[待核实，不阻断本卡]** |

**YOLO11s-seg 的 AGPL-3.0 一手依据**：
1. 该 ONNX 文件自身元数据包含 `Ultralytics YOLO11s-seg model trained on …` 与 `AGPL-3.0 License (https://ultralytics.com/license)`（扫描记录见 `verification/AGPL-RELEASE-1/weights-licenses.json`）。
2. Ultralytics 官方许可页（https://www.ultralytics.com/license，抓取日期记录于证据 JSON）明确 YOLO 模型按 **AGPL-3.0** 提供。
3. Ultralytics 仓库 `LICENSE`（https://raw.githubusercontent.com/ultralytics/ultralytics/main/LICENSE）与 GNU 官方 AGPL-3.0 全文逐字节一致（sha256 `0d96a4ff…`）。

**发行后果（强制）**：
- **models** 变体包含上述 AGPL-3.0 权重 → **该发行包整体按 AGPL-3.0 分发**；随包附 `LICENSE-AGPL-3.0.txt` 全文，并提供对应源码（本仓库/发行页）。
- **base** 变体不含任何模型权重 → 仍按 **GPL-3.0-or-later** 分发；其随包的 `LICENSE-AGPL-3.0.txt` 仅作为可选组件许可说明。

[待核实] 项（RT-DETR / MangaOCR 配置与权重）不作为本卡阻断项；在下一次发行 Gate 前补成一手结论。

## 4. 字体

| 字体 | 许可 | 处置 |
|---|---|---|
| Source Han Sans / Noto Sans（思源） | OFL-1.1 | 可随包 |
| `msyh.ttc` / `msyhbd.ttc` | Microsoft 系统字体 | **不得随包**；只能依赖系统已安装 |
| `STKAITI` / `STZHONGS` / `STSONG` / `STFANGSO`（华文） | 商业字体 | **不得随包** |

## 5. 发行 Gate

- [ ] 每次发行前重跑本表逐项核对（一手 license 文件/模型卡）。
- [x] models 变体含 AGPL 组件（Ultralytics YOLO11s-seg）→ `NOTICE` 与发行页明确 **AGPL-3.0**，随包附 `LICENSE-AGPL-3.0.txt` 全文（AGPL-RELEASE-1 落地）。
- [ ] base 变体不含权重 → 保持 GPL-3.0-or-later 声明；包内 4 个许可文件与仓库根逐字节一致（`package.ps1` 校验）。
- [ ] 输出 `THIRD_PARTY_LICENSES` 与源码同包/同页提供。
