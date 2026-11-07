# FEA-11-L-R11-GATE-UNIFY-1：L-R11 两读面 publication gate 统一（Core 单谓词）— 证据（EV）

> 本 EV 只陈述**实跑**事实；未跑项目逐项标注。本卡是 **Core-only 实现卡**：把 Core 内 publication gate
> 判定统一为**唯一谓词**（healthy + publication 行状态 + **全链**检测；旧 v7 legacy 全链无 publication → `open`；
> 新同步链缺 publication 行 → fail-closed），并由 `core_assembly.read_gate`（Run 目标/commit guard/provider）、
> `core_service._assert_source_sync_gate`（resolve/reader）与 `AuthorizeSourceReadForRun` 的 per-page 路径共同消费。
> **不得**把本卡写成「C-17 §3.3 已完全实现 / L-R11 全部关闭」；`relation='added'` 缺行、写面/章级面仍未覆盖
> （见 §7 limitation L-R11-a…e）。

- Task：`doc/tasks/FEA-11-L-R11-GATE-UNIFY-1.md`（`base_commit=2175238ab`；`status=ready` 由 Lead 维护，本卡未改）
- 权威 scope review：`doc/reviews/L-R11-GATE-UNIFY-scope-r1.md`（recommended；方案 C 单谓词 + 全链）
- 前提契约：C-16 v1.7 §2.4（`doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md:90`，PREREQ `2175238ab`，1/18 pin）
  + C-17 §3.3（`doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md:171-173`，零字节）
- 分支/环境：`main`；Windows 11 / PowerShell 7 / CPython 3.14.6 / pytest 9.1.1；未建 worktree；未 push；
  零新依赖；零 schema/迁移；零 wire/命令/能力/错误码/`PROTOCOL_MINOR` 变更

## 1. 交付 commit 链（显式 pathspec；未 push）

| # | commit | 内容 | 文件 |
|---|---|---|---|
| 1 | `1c1c9ca2f` | 实现：Core 单谓词 + 两处委托 + docstring 修正 | `src/infrastructure/sqlite/source_sync.py`（+127/−25）、`src/bootstrap/core_assembly.py`（+19/−14）、`src/bootstrap/core_service.py`（+26/−24） |
| 2 | `86cd1d124` | 测试：真实 v7→v8 / 一跳 / 两跳 / pending-open 判别测试（6 例） | `tests/fea11/test_source_gate_unify.py`（新增 645 行） |

- **delivery_head = `86cd1d124`**（实现 `1c1c9ca2f` + 测试 `86cd1d124`）；随后同批 docs/evidence 提交（本 EV /
  `RESOURCE-MANIFEST.json` / Handoff / 卡面「交付记录」）。
- 实现起点：派发时 HEAD 实测 `28a2826af`；实现/测试提交落在 `2e4d6128e`（Lead 并发 docs commits）之上。
  卡面 `base_commit=2175238ab` 与本卡实现 diff 的关系见 §6。

## 2. 实现语义（单谓词 + 四态 + 委托）

### 2.1 唯一判定（`src/infrastructure/sqlite/source_sync.py`）

- `_publication_gate_verdict(conn, page_id)`：Core 内**唯一** publication-gate 判定，返回四态：

  | 状态 | 条件 | 含义 |
  |---|---|---|
  | `open` | 当前 binding 的 publication `read_gate='open'`，或当前 binding 无行且**全链无任何 publication** | 可读；后者即 v7 legacy / C-16 导入形态（C-16 v1.7 §2.4） |
  | `pending` | 当前 binding 有行且 `read_gate='pending'` | 待 Host ACK（C-17 §3.3） |
  | `unavailable` | 无（非 superseded）当前 binding，或当前 binding 非 healthy | 既有「不可读」状态（消费方码不变） |
  | `corrupt_chain` | 当前 binding **无行**，但沿 `page_bindings.previous_binding_id` 的**全链**任一 binding 有 publication | 新同步链缺行 = 损坏，fail-closed，**不得**当 legacy（C-17 §3.3；L-R11） |

