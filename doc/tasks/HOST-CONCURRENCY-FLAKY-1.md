---
id: HOST-CONCURRENCY-FLAKY-1
title: test.ps1 环境下的 Host.Tests 失败 —— SOURCE_REGISTRY_BUSY 零超时缺陷（已修）+ FILE_IDENTITY_CHANGED 53 位口径缺口（已定位并修复）
kind: defect
governance_version: 3
status: in_review
suggested_owner: DSH
owner: DSH
reviewer: "reviewer-hcf (AC6 一轮, 277406eeb, CHANGES_REQUESTED) / reviewer-hcf2 (AC6 二轮, 9ce819ae7, CHANGES_REQUESTED→已返修); 三轮待派"
depends_on: []
approval: 用户 2026-11-15「全部授权」；本卡由 SIDECAR-SCHEMA-STALE-1 的 R87 诊断派生
base_commit: 54fd6f77a
branch: main
worktree: G:/CODEX/New Manga
evidence_dir: verification/HOST-CONCURRENCY-FLAKY-1
allowed_paths:
  - doc/tasks/HOST-CONCURRENCY-FLAKY-1.md
  - apps/desktop-avalonia/src/NewManga.Host/Sources/**
  - apps/desktop-avalonia/src/NewManga.Host/Resources/TileChannel.cs
  - apps/desktop-avalonia/src/NewManga.CoreClient/Issuer/**
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/**
  - verification/HOST-CONCURRENCY-FLAKY-1/**
  - doc/handoffs/GOAL-WRAPUP-R100.md
---

# HOST-CONCURRENCY-FLAKY-1：Host.Tests 的并发 flaky

## 怎么发现的

`SIDECAR-SCHEMA-STALE-1` 在 R85 把 `NewManga.CoreClient.Tests` 修到全绿后，
`test.ps1` 才第一次跑到后续测试项目，暴露出 `NewManga.Host.Tests` 的 3 个失败。

## 现象（R87 已实测）

| 运行方式 | 失败 | 通过 | 跳过 | 总计 |
|---|---|---|---|---|
| `dotnet test NewManga.Host.Tests.csproj` | **0** | 331 | **74** | 405 |
| `apps/desktop-avalonia/scripts/test.ps1` | **3** | 358 | **44** | 405 |

`passed + skipped` 都是 405，但**分布差 30** ⇒ `test.ps1` 的额外环境变量
（`NEWMANGA_CORECLIENT_SIDECAR_DIR`、`NEWMANGA_EVIDENCE_DIR` 等）
让 30 个原本 skip 的测试变成实际执行。

三个测试**单独跑全部 EXIT=0**（已实测）。

## 失败签名

| 测试 | 错误 | 代码位置 |
|---|---|---|
| `GrantIssuerTests.Export_GrantRegisters_ThenCoreFailsTyped_OnMissingTranslatedPages` | `[FILE_IDENTITY_CHANGED] Import source reference was rejected` | `src/.../scanner.py:170`：`"granted folder member identity drifted"` |
| `GrantIssuerTests.Import_IntoNewChapter_Executes_AndRegistersGrant` | 同上 | 同上 |
| `Fea11WatchHostRuntimeTests.Ready_ArmsWatcher_RealFileEventProducesHint_DisposeDisarms` | `SOURCE_REGISTRY_BUSY` | `SourceAccessRegistry.cs:346`（拿不到锁）、`:71`（`Generation` 乐观并发失配） |

## 已排除的假设

| 假设 | 排除依据 |
|---|---|
| `alpha.png` 被污染 | `verification/CORE-SLIM-1/ac1/fixtures/alpha.png` 的 `git status` 干净，只有一个历史提交 `95c2c28bb` |
| dataRoot 冲突 | `HostFixture.CreateOptions` 里 `dataRoot = NewDataRoot(testName)`、`MutexName = @"Local\NewManga.Host.Test." + Guid.NewGuid()[..12]`，**每测试唯一** |
| 与 `SIDECAR-SCHEMA-STALE-1` 的改动有关 | `git log b8113e740..HEAD -- apps/desktop-avalonia/src/NewManga.Host` 为空 |

## 初步判断（需本卡验证）

`SourceAccessRegistry` 用**跨进程命名锁 + `Generation` 乐观并发**：

```csharp
// :346
if (!acquired) throw new SourceAccessException("SOURCE_REGISTRY_BUSY");
// :71
if (entry.Generation != expectedGeneration) throw new SourceAccessException("SOURCE_REGISTRY_BUSY");
```

~~在 xUnit 并行运行多个 Host 测试时，这些检查会互相触发；
`FILE_IDENTITY_CHANGED` 也可能因为并行写入同一 granted folder 而误判。~~

> **⚠️ 上述「xUnit 并行」假设已作废（2026-11-16，AC6 复核后更正）。** 实测
> `NewManga.Host.Tests/AssemblyInfo.cs:1` = `[assembly: Xunit.CollectionBehavior(DisableTestParallelization = true)]`
> ⇒ Host.Tests **本来就不并行**。真实触发条件是**同进程内多线程**（测试线程 vs `HostRuntime` 后台
> watcher 线程争同一把 mutex / 锁文件），且 `FILE_IDENTITY_CHANGED` 后来被证明与并发**无关**
> （是 raw 64 位 index vs masked 53 位 comparator 的口径缺口，见「根因铁证」节）。
> 保留原始假设原文以示推论过程，勿据此复述。

**待验证（已完成）**：`_lockName` 的生成方式是否真的 per-test 唯一（**是**，`dataRoot` 的 SHA256，`:31-32`）；
`SourceAccessRegistry` 是否为进程级单例（**不是**：每 dataRoot 一个实例 + 跨进程命名 mutex）；
xUnit 的并行集合配置（**已确认 `DisableTestParallelization = true`**）。三项见 AC1。

## Acceptance Criteria

- [x] **AC1 并发路径澄清**：确认 `SourceAccessRegistry` 的锁作用域（进程级/实例级）、`_lockName` 生成方式、xUnit 并行配置。 <!-- 三项全部澄清：①_lockName 由 dataRoot 的 SHA256 派生（SourceAccessRegistry.cs:31-32），HostFixture 的 dataRoot 每测试唯一 ⇒ per-test 唯一，不是跨测试抢同一把锁；②锁是 Global 命名 mutex（`UnauthorizedAccessException` 时回退 Local）+ registry.v1.lock 独占文件锁 ⇒ 进程级互斥；③xUnit 配置实测 NewManga.Host.Tests/AssemblyInfo.cs:1 = [assembly: Xunit.CollectionBehavior(DisableTestParallelization = true)] ⇒ Host 测试不并行。原「xUnit 并行导致互相触发」叙事已被 ③ 证伪，真实触发条件是同进程内多线程（测试线程 vs HostRuntime 后台 watcher），见「叙事更正」节。 --> <<MET>>
- [x] **AC2 失败复现**：在受控条件下稳定复现 3 个失败（如提高并行度或多跑几轮），并保存日志。 <<MET>>
- [x] **AC3 根因判定**：区分「锁粒度不足」「identity 检查过严」「测试间共享状态」三类，给出代码级依据。 <<MET>>
- [x] **AC4 修复或登记**：修复（需先范围冻结，因为改并发语义属产品行为变更），或明确登记为已知限制并给出可执行的处置步骤。 <!-- 三处 producer 全部处置：①HostIssuer.cs:563（file）/ :596-597（dir）已套 NormalizeFileId（import grant 路径）；②SourceReadCoordinator.cs:408 / :632 已套 SourceSecurity.NormalizeFileId（source-read wire facts 路径，AC6 复核 P0-1）；③SourceSecurity.Identity 本体刻意保持 raw —— 该值被 SourceAccessRegistry.cs:49/137-141 持久化进 registry.v1.dat 作 SourceRoot.FileId 并校验，mask 会让既有 dataRoot 的 registry 全部 SOURCE_REGISTRY_UNAVAILABLE。TileChannel.cs:437 经 AC6 二次复核判定**不参与跨语言 identity 比较**（FileIdentity 只在 Issue/ReadTile 内同源 raw 自比；TileGrantView 不含 identity 字段；唯一生产调用点 HostRuntime.cs:1044-1050 不传 VolumeSerial/FileIndex），故不需修，已在代码内加契约注释。回归测试 HostFileIdNormalizationTests 固定常量与 wire 口径（已做回退红测验证）。 --> <<MET>>
- [x] **AC5 不影响既有基线**：全量 `test.ps1` 在当前 HEAD 仍全绿 1579/1627 passed / 0 failed / 48 skipped，App.Tests 962/0/4 不退化基线 955/0/11。 <!-- 判据改写（AC6 复核 P1-2 给的两个选项之一）：原判据「裸跑 dotnet test 仍全绿（331/0/74）」本身不成立 —— 裸跑缺 NEWMANGA_* fixture 变量，两个 GrantIssuerTests 是 SKIP 而非 passed（见 correction-skip-vs-pass.md）。改用 test.ps1 全量（是该环境的超集）作为判据；证据 after-p0-fix.log（二次复核通道）与本次返修后的全量运行。 --> <<MET>>
- [ ] **AC6 独立复核**：固定 head 交独立上下文 Review。 <!-- 已做两轮独立上下文复核：reviewer-hcf 审 277406eeb 结论 CHANGES_REQUESTED（P0-1/P1-1..P1-4/P2-1..P2-5）；reviewer-hcf2 审 9ce819ae7 结论 CHANGES_REQUESTED（认定代码侧可放行、文档/证据/门禁需再修一轮）。已按二次复核 findings 返修：控制字符 17 处、证据 sha256 15 行、卡面自相矛盾与旧表述、AC 标记合规、P2-3/P2-4/P2-5、P2-N1/P2-N4、新增回归测试。待第三次复核确认后勾选。 --> <<PARTIAL: 二次复核 CHANGES_REQUESTED 已按 findings 逐条返修，待第三次独立复核对返修结果确认>>

## 禁止范围

- 不得为了「让 `test.ps1` 绿」而让这 30 个测试重新 skip（那是掩盖问题）；
- 不得在未做范围冻结的情况下修改 `SourceAccessRegistry` 的并发语义；
- 不得修改 `alpha.png` 或其他 fixture 内容来「避开」identity 检查。

## 说明

本卡与 `SIDECAR-SCHEMA-STALE-1` 是**独立**问题：
后者是 sidecar schema 与测试期望对齐（已把 CoreClient.Tests 修到全绿），
前者是 Host 层并发健壮性。**不要把两个问题混在一张卡里。**

## 诊断结论（AC1 / AC3，2026-11-16）

**AC1 完成**：`_lockName` 由 `dataRoot` 的 SHA256 派生（`SourceAccessRegistry.cs:31-32`），
配合 `HostFixture.CreateOptions` 的 `dataRoot = NewDataRoot(testName)` ⇒ **per-test 唯一**。
**不是跨测试抢同一把锁。**

**AC3 部分完成**，根因是**同进程内竞争 + 零超时**：

```csharp
// SourceAccessRegistry.cs:344
try { acquired = mutex.WaitOne(0); }          // ← 零超时，不重试
if (!acquired) throw new SourceAccessException("SOURCE_REGISTRY_BUSY");   // :346
...
fileLock = new FileStream(... "registry.v1.lock", ..., FileShare.None);   // ← 独占文件锁，失败同样立即 BUSY
```

外加 `:71` 的 `Generation` 乐观并发失配也抛同一码、同样无重试。

**`Fea11WatchHostRuntimeTests` 为何暴露**：测试线程 `Register(...)` 与 `HostRuntime` 的
**后台 watcher 线程**在同一 dataRoot 上竞争同一把 mutex / 文件锁，
`WaitOne(0)` 不等 ⇒ 任一方立即失败。

**`FILE_IDENTITY_CHANGED`**：机制关联已指出（两个 `GrantIssuerTests` 同样走 grant/import 路径），
但**需 AC2 受控复现**才能确认到代码级，本轮不下定论。

**修复方向（供 AC4，本轮不实施）**：`WaitOne(0)` → `WaitOne(boundedTimeout)`、
`FileShare.None` 失败改有界重试。关键语义更正：
`SOURCE_REGISTRY_BUSY` 应是「**合理等待后仍然忙**」，而非「**这一次抢占失败了**」。
当前实现把瞬时竞争与真正繁忙混为一谈。

详见 `verification/HOST-CONCURRENCY-FLAKY-1/ac1-ac3-diagnosis.md`。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class | sha256_basis |
|---|---|---|---|---|---|---|
| EV-HCF-01 | AC1/AC3 代码摘录与诊断 | verification/HOST-CONCURRENCY-FLAKY-1/code-evidence.log | 84b4a2456 | cd56c9115852142faf19637c4c516c03ce05ad12839782c5e76a7ef788e9d92c | CANONICAL | BLOB |
| EV-HCF-02 | AC2 受控复现（2/2 稳定） | verification/HOST-CONCURRENCY-FLAKY-1/ac2-repro.md | fbf704a37 | 7544f69b96563434b1bf8e2f0699b9950f3c804104c54806536a414558302a4a | CANONICAL | BLOB |
| EV-HCF-03 | AC2 复现日志第 1 轮 | verification/HOST-CONCURRENCY-FLAKY-1/repro-1.log | fbf704a37 | bd5b44748d1bf5a784256364ef6e672dcf4ce011bc0c5421ac174ae3a0c5d3d0 | CANONICAL | BLOB |
| EV-HCF-04 | AC2 复现日志第 2 轮 | verification/HOST-CONCURRENCY-FLAKY-1/repro-2.log | fbf704a37 | 01244f82eb49c100d49583109d1e4f4eb46d5e1ccac9b8fd5c138ba0efd79c3a | CANONICAL | BLOB |
| EV-HCF-05 | AC4 修复后 test.ps1 全量 | verification/HOST-CONCURRENCY-FLAKY-1/after-fix.log | e66323bf2 | 5ba3e18433712f24a9daadbc6fa59b3dd20648a833e3080c5e0b1ec6c5bb6985 | CANONICAL | BLOB |
| EV-HCF-06 | AC4 Host 项目 -warnaserror 编译 | verification/HOST-CONCURRENCY-FLAKY-1/build.log | e66323bf2 | 3e4ef652f53a34659a8b8483daacfabc4ee27a3994062b598b5252bc8965fbd7 | CANONICAL | BLOB |
| EV-HCF-07 | **定性更正**：裸跑 EXIT=0 实为 SKIP | verification/HOST-CONCURRENCY-FLAKY-1/correction-skip-vs-pass.md | ac434d911 | b48e9f14f6e4b1ebd1efeb78a6b8b7d242e073a730d83a5d2e4f8b8fdc3bd30f | CANONICAL | BLOB |
| EV-HCF-08 | 单跑 detailed 日志（4 条 SKIP 证据） | verification/HOST-CONCURRENCY-FLAKY-1/solo-detail.log | ac434d911 | ac844014e387e117e9e7be1e4ce128a33b4071a1f07d2a213060a34ac9ab812d | CANONICAL | BLOB |
| EV-HCF-09 | FILE_IDENTITY_CHANGED 口径契约与缺口定位 | verification/HOST-CONCURRENCY-FLAKY-1/file-identity-diagnosis.md | 062918039 | 2714127339039ae731a5ba2e77cb0fb99e850caad0bd214ed2da7fbd3de290b8 | CANONICAL | BLOB |
| EV-HCF-10 | st_ino 超出 53 位实测（6/7） | verification/HOST-CONCURRENCY-FLAKY-1/st-ino-measured.md | 4b1198443 | 2cf046745af297e946b84efd57d647c3a51908e95d8cd60ac9123c983c4070fb | CANONICAL | BLOB |
| EV-HCF-11 | st_ino 探针脚本（可复算） | verification/HOST-CONCURRENCY-FLAKY-1/probe_st_ino.py | 4b1198443 | a62d26e87d7407396a5fca3f794cb0af37c757f421541135154b2b01ea471322 | CANONICAL | BLOB |
| EV-HCF-12 | 探针原始输出 | verification/HOST-CONCURRENCY-FLAKY-1/st-ino-probe-output.log | 4b1198443 | c67c81482ab2d8579b4872d048162656cba982f4a5c18a14b2c3b7d9b56511e5 | CANONICAL | BLOB |
| EV-HCF-13 | **根因铁证**：Host producer 未 mask | verification/HOST-CONCURRENCY-FLAKY-1/root-cause-proven.md | c75740cb9 | 5175256b81ae9b28035df456da4b467df7882adf83ac8b96d1be309333d73b7f | CANONICAL | BLOB |
| EV-HCF-14 | **test.ps1 首次全绿** EXIT=0 | verification/HOST-CONCURRENCY-FLAKY-1/after-identity-fix.log | 277406eeb | 0fca42ce83293a012e44a3a4c1132850a0101e5d130f61243e1bed46cbd0b976 | CANONICAL | BLOB |
| EV-HCF-15 | CoreClient -warnaserror 编译 | verification/HOST-CONCURRENCY-FLAKY-1/build-r99.log | 277406eeb | 81aa19763b9320b2696b6bf6ce7478beed46241e8988d84ceb54a1b882bfdbbf | CANONICAL | BLOB |
| EV-HCF-16 | AC6 独立复核报告（CHANGES_REQUESTED + P0/P1/P2） | verification/HOST-CONCURRENCY-FLAKY-1/review-ac6.md | bbeb28dcb | ca480b624833edee8201ba76ed927f08b464dab4f908a3db65361f44e137fbee | CANONICAL | BLOB |
| EV-HCF-17 | P0-1 修复后 test.ps1 全量（仍 EXIT=0） | verification/HOST-CONCURRENCY-FLAKY-1/after-p0-fix.log | bbeb28dcb | c9ff683c687acb564a6a9d9fec10221a862a03741af3e689b17420f421ad695d | CANONICAL | BLOB |
| EV-HCF-18 | P0-1 修复的 Host -warnaserror 编译 | verification/HOST-CONCURRENCY-FLAKY-1/build-p0.log | bbeb28dcb | 5a1e95234be694cb71a90e80efa57321672d506ec82996e60803220b32880cef | CANONICAL | BLOB |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | verification/HOST-CONCURRENCY-FLAKY-1/ | NOT_APPLICABLE | - | - | 新增证据，无迁移/归档 |

## AC2 复现结论（2026-11-16）

**2/2 稳定复现**，失败集合与顺序完全一致（同 R87）。

**关键定性修正**：这**不是偶发 flaky**，而是 test.ps1 完整环境下的**确定性触发**：

| 运行方式 | 失败 | 通过 | 跳过 |
|---|---|---|---|
| dotnet test（裸环境） | 0 | 331 | 74 |
| test.ps1（完整环境） | 3 | 358 | 44 |

test.ps1:102-134 的 fixture 变量（NEWMANGA_S4_FIXTURES / BOOK_FIXTURE_ROOT /
S4_REGION_FIXTURE / MODELS_SIDECAR_DIR / CORE_TILE_E2E / EVIDENCE_DIR /
CORECLIENT_SIDECAR_DIR）让 30 个原本 self-skip 的测试实际执行，
并行下对 SourceAccessRegistry 的访问密度上升，命中 WaitOne(0) 的零超时窗口。

**对 AC4 的影响**：修复方向（WaitOne(boundedTimeout) + 有界重试）**必须做**，
不能只登记为已知限制 —— 那等于承认 test.ps1 永久红。
若 AC4 决定不改产品代码，必须在 Release Gate 层面明确接受该后果并写入已知限制清单。

## AC4 实施记录（2026-11-16，已做范围冻结）

### 冻结的范围（改什么）

apps/desktop-avalonia/src/NewManga.Host/Sources/SourceAccessRegistry.cs 的 Locked<T>() 及新增 AcquireLockFile()：

| 改动 | 原来 | 现在 |
|---|---|---|
| mutex 等待 | mutex.WaitOne(0)（零超时） | mutex.WaitOne(LockWaitMillis)（5000ms） |
| 文件锁 | 单次 FileShare.None open，失败立即 BUSY | AcquireLockFile() 有界重试（25ms 间隔，直到同一 deadline） |
| 常量 | 无 | internal const int LockWaitMillis = 5000 / LockRetryMillis = 25 |

### 明确不改（冻结边界）

- **不动** Generation 乐观并发语义（:71）—— 它抛 SOURCE_REGISTRY_BUSY 是"状态被别人改了"，
  属于另一个语义，本轮不改；
- **不动** _lockName 的生成方式（AC1 已证明 per-dataRoot 唯一）；
- **不动** HostErrorCodes 的错误码集合；
- **不动** 调用方（HostRuntime / watcher）的任何代码。

### 语义变化（这是产品行为变更，需记录）

> SOURCE_REGISTRY_BUSY 的含义从「这一次抢占失败了」变成
> 「**在 5000ms 内多次尝试仍未获得锁**」。

这个新语义与 HostErrorCodes.cs:27 把 BUSY 归类为可重试错误的既定契约**一致** ——
原来的实现反而与该契约矛盾（一次抢占失败就报"忙"，调用方重试也未必有意义）。

### 验证结果：3 failed -> 2 failed

test.ps1 全量（含 CoreClient + Host.Tests）：

`
已通过! - 失败: 0，通过: 256，已跳过: 0，总计: 256   (NewManga.CoreClient.Tests)
失败!  - 失败: 2，通过: 359，已跳过: 44，总计: 405   (NewManga.Host.Tests)   <- 原 3 failed / 358
`

**Fea11WatchHostRuntimeTests.Ready_ArmsWatcher_RealFileEventProducesHint_DisposeDisarms 已修好**
（SOURCE_REGISTRY_BUSY 消失），passed 358 -> 359。

NewManga.Host 项目 -warnaserror 编译通过。

### 剩余 2 个失败属于**另一个根因**

`
GrantIssuerTests.Export_GrantRegisters_ThenCoreFailsTyped_OnMissingTranslatedPages
GrantIssuerTests.Import_IntoNewChapter_Executes_AndRegistersGrant
`

错误仍是 [FILE_IDENTITY_CHANGED] Import source reference was rejected
（scanner.py:170 "granted folder member identity drifted"）。

**这与锁无关** —— 是身份校验判定「授权文件夹里的文件指纹变了」。
两测试在 test.ps1 下才失败、裸跑通过，说明是**并行下身份快照与文件读取的时序问题**，
需下一轮按同样的方法（读 scanner.py 的 identity 计算与比较逻辑）定位。

**AC4 标 PARTIAL**：锁问题已修并验证；identity 问题待办。

## ⚠️ 定性更正（2026-11-16，本轮自查推翻了本卡原有定性）

**我此前把裸跑 EXIT=0 当作「测试通过」，这是错的。**

用 --logger "console;verbosity=detailed" 单跑 GrantIssuerTests，实际输出是：

`
[xUnit.net] ...Export_GrantRegisters_ThenCoreFailsTyped_OnMissingTranslatedPages [SKIP]
[xUnit.net] ...Import_IntoNewChapter_Executes_AndRegistersGrant [SKIP]
[xUnit.net] ...ShellActions_Open_Whitelisted_... [SKIP]
[xUnit.net] ...ShellActions_RealOpener_... [SKIP]

已跳过 ... [1 ms]
`

⇒ **裸跑时这 3 个测试是 SKIP，根本没执行**；dotnet test 的 EXIT=0 不区分 passed 与 skipped。

### 更正后的正确结论

| 环境 | 状态 |
|---|---|
| 裸 dotnet test | **SKIP**（缺 NEWMANGA_* fixture 变量） |
| test.ps1 | **实际执行** |

- **SOURCE_REGISTRY_BUSY（Fea11）**：是被 skip 掩盖的**真实锁等待缺陷**，本轮已修并验证
  （3 failed -> 2 failed，passed 358 -> 359）。**修复有效，保留。**
- **FILE_IDENTITY_CHANGED（2 个 GrantIssuerTests）**：**不是 flaky、不是并发**，
  而是这两个测试**第一次真正执行**时暴露的**真实失败**。需要单独定位：
  注册时 Host 记录的 file_id 与导入时 Python st_ino
  （scanner.py:163 _stat_folder_entry -> st_dev/st_ino/st_size）口径是否一致。

### AC2 的效力下调

AC2 只证明了「在会执行这些测试的环境下运行就会失败」，**不证明并发相关**。
AC2 的 MET 保留（复现事实成立），但**据此得出的"并发 flaky"定性作废**。

### 共同根因（本会话第 6 次同类错误）

把「命令成功退出」当成「被测行为正确」。判断测试通过必须看具体结果行
（已通过 / 失败 / 已跳过），EXIT=0 只说明没有失败，不说明跑过了。

## FILE_IDENTITY_CHANGED 定位（2026-11-16）

**契约**（identity.py:3-9 原文）：每个 producer 与每个 comparator 都必须调用

ormalize_identity，**绝不用原始 st_ino**。归一化规则：

`python
_VOLUME_MASK = 0xFFFFFFFF        # 与 dwVolumeSerialNumber 一致
_FILE_MASK   = (1 << 53) - 1     # 53 位，C-17 N/G 整数族可精确表示
`

**比较点是对的**：scanner.py:163-171 的 dev/ino 来自 _stat_folder_entry，
其尾部已 
eturn normalize_identity(info.st_dev, info.st_ino) + (size,)。

**缺口在 producer 侧**，两个强候选：

1. HostIssuer.cs:591-596 的 Windows handle probe 返回
   (info.VolumeSerialNumber, ((ulong)info.FileIndexHigh << 32) | info.FileIndexLow)
   —— **完整 64 位，未 mask 到 53 位**；
2. source_read_refs.py:1080 的 GrantFacts(*numbers, raw["sha256"])
   —— 
umbers 是否经 
ormalize_identity 尚未确认。

若未 mask 的 64 位值经 IPC 进入 grant scope，比较时 ino（已 mask）与
facts.file_id（未 mask）就会不等 ⇒ FILE_IDENTITY_CHANGED。

**这解释了"偶发"**：FileIndex ≤ 2^53 时两者相同；test.ps1 下创建更多临时文件，
命中 > 2^53 的 index 概率上升。

**这是假设，未经实测验证。** 下一轮需抓取两侧实际数值确认，再决定修 Host 侧（契约要求的 A）
还是 core 侧反序列化（纵深防御的 B）。

**本轮不改代码**：改哪一侧取决于实测数据，不靠猜。

## 实测证实：st_ino 超过 53 位是常态（不是偶然）

探针 verification/HOST-CONCURRENCY-FLAKY-1/probe_st_ino.py（只读 stat）：

`
path            st_ino              > 2^53?  masked              丢位?
alpha.png       844424931403221     no       844424931403221     no
page-01.png     36873221950633840   YES      844424931669872     YES
page-02.png     27021597765760890   YES      1537914             YES
page-03.png     19703248371283835   YES      1688849861801851    YES
page-04.png     27021597765760892   YES      1537916             YES
page-05.png     25051272928786301   YES      7036874419304317    YES
page-06.png     22799473115101054   YES      4785074605619070    YES

样本总数 7，其中 st_ino > _FILE_MASK 的：6
`

st_dev 同样溢出 32 位（15333285442011643084 -> 0xCAC5BCCC）。

### 决定性推论

GrantIssuerTests.FixtureImages（:44-50）把夹具写到 %TEMP%/grant-fixtures-*/page-NN.png
**全部是新建文件** ⇒ 实测 6/6 的 st_ino > 2^53。
**只要链路上有一处用未 mask 的 64 位值参与比较，就必然报 FILE_IDENTITY_CHANGED。**

