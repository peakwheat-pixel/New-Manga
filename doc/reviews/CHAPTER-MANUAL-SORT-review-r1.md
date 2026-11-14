# CHAPTER-MANUAL-SORT 独立复核（r1）

- **verdict: ACCEPT_WITH_LIMITATIONS**
- **审查者**：`review-chapter-sort`（DSH `lead` 派发的独立上下文子 agent；**未参与** CHAPTER-MANUAL-SORT 的实现、返修或证据生成；只读复核被审 head；本报告是本次复核唯一写入）
- **被审 head**：`13d8367130e43e79c86ce688064e3f1b267b9a00`（`feat(chapter-manual-sort): 书架章节拖拽排序 + 原子持久化 + 缓存失效`），父提交 `79606ea4a`（基线）
- **复核期间 HEAD 变化**：另一会话在 2026-11-14 23:29:33 创建了后继提交 `97d9476b6`（maint：Gate §14 + 扩展既有缺陷登记）。本报告仍以 `13d836713` 为被审对象；`97d9476b6` **未修** F1，F4 的计数矛盾由该后继提交引入（见 F4 归因）。
- **复核时间**：2026-11-14 23:25–23:55（Asia/Shanghai）
- **环境**：Windows / Python 3.14.6 / .NET 9 / 仓库 `G:\CODEX\New Manga`
- **纪律声明**：未设置 `NEWMANGA_CORECLIENT_SIDECAR_DIR`；未跑全量 .NET；未修改生产源码（AC2 判别力实验的临时改动已还原，见 §4）；未提交、未 push。

## 0. 总结论

**代码正确性基本成立，契约零变化成立，AC2 的判别力经我实测成立**；但被审提交**不能原样集成**：它把一个越界文件（FEA-09 的 canonical evidence 日志）卷进了提交，并使 `EV-059` 的 pin 失效（P1）；另有 1 个真实的 UI 竞态（P2）、AC3 无任何可执行测试（P2）；当前树（复核期间的后继 maint 提交 `97d9476b6`）里 Gate 条件 1 计数自相矛盾（P2，归因见 F4）。修掉 P1、并对 P2 作出处置或明确接受后，可进入集成；AC3/AC5 必须在集成说明中继续保持 `NOT_RUN`。

---

## 1. 被审对象与范围核对

在被审 head `13d836713` 上，`git show --stat HEAD` 与任务卡一致，另含两项任务卡"改动文件"清单未列、但确在 diff 中的文件：

- `doc/TASK_LEDGER.md` — 在 `allowed_paths` 内（第 29 行），仅台账计数/表行同步，合规。
- `verification/FEA-09/logs/wire-redacted.ndjson` — **不在** `allowed_paths`，见 F1。

范围核对结论：除 F1 外，所有改动文件均落在卡面 `allowed_paths` 内；**未**发现新增 skip/xfail（`git diff` 精确扫描 `pytest.mark.skip|xfail|Skip=|Ignore=` 无命中）；**未**发现删除既有测试或放宽既有断言（测试侧仅新增 `ShelfChapterReorderTests.cs` 与 `FakeHostController` 的替身字段）。

复核期间工作树/HEAD 出现两处**他方会话的并发变化**：① `doc/REBASELINE_PLAN.md` 被并发修改（把 3 行 FEA-14 合并为 1 行）；② HEAD 在 23:29:33 前进到 `97d9476b6`（maint：Gate §14 + 扩展既有缺陷登记）。两者都不是我做的、与本报告无关；本报告所有结论以 **被审 head 13d836713** 为准，仅 F4 明确归因到后继 `97d9476b6`。

复核收尾时（约 23:50 后）工作树又出现**他方未提交改动**：`verification/FEA-09/logs/wire-redacted.ndjson` 已暂存回退（-1 行，工作树 5004 bytes，对应 F1 的修复动作）；`ShelfViewModel.cs` 与 `ShelfChapterReorderTests.cs` 有 +55/-2 未暂存改动（疑似针对 F2/F6/F10 的返修）。这些改动**不在本报告的复核范围**，其正确性我未审查、未运行；F1/F2/F3/F4 的判定均针对被审 `13d836713`（F4 针对 `97d9476b6`）的既有字节。

---