- 链检测为**全链 walk**（`_binding_chain_ids`，cycle-safe），不是一跳；`relation='added'`（previous NULL）无行时
  链检测不可见 → `open`（limitation L-R11-a）。
- `SourceSyncStore.publication_gate_of_page(page_id)` 是唯一公开入口（委托上面的判定）。
- `SourceSyncLineageFacts.page_is_sync_managed`（C-17 §7.1）改为复用同一 `_binding_chain_ids` /
  `_publication_row`，**行为不变**（既有 lineage 测试全绿）。

### 2.2 消费方（全部委托，无第二套判定）

| 消费面 | 位置 | 处理 |
|---|---|---|
| `read_gate`（Run 目标准入 / commit guard / provider） | `core_assembly.py` `read_gate` | 委托 `store.publication_gate_of_page`；仅把 `corrupt_chain` 映射为冻结三态的 `unavailable`。docstring 中「无行即 open」过期表述已删除 |
| resolve / reader 面 | `core_service._assert_source_sync_gate` | 委托同一谓词：`pending` → 既有 `SOURCE_ACCESS_DENIED "page binding is pending acknowledgement"`；`corrupt_chain` → 既有 `SOURCE_ACCESS_DENIED "page binding has no read gate"`；`unavailable` 保持交给 resolve 自身的 binding-readiness 检查（同一既有码，legacy 零漂移）；`open` 放行。**删除**原一跳 `previous_binding_id` 启发式 |
| `AuthorizeSourceReadForRun` per-page | `core_service._authorize_source_read_for_run`（`catalog.source_gate_reader`，未改代码） | 继续消费同一 `read_gate`；损坏形态下 `catalog.expand` 即 typed 拒绝（`INVALID_REQUEST`，既有 family）、**零映射**、零业务写 |

**零新增**：无新错误码 / 命令 / 能力 / wire 字段 / `PROTOCOL_MINOR` / schema / 迁移 / 依赖。

## 3. AC 判定（全部 <<MET>>）

