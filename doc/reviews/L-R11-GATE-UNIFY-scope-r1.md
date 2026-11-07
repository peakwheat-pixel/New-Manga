---
task: L-R11-GATE-UNIFY
title: L-R11 两读面 publication gate 统一（scope review r1）
reviewer: fresh subagent（独立上下文）
session: 5aa2c0cf-5c75-43f0-91fb-ef3027cc33b5
date: 2026-11-07
reviewed_head: 3945e1f5c72e38acdefc6854158585569e40b928
verdict: recommended
---

# L-R11 两读面 publication gate 统一：scope review（r1）

> 只读 scope review。未参与本项任何实现、返修、契约起草或前置 review；未修改生产代码/测试/契约/卡；未 `git add/commit/push`。本报告是本次唯一写入仓库的文件；临时复现脚本与日志在仓外 `G:\CODEX\New Manga.workspace\L-R11\scope-review\`。

## 0. 结论先行

1. **L-R11 事实成立，且已用真实 production migrations 库 + 真实 assembly 复现**：当前 binding 健康、无 publication 行、其 `previous_binding_id` 指向一个有 publication 行的 binding 时，`core_assembly.read_gate` 返回 **open**，而 `core_service._assert_source_sync_gate` 抛 **`SOURCE_ACCESS_DENIED`**。在该形态下 Run 目标可进入、provider 可读出真实 rendition、commit guard 可打开、`AuthorizeSourceReadForRun` 可建立授权；写面与章级面也放行；只有 resolve/reader 拒绝——**不是对称的“两读面分歧”**。
2. **比 L-R11 记录更进一步的两个事实**（本报告新核实）：
   - resolve 面的“previous 链检测”只查**一跳**；当损坏链为 `B3(无行)→B2(无行)→B1(有行)` 时，resolve **也放行**，与 read_gate 一起违反 C-17 §3.3 的“新 previous 链缺行 fail-closed”。因此“把 resolve 对齐 read_gate”或“只收紧 read_gate”都不完整。
   - 对 `relation='added'` 的新同步 binding（`previous_binding_id IS NULL`），缺 publication 行时**任何链检测都不可见**，只能靠 plan receipt 检测；当前无实现。这是 L-R11 修复也无法顺带关闭的残余缺口，必须登记 limitation。
3. **推荐方案 A+C（同一个 Core 内部谓词 + 全链检测；legacy 无行 open、链上可证的新同步缺行 fail-closed）**。`read_gate`、`_assert_source_sync_gate`、`AuthorizeSourceReadForRun` 的 per-page gate 都改为消费同一谓词；Run 面错误码沿用既有 family，不新增 wire/错误码。
4. **UNFREEZE 判定：推荐 1/18 pin（仅 C-16）**。C-17 §3.3（`:171-173`）已经冻结“新同步 binding 缺行 fail-closed”，不需要改；但 C-16 §2.4（`:90`）冻结了“无 publication 行按既有 open 处理”，与本修复在损坏形态下**字面冲突**；C-16 §2.4（`:93`）的“L-R11 不属本命令语义”不能消除 `:90` 的规范句。按项目字节保留规则，改这一句必须走 UNFREEZE 载体 + 独立 byte-level 复核 + 重冻 + pins 重算。若 DSH 选择“解释性裁决”（认定 `:90` 只描述 legacy 路径）则可 0 pin，但契约文本会继续自相矛盾，本报告不推荐。
5. **结论：`推荐建卡实施`**，但建议拆为 `PREREQ（C-16 §2.4 一句 UNFREEZE）` + `实现卡（Core 单谓词，0 pin）` 两步；排在 `FEA-11-RUN-GRANT-2C` closeout 之后、C-04b/UI P3 之前，可与 SCAN-RH 穿插。**不建议**仅登记不实施，也不建议把 resolve 放宽成 open（明确违反 C-17）。

## 1. 核对范围与方法

- 仓库/HEAD：`G:\CODEX\New Manga`，`main`，HEAD `3945e1f5c72e38acdefc6854158585569e40b928`；review 期间本报告作者对 tracked 文件零 diff。并发活动：另一独立上下文在同一时段创建 `doc/reviews/FEA-11-RUN-GRANT-2C-r2.md` 并对 `doc/tasks/FEA-11-RUN-GRANT-2C.md` 做 closeout 编辑（status→done 等），均非本报告作者所为（见 §11）。
- 代码事实：逐行读 `src/bootstrap/core_assembly.py`、`src/bootstrap/core_service.py`、`src/infrastructure/sqlite/source_sync.py`、`src/infrastructure/sqlite/schema.py`、`src/application/sources/service.py`、`src/application/sources/lineage.py`、`src/application/importing/referenced/resolve.py`、`src/infrastructure/sqlite/library.py`、`src/infrastructure/resource_channel/source_read_refs.py`。
- 契约事实：`doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md`（§3.3 `:171-173`、§6.2 `:298-300`、§7.2 `:329-337`）、`doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md`（§2.4 `:76-93`）、`doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md`（§4.1 `:264`、§5 `:313-315`、§6 `:326`）；`doc/plan/FEA-CONTRACT-FROZEN-C16.md` / `-C17.md` 与 `FEA-CONTRACT_FREEZE_MATRIX.md`。
- 测试：`tests/fea11/test_source_rendition_gates.py`、`test_source_rendition_source.py`、`test_source_rendition_run.py`、`test_source_run_grant.py`、`test_source_resolve.py`、`tests/core/test_page_resource_resolve.py`、`tests/fea09/test_referenced_resolve.py`、`tests/fea11/test_v8_migration.py`、`test_source_scan.py`、`test_source_sync.py`。
- 实跑：见 §4；复现脚本见 §3（仓外）。
- 未跑：全量 `pytest tests`、全量 .NET、`check.ps1`、API inventory（本报告不宣称这些门禁结果；pins 实跑为 18/18，见 §7）。

> **一处题面更正**：题目背景把“旧未参与同步且无 publication 行的 v7 binding 沿旧规则；新同步 binding 缺行属于损坏，fail-closed”标为 **C-17 §7.2（`:173`）**。逐行核对后，该句在 **C-17 §3.3**（`doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md:171-173`）；§7.2 是 resolve/issue 资源版本选择（`:329-337`，其中 `:335` 另有“门控/授权/identity 在 cache/catalog 命中前”的顺序句）。下文一律按真实章节引用。

## 2. 代码事实

### 2.1 assembly 侧 `read_gate`

`src/bootstrap/core_assembly.py:1244-1261`：

```python
def read_gate(page_id: str) -> str:
    binding = source_sync_store.current_binding_of_page(page_id)
    if binding is None or binding["status"] != "healthy":
        return "unavailable"
    gate = source_sync_store.gate_of_binding(binding["binding_id"])
    if gate is None:
        return "open"                      # ← L-R11 的分歧点：任何无行 binding 都 open
    return "open" if gate["read_gate"] == "open" else "pending"
