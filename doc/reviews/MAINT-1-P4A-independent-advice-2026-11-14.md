# 第二份独立建议（整理版，2026-11-14）

> **性质说明**：本文是独立上下文子 agent 建议的**结构化整理版**（摘录 + 事实核对表），非逐字节原文。
> 摘录保留全部 `文件:行号` 事实与结论，只压缩行文。事实以本文所列路径为准，不以对话记录为准。
> 独立性：该 agent 在 Codex 结论落盘后派发，被明确要求"不打开"裁决文档与 Codex 建议；其自述中途 HEAD 由 `53ce9d55c` 迁移到 `4538c323b`，未读取两份新增文件。

## 0. 与已落盘结论的对账

该 agent 独立核出的两处"stale premise 更正"（Q8 全链路用例存在、Q7 前提成立）与 DSH 在 `4538c323b` 前的本地核实一致。
两份意见在**方向**上无冲突：Q7、Q8 均判 `OUT`。差异在两处**证据精度**与**治理口径**，见 §1.6、§2.5。

## 1. Q7 · `FEA-06-RESIDUAL-4` → `OUT`

### 1.1 缺的不是"冲突字段"，是基底文本读口
- `RegionSummary` 无冲突字段：`CoreServiceClient.cs:204-210`。
- `IHostController` 只有 `LoadPageRegionsAsync`（`IHostController.cs:262-264`），**无** region 文本方法。
- 严格投影已存在但**生产零消费者**：`RegionTextProjection.cs:224-281`（仅 `RegionWriteCommandTests.cs:435/492/514-551` 使用）。
- 对照的另一半数据已在手：冲突时 `DraftLease.Draft.Patch` 即对方草稿文本（`DraftCommands.cs:13-26`；`WorkbenchViewModel.cs:587-589`）。

### 1.2 Core/Host 侧不需要改
- Core 已实现：`src/bootstrap/core_service.py:3533`、`:7787`、`:7796`。
- 注册/分发就绪：`HostCommandRegistry.cs:191/357/462-466`、`HostCommandDispatcher.cs:868-871`。

### 1.3 成本全在 C-07
`IHostController` 加方法 → 重跑 `tools/generate_api_inventory.py` → inventory 变化（`FEA-C07_API_INVENTORY.md:12/20-24`）→ pin 变化（`FEA-CONTRACT-FROZEN-C07.md:15`）→ 按冻结语义必须走 UNFREEZE 载体 + 独立 byte-level 复核 + 重冻（`:25`；`:50` 虽允许同卡更新清单，但 §1 语义与 v1.2→v1.8 全部先例都走 carrier，如 `CONTRACT-UNFREEZE-2026-11-10-EDIT1.md`）。
`verify_pins.ps1:10-25` 是机械门禁，漏重算即 `PIN AUDIT FAIL`。

### 1.4 OUT 的性质必须说准
- 设计行**确实要求**它：`doc/design/fluent-v1/06-page-workbench.md:50`、`09-state-matrix.md:14`。
- `FEA-06` AC3 为 **PARTIAL** 且明写缺「查看对照」：`FEA-06.md:114`、`:176`。
- `ADJ-2026-11-RESIDUAL-WAIVER.md:100` 是 **re-home 不是 waive**。
- 结论：OUT = **正式放弃一条冻结设计意图**，不是"修掉一个 bug"；载体必须写清用户可见后果与重开条件，**不得**写成"已实现/无缺口"。

### 1.5 反向不变量（R1 的真实代价）
- 设计文档**没有对照内容规格**（`06:50` 只有"原因 + 「查看对照」"）→ R1 需先补 UX 规格，属扩大范围。
- `FluentResidualBatchATests.cs:643/664-669` 显式断言冲突条在**且不存在「查看对照」按钮**（`WithoutFabricatedCompare`）→ R1 必须改写该负向断言，存在削弱"不伪造对照"防护的风险。

### 1.6 两处事实校正（对 DSH 原判据的修正）
- 卡面行号已漂移：`RegionSummary` 现为 `204-210`（非 172-178）；冲突用例现为 `642-670`（非 613-641）。
- 原 triage 引用的「术语冲突 NOT_WIRED（`StudioTermsViewModel.cs:36-62`）」是**范畴错误**——术语冲突 ≠ 区域冲突，不能作为 region 对照的证据。

### 1.7 成本/风险/自评
- OUT：0 代码 + 1 份裁决/载体（append-only 更新 `FEA-06-RESIDUAL-2`/`-4`），0 契约/pin。
- R1：1 张实现卡（4 个 `IHostController` 实现 + 4 个 fake + carrier + inventory + pin + UI + 测试改写）+ 1 条 UNFREEZE 授权；0 Core 改动，只触 C-07。
- OUT 选错 → 用户永久失去设计中的对照能力；R1 选错 → C-07 第 9 次 UNFREEZE、UX 自由发挥、负向断言被削弱；用户价值低（单用户桌面，冲突多为 lease 失效/自冲突）。
- 自评：技术高置信；**治理 `UNCERTAIN`**——DSH 2026-11-08 全权授权是否覆盖"产品缩减"。更保守路线＝加一次用户确认，成本极低。