⇒ 这两个测试**只要真正执行就必然失败**，不是 flaky、不是并发，
而是**默认会失败**（只有 file index 恰好 ≤ 2^53 时才偶然通过）。

对比：repo 内长期存在的 alpha.png 的 st_ino = 844424931403221 < 2^53，
mask 不改变数值 —— 这正是"用既有文件没事、用新建临时文件就失败"的原因。

### 还差最后一环

物理条件已证，还差「链路上哪一处没 mask」：
1. HostIssuer.cs:591-596 handle probe 返回完整 64 位 FileIndex；
2. source_read_refs.py:1080 的 GrantFacts(*numbers, ...) 是否 mask。

下一轮抓 IPC 报文里的 file_id 与 os.stat() 值对比定论。

## 根因铁证（2026-11-16）—— 三环链路全部定位到行

| 环 | 位置 | 行为 |
|---|---|---|
| 1 producer | `NewManga.CoreClient/Issuer/HostIssuer.cs:563` | `ulong index = ((ulong)info.FileIndexHigh << 32) \| info.FileIndexLow;` —— **完整 64 位，未 mask** |
| 2 透传 | `src/infrastructure/resource_channel/source_read_refs.py:1068` | `numbers = (raw["volume_serial"], raw["file_id"], raw["size"])` —— **原样透传；该文件里 `normalize_identity` 一次都没出现** |
| 3 comparator | `src/application/importing/referenced/scanner.py:163` | `_stat_folder_entry` 返回 `normalize_identity(st_dev, st_ino)` —— **mask 到 53 位** |

