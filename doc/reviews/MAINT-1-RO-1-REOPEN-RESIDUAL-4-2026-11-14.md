# RO-1 重开裁决：撤销 Q7 OUT，`FEA-06-RESIDUAL-4` 转实现路线（2026-11-14）

task: MAINT-1-RELEASE-MONITOR
kind: 产品范围/契约路线裁决（DSH 终裁）
date: 2026-11-14
authority: 用户 2026-11-14 会话直接指令
supersedes: `MAINT-1-P4A-Q7-Q8-ADJUDICATION.md` §3 Q7 的 `OUT` 结论
status: 生效（`FEA-06-RESIDUAL-4` 已由 `cancelled` → `proposed`）

## 1. 依据

用户在 2026-11-14 会话中明确要求：

> 继续 FEA 线收口，且重开卡走 C-07 UNFREEZE 路线。

该指令精确命中 `MAINT-1-P4A-Q7-Q8-ADJUDICATION.md:38` 保留的推翻条件：

> **可推翻**：若用户或后续需求明确要求该能力，重开卡并走 C-07 additive UNFREEZE。

同时满足 `doc/tasks/FEA-06-RESIDUAL-4.md:59` 重开条件①「用户要求冲突对照或列为发布前必做」。

**性质澄清（不得误读）**：本次是**产品范围重新纳入**，不是"修正一个错误"。Q7 的 `OUT` 审计链、Codex 原字节、独立第二意见均保持有效并保留；RO-1 是在其上追加的**后续裁决**，不删除、不改写任何历史字节。

## 2. 事实基线（本地复核，2026-11-14）

| 事实 | 结论 | 证据 |
|---|---|---|
| 基底文本读口在 Core 侧已实现 | ✅ | `src/bootstrap/core_service.py:3533/7787/7796`（`list_page_region_texts`） |
| 命令已注册并分发 | ✅ | `HostCommandRegistry.cs:191/357/462-466`；`HostCommandDispatcher.cs:868-871` |
| App 侧 `IHostController` **未暴露**该投影 | ✅ 缺口 | `IHostController.cs` 仅有 LoadPageRegions / LoadRegionRevisions / SetRegionType / RestoreRegionRevision |
| `RegionSummary` 无冲突字段 | ✅ 缺口 | `CoreServiceClient.cs:204-210` |
| 冻结设计意图要求该动作 | ✅ | `doc/design/fluent-v1/06-page-workbench.md:50`、`09-state-matrix.md:14`；`FEA-06` AC3 = PARTIAL |
| C-07 当前基线 | 79 / 86，pin v1.8 | `doc/plan/FEA-C07_API_INVENTORY.md` 统计节；`FEA-CONTRACT-FROZEN-C07.md` |

结论：缺口只在 **App 端口 + UI**，数据面已存在。这使 UNFREEZE 成为纯 additive（新增端口方法），不需要 Core/schema/wire 变更。

## 3. 路线（固定，不得自行降级）

1. **R1 规格冻结**：补「对照内容规格」——显示哪两层、字段、布局、交互、空态/失败态。
2. **R2 C-07 additive UNFREEZE**：新增 `IHostController` 逐 region 文本投影方法（建议名 `ListPageRegionTextsAsync`），`tools/generate_api_inventory.py` 重跑 → 更新 `FEA-C07_API_INVENTORY.md` 正式成员表 + 统计（79→80 / 86→87）→ 重算 pin → 写 `doc/reviews/CONTRACT-UNFREEZE-<DATE>-C07-RO1.md` 载体 → **独立字节级复核**（未参与实现者）→ 重冻、更新 `FEA-CONTRACT-FROZEN-C07.md` §1/§1B/§2/§5。
3. **R3 实现**：HostController + NullHostController + Fake 实现；UI 对照面板；判别测试（含负向断言，不得削弱既有 `WithoutFabricatedCompare`）。
4. **R4 独立 Review + 集成验证**：门禁四件套 + 独立上下文复审。

## 4. 拆卡计划

| 卡 | 内容 | 依赖 | 写域要点 |
|---|---|---|---|
| `FEA-06-RESIDUAL-4A`（契约前置） | R1 规格 + R2 UNFREEZE 载体 + pin 重算 + 独立字节复核 + 重冻 | — | `doc/plan/FEA-C07_API_INVENTORY.md`、`FEA-CONTRACT-FROZEN-C07.md`、`doc/reviews/CONTRACT-UNFREEZE-*`、卡面、证据 |
| `FEA-06-RESIDUAL-4B`（实现） | R3 + R4 | 4A | `IHostController.cs`/`NullHostController.cs`/Fake、`MainWindow`/RegionBox UI、测试、证据 |

