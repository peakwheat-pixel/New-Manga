---
task_id: FEA-14-EDIT-1
reviewer: 独立子 agent（lead 会话 session-408d4e24-3789-4111-acde-983899601dad 派发；全新上下文，未参与实现或返修；只读）
reviewer_kind: subagent
author: dsh
base_commit: 68a9e2e748953c13ed49431b30ca6b0c151cc65c
reviewed_head: 8b2977209c61dce310aac2173b212a5cd56aa34c
decision: changes_requested
---

# Review：FEA-14-EDIT-1（r1 独立复核）

## 0. 审查对象与环境

- 仓库 `G:\CODEX\New Manga`，分支 `main`，主工作树（无 linked worktree）。审查者由 lead 会话 `session-408d4e24-3789-4111-acde-983899601dad` 派发，为**全新上下文子 agent**，未参与本卡实现、测试或返修。
- **被审 head = `8b2977209c61dce310aac2173b212a5cd56aa34c`**（仅回填证据表 commit pin）。产品/文档提交 `9a968c3e4d2ec18f0a64e4b16067fe0813c574cc`（26 文件，+1305/−85）；证据提交 `f803416b77d1ddd87f65ad348c9373556b6e5762`（6 文件，+172）；head 提交 `8b2977209` 只改任务卡 5 个 `commit` 单元格。
- **diff 基线 = `68a9e2e748953c13ed49431b30ca6b0c151cc65c`**（release 提交 = LIB-1 收口 + EDIT-1 冻结；卡面 `base_commit` 即此值）。`git diff 68a9e2e74..HEAD` 共 **31 文件 / +1477 / −85**。
- 审查窗口：`2026-11-10 17:06–17:20 +08:00`。开始、写报告前（17:19:27）与写报告后 `git rev-parse HEAD` 均为 `8b2977209`；开始与写报告前 `git status --porcelain` 均 **clean（0 行）**。
- 只读纪律：仓库内唯一写入为本报告；探针脚本、隔离数据库与本地复跑日志全部位于 `C:\Users\49745\AppData\Local\Temp\FEA14-EDIT1-review\`；未写真实 `%APPDATA%`，未 commit、未 push，未改源码/测试/契约/卡面/证据。
- 本报告只对 `8b2977209c61dce310aac2173b212a5cd56aa34c` 的字节有效；head 变化即自动失效。

## 1. 结论

**`changes_requested`**（**P0=0 / P1=0 / P2=1 / P3=4**）。

产品面（schema v13 additive、数据面 CHECK/repository、P16–P20 wire、Host 六处、证据 provenance、allowed_paths）经本次独立实测**全部通过**；四道门禁全部 EXIT 0 且计数与证据表一致。唯一阻断项是 **F-01（P2，C-07 契约文档的「S5 计划追加」节仍保留 P16/P17/P18 三行已落地命令**，与同文件标题、同文件口径、冻结记录 §3/§5、UNFREEZE 载体、README 与卡面「实现说明」的「只剩 P21–P25」直接矛盾；且 P17 的计划返回类型仍是旧的 `Task<IssueMarkerInfo?>`，正式成员表已改为 `Task<string?>`）。该问题只需文档修正，但会触发 C-07 pin 重算与 FROZEN/载体/README/证据表的连锁更新，故不能按「已登记 P3」接受。

AC 独立判定：**AC1–AC4、AC6 MET；AC5 PARTIAL**（其四条第项均通过，但本卡交付的 C-07 文件 S5 节与多项「20/25 已落地」自述不实，见 §3）。

## 2. Findings

| ID | 级别 | 文件/行 | 问题 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| **F-01** | **P2** | `doc/plan/FEA-C07_API_INVENTORY.md:126,128,132-134,141`；`doc/plan/FEA-CONTRACT-FROZEN-C07.md:31,50,93`；`doc/reviews/CONTRACT-UNFREEZE-2026-11-10-EDIT1.md:9`；`verification/FEA-14-EDIT-1/README.md:28`；`doc/tasks/FEA-14-EDIT-1.md:97` | C-07「S5 计划追加」节标题写「剩余 P21–P25 尚未实现」，正文写「本节只保留尚未实现的 AI-1 P21–P25」，统计行写「已落地 20 条，剩余 5 条」，但表格仍列 **P16（ListIssueMarkers）/P17（CreateIssueMarker）/P18（ResolveIssueMarker）** 三行 EDIT-1 已落地命令（P19/P20 反被删除），合计 8 行；P17 计划返回类型 `Task<IssueMarkerInfo?>` 与正式成员表 `Task<string?>` 冲突。FROZEN §3/§5、UNFREEZE 载体第 3 条、README「S5 计划节仅剩 P21–P25」与卡面实现说明均沿用「只剩 P21–P25」的错误自述。`--check` 只比对计数行，无法发现该不一致。 | 自写解析器：正式表 74 方法 + 4 非方法 == `generate_api_inventory.py` stdout（`ALL_MATCH: True`）；同一解析器读 S5 节 id：`['P16','P17','P18','P21','P22','P23','P24','P25']`（期望 `P21..P25`）。`python tools/generate_api_inventory.py --check` EXIT 0（只打印 1/74/6=81 与计数表）。文件 hash 与 pin `bb775912…` 一致，说明错误已进入待冻结字节。 | 从 S5 表删除 P16/P17/P18 三行（保留 P21–P25），使标题/正文/统计/表格一致；重算 `FEA-C07_API_INVENTORY.md` SHA-256；同步 FROZEN §1 pin 与 §5 v1.7 行、UNFREEZE 载体「新 pin」行、README 的 pin/S5 表述、卡面实现说明及 Canonical Evidence 中受影响文件的 sha256（README 字节会变），再跑 `--check`/`verify_pins`/`check.ps1`；随后 r2 复核。 | open |
| **F-02** | P3 | `doc/REBASELINE_PLAN.md:55` | 「当前活动：`FEA-14-EDIT-1`（**ready**；v13 + P16–P20）」未随同文件 `:50` 的 `in_review`、`:56` 的「READY 节点：无」及 `doc/STATUS.md:7` 的 `in_review` 更新，同一文件内三种口径并存。 | 读文件逐行；`check.ps1` 未报错（该处不在其检查范围）。 | 将 `ready` 改为 `in_review`；无 pin 影响。 | open |
| **F-03** | P3 | `apps/desktop-avalonia/tests/NewManga.App.Tests/FakeHostController.cs:305-312`（过滤在 `:309`） | Fake 的 `ListIssueMarkersAsync` **不按 `bookId` 过滤**（`IssueMarkerInfo` 无 `bookId` 字段，fake 只在单一列表中过滤 state），且 `state is null` 返回**全部状态**；真实 Core 的 `_normalize_state(None)` 默认为 `open` 且按 `book_id` 查询。UI 测试若依赖 fake，会把「跨书标记」或「null 返回 resolved」的 bug 掩盖为通过。 | 代码逐行；Core 对照 `src/application/editing/issue_markers.py:130-138`、`src/infrastructure/sqlite/issue_markers.py:53-66`；`IssueMarkerPortTests.cs` 只覆盖单一 fake 列表与显式 state。 | 在 Fake 中为 marker 记录其 bookId（如 `Dictionary<string,(string BookId, IssueMarkerInfo Marker)>`）并按 `bookId` 过滤；`state == null` 时按 `open` 处理（或显式约定「null=全部」并让 Core/Fake 一致，但那会改产品语义，需另裁）。属测试保真度问题，不阻断产品。 | open |
| **F-04** | P3 | `tests/storage/test_issue_markers.py:57-83`（断言在 `:82`）；`verification/FEA-14-EDIT-1/README.md:12` | v12→v13 测试插入了 book/chapter/page 三行，但升级后只断言了 chapter.title（`:82`）和新表为空（`:83`），**未断言 book/page 行保留**；README 却写「插入真实书/章/页行、再升 v13 并断言行保留」，测试强度与自述不完全一致。我的独立探针已做全表逐行比对并证明产品行为正确（见 §4），故这是覆盖/表述问题而非产品缺陷。另 `tests/storage/test_fonts.py:50` 的 `read_schema_version(conn) == LATEST == 13` 随本卡把常量从 12 改为 13 后仍是指向自身上限的弱断言（既有模式，非本卡引入）。 | 读测试文件；独立探针 `probe_schema.py` 对 books/chapters/pages 的 `SELECT * ORDER BY rowid` 升级前后逐行比较为 `rows preserved: True`；`issue_markers count: 0`。 | 测试改为对三张表分别做行级比较（或至少断言 book/page 关键列与行数），README 与测试保持一致；`test_fonts.py` 可恢复为 `LATEST == 13` + 显式 v11 表/列断言（可选）。 | open |
| **F-05** | P3 | `src/infrastructure/sqlite/schema.py:939-957`；`src/infrastructure/sqlite/library.py:1959-1968` | `issue_markers` 无外键；书本永久删除路径删除 progress/regions/pages/chapters/books，但**不删除 issue_markers**。对已永久删除的书/页，marker 行会成为孤儿；因 `list_markers` 先要求 `book_exists`（`deleted_at IS NULL`），这些行不会在正常 UI 中重新出现，主要影响数据库残留与「彻底删除」语义完整性。该模式与 v10 `reading_bookmarks`（同样无 FK、同样未被该书删除路径清理）一致，属既有先例而非本卡独有。 | 代码逐行；`git grep` 确认 `library.py` 永久删除事务未包含 `issue_markers`/`reading_bookmarks`；`IssueMarkerService.list_markers` 的 `book_exists` 守卫。 | 在本卡 limitation 或后续删除/清理卡登记「marker 不参与 book 永久删除清理」；若产品要求“彻底删除即删净”，在 C-09 允许的删除事务中补 `DELETE FROM issue_markers WHERE book_id = ?`（或按页/章），并补回归测试。不阻断本卡。 | open |

### 2.1 观察项（不构成 finding，不改变结论）

1. `position` 形状裁决：PREQ §8 未定义 `position` 内部形状；实现选择 `{"x":number,"y":number}`（0–1 相对坐标、成对），只新增子键、未改 PREQ 键名/可选性，且已在卡面「裁决」与 README `:32` 记录。按 PREQ §8「请求/响应键形状为实现下限，实现卡可加可选键但不得改已有键名/语义」的口径，本裁决**不强制要求 PREQ errata**；若 DSH 希望把它升级为跨卡/UI 契约，建议在后续 PREQ errata 或 UI 卡显式引用该形状。
2. `state` 边界：wire 对缺省与显式 `null` 都按「默认 open」处理；空串、`"OPEN"`、整数、bool 均 `INVALID_REQUEST`。该选择与卡面「默认 open」一致，但显式 `null` 的语义未在卡面单独写明；当前无 UI 依赖，建议在 EDIT-2 文档中固定（null=缺省 vs null=全部）。
3. `IssueMarkerService.STATES`（`src/application/editing/issue_markers.py:29`）未被任何代码引用；属无害死代码，可在后续清理。
4. `CoreServiceClient.ReadIssueMarkerPosition` 用 `ReadDouble`（`:2401-2404`，缺键返回 0）读取 `x/y`；若未来 Core 返回半对象，客户端会静默得到 `(0, y)`。Core 当前保证成对，故不影响本卡。
5. Host command id：PREQ §8 的 `editing_*` 列未在 `HostCommandRegistry` 注册（P1–P15 的 S5 命令同样未注册）；P16–P20 沿用既有「IHostController 直连」模式，与已收口切片一致，不构成本卡 finding。
6. `CoreServiceClient.CreateIssueMarkerAsync` 的参数校验在缺 chapter/page/kind 时抛 `ArgumentException(..., nameof(bookId))`（`:1801-1804`），诊断信息指向 `bookId` 不够精确；同类既有方法也有此模式，建议后续统一。

## 3. AC 逐项判定

| AC | 判定 | 依据（本次实测，不采信自述） |
|---|---|---|
| **AC1 数据面/v13** | **MET** | 自写导入 base/head `schema.py` 模块：`MIGRATION_V1..V12_{NAME,SQL}` 全部字符串相等（`MISMATCHES: NONE`）；`SCHEMA_VERSION_V13=13`、`default_migrations()` 顺序 `[1..13]`；v13 仅新增 `issue_markers` 表 + `idx_issue_markers_book_state`/`idx_issue_markers_page`；v12 真实库（repository 写入 book/chapter/page）升级后三表 `SELECT * ORDER BY rowid` 逐行相等、`issue_markers` 0 行；直接 INSERT 反例（半对、x<0、y>1、kind 空、state 非枚举、state NULL、marker_id 空、created_at NULL）全部被 SQLite CHECK/NOT NULL 拒绝，合法 (0.0,1.0) 接受；repository insert/get/list(open/resolved)/update/delete 五路径实测一致。 |
| **AC2 P16 列表** | **MET** | `%TEMP%` 隔离库经真实 `CoreServiceServer.dispatch_request`：默认列表仅 open、键集 `{marker_id,chapter_id,page_id,kind,note,state,created_at}`（无 `book_id`，与 PREQ 一致）；位置标记多 `position:{x,y}`；`state="resolved"` 只回已解决且多 `resolved_at`；`""`/`"OPEN"`/int/bool/未知键/缺 `book_id` 均 `INVALID_REQUEST`；未知书 `TARGET_NOT_FOUND`；同毫秒双 marker 按 `(created_at, marker_id)` 稳定排序。 |
| **AC3 P17 新建** | **MET** | 缺书/章不属于书/页不属于章/页不存在均 `TARGET_NOT_FOUND`（另测「page 存在但属于另一 chapter」）；`position` 缺失/null 可整页，半对、空对象、`{x}`、多余 `z`、数组、字符串、bool、字符串坐标、±越界、`inf` 均 `INVALID_REQUEST`；`kind` 空/全空白/超 64 → `INVALID_REQUEST`；成功返回非空 `marker_id`，DB 读回 `state=open`、`created_at` 非空、position 落为 REAL。 |
| **AC4 P18–P20 状态/删除** | **MET** | resolve 连续三次 `resolved_at` 不变；reopen 清空 `resolved_at`，重复 reopen 不写；delete 前后对 `sqlite_master` 全表计数，仅 `issue_markers` −1，books/chapters/pages/reading_progress/reading_bookmarks/regions 等均不变；二次 delete → `TARGET_NOT_FOUND/not_found`；三命令响应分别为 `{resolved:true}`/`{reopened:true}`/`{deleted:true}`；参数多键/缺键/null/空串均 `INVALID_REQUEST`。 |
| **AC5 契约/门禁** | **PARTIAL** | 字面条目均通过：正式成员表 74 方法 + 4 非方法 == stdout（`ALL_MATCH: True`；`IHostController 74`、合计 81）；`Get-FileHash` = pin `bb77591266208b763c4d4478dd88e525c1b2ddd4934c2e3b1f05ccd3e4c1ef34`；`--check` EXIT 0；`verify_pins` 18/18。**但** C-07 的 S5 计划节仍列 P16–P18（F-01），与本卡实现说明/README/FROZEN/载体「只剩 P21–P25」的交付自述矛盾，且 P17 计划类型仍为旧值；故不能判全 MET。 |
| **AC6 证据** | **MET** | 4 日志头均 `HEAD=9a968c3e4d2ec18f0a64e4b16067fe0813c574cc` 并带 dirty（dotnet/pytest `[]`；regression/pins 见 `?? verification/FEA-14-EDIT-1/`）；计数 5/1258/882(0 failed/11 skipped)/18 + API 74-81 与本次复跑逐项一致；5 份 Canonical Evidence sha256 与工作树逐一匹配（5/5）；`git ls-tree -r f803416b7 -- verification/FEA-14-EDIT-1` 含 5 文件且 blob hash 与工作树相等；README NOT_RUN 章节如实（EDIT UI/批量/真实 IPC/管线/性能/FEA-15）。 |

## 4. 必查项判定

| # | 必查项 | 判定 | 依据 |
|---|---|---|---|
| 1 | schema v13 additive；v1–v12 字节不变；旧库升级行级无损 | **PASS** | 见 AC1；base/head 模块逐属性比对 + v12 真实行升级全表比对；`default_migrations()` 1..13。 |
| 2 | AC1 数据面：DB CHECK + repository 五路径 | **PASS** | 直接 INSERT 反例全部被拒；合法成对接受；repository 五路径一致。 |
| 3 | AC2 P16 wire 形状/默认/过滤/排序/无书 | **PASS** | 见 AC2；响应键集与 PREQ §8 逐键一致；`position`/`resolved_at` 均为条件出现。 |
| 4 | AC3 P17 wire 形状/错误/成功 | **PASS** | 见 AC3；`position` 形状裁决只细化内部形状、未改 PREQ 顶层键集；卡面/README 已记录（§2.1-1）。 |
| 5 | AC4 P18–P20 幂等/物理删/typed/响应键 | **PASS** | resolve 幂等时间戳稳定、reopen 清空；全表计数仅 marker 变化；未知 marker typed；响应键正确。 |
| 6 | Host 六处 5 方法签名逐字一致；NullHost 降级；Client 序列化/解析；三状态命令路由 | **PASS（真实 IPC=NOT_RUN）** | 自写签名提取器：`IHostController`/`HostController`/`NullHostController`/`HostRuntime`/`CoreServiceClient`/`FakeHostController` 五方法参数文本全部相等；`ListIssueMarkersAsync` 的 `state` 可选参数一致。NullHost 四测 + 四端口测试；`HostController` 分别路由 Resolve/Reopen/Delete（无 delete→reopen 错映射）；Client 写 `position` 为 `{x,y}` 对象、读缺失 position→null、缺失 `resolved_at`→null（代码核对）；真实 Host↔Core IPC 未跑（README 已登记 NOT_RUN）。 |
| 7 | C-07 逐行/pin；S5 只剩 P21–P25；FROZEN §1/§1B/§2/§3/§5 | **PARTIAL（F-01）** | 正式表 `ALL_MATCH: True`（74+4）、pin 匹配、`--check` 0、`verify_pins` 18/18；FROZEN §1 保留 v1.6 + v1.7、§1B 记 v1.7 待 r1、§2 条件 3 `1/74/6=81`、§3 已落地 20 均正确；但 S5 表多出 P16–P18，FROZEN §5/§3、载体 `:9`、README `:28` 的「只剩 P21–P25」为假，且 P17 计划类型旧。 |
| 8 | 契约字节：只有 C-07 inventory/FROZEN/新载体变化；其余 17 pins 不变 | **PASS** | 自写脚本比对 verify_pins 的 18 个 pinned blob（base vs HEAD）：**仅 C-07 变化**；`doc/contracts` 零 diff；`verify_pins` 18/18；C-07 hash 与 pin 一致。 |
| 9 | 证据 provenance：日志 HEAD/dirty/计数/哈希/commit tree | **PASS** | 见 AC6；日志头 HEAD=9a968c3e4；计数与本地复跑一致；5/5 sha256；f803416b7 tree 含 5 文件且 blob 相等；8b2977209 只改 5 个 commit 单元格。 |
| 10 | 范围：diff ⊆ allowed_paths；无 worktree 外产物 | **PASS** | 自写 fnmatch 脚本：`changed=31`，`OUTSIDE=NONE`；报告路径本身命中 `doc/reviews/FEA-14-EDIT-1-*.md`；diff 无仓外路径。 |
| 11 | AC 独立判定：全 MET 是否站得住；NOT_RUN 是否诚实 | **PARTIAL** | AC1–AC4/AC6 站得住；AC5 四字面条目通过但 S5 自述不实（F-01），不能判全 MET；NOT_RUN 章节诚实且覆盖真实 IPC/UI/批量/性能/FEA-15。 |
| 12 | 扫新 P0/P1/P2（无 FK、position、state 边界、Fake、迁移测试） | **P0=0 / P1=0 / P2=1 / P3=4** | 无产品 P0/P1；F-01 P2；P3 见 F-02..F-05；state null/空串与 position 形状为已记录的边界选择（§2.1）。 |

### 4.1 关键实测输出摘录

- schema 探针：`MISMATCHES: NONE (V1..V12 exact match)`；`versions: [1..13]`；`rows preserved: True`；`issue_markers count: 0`；CHECK 反例均 `REJECTED`，合法成对 `ACCEPTED`。
- wire 探针：默认列表键集无 `book_id`、无 `resolved_at`；位置 marker 含 `position:{"x":0.0,"y":1.0}`；`state=null` 与缺省均回 2 条 open；`state=""`/`"OPEN"`/`1`/`true` → `INVALID_REQUEST`；未知书 → `TARGET_NOT_FOUND`；resolve 三次 `resolved_at` 恒为 `2026-11-10T09:08:54.271+00:00`；delete 后全表计数仅 marker−1。
- Host 签名比对：五方法六处 `all equal to IHostController: True`；状态命令路由分别为 `ResolveIssueMarkerAsync`/`ReopenIssueMarkerAsync`/`DeleteIssueMarkerAsync`。
- C-07 比对：`stdout interface counts {'IReaderProgressSink':1,'IHostController':74,'IRunController':6}`，`non-method 4`，`ALL_MATCH: True`；S5 行 `P16,P17,P18,P21..P25`。
- 范围：`changed=31`，`OUTSIDE=NONE`；pinned blob 仅 C-07 `changed=True`。

## 5. 门禁与测试（本次审查实测）

| # | 命令/检查 | 时点（+08:00） | 结果 | EXIT |
|---|---|---|---|---|
| 1 | `python -m pytest tests/storage/test_issue_markers.py tests/core/test_issue_marker_wire.py -q` | 17:09:03 起 | **5 passed** in 0.96s | **0** |
| 2 | `python -m pytest tests/storage tests/core tests/fea09/test_v7_migration.py tests/fea11/test_source_gate_unify.py -q` | 17:09:09–17:11:08 | **1258 passed, 1 warning** in 118.79s | **0** |
| 3 | `dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj --nologo` | 17:09:05–17:14:29（测试执行 5m24s） | **882 passed / 0 failed / 11 skipped / 893 total** | **0** |
| 4 | `pwsh -NoProfile -File tools/governance/check.ps1` | 17:09:32–17:09:33 | **PASS**（3 warnings：11 非终态 / STATUS 3168 B·31 L / PLAN 6950 B·63 L） | **0** |
| 5 | `... check.ps1 -TaskPath doc/tasks/FEA-14-EDIT-1.md` | 17:16:32–17:16:33 | **PASS**（同上 3 warnings） | **0** |
| 6 | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 17:09:31–17:09:32 | `PIN AUDIT: PASS (all 18)`；`OK C07 bb7759126620` | **0** |
| 7 | `python tools/generate_api_inventory.py --check` | 17:16:31 | `OK: rendered counts match FEA-C07 doc`；1/74/6 = 81 | **0** |
| 8 | `Get-FileHash doc/plan/FEA-C07_API_INVENTORY.md -Algorithm SHA256` | 17:16:31 | `BB77591266208B763C4D4478DD88E525C1B2DDD4934C2E3B1F05CCD3E4C1EF34`（= pin） | — |
| 9 | 迁移/schema 探针（base vs head 模块；v12→v13；DB CHECK；repository） | 17:07–17:08 | 见 §4.1；全部符合 AC1 | 0 |
| 10 | wire 探针（真实 `CoreServiceServer`，隔离数据根） | 17:08–17:09 | P16–P20 形状/typed/幂等/删除范围全部符合 | 0 |
| 11 | Host 签名提取器（六文件五方法） | 17:10 前后 | `all equal to IHostController: True` | 0 |
| 12 | C-07 表 vs stdout 解析器 | 17:10 前后 | `ALL_MATCH: True`；S5 多出 P16–P18（F-01） | 0 |
| 13 | allowed_paths 逐路径脚本 | 17:10 前后 | `changed=31`，`OUTSIDE=NONE` | 0 |
| 14 | Canonical 5 份 SHA-256 + f803416b7 tree/blob 比对 | 17:11 前后 | 5/5 匹配；5 文件均在 tree 且 blob 相等 | — |
| 15 | 18 pins 的 base/HEAD blob 比对 | 17:12 前后 | 仅 C-07 变化 | — |
| 16 | `check.ps1`（写报告后复跑） | 17:20:48 | **PASS**（同上 3 warnings）；确认报告新增未改变治理检查结论 | **0** |

> 本地复跑日志在 `%TEMP%\FEA14-EDIT1-review\`（`pytest-edit-local.log`、`pytest-regression-local.log`、`dotnet-app-tests-local.log`），未入库；卡面 4 个 Canonical 日志仅用于 provenance 核对，未替代本次运行。

## 6. NOT_RUN（如实登记，不得记 PASS）

- **真实 Host↔Core 进程级 IPC**：5 个新 `CoreServiceClient` 方法未对活 Core 调用；C# 4 个端口测试只覆盖 NullHost 降级与 Fake 记录/状态机，**不覆盖真实 IPC 读写映射**（README `:43` 已登记）。
- EDIT 可见 UI：标记列表、位置标记的页面定位渲染、kind 选择器、新建/解决/重开/删除交互 = NOT_RUN（EDIT-2/EDIT-3/UI 卡）。
- 批量 resolve/delete 与列表分页/跨书聚合/时间过滤 = NOT_RUN（PREQ 未纳入）。
- 标记与翻译/渲染管线联动（EDIT-3 受控样式重渲染）= NOT_RUN。
- 万级标记/大库迁移性能、真实 `%APPDATA%` 数据、备份/恢复对 `issue_markers` 的端到端演练 = NOT_RUN。
- C# 客户端对畸形 Core 响应（`position` 半对象、`markers` 非数组、`resolved_at` 非字符串）的解析 = 未运行，仅代码核对。
- `position` 在双页/旋转/缩放 UI 中的坐标映射 = NOT_RUN（UI 未实现）。
- 并发场景（同一 marker 并发 resolve/delete）未演练；Core 单进程顺序调用假设未验证。
- FEA-15 正式验收声明未审。
- `HostCommandRegistry` 是否应登记 `editing_*` 未审（P1–P15 同类未登记，见 §2.1-5）。

## 7. 处置建议

1. **先修 F-01（阻断）**：从 C-07 S5 表删除 P16/P17/P18 三行，保留 P21–P25；确认标题/正文/统计一致后重算 C-07 SHA-256；同步 FROZEN §1 pin 与 §5、UNFREEZE 载体新 pin、README（pin 与 S5 表述）、卡面实现说明/AC5 与 Canonical Evidence 中 README 的 sha256；重跑 `--check`、`verify_pins`、`check.ps1`（默认 + `-TaskPath`）并更新证据提交与卡面 commit pin；随后 r2 复核。
2. **P3 可选但建议一并处理**：F-02（REBASELINE_PLAN 一处 `ready`→`in_review`）；F-03（Fake 按书过滤 + null 默认 open）；F-04（v13 迁移测试断言 book/page 行、README 口径对齐）；F-05（在 limitation 或删除卡登记 marker 清理，或补删除事务）。
3. **不要求产品返修**：本次未发现 P0/P1；schema v13、P16–P20、Host 六处与门禁均通过，修复应集中在文档/pin/证据簿记。
4. **不 push、不关闭 Task**：r1 为 `changes_requested`；待 F-01 处置后的新 head 由 r2 复核再决定 approved；本报告不得作为 approved 依据。
5. **position 形状**：若 DSH 要把 `{x,y}` 提升为跨卡契约，补 PREQ errata/ADR；若维持「实现卡记录」口径，§2.1-1 已说明理由，无需额外动作。

## 8. 审查者声明

本报告由 lead 会话 `session-408d4e24-3789-4111-acde-983899601dad` 派发的**全新上下文子 agent**出具；审查者未参与 FEA-14-EDIT-1 的实现、测试、证据生成或返修，审查期间只读。唯一仓库写入为本报告；探针脚本、隔离数据库与本地复跑日志全部在 `%TEMP%\FEA14-EDIT1-review\`，未写真实 `%APPDATA%`，未 commit/push。PASS 仅基于本次 2026-11-10 17:06–17:20 的实测、脚本逐行比对与代码核对；未执行项已在 §6 记 NOT_RUN，未把未实测项写成 PASS。本报告只对 `8b2977209c61dce310aac2173b212a5cd56aa34c` 的字节有效；head 变化即自动失效。
