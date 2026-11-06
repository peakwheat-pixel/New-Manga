---
task: FEA-11-RENDITION-1
title: FEA-11-RENDITION-1 独立实现 Review r1（Core 侧 referenced rendition 图源承接；交付 head a05a419f7）
reviewer: fresh subagent（独立上下文；未参与实现/返修；只读）
session: e79484b2-5994-4ac5-9e44-6ac5d0c2edf8（DSH fresh subagent）
parent_session: session-c2883c5f-dcf8-400d-b161-9c84f562486a
reviewer_kind: subagent
date: 2026-11-06
repo: G:\CODEX\New Manga
branch: main
reviewed_head: a05a419f7（代码+测试；693ab469b + a05a419f7）
reviewed_docs: 75dace4c2/c7c072b39
scope_base: 4360fbcdb
head_at_review_end: c7c072b39d38b348f499ecf74e083a0df4d2d325（评审期未前进；工作树 clean）
decision: approved
findings: P0=0/P1=0/P2=1/P3=8
---

# FEA-11-RENDITION-1 独立实现 Review r1

> **结论先行：`approved`（P0=0 / P1=0 / P2=1 / P3=8）。**
>
> - **代码正确性：通过。** `pipeline.py` 的 referenced 准入确实复用冻结的 C-15 §4.1 `V`（`page_visibility = repository.get_page`，`library.py:508-524` + `:413-429`）与唯一 `read_gate`，未手写第三份 V 谓词；managed 页与遗留混合页在目标进入层保持既有门槛（逐行未变）；`TargetSnapshot.metadata` 仍为固定 5 键（`context_pages` 为既有 `pinned` 投影，非本卡新增）；`source_gate_reader`/`page_visibility` 未注入时 fail-closed。`_ManagedPageImageSource` 的 referenced 分支只经 `prepare_referenced_rendition` → `render_prepared_rendition`，**未发布 catalog、未写 `rendition_cache`、源码不含 `"cache_key"` 字面**；所有 `SourceImportError` 折叠为固定安全文本 `ProviderInputError`（`INVALID_INPUT`），无路径/locator/entry 名。`_ensure_input_guard` 位于 `region_creator` **之前**，digest 来自 `step_run.input_refs["__fea10_guard__"]`，不一致即 `INPUT_REVISION_CHANGED` 且零 region/revision/lineage 写；`None`/无 ref 时保持旧行为。范围边界干净：`4360fbcdb..a05a419f7` 仅 6 个 allowed 文件；`doc/plan`/`doc/contracts`/`schema.py`/`apps/`/依赖/`core_service.py`/`conftest.py`/`test_source_lineage_run.py` 零 diff。
> - **测试真实性与判别性：通过。** 3 个新文件 37 用例全部使用真实 Pillow 像素（A=30×20 / B=12×7 / C=20×9，尺寸与内容双重判别）、真实 zip、真实 HMAC grant、真实 v8 库与真实 production 类；**无 `_StubImages`**（唯一命中是 docstring 说明与一个从不调用的 `_StubStyleAnalyzer` 非图像端口替身）。我独立做了 **2 处破坏性复跑**（I-1 准入、I-3 gate），分别 3 failed / 4 failed，恢复后文件 sha256 与破坏前逐字节相同、`git status --short` 为空、37 用例复绿（§8）。
> - **AC：AC-R1…AC-R7 全部 `<<MET>>` 成立**（逐条证据见 §4）。**无「referenced 页 Run 产品可用」「L10 全修」「FEA-11 AC 回填」类夸大**；L-R1 负向用例真实存在。
> - **门禁：可复现。** `tests/fea11` 145 passed；三新文件 37 passed；全量 pytest 一次 **3249 passed / 10 skipped**（EXIT=0）；全量 .NET **1527/0/86**（EXIT=0）；pins 18/18；`check.ps1` PASS(3 warnings)；API inventory EXIT=0；`tests/providers` 559/4。全量 pytest 另一次运行命中**既有 flaky** `tests/infrastructure/test_plugin_sandbox.py::test_sandbox_job_kills_grandchildren`（与本卡无关，隔离复跑 2 次通过；见 §6.1）。
> - **P2 唯一项是证据/limitation 文本问题（R1-01，L-R10 与代码/测试不符），不改代码即可在 closeout 前更正**；其余 8 条为 P3（证据日志/计数/manifest/诊断文本/既有 gate 分歧/flaky 环境项）。**不需要返修生产代码或测试。**

---

## 1. 基线核验（评审开始时 / 结束时）

| 项 | 实测 | 证据 |
|---|---|---|
| HEAD | `c7c072b39d38b348f499ecf74e083a0df4d2d325`（= Lead 的 in_review 文档提交） | `git rev-parse HEAD` |
| 分支 | `main` | `git branch --show-current` |
| 工作树（开始） | **clean**（`git status --short` 空） | 实测 |
| 工作树（结束） | **clean**；全量 .NET 重写的 `verification/FEA-09/logs/wire-redacted.ndjson` 已 `git checkout -- verification/FEA-09` 恢复 | 实测 + §6 |
| 被审代码范围 | `4360fbcdb..a05a419f7`：`693ab469b`（src 3 文件）+ `a05a419f7`（3 个新测试文件，37 用例），共 6 文件 / +2056 −33 | `git diff --stat` |
| `delivery_head` | 卡面 `a05a419f7f6c6023786b61d9f11d8f6cdd0eb800` = 实测 head | 卡 frontmatter、`git rev-parse a05a419f7` |
| 证据/卡/Handoff 提交 | `75dace4c2`：9 个证据文件 + 卡 + Handoff（`git ls-tree -r 75dace4c2 -- verification/FEA-11-RENDITION-1` 命中全部 9 个 blob；`git diff 75dace4c2 -- verification/FEA-11-RENDITION-1` 为空） | 实测 |
| 其上的 in_review 提交 | `c7c072b39`：仅 `doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/TASK_LEDGER.md`、`doc/tasks/FEA-11-RENDITION-1.md`（Lead 文档面；`src`/`tests`/`verification`/契约零 diff） | `git show --stat c7c072b39`、`git diff --name-only 75dace4c2..HEAD` |
| 解释器/工具 | CPython 3.14.6（`C:\Python314\python.exe`）、Windows 11 10.0.26300、PowerShell 7、`dotnet test`（net9.0） | 复跑输出 |

