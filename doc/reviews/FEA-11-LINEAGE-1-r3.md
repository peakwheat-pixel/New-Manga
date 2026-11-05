---
task_id: FEA-11-LINEAGE-1
reviewer: 独立上下文 fresh subagent（DSH 派发；未参与实现/返修）
reviewer_kind: subagent
base_commit: 81c28d305
reviewed_head: 90a8c8218
decision: changes_requested
---

# Review：FEA-11-LINEAGE-1（r3）

> 审查者：DSH 派发的独立上下文 fresh subagent（父会话 `session-8db9dae5-49df-4d09-ac62-696f0805a95c`），未参与本任务任何实现、返修或 r1/r2 处置；本报告只读审查。
> 审查对象：`90a8c8218`（main，`base_commit=81c28d305`）；r3 commits `d8ed04e13`（修复）、`6c0ab6594`（测试）、`280bb7bd0`（gates 证据）、`90a8c8218`（卡面）。r2 被审 head `3c40f7020`，r2 Review `doc/reviews/FEA-11-LINEAGE-1-r2.md`。
> 冻结依据：`doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md` §7.1/§8；`doc/reviews/FEA-11-r7-acceptance.md` 的 LINEAGE-1 硬约束；任务卡 r2 DSH 裁决（4 点）；r1 Review `doc/reviews/FEA-11-LINEAGE-1-r1.md`。
> 环境：Windows / PowerShell 7.6.8 / `C:/Python314/python.exe`（3.14.6, sqlite 3.50.4）。审查日志与探针全部在仓外 `G:\CODEX\New Manga.workspace\FEA-11\review-r3\`。

## 结论

**changes_requested：P0=0 / P1=0 / P2=1 / P3=4。**

- **代码与测试层：R2-01、R2-02、R2-03（4 个测试）、R2-05 均实质修复**，测试具备判别力（见「独立反证」）；AC1/AC3 维持 MET，AC2 按卡面原文（读守卫/过滤/typed/计数）可维持 MET。
- **P2-R3-01（closeout 前必须处置，非代码阻断）**：L1 的「已闭环…**无 deferral**」与行为矩阵「全 hidden 时**在新图**检测」属于**过度声明**。真实 AD-003 referenced 同步页（`managed_original_ref=NULL`）在 `_page_or_error` 即被既有门槛拒绝（`TARGET_NOT_FOUND "page has no managed original"`，`src/infrastructure/sqlite/pipeline.py:1433-1434`）；r3 的 REOCR_ALL 测试页是「referenced **且** `managed_original_ref` 非空」的混合构造（`tests/fea11/test_source_lineage_native.py:85-98`），且 detect 的图源 `_ManagedPageImageSource` 只读 Managed Copy original，**不是**当前 binding 的 C-17 §7.2 rendition（`src/bootstrap/core_assembly.py:351-428`）；测试用 `_StubImages`（`tests/fea11/test_source_lineage_run.py:122-131`）只证明执行链被调用，未证明「新图」。因此：在纯 referenced 页上 page-scope Run 仍是不可执行（既有门槛，非 r3 引入）；在混合页上「新图检测」的输入仍是旧 Managed Copy 图（同步不更新该字段），若该图与当前 binding 不同，detect 输出坐标会被以 native lineage 记到新 binding（潜在旧坐标 native 化；当前真实 referenced 路径被门槛挡住，未证实为生产泄漏）。**这不否定 R2-01 的代码修复**（不再复用 hidden、不再 `DB_FAILED`、空集干净终态均已实现并有判别测试），但 L1/矩阵必须限定或登记 L10，交付方不得写「无 deferral」。
- 其余 4 项为 P3（prepared-snapshot digest 兼容、detect 输出被隔离时的静默完成、卡面残留 r2 文本/行号/新测试文件未入 frontmatter allowed_paths、gates 日志命令细节），均不阻断，建议在本轮卡面修正时一并处理。
- **R2-02 语义裁决：满足 C-17 §7.1 交错行「结果留 candidate，不改已接受快照」**（详见专节）；旧命令面保持既有 conflict，不重映射 §8。

## 范围与依据

- 需求：任务卡 AC1/AC2/AC3 + r2 DSH 四点裁决 + C-17 §7.1（同事务 native lineage、same_content 读边、changed 切断、page-id-only repository 不得成为旁路）+ §8（局部错误闭集仅 C-17 命令投影，旧命令不重映射）+ r7 硬约束（LINEAGE-1 完成前读路径不得消费同步新 binding）。
- r3 逐 commit 范围（本审查实际核验的代码面）：
  - `d8ed04e13`：`src/application/rendering/service.py`、`src/application/sources/lineage.py`、`src/application/tasks/service.py`、`src/bootstrap/core_assembly.py`、`src/infrastructure/providers/handlers.py`、`src/infrastructure/sqlite/pipeline.py`、`src/infrastructure/sqlite/source_sync.py`（7 文件，全部在 allowed_paths）；
  - `6c0ab6594`：`tests/fea11/{conftest,test_source_lineage_native,test_source_lineage_assembly}.py` + 新增 `test_source_lineage_run.py`（Scope Review line 58 的 `tests/fea11/**` 覆盖；frontmatter 明细未列新文件，见 P3-R3-04）；
  - `280bb7bd0`：`verification/FEA-11-LINEAGE-1/logs/gates-r3.log`；`90a8c8218`：仅卡面。
- 期间并发任务：base..head 整体含 FEA-11-HOST-AUTH-1/FEA-12-PREREQ-1/DSIM-1 的提交（含 `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` 的 166 行变更，属 `26775dfef`/`08b359251`，非本卡）；本卡 r3 四个 commit 的逐段 diff 已独立核对。
- 审查期间并发事实（诚实记录）：开始 HEAD=`90a8c8218`；复跑期间 Lead/其他 Agent 提交 `144683876`、`4a63c781a`（FEA-12-DSIM-1 docs），HEAD 前进到 `4a63c781a`；`git diff 90a8c8218..4a63c781a -- src tests` **为空**，故本报告测试结果对 `reviewed_head` 的 Python 代码有效。fea11 测试会向 tracked `verification/FEA-09/logs/wire-redacted.ndjson` 追加一行（15:50:19），该测试副作用在审查期间已被并发工作恢复；当前 `git status` 干净。本 Reviewer 未主动写仓库。

## R2 finding 核销表

| R2 | 级别 | 判定 | 核销证据（file:line / 测试 / 独立复跑） |
|---|---|---|---|
| **R2-01** page-scope Run detect 复用绕过 lineage 集合 | P1 | **已修复（代码与测试成立）；L1 表述需修正（R3-01）** | `handlers.py:351`（detect 复用改走 `_lineage_visible_live_regions`）、`:446-479`（guard 过滤 + `[providers.detect] lineage_hidden=N`）；`core_assembly.py:1562-1568` 注入与 catalog **同一** `lineage_guard`（唯一生产 `build_production_handlers` 调用点）；`pipeline.py:1544-1577` 返回 `(visible, hidden_count)`，`:1462-1466` 计数入 page metadata；`tasks/service.py:573-588` 全 hidden 且链不含 `ocr` → 空 unit（task SKIPPED/run COMPLETED），`_plan_region` 的 detect 链对 REOCR_ALL/TRANSLATE_ALL 仍保留；`:1455-1474` 把 LINEAGE_* 加入 `_backfill_detected_regions` 的「不可读跳过」集。测试：`test_source_lineage_run.py:224-282`（hidden 不复用、detector 实际调用、2 个新 region native 入当前 binding、hidden 零写）、`:285-307`（RERENDER_ALL 零 step/SKIPPED/COMPLETED）；REINPAINT_* 共用同一「链不含 `ocr`」短路分支（`_COMMAND_STEPS`，`tasks/service.py:104-128`），未单独测试（低风险）。独立复跑 69/69 与定向 8/8 全绿；反证见下。**TASK-040 既有 regionless clean-probe 语义未被破坏**：planner 仅对 `lineage_hidden>0` 且链不含 `ocr` 短路（`tasks/service.py:573-588`），hidden=0 的 regionless 页仍走原 `_plan_region(None)`；`tests/core/test_bootstrap.py:800/814` 的既有 TASK-040 测试在 3093 全量中通过。残余见 R3-01（真实图源/门槛）。 |
| **R2-02** 候选提交 typed lineage 分支不可达 | P2 | **已修复；语义满足（approve）** | `pipeline.py:1048-1064` 新增 `except PipelineError`：`_LINEAGE_PIPELINE_CODES`（`:65`）→ `_reject_prepared("input_revision_changed", error.code, ...)`，其他 PipelineError 仍 `db_failed`；`_reject_prepared`（`:1230-1264`）回滚 + 旧 prepared token 标 `abandoned`；`tasks/service.py:945-967` 既有 `input_revision_changed` 分支把 `result.outputs` 保留为 reason=`INPUT_REVISION_CHANGED` 的新 `StepResultCandidate`（`domain/tasks/models.py` 默认 `status="pending"`，非 abandoned）。测试 `test_source_lineage_run.py:315-383` 断言 `outcome.status=candidate`、`error_code=INPUT_REVISION_CHANGED`、detail 含 `LINEAGE_BINDING_CHANGED`、零 revision/lineage、current 不变、DB 候选行 reason=INPUT_REVISION_CHANGED 且 status≠abandoned。反证：把 `_LINEAGE_PIPELINE_CODES` 置空后同场景得 `failed/DB_FAILED`（probe B），证明测试判别修复。 |
| **R2-03** 关键判别性测试缺失 | P2 | **已修复（4 个测试均真实判别）** | (a) `test_source_lineage_native.py:882-936`（真实 `DraftProtectionService`+`SqliteRegionRepository`；cut 后 `DraftError.code=LINEAGE_BINDING_CHANGED`+零写）；(b) `:938-984`（真实 `RegionEditingService`；reorder/merge 均 `LineageBindingChanged`+零 revision/lineage/新 region）；(c) `test_source_lineage_assembly.py:214-236`（monkeypatch `SourceSyncStore.backfill_legacy_unverified_lineage` 抛错，`assemble_core_services` 仍成功、guard identity 仍在、stderr 含 `legacy lineage backfill failed`）；(d) `test_source_lineage_assembly.py:327-346`（真实装配 `core.render.rerender_page("p2")` → blocked + `skip_reason=LINEAGE_BINDING_CHANGED` + reports；`server.handle_rerender_page` → `RenderCommandError` code/category）。无 fake repo/`__new__`，无删测试/放宽既有断言（r2 断言保留，conftest 仅修正 `verified_digest` 为 entry digest）。 |
| **R2-04** allowed_paths 与卡面不一致 | P2 | **已处置（Lead 改卡文本；自洽）** | 卡面 line 58 明确「`doc/TASK_LEDGER.md` 由 Lead 维护、不计入本卡 allowed_paths（r2 Review R2-04 更正…；本卡提交未再修改该文件）」，line 74/98 呼应。`git log 81c28d305..90a8c8218 -- doc/TASK_LEDGER.md` 显示的修改均来自 Lead/FEA-12 生命周期与 r1 生命周期（`ef35fc035`/`035468a81`/`912f97eac`/`86bc87e1e`/…），**r3 四个 commit 均未改该文件**。文字自洽。 |
| **R2-05** lineage 未校验 region 归属 | P3 | **已修复（判别性成立）** | `lineage.py:54-64` 增 `RevisionLineageStanding.region_id`；`:182-185` 在 `_code_for` 中「行归属的 region ≠ 查询 region」→ `LINEAGE_UNVERIFIED`；`source_sync.py:922-946` facts 查询同取 `region_id`。测试 `test_source_lineage_native.py:986-1013` 构造 FK 合法但 `rv1` 的 lineage 行写 `region_id=rg2`、binding relation=`same_content`（**可达**），断言 `verdict.hidden==[("rg1",LINEAGE_UNVERIFIED)]` 且 `ensure_readable` 抛 `LineageUnverified`；即只有归属校验能否决，判别性成立（若删校验会沿 same_content 放行）。 |
| **R2-06** mixed 页 reorder/text 读诊断 | P3 | **登记充分（L4）** | 代码事实核对一致：`editing/service.py:1183-1215` reorder 用未过滤的 `list_regions`（含 hidden），`_commit_region_batch` 的 `ensure_writable` 会整体拒绝 mixed 页重排；`create_region` 的 `existing`（`:691-695`）含 hidden；`core_service.py:2407-2479` 显式 `region_ids` 命中 hidden → `RegionLookupError`（TARGET_NOT_FOUND）+ `_log_lineage_hidden` 计数。L4 描述与事实一致，非数据安全问题。 |
| **R2-07** freeze_context 未过滤 | P3 | **登记充分（L5）** | `pipeline.py:1596-1615` 仍直读相邻页全部 region 的 `ocr_text` 作为翻译上下文，未过 guard；无坐标产物。L5 描述准确。 |
| **R2-08** Host 未注册 LINEAGE 码 | P3 | **登记充分（L6）** | `apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandRegistry.cs:30-39` 的 `AllowedRunErrorCodes` 无 `LINEAGE_BINDING_CHANGED/LINEAGE_UNVERIFIED`；未注册码保持原串、category=unknown、retryable=false（fail-closed）。L6 与代码一致；`apps/**` 不在本卡 allowed_paths。 |
| **R2-09** 证据卫生 | P3 | **部分处置，可接受** | EV-0/EV-1/EV-2 `sha256` 已补并与实际文件一致（`e4861691…`/`a2b2aa86…`/`729ed81e…`，本次独立复算）；`gates-r3.log:1-12` 有 shell/解释器/sqlite/venv/OS/worktree 头；`delivery_head`/`canonical_evidence_status` 按生命周期留 closeout。 |

## R2-02 语义裁决（关键）

**意见：满足 C-17 §7.1 交错行「结果留 candidate，不改已接受快照」，不要求把原 prepared 行保持为非 abandoned。**

依据：

1. C-17 §7.1 表格该行为「Prepare Run(B1)后同步B2 → 旧 Accept/结果 live apply 拒绝 STALE_RUN_SNAPSHOT/既有 source guard；**结果留 candidate，不改已接受快照**」。「结果」指 Run 步骤产出的 `StepResult.payload`；`prepared token` 是 prepare 阶段的**租约**（绑定 base revision/绑定的候选 id），切换后本来就不能再 commit（既有 `input_revision_changed` 语义就是 abandon 旧 token）。
2. 实现把 `result.outputs` 转存为**新的** `StepResultCandidate`（reason=`INPUT_REVISION_CHANGED`、`status="pending"`、`base_revision_id` 仍是旧基线），并让 `step_run.error_code=INPUT_REVISION_CHANGED`、task 失败、run 不进新 binding；业务零写（测试断言 revision/lineage/current 不变）。这正是「结果保留为 candidate、不改已接受快照」。
3. 旧命令面：Run 的 wire 映射（`core_service.py:5088-…`）把 `LINEAGE_*` 投影为既有 `conflict`（应用层码），未加入 C-17 §8 闭集，也未修改 §8 冻结字节——符合 DSH 裁决「旧命令不重映射」。
4. 若 DSH 坚持「prepared 行本身也必须保留为非 abandoned」，则需要改 `_reject_prepared`（新增 `keep_prepared` 分支、不 UPDATE status='abandoned'），风险是：该行仍是 `prepared` 状态会被后续 prepare/commit 校验或清理逻辑当作可用租约（`_run_startup_cleanup` 会扫 prepared→abandoned），且与既有 `input_revision_changed`（Run 失败 + 新候选行）语义冲突。**不建议**在本卡改；当前「旧 token abandoned + 结果转存新 candidate」是可辩护的 §7.1 落法。

## AC 逐条判定

- **AC1（同事务 native lineage；B1/R1→B2、same_content、changed 有测试）→ MET**：r2 已覆盖全部写路径，r3 未回退；本次复跑 `tests/fea11` 69 passed（含 native 写路径/回滚/多跳/draft/Run/restore）。`<<MET>>` 有实体证据。
- **AC2（ListRegions/渲染/导出/Run/编辑入口读守卫；same_content 放行；过滤带诊断计数）→ MET（按原文）**：ListRegions/`list_page_region_texts` 过滤（`core_service.py:2407-2479` 与 editing `_visible_regions`）、export 过滤、page render reports/skip、单 region `BLOCKED`、编辑/region-scope Run typed、page-scope Run detect 可见集合（r3）均已实现；本次复跑含 assembly wire 断言与 stderr 计数。**限定**：若 DSH 把「page-scope Run 在真实 referenced 页上完成新图检测」纳入 AC2，则受 R3-01 影响，应为 MET-with-limitation；按 AC2 原文字面（读守卫）判 MET。
- **AC3（AC11-5 旧坐标对新图不可见 + 回归）→ MET**：native/assembly 测试覆盖 cut 后 list/export/编辑/渲染/Run 拒绝与零写；r3 的 REOCR_ALL 测试额外证明 hidden 区域无新 revision/lineage。`<<MET>>` 有实体证据。

## 独立复跑与证据

| 门禁 | 命令 | 实测 | 证据 |
|---|---|---|---|
| fea11 | `C:/Python314/python.exe -m pytest tests/fea11 -q -p no:warnings -p no:cacheprovider --tb=no` | **69 passed**，EXIT 0（1.89s） | `review-r3\gate1-fea11.log` |
| 全量 pytest | `… -m pytest tests -q -p no:warnings -p no:cacheprovider --tb=no` | **3093 passed, 10 skipped**，EXIT 0（253.35s） | `review-r3\gate2-full.log` |
| r3 定向（-s） | `pytest tests/fea11/test_source_lineage_run.py tests/fea11/test_source_lineage_native.py::test_mixed_library_scope_matrix_is_diagnosable tests/fea11/test_source_lineage_assembly.py -q -p no:warnings -p no:cacheprovider -s` | **8 passed**，EXIT 0；stderr 见 `[providers.detect] page=p1 lineage_hidden=1`、`[core.rerender_page] code=LINEAGE_BINDING_CHANGED`、matrix 五行 | `review-r3\gate3-r3-discriminating.log` |
| governance | `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS (3 warnings)**，EXIT 0 | `review-r3\gate4-check.log` |
| governance（本卡） | `… check.ps1 -TaskPath doc/tasks/FEA-11-LINEAGE-1.md` | **PASS (2 warnings)**，EXIT 0（warning 数与交付日志差 1，系并发文档变化） | `review-r3\gate5-check-task.log` |
| pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PIN AUDIT: PASS (all 18)**，EXIT 0 | `review-r3\gate6-pins.log` |
| .NET | 未跑 | **NOT_RUN（合理）**：本卡 Python-only；r3 commit 范围 `apps/**` 零 diff；`base..head` 的 apps 变更为 FEA-11-HOST-AUTH-1/FEA-12 并发任务，不计入本卡 | 本报告 |
| 冻结/依赖/schema | `git diff d8ed04e13^..6c0ab6594 -- doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md doc/contracts doc/design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md verification/FEA-09 'apps/**' pyproject.toml 'requirements*.txt' src/infrastructure/sqlite/schema.py src/infrastructure/sqlite/migrator.py` | **空 diff**，EXIT 0；`base..head` 的 `doc/contracts/M2-C1…` 166 行属 FEA-12 提交（`26775dfef`/`08b359251`） | 本报告 |

**独立反证（判别力）**（`review-r3\gate7-probes.log`）：

- **Probe A（R2-01）**：在 r3 代码上把 `ProductionHandlers._lineage_visible_live_regions` 换回 r2 的 page-id-only 行为，跑同一 REOCR_ALL 场景 → detect 输出 `region_ids=('rg1',)`、`reused_existing_regions=1`、detector 调用 0；r3 测试的 `"rg1" not in output_ids / len==2 / detector.requests` 断言会失败。**注意**：由于 r3 的 `_backfill_detected_regions` 已把 LINEAGE_* 加入 skip，旧行为下 run 仍会 COMPLETED（静默、零 OCR），所以「run COMPLETED」本身不构成判别断言；测试的判别力来自 detect output/新 region/OCR 断言——这一点成立。
- **Probe B（R2-02）**：把 `pipeline._LINEAGE_PIPELINE_CODES` 置空（模拟 r2 路由），同 prepare→cut→commit 场景 → `outcome.status=failed`、`error_code=DB_FAILED`、detail 含 `LINEAGE_BINDING_CHANGED`；r3 测试的 `candidate/INPUT_REVISION_CHANGED` 断言会失败。判别力成立。
- R2-03(a)(b)(d) 与 R2-05 的判别性由「代码路径 + 测试构造」独立核对：去掉 `ensure_writable`/draft `lineage_binding`/`_active_regions` 全 hidden 提前拒绝/region_id 归属校验，对应断言分别失败；R2-05 的 `same_content` 关系使“只有归属校验能否决”成立。

## 范围 / 冻结 / 诚实性核对

- **allowed_paths**：r3 四 commit 的 11 个文件全部落在卡面 allowed_paths（含 `src/application/rendering/**`、两处 r3 窄批、`src/infrastructure/sqlite/*`、`src/application/sources/lineage.py`、`src/bootstrap/core_assembly.py`）与 Scope Review line 58 的 `tests/fea11/**` 内。**无越界代码**。
- **冻结**：C-17 §7.1/§8 字节零 diff；ADJ-001、FEA-01 零 diff；`verification/FEA-09/**` 在 r3 commit 范围零 diff；无新增依赖；无 schema/migrator 变更；未 push（无远端引用证据）。
- **AC 标记**：AC1/AC2/AC3 均 `<<MET>>` 且有实体测试证据（见上）；AC2 的 MET 可按原文维持，但 L1 的「无 deferral」不成立（R3-01）。
- **并发隔离**：`base..head` 整体包含其他任务（FEA-12-PREREQ-1/DSIM-1、FEA-11-HOST-AUTH-1）的提交与 `doc/contracts/M2-C1…` 变更；本审查按 r3 逐 commit 核验，未把这些计入本卡。审查期间 HEAD 前进到 `4a63c781a`，但 `90a8c8218..4a63c781a` 的 `src/tests` 为空，复跑结果对 reviewed_head 有效。

## limitation 意见

- **L1（导出/Run/ListRegions/单区域渲染守卫）→ 不能判「已闭环、无 deferral」**。读守卫与执行链（detect 不复用 hidden、不 DB_FAILED、空集干净终态、candidate typed 投影）已实现并有判别测试；但「全 hidden 时在**新图**检测」在真实图源上不成立：纯 referenced 同步页被既有 `managed_original_ref` 门槛拒绝（`pipeline.py:1433-1434`），r3 测试页是「referenced + managed original 非空」的混合构造，detect 图源 `_ManagedPageImageSource` 读 Managed Copy original 而非当前 binding 的 §7.2 rendition（`core_assembly.py:351-428`），测试 `_StubImages` 未验证图像内容。建议把 L1 改为「**执行链守卫已闭环**；provider 图像源仍为 Managed Copy original，纯 referenced 页不可进入 page-scope Run（既有门槛），真实 referenced 图像源（C-17 §7.2 rendition）属后续卡/集成限制」，并在矩阵对应行同步限定；建议新增 **L10** 记录该缺口与「混合页 managed original 与当前 binding 不同时 detect 坐标不可信」的风险。
- **L2/L3 → 已闭环**：同意（真实 SQLite/装配覆盖；same_content 多跳实现与测试）。
- **L4/L5/L6/L7 → 登记充分**：与代码事实一致（见核销表）；L6 的 Host 窄批建议、L4 的 reorder/text 诊断建议、L5 的 context 过滤建议均合理。
- **L8/L9 → 说明性，同意**。
- 建议：若 DSH 认为「referenced 页 Run」不属于本卡可达产品范围，请在卡面/矩阵显式写「Run 仅支持 `managed_original_ref` 非空的页（含升级混合页）」，避免后续误读为已支持 AD-003 referenced 页。

## done / changes_requested 意见与最小返修点

- **当前不建议 done**：R3-01 是明确的过度声明（L1「无 deferral」/矩阵「在新图检测」），与卡面「不得把未实现写成 MET/闭环」的自律要求冲突；但这**不是代码或测试返修**，而是卡面/限制登记问题。
- **最小返修点（不要求改代码/测试，建议 r4 或 closeout 前由 Lead 处置）**：
  1. 卡面 L1 改为「执行链守卫已闭环；真实 referenced 图源/既有 managed-original 门槛为集成限制」，并新增 L10（含证据 `pipeline.py:1433-1434`、`core_assembly.py:351-428`、r3 测试页混合构造与 `_StubImages`）；
  2. 行为矩阵的「全 hidden 时在新图检测」改为「在测试装配的 stub 图源上执行检测；真实 referenced 图源待后续卡」；
  3. （P3）清理卡面 line 152-153 残留的 r2 门禁/自审段落、line 74 的旧行号引用；把 `tests/fea11/test_source_lineage_run.py` 补进 frontmatter allowed_paths；
  4. （P3）在 L 或 EV 说明中记录 `lineage_hidden_regions` 进入 prepared-snapshot digest 的一次性 `RUN_STALE_PREVIEW` 影响，以及 `_backfill_detected_regions` 对 LINEAGE_* 静默 skip 的行为（建议加 stderr 计数）。
- **判别性测试建议（针对 R3-01，后续卡）**：用真实 `_ManagedPageImageSource` + 纯 referenced 页（`managed_original_ref=NULL`）断言 `_page_or_error` 的既有 `TARGET_NOT_FOUND`，固化「Run 不支持 referenced 页」边界；或在接 rendition 后，用真实新图与旧 managed original 不同的页断言 detect 输入来自当前 binding（否则禁止写 native）。
- 若 DSH 裁决 R3-01 仅为文字修正并接受为已知限制，则本轮代码/测试已满足 R2-01/R2-02/R2-03/R2-05 的返修目标；但在卡面修正前，不建议把 L1 保持「已闭环/无 deferral」。

## 自审声明

- 独立上下文 fresh subagent（DSH 派发，父会话 `session-8db9dae5-49df-4d09-ac62-696f0805a95c`），未参与 FEA-11-LINEAGE-1 的任何实现、返修或 r1/r2 处置；只读审查。
- 只读仓库：未 commit/push/stash/reset/checkout；未主动修改仓库任何文件。观察到的 `verification/FEA-09/logs/wire-redacted.ndjson` 一行追加是 fea11 测试的既有副作用（15:50:19），在被并发工作恢复后当前工作树干净；HEAD 前进到 `4a63c781a` 是其他 Agent 的并发提交，非本 Reviewer 所为。
- 所有 pytest 日志、探针、报告均写在仓外 `G:\CODEX\New Manga.workspace\FEA-11\review-r3\`；测试使用 `:memory:`/pytest `tmp_path`，未触碰真实用户数据、AppData、外部卷或回收站。目录内 `pytest-full-reviewer.log`（02:58 创建）为既有遗留文件，非本 Reviewer 写入；本 Reviewer 的文件为 `gate1…gate7` 日志、`probe_r3_discriminating.py` 与本报告。
- 未引用聊天记录作为事实；所有结论以 Git、文件与实测输出为依据。