两张卡均须独立 scope review 后才可 `ready`；本项目 Review 独立性以**上下文独立**为准（同会话不得自审）。

## 5. 对照内容规格（草案 v0，供 4A 冻结）

**目标**：冲突发生时，让用户能看清"基底文本 vs 对方草稿"的差异，而不是只看到横幅。

- **层（两层，固定）**：
  - L1 = **基底/已提交文本**（来自 `list_page_region_texts`，即 Core 的 region 文本投影，只读）；
  - L2 = **当前工作副本**（现有 `LoadPageRegions` + 草稿 lease 内的本地文本）。
- **字段**：`RegionId`、`RegionType`、`SfxPolicy`、`Origin`、`RevisionNo`、`Text`（L1 取投影值，L2 取草稿值）、`IsConflict`（派生，不新增存储字段）。
- **布局**：RegionBox 内冲突态展开为纵向双栏（上=基底，下=工作副本），行高自适应；非冲突态不展开，不改变现有渲染。
- **交互**：`查看对照` 按钮（冲突横幅内）；打开后只读，不提供"以某一方覆盖"的一键动作（避免误操作）；关闭恢复原状。
- **空态/失败态**：投影不可用（IPC 失败/lease 失效/source 不可读）→ 面板显示 typed 原因 + 不可重试提示，**不得**显示伪造的对照内容（沿用既有 `WithoutFabricatedCompare` 负向不变量）。
- **可访问性**：双栏有明确标签；键盘可达；对比度符合既有主题。

> 规格 v0 由 DSH 起草；4A 冻结前须经独立 review；若 ZCode 恢复，由其复核 UI/UX 面（本项目 UI/UX 主责）。

## 6. 预算与登记

`doc/REBASELINE_PLAN.md` 当前 64/64 行、6954/7000 B，**无行余量**。4A/4B 的 `ready/in_progress` 登记必须：

- 优先把卡 ID 并入「当前活动程序」段既有表外节点行（不新增行）；
- 若字节不足，压缩 PLAN 冗余注释腾字节，**不得删除既有语义**；
- 两者都不行时，先由 4A 卡以 `proposed` 存在、`MAINT-1` 代为持有实施权（proposed 不触发 DAG 登记）。

## 6A. Errata（2026-11-14，实施后更正统计口径）

原 §3 R2 写「inventory 更新 79→80 / 86→87」，**在 4A 内不可达**，更正为两段式：

- **4A（已交付 `7c1ac472f`）**：inventory 新增「RO-1 计划追加（v1.9 预授权）」节，锁死 `ListPageRegionTextsAsync` / `Task<RegionPageTextProjection?>` / 落地行 `#80`；**正式成员表与统计保持 79/86 = 代码实测**；`generate_api_inventory.py --check` 保持 EXIT 0；pin 因文档字节变化重算为 **v1.9 `91e51ab7…`**。
- **4B**：落地端口实现后，把计划行并入正式成员表、统计翻转为 **80/87**，pin 更新为 **v1.10**。

**不可达的原因**（写入载体 §"为什么本次不翻转统计"）：生成器从源码 interface 解析计数，4A 不写 `apps/**`；`--check` 是子串判定，伪造 80 必 FAIL；同型先例 v1.2 PREQ 就是「计划追加 + 代码零改动 + pin 重算」；`FEA-CONTRACT-FROZEN-C07.md:50` §3 要求新增端口方法在同一 Task 内重跑脚本并更新清单 ⇒ 翻转归 4B。

## 7. 状态变更（已执行）

- `doc/tasks/FEA-06-RESIDUAL-4.md`：`status: cancelled` → `proposed`；`disposition` 追加 RO-1 反转说明；正文追加 append-only「RO-1 重开记录」，原处置记录字节保留。
- 台账：`TASK_LEDGER` 重生成（`cancelled` −1、`proposed` +1、`non-terminal` 6 → 7）。
- 未翻转任何 `closed_with_limitations` 节点；`FEA-06` AC3 仍为 PARTIAL，直到 4B 集成验证通过。

## 8. 不做的事

- 不删除 Q7 的 OUT 审计链与双签证据。
- 不把 `FEA-06` AC3 提前改成 MET。
- 不在本裁决中改任何契约字节（UNFREEZE 属 4A 卡）。
- 不 push 远端。