## 2. Q8 · `FEA-11-HOST-AUTH-5` → `OUT`（卡面前提已过期，勿释放实现）

### 2.1 默认套件没有等价覆盖
`Fea11Residual4AIpcTests` 为 opt-in（skip attr `Fea11Residual4AIpcTests.cs:668-679`，`:672` 读 `NEWMANGA_FEA11_IPC`）；`scripts/test.ps1` **不设置**该变量（grep 0 命中）；同类真实 Core 用例全部同 gated（`Fea11SourceIpcTests.cs:587-593`、`Fea11HostAuthIpcTests.cs:351-357`、`Fea11ScanIpcTests.cs:1174-1180`、`SourceRecoveryIpcTests.cs:611-617`）。

### 2.2 缺口定性：链已存在但未默认执行 + fresh ACK 不在同一条链
- 链在：`Fea11Residual4AIpcTests.cs:33-36`；helper `:494-503` 即 `runtime.Commands!.InvokeAsync`。路径：`:65` register + `:72-74` Host-issued grant → `:87` scan → `:108` plan → `:109-115` preview → `:116-122` confirm → `:139` apply(`source_resync`) → `:160-162` core-committed → `:165-168` ACK 前 gate 拒 → `:171-175` `acknowledged` → `:179-195` 新 v2 键/新字节 → `:198-224` 旧摘要不可变 → `:227` 源字节守恒 → `:232-242` 撤销 fail-closed。
- **已执行过**：`FEA-11-RESIDUAL-4A.md:66`（AC-R3-2 MET）、`:97-101`、`:130`（4 passed/0 failed）；`logs/fea11-ipc-r4a.log` 末行"失败 0，通过 4，跳过 0"；`evidence/after-full-chain.txt` 含 `scan_via=dispatcher`/`apply_via=dispatcher`/`ack=acknowledged`/`old_digest_immutable=1`/`source_conserved=1`/`PASS`。
- fresh ACK 在别处断言：`Fea11HostAuthIpcTests.cs:51-61`（fresh 授权、`authorized_at` 前进）、`:74-82`（ACK wire 为 fresh）、`:106-111`（二次 ACK 零帧）；但走 client+coordinator 直连（`:448-452`），**非 dispatcher**。默认套件另有纯单元覆盖 `Fea11HostAuthTests.cs:647-652`。
- 两个 delta：① r4a 用 `Registry.Register`（`:65`）/`Sources.IssueAsync`（`:72`），非经 dispatcher 的 `source_register_root`（`HostRuntime.cs:1243-1248`）；② 打包 sidecar 腿 `NOT_RUN`。

### 2.3 卡面两处前提在 HEAD 已为假
- `FEA-11-HOST-AUTH-5.md:36`「仓内无 `runtime.Commands.InvokeAsync` 全链路用例」→ **假**。
- `:7/:13`「需 `HostOptions` 最小 Core 覆盖 seam（4-6 行）」→ **假**（`SidecarDirectoryOverride` 自 S1/`eb123ad4f` 已存在：`HostOptions.cs:52`、`HostRuntime.cs:1169`，测试 `:729` 直接使用）。
- 仍为真的只有「打包 sidecar 早于 C-17」（`Fea11Scan2HostRuntimeTests.cs:16-17`、`:57-59`）；这才是"默认套件跑不了该链"的根因，不是缺 seam。

### 2.4 若要"默认执行"
不是实现新链，而是把现有 gated 用例提升为默认：1 张纯测试卡，0 产品代码、0 契约/pin；但须处理 `Fea11Residual4AIpcTests.cs:708-709` 的 `NEWMANGA_BUILD_PYTHON ?? "C:/Python314/python.exe"` 硬编码（`test.ps1` 不导出）与 .NET 基线计数重钉，否则默认门禁新增机器相关故障类。

### 2.5 风险与验收口径
- OUT 错 → 默认门禁对 source-sync 授权链回归不报红（仍由 opt-in 套件守着）；IMPLEMENT 错 → 重复造链/无谓 seam/默认门禁 flake/基线重钉，且误导"打包 sidecar 已覆盖"。
- 验收关键：OUT 记录必须写「默认套件无全链路 e2e / opt-in 已执行 / 打包 sidecar `NOT_RUN` / fresh-ACK 在直连 gated 用例断言」，**不得**把 AC-F4 写成完全 MET。
- 诚实边界：该 agent **未重跑** gated 测试（只读），"已执行"依据是仓内提交的日志与证据；建议双签记录直接引用这些日志路径，不引用其转述。
