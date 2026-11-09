# CONTRACT-UNFREEZE-2026-11-09-C17：C-17 v1.2 additive 载体

- 发起：DSH（Lead / Architect / Integrator；用户 2026-11-08 全部授权）
- 触发：`FEA-11-HOST-AUTH-3` scope review r1 判 `NEEDS_UNFREEZE`（`doc/reviews/FEA-11-HOST-AUTH-3-scope-r1.md`）→ ZCode 独立架构裁决（`doc/reviews/ADJ-2026-11-09-ZCODE-ARCH-ADJUDICATION.md`）**批准 C-17 单 pin ADDITIVE_UNFREEZE（路线 B + D-4 合批）**
- 目标契约：`doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md`（FROZEN v1.1，pin `aefa0fa5b17e0f10d9f23aebc3146c98c3c2bc170f2a18154d56a148e9701a59`）
- 冻结基线：`doc/plan/FEA-CONTRACT-FROZEN-C17.md`

## 1. 变更性质

**单 pin additive**：仅新增一条**只读** host-control 命令 `GetSourceSyncPlanMaterialized / source_get_sync_plan_materialized` + 1 个 DTO + 2 个错误码 + §5.3/§9 注记。**不修改**：六字段 `CompletionRequest`、HostJournal、C-16 grant 形状/校验、§6 CAS、§7 lineage、P1/P2/P4/P5/P6 断言、schema（无 DDL）。

- 18 pins 中**仅 C17 重算**；其余 17 pins 与既有冻结字节零变化。
- 新命令 wire 面：`new-manga.core` major=2 / minor=3（沿用 C-16 默认面 additive 先例）；强制 capability 门禁；普通面调用按 M2-C1 §5.7 拒 `HOST_ONLY_REQUIRED`。

## 2. 语义（为什么需要）

整树 kill（Host+Core 同死）后新 Core 无 source-read grant；C-17 禁止非缺失源 `grant_ids=[]`、ACK 要求 fresh grant。恢复路径要在 Host 侧**重铸 fresh grant**（TTL ≤300s），但重铸所需的 `version_id` + `entries` 只有 Core 已持久化的 `source_sync_plans.body_json` 有权威来源（Host 侧 `SourceIdentityCache` 纯内存、C# 生产 `grep PlanBody` 0 命中）。

新命令只是**回传 Host 自己在 `PlanSourceSync` 已提交过的同一物化子集**：不新增披露面、零写、不铸 grant、不建 operation/receipt/journal。

## 3. 变更清单（草案 `FEA-C17_SOURCE_SYNC_DRAFT.md`）

| 位置 | 变更 |
|---|---|
| 头部状态行 | v1.1 → **v1.2 / 2026-11-09 UNFREEZE 重冻**；载体指向本文件 |
| §0 版本面 | 文档 C-17 **v1.2**；命令面/全局默认/M2-C1 无增量 |
| §0 末段 | 增补「v1.2 仅新增只读计划物化投影命令」声明 |
| §5.1 命令表 | +1 行：`GetSourceSyncPlanMaterialized / source_get_sync_plan_materialized` |
| §5.2 DTO 表 | +1 行：`SourceSyncPlanMaterialization` |
| §5.3 | +1 条：v1.2 只读守卫（零写、closed shape、host-control、不铸 grant、不绕过 live 校验） |
| §8 错误闭集 | +2 码：`SOURCE_PLAN_NOT_FOUND`（not_found/false）、`SOURCE_PLAN_UNAVAILABLE`（internal/true） |
| §9 | +「v1.2 适用声明」：按 P3/P7/P8 执行，不改 P1/P2/P4/P5/P6 |
| §4（r1 复核增补） | host-control 枚举加入 `GetSourceSyncPlanMaterialized`；capability 串新增 `source.sync.plan-materialization/1`（`Capabilities` DTO 仍 7 项，沿 v1.1 先例）；修正「其余新Core命令沿Request/Response」残句 |

## 4. 风险与 NOT_RUN 声明

| 风险 | 处置 |
|---|---|
| 新只读命令成为越权读取面 | host-control + closed shape + wirelog 脱敏断言（沿用 C-16 §7）；读回值不构成授权 |
| 读回数据被误当授权 | §5.3 明写「不修改 C-16 grant 形状/校验，不绕过 live grant/lease/digest」；Host 重铸仍走 `RegisterSourceReadGrant` 校验 |
| 崩溃恢复未实测 | FEA-11-HOST-AUTH-3 实现须做真实 kill 注入；契约层面记 `NOT_RUN`，不得写成 PASS |
| 契约字节改动影响其他 pin | 只影响 C17；重冻后 `verify_pins` 必须 18/18 且其余 17 个哈希不变 |

## 5. 冻结程序（本载体必须全部完成才解除 blocked）

1. 草案 v1.2 字节落盘（本文件 §3 清单执行完毕）
2. **独立 byte-level 复核**（上下文独立子代理；对照 §3 清单逐行核对，确认无越界改动、无隐藏字段变化）
3. 复核通过后**重冻**：更新 `doc/plan/FEA-CONTRACT-FROZEN-C17.md`（v1.2 冻结字节三指纹：工作树 SHA-256 / blob ID / blob SHA-256）+ 追加 v1.2 变更记录
4. **pin 重算**：`tools/governance/verify_pins.ps1` 的 C17 映射更新为新 pin；全量 `verify_pins` 必须 **18/18 PASS**，其余 17 个哈希不变
5. **复冻记录**（本文件 §6 回填）
6. 最后才允许 `FEA-11-HOST-AUTH-3` 从 blocked 转 ready（另立 scope 冻结）

**r1 复核处置（2026-11-09）**：`doc/reviews/C17-v1.2-byte-review.md` 判 CHANGES_REQUESTED（P0=0/P1=1/P2=4/P3=6）。处置：P1-1/P2-1 → §4 增补（本表第 8 行）；P2-2 → §5.3 归因修正（body_json 仅含计划子集，state/expires_at 为表列）；P2-3 → DTO `version_id?`/`content_digest?`（missing 目标合法为 null）；P2-4 → §0「不改变既有错误码语义，仅新增两个码」；P3-1 → §5.3 补 host-control 复述。以上均为 §3 清单内增补，未越界改受保护条款。

## 6. 复冻记录（待回填）

| 项 | 值 |
|---|---|
| 复核 head | 待填 |
| 复核结论 | 待填 |
| v1.2 工作树 pin | 待填 |
| v1.2 blob ID / blob SHA-256 | 待填 |
| verify_pins | 待填（须 18/18） |

## 7. 不构成什么

- 不构成 UNFREEZE 完成（程序未走完）；
- 不构成任何实现授权（`FEA-11-HOST-AUTH-3` 仍 blocked）；
- 不改其他 17 份冻结契约的任何字节。
