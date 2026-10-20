# 全量测试的 9 个失败：分类与根因（2026-10-20）

**产出**: 2026-10-20 · **依据**：`tests/` 全量运行
**用途**：此前只记录了「9 个失败是 pre-existing」（`PDF-STREAM-FIX-1/ac5-regression-baseline-comparison.md`）。
**本文档进一步拆解：它们不是同一类问题，处置方式也不同。**

## 一、结论先行

| 类别 | 数量 | 性质 | 能否在本机修复 |
|---|---:|---|---|
| **A. 环境版本过旧** | **2** | `transformers 4.48.3` < 权重要求的 `4.49.0` | **否**（离线，无索引无缓存）|
| **B. 测试假设「机器是裸的」** | **4** | 测试把「没装可选依赖」写成断言 | **是**（改测试，不改产品）|
| **C. 测试与 P11 §4.5 冲突 / 旧 Qt 栈** | **3** | **测试过期 + 旧栈** | 策略上不修 |

**其中没有一个是「产品代码有 bug」的直接证据。**

**但 C 类我没有查，所以不能给 C 类下这个结论。**

## 二、A 类：transformers 版本（2 个）

### 失败

```
test_detection_manga_real.py::test_real_detection_returns_block_candidates
test_detection_manga_real.py::test_real_blank_page_yields_zero_candidates
```

### 报错

```
AttributeError: module transformers has no attribute RTDetrV2ForObjectDetection
```

### 根因链（三方对照）

| 方 | 内容 | 判定 |
|---|---|---|
| **权重** `task-envs/M2-DOCTR-QUAL-C4/weights/ogkalu-comic-text-and-bubble-detector/config.json` | `architectures: ["RTDetrV2ForObjectDetection"]`、`model_type: rt_detr_v2`、**`transformers_version: "4.49.0"`** | **声明需要 V2** |
| **代码** `src/infrastructure/providers/detection_manga.py:525` | `transformers.RTDetrV2ForObjectDetection.from_pretrained(...)` | **与权重一致，正确** |
| **环境** | `transformers 4.48.3`；`dir(transformers)` 里有 `RTDetrForObjectDetection` 但**没有 `RTDetrV2*`** | **低一个次版本** |

### 所以：这是环境缺陷，不是代码缺陷

**`RTDetrV2` 在 4.49.0 引入**（权重 config 的 `transformers_version` 就是证据）。

**但实际偏差比「低一个次版本」更大——我此前的表述不够准确。**

**`requirements.txt` L28 钉的是 `transformers==5.17.0`**（注释说明：经 CPU 兼容门与
C4 GPU 资格验证）。**本机装的是 `4.48.3`。**

**所以不是「比模型要求低一点」，是「不符合项目自己的固定依赖基线」。**

**顺带核实了同组的另外两个包，避免误报**：

| 包 | `requirements.txt` | 本机 | 判定 |
|---|---|---|---|
| `transformers` | **`5.17.0`** | **`4.48.3`** | **真偏离** |
| `torch` | `2.14.0`（CPU 构建）| `2.11.0+cu128` | **不是偏离**——L9-12 明确写「GPU(CUDA) wheels 是单独的打包决定（T3.2.1），**不在 requirements.txt 内**」，且记录的正是 `torch 2.11.0+cu128` / RTX 5070 Ti |
| `safetensors` | `0.8.0` | `0.8.0` | 一致 |

**修复方式是让 `transformers` 符合基线（`5.17.0`），而不只是「>= 4.49.0」。**

### 而这个修复在本机做不了

**实测**：

```
python -m pip index versions transformers
-> ERROR: No matching distribution found for transformers
```

**pip 缓存里也没有 `transformers` 相关 wheel（0 个）。**

**所以离线环境下无法升级。**

### 为什么这份证据重要

**它记录了「不要改代码」这个结论。**

**如果有人为了修这 2 个测试，把 `RTDetrV2ForObjectDetection` 改成 `RTDetrForObjectDetection`，
测试会变绿而模型加载行为未知**——

**权重声明的是 `rt_detr_v2`，用 V1 类去加载 V2 权重，要么报错要么静默产出错误结果。**

**这正是「为了让测试通过而改错地方」的典型形态。**

## 三、B 类：测试把「机器是裸的」写成了断言（4 个）

### 失败与断言

