# CONTRACT-UNFREEZE-2026-11-07-C16-L-R11：C-16 v1.7（§2.4「无 publication 行」口径澄清）

> 载体用途：按 C-16 冻结记录的 UNFREEZE 流程提出 C-16 v1.7 字节修订；须经独立上下文 fresh subagent 做 **byte-level 复核** + DSH 重新冻结后方可视为最终字节。
> 触发：用户 2026-11-06「自动推进/全部授权/裁决交 Codex 或 DSH」；独立 scope review
> `doc/reviews/L-R11-GATE-UNIFY-scope-r1.md`（fresh subagent session `5aa2c0cf…`，verdict **recommended**；
> 方案 C：Core 单谓词 + 全链检测；**1/18 pin UNFREEZE**）；**DSH 裁决（2026-11-07）**：采纳 recommended，
> 先 `FEA-11-L-R11-GATE-UNIFY-PREREQ-1`（本载体）→ 后 `FEA-11-L-R11-GATE-UNIFY-1`（Core-only 实现，0 pin）。
> 顺序约束：本载体 + C-16 v1.7 + 冻结记录 + 矩阵为 UNFREEZE 提交；实现另卡（依赖本 PREREQ）。

## 1. 背景与目标

- **L-R11 事实**（RENDITION-1 卡 `:159` 登记，scope review 复现）：assembly 侧 `core_assembly.read_gate` 对
  「healthy binding 但**无 publication 行**」返回 **open**（它的 docstring 自称是 Run 目标/commit guard 共享的
  单一定义）；resolve 面 `core_service._assert_source_sync_gate` 在 `previous_binding_id` 有 publication 行时
  **fail-closed**（`SOURCE_ACCESS_DENIED`）。该损坏形态下两读面语义不一致（provider/target 首次可达）。
- **C-17 §3.3（`:171-173`）已冻结正确语义**：「旧未参与同步且无 publication 行的 v7 binding 沿旧规则；**新同步
  binding 缺 publication 行属于损坏，fail-closed（由 plan receipt/new previous 链检测），不能当作 legacy 放行**」。
  该条**零字节**（本卡不是改它，而是让代码/契约文本与之对齐）。
- **冲突点**：C-16 §2.4 `:90`（`per-page 授权匹配（冻结）` 段落）写「…沿用 Run 目标/commit guard 的**同一** gate
  谓词，C-17 §3.3；**无 publication 行按既有 open 处理**…」，与 C-17 §3.3 在「新同步链缺行」子形态下字面矛盾；
  且 `AuthorizeSourceReadForRun` 的 per-page 路径经 `catalog.source_gate_reader` 消费同一 `read_gate`
  （`core_service.py:5030,5057`），故该命令在损坏形态下会从「可授权」变为「拒绝」——必须由契约澄清。
- **目标**：C-16 v1.7 **仅澄清** §2.4 的「无 publication 行」口径（旧 v7 legacy open / 新同步链缺行 fail-closed），
  并同步修正 `:93` 的「两读面既有差异」过期陈述。**不改 wire 字段/命令集/能力/错误闭集/TTL/撤销语义/
  `PROTOCOL_MINOR=3`/schema/依赖；C-17 与其余 17 pins 零字节。1/18 pin。**

## 2. 提议修订

### A. §2.4 per-page 授权匹配（`:90`）

- 原文括注：「沿用 Run 目标/commit guard 的**同一** gate 谓词，C-17 §3.3；无 publication 行按既有 open 处理」
- 改为：「沿用 Run 目标/commit guard 的**同一** gate 谓词，C-17 §3.3；**旧未参与同步且无 publication 行的 v7
  binding 按既有 open 处理；新同步 binding 缺 publication 行属于损坏，fail-closed（C-17 §3.3），不得当作
  legacy 放行**」

### B. §2.4 兼容句（`:93`）

- 原文：「publication gate 的两读面既有差异（L-R11，`core_assembly.read_gate` vs resolve 面
  `_assert_source_sync_gate`）不属于本命令语义，本命令不引入第三套 gate 判定。」