| AC | 判定 | 证据 |
|---|---|---|
| **AC-1 单谓词唯一** | **<<MET>>** | 静态断言（`test_core_has_exactly_one_publication_gate_judgement`）：`source_sync.py` 仅 1 个 `_publication_gate_verdict` / 1 个公开 `publication_gate_of_page` / 1 个 `_binding_chain_ids`；`core_assembly` 仅 1 个 `def read_gate(` 且无 `gate_of_binding(` / `previous_binding_id`；`_assert_source_sync_gate` 无本地 row/一跳判定；`AuthorizeSourceReadForRun` 仍取 `catalog.source_gate_reader`。判别性 M4：把 resolve 面改回旧一跳启发式 → 静态用例 **RED**（见 §5） |
| **AC-2 legacy 零回归** | **<<MET>>** | `test_legacy_v7_bindings_stay_open_on_every_face`：**真实 `MigrationRunner(conn, MIGRATIONS[:7])` 造 v7**（books/chapter/source/source_locations/versions/entries/pages/page_bindings 全部 v7 行）→ 应用 v8 迁移 → 真实 `assemble_core_services`。两种 legacy 形态均 `open`：`p1`（previous NULL、无行）与 `p2`（previous 非空但**全链无 publication**）。同时验证 resolve 返回 v2 resource key、provider 读出真实 zip 成员（12×7 B）、`create_run` 目标、commit guard（真实 wire grant）、`AuthorizeSourceReadForRun` `bound_pages=1`。判别性 M1：把「无行即 corrupt」改坏 → 该用例 **RED** |
| **AC-3 L-R11 一跳 fail-closed** | **<<MET>>** | `test_one_hop_missing_publication_fails_closed_everywhere`：真实 v8 库 B1（publication `open`）+ B2（healthy、无行、`previous=B1`）→ 谓词 `corrupt_chain`、`read_gate="unavailable"`；`create_run` → `TARGET_NOT_FOUND`；commit guard → `TARGET_NOT_FOUND`（`source binding is unavailable`）；provider → `INVALID_INPUT` 且主演 `prepare_referenced_rendition`/`read_entry_bytes` **0 次调用**（真实 grant 已 mint+bind，拒绝只因 gate）；resolve/reader → `SOURCE_ACCESS_DENIED`（固定文本 `page binding has no read gate`）；`AuthorizeSourceReadForRun` → typed `INVALID_REQUEST`、零映射、全表快照不变。判别性 M2：分支改回 `open` → **RED** |
| **AC-4 全链检测（两跳）** | **<<MET>>** | `test_two_hop_missing_publication_fails_closed_everywhere`：B1（publication）+ B2（superseded、无行、`previous=B1`）+ B3（healthy、无行、`previous=B2`）→ 与一跳完全相同各面拒绝。判别性 M3：改回**只查一跳** → 该用例 **RED**（一跳用例仍 PASS，证明判别点精确） |
| **AC-5 零漂移** | **<<MET>>** | `verify_pins.ps1` → **PIN AUDIT: PASS (all 18)**（C16 `67286eeca8cb…`、C17 `aefa0fa5b17e…`）；实现 diff 仅 3 个 `src/**` 允许文件；`doc/plan`+`doc/contracts`+`schema.py`+`apps/**` 对 HEAD 零 diff（0 字节）；无新错误码/命令/能力/`PROTOCOL_MINOR`/依赖。见 §6 |
| **AC-6 门禁/证据/不夸大** | **<<MET>>** | 见 §4 实跑门禁 + §5 判别性 + §7 limitation + §8 不夸大声明；EV / Handoff / 卡面交付记录齐备 |

## 4. 门禁实跑（repo root；`main`；delivery_head `86cd1d124`）

