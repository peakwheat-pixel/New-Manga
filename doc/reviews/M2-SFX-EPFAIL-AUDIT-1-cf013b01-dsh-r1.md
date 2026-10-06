# M2-SFX-EPFAIL-AUDIT-1 非作者独立 Review（DSH r1）

审查对象：worktree `G:\CODEX\New Manga.worktrees\M2-SFX-EPFAIL-AUDIT-1-zcode`｜branch `agent/zcode/M2-SFX-EPFAIL-AUDIT-1`｜base `d298ecd0`。交付链经 Git common-dir 分支 reflog 实证：`d298ecd0`（切点）→ `a336bd41` claim → `0f4702d0` impl → `0afb22dd` test → `2bed03d0` verify → `cf013b01` docs（**分支 tip = `cf013b01`**，与 Handoff「delivery_head=2bed03d0 + docs 后继、tip 以分支头为准」一致）。审查为纯静态读码/读证据，未执行命令、未写文件。

## 1. 终判

**changes_requested**（1×P1、1×P2、2×P3、8×P4）。

机制本体正确且已被我独立复核：每 detect 一次公共 `get_providers()` 读回、与构建期 effective 比对、变化才追加单键——这条链路在 provider 级成立，四项硬约束（三键语义/写入时点、`NEWMANGA_SFX_EP` 解析与 fail-fast 时序、零 stdout、≤1% 时延门）均守住，先红后绿、parity 与全量回归证据也自洽。但新键所落的 options 容器在**生产装配路径上被 `MangaSfxParallelDetectionProvider` 丢弃**，任何持久化/呈现面（detect provenance、`core.detect`）都看不到它，因此 AC1 的「可观测性」只在 provider 级成立，deploy-record §0「本 Task 闭合该登记」属过度声明；另有 1% 硬门证据的预算口径算错 100×（结论不变）。二者其一为必须返修、其二为应返修，故不判 approved。

## 2. 分级发现

### 2.0 正向核验（无发现，供集成方对账）

