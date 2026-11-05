---
task_id: FEA-12-CORE
reviewer: dsh-fea12-core-r2 (fresh subagent; session 113ad38d-f601-4e30-b2c7-0721a95ae384)
reviewer_kind: subagent
review_session_id: 113ad38d-f601-4e30-b2c7-0721a95ae384
parent_agent_id: session-8db9dae5-49df-4d09-ac62-696f0805a95c
base_commit: e47fd47e
reviewed_head: 3da210518
decision: approved
---

# Review r2：FEA-12-CORE（r1 changes_requested 处置复审）

> 审查身份：独立上下文 fresh subagent，未参与 FEA-12-CORE 的实现、r1/r2 返修、分片设计或任务卡编写；会话 `113ad38d-f601-4e30-b2c7-0721a95ae384`，父会话 `session-8db9dae5-49df-4d09-ac62-696f0805a95c`。
> 审查范围：`base_commit=e47fd47e` → `reviewed_head=3da210518`；重点复核 r1 findings（R-001–R-012）处置与 r2 新增代码/测试/证据/卡面，并做独立复跑与变异反证。
> 审查方式：只读仓库；全部日志、探针、变异实验与报告写在仓外 `G:\CODEX\New Manga.workspace\FEA-12\review-core-r2\`；未 commit/stash/push，未改仓库文件。审查期间运行仓库探针曾生成 `verification/FEA-12-CORE/scripts/__pycache__`（ignored），已删除；最终 `git status --porcelain` 为空。

## 0. 结论摘要

**P0=0，P1=0，P2=0；新增 P3（含文档/证据精度）=10，均不阻断。decision: approved，可进入 closeout。**

r1 的 3 个 P2（R-001 派生文件披露、R-002/AC11 定稿、R-003 范围窄批）与 9 个 P3 全部有实际处置；其中实现类修复均经独立复跑与变异实验验证不是"测试空转"：

- **R-001 真实修复且判别成立**：`_derived_cleanup_entries` 用与 `cleanup_book_files` 相同的 catalog 查询（`preview_resource_ids_for_artifacts` + `page-original-<page_id>` + `catalog.lookup`）计算派生文件，按绝对路径与 managed 清单去重后计入 `deletedFiles/deletedBytes`；catalog 读失败在 preview/single/batch delete 三条路径均映射 `BOOK_DELETE_PROTECTION_INVENTORY_UNAVAILABLE`（我用真实 catalog 注入失败实测，零副作用）。golden 向量含 derived 记录（`deletedFiles=3/deletedBytes=46`，其中 derived 14B），我复跑探针与仓库证据 JSON 逐键一致（除 `computedAt`）。变异"去掉派生计入"→对应测试精确失败（1==2），证明测试判别真实。
- **R-008/R-009/R-010/R-011/R-012 均有直接判别测试**：混合 live+retry 批次集合级只形状校验、存活目标逐书强校验（失配→STALE 零副作用；正确→retry 成功）；R-009 竞态注入实测落在 `execute_permanent_delete_db` 写边界（非 preflight），顶层 `BOOK_BUSY` + items 归因；R-010 直接构造"目标外 binding.previous→目标 binding"图并预检 CONFLICT；R-011 已钉 `== "rr1"`；R-012 批量 partial cleanup→显式 retry→幂等重放有跨状态断言。
- **R-004/R-005/R-007** 已按裁决落地：isolation 探针 `Path.is_relative_to` 且纳入 `pass`、`DRIVE_PATH` 实际扫描；计数口径 CORE +51 / DSIM-1 +8（DSIM 21−13=8 已核）；`Book.restore()` 真正接线（domain 产生值 + guarded UPDATE）并有 domain 单测。
- **独立复跑**：相关组 **1104 passed**、全量 **3152 passed / 10 skipped**、定向 10 passed、`check.ps1 -TaskPath` **PASS (3 warnings)**、全量 check **PASS (3 warnings)**、pins **18/18**；均与 r2 宣称一致。
- **范围/冻结干净**：r2 自有 diff 仅 allowed_paths；18 pinned 契约、C-17 schema/migrator/connection、依赖、`apps/**`、`verification/FEA-09/**` 零 diff；origin/main 不含 reviewed head（未 push）；工作树 clean。

**AC4 判定：可恢复 MET**（r2 证据已满足；卡面仍 PARTIAL 属"待 Lead 定稿"，不是证据缺口）。**AC11：维持 MET**（B 证据 pin 可解析、r2 零 .NET 改动）。

## 1. 审查对象与 HEAD

- 开始审查：`HEAD=3da210518`（与 reviewed_head 一致），`git status` clean。
- r2 自有 commit：`60dd4d563`（源码 2 + 测试 3 + `verification/FEA-12-CORE/**` 22 文件）→ `3da210518`（任务卡 + Handoff）。二者父提交为 `f0df59610`（r1 Review 定稿）。
- `85db8354f..3da210518` 区间还含 Lead 的 `388f5476e`（集成证据/证据表）、`6b985c14b`（r1 处置：卡、r1 Review 落盘、allowed_paths 窄批、TASK_LEDGER）、`f0df59610`（r1 Review 最终版）；这些不是 r2 实现者的自有改动，故范围核对以 `60dd4d563^..3da210518` 为准，另对整段做了冻结/依赖/`apps` 扫描。
- `origin/main=b1c1f5a5...`，`git branch -r --contains 3da210518` 为空；本地领先 910 个提交，未发现 push。

## 2. r1 findings 核销表

| r1 ID | 级别 | r2 处置 | 独立核实结果 | 核销 |
|---|---|---|---|---|
| **R-001** 派生文件漏披露 | P2 | `core_service.py` 新增 `_derived_cleanup_entries`，`_finalize_delete_inventory` 计入派生文件/字节并按绝对路径去重；catalog 读失败不吞；golden 增 derived 记录；测试 2 条 | 代码与 `cleanup_book_files` 查询同源（preview ids + page-original ids + `lookup`；page_ids 取法一致）；实际删除测试证明披露=删除；catalog 注入失败 → preview 与 delete 均 `INVENTORY_UNAVAILABLE` 且 books/文件保留；golden 复跑逐键一致；变异 A 精确失败 | **核销** |
| **R-002** AC11 未定稿 | P2 | Lead 在 r1 处置中定稿 AC11 MET；B 证据留在表中 | AC11 卡面 `<<MET>>`；B 证据文件在 pin commit `fc7125586` 可解析；r2 对 `apps/**` 零 diff | **核销（Lead）** |
| **R-003** allowed_paths 缺 `tests/core/test_core_service.py` | P2 | Lead 补登 allowed_paths；Handoff 改为"Lead r1 处置时补登" | 当前 allowed_paths 已含该路径；r2 未再改该文件；Handoff 表述已更正 | **核销（Lead）** |
| **R-004** 隔离探针自相矛盾/死代码 | P3 | `Path(core.data_root).is_relative_to(WORK_ROOT.resolve())` 并纳入 `runtime["pass"]`；`DRIVE_PATH` 扫描删除模块+证据脚本并纳入 static pass；重生成 evidence | evidence JSON：`data_root_under_workspace_temp=true`、`drive_path_hits=[]`、`drive_path_files_scanned=6`、`pass=true`；我外部复跑静态段与 pass 完全一致 | **核销** |
| **R-005** 计数口径/protection 计数 | P3 | 卡/记录/Handoff 改「CORE +51 / DSIM-1 +8」；gates log protection 改 11（policy 子集 8 + wire/隔离 3） | DSIM 21−13=8；相关组 1104=1096+8；全量 3152=3093+59=3093+51+8；protection 文件实测 11。**但 gates log 的 purge 计数写 11，实际 collected 10**（见 P3-N2） | **核销（含 1 处残余计数）** |
| **R-006** 测试要求表/指针 | P3 | Lead closeout 项 | 测试表仍 `NOT_RUN`；`integration_commit`/`delivery_head`/`canonical_evidence_status` 仍 null/pending，卡内已注明 closeout 填写（:144、:149、:169） | **转 closeout（Lead）** |
| **R-007** `Book.restore` 未接线 | P3 | `restore_book_from_trash` 读行→`Book.restore()`→`deleted_at IS NOT NULL` guarded UPDATE；补 domain 单测 | 适配器已实际调用 domain 方法；单测钉住"只清 marker + bump updated_at、其余字段不变"；AC2 全表快照测试仍通过；`utc_now` 时间格式与原 SQL 一致（毫秒 ISO） | **核销** |
| **R-008** 混合 retry 集合级 digest | P3 | 明确限定：存在 retry 目标时只跳集合级；逐书对存活目标强校验；记录 §2.8/记录 AC5 写明；补测试 | 代码 `if not retry_ids` 仅跳过集合级；测试 (a) live 失配→STALE、b2 归因、零副作用；(b) 正确 digest→retry 成功、b1 cleanup manifest 清除。记录未扩大为"两级全部跳过" | **核销（限定语义）** |
| **R-009** 批量写边界错误码 | P3 | `PermanentDeleteBlockedError` 携带 `book_id`；批量顶层 `caught.code`、items 归因具体 book；补竞态测试 | 我用调用点探针确认注入点确为 `execute_permanent_delete_db`（call#5，非 preflight），响应顶层 `BOOK_BUSY`、b1 归因、b2 None、books 未删；变异 C 复原旧码→测试精确失败 | **核销** |
| **R-010** previous_binding 预检盲点 | P3 | `has_unsafe_source_references` 第 5 条：目标外 `page_bindings.previous_binding_id` 指向目标 binding → CONFLICT；补直接构造测试 | 查询参数正确；测试直接插入 bind-1(p1/b1) + bind-2(p2/b2, previous=bind-1)，断言 `has_unsafe...True` 与删除 CONFLICT、books/bindings 不变；变异 B 移除该检查→测试精确失败（`False is True`） | **核销** |
| **R-011** currentRevisionId 弱断言 | P3 | 改 `== "rr1"` | 当前断言已钉住；隐藏 region 测试保留 | **核销** |
| **R-012** 批量 cleanup/retry 无测试 | P3 | 新增 2 条批量测试（partial cleanup→BATCH_CLEANUP_PENDING→显式 retry→幂等重放；混合 live+retry 三态 items） | 测试覆盖逐项 `deleted/cleanup_pending/not_started`、只带 pending ID 重试、不重跑预览、二次重放 `BOOK_NOT_FOUND` 零副作用；断言与代码语义一致 | **核销** |

## 3. AC4 / AC11 判定

### AC4 只读预览：**可恢复 MET（证据已满足）**

- 披露完整性：`deletedFiles/deletedBytes` = managed 清理清单 + catalog preview/page-original 派生文件；派生文件正是 `cleanup_book_files` 会 unlink 的两个家族，查询与删除路径同源；`_finalize` 的派生路径与 managed 路径均 `normcase(abspath(...))` 后去重。
- 只读性：`_derived_cleanup_entries` 只做 catalog `SELECT`；既有 `test_preview_is_read_only` 断言全表快照、文件树指纹、`library.db` mtime 不变（派生读取不写 catalog）。
- 失败语义：catalog 读失败（我注入 `catalog.lookup` 抛错）→ preview/single/batch delete 均 `BOOK_DELETE_PROTECTION_INVENTORY_UNAVAILABLE`（retryable，零副作用），不静默少报；代码在 `_finalize` 与三处 handler try/except 中如实传播。
- golden：`derived_disclosure`（3 files / 46 bytes / derived 14B）与 `single-book-full-protection` 向量一致；外部复跑 `all_match=true` 且除 `computedAt` 外与仓库 JSON 完全相同。
- 结论：AC4 的 r1 阻断点已消除；卡面 `<<PARTIAL...待 Lead 定稿>>` 是流程状态而非证据缺陷。closeout 时可改 `[x] <<MET>>`。

### AC11 Host 命令桥：**MET（维持 Lead 定稿）**

- 卡面已 `<<MET>>`；B 侧 4 条证据 pin `fc7125586` 均可解析且文件存在；r2 对 `apps/**`、csproj/sln 零 diff；集成日志（head=85db）记录 .NET 1405/0/80。r2 无 .NET 变更，不需要重跑即可维持。

## 4. 独立复跑（仓外日志）

| 场景 | 命令 | 结果 | 日志 |
|---|---|---|---|
| 相关组 | `C:/Python314/python.exe -m pytest tests/core tests/storage tests/maintenance tests/fea12 -q -p no:warnings -p no:cacheprovider --tb=no` | **1104 passed**，EXIT 0，77.86s | `pytest-related.log` |
| 全量 pytest | `... -m pytest tests -q -p no:warnings -p no:cacheprovider --tb=no` | **3152 passed / 10 skipped**，EXIT 0，227.00s | `pytest-full.log` |
| 关键定向 | R-001×2、R-008、R-009、R-010、R-011、R-012×2、`Book.restore`、`INVENTORY_UNAVAILABLE` | **10 passed**，EXIT 0 | `pytest-targeted.log` |
| 任务 check | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-12-CORE.md` | **PASS (3 warnings)**：非终态 Task/STATUS 80%/PLAN 80% | `check-task-2.log` |
| 全量 check | `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS (3 warnings)** | `check-all.log` |
| pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PASS (all 18)**，EXIT 0 | `verify-pins.log` |
| golden 探针 | 外部加载仓库 `core_py_inventory_digest.py`（EVIDENCE/WORK_ROOT 重定向到仓外） | `all_match: true`，EXIT 0；JSON 与仓库证据逐键一致 | `probes.log`、`review-digest-golden.json` |
| isolation 探针 | 同上，`core_py_isolation_scan.py` | `pass: true`，EXIT 0；static 段与仓库一致，`data_root_under_workspace_temp=true`、`drive_path_hits=[]` | `probes.log`、`review-isolation-scan.json` |
| 仓库测试文件计数 | `--collect-only` | delete 33 / preview 11 / trash 15 / protection 11 / purge **10** / DSIM 21 | 见 §2 R-005 |
| 全量 .NET | **NOT_RUN**（理由见下） | 引用 Lead 集成 head=85db 的 **1405 passed / 0 failed / 80 skipped**（`gates-integration.log` 逐程序集可加总：21+38+253+117+107+31+167+671=1405，skip 49+24+7=80）；r1 已在 85db 独立复跑同数字 | `gates-integration.log` |

**未重跑全量 .NET 的理由**：r2 自有 diff 与 `85db..3da` 整段的 `apps/**`、`*.csproj/*.sln` 均为空，依赖文件零 diff；.NET 门禁的测试对象在 r2 未变化；r1 已在该 head 独立复跑 1405/0/80。重跑不会增加对本卡 r2 改动的判别力，且会重写 `verification/FEA-09` 证据（需额外恢复），故按任务允许的"引用 + 说明"处理。

## 5. 变异/反证（仓外 r2 源码副本，未改仓库）

副本：`G:\CODEX\New Manga.workspace\FEA-12\review-core-r2\mutation-r2\`（`git archive 3da210518 src tests ...` 解包）；每个变异后恢复原文件。

| 变异 | 预期 | 实测 |
|---|---|---|
| **A**：`_derived_cleanup_entries` 直接 `return []`（去掉派生计入） | R-001 计数测试失败 | **FAILED** `test_preview_counts_catalog_derived_files_and_delete_removes_them`，断言 `assert 1 == 2`（`deletedFiles` 少计 derived） |
| **B**：删除 `has_unsafe_source_references` 第 5 条检查 | R-010 判别测试失败 | **FAILED** `test_delete_book_unsafe_binding_previous_reference_conflicts`，断言 `has_unsafe_source_references("b1") is True` → `AssertionError: assert False is True` |
| **C**：R-009 回退为 `BOOK_DELETE_BATCH_PREFLIGHT_FAILED` + items None | R-009 竞态测试失败 | **FAILED** `test_delete_books_write_boundary_race_projects_busy_item`，断言 `'BOOK_DELETE_BATCH_PREFLIGHT_FAILED' == 'BOOK_BUSY'` |

补充反证（非仓库测试）：

- **R-009 注入点真实**：外部探针显示 `list_book_source_busy_operation_ids` 第 5 次调用栈为 `_dispatch_request → handle_permanently_delete_books → execute_permanent_delete_db`，即预检之后、事务写边界，不是 preflight 重入（`probe-r009-callsites.log`）。
- **R-001 catalog 失败映射真实**：真实 `ResourceCatalogStore` 的 `lookup` 注入 `RuntimeError` 后，preview 与 delete 均返回 `BOOK_DELETE_PROTECTION_INVENTORY_UNAVAILABLE`，books=1、managed 文件保留（`catalog-failure-probe.log`）。该行为目前**没有仓库内测试直接覆盖**（见 P3-N8），但行为本身已独立确认。

## 6. 范围 / 冻结 / 纪律核对

| 项 | 结果 |
|---|---|
| r2 自有 commits（`60dd4d563^..3da210518`）文件 | 2 src（core_service.py、sqlite/library.py）、3 tests（delete/preview/trash）、`verification/FEA-12-CORE/**`、卡、Handoff；**全部在 allowed_paths**（`tests/core/test_core_service.py` 本 r2 未改，Lead 已补登） |
| `git show --stat 60dd4d563` | 27 files / +809 −169；无 allowed_paths 外文件 |
| 18 pinned 契约 / `doc/contracts` / FEA-01 | `git diff --name-only 60dd^..3da` 与 `85db..3da` 均空；`verify_pins.ps1` 18/18 |
| C-17 schema/migrator/connection | 零 diff |
| 依赖/构建（pyproject、requirements、csproj/sln/props/targets、package.json） | 零 diff；无新依赖 |
| `apps/**`、`verification/FEA-09/**` | 零 diff（r2 零 .NET） |
| 新 schema/migration | 无（仅文档/测试/源码逻辑） |
| push | 未 push：`origin/main=b1c1f5a5...` 不含 3da；无远程分支包含 |
| 工作树 | 审查结束 `git status --porcelain` 为空（`tracked-dirty-count=0`）；我自建的探针 pycache 已清理 |
| 真实数据/回收站 | 全部测试与探针在 `tmp_path` / `G:\CODEX\New Manga.workspace\temp\` 隔离根；未触碰真实 AppData/外部卷/Windows 回收站 |

## 7. 残余风险与新增 P3（均不阻断）

**P0/P1/P2：0。**

| ID | 级别 | 项 | 最小返修/关闭动作 |
|---|---|---|---|
| N-1 | P3 | 卡面 `:113`、`:167` 写 "check PASS (4 warnings)"，实际与证据日志（`core-py-check.log`）及我的复跑均为 **3 warnings**（第 4 条是 85db 时 B 证据未登记的旧告警） | closeout 时改 3 warnings（或注明历史值） |
| N-2 | P3 | `gates-core-py.log:48` 写 `test_purge_integrity.py 11`，实际 collected **10**；`G9` 写 "tests 4 文件"，r2 实际改 3 个测试文件 | 改 10、改 3 文件（或注明包含 r1 交付） |
| N-3 | P3 | 卡面 `:7`/`:141` 仍写 r1 "P3=8"，r1 最终为 **P3=9**（含 R-012）；`:148` 的 R-005 计划（CORE +43）与 `:159` 的 r2 结果（CORE +51）易混淆 | 改 P3=9；给 R-005 加"r1 时 43，r2 后 51"一句 |
| N-4 | P3 | 任务卡 AC5（`:74`）仍只写"集合级与逐书两级校验"，未内联 R-008 的 retry 限定；限定已写在记录 §2.8/记录 AC 表 | closeout 在 AC5 后加"（混合 live+retry 时集合级仅形状校验，见 R-008）" |
| N-5 | P3 | `EV-FEA12CORE-A-HANDOFF` pin `60dd4d563`，但 Handoff 终稿在 `3da210518` 才定稿（其余 A 证据文件在 60dd 后未变） | 二选一：pin 改 `3da210518`，或注明"evidence commit，文档终稿见 3da" |
| N-6 | P3 | `doc/TASK_LEDGER.md:42` 仍为 `changes_requested`，与卡面 `in_review` 不一致；卡面 `reviewer:` 仍只记 r1 session | Lead closeout 时同步 ledger/status 并登记 r2 reviewer/session |
| N-7 | P3 | Handoff `:47` "19→3 files/46 bytes 场景"数字疑为笔误（实际 3 files/46 bytes） | 改为 "3 files/46 bytes" |
| N-8 | P3 | **测试缺口**：仓库内没有直接测试"catalog 读失败 → `BOOK_DELETE_PROTECTION_INVENTORY_UNAVAILABLE`"；`test_preview_inventory_unavailable_is_typed` 注入的是 `book_delete_inventory`，不是派生 catalog 读取 | 建议补 1 条（把 `catalog.lookup`/`preview_resource_ids_for_artifacts` 置为抛错，断言 UNAVAILABLE + 零副作用）；我已在仓外探针确认行为正确 |
| N-9 | P3 | **测试缺口**：R-001 的"与 managed 绝对路径去重"与 `preview-<uuid>` 家族披露未被直接断言（测试覆盖了 page-original 家族与计数/字节） | 可选：补一个去重/预览家族的断言，或在记录中注明覆盖边界 |
| N-10 | P3 | `_derived_cleanup_entries` 复制了 `_collect_delete_targets` 的查询组合而非共享 helper，未来 cleanup 查询变更时有漂移风险 | 可选：抽共享 helper 或在记录中注明"两处需同步"（当前语义已核对同源） |

## 8. done vs closed_with_limitations 意见

- **建议 `done`**：r1 的全部 P2/P3 阻断/提升项已处置；r2 仅剩文档精度与两个测试覆盖 P3（N-8/N-9），不改变行为、不涉及数据安全；R-008 的"混合 retry 集合级仅形状校验"是 Lead 裁决的 PD-07 限定语义，属于**已登记的契约限定**，不是新 limitation（保留在卡/记录中即可）。
- closeout 前置（Lead，最小清单）：
  1. AC4 改 `[x] <<MET>>`（本 Review 判定证据已满足），AC11 维持 MET；
  2. 填 `delivery_head=3da210518`（或 closeout 时最终 head）、`integration_commit`、`canonical_evidence_status`；
  3. R-006：把"测试要求"表 `NOT_RUN` 改为实跑结果/证据路径；
  4. 按 N-1/N-2/N-3/N-4/N-5/N-6/N-7 做文档/证据数字与 ledger 同步；
  5. （可选）补 N-8 的 catalog 失败判别测试；不需要返修代码。

## 9. 自审声明

- 我未参与 FEA-12-CORE 的实现、r1/r2 返修、分片设计或任务卡编写；本会话为新启动的独立上下文子 agent。
- 只读仓库：未修改、未 commit、未 stash/reset/checkout、未 push；未写入任何仓库文件。运行仓库探针产生的 `verification/FEA-12-CORE/scripts/__pycache__`（ignored）已删除，最终 tracked 工作树 clean；变异实验在仓外 `git archive` 副本中进行。
- 未触碰真实用户数据、AppData、外部卷或真实 Windows 回收站；全部测试/探针使用 `tmp_path` 或 `G:\CODEX\New Manga.workspace\temp\` 隔离根。
- 所有日志/探针/报告位于 `G:\CODEX\New Manga.workspace\FEA-12\review-core-r2\`；结论基于 Git 对象、文件原文、实际 pytest/check/pins/探针/变异输出，不基于聊天记录。

## 最终决定

**decision: approved（P0=0，P1=0，P2=0；新增 P3=10，均不阻断）。**

r1 的 R-001（派生披露）已按冻结语义真实修复并有判别测试、golden 与 catalog 失败映射证据；R-004/R-007/R-008/R-009/R-010/R-011/R-012 均已核销；R-002/R-003 由 Lead 处置完毕，AC11 维持 MET。独立复跑（相关组 1104、全量 3152/10、check PASS 3 warnings、pins 18/18、两个探针 all_match/pass、3 个判别变异）与 r2 宣称一致，范围/冻结/纪律干净。**可 approved 并进入 closeout**；closeout 仅需 Lead 定稿 AC4、填指针/证据表与少量文档计数修正（N-1…N-7），可选补 N-8/N-9 两个测试覆盖。