比较处 `scanner.py:168`：`if dev != expected_volume or ino != facts.file_id or size != facts.size`
⇒ **mask 后的 `ino` 对比未 mask 的 `facts.file_id`**。

### 违约条款

`identity.py:3-9` 明确点名 **"the Windows handle probe"** 与 **"the grant scope"** 都是 producer，
都必须 `normalize_identity`。`HostIssuer.cs:563` 正是 Windows handle probe 的实现 ——
**它就是违约的 producer**。

### 影响面：不只是测试

`st-ino-measured.md` 已实测 `%TEMP%` 新建文件 `st_ino > 2^53` 达 6/7。
⇒ 当 NTFS file index 超过 2^53 时**必然**报 `FILE_IDENTITY_CHANGED`
（"Import source reference was rejected"）；实测样本 6/7 超过，故在**新建文件场景下高概率触发**。

> **⚠️ 表述更正（2026-11-16，AC6 复核 P1-4）**：本节原文写「**任何**用户新导入的源文件都会**稳定**报」
> 属**过强**。是否触发取决于该卷 NTFS 文件 ID 的复用序列是否使 64 位值 > 2^53 ——
> 仓库内长期可用的 `alpha.png`（`st_ino = 844424931403221 < 2^53`）就是反例。
> 正确表述为「超过 2^53 时必然失败；本机 %TEMP% 实测 6/7 超过 ⇒ 新建文件场景高概率触发」。
> 时间线上这是本会话**第一个**被识别的产品缺陷；「唯一一个」无法核验（需审计全部门卡）。

