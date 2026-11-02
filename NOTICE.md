# NOTICE — New Manga

本产品（Windows 桌面端：Avalonia Host + Python Core + Managed Copy）提供两个发行变体，两个变体的整体分发许可**不同**：

| 发行变体 | 内容 | 整体分发许可 |
|---|---|---|
| **base**（`NewManga-<ver>-win-x64`） | 应用 + Core sidecar，**不含模型权重** | **GPL-3.0-or-later**（全文见 [LICENSE](LICENSE)） |
| **models**（`NewManga-<ver>-win-x64-models`） | 应用 + Core sidecar + `app/core-sidecar/models/` 模型权重 | **AGPL-3.0**（GNU Affero General Public License v3.0，全文见 [LICENSE-AGPL-3.0.txt](LICENSE-AGPL-3.0.txt)） |

**models 变体整体按 AGPL-3.0 分发的原因**：该变体随包分发 **Ultralytics YOLO11s-seg** 模型权重（`app/core-sidecar/models/detector/yolo11s-seg.onnx`，40,824,255 B，sha256 `944e811410933ad6ff8d32446fcc9eef90fb463794e1874ce83035e83acd418d`）。Ultralytics YOLO 模型/代码按 **AGPL-3.0** 许可；该 ONNX 文件自身的元数据即写明 `Ultralytics YOLO11s-seg` 与 `AGPL-3.0 License (https://ultralytics.com/license)`。因此 models 发行包必须整体满足 AGPL-3.0，并随包提供 AGPL-3.0 全文；对应源码（本仓库）与构建脚本同在发行页/仓库提供。

base 变体不含任何模型权重；随包携带 `LICENSE-AGPL-3.0.txt` 仅用于说明可选 models 组件（及 YOLO11s-seg 权重）的许可，**不改变 base 变体自身的 GPL-3.0-or-later 声明**。

## 第三方来源登记

| 组件 | 来源 | 许可证 | 使用方式 | 登记状态 |
|---|---|---|---|---|
| Saber-Translator | https://github.com/MashiroSaber03/Saber-Translator | GPL-3.0 | **参考**（架构/流程/交互）；当前仓库**未包含其代码** | 待移植时逐文件登记 |
| Ultralytics YOLO11s-seg 权重 | https://github.com/ultralytics/ultralytics （模型由 Ultralytics 导出/训练） | **AGPL-3.0** | `models` 变体随包分发（`models/detector/yolo11s-seg.onnx`） | 已核实（一手来源与文件元数据见 `THIRD_PARTY_LICENSES.md` §3 与 `verification/AGPL-RELEASE-1/weights-licenses.json`） |
| （移植登记区） | — | — | 每移植一个文件在此记：源路径 + commit + 许可头保留 | 空 |

## 移植规则（强制）

1. 每个从 Saber-Translator 移植的文件必须在文件头保留原版权声明与 GPL-3.0 许可头，并在上表登记「源路径 + 上游 commit + 本仓库路径」。
2. 不得移植后附加额外限制、不得改许可、不得删除版权声明。
3. 模型权重按其自身许可证处理，不视为本仓库代码；随包分发前必须逐个核实（见 `THIRD_PARTY_LICENSES.md` §3）。**当前 models 变体随包的 YOLO11s-seg 已核实为 AGPL-3.0，故 models 变体整体按 AGPL-3.0 分发。**
4. 字体只允许随包分发 OFL/Apache 等兼容许可字体；商业/系统字体（如 `msyh`、`STKAITI`、`STZHONGS`）不得随包。

## 当前状态

- 仓库当前**没有**任何 Saber-Translator 代码；仅有参考规格与截图（`verification/DISPLAY-PERF-DECISION-1/ui-spec/`）。
- `models` 变体包含模型权重（见上表）；`base` 变体不包含。
- 本文件与 `LICENSE`、`LICENSE-AGPL-3.0.txt`、`THIRD_PARTY_LICENSES.md` 构成发行前的许可文件组；每次发行重打 base/models 两包，包内这 4 个文件必须与仓库根逐字节一致（`apps/desktop-avalonia/scripts/package.ps1` 校验）。
