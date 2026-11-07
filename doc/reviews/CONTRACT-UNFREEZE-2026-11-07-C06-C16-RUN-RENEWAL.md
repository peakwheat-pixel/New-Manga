# CONTRACT-UNFREEZE-2026-11-07-C06-C16-RUN-RENEWAL：C-06 v1.3 + C-16 v1.6（Run 非终态期间 mid-run 重复建立语义；2 pins）

> 载体用途：按 C-06/C-16 冻结记录流程提出 UNFREEZE；须独立上下文 fresh subagent **byte-level 复核** + DSH 重新冻结后方为最终字节。
> 触发：用户 2026-11-06「自动推进/全部授权/裁决交 Codex 或 DSH」；`2C-LONG-RUN-RENEWAL-scope-r1`（`857903ae-…`，READY-WITH-UNFREEZE 2 pins）；ZCode 故障转移裁决（`cbdf231a-…`，APPROVE 2 pins 路径，0-pin 不成立）；DSH D-1…D-10。
> 顺序约束：本载体 + 两契约 + 两份冻结记录 + 矩阵为 UNFREEZE 提交；实现卡 `FEA-11-RUN-GRANT-2C` 另卡、依赖本 PREREQ。

## 1. 背景与目标

L-G1：Run 由 Core 后台单线程串行整跑（`core_service.py:1277-1319`；`tasks/service.py:1020-1169`、`:1632-1655`），而 source-read grant 在 4 个 Run 命令 **dispatch 前**一次性铸造（`HostCommandDispatcher.cs:78-84`/`:153-157`；`SourceReadCoordinator.cs:586` `expires_at=_clock()+300`）→ 排队 Run 尚未开始即失权；中途 >300s 亦失权（读图 `PROVIDER_FAILED`、提交 `DB_FAILED`；容器重验在过期判定之后救不了）。无任何续期机制。

目标：契约层允许 Host 在 Run **非终态期间**对同一冻结 `{command, scope}` **重复建立**（每次新铸新 grant、各自 ≤300s、顺序重验 facts）；不延长任何 TTL、不改 scope、不绕过撤销。实现侧 Host-only 周期重铸 + 重发 `AuthorizeSourceReadForRun`（零 Core、零 Run wire、零新命令/能力/错误码）。

## 2. 提议修订

### A. C-06 v1.2→v1.3（只追加）
- 头部状态 → `FROZEN v1.3`；日期行补 v1.3；载体链接。
- §2.2「授权建立（第三生产者）」行追加：Run 非终态期间可对同一冻结 `{command, scope}` 重复建立；每次**新铸新 grant**（各自 ≤300s、按当时 facts 顺序重验）；**不得**延长既有 grant `expires_at`、不得扩大 scope、不得撤销后重建、不得改选 command/scope；任一页不可授权 → 整请求 typed 拒绝、零映射写入。
- §5 条件追加 ⑥；变更记录追加 v1.3。grant 形状/TTL/撤销/失联/错误闭集零改动。

### B. C-16 v1.5→v1.6（只追加）
- 头部状态 → `FROZEN v1.6`；日期行补 v1.6；载体链接。
- §2.4「用途（冻结）」追加：可在 Run 非终态期间对同一 `{command, scope}` 重复调用——每次只绑定当次 live grants；不延长任何 TTL、不改 scope、不绕过撤销；任一页不可授权仍整请求 typed 拒绝、零映射写入。
- §10 条件追加 ⑧ v1.6；变更记录追加 v1.6。wire 字段/命令集/能力/错误闭集/TTL/撤销/`PROTOCOL_MINOR=3` 零改动。

### C. 冻结记录/矩阵
- FROZEN-C06 → v1.3，pin `75f8e2b4eb808a7b33f503ae64e6455a390587a552a2689df9ce2ae133341c84`；FROZEN-C16 → v1.6，pin `b8f46fb1feec7c85bc997516f1e7fa9d51ab46717cb4dcf982d8c6e7db1d18a0`；历史 pin 保留。
- 矩阵 C-06 → FROZEN v1.3、C-16 → FROZEN v1.6（2026-11-07）。
- `verify_pins` 18/18（C06/C16 新值、其余 16 不变）。

## 3. 安全与兼容

- **安全**：每次续期都是**新 grant** + 新一次 `AuthorizeSourceReadForRun`，mint 内部重走 `Registry.Authorize`+facts（撤销/漂移/根替换自动 typed 停止）；不延长单 grant TTL、不扩 scope、不绕过撤销、不自动重新授权、不新增授权入口；任一页不可授权整请求拒绝。
- **兼容**：旧 Host 不续期 → 行为不变（长 Run 仍失权）；旧 Core 不认识 mid-run 重发 → 按既有单次建立处理（重复调用仅追加绑定，无新 wire）；无新字段/命令/能力/错误码/schema/依赖。
- **窗口锚点解释（不改字节）**：首次建立仍须在 Run **dispatch 前**；v1.3/v1.6 只允许对**同一冻结 `{command, scope}`** 在 Run 非终态期间重复建立，且只对其后读取/提交生效；不改变既有「dispatch 前/≤300s/不得长期通行证」三锚。
- **C-06 v1.2/C-16 v1.5 解释**：幂等条款对象是「同请求」；「同一 binding 多份 grant」是读端选择规则，不是建立时机授权 → 必须显式追加本语义（2 pins）。

