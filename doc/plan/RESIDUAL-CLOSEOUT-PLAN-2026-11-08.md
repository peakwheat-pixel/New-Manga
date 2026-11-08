# 残余收口方案（RESIDUAL-CLOSEOUT-PLAN v1 · 2026-11-08）

> 目标：把 4 个 `closed_with_limitations` 节点**逐项收口到终态**。
> 事实基线：HEAD `cf8496b38`（=origin，AHEAD=0，clean）；pytest **3390/10**、.NET **1691/0/96**、pins **18/18**、check PASS(3w)。
> 本文件是**执行方案**，不是事实来源；节点状态以 [REBASELINE_PLAN](../REBASELINE_PLAN.md)、运行状态以 [STATUS](../STATUS.md) 为准。

## 0. 「彻底解决」的定义（避免自欺）

4 个节点各自的残余分为 4 类，**只有前两类能靠工程手段关闭**：

| 类 | 含义 | 关闭方式 |
|---|---|---|
| **C1 工程可闭环** | 代码/测试缺口，可用 headless 或 gated 真实 IPC 在 CI 内完成 | 补实现 + 判别测试 → AC 重判 MET → 独立 Review |
| **C2 契约对齐** | 已冻结契约要求但实现未遵守（或需 additive） | 遵守型：改实现（0 pin）；additive 型：UNFREEZE 卡 |
| **C3 设计选择/范围外** | 有意不实现（如「启动不做全量扫描」） | **裁决转 OUT**（`<<NOT_APPLICABLE: 原因>>`），不写实现 |
| **C4 硬件/真机** | 双屏、拔屏、DPI、原生 IME、a11y、真机截图 | 只能 **waiver**（保留 `NOT_RUN` + 书面裁决），**不得伪造 PASS** |

**完成定义**：每个节点满足其一即视为「彻底解决」：
- **(a) `done`**：全部 AC `<<MET>>`；
- **(b) `done` + 显式 waiver**：C4/C3 项有独立裁决记录并标 `<<NOT_APPLICABLE: 原因>>`，其余 AC 全 MET；
- 不接受：直接改 `status:`、删除 limitation、`NOT_RUN` 写成 PASS。

## 1. 卡片清单（6 张 + 依赖）

| # | 卡 | 节点归属 | 类型 | 依赖 | 预计轮次 |
|---|---|---|---|---|---|
| **R0** | `RESIDUAL-WAIVER-1` | 全部 4 节点 | governance（0 实现） | 无（可先做） | 1 |
| **R1** | `FEA-11-HOST-AUTH-2` | FEA-11-HOST-AUTH-1 | Host 实现 + gated IPC | 无 | 1–2 |
| **R2** | `FEA-06-RESIDUAL-3` | FEA-06-RESIDUAL-2 | UI 实现 + headless 快照 | 无（端口已 done） | 1–2 |
| **R3** | `FEA-11-RESIDUAL-4A` | FEA-11 | Core/Host/UI 实现 | R1（共用 ACK 语义） | 2 |
| **R4** | `FEA-07-RESIDUAL-2` | FEA-07 | App/Host 实现 + gated | R0 | 2 |
| **R5** | 各节点「翻终态」记录卡（合并进 R1–R4 的 closeout，不单独立卡） | — | docs（append-only） | 对应 R 卡 | 同轮 |

**每轮 ≤2 张实现卡**（R0/R5 属治理/文档，不占名额）。

## 2. R0：`RESIDUAL-WAIVER-1`（裁决集，必须最先或有并行）

一次性把 **C3/C4 类 10 项**裁决清楚，产出 `doc/reviews/ADJ-2026-11-RESIDUAL-WAIVER.md`：

