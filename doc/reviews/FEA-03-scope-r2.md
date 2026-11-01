---
document_id: FEA-03-scope-r2
kind: independent_scope_review
reviewer: fea03-scope-reviewer
reviewer_kind: subagent
reviewer_source: "同一独立席位续任（DSH Agent Teams durable teammate `fea03-scope-reviewer`，fresh 独立上下文，由 Team Lead `lead` 派发；未参与 FEA-03 的起草、v1/v2 范围冻结或实现）；子任务标识 = teammate target 名 + 本报告 frontmatter"
reviewer_independent: true
reviewed_by_implementer: false
author: dsh
base_commit: dfa70c002
reviewed_head: dfa70c002
reviewed_head_full: dfa70c002c1adf105342c4fd4fea2982afd80902
repository: G:/CODEX/New Manga
scope: "FEA-03 范围冻结 v2 复核（r1 P0×1/P1×7/P2×11 逐项 disposition 核验 + 新 findings）；只审范围冻结，不构成实现验收"
decision: changes_requested
verdict: changes_requested
p0_count: 1
p1_count: 5
p2_count: 12
checkps1: "Governance check: PASS (2 warnings)，EXIT=0（11 个非终态 Task + STATUS 达预算 80%）"
verifypins: "PIN AUDIT: PASS (all 15)，EXIT=0；C13 = d2cb8de4dd79…"
captured_at: 2026-11-01T23:22:00+08:00
captured_by: fea03-scope-reviewer
---

# Review：FEA-03 范围冻结 v2（base/reviewed_head = `dfa70c002`）

**结论：`changes_requested`（P0 × 1 / P1 × 5 / P2 × 12）。**

**不写 `approved`**：P0-01 未闭环（SC-D11 冻结语义仍未按 UNFREEZE 程序处置），另有 5 条 P1。本报告**只审范围冻结**，不评价实现、不构成实现验收；即使后续复核改为 `approved`，仍需实现、CORE/BRIDGE 验收、独立实现复核、集成与 AC 证据闭环。

判定口径沿用 r1：**P0** = 与冻结契约/授权直接冲突或按现文无法在不越权前提下实现，必须重写/先完成治理动作；**P1** = `ready` 前必须补齐的覆盖、自洽性或接口缺口；**P2** = 一致性、精度与证据卫生改进。

---

## 0. 复核对象、方法与环境

**被审 head `dfa70c002`（v2 提交，仅 5 个文档变更）**

1. [`doc/tasks/FEA-03.md`](../tasks/FEA-03.md)（v2 范围冻结卡，206 行；Q-6…Q-10、R-JOURNAL/R-RECEIPT、AC1–AC16、V1–V21、L、写域）
2. 入库的 r1 报告 [`doc/reviews/FEA-03-scope-r1.md`](FEA-03-scope-r1.md)（作为 disposition 依据，未改字节）
3. 指针：[`doc/STATUS.md`](../STATUS.md)、[`doc/REBASELINE_PLAN.md`](../REBASELINE_PLAN.md)、[`doc/TASK_LEDGER.md`](../TASK_LEDGER.md)
4. 对照契约/源码（只读）：C-13 冻结 v5（`doc/plan/FEA-C13_DRAFT_PROTECTION_DRAFT.md:151-153`、`:173`、`:181`、`:94`）及冻结记录（`:18`、`:55`）；`doc/contracts/V11R_REGION_WRITE_CONTRACT.md:146-150`、`:233`；`src/application/editing/{ports.py,service.py,errors.py}`；`src/domain/regions/entities.py:138-139`、`:187-189`；`src/infrastructure/sqlite/regions.py:288`（`commit_region_batch`）；`src/infrastructure/filesystem/managed_storage.py:98-124`；`src/bootstrap/core_assembly.py:747`、`:944`、`:1414`；`src/bootstrap/core_service.py:744`、`:5764`；`apps/desktop-avalonia/src/NewManga.CoreClient/CoreServiceClient.cs:352-362`、`NewManga.Host/{HostRuntime,DataSafety,Coexistence}.cs`；`apps/desktop-avalonia/tests/NewManga.ApplicationCore.Tests/`
5. 方案 §12.1 `:641`、§15.6 `:923`、§15.7 `:950`（与 r1 同口径）

**环境与只读证据**

- `git rev-parse HEAD` = `dfa70c002c1adf105342c4fd4fea2982afd80902`；`git status --porcelain` 为空（clean）。
- v2 提交 `git diff --stat 106299b50 dfa70c002` = 5 文件：`FEA-03.md`（+202/-81 行）、`FEA-03-scope-r1.md`（新增 364 行）、`STATUS.md`、`REBASELINE_PLAN.md`、`TASK_LEDGER.md`；**未改契约字节、未改源码**；`verify_pins.ps1` 15/15 PASS（C13 pin `d2cb8de4…` 未变）。
- `check.ps1` → `PASS (2 warnings)`，EXIT=0。
- 复核期间未修改被审文件；只新增本报告；未 commit/push。

**未执行**：未运行 `pytest`/`dotnet test`（无实现可测）；未实测 journal/receipt 崩溃与并发（无实现）；未逐字节重审 C-04b/C-08/C-01b/C-05 正文（本卡不改，只读冻结记录与交叉引用）。

---

## 1. r1 findings 逐项 disposition 核验

状态口径：**closed**（已按 r1 建议闭环）、**partial**（方向已落实但仍有必须修的缺口）、**open**（未闭环）。

