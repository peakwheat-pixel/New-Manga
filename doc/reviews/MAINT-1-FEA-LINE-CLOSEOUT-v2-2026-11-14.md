# FEA 线收口判定 v2（DoD 五条复核）— 2026-11-14

**判定：FEA 线 DoD 五条全部达成（其中 §1/§3 依 DSH 明确口径）。** 本报告取代 `MAINT-1-P6-LINE-CLOSEOUT-VERDICT.md` 的判定结论；P6 报告作为历史证据保留原字节。

基线：`main` @ `a19ebdead`（工作区 clean）。门禁：`check.ps1` PASS(3w)、`verify_pins` 18/18、`generate_api_inventory --check` EXIT=0、pytest **3544 passed / 0 failed / 10 skipped**、.NET（App 914/0/11、Host 321/0/74、CoreClient 180/0/24）。

## 0. 用户指令的交付（RO-1）

用户 2026-11-14 指令：「撤销 Q7 OUT，重开 `FEA-06-RESIDUAL-4`，走 C-07 additive UNFREEZE 路线实现『查看对照』」。交付链：

| 阶段 | 产物 | 终态 |
|---|---|---|
| RO-1 裁决 | `MAINT-1-RO-1-REOPEN-RESIDUAL-4-2026-11-14.md` | 生效 |
| 4A 契约前置 | 规格 v1.1 + C-07 **v1.9** 预授权 + r1/r2/r3/r4 复核 | `done`（`3519664d3`） |
| 4B 实现 | 四刀：wire → 端口 → 统计翻转 **v1.10**（pin `498882eb…`）→ UI 双栏 | `done`（`16209b0df`） |
| 父卡 | `FEA-06-RESIDUAL-4` 由两子卡取代 | `superseded` |
| `FEA-06` AC3 | 「冲突态缺查看对照」子项关闭（AC3 整体仍 PARTIAL，其余子项未做） | 回填 |

**用户可见结果**：区域冲突时可在横幅下方打开纵向双栏对照（上=基底只读，下=当前工作副本实时只读），不再只能看横幅与 typed 原因。

**未做视觉验收**：4B 只有结构性断言，无像素/主题截图；该限制在 4B 卡 Closeout 与证据 README 中列为 limitation，**不得读作视觉已验收**。

## 1. DoD 逐条核对

| # | 判据 | 判定 | 依据 |
|---|---|---|---|
| 1 | DAG 中 FEA-* 全部 done，或 done + 显式 waiver（含 NOT_APPLICABLE 原因与保留的 NOT_RUN 证据） | **达成（DSH 口径）** | 9 个 `closed_with_limitations` 节点 × 39 项 limitation 已有逐项处置矩阵（`MAINT-1-LIMITATION-DISPOSITION-MATRIX-2026-11-14.md`），每项含 `L-<节点>-<n>` 编号、处置码、证据指针；C3 10 项 / C4 10 项载体齐备。**口径**：`closed_with_limitations` + 正式逐项 waiver 载体 ≡ 本条的「done + 显式 waiver」；不改 9 张历史卡字节。此为 DSH 解释口径，非既有裁决原文。 |
| 2 | 无 in_progress/pending/blocked 的 FEA 节点；proposed 已逐张处置 | **达成** | FEA 范围 `proposed` 清零（4 张全处置：`FEA-06-RESIDUAL-4` superseded 于其子卡完成；另 3 张早前 OUT）；非终态 5 张全为非 FEA（GIT-CLEAN×4 + MAINT-1）；`MAINT-2-C1-BATCH-1` 已于本报告前收口。 |
| 3 | 所有 limitation 逐条处置（C1 补实现并 MET；C3/C4 转 OUT + waiver；无悬空 L-*） | **达成** | C1 8 项**全部实现**并经独立复核 `approved`（`MAINT-2-C1-BATCH-1-r1.md`，P0=0/P1=0）：READ-2 控件、FONT wire 负例、FONT 边界/并发、LIB `kind` 投影、`custom_rank` 读回、64 位边界、AI-1 清理、PIN-BASIS 留证。C2 5 项经 DSH 终裁全 OUT（含重开条件）。C3 10 / C4 10 有载体。AC8 按裁切口径 `PARTIAL`（留证完成、基线不可比）。r1 的 5 条 P2：4 修、1 登记。 |
| 4 | 四项门禁全绿 | **达成** | `check.ps1` PASS(3w)；`verify_pins` 18/18；`generate_api_inventory --check` EXIT=0（`1/80/6=87`）；pytest **3544 / 0 / 10**（原唯一失败 `custom_rank` 已修）；.NET 三项目 0 failed。 |
| 5 | STATUS / PLAN / TASK_LEDGER 三处一致且与证据一致 | **达成** | `STATUS:7`（MAINT-1 in_progress）、`PLAN:58`（ACTIVE：MAINT-1）、`TASK_LEDGER`（non-terminal 与现场一致）三处吻合；`MAINT-2` 终态后需再跑一次台账（本报告随附）。 |