| 项 | 节点 | 类别 | 建议裁决 |
|---|---|---|---|
| 原生 IME、A03 真库 DB/current/pinned/Lock 往返 | FEA-07 AC1 | C4 | `NOT_APPLICABLE`（无硬件，保留 `NOT_RUN` 证据） |
| 真实双屏 broker owner / 单写 owner | FEA-07 AC2 | C4 | 同上 |
| 双屏/拔屏/DPI 100/125/150/200% 原生矩阵 | FEA-07 AC5 | C4 | 同上（原 D-1 blocked） |
| 完整 Tab 遍历、原生 a11y、200% DPI、原生桌面/截图 | FEA-06-RESIDUAL-2 | C4 | 同上 |
| 启动不做全量内容扫描（L-STARTUP） | FEA-11 AC11-1 | C3 | OUT：依据 AD-003 §3.6 + C-01b SC-25 FROZEN v5 |
| PDF 插页不产 pixel profile（L-M1） | FEA-11 AC11-3 | C2/C3 | OUT（无消费者）；若产品要，则另立 C-15 UNFREEZE 卡 |
| folder source 的 relink 一律 typed 拒绝（AC11-6） | FEA-11 AC11-6 | C2 | OUT（C-15 冻结规则，需 UNFREEZE 才能改） |
| IPC flake / 大库冷启动成本未标定 | FEA-11 L 项 | C1 | 不做（登记基础设施项，非节点 AC） |

> **授权**：产品范围取舍按 AGENTS 属用户；本仓当前有 2026-11-08「全部授权、自主裁决、不询问用户」。**建议执行口径**：由 DSH 自裁并写「裁决人=DSH + 依据」，用户可事后推翻（记录可改，状态可回退）。

## 3. R1：`FEA-11-HOST-AUTH-2`（首推：最可能真正翻 done）

- **kind**：implementation；**节点**：把 `FEA-11-HOST-AUTH-1` 从 `closed_with_limitations` 翻 `done`
- **base**：当轮 HEAD；**0 pin**（C-17 已冻结要求，不新增契约字节）
- **范围（草案 allowed_paths）**：
  - `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceOperationCoordinator.cs`（ACK/recovery 授权来源）
  - `apps/desktop-avalonia/src/NewManga.Host/Sources/HostRuntime.cs`（如需接线）
  - `apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11SourceIpcTests.cs`（gated 真实 IPC 用例）
  - `apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceOperationTests.cs`
  - 卡/评审/证据路径
- **AC（草案）**：
  - AC-R1-1：`AcknowledgeSourceOperation` 与 recovery 路径使用 **fresh grant/授权重验**（C-17 `:161` 要求），不再读 journal 原 authorization；判别测试：让 grant 在 journal 后失效 → 必须 typed 拒绝且零 binding 变化。
  - AC-R1-2：ACK 重发/恢复 e2e（gated `NEWMANGA_FEA11_IPC=1`）：同 operation 重试返回原 commit receipt、零新 binding；不同 digest → typed 拒绝。
  - AC-R1-3：崩溃点注入（Host 进程 kill 于 core-committed 与 acknowledged 之间）→ 重启后恢复路径幂等、无重复 binding、无越权。
  - AC-R1-4：AC11-8 的 durable receipt/ACK 顺序断言并入（避免 FEA-11 二次开卡）。
  - AC-R1-5：门禁不降（pytest ≥3390/10、.NET ≥1691/0/96、pins 18/18、check PASS、gated 用例 default skip 不改变默认基线）。
  - AC-R1-6：`FEA-11-HOST-AUTH-1` 的 AC3 从 PARTIAL 重判为 MET，append-only 关闭记录 + PLAN 行改 `done`。
- **风险**：ACK 语义改动触及跨进程恢复 → 必须保持 fail-closed；gated 用例默认 skip 不得掩盖默认门禁。
- **成本**：1–2 轮；**收益最高**（唯一不依赖 waiver 就能翻 done 的节点）。

## 4. R2：`FEA-06-RESIDUAL-3`（依赖已就绪的 5 格）

