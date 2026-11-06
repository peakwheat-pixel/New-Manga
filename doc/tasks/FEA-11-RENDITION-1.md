---
id: FEA-11-RENDITION-1
title: FEA-11 referenced rendition 图源承接（Core 侧 Run/provider 消费当前 binding 真实 rendition）
kind: implementation
governance_version: 3
status: ready
approval: 用户 2026-11-06「自动推进/全部授权/裁决交 Codex 或 DSH，无需用户介入」；独立 scope review `doc/reviews/FEA-11-RENDITION-1-scope-r1.md`（fresh subagent，verdict **READY-TO-FREEZE**，契约零字节）；DSH 2026-11-06 裁决（见「Scope Review 裁决」）：接受 **Core-only** 范围，F1（Run 无 source-read grant 通道）登记 limitation **L-R1** 并另立后续候选 `FEA-11-RUN-GRANT-1`，**I-5（commit guard 投影改造）出域**；释放为 ready、base `cdba15742`、Owner=`rendition-impl`（DSH Agent Teams）
suggested_owner: codex
owner: rendition-impl
reviewer: 独立上下文 fresh subagent（不得由实现会话/实例自审；报告须记录 reviewer 与会话 ID）
depends_on:
  - FEA-11-LINEAGE-1
  - FEA-09
base_commit: cdba15742
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
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

> **状态：`ready`（scope 已冻结；Owner=`rendition-impl`；base `cdba15742`）。**
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

