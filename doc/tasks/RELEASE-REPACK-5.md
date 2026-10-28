---
id: RELEASE-REPACK-5
title: 第五次重打包（含三布局主题合并）与安装验收
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-28_repack
suggested_owner: core-admin-rca
owner: null
reviewer: dsh
depends_on: []
base_commit: 6120f91e5
branch: task/RELEASE-REPACK-5
worktree: G:/CODEX/New Manga.workspace/worktrees/RELEASE-REPACK-5
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/RELEASE-REPACK-5
allowed_paths:
  - doc/tasks/RELEASE-REPACK-5.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - packaging/**
  - apps/desktop-avalonia/scripts/**
  - apps/desktop-avalonia/docs/**
  - verification/RELEASE-REPACK-5/**
  - G:/CODEX/New Manga.workspace/task-envs/RELEASE-REPACK-5/**
  - G:/CODEX/New Manga.workspace/worktrees/RELEASE-REPACK-5/**
---

# RELEASE-REPACK-5：第五次重打包（含三布局主题）

## 背景
REPACK-4（repo_head 1b89c5e5）之后，main 已合并 **THEME-MACOS-2 三布局实现**（Sonoma/Launchpad/Split，superset，test 249/249，HEAD \$h\）。REPACK-4 包不含该主题，需要重新出包。

## Acceptance Criteria

- [x] **AC1 重打包**：当前 HEAD 重打 base+models zip（记录 HEAD/新旧 sha256/大小；torch-free 断言）。→ **MET**：HEAD `6120f91e5`；base zip **103,374,546B** sha256 `7e178f29aba35a1fb9eb1941ee66828d3c1127e387c187233c12fe427b42bbff`、models zip **725,382,787B** sha256 `41b330f575f28e62e1b5b566f1ba5c4ba90dd6b5d251d0adf069b99974a9d32e`（旧 103,330,812/725,339,894B）；sidecar base `28ba3bb9…`/models `bde2d866…`（未复用旧 exe）；VERSION `repo_head=6120f91e5…`；torch-free PASS。证据 `package-hashes.json`。
- [x] **AC2 安装 + 主题验收**：全新安装 → 启动 → 设置页主题列表可见 7 packs 且含 macOS 三套布局主题 → 切换生效（≥2 截图含一套布局）。→ **MET（实际 9 packs）**：安装 2,549.2ms、Host 就绪 4,112.6ms；设置页实际可见 **9 packs**（6 legacy + 3 macOS=风/启动台/分栏，按实际注册名；任务预期 7，实为超集）；`macos-sonoma`/`macos-launchpad`（底部 Dock）/`macos-split`（左侧 Sidebar）切换生效并有截图。证据 `screens/01,02-*`、`smoke.json`。
- [x] **AC3 冒烟**：书架 → 导入 → 阅读 → 沉浸 Esc/H → 导出 ZIP（记录产物 sha）。→ **PARTIAL**：书架/阅读/沉浸 Esc/H（前台真实 keybd_event；H 后 sha `238C10E2…`→`CCC9E3AE…`，Esc 回到 `1D3E3CBF…`）/导出 ZIP **7,070,562B sha256 `5cfffa9f52fd2ab5967d40b6b6fcf1341a45e31b8670128feb0a5c4263e33609`** 成功；**导入 BLOCKED**：状态卡「正在导入文件…」>40s、DB pages 不增、wire 仅 Register/RevokeImportSource 无 ImportPages（书架+工作台+默认主题+重复 fixture 均复现），未伪造；`ImportExportPanels/HostController` 与 REPACK-4（导入正常）无 diff → 需 DSH triage。证据 `screens/04*,05,08`、`import-wire-tail.ndjson`。
- [x] **AC4 门禁**：干净 worktree `test.ps1` 全绿（≥249）；pytest 无新增失败；check.ps1 -TaskPath PASS；64-hex pin；Handoff。→ **MET**：`TEST PASS 249/249`（CoreClient 61+Host 56+App 132）；pytest **0F/2773P/10S**；check.ps1 PASS；pin 见下表；Handoff 已交付。
- [x] **AC5**：Launchpad/Split 仅截图记录，不做完整视觉验收。→ 已记录 `screens/02-theme-macos-launchpad.png`、`02-theme-macos-split.png`。

## 允许修改范围
packaging/**、pps/desktop-avalonia/scripts/**、pps/desktop-avalonia/docs/**、本卡、STATUS/PLAN/LEDGER、erification/RELEASE-REPACK-5/**、workspace。

## 禁止范围
不改 Core/协议/Host 契约/旧壳、不 push、不 gc/prune；不得复用旧 exe 冒充新构建；不伪造截图/数字；禁止 \git add -A\。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/RELEASE-REPACK-5 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/RELEASE-REPACK-5 | `out/`（新包）、`sidecar-*/`、`data-root/`、`screens/` | 证据已复制到 `verification/RELEASE-REPACK-5/`；旧包 REPACK-4/out 未动 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：导入 BLOCKED（待 DSH triage：HEAD 回归 vs 数据根/环境）；主题数量 9 与预期 7 口径确认；4K@200% 环境限制；凭据 2 条历史残留待裁决。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
