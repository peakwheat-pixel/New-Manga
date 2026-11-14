# SIDECAR-REBUILD-1 证据：E-2 根因已消除，但产生 13 个待归因失败

卡面：`doc/tasks/SIDECAR-REBUILD-1.md`。基线 `6ad457c62`。**状态：`in_progress`（未收口）**。

## 1. AC1 构建环境：成功

在 `G:\CODEX\New Manga.workspace\task-envs\m2ac5-build` 建 venv，用 **`-i https://pypi.org/simple`** 安装
`packaging/m2ac5/requirements-build.txt` 的**全部钉死版本**，逐个成功：

| 包 | 钉死版本 | 实际安装 |
|---|---|---|
| pyinstaller | 6.22.3 | **6.22.3** ✅ |
| torch | 2.14.0 | **2.14.0**（cp314 wheel）✅ |
| torchvision | 0.29.0 | **0.29.0** ✅ |
| transformers | 5.17.0 | **5.17.0** ✅ |
| python-doctr | 1.1.0 | **1.1.0** ✅ |
| safetensors | 0.8.0 | **0.8.0** ✅ |
| onnxruntime-directml | 1.24.4 | **1.24.4** ✅ |

完整清单见 `pip-freeze.txt`（63 个包）。

> **这彻底推翻了我此前"PyPI 不可达"的结论**（`RELEASE-PACKAGE-PROBE-1` r1 已指出，本卡实证）：
> 默认镜像缺包，但 `pypi.org` 直连**全套可装**，包括 2 GB 级 torch。

## 2. AC2 PyInstaller 构建：**成功**

```
Build complete! The results are available in: apps\desktop-avalonia\build\sidecar\core-sidecar
closure assertion: core_service carries ONNX Runtime onnxruntime, PIL.Image, numpy (928 pure modules, torch-free)
  + extensions onnxruntime_pybind11_state.pyd, DirectML.dll
closure assertion: sfx_detect_probe PYZ carries onnxruntime (687 pure modules) + extensions ..., DirectML.dll
build_sidecar: verified 0 shadowing ICU binaries across bundle layout (fail-closed guard satisfied)
build_sidecar: manga detector ONNX bundled (rtdetr-v2-fixed.onnx, sha256 verified)
build_sidecar: manga-ocr ONNX bundled (encoder/decoder/vocab, sha256 verified)
```

产物：`apps/desktop-avalonia/build/sidecar/core-sidecar/core-sidecar/`（**753 MB**，git-ignored），
5 个 exe（`core_service`/`host_bridge`/`catalog_loader`/`acceptance_bridge`/`sfx_detect_probe`，均 0.40 MB bootloader）
+ 3 个 ONNX（detector 164 MB、ocr encoder 328 MB / decoder 112 MB）。

**最后一步失败并退出 1**：

```
sfx weights file missing: G:\CODEX\New Manga.workspace\task-envs\M2-SFX-DETECT\weights-v2b\yolo11s-seg.onnx
(place the pinned v2b ONNX export there — local-release:sfx-train-v2/v2b — or rebuild with -SkipWeights)
```

**性质**：`yolo11s-seg.onnx`（SFX 检测权重）在全工作区**不存在**（已递归搜索）。它是训练产物，
不是可从 PyPI 获取的第三方包 ⇒ **属于 goal 定义里"需要用户提供不可替代的实物（模型文件）"**。
它只影响 `sfx_detect_probe`，**不影响 core_service 的命令面**（见 §3）。

新 `core_service.exe` 能正常启动：`[core.schema] applied 7 migration(s) up to v14`，
并对缺失的 SFX 权重**优雅降级**（`PROVIDER_NOT_CONFIGURED` fail-closed）。

## 3. AC3 命令面核对：**E-2 根因确已消除**

用新 sidecar 跑 "frozen/old Core" 前提的测试，`Assert.DoesNotContain` 失败并**打印出实际 capabilities**：