| r1 ID | r1 问题（摘要） | v2 处置（证据） | 核验结论 | r2 关联 |
|---|---|---|---|---|
| P0-01 | AC11 与 C073 append-only 冲突、去重键不可判定 | Q-6（`:64`）+ R-LEGACY-1/2（`:100-102`）+ R-APPLY-2（`:92`）+ AC11（`:138`）+ V18/V19（`:174-175`） | **open**：方向（旧路径不变）合理，但未按 C-13 冻结记录 `:18` 走 UNFREEZE；SC-D11 明文仍被违反；V19 两种顺序的期望值仍未写出 | R2-P0-01 |
| P1-01 | 写域缺 data-root/journal 适配器/Draft 领域路径；`PageBindingVersion` 无口径 | `allowed_paths` 增 `src/domain/drafts/**`、`src/infrastructure/filesystem/**`、`src/bootstrap/core_assembly.py`、`src/bootstrap/core_service.py`（`:32-36`）；R-DRAFT-1 写明 `PageBindingVersion` 为注入的不透明整数、不读四表（`:73`） | **closed**（可再用性有 P2 级收窄建议） | R2-P2-02 |
| P1-02 | journal 宿主边界：只读、单写者、原子性、并发 | R-JOURNAL-1（app-owned `:79`）、R-JOURNAL-2（fsync/掉电窗口/`*.tmp` 清理 `:80`）、R-JOURNAL-4（只读 fail-closed + 单写者 `:82`）、R-JOURNAL-5（`:83`） | **partial**：规则已写，但“Host 只读”无输入通道、R-JOURNAL-4 无 AC/V、并发 flush 无断言；`fsync 目录` 在 Windows 上不可直接用 stdlib | R2-P1-02 / R2-P2-07 |
| P1-03 | commit receipt 缺失 | Q-7（`:65`）、R-RECEIPT-1/2（`:84-85`）、AC15（`:142`）、V20（`:176`） | **partial**：机制存在但多序列/崩溃窗口/保留期/摘要比对未自洽，且与 R-APPLY-2 冲突 | R2-P1-01 / R2-P1-04 |
| P1-04 | BRIDGE 写域矛盾、无独立验收 | Q-8（`:66`）、AC12 收窄（`:139`）、写域（`:107`）、禁止范围（`:182`）、CORE→BRIDGE→复核顺序（AC12 末句） | **closed**（写域矛盾消除；仍缺 AC12 的 V 行 → 归入 P1-06 残留） | R2-P1-03 |
| P1-05 | SC-D02/D06/D03/D10/D12 覆盖缺口 | D02：R-DRAFT-3 + AC2 deferral（`:75`/`:129`）；D06：AC16+V21（`:143`/`:177`）；D10：R-STYLE-1+AC9+V16（`:96`/`:136`/`:172`）；D03：Q-10+AC3+V7（`:68`/`:130`/`:163`）；D12：Q-9+AC10+V17（`:67`/`:137`/`:173`） | **partial**：D02/D06/D10/D03 基本闭环；D12 的 Q-9 选择存在保护变化漏检（见 R2-P1-05）；另 C-13 `:94` 导出/删除 preflight 边界未登记（R2-P2-10） | R2-P1-05 / R2-P2-10 |
| P1-06 | V 矩阵不覆盖全部 AC、多条 AC 不可机械判定 | V1–V21（`:157-177`）；AC2 测量方法（R-DRAFT-2 `:74`）；AC13 命令（`:140`） | **partial**：AC1–AC11/AC15/AC16 有 V；**AC12 仍无 V**；AC11 的 V19 无期望值（并入 P0）；AC13/AC14 为过程项未标注；崩溃注入机制未定义 | R2-P1-03 / R2-P2-06/08 |
| P1-07 | L-2 N/A 与 BRIDGE 错误面冲突 | Q-8 不接线、R-TOKEN/R-RECEIPT 新码仅 Core 内部、L-2 行注明 `allowedRunErrorCodes` 当前代码不存在（`:150`） | **closed**（L-2 N/A 在“不新增 Core 命令/不透传码”前提下成立）；“真实 Core 服务执行”需澄清（R2-P2-03） | R2-P2-03 |
| P2-01 | `allowed_paths` 含中文括号注解 | v2 全部纯 glob（`:23-44`），排除项移入正文（`:106`） | **closed** | — |
| P2-02 | reviewer 字段/Appointment 缺失 | `reviewer: fea03-scope-reviewer`（`:10`）、`review_appointment`（`:21`）、AC14 含 Appointment（`:141`） | **closed** | — |
| P2-03 | 禁止范围缺 C-04b/C-08；journal 目录 app-owned | `:181` 明列 C-04b/C-08；R-JOURNAL-1 `:79` app-owned | **closed** | — |
| P2-04 | R-LEGACY-2 过渡期判据不可执行 | R-LEGACY-3（`:102`）：`rg` 命令 + ②由 FEA-04/06 + ③复核 | **partial**：`rg "save_manual_translation\(" src apps` 未排除定义（会命中 `def save_manual_translation(`） | R2-P2-07 |
| P2-05 | 防抖“本卡实测”措辞/方法缺失 | R-DRAFT-2（`:74`）：实现实测 + p50/p95 + 证据文件 | **closed** | — |
| P2-06 | `RegionCandidate` 生命周期未定义 | R-CAND-2（`:90`）+ AC6（`:133`） | **closed** | — |
| P2-07 | AC13 回归基线未列 | AC13 给出 pytest 命令（`:140`） | **closed**（`tests/infrastructure` 过宽，R2-P2-08） | R2-P2-08 |
| P2-08 | AC5 原子写断言机制未定义 | AC5 + V10 定义 CRASH-A/B/C（`:132`/`:166`） | **closed**（注入机制与“模拟崩溃”口径仍需一句，R2-P2-06） | R2-P2-06 |
| P2-09 | 方案交付项映射缺失 | 交付项映射表（`:113-124`） | **closed** | — |
| P2-10 | 指针漂移 | STATUS 当前 Task/下一候选已修正（`:7`/`:11`）；PLAN C11 行已修正（`:10`）；LEDGER FEA-03 proposed（`:46`） | **partial**：PLAN 的 FEA-03 行仍是“范围冻结 v1；待 r1”（PLAN `:15`） | R2-P2-01 |
| P2-11 | 未复用 `commit_region_batch` | R-APPLY-1 明写复用/扩展（`:91`） | **closed**（在事务内保护检查位置需一句，R2-P2-09） | R2-P2-09 |

---

## 2. 逐项核查（对应派发清单 1–10）

### 2.1 P0-01：Q-6 与 AC11/V18/V19

