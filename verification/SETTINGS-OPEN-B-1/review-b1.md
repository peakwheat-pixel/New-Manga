# SETTINGS-OPEN-B-1 独立 Review（批次 B-1：模型/GPU + 任务/并发）

- 审查者：`reviewer-settings-a`（独立 Review，非实现者；批次 A 的同一 reviewer）
- 审查对象：**commit `7d19164f838607e68e2b6970bbbd57bee7bd5777`**（`feat(settings): open model/GPU and tasks settings (batch B-1)`）
  - parent：`da3b781d8971dcc36bd7bfd1165fa1a2f4519ea5`（与 Task `base_commit` 一致）
  - 分支 `main`；审查时 HEAD 即该 commit
- 审查方式：`git show 7d19164` 读全部 36 个文件；独立探针（真实 `ProductionHandlers._invoke_provider`、`ProviderRegistry`/`ProviderDescriptor`、`DeviceManager`、`_retry_policy_for_run`）；在 **clean commit 快照**（`git archive 7d19164` 到 `G:\CODEX\New Manga.workspace\review-b1-7d19164`）重跑 pytest/npm/tsc/全量回归；当前工作区因 Lead 并行开发 B-2 而 **不干净**，见 §1/§5。
- 说明：Task 文本写"结论落 `review-r1.md`"，Lead 指令要求 `review-b1.md`；本报告按 Lead 指令落在 `verification/SETTINGS-OPEN-B-1/review-b1.md`，Task 元数据应同步修正。

## 1. 结论

**changes_requested**（不能按当前 commit 直接进入集成/关闭）。

理由：AC1、AC3、AC4 的实现与测试基本成立，独立测试也全绿；但 AC2 的 **Provider 声明来源与设计 §4.1 不一致**（`supports_cpu_fallback`/`requires_gpu` 从 provider 实例读取，而真实 provider 未声明这些属性，导致 `allow_cpu_fallback` 对真实 provider 完全无效、D06 §82 的 CPU 回退不成立），这是 blocker；另有显式偏好只校验不生效的语义缺口、交付 commit 自身 `check.ps1` 失败（canonical evidence 仍为 pending）、以及工作区被未提交的 B-2 工作污染/与"工作区干净"不符。详见 §2。

## 2. Findings

### B1（blocker，AC2/D06 §82）— `supports_cpu_fallback` 读 provider 实例而非 Provider descriptor，真实 provider 的回退开关完全失效

- **设计**：`doc/design/SETTINGS_SECTION_SCHEMAS.md:106` 明确"`allow_cpu_fallback` 与 **Provider descriptor** 的 `supports_cpu_fallback` 相与：只有 Provider 声明支持且用户允许时才回退 CPU（D06 §82 语义不变）"。
- **实现**：`src/infrastructure/providers/handlers.py:955-961`：
  - `requires_gpu=bool(getattr(provider, "requires_gpu", False))`
  - `supports_cpu_fallback=bool(getattr(provider, "supports_cpu_fallback", False))`
  读取的是 `registry.resolve()` 返回的 **provider 实例**，不是 `ProviderDescriptor`。
- **真实 provider 没有这个实例属性**：
  - `src/infrastructure/providers/registry.py:47-55` 的 `ProviderDescriptor` 才声明 `requires_gpu/supports_cpu_fallback`；
  - `registry.resolve()`（`registry.py:239-270`）返回 `registration.factory()` 的实例，不会把 descriptor 字段复制到实例；
  - `src/infrastructure/providers/ocr_local.py:87`（`MangaOcrProvider`）、`:170`（`PaddleKoreanOcrProvider`）均未定义这两个属性；而 `src/infrastructure/providers/runtime.py:560-583` 为它们注册的 descriptor 是 `requires_gpu=False, supports_cpu_fallback=True`。`MangaOcrProvider()`/`PaddleKoreanOcrProvider()` 实测 `hasattr(..., "supports_cpu_fallback") == False`。
