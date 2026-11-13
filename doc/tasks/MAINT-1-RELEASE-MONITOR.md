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