- Q-6（`:64`）与 R-LEGACY-1（`:100`）确实选择“旧路径保持 C073 append-only、不静默去重”；R-LEGACY-2（`:101`）给出内容摘要 canonical 字段集与归一口径；R-APPLY-2（`:92`）给出“stale 先于去重”。方向与 r1 建议一致。
- **未闭环**：C-13 `:151-153` 是冻结字节，明文要求“新旧路径不得双写……无论走新 token 还是旧路径，都以最终去重键 `(RegionId, BaseRevisionId, 内容摘要)` 判幂等”“token 只防重放，不单独决定去重”。v2 把去重键限定为新路径回放、并由 receipt/token 单独决定，同时旧路径保持 append-only，这与 SC-D11 三处明文同时冲突。C-13 冻结记录 `:18` 规定修订须走 `CONTRACT-UNFREEZE-<DATE>` 载体 + 重新独立复核 + 重新冻结；v2 仅在卡内登记 `FOLLOW-UP-FEA03-1`（“需时走 UNFREEZE”），但 AC11 已经按偏离后的语义冻结验收——**必须先完成 UNFREEZE 再 ready**，否则实现就是“按未冻结口径落地”。
- **V19 期望值缺失**：V19 只写“旧→新 / 新→旧 各自期望固定；无意外双写”（`:175`），没有写出两个期望。按 v2 自身规则推导应为：旧→新 = 旧路径写入 1 个 revision、新路径因 stale 被 `STALE_BASE_REVISION` 拒绝（共 1 个）；新→旧 = 新路径写入 1 个 + 旧路径 append 第 2 个（共 2 个，这正是 SC-D11 所称的“双写”）。把“新→旧 = 2 revision”写清楚并把该偏差明确归属 Q-6/UNFREEZE，是 P0 的必要组成；否则 V19 不可机械判定。→ **R2-P0-01**

### 2.2 P1-01 写域

- `allowed_paths`（`:23-44`）已覆盖 `src/bootstrap/core_assembly.py`、`src/bootstrap/core_service.py`（`:35-36`，正文限定仅 data-root 注入）、`src/infrastructure/filesystem/**`（`:34`）、`src/domain/drafts/**`（`:32`）；`PageBindingVersion` 口径见 R-DRAFT-1（`:73`）。r1 P1-01 的主体已闭环。
- 残留：`core_service.py` 的写入授权很可能是**不必要的**——`assemble_production_core(data_root)` 已把 data-root 传给装配（`core_service.py:744`、`:5764`），`assemble_core_services` 内部由 `db_path` 派生 `data_root`（`core_assembly.py:1414`），journal root 可在 `core_assembly.py` 内构造，无需改 5937 行的 wire 分发文件。建议收窄/移除，降低误触 wire 的风险。→ **R2-P2-02**

### 2.3 P1-02 journal 宿主

- 规则面已补齐：app-owned（R-JOURNAL-1 `:79`）、写序含 flush/fsync/replace/fsync 目录与掉电窗口（R-JOURNAL-2 `:80`）、损坏丢弃（R-JOURNAL-3 `:81`）、只读 fail-closed + 单写者（R-JOURNAL-4 `:82`）、孤儿/Session 清理（R-JOURNAL-5 `:83`）。
- **接口缺口（实质）**：Host 的只读策略是 C# 侧 `DataRootPolicy`/`ReadOnlyHostException`（`HostRuntime.cs:228-235`、`DataSafety.cs:15-24`）；Core sidecar 只收到 `NEWMANGA_DATA_ROOT`/`M2RC1_DERIVED_ROOT`/`M2RC2_CATALOG_DB`/`M2RC1_MANAGED_ROOT`（`CoreServiceClient.cs:352-362`），`src/**` 中不存在 read-only 标志或通道（grep `read_only` 仅 `connection.open_readonly`）。本卡 CORE 是库级对象图、不接线 Host/IPC，因此“Host 只读时 journal 写 fail-closed”**无输入来源、无法实现也无法测试**；第二写者 fail-closed 也没有机制（依赖 Host 单实例？文件锁？均未写）。
- R-JOURNAL-4 没有对应 AC/V（V21 只覆盖 Session 结束/孤儿）；并发 flush 串行化也没有断言（R-DRAFT-4 只有规则）。→ **R2-P1-02**

### 2.4 P1-03 commit receipt

- 规则与 AC/V 已补（Q-7 `:65`、R-RECEIPT-1/2 `:84-85`、AC15 `:142`、V20 `:176`），且“与 journal 同目录、独立文件”明确。
- 但设计不自洽：① **单文件只存一条** receipt（`{tokenId, DraftId, DraftSequence, revisionId, committedAt}`），同一 Draft 多个 DraftSequence 提交后只保留最后一条，重启后重放**较早序列**的 token 无法命中 receipt → 可能产生第二个 revision；② **崩溃窗口**：apply 的 SQLite 事务提交后、receipt 文件写入前崩溃 → 重启重放无 receipt → 重复 revision；receipt 是文件、不在事务内，卡内没有 fallback（例如用 R-LEGACY-2 内容摘要回查 revision 历史去重）或两阶段收据方案；③ AC15 说“receipt 清理不影响 journal（R-RECEIPT-1/2）”，但 R-RECEIPT-1/2 **没有** receipt 清理/保留规则，R-JOURNAL-5 只规定“清理不得删除 receipt”；孤儿草稿的 receipt 是否永久保留、何时清、上限多少均未定义；④ R-RECEIPT-2 要求“同 token 但内容摘要不同 → 拒绝”，receipt 未存 content digest，只能从已提交 revision 的 snapshot 反算（可行但未写对象与方法）。→ **R2-P1-01**

### 2.5 P1-04/P1-07 BRIDGE 与 L-2

