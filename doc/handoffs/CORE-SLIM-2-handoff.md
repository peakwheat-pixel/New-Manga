# CORE-SLIM-2 Handoff（检测链 ONNX 化 / torch 裁剪）

- Task: `doc/tasks/CORE-SLIM-2.md`（AD-002 §3.5 预算规则；依赖 `INFER-BASELINE-EP-1`）
- Branch: `task/CORE-SLIM-2`；Worktree: `G:/CODEX/New Manga.workspace/worktrees/CORE-SLIM-2`
- Base: `21960f4cb`（= CORE-SLIM-1 集成 `4b0d5f0eb` + INFER 基线集成 `1b91d93a9` + docs）
- Delivery head: `9ebc2caa4`（实现+证据所在提交；任务卡 Canonical Evidence 的 pin 均指向它）
- 未 push（按卡禁止）。

## 1. 交付摘要

| AC | 结论 | 证据 |
|---|---|---|
| AC1 可行性（方案 + 精度/速度） | **MET** | `verification/CORE-SLIM-2/REPORT.md` §1；`parity.json` |
| AC2 实现（ORT + torch 可选回退） | **MET** | 3 个新 provider 模块；spec/build 脚本改动；`REPORT.md` §2 |
| AC3 体积 ≤700MB | **MET**：**970.1 → 186.3 MiB**（不含模型，余量 513.7） | `verification/CORE-SLIM-2/size-report.md` |
| AC4 回归 | **MET**：pytest `3F/2739P/9S`（失败集合=基线，0 新增）；`test.ps1` 102/102；10/10 页检测一致 | `pytest-after.log`、`scripts-test.log`、`parity.json` |
| AC5 门禁 | **MET** | check.ps1 PASS；64-hex pin；本文件 Record Decision |

冻结闭包能力 smoke：**7/7 PASS**（catalog_loader / core_service core.ping / acceptance_bridge
seed_fixture+run_pipeline+reader_pages+export_page / sfx_detect_probe）；`capability-smoke.json`。

## 2. 关键决策（Record Decision）

1. **检测/OCR 运行时 = ONNX Runtime（DirectML 优先），torch 退为可选回退。**
   依据 INFER-BASELINE-EP-1 的“无必须 torch 的模型”实测：RT-DETR-v2 fixed ONNX 与 manga-ocr
   enc/dec ONNX 均与 torch 逐结果一致。发布闭包不再含 torch/torchvision/transformers/doctr 及其传递
   依赖（spec 负向断言保证不回流）；旧适配器保留在源码，`NEWMANGA_DETECTOR_BACKEND=torch` /
   `NEWMANGA_OCR_BACKEND=torch` 显式选择，需操作者自装 torch 栈。
2. **只发 fixed-shape ONNX（不发明态图）。** 基线确认动态 RT-DETR 图 ORT 不可加载；fixed 图
   163.7 MB，10/10 页结果一致。导出环境（transformers 5.21.0）与产品 pin（5.17.0）不同 →
   **只钉 ONNX 产物 + SHA-256**，不要求产品运行时复现导出。
3. **EP 策略：默认 auto=DirectML，OCR 默认 CPU，EP 静默回退硬断言。**
   基线实测 DML 检测 61.47 ms/页（torch CPU 263.14），而 OCR 在 GPU 上并不更快（DML 97.87 vs
   CUDA 23.17，主包无 CUDA 轮子）→ OCR 留在 CPU；`onnx_sessions.create_session` 校验
   `session.get_providers()`，任何 ORT 静默回退都变成 typed 构建/加载失败（沿用基线 EP_NOT_ACTIVE 规则）。
4. **模型分发：SHA-256 pin 的 in-bundle 拷贝。** `build_sidecar.ps1` 新增
   `Copy-MangaDetectorOnnx` / `Copy-MangaOcrOnnx`，pin 与 provider 常量同源（PowerShell 不能 import src，
   重复为字面量；构建期校验，provider 加载期再校验一次）。模型计入 `models/` 预算（≤2GB 主包口径），
   不计 Core 运行时 700MB。
5. **协议/契约零改动。** 未改 stdio JSON-lines 协议、命令语义、Host 契约、`ports/**`；检测结果仍是
   page-global 绝对像素的匿名 `manga-<n>` 候选，合并策略与 tiling 常量沿用冻结值（导入而非复制）。

## 3. 修改文件

