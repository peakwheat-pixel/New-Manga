# L2 Vision OCR「合法 replay 配置被判 PROVIDER_NOT_CONFIGURED」根因诊断

- **日期**：2026-11-14
- **性质**：只读诊断（未改任何 `src/**`、`tests/**`、契约、既有文档；只新建本文件）
- **基线**：`G:/CODEX/New Manga` HEAD `a05dbc64b`，工作区无未提交改动
- **输入证据**：会话内实测（`create_run` 后 `run.provider_binding_snapshot["ocr"]` 完整合法 + 执行期 `ocr / PROVIDER_NOT_CONFIGURED`）、`verification/L2-CORE-E2E/**`、源码与测试
- **本次新增的只读复现**：`G:/CODEX/New Manga.workspace/L2-VISION-OCR-DIAG/{probe_registry.py,probe_e2e.py}`（仓外，未进 Git；只走真实代码路径，不发真实网络请求）

---

## 0. 结论（一句话根因）

**`ocr` 的"就绪"不是从 Run 的冻结 replay 配置判定的，而是从装配期一次性构建的 `ProviderRegistry` 静态 `requirements` 判定的：`ProviderRegistry.resolve()` 先无条件调用 `status()` 做就绪门，`status()` 探测的是 `build_provider_registry` 建表时用「装配期读到的 `pipeline_defaults` 行」算好的 `endpoint`/`credential` 需求（`registry.py:282-284` → `registry.py:190-192,228-240` → `dependencies.py:161-205`）；因此只要执行该 Run 的 Core 在启动时那一行里没有 `providers.profiles["openai-vision-ocr"]` 的 `base_url|model`，`ocr` 就必然抛 `PROVIDER_NOT_CONFIGURED`（detail `no base_url configured`，`registry.py:551-554`），快照再合法也不参与判定 —— 这是**产品缺陷**（配置写入成功 ≠ 运行期生效，且失败码伪装成"未配置"），而**不是**"视觉 provider 无法解析合法 replay 配置"，也**不是**配置形状写错。**

> 需要同时说明的关键推论（第 6 节有证明）：在**同一个** `ProviderRegistry` 实例内，"冻结快照的 `execution` 完整"与"`resolve()` 判 not-configured"**不可能同时成立**。本次实测已证明：把 profile+binding 在启 Core 前写进 `pipeline_defaults`，`translate_all` + page scope 的 `ocr` 会**真实执行**（走冻结的 `base_url`，写出 `ocr_text`）。所以 L2 观测到的这一对事实来自**两个不同的装配实例/进程**（进程内自建 runtime 的核对 vs. 真正执行 Run 的那个 Core）。

---

## 1. 事实基线

| 事实 | 证据 |
|---|---|
| 冻结快照完整（`provider_id: glm-vision-ocr`，`execution.provider_id: openai-vision-ocr`，type `openai-compatible-vision`，`base_url/model/credential_ref/network_profile` 齐全，digest 合法） | 会话内实测；同形描述见 `verification/L2-CORE-E2E/README.md:167-168` |
| 执行 `translate_all` + page scope 时 `ocr` 失败、translate 未执行 | `verification/L2-CORE-E2E/README.md:159-165`；`translate_all` 的步骤序为 `ocr → color → term_extract → translate → segment → mask_refine → inpaint → render`（`src/application/tasks/service.py:93-102,109-110`），前置步骤失败即不再执行后续 unit（既有语义） |
| 三种绑定形状（用户 profile id / 固定槽 id / 槽 id + 保留 translate）全部同码 | `README.md:159-165` |
| **证据缺口**：仓库内唯一落盘的 route-E 运行记录，其 `overrides.provider_bindings.ocr` 实际是 `manga-ocr`，不是 GLM | `verification/L2-CORE-E2E/l2-routeE-run.json:43-47`、`81-86`；`core-stderr-routeE.log` 仅 137 B，无 provider 诊断行 |
| GLM 轮的 `StepRun.error_detail` / Core stderr 未落盘 | 未找到，需进一步确认（见 §9） |

---

## 2. `ocr` step 的 `PROVIDER_NOT_CONFIGURED` 从哪抛出

### 2.1 总调用链（执行期，按顺序）