```

- 签名：`Callable[[str], str]`，返回三值 `unavailable|pending|open`（docstring `:1245-1254`）。
- 判定顺序：`current_binding_of_page`（排除 superseded，`:667-677`）→ 要求 `status == "healthy"` → `gate_of_binding(binding_id)`（`:332-340`）→ 无行一律 `open`；有行按 `read_gate` 值。
- **没有** previous 链检测，也没有 plan receipt 检测。

所有消费点（grep 全仓）：

| # | 读面 | 位置 | 行为 |
|---|---|---|---|
| 1 | provider 图源（referenced 页） | `core_assembly.py:461-468`（`_referenced_page_image`）；注入 `:1675-1687` | `gate != "open"` → `ProviderInputError`（`INVALID_INPUT`，detail 带 gate 状态），不读 source byte |
| 2 | Run 目标目录 | `core_assembly.py:1750` `pipeline._catalog.source_gate_reader = read_gate`；`pipeline.py:1603-1604` 消费 | `gate != "open"` → `TARGET_NOT_FOUND`（文本 `page … has no readable source`，RENDITION-1 冻结口径） |
| 3 | Run commit guard | `core_assembly.py:1757-1776`（`run_source_guard`），`:1780` 注入 `source_commit_guard` | `unavailable` → `TARGET_NOT_FOUND "source binding is unavailable"`；`pending` → `TARGET_NOT_FOUND "source binding is pending acknowledgement"`；`open` 才进入 `find_bound_for_source` + `commit_guard` |
| 4 | C-16 §2.4 `AuthorizeSourceReadForRun` 的 per-page gate | `core_service.py:5029-5057`（`gate_reader = catalog.source_gate_reader`；`gate = gate_reader(page_id)`）→ `source_read_refs.py:517-536`（`gate != "open"` 即 refuse） | gate 值直接决定 Host 能否为 Run 建立 grant→binding 读授权；当前无行→open，因此损坏形态可授权 |

> 题面所列的 “issue” 面在当前代码中**没有独立 gate 调用点**；`issue_resource_url` 只出现在 `handle_resolve_page_resource` 的文档字符串（`core_service.py:4448`），wire 命令 `resolve_page_resource` 直接调用同一 handler（`:7564-7571`）。因此“resolve 面”即 `handle_resolve_page_resource` 及其 reader 组合面。

### 2.2 resolve 侧 `_assert_source_sync_gate`

`src/bootstrap/core_service.py:5303-5334`：

```python
def _assert_source_sync_gate(self, page_id: str) -> None:
    ...
    binding = store.current_binding_of_page(page_id)
    if binding is None:
        return
    gate = store.gate_of_binding(binding["binding_id"])
    if gate is None:
        previous = store.gate_of_binding(binding["previous_binding_id"]) \
            if binding.get("previous_binding_id") else None
        if previous is not None:
            raise SourceImportError("SOURCE_ACCESS_DENIED",
                                    "page binding has no read gate")
        return
    if gate["read_gate"] != "open":
        raise SourceImportError("SOURCE_ACCESS_DENIED",
                                "page binding is pending acknowledgement")
```

- 调用点：`handle_resolve_page_resource`（`:4467` 定义，`:4505` 调用）；reader 投影 `handle_get_reader_projection`（`:4766`）逐页调用 resolve（`:4785`），因此 reader 也受该 gate 约束。
- **只查一跳** `previous_binding_id`；没有全链 walk，也没有 receipt 检测。
- 另有两条“pending-only”面（不查无行/损坏）：
  - 写面 `_refuse_pending_gate_writes`（`:5340-5372`，调用 `:4188`）→ `pending_gate_pages`（`source_sync.py:342-358`，SQL 只匹配 `p.read_gate = 'pending'`）。
  - reader 章级 `_refuse_pending_gate_chapter`（`:5374-5388`，调用 `:4774`）→ 同一个 `pending_gate_pages`。
  - 这两面在 L-R11 形态下 `pending_gate_pages([])` 为空 → **放行**（见 §3 实测）。

### 2.3 数据模型与写入者：为什么该形态是“损坏”

- `page_bindings`：`schema.py:698-724`；`previous_binding_id` 在 `:708`；当前 binding 唯一索引 `:720-721`；`status ∈ healthy/needs_confirmation/missing/superseded` `:706-707`。
- `source_binding_publications`：`schema.py:810-822`；`previous_binding_id` `:813`；`relation` 五值 `:814`；`read_gate ∈ pending/open` `:815`；`(relation='added') = (previous_binding_id IS NULL)` `:818`；`previous` 索引 `:822`（C-17 `:98` 同款）。
- 写入者只有两处会创建 binding：
  - sync apply：`application/sources/service.py:588-611`（`added` 页：新 binding + publication 同一段代码）与 `:653-678`（换代：`supersede` 旧 binding、插入新 binding、插入 publication，`previous_binding_id=old`）。两者都在同一 apply 业务事务内（C-17 §6.2 `:298-300`；publication 与 binding 同事务 COMMIT）。
  - C-16 导入：`application/importing/referenced/runtime.py:876-891`，`binding_version=1`、`previous_binding_id=None`，不写 publication（符合“导入未参与同步”）。
- 没有其他 `INSERT INTO page_bindings` 生产者（grep 全仓仅 `source_sync.py:781` 与 `library.py:2448` 的同一 insert helper，被上述两处调用）。
- 删除路径（`library.py:868-889` 页级 purge；`:1959-2022` 书级 source graph）都是 **publications → lineage → bindings** 同事务删除；R-010 另有“跨书 previous 引用阻断删除”的守卫（`library.py:1330-1356`；测试 `tests/core/test_core_delete_commands.py:1278+`）。因此正常删除也不会留下“binding 在、publication 没了”的状态。
- **推论**：`current binding 有 publication 的祖先、自己却没有行` 只能由**外部损坏**（手工 SQL、磁盘损坏、未来代码缺陷）产生；正常产品流程（import / sync apply / 删除/恢复）不产生该形态。C-17 §3.3 `:173` 也正是把它定义为“损坏”。

### 2.4 现成的全链检测器

`src/infrastructure/sqlite/source_sync.py:929` 的 `SourceSyncLineageFacts` 已有：

```python
def page_is_sync_managed(self, page_id: str) -> bool:
    """True when any binding of the page's own chain has a publication."""
    binding_id = self.page_binding(page_id)
    seen: set[str] = set()
    while binding_id is not None and binding_id not in seen:
        seen.add(binding_id)
        if self._publication_of(binding_id) is not None:
            return True
        ...  # 沿 page_bindings.previous_binding_id 走
    return False