```
Collection: [..., "source.read.run/1", "source.reattest/1",
             "library.delete.preview/1", "library.trash.read/1", "library.trash.write/1", ...]
```

⇒ **新 sidecar 宣告了 FEA-12 的 delete/trash 三条能力**，而旧 sidecar（2026-10-23）没有。
这正是 E-2 的核心：**新命令面已追上当前 head**。

## 4. AC4 skip 下降实测：大幅下降

| 项目 | 旧 sidecar（基线） | **新 sidecar** | 变化 |
|---|---|---|---|
| `NewManga.CoreClient.Tests` | 186 / 0 / **26** / 212 | **208 / 4 / 0** / 212 | skip **26 → 0**，pass +22 |
| `NewManga.Host.Tests` | 321 / 0 / **74** / 395 | **342 / 9 / 44** / 395 | skip **74 → 44**（-30），pass +21 |
| 合计 | 507 / 0 / 100 | **550 / 13 / 44** | skip **-56**，pass **+43**，**新增 13 失败** |

## 5. **13 个失败（未归因完成，不得当作已解决）**

### 5.1 CoreClient 4 个 —— 性质清楚："Frozen Core" 前提过期

```
CommandIntegrationTests.Fea12Core_DeleteTrashCapabilityProbe_OldCoreFailsClosedBeforeAnyCommandFrame
CommandIntegrationTests.Fea12NewCommands_FrozenCoreFailsClosedWithTypedError
CommandWiringB2Tests.B2Commands_ExecuteAgainstFrozenCore
CommandWiringB1Tests.B1Commands_ExecuteAgainstFrozenCore
```

这四个测试**明确以"sidecar 是旧的"为前提**（断言 Core**不**宣告 delete/trash、命令**不**被识别）。
新 sidecar 具备这些能力后，前提消失 ⇒ 失败是**预期内的契约变化**，不是回归。
但**不得**简单删除：它们守的是 `CORE_CAPABILITY_MISSING` fail-closed 语义，需改为**显式模拟旧 capabilities**。

### 5.2 Host 9 个 —— **归因未完成，至少 1 个是数据层真实差异**

```
HostRuntimeIntegrationTests.ReadOnlyUntilParity_Ready_WithBothSidecars_AndWriteBlocked
GrantIssuerTests.Export_GrantRegisters_ThenCoreFailsTyped_OnMissingTranslatedPages
GrantIssuerTests.Import_IntoNewChapter_Executes_AndRegistersGrant
HostReaderChaptersIntegrationTests.ListChapters_MatchesReaderProjection      <- Assert.NotEmpty: 集合为空
HostReaderProgressIntegrationTests.SaveReadingProgress_PersistsAcrossHostRestart_AndResumes
HostReaderProgressIntegrationTests.SaveReadingProgress_UnknownPage_IsTypedCoreRejection
Fea11WatchHostRuntimeTests.Ready_ArmsWatcher_RealFileEventProducesHint_DisposeDisarms
HostRegionWorkbenchIntegrationTests.RegionWrites_ReadOnlyHost_AreTypedRefusals_WithZeroCoreFrames
HostRegionWorkbenchIntegrationTests.RegionReadWriteFace_ExecutesAgainstFrozenCore_AndProjectsOverlayGeometry
```

其中 `ListChapters_MatchesReaderProjection` 的失败是 **`Assert.NotEmpty() Failure: Collection was empty`** ——
这是**数据/夹具层面**的差异（schema 升到 v14 后，fixture 导入的章节读不出来），**不能**归为"前提过期"。
其余 8 个的归因**未做**。

**⇒ 本卡不得收口为 done。** E-2 的**根因**（sidecar 过期）已消除，但**新 sidecar 引入了 13 个失败**，
其中至少 1 个指向真实的数据兼容问题。这些必须先归因、再决定处置（改测试前提 / 修 fixture / 修实现）。

## 6. 本卡自身的边界