```
pipeline.execute_run
  └─ ProductionStepExecutor.execute            src/infrastructure/pipeline/executor.py:24-42
      └─ ProductionHandlers._typed(wrapper)    src/infrastructure/providers/handlers.py:247-258
          └─ handle_ocr                        src/infrastructure/providers/handlers.py:522-591
              ├─ (a) self._chain(run, "ocr")   handlers.py:526 → 1266-1274
              ├─ run_chain(...)                src/infrastructure/providers/fallback.py:101-161
              └─ _invoke_provider              handlers.py:540-550 → 1160-1166
                  └─ registry.resolve_for_run  src/infrastructure/providers/registry.py:456-457
                      └─ registry.resolve      registry.py:262-293
                          ├─ capability 校验    registry.py:275-281
                          ├─ status() 就绪门    registry.py:282-284 → 178-250
                          │   └─ evaluate_requirements → failure_for
                          │       src/infrastructure/providers/dependencies.py:161-178,181-206
                          └─ _status_error     registry.py:542-563
              └─ provider.recognize            src/infrastructure/providers/ocr_vision.py:71-109
                  └─ client.complete           src/infrastructure/providers/openai_client.py:165-184
                      └─ require_configured    openai_client.py:93-106
```

### 2.2 全部可达的 raise 点（`ocr` 路径）

| # | 位置 | 触发条件 | 错误码 / detail 指纹 |
|---|---|---|---|
| A | `handlers.py:1266-1274` | `run.provider_binding_snapshot["ocr"]` 缺失或无 `provider_id/provider_profile_id/id`（`chain_from_binding` 返回 `None`，`fallback.py:164-196`） | `stage='ocr'`，detail `no provider binding configured for step 'ocr'` |
| B | `registry.py:275-281` | 解析出的槽不声明 capability `'ocr'` | `stage='resolve'`，detail `provider ... does not declare capability 'ocr'` |
| C | `registry.py:282-284` + `551-554` | `status()` 的 `state == not_configured`：`endpoint` 需求空（`base_url`/`model` 缺失） | `stage='resolve'`，detail **`no base_url configured`** / `no model configured for this endpoint` |
| D | `registry.py:303-323` | `resolve_binding` 名不到 provider（`ocr` 路径未用，`_invoke_provider` 走的是 `resolve_for_run`） | `stage='resolve'` |
| E | `openai_client.py:93-106`（经 `ocr_vision.py:84-93`） | **调用期** `config.base_url`/`model` 为空 | `stage='configure'`，detail `no base_url configured for this provider profile` |
| F | `openai_client.py:63-68` | `base_url` 为空（URL 组成期） | `stage='http'` |
| G | `handlers.py:353-357` | **detect** step 没有装配 detector/region_writer（不是 ocr 的错，但 0-region 页会先跑 detect，`service.py:603-615`） | `stage='detect'` |

**明确排除的**：`VisionOcrProvider` 自身**没有**任何 `PROVIDER_NOT_CONFIGURED` 抛出点（`ocr_vision.py` 全文只有 `ProviderInputError`/`ProviderInvalidOutput`）；其 docstring（`ocr_vision.py:12-14`）说的是"registry 层就绪"，实现落在 registry/dependencies 与 client，不在适配器内。

### 2.3 三种形状在"判定条件"上的差别（为什么形状不影响结论）

- `_chain` 只要求 binding 能读出 `provider_id`（`fallback.py:178-185`）——三种形状都满足。
- `resolve()` 会先把"用户 profile id"经 `binding_aliases` 翻成固定槽 id（`registry.py:264-266`），别名在装配期由 `_apply_profile_bindings` 建立（`runtime.py:418-467`，键为 `(profile_id, capability)`，ocr 的 capability 是 `"ocr"`，`runtime.py:389-393`）。
- 因此 E-1 / E-2 / E-3 三条路径最终都落到**同一个**槽 `openai-vision-ocr` 的同一个 `status()` 上 —— 形状再怎么换都不改变判定结果，这与"三种形状全部复现"完全一致。

---

## 3. "Not-Ready / 未配置"的判定条件（逐条，精确）

`registry.register` 时 vision OCR 槽声明（`src/infrastructure/providers/runtime.py:628-639`）：