- Q-8（`:66`）把 AC12 收窄为“ApplicationCore 本地草稿缓冲 + 可注入 seam（不接线 Host/IPC/CoreClient）”，写域（`:107`）与禁止范围（`:182`）一致；`NewManga.ApplicationCore` 现状确为无 Host/IPC 依赖的纯 .NET 层（`README.md:3`），`NewManga.ApplicationCore.Tests.csproj` 存在。
- AC12 末句“CORE 先通过验收，BRIDGE 完成后 Task 才可提交复核”给出了可停靠状态（CORE 完成但 BRIDGE 未完成时 Task 不进入复核）。**写域矛盾已消除**。
- L-2 N/A（`:150`）在“不新增 Core 命令、错误码仅 Core 内部”前提下成立；v2 已注明 `allowedRunErrorCodes` 当前代码不存在（核实：`src/**`/`apps/**` 0 命中，仅 doc 有），该表述正确。
- 残留：**AC12 没有任何 V 行**（V1–V21 无 BRIDGE 场景）；“CORE 全部从真实 Core 服务执行”（`:153`）未定义是 `assemble_production_core` 对象图还是 `CoreServiceServer` 命令面——若后者，新增 draft 命令/码会把 L-2 N/A 与“不新增 wire 码”推翻。→ **R2-P1-03 / R2-P2-03**

### 2.6 P1-05 契约覆盖

- SC-D02：R-DRAFT-3 “UI 提示由 FEA-04 承载（deferral）”（`:75`）+ AC2（`:129`）✓。
- SC-D06：AC16 + V21（`:143`/`:177`）覆盖登记/清理/孤儿/receipt 保留 ✓；但 C-13 `:94` 的“导出与删除 preflight 前必须 flush 或提示”这一后果承接未在卡内登记（导出 Task AC / 删除侧 UNFREEZE），建议一行 deferral（P2-11）。
- SC-D10：R-STYLE-1 + AC9 + V16 含“错误必须列出违规键名” ✓。
- SC-D12：Q-9 选定 `manual_edited` + AC10 + V17，但见下条 **R2-P1-05**（与 C-13 `:173` 引用不一致，存在保护变化漏检）。
- SC-D03：Q-10 + AC3 + V7 ✓；但“不产生新 revision”的层级需明确——若指 apply 阶段则与 D06 §87 revision-owned state 冲突；应写明是草稿缓冲阶段（P2-06）。

### 2.7 P1-06 V 矩阵

- V1–V21 ↔ AC1–AC11、AC15、AC16 的映射基本完整：AC1(V1/V2)、AC2(V3/V4)、AC3(V5/V6/V7)、AC4(V8/V9)、AC5(V10/V11)、AC6(V12/V13)、AC7(V14)、AC8(V15)、AC9(V16)、AC10(V17)、AC11(V18/V19)、AC15(V20)、AC16(V21)。
- **AC12 无 V**；AC13/AC14 为过程项但未在表内标注“process/无 V”；V19 期望值未写（并入 P0-01）；AC5/V10 的“CRASH-A/B/C”未说明注入机制（异常注入 vs 真实 kill，CRASH-C 的“rename 后”具体时点）。→ **R2-P1-03 / R2-P2-06**

### 2.8 P2-01…P2-11

逐条见 §1 表：P2-01/02/03/05/06/07/08/09/11 已闭环（其中 P2-07/08 有小残留），P2-04 部分（`rg` 命令未排除定义），P2-10 部分（PLAN 的 FEA-03 行未更新到 v2/r2）。残留见 R2-P2-01、R2-P2-07、R2-P2-08；其余新 P2 见 §3。

### 2.9 v2 新问题

1. **R-APPLY-2 与 R-RECEIPT-2/AC4/AC15 直接冲突**：同 token 重放时 base 必然已 stale；按“stale 先于去重”会返回 `STALE_BASE_REVISION`，而 AC4/AC15 要求返回同 `revisionId`。两条规则不能同时满足，必须定义优先级。→ R2-P1-04
2. **receipt 多序列/崩溃窗口/清理/摘要比对**（见 §2.4）→ R2-P1-01
3. **journal 只读接口**（见 §2.3）→ R2-P1-02
4. **Q-9 manual 位漏检**：见 R2-P1-05（详见 §3）。
5. `fsync 目录` 在 Windows 上 `os.open(dir)` 会 `PermissionError`（本轮实测），仓库既有 `FILE_FLAG_BACKUP_SEMANTICS` 模式（`win_unlink.py:59`、`handle_resolver.py:52`）或 `managed_storage.write_temp/publish`（`:98-124`，只 fsync 文件 + replace）可参考；卡未说明实现或降级口径。→ R2-P2-07
6. R-APPLY-1 复用兼容性：`commit_region_batch` 签名（`ports.py:83-92`、`regions.py:288-297`）支持 `updated_regions` 的 `expected current` 与整批回滚 → 与 AC7 的 BaseRevisionId 校验兼容；但**没有 lock snapshot/digest 参数**（单条 `commit_region_revision` 有，`ports.py:74-81`），保护/lock/digest 检查只能在事务外预检，存在 TOCTOU 窗口。卡未写检查位置。→ R2-P2-09
7. 其他精度项：R-LEGACY-3 `rg` 未排除定义（P2-08）；AC13 的 `tests/infrastructure` 过宽（P2-09）；Q-10 措辞（P2-06）；C-13 `:94` 未登记（P2-11）；`core_service.py` 写权（P2-02）；`tests/core/test_region_write_commands.py` 写权与“旧路径语义不变”张力（P2-05）。

### 2.10 治理指针与检查器

- `STATUS.md:7` = FEA-03 `proposed`（范围冻结 v2，待 r2）✓；`:11` 下一候选已改 FEA-04/04b（r1 P2-10 的 STATUS 矛盾已修）✓。
- `REBASELINE_PLAN.md:15` 的 FEA-03 行仍是“范围冻结 v1；待上下文独立复核 r1”（**未同步 v2/r2**）；`:10` 的 FEA-C11-PREREQ-1 已改 approved ✓；`:29` 摘要中性可接受。
- `TASK_LEDGER.md:46` FEA-03 `proposed` ✓；`:39` FEA-C11-PREREQ-1 `approved` ✓。
- `check.ps1` PASS（2 warnings）；`verify_pins.ps1` 15/15 PASS。检查器仍不校验 `reviewer`/`allowed_paths`/PLAN 行版本文字/`approval` 元数据（r1 已实测，本轮结论不变）；因此上述 PLAN 漂移与 `approval` 字段滞后不会被机械检查发现。
- `GOAL-PROGRESS-2026-11-01.md` 未被 v2 修改；Q-6…Q-10 只存在于卡内，未进入 checkpoint/ADJ 裁决记录（r1 的检查点登记先例：`FOLLOW-UP-FEA00A-1` 在 `GOAL-PROGRESS:32`）。`approval` 字段仍为 `dsh_ruling_2026-11-01_GOAL_Q1_Q3`（`:7`），未反映 Q-6…Q-10。→ R2-P2-01/02