- **独立探针**（真实 `_invoke_provider` + `ProviderRegistry` + 无实例属性的 provider）：
  ```text
  descriptor: {'requires_gpu': True, 'supports_cpu_fallback': True} | provider attrs: {}
    -> forwarded: {'requires_gpu': False, 'preferred_device': 'gpu',
                   'allow_cpu_fallback': True, 'supports_cpu_fallback': False}
  descriptor: {'requires_gpu': False, 'supports_cpu_fallback': True} | provider attrs: {}
    -> forwarded: supports_cpu_fallback=False
  ```
  descriptor 声明 `True` 时 handler 仍传 `False`；只有给实例手工塞属性（测试里的 `_Provider`）才会传 `True`。
- **用户可见后果**：用户选择 `gpu` 偏好、允许 CPU 回退（默认 true）、但本机无 GPU 时，Manga OCR / Paddle Korean 本应按 descriptor `supports_cpu_fallback=True` 回退 CPU；实际 `DeviceManager.plan` 收到 `supports=False`，直接抛 `DeviceUnavailable`，OCRE 步骤失败。同时 `allow_cpu_fallback` 开关对所有真实 heavy_runner provider 都没有效果（属于设计 §2.4 不允许的"假控件"）；`requires_gpu` 对将来 descriptor 为 True 的 provider 也会被读成 False，heavy gate 被绕过。实现报告已自认这一点（`core-report.md:54`、`:71`），但按设计应读 descriptor，不能以"更保守"代替 D06 §82 语义。
- **测试为何没发现**：`tests/providers/test_handlers_b1_settings.py:97-113` 的 `_Provider` 手工设置 `requires_gpu/supports_cpu_fallback`，而 `_registry()` 的 descriptor 没有设置这两个字段；测试验证的是 handler 的 `getattr`，不是生产数据源。`test_handle_ocr_forwards_the_run_snapshot_preference_end_to_end` 只断言 `preferred_device`，未断言 `supports_cpu_fallback`。属于 false green。
- **建议**：在 `_invoke_provider` 中按 `provider_id` 取 registry descriptor（可给 `ProviderRegistry` 增加公开 `descriptor(provider_id)`，或用 `descriptors_for(capability)` 匹配 id），用 descriptor 的 `requires_gpu`/`supports_cpu_fallback`（对无 descriptor 的测试替身保留 getattr 回退）；补一条"descriptor 声明 True、provider 实例无属性"的回归测试，以及 OCR handler 端到端回退测试。`preferred_device`/`allow_cpu_fallback`/`supports_cpu_fallback` 三者的 D06 §82 组合需要在真实 registry 上成立。

### M1（major，AC2 语义）— 显式 `cpu`/`gpu` 偏好只做 `plan` 校验，plan 结果被丢弃，实际 provider 调用没被改变

- `src/infrastructure/devices/manager.py:284-292`：`run_guarded` 在 `preferred_device is not None` 时调用 `self.plan(...)`，但**不接收/使用返回的 `DevicePlan`**，随后照旧执行 `call`；`plan` 只在 GPU 不可用且不允许回退时抛 `DeviceUnavailable`。
- 独立探针：
  ```text
  manager.run_guarded(requires_gpu=True, preferred_device="cpu",
                      allow_cpu_fallback=False, supports_cpu_fallback=False,
                      call=...)
  => "executed"，call 执行；manager._gpu_info is None
  ```
  即 `cpu` 偏好只让 `plan` 直接返回 CPU，不探测 GPU、不改变调用；若 provider 本身需要/使用 GPU，CPU 偏好不会被强制。`gpu` 偏好同样只做可用性/回退校验，不向 provider 传递设备。