- **kind**：implementation（UI-only）；**节点**：`FEA-06-RESIDUAL-2` → `done`（a11y/DPI 走 R0 waiver）
- **关键前提**：其 BLOCKED 表的 5 格恢复条件（FEA-09/10/12 端口 done）**现已满足**（FEA-09 done、FEA-10 done、FEA-12 四卡 done）。
- **范围（草案）**：`apps/desktop-avalonia/src/NewManga.App/Views/**`（对应组件视图/VM）、`apps/desktop-avalonia/tests/NewManga.App.Tests/**`（视觉/状态矩阵用例）、`verification/FEA-06-RESIDUAL-3/**`。
- **AC（草案）**：
  - 5 格逐一：BatchMatrix 七状态/吸顶表头、RunProjectionBar 投影态、ReaderPage 双页第二图/滚动、RegionBox 冲突态、书架满态统计、Console 投影/9 行 → 每格 1 个判别用例 + 1 张 headless 快照（显式开关写 `verification/**`，默认零仓库写入）。
  - 原生 a11y/200% DPI/原生截图 → R0 waiver 记录，标 `NOT_APPLICABLE: 无硬件`（不得写 PASS）。
  - 证据：逐图元数据（head、场景、主题、视口、帧位置、生成命令与 EXIT）。
  - `FEA-06-RESIDUAL-2` append-only 关闭记录 + PLAN 改 `done`。
- **风险**：视觉断言易依赖像素/字体 → 需用状态断言优先、快照仅作证据；不得弱化既有 Fluent 快照基线。

## 5. R3：`FEA-11-RESIDUAL-4A`（FEA-11 主体收口）

- **kind**：implementation（Core/Host/UI）；**节点**：`FEA-11` → `done`（配 R0）
- **范围（草案）**：`src/bootstrap/core_service.py`（诊断查询投影）、`apps/desktop-avalonia/src/NewManga.Host/**`、`apps/desktop-avalonia/src/NewManga.App/**`（诊断入口）、`tests/**`、`apps/desktop-avalonia/tests/**`。
- **AC（草案）**：
  - AC-R3-1（原 AC11-7）：`missing/needs_confirmation/tombstone` 管理诊断查询接线（Core 读面 + Host 投影 + UI 只读诊断入口），遵守 C-05 P8 可见性，不扩 `V(p,t)`。
  - AC-R3-2（原 AC11-9）：真实生产链路 gated IPC：resolve 旧绑定读旧字节 → 同步新绑定 → resolve 新内容且旧资源键/摘要不可变。
  - AC-R3-3（L-M4）：旧证据按冻结参数重算实现 + 判别测试（算法/decoder/version/params 可比性）。
  - AC-R3-4：AC11-5/AC11-8 由既有承接卡（LINEAGE-1/AC4-GAPS-1/HOST-AUTH-2）结果回填重判。
  - AC-R3-5：`FEA-11` append-only 关闭记录 + PLAN 改 `done`；L-STARTUP/L-M1/AC11-6 引 R0 waiver/OUT。
- **风险**：跨三层，写域大 → 拆 2 轮；诊断入口新增 UI 面须遵守「UI 不直连 DB/OS」。
- **说明**：若 AC11-7 的诊断入口产品上不想要 → 也可走 R0 裁决为 OUT（本方案默认「做」，因为它是真实功能缺口而非设计选择）。

## 6. R4：`FEA-07-RESIDUAL-2`（成本最高，最后做）

- **kind**：implementation（App/Host）；**节点**：`FEA-07` → `done`（AC1/AC2/AC5 走 R0 waiver）
- **AC（草案）**：
  - AC-R4-1（原 AC3）：跨进程崩溃注入（子进程 kill at 注入点）→ 恢复幂等、保护状态一致、零隐式 Start/Dispose。
  - AC-R4-2（原 AC4）：真实 App 初始化入口 + 坏包/scale 完整矩阵（组合根真实装配）。
  - AC-R4-3（原 AC6）：真实规模合成负载 p95 与 UI freeze 实测（固定基准环境；若 flaky 则只做上限回归并以 3 次中位数记录）。
  - AC-R4-4：AC1/AC2/AC5 标 `NOT_APPLICABLE: 无硬件（R0 waiver）`，保留 `NOT_RUN` 证据，不写 PASS。
  - AC-R4-5：`FEA-07` append-only 关闭记录 + PLAN 改 `done`。
