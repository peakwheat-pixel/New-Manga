---
task_id: FEA-11-LINEAGE-1
reviewer: 独立上下文 fresh subagent（DSH 派发；未参与实现/返修/前轮处置；session dde30402-06b5-43e7-ae1d-374408e55823，父会话 session-8db9dae5-49df-4d09-ac62-696f0805a95c）
reviewer_kind: subagent
base_commit: 81c28d305
reviewed_head: f11bff37e
decision: approved
---

# Review：FEA-11-LINEAGE-1（r4 复核）

> 审查者：DSH 派发的独立上下文 fresh subagent（session `dde30402-06b5-43e7-ae1d-374408e55823`，父会话 `session-8db9dae5-49df-4d09-ac62-696f0805a95c`）。未参与本任务任何实现、返修或 r1/r2/r3 处置；本报告只读复核，未修改仓库。
> 审查对象：`f11bff37e`（main；`git rev-parse HEAD` = `f11bff37e2522afd7de88aa169d70e90c82c9978`）。r3 代码/测试 head 为 `90a8c8218`；f11bff37e 为 docs-only 处置提交（r3 报告落盘 + 卡面 L1 限定/L10/L11/矩阵修正/R3 P3 登记）。
> 依据：任务卡 `doc/tasks/FEA-11-LINEAGE-1.md`（status in_review）、r3 Review `doc/reviews/FEA-11-LINEAGE-1-r3.md`（decision changes_requested；reviewed_head `90a8c8218`）、r3 派发指令中的 R3 finding 清单、C-17 §7.1/§8 与 AD-003 架构事实。
> 环境：Windows / PowerShell 7 / `C:/Python314/python.exe`（3.14.6）。本轮日志全部在仓外 `G:\CODEX\New Manga.workspace\FEA-11\review-r4\`。

## 结论

**approved：P0=0 / P1=0 / P2=0 / P3=1。**

- **R3-01（原唯一 P2，过度声明）已消除**：L1 改为「执行链守卫已闭环（r3 Review 限定口径）」，新增 L10 如实登记真实 referenced 图源缺口，行为矩阵 changed 行改为「测试装配 stub 图源」并指向 L10；独立核对 `pipeline.py:1433-1434`、`core_assembly.py:351-428`、r3 测试页混合构造（`seed_page` 的 `source_mode='referenced'` + `managed_original_ref='original/p1.png'`）与 `_StubImages`（固定全零 32×16 帧）后，L10 三点描述与代码/测试事实一致。
- **R3-02/R3-03 已登记为 L11①/②，且与代码事实一致**：`TargetSnapshot.metadata` 是 `prepared_quartet` 的组成部分（`store.py:46-69`、`service.py:477-479`），`lineage_hidden_regions` 变化确会触发旧 prepared run 的 `RUN_STALE_PREVIEW`；`_backfill_detected_regions` 的 `LINEAGE_*` skip 分支（`tasks/service.py:1464-1474`）确实静默 `continue`、无计数输出。
- **R3-04 部分核销（唯一 P3）**：`tests/fea11/test_source_lineage_run.py` 已补进 frontmatter allowed_paths；尾部「请求 Lead 指派 fresh reviewer 做 r2 Review」「交付 head 以最终报告为准」两行已删。但 **r2 门禁数字行（62 passed / 3073 passed）仍保留为现卡 line 155**，与 r3 门禁行（69/3093）并列且无 r2 标签；Lead 处置声明「删除…r2 门禁/自审段落」与实际不完全一致。另 line 169 重复「本实现者不自审…」句。均属 cosmetic，不阻断。
- **R3-05 已记录且事实成立**：`gates-r3.log:15` 的 gate1 命令确缺 `-p no:cacheprovider`；本轮实测 check 默认/本卡均 PASS (2 warnings)，与 r3 记录的 3/2 warnings 差异可由并发文档环境解释。
- **AC1/AC2/AC3 维持 MET**：`<<MET>>` 有实体证据（r3 独立复跑 69/3093 + 本轮独立复跑 69 + collect 全量测试名映射），AC2 的限定已由 L1/L10 显式承接，卡内无与 limitation 矛盾的 MET 声明。
- **未发现新 P0/P1/P2**；无代码/测试改动可审。**可转 approved 并进入 closeout**（closeout 时建议顺手清理 P3 残留，见末节）。

## R3 finding 核销表

| R3 | 级别 | 判定 | 核销证据（独立核对） |
|---|---|---|---|
| **R3-01** L1「无 deferral」/矩阵「在新图检测」过度声明 | P2 | **已消除（核销）** | 卡面 L1（line 127）改为「执行链守卫已闭环（r3 Review 限定口径）」并明写「**不得**表述为『真实 referenced 图源已闭环』」；新增 L10（line 136）记录三类事实；矩阵 changed 行（line 112）改为「在**测试装配 stub 图源**上检测（…真实 referenced 图源受既有 managed-original 门槛限制，见 L10）」。独立核实：`pipeline.py:1429-1434` 对 `source_hash IS NULL OR managed_original_ref IS NULL` 抛 `TARGET_NOT_FOUND "page … has no managed original"`；`core_assembly.py:351-428` 的 `_ManagedPageImageSource._page_image` 只读 `page.managed_original_ref`（缺失即 `ProviderInputError`），生产装配点 `core_assembly.py:1553`；`tests/fea11/test_source_lineage_native.py:85-97` 的 `seed_page` 为 `source_mode='referenced'` **且** `managed_original_ref='original/{page_id}.png'`；`tests/fea11/test_source_lineage_run.py:122-131` 的 `_StubImages` 返回固定全零帧、不读取/校验图像内容。L10 的「混合页旧图坐标潜在风险」与「后续接 C-17 §7.2 rendition 的判别测试要求」均有明确文字。 |
| **R3-02** prepared-snapshot digest 一次性 `RUN_STALE_PREVIEW` | P3 | **已登记（核销）** | L11①（line 137）写明「`lineage_hidden_regions` 进入 page target metadata 后会影响 prepared-snapshot digest，已 prepared 的 Run 可能一次性得到 `RUN_STALE_PREVIEW`（安全、可重预览）」。独立核实：`pipeline.py:1462-1468` 把 `lineage_hidden_regions` 写入 `TargetSnapshot.metadata`；`store.py:65-69` 的 `prepared_quartet` 含 `requestedTargets=[target.snapshot …]`；`snapshot_value` 递归 dataclass 字段（`store.py:46-56`），`TargetSnapshot.metadata` 是 dataclass 字段（`domain/tasks/models.py:233`）；`service.py:477-479` 在 accept 时 digest 不等即 `RUN_STALE_PREVIEW`。事实成立。 |
| **R3-03** `_backfill_detected_regions` 对 `LINEAGE_*` 静默 skip | P3 | **已登记（核销）** | L11②（line 137）写明「对 `LINEAGE_*` 码按『不可读跳过』处理（当前无 stderr 计数），建议后续补诊断计数」。独立核实：`tasks/service.py:1455-1474` 的 `except PipelineError` 在码属于 `{TARGET_DELETED, TARGET_NOT_FOUND, LINEAGE_BINDING_CHANGED, LINEAGE_UNVERIFIED}` 时直接 `continue`，无 log/print/计数；其他码 `raise`。事实成立。 |
| **R3-04** 卡面残留 r2 文本/旧行号/新测试文件未入 allowed_paths | P3 | **部分核销（剩 P3-1）** | ①`tests/fea11/test_source_lineage_run.py` 已在 frontmatter allowed_paths（line 43，注明「r3 新增；r3 Review P3 补登」）；②`90a8c8218` 尾部 line 153（请求 Lead 指派 r2 reviewer）与 line 154（交付 head 旧文本）已删除；③**但 `90a8c8218` line 152 的 r2 门禁（62/3073）被原样保留为 `f11bff37e` line 155**，未加 r2 标签，且紧接在 r3 门禁 line 152 之后；④line 74「更正 line 56…」旧行号引用未改，但处置节已声明「历史行号引用以 r3 Report/本卡滚动内容为准」，可接受。 |
| **R3-05** gates 日志瑕疵/check 警告数差异 | P3 | **已记录（核销）** | 处置节 line 166 记录「gates-r3.log gate1 缺 `-p no:cacheprovider`；check 警告数差异属并发文档环境，closeout 记录实测值」。独立核实：`verification/FEA-11-LINEAGE-1/logs/gates-r3.log:15` 的 gate1 命令为 `pytest tests/fea11 -q -p no:warnings --tb=no`（确无 `-p no:cacheprovider`）；本轮 check 默认与 `-TaskPath` 均 `PASS (2 warnings)`，与 r3 的 3/2 差异可由并发文档环境解释。 |

## AC 判定

| AC | 判定 | 实体证据 |
|---|---|---|
| **AC1** 同事务 native lineage（B1/R1→B2、same_content、changed 切断有测试） | **MET（维持）** | 本轮 `pytest tests/fea11` **69 passed, EXIT 0**；collect 列出 `test_every_user_single_revision_write_path_registers_native_lineage`、`test_reorder_batch_registers_native_lineage`、`test_add_revision_writes_the_requested_lineage`、`test_draft_apply_registers_native_lineage`、`test_run_region_candidate_registers_native_lineage`、`test_failed_revision_transaction_leaves_no_orphan_lineage`、`test_same_content_chain_is_readable_multi_hop`、`test_changed_cut_hides_and_refuses_typed`。 |
| **AC2** ListRegions/渲染/导出/Run/编辑入口读守卫（typed 拒绝/等价放行/过滤计数） | **MET（按原文；限定见 L1/L10）** | collect 列出 `test_mixed_library_scope_matrix_is_diagnosable`、`test_single_region_rerender_refuses_a_changed_binding_typed`、`test_single_region_rerender_refuses_unverified_typed`、`test_page_render_active_regions_excludes_hidden_with_reason`、`test_wire_faces_refuse_a_changed_binding_typed`、`test_run_entry_refuses_a_changed_binding_region_typed`、`test_reorder_and_merge_refuse_hidden_coordinates_with_zero_write`、`test_draft_apply_on_cut_binding_refused_typed_with_zero_write`、`test_missing_lineage_row_is_typed_unverified`、`test_legacy_unverified_row_is_not_coordinate_evidence`、`test_corrupt_lineage_region_attribution_is_unverified`。AC2 原文未要求「真实 referenced 图源 page-scope Run 的新图检测」，该缺口由 L1/L10 显式登记，不构成 AC2 与 limitation 的矛盾。 |
| **AC3** AC11-5 旧坐标对新图不可见 + 回归 | **MET（维持）** | `test_page_scope_reocr_all_filters_hidden_region_and_detects_new_image`（`test_source_lineage_run.py:224-282`）断言 hidden `rg1` 不复用、hidden 零 revision/lineage、新 region 以 `native` 记入当前 binding；`test_page_scope_rerender_all_on_empty_visible_set_is_a_clean_noop`（`:285-307`）干净终态；cut 拒绝面见 AC2 测试。 |

- `delivery_head` / `canonical_evidence_status`：卡面 frontmatter 仍为 `null` / `pending`，line 154 与 line 169 均注明「按集成生命周期由 Lead closeout 填写」——**已注明**，符合 closeout 前状态。
- `<<MET>>` 标记与 limitation 一致性：L1（执行链限定）不与 AC1/AC3 冲突；L10（真实图源不可达）不与 AC2 原文冲突；无其它 `<<MET>>` 过度声明。

## 独立复跑（只读；日志仓外 `review-r4\`）

| 门禁 | 命令 | 实测 | 证据 |
|---|---|---|---|
| 范围（docs-only） | `git diff --name-only 4a63c781a..f11bff37e` | `doc/TASK_LEDGER.md`、`doc/reviews/FEA-11-LINEAGE-1-r3.md`、`doc/tasks/FEA-11-LINEAGE-1.md`（3 个 docs；TASK_LEDGER 由 Lead 维护，属生命周期同步） | 本报告 |
| 代码零 diff | `git diff --name-only 90a8c8218..f11bff37e -- src tests 'apps/**'` | **空**，EXIT 0 | 本报告 |
| fea11 | `C:/Python314/python.exe -m pytest tests/fea11 -q -p no:warnings -p no:cacheprovider --tb=no` | **69 passed**，EXIT 0（1.81s） | `gate1-fea11.log` |
| governance | `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS (2 warnings)**，EXIT 0 | `gate2-check.log` |
| governance（本卡） | `… check.ps1 -TaskPath doc/tasks/FEA-11-LINEAGE-1.md` | **PASS (2 warnings)**，EXIT 0 | `gate3-check-task.log` |
| pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PIN AUDIT: PASS (all 18)**，EXIT 0 | `gate4-pins.log` |
| 测试清单 | `… -m pytest tests/fea11 --collect-only -q` | **69 tests collected**，EXIT 0 | `gate5-collect.log` |
| EV-2 hash | `Get-FileHash verification/FEA-11-LINEAGE-1/logs/gates-r3.log -Algorithm SHA256` | `729ED81EDF28F5F618146C7E8517BAFCD8B8B56C84AC870B097CD8DD2FA5D4AD`，与卡面一致 | 本报告 |
| 全量 pytest | 引用 r3 独立复跑：`pytest tests` **3093 passed / 10 skipped**（r3 `gate2-full.log`） | **未重跑**：①`90a8c8218..f11bff37e` 的 `src/tests/apps` 为空，Python 代码与测试零变化；②fea11 69 已本轮独立复跑；③全量约 253s 且 r3 记录其会写 tracked `verification/FEA-09` 副作用；派发指令允许引用 r3 结果。结论对 `f11bff37e` 有效。 | 引用 r3 报告 |
| .NET | **NOT_RUN**（同 r3）：本卡 Python-only，r3/f11bff37e 的 `apps/**` 零 diff；.NET 属 Host 侧 L6 集成限制。 | — | 本报告 |

