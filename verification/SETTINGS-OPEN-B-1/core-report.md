# SETTINGS-OPEN-B-1 Core 实现报告（批次 B-1：模型/GPU + 任务/并发）

- 团队任务：`task-5`
- 实现 agent：`core-settings-b1`（DeepSeek Harness）
- 仓库 / 分支：`G:\CODEX\New Manga` / `main`（base HEAD `da3b781`，未 commit、未 push）
- 依据：[SETTINGS 分区 Schema 设计 §4.1–§4.2](../../doc/design/SETTINGS_SECTION_SCHEMAS.md)、[SETTINGS-OPEN-B-1 任务](../../doc/tasks/SETTINGS-OPEN-B-1.md)、批次 A 已批准实现（[settings_sections.py](../../src/bootstrap/settings_sections.py)、[handlers.py](../../src/infrastructure/providers/handlers.py) 的 `typeset_style_defaults`、[manager.py](../../src/infrastructure/devices/manager.py) 的 `DeviceManager.plan/run_guarded`）
- 实现范围：`src/bootstrap/settings_sections.py`、`src/infrastructure/{devices/manager,providers/runtime,providers/handlers}.py`、`tests/core/**`、`tests/providers/**`、`verification/SETTINGS-OPEN-B-1/**`；**r1 返修**按 Review B1/Lead 指令新增 `src/infrastructure/providers/registry.py` 的只读 `descriptor()` 方法（超出原 write scope，已由 Lead 在返修指令中明确授权）
- 并行关系：前端（task-6，`ui-settings-b1`）提交的 wire 节名已只读核对为 `model_gpu` / `tasks`，与本实现一致；前端报告见 [ui-report.md](ui-report.md)

## 1. 交付结论

| AC | 结论 | 证据 |
|---|---|---|
| AC1 Core 写入校验 | 完成：`model_gpu` / `tasks` 进入白名单；未知键、非法值、bool/int 混用均 `INVALID_REQUEST` 且不落库 | §5.2、§5.3 |
| AC2 模型/GPU 消费点 | Core 完成（r1 返修后）：`heavy_runner` 读 Run 快照 `model_gpu`；`requires_gpu` / `supports_cpu_fallback` 取自 registry 的 `ProviderDescriptor`（真实 provider 的声明源），显式偏好经 `DeviceManager.plan` 校验，GPU 不可用且不允许回退时抛 typed `DeviceUnavailable`，允许回退时真实执行；`auto` 零行为变化 | §3.2、§5.2、§8 |
| AC3 任务/并发消费点 | Core 完成：按 Run 快照 `tasks` 构造 `RetryPolicy`；未设置时与 `deps.retry_policy` 同一对象（等价）；非 Mapping 快照按空节处理（r1 m1） | §3.3、§5.2 |
| AC4 前端两面板 | 非本 agent（task-6 已交付，见 [ui-report.md](ui-report.md)） | — |
| AC5 测试与证据 | pytest 证据见 §5；GUI 烟测 / 真实 GPU 端到端 / 独立 Review 见 §6 NOT_RUN | §5 |

- 未设置 `tasks` 节时，`run_chain` 收到的就是装配期 `deps.retry_policy` 对象本身（不是"等值的新对象"），因此重试次数/退避/`retry_codes`/`Retry-After` 消费器全部与 HEAD 行为逐位相同；测试从"对象同一性"与"真实重试循环次数"两面证明（§5.2）。
- 未设置/`auto` 的 `model_gpu`：`preferred_device=None` → `ProviderRuntime.heavy_runner` 直通 `self.devices.run_guarded(requires_gpu=..., call=...)`（签名/调用形状与 HEAD 完全一致），`DeviceManager.run_guarded` 分支不调用 `plan`；测试用 monkeypatch 断言 `auto` 路径从不触碰 `plan`（§5.2）。

## 2. 改动清单