- **风险**：性能断言 flaky、崩溃注入可能受环境限制 → 需隔离证据与可重跑命令。

## 7. 执行顺序与轮次

```
轮次 A：R0（waiver 裁决）＋ R1（HOST-AUTH-2 scope review → 冻结 → 实现）
轮次 B：R1 收口（Review → 门禁 → closeout → 翻 HOST-AUTH-1=done → push）＋ R2 scope review
轮次 C：R2 收口（→ 翻 RESIDUAL-2=done）＋ R3 scope review
轮次 D：R3 实现（可拆 D/E 两轮）→ 收口（→ 翻 FEA-11=done）
轮次 E：R4 实现 + 收口（→ 翻 FEA-07=done）
轮次 F：终局核对（PLAN 4 行 done、STATUS、ledger、handoff §、全量门禁）
```
预计 **6–8 轮**；每轮最多 2 张实现卡。

## 8. 每卡门禁（不得降低）

`check.ps1`（默认 + `-TaskPath`）、`verify_pins 18/18`、全量 `pytest ≥3390/10`、全量 `.NET ≥1691/0/96`（新增用例只增不减）、`generate_api_inventory.py --check`、scope ⊆ allowed_paths、契约/schema/依赖零漂移、跑后 `git checkout -- verification/FEA-09`、独立 Review（含变异判别：改坏→RED→逐字节复原 sha256 MATCH→复绿）。

## 9. 红线（写死）

1. **不伪造硬件 PASS**：C4 项只能 `NOT_RUN` + waiver `NOT_APPLICABLE`。
2. **不删 limitation**：原卡历史字节不改，只 append-only 关闭记录。
3. **不改冻结契约字节**（除非显式 UNFREEZE 卡 + 独立 byte-level 复核 + 重冻 + pin 重算）。
4. **不得自审**：每张卡由未参与实现的独立上下文 Review。
5. **文案**：只能写「关闭 X 项 / 转 OUT Y 项」，**不得**写「FEA-07/FEA-11 完全实现」「L-G1 关闭」「C-17 §3.3 完全实现」。

## 10. 终局判定矩阵

| 节点 | 需完成卡 | 需 waiver 项 | 目标终态 | 判据 |
|---|---|---|---|---|
| FEA-11-HOST-AUTH-1 | R1 | 无 | **done** | AC3 MET + 10 limitation 逐项注销（e2e/崩溃点/ACK 重发） |
| FEA-06-RESIDUAL-2 | R2 | a11y/DPI/截图 | **done** | 5 格 MET + 1 格 NOT_APPLICABLE |
| FEA-11 | R3（+R1 回填） | L-STARTUP/L-M1/AC11-6 | **done** | AC11-1…10 全 MET 或 NOT_APPLICABLE |
| FEA-07 | R4 | AC1/AC2/AC5 | **done** | AC3/4/6 MET + 3 项 NOT_APPLICABLE |

> 若某项裁决被用户否决（要求真机实测），则该节点保持 `closed_with_limitations`，并在 PLAN 行注明「待硬件」。这是唯一被允许的不完成情形，且必须写明原因。

---

## 11. v2 修订（2026-11-08，R0 scope review NOT_RECOMMENDED → DSH 采纳）

> 本节**覆盖**上文 §2/§3–§6 的分类与卡片范围；裁决明细见 `doc/reviews/ADJ-2026-11-RESIDUAL-WAIVER.md`、评审原文见 `doc/reviews/RESIDUAL-WAIVER-1-scope-r1.md`。