---

## 3. Findings（r2）

| 编号 | 级别 | 位置 | 问题 | 建议 | 状态 |
|---|---|---|---|---|---|
| R2-P0-01 | P0 | `doc/tasks/FEA-03.md:64`（Q-6）、`:100-102`（R-LEGACY-1/2）、`:138`（AC11）、`:175`（V19）；对照 `doc/plan/FEA-C13_DRAFT_PROTECTION_DRAFT.md:151-153`、`doc/plan/FEA-CONTRACT-FROZEN-C13.md:18`、`doc/contracts/V11R_REGION_WRITE_CONTRACT.md:146-150` | Q-6 的“旧路径保持 append-only、去重键只约束新路径”未按 C-13 冻结记录 `:18` 走 UNFREEZE 载体，仅以卡内 `FOLLOW-UP-FEA03-1`（“需时”）登记；但 AC11 已把偏离后的语义写成冻结验收。C-13 `:152-153` 明文要求“无论走新 token 还是旧路径”都以 `(RegionId, BaseRevisionId, 内容摘要)` 判幂等、且“token 只防重放，不单独决定去重”，v2 三点都不满足（旧路径不去重、内容摘要不是最终判据、receipt/token 单独决定回放）。V19 仍未写出“旧→新”和“新→旧”的期望值（按 v2 推导：旧→新 1 revision + `STALE_BASE_REVISION`；新→旧 2 revisions，即 SC-D11 所称“双写”） | 先做 `CONTRACT-UNFREEZE-C13`（明确 SC-D11 对新路径回放/旧路径的适用范围）→ 独立复核 → 重冻/重算 pin，再更新 AC11/V18/V19 并在卡内写明两个顺序的期望与偏差归属；若选择不 UNFREEZE，则只能按 SC-D11 字面实现（会改动 C073，仍需 UNFREEZE）。同步把 Q-6 裁决写入 checkpoint/ADJ 记录 | open |
| R2-P1-01 | P1 | `doc/tasks/FEA-03.md:65`（Q-7）、`:84-85`（R-RECEIPT-1/2）、`:142`（AC15）、`:83`（R-JOURNAL-5）、`:176`（V20） | receipt 设计不自洽：① `<DraftId>.receipt.json` 单对象只保留最后一次提交，重启后重放较早 DraftSequence 的 token 无 receipt → 可能产生第二 revision；② apply 的 SQLite 事务提交后、receipt 文件写入前崩溃 → 无 receipt，重放产生重复 revision（文件不在事务内，无 fallback）；③ AC15 引用“receipt 清理不影响 journal”，但 R-RECEIPT-1/2 无 receipt 清理/保留规则，孤儿草稿 receipt 生命周期未定义；④ 同 token 不同内容需内容摘要，但 receipt 未存摘要，且 R-LEGACY-2 只写“用于新路径回放判定”，未写反算对象（已提交 revision snapshot） | receipt 改为按 `(DraftId, DraftSequence)` 的多条记录（数组/按序文件）；定义提交协议（预写 pending → DB commit → 标记 committed，或 commit 后用内容摘要回查 revision 历史去重）；定义 receipt 保留/清理策略（含孤儿草稿）；AC15/V20 增加“崩溃于 DB commit 与 receipt 落盘之间”用例与“较早序列重放”用例 | open |
| R2-P1-02 | P1 | `doc/tasks/FEA-03.md:82`（R-JOURNAL-4）、`:106`（写域）；`apps/desktop-avalonia/src/NewManga.CoreClient/CoreServiceClient.cs:352-362`；`apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs:228-235`、`DataSafety.cs:15-24` | R-JOURNAL-4 的“Host 只读时 journal 写 fail-closed”没有输入通道：Core sidecar 只接收 data-root/derived/catalog/managed-root 环境变量，Host 只读策略是 C# 侧 `DataRootPolicy`；`src/**` 无 read-only 标志（仅 `connection.open_readonly`）。第二写者 fail-closed 也无机制说明（文件锁/复用 Host 单实例）。R-JOURNAL-4 没有 AC/V（V21 只覆盖 Session 结束/孤儿）；并发 flush 串行化也无断言 | 定义 Core 侧只读标志来源（assembly 参数/测试注入；生产由 FEA-04 接线并写明 deferral）与第二写者机制（例如 `<data-root>/drafts/.lock` 独占句柄，或明确以 Host 全局单实例为前提并加启动校验）；补 AC/V（只读下 journal 写被拒、内存草稿保留并提示；第二写者拒绝；并发 flush 串行） | open |
| R2-P1-03 | P1 | `doc/tasks/FEA-03.md:139`（AC12）、`:153-177`（V 矩阵）、`:205`（closeout） | AC12（BRIDGE 切片）在 V1–V21 中**没有任何 V 行**；AC13/AC14 为过程项但表内未标注；“V1–V21 覆盖全部 AC”的 closeout 表述不实 | 增 V22：`dotnet test apps/desktop-avalonia/tests/NewManga.ApplicationCore.Tests/NewManga.ApplicationCore.Tests.csproj`，断言 11 字段投影/单串行 patch 队列/flush 触发出现在桥接 seam/不引用 Host、IPC、CoreClient、Avalonia；closeout 改为“AC12 由 .NET 测试承载，AC13/AC14 为过程项” | open |
| R2-P1-04 | P1 | `doc/tasks/FEA-03.md:92`（R-APPLY-2）、`:85`（R-RECEIPT-2）、`:131`（AC4）、`:142`（AC15）、`:176`（V20） | R-APPLY-2 要求 stale 检查先于去重（“即使内容命中 receipt 也不返回旧 revision”）；但同 token 重放时 BaseRevisionId（首次 apply 前的 current）必然已 stale，按该规则会返回 `STALE_BASE_REVISION`，与 R-RECEIPT-2/AC4/AC15 的“返回同 revisionId、不产生第二 revision”直接矛盾；卡未定义 precedence | 明确顺序：token 有效性/过期 → receipt 命中（返回 revisionId，终止）→ stale base 检查 → 同 token 内容不一致拒绝 → apply；据此改写 R-APPLY-2（它只应约束“非 receipt 命中的内容去重/跨 token 场景”），并补 V20 的“重放时 base 已变”场景 | open |
| R2-P1-05 | P1 | `doc/tasks/FEA-03.md:67`（Q-9）、`:97`（R-DIGEST-1）、`:137`（AC10）、`:173`（V17）；`doc/plan/FEA-C13_DRAFT_PROTECTION_DRAFT.md:173`、`:181`；`src/domain/regions/entities.py:138-139`、`:187-189`；`src/application/editing/service.py:127-133`、`:1334-1341` | Q-9 选 `manual_edited` 作为 digest 的 manual 位，但 C-13 `:173` 引用的 `service.py:128-129` 实际读 `region.translation_locked or region.text.translation_locked`；两 bit 可分歧（manual save 后 region 列保持 False、text 列 True；随后 `set_locks(translation_locked=False)` 只把 text 列置 False，`manual_edited` 仍 True）→ digest（三锁 region 列 + manual_edited）在“文本人工锁被释放”时不变，apply 不会拒绝，违反 SC-D12 “任一目标 Region 的 digest 变化 → 拒绝”。AC10/V17 未覆盖该场景 | digest 至少纳入 `text_json.translation_locked`（或同时纳入两个 bit，二者都属保护位，不产生假阳性）；补 AC10/V17 的逐锁位矩阵与 unlock 场景；把 Q-9 的口径变更按 C-13 `:181`/实现铁律 2 登记，若属契约解释则并入 UNFREEZE/errata，避免实现后再改 | open |
| R2-P2-01 | P2 | `doc/REBASELINE_PLAN.md:15`；`doc/STATUS.md:7`；`doc/TASK_LEDGER.md:46` | PLAN 的 FEA-03 行仍写“范围冻结 v1；待上下文独立复核 r1”，未同步 v2/r2；STATUS/LEDGER 正确；`check.ps1` 不校验该文字 | 更新 PLAN FEA-03 行为 v2/r2；r2 处置时同步 | open |
| R2-P2-02 | P2 | `doc/tasks/FEA-03.md:36`（core_service.py 写域）、`:7`（approval）；`GOAL-PROGRESS-2026-11-01.md`（未被 v2 修改） | `core_service.py` 的写入授权很可能不必要（`assemble_production_core(data_root)` 已传 data-root，`assemble_core_services` 由 `db_path` 派生 data_root）；Q-6…Q-10 裁决只存在于卡内、未进 checkpoint/ADJ，`approval` 字段仍为 Q1_Q3；Q-6/Q-9 的 `FOLLOW-UP-FEA03-1/2` 只出现在卡内，无保留 owner/闭环条件（对照 `FOLLOW-UP-FEA00A-1` 在 `GOAL-PROGRESS:32` 的登记先例） | 收窄/移除 `core_service.py` 写权；把 Q-6…Q-10 与两个 FOLLOW-UP 登记到 checkpoint/ADJ（含 owner、闭环条件、必要时 UNFREEZE 载体指针），更新 `approval` 元数据 | open |
| R2-P2-03 | P2 | `doc/tasks/FEA-03.md:153`（“CORE 全部从真实 Core 服务执行”）、`:150`（L-2） | CORE 的测试执行面未定义：是 `assemble_production_core` 对象图（不经 wire）还是 `CoreServiceServer` 命令面（`tests/core` harness 的 `harness.rpc` 风格）。若为后者，新增 draft 命令/错误码会进入 wire 命令面，与 L-2 N/A、“不新增 wire 码”冲突 | 明确“真实 Core 服务 = assemble_production_core 装配后的对象图，直接调用 application 服务，不经 CoreServiceServer 命令面”；加一条机械断言（core_service.py 不新增命令/错误字面量）以锁定 L-2 N/A 前提 | open |
| R2-P2-04 | P2 | `doc/tasks/FEA-03.md:42-43`（`tests/core/test_region_write_commands.py`、`test_region_batch_locking.py` 写权）、`:100`（R-LEGACY-1）、`:185`（不降低既有断言） | AC11 要求旧路径语义不变，这两份 `tests/core` 基线测试不应需要修改；授予写权与“不降低既有测试断言”存在张力（易被用来放宽基线）。它们只应作为 AC13 回归读取 | 将这两份文件从写权移除，或明确“仅在基线因无关原因漂移且 DSH 批准时可改，不得削弱断言”；新测试放 `tests/editing`/`tests/domain`/`tests/infrastructure` | open |
| R2-P2-05 | P2 | `doc/tasks/FEA-03.md:68`（Q-10）、`:130`（AC3）、`:163`（V7） | “几何/样式按域合并 = 同键后到覆盖且不产生新 revision”的层级不明：若指草稿缓冲阶段（patch 层），不产生 revision 是自然结果；若指 apply 阶段，则与 D06 §87“区域状态变更须产生 revision”冲突 | 明确为草稿缓冲阶段的后到覆盖；apply 仍按 revision-owned state 产生 revision；必要时在 AC3/V7 措辞中点明 | open |
| R2-P2-06 | P2 | `doc/tasks/FEA-03.md:132`（AC5）、`:166`（V10） | CRASH-A/B/C 的注入机制未定义（异常注入点 vs 真实 kill -9；CRASH-C 的“rename 后”具体时点与 fsync 目录的关系），V10 不可直接实现 | 写明用可注入失败点模拟（在写 tmp 前/rename 前/rename 后抛错），明确“模拟崩溃即可、不要求真实进程 kill”，并说明模拟覆盖不到掉电持久性 | open |
| R2-P2-07 | P2 | `doc/tasks/FEA-03.md:80`（R-JOURNAL-2）、`:102`（R-LEGACY-3） | ①“fsync 目录”在 Windows 上不能直接用 `os.open(dir)`（本轮实测 `PermissionError`）；仓库既有 `FILE_FLAG_BACKUP_SEMANTICS` ctypes 模式（`win_unlink.py:59`、`handle_resolver.py:52`），既有 `ManagedFileStorage.write_temp/publish` 只 fsync 文件 + `os.replace`（`managed_storage.py:98-124`）；②R-LEGACY-3 的 `rg "save_manual_translation\(" src apps` 会命中 `def save_manual_translation(`，未实现“排除定义” | R-JOURNAL-2 写明 Windows 目录 fsync 的实现（ctypes CreateFileW+FlushFileBuffers）或降级为“文件 fsync + replace，目录项掉电可丢”并记录窗口；R-LEGACY-3 给出正确命令（如 `rg -t py "save_manual_translation\(" src apps` 再排除定义行，或 `-g '!**/service.py'`） | open |
| R2-P2-08 | P2 | `doc/tasks/FEA-03.md:140`（AC13） | AC13 的回归命令包含整个 `tests/infrastructure`（含 plugin 打包/沙箱等与本卡无关且可能受环境影响的项目），基线噪声大、skip 原因难判 | 收窄到与本卡相关的文件/目录，或明确“逐文件 outcome + skip 原因 + 与本卡无关的失败如何裁定”；新增测试在 Handoff 单列 | open |
| R2-P2-09 | P2 | `doc/tasks/FEA-03.md:91`（R-APPLY-1）、`:134`（AC7）；`src/application/editing/ports.py:83-92`、`src/infrastructure/sqlite/regions.py:288-297` | 复用 `commit_region_batch` 与 AC7 的 BaseRevisionId 校验/整批回滚**签名兼容**；但该 seam 没有 lock snapshot/digest 参数（单条 `commit_region_revision` 有，`ports.py:74-81`），保护/lock/digest 检查只能放在事务外预检，存在 TOCTOU；卡未写检查位置 | 明确保护/lock/digest 检查是“事务外预检 + 记录已知限制”还是“扩展 batch 在 BEGIN IMMEDIATE 内校验”（R-APPLY-1 已允许扩展）；若是前者，登记为已知限制并说明为何可接受 | open |
| R2-P2-10 | P2 | `doc/tasks/FEA-03.md:52`、`:143`（AC16）；`doc/plan/FEA-C13_DRAFT_PROTECTION_DRAFT.md:94` | C-13 `:94` 的后果承接（导出/删除 preflight 前必须 flush 或显式提示“有未保存草稿”；导出侧由导出 Task AC 承载，删除侧需 C-04b UNFREEZE）未在卡内登记，活跃草稿产生后这是必须显式 deferral 的边界 | 在“来源与授权”或“交付项映射”加一行：本卡不实现导出/删除 preflight，分别由 FEA-14-EXPORT AC 与 C-04b UNFREEZE 承载（引用 C-13 `:94`） | open |
| R2-P2-11 | P2 | `doc/tasks/FEA-03.md:129`（AC2）、`:159`（V3） | AC2 的“5 个强制 flush 触发点逐一断言”在 CORE 层只能测 flush API 被以 5 类原因调用，真实 UI 触发点在 FEA-04/06；未说明断言层级 | 写明 CORE 断言 = 5 类 flush 原因枚举均触发持久化；真实 UI 触发接线由 FEA-04/06 AC 承载 | open |
| R2-P2-12 | P2 | `doc/tasks/FEA-03.md:134`（AC7）、`:137`（AC10）、`:140`（AC13）；`doc/plan/FEA-C13_DRAFT_PROTECTION_DRAFT.md:175`、冻结记录 `:55` | C-13 冻结记录 `:55` 的“不新增任何错误码”与 v2 新增的 `EDIT_TOKEN_REUSED`/`DRAFT_FLUSH_FAILED` 措辞张力未在卡内说明；按上下文该铁律应限于 SC-D12（C-13 自身也新增 `EDIT_TOKEN_EXPIRED` 等 3 码），但需一句澄清，避免实现复核时争议 | 在 L-2 行注明：两个新码为 Core 内部实现标识、不是契约码、不进 wire；C-13 §4.4 的“不新增错误码”按 SC-D12 范围解释 | open |