| 文件 | 变更 |
|---|---|
| `src/bootstrap/settings_sections.py` | 新增 `_MODEL_GPU_RULES`（`device_preference: auto\|cpu\|gpu`、`allow_cpu_fallback: bool`）与 `_TASKS_RULES`（`retry_max_attempts: int 1..3`、`retry_backoff_seconds: float 0.1..30`），注册进 `_SECTIONS`；模块/函数 docstring 更新为批次 A + B-1。复用既有 `_normalize`（enum/bool/int/float），因此 bool 不作 int、未知键 fail-closed 的语义与批次 A 完全一致 |
| `src/infrastructure/providers/handlers.py` | ① 新增 `_EXPLICIT_DEVICE_PREFERENCES`；② `_invoke_provider` 增加 keyword-only `run: PipelineRun`，`heavy_runner` 调用点从 Run 快照 `model_gpu` 读取 `device_preference`/`allow_cpu_fallback`，`requires_gpu`/`supports_cpu_fallback` 取自 registry descriptor（r1 返修；descriptor 缺失时回退 provider 实例属性）；③ 新增 `_retry_policy_for_run(run)`（`tasks` → `RetryPolicy`，缺省/非法值回落装配期 policy，保留 `retry_codes` 与 `retry_after_provider`）；④ OCR / translate 两处 `run_chain` 的 `policy=self.deps.retry_policy` 改为 `policy=self._retry_policy_for_run(run)`；⑤ 新增 `_clamped_int` / `_clamped_number` 防御性夹取助手；⑥ `_section` 对非 Mapping（含 None）快照返回空节（r1 m1） |
| `src/infrastructure/providers/registry.py` | **r1 返修新增**：公开只读 `descriptor(provider_id, *, capability=None) -> ProviderDescriptor \| None`，供运行期读取 `requires_gpu`/`supports_cpu_fallback` 声明；给出 `capability` 时复用 `resolve` 同款 binding-alias 翻译；未知 id 返回 `None`，`resolve` 语义不变 |
| `src/infrastructure/providers/runtime.py` | `ProviderRuntime.heavy_runner` 增加 `preferred_device=None / allow_cpu_fallback=True / supports_cpu_fallback=False` 关键字；`preferred_device is None` 时**原样**调用 `self.devices.run_guarded(requires_gpu=requires_gpu, call=call)`（零行为变化），否则转发扩展参数 |
| `src/infrastructure/devices/manager.py` | `DeviceManager.run_guarded` 增加同三关键字；`preferred_device is not None` 时先调用 `self.plan(requires_gpu=..., supports_cpu_fallback=supports_cpu_fallback and allow_cpu_fallback, preferred_device=preferred_device)` 并让 `DeviceUnavailable` 直接传播，然后走既有 heavy gate / OOM 路径；`preferred_device is None` 时旧代码路径逐行不变 |
| `tests/core/test_settings_b1_sections.py` | **新建**（60 tests）：白名单合法/规范化/边界；非法值、未知键、bool/int；`settings.update_section` 真实装配下的落库/拒绝/未设置 null 投影；保存后下一 Run 快照冻结（AC2/AC3 的前置条件） |
| `tests/providers/test_handlers_b1_settings.py` | **新建**（r1 后 47 tests）：`_retry_policy_for_run` 有无 `tasks` 节/部分键/越域/非数字/非 Mapping 快照；两个 `run_chain` 调用点的 policy 来源；真实重试循环次数随 `tasks.retry_max_attempts` 变化；`_invoke_provider` → `heavy_runner` 偏好/回退参数矩阵（r1 起断言的 flags 来自 **descriptor**，替身实例不带属性）；OCR 端到端偏好 + descriptor `supports_cpu_fallback` 传递；真实 `DeviceManager` 链路回归（descriptor True + 无 GPU + 用户允许 → 实际执行；用户拒绝/descriptor False → `DeviceUnavailable` 且 call 未执行；`auto` 仍走未计划旧路径） |
| `tests/providers/test_devices.py` | 追加 10 tests：gpu 偏好 + GPU 不可用 + 不允许回退（用户关闭 / Provider 不支持 / 两者）→ `DeviceUnavailable` 且 call 未执行；允许回退 → 正常返回；CPU 偏好 → 正常返回且不探测 GPU；`auto` 不调用 `plan`；`auto` 保留历史"未计划 GPU 路径"；偏好路径保留 OOM 隔离 |
| `tests/providers/test_registry_readiness.py` | **r1 返修追加 2 tests**：`descriptor()` 返回静态声明、未知 id 返回 `None`；binding alias 按 capability 翻译（错误 capability 与裸 id 不命中） |
| `tests/core/test_core_service_settings.py` | 既有测试根因修复：`test_settings_commands_redact_paths_in_every_section` 的 pass-through 节列表移除已冻结的 `model_gpu`，并把 `model_gpu` / `tasks` 加入"路径形状 payload 在持久化前被拒绝"的强断言循环（§4.6） |
| `verification/SETTINGS-OPEN-B-1/core-report.md` 等 | 本报告与原始 pytest 证据（`core-pytest-*.txt`） |