- 对当前 heavy_runner 真实 provider（OCR/translate 均为 CPU-only）`cpu` 与历史行为完全一致（属于 no-op）；UI 标签"仅 CPU (cpu)"/"优先 GPU (gpu)"（`sections.ts`）让用户以为会强制设备。设计 §4.1 的消费点写的是"经 `DeviceManager.plan` **校验**"，实现字面符合设计，因此这是**设计/产品语义缺口**而非实现私自加戏：请 Lead 明确是否接受"只校验、不改变实际设备"；若接受，应改 UI 文案/设计说明并明确记录；若不接受，需要把 plan 的 `device` 传给 provider 或增加设备选择装配点（超出当前 AC2 的最小实现）。
- 建议：至少让 `run_guarded` 使用 `plan` 的结果（或在设计 §4.1 冻结"仅校验"语义并由 UI 如实展示），并补一条明确断言"cpu 偏好不改变 provider 设备调用"或"cpu 偏好强制 CPU"的测试，避免当前空泛的"返回正常"。

### M2（major，AC5/治理）— 交付 commit 自身 `check.ps1` FAIL；canonical evidence/pin/handoff 未随 commit 固定

- 在 **clean commit 快照** 运行 `pwsh -NoProfile -File tools/governance/check.ps1`：
  ```text
  FAIL: Canonical evidence 路径缺失：pending
  Governance check: FAIL (1 errors, 3 warnings), exit 1
  ```
  原因：committed `doc/tasks/SETTINGS-OPEN-B-1.md` 的 Canonical Evidence 表仍是 `| pending | pending | ... |`（`doc/tasks/SETTINGS-OPEN-B-1.md:88-92` 附近），且 `delivery_head: null` / `integration_commit: null`（`:15-16`）。
- 当前工作区 `check.ps1` 为 **PASS**，但那是因为 Lead 在 commit 之后又**未提交**地补了 pins、canonical 表和 Handoff（`git status` 显示 `doc/tasks/SETTINGS-OPEN-B-1.md`、`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/TASK_LEDGER.md` 均 M，`doc/handoffs/SETTINGS-OPEN-B-1-7d19164.md` 未跟踪）。也就是说 Lead 消息中的"工作区干净/check PASS"只对当前未提交工作区成立，**不是交付 commit 的状态**。
- `canonical_evidence_status` 仍为 `pending`、`resource_closeout_status: pending`；AC5 未勾（`:53`）。Task 文件还把 Review 结论路径写成 `review-r1.md`（`:84`），与 Lead 要求的 `review-b1.md` 不一致。
- 影响：交付 commit 无自指 pin、无 Handoff、无 canonical evidence，`check.ps1` 不能通过；Codex/集成方拿 `7d19164` 无法按治理流程关闭。建议把 pins/canonical evidence/Handoff/Task 状态与 Review 路径一次性 commit（或 amend 到 B-1 交付提交），再重跑 `check.ps1`；关闭前 GUI 烟测仍需 NOT_RUN 明确记录。
- 备注：当前 dirty 工作区 check PASS 时仍报 `3 个非终态 Task` 与 `STATUS 80%` 预算 WARN；committed 树为 2 个非终态 Task——与 B-2 WIP 有关（见 M3）。

### M3（major，流程/环境）— 工作区被未提交的 B-2 实现污染；"工作区干净"不成立，B-1 的 npm 证据必须在 clean commit 上取

- 审查开始时 `git status`（相对 `7d19164`）已包含未提交的 B-2 工作：
  - `M apps/desktop/frontend/src/settings/SettingsPage.tsx`、`SettingsPage.test.tsx`、`client.ts`；
  - `?? CacheRevisionPanel.tsx`、`CacheRevisionPanel.test.tsx`、`client.cleanup.test.ts`；
  - `?? doc/tasks/SETTINGS-OPEN-B-2.md`（`status: in_progress`，`base_commit: 7d19164`），以及 `doc/REBASELINE_PLAN.md`/`STATUS`/`TASK_LEDGER` 的未提交更新。
