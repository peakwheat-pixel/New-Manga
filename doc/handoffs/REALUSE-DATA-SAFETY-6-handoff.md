# REALUSE-DATA-SAFETY-6 Handoff

- Task：[REALUSE-DATA-SAFETY-6](../tasks/REALUSE-DATA-SAFETY-6.md)
- 分支：`task/REALUSE-DATA-SAFETY-6`（**不合并 main、不 push 远端**）
- Worktree：`G:/CODEX/New Manga.workspace/worktrees/REALUSE-DATA-SAFETY-6`（保留给 Review / 集成）
- 基线：`main@841cbdc4b`
- 实现提交（delivery_head）：`fb5065013`
- 文档与证据提交：本文件所在提交（其直接父提交为 `fb5065013`）；分支 tip 以 `git rev-parse HEAD` 为准
- 状态：`in_review`，owner `dsh-lead`，reviewer 未指派

## 1. 完成项

| AC | 结论 | 交付物 |
|---|---|---|
| AC1（MA-09 进度刷新） | **MET**：保存后书架与阅读器同一次用户动作内一致；关闭浮层改为 Host 投影重读（权威值）；导入后刷新进度（页数分母不陈旧）；类型化拒绝不伪造 | `ReaderOverlayViewModel.cs`、`LibraryViewModel.cs`、新增 `LibraryProgressRefreshTests.cs`、`verification/.../ac1-*.md/.txt` |
| AC2（MA-19 derived 冗余） | **MET（结论型，无代码改动）**：derived 全尺寸副本**现阶段必需**；给出代码路径 + 真实数据逐字节印证 + 未来移除的前置条件 | `verification/.../ac2-derived-conclusion.md`、`ac2-derived-realdata.json` |
| AC3（MA-11 / MA-20 待裁决项） | **MET（仅方案）**：MA-11 五选（A0 保持 / A1 只读封存 / A2 显式迁移灾备 / A3 以旧库为准不建议 / A4 阻断旧壳写入），MA-20 四选（M-1 默认隔离+实测断言 / M-2 二次确认 / M-3 仅文档化 / M-4 验证强制隔离），附影响与建议；**未实施** | `verification/.../ac3-options.md` |

### AC1 关键实现（3 个生产文件 + 1 个测试支撑）

1. `ReaderOverlayViewModel`：`ReaderProgressSavedEvent` + 可选回调 `progressSaved`；**只有 `IsSaved` 才回调**；`CloseAsync()` → `SaveProgressAsync(isClosing: true)`；新增 `LastSaveResult`。
2. `LibraryViewModel`：注入回调；`OnReaderProgressSavedAsync`（同章节镜像 / 关闭时重读投影）；`FormatSavedProgress` 单一格式化器；`SetDetailProgress`（写值 + `ProgressRefreshes++` + `PropertyChanged`）；`ReloadAfterImportAsync()` 补 `LoadProgressAsync()`；深链到其它章节不改写本书架行。
3. `FakeHostController`：新增 `ReaderLoadCount`（证明关闭/导入路径确实发生一次真实 Host 投影读）。

## 2. 测试与检查结果（真实运行，未伪造）

```powershell
cd apps/desktop-avalonia
dotnet build NewManga.sln -v q --nologo
dotnet test tests/NewManga.App.Tests/NewManga.App.Tests.csproj `
  --filter "FullyQualifiedName~LibraryProgressRefreshTests" --nologo -v q