未改动：`src/bootstrap/core_service.py`、`src/application/**`、`apps/desktop/frontend/**`、`doc/**`、Schema/migration、依赖清单；工作区中 `doc/**`、前端与 `verification/.../ui-report.md` 的变更为 Lead / task-6 所有，不在本报告变更清单内。

## 3. 实现语义（设计 §4.1–§4.2）

### 3.1 写入校验（AC1）

- 节名与键集严格按设计冻结：`model_gpu{device_preference, allow_cpu_fallback}`、`tasks{retry_max_attempts, retry_backoff_seconds}`；其余节（含 `cache_revision` / `recycle_bin` / `backup` / `plugins`）保持既有 pass-through（B-2/C 未释放）。
- 未知键 → `SettingsSectionError`（message 含节名、键名、allowed keys）→ `INVALID_REQUEST`/`validation`，**先于** `PipelineDefaultsService.save_settings_section`，落库前拒绝。
- `bool` 不作 `int`（`isinstance(value, bool)` 显式排除）；int 规则拒绝字符串/浮点，float 规则接受 int 并规范化为 float（JSON `30` → `30.0`）。

### 3.2 模型/GPU 消费点（AC2）

Run 快照路径：`PipelineRun.settings_snapshot["model_gpu"]` → `handlers._invoke_provider` → `deps.heavy_runner` → `ProviderRuntime.heavy_runner` → `DeviceManager.run_guarded`。

- `device_preference == "auto"`（或节/值缺失、非白名单字符串）→ `preferred_device=None`。
- `device_preference == "cpu"` / `"gpu"` → 原值传给 `plan`；`plan` 的 `requested = preferred_device or ...` 使 CPU 偏好直接成立，GPU 偏好在 GPU 不可用时按 `supports_cpu_fallback and allow_cpu_fallback` 决定回退或抛 `DeviceUnavailable`（D06 §82：用户开关与 Provider 声明相与）。
- `allow_cpu_fallback` 缺省/类型损坏 → `True`（设计默认"允许"；与批次 A 的防御性读取一致：损坏值不放大权限也不误伤默认）。
- `requires_gpu` / `supports_cpu_fallback` 取自 **`ProviderRegistry.descriptor(provider_id, capability=capability)` 的 `ProviderDescriptor` 声明**（r1 返修，见 §8）：真实 provider（`MangaOcrProvider` / `PaddleKoreanOcrProvider` 等）不在实例上重复这些声明，实例属性只作为 registry 无法回答 descriptor 时的后备。例：本地 Manga OCR 的 descriptor 为 `requires_gpu=False, supports_cpu_fallback=True`，用户选 `gpu` 且本机无 GPU、允许回退时按 D06 §82 回退 CPU 实际执行（有真实 `DeviceManager` 回归测试）。
- 偏好只影响经 `heavy_runner` 的 provider 调用（当前实现中即 OCR / translate 的 `_invoke_provider`）；`detect` / `inpaint` 等步骤现状不经过 `heavy_runner`，本 Task 不新增装配点。

### 3.3 任务/并发消费点（AC3）

`ProductionHandlers._retry_policy_for_run(run)`：

