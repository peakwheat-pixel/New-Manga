# 许可证一致性审计（AGPL-RELEASE-1 / 包内随包副本）

本文件随包分发，说明 **base** 与 **models** 两个发行变体的整体许可结论。包内许可文件与仓库根逐字节一致（SHA-256 相等，见 `package-summary.json` / `package-manifest.json`）。

## 1. 变体结论

| 发行变体 | 包名 | 是否含模型权重 | 整体分发许可 | 依据 |
|---|---|---|---|---|
| **base** | `NewManga-<ver>-win-x64` | **否**（sidecar 复制时排除 `models/`） | **GPL-3.0-or-later**（包内 `LICENSE`） | 不含 AGPL 组件；包内 `LICENSE-AGPL-3.0.txt` 仅说明可选 models 组件的许可 |
| **models** | `NewManga-<ver>-win-x64-models` | **是**（`app/core-sidecar/models/`，642.3 MiB） | **AGPL-3.0**（包内 `LICENSE-AGPL-3.0.txt` 为 GNU AGPL-3.0 官方全文） | 随包分发 **Ultralytics YOLO11s-seg**（`detector/yolo11s-seg.onnx`，AGPL-3.0）；AGPL 要求许可证副本随分发提供 |

## 2. 随包文件（base 与 models 均含，4 项）

`LICENSE`、`LICENSE-AGPL-3.0.txt`、`NOTICE.md`、`THIRD_PARTY_LICENSES.md` —— 均由 `package.ps1` 从仓库根复制并做 SHA-256 逐字节校验（不一致即打包失败）。

## 3. 模型权重结论

- `models` 变体随包权重（实测字节/sha256）：
  - `detector/yolo11s-seg.onnx` 40,824,255 B sha256 `944e8114…18d` —— **AGPL-3.0（Ultralytics）**（文件自身元数据含 `Ultralytics YOLO11s-seg` 与 `AGPL-3.0 License`；Ultralytics 官方许可页与仓库 LICENSE 交叉核实）。
  - `detector/rtdetr-v2-fixed.onnx`、`ocr/manga-ocr-onnx/{encoder,decoder}_model.onnx` 等 —— 上游声明 [待核实]，不作为本包许可结论的阻断项（明细见 `THIRD_PARTY_LICENSES.md` §3）。
- `base` 变体**不随包任何模型权重**；此前「模型权重不随包」的笼统表述仅对 base 成立，对 models 变体与事实不符，已按变体分别修正（本文件即修正后版本）。
