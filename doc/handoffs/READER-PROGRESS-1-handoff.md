---
task_id: READER-PROGRESS-1
author: saber-ui-spec (DSH team)
recipient: DeepSeek Harness
base_commit: 230164c5c
delivery_head: 10a0308c13a11c8be4f75967b48dbdb051116397
status: ready-for-integration
---

# Handoff：READER-PROGRESS-1（阅读进度保存接线）

## 交付结果

实现提交 **`10a0308c13a11c8be4f75967b48dbdb051116397`**（branch `task/READER-PROGRESS-1`，worktree `G:/CODEX/New Manga.workspace/worktrees/READER-PROGRESS-1`）；本 Handoff 与任务卡 pin 在后续文档提交中记录。未 push、未改 Python Core/旧壳/协议语义/Host 契约语义。

| AC | 结论 | 说明 |
|---|---|---|
| AC1 保存/恢复 | **MET** | 翻页、离开阅读器页、关闭主窗/沉浸窗 → `SaveReadingProgress`（参数对齐旧壳）；重开 → `GetReaderProjection(start_position=resume)` 恢复；失败 typed 降级（NotReady/ReadOnly/Failed），UI 不阻塞。 |
| AC2 边界 | **MET** | 多书独立；页数变少钳制（Core `_remap` + 客户端 clamp）；只读 Host 不发 Core 请求；无 Core → NotReady。 |
| AC3 测试 | **MET** | Headless「打开→翻页→关闭→重开恢复」；真机 BOOK-FIXTURE 隔离根两会话：首启翻页保存→关闭→重启 resume 到保存页，恢复过程零写入。 |
| AC4 回归 | **MET** | test.ps1 **131/131**；vitest **60/567**；pytest **3F/2739P/9S**（基线同）。 |
| AC5 门禁 | **MET** | `check.ps1 -TaskPath` PASS；11 条 64-hex pin；本 Handoff。 |

### 代码变更（全部 `apps/desktop-avalonia/**`）

