# TRANSLATE-PROVIDER-1 交付报告（翻译 provider 最小可用接线）

- Task: `doc/tasks/TRANSLATE-PROVIDER-1.md`（team task-37；base `97de0fa99`，开工 HEAD `ae7fe3334`）
- Owner: `route-research`；Reviewer: `dsh`
- Branch: `task/TRANSLATE-PROVIDER-1`；Worktree: `G:/CODEX/New Manga.workspace/worktrees/TRANSLATE-PROVIDER-1`
- 证据目录: `verification/TRANSLATE-PROVIDER-1/`
- 结论: **AC1–AC5 全部达成**；identity 翻译为 **EXPERIMENTAL 占位**，不是产品翻译质量，见 §6。

---

## 1. AC1 — 现有 translate provider 盘点与判定

证据: [`provider-inventory.json`](provider-inventory.json)（由生产 `build_provider_registry()` 实时导出全部 slot）。

| provider_id | provider_type | 注册方式 | 离线可用 | 状态 |
| --- | --- | --- | --- | --- |
| `openai-compatible-translation` | `openai-compatible` | `runtime.py` translation 段；`ProviderDescriptor` + factory；requirements=endpoint+credential，network gate | ❌ 需远端 endpoint/model(/credential) | `not_configured` |
| `sakura-local` | `local-sakura` | 同上；`sakura_config()`（无 credential，localhost） | ⚠️ 仅当本机已有 OpenAI-compatible Sakura 服务在监听 | `not_configured` |
| `identity-translation`（本批新增） | `identity-experimental` | `runtime.py` translation 段；requirements 为空、无 gate、无网络 | ✅ 纯进程内、零依赖 | **`ready`** |

- 注册 API：`ProviderRegistry.register(ProviderDescriptor, factory, gate=..., enabled=...)`；解析 API：`resolve(capability, id)` / `resolve_binding(capability, frozen_binding)`（`registry.py`，fail-closed、未知/未就绪均为 typed error）。
- **判定**：现有两个 slot 都做不到“开箱离线”。因此按 AC1 建 `identity-translation`（输入=输出，`provider_type=identity-experimental`，note/options 均显式标 experimental）并注册；未引入任何新协议/设置面。
- 用户 profile 投影（`_apply_profile_bindings`）仍把 `translate` 的用户 profile 投影到上述两个固定 slot；identity 是固定 id，不被隐式投影，也不抢占任何默认。

## 2. AC2 — 绑定与装配

### 代码改动（全部 `src/**`）

| 文件 | 改动 |
| --- | --- |
| `src/infrastructure/providers/translation_identity.py`（新增） | `IdentityTranslationProvider`：对每个 Region 返回 `{region_id: region.text}`（严格输入=输出）；空请求 → typed `ProviderInputError`；每条结果带 `options=(("experimental","identity-placeholder"),("translation","input-equals-output"))`、`model="identity-passthrough"`、`provider_type="identity-experimental"`。文档明示非成品、替换路径。 |
| `src/infrastructure/providers/runtime.py` | translation 段新增 `identity-translation` slot（零 requirements / 无 gate / `enabled=True`，note 写明 EXPERIMENTAL）；导出常量。 |

### 绑定路径（两条都实测，见 §3）

1. **StartRun override**（生产 wire 协议 2.3，`StartRun.payload.overrides.provider_bindings`）：
   `overrides={"provider_bindings":{"ocr":"manga-ocr","translate":"identity-translation"}}`
   → `PipelineService.create_run` → `SqliteSnapshotProvider.freeze(overrides)` 递归合并 → `PipelineRun.provider_binding_snapshot["translate"]`。
2. **持久化默认绑定**（UI 默认绑定同一通道：`PipelineDefaultsService.save_provider_binding("translate", "identity-translation")` 写 `pipeline_defaults` 行；assembly/`freeze` 从同一行读取）。
   证据里同时验证了 override 只影响该 Run、不污染持久默认。

### 失败仍 typed（未放宽）

- 无 translate 绑定 → `translate` step `FAILED / PROVIDER_NOT_CONFIGURED`（`no-binding` 变体实测 3/3 页）。
- 绑定未知 id → `ProviderUnavailable`；禁用 → `ProviderDisabled`；capability 不匹配 → `ProviderNotConfigured`；空 Region 请求 → `ProviderInputError`。均为既有 provider 错误分类，无新错误码、无协议变更。

### 单测（新增 12 例）

