# TEST-ENV-ASSUMPTIONS-1：两侧覆盖与判别力证据

**产出**：2026-10-20 · **分支** `agent/dsh/TEST-ENV-ASSUMPTIONS-1`
**base** `a3d5dfd8a`

## 一、问题

**4 个测试把「这台机器没装可选重运行时」写成了硬断言。**

| 测试 | 原断言 | 本机实际 |
|---|---|---|
| `test_production_stack_starts_without_heavy_runtimes` | `states["manga-ocr"] == "missing_dependency"` | **`'ready'`** |
| `test_real_environment_reports_optional_providers_as_not_ready` | `status.ready is False` | **`True`** |
| `test_gpu_is_unavailable_without_a_runtime_but_reported_not_invented` | `info.state == GPU_UNAVAILABLE` | **`'available'`** |
| `test_cpu_fallback_only_when_the_provider_declares_it` | `plan.device == DEVICE_CPU` | **`'gpu'`** |

**两个测试的**名字**承认了前提（`without_a_runtime` / `without_heavy_runtimes`），代码从未检查前提。**

**所以它们在 CI 裸机上绿、在有依赖的机器上红——而这与 `DeviceManager` 或 Provider 就绪规则是否正确**毫无关系**。**

## 二、做法：把环境状态变成测试输入

**新增测试专用模块** `tests/providers/env_sim.py`（**只被测试导入，`src/` 完全不知道它存在**）。

**用了两个**已有**的 seam，没有新增任何生产接口**：

| seam | 位置 | 使用方 |
|---|---|---|
| `dependencies.probe_module` | `infrastructure/providers/dependencies.py:81` | `evaluate_requirements` 在**调用时**通过模块全局查找 |
| `manager._module_present` | `infrastructure/devices/manager.py:50` | `DeviceManager._probe_gpu` |

**两者本来就是这个问题的**唯一**答案来源，所以 patch 它们不是发明 seam，是使用已有的那个。**

**三个上下文管理器**：

- `modules_state(present=…, absent=…)` —— 强制指定模块探针结果
- `with_optional_runtimes(available=…)` —— 一次性覆盖全部可选运行时
- `gpu_state(available=…)` —— 强制 GPU 可见/不可见；
  **可用侧还需注入一个伪 `torch` 到 `sys.modules`**，因为探针在模块检查通过后会真的 `import torch`

## 三、两侧覆盖

**每个原测试改成**强制**其前提，并新增一条**相反**侧测试：**

| 行为 | 缺失侧（原，已改为强制） | 存在侧（新增） |
|---|---|---|
| **GPU 探针** | `test_gpu_is_unavailable_without_a_runtime_but_reported_not_invented` | **`test_gpu_is_reported_available_when_a_runtime_is_present`** |
| **GPU 规划** | `test_cpu_fallback_only_when_the_provider_declares_it` | **`test_plan_uses_the_gpu_when_one_is_available_and_does_not_fall_back`** |
| **Provider 就绪** | `test_real_environment_reports_optional_providers_as_not_ready` | **`test_optional_providers_report_ready_when_their_runtimes_are_present`** |
| **应用装配** | `test_production_stack_starts_without_heavy_runtimes` | **`test_production_stack_reports_optional_runtimes_as_ready_when_present`** |

## 四、判别力：7 个 sabotage 全部被抓

**覆盖一侧只有在**行为错时它会红**才算覆盖。**

**第一版判别检查失败了，而失败本身有信息量**：

**我先破坏 `_module_present` / `probe_module`，结果 sabotage 被 `env_sim` 自己覆盖了**——
**helper 在同一批名字上做 patch，所以测试照旧通过。**

**那不是测试的漏洞，是**检查的漏洞**：破坏点必须落在 helper 不碰的地方。**

**改破坏 `DeviceManager._probe_gpu` 与 `registry.failure_for`**（决策点本身）：

| # | sabotage | 目标测试 | 结果 |
|---:|---|---|---|
| 1 | `_probe_gpu` 永远报不可用 | GPU 存在侧 | **RED** |
| 2 | `_probe_gpu` 永远报可用 | GPU 缺失侧 | **RED** |
| 3 | `_probe_gpu` 永远报可用 | CPU fallback | **RED** |
| 4 | `failure_for` 永远返回失败 | Provider 存在侧 | **RED** |
| 5 | `failure_for` 永远不返回失败 | Provider 缺失侧 | **RED** |
| 6 | `failure_for` 永远不返回失败 | 装配缺失侧 | **RED** |
| 7 | `failure_for` 永远返回失败 | 装配存在侧 | **RED** |

**`ALL 7 SABOTAGES CAUGHT`。**

**第 2、3、5、6 条尤其重要**：它们证明**原来的**测试方向也仍在断言——
**如果只把断言改成「总是可用」，缺失侧会立刻红。**

## 五、套件结果

| 范围 | 改动前 | 改动后 |
|---|---|---|
| `tests/providers` | **6 failed**, 432 passed, 3 skipped | **2 failed**, 440 passed, 3 skipped |

**剩余 2 个失败**：

```
test_detection_manga_real.py::test_real_detection_returns_block_candidates
test_detection_manga_real.py::test_real_blank_page_yields_zero_candidates
```

**都是 `transformers 4.48.3` 缺 `RTDetrV2ForObjectDetection`。**

**它们属于 `M2-PROD-DETECT-ENV-1`（`blocked`，本机离线无法升级），不属于本 Task。**

**本 Task 的 4 个目标全部转绿，且新增 4 个存在侧测试，净增 8 个有效断言组。**

## 六、明确未做

- **未修改 `src/**`**（`env_sim` 只 patch，不改实现）
- **未修改 `requirements.txt`**
- **未用 `skip` 替代任何一侧**——`tests/providers` 的 3 个 skip 全部是改动前就有的
  （`importorskip` 与既有条件跳过），本 Task 未新增 skip
- **未把断言值改成当前机器的实际值**
- **未处理 2 个 `transformers` 失败**（属 `M2-PROD-DETECT-ENV-1`）
- **未新增生产接口**

## 七、可复现

```powershell
$env:PYTHONPATH = "G:\CODEX\New Manga;G:\CODEX\New Manga\src"
python -m pytest tests/providers -q
# 期望：2 failed, 440 passed, 3 skipped（2 个失败属环境 Task）
```

**判别力检查脚本未入库**（一次性验证工具）；其逻辑见 §四，
任何人对 `DeviceManager._probe_gpu` / `registry.failure_for` 施加表中破坏即可复现。
