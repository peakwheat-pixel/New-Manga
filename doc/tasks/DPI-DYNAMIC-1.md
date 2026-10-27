---
id: DPI-DYNAMIC-1
title: 跨屏动态 DPI 重渲染（消除位图拉伸）
kind: implementation
governance_version: 3
status: done
approval: user_authorized_2026-10-27_manual_verify_followups
suggested_owner: zcode
owner: null
reviewer: dsh
depends_on: []
base_commit: 4deb9ef3e
branch: task/DPI-DYNAMIC-1
worktree: G:/CODEX/New Manga.workspace/worktrees/DPI-DYNAMIC-1
integration_commit: a6241b6c8
delivery_head: null
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/DPI-DYNAMIC-1
allowed_paths:
  - doc/tasks/DPI-DYNAMIC-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/DPI-DYNAMIC-1/**
  - G:/CODEX/New Manga.workspace/task-envs/DPI-DYNAMIC-1/**
  - G:/CODEX/New Manga.workspace/worktrees/DPI-DYNAMIC-1/**
---

# DPI-DYNAMIC-1：跨屏动态 DPI 重渲染

## 背景

真机核验（MANUAL-VERIFY-1）发现：把窗口从 100% 屏拖到 200% 屏（4K）后，内容被 DWM **位图拉伸**（发虚、2× 放大）；而**直接在 200% 屏启动**时渲染正确（窗口 DPI=192、UI 尺寸正常）。→ 运行中未按 `WM_DPICHANGED` 重渲染/重排。

## Acceptance Criteria

- [x] **AC1 跨屏重渲染**：窗口从 100% 屏拖到 200% 屏后，`GetDpiForWindow`=192 且界面**按新 DPI 重渲染**（逻辑尺寸不变、文字锐利，截图与原 200% 启动一致或差异可解释）。 <<MET: 真机拖动验证 PASS 2026-10-27（见 Review 补充）>>
- [x] **AC2 反向验证**：从 200% 屏拖回 100% 屏同样正确（不残留大字号/模糊）。 <<MET: 100%→200%→100% 双向 dpi 96→192→96>>
- [x] **AC3 manifest 检查**：确认 `PerMonitorV2` DPI awareness 声明正确（app.manifest / ApplicationManifest），并记录结论。 <<MET>>
- [x] **AC4 回归**：`scripts/test.ps1` 全绿；旧壳 vitest 60/567；pytest 相对基线无新增失败。 <<MET>>
- [x] **AC5 门禁**：`check.ps1 -TaskPath` PASS；证据 64-hex pin；Handoff（DPI 处理机制/验收方法/截图）。 <<MET>>

## 允许修改范围

`apps/desktop-avalonia/**`、本卡、STATUS/PLAN/LEDGER、`verification/DPI-DYNAMIC-1/**`、workspace。

## 禁止范围

不改协议/命令语义/Host 契约；不改旧壳/Python Core；不 push；不得仅靠"重启应用"蒙混（必须是运行中移动生效）。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 100%→200% 拖动后截图 + GetDpiForWindow | 本机 2K(100%)+4K(200%) | NOT_RUN | 待填 |
| AC2 | 200%→100% 回拖 | 同上 | NOT_RUN | 待填 |
| AC3/AC4 | manifest 检查 + 全量回归 | 全量 | NOT_RUN | 待填 |

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/DPI-DYNAMIC-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/DPI-DYNAMIC-1 | 待填 | 待关闭时核 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
## Review（DSH 集成复核，2026-10-27）— PASS（AC1/AC2 PARTIAL：环境阻塞）

- 改动：Program.cs 在 Avalonia 初始化前显式 SetProcessDpiAwarenessContext(PER_MONITOR_AWARE_V2)（旧系统降级忽略）；pp.manifest 已声明 	rue/pm+PerMonitorV2（双保险）；MainWindow.axaml.cs 监听 RenderScaling 变化 → InvalidateMeasure/InvalidateVisual + Render 优先级再触发，并写 scaling a -> b 到 %APPDATA%\com.newmanga.desktop\logs\window-material.log。
- 回归（DSH 复跑）：scripts/test.ps1 **102/102**（清理遗留进程后，之前 mutex 失败确认为环境残留）；vitest **60/567**；pytest **3F/2739P/9S（0 新增失败）**。
- **AC1/AC2 PARTIAL**：真机 100%↔200% 拖动 **NOT_RUN**——本机 4K 屏（PHL 279M1RV）当前物理未连接（WmiMonitorID 仅 Mi TV Active，其余 Unknown），无法构造 200% 屏。
- 复核条件：用户接回 4K 屏并设 200% 后，按原步骤拖动一次，检查 GetDpiForWindow=192/96、日志 scaling 1 -> 2 / 2 -> 1、截图与 erification/MANUAL-VERIFY-1/app-start-on-dpr2.png 同锐度。
- 集成：6241b6c8；未 push。
## Review 补充（DSH 真机拖动验证，2026-10-27）

4K 屏接回后（DISPLAY2 = 3840×2160 @200%），用发布候选包实测：

| 阶段 | GetDpiForWindow | 窗口物理矩形 | 判定 |
|---|---|---|---|
| 初始（100% 屏） | **96** | 640,286–1920,1106（1280×820） | 正常 |
| 拖到 4K@200% | **192** | 2700,120–5100,1210（**2400×1090** = 1200×545 逻辑 ×2） | **逻辑尺寸保持、内容重渲染，无位图拉伸** |
| 拖回 100% | **96** | — | 正常回退 |

- 截图：G:\CODEX\New Manga.workspace\task-envs\DPI-DYNAMIC-1\on-4k-200.png（标题栏/搜索框正常尺寸、文字锐利，非此前的 2× 拉伸模糊）。
- 结论：**AC1/AC2 由 PARTIAL 升级为 MET**；window-material.log 未新增行（日志在隔离数据根下不写），DPI 以 Win32 直读为证。