## 2. 逐 AC 判定表

判定以"我亲自核对/运行"为准，不以卡面声称代替。

| AC | 判定 | 依据（证据与我的核对） | 判别测试是否能固定住 |
|---|---|---|---|
| **AC1 原子持久化** | **通过** | `service.reorder_chapters` 先算全部 `sort_order` 再一次性调用 `update_chapters_atomic`（`service.py:212-230`）；repo 用单个 `with self._conn:` 包整批 UPDATE（`library.py:265-290`）；连接为默认 `isolation_level`（全仓无 `isolation_level=None`），`with conn` 的提交/回滚语义成立；空列表提前 return no-op（`:274-275`）；`import_order` 仅原样回写、`Chapter.reorder` 只改 `sort_order`（`entities.py:164-167`）。 | 有（见 AC2）。 |
| **AC2 判别测试（原子性）** | **通过** | 测试用 SQLite trigger 在提交顺序的**第三个**章节上 `RAISE(ABORT)`，逐章实现会先提交前两行。**我亲自把实现回退成逐章 `update_chapter` 循环后运行：1 failed, 4 passed**（失败点正是回滚断言）；还原后 5 passed（§4）。 | **是，已实测变红。** |
| **AC3 缓存失效** | **无法判定（作者标 NOT_RUN，诚实）** | 代码 `HostController.cs:651-662` 在 `updated == true` 时 `_chapterCache.Remove(bookId)`，位置/锁/键均正确；但仓库内**没有任何可执行测试**覆盖该行：`ShelfChapterReorderTests` 用无缓存的 Fake；`pending-host-cache-test.cs.txt` 是 `.cs.txt`，不参与编译与运行。 | **否**（删掉该行现有测试仍全绿）。 |
| **AC4 VM 拖拽语义** | **通过（有限）** | `ReorderChapterAsync` 计算移动、调用 Host、成功才重建集合、失败保持原序并给文案、越界不发起、同索引 no-op、只读拒绝（`ShelfViewModel.cs:275-332`）；8 个 .NET 测试实测通过。**保留**：AC 字面方法名是 `MoveChapterAsync`，实现/证据是 `ReorderChapterAsync`；"`SelectedChapter` 保持在原选中章节"无断言；空书/未选书边界无测试；另有 F2 的切书竞态。 | 部分（主体行为可判别；上述子条款不可）。 |
| **AC5 视图拖拽手势** | **无法判定（作者标 NOT_RUN，诚实）** | 只做静态核对：4px 阈值、隧道阶段 `PointerPressed` 不设 `Handled`（单击仍可选中）、独立 `DataFormat`（`CreateStringApplicationFormat("newmanga-shelf-chapter-index")`）、拖放只认领自身格式、文件格式未处理时继续冒泡。反射确认 Avalonia 11.3.22 的 `DragOverEvent`/`DropEvent` 均为 `Bubble`（文件导入在章节按钮上仍能到根节点）；`DataFormat.File` 与自定义 app format 不冲突。**无真机 GUI 拖拽/单击回归证据。** | **否**（没有任何 GUI/自动化手势测试）。 |
| **AC6 契约零变化** | **通过** | `doc/contracts/**`、`NewManga.CoreClient/**`、`IHostController.cs`、`NullHostController.cs` 均未改；`ListChapters` 仍由 service/`SQL` 按 `sort_order` 升序（`service.py:194-199`、`library.py:241-247`），并有 `test_list_chapters_wire_order_stays_sort_order_after_reorder`；`generate_api_inventory.py --check` → `OK`、`1/80/6=87`；`verify_pins.ps1` → `PASS (all 18)`；`check.ps1` → `PASS (2 warnings)`。 | 机械固定（inventory/pins）；排序语义有 Python 测试。 |
| **AC7 新增章节排末尾** | **通过** | `test_chapter_created_after_manual_reorder_lands_at_the_end` 实测通过；`create_chapter` 仍按 `max(sort_order)+1`（`service.py:167-172`），本卡未改该路径。 | 是（对 `create_chapter` 的排序回归有判别力）。 |
| **AC8 失败不假装成功** | **通过（有限）** | VM 失败路径断言集合顺序不变且含"失败"文案（`ShelfChapterReorderTests`）；Host catch 分支补 `SetLastError(ErrorCodeOf(ex))`（`HostController.cs:665-671`）。**保留**：Host 的 early-return（未就绪/空 bookId）仍不设错误码；VM 文案不显示 `LastError`；`SetLastError` 行为无测试。 | 部分（VM 文案与顺序有测试；Host 错误码无）。 |
| **AC9 并发保护（同实例重入）** | **通过** | `_isReordering` 在首个 `await` 前置位、`finally` 复位（`ShelfViewModel.cs:308-331`）；`ReorderChapter_WhileAWriteIsInFlight_RefusesTheSecondDrag` 实测通过，并断言 `ReorderCallCount == 1`。**测试质量保留**：若删掉守卫，第二次调用会 await 同一个未放行的 gate，测试会**挂起**而不是干净失败（F10）。 | 是（但回归呈现为 hang 而非 red）。 |
| **AC10 不回归** | **无法完全判定（已抽样验证）** | 我实跑：`tests/storage/ tests/library/` → **279 passed**；`tests/core/test_library_wire.py` → **6 passed**；`ShelfChapterReorderTests` → **8 passed**；未新增 skip/xfail、未放宽断言（静态）。**未复跑**全量 Python 与三项目 .NET（按任务要求不跑全量），卡面的 931/321/182 与"Python 全量 EXIT 0"未被独立复现；且 `regression.log` 的 914 基线疑似陈旧（见 F11）。 | 部分。 |

