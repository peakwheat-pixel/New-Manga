# DSH 进度与裁决记录（2026-11-07 起）

> 用途：满足「需要用户拍板的事项写进『待裁决』区并附推荐，但不阻塞推进」；实际裁决按用户授权交 Codex（优先）或 DSH，Codex 无额度/不可用时转 ZCode。本文件由 DSH 维护，事实以 Git/仓库字节为准。

## 1. 当前进度（自动更新）

| 项 | 值 |
|---|---|
| HEAD | `47a5b5167`（main，origin 同步；L-S1-B1 done，无活动 Task） |
| 本轮已完成 | C-15 v1.5（`ae8c2de07`）；L-S1 A（`b56c5a0e6`）；L-S4 A（`0ebb234bf`）；**L-S1-B1 done（`80d2799de`；r1→r2→r3 approved；AC-LSB MET；基线 pytest 3317/10、.NET 1617/0/93）** |
| 基线（本轮实测） | 全量 pytest **3317/10**；全量 .NET **1570/0/92**（Lead combined 全量 .NET 命中已知 flaky `FluentResidual2VisualEvidenceTests`，隔离复跑 1 passed）；pins 18/18；check PASS(3w) |
| 下一队列 | ①L-S4-B（proposed；零交互自动恢复枚举）+ B2（roots 投影）→ **C-16 v1.5 批量 UNFREEZE**（1 pin）；②2C 长 Run 续期（L-G1）；③L-R11 gate 统一；④C-04b residual；⑤SCAN-RH；⑥UI P3 |

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
| 2026-11-07 | **L-S1-B1 裁决（DSH D-1…D-10 + ZCode 故障转移）** | B1（App 显式恢复/重授权入口）**App-only 零契约 0/18 pins** 释放；B2（`source_list_roots` 可用性投影，C-16 v1.5）/B3（扫描侧投影）暂缓；**C-16 v1.5 版本号一次性批量保留**给 B2+L-S4-B；红线 R-1 禁「mint 失败就重注册」；`quarantine_path` 不展示；`ISourceImportController` 恢复面不扩 `IHostController`（C-07 pin 不变）。ZCode 裁决：**APPROVE**（D-1…D-10 全同意；附 1 项补登：C-17 journal 撤销撕裂 limitation，锚 `HostOperationOrchestrator.cs:112-133`，仅登记不处理）。 | 依据 `doc/reviews/FEA-11-L-S1-B-RECOVERY-REAUTH-1-scope-r1.md`、卡、ZCode `cb81fae0-…` |
| 2026-11-07 | **L-S4 契约路径（DSH D-1…D-6；ZCode 故障转移）** | A（重注册/重授权原地刷新接线，零契约 0/18 pins）本轮释放；B（零交互自动恢复只读枚举）需 C-16 v1.5 UNFREEZE 另卡；不得在 `RegisterSourceReadGrant` 里刷新；L-S4-1/L-S4-2 登记 limitation。 | 依据 `doc/reviews/FEA-11-L-S4-LOCATION-AUTH-REFRESH-1-scope-r1.md`、卡 |
| 2026-11-07 | **L-S1 契约路径（DSH D-1…D-9；ZCode 故障转移）** | 采纳 scope review：**C-15 v1.5 单条 UNFREEZE（1 pin）**；C-16/C-17 零改动；A（读取韧性）本轮、B（恢复/重授权，依赖 L-S4）另卡、C（corrupt 复制）limitation；错误码保持 `SOURCE_REGISTRY_UNAVAILABLE`（码义收窄登记）；`Authorize` 必须逐请求补位（只删不补=安全回退，红线）。Codex 不可用（limit）→ ZCode 裁决：对 D-1…D-9 无异议，建议 A Owner=ZCode（DSH 采用既有 Host Owner）。 | 依据 `doc/reviews/FEA-11-L-S1-REGISTRY-RESILIENCE-1-scope-r1.md`、`doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C15.md`、PREREQ 卡 |
| 2026-11-07 | **L-G12① 纠正 + L-G15** | 生产 Host `scope.version` 恒 `"1"` → referenced Run dispatch 前 100% typed 拒绝（不是边界收窄）；L-G15 由 2A 修复 | scope review D-1；RUN-GRANT-1 卡 Closeout 补充（append-only） |

## 4. 更新规则

- 每次 closeout/裁决后更新 §1；新「待裁决」项写入 §2（附推荐）；裁决结论写入 §3（含记录路径）。
- 不把未落地写成已做；limitation 与 NOT_RUN 如实保留。
