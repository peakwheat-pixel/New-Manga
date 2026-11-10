---
task_id: FEA-14-READ-1
reviewer: fresh 独立上下文子 agent（未参与实现；只读）
reviewer_kind: subagent
author: dsh
base_commit: 82ea7ca82
reviewed_head: a44c631cb
decision: changes_requested
---

# Review：FEA-14-READ-1（r1）

## 0. 范围异常与审查对象（先读）

- 仓库 `G:\CODEX\New Manga`，`main`；**HEAD = `a44c631cbe06c29fbd3744f069374979bfe47bed`**。审查开始 `2026-11-10T13:08:49+08:00`、结束 `13:13+08:00`，两次 `git status --short` 均 **clean**，HEAD 不变。
- **用户指定 base `82ea7ca82` 在实现提交之后**：`git log` 顺序为 f3f9ee5c4（Core schema）→ 9b1cabc23（Core wire）→ dacd2e901（v9 适配）→ d05460684（CoreClient/HostRuntime）→ 707ede92d（Host）→ 82ea7ca82（C-07 冻结落地）→ a44c631cb（证据/卡面）。因此 `git diff 82ea7ca82..a44c631cb` **只有 10 个文档/证据文件、没有一行 src/apps 代码**；真正实现 diff 是 `f9bf922aa..a44c631cb`（28 文件）。
- 本报告按用户要求记 `base_commit=82ea7ca82`，但**实际审查实现 diff 使用 `f9bf922aa..a44c631cb`**；卡面 `base_commit: e6964bf58` 也与两者均不一致。范围/provenance 见 R-008。
- 只读纪律：仅写本文件；未改源码/测试/契约/卡面/证据，未 commit/push。门禁/定向日志写仓外 `G:\CODEX\New Manga.workspace\temp\FEA-14-READ-1-r1\`。

## 1. 结论

**`changes_requested`**（P0=0 / **P1=1** / **P2=7** / **P3=3**）。

迁移与 Core 存储主链路可运行，但存在 **功能性 P1**：整书进度 P14 把「章节完成数」当作 `read_pages`、把「章节总数」当作 `total_pages`，与 AC3「按页面数计算」相反；此外 P10 部分 patch、P15 confirm/签名、P12/P15 Host 签名、C-07 inventory 合计、UNFREEZE pin 记录、范围外文件等问题需要返修。

## 2. Findings

| ID | 级别 | 位置 | 事实与影响 | 建议 |
|---|---|---|---|---|
| R-001 | **P1** | `src/infrastructure/sqlite/reading_export.py:627-648`；`src/bootstrap/core_service.py:5085-5088`；`tests/storage/test_reading_preferences.py:138`；`tests/core/test_read_wire.py:88-90` | **P14 整书进度按章节而非页面**：`book_progress` 的 `total` 是 `COUNT(*) FROM chapters`，`completed_chapters` 来自 `reading_progress.progress_percent`，handler 又把 `completed_chapters` 写成 `read_pages`、`total_chapters` 写成 `total_pages`。AC3 要求「按页面数计算」；测试只覆盖空书/两章场景，未对非空页面数做断言，因此该错误未被捕获。 | 用 pages 统计 `total_pages`/已完成页（含章节内按页进度），或在 wire 契约中明确字段改名为 chapters；补非空页数测试并断言 `read_pages/total_pages` 与实际 pages 一致 |
| R-002 | **P2** | `apps/desktop-avalonia/src/NewManga.App/Services/IHostController.cs:196,205`；`HostController.cs:478,535`；`CoreServiceClient.cs:1411,1475`；PREQ wire `:41-47,102-108` | **P12/P15 的 Host 签名偏离 PREQ**：PREQ 为 `CreateBookmarkAsync -> Task<BookmarkInfo?>`、`ResetReadingProgressAsync -> Task<bool>`；实现分别为 `Task<string?>` 与 `Task<int>`。P15 请求键 PREQ 为 `book_id,confirm_token?`，实现为 `book_id,confirm:bool`。偏差未在卡内记录，AC5「按 PREQ §8 形状」不成立。 | 按 PREQ 收紧签名/请求键，或在卡内记录偏离并更新冻结记录；同时更新 inventory/测试 |
| R-003 | **P2** | `IHostController.cs:205`；`HostController.cs:535-536`；`CoreServiceClient.cs:1475-1476` | **P15 默认 `confirm=true`**：Host 与 CoreClient 的 `confirm` 参数默认 true；任何调用方不显式传 confirm 也会发送 `confirm=true`，与 AC3「重置需确认」及 Core 的 `confirm=False` 拒绝语义相冲突。UI 未接线，但 API 层已埋下无确认重置路径。 | 默认改 `confirm=false`（或要求 confirm_token），由 UI 显式确认后再传 true；补 Host/Client 默认值测试 |
| R-004 | **P2** | `src/application/reading/service.py:549-609`；`src/bootstrap/core_service.py:5052`；无 partial-patch 测试 | **P10 部分 patch 会重置未提供字段**：PREQ P10 的 `prefs{mode?,...}` 全部可选，但 `save_preferences` 对缺省字段使用默认值写整行；例如先保存 `mode=translated`，再只保存 `zoom=2.0`，mode 会回到 `original`。`_extras_prefs` 也未与现有值合并。 | 先读现有 prefs 再合并 patch，或要求 wire 发送完整五字段并记录；补 partial patch 测试 |
| R-005 | **P2** | `doc/plan/FEA-C07_API_INVENTORY.md:20-22`；`generate_api_inventory.py --check` 输出 | **inventory 合计仍写 61，渲染值为 68**：`IHostController` 已改 61，但「合计」行未改 68；`--check` 仍返回 EXIT 0，说明 checker 未校验「合计」/IReaderProgressSink+IRunController 总和。README 却写「61/68」「EXIT 0」，AC5 的计数证据不成立。 | 把合计改为 68；修正 checker 让它校验合计；重跑并更新 README/卡面 |
| R-006 | **P2** | `doc/reviews/CONTRACT-UNFREEZE-2026-11-10-READ1.md:10-11` | **UNFREEZE 记录未填新 pin**：`新 pin（v1.3）：$h` 是占位符；同段 `erify_pins` 缺 `v`。`verify_pins` 能过是因为冻结文档 pin 正确，但该记录本身不可审计/不可复现。 | 填 `ab60d503…`（实际新 pin），修正 `erify_pins`→`verify_pins`；复核记录与 pin 文档哈希一致 |
| R-007 | **P2** | `git diff --name-only f9bf922aa..a44c631cb`；卡 allowed_paths `:21-52` | **范围 OUT=3**：`doc/reviews/CONTRACT-UNFREEZE-2026-11-10-READ1.md`（allowed 只有 `doc/reviews/FEA-14-READ-1-*.md`）、`tests/fea09/test_v7_migration.py`、`tests/fea11/test_source_gate_unify.py` 均不在 READ-1 allowed_paths（后两者是 v10 适配修改）。用户要求「系列提交 ⊆ allowed_paths」不成立。 | 扩 allowed_paths 并记录（尤其 UNFREEZE 载体与两个适配测试），或把这些改动移入后续/独立卡；重跑范围审计 |
| R-008 | **P2** | 用户 base `82ea7ca82`；卡 `:13` `base_commit: e6964bf58`；实现提交 f3f9…/82ea | **base/range provenance 不一致**：实现代码在 82ea 之前，`82ea..head` 没有任何 src/apps 变更；卡面 base 又是 e696（更早的 A4 r1 head）。按用户给的 base 会漏审全部实现；按卡面 base 也不正确。 | 统一 base 为 `f9bf922aa`（A4 收口、READ-1 实现起点）或明确「实现 diff f9bf..head」；卡面 base 同步 |
| R-009 | **P3** | `verification/FEA-14-READ-1/logs/dotnet-app-tests.log`；README `:22` | README 称「Reader 定向 70 passed」，但 `dotnet-app-tests.log` 只有 App 全量 867/0/11，没有 Reader 定向命令/结果；无法从仓库证据复现 70。 | 补 Reader 定向日志（或删除该数字，仅保留全量 867）；保留命令与 EXIT |
| R-010 | **P3** | `verification/FEA-14-READ-1/logs/pytest-full.log:119-124,170`；README `:23` | pytest 首轮 **5 failed / 3482 passed**、EXIT 1（fea09/fea11 v10 适配失败），随后重跑 3487/0/10、EXIT 0；README 只给最终 3487，未说明首轮失败与适配。 | README 注明首轮 5 failed→v10 适配→重跑通过；保留两段日志（已在 log 中） |
| R-011 | **P3** | `tests/storage/test_reading_preferences.py:80-116`；`tests/core/test_read_wire.py:55-84`；README AC1/AC3 | AC1 要求「重启/重新加载恢复（两次进程/两次装配）」，Core/wire 测试都在同一连接/同一 server 内读写；没有重启/两次装配验证。AC3 非空 P14 未测（见 R-001）。 | 增加两次装配/重开 DB 的偏好恢复测试；增加非空页面数的 P14 断言 |

## 3. AC 逐项

| AC | 状态 | 依据 |
|---|---|---|
| AC1 偏好持久化 | **PARTIAL** | Core schema v10/P9/P10 往返有测试；**UI 未接线**（README 披露）；P10 partial 有缺陷（R-004）；无两次装配/重启验证（R-011） |
| AC2 书签 | **PARTIAL** | Core+P11-P13 CRUD/跨书/非法 side 测试通过；**UI 未接线**；P12 Host 签名偏离 PREQ（R-002） |
| AC3 整书进度 | **PARTIAL** | reset confirm 有 Core 测试；**P14 实际是章节数而非页面数（R-001，P1）**；**UI 未接线**；P15 默认 confirm true（R-003） |
| AC4 迁移无损 | **MET** | v10 additive；旧 `reading_progress` 行字段级保留、新列 NULL；`test_v10_migration_preserves_legacy_progress_rows` 通过；v1-v9 bytes 未被改（v9 测试适配） |
| AC5 契约/门禁 | **PARTIAL** | pins 18/18、inventory `--check` EXIT 0、C-07 更新；但「合计 61 vs 渲染 68」、UNFREEZE `$h` 占位、P12/P15 签名偏离 PREQ（R-002/R-005/R-006） |
| AC6 证据 | **MET（P3）** | App 867/0/11、pytest 3487/0/10、targeted 8/0；但首轮 5 failed 未披露、Reader 70 无日志（R-009/R-010） |

## 4. 门禁与定向

| # | 命令/检查 | 时点（+08:00） | 结果 | EXIT |
|---|---|---|---|---|
| 1 | `pwsh -NoProfile -File tools/governance/check.ps1` | 13:12:45 → 13:12:48 | PASS（3 warnings：11 非终态 / STATUS 3173 B·31 L / PLAN 6926 B·64 L） | **0** |
| 2 | `... check.ps1 -TaskPath doc/tasks/FEA-14-READ-1.md` | 13:12:45 → 13:12:48 | PASS（同上） | **0** |
| 3 | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 13:12:47 → 13:12:48 | **PIN AUDIT: PASS (all 18)** | **0** |
| 4 | `python tools/generate_api_inventory.py --check` | 13:12:48 | **EXIT 0，但渲染合计 68 与文档合计 61 不一致**（checker 未校验合计） | **0** |
| 5 | `python -m pytest tests/storage/test_reading_preferences.py tests/core/test_read_wire.py -q` | 13:11:56 → 13:11:57 | **8 passed** | **0** |
| 6 | App.Tests（采用日志） | 12:57:43 起 | **867 passed / 0 failed / 11 skipped** | **0** |
| 7 | pytest 全量（采用日志） | 13:03:26 起 | **3487 passed / 0 failed / 10 skipped**；首轮 5 failed/3482 passed/EXIT 1（log `:119-124,170`） | **0（最终）** |
| 8 | `git status --short` + `git rev-parse HEAD`（开始/结束） | 13:08:49 / 13:13+ | 两次均 **clean**；HEAD 均 `a44c631cb…` | — |

**Canonical Evidence 5/5 sha256 与文件匹配**；**范围**按实际实现 diff `f9bf922aa..a44c631cb` 为 28 文件，OUT=3（R-007）；`82ea..a44c` 仅 10 文档/证据文件、无代码（R-008）。

## 5. NOT_RUN

- Fluent Reader UI 的偏好应用/书签面板/整书进度显示/reset 确认：**未接线**（README limitation）。
- 真实 UI 手势/IME/多屏/DPI/主题/托盘：NOT_RUN（沿用 A3 登记）。
- 跨内容连续序列（READ-2）：NOT_RUN。
- 本审查未重跑 App 全量/pytest 全量；采用 `verification` 日志 + targeted 8/0；未修改产品/测试/契约。

## 6. 处置建议

1. **R-001（P1）**：修正 P14 为按页面数统计（或明确改为 chapters 字段并改 AC/契约）；补非空页数测试。
2. **R-002/R-003（P2）**：P12/P15 Host 签名与 P15 confirm_token 对齐 PREQ，或将偏离记录并更新冻结；P15 默认 confirm 改 false。
3. **R-004（P2）**：P10 实现真正的 partial patch（读现有 prefs 合并），补测试。
4. **R-005/R-006（P2）**：inventory 合计改 68、checker 校验合计；UNFREEZE 填 `ab60d503…` 并修 `erify_pins`。
5. **R-007/R-008（P2）**：扩 allowed_paths/拆分 UNFREEZE 载体与适配测试；base 统一为 f9bf922aa（或明确实现范围）。
6. **R-009/R-010/R-011（P3）**：补 Reader 定向日志、首轮失败说明、两次装配/重启与 P14 非空测试。
7. 修后重跑 check/pins/API/targeted；真实 UI 仍按 NOT_RUN 登记。

## 7. 审查者声明

本报告由未参与 FEA-14-READ-1 实现的独立上下文子 agent 出具；只读审查，唯一写入为本文件。PASS 基于本次实测/日志/逐行核对；范围异常已在 §0 说明，未把 `82ea..a44c` 的文档增量误当实现证据；未执行项在 §5 记 NOT_RUN。
