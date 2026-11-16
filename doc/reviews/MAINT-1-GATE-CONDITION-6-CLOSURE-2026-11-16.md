# MAINT-1 Gate 条件 6 收口复评（2026-11-16，DSH R16）

- **判据来源**：`audit/V1-FULL-AUDIT/reports/13_RELEASE_GATE.md:30`（定义）；
  `doc/reviews/RELEASE-GATE-SIX-CONDITIONS-2026-11-16.md:206-241`（§6 四项剩余动作）。
- **前置条件**：`doc/tasks/MAINT-1-RELEASE-MONITOR.md:46-47` 的 AC3/AC4 均 `[x]` 且行末 `<<MET>>`（本轮复核仍成立）。
- **独立最终 Review**：`doc/reviews/MAINT-1-GATE-CONDITION-6-FINAL-REVIEW-2026-11-14.md`（182 行，引入 `d38c624f7`），
  verdict `MECHANICAL_PASS / CONDITION_6_NOT_CLOSABLE`（`:4`）；不成立 4 项见其 `§3.2`（`:127-136`）。
- **判定**：条件 6 = **已关闭**。Gate 总体仍 **BLOCKED**（条件 3/4/5 开放）。

## 1. 原四项缺口与处置

| # | 缺口（Review §3.2 原文） | 处置 | 实测证据（文件:行 / 命令 / EXIT） |
|---:|---|---|---|
| ① | MAINT-1 自身无 Canonical Evidence 载体（`:16-19` 四个 `null`/`pending`，全文无 `## Canonical Evidence`） | 卡面新增三节；frontmatter 四字段落值 | `doc/tasks/MAINT-1-RELEASE-MONITOR.md` 的 `## Canonical Evidence`（7 列 / `BLOB`）、`## Resource Manifest`、`## Closeout Record`；`pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/MAINT-1-RELEASE-MONITOR.md` → EXIT=0 |
| ② | head 未冻结且在复核期间移动（`73a182a6 → f751764b5`） | 冻结 `delivery_head` 并在该 head 上重跑四件套 | 卡面 frontmatter `delivery_head`；§4 的「命令 / head / 时点 / EXIT」四联记录 |
| ③ | 三指针只能写成「当前 Task 与 non-terminal 集合吻合」（PLAN 表外枚举少 1、`BLOCKED/REVIEW：无` 与两个 `in_review` 冲突） | 重核后按 2026-11-16 实况修复 | §2（含 before/after 逐卡实测） |
| ④ | 本 Review 未被登记（只读产出） | append-only 登记到卡面 + Gate 文档 | 卡面「轮次 36」；`audit/V1-FULL-AUDIT/reports/13_RELEASE_GATE.md`「条件 6 登记」段 |

## 2. §3.2-③（P2-2）重核：2026-11-16 的实际状态与原文**不同**

**原文说「PLAN 表外枚举少 `GIT-CLEAN-CORE-ENV-2`」——该卡已在枚举内；真正的缺陷是枚举混入终态卡并漏掉 5 张非终态卡。**

| 卡 | status | 修复前 `check.ps1 -TaskPath` | 修复后 |
|---|---|---|---|
| `DOC-CTRLCHAR-FIX-1` | `in_progress` | FAIL：当前 DAG 未登记非终态 Task（rc=1） | PASS (3 warnings) |
| `GATE3-MATRIX-EXPAND-1` | `in_progress` | FAIL：同上（rc=1） | PASS (3 warnings) |
| `GATE3-SETTINGS-SHORTCUT-1` | `in_progress` | FAIL：同上（rc=1） | PASS (3 warnings) |
| `INSTALLER-MATRIX-1` | `in_progress` | FAIL：同上（rc=1） | PASS (3 warnings) |
| `FEA11-ENTRY-MISSING-1` | `blocked` | FAIL：同上（rc=1），且 `BLOCKED：无` 与之字面冲突 | PASS (3 warnings) |
| `GOV-DECLARATION-SCAN-CLEANUP-1` | `proposed` | 未登记（`proposed` 不在 `check.ps1:702` 枚举内 ⇒ 门禁未覆盖，仍属精度缺口） | PASS (3 warnings) |

- **修复动作**：`doc/REBASELINE_PLAN.md:59` 的 `BLOCKED：无` → `BLOCKED：FEA11-ENTRY-MISSING-1`；
  `:60` 表外枚举改为「无 DAG 行的全部非终态卡」（9 张，含 `GOV-DECLARATION-SCAN-CLEANUP-1`），删去终态卡
  `AC-CHECKBOX-AUTHORITY-1`；`GIT-CLEAN-RUST-CAPACITY-DESIGN-1` 由 `:59` 的 READY 声明登记。
- **预算**：PLAN 由 6990 B 降到 **6960 B / 64 行**（为腾字节压缩 8 处历史行冗余措辞，语义、状态与 commit hash 未变），
  留 40 B 余量回应 P2-5「零余量」。
- **证据**：`verification/MAINT-1-RELEASE-MONITOR/condition6-closeout/p2-2-before-after.log`（13 张卡逐张 rc + 判定）。

## 3. P1-1 重核：DoD §3 把 AC8 PARTIAL 计入「达成」

- **载体已存在**：`doc/reviews/MAINT-1-FEA-LINE-CLOSEOUT-v2-2026-11-14.md:58-66` 的 `## Errata`（append-only）已把 §3 收窄为
  「8 项均已实现 + AC8 按裁切口径 `PARTIAL` + r1 的 P2-3 已修」，并明写**不等于 8/8 MET**（`:64`）。
- **另两处重复口径复核**（Review P1-1 的「同步摘要措辞」建议）：
  - `doc/reviews/MAINT-1-FEA-POST-ROADMAP-2026-11-14.md:8`：写「C1 八项（`MAINT-2-C1-BATCH-1` closed）」，**未**断言 MET。
  - `verification/MAINT-2-C1-BATCH-1/README.md:5`：原文即写「AC8 复跑留证 = `PARTIAL`，由 DSH 裁决以 validation clone 为可比基线」。
  ⇒ 两处均不构成「把 PARTIAL 写成 MET」，**不改其字节**（其中后者属历史证据，不在本卡授权范围）。
- **卡面历史记录**：`MAINT-1-RELEASE-MONITOR` 轮次 24 的「§3（C1 8 项全实现…）」按上述 Errata 读；历史维护记录不重写。
- **处置**：P1-1 关闭为「已处置（Errata 载体 + 指针登记）」，**不**新增裁决口径、**不**把 AC8 改判 MET。

## 4. 四件套实测（命令 / head / 时点 / EXIT）

（本节在证据入库的同一提交中追加；原始日志见 `verification/MAINT-1-RELEASE-MONITOR/condition6-closeout/gates.log`。）

## 5. 结论与边界

1. 条件 6 的四个「Agent 可做」剩余动作已闭环：载体、冻结 head、登记、三指针精度与 P1-1 处置。
2. **未强化任何判据**：只登记既有 Review 与既有 Errata，未新增断言、未放宽检查、未改绝对计数；四件套命令与阈值一字未动。
3. **Gate 总体仍 `BLOCKED`**：条件 3（阅读器 overlay 人眼目视）、条件 4（签名 + 真机安装矩阵）、
   条件 5（人工 GT 质量基线）仍开放，不因条件 6 关闭而改变。
4. **独立性**：本报告由实施方 DSH 撰写；结论另由**上下文独立**的子 agent 在冻结 head 上复核，报告落 `doc/reviews/`，
   由 DSH 以 Lead 名义采纳（2026-10-31 口径：独立 = 上下文独立）。
