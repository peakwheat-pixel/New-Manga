# WEIGHTS-LICENSE-PROVENANCE-1 · 三项权重的许可来源核查（2026-11-17）

# head: 3f99d0750（开工 HEAD）
# interpreter: python 3（字节扫描）+ web_search（外部来源）
# 结论边界：本文件只记录**上游自己怎么声明**与**本地能不能自证**，**不做法律认定**（ZCode 2026-11-17 裁定：上游许可的法律属性证据不足）

## 1. 本地自证：不可行

`verification/WEIGHTS-LICENSE-PROVENANCE-1/ac1-onnx-metadata-probe.log`（原始字节扫描）：

| 权重 | 字节 | 可读许可元数据 |
|---|---|---|
| `detector/rtdetr-v2-fixed.onnx` | 171,618,071 | **无**（7 处关键词命中全是二进制噪声，如 `];MIT<`、`C8<MIT<`，无上下文） |
| `ocr/manga-ocr-onnx/encoder_model.onnx` | 343,454,249 | **无**（10 处命中全为噪声） |
| `ocr/manga-ocr-onnx/decoder_model.onnx` | 117,480,262 | **无**（4 处命中全为噪声） |

对比参照：`yolo11s-seg.onnx` 当年是**文件自身元数据**就写明 `Ultralytics YOLO11s-seg` 与 `AGPL-3.0 License`，可直接引用；
这三个 ONNX **没有**这类可读元数据 ⇒ **本地无法自证**，`THIRD_PARTY_LICENSES.md` 的「待核实」是**事实正确**的。

## 2. 上游声明（外部来源，仅记录，不做认定）

### manga-ocr（encoder + decoder）

| 来源 | 声明 |
|---|---|
| HuggingFace 模型卡 `kha-white/manga-ocr-base` 的 README 头部（镜像可读：<https://repo.model.xfyun.cn/kha-white/manga-ocr-base/raw/commit/1d0bb748d3b7551b2c556f406157459949ad32bc/README.md>） | `license: apache-2.0` |
| nixpkgs `pkgs/development/python-modules/manga-ocr/default.nix`（<https://github.com/NixOS/nixpkgs/blob/release-25.05/pkgs/development/python-modules/manga-ocr/default.nix>） | `license = licenses.asl20;`（Apache-2.0 的 nixpkgs 标识） |
| 上游代码仓库 | <https://github.com/kha-white/manga_ocr> |

### RT-DETR（detector）

| 来源 | 声明 |
|---|---|
| 百度 AI Studio 模型页 `RT-DETR_HGNetV2_l`（<https://aistudio.baidu.com/modelsdetail/273?modelId=273>） | `license: Apache License 2.0` |
| HuggingFace `PekingU/rtdetr_r50vd` 模型卡（<https://huggingface.co/PekingU/rtdetr_r50vd>） | `License: Apache-2.0` |
| Roboflow RT-DETR 页（<https://playground.roboflow.com/models/baidu/rt-detr>） | `Apache 2.0` |
| Kornia 文档 RT-DETR（<https://kornia.readthedocs.io/en/v0.7.2/models/rt_detr.html>） | `Licence: Apache 2.0` |

## 3. 这对本仓库意味着什么

- 三项权重的**上游均声明 Apache-2.0**（宽松许可），因此**理论上**把它们打进包里**不强制**整包 AGPL。
- 但本仓库**不做法律认定**（ZCode 裁定的边界），且当前已发布的合规包**保守按 AGPL-3.0 声明** —— 过度声明对版权人安全，不构成违规。
- 是否收紧为 `GPL-3.0-or-later`（或不含 AGPL 的声明），属于**发布声明变更**，需书面裁定 + 重新打包 + 重新取证，**不在本轮执行**。
  已派发 ZCode 就此出裁定。

## 4. 未做的事（如实）

- 未核对本地 `vocab.*` / `config.json` 等 6 个非权重文件的来源许可（它们随上游 tokenizer 分发，`THIRD_PARTY_LICENSES.md` 记为「随上游 MangaOCR」）。
- 未做上游代码 LICENSE 文件的逐字比对（只记录模型卡/打包清单的声明）。
