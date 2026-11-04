---
id: FEA-10-PREREQ-1
title: C-08 块②协议注册（M2-C1 rev 2.12：PrepareRun/AcceptRun + 3 错误码 + host 投影白名单）
kind: implementation
governance_version: 3
status: in_review
approval: **scope approved（r5 Codex，P0=0/P1=0；仅 P2 残留）+ DSH Appointment 2026-11-04**；C-08 冻结记录 §3 为释放前置；等 Codex 额度恢复（13:31 后）认领实施
suggested_owner: codex
owner: codex（本实现会话；DSH Appointment 2026-11-04）
claimed_at: 2026-11-04T06:52:08.999Z
reviewer: codex（全新上下文；实现 Review 待交付；不得由实现者自审）
depends_on:
  - FEA-01-FREEZE-1
base_commit: 1254d4e01608d3c9577872abb1dedea5661889aa
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-10-PREREQ-1
allowed_paths:
  - doc/tasks/FEA-10-PREREQ-1.md
  - doc/tasks/FEA-10.md
  - doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md
  - apps/desktop-avalonia/src/NewManga.CoreClient/Wire/CoreProtocol.cs
  - apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandDispatcher.cs
  - apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandRegistry.cs
  - apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs
  - apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/WireTests.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/HostRuntimeIntegrationTests.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea10PrereqProjectionTests.cs
  - doc/reviews/FEA-10-PREREQ-1-*.md
  - doc/handoffs/FEA-10-PREREQ-1-*.md
  - verification/FEA-10-PREREQ-1/**
out_of_scope:
  - FEA-10 实现（PreparedRun/候选存储/校验/提交 seam；另卡）
  - 既有 Run 命令语义修改、Core 协议 major/minor 提升（除 DSH 明确批准）、wire 行为改动
  - C-01b/C-05/C-08 等冻结契约字节（C-08 记录/冻结矩阵的更新须 DSH 授权）
  - 真实用户数据/AppData/外部卷；push
---

# FEA-10-PREREQ-1：C-08 块②协议注册

> 来源：`doc/plan/FEA-CONTRACT-FROZEN-C08.md` §3「协议注册（块②，释放前置）」；`doc/plan/FEA-C08_RUN_SNAPSHOT_DRAFT.md` SC-R01…SC-R09；`doc/reviews/ADJ-2026-11-01-FEA-DECISIONS.md` 冻结授权；`doc/reviews/ADJ-2026-11-04-NEXT-TASK.md`（Codex 裁决 + DSH 修正）。
> 本 Task 是 **FEA-10 的硬前置**：未完成前 FEA-10 不得 `ready`/`in_progress`。

## 事实与缺口

- C-08 已 **FROZEN**（pin `453f993c…`）；其 §3 规定块②：M2-C1 §5.5 追加 `PrepareRun`/`AcceptRun` 两行、3 个新错误码（`RUN_STALE_PREVIEW` conflict/false、`RUN_PREVIEW_EXPIRED` conflict/false、`RUN_SNAPSHOT_INCOMPLETE` unavailable/true）、§8「Proposed（未观察）」3 行、`:1119` retryable 证据规则例外、`:1122` taxonomy 例外、host 投影层 `allowedRunErrorCodes` 白名单、wire 版本登记 minor 2.12。
- **当前 M2-C1 为 rev 2.11，未含 PrepareRun/AcceptRun 与 3 个错误码**（`grep` 实证）；host 错误投影白名单亦未实现 → C-08 释放前置 (b) 未完成。
- 本 Task **只做协议注册与投影注册**，不实现 Run 的两阶段/候选/提交逻辑；不得提前实现 FEA-10。

## 文件级写域矩阵

| 文件 | 用途 | AC |
|---|---|---|
| `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` | rev 2.12 命令行/结果/3 码/§8/例外登记 | AC1 |
| `apps/desktop-avalonia/src/NewManga.CoreClient/Wire/CoreProtocol.cs` | 业务错误类型 `CoreErrorInfo`/`CoreOperationException`；`code/category/retryable` 白名单投影落点 | AC2 |
| `apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandRegistry.cs` | 客户端命令 registry 映射 | AC1/AC2 |
| `apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandDispatcher.cs` | dispatch/payload 形状校验 | AC2/AC3 |
| `apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs` | host 投影层/`allowedRunErrorCodes` | AC2/AC3 |
| `apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/WireTests.cs` | 注册/投影测试 | AC2/AC3 |
| `apps/desktop-avalonia/tests/NewManga.Host.Tests/HostRuntimeIntegrationTests.cs` | host 投影负向对照 | AC3/AC4 |
| `apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea10PrereqProjectionTests.cs`（新） | 3 码白名单/unknown 降级 | AC2/AC3 |

## 交付物

1. `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`：rev 2.12 增量（PrepareRun/AcceptRun 请求/结果形状、3 码、§8 未观察、retryable/taxonomy 例外；既有行语义不改）。
2. host 投影层：`allowedRunErrorCodes` 白名单 + 未注册码 → `category=unknown` + 安全短消息、**不重写 `code`**；负向对照测试（未扩 M2-C1 时 3 码降级为 unknown）。
3. CoreClient/Host 对应测试；协议注册与既有 Run 命令回归。
4. `verification/FEA-10-PREREQ-1/**` 证据、Handoff、实现 Review 报告（独立上下文）。

## Acceptance Criteria

- [x] **AC1（M2-C1 字节增量与 wire 登记）**：rev 2.12 只新增/登记 §3 所列内容；既有冻结命令/结果/错误/状态/事件语义零改动；文档 diff 逐条对照 C-08 §3；登记 C-08 §3 **已批准的 wire 版本 2.12**（文档 rev 与 Core `PROTOCOL_MINOR` 不是同一概念；是否提升运行 minor 由 DSH 明确批准）；明确客户端 registry/错误投影映射与测试归属（PREREQ 只做文档+host 白名单；Core dispatch/运行实现归 FEA-10）。 <<MET>>
- [x] **AC2（host 白名单）**：`allowedRunErrorCodes` 实现；未注册错误码投影为 `category=unknown`、安全消息、原 `code` 保留；三个新码仅在注册后进入白名单；**未注册码不得触发专属恢复/重试动作，也不得作为 UI 分支依据**。 <<MET>>
- [x] **AC3（负向对照）**：模拟未注册码 → 断言 host 投影降级 unknown（不拒绝、不改 code、无专属恢复/重试动作）；注册后 → 断言按冻结 category/retryable 投影。 <<MET>>
- [ ] **AC4（回归与冻结面）**：既有 Run 命令 wire/测试不回归；`check.ps1`、`verify_pins.ps1` 17/17；C-05/C-15/C-16 字节未改；无生产 Run 实现。 <<PARTIAL: 原定 build 与全量测试未绿，治理指针写域外待 DSH；pins 17/17 通过>>
- [ ] **AC5（证据与 Review）**：真实命令/测试日志（含 EXIT）、范围 diff、独立实现 Review、Handoff、EV/Resource Manifest。 <<PARTIAL: 日志、Handoff 与 EV/资源清单已交；独立实现 Review 和 DSH 集成待进行>>

## 测试要求

| 场景/AC | 计划命令 | 前提/环境 | 期望 |
|---|---|---|---|
| AC1 | `git diff -- doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` + 逐条对照 C-08 §3 | 主工作树 | 仅增量；无旧语义改动 |
| AC2/AC3 | `dotnet build apps/desktop-avalonia/NewManga.sln -c Release --nologo`；`dotnet test apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/NewManga.CoreClient.Tests.csproj -c Release --no-build --filter "FullyQualifiedName~CoreProtocolTests|FullyQualifiedName~AsciiWireTests"`；`dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Release --no-build --filter FullyQualifiedName~Fea10PrereqProjectionTests` | .NET 9；隔离测试数据根 `G:/CODEX/New Manga.workspace/FEA-10-PREREQ-1/`；日志/EXIT 写 `verification/FEA-10-PREREQ-1/logs/` | 白名单/unknown 降级通过；日志可复现 |
| AC4 | `pwsh -NoProfile -File tools/governance/check.ps1`；`pwsh -NoProfile -File tools/governance/verify_pins.ps1`；`dotnet test apps/desktop-avalonia/NewManga.sln -c Release --no-build`（不减少） | 主工作树；日志/EXIT 写 `verification/FEA-10-PREREQ-1/logs/` | PASS；17/17 |
| AC5 | 证据写 `verification/FEA-10-PREREQ-1/**`；`git diff --name-only` 对照写域 | 主工作树 | 全合规；独立 Review approved |

## 文档 rev 与 wire 版本边界（P2-3 澄清）

- C-08 冻结记录 §3 已批准新命令登记为 **wire 版本 2.12**；`M2-C1 rev 2.12` 是该登记对应的**文档修订号**。Core `PROTOCOL_MINOR` 是否需要提升是独立问题，由 DSH 在实施前明确，不因文档 rev 自动提升。
- 本卡登记：M2-C1 命令行/结果形状/3 码/§8 未观察/例外；客户端 registry 与错误投影映射/白名单；负向对照测试。
- Core `_RUN_COMMANDS`/dispatch、`core_assembly.py`、`CoreServiceClient.cs` 的运行实现与兼容回归由 **FEA-10 实现卡**承接；本卡不实现命令、不改运行语义。

## 依赖、风险与阻塞

- 依赖：C-08 已冻结、FEA-01 已冻结；无代码实现前置。
- 风险：M2-C1 是既有运行协议文档，增量必须 additive；host 投影不能改变既有错误处理分支；不得顺手实现 FEA-10。
- 释放条件：scope review approved + DSH Appointment；FEA-10 的 `ready` 以本 Task `done` 为硬前置。

## Closeout Record

- 2026-11-04：Codex 按 DSH Appointment 认领并交付未提交实现快照，status=in_review；无 commit/push；等待独立实现 Review 与 DSH 门禁处置。

## 认领与 Reality Check（Codex，2026-11-04）

- 指定 base `1254d4e01608d3c9577872abb1dedea5661889aa`；实际开始/当前 HEAD `e45baa8b5946a1d581f30b025db045c77e99a6df`，main，Git common dir `.git`，初始工作树 clean。其间两提交仅为 DSH ready 与 Appointment，保留，不重置。
- 本会话只做实现与实施验证，不签发 Review、不 commit/push、不增加子 agent。

## 待裁决（DSH 已处置）

- 并发出现的 `doc/reviews/FEA-10-appointment.md`、`doc/reviews/FEA-10-scope-r6.md` 为 DSH 的 scope r6 归档与 Appointment，来源已核对，纳入 DSH 提交。
- PLAN READY 节点/STATUS 指针已由 DSH 同步：Task 当前 `in_review`，READY 节点随之为空。
- 原定 build/全量/治理在 DSH 原生环境复跑全绿（见 AC-MATRIX DSH 节）；不修改 checker 或历史日志。

## 实施交付记录

- AC1–3 MET（Owner）；AC4 **MET（DSH 原生复跑）**；AC5 PARTIAL（独立 Review 待进行；固定交付 commit 已建立）。精确结果见 `verification/FEA-10-PREREQ-1/AC-MATRIX.md`。
- CoreClient 定向 13/13、Host 定向 23/23；补充完整缓存编译 0 warnings/0 errors；全量 1333 passed / 11 failed / 74 skipped；pins 17/17；未增加过滤/修改 skip 条件。
- 代码写入仅 Commands registry/dispatcher；CoreProtocol 原始解析保持；测试仅 WireTests + 新 Fea10PrereqProjectionTests；M2-C1 为授权增量。PrepareRun/AcceptRun 无运行实现。
- 全量期间重写的 FEA-09 wire evidence 已还原：checkout 被 .git/index.lock 权限拒绝后，使用只读 git cat-file --filters 获取 HEAD checkout-filtered 字节恢复；Git diff 为空，见 logs/fea09-restore.log。
- 用户禁止 commit/push，delivery_head 仍 null；不把开始 HEAD 冒充实现提交。字节绑定 `verification/FEA-10-PREREQ-1/delivery-manifest.json`，由 DSH 固定提交后任命新上下文 Reviewer。
- 环境、NOT_RUN、失败/skip 原因与实际命令/EXIT 见 AC-MATRIX、ENVIRONMENT 与 logs；未在 base 上重跑全量，不声明失败全部为既有。


## DSH 集成验证（2026-11-04）

- build EXIT=0（0/0）；全量 .NET **1344/0/74** EXIT=0；定向 13/13 + 23/23；pins 17/17；范围合规；FEA-09 证据已恢复。
- 证据：`verification/FEA-10-PREREQ-1/logs/dsh/{build.log,full-test.log,commands.md}`。
- 下一步：全新上下文 Codex 实现 Review；approved 后 DSH closeout 为 done，FEA-10 方可 ready。

## Canonical Evidence

（工作树 SHA-256；DSH 提交后回填 commit）

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-001 | FEA-10-PREREQ-1 证据 | `verification/FEA-10-PREREQ-1/AC-MATRIX.md` | pending | `7f8045b756b47f91cb2ebcb0de2061ea664dd1ecf36156fb0eec7a01ca3f85ec` | CANONICAL |
| EV-002 | FEA-10-PREREQ-1 证据 | `verification/FEA-10-PREREQ-1/ENVIRONMENT.md` | pending | `d072f463318f76bfa6a1f99a5660ed3f57466b8359703504cce345947378bf73` | CANONICAL |
| EV-003 | FEA-10-PREREQ-1 证据 | `verification/FEA-10-PREREQ-1/REGISTRATION-COMPARISON.md` | pending | `7b5a250e86e15ddfdc61be7d302cf48e71256978b698d37a46b52e8adf0c5058` | CANONICAL |
| EV-004 | FEA-10-PREREQ-1 证据 | `verification/FEA-10-PREREQ-1/delivery-manifest.json` | pending | `1c0a8e309088e057a6b9e706af53cbf6ef90069e7834243c939349469549a4b8` | CANONICAL |
| EV-005 | FEA-10-PREREQ-1 证据 | `verification/FEA-10-PREREQ-1/logs/build-absolute-dotnet.log` | pending | `1b11e9be196d6d1d825745a11b7c212b56efa9e2599af05d6ca2f1a2e1880df0` | CANONICAL |
| EV-006 | FEA-10-PREREQ-1 证据 | `verification/FEA-10-PREREQ-1/logs/build-cache-no-telemetry.log` | pending | `ce7e3688c160ec9377c7a2478d1407177b0b092466da54c1508a457657c14906` | CANONICAL |
| EV-007 | FEA-10-PREREQ-1 证据 | `verification/FEA-10-PREREQ-1/logs/build-diagnostic.log` | pending | `0313a4002804250c351923f343ab12ca97eb2b825a3ea382a298d1f5e00d0135` | CANONICAL |
| EV-008 | FEA-10-PREREQ-1 证据 | `verification/FEA-10-PREREQ-1/logs/build-direct-environment.log` | pending | `ac0ff9087e2e645326343dce2d22681460b715f782fa852f2a85900ec932c113` | CANONICAL |
| EV-009 | FEA-10-PREREQ-1 证据 | `verification/FEA-10-PREREQ-1/logs/build-env-fixed.log` | pending | `bce15719cce915ccc2f9cacb85c80c24d639dbdc9b45ea74d737777500203381` | CANONICAL |
| EV-010 | FEA-10-PREREQ-1 证据 | `verification/FEA-10-PREREQ-1/logs/build-initial.log` | pending | `10a24215478a9f376a75bb7608c5f4ba97a98d725416af736416d1a87b03f7c8` | CANONICAL |
| EV-011 | FEA-10-PREREQ-1 证据 | `verification/FEA-10-PREREQ-1/logs/build-no-node-reuse.log` | pending | `5d49102781587af934236828b52447402a2d4d09434996d718699aeeeb4acdf6` | CANONICAL |
| EV-012 | FEA-10-PREREQ-1 证据 | `verification/FEA-10-PREREQ-1/logs/build-no-restore-telemetry-optout.log` | pending | `a120cdbe5073ecfc8202613887c2068e62999e5970d7e9fa70d809efd49e9d38` | CANONICAL |
| EV-013 | FEA-10-PREREQ-1 证据 | `verification/FEA-10-PREREQ-1/logs/build-no-restore.log` | pending | `029a5e1f671fe0d80761238b1e2de5c51c5d68ed808c0616b7645c304929e1fd` | CANONICAL |
| EV-014 | FEA-10-PREREQ-1 证据 | `verification/FEA-10-PREREQ-1/logs/build-sdk9.log` | pending | `82726df6384726714c0e09161874e1307f42667c2b797ee296ad1595780f05fe` | CANONICAL |
| EV-015 | FEA-10-PREREQ-1 证据 | `verification/FEA-10-PREREQ-1/logs/build.log` | pending | `0c644665fec3d160003c53676129d76a55e6b245c14f0c0720a2d53c7cd75840` | CANONICAL |
| EV-016 | FEA-10-PREREQ-1 证据 | `verification/FEA-10-PREREQ-1/logs/coreclient-tests.log` | pending | `dd8ea3b163fe2c1d39f8e4c1a8c39687d68821bf9385f195011a136ba1526d91` | CANONICAL |
| EV-017 | FEA-10-PREREQ-1 证据 | `verification/FEA-10-PREREQ-1/logs/dsh/build.log` | pending | `c3184b029e015093cbbbc117b7ef9c2dcf0fb35d3ee24bbe0271fbae4055168e` | CANONICAL |
| EV-018 | FEA-10-PREREQ-1 证据 | `verification/FEA-10-PREREQ-1/logs/dsh/commands.md` | pending | `aae782ed6b4fe6e57b04d13761af8b9dac4af914b05f304e08b003e12ce47755` | CANONICAL |
| EV-019 | FEA-10-PREREQ-1 证据 | `verification/FEA-10-PREREQ-1/logs/dsh/full-test.log` | pending | `10dff3c12b1ebf98b0406b78be6f13846769d9209cfbc1c4497f0d55daaf552f` | CANONICAL |
| EV-020 | FEA-10-PREREQ-1 证据 | `verification/FEA-10-PREREQ-1/logs/fea09-restore.log` | pending | `18c1eedf7600e09e8e896320640d1dd17f6d168375b72d0270d464d1d139d0ed` | CANONICAL |
| EV-021 | FEA-10-PREREQ-1 证据 | `verification/FEA-10-PREREQ-1/logs/governance-final-readable.log` | pending | `d4ed0838794a962ff5447d66e53708010779911245d8f6f54d2fe90da1cd39d2` | CANONICAL |
| EV-022 | FEA-10-PREREQ-1 证据 | `verification/FEA-10-PREREQ-1/logs/governance-final.log` | pending | `64d75e335c23f2144052d987e50d425d5246aa1cf62b2c0959c4c715958d580e` | CANONICAL |
| EV-023 | FEA-10-PREREQ-1 证据 | `verification/FEA-10-PREREQ-1/logs/governance-in-progress.log` | pending | `78391b7a4b827acd26e5ca5c06b535212540b4fae5b8cc834992ed375a5cdeb9` | CANONICAL |
| EV-024 | FEA-10-PREREQ-1 证据 | `verification/FEA-10-PREREQ-1/logs/host-projection-tests.log` | pending | `dc1bb5d10bfa19ea5ecf9c163e6a7acdc9f297cc5ecb54783d40b31fe43891eb` | CANONICAL |
| EV-025 | FEA-10-PREREQ-1 证据 | `verification/FEA-10-PREREQ-1/logs/pins-final.log` | pending | `ac14e6ebf2bdfabfad588ea85d535123e0ed83c1b9b0e3d4a67a631c74acb13c` | CANONICAL |
| EV-026 | FEA-10-PREREQ-1 证据 | `verification/FEA-10-PREREQ-1/logs/pins.log` | pending | `65556ec37b78b9289d5fe0b88dbe97eb8cfbabcf815b9c831543267ae87c36e6` | CANONICAL |
| EV-027 | FEA-10-PREREQ-1 证据 | `verification/FEA-10-PREREQ-1/logs/registration-comparison.log` | pending | `ce3c4d9cce8e44d79f1d2f787f26dce617ff2d3542f6d15a3fd3c6f4b252f45b` | CANONICAL |
| EV-028 | FEA-10-PREREQ-1 证据 | `verification/FEA-10-PREREQ-1/logs/scope-check.log` | pending | `fc9da1fa0f0b8de0786086eeb62873e7d344b5883934616fae6bcd8f17f6a205` | CANONICAL |
| EV-029 | FEA-10-PREREQ-1 证据 | `verification/FEA-10-PREREQ-1/logs/skipped-tests.json` | pending | `1358a9b17c9f07c78924b95e0d8159554fa858f065d2f06412a0ed9a1b88b6b2` | CANONICAL |
| EV-030 | FEA-10-PREREQ-1 证据 | `verification/FEA-10-PREREQ-1/logs/solution-tests.log` | pending | `293405c14bf49ea0038057723e1b70ccb9294e75bd88546c852b1dffb4469fa4` | CANONICAL |
| EV-031 | FEA-10-PREREQ-1 证据 | `doc/handoffs/FEA-10-PREREQ-1-1254d4e01.md` | pending | `7f842b5a1c6caf5b9140165f846fff3292b472ad976c541f82ec6839b70196e7` | CANONICAL |


## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga（main 主工作树） | NOT_APPLICABLE | - | - | 复用主工作树；交付后 clean |
| evidence（仓库） | verification/FEA-10-PREREQ-1/** | NOT_APPLICABLE | 仓库内 | verification/FEA-10-PREREQ-1/AC-MATRIX.md | 逐文件 EV 已登记；命令/EXIT/日志完整 |
| build artifacts | apps/desktop-avalonia/**/bin、obj | NOT_APPLICABLE | 原位 | logs/dsh/build.log | 既有构建目录，不清理/不提交 |
| temp | 既有测试 fixture 的 OS TEMP | NOT_APPLICABLE | - | logs/dsh/full-test.log | 测试自管理；无用户数据 |
| agent-output | -（无仓外派生产物） | NOT_APPLICABLE | - | - | 无 |
| dataset/model | - | NOT_APPLICABLE | - | - | 未使用用户数据/模型 |

## 当前恢复点

- ExecutionState: REVIEW；TaskStatus: in_review；main / G:/CODEX/New Manga；交付提交由 DSH 固定。
- 下一接收者：全新上下文 Codex 实现 Review；Review 通过后 DSH 集成 closeout；FEA-10 以本卡 done 为硬前置。
- Handoff：doc/handoffs/FEA-10-PREREQ-1-1254d4e01.md。