- **未**提交任何二进制；新 sidecar 在 `build/`（git-ignored）与 workspace。
- **未**声称 E-2 已完全解决 —— 只能说"根因消除、skip 降 56、但同时暴露 13 个失败"。
- **未**跑 App.Tests 的 7 个 sidecar 测试（时间原因）。
- **未**用新 sidecar 重跑 publish 冒烟（条件 4 的下一步）。
- SFX 权重缺失 → 该 probe 永远 `PROVIDER_NOT_CONFIGURED`，需用户提供 `yolo11s-seg.onnx`。
## 7. 独立直连探测：新 sidecar **本身完全正常**（关键诊断）

为排除"新 sidecar 自身有问题"，写了 `probe_core.py`（在 workspace）直接以 NDJSON 与
`build/sidecar/core-sidecar/core-sidecar/core_service.exe` 通信：

```
=== core.ping ===
{"protocol":"new-manga.core","version":{"major":2,"minor":3},"request_id":"req-1",
 "result":{"status":"ready","protocol_version":{"major":2,"minor":3},
 "capabilities":["library.list_books","source.read/1","source.resolve-secret/1","source.read.run/1",
 "source.reattest/1","library.delete.preview/1","library.trash.read/1","library.trash.write/1",
 "source.sync.scan/1","source.sync.plan/1","source.sync.apply/1","source.sync.relink/1",
 "source.sync.repoint/1","source.sync.resync/1","source.sync.operation/1",
 "source.sync.enumerate/1","source.sync.plan-materialization/1"]},"error":null}

=== ListBooks (minor=3) ===
{"protocol":"new-manga.core","version":{"major":2,"minor":3},"request_id":"req-2",
 "result":[],"error":null}
```

**结论**：

1. 新 sidecar **协议正常**（`status=ready`、`2.3`）、**`ListBooks` 返回合法空数组**（不是 `null`、不是错误对象）。
2. capabilities 共 **17 条**，**含 `library.delete.preview/1`、`library.trash.read/1`、`library.trash.write/1`**
   ⇒ E-2 的根因（缺新命令能力）**确已消除**。
3. ⇒ **13 个失败不是 sidecar 造成的**，而在**测试夹具 / 协议配置 / 数据准备**这一层。这是把问题范围
   从"sidecar 有问题"缩小到"测试侧适配"的关键一步。

（注意：我第一版探测脚本把 protocol 名写成 `newmanga.core`，得到 `PROTOCOL_VERSION_UNSUPPORTED`；
正确值是 **`new-manga.core`**。这个错误也说明：**协议名写错时的表现是"版本不支持"，不是"列表不是数组"**。）

## 8. 因此 13 个失败的归因方向（下一轮）

- `ListBooks result is not an array`（`WritePolicyTests.DefaultStart_IsReadWrite_AndCanCreateBook`）：
  既然直连返回 `[]`，C# 侧拿到非数组的最可能原因是**它连的不是这个 sidecar**（夹具路径/环境变量没生效）
  或**它走的是另一个通道**。需核 `WritePolicyTests` 的 sidecar 启动参数。
- "集合为空" 类（`ListChapters` / `ConcurrentChapterAndProjectionReads` / `SaveReadingProgress` ×2）：
  测试创建了 book/chapter 但列表读不到 ⇒ 可能**数据根不一致**（夹具用 A 的数据根，sidecar 写 B）。
- `KeyNotFoundException`（`GrantIssuerTests` ×2）：响应里缺某个字段名，需核具体哪一帧。
- `SOURCE_REGISTRY_BUSY`（`Fea11WatchHostRuntimeTests`）：疑似**并发/残留锁**，与 sidecar 版本无关。
- `Assert.Equal Expected:8 Actual:0`（`RegionWrites_ReadOnlyHost...`）：需核这两处 8 的含义。

**⇒ 本卡仍不得收口为 done**：归因方向已明确，但逐项核实未完成。
## 9. 第二轮诊断：数据根传递与 namespace（把 13 个失败进一步收窄）

