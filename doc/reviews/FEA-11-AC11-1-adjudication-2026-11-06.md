---
task: FEA-11
decision: AC11-1-MET-WITH-LIMITATION
author: DSH（Lead / Architect / Integrator；2026-10-25 用户接管授权）
date: 2026-11-06
reviewed_head: 987d81981baf6e45c0de520bcd905b26f524fd34
inputs:
  - doc/reviews/AC11-1-ADJUDICATION-INPUT-2026-11-06.md（fresh subagent `8a6c3d10-bc90-4809-95ed-7d3be9648869` 独立裁决输入，未参与任何 AC11-1 相关实现）
  - doc/tasks/FEA-11.md（AC11-1 原文与历史 limitation）
  - doc/tasks/FEA-11-SCAN-1.md / FEA-11-SCAN-2.md / FEA-11-WATCH-1.md（承接卡 closeout）
  - doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md §3.6；doc/plan/FEA-C01b_STORAGE_CONTRACT_DRAFT.md SC-25；doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md v1.1 §0
limitation: AC11-1-L-STARTUP（启动不做全量内容扫描；最迟默认 900s 周期或下次访问/操作发现）
---

# FEA-11 AC11-1 终态裁决（DSH，2026-11-06）

> **裁决：AC11-1 终态 `MET`（带 limitation `AC11-1-L-STARTUP`）。**
> 解释口径：「**启动/访问前检查**」= ①启动期**冷启动目标枚举 + registry/root 可用性/授权核验**（FEA-11-SCAN-2）；②每次**访问/读取/操作前**的 live grant + stable lease + digest 强验证（FEA-11 + FEA-09 既有实现）。**不要求**应用启动时对全部已注册源执行全量内容扫描。
> 依据：AD-003 §3.6（用户架构决定，2026-10-31）与 C-01b SC-25（FROZEN v5，pin `3c9f5af7…`）的检测组合均为「访问前检查、操作前强验证、定期扫描、目录 watcher hint」四项，**不含启动内容扫描**；C-17 v1.1:18 把「启动/访问前」写成四路中的**一路**，其 v1.1 新增命令 `source_list_scan_targets` 只枚举目标、不读内容。
> 边界：FEA-11 已 `closed_with_limitations`，本裁决**不重开**该卡、不改历史 AC 行字节（`doc/tasks/FEA-11.md:103` 的 `- [ ]` 与双 `<<PARTIAL>>` 保持原字节），只在卡末追加 append-only「Closeout 补充」；STATUS/PLAN 仅做指针文本更新。

## 1. 裁决要点

1. **`MET`（带 limitation）**：AC11-1 的逐项语义都已有实现/测试或由明确承接卡闭合（见 §2）；「启动/访问前」按最高效力文本解释为「访问前强验证 + 启动枚举/核验」，与 AD-003/C-01b 冻结组合一致。
2. **不做启动全量内容扫描**：登记 limitation `AC11-1-L-STARTUP`——外部变化最迟在默认 900s（`NEWMANGA_SOURCE_SCAN_INTERVAL_SECONDS`，可配 [60,86400]）的下一周期或下一次访问/操作时被发现；访问时检测为 typed 阻断（`FILE_IDENTITY_CHANGED` / `SOURCE_GRANT_REVOKED` 等），后台 changed 观察由周期扫描/watcher 产生。
3. **不采纳 B（启动全量扫描）**：B 需要把「访问前检查」扩读为「启动也扫描」，超出 C-01b SC-25 的封闭组合，且成本/启动 IO 峰值未标定；若产品未来要求更低检测延迟，另立可选卡（非 AC11-1 前置，见 §5）。
4. **不改冻结字节**：不修改 C-01b/C-17/C-16/C-15/C-06/M2-C1/ADJ-001/FEA-01 任何字节；18 pins 不变。本裁决是**契约解释 + 实现闭合判定**，不是 UNFREEZE。

## 2. 四路闭合证据（逐项）

| AC11-1 子项 | 状态 | 证据 |
|---|---|---|
| 访问前检查（读取时强验证） | **已实现/已测** | `src/infrastructure/resource_channel/source_strict_read.py:12-41`（file identity + size + sha256 + 复核）；`src/application/importing/referenced/reader.py:50-111` 每次 entry 读取经 `read_verified_bytes`；测试 `tests/fea09/test_referenced_flow.py:296,529`、`tests/fea09/test_referenced_scanner.py:79-89,139-149` |
| 操作前强验证（lease+digest，不被缓存替代） | **已实现/已测** | `src/infrastructure/resource_channel/source_read_refs.py:275-289` commit guard；`tests/fea11/test_source_scan.py:168-186`（撤销 typed）、`tests/fea11/test_source_sync.py:1541-1556`（同步前漂移 typed） |
| 目录 watcher 生产者/消费者 | **已实现/已测（FEA-11-WATCH-1 `done` `00083a977`）** | `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceWatcher.cs`；`Fea11WatchHostRuntimeTests.cs:22`（Ready→arm→真实事件 hint→Dispose disarm）；`SourceWatcherTests.cs`（去抖/合并/overflow/根删除/单飞/预算/脱敏） |
| 定时扫描（丢 hint/overflow 可全量重枚举） | **已实现/已测（FEA-11-SCAN-1 `done` `7080167e1`；WATCH-1 补 overflow 重枚举）** | `SourceScanScheduler.cs`（周期/预算/退避/单飞）；`tests/fea11/test_source_scan.py`；`Fea11ScanIpcTests.cs:29-128`（同 name/size 不同 bytes→changed；零 Core 写） |
| 相同 mtime/size 但字节变可发现；mtime/size 未变不作内容未变证明 | **已实现/已测** | `tests/fea11/test_source_scan.py:128-165`；`Fea11ScanIpcTests.cs:39-105` |
| Dirty 阻断依赖旧绑定的新写入 | **已实现/已测** | C-17 §6/§7.1 pending gate 与 lineage 守卫（FEA-11/FEA-11-LINEAGE-1）；`core_assembly.py:1622-1645` `run_source_guard` |
| 启动/访问前检查 = 启动枚举/核验 + 访问前强验证 | **MET（本裁决解释）** | 启动：`SourceScanScheduler.cs:1727-1733`（枚举只读、不读内容）、`RefreshTargetsAsync:525-638`（不触发 Tick）、`HostRuntime.cs:1326-1331`（后台非阻塞枚举）、`Fea11Scan2HostRuntimeTests.cs:29-77`；周期首 tick 在一个间隔之后（`SourceScanScheduler.cs:961-994`；`FEA-11-SCAN-1.md:183`） |