1. `run.settings_snapshot` 非 Mapping 或 `tasks` 节缺失/非 Mapping/空 → **返回 `self.deps.retry_policy` 本身**；
2. 否则逐键取值：合法数值按设计域使用；缺失/非数字（含 bool、字符串、None）→ 用装配期 policy 的同名字段；数值越域 → 夹取进 `1..3` / `0.1..30`（与 `runtime._retry_policy` 对历史 `providers.retry` 的 clamp 纪律一致，见 task-5 描述）；
3. 新 policy 复制装配期 policy 的 `retry_codes` 与 `retry_after_provider`，用户可调的只有两个键，其余语义不丢。

替代点：`handle_ocr`、`handle_translate` 两处 `run_chain(policy=...)`。全仓 `grep 'policy=self.deps.retry_policy'` 只此两处（改动后为 0 处）；`run_chain` 的其他调用点不存在（`grep 'run_chain('` 仅此两处 + `fallback.py` 定义）。

## 4. 设计/任务冲突与保守选择

1. **验收命令中的 `tests/infrastructure` 不存在（任务文本笔误，Lead 2026-10-22 已确认）**：任务原文要求运行 `python -m pytest tests/core tests/providers tests/infrastructure -q`，但本仓库无 `tests/infrastructure` 目录（`Test-Path` = False），该命令以 exit 4 失败（`ERROR: file or directory not found: tests/infrastructure`，原始输出见 `core-pytest-required-command-raw.txt`），与代码无关。Lead 已确认该路径为任务文本笔误、无需补建目录：**验收路径（含设备/GPU 测试）已由 `tests/core` + `tests/providers` 完整覆盖**（设备测试在 `tests/providers/test_devices.py`），替代证据见 §5.1/§5.3。
2. **`retry_*` 越域/损坏值的处理**：task-5 描述提到"clamp 语义与 `DEFAULT_RETRY_POLICY` 一致"，用户指令只规定"字段缺失时沿用 `deps.retry_policy` 对应值"。保守实现：数值越域 → clamp（不放大用户权限、不因损坏快照崩 step）；非数值 → 回落装配期值。二者都有测试固定；若 Review 要求"非法值一律回落 base"，改动仅在 `_retry_policy_for_run` 一行判断。
3. **`requires_gpu` / `supports_cpu_fallback` 的声明来源（r1 已修正）**：初版按用户指令从 provider 实例 `getattr` 读取，Review B1 证明真实 provider 不在实例上声明这两项，导致 `allow_cpu_fallback` 对生产 provider 永远无效、D06 §82 回退不可达。r1 起改为读 `ProviderRegistry.descriptor()`（descriptor 缺失时才回退实例属性），`resolve` 语义不变；真实 provider 的 descriptor 由 `runtime.build_provider_registry` 注册，属既有声明源。详见 §8。
4. **`model_gpu` 偏好只接 `heavy_runner` 调用点**：任务明确"heavy_runner 调用点"，未把 `plan` 扩散到 detect/inpaint 或其他直接调用；避免扩大本 Task 范围。
5. **`task_concurrency` 不是 wire 节名**：设计 §4.2 的持久化节为 `tasks`，`task_concurrency` 只是 UI 分类名。已只读核对前端 `sections.ts` 使用 `TASKS_SECTION = "tasks"` / `MODEL_GPU_SECTION = "model_gpu"`，wire 对齐；未改动前端。
6. **既有测试 `test_settings_commands_redact_paths_in_every_section` 的必要更新**：该测试原先把 `model_gpu` 当作"未冻结、pass-through"节写入路径形状 payload；B-1 冻结后该写入按设计被拒绝（这是本 Task 的目标行为）。修复方式：pass-through 列表移除 `model_gpu`，并把 `model_gpu`/`tasks` 加入"持久化前拒绝 + 不回显路径 + 存储保持未设置"的更强断言，未删除或弱化任何断言。
7. **`heavy_runner` 的 auto 调用形状**：按用户指令，`_invoke_provider` 在 auto 时也显式传 `preferred_device=None / allow_cpu_fallback=True / supports_cpu_fallback=...`（而非省略关键字）；`ProviderRuntime.heavy_runner` 内部据 `preferred_device is None` 直通旧 `run_guarded(requires_gpu, call)`，因此设备层零行为变化。装配点唯一注入 `ProviderRuntime.heavy_runner`（签名已同步扩展），仓库内无其他 heavy_runner 实现；若未来引入第三方替身需接受这三个关键字。为把 Run 快照传入该调用点，`_invoke_provider` 增加了 keyword-only `run` 参数（私有方法，仓库内仅 OCR/translate 两处调用，均已同步）。