dotnet test tests/NewManga.App.Tests/NewManga.App.Tests.csproj --nologo -v q
```

| 命令 | 结果 |
|---|---|
| `dotnet build NewManga.sln` | **PASS**：0 警告 / 0 错误 |
| 新增 `LibraryProgressRefreshTests` | **PASS 5/5** |
| 全量 `NewManga.App.Tests` | **PASS**：394 通过 / 0 失败 / 7 跳过（共 401） |
| 负向对照（临时移除回调接线后重跑） | **3/5 失败**（同动作刷新、关闭后重读、导入刷新），另 2 例按设计仍通过 → 证明测试确实覆盖"刷新已接线" |

原始日志：[`verification/REALUSE-DATA-SAFETY-6/ac1-progress-refresh-test-log.txt`](../../verification/REALUSE-DATA-SAFETY-6/ac1-progress-refresh-test-log.txt)

### 治理检查（**FAIL，全部为既有债务；未伪造 PASS**）

```powershell
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/REALUSE-DATA-SAFETY-6.md
# Governance check: FAIL (2 errors, 2 warnings)
```

- 2 条 error（**与本 Task 无关的既有失效引用**）：
  - `doc\AD-003_REFERENCED_SOURCE_ARCHITECTURE.md → design/FLUENT_MANGA_USER_CONCEPT_2026-10-30.md`
  - `doc\AD-003_REFERENCED_SOURCE_ARCHITECTURE.md → design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md`
- 既有证明：`git ls-tree -r --name-only 841cbdc4b | Select-String FLUENT` → **空**（基线提交不含这两个文件）；它们只存在于主工作区且**未提交**（`git -C 'G:\CODEX\New Manga' status --short -- doc/design` → 两个 `??`）。因此任何干净 worktree 上都会红，修复面是 `doc/AD-003_*.md` / `doc/design/`，**不在本 Task allowed_paths**，未擅自修改。
- 2 条 warning：既有"7 个非终态 Task"提示、`doc/REBASELINE_PLAN.md` 已达预算 80%（既有债务）。
- **与改动前基线逐字一致**（同样 2 errors / 2 warnings），本 Task 没有新增 finding。原始对照见 [`verification/REALUSE-DATA-SAFETY-6/governance-check.txt`](../../verification/REALUSE-DATA-SAFETY-6/governance-check.txt)。

## 3. 未完成项（交 DSH / 后续）

1. **独立 Review 未做**：本 Task 只交付实现与证据；`reviewer` 仍为 null，需 DSH 指派上下文独立的审查者（不得由本会话自审）。
2. **AC3 裁决未做**：MA-11 走 A0/A1/A2/A4 哪条、MA-20 走 M-1/M-2/M-3/M-4 哪条，**必须由用户或 DSH 裁决**；本 Task 未运行迁移、未改部署脚本。
3. **AC2 的"真正去掉副本"未做**：属资源通道契约演进（`G-CONTRACT` OPEN），需要另立 Task；本 Task 只给结论与前置条件。
4. **集成与合并未做**：不合并 main、不 push。
5. **`resource_closeout_status` 仍为 `pending`**：worktree 与仓外临时目录的最终处置在集成后由 DSH 决定（本 Task 未删除任何东西）。

## 4. 风险与已知边界

| 风险/边界 | 说明 | 缓解 |
|---|---|---|
| 每翻一页的进度是"本地镜像"，不是每次回读 Host | 为避开"每翻一页对整章每页做 resolve + sha256"的性能回归；关闭浮层与导入各做一次权威重读 | 已在 `ac1-progress-refresh.md` §2.4 / §4 记录；若要求逐次权威，需先改 Core 投影成本 |
| webtoon 模式百分比口径不同 | 书架百分比按页码/总页数；阅读器 webtoon 显示滚动比例（Core 侧两种口径本来并存） | 测试用分页模式做逐字符一致断言；webtoon 只保证页码一致 |
| 深链阅读其它章节时不刷新书架行 | 刻意的隔离：书架行描述的是当前选中章节 | 有专门用例 `ReaderOnAnotherChapter_DoesNotRewriteTheSelectedChapterLine` |
| 治理检查整体仍 FAIL | 既有失效引用（AD-003 → 未提交的设计文档） | 已记录证据与位置；修复需另立 Task（改 `doc/AD-003` 或提交 design 文档），不在本 Task 范围 |
| 真实数据触碰风险 | 本 Task 全程只读真实数据根；仓外 DB 副本含用户数据 | 副本在 `G:/CODEX/New Manga.workspace/tmp/REALUSE-DATA-SAFETY-6/`（未入 git），可随时删除 |
| MA-11 旧根仍可被旧壳写入 | 双库分叉风险未消除 | 见 `ac3-options.md` 的 A1/A4，等裁决 |

## 5. 下一步（可直接转发的指令）

1. **DSH**：给 `REALUSE-DATA-SAFETY-6` 指派上下文独立的 Review（只读 `task/REALUSE-DATA-SAFETY-6`，重点看 AC1 的三条刷新路径是否真实、AC2 结论的证据链、AC3 是否越界实施）；同时把 MA-11/MA-20 的选项提交用户裁决。
2. **Review 关注点（建议）**：
   - `LibraryProgressRefreshTests` 是否真的会在"接线被移除"时失败（负向对照已记录，可复跑）；
   - `OnReaderProgressSavedAsync` 的章节隔离与"拒绝不刷新"是否覆盖所有类型化失败；
   - AC2 的"必须保留"是否与 `HostRuntime.cs:523-528`（本可读 managed 根）冲突——结论已说明差的是 catalog 登记 + 命名空间绑定，不是 Host 能力；
   - AC3 是否严格只出方案（`ac3-options.md`，代码零改动）。
3. **集成（集成前检查）**：`git diff 841cbdc4b..fb5065013` 只含 3 个生产文件 + 1 个测试文件 + `verification/REALUSE-DATA-SAFETY-6/**`；文档提交只含任务卡、STATUS、REBASELINE_PLAN、TASK_LEDGER、本 handoff 与治理检查证据。

## 6. 证据清单

| 文件 | 内容 |
|---|---|
| `verification/REALUSE-DATA-SAFETY-6/README.md` | 证据索引与复现步骤 |
| `verification/REALUSE-DATA-SAFETY-6/ac1-progress-refresh.md` | AC1 根因/实现/测试矩阵/边界 |
| `verification/REALUSE-DATA-SAFETY-6/ac1-progress-refresh-test-log.txt` | AC1 测试原始输出 + 负向对照 |
| `verification/REALUSE-DATA-SAFETY-6/ac2-derived-conclusion.md` | AC2 结论与代码/数据证据链 |
| `verification/REALUSE-DATA-SAFETY-6/ac2-derived-realdata.json` | AC2 真实数据只读盘点原始输出 |
| `verification/REALUSE-DATA-SAFETY-6/ac3-options.md` | AC3 MA-11/MA-20 方案与影响 |
| `verification/REALUSE-DATA-SAFETY-6/governance-check.txt` | 治理检查原文 + 既有债务证明 |

commit / sha256 pin 见任务卡 `Canonical Evidence` 表。
