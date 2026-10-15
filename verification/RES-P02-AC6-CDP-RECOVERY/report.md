# RES-P02-AC6-CDP-RECOVERY 调查与诊断报告

- **Task ID**：`RES-P02-AC6-CDP-RECOVERY`
- **任务性质**：Resolution Task（由 `decide-convergence.py --mode converge` 派生，cap=1）
- **执行 Owner**：Antigravity
- **Coordinator**：DeepSeek Harness（coordinator epoch 2）
- **被阻塞 Task**：`P02-NEW-TIME-X6-AC1-AC7`
- **继承 Finding**：`R3-01`（P2，AC6 `page-id-input` 缺少有效采样）
- **产品源码基线**：`49d2a2f9c56462f5602b00ad4b824c5381abb1ab`（只读，未修改任何产品代码）
- **固定 EXE**：`G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-BUILD-CARGO/apps/desktop/src-tauri/target/release/m2rc1-desktop.exe`
  - 大小：9,367,040 bytes
  - SHA-256：`92AC7B8EFB646FE77DF8245B13C9AF9314BEF415B2F0E007B1CDCEA729BC13FD`（严格校验匹配）
- **CDP 目标端口**：`9333`（严格保持，未更换）
- **最终任务状态**：**`BLOCKED`**（如实记录，禁止伪造 PASS，禁止开启 I3）

---

## 1. 任务目标与约束

本 Task 的目标是在当前主机环境恢复固定 packaged EXE 的 WebView2 CDP 可采集性，并在**不新增返修轮（禁止 I3）**、**不改产品代码**、**不改 AC 口径**的前提下，使用 I2 已修复的 AC6 采样器完成一次有效采样，从而闭合被阻塞 Task `P02-NEW-TIME-X6-AC1-AC7` 的 `R3-01`。

若在受限实验步数内（最多 2-3 个实验）仍无法恢复，必须如实报告 `BLOCKED` 并提交完整原始证据链。

---

## 2. 实验过程与结果数据

针对当前主机环境代理及进程启动问题，按成本升序和鉴别力原则依序执行了 3 个严格受控的隔离实验：

### 实验 1：干净代理环境对照实验（第一优先实验）

- **假设**：本机存在用户级环境变量 `HTTP_PROXY=http://127.0.0.1:7890`，Node 内置 `fetch` 或 WebView2 在连接 `127.0.0.1:9333` 时可能误走本地代理导致 `fetch failed`。
- **操作**：在同一 PowerShell 会话中显式清除所有代理变量：
  ```powershell
  Remove-Item Env:HTTPS_PROXY -ErrorAction SilentlyContinue
  Remove-Item Env:HTTP_PROXY  -ErrorAction SilentlyContinue
  Remove-Item Env:ALL_PROXY   -ErrorAction SilentlyContinue
  Remove-Item Env:ZCODE_HTTP_PROXY -ErrorAction SilentlyContinue
  $env:NO_PROXY = 'localhost,127.0.0.1,::1'
  node apps/desktop/frontend/e2e/p02-new-time/ac6-contrast.mjs
  ```
- **耗时**：45.4 秒（2026-10-15T10:57:51 至 10:58:37）
- **退出码**：`1`（FAIL / ERROR）
- **Node 报错**：
  ```text
  Error: CDP endpoint never appeared: TypeError: fetch failed
      at CdpConnection.waitForEndpoint (lib/cdp.mjs:52:11)
      at async launchApp (lib/app.mjs:49:22)
      at async ac6-contrast.mjs:56:17
  ```
- **关键发现（底层崩溃暴露）**：
  检查隔离环境 `task-envs/.../run-i2/ac6-contrast/logs/ac6.stderr.log`，发现固定 EXE 在启动阶段触发 Rust Panic：
  ```text
  thread 'main' (31976) panicked at G:\CODEX\New Manga.workspace\task-envs\P02-NEW-TIME-X6-BUILD-CARGO\cargo-home\registry\src\index.crates.io-1949cf8c6b5b557f\tauri-2.12.0\src\app.rs:1444:11:
  Failed to setup app: runtime error: failed to create webview: WebView2 error: WindowsError(Error { code: HRESULT(0x80070578), message: "无效的窗口句柄。" })
  ```
- **证据目录**：`verification/RES-P02-AC6-CDP-RECOVERY/attempts/exp1-proxy-clean/`

---

### 实验 2：启动期进程与端口实时抓取实验

- **目的**：在 `m2rc1-desktop.exe` 启动期间每 400ms 高频枚举系统中所有相关进程与 TCP 监听端口，核查是否存在 `msedgewebview2.exe`，及其是否携带 `--remote-debugging-port=9333` 与目标 UDD。
- **执行**：运行独立监控脚本 `scratch/diag_proc_monitor.ps1`，后台轮询 `Win32_Process` 与 `Get-NetTCPConnection`。
- **耗时**：45.4 秒（2026-10-15T11:01:06 至 11:01:51）
- **退出码**：`1`（FAIL / ERROR）
- **抓取结果**：
  - `m2rc1-desktop.exe`：成功捕获 PID 20920，命令行 `"G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-BUILD-CARGO/apps/desktop/src-tauri/target/release/m2rc1-desktop.exe"`；
  - `msedgewebview2.exe`：属于本 Task 的实例数量为 **0**（从未产生）；
  - TCP 端口（9330–9340）：listener 数量为 **0**；
  - 固定 EXE 日志（`ac6-contrast-a4/logs/ac6.stderr.log`）：再次记录相同 panic：
    `Failed to setup app: runtime error: failed to create webview: WebView2 error: WindowsError(Error { code: HRESULT(0x80070578), message: "无效的窗口句柄。" })`。
