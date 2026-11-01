---
id: FEA-02-CORE
title: FEA-02-CORE 共享应用状态与 Run 轮询基础（ApplicationCore 抽取）
kind: implementation
governance_version: 3
status: in_review
approval: user_ruling_2026-11-01_U12
suggested_owner: codex
owner: codex
reviewer: c01b-reviewer
depends_on:
  - FEA-01-FREEZE-1
base_commit: bf1c8eb00
branch: feat/fea-02-core
worktree: G:/CODEX/New Manga.workspace/FEA-02-CORE
integration_commit: null
delivery_head: 5efb8f58c88e1acb11eaf53b1eab9135f26f29db
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-02-CORE
allowed_paths:
  - doc/tasks/FEA-02-CORE.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/checkpoints/**
  - doc/reviews/FEA-02-CORE-*.md
  - apps/desktop-avalonia/src/NewManga.ApplicationCore/**
  - apps/desktop-avalonia/tests/**
  - apps/desktop-avalonia/NewManga.sln
  - verification/FEA-02-CORE/**
---

# FEA-02-CORE：共享应用状态与 Run 轮询基础

## 来源与定位

用户 2026-11-01 追加确认（[ADJ 追加裁决](../reviews/ADJ-2026-11-01-FEA-DECISIONS.md) U-12）：**首个实现候选 = `FEA-02-CORE`，由 Codex 承担实现；DSH 负责范围冻结、Review Appointment 与集成。** 选择理由：适合先建立**共享应用状态、意图去重与 Run 轮询基础**；`FEA-03` 额外依赖 `FEA-00a` 数据安全修复，应后置（方案 `:640` 候选依赖）。

**门禁**：FEA-01 稳定端口冻结（[FROZEN v2](../plan/FEA-CONTRACT-FROZEN-FEA01.md)，pin `0370c189…`；任务 `FEA-01-FREEZE-1`）→ 本卡范围冻结 + 独立复核 → `ready` → Codex 实现。

## 范围（范围冻结核心）

- **写域（唯一）**：`apps/desktop-avalonia/src/NewManga.ApplicationCore/**` + `apps/desktop-avalonia/tests/**`（仅与 ApplicationCore 相关的测试文件）+ `apps/desktop-avalonia/NewManga.sln`（**仅新增 ApplicationCore / ApplicationCore.Tests 两条项目条目，不改既有项目与平台配置**）。
- **保留 Current 入口**：现有入口/调度路径**不得删除、不得改变行为**；新实现只能作为可替换层接入（方案 §15.6 FEA-02-CORE 的「保留 Current 原入口；不得双调度」）。
- **不写**：`apps/desktop-avalonia/src/NewManga.App/**` 其它目录、`NewManga.CoreClient/**`、`src/**`（Python）、契约文档、其它 Task 文件。
- **共享组合根**：如需改动组合根/DI 注册，必须先在卡内列出精确文件与理由，经 DSH 范围确认后另批提交（不在默认写域内）。

## 验收标准（草案；范围冻结时以用户确认版本为准）

- [x] **AC1 无 Avalonia 依赖**：`NewManga.ApplicationCore` 不引用 Avalonia 程序集（架构测试/编译期断言：程序集引用清单不含 `Avalonia*`；方案 §15.6 出口「无 Avalonia 引用」）。 <<MET>>
- [x] **AC2 多观察者共享一次轮询**：N 个观察者同时订阅同一 Run/任务状态 → 断言只发生 **1 次**底层轮询（调用计数断言），观察者各自收到同一快照。 <<MET>>
- [x] **AC3 同一意图重试不重复启动**：同一意图键（intent key）在 pending/重试期间的重复请求 → 断言不产生第二个启动（去重命中，返回同一 in-flight 结果）；意图完成后允许新意图。 <<MET>>
- [x] **AC4 请求错误互不串扰**：并发多个请求，其中一个失败（含超时/取消）→ 断言错误只归属该请求（request-scoped error），其它请求结果与状态不受影响，且不污染共享状态缓存。 <<MET>>
- [ ] **AC5 保留 Current 入口（非回归）**：①**基线非回归**——现有入口相关测试项目保持通过（对照基线）；②**结构断言**——本卡 diff 不触 `apps/desktop-avalonia/src/NewManga.App/**`（脚本断言 0 命中）；③**无双调度**——本卡不接线，接线后须验「同一意图只经一条路径启动」。 <<PARTIAL: Current 回归与结构断言通过；全 solution 尚有与基线相同的 3 个 Host junction 清理失败，未满足全量 test 必须通过的交付要求>>
- [x] **AC6 L 前置适用性判定**：按**实际写域**逐项判定 L-1/L-2/L-5（见下节），判定结论与再触发条件写入本卡；前置未满足时本卡保持 `proposed/blocked`。 <<MET>>
- [ ] **AC7 独立复核**：`doc/reviews/FEA-02-CORE-r1.md` 判 `approved`（P0/P1 = 0）。 <<BLOCKED: 待 DSH 按 delivery_head 安排上下文独立复核，本实现会话不得自审>>

## L 前置适用性判定（用户要求：按实际写域判定，不机械复制）

| 保留项 | 本卡写域是否触及 | 判定 | 依据 / 再触发条件 |
|---|---|---|---|
| **L-1** 四表 DDL 未冻 | **否**——本卡只做 Avalonia 侧 ApplicationCore 内存状态/轮询/去重；不访问 SQLite、不定义 schema | **NOT_APPLICABLE**（本卡） | 若实现新增任何 DB/schema 访问 → 立即转 `blocked`，并先完成 L-1 前置（DDL 冻结 + pin） |
| **L-2** M2-C1 字节修订（`TRASH_*` 3 码 + Run 错误码白名单） | **否（边界）**——本卡消费既有 Run 错误语义，但**不新增/不修改 wire 码表，也不实现 host 投影白名单**（属 Host 层）；如需新增错误码 → 属 M2-C1 | **NOT_APPLICABLE**（本卡） | 若实现 ①新增 `RUN_*`/`TRASH_*` 码 ②改主机白名单 ③**把既有 Run 错误码→category 映射 / host 投影白名单逻辑搬入 ApplicationCore** → 转 `blocked`，先完成 M2-C1 独立字节修订 |
| **L-5** 整库恢复独占锁 | **否**——本卡不触及备份/恢复/维护窗口 | **NOT_APPLICABLE**（本卡） | 若实现触及恢复或维护互斥 → 转 `blocked`，先按 L-5 的 4 步序列补 AC |

> 说明：`doc/plan/FEA-C11_IMPL_PREREQS.md` §0 的禁则在此适用——**不适用不等于豁免**；一旦写域扩展到对应范围，立即转 `blocked` 并补前置。

## 首批验收聚焦（用户明确）

无 Avalonia 依赖 · 多个观察者共享一次轮询 · 同一意图重试不重复启动 · 请求错误互不串扰。

## 禁止范围

- 不改任何冻结契约字节（15 份 pin）；不改 `G-DELETE-IMPL` 状态；不动用户数据；不 push。
- 不删除/不改 Current 入口行为；不做双调度。
- 不在本卡内顺手修 `FEA-00a`（数据安全）或其它候选 Task 的问题。

## 测试要求（草案）

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | `dotnet test apps/desktop-avalonia/tests/NewManga.ApplicationCore.Tests/NewManga.ApplicationCore.Tests.csproj --verbosity minimal` | Windows / net9.0 / SDK 10.0.401 | executed，L2；全部新增测试 25 passed / 0 failed / 0 skipped | verification/FEA-02-CORE/final-test.log；test-summary.json |
| AC2 | 同上，`Many_observers_share_one_query_and_the_same_snapshot_then_one_next_tick` | 注入时钟，32 订阅 + 32 refresh | executed，底层计数 1，共享相同快照；下一 tick 只增 1 | verification/FEA-02-CORE/README.md |
| AC3 | 同上，`Concurrent_retries_of_pending_intent_share_one_start_task_and_result` | 64 并发调用 | executed，一次启动，同一 task/result；新意图可开始 | verification/FEA-02-CORE/test-summary.json |
| AC4 | 同上，RequestExecutor / IntentCoordinator / RunMonitor 失败、超时、取消、迟到结果测试 | 单测，不运行 Host/Core | executed，错误局部化；失败不覆盖成功缓存 | verification/FEA-02-CORE/test-summary.json |
| AC5 | `dotnet build apps/desktop-avalonia/NewManga.sln --verbosity minimal`；`dotnet test apps/desktop-avalonia/NewManga.sln --no-build --logger 'trx;LogFilePrefix=final' --results-directory 'build/FEA-02-CORE/final-results' --verbosity minimal` | 默认项目输出；TEMP/TMP 隔离到 task-env | executed，build EXIT=0；test EXIT=1，905 passed / 3 failed / 60 skipped；943 既有用例 outcome 变化 0；Current 396 passed / 7 skipped | verification/FEA-02-CORE/final-build.log；final-test.log；test-summary.json |
| AC5/6 | `pwsh -NoProfile -File verification/FEA-02-CORE/verify-boundaries.ps1`；`pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 本工作树；固定 base/release | executed，边界 PASS，pin 15/15 PASS；L-1/L-2/L-5 判定不变 | verification/FEA-02-CORE/boundaries.log；pins.log |

所有 skip 的逐项名称与原因见 test-summary.json（既有 sidecar fixture 未配置）；没有新增 skip/filter。未执行 L3/L4、真实 Host/Core 接线、GUI 验证。完整基线失败、精确命令、环境与试验路径见验证 README。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| CORE-RESULT | AC1–AC6；限制/命令 | verification/FEA-02-CORE/README.md | 5efb8f58c | 96a0663fd3c5907df488bad371763531736823e5486441f152f57eee40da5003 | CANONICAL |
| CORE-TESTS | AC1–AC5；逐项 outcome / skip 原因 | verification/FEA-02-CORE/test-summary.json | 5efb8f58c | 5cbbb11608b64a31129132fa2fa2b49c6829e2f5b0fd9064d17c36d8542e87e6 | CANONICAL |
| CORE-BOUNDARY | AC5/AC6 | verification/FEA-02-CORE/boundaries.log | 5efb8f58c | 0aaa1a39028e8b7f6f0fa74b6166909c89cfdcb3c2fd8fb8db9e3558629bdff5 | CANONICAL |
| CORE-PINS | 冻结字节保留 | verification/FEA-02-CORE/pins.log | 5efb8f58c | 9dbee7d8ed4c79560914c576bac42deed72e37308e7cc4a323c551e9c6f2273f | CANONICAL |
| CORE-BUILD | solution build | verification/FEA-02-CORE/final-build.log | 5efb8f58c | 41d19138b94149a2434e2e88307294fd0e9228efdc9b1a9099296a432ccd7545 | CANONICAL |
| CORE-TEST-LOG | solution test（FAIL 如实保留） | verification/FEA-02-CORE/final-test.log | 5efb8f58c | b04fbe7e1e9fc741c09d7f91058a27b3c035be18d81ef3e58d18149cf7033db2 | CANONICAL |
| BASE-BUILD | AC5 基线 build | verification/FEA-02-CORE/baseline-standard-build.log | 5efb8f58c | 88e9a5b6224dcd5168988200fbf50f3b2a0b644fb059dd292ad2d168802b8cc1 | SOURCE_PIN |
| BASE-TEST | AC5 基线 test（同 3 失败） | verification/FEA-02-CORE/baseline-standard-test.log | 5efb8f58c | 188843c96cdfe47c498da38a025e05ec768bdcdd721bfd1375d06a07f0c61d68 | SOURCE_PIN |
| CORE-COMPARE | 汇总程序 | verification/FEA-02-CORE/collect-test-results.ps1 | 5efb8f58c | - | SOURCE_PIN |
| CORE-BOUNDARY-SCRIPT | 边界程序 | verification/FEA-02-CORE/verify-boundaries.ps1 | 5efb8f58c | - | SOURCE_PIN |

## Resource Manifest

全部为本 Task 派生资源，当前保留待复核；未清理/移动/删 worktree。下列为保守保留记录，最终处置及 closeout 仍由 DSH 决定；`resource_closeout_status` 保持 pending。未读取/更改用户漫画、数据库、模型缓存。

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/FEA-02-CORE | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/FEA-02-CORE | verification/FEA-02-CORE/README.md | feat/fea-02-core；delivery_head 为本卡固定提交；有待审独有提交，不能删除 |
| build/artifact | G:/CODEX/New Manga.workspace/FEA-02-CORE/build/FEA-02-CORE | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/FEA-02-CORE/build/FEA-02-CORE | verification/FEA-02-CORE/test-summary.json | 原 TRX 的 hash 已登记；构建/测试已结束，基线和交付对照仍被引用 |
| task-env/temp | G:/CODEX/New Manga.workspace/task-envs/FEA-02-CORE | PRESERVE_UNKNOWN | G:/CODEX/New Manga.workspace/task-envs/FEA-02-CORE | verification/FEA-02-CORE/README.md | 含早期 artifacts 与 junction 清理失败的残留；未逐项核销，禁止自动删 |
| agent-output | G:/CODEX/New Manga.workspace/agent-output/codex/FEA-02-CORE | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/agent-output/codex/FEA-02-CORE | verification/FEA-02-CORE/README.md | 原始尝试与基线/交付日志保留；判别力日志已入库，未执行清理 |
| bin/obj/test-artifacts | G:/CODEX/New Manga.workspace/FEA-02-CORE/apps/desktop-avalonia | PRESERVE_UNKNOWN | G:/CODEX/New Manga.workspace/FEA-02-CORE/apps/desktop-avalonia | verification/FEA-02-CORE/README.md | 各项目默认 bin/obj 及测试证据均在本工作树，未触碰主仓库构建产物 |
| dataset/model/user-data/exchange | - | NOT_APPLICABLE | - | - | 仅本地单元测试；没有数据集、模型、用户数据或交换目录 |

## Closeout Record

- 范围冻结完成（2026-11-01）：写域 = `NewManga.ApplicationCore` + 对应测试 + sln 两条项目条目；R2 `approved`（`FEA-01-FREEZE-r2`）；交 Codex 实现；`G-DELETE-IMPL` 仍 OPEN。
- Codex 开始实现（2026-11-01）：从 `bf1c8eb00` 新建 linked worktree，快进纳入仅含任务释放元数据的 `2546410c4`；源代码基线不变。工作树 `G:/CODEX/New Manga.workspace/FEA-02-CORE`、分支 `feat/fea-02-core`。未接线 Current，不触发 L-1/L-2/L-5 再触发条件；AC7 留待 DSH 安排上下文独立复核。
- 实现提交 `5efb8f58c`：共享 Run 轮询/快照、进行中意图去重、请求级结果；25 项新增 L2 测试通过；Current 无代码差异。全 solution test 尚未通过（基线同 3 项 Host Dispose 失败），AC5 PARTIAL、AC7 BLOCKED，不能标 approved/done。
- Handoff：[FEA-02-CORE-5efb8f58c](../handoffs/FEA-02-CORE-5efb8f58c.md)。没有修改冻结契约/pin、Gate 状态或其它 Task；没有 push。
