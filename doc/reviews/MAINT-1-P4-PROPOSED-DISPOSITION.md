# P4 · 4 张 FEA proposed 卡处置（MAINT-1，2026-11-14）

依据 `doc/REBASELINE_PLAN.md` 的 DoD §2「proposed 卡已逐张处置为 released 或 OUT」。
本记录只处置提案，**不改任何历史字节**；状态变更一律在裁决记录落盘之后。

## 0. 处置结论

| 卡 | 实质 | 处置 | 是否需双签 |
|---|---|---|---|
| `FEA-11-HOST-AUTH-4` | HOST-AUTH-1 limitation 6/7/8/9 + HOST-AUTH-2 Review P3-1…8/10（测试/健壮性观测项，无产品可见变化） | **OUT**（保留为已登记限制） | 否（非产品取舍） |
| `FEA-11-L-S1-B2-ROOTS-AVAILABILITY-1` | C-16 v1.5 已冻结 `roots_available` 字段，**当前无消费者**（无 roots UI、导入复用与 B1 诊断均不消费） | **OUT**（字段保留在契约内，实现延后至有消费者时） | 否（无用户可见功能） |
| `FEA-06-RESIDUAL-4` | 「查看对照」面板：Current V2 也没有该功能；实现需 C-07 additive UNFREEZE + API inventory 重算 | **待 Q7 双签**（见 §1） | **是** |
| `FEA-11-HOST-AUTH-5` | HostRuntime/dispatcher 全链路 e2e：仓内**无** register→scan→plan→apply→ACK 全链路用例；需 `HostOptions` Core 覆盖 seam（约 4–6 行） | **待 Q8 双签**（见 §2） | **是** |

## 1. Q7：`FEA-06-RESIDUAL-4` 的两条路线

| 路线 | 内容 | 代价 | 后果 |
|---|---|---|---|
| R1 实现 | 把逐 region 冲突投影加入 `IHostController` → 触 `generate_api_inventory.py` 与 **C-07 pin** → 需 `FEA-C07` additive UNFREEZE 载体 + byte-level 独立复核 + 重冻 | 1 张 UNFREEZE 卡 + 1 张实现卡 + UI | 新增用户可见功能「查看对照」 |
| **R2 裁 OUT（推荐）** | 正式记录「不提供查看对照，仅保留并发冲突横幅 + typed 原因」 | 1 条裁决记录 | 用户可见后果：冲突时只能看到横幅与原因，不能并排比对 |

推荐 R2 的理由：① Current V2 亦无此功能，不属于回归；② 红线 8「不扩大产品范围」；③ 实现需动冻结契约与 pin，风险/收益比不利。
待双签确认后落 `doc/reviews/`，并以 `NOT_APPLICABLE: 产品范围决定（无查看对照）` 更新 `FEA-06-RESIDUAL-2` 卡（append-only）。

## 2. Q8：`FEA-11-HOST-AUTH-5` 的验收强度

| 路线 | 内容 | 代价 | 收益 |
|---|---|---|---|
| R1 释放实现 | `HostOptions` 加最小 Core 覆盖 seam（4–6 行）+ 全链路 e2e 用例（register→…→ACK，断言 `acknowledged`、gate 开、源字节守恒、ACK fresh） | 1 张实现卡（Codex） + 1 轮独立 Review | 把「FEA-11 Host 授权已完成」从"部件已测"提升到"全链路已测" |
| **R2 裁 OUT（保守）** | 保留现状：部件级测试 + limitation 1 已登记 re-home | 0 | 全链路缺口作为已登记限制永久存在 |

说明：本项不改变任何用户可见行为，属**验收强度**取舍，不是产品功能取舍；但它是「done 是否名副其实」的关键一环，故仍按矩阵走双签。

## 3. 已直接执行的两项（本轮）

### 3.1 `FEA-11-HOST-AUTH-4` → `cancelled`（OUT）

理由：承接的都是 HOST-AUTH-1 的 limitation 6/7/8/9 与 HOST-AUTH-2 的 Review P3 观测项，均为**测试/健壮性**缺口，已在原卡 limitation 与 Review 中登记，不改变任何用户可见行为，也不影响 FEA-11 的 done 判定所用部件级证据。释放它会新增工作但不提升线收口判据。

保留：原卡 limitation 文本与 Review P3 条目全部保留；本处置只关闭"是否新建实现卡"这一问题。

### 3.2 `FEA-11-L-S1-B2-ROOTS-AVAILABILITY-1` → `cancelled`（OUT）

理由：C-16 v1.5 已冻结 `roots_available: [bool]` additive 字段，但**无任何消费者**（无 roots UI；导入复用与 B1 诊断不消费可用性）。在无消费者时实现探测，等于给未使用字段付 I/O 与锁外探测成本。

保留：契约字段保留（已冻结，不删）；若将来立项 roots UI/诊断消费该字段，重新开卡即可，本 OUT 可撤销。

## 4. 未处置完的部分（不得读作已完成）

`FEA-06-RESIDUAL-4` 与 `FEA-11-HOST-AUTH-5` 仍为 `proposed`，DoD §2 尚未满足。下一步为双签派发：
- 派 Codex：Q7、Q8 各一份书面建议（附证据与复现命令）。
- 派 ZCode：同一议题独立一份（不共享 Codex 结论）。
- 冲突时取更保守一方，另一方理由登记为残留风险。