### 修法方向（Contract 要求）

```csharp
// HostIssuer.cs:563
const ulong FileIdMask = (1UL << 53) - 1;
ulong index = (((ulong)info.FileIndexHigh << 32) | info.FileIndexLow) & FileIdMask;
```

还需检查 `DirectoryIdentity`（`HostIssuer.cs:596`）是否走同一比较口径。
**常量单一事实来源**：`_VOLUME_MASK` / `_FILE_MASK` 现只在 `identity.py` 定义，
C# 镜像需在注释中指向该文件作为权威。

### 范围变更（本轮裁决并记录）

`HostIssuer.cs` 位于 `NewManga.CoreClient/Issuer/`，**超出本卡原 `allowed_paths`**
（原只授权 `NewManga.Host/Sources/**`）。按治理规则由 DSH 作为 Lead/Integrator 裁决
**扩展 `allowed_paths` 增加 `apps/desktop-avalonia/src/NewManga.CoreClient/Issuer/**`**，
理由：根因已定位到该文件第 563 行，另立卡会产生跨卡的同一缺陷片段。

本轮**仅扩展范围并记录证据，未改代码**；实施下一轮进行。

## 修复完成：test.ps1 首次全绿（2026-11-16，本会话最大里程碑）

### 改动（HostIssuer.cs，25 行）