## 3. 为什么不采 B（启动全量扫描）

1. **文本层级**：AD-003 §3.6 与 C-01b SC-25（FROZEN v5）的检测组合只有四项且不含启动扫描；C-17 v1.1:18 的「启动/访问前」是一路（否则成五路）。B 依赖 FEA-00 提案措辞与 SCAN-1 scope review 的拆读，二者均非冻结文本。
2. **正确性非必需**：任何访问/读取都被 live grant + lease + digest 拦截（typed 失败），周期扫描在 900s 内兜底；B 的收益只是「重开应用后更早后台发现」，属检测延迟优化。
3. **成本与风险**：启动期全量读+digest 对大型/网络/可移动卷会产生 IO 峰值，需要一次性 pass 的预算/退避/单飞/停机取消/状态面设计与判别测试，且要显式声明不改变 SCAN-1 的 900s 周期与「冷启动不枚举」冻结行为（范围变更须先 scope review）。
4. **治理一致性**：B 会让 C-01b SC-25 组合仍需追加解释；A 使该冻结条款的四项全部有实现/测试，契约债务闭环。

## 4. Limitation（登记进 FEA-11 Closeout 补充）

```text
AC11-1-L-STARTUP（DSH 裁决 2026-11-06，A 解释）：
应用启动不做全量内容扫描。启动期只做冷启动目标枚举与 registry/root 可用性/授权核验
（FEA-11-SCAN-2），随后由周期全量扫描（FEA-11-SCAN-1，默认 900s，可配 [60,86400]）
与 watcher hint（FEA-11-WATCH-1）承担后台发现；任何访问/读取/操作前仍有 live grant +
stable lease + digest 强验证（失配 typed 阻断）。
因此关闭期间发生的外部变化，最迟在下一周期或下一次访问/操作时被发现；
不承诺应用启动即发现。若产品要求更低延迟，另立可选卡（非 AC11-1 前置）。
```

## 5. 可选后续卡（非 AC11-1 前置，不自动释放）

- 候选 `FEA-11-STARTUP-SCAN-1`（启动后一次性只读全源扫描）：Host Ready 且冷启动枚举尝试完成后，对当前 target 集执行一次 `ScanSourceSync` pass（受预算/退避/单飞/停机取消），结果只进 `SourceScanStatus`；不建 plan/apply、零 Core 业务写、不改 900s 周期语义。
- 释放条件：产品确有「启动即后台发现变化」的需求，且先做独立 scope review；**不得**因本裁决自动建卡/释放。

## 6. 历史字节与门禁

- `doc/tasks/FEA-11.md:103` 的 AC11-1 行 `- [ ]` 与两个 `<<PARTIAL>>` **保持原字节**；终态以本裁决 + FEA-11 末尾 append-only「Closeout 补充」为准。
- 不修改 `FEA-11` 的 `closed_with_limitations` 终态、`delivery_head`、Canonical Evidence 或 18 pins；不修改任何历史 Review/证据字节。
- 门禁：`check.ps1 -TaskPath doc/tasks/FEA-11.md`、`check.ps1`、`verify_pins.ps1`（18/18）、`task_ledger.py --write`；本裁决为文档面变更，不重跑 pytest/.NET（未被代码改动触及）。

## 7. 决策记录

- 用户授权（2026-11-06）：「自动推进，全部授权，裁决交给 Codex 或 DSH，不需要用户介入」；本裁决由 DSH 作出，独立输入由 fresh subagent 产出（未参与 AC11-1 相关实现/返修）。
- 输入文件：`doc/reviews/AC11-1-ADJUDICATION-INPUT-2026-11-06.md`（A+ 建议；含 A/B 矩阵、证据表、B 分支草案）。

AC11-1-ADJUDICATION: MET-WITH-LIMITATION — 「启动/访问前检查」= 启动枚举/registry-root 核验（SCAN-2）+ 每次访问/操作前 live grant+lease+digest 强验证；不要求启动全量内容扫描（L-STARTUP：最迟默认 900s 周期或下次访问/操作发现）；四路实现均有证据，冻结契约字节与历史 AC 行零改动。