```python
registry.register(
    ProviderDescriptor(
        provider_id=PROVIDER_VISION_OCR,                      # "openai-vision-ocr"
        provider_type="openai-compatible-vision",
        capabilities=frozenset({CAPABILITY_OCR}),             # {"ocr"}
        requirements=_openai_requirements(PROVIDER_VISION_OCR, settings),   # ← 装配期算
        note="explicit Vision fallback for art text / low-quality OCR",
    ),
    vision_client(PROVIDER_VISION_OCR, "openai-compatible-vision"),         # ← 同一个 settings
    gate=_network_gate(PROVIDER_VISION_OCR, settings),
    enabled=_slot_enabled(settings, PROVIDER_VISION_OCR),
)
```

`_openai_requirements` 的展开（`runtime.py:470-483`）：

```python
profile = _provider_settings(settings, provider_id)          # settings["providers"]["profiles"][id]
base_url = str(profile.get("base_url", ""))
model = str(profile.get("model", ""))
requirements = [Requirement(KIND_ENDPOINT, f"{base_url}|{model}", detail="remote endpoint")]
if profile.get("credential_ref"):
    requirements.append(Requirement(KIND_CREDENTIAL, str(profile["credential_ref"])))
```

判定顺序（`registry.py:214-250` + `dependencies.py:181-206`）：

1. `enabled is False` → `disabled / PROVIDER_DISABLED`；
2. `implements is False` → `not_ready / PROVIDER_NOT_IMPLEMENTED`（vision OCR 是 `implements=True`）；
3. 逐条探测 `requirements`，**第一条不满足者**决定错误：
   - `KIND_MODULE`/`KIND_WEIGHT` → `PROVIDER_DEPENDENCY_MISSING`；
   - `KIND_CREDENTIAL` → `MissingCredential`，state 记为 `missing_dependency`（`registry.py:230-234`），最终经 `_status_error` 变成 **`PROVIDER_DEPENDENCY_MISSING`**；
   - `KIND_ENDPOINT`（其余分支兜底）→ `ProviderNotConfigured` → state `not_configured` → **`PROVIDER_NOT_CONFIGURED`**（`dependencies.py:203-205` + `registry.py:551-554`）；
4. `gate()`（网络解析，`runtime.py:486-499`）不满足 → state `not_ready`，`error_code` 虽写成 `PROVIDER_NOT_CONFIGURED`（`runtime.py:496`），但 `_status_error` 按 **state** 分派，最终抛 **`PROVIDER_UNAVAILABLE`**（`registry.py:561-563`）——这是本次诊断一个重要的"码不等于原因"陷阱；
5. 能力声明不含请求的 capability → 直接 `PROVIDER_NOT_CONFIGURED`（`registry.py:275-281`）。

**所以：`PROVIDER_NOT_CONFIGURED` 在本路径上等价于"该槽的 endpoint 需求为空（`base_url` 或 `model` 缺）"**（或 capability 不符，见 §4-3）。

---

## 4. 逐项排除表