### 11.1 裁决口径修正（关键）

- **不得再以「无硬件」为唯一理由**：本机实测 2 个活动显示器、仓库记录 3 个虚拟适配器 → 原生项正确状态是「**原生交互矩阵未执行**」，不是「没有硬件」；`GOAL-PROGRESS:311` 的「本机可能无双屏」是推测。
- **C1 不得写成 C4/C3**（会把未做的工作合法化）：FEA-07 AC1 的 A03/ACK/Run、AC2 的 `(SessionId,RegionId)` 单写 owner/Host 生命周期、FEA-06-RESIDUAL-2 的 Tab 遍历/a11y 属性、FEA-11 的 folder relink 判别测试 → **全部进实现卡**。
- **契约误读纠正**：PDF 插页（L-M1）在 C-15 §3.2 `:230` 覆盖范围内且有 matcher 消费者 → 不是「能力外/无消费者」，只能 BLOCKED 或产品显式决定；folder relink 在 C-17 `:278` 允许「能证明同一」→ 不是「C-15 冻结规则」。
- **翻 done 的治理前置**：需改写 17 条历史 AC 行，冲突 `09_COLLABORATION:79` 与 HOST-AUTH-1 Codex 终裁 → 以**用户 2026-11-08 指令为新授权**，按节点逐个翻转、逐条登记 before/after、不改任何 Review/证据字节（见 ADJ §3）。

### 11.2 卡片范围修订（v2）

| 卡 | v2 范围（增量以加粗标出） |
|---|---|
| R0 | 已执行：ADJ v2 + 评审落盘（不以 task 卡形式，见 ADJ §6 DSH 说明） |
| **R1** `FEA-11-HOST-AUTH-2` | 已冻结（AC-F1…F5）：ACK/recovery fresh 授权 + 拒绝矩阵 + gated e2e + 崩溃点 + 条件性 HostRuntime e2e；**窄口径 done**（limitation {1,2,5,P2-7} 关闭，{3,4,6,7,8,9} re-home） |
| **R2** `FEA-06-RESIDUAL-3` | 5 个依赖格 **+ 完整 Tab 遍历 + a11y 属性/UIA 树断言**；仅原生 a11y 行为/200% DPI/原生截图走 NA |
| **R3** `FEA-11-RESIDUAL-4A` | AC11-7 诊断接线、AC11-9 生产链路、L-M4 重算、AC11-5/8 回填 **+ folder relink 判别测试 + 成员重排/多项目 + L-S4-2 缺陷登记**；L-M1 默认 BLOCKED（不 NA） |
| **R4** `FEA-07-RESIDUAL-2` | AC3 崩溃注入（含**暂停期间保护状态**）、AC4 启动矩阵、AC6 真实负载 **+ AC1 的 A03/ACK 重连/Run gated 用例 + AC2 的 `(SessionId,RegionId)` 单写 owner/Host 生命周期实现**；仅原生 IME/AC5 矩阵/真实双屏落位走 NA |

### 11.3 done 口径（统一，防假 done）

- 节点 `done` 前置：该节点**全部 C1 项完成并 MET** + 可 NA 项有 `<<NOT_APPLICABLE: 原生交互未执行（保留 NOT_RUN）+ 用户 2026-11-08 授权豁免>>` + **其余 limitation 逐项 re-home 到具名后续卡**。
- `FEA-06-RESIDUAL-2` 的 6 行 BLOCKED 表**不被 AC 门禁看见**：done 记录必须显式声明「done 不覆盖 BLOCKED 表」，且 5 个依赖格必须先做完。
- 禁止：先改状态后补证据；把 `NOT_RUN` 写成 PASS；把「done」读成「可发布」。

### 11.4 基线重钉

pytest **3390/10**、.NET **1691/0/96**、pins **18/18**、check PASS(3w)（本轮实测；`doc/STATUS.md:20` 的 1683 已在本轮校正）。