---

## 3. 核心正确性核对（AC1/AC2/AC3 细节）

### 3.1 原子性确实在单事务内

`update_chapters_atomic`：

```python
if not chapters:
    return
with self._conn:
    for chapter in chapters:
        self._conn.execute("UPDATE chapters SET ... WHERE chapter_id = ?", (...))
```

- 整批 UPDATE 在同一 `with self._conn:` 内；异常时 sqlite3 上下文管理器回滚。
- 连接由 `src/infrastructure/sqlite/connection.py:347` 以默认 `isolation_level` 创建；全仓未发现 `isolation_level=None`/autocommit，因此 `with conn` 的"进入即开事务、退出提交/异常回滚"语义成立。
- 空列表 no-op（提前 return）符合 AC1；`test_empty_book_reorder_is_a_noop` 覆盖。
- `reorder_chapters` 返回的 `Chapter` 对象在内存中已变序；但对象来自 `self.list_chapters` 的**新查询结果**，失败时不会污染仓库内存状态；下一次读取仍从 DB 取。
- `import_order` 保持不变：`Chapter.reorder` 只写 `sort_order`/`updated_at`，批量 UPDATE 把原 `import_order` 原样写回；`test_reorder_persists_one_to_n_and_freezes_import_order` 校验。
- `update_chapters_atomic` 是 `LibraryRepository` Protocol 的新必需方法；仓库内实现者只有 `SqliteLibraryRepository` 与测试替身 `InMemoryLibraryRepository`，两者都已实现（`tests/library/helpers.py:56-61`），无第三个实现者可被遗漏。

### 3.2 Host 缓存失效

`HostController.ReorderChaptersAsync`：

```csharp
var updated = await runtime.ReorderChaptersAsync(...);
if (updated) lock (_chapterCacheLock) { _chapterCache.Remove(bookId); }
SetLastError(updated ? null : "INVALID_REQUEST");
return updated;
```

- 只在 Core 返回 `{"updated": true}` 时失效；失败不失效（正确）。
- `SetLastError` 仅在值变化时触发 `Changed`（`:3020-3029`），不会造成事件风暴；现有测试中**没有**对真实 `HostController` 的 `ReorderChaptersAsync` + `LastError` 断言，因此未发现 `SetLastError(null)` 与既有测试冲突。`NullHostController`/`FakeHostController` 各自实现，不受影响。
- 保留的洞：`_runtime` 未就绪或 `bookId` 空时直接 `return false`，不设 `LastError`（F7）；缓存"读-填"与 eviction 的并发次序可把旧序重新填回（F8）。

---

## 4. 判别力实测（我亲自做，已还原）

### 4.1 实验步骤与原始结果

前置：`git status --porcelain` 为空；`service.py` sha256 = `8F3B73294AA20D48752DCD3C837A062182944BF41906307AB547EAA5BD7255CA`。

