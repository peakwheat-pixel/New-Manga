---
id: E7-5-SHUTDOWN-RACE-1
title: 核证 E-7 第 5 项（Dispose/StopAsync 在租约外）并把在途交换行为固化为回归测试
kind: defect
governance_version: 3
status: done
suggested_owner: DSH
owner: DSH
reviewer: e7-5-review-b（r1，APPROVED_WITH_LIMITATIONS）+ e7-5-review-r2（r2，APPROVED_WITH_LIMITATIONS）
integration_commit: 1edc69c49
canonical_evidence_status: complete
resource_closeout_status: complete
depends_on:
  - R005-CANCEL-POISON-1
approval: 用户 2026-11-15「全部授权、持续自动推进」；目标 B 的产品门槛收敛
base_commit: f65adfb4b
branch: main
worktree: G:/CODEX/New Manga
evidence_dir: verification/E7-5-SHUTDOWN-RACE-1
allowed_paths:
  - doc/tasks/E7-5-SHUTDOWN-RACE-1.md
  - apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/SidecarShutdownRaceTests.cs
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - verification/E7-5-SHUTDOWN-RACE-1/**
---

# E7-5-SHUTDOWN-RACE-1：核证 `Dispose`/`StopAsync` 在租约外

## 来源

`E7-CONCURRENCY-STATUS-1` 核实的权威 E-7 第 5 项（`PIPE-EXCLUSIVE-TRANSPORT-1.md:123-129`）：

> **`Dispose`/`StopAsync` 在租约外**，在途命令会得 `ProcessExited`。

代码：`CoreServiceClient.DisposeAsync`（`:2629-2630`）与 `SidecarProcess.StopCoreAsync`
—— 两者都不持交换租约。

## 本轮做法：先实测，再决定是否改代码

R-005 的教训是「理解不准就动手会返修」。第 5 项的表述只说了「会得 `ProcessExited`」，
**没说这是不是缺陷** —— 如果错误码明确、可处理，那它可能只是描述了一个合理行为。
所以本轮先写**诊断测试**观察真实行为，再决定。

## 目标（一个可观察结果）

两条测试把当前行为**固化为回归**，并给出书面判定：E-7 第 5 项的表述是否准确、
风险是否如清单暗示的那样严重、以及是否需要改产品代码。

## Acceptance Criteria

- [x] **AC1 在途交换的诊断**：构造「子进程 5s 后才响应 + 0.5s 时并发 `StopAsync`」， <<MET>>
      记录在途 `ExchangeAsync` 抛出的**异常类型与错误码**。
- [x] **AC2 停止后的诊断**：`StopAsync` 完成后发起新交换，记录其错误类型与码 <<MET>>
      （必须 fail-fast、不得挂起、不得泄漏 BCL 异常）。
- [x] **AC3 固化断言**：把实测到的具体错误码写进断言（而非宽松的「三者之一」）， <<MET>>
      使未来任何行为变化都会让测试变红。
- [x] **AC4 书面判定**：明确回答「第 5 项表述是否准确」「是否真有缺陷」「是否需要改代码」， <<MET>>
      并如实说明未能覆盖的残余窗口。
- [x] **AC5 不回归**：`NewManga.CoreClient.Tests` 全量 **199 passed / 0 failed / 30 skipped**； <<MET>>
      四件套 PASS。
- [x] **AC6 独立复核**：固定 head 交独立上下文 Review。 <<MET>>

## 允许修改范围

见 frontmatter `allowed_paths`：**只新增测试文件，不改产品代码**
（除非诊断发现真缺陷 —— 那须在卡内说明并扩范围）。

## 禁止范围

- 不得为「让第 5 项看起来已修」而改 `StopCoreAsync`/`DisposeAsync`；
- 不得把「错误码明确」夸大成「无风险」；
- 不得声称 E-7 第 5 项已修复（本轮只核证 + 固化）。

## 测试要求

| 场景 | 命令 | 期望 |
|---|---|---|
| 诊断测试 | `dotnet test … --filter FullyQualifiedName~SidecarShutdownRaceTests` | 4 passed |
| 全量不回归 | `dotnet test …NewManga.CoreClient.Tests.csproj` | 199 / 0 / 30 |
| 四件套 | check / pins / inventory | PASS / 18-18 / 87 |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class | sha256_basis |
|---|---|---|---|---|---|---|
| EV-E75-01 | AC1-AC4 证据总述与书面判定 | verification/E7-5-SHUTDOWN-RACE-1/README.md | 6f8cf83a2 | 26400b7732b8b64e5c192fdd635808bbf88d8fac324d2cc1a95734198710d521 | CANONICAL | BLOB |
| EV-E75-02 | AC1 精确错误码探针 | verification/E7-5-SHUTDOWN-RACE-1/probe-exact-code.log | 1edc69c49 | a4b564f8750a70d4cb36149488a546f8850c4491c8e907f18ecc4ba0ac495714 | CANONICAL | BLOB |
| EV-E75-03 | AC1/AC2/AC3 最终绿（4 passed） | verification/E7-5-SHUTDOWN-RACE-1/final-green2.log | 1edc69c49 | 2c81006a7cb4996ddcc8f45a451106f3e8e4a6925c12001989b89118ecb5e632 | CANONICAL | BLOB |
| EV-E75-04 | AC5 全量不回归（199/0/30） | verification/E7-5-SHUTDOWN-RACE-1/coreclient-full-final2.log | 1edc69c49 | e3e63e60fb5aab924ebbb381931a38920af4480474d1d70682613065fc8aae41 | CANONICAL | BLOB |
| EV-E75-05 | AC 过程证据（中间态/诊断） | verification/E7-5-SHUTDOWN-RACE-1/coreclient-full-final.log | 1edc69c49 | 19e1c6ee412aa4b0713fd0dbd49881bd0061ea6b06754cf385d9a3355f74d719 | CANONICAL | BLOB |
| EV-E75-06 | AC 过程证据（中间态/诊断） | verification/E7-5-SHUTDOWN-RACE-1/diagnostic.log | 1edc69c49 | b8ccba57e35b59703ac9aff8899f0b6e8b00546c2aad7fad4c42ef9c4979a29d | CANONICAL | BLOB |
| EV-E75-07 | AC 过程证据（中间态/诊断） | verification/E7-5-SHUTDOWN-RACE-1/final-green.log | 1edc69c49 | c8555ada8d6bd723701043992980d043b502ba3bb7fb1f99192d6668084e13b1 | CANONICAL | BLOB |
| EV-E75-08 | F-4 r1 探针日志（16/16 的原始来源） | verification/E7-5-SHUTDOWN-RACE-1/r1-probe-b.log | 6f8cf83a2 | 70926c55e72151525e14c3b62802ba9832b8c85a05bb4b0b9681c70b7c831618 | CANONICAL | BLOB |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | verification/E7-5-SHUTDOWN-RACE-1/ | NOT_APPLICABLE | — | — | 新增证据，无迁移/归档 |

## Closeout Record

- Closeout：2026-11-16，DSH；实现 `5842bdfcf` + r1 返修 `1edc69c49`。
- **结果**：E-7 第 5 项**核证完成**，**未改任何产品代码**（只新增 4 条回归测试）。
- **实测结论**：
  - 在途交换 + 并发 `StopAsync` ⇒ `SidecarException(ProcessExited)`（与 E-7 表述一致）；
  - `StopAsync` 完成后新交换 ⇒ fail-fast `ProcessExited`；
  - 并发 `DisposeAsync` 撞在途交换 ⇒ **16/16 `ProcessExited`，dispose 从不抛**。
- **半行窗口（r1 P2-3 更正）**：**可稳定复现** —— 子进程写一行不完整 JSON 并 flush，
  `ReadLineAsync` 返回整行，调用方 `CoreProtocol.Parse` 抛 `MalformedResponse`。
  ⇒ **E-7 #5 的表述只在该窗口之外准确**；两者都是 typed 可处理，差别只在错误码。
- **判定**：「不需要改产品代码」—— 复核确认**可以接受**（限定于本卡不改产品代码），
  但**不得**读作「E-7 #5 已修复/已无风险」。
- **独立复核**：`e7-5-review-b` **APPROVED_WITH_LIMITATIONS**（0/0/3/3），核心理由：
  3 个 P2 全是证据/表述缺口、不动产品代码。其 P2-1（死容忍 `IoFailure`）、
  P2-2（结构性规避真实关停路径）、P2-3（半行窗口可复现）已在本轮**全部处置**；
  P3-1（ledger 过期）已重跑；P3-2（建议加显式 `_stopping` 守卫）与 P3-3（pid 临时文件）
  登记为后续项。
- **门禁**：诊断测试 4 passed / 8s；全量 **199 passed / 0 failed / 30 skipped**；
  `check.ps1` PASS (3 warnings)｜`verify_pins` 18/18｜`api_inventory` 1/80/6=87。
- **未关闭项（不淡化）**：
  1. **E-7 仍未完成**：`_pipeGate` 未统一 + `ExchangeAsync` 仍 `public`、无 `request_id` 时 fail-open、
     **R-002 错配无重同步** ⇒ **「并发安全」仍不可宣称**；
  2. 建议的显式 `_stopping` 守卫（`StopCoreAsync` 入口置标志并抛 `ProcessExitedFailure`）
     **本轮未做** —— 实测无缺陷，属加固而非修缺陷；注意**不要复用 `_poisoned`**
     （会误报 `RequestTimeout` 文案）；
  3. 「问题 A（stop 进行中新交换）」当前是**靠 `HasExited` + 两处宽 catch 过滤**偶然正确，
     无显式状态保证；
  4. 测试夹具在 `%TEMP%` 留 pid 文件/stderr 目录（与既有 `SidecarLifecycleTests` 同款）。