- **wrapper 机理逐行实证**：`get_providers` 是 `return self._providers`（`G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Lib/site-packages/onnxruntime/capi/onnxruntime_inference_collection.py:214-216`，纯属性读，无 native 调用）；`run` 的 EPFail 分支 `:295-305`（`:297 except C.EPFail` → `:298 if self._enable_fallback` → `:299-300` 两行 stdout `print` → `:301 set_providers(self._fallback_providers)` → `:303 disable_fallback()` → `:304` CPU 重跑并正常返回 → `:305` 否则 `raise`）；`set_providers` → `_reset_session`（`:231-251`、`:625-644`）→ `_create_inference_session` 在 `:621` 重写 `self._providers = self._sess.get_providers()`。**因此「run 之后读回可见 `[Dml,CPU]→[CPU]`」这一设计前提在源码级成立**，不是猜测。
- **fallback 列表形态**：DML 请求走 `:541-577` 的 else/else 分支 → `self._fallback_providers = ["CPUExecutionProvider"]`（CUDA 分支要求请求里含 CUDA，本仓不会命中）→ 首 provider 必变，比对判据不会漏报。
- **归因前提可核**：全仓 `set_providers` 仅出现在注释与 wrapper，本仓代码零调用；`get_providers` 在 `src/` 内的调用只有 `detection_sfx.py:530`（新审计）与 `:1034`（构建期读回）。
- **实现与声称一致（稳态零追加）**：`src/infrastructure/providers/detection_sfx.py:800` 在 run 之后、`elapsed_ms` 采集（`:801`）之前取 `runtime_options`，`:818 *runtime_options` 在稳态是空元组展开 → options 与改动前逐字节一致，三键值仍来自 `:811-817` 的构建期缓存 provenance（写时点=引擎构建一次，`_engine_or_raise` `:887-889`）。
- **时序零改动**：`detect` 入口 `:745-748`（`_tile_config` → `_ep_config` fail-fast）与 `_build_engine` 的 6 步检查顺序未变，新调用在 `_engine_or_raise` 之后，不在任何 fail-fast 之前。
- **零 stdout 依赖**：新代码与全 `_runtime_ep_audit` 无 `print`/无 stdout 捕获（`:504-548`）。
- **红绿自洽**：红 log `verification/M2-SFX-EPFAIL-AUDIT-1/raw/tests-epfail-red.log:5,92` = `-k runtime` 选中 4 条（3 新用例 + 既有 `test_hash_mismatch_fails_before_any_runtime_import`，`tests/providers/test_detection_sfx.py:172`）、`1 failed, 3 passed, 78 deselected` → 文件总数 82；绿 log `:5,10` = `4 passed` + 全文件 `82 passed` = 79 基线 + 3 新增；失败点正是 `tests/providers/test_detection_sfx.py:1589` 的 `KeyError: 'sfx_ep_runtime_check'`（red log:87）。
- **AC3 数字独立对表**：`raw/epfail-audit-parity-prek01.json:22-52` 与 GPU-EP-1 基准行 `verification/M2-SFX-GPU-EP-1/raw/gpu-ep-parity-perf.json:61-76`（pre-k01：23/23、bit_identical=false、1e-06、0.0001px、gate_flips=0、2/2、5/48、bit_stable=true）**逐字段一致**；回归 `raw/pytest-full-regression.log:401-402` = `1 failed, 1826 passed, 1 skipped`，唯一失败=`test_catalog.py::test_manifest_has_unique_cases_and_exact_taxonomy`（既有 BASELINE_FAILURE），对照 GPU-EP-1 r2 `raw/pytest-full-regression-r2run.log:399` = `1823 passed` → 等量递增 1823+3=1826 成立。
- **禁改面线索**：全仓 grep `EPFAIL-AUDIT-1` 的命中文件仅 tests / src（1 文件）/ experiments（2 脚本）/ verification（5 raw + 部署记录）/ doc/tasks / doc/handoffs / doc/STATUS.md（释放登记原句，非本 Task 写入）；`contracts/**`、`apps/**`、`packaging/**`、`requirements.txt`、其他 provider 无命中。（**不可核验项**：静态沙箱无法执行 `git diff --name-only`，禁改面「零 diff」仍建议集成方在 merge 前以 git 复核。）

### P1（必须返修）

**P1-1 审计键在装配形态（生产路径）不可达 → AC1 的「可观测性」未落到产出面，§0 闭合声明过度。**