在两处 identity 源头套用 53 位归一化：

`csharp
// :563 文件 identity
ulong index = NormalizeFileId(((ulong)info.FileIndexHigh << 32) | info.FileIndexLow);

// :596 目录 identity
return (info.VolumeSerialNumber,
    NormalizeFileId(((ulong)info.FileIndexHigh << 32) | info.FileIndexLow));
`

新增（注释完整引用 identity.py 作为权威定义）：

`csharp
internal const ulong FileIdMask = (1UL << 53) - 1;
internal static ulong NormalizeFileId(ulong rawFileId) => rawFileId & FileIdMask;
`

**VolumeSerialNumber 无需 mask**：dwVolumeSerialNumber 本身是 32 位。

### 验证：test.ps1 EXIT=0（首次）

`
已通过! - 失败: 0，通过: 256，已跳过: 0，总计: 256    (NewManga.CoreClient.Tests)
已通过! - 失败: 0，通过: 361，已跳过: 44，总计: 405   (NewManga.Host.Tests)
已通过! - 失败: 0，通过: 962，已跳过: 4，总计: 966    (NewManga.App.Tests)

TEST PASS (Debug): 1579/1627 passed, 48 skipped
`

| 项目 | 修复前 | 修复后 |
|---|---|---|
| CoreClient.Tests | 0 failed / 256 passed | 0 / 256 |
| Host.Tests | **2 failed** / 359 passed | **0 / 361** |
| App.Tests | 0 / 962 | 0 / 962 |
| **整体** | **EXIT=1** | **EXIT=0** |