### 9.1 `--data-root` 参数**从来就不被支持**（新旧 sidecar 都不认）

| 调用方式 | 新 sidecar | 旧 sidecar |
|---|---|---|
| `--data-root <path>`（空格） | 忽略 → 打开**默认库**（v14，0 本书） | 忽略 → 打开默认库，报 `schema v14 is newer than this application knows (v6)` |
| `--data-root=<path>`（等号） | 同样忽略 | — |
| **`NEWMANGA_DATA_ROOT=<path>`** | ✅ **生效**：读到 fixture 的 1 本书，日志 `applied 8 migration(s) up to v14` | — |

**结论**：`app.py:20` 的文档（"可用 `--data-root` 或环境变量"）与实际不符 —— **CLI 参数被静默忽略**。

### 9.2 Host 侧传参是**正确的**

`CoreServiceClient.cs:499`：`["NEWMANGA_DATA_ROOT"] = options.DataRoot` —— 用的是**环境变量**，
与我验证成功的路径一致。`HostFixture.SidecarDirectory` 也确实读 `NEWMANGA_CORECLIENT_SIDECAR_DIR`（我设置的变量生效）。

**因此 13 个失败既不是"sidecar 坏了"，也不是"数据根传错"。**

### 9.3 剩下的怀疑集中在 **namespace 隔离**

用环境变量打开 fixture 副本时，sidecar stderr 出现：

```
[core.namespace] data root identity changed (preview namespace unavailable:
  namespace binding identity mismatch); re-bound preview namespace: derived_root=...
```

即：**每换一个 data root，sidecar 会重新绑定 namespace**。13 个 Host 测试**并行**、各自不同 dataRoot、
且 `HostOptions.ParityReached=true` —— 这条 re-bind 路径很可能就是失败来源（例如并发 re-bind 竞争、
或 re-bind 后读的是 `derived` 根而非传入根）。

**这一步把 13 个失败从"未知"收窄到"namespace 隔离/re-bind 路径"**，是下一轮的直接入口。

### 9.4 尚未验证

- 单线程（`-m:1` 或 xunit 并行度 1）跑那 13 个测试是否还失败 —— 若单线程全绿，则确认是并发/namespace 竞争。
- `HostOptions.ParityReached` 与 namespace 的关系。
- `derived_root` 是否被用于读数据。
## 10. 第三轮诊断：失败是**测试间交互**，不是并行、不是 fixture 污染、不是 namespace

### 10.1 决定性对照

| 运行方式 | 结果 |
|---|---|
| **单独**跑 `HostReaderChaptersIntegrationTests.ListChapters_MatchesReaderProjection` | **PASSED**（1/1） |
| **连跑** `HostReaderChaptersIntegrationTests` + `HostReaderProgressIntegrationTests`（跨 2 个 class） | **4 failed / 1 passed** |

⇒ 同一测试**单独跑绿、连跑红** ⇒ 这是**测试之间的交互**，不是该测试或 sidecar 本身的缺陷。

### 10.2 逐项排除（都有实证）

| 假设 | 结论 | 证据 |
|---|---|---|
| xunit 并行导致 | **排除** | 两个测试项目都已 `[assembly: Xunit.CollectionBehavior(DisableTestParallelization = true)]` |
| 残留 sidecar 进程 | **排除** | 连跑后 `Get-Process core_service` **为空** |
| namespace re-bind 导致 | **排除** | `_ensure_preview_namespace` 只处理 **preview/derived catalog**（`core_service.py:8435-8473`），与 `library.db` 的 books 读取无关 |
| fixture **源**被测试改脏 | **排除** | 源仍是 `schema_version=6`、`books=1`、`chapters=1`；源目录出现的 `library.db-shm/-wal` 时间戳（3:27/3:32）对应的是**我自己的只读 probe**（`sqlite3 mode=ro` 也会建 shm），不是测试 |
| `--data-root` 传参 | **排除** | Host 用 `NEWMANGA_DATA_ROOT` 环境变量（`CoreServiceClient.cs:499`），我实测该通道能正确读到 fixture 的 1 本书 |

