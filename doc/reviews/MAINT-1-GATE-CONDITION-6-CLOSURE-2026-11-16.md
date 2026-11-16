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
- **预算**：PLAN 由 6990 B 压到 **6972 B / 64 行**（留 28 B 余量回应 P2-5「零余量」）。压缩只落在**冗余措辞**上：
  子卡描述（拖拽排序 / 偏好落库 / E-1 断言口径）、重复的 `delivery` 字样、一处日期后缀与 `明细` 二字；
  **status / limitation / NOT_RUN / 根因 等披露性字样一律保留** —— 初版曾连带删掉 4 处（`AC3 limitation`、`根因 UNKNOWN`、
  `仅部分证据`、`NOT_RUN 见卡面`）与 2 个 `done`，经独立复核 P1-2 指出后**已全部恢复**（见 §6）。
  同时修掉一处既有精度缺陷：`SIDECAR-REBUILD-1` 行原写 `done`，其卡与台账均为 `in_progress`，已改为 `in_progress`。
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

- **冻结交付 head**：`45af570079eeaa57bb731e766caa82a480e7d0cd` —— 载体、登记与精度修复的最终**内容**提交。其后的提交只追加
  `verification/**` 证据与卡面登记字段（`delivery_head` / 三口径行），零源码、零测试、零契约、零 pin 字节。
- **工作区状态**：四件套启动时 `git status --porcelain` 为空（clean）。
- **时点**：`2026-11-16T07:25:49Z` 起（四项快速门禁）→ `2026-11-16T07:34:28Z`（.NET 全量结束）。
- **原始日志**：`verification/MAINT-1-RELEASE-MONITOR/condition6-closeout/gates.log`（含 `# head:` / `# at_utc:` /
  `# command:` 头与逐步 `EXIT=`，未删改）。

