# V11R-A-1 证据包：CreateChapter 服务层补齐（审计 P-01）

- Task：`V11R-A-1`（`doc/tasks/V11R-A-1.md`）
- Owner：`core-bridge`（DSH teammate）
- Worktree：`G:/CODEX/New Manga.workspace/worktrees/V11R-CORE-BRIDGE`，分支 `v11r/core-bridge`
- 基线 commit：`c73239999`
- 交付 commit（本证据对应的代码 SHA）：`f4f176f66cf98f865acd688e8b0be6399ed25fb5`
- 契约：`doc/plan/V11R_AVALONIA_CONTRACT.md` §5.1（FROZEN）
- 状态：AC1–AC6 已实现并有真实执行证据；Owner 未自审，待独立 Reviewer。

## 1. 交付内容

| 文件 | 变更 |
|---|---|
| `apps/desktop-avalonia/src/NewManga.App/Services/IHostController.cs` | **追加** `Task<ChapterSummary?> CreateChapterAsync(string bookId, string title, CancellationToken ct = default)`；`HostViewSnapshot` 追加 init-only `LastError`（typed code 通道）。既有 36 方法签名/行为未改。 |
| `apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs` | 实现 `CreateChapterAsync`：走 `HostRuntime.CreateChapterAsync`（Core `CreateChapter`，protocol minor 8，wire payload `{"book_id","title"}`）；空 `bookId` 本地拒绝；取消本地短路；其余失败经统一 `IsUiFacingFailure`/`ErrorCodeOf` 映射为 typed code。追加私有 `SetLastError`。 |
| `apps/desktop-avalonia/src/NewManga.App/Services/NullHostController.cs` | 确定性假实现：合法调用返回递增章节 `null-chapter-N`（计数器只在成功时前进）；空参数/取消返回 null；不抛异常。 |
| `apps/desktop-avalonia/tests/NewManga.App.Tests/FakeHostController.cs` | 追加脚本化 `CreateChapterAsync`：记录 `(bookId,title)`、可排队脚本结果、失败/取消走同一 `LastError` 通道。 |
| `apps/desktop-avalonia/tests/NewManga.App.Tests/ChapterCreationTests.cs` | 新增 10 条测试（见 §3）。 |

未修改：`src/NewManga.Host/**`（`HostRuntime.CreateChapterAsync` 在 GRANT-ISSUER-1 已存在，直接复用）、Python Core、UI/ViewModel、旧 `apps/desktop`。

## 2. AC 覆盖

| AC | 结论 | 证据 |
|---|---|---|
| AC1 三处新增契约签名 | PASS | `IHostController.cs`（`CreateChapterAsync` + `LastError`）；`git show f4f176f66 --stat` |
| AC2 走 Core `CreateChapter`（C037, minor 8），参数形状与 Core 实参一致 | PASS | 源码核对见表；真实 wire 帧见 `core-wire-createchapter.ndjson`（`version.minor=8`、payload 仅 `book_id`+`title`） |
| AC3 失败返回 null + 既有错误通道（不吞异常、不回显路径/secret） | PASS | 单测 + 集成断言 `LastError ∈ {INVALID_REQUEST, TARGET_NOT_FOUND, HOST_READ_ONLY, CANCELLED, HOST_NOT_READY}`；`LastError` 仅存 code，不含 message/path/secret |
| AC4 空白/超长/重名/空 bookId 与 Core 语义一致 | PASS | 集成测试：空白标题→`INVALID_REQUEST`；1024 字符标题→成功（Core 无长度限制）；同名重复→新章节（Core 不去重）；空 `bookId`→本地 `INVALID_REQUEST`（零 wire 帧） |
| AC5 单测：Null 确定性 + Host 成功/失败/取消；`dotnet test` PASS | PASS | `createchapter-tests.log`（10/10 PASS，含真实 sidecar 集成）；三项目全量日志见 §4 |
| AC6 `verification/V11R-A-1/` 证据 | PASS | 本目录 |

## 3. 测试（真实执行）

`ChapterCreationTests.cs` 共 10 条：

- `CreateChapterNullControllerTests`（2）：Null 假实现确定性递增；空参数/取消不推进序列。
- `CreateChapterHostLocalFailureTests`（3）：未启动→`HOST_NOT_READY`；空 bookId→`INVALID_REQUEST`；已取消 token→`CANCELLED`（均发 `Changed`）。
- `CreateChapterUiSeamTests`（3）：`FakeHostController` 记录请求并返回章节；脚本失败→`SCRIPTED_FAILURE`；空参数/取消 typed code。
- `CreateChapterHostIntegrationTests`（2，`[HostSidecarFact]`，无 fixture 时显式 Skip）：
  - 真实 sidecar：成功建章 → 重名建章（新 id、sort_order 递增）→ 1024 字符长标题成功 → 空白标题 `INVALID_REQUEST` → 不存在书籍 `TARGET_NOT_FOUND` → 预取消 token `CANCELLED` 且章节数不变。
  - 只读 Host（`parity=false`）：`HOST_READ_ONLY`，Host 状态保持 Ready。