| # | 假设 | 结论 | 依据 |
|---|---|---|---|
| 1 | **判定读执行期 Run 快照**（应如此） | **否 —— 这是根因** | `resolve_for_run` 第一步就是 `self.resolve(...)`（`registry.py:456-457`），而 `resolve` 用 `status()` 的**装配期** requirements（`registry.py:190-192`）；冻结的 `execution` 只用于之后**重建 config**（`registry.py:466-502`），**不参与就绪判定**。即：快照只在"判定通过后"才有意义 |
| 2 | 判定读**装配期 registry 静态实例** | **是** | ① 实例在装配期一次性构建：`core_assembly.py:1419-1426`；② `requirements` 在建表时求值：`runtime.py:633`；③ 全仓只有一处 `build_provider_runtime`（grep 确认 `core_assembly.py:1421`），**没有任何运行时重建/刷新**；④ `ProviderRegistry.invalidate` 存在（`registry.py:526-531`）但生产无调用者 |
| 3 | `provider_id` 必须是注册槽 id | **否** | 别名机制把 profile id 翻成槽 id（`registry.py:264-266`，`runtime.py:418-467`）；实测 E-1 形状 `resolve("ocr","glm-vision-ocr")` 返回的是槽实例（`base_url` 取自 profile）。前提是**装配期**那一行里有该 profile 且 binding 指向它 |
| 4 | E-3 用槽 id 仍失败 ⇒ 还差什么 | 差的是**装配期那一行里槽位 profile 是否存在** | 槽 id 路径不依赖别名；此形状下唯一的变量就是 `settings["providers"]["profiles"]["openai-vision-ocr"]`。实测：有 → `ready`；无 → `not_configured / no base_url configured` |
| 5 | `provider_type` 字符串必须与 registry 完全一致 | **对 ocr 的就绪判定无影响**，但影响冻结 | 槽 descriptor 的 type 由 registry 自己写死（`runtime.py:631`）；`_registry_target_for_step("ocr", ...)` 不看 type（`runtime.py:396-403`）。type 只决定 ① `freeze_run_snapshots` 是否冻结（`registry.py:366-372`）② 重放 schema 是否接受（`store.py:210-213`）。写错 type 的后果是 `RUN_SNAPSHOT_INCOMPLETE`，不是 `PROVIDER_NOT_CONFIGURED` |
| 6 | vision provider 需要额外 detect 前置能力绑定 | **否** | `needs_detection` 在 `src/**` 内**没有任何消费方**（只有定义：`ports/ocr/ports.py:119`、`ocr_vision.py:60`、`ocr_local.py:95,182`、`ocr_manga_onnx.py:158`）；detect 是**页面级**独立 unit（`service.py:603-615`），与 ocr 的 provider 解析无关 |
| 7 | `credential_ref` 特定格式 / vault 命中失败导致 | **否（且不是本码）** | `probe_credential`（`dependencies.py:141-158`）失败在 `failure_for` 里映射为 `MissingCredential`，state=`missing_dependency`，`_status_error` 转成 **`PROVIDER_DEPENDENCY_MISSING`**（`registry.py:555-560`）。**实测**：credential 解析不到时 `resolve()` 抛 `PROVIDER_DEPENDENCY_MISSING`，**不会**抛 `PROVIDER_NOT_CONFIGURED`。格式本身无关：`credential_ref` 是 opaque 字符串，直接交给 resolver（`openai_client.py:207-208,240-254`） |
| 8 | `credential_ref` 必须能在 vault 以**该 profile 的 id** 命中 | **否** | resolver 只按 ref 字符串查（`core_assembly.py:803-818`）；ref 里出现 `glm-vision-ocr` 而 profile 叫 `openai-vision-ocr` 并不影响命中，只要 vault target 与 ref 一致（L2 用 `cmdkey /generic:NewManga/provider/glm-vision-ocr/ocr-basic`，`README.md:155`） |
| 9 | run 快照的 `ocr` 绑定缺失 | **否（就本证据而言）** | 会话内实测明确存在且带 `execution`；且若缺失，A 点 detail 会是 `no provider binding configured for step 'ocr'` |
| 10 | 网络 profile 引用解析失败 | **否** | 走 gate → 最终抛 `PROVIDER_UNAVAILABLE`（`registry.py:561-563`），与观测码不同 |

---

## 5. 装配期与执行期的关系（问题 4）

### 5.1 装配期读 profile 的路径

```
assemble_core_services
  ├─ credential_store = _credential_store()                 core_assembly.py:787-800
  ├─ transport = StdlibTransport(credential_store=...)      core_assembly.py:1420
  └─ build_provider_runtime(
        settings=_load_pipeline_settings(conn),             core_assembly.py:1422 → 770-784（读 settings_json 一次）
        provider_bindings=_load_pipeline_defaults(conn)["provider_bindings"],   core_assembly.py:1423 → 727-767
        credential_resolver=_credential_resolver(...),      core_assembly.py:1425 → 803-818
     )                                                       core_assembly.py:1421-1426
       └─ runtime.build_provider_runtime                     runtime.py:752-796
           ├─ settings, _ = _apply_profile_bindings(settings, provider_bindings)   runtime.py:761
           └─ build_provider_registry(settings=..., provider_bindings=...)        runtime.py:764
               ├─ settings, aliases = _apply_profile_bindings(...)               runtime.py:512
               └─ 注册 vision OCR（requirements 在此刻定值）                      runtime.py:628-639
```

关键点：`_openai_requirements(PROVIDER_VISION_OCR, settings)`（`runtime.py:633`）与工厂里的 `_openai_config(PROVIDER_VISION_OCR, ..., settings)`（`runtime.py:522-532,252-271`）读的是**同一个** `settings` 映射。因此：

> **`execution.base_url` 非空 ⇔ 装配期该槽的 endpoint 需求满足**（`validate_provider_execution` 还强制 `base_url`/`model` 非空，`store.py:170,223`）。

### 5.2 "先 seed 再启 Core" 是否真的能让 vision provider 在装配期就绪

