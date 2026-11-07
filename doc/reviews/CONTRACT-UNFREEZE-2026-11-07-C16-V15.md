# CONTRACT-UNFREEZE-2026-11-07-C16-V15：C-16 v1.5（`source.reattest/1` + `ReattestSourceLocation` + `roots_available`）

> 载体用途：按 C-16 冻结记录的 UNFREEZE 流程提出 C-16 v1.5 字节修订；须经独立上下文 fresh subagent 做 **byte-level 复核** + DSH 重新冻结后方可视为最终字节。
> 触发：用户 2026-11-06「自动推进/全部授权/裁决交 Codex 或 DSH」；`C16-V15-BATCH-scope-r1`（`6f75eb58-…`）**BLOCKED 按旧卡面**并推荐 b3 形状；ZCode 故障转移裁决（`cb81fae0-…` 对旧 scope？→ 本批 `74371e2a-…`）**接受 b3，恰 1 pin**；DSH 裁决 D-1…D-8（`doc/tasks/FEA-11-L-S4-B-PREREQ-1.md`）。
> 顺序约束：本载体 + C-16 + 冻结记录 + 矩阵为 UNFREEZE 提交；L-S4-B 实现另卡（依赖本 PREREQ）；B2 只冻结字段、实现延后。

## 1. 背景与目标

`C16-V15-BATCH-scope-r1` 核实：B1 显式重授权只改 Host Registry（新条目 gen=1、旧条目撤销），**不写 Core DB**；Core `source_locations` 停旧 `(registry_id,generation)`；Host 枚举精确命中要求（`SourceScanScheduler.cs:2162-2169`/`:1561-1610`）→ 只重授权不重导入/apply 的源静默丢失；周期 loop 只 tick 不重枚举（`:1118-1151`）。旧卡面「只读命令 + 零 DB 写」不可行（读面改不了行）；Host-only 重证会改 C-17 §5.3 fail-closed 语义（+1 pin + 安全复核）。

目标：C-16 v1.5 additive——①能力 `source.reattest/1`；②条件写命令 `ReattestSourceLocation`（只写 `registry_id/authorization_generation` 两列、`last_verified_at` 保持原值，复用 A 卡唯一 SQL）；③`source_list_roots` 的 `roots_available` 只读投影字段（实现延后）。**C-15/C-17/C-06/C-07/M2-C1 零字节；1/18 pins。**

## 2. 提议修订

### A. 头部与 §0
- 状态行 → `FROZEN v1.5`（历史 v1.0/v1.1/v1.3/v1.4 保留）；日期行补 v1.5。
- §0 能力追加 `source.reattest/1`：Host 在 B1 显式重授权成功后探测；缺失/探测异常 → 不发送、行为与现状一致。

### B. §1 `source_list_roots`
- 响应 additive `roots_available: [bool]`（与 `roots[]` 同序同长；缺失/不可读/身份不符/单根探测异常 → false；每根至多一次、锁外、不缓存；文件级损坏仍整命令 `SOURCE_REGISTRY_UNAVAILABLE`）；旧读者忽略；**实现延后**（无消费者）。

### C. §2.5 `ReattestSourceLocation`（host-control）
- 请求 closed shape **恰 2 键** `{source_id, grant_id}`；无 command/scope/路径/registry_id/generation 入参；形状错 → `INVALID_REQUEST`；host-only/session 违例沿用既有守卫码。
- **Core 校验顺序**：host-only → shape（恰 2 键）→ grant live/未过期/未撤销 + `scope.source_id` → location 四键身份 == grant facts → 条件 UPDATE；拒绝/无匹配**零写**。
- **Host 前置义务（不由 Core 校验）**：唯一 live 非撤销条目、恰 1 根、路径 normalize 与 Core location 同一物理文件、`live.CreatedAt > old.RevokedAt`、非 folder、每轮至多一次；不满足不发送（Core `source_locations` 无 path 列）。
- 动作：仅原地更新 `registry_id/authorization_generation`（**两值取自 live grant 载荷** `grant.registry_id`/`grant.generation`；`last_verified_at` **保持当前行原值**、不刷新审计时间、不取 `now()`）；复用 A 卡唯一 SQL（其 `(registry_id <> ? OR authorization_generation <= ?)` 与相等分支谓词保证仅当两列实际变化时更新，同值重复 `rowcount=0`）；不新增行、不改 source_id/digest/is_current/binding；响应 `{source_id, updated, version}`（`version` 只读诊断）；幂等（同 grant 第二次 `updated:0` 零写）/单调。
- 错误复用 §6 既有闭集（零新增）。

