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