运行（`NEWMANGA_CORECLIENT_SIDECAR_DIR` = 既有 AC11 sidecar 副本 `G:/CODEX/New Manga.workspace/task-envs/HOST-CORECLIENT-1/sidecar-copy`）：

```
cd apps/desktop-avalonia
dotnet test tests/NewManga.App.Tests/NewManga.App.Tests.csproj --no-build \
  --filter "FullyQualifiedName~CreateChapter" \
  --logger "trx;LogFileName=createchapter.trx" --logger "console;verbosity=minimal"
# 通过: 10, 跳过: 0, 总计: 10 → EXIT=0
```

## 4. 质量门（命令 / exit code / 结果）

| # | 命令（工作目录 `apps/desktop-avalonia`） | exit | 结果 | 证据 |
|---|---|---:|---|---|
| 1 | `dotnet build NewManga.sln -warnaserror` | 0 | 0 warning / 0 error | `build.log` |
| 2 | `dotnet test tests/NewManga.App.Tests/... --no-build` | 0 | 通过 147 / 失败 0 / 跳过 0（15 s） | `dotnet-test-app.log`, `trx/app.trx` |
| 3 | `dotnet test tests/NewManga.Host.Tests/... --no-build` | 0 | 通过 60 / 失败 0 / 跳过 0（1 m 20 s） | `dotnet-test-host.log`, `trx/host.trx` |
| 4 | `dotnet test tests/NewManga.CoreClient.Tests/... --no-build` | 0 | 通过 61 / 失败 0 / 跳过 0（1 m 46 s） | `dotnet-test-coreclient.log`, `trx/coreclient.trx` |
| 5 | `dotnet test NewManga.sln --no-build`（整解） | 0 | 通过 147 + 60 + 61 = 268 / 失败 0 / 跳过 0 | `dotnet-test-full.log` |

环境注记（既有测试夹具行为，非本任务改动）：若把 `NEWMANGA_EVIDENCE_DIR` 指向一个**全新**目录，`S3ShellTests.SettingsWiring_CoversImplementedCommands_AndRegistersNsBatch` 会因 `Evidence.Directory/commands/` 子目录不存在而失败（`ShellCommandCatalog.WriteEvidence` 直接 `File.Create`，不建父目录；`src/NewManga.App/Shell/ShellSupport.cs` 不在本任务写域）。重跑时预先创建该子目录后 147/147 PASS（见 `dotnet-test-app.log`）。不用该环境变量时测试走 `%TEMP%`，与基线行为一致。

## 5. 契约核实（源码 + 真实 wire）

### 5.1 Core 源码（`c73239999`）

| 事实 | 引用 |
|---|---|
| 命令路由 `CreateChapter` → `handle_create_chapter`，protocol minor 固定 8；错误 `INVALID_REQUEST`(+details)/`TARGET_NOT_FOUND`/`LIBRARY_WRITE_FAILED`/`UNKNOWN` | `src/bootstrap/core_service.py:240`（`_CREATE_PROTOCOL_MINOR=8`）、`:3513`（minor 校验）、`:3520-3552`（校验/异常映射） |
| CreateChapter 合法字段 = `book_id`(必填)、`title`(必填)、`chapter_number`(可选，默认 `""`)；未知字段→`INVALID_REQUEST`；book_id/title 必须非空字符串（`strip()` 判空） | `src/bootstrap/core_service.py:244-247`（`_CREATE_FIELDS`）、`:921-941`（`_create_validation_details`） |
| 结果外形 = `{chapter_id, title, chapter_number, sort_order}`（无 book_id/时间戳） | `src/bootstrap/core_service.py:1328-1339`（`handle_create_chapter`） |
| 标题唯一性/长度：Core 仅要求 `_require_text`（非空）；无长度上限、无重名去重 | `src/domain/books/entities.py:34-37`、`:118-159`（`create_chapter`）；`sort_order` 为当前最大值+1 |
| C# 侧已有 typed 通道：`HostRuntime.CreateChapterAsync` 以 minor 8 发送 `{"book_id","title"}` 并解析上述 4 字段 | `apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs:78-113` |
| 命令注册 `create_chapter → CreateChapter, minor 8` | `apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandRegistry.cs:123` |
| Dispatcher 对 `create_chapter` 无特判，payload 原样透传（因此服务层必须只发 Core 允许的键） | `apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandDispatcher.cs:169-427`（default 分支） |