1) 在 HEAD 上运行：

```
python -m pytest tests/storage/test_chapter_reorder_atomic.py -q
.....                                                                    [100%]
5 passed
```

2) 临时把 `LibraryService.reorder_chapters` 改回逐章循环（`self._repo.update_chapter(chapter)`，不使用 `update_chapters_atomic`），重跑同一测试：

```
FAILED tests/storage/test_chapter_reorder_atomic.py::test_reorder_rolls_back_every_row_when_a_later_write_fails
AssertionError: assert {'c7b92d49…': 1} == {'c7b92d49…': 3}
  Differing items:
  {'c7b92d49…': 1} != {'c7b92d49…': 3}
  {'b2cd1138…': 2} != {'b2cd1138…': 1}
1 failed, 4 passed in 4.77s
```

失败点正是"回滚后全部 `sort_order` 与调用前一致"的断言：逐章实现下 `third` 已落库为 1、`first` 被改为 2，未回滚。

3) 还原：

```
git checkout -- src/application/library/service.py
sha256 after restore = 8F3B73294AA20D48752DCD3C837A062182944BF41906307AB547EAA5BD7255CA   # 与实验前一致
git status --porcelain -- src/application/library/service.py   # 空
python -m pytest tests/storage/test_chapter_reorder_atomic.py -q
5 passed
```

**结论：AC2 的判别性成立，不是卡面自说自话。** 还原后文件与 HEAD 字节一致（sha256 相等于实验前），`git diff` 为空。

### 4.2 其他 AC 的判别力（静态核对 + 一处重要保留）

- **AC4 边界/失败**：若删除 `_isReordering` 之外的分支，`OutOfRange`（`LastReorderCalled=false`）、`SameIndex`（无 wire 调用）、`ReadOnly`（无写 + 文案）、`WhenTheWriteFails`（可见顺序不变）都会变红——判别性成立（未逐个做 mutation，断言直接对应行为）。
- **AC9 重入**：断言 `ReorderCallCount == 1` 与最终可见顺序，当前实现下通过。**但**若守卫被移除，第二次调用会 `await` 同一个尚未 `SetResult` 的 gate（测试在 `await` 之后才放行），测试将挂起而不是失败（F10）。这是测试设计问题，不是实现问题。
- **AC3**：没有任何测试会在移除 eviction 时变红（F3）。
- **AC5**：没有任何自动化手势测试；pending 文件未编译（F3/F5）。

---

## 5. Findings

### F1（P1，必须修）越界改动 FEA-09 canonical evidence，并使 `EV-059` pin 失效

- **位置**：`verification/FEA-09/logs/wire-redacted.ndjson`（新增第 7 行）；对应 pin `verification/FEA-09/EV.md:69`（`EV-059`）。
- **证据**：
  - `EV-059` 记：`5004` bytes，sha256 `548de629d163d80b9cd8d1e62251de2016782e46a0c48a48575749d2a059d593`。
  - 父提交 `79606ea4a` 的该文件按工作树 CRLF 口径恰为 `5004` bytes / `548de629…`（我验证了 blob 的 LF 4998 加 CRLF 还原后完全等于 pin）。
  - HEAD 工作树为 `5838` bytes / `7d8dd346f0c94ff9fd023de336878071c3f61a8af307b00776adaf397fcad1b4`；本提交未更新 `EV.md`。
  - 成因：`apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/WireLogSourceRedactionTests.cs:33` 把测试帧写到仓库内该路径；本卡跑 CoreClient 回归时追加了一行，提交时未回退。
- **影响**：closed task `FEA-09` 的 canonical evidence 字节被改变、pin 失效；违反"历史日志/证据 pin 保持原字节"的治理要求与卡面 `allowed_paths`。这不是产品缺陷，但属证据完整性回归。
- **建议**：集成前由 Integrator 执行 `git checkout 79606ea4a -- verification/FEA-09/logs/wire-redacted.ndjson`（校验 5004 / `548de629…`）；把该测试改为写临时目录或本卡 evidence 目录，另开小卡（不属本卡范围）。

### F2（P2）`ReorderChapterAsync` 与"切换作品"并发时，会把旧书章节写进新书

