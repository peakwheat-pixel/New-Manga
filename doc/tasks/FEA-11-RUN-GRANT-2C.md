---
id: FEA-11-RUN-GRANT-2C
title: 2C 长 Run 续期实现（Host-only 周期重铸 grant + 重发 AuthorizeSourceReadForRun；L-G1 降级）
kind: implementation
governance_version: 3
status: ready
approval: 用户 2026-11-06「自动推进/全部授权/裁决交 Codex 或 DSH」；PREREQ `FEA-11-RUN-GRANT-2C-PREREQ-1` done（C-06 v1.3 + C-16 v1.6，2 pins，`7317837d5`）；权威 scope `2C-LONG-RUN-RENEWAL-scope-r1` + ZCode 裁决 `cbdf231a-…`（APPROVE 2 pins/方案 a）；旧别名 `FEA-11-2C-LONG-RUN-RENEWAL-1` 仅登记、不得并存；DSH D-1…D-10 见下
suggested_owner: codex
owner: null
reviewer: null
depends_on:
  - FEA-11-RUN-GRANT-2C-PREREQ-1
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-11-RUN-GRANT-2C
allowed_paths:
  - doc/tasks/FEA-11-RUN-GRANT-2C.md
  - doc/reviews/FEA-11-RUN-GRANT-2C-*.md
  - doc/handoffs/FEA-11-RUN-GRANT-2C-*.md
  - verification/FEA-11-RUN-GRANT-2C/**
  - apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs
  - apps/desktop-avalonia/src/NewManga.Host/Sources/SourceReadCoordinator.cs
  - apps/desktop-avalonia/src/NewManga.Host/Sources/RunGrantRenewal.cs
  - apps/desktop-avalonia/src/NewManga.Host/HostOptions.cs
  - apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandDispatcher.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/RunGrantRenewalTests.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11RunGrantIpcTests.cs
  - tests/fea11/test_source_run_grant.py
out_of_scope:
  - C-06/C-16 契约字节（PREREQ 卡负责）；C-05/C-15/C-17/C-07/M2-C1
  - `src/**`（Core/Python）零 diff；Run wire/TTL≤300s/撤销/失联/错误闭集/能力
  - App/UI；自动重新授权；B2/folder/L-S4-1/L-R1/L-G16；真实用户数据；push
---

# FEA-11-RUN-GRANT-2C：2C 长 Run 续期实现（proposed 占位）

> **状态：`ready`；PREREQ（C-06 v1.3 + C-16 v1.6）已 done；按卡面 In/AC 实施（Host-only 续期）。**

## 目标（草案）

Run 由 Core 后台串行整跑，grant 在 dispatch 前一次性铸造（`SourceReadCoordinator.cs:586` `+300s`）→ 排队/长 Run 未开始或中途即失权（`PROVIDER_FAILED`/`DB_FAILED`）。实现 **Host-only 周期续期**：Run 非终态期间对同一冻结 `{command, scope}` 重铸 grant + 重发 `AuthorizeSourceReadForRun`（零 Core、零 Run wire、零新命令/能力/错误码）。

## 候选 Scope（待 PREREQ 后冻结；依据 scope review §3 + ZCode D-1…D-10）

- In：新 `RunGrantRenewal.cs`（interval=240s/maxRenewals=12/TimeProvider/HostOptions）+ `HostRuntime` 接线（`AuthorizeSliceAsync` 返回 `RunAuthorizationResult`，不得「发了就算成功」）+ `SourceReadCoordinator` 刷新/计数/停止条件（禁碰 `+300`/TTL/`MaxRunGrants`/`MaxTrackedPayloads`）+ dispatcher post-dispatch 钩子 + 单测 + `tests/fea11/test_source_run_grant.py` in-process fake clock 判别 + gated「同 scope 二次 mint+bind+可读」。
- Out：`src/**` 零 diff；Run wire/TTL/撤销/失联/错误闭集/能力；App/UI；自动重新授权；B2/folder/L-S4-1/L-R1/L-G16；真实用户数据；push。

## Acceptance Criteria（草案，PREREQ 后冻结）

- [ ] **AC-2C-1 续期主 AC**：Run 非终态期间，同一冻结 `{command, scope}` 在 TTL 前被重铸并重发 `AuthorizeSourceReadForRun`；in-process fake clock 前推 300s+ 后页读/提交仍成功；判别性：删续期 → 回到 `PROVIDER_FAILED`/`DB_FAILED` RED。
- [ ] **AC-2C-2 不延长/不扩 scope/不改 command**：旧 grant `expires_at` 不变；每次新 grant id；scope/command 逐字节同值；判别性：复用旧 grant 或换 scope/command → RED。
- [ ] **AC-2C-3 撤销/漂移即停**：续期前重走 `Registry.Authorize`+facts；revoked/generation 漂移/根替换 → typed 停止、不发送、不自动重建 identity；判别性：绕过 Authorize → RED。
- [ ] **AC-2C-4 失败不放行/不自动重试成自动恢复**：续期失败 typed；不重试 reattest/不自动重新授权；整请求任一页不可授权 → 不发送部分映射。
- [ ] **AC-2C-5 预算/间隔**：`interval + 单轮 mint 时长 < 300s`；每轮单次发送（`_gate` 串行）；单轮超限 typed skip + 计数入 EV；不得并行绕 gate。
- [ ] **AC-2C-6 接线点/无 App 改动**：dispatcher post-dispatch 钩子；`HostCommandDispatcher.cs` 属 Host 内部零 wire；App 零 diff；`+300`/TTL/`MaxRunGrants`/`MaxTrackedPayloads` 既有值不变。
- [ ] **AC-2C-7 L-G1 只降级不关闭 + 不夸大**：STATUS/Handoff/EV 写「有续期 + 子限制」（单步 >300s/续期失败/L-G2/L-G9/L-R1/L-G16）；不宣称任意长 Run 可用/自动恢复/自动重新授权。
- [ ] **AC-2C-8 门禁**：pins 18/18（C06 v1.3/C16 v1.6 新值）；check（默认+`-TaskPath`）PASS；API；scope ⊆ allowed_paths、`src/**` 零 diff；全量 pytest/.NET 不降（起点重测）；跑后恢复 `verification/FEA-09`。

## 依赖与下一步

- 依赖：`FEA-11-RUN-GRANT-2C-PREREQ-1`（done 后 DSH 冻结 release）。
- Release 后走实现 → 独立 Review → 集成门禁 → closeout → push。