- 写入点：`src/infrastructure/providers/detection_sfx.py:796-824`——四键（`device`/`sfx_ep`/条件 `sfx_ep_fallback`/条件 `sfx_ep_runtime_check`）写在 **`SfxDetectionProvider` 自己的 `DetectionResult.options`**。
- 丢弃点：同文件 `:1394-1405`——composite `MangaSfxParallelDetectionProvider.detect` 用 `replace(result, options=result.options + arbitration_options + (sfx_provider, sfx_candidates, sfx_conf_threshold))` 重建 options，**`sfx_result.options` 从不进入**；typed 降级分支 `:1326-1328` 同样只追加 `sfx_provider_status`（所以「读回在 run 之后」的信号在装配面既不透传、也不在降级路径里被替代承载）。
- 生产装配事实：`src/bootstrap/core_assembly.py:973-985`（非 mock = 生产形态才包 composite；mock 分支不装 sfx=已登记决策）、`:1061` 与 `:1194-1196`（handler deps 与 core service 拿到的都是 composite）。
- 持久化/呈现面：`src/infrastructure/providers/handlers.py:278-299`（`detection.provenance()` → `StepResult.outputs["detection"]` 与 region provenance）+ `src/ports/detection/ports.py:118-127`（`provenance()` 内含 `"options": dict(self.options)`）；另一 RPC 面 `src/bootstrap/core_service.py:522-538` 的 `core.detect` **只返回 candidates + elapsed_ms，连 options 都不返回**。→ 生产上没有任何一条通路能看到 `sfx_ep_runtime_check`（GPU-EP-1 的 `sfx_ep`/`sfx_ep_fallback` 同样看不到；而 primary 的 `device`（torch，`src/infrastructure/providers/detection_manga.py:402-404`）却会出现在同一 provenance 里，读者反而更容易误读）。GPU-EP-1 r2 的 P4-3 只核了代码消费方（`apps/**` 零命中），未核 composite 的透传面。
- 本 Task 的证据路径全在 provider 级：`experiments/M2-SFX-EPFAIL-AUDIT-1/verify_epfail_audit_parity.py:151-169` 直接 `SfxDetectionProvider(...)`；三条新用例 `tests/providers/test_detection_sfx.py:1519-1648` 也是 provider 级（composite 用例 `:569-572` 只断言 3 个 summary 键，永不会碰到 EP 键）。因此 `verification/M2-SFX-EPFAIL-AUDIT-1/deploy-record.md:9`「本 Task 闭合该登记」在生产层面不成立（provider 层面成立）。
- 返修建议（二者择一，前者优先；均在 Task 允许路径内）：
  - **(a) 透传（推荐、增量安全）**：在 composite 的 tail **条件性**追加 `sfx_ep_runtime_check`（仅当 `"sfx_ep_runtime_check" in dict(sfx_result.options)`；稳态生产 provenance 逐字节不变），并补 1 条 composite 级用例钉住「静默回退页 → composite options 携带该键」。若要同时透传 `sfx_ep`/`sfx_ep_fallback`，注意 `device` 与 primary 同名、`dict()` 会取后者，建议只透传 sfx 专属键或改前缀。现有断言（`:569-572`）与 `tests/core/test_sfx_assembly.py`（无 options 断言）均不会被破坏。
  - **(b) 如实登记**：若判定 composite options 面属 M2-SFX-PROD-1 冻结语义、不在本 Task 授权内，则把「审计仅 provider 级可见；生产 composite 不透传 sfx options（三键+新键）；core.detect 不呈现 options」写进 deploy-record §5 已知限制 + Handoff/Task，并把 §0 收窄为「provider 级闭合 + 装配面透传缺口（后续切片）」，交 Codex 裁决。此时本 P1 降为文档返修。

### P2（应返修）

**P2-1 1% 硬门证据的「预算」实为整页时延，且「占 1% 预算」的比例被写成整页占比（差 100×）。**

- `experiments/M2-SFX-EPFAIL-AUDIT-1/measure_get_providers_cost.py:176-186`：`per_page_budget_us = min(GPU_EP1_KO_DML_PER_PAGE_S) * 1e6  # 1% of 1.106 s` —— 实际算出 **1,106,000 μs = 整页**，1% 应为 **11,060 μs**；`worst_call_share_of_budget_pct` 与 `worst_call_share_of_page_pct` 因此是**同一个量**（增量/整页）的两种舍入（`raw/epfail-audit-get-providers-cost.json:60-70`：`one_percent_budget_us: 1106000.0`、`worst_call_share_of_budget_pct: 3e-06`、`worst_call_share_of_page_pct: 2.76e-06`）。
- 正确口径：增量/整页 = 0.0305/1,106,000 = 2.76e-8 = **2.76e-6 %**；增量/1% 预算 = 0.0305/11,060 = 2.76e-6（无量纲）= **2.76e-4 %**。而 `deploy-record.md:25`「的 ~2.8e-6 %（**1% 预算占比 3e-6 %**）」、`doc/tasks/M2-SFX-EPFAIL-AUDIT-1.md:46,50` 与 `doc/handoffs/…:17,25`「**1% 时延预算** ~2.8e-6%」把整页占比当成了 1% 预算占比。
- 结论不受影响（即使按整页口径 2.76e-8 也 ≪ 1%；按正确预算口径充裕 5 个数量级），故非阻塞；但这是硬门数字，建议修正 `one_percent_budget_us`=11060、重述两处占比文案，并把脚本 gate 比较改用 11,060 μs（现比较用的是整页，门被弱化 100×）。

### P3（建议）

