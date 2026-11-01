# 自主段 Checkpoint · 2026-11-01（契约线收尾）

- **Agent**：DSH（Lead / Architect / Integrator），自主执行，用户不在线
- **仓库 / 分支**：`G:\CODEX\New Manga` / `main`
- **TaskStatus**：见下表（每项完成即 commit）
- **ExecutionState**：ACTIVE
- **起始 HEAD**：`6358cfd05`（工作区 clean；未 push 提交 246）
- **起始检查**：`check.ps1` PASS（3 warnings：11 非终态 Task / STATUS 3159 B / PLAN 6687 B）；`verify_pins.ps1` 13/13 PASS

> **性质声明（R-008）**：本文件是**计划与执行记录**，**不是任务释放**。队列各项的真实释放以 `doc/STATUS.md` 指针 + `doc/REBASELINE_PLAN.md` 当前 DAG + 范围冻结（`allowed_paths`）三者同时成立为准（09 §5.1：下一任务建议 ≠ 任务释放）。
>
> **恢复点登记**：本文件由 `doc/STATUS.md`「当前权威指针」指定为**当前 rolling checkpoint**（`doc/00_INDEX.md:15` 口径：当前恢复点 = STATUS 指定的 rolling checkpoint）。
>
> **与 §5.2 的关系（有意偏离）**：09 §5.2 偏好 Task-local checkpoint（`verification/<Task-ID>/`）并「不另建全局 CHECKPOINT.md」；本文件为**用户 2026-11-01 明确指令**指定的跨任务载体 `doc/checkpoints/AUTONOMOUS-<DATE>.md`，因此保留全局位置，并按用户指令登记为偏离；已同步把 `doc/checkpoints/**` 增列进相关 Task 的 `allowed_paths`，并让 STATUS 指向本文件，避免形成未登记的第二个恢复点。

## 队列与结果（每项完成即追加一行）

| # | 任务 | 结果 HEAD | check.ps1 | verify_pins.ps1 | 复核报告 | 问题/偏离 |
|---|---|---|---|---|---|---|
| 0 | 建立复核席位 `c01b-reviewer` + 本 checkpoint | — | — | — | — | 无 |
| 1 | 收口 `FEA-D06-GAP` | **done**（收口材料 `1027de616`） | PASS (3w) | 13/13 | `doc/reviews/FEA-D06-CLOSEOUT-r2.md`（approved，P0/P1=0，P2×6 非阻断；R1 为 changes_requested→已修） | R2 条件：done 为纯元数据回填；R2-001…006 技术债**未修**，登记待处置 |
| 2 | 收口 `FEA-C14-DRAFT` | **done**（收口材料 `ff432e97c`） | PASS (3w) | 13/13 | `doc/reviews/FEA-C14-CLOSEOUT-r1.md`（approved，P0/P1=0，P2×6 非阻断） | R1 条件：done 为纯元数据回填；P2-1/5 在 done 处理，P2-2/3/4/6 未修（非阻断） |
| 3 | L-3 Errata（裁定 `:63`/`:111` + C04b/C08/C13/C09 注记） | **approved**（`14e6e6a3c`；P2 修复 `500aa6b27`） | PASS (3w) | 13/13 | `doc/reviews/FEA-WRAP-ERRATA-r1.md`（approved，P0/P1=0，P2×5；2 处死链与 C-08 措辞已在 `500aa6b27` 修） | 裁定 §4:58 括注指向落空，已在 C-08 注记留痕、未改裁定正文 |
| 4 | 起草 `C-10`（不冻结） | **approved**（草案 v3 `b45658c17`） | PASS (3w) | 13/13 | `doc/reviews/FEA-C10-r2.md` + `FEA-C10-r3.md`（均 approved，P0/P1=0） | 未冻结：§10 待用户裁定阈值 `T`；已知 P2：§8 表末缺空行（格式） |
| 5 | PLAN 预算卫生 + WRAP 收尾材料 | **done**（收口材料 `6c0195437`；集成 `6cfe7ab92`） | PASS (2w) | 13/13 | `doc/reviews/FEA-WRAP-CLOSEOUT-r2.md`（approved，P0/P1=0，P2×4）；R1 为 changes_requested（P1×1 = Manifest 词表，已修） | PLAN 6777 B/57 行 → **2302 B/32 行**；历史 31 行原样迁入 `PLAN-HISTORY`（+38/−0）；closeout-check 数字为 `6c0195437` 时刻快照（P2-002） |
| 6 | C-10 文档冻结（用户 U-06/U-11） | **done**（冻结 `170b384e2`；pin `ec8fd862…`） | PASS (2w) | **14/14** | `doc/reviews/FEA-C10-r4b.md`（approved，P0/P1=0，P2×2 记录侧） | `T=4 DIP` 仅鼠标、跨阈保持、不随缩放、DPI 无关；13 份既有 pin 未变；实现线未释放 |
| 7 | U-09 前置登记（L-1/L-2/L-5 → 候选 Task 前置与 AC） | **approved**（`FEA-C11-PREREQ-r1` P0/P1=0；非终态、未集成） | PASS (2w) | 14/14 | `doc/reviews/FEA-C11-PREREQ-r1.md`（approved，P2×5 已处置） | 登记文档 `doc/plan/FEA-C11_IMPL_PREREQS.md`；不豁免、不释放实现（`G-DELETE-IMPL` OPEN） |
| 8 | FEA-01 稳定端口冻结（门禁链最后一环） | **done**（v2，pin `0370c189…`；集成 `bf1c8eb00`） | PASS (2w) | **15/15** | r1 `changes_requested`（P1×2）→ **r2 `approved`**（`FEA-01-FREEZE-r2`，P0/P1=0，P2×5） | 门禁链 4/4；稳定端口唯一载体 = C-07 清单；§3 待决项 8/8 对账（U-06/U-07 默认采用待追认）；不释放实现 |
| 9 | `FEA-02-CORE` 范围冻结卡（Codex 实现） | **ready**（交 Codex；`bf1c8eb00`） | PASS | 15/15 | `FEA-01-FREEZE-r2`（approved；范围冻结复核含 sln） | 写域 = ApplicationCore + 对应测试 + sln 两条项目条目；保留 Current、不双调度；L-1/L-2/L-5 判 N/A + 再触发 |
| 10 | FEA-02-CORE 实现交付与集成（Codex 实现） | **done**（集成 `135479270`；delivery `5efb8f58c`） | PASS (2w) | 15/15 | `doc/reviews/FEA-02-CORE-r1.md`（approved，P0/P1=0，P2×4） | 新增 25/25；干净 TEMP 全量 908/0/60（基线 883/0/60）；3 项 Host 失败=环境 flaky（非基线缺陷、非本 Task 引入）；无 Current 接线、无冻结字节改动 |
| 11 | FEA-00a 只读评估（FEA-00A-PREP-1） | **done**（集成 `aec780362`） | PASS (2w) | 15/15 | `doc/reviews/FEA-00A-PREP-r1.md`（approved，P0/P1=0，P2×6 已处置） | G1–G7 缺口证据（快照 `15aa7bf3b`）；A1–A7 断言；D1–D4 待用户拍板；未释放实现卡 |