- **位置**：`apps/desktop-avalonia/src/NewManga.App/ViewModels/Fluent/ShelfViewModel.cs:312`（await 前取 `SelectedBook.BookId`）、`:319-324`（await 后无条件 `Chapters.Clear()`/重填并读 `SelectedBook.Title`）；`SelectBookAsync:182-205` 无 `_isReordering` 守卫；`ShelfPageView.cs:453/471/492/496` 在写期间仍允许选书。
- **机制**：重排 await 期间用户点另一本书 → `SelectBookAsync` 用新书章节替换 `Chapters`；重排返回后把**旧书**的 `reordered` 列表清空重填，`SelectedChapter` 变成"不在集合里的章节"，详情栏/导入目标随之错位。
- **影响**：用户可见的错误状态（新书显示旧书章节）；AC4 只覆盖单书顺序，未覆盖该交叉路径。需要窗口期内点另一本书，概率不大但真实可达。
- **建议**：捕获 `bookId`（或 generation）并在 await 后校验 `SelectedBook?.BookId == bookId` 再改集合；或在 `IsReordering` 期间拒绝 `SelectBookAsync`。补一个 gated fake 测试：起重排 → 切书 → 放行 → 断言新书列表未被覆盖。

### F3（P2）AC3 是核心交付，但没有任何可执行测试固定住缓存失效

- **位置**：`HostController.cs:651-662`；`ShelfChapterReorderTests`（Fake 无缓存）；`verification/CHAPTER-MANUAL-SORT/pending-host-cache-test.cs.txt`（`.cs.txt`，不编译）。
- **证据**：全测试目录 grep 无"重排后 `ListChaptersAsync` 必须返回新序"的断言；`FakeHostController.ListChaptersAsync` 直接返回脚本列表，不缓存。pending 测试设计本身有判别力（会命中 stale cache），但当前不可执行；其依赖的 `CreateChapterSidecarFixture.CreateOptions`/`TryDeleteDirectory`/`HostSidecarFact` 均存在（静态核对），仍不能替代运行。
- **影响**：删掉 eviction 行，现有测试全绿；该回归无自动防线。作者标 `NOT_RUN` 是诚实的，但集成时必须把它当作限制而不是"已覆盖"。
- **建议**：Gate 条件 4 产出绑定当前 commit 的 sidecar 后转正 pending 测试；在此之前不得在集成说明中写 AC3 通过。可顺带把 pending 测试纳入编译检查（独立 sidecar 测试工程或条件编译），避免位腐。

### F4（P2，归因后继 maint 提交 `97d9476b6`，非被审 feat commit）Gate 条件 1 计数在当前树自相矛盾

- **归因**：被审 `13d836713` 中 assessment 只到 §13；STATUS 的 "4/8" 与 §11 的 "3/8 → 4/8" 一致，**没有矛盾**。复核期间（2026-11-14 23:29:33）另一会话提交 `97d9476b6` 追加 §14（"0/8 → 6/8 → 7/8 → 8/8 有处置依据"），但**未同步 STATUS**（仍 4/8）。
- **位置/证据（当前 HEAD 97d9476b6）**：
  - `doc/STATUS.md:8`："条件 1 = 4/8（本卡承接 L-L1-2 排序 UI）"。
  - `doc/reviews/MAINT-1-RELEASE-GATE-ASSESSMENT-2026-11-14.md:165`："0/8 → 6/8（本轮前）→ 7/8（本轮 L-L1-2）→ 8/8 有处置依据"；§14 表把 `L-R1-1`/`L-R2-1` 记为已实现。
  - 更早的 `doc/reviews/HANDOFF-2026-11-14.md:44/108` 把 `L-R1-1`/`L-R2-1` 列为剩余 4 项之一。
- **影响**：当前树上同时存在 4/8 与 7/8 两个"已关闭"口径；若以任一数字继续 Gate 工作，会建立在不确定基线上。这不影响被审 feat commit 的代码结论，但影响集成时的 Gate 记录。
- **建议**：DSH 在集成前统一口径（区分"已关闭"与"有处置依据"），同步 STATUS/assessment/handoff；若 §14 的 L-R1-1/L-R2-1 复核成立，STATUS 应更正为 7/8（或明确标注旧口径）。