**工作树/并发隔离**：复核开始（16:04）与 fea11/check/pins 复跑结束时 `git status --porcelain` 均干净，HEAD 始终 `f11bff37e`；`verification/FEA-09/logs/wire-redacted.ndjson` 复核前后 sha256 均为 `548DE629…D593`（本轮 fea11 未产生该副作用）。报告撰写完成时（约 16:09）工作树出现并发 Agent 的未提交改动：`M doc/tasks/FEA-12-PREREQ-1.md`、`?? doc/reviews/FEA-12-PREREQ-1-r2.md`——属 FEA-12-PREREQ-1 的 r2 处置，**非本 Reviewer 写入**，与本卡无关。`90a8c8218..f11bff37e` 整体包含的 FEA-12-DSIM-1 docs/verification 提交（`144683876`、`4a63c781a`）不计入本卡；其 `doc/contracts/M2-C1…` 变更属 `26775dfef`/`08b359251`（FEA-12-PREREQ-1），非本卡。

## 范围 / 冻结 / 诚实性核对

- **allowed_paths**：r3 四 commit（`d8ed04e13`/`6c0ab6594`/`280bb7bd0`/`90a8c8218`）与本轮 `f11bff37e` 的改动文件全部落在卡面 allowed_paths 内（含 r3 窄批 `providers/handlers.py`、`tasks/service.py`，`tests/fea11/**`，`verification/FEA-11-LINEAGE-1/**`，`doc/reviews/FEA-11-LINEAGE-1-*.md`）。`f11bff37e` 另改 `doc/TASK_LEDGER.md`——该文件由 Lead 维护、卡面 line 59 明确不计入本卡 allowed_paths，属生命周期同步，**不构成越界**。
- **冻结**：`f11bff37e` docs-only，未触 C-17/ADJ-001/FEA-01 字节；`90a8c8218..f11bff37e` 的契约变更均属 FEA-12 并发提交；无 schema/migrator/依赖变更；`pins 18/18` PASS。
- **未 push**：`git status -sb` 显示 `## main`（无 upstream 跟踪），无远端推送证据。
- **诚实性**：Report 与卡面引用的事实（行号、hash、数字）经独立复核一致；唯一偏差是 R3-04 处置声明与残留行不完全对应（P3-1，见下）。Reviewer 未引用聊天记录作为事实。

