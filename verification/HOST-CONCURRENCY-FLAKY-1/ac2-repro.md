# HOST-CONCURRENCY-FLAKY-1 AC2：受控复现结果

- head: `84b4a2456`
- 环境：`NEWMANGA_WORKSPACE_ROOT=G:\CODEX\New Manga.workspace`，通过 `apps/desktop-avalonia/scripts/test.ps1`
  完整流程（含 S4 fixture 生成、Core tile 合成、AC1/AC3 探针）运行
- 复现轮次：2
- 命令：`pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1`

## 结果：2/2 稳定复现

| 轮次 | EXIT | Host.Tests 失败 |
|---|---|---|
| 1 | 1 | 3（同 R87） |
| 2 | 1 | 3（同 R87） |

两次失败的**测试集合与顺序完全一致**：

```
GrantIssuerTests.Export_GrantRegisters_ThenCoreFailsTyped_OnMissingTranslatedPages
GrantIssuerTests.Import_IntoNewChapter_Executes_AndRegistersGrant
Fea11WatchHostRuntimeTests.Ready_ArmsWatcher_RealFileEventProducesHint_DisposeDisarms
```

## 关键结论：这**不是偶发 flaky**，是确定性触发

R87 的对比数据：

| 运行方式 | 失败 | 通过 | 跳过 | 总计 |
|---|---|---|---|---|
| `dotnet test Host.Tests.csproj`（裸环境） | **0** | 331 | 74 | 405 |
| `test.ps1`（完整环境） | **3** | 358 | 44 | 405 |

**两次 test.ps1 都失败，两次裸跑都通过 ⇒ 由环境差异确定性地触发，不是随机抖动。**

这个定性修正很重要：R88 建卡时写作「并发 flaky」，但 AC2 证明它**在真实 CI 流程下必然失败**。
所以它不是「偶尔让人烦」，而是「`test.ps1` 永远不会绿」的确定性障碍。

## 差异的来源（R87 已测，本轮复述）

`passed + skipped` 都是 405，但分布差 30：

- 裸环境：331 passed / **74 skipped**
- `test.ps1`：358 passed / **44 skipped**

`test.ps1:102-134` 设置的 fixture 变量让 30 个原本 self-skip 的测试实际执行：

```
NEWMANGA_S4_FIXTURES           (L109)
NEWMANGA_BOOK_FIXTURE_ROOT     (L114)
NEWMANGA_S4_REGION_FIXTURE     (L125)
NEWMANGA_MODELS_SIDECAR_DIR    (L130)
NEWMANGA_CORE_TILE_E2E         (L134)
NEWMANGA_EVIDENCE_DIR          (L83)
NEWMANGA_CORECLIENT_SIDECAR_DIR (L82)
```

⇒ 这些测试**并行**执行时，同进程内对 `SourceAccessRegistry` 的访问密度显著上升，
`WaitOne(0)` 的零超时窗口被命中（AC3 已定位到 `:344`/`:349`/`:71`）。

## AC2 结论

**AC2 MET**：失败在 `test.ps1` 环境下 100% 复现（2/2），测试集合固定。

**对 AC4 的影响**：既有「修（`WaitOne(boundedTimeout)` + 有界重试）」的修复方向**必须做**，
不能只「登记为已知限制」—— 因为登记为限制等于承认 `test.ps1` 永久红。
如果 AC4 决定不做产品代码变更，则必须在 Release Gate 层面明确接受
「`test.ps1` 走 Host.Tests 会红」这一后果，并把它写进 HUMAN-REQUIRED 或已知限制清单。

## 证据

- `repro-1.log` / `repro-2.log`（各含完整 test.ps1 输出与失败列表）