---

## 4. 验证记录（实际执行）

| 场景 | 命令或步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| HEAD 与工作区 | `git rev-parse HEAD`；`git status --porcelain` | `dfa70c002`，main | PASS（clean） | `dfa70c002c1adf105342c4fd4fea2982afd80902`；空输出 |
| v2 提交范围 | `git show --stat dfa70c002`；`git diff --stat 106299b50 dfa70c002` | `dfa70c002` | PASS | 5 文件：卡、r1 报告、STATUS、PLAN、LEDGER；未触契约/源码 |
| 治理检查器 | `pwsh -NoProfile -File tools/governance/check.ps1` | `dfa70c002` | PASS（2 warnings） | `Governance check: PASS (2 warnings)` |
| 契约 pin | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | `dfa70c002` | PASS | `PIN AUDIT: PASS (all 15)`；C13 `d2cb8de4dd79` |
| STATUS/PLAN/LEDGER | 读 `STATUS.md:7`/`:11`、`REBASELINE_PLAN.md:10`/`:15`/`:29`、`TASK_LEDGER.md:39`/`:46` | `dfa70c002` | FEA-03 均 proposed；PLAN FEA-03 行仍是 v1/r1（R2-P2-01） | — |
| Host→Core 只读通道 | grep `NEWMANGA_`（`apps/desktop-avalonia/src`）；读 `CoreServiceClient.cs:352-362`、`HostRuntime.cs:228-235`、`DataSafety.cs:15-24` | `dfa70c002` | 无 read-only 标志；仅 data-root/derived/catalog/managed-root（R2-P1-02） | — |
| Core 侧 read-only 标志 | grep `read_only` 与 `READ_ONLY`（`src/**/*.py`） | `dfa70c002` | 仅 `connection.open_readonly`；无 Host 模式通道 | — |
| 批事务 seam 兼容性 | 读 `src/application/editing/ports.py:74-92`、`src/infrastructure/sqlite/regions.py:288-313` | `dfa70c002` | 支持 expected current + 整批回滚；无 lock/digest 参数（R2-P2-09） | — |
| receipt/apply 规则冲突 | 读卡 `:84-85`、`:92`、`:131`、`:142`、`:176` | `dfa70c002` | stale-first 与同 token 同 revisionId 不能同时成立（R2-P1-04） | — |
| manual 位分歧 | 读 `service.py:127-133`、`:1334-1341`；`entities.py:138-139`、`:187-189`；C-13 `:173`/`:181` | `dfa70c002` | unlock 场景下 digest（manual_edited）不变（R2-P1-05） | — |
| Windows 目录 fsync | 本机 `python -c`：`os.open(dir)+os.fsync` | win32 | FAIL（`PermissionError`） | 证明 R-JOURNAL-2 的 `fsync 目录` 需 ctypes 或降级（R2-P2-07） |
| 既有文件发布模式 | 读 `src/infrastructure/filesystem/managed_storage.py:98-124` | `dfa70c002` | 现有模式 = 文件 fsync + `os.replace`（无目录 fsync） | — |
| `assemble_production_core` 数据根 | 读 `core_service.py:744`、`:5764`；`core_assembly.py:1414` | `dfa70c002` | data_root 已在装配内可用，`core_service.py` 改动非必需（R2-P2-02） | — |
| FOLLOW-UP 登记 | grep `FOLLOW-UP-FEA03`（`doc/**`） | `dfa70c002` | 仅卡内 `:64`、`:67` 两处；未进 checkpoint/ADJ（R2-P2-02） | — |
| 运行 pytest / dotnet test | — | — | **NOT_RUN** | 无实现可测；范围冻结阶段 |
| 崩溃/并发/journal 实测 | — | — | **NOT_RUN** | 无实现 |
| C-04b/C-08/C-01b/C-05 正文逐字节复核 | — | — | **NOT_RUN** | 非本卡写域，只读冻结记录与交叉引用 |

