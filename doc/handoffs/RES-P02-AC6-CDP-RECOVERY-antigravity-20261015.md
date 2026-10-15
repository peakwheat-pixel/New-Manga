---
task_id: RES-P02-AC6-CDP-RECOVERY
author: Antigravity
recipient: DeepSeek Harness (Coordinator) / Codex
base_commit: 8ec9f3b8cefe3d2165eb8f6b15fac805394619ee
delivery_head: 40c38a5fa502cd1be633acc5bff3f9c1e06ff9e3
status: blocked
---

# Handoff：RES-P02-AC6-CDP-RECOVERY

## 交付结果

本 Task 为 resolution 任务，目标为恢复固定 packaged EXE 的 WebView2 CDP 可采集性并完成 AC6 重采样以闭合 `R3-01`。
在当前主机环境下，Owner 完成了三组严格对照实验（干净代理环境对照、启动期进程与端口实时抓取、直接 Node 启动追踪），结果全部确认：固定 packaged EXE 在启动进入主窗口 setup 阶段调用 Windows / WebView2 控制器时抛出 `WindowsError(Error { code: HRESULT(0x80070578), message: "无效的窗口句柄。" })` 并发生 Rust panic 崩溃退出。由于主进程崩溃，`msedgewebview2.exe` 从未成功初始化，CDP 调试端口 9333 绝无可能产生 listener，Node 采集器在 45 秒超时后报 `TypeError: fetch failed`。

根据治理规则与验收标准，**本任务如实标记为 `BLOCKED`，禁止伪造 PASS，禁止新增 I3 返修轮**。

- **产品代码 / 依赖 / 契约 / AC**：零修改。
- **被阻塞 Task 文件**（`doc/tasks/P02-NEW-TIME-X6-AC1-AC7.md`）：零修改。
- **既有证据保护**：未覆盖 `runs/p02-newtime-ac-20261014-i1/**` 与 `-i2/attempts/**`，所有新证据以 `COPYFILE_EXCL` 写入隔离目录 `verification/RES-P02-AC6-CDP-RECOVERY/`。

## 验证证据

| 场景/实验 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| 实验 1：干净代理环境对照 | `Remove-Item Env:*PROXY*; node apps/desktop/frontend/e2e/p02-new-time/ac6-contrast.mjs` | 固定 EXE sha256 `92AC7B...FD` / Node v24.15.0 / 清空代理 | `FAIL` (exit 1) | `verification/RES-P02-AC6-CDP-RECOVERY/attempts/exp1-proxy-clean/`；暴露 0x80070578 panic |
| 实验 2：启动期进程与端口实时抓取 | `pwsh -NoProfile -File scratch/diag_proc_monitor.ps1` | 固定 EXE sha256 `92AC7B...FD` / 400ms 轮询抓取 | `FAIL` (exit 1) | `verification/RES-P02-AC6-CDP-RECOVERY/attempts/exp2-live-monitor/`；捕获 PID 20920，webview2 为 0，端口为 0 |
| 实验 3：直接调用 Node 进程追踪 | `& node apps/desktop/frontend/e2e/p02-new-time/ac6-contrast.mjs` + 后台 trace | 原生 pwsh / Node v24.15.0 / 后台 trace | `FAIL` (exit 1) | `verification/RES-P02-AC6-CDP-RECOVERY/attempts/exp3-direct-trace/`；捕获 PID 12972 瞬间崩溃退出 |
| 综合诊断报告 | 查证注册表 Edge 策略、WebView2 运行时版本与错误码 | 详细分析 Win32 窗口句柄失效与 Tauri 2 窗口初始化机制 | `BLOCKED` | `verification/RES-P02-AC6-CDP-RECOVERY/report.md` |

## 逐条“已闭合 / 未闭合”声明

- **R3-01 — 未闭合（BLOCKED）**：采样器代码在 I2 中已包含表单控件采样逻辑，但因固定 EXE 在当前主机环境触发 0x80070578 崩溃，未能取得真实 DOM 对比度数据；不伪造 PASS。
- **AC6 — BLOCKED**：`[data-testid="page-id-input"]` 行未能采得；无虚构数据。
- **R3-04 — 保持已闭合**（I2 已闭合）。
- **R3-06 — 保持已闭合**（I2 已闭合）。

## 接收方式

- 分支：`agent/antigravity/P02-NEW-TIME-X6-AC1-AC7`
- Worktree：`G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-AC1-AC7-ANTIGRAVITY`
- 证据目录：`verification/RES-P02-AC6-CDP-RECOVERY/`
- Manifest：`verification/RES-P02-AC6-CDP-RECOVERY/manifest/owner-evidence-manifest.json`

## 下一任务建议（必填）

- **Task ID / 标题**：`RES-P02-AC6-HOST-INTERACTIVE-ENV-RECOVERY` / 主机交互式桌面环境恢复与复测
- **推荐 Agent / Reviewer**：用户（操作主机环境）/ DeepSeek Harness（Coordinator 验证）
- **推荐原因与前置依赖**：0x80070578（ERROR_INVALID_WINDOW_HANDLE）系 Windows 主机当前桌面会话无活动交互窗口站（WinSta0\Default）引发的系统级限制。需要用户在前台交互式桌面会话中复测或重启主机。
- **Recovery point**：`G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-AC1-AC7-ANTIGRAVITY`
- **允许修改路径**：`verification/RES-P02-AC6-CDP-RECOVERY/**`
- **禁止范围与新增授权条件**：禁止修改产品代码，禁止修改 `doc/tasks/P02-NEW-TIME-X6-AC1-AC7.md`，禁止进入 I3 返修轮。
- **交付物**：前台交互桌面下的复测结果与端口监听证据。
- **验证命令、环境与完成 Gate**：在交互桌面会话中执行 `node apps/desktop/frontend/e2e/p02-new-time/ac6-contrast.mjs`。
- **可直接转发给 Agent 的指令**：
  > 请在确保当前 Windows 处于前台交互式用户桌面（非锁屏、非远程会话挂起）后，执行复测命令，并验证端口 9333 listener 是否正常出现。

## 风险与遗留

- 固定 EXE 本身并非功能性缺陷，但在无头或断开桌面的会话中无法创建 Win32 窗口并附加 WebView2 控制器。
- 只有在交互桌面恢复后，才能最终判定输入框的对比度是否满足 WCAG 阈值。
