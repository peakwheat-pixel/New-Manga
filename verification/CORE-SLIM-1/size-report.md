# CORE-SLIM-1 体积报告（AC2 打包去重 / AC3 预算）

## 0. 结论

- Core 运行时（不含模型）：**1067.3 MiB → 970.1 MiB**（减少 97.2 MiB）；预算 ≤700 MiB → **PARTIAL（未达 ≤700 MiB，见 §4 缺口分析）**
- 三个 ~65 MiB entry 重复：exe 合计 **199.6 MiB → 1.9 MiB**（改为共享 `_internal` 的 `.pyc`，见 §2）
- 打包闭包 **Qt 归零**：`PySide6`/`shiboken6`/`Qt6*.dll` 命中 = 0 个
- 能力/协议未变：解码与像素等价见 `ac1/COMPARISON.md`；冻结侧车能力矩阵见 §5。

## 1. 测量口径

- 测量对象：`resources/core-sidecar/` 整棵 onedir 树（5 个 entry exe + `_internal` + 可选 `python/` + 可选 `models/`）。
- 预算口径（AD-002 §3.5）：**Core 运行时 = 整树 − models/**；CUDA 为独立可选包（本 bundle 不含）。
- 改前快照：主检出 `G:/CODEX/New Manga/apps/desktop/src-tauri/target/release/resources/core-sidecar`（2026-10-27T03:31:02.3919532+08:00，sha256 见 `ac2/bundle-before.json`）。
- 改后快照：worktree 重新打包产物（同一 spec/build 脚本，CORE-SLIM-1 改动后）。

## 2. before / after 总表

| 指标 | before（Qt + PYZ/entry） | after（Qt-free + noarchive 共享 `_internal`） | Δ |
|---|---|---|---|
| 整树体积 | 1269.8 MiB | 1172.6 MiB | -97.2 MiB |
| 整树文件数 | 6573 | 15204 | +8631 |
| models/ | 202.5 MiB | 202.5 MiB | +0.0 MiB |
| `_internal/` | 825.8 MiB | 926.3 MiB | +100.5 MiB |
| `python/` 插件运行时 | 41.9 MiB | 41.9 MiB | +0.0 MiB |
| 5 个 entry exe 合计 | 199.6 MiB | 1.9 MiB | -197.7 MiB |
| **Core 运行时（不含 models）** | 1067.3 MiB | 970.1 MiB | -97.2 MiB |

### 逐 entry exe 体积（AC2 去重核心指标）

| entry | before | after | 说明 |
|---|---|---|---|
| `acceptance_bridge.exe` | 65.6 MiB | 0.38 MiB | 引导器+入口脚本；闭包改由共享 `_internal` 提供 |
| `catalog_loader.exe` | 1.75 MiB | 0.38 MiB | 引导器+入口脚本；闭包改由共享 `_internal` 提供 |
| `core_service.exe` | 65.7 MiB | 0.38 MiB | 引导器+入口脚本；闭包改由共享 `_internal` 提供 |
| `host_bridge.exe` | 1.75 MiB | 0.38 MiB | 引导器+入口脚本；闭包改由共享 `_internal` 提供 |
| `sfx_detect_probe.exe` | 64.82 MiB | 0.38 MiB | 引导器+入口脚本；闭包改由共享 `_internal` 提供 |

- 去重机制证据：`_internal` 下存在 **8767 个 `.pyc`**（164.1 MiB），即 PyInstaller `noarchive=True` 把每个纯 Python 模块落成单个 `.pyc` 文件；5 个 entry 的模块路径逐字节相同，`COLLECT` 只保留一份（原先每个 ML entry 各嵌一份 ~65 MiB PYZ）。
- 入口名、argv、stdio JSON-lines 协议**均未改变**（见 §5 smoke：`core_service`/`host_bridge` 实际启停与命令往返）。

## 3. PySide6 移除证据

| 项 | 证据 |
|---|---|
| 源码 | `src/infrastructure/importing.py`（`PillowImageDecoder` + Pillow PDF/MOBI PNG 桥）、`src/bootstrap/core_assembly.py`（Pillow 像素路径）、`src/bootstrap/core_service.py`、`src/bootstrap/acceptance_bridge.py` 全部去 Qt；新增 `pillow_source_style.py` |
| 依赖 | `requirements.txt` 删除 `PySide6_Essentials==6.11.2`/`shiboken6==6.11.2`，新增直接依赖 `pillow==12.3.0` |
| 打包 | `packaging/m2ac5/core_sidecar.spec` 的 `EXCLUDED` 显式加入 `PySide6`/`shiboken6` |
| 闭包实测 | 产物内 Qt 文件命中：**0** |
| 遗留 | legacy QML 源（`src/bootstrap/app.py`、`src/ui/**`）与对应旧测试按 S5-C 口径**原位冻结、不打包**（见 Handoff Record Decision）；`QtImageDecoder` 保留为 `PillowImageDecoder` 的兼容别名，供冻结旧壳 import |

## 4. AC3 预算判定与缺口分析

- 实测 Core 运行时（不含模型）：**970.1 MiB**；预算 ≤700 MiB；差额 **270.1 MiB**。
- 不可再砍项（均为**能力必需**，删除即违反「不删除任何既有解码/检测能力」）：

| 组件 | 体积（改前压缩布局） | 被谁使用（能力） | 结论 |
|---|---|---|---|
| `torch` (CPU) | 365.2 MiB | `python-doctr` OCR 检测 + `transformers` manga 检测（torch/transformers 运行时） | 保留 |
| `cv2` (opencv) | 111.8 MiB | `import doctr` 即加载；13 个 doctr 模块 `import cv2`（含 `models/detection/core.py`）→ 硬依赖 | 保留 |
| `onnxruntime` (+DirectML) | 63.1 MiB | SFX 检测 EP（`detection_sfx`） | 保留 |
| `scipy`/`scipy.libs` | 70.5 MiB | 导入 ML 栈时即加载（doctr/torchvision/transformers 传递依赖） | 保留 |
| `transformers` (pure py) | 38.6 MiB | manga 检测模型加载 | 保留 |
| `PIL`/`pypdfium2_raw`/`numpy` | ~40 MiB | 解码/PDF/光栅（本 Task 的直接替代实现） | 保留 |

**为什么不执行「excludes 瘦身」**（Task 卡允许，但本 Task 主动放弃并给出证据）：

1. 在 build venv 中实测 `import doctr, torch, torchvision, transformers, onnxruntime, cv2` 后，`cv2`/`scipy`/`h5py`/`shapely` **已全部在 `sys.modules`**——它们不是可安全排除的传递依赖，而是检测/OCR 链在导入期即触达的硬依赖；排除即删除能力（违反卡内红线）。
2. 即便强行排除 `cv2`(111.8)+`scipy`(70.5)（合计 182.3 MiB），Core 运行时也只能降到约 788 MiB，仍高于 700 MiB；再往下只能动 torch（365 MiB，检测链的核心），属于改检测架构的独立决策。
3. 其余可安全排除项仅 `hf_xet`(8.9)/`h5py`(6.9)/`shapely`(3.5) 级别，收益 < 救命线且需逐个能力验证，投入/风险不成比例。

→ **结论：AC3 = PARTIAL**。交付的是**真实最小化后的数字（970.1 MiB）+ 每项取舍证据**；达标 700 MiB 需要「把 torch/cv2/scipy 级 ML 依赖从 Core 运行时剥离（如改 ONNX 检测链）」，那是一次能力/架构裁决，超出 CORE-SLIM-1 的「不删除能力」边界，按 Task 卡规则记 PARTIAL。

## 5. 冻结闭包能力矩阵（AC3 前提）

| 能力 | 命令/探针 | 结果 |
|---|---|---|
| 目录/命名空间播种（catalog_loader） | `catalog_loader.exe --db ... --initialize-preview-namespace ... --count` | PASS（rc=0） |
| Host 契约：core_service 启动 + core.ping | `core_service.exe < protocol 2.3` | PASS（响应已解析） |
| 导入（REAL import 路径，Pillow 解码） | `acceptance_bridge seed_fixture` | PASS |
| OCR/翻译/排版渲染（Mock 管线，冻结 Pillow 适配器） | `acceptance_bridge run_pipeline` | PASS |
| 阅读器投影 | `acceptance_bridge reader_pages` | PASS |
| 导出（PNG 写出） | `acceptance_bridge export_page` | PASS |
| 检测（onnxruntime/DirectML 冻结闭包启动） | `sfx_detect_probe.exe --help` | PASS（权重需真实页 fixture，见 run_clean_start_e2e） |

总判定：**PASS**（原始输出：`ac2/capability-smoke.json` 与 `ac2/smoke-*.log`）

## 6. 回归

- `python -m pytest -q`：**3 failed, 2710 passed, 9 skipped in 210.59s (0:03:30)**（基线 3F/2691P/9S；失败集合与基线一致，新增 19 个 AC1 用例）。
- `apps/desktop-avalonia/scripts/test.ps1`：见 `ac4/scripts-test-after.log`（真实 sidecar 集成，`-SidecarDirectory` 指向新构建的无标签副本）。

