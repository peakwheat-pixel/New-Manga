---
task: FEA-11-RENDITION-1
title: FEA-11-RENDITION-1 独立 scope review r1（C-17 §7.2 / C-15 充分性裁决 + Core 侧最小写域）
reviewer: fresh subagent（独立上下文；未参与实现；只读）
session: 15bc65d0-4dee-43e5-9135-37539f05234c（DSH fresh subagent）
parent_session: session-c2883c5f-dcf8-400d-b161-9c84f562486a
reviewer_kind: subagent
date: 2026-11-06
repo: G:\CODEX\New Manga
branch: main
worktree: clean（审查开始时；审查中 Lead 提交 AC11-1 裁决，HEAD 前进，见 §1）
reviewed_head: 987d81981baf6e45c0de520bcd905b26f524fd34
head_at_review_end: cdba157429f547c2d6b06ca41699978596fcfd12（仅治理文档变更；本 review 引用的契约/代码/测试零 diff）
verdict: READY-TO-FREEZE
---

# FEA-11-RENDITION-1 Scope Review r1（独立只读）

> **结论先行：`READY-TO-FREEZE`（契约零字节；但必须把 F1 冻结成 limitation，并把 AC 限定在「Core 侧 + live grant」前提）。**
>
> - **契约充分：不需要 UNFREEZE。** `C-17 v1.1 §7.2`（`doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md:329-337`）已冻结选择函数、键形状、cache/catalog 命中前门控、同 key 摘要冲突，并明写「resolve 与 issue/**实际资源读取**必须使用同一选择结果」；`§3.3`（同文件 `:171-173`）逐字把「**Run 输入**」纳入 publication gate；`§7.1`（`:310-315`）明写 Run 读取当前区域必须以当前 binding 为准、且「应用装配须确保现有 page_id-only repository 不会成为旁路」。`C-15 §4.1`（`doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md:264`）给出 referenced 可读的**唯一**授权谓词（live source-read grant + identity digest），`§4.2`（`:266-274`）只约束 **resolve/发布面**（只发 decoded/re-encoded rendition、禁 raw 字节），并未禁止 Core 进程内的 provider 读取；`C-16 §2/§7`（`doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md:66-70,182`）把读取来源钉死在 grant facts（无路径回退）。因此「provider 进程内读当前 binding 的 entry → 解码为 PNG rendition → **不发布、不写 cache、不新增 wire**」是契约内的实现选择，**零契约字节**成立。
> - **代码事实：L10①②③ 全部复现**（见 §3 实测），并发现比 L10① **更大**的既有缺陷：同一 `managed_original_ref` 门槛让 **chapter/book-scope Run 整批失败**（`pipeline.py:809-834` 先展开全部页再逐页 `_page_or_error`），不止 page-scope。
> - **关键新事实 F1（决定 scope 边界）**：**Run 没有 source-read grant 通道**。source-read grant 只在 import（`SourceImportModels.cs:741-753`，Core 侧 `runtime.py:567` 绑定）与 sync apply（`application/sources/service.py:287,295-314` 绑定 operation grant）时铸造/绑定，scan（`SourceScanScheduler.cs:1371`）铸 grant 但不绑定 page binding，secret-resolve（`HostRuntime.cs:683-717`）只给**已发行**的 grant 追加一次性 `secret_ref`。而 `library_start_run` 走普通 CoreService 通道（`HostCommandRegistry.cs:284`、`HostRuntime.cs:861-867`）。Run 步骤提交处的 `run_source_guard`（`core_assembly.py:1623-1641`）**强制** `find_bound_for_source` 有 live grant；实测无 grant → `SOURCE_ACCESS_DENIED`，`commit_step` 投影 `db_failed`（→ `DB_FAILED`，`application/tasks/service.py:971`）。**结论：本卡把 Core 侧读路径修好之后，生产环境的 referenced 页 Run 仍然不可端到端执行**（只有在 import/sync 后 ≤300s 的 grant 窗口内才可能通过）；同样的 grant 约束也作用于 `handle_resolve_page_resource`（`core_service.py:4450-4463`）。该缺口不是本卡引入，也**不在本卡可修范围**（需 Host 为 Run 铸 grant = `apps/**` + C-06/C-16 wire 复用）。
> - **因此本卡必须冻结为 `Core-only`**：交付「目标可进入 + 像素来自当前 binding 的真实 rendition + typed 拒绝 + 真实图判别测试」；生产级 Run 闭环作为 **limitation L-R1** 登记，并登记后续候选（建议 `FEA-11-RUN-GRANT-1`）由 Lead 决定是否立项。**不得**在卡面/Handoff/STATUS 写「referenced 页 Run 已可用」或「L10 全部已修」。
> - **若 DSH 要求本卡以「产品级 Run 端到端可用」为完成标准**，则本卡应改判 **BLOCKED/拆分**（F1 需要 Host 侧新切片 + .NET 门禁），而不是扩大本卡写域。本 review 推荐前一分支（Core-only + limitation），因为它是 L10 的直接承接、可用真实 grant 判别、且零契约字节。

---

## 1. 只读核验基线（review 时点）

| 项 | 事实 | 证据 |
|---|---|---|
| HEAD | `987d81981baf6e45c0de520bcd905b26f524fd34`（`docs(handoff): DSH 新会话交接…`） | `git rev-parse HEAD` |
| 分支 | `main` | `git branch --show-current` |
| 工作树（审查开始 18:49） | clean（`git status --short` 空） | 实测 |
| 工作树（审查中 19:0x） | **Lead 并发写入并随后提交**：`M doc/tasks/FEA-11.md` + `?? doc/reviews/AC11-1-ADJUDICATION-INPUT-2026-11-06.md` + `?? doc/reviews/FEA-11-AC11-1-adjudication-2026-11-06.md`（AC11-1 终态裁决，与本卡无关；**非本 review 写入**） | `git status --porcelain`、`git diff --stat` |
| HEAD 前进（审查结束 19:09） | `987d81981 → cdba15742`（`docs(fea-11-ac11-1): 终态裁决 AC11-1 MET…`）。变更文件：`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`、`doc/tasks/FEA-11.md`、两份 AC11-1 review；**`doc/plan`/`src`/`tests`/`apps`/`verification` 在 `987d81981..cdba15742` 零 diff** → 本 review 的全部事实断言对该区间仍有效 | `git diff --name-only 987d81981..HEAD -- doc/plan src tests apps verification`（空） |
| 冻结 pins | **18/18 PASS**（C15 `d8c0a3bcfc21`、C17 `aefa0fa5b17e`） | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` → `PIN AUDIT: PASS (all 18)` |
| governance check | **PASS（3 warnings）**：9 个非终态 Task / STATUS 80% / PLAN 80% | `pwsh -NoProfile -File tools/governance/check.ps1` |
| pytest `tests/fea11` | **108 passed**（8 warnings） | `C:/Python314/python.exe -m pytest tests/fea11 -q -p no:cacheprovider` |
| pytest 相邻面 | **29 passed**（`tests/core/test_p13_run_runtime.py` + `tests/fea09/test_referenced_resolve.py` + `tests/fea09/test_rendition_cache_unittest.py`） | 同上命令 |
| 全量 pytest | **NOT_RUN（本 review）**；Lead 提供基线 3212 passed / 10 skipped | 已知副作用：全量 pytest 会改写 tracked `verification/FEA-09` 字节，需事后恢复（`doc/tasks/FEA-11-LINEAGE-1.md:102,153` 先例）；本 review 为只读纪律不做该操作 |
| 全量 .NET | **NOT_RUN（本 review，遵守审查约束）**；Lead 提供基线 1527/0/86 | — |
| 内存库只读探针（3 次，`:memory:`；未写仓库） | 见 §3.2 输出摘要 | `python -`（stdin） |

本 review 未修改生产代码/测试/契约/STATUS/PLAN/LEDGER，未 commit/push；唯一写入是本文件（属占位卡 `allowed_paths` 的 `doc/reviews/FEA-11-RENDITION-1-*.md`）。

---

## 2. 契约充分性裁决（核心问题）

### 2.1 逐条核实：冻结条款覆盖什么

| 条款 | 原文要点（引用） | 对「Run/provider 消费当前 binding 的真实 referenced rendition」的含义 |
|---|---|---|
| `C-17 §7.2`（`doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md:329-337`） | 保持 `resolve_page_resource {page_id} → {resource_id,revision:"original"}` 形状与 managed `page-original-{page_id}` 稳定键；referenced 一律选 `page-rendition-v2-`+sha256(canonical{page_id,binding_id,source_id,version_id,entry_id,verified_digest,rendition_kind,decoder_name,decoder_version,params_digest})；**门控/授权/identity 检查在 cache/catalog 命中前**；产物只能 decoded/re-encoded；key 变必另键；**同 key 既有摘要不同 → typed 冲突，绝不替换**；**「resolve 与 issue/实际资源读取必须使用同一选择结果」** | 选择函数是**唯一的**；「实际资源读取」被逐字点名，因此 provider 的进程内读取必须复用同一选择结果（binding→source/version/entry + decoder/profile），**不需要新 wire**；`resource_id` 只在「发布到 catalog」时产生，provider 不发布即不涉及该键；门控在命中前 → provider 读取前必须做 gate/授权/identity |
| `C-17 §7.3`（`:339-348`） | 四条证据映射（direct / unique_pixel / duplicate_group / missing_old）；「**不建立第二套匹配规则**」 | 禁止在本卡另造「哪张图算当前图」的规则；只能复用 §7.2 选择 + 既有 gate + C-15 §3.2 证据语义 |
| `C-17 §3.3`（`:171-173`） | 「R、resolve、issue 新资源、**Run 输入**和 live edit/apply 在授权校验外，**必须检查当前 binding 的 publication gate**；pending → `SOURCE_ACCESS_DENIED`」 | **Run 输入**（含 provider 读图）的门控是**契约要求**，不是本卡新增语义；当前 provider 读图完全没有 gate（`core_assembly.py:379-411`），本卡必须补上 |
| `C-17 §7.1`（`:310-315`） | 读「当前区域」必须 lineage 等于当前 binding；「**应用装配须确保现有 page_id-only repository 不会成为旁路**」；changed/repoint/missing 切断坐标继承 | 直接支持「像素源必须按 binding 选，而不能 `get_page(page_id).managed_original_ref`」；也支持 F3（detect 写 region 前必须确认 binding 未变） |
| `C-15 §4.1`（`doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md:237-264`） | `is_complete_page` referenced = healthy binding ∧ `verified_digest = entry.content_digest` ∧ 正尺寸；**`R(p,t)`** referenced = 有效 source-read grant + identity digest 匹配（加密源另需 C-16 v1.1 fresh grant） | 这是 referenced **读取**的权威谓词：provider 读取必须满足 R；R 不限定「只能由 resolve 命令读」 |
| `C-15 §2.7`（`:174-205`） | `rendition_cache` 元数据；`rendition_kind` **五值白名单**；只允许 decoded/re-encoded rendition，禁 raw；`rel_path` 在 `source-renditions/` 下 | 该表是**缓存元数据**，写入者是 resolve 面（`core_service.py:4470-4511,4536-4543`）；provider「不发布」时不受该表白名单约束；若要在 cache 里新建 `detect_input` 之类 kind → **会撞 v8 已冻结的 CHECK**（`src/infrastructure/sqlite/schema.py:732-733`）→ 需要 schema 迁移，**本卡不可做** |
| `C-15 §4.2`（`:266-274`） | 五读路径；`handle_resolve_page_resource` referenced「只允许经 source-read grant 读取并按 rendition_cache 规则**发布** decoded/re-encoded rendition…禁止把 raw user-source 字节直接发布」 | 该行约束的是 **resolve/发布面**，也是 referenced **资源（wire）**的唯一合法面；它没有、也无法禁止 Core 进程内的 provider 读取（provider 不发布任何字节） |
| `C-16 §2`（`doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md:66-70`） | 四维 scope 冻结；Core 每次读取前/提交前校验签名/session/expiry/generation/scope/identity；`budget.max_decode_bytes` = 单次 rendition 解码上限 | provider 读取只能走 grant facts 的路径与 facts（`reader.read_entry_bytes` → `read_verified_bytes` → `source_lease`），且受 `max_decode_bytes` 约束；已有实现可原样复用 |
| `C-16 §7`（`:176-186`） | 第 4/5 条：`user-source` 不得进入 derived-cache grant；derived 产物不得作为 SourceVersion 证据；**「Core 只接受 grant 中的路径与 facts；不得以调用方/receipt/UI 路径读取」** | provider 不得从 Run 请求/目标 metadata 里取路径；必须从 grant registry 解析。本卡设计（`prepare_referenced_rendition` + `access`）符合 |
| `C-17 §8`（`:352`） | 「下表仅 C-17 命令投影，**旧命令不重映射**」 | Run 面不需要新增 `SOURCE_*` 错误码；provider 失败沿用既有 provider/Run 码（`PROVIDER_FAILED` / `INVALID_INPUT` 等）即合法 |

### 2.2 逐个回答 Lead 提出的四个问题

1. **§7.2 的选择函数/键形状/门控/同 key 摘要冲突语义，是否覆盖「provider 内部读图」而不需要新 wire？**
   **覆盖。** ①选择函数唯一且 §7.2 逐字要求「实际资源读取」与 resolve 同一结果；②`resource_id` 是**发布键**，provider 不发布则不产生该键（无形状变化）；③门控/授权/identity 必须在「cache/catalog 命中前」——provider 读取前做同一套检查即可；④同 key 摘要冲突只发生在**已发布资源**上，provider 不发布则无冲突面；若未来让 provider 走 cache，则 `rendition_cache.acquire` 的 digest 校验（`rendition_cache.py:145-158`）与 `_publish_rendition_bytes` 的冲突拒绝（`core_service.py:4634-4650`）已覆盖。wire 形状（`{page_id}→{resource_id,revision}`）与命令集**零变化**。

2. **C-15 §4.2 的 `handle_resolve_page_resource` 读路径是否唯一合法读面？内部 provider 读取是否被授权（还是必须走 resolve/issue）？**
   **它是 referenced「资源/发布」的唯一合法读面，但不是「像素」的唯一合法路径。** 理由：①C-15 §4.2 的表格标题是「五读路径（**FEA-09 必改/必回归**）」，行标题是 `handle_resolve_page_resource`（wire 命令），其语义是「按 rendition_cache 规则**发布**」——它是 FEA-09 的改动/回归清单，不是「任何读取都必须走这里的授权穷举表」；②C-15 §4.1 的 `R(p,t)` 才是「可读」的权威定义（grant + identity），并不限定读的触发者；③C-17 §7.1:313 逐字把「**Run 读取当前区域**」列为必须按当前 binding 的读路径，C-17 §3.3:173 又把「**Run 输入**」纳入 publication gate——冻结契约**已经预设 Run 会读源**，因此「§4.2 表没有 provider 行 ⇒ provider 读取未授权」的读法不能成立（否则 §3.3/§7.1 的「Run 输入/Run 读取」两处将无对象）。④因此 Core 进程内的 provider 读取是 `R` 的一个实现面，不需要、也不应该绕道 wire resolve（那会让每次 Run 都向 catalog 发布派生产物，触发 GC/预算/目录增长，反而扩大风险）。

3. **是否存在契约缺口（需要 UNFREEZE）？**
   **不存在必须的缺口。** 唯一可想象的「缺口」是两个**不推荐**的写法：
   - **新增 `rendition_kind`**（例如 `detect_input`）以把 provider 解码写进 `rendition_cache`：会同时撞 `C-15 §2.7` 五值白名单（`:181`）和 **v8 迁移里已冻结的 CHECK**（`schema.py:732-733`）。→ 需要 schema 迁移 + C-15 UNFREEZE + 重 pin，**本卡明确不做**（provider 不写 cache 即无此需求）。
   - **把「provider 进程内读取」写成契约文字**（澄清而非改语义）：最小载体是 `C-17 §7.2` 追加一句「Core 进程内 provider 读取（Run 输入）与 resolve 使用同一选择结果，不新增 wire/不发布资源」。这会改冻结字节 → 需 `CONTRACT-UNFREEZE-2026-11-06-C17` 同类载体 + C17 单 pin 重签；**不必要**，建议把该解释写进 **Task 卡面/Handoff**（非契约字节），不改 `doc/plan`。
   - 若 DSH 坚持要文字化：影响面 = `doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md` 单文件（C17 pin）或 `doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md`（C15 pin）；**无 schema/wire/代码影响**；但会触发 18 pins 中 1 项重签与一次 UNFREEZE Review。

4. **明确结论三选一**
   **`READY-TO-FREEZE`**（零契约字节；条件见 §4 F1 与 §6 AC-R1 的「live grant」前提）。**不是** `READY-WITH-UNFREEZE`（无必须的契约改动）；**也不是** `BLOCKED`——除非 DSH 把「产品级 Run 端到端可用」定为本卡完成标准（那时应拆分 F1 为独立卡，而不是把本卡判死）。

### 2.3 为什么「零契约字节」成立（一句话版）

选择函数（§7.2）、门控（§3.3）、lineage 隔离（§7.1）、可读谓词（C-15 §4.1）、读取来源（C-16 §2/§7）**都已冻结并且正好覆盖本卡要做的每一件事**；本卡只增加「Core 进程内的一个读取实现 + 两个既有门槛的 referenced 分支 + 一个既有 commit guard 的前置复核」，**不新增命令、DTO、错误码、rendition kind、schema 或依赖**。

---

## 3. 代码事实与证据

### 3.1 Run 入口链与 provider `images` 端口

| 时点 | 文件/行 | 事实 |
|---|---|---|
| Run 命令面 | `src/bootstrap/core_service.py:383-385,5850-5895` | `_RUN_COMMANDS = {PrepareRun, AcceptRun, StartRun, ControlRun, ResumeBlockedRun, GetRunSnapshot}`；`PrepareRun`→`pipeline.prepare_run`，`AcceptRun`→`accept_prepared_run`，`StartRun`→`accept_start_run`；**无 grant 参数、无 wire 变化** |
| 计划/接受快照 | `src/application/tasks/service.py:400-422,433-504` | `prepared_quartet = {requestedTargets, settingsSnapshot, providerBindingSnapshot, constraintSnapshotRef}`；`preparedDigest=snapshot_digest(quartet)`；接受时重算并比对 → `RUN_STALE_PREVIEW` |
| 目标来源 | `src/infrastructure/sqlite/pipeline.py:780-843` | `SqliteTargetCatalog.expand`：book/chapter 先取出**全部页 id** 再逐页 `_page_or_error`（`:809-834`）；page/region 走 `_page_or_error`/`_region_or_error` |
| page 门槛 | `src/infrastructure/sqlite/pipeline.py:1420-1469` | `_page_or_error`：`source_hash IS NULL or managed_original_ref IS NULL` → `TARGET_NOT_FOUND "page … has no managed original"`（`:1433-1434`）；metadata 写 `source_filename/managed_original_ref/source_hash/lineage_hidden_regions/commit_guard`（`:1462-1468`） |
| region 门槛 | `src/infrastructure/sqlite/pipeline.py:1471-1512` | SQL 硬要求 `p.managed_original_ref IS NOT NULL AND p.width IS NOT NULL AND p.height IS NOT NULL`（`:1477-1478`）；随后 `_ensure_lineage_readable`（`:1489-1491`） |
| 行级 lineage 过滤 | `src/infrastructure/sqlite/pipeline.py:1544-1594` | `_lineage_visible_regions` 只把 lineage-visible region 放进 page target；`_ensure_lineage_readable` 把 `LineageVerificationError` 映射为 `PipelineError(code)` |
| commit guard 值 | `src/infrastructure/sqlite/pipeline.py:1540-1542` + `src/bootstrap/core_assembly.py:1611-1619,1643` | `commit_guard = {"binding": get_page_binding(page_id), "drafts": [...]}`（装配期注入 `run_guard_value`） |
| 步骤 attempt / digest | `src/application/tasks/service.py:855-886` | `input_refs["__fea10_guard__"] = snapshot_digest(commit_guard)`、`__fea10_protection__`（`:865-867`）；commit 时按 digest 比对（`pipeline.py:970-975`） |
| provider 端口 | `src/infrastructure/providers/handlers.py:143-154` | `PageImageSource` Protocol：`page_frame/region_crop/page_png` |
| 消费点（5 处） | `handlers.py:360`（detect）、`:490`（ocr）、`:683`（segment）、`:794→1081`（inpaint `_upstream_frame`）、`:892`（color） | 全部经 `HandlerDependencies.images`；生产注入在 `core_assembly.py:1553-1555` |
| 生产图源 | `src/bootstrap/core_assembly.py:351-475` | `_ManagedPageImageSource._page_image` 只读 `page.managed_original_ref`（`:387-392`），经 `ManagedRootTrust` 读取；refusal = `ProviderInputError`（`INVALID_INPUT`） |
| 生产装配 | `src/bootstrap/core_assembly.py:1547-1569` | `build_production_handlers(... images=_ManagedPageImageSource(repository, storage, regions, root_trust=...))`；`lineage_guard` 同源注入 |
| detect 复用 | `handlers.py:316-409` | 有 live region 就复用（`:351-358`）；否则 `page_frame`（`:360`）→ detector → `region_creator`（`:396-409`）**在 commit 之前写 region** |
| Run 源守卫 | `src/bootstrap/core_assembly.py:1623-1641` | commit 时：binding 缺失→放行；`status!='healthy'`→`TARGET_NOT_FOUND`；gate≠open→`TARGET_NOT_FOUND`；**`find_bound_for_source` 必须找到 live grant**（`:1638-1640`）→ 否则 `SourceImportError` |
| commit 异常投影 | `src/infrastructure/sqlite/pipeline.py:886-887,1041-1068` | guard 抛出的 `SourceImportError` 被 `except Exception`（`:1065-1068`）吞为 `db_failed` → `service.py:971` 映射 `DB_FAILED` |
| typed provider 投影 | `handlers.py:230-253` + `infrastructure/pipeline/executor.py:34-42` | `ProviderError`→`StepExecutionError(error_code)`；其它异常→`PROVIDER_FAILED`；`service.py:1109-1116` 写入 step error_code |
| Host Run 错误 allow-list | `apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandRegistry.cs:30-37` | 仅用于**命令级**错误；含 `PROVIDER_FAILED/PROVIDER_UNAVAILABLE/TARGET_NOT_FOUND/RUN_STALE_PREVIEW` 等，不含 `INVALID_INPUT/DB_FAILED`（step/task 码直接进 Run 快照，不经该表） |

### 3.2 实测（内存库 + 临时目录；只读，未写仓库）

命令：`C:/Python314/python.exe -`（stdin 脚本，`sqlite3 :memory:` + `MigrationRunner(default_migrations())`；fixture 复用 `tests/fea11/conftest.py` 的 `add_source_tree/add_referenced_page`）。

```text
# 探针 1：referenced 页（managed_original_ref=NULL）+ 一个 managed 页同 chapter
page-scope expand(pr): PipelineError code=TARGET_NOT_FOUND detail=page pr has no managed original
page current(pr):      PipelineError code=TARGET_NOT_FOUND detail=page pr has no managed original
region-scope expand(rg1): PipelineError code=TARGET_NOT_FOUND detail=rg1
chapter-scope expand(c1): PipelineError code=TARGET_NOT_FOUND detail=page pr has no managed original
row source_mode: ('referenced', None)
# 探针 2：生产 image source（真实类，非 stub）
page_frame: INVALID_INPUT stage=image-source detail="page 'pr' has no managed original"
page_png:   INVALID_INPUT stage=image-source detail="page 'pr' has no managed original"
find_bound_for_source(no grant): SOURCE_ACCESS_DENIED | no active source-read grant is bound to this page binding
find_for_source(no grant):       SOURCE_ACCESS_DENIED | no active source-read grant covers this source
# 探针 3：commit guard 失败投影
commit_step status: db_failed
commit_step detail: SourceImportError('no active source-read grant is bound to this page binding')
=> service.py:971 将 'db_failed' 映射为 DB_FAILED
```

**判读**：①L10① 复现；②**chapter-scope 整批失败**（同一门槛，L10 未记录，见 F2）；③L10② 复现（图源只读 managed original）；④无 grant 时 Run commit 必然 `DB_FAILED`（F1）。

---

## 4. Findings（P1…P3；本卡 scope 必须回应的项）

| ID | 级别 | 文件/行 | 触发与影响 | 证据 | 建议 |
|---|---|---|---|---|---|
| **F1** | **P1（scope-defining）** | `core_assembly.py:1638-1641`；`HostCommandRegistry.cs:284`；`HostRuntime.cs:861-867`；`SourceImportModels.cs:741-753`；`SourceScanScheduler.cs:1371`；`application/sources/service.py:287,295-314`；`SourceReadCoordinator.cs:226-263`；`HostRuntime.cs:683-717`；`source_read_refs.py:442-475`（`find_bound_for_source`）、`:559-584`（`_checked`）、`:165-166`（grant 窗口 ≤300s） | **Run 无 source-read grant 通道**：grant 只在 import 与 sync apply 时铸造/绑定（scan 铸但不绑定 page binding；secret-resolve 只附加一次性 secret）；`library_start_run` 走普通 CoreService。因此 Core 修好后，生产 Run 仍会在 commit guard 被拒（`DB_FAILED`），provider 读取也会被 `SOURCE_ACCESS_DENIED` 拒；只有 import/sync 后 ≤300s 的窗口内可能通过。**本卡不得宣称产品级 Run 可用。** | §3.2 探针 2/3 | 冻结为 limitation **L-R1**；AC-R1 明写「Core 侧 + live grant（测试铸造）」；登记后续候选（建议 `FEA-11-RUN-GRANT-1`，proposed）由 Lead 决定；若 Lead 要求端到端 → 本卡 BLOCKED/拆分 |
| **F2** | **P1（L10 扩大）** | `pipeline.py:809-834`（先全量展开）+ `:1433-1434` | **chapter/book-scope Run 在含 referenced 页的章节/书里整批失败**（不是跳过、不是部分成功）。修 `_page_or_error` 会让 referenced 页**进入** chapter/book target 集 → 行为变化必须被 AC 覆盖，否则修复即"静默扩大 Run 范围"。 | §3.2 探针 1 | In：同一门槛修复；AC-R1 增加「混合 chapter scope 展开成功且同时含 managed + referenced」；卡面明写该行为变化与 Run 成本影响 |
| **F3** | **P2（L10③ 的正确性面）** | `handlers.py:396-409`（detect 在 commit 前写 region）；`core_assembly.py:1501-1534`（`_create_detected_region`→`editing.create_region`）；`application/editing/service.py:467-475`（native lineage 按**写入时**的 binding 盖戳）；`pipeline.py:970-972`（binding 变化只在 commit 才比对）；`service.py:865-867`（`__fea10_guard__` 机制已存在） | 一旦像素变成「可变的当前 binding 图」，在「解码 → 建 region」之间 binding 改变会把 **B1 图像的坐标盖成 B2 的 native**（正是 L10③ 警告的 native 化）。managed 静态图时代该窗口不产生新风险；本卡会把它变成可达路径。 | 代码事实（见左列） | In：`handle_detect` 在调用 `region_creator` **之前**用 `step_run.input_refs["__fea10_guard__"]` 复核当前 commit guard digest；不一致 → `StepExecutionError("INPUT_REVISION_CHANGED")`，**零 region 写**；注入 `commit_guard` reader（装配期 `run_guard_value` 已有） |
| **F4** | **P2（契约要求缺失）** | `core_assembly.py:379-411`（provider 读图无 gate）；`core_assembly.py:1630-1637`（gate 只在 commit）；`core_service.py:4458`（resolve 有 gate）；`core_service.py:5072-5103`（另一份 gate 实现） | C-17 §3.3 逐字要求「**Run 输入**」在授权校验外检查 publication gate；当前 provider 读图完全没有 gate，且 gate 谓词已有**两份**实现（core_service / assembly），本卡若再加一份就是第三份。**码投影说明**：§3.3 的 `SOURCE_ACCESS_DENIED` 是 C-17/C-16 读面的码；旧 Run 命令面按 §8:352「旧命令不重映射」不新增/不改码，故 Run 面投影为 `TARGET_NOT_FOUND`（目标展开/commit guard，`core_assembly.py:1633-1637` 既有先例）或 `PROVIDER_FAILED`（step 读图），并把 `SOURCE_ACCESS_DENIED` 记入 step detail/stderr；该解释须写进卡面，避免后续审查者再开同一 finding。 | `FEA-C17…:173`、`:352`；代码两处 | In：抽**一个** `read_gate(page_id)` 谓词（unavailable/pending/None），同时供 ①`run_source_guard` ②`_ManagedPageImageSource` ③`pipeline._catalog.source_gate_reader`（目标展开）使用；refusal 分别投影 `TARGET_NOT_FOUND`（Run 面）/`PROVIDER_FAILED`（step 面），detail 记录 `SOURCE_ACCESS_DENIED` |
| **F5** | **P2（不得造第二套规则）** | `library.py:412-429`（`_visible_page_where` = C-15 §4.1 引用谓词，含 `verified_digest=e.content_digest`）、`:508-524`（`get_page` 用 V）；`pipeline.py:1421-1434`（target 门槛是另一段手写 SQL，只看非空） | referenced target 若只查「有 healthy binding」，会把 **V 为假**（`integrity_status≠complete` / digest 不一致 / 尺寸为 0）的页放进 Run，与 C-15 §4.1/§4.2 的可见性口径不一致。 | 代码事实 | In：`_page_or_error` 的 referenced 分支**复用同一 V 谓词**（推荐 `SqliteLibraryRepository` 暴露一个 classmethod 供 catalog 复用；或给 catalog 注入 `page_visibility` reader）；禁止在 pipeline 里第三次手写该谓词 |
| **F6** | **P3（既有不一致，被本卡放大）** | `infrastructure/importing.py:137-157`（导入 width/height 用 `PillowImageDecoder.decode`，**无 exif_transpose**）vs `application/importing/referenced/reader.py:174`（rendition **有** `ImageOps.exif_transpose`） | 带 EXIF 方向的 referenced 图：provider frame 尺寸 = rendition（转置后）尺寸，可能 ≠ `pages.width/height`（导入方向）；`region_crop` 用 region geometry（导入方向）去裁 rendition frame → 可能错位。 | 代码事实 | Limitation **L-R4**；AC-R2 断言 frame 尺寸 = rendition 尺寸；卡面注明「EXIF 方向源的坐标一致性不在本卡」；后续卡统一导入/rendition 方向 |
| **F7** | **P3（边界）** | `core_assembly.py:387-392`（无条件访问 `page.managed_original_ref`）；`domain/pages/entities.py:78-100`（`PageView` 无该属性）；`resolve.py:94-100`（entry 尺寸缺失才回读 page 尺寸）；`core_service.py:4480-4489`（Secret-G 只在 resolve cache-miss 消费） | ①V 真但不可构造为 `Page` 的 referenced 页（width/height NULL）会走 `PageView`，当前 `_page_image` 会 `AttributeError` → 非预期码；②**加密 referenced 源无法 Run**：Run 没有 Secret-G 通道（Host 只对 resolve 提供 `IssueSecretGrantsAsync`）→ 只能 typed `SOURCE_PASSWORD_REQUIRED`。 | 代码事实 | Limitation **L-R2**；实现用 `getattr(page, "managed_original_ref", None)`/`source_mode` 分支，refusal 用固定安全文本；卡面写明加密源 Run 不支持 |
| **F8** | **P3（域外，登记）** | `core_service.py:2753-2769`（`_fetch_page_counts` 的 WHERE 要求 `managed_original_ref IS NOT NULL`） | 书架/书列表页数对 referenced 页计 0（用户可见）。与本卡 Run 写域无关，但会让人误以为「referenced 页不存在」。 | 代码事实 | §11 P3；建议另立小卡，不在本卡域内 |

---

## 5. In / Out 冻结草案（到文件/函数级）

### 5.1 In（建议冻结；共 4 个生产文件 + 3 个新测试文件）

| # | 冻结项 | 文件 / 函数 | 说明（最小性） |
|---|---|---|---|
| **I-1** | referenced 目标进入 | `src/infrastructure/sqlite/pipeline.py`：`_page_or_error`、`_region_or_error` | `_page_or_error`：SQL 增选 `p.source_mode`；referenced 时**不再要求** `managed_original_ref`，改为要求 ①`source_hash` 非空 ②V 谓词（复用 F5 的单一实现）③read gate open；metadata **形状不变**（不新增键，避免 prepared digest 形状变化）。`_region_or_error`：SQL 谓词改 `(p.managed_original_ref IS NOT NULL OR p.source_mode='referenced')`，保留 `width/height` 与 `_ensure_lineage_readable`。新增 `source_gate_reader` 属性（沿 `guard_reader` 先例，`None` 时保持旧行为） |
| **I-2** | provider 像素源（核心） | `src/bootstrap/core_assembly.py`：`_ManagedPageImageSource.__init__`/`_page_image`/三个端口方法 | `_page_image` 按 `getattr(page,"source_mode","managed")` 分支：referenced → ①`read_gate` ②`prepare_referenced_rendition(page_id, repository=…, access=…)` ③必要时 `access.claim_secret_for_binding(...)` 取一次性密码 ④`render_prepared_rendition(..., image_decoder=…, document_raster=…, password=…)` ⑤PNG → Pillow `Image.open/load`；所有 `SourceImportError` → `ProviderError`（`PROVIDER_FAILED`）**固定安全文本**（禁绝对路径/locator/entry 名）。managed 分支**逐字节不变**。**不发布 catalog、不写 rendition_cache、不新增 rendition_kind、不新增 key** |
| **I-3** | 单一 gate 谓词与装配 | `src/bootstrap/core_assembly.py`：`assemble_core_services`（handler 构建前后） | 在 `source_sync_store` 可用处定义**唯一** `read_gate(page_id) -> "unavailable"|"pending"|None`；`run_source_guard`（`:1623-1641`）改用它（refusal 仍 `PipelineError("TARGET_NOT_FOUND")`，并捕获 `SourceImportError`→同码）；注入 `pipeline._catalog.source_gate_reader`；`_ManagedPageImageSource(access=source_read_refs, gate=read_gate, image_decoder=…, document_raster=…)` |
| **I-4** | detect 前置复核（F3） | `src/infrastructure/providers/handlers.py`：`HandlerDependencies`、`handle_detect`；`core_assembly.py` 装配 `commit_guard=run_guard_value` | 在 `region_creator` 之前复核 `step_run.input_refs["__fea10_guard__"]` == `snapshot_digest(current commit_guard)`；不一致 → `StepExecutionError("INPUT_REVISION_CHANGED")`。`None` 依赖 → 跳过（所有旧单测构造不变） |
| **I-5** | commit guard 失败投影（推荐、小改） | `src/infrastructure/sqlite/pipeline.py`：`commit_step` 中 guard 的进入位置 | 把 `source_commit_guard` 的 `ExitStack.enter_context` 移到 `BEGIN IMMEDIATE` 之前（lease 仍持到 commit 结束），使 guard 的 `PipelineError` 不被 `:1065-1068` 吞成 `db_failed`，由 `service.py:1124-1129` 投影为 `TARGET_NOT_FOUND`。若 Owner 判定风险大，可退化为「保留 `DB_FAILED` + 登记 limitation」，但 AC-R4 必须相应降级为「typed 失败 + 零写」，并在卡面写明选择 |
| **I-6** | 测试 / 证据 | 新增 `tests/fea11/test_source_rendition_source.py`、`tests/fea11/test_source_rendition_run.py`、`tests/fea11/test_source_rendition_gates.py`；`verification/FEA-11-RENDITION-1/**` | 真实 zip/PNG 双图、真实 grant（复用 `tests/fea11/conftest.py:161-229`）、真实 `run_source_guard` 接线、真实 `_ManagedPageImageSource`；禁 `_StubImages` |

### 5.2 Out（明确不改）

| # | 不做项 | 理由 / 边界 |
|---|---|---|
| **O-1** | Host/App/`apps/**` 任何改动；Run 的 grant 铸/撤通道 | F1：需 C-06/C-16 wire 复用 + .NET 门禁，属另一卡（`FEA-11-RUN-GRANT-1` 候选） |
| **O-2** | `src/bootstrap/core_service.py`（resolve/`_assert_source_sync_gate`/Run dispatch） | resolve 面已正确；本卡不碰 wire 面（F4 的 gate 复用可只在 assembly 内做，不改 core_service） |
| **O-3** | `src/application/importing/referenced/**`（resolve/reader/runtime）、`resource_channel/**`（grant/strict read/rendition cache） | 只**复用**，不改语义；`prepare_referenced_rendition` 是唯一选择入口（§7.2/§7.3） |
| **O-4** | `schema.py`/迁移/新表/新列；`rendition_kind` 扩展；新依赖 | v8 已冻结（`schema.py:732-733`）；无新包（Pillow/pypdfium2 已在闭包内） |
| **O-5** | `doc/plan/**`、`doc/contracts/**`、18 pins、`doc/tasks/FEA-11.md` 历史字节、STATUS/PLAN/LEDGER | 零契约字节；不得回填 FEA-11 的 AC11-5/AC11-9；Lead 维护 |
| **O-6** | reader/导出/渲染/`core.detect`/单 region rerender 等非 Run 读面 | 除非 L10 证明确需；本卡只做 Run 目标与 provider 读图（`core.detect` 收 base64 由 Host 供图，`core_service.py:6577-6640`，不经过本图源） |
| **O-7** | 删除/GC/回收站/扫描/调度/watcher/UI/通知 | 硬边界（卡片 `out_of_scope` 一致） |
| **O-8** | 真实用户数据/AppData/外部卷；push | 硬边界；测试文件用隔离根 |
| **O-9** | 让 provider 发布 catalog 资源、写 `rendition_cache`、或调用 `handle_resolve_page_resource` | 会引入 GC/预算/目录增长与「第二套发布语义」；违反最小性 |
| **O-10** | 新错误码（尤其 `SOURCE_*` 进入 Run 命令面） | C-17 §8:352「旧命令不重映射」；Host allow-list 不变（`HostCommandRegistry.cs:30-37`） |
| **O-11** | 宣称「referenced 页 Run 产品可用」「L10 全部已修」「AC11-5/9 回填」 | F1/L-R1 仍成立；必须写 limitation |

---

## 6. AC-R1…AC-R7（可验证条款 + 判别性测试要求）

> 通用要求：每条 AC 必须有「**删掉实现 / 改坏关键分支必须变红**」的测试；像素类断言**禁止 stub**（不得使用 `tests/fea11/test_source_lineage_run.py:122-130` 的 `_StubImages` 模式）；真实文件放隔离根（见 §8）。

### AC-R1 目标进入（page / chapter / region scope）
**冻结判定**：`source_mode='referenced'` 且 V 为真、binding healthy、gate open 的页，在 page-scope 与 chapter-scope（混合页）`expand` 成功，不再 `TARGET_NOT_FOUND`；`current(page_id)` 可返回快照；region-scope 在其 `width/height` 非空且 lineage 可读时成功。**live grant 是前提**（Core 侧测试直接铸 grant；生产端限制见 L-R1）。
**判别性测试**：(a) 纯 referenced 页 page-scope 展开 + `PrepareRun`/`StartRun`（真实 pipeline）；(b) 同 chapter 混合 managed+referenced 的 chapter-scope 展开，断言 target 数 = 2 且无 `TARGET_NOT_FOUND`（改回门槛 → 红）；(c) region-scope 在该页上成功（width/height 非空）；(d) 反向：`integrity_status≠complete` 或 `verified_digest≠entry.content_digest` 的页仍 `TARGET_NOT_FOUND`（证明不是「有 binding 就放」）；(e) `width/height` 为 NULL 的 referenced 页：region-scope 保持既有 `TARGET_NOT_FOUND`（`pipeline.py:1477-1478`），page-scope 若进入不得把「尺寸缺失」误报为 `SOURCE_BUDGET_EXCEEDED`（`resolve.py:92-100` 回退 `page.width`；`rendition_cache.acquire` 对非正尺寸给预算码——本卡不走 cache，需显式 typed）。

### AC-R2 像素来自**当前 binding 的真实 rendition**（判别性核心）
**冻结判定**：用**两套真实、内容不同的图**：旧图 A（写入 managed copy，模拟混合/旧路径）与新图 B（当前 binding 的 source entry）。断言 `page_frame` 的宽高与像素标记只匹配 B；`page_png` 解码后像素 = B；`region_crop` 的 bbox 在 B 的坐标系上命中标记。用真实 production pipeline + `run_source_guard` 接线 + 记录型 detector：断言 detector 收到的像素来自 B（不是 A），且 detect 产出 region 的 native lineage 绑定到 B 的 binding。
**判别性测试**：把图源改回 managed original（A）或旧 entry → 测试必须红；断言不能只比较尺寸（A/B 尺寸不同 + 标记像素不同，双重判别）。

### AC-R3 旧 managed 路径零回归
**冻结判定**：managed 页（`source_mode='managed'`）的 `TargetSnapshot.metadata` 键集合与 `commit_guard` 形状**不变**；`page_frame/region_crop/page_png` 与原实现一致（尺寸 + PNG 载荷）；managed 分支**从不**调用 grant registry / gate（注入一个「任何调用即失败」的 access/gate 探针，managed 路径必须不触发）；混合页（referenced + `managed_original_ref` 非空）按 AC-R2 走 binding 图（行为变化在卡面登记）。
**判别性测试**：managed 用例 + 「access 被调用即红」的哨兵；把 `source_mode` 判断写错（managed 走 referenced 分支）→ 红。

### AC-R4 typed 拒绝与零写（binding 变化 / 授权撤销 / 门禁 / 摘要冲突）
**冻结判定**（每条都要求：失败为 typed、无崩溃、无业务写、无部分产物）：
1. prepare→accept 之间 binding 变化 → `RUN_STALE_PREVIEW`；
2. accept→commit 之间变化 → step `FAILED`（`LOCK_CHANGED` 或 `INPUT_REVISION_CHANGED`，按既有提交面），affected 表零写；
3. 无 grant / grant revoked / expired：**读图前**拒绝（`PROVIDER_FAILED`，detail 含 `SOURCE_ACCESS_DENIED`/`SOURCE_GRANT_REVOKED`），**解码器不被调用**（spy decoder 0 次）；
4. gate pending：目标展开 `TARGET_NOT_FOUND` 或读图 `PROVIDER_FAILED`（依失败点），零解码；
5. 读后、写 region 前 binding 变化（F3）：`INPUT_REVISION_CHANGED`，region/revision/lineage 行数不变；
6. 解码预算超限（`max_decode_bytes`）或 entry 缺失/损坏：`PROVIDER_FAILED`/`INVALID_INPUT` typed，零写。
**判别性测试**：为每条做独立用例；3/5 用 spy/monkeypatch 计数（解码 0 次、写 0 行）；改坏 guard/goal 顺序必须红。

### AC-R5 不建第二套选择规则
**冻结判定**：resolve 与 provider 对同一页调用**同一** `prepare_referenced_rendition`，得到的 `(source_id, version_id, entry_id, decoder_name, decoder_version, params_digest, verified_digest, rendition_kind)` 完全一致；provider **不**自行推导 cache key/resource_id；已发布路径的 v2 key 仍等于 `_referenced_resource_id(prepared)`（`core_service.py:4607-4632`）；不新增 key 公式/不新增 rendition kind。**静态约束**：若将来引入缓存复用，必须用 `rendition_cache.rendition_key(...)` 的同参（`rendition_cache.py:22-27`），**禁止**使用 `prepared["cache_key"]`（`resolve.py:107-118`）作为缓存键（两者派生不同，见 L-R7）。
**判别性测试**：同一 fixture 分别走 resolve 与 provider，断言选择元组相等；把 provider 改成「读 page.managed_original_ref」或「另算 key」→ 红。

### AC-R6 零契约/schema/依赖/wire 漂移
**冻结判定**：`git diff <base>..HEAD -- doc/plan doc/contracts src/infrastructure/sqlite/schema.py apps/` 为空；`verify_pins.ps1` **18/18 PASS**；`python tools/generate_api_inventory.py --check` PASS；无 `pyproject.toml/requirements*.txt` 变更；Run 命令集与 payload 形状不变（`git grep` 无新命令名）；Core protocol minor 不变。
**判别性测试**：门禁命令实跑并留日志；scope diff 逐文件核对。

### AC-R7 门禁、证据与「不夸大」约束
**冻结判定**：`pytest tests` 不减少（参考基线 3212/10，释放时实测并记录 passed/failed/skipped）；`pytest tests/fea11` 只增不减（本次实测 108）；`check.ps1` PASS；.NET 全量按项目门禁实测或 `NOT_RUN` 并写明理由；`git status --porcelain` 仅 allowed_paths；EV/Resource Manifest/Handoff 完整；**Handoff 必须写明 L-R1（无 Run grant 通道）与 L-R2（加密源）**，且不得声称产品级 referenced Run 可用、不得回填 FEA-11 AC。
**判别性测试**：一条「**无 live grant 时 Run 不能执行且为 typed**」的负向用例（证明限制真实存在，防止 Reviewer 误判为已闭环）；门禁日志含 shell/解释器头与 EXIT。

---

## 7. allowed_paths / Owner / Reviewer / base / depends_on / 门禁草案

### 7.1 allowed_paths（建议冻结；逐文件）

**卡/评审/交接/证据**
- `doc/tasks/FEA-11-RENDITION-1.md`
- `doc/reviews/FEA-11-RENDITION-1-*.md`
- `doc/handoffs/FEA-11-RENDITION-1-*.md`
- `verification/FEA-11-RENDITION-1/**`

**生产代码（4 个文件）**
- `src/infrastructure/sqlite/pipeline.py`（I-1、I-5）
- `src/bootstrap/core_assembly.py`（I-2、I-3、I-4 装配）
- `src/infrastructure/providers/handlers.py`（I-4）
- `src/infrastructure/sqlite/library.py`（**仅当**按 F5 暴露单一 V 谓词 classmethod 时需要；否则不列）

**测试（3 个新文件；不改既有测试/conftest）**
- `tests/fea11/test_source_rendition_source.py`（新）
- `tests/fea11/test_source_rendition_run.py`（新）
- `tests/fea11/test_source_rendition_gates.py`（新）

**明确不在 Owner 写域**：`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`、`doc/plan/**`、`doc/contracts/**`、`src/infrastructure/sqlite/schema.py`、`src/bootstrap/core_service.py`、`apps/**`、`tests/fea11/conftest.py`、`tests/fea11/test_source_lineage_run.py`。若实现确需触碰其中任一项（例如 conftest 复用 helper），Owner **必须先停下报 DSH 增列 allowed_paths**（SCAN-2 P2-4 先例），不得静默扩域。

### 7.2 Owner / Reviewer

- **Owner 建议：Codex**（Python/Core + provider/rendition 语义 + 真实 fixture；与 `FEA-11-LINEAGE-1` 的 `suggested_owner: codex`、`lineage-impl`（DSH Team teammate）先例一致）。ZCode 作为备选（独立 Feature/长任务能力具备，但其主责在 UI/Avalonia；本卡零 .NET）。DSH 保留 Appointment 与最终指派。
- **许可证/角色**：本卡**不新增依赖**（Pillow/pypdfium2 已在既有闭包），不移植外部代码、不随包字体 → 无 GPL/AGPL 影响；角色约束按 `AGENTS.md`（2026-10-31 裁决：Review 只要求上下文独立）。
- **Reviewer：独立上下文 fresh subagent**（不得由实现会话/实例自审；报告须记录 session 与 `reviewer_kind=subagent`）；Lead 保留 findings 处置与集成验证。

### 7.3 依赖与 base

- `depends_on`：`FEA-11-LINEAGE-1`（done；L10 来源 + lineage guard）、`FEA-09`（done；referenced 读面/grant/cache/`prepare_referenced_rendition`）。**建议移除 `FEA-11-SCAN-2`**（与本卡无技术依赖，仅为占位卡登记时间顺序；保留会误导 DAG）。
- `base_commit`：`987d81981`（本 review HEAD）；释放时以 DSH 固定为准。
- `branch`/`worktree`：null（沿用 main 工作树；如需 worktree 由 DSH 创建并登记）。

### 7.4 门禁（建议冻结）

1. `pytest tests` 全量不减少（实测 before/after，passed/failed/skipped 分列；skip 逐条原因）；**跑完必须检查 `git status --porcelain`**：若已知副作用改写 tracked `verification/FEA-09` 字节（LINEAGE-1:102,153 先例），按原字节恢复并记录，不得把该 churn 混入交付 diff。
2. `pytest tests/fea11` 只增不减（本 review 实测 108）。
3. `pwsh -NoProfile -File tools/governance/verify_pins.ps1` → 18/18 PASS。
4. `pwsh -NoProfile -File tools/governance/check.ps1` → PASS（记录 warnings 实测数；本 review 为 3）。
5. `python tools/generate_api_inventory.py --check` → PASS（`IHostController`/`RunContracts` 未变）。
6. `git diff --name-only <base>..HEAD` ⊆ allowed_paths；`doc/plan`/`doc/contracts`/`schema.py`/`apps/` 零 diff。
7. .NET 全量 `dotnet test apps/desktop-avalonia/NewManga.sln -c Release`：本卡零 C# 改动，仍按项目门禁实测或 `NOT_RUN` + 理由（参考基线 1527/0/86）。
8. 无新依赖；无真实用户数据/AppData/外部卷；不 push；EV/Resource Manifest/Handoff/独立 Review/DSH 集成。

---

## 8. 测试策略与证据可行性

### 8.1 可扩展面（复用，不改）

| 现有面 | 位置 | 可复用点 |
|---|---|---|
| 真实 source 树/引用页/grant | `tests/fea11/conftest.py:161-229`（`mint_grant`，真实 HMAC + 真实文件 facts）、`:242-278`（`add_referenced_page`，`managed_original_ref=NULL`）、`:281-333`（`add_source_tree`） | 真实 zip + 真实 binding + live grant；`add_referenced_page` 默认纯 referenced（正好是 AC-R1 形态） |
| 混合页构造 | `tests/fea11/test_source_lineage_native.py:85-97`（`seed_page` 写 `managed_original_ref='original/{page}.png'`） | 直接复用作 AC-R2「旧图 A」页（但**不得**复用 `_StubImages`） |
| 真实 pipeline + 真实 handlers | `tests/fea11/test_source_lineage_run.py:138-199`（`_build_pipeline`） | 换成真实 `_ManagedPageImageSource` + 真实 `run_source_guard` 即为 AC-R2/AC-R4 的装配级用例 |
| image source 单测 | `tests/providers/test_bootstrap_providers.py:143-185` | managed 分支回归模板（AC-R3） |
| resolve/cache 语义 | `tests/fea11/test_source_resolve.py`、`tests/fea09/test_referenced_resolve.py`、`tests/fea09/test_rendition_cache_*` | AC-R5 选择一致性、AC-R4 摘要冲突 |
| Run 运行时 | `tests/core/test_p13_run_runtime.py:63-83`（真实装配 + 真实库） | PrepareRun/StartRun 命令面用例 |

### 8.2 需新建 / 隔离根

- 新测试文件见 §7.1。**真实图 fixture 生成**：在 `tmp_path` 下用 Pillow 写两张**内容不同**的 PNG（A: 30×20 红底左上 4×4 黑块；B: 12×7 绿底右下 3×3 蓝块），再打成真实 zip（`write_zip`）；**不要**把二进制 fixture 提交进仓库（避免大文件与许可证问题）。
- 隔离根：手工/verification 证据与脚本放 `G:\CODEX\New Manga.workspace\FEA-11-RENDITION-1\`；自动化测试优先 `tmp_path`（可移植），**不要**沿用 `tests/fea11/conftest.py:46` 的硬编码 `G:/CODEX/New Manga.workspace/FEA-11`（跨卡耦合，见 P3）。不得触碰真实用户数据。
- 量级估计（供排期）：生产 ~150–250 行净增；测试 ~700–1000 行；证据 3–6 个日志/清单。
- flaky 风险：**低**。全部为确定性文件 + Pillow 解码 + 注入时钟的 grant（`mint_grant` 可传 `clock`）；无 watcher/无睡眠/无网络。主要风险是 Windows 临时目录清理与 `:memory:` 连接生命周期（既有模式已覆盖）。

---

## 9. 契约影响表（预期零触碰）

| 契约/面 | 是否改 | 证据/说明 |
|---|---|---|
| **C-17 v1.1** | **否** | 不新增命令/DTO/capability；`resolve_page_resource` 形状与 v2 key 公式不变（`FEA-C17…:329-337`）；§3.3/§7.1 是**兑现**不是修改；`git diff -- doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md` 为空；C17 pin `aefa0fa5b17e` 不变 |
| **C-15** | **否** | 无 schema/DDL/rendition_kind 变化；§4.1 R / §4.2 resolve 面语义不变；`git diff -- doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md` 为空；C15 pin `d8c0a3bcfc21` 不变 |
| **C-16** | **否** | grant scope/读取来源/失败码不变；provider 只经 grant facts 读取（`C16:66-70,182`）；diff 为空；C16 pin 不变 |
| **C-08（Run 快照）** | **否** | `requestedTargets` 形状不变（metadata 不新增键，见 I-1）；`preparedDigest` 四元组算法不变（`application/tasks/store.py:65-71`）；C08 pin `453f993c1a16` 不变 |
| **C-05（可见性）** | **否** | 复用既有 V 谓词（`library.py:412-429`），不改可见性语义；C05 pin 不变 |
| **C-14 / C-01b / C-13 / C-09 / C-10 / C-11 / C-12 / C-06 / C-02 / C-03 / C-04b / FEA-01** | **否** | 均在 `doc/plan`，diff 为空 |
| **18 pins** | **18/18 PASS** | 本 review 实测（§1） |
| **C-07 / API inventory** | **否** | 不改 `IHostController.cs`/`RunContracts.cs`/`FEA-C07_API_INVENTORY.md`；`generate_api_inventory.py --check` 应 PASS |
| **Schema / migration / 依赖 / wire** | **否** | 无 `schema.py` diff、无迁移号、无新包；命令集/协议 minor 不变 |

---

## 10. 风险与 limitation 预登记（≥5）

- **L-R1（blocker for product claim）**：**无 Run-scoped source-read grant 通道**（F1）。本卡交付后，生产环境的 referenced 页 Run 仍会在读图/提交处被拒（`PROVIDER_FAILED`/`DB_FAILED`），只有 import/sync apply 后 ≤300s 的 grant 窗口内可能通过；同样的 grant 约束也作用于 resolve（重启后 `SOURCE_ACCESS_DENIED`）。本卡只交付 Core 侧能力；后续需 Host 为 Run 铸 grant 的切片（建议 `FEA-11-RUN-GRANT-1`）。**禁止**写成「referenced 页 Run 已可用」。
- **L-R2**：**加密 referenced 源无法 Run**（Run 无 Secret-G 通道；`claim_secret_for_binding` 只在 resolve cache-miss 由 Host 铸发）。表现为 typed `SOURCE_PASSWORD_REQUIRED`，不是崩溃。
- **L-R3**：**chapter/book-scope 行为变化**（F2）：含 referenced 页的章节/书，Run 目标集从「整批失败」变为「包含 referenced 页」，成本与产物范围变化；卡面必须明写，UI/通知不承诺。
- **L-R4**：**EXIF 方向不一致**（F6）：provider frame 尺寸 = rendition（exif_transpose 后）尺寸，可能 ≠ `pages.width/height`（导入方向）；旧 region geometry 在方向源上可能错位。本卡不统一方向。
- **L-R5**：**混合页行为翻转**：`referenced + managed_original_ref 非空` 的页（测试/损坏/遗留形态）从此按 binding 图；旧 managed 副本被忽略。属预期修复，但需在卡面登记，且不做数据迁移。
- **L-R6**：**detect 的 region 写在 step commit 之外**（既有形态）：commit 失败可能留下 machine region；F3 的复核只把「binding 竞态窗口」缩到 guard 复核→写 region 之间，不提供事务回滚。
- **L-R7**：**provider 不走 rendition_cache**（有意）：每次读图重复解码（与 managed 路径同成本画像：`region_crop` 每 region 解码一次）；预算按 grant `max_decode_bytes`；后续若要复用 cache 需另卡。**实现约束（防止未来误用）**：`resolve.py:107-118` 的 `prepared["cache_key"]`（`"\0".join(...)`，不含 kind）与 `RenditionCache.rendition_key(...)`（`json.dumps([source,version,entry,kind,decoder,decoder_version,params])`）是**两套派生**，且 `acquire` 用后者查表、`_record_rendition_cache` 用前者写行；任何缓存复用必须用 `acquire` 的同一组参数，**不得**把 `prepared["cache_key"]` 当缓存键。
- **L-R8**：**Run 面错误码为既有 family**（`PROVIDER_FAILED`/`INVALID_INPUT`/`TARGET_NOT_FOUND`/`DB_FAILED`/`INPUT_REVISION_CHANGED`），不新增 `SOURCE_*` 投影；用户看到的是「源不可用」类通用文案（无路径泄露）。
- **L-R9**：**Run 快照不含 binding/rendition 观测**（metadata 形状不变）→ 无法从 Run 快照直接诊断「用了哪个 binding 的图」；只能从 step detail/lineage 推断。
- **L-R10**：**width/height 为 NULL 的 referenced 页**：page-scope 可能可进入（像素由解码得出），region-scope 仍按既有谓词 `TARGET_NOT_FOUND`；此类页 V 为假，本卡不承诺其可用。

---

## 11. P3 观察（非阻断，供 Lead 处置）

1. **`_fetch_page_counts` 排除 referenced 页**（`core_service.py:2753-2769`）：书架页数对纯 referenced 书显示 0。域外（非 Run），但用户可见；建议另立小卡或并入 UI/库面切片。
2. **`run_source_guard` 无直接测试**：全仓仅 `tests/fea10/test_commit_zero_write.py` 以 fake 注入 `source_commit_guard`；生产 guard 的 grant/gate 分支从未被端到端覆盖（正是 F1 长期未被发现的原因）。本卡 AC-R4/R7 应补上。
3. **gate 谓词有两份实现**：`core_service.py:5072-5103` 与 `core_assembly.py:1630-1637`；本卡应抽一份（I-3），避免第三份；core_service 侧的去重可作为后续小改。
4. **`_page_image` 对 `PageView` 不安全**（`core_assembly.py:387-392`）：`getattr(page,"managed_original_ref")` 在 V 真但不可构造的页上会 `AttributeError`（既有）；实现 referenced 分支时顺手用 `getattr(..., None)` + `source_mode` 判断，不扩大行为。
5. **`tests/fea11/conftest.py:46` 硬编码 `G:/CODEX/New Manga.workspace/FEA-11`**：跨卡耦合、不可移植；新卡测试建议 `tmp_path`，不要把新 fixture 再塞进 FEA-11 根。
6. **`_ManagedPageImageSource` 名称将不再准确**（同时读 rendition）；建议保留类名 + 改 docstring（避免无谓 rename churn），或后续清理卡统一改名。
7. **`core.detect`（`core_service.py:6577-6640`）**：Host 以 base64 供图、不经本图源；若 App 对 referenced 页调用它，行为不变（Host 侧供图失败）。不属本卡，但值得在 FEA-12-UI 残余中登记。
8. **C-17 §8:352「旧命令不重映射」** 是本卡「零 Host 改动」的治理依据，建议写进卡面以免后续 Reviewer 要求 `SOURCE_*` 投影。

---

## 12. 摘要

- **裁决：`READY-TO-FREEZE`（条件：F1 写成 limitation；AC-R1 限定 Core + live grant）。** 契约侧 `C-17 §7.2/§7.3/§3.3/§7.1` + `C-15 §4.1/§4.2/§2.7` + `C-16 §2/§7` 已完整覆盖「选择函数、门控、可读谓词、读取来源、发布边界」，**零契约字节**，不需要 UNFREEZE；唯一可想象的 UNFREEZE（新增 rendition kind 或给 §7.2 加一句澄清）都不必要且不推荐。
- **代码事实**：L10① 复现（`pipeline.py:1433-1434`）、L10② 复现（`core_assembly.py:379-411`，实测 `INVALID_INPUT`）、L10③ 成立（混合页 + `_StubImages`）；额外发现 **chapter/book-scope 整批失败**（F2）与 **Run 无 grant 通道**（F1，实测 `SOURCE_ACCESS_DENIED`→`db_failed`）。
- **范围**：Core-only、4 个生产文件（`pipeline.py`/`core_assembly.py`/`handlers.py`，可选 `library.py`）+ 3 个新测试；不碰 `core_service.py`/契约/schema/Host/App；provider **不发布、不写 cache、不新增 wire/key/kind**。
- **AC**：AC-R1…R7（目标进入、真实新图判别、managed 零回归、typed 拒绝与零写、单一选择规则、零契约漂移、门禁与不夸大），每条含判别性要求；像素断言禁止 stub。
- **Owner=Codex**（备选 ZCode）；Reviewer=独立上下文 fresh subagent；base `987d81981`；depends_on `FEA-11-LINEAGE-1` + `FEA-09`（建议去掉 SCAN-2）。
- **契约影响**：C-17/C-15/C-16/C-08/C-05 及 18 pins 全部零改动（本 review 实测 pins 18/18、check PASS、fea11 108 passed）。
- **必须由 Lead 裁决的争议点**：①F1 是否作为 limitation 接受（推荐）还是要求本卡并入 Host 铸 grant 切片（则本卡 BLOCKED/拆分）；②F2 的 chapter/book-scope 行为变化是否在卡面冻结；③I-5（commit guard 投影）是否纳入本卡。

RENDITION-1-SCOPE: READY-TO-FREEZE — 契约零字节（C-17 §7.2/§7.3/§3.3/§7.1 + C-15 §4.1/§4.2/§2.7 + C-16 §2/§7 已足够覆盖 provider 进程内读取，无需新 wire/新 kind/新错误码）；范围冻结为 Core-only：`pipeline.py` 两个目标门槛 + `core_assembly.py` 图源/gate/装配 + `handlers.py` detect 前置复核（+ 可选 `library.py` 单一 V 谓词），不碰 core_service/契约/schema/Host/App。**P1 前提**：F1「Run 无 source-read grant 通道」使生产级 Run 仍不可端到端执行 → 必须写成 limitation L-R1 并登记后续候选；若 DSH 以「产品级 Run 可用」为完成标准，则本卡应改判 BLOCKED/拆分。附带发现 F2「chapter/book-scope 含 referenced 页即整批失败」与本卡同一门槛修复，需在卡面与 AC-R1 登记。