| 文件 | 改动 |
|---|---|
| `src/infrastructure/providers/onnx_sessions.py`（新） | ORT 会话/EP 策略 + 硬断言 + typed 错误 |
| `src/infrastructure/providers/detection_manga_onnx.py`（新） | RT-DETR-v2 fixed-ONNX 检测适配器 |
| `src/infrastructure/providers/ocr_manga_onnx.py`（新） | manga-ocr 编解码 ONNX 适配器（Python 解码循环） |
| `src/infrastructure/providers/runtime.py` | manga-ocr 注册按 `NEWMANGA_OCR_BACKEND`（默认 onnx） |
| `src/bootstrap/core_assembly.py` | 检测后端选择（默认 ONNX，torch/doctr 可选） |
| `packaging/m2ac5/core_sidecar.spec` | EXCLUDED + ONNX hiddenimports + torch-free closure 断言 |
| `packaging/m2ac5/build_sidecar.ps1` | ONNX 模型 SHA-256 校验拷贝（替换 torch 三件套拷贝） |
| `requirements.txt` | torch 栈标注为可选开发/回退依赖 |
| `tests/providers/{test_onnx_sessions,test_detection_manga_onnx,test_ocr_manga_onnx}.py`（新） | 29 个新用例（EP 策略/后处理/解码循环/pin/负向断言） |
| `tests/providers/{test_detection_manga,test_detector_weights_lookup,env_sim,test_registry_readiness}.py`、`tests/core/test_sfx_assembly.py` | 适配“默认 ONNX、torch 可选”的新语义 |

## 4. 体积（口径：整树 − models）

| 项 | before（CORE-SLIM-1） | after（CORE-SLIM-2） |
|---|---|---|
| Core 运行时（不含模型） | 970.1 MiB | **186.3 MiB** |
| `_internal/` | 926.3 MiB | 142.5 MiB |
| `models/` | 202.5 MiB | 642.3 MiB（ONNX 置换） |
| 整包 | 1172.6 MiB | 828.6 MiB |
| 闭包内 torch 栈 | 416.7+111.8+80.8+… | **0** |

详见 `verification/CORE-SLIM-2/size-report.md`（含每项移除的依赖证据）。

## 5. 回归证据

- `python -m pytest -q`：`3 failed, 2739 passed, 9 skipped`（基线 3F/2710P/9S；失败集合相同=2 项
  weights-missing 环境失败 + 1 项基线 flaky；**无新增失败**；新增 29 个 CORE-SLIM-2 用例）。
- `apps/desktop-avalonia/scripts/test.ps1 -SidecarDirectory <新构建无标签副本>`：
  `TEST PASS (Debug): 102/102 passed, 0 skipped`。
- 检测/OCR 等价：`parity.json` —— 10/10 页候选数一致、合并前框数一致、recall 1.0、meanIoU 1.0、
  OCR 逐字符 10/10 一致；速度 torch 263.14 → ONNX-DML 61.47 ms/页。
- 冻结闭包能力 smoke：7/7 PASS（含 ORT/DirectML 引擎在冻结 exe 内可用）。

## 6. 遗留 / 后续

1. **绝对精度**（检测 vs 人工 GT、OCR vs 人工转录）未测：与 INFER 基线同一环境限制（样本与标注页数不匹配），
   建议后续在有对齐 GT 的样本卷上另开评估 slice。
2. **CUDA 可选包**：主包只发 `onnxruntime-directml`；可选高性能包（`onnxruntime-gpu` + CUDA 12.8）沿用基线
   预算估算（≈2.30 GB，≤8GB 可选包预算），未在本 Task 构建/验证。
3. **设备管理器**：`devices/manager.py` 仍以 torch 探测 CUDA；打包闭包无 torch 时会报“无 GPU 运行时”。
   这对 ONNX provider 无影响（它直接按 ORT EP 选择），但 Settings 的 GPU 状态可能显示不可用 →
   建议后续改为 ORT EP 探测（小改动，另开 slice）。
4. **`python/` 插件运行时与 `playwright`**：与 CORE-SLIM-1 相同边界（build venv 未装 playwright，旧包亦然）。
5. 主检出的 `target/release/resources/core-sidecar` 仍是旧包；集成时以本 Task 的构建命令重建
   （`build_sidecar.ps1 -Force`，模型源默认指向 `task-envs/CORE-SLIM-2/models`）。
6. 任务卡 `allowed_paths` 未含 `doc/handoffs/**`；本 Handoff 按 AC5 落位，建议 DSH 补该路径。
7. 需独立 Review（Owner 不得自审）。