> 说明：`4360fbcdb..HEAD` 另含 Lead 的 `doc/STATUS.md`/`doc/REBASELINE_PLAN.md`/`doc/TASK_LEDGER.md` 变更（`c7c072b39`）；按任务说明只审卡面与代码交付，Lead 文档面不计入实现审查。

---

## 2. 代码正确性（A）

### 2.1 `src/infrastructure/sqlite/pipeline.py`

| 检查点 | 结论 | 证据 |
|---|---|---|
| referenced 目标进入复用 C-15 §4.1 V | **成立**：注入 `page_visibility`（`pipeline.py:809`，assembly 实现为 `repository.get_page(page_id) is not None`，`core_assembly.py:1751-1753`）；`get_page` 的 WHERE 即 `_visible_page_where`（`library.py:508-524` + `:413-429`：`source_mode='referenced'` ∧ `integrity_status='complete'` ∧ `source_hash IS NOT NULL` ∧ `width/height>0` ∧ `EXISTS(healthy binding ∧ verified_digest=entry.content_digest)`） | 源码 + 复跑 |
| 是否手写第三份 V 谓词 | **否**：唯一新增谓词 `_ensure_referenced_target_readable`（`:1586-1604`）只是「调用 visibility + 调用 gate」，没有重复 SQL；目标面没有第二段可见性 SQL | 源码；`gates.py:240-243` 对 `def read_gate(` 计数为 1 |
| 唯一 `read_gate` | **成立**：`core_assembly.py:1244-1261` 单一定义；三处消费：`source_guard`（`:1766`）、provider（`:1684`）、target catalog（`:1750`）；装配级 identity 断言 `gates.py:226-244` | 源码 + `gates.py` 实测 |
| page 准入（纯 referenced） | 仅当 `source_mode='referenced' ∧ managed_original_ref IS NULL` 走新准入（`pipeline.py:1446-1460`）；新准入 = `source_hash` 非空 + V 为真 + gate=open | 源码；`test_source_rendition_run.py` 5 用例 |
| page 准入（managed / 遗留混合页） | **逐行未变**：`elif` 分支仍为 `source_hash is None or managed_original_ref is None → TARGET_NOT_FOUND "page … has no managed original"`（`:1461-1462`）；managed 与混合页不查 V/gate | 源码对照 base |
| region 准入 | SQL 改为 `(managed_original_ref IS NOT NULL OR source_mode='referenced')` 并**保留** `width/height` 与 `source_hash`（`:1507-1509`）；纯 referenced 页在 `_region_from_id`/`_ensure_lineage_readable` 之前做同一 V+gate（`:1520-1526`） | 源码；`test_region_scope_with_null_dimensions_…` |
| `metadata` 键集合 | **不变**（`source_filename`/`managed_original_ref`/`source_hash`/`lineage_hidden_regions`/`commit_guard`，`:1490-1496`）；`context_pages` 由既有 `pinned` 投影添加（`pipeline.py:1679`，base 已有）→ prepared digest 形状不变 | 源码 + `test_pure_referenced_page_enters_page_scope_with_an_unchanged_metadata_shape` |
| `None` fail-closed | `visibility`/`gate` 任一不可调用或 `source_hash` 空 → `TARGET_NOT_FOUND` 历史 detail（`:1599-1600`）；region 侧同样（`:1524-1525`，detail 恢复为 `region_id`） | 源码；既有单测不改即绿 |
| 混合页 V 假风险 | 混合页仍走旧门槛：V 假（如 digest 不符/尺寸 NULL）**仍可进入目标层**；provider 端因 `get_page`(V) 返回 None 而 typed 拒绝，像素不解码（只读探针实证，见 §9.3）。属 A-1 已接受决策，仅作 limitation 精度问题（R1-01） | 只读探针（PURE refused；MIXED target-admitted → detect `INVALID_INPUT`） |

### 2.2 `src/bootstrap/core_assembly.py`

| 检查点 | 结论 | 证据 |
|---|---|---|
| referenced 像素源只用唯一选择入口 | **成立**：`_referenced_page_image`（`:444-501`）= gate → `prepare_referenced_rendition(page_id, repository=…, access=…)` → `claim_secret_for_binding(...)` → `render_prepared_rendition(..., image_decoder=…, document_raster=…, password=…)` → PNG→Pillow | 源码 |
| 未发布 catalog / 未写 rendition_cache / 未用 `prepared["cache_key"]` | **成立**：provider 类与 `_referenced_page_image` 源码无 `rendition_cache`/`cache_key` 的代码引用（仅 docstring 说明）；`"cache_key"` 静态断言在 `test_provider_reuses_the_single_selection_function_and_never_caches`；`RenditionCache.acquire` 探针 0 次 | 源码 + 测试 |
| 失败 typed 且文本安全 | **成立**：所有 `SourceImportError` → `ProviderInputError(f"{_REFERENCED_REFUSAL} ({error.code})")`（`:489-492`），固定文本 `referenced page source is not readable`；gate 拒绝只附状态；PNG 解码失败也只带 page_id。无绝对路径/locator/entry 名 | 源码 + `test_refusal_detail_never_leaks_a_path_or_entry_name` |
| managed 分支逐字节行为 | 对可构造 `Page` 的 managed 页：`getattr(page,"source_mode","managed")` 为 `managed` → `ref=getattr(...,None)` 等价旧 `page.managed_original_ref` → 同一 `ManagedRootTrust.read_bytes`/错误文本。**唯一有意的行为差异**是 F7：`PageView`（无/空 ref）从 `AttributeError` 变为 typed `INVALID_INPUT`（改善，不是回归）；卡面「逐字节不变」在这一点上措辞不严谨（P3 观感，不判缺陷） | 源码 + `test_managed_page_*` + `tests/providers` 559/4 |
| `read_gate` 三处共用 | **成立**：`run_source_guard` 改用 `read_gate` 的 `unavailable`/`pending`（`:1766-1772`），原 `binding["status"]` 与 `gate_of_binding` 分支语义保持；provider（`:1684`）与 target（`:1750`）同一对象；`gates.py:232-243` 断言 `deps.images._read_gate is catalog.source_gate_reader`、`source.count("def read_gate(")==1` | 源码 + 测试 |
| `page_visibility` 是 repository V 读 | **成立**：lambda 只调用 `repository.get_page`；未新增 SQL | 源码 |
| 与 `core_service` 既有 gate 的分歧 | `read_gate` 对「healthy binding 无 publication 行」返回 open；`core_service._assert_source_sync_gate`（`core_service.py:5072-5103`）在 `previous_binding_id` 有 publication 时 fail-closed。属既有两份 gate 的历史分歧（本卡 Out 明确不碰 `core_service.py`），但 provider/target 首次可达 → 见 R1-06（P3） | 源码对照 |
| managed 只读没有被新分支污染 | managed 页不调用 `read_gate`/`source_access`；`_ForbiddenAccess`+`_forbidden_gate` 探针在 `test_managed_page_reads_the_managed_copy_and_never_touches_grant_or_gate` 通过 | 测试 |

