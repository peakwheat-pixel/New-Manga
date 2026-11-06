# DSH 进度与裁决记录（2026-11-07 起）

> 用途：满足「需要用户拍板的事项写进『待裁决』区并附推荐，但不阻塞推进」；实际裁决按用户授权交 Codex（优先）或 DSH，Codex 无额度/不可用时转 ZCode。本文件由 DSH 维护，事实以 Git/仓库字节为准。

## 1. 当前进度（自动更新）

| 项 | 值 |
|---|---|
| HEAD | `b2261825e`（main，origin 同步，AHEAD=0） |
| 本轮已完成 | `FEA-11-RUN-GRANT-1-PREREQ-1` done（`116a711ba`；C-06 v1.2+C-16 v1.3 UNFREEZE，r3 approved）；`FEA-11-RUN-GRANT-1` done（`a11ded0d3`；AC-R1…R7 MET，r1→r2→r3 approved） |
| 基线 | pytest 3281/10；全量 .NET 1551/0/89；pins 18/18；check PASS(3w) |
| 下一队列 | ①`FEA-11-RUN-GRANT-2` proposed（scope review 中/待裁决）；②L-S1 registry resilience；③L-S4 死代码；④L-R11 两读面 gate 统一；⑤C-04b 8 项文档 residual；⑥SCAN-2 RH-1…RH-5；⑦UI P3/L3/L4 |

## 2. 待裁决（需用户产品取舍的候选；DSH 已附推荐并直接交 Codex/DSH 裁决，不阻塞）

| ID | 事项 | 推荐 | 状态 |
|---|---|---|---|
| U-1 | L-G12 产品边界是否接受为当前交付口径 | **纠正**：L-G12① 不是「边界收窄」而是**生产 100% 阻断**（Host version 恒 "1"）；登记 L-G15，由 RUN-GRANT-2A 修 | **已裁决（DSH S-3 + Codex）**；依据 scope review r1 D-1 |
| U-2 | 下一优先线：RUN-GRANT-2 vs 其它小项 | **2A（Host version）最先 → 2B（C-16 v1.4 容器成员）→ L-S1**；L-S4/L-R11/C-04b/SCAN-RH 穿插；2C（长 Run）另卡 | **已裁决（DSH S-1）**；依据 scope review Q5 + Codex |
| U-3 | 长 Run（>300s）授权续期是否本卡做 | **继续登记 limitation；续期另立设计卡**（不扩 2A/2B） | **已裁决（DSH S-1/S-5；Codex 同意）** |

## 3. 已裁决记录（Codex/DSH，含依据）

| 日期 | 裁决事项 | 结论 | 依据/记录 |
|---|---|---|---|
| 2026-11-06 | RUN-GRANT-1 契约路径（U-A vs identity 回退） | 采纳 U-A（新增 host-control 授权建立命令；C-06 v1.2 + C-16 v1.3 UNFREEZE）；否决 identity/facts 回退与 grant 进 overrides | scope review r1 + Codex 第二意见一致；载体 `doc/reviews/CONTRACT-UNFREEZE-2026-11-06-C06-C16.md` |
| 2026-11-06 | AC-R5 口径（Host managed 零回归） | 修订为「Core 授权面 managed 跳过 + Host best-effort 不阻断 + managed 读/metadata 零回归」；Host mint/能力失败不得阻断 Core 本可接受的 Run | Review r1 P1 R1-01；卡「Review r1 处置」 |
| 2026-11-07 | RUN-GRANT-1 集成与 closeout | 接受 r3 approved；L-G12 边界（version/容器成员 entry）如实保留；登记 follow-up `FEA-11-RUN-GRANT-2` | r3 报告；卡 Closeout Record |
| 2026-11-07 | 本轮继续推进策略 | 不阻塞于用户；按队列推进 RUN-GRANT-2 scope review，Codex 优先裁决，ZCode 故障转移 | 用户 2026-11-06 全授权 + 本轮目标 |
| 2026-11-07 | **RUN-GRANT-2 契约路径裁决（DSH S-1..S-6）** | 采纳 scope review 拆分：**2A（Host 从既有 `ScanSourceSync` 响应缓存 Core 权威 version，零契约）先做；2B（容器多成员 entry）需 C-16 v1.4 UNFREEZE（1 pin）+ 实现；2C 另卡；R3-02 并入 2A**。Codex 建议的「C-16 新身份查询命令（1 pin）」作为**未采纳备选**记录（契约面更大，2A 用现有响应已足够）。 | scope review `doc/reviews/FEA-11-RUN-GRANT-2-scope-r1.md`（READY-WITH-UNFREEZE）+ Codex 输入 `196dede9…`；卡 `FEA-11-RUN-GRANT-2A` DSH 裁决表 |
| 2026-11-07 | **L-G12① 纠正 + L-G15** | 生产 Host `scope.version` 恒 `"1"` → referenced Run dispatch 前 100% typed 拒绝（不是边界收窄）；L-G15 由 2A 修复 | scope review D-1；RUN-GRANT-1 卡 Closeout 补充（append-only） |

## 4. 更新规则

- 每次 closeout/裁决后更新 §1；新「待裁决」项写入 §2（附推荐）；裁决结论写入 §3（含记录路径）。
- 不把未落地写成已做；limitation 与 NOT_RUN 如实保留。