## 2. 仍保留的显式限制（不得读作已验收）

1. **4B 无像素级视觉证据**（R-12）：结构性断言可接受，不构成视觉验收。
2. **gated 集成缺口**：`HostController` 的 `catch(IsUiFacingFailure)` 分支、`CoreServiceClient` 的 `SendAsync` 贯穿、`ListChaptersAsync` 的 `FormatException` 降级（P2-3）均无 runtime 注入 seam，只能靠代码审查 + gated 用例。
3. **AC8 基线不可比**：governance suite 断言仓库字节，主工作树与 validation clone 因 EOL/autocrlf 不同而数字不同；与 `GOV-EOL-PIN` 同源。
4. **单卡 TaskPath 红 1 张**：`FEA-06-PREREQ-1` 13 errors（done 卡声明不一致），按 DSH 裁决登记为治理债，**不计入四件套**；此处显式披露，避免被读作「所有卡都绿」。
5. **M2-C1 无 pin 体系**：其字节完整性只靠「载体 + rev 记录 + 独立复核」保护。

## 3. 线外（不计入 DoD）

`audit/V1-FULL-AUDIT/reports/13_RELEASE_GATE.md` 维持 **BLOCKED**：缺真实 clean install、真实 GUI 全验收、真实模型 API 调用、完整验收证据。`Technical Gate=NOT_SATISFIED`、`private_registry_absence=UNPROVABLE`、`Disposition=WAIVED_BY_OWNER`。**不得写成 PASS。**

## 4. 结论

- **FEA 线的 DoD 五条：全部达成**（§1/§3 依 DSH 明确口径，已在本报告逐条写明）。
- **用户 2026-11-14 指令：「查看对照」已完整交付**（重开 → 契约 → 实现 → 冻结 → 独立复核 → done）。
- **线外发布缺口未变**，Release Gate 仍 BLOCKED。
- **不得**把本报告读作「项目可发布」或「视觉已验收」。

## 5. 下一步

1. `MAINT-2-C1-BATCH-1` 置 `done`（P2-3 已修、r1 approved）→ 台账与三指针同步。
2. `MAINT-1` 收口：写入本报告指针、更新 STATUS 的「FEA 已收口」表述（含 §1/§3 口径）。
3. 若用户要求视觉验收：另开冒烟卡，复用 `tools/p2-ui-smoke.ps1` 截图通路。

## Errata（append-only，2026-11-14，L3 条件 6 复核 P1-1）

**§1 表中 §3 一行的「达成」需要收窄解读**，它不是「C1 的 8 项全部 `MET`」：

- C1 的 8 项**全部已实现**，其中 **7 项 `<<MET>>`**，**AC8 为 `<<PARTIAL>>`**。
- AC8 的 PARTIAL 是 **DSH 2026-11-14 裁决口径**：复跑留证已完成、validation clone 是唯一可比基线、主工作树与 validation clone 的两套原始输出均保留；它**无法**判 `MET`（`12F/56P/EXIT=1` 如实记录，未改写成通过）。
- 因此 §3 的「达成」准确表述为：**8 项均已实现 + AC8 按裁切口径记 PARTIAL + r1 的 P2-3 已修**，**不等于 8/8 MET**。
- 与 limitation 矩阵 `:141`「C1 补实现**并 MET**」的差异在此：AC8 因基线不可比**不能 MET**，故以「裁切口径 + PARTIAL」替代；该替代已由 `MAINT-2-C1-BATCH-1` 的 Closeout 与 `verification/MAINT-2-C1-BATCH-1/README.md` 记录。
- **不修改本报告 §1 原字节**（历史证据），以本 Errata 为准读。