### 10.3 因此剩下的范围

失败表现为 `Assert.Single/NotEmpty` 收到空集合（即 sidecar 的 `ListBooks` 返回 `[]`），
且**只在前面的测试跑过之后出现**。剩下两种可能：

1. **共享的全局 `derived`/namespace 状态**被前一个测试改写，导致后续 sidecar 打开 preview 命名空间时
   走了不同分支（虽然理论上不影响 books，但需实证）；
2. **sidecar 启动在连续运行时更容易失败**（例如 753 MB bundle 连续解压/加载、或某个全局 lock 被前进程
   短暂占用），导致该次 session 没真正 ready —— 但测试断言的是空集合而非 `IsReady`，所以**未排除
   "session 起来了但读的是空库"**。

### 10.4 下一步（需要日志证据）

`HostFixture.EvidenceDirectory` 指向 `G:\CODEX\New Manga.workspace\FEA-09-UI-1\...` 一类路径
（旧日志在 3:19–3:24，**本轮 3:32+ 的测试日志没找到**）。下一轮必须先**定位当次测试的 `core_service.stderr.log`**，
看它打开的是哪个 data root、迁移了什么、`ListBooks` 实际查了什么 —— 只有这份日志能区分 10.3 的两种可能。

**现状**：`E2-FALLOUT-TRIAGE-1` 未完成；本卡仍 `in_progress`。
## 11. 第四轮诊断：**sidecar 侧完全正常**，失败在客户端/断言层

用 `NEWMANGA_EVIDENCE_DIR` 指定 evidence 目录后，成功抓到**当次**两个测试的 `core_service.stderr.log`：

**`reader-chapters-list`（该测试单独跑时通过）**：
```
[core.schema] applied 8 migration(s) up to v14; schema bootstrap is the only write a read-only
              session performs (user rows and managed originals are never modified)
[core.backup] automatic backup created: 136615b4... (4023097 bytes, verified=True,
              first writable start with an existing library)
[core.derived_gc] orphan_files_removed=0 dead_rows_removed=0
```

**`reader-chapters-concurrent`（该测试失败）**：
```
[core.schema] applied 8 migration(s) up to v14; ...
[core.backup] automatic backup created: 6fbea9d6... (4023108 bytes, verified=True, ...)
[core.derived_gc] orphan_files_removed=0 dead_rows_removed=0
```

### 结论

两次 sidecar 启动**都正常**：

1. 都打开了**各自**的 dataRoot（日志里的 weights 探测路径含
   `newmanga-host-runtime-tests\reader-chapters-list-1a51c65dbc` / `…-concurrent-d4264dc387`）；
2. 都成功把 fixture 的 **v6 迁移到 v14**（`applied 8 migration(s)`）；
3. 都成功做了首次备份（4 MB，`verified=True`）；
4. **没有任何 error/exception 行**。

⇒ **sidecar 没有读错库、没有迁移失败、没有 namespace 问题**。失败发生在 **C# 客户端 / 测试断言**这一侧。

### 这把范围进一步收窄到

- 为什么 `ListBooksAsync` 在连续运行时拿到空列表（sidecar 日志显示它正常起来了）；
- `WritePolicyTests` 的 `ListBooks result is not an array` 是**明确的解析失败**，与"空列表"是**两种不同症状**，
  说明 C# 侧收到的响应在连续运行时**结构不同**（值得直接抓 wire 帧）；
- `EnableWireEvidence = true` 已开启 —— 下一轮应直接读 **wire 证据文件**，看那两次 `ListBooks`
  的请求/响应原文，这是唯一还没看的决定性证据。

### 已入库证据

- `core_service.stderr.reader-chapters-list.log`
- `core_service.stderr.reader-chapters-concurrent.log`
## 12. 第五轮诊断（决定性）：wire 帧证明 **sidecar 返回正确的数据**，失败在 C# 客户端