**P3-1 「重跑亦失败 → 下一页观测」只有推理，无用例钉子。** 登记见 `deploy-record.md:35-38`（覆盖面形态 2）与 `doc/tasks/…:46`；但 `tests/providers/test_detection_sfx.py:1595-1599` 的第二页是「第 1 页静默回退**成功**」之后，`tests:1628-1648` 只覆盖无读回面跳过。链路本身成立（provider 实例装配期构造一次 `core_assembly.py:976`，session 缓存于 `self._engine` `detection_sfx.py:887-889`，wrapper 已用 `:301`→`:621` 改写 `_providers`），但建议补 1 条用例（首次 `run` 抛 `C.EPFail` 形态 → 当页 typed 失败/无 options；同 provider 第二次 detect → 新键出现），把登记的第 2 种形态变成钉子。

**P3-2 红 log 的「3 passed」叙述不精确。** `raw/tests-epfail-red.log:5,92` 实际是 `-k runtime` 选中 4 条 = 3 新用例 + 既有 `test_hash_mismatch_fails_before_any_runtime_import`（`tests:172`）；`deploy-record.md:64` 与 `handoff:26` 写成「两个辅助用例按构造在基线通过」，漏计那 1 条既有用例（数字自洽，仅叙述层面，建议改为「3 passed = 2 新辅助用例 + 1 条被 `-k` 选中的既有用例」）。

### P4（备注）

- **P4-1 base 语义双值**：`doc/tasks/M2-SFX-EPFAIL-AUDIT-1.md:12` `base_commit: 72807d30`（释放登记 base，与 `M2-PROD-SFX-PROBE-1:11`/`M2-SFX-TILE-WIDTH-CALIB-1:11` 同款、与 `STATUS.md:14` 的 `base=72807d30` 相符）vs `handoff:5` `base_commit: d298ecd0`（worktree 切点，reflog 首条实证）。建议在 Task 注记两值含义，避免集成 diff 取点歧义。
- **P4-2 「never a new failure point」略强**：`detection_sfx.py:530-533` 用 `getattr(session,"get_providers",None)` 后直接调用；若该属性存在但不可调用会 `TypeError`（真实 ORT session 不会命中）。文档可加「不可调用形态不兜底」一句。
- **P4-3 只比对 `providers[0]`**（`:536-540`）：首 provider 不变而列表变化的形态不可见；本 wheel 的 fallback 恒为 `["CPUExecutionProvider"]`（wrapper `:541-577`）故当前无漏报，建议在注释登记「wheel 升级复核面」。
- **P4-4 键值内嵌因果归因**：观测到的只是「列表相对构建期变化」，值里却写死 `"(ORT wrapper run-time EPFail fallback)"`（`:543-547`）。已由 `deploy-record §5.1` 与代码注释 `:419-443` 登记归因依赖，可接受；更中性的值会更严谨。
- **P4-5 证据 mark 小瑕**：`raw/tests-epfail-green.log:6` `EXIT_K Runtime=0`（变量名/拼写破损）；红证据依赖「实现 stash 隔离」手法（`red log:1`），不能由单一 commit 复现（已如实登记，属可接受口径）。
- **P4-6 测量范围**：0.0305 μs 只测原语 `get_providers()` 本身，未含 `_runtime_ep_audit` 的 `getattr`/真值判断/`dict.get`/比较开销；`deploy-record.md:25` 把整页增量等同于该单值，建议注明「口径=单次原语调用」。
- **P4-7 跨 worktree 依赖**：`experiments/M2-SFX-EPFAIL-AUDIT-1/verify_epfail_audit_parity.py:44-46` 从**主 checkout** `G:/CODEX/New Manga/verification/M2-SFX-GPU-EP-1/raw/gpu-ep-parity-perf.json` 读基准行，而非 worktree 相对路径；worktree 内副本与引用值一致（`verification/M2-SFX-GPU-EP-1/raw/gpu-ep-parity-perf.json:61-76`），本次结论不受影响，建议脚本注释登记该依赖。
- **P4-8 parity 脚本门弱于措辞**：`:236-246` 的 `same_shape` 只用 `dconf ≤ 1e-05 / dxyxy ≤ 0.001` 的宽松判据，而 `deploy-record §4.1` 声称「逐数字一致」；「逐数字一致」由 json 内两行对照成立（`epfail-audit-parity-prek01.json:22-52`），建议在脚本注释里区分「脚本门=同量级」与「人工对表=逐数字」。