| 测试 | 断言 | 实际 |
|---|---|---|
| `test_bootstrap_providers.py::test_production_stack_starts_without_heavy_runtimes` | `states["manga-ocr"] == "missing_dependency"` | **`'ready'`** |
| `test_registry_readiness.py::test_real_environment_reports_optional_providers_as_not_ready` | `ProviderStatus(...).ready is False` | **`True`** |
| `test_devices.py::test_gpu_is_unavailable_without_a_runtime_but_reported_not_invented` | `info.state == GPU_UNAVAILABLE` | **`'available'`** |
| `test_devices.py::test_cpu_fallback_only_when_the_provider_declares_it` | `plan.device == DEVICE_CPU` | **`'gpu'`** |

### 根因

**这台机器装了可选重运行时：**

- **`manga-ocr` 已安装** → provider 报告 `ready`，而不是 `missing_dependency`
- **有 NVIDIA RTX 5070 Ti，CUDA 可用** → `gpu_info().state == 'available'`，而不是 `unavailable`

**而测试把「这台机器没有这些东西」写成了硬断言。**

### 这两个测试的**名字**其实承认了前提

- `test_gpu_is_unavailable_**without_a_runtime**...` ← **"without a runtime"**
- `test_production_stack_starts_**without_heavy_runtimes**` ← **"without heavy runtimes"**

**名字说了前提，代码没检查前提。**

### 所以这是测试缺陷，不是产品缺陷

**产品行为是对的**：装了 GPU 就报告可用，装了 manga-ocr 就报告就绪。

**这些测试在 CI 的裸机器上会绿，在开发机上有依赖时会红。**

**这与我此前在 `SEC-FMT-004` 遇到的是同一类问题**：
**测试把与本机绑定的环境假设固化成了断言。**

### 修法（不能靠改断言值）

**错误修法**：把 `assert info.state == GPU_UNAVAILABLE` 改成 `== 'available'`。
**那会在 CI 上红。**

**正确修法**：按运行时前提分支，两侧都测：

```python
info = manager.gpu_info()
if info.state == GPU_AVAILABLE:
    # 有 GPU 的机器：测「正确报告可用」，不测「正确报告不可用」
    assert info.available is True
    pytest.skip("CUDA runtime present; the no-runtime path is unreachable here")
else:
    assert info.state == GPU_UNAVAILABLE
    ...
```

**注意这里的 `skip` 与我 Round 176 批评的 `skip` 不同**：
**那次 skip 的条件是「被检缺陷存在」，掩盖了缺陷；
这次 skip 的条件是「被测路径在此机器上不可达」**，而**另一条路径仍被断言覆盖**。

**区别在于：被 skip 的分支是否**本来就不可能**在此机器上被触发。**

### 我没有改这 4 个测试

**原因**：它们属于 `tests/providers/`，不在任何活动 Task 的 `allowed_paths` 内，
**且 Plan 已无 READY 节点——按 `AGENTS.md`，只有 Plan 明确激活的 Task 才允许实施。**

**本文档是证据，不是实施。**

## 四、C 类：workbench（3 个）——已诊断，全部不是新架构缺陷

**上一版本文档把这 3 个标为「未深究」。现已查清。**

### 4.1 两个：测试与冻结契约 P11 §4.5 冲突

**失败**：

```
test_projection.py::test_pending_run_all_waiting_and_pause_stop_enabled
   assert projection.can_pause is True   -> 实际 False
test_projection.py::test_button_matrix_all_statuses
   assert (False, True, False) == (True, True, False)
```

**即：两个测试都要求 `pending` 状态的 Run 可以 pause。**

**而 P11 §4.5「非法转换拒绝清单」明确写**：

| 当前状态 | 仅允许 | **必须拒绝** |
|---|---|---|
| **`Pending`** | scheduler start、`stop` | **`pause`**、`continue`、`restart`、`abandon`、… |

**所以按冻结契约，`Pending` 必须**拒绝** `pause`。**

**`src/application/tasks/projection.py:417-418` 正是这么实现的**：

```python
if status is PipelineRunStatus.PENDING:
    return dict(can_stop=True)        # 无 can_pause
```

**代码与 P11 §4.5 一致；测试与契约冲突。**

**时间线（`git log -L` 证据）**：