### 12.1 两个 session 的帧对比

| session | 帧数 | 命令 |
|---|---|---|
| `reader-chapters-list`（**通过**） | 6 | `core.ping`×3、`OpenHostSession`、`ListBooks`、`list_chapters` |
| `reader-chapters-concurrent`（**失败**） | 19 | `core.ping`×3、`OpenHostSession`、`source_list_scan_targets`、`ListBooks`、**`list_chapters`×7**、**`GetReaderProjection`×6** |

失败的那个正是 `ConcurrentChapterAndProjectionReads_AreSerialized` —— 它**故意**发 1+6 次 `list_chapters` 与 6 次
`GetReaderProjection` 来验证"读 I/O 必须串行化"。**`errors: {}` —— 所有响应都没有 error。**

### 12.2 关键：两者的 `ListBooks` 响应**都返回了那本书**

```json
// FAIL session 的 ListBooks 响应（request_id req-6）
{"protocol":"new-manga.core","version":{"major":2,"minor":3},"request_id":"req-6",
 "result":[{"book_id":"14340ddad0ed472fbe687fe12340c5d8","title":"BOOK-FIXTURE-1 日漫_JA 测试书",
            "page_count":8, ...}],"error":null}
```

### 12.3 关键：7 次 `list_chapters` **全部**返回了正确的 chapters

```
RESP#1..RESP#7 content: {"chapters":[{"chapter_id":"240bdba549b74281bfc6d901b1a7abd7",
                           "title":"第 1 章","chapter_number":"1","sort_order":1,...}]} | error: None
```

**⇒ sidecar 对每一次请求都返回了正确的数据。**

### 12.4 C# 侧的解析代码看起来是**正确**的

```csharp
var result = RequireResult(response, "list_chapters");
if (result.TryGetProperty("chapters", out var array) && array.ValueKind == JsonValueKind.Array) { ... }
return chapters;   // ← 属性缺失时【静默返回空列表】，不报错
```

它与 sidecar 的 `{"chapters": [...]}` 形状**一致**。但注意：**属性缺失时静默返回空**，
这正是 `Assert.Single` 得到空集合而不抛异常的形态。

### 12.5 结论

**sidecar 100% 正常（帧为证），C# 解析与帧形状一致，测试却拿到空集合。**

唯一能同时满足这三件事的解释是：**C# 客户端在并发读时把响应配错了请求**
（12 个并发请求共用一条 stdin/stdout 管道；若 `CoreServiceClient` 的读端未按 `request_id` 严格配对，
`ListChaptersAsync` 会拿到 `GetReaderProjection` 的响应 —— 后者没有 `chapters` 属性 ⇒ **静默返回空** ⇒ `Assert.Single` 失败）。

**这是一个产品级缺陷候选（P1 级）**：真实 UI 里同时读章节列表与阅读投影（正是 CONCURRENT 测试模拟的场景）
同样会串响应、静默显示空章节。**需要独立复核确认**，不得只凭推断定级。

### 12.6 为什么"单独跑通过、连跑失败"

连跑时前一个测试留下的 sidecar/管道状态使第二个测试的并发窗口更长或响应到达顺序变化，
从而更容易触发串配。**但根因仍是客户端的响应配对**，不是测试顺序本身。

### 12.7 下一轮（代码级）

1. 读 `CoreServiceClient.SendAsync` 的读端循环，确认是否按 `request_id` 派发响应、是否允许两帧交错；
2. 若确认串配，**先写一个能在实现回退时变红的判别测试**（并发发 `list_chapters` + `GetReaderProjection`，
   断言每个响应被派给正确的请求），再修实现；
3. 该缺陷若成立，应作为**独立 finding 登记**（它不属于 E-2，是被 E-2 解除后**暴露**出来的既有缺陷）。
## 13. 第六轮诊断：我的"串帧"假设**被证伪**，但矛盾更尖锐了