### F5（P3）E-1 的"前端不可达/未投影"表述过强；"与本卡无关"成立

- **位置**：`doc/reviews/MAINT-1-EXISTING-FINDINGS-2026-11-14.md:31-32`（被审 `13d836713` 版本；后继 `97d9476b6` 改写根因后，同一句仍在 `:43`）。
- **我验证的算术**：反射 `NewManga.CoreClient.Commands.HostCommandRegistry`：`All.Count = 111`；六域合计 `90`；`Drafts = 6`、`SourceSync = 15`（合计 21）。E-1 的失败断言（111 vs 90）在结构上确实无法通过，且本卡未改 registry/domain services/该测试 → **"与本卡无关"成立**。
- **但**：`drafts_*` 在 `HostController.cs:3121-3263` 直接 `commands.InvokeAsync`；`source_*` 在 `HostRuntime.cs:1275/1368` 出现。至少不能说"这些命令在前端不可达"。建议改为"未由 `HostDomainService` 覆盖（测试口径与生产分派方式不一致）"。

### F6（P3）AC4 的方法名与实现不一致，且 SelectedChapter/空边界无测试

- **位置**：卡面 `doc/tasks/CHAPTER-MANUAL-SORT.md:79`、`:93` 写 `MoveChapterAsync`；实现 `ShelfViewModel.cs:275` 与证据写 `ReorderChapterAsync`。
- **缺口**：AC4 的"`SelectedChapter` 保持在原选中章节"无断言（代码上同一实例确实保留，但 `??= moved` 会在无选中时新建选中，且不刷新 `PreviewPages`，`ShelfViewModel.cs:323`）；空书、未选书边界无测试（`:278-285` 返回 false）。
- **建议**：统一命名（建议改卡面文字为 `ReorderChapterAsync`）；补 SelectedChapter 断言与两个边界用例。

### F7（P3）Host 失败诊断只覆盖 exception 路径；VM 文案未用上错误码

- **位置**：`HostController.cs:644-647` 在 `_runtime` 未就绪/`bookId` 空时直接 `return false`，不 `SetLastError`；`:662` 的 `INVALID_REQUEST` 只覆盖响应非 true。`ShelfViewModel.cs:315` 固定"章节顺序保存失败"，没有像 `CreateBookAsync:344` 那样带 `_host.Snapshot.LastError`。
- **影响**：与提交信息"失败补 `SetLastError`，可诊断"的意图不完全一致；用户仍无法区分 `INVALID_REQUEST` 与旧 sidecar。
- **建议**：early-return 也设 `HOST_NOT_READY`/`INVALID_REQUEST`；VM 文案附 code（与 CreateBook 一致）。

### F8（P3）缓存"读-填"竞态：eviction 可能被在途 ListChapters 的旧结果重新填回

- **位置**：`HostController.cs:943-958`（查缓存 miss → await Core 读 → 写回）；eviction 在 `:655-660`。
- **机制**：一个在重排写入前发出、在 eviction 后返回的 `ListChapters` 会把旧序写回缓存；此后 `ListChapters` 命中旧序，AC3 的"成功返回后必须返回新序"在并发读下不严格成立。
- **性质**：预存在的缓存设计限制，本卡的单点 eviction 不能单独消除；窗口很小。
- **建议**：缓存条目加 generation（重排成功递增，写回时校验），或写回前检查是否已被显式失效；至少登记为已知限制并在 AC3 的未来测试中覆盖。

### F9（P3）`update_chapters_atomic` 复制了 `update_chapter` 的整段 SQL

- **位置**：`src/infrastructure/sqlite/library.py:249-263` 与 `:265-290`。
- **影响**：将来加列/改列容易只改一处，形成两套写路径语义漂移。
- **建议**：抽 `_CHAPTER_UPDATE_SQL` 与 `_chapter_update_params(chapter)` 共用。

### F10（P3）判别测试的注释计数与 AC9 的失败模式