## 3. AC 逐条判定

| AC | 判定 | 一句话理由 |
|---|---|---|
| **AC1 审计机制** | **PARTIAL** | 所选设计（每 detect 一次 `get_providers()` 读回、与构建期 effective 比对、变化才追加单键）与四项硬约束（三键语义/写时点不变、`NEWMANGA_SFX_EP` fail-fast 时序零改、零 stdout、≤1% 门）**全部成立且经源码级复核**，但审计键在生产 composite 面被丢弃（P1-1）、1% 预算口径数字标错（P2-1），「可观测性」只到 provider 级。 |
| **AC2 单测先红后绿** | **PASS** | 3 条用例真实复现 wrapper 静默回退形态（stub 构造器正常返回、run 期翻转 providers、零异常，`:1541-1566`），红 log 恰为 `KeyError: 'sfx_ep_runtime_check'`（1 failed/3 passed/78 deselected）、绿 log 全文件 82 passed=79+3，计数与文件实测一致；仅「重跑亦失败→下一页」无钉子（P3-1）与红 log 叙述小瑕（P3-2），不影响 AC2 成立。 |
| **AC3 数值与回归零变化** | **PASS** | parity 抽 pre-k01 与 GPU-EP-1 基准行逐字段一致（我按 GPU-EP-1 raw:61-76 独立对表），真实稳态两 face 零新键、三键照常（parity log:8），全量回归 1826+1sk+1 failed 对基线 1823+1sk+1 failed 等量递增且唯一失败同为 test_catalog 既有项；数值结论不因本 Task 变化。 |
| **AC4 文档** | **PARTIAL** | 部署记录/ Task 回填 / Handoff 齐备，GPU-EP-1 §1.3 以注记闭合且历史文件零改动（`M2-SFX-GPU-EP-1/deploy-record.md:93-98` 原文未变）合规；但 §0「本 Task 闭合该登记」在生产面过度声明（P1-1），且 1% 预算/占比表述在 Task、Handoff、部署记录与 JSON 间不一致（P2-1）。 |

## 附：推荐下一步（依仓库协作协议）

1. 本 Review 落档建议路径 `doc/reviews/M2-SFX-EPFAIL-AUDIT-1-cf013b01-dsh-r1.md`（分支 tip 以 common-dir 分支 reflog 为准 = `cf013b01`，非 Handoff 的证据锚 `2bed03d0`）。
2. Codex/集成方先裁决 **P1-1**：判 (a) 透传 → Owner 返修（composite tail 条件性追加 + 1 条 composite 用例 + 文档数字修正）后走 r2；判 (b) 冻结语义不可动 → 只需文档如实登记并收窄 §0 闭合声明，可直接进入集成（P2-1 建议同批顺笔修正）。
3. 可直接转发的指令：「对 M2-SFX-EPFAIL-AUDIT-1 执行 r1 Review 返修：worktree `G:/CODEX/New Manga.worktrees/M2-SFX-EPFAIL-AUDIT-1-zcode`，branch `agent/zcode/M2-SFX-EPFAIL-AUDIT-1`，tip=`cf013b01`。处置 P1-1（composite 不透传 sfx options → 按批准口径选择 `detection_sfx.py:1394-1405` 条件性透传 `sfx_ep_runtime_check` 并补 composite 级用例，或按 Codex 裁决在 deploy-record/Handoff/Task 如实登记并收窄闭合声明）与 P2-1（`experiments/M2-SFX-EPFAIL-AUDIT-1/measure_get_providers_cost.py:176-186` 的 1% 预算口径与四处占比文案）；同步处理 P3-1/P3-2；不改 contracts/apps/packaging/requirements 与其他 provider。」
