# Q7/Q8 裁决记录（MAINT-1 P4-a，2026-11-14）

流程：按 DSH 裁决矩阵，产品/验收取舍须由 **Codex 与 ZCode 各出独立书面建议**，DSH 终裁并记录依据。

## 0. 意见收集状态

| 来源 | 状态 | 证据 |
|---|---|---|
| **Codex**（`gpt-6-luna`，xhigh，会话 `01a1d658-74e5-74a3-8476-69f32ea95440`） | ✅ 已返回（5431 B） | `workspace/flea-loop/q7q8-codex-advice.md`；CLI `0.162.0`，`CODEX_EXIT=0` |
| **ZCode**（`zcode.cjs`） | ❌ **服务不可用** | 三项环境变量齐全仍报 `Select a model before sending a message`（traceId `0c667037…`）+ `ERA_NEGOTIATION_FAILED`；最小探测 `PROBE_EXIT=1`，stdout 0 B、stderr 154,548 B |
| 第二独立意见（代行） | ⏳ 独立上下文子 agent | 派发于 Codex 结论之后，未向其透传任何结论 |

**偏差登记**：ZCode 不可用时不得自行升权（`--mode yolo`）或改桌面端模型配置。为保持"两个独立视角"，第二份意见改由**独立上下文子 agent**（本会话外的干净上下文）代行；该代行不等同于 ZCode，若后续 ZCode 恢复，可补发并覆盖本条。

## 1. Codex 意见摘要

- **Q7 → `OUT`**（自评 `UNCERTAIN`，因它无法读取本地 HEAD，只能读远端 `9b068382`）：实现需 C-07 additive UNFREEZE + 重算 inventory/pin + UI；OUT 不触契约。反悔条件＝冻结需求明确要求查看逐 region 冲突文本。
- **Q8 → `CONDITIONAL_ON(是否已有覆盖 fresh ACK 的 HostRuntime 全链路用例)`**：Codex 指出远端快照中 `Fea11Residual4AIpcTests.cs` 已走 `HostRuntime.StartAsync` + 生产 dispatcher + ACK，**与卡面「仓内无全链路用例」冲突**，要求本地核实。

## 2. DSH 本地核实（事实优先级最高）

| 断言 | 本地结果 | 证据 |
|---|---|---|
| Codex 说 Q8 存在全链路用例 | **部分成立** | `tests/NewManga.Host.Tests/Fea11Residual4AIpcTests.cs`：`HostRuntime.StartAsync`（:725）、`InvokeAsync(runtime,"source_resync",…)`（:139/:435）、断言 `acknowledged`（:173-174） |
| 该用例是否默认执行 | **否，opt-in** | 类注释「Opt-in only (`NEWMANGA_FEA11_IPC=1`)」+ `[Fea11Residual4AIpcFact]`；Host.Tests 默认 skip 74 |
| 该用例是否断言 **fresh** ACK | **否** | 全文无 `fresh` 匹配；仅断言 authorization payload 形状（:143-157） |
| 卡面「仓内无 `runtime.Commands.InvokeAsync` 全链路用例」 | **不准确** | 用例存在且调用生产 dispatcher 路径；只是**默认不执行** |
| Q7：`RegionSummary` 无冲突字段 | ✅ 成立 | `CoreServiceClient.cs:204-210`（RegionId/RegionType/SfxPolicy/Origin/RevisionNo/Geometry） |
| Q7：`list_page_region_texts` 已注册但未经 `IHostController` 暴露 | ✅ 成立 | 注册 `HostCommandRegistry.cs:191/357/465`、分发 `HostCommandDispatcher.cs:868`；`IHostController.cs` 只有 LoadPageRegions/LoadRegionRevisions/SetRegionType/RestoreRegionRevision，**无 region-text 方法** |

## 3. DSH 终裁

### Q7 → `OUT`（不提供「查看对照」）

- **依据**：数据面确实缺冲突字段（需 additive 契约变更）；App 侧接口未暴露投影；Current V2 亦无此能力（非回归）。实现需 UNFREEZE + inventory/pin 重算 + 新 UI，属**扩大产品范围**（红线 8）。
- **记录方式**：`FEA-06-RESIDUAL-2` 卡面 append-only 增加 `NOT_APPLICABLE: 产品范围决定（不提供查看对照，保留冲突横幅 + typed 原因）`，原 limitation 字节不动。
- **用户可见后果**：冲突发生时只能看到横幅与 typed 原因，不能并排比对 region 文本。
- **可推翻**：若用户或后续需求明确要求该能力，重开卡并走 C-07 additive UNFREEZE。

### Q8 → `OUT`（不新建全链路卡），改为**窄范围测试补强**

- **依据**：全链路用例**已存在**（`Fea11Residual4AIpcTests`），只是 opt-in 且未断言 fresh ACK。因此「新建一条全链路 e2e」的前提不成立；真实缺口只有两处：① fresh ACK 无断言；② 默认套件不执行。
- **处置**：`FEA-11-HOST-AUTH-5` 裁 `OUT`（作为"新建全链路卡"的提案）；把"补 fresh ACK 断言"作为**测试补强项**登记（不改变产品行为，不影响 DoD 判据），并在 `FEA-15-ACCEPT-1` 的验收口径中保留"打包 sidecar 腿 `NOT_RUN`"。
- **为何不直接释放实现卡**：Codex 的保守建议是"若 fresh ACK 未在同一链证明则 IMPLEMENT"；但既然链存在，正确动作是"补断言"而非"重造链"——重造会得到更慢的重复 sidecar 测试，并可能把"已测当前 Core"误读成"已测打包 sidecar"。
- **可推翻**：若补断言后发现该链并不覆盖 register→scan→plan→apply 全序列，则升级为 `IMPLEMENT`（复用现有 fixture，不新建）。

## 4. 状态变更（**待第二意见回来后执行**）

计划：据此把 `FEA-06-RESIDUAL-4` 与 `FEA-11-HOST-AUTH-5` 由 `proposed` → `cancelled`（OUT）。
当前**尚未执行**：第二份独立意见仍在途，按矩阵须先收齐两份再落状态；本记录先固定 DSH 的终裁意向与全部证据。
若第二意见与上述结论冲突，取更保守一方，并把另一方理由登记为残留风险（见 §5）。
依据先行：本裁决记录与 Codex 原始建议同时入库，符合红线 4「先证据后状态」。