## 5. 测试原始结果

> §5.1–§5.4 是 r1 返修**之前**、commit `7d19164` 对应实现的交付证据；Review B1/m1 返修后的最终原始结果与命令见 **§8**。

环境：Python 3.14.6、pytest 9.1.1；仓库根执行。原始输出文件均在 `verification/SETTINGS-OPEN-B-1/`。

### 5.1 验收主命令（任务原文）

```text
PS> python -m pytest tests/core tests/providers tests/infrastructure -q
no tests ran in 0.00s
ERROR: file or directory not found: tests/infrastructure
[exit code 4]
```

原始输出：`core-pytest-required-command-raw.txt`。原因见 §4.1（任务文本笔误；验收路径已由 `tests/core` + `tests/providers` 覆盖，含 `tests/providers/test_devices.py` 的 GPU/设备测试）。

### 5.2 验收范围内的实际结果

```text
PS> python -m pytest tests/core tests/providers -q
2 failed, 1212 passed, 3 skipped, 1 warning in 51.03s
FAILED tests/providers/test_detection_manga_real.py::test_real_detection_returns_block_candidates
FAILED tests/providers/test_detection_manga_real.py::test_real_blank_page_yields_zero_candidates
[exit code 1]
```

- 2 个失败是 **HEAD 基线即存在**的环境失败（改动前基线 `2 failed, 1104 passed, 3 skipped in 51.66s`，见 `core-pytest-baseline-before-change-raw.txt`），与 B-1 无关：本机 `transformers 4.48.3` 不含 `RTDetrV2ForObjectDetection`，而 `test_detection_manga_real.py` 的模块级 skip 只检查权重目录存在、不检查引擎类可用；属环境版本不匹配，不修改（改测试或装依赖均超出本 Task 范围/被禁止）。
- 新增 108 条测试（1104 → 1212 passed）：`tests/core/test_settings_b1_sections.py` 60 + `tests/providers/test_handlers_b1_settings.py` 38 + `tests/providers/test_devices.py` 新增 10。

排除上述环境模块后的全绿证据：

```text
PS> python -m pytest tests/core tests/providers -q --ignore=tests/providers/test_detection_manga_real.py
1212 passed, 3 skipped, 1 warning in 49.16s
[exit code 0]
```

原始输出：`core-pytest-core-providers-raw.txt`、`core-pytest-green-no-env-module-raw.txt`。

### 5.3 本 Task 目标子集

```text
PS> python -m pytest tests/core/test_settings_b1_sections.py \
      tests/providers/test_handlers_b1_settings.py tests/providers/test_devices.py -q
119 passed in 0.97s
[exit code 0]
```

原始输出：`core-pytest-b1-targeted-raw.txt`。分文件：settings 校验 60、handlers/runtime 38、devices 21（既有 11 + 新增 10）。

关键断言（与 AC 对应）：

- AC1：合法值写入后 `settings.get` / 存储 / 下一 Run 快照均出现规范化值；非法值/未知键 → `INVALID_REQUEST` 且 `pipeline_defaults.settings` 保持未设置；未设置节 → `settings.get` 投影 `null`，Run 快照不含该节。
- AC2：`_invoke_provider` 对 `{}` / `{"model_gpu": {"device_preference": "auto"}}` 传 `preferred_device=None`；`cpu`/`gpu` 传原值；`allow_cpu_fallback` 分别传 False/True；OCR handler 端到端把 `cpu` 偏好送达 `heavy_runner`；`run_guarded` 的 GPU 不可用矩阵：允许回退（用户允许 **且** provider 声明支持）→ 正常返回；任一不满足 → `DeviceUnavailable` 且 call 未执行；`auto` 时 `plan` 从未被调用（monkeypatch 断言）且保留"未计划 GPU 路径"。
- AC3：无 `tasks` 节时 `run_chain` 收到 `deps.retry_policy` 同一对象；真实失败 provider 的重试次数在无节时等于装配期 `max_attempts`（3），有节时精确等于 `retry_max_attempts`（1/2/3）；`retry_codes` / `retry_after_provider` 被保留。

