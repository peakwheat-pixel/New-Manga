---
id: FEA-11-L-S4-B-PREREQ-1
title: C-16 v1.5 UNFREEZE（source.reattest/1 + ReattestSourceLocation 条件写 + roots_available 投影字段）
kind: contract
governance_version: 3
status: ready
approval: 用户 2026-11-06「自动推进/全部授权/裁决交 Codex 或 DSH」；权威 scope review `doc/reviews/C16-V15-BATCH-scope-r1.md`（fresh subagent `6f75eb58-…`，**BLOCKED 按现卡面**；推荐 C-16 v1.5 = §0 能力 `source.reattest/1` + §2.5 条件写 `ReattestSourceLocation` + §1 `roots_available` additive；C-15/C-17/C-07/M2-C1 零字节；**1/18 pins**）；Codex 不可用 → ZCode 故障转移裁决（见卡）；DSH 裁决 D-1…D-8（见下）
suggested_owner: dsh
owner: dsh
reviewer: 独立上下文 fresh subagent（byte-level；不得参与本 UNFREEZE 起草；session 见 `doc/reviews/FEA-11-L-S4-B-PREREQ-1-r1.md` 与载体）
depends_on:
  - FEA-11-L-S1-B-RECOVERY-REAUTH-1
  - FEA-11-L-S4-LOCATION-AUTH-REFRESH-1