- 直接在当前工作区跑 `npm --prefix apps/desktop/frontend test` 得到 **4 failed / 383 passed**，失败全在 `SettingsPage.test.tsx`（8 开/4 关矩阵、键盘导航、cache disabled、placeholder id），因为工作区代码已按 B-2 把 `cache_revision` 打开（实际 9 开/3 关）。在 clean commit 快照上同一命令是 **39 files / 387 tests passed**（见 §3）。这证明失败来自未提交 B-2 WIP，不是 B-1 commit 的缺陷；但也说明"当前工作区测试=交付 commit 测试"不成立。
- B-2 依赖 `depends_on: [SETTINGS-OPEN-B-1]`，而 B-1 尚未 done/Review 未完成，B-2 实现已开始；且 B-1 交付 commit 的 `doc/design/SETTINGS_SECTION_SCHEMAS.md:121-128` 已把 **B-2 的清理操作面**（`GetCleanupPreview`/`RunCleanup`/`RetryPendingCleanups`）从"拟议"改为"B-2 冻结的操作面"——这是 B-1 AC（§4.1–§4.2）之外的额外范围。
- 建议：Lead/Codex 明确 B-2 是否已授权并行；把 B-2 WIP 移到独立 worktree/分支，B-1 的验收与 Review 一律取 clean commit；B-1 交付 commit 中的 design §4.3 B-2 冻结要么由 B-2 Task/契约 owner 确认，要么移到 B-2 的任务/提交，避免 B-1 范围与证据混乱。

### m1（minor，AC3 防御性契约）— `_retry_policy_for_run` docstring 承诺非 Mapping snapshot 返回 base，但 `_section` 会崩

- `src/infrastructure/providers/handlers.py:1054-1056`：`_section` 直接 `settings.get(name)`，`settings` 为 `None`/非 Mapping 时 `AttributeError`；`_retry_policy_for_run` docstring（`:965-980`）却写"`run.settings_snapshot` 非 Mapping 或 tasks 节缺失/非 Mapping/空 → 返回 base"。
- 独立探针：`_retry_policy_for_run(SimpleNamespace(settings_snapshot=None))` 抛 `AttributeError: 'NoneType' object has no attribute 'get'`（不是返回 base）。
- 可达性：`PipelineRun.__post_init__` 用 `freeze_snapshot` 把 `None` 规范成 `{}`（`domain/tasks/models.py:395/416`），sqlite 载入默认 `{}`，正常构造不会传 `None`；但 handler 作为独立 seam 被测试/重放或未来调用方以 SimpleNamespace 调用时可能触发，且与自身文档承诺相反。建议在 `_section` 开头 `if not isinstance(settings, Mapping): return {}` 并补一条测试；不影响 AC3 主路径。

### m2（minor，Task/元数据）— Review 文件名、Handoff 与 pin 的书写不一致

- committed Task `doc/tasks/SETTINGS-OPEN-B-1.md:84` 写 Review 结论落 `review-r1.md`；Lead 要求 `review-b1.md`。
- Handoff `doc/handoffs/SETTINGS-OPEN-B-1-7d19164.md`（未跟踪）头 `delivery_head: 7d19164` 正确，但未入库；committed Task 仍 null（见 M2）。
- 建议关闭前统一：Task pins/Handoff/Review 文件名一处 commit；`canonical_evidence_status` 从 pending 改为 done/pinned。