### 5.4 全量回归

```text
PS> python -m pytest tests -q
3 failed, 2544 passed, 9 skipped, 2 warnings in 174.86s (0:02:54)
FAILED tests/providers/test_detection_manga_real.py::test_real_detection_returns_block_candidates
FAILED tests/providers/test_detection_manga_real.py::test_real_blank_page_yields_zero_candidates
FAILED tests/workbench/test_workbench_viewmodel.py::test_pause_shows_optimistic_feedback_immediately
[exit code 1]
```

原始输出：`core-pytest-full-suite-raw.txt`。三个失败均为**既有**问题、与 B-1 改动面无关：

- 前两个：§5.2 的环境版本问题（基线已失败）。
- `test_workbench_viewmodel.py::test_pause_shows_optimistic_feedback_immediately`：旧 PySide6 工作台栈的已知失败，[P11-PROJECTION-TEST-ALIGN-1](../../doc/tasks/P11-PROJECTION-TEST-ALIGN-1.md) L146 明确记为"仍失败、不释放"，且 `verification/P09-AC3-DELETE-1/t2-logs/P09-BASELINE-PRE-fullpytest.log` 在我改动前的基线就记录同一失败；本 agent 未修改 `tests/workbench/**` 或 `src/ui/**`，该测试单独运行同样失败（15s 超时，属该栈自身环境/时序问题）。

## 6. 未执行 / 遗留项

| 项 | 状态 | 说明 |
|---|---|---|
| GUI 烟测（两分区保存 + 重启复查 + 新 Run 生效） | NOT_RUN | 需真实 Tauri 应用 + Python Core 集成环境，由 Lead/集成阶段执行 |
| 真实 GPU 端到端（真 CUDA 设备上验证 `gpu` 偏好） | NOT_RUN（环境无 GPU/torch） | 分支逻辑用 `tests/providers/env_sim.py::gpu_state` 模拟覆盖，属 typed 单测证据；真实设备验证留待有 GPU 的集成环境 |
| 独立 Review（非实现者） | 待指派 | 按项目规则执行 |
| 前端 Vitest / tsc / 两面板 | 非本 agent | 已由 task-6 交付（[ui-report.md](ui-report.md)） |
| `doc/**`、STATUS/LEDGER、Task 文件状态 | 非本 agent | 工作区中相关变更为 Lead 所有；本报告未改 `doc/**` |
| `tests/infrastructure` 验收路径 | 任务文本笔误，已由 Lead 确认 | 见 §4.1；无需补建目录，`tests/core` + `tests/providers`（含 `test_devices.py`）已覆盖全部验收范围 |
| `git commit` / `push` / `reset` / `stash` | 未执行 | 按指令保持工作区未提交 |

## 8. r1 返修记录（Review B1 / m1，2026-10-22）

### 8.1 输入与结论

- Review 报告：[review-b1.md](review-b1.md)，结论 `changes_requested`（审查对象 commit `7d19164`）。
- 本 agent 负责返修的 finding：**B1（blocker，AC2/D06 §82）** 与 **m1（minor，AC3 防御性契约）**。
- 明确不在本 agent 修复范围（需 Lead/设计裁决，见 §8.5）：M1（`plan` 结果只校验不改变设备的产品语义）、M2（交付 commit 的 canonical evidence/pin/Handoff 治理）、M3（B-2 WIP 并行与工作区隔离）、m2（Task 元数据/Review 文件名）。

### 8.2 B1 返修内容

根因：`_invoke_provider` 从 `registry.resolve()` 返回的 **provider 实例** `getattr` 读取 `requires_gpu` / `supports_cpu_fallback`，而真实 provider（`MangaOcrProvider`、`PaddleKoreanOcrProvider` 等）不在实例上重复这些声明，声明只在注册时给出的 `ProviderDescriptor` 上。后果：所有真实 heavy_runner provider 永远收到 `supports_cpu_fallback=False`，用户的 `allow_cpu_fallback` 对生产路径无效（假控件），D06 §82 的 CPU 回退不可达。