**能，且本次已实测。** 用真实代码路径（`SqliteSnapshotProvider.set_defaults` 写入 `pipeline_defaults` 行 → `build_provider_runtime` → `build_production_pipeline(snapshot_transform=registry.freeze_run_snapshots)`）复现 E-1 与 E-3 两种形状：

```
===== E-1 user profile id (profile=glm-vision-ocr, binding=glm-vision-ocr)
   readiness openai-vision-ocr: ready
   frozen ocr binding keys: mappingproxy
   run status: PipelineRunStatus.COMPLETED_WITH_FAILURES | transport calls: ['https://open.bigmodel.cn/api/paas/v4/chat/completions']
   step: ocr StepRunStatus.COMPLETED None
   region-a ocr_text= 'おはようございます。'
===== E-3 fixed slot id (profile=openai-vision-ocr, binding=openai-vision-ocr)
   ... 同上（ready，ocr COMPLETED，写出 ocr_text）
```

（`color` 之后失败是探针的假图像源没有 PNG —— `INVALID_INPUT: page ... has no PNG in this double`；生产装配了真实 `SourceStyleService(PillowSourceStyleAnalyzer())`，`core_service.py:900`、`core_assembly.py:1719`，不属于本次问题。）

反面（同一探针构造"槽位无 profile"）：

```
--- profile present, NO ocr binding at assembly
   status : not_configured PROVIDER_NOT_CONFIGURED | no base_url configured | missing: ('endpoint',)
   resolve('openai-vision-ocr') -> ProviderNotConfigured: PROVIDER_NOT_CONFIGURED: no base_url configured
--- E-1 profile-id binding, vault MISSES
   status : missing_dependency MISSING_CREDENTIAL | credential '...' is empty
   resolve('...') -> ProviderDependencyMissing: PROVIDER_DEPENDENCY_MISSING
```

### 5.3 产品的生效语义：写入成功 ≠ 运行期生效

- 设置写入只落到 `pipeline_defaults` 行（`provider_runtime_mirror.py:119-124` → `pipeline_defaults.py:105-120`），**不触碰已装配的 runtime**；
- 装配注释自己写明"配置变更需下一次装配生效"：`core_assembly.py:1459-1462`；
- 全仓**没有** registry 重建/`invalidate()` 的生产调用者（grep `provider_runtime` 的 19 处引用中无重建；`invalidate` 无调用者）；
- 设置命令返回成功时**不告知**"需重启 Core 才生效"（`settings_commands.py:1003-1020` 只描述 mirror 到 DB，没有 restart 信号）。

### 5.4 一个容易放过的旁路：字符串 binding 同时绕过"冻结校验"和"planning 就绪门"

- `freeze_run_snapshots`：id 查不到 descriptor 或 type 不在 typed 集合时直接 `continue`，**binding 保持裸字符串，不报错**（`registry.py:366-372`）→ `validate_provider_execution` 不执行 → StartRun 照样被接受；
- `run_binding_available`：`if not isinstance(binding, Mapping) or "execution" not in binding: return True`（`registry.py:504-507`）→ 规划期 `_provider_available` 直接放行（`service.py:711-712,796-804`）；
- 于是这种形状会"顺利规划、到执行期才炸"，且炸出来的码恰好也是 `PROVIDER_NOT_CONFIGURED`。这是"合法快照 vs. 早/晚失败"之外**第二条**会制造同类误导的路径。

---

## 6. 为什么"快照合法 + 执行期 not-configured"在**同一 registry** 内不可能

推理（全部有行号支撑）：

1. 快照 `execution` 完整 ⇒ `validate_provider_execution` 通过 ⇒ `base_url`/`model` 非空（`store.py:155-235`，`170`、`223`）；
2. 该 `execution` 只可能由工厂 `_openai_config(槽, ..., 装配期 settings)` 产出（`registry.py:377-381,423-448`；工厂见 `runtime.py:522-532`）；
3. 因此 `_openai_requirements(槽, 同一 settings)` 的 endpoint 需求**必然满足**（`runtime.py:470-483,633`）；
4. 于是 `status()` 只可能有两种结果：`ready`（credential 也解析到）或 `missing_dependency/MISSING_CREDENTIAL`（credential 解析不到，`dependencies.py:199-202` + `registry.py:230-234`）——**都不是** `not_configured`；
5. 由 4，`resolve()` 只会返回实例或抛 `PROVIDER_DEPENDENCY_MISSING`，不会抛 `PROVIDER_NOT_CONFIGURED`；
6. 且规划期先跑同一个 `resolve_for_run`（`service.py:711-712` → `registry.py:504-524`）：若槽真的 not-configured，ocr unit 会在**规划期**被标 `BLOCKED(PROVIDER_UNAVAILABLE)`（`service.py:712`），根本不会有 `StepRun` 失败记录（对照 `verification/L2-CORE-E2E/README.md:90,132` 的 route 2：blocked 且无错误码）。

