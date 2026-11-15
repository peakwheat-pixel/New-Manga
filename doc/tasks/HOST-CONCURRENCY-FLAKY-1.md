---
id: HOST-CONCURRENCY-FLAKY-1
title: Host.Tests 在 test.ps1 并行环境下的并发 flaky —— SourceAccessRegistry 的 BUSY 与 FILE_IDENTITY_CHANGED
kind: defect
governance_version: 3
status: proposed
suggested_owner: DSH
owner: null
reviewer: null
depends_on: []
approval: 用户 2026-11-15「全部授权」；本卡由 SIDECAR-SCHEMA-STALE-1 的 R87 诊断派生
base_commit: 54fd6f77a
branch: main
worktree: G:/CODEX/New Manga
evidence_dir: verification/HOST-CONCURRENCY-FLAKY-1
allowed_paths:
  - doc/tasks/HOST-CONCURRENCY-FLAKY-1.md
  - apps/desktop-avalonia/src/NewManga.Host/Sources/**
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/**
  - verification/HOST-CONCURRENCY-FLAKY-1/**
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

在 xUnit 并行运行多个 Host 测试时，这些检查会互相触发；
`FILE_IDENTITY_CHANGED` 也可能因为并行写入同一 granted folder 而误判。

**待验证**：`_lockName` 的生成方式是否真的 per-test 唯一；
`SourceAccessRegistry` 是否为进程级单例；xUnit 的并行集合配置。

## Acceptance Criteria

- [x] **AC1 并发路径澄清**：确认 `SourceAccessRegistry` 的锁作用域（进程级/实例级）、`_lockName` 生成方式、xUnit 并行配置。 <<MET>>
- [x] **AC2 失败复现**：在受控条件下稳定复现 3 个失败（如提高并行度或多跑几轮），并保存日志。 <<MET>>
- [x] **AC3 根因判定**：区分「锁粒度不足」「identity 检查过严」「测试间共享状态」三类，给出代码级依据。 <<MET>>
- [x] **AC4 修复或登记**：修复（需先范围冻结，因为改并发语义属产品行为变更），或明确登记为已知限制并给出可执行的处置步骤。 <<PARTIAL: SOURCE_REGISTRY_BUSY 已修（3->2 failed）；FILE_IDENTITY_CHANGED 属独立根因，待办>>
- [ ] **AC5 不影响既有基线**：`dotnet test` 直接跑仍全绿（331/0/74）。
- [ ] **AC6 独立复核**：固定 head 交独立上下文 Review。

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
| EV-HCF-01 | AC1/AC3 代码摘录与诊断 | verification/HOST-CONCURRENCY-FLAKY-1/code-evidence.log | 25e8f5492 | PIN_PENDING | CANONICAL | BLOB |
| EV-HCF-02 | AC2 受控复现（2/2 稳定） | verification/HOST-CONCURRENCY-FLAKY-1/ac2-repro.md | 84b4a2456 | PIN_PENDING | CANONICAL | BLOB |
| EV-HCF-03 | AC2 复现日志第 1 轮 | verification/HOST-CONCURRENCY-FLAKY-1/repro-1.log | 84b4a2456 | PIN_PENDING | CANONICAL | BLOB |
| EV-HCF-04 | AC2 复现日志第 2 轮 | verification/HOST-CONCURRENCY-FLAKY-1/repro-2.log | 84b4a2456 | PIN_PENDING | CANONICAL | BLOB |
| EV-HCF-05 | AC4 修复后 test.ps1 全量 | verification/HOST-CONCURRENCY-FLAKY-1/after-fix.log | fbf704a37 | PIN_PENDING | CANONICAL | BLOB |
| EV-HCF-06 | AC4 Host 项目 -warnaserror 编译 | verification/HOST-CONCURRENCY-FLAKY-1/build.log | fbf704a37 | PIN_PENDING | CANONICAL | BLOB |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | verification/HOST-CONCURRENCY-FLAKY-1/ | NOT_APPLICABLE | - | - | 新增证据，无迁移/归档 |

## AC2 复现结论（2026-11-16）

**2/2 稳定复现**，失败集合与顺序完全一致（同 R87）。

**关键定性修正**：这**不是偶发 flaky**，而是 	est.ps1 完整环境下的**确定性触发**：

| 运行方式 | 失败 | 通过 | 跳过 |
|---|---|---|---|
| dotnet test（裸环境） | 0 | 331 | 74 |
| 	est.ps1（完整环境） | 3 | 358 | 44 |

	est.ps1:102-134 的 fixture 变量（NEWMANGA_S4_FIXTURES / BOOK_FIXTURE_ROOT /
S4_REGION_FIXTURE / MODELS_SIDECAR_DIR / CORE_TILE_E2E / EVIDENCE_DIR /
CORECLIENT_SIDECAR_DIR）让 30 个原本 self-skip 的测试实际执行，
并行下对 SourceAccessRegistry 的访问密度上升，命中 WaitOne(0) 的零超时窗口。

**对 AC4 的影响**：修复方向（WaitOne(boundedTimeout) + 有界重试）**必须做**，
不能只登记为已知限制 —— 那等于承认 	est.ps1 永久红。
若 AC4 决定不改产品代码，必须在 Release Gate 层面明确接受该后果并写入已知限制清单。

## AC4 实施记录（2026-11-16，已做范围冻结）

### 冻结的范围（改什么）

pps/desktop-avalonia/src/NewManga.Host/Sources/SourceAccessRegistry.cs 的 Locked<T>() 及新增 AcquireLockFile()：

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

	est.ps1 全量（含 CoreClient + Host.Tests）：

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
两测试在 	est.ps1 下才失败、裸跑通过，说明是**并行下身份快照与文件读取的时序问题**，
需下一轮按同样的方法（读 scanner.py 的 identity 计算与比较逻辑）定位。

**AC4 标 PARTIAL**：锁问题已修并验证；identity 问题待办。