修复（按 Lead 返修指令）：

1. `src/infrastructure/providers/registry.py`：新增公开只读 `descriptor(provider_id, *, capability=None) -> ProviderDescriptor | None`。给出 `capability` 时复用 `resolve()` 相同的 binding-alias 翻译（Run 快照里的用户 profile id → 固定 registry slot）；未知 id 返回 `None` 而不是抛错；`resolve()` / readiness / 实例缓存语义不变。
2. `src/infrastructure/providers/handlers.py` `_invoke_provider`：按 `provider_id + capability` 取 descriptor，用其 `requires_gpu` / `supports_cpu_fallback` 传给 `heavy_runner`；descriptor 不可用（registry 无法回答的替身）时才回退 provider 实例属性。`preferred_device` / `allow_cpu_fallback` 的读取与 `auto` 路径不变（`auto` 仍 `preferred_device=None` 直通旧 `run_guarded(requires_gpu, call)`）。
3. 测试改造（不再用"手工塞实例属性"证明回退）：
   - `tests/providers/test_handlers_b1_settings.py` 的 provider 替身**不带任何能力属性**，`requires_gpu`/`supports_cpu_fallback` 一律声明在 `ProviderDescriptor` 上；
   - 新增真实设备链回归（`_invoke_provider` → `ProviderRuntime.heavy_runner` → **真实 `DeviceManager`**，`gpu_state(available=False)`）：
     - descriptor `supports_cpu_fallback=True`、实例无该属性、`gpu` 偏好 + `allow_cpu_fallback=True` + GPU 不可用 → **回退 CPU 实际执行，call 被调用一次**；
     - 同一 descriptor 但 `allow_cpu_fallback=False` → typed `DeviceUnavailable` 且 call **未执行**；
     - descriptor `supports_cpu_fallback=False` 且用户 `True` → 仍 `DeviceUnavailable`（相与语义，用户开关不能放大 Provider 能力）；
     - `auto`（无 `model_gpu` 节）+ descriptor 声明 GPU 要求 → 仍走旧未计划路径，实际执行（零行为变化非回归）；
   - OCR handler 端到端：`FakeOcrProvider`（无 `supports_cpu_fallback` 属性）+ descriptor 声明 `True` → 断言送达 `heavy_runner` 的 `supports_cpu_fallback=True` 且 `requires_gpu=False`；
   - descriptor 与实例属性冲突时 descriptor 胜出；registry 无 descriptor 时实例属性作为后备；
   - `tests/providers/test_registry_readiness.py` 追加 2 tests：`descriptor()` 静态声明/未知 id、binding alias 按 capability 翻译。

### 8.3 m1 返修内容

- `ProductionHandlers._section` 增加 guard：`settings` 非 `Mapping`（含 `None`）→ 返回空节（`{}`），与 `_retry_policy_for_run` 文档承诺一致；正常 `PipelineRun` 路径（`freeze_snapshot` 把 `None` 规范成 `{}`）行为不变。
- 新增测试：`settings_snapshot` 为 `None` / 字符串 / 列表 / 数字时 `_retry_policy_for_run` 返回装配期 policy 同一对象（4 个参数化用例）。

### 8.4 返修后原始测试结果

验收主命令（Lead 指定）：

```text
PS> python -m pytest tests/core tests/providers --ignore=tests/providers/test_detection_manga_real.py -q
1251 passed, 3 skipped, 1 warning in 48.87s
[exit code 0]
```

原始输出：`core-pytest-r1-acceptance-raw.txt`。说明：当前工作区还包含 B-2 WIP 的未跟踪测试 `tests/core/test_core_cleanup_wire.py`（28 tests，非本 Task 范围，未改动）；B-1 自身的 r1 后子集为 **140 passed / 1 skipped**（下条），相较 r1 前 1212 passed 净增 39（B-1 新增 11 + B-2 WIP 28）。

目标子集（B-1 Core 文件 + registry descriptor 新用例）：

```text
PS> python -m pytest tests/core/test_settings_b1_sections.py \
      tests/providers/test_handlers_b1_settings.py tests/providers/test_devices.py \
      tests/providers/test_registry_readiness.py -q
140 passed, 1 skipped in 1.80s
[exit code 0]
```

