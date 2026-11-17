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
| `detector/yolo11s-seg.onnx` | 40,824,255 | `944e811410933ad6ff8d32446fcc9eef90fb463794e1874ce83035e83acd418d` | SFX 检测 | AGPL-3.0（Ultralytics）**已核实** —— **当前 sidecar 不含该文件**（sfx 权重缺失） |
| `detector/rtdetr-v2-fixed.onnx` | 171,618,071 | `c7fb5af1a8982416b56955e621c1b10397730807956998066e2fbc132c77bbc3` | 文本/气泡检测 | **上游声明 Apache-2.0**（百度 AI Studio 模型页 + HuggingFace `PekingU/rtdetr_r50vd` 模型卡 + Roboflow；来源与抓取日期见 `verification/WEIGHTS-LICENSE-PROVENANCE-1/`；**本仓库未做法律认定**） |
| `ocr/manga-ocr-onnx/encoder_model.onnx` | 343,454,249 | `15fa8155fe9bc1a7d25d9bb353debaa4def033d0174e907dbd2dd6d995def85f` | 日文 OCR | **上游声明 Apache-2.0**（HF 模型卡 `kha-white/manga-ocr-base` + nixpkgs `asl20`；来源见 `verification/WEIGHTS-LICENSE-PROVENANCE-1/`；**本仓库未做法律认定**） |
| `ocr/manga-ocr-onnx/decoder_model.onnx` | 117,480,262 | `ef7765261e9d1cdc34d89356986c2bbc2a082897f753a89605ae80fdfa61f5e8` | 日文 OCR | **上游声明 Apache-2.0**（同上来源；**本仓库未做法律认定**） |
| `ocr/manga-ocr-onnx/{config,generation_config,preprocessor_config,special_tokens_map,tokenizer_config,vocab.*}` | 2–77 KB 级 | 见 `weights-licenses.json` | OCR 配置/词表（非权重） | 随上游 MangaOCR，**上游声明 Apache-2.0**（本仓库未做法律认定） |

**整包许可结论（2026-11-17，按 ZCode 收紧裁定）**：上表 3 个 ONNX 权重（`rtdetr-v2-fixed` 与 `manga-ocr` encoder/decoder）
的上游**均声明 Apache-2.0**（来源见本表与 `verification/WEIGHTS-LICENSE-PROVENANCE-1/`，**本仓库未做法律认定**）。
Apache-2.0 与 GPL-3.0 兼容，且当前 sidecar **不含任何 AGPL 权重** ⇒ **models 与 base 两个变体都按 `GPL-3.0-or-later` 分发**，
并随包提供 Apache-2.0 全文（`LICENSE-Apache-2.0.txt`）。
依据：`doc/reviews/ZCODE-RULING-INSTALLER-LICENSE-2026-11-17.md` 的「声明变更裁定（TIGHTEN_TO_GPL）」。
**防回归**：若将来重新打入任何 AGPL 权重（例如 `yolo11s-seg.onnx`），必须同时把本段、`NOTICE.md` 变体表与 `package.ps1` 的判定改回 AGPL。

**YOLO11s-seg 的 AGPL-3.0 一手依据（历史登记；该文件当前不在 sidecar 内）**：
1. 该 ONNX 文件自身元数据包含 `Ultralytics YOLO11s-seg model trained on …` 与 `AGPL-3.0 License (https://ultralytics.com/license)`（扫描记录见 `verification/AGPL-RELEASE-1/weights-licenses.json`）。
2. Ultralytics 官方许可页（https://www.ultralytics.com/license，抓取日期记录于证据 JSON）明确 YOLO 模型按 **AGPL-3.0** 提供。
3. Ultralytics 仓库 `LICENSE`（https://raw.githubusercontent.com/ultralytics/ultralytics/main/LICENSE）与 GNU 官方 AGPL-3.0 全文逐字节一致（sha256 `0d96a4ff…`）。

**发行后果（强制）**：
- **models** 变体当前随包的 3 个权重**上游均声明 Apache-2.0** → 与 base 一样按 **GPL-3.0-or-later** 分发；随包附 `LICENSE` 与 `LICENSE-Apache-2.0.txt` 全文。（历史：若将来打入任何 AGPL 权重，本节与 `NOTICE.md`、`package.ps1` 必须同时改回 AGPL。）
- **base** 变体不含任何模型权重 → 仍按 **GPL-3.0-or-later** 分发；其随包的 `LICENSE-AGPL-3.0.txt` 仅作为可选组件许可说明。

RT-DETR / MangaOCR 的权重与配置：**上游均声明 Apache-2.0**（来源见 §3 与 `verification/WEIGHTS-LICENSE-PROVENANCE-1/`；本仓库未做法律认定）。**本地 ONNX 内不含可读许可元数据**（实测），因此该结论只以上游声明为依据。

## 4. 字体

| 字体 | 许可 | 处置 |
|---|---|---|
| Source Han Sans / Noto Sans（思源） | OFL-1.1 | 可随包 |
| `msyh.ttc` / `msyhbd.ttc` | Microsoft 系统字体 | **不得随包**；只能依赖系统已安装 |
| `STKAITI` / `STZHONGS` / `STSONG` / `STFANGSO`（华文） | 商业字体 | **不得随包** |

## 5. 发行 Gate

- [ ] 每次发行前重跑本表逐项核对（一手 license 文件/模型卡）。
- [x] models 变体随包权重（rtdetr-v2-fixed + manga-ocr encoder/decoder）的上游**均声明 Apache-2.0** ⇒ 两变体均按 **GPL-3.0-or-later** 分发，随包附 `LICENSE`、`LICENSE-Apache-2.0.txt`（以及历史沿革用的 `LICENSE-AGPL-3.0.txt`）全文。
- [x] （历史）曾经的 `Ultralytics YOLO11s-seg` 权重已不在当前 sidecar 内；其 AGPL-3.0 依据仍保留在上文，供将来重新打入时引用。
- [ ] base 变体不含权重 → 保持 GPL-3.0-or-later 声明；包内 4 个许可文件与仓库根逐字节一致（`package.ps1` 校验）。
- [ ] 输出 `THIRD_PARTY_LICENSES` 与源码同包/同页提供。
