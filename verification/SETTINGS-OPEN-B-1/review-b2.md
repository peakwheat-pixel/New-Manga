# SETTINGS-OPEN-B-1 独立 Review r2（返修复审）

- 审查者：`reviewer-settings-a`（独立 Review，非实现者）
- 审查对象：HEAD **`81f822127f6c98a16b5456bf0595ef29bdd437f8`**（B-1 返修链）
  - `3ec334f77`：B1 descriptor 修复 + m1 guard + M1 设计/UI 同步 + 回归测试
  - `2fdcd5db4` / `e9c3b5f0e`：B-1 r1 证据恢复（acceptance raw 曾被截断为 0 字节）
  - `81f822127`：Task pins/Canonical Evidence/Handoff/STATUS/REBASELINE 收口 + 登记 B-2
  - base `da3b781d8971dcc36bd7bfd1165fa1a2f4519ea5`（与 Task 一致）
- 审查方式：读完整修复链；独立探针（真实 `ProviderRegistry.descriptor()`/alias、`_invoke_provider`、`ProviderRuntime.heavy_runner`、真实 `DeviceManager` + `env_sim`、`_retry_policy_for_run`）；因为 B-2 WIP 仍在工作区，用 **clean `git worktree` at 81f8221** 做验证与 `check.ps1`（临时 worktree/archive 审查后已清理）。
- 结论：**changes_requested**。B1/m1/M1 已闭环；但 canonical acceptance 证据与 clean commit 不可复现（含 B-2 WIP 28 个测试），并发现一个显式 `gpu` 偏好波及非 GPU 远程 provider 的边界问题；另有 pins/元数据自洽性小问题。

## 1. 结论与 AC 状态

| AC | 状态 | 说明 |
|---|---|---|
| AC1 Core 写入校验 | PASS | 与 r1 相同；60 个 settings tests 全绿，未回归 |
| AC2 模型/GPU 消费点 | **PASS（B1 已修）**，但新增边界 major（M3） | descriptor 来源、真实回退、`auto` 不 plan、OOM 隔离均成立；显式 `gpu` 对非 GPU 远程 provider 的行为未定义/未测试 |
| AC3 任务/并发消费点 | PASS | 同对象/夹取/`retry_codes`/`retry_after_provider` 保持；m1 guard 已补 |
| AC4 前端两面板 | PASS | clean `npm` 39 files/387 tests、tsc exit 0；M1 文案/标签与设计一致 |
| AC5 测试与证据 | **FAIL（证据语义）** | 结构 pins/`check.ps1` clean PASS，但 canonical raw 计数来自含 B-2 WIP 的 dirty 工作区，clean commit 无法复现；Task/Handoff/报告计数互相矛盾 |

**不建议按当前证据集关闭 B-1**；代码修复本身（B1/m1/M1）可接受，主要剩余项是证据/产品边界。

## 2. Findings

### B1（原 blocker，已闭环）— descriptor 来源修复成立

- `ProviderRegistry.descriptor(provider_id, *, capability=None)`（`src/infrastructure/providers/registry.py:141-162`）：
  - 按 capability 复用 `binding_aliases` 翻译（`:158`），与 `resolve()` 一致；
  - 未知 id 返回 `None`，`resolve()` fail-closed 语义不变；
  - `handlers._invoke_provider` 用 descriptor 的 `requires_gpu`/`supports_cpu_fallback`（`handlers.py:944-976`），descriptor 缺失时才回退实例属性（`:961-976`）。
- 独立探针（真实 registry + handler，provider 实例无任何能力属性）：
  ```text
  alias descriptor forwarded: requires_gpu=False, supports_cpu_fallback=True
  real DeviceManager (gpu unavailable):
    descriptor requires_gpu=True/supports=True + gpu 偏好 + allow=True  -> executed, call 1 次
    descriptor requires_gpu=True/supports=True + gpu 偏好 + allow=False -> DeviceUnavailable, call 0 次
    local OCR descriptor requires_gpu=False/supports=True + gpu + allow=True -> executed
    remote translate descriptor requires_gpu=False/supports=False + gpu + allow=True -> DeviceUnavailable（见 M3）
  ```