## 处置准确性备注（P3-1，不阻断）

- **P3-1（政策/卡面卫生）**：`f11bff37e` 的 R3-04 处置声明称「删除本卡尾部残留的 r2 门禁/自审段落」，实际删除的是 `90a8c8218` line 153-154（r2 reviewer 请求、旧交付 head 文本）；`90a8c8218` line 152 的 r2 门禁数字（`pytest tests/fea11` 62 passed / `pytest tests` 3073 passed / 10 skipped）仍保留为 `f11bff37e` line 155，位于 r3 门禁行（line 152；69/3093）之后且无 r2 标签。建议在 closeout 时标注「r2 历史门禁（62/3073，r2 head 791cfef28）」或删除该行，避免后续读者误读当前门禁数字。另 `f11bff37e` line 169 与 line 154 重复「本实现者不自审…」句，属同一 cosmetic 类，可一并清理。
- **判定**：该 P3 不涉及代码、测试、AC 或数据安全，不改判 changes_requested；建议 closeout 顺手处理，不要求另开返修轮。

## done / closeout 意见

- **同意转 approved 并进入 closeout**。R3-01 的过度声明已由 L1 限定 + L10 登记 + 矩阵行修正消除；R3-02/R3-03 已如实登记且与代码事实一致；R3-05 已记录；R3-04 仅剩 r2 门禁残留的 cosmetic 项（P3-1）。
- closeout 时由 Lead 填写 `delivery_head`（建议 `f11bff37e`，如 closeout 再有 docs 提交则以最终 head 为准）与 `canonical_evidence_status`；建议在 closeout 一并清理 P3-1 并对 `verification/FEA-11-LINEAGE-1/` 的 EV 行记录最终实测门禁（fea11 69、check 2 warnings、pins 18/18）。
- 本轮结论可支撑卡面 `status` 进入 done（最终以 Lead 集成验证为准）；无代码/测试返修要求。