---

## 5. 边界声明、结论与复审

**边界声明**

- 本 Review 只审范围冻结 v2（被审 head `dfa70c002`），不评价实现、不构成实现验收，也不构成 Task 释放或集成结论。
- 未修改任何被审文件；未 commit、未 push；只新增本报告。未访问用户数据。
- `check.ps1`/`verify_pins.ps1` 的 PASS 是机械结果，不替代契约语义或范围判定（本轮再次给出 PASS 下仍存在的治理漂移）。

**结论**

**`changes_requested`（P0 × 1 / P1 × 5 / P2 × 12）。不写 `approved`。**

v2 对 r1 的处置是**实质性**的：写域补齐（P1-01）、BRIDGE 收窄（P1-04）、SC-D02/D06/D10/D03 覆盖、AC13 基线、交付项映射、reviewer/Appointment、禁止范围等都已落地，r1 的 19 条中有 12 条 closed、6 条 partial、1 条 open。但仍有 1 条 P0 与 5 条 P1：

1. **P0-01**：SC-D11 冻结语义仍未走 UNFREEZE（Q-6 仅卡内登记），AC11 已冻结偏离语义；V19 两种顺序期望未写。
2. **P1-01**：receipt 单文件/崩溃窗口/保留期/摘要比对未自洽（P1-03 残留）。
3. **P1-02**：R-JOURNAL-4 只读/单写者无输入通道、无 AC/V（P1-02 残留）。
4. **P1-03**：AC12 无 V 行，closeout “覆盖全部 AC” 不实（P1-06 残留）。
5. **P1-04**：R-APPLY-2 与 R-RECEIPT-2/AC4/AC15 直接冲突（v2 新引入）。
6. **P1-05**：Q-9 的 manual 位选择存在保护变化漏检（v2 新引入）。

