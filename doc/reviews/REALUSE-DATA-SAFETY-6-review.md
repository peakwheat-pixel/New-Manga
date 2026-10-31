---
document_id: REALUSE-DATA-SAFETY-6-review
kind: independent_review
task_id: REALUSE-DATA-SAFETY-6
reviewer: safety6-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams fresh context task-3（独立子 agent，未参与实现与返修）"
reviewer_independent: true
reviewed_head: 0feff7a4c
reviewed_base: 841cbdc4b
delivery_head: fb5065013
verdict: approved
captured_at: 2026-11-01T01:17:35+08:00
---

# Review：REALUSE-DATA-SAFETY-6（上下文独立审查）

> 本报告只对 `reviewed_base = 841cbdc4b`、`reviewed_head = 0feff7a4c`（`task/REALUSE-DATA-SAFETY-6` HEAD，含 merge `main@6cab0b083`）有效。审查者只读该 head；仓库内唯一写入即本文件。所有运行命令均在该 worktree 内执行，负向对照/竞态复现只在仓外临时副本执行（`G:\CODEX\New Manga.workspace\tmp\safety6-review\`）。

## 1. 结论

**verdict: approved。**

- **P0：0 条；P1：0 条；P2：3 条（open，均不阻断集成）**。
- AC1（MA-09 进度刷新）**MET**：三条刷新路径（保存后同动作镜像、关闭后权威重读、导入后补读）在生产代码里真实接线；只有 Core 真正提交（`IsSaved`）才刷新；类型化拒绝不伪造；深链不串章。新增用例复跑 **5/5**，全量 App.Tests 复跑 **394 通过 / 0 失败 / 7 跳过**；"移除接线 → 3/5 失败"的负向对照由本 Reviewer 在仓外副本独立复现（3 failed / 2 passed）。
- AC2（MA-19 derived 冗余）**MET**：结论"现阶段必需、不改代码"的代码面、数据面、约束面三条证据链均能复核——关键代码行号与真实数据只读盘点（managed 169 文件 / 100,434,899 B ≡ derived/pages 169 文件 / 100,434,899 B；catalog 169 行全 `derived-read-only`）由本 Reviewer 独立重算一致；AD-003 §3.2 原文禁止以"消除双份"为由删除；**无越权代码改动**（branch diff 内 `src/**`、`scripts/**`、`tools/**` 零改动）。
- AC3（MA-11 / MA-20）**MET（严格零实施）**：只出方案（A0–A4 / M-1–M-4）与影响、建议、决策输入；未跑迁移、未改安装脚本、未动真实数据；真实数据访问为只读。
- 可复现性：`dotnet build apps/desktop-avalonia/NewManga.sln` → **0 警告 / 0 错误（EXIT 0）**；`dotnet test tests/NewManga.App.Tests`（全量）→ **394/0/7（EXIT 0）**；`check.ps1 -TaskPath doc/tasks/REALUSE-DATA-SAFETY-6.md` → **PASS (2 warnings)（EXIT 0）**。
- 数据安全边界：无删除用户数据、无迁移、无 push、未改主工作区（详见 §8）。

**审批判断**：3 条 P2 分别是（R-001）关闭与进行中保存并发时新增镜像代码会抛未捕获 `NullReferenceException` 并跳过关闭时权威重读；（R-002）Canonical Evidence 的 sha256 pin 依赖 CRLF/LF，其中 1 条在本次 reviewed worktree 直接哈希即与 pin 不符；（R-003）AC1 测试证据文件缺 EXIT 码、负向对照为散文摘要。三者均不影响 AC1/AC2/AC3 的成立（已逐条复跑/复算），故不构成 P0/P1；按本仓库 Review 门槛可以批准集成，建议 DSH 把 R-001/R-002 作为集成前小修或紧随的后续项处置。

## 2. 审查范围与依据

- **被审对象**：`task/REALUSE-DATA-SAFETY-6` @ `0feff7a4c`（`0feff7a4cd926eb2f08b18246cc1f54974a90b48`）。
- **提交链**（本分支实际）：

| commit | 内容 |
|---|---|
| `fb5065013` | 实现（delivery_head）：3 个生产文件 + 1 个测试文件 + `verification/REALUSE-DATA-SAFETY-6/**` 6 个证据文件 |
| `b94dc3d86` | 文档与证据：任务卡 `in_review`、STATUS / REBASELINE_PLAN / TASK_LEDGER、handoff、`governance-check.txt` |
| `0330b0a38` | 任务卡 Canonical Evidence 一行（E-GOV-CHECK pin 到 `b94dc3d86`） |
| `c08a660e4` | handoff 交付链说明（不触代码/证据/任务卡） |
| `0feff7a4c` | merge `main@6cab0b083`（FEA 文档入库 + AD-003 引用修复；合并内容全部在 `doc/`） |

- **被审内容与 head 的关系**：`git diff fb5065013..0feff7a4c -- <4 个代码/测试文件>` 为空；`verification/REALUSE-DATA-SAFETY-6/` 相对 `fb5065013` 只多 `governance-check.txt`（`b94dc3d86` 加入）。即 reviewed_head 上的实现与证据与 delivery_head 一致，merge 未改动它们。
- **依据**：任务卡 `doc/tasks/REALUSE-DATA-SAFETY-6.md`、`doc/handoffs/REALUSE-DATA-SAFETY-6-handoff.md`、`verification/REALUSE-DATA-SAFETY-6/**` 全部 7 个文件、`git show fb5065013` 全量 diff、`HostController.SaveReadingProgressAsync` / `LoadReaderBookAsync`、`ImportDockViewModel`、`AppShellViewModel` 的关闭链、`src/bootstrap/core_service.py`、`src/infrastructure/resource_channel/render_preview.py`、`catalog_store.py`、`HostRuntime.cs`、`doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md` §3.2、`apps/desktop-avalonia/scripts/*`。
- **视角**：Architecture + Verification 两面均已执行（Standards/Spec 为可选视角，本次按任务卡 AC 原文直接核对，未单独启用）。

## 3. Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| R-001 | P2 | `apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Library/ReaderOverlayViewModel.cs:344-394`（`_isSaving` 早退 346-349；回调内解引用 `_book` 377-384；`CloseAsync` 274-285） | **关闭阅读浮层与进行中保存并发 → 未捕获 NullReferenceException，且关闭时权威重读被跳过。** 时序：翻页保存已在 Host 往返中（`_isSaving=true`）→ 用户点"返回（Esc）"→ `CloseAsync` 调 `SaveProgressAsync(isClosing:true)` 因 `_isSaving` 直接 return → `CloseAsync` 继续 `_book = null`、`Pages.Clear()` → 在途保存恢复后 `result.IsSaved` 为真，回调实参解引用 `_book.BookId/_book.ChapterId`（378-379）→ NRE；386 行 catch 只覆盖 `InvalidOperationException`/`SidecarException`，NRE 逃逸到被丢弃的 Task（`_ = GoToAsync(...)`），且 `OnReaderProgressSavedAsync(IsClosing)` 从未执行。可见后果：关闭后书架停在上一页的镜像值（MA-09 症状的一次性复现）+ 静默未观察异常；无数据损坏（Core 已提交） | 仓外副本 `...\tmp\safety6-review\race`：给 Fake 保存口加确定性 gate + 用例 `ReviewerRace_CloseWhileSaveInFlight_DoesNotThrow`。实际输出：`System.NullReferenceException`，堆栈 `ReaderOverlayViewModel.SaveProgressAsync(Boolean isClosing) ... ReaderOverlayViewModel.cs:line 377` ← `GoToAsync ... :line 308`，`失败: 1 / 总计: 1`，EXIT 1（副本已按 §7 说明打补丁，未触碰仓库） | 在 `await` 前把 `bookId/chapterId/pageNumber/pageCount` 落成局部值再回调；`CloseAsync` 在 `_isSaving` 时应等待在途保存或在其完成后补一次权威重读；回调分支加空值守卫，并把"保存失败"与"刷新失败"文案分开 | open |
| R-002 | P2 | `doc/tasks/REALUSE-DATA-SAFETY-6.md:101-113`（Canonical Evidence 表）；`verification/REALUSE-DATA-SAFETY-6/**`；`.gitattributes`（无本 Task 证据目录的 eol 规则） | **sha256 pin 的哈希基准是"作者工作树字节"，且 1 条在当前 reviewed worktree 即不可复现。** 11 条 pin 中：与当前 worktree 文件字节一致 10/11、与 git blob 一致 6/11；差异全部只是 CRLF↔LF（抽 6 个差异文件做 CRLF→LF 归一后哈希相等，内容无差异）。`E-GOV-CHECK` 的 pin `bc97d7a7…` 只在 blob（LF，2439 B）成立；当前 worktree 文件是 CRLF（2475 B，sha256 `5ca6e84b…`），直接 `Get-FileHash` 即不符。另 5 条（`ReaderOverlayViewModel.cs`、`LibraryViewModel.cs`、`FakeHostController.cs`、`ac1-…-test-log.txt`、`ac2-derived-realdata.json`）的 pin 只对 CRLF 工作树成立、对 blob 不成立。影响：新 checkout（`autocrlf=false` / CI Linux）上这些 pin 无法复现；仓库已有 GOV-EOL-PIN-1 / P19-UI-MANIFEST-VIEW-1 的 `.gitattributes … text eol=lf` 先例，本 Task 未加 | 逐条实测表见 §5；命令：`git show <commit>:<path> > blob` 后 `Get-FileHash`，并对工作树文件做同样哈希；对 6 个差异文件做了 EOL 归一后哈希比对（全 equal） | 在 `.gitattributes` 加 `verification/REALUSE-DATA-SAFETY-6/** text eol=lf`，并在集成前按 blob 口径重算/复核 pin；在任务卡注明 pin 的字节基准（blob bytes 或 worktree bytes） | open |
| R-003 | P2 | `verification/REALUSE-DATA-SAFETY-6/ac1-progress-refresh-test-log.txt:1-24` | **AC1 测试证据缺 EXIT 码/完整命令，负向对照是散文摘要而非原始输出。** 文件只有生成时间 + 环境头 + 两段"已通过"摘录；无 `exit_code=`、无完整命令与逐段输出；第 19-24 行负向对照标注"recorded earlier, same branch"，是手写结论。REVIEW 模板的证据纪律（Q-009）要求运行日志带 EXIT 与 shell/环境头、判别力 artefact 缺失即记 `NOT_RUN`，不得以散文代替。影响：canonical evidence 本身不能独立审计执行退出状态；本次 Reviewer 已复跑（5/5、394/0/7）并独立复现负向对照（3/5 失败），故交付结论成立，但证据强度弱于仓库口径 | 见 §6、§7 的真实输出；对照 `governance-check.txt`（同 Task 另一份证据，已带 `exit_code=1`，格式正确） | 重生成证据时把每段命令原文、输出尾部与 `exit_code=` 写入；可直接复用 `governance-check.txt` 的格式 | open |

> 没有 P0/P1。上述 3 条均属"边缘竞态 / 证据卫生"，不改变 AC1–AC3 的成立；R-001 若 DSH 认为"未捕获异常"应升级处置，可视为 P1 要求返修，但按本仓库既有 P 级先例（P1 = 用户可见能力整体失效或证据造假，P2 = 次要/边缘/证据卫生），本 Reviewer 判为 P2。

## 4. AC 逐项判定

### AC1（MA-09 阅读进度刷新）：**MET**

| 审查点 | 代码/测试事实 | 判定 |
|---|---|---|
| 保存后同动作镜像 | `LibraryViewModel.cs:73` 注入 `OnReaderProgressSavedAsync`；`ReaderOverlayViewModel.cs:375-384` 在 `await SaveReadingProgressAsync` 返回后同步回调；`LibraryViewModel.cs:1051-1066` 同章节时 `SetDetailProgress(FormatSavedProgress(...))`；`ReaderOverlayViewModel.cs:291-309`（`GoToAsync`）awaits 保存与回调后才返回 | 真实接线 ✓ |
| 关闭后权威重读 | `ReaderOverlayViewModel.cs:274-285` `CloseAsync` → `SaveProgressAsync(isClosing:true)`；`LibraryViewModel.cs:1053-1057` `IsClosing` → `LoadProgressAsync()`，后者走 `_controller.LoadReaderBookAsync`（生产 `HostController.cs:328-410` 的 Core 投影读，`SavedPageId/InitialPageIndex` 来自 Core 持久行，`ReaderLibrary.cs:39-43`） | 真实接线 ✓（窄竞态见 R-001） |
| 导入后补读 | `ImportDockViewModel.cs:198-238`：导入循环结束后（无论全成功/部分失败）调用 `await _afterImport()`；`LibraryViewModel.cs:789-801` `ReloadAfterImportAsync` 先重载页列表/计数，再 `await LoadProgressAsync()`；用例走真实 `ImportDock.OpenWithFilesAsync`（不是直接调私有方法） | 真实接线 ✓ |
| 只有 Core 真正提交（`IsSaved`）才刷新 | `IHostController.cs:84` `IsSaved => Status == ReaderProgressSaveStatus.Saved`；`ReaderOverlayViewModel.cs:375` 以 `result.IsSaved` 为唯一门；`HostController.cs:415-458` 生产保存只返回类型化结果（NotReady/ReadOnly/Failed/Saved） | ✓ |
| 类型化拒绝不伪造刷新 | `RefusedSave_DoesNotFabricateShelfRefresh`（`LibraryProgressRefreshTests.cs:204-219`）：ReadOnly 时书架文本保持"未开始阅读 · 共 8 页"、`ProgressRefreshes` 不变、`FakeProgressStore` 无条目 | ✓（`NotReady`/`Failed` 共用同一守卫但无独立用例，见 O-4） |
| 深链不串章 | `LibraryViewModel.cs:1059-1063` 仅在 `SelectedChapter.ChapterId == saved.ChapterId` 时镜像；`ReaderOnAnotherChapter_DoesNotRewriteTheSelectedChapterLine`（同文件 225-253）断言书架文本与刷新计数都不变 | ✓ |
| 测试有效性（负向对照） | 证据称"移除接线后 3/5 失败"；本 Reviewer 在仓外副本独立复现 **3 failed / 2 passed**（失败的正是 `CommittedSave_*`、`ClosingReader_*`、`Import_*`） | ✓（证据文件本身格式见 R-003） |
| 复跑 | 新增用例 5/5（见 §6） | ✓ |

边界（作者已在 `ac1-progress-refresh.md` §4 记录，本 Reviewer 认可为诚实边界）：webtoon 模式百分比口径（书架按页比、阅读器 webtoon 按滚动比例，`src/application/reading/service.py:207-214` 确认 Core 两种口径并存）；每翻一页用本地镜像而非逐次回读；深链阅读其它章节时不改本书架行。

### AC2（MA-19 `derived/` 全尺寸副本）：**MET（结论型，无代码改动）**

| 证据链 | 复核结果 |
|---|---|
| 代码面：resolve 把 managed 原件按确定性键发布进 derived | `core_service.py:3189-3252`（`handle_resolve_page_resource`；键 `page-original-{page_id}` 在 3234、`publish_original` 在 3248）；`render_preview.py:115-156`（`publish_original`，`ORIGINAL_REVISION="original"` 在 19）；catalog 命中带 `artifact_exists()` 探针（`render_preview.py:31`，`core_service.py:3236`） → 与结论一致 ✓ |
| Host 侧两个作用域根都支持，但只有 derived 有数据 | `HostRuntime.cs:511`（`ReadPageImageAsync`）、`:525-527`（`derived-read-only` / `managed-read-only` / 其余 `SCOPE_NOT_SERVABLE`）✓；catalog 无 managed 行（数据面见下）→ "缺的是 Core 侧登记与命名空间绑定，不是 Host 能力" 成立 ✓ |
| `preview_namespace` 把 catalog 身份绑定在 derived 根身份上 | `catalog_store.py:198` `initialize_namespace(catalog_db, derived_root)`；`core_service.py:5553-5583` `_ensure_preview_namespace`；启动加锁 `core_service.py:5757/5759/5798`；`dto.py:69` 允许的 scope classes；`catalog_store.py:128/726`。真实 `preview_namespace` 单行绑定真实 derived 路径（本 Reviewer 独立读出，见下）✓ |
| 真实数据面（只读） | 本 Reviewer 独立复核（只读枚举真实根 + 仓外 DB 副本 `mode=ro`）：managed **169 文件 / 100,434,899 B**；derived/pages **169 文件 / 100,434,899 B**；169/169 成对同尺寸、`missing_managed`/`missing_derived` 皆空；样本页 `48b5b58e…676c` managed 与 derived sha256 同为 `70c2fd73…e6eb07`、size 82,862；`catalog.sqlite.resource_catalog` **169 行全部 `derived-read-only`**；`derived/previews` 不存在；`.preview-lifecycle.lock` 315 B；`preview_namespace.derived_root` 指向真实 derived 根（volume 1485189147 / index 72620543991401102）→ 与 `ac2-derived-realdata.json` 逐项一致 ✓ |
| 约束面 | `doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md` §3.2 原文（`:61`）："**未实现新源读取前，不得以'消除双份'为由删除现有 `derived/` 或 managed 文件。**" ✓ |
| 结论充分性 | 删 derived 后，任何一次投影读都会对每页调用 resolve，从而按同键**全量重建**（`handle_get_reader_projection` 循环 `core_service.py:3268-3271`）→ "删副本省不到空间"成立 ✓ |
| 越权改代码 | branch diff `841cbdc4b..HEAD` 内 `src/**`、`scripts/**`、`tools/**` 零改动；AC2 只有两份证据文件 ✓ |

### AC3（MA-11 / MA-20 待裁决项）：**MET（严格零实施）**

| 审查点 | 复核结果 |
|---|---|
| 只出方案 | `ac3-options.md`：MA-11 A0（保持）/A1（只读封存）/A2（显式迁移灾备）/A3（以旧库为准，**不建议**）/A4（阻断旧壳写入）＋影响/可回滚性/建议；MA-20 M-1（默认隔离+实测断言，推荐）/M-2（二次确认）/M-3（仅文档化，不推荐）/M-4（验证强制隔离）＋影响；均给决策所需最小输入 ✓ |
| 事实基线可核 | `install.ps1:4` 默认真实 `%APPDATA%`；`:20` 不加 `-SkipBackup` 会向真实 `backups/` 写整根 zip；`install-verify.ps1` 末尾硬编码 `data_root_untouched=$true`（实测为常量断言）；`install-smoke.ps1` 每次调用带 `-SkipBackup`；`Coexistence.cs:33-34,57` 旧壳运行 → Host 只读；`core_service.py:5721-5737` 每次启动尝试 `migrate_legacy_layout` 且失败拒绝启动；`upgrade_legacy_layout.py:196-200` 只有真复制才写日志 ✓ |
| 零实施 | branch diff 无 `scripts/**`、`src/**`、`tools/**` 改动、无删除；真实数据根无 `logs/upgrade-legacy.log`、无 `.upgrade-legacy-staging`；`library.db` mtime 仍是 2026-10-30 11:02、`data/library.db` 仍是 2026-10-29 17:17（均早于本 Task 2026-11-01）；未执行安装/卸载/打包/备份/恢复 ✓ |
| 真实数据访问只读 | 枚举 + 仓外副本 `mode=ro` SQLite + 样本文件只读 sha256；本 Reviewer 独立复核无写入痕迹（唯一异常见 O-3，无法归因本 Task） ✓ |

## 5. 证据 pin 一致性核对

任务卡 Canonical Evidence 11 条；本 Reviewer 对每条同时计算"当前 worktree 文件字节"与"`git show <pin commit>:<path>` 的 blob 字节"的 sha256（`Get-FileHash`，blob 用 cmd 重定向保字节）：

| evidence_id | pin commit | pin sha256 | worktree 一致 | blob 一致 | 差异性质 |
|---|---|---|---|---|---|
| E-AC1-READER-VM | fb5065013 | `603ed15e…e865` | ✓ | ✗ | CRLF↔LF（归一后相等） |
| E-AC1-LIBRARY-VM | fb5065013 | `2b6f2525…66f6` | ✓ | ✗ | CRLF↔LF（归一后相等） |
| E-AC1-TEST | fb5065013 | `135de02c…60a2` | ✓ | ✓ | — |
| E-AC1-TEST-FAKE | fb5065013 | `6c63c2c5…4a11` | ✓ | ✗ | CRLF↔LF（归一后相等） |
| E-AC1-DOC | fb5065013 | `e913e2dd…66e8` | ✓ | ✓ | — |
| E-AC1-LOG | fb5065013 | `2eab8096…0a63c` | ✓ | ✗ | CRLF↔LF（归一后相等） |
| E-AC2-DOC | fb5065013 | `1edb35f1…7c47` | ✓ | ✓ | — |
| E-AC2-DATA | fb5065013 | `22f9793f…0ddc` | ✓ | ✗ | CRLF↔LF（归一后相等） |
| E-AC3-DOC | fb5065013 | `9c27d477…950b` | ✓ | ✓ | — |
| E-EVIDENCE-INDEX | fb5065013 | `d199f484…a3ff` | ✓ | ✓ | — |
| E-GOV-CHECK | b94dc3d86 | `bc97d7a7…592e` | ✗（worktree `5ca6e84b…`） | ✓ | worktree 为 CRLF（2475 B）、blob 为 LF（2439 B） |

- 汇总：**worktree 一致 10/11、blob 一致 6/11**；所有不符均为纯行尾差异（已对 6 个差异文件做 CRLF→LF 归一后的哈希比对，全部相等，内容无差异）。
- 唯一在 reviewed worktree 上"直接哈希即不符"的是 `E-GOV-CHECK`：pin 取的是 blob（LF）字节，而该 checkout 的文件是 CRLF。内容本身可用（本 Reviewer 已按 §6 复跑治理检查得到 PASS(2 warnings)）。
- 证据归属：7 个证据 blob 均仅出现在 `verification/REALUSE-DATA-SAFETY-6/` 路径（用 `git rev-list --objects --all` 反查，无跨任务复制——对照历史上 V11R-B-1 的复制证据问题，本 Task 未复现）。
- 结论：pin 数值与"作者生成时的文件字节"一致，**但 pin 的字节基准未固定、未做 eol pin**，属证据卫生问题（R-002），不构成内容不实。

## 6. 复跑验证（本 Reviewer 真实执行，worktree 内）

环境：Windows、`dotnet --version = 10.0.401`、worktree `G:\CODEX\New Manga.workspace\worktrees\REALUSE-DATA-SAFETY-6`、HEAD `0feff7a4c`（审查开始时 `git status --porcelain` 为空）。

| # | 命令 | 真实结果 | EXIT |
|---|---|---|---|
| 1 | `dotnet build apps/desktop-avalonia/NewManga.sln --nologo` | `已成功生成。0 个警告 0 个错误`（构建输出列出 12 个项目，全部生成成功） | **0** |
| 2 | `dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj --filter "FullyQualifiedName~LibraryProgressRefreshTests" --nologo -v q` | `已通过! - 失败: 0，通过: 5，已跳过: 0，总计: 5，持续时间: 64 ms` | **0** |
| 3 | `dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj --nologo -v q` | `已通过! - 失败: 0，通过: 394，已跳过: 7，总计: 401，持续时间: 54 s` | **0** |
| 4 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/REALUSE-DATA-SAFETY-6.md` | `Governance scope: 15 current documents; no historical directory scan.` / `WARN: 存在 7 个非终态 Task…` / `WARN: doc/REBASELINE_PLAN.md 已达到预算的 80%：6610 bytes / 58 lines` / `Governance check: PASS (2 warnings)` | **0** |

与任务卡/handoff 声称的一致性：构建 0/0 ✓、新增用例 5/5 ✓、全量 394/0/7（401）✓；治理检查在 merge 后由历史 FAIL(2 errors) 变为 **PASS(2 warnings)**（2 条 error 系 main 上 FEA 文档入库修复，见 O-2）。

## 7. 独立负向对照与竞态复现（仓外临时副本，未触碰仓库）

副本构造：`git -C <worktree> archive HEAD apps/desktop-avalonia | tar -x -C <tmp>`（tracked 文件、无 bin/obj）。所有改动只发生在 `G:\CODEX\New Manga.workspace\tmp\safety6-review\**`。

**(a) 副本基线**：过滤用例 **5/5 通过**（EXIT 0）——证明副本环境可用，排除"在副本里必挂"的环境偏差。

**(b) 负向对照（独立复现）**：仅把 `LibraryViewModel.cs:73` 的构造函数回调接线去掉（`new ReaderOverlayViewModel(controller, notify, OnReaderProgressSavedAsync)` → `new ReaderOverlayViewModel(controller, notify)`），其余不动：

```
[xUnit.net] NewManga.App.Tests.LibraryProgressRefreshTests.Import_RefreshesProgressLine_WithNewPageCount [FAIL]
[xUnit.net] NewManga.App.Tests.LibraryProgressRefreshTests.ClosingReader_ReReadsHostProjection_AndShelfShowsResumePage [FAIL]
[xUnit.net] NewManga.App.Tests.LibraryProgressRefreshTests.CommittedSave_RefreshesShelfDetail_AndShelfMatchesReader [FAIL]
失败!  - 失败: 3，通过: 2，已跳过: 0，总计: 5        EXIT 1
```

→ 与证据声称的"移除接线后 3/5 失败（另 2 例按设计仍通过：拒绝不伪造、深链不串章）"**一致**，测试确有判别力。

**(c) 竞态复现（对应 R-001）**：在独立副本给 Fake 保存口加确定性 gate（`SaveGate`），新增用例 `ReviewerRace_CloseWhileSaveInFlight_DoesNotThrow`：打开阅读 → `GoToAsync(4)` 进入被 gate 阻塞的保存 → `CloseAsync()`（因 `_isSaving` 早退）→ 放行 gate → 泵 Avalonia 消息：

```
失败 NewManga.App.Tests.LibraryProgressRefreshTests.ReviewerRace_CloseWhileSaveInFlight_DoesNotThrow
错误消息: System.NullReferenceException : Object reference not set to an instance of an object.
堆栈: at ReaderOverlayViewModel.SaveProgressAsync(Boolean isClosing) ... ReaderOverlayViewModel.cs:line 377
      at ReaderOverlayViewModel.GoToAsync(Int32 index) ... ReaderOverlayViewModel.cs:line 308
失败!  - 失败: 1，通过: 0，已跳过: 0，总计: 1        EXIT 1
```

→ R-001 为真实可复现缺陷（不是从代码推断）。副本补丁与日志只存在于仓外 tmp，不进入仓库。

## 8. 数据安全边界核查

- **无删除用户数据**：`git diff --diff-filter=D --name-status 841cbdc4b..HEAD` 为空；真实数据根文件数/字节与 `ac2-derived-realdata.json` 一致（managed 169 / derived pages 169），无缺失。
- **无迁移**：未运行 `migrate_legacy_layout`；真实根无 `logs/upgrade-legacy.log`、无 `.upgrade-legacy-staging`；`library.db` / `data/library.db` mtime 早于 Task 日期。
- **无 push**：`task/REALUSE-DATA-SAFETY-6` 无 upstream（`git branch -vv` 无 tracking）；`git branch -r --contains 0feff7a4c` 为空（本地已知远端引用无该提交）；本 Reviewer 未执行任何 fetch/push。
- **未改主工作区**：`G:\CODEX\New Manga` 在审查前后 `git status --porcelain` 均为空，HEAD `6cab0b083`（= 本分支 merge 的 main 侧）。本分支的文档提交（STATUS/PLAN/LEDGER 等）都在 worktree 分支上，未落到 main。
- **本 Reviewer 的写操作**：仓库内仅本文件；真实数据根只做只读枚举与样本 sha256；SQLite 只读连接只指向仓外副本（`...\tmp\REALUSE-DATA-SAFETY-6\dbcopy`），未在真实根创建 `-wal/-shm`。
- 观察：真实根 `logs/window-material.log` 在 `2026-10-31T17:09:04Z`（本地 2026-11-01 01:09）有一次追加（真实 UI 启动日志，见 O-3），任何数据文件 mtime 均未变；无法归因于本 Task 证据采集。

## 9. 独立性声明

- 本审查由 **Agent Teams 独立上下文子 agent `safety6-reviewer`** 执行（任务 task-3），**未参与** REALUSE-DATA-SAFETY-6 的实现、返修、证据生成或 handoff；与实现会话无共享上下文。
- 全程只读 `task/REALUSE-DATA-SAFETY-6` @ `0feff7a4c`；未修改任何代码、任务卡、STATUS、PLAN、LEDGER、证据文件；未 `git add/commit/checkout/stash/merge`，未 push。
- 仓库内唯一写入：`doc/reviews/REALUSE-DATA-SAFETY-6-review.md`（本文件，新建）。仓外写入仅限 `G:\CODEX\New Manga.workspace\tmp\safety6-review\`（副本/脚本/日志）。
- 所有 PASS/FAIL 结论均来自本 Reviewer 当次真实执行（§6/§7）；无法执行的项逐条列在 §10，未以散文代替。

## 10. NOT_RUN

| 项 | 原因 |
|---|---|
| 真机 UI 手工验收（打开阅读器→翻页→关闭→书架肉眼核对） | 只读审查，且需启动真实产品进程会写真实数据根日志/可能触 DB；不在 Review 授权范围 |
| 真实 Host/Core 的端到端进度往返 | 新增用例全部走 `FakeHostController`（`IHostController` seam），真实 `HostController`/Core 未在自动化内覆盖；属既有测试策略边界（O-4） |
| Release publish / 安装器真实流程（install/uninstall/backup/restore） | AC3 明确禁止实施；只核对脚本事实基线 |
| 在真实数据根上执行 SQLite 直连查询 | 为避免任何写风险，DB 查询全部在仓外副本（`mode=ro`）进行 |
| 验证 MA-11 / MA-20 方案的正确性/收益 | 属用户/DSH 裁决输入，不是本 Task 实施内容；Review 只核方案完备性与"零实施" |
| 验证 `task/REALUSE-DATA-SAFETY-6` 是否已 push 到远端（`git ls-remote` 实测） | 未做网络访问；以本地远端引用与无 upstream 判定"未 push"（§8） |
| 全量 401 用例中 7 条 skip 的逐条原因 | 本 Task 未改变 skip 集合；沿用仓库既有基线，未逐条复核 |
| 清理/删除仓外副本（negtl/race/dbcopy） | 由 DSH 在集成后按资源处置裁决；本 Reviewer 保留以便复核 |

## 11. 审查前后 git status

**审查前**（2026-11-01T01:0x，worktree HEAD `0feff7a4c`）：

```
$ git status --porcelain=v1
(空)
```

**审查后**（写入本报告后）：

```
$ git status --porcelain=v1
?? doc/reviews/REALUSE-DATA-SAFETY-6-review.md
```

除本报告外无新增/修改/删除；`bin/`、`obj/` 构建产物均被忽略，不进入 status。主工作区 `G:\CODEX\New Manga` 审查前后 `git status --porcelain` 均为空。

## 12. 观察与建议（非 finding）

- **O-1 关闭时权威重读的代价未量化**：`handle_get_reader_projection` 对每页调用 `handle_resolve_page_resource`，后者每次先 `managed_root_trust.read_bytes()` 读全文件（`core_service.py:3225`），投影里再对每页 `_reader_sha256`（`:3834-3843`）；169 页 ≈ 200 MB 读 + 100 MB 摘要。`CloseAsync` 在该重读完成前不置 `IsOpen=false`，故关闭按钮可能明显变慢。`ac1-progress-refresh.md` §2.4 已记录取舍（"一次投影读≈对 100 MB 做摘要"，方向正确但略低估：实际是 2 次全量读 + 1 次摘要）。建议集成时实测一次 close 延迟；若不可接受，另立 Task 增加轻量 `get_reader_progress` seam（本 Task 未改契约，属正确克制）。
- **O-2 任务卡"治理检查"与 reviewed_head 有历史差**：`doc/tasks/REALUSE-DATA-SAFETY-6.md:126-130` 记录的是 merge 前的 `FAIL (2 errors, 2 warnings)`（在其提交时点属实且有原文证据）；reviewed_head 复跑为 `PASS (2 warnings)`（2 条 error 已由 main 的 FEA 文档入库修复）。建议集成时在任务卡 Closeout/治理检查处补一行"merge main 后 PASS(2 warnings)"，避免后续读者误判。
- **O-3 真实根存在不可归因的外部日志写入**：`logs/window-material.log` 在 `2026-10-31T17:09:04Z` 追加（该文件由 `MainWindow.axaml.cs:158/889` 在产品 UI 启动时写）；DB/catalog/derived/managed 的 mtime 均未变。不改变 AC3 结论，但提示集成前确认没有并行的真实数据根写入者（例如其它会话启动真实产品）。
- **O-4 类型化拒绝覆盖与测试层边界**：`NotReady` / `Failed` 与 `ReadOnly` 共用 `result.IsSaved` 守卫（代码上等价安全），但只有 `ReadOnly` 有专门用例；新用例全部基于 Fake seam，未覆盖真实 Host。两者都不降低 AC1 判定，但建议后续补一条 `Failed` 用例，并在集成/发布验证时做一次真机进度核对。
- **O-5 未使用字段**：`ReaderProgressSavedEvent` 携带 `BookId` 与 `Result`，`LibraryViewModel.OnReaderProgressSavedAsync` 均未使用（只用 `ChapterId/PageNumber/PageCount/IsClosing`）。属预留字段，不影响正确性；若后续不需要，可在下一次触碰时精简。

## 13. 复审与集成说明

- 本 Review 对 `0feff7a4c` 有效；head 变化后本文件自动成为历史记录，不得当作对新 head 的批准。
- 建议 DSH 集成处置：① 按 §6 复跑结果与 §7 负向对照可接受 AC1 证据；② R-001 建议随集成前小修（改动面小：局部变量化 + `_isSaving` 时关闭仍需权威重读）或紧随另立小 Task，并在 Closeout 记录；③ R-002 建议在集成提交前加 `.gitattributes` eol 规则并重算 pin（或明确 pin 基准）；④ R-003 建议下次证据重生成时按 `governance-check.txt` 格式补齐 EXIT；⑤ MA-11 / MA-20 仍需用户/DSH 裁决（AC3 只出方案，本 Review 不代为裁决）。
- 剩余风险：R-001（窄竞态、无数据损坏）、R-002/R-003（证据可复现性与强度）、O-1（关闭时延未量化）、O-4（真机未覆盖）。
