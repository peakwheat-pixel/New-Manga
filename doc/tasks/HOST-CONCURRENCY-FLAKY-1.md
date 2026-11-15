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
- [ ] **AC4 修复或登记**：修复（需先范围冻结，因为改并发语义属产品行为变更），或明确登记为已知限制并给出可执行的处置步骤。
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