- `tests/storage/test_chapter_reorder_atomic.py:62-64` 写 "Fail on the SECOND update"，实际是提交顺序的**第三个**（`[third, first, second]`，trigger 在 `second`）。
- AC9 测试若移除守卫，第二次调用会 await 同一个未放行的 gate（`ShelfChapterReorderTests.cs:100-115`），测试将**挂起**而非断言失败；建议给 gate 加短超时/先放行后断言，使回归是干净的 red。
- AC2 的失败注入点从 AC 字面的"注入 `update_chapter` 抛错"改成 SQL trigger（实现已不逐章调用）——这是合理且更强的做法，但 AC 文字应同步，避免读者按字面对照。

### F11（P3）卡面交付记录、回归基线与四件套日志的陈旧/算术问题

- `doc/tasks/CHAPTER-MANUAL-SORT.md:128-131` 仍写"实际测试：尚无"，与 `:109-116` 的 PASS/NOT_RUN 表矛盾；AC 复选框全未勾（可解释为 review 前状态，但"实际测试"应同步）。
- `verification/CHAPTER-MANUAL-SORT/regression.log:22-26` 以 914 作 App 基线并与 931 比；本提交只新增 8 个测试（`ShelfChapterReorderTests`），`HANDOFF-2026-11-14.md:27` 记 TRANS-ENTRY-UI 已 923 ⇒ 实际基数应为 923、+8；CoreClient 182 vs 180 也来自陈旧基线。建议按被审 base 重跑或明确标注"与 handoff 旧记录比，不可归因于本卡"。
- `four-pieces.log` 记 `check.ps1` `PASS (3 warnings)`，并记 `doc/STATUS.md` 为 `3164 bytes / 32 lines`；但被审 `13d836713` 里的 `doc/STATUS.md` 实际为 **2448 bytes**（我实跑同版 check.ps1 得 `PASS (2 warnings)`，无 STATUS 警告；期间 PLAN 被他方并发修改）。说明该日志生成于提交前的中间态，不是被审树的逐字节复现；建议注明生成时点或重生成。

### F12（P3）视图/VM 的健壮性与排版细节

- `ShelfPageView.cs:577-639` 的 PointerMoved/Drop 是 `async void` 句柄；若 `ReorderChapterAsync` 抛出 Host catch 列表之外的异常（如 `ObjectDisposedException`），会成为未处理异常。`HostController` 的 catch 只列固定类型（`:665-671`）。
- `ShelfViewModel.cs:323` `SelectedChapter ??= moved`：无选中时拖拽会隐式选中被拖章节，但不刷新 `PreviewPages`（与 `SelectChapterAsync` 不一致；AC4 未要求）。
- `ShelfViewModel.cs:319` `Chapters.Clear();            foreach` 同行排版；`_isReordering` 字段插在方法之间。
- 视图侧路由我做了静态验证（`DragOverEvent`/`DropEvent` 均为 `Bubble`；自定义 app format 与 `DataFormat.File` 分离），但真实手势/单击回归仍需 AC5 的真机证据。

---

## 6. 契约零变化核对

- `git diff --name-only 79606ea4a..HEAD -- doc/contracts apps/.../NewManga.CoreClient apps/.../IHostController.cs apps/.../NullHostController.cs` → **空**。
- `M2-C1` 明确 `ListChapters` 按 `sort_order` 升序（`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:204/661/690`）；`service.list_chapters` 与 `SqliteLibraryRepository.list_chapters` 都按 `sort_order`，本卡未改该逻辑。
- `python tools/generate_api_inventory.py --check` → `OK: rendered counts match FEA-C07 doc`，`1/80/6=87`。
- `pwsh -NoProfile -File tools/governance/verify_pins.ps1` → `PIN AUDIT: PASS (all 18)`。
- `pwsh -NoProfile -File tools/governance/check.ps1` → `Governance check: PASS (2 warnings)`。
- 结论：**wire 命令、DTO、字段未改；`ReorderChapters` 复用既有命令；零 UNFREEZE 成立。** 与卡面的方案偏离登记一致（`custom_rank` 未新增消费端，作为已知限制）。

---

## 7. 诚实性核对

