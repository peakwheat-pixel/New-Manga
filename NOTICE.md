# NOTICE — New Manga

本产品（Windows 桌面端：Avalonia Host + Python Core + Managed Copy）提供两个发行变体；两个变体的整体分发许可**相同**（均为 GPL-3.0-or-later），差别只在是否随包携带模型权重：

| 发行变体 | 内容 | 整体分发许可 |
|---|---|---|
| **base**（`NewManga-<ver>-win-x64`） | 应用 + Core sidecar，**不含模型权重** | **GPL-3.0-or-later**（全文见 [LICENSE](LICENSE)） |
| **models**（`NewManga-<ver>-win-x64-models`） | 应用 + Core sidecar + `app/core-sidecar/models/` 模型权重 | **GPL-3.0-or-later**（全文见 [LICENSE](LICENSE)）；随包权重的上游声明为 Apache-2.0，全文见 [LICENSE-Apache-2.0.txt](LICENSE-Apache-2.0.txt) |

**models 变体的许可结论（2026-11-17 收紧为 GPL-3.0-or-later）**：该变体随包分发以下 **3 个 ONNX 权重**，合计 **632,552,582 B**
（`app/core-sidecar/models/` 下另有 6 个 config/vocab 文件共 109,678 B，不入此合计）：

| 文件 | 字节 | sha256（前 16 位） | 上游声明 |
|---|---|---|---|
| `models/detector/rtdetr-v2-fixed.onnx` | 171,618,071 | `c7fb5af1a8982416` | Apache-2.0（RT-DETR） |
| `models/ocr/manga-ocr-onnx/encoder_model.onnx` | 343,454,249 | `15fa8155fe9bc1a7` | Apache-2.0（MangaOCR） |
| `models/ocr/manga-ocr-onnx/decoder_model.onnx` | 117,480,262 | `ef7765261e9d1cdc` | Apache-2.0（MangaOCR） |

**这三项的上游均声明 Apache-2.0**（一手来源与抓取日期登记在 `THIRD_PARTY_LICENSES.md` §3 与
`verification/WEIGHTS-LICENSE-PROVENANCE-1/`；**本仓库不做法律认定**）。Apache-2.0 与 GPL-3.0 兼容，
因此 models 变体与 base 变体一样按 **GPL-3.0-or-later** 分发，并随包提供 Apache-2.0 全文副本。

> 历史沿革：2026-11-17 早些时候，models 变体曾按 **AGPL-3.0** 声明 —— 当时整包 AGPL 的唯一事实源是
> **Ultralytics YOLO11s-seg**（其 ONNX 文件自身元数据写明 AGPL-3.0）。该权重**已不在 sidecar 内**；
> 经 ZCode 书面裁定（`doc/reviews/ZCODE-RULING-INSTALLER-LICENSE-2026-11-17.md` 与 `WEIGHTS-LICENSE-PROVENANCE-1` 的收紧裁定）
> 按同等级证据收紧为 GPL-3.0-or-later。**若将来重新打入任何 AGPL 权重，必须同时把本表与 `package.ps1` 的判定改回 AGPL。**

> 说明（2026-11-17）：本文件此前把 models 变体的权重写成 **Ultralytics YOLO11s-seg**（`models/detector/yolo11s-seg.onnx`）。实测 0.1.1 的 sidecar **不含该文件**（其 `VERSION.json` 的 `sidecar_build.known_limitation` 亦写明 sfx 权重缺失、`sfx_detect_probe` fail-closed），实际随包的是上表三个文件。该错误描述已更正；若将来重新打入 yolo11s-seg，需同时更新本表与 `LICENSE_AUDIT.md`。

base 与 models 变体均按 **GPL-3.0-or-later** 声明；随包同时携带 `LICENSE-AGPL-3.0.txt`（历史沿革与未来可能的 AGPL 组件）与 `LICENSE-Apache-2.0.txt`（随包权重的上游许可）。

## 第三方来源登记

| 组件 | 来源 | 许可证 | 使用方式 | 登记状态 |
|---|---|---|---|---|
| Saber-Translator | https://github.com/MashiroSaber03/Saber-Translator | GPL-3.0 | **参考**（架构/流程/交互）；当前仓库**未包含其代码** | 待移植时逐文件登记 |
| rtdetr-v2-fixed / manga-ocr encoder+decoder 权重 | 见 `THIRD_PARTY_LICENSES.md` §3 | **待核实**（保守按 AGPL-3.0 声明整包） | `models` 变体随包分发（3 个 ONNX，632,552,582 B） | 待一手核实 |
| Ultralytics YOLO11s-seg 权重 | https://github.com/ultralytics/ultralytics | **AGPL-3.0** | **当前 sidecar 不含该文件**（sfx 权重缺失，`sfx_detect_probe` fail-closed）；如将来打入则整包 AGPL-3.0 | 已核实（历史登记保留） |
| （移植登记区） | — | — | 每移植一个文件在此记：源路径 + commit + 许可头保留 | 空 |

## 移植规则（强制）

1. 每个从 Saber-Translator 移植的文件必须在文件头保留原版权声明与 GPL-3.0 许可头，并在上表登记「源路径 + 上游 commit + 本仓库路径」。
2. 不得移植后附加额外限制、不得改许可、不得删除版权声明。
3. 模型权重按其自身许可证处理，不视为本仓库代码；随包分发前必须逐个核实（见 `THIRD_PARTY_LICENSES.md` §3）。**当前 models 变体随包的 3 个 ONNX 权重上游许可均未一手核实，故按保守策略整包声明 AGPL-3.0。**
4. 字体只允许随包分发 OFL/Apache 等兼容许可字体；商业/系统字体（如 `msyh`、`STKAITI`、`STZHONGS`）不得随包。

## 当前状态

- 仓库当前**没有**任何 Saber-Translator 代码；仅有参考规格与截图（`verification/DISPLAY-PERF-DECISION-1/ui-spec/`）。
- `models` 变体包含模型权重（见上表）；`base` 变体不包含。
- 本文件与 `LICENSE`、`LICENSE-AGPL-3.0.txt`、`THIRD_PARTY_LICENSES.md` 构成发行前的许可文件组；每次发行重打 base/models 两包，包内这 4 个文件必须与仓库根逐字节一致（`apps/desktop-avalonia/scripts/package.ps1` 校验）。
