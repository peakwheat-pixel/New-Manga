# CORE-SLIM-2 体积报告（AC2 实现 / AC3 预算）

## 0. 结论（先行）

- **AC3 达标**：Core 运行时（整树 − `models/`）= **186.3 MiB**，目标 ≤700 MiB，余量 **513.7 MiB**。
  - before（CORE-SLIM-1 发布态）：**970.1 MiB** → after：**186.3 MiB（−783.8 MiB，−80.8%）**。
- **torch 栈移除**：`torch / torchvision / transformers / doctr` 及其传递依赖（`cv2 / scipy / h5py /
  shapely / tokenizers / huggingface_hub / safetensors / networkx / mpmath`）在闭包内 **0 命中**
  （`bundle-after.json.torchArtifacts == []`，spec 的 `torch-free closure assertion` 在构建期强断言）。
- **能力不减**：检测/OCR 改由 ONNX Runtime 承载，torch 适配器保留为**可选回退**（不随包）；
  10/10 页检测候选数与 torch 完全一致（recall 1.0 / meanIoU 1.0），OCR 逐字符 10/10 一致。
- **模型预算**：`models/` 642.3 MiB（RT-DETR-v2 ONNX 163.7 + SFX YOLO 38.9 + manga-ocr ONNX 439.6），
  整包 828.6 MiB；主安装包（sidecar 828.6 MiB + Avalonia Host/资源，估算 <1.2 GiB）落在 ≤2 GiB 预算内。

## 1. 测量口径

- 对象：`apps/desktop/src-tauri/target/core-sidecar/core-sidecar/` 整棵 onedir 树
  （5 个 entry exe + `_internal/` + `python/` + `models/`）。