### 13.1 两个 gate 都存在，我的串帧假设不成立

| 事实 | 证据 |
|---|---|
| `HostRuntime._readerIoGate = new(1,1)` 存在 | `HostRuntime.cs:34` |
| `ListChaptersAsync` 在 gate 内 | `HostRuntime.cs:509-521`（`:511` WaitAsync / `:519` Release） |
| **`GetReaderProjectionAsync` 也在 gate 内** | `HostRuntime.cs:782-795`（`:784` WaitAsync） |
| `_sessionGate` 只保护 `OpenHostSessionAsync` | `CoreServiceClient.cs:595/633` |

⇒ 测试的 12 个并发调用**全部**经过同一个 `_readerIoGate`，**不可能**在客户端串帧。
**我在 §12.5 的"客户端串帧"推断被证伪，现撤回。**

（附带更正：`ExchangeAsync` 确实**无锁**（`Transport/SidecarProcess.cs:186-240`，写法是"写一行→读下一行"），
所以**如果**有 gate 外的调用与 gate 内并发，理论上仍会串 —— 但本测试的两条路径都在 gate 内。）

### 13.2 失败点精确定位到 `Assert.NotEmpty(chapters)`

`HostReaderChaptersIntegrationTests.cs` 逐行映射（按实际行号）：

```
43: var books = await runtime.ListBooksAsync();
44: Assert.NotEmpty(books);
45: var book = books[0];
46: var chapters = await runtime.ListChaptersAsync(book.BookId);
47: Assert.NotEmpty(chapters);          <-- 失败在这里
```

**而 wire 帧显示该 session 的 `list_chapters` 响应是**：
```json
{"chapters":[{"chapter_id":"240bdba549b74281bfc6d901b1a7abd7","title":"第 1 章",...}]}
```

**矛盾到极致：sidecar 返回了 1 个 chapter，C# 的 `ListChaptersAsync` 却返回空。**

### 13.3 两个测试**交替**失败 ⇒ 竞态

| 运行 | `ListChapters_MatchesReaderProjection` | `ConcurrentChapterAndProjectionReads_AreSerialized` |
|---|---|---|
| 单独跑前者 | **PASS** | — |
| 单独跑后者 | — | **PASS** |
| 连跑（第一次） | PASS | **FAIL**（`Assert.Single` 空） |
| 连跑（第二次） | **FAIL**（`Assert.NotEmpty` @47 空） | PASS |

⇒ **不是固定失败某个测试，而是两者交替** —— 典型的竞态/时序问题。

### 13.4 剩下的唯一嫌疑

既然 sidecar 正确、解析形状正确、gate 覆盖两点，那么"返回空"只能发生在
**`result.TryGetProperty("chapters")` 取到的 `result` 不是那个响应**。

两条可能路径：

1. **`SendAsync` 的"跳过事件帧"循环**（`CoreServiceClient.cs:2376-2384`）在 gate 内仍可能多读一行，
   把**下一个请求的响应**吃掉/错配；`core_service` 在 `READER-PROGRESS-1` 之后确实会推
   `ReadingProgressChanged` 事件帧 —— **本 session 里若有事件帧，这个循环就是唯一能"吃掉"响应的地方**。
2. **wire 记录与实际读到的行不一致**（例如 wire 记录的是 sidecar 写出，而客户端读了另一行）。

### 13.5 下一轮（决定性实验，代码级）

在 `ListChaptersAsync` 解析前**临时打印 `result.GetRawText()`**（或断言其形状），跑连跑场景：
- 若打印出的 `result` 是 `{"chapters":[...]}` 而返回仍为空 ⇒ 解析逻辑有 bug（不可能，代码很直白）；
- 若打印出的是**别的响应**（如 projection）⇒ 确认 1（事件帧循环吃掉了响应）；
- 若打印不出（异常）⇒ 看异常。

**这是唯一能一步定性的实验**，不需要再猜。
## 14. ★ 第七轮诊断（**根因确认**）：request_id 错配，后台 source 扫描抢走了阅读器响应

