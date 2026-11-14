---
id: MAINT-1-RELEASE-MONITOR
title: 项目计划收口后的维护与 Release Gate 监测
kind: governance
governance_version: 3
status: in_progress
resume_status: in_progress
approval: user_authorized_2026-11-14 (所有任务交 DSH、自动裁决/规划、全部授权、无需用户介入)
suggested_owner: DSH
owner: DSH
reviewer: "DSH auto-adjudication (2026-11-14 owner directive); independent sub-agent review optional"
depends_on: [PUBLISH-FIX-1]
base_commit: ef5881ffe
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/MAINT-1-RELEASE-MONITOR
allowed_paths:
  - verification/MAINT-1-RELEASE-MONITOR/**
  - doc/tasks/MAINT-1-RELEASE-MONITOR.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/reviews/MAINT-1-*.md
  - tools/governance/task_ledger.py
  - doc/tasks/CHAPTER-SELECTOR-1.md
  - doc/tasks/FEA-11-HOST-AUTH-4.md
  - doc/tasks/FEA-11-L-S1-B2-ROOTS-AVAILABILITY-1.md
  - doc/tasks/FEA-06-RESIDUAL-4.md
  - doc/tasks/FEA-11-HOST-AUTH-5.md
---

# MAINT-1-RELEASE-MONITOR：项目计划收口后的维护与 Release Gate 监测

## 来源与目标

NEW-MANGA-V1-FULL-AUDIT 与 R1–R4 整改、SEC-01/02/03、CORE-01、AUDIT-07/09/12/14、REL-GATE-1、PUBLISH-FIX-1 已全部收口；`doc/REBASELINE_PLAN.md` 的 DAG 节点均 done/closed。本 Task 是**长期维护节点**：记录项目计划收口状态、V1 承诺清单、Release Gate BLOCKED 的事实与边界，并在用户提供 clean install / 模型 API / 安装验证条件后重新评估 Gate；不改变任何产品结论。

## Acceptance Criteria

- [x] **AC1**：维护记录：DAG 收口状态、V1 承诺清单与 Release Gate BLOCKED 的当前依据（引用 STATUS/13_GATE/V1_COMMITMENT_MANIFEST）。 <<MET>>
- [x] **AC2**：监测规则：四项治理门禁保持 EXIT 0；任何 Task/证据变更后复跑并保存原始输出。 <<MET>>
- [x] **AC3**：重新评估入口：若获得 clean install / 真实模型 API / 安装验证条件，按 13_RELEASE_GATE 要求复评；未获得时保持 BLOCKED，不写成 PASS。 <<MET>>
- [x] **AC4**：不得以本 Task 扩大产品范围或改写历史证据；维护记录按需更新。 <<MET>>

## 允许修改范围

- `verification/MAINT-1-RELEASE-MONITOR/**`
- 本 Task 卡、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`
- `doc/reviews/MAINT-1-*.md`、`tools/governance/task_ledger.py`

## 禁止范围

产品源码、契约、依赖、真实用户数据、远端写操作、安装/发布、历史改写。

## 测试要求

无产品测试；维护检查以四项治理门禁与原始证据为准。

## 维护记录（append-only）

### 轮次 1（2026-11-14）

- **P0 治理一致性**：E-1…E-4 见 [errata](../reviews/MAINT-1-P0-ERRATA-2026-11-14.md)。PLAN 补 READY/表外节点声明；TASK_LEDGER 重生成并补算术说明；STATUS 时效修正；REL-GATE-1 AC2 只登记不改历史字节。
- **门禁**：`check.ps1` PASS（3 warnings）；`verify_pins` 18/18 PASS；4 张非终态卡的分卡检查由 FAIL 转 PASS。
- **AC1 进度**：已记录 DAG 收口状态、V1 承诺清单指针与 Release Gate BLOCKED 依据。
- **下一步（P1）**：`.NET` 全量 127 failed 逐项归因，红基线不得当作绿通过。

### 轮次 2（2026-11-14）

- **P1 归因完成**：127 failed 逐条按首帧归因 → 93 `SetSecurityInfo`（ACL）+ 31 仓库根发现（三处 `.git` 向上查找）+ 3 `RemoveDirectoryRecursive`，**0 条产品断言回归**。
- **复跑**：真实仓库 App.Tests 889/0/11、Host.Tests 321/0/74；全量 8 项目 Release **1875 passed / 0 failed / 109 skipped，`EXIT=0`**（高于登记基线 1804/0/107）。
- **证据**：[归因记录](../../verification/MAINT-1-RELEASE-MONITOR/P1-DOTNET-BASELINE-ATTRIBUTION.md) 与 `logs/dotnet-*.log`。
- **未翻转状态**：`FEA-15-ACCEPT-1` 仍 `closed_with_limitations`；解冻须 P3 独立 Review + 显式关闭记录。
- **下一轮（P2）**：可见 UI 冒烟（`--data-root/--theme-home/--page/--exit-after`，隔离数据根，四页留进程+截图+EXIT）。

### 轮次 3（2026-11-14）

- **P2 达成**：四页（bookshelf / workbench / reader / settings）在双根隔离下各自起进程，窗口分别于 1582 / 1570 / 1535 / 1532 ms 出现，`PrintWindow` 截图 28–60 KB，`exit=0`，`host.log` 落地；真实 `%APPDATA%\com.newmanga.desktop` 前后零变化 → `P2_SMOKE PASS`。
- **证据**：[P2 记录](../../verification/MAINT-1-RELEASE-MONITOR/P2-UI-SMOKE.md)、`tools/p2-ui-smoke.ps1`、`logs/p2-ui-smoke.log`、`tools/ui-smoke/p2-ui-smoke.json` 与四张 `page-*.png`。
- **目视判读**：资料库空态（0/0 作品、导入入口）与设置中心 9 分区两图人工确认；`04 模型与设备` 显示「待接入」，与模型 API NOT_RUN 一致，界面未假装已接入。
- **未翻转状态**：`REL-GATE-1`、`FEA-15-ACCEPT-1` 均 `closed_with_limitations`，未改一字、未改状态；解冻留待 P3 独立 Review。
- **会话教训（写死）**：`Start-Process` 在本会话无限阻塞、`CopyFromScreen` 无交互桌面时阻塞、`Start-Job` 受命名管道限制挂死；改用 `Process.Start(UseShellExecute=false)` + `PrintWindow`。
- **下一轮（P3）**：9 个 `closed_with_limitations` 节点逐项分类（C1 工程闭环 / C2 契约对齐 / C3 设计选择 / C4 硬件）并处置。

### 轮次 4（2026-11-14）

- **P3 分类完成**：[triage 记录](../reviews/MAINT-1-P3-LIMITATION-TRIAGE.md)。9 个节点拆出 C1 约 13 项、C2 5 项、C3 7 项、C4 10 项，另有 2 项已由本循环 P1/P2 解决。
- **一处自我更正**：A3-1「日志路径写真实 %APPDATA%」原先被我判定为 C1 真实缺陷；核对源码 `MainWindow.axaml.cs:1041-1047` 后确认 `ResolveDiagnosticsRoot` 是**有意**的发行默认（显式 `--log-dir` 时全部重定向，未传时保留每用户位置），故降级为 C3/C1 边界并转入 Q5 双签。P2 冒烟同时传了 `--log-dir`，所以未触发该路径，与 A3-1 现象一致。
- **双签队列（6 项）**：Q1 name 规范化、Q2 position 形状、Q3 FONT-2 拆分与字体授权、Q4 READ P12/P15 偏差、Q5 日志根是否跟随数据根、Q6 pytest 16F 修或永久登记。
- **未翻转状态**：9 个节点全部保持 `closed_with_limitations`。
- **下一轮（P3-a）**：把两处 `TaskPath FAIL`（`FEA-06-PREREQ-1` 13 errors、`CHAPTER-SELECTOR-1` 6 errors）作为首批 C1 治理卡修复。

### 轮次 5（2026-11-14）

- **`CHAPTER-SELECTOR-1` 转绿**：5 个 AC 补 `<<MET>>` 行末标记（结论早已写在正文，仅补机器可读格式）；Resource Manifest 的 `sha256/manifest` 列改为真实索引 `verification/CHAPTER-SELECTOR-1/live-evidence.json`，原长描述**迁入**结果列未删。`check.ps1 -TaskPath` → **PASS**；diff 6 增 6 删。
- **`FEA-06-PREREQ-1` 仅诊断不改**：[诊断记录](../reviews/MAINT-1-P3A-TASKPATH-DIAGNOSIS.md)。13 个错误分四类，其中 4 条证据 SHA 漂移属 pin 基准策略议题，须独立成卡重钉；本轮取 O2（登记债），不重钉、不改历史 AC 语义。
- **允许路径扩展**：本卡 `allowed_paths` 增加 `doc/tasks/CHAPTER-SELECTOR-1.md`（本轮实际改动前已补登）。
- **单卡 FAIL 清单**：2 张 → 1 张（仅剩 `FEA-06-PREREQ-1`）。
- **未翻转节点状态**：无。
- **下一轮（P4）**：4 张 FEA proposed 卡逐张处置（释放或裁 OUT）。

### 轮次 6（2026-11-14）

- **P4 处置**：[P4 记录](../reviews/MAINT-1-P4-PROPOSED-DISPOSITION.md)。
  - `FEA-11-HOST-AUTH-4` → **OUT / `cancelled`**（承接项全是测试/健壮性观测，无产品可见变化，原 limitation 与 Review P3 原样保留）。
  - `FEA-11-L-S1-B2-ROOTS-AVAILABILITY-1` → **OUT / `cancelled`**（C-16 v1.5 字段已冻结但**无消费者**，契约字段不删，可撤销）。
  - `FEA-06-RESIDUAL-4`（查看对照）→ **待 Q7 双签**（实现需 C-07 additive UNFREEZE + API inventory，且 Current V2 亦无此功能）。
  - `FEA-11-HOST-AUTH-5`（HostRuntime 全链路 e2e）→ **待 Q8 双签**（仓内无 register→…→ACK 全链路用例，属验收强度取舍）。
- **DoD §2 未满足**：仍有 2 张 `proposed`，必须完成双签后终裁。
- **状态翻转**：2 张 `proposed` → `cancelled`（依据裁决记录先落盘，符合红线 4「先证据后状态」）。
- **下一轮（P4-a）**：派 Codex 与 ZCode 各出一份 Q7/Q8 独立书面建议。

### 轮次 7（2026-11-14）

- **Q7/Q8 意见收集**：[Codex 原字节](../reviews/MAINT-1-P4A-codex-advice-2026-11-14.md)（`gpt-6-luna` xhigh，会话 `01a1d658…`，`EXIT=0`）；**ZCode 服务不可用**（三项环境变量齐全仍 `Select a model` + `ERA_NEGOTIATION_FAILED`，最小探测 `EXIT=1`），按 skill 不自行升权、不改桌面端配置，第二意见改由独立上下文子 agent 代行并登记偏差。
- **本地核实纠正两处前提**（Codex 读不到本地 HEAD，只能读远端快照）：
  - Q8 卡面「仓内无全链路用例」**不准确**：`Fea11Residual4AIpcTests.cs` 已走 `HostRuntime.StartAsync`(:725) + `source_resync`(:139) + 断言 `acknowledged`(:173-174)；但它 **opt-in**（`NEWMANGA_FEA11_IPC=1`）且**未断言 fresh ACK**（全文无 `fresh`）。
  - Q7 前提成立：`RegionSummary` 无冲突字段（`CoreServiceClient.cs:204-210`）；`list_page_region_texts` 已注册（`HostCommandRegistry.cs:191/357/465`）但 `IHostController` 无对应方法。
- **DSH 终裁意向**：Q7 → `OUT`（不提供查看对照）；Q8 → `OUT`（不新建全链路卡），改为"补 fresh ACK 断言"的测试补强项。
- **状态未翻转**：两张 `proposed` 卡保持原状，待第二意见回来后落状态（矩阵要求收齐两份）。
- **下一轮（P4-b）**：收第二意见 → 终裁 → 翻转两卡状态 → 更新台账与三指针。

### 轮次 8（2026-11-14）

- **双签收齐**：[裁决记录](../reviews/MAINT-1-P4A-Q7-Q8-ADJUDICATION.md)；[Codex 原字节](../reviews/MAINT-1-P4A-codex-advice-2026-11-14.md)；[第二意见整理版](../reviews/MAINT-1-P4A-independent-advice-2026-11-14.md)（ZCode 不可用，独立子 agent 代行并登记偏差）。
- **无实质冲突**：Q7、Q8 均判 `OUT`；第二意见在治理口径上更保守（要求写清"放弃冻结设计意图"的性质、要求先更正假前提），已全部采纳。
- **Q7 `FEA-06-RESIDUAL-4` → `cancelled`**：性质＝**冻结设计意图的产品可见缩减**（`06-page-workbench.md:50`、`09-state-matrix.md:14`；AC3 PARTIAL；原裁决是 re-home 非 waive），已写清用户可见后果（只能看横幅+typed 原因，不能并排比对）与 3 条重开条件；未写成"已实现/无缺口"。
- **Q8 `FEA-11-HOST-AUTH-5` → `cancelled`**：登记 4 条事实（默认套件无全链路 e2e / opt-in 已执行且有日志 / fresh-ACK 只在直连 gated 用例 / 打包 sidecar `NOT_RUN`），明确 **AC-F4 不得写成 MET**。
- **两处卡面前提更正（Errata，append-only）**：「仓内无全链路用例」为假、「需 HostOptions seam」为假；真实根因是打包 sidecar 早于 C-17。同步更正 P4 处置文档 §2。
- **台账**：`non-terminal` 8 → 6；**FEA 范围内 `proposed` 清零 → DoD §2 达成**。
- **门禁**：check 默认 + 三张分卡 PASS；pins 18/18。
- **下一轮（P5）**：MAINT-1 自身 AC1–AC4 收口。

### 轮次 9（2026-11-14）

- **P5 AC1–AC4 达成**：[维护记录](../../verification/MAINT-1-RELEASE-MONITOR/MAINTENANCE-RECORD.md) 为正本；门禁原始输出 `logs/gates-2026-11-14.log`（7,374 B，四项全 `EXIT=0`）。
- **AC 状态**：AC1–AC4 全部标 `<<MET>>`；任务**保持 `in_progress`**，待 P6 收官核对三指针后再置终态——不在 C1 待办未处置时提前关闭维护哨位。
- **AC4 自证**：未扩大产品范围（4 张提案全 OUT）、未改历史字节（更正一律 errata/独立 review）、未覆盖任何 pin（`FEA-06-PREREQ-1` 的 4 条 SHA 漂移保持 FAIL）。
- **下一轮（P6）**：三指针一致性核对 + 四项门禁复跑 + 收官报告。

### 轮次 10（2026-11-14）

- **P6 收官核对完成**：[判定报告](../reviews/MAINT-1-P6-LINE-CLOSEOUT-VERDICT.md)。**判定：线未收口（DoD 5 条中 §1、§3 未达成）**，不构成完成声明。
- **三指针一致（DoD §5 达成）**：`STATUS:6-7`、`PLAN:58`、`TASK_LEDGER`（`non-terminal 6` / `named 5`）互相吻合。
- **DoD §2 达成**、**§4 有条件达成**（check/pins/api-inventory/.NET 全绿；pytest 16F 为登记基线内未清零）。
- **结构性阻塞已定位并给出解法**：PLAN 64/64 行、6954/7000 B；新开实现卡会超预算 → 下轮以 `MAINT-2-*` 登记并把 ID 并入既有表外行（+约 35 B，预算内）。
- **未翻转任何节点状态**；Release Gate 保持 BLOCKED，未写成 PASS。
- **下一轮（P7）**：释放 `MAINT-2-C1-BATCH-1` 承载价值最高的 3–4 项 C1。

### 轮次 11（2026-11-14）

- **队列调整（依据依赖，非跳步）**：先做 **C4 waiver 载体**再做 C1 实现卡。理由：DoD §1/§3 要求"显式 waiver 裁决"，而 waiver 是纯文档、可立即验证；C1 实现需派外部 Agent + 独立 Review，成本高且受本会话预算约束。调整已在此登记。
- **C4 waiver 载体落盘**：[MAINT-1-C4-WAIVER-CARRIER-2026-11-14.md](../reviews/MAINT-1-C4-WAIVER-CARRIER-2026-11-14.md)，共 W1–W10 十项，逐项写明 `NOT_APPLICABLE` 原因与保留的 `NOT_RUN` 证据路径。
- **防误判复核**：载体 §1 明确登记三处曾差点误判的项（`FEA-07` "无硬件"措辞、`FEA-15-A3-1` 日志根降级为 C3、`FEA-11` folder relink 属 C1），确保没有把工程可闭环项塞进 C4。
- **不改变 DoD 判定**：C1（约 13）/C2（5）/C3（7）仍开放，故 DoD §1/§3 仍未达成。
- **下一轮（P8）**：C3 设计选择类 OUT 载体；若预算允许则并行释放 C1 首卡。

### 轮次 12（2026-11-14）

- **P8 C3 OUT 载体落盘**：[MAINT-1-C3-OUT-CARRIER-2026-11-14.md](../reviews/MAINT-1-C3-OUT-CARRIER-2026-11-14.md)，C3 共 6 项逐条 OUT（AI-1 DDL 版本、EDIT-1 position 形状/批量分页/孤儿行、FONT-2 范围、A3-1 日志根），每项带用户可见后果与重开条件。
- **§3 排除项**：明确登记 5 项不属 C3 的项（FEA-11 folder relink=C1、RESIDUAL-2 Tab/a11y=C1、FEA-07 AC1/AC2=C1、A3-1 硬编码说法不成立、术语冲突为无关项），防止把可做的工作误分类为设计选择。
- **limitation 处置进度**：C4 10 项（轮次 11）+ C3 6 项（本轮）已有正式载体；**C1 约 13、C2 5、Q6 仍开放**，DoD §1/§3 未达成。
- **下一轮（P9）**：Q6（pytest 16F 修 or 永久登记）裁决；并评估是否释放 C1 首卡（受会话预算约束）。

### 轮次 13（2026-11-14）

- **P9 Q6 裁决完成**：[Q6 裁决](../reviews/MAINT-1-P9-Q6-PYTEST-ADJUDICATION.md)。16 个 pytest 失败**全部集中在插件沙箱子系统**，复跑 `tests/infrastructure/test_plugin_sandbox.py` → **16 passed / 26.23s**，与验收 16 failed 数目精确吻合 → 裁决为**环境性失败、非产品缺陷**，不开修复卡。
- **限制登记**：仅复跑该文件，全量 pytest 复跑列入下一轮；复跑环境 `python`+`pytest 9.1.1` 与验收 `C:\Python314`（无 pytest）不同，差异本身即环境证据。
- **DoD §4**：`.NET` 1875/0/109 已实测；pytest 16F 已归因；仍需一次全量复跑给出同环境干净数字，故 §4 仍为「有条件达成」。
- **下一轮（P10）**：全量 pytest 复跑 + 更新 V1 清单数字；随后评估 C1 首卡。

### 轮次 14（2026-11-14）

- **全量 pytest 复跑完成**：`1 failed, 3536 passed, 10 skipped`（292 s）。相对验收基线 `16 failed / 3515 passed`，16 个沙箱失败未复现，Q6 归因结论再次得到支持。
- **唯一失败未归因**：`test_real_v7_import_fixture_degrades_then_pixel_matches_on_generation_two`（依赖 `workspace/FEA-11/fixtures` 真实 fixture），未逐行定位，**不得写全绿**。
- **DoD §4**：仍为「有条件达成」。
- **下一轮（P11）**：定位该用例；随后评估 C1 首卡（受会话预算限制，可能需要新会话续跑）。

### 轮次 15（2026-11-14）

- **唯一失败已定位**：`sqlite3.OperationalError: no such column: custom_rank`（`planner.py:94` → `library.py:235`）。v7 旧库 fixture 缺 `custom_rank` 列，属 schema 演进与旧 fixture 的版本缺口（LIB-1 侧新增），**非已迁移库的运行时回归**。
- **处置**：不开产品修复卡；登记为测试支撑缺口，路线 (a) 修 fixture / (b) 仓储容错 留待裁决。
- **DoD §4**：失败已归因未消除，仍不写全绿。
- **会话预算**：已近上限，下一轮建议新会话按 `CHECKPOINT.md` 续跑。

### 轮次 16（2026-11-14）

- **P11 裁决完成**：[custom_rank 裁决](../reviews/MAINT-1-P11-CUSTOM-RANK-ADJUDICATION.md)。源码 `schema.py:930-932` 证实生产路径有 v12 迁移，故取**路线 (a) 修 fixture**，不改产品代码/契约；路线 (b) 仓储容错会弱化 SELECT 列清单。
- **下一会话派发**：Owner Codex，范围仅 `tests/fea11/test_source_scan.py` 的 fixture 建库逻辑；验收＝该用例通过 + 全量 pytest 0 failed + 门禁不降。
- **DoD §4**：用例通过前仍为「有条件达成」。
- **会话预算**：已到上限，后续按 `CHECKPOINT.md` 新会话续跑。

### 轮次 17（2026-11-14）

- **修复点精确定位**：`tests/fea11/test_source_match.py:1028` 用 `migrations[:7]` 把库停在 v7，而下游 planner → `library.py:217` 需要 v12 的 `custom_rank`。**结论修正**：不是"fixture 缺一列"，而是该用例的**迁移时序与该用例声称的终态版本不一致**，不能靠加列修。
- **未擅自改测**：该用例意图（v7 生产迁移 + 真实导入 → v8）需先读懂再动；已写成可执行的移交单（4 步，含验收与独立 Review 要求）。
- **DoD §4**：仍「有条件达成」。
- **会话预算**：已到上限，后续按 CHECKPOINT 新会话续跑。

### 轮次 18–19（2026-11-14，前一会话）

- **18**：终局定位——同一用例 `:1028` 停 v7 与 `:1085` 全量迁移的时序冲突，失败发生在 v7 阶段误用当前 schema 数据访问路径（`_CHAPTER_COLUMNS` 含 v12 的 `custom_rank`）；结论修正为"迁移时序与终态版本不一致"，非缺列。
- **19**：**会话上下文耗尽终止**（非 DoD 达成、非用户中断、非轮次上限），HEAD `67de32919`；CHECKPOINT 已登记续跑顺序。
- **状态**：未翻转任何节点；DoD §4 仍「有条件达成」。

### 轮次 20（2026-11-14）

- **可执行修复提案落盘**（`MAINT-1-P11-CUSTOM-RANK-ADJUDICATION.md` 末节）：把 `:1085` 的全量迁移提前到 `:1048` 的仓储构造之前；**未实施**（前一会话上下文不足）。HEAD `89547e366`。

### 轮次 21（2026-11-14，本会话）

- **用户新指令**：「继续 FEA 线收口，且重开卡走 C-07 UNFREEZE 路线」→ **撤销 Q7 `OUT`**，`FEA-06-RESIDUAL-4` 由 `cancelled` → `proposed`。
- **裁决落盘**：[RO-1](../reviews/MAINT-1-RO-1-REOPEN-RESIDUAL-4-2026-11-14.md)：路线＝规格冻结 → C-07 additive UNFREEZE（`ListPageRegionTextsAsync`，79→80 / 86→87，独立 byte-level 复核 + 重冻 + pin 重算）→ 端口/UI/测试 → 独立 Review。
- **拆卡**：`FEA-06-RESIDUAL-4A`（契约前置）、`FEA-06-RESIDUAL-4B`（实现）；两卡均须独立 scope review 后才 `ready`。
- **保留**：Q7 的 OUT 审计链、Codex 原字节、独立第二意见**原样保留**；`FEA-06` AC3 仍 **PARTIAL**。
- **DoD §2 回退**：`proposed` 0 → 1（用户主动重新纳入），P6 §2 的「达成」在 RO-1 完成前**不得再引用**。
- **并行**：派 Codex（`gpt-6-luna` xhigh，`workspace-write`）执行 `custom_rank` fixture 修复，使 DoD §4 转达成；结果待回。
- **下一轮（RO-2）**：释放 4A（scope review + PLAN 预算登记 + UNFREEZE 载体）；收 Codex 结果并复跑全量 pytest。

### 轮次 22（2026-11-14，本会话续）

- **`custom_rank` 已修，DoD §4 转「达成」**：Codex 首轮 `BLOCKED`（未改文件，理由是「提前迁移会改变 v7 导入语义」）；DSH 实证推翻——提前迁移后用例 `1 passed`、legacy 形状断言全部保持；全文件 20 passed；**全量 `3537 passed / 0 failed / 10 skipped`（316s）**。实施细节见 [P11 裁决 · 实施与实证节](../reviews/MAINT-1-P11-CUSTOM-RANK-ADJUDICATION.md)。
- **环境澄清**：Codex 报 `Python314 无 pytest` 是其沙箱限制；该解释器实测有 `pytest 9.1.1`。后续 pytest 类验证由 DSH 代跑。
- **4A 已交付**：`FEA-06-RESIDUAL-4A`（契约前置）由 DSH 派出的实施 Agent 完成并提交 `7c1ac472f`；C-07 pin **v1.8 `8ccaba05…` → v1.9 `91e51ab7…`**；inventory 正式成员表与统计保持 **79/86 = 代码实测**（新增「RO-1 计划追加（v1.9 预授权）」节锁死 `ListPageRegionTextsAsync` / `Task<RegionPageTextProjection?>` / 落地行 `#80`），翻转 80/87 留给 4B；载体 §6 复核记录 `pending`。
- **偏差登记（RO-1 裁决与实际的一致性）**：RO-1 §3 R2 原写「79→80 / 86→87」，在 4A 内不可达（生成器解析源码、`--check` 为子串判定、`apps/**` 不在 4A 写域）；按 v1.2 PREQ 先例改为「4A 计划追加 + pin v1.9；4B 翻转 80/87 + pin v1.10」。
- **门禁**：check 默认 + 两卡 `TaskPath` PASS；pins **18/18**（C07 新值）；`generate_api_inventory --check` EXIT 0；成员表逐行 = stdout（`ALL_MATCH=True`）。
- **未翻转**：9 个 `closed_with_limitations` 全部保持；`FEA-06` AC3 仍 PARTIAL；`FEA-06-RESIDUAL-4A` 仍 `proposed`（PLAN 无行余量）。
- **下一轮（RO-3）**：派独立上下文对 4A 做 byte-level 复核（重点：v1.9 差异范围、新 typed 码 `REGION_TEXT_PROJECTION_UNAVAILABLE`、pin 的 CRLF 可复现性、Banner 单 action 布局依据）；复核 approved 后追写载体 §6 与 §1B 并重冻，再释放 4B。

### 轮次 23（2026-11-14，本会话续）—— limitation 处置矩阵

- **产出**：[limitation 处置矩阵](../reviews/MAINT-1-LIMITATION-DISPOSITION-MATRIX-2026-11-14.md)（39 项，9 个 `closed_with_limitations` 节点全覆盖；每项含 `L-<节点>-<n>` 编号 + 处置码 + 证据指针）。
- **处置分布**：`C3` 10 / `WAIVER` 10 / `IMPL` 8 / `C2` 4 / `SOLVED` 3 / `KEEP` 2 / `UNCERTAIN` 2。
- **DSH 终裁**（append 于载体）：① 接受「`closed_with_limitations` + 载体 ≡ done+waiver」**作为 DSH 解释口径**（明写不是既有裁决）；② C2 五项全 OUT；③ AI-1 两项 C3 重分类接受但加**硬重开条件**；④ `FEA-06-PREREQ-1` 13 errors 的 OUT 仅在「单卡 TaskPath 红不计入 DoD §4」前提下成立，且须在判定报告显式披露；⑤ **C1 的 8 项 `IMPL` 是待办，DoD §3 未达成**。
- **DoD 影响**：§1 由「未达成」转为「有载体 + 待口径确认」；§3 仍**未达成**（8 项实现待落）。
- **副产物**：`FEA-15-ACCEPT-1` 的 pytest 16F 与 .NET 127F **均已解**（3537/0/0、1875/0/109）；`CHAPTER-SELECTOR-1` 已转绿。
- **下一轮**：释放 `MAINT-2-C1-BATCH-1` 承载 8 项 C1 实现（PLAN 已腾出 45B）。