## 自审声明

- 独立上下文 fresh subagent（DSH 派发，session `dde30402-06b5-43e7-ae1d-374408e55823`，父会话 `session-8db9dae5-49df-4d09-ac62-696f0805a95c`），未参与 FEA-11-LINEAGE-1 的任何实现、返修或 r1/r2/r3 处置；只读复核。
- 未 commit/push/stash/reset/checkout；未修改仓库任何文件；测试后仓库内无本 Reviewer 产生的改动（fea11/check/pins 复跑结束时 `git status` 干净；报告完成时出现的 `doc/tasks/FEA-12-PREREQ-1.md` / `doc/reviews/FEA-12-PREREQ-1-r2.md` 改动为并发 Agent 的 FEA-12 工作，非本 Reviewer 写入）。所有日志与报告写在仓外 `G:\CODEX\New Manga.workspace\FEA-11\review-r4\`；测试仅用 `:memory:`/pytest `tmp_path`，未触碰真实用户数据、AppData、外部卷或回收站。
- 复核开始时 HEAD 已是 `f11bff37e`，全程未变化；未把其他任务的并发提交计入本卡结论。

---

**decision: approved（P0=0 / P1=0 / P2=0 / P3=1）**——R3-01 已消除过度声明（L1 限定 + L10 + 矩阵修正，独立核实 `pipeline.py:1433-1434`/`core_assembly.py:351-428`/测试混合构造均准确）；R3-02/R3-03 已登记 L11①/② 且与代码事实一致；R3-05 已记录且日志事实成立；R3-04 仅剩任务卡 line 155 的 r2 门禁残留（cosmetic P3，建议 closeout 清理）。独立复跑 `pytest tests/fea11` 69 passed、check 默认/本卡 PASS (2 warnings)、pins 18/18 PASS、`90a8c8218..f11bff37e` 的 `src/tests/apps` 零 diff、`4a63c781a..f11bff37e` docs-only；全量 pytest 引用 r3 的 3093/10（本轮无代码/测试 diff，未重跑），.NET NOT_RUN（Python-only，apps 零 diff）。**可转 approved 并进入 closeout。**