### 14.1 失败 session 的完整 wire（6 帧）

```
# 1  REQ core.ping      req-1  → RESP req-1  ✅
# 2  REQ OpenHostSession hostctl-2 → RESP hostctl-2 ✅
# 3  REQ core.ping      req-3  → RESP req-3  ✅
# 4  REQ core.ping      req-4  → RESP req-4  ✅
# 5  REQ ListBooks      req-5  → RESP req-5  ✅  result: [1 本书]
# 6  REQ list_chapters  req-7  → RESP req-6  ❌  result: {"targets": []}
```

**第 6 帧：请求是 `req-7`（`list_chapters`），拿到的却是 `req-6` 的响应，
内容是 `{"targets": []}` —— 那是 `source_list_scan_targets` 的响应！**

`list_chapters` 的解析器在结果里找不到 `chapters` 属性 ⇒ **静默返回空列表** ⇒
`Assert.NotEmpty(chapters)` @ `HostReaderChaptersIntegrationTests.cs:47` **失败**。

### 14.2 根因（三方同时满足）

| 环节 | 事实 | 位置 |
|---|---|---|
| 管道本身 | `ExchangeAsync` **无锁**，写法是"写一行 → 读下一行"，**假定一次只有一个请求在途** | `Transport/SidecarProcess.cs:186-240` |
| Host 层保护 | `_readerIoGate` 只覆盖 **reader 类**方法（`ListChaptersAsync:511`、`GetReaderProjectionAsync:784` 等 5 处） | `HostRuntime.cs:34/511/527/543/559/576/784` |
| **漏洞** | **后台 source 扫描直接调 `CoreServiceClient`，完全不经过该 gate** | **`SourceScanScheduler.cs:2415`**（`_core.ListSourceScanTargetsAsync`）、`SourceOperationCoordinator.cs:219` |

⇒ 后台扫描（`source_list_scan_targets`）与阅读器命令**并发**使用同一条 core_service stdin/stdout 管道，
响应互相错配。**这正是 `req-7` 拿到 `req-6` 响应的原因。**

### 14.3 为什么它现在才暴露

旧 sidecar（2026-10-23）时代这两个测试是 **SKIP**（`[BookFixtureFact]` 检查不到 sidecar 就跳过），
所以这条竞态**从未被执行过**。E-2 解除后测试开始真跑，缺陷立即显现。

### 14.4 严重度：**P1（用户可见）**

真实场景：用户打开阅读器读章节列表时，后台 source 扫描若正在跑，`list_chapters` 可能拿到
`source_list_scan_targets` 的响应 ⇒ **阅读器章节列表静默变空**，无任何错误提示。
同类风险还波及任何"gate 外调用 + gate 内调用"并发的组合（`SourceOperationCoordinator` 亦在 gate 外）。

### 14.5 修复方向（两层，建议做底层）

1. **根治（推荐）**：在 `SidecarProcess.ExchangeAsync`（或 `CoreServiceClient.SendAsync`）加一个
   **全局管道锁**（`SemaphoreSlim(1,1)`）。管道本来就是严格请求-响应复用，
   "一次一个在途"必须由最底层保证 —— 否则今后任何新调用点都可能再踩。
2. **局部（不充分）**：把 `SourceScanScheduler` / `SourceOperationCoordinator` 的调用也纳入 `_readerIoGate`。
   能用，但每新增一个调用点就要记得加，脆弱。

**判别测试要求**（修复必须能固定住）：
并发发 `list_chapters` 与 `source_list_scan_targets`（或任何 gate 外命令），断言
**每个响应的 `request_id` 与请求一致**；把底层锁去掉后该测试必须变红。
`CoreServiceClient.SendAsync` 目前**不校验响应的 `request_id`** —— 这也是它能"静默错配"的原因，
修复时建议同时加上**错配即抛 typed 错误**（而不是把别的命令的响应当成自己的结果）。