原始输出：`core-pytest-r1-targeted-raw.txt`。分文件：settings 校验 60、handlers/runtime 47（r1 前 38）、devices 21、registry readiness 12 + 1 既有 skip（其中新增 `descriptor()` 用例 2 条）。

不含 ignore 的整目录结果（确认只剩既有环境失败）：

```text
PS> python -m pytest tests/core tests/providers -q
2 failed, 1251 passed, 3 skipped, 1 warning in 64.27s (0:01:04)
FAILED tests/providers/test_detection_manga_real.py::test_real_detection_returns_block_candidates
FAILED tests/providers/test_detection_manga_real.py::test_real_blank_page_yields_zero_candidates
[exit code 1]
```

原始输出：`core-pytest-r1-core-providers-raw.txt`（2 个失败仍为 §5.2 的环境版本问题：`transformers 4.48.3` 无 `RTDetrV2ForObjectDetection`）。

全量回归：

```text
PS> python -m pytest tests -q
3 failed, 2583 passed, 9 skipped, 2 warnings in 188.11s (0:03:08)
FAILED tests/providers/test_detection_manga_real.py::test_real_detection_returns_block_candidates
FAILED tests/providers/test_detection_manga_real.py::test_real_blank_page_yields_zero_candidates
FAILED tests/workbench/test_workbench_viewmodel.py::test_pause_shows_optimistic_feedback_immediately
[exit code 1]
```

原始输出：`core-pytest-r1-full-suite-raw.txt`。3 个失败与 §5.4 完全相同（2 个环境 + 1 个既有 PySide6 基线），无新增失败。

### 8.5 返修遗留 / 交给 Lead 的观察

| 项 | 状态 | 说明 |
|---|---|---|
| M1（`run_guarded` 丢弃 `DevicePlan`，显式偏好只校验不改变 provider 设备） | 待 Lead 裁决 | 本次未改：设计 §4.1 的消费点写的是"经 `DeviceManager.plan` 校验"，实现与原 AC 字面一致；按"最小且保守"原则不擅自把 plan 结果传进 provider（需新增设备传递装配点，超出本 Task AC）。若判定"只校验"，建议同步 UI"仅 CPU/优先 GPU"文案与设计说明并固化断言；若判定"真正强制设备"，另立 Task。 |
| M2/M3/m2（治理/工作区/元数据） | Lead/流程侧 | 非本 agent 范围：canonical evidence/pin/Handoff、B-2 WIP 隔离与 Task Review 文件名由 Lead 统一处理；本报告未触碰 `doc/**`、未 commit。 |
| 观察：远程 translate provider 的 descriptor 未声明 `supports_cpu_fallback` | 记录，未改 | `runtime.build_provider_registry` 中远程 OpenAI/Sakura descriptor 使用默认 `supports_cpu_fallback=False`；用户**显式**选择 `gpu` 且本机无 GPU 时，translate 会按 D06 §82 判为"无回退"并抛 `DeviceUnavailable`（`auto` 不受影响）。本地 OCR descriptor 已声明 `True`，Review B1 关注的回退场景可达。是否给远程 Provider 声明 CPU 回退属 Provider 声明面改动，需 Lead/设计裁决，本次未擅自修改。 |
| 真实 GPU 端到端 | NOT_RUN | 环境无 GPU/torch；用 `tests/providers/env_sim.py::gpu_state` 模拟 + 真实 `DeviceManager` 覆盖分支，真实 CUDA 验证留待集成环境。 |
| GUI 烟测 | NOT_RUN | 由 Lead/集成阶段执行（同 §6）。 |

## 9. 合规声明

- 仅修改/新增上表 §2 所列文件；未改 `apps/desktop/frontend/**`、`doc/**`、Schema/migration、依赖、缓存/回收站/备份/Plugin 代码。
- 未删除既有测试文件或降低断言强度；对既有测试的唯一改动是 §4.6 的根因适配（pass-through 列表 + 更强的拒绝断言）。
- 未使用 `skip` / `xfail` / `only` 等绕过手段；未 commit/push/reset/stash。