```

位置 `source_sync.py:951-967`；已被 `LineageIsolationGuard.page_verdict` 使用（`application/sources/lineage.py:223`）。它正好实现 C-17 §3.3 的“new previous 链”检测；本卡应复用它（或把等价逻辑下沉到 store 的单一谓词），不要另造第三份规则。

## 3. 分歧最小形态与实测

### 3.1 数据状态（最小）

在同一 production-migrations v8 库中：

- `pages.p`：`source_mode='referenced'`、`integrity_status='complete'`、`source_hash`/`width`/`height` 非空（C-15 §4.1 V 为真）。
- `page_bindings.B2`：`status='healthy'`、`binding_version=2`、`verified_digest = source_entries.content_digest`（V 为真）、`previous_binding_id = B1`。
- `page_bindings.B1`：`status='superseded'`、`previous_binding_id=NULL`。
- `source_binding_publications`：**B2 无行**；**B1 有一行**（`read_gate='open'` 或 `pending` 均可，关键是“存在”）。
- 无其他数据条件（不需要 pending、不需要缺 grant）。

### 3.2 实测输出

复现脚本：`G:\CODEX\New Manga.workspace\L-R11\scope-review\repro_lr11.py`（只读：临时目录建库、真实 `assemble_core_services`、真实 zip/PNG、真实 grant；不写仓库）；日志：同目录 `repro-output.log`。实跑：

```text
[p2] legacy/imported: no row, previous NULL
    read_gate = open
    resolve   = ALLOW (returns)
[p3] pending row
    read_gate = pending
    resolve   = DENY SOURCE_ACCESS_DENIED: page binding is pending acknowledgement
[p]  no row, previous NULL (legacy shape)
    read_gate = open
    resolve   = ALLOW (returns)

--- after: publication(B1)=open, B2 healthy + previous=B1, B2 has NO row ---
[p] L-R11 shape (one-hop previous has a row)
    read_gate = open
    resolve   = DENY SOURCE_ACCESS_DENIED: page binding has no read gate
write/reader face pending_gate_pages(['p']) = [] | page_is_sync_managed('p') = True
create_run(p): ['p']
provider page_frame(p): (12, 7)
commit_guard(p): OPEN
handle_resolve_page_resource(p): FAILED SourceImportError SOURCE_ACCESS_DENIED page binding has no read gate
handle_get_reader_projection(c1): FAILED SourceImportError SOURCE_ACCESS_DENIED page binding has no read gate

--- after: B3 current, B3/B2 no row, B1 has one (two-hop) ---
[p] two-hop chain: one-hop check sees B2 (no row)
    read_gate = open
    resolve   = ALLOW (returns)
