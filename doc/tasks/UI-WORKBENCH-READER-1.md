---
id: UI-WORKBENCH-READER-1
title: S4 工作台画布/区域编辑 + 沉浸式阅读器（含 webtoon 接线）
kind: implementation
governance_version: 3
status: in_review
approval: user_authorized_2026-10-26_ad002_autonomy
suggested_owner: zcode
owner: avalonia-spike
reviewer: dsh
depends_on: [UI-SHELL-THEME-1]
base_commit: 657d36817
branch: task/UI-WORKBENCH-READER-1
worktree: G:/CODEX/New Manga.workspace/worktrees/UI-WORKBENCH-READER-1
integration_commit: null
delivery_head: c8772697beb589b27ce9ba40c14bc65310a24087
canonical_evidence_status: pinned
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

- [x] **AC1 工作台**：三栏 IA（左 300 翻译设置 + 按色族分组动作栈、中画布控制条 + 缩放 50–200%、右 230 缩略图）；画布 tile 渲染（BitmapInterpolationMode=None）；区域选择/编辑与气泡检查器（编辑态深色 chrome，参考规格）；命令接线（region/reader 相关 NS 子集，列清单）。 <<MET>>
- [x] **AC2 阅读器**：沉浸式阅读（无边框、隐藏 UI、Esc 退出）；fit/1:1/适应宽切换；**横向利用率 ≥90%**；翻页首帧 ≤120ms；键盘/滚轮/点击热区。 <<MET>>
- [x] **AC3 webtoon**：长条虚拟化（4000×60000，tile 4000×2048 设备光栅）；滚动 **p95 ≤20ms**、0 掉帧、内存 ≤1.5GB；DPR2 下 400% 等效像素锐利（无插值模糊）。 <<MET>>
- [x] **AC4 排版显示**：竖排/横排 Core 渲染图 **1:1 像素**显示（禁插值），禁则样例 0 违例。 <<MET>>
- [x] **AC5 门禁**：`scripts/test.ps1` 全绿（含 headless UI + 性能脚本）；旧壳 vitest 60/567 不变；pytest 相对基线无新增失败；`check.ps1 -TaskPath` PASS；证据 64-hex pin。 <<MET>>
- [x] **AC6 交接**：Handoff + Record Decision（渲染服务设计、NS 接线批次、性能测量方法）。 <<MET>>

## 允许修改范围

`apps/desktop-avalonia/**`、本卡、STATUS/PLAN/LEDGER 指针、`verification/UI-WORKBENCH-READER-1/**`、workspace。只读：`ui-spec/**`、`doc/AD-002*`、`doc/design/ADR-*`、`verification/DISPLAY-PERF-DECISION-1/**`。

## 禁止范围

不改旧壳/Core/AD；不 push；不 1:1 复刻；字体仅系统栈；不 gc/prune；不得改 S3 主题契约（只消费）。

## 测试要求

| 场景/AC | 命令/步骤 | 结果 | 证据 |
|---|---|---|---|
| AC1 | headless WorkbenchPage：三栏 300/230、缩放宽 50/200、区域增删移改、气泡检查器 | PASS | E3 |
| AC2 | 阅读器 fit-width 利用率 + 6 次翻页首帧 + 沉浸窗口（无边框/Esc/H/F/键鼠热区） | PASS：**利用率 0.99**、**翻页 p95 1.05ms** | E1/E2 |
| AC3 | S0 长条夹具 4000×60000/30 tiles；60 次滚动计时；DPR2+400%；内存核算 | PASS：**滚动 p95 0ms**、解码 98.3MB ≤1.5GB、整数像素锐利 | E4/E5 |
| AC4 | 竖排 1200×1800 / 横排 1800×1200 1:1 渲染 | PASS：DisplaySize 精确相等、Stretch=None、无插值 | E6 |
| AC5/AC6 | `scripts/test.ps1`、vitest、pytest、check.ps1 | PASS：dotnet **84/84**；vitest 60/567；pytest 3F/2687P/9S=基线 | E7–E13 |
## 依赖、风险与阻塞