App.Tests 962 passed / 0 failed / 4 skipped —— **不退化基线 955/0/11**（通过数 +7）。

### AC 状态

- AC1–AC5 全部 `<<MET>>`（依据见 Acceptance Criteria 行的行内注释与 Canonical Evidence 表）
- AC6（独立上下文复核）：已完成两轮；二次复核 CHANGES_REQUESTED 的 findings 已逐条返修，待第三轮确认

> **⚠️ 本小节曾与 AC 行自相矛盾（2026-11-16 二次复核 P1-2 指出）**：原文写「AC1 MET / AC2 MET /
> AC3 MET / **AC4 现在 MET** / **AC5 MET**」，而 AC 行同时标 `<<PARTIAL>>`。现统一为 `<<MET>>`
> 并在 AC 行给出依据；矛盾已消除。

### 这个缺陷的真实影响（更正后的口径）

不是测试问题：当 NTFS FileIndex 超过 2^53 时（本机 `%TEMP%` 新建文件实测 6/7 超过），
`scanner.py` 的 masked 比较会**必然**报 `FILE_IDENTITY_CHANGED`。
在新建文件场景下**高概率**触发；低复用序列的卷可能不触发（`alpha.png` 是反例）。
这是本会话**第一个**被识别的、可能直接影响真实用户的缺陷；「唯一一个」无法核验（需审计全部门卡）。

> **⚠️ 表述更正（2026-11-16，AC6 二次复核 P1-4）**：原文「任何用户**新导入**的源文件，NTFS
> FileIndex 大概率 > 2^53……**这是本会话唯一一个确认影响真实用户的产品缺陷**」为过强表述。
> 已按复核意见下调；同一断言已在 `doc/handoffs/GOAL-WRAPUP-R100.md`（`07a8f828b`）同步更正。

### 附带发现（已登记，下一轮处理）

1. 跑 `test.ps1` 会重新生成 `verification/READER-OVERLAY-HEADLESS-PNG-1/immersive-reader.png`
   与 `verification/READER-OVERLAY-HEADLESS-PNG-1/render-info.md`（测试副作用），
   本轮已 `git checkout` 还原、未混入提交。应独立登记。
   （原文此处曾被损坏为「与 / ender-info.md」，2026-11-16 修复。）
