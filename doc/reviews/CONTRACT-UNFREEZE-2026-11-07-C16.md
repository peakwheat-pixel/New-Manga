# CONTRACT-UNFREEZE-2026-11-07-C16：C-16 v1.4（容器源多成员 entry 授权接受面）

> 载体用途：按 [C-16 冻结记录](../plan/FEA-CONTRACT-FROZEN-C16.md) 的 UNFREEZE 流程，提出 C-16 v1.4 字节修订；须经独立上下文 fresh subagent 做 **byte-level 复核** + DSH 重新冻结后方可视为最终字节。
> 触发：用户 2026-11-06「自动推进/全部授权/裁决交 Codex 或 DSH」；`FEA-11-RUN-GRANT-2` 权威 scope review `doc/reviews/FEA-11-RUN-GRANT-2-scope-r1.md`（**READY-WITH-UNFREEZE**：2B 仅需 C-16 v1.4，1 pin）；Codex 裁决输入（`196dede9…`，同意容器多 entry 需 C-16 修订且建议一次 UNFREEZE 收敛）。
> 授权链：用户 2026-11-06 全授权 → DSH 裁决 T-1…T-5（`doc/tasks/FEA-11-RUN-GRANT-2B-PREREQ-1.md`「DSH 裁决」）。
> 顺序约束：本载体 + C-16 + 冻结记录 + 矩阵为 UNFREEZE 提交；2B 实现另卡（`FEA-11-RUN-GRANT-2`，proposed）。

## 1. 背景与目标

`FEA-11-RUN-GRANT-1`（done，`a11ded0d3`）后仍留 L-G12②：Host 对 zip/cbz/pdf 只铸容器单 entry（locator=容器文件名、ordinal=0），Core 按成员 `source_entries` 匹配 → 多成员容器仅 `ordinal=0` 首成员可授权。根因：Core 注册期与匹配期硬性要求容器 grant **恰好 1 个 entry**（`src/infrastructure/resource_channel/source_read_refs.py:986-990`、`:598-610`），冻结 C-16 §2 未正面规定成员 entry 形态。

目标：在 C-16 v1.4 中以**最小明文**允许容器 grant 携带 1..N 个成员 entry，同时保持既有授权不变量（四维 scope、facts/identity、无路径回退、fail-closed、TTL/撤销/错误闭集/Run wire 零改动）。

## 2. 提议修订（C-16 v1.4）

### A. 头部与 §0
- 头部状态行 → `FROZEN v1.4（2026-11-07 重冻；v1.0 2026-11-03、v1.1 2026-11-04、v1.3 2026-11-06）` + 载体/冻结记录链接；日期行补 v1.4。
- §0「source-access wire」行 → `source-access-wire/1.3`（v1.4 仅澄清容器源多成员 entry 的授权接受面，不改 wire 字段/命令集）。

### B. §2 新增明文（容器源多成员 entry）
- 容器源（`rendition.decoder ∈ {zip, cbz, pdf}`）的 `scope.entries[]` 允许 **1..N**（N ≤ `budget.max_entries`）：
  - 每项 `path` 必须为**同一容器**的绝对路径；
  - `locator`/`ordinal` 为容器内成员身份，**以 Core 权威扫描结果为准，Host 不得自行推断**；
  - 每项 `facts` 必须等于**容器**物理身份（`volume_serial`/`file_id`/`size`/`sha256` 四键同一）。
- **注册校验（逐项）**：locator 安全（不得 `.`/`..`/绝对）、`ordinal ≥ 0` 且唯一、`path` 一致、facts 与容器身份一致、条目数 ≤ `budget.max_entries`；任一项不满足 → **整 grant typed 拒绝**（`SOURCE_ACCESS_DENIED`，不截断、不部分接受）。
- **读取/匹配**：沿用既有 `entry_key == entry_id OR locator == source_entries.locator OR ordinal == source_entries.ordinal` + facts 与容器身份比对；**无路径回退**；`find_bound_for_source`/`commit_guard` 语义不变。
- `folder`（逐成员、路径各自独立）与 `image`（单 entry）语义不变。

### C. §10
- 冻结条件追加 ⑥（v1.4 独立 byte-level 复核 approved、wire/命令集/TTL/撤销零改动、其余 pins 零改动）。
- 变更记录追加 v1.4 行。

### D. 冻结记录/矩阵
- `doc/plan/FEA-CONTRACT-FROZEN-C16.md`：pin → v1.4 最终字节 sha256；新增 v1.4 UNFREEZE 重冻记录（历史 pin 保留）。
- `doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md`：C-16 行 → `FROZEN v1.4`（2026-11-07）。
- `verify_pins.ps1` 不改；18/18，其中 C16 新值、其余 17 项不变。

## 3. 兼容与影响

- 新 Host × 旧 Core（无 v1.4 实现）：仍按旧行为（容器单 entry 注册成功；多 entry grant 被拒）→ 多成员容器不可用（维持 L-G12②），不破坏既有安全。
- 旧 Host × 新 Core：旧 Host 仍铸单 entry，行为不变。
- 无 schema/migration/依赖变化；Run wire/`PROTOCOL_MINOR`/错误码闭集/`source.read.run/1` 命令零改动。
- C-06/C-17 在内的其余 17 份冻结契约逐字节不变（18−1：本批仅重签 C-16）。