### D. §6/§10
- §6 增 v1.5 补充句（复用既有码，不新增）。
- §10 冻结条件追加 ⑦；变更记录追加 v1.5 行。

### E. 冻结记录/矩阵
- `FEA-CONTRACT-FROZEN-C16.md`：pin → v1.5 最终字节 sha256；v1.5 重冻记录；历史 pin 保留。
- `FEA-CONTRACT_FREEZE_MATRIX.md`：C-16 行 → `FROZEN v1.5`（2026-11-07）。
- `verify_pins.ps1` 不改；18/18（C16 新值、其余 17 不变）。
- **§1B v1.4 行登记**：FROZEN §1B 的 v1.4 行历史值保留并加注「历史行，见 §8」；原明细（r1 计数/session/head）见 §8，未改动历史 pin 值；v1.5 行追加。

## 3. 安全与兼容

- **安全**：请求由 Host 铸的签名 grant 证明同一 source + 同一物理身份；Core 不识路径；只写 `registry_id/authorization_generation` 两列（`last_verified_at` 不变）；拒绝零写；不自动重新授权/不重建 identity/撤销后不放行；folder 排除。
**契约就绪 ≠ 实现/产品可用**：本载体只解除 C-16 v1.5 语义阻塞；L-S4-B 实现与 B2 投影均未交付。
- **兼容**：旧 Host 不发送新命令；旧 Core 无能力 → Host 不发送、行为与现状一致；`roots_available` additive 旧读者忽略；无 wire minor/schema/依赖变更。
- **C-15 零字节的解释**：C-15 `:204` 要求重授权原地更新；`:314` 的「显式用户操作」= B1 点击；reattest 是事实传播而非新恢复动作（D-6 背书；若后续 Review 不背书则升 2 pins）。
- **C-17 零字节**：Host 枚举 exact-match 守卫原文不动；先修行、后枚举。

## 4. 风险与回退

- 风险：①1/18 pin 重签须独立复核；②reattest 若被扩大为通用修授权入口（同路径异身份/多 live/忽略时间序）会绕过 B1 R-1，靠 AC-LS4B-2/3 判别；③实现需保证「先 reattest 后枚举」顺序，不得在扫描内隐式写。
- 回退：恢复 C-16 v1.4 字节（sha `ad25fb3c…`）与冻结记录/矩阵；L-S4-B 不释放。

## 5. 独立复核要求

- Reviewer：未参与起草/前轮复核的 fresh subagent；只读最终字节；记录 session/reviewed_head。
- 核对：①本载体 §2 逐项落地；②仅 C-16/冻结记录/矩阵变化（`git diff --name-only`），C-15/C-17/C-06/C-07/M2-C1 及 src/apps/tools/tests 零 diff；③无新错误码/wire minor/schema/依赖；④pin 可复算、18/18、其余 17 不变；⑤安全语义无放宽（条件写/零写/幂等/单调/红线）；⑥载体/卡不夸大（契约就绪 ≠ 实现/产品可用）。
- 通过标准 approved（可含非阻断 P3）；随后 DSH 提交 UNFREEZE 并重跑 pins。

## 6. 复核结果（独立 byte-level）