- 新增测试（clean snapshot 141 passed / 1 skipped 的 B-1 子集）确认真实数据源：
  - `_Provider` 不再带 `requires_gpu/supports_cpu_fallback` 实例属性，flags 只声明在 `ProviderDescriptor`（`tests/providers/test_handlers_b1_settings.py:102-135`）；
  - `test_descriptor_flags_win_over_conflicting_instance_attributes`、`test_instance_attributes_are_the_fallback_without_a_descriptor`；
  - `test_descriptor_cpu_fallback_is_reachable_on_the_real_device_chain` 使用真实 `DeviceManager` + `gpu_state(available=False)`；
  - OCR 端到端 `FakeOcrProvider`（无实例属性）+ descriptor `supports_cpu_fallback=True`，真实 fallback 执行；
  - `tests/providers/test_registry_readiness.py` 新增 descriptor/alias 2 条测试。
- **不再存在 r1 的 false green**：测试只靠 descriptor 声明即可通过；实例属性仅作为 registry 无法回答时的后备，且测试固定。

### m1（原 minor，已闭环）— 非 Mapping snapshot guard

- `_section` 增加 `isinstance(settings, Mapping)` guard（`handlers.py:1073-1080`），非 Mapping/`None` → `{}`。
- 4 个参数化测试 `test_non_mapping_snapshot_is_an_absent_tasks_section`（`None`/字符串/列表/数字）均返回装配期 policy 同一对象。
- 独立探针 `SimpleNamespace(settings_snapshot=None)` → `is base == True`，不再 `AttributeError`。

### M1（原 major，已裁决且文档/UI 一致）— 设备偏好是校验/回退策略，不强制 Provider 内部设备

- 设计 §4.1（`doc/design/SETTINGS_SECTION_SCHEMAS.md:105-106`）已明确：
  - `auto` 历史行为；
  - `cpu` = 跳过 GPU 校验直接执行；
  - `gpu` = 校验 GPU 可用性，不可用时按回退策略执行或拒绝；
  - **不强制 Provider 内部设备实现**（provider API 无 device 参数）。
- 前端标签/说明同步（`sections.ts:545-554`、`ModelGpuSettingsPanel.tsx:100`），并且 `ModelGpuSettingsPanel.test.tsx:76-145` 断言新文案（含"GPU 不可用时按回退策略"、"不强制 Provider 内部设备实现"）。
- `run_guarded` 的代码未改成"强制设备"，与上述裁决一致；此前 M1 风险已从"未说明"变为"显式冻结语义"。**无剩余代码 finding**。

### M2（major，证据/AC5）— canonical acceptance raw 与 clean commit 不可复现（含 B-2 WIP 28 个测试）

- 在 clean `git worktree` at `81f8221`（无 B-2 WIP）上：
  - `python -m pytest tests/core tests/providers -q --ignore=tests/providers/test_detection_manga_real.py` → **1224 passed / 3 skipped**；
  - `python -m pytest tests -q` → **2556 passed / 3 failed / 9 skipped**（3 个既有失败）；
  - B-1 靶向（settings+handlers+devices+registry）→ **141 passed / 1 skipped**；
  - `check.ps1` → **PASS**（2 warnings，clean worktree）。
- 但 canonical evidence 的 raw 文件与报告文字不一致，且包含工作区 B-2 WIP：
  - `verification/SETTINGS-OPEN-B-1/core-pytest-r1-acceptance-raw.txt` → **1252 passed / 3 skipped**；
  - `core-pytest-r1-full-suite-raw.txt` → **2584 passed / 3 failed**；
  - dirty 工作区当前同命令 → **1252 passed / 3 skipped**（B-2 WIP `tests/core/test_core_cleanup_wire.py` 收集 **28** tests）；
  - 1224 + 28 = 1252；2556 + 28 = 2584，差异完全由 B-2 WIP 测试解释。