## 4. 风险与回退

- 风险：①1/18 pin 重签，须独立 byte-level 复核；②若实现方向被理解为「放宽 facts 校验」将破坏授权不变量——本载体明确 facts 必须等于**容器**身份、无路径回退、逐项校验整 grant 拒绝；③`max_entries` 限制单 grant 条目数、64 限制单次命令 `grant_ids` 数（超限 typed，不截断；二者都不是「容器成员数上限」）→ 由 2B 实现卡登记 limitation/设计取舍。
- 回退：若独立复核否决或用户要求回退，恢复 C-16 v1.3 字节（sha `7c355ccb8f826879e34252750c642c8a7b5c138cd5be5b089a7a518bb56519e5`）与冻结记录/矩阵；2B 实现卡不释放。

## 5. 独立复核要求

- Reviewer：未参与本提案起草/前轮复核的 fresh subagent；只读最终工作树字节；记录 session/reviewed_head。
- 核对：①本载体 §2 各项逐项落地；②仅 C-16/冻结记录/矩阵变化（`git diff --name-only`），C-06/C-17 及 src/apps/tools/tests 零 diff；③wire 字段/命令集/TTL/撤销/错误闭集/§7 脱敏/§2.4 命令零改动；④pin 可复算、18/18、其余 17 项不变；⑤载体/卡不夸大（契约就绪 ≠ 实现/产品可用）。
- 通过标准：approved（可含非阻断 P3）；随后 DSH 提交 UNFREEZE 提交并重跑 pins；未通过 → 返修后窄面复审，不得先提交后补审。

## 6. 复核结果（独立 byte-level）

- **r1（`doc/reviews/FEA-11-RUN-GRANT-2B-PREREQ-1-r1.md`）**：`changes_requested`，**P0=0 / P1=2 / P2=4 / P3=9**；安全语义逐条通过（无授权放宽）。两 P1：①契约把「条目数 > `budget.max_entries`」也归入 `SOURCE_ACCESS_DENIED`，与既有 `SOURCE_BUDGET_EXCEEDED` 冲突；②复核期间 2A 并发改动进入工作树导致「src/apps 零 diff」在最终工作树不成立（提交面问题）。
- **处置（2026-11-07）**：①错误码拆分——**条目数超预算 → `SOURCE_BUDGET_EXCEEDED`（不截断）**，其余项不满足 → 整 grant `SOURCE_ACCESS_DENIED`；②§2 示例 decoder 枚举改为 `zip|cbz|pdf|image|folder`；③计数修正（C-16 §10⑥/变更记录、载体 §3 均为「其余 **17** 项不变」）；④冻结记录清理（删除残留旧行、补 v1.4 冻结时间）；⑤C-16 规范化 LF 并重算 pin（`ad25fb3c…`；blob `b9be0acf…`）；⑥提交隔离：UNFREEZE 提交只含本 UNFREEZE 面，2A 改动走其自身提交。
- **r2 窄面复核（`doc/reviews/FEA-11-RUN-GRANT-2B-PREREQ-1-r2.md`，reviewed_head `a0bafc89e`，C-16 字节 `ad25fb3c…`）**：**`approved`，P0=0 / P1=0 / P2=0 / P3=11（非阻断）**；A/B/C/D/E/F 全 PASS；安全语义逐条通过（容器多成员 entry 无授权放宽）；pin 18/18 与其余 17 项不变可复算；`verify_pins`/check/EV 证据一致。
- **r2 P3 处置（登记，不阻断）**：**N-1** 载体 §6 现按 P3 逐项登记（本条）；**N-2** 载体 §2.B 已改为「超预算 → `SOURCE_BUDGET_EXCEEDED`；其余项不满足 → `SOURCE_ACCESS_DENIED`」（与冻结字节一致）；**N-3** 卡面「其余 16」在本次 closeout 统一为「其余 17（含 C-06/C-17）」；**N-4** 实现侧硬上限 10000 与 `max_entries` 的差异接受为更严 fail-closed，记入 2B 实现卡；**N-5** UNFREEZE 提交按显式 pathspec 只 stage 本 UNFREEZE 面（经 DSH 执行，工作树 `verification/FEA-09` 与 2A 证据均不进入）；**P3-2**（wire 1.3 追溯登记）接受为非阻断；**P3-3** 载体 §4 措辞已修（64 是单次命令 `grant_ids` 上限，不是成员数）；**P3-4**（facts 参考点）/ **P3-5**（ordinal 越界显式拒绝）转入 2B 实现卡作为实现/测试要求；**P3-6** `other-17-pins.txt` 已改为完整 64 hex；**P3-9** 「C-06/C-17 与其余 17」冗余语序接受为非阻断（数字正确，不改冻结字节）。
- **结论**：C-16 v1.4 通过独立 byte-level 复核（r1 changes_requested → 处置 → r2 approved，P0=0/P1=0/P2=0），pins 18/18；可提交 UNFREEZE 并重冻。

## 7. 证据

- `verification/FEA-11-RUN-GRANT-2B-PREREQ-1/pre-post.sha256`（C-16 v1.3→v1.4）
- `changed-lines.diff`、`other-17-pins.txt`（C-16 以外 17 项不变）
- `logs/pins.log`、`logs/check.log`、`logs/check-taskpath.log`


