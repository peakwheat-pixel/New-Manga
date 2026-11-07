---
id: FEA-11-L-S1-B-RECOVERY-REAUTH-1
title: App 显式恢复/重授权入口（B1：撤销→再注册→重导入；零契约、App-only）
kind: implementation
governance_version: 3
status: ready
approval: 用户 2026-11-06「自动推进/全部授权/裁决交 Codex 或 DSH」；权威 scope review `doc/reviews/FEA-11-L-S1-B-RECOVERY-REAUTH-1-scope-r1.md`（fresh subagent `7d2a572e-…`，**READY-WITH-UNFREEZE**；拆卡：**B1 = READY-TO-FREEZE（App-only，零契约 0/18 pins）**；B2（wire 可用性投影）/ B3（扫描侧投影）暂缓）；Codex 不可用（product limit）→ 按用户授权 ZCode 故障转移裁决（记录见卡）；DSH 裁决 D-1…D-10（见下）
suggested_owner: zcode
owner: l-s1b-impl
reviewer: 独立上下文 fresh subagent（未参与实现/返修；只读交付 head；session 见 `doc/reviews/FEA-11-L-S1-B-RECOVERY-REAUTH-1-r1.md`）
depends_on:
  - FEA-11-L-S1-REGISTRY-RESILIENCE-1
  - FEA-11-L-S4-LOCATION-AUTH-REFRESH-1
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1
allowed_paths:
  - doc/tasks/FEA-11-L-S1-B-RECOVERY-REAUTH-1.md
  - doc/reviews/FEA-11-L-S1-B-RECOVERY-REAUTH-1-*.md
  - doc/handoffs/FEA-11-L-S1-B-RECOVERY-REAUTH-1-*.md
  - verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/**
  - apps/desktop-avalonia/src/NewManga.App/Services/SourceImportModels.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/SourceRecoveryModels.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/NullHostController.cs
  - apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Library/ImportDockViewModel.cs
  - apps/desktop-avalonia/src/NewManga.App/Views/V2/Library/ImportDockView.axaml
  - apps/desktop-avalonia/tests/NewManga.App.Tests/SourceRecoveryUiTests.cs
  - apps/desktop-avalonia/tests/NewManga.App.Tests/FakeHostController.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceRecoveryIpcTests.cs
out_of_scope:
  - Host/Avalonia Host 源（`apps/desktop-avalonia/src/NewManga.Host/**`）、CoreClient、`IHostController.cs`、Core/Python
  - C-16/C-15/C-17/任何契约字节；新命令/能力/错误码/字段；C-07 inventory 变化
  - `quarantine_path`（绝对路径）展示；自动重新授权/自动重建 identity/撤销后自动放行
  - B2（`source_list_roots` 可用性投影，需 C-16 v1.5）/ B3（扫描侧投影）；folder 身份键（L-S4-2）；真实用户数据；push
---

# FEA-11-L-S1-B-RECOVERY-REAUTH-1（B1）：App 显式恢复/重授权入口

> **状态：`ready`（App-only，零契约 0/18 pins）。** 来源：`FEA-11-L-S1-REGISTRY-RESILIENCE-1` scope review B 面——恢复路径今天不存在：`source_reset_registry`/`source_revoke_root` App 侧 0 调用；被替换根同路径重导入因复用失效条目而**永久失败**。

## 来源与裁决（2026-11-07）

- 权威 scope review：`doc/reviews/FEA-11-L-S1-B-RECOVERY-REAUTH-1-scope-r1.md` → **READY-WITH-UNFREEZE**，拆卡：**B1（本卡）= READY-TO-FREEZE（App-only，零契约）**；B2（`source_list_roots` 可用性投影，C-16 v1.5，1 pin）暂缓；B3（扫描侧投影）暂缓。
- 关键事实：`source_revoke_root`/`source_register_root` 均为 C-16 v1.4 既有命令，Host handler 与 Core ACK（允许空 grant_ids）已实现，App 只是 0 接线；「撤销失效条目 → 按登记 root 再注册 → 重导入」今天即可走通；闭环依赖 L-S4 A 的原地刷新（已 done）。
- **DSH 裁决 D-1…D-10**：
  - **D-1** 拆 B1/B2/B3：**B1 本轮释放（App-only 零契约）**；B2/B3 暂缓另卡。
  - **D-2** **C-16 v1.5 版本号一次性保留**给「B2 wire 可用性投影 + L-S4-B 零交互恢复枚举」的单一批量载体（避免两卡各自宣称 v1.5）；本卡与 L-S4-B 均不得单独占用。
  - **D-3** B1 写域严格 App-only：Host/Core/契约/`IHostController` 零字节。
  - **D-4** 红线 R-1：**禁止**把 `FindOrRegisterRootAsync` 改为「mint 失败就重注册」（=自动重新授权）；AC-LSB-5 判别。
  - **D-5** Owner：采用 DSH Agent Teams teammate（`l-s1b-impl`）；ZCode 建议记为可用候选。
  - **D-6** AC 采用 AC-LSB-1…10（见下）。
  - **D-7** `source_reset_registry` 返回的 `quarantine_path` 为绝对路径，与 C-16 §7.3 冲突 → **B1 不得展示/记录/渲染**；AC-LSB-7 判别。
  - **D-8** AC-LSB-9 须有 1 条 gated 真实 IPC（闭环：typed 失败→显式重授权→再预览成功→刷新→枚举新代次）。
  - **D-9** allowed_paths 按 scope review §5.2（App 5 文件 + 2 新测试文件 + FakeHostController；不含 `IHostController.cs`）。
  - **D-10** STATUS 测试基线更新为 **3317/10、1570/0/92**（本 closeout 同批）。

## In（冻结）

1. `SourceImportModels.cs`：`ISourceImportController` 增加恢复面（探测/重授权/重置）；展示文案细化（零新码）。
2. `SourceRecoveryModels.cs`（新增）：恢复编排 + 结果模型 + 分流判定。
3. `HostController.cs`/`NullHostController.cs`：实现新成员（复用既有 `HostCommandDispatcher` 路径；不扩 `IHostController`）。
4. `ImportDockViewModel.cs` + `ImportDockView.axaml`：显式命令 + 状态 + 披露文案（脱敏）。
5. 测试：`SourceRecoveryUiTests.cs`（VM 级计数/文案/顺序/幂等/fail-closed）、`FakeHostController.cs` 扩展、`SourceRecoveryIpcTests.cs`（gated 真实 IPC 闭环）。
6. 证据/Handoff/卡面。

## Out

- Host/Avalonia Host 源、CoreClient、`IHostController.cs`、Core/Python；契约/新命令/能力/错误码/字段；`quarantine_path` 展示；自动重授权/自动重建 identity/撤销后自动放行；B2/B3；folder 身份键；真实用户数据；push。

## Acceptance Criteria（v3）

- [ ] **AC-LSB-1 入口仅显式**：预览以 `SOURCE_REGISTRY_UNAVAILABLE` 失败时，只暴露「重新授权此来源」/「重置源授权存储」两个显式动作；未点击前 revoke/register/reset 调用计数均为 **0**。
- [ ] **AC-LSB-2 分流正确**：只读 `source_list_roots` 探针——探测抛 `SOURCE_REGISTRY_UNAVAILABLE` → 只给「重置」；探测成功 + 铸造失败 → 只给「重授权」；探测抛其它码 → 不给任何恢复动作，只显示该码。
- [ ] **AC-LSB-3 撤销→注册顺序与幂等**：同一路径 2 条 stale 非撤销条目都被撤销（generation+1、`revoked_at` 非空），随后只新增 1 条非撤销条目；重复执行不产生重复条目。
- [ ] **AC-LSB-4 部分失败 fail-closed**：撤销成功但注册失败 → 明确「已撤销、未重新授权」+ typed 码；不得显示成功、不得隐式回滚 `revoked_at`；可重试。
- [ ] **AC-LSB-5 不自动重授权（安全核心）**：铸造失败后不自动注册/不自动换候选；`FindOrRegisterRootAsync` 复用选择器语义不变（首个非 revoked 匹配）。
- [ ] **AC-LSB-6 授权面不扩大**：重授权只使用条目已登记 `roots[0]`；恢复成员**无**任意路径入参；`HostCommandRegistry.All` 数量不变；恢复成员不在 `IHostController` 上（C-07 pin 不变）。
- [ ] **AC-LSB-7 脱敏**：恢复文案/通知/日志只含叶子名/typed 码/计数；不含绝对路径/`quarantine_path`；gated IPC 断言 wire/stderr 中 fixture 根路径 0 命中。
- [ ] **AC-LSB-8 零漂移/门禁**：Host/CoreClient/doc-plan/src 零 diff；API inventory PASS；pins 18/18；check（默认+`-TaskPath`）PASS；全量 pytest/.NET 不降（基线 **3317/10、1570/0/92**）。
- [ ] **AC-LSB-9 闭环证据（gated 真实 IPC 1 条）**：注册→同路径替换→预览 typed 失败→显式重授权→再预览成功→重新导入后 `source_locations.registry_id/generation` 原地刷新（L-S4 A）→ `source_list_scan_targets` 返回新代次。
- [ ] **AC-LSB-10 边界/不夸大**：只承诺 **file-source 同路径恢复**；folder 变体受 L-S4-2、重定位走新源；L-S4-1 零交互恢复仍开放；不得写「零交互自愈/根级问题全解」。

## 已知 limitation（本卡）

- **B2**（`source_list_roots` 可用性投影）未做 → 多根健康/逐条管理不可见；**B3**（扫描侧投影）未做。
- **L-S4-1**（零交互自动恢复枚举，需 C-16 v1.5 批量载体）仍开放；**L-S4-2**（folder 身份键）未修。
- 只覆盖 file-source 同路径恢复；重定位（换路径）走「重新导入成新源」。
- `source_reset_registry` 的 `quarantine_path` 不展示（C-16 §7.3 冲突，未来随 UNFREEZE 澄清）。

## 测试要求

| 场景/AC | 命令 | 预期 | 证据 |
|---|---|---|---|
| VM 级（LSB-1/2/3/4/5/7） | `dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests -c Release --filter "FullyQualifiedName~SourceRecovery"` | 全绿；破坏点 RED | `logs/app-unit.log`、`logs/discrimination.log` |
| gated 真实 IPC（LSB-9） | `NEWMANGA_FEA11_IPC=1 dotnet test ... --filter "FullyQualifiedName~SourceRecoveryIpc"` | 1 passed（闭环） | `logs/host-ipc.log` |
| 门禁 | 全量 pytest/.NET、pins、check、API、scope | 不降/不漂移 | `logs/gates.log` |

## 交付记录（Owner 回填；不改 status）

- 待实施。
