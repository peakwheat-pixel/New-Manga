---
id: UI-WORKBENCH-READER-1
title: S4 工作台画布/区域编辑 + 沉浸式阅读器（含 webtoon 接线）
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-26_ad002_autonomy
suggested_owner: zcode
owner: null
reviewer: dsh
depends_on: [UI-SHELL-THEME-1]
base_commit: 657d36817
branch: task/UI-WORKBENCH-READER-1
worktree: G:/CODEX/New Manga.workspace/worktrees/UI-WORKBENCH-READER-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/UI-WORKBENCH-READER-1
allowed_paths:
  - doc/tasks/UI-WORKBENCH-READER-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/UI-WORKBENCH-READER-1/**
  - G:/CODEX/New Manga.workspace/task-envs/UI-WORKBENCH-READER-1/**
  - G:/CODEX/New Manga.workspace/worktrees/UI-WORKBENCH-READER-1/**
---

# UI-WORKBENCH-READER-1：S4 工作台 + 阅读器

## 目标

AD-002 §4；DISPLAY-PERF 决策书 G2–G5；S3 已完成主窗/主题/书架。目标：工作台画布与区域编辑可用，阅读器满足性能门槛（含 webtoon 长条虚拟化），并把 region/reader/Run/Export 相关 NS 命令分批接线。

## Acceptance Criteria

- [ ] **AC1 工作台**：三栏 IA（左 300 翻译设置 + 按色族分组动作栈、中画布控制条 + 缩放 50–200%、右 230 缩略图）；画布 tile 渲染（BitmapInterpolationMode=None）；区域选择/编辑与气泡检查器（编辑态深色 chrome，参考规格）；命令接线（region/reader 相关 NS 子集，列清单）。
- [ ] **AC2 阅读器**：沉浸式阅读（无边框、隐藏 UI、Esc 退出）；fit/1:1/适应宽切换；**横向利用率 ≥90%**；翻页首帧 ≤120ms；键盘/滚轮/点击热区。
- [ ] **AC3 webtoon**：长条虚拟化（4000×60000，tile 4000×2048 设备光栅）；滚动 **p95 ≤20ms**、0 掉帧、内存 ≤1.5GB；DPR2 下 400% 等效像素锐利（无插值模糊）。
- [ ] **AC4 排版显示**：竖排/横排 Core 渲染图 **1:1 像素**显示（禁插值），禁则样例 0 违例。
- [ ] **AC5 门禁**：`scripts/test.ps1` 全绿（含 headless UI + 性能脚本）；旧壳 vitest 60/567 不变；pytest 相对基线无新增失败；`check.ps1 -TaskPath` PASS；证据 64-hex pin。
- [ ] **AC6 交接**：Handoff + Record Decision（渲染服务设计、NS 接线批次、性能测量方法）。

## 允许修改范围

`apps/desktop-avalonia/**`、本卡、STATUS/PLAN/LEDGER 指针、`verification/UI-WORKBENCH-READER-1/**`、workspace。只读：`ui-spec/**`、`doc/AD-002*`、`doc/design/ADR-*`、`verification/DISPLAY-PERF-DECISION-1/**`。

## 禁止范围

不改旧壳/Core/AD；不 push；不 1:1 复刻；字体仅系统栈；不 gc/prune；不得改 S3 主题契约（只消费）。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | headless UI + 真 sidecar 数据 | sidecar 无标签副本 | NOT_RUN | 待填 |
| AC2/AC3 | 长条夹具（4000×60000）+ 滚动计时 + 内存 | DPR2、Win11 | NOT_RUN | 待填 |
| AC4 | 竖排样例 1:1 像素比对 | Core 渲染图 | NOT_RUN | 待填 |
| AC5 | `scripts/test.ps1` + vitest + pytest 基线 | 全量 | NOT_RUN | 待填 |

## 依赖、风险与阻塞

- 依赖：UI-SHELL-THEME-1（done）。
- 风险 1：tile 渲染与 DPI/滚动虚拟化边界；风险 2：NS 命令未接线导致区域编辑不可用（列清单先接线最小集）；风险 3：性能门槛需真实夹具与可复跑脚本。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/UI-WORKBENCH-READER-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/UI-WORKBENCH-READER-1 | 待填 | 待关闭时核 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