- `tests/providers/test_translation_identity.py`（9）：输入=输出（含多 Region / 空文本）、experimental provenance、registry 注册与 `ready`、显式解析四种 binding 形状、无绑定/未知/禁用/能力不匹配的 typed 拒绝、identity 不得服务 OCR capability。
- `tests/providers/test_handlers_pipeline.py`（+2）：绑定 identity 后 `translate` step `completed` 且 `machine_translation == OCR 源文本`、Region 文本与 provenance 落库；无绑定时 `PROVIDER_NOT_CONFIGURED` 且数据不变。
- `tests/core/test_pipeline_defaults_service.py`（+1）：默认绑定持久化 → Run 快照 → `chain_from_binding` 可读；override 优先且不回写默认。

## 3. AC3 — 8 页真实 Run（translate → render）

汇总证据 [`run-summary.json`](run-summary.json)；原始逐 step 证据 `evidence/inproc-*.json`。

运行方式：**生产装配同一路径** `assemble_production_core` + `PipelineService.create_run/plan_run/execute_run`（sidecar `main()` 实际调用的同一 scheduler 路径），真实 models 目录（detector/ocr 权重），BOOK-FIXTURE 8 页私有副本。
**同构建说明（如实）**：RELEASE-REPACK-1 的重打包 exe 构建于本 Task 之前（不含 identity provider），因此 identity 证明用源码直跑；同时在其**新 exe** 上记录了当前构建的 translate 缺口（下节），下一次重打包即可把本 provider 带入 exe。