- 改为：「publication gate 两读面判定由 **L-R11** 统一为同一谓词（`core_assembly.read_gate` 与 resolve 面
  `_assert_source_sync_gate` 共用；v1.7 澄清「无 publication 行」口径），本命令沿用该谓词，不引入第三套
  gate 判定。」

### C. §0 版本面行

- `source-access wire` 行补注：「v1.5 增 §2.5 reattest；v1.6 澄清 §2.4 重复调用；v1.7 澄清 §2.4
  「无 publication 行」口径（旧 v7 legacy open / 新同步链缺行 fail-closed），均不改 wire 字段/命令集/能力/错误码」。

### D. 头部与日期行

- 状态行 → `FROZEN v1.7`（历史 v1.0/v1.1/v1.3/v1.4/v1.5/v1.6 保留）；载体链接指向本文件；日期行补 v1.7。

### E. §10 冻结条件与变更记录

- 冻结条件追加 ⑨ v1.7（§2.4 无 publication 行口径经独立 byte-level 复核 approved；wire/能力/错误闭集/TTL/
  撤销/`PROTOCOL_MINOR=3` 零改动；C-17/C-06/C-15/C-07/M2-C1 与其余 17 pins 零字节）。
- 变更记录追加 v1.7 行（修订内容、载体、复核后重冻）。

### F. 冻结记录 / 矩阵

- `FEA-CONTRACT-FROZEN-C16.md`：pin → v1.7 最终字节 sha256 `67286eec…`；`git hash-object` →
  `3cd9d2fb…`；§1B 追加 v1.6/v1.7 行；§2 条件 9（v1.7，复核前 ⏳、approve 后 ✅）；新增 §11 v1.7 重冻记录。
- `FEA-CONTRACT_FREEZE_MATRIX.md`：状态行 C-16 v1.6→v1.7；第 16 行 → `FROZEN v1.7`（含 v1.7 复核 ⏳ 及
  「L-R11 实现归 FEA-11-L-R11-GATE-UNIFY-1」）。
- `verify_pins.ps1` 不改；18/18（C16 新值 `67286eec…`、其余 17 实测不变）。

## 3. 安全与兼容

- **不改判定方向的安全语义**：legacy v7（全链无 publication 行）仍 **open**；只有「新同步链缺行」这一**损坏形态**
  从 open 变 fail-closed——这是收紧，不是放宽；不会把未确认/损坏 binding 放行。
- **影响面（契约目标语义；L-R11 实现卡落地后才生效，本卡不改变任何运行时行为）**：Run 目标层/provider/commit
  guard 在损坏页从「可进入」变既有 family 拒绝（`TARGET_NOT_FOUND` / `INVALID_INPUT`）；resolve 保持
  `SOURCE_ACCESS_DENIED`；`AuthorizeSourceReadForRun` 在损坏页整请求 typed 拒绝、零映射（其既有原子语义不变）。
  正常页/legacy 页零变化。
- **零 wire/能力/错误码/schema**：本卡不改任何命令请求/响应字节、能力集、错误闭集、TTL、撤销语义、
  `PROTOCOL_MINOR=3`；C-17/C-06/C-15/C-07/M2-C1 **零字节**。
- **契约就绪 ≠ 实现/产品可用**：本卡只解除 C-16 文本阻塞；L-R11 的实现（单谓词 + 全链检测）由
  `FEA-11-L-R11-GATE-UNIFY-1` 承担，**不得**把本卡写成「C-17 §3.3 已实现/L-R11 已关闭」。

## 4. 风险与回退

- 风险：①1/18 pin 重签须独立复核；②实现若把「任何 previous 链接」当作「参与过同步」，会误伤从未同步但有
  previous 链接的旧数据——实现卡 AC-2 要求 real v7→v8 legacy 用例判别；③`relation='added'` 的同步 binding
  缺行（previous NULL）链检测不可见，属实现卡 L-R11-a limitation（本契约不承诺覆盖）。
- 回退：恢复 C-16 v1.6 字节（sha `b8f46fb1…`）与冻结记录/矩阵；L-R11 不释放。

