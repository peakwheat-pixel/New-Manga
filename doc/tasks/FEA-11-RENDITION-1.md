---
id: FEA-11-RENDITION-1
title: FEA-11 referenced rendition 图源承接（Core 侧 Run/provider 消费当前 binding 真实 rendition）
kind: implementation
governance_version: 3
status: done
approval: 用户 2026-11-06「自动推进/全部授权/裁决交 Codex 或 DSH，无需用户介入」；独立 scope review `doc/reviews/FEA-11-RENDITION-1-scope-r1.md`（fresh subagent，verdict **READY-TO-FREEZE**，契约零字节）；DSH 2026-11-06 裁决（见「Scope Review 裁决」）：接受 **Core-only** 范围，F1（Run 无 source-read grant 通道）登记 limitation **L-R1** 并另立后续候选 `FEA-11-RUN-GRANT-1`，**I-5（commit guard 投影改造）出域**；释放为 ready、base `cdba15742`、Owner=`rendition-impl`（DSH Agent Teams）。实施交付 head `a05a419f7`（`693ab469b` + `a05a419f7`；证据/卡/Handoff `75dace4c2`）；DSH 核验后 2026-11-06 转 `in_review`，I-1 混合页取舍按「实施取舍裁决」接受；Review 由独立上下文 fresh subagent 执行
suggested_owner: codex
owner: rendition-impl
reviewer: 独立上下文 fresh subagent（r1 已指派；不得由实现会话/实例自审；session 与来源见 `doc/reviews/FEA-11-RENDITION-1-r1.md`）
depends_on:
  - FEA-11-LINEAGE-1
  - FEA-09