2. **（AC6 二次复核 P2-5 补充）** `test.ps1` 还会**覆写**仓外证据目录
   `G:\CODEX\New Manga.workspace\task-envs\HOST-RESOURCE-SECURITY-1\evidence-rerun\test\`
   —— `results-*.trx` 与 `summary.json` 的 `at_utc` 每次全量运行都被重写，使任何依赖该目录
   旧文件的 `trx_sha256` 声明**不可复验**。二次复核期间实证：P0-1 运行的 `at_utc`
   `2026-11-15T21:38:54Z` 被 2026-11-16 的 `09:53:46` 覆写。
   ⇒ 后续本卡 TRX 证据复算须「当日运行即当日校验」，或把证据目录改为按 run 分目录（建议另立卡）。


## AC6 一轮复核处置（reviewer-hcf，2026-11-16）

独立上下文复核者 **reviewer-hcf**（只读；`git status --porcelain` 全程为空）
结论 **CHANGES_REQUESTED**。报告：`verification/HOST-CONCURRENCY-FLAKY-1/review-ac6.md`（361 行）。

### 复核确认成立的部分（保留原修复）

- 两处原修复**正确、应保留**：`HostIssuer.cs:563/596-597` 归一化、
  `SourceAccessRegistry.cs:362/379-398` 有界等待；
- `FileIdMask = (1UL << 53) - 1` 与 `identity.py:20` 数值一致；
  `dwVolumeSerialNumber` 是 `uint` ⇒ C# 侧 `_VOLUME_MASK` 是 no-op；
- **测试证据是真绿、不是 skip 冒充 pass**：复核者用 log 里的 `trx_sha256` 校验磁盘 TRX，
  三个哈希逐一相同；解析 `results-host.trx` 得 405 = 361 Passed + 44 NotExecuted + 0 Failed，
  两个曾失败的 `GrantIssuerTests` 是 `Passed` 且有真实执行时长（0.758s / 0.609s）。

### P0-1（已修）：producer 遗漏

发现 `HostIssuer` 只修了 3 处 handle probe 中的 1 处。
`SourceSecurity.Identity` 的 raw file index 经 `SourceReadCoordinator` 流入
**source-read grant facts**，Py 侧 `source_read_refs.py:1068/1080` 原样透传，
在 `scanner.py:168` 与 masked 值对撞 ⇒ 同签名 `FILE_IDENTITY_CHANGED`。

**修法采纳复核者关键提醒**：不在 `SourceSecurity.Identity` 内 mask —— 该值还被
`SourceAccessRegistry.cs:49/137` 持久化到 `registry.v1.dat` 作 `SourceRoot.FileId`
并在 `:140-141` 校验，单边 mask 会让既有 registry 全部 `SOURCE_REGISTRY_UNAVAILABLE`。
改为在**写入 wire facts 的两处**（`SourceReadCoordinator.cs:408` / `:632`；修复提交时为 `:404` / `:624`，后因加注释偏移 +4/+8）归一化。

验证：`test.ps1` 仍 **EXIT=0**（1579/1627），Host `-warnaserror` 编译通过。

### P1（已修）：证据 pin 表 15/15 行 commit 全错

原表的 `commit` 填的是"该证据入库前的父提交"，`git cat-file -e` 对多数行返回 128（不存在）。
最严重的是 EV-HCF-14/15 把"修复后首次全绿"的日志钉在修复提交**之前**。

根因：`apply_card_r98.py:20-46` 用当时 HEAD 填 commit，blob 不存在就写 `PIN_PENDING`。
**`check.ps1` 仍 PASS(3w)，说明检查器不校验 pin 的 commit 归属。**

已用 `git log --diff-filter=A -- <path>` 反查实际引入 commit 并全部更正；
本轮新增 EV-HCF-16/17/18 亦按同一规则填写。
**18/18 行 `git cat-file -e <commit>:<path>` = 0，且与实际引入提交逐一相同；sha256 也已全部补为 BLOB 口径实算值**（二次复核 P1-1 剩余项，见「AC6 二次复核处置」节）。

### AC 标记裁决轨迹（一轮复核 → 二轮复核 → 最终收敛）

| AC | 一轮复核前 | 一轮复核后 | 二轮复核后（现状） | 理由 |
|---|---|---|---|---|
| AC1 | MET | PARTIAL | **MET** | 一轮指出「xUnit 并行配置」未澄清且并行叙事被 `AssemblyInfo.cs:1` 证伪 ⇒ 降级合理。返修时把三项（锁作用域 / `_lockName` / xUnit 配置）逐一写进 AC 行并删除旧叙事，缺项已补齐 ⇒ 恢复 MET |
| AC4 | MET | PARTIAL | **MET** | 一轮指出遗漏 producer（P0-1）⇒ 降级合理。返修：`SourceReadCoordinator.cs:408/:632` 已归一化；`TileChannel.cs:437` 经二轮复核判定**不参与跨语言比较、不需修**；新增回归测试并做回退红测 ⇒ 恢复 MET |
| AC5 | MET | PARTIAL | **MET** | 原判据「裸跑 331/0/74」本身不成立（裸跑是 SKIP）。二轮复核给的二选一里选了**改写判据**为「全量 `test.ps1` 1579/1627 / 0 failed、App 不退化 955/0/11」，并在 AC 行写明 ⇒ 恢复 MET |

**叙事更正（重要）**：`AssemblyInfo.cs:1` 的 `DisableTestParallelization = true` 证明
Host.Tests **本来就不并行**。所以本卡早前「并行导致 `SOURCE_REGISTRY_BUSY`」的归因是错的。
**缺陷本身真实**（`WaitOne(0)` 零超时 + `FileShare.None` 单次 open），修复有效，
但**触发条件是「同进程内多线程」而非「测试并行」** —— 后者在 Host.Tests 中被显式禁用。

### 过度声明更正

原文「任何用户新导入都会稳定报 `FILE_IDENTITY_CHANGED`」**过强**。
复核指出触发取决于 NTFS 64 位 file ID 的复用序列是否使值 > 2^53；
`alpha.png` 的 `st_ino = 844424931403221 < 2^53` 长期可用即是反例。
**正确表述**：当 file index 超过 2^53 时必然失败；实测样本 6/7 超过，
故在新建文件场景下**高概率**触发，而非"任何情况"。

### 复核者未能独立验证的项（如实记录）

- 未重跑 `test.ps1`/`dotnet test`（只读约束）⇒ 绿是 TRX 级强证据，
  但"运行树 == `277406eeb`"只能间接推断；
- P0 是代码级链路核对，端到端需 opt-in `NEWMANGA_FEA11_IPC=1`（会起真实 Core），未跑；
- "本会话唯一一个产品缺陷"需审计全部门卡，未核。

---

## AC6 二次复核处置（reviewer-hcf2，2026-11-16 返修轮）

### 复核安排（上下文独立）

- 复核者：**`reviewer-hcf2`**（全新上下文子 agent，**未复用** `reviewer-hcf` 的会话；
  两者互不可见对方的推理过程）
- 被审 head：`9ce819ae7`
- 复核方式：只读（`git log/show/cat-file/rev-parse/grep`、读代码/日志/TRX/summary、只读 `check.ps1`）；
  **未重跑** `test.ps1` / `dotnet test`（只读约束，且 Lead 正在跑全量会冲突）
- 报告：`verification/HOST-CONCURRENCY-FLAKY-1/review-ac6-2nd.md`（278 行，EV-HCF-19）

### 结论：CHANGES_REQUESTED，但**代码侧明确放行**

| 维度 | 复核判定 |
|---|---|
| **P0-1 补修正确性** | ✅ **独立验证通过（正确且完整）**：`:408` / `:632` 均套 `SourceSecurity.NormalizeFileId`；`Identity` 本体保持 raw 与声称一致；全 producer 穷举后**无遗漏**；Python 侧 `scanner.py` / `source_strict_read.py` / `handle_resolver.py` 全部 masked，而 `source_read_refs.py:1068/1080` 原样透传 ⇒ **两侧现在必然相等** |
| **`TileChannel.cs:437` 同源风险** | ✅ **明确结论：不参与跨语言 identity 比较，不构成同源风险，不需修**。`Issue`/`ReadTile` 是同进程同源 raw 自比；`TileGrantView`/`ToView` 不含 identity 字段；唯一生产调用点 `HostRuntime.cs:1044-1050` 不传 `VolumeSerial/FileIndex`；`BridgeGrant` 两字段虽来自 Core masked 值但生产代码零消费 |
| **不改 `Identity` 的取舍** | ✅ 正确（跨语言边界归一、Host 持久化本体保持原语义）。但指出作者「既有**用户** registry 会失效」表述过强：`v0.1.1` tag 不含该文件（`995d80ca5` 引入），影响面实为本机 dataRoot + 持久化语义变更 |
| **证据 commit 列** | ✅ **18/18 全部修对**：`git cat-file -e` = 0，且与实际引入提交逐一相同；EV-14/15 因果顺序正确（日志早于提交 49 秒） |
| **证据 sha256 列** | ❌ 15 行仍 `PIN_PENDING`（P1-1 剩余） |
| **卡面自相矛盾** | ❌ AC 行 `<<PARTIAL>>` vs 正文「AC4 现在 MET」并存（P1-2 未完成） |
| **AC 标记合规** | ❌ AC1/AC4/AC5 为 `[x]` + `<<PARTIAL>>`（§4.3 不允许）；AC6 缺标记 ⇒ **一旦进 `in_review` 即 4 条 FAIL**（当前 `proposed` 不触发门禁） |
| **P2-1/2/3/4/5** | ❌ 全部未处置 |
| **P1-3/P1-4 正文** | ❌ 只在处置节追加更正，正文原文未改 |

### 本轮返修（逐条）

| 复核 finding | 返修动作 | 落点 |
|---|---|---|
| P1-1 剩余：15 行 sha256 | 全部补为 `git cat-file blob <commit>:<path>` **原始字节的 SHA-256**（BLOB 口径）。EV-16/17/18 用同一法复算，与卡面已有值**逐一相同** ⇒ 口径正确 | Canonical Evidence 表 |
| P1-2 自相矛盾 | 删除「AC4 现在 MET / AC1 MET / AC5 MET」，统一为 AC1–AC5 全 `<<MET>>` 并给依据；保留矛盾更正声明 | 「AC 状态」节 |
| P1-N1 勾选/标记不合规 | AC1/AC4/AC5 → `[x]` + `<<MET>>`（依据进行内注释）；AC6 → `[ ]` + `<<PARTIAL: 原因>>`（待三轮确认） | Acceptance Criteria |
| P1-3 并行叙事 | 正文「xUnit 并行」段加删除线 + 更正块（`AssemblyInfo.cs:1` = `DisableTestParallelization = true`）；「待验证」三项改为已确认；`verification/HOST-CONCURRENCY-FLAKY-1/ac1-ac3-diagnosis.md` 的 `:103` 同步更正 | 本卡「初步判断」节 + 诊断文件 |
| P1-4 绝对化表述 | 两处「任何用户 / 唯一一个」下调为「超过 2^53 必然失败；新建场景高概率触发」，并注明「唯一一个」不可核验 | 「影响面」「缺陷真实影响」两节 |
| P2-1 控制字符 | 17 处词内控制字符全部还原：`<TAB>est.ps1`→`test.ps1`（11）、`<BEL>pps`→`apps`、`<BEL>lpha`→`alpha`、`<FF>ile_id`→`file_id`（2）、`<FF>acts.`→`facts.`、`<VT>erification`→`verification`（2）；另修复原文缺字的 `ender-info.md`→`render-info.md`。**字节级复扫零残留** | 本卡 |
| P2-2 front-matter/标题 | `status: proposed → in_review`；`owner: null → DSH`；`reviewer:` 记录两轮复核与待派三轮；`title` 去掉「（待定位）」 | front-matter |
| P2-3 最坏等待 | `SourceAccessRegistry` 的 `LockWaitMillis` 注释补「mutex 5000ms + 文件锁 5000ms ⇒ **最坏 ≈10s**，不得按 5s 宣称」 | 源码注释 |
| P2-4 常量一致性测试 | 新增 `HostFileIdNormalizationTests`：`CoreFileIdMask == (1<<53)-1`、`NormalizeFileId` 的 mask/幂等/边界、`DescribeContainer` 的 wire facts 必为 masked | 新增测试文件 |
| P2-5 evidence 目录覆写 | 「附带发现」补第 2 条：`evidence-rerun/test/` 每次全量被覆写、旧 `trx_sha256` 不可复验，并给处置建议 | 「附带发现」节 |
| P2-N1 opt-in helper 口径 | `Fea11ScanIpcTests.ReadFileIdentity` 改为返回 `SourceSecurity.NormalizeFileId(...)`，与生产 grant 同口径（附完整因果注释） | 测试 helper |
| P2-N2 无直接回归测试 | **已补**：`DescribeContainer` 由 `private` 改 `internal` 供测试（纯静态 fact-builder，零行为面）；新测试**做了回退红测**（详见下） | 新增测试 + 源码可见性 |
| P2-N3 日志缺 EXIT 头 | 本轮证据日志以 `EXIT=0` 收尾（`test.ps1` 已有 `TEST PASS` 行） | EV-HCF-20 |
| P2-N4 行号漂移 | 处置节 `:404/624` 改为 `:408/:632` 并注明原值；AC4 行注释用新行号 | 本卡 |

### 补测试时我差点又犯的同一类错（记录）

第一版 `DescribeContainer_EmitsNormalizedFileId_NotTheRawHandleIndex` 把探针目录建在
`G:\CODEX\New Manga.workspace`，实测该卷新建文件 `st_ino ≈ 1.69e15 < 2^53` ⇒
**强断言根本不会触发**，测试会绿但什么都没测到（典型的「假绿」）。
改用 `%TEMP%`（实测 11/12 > 2^53）并把「拿不到溢出样本」改为 **直接 FAIL** 后，
再用**临时回退实现**做红测确认：

```
回退 :408 为 ["file_id"] = before.Id
  → 失败 DescribeContainer_EmitsNormalizedFileId_NotTheRawHandleIndex
    Assert.Equal() Failure: Expected 5348024557882020 / Actual 59391220086327972
还原后 → 3/3 通过
```

这与本卡最早的「把 `EXIT=0`（含 SKIP）当成 passed」是**同一类错误**（工具/口径不忠实反映真实链路），
记录在此。

### 仍未处置 / 明确留待三轮复核的点

1. **P0-1 的端到端运行时行为未实跑**：覆盖 source-read 路径的 `Fea11*IpcTests` 是
   `NEWMANGA_FEA11_IPC=1` opt-in，`test.ps1` 不设该变量 ⇒ 本卡绿只能证明「不退化 + 静态链路成立」。
   已在 AC4 / 「未能独立验证」处如实登记，**不宣称端到端已验证**。
2. **`v0.1.1` 发布语义上的影响面**：二次复核指出「既有用户 registry」表述过强，本卡已按新表述记录，
   但未改动 `SourceAccessRegistry` 的持久化语义（也不需要）。
3. **第三次复核**：本卡 AC6 需第三轮独立上下文复核确认返修结果后，才能把 AC6 标 `<<MET>>` 并关闭。