**契约就绪 ≠ 实现/产品可用**：本载体只解除 2C 的契约阻塞；Host 续期实现与 L-G1 降级均未交付。**L-G1 只降级不关闭**（子限制：单步 >300s／续期失败／L-G2 加密／L-G9 重启／L-R1 viewer 残余／L-G16 >4096）。

## 4. 风险与回退

- 风险：①续期被漂移成「放宽授权」（软化 dispatch 前/≤300s/不得长期通行证三锚）→ 载体逐字落「不延长/不扩/不绕过撤销」+ 实现 AC 判别；②mint 成本放大（大 folder 逐成员 sha256）→ 实现 D-4b 单轮上限 + typed skip + 计数；③全有或全无归因 → 证据明写。
- 回退：恢复 C-06 v1.2 / C-16 v1.5 字节与冻结记录/矩阵；实现卡不释放。

## 5. 独立复核要求

- Reviewer：未参与起草/前轮复核的 fresh subagent；只读最终字节；记录 session/reviewed_head。
- 核对：①A/B 逐项落地；②仅 C-06/C-16/冻结记录/矩阵变化（`git diff --name-only`），其余 16 契约零字节；③无新字段/命令/能力/错误码/TTL 变更/schema/依赖；④pin 可复算、18/18、其余 16 不变；⑤安全语义无放宽；⑥载体/卡不夸大（契约就绪 ≠ 实现；L-G1 只降级不关闭）。
- 通过标准 approved（可含非阻断 P3）；随后 DSH 提交 UNFREEZE 并重跑 pins。

## 6. 复核结果（独立 byte-level）

- **r1**（`doc/reviews/FEA-11-RUN-GRANT-2C-PREREQ-1-r1.md`）：`changes_requested`（P0=0/P1=0/P2=4/P3=8）——FROZEN-C16 §2 行 7/8 记录损坏、`other-16-pins.txt` 缺失、卡 I-2/AC-T1 未登记 §5 ⑥、矩阵条件/依赖列过时；P3 若干。
- **处置 1**：行 7 恢复（含 P0/P1/P2/P3=0 与证据列）、行 8 改回 4 列；补 `other-16-pins.txt`（16 项 changed=0）；卡 I-2/AC-T1 补 §5 ⑥+§6 记录；矩阵 C-06/C-16 行更新；载体补窗口锚/不夸大句；C-06 §5 ⑥ 合并入列表项 5（**C-06 字节变化 → pin `0fb2bdaf…`**；C-16 不变）。
- **r2**（`doc/reviews/FEA-11-RUN-GRANT-2C-PREREQ-1-r2.md`）：`changes_requested`（P0=0/P1=0/**P2=1**/P3=5）——本段仍写「r1：pending」，未落 r1/r2 与 r3 状态；其余实质闭合。
- **r3**（`doc/reviews/FEA-11-RUN-GRANT-2C-PREREQ-1-r3.md`）：`changes_requested`（P0=0/P1=0/P2=1/P3=3）——R3-001 载体未记 C-06 pin 迁移；R3-002 条件列预填 approved；R3-003 FROZEN §1B/§2 缺行。
- **处置 3**：载体补 `0fb2bdaf…→75f8e2b4…` 迁移；矩阵/FROZEN 条件列改 pending/⏳；FROZEN-C06 §1B 补 v1.3 行。
- **r4**（`doc/reviews/FEA-11-RUN-GRANT-2C-PREREQ-1-r4.md`）：`changes_requested`（P0=0/P1=0/P2=1/P3=1）——R4-001 记录链仍停 r3；R4-002 FROZEN-C06 §2 缺 v1.3 条件行。
- **处置 4**：本段及 FROZEN/矩阵/EV 统一记录（矩阵条件列随后按 r5/r6 记录同步）；FROZEN-C06 §2 补 v1.3 行。
- **r5**（`doc/reviews/FEA-11-RUN-GRANT-2C-PREREQ-1-r5.md`）：`changes_requested`（P0=0/P1=0/P2=1/P3=1）——FROZEN-C06 §2 仍无 v1.3 条件行、两处 §1B 仍「待 r4 收口」。
- **处置 5**：FROZEN-C06 §2 补 v1.3 第 7 条（⏳）、§1B 两处改「待 r6 收口」；FROZEN-C16 §1B/§10、矩阵、EV 统一。
- **r6**（`doc/reviews/FEA-11-RUN-GRANT-2C-PREREQ-1-r6.md`）：**`approved`（P0=0/P1=0/P2=0/P3=1 非阻断，仅矩阵措辞）**；session `308751b9-…`；reviewed_head `c1e19ed82`。
- **处置 6（落 approved）**：矩阵条件列改「r1–r5 处置后待 r6 收口」；FROZEN-C06 §2 第 7 条 → ✅、§1B/§7 → approved；FROZEN-C16 §1B/§10 → approved、§2 第 8 行 → ✅；EV 同步。**C-06/C-16 字节保持 `75f8e2b4…`/`b8f46fb1…` 不变**（2 pins 不变）。

## 7. 证据

- `verification/FEA-11-RUN-GRANT-2C-PREREQ-1/pre-post.sha256`
- `changed-lines.diff`、`other-16-pins.txt`
- `carrier.md`、`EV.md`、`logs/{pins,check,check-taskpath}.log`