- 因此 canonical raw 不是从 B-1 commit 树生成的（Lead 消息中的"1251"也与 raw 的 1252 不一致）；`Task` 的测试表/运行记录仍是 r1 的 **1212 / 2544**（`doc/tasks/SETTINGS-OPEN-B-1.md:69,72,85`），Handoff 写 **1251 / 1212**（`doc/handoffs/SETTINGS-OPEN-B-1-7d19164.md:26-27,49`），core-report 同段有 **1252 / 1251 / 141 / 140** 混用（`core-report.md:202,206,214,224`），`core-pytest-r1-core-providers-raw.txt` 与 raw 计数也不一致。
- `Task` 结构 pins 与 canonical 表在 clean worktree 上 `check.ps1` PASS（commit `e9c3b5f` 存在、16 文件 hash 校验通过），所以这是 **证据内容/计数可复现性**问题，不是"pins 路径不存在"问题。
- 建议：用 clean commit（81f8221）重录 B-1 acceptance raw（1224/3），把 B-2 WIP 的 28 个测试明确排除或单独记录；同步 Task 测试表、Handoff、core-report、ui-report 的计数；`canonical_evidence_status: pending`（Task `:17`/`:117`）在关闭时更新为 pinned/complete。

### M3（major，AC2 边界）— 显式 `gpu` 偏好会波及不需要 GPU 的远程 Provider，可能导致 translate/vision OCR 失败

- 当前 `model_gpu` 是 Run 级全局偏好，`_invoke_provider` 对所有经 `heavy_runner` 的步骤生效（OCR/translate；`handlers.py:944-976`）。
- 远程 provider 的 descriptor（OpenAI/Sakura translation、Vision OCR，`runtime.build_provider_registry`）默认 `requires_gpu=False, supports_cpu_fallback=False`；当用户选 `device_preference=gpu`、本机无 GPU、`allow_cpu_fallback=true` 时：
  ```text
  remote translate descriptor (requires_gpu=False, supports=False)
    + gpu 偏好 + allow_cpu_fallback=True + GPU 不可用
    -> DeviceUnavailable（call 未执行）
  ```
  本地 OCR descriptor（supports=True）已能回退并执行；但同一个 Run 的远程翻译/视觉 OCR 会直接失败，虽然它们不需要 GPU。
- 该行为不是 B1 的 false-green，而是 B1 修复后真实暴露的边界；core-report §8.5 已把它列为"待 Lead/设计裁决"的观察，但当前无测试、无 UI 提示，且 `device_preference=gpu` 是全局设置。
- 需裁决：显式 gpu 是否只应作用于声明需要 GPU 的 provider（跳过非 GPU provider 的 `plan`），或为远程 provider 声明可回退/忽略偏好，或在 UI/设计中明确"gpu 偏好会使无 fallback 的 provider 失败"。在裁决前建议至少补一条"远程 descriptor + gpu + 无 GPU"的行为测试，把边界冻结。

### m1（minor，pins/元数据）— delivery/integration pin 的语义与最终收口 commit 不一致

- `Task`（81f8221）：`delivery_head: 3ec334f`（修复代码 commit）、`integration_commit: e9c3b5f`（证据恢复 commit）；Handoff 头同样 `delivery_head: 3ec334f`；但最终收口 commit 是 `81f8221`，且 Task 运行记录仍写"交付 commit `7d19164`"（`:84`）、Lead 验证仍是 1212（`:85`）。
- `REBASELINE_PLAN.md:27` 仍写"实现 7d19164；独立 Review 进行中"，未反映 3ec334f/81f8221；`STATUS.md:7` 已写修复 `3ec334f`。
- 如果 `integration_commit` 的定义是"证据/收口 commit"，`e9c3b5f`（只恢复 core raw）不是最终 81f8221；如果定义是"代码交付"，则不应指向证据 commit。请统一 Task/Handoff/Plan/Status 的 pin 语义，并把最终收口 commit（或 r1+r2 链）写清楚；这是关闭前的元数据一致性要求，不是代码问题。

### m2（nit，计数/文案）— 多处 off-by-one 与旧计数