⇒ 观测到的"完整快照 + `StepRun` 级 `PROVIDER_NOT_CONFIGURED`"只能来自**两个不同的装配实例**（核对快照的 runtime ≠ 执行 Run 的 Core），或来自 §5.4 的字符串 binding 旁路（但那样快照里不会有 `execution`）。

⇒ 换言之：**该现象不是"registry 拒绝了合法 replay 配置"，而是"执行它的那个 Core 在启动时读到的配置里没有这个槽"**——`verification/L2-CORE-E2E/README.md:24-27` 自己记录的装配期约束（run-level override 无效、必须 DB seed 后重启）正是同一枚硬币的另一面。

---

## 7. 最小修复方向（不实现，只给方向）

按优先级：

1. **让就绪判定吃 Run 的冻结配置**（根治，最小面）：`ProviderRegistry.resolve_for_run`（`registry.py:456-459`）目前是"先 `resolve()` 再考虑 `execution`"。改为在 `execution` 存在时**以冻结配置为准**做 fail-closed 校验（`provider_id/model/base_url/credential_ref` 齐备 + digest 一致 + capability 匹配），把 `resolve()` 的 live `status()` 降级为"仅当没有冻结执行面时使用"。这样"快照合法但进程启动态陈旧"不再互相矛盾，也不破坏 D06 §50「Run 命名 provider」语义。
2. **给配置写入一个显式的生效语义**（体验/可诊断）：`settings_provider_profiles_*` / `settings_provider_bindings_*` 成功后返回 `restart_required: true`（或提供 `providers.reload` 之类的显式刷新，重建 `build_provider_runtime` + 替换 handlers 里的 registry 引用）。当前完全没有该信号（§5.3）。
3. **收紧"静默跳过"**（防同类误导）：`freeze_run_snapshots` 对"binding 命中了已知能力但无法 typed 冻结"的情况不要 `continue`，而应 `RUN_SNAPSHOT_INCOMPLETE`（`registry.py:366-372`）；`run_binding_available` 对无 `execution` 的字符串 binding 不应无条件放行（`registry.py:504-507`）。
4. **修错误分类（让码说实话）**：`_status_error`（`registry.py:542-563`）应按 `status.error_code` 保留 `MISSING_CREDENTIAL`（现在被抹成 `PROVIDER_DEPENDENCY_MISSING`），并把网络 gate 的 `not_ready` 单独成型（现在被抹成 `PROVIDER_UNAVAILABLE`）。
5. 文档口径：`ocr_vision.py:12-14` 与 `registry.py:1-18` 的"Not-Ready at the registry level"应补一句"该判定读装配期配置，不读 Run 的冻结 replay 配置"，避免下一次把合法配置误判为形状错误。

**不需要**改的地方（已证明）：vision 适配器的 `requirements`、`provider_type` 常量、`needs_detection`、`_apply_profile_bindings` 的别名机制、`credential_ref` 格式。

---

## 8. 判定：产品缺陷还是配置用法错误

- **配置用法：不是错误。** 形状（profile id / 槽 id）、type、`base_url`、`model`、`credential_ref`、vault target 全部正确；用同一份配置走真实装配路径，`ocr` 能执行并落 `ocr_text`（§5.2）。
- **产品缺陷：是，等级 P1（不是 P0）。**
  1. 就绪判定读装配期静态 `requirements`，Run 的冻结 replay 配置**不参与判定**（`registry.py:456-457` → `282-284`）——"冻结快照完整"对执行期没有任何保证力；
  2. 配置写入成功没有生效语义/重启提示，也没有任何运行时重建 seam（§5.3）；
  3. 错误分类会把"凭证缺失/网络不可达"抹成别的码，并把"无法 typed 冻结的 binding"静默放行（§5.4、§7-3/4），使失败现场极难区分"真没配"与"配了没生效"。