### 2.3 `src/infrastructure/providers/handlers.py`（I-4）

| 检查点 | 结论 | 证据 |
|---|---|---|
| 复核在 `region_creator` 之前 | **成立**：`handle_detect` 在 `provenance = detection.provenance()` 之后、`region_creator(...)` 之前调用 `self._ensure_input_guard(step_run, unit)`（`:403-410`）；前面的提前返回路径（复用 live region、空检测）均**不写** region | 源码 |
| 比对来源 | `step_run.input_refs["__fea10_guard__"]`（`application/tasks/service.py:865-866` 用 `snapshot_digest(metadata["commit_guard"])` 记录）与 `deps.commit_guard(unit.page_id)`（assembly 注入同一个 `run_guard_value`，`core_assembly.py:1607-1618,1705`）经**同一个** `snapshot_digest` 比较 | 源码 |
| 不一致结果 | `StepExecutionError("INPUT_REVISION_CHANGED", …)`（`:478-482`）→ 零 region/revision/lineage；`test_binding_change_between_decode_and_region_write_is_input_revision_changed` 断言三表计数均为 0；`gates.py` 4 个 handler 级用例 | 源码 + 测试 |
| `None`/无 ref | 依赖为 `None` 或 ref 缺失 → 直接返回（旧行为）；两个用例分别覆盖 | 测试 |
| 装配注入 | `commit_guard=run_guard_value`（`core_assembly.py:1705`）；`build_production_handlers` 参数默认 `None`（唯一调用方是 assembly，无位置参数破坏） | 源码 |

### 2.4 边界

- `git diff --name-only 4360fbcdb..a05a419f7` = `{src/bootstrap/core_assembly.py, src/infrastructure/providers/handlers.py, src/infrastructure/sqlite/pipeline.py, tests/fea11/test_source_rendition_{gates,run,source}.py}` ⊆ 卡面 `allowed_paths`。
- `4360fbcdb..75dace4c2` 的 17 个文件全部在 `allowed_paths`（卡/Handoff/证据 + 上述 6 个）。
- **禁止面零 diff**（实测空）：`doc/plan`、`doc/contracts`、`src/infrastructure/sqlite/schema.py`、`apps/`、`pyproject.toml`/`requirements*.txt`、`src/bootstrap/core_service.py`、`tests/fea11/conftest.py`、`tests/fea11/test_source_lineage_run.py`。
- `src/infrastructure/sqlite/library.py` 未改（allowed 但未用）。

---

## 3. 测试真实性与判别性（B）

### 3.1 真实性

- 3 个新文件（37 用例）**全部**使用真实构件：`Image.new/putpixel` 生成真实 PNG（`test_source_rendition_source.py:84-95`）、`write_zip` 真实 zip（`conftest.py:141-149`）、`mint_grant` 真实 HMAC 签名 grant（`conftest.py:152-229`）、真实 v8 migrations 库、真实 production 类（`_ManagedPageImageSource`、`ProductionHandlers`、`build_production_pipeline`、`assemble_core_services`）。
- **像素断言无 stub**：`_StubImages` 仅出现在 docstring（说明「刻意不用」）；`gates.py` 的 `_StubStyleAnalyzer` 是 `SourceStyleService` 的非图像端口替身（从不被调用），不参与像素断言。`RecordingDetector`/`RecordingOcr` 是**记录型**适配器，接收的是 production 图源输出的真实 frame/crop。
- A/B/C 三重判别：A=30×20（managed 旧副本，左上黑块）/B=12×7（当前 binding entry，右下蓝块）/C=20×9（旧 entry，黄底品红块），尺寸与像素**双重不同**；`test_repointing_the_binding_changes_the_pixels` 重指 binding 后像素随 binding 变为 C。`ManagedRootTrust.read_bytes` 哨兵在 `test_mixed_page_never_reads_the_stale_managed_copy` 与 `test_run_detector_receives_the_binding_rendition_pixels` 中证明混合页不读旧 managed 副本。

### 3.2 测试名 → AC 对应（`--collect-only` 实测 37 个）

| AC | 用例（节选；文件内全部命中） | 计数 |
|---|---|---|
| AC-R1 | `test_pure_referenced_page_enters_page_scope_with_an_unchanged_metadata_shape`、`test_mixed_chapter_scope_expands_to_managed_and_referenced_pages`、`test_region_scope_admits_a_referenced_page_region`、`test_unverifiable_referenced_pages_stay_target_not_found`、`test_region_scope_with_null_dimensions_stays_a_stable_target_not_found` + `gates.py::test_pending_gate_blocks_the_real_run_target_and_opens_when_acknowledged` | 5 + 1 |
| AC-R2 | `test_page_frame_pixels_…`、`test_page_png_is_…`、`test_region_crop_is_taken_in_the_rendition_coordinate_system`、`test_mixed_page_never_reads_…`、`test_repointing_the_binding_changes_the_pixels`（source.py，5）+ `test_run_detector_receives_…`、`test_detect_regions_register_native_lineage_…`（run.py）+ `gates.py::test_real_assembly_provider_reads_the_binding_rendition_end_to_end` | 5 + 2 + 1 |
| AC-R3 | `test_managed_page_reads_the_managed_copy_and_never_touches_grant_or_gate`、`test_managed_page_without_a_managed_original_stays_the_historical_refusal` + run.py 两处 metadata 键集合断言 | 2 + 2 |
| AC-R4 | source.py 8 用例（pending/unavailable gate、missing/revoked grant、detail 无泄漏、disappeared、corrupt、budget）+ run.py 2 个 binding-change + `gates.py` 4 个 handler 级 + 1 个真实 commit guard | 8 + 2 + 5 |
| AC-R5 | `test_provider_reuses_the_single_selection_function_and_never_caches` + `gates.py::test_real_assembly_wires_one_gate_object_into_every_consumer` | 1 + 1 |
| AC-R6 | `test_run_target_face_never_introduces_a_source_star_error_code` + 门禁日志 | 1 |
| AC-R7 | `test_run_without_a_live_source_grant_is_typed_and_writes_nothing` + 门禁 | 1 |