- 依赖：UI-SHELL-THEME-1（done）。
- 风险 1：tile 渲染与 DPI/滚动虚拟化边界；风险 2：NS 命令未接线导致区域编辑不可用（列清单先接线最小集）；风险 3：性能门槛需真实夹具与可复跑脚本。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| E1-fit-utilization | AC2 | verification/UI-WORKBENCH-READER-1/performance/fit.json | c8772697beb589b27ce9ba40c14bc65310a24087 | d0d1eee723ad39ac837403de6569a2aa32434ab8c348a32d370a3d26e76db017 | CANONICAL |
| E2-page-turn | AC2 | verification/UI-WORKBENCH-READER-1/performance/page-turn.json | c8772697beb589b27ce9ba40c14bc65310a24087 | bfedddb524407bd5695385b82b2380aea54cb4551b2cc276ec8b416058d781f4 | CANONICAL |
| E3-workbench | AC1 | verification/UI-WORKBENCH-READER-1/commands/wiring.json | c8772697beb589b27ce9ba40c14bc65310a24087 | 1b5a31590d0c993533d4912df6587689b15ed658631ce70e39badeae4f1bc1d8 | CANONICAL |
| E4-webtoon | AC3 | verification/UI-WORKBENCH-READER-1/performance/webtoon.json | c8772697beb589b27ce9ba40c14bc65310a24087 | 888ec0f0007d3cef9d2bfa173969861ca7c4211f53b15a01028bedf60b29d4b6 | CANONICAL |
| E5-fixtures | AC3/AC4 | verification/UI-WORKBENCH-READER-1/performance/fixtures.json | c8772697beb589b27ce9ba40c14bc65310a24087 | d8f51120dea7b872a63700eaca7ae25505780b238db50919b067603b2dd3c557 | CANONICAL |
| E6-one-to-one | AC4 | verification/UI-WORKBENCH-READER-1/performance/one-to-one.json | c8772697beb589b27ce9ba40c14bc65310a24087 | 34b49b321f9b03d777cfcffe1de65268e22b2c927eedb8137ceee00581cd8607 | CANONICAL |
| E7-test-log | AC5 | verification/UI-WORKBENCH-READER-1/test/dotnet-test-Debug.log | c8772697beb589b27ce9ba40c14bc65310a24087 | 68dcc6bfd8201decb2fa9a225285944bae473e423e36eeaf353158bb106b4cc7 | CANONICAL |
| E8-test-summary | AC5 | verification/UI-WORKBENCH-READER-1/test/summary.json | c8772697beb589b27ce9ba40c14bc65310a24087 | 73310245320c32b70e83b31cdb3ffe907fa69274959067e0ceb172f9e8fff1fb | CANONICAL |
| E9-trx-app | AC1–AC5 | verification/UI-WORKBENCH-READER-1/test/results-app.trx | c8772697beb589b27ce9ba40c14bc65310a24087 | 66c5a12f43a1e5bf962f9f4d4f6418c7313bfaf92c31d1a7f359be06b3d4a18e | CANONICAL |
| E10-vitest | AC5 | verification/UI-WORKBENCH-READER-1/test/vitest-baseline.log | c8772697beb589b27ce9ba40c14bc65310a24087 | a822b83f595acc9b9baea098e35b4452cc8b3bb5edd75b3d19d2ddcee13a5e57 | CANONICAL |
| E11-pytest | AC5 | verification/UI-WORKBENCH-READER-1/test/pytest-baseline.log | c8772697beb589b27ce9ba40c14bc65310a24087 | 57599fbe92baccaa6b0c6c8a2bb4dedcdefb655424115164637626ec1e1250a6 | CANONICAL |
| E12-build | AC5 | verification/UI-WORKBENCH-READER-1/build/dotnet-build-Debug.log | c8772697beb589b27ce9ba40c14bc65310a24087 | 97c1442796182fd5eaeaf0f6cc64e884e1b3eda2ba9d21e2736afabb0a368052 | CANONICAL |
| E13-manifest | 全 AC | verification/UI-WORKBENCH-READER-1/MANIFEST.json | c8772697beb589b27ce9ba40c14bc65310a24087 | a020e9a99d524dae0ee9e8b5223e554a05f65372902a536c41717a66ac7785d5 | CANONICAL |
## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/UI-WORKBENCH-READER-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/UI-WORKBENCH-READER-1 | a020e9a99d524dae0ee9e8b5223e554a05f65372902a536c41717a66ac7785d5 | 待关闭时核 |

## Closeout Record

- Closeout date / DSH：待 DSH 复核后填写（in_review）。
- canonical_evidence_status：`pinned`（E1–E13，commit c8772697b）。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：已更新 STATUS/PLAN/LEDGER。
