# GPU-ORT-PROBE-1 报告：GPU 状态改 ORT EP 探测（打包后正确显示）

- Task: `doc/tasks/GPU-ORT-PROBE-1.md`（team task-27）；Branch/Worktree: `task/GPU-ORT-PROBE-1` /
  `G:/CODEX/New Manga.workspace/worktrees/GPU-ORT-PROBE-1`；卡面 Base `171529b5d`，实际基于释放提交
  `04b657131`（该提交才包含任务卡与治理 PASS 的 STATUS/PLAN/LEDGER）
- 未 push；未改推理默认 EP、模型清单、协议/Host 契约、旧壳。

## 0. 结论

| AC | 判定 | 证据 |
|---|---|---|
| AC1 探测替换 | **MET** | `infrastructure/devices/manager.py`：可用性判据改为 `onnxruntime.get_available_providers()`（DML/CUDA/ROCm/MIGraphX/TensorRT→CPU），返回设备名+状态；Windows 显示适配器注册表（`DriverDesc`/`qwMemorySize`，stdlib）补设备名/显存；torch 仅在可导入时作为名称补充，不再作主判据 |
| AC2 打包验证 | **MET** | 重建 torch-free 闭包 → 重新打包（base 97.88MB）→ 发布件启动并打开「设置」：**「GPU：NVIDIA GeForce RTX 5070 Ti · DirectML 可用」**；截图 `screens/01-settings-gpu.png` + `settings-page-evidence.json` + `device-probe-buildenv.json` |
| AC3 单测 | **MET** | EP 矩阵（DML only / CUDA+DML / CPU only / 空 providers / torch-only 补充 / snapshot）7 项新增；`tests/providers/test_devices.py` **28 passed** |
| AC4 回归 | **MET** | pytest **3 failed, 2746 passed, 9 skipped**（基线 3F/2739P/9S，新增 7 项测试；失败集合与基线相同，0 新增失败）；`scripts/test.ps1` 见 §4；sidecar 构建闭包断言 **torch-free** |
| AC5 门禁 | **MET** | `check.ps1 -TaskPath` PASS；64-hex pin；Handoff |

## 1. AC1 实现（`src/infrastructure/devices/manager.py`）

- `_onnxruntime_providers()`：导入 onnxruntime 并读 `get_available_providers()`；导入失败/运行时异常
  fail-closed 为空元组（不猜设备）。优先级 `DmlExecutionProvider` > `CUDAExecutionProvider` >
  `ROCmExecutionProvider` > `MIGraphXExecutionProvider` > `TensorrtExecutionProvider`。
- `_windows_gpu_name()`：Windows 注册表显示适配器类
  `HKLM\SYSTEM\CurrentControlSet\Control\Class\{4d36e968-...}\*\DriverDesc` + `HardwareInformation.qwMemorySize`，
  选显存最大的适配器（本机有 3 个虚拟显示适配器，RTX 5070 Ti 胜出）；只用 stdlib `winreg`，失败返回 None。
- `_torch_supplement()`：仅开发环境可用时补设备名/显存，**不改可用性判据**。
- `probe_snapshot()`：输出 `{onnxruntime_providers, gpu: DeviceInfo}`，供打包元数据/证据使用。
- 可用时 `DeviceInfo.detail` 记录 `providers=[...]` 与 `execution_provider=...`；不可用时给出
  "onnxruntime has no GPU execution provider(...)"（保留 torch 补充说明）。

## 2. AC2 打包与 UI

- 打包链路：`scripts/gpu_probe.py`（build venv 运行，ORT 已装）→ `scripts/package.ps1` 在写
  `VERSION.json` 时记录 `devices`（本机：`DmlExecutionProvider`、`NVIDIA GeForce RTX 5070 Ti`、16303 MB、
  state=available），并同时复制一份到 `app/VERSION.json` 旁确保 single-file host 可读。
- 设置页新增「运行环境 · GPU」卡片：`Services/DeviceStatus.cs` 读 `VERSION.json.devices`，
  显示「GPU：<name> · DirectML 可用」；非打包运行（无 VERSION.json）显示「未打包探测（开发运行）」。
  4 项 headless 测试覆盖 available/CPU-only/缺失/损坏元数据与设置页渲染。
- 真机截图：`verification/GPU-ORT-PROBE-1/screens/01-settings-gpu.png`（发布件 + BOOK-FIXTURE 隔离根启动）。

## 3. AC4 回归

| 门 | 结果 |
|---|---|
| pytest（基线 3F/2739P/9S） | **3 failed, 2746 passed, 9 skipped**：失败集合=基线 3 项；通过数 +7（本任务新增 EP 矩阵测试） |
| `scripts/test.ps1` | 见 `dotnet-all.log`（App/CoreClient/Host 三项目） |
| 闭包 torch-free（spec 断言） | `packaging/m2ac5/build_sidecar.ps1 -Force` exit=0：`closure assertion: core_service carries ONNX Runtime ... (856 pure modules, torch-free) + ... DirectML.dll`、`sfx_detect_probe ... torch-free` |
| 打包体积 | base zip 97.88 MB ≤150 MB；许可三件套逐字节一致（沿用 package.ps1 校验） |

## 4. 遗留 / NOT_RUN

1. `torch` 分支（CUDA torch 开发机）本机无法实测（build venv 的 torch 为 CPU 版）；行为由单测覆盖。
2. 注册表名称是显示适配器（虚拟适配器可能干扰），已按显存最大者选择；未知/无注册表时退化为 EP 标签。
3. `device-probe` 记录的是**打包环境**的 EP 列表（分发包能力），不是每次启动的实时探测；实时探测仍在
   Core 内（`DeviceManager.gpu_info()`），本 Task 未新增 IPC 面（协议/Host 契约冻结）。
4. 需独立 Review（Owner 不得自审）。
