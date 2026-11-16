---
id: FEA-11-HOST-AUTH-3
title: 跨进程崩溃恢复的 grant 语义（C-17 v1.2 计划物化投影 + Host 恢复重铸）
kind: implementation
governance_version: 3
status: done
approval: **scope review r2 `READY-TO-FREEZE`（`doc/reviews/FEA-11-HOST-AUTH-3-scope-r2.md`）** + ZCode 独立裁决（`doc/reviews/ADJ-2026-11-09-ZCODE-ARCH-ADJUDICATION.md`）+ **C-17 v1.2 已冻结**（载体 `doc/reviews/CONTRACT-UNFREEZE-2026-11-09-C17.md`；`verify_pins` 18/18）。**实现范围按本卡冻结；不得自行 UNFREEZE/重算 pin。**
suggested_owner: dsh
owner: dsh
reviewer: 独立上下文子代理（r1–r6；DSH 派发、只读被审 head）
depends_on:
  - FEA-11-HOST-AUTH-2
base_commit: e9ab2ef7c
branch: null
worktree: null
integration_commit: e9ffad62c
delivery_head: e9ffad62c
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/FEA-11-HOST-AUTH-3
allowed_paths:
  - doc/tasks/FEA-11-HOST-AUTH-3.md
  - doc/reviews/FEA-11-HOST-AUTH-3-*.md
  - doc/handoffs/FEA-11-HOST-AUTH-3-*.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - verification/FEA-11-HOST-AUTH-3/**
  - src/bootstrap/core_service.py
  - src/application/sources/materialization.py
  - src/application/sources/errors.py
  - tests/fea11/test_source_plan_materialization.py
  - tests/fea11/test_source_command_parity.py
  # DSH 2026-11-10 裁决扩域：C-17 v1.2 新增 capability 必然改变
  # `core.ping.capabilities` 的精确列表断言（两处），仅更新期望值。
  - tests/core/test_core_service.py
  - apps/desktop-avalonia/src/NewManga.CoreClient/CoreServiceClient.cs
  - apps/desktop-avalonia/src/NewManga.Host/Sources/SourceOperationCoordinator.cs
  - apps/desktop-avalonia/src/NewManga.Host/Sources/SourceReadCoordinator.cs
  - apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs
  - apps/desktop-avalonia/src/NewManga.Host/Sources/HostErrorCodes.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11HostAuthTests.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11HostAuthIpcTests.cs
out_of_scope:
  - **契约字节零改动**：`doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md`（v1.2 已冻 `cdeee487…`）、`FEA-CONTRACT-FROZEN-C17.md`、`CONTRACT-UNFREEZE-2026-11-09-C17.md`、其余 17 份契约、`doc/contracts/FEA-C07_API_INVENTORY.md`
  - **不得改动**：`HostCommandRegistry.cs`、`HostCommandDispatcher.cs`（契约 :196 不登记/C-07 零增量）、`src/infrastructure/resource_channel/source_read_refs.py`、`src/application/sources/runtime.py`、`src/infrastructure/sqlite/source_sync.py`、`src/application/sources/ports.py`
  - 不实现 retry 命令（D-3 out_of_scope）、不修 R-03（另立缺陷卡）、不实现 FEA-13 备份/恢复、不改 UI 面
  - 不把 gated 未跑写成 PASS；不得使用禁止措辞（见 AC-H3-6）
---

# FEA-11-HOST-AUTH-3：跨进程崩溃恢复的 grant 语义

## 来源与冻结依据

- 来源：`FEA-11-HOST-AUTH-2` 的 AC-F3 被范围审查判架构阻塞后 re-home；A/C 路线 `ARCHITECTURE_BLOCKED`，B+D-4 单 pin additive 经 ZCode 裁决批准。
- **C-17 v1.2 已冻结**：新增只读 host-control `GetSourceSyncPlanMaterialized / source_get_sync_plan_materialized`（`plan_id!`/`plan_digest!`），读回 Core 已持久化计划子集（`body_json` 的 kind/source_id/version_id/content_digest/entries/reference_set_digest + 表列 state/expires_at）；`SOURCE_PLAN_NOT_FOUND`/`SOURCE_PLAN_UNAVAILABLE`；capability `source.sync.plan-materialization/1`；零写、不铸 grant。
- scope r2 冻结：19 条 allowed_paths、AC-H3-1…6、证据计划、风险。

## 实现口径

| 侧 | 内容 |
|---|---|
| Core | `core_service.py` 注册 host-control 命令 + handler；`application/sources/materialization.py`（新）单函数 `materialize(store, payload)` closed shape；`errors.py` 两错误码；capability 仅在装配时出现 |
| Host | `CoreServiceClient` 新常量与调用；`SourceOperationCoordinator` 在 `Acknowledge/Recover` 的 **Core-backed 段**（非 `PrepareCompletion`）读物化并重铸；`SourceReadCoordinator.IssueForRecoveryAsync` 窄 seam；`HostRuntime` 注入 `Sources` |
| 重铸输入规则 | `registry_id/generation/identity_digest` 来自 journal `authorization`；**source 路径 = `SourceAccessRegistry` 的 `Roots`（必须恰好 1 个 readable root，否则 typed fail-closed）**；`source_kind` = `ScanTarget.source_kind`；`version_id/entries` = 物化投影。**不得猜 locator/kind** |
| 语义边界 | `_verify_fresh` 只校验 grant 的物理 identity 与 authorization 基线 → 重铸 grant 必须真实、同源，不得伪造；entries 不必与 plan 逐条相同。**冻结矩阵「source 不符」在冻结面不可实现**（Host journal 无 source 字段，物化是唯一 source 权威）——登记 limitation。 |
| 通道 | 新命令 host-control（普通面 `HOST_ONLY_REQUIRED`）；不登记 HostCommandRegistry/C-07 |
| state 语义（r2 定稿） | Core **不过滤** state（`draft/previewed/confirmed/applied/stale` 均可物化，守卫只校验 plan_id/digest）；`applied` 仅为 **Host 恢复的前置条件**（Host 侧拒绝矩阵负责） |

## Acceptance Criteria（AC-H3-1…6）

- [x] **AC-H3-1 契约与字节不回退**：`verify_pins` 18/18（C17 `cdeee487…`，其余 17 零变化）；`git diff --name-only` 不含「不列入」清单；C-17 工作树 SHA-256 不变。 <<MET>>
- [x] **AC-H3-2 Core 新命令**：零写（逐表相等）、closed shape/类型/未知键负例、host-control vs 普通面、typed 矩阵（NOT_FOUND/STALE/UNAVAILABLE/BUDGET）、entries ordinal 升序唯一、missing 目标 null、过期 applied 可读、脱敏器命中面（敏感键/Bearer/sk- 形态）0 命中，归档 wirelog 的裸 `signature` 由 `tools/redact_signature.py` 重脱敏（10 条 → `[redacted]`，0 明文）。 <<MET>>
- [x] **AC-H3-3 Host 重铸**：completion 不再用 journal `GrantIds`（`MintRecoveryGrantsAsync` + `prepared with { GrantIds = recoveryGrants }`）；每 registry `Authorize(liveGeneration, 唯一 readable root)` 后 mint（TTL ≤300s 沿 `IssueAsync`）；**拒绝矩阵 7 例全部 typed（含多 baseline）**（state≠applied→`SOURCE_PLAN_STALE`、无 source/version→`SOURCE_PLAN_UNAVAILABLE`、kind 缺失→`SOURCE_ACCESS_DENIED`、撤销→`SOURCE_GRANT_REVOKED`、registry 缺失→`SOURCE_ACCESS_DENIED`、mint seam 不可用→`CORE_UNAVAILABLE`；journal 保持 core-committed、未 ACK）。 <<MET>>
- [x] **AC-H3-4 真实 kill 恢复一次**：park（`core-committed`）→ `Kill(entireProcessTree)`（断言 dotnet 与全部 Python PID 消失，未证实记 FAIL）→ 新进程 recover 成功一次；行数不变、`read_gate` 0 pending、`commit_digest` 一致、源 sha 不变、**三重防伪**（PID/session/grant_id 不在 journal）；二次调用 0 新帧。**实测 PASS（2026-11-10，驱动 attempt 6）**：`CRASH_POINT=PASS acknowledge_once=1 gates_open=1 rows_unchanged=1 second_call_idempotent=1 commit_digest_match=1 distinct_host_pid=1 distinct_core_session=1 fresh_grant=1`；日志 `logs/crash-driver-attempt12.log`（**10 个 CHECK 全部由记录事实计算**：含 page_bindings 字段级对拍与 journal 存在性；journal 加密故 grant 明文 grep 记 OBSERVE，权威记录为 recover.json）。修复链：host-control 命令名 CamelCase、fixture `reads` 接线、fixture 生产语义注册源路径（ZCode 裁决 E′）、终态 journal 记录重铸 grants、驱动真实 PID 树枚举（12 pid / 1 python，30s 轮询证明 sidecar 全灭）+ DB 行数/源 sha/gate 查询 + page_bindings 字段级对拍。**崩溃反例已实测**（`crash-ack.ps1 -Negative`）：phase 间替换源文件 → recover 被 typed 拒绝（`CHECK negative_typed_refusal=1 code=SOURCE_ACCESS_DENIED` + `CRASH_POINT=NEGATIVE_PASS`，`logs/crash-driver-negative.log`）。 <<MET>>
- [x] **AC-H3-5 变异判别**：M1（复用 journal grant）由拒绝矩阵第 6 例判别（mint seam 不可用时抛 `CORE_UNAVAILABLE` 而非回退）；M2（移除 host-control）→ parity 测试 RED；M3（投影写库）→ 零写断言 RED；M4（删 digest 校验）→ STALE 用例 RED；M5（删 applied 前置）→ 拒绝矩阵第 1 例 RED；M6（猜 kind）→ 第 3 例 RED。证据：`verification/FEA-11-HOST-AUTH-3/mutations/M2…M6*.log`。 <<MET>>
- [x] **AC-H3-6 门禁/范围/不夸大**：`check.ps1`（默认 + `-TaskPath`）PASS；`verify_pins` 18/18；`generate_api_inventory.py --check` EXIT 0；diff ⊆ allowed_paths；工作树 clean；全量 pytest 不低于当轮基线、.NET failed=0；gated 用例默认 skip 且逐条原因。**全量（在门禁运行 head `caaaddc53` 重跑）**：.NET **1811 passed / 0 failed / 109 skipped**（8 项目）；pytest **3468 passed / 0 failed / 10 skipped**（`logs/pytest-full.log`）；`mutations/` 与崩溃日志齐备；`crash-ack.ps1 -Negative` 反例实测；无禁止措辞。 <<MET>>

## 卡面 errata（冻结时已落盘）

- `SOURCE_GRANT_EXPIRED` → **`SOURCE_ACCESS_DENIED`**（整树 kill 后未注册 grant 的码）；AC 与实现诊断以 `SOURCE_ACCESS_DENIED` 为准。
- AC-H3-2 的 state 语义按 v1.2 DTO 全枚举（`draft/previewed/confirmed/applied/stale`），不只 applied。
- 物化读取位置：`Acknowledge/Recover` 的 Core-backed 段，**不进 `PrepareCompletion`**。
- 禁止措辞（AC-H3-6）：任意崩溃点均可恢复 / grant 已持久化 / 自动重新授权 / limitation 3 或 4 已闭合 / 无副作用。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-H3-001 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/crash/host-auth-crash-289e5a14b37c4a679bb9259131638718/library.db` | `-` | `aa02017b8a05c98b6de1704007b5483b838bbbd7f7e362dcc118e9a31024d142` | CANONICAL |
| EV-H3-002 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/crash/host-auth-crash-289e5a14b37c4a679bb9259131638718/park.json` | `-` | `af58fb989983e8aab76179df7014aea7ccd93de97927d17caaabc9f81c641d03` | CANONICAL |
| EV-H3-003 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/crash/host-auth-crash-289e5a14b37c4a679bb9259131638718/pids-after.txt` | `-` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | CANONICAL |
| EV-H3-004 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/crash/host-auth-crash-289e5a14b37c4a679bb9259131638718/pids-before.txt` | `-` | `60d672fc657f6f1cc226001d764adc034a673701aae27e47fbcc315940c934c3` | CANONICAL |
| EV-H3-005 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/crash/host-auth-crash-289e5a14b37c4a679bb9259131638718/recover.json` | `-` | `4acfd914d6ecfad3f3a3a51ed3013b9f483d02c5a9308613921120f732c23d88` | CANONICAL |
| EV-H3-006 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/crash/host-auth-crash-289e5a14b37c4a679bb9259131638718/wire-redacted.ndjson` | `-` | `2d88a55fbaa4fcfd8ff8233f73935ad25a0fd9a828931a2dc011bb3a5b51ea15` | CANONICAL |
| EV-H3-007 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/crash/host-auth-crash-4a181a677b4a486ab99b1ff4ecb8277c/library.db` | `-` | `3755a76d9c5f54c086133b75af95742a50379c80b0089ebc4f65e813a8228efe` | CANONICAL |
| EV-H3-008 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/crash/host-auth-crash-4a181a677b4a486ab99b1ff4ecb8277c/park.json` | `-` | `d7deaa222463bf0bd3a9b8e9b014f708b7d4d244cea70f2f8a926793418aabcf` | CANONICAL |
| EV-H3-009 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/crash/host-auth-crash-4a181a677b4a486ab99b1ff4ecb8277c/pids-after.txt` | `-` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | CANONICAL |
| EV-H3-010 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/crash/host-auth-crash-4a181a677b4a486ab99b1ff4ecb8277c/pids-before.txt` | `-` | `5b04b13948ff455e4cc8c0291bc5f43b2a1d01de889827ca734f894d81818558` | CANONICAL |
| EV-H3-011 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/crash/host-auth-crash-4a181a677b4a486ab99b1ff4ecb8277c/recover.json` | `-` | `e081243fdb642c6094ca350d66ab85198f7dfc5d465d118e296877ab342c3ec8` | CANONICAL |
| EV-H3-012 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/crash/host-auth-crash-4a181a677b4a486ab99b1ff4ecb8277c/wire-redacted.ndjson` | `-` | `2998e17213b66049d773579069fabdd614ae0464d6545f9d252f3cef506d79a5` | CANONICAL |
| EV-H3-013 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/crash/host-auth-crash-588f690edfca4e89b2acbb3ed49c9f11/library.db` | `-` | `4647a4e6742e396a3d7ffac84acbef7d02de2b10494f6683d46812e1e1a0871c` | CANONICAL |
| EV-H3-014 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/crash/host-auth-crash-588f690edfca4e89b2acbb3ed49c9f11/park.json` | `-` | `174068628208d986014be041f465a53dc8d959b4bd88635ec63bb66208fce032` | CANONICAL |
| EV-H3-015 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/crash/host-auth-crash-588f690edfca4e89b2acbb3ed49c9f11/pids-after.txt` | `-` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | CANONICAL |
| EV-H3-016 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/crash/host-auth-crash-588f690edfca4e89b2acbb3ed49c9f11/pids-before.txt` | `-` | `24ccf76dae7d0e4317b19e1f54b3582845401362d890f47105655a48baa212b4` | CANONICAL |
| EV-H3-017 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/crash/host-auth-crash-588f690edfca4e89b2acbb3ed49c9f11/recover.json` | `-` | `5e0129d6447e90be793086878a3b2ccd40a3ed7aed6fefcabfac7a640cdf216a` | CANONICAL |
| EV-H3-018 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/crash/host-auth-crash-588f690edfca4e89b2acbb3ed49c9f11/wire-redacted.ndjson` | `-` | `707ccbc1634e04f54431b6cefb40e1f242d36f969fd3e6bfe325e110b65dc37c` | CANONICAL |
| EV-H3-019 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/crash/host-auth-crash-8e633dd6851e46b7a01f15e4f3d0e195/library.db` | `-` | `1cc4d385599b0be196a682ba6e1c20d135af4bad1d859a4067459a8ea5337b5d` | CANONICAL |
| EV-H3-020 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/crash/host-auth-crash-8e633dd6851e46b7a01f15e4f3d0e195/park.json` | `-` | `64a605fd4cda3cd704dff468a967dfdc7ca0365ef874a109947b0faf3f6ca2c9` | CANONICAL |
| EV-H3-021 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/crash/host-auth-crash-8e633dd6851e46b7a01f15e4f3d0e195/pids-after.txt` | `-` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | CANONICAL |
| EV-H3-022 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/crash/host-auth-crash-8e633dd6851e46b7a01f15e4f3d0e195/pids-before.txt` | `-` | `d6ed0b433e31aa14f6133022bd84a8f73160df3f0f82b15b6086f6d006d09732` | CANONICAL |
| EV-H3-023 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/crash/host-auth-crash-8e633dd6851e46b7a01f15e4f3d0e195/recover.json` | `-` | `d027fee77bcb66a0b7429fc9b293822fc82c58f481c8611f9e971994019724bd` | CANONICAL |
| EV-H3-024 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/crash/host-auth-crash-8e633dd6851e46b7a01f15e4f3d0e195/wire-redacted.ndjson` | `-` | `691d9700ce21ada1c964ca101f72e110e89ef66fcdeccd6ac5dd93b2bb89ebdd` | CANONICAL |
| EV-H3-025 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/crash/host-auth-crash-e8e38b84342040ca9659432306239ffa/library.db` | `-` | `917d258849909713f23ed28722dd4e5ace618b7c9faa5f9e73baf039fc04831e` | CANONICAL |
| EV-H3-026 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/crash/host-auth-crash-e8e38b84342040ca9659432306239ffa/park.json` | `-` | `7100c891670a5e0e468b1f575ae0d4c68aba3797a5595b1ae8ca83b995d1e041` | CANONICAL |
| EV-H3-027 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/crash/host-auth-crash-e8e38b84342040ca9659432306239ffa/pids-after.txt` | `-` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | CANONICAL |
| EV-H3-028 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/crash/host-auth-crash-e8e38b84342040ca9659432306239ffa/pids-before.txt` | `-` | `6e01c0482f562f11c86e8adb103df9b91a8632b0415a086d96f347b5935f7f83` | CANONICAL |
| EV-H3-029 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/crash/host-auth-crash-e8e38b84342040ca9659432306239ffa/recover.json` | `-` | `a26bc794515ff20b8ee4fd266950d6bad268fb3793fb5862b25888c74d3daee1` | CANONICAL |
| EV-H3-030 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/crash/host-auth-crash-e8e38b84342040ca9659432306239ffa/wire-redacted.ndjson` | `-` | `d67defc19a8f8b02ad6e9558a1ba0297008328e8651a02473442fd4b9653648d` | CANONICAL |
| EV-H3-031 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/logs/crash-driver-attempt10.log` | `-` | `55e5f17520524daa90a0e1ce47daafc35c8ee664a5ce4e170cf3f0cd95a4759d` | CANONICAL |
| EV-H3-032 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/logs/crash-driver-attempt11.log` | `-` | `4234811a666bc27711a8bb5f031fe6d1907d10cfe8ba2cdd8c72f46feb8fabcc` | CANONICAL |
| EV-H3-033 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/logs/crash-driver-attempt12.log` | `-` | `acb30d7389f9ce57458fab7a841c8e6f0005cdde10247cb3ab49b87b9e52a35e` | CANONICAL |
| EV-H3-034 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/logs/crash-driver-attempt2.log` | `-` | `f1da91873d1abb248f0fc7e3c9a40cbb914bc254a9fa6db9165656c7d87f934e` | CANONICAL |
| EV-H3-035 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/logs/crash-driver-attempt3.log` | `-` | `3e1466b908dfb677c1a2ada9d58fe42dc8760120d3edda2208aeafc017689f45` | CANONICAL |
| EV-H3-036 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/logs/crash-driver-attempt4.log` | `-` | `bdd4a6f56baa10312cd8e960b61fbbef85d18081f2abf88067133b23e3ebec22` | CANONICAL |
| EV-H3-037 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/logs/crash-driver-attempt5.log` | `-` | `4da4ebdd03a6ef205bba7d9ca58569594ff98a4e4093716c6375f45ffb1defef` | CANONICAL |
| EV-H3-038 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/logs/crash-driver-attempt6.log` | `-` | `ce5f163a08f86be37434e5276ef9a013fa9bc140fd9ab7d7af3ac939576202ae` | CANONICAL |
| EV-H3-039 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/logs/crash-driver-attempt7.log` | `-` | `d4d0e19cd0d35d24d78a63b857f3518752389a62cfaccb71b8551d4a6d2293f9` | CANONICAL |
| EV-H3-040 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/logs/crash-driver-attempt8.log` | `-` | `5e922b21e9e2f3ea69814f1d12788ad76f36c4d3a8393dc61e09f358fd4f0635` | CANONICAL |
| EV-H3-041 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/logs/crash-driver-attempt9.log` | `-` | `5c4da01cab84a5de1af727a451c15d13e7692d8448aa210978c353b67456e1e5` | CANONICAL |
| EV-H3-042 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/logs/crash-driver-negative.log` | `-` | `e7a3cbd50840c754ad2a77735b3d6789dbcb5e310d9e604f3e3f351099aaed8c` | CANONICAL |
| EV-H3-043 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/logs/dotnet-full-console.log` | `-` | `353e5226bcee55b69740397d30c5e16d7e01600953c0adf3c39a1556cd0ee729` | CANONICAL |
| EV-H3-044 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/logs/dotnet-NewManga.App.Tests.log` | `-` | `8f0677206bfe44d3f243ae8b7e58f04ef49dda60ab512523bc14cee878dd8949` | CANONICAL |
| EV-H3-045 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/logs/dotnet-NewManga.Appearance.Tests.log` | `-` | `080915a9d69eb081a9095980db774870818baefb2f47c105b031bd005400a18f` | CANONICAL |
| EV-H3-046 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/logs/dotnet-NewManga.ApplicationCore.Tests.log` | `-` | `62c202de8bf9d5ebabb4f5a2c875b77a3a19fbf850f363f7aaa17d8134dd5c85` | CANONICAL |
| EV-H3-047 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/logs/dotnet-NewManga.CoreClient.Tests.log` | `-` | `5737f83eacf273a054f3a51c2d7ae24ae6474140da4b8b507527860a4c6b2990` | CANONICAL |
| EV-H3-048 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/logs/dotnet-NewManga.DesignSystem.Tests.log` | `-` | `0e83aa60daace8bf893fcf65b0d000cda2c061de2e4dc7fe001c569ec5f379b6` | CANONICAL |
| EV-H3-049 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/logs/dotnet-NewManga.Host.Tests.log` | `-` | `64de275f2026fe83112e4ced69b704aae20d13b41b1762838f7ee3d7cbdff871` | CANONICAL |
| EV-H3-050 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/logs/dotnet-NewManga.Presentation.Avalonia.Tests.log` | `-` | `18cc43aaf1c40148cde99439cf726d7331b878a8fc3b9d61dcbe2167a5839ece` | CANONICAL |
| EV-H3-051 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/logs/dotnet-NewManga.ThemeEngine.Tests.log` | `-` | `8cdd1cc0fee3ab592f2e49d401f5d6806051f68c09218574237e5ca72ec18dc8` | CANONICAL |
| EV-H3-052 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/logs/pytest-full.log` | `-` | `8a0e57138247136d44a15068e9e0f6252ce2e65c1453123ebfaa503b94da0ff8` | CANONICAL |
| EV-H3-053 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/mutations/M1-journal-grant-reuse.log` | `-` | `c76a71c183b7ce2821ec89459e414c1de50abbfaabd8486eaa0220257aef48ed` | CANONICAL |
| EV-H3-054 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/mutations/M2-host-control-removed.log` | `-` | `7efcd68b2e14652eac10bacaf62df5e119390ad1186a3e14c8840fb07efbe157` | CANONICAL |
| EV-H3-055 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/mutations/M3-projection-writes.log` | `-` | `8e0299ec632506d29a4b274fe38fdf034597e11d02e8d3ee26909bb0ac06ace2` | CANONICAL |
| EV-H3-056 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/mutations/M4-digest-check-removed.log` | `-` | `024dfe863f033c191e1d2379c48f14246e554d23d9a4c517f4480707607e3d64` | CANONICAL |
| EV-H3-057 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/mutations/M5-applied-precondition-removed.log` | `-` | `f876871a67ba634246f4982795acc0341588fff985788630068af3b5b9d5894d` | CANONICAL |
| EV-H3-058 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/mutations/M6-guessed-source-kind.log` | `-` | `962fcffd095f73f57036253250bde39d036e5d8001e17ebf97f895f26923b438` | CANONICAL |
| EV-H3-059 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/README.md` | `-` | `b4571d27801c5ab3738306dac7b212af69c5a36bf34f6e0229222df258971da1` | CANONICAL |
| EV-H3-061 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/tools/check_gate.py` | `-` | `1cfc83218522ee582f195b0650519d9a4ca9baeef44e4fd61e621db17c1aa180` | CANONICAL |
| EV-H3-062 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/tools/crash-ack.ps1` | `-` | `43bb77e1c2bd4b9fcd34aa7c568b7476e2807345b13a765f289a6945806fca15` | CANONICAL |
| EV-H3-063 | AC-H3-1…6 | `verification/FEA-11-HOST-AUTH-3/tools/redact_signature.py` | `-` | `33469b9e99e96e49c752806849444d7643c00938f384602d4ced3530758d1423` | CANONICAL |

## 证据计划

`verification/FEA-11-HOST-AUTH-3/`：`crash-ack.ps1`（从 HOST-AUTH-2 骨架复制后改）、`park.json`/`recover.json`、kill 前后 PID 列表、DB 前后导出、脱敏 wirelog、两次 ACK 帧计数、源文件 sha256、`mutations/`（M1–M6 diff+失败输出）、日志（命令头/EXIT）。

## 风险与回退

| 风险 | 处置 |
|---|---|
| 重铸输入缺口（路径/kind） | 规则 + fail-closed（多 root/缺 kind → typed 拒绝） |
| Core-free 默认门禁被破坏 | 物化读取不进 `PrepareCompletion` |
| kill 未真正杀 Python | AC-H3-4 显式 PID 断言；未证实记 FAIL/NOT_RUN |
| 契约回退风险 | AC-H3-1 字节与 pin 断言；需要重算 pin 即停止回 DSH |
| 回退 | `git revert` 实现提交；无 schema/契约变更 |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | NOT_APPLICABLE（main；base `e9ab2ef7c`） | NOT_APPLICABLE | — | — | 未创建 worktree |
| temp | C:/Users/49745/AppData/Local/Temp | DELETE_SAFE | — | — | 测试隔离 |
| build | `apps/desktop-avalonia/**/bin,obj` | NOT_APPLICABLE | — | — | 既有 ignore |
| user-data | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 未访问真实库 |

## Closeout Record

- 结论：**完成**。C-17 v1.2 additive 载体 + Host 恢复重铸 + 真实崩溃正/反例 + 变异判别 + 全量门禁，全部经 **6 轮独立上下文 Review**（r1→r5 处置 + r6 收口终审）收敛。
- 核心证据：`logs/crash-driver-attempt12.log`（10 CHECK 全 =1，`CRASH_POINT=PASS`）、`logs/crash-driver-negative.log`（`NEGATIVE_PASS` / `SOURCE_ACCESS_DENIED`）、`logs/pytest-full.log`（3468/0/10）、`logs/dotnet-full-console.log`（fresh build 1811/0/109）、`mutations/M1…M6`、`crash/<run-id>/`（每次运行归档）。
- 残余 limitation（已登记，非阻塞）：①`signature` 裸值不在 C-16 §7 脱敏器命中面（归档由本卡工具重脱敏，脱敏器本身另立缺陷卡）；②Host journal 无 source 字段，冻结矩阵「source 不符」在冻结面不可实现；③多 baseline/多 root 均 fail-closed，会话层并发 recover 未建模。
- 生命周期：scope r2 冻结 → 实现（Core/Host/测试/证据）→ 6 轮 Review → 收口；`verify_pins` 18/18、C-17 字节零变化、diff ⊆ allowed_paths。