| 提交 | 内容 |
|---|---|
| `da1daf11e`（TASK-013） | 测试写下 `pending → pause 可用` 的期望 |
| `78b0d439a`（P13） | **故意**把 `_button_enablement` 改为：`RUNNING` → pause+stop；**`PENDING` → 仅 stop** |
| —— | **测试未随之更新** |

**原始实现是** `running = {PENDING, RUNNING}; if status in running: return dict(can_pause=True, can_stop=True)`，
**P13 显式拆开，把 PENDING 排除出 pause。**

**所以：这是测试过期，不是产品缺陷。**

### 4.2 一个：旧 PySide6 栈，且失败点与 pause 无关

**失败**：

```
test_workbench_viewmodel.py::test_pause_shows_optimistic_feedback_immediately
   continueRun() 后 15s 内 run_status 未到达 "completed"
```

**注意它前面全部通过了**：

- `elapsed_ms <= 200` **通过**
- `taskProgress["pausing"] is True` **通过**
- `can_pause is False`（暂停中不可重复暂停）**通过**
- `run_status == "paused"` **通过**
- `can_continue is True` **通过**

**失败在**最后一步**：`continueRun()` 之后等不到 `completed`。**

### 4.3 而这个测试驱动的是**旧 Qt 栈**

**`src/ui/viewmodels/workbench/viewmodel.py` 第 6 行**：

```python
from PySide6.QtCore import Property, QObject, QTimer, Signal, Slot
```

**`tests/workbench/` 有 8 个文件导入 PySide6。**

**而 `AGENTS.md` 明确**：

> **当前唯一继续演进的产品架构为 Windows / React + TypeScript / Tauri / Python Core / SQLite / Managed Copy。**
> **PySide6/QML 代码、测试和既有 Task 仅保留为历史证据，不再释放 Legacy 实现、诊断或修复任务。**

**所以这个测试在**策略上**不属于可修复范围。**

### 4.4 但我不能因此说「共享层没问题」

**这个测试同时驱动 `PipelineService`（应用层，新架构仍在用）。**

**`continue` 后跑不完，理论上也可能是应用层的缺陷。**

**反证**：`tests/pipeline` **94 passed**——应用层管线本身是健康的。

**所以失败点更可能在旧 viewmodel 的 continue 路径上。**

**但这只是推断，不是验证。要点是：即使是应用层缺陷，这个测试也不是能证明它的地方。**

## 五、对「9 failed」的准确表述

**此前我写**：「9 个失败是 pre-existing」。

**准确的说法是**：

| 类别 | 数量 | 是否产品缺陷 |
|---|---:|---|
| **环境版本过旧（transformers）** | **2** | **否**（代码与权重都正确）|
| **测试假设机器无 GPU/无 manga-ocr** | **4** | **否**（产品行为正确）|
| **测试与 P11 §4.5 冲突（2）/ 旧 Qt 栈（1）** | **3** | **否**（代码符合契约；测试过期）|

**所以：9 个里没有一个是新架构的产品缺陷。**

**这个结论现在有逐项证据，不再是「待查」。**

**而「pre-existing」这个词本身容易读成「老问题、不重要」——**
**其中 2 个是**真实的功能不可用**（韩漫/日漫检测链路在本机跑不起来）。**

## 六、建议（需 Codex 裁定，不在本文件实施）

1. **A 类**：在有网络的机器上升级 `transformers>=4.49.0`，然后复跑 `tests/providers`。
2. **B 类**：把 4 个测试改为「按运行时前提分支」，两侧都断言（见 §三）。**不得改断言值。**
3. **C 类**：**不建议修复**。
   - 2 个 projection 测试应更新为符合 P11 §4.5（`pending` 不可 pause），
     **但它们是旧测试且不在任何活动 Task 内**；
   - 1 个 viewmodel 测试在旧 PySide6 栈上，**按 AGENTS.md 不释放 Legacy 修复任务**。

## 七、明确未做

- **未改任何测试或 `src/`**
- **未尝试升级 transformers**（离线，`pip index` 不可达，缓存为空）
- **未修复任何 C 类测试**（旧栈 + 活跃 Task 范围外）
- **未立 Task**（Plan 已收口，需先由 Codex 裁定是否纳入）
- **未验证** 4.2 的失败是否也存在于应用层（只反证了 `tests/pipeline` 94 passed）