> 卡面/EV 的**计数**有两处偏差（见 R1-05）：AC-R2 标「source.py（8 用例）」实为 5；AC-R4 标「source.py（10 用例）」实为 8。**测试名与行为均真实存在**，不影响 AC 判定，属证据计数错误。

### 3.3 判别性（我独立复跑，详见 §8）

| 破坏点 | 方法 | 结果 |
|---|---|---|
| I-1 referenced 准入 | 在 `_ensure_referenced_target_readable` 首行插入 `return` | **3 failed**（`test_unverifiable_referenced_pages_stay_target_not_found`、`test_region_scope_with_null_dimensions_…`、`test_pending_gate_blocks_…`），EXIT=1 |
| I-3 唯一 gate | `read_gate` 恒返回 `"open"` | **4 failed**（gate 三态、pending 目标展开、真实 commit guard、真实 provider 读图），EXIT=1 |

两次破坏均**恢复**：文件 sha256 与破坏前相同、`git status --short` 为空、37 用例复绿。

---

## 4. AC 判定（C）

| AC | 判定 | 复核证据 | 备注 |
|---|---|---|---|
| **AC-R1** 目标进入（page/chapter/region） | **MET** | `pytest tests/fea11` 145 passed；`test_source_rendition_run.py` 5 用例 + `gates.py` pending-gate 真实装配；我的只读探针确认纯 referenced NULL 尺寸在 page-scope 被 `TARGET_NOT_FOUND "page pr has no readable source"` 拒绝（测试断言一致） | 反向 V 假拒绝成立（integrity≠complete / digest 不符）；`current(page_id)` 返回快照由 `test_pure_referenced_page_…` 断言；卡面「retryable 稳定」无法直接断言——`PipelineError` 只有 `code`/`detail`，无 `retryable` 成员（R1-05 一并记录） |
| **AC-R2** 像素来自当前 binding 的真实 rendition | **MET** | 真实 A/B/C + 真实 zip/grant + 真实 `_ManagedPageImageSource`；`page_frame`/`page_png`/`region_crop` 尺寸与像素只匹配 B；混合页 `ManagedRootTrust.read_bytes` 哨兵；记录型 detector/OCR；detect 产出的 `source_revision_lineage` 行 binding=`pb-pr`、provenance=`native`；重指 binding 后像素=C | 判别性 case B（删 referenced 分支）经实现者自检 4 failed，我另以 I-1/I-3 破坏复跑佐证；run 级 guard 为行为等价复刻，见 R1-08 |
| **AC-R3** managed 零回归 | **MET** | metadata 5 键 + 既有 `context_pages`；`_ForbiddenAccess`/`_forbidden_gate` 探针；`tests/providers` **559 passed/4 skipped**（我实测）；`tests/fea11` 145 | 「逐字节不变」措辞在 F7 PageView 路径上不严格（见 §2.2），但属改善 |
| **AC-R4** typed 拒绝与零写 | **MET** | ①`RUN_STALE_PREVIEW`；②⑤`INPUT_REVISION_CHANGED` + region/revision/lineage 三表 0 行；③无/吊销 grant 读图前 `INVALID_INPUT` + `SOURCE_ACCESS_DENIED`/`SOURCE_GRANT_REVOKED`，`read_entry_bytes` spy 0 次；④pending/unavailable 目标展开 `TARGET_NOT_FOUND`、detector 0 次；⑥disappeared/corrupt/budget typed | ①⑤ 的 binding 切换均由测试主动制造；⑥「entry 消失」走 V 假（页面不可读）路径，不是「prepare 后条目消失」的独立场景（可接受） |
| **AC-R5** 不建第二套选择规则 | **MET** | spy `prepare_referenced_rendition` 恰 1 次，选择元组与直接调用逐字段相等；`RenditionCache.acquire` 探针 0 次；`media_artifacts`/`rendition_cache` 0 行；`"cache_key"` 不在 provider 源码 | resolve 面与 provider 共用同一函数（`resolve.py:47`）；assembly 侧 `source_read_refs` 与 resolve 面同一 registry（`core_assembly.py:1293,1903`；`core_service.py` 经 `self._core.source_read_refs`） |
| **AC-R6** 零契约/schema/依赖/wire 漂移 | **MET** | 禁止面 diff 空（实测）；pins 18/18；API inventory EXIT=0；依赖文件空 diff；`test_run_target_face_never_introduces_a_source_star_error_code` | 另核 `c7c072b39` 只动 STATUS/PLAN/LEDGER/卡面 |
| **AC-R7** 门禁、证据与「不夸大」 | **MET** | 全量 pytest **3249/10**（EXIT=0，我实测）；fea11 145；.NET **1527/0/86**（EXIT=0）；check PASS(3 w)；scope diff ⊆ allowed；EV/Manifest/Handoff 齐全；L-R1 负向用例存在；Handoff 明写 L-R1/L-R2、未宣称产品级可用、未回填 FEA-11 AC | 一次全量 pytest 命中**既有 flaky**（§6.1）；EV/Manifest 的 FEA-09 恢复归因与「尾注」表述不实（R1-02），但最终 clean 状态成立 |

