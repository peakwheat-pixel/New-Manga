# Codex 独立建议原字节（Q7/Q8）

- 请求方：DSH（MAINT-1 P4-a）
- CLI：`codex-cli 0.162.0`，`-m gpt-6-luna -c model_reasoning_effort=xhigh`，`-s read-only`
- 会话 id：`01a1d658-74e5-74a3-8476-69f32ea95440`
- 退出码：0
- 说明：Codex 无法读取本地 HEAD（Windows 错误 740），其行号证据来自远端快照 `9b068382`，已由 DSH 在 §2 本地复核更正。
- 原文下方逐字节保留，未编辑。

---
## Q7：`FEA-06-RESIDUAL-4`「查看对照」

1. **结论：`OUT`**

2. **依据**

   - 我无法读取指定本地 HEAD `53ce9d55c`：shell 调用被 Windows 错误 740 拒绝，本机文本查看器也无法打开。GitHub `main` 当前可读到的是另一提交 `9b068382`，不能当作 `53ce9d55c` 的证据。以下本地行号是请求中提供的核验锚点，未能在目标 HEAD 独立复核。
   - `doc/tasks/FEA-06-RESIDUAL-4.md:35-38`（远端 `9b068382` 快照）：占位卡记录 `RegionSummary` 无冲突字段、术语/冲突面未接线、当前 V2 无「查看对照」，仅有冲突横幅。
   - 请求指定的 `CoreServiceClient.cs:172-178`、`HostCommandRegistry.cs:191`、`RegionTextProjection.cs:224-281`、`StudioTermsViewModel.cs:36-62`、`FluentResidualBatchATests.cs:613-641`：分别用于核对数据面缺字段、投影是否暴露、UI 是否接线以及横幅测试边界；这些位置在当前 HEAD 未能独立确认。
   - `doc/tasks/FEA-06-RESIDUAL-4.md:42-48`（远端快照）将实现路线与 `NOT_APPLICABLE: 产品范围决定` 路线分开，并要求实现路线做 C-07 additive UNFREEZE 与独立 byte-level 复核。**C-07 契约正文及当前 pin 未能在目标 HEAD 核验。**

3. **成本**

   - `IMPLEMENT`：至少一张 C-07 additive UNFREEZE 载体卡，加一张投影与 UI 实现卡；重算 API inventory/pin，独立字节复核并重冻，再实现对照面板。
   - `OUT`：不触碰冻结契约或 pin；由 DSH 裁决并对相关 Task 做 append-only 收口记录，保留横幅与 typed 原因。

4. **风险**

   - 选 `OUT` 的代价是用户无法并排核看冲突 region 的文本，冲突处理信息较少。
   - 选 `IMPLEMENT` 的代价是扩展可见产品行为并触及冻结契约流程；若投影语义不完整，面板可能呈现误导性的对照。

5. **反悔条件**

   若当前 HEAD 的冻结需求已明确要求用户查看逐 region 冲突文本，或真实用户任务表明横幅与 typed 原因不足以完成安全处理，我会改为支持 `IMPLEMENT`。

6. **保守性自评**

   **UNCERTAIN**：由于未能检查指定本地 HEAD 与 C-07 正文，建议暂采更保守的 `OUT`，不启动契约解冻或扩大 UI 范围。

## Q8：`FEA-11-HOST-AUTH-5` 全链路 e2e

1. **结论：`CONDITIONAL_ON(53ce9d55c 是否已有覆盖 fresh ACK wire 的 HostRuntime 全链路用例)`**

2. **依据**

   - 指定本地 HEAD 同样无法直接读取；以下额外证据来自 GitHub `main@9b068382`，只能作为反证线索，不能视作本地 HEAD 已验证。
   - `apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11Residual4AIpcTests.cs:25-30, 85-161, 170-184, 494-502, 725-747`（远端快照）：已有真实 `HostRuntime.StartAsync`、生产 dispatcher 的 scan → plan/preview/confirm → `source_resync` → ACK → resolve 全链路；辅助方法确实调用 `runtime.Commands.InvokeAsync`。因此“仓内无全链路用例”的说法至少在该快照不成立。
   - `apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs:1042-1055`（远端快照）：同步命令能力门要求 `source.sync.apply/1`；缺少该能力会在 dispatch 前失败。现存用例的 `source_resync` 路径也经过此门。
   - `apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11HostAuthIpcTests.cs:15-25, 42-74`（远端快照）：另有真实 IPC 测试核验 ACK 使用 fresh authorization、wire 携带 fresh 授权并打开 gate；但它不等于同一条 HostRuntime dispatcher 全链路中的 fresh ACK 证明。
   - 请求指定的 `HostRuntime.cs:872-909`、`Fea11Scan2HostRuntimeTests.cs:20-24`、`FEA-11-HOST-AUTH-2.md` AC-F4、`FEA-11-HOST-AUTH-1.md` limitation 1 是核验打包 sidecar 过旧及原始 re-home 来源的锚点；未能在 `53ce9d55c` 独立复核。

3. **成本**

   - 若当前 HEAD 已有上述全链路，但同一链中缺 fresh ACK wire 断言：建议复用现有用例，只补该缺口；预计一张窄范围测试卡，不应重复建设另一套全链路。若当前 HostOptions 确实缺覆盖 seam，再补最小 seam。
   - 若当前 HEAD 没有等价用例：按 `FEA-11-HOST-AUTH-5` 做一张实现卡，覆盖 HostRuntime、生产 dispatcher 和真实 Core；此路线本身不需要改冻结契约或 pin。
   - 打包 sidecar 腿仍须单独标 `NOT_RUN`，不能用测试 Core 的覆盖冒充通过。

4. **风险**

   - 直接 `OUT` 且现存用例未覆盖同链 fresh ACK，会留下授权发放、apply、ACK 与 gate 整合处的验收缺口。
   - 盲目新增完整用例，若现存 4A 测试已覆盖主体链路，会造成重复、较慢的 sidecar 测试，并可能把“已测当前 Core”误读成“已测打包 sidecar”。

5. **反悔条件**

   若在 `53ce9d55c` 核实 `Fea11Residual4AIpcTests` 已通过生产 dispatcher 覆盖当前 apply 语义，且同一链验证 fresh ACK wire，则改为 `OUT`，不再加 e2e。若该用例不存在、被 skip，或未覆盖同链 fresh ACK，则改为 `IMPLEMENT`，优先复用已有 fixture。

6. **保守性自评**

   **UNCERTAIN**：目标 HEAD 不可读，且可读远端快照已出现与卡面“无全链路”描述冲突的测试。保守建议是先按目标 HEAD 核实上述现存测试；若 fresh ACK 尚未在同一 HostRuntime 链中得到证明，采用 `IMPLEMENT` 的验收强度，但复用现有测试路径，保持打包 sidecar 为 `NOT_RUN`。