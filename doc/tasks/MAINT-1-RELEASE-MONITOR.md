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
integration_commit: b18a2ef90
delivery_head: 45af57007
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/MAINT-1-RELEASE-MONITOR
allowed_paths:
  - verification/MAINT-1-RELEASE-MONITOR/**
  - doc/tasks/MAINT-1-RELEASE-MONITOR.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/reviews/MAINT-1-*.md
  - doc/reviews/RELEASE-GATE-SIX-CONDITIONS-2026-11-16.md
  - audit/V1-FULL-AUDIT/reports/13_RELEASE_GATE.md
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

### 轮次 24（2026-11-14，本会话续）—— FEA 线 DoD v2 达成

- **判定报告**：[`MAINT-1-FEA-LINE-CLOSEOUT-v2-2026-11-14.md`](../reviews/MAINT-1-FEA-LINE-CLOSEOUT-v2-2026-11-14.md)（取代 P6 判定结论；P6 原字节保留）。
- **DoD 五条全部达成**：§1（9 节点 × 39 项 limitation 处置矩阵 + DSH「closed_with_limitations + 载体 ≡ done+waiver」口径）、§2（FEA proposed 清零）、§3（C1 8 项全实现 + r1 approved + P2 处置）、§4（pytest 3544/0/10、.NET 三项目 0 failed、四门禁绿）、§5（三指针一致）。
- **用户指令交付**：「查看对照」重开 → 4A 契约（C-07 v1.9）→ 4B 实现（v1.10 冻结、pin `498882eb…`）→ 独立复核 approved → 两子卡 done、父卡 superseded。
- **MAINT-2 收口**：`closed_with_limitations`（AC8 PARTIAL 按裁切口径），P2-3 已修。
- **保留限制 5 条**（不得读作已验收）：无像素视觉证据、gated 集成缺口、AC8 基线不可比、单卡 TaskPath 红 1 张、M2-C1 无 pin 体系。
- **线外**：Release Gate 仍 BLOCKED，不计入 DoD、不得写 PASS。
- 本维护哨位保持 `in_progress`（Gate 复评入口仍开放）。

### 轮次 25（2026-11-14，本会话续）—— 用户要求的三项后续

- **① 目视确认「查看对照」：完成**。新增 opt-in 截图测试渲染真实冲突帧与展开后面板（`verification/FEA-06-RESIDUAL-4B/visuals/`）；DSH 逐项目视核对：横幅保留「重读草稿」、其下独立「查看对照」入口、面板「区域文本对照」纵向双栏、上栏 `基底译文`/`user`/`edited`、下栏 `draft text`/`detect`/`本地草稿`、唯一按钮「关闭」、检查器 19 键未混入面板本地码。
- **② 像素级验收：完成并落库**。口径沿用 `FluentResidual3VisualEvidenceTests`——**像素是签署证据、不作 AC 判据**；默认零写入，仅 `NEWMANGA_CAPTURE_FEA06_COMPARE_PNGS=1` 时产出。4B 的 R-12 limitation **关闭**；两张 PNG 已登记为 EV-8/EV-9。
- **③ Release Gate：仍 `BLOCKED`**。出具 [差距评估](../reviews/MAINT-1-RELEASE-GATE-ASSESSMENT-2026-11-14.md)：更新了已变的旧事实（pytest 16F→0F、FEA DoD v2、视觉证据），逐条列出六项解锁条件的现状；明确**本轮未生成任何 Windows 包、未做 clean install / 升级回退 / 卸载、未调用真实模型 API、未做远端可见性调查**。现存 `0.1.1` 安装包不绑定当前基线，不得当作证据。
- **可安全推进的两项**（后续会话）：条件 6 的独立最终 Review；条件 4 的前置——用 `tools/ci/publish-release.ps1` 在当前 HEAD 重新打包并跑 singlefile + `-Smoke`。
- 门禁：check PASS(3w)；pins 18/18；inventory --check EXIT 0；4B TaskPath PASS（EV-8/EV-9 已登记）。

### 轮次 26（2026-11-14，本会话续）—— 真实模型 API 调用已验

- 用户提供 API 凭据位置（`C:\Users\49745\DeskBox\杂项文件\api.txt`）。**凭据只按需从环境变量注入，未写入仓库任何文件、提交或日志。**
- 用产品自身 `OpenAiTranslationProvider` + `StdlibTransport` 对 DeepSeek 完成真实翻译：`deepseek-chat`、≈740ms、`valid_protocol=True`、`你好，你好吗？` / `轰`（SFX 文化等效）。
- 证据：`verification/MAINT-1-RELEASE-MONITOR/model-api-verification.log`（已核验无密钥）。
- **Gate 条件 5：未完成 → 部分**；其余条件未变，**Gate 仍 BLOCKED**。未做代表性质量基线（无人工 GT）与 App→Host→Core 完整 UI 端到端。

### 轮次 27（2026-11-14，本会话续）—— 第二条 provider 路径 + 端到端边界

- **视觉 OCR 路径已验**：产品 `VisionOcrProvider` + `StdlibTransport` → 智普 `glm-4v-flash`，渲染图 `こんにちは` 正确识别。证据 `vision-ocr-verification.log`。
- **qwen 视觉模型不可用**：`qwen3-max`/`qwen-vl-plus` HTTP 404、`qwen-vl-ocr` HTTP 403（同一 dashscope 端点）→ 第二条路径改用智普；验证目标是协议与适配器，不是厂商。
- **端到端不可达（产品缺口）**：`HostCommandRegistry` 只有 `save_manual_translation`，**无自动翻译命令**；UI 的 `Translate` 只是批处理动作枚举/阶段标签；设置页显示「模型与设备：待接入」。**这不是 API key 能解决的**，需独立功能卡。
- **Gate 条件 5 最终表述：部分**（两条路径已验；缺质量基线与 UI 端到端）；**Gate 仍 BLOCKED**。
- 两个证据日志均已核验无密钥。

### 轮次 28（2026-11-14，本会话续）—— 自动翻译可行性与契约面评估

- **评估报告**：[`MAINT-1-AUTO-TRANSLATE-FEASIBILITY-2026-11-14.md`](../reviews/MAINT-1-AUTO-TRANSLATE-FEASIBILITY-2026-11-14.md)（独立上下文调研，只读、38KB）。
- **结论：条件可行，零冻结契约改动 / 零 UNFREEZE / 零 pin 变更。** 运行链路（`StartRun(command=translate_*)` + `execute_translate_step` + pipeline executor）**已存在**。
- **真实缺口是配置桥，不是 wire**：G1 P15 profile/binding 从不镜像进 `settings["providers"]["profiles"]`（`runtime.py:182-193` vs `settings_commands.py:590-670`）；G2 `RunBindingDefaults.DefaultJson` 只注 `{"ocr":"manga-ocr"}`（可被 `NEWMANGA_RUN_PROVIDER_BINDINGS` 覆盖）；G3 `library_start_run` 对冻结 Core 曾 `INVALID_REQUEST`（遗留未定位）。
- **四卡拆分**：T-A 配置桥（Core，唯一必做新代码）→ T-B 运行路径收口（Host）→ T-C 入口与文案（App）；T-D 质量项可选。**明确排除**新 wire 命令与新 `IHostController` 成员。
- **失败模式已盘点**：403→`PROVIDER_AUTH_FAILED`（不可重试，qwen 已遇）；404 模型名与 402 无余额都落 `INVALID_INPUT`（**语义错位**）；429→`PROVIDER_RATE_LIMITED`；**无 token/成本计量**（账单风险）；配置变更需重启 Core。
- **DSH 补充（§10）**：既有 `REAL-TRANSLATE-PROVIDER-1` 已把装配链路跑通（`PROVIDER_NOT_CONFIGURED`=0，全部 429），**BLOCKED 仅因 key 无额度**；本机 DeepSeek key 已实测可用，故可**零代码重跑**换取「Core 侧端到端」证据（但无法证明 Host/UI 侧，因该探针走冻结 Core stdio 直连）。

### 轮次 29（2026-11-14，本会话续）—— Core 端到端重跑：尝试并**未成功**（如实记录）

- **做了什么**：复用 `run_translate_probe.py`，把旧 `REAL-TRANSLATE-PROVIDER-1` 隔离根的 profile 改为 DeepSeek（`api.deepseek.com/v1` + `deepseek-chat`），用 `cmdkey /generic` 写入与 Core `CRED_TYPE_GENERIC` 兼容的凭据，然后真跑 `StartRun translate_untranslated`。
- **结果**：`completed_with_failures`，8 target = **3 skipped + 5 failed（全部 `ocr / INVALID_INPUT`）**，**translate step 从未执行**。证据 `verification/MAINT-1-RELEASE-MONITOR/auto-translate-rerun/`。
- **为什么不算成功（三条，缺一不可）**：① 隔离根已被上次运行污染（`library.db` 已有 26 regions，非 0-region 初始态）；② sidecar 是 `0.1.1` 发布包，**不是**原验证用的 RELEASE-REPACK-2 models sidecar；③ 该 Task 报告本身写明「identity 回退运行另有 5 个 OCR `INVALID_INPUT`（region-less 页既有行为）」，本次同型，**不能归因于 DeepSeek 配置**。
- **结论修正**：「零代码重跑即可拿到 Core 端到端」的设想在当前工作区**不成立**。前置是「干净 fixture（8 页 / 0 regions）」+「含 OCR 模型的 sidecar（或改跑源码 Core）」，两者都不现成。
- **未变**：provider 层真实调用已验（翻译 + 视觉 OCR 两份日志）；Core→落库端到端**仍未验证**；Gate 仍 `BLOCKED`。

### 轮次 30（2026-11-14，本会话续）—— Gate 条件 6 独立最终复核

- **复核结论**：`MECHANICAL_PASS / CONDITION_6_NOT_CLOSABLE`（报告 [`MAINT-1-GATE-CONDITION-6-FINAL-REVIEW-2026-11-14.md`](../reviews/MAINT-1-GATE-CONDITION-6-FINAL-REVIEW-2026-11-14.md)；Gate 结论仍 `BLOCKED` 未改）。
- **实测通过**：四件套全绿；3 张卡 20 条 Canonical Evidence 的 path/sha256/`git cat-file -e` 三口径 **20/20**；limitation 矩阵 **9 节点 39 项、0 行缺处置码或指针**（`10/10/8/4/3/2/2=39` 自洽）；现行权威面 **0 处**把 `BLOCKED` 写成 PASS/CONDITIONAL。
- **P1-1 已处置**：收口判定报告 append-only errata，把 §3 的「达成」收窄为「8 项均已实现 + AC8 按裁切口径 PARTIAL + P2-3 已修」，明写**不等于 8/8 MET**；并解释与矩阵「补实现并 MET」的差异（AC8 基线不可比）。
- **P2 处置**：P2-3（MAINT-2 卡 `L-PB1-1`→`L-PB1-3`）已修；P2-4（4B「7 条 EV」→「9 条 EV」）已修；P2-2（PLAN 表外漏 `GIT-CLEAN-CORE-ENV-2` + `BLOCKED/REVIEW` 字面冲突）已修（`READY 节点` 声明恢复、`BLOCKED：无`）；P2-5（PLAN 零余量）已缓解为 **6995/7000**；P2-1（4B R-12 关闭后 Closeout 第 1 项仍按未关闭表述）登记为**历史记录 + 后附关闭记录并存**，不改历史字节。
- **仍未闭合（条件 6 的完成态缺口）**：① `MAINT-1` 交付 head 未冻结（`integration_commit`/`delivery_head` 为 null、`canonical_evidence_status=pending`，且卡内缺 Canonical Evidence 表 / Resource Manifest / Closeout Record）；② 复核期间 head 被并发提交推动；③ 本 Review 需在冻结 head 上登记。
- **计划**：待 `TRANS-BINDING-BRIDGE` 落地、head 稳定后，一次性补 MAINT-1 的 evidence/manifest/closeout 并冻结交付 head，在该 head 重跑四件套，再登记本 Review —— 届时条件 6 方可判「完成」。

### 轮次 31（2026-11-14，本会话续）—— Gate 条件 6 的交付头已冻结

- **交付头**：` d0ae50305 `（main，工作区 clean）。这是条件 6 要求的「当前交付 head」。
- **该 head 上的四件套实测**：`check.ps1` PASS(3w) / `verify_pins` 18/18 / `generate_api_inventory --check` EXIT 0（`1/80/6=87`）；pytest 同批实测 **3562/0/10**。
- **独立复核已登记**：[`MAINT-1-GATE-CONDITION-6-FINAL-REVIEW-2026-11-14.md`](../reviews/MAINT-1-GATE-CONDITION-6-FINAL-REVIEW-2026-11-14.md)（r 判 `MECHANICAL_PASS / CONDITION_6_NOT_CLOSABLE`，其四项缺口中的「交付 head 未冻结」「Review 未登记」由本节关闭；「复核期间 head 被推动」由本次冻结消除；「PLAN 枚举漏项」已在轮次 30 修复）。
- **条件 6 判定**：**机械部分 + 交付头冻结 + Review 登记三项齐备**，条件 6 可判完成。**Release Gate 仍 `BLOCKED`**（其余五项条件未变）。
- 本哨位保持 `in_progress`（Gate 复评入口开放），不因条件 6 完成而关闭。

### 轮次 32（2026-11-14，本会话续）—— L2 终局 BLOCKED（环境资源）

- **L2（Core 端到端翻译验证）按止损条件收口为 `BLOCKED`**，性质＝**环境资源缺失**（缺推理模型），**不改产品代码即可解决**，不影响产品可用性，只影响 Gate 条件 5 的措辞。
- 三条路线均无产出（book/detect 无 detect provider；region/blocked 无 error_code 的 planning 门；page/ocr 缺 ONNX 模型）；已排除 6 项假设。
- **解除条件**：D 提供 OCR ONNX 模型；或 E 配置远程视觉/OCR provider。
- **沉淀 5 条**（源码 Core 入口、fixture v6→v14 无损、**装配期 provider 约束**、region seed 产品 API 路径、证据目录）已写入路线文档，后续 T-C 与任何 Core 侧验证可直接复用。
- **转 T-C**：自动翻译的入口与错误文案（前置约束已攒 5 条，含本轮新增的「必须先写 `pipeline_defaults` 再启 Core」）。

### 轮次 33（2026-11-14，本会话续）—— Gate 条件 1 的 8 项 finding 已裁决

- **裁决文件**：[`MAINT-1-GATE-CONDITION-1-FINDING-ADJUDICATION-2026-11-14.md`](../reviews/MAINT-1-GATE-CONDITION-1-FINDING-ADJUDICATION-2026-11-14.md)。
- **分布**：`IMPL-NOW` 3（L-F1-2 / L-L1-4 / L-AI1-6）、`IMPL-CARD` 4（L-R1-1 / L-R2-1 / L-L1-1 / L-L1-2）、`KEEP-NOTRUN` 1（L-F1-3）、`OUT` 0。
- **数量差异已记录**：评估原文写「7 项」，矩阵现有 8 项（`L-AI1-6` 后续增补）；**以矩阵为准**，原文 append-only 不改。
- **诚实结论**：条件 1 从「未处置」→「已逐项裁决」，但 **0 项已关闭**（3 个 IMPL-NOW 尚未实现）⇒ **条件 1 仍未完成**；**Gate 仍 `BLOCKED`**。
- **执行顺序**：先做 3 个 IMPL-NOW（1–2 轮可关闭）；#1+#2 合并一张 UI 控件卡；#5 先出契约评估；#6 等用户裁排序语义；#4 留到发布前性能验收。

### 轮次 34（2026-11-14，本会话续）—— 条件 1：3/8 已关闭（矩阵滞后被发现）

- 复核发现裁决时判为 `IMPL-NOW` 的 3 项**早已完成**，矩阵未回流：
  - L-F1-2：`tests/core/test_font_wire.py:92-108`（wire 级负例，注释明标 `MAINT-2-C1-BATCH-1 AC2`）
  - L-L1-4：`service.py:28-33`/`:298` + `test_library_wire.py:172-186/191-200/214-250`
  - L-AI1-6：`src/**` 中 `reassign_references` 命中 0；`test_prompt_templates.py:221` 以 `not hasattr` 固定
- **条件 1 进度：0/8 → 3/8**；剩余 5 项（4 张卡 + 1 项 NOT_RUN）。**仍未完成，Gate 仍 BLOCKED**。
- **教训**：矩阵是处置快照，实施进展不会自动回流；条件类裁决依赖矩阵计数前必须核实现状态。

### 轮次 35（2026-11-14，本会话续）—— L2 路线 E 失败，性质升级为产品缺陷

- **路线 E（远程 GLM-4V 视觉 provider，绕开 ONNX）仍无产出**，但把失败精确定位：
  - `run.provider_binding_snapshot["ocr"]` 是**完整合法**的 replay 配置（`execution` 含 base_url/model/credential_ref/adapter_version/network_profile，`execution_digest` 合法）
  - 执行期仍 `ocr / PROVIDER_NOT_CONFIGURED`；**三种绑定形状**（用户 profile id、固定注册槽、固定槽+保留 translate）均复现
  - 新排除 5 项 ⇒ **不是配置形状问题**，是 **Core 侧 vision provider 的就绪/解析判定**缺陷
- **L2 最终：`BLOCKED`（Core 侧 vision provider 解析缺口）**；四次尝试（book/detect、region/planning 门、page/ocr 缺模型、page/远程视觉）全部穷尽
- **建议下一步**：开一张小诊断卡查 `src/infrastructure/providers/**` 的 vision OCR registry 就绪/解析路径（很可能属真实缺陷）；或回到 D（用户提供 ONNX 模型）
- **Gate 条件 5 维持「部分」**：两条 provider 路径已验；Core→落库未证明，且现在有明确的缺陷指向

### 轮次 36（2026-11-16，DSH R16）—— Gate 条件 6 收口：载体 / 登记 / 三指针精度 / P1-1

- **冻结交付 head + 四件套实测**：在本轮开工前的 clean head 上重跑四件套并留证（命令 / head / 时点 / EXIT 见
  `doc/reviews/MAINT-1-GATE-CONDITION-6-CLOSURE-2026-11-16.md` §5 与
  `verification/MAINT-1-RELEASE-MONITOR/condition6-closeout/gates.log`）。不再有「复核期间 head 被推动」的漂移：
  交付 head 以 frontmatter `delivery_head` 为唯一权威。
- **补载体**：本卡新增 `## Canonical Evidence`、`## Resource Manifest`、`## Closeout Record` 三节；frontmatter
  `integration_commit` / `delivery_head` / `canonical_evidence_status` / `resource_closeout_status` 已落值。
- **登记独立最终 Review**：`doc/reviews/MAINT-1-GATE-CONDITION-6-FINAL-REVIEW-2026-11-14.md`（182 行，引入
  `d38c624f7`，verdict `MECHANICAL_PASS / CONDITION_6_NOT_CLOSABLE`）已以 append-only 方式登记于本卡与
  `audit/V1-FULL-AUDIT/reports/13_RELEASE_GATE.md` 的条件 6 段。
- **§3.2-③（P2-2）重核后修复（非照抄）**：2026-11-16 的 PLAN 表外枚举列了 5 个节点，其中
  `AC-CHECKBOX-AUTHORITY-1` 已是终态，同时漏掉 5 张非终态卡（`DOC-CTRLCHAR-FIX-1`、`GATE3-MATRIX-EXPAND-1`、
  `GATE3-SETTINGS-SHORTCUT-1`、`INSTALLER-MATRIX-1` 均 `in_progress`，`FEA11-ENTRY-MISSING-1` 为 `blocked`），
  且 `BLOCKED：无` 与后者字面冲突。修后：`BLOCKED：FEA11-ENTRY-MISSING-1`，表外枚举含全部无 DAG 行的非终态卡
  （含 `GOV-DECLARATION-SCAN-CLEANUP-1`），13/13 张非终态卡 `-TaskPath` 由 5 FAIL 转全 PASS；
  PLAN 6960 B / 64 行（保留 40 B 余量，回应 P2-5 零余量）。证据：
  `verification/MAINT-1-RELEASE-MONITOR/condition6-closeout/p2-2-before-after.log`。
- **P1-1 重核与处置**：`doc/reviews/MAINT-1-FEA-LINE-CLOSEOUT-v2-2026-11-14.md` 的 Errata（`:58-66`，append-only）
  已把 DoD §3 收窄为「8 项均已实现 + AC8 按裁切口径 PARTIAL + r1 的 P2-3 已修」，明写**不等于 8/8 MET**。
  本轮另核两处重复口径：`doc/reviews/MAINT-1-FEA-POST-ROADMAP-2026-11-14.md:8` 与
  `verification/MAINT-2-C1-BATCH-1/README.md:5` 均未出现「8/8 MET」断言（后者原文即写 AC8 = PARTIAL），
  故**不改其字节**，仅在此登记指针；轮次 24 的历史记录按 Errata 读。
- **未翻转**：Release Gate 总体仍 `BLOCKED`（条件 3/4/5 开放）；本卡作为伞形哨位保持 `in_progress`。
- **冻结值与实测（回填）**：交付 head `45af57007`（四件套实测所在树）；证据提交 `3cc4e1186`；载体完成提交 `b18a2ef90`
  （= `integration_commit`）。四件套 EXIT 全 0（`check` PASS 3w / `pins` 18/18 / `inventory` `1/80/6=87` /
  `.NET` **1591/1639 passed, 48 skipped**：CoreClient 258/0/0、Host 364/0/44、App 969/0/4）。
  三口径（path 存在 / Git blob sha256 重算 / `git cat-file -e`）见
  `verification/MAINT-1-RELEASE-MONITOR/condition6-closeout/threeway.log`。

## Canonical Evidence

本卡是长期维护哨位（`in_progress`），下表是 Gate 条件 6 与既有 AC 的唯一当前证据。`BLOB` 口径 = 校验
`commit:path` 的 Git blob 原始字节（sha256 为该 blob 的 SHA-256，不是工作树字节）。逐条三口径复算
（路径存在 / sha256 重算 / `git cat-file -e`）由 `tools/governance/check.ps1 -TaskPath` 对 review/done 卡执行；
本卡停留 `in_progress`，故另以
`verification/MAINT-1-RELEASE-MONITOR/condition6-closeout/README.md` 记录手工复算结果。

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class | sha256_basis |
|---|---|---|---|---|---|---|
| EV-MR-1 | AC1–AC4 维护记录 | verification/MAINT-1-RELEASE-MONITOR/MAINTENANCE-RECORD.md | 6a408e5aa | 39c3ba2ef917705a20b52f4ba0a79e23f7cb93f047bb6f8bafae4b0ef7c91614 | CANONICAL | BLOB |
| EV-MR-2 | 条件 5 ① 真实 API 适配 | verification/MAINT-1-RELEASE-MONITOR/model-api-verification.log | 6a408e5aa | 120fe35b56222a7ef2229ecf8e6f27cb3684fe0e9a3cdc417b50dc3b1a30f38c | CANONICAL | BLOB |
| EV-MR-3 | 条件 6 独立最终 Review | doc/reviews/MAINT-1-GATE-CONDITION-6-FINAL-REVIEW-2026-11-14.md | 6a408e5aa | fd1c3d995c6bf11f0a2c47b9c3e4adaac5be0c7d554ec1e4f072f4c11d688613 | CANONICAL | BLOB |
| EV-MR-4 | P1-1 处置载体（Errata :58-66） | doc/reviews/MAINT-1-FEA-LINE-CLOSEOUT-v2-2026-11-14.md | 6a408e5aa | f7a5d0ad6cd664efd19259ab00a09d7a424a60b9ca5f3d7b066708411964d79a | CANONICAL | BLOB |
| EV-C6-1 | 条件 6-①② 四件套实测（冻结 head） | verification/MAINT-1-RELEASE-MONITOR/condition6-closeout/gates.log | 3cc4e1186 | eaf8c759b0ed132e02b3aa3650a406939bae60d925c82b595300c0be35a84b46 | CANONICAL | BLOB |
| EV-C6-2 | 条件 6-③ P2-2 前后实测 | verification/MAINT-1-RELEASE-MONITOR/condition6-closeout/p2-2-before-after.log | 3cc4e1186 | 63b093ed8b0f2ed6f52fce50064458e8d7e1231de4d018245131d98af75664f3 | CANONICAL | BLOB |
| EV-C6-3 | 资源核销（8 个 temp 数据根删除） | verification/MAINT-1-RELEASE-MONITOR/condition6-closeout/resource-closeout.log | 3cc4e1186 | e161401eca1c7e069c883b53a3ba7fbf8d729574b2d51bc4cb5de0d2885ac171 | CANONICAL | BLOB |
| EV-C6-4 | 条件 6 收口复评报告 | doc/reviews/MAINT-1-GATE-CONDITION-6-CLOSURE-2026-11-16.md | 3cc4e1186 | d983a652b9633547c96388d54259e78f21dbf2ccbeec391ae8410c061c28b79e | CANONICAL | BLOB |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | — | NOT_APPLICABLE | — | — | 无独立 worktree：全程在主线工作树 `G:/CODEX/New Manga`；`git worktree list` 无本卡专属条目 |
| task-env | G:/CODEX/New Manga.workspace/task-envs/HOST-CORECLIENT-1/sidecar-copy | PRESERVE_REFERENCED | — | 由 HOST-CORECLIENT-1 持有 | P2 UI 冒烟只读取该 sidecar，未改写；仍被 HOST-CORECLIENT-1 引用 ⇒ 不迁移 |
| temp | C:/Users/49745/AppData/Local/Temp/newmanga-p2-bookshelf-e2caedba | PRESERVE_UNKNOWN | — | 8 目录 / 1,523,132 B | 8 个隔离数据根已删除，逐项见 `condition6-closeout/resource-closeout.log`；删除后复查 0 残留 |
| artifact | apps/desktop-avalonia | DELETE_SAFE | — | — | `bin/obj` 构建产物可重建；不入库、不归档 |
| agent-output | — | NOT_APPLICABLE | — | — | 本卡未使用 `workspace/agent-output` |
| dataset/model | — | NOT_APPLICABLE | — | — | 本卡未复制、未删除模型权重；ONNX 权重证据在 `verification/GATE4-MODEL-RECOVERED-1/`（属该 Task 的证据目录，本卡只读引用） |

## Closeout Record

- Closeout date / DSH：2026-11-16 / DSH（R16）
- integration_commit：`b18a2ef90`（载体完成：frontmatter 落值 + EV-C6 行）｜delivery_head：`45af57007`（四件套实测所在树）｜证据提交：`3cc4e1186`
  · **回填顺序（提交无法自证，故逐代登记）**：`45af57007` 内容 + 四件套实测 → `3cc4e1186` 追加证据文件 → `b18a2ef90` 落本卡字段与三口径行。
    三者是同一交付的连续快照，任一提交都不可能在自己的树里写出自己的 hash；读者应以**本卡当前树**为权威载体、
    以 `45af57007` 为被测树。独立复核者已在 `b18a2ef90` 上亲跑 `check` / `-TaskPath` / `pins` / `inventory` 全 PASS（见复核报告 §1）。
- canonical_evidence_status：`complete`（条件 6 与 AC1–AC4 的当前证据见上表；`threeway.log` 三口径零 FAIL）
- resource_closeout_status：`complete`（见 Resource Manifest：无 worktree 操作；8 个 temp 数据根已删除并记为 `ALREADY_ABSENT`；其余为 PRESERVE_REFERENCED / DELETE_SAFE / NOT_APPLICABLE）
- 删除、迁移、归档数量/字节数：删除 8 目录 / 1,523,132 B（temp）；迁移 0；归档 0
- 未关闭项及保留原因：Release Gate 条件 3（阅读器 overlay 人眼目视）、条件 4（签名 + 真机安装矩阵）、条件 5（人工 GT 质量基线）仍开放，均非本卡可单方关闭；本卡作为伞形哨位保持 `in_progress`，不冒充 `done`
- 当前指针清理：STATUS / Plan / TASK_LEDGER 已更新至本轮；`NEXT-SESSION-STARTER` 在本轮收尾提交中更新（不晚于本提交之后的第一个提交）

## 2026-11-17 Gate 条件 3/4/5 的裁定登记（Codex Q3 + DSH 采纳）

来源：`doc/reviews/CODEX-RULING-CORE-ENV2-FEA11-GATE-2026-11-17.md` Q3 段（Codex 书面裁定；DSH 采纳）。
本 Task 保持 `in_progress`（长期维护节点），**不关闭**；下列为三条件的当前处置与下一步。

| 条件 | 当前处置 | 下一步（Agent 可推进） | 不可代理的部分 |
|---|---|---|---|
| **3｜阅读器 overlay 视觉** | **`PARTIAL_WINDOW_EVIDENCE`**（2026-11-17 推进）—— 已用发布产物在真实桌面会话抓到 **F11 全屏沉浸 overlay 截图** 与书架截图：证据 `verification/MAINT-1-RELEASE-MONITOR/condition3/`（`c3-01-library.png` / `c3-02-f11-immersive-empty.png`，sha256 见该目录 README）；**已可裁定**：全屏/无边框、控件四角布局、无裁切、无整幅遮挡；**仍缺**：选中页面后的 F11 截图（内容渲染/分页/Webtoon 布局/缩放未覆盖） | ① 交独立 Agent 对现有两张截图出**具名书面视觉裁定**；② 取得「选中页后的 F11 截图」后补做内容渲染裁定 | 真实窗口截图必须来自安装/运行产物；不得用 headless 冒充；不得因已有一张全屏截图就判条件 3 MET |
| **4｜签名 + 安装矩阵** | `INSTALLER-MATRIX-1` 已 `closed_with_limitations`（旧 sidecar 机制验证；AC7 NOT_RUN；无签名）；真实签名与跨版本矩阵由 **`RELEASE-GATE4-SIGNED-MATRIX-1`（proposed）** 承接 | 取得 Authenticode 证书与干净 Windows 环境后释放该卡；否则停在 AC1 并登记 `NOT_RUN` | 真实证书凭据、真实 Windows 环境 |
| **5｜人工 GT / 质量基线** | **`LIMITATION_ACCEPTED`** —— 按 Gate 原文允许的替代分支登记：**没有代表性质量基线，不宣称翻译/识别准确率达标**；实测基线仍 `NOT_RUN` | 若将来取得独立人工标注数据，须核代表性/来源/许可与固定哈希后再复评 | 独立人工 GT 数据本身 |

**边界**：
- 三条件的处置**不改变** `Technical Gate=NOT_SATISFIED`；Codex 唯一「需用户裁决」项是**是否把 Gate 总体改为 `SATISFIED`**，DSH 未改、也不代裁决。
- 不得把 `AGENT_ADJUDICATION_PENDING` 或 `LIMITATION_ACCEPTED` 表述为「条件已通过」。
- 条件 1（已关闭 8/8）、条件 2（调查完成）、条件 6（已关闭）状态不变。