- [ ] **AC-R1 目标进入（page/chapter/region）**：V 为真、binding healthy、gate open、授权有效的 referenced 页在 page-scope 与 chapter-scope（含 managed+referenced 混合章节）`expand` 成功且 `current(page_id)` 可返回快照；region-scope 在 `width/height` 非空且 lineage 可读时成功；反向：`integrity_status≠complete` 或 `verified_digest≠entry.content_digest` 的页仍 `TARGET_NOT_FOUND`（证明不是「有 binding 就放」）；region-scope 在 `width/height` 为 NULL 时仍 `TARGET_NOT_FOUND` 且 message/retryable 稳定（不得落到 `KeyError`/`SOURCE_BUDGET_EXCEEDED` 误导码）。证据：新测试三文件相应用例。
- [ ] **AC-R2 像素来自当前 binding 的真实 rendition（判别核心）**：用两套真实、内容不同的图（旧图 A 写入 managed copy；新图 B 为当前 binding 的 source entry；尺寸与内容均不同），断言 `page_frame`/`page_png`/`region_crop` 的像素与尺寸只匹配 B；混合页（referenced + `managed_original_ref` 非空）中 managed 路径**零调用**（spy）；用真实 production pipeline + `run_source_guard` 接线 + 记录型 detector，断言 detector 收到的像素来自 B（非 A），且 detect 产出的 native lineage 绑定当前 binding。改回 managed original 或旧 entry 必须变红。证据：真实 zip/PNG + 真实 grant + 真实装配日志。
- [ ] **AC-R3 managed 零回归**：managed 页 `TargetSnapshot.metadata` 键集合与 `commit_guard` 形状不变；`page_frame/region_crop/page_png` 与原实现一致（尺寸+PNG 载荷）；managed 分支**从不**调用 grant/gate（注入「任何调用即失败」探针）；混合页按 AC-R2 走 binding 图（行为变化见 L-R5）。证据：managed 用例 + 哨兵 + 既有 `tests/providers/test_bootstrap_providers.py` 回归。
- [ ] **AC-R4 typed 拒绝与零写**：①prepare→accept 之间 binding 变化 → `RUN_STALE_PREVIEW`；②accept→commit 之间变化 → step `FAILED`（既有 family：`LOCK_CHANGED`/`INPUT_REVISION_CHANGED`/commit 期 `DB_FAILED`，按失败点），零业务写；③无 grant/`SOURCE_GRANT_REVOKED`/过期：**读图前**拒绝（`PROVIDER_FAILED`，detail 含 source 语义），spy decoder **0 次**调用；无匹配 grant 必须 typed，不得落到 `KeyError`/`None`/崩溃；④gate pending：Core `StartRun`/目标展开 `TARGET_NOT_FOUND`（§3.3 的 gate 检查必须存在；码按既有 family — C-17 §8:352 旧命令不重映射；Host 侧投影不在本卡，`apps/**` 出域）或读图 `PROVIDER_FAILED`，零解码；⑤读图后、写 region 前 binding 变化（F3）：`INPUT_REVISION_CHANGED`，region/revision/lineage 行数不变；⑥预算超限/entry 缺失/损坏：typed ProviderError，零写。证据：独立用例 + spy/monkeypatch 计数 + 行数快照。
- [ ] **AC-R5 不建第二套选择规则**：同一 fixture 下 resolve 与 provider 的 `prepare_referenced_rendition` 选择元组完全一致；已发布路径的 v2 key 仍等于 `_referenced_resource_id(prepared)`（`core_service.py:4608-4632` 行为不变）；不新增 key 公式/rendition kind；provider **不调用** `rendition_cache.acquire`、**不发布** catalog（spy 0 次）且**不使用** `prepared["cache_key"]` 作为缓存键。证据：选择一致性用例 + 探针计数。
- [ ] **AC-R6 零契约/schema/依赖/wire 漂移**：`git diff <base>..HEAD -- doc/plan doc/contracts src/infrastructure/sqlite/schema.py apps/` 为空；`verify_pins.ps1` 18/18 PASS；`generate_api_inventory.py --check` PASS；无 `pyproject.toml/requirements*.txt` 变更；Run 命令集/payload/协议 minor 不变。证据：`gates.log`/`scope-validation.log`。
- [ ] **AC-R7 门禁、证据与「不夸大」约束**：`pytest tests` 不减少（基线 3212/10，实测记录 passed/failed/skipped 并逐条记 skip 原因；跑后恢复 `verification/FEA-09` 字节）；`pytest tests/fea11` 只增不减（基线 108）；全量 .NET 按门禁实测或 `NOT_RUN`+理由（基线 1527/0/86）；`check.ps1` PASS；scope diff ⊆ allowed_paths；EV/Resource Manifest/Handoff 完整；**必须含「无 live grant 时 Run 不能执行且为 typed」负向用例**（证明 L-R1 真实存在）；Handoff 写明 L-R1/L-R2 且不得声称产品级可用/不得回填 FEA-11 AC。

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
- **L-R5**：混合页（referenced + `managed_original_ref` 非空）从此按 binding 图，旧 managed 副本被忽略；不做数据迁移。
- **L-R6**：detect 的 region 写在 step commit 之外（既有形态）；I-4 只缩小竞态窗口，不提供事务回滚。
- **L-R7**：provider 不走 rendition_cache（有意）：重复解码；预算按 grant `max_decode_bytes`；后续复用需另卡。
- **L-R8**：Run 面错误码沿用既有 family（`PROVIDER_FAILED`/`INVALID_INPUT`/`TARGET_NOT_FOUND`/`DB_FAILED`/`INPUT_REVISION_CHANGED`），不新增 `SOURCE_*` 投影；commit 期 guard 失败仍为 `DB_FAILED`（I-5 出域）。
- **L-R9**：Run 快照不含 binding/rendition 观测（metadata 形状不变）→ 无法从快照直接诊断用了哪个 binding 的图。
- **L-R10**：`width/height` 为 NULL 的 referenced 页：page-scope 可能可进入，region-scope 仍 `TARGET_NOT_FOUND`；此类页 V 为假，本卡不承诺可用。

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
- Handoff：`doc/handoffs/FEA-11-RENDITION-1-<head>.md`（交付 head 后追加）。
- Review：独立上下文 fresh subagent（`doc/reviews/FEA-11-RENDITION-1-r*.md`）。
- 实际测试：待实施记录（before/after、passed/failed/skipped、skip 原因）。

## Canonical Evidence

（Owner 提交前填写；`in_review` 时必须逐项 pin commit/SHA-256。）

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| pending | AC-R1…R7 | pending | pending | pending | CANONICAL |

## Resource Manifest

（closeout 时填写真实路径与 disposition；不适用写 `NOT_APPLICABLE`。）

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| pending | pending | pending | — | — | pending |

## Closeout Record

- 待实施、Review、集成与 closeout 时填写（DSH 保留最终集成/closeout 责任）。