chain: {'binding_id': 'pb-p', 'status': 'superseded', 'previous_binding_id': None, 'read_gate': 'open'}
chain: {'binding_id': 'pb-p-b2', 'status': 'superseded', 'previous_binding_id': 'pb-p', 'read_gate': None}
chain: {'binding_id': 'pb-p-b3', 'status': 'healthy', 'previous_binding_id': 'pb-p-b2', 'read_gate': None}
```

关键点：

- 在 L-R11 形态下，provider 读出的是当前 binding 的真实 rendition（12×7 = 测试图 B，非 managed 旧图 A），且这次读取用的是**真实 live grant**（`mint_grant` + `bind_imported_entry`）——说明 gate 放宽**没有绕过** C-15 §4.1 的 R/grant/identity 授权，只是绕过了 publication ACK 状态。
- `commit_guard(p)` 打开，意味着若该页已在 Run 中，region/revision 可继续提交；`create_run(p)` 也接受该页。
- `pending_gate_pages(['p']) = []`：写面与 reader 章级面都看不到异常；`page_is_sync_managed(p) = True`：全链检测器**已能识别**该形态（修复抓手现成）。
- 两跳链（B3/B2 无行、B1 有行）：read_gate 与 resolve **都放行**——这是 L-R11 记录之外的**第二个契约缺口**：resolve 的一跳检测漏掉了“更深的 new previous 链”。C-17 §3.3 要求的是“new previous 链检测”，不是“一跳检测”。

### 3.3 反向形态（read_gate 拒绝、resolve 放行）不存在

核查了所有分支：

- binding 缺失：read_gate `unavailable`；resolve 的 gate helper 直接 `return`，但随后 `prepare_referenced_rendition` 必抛 `SOURCE_ACCESS_DENIED "page binding is not healthy"`（`resolve.py:54-56`）——命令面仍拒绝，码相同。
- binding 非 healthy：read_gate `unavailable`；resolve helper 不查 status，但 `prepare` 同样拒绝；Run 目标经 V 拒绝。
- pending 行：两面都拒绝（实测）。
- 无行 + previous 有行：唯一“read_gate 放行 / resolve 拒绝”的形态（L-R11）。
- 无行 + 更深 previous 有行：两面都放行（共同违反 C-17）。
- 无行 + `relation='added'`（previous NULL）：两面都放行；链检测不可见（残余缺口，见 §6.3）。

## 4. 现有测试覆盖与实跑数字

### 4.1 覆盖矩阵

| 形态 | read_gate 侧覆盖 | resolve 侧覆盖 | 断言方向 |
|---|---|---|---|
| healthy binding、无 publication、previous NULL（legacy/import） | `tests/fea11/test_source_rendition_gates.py:247-264`，`:253` 断言 `gate("pr") == "open"`（注释“no publication row yet”） | **无直接覆盖**（无测试调用 `_assert_source_sync_gate`；无测试构造该形态后走 resolve） | 只锁定了“无行→open”，没有锁定 resolve 的 legacy 放行 |
| binding 缺失 | `:251-252`（`gate("pm") == "unavailable"`） | 无直接覆盖 | read_gate 三态 |
| pending 行 | `:255-256`（`gate("pr") == "pending"`）；`:267-283`（目标层 `TARGET_NOT_FOUND`）；`:286-321`（commit guard）；`:324-344`（provider 拒绝） | 间接：reader/其它 pending 用例；**无 resolve 面 pending 的直接单测**（`handle_resolve_page_resource` 的 pending 分支无用例） | 拒绝方向正确 |
| open 行 | `:258-264`（UPDATE 后 `open`） | 无直接覆盖 | 放行方向正确 |
| **无行 + previous 有行（L-R11）** | **无** | **无** | **零覆盖** |
| 无行 + 两跳 previous（本报告新发现） | **无** | **无** | **零覆盖** |
| `added` binding 缺行（残余） | **无** | **无** | **零覆盖** |

补充：

- `tests/fea11/test_source_run_grant.py:971-1005` 覆盖 `AuthorizeSourceReadForRun` 的 pending gate（通过 `catalog.source_gate_reader`），但它用的是当前 binding 的 pending 行，不是无行损坏形态。
- `tests/fea11/test_source_rendition_run.py:611` 与 `:241` 是**fake** gate/guard（`site.gate_state["value"] = "pending"`），不经过真实 `read_gate`/真实 DB 形态。
- grep 全仓：`_assert_source_sync_gate` 在 `tests/**` **零引用**；`no read gate` **零命中**；没有任何测试构造“current 无行、previous 有行”的 binding 链。`previous_binding_id` 的测试命中集中在 sync apply/relink/lineage 的写入断言（`test_source_scan.py:373`、`test_source_relink.py:229`、`test_source_lineage.py:113`、`conftest.py:422-435`），不是 gate。

### 4.2 实跑数字（本机，HEAD `3945e1f5c`）

环境：`C:\Python314\python.exe`（Python 3.14.6）、`pytest 9.1.1`、`PYTHONPATH=src`、`-p no:cacheprovider`。

| 命令 | 结果 |
|---|---|
| `pytest tests/fea11 -q` | **206 passed**（约 16.2s） |
| `pytest tests/fea11/test_source_rendition_gates.py tests/fea11/test_source_rendition_source.py tests/fea11/test_source_rendition_run.py tests/fea11/test_source_run_grant.py tests/fea11/test_source_resolve.py -q` | **72 passed**（10 + 16 + 11 + 30 + 5） |
| `pytest tests/core/test_page_resource_resolve.py tests/fea09/test_referenced_resolve.py tests/fea11/test_source_resolve.py -q` | **22 passed**（9 + 8 + 5） |
| `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PIN AUDIT: PASS (all 18)**；C16 `b8f46fb1feec…`、C17 `aefa0fa5b17e…` |

**未跑**：全量 `pytest tests`（STATUS 记录的当前基线是 3363/10，但本报告未实跑，不背书）、全量 .NET、`check.ps1`、API inventory。上述数字只说明“相关测试现状全绿”，**不说明任何实现已完成或门禁已通过**。

## 5. 实际可达性、安全与“哪边更危险”

### 5.1 可达性

- **正常产品流程不可达**：§2.3 已证明 binding 与 publication 在同事务写入；删除路径同事务清两者；导入路径不产生 previous 链。只有外部损坏/未来缺陷能产生。
- **损坏后的后果是可达的**：一旦库进入该形态，referenced Run 的目标/读图/提交、以及 live edit 写面都可用（实测），而 resolve/reader 拒绝。也就是说，“损坏库”不会让应用崩溃，但会让一部分面按旧规则工作、另一部分面 fail-closed。
- **pending 是正常可达的**（apply COMMIT 后、Host ACK 前），但 pending 形态两面一致（都拒绝），不属 L-R11。

### 5.2 是否越权/数据安全

- **不是路径/授权绕过**：read_gate 只回答 publication ACK 状态；provider/target 仍要 V + live grant + identity/budget（实测 provider 需要真实 grant 才能读），resolve 仍要 `R(p,t)`。放宽 gate 不会让无 grant 的读取成功。
- **是完整性/审计风险**：fail-open 会消费“未知 ACK 状态”的 binding，Run 提交可给该 binding 盖 native lineage；若该次 sync 实际未被 Host 确认（或 operation 损坏），后续难以从回执判断。收紧只会拒绝访问损坏数据，不写坏数据。
- **因此收紧（fail-closed）比放宽更安全**；B 方案（把 resolve 放宽成 open）会把仅剩的 fail-closed 面也去掉，**明确违反 C-17 §3.3 “不能当作 legacy 放行”**，不可取。
- 写面/章级面在损坏形态下仍放行（§2.2），这是修复后仍存在的**非读面**不一致；若 DSH 要求“全系统一致”，需把 `pending_gate_pages` 扩展为“pending 或链损坏”，但那会扩大本卡范围（见 §8 Out/limitation）。

## 6. 候选方案对比与推荐

### 6.1 候选

| 方案 | 内容 | 正确性 | 契约一致性 | 影响面 | 测试 | pins |
|---|---|---|---|---|---|---|
| **A. 收紧 read_gate（链检测）** | `read_gate` 对“新同步链（previous 链可证）缺行”返回拒绝；legacy（链上无 publication）保持 open。resolve 若不同步改，则两跳形态仍分歧 | 中：修好 L-R11 一跳形态，但不修 resolve 的一跳盲区 | 对齐 C-17 §3.3；与 C-16 §2.4 `:90` 冲突 | Run 目标/provider/commit guard/AuthorizeSourceReadForRun 在损坏形态下收紧；正常库零变化 | 需要真实损坏形态测试；现有 206 例预计不受影响 | **1 pin（C-16）** |
| **B. 放宽 resolve** | `_assert_source_sync_gate` 改为“缺行 open”，与 read_gate 一致 | 低：让两面在损坏形态都放行 | **直接违反 C-17 §3.3**（“不能当作 legacy 放行”）；只对齐 C-16 `:90` | 两面都 fail-open；损坏 binding 全面可用 | 测试容易，但锁死错误语义 | 0 pin（但不可接受） |
| **C. 抽单一共享谓词（推荐，A+C）** | 在 Core 内部（`SourceSyncStore` / `SourceSyncLineageFacts`）实现唯一谓词：healthy + 行状态 + 全链检测 + legacy open / 新同步缺行 fail-closed；`core_assembly.read_gate` 与 `core_service._assert_source_sync_gate` 都委托它（必要时组装层做三态适配） | 高：L-R11 一跳 + 两跳 + 未来新读面都走同一判定 | 对齐 C-17 §3.3；同样需要 C-16 `:90` 一句 UNFREEZE | 同上；另消除两处重复实现（RENDITION-1 scope review 的“后续小改”承诺） | 可用真实库造 5 种形态 + 静态断言“只有一处判定” | **1 pin（C-16）** |
| **C′. 只抽单谓词、保留“缺行 open”** | 纯重构，语义不变 | 只消除重复，不修分歧 | 维持 C-16，违反 C-17 | 零行为变化 | 无判别性 | 0 pin（但无意义） |
| **D. 仅登记/文档/测试卡，不改代码** | 保留现状 + 把损坏形态写成 limitation/诊断测试 | 不修 | 违反 C-17 §3.3（未实现） | 零 | 只能记录现状 | 0 pin |
| **E. 只把 resolve 扩成全链、read_gate 不动** | resolve 更严 | 低：扩大分歧（两面都拒绝的页更多，但 read_gate 仍放行） | 部分对齐 C-17 §3.3，但“两面不一致”更严重 | 读者/Resolve 更易拒绝损坏页；Run 仍放行 | 可测 | 0 pin（不推荐） |

### 6.2 推荐

**推荐 C（= A 的完整形态）**：单一 Core 谓词 + 全链检测 + legacy open + 新同步链缺行 fail-closed；`read_gate`、`_assert_source_sync_gate`、`AuthorizeSourceReadForRun` 的 per-page gate 共用。实现要点（供卡面冻结，不代替实现设计）：

- 谓词返回至少区分 `open` / `pending` / `unavailable` / `corrupt_chain`（或内部 reason），组装层把 `corrupt_chain` 映射为既有的 `unavailable`（保持下游三态消费和错误码 family 不变），另提供只读 reason 供日志/测试。
- 检测用 `page_is_sync_managed` 同款**全链** walk（沿 `page_bindings.previous_binding_id`，任一 binding 有 publication 即视为“参与过同步”）；不要只查一跳。
- legacy 判定：链上**没有任何** publication → open（v7 未同步/导入页）。这不会误伤“有 previous 链接但从未同步”的旧数据，因为检测条件要求至少一行 publication。
- 不新增错误码/wire/schema/命令；Run 面保持 `TARGET_NOT_FOUND`，provider 保持 `ProviderInputError`/`INVALID_INPUT`，resolve 保持 `SOURCE_ACCESS_DENIED`。
- `AuthorizeSourceReadForRun` 的行为变化（损坏形态由“可授权”变“拒绝”）是 C-16 `:90` 需要同步澄清的直接原因。

**备选**：若 DSH 不愿为一句澄清走 UNFREEZE，可先做 **C′ + 文档/诊断**（仅抽谓词、不改语义），把 L-R11 作为已登记 contract debt；但这不解决 C-17 §3.3，且未来每次加读面都要提醒“别走这个洞”。**不推荐**。

**“不做”的理由是否成立**：部分成立（正常用户不可达、值不高），但不足以支撑“仅文档”：
- 项目已经把 L-R11 登记为待统一项，且 C-17 §3.3 是冻结语义；继续不实现就是明确的契约债务。
- 修复代码面很小（一个谓词 + 两个调用点 + 测试），且能顺手消除重复谓词（未来读面的风险源）。
- 唯一让“不做”变得合理的是 UNFREEZE 流程成本；若 DSH 判断流程成本高于收益，可以“仅登记 + 在 RENDITION-1/L-R11 limitation 里写清未实现”，但必须明确这不是“C-17 §3.3 已满足”。

## 7. UNFREEZE 判定（关键）

### 7.1 需要改哪一条

**C-16 §2.4（`doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md:90`）**：

> “binding 非 healthy 或 publication gate 非 open（沿用 Run 目标/commit guard 的**同一** gate 谓词，C-17 §3.3；**无 publication 行按既有 open 处理**）→ 不可授权”

这句是 `per-page 授权匹配（冻结）` 段落里的规范句。若把共享谓词收紧为“新同步链缺行 fail-closed”：
- `AuthorizeSourceReadForRun` 的实现经 `catalog.source_gate_reader` 消费同一谓词（`core_service.py:5030,5057`），因此该命令在损坏形态下会从“可授权”变为“拒绝”；
- `:90` 的“无 publication 行按既有 open 处理”在该子形态下变为**字面不成立**；
- `:93` 的“publication gate 两读面既有差异（L-R11）不属于本命令语义、本命令不引入第三套 gate 判定”只能说明“本命令不裁决 L-R11”，不能豁免 `:90` 已经写下的规范句。

**C-17 §3.3（`:171-173`）不需要改**：它已经逐字要求“新同步 binding 缺 publication 行属于损坏，fail-closed（由 plan receipt/new previous 链检测），不能当作 legacy 放行”。本卡的实现是让代码开始满足它，不是改它。

### 7.2 建议的 UNFREEZE 形态

- 1/18 pin：仅 C-16 变更；C-17 `aefa0fa5…`、C-06/C-15/C-07/M2-C1 及其余 16 个 pin 保持。
- 版本：C-16 v1.6 → **v1.7**；只改 `:90` 一个括注分句（建议措辞）：
  > “沿用 Run 目标/commit guard 的**同一** gate 谓词，C-17 §3.3；**旧未参与同步且无 publication 行的 v7 binding 按既有 open 处理；新同步 binding 缺 publication 行属于损坏，fail-closed（C-17 §3.3），不得当作 legacy 放行**”
- 同步更新：`doc/plan/FEA-CONTRACT-FROZEN-C16.md`（pin/版本/§1B/§9 记录）、`doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md` 第 16 行；新增载体 `doc/reviews/CONTRACT-UNFREEZE-2026-11-XX-C16-L-R11.md`；独立上下文 fresh subagent 做 **byte-level 复核**；重冻后 `verify_pins.ps1` 18/18（C16 新值、其余 17 不变）。
- 建议同一 pin 内顺带处理 `:93` 的过期陈述：把“publication gate 的两读面既有差异（L-R11）不属于本命令语义”改为“该差异由 L-R11 统一；本命令仍不引入第三套 gate 判定”。否则实现后该句仍说“存在差异”，与新代码不符（仍属同一处 §2.4、同一个 C-16 pin，不增加 pin 数）。
- 不做：C-16 的 wire 字段/命令集/能力/错误闭集/TTL/撤销/`PROTOCOL_MINOR=3` 零改动；C-17/C-06/C-15/C-07/M2-C1 零字节；schema/迁移/依赖零改动。

### 7.3 替代路径（不推荐，但可裁决）

若 DSH 认定 `:90` 的“无 publication 行”只描述“旧 v7 binding 沿旧规则”的场景，并正式记录该解释，则实现可 0 pin 单卡推进；但：
- 契约文本仍会让下一个读者把 `:90` 与 C-17 §3.3 读成矛盾；
- 2026-11-06 的 C-06/C-16 PREREQ review 已经用 `:90` 作为“无行 open”的依据（`doc/reviews/FEA-11-RUN-GRANT-1-PREREQ-1-r2.md:82`、`doc/reviews/FEA-11-RUN-GRANT-1-PREREQ-1-r3.md:86`），说明这不是无人使用的边角句；
- 因此本报告推荐走 UNFREEZE，而不是解释性 0 pin。

### 7.4 0 pin 的成立条件

只有当实现**完全不改变** `AuthorizeSourceReadForRun` 的 per-page 判定、也不改变任何已冻结的 gate 语义时，才能 0 pin。L-R11 的修复必然改变 `read_gate`（Run 目标/commit guard/provider）与 resolve 的判定，并经由 `source_gate_reader` 影响该命令；所以“0 pin”不能仅凭“C-17 已写明 fail-closed”推出，必须叠加 C-16 的解释或 UNFREEZE。

> **与历史判断的差异**：2026-11-07 前后的多份 scope review 把 L-R11 判为“0 pin、可穿插”（例如 `doc/reviews/FEA-11-RUN-GRANT-2-scope-r1.md:450`、`FEA-11-L-S1-REGISTRY-RESILIENCE-1-scope-r1.md:223`、`FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1-scope-r1.md:534`）。那些判断基于“只改 Core 代码、C-17 §3.3 已冻结、C-16 `:90` 只是描述”的假设；本 review 核实 `:90` 是 `per-page 授权匹配（冻结）` 段落里的规范句，且 `AuthorizeSourceReadForRun` 确实消费同一 `read_gate`，故把它修正为 **1 pin（或解释性 0 pin）**。这不改变“价值低-中、成本小-中、可穿插”的优先级结论。

## 8. 影响面、风险与测试策略

### 8.1 按库形态

| 库形态 | 修复后行为 | 是否受益/误伤 |
|---|---|---|
| 纯 legacy v7 升级库（所有 binding 无 publication、previous NULL） | 全链无 publication → open；provider/target/resolve 与现状一致 | 不受影响 |
| 正常升级 + C-16 导入的 referenced 页（无 publication、previous NULL） | 同上 open | 不受影响 |
| 正常 sync 过的页（current binding 有 publication 行） | 走行分支：open/pending 不变 | 不受影响 |
| 损坏链（current 无行、链上有行；一跳或两跳） | read_gate 拒绝（映射 `unavailable`）；resolve 拒绝；provider/target/commit/Authorize 均拒绝；写面/章级面仍按 pending-only 放行（limitation） | 受益：不再消费未确认/损坏 binding；可能“误伤”的是本来就读不了/不该读的损坏页 |
| 混合页（referenced + managed_original_ref 非空） | gate 判定只看 binding，不受 `managed_original_ref` 影响；与 RENDITION-1 L-R5 的既有取舍一致 | 不受本卡影响 |
| `added` binding 缺行（previous NULL） | 链检测不可见 → 两面仍 open | **未修复**（limitation） |

### 8.2 各读面

- **Run 目标层**：损坏页从“可进入”变 `TARGET_NOT_FOUND`（既有 family；目标层文本 `page … has no readable source`，`pipeline.py:1603-1604`；commit guard 文本 `source binding is unavailable`，`core_assembly.py:1767-1768`）。正常页零变化。
- **commit guard**：损坏页在进入 `find_bound_for_source` 前即拒绝；不会给损坏 binding 盖 native lineage。commit 期错误的最终投影仍可能是 `DB_FAILED`（L-R8 既有），卡面不得宣称新增码。
- **provider**：损坏页在 `_referenced_page_image` 的 gate 检查处拒绝，零 source byte 读；detail 只带固定状态，不带路径/locator。
- **resolve/reader**：行为与今天一致（拒绝），但原因从“一跳 heuristic”变为“同一谓词”；错误文本仍是既有 `SOURCE_ACCESS_DENIED`（非新增）。reader 章节因逐页 resolve 而整体 typed 拒绝。
- **写面/章级面**：本卡建议**不改**（它们只关心 pending）；损坏形态下仍允许写/章级投影进入，直到逐页 resolve 拒绝。若 DSH 要求“全系统一致”，需要另加 `pending_gate_pages` 的“链损坏”扩展，成本/风险另算。
- **AuthorizeSourceReadForRun**：损坏页由“可授权”变“整请求 `SOURCE_ACCESS_DENIED`、零映射写入”（C-16 §2.4 既有整体语义）；这正是 C-16 `:90` 需要澄清的行为变化。

### 8.3 判别性测试建议（不靠 stub）

用真实 production migrations 库 + 真实 zip/PNG + 真实 grant + 真实 `assemble_core_services`（RENDITION-1 的 test 模板可复用）：

1. **legacy v7→v8**：先迁到 v7，插 book/chapter/page/binding（无 publication、previous NULL），再迁到 v8 并 assemble → `read_gate` open；resolve 返回；provider/target/commit 正常（可用真实 grant 读图）。判别性：把“链上有 publication 才算 corrupt”改成“无行即 corrupt” → 该用例红。
2. **L-R11 一跳**：v8 库造 B1（有 publication）+ B2（无行、previous=B1）→ read_gate 拒绝；resolve `SOURCE_ACCESS_DENIED`；provider 在 read byte 前拒绝（spy `prepare_referenced_rendition`/`read_entry_bytes` 0 次）；`create_run` `TARGET_NOT_FOUND`；commit guard 拒绝；`AuthorizeSourceReadForRun` typed 拒绝且零映射。判别性：删掉全链检测/把分支改回 open → 红。
3. **两跳**：B3/B2 无行、B1 有行 → 同样拒绝。判别性：把实现改成只查一跳 → 红（这是本报告新增的判别点）。
4. **pending/open/legacy 回归**：现有 206 例全绿；特别是 `test_gate_predicate_reports_the_three_frozen_states`、pending target/commit/provider、Authorize pending 用例不改断言方向。
5. **静态唯一性**：Core 内只有一处 gate 判定（如 `source.count("def read_gate(") == 1` 的升级版）；`core_service` 不再有独立的一跳 previous 判定；`AuthorizeSourceReadForRun` 仍通过 `catalog.source_gate_reader` 消费同一谓词。
6. **不靠 stub**：像素/真实文件用 `tmp_path`；gate 形态用真实 SQL 行；grant 用 `tests/fea11/conftest.py` 的 `mint_grant`；不要用 `_StubImages`/fake gate 状态来证明本卡。

### 8.4 回滚/失败语义

- 误判风险：若全链检测写错（例如把“任何 previous 链接”当作“参与过同步”），会误伤**从未同步但有 previous 链接**的旧数据。缓解：判定条件必须是“链上至少一行 publication”，不是“previous 非空”；legacy 测试必须覆盖“previous 非空但链上无 publication”的形态（如果这种数据可能存在，见 §2.3 的写入者分析——当前正常流程不会产生，但测试可造）。
- 用户可见码：Run `TARGET_NOT_FOUND`；provider `INVALID_INPUT`（detail 带 gate 状态）；resolve/reader `SOURCE_ACCESS_DENIED`；commit 可能 `TARGET_NOT_FOUND` 或 `DB_FAILED`（既有 L-R8）。全部是既有 family，无新增码。
- 可诊断性：固定文本 + 可选 stderr 日志（page_id + reason，不含路径/locator/secret）。若不加日志，用户只能看到“不可用/无 gate”，难以区分“损坏”与“缺源”；建议卡面要求一条固定、无敏感信息的诊断行，或登记 limitation。
- 无数据修复路径：本卡不做“重建 publication 行/修复损坏库”；用户需要外部恢复。登记 limitation。

## 9. 卡面建议（供 DSH 冻结）

### 9.1 建议拆卡

| 项 | 建议 |
|---|---|
| **PREREQ 卡** | `id: FEA-11-L-R11-GATE-UNIFY-PREREQ-1`；kind: contract；title: “C-16 v1.7：§2.4 无 publication 行口径澄清（legacy open / 新同步链缺行 fail-closed）”；depends_on: `FEA-11-RENDITION-1`；suggested_owner: codex（DSH 可改 ZCode）；base_commit: `3945e1f5c`（冻结时以当时 HEAD 为准）；allowed_paths: `doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md`、`doc/plan/FEA-CONTRACT-FROZEN-C16.md`、`doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md`、`doc/reviews/CONTRACT-UNFREEZE-2026-11-*-C16-L-R11.md`、`doc/tasks/FEA-11-L-R11-GATE-UNIFY-PREREQ-1.md`、`doc/reviews/FEA-11-L-R11-GATE-UNIFY-PREREQ-1-*.md`、`verification/FEA-11-L-R11-GATE-UNIFY-PREREQ-1/**`；Out: 其它 17 pins、wire/命令/能力/错误码/schema/依赖/src/apps；AC: ①载体逐项落地 ②仅 C-16/FROZEN/矩阵/载体/卡变化 ③C-17/C-06/C-15/C-07/M2-C1 及 src/apps/tests 零 diff ④无新 wire/码/schema ⑤独立 byte-level 复核 approved ⑥pins 18/18（C16 新值、其余 17 不变） |
| **实现卡** | `id: FEA-11-L-R11-GATE-UNIFY-1`；kind: implementation；title: “L-R11 两读面 publication gate 统一：Core 单谓词（legacy open / 新同步链缺行 fail-closed）”；depends_on: `FEA-11-RENDITION-1`、`FEA-11-RUN-GRANT-2C`（closeout；共享 `tests/fea11/test_source_run_grant.py`）、`FEA-11-L-R11-GATE-UNIFY-PREREQ-1`（若走 UNFREEZE）；suggested_owner: codex（DSH 可改 ZCode）；base_commit: 冻结时 HEAD；branch/worktree: null；allowed_paths: `src/infrastructure/sqlite/source_sync.py`、`src/bootstrap/core_assembly.py`、`src/bootstrap/core_service.py`、`tests/fea11/test_source_gate_unify.py`（新；或经 DSH 同意扩 `tests/fea11/test_source_rendition_gates.py`/`test_source_resolve.py`/`test_source_run_grant.py`）、`doc/tasks/FEA-11-L-R11-GATE-UNIFY-1.md`、`doc/reviews/FEA-11-L-R11-GATE-UNIFY-1-*.md`、`doc/handoffs/FEA-11-L-R11-GATE-UNIFY-1-*.md`、`verification/FEA-11-L-R11-GATE-UNIFY-1/**`；Out: 契约字节（PREREQ 负责）、schema/迁移、wire/错误码/命令/能力、`apps/**`、依赖、RENDITION-1 的 provider/选择语义、写面/章级面的 pending-only 语义、C-04b/SCAN-RH/UI、STATUS/PLAN/LEDGER、push |

### 9.2 实现卡 AC（3–6 条，可验证）

- **AC-1 单谓词唯一**：Core 内只存在一处 publication-gate 判定（建议放在 `SourceSyncStore` 或 `SourceSyncLineageFacts`）；`core_assembly.read_gate`、`core_service._assert_source_sync_gate` 与 `AuthorizeSourceReadForRun` 的 per-page 路径都消费它；静态断言无第二份“一跳 previous”判定；同步更新 `read_gate` docstring 中“无行即 open”的过期表述。判别性：复制判定或删委托 → 新用例红。
- **AC-2 legacy 零回归**：真实 v7→v8 迁移库（或等价 legacy 形态）中，无 publication、previous NULL 的 healthy binding → `read_gate("p") == "open"`；resolve 返回；provider/target/commit/Authorize 行为与修复前一致（真实 grant 可读图）。判别性：把“无行即 corrupt” → 红。
- **AC-3 L-R11 一跳 fail-closed**：真实 v8 库造 B1（publication open）+ B2（healthy、无行、previous=B1）→ read_gate 拒绝；resolve `SOURCE_ACCESS_DENIED`；provider 在 read byte 前拒绝（0 次解码/0 次 read）；`create_run` `TARGET_NOT_FOUND`；commit guard 拒绝；`AuthorizeSourceReadForRun` 整请求 typed 拒绝且零映射。判别性：分支改回 open → 红。
- **AC-4 全链检测**：两跳（B3/B2 无行、B1 有行）同样 fail-closed；判别性：改回一跳 → 红。
- **AC-5 零契约/schema/wire/依赖漂移**（若 PREREQ 已合入）：C-16 v1.7 与实现一致；C-17/C-06/C-15/C-07/M2-C1 及其余 16 pins 零 diff；`schema.py`/`apps/**`/依赖零 diff；无新错误码/命令/能力/`PROTOCOL_MINOR`；`src/**` diff ⊆ allowed_paths。若 DSH 走解释性 0 pin，则本 AC 改为“C-16 字节零 diff + 裁决记录入卡”，其余不变。
- **AC-6 门禁、证据与不夸大**：定向 pytest（新用例 + `tests/fea11` 全量 206 基线 + `tests/fea11/test_source_run_grant.py`/`test_source_resolve.py`）；全量 `pytest tests` 不降（起点在卡面重测）；`check.ps1` PASS；`verify_pins.ps1` 18/18（若 PREREQ 后 C16 新值）；API inventory PASS；scope diff；EV/Handoff 完整；卡面明确登记 §9.3 的 limitations，且**不得**写“C-17 §3.3 已完全实现”“L-R11 全部关闭”。

### 9.3 预登记 limitation（若实现）

- **L-R11-a（残余，必须写）**：`relation='added'` 的新同步 binding 缺 publication 行时，previous 链无行可查，**无法与 v7 legacy 导入页区分**；C-17 §3.3 的“plan receipt”检测未实现（需扫描 `source_operations.commit_receipt_json` 或新持久标记；后者会碰冻结 schema）。本卡只覆盖 previous 链可检测的损坏子集。
- **L-R11-b**：写面 `_refuse_pending_gate_writes` 与章级 `_refuse_pending_gate_chapter` 仍为 pending-only；损坏链形态下编辑/章级预检仍放行，直到逐页 resolve 拒绝。本卡不改（避免把 managed 页/无 binding 页误伤）。
- **L-R11-c**：损坏状态映射到既有 `unavailable`/`TARGET_NOT_FOUND`/`INVALID_INPUT`/`SOURCE_ACCESS_DENIED`，无专用诊断码（C-17 §8 禁止新增码）；仅固定文本/可选日志可诊断。
- **L-R11-d**：不提供损坏 publication 行的自动修复/重建；损坏库需外部恢复。
- **L-R11-e**：若测试不使用真实 v7→v8 fixture，只以 v8 库中的 legacy 形态代替，需在卡面写明；优先用 `MigrationRunner(..., MIGRATIONS[:7])` 造 v7 再升级（`tests/fea11/test_v8_migration.py:59-80` 已有模式），成本很小。

### 9.4 门禁清单

- 定向：`python -m pytest tests/fea11/test_source_gate_unify.py tests/fea11/test_source_rendition_gates.py tests/fea11/test_source_rendition_source.py tests/fea11/test_source_rendition_run.py tests/fea11/test_source_run_grant.py tests/fea11/test_source_resolve.py -q`；再跑 `tests/fea11` 全量（本报告基线 206 passed）。
- 全量：`python -m pytest tests -q`（卡面重测起点；本报告未跑，不背书 3363/10）。
- `pwsh -NoProfile -File tools/governance/check.ps1`（默认 + `-TaskPath`；若卡面流程要求）。
- `pwsh -NoProfile -File tools/governance/verify_pins.ps1` → 18/18（PREREQ 后 C16 新值）。
- `python tools/.../generate_api_inventory.py --check`（以仓库实际脚本路径为准）。
- scope diff ⊆ allowed_paths；`doc/plan`/`doc/contracts`/`schema.py`/`apps/**`/依赖文件零 diff（PREREQ 卡除外）。
- **无 .NET 影响**：本卡仅 Python Core + tests；不要求 `dotnet test`（若卡面流程固定要求，跑回归但不作为本卡证据）。
- 跑后恢复 `verification/FEA-09` 若被全量 pytest 触碰（沿既有惯例）。

## 10. 优先级与最终结论

### 10.1 评级

| 维度 | 评级 | 说明 |
|---|---|---|
| 价值 | **低-中** | 只在损坏库显形；但属 C-17 §3.3 冻结语义与两读面一致性，且能消除重复谓词（未来读面风险） |
| 成本 | **小（代码）+ 中（1 pin UNFREEZE）** | 预计 3 个生产文件（`source_sync.py` + `core_assembly.py` + `core_service.py`）+ 1–2 个测试文件；若走 UNFREEZE，另加载体/独立复核/重冻/pins |
| 风险 | **低** | 正常 legacy/import/sync 库行为不变；只收紧损坏形态；无 schema/wire/依赖；误伤风险可由“链上至少一行 publication”条件消除 |
| 优先级 | **2C closeout 之后、C-04b/UI P3 之前；可与 SCAN-RH 穿插** | 不抢占任何用户可见阻断项；2C 共享测试文件，先等其 closeout 避免冲突 |

一句话：**在 2C 收尾后安排一张很小的 Core 卡，可与 SCAN-RH 穿插；C-04b/UI P3 之后放它即可，但不建议无限期挂账。**

### 10.2 结论

**`推荐建卡实施`**（含 `PREREQ` 的 C-16 一句 UNFREEZE），最短可行路径：

1. 释放 `FEA-11-L-R11-GATE-UNIFY-PREREQ-1`：C-16 v1.7 一句澄清 → 独立 byte-level 复核 → 重冻 → pins 18/18（1/18 变）。
2. 释放 `FEA-11-L-R11-GATE-UNIFY-1`：Core 单谓词（全链 + legacy open + 新同步链缺行 fail-closed）+ 真实库判别测试 + limitations。
3. 若 DSH 裁决“解释性 0 pin”，可合并为一张实现卡，但必须在卡面/评审记录该裁决，并保留 L-R11-a（`added`）等限制；本报告不推荐这条路径。

**不推荐**：B（放宽 resolve，违反 C-17）；E（只收紧 resolve，扩大分歧）；D（仅登记）在没有明确“接受 C-17 §3.3 未实现”的裁决时也不推荐。

## 11. 真实性声明

- **写入范围**：本报告 `doc/reviews/L-R11-GATE-UNIFY-scope-r1.md` 是唯一写入仓库的文件；未修改任何生产代码、测试、契约、schema、卡、STATUS/PLAN/LEDGER；未 `git add/commit/push`。临时复现脚本与日志写在仓外 `G:\CODEX\New Manga.workspace\L-R11\scope-review\`（`repro_lr11.py`、`repro-output.log`）。
- **独立性**：fresh subagent（session `5aa2c0cf-5c75-43f0-91fb-ef3027cc33b5`），未参与 L-R11 / RENDITION-1 / RUN-GRANT / 2C 的任何实现、返修、契约起草或前置 scope/review；只读 HEAD `3945e1f5c` 与冻结契约。
- **实跑与未跑**：实跑 `tests/fea11`（206 passed）、五个相关文件（72 passed）、三个 resolve/reader 文件（22 passed）、`verify_pins.ps1`（18/18）、以及 §3 的真实 assembly 复现。**未跑**全量 pytest、全量 .NET、`check.ps1`、API inventory；未对任何未跑项背书。
- **工作树**：开始时 `git status` 曾因行尾/stat 缓存瞬时显示 `apps/.../HostRuntime.cs`，刷新后为 clean、无内容 diff；review 期间另一独立上下文 session `a4410d0a-cb74-43d2-8379-7c5a9d8a88d6` 在 2026-11-07 21:36:43 创建了未跟踪文件 `doc/reviews/FEA-11-RUN-GRANT-2C-r2.md`（21:41 前后该上下文/Lead 又对 `doc/tasks/FEA-11-RUN-GRANT-2C.md` 做了 4+/4− 的 closeout 编辑：`status: done`、`integration_commit: 7c95bb3c4`、证据状态 complete）。二者均非本报告作者，未触碰；本报告自身也是未跟踪文件。本报告作者对 tracked 文件零 diff、未 staged。
- **不夸大**：本报告**不**声称任何实现已完成、**不**声称任何门禁（除 pins 外）已通过、**不**声称 C-17 §3.3 已满足或 L-R11 已关闭；所有结论均为 scope review 建议，供 DSH 裁决。