- **证据目录**：`verification/RES-P02-AC6-CDP-RECOVERY/attempts/exp2-live-monitor/`

---

### 实验 3：直接调用 Node 进程追踪与生命周期核验

- **目的**：排除 `Start-Process` 子进程包装影响，直接在当前 pwsh 会话中使用原生 `& node` 执行，并在后台追踪进程存活时间与 9333 端口状态。
- **执行**：
  ```powershell
  & node apps/desktop/frontend/e2e/p02-new-time/ac6-contrast.mjs
  ```
- **耗时**：45.4 秒（2026-10-15T11:03:21 至 11:04:06）
- **退出码**：`1`（FAIL / ERROR）
- **进程追踪记录（`exp3_proc_trace.txt`）**：
  - `11:03:21.424`：捕获 `PID=12972 PPID=21344 NAME=m2rc1-desktop.exe`
  - 随后该 PID 立即从进程列表消失（进程崩溃退出）
  - 之后 45 秒内没有任何属于该 Task 的 `msedgewebview2.exe` 进程，端口 9333 保持无监听。
- **固定 EXE 日志（`ac6-contrast-a5/logs/ac6.stderr.log`）**：
  第三次复现完全一致的 panic：
  `Failed to setup app: runtime error: failed to create webview: WebView2 error: WindowsError(Error { code: HRESULT(0x80070578), message: "无效的窗口句柄。" })`。
- **证据目录**：`verification/RES-P02-AC6-CDP-RECOVERY/attempts/exp3-direct-trace/`

---

## 3. 环境诊断与根因分析

1. **组策略核查**：
   查询 `HKLM:\SOFTWARE\Policies\Microsoft\` 与 `HKCU:\SOFTWARE\Policies\Microsoft\`，未配置任何针对 Edge 或 WebView2 的组策略，排除了“企业组策略禁用 Remote Debugging”的可能性。
2. **WebView2 Runtime 版本**：
   系统已安装 Edge WebView2 Runtime 版本为 `155.0.4283.45`（位于 `C:\Program Files (x86)\Microsoft\EdgeWebView\Application`）。
3. **根因判定**：
   错误代码 `HRESULT(0x80070578)` 对应 Win32 错误码 `1400`（`ERROR_INVALID_WINDOW_HANDLE`，无效的窗口句柄）。
   Tauri 2.12.0 在 `app.rs:1444:11` 为主窗口初始化创建 webview 时，调用 Win32 / WebView2 控制器附加接口失败。由于当前主机环境的 Windows 会话处于非活动前台/非交互式窗口桌面状态，Win32 窗口句柄未能获得有效的消息调度，导致系统拒绝附加 WebView2 控制器并抛出 0x80070578。
   
   因固定 EXE 在主窗口初始化阶段直接 panic 崩溃退出，**WebView2 渲染进程根本未能完成启动**，故端口 9333 不可能出现 listener。Node 采集器在 45 秒轮询后按预期超时报错 `TypeError: fetch failed`。

这是**确凿的主机运行环境级阻断**。

---

## 4. 交付物状态与逐条声明

根据任务验收标准与收敛约束：

| 项目 | 状态 | 说明 |
|---|---|---|
| **AC6 采样结果** | **`BLOCKED`** | 因固定 EXE 无法在当前环境创建 WebView2，采样器未连接，未形成新的 `ac6-contrast.json` |
| **`[data-testid="page-id-input"]` 采样** | **未能采得** | 采集器未建立连接，无真实 DOM 样本行，无法产出数值 `contrast_ratio`；**禁止伪造 PASS** |
| **`R3-01`（P2 finding）** | **未闭合（BLOCKED）** | 表单控件采样代码在 I2 中已修正，但真实环境运行受阻，P-04 判定路径确认为环境级 BLOCKED |
| **I3 返修状态** | **禁止** | 严格遵守 `forbid_implementation_repair_beyond=I2`，未新增返修轮次 |
| **产品代码 / 契约 / 依赖** | **零变更** | 未修改任何产品源码、Tauri、Python Core、依赖或契约 |
| **被阻塞 Task 文件** | **零变更** | 未修改 `doc/tasks/P02-NEW-TIME-X6-AC1-AC7.md` |
| **证据保存** | **版本化隔离** | 证据写入 `verification/RES-P02-AC6-CDP-RECOVERY/`，未覆盖 I1/I2 既有文件，采用 `COPYFILE_EXCL` |

---

## 5. 推荐下一步

由于当前障碍属于 Windows 主机交互桌面/会话级窗口创建限制（`ERROR_INVALID_WINDOW_HANDLE`），建议下一步操作：
1. **用户侧环境恢复动作**：
   - 确保当前用户桌面处于交互式登录前台状态（非远程桌面断开会话、非锁屏挂起状态）；
   - 或重启主机以清除会话层残留的窗口站/桌面句柄状态；
2. **在恢复交互桌面后重新触发探测**，或由 Coordinator / Codex 将该环境缺陷裁定为外部主机环境限制。
