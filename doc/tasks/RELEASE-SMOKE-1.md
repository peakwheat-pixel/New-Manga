---
id: RELEASE-SMOKE-1
title: 新包真机全流程快检
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-27_round_2_5
suggested_owner: core-admin-rca
owner: null
reviewer: dsh
depends_on: []
base_commit: 13cf26f6c
branch: task/RELEASE-SMOKE-1
worktree: G:/CODEX/New Manga.workspace/worktrees/RELEASE-SMOKE-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/RELEASE-SMOKE-1
allowed_paths:
  - doc/tasks/RELEASE-SMOKE-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/scripts/**; apps/desktop-avalonia/docs/**
  - verification/RELEASE-SMOKE-1/**
  - G:/CODEX/New Manga.workspace/task-envs/RELEASE-SMOKE-1/**
  - G:/CODEX/New Manga.workspace/worktrees/RELEASE-SMOKE-1/**
---

# RELEASE-SMOKE-1：新包真机全流程快检

## 背景
REPACK-2 包（base 102,981,645B / models 724,989,976B）已产出；UI 导入/导出入口已接。需要一次全新安装→使用→导出的真机验收。

## Acceptance Criteria
- [x] **AC1 安装**：全新目录安装最新 models 包（install.ps1 / 安装 smoke 流程）→ 启动应用（无 console 窗口、sidecar 随包）。→ **MET**：全新目录安装 **2,602.8ms**；启动→Host 就绪 **4,098.0ms**；**console 窗口 0**；sidecar 随包 **1965 files / 868,862,035B**（models_bundled=true）；窗口 "New Manga"、书架 1 本 8 页；证据 `smoke.json`、`screens/09-fresh-install-bookshelf.png`、`install-timed.log`。
- [x] **AC2 全流程**：书架→（导入 fixture 书）→阅读器→翻页/进度→沉浸 Esc/H→导出（ZIP）→打开导出目录；每步截图 + 关键耗时。→ **PARTIAL / BLOCKED（包过期）**：书架→阅读器→**滚动翻页**→**reading_progress 落库**（progress_percent=2.26、total_read_seconds=68.32）→**沉浸模式真机触发**（UIA ImmersiveButton，无边框全屏+chrome 隐藏）均通过；**导入/导出 BLOCKED**：REPACK-2 包构建于 `0f4b836a5`，早于 IMPORT-EXPORT-UI-1（`13cf26f6c`），exe 内无「导入文件/开始导出/打开导出目录」字符串、工作台/阅读器无对应控件 → 未伪造；证据 `screens/02–06`、`package-evidence.json`。
- [x] **AC3 稳定性**：运行中无残留进程；卸载后目录干净、无系统残留（凭据/注册表项列清）。→ **MET**：WM_CLOSE 优雅退出 **4,084.3ms**，app/core_service/host_bridge **0 残留**；卸载 exit=0、安装目录消失、数据根保留；注册表 `*NewManga*` **0**；凭据管理器 **1 条历史遗留**（`NewManga/provider/p15-host-2-smoke/…`，旧 Tauri 测试产生，非本 Task，未删）；`%TEMP%` 无本次残留；证据 `host.log`、`uninstall-timed.log`、`smoke.json`。
- [x] **AC4 真机 5 项快检**：Mica 取色、4K@200% DPI、工作集、IME（用户确认）、Esc/H；其中 IME 标注需用户确认。→ **PARTIAL（环境不满足 + 待用户确认）**：**Mica N/A**（本机 Windows 10 Pro 26H2 build 26300；DWM backdrop type=0，窗口像素不透明：标题栏 #FFFFFF/主体 #F5F3FA）；**4K@200% N/A**（实际 2×2560×1440 @96DPI=100%，需 4K@200% 机器）；工作集 App 空闲 147.5MB / 阅读滚动 411.9MB、core_service 41.1MB、host_bridge 22.7MB；**IME 待用户确认**；**Esc/H**：沉浸按钮（Esc/H/F 同组）真机验证为无边框全屏+chrome 隐藏，键盘 Esc/H 需前台焦点（自动化会话被用户 DSH 窗口占前台）→ 待用户前台确认；证据 `smoke.json`、`screens/06`、`screens/08`。
- [x] **AC5 门禁**：check.ps1 -TaskPath PASS；64-hex pin；Handoff；不 push、不删旧包。→ **MET**：check.ps1 PASS（2 条既有 WARN）；pin 见下表；`doc/handoffs/RELEASE-SMOKE-1-handoff.md`；未 push、未删旧包、未触碰真实 `%APPDATA%` 书库/凭据库。

## 允许修改范围

`apps/desktop-avalonia/scripts/**; apps/desktop-avalonia/docs/**`、本卡、STATUS/PLAN/LEDGER、`verification/RELEASE-SMOKE-1/**`、workspace。

## 禁止范围

不改协议/Host 契约/旧壳、不 push、不 gc/prune；不得伪造结果；**不得把任何 API key/secret 写入仓库、日志或证据**。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| E-RS-REPORT | AC1–AC5 | `verification/RELEASE-SMOKE-1/REPORT.md` | `5c3e90269` | `ed87156017ff067d47f92b1545baf2810a12bd69bba2a6188bee71107cebfb26` | CANONICAL |
| E-RS-SMOKE | AC1–AC4 | `verification/RELEASE-SMOKE-1/smoke.json` | `5c3e90269` | `82a65f0370957c0f13e8ace5ed58cc0fce058d722201bc41db4ba400354a8968` | CANONICAL |
| E-RS-PKG | AC2 | `verification/RELEASE-SMOKE-1/package-evidence.json` | `5c3e90269` | `a55fccffac96952c05fbadff760c5fd5af9e8dcd8e5698906b4587eda4ae67c2` | CANONICAL |
| E-RS-BOOKSHELF | AC1/AC2 | `verification/RELEASE-SMOKE-1/screens/09-fresh-install-bookshelf.png` | `5c3e90269` | `54c44d20ff6c5cc8134d405d5087317a0255430af8b3781c85ea1f72026289ca` | CANONICAL |
| E-RS-WORKBENCH | AC2 | `verification/RELEASE-SMOKE-1/screens/03-workbench.png` | `5c3e90269` | `85954f09cf058bbf151a18d492c234e02356acc4e052441848dea312b50ffb79` | CANONICAL |
| E-RS-READER | AC2 | `verification/RELEASE-SMOKE-1/screens/04-reader.png` | `5c3e90269` | `2b46dbcbb89819ecac0254840954d8eeaf6d2c51f96ce42d8269df3884ec52e0` | CANONICAL |
| E-RS-SCROLL | AC2 | `verification/RELEASE-SMOKE-1/screens/05-reader-page2.png` | `5c3e90269` | `d6f6a843e2be348ee4f1a8dec364b1951851b192d184191f625b1a519596329d` | CANONICAL |
| E-RS-IMMERSIVE | AC2/AC4 | `verification/RELEASE-SMOKE-1/screens/06-immersive.png` | `5c3e90269` | `3fc2c1df1f67982c75c3e46117034f68309e3591585748970990b2e0f08dd356` | CANONICAL |
| E-RS-HOSTLOG | AC1/AC3 | `verification/RELEASE-SMOKE-1/host.log` | `5c3e90269` | `79b79615b0e9b690b584122e8b95d9b1f91e1989fa1402d0771475a9511fd158` | CANONICAL |
| E-RS-INSTALL | AC1 | `verification/RELEASE-SMOKE-1/install-timed.log` | `5c3e90269` | `8ae9284eab6072c337b5503aa3bf72cf0e55c327ffc46976cc0fe55415fef66c` | CANONICAL |
| E-RS-UNINSTALL | AC3 | `verification/RELEASE-SMOKE-1/uninstall-timed.log` | `5c3e90269` | `babbccf06adb6765e3a6a6cc625436685a8b5b2e023c3db95a541a003df23b32` | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/RELEASE-SMOKE-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/RELEASE-SMOKE-1 | `screens/`、`data-root/`（隔离副本）、`app-logs/`、`install-timed.log`、`uninstall-timed.log` | 证据已复制到 `verification/RELEASE-SMOKE-1/`；无 secret；关闭时按裁决保留/清理 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：AC2 导入/导出被陈旧包阻塞（需 REPACK-3）；AC4 Mica/4K/IME/键盘 Esc/H 待环境或用户确认。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