### 4.1 limitation L-R1…L-R10 与代码事实

| Limitation | 与代码事实 | 说明 |
|---|---|---|
| L-R1 无 Run grant 通道 | ✅ | 负向用例 `test_run_without_a_live_source_grant_is_typed_and_writes_nothing`；commit guard 仍要 live grant（`gates.py:286-321`） |
| L-R2 加密源 typed | ✅（本卡无测试） | provider 对加密源会经 `claim_secret_for_binding`→`render_entry_png` 得 `SOURCE_PASSWORD_REQUIRED` 并被折叠为 `INVALID_INPUT`+detail；**无本卡加密 fixture**，属 §9 未验证项 |
| L-R3 章节/书范围行为变化 | ✅ | `test_mixed_chapter_scope_…` |
| L-R4 EXIF 方向 | ✅（未测试） | `reader.py:174` 有 `exif_transpose`；无本卡 EXIF fixture |
| L-R5 混合页按 binding 图 | ✅（部分） | provider 确实按 binding；目标层确实不查 V/gate；但**未写明 V 假混合页会进入目标层后在 provider typed 拒绝**（R1-01 一并更正） |
| L-R6 detect region 写在 step commit 外 | ✅ | I-4 只缩小窗口 |
| L-R7 不走 rendition_cache | ✅ | 源码/测试 |
| L-R8 错误码沿用既有 family | ✅ | 静态用例 + 源码 |
| L-R9 快照无 binding 观测 | ✅ | metadata 键集合断言 |
| L-R10 NULL 尺寸 | ❌ **不准确** | 卡面「page-scope 可能可进入」与 Handoff「page-scope 可进入（像素由解码得出）」均不成立于纯 referenced 页（V 为假 → page-scope 也 `TARGET_NOT_FOUND`，测试同样断言）；混合页可进入目标层但 provider 端 typed 拒绝、像素不解码。见 R1-01（P2） |

### 4.2 A-1 混合页不对称（Lead 已接受决策）

- 核查结论：**纯 referenced**（`managed_original_ref IS NULL`）走 V+gate；**遗留混合页**在目标进入层保持旧门槛（不查 V/gate）；provider 对任何 `source_mode='referenced'` 页都按 binding 图读取，binding 不可用/V 假时 `get_page` 返回 None → `ProviderInputError`（fail-closed，绝不回退旧 managed 图）。**不据此判 AC-R1 未满足。**
- 该不对称在 L-R5 中被描述为「Run 目标进入层对混合页保持既有门槛（不查 V/gate）」，**准确但不完整**；未登记的后果是「V 假的混合页仍能进入目标集，Run 在 detect 处 typed 失败（detail 误导为 has no managed original），不产生错误像素」。我以只读探针实证（§9.3），归入 R1-01/R1-07（P2/P3，非阻塞）。

---

## 5. Findings（P0=0 / P1=0 / P2=1 / P3=8）

