---
id: RELEASE-REPACK-4
title: 最终发布包（含 PDF UI/工具/修复）与端到端验收
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-28_goal_all_authorized
suggested_owner: core-admin-rca
owner: null
reviewer: dsh
depends_on: []
base_commit: f1b89c5e5
branch: task/RELEASE-REPACK-4
worktree: G:/CODEX/New Manga.workspace/worktrees/RELEASE-REPACK-4
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/RELEASE-REPACK-4
allowed_paths:
  - doc/tasks/RELEASE-REPACK-4.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - packaging/**; apps/desktop-avalonia/scripts/**; apps/desktop-avalonia/docs/**
  - verification/RELEASE-REPACK-4/**
  - G:/CODEX/New Manga.workspace/task-envs/RELEASE-REPACK-4/**
  - G:/CODEX/New Manga.workspace/worktrees/RELEASE-REPACK-4/**
---

# RELEASE-REPACK-4：最终发布包（含 PDF UI / 翻译工具 / 最终修复）

## 背景
REPACK-3（repo_head dd2408869）之后合入了 PDF-EXPORT-UI-1（PDF 面板）、REAL-TRANSLATE-PROVIDER-1 工具与测试修复。需要一次**最终**打包，并做端到端验收（含 PDF 导出）。

## Acceptance Criteria

- [x] **AC1 重打包**：当前 HEAD 重打 base+models zip（记录新旧 sha256/大小/HEAD；torch-free 断言）。→ **MET**：构建 HEAD `f1b89c5e5`（含 Lead 修复 `4be1c3f4f`；原 base `84dd38978` 编译失败，证据 `build-head-failure.log`）；新 base zip **103,330,812B**、models zip **725,339,894B**（旧 103,326,248 / 725,334,588B）；sidecar base `bd23e66f…0d99`、models `3909a4a2…f57dde5`（未复用旧 exe）；VERSION `repo_head=f1b89c5e5…`；torch-free PASS。
- [x] **AC2 全流程（含 PDF）**：全新安装 → 导入 → 阅读 → 沉浸 Esc/H → 导出 ZIP → 导出 PDF（面板 PDF/searchable_dual_layer）→ 打开导出目录；每步截图/耗时。→ **MET**：安装 2,545.5ms、Host 就绪 1,100.1ms、console 0；导入 1 文件 9→10 页；阅读/滚动；沉浸（UIA 按钮）；**PDF 20,728,075B sha256 `c0a97eb3…b210` 3 页 `%PDF-1.7`+ToUnicode**；ZIP 7,070,562B sha256 `72d81db9…945c`（3 JPG+manifest）；打开导出目录 2.9s。证据 `screens/01–10`、`smoke.json`。
- [x] **AC3 真机 5 项**：Mica（actual/取色）、4K@200% DPI、工作集、Esc/H 键盘（前台自动化）、IME N/A。→ **部分**：Mica **本次 actual=None**（transparency=1、DWM 38=0；REPACK-3 同机曾 actual=Mica → 疑似回归，需复核）；4K@200% **NOT_AVAILABLE**（主屏 2560×1440@100%；Mi TV 3840×2160 物理连接但当前未在桌面扩展，REPACK-3 时为 150%）；WS App **526.7MB**、core 44.5MB、bridge 23.7MB；Esc/H **前台已取得（foreground_pid==app_pid）且真实 keybd_event 已发送，但前后截图 sha 相同、UI 无可观察变化** → PARTIAL；IME N/A。证据 `environment.json`、`screens/11–14`。
- [x] **AC4 稳定性**：0 残留、console 0、卸载干净。→ **MET**：WM_CLOSE 4,267.9ms；本安装 0 残留；卸载 exit=0、目录消失、数据根保留；注册表 `*NewManga*` 0；凭据 2 条历史/他 Agent 残留只上报未删。
- [x] **AC5 门禁**：干净 worktree test.ps1 全绿（≥241）；pytest 0F/2773P/10S；check.ps1 PASS；64-hex pin；Handoff。→ **MET（test 计数为 Lead 修复后预期 232/232，非 241；Mac 主题测试已移除待 THEME-MACOS-2 重做）**：`TEST PASS 232/232`；pytest **0F/2773P/10S**；check.ps1 PASS；pin 见下表；Handoff 已交付。

## 允许修改范围
`packaging/**`、`apps/desktop-avalonia/scripts/**`、`apps/desktop-avalonia/docs/**`、`verification/RELEASE-REPACK-4/**`、本卡/STATUS/PLAN/LEDGER、workspace。

## 禁止范围

不改 Python Core 语义/协议/Host 契约/旧壳、不 push、不 gc/prune；不得伪造结果；**禁止 `git add -A`（主工作树有其它会话改动）**。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/RELEASE-REPACK-4 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/RELEASE-REPACK-4 | `out/`（新包）、`sidecar-*/`、`data-root/`、`screens/` | 证据已复制到 `verification/RELEASE-REPACK-4/`；旧包 REPACK-3/out 未动 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：Mica actual=None 疑似回归（待 DSH 复核）；4K@200% 环境不具备；Esc/H 键盘无可观察响应（待用户真机确认）；凭据 2 条历史残留待裁决。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。

## 构建阻塞记录

原 base `84dd38978`：`MainWindow.axaml.cs(593) error CS1061: SettingsPage 未包含 ApplyLayout`（`152538e34` 引入调用、未提交实现）；已上报 Lead，修复提交 `4be1c3f4f` 回退未落地主题 API（UI 文件→`4ea86e03a`，Mac 主题测试移出），其后 `f1b89c5e5` 为 ledger 提交；本任务以 `f1b89c5e5` 出包。