### 说明（非 finding，已随机验证）
- `tests/core/test_core_service_settings.py:174/218-222` 的 pass-through 根因适配合理：`model_gpu` 从 pass-through 节列表移除，`model_gpu`/`tasks` 加入"路径 payload 在持久化前被拒绝"的更强断言，未删除/弱化原有断言。
- AC1 校验矩阵（含 bool/int 不互转、未知键、越界、未知 section 透传）与设计 §4.1–§4.2 逐键一致；探针结果见 §3。
- AC3 主路径（无 tasks 节返回同一对象、部分键、夹取、`retry_codes`/`retry_after_provider` 保留、两处 `run_chain` 均已替换）均成立；`grep -r "policy=self.deps.retry_policy" src` 在 clean commit 为 0 处，`run_chain(` 定义外仅 OCR/translate 两处。
- AC4 两面板真实（真实下拉/开关/数字输入、`settings_get`/`settings_update_section`、加载/错误/未设置/生效说明），`task_concurrency` 只有串行只读说明，无并发控件；committed `SettingsPage.tsx:55-67` 为 8 开/4 关，`DISABLED_SECTION_TEST_IDS` 恰为 cache_revision/recycle_bin/backup_restore/plugins；`client.ts:72-96` union 为 7 节（含 sfx）；clean npm 39/387、tsc 0。
- 契约：`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:262` 与 `doc/contracts/P15_SETTINGS_IPC_CONTRACT.md:272` 的 B-1 追加注记与实现/设计一致（两节冻结、其余仍未开放、wire 形状不变）。

## 3. 独立测试原始结果

### 3.1 clean commit 快照（`git archive 7d19164`，排除工作区 B-2 WIP）

| 命令 | 原始结果 | exit |
|---|---|---|
| `python -m pytest tests/core tests/providers -q --ignore=tests/providers/test_detection_manga_real.py` | `1212 passed, 3 skipped, 1 warning in 50.22s` | 0 |
| `python -m pytest tests/core/test_settings_b1_sections.py -q` | `60 passed in 1.81s` | 0 |
| `python -m pytest tests/providers/test_handlers_b1_settings.py tests/providers/test_devices.py -q` | `59 passed in 0.25s`（handlers 38 + devices 21，含新增 10） | 0 |
| `python -m pytest tests -q`（全量） | `3 failed, 2544 passed, 9 skipped, 2 warnings in 193.48s`；3 个失败为 `test_detection_manga_real.py`（2，transformers 环境）与 `test_workbench_viewmodel.py::test_pause_shows_optimistic_feedback_immediately`（1，既有 PySide6 基线），与 core-report §5.4 一致 | 1（已知基线失败） |
| `npm --prefix apps/desktop/frontend test` | `Test Files 39 passed (39)` / `Tests 387 passed (387)`，Duration ~3.4s | 0 |
| `cd apps/desktop/frontend && .\node_modules\.bin\tsc --noEmit` | 无输出 | 0 |
| `pwsh -NoProfile -File tools/governance/check.ps1`（clean 快照） | `FAIL: Canonical evidence 路径缺失：pending`（1 error / 3 warnings） | 1 |

### 3.2 当前 dirty 工作区（仅用于说明污染，不是 B-1 验收）

| 命令 | 结果 |
|---|---|
| `npm --prefix apps/desktop/frontend test`（dirty，含 B-2 WIP） | `39 files`，`4 failed / 383 passed`，失败均在 `SettingsPage.test.tsx`（B-2 已提前打开 cache_revision，实际 9 开/3 关） |
| `python -m pytest tests/core tests/providers ...`（dirty，Python 未受 B-2 前端影响） | `1212 passed / 3 skipped` |
| `check.ps1`（dirty，pins/canonical/handoff 未提交更新） | PASS（2 warnings；但 3 个非终态 Task，含未跟踪 B-2） |

### 3.3 独立探针（关键结论）

```text
# AC2 descriptor vs instance（真实 ProviderRegistry + ProductionHandlers._invoke_provider）
descriptor supports_cpu_fallback=True, provider 实例无属性
  -> forwarded supports_cpu_fallback=False          # B1
descriptor supports_cpu_fallback=True, provider 实例也设 True
  -> forwarded supports_cpu_fallback=True           # 测试替身路径，非生产

# AC2 cpu 偏好（真实 DeviceManager）
run_guarded(requires_gpu=True, preferred_device="cpu", allow_cpu_fallback=False,
            supports_cpu_fallback=False, call=...)
  => "executed"；calls=["called"]；_gpu_info=None    # plan 返回值被丢弃，M1

# AC3 同一对象/夹取/保留
{} / {"tasks":None} / {"tasks":{}} / {"tasks":{"retry_max_attempts":True}} -> base 同一对象 (is True)
{"tasks":{"retry_max_attempts":2}} -> attempts 2, backoff=base 1.0, 新对象
{"tasks":{"retry_max_attempts":99,"retry_backoff_seconds":0}} -> 3 / 0.1
{"tasks":{"retry_max_attempts":1,"retry_backoff_seconds":7.5}} -> 1 / 7.5, codes/after 保留
SimpleNamespace(settings_snapshot=None) -> AttributeError（m1）
```