base_commit: 71d616881
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-11-L-S4-B-PREREQ-1
allowed_paths:
  - doc/tasks/FEA-11-L-S4-B-PREREQ-1.md
  - doc/reviews/FEA-11-L-S4-B-PREREQ-1-*.md
  - doc/handoffs/FEA-11-L-S4-B-PREREQ-1-*.md
  - doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C16-V15.md
  - doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md
  - doc/plan/FEA-CONTRACT-FROZEN-C16.md
  - doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md
  - verification/FEA-11-L-S4-B-PREREQ-1/**
out_of_scope:
  - 生产代码/测试（src/**、apps/**、tests/**）——L-S4-B 实现卡另起
  - C-15/C-17/C-06/C-07/M2-C1 及其余 17 份冻结契约字节
  - UI/App 实现；自动重新授权/自动重建 identity；schema/依赖；真实用户数据；push
---

# FEA-11-L-S4-B-PREREQ-1：C-16 v1.5 UNFREEZE

> **状态：`ready`（契约前置；只起草 + 独立 byte-level 复核 + 重冻；不实现）。**
> 来源：`C16-V15-BATCH-scope-r1` BLOCKED——L-S4-B 缺口不是读面能补的（B1 重授权只改 Host Registry，Core `source_locations` 停旧 `(registry_id,generation)`；Host 枚举/执行期要求精确命中且未撤销）；推荐形状为「C-16 v1.5 增加条件写 re-attest 命令 + 能力，B2 字段 additive，仍 1 pin」。

## DSH 裁决（2026-11-07）

| # | 裁决 | 内容 |
|---|---|---|
| D-1 | **零 DB 写只约束枚举/投影** | L-S4-B 的恢复触发允许**条件单行写**（只写 `source_locations` 的 registry_id/generation/last_verified_at 三列），复用 A 卡唯一 SQL；不新增表/迁移/依赖。 |
| D-2 | **形状 b3（推荐）** | C-16 v1.5 = §0 能力 `source.reattest/1` + §2.5 条件写命令 `ReattestSourceLocation`（请求 `{source_id, grant_id}`；closed shape；host-control envelope；live grant + live 非撤销 Host 条目 + 同一物理身份才写；恰一根/唯一 live；`live.CreatedAt > old.RevokedAt`；拒绝/无匹配零写；幂等/单调）+ §1 `source_list_roots` 的 `roots_available:[bool]` additive 字段。**否决** b2（Host-only 重证，会改 C-17 §5.3 fail-closed 语义，+1 pin + 安全复核）与 b1（只读新命令不达目标）。 |
| D-3 | **B2 只冻结字段、实现延后** | `roots_available` 无今日消费者（无 roots UI；导入复用/B1 诊断均不消费），且用它跳过失效条目自动注册 = 自动重新授权（撞 B1 R-1）。字段随 v1.5 冻结；B2 实现另卡（无消费者前不实现）。 |
| D-4 | **1/18 pins** | 只重签 C-16；C-15/C-17/C-07/M2-C1 零字节；错误码复用既有闭集（`SOURCE_ACCESS_DENIED`/`SOURCE_GRANT_REVOKED`/`SOURCE_BUDGET_EXCEEDED`/`SOURCE_REGISTRY_UNAVAILABLE`，不新增）。 |
| D-5 | **红线** | 不自动重新授权/不自动重建 identity/撤销后不放行/不下发路径/不新增 UI→Host 命令（`HostCommandRegistry.All` 不变、C-07 pin 不变）；folder 排除（L-S4-2）；`source_reset_registry` 后无旧条目可桥接 → limitation。 |
| D-6 | **C-15 零字节** | 解释：C-15 `:204` 已要求重授权原地更新；`:314` 的「显式用户操作」= B1 的点击；reattest 是该操作的事实记录，不是第二个恢复动作/授权决定。若独立复核要求字面澄清 → 在 C-16 载体加引用句，不改 C-15 字节。 |
| D-7 | **措辞修正** | 「零交互」限定为「用户完成 B1 显式动作之后不再要求第二次交互」；「周期枚举」改为「冷启动枚举 + 下一次 refresh 枚举（completed import/显式请求）」（周期 loop 只 tick，不重枚举）。 |
| D-8 | **基线修正** | STATUS 测试基线更新为 **3317/10、1617/0/93**（已在 71d616881 提交）。 |

## In（本卡变更点，冻结）

### I-1 载体
`doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C16-V15.md`：触发/授权/缺口/逐项修订/安全分析/兼容/回退/复核要求/结果。

### I-2 C-16 v1.5（`doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md`）
- 头部状态 → `FROZEN v1.5（2026-11-07 重冻；v1.0/v1.1/v1.3/v1.4 历史）`；日期行补 v1.5。
- §0 能力矩阵：新增 `source.reattest/1`（Host→Core；条件写 re-attest；零新错误码；minor 不变）。
- §1：`source_list_roots` 响应 additive 字段 `roots_available: [bool]`（逐根只读可用性投影；不改变既有字段/命令形状）。**实现延后（B2）**，但字段随 v1.5 冻结。
- 新增 **§2.5 `ReattestSourceLocation`（Host→Core，host-control envelope）**：
  - 请求 closed shape：`{"source_id": "<Core source id>", "grant_id": "<source-read grant id>", "command": "<PipelineCommand>", "scope": {"kind": "book|chapter|page|region|page_selection", "...": "<id 或 ids>"}}`（与 §2.4 同形；无路径/无 registry_id/无 generation 入参）。
  - 前置：`grant_id` 必须是 **live 且未撤销** 的 source-read grant（C-06 校验）；Host 侧必须存在**唯一** live 非撤销条目且其单根 `roots[0]` 与 grant 的 facts 同一物理身份；`live.CreatedAt > old.RevokedAt`（新条目晚于旧撤销）。
  - 动作：仅把 Core `source_locations` 当前行的 `registry_id/authorization_generation/last_verified_at` 原地更新为新条目（复用与 L-S4-A 同一单点 SQL；不新增行、不改 source_id/digest/is_current/binding）。
  - 拒绝/无匹配 → typed（复用既有闭集）+ **零写**；幂等（同条目重复 → 0 行或等价无变化）；单调（generation 不倒退）；恰一根/唯一 live；folder 源排除（L-S4-2）。
  - 成功响应：`{"source_id": "...", "updated": <int>, "version": "<current source version>"}`（closed shape；`updated` 仅 0/1）。
- §6 错误闭集：**零新增**（复用既有码）；§7 脱敏：请求/响应不含路径；§10 冻结条件追加 v1.5 条；变更记录追加 v1.5 行。

### I-3 冻结记录与矩阵
- `doc/plan/FEA-CONTRACT-FROZEN-C16.md`：pin → v1.5 最终字节 sha256；v1.5 重冻记录（历史 pin 保留）。
- `doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md`：C-16 行 → `FROZEN v1.5`（2026-11-07）。
- `verify_pins.ps1` 不改；18/18（C16 新值、其余 17 不变）。

### I-4 证据
`verification/FEA-11-L-S4-B-PREREQ-1/**`：pre/post sha、changed-lines.diff、other-17-pins、pins/check 日志、carrier。

## Out

- 生产实现（L-S4-B 实现卡）；B2 实现（延后）；C-15/C-17/C-06/C-07/M2-C1；UI；自动重新授权；schema/依赖；真实用户数据；push。

## Acceptance Criteria（v3）

- [ ] **AC-T1 契约增量最小**：C-16 v1.5 只含 I-2（能力 `source.reattest/1` + §2.5 命令 + §1 `roots_available` 字段 + §6/§7/§10 澄清）；C-15/C-17/C-06/C-07/M2-C1 及其余 17 契约逐字节不变；无新错误码/wire minor/schema/依赖。
- [ ] **AC-T2 安全语义明确**：§2.5 明确 live grant + live 唯一非撤销条目 + 同一物理身份 + `live.CreatedAt > old.RevokedAt` + 恰一根/唯一 live + folder 排除；拒绝/无匹配零写；幂等/单调；无路径/无 registry_id 入参；不自动重新授权/不重建 identity。
- [ ] **AC-T3 独立 byte-level 复核 approved**：fresh subagent 复核最终字节（diff 逐行、安全语义无放宽、17 项不变、pin 可复算）；P0/P1=0；session/reviewed_head 入载体。
- [ ] **AC-T4 重冻与 pins**：FROZEN-C16 更新；矩阵更新；`verify_pins` **18/18**（C16 新值、其余 17 原值）；`check.ps1`（默认 + `-TaskPath`）PASS。
- [ ] **AC-T5 载体与不夸大**：载体含触发/授权/变更点/安全/兼容/回退/复核要求/结果；明写「契约就绪 ≠ 实现/产品可用」；未改 C-15/C-17/错误闭集/Run wire。

## 独立复核要求（byte-level）

- Reviewer：未参与起草/前轮复核的 fresh subagent；只读最终字节；记录 session/reviewed_head。
- 核对：I-2 逐项落地；C-15/C-17/C-06/C-07/M2-C1 及其余 17 契约零字节；无新错误码/wire minor/schema/依赖；pin 可复算 18/18；载体/卡不夸大。
- 通过标准 approved（可含非阻断 P3）；随后 DSH 提交 UNFREEZE 并重跑 pins。

## ZCode 裁决记录

- **已记录（ZCode，2026-11-07，`subagent_zcode` 只读）**：**维持 BLOCKED 按旧卡面；接受推荐形状 b3**（C-16 v1.5 = `source.reattest/1` + §2.5 `ReattestSourceLocation` + §1 `roots_available`，**恰 1 pin**；C-17/C-07/M2-C1 零字节）；确认 b1/b2 否决正确；B2 字段随 v1.5 冻结、实现延后；背书条件写安全性（Host 签名 grant 作同一 source+四键身份证明；请求无路径；只写三列；复用 A 卡唯一 SQL；拒绝路径零写；幂等单调；校验顺序 host-only→shape→grant live→source_id→identity→条件 UPDATE）。
- **C-15 零字节的条件性（ZCode 补充）**：依赖 D-6 解释背书（B1 点击=显式操作、reattest=事实传播非新恢复动作）；DSH 已在 D-6 显式背书；若后续 Review 不背书则升为 2 pins（C-16+C-15），不得把解释当既定事实。
- **ZCode 补充 AC**：① 每轮 refresh 每 target 至多一次 reattest、无重试风暴 → 已入 L-S4-B 卡 AC-LS4B-9；②「零交互」限定为 B1 显式动作之后的传播、禁止「自动恢复/自愈」字样 → 已入 AC-LS4B-10。
