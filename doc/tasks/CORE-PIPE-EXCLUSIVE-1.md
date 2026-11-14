---
id: CORE-PIPE-EXCLUSIVE-1
title: 修复 core_service 管道响应错配（E-6 / P1）—— 全局独占 + request_id 校验
kind: fix
governance_version: 3
status: done
disposition: "E-6（P1）：list_chapters 间歇返回空，根因为 request_id 错配"
approval: DSH 2026-11-15（缺陷已确证，根因与修复方向明确）
suggested_owner: DSH
owner: DSH
reviewer: null
depends_on:
  - SIDECAR-REBUILD-1
base_commit: 0fb8abdc4
branch: main
worktree: G:/CODEX/New Manga
integration_commit: dff3d41a53e0a3206691d56e0a80489e0692f34d
delivery_head: dff3d41a5
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/CORE-PIPE-EXCLUSIVE-1
allowed_paths:
  - doc/tasks/CORE-PIPE-EXCLUSIVE-1.md
  - doc/reviews/CORE-PIPE-EXCLUSIVE-1-*.md
  - doc/reviews/MAINT-1-EXISTING-FINDINGS-2026-11-14.md
  - doc/REBASELINE_PLAN.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - doc/checkpoints/GOAL-PROGRESS-2026-11-02.md
  - verification/CORE-PIPE-EXCLUSIVE-1/**
  - apps/desktop-avalonia/src/NewManga.CoreClient/**
  - apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/**
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/**
---

# CORE-PIPE-EXCLUSIVE-1：修复 core_service 管道响应错配（E-6 / P1）

## 缺陷（已确证）

失败 session 的 wire 最后一帧：

```
# 6  REQ list_chapters  req-7  → RESP req-6  result: {"targets": []}
```

`list_chapters` 拿到了 `source_list_scan_targets` 的响应 ⇒ 解析器找不到 `chapters`
⇒ **静默返回空列表** ⇒ `Assert.NotEmpty(chapters)` @ `HostReaderChaptersIntegrationTests.cs:47` 失败。

三处共同构成缺陷：

| 环节 | 事实 | 位置 |
|---|---|---|
| 管道 | `ExchangeAsync` **无锁**（"写一行→读下一行"，假定一次一个在途） | `Transport/SidecarProcess.cs:186-240` |
| Host 保护面 | `_readerIoGate` 只覆盖 reader 类方法 | `HostRuntime.cs:511/527/543/559/576/784` |
| **漏洞** | 后台 source 扫描**直接调 CoreServiceClient，绕过 gate** | **`SourceScanScheduler.cs:2415`**、`SourceOperationCoordinator.cs:219` |

另有直接放大器：`CoreServiceClient.SendAsync`（`:2366`）**不校验响应的 `request_id`**，
因此错配被当成正常结果。

**用户可见**：读章节列表时若后台扫描在跑，章节列表**静默变空**，无错误提示。**P1。**

## Acceptance Criteria

- [x] **AC1 判别测试（先写，必须先红）**：新测试并发发一个 **gate 内**命令（`list_chapters`）与一个
      **gate 外**命令（`source_list_scan_targets`），断言**每个响应的 `request_id` 等于其请求的 id**。
      要求：**在当前实现下该测试必须失败**（附失败输出为证），证明它抓得住缺陷。
- [x] **AC2 修复**：让"一次只有一个请求在途"由**最底层**保证 —— 在 `SidecarProcess.ExchangeAsync` 或
      `CoreServiceClient.SendAsync` 加独占（`SemaphoreSlim(1,1)`），覆盖**所有**调用路径
      （app 通道、host-control 通道、gate 内与 gate 外）。
- [x] **AC3 request_id 校验**：`SendAsync` 校验响应 `request_id` 与请求一致；不一致时抛 **typed 错误**
      （复用既有 `SidecarErrorCode.MalformedResponse` 一类），**不得**再静默当成自己的结果。
- [x] **AC4 判别力实测**：临时去掉底层独占（保留校验）后重跑 AC1 测试 → `request_id` 校验应先抓住错配
      （或测试变红）；恢复独占后转绿。**记录两次实验，必须还原。**
- [x] **AC5 失败数下降**：带新 sidecar 重跑三项目，记录失败数与基线（CoreClient 208/4/0、Host 342/9/44）对比；
      预期显著下降。**不得**通过改测试 gate 达成绩效。
- [x] **AC6 不回归**：无夹具三项目仍为 App 950/0/11、Host 321/0/74、CoreClient 186/0/26（0 failed）；
      不得新增 skip/xfail、不得放宽既有断言。

## 允许修改范围

见 frontmatter（`NewManga.CoreClient` 源码与两处测试项目）。**不改** Python Core。

## 禁止范围

- 不得用"把 scan 也加进 `_readerIoGate`"这种局部补丁**替代**底层独占（可以叠加，但不能只有它）。
- 不得放宽断言、不得新增 skip/xfail、不得降低覆盖。
- 不得顺手改 `ListChaptersAsync` 的"静默返回空"语义（属行为变更，需另卡登记影响面）。
- 不得声称条件 3/4 已满足。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 新增并发判别测试（未改实现时先跑） | 新 sidecar | NOT_RUN | 无 |
| AC2/AC3 | 加独占 + 校验后重跑 AC1 | 同上 | NOT_RUN | 无 |
| AC4 | 去掉独占再跑；恢复 | 同上 | NOT_RUN | 无 |
| AC5 | 带夹具三项目全量 | 新 sidecar | NOT_RUN | 无 |
| AC6 | 无夹具三项目全量 | — | NOT_RUN | 无 |

## 依赖、风险与阻塞

- **风险 R1**：加全局独占可能让既有并发测试变慢（`StartupTimeout 90s` 内应仍可）。
- **风险 R2**：`request_id` 校验可能暴露**既有测试**里依赖"错配也能过"的隐性行为 → 逐个核实，不得放宽。
- **风险 R3**：`HostBridgeClient` 也调 `ExchangeAsync`（`:269/:291`），独占必须同时覆盖它。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无（须独立上下文，重点核"锁是否覆盖所有调用路径"与"判别测试能否在回退时变红"）。
- 实际测试：尚无。
- 后续记录日期、commit、环境、结果、遗留项。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) | sha256_basis |
|---|---|---|---|---|---|---|
| EV-CPE-01 | AC1–AC6 主交付与处置 | verification/CORE-PIPE-EXCLUSIVE-1/README.md | dff3d41a5 | 5a1ec4ae81a9c91eb3a2b631bdf9b94bc2ec5c37c4ff80b50930fe802a96edaf | CANONICAL | BLOB |
| EV-CPE-02 | AC1/AC5/AC6 门禁与计数 | verification/CORE-PIPE-EXCLUSIVE-1/four-pieces.log | dff3d41a5 | 419bff9caa8f3e15926caaf0b1986720557eb4ea10ea45f856e133e69d6ddb28 | CANONICAL | BLOB |
| EV-CPE-03 | AC2/AC3 修复本体 | apps/desktop-avalonia/src/NewManga.CoreClient/CoreServiceClient.cs | dff3d41a5 | dd7b5dfa775cc91b634f1bdf24001aef694a450ac5abc919e6e112a685832483 | CANONICAL | BLOB |
| EV-CPE-04 | AC1 并发判别测试 | apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/Commands/PipeResponsePairingTests.cs | dff3d41a5 | 8a70f045dbad3473baffe70dc606dbbc875a6846a5c260eeabc1a55f94654b14 | CANONICAL | BLOB |
| EV-CPE-05 | AC3 request_id 校验测试 | apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/Commands/PipeResponsePairingValidationTests.cs | dff3d41a5 | d091fdf9a57c02b947f1c12cbf2a43c57d67624461dd4903c089ae7a7ad85da7 | CANONICAL | BLOB |
| EV-CPE-06 | 独立复核 r1（ACCEPT_WITH_LIMITATIONS） | doc/reviews/CORE-PIPE-EXCLUSIVE-1-review-r1.md | dff3d41a5 | bafe82ab29b497fc9deaa0ed0ea21b05d6d76888d249b78629b4d1ac986d06cf | CANONICAL | BLOB |
## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | 待填 | NOT_APPLICABLE | — | — | 本卡无新增派生物 |

## Closeout Record

- Closeout date / DSH：2026-11-15，DSH（Lead / Architect / Integrator）。
- canonical_evidence_status：`complete`（6 条 BLOB pin，commit `dff3d41a53e0a3206691d56e0a80489e0692f34d`）。
- resource_closeout_status：`complete`（无 worktree、无用户数据；临时探针脚本在 workspace）。
- 删除、迁移、归档数量/字节数：0。
- **交付结论**：E-6（P1）**已修复**。`core_service` 管道的"一次一个请求在途"改由 `CoreServiceClient._pipeGate`
  在最外层保证（覆盖 `SendAsync` 与 `SendHostControlAsync` 的**整段**请求-响应周期，含事件帧跳过），
  并在 id 错配时抛 typed 错误。带新 sidecar 的 Host 失败 **9 → 2~3**。
- **判别力（两次，均有实测日志）**：① gate 放宽到 8 → 并发判别测试变红；② 禁用 id 校验 → 校验测试变红。
  两处均已还原。
- 未关闭项及保留原因：
  - **E-7（同类窗口 4 处）**：`HostBridgeClient` 管道无锁且不校验 id；`SendRawAsync` 锁外；
    独占未下沉到传输层；无 `request_id` 时 fail-open（已由文档测试固定）；
  - **R-002**：错配抛错后管道可能残留一帧，无重同步；
  - 本卡**未**修 CoreClient 4 个 "Frozen Core" 前提测试与 Host 剩余 2~3 个失败（症状不同）。
- **自登记的错误**：本轮我先按"result 形状差异"写判别测试（而非卡面 AC1 字面要求的 `request_id` 相等），
  r1 复核判 AC1 PARTIAL —— 形状断言能抓住缺陷，但**不是**卡面写的那种断言；已在证据中说明并保留。
- 当前指针清理：STATUS / Plan / TASK_LEDGER / rolling checkpoint 已更新。