- **对 L2 具体这一对证据的附加判定（诚实标注）**：它**不能**用"registry 拒绝合法 replay 配置"来解释（§6 已证明不可能）；最可能是"进程内自建 runtime 的核对"与"真正执行 Run 的 Core"并非同一装配/同一 `pipeline_defaults` 行（seed 时机或 data-root 不一致）。这层**环境/证据**问题本身不是代码 bug，但它正是缺陷 1+2 制造出来的可用性陷阱。

---

## 9. 未确认项（需下一轮补一次最小证据）

| 项 | 为什么缺 | 需要什么 |
|---|---|---|
| GLM 轮那次失败 `StepRun` 的 `error_detail` | 未落盘（`verification/L2-CORE-E2E/` 无 glm 轮 run json） | `l2-glm` 的 `GetTaskProjection` + StepRun detail，或 Core stderr 的 `[core.run]` 行 |
| `_chain` vs `resolve` vs `require_configured` 的归属 | 只能靠 detail 文本区分（§2.2 的 stage 字段） | 同上（`stage='ocr'` / `'resolve'` / `'configure'` 一眼定案） |
| 该 Core 装配期的 `pipeline_defaults.settings_json` 内容 | 该 work-root 未提供 dump | `work-root-glm/app.db` 的 `settings_json`/`provider_bindings_json` 只读导出（脱敏） |

> 有上述任一项即可把 §6 的推论从"代码级不可能"升级为"现场已证"。

---

## 10. 复现（只读，无外部 key、无网络）

```
C:\Python314\python.exe "G:\CODEX\New Manga.workspace\L2-VISION-OCR-DIAG\probe_registry.py"
C:\Python314\python.exe "G:\CODEX\New Manga.workspace\L2-VISION-OCR-DIAG\probe_e2e.py"
```

- `probe_registry.py`：只建 registry，打印四种形状的 `aliases / status / resolve`。
- `probe_e2e.py`：真实 DB（schema v14 迁移）+ 真实 `SqliteSnapshotProvider` 行 + 真实 `build_provider_runtime` + 真实 `build_production_pipeline`，用假 transport 顶替 HTTP（把 HTTP 200 + vision JSON 固定返回），跑 `translate_all` page scope。
- 两个脚本都写在仓外 workspace，未改动仓库任何文件。

---

## 附：本次诊断引用的关键行号索引

| 主题 | 位置 |
|---|---|
| 实例一次性装配 | `src/bootstrap/core_assembly.py:1419-1426` |
| 装配期读 settings/bindings | `src/bootstrap/core_assembly.py:770-784`、`727-767` |
| 无 live reload 的口径 | `src/bootstrap/core_assembly.py:1459-1462`；`src/bootstrap/settings_commands.py:1003-1020` |
| vision 槽注册（requirements 定值） | `src/infrastructure/providers/runtime.py:628-639`、`470-483` |
| profile→槽投影/别名 | `src/infrastructure/providers/runtime.py:418-467`、`378-403` |
| 就绪状态机 | `src/infrastructure/providers/registry.py:178-250` |
| resolve 的就绪门 | `src/infrastructure/providers/registry.py:262-293` |
| 冻结路径（含静默跳过） | `src/infrastructure/providers/registry.py:353-454`、`366-372` |
| 冻结只影响 config 重建 | `src/infrastructure/providers/registry.py:456-502` |
| planning 探针（字符串旁路） | `src/infrastructure/providers/registry.py:504-524` |
| 码→异常的分派失真 | `src/infrastructure/providers/registry.py:542-563` |
| 需求探测与首失败映射 | `src/infrastructure/providers/dependencies.py:130-158`、`161-178`、`181-206` |
| ocr 处理器与链路 | `src/infrastructure/providers/handlers.py:522-591`、`1160-1166`、`1266-1274` |
| 适配器 | `src/infrastructure/providers/ocr_vision.py:12-14`、`38`、`60`、`71-109` |
| 客户端配置门 | `src/infrastructure/providers/openai_client.py:56-68`、`93-106`、`165-184`、`240-254` |
| 重放 schema | `src/application/tasks/store.py:155-235`（`170`、`210-213`、`223`） |
| 规划门 | `src/application/tasks/service.py:711-712`、`796-804`、`603-615` |
| 命令步骤序 | `src/application/tasks/service.py:93-110` |
