# 许可证一致性审计（AGPL-RELEASE-1 / 包内随包副本）

本文件随包分发，说明 **base** 与 **models** 两个发行变体的整体许可结论。包内许可文件与仓库根逐字节一致（SHA-256 相等，见 `package-summary.json` / `package-manifest.json`）。

## 1. 变体结论

| 发行变体 | 包名 | 是否含模型权重 | 整体分发许可 | 依据 |
|---|---|---|---|---|
| **base** | `NewManga-<ver>-win-x64` | **否**（sidecar 复制时排除 `models/`） | **GPL-3.0-or-later**（包内 `LICENSE`） | 不含 AGPL 组件；包内 `LICENSE-AGPL-3.0.txt` 仅说明可选 models 组件的许可 |
| **models** | `NewManga-<ver>-win-x64-models` | **是**（`app/core-sidecar/models/`，632,662,260 B = 3 个 ONNX 632,552,582 B + 6 个 config/vocab 109,678 B） | **AGPL-3.0**（包内 `LICENSE-AGPL-3.0.txt` 为 GNU AGPL-3.0 官方全文） | 随包 3 个 ONNX 权重的上游许可**尚未一手核实**（`THIRD_PARTY_LICENSES.md` §3「待核实」）；按保守策略整包声明 AGPL-3.0（见 §3） |

## 2. 随包文件（base 与 models 均含，4 项）

`LICENSE`、`LICENSE-AGPL-3.0.txt`、`NOTICE.md`、`THIRD_PARTY_LICENSES.md` —— 均由 `package.ps1` 从仓库根复制并做 SHA-256 逐字节校验（不一致即打包失败）。

## 3. 模型权重结论

- `models` 变体随包权重（2026-11-17 实测，`NewManga-0.1.1-win-x64-models` 干净重建产物）：

| 文件 | 字节 | sha256（前 16 位） | 上游许可 |
|---|---|---|---|
| `detector/rtdetr-v2-fixed.onnx` | 171,618,071 | `c7fb5af1a8982416` | **待核实** |
| `ocr/manga-ocr-onnx/encoder_model.onnx` | 343,454,249 | `15fa8155fe9bc1a7` | **待核实** |
| `ocr/manga-ocr-onnx/decoder_model.onnx` | 117,480,262 | `ef7765261e9d1cdc` | **待核实** |

  合计 **632,552,582 B**；`models/` 目录另有 6 个 config/vocab 文件 **109,678 B**（`package.ps1` 分别记为 `models_bundled_bytes` 与 `models_dir_bytes`）。
  **结论**：三项上游许可均未一手核实 ⇒ 整包**保守声明 AGPL-3.0**（宁可过度声明，不可漏声明）。核实完成后若确认全部为宽松许可，可另行收紧；
  在此之前 `GPL-3.0-or-later` 声明**不成立**。
- `base` 变体**不随包任何模型权重**（`package.ps1` 复制 sidecar 时排除 `models/`），维持 `GPL-3.0-or-later`。
- **2026-11-17 更正**：本文件此前把 models 变体的权重写成 `detector/yolo11s-seg.onnx`（40,824,255 B，AGPL-3.0，已核实）。
  实测 0.1.1 的 sidecar **不含该文件**（其 `VERSION.json` 的 `sidecar_build.known_limitation` 写明 sfx 权重缺失、`sfx_detect_probe` fail-closed），
  且当时 `NewManga-0.1.1-win-x64` 这个**名为 base 的包实际装了 632,552,582 B 权重却声明 GPL-3.0-or-later** —— 见
  `doc/reviews/ZCODE-RULING-INSTALLER-LICENSE-2026-11-17.md`（ZCode 裁定：该声明非法，Q2 = P0 发布阻塞）。
  本文件即按该裁定修正后的版本。
