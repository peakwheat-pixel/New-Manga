---
id: FEA-11-HOST-AUTH-5
title: HostRuntime/dispatcher 全链路 e2e（原 FEA-11-HOST-AUTH-2 AC-F4；含 Core 覆盖 seam）
kind: implementation
governance_version: 3
status: cancelled
disposition: OUT（2026-11-14 DSH；双签：Codex CONDITIONAL/OUT + 独立子 agent OUT；见 doc/reviews/MAINT-1-P4A-Q7-Q8-ADJUDICATION.md。卡面两处前提已过期，另行 errata 更正）
approval: 占位卡：由 `FEA-11-HOST-AUTH-2` Review r1（R1-P2-2）与 DSH 2026-11-08 裁决 re-home；**scope 未冻结，不得实施**；须先独立 scope review
suggested_owner: dsh
owner: null
reviewer: null
depends_on:
  - FEA-11-HOST-AUTH-2
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: complete
evidence_dir: verification/FEA-11-HOST-AUTH-5
allowed_paths:
  - doc/tasks/FEA-11-HOST-AUTH-5.md
  - doc/reviews/FEA-11-HOST-AUTH-5-*.md
  - doc/handoffs/FEA-11-HOST-AUTH-5-*.md
  - verification/FEA-11-HOST-AUTH-5/**
out_of_scope:
  - 未 scope review 前不得实施任何实现
---
# FEA-11-HOST-AUTH-5：HostRuntime/dispatcher 全链路 e2e（占位）

## 来源
`FEA-11-HOST-AUTH-2` 的 **AC-F4**（条件性 HostRuntime e2e）未做 → DSH re-home 到本卡；同时承接 `FEA-11-HOST-AUTH-1` **limitation 1**（HostRuntime e2e）的收窄口径。

## 已核实事实
- 打包 sidecar `core_service.exe` 实测 2026-10-23，**早于 C-17 v1.0**（`HostRuntime.cs:872-909`；`Fea11Scan2HostRuntimeTests.cs:20-24` 已记录），故覆盖 C-17 同步链需 **`HostOptions` 最小 Core 覆盖 seam**（约 4–6 行）。
- 仓内**无** `runtime.Commands.InvokeAsync` 全链路用例（register→scan→plan/preview/confirm→apply→ACK）。

## 验收（草案，待冻结）
- `HostRuntime.StartAsync` Ready（覆盖 seam）；`source.sync.apply/1` 能力存在（缺→**RED**，不得 skip 冒充）；
- 经生产 dispatcher 完成全链路；`Operations.Get(id).State==acknowledged`、gate 开、resolve 新键、源字节守恒、ACK wire 为 fresh；证据须显示测试**实际执行**（不是 skipped）；
- 打包 sidecar 腿单列 `NOT_RUN`（不得写成已覆盖）。

## 处置记录（append-only，2026-11-14）

**结论：OUT / `cancelled`**——作为「新增默认套件全链路 e2e」的实现卡。双签：Codex `CONDITIONAL/OUT` + 独立子 agent `OUT`；DSH 终裁取保守方＝OUT，但**同时改正卡面前提**。

**为何 OUT**：卡要求的东西在 HEAD 上**已经存在并已执行过**，只是不在默认门禁里；照卡面实现会重复造链，并做一条并不存在的 seam。

**必须随本处置同时登记的 4 条事实（缺一条即等于把 skip/NOT_RUN 写成 PASS）**：
1. **默认套件无全链路 e2e**：`Fea11Residual4AIpcTests` 为 opt-in（`:668-679`，`:672` 读 `NEWMANGA_FEA11_IPC`）；`scripts/test.ps1` 不设置该变量（grep 0 命中）。
2. **opt-in 已执行并有日志**：`FEA-11-RESIDUAL-4A.md:66`（AC-R3-2 MET）、`:130`（4 passed / 0 failed）；`verification/FEA-11-RESIDUAL-4A/logs/fea11-ipc-r4a.log` 末行「失败:0，通过:4，跳过:0」；`evidence/after-full-chain.txt` 含 `scan_via=dispatcher`/`apply_via=dispatcher`/`ack=acknowledged`/`old_digest_immutable=1`/`source_conserved=1`/`PASS`。
3. **fresh-ACK 只在直连 gated 用例断言**：`Fea11HostAuthIpcTests.cs:51-61`、`:74-82`、`:106-111`，但走 `CoreServiceClient`+coordinator 直连（`:448-452`），**非 dispatcher**。
4. **打包 sidecar 腿 `NOT_RUN`**（源于 sidecar 早于 C-17，见 errata）。

**因此 AC-F4 不得写成完全 MET**：其原文要求「ACK wire 为 fresh」，该断言目前不在 dispatcher 链里。

**Errata（更正卡面两处已过期前提，不改正文字节）**：
- `:36`「仓内无 `runtime.Commands.InvokeAsync` 全链路用例」→ **为假**。链在 `Fea11Residual4AIpcTests.cs:33-36`，helper `:494-503` 即 `runtime.Commands!.InvokeAsync`；路径 `:65/:72-74` register+grant → `:87` scan → `:108` plan → `:109-122` preview/confirm → `:139` apply → `:160-162` core-committed → `:165-168` gate 拒 → `:171-175` acknowledged → `:179-224` 新键/旧摘要不可变 → `:227` 源字节守恒 → `:232-242` 撤销 fail-closed。
- `:35`「需 `HostOptions` 最小 Core 覆盖 seam（约 4–6 行）」→ **为假**。`SidecarDirectoryOverride` 自 S1（`eb123ad4f`）已存在（`HostOptions.cs:52`、`HostRuntime.cs:1169`，测试 `:729` 直接使用）。
- 仍为真的只有「打包 sidecar 早于 C-17」（`Fea11Scan2HostRuntimeTests.cs:16-17`、`:57-59`），这才是默认门禁跑不了该链的根因。

**两个不足以立卡的 delta**：① r4a 用 `Registry.Register`/`Sources.IssueAsync` 直接建源，未经 dispatcher 的 `source_register_root`；② `FEA-11-RESIDUAL-4A.md:203` 的 D-5 limitation 仍保留。

**重开条件**：① 打包 sidecar 重建到 ≥ C-17（发行打包卡）→ 用打包 sidecar 把该链提升为默认并断言 `source.sync.apply/1`；② `HostCommandDispatcher`/`HostRuntime` 的 source-sync 或 journal 分支任何改动 → 该 opt-in 套件列为必跑门禁；③ 未来任何 FEA-11 触达卡 → 顺手把 `authorized_at` freshness 断言并进 r4a 链（1 条断言、无产品代码）。
若届时确需「默认执行」，正确动作是 1 张纯测试卡把现有 gated 用例提升为默认（0 产品代码、0 契约/pin），并处理 `:708-709` 的 `NEWMANGA_BUILD_PYTHON` 硬编码与 .NET 基线重钉。

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| none | - | NOT_APPLICABLE | - | - | 本卡为占位提案，从未实施（`proposed` 直接处置为 `cancelled`），无 task-env、无派生产物；2026-11-14 DSH 复核 |