| ID | 级别 | 文件/行 | 问题 | 证据 | 建议 |
|---|---|---|---|---|---|
| **R1-01** | **P2** | `doc/handoffs/FEA-11-RENDITION-1-a05a419f7.md:65`；`doc/tasks/FEA-11-RENDITION-1.md:158` | **L-R10 与代码/测试事实不符**：纯 referenced 页 `width/height` NULL 时 V 为假，page-scope 亦被 `TARGET_NOT_FOUND` 拒绝（卡面 AC-R1 的反向断言与测试 `test_region_scope_with_null_dimensions_…` 都只覆盖拒绝）；Handoff 却写「page-scope 可进入（像素由解码得出）」。混合页可进入目标层，但 provider 因 V 读返回 None 而 typed 拒绝，**像素并未解码**。这是 canonical evidence 中的错误 limitation，closeout 会被引用。 | 我的只读探针：PURE → `TARGET_NOT_FOUND page pr has no readable source`；MIXED → target-admitted，detect `INVALID_INPUT "page 'pr' has no managed original"`；`tests/fea11/test_source_rendition_run.py:470-475` | closeout 前把 L-R10 改为「纯 referenced：page/region-scope 均拒绝；混合页：目标层可进入、provider typed 拒绝且不解码」，Handoff 同步；**不需改代码** |
| **R1-02** | P3 | `verification/FEA-11-RENDITION-1/EV.md:35`；`verification/FEA-11-RENDITION-1/RESOURCE-MANIFEST.json:90` | 声称 FEA-09 恢复见 `gates-full-pytest.log`「尾注」，但该日志**无头部/EXIT/恢复记录**（只有 `3249 passed` 汇总 + QML stderr）；且该 tracked 文件实际由 **.NET** `WireLogSourceRedactionTests`（`apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/WireLogSourceRedactionTests.cs:33`）重写，**不是全量 pytest**（卡/EV 归因错误）。最终 clean 状态事实成立。 | 我跑 .NET 后 `git status` 出现 `M verification/FEA-09/logs/wire-redacted.ndjson`，`git checkout -- verification/FEA-09` 后 clean；`git diff` 显示追加 1 行；仓库历史（FEA-10/FEA-12 Handoff）同样记录为 .NET 重写 | 更正 EV/Manifest 的归因与「尾注」表述；恢复证明指向 `G:\CODEX\New Manga.workspace\FEA-11-RENDITION-1\final-scope-validation.log`（HEAD=75dace4c2、worktree status 空）或补一条含命令/EXIT 的恢复日志 |
| **R1-03** | P3 | `verification/FEA-11-RENDITION-1/logs/gates-full-pytest.log`、`logs/gates-dotnet.log` | scope-r1 §6 AC-R7 要求门禁日志含 shell/解释器头与 EXIT；这两份**没有**（`gates-feature.log`/`gates-governance.log` 有）。 | 日志首尾实测 | closeout 时补 header/EXIT 或注明原始命令、时间与退出码 |
| **R1-04** | P3 | `verification/FEA-11-RENDITION-1/RESOURCE-MANIFEST.json:17-59` | manifest 声明仓外隔离根「9 文件」+ 聚合 sha `c925f360…`；实际目录现有 **10 个文件**（多出 `final-scope-validation.log`，19:41:47，HEAD=75dace4c2，worktree status 空），集合/聚合已与现状不符。9 个已列文件的 sha256 **逐一匹配**。 | `Get-ChildItem` 实测 10 个文件；per-file sha 全部匹配 | closeout 时更新 manifest（登记第 10 个文件并重算聚合）或移动/删除该文件并如实说明 |
| **R1-05** | P3 | `doc/tasks/FEA-11-RENDITION-1.md:119,120,122`；`verification/FEA-11-RENDITION-1/EV.md` §4 | AC 证据**计数错误**：AC-R2 标「source.py（8 用例）」实为 5（另 2 个在 run.py、1 个在 gates.py，卡面又另行列出 → 重复计数）；AC-R4 标「source.py（10 用例）」实为 8（run 2 + gates 5 另列）。另 AC-R1 的「message/retryable 稳定」无法断言（`PipelineError` 仅 `code`/`detail`）。测试名与行为真实存在。 | `--collect-only`：16/12/9=37；逐条映射 | 修正卡面/EV 计数与措辞（不改代码） |
| **R1-06** | P3 | `src/bootstrap/core_assembly.py:1244-1261`；`src/bootstrap/core_service.py:5072-5103` | 新 `read_gate` 对「healthy binding 但无 publication 行」返回 `open`；resolve 面 `_assert_source_sync_gate` 在 `previous_binding_id` 有 publication 时 fail-closed（新 sync binding 无 gate = 损坏）。同一 binding 在两个读面语义不一致；本卡 Out 明确不碰 `core_service.py`，provider/target 首次可达该分歧。 | 两处源码对照；`schema.py` 唯一索引；无测试覆盖该损坏形态 | 登记为 limitation 或后续卡统一 gate（补 previous-binding 链 fail-closed）；本卡不改 |
| **R1-07** | P3 | `src/bootstrap/core_assembly.py:413-423,549-551` | 诊断文本：V 为假的 referenced 页（NULL 尺寸/摘要不符的混合页）在 provider 端报 `page 'pr' has no managed original`，语义误导；`page_png` docstring 仍写「whole Managed Copy page」。 | 探针 step detail；源码 | 更新 docstring；V 假时给固定 typed 文本以区分「源不可读」（禁路径安全要求不变） |
| **R1-08** | P3 | `tests/fea11/test_source_rendition_run.py:226-249`；`doc/tasks/FEA-11-RENDITION-1.md:121` | run 级像素 E2E 使用测试内**行为等价复刻**的 `run_source_guard`（assembly 内闭包不可导入，模块 docstring 已自述），不是生产闭包本身；真实装配的 identity/guard 由 `gates.py:226-321` 覆盖。卡面「真实 production pipeline + `run_source_guard` 接线」的表述**强于实际证据**。 | 源码阅读 | 卡面/EV 注明「run 级用行为等价复刻 + assembly 级 identity 测试」，或后续抽公共函数直测 |
| **R1-09** | P3（环境，非本卡） | `tests/infrastructure/test_plugin_sandbox.py:384-422` | 全量 pytest 命中**既有 flaky** `test_sandbox_job_kills_grandchildren`（测试内已注 `FLAKY-PYTEST-1`）；一次全量 `3248 passed / 1 failed / 10 skipped`。隔离复跑：单文件 `1 failed/15 passed`，再单测连续 2 次 `1 passed`。另：第一次后台全量 EXIT=1 的失败明细因我只保留末 30 行而**未捕获**，无法归因（很可能同一 flake，但不能证明）。**本卡零 plugin 改动，不是本卡回归**。 | 三次全量 + 隔离复跑记录（§6.1） | Lead 集成验证时按既有「首跑/复跑」惯例记录；不要把该 flake 归因本卡 |

---

## 6. 门禁实测（before → after）

| 门禁 | 命令 | Before（Lead 基线/卡面） | 我的实测 After | 判定 |
|---|---|---|---|---|
| `pytest tests/fea11` | `C:/Python314/python.exe -m pytest tests/fea11 -q -p no:warnings --tb=short` | 108 passed | **145 passed**（8.04 s）EXIT=0 | PASS |
| 三个新测试文件 | 同解释器，三文件显式列出 | — | **37 passed**（1.74 s）EXIT=0 | PASS |
| 全量 pytest（第 1 次，后台） | `python -m pytest tests -q -p no:warnings --tb=short` | 3212 passed / 10 skipped | **EXIT=1；失败明细未捕获**（输出仅保留末 30 行；不可归因，见 §6.1） | 不可判定 |
| 全量 pytest（第 2 次，完整捕获） | 同上，日志落 `G:\CODEX\New Manga.workspace\FEA-11-RENDITION-1-review\full-pytest-review.log` | 3212/10 | **3249 passed / 10 skipped**（281.67 s）EXIT=0 | PASS |
| 全量 pytest（第 3 次，`-rs` 采 skip 原因） | `python -m pytest tests -q -p no:warnings -rs --tb=no` | — | **3248 passed / 1 failed / 10 skipped**（288.14 s）EXIT=1；唯一失败=既有 flaky sandbox 用例 | FLAKY（非本卡） |
| flaky 隔离复跑 | `pytest tests/infrastructure/test_plugin_sandbox.py`；再单测 ×2 | — | 文件：1 failed/15 passed；单测：**1 passed / 1 passed** | 既有 flaky 确认 |
| `tests/providers` | `pytest tests/providers -q` | 559/4（卡面） | **559 passed / 4 skipped** EXIT=0 | PASS |
| 全量 .NET | `dotnet test apps/desktop-avalonia/NewManga.sln -c Release` | 1527 通过 / 0 失败 / 86 跳过 | **1527 / 0 / 86**（EXIT=0；8 项目 21+38+253+117+31+185+167+715；skip 0+0+0+0+0+55+24+7） | PASS |
| `verify_pins.ps1` | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 18/18 | **18/18 PASS** EXIT=0 | PASS |
| `check.ps1` | `pwsh -NoProfile -File tools/governance/check.ps1` | PASS(3 warnings) | **PASS(3 warnings)** EXIT=0（9 非终态 Task / STATUS 80% / PLAN 80%） | PASS |
| API inventory | `C:/Python314/python.exe tools/generate_api_inventory.py --check` | PASS | **EXIT=0**（`OK: rendered counts match FEA-C07 doc`） | PASS |
| scope diff | `git diff --name-only 4360fbcdb..a05a419f7` 等 | ⊆ allowed | 6 文件 ⊆ allowed；禁止面空 | PASS |