- **AC3/AC5 的 NOT_RUN 是诚实的**，不是把未验证写成通过。理由核对：
  - `ReorderChapters` 命令确实由 `83e45cfe5`（2026-11-10 15:03:39 +0800）引入；
  - `NEWMANGA_CORECLIENT_SIDECAR_DIR` 指向的 sidecar copy 内 `core_service.exe` 等确为 **2026-10-23 19:21**；
  - 我扫过的 `core_service.exe` 中，2026-11-14 的 5 KB 文件是测试 stub；真实 sidecar 主要是 2026-10-23 的 68 MB 包（另有 2026-10-29 的 399 KB 发布启动器），**未发现 2026-11-10（`ReorderChapters` 引入）之后构建的可用 sidecar**。
  - "PyPI 不可达"我**未**复验（见 §8），但上述两条足以支撑"该环境无法跑 AC3 集成"。
- **E-1 的"与本卡无关"成立**（算术 111/90/21 已独立验证；本卡未改相关文件）；但"前端不可达/未投影"表述过强（F5）。
- **条件 1 计数**：被审 `13d836713` 内为 4/8（与 §11 一致）；复核期间的后继 maint 提交 `97d9476b6` 追加 §14 后与 STATUS 4/8 形成两个口径，需要 DSH 统一（F4，归因后继提交）。
- **卡面 "实际测试：尚无"** 与测试表 PASS 矛盾（F11），属文档陈旧而非虚构。
- 未发现把失败写成通过、把 NOT_RUN 写成 MET 的文字。

---

## 8. 我没有验证的面（如实列出）

1. **AC3 真实缓存失效集成**：未设置 `NEWMANGA_CORECLIENT_SIDECAR_DIR`（任务要求且夹具过期），未跑 sidecar 集成；pending 测试未编译、未运行。
2. **AC5 真实 GUI 拖拽**：无 Avalonia 真机/交互证据；未验证拖拽是否误触发单击、拖拽后按钮重建时序、文件拖入章节按钮的实际行为（只做了路由策略反射与静态核对）。
3. **全量测试**：未跑全量 Python（只跑 `tests/storage/ tests/library/`、`tests/core/test_library_wire.py`），未跑三项目 .NET 全量；卡面的 931/321/182、CoreClient 全绿、"Python 全量 EXIT 0" 未被独立复现。
4. **PyPI/PyInstaller 重建 sidecar**：未验证网络与重建可行性。
5. **pending 测试的可编译性**：只核对了其依赖符号存在（`CreateChapterSidecarFixture.CreateOptions`、`TryDeleteDirectory`、`HostSidecarFact`、`HostViewState`），未实际编译。
6. **SEC-01/SEC-02 的远端可见性内容**：只核对了 task `status`/`integration_commit` 与 `REPORT.md` 的结论段落，未做 GitHub 访问验证。
7. **条件 1 其余 5 项的逐项裁决**：只验证了 `ReaderVisibleControlsTests` 4/4 通过（支持 §14 的 #1），未重裁 8 项 finding 的状态。
8. **他方会话在复核期间对 `doc/REBASELINE_PLAN.md` 的并发修改、以及 HEAD 前进到 `97d9476b6`**：未审查该后继提交的全部内容（只核对了它触及的两份文档与 F4 归因），未回退任何他方改动。

---

## 9. 集成结论（明确回答）

**这份改动能否进入集成？**

- **代码本身可以进入集成**：AC1/AC2/AC4/AC6/AC7/AC8/AC9 的实现正确，AC2 的判别力经实测成立，契约零变化；AC10 的定向回归通过。
- **当前树（含后继 `97d9476b6`）的字节不能原样集成**：F1 仍存在于当前 HEAD，必须先处理 **F1（P1）**，即把 `verification/FEA-09/logs/wire-redacted.ndjson` 回退到父提交字节（5004 / `548de629…`），否则会破坏 closed task 的 canonical evidence pin。
- **F2（P2）** 应在集成前修复或由 DSH 明确接受并登记；**F3（P2）** 的 AC3 自动化缺口、**F4（P2，属后继 `97d9476b6`）** 的 Gate 计数矛盾，至少要在集成说明/STATUS 中如实登记，不得写成"AC3 已通过""条件 1 已 X/8"而不给出统一口径。
- **AC3、AC5 必须保持 `NOT_RUN`**，在 sidecar 重建与真机 GUI 验证前不得宣称通过。

综合：**ACCEPT_WITH_LIMITATIONS——修掉 P1、处置/登记 P2 后可集成；否则不能。**