- 预算口径（AD-002 §3.5）：**Core 运行时 = 整树 − models/**；CUDA 为独立可选包（本 bundle 不含）。
- before 快照：CORE-SLIM-1 交付的同一 bundle 度量（`verification/CORE-SLIM-1/ac2/bundle-after.json`，
  复制为 `verification/CORE-SLIM-2/bundle-before.json`，64-hex pin 见 §6）。
- after 快照：本 Task 用同一 spec/build 脚本重建（`verification/CORE-SLIM-2/bundle-after.json`）。

## 2. before / after 总表

| 指标 | before（CORE-SLIM-1：Qt-free，torch 栈在包内） | after（CORE-SLIM-2：torch-free，ONNX 检测/OCR） | Δ |
|---|---|---|---|
| 整树 | 1172.6 MiB | **828.6 MiB** | −344.0 MiB |
| `models/` | 202.5 MiB | 642.3 MiB | +439.8 MiB（新增 manga-ocr ONNX 439.6 + RT-DETR ONNX 163.7 − torch safetensors 202.5 + 口径差） |
| **Core 运行时（不含 models）** | **970.1 MiB** | **186.3 MiB** | **−783.8 MiB** |
| `_internal/` | 926.3 MiB | 142.5 MiB | −783.8 MiB |
| `python/` 插件运行时 | 41.9 MiB | 41.9 MiB | 0 |
| 5 个 entry exe 合计 | 1.9 MiB | 1.95 MiB | ≈0 |
| 文件数 | 15,204 | 1,964 | −13,240 |
| 闭包内 Qt | 0 | 0 | 0 |
| 闭包内 torch 栈 | torch 416.7 / cv2 111.8 / transformers 80.8 / scipy 63.5+19.3 … | **0** | 全部移除 |

> 注：`models/` 的 +439.8 MiB 是**模型预算**内部置换（torch safetensors 快照 202.5 MiB 换成 163.7 MiB ONNX
> + 新增 manga-ocr encoder/decoder ONNX 439.6 MiB）；预算口径把模型排除在 700 MiB 之外，故不影响 AC3。
> sfx 的 yolo11s-seg.onnx 38.9 MiB 两侧相同。

## 3. 依赖移除清单（每项的证据）

| 移除项 | 体积 | 为何可移除（证据） |
|---|---|---|
| `torch` / `torchvision` | 416.7 / ≈4 MiB | INFER-BASELINE-EP-1：**没有"必须 torch"的模型**；RT-DETR-v2 已导出 fixed ONNX（opset17，三档 EP 可加载），manga-ocr encoder/decoder ONNX 逐字符 10/10 一致。本 Task 复测（`parity.json`）：候选数 10/10 相同、recall 1.0、meanIoU 1.0。 |
| `transformers` | 80.8 MiB | 仅用于 RT-DETR/manga-ocr 推理（导出与旧回退路径）；默认路径改 ORT 后不再被 import（spec 负向断言保证）。 |
| `doctr`（python-doctr） | 小 | T1.1.1 的替代检测器，早已不是默认后端（`NEWMANGA_DETECTOR_BACKEND=doctr` 可选）；主包用 ORT 检测，保留为可选回退。 |
| `cv2`（opencv） | 111.8 MiB | doctr 的硬依赖（13 处 import）；doctr 移出闭包后不可达。 |
| `scipy` / `scipy.libs` | 63.5 + 19.3 MiB | torch/transformers 的传递依赖（`import doctr,torch,torchvision,transformers` 即入 sys.modules，CORE-SLIM-1 已实测）；trio 移出后不可达。 |
| `h5py` / `shapely` | 6.9 / ≈3.5 MiB | transformers 可选依赖（同上实测）。 |
| `tokenizers` / `huggingface_hub` / `hf_xet` / `safetensors` | 7.5 / 8.9 / … | transformers/torch 的模型加载链；ORT 不需要。 |
| `networkx` / `mpmath` | 15.4 / 小 | torch 的传递依赖（`sympy` 保留——onnxruntime 运行时依赖）。 |

保留项：`onnxruntime`（63.2 MiB，含 `DirectML.dll`）、`numpy`（9.8+20.2 libs）、`PIL` 14.0、`pypdfium2_raw` 7.1、
`python312.dll` 6.6、`libcrypto/libssl` 5.8、`python/` 插件运行时 41.9 —— 均为现有能力的运行时面。

## 4. 去重/打包机制（沿用 CORE-SLIM-1 并复核）

- `noarchive=True`：纯 Python 模块落共享 `_internal/*.pyc`（本次 859 个），5 个 entry 复用一份；
  exe 每个仅 ~0.39 MiB（引导器+入口脚本）。entry 名/argv/stdio 协议未变（能力 smoke 7/7 PASS）。
- 模型随包方式：`packaging/m2ac5/build_sidecar.ps1` 在 PyInstaller 构建后按 **SHA-256 pin**
  拷贝 `models/detector/rtdetr-v2-fixed.onnx` 与 `models/ocr/manga-ocr-onnx/`（pin 与
  `src/infrastructure/providers/{detection_manga_onnx,ocr_manga_onnx}.py` 同源，构建期强校验）。

## 5. AC3 判定

**AC3 = MET**：Core 运行时 186.3 MiB ≤ 700 MiB，余量 513.7 MiB。无未达项、无需 PARTIAL。

## 6. 可复跑

```powershell
# 1) 重建 bundle（build venv 里 torch 仍在也不影响——spec 显式 exclude + 负向断言）
pwsh -NoProfile -File packaging/m2ac5/build_sidecar.ps1 -Force
# 2) 体积度量（after）
python verification/CORE-SLIM-2/tools/measure_bundle.py `
  --bundle apps/desktop/src-tauri/target/core-sidecar/core-sidecar `
  --label after --out verification/CORE-SLIM-2/bundle-after.json
# 3) 检测/OCR 等价（需要 torch 参考侧：build venv）
& 'G:/CODEX/New Manga.task-envs/m2ac5-build/Scripts/python.exe' verification/CORE-SLIM-2/tools/parity.py
# 4) 冻结闭包能力 smoke（无标签副本，规避 AC11 Low-IL）
$env:CORE_SLIM_BUNDLE="G:/CODEX/New Manga.workspace/task-envs/CORE-SLIM-2/sidecar-copy"
python verification/CORE-SLIM-2/tools/capability_smoke.py
```

关键 JSON：`bundle-before.json`、`bundle-after.json`、`parity.json`、`capability-smoke.json`、
`build.log`、`pytest-after.log`、`scripts-test.log`。