### 5.2 真实 sidecar 探针（`core-probe/sidecar-createchapter-probe.txt`，脚本 `tools/probe_create_chapter.py`）

对既有 AC11 sidecar 副本逐条驱动 JSON-lines：`core.ping`(minor 3) → `CreateBook`(minor 8) → `CreateChapter` 5 个用例。关键响应（完整见文件）：

- 合法：`{"result":{"chapter_id":"8bfde…","title":"第 1 章","chapter_number":"","sort_order":1},"error":null}`，响应 `version.minor=8`。
- 空白标题：`{"error":{"code":"INVALID_REQUEST","category":"validation","details":[{"field":"title","issue":"blank"}]}}`
- 不存在书籍：`{"error":{"code":"TARGET_NOT_FOUND","category":"not_found"}}`
- 空 payload：`INVALID_REQUEST` + `details` 两项 `required`。
- wrong minor=3：`{"error":{"code":"INVALID_REQUEST"}}`（minor 必须 8）。

### 5.3 集成测试捕获的真实 wire 帧（`core-wire-createchapter.ndjson`，来自 `integration-evidence/host-logs/v11r-a1-create/wire/core-service.ndjson` 过滤）

| 帧 | 请求 | 响应 |
|---|---|---|
| req-6 | `{"version":{"major":2,"minor":8},"command":"CreateChapter","payload":{"book_id":"ad70…","title":"第 1 章"}}` | `result:{chapter_id:"a940…",title:"第 1 章",chapter_number:"",sort_order:1}` |
| req-8 | 同 req-6（重名标题） | 新 `chapter_id`，`sort_order:2` → Core 允许重名，服务层不去重 |
| req-9 | 1024 字符标题 | 成功 → 无长度限制 |
| req-10 | `title:"   "` | `error:{code:"INVALID_REQUEST",details:[{field:"title",issue:"blank"}]}` |
| req-11 | `book_id:"missing-book-id"` | `error:{code:"TARGET_NOT_FOUND"}` |
| （无帧） | 预取消 token | 本地 `CANCELLED`，0 帧 → 取消短路、不产生副作用 |

## 6. 偏差 / 遗留

1. **`LastError` 通道为追加实现**：契约 §5.1 要求“记录 `LastError`（沿用现有错误通道风格）”，但基线 `IHostController` 无该成员。实现选择在 `HostViewSnapshot` 追加 init-only `LastError`（仅 typed code），随既有 `Changed` 事件传播；不改既有 36 方法签名，不新增 interface 成员。
2. **NullHostController 语义**：契约 §5.1 要求“确定性假实现（返回递增章节）”，与既有的全 inert 风格不同；实现按契约返回 `null-chapter-N` 递增章节，但空参数/取消仍返回 null（不伪造成功）。
3. **集成测试 self-skip**：沿用仓库既有 AC11 fixture 约定（`NEWMANGA_CORECLIENT_SIDECAR_DIR`）。本次用既有副本 `task-envs/HOST-CORECLIENT-1/sidecar-copy`（未从 `c73239999` 重建），其行为已与当前源码逐条对照（§5.1/§5.2）；证据不声称该副本由本 SHA 构建。
4. **未改 `HostRuntime`**：其 `CreateChapterAsync` 已存在且语义正确，本任务只在 App 服务层补 seam，避免触碰 `NewManga.Host` 写域。
5. 后续消费方：`ui-shell`（B-1）可在建章对话框直接调用 `IHostController.CreateChapterAsync` 并读 `Snapshot.LastError` 显示 typed 错误。

## 7. 文件清单

```
verification/V11R-A-1/
  README.md                              （本文件）
  build.log                              dotnet build -warnaserror（0 warning/0 error, EXIT=0）
  createchapter-tests.log                CreateChapter 过滤测试（10/10 PASS, EXIT=0）
  dotnet-test-app.log                    App.Tests 全量（147 PASS, EXIT=0）
  dotnet-test-host.log                   Host.Tests 全量（60 PASS, EXIT=0）
  dotnet-test-coreclient.log             CoreClient.Tests 全量（61 PASS, EXIT=0）
  dotnet-test-full.log                   整解 dotnet test（268 PASS, EXIT=0）
  trx/createchapter.trx / app.trx / host.trx / coreclient.trx
  core-wire-createchapter.ndjson         集成测试真实 wire 帧（CreateChapter 过滤）
  core-probe/sidecar-createchapter-probe.txt
  tools/probe_create_chapter.py          探针脚本（可重跑）
  integration-evidence/host-logs/**      两次集成 Host 的 host.log / stderr / wire NDJSON
```