| # | 命令 | EXIT | 判定行（原文） |
|---:|---|---:|---|
| 1 | `pwsh -NoProfile -File tools/governance/check.ps1` | 0 | `Governance check: PASS (3 warnings)` |
| 2 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/MAINT-1-RELEASE-MONITOR.md` | 0 | `Governance check: PASS (3 warnings)` |
| 3 | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 0 | `PIN AUDIT: PASS (all 18)` |
| 4 | `python -B tools/generate_api_inventory.py --check` | 0 | `OK: rendered counts match FEA-C07 doc`（`1/80/6 = 87`） |
| 5 | `pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1` | 0 | `TEST PASS (Debug): 1591/1639 passed, 48 skipped` |

逐项目（.NET，取自 `gates.log` 的「已通过/失败/跳过/总计」行）：CoreClient **258/0/0**、Host **364/0/44**、App **969/0/4**。

**与旧记录的关系（不做绿洗）**：

- 2026-11-16 的 `RELEASE-GATE-SIX-CONDITIONS` §6.3 记录的是 `1582/1630`（App 962/0/4），本 head 为 `1591/1639`
  （App 969/0/4）：通过数 +9、失败 0、`skipped` 仍 **48**（未新增 skip），总计 +9 来自这期间合入的测试。
- 3 条 warning 与基线同量：非终态 Task 13 个（r38 不得据此批量关闭）、STATUS 3174 B、PLAN 6960 B 均达预算 80%。
- **未放宽任何断言、未改任何阈值、未删任何用例**：四件套命令与 `check.ps1` 内的预算/规则一字未动（本卡只改文档与证据）。

**测试副作用（已处置）**：`ImmersiveReaderVisualEvidenceTests` 每次全量测试都会重写
`verification/READER-OVERLAY-HEADLESS-PNG-1/render-info.md`。本轮在提交前用
`git checkout 6a408e5aa -- <该文件>` 恢复基线字节，`git diff 6a408e5aa -- <该文件>` 为空（净零改动）。

## 5. 结论与边界

1. 条件 6 的四个「Agent 可做」剩余动作已闭环：载体、冻结 head、登记、三指针精度与 P1-1 处置。
2. **未强化任何判据**：只登记既有 Review 与既有 Errata，未新增断言、未放宽检查、未改绝对计数；四件套命令与阈值一字未动。
3. **Gate 总体仍 `BLOCKED`**：条件 3（阅读器 overlay 人眼目视）、条件 4（签名 + 真机安装矩阵）、
   条件 5（人工 GT 质量基线）仍开放，不因条件 6 关闭而改变。
4. **独立性**：本报告由实施方 DSH 撰写；结论另由**上下文独立**的子 agent 在冻结 head 上复核，报告落 `doc/reviews/`，
   由 DSH 以 Lead 名义采纳（2026-10-31 口径：独立 = 上下文独立）。

## 6. 独立复核（上下文独立子 agent）与 findings 处置

- 复核者：`c6-reviewer`（DSH 派发的新上下文子 agent，**未参与实施**，只读；按 2026-10-31 口径「独立 = 上下文独立」）。
- 报告：`doc/reviews/MAINT-1-GATE-CONDITION-6-CLOSURE-REVIEW-2026-11-16.md`。
- **verdict：`APPROVED_WITH_FINDINGS`**：7 项复核项 5 PASS / 2 FAIL，**P0 = 0**，两项 P1 均为文档级。

| finding | 复核意见 | 本轮处置 |
|---|---|---|
| **P1-1** | 交付 head 与载体完成态错位：`45af57007` 上 frontmatter 四字段仍 `null/pending`、`EV-C6-*` 尚不存在，载体实际在 `b18a2ef90` 完成 | **已处置**：`integration_commit` 改为 `b18a2ef90`（载体完成提交），`delivery_head` 明确为「四件套实测所在树」`45af57007`；卡面 Closeout 新增「回填顺序」段（提交无法自证 ⇒ 逐代登记），并引用复核者在 `b18a2ef90` 上的独立复跑结果 |
| **P1-2** | PLAN 压缩删除了披露性字样（`根因 UNKNOWN` / `仅部分证据` / `AC3 limitation` / `NOT_RUN 见卡面`）与 2 个 `done`，与「语义未变」的表述不符 | **已处置**：4 处披露字样 + 2 个 `done` **全部恢复**；§2 措辞改为如实列出只压缩冗余措辞，并登记初版误删与恢复过程 |
| P2-a | EOL 前提：fresh checkout 下 PLAN/STATUS 会因 CRLF 超出预算（`git checkout` 写 CRLF） | **登记（不修）**：属仓库级 `.gitattributes` 议题，不在本卡授权内；写入 `NEXT-SESSION-STARTER` 队列 3 与陷阱区。本轮所有 doc 均为 LF，预算实测通过 = 6972/3200… 见 §4 |
| P2-b | `gates.log` 的 `started_utc` 与 .NET `elapsed` 相差约 55 s（两项之间的切换开销） | **登记**：以 `finished_utc` + `elapsed=461 s` 为准，`started_utc` 为约值 |
| P2-c | `render-info.md` 的测试副作用曾在 `45af57007` 被提交 | **已处置**：`3cc4e1186` 恢复为 `6a408e5aa` 基线字节；`git diff 6a408e5aa HEAD -- verification/READER-OVERLAY-HEADLESS-PNG-1/` 为空 |
| P2-d | Closeout 里「NEXT-SESSION-STARTER 已更新」在载体提交上不成立 | **已处置**：改为「在本轮收尾提交中更新」 |
| P2-e | 报告写 CoreClient `256`，日志实为 `258` | **已处置**：§4 改为 258/0/0 |
| P2-f | 指向 `GATE4-MODEL-RECOVERED-1` 的 Canonical Evidence 属悬空引用 | **已处置**：卡面 Manifest 改为指向证据目录 `verification/GATE4-MODEL-RECOVERED-1/` |
| P2-g | PLAN `SIDECAR-REBUILD-1` 行写 `done`，其卡与台账为 `in_progress` | **已处置**：改为 `in_progress`（见 §2） |

- **未处置项口径**：P2-a 需 `.gitattributes` 级改动（改变全仓 checkout 行为），不在本卡授权与风险预算内 ⇒ 如实登记为下一轮前置债，
  **不**通过放宽预算或改 `check.ps1` 掩盖。
- **结论不变**：条件 6 成立；Gate 总体仍 `BLOCKED`（条件 3/4/5 开放）。

## 7. 采纳声明

本报告由 DSH 以 Lead / Integrator 名义采纳，采纳依据 = `c6-reviewer` 的 `APPROVED_WITH_FINDINGS`（P0=0）+ 上述 P1 全部处置 +
P2 逐条处置/登记。复核者未参与实施，满足「上下文独立」口径。