## 偏离登记

| # | 偏离 | 原因 | 处置 |
|---|---|---|---|
| 1 | Resource Manifest 采用「纯文本说明 + 真实表格」，而非用户口头的「纯文本不建表」 | `check.ps1` 对 `done` Task 只接受非空 6 列表或 `verification/**` 单个 JSON；「纯文本无表」在现行检查器下不可满足 | 保留纯文本说明 + 只填真实路径/哈希；在 Task Closeout 与本节登记；如需纯文本口径须另立 governance Task 改检查器 |
| 2 | 全局 checkpoint 位于 `doc/checkpoints/`（§5.2 偏好 Task-local） | 用户 2026-11-01 指令明确要求该路径 | 增列 `allowed_paths`、STATUS 指定为恢复点、本节声明与 §5.2 的关系 |

## 待裁决（用户在线后裁定）

1. **C-10 冻结**：草案 v3 已起草并复核 `approved`，但**未冻结**。冻结前置 = 用户裁定阈值 `T` 的数值（草案 §10 第 1 项）+ 条款终稿；之后才走冻结记录 + pin + `integration_commit`。
2. **C-10 的验证等级口径**：草案 §8 给出 L1–L4 定义（方案 §15.6 只使用未定义）；若用户另有口径，冻结前替换。
3. **Resource Manifest 格式偏离**：用户口头要求「纯文本不建表」，但 `check.ps1` 对 `done` Task 只接受 6 列表或 `verification/**` JSON → 现采「纯文本说明 + 真实表格」；是否接受该偏离，或另立 governance Task 改检查器。
4. **既有保留项 L-1…L-9**（尤其 **L-5 整库恢复锁**、**L-1 四表 DDL 未冻**、**L-2 M2-C1 字节修订**）仍按冻结记录执行，需用户决定处置时机。
5. **`G-DELETE-IMPL` 仍 OPEN**：本段只做契约线，**未释放任何实现 Task**；实现线须按 C-11 选候选 → 建 Task → 独立复核，以用户确认为准。
6. **非队列非终态 Task 未处理**：`FEA-D07-UNBLOCK`、`FEA-GOV-11`（AC1/AC2 `<<PARTIAL: 待用户裁决>>`）、`GIT-CLEAN-*` 等保持原状，本段未触碰。
7. **已接受为非阻断的技术债**：D06 的 R2-001…006、C14 的 P2-002/3/4/6、C-10 的 R3-001（§8 表末缺空行，纯格式）——均**未修**，理由见各复核报告。
8. **裁定 `GATE-DELETE-CONTRACT-CLOSURE-2026-11-01.md:58` 括注指向落空**：该括注称 C-08 的 D07 表述「以其 §5 历史段落为准」，但 C-08 记录全文无 D07 表述。已按用户指令**不改裁定正文**，仅在 C-08 §8 注记留痕。