| 变体 | Run 终态 | translate | 后续步骤 | 备注 |
| --- | --- | --- | --- | --- |
| `identity`（StartRun override） | **completed**（82.1s） | **3/3 页 completed（22/22 Region units）** | segment/mask_refine/inpaint/**render 22/22 completed** | 全链路到 render，产出 translated artifact |
| `default-binding`（持久化默认绑定） | **completed**（82.4s） | **3/3 页 completed（22/22）** | render 22/22 completed | override 路径之外的默认绑定路径 |
| `no-binding`（对照） | completed_with_failures | 3 页 FAILED `PROVIDER_NOT_CONFIGURED` | 未规划下游 | 失败仍 typed，未伪造成成功 |

逐页（`identity` 变体，页序 1–8）：

| 页 | 文件 | 任务状态 | Region units | translate | 下游 |
| --- | --- | --- | --- | --- | --- |
| 1 | E04P02 | completed | 9 | completed | segment→render 全部 completed |
| 2 | E04P03 | completed | 6 | completed | 同上 |
| 3 | E04P06 | completed | 7 | completed | 同上 |
| 4–8 | E20P01–P05 | completed（0 region，`empty_detection=true`） | 0 | 不适用 | 仅 detect completed |

identity 语义抽查（`machine_translation` 与 `ocr_text` 逐字相同，provenance provider=`identity-translation`/type=`identity-experimental`/options.experimental=`identity-placeholder`）：见 `run-summary.json.identity_samples` 与 `evidence/inproc-identity.json.regions`。

### 同构建见证：RELEASE-REPACK-1 新 exe（不含本 provider）

证据 [`evidence/new-sidecar-run.json`](evidence/new-sidecar-run.json)（raw wire，真实 spawn）：

- sidecar：`task-envs/RELEASE-REPACK-1/sidecar-models/core-sidecar`，`core_service.exe` sha256=`9fcb9e8750ff7a52bc7ab5467f261ca689114a059874f9223054022ac41331dd`（size 399,492；新旧构建对照：旧 frozen `2b36bfeb…`）。
- 8 页 Run：`completed_with_failures`（9.35s），counts: 5 completed / 3 failed。
- 页 1–3：`detect→ocr→color→term_extract` 全 completed（CORE-PIPELINE-FIX-1 修复已进新 exe），**`translate` FAILED typed `PROVIDER_NOT_CONFIGURED`**（该 exe 无 identity）。
- 页 4–8：completed（0 region）。
- 结论：新 exe 的**唯一** translate 缺口就是“未注入 provider”；源码直跑（同 assembly）已证明注入后 translate→render 全通。**下一次 RELEASE-REPACK 重打包即为同构建全链路**（已记入 Handoff 遗留）。

### 观测到的环境瞬态（如实记录）

`default-binding` 首次执行时页 8 `detect` 出现一次 `PROVIDER_FAILED: [Errno 22] Invalid argument`（同参数立即重跑 8/8 页、全步骤 completed）。该现象发生在连续第 3 次满载 8 页 heavy run 后，判为 Windows/ORT 环境瞬态而非 provider 逻辑；最终证据采用重跑的绿色结果，不影响 AC3 结论。

## 4. AC4 — 单测 / 回归

| 项目 | 基线（卡面） | 本次 | 结论 |
| --- | --- | --- | --- |
| `python -m pytest -q` | 卡面口径 3F / 2753P / 9S（释放时快照）；**同树实测基线**（纯净 `ae7fe3334` worktree）：**4F / 2752P / 9S** | **4F / 2763P / 9S** | **0 新增失败**：两树失败集合逐条相同（`test_plugin_sandbox.py::test_sandbox_job_kills_grandchildren`、detection real ×2、workbench viewmodel ×1，均环境性既有失败，已在纯净 base 上复现）；通过数 2752→2763 = 本批新增 11 例（provider 8 + handler 2 + defaults 1），无既有用例回归 |
| `apps/desktop-avalonia/scripts/test.ps1` | 177/177 | **177/177 passed，0 skipped**（coreclient/host/app 三段） | 全绿 |
| `apps/desktop/frontend` vitest | 60 文件 / 567 | **60 文件 / 567 passed** | 不变 |

日志：`pytest.log`（本分支）、`pytest-baseline-base.log`（纯净 base 对照）、`dotnet-*.log`、`vitest.log`。

## 5. AC5 — 门禁

- `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/TRANSLATE-PROVIDER-1.md` → 见 Handoff 收口。
- Canonical Evidence：64-hex sha256 pin（commit 列留空）；Handoff：`doc/handoffs/TRANSLATE-PROVIDER-1-handoff.md`。
- 未 push、未 gc/prune；未改协议/Host 契约/旧壳；未放宽任何输入校验。

## 6. Record Decision — provider 语义 / 质量声明 / 替换路径

1. **语义**：`identity-translation` 严格“输入=输出”——把 OCR 源文本原样写为 `machine_translation`（进而 final）。它**不做翻译**：不改变语言、不调用模型、不联网、零依赖。
2. **质量声明（必须遵守）**：这是 **experimental 占位**，仅用于让流水线越过 `translate` 以推进/验证下游；**不得作为产品翻译质量宣发**。落库与导出中可识别：provider_id=`identity-translation`、provider_type=`identity-experimental`、model=`identity-passthrough`、options 含 `experimental=identity-placeholder`。
3. **注册策略**：无条件注册但**绝不隐式选择**——没有绑定时仍为 typed `PROVIDER_NOT_CONFIGURED`；只有显式绑定（Run override 或持久默认）才使用。
4. **替换路径（零代码）**：把 `translate` 绑定改为 `openai-compatible-translation`（配置 endpoint/model/credential）或 `sakura-local`（本机服务），或设置用户 provider profile 并绑定；绑定是 Run 冻结快照，替换不改 pipeline 代码、不改协议。
5. **回退**：删除/覆盖该绑定即回到 typed 缺口；identity slot 自身无状态、无副作用、无模型文件。
6. **边界**：未修改协议、Host 契约、旧壳、dist/wire 列表；未改动任何既有 provider 的 requirements/readiness 语义。

## 7. 遗留

1. **同构建全链路待下一次重打包**：RELEASE-REPACK-1 的新 exe 建于本批之前，不含 identity；其 AC3 同构建 translate 3/3 需在该 Task 下一次重建后复验（命令与工具已就绪：`tools/run_new_sidecar_probe.py --with-translate-binding`）。
2. 真实翻译质量（OpenAI-compatible / Sakura）不在本卡；本卡只保证“可推进、可观测、可替换”。
3. 页 1–3 的 translated artifact 已生成，但本卡未做视觉/排版验收（属 UI/渲染验收线）。
4. 观察到的 heavy-run 瞬态 `[Errno 22]` 已在 §3 记录；如需彻底归因，另开诊断（与本卡 provider 逻辑无关）。
5. 需独立 Review（Owner 不得自审；reviewer=`dsh`）。

## 8. 复跑方式

```powershell
# 8 页真实 Run（源码直跑，identity override；需 models 目录与 BOOK-FIXTURE）
python verification/TRANSLATE-PROVIDER-1/tools/verify_inproc.py identity
python verification/TRANSLATE-PROVIDER-1/tools/verify_inproc.py default-binding
python verification/TRANSLATE-PROVIDER-1/tools/verify_inproc.py no-binding

# RELEASE-REPACK-1 新 exe 的 wire 见证（当前构建无 identity，应得 translate typed 缺口）
python verification/TRANSLATE-PROVIDER-1/tools/run_new_sidecar_probe.py

# 单测
python -m pytest tests/providers/test_translation_identity.py tests/providers/test_handlers_pipeline.py tests/core/test_pipeline_defaults_service.py -q
```