| 项 | 命令 | 结果 | 日志 |
|---|---|---|---|
| 定向 pytest | `python -m pytest tests/fea11/test_source_gate_unify.py tests/fea11/test_source_rendition_gates.py tests/fea11/test_source_rendition_source.py tests/fea11/test_source_rendition_run.py tests/fea11/test_source_run_grant.py tests/fea11/test_source_resolve.py -q` | **78 passed**（既有 72 + 新增 6） | `logs/pytest/targeted-gate-files.log` |
| `tests/fea11` 全量 | `python -m pytest tests/fea11 -q` | **212 passed**（**before 206 → after 212**，+6 本卡新增） | `logs/pytest/tests-fea11-full.log` |
| 全量 Python | `python -m pytest tests -q -p no:warnings --tb=no` | **3369 passed / 10 skipped**（**before 3363/10 → after 3369/10**，+6，不降、skip 不变） | `logs/pytest/full-pytest.log` |
| pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PIN AUDIT: PASS (all 18)** | `logs/governance/pins.log` |
| check（默认） | `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS (3 warnings)** | `logs/governance/check.log` |
| check（-TaskPath） | 同上 + `-TaskPath doc/tasks/FEA-11-L-R11-GATE-UNIFY-1.md` | **PASS (3 warnings)** | `logs/governance/check-taskpath.log` |
| API inventory | `python tools/generate_api_inventory.py --check` | **EXIT 0** | `logs/governance/api-inventory.log` |
| 构建 | — | **NOT_RUN（不适用）**：纯 Python Core + tests，无 build 产物 | — |
| 全量 .NET | — | **NOT_RUN（不适用）**：本卡零 App/Host 改动；`apps/**` 零 diff | — |
| 真实 IPC / gated | — | **NOT_RUN（不适用）**：本卡零 wire/命令改动；`AuthorizeSourceReadForRun` 用真实 `CoreServiceServer` 的 host-control dispatch 面覆盖 | — |

- 新增文件 verbose：`tests/fea11/test_source_gate_unify.py` **6 passed**（`logs/pytest/new-file-verbose.log`）。
- 全量 pytest 后工作树无额外 tracked 变更（`verification/FEA-09` 未被触碰，无需恢复）。

## 5. 判别性（破坏 → RED → 复原 sha256 MATCH → 复绿）

工具：仓外 `G:/CODEX/New Manga.workspace/FEA-11-L-R11-GATE-UNIFY-1/mutate.py`；日志在
`logs/discriminative/**`；每例破坏后即从 baseline 字节复制复原并核对 sha256。

| # | 破坏 | 期望 | 实测 | 复原 |
|---|---|---|---|---|
| **M1** | 把「全链无 publication → open」改成「无行即 `corrupt_chain`」 | legacy v7→v8 用例 RED | `test_legacy_v7_bindings_stay_open_on_every_face` **RED**（`assert 'corrupt_chain' == 'open'`） | sha256 MATCH |
| **M2** | 把「新同步链缺行 → corrupt」改回 `open` | 一跳 + 两跳用例 RED | `test_one_hop_*` + `test_two_hop_*` **RED** | sha256 MATCH |
| **M3** | 把全链 walk 改回**只查一跳** | 两跳 RED、一跳仍 PASS | 两跳 **RED**、一跳 **PASS**（1 failed / 1 passed） | sha256 MATCH |
| **M4** | 把 resolve 面 `_assert_source_sync_gate` 改回旧一跳启发式（本地 `gate_of_binding` + `previous_binding_id`） | 静态唯一性用例 RED（且两跳 resolve 不再按统一谓词拒绝） | `test_core_has_exactly_one_publication_gate_judgement` **RED** + `test_two_hop_*` **RED** | sha256 MATCH |
| **复绿** | 全部还原后重跑新用例 | 6 passed | **6 passed** | `source_sync.py` / `core_service.py` sha256 与破坏前 **MATCH** |

计数：**判别性 4/4 RED_AS_EXPECTED + 复原 sha256 2/2 MATCH + 复绿 1/1**（`logs/discriminative/SUMMARY.txt`）。

## 6. 零漂移与 scope（实跑）

- 实现起点 HEAD `28a2826af`（会话开始实测）→ 落地于 `2e4d6128e`（Lead 并发 docs commits）之上；交付提交
  `1c1c9ca2f` + `86cd1d124`。对本卡实现 diff 而言（`git diff HEAD~2 -- src`）：
  - `src/**` 仅 3 个 allowed 文件：`src/infrastructure/sqlite/source_sync.py`（+127/−25）、
    `src/bootstrap/core_assembly.py`（+19/−14）、`src/bootstrap/core_service.py`（+26/−24）。
  - `git diff HEAD -- doc/plan doc/contracts src/infrastructure/sqlite/schema.py apps` = **0 字节**。
  - 18 pins 零改动（`PIN AUDIT: PASS (all 18)`；C16 v1.7 `67286eeca8cb…` 与 PREREQ 后一致）。
  - `git diff --check` = 0（`logs/scope/diff-check.log`）。
- **卡面 `base_commit=2175238ab` 与实现 diff 的关系（如实披露）**：`git diff 2175238ab --name-only` 包含
  `2175238ab..2e4d6128e` 间 Lead 的 docs-only commits（PREREQ closeout、C-04b/SCAN-RH 文档、handoff 等），
  与实现 diff 无关；本卡实现 diff 以 `86cd1d124^..86cd1d124` 为界（见 `logs/scope/show-*.log` 与
  `delivery-file-sha256.log`）。
- 提交隔离：两次提交均用显式 pathspec（无 `git add -A`）；未触碰 Lead 的 C-04b/SCAN-RH 文档。

## 7. Limitation（如实保留，不随本卡关闭）

- **L-R11-a（残余，关键）**：`relation='added'` 的新同步 binding（`previous_binding_id IS NULL`）缺 publication
  行时，previous 链无行可查，**无法与 v7 legacy / C-16 导入页区分**；C-17 §3.3 的「plan receipt」检测**未实现**。
  本卡只覆盖 previous 链可检测的损坏子集。
- **L-R11-b**：写面 `_refuse_pending_gate_writes` 与 reader 章级 `_refuse_pending_gate_chapter` 仍为 **pending-only**；
  损坏链形态下它们仍放行，直到逐页 resolve 拒绝。本卡未改（避免误伤 managed 页/无 binding 页）。
- **L-R11-c**：损坏状态映射既有 `unavailable` / `TARGET_NOT_FOUND` / `INVALID_INPUT` / `SOURCE_ACCESS_DENIED`，
  **无专用诊断码**（C-17 §8 禁止新增码）；仅固定文本可诊断，无新增日志行。
- **L-R11-d**：不提供损坏 publication 行的自动修复/重建；损坏库需外部恢复。
- **L-R11-e**：legacy 用例**使用真实 `MigrationRunner(conn, MIGRATIONS[:7])` 造 v7 再升级 v8**（不是 v8 内伪造
  legacy 形态）；`previous 非空但全链无 publication` 的形态也在真实库中构造并断言 `open`。

## 8. 不构成什么

- **不构成**「C-17 §3.3 已完全实现」；**不构成**「L-R11 全部关闭」。
- 未覆盖：`relation='added'` 缺行检测（L-R11-a）、写面/章级面 pending-only（L-R11-b）、专用诊断码（L-R11-c）、
  损坏行自动修复（L-R11-d）、plan receipt 检测；真实 IPC/gated 不适用本卡。
- **不构成**契约修改：18 份冻结契约零字节；C-16 v1.7 由 PREREQ 卡 `2175238ab` 冻结，本卡只实现。
- **不构成** wire/命令/能力/错误码/`PROTOCOL_MINOR`/schema/依赖/App 变更；不构成 push 授权（Lead 统一）。
- 实现 ≠ 集成：本卡仍需独立上下文 Review 与 Lead 集成门禁/closeout。

## 9. 复现（repo root）

```powershell
git log --oneline -3            # 86cd1d124（测试）/ 1c1c9ca2f（实现）/ 2e4d6128e
C:/Python314/python.exe -m pytest tests/fea11/test_source_gate_unify.py -q
C:/Python314/python.exe -m pytest tests/fea11 -q
C:/Python314/python.exe -m pytest tests -q -p no:warnings --tb=no
pwsh -NoProfile -File tools/governance/verify_pins.ps1
pwsh -NoProfile -File tools/governance/check.ps1
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-11-L-R11-GATE-UNIFY-1.md
C:/Python314/python.exe tools/generate_api_inventory.py --check
git diff HEAD~2 --name-only
git diff HEAD -- doc/plan doc/contracts src/infrastructure/sqlite/schema.py apps
```

- 判别性复现（仓外脚本，会临时改写生产文件并逐例复原）：
  `C:/Python314/python.exe "G:/CODEX/New Manga.workspace/FEA-11-L-R11-GATE-UNIFY-1/mutate.py"`。

## 10. 环境与并发披露

- 操作系统 Windows；CPython 3.14.6；pytest 9.1.1；PowerShell 7。
- 并发：共享 `main` 同期 Lead 有 docs-only 提交（`698ac9524…2e4d6128e`，C-04b residual / SCAN-RH /
  STATUS/handoff），本卡两次提交均显式 pathspec、仅含本卡允许文件；实现与测试不受 docs 提交影响。
- 证据归因：`delivery_head=86cd1d124`；本 EV/Manifest/Handoff/卡面属其后同批 docs/evidence 提交（未 push）。