## 4. 范围核对（commit `7d19164`，36 个文件）

| 分组 | 文件 | allowed_paths |
|---|---|---|
| Core（4） | `src/bootstrap/settings_sections.py`、`src/infrastructure/devices/manager.py`、`src/infrastructure/providers/runtime.py`、`src/infrastructure/providers/handlers.py` | 是 |
| 测试（4） | `tests/core/test_settings_b1_sections.py`、`tests/core/test_core_service_settings.py`、`tests/providers/test_handlers_b1_settings.py`、`tests/providers/test_devices.py` | 是 |
| 前端（10） | `apps/desktop/frontend/src/settings/**`（两个新面板 + 两个测试、SettingsPage/测试、client/测试、sections） | 是 |
| 文档/契约（7） | `doc/design/SETTINGS_SECTION_SCHEMAS.md`、`doc/contracts/M2-C1_...`、`doc/contracts/P15_...`、`doc/tasks/SETTINGS-OPEN-B-1.md`、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md` | 是 |
| 证据（11） | `verification/SETTINGS-OPEN-B-1/**` | 是 |

- 无 Schema/migration、无依赖变更、无 Provider/Network/凭据/SFX wire 语义修改；`settings_update_section` 形状/错误码未变（契约注记一致）。
- 额外范围：`doc/design/SETTINGS_SECTION_SCHEMAS.md:121-128` 把 B-2 的清理操作面改为"B-2 冻结的操作面"，超出 B-1 AC（§4.1–§4.2）；虽在 allowed_paths 内，建议由 B-2 任务/契约 owner 确认（M3）。
- 未提交的 B-2 文件不属于本 commit（在 M3 记录，不应混入 B-1 证据）。

## 5. 亲自验证 / NOT_RUN

**已亲自验证**
- 通读 36 文件 diff + 两个报告 + 任务/Handoff + 契约注记 + 证据 raw logs；`check.ps1` 在 clean commit 与 dirty 工作区分别运行。
- AC1：validator 探针覆盖 legal/illegal/unknown key/bool-int/越界/未知 section；60 tests 与 wire 测试读码；pass-through 根因适配合理。
- AC2：链路读码（assembly `heavy_runner=provider_runtime.heavy_runner` → runtime → manager）；`auto` no-plan 测试读码 + 独立 probe；**descriptor vs instance 独立 probe（B1）**；`gpu/cpu` 偏好 probe（M1）；OOM 隔离测试读码/全绿。
- AC3：独立 probe 覆盖无节同对象、部分键、夹取、非数字、`retry_codes`/`retry_after_provider`；两处 `run_chain` 替换 grep；`_section` None 崩溃 probe（m1）。
- AC4：两面板代码/测试/提交 payload/错误投影/未设置/只读说明读码；committed 分类矩阵 8/4、client union 7、`cache_revision` 仍关闭；clean npm 39/387 与 tsc 0。
- 证据：clean 快照 pytest/npm/全量/tsc 重跑；raw log 数字与 core-report/ui-report 一致；B-1 Task canonical evidence 当前表/Handoff 为未提交状态；clean commit `check.ps1` FAIL（M2）。
- 范围：36 文件逐一映射 allowed_paths；无 Schema/依赖/其他分区实现。

**NOT_RUN / 未独立验证**
- GUI 烟测（模型/GPU、任务/并发保存 + 重启复查）：Lead/任务声明 NOT_RUN，需真实 Tauri + Core；我未做。
- 真实 GPU 端到端：本机无 GPU/torch，只有 `tests/providers/env_sim.py::gpu_state` 模拟证据；未做真实 CUDA 设备验证。
- `tests/infrastructure` 验收路径：任务文本笔误（目录不存在）；我未补建，按 core-report/Lead 说明由 `tests/core` + `tests/providers` 覆盖。
- 旧 PySide6 workbench 失败/transformers 真实检测失败：全量回归复现为既有基线失败，未逐项修/深挖（不在 B-1 diff）。
- B-2 WIP 的正确性：只确认它造成 dirty 工作区 npm 失败与 B-1 隔离需求，未审查 B-2。

## 6. 给出 Lead 的关键结论

1. **AC2 blocker 必须修**：把 `supports_cpu_fallback`（以及 `requires_gpu`）的来源改为 `ProviderRegistry` 的 `ProviderDescriptor`（或把 descriptor flags 真正暴露到 provider），否则 `allow_cpu_fallback` 对 Manga OCR/Paddle Korean 等真实 provider 是假控件，D06 §82 回退不成立；当前测试用假 provider 实例属性掩盖了这一点。修好后补"descriptor 声明、实例无属性"的回归测试与 OCR 端到端回退测试。
2. **AC2 语义需裁决**：`run_guarded` 丢弃 `DevicePlan`，`cpu` 偏好不改变实际调用、`gpu` 只做可用性/回退校验；设计只要求"经 plan 校验"，但 UI"仅 CPU/优先 GPU"会被用户理解为强制设备。请 Lead 决定是"只校验"（改 UI/设计说明并固化测试）还是真正传递设备（更大改动）。
3. **交付 commit 治理未闭环**：committed Task canonical evidence 仍 pending、delivery/integration pin 为 null、Handoff 未跟踪；clean commit `check.ps1` FAIL。请在 B-1 交付/关闭 commit 中固定 pins、canonical evidence、Handoff、Review 路径（`review-b1.md`），并重跑 `check.ps1`。
4. **工作区污染**：Lead 消息称工作区干净/387 测试全绿，但当时工作区有未提交 B-2 前端/测试/任务（`CacheRevisionPanel*`、`client.cleanup.test`、SettingsPage/client 改动、未跟踪 B-2 Task）；直接 npm 会 4 failed。B-1 的验收/Review 必须基于 clean commit（我已用 `git archive` 快照验证 39/387 全绿）；B-2 应隔离到独立 worktree/分支，且 B-2 依赖 B-1，先完成 B-1 再推进。
5. **小问题**：`_retry_policy_for_run` 文档说非 Mapping snapshot 返回 base，实际 `_section` 对 None 会 AttributeError（当前 `PipelineRun` 会规范化为 `{}`，建议加 guard + test）；Task 的 Review 文件名与 `review-r1.md` 不一致；design §4.3 的 B-2 冻结超出 B-1 AC，请 B-2 owner 确认或移出。

## 7. 审查快照

- commit `7d19164f838607e68e2b6970bbbd57bee7bd5777`，parent `da3b781d8971dcc36bd7bfd1165fa1a2f4519ea5`。
- clean 快照：`git archive 7d19164` 解压到 `G:\CODEX\New Manga.workspace\review-b1-7d19164`（仅用于本次验证，含 junction 到原 `node_modules`）；审查完成后已安全删除 junction 与该临时目录，原仓库 `node_modules` 未受影响。
- 关键证据：`verification/SETTINGS-OPEN-B-1/core-report.md`、`ui-report.md`、`core-pytest-*.txt`、`frontend-*.txt`；我未修改任何产品代码或 Task/Handoff/证据文件。
- 审查期间工作区另有 Lead 未提交的 B-2/Task/Plan/Status 改动；这些未进入本报告的 commit 结论（除 M2/M3 明示外）。