- `src/NewManga.CoreClient/CoreServiceClient.cs`：`GetReaderProjectionAsync(..., startPosition)` + `initial_position`/`saved_progress` 解析；`SaveReadingProgressAsync`（可选字段 MISSING=NOT SENT）；`ReadingProgressSnapshot`。
- `src/NewManga.CoreClient/Wire/CoreProtocol.cs` + `Transport/SidecarProcess.cs`：识别并跳过 `core_service` 事件帧（`ReadingProgressChanged` 先于响应到达同一条 stdout），否则客户端会拿到 `INVALID_RESPONSE`。
- `src/NewManga.Host/HostRuntime.cs`：`SaveReadingProgressAsync` 写权限门（只读 → typed `ReadOnlyHostException`）+ 复用 `_readerIoGate` 串行门（core_service 严格一问一答）。
- `src/NewManga.App/Services/{IHostController,HostController,NullHostController,ReaderLibrary}.cs`：`IReaderProgressSink` seam、resume 映射与页数钳制。
- `src/NewManga.App/Views/ReaderWorkbenchPages.cs`：进度保存（翻页/滚动/离开/关闭）、reading clock 仅成功后重置、重复位置合并、**恢复期间抑制 ScrollChanged 写入**、webtoon 逻辑页像素偏移。
- `src/NewManga.App/Views/MainWindow.axaml.cs`：注入 sink、`LoadReaderAsync(bookId, chapterId)`、离开/关闭 flush、沉浸窗 sink。
- 测试：`tests/NewManga.App.Tests/ReaderProgressTests.cs`（18）、`tests/NewManga.Host.Tests/HostReaderProgressIntegrationTests.cs`（3）+ `Support/BookFixture.cs`；`FakeHostController` 增加 `FakeProgressStore`。
- 脚本（向后兼容）：`scripts/test.ps1` 新增可选 `-EvidenceDirectory`；`scripts/start-book-fixture.ps1` 新增可选 `-ExtraArgs`。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC4 全量 | `pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1 -EvidenceDirectory G:/CODEX/New Manga.workspace/task-envs/READER-PROGRESS-1/evidence` | Windows 10.0.26300；`10a0308c1` | PASS 131/131（coreclient 40 / host 40 / app 51） | `verification/READER-PROGRESS-1/test/summary.json`、`test/dotnet-test-Debug.log`、`test/results-*.trx` |
| AC4 vitest | `cd apps/desktop/frontend && npm test`（主仓运行；`git diff b50ab8fc5 -- apps/desktop/frontend` 为空） | 旧壳未改动 | PASS 60 files / 567 tests | `test/vitest.log` |
| AC4 pytest | `PYTHONPATH=src python -m pytest -q` | 未改 Python | 3F/2739P/9S（基线一致，失败集合：detection_real ×2 + workbench 时序） | `test/pytest.log` |
| AC1/AC3 真机 | `start-book-fixture.ps1 -AppExe <pkg>/NewManga.App.exe -DataRoot <isolated-data> -ExtraArgs '--demo-write'`；会话 A：打开→翻页×2→离开→关闭；会话 B：重启→打开阅读器 | 发布件 `pkg/app`（29,364,046 B）+ `core-sidecar`（junction → FINAL-VALIDATION-1 打包件）；BOOK-FIXTURE 副本 | PASS：会话 A 保存页 `a607fc…`（total 34.64s）；会话 B `resume` 返回 `initial_position=a607fc…`，零写入，DB 行不变 | `live-evidence.json`、`screens/01-*.png`、`screens/02-*.png`、`runtime-logs/*` |
| AC5 治理 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/READER-PROGRESS-1.md` | `10a0308c1` + 文档提交 | PASS（2 warnings：非终态 Task / STATUS 预算） | 见任务卡 pin |

明确未运行：真实 Core 的「第二本书」与「页数变少」场景（fixture 仅 1 书 1 章 8 页，未改 fixture 语义）→ 由 headless + Core `_remap` 单测覆盖，真机 NOT_RUN。旧壳 vitest 在主仓运行而非 worktree（worktree 无 `node_modules`），因前端目录与 base 零差异。

## 接收方式

- 分支/worktree：`task/READER-PROGRESS-1` / `G:/CODEX/New Manga.workspace/worktrees/READER-PROGRESS-1`；delivery head `10a0308c1`。
- 复现：见 `verification/READER-PROGRESS-1/REPORT.md §6`。
- 真机前置：发布单文件 App + `app/core-sidecar`（含 core_service.exe/host_bridge.exe）；数据根用 BOOK-FIXTURE 的 **durable 状态副本**（`library.db`+`managed/`；不要拷贝 `derived/`、`catalog/`，其绑定源根身份会让 Core 拒绝启动）；写权限需 `--demo-write`（AppOptions 只认 `--data-root=` 等号形式）。
- 需要 DSH 做：独立 Review（Owner 不自审）→ 运行 test.ps1 复核 → 合入/集成 → closeout（resource manifest 复核后决定 task-env 去留）。

## 下一任务建议（必填）

- Task ID / 标题：**CHAPTER-SELECTOR-1**（team task-25，多章选择器 + 多书入口，同一 A 组第一批；已授权）。
- 推荐 Agent / Reviewer：Owner = saber-ui-spec（同一实现者续作，上下文已热）；Reviewer = DSH（必要时另指定未参与实现的 Agent）。
- 推荐原因与前置依赖：与本任务改同一批文件（ReaderWorkbenchPages/MainWindow/HostController/LoadReaderBookAsync），已有 `LoadReaderBookAsync(bookId, chapterId)` 与 `ReaderBookData.ChapterId` 基础，继续施工冲突最小；依赖本任务不破坏 resume 语义。
- Recovery point：仓库 `G:/CODEX/New Manga`；建议从 `10a0308c1` 建 `task/CHAPTER-SELECTOR-1`（worktree `G:/CODEX/New Manga.workspace/worktrees/CHAPTER-SELECTOR-1`）。
- 允许修改路径：`apps/desktop-avalonia/**`、`doc/tasks/CHAPTER-SELECTOR-1.md`、STATUS/PLAN/LEDGER、`verification/CHAPTER-SELECTOR-1/**`、workspace task-env。
- 禁止范围：不改 Python Core/旧壳/协议与 Host 契约语义；不 push；不 gc/prune。
- 交付物：章节列表（`list_chapters`）+ 当前书/章可见 + 从书架任一本书进入阅读器（不再固定第一本第一章）+ headless（切章更新页数、投影、多书分别打开）+ 真机（BOOK-FIXTURE 可复制成两本书）+ 门禁。
- 验证命令与完成 Gate：同本任务（test.ps1 全绿、vitest 60/567、pytest 基线、check.ps1 PASS、64-hex pin、Handoff）。
- 可直接转发给 Agent 的指令：

```text
接 A 组第一批第二个任务 CHAPTER-SELECTOR-1（team task-25）。base 用 10a0308c1（READER-PROGRESS-1 delivery head），建 worktree G:/CODEX/New Manga.workspace/worktrees/CHAPTER-SELECTOR-1 与 branch task/CHAPTER-SELECTOR-1。
先读 doc/tasks/CHAPTER-SELECTOR-1.md、doc/handoffs/READER-PROGRESS-1-handoff.md、apps/desktop-avalonia/src/NewManga.App/Views/ReaderWorkbenchPages.cs、ReaderLibrary.cs、HostController.cs、IHostController.cs。
实现：阅读器页显示章节列表（走 HostRuntime.ListChaptersAsync）并可切换章节（复用 LoadReaderBookAsync(bookId, chapterId) + GetReaderProjection resume）；书架多书任选进入阅读器（MainWindow 接受 bookId 入口，不再固定第一本/第一章）；当前书/章可见；切章后页数与投影更新。
测试：headless 覆盖切章更新页数/投影、多书分别打开；真机用 BOOK-FIXTURE 副本（可复制成两本书）验证。
门禁：scripts/test.ps1 全绿、check.ps1 -TaskPath PASS、64-hex pin、Handoff；不改 Python Core/旧壳/契约语义；不 push；不 gc/prune；验证不了就标 PARTIAL/BLOCKED。
每个 AC 逐条回报并给证据路径。
```

## 风险与遗留

1. `HostCommandRegistry` 中 `library_save_reading_progress` 仍为 `NOT_SUPPORTED`：parity 探针 `probe-core-commands.ps1` 用了错误 payload（`{chapter_id, position}`），Core 返回 `INVALID_REQUEST` 才被登记；本轮与 `GetReaderProjection` 相同，从 Host/CoreClient 直接接线，未改分类与冻结 parity 证据。建议后续单开任务修正探针 payload 并同步 parity 快照（改动会触发 HOST-COMMAND-MIGRATION-1 证据重建）。
2. 真机未覆盖「多书独立」「页数变少」（fixture 单书单章）；如需，需新建含两本书的 fixture（会改动 BOOK-FIXTURE 语义，超出本卡）。
3. 关闭主窗 flush 用线程池执行（同步等待会与 UI 上下文死锁）；若关闭时恰有无网络/慢 Core，最长等待 5s，超时放弃（进度可能丢最后一段，不影响退出）。
4. 进度写入策略：翻页即时写；webtoon 滚动「换页或 >1s」节流；恢复期间与无用户交互时不写（防止 restore 自覆盖）。未做长时滚动写压力测试。
5. 需独立 Review（Owner 不得自审）。