**pytest 10 skipped（逐条原因，`-rs` 实测）**：
1. `tests/providers/test_detect_seam_t111.py:15` — docTR (python-doctr) is not installed
2. `tests/providers/test_detection_doctr_real.py:11` — docTR (python-doctr) is not installed
3. `tests/providers/test_detection_manga_real.py:30` — installed transformers 4.48.3 has no RTDetrV2ForObjectDetection；pinned snapshot needs transformers>=4.49（requirements.txt pins 5.17.0）
4. `tests/network/test_connection_tester.py:106` — openssl unavailable
5–9. `tests/network/test_transport_tls.py:39,47,62,69,83` — openssl unavailable
10. `tests/providers/test_registry_readiness.py:274` — dev venv intentionally carries the ML stack（既有环境门控；该 skip 文本自带的历史断言失效说明）
> 与基线 10 skipped 一致，本卡未新增/改变任何 skip。

**.NET 86 skipped**：`Host.Tests` 55（read-only 策略/UI 集成/IPC 证据类，如 `Fea09UiImportIpcProductionTests`、`CommandIntegrationTests`、`GrantIssuerTests`、`HostRegionWorkbenchIntegrationTests`）、`CoreClient.Tests` 24（frozen sidecar/命令集成类）、`App.Tests` 7（`StartupSelfCheckUiTests`、`RunControllerHostIntegrationTests`、`WritePolicyUiIntegrationTests` 等）。`dotnet test` 默认 logger 不打印 skip 原因，名称逐条见 `logs/gates-dotnet.log` 与我的 `dotnet-review.log`。

### 6.1 flaky 与异常记录（不静默重试）

- 第 3 次全量（`-rs`）唯一失败：`tests/infrastructure/test_plugin_sandbox.py::test_sandbox_job_kills_grandchildren`（`still_alive is True`）。该测试源码自带 `FLAKY-PYTEST-1` 注释，历史上即依赖 Job Object 回收时延；本卡未改动 plugin/sandbox 任何文件。
- 隔离复跑：单文件 1 failed/15 passed；随后**单独**该用例连续 2 次 `1 passed`。结论：**既有 flaky，不是本卡回归**。
- 第 1 次后台全量 EXIT=1 的失败名未保留（我的命令只截取末 30 行），**无法归因**；`.pytest_cache/lastfailed` 含历史陈旧条目（含已改名的 `test_missing_bound_entry_is_typed_not_a_crash`），不可作为该次失败证据。第 2 次完整捕获为全绿，第 3 次失败已隔离确认是 sandbox flake。
- 结论：AC-R7 的「全量 3249/10」**可复现一次完整绿跑**；环境中存在与本卡无关的既有 flaky，集成验证时建议保留首跑/复跑记录。

---

## 7. 证据 sha256 复核（卡面 Canonical Evidence vs 实测）

| evidence_id | path | 卡面 sha256 | 实测 sha256 | 一致 |
|---|---|---|---|---|
| EV-1 | `verification/FEA-11-RENDITION-1/logs/gates-feature.log` | `dff05bcfc9459412465e22b604bdc1cdca9009202d9157a7f929ea19bc31b403` | 同左 | ✅ |
| EV-2 | `.../logs/gates-full-pytest.log` | `9afbe6a9375a4cba7db6a51589326b914553854ce92503df044797ff35dc99eb` | 同左 | ✅ |
| EV-3 | `.../logs/gates-dotnet.log` | `ddf6593612cc702ba608846eef06632a3ffd038add0e6e6c1790564e2571d244` | 同左 | ✅ |
| EV-4 | `.../logs/gates-governance.log` | `b9e87be18819ba2ba13a4fc062ed7527a26241da713d7057fc94b1a5724277ec` | 同左 | ✅ |
| EV-5 | `.../logs/scope-validation.log` | `4294f8ce24ce1e06eb91ed141b6dc06288dea7d92a28a4daf91772a950e0a484` | 同左 | ✅ |
| EV-6 | `.../logs/discrimination.log` | `c2e961cde3905e8d04e5bf0494b2fdc3935cf9b7d1126b1af68cd964c0e35f7d` | 同左 | ✅ |
| EV-7 | `.../RESOURCE-MANIFEST.json` | `37b7f8680e4f8eb8cda3ddf9ae2416c5fb52bfce99a3097933c4d7f0540a5190` | 同左 | ✅ |
| EV-8 | `.../changed-files.txt` | `36e3a73cfb0dd719df093f25464a55b07997853e0df6dfd819c9e4a017291bc9` | 同左 | ✅ |
| EV-9 | `.../EV.md` | `5dab7f50ffdfcc193eadbaea9710d7c4051c817a2ce14eb57d24781afe585289` | 同左 | ✅ |