## 5. 独立复核要求

- Reviewer：**未参与起草/前轮复核**的 fresh subagent；只读**最终字节**（工作树 SHA-256 `67286eec…`）；记录
  session/reviewed_head。
- 核对：①本载体 §2 逐项落地（C-16 仅 §2.4 两处 + §0 行 + 头部/日期 + §10；无其他条款改动）；②仅
  C-16/冻结记录/矩阵/载体/卡/证据变化（`git diff --name-only`），C-17/C-06/C-15/C-07/M2-C1 及 `src/apps/tests/tools`
  零 diff；③无新错误码/wire minor/能力/schema/依赖；④pin 可复算、`verify_pins.ps1` 18/18、其余 17 不变；
  ⑤安全语义：legacy open 不回归、损坏形态收紧、无放行扩大；⑥载体/卡不夸大（契约就绪 ≠ 实现/产品可用）。
- 通过标准：`approved`（可含非阻断 P3）；随后 DSH 提交 UNFREEZE 并重跑 pins。

## 6. 复核结果（独立 byte-level）

- **r1 `approved`（P0=0 / P1=0 / P2=0 / P3=7，均为非阻断）**：`doc/reviews/FEA-11-L-R11-GATE-UNIFY-PREREQ-1-r1.md`
  （reviewer = fresh subagent，独立上下文，未参与 C-16 v1.7 起草/前轮复核；session
  `9bc4c117-e171-48b6-8f13-582845d2e12f`；reviewed_head `07a7d746a`；reviewed worktree SHA-256 `67286eec…`）。
  核对：字节三口径一致；diff 仅 5 个允许 hunk（7+/6−）；其余 17/18 blob 与 HEAD 相同；pins 18/18；check PASS×2；
  `git diff --check` 0；语义方向成立（legacy open 不回归、新同步链缺行收紧）；记录/矩阵一致；未夸大。
- **P3 处置（不改变 C-16 字节）**：P3-01 提交隔离（本 UNFREEZE 提交只 stage 本包，排除 `doc/STATUS.md`、
  `doc/handoffs/DSH-HANDOFF-2026-11-06.md` 与并发 C-04b scope review）→ **已执行**；P3-02 EV「逐字一致」措辞 →
  **已改为「语义一致」**；P3-05 卡面元数据（§11 引用、AC 范围、base_commit）→ **已修**；P3-06 载体 §3 完成式 →
  **已加「契约目标语义/实现未开始」限定**；P3-07 `unfreeze.diff` CRLF → EV 注明归一化后一致。P3-03（C-16 §0 `:17`
  「均不改…能力」范围可歧义）与 P3-04（§10 ⑨ 完成式）**保持现状**——修改会改变 C-16 字节并触发新 pin/复核，
  登记为后续 UNFREEZE 候选，不阻断本次冻结。
- **记录回填**：FROZEN-C16 §2 条件 9 → ✅、§1B v1.7 行 → r1 approved、§11 → r1 approved（P0/P1/P2/P3）；
  矩阵第 16 行 ② → ✅；C-16 字节不变（`67286eec…`），pins 重跑 18/18。

## 7. 真实性声明

1. 本载体只提出并记录 C-16 v1.7 的**提议字节**；在独立 byte-level 复核 approved + DSH 重冻前，不得作为
   「已复核字节」引用。
2. C-16 变更已实测 diff：仅 §2.4 两处 + §0 版本面行 + 头部状态/日期 + §10 条件/变更记录（`git diff --stat`：
   1 file / 7 insertions / 6 deletions）。C-17/C-06/C-15/C-07/M2-C1 及 `src/apps/tests/tools` 未改动。
3. 工作树 SHA-256 `67286eeca8cb2109f35445c6b925b03053c483293b1bdb19e56efdc9965b657d`；blob
   `3cd9d2fbf79bd37b3fc35e1895efa1c75d2fc232`；`verify_pins.ps1` 实跑 18/18（C16 新值）。
4. 不声称 L-R11 已修复、C-17 §3.3 已实现、或任意读面行为已改变。
