# GPU-ORT-PROBE-1 Handoff（GPU 状态改 ORT EP 探测）

- Task: `doc/tasks/GPU-ORT-PROBE-1.md`（team task-27）
- Branch: `task/GPU-ORT-PROBE-1`；Worktree: `G:/CODEX/New Manga.workspace/worktrees/GPU-ORT-PROBE-1`
- Base: `171529b5d`（卡面）；实际分支基于释放提交 `04b657131`（含任务卡与治理 PASS 状态）
- Delivery head: `064e4fe22`（实现+证据提交；任务卡 Canonical Evidence 的 pin 均指向它）
- 未 push；未改推理默认 EP/模型清单/协议/Host 契约/旧壳。

## 1. 交付摘要

| AC | 结论 | 证据 |
|---|---|---|
| AC1 探测替换 | **MET** | `infrastructure/devices/manager.py`：`onnxruntime.get_available_providers()` 为唯一可用性判据（DML/CUDA/ROCm/MIGraphX/TensorRT→CPU）；注册表补名称/显存；torch 仅名称补充 |
| AC2 打包验证 | **MET** | 发布件（torch-free 闭包）设置页显示「GPU：NVIDIA GeForce RTX 5070 Ti · DirectML 可用」；截图 + `device-probe-buildenv.json` + `settings-page-evidence.json` |
| AC3 单测 | **MET** | EP 矩阵 7 项新增（DML only / CUDA+DML / CPU only / 空 / torch-only / snapshot）；device 测试 28 passed |
| AC4 回归 | **MET** | pytest **3F/2746P/9S**（基线 2739P + 新增 7；失败集合同基线，0 新增）；test.ps1 见 §3；sidecar 闭包断言 torch-free |
| AC5 门禁 | **MET** | check.ps1 PASS；64-hex pin；本 Handoff |

## 2. 代码改动

| 文件 | 改动 |
|---|---|
| `src/infrastructure/devices/manager.py` | `_probe_gpu` 改 ORT EP；新增 `_onnxruntime_providers`/`_windows_gpu_name`/`_torch_supplement`/`probe_snapshot`；模块 docstring 更新 |
| `tests/providers/env_sim.py` | `gpu_state` 从伪造 torch 改为伪造 ORT providers + 名称/显存补充（API 兼容，既有 27 项测试不改断言语义） |
| `tests/providers/test_devices.py` | no-runtime 断言改 "onnxruntime"；新增 EP 矩阵 7 项测试 |
| `apps/desktop-avalonia/scripts/gpu_probe.py`（新） | build venv 探测脚本（输出 `device-probe` JSON，供打包/证据） |
| `apps/desktop-avalonia/scripts/package.ps1` | 新增 `-BuildPython`；写 `VERSION.json.devices`（来自 gpu_probe）并复制到 `app/VERSION.json` |
| `apps/desktop-avalonia/src/NewManga.App/Services/DeviceStatus.cs`（新） | 读 `VERSION.json.devices` → 「GPU：<name> · DirectML 可用」/「不可用（detail）」 |
| `apps/desktop-avalonia/src/NewManga.App/Views/Pages.cs` | 设置页新增「运行环境 · GPU」卡片（`DeviceStatusText`，无元数据时显示"未打包探测（开发运行）"） |
| `apps/desktop-avalonia/tests/NewManga.App.Tests/DeviceStatusTests.cs`（新） | 4 项 headless 测试：available / CPU-only / 缺失+损坏元数据 / 设置页渲染 |

## 3. 验证记录

- 真机（发布件 + BOOK-FIXTURE 隔离根）：设置页「运行环境 · GPU」= **GPU：NVIDIA GeForce RTX 5070 Ti ·
  DirectML 可用**；探测源行注明 ONNX Runtime 执行提供程序（打包时写入 VERSION.json）。
- 打包：`package.ps1 -OutputRoot task-envs/GPU-ORT-PROBE-1/out` → base zip 97.88MB，VERSION.json.devices：
  `providers=[DmlExecutionProvider, CPUExecutionProvider]`、`name=NVIDIA GeForce RTX 5070 Ti`、
  `total_memory_mb=16303`、`state=available`。
- 闭包：`build_sidecar.ps1 -Force` → `closure assertion: ... (856 pure modules, torch-free) + ... DirectML.dll`。
- 回归：pytest 3F/2746P/9S（0 新增失败）；`test.ps1` 见 `dotnet-all.log`。

## 4. 遗留 / NOT_RUN

1. CUDA-torch 开发机路径无法本机实测（build venv torch 为 CPU 版）：由单测（torch 仅名称补充）覆盖。
2. 设备名来自注册表显示适配器（本机有 3 个虚拟适配器，按显存最大者选）；无注册表时退化为 EP 标签。
3. 打包记录的 `devices` 是**打包环境**的 EP 能力，不是逐次启动实时值；实时探测仍在 Core 内，
   本 Task 未新增 IPC 面（协议/Host 契约冻结）。
4. 需独立 Review（Owner 不得自审）。