- 9 个证据文件**确在 `75dace4c2`**（`git ls-tree -r 75dace4c2 -- verification/FEA-11-RENDITION-1` 命中 9 个 blob；`git diff 75dace4c2 -- verification/FEA-11-RENDITION-1` 为空）。
- `changed-files.txt` 与 `git diff --name-only 4360fbcdb..75dace4c2` **逐行一致**（17 个文件，含自身；无说明性差异）。
- EV-6 `discrimination.log` 为实现者自检（A-3 已裁定不采信为最终证据），本 review 的 §8 为其独立替代。
- 仓外隔离根（`G:\CODEX\New Manga.workspace\FEA-11-RENDITION-1\`）9 个已登记文件 sha256 全部匹配 manifest；但目录现有 10 文件（R1-04）。

---

## 8. 破坏性复跑与恢复证明（独立，非实现者自检）

### 8.1 Break A — I-1 referenced 准入

- 修改：`src/infrastructure/sqlite/pipeline.py` 的 `_ensure_referenced_target_readable` 首行插入 `return`（其余不动）。
- 破坏前文件 sha256：`d774a18cb91ead0407c934f38d7da464e53389f8aeb6faa79b3a4b6498ebe934`。
- 复跑：`pytest tests/fea11/test_source_rendition_run.py::test_unverifiable_referenced_pages_stay_target_not_found tests/fea11/test_source_rendition_run.py::test_region_scope_with_null_dimensions_stays_a_stable_target_not_found tests/fea11/test_source_rendition_gates.py::test_pending_gate_blocks_the_real_run_target_and_opens_when_acknowledged -q -p no:warnings --tb=line` → **3 failed**（`DID NOT RAISE PipelineError` ×3），EXIT=1。
- 恢复：`git checkout -- src/infrastructure/sqlite/pipeline.py`。
- 恢复证明：文件 sha256 复算 `d774a18cb91ead0407c934f38d7da464e53389f8aeb6faa79b3a4b6498ebe934`（与破坏前相同）；`git status --short` 空；`git diff --stat` 空；三文件 37 passed 复绿。

### 8.2 Break B — I-3 唯一 gate

- 修改：`src/bootstrap/core_assembly.py` 的 `read_gate` 在健康检查后直接 `return "open"`（跳过 `gate_of_binding`）。
- 破坏前文件 sha256：`87978893e32777c8f2fdae3b328de7264d9e7d3751e9f56aa3b3a5bad2db30b4`。
- 复跑：`pytest tests/fea11/test_source_rendition_gates.py -q -p no:warnings --tb=line` → **4 failed**（gate 三态 / pending 目标展开 / 真实 commit guard / 真实 provider 读图），EXIT=1。
- 恢复：`git checkout -- src/bootstrap/core_assembly.py`。
- 恢复证明：sha256 复算 `87978893e32777c8f2fdae3b328de7264d9e7d3751e9f56aa3b3a5bad2db30b4`；`git status --short` 空；`git diff --stat` 空；三文件 37 passed 复绿。

> 两次破坏均在**已提交的 clean 文件**上做，用 `git checkout --` 恢复；未在工作树留下任何破坏态。报告写入后工作树仅多出本 Review 文件。

---

## 9. 风险与未验证项

1. **L-R1（产品级 blocker，已登记）**：Run 无 source-read grant 通道；生产 referenced Run 仍会在读图/提交被 typed 拒绝。本卡只交付 Core 侧；负向用例已固化。**不得**读作「referenced 页 Run 已可用」。
2. **L-R2 未被本卡测试覆盖**：provider 的加密源路径没有新 fixture；`SOURCE_PASSWORD_REQUIRED` 只经 FEA-09 既有用例证明（reader 层），本卡只保证折叠为 `INVALID_INPUT` + detail code。建议后续卡补一条 provider 级加密用例。
3. **A-1 混合页 V 假可进入目标层（实测，已接受决策）**：只读探针（内存 v8 库，`tmp` 目录，未写仓库）：
   - PURE referenced + `width/height=NULL` → `TARGET_NOT_FOUND "page pr has no readable source"`（V 假）；
   - MIXED（`managed_original_ref` 非空）+ `width/height=NULL` → `create_run` **成功进入** `['pr']`；execute 后 detect `INVALID_INPUT`，detail=`page 'pr' has no managed original`；**regions/revisions/lineage 无行**。
   → 结论：不对称是 Lead A-1 已接受项；后果是「Run 进入后在 provider 处 typed 失败、像素不解码」，**不产生错误像素/错误 lineage**，但 limitation 文本（L-R5/L-R10）应补全这一后果（R1-01/R1-07）。
4. **read_gate 与 core_service gate 的损坏形态分歧**（R1-06）：只在「healthy binding 缺 publication 行」时可触发；不改变正常/ pending 语义，但读面不一致。
5. **EXIF 方向（L-R4）无测试**：`exif_transpose` 在 rendition 读取中生效；若源图带方向，frame 尺寸与 `pages.width/height` 可能不一致，旧 region geometry 可能错位——本卡明确不统一，未验证。
6. **PDF 源类型未覆盖**：新测试的 provider 像素只用 zip（`archive_page`）；`pdf_raster`/`pdf` 分支（`document_raster`）无本卡用例（FEA-09 既有覆盖不属于 provider 面）。
7. **既有 flaky**：`test_sandbox_job_kills_grandchildren`（R1-09）；集成验证时应保留首跑/复跑记录。
8. **第一次全量 pytest EXIT=1 的失败明细未捕获**：无法归因；第二次完整捕获全绿、第三次失败已隔离为上述既有 flaky。
9. **证据日志元数据不全**：`gates-full-pytest.log`/`gates-dotnet.log` 无 header/EXIT（R1-03）；FEA-09 恢复归因错误（R1-02）；manifest 9 vs 10（R1-04）。
10. **未验证「产品级端到端 Run」**：按范围定义不可验证（L-R1），本卡未宣称。

---

## 10. 只读纪律声明

- 本 Review 只新增本文件（`doc/reviews/FEA-11-RENDITION-1-r1.md`，属卡面 allowed_paths 的 `doc/reviews/FEA-11-RENDITION-1-*.md`）。
- 未修改生产代码/测试/契约/STATUS/PLAN/LEDGER/证据；§8 的两处破坏性编辑均已 `git checkout --` 恢复并逐字节证明。
- 未 commit、未 push、未创建 worktree、未改动 `apps/**`。
- 我使用的临时脚本/日志都在 **仓外** `G:\CODEX\New Manga.workspace\FEA-11-RENDITION-1-review\`（`full-pytest-review.log`、`full-pytest-skipreasons.log`、`dotnet-review.log`），未进入仓库。
- 全量 .NET 触发的 tracked `verification/FEA-09/logs/wire-redacted.ndjson` 追加已 `git checkout -- verification/FEA-09` 恢复；评审结束时 `git status --short` 空、HEAD 仍为 `c7c072b39`。

---

RENDITION-1-REVIEW: approved — 代码/测试/范围与 AC-R1…R7 均成立（P0=0/P1=0/P2=1/P3=8）；唯一 P2 为不准确的 limitation 文本（L-R10/Handoff，更正文本后即可 closeout，不需返修代码）；P3 集中在证据日志/计数/manifest 与既有环境 flake；工作树结束时 clean。