- **r1**（`doc/reviews/FEA-11-L-S4-B-PREREQ-1-r1.md`）：`changes_requested`（P0=0/P1=2/P2=4/P3=5）——请求 4 键 vs 2 键矛盾；三列写入值来源未定义（`grant.created_at` 不在 grant 载荷）；Host/Core 校验混排；矩阵头 v1.4；FROZEN §2 缺 v1.5 行；形状错误码不一致。
- **处置 1**：请求改恰 2 键 `{source_id, grant_id}`；写入改 `registry_id/authorization_generation` 两列、`last_verified_at` 保持原值；Core/Host 义务分离；shape 错误 `INVALID_REQUEST`、host-only/session 沿用既有码；矩阵/FROZEN 行修复。
- **r2**（`…-r2.md`）：`changes_requested`（P0=0/P1=1/P2=4/P3=6）——`grant.created_at` 不在冻结 grant 载荷；矩阵头/FROZEN §2 表损坏；载体 §6 未记 r1；§2.5 ① 映射错误。
- **处置 2**：两列方案落 C-16；矩阵/FROZEN/载体修正。
- **r3**（`…-r3.md`）：`changes_requested`（P0=0/P1=1/P2=2/P3=7）——两列方案未传播到载体 §2.C/PREREQ I-2/C-16 用途/§10/FROZEN §9；FROZEN 状态与载体不一致；§6 权限面映射。
- **处置 3**：全包传播两列语义（规范条款 0 处三列/`grant.created_at`）；§6 映射拆分；记录链补充。
- **r4**（`…-r4.md`）：`changes_requested`（P0=0/P1=1/P2=0/P3=6）——R3-01 包级残留（FROZEN §9 同行两列/三列、PREREQ I-2、ZCode 记录）；R3-04 §1B 措辞；其余 P3。
- **处置 4**：FROZEN §9/PREREQ 两列化；§1B v1.4 行加注为历史摘要（原明细见 §8）。
- **r5**（`…-r5.md`）：`changes_requested`（P0=0/P1=1/P2=1/P3=3）——PREREQ I-2:67 残留三列；R5-N1 记录链停 r4；R3-04/08/09 残余。
- **处置 5**：PREREQ I-2 两列化；AUTO 卡两处修正；FROZEN 链、载体 §2.B/§2.E 修正。
- **r6**（`…-r6.md`）：`changes_requested`（P0=0/P1=0/P2=1/P3=2）——载体 §6 未记 r5/r6；§2.E 未登记 §1B v1.4 改写；AC-T5 字面句位置；反斜杠转义格式。
- **处置 6**：载体 §6 补 r5/r6；§2.E 登记；AC-T5 字面句落 §3；转义格式修正。
- **r7**（`…-r7.md`）：`changes_requested`（P0=0/P1=0/P2=1/P3=2）——FROZEN §1B/§9 链停在 r6 pending；§2.E 登记与措辞；转义格式。
- **处置 7（本轮）**：FROZEN §1B/§9、EV、载体 §6 统一为 `r1→r2→r3→r4→r5→r6→r7 changes_requested → 处置 → r8 pending`；§2.E 登记 §1B v1.4 行改写；转义格式修正。
- **r8**（`doc/reviews/FEA-11-L-S4-B-PREREQ-1-r8.md`）：**`approved`（P0=0/P1=0/P2=0/P3=0，仅非阻断观察）**；session `fc11c286-8b80-4276-9d57-9b4b226b30d5`，reviewed_head `59ba5189f`；C-16 字节保持 `a7f57ebd…` 不变；记录链四处一致、§2.E 登记、转义修正、证据/pins/check 全 PASS。
- **结论**：C-16 v1.5 通过独立 byte-level 复核（r1→r8，最终 r8 approved）；可提交 UNFREEZE 并重冻。

## 7. 证据

- `verification/FEA-11-L-S4-B-PREREQ-1/pre-post.sha256`
- `changed-lines.diff`、`other-17-pins.txt`
- `carrier.md`、`EV.md`
- `logs/pins.log`、`logs/check.log`、`logs/check-taskpath.log`