**建议最小闭环顺序**

1. 先做 `CONTRACT-UNFREEZE-C13`（SC-D11 适用范围）→ 独立复核 → 重冻/更新 pin；或改回 SC-D11 字面（需同时 UNFREEZE C073，代价更大）。把 Q-6 与两个 FOLLOW-UP 登记到 checkpoint/ADJ。
2. 修 R-APPLY-2 优先级（receipt 命中先于 stale）；补 AC4/AC15/V20 的“重放时 base 已变”场景。
3. 修 receipt：按序多记录/两阶段 + 崩溃窗口 fallback（内容摘要回查 revision 历史）+ 保留期/清理；补 AC15/V20 用例。
4. 修 R-JOURNAL-4：定义 Core 只读标志来源（assembly/测试注入；生产 FEA-04 接线 deferral）与第二写者机制；补 AC/V（只读、第二写者、并发 flush）。
5. 修 Q-9：digest 纳入 text 人工锁位（或两个 bit），补 AC10/V17 unlock 场景；更新对应 FOLLOW-UP/UNFREEZE 载体。
6. 补 AC12 的 V22（.NET 测试）与“CORE 真实执行面 = assemble_production_core 对象图”的声明；更新 closeout。
7. 清 P2：PLAN 行版本、`approval`/follow-up 登记、`core_service.py` 写权收窄、`tests/core` 写权、Q-10 措辞、崩溃注入机制、Windows 目录 fsync、`rg` 命令、AC13 基线范围、保护检查位置、C-13 `:94` deferral、AC2 层级。
8. 修订后以新 head 提交，派 r3（可基于 diff 复审）；只有 P0/P1 清零才写 `approved`。

**复审口径**：r3 需逐条 disposition 本报告 P0/P1（fixed/deferred with owner/not applicable + 理由），并重新确认 `check.ps1`/`verify_pins.ps1` 与三条指针；实现复核（`doc/reviews/FEA-03-r1.md`）不在本报告范围。

---

*Reviewer：`fea03-scope-reviewer`（DSH Agent Teams durable teammate，fresh 独立上下文，由 Team Lead `lead` 派发；未参与 FEA-03 的起草/实现/v1/v2 范围冻结）。日期：2026-11-01。*
