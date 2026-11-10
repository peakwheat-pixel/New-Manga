---
task_id: FEA-14-EDIT-1
reviewer: 独立子 agent（lead 会话 session-408d4e24-3789-4111-acde-983899601dad 派发；全新上下文，未参与实现或返修；只读）
reviewer_kind: subagent
author: dsh
base_commit: 68a9e2e748953c13ed49431b30ca6b0c151cc65c
reviewed_head: 54b87dcc94b5f64c1dc4f4ffddf45dc5f66009ac
decision: approved
---

# Review：FEA-14-EDIT-1（r2 独立复核）

## 0. 审查对象与环境

- 仓库 `G:\CODEX\New Manga`，分支 `main`，主工作树（无 linked worktree）。审查者由 lead 会话 `session-408d4e24-3789-4111-acde-983899601dad` 派发，为**全新上下文子 agent**，未参与本卡实现、测试、证据生成或 r1 返修。
- **被审 head = `54b87dcc94b5f64c1dc4f4ffddf45dc5f66009ac`**，仅回填任务卡 5 个 Canonical Evidence 的 `commit` 单元格（5 行 `-`→`4635ab306`，无其他字节）。
- 提交链（`git log --oneline` 实测）：`9a968c3e4`（初版实现）→ `f803416b7`（初版证据）→ `8b2977209`（初版证据 pin 回填，r1 被审 head）→ `a89b3421c`（r1 处置）→ `4635ab306`（r1 处置证据）→ `54b87dcc9`（r1 处置证据 pin 回填，HEAD）。
- **diff 基线 = `68a9e2e74`**（卡面 `base_commit`；LIB-1 收口 + EDIT-1 冻结）。`git diff 68a9e2e74..HEAD`：**32 文件 / +1654 / −89**；其中 `68a9e2e74..8b2977209` = 31 文件 / +1477 / −85（r1 审查范围），HEAD 多出 r1 报告与 r1 处置/重证据。
- 审查窗口：**2026-11-10 17:32:48 – 17:41 +08:00**。开始（17:32:48）、门禁后（17:36:29 / 17:38:11）、写报告前（17:40:00）`git rev-parse HEAD` 均为 `54b87dcc9`，`git status --porcelain` 均 **clean（0 行）**；写报告后复核见 §8（仅本报告自身为新增未跟踪文件）。
- 只读纪律：仓库内唯一写入为本报告；探针脚本、隔离数据库与本轮复跑日志全部位于 `C:\Users\49745\AppData\Local\Temp\FEA14-EDIT1-review-r2\` 与 `%TEMP%\fea14edit1-r2-*`；未写真实 `%APPDATA%`，未 commit、未 push，未改源码/测试/契约/卡面/证据。
- 本报告只对 `54b87dcc94b5f64c1dc4f4ffddf45dc5f66009ac` 的字节有效；head 变化即自动失效。

## 1. 结论

**`approved`**（**P0=0 / P1=0 / P2=0 / P3=1**）。

r1 的 **F-01（P2）已真正关闭**：C-07「S5 计划追加」节表格只剩 P21–P25 五行，标题/正文/统计与表格一致；正式成员表逐行等于 `generate_api_inventory.py` stdout（74 方法 + 4 非方法）；新 pin `89781583…` 与文件 SHA-256、FROZEN §1/§1B/§2#3/§3/§5、UNFREEZE 载体、README、卡面全部自洽；18 pins 中仅 C-07 变化。**F-02–F-05 亦逐项关闭**（F-05 按 limitation 登记接受）。r1 已通过的产品面（schema v13、v1–v12 迁移字节、P16–P20 wire、Host 六处签名、NullHost 降级）**未被 r1 处置提交破坏**：`9a968c3e4..HEAD` 对 `src/`、`apps/desktop-avalonia/src/`、`tools/` 的 diff 为**空**，r1 处置只改了 Fake/测试与文档。

AC 独立判定：**AC1–AC6 全部 MET**（r1 的 AC5 PARTIAL 已转为 MET），NOT_RUN 登记诚实。

## 2. Findings 关闭核对

### 2.1 F-01–F-05 逐项关闭表

| ID | r1 级别 | r2 状态 | 本次实测依据 |
|---|---|---|---|
| **F-01** | P2（阻断） | **CLOSED** | 自写解析器（`probe_c07.py`）：①「S5 计划追加」节表格 **5 行**，id = `['P21','P22','P23','P24','P25']`，无 P16/P17/P18 计划行（节内提及 P16–P20 仅存在于「已落地」叙述文字）；②标题「剩余 P21–P25 尚未实现」、正文「P1–P20 已落地，本节只保留 AI-1 P21–P25」、统计「25 条（4/4/7/5/5）；已落地 20、剩余 5；目标 74+5=79、三接口 86」与 5 行表格一致；③正式成员表与 stdout **85 行全量有序相等**（`doc == stdout: True`；IReaderProgressSink 1、IHostController 74 方法 + 4 非方法、IRunController 6）；④`Get-FileHash` = `89781583964eb81db0e12974fdd03adc44231461ac3b2fad65f0eacdb74261c6` = FROZEN §1 pin；⑤FROZEN §1（v1.7 新 pin + v1.6 前一 pin 保留）、§1B（v1.7 待 r2）、§2 条件 3（`1/74/6=81`）、§3（已落地 20，剩 AI-1 5）、§5 v1.7 行均与新 pin 自洽；载体 `CONTRACT-UNFREEZE-2026-11-10-EDIT1.md:12` 新 pin 行自洽并注明初值 `bb775912…` 仅历史；⑥`generate_api_inventory.py --check` 17:39:40 **EXIT 0**；`verify_pins` **18/18**；⑦18 个 pinned blob 的 base→HEAD 比对**仅 C07 变化**；⑧r1 指出的 P17 计划返回类型冲突随残留行删除消失（正式表 `Task<string?>`）。 |
| **F-02** | P3 | **CLOSED** | `doc/REBASELINE_PLAN.md:50` 节点行 = `in_review`；`:55` 当前活动行 = `in_review`（原 `ready` 已改）；`:56` `READY 节点：无`；`doc/STATUS.md:7` = `in_review`；`doc/TASK_LEDGER.md` 同步为 `in_review` 3 / `ready` 1（EDIT-1 从 ready 行移入 in_review 行）。EDIT-1 无 `ready` 残留。 |
| **F-03** | P3 | **CLOSED** | `FakeHostController.cs`：新增 `_issueMarkerBooks` 记录每 marker 的 bookId（`:303`），`CreateIssueMarkerAsync` 写入归属（`:328`），`Delete` 移除归属（`:348`）；`ListIssueMarkersAsync` 先按 `owner == bookId` 过滤、再按 `effectiveState = state ?? "open"` 过滤（`:308-317`），与 Core `IssueMarkerService._normalize_state(None) → OPEN`（`issue_markers.py:130-132`）及仓储按 `book_id` 查询一致；新增 `FakeHost_ListFiltersByBookAndDefaultsToOpen`（`IssueMarkerPortTests.cs:84-100`，覆盖跨书过滤、未知书为空、显式 null 默认 open、resolved 过滤）；全量 App.Tests **883 passed / 0 failed**（含该测试）；`git grep IssueMarkers` 确认无其他测试直接向 `IssueMarkers` 列表注入 marker 而绕过归属字典。 |
| **F-04** | P3 | **CLOSED** | `tests/storage/test_issue_markers.py:76-90`：升级前对 `books`/`chapters`/`pages` 三表做 `SELECT * ORDER BY rowid` 的**行级快照**（`rows_before`），升级 v13 后逐表比较 `actual == expected`，并保留 chapter.title 断言与 `issue_markers` 空表断言；README `:12` 表述与测试一致（“对 v12 真实 books/chapters/pages 逐行快照比较”）。该测试在本轮定向门禁中通过（5 passed 含此文件）。 |
| **F-05** | P3 | **CLOSED（登记接受）** | limitation 已在卡面「实现说明」`:98` 与 `verification/FEA-14-EDIT-1/README.md:44` 登记：`issue_markers` 无外键、book 永久删除事务不清理 marker 行（与 v10 `reading_bookmarks` 先例一致）；代码核对 `library.py:1936-1968` 永久删除确实未含 `issue_markers`，`SqliteIssueMarkerStore.book_exists` 用 `deleted_at IS NULL` 守卫（`:82-86`），孤儿行不会在 UI 复现。属已知 limitation，不阻断本卡，留给后续删除/清理卡。 |

### 2.2 r1 已通过项无回退核对

| r1 通过项 | r2 核对 | 结论 |
|---|---|---|
| 产品源码（schema/服务/wire/Host 六处/NullHost/Client） | `git diff --stat 9a968c3e4..HEAD -- src apps/desktop-avalonia/src tools` → **空输出**；r1 处置提交 `a89b3421c` 仅触及 `FakeHostController.cs`、`IssueMarkerPortTests.cs`、`tests/storage/test_issue_markers.py` 与文档（C-07/FROZEN/载体/PLAN/卡面/r1 报告） | **无回退** |
| schema v13 表/CHECK/索引 | `schema.py` diff 仅新增 `SCHEMA_VERSION_V13`、`MIGRATION_V13_*` 与 `default_migrations()` 末项；独立 SQLite 探针：半对、x<0、y>1、空 kind、非法 state、NULL state、空 marker_id、NULL created_at **全部 REJECTED**；整页与 `(0.0,1.0)` **ACCEPTED**；两索引 `idx_issue_markers_book_state`/`idx_issue_markers_page` 存在 | **PASS** |
| v1–v12 迁移字节不变 | 分别从 `68a9e2e74:` 与 HEAD 加载 `schema.py` 模块，`MIGRATION_V1..V12_{NAME,SQL}` 全等（`MISMATCHES: NONE`）；迁移序列 `[1..13]` | **PASS** |
| P16–P20 wire 形状/typed/幂等/物理删 | 提交的 `test_issue_marker_wire.py` 2 测试 + `test_issue_markers.py` 3 测试 **5 passed**；独立探针经真实 `CoreServiceServer.dispatch_request`：`state` 为 `""`/`"OPEN"`/`1`/`true` → `INVALID_REQUEST`，缺省/`null` → open；position 半对/越界/bool/字符串/多余键/数组 → `INVALID_REQUEST`，`(0.0,1.0)` 接受；书/章/页归属错误 → `TARGET_NOT_FOUND`；resolve 三次 `resolved_at` 稳定不变（探针）；reopen 清空 `resolved_at` 由 storage 测试断言；delete 前后全表计数**仅 `issue_markers` −1**、二次 delete → `TARGET_NOT_FOUND` | **PASS** |
| Host 六处 5 方法签名 | 提取 `IHostController` 与 `HostController`/`NullHostController`/`HostRuntime`/`CoreServiceClient`/`FakeHostController` 五方法：参数文本逐字一致（5 实现之间 5/5 相同；与接口声明相同；返回类型相同，`async` 修饰符差异属实现修饰）；`HostController` 分别路由 Resolve/Reopen/Delete，`CoreServiceClient` 命令名分别为 `ListIssueMarkers`/`CreateIssueMarker`/`ResolveIssueMarker`/`ReopenIssueMarker`/`DeleteIssueMarker` | **PASS** |
| NullHost 降级 | `IssueMarkerPortTests` 5 个 Fact 全部随全量 App.Tests 通过（883 passed）；NullHost 返回空列表/null/false 不抛 | **PASS** |
| 门禁/回归 | 1258 passed（storage+core+fea09+fea11）、883 passed / 0 failed / 11 skipped、`check.ps1` 默认与 `-TaskPath` PASS、pins 18/18 | **PASS** |

## 3. AC 逐项判定

| AC | 判定 | 依据（本次实测/核对） |
|---|---|---|
| **AC1 数据面/v13** | **MET** | `schema.py` 仅 additive 新增 v13 表 + 两索引；v1–v12 NAME/SQL 模块级全等；v13 CHECK 反例全部被 SQLite 拒绝；`tests/storage/test_issue_markers.py` 的 v12→v13 行级快照测试通过；repository insert/get/list/update/delete 路径由 3 个 storage 测试覆盖并通过。 |
| **AC2 P16 列表** | **MET** | `test_issue_marker_wire.py` 断言默认列表仅 open、键集无 `book_id`、`position` 仅位置 marker、`resolved_at` 仅 resolved、排序 = `(created_at, marker_id)`；独立探针补齐空串/大小写/非字符串 state → `INVALID_REQUEST`，未知书 → `TARGET_NOT_FOUND`；未知键拒绝由提交测试覆盖。 |
| **AC3 P17 新建** | **MET** | 归属（书/章/页）与 position 成对 0–1、kind 非空/≤64 由独立探针与提交测试覆盖；note 类型/2000 长度上限为代码核对（`issue_markers.py:65-68`），未单独实测；成功返回非空 `marker_id`、`state=open`、`created_at` 有值（storage 测试断言）。 |
| **AC4 P18–P20 状态/删除** | **MET** | resolve 幂等：探针连续三次调用后 `resolved_at` 稳定不变；reopen 清空 `resolved_at`（storage 测试断言）；重复 reopen 返回成功且不再写（代码核对）；delete 只影响 marker 行（全表计数 diff = `{'issue_markers': (2,1)}`），二次 delete typed `TARGET_NOT_FOUND`；响应键 `{resolved:true}`/`{reopened:true}`/`{deleted:true}`（探针）。 |
| **AC5 契约/门禁** | **MET** | 正式成员表 85 行 == stdout（74 方法 + 4 非方法 + 1 + 6）；S5 节仅 P21–P25；pin `89781583…` = `Get-FileHash`；`--check` EXIT 0；`verify_pins` 18/18；FROZEN §1/§1B/§2#3/§3/§5 与载体自洽。r1 的 PARTIAL 原因已消除。 |
| **AC6 证据** | **MET** | 4 日志头均 `HEAD=a89b3421c626b8ee08842c1ebc3447a2d7996d9d`（dirty：dotnet/pytest `[]`；regression `[M dotnet, M pytest]`；pins `[M dotnet, M pytest, M regression]`，与同批顺序生成一致）；计数 5 / 1258 / 883(0 failed/11 skipped/894 total) / 18 + API 74-81 与本轮复跑一致；5 份 Canonical sha256 与工作树 5/5 匹配；`git ls-tree 4635ab306` 含 5 文件且 blob 与工作树逐一相等；卡面 5 行 commit = `4635ab306`；`54b87dcc9` 仅改 5 个 `commit` 单元格；README NOT_RUN 如实。 |

## 4. 必查项判定

| # | 必查项 | 判定 | 依据 |
|---|---|---|---|
| 1 | 迁移字节 v1–v12 不变 | **PASS** | base/HEAD 模块逐属性比对 `MISMATCHES: NONE`；diff 仅追加 v13。 |
| 2 | C-07 逐行 = stdout、pin、S5 只剩 P21–P25、FROZEN/载体自洽 | **PASS** | 自写解析器 85 行全量相等；S5 5 行；hash = pin；`--check` 0；pins 18/18。 |
| 3 | Fake 保真（按书过滤 + null=open） | **PASS** | 代码 + 新测试 + 全量 883 passed；未发现绕过归属字典的测试注入。 |
| 4 | 证据 provenance（HEAD/dirty/计数/哈希/tree/commit pin） | **PASS** | 4 日志头 = `a89b3421c`；计数与复跑一致；5/5 sha256；tree blob 相等；卡面 commit pin = `4635ab306`；HEAD 仅改 5 单元格。 |
| 5 | allowed_paths | **PASS** | 自写 fnmatch：`changed=32`，`OUTSIDE=NONE`（29 条 allowed_paths；r1 报告命中 `doc/reviews/FEA-14-EDIT-1-*.md`，证据/测试/源码均在白名单）。 |
| 6 | 契约字节范围 / 18 pins | **PASS** | `doc/contracts` 零 diff；base→HEAD 的 18 个 pinned blob **仅 C07** 变化；其余 17 项与 base 逐字节相同；`verify_pins` 18/18。 |
| 7 | 扫新 P0/P1/P2（r1 处置是否引入新问题） | **P0=0 / P1=0 / P2=0** | C-07 删除仅 P16–P18 三行、未误删 AI 行（P21–P25 完整）；pin 链可追溯（FROZEN 保留 v1.6 原值、§5 记录初值 `bb775912…`→`89781583…`，载体注明初值仅历史）；Fake/测试改动未触产品；阅读/回归/签名无回退。 |
| 8 | AC 独立判定 / NOT_RUN 诚实 | **PASS** | AC1–AC6 均有本轮实测或可复现证据；NOT_RUN 覆盖真实 IPC/UI/批量/性能/FEA-15，未见把未跑项写成 PASS。 |

## 5. 门禁与测试（本次审查实测）

| # | 命令/检查 | 时点（+08:00） | 结果 | EXIT |
|---|---|---|---|---|
| 1 | `python -m pytest tests/storage/test_issue_markers.py tests/core/test_issue_marker_wire.py -q` | 17:33:39–17:33:41 | **5 passed** in 1.03s | **0** |
| 2 | `python -m pytest tests/storage tests/core tests/fea09/test_v7_migration.py tests/fea11/test_source_gate_unify.py -q` | 17:33:05–17:34:47 | **1258 passed, 1 warning** in 101.25s | **0** |
| 3 | `dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj --nologo` | 17:33:05–17:37:58（测试执行 4m44s） | **883 passed / 0 failed / 11 skipped / 894 total** | **0** |
| 4 | `pwsh -NoProfile -File tools/governance/check.ps1` | 17:33:42 | **PASS**（3 warnings：11 非终态 / STATUS 3168 B·31 L / PLAN 6954 B·63 L） | **0** |
| 5 | `... check.ps1 -TaskPath doc/tasks/FEA-14-EDIT-1.md` | 17:33:44 | **PASS**（同上 3 warnings） | **0** |
| 6 | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 17:33:41 | `PIN AUDIT: PASS (all 18)`；`OK C07 89781583964e` | **0** |
| 7 | `python tools/generate_api_inventory.py --check` | 17:39:40 | `OK: rendered counts match FEA-C07 doc`；`1/74/6 = 81` | **0** |
| 8 | `Get-FileHash doc/plan/FEA-C07_API_INVENTORY.md -Algorithm SHA256` | 17:39:40 | `89781583964EB81DB0E12974FDD03ADC44231461AC3B2FAD65F0EACDB74261C6`（= pin） | — |
| 9 | C-07 表 vs stdout 解析器（自写，`probe_c07.py`） | 17:33 前后 | `doc rows 85 == stdout rows 85: True`；S5 ids `[P21..P25]` | 0 |
| 10 | schema/迁移探针（base vs HEAD 模块；v13 CHECK/索引） | 17:35–17:36 | `v1-v12 mismatches: NONE`；版本 `[1..13]`；CHECK 反例全拒、合法成对接受 | 0 |
| 11 | wire 探针（真实 `CoreServiceServer`，隔离数据根） | 17:36 | 见 §2.2/§3；typed/幂等/删除范围全部符合 | 0 |
| 12 | Host 签名提取器（接口 + 5 实现） | 17:37 | 参数 5/5 一致，与接口一致；命令路由无错映射 | 0 |
| 13 | allowed_paths + 18 pins 脚本（`probe_scope.py`） | 17:35 | `changed=32`，`OUTSIDE=NONE`；`pinned changed: ['C07']` | 0 |
| 14 | Canonical 5 份 SHA-256 + `4635ab306` tree/blob 比对 | 17:35 | 5/5 匹配；tree 5 文件 blob == 工作树 | — |
| 15 | 4 日志头/计数/EXIT 核对 | 17:35 | HEAD=`a89b3421c`；5 / 1258 / 883-0-11 / pins 18 + API 74-81 | — |
| 16 | `check.ps1`（写报告后复跑，默认 + `-TaskPath`） | 17:40:43–17:40:46 | **PASS**（同上 3 warnings）；报告新增未改变治理结论 | **0** |

> 本地复跑日志：`%TEMP%\FEA14-EDIT1-review-r2\gate1.log`、`gate2.log`、`gate3-dotnet.log`、`gate5.log`；探针脚本 `probe_c07.py`、`probe_scope.py`、`probe_check.py`、`probe_wire.py`；均未入库。

## 6. NOT_RUN（如实登记，不得记 PASS）

- **真实 Host↔Core 进程级 IPC**：`CoreServiceClient` 的 5 个新方法未对活 Core 调用；C# 端口测试覆盖 NullHost 降级与 Fake 记录/状态机/按书过滤，**不覆盖真实 IPC 读写映射**（README `:52` 已登记）。
- EDIT 可见 UI：标记列表、新建标记、页面定位渲染、kind 选择器 = NOT_RUN（EDIT-2/EDIT-3/UI 卡）。
- 批量 resolve/delete、列表分页/跨书聚合/时间过滤 = NOT_RUN（PREQ 未纳入）。
- 标记与翻译/渲染管线联动（EDIT-3 受控样式重渲染）= NOT_RUN。
- 万级标记/大库迁移性能、真实 `%APPDATA%` 数据、备份/恢复对 `issue_markers` 的端到端演练 = NOT_RUN。
- C# 客户端对畸形 Core 响应（`position` 半对象、`markers` 非数组、`resolved_at` 非字符串）的解析 = 仅代码核对，未运行。
- `position` 在双页/旋转/缩放 UI 中的坐标映射 = NOT_RUN（UI 未实现）。
- 并发场景（同一 marker 并发 resolve/delete）未演练；Core 单进程顺序调用假设未验证。
- FEA-15 正式验收声明未审。
- `HostCommandRegistry` 是否应登记 `editing_*` 未审（P1–P15 同类未登记，沿用既有直连模式）。
- v13 迁移的“真实用户大库”只以测试构造库验证；未使用真实 `%APPDATA%` 库。

## 7. 处置建议

1. **可进入收口**：本报告 `approved`，P0/P1/P2=0；C-07 v1.7 的字节（pin `89781583…`）可作为重冻依据。建议 lead 在 closeout 时把 FROZEN §1B、§2 条件 1/3、§5 的 v1.7 行更新为“EDIT-1 r2 approved（`doc/reviews/FEA-14-EDIT-1-r2.md`，被审 head `54b87dcc9`）”，并按治理流程更新卡面 `status`/`canonical_evidence_status`/`delivery_head`。
2. **P3（accepted，可随手修）**：`doc/tasks/FEA-14-EDIT-1.md:136` 的 Closeout Record 仍写「r1 独立复核待派发」，与已完成的 r1（`changes_requested`）和本次 r2 不符；建议在 closeout 一并改为「r1 changes_requested → r1 处置 → r2 approved」。不影响 AC/产品，不要求返修或重审。
3. **F-05 limitation 继续跟踪**：`issue_markers` 不参与 book 永久删除清理；建议在后续删除/清理卡补 `DELETE FROM issue_markers WHERE book_id = ?` 或按页/章清理并补回归测试；本卡不阻断。
4. **不 push、不关闭 Task**：reviewer 不执行 commit/push；是否 push 由 lead 按门禁与授权决定。approved 仅代表对本报告所审 `54b87dcc9` 字节的独立审查结论，不替代集成验证。
5. 真实 IPC/UI/批量/性能等 NOT_RUN 项按既有计划留给 EDIT-2/EDIT-3/UI/验收卡，不因本卡 approved 而被视为已覆盖。

## 8. 审查者声明

本报告由 lead 会话 `session-408d4e24-3789-4111-acde-983899601dad` 派发的**全新上下文子 agent**出具；审查者未参与 FEA-14-EDIT-1 的实现、测试、证据生成或 r1 返修，审查期间只读。唯一仓库写入为本报告；探针脚本、隔离数据库与本轮复跑日志全部在 `C:\Users\49745\AppData\Local\Temp\FEA14-EDIT1-review-r2\` 与 `%TEMP%\fea14edit1-r2-*`，未写真实 `%APPDATA%`，未 commit/push。PASS 仅基于本次 2026-11-10 17:32–17:41 的实测、脚本逐行比对与代码核对；未执行项已在 §6 记 NOT_RUN，未把未实测项写成 PASS。写报告后复核：`git rev-parse HEAD` = `54b87dcc94b5f64c1dc4f4ffddf45dc5f66009ac`（未变），`git status --porcelain` 仅 `?? doc/reviews/FEA-14-EDIT-1-r2.md`（本报告）；`check.ps1` 复跑 PASS。本报告只对 `54b87dcc94b5f64c1dc4f4ffddf45dc5f66009ac` 的字节有效；head 变化即自动失效。