- raw acceptance **1252** vs Lead/Handoff/core-report 文本 **1251**；clean 为 **1224**；full raw **2584** vs 文本 **2583** vs clean **2556**；targeted **141/1 skipped** vs core-report 文本 **140/1**。
- `core-report` §8.4 的"新增 12 + B-2 28 = 净增 40"与 1212→1252 不符（1212+40=1252，但 clean B-1 自身 1224，说明 12 里含 B-1 新增 12；clean 1224 = 1212+12，正确；文本 1251 是笔误）。建议统一重算并更新。

### 说明（已复核，无 finding）
- AC1/AC3 代码与测试未回归；AC4 两面板真实、无假并发控件；M1 的 UI/设计一致；B1/m1 独立 probe 与 clean 测试均通过。
- `check.ps1` clean worktree **PASS**（2 warnings：3 个非终态 Task、STATUS 约 80% 预算）；结构 pins 自洽。
- `tests/providers/test_registry_readiness.py` 的 descriptor/alias 测试通过；`ProviderRegistry.descriptor()` 未改变 `resolve()`/readiness 语义。
- `heavy_runner` 旧替身若不接受新增 3 个关键字会 TypeError；仓库内唯一生产实现为 `ProviderRuntime.heavy_runner`，现有测试替身已适配；属可选兼容性 nit。

## 3. 独立测试原始结果

### 3.1 clean commit（`git worktree` at `81f8221`，无 B-2 WIP）

| 命令 | 结果 | exit |
|---|---|---|
| `python -m pytest tests/core tests/providers -q --ignore=tests/providers/test_detection_manga_real.py` | **1224 passed, 3 skipped, 1 warning in 50.49s** | 0 |
| `python -m pytest tests/core/test_settings_b1_sections.py tests/providers/test_handlers_b1_settings.py tests/providers/test_devices.py tests/providers/test_registry_readiness.py -q` | **141 passed, 1 skipped in 3.33s** | 0 |
| `python -m pytest tests -q` | **3 failed, 2556 passed, 9 skipped, 2 warnings in 177.35s**；3 failed = 2×`test_detection_manga_real`（环境）+ 1×`test_workbench_viewmodel`（既有基线），与 core-report 记录同类 | 1（既有失败） |
| `npm --prefix apps/desktop/frontend test` | **39 files / 387 tests passed** | 0 |
| `tsc --noEmit` | 无输出 | 0 |
| `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS (2 warnings)** | 0 |

### 3.2 dirty 工作区（说明污染，不作为 B-1 验收）

| 命令 | 结果 |
|---|---|
| `pytest tests/core tests/providers --ignore=...`（含未跟踪 B-2 `test_core_cleanup_wire.py`） | **1252 passed / 3 skipped** |
| `pytest tests/core/test_core_cleanup_wire.py --collect-only -q` | **28 tests collected** |
| 差异 | clean 1224 + 28 = dirty 1252；clean full 2556 + 28 = dirty 2584 |

### 3.3 关键独立探针

```text
# B1 descriptor + alias through real handler
alias descriptor forwarded: requires_gpu=False, supports_cpu_fallback=True

# B1 real DeviceManager fallback/refusal (gpu unavailable)
local OCR descriptor requires_gpu=False/supports=True + gpu + allow=True -> executed (call 1)
descriptor requires_gpu=True/supports=True + gpu + allow=False -> DeviceUnavailable (call 0)
remote translate descriptor requires_gpu=False/supports=False + gpu + allow=True -> DeviceUnavailable (M3)

