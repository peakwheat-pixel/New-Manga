# 全量测试的 9 个失败：分类与根因（2026-10-20）

**产出**: 2026-10-20 · **依据**：`tests/` 全量运行
**用途**：此前只记录了「9 个失败是 pre-existing」（`PDF-STREAM-FIX-1/ac5-regression-baseline-comparison.md`）。
**本文档进一步拆解：它们不是同一类问题，处置方式也不同。**

## 一、结论先行

| 类别 | 数量 | 性质 | 能否在本机修复 |
|---|---:|---|---|
| **A. 环境版本过旧** | **2** | `transformers 4.48.3` < 权重要求的 `4.49.0` | **否**（离线，无索引无缓存）|
| **B. 测试假设「机器是裸的」** | **4** | 测试把「没装可选依赖」写成断言 | **是**（改测试，不改产品）|
| **C. workbench 时序/投影** | **3** | **未深究** | 未知 |

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

**修复方式是 `pip install "transformers>=4.49.0"`。**

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

## 四、C 类：workbench（3 个，未深究）

| 测试 | 首条断言 |
|---|---|
| `test_projection.py::test_pending_run_all_waiting_and_pause_stop_enabled` | `assert False is True` |
| `test_projection.py::test_button_matrix_all_statuses` | `assert (False, True, False) == (True, True, False)` |
| `test_workbench_viewmodel.py::test_pause_shows_optimistic_feedback_immediately` | `assert False` |

**这三个我没有查根因。**

**它们可能是**：
- **产品缺陷**（UI 状态投影错了）
- **测试过期**（期望值对应旧行为）

**从名字看涉及 pause 的乐观反馈与按钮矩阵投影。**

**我无法从断言文本区分这两者**，需要读 `tests/workbench` 与被测的 projection/ViewModel 代码。

**所以：C 类既不能算「环境问题」，也不能算「已证明无害」。**

## 五、对「9 failed」的准确表述

**此前我写**：「9 个失败是 pre-existing」。

**准确的说法是**：

| 类别 | 数量 | 是否产品缺陷 |
|---|---:|---|
| **环境版本过旧（transformers）** | **2** | **否**（代码与权重都正确）|
| **测试假设机器无 GPU/无 manga-ocr** | **4** | **否**（产品行为正确）|
| **workbench 时序/投影** | **3** | **未知**（未深究）|

**所以「6 个不是产品缺陷、3 个待查」比「9 个都是 pre-existing」更准确。**

**而「pre-existing」这个词本身容易读成「老问题、不重要」——**
**其中 2 个是**真实的功能不可用**（韩漫/日漫检测链路在本机跑不起来）。**

## 六、建议（需 Codex 裁定，不在本文件实施）

1. **A 类**：在有网络的机器上升级 `transformers>=4.49.0`，然后复跑 `tests/providers`。
2. **B 类**：把 4 个测试改为「按运行时前提分支」，两侧都断言（见 §三）。**不得改断言值。**
3. **C 类**：先诊断，再定性。

## 七、明确未做

- **未改任何测试或 `src/`**
- **未尝试升级 transformers**（离线，`pip index` 不可达，缓存为空）
- **未诊断 C 类 3 个失败**
- **未立 Task**（Plan 已收口，需先由 Codex 裁定是否纳入）
