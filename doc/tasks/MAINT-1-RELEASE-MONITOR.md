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
---

# MAINT-1-RELEASE-MONITOR：项目计划收口后的维护与 Release Gate 监测

## 来源与目标

NEW-MANGA-V1-FULL-AUDIT 与 R1–R4 整改、SEC-01/02/03、CORE-01、AUDIT-07/09/12/14、REL-GATE-1、PUBLISH-FIX-1 已全部收口；`doc/REBASELINE_PLAN.md` 的 DAG 节点均 done/closed。本 Task 是**长期维护节点**：记录项目计划收口状态、V1 承诺清单、Release Gate BLOCKED 的事实与边界，并在用户提供 clean install / 模型 API / 安装验证条件后重新评估 Gate；不改变任何产品结论。

## Acceptance Criteria

- [ ] **AC1**：维护记录：DAG 收口状态、V1 承诺清单与 Release Gate BLOCKED 的当前依据（引用 STATUS/13_GATE/V1_COMMITMENT_MANIFEST）。
- [ ] **AC2**：监测规则：四项治理门禁保持 EXIT 0；任何 Task/证据变更后复跑并保存原始输出。
- [ ] **AC3**：重新评估入口：若获得 clean install / 真实模型 API / 安装验证条件，按 13_RELEASE_GATE 要求复评；未获得时保持 BLOCKED，不写成 PASS。
- [ ] **AC4**：不得以本 Task 扩大产品范围或改写历史证据；维护记录按需更新。

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
