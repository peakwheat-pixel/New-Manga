---
task: FEA-11-L-R11-GATE-UNIFY-1
reviewer: fresh subagent
session: session-3ac1953a-094e-4339-889a-284df2b7b34d
reviewed_head: 86cd1d124
verdict: approved
p0: 0
p1: 0
p2: 0
p3: 5
date: 2026-11-08
---

# FEA-11-L-R11-GATE-UNIFY-1 实现 Review（r1）

> 只读审查。被审对象为 `delivery_head=86cd1d124` 的 Core 单谓词实现、测试与证据；作者未参与该卡任何实现、返修、scope review 或契约 UNFREEZE。仓内唯一写入为本报告；临时脚本、备份与复跑日志写在仓外 `G:\CODEX\New Manga.workspace\L-R11\review\`。未 `git add/commit/push`。

## 0. 结论先行

1. **`approved`**：P0=0、P1=0、P2=0；5 条非阻断 P3（证据 EOL 可移植性、全链 walk 的查询放大、多语句读取窗口、resolve 面非 healthy+pending 的文本漂移、单谓词 docstring/静态断言的措辞精度）。
2. **AC-1…AC-6 全部成立**。单一 publication-gate 判定确为 `source_sync._publication_gate_verdict`，四个读面（`core_assembly.read_gate`、`core_service._assert_source_sync_gate`、`_assert_source_sync_gates`、`AuthorizeSourceReadForRun` 经 `catalog.source_gate_reader`）都消费同一谓词；旧一跳 `previous_binding_id` 启发式已从代码删除，`read_gate` 过期 docstring 已修正。
3. **独立实跑数字与交付声明一致**：新用例 **6 passed**；五个相关文件 **72 passed**；`tests/fea11` **212 passed**；`verify_pins.ps1` **PASS (all 18)**；`check.ps1` 默认与 `-TaskPath` 均 **PASS (3 warnings)**；API inventory **EXIT 0**。全量 `pytest tests` 本报告未重跑，仅核对证据日志中的 `3369 passed, 10 skipped`。
4. **独立破坏性复跑 3/3 RED_AS_EXPECTED**：R1「无行即 corrupt」只使 legacy 用例红、一跳/两跳仍绿；R2「全链改回一跳」只使两跳红、legacy 与一跳绿；R3「resolve 面恢复旧一跳启发式」使静态唯一性 + 两跳红。三次均从备份逐字节复原并核对 SHA-256（`f0a014…`、`b4176d…`），最终复绿 6 passed，工作树回到 `1e339f30a` 的 clean 状态。
5. **口径未夸大**：卡面/EV/Handoff 均未写「C-17 §3.3 完全实现」或「L-R11 全部关闭」；`L-R11-a…e` 逐项保留，尤其 a（`relation='added'` 缺行不可检测）与 b（写面/章级面仍 pending-only）。
6. **非阻断建议**：closeout 时记录/固定三个修改文件的 sha256 是「工作树 CRLF 字节」而非 commit blob 字节这一 EOL 事实；其余 P3 只作为后续观察项，不要求本卡返修。

## 1. 基线事实

- 仓库：`G:\CODEX\New Manga`；分支 `main`；审查开始时 HEAD `1e339f30a`，工作树 clean；审查结束时仍 clean（仅本报告为 untracked）。
- 交付链：`1c1c9ca2f`（feat：3 个 `src/**` 文件）→ `86cd1d124`（test：新增 `tests/fea11/test_source_gate_unify.py`）→ `1e339f30a`（docs/evidence）。父链实测为 `2e4d6128e` → `1c1c9ca2f` → `86cd1d124` → `1e339f30a`。
- `git diff 2e4d6128e 86cd1d124 --stat`：**4 files changed, 817 insertions(+), 63 deletions(-)**，恰为 `src/infrastructure/sqlite/source_sync.py`（+127/−25）、`src/bootstrap/core_assembly.py`（+19/−14）、`src/bootstrap/core_service.py`（+26/−24）与新测试文件（+645）。
- `git diff 86cd1d124 1e339f30a -- src tests` 为 0；`1e339f30a` 只含卡面、Handoff、`verification/FEA-11-L-R11-GATE-UNIFY-1/**`。
- 任务卡：`status: ready`；Owner `l-r11-impl`；`delivery_head: 86cd1d124`；AC-1…AC-6 均 `<<MET>>`；`canonical_evidence_status` / `resource_closeout_status` 仍为 `pending`（符合「实现 ≠ 集成」）。
- 依据：`doc/reviews/L-R11-GATE-UNIFY-scope-r1.md`（方案 C：单谓词 + 全链）；C-17 §3.3 `doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md:171-173`；C-16 v1.7 §2.4 `doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md:90/93`；`doc/tasks/FEA-11-RENDITION-1.md:159` 的 L-R11 登记。
- 审查者独立性：fresh subagent，未参与 L-R11 / RENDITION-1 / RUN-GRANT / C-16 v1.7 的任何实现、返修、scope review 或冻结；只读 `86cd1d124` 与 HEAD `1e339f30a`（二者 `src/**`、`tests/**` 无代码差异，文本等价；line-ending 差异见 P3-1）。

## 2. 逐 AC 核对

### AC-1 单谓词唯一 — **MET**

- `src/infrastructure/sqlite/source_sync.py:116-147` 的 `_publication_gate_verdict(conn, page_id)` 是 Core 内唯一的 publication-gate 判定；四态 `open/pending/unavailable/corrupt_chain`，health + 当前 binding 的 publication 行 + **全链** walk。
- 唯一公开入口：`SourceSyncStore.publication_gate_of_page`（`:450-461`）。
- 消费方实查：
  - `core_assembly.read_gate`（`core_assembly.py:1246-1266`）只委托该谓词，并把 `corrupt_chain` 映射为冻结三态的 `unavailable`；不再本地读 `gate_of_binding`，不再读 `previous_binding_id`。
  - `core_service._assert_source_sync_gate`（`core_service.py:5303-5336`）委托同一谓词；`pending` → 既有 `SOURCE_ACCESS_DENIED "page binding is pending acknowledgement"`；`corrupt_chain` → 既有 `SOURCE_ACCESS_DENIED "page binding has no read gate"`；`unavailable` 交由 resolve 自身的 binding-readiness 检查。`_assert_source_sync_gates`（`:5338-5340`）只循环委托。
  - `AuthorizeSourceReadForRun` 未改代码，仍经 `catalog.source_gate_reader`（`core_service.py:5030/5057`）消费同一 `read_gate`；`source_read_refs.authorize_run_bindings`（`source_read_refs.py:521-526`）按 `gate != "open"` 拒绝。
- 旧「一跳 `previous_binding_id`」启发式已从实现删除；grep/AST 独立抽样确认 `core_service` 中该名称只出现在 docstring（说明已删除），实现无 `gate_of_binding` / `binding["previous_binding_id"]` 读取。
- `read_gate` docstring 的过期「无 publication 行即 open」已改为「全链从未发布 → legacy open；`corrupt_chain` → 映射 `unavailable`」。
- 静态判别：`tests/fea11/test_source_gate_unify.py:611-645` 断言 `_publication_gate_verdict` / `publication_gate_of_page` / `_binding_chain_ids` 各 1 个、`def read_gate(` 1 个、assembly 无 `gate_of_binding(` / `previous_binding_id`、service 无本地 row/一跳判定、`AuthorizeSourceReadForRun` 仍取 `catalog.source_gate_reader`。本报告独立 R3 把 service 改回旧启发式后，该静态用例确实 RED，说明断言有判别性（不是只看测试名）。
- 本报告独立 AST/grep 结果：`src/**` 中 publication-gate 的**判定**只有 `_publication_gate_verdict`；`gate_of_binding` 仍作为行读取 API 保留（被既有 `test_source_operation.py` / `test_source_sync.py` / `test_source_scan.py` 使用），不是第二份判定；`pending_gate_pages` 仍是写面/章级面的 pending-only 过滤（属卡面 Out 的 L-R11-b，不是本卡读面谓词）。
- P3 备注：`_publication_gate_verdict` 的 docstring 写「only publication-gate judgement in Core」在字面上略宽（写面/章级面仍有 pending-only 检查），建议理解为「唯一的读面 gate verdict」（P3-5）。

### AC-2 legacy 零回归 — **MET**

- 测试 `tests/fea11/test_source_gate_unify.py:368-418` 用真实 `MigrationRunner(conn, MIGRATIONS[:7])` 建 v7 库，插入 books/chapter/source/source_locations/version/entries/pages/page_bindings，再应用 v8 迁移（断言 applied == `[8]`），最后真实 `assemble_core_services`；不是 v8 内伪造 legacy 形态。
- 两种 legacy 形态均 `open`：
  - `p1`：healthy、`previous_binding_id IS NULL`、无 publication；
  - `p2`：两代 binding 链，`previous` 非空但**全链无 publication**（测试显式构造 `pb-p2` superseded + `pb-p2-b2` healthy）。
- 行为面在真实 assembly 上验证：`store.publication_gate_of_page` 与 `pipeline._catalog.source_gate_reader` 均 `open`；`create_run` 接受 `p2`；`source_commit_guard("p2")` 打开；provider 读出真实 zip 成员（12×7）；`handle_resolve_page_resource` 返回 `page-rendition-v2-…`；真实 wire grant + `AuthorizeSourceReadForRun` 返回 `{"bound_pages": 1}`。该用例实跑通过（新文件 6 passed）。
- 代码路径核对：当前 binding 无行时只遍历 `previous_binding_id` 链；链上没有任何 publication 才返回 `open`，因此「previous 非空但从未同步」的旧数据不会被误判为 corrupt（判据是「至少一行 publication」，不是「previous 非空」）。与 scope review §8.4 的误伤缓解要求一致。
- 回归面：`tests/fea11` 全量 212 passed；额外 resolve/reader 三文件 22 passed；未见 legacy 行为回归。

### AC-3 L-R11 一跳 fail-closed — **MET**

- 测试 `:519-525` 用真实 v8 库造 B1（publication `open`）+ B2（healthy、无行、`previous=B1`）；`_assert_damage_refused` 逐面断言：
  - 谓词 `corrupt_chain`、`read_gate == "unavailable"`；
  - `create_run` → `TARGET_NOT_FOUND`；
  - commit guard → `TARGET_NOT_FOUND`，detail `source binding is unavailable`；
  - provider → `ProviderInputError` / `INVALID_INPUT`，且 monkeypatch 的真实 `prepare_referenced_rendition` / `read_entry_bytes` 调用数 **0/0**（先 gate 后读取）；
  - resolve → `SOURCE_ACCESS_DENIED`，固定文本 `page binding has no read gate`；
  - reader projection → `SOURCE_ACCESS_DENIED`；
  - `AuthorizeSourceReadForRun` → `INVALID_REQUEST`（`catalog.expand` 先 typed 拒绝）、`result is None`、`_bindings == {}`、全表快照不变。
- 本报告 R1（把「全链无 publication → open」改成「无行即 corrupt」）使 legacy 用例 RED 而一跳/两跳仍 PASS，证明 legacy 与损坏分支的判别点在链上 publication 的存在性，不是测试名或断言方向凑巧。
- 错误 family：仅使用既有 `TARGET_NOT_FOUND` / `INVALID_INPUT` / `SOURCE_ACCESS_DENIED` / `INVALID_REQUEST`；diff 未新增错误码、wire 字段、命令、能力（P3-1/AC-5 另证）。

### AC-4 全链检测（两跳）— **MET**

- 测试 `:528-538` 用 B1（publication）+ B2（superseded、无行）+ B3（healthy、无行、`previous=B2`），各面与一跳完全相同的拒绝，实跑通过。
- 实现不是一跳：`_binding_chain_ids` 从 `previous_binding_id` 开始逐代读取，任一祖先有 publication 即 `corrupt_chain`；`seen` 防环，不会因损坏指针死循环。
- 判别性：本报告 R2 把 walk 改回「只查一跳」后，**两跳 RED、一跳 PASS、legacy PASS**（1 failed / 2 passed），精确命中 AC-4 的判别点；R3（resolve 面恢复旧一跳启发式）使两跳 + 静态唯一性 RED，说明 resolve 面也依赖同一全链判定。
- 两跳/多跳的语义与 C-17 §3.3「由 new previous 链检测」一致；`relation='added'`（previous NULL）缺行仍不可检测，按卡面 L-R11-a 保留。

### AC-5 零漂移 — **MET**

- `git diff 2e4d6128e 86cd1d124 --stat` 仅 3 个 allowed `src/**` + 新测试文件，共 4 文件。
- `git diff 2e4d6128e 86cd1d124 -- doc/plan doc/contracts src/infrastructure/sqlite/schema.py apps pyproject.toml requirements.txt` 为 **0 字节**（`ZERO_DIFF`）。
- `verify_pins.ps1` 实跑 **PIN AUDIT: PASS (all 18)**；C16 `67286eeca8cb`、C17 `aefa0fa5b17e`，与 EV 声明一致。
- `PROTOCOL_MINOR` 未被 diff 触碰，仍为 `src/bootstrap/core_service.py:320` 的 `PROTOCOL_MINOR = 3`。
- 未新增错误码/命令/能力/wire 字段；新增的 `PUBLICATION_GATE_*` 是 Core 内部 Python 常量，不是 wire 枚举。
- 提交隔离：`git show --stat` 显示 `1c1c9ca2f` 只含 3 个 src 文件、`86cd1d124` 只含新测试文件；未混入 Lead 的 docs-only 提交。

### AC-6 门禁/证据/不夸大 — **MET**

- 实跑数字与 EV/卡面一致（见 §3）：新用例 6、五个相关文件 72、`tests/fea11` 212、pins 18/18、check×2 PASS、API EXIT 0。
- 证据完整性：`RESOURCE-MANIFEST.json` 的 33 条 sha256（4 个 changed files + 29 个 evidence files）**逐条复算全部 MATCH**（0 mismatch）；`git diff --check` 退出 0。
- 未夸大：全文检索卡面/EV/Handoff，只有「不得写」「不构成」等否定表述；没有「C-17 §3.3 已完全实现」或「L-R11 全部关闭」的肯定主张。
- Limitation 逐项保留：`L-R11-a`（`relation='added'` 缺行不可检测 / plan receipt 未实现）、`L-R11-b`（写面/章级面仍 pending-only）、`L-R11-c`（映射既有 family、无专用诊断码/无新增日志行）、`L-R11-d`（不自动修复损坏 publication 行）、`L-R11-e`（真实 v7→v8 fixture）。卡面「交付记录」、EV §7、Handoff §4 三处一致。
- 全量 `pytest tests`：按任务要求未重跑；证据日志 `logs/pytest/full-pytest.log` 的 summary 为 `3369 passed, 10 skipped in 275.61s`，本报告只记录该证据、不独立背书。`verification/FEA-09` 对 `2e4d6128e` 与 `1e339f30a` 均零 diff，本次审查也未触碰它。

## 3. 实跑表

环境：Windows；`C:/Python314/python.exe`（CPython 3.14.6）；pytest 9.1.1；repo root 为 `G:\CODEX\New Manga`；HEAD 为 `1e339f30a`（`src/**`、`tests/**` 与 `86cd1d124` 无代码差异，文本等价；EOL 口径见 P3-1）。

| # | 命令 | 实测结果 | 备注 |
|---|---|---|---|
| 1 | `C:/Python314/python.exe -m pytest tests/fea11/test_source_gate_unify.py -q -p no:warnings` | **6 passed in 1.11s** | 与交付声明「新增 6」一致 |
| 2 | `C:/Python314/python.exe -m pytest tests/fea11/test_source_rendition_gates.py tests/fea11/test_source_rendition_source.py tests/fea11/test_source_rendition_run.py tests/fea11/test_source_run_grant.py tests/fea11/test_source_resolve.py -q` | **72 passed, 1 warning in 5.32s** | 既有面零回归；warning 为 `zipfile` duplicate name，既有 |
| 3 | `C:/Python314/python.exe -m pytest tests/fea11 -q -p no:warnings` | **212 passed in 11.33s** | 与「206 → 212」一致 |
| 4 | `C:/Python314/python.exe -m pytest tests/core/test_page_resource_resolve.py tests/fea09/test_referenced_resolve.py tests/fea11/test_source_resolve.py -q -p no:warnings` | **22 passed in 1.64s** | 额外 resolve/reader 回归 |
| 5 | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PIN AUDIT: PASS (all 18)**，EXIT 0 | C16 `67286eeca8cb`、C17 `aefa0fa5b17e` |
| 6 | `pwsh -NoProfile -File tools/governance/check.ps1` | **Governance check: PASS (3 warnings)**，EXIT 0 | 3 warnings 均为既有预算/非终态提示 |
| 7 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-11-L-R11-GATE-UNIFY-1.md` | **Governance check: PASS (3 warnings)**，EXIT 0 | 卡面路径检查通过 |
| 8 | `C:/Python314/python.exe tools/generate_api_inventory.py --check` | **API_EXIT=0**；61 方法 | `IReaderProgressSink` 1 / `IHostController` 54 / `IRunController` 6，与 FEA-C07 文档一致 |
| 9 | `git diff --check` | **exit 0**（无输出） | 无空白错误 |
| 10 | manifest 复核脚本（33 条） | **33 checked / 0 mismatch** | 见 §5 的 EOL 说明 |
| 11 | `C:/Python314/python.exe -m pytest tests -q -p no:warnings --tb=no` | **NOT_RUN**（按任务要求未重跑） | 证据日志 summary：`3369 passed, 10 skipped in 275.61s` |

## 4. 破坏性复跑表（独立于交付的 `mutate.py`）

备份：`G:\CODEX\New Manga.workspace\L-R11\review\baseline\{source_sync.py, core_service.py}`；破坏前 SHA-256：
- `source_sync.py` = `f0a014a9a40a83eea5c4496e49100512932ad55225dd9f7644c969befbaa861a`
- `core_service.py` = `b4176db635c3306102812ecb7cb7def4141781ad79e051986437411fe86b9474`

| # | 破坏点 | 预期 | 实测 | 复原 |
|---|---|---|---|---|
| **R1** | 把「全链无 publication → `open`」改成「无行即 `corrupt_chain`」 | legacy v7→v8 用例 RED；一跳/两跳（期望 corrupt）仍 PASS | `test_legacy_v7_bindings_stay_open_on_every_face` **FAILED**（`assert 'corrupt_chain' == 'open'`，`:379`）；`-k "legacy_v7 or hop"` 为 **1 failed, 2 passed** | 从备份复制；sha256 = `f0a014…` **MATCH** |
| **R2** | 把全链 walk 改回只查一跳 | 两跳 RED；一跳 + legacy PASS | `test_two_hop_missing_publication_fails_closed_everywhere` **FAILED**（`assert 'open' == 'corrupt_chain'`，`:433`）；**1 failed, 2 passed** | sha256 = `f0a014…` **MATCH** |
| **R3** | 把 resolve 面 `_assert_source_sync_gate` 改回旧一跳启发式（本地 `gate_of_binding` + `previous_binding_id`） | 静态唯一性 RED；两跳 resolve 面 RED；一跳仍 PASS | `test_two_hop_missing_publication_fails_closed_everywhere` + `test_core_has_exactly_one_publication_gate_judgement` **FAILED**；**2 failed, 4 passed** | sha256 = `b4176d…` **MATCH** |
| **R4** | 全部还原后重跑新用例 | 6 passed | **6 passed** | 两文件均与备份逐字节一致；`git status --porcelain` 无输出 |

结论：判别性 **3/3 RED_AS_EXPECTED + 3/3 复原 sha256 MATCH + 1/1 复绿**；与交付 `logs/discriminative/**` 的 4/4 结论方向一致（本报告独立覆盖了 M1/M3/M4 的判别点；未重复跑 M2 的原脚本，但 R2 已证明两跳对一跳截断的判别性）。破坏期间唯一改写的是两个生产文件，未触碰测试、证据、卡或其它路径。

## 5. 证据与关键代码事实核对

### 5.1 证据 sha256

- `RESOURCE-MANIFEST.json` 的 **33** 条记录（4 个 changed files + 29 个 evidence files）全部按当前工作树字节复算 **MATCH**，0 mismatch；`EV.md`、`logs/discriminative/SUMMARY.txt`、`logs/pytest/*`、`logs/scope/*` 均在内。
- **EOL 说明（P3-1）**：`changed_files` 中 3 个既有 `src/**` 文件的 sha256 是当前工作树的 **CRLF** 字节（`core.autocrlf=true`），不是 commit blob 的 LF 字节；`git show 86cd1d124:src/...` 的 sha256 分别为 `8bb643…`、`69eb66…`、`28dfde…`，但把 LF 规范为 CRLF 后与 manifest/工作树完全一致（文本内容逐字相同）。新测试文件恰好是 LF，manifest 值与其 blob 一致。该差异只影响「从 commit 重新 checkout 后复算」的可移植性，不构成本卡的行为或证据伪造；closeout 时建议显式记录该 EOL 口径（或按项目既有 `text eol=lf` 规则固定）。
- `file_count: 30` 与列出的 29 个 evidence 文件相差 1，因为生成器 `tools/gen_manifest.py:134` 有意把 manifest 容器自身计入（`len(evidence_files) + 1`）；manifest 的 `note` 已说明容器不自哈希。不是缺文件或伪造，仅为计数口径说明。

### 5.2 代码质量与本报告独立观察

- `_publication_gate_verdict` 顺序：当前非 superseded binding → 必须 healthy → 当前 publication 行（`open`/`pending`）→ 无行则全链任何 publication → `corrupt_chain`，否则 `open`。与 C-17 §3.3 / C-16 v1.7 §2.4 的规范句一致。
- `page_is_sync_managed` 改为复用 `_binding_chain_ids` / `_publication_row`，行为等价（存在性判断），`same_content_reachable` 改读同一行 helper，`_publication_of` 删除；`tests/fea11` 212 passed 覆盖了 lineage 既有用例。
- 全链 walk 有界：以 chain 长度为界，`seen` 防环；两跳/多跳均适用。
- P3-2（性能）：无 publication 的 legacy 链每代需要 2 条查询（previous + publication），初始还有 2 条；对 reader projection 的逐页调用是潜在 N+1。当前正常数据链很短，且 `page_is_sync_managed` 早已有同样 walk；不建议本卡返修，若后续 profiling 显示热点可改单条递归 CTE / JOIN。
- P3-3（观察一致性）：谓词由多条 SELECT 组成，未显式开只读事务；并发 sync apply 在语句之间提交时，理论上可观察到混合代次。该模式在修复前的 `read_gate`（binding + gate 两条查询）与 `SourceSyncLineageFacts` 已存在，本卡把窗口略微拉长（无行链时更多语句）；不是本卡新引入的类别，且 Core 写面通常串行。记录为残余风险。
- P3-4（错误文本）：`_assert_source_sync_gate` 对 `unavailable` 直接返回；若当前 binding 非 healthy 且同时有 pending publication（或 previous 链有 publication），旧 helper 会抛 `"page binding is pending acknowledgement"` / `"page binding has no read gate"`，新路径则落到 `prepare_referenced_rendition` 的 `"page binding is not healthy"`。**错误码/类别/retryable 不变（均为既有 `SOURCE_ACCESS_DENIED` / authorization / false）**，只是 wire `message` 文本在非 legacy 的窄形态下变化。若 Host 依赖文本匹配需注意；否则可接受。
- P3-5（措辞/静态断言）：`_publication_gate_verdict` docstring「only publication-gate judgement in Core」建议限定为「read-face verdict」，因为写面/章级面的 `pending_gate_pages` 仍是 pending-only 检查（L-R11-b）；静态测试用 `inspect.getsource` 子串计数，能覆盖当前代码并可被 R3 判别，但对未来重构（换名/换 SQL）不是强约束；行为测试与本次独立 AST 复核可补偿。
- 观察（非 finding）：无 publication 的**环或悬挂 previous 指针**会被 `seen`/遍历终止当作 legacy `open`；这符合「链上至少一行 publication 才算同步证据」的设计，但如果未来把「环」本身视为独立损坏形态，需要另加判定/limitation，目前不在卡面范围。

## 6. Findings

### P0

无。

### P1

无。

### P2

无（本报告没有发现需要返修才能 approved 的阻断项）。

### P3

1. **P3-1 证据 sha256 的 EOL 可移植性**：`RESOURCE-MANIFEST.json` 的 `changed_files` 三个 `src/**` 哈希是工作树 CRLF 字节，commit blob 是 LF；从 commit 重新 checkout（不同 `core.autocrlf`/`eol` 配置）复算会得到不同值。建议 closeout 记录口径，或按项目既有 `text eol=lf` 规则固定后再 pin。位置：`verification/FEA-11-L-R11-GATE-UNIFY-1/RESOURCE-MANIFEST.json:34-55`、`logs/scope/delivery-file-sha256.log`。
2. **P3-2 全链 walk 的查询放大**：无 publication 链每代 2 条查询，reader projection 逐页调用，存在潜在 N+1；当前数据规模可接受，建议作为性能观察项。位置：`src/infrastructure/sqlite/source_sync.py:81-147`。
3. **P3-3 多语句读取窗口**：谓词未在显式只读事务内取快照；并发 apply 提交时理论上可混合代次。修复前已有同类窗口，本卡仅略微加长；记录为残余 TOCTOU 风险。位置：同上。
4. **P3-4 resolve 面非 healthy+pending 的文本漂移**：错误码/类别不变，仅 `message` 从旧 helper 的 pending/no-gate 文本变为 `page binding is not healthy`；建议在 Host 侧确认不依赖该文本。位置：`src/bootstrap/core_service.py:5303-5336`。
5. **P3-5 措辞与静态断言精度**：单谓词 docstring 的「only judgement in Core」应限定 read-face（写面/章级面 pending-only 仍在）；静态唯一性用例是源码子串计数，建议保留行为用例作为主判据。位置：`src/infrastructure/sqlite/source_sync.py:116-121`、`tests/fea11/test_source_gate_unify.py:611-645`。

## 7. 结论与复审建议

- **Verdict: `approved`**。AC-1…AC-6 均成立；单一读面谓词、legacy 零回归、一跳/两跳 fail-closed、零契约/schema/wire/依赖漂移、证据与 limitation 口径均达到卡面要求。P0/P1/P2=0，P3 均为非阻断观察项，不要求本卡返修。
- 复核建议：Lead 集成门禁在其当前 HEAD 重跑 pins/check/定向与 `tests/fea11`；closeout 时把 P3-1 的 EOL 口径写进 evidence/release note，保留 L-R11-a…e，不把本卡写成「C-17 §3.3 已完全实现」或「L-R11 全部关闭」。
- 若实现/测试在集成前发生变化，需按新 head 重新审查本报告的 AC-1/AC-2/AC-3/AC-4 行为与 §4 判别点；若只前进 docs/evidence（本报告审查的 `1e339f30a` 相对 `86cd1d124` 即如此），现有结论可沿用。

## 8. 真实性声明

- **写入范围**：仓内唯一写入为 `doc/reviews/FEA-11-L-R11-GATE-UNIFY-1-r1.md`；未修改实现、测试、证据、卡、契约、schema、STATUS/PLAN/LEDGER；未 `git add/commit/push`。临时脚本、备份与破坏性复跑日志在仓外 `G:\CODEX\New Manga.workspace\L-R11\review\`（`replay.py`、`verify_manifest.py`、`eol_check.py`、`ast_scan.py`、`baseline/`、`logs/`）。
- **独立性**：fresh subagent（派发会话 `session-3ac1953a-094e-4339-889a-284df2b7b34d`），未参与本卡任何实现、返修、scope review、C-16 v1.7 UNFREEZE 或 Lead 的并发 docs 提交；只读 `86cd1d124` 与 `1e339f30a`。
- **破坏性复跑**：仅临时改写 `src/infrastructure/sqlite/source_sync.py` 与 `src/bootstrap/core_service.py`，每次从备份逐字节复原并核对 SHA-256；结束后两文件 sha256 与备份一致，`git status --porcelain` 无 tracked 变更；未触碰 `verification/FEA-09`。
- **实跑与未跑**：实跑见 §3 第 1–9 项；**未跑**全量 `pytest tests`（按任务指示；仅核对证据日志）、全量 .NET、真实 IPC/gated、`build`；未对未跑项背书。
- **不夸大**：本报告不声称「C-17 §3.3 已完全实现」「L-R11 全部关闭」；不声称实现已完成集成或 push；P3 均为非阻断建议，最终处置由 Lead 决定。