base_commit: cdba15742
branch: null
worktree: null
integration_commit: a05a419f7f6c6023786b61d9f11d8f6cdd0eb800
delivery_head: a05a419f7f6c6023786b61d9f11d8f6cdd0eb800
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/FEA-11-RENDITION-1
allowed_paths:
  - doc/tasks/FEA-11-RENDITION-1.md
  - doc/reviews/FEA-11-RENDITION-1-*.md
  - doc/handoffs/FEA-11-RENDITION-1-*.md
  - verification/FEA-11-RENDITION-1/**
  - src/infrastructure/sqlite/pipeline.py
  - src/bootstrap/core_assembly.py
  - src/infrastructure/providers/handlers.py
  - src/infrastructure/sqlite/library.py
  - tests/fea11/test_source_rendition_source.py
  - tests/fea11/test_source_rendition_run.py
  - tests/fea11/test_source_rendition_gates.py
out_of_scope:
  - Host/App/apps/**（Run-scoped source-read grant 铸/撤通道）→ 后续候选 FEA-11-RUN-GRANT-1；本卡不得宣称产品级 referenced Run 可用
  - src/bootstrap/core_service.py（resolve 面/Run dispatch/_assert_source_sync_gate）；commit guard 投影改造（原 I-5）
  - 冻结契约/schema/依赖/wire/命令集/协议 minor；18 pins；FEA-11 历史 AC 行字节
  - reader/导出/渲染/core.detect/UI/通知；删除/GC/回收站；扫描/调度/watcher
  - 真实 v7 legacy 迁移 fixture（既有 FEA-09 覆盖）；真实用户数据/AppData/外部卷/回收站；push
---

# FEA-11-RENDITION-1：referenced rendition 图源承接（Core 侧）

> **状态：`in_review`（交付 head `a05a419f7`；Owner=`rendition-impl`；base `cdba15742`）。**
> 承接 `FEA-11-LINEAGE-1` **L10**（Run/provider 消费 `managed_original_ref` 旧图，真实 referenced 图源/rendition 未承接）。
> **本卡只交付 Core 侧能力**：目标可进入 Run + provider 像素来自当前 binding 的真实 rendition + typed 拒绝 + 真实新旧图判别测试。**生产级端到端 Run 仍受 L-R1 限制**（Run 无 source-read grant 通道，Host/App 切片另卡）。

## 来源与依据

1. 独立 scope review：`doc/reviews/FEA-11-RENDITION-1-scope-r1.md`（fresh subagent `15bc65d0…`；**READY-TO-FREEZE**；契约零字节；含 F1–F8 证据与 In/Out/AC 草案）；第二独立只读复核 `doc/reviews/FEA-11-RENDITION-1-scope-r1-delta.md`（仅契约文本层判 READY-WITH-UNFREEZE，其 U1/U2 未被采纳，见「Scope Review 裁决」；两份报告均存档）。
2. L10：`doc/tasks/FEA-11-LINEAGE-1.md:136`（①纯 referenced 页被 `pipeline.py:1433-1434` 门槛拒绝；②`core_assembly.py:351-475` 只读 managed original；③混合页判别测试用 stub 图源）。
3. 契约：C-17 v1.1 §7.2（选择函数/键/门控/同 key 冲突）、§7.3（不建第二套匹配规则）、§3.3（Run 输入必须检查 publication gate）、§7.1（当前 binding 读隔离）；C-15 §4.1（`R(p,t)` 可读谓词）与 §4.2（resolve 是发布面，不禁止进程内 provider 读取）、§2.7（`rendition_kind` 五值白名单）；C-16 §2/§7（读取只经 grant facts，无路径回退）。均**不修改字节**。
4. 现状：`tests/fea11/conftest.py:161-333` 可造真实 source 树/binding/真实 grant（`mint_grant`）；`tests/fea11/test_source_lineage_run.py:138-199` 有真实 pipeline 装配模板（但其 `_StubImages` 禁止用于本卡判别）。

## Scope Review 裁决（DSH，2026-11-06）

| 争议点 | 独立 review 建议 | **DSH 裁决** |
|---|---|---|
| F1「Run 无 source-read grant 通道」使生产 Run 仍不可端到端 | 接受并写 limitation L-R1；若要求端到端则本卡 BLOCKED/拆分 | **接受 Core-only + L-R1**；另立候选 `FEA-11-RUN-GRANT-1`（proposed，后续由 Lead 决定是否释放）；本卡/Handoff/STATUS **不得**写「referenced 页 Run 已可用」「L10 全修」 |
| F2「chapter/book-scope 含 referenced 页整批 TARGET_NOT_FOUND」 | 同一门槛修复，AC 覆盖行为变化 | **接受**：卡面冻结该行为变化（L-R3）；AC-R1 覆盖混合 chapter scope |
| I-5「commit guard 投影改造」（把 guard 提前到 BEGIN 前） | 推荐但可退化 | **出域（Out）**：不在本卡改 `commit_step` guard 位置；commit 期 guard 失败沿用既有 `DB_FAILED` typed（L-R8），AC-R4 按此断言 |
| F3「detect 在 commit 前写 region 的 native 化竞态」 | In：写 region 前用 `__fea10_guard__` 复核 | **接受（I-4）**：解码→写 region 之间 binding 变化必须 `INPUT_REVISION_CHANGED` 且零 region 写 |
| F4「provider 读图无 publication gate」/ F5「不得第三份 V 谓词」 | In：抽单一 gate 谓词；复用 C-15 §4.1 V 谓词 | **接受（I-3/F5）**：gate 只在 assembly 内抽一份；target 进入复用 V 谓词（必要时 `library.py` 暴露单一 classmethod） |
| U1/U2 契约文本追加（delta 建议） | delta 判 READY-WITH-UNFREEZE（仅文本层） | **不采纳 UNFREEZE**：C-17 §7.2「实际资源读取」+ C-15 §4.1 `R(p,t)` + §4.2 发布面已覆盖本卡读法；改以本卡「实现语义」段写死同一读法（DSH 认账）；零契约字节 |
| §3.3 pending 码投影（delta D-A） | 需显式裁决 | **按既有 family 投影**：Run 目标展开/`StartRun` pending → `TARGET_NOT_FOUND`；provider 读图 → `PROVIDER_FAILED`/`INVALID_INPUT`（detail 记 source 语义）；C-17 §8:352「旧命令不重映射」，不新增 `SOURCE_*`（L-R8） |
| `prepared["cache_key"]` vs `RenditionCache.rendition_key`（delta D-B） | provider 若接缓存必须用 `acquire` 同参 | **本卡 provider 不接 `rendition_cache`**（Out/L-R7）；卡面实现语义与 AC-R5 增加禁止性断言（不得用 `prepared["cache_key"]` 作缓存键） |

## 实施取舍裁决（DSH，2026-11-06；交付后核验）

| # | 实现取舍 | **DSH 裁决** |
|---|---|---|
| A-1 | **I-1 混合页准入**：Owner 实现为「**纯 referenced 页**（`managed_original_ref IS NULL`）走 V+gate 新准入；**遗留混合页**（referenced + `managed_original_ref` 非空）在 Run **目标进入层**保持既有门槛」；provider 层混合页仍按 binding 图（L-R5） | **接受**。理由：①纯 referenced 是 AD-003/C-15 的产品形态，必须走冻结 V+gate；②混合页是历史/测试/损坏形态，改其准入会扩大与本卡目标无关的既有行为面，且可能在无 binding 的遗留行上引入新失败；③provider 读取仍 fail-closed：混合页若 binding 不可用 → `ProviderInputError`（`PROVIDER_FAILED`）typed 拒绝，绝不回退旧 managed 原图（L-R5）。该不对称已写入 L-R5，**Review 不得据此判 AC-R1 未满足**（AC-R1 的 V 假反向断言在纯 referenced 页上成立）。 |
| A-2 | `delivery_head` 指向实现+测试 head `a05a419f7`（证据/卡/Handoff 提交 `75dace4c2` 在其后） | **接受**：`delivery_head` = 实现+测试 head；证据提交由 `integration_commit`/证据 commit 字段反映（沿既往卡惯例）。 |
| A-3 | 判别性自检由实现者完成（4/4 破坏变红） | **接受但不采信为最终证据**：独立 Review 必须自行破坏至少一条分支复跑（Handoff §5 已要求）；实现者自检仅作辅助。 |

## 目标（可观察交付）

1. `source_mode='referenced'`、V 为真、binding healthy、publication gate open 且授权有效的页，可作为 Run 目标（page/chapter/region scope）进入，不再被 `TARGET_NOT_FOUND "page … has no managed original"` 拒绝。
2. provider 的 `page_frame/region_crop/page_png` 对 referenced 页读取**当前持久化 binding** 对应的 source entry，经既有 grant/identity/budget 通道解码为 re-encoded PNG rendition（**不发布 catalog、不写 rendition_cache、不新增 rendition_kind/key**）。
3. managed 页读取路径与 Run 行为**零回归**；binding 变化/授权撤销/门禁 pending/预算超限/entry 损坏均为 typed 失败、零业务写、无崩溃。
4. 真实新旧不同图像判别测试（禁 stub）与 `verification/FEA-11-RENDITION-1/**` 证据。

## Scope（冻结）

### In

| # | 冻结项 | 文件/函数 | 要点 |
|---|---|---|---|
| **I-1** | referenced 目标进入 | `src/infrastructure/sqlite/pipeline.py`：`_page_or_error`、`_region_or_error`、`SqliteTargetCatalog` | `_page_or_error` 增选 `p.source_mode`；referenced 分支不再要求 `managed_original_ref`（要求 `source_hash` 非空 + V 谓词 + gate open）；`_region_or_error` 谓词改 `(p.managed_original_ref IS NOT NULL OR p.source_mode='referenced')` 并保留 `width/height`/`_ensure_lineage_readable`；`metadata` 键集合**不变**（不改变 prepared digest 形状）；新增 `source_gate_reader`/`page_visibility` 注入（`None` 时旧行为不变，沿 `guard_reader` 先例） |
| **I-2** | provider 像素源 | `src/bootstrap/core_assembly.py`：`_ManagedPageImageSource.__init__/_page_image/page_frame/region_crop/page_png` | referenced 分支：①read gate ②`prepare_referenced_rendition(page_id, repository=…, access=…)`（唯一选择入口）③必要时 `access.claim_secret_for_binding(...)` 取一次性密码 ④`render_prepared_rendition(..., image_decoder=…, document_raster=…, password=…)` ⑤PNG→Pillow；所有 `SourceImportError`→`ProviderInputError`/typed ProviderError，**固定安全文本**（禁路径/locator/entry 名）。managed 分支逐字节行为不变。**不发布、不写 cache、不新增 wire/key/kind** |
| **I-3** | 单一 gate 谓词与装配 | `src/bootstrap/core_assembly.py`（`assemble_core_services` 内） | 定义唯一 `read_gate(page_id) -> unavailable/pending/open`；同时供 `run_source_guard`、`_ManagedPageImageSource`、`pipeline._catalog.source_gate_reader` 使用；Run 面 refusal 沿既有 `TARGET_NOT_FOUND`/`PROVIDER_FAILED` family，detail 记 `SOURCE_ACCESS_DENIED` 语义，不新增命令码 |
| **I-4** | detect 前置复核 | `src/infrastructure/providers/handlers.py`：`HandlerDependencies`、`handle_detect`；`core_assembly.py` 注入 `commit_guard` reader | 调用 `region_creator` **之前**用 `step_run.input_refs["__fea10_guard__"]` 与当前 commit guard digest 比对；不一致 → `StepExecutionError("INPUT_REVISION_CHANGED")` 且**零 region 写**；`None` 依赖 → 跳过（旧单测构造不变） |
| **I-5** | 测试/证据 | 新测试 3 文件 + `verification/FEA-11-RENDITION-1/**` | 见「测试要求」；真实 zip/PNG、真实 grant、真实 pipeline/`run_source_guard` 接线；禁 `_StubImages` |

### Out（明确不做）

- Host/App/`apps/**`、Run-scoped grant 通道（L-R1；候选 `FEA-11-RUN-GRANT-1`）。
- `src/bootstrap/core_service.py`（resolve 面已正确；本卡不碰 wire 面）；`commit_step` guard 位置改造（原 I-5，L-R8）。
- 契约/schema/依赖/wire/命令集/协议 minor/18 pins；`doc/plan/**`、`doc/contracts/**`、`schema.py`。
- reader/导出/渲染/`core.detect`/UI/通知；删除/GC/回收站；扫描/调度/watcher；真实 v7 迁移 fixture。
- 让 provider 发布 catalog、写 `rendition_cache`、或调用 `handle_resolve_page_resource`（避免第二套发布语义与 GC/预算耦合）。
- 新错误码（尤其 `SOURCE_*` 进入 Run 命令面）；Host allow-list 变更。
- 真实用户数据/AppData/外部卷/回收站；push。

## 实现语义（DSH 冻结口径）

- **唯一选择规则**：provider 与 resolve 必须调用同一 `prepare_referenced_rendition`，选择元组 `(source_id, version_id, entry_id, decoder_name, decoder_version, params_digest, verified_digest, rendition_kind)` 完全一致；provider **不得**自行推导 key/公式，不得读 `page.managed_original_ref` 作为 referenced 图源。
- **门控先于读取**：C-17 §3.3「Run 输入」必须在授权校验外检查当前 binding publication gate（pending → 拒绝，不读源）；gate/身份/预算检查在解码前。
- **像素与尺寸**：`page_frame` 返回的 `ImageFrame(width,height,"rgb32",payload)` 必须对应 rendition 解码后的实际像素；`region_crop` bbox 以 rendition 坐标系裁切；`page_png` 为 rendition 的 PNG 重编码。
- **detect native 化防护**：I-4 的复核必须发生在任何 region 写之前；失败时不得留下 machine region/revision/lineage 行。
- **managed 路径零触碰**：managed 页的 `metadata`、`commit_guard`、三个端口行为与现状逐字节一致；不得因新分支对 managed 页调用 grant/gate。
- **不夸大**：卡面/Handoff/STATUS 只写「Core 侧 referenced rendition 图源已承接」；**不写**「产品级 Run 可用」「L10 全部修复」。
- **缓存键禁令**：provider **不接 `rendition_cache`**（Out/L-R7）；**不得**把 `prepared["cache_key"]`（`resolve.py:107-118`）当作任何缓存键——它与 `RenditionCache.rendition_key` 是两个派生。若未来接缓存，必须只用 `RenditionCache.acquire(source_id, version_id, entry_id, kind, decoder, decoder_version, params, ...)` 同参，不得另算键。

## Acceptance Criteria

> 每条 AC 必须有「删掉实现/改坏关键分支必须变红」的判别性测试；像素断言**禁止 stub**；真实文件放隔离根/`tmp_path`。

- [x] **AC-R1 目标进入（page/chapter/region）**：V 为真、binding healthy、gate open 的 referenced 页在 page-scope 与 chapter-scope（含 managed+referenced 混合章节）`expand` 成功且 `current(page_id)` 可返回快照；region-scope 在 `width/height` 非空且 lineage 可读时成功；反向：`integrity_status≠complete` 或 `verified_digest≠entry.content_digest` 的页仍 `TARGET_NOT_FOUND`；region-scope 在 `width/height` 为 NULL 时仍 `TARGET_NOT_FOUND` 且 message 稳定（`PipelineError` 无 `retryable` 成员，R1-05 更正）。 证据：`tests/fea11/test_source_rendition_run.py`（5 用例）+ `tests/fea11/test_source_rendition_gates.py::test_pending_gate_blocks_the_real_run_target_and_opens_when_acknowledged`（真实装配）；`verification/FEA-11-RENDITION-1/logs/gates-feature.log`。 <<MET>>
- [x] **AC-R2 像素来自当前 binding 的真实 rendition（判别核心）**：两套/三套真实不同图（A=30×20 managed copy、B=12×7 当前 binding entry、C=20×9 旧 entry），断言 `page_frame`/`page_png`/`region_crop` 的像素与尺寸只匹配 B；混合页 managed 路径**零调用**（`ManagedRootTrust.read_bytes` 哨兵）；真实 production pipeline + `run_source_guard` 行为等价复刻（assembly 级 identity/guard 由 `gates.py:226-321` 覆盖，R1-08）+ 记录型 detector/OCR 断言像素来自 B 且 detect 产出的 native lineage 绑定当前 binding；重指 binding 后像素随 binding 变化。 证据：`test_source_rendition_source.py`（5 用例，R1-05 更正）+ `test_source_rendition_run.py`（2 用例）+ `gates.py::test_real_assembly_provider_reads_the_binding_rendition_end_to_end`；判别性 case B（删掉 referenced 分支 → 4 failed）。 <<MET>>
- [x] **AC-R3 managed 零回归**：managed 页 `TargetSnapshot.metadata` 键集合不变（基础 5 键 + 既有 `context_pages` 投影）；`page_frame/region_crop/page_png` 与既有实现一致；managed 分支**从不**调用 grant/gate（`_ForbiddenAccess` + `_forbidden_gate` 探针）；既有 `tests/providers`（559 passed/4 skipped）与 `tests/fea11` 基线全绿。 证据：`test_source_rendition_source.py::test_managed_page_reads_the_managed_copy_and_never_touches_grant_or_gate` 等 + `gates-feature.log`。 <<MET>>
- [x] **AC-R4 typed 拒绝与零写**：①prepare→accept 之间 binding 变化 → `RUN_STALE_PREVIEW`；②accept→commit 之间变化 → step FAILED（`INPUT_REVISION_CHANGED`，I-4），零业务写；③无 grant/revoked：读图前拒绝（`INVALID_INPUT`，detail 含 `SOURCE_ACCESS_DENIED`/`SOURCE_GRANT_REVOKED`），`read_entry_bytes` spy 0 次；④gate pending/unavailable：目标展开 `TARGET_NOT_FOUND`，零解码；⑤读图后、写 region 前 binding 变化 → `INPUT_REVISION_CHANGED`，region/revision/lineage 行数不变；⑥entry 消失/损坏/预算超限：typed ProviderError。 证据：`test_source_rendition_source.py`（8 用例，R1-05 更正）+ `test_source_rendition_run.py::test_binding_change_*` + `test_source_rendition_gates.py`（I-4 handler 级 4 用例 + 真实 commit guard 用例）；判别性 case C/D。 <<MET>>
- [x] **AC-R5 不建第二套选择规则**：spy `prepare_referenced_rendition` → provider 与 resolve 的选择元组逐字段一致且只调用一次；`RenditionCache.acquire` 探针 0 次；`media_artifacts`/`rendition_cache` 零发布；provider 源码不含 `"cache_key"` 字面（L-R7 禁令）。 证据：`test_source_rendition_source.py::test_provider_reuses_the_single_selection_function_and_never_caches`；`gates.py::test_real_assembly_wires_one_gate_object_into_every_consumer`。 <<MET>>
- [x] **AC-R6 零契约/schema/依赖/wire 漂移**：`git diff 4360fbcdb..HEAD -- doc/plan doc/contracts src/infrastructure/sqlite/schema.py apps/` 为空；`verify_pins.ps1` 18/18 PASS；`generate_api_inventory.py --check` PASS；依赖文件零 diff；无 `SOURCE_*` 进入 Run 面（静态用例）。 证据：`logs/gates-governance.log`、`logs/scope-validation.log`。 <<MET>>
- [x] **AC-R7 门禁、证据与「不夸大」约束**：`pytest tests` **3249 passed / 10 skipped**（基线 3212/10，差额 37 = 本卡新增；跑后已恢复 `verification/FEA-09` 字节）；`pytest tests/fea11` **145 passed**（基线 108）；全量 .NET **1527/0/86**（基线一致）；`check.ps1` PASS(3 warnings)；scope diff ⊆ allowed_paths；EV/Resource Manifest/Handoff 完整；**含 L-R1 负向用例**（`test_run_without_a_live_source_grant_is_typed_and_writes_nothing`）；Handoff 写明 L-R1/L-R2 且未宣称产品级可用/未回填 FEA-11 AC。 证据：`verification/FEA-11-RENDITION-1/**`。 <<MET>>

## 实施记录（Owner `rendition-impl`，2026-11-06）

- **commit 链**：`693ab469b`（`src/` 3 文件：pipeline 目标准入 + provider rendition 分支 + detect 前置复核）、`a05a419f7`（3 个新测试文件，37 用例）；证据/卡面/Handoff 见本目录后续提交。base `4360fbcdb`。
- **I-1**（`src/infrastructure/sqlite/pipeline.py`）：`_page_or_error` 增选 `p.source_mode`；**纯 referenced 页**（`managed_original_ref IS NULL`）改由 `_ensure_referenced_target_readable` 准入 = `source_hash` 非空 + 复用 **C-15 §4.1 V**（注入 `page_visibility`，assembly 用 `repository.get_page`）+ 唯一 `read_gate`；managed 页与**遗留混合页**（仍有 managed original，L-R5）保持既有准入逐字节不变；`_region_or_error` SQL 改 `(managed_original_ref IS NOT NULL OR source_mode='referenced')` 并保留 width/height + `_ensure_lineage_readable`；`TargetSnapshot.metadata` 键集合不变；`source_gate_reader`/`page_visibility` 为 `None` 时 fail-closed 保持旧拒绝。
- **I-2**（`src/bootstrap/core_assembly.py`）：`_ManagedPageImageSource` 新增 `source_access`/`read_gate`/`image_decoder`/`document_raster` 注入；referenced 分支 = `read_gate` → `prepare_referenced_rendition`（唯一选择入口）→ `claim_secret_for_binding`（加密源一次性 Secret-G，缺失即 typed `SOURCE_PASSWORD_REQUIRED`）→ `render_prepared_rendition` → PNG→Pillow；所有 `SourceImportError` → 固定安全文本 `ProviderInputError`（只带 code，不含路径/locator/entry 名）；**不发布 catalog、不写 rendition_cache、不使用 prepared cache_key**；managed 分支逐字节不变（并用 `getattr` 修 F7 的 `PageView` 安全性）。
- **I-3**：assembly 内唯一定义 `read_gate(page_id) -> unavailable/pending/open`，由 `run_source_guard`、provider、`pipeline._catalog.source_gate_reader` 三处共用（装配级 identity 断言）；Run 面沿用既有 `TARGET_NOT_FOUND` family，不新增 `SOURCE_*` 命令码（L-R8）。
- **I-4**：`HandlerDependencies.commit_guard` 可选注入；`handle_detect` 在 `region_creator` **之前**用 `step_run.input_refs["__fea10_guard__"]` 与当前 `run_guard_value` digest 比对，不一致 → `INPUT_REVISION_CHANGED` 且零 region 写；`None`/无 ref 时保持旧行为。
- **门禁实测（before → after）**：fea11 **108 → 145 passed**；全量 pytest **3212/10 → 3249/0/10**（+37；跑后 `git checkout -- verification/FEA-09` 已恢复）；.NET **1527/0/86 → 1527/0/86**；`verify_pins` 18/18；`check.ps1` PASS(3 warnings)；API inventory PASS；scope diff ⊆ allowed_paths，禁止面（`doc/plan`/`doc/contracts`/`schema.py`/`apps/`/依赖文件/`core_service.py`/conftest/冻结测试）零 diff。
- **判别性验证**：4/4 破坏点（删 I-1 准入 / 删 I-2 referenced 分支 / 删 I-4 调用 / read_gate 恒 open）均使目标用例变红，随后从内存原文恢复（`verification/FEA-11-RENDITION-1/logs/discrimination.log`）。
- **不夸大**：本卡只交付 **Core 侧能力**；**L-R1**（Run 无 source-read grant 通道）仍使生产 referenced Run 在读图/提交被 typed 拒绝（负向用例已固化），**不得**表述为「referenced 页 Run 已可用」或「L10 全修」。

## 测试要求

| 场景/AC | 命令或步骤 | 前提/环境 | 预期 | 证据 |
|---|---|---|---|---|
| AC-R1/R2/R3/R4/R5 | `python -m pytest tests/fea11/test_source_rendition_source.py tests/fea11/test_source_rendition_run.py tests/fea11/test_source_rendition_gates.py -q` | 真实 production migrations 库 + 真实 zip/PNG + 真实 grant + 真实 pipeline | 全绿；改坏分支变红 | `verification/FEA-11-RENDITION-1/logs/*.log` |
| AC-R1/R2 判别 | 同上（真实装配 + 记录型 detector） | 隔离根/`tmp_path`；禁 stub | 像素只匹配当前 binding 图 | 判别日志（含像素标记/尺寸） |
| AC-R6/R7 | `pytest tests`、`dotnet test`、pins、check、API inventory、scope diff | 仓库根 | 不减少/不漂移 | `gates.log`、`scope-validation.log`、`changed-files.txt` |
| L-R1 负向 | 无 grant 的 Run | 真实装配 | typed 失败、零写 | 负向用例日志 |

## 已知 limitation（预登记，closeout 必须如实保留）

- **L-R1（产品级 blocker）**：Run 无 source-read grant 通道（F1）→ 生产 referenced 页 Run 仍会在读图/提交被拒；本卡只交付 Core 侧。后续候选 `FEA-11-RUN-GRANT-1`（Host 铸 grant 切片，需 .NET 门禁）。
- **L-R2**：加密 referenced 源无法 Run（无 Secret-G 通道）→ typed `SOURCE_PASSWORD_REQUIRED`，不崩溃。
- **L-R3**：chapter/book-scope 行为变化（F2）：含 referenced 页的章节/书从「整批失败」变为「包含 referenced 页」；成本/产物范围变化。
- **L-R4**：EXIF 方向不一致（F6）：frame 尺寸=rendition（exif_transpose 后）；旧 region geometry 在方向源上可能错位；本卡不统一方向。
- **L-R5**：混合页（referenced + `managed_original_ref` 非空）provider 从此按 binding 图，旧 managed 副本被忽略；**Run 目标进入层对混合页保持既有门槛**（不查 V/gate，见「实施取舍裁决」A-1）；混合页若 V 为假（binding 不可用/摘要不符/尺寸 NULL）**仍会进入目标层**，但 provider 因 V 读返回 None 而 typed 拒绝（`INVALID_INPUT`，detail 沿用 "has no managed original"）、**像素不解码**、不产生错误像素或 lineage；不做数据迁移（R1-01 补全）。
- **L-R6**：detect 的 region 写在 step commit 之外（既有形态）；I-4 只缩小竞态窗口，不提供事务回滚。
- **L-R7**：provider 不走 rendition_cache（有意）：重复解码；预算按 grant `max_decode_bytes`；后续复用需另卡。
- **L-R8**：Run 面错误码沿用既有 family（`PROVIDER_FAILED`/`INVALID_INPUT`/`TARGET_NOT_FOUND`/`DB_FAILED`/`INPUT_REVISION_CHANGED`），不新增 `SOURCE_*` 投影；commit 期 guard 失败仍为 `DB_FAILED`（I-5 出域）。
- **L-R9**：Run 快照不含 binding/rendition 观测（metadata 形状不变）→ 无法从快照直接诊断用了哪个 binding 的图。
- **L-R10（R1-01 更正）**：纯 referenced 页 `width/height` 为 NULL ⇒ V 为假 ⇒ **page-scope 与 region-scope 均 `TARGET_NOT_FOUND`**（不存在「page-scope 可进入、像素由解码得出」的路径；本卡不承诺可用）。**遗留混合页**见 L-R5：目标层可进入（旧门槛），但 provider typed 拒绝且像素不解码。
- **L-R11（R1-06 新登记）**：assembly 新 `read_gate` 对「healthy binding 但无 publication 行」返回 open；resolve 面 `core_service._assert_source_sync_gate` 在 `previous_binding_id` 有 publication 时 fail-closed。该损坏形态下两读面语义不一致（provider/target 首次可达）；本卡 Out 不碰 `core_service.py`，后续卡统一 gate（含 previous-binding 链 fail-closed）。
- **Follow-up（R1-07/R1-08，P3，本卡不改代码）**：`page_png` docstring 仍写「whole Managed Copy page」；V 为假的 referenced 页 provider 诊断文本沿用 "has no managed original"（语义误导，但无路径泄露）；run 级像素 E2E 的 `run_source_guard` 为测试内行为等价复刻（真实装配 identity/guard 由 `gates.py` 覆盖）。

## 允许修改范围

- 卡/评审/交接：`doc/tasks/FEA-11-RENDITION-1.md`、`doc/reviews/FEA-11-RENDITION-1-*.md`、`doc/handoffs/FEA-11-RENDITION-1-*.md`。
- 证据：`verification/FEA-11-RENDITION-1/**`。
- 生产代码（4 个文件）：`src/infrastructure/sqlite/pipeline.py`、`src/bootstrap/core_assembly.py`、`src/infrastructure/providers/handlers.py`、`src/infrastructure/sqlite/library.py`（仅按 F5 暴露单一 V 谓词时需要）。
- 测试（3 个新文件）：`tests/fea11/test_source_rendition_source.py`、`tests/fea11/test_source_rendition_run.py`、`tests/fea11/test_source_rendition_gates.py`。
- **不在 Owner 写域**：`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`、`doc/plan/**`、`doc/contracts/**`、`src/infrastructure/sqlite/schema.py`、`src/bootstrap/core_service.py`、`apps/**`、`tests/fea11/conftest.py`、`tests/fea11/test_source_lineage_run.py`。实现确需触碰时 Owner 必须先停下报 DSH 增列，不得静默扩域；不得 `git add -A`，提交用显式 pathspec。

## 禁止范围

- Host/App/apps/**；Run-scoped grant 通道；契约/schema/依赖/wire/18 pins；`core_service.py`；commit guard 投影改造；reader/导出/渲染/UI/通知；删除/GC/回收站；扫描/调度/watcher；真实用户数据/AppData/外部卷/回收站；push。
- 不得修改 FEA-11 历史 AC 行字节；不得回填 AC11-5/AC11-9；不得宣称产品级 referenced Run 可用或 L10 全修。

## 依赖、风险与阻塞

- 硬依赖：`FEA-11-LINEAGE-1`（done；L10 来源 + lineage guard）、`FEA-09`（done；referenced 读面/grant/cache/`prepare_referenced_rendition`）。`FEA-11-SCAN-2` 与本卡无技术依赖，占位卡登记时的顺序依赖已移除。
- 风险：F3 native 化竞态（I-4 缓解）；混合页行为翻转（L-R5 登记）；EXIF 方向（L-R4）；provider 重复解码成本（L-R7）；时间测试不使用 sleep。
- 阻塞标准：若实现证明必须改 `core_service.py`/schema/契约/Host 才能完成 Core 侧目标，Owner 停下报 DSH，不得自行扩域；若确认必须产品级端到端，DSH 改判拆分 `FEA-11-RUN-GRANT-1`。

## 交付与运行记录

- 实施 Owner：`rendition-impl`（DSH Agent Teams teammate）。
- Handoff：`doc/handoffs/FEA-11-RENDITION-1-a05a419f7.md`。
- Review：独立上下文 fresh subagent `doc/reviews/FEA-11-RENDITION-1-r1.md`（session `e79484b2-5994-4ac5-9e44-6ac5d0c2edf8`）→ **approved（P0=0/P1=0/P2=1/P3=8）**；findings 处置见 `EV.md` §7 与 Closeout Record。
- 实际测试：before/after、passed/failed/skipped 与 skip 原因见 `verification/FEA-11-RENDITION-1/EV.md` §1 与 `logs/gates-*.log`、`logs/final-scope-validation.log`。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-1 | AC-R1…R5/R7 判别性（fea11 145 / 三文件 37） | `verification/FEA-11-RENDITION-1/logs/gates-feature.log` | `75dace4c2` | `dff05bcfc9459412465e22b604bdc1cdca9009202d9157a7f929ea19bc31b403` | CANONICAL |
| EV-2 | AC-R7 全量 pytest（3249/10；含 FEA-09 恢复） | `verification/FEA-11-RENDITION-1/logs/gates-full-pytest.log` | `75dace4c2` | `9afbe6a9375a4cba7db6a51589326b914553854ce92503df044797ff35dc99eb` | CANONICAL |
| EV-3 | AC-R7 全量 .NET（1527/0/86） | `verification/FEA-11-RENDITION-1/logs/gates-dotnet.log` | `75dace4c2` | `ddf6593612cc702ba608846eef06632a3ffd038add0e6e6c1790564e2571d244` | CANONICAL |
| EV-4 | AC-R6/R7 pins 18/18 + check PASS(3 w) + API inventory PASS | `verification/FEA-11-RENDITION-1/logs/gates-governance.log` | `75dace4c2` | `b9e87be18819ba2ba13a4fc062ed7527a26241da713d7057fc94b1a5724277ec` | CANONICAL |
| EV-5 | AC-R6 scope diff ⊆ allowed_paths / 禁止面零 diff | `verification/FEA-11-RENDITION-1/logs/scope-validation.log` | `75dace4c2` | `4294f8ce24ce1e06eb91ed141b6dc06288dea7d92a28a4daf91772a950e0a484` | CANONICAL |
| EV-6 | 判别性（4/4 破坏变红） | `verification/FEA-11-RENDITION-1/logs/discrimination.log` | `75dace4c2` | `c2e961cde3905e8d04e5bf0494b2fdc3935cf9b7d1126b1af68cd964c0e35f7d` | CANONICAL |
| EV-7 | Resource Manifest（Review R1-04 后：仓外 10 文件聚合 + closeout 说明） | `verification/FEA-11-RENDITION-1/RESOURCE-MANIFEST.json` | `3eda60ac8` | `8ded4d9ba786dbabf5a9705455c6ef91cd09353024c8272e3656cc260ebd26f8` | CANONICAL |
| EV-8 | 变更清单 | `verification/FEA-11-RENDITION-1/changed-files.txt` | `75dace4c2` | `36e3a73cfb0dd719df093f25464a55b07997853e0df6dfd819c9e4a017291bc9` | CANONICAL |
| EV-9 | Evidence 索引（Review R1-02/R1-05/R1-06 更正后） | `verification/FEA-11-RENDITION-1/EV.md` | `3eda60ac8` | `b5112d4d384ca3d2dd6245c0d37da799e6b96ecf7c09ebc023676bf4fefbe44d` | CANONICAL |
| EV-10 | 最终范围/工作树复原证明（HEAD=`75dace4c2`、worktree 空；FEA-09 已恢复，R1-02/R1-04） | `verification/FEA-11-RENDITION-1/logs/final-scope-validation.log` | `3eda60ac8` | `507cdec26046222f139105701fd6cbae1fca4937ee1eb0d6b74add4faec53d12` | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | NOT_APPLICABLE（main 工作树；base `4360fbcdb`） | NOT_APPLICABLE | — | — | 未创建 linked worktree；`git worktree list` 无本卡新增 |
| temp | `G:\CODEX\New Manga.workspace\FEA-11-RENDITION-1\` | PRESERVE_REFERENCED | `G:\CODEX\New Manga.workspace\FEA-11-RENDITION-1\` | `448272d64059f26444bf2bcd9e4e8f99ce6eb58c989192cf01438895e5aceca8` | 仓外隔离根，agent 脚本 + 判别日志 + `final-scope-validation.log`；无进程持有；产品/测试不引用；仓内 canonical 副本 `logs/discrimination.log` 与 `logs/final-scope-validation.log`（EV-6/EV-10） |
| test-fixture | `tests/fea11/test_source_rendition_*.py`（`tmp_path` 运行时生成真实 PNG/zip） | NOT_APPLICABLE | — | — | 仓库不提交二进制 fixture；不使用 conftest 的硬编码工作区根 |
| user-data | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 未读写真实用户数据/AppData/外部卷/回收站 |
| build-artifact | NOT_APPLICABLE（本卡零 C# 改动） | NOT_APPLICABLE | — | — | `dotnet test` 的 obj/bin 在既有 build 目录，未纳入交付 |
| integration-log | `G:\CODEX\New Manga.workspace\FEA-11-RENDITION-1-closeout\`（Lead 集成门禁原始日志 3 文件） | PRESERVE_REFERENCED | `G:\CODEX\New Manga.workspace\FEA-11-RENDITION-1-closeout\` | `98b8bda775a4d946aac5108529b85868c4004082aaf096e6a73901cc5d5d57a5` | 仓外；无进程持有；产品/证据不引用；不删除（集成验证原始输出） |

## Closeout Record

- **Closeout date / DSH**：2026-11-06；DSH（Lead / Architect / Integrator）。
- **交付/集成**：`base_commit=cdba15742`；实现链 `693ab469b`（I-1…I-4）→ `a05a419f7`（3 个测试文件 37 用例，`delivery_head`）→ `75dace4c2`（证据/卡/Handoff）；Review 处置 `3eda60ac8`（证据更正，R1-01…R1-09，无代码改动）。`integration_commit=a05a419f7`（代码+测试集成点）；卡/STATUS/PLAN/LEDGER closeout 提交见本提交。
- **AC 判定**：**AC-R1…AC-R7 全部 MET**（逐项证据见 `EV.md` §4 与 Canonical Evidence EV-1…EV-10）；无 PARTIAL/BLOCKED。
- **独立 Review**：`doc/reviews/FEA-11-RENDITION-1-r1.md`（fresh subagent `e79484b2-5994-4ac5-9e44-6ac5d0c2edf8`，未参与实现/返修）→ **approved（P0=0 / P1=0 / P2=1 / P3=8）**；无代码返修。findings 处置：R1-01(P2) → L-R10/L-R5 文本更正 + Handoff Errata；R1-02/R1-03/R1-04(P3) → 证据归因更正、`final-scope-validation.log` 入 canonical（EV-10）、manifest 重算（10 文件）；R1-05 → AC/EV 计数与措辞更正；R1-06 → 新登记 **L-R11**；R1-07/R1-08 → follow-up 登记（不改代码）；R1-09 → 既有 flaky 非本卡回归。
- **DSH 集成验证（Lead 实测，HEAD=`3eda60ac8`，2026-11-06）**：全量 `pytest tests` **3249 passed / 10 skipped（EXIT=0）**；全量 `dotnet test apps/desktop-avalonia/NewManga.sln -c Release` **1527 passed / 0 failed / 86 skipped（EXIT=0）**；`verify_pins.ps1` **18/18 PASS**；`check.ps1` **PASS(3 warnings)**；`generate_api_inventory.py --check` PASS；scope diff ⊆ allowed_paths，`doc/plan`/`doc/contracts`/`schema.py`/`apps/`/依赖/`core_service.py` 零 diff。两次全量后均 `git checkout -- verification/FEA-09`（restore_exit=0），最终 worktree clean。原始日志：`G:\CODEX\New Manga.workspace\FEA-11-RENDITION-1-closeout\`（PRESERVE_REFERENCED）。本卡集成轮未命中既有 flaky；Review 轮命中 `test_sandbox_job_kills_grandchildren` 并隔离复跑通过（R1-09）。
- **canonical_evidence_status**：`complete`（EV-1…EV-10，逐文件 sha256；EV-1…EV-6/EV-8 在 `75dace4c2`，EV-7/EV-9/EV-10 在 `3eda60ac8`）。**resource_closeout_status**：`complete`。
- **删除/迁移/归档**：0 文件、0 字节（`PRESERVE_REFERENCED`/`NOT_APPLICABLE`；未删除/移动/归档任何资源）。
- **未关闭项（如实保留）**：L-R1（生产级 blocker：Run 无 source-read grant 通道；候选 `FEA-11-RUN-GRANT-1`）、L-R2…L-R11；R1-07/R1-08 follow-up（`page_png` docstring、V 假诊断文本、run 级 guard 等价复刻——本卡不改代码）；既有 flaky R1-09。**不得**宣称「referenced 页 Run 产品可用」「L10 全修」；FEA-11 AC 未回填。
- **指针清理**：STATUS 当前 Task → 无活动 Task（下一候选 `FEA-12-UI-RESIDUAL-1` proposed）；PLAN 增本节点 done 事实；TASK_LEDGER 重生成；本卡不再是 READY 节点。
- **push**：见最终答复（门禁全过后按用户 2026-11-06 授权判定）。