9. **FEA-01 §3 U-06 离线阅读 / U-07 外部卷**：默认采用方案默认（无独立裁决）；**待用户追认**；追认若只改产品默认 → 新裁决 + 调整受影响 Task，**不改 FEA-01 冻结字节**。

**处置状态（2026-11-01 18:43 用户在线裁定后）**：第 1 项 ✅ 已裁定（`T=4 DIP`，ADJ U-06；冻结进行中）；第 2 项 ✅ 采用 L1–L4（U-07）；第 3 项 ✅ 接受偏离（U-08）；第 4 项 ✅ 保留 L-1…L-9 不作整体豁免，L-1/L-2/L-5 进实现 Task 前置与 AC（U-09）；第 5 项 ⏸ `G-DELETE-IMPL` 仍 OPEN（未授权实现）；第 6 项 ✅ 非队列 Task 保持原状（U-10）；第 7 项 ✅ P2 暂不扩修（U-10）；第 8 项 ✅ 以追加 errata 澄清（U-10）。

## 用户裁定落盘（2026-11-01 18:43）

6 项在线裁定已写入 [ADJ-2026-11-01-FEA-DECISIONS](../reviews/ADJ-2026-11-01-FEA-DECISIONS.md)「追加裁决 U-06…U-11」：C-10 阈值 `T=4 DIP`（仅鼠标、`<4` 单击 / `≥4` 拖动、跨阈保持、不随画布缩放、DPI 无关、首版基线须 UNFREEZE）、验证等级 L1–L4、Resource Manifest 偏离接受、L-1…L-9 保留不豁免（L-1/L-2/L-5 进实现 Task 前置与 AC）、P2 暂不扩修 + 非队列 Task 原状 + 失效引用 errata + STATUS 陈旧阻塞描述纠正、推进 C-10 冻结且不释放实现 Task。

## 收尾（2026-11-01）

- **队列 5 项均已交付**：`FEA-D06-GAP` **done**（R2 approved）→ `FEA-C14-DRAFT` **done**（R1 approved）→ L-3 Errata **approved**（含 P2 修复）→ C-10 草案 **approved**（**未冻结**，待裁定 `T`）→ PLAN 预算达标（2302 B/32 行）+ WRAP 收尾（R2 `approved`，`6cfe7ab92`；done）。
- **边界零违反**：未 push；13 份冻结契约字节 0 改动（`verify_pins.ps1` 13/13）；未改 Gate 状态；未动用户数据；未运行安装器；未自审（全部独立复核）。
- 每项均有独立复核报告：`FEA-D06-CLOSEOUT-r2.md` / `FEA-C14-CLOSEOUT-r1.md` / `FEA-WRAP-ERRATA-r1.md` / `FEA-C10-r2.md` / `FEA-C10-r3.md` / `FEA-WRAP-CLOSEOUT-r1.md`（最后一项的 P1 修正后由 R2 确认）。
- 未完成/待裁决项见上节；`FEA-D07-UNBLOCK`、`FEA-GOV-11`、`GIT-CLEAN-*`、实现线保持原状。
- **已知环境债务（FEA-02-CORE 复核发现）**：`NewManga.Host.Tests` 的 junction 清理测试（`TileChannelTests`、`D4SecurityHarnessTests`）在共享/残留 TEMP 下会因 `Dispose` 删除 reparse point 抛 `UnauthorizedAccessException` 而失败（3 项），干净 TEMP 全量 0 失败；属既有 Host 测试健壮性债务，不属 FEA-02-CORE，登记待后续 Task 修。`r`n- **已知限制**：`doc/PLAN-HISTORY.md` 迁入块原样继承了旧 PLAN 表内的空行（第 62 行），其后 17 行在 GFM 下渲染为无表头续表——**按「原样迁移」要求不改这 31 行**，已在 `PLAN-HISTORY` 块后加说明。
- **更新（用户 18:43 裁定后）**：C-10 **已冻结**（v5，`T=4 DIP`，pin `ec8fd862…`，R4b approved）；U-09 前置登记 approved；失效引用 errata 与 STATUS 陈旧阻塞描述已按 U-10 纠正；P2 暂不扩修、非队列 Task 保持原状。