# m1
_retry_policy_for_run(SimpleNamespace(settings_snapshot=None)) is base -> True
```

## 4. 证据/范围核对

- 修复链范围（`git show --stat`）：
  - `3ec334f`：`registry.py` 新增 descriptor、`handlers.py` descriptor 来源 + `_section` guard、B-1 测试 + 设计/UI 文案 + core-report/review-b1；
  - `2fdcd5d`/`e9c3b5f`：证据 raw 修复（acceptance raw 从 0 字节恢复）；
  - `81f8221`：Task 16 条 canonical evidence + pins、Handoff、STATUS/REBASELINE、登记 B-2。
- **clean `check.ps1` PASS**，Task canonical 表 16 文件在 commit `e9c3b5f` 存在且 hash 校验通过；但 canonical acceptance raw 是 dirty 工作区生成（含 B-2 WIP 28 tests），与 clean commit 的 1224/2556 不一致（M2）。
- `doc/REBASELINE_PLAN.md:27` 仍写实现 `7d19164`/Review 进行中；`Task` 运行记录 `:84` 仍写交付 `7d19164`；建议随收口更新。
- `B-2` 已登记为独立 Task（`SETTINGS-OPEN-B-2`），B-2 WIP 未进入 B-1 交付 commit；但 B-2 WIP 测试仍被 B-1 canonical raw 计入，需在证据层隔离。

## 5. 亲自验证 / NOT_RUN

**已亲自验证**
- B1：descriptor 方法/alias、handlers 数据源、真实 DeviceManager 回退/拒绝、OCR 端到端 fallback、测试替身无实例属性；clean tests 全绿。
- m1：guard + 4 参数化测试 + `None` probe。
- M1：设计 §4.1 文案、UI 标签/说明、panel tests 与 manager 行为一致；无强制设备实现。
- 证据：clean worktree 的 pytest/npm/tsc/check、raw 计数与 dirty 工作区差异、B-2 WIP 28 tests；Task pins/Canonical table/check.ps1。
- 范围：修复链文件、allowed_paths、B-2 登记与 WIP 隔离情况。

**NOT_RUN / 未独立验证**
- GUI 烟测（模型/GPU、任务/并发保存 + 重启）：仍 NOT_RUN，需真实 Tauri + Core。
- 真实 GPU 端到端：无 GPU/torch，仍只有 `env_sim` 模拟证据。
- B-2（缓存清理操作面）：按 Lead 要求本轮不审；其 WIP 不作为 B-1 结论依据。
- `tests/infrastructure` 路径：任务文本笔误（不存在），沿用 core-report/Lead 的替代覆盖说明。

## 6. 给 Lead 的关键结论

1. **B1/m1/M1 已闭环，可以认可**：descriptor 来源、真实 DeviceManager 回退、无 false green、m1 guard、M1 文档/UI 一致均已独立验证。
2. **需先修证据语义（M2）**：canonical acceptance raw 1252 是 dirty 工作区（B-2 WIP 28 tests）结果；clean 81f8221 的真实 acceptance 是 **1224 passed / 3 skipped**，full 是 **2556 passed / 3 failed**。请用 clean commit 重录 raw，或把 B-2 WIP 28 项明确排除并同步 Task/Handoff/core-report/ui-report 的计数；`canonical_evidence_status: pending` 与 AC5 勾选/closeout 记录也要在关闭时一致。
3. **需裁决 M3（AC2 边界，major）**：显式 `gpu` 偏好会让无 GPU 机器上的远程 translation/Vision OCR（descriptor 无 CPU fallback）以 `DeviceUnavailable` 失败，尽管它们不需要 GPU；当前无测试/UI 提示。请决定是否只对需要 GPU 的 provider 应用偏好、为远程 provider 声明忽略/回退，或在 UI/设计中明确警告；至少补一条边界测试。
4. **元数据小修（m1/m2）**：Task 的 `integration_commit=e9c3b5f`/`delivery_head=3ec334f`/运行记录 `7d19164`、REBASELINE 的 `7d19164`/Review 进行中、Handoff 的 1251/1212 与 raw 1252/clean 1224 需统一；Review 文件名 `review-b1.md` 已在 Task/Handoff 正确引用（本报告为 `review-b2.md`）。

**结论：changes_requested**（代码修复本身无 blocker；证据可复现性与 M3 边界需处理后再关闭）。

## 7. 快照

- HEAD `81f822127f6c98a16b5456bf0595ef29bdd437f8`；base `da3b781d8971dcc36bd7bfd1165fa1a2f4519ea5`。
- 验证用 clean `git worktree`（detached 81f8221）与 `git archive` 临时快照；审查后已清理，原工作区/`node_modules` 未改动。
- 工作区仍有 B-2 WIP（Tauri/Core/frontend 测试与 `SETTINGS-OPEN-B-2.md` 等未提交文件），未进入 B-1 交付 commit；B-2 本轮不审。
