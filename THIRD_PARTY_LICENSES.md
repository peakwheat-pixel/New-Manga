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

## 3. 模型权重（不随本仓库代码分发）

| 模型 | 用途 | 许可证（核实状态） | 备注 |
|---|---|---|---|
| YOLO11s-seg（v2b pin） | SFX 检测 | **AGPL-3.0（Ultralytics）** | 若进主安装包 → 整体须 AGPL-3.0 声明；否则单独下载/可选包 |
| RT-DETR-v2 (comic-text-and-bubble-detector) | 检测 | Apache-2.0（HF 模型卡） [待核实] | |
| PaddleOCR 系 | OCR | Apache-2.0 | |
| MangaOCR | 日文 OCR | [待核实]（HF 模型卡） | 若移植需先核 |
| LaMa / litelama | 修复 | [待核实] | |
| Saber 随包模型 | 参考 | 各自上游许可 [待核实] | **不得直接拷贝进仓库** |

## 4. 字体

| 字体 | 许可 | 处置 |
|---|---|---|
| Source Han Sans / Noto Sans（思源） | OFL-1.1 | 可随包 |
| `msyh.ttc` / `msyhbd.ttc` | Microsoft 系统字体 | **不得随包**；只能依赖系统已安装 |
| `STKAITI` / `STZHONGS` / `STSONG` / `STFANGSO`（华文） | 商业字体 | **不得随包** |

## 5. 发行 Gate

- [ ] 每次发行前重跑本表逐项核对（一手 license 文件/模型卡）。
- [ ] 主包若含 AGPL 组件 → `NOTICE` 与发行页明确 AGPL-3.0。
- [ ] 输出 `THIRD_PARTY_LICENSES` 与源码同包/同页提供。
