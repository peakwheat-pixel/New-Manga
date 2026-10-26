# 非管理员（非提权）启动时 Core 不启动 —— RCA（AC9 / task-4）

- 父任务：`DISPLAY-PERF-DECISION-1`（AC9）
- Owner：`core-admin-rca`（DSH teammate）
- 结论状态：**已复现 + 根因链闭合到「sidecar 子进程被以 Low 完整性级别（Low IL）启动 → 对 Medium 级数据目录的写操作被强制完整性控制（MIC）拒绝 → Core 秒退」**；**上游「谁把令牌降到 Low」尚未最终定位**，标 PARTIAL（详见 §7）。
- 时间：2026-10-26 22:01–22:35（Asia/Shanghai）；本机 `HOME-MY\49745`，Windows 10.0.26300，本地 NTFS 固定盘 `G:`。
- 被测二进制：`pinned-baseline/new-manga.exe`，SHA-256 `1136BB0A8D582A30C6EF0B16959B86A62DD26D2C6D9CE49E298C9B86C3343226`（= 产品基线 exe；sidecar `host_bridge/core_service/acceptance_bridge/catalog_loader` 与 `target/release/resources/core-sidecar` 逐字节一致，已验证）。**未修改任何产品源码/配置/依赖。**

---

## 1. 结论摘要（TL;DR）

| 维度 | 事实 |
|---|---|
| 是否复现 | **是**，非提权 3 次（app×1、独立 core_service×2）、提权对照 2 次，结果稳定可重复 |
| 现象分类 | **b → a**：窗口**出现**（标题 `New Manga`，t≈2.2 s）→ Core 未就绪 → supervisor 3 次重启全失败 → 约 t≈20 s 应用 panic 退出（用户感知为"闪一下就没/只有壳"） |
| 直接原因 | Core 第一步 `initialize_namespace` 打不开/建不了 `<derived>\.preview-lifecycle.lock`，`win32 error 5 = ERROR_ACCESS_DENIED`；三种打开方式（独占 OPEN_EXISTING、独占 CREATE_NEW、以及预置空文件后）**全部被拒** |
| 关键中间事实 | 同一目录、同一 Medium 令牌下，用 sidecar 自带 CPython 复刻**完全相同的 CreateFileW 参数**（`access=0xC0000000, share=0, disposition=1/3, FILE_ATTRIBUTE_NORMAL`）→ **成功**；仓库源码 `initialize_namespace` 在 Medium 下也**成功** → **不是 ACL、不是路径、不是代码缺陷** |
| 根因（最强、已有直接证据） | **非提权启动时，三个 PyInstaller sidecar 子进程的令牌完整性级别是 Low（0x1000）**，而同一父进程下的 `python.exe / cmd.exe / notepad.exe` 是 Medium（0x2000）；提权父进程下 sidecar 是 High（0x3000）。Low IL 进程对 Medium IL 目录 `%APPDATA%\com.newmanga.desktop`（及其派生的 `derived/`、`catalog/`）**写操作属于 write-up，被 MIC 直接判 ERROR_ACCESS_DENIED**，与 ACL 无关（ACL 明确允许 `NT AUTHORITY\Authenticated Users:(M)`）。 |
| 影响 | 非提权冷启动 100% 失败（本机）；提权冷启动正常（与用户"以管理员身份启动才能用"一致） |

---

## 2. 复现步骤（可原样重放）

非提权通道（本会话是提权会话，必须去提权）：把 `.lnk`（指向 `powershell -File scripts/launch-probe.ps1 ...`）交给**已在运行的、Medium 完整性 explorer.exe** 启动；`explorer.exe` 的 DDE 转发会让目标以登录用户的**过滤令牌（Medium）**运行。已用 `probe-token.json` 自证：`user=HOME-MY\49745, isInRole(Administrator)=False, Mandatory Label\Medium Mandatory Level`。

```powershell
# 通道自证（非提权）
pwsh -File .../nonadmin/scripts/launch-via-explorer.ps1 `
  -ProbeArgs '-Mode shell -Label nonadmin-shell-01' ...
# 非提权 app 冷启动（隔离 env、75s 采样、结束时杀残留）
pwsh -File .../nonadmin/scripts/launch-via-explorer.ps1 `
  -ProbeArgs '-Mode app -Label nonadmin-app-01 -TimeoutSec 75' ...
# 提权对照（同 exe、同 env）
powershell -File .../nonadmin/scripts/launch-probe.ps1 -Mode app -Label admin-app-01 -TimeoutSec 75
```

隔离 env（每次启动全新目录，绝不触碰用户真实 `%APPDATA%`/媒体库）：
`M2RC1_PACKAGED=1, APPDATA=<run>/appdata-roaming, LOCALAPPDATA=<run>/appdata-local, TEMP/TMP=<run>/tmp, NEWMANGA_DATA_ROOT=<run>/data-root, M2RC1_DERIVED_ROOT=<run>/scope/derived, M2RC1_MANAGED_ROOT=<run>/scope/managed, M2RC2_CATALOG_DB=<run>/catalog/catalog.sqlite, WEBVIEW2_USER_DATA_FOLDER=<run>/webview2-udd`（脚本内置隔离断言，越界即 exit 90）。

复现脚本：`nonadmin/scripts/{launch-probe.ps1, launch-via-explorer.ps1, token-probe.ps1, child-token-probe.ps1, lock-call-probe.py, python-lock-probe-wrapper.ps1, repo-core-namespace-probe.py, repo-core-probe-wrapper.ps1}`（位于 `G:/CODEX/New Manga.workspace/task-envs/DISPLAY-PERF-DECISION-1/nonadmin/scripts/`）。

---

## 3. 现象时间线（非提权 app 冷启动，`nonadmin-app-01`）

| t (s) | 事件 | 证据 |
|---|---|---|
| 0.0 | `new-manga.exe` 启动（Medium）、`host_bridge.exe` 启动 | `host.log`、`samples.json` |
| ~1.0 | `core_service.exe` 首次启动 → 立即失败退出 | `app.stderr.log` 第 1 段 traceback |
| **2.2** | **窗口出现**：`MainWindowHandle=5771214`，标题 `New Manga` | `samples.json` |
| 2.2→16.5 | 窗口存活；后台 supervisor 重试 2/3、3/3，均失败 | `app.stderr.log` |
| ~17 | `host_bridge.exe` 失败：`catalog database does not exist (unbound namespace; run the controlled initializer first)` | 同上 |
| **~20** | `new-manga.exe` panic 退出：`Failed to setup app: ... failed to create webview: WebView2 error: WindowsError(0x8000FFFF 灾难性故障)`，无残留进程 | 同上；`samples.json` 最后一条 `alive=False` |

Core 侧实际报错（非提权，逐字）：

```
FileNotFoundError: <run>\scope\derived\.preview-lifecycle.lock
...
  File "...handle_resolver.py", line 1041, in open_exclusive_lock_for_initialize
  File "...handle_resolver.py", line 903, in _open_lock_handle
TypedResourceChannelError: preview namespace unavailable:
  namespace lock open failed (win32 error 5, exclusive=True)
[PYI-xxxxx:ERROR] Failed to execute script 'entry_core_service' due to unhandled exception!
[startup] WARNING: initial core_service startup failed (CORE_UNAVAILABLE: production core startup ping timed out or failed ...); supervisor will recover
```

提权对照（`admin-app-01`，同 exe、同隔离 env）：`[core.derived_gc] orphan_files_removed=0 dead_rows_removed=0`，窗口标题持续 75 s，`catalog/catalog.sqlite`(24576B)+`data-root/library.db`+WAL 正常生成，**0 次重启、0 traceback**。→ **本问题与提权强相关，不是 env/参数的差异。**

---

## 4. 根因链（证据逐环闭合）

1. **非提权 → sidecar 令牌 = Low IL（决定性，E6）**
   用 P/Invoke 读子进程令牌（`child-token-probe.ps1`，`OpenProcessToken`+`GetTokenInformation(TokenIntegrityLevel)`）：

   | 父上下文 | 子进程 | 完整性级别 |
   |---|---|---|
   | Medium（非提权 explorer→powershell） | `core_service.exe` | **0x1000 Low** |
   | 同上 | `host_bridge.exe` | **0x1000 Low** |
   | 同上 | `acceptance_bridge.exe` | **0x1000 Low** |
   | 同上 | sidecar 自带 `python.exe` | 0x2000 Medium |
   | 同上 | `cmd.exe` | 0x2000 Medium |
   | 同上 | `notepad.exe` | 0x2000 Medium |
   | High（提权 powershell） | `core_service.exe` | 0x3000 High |

   重复测量一致（`token-core-medium-repeat.json`）；`appContainer=0`、`tokenType=1`。→ **不是 AppContainer，就是一个被降到 Low 的普通受限令牌**，且只发生在三个 PyInstaller sidecar 上。

2. **Low IL → 数据目录写被 MIC 拒绝**：`%APPDATA%\com.newmanga.desktop`（= `packaged_user_root()`，main.rs:1540-1544）以及 `derived/`、`catalog/` 都是 Medium IL 目录；Low 进程创建/独占可写打开文件属于 **write-up**，内核直接返回 `ERROR_ACCESS_DENIED(5)`，**与 DACL 无关**。这与 §5 的排除证据（DACL 允许 `Authenticated Users:(M)`、Medium CPython 创建同一文件成功）完全自洽。

3. **Core 因此秒退**：`bootstrap/core_service.py:4604 → _ensure_preview_namespace → catalog_store.initialize_namespace(catalog_store.py:211) → open_exclusive_lock_for_initialize(handle_resolver.py:1033-1042) → _open_lock_handle(876-915)` 第一步即失败，进程 `[PYI-…:ERROR]` 退出。

4. **首次绑定失败 → 后续全崩**：Core 不启动 ⇒ catalog 从未初始化 ⇒ `host_bridge.exe` 以 `catalog database does not exist` 退出；`StdioCoreChannel::spawn_packaged` 只判 spawn 成功（不判子进程存活），所以不在这里 panic；library channel supervisor 3 次重试全部失败；随后 Tauri setup 里创建 WebView2 失败（`0x8000FFFF`）触发 panic → **整体退出**（用户看到"窗口闪一下/只有壳"）。

5. **为什么用户会感知为"Core 不启动"**：提权时 High 令牌可写 Medium 目录，一切正常；非提权时 Low 令牌被 MIC 拒绝，Core 从不曾就绪。

> 预置空 `.preview-lifecycle.lock` 再非提权启动（`nonadmin-core-02`）**仍然 error 5**，且失败点前移到 `_open_lock_handle` 的**独占 OPEN_EXISTING**（第 1039 行）→ 说明不是"CREATE_NEW 特例"，而是**该进程对整个文件的一切写/独占访问都被拒**，与 write-up 结论一致。

---

## 5. 已排除项（逐项 + 证据）

| 候选 | 结论 | 证据 |
|---|---|---|
| exe 清单强制提权 | **排除** | `new-manga.exe` 清单无 `requestedExecutionLevel`；四个 sidecar 均为 `asInvoker`，无 `autoElevate`（`core_service.exe` 清单全文已 dump：trustInfo/compatibility/Common-Controls/longPathAware，无提权项） |
| 目录 ACL / 所有权 / Deny ACE | **排除** | `%APPDATA%\com.newmanga.desktop` 及 `derived/`：`NT AUTHORITY\Authenticated Users:(M)`（继承），无 Deny；隔离 run 目录同样。Medium CPython 在同一目录创建/删除 `.preview-lifecycle.lock` **成功**（`token-probe-medium.txt`、`python-lock-medium.stdout.json`） |
| 代码缺陷（锁逻辑/参数） | **排除** | 用 sidecar 自带 CPython 3.12.3 + 仓库 `src` 在 **Medium** 下直接跑 `catalog_store.initialize_namespace()` → **成功返回 binding**（`repo-core-medium.stdout.json`）；同参数裸 CreateFileW 6 个变体在 Medium 下除"文件已存在(80)"外全部成功 |
| G: 是映射/网络盘 | **排除** | `Win32_LogicalDisk DriveType=3`（本地固定盘）、NTFS、无 ProviderName |
| Defender 实时保护/ASR/受控文件夹访问 | **排除** | `Get-MpComputerStatus` 正常但 `EnableControlledFolderAccess=0`、无 ASR 规则；Defender Operational 24h 内仅健康/SI 更新/扫描，无拦截；Application 日志无 Application Error/Hang/WER 记录；CodeIntegrity 仅 nvspcap64.dll 历史记录；AppLocker 4 个日志 RecordCount=0 |
| AppCompat 兼容层 / IFEO | **排除** | HKCU Layers 无 sidecar 条目、HKLM Layers 空、三个 sidecar 无 IFEO 项 |
| sidecar 文件带 Low IL 标签 | **排除** | 三个 sidecar 的 SACL `S:AI`（纯继承，无 `ML;...;LW` 标签） |
| catalog 缺失（治理假设） | **排除为主因** | catalog 由 Core 首启创建（提权对照成功生成 24576B）；非提权失败发生在创建 catalog **之前**的锁阶段 |
| PyInstaller 解包/文件锁/端口/DPAPI/防火墙 | **未发现证据** | 非提权时 Core 已在 Python 层执行到 `initialize_namespace`（有完整 traceback），说明解包/启动链正常；无端口/凭据相关日志 |

---

## 6. 最小修复方案（只给方案，未改产品代码）

**A. 环境侧（首选，若 Low IL 来自本机安全/沙箱组件）**
把三个 sidecar（`core_service.exe / host_bridge.exe / acceptance_bridge.exe`，可加 `catalog_loader.exe`）从"低完整性策略/沙箱策略"中放行，使非提权启动时令牌为正常 Medium。判定与操作：
1. `Get-ProcessMitigation -PolicyFilePath` / `Get-CimInstance -ClassName Win32_DeviceGuard` + `GPResult /h` 复核是否有进程缓解/完整性策略；
2. 若确认由本机 sandbox 痕迹（本机存在 `HOME-MY\CodexSandboxUsers`、`S-1-5-21-…`/`S-1-4-…` 等非标准 ACE）引入，则清理该沙箱对 `core-sidecar` 的策略，而不是改产品。

**B. 产品侧（若 A 不可行 / 需兼容此类环境）——建议位置**
1. **启动前自检 + 显式诊断（最小、低风险）**：`apps/desktop/src-tauri/src/core_bridge.rs::spawn_packaged` 与 `library_bridge.rs::spawn_with_startup_ping` 在 spawn 后（或首次 ping 失败时）读取子进程令牌完整性级别（`OpenProcessToken`+`TokenIntegrityLevel`），与父进程比较；若子 < 父，日志/弹窗给出明确错误（当前只有 `[startup] WARNING` 且被 GUI 吞掉，用户完全无感）。这是让 AC9 可诊断的最小改动。
2. **降级可用的真正修复**：在 `main.rs:1598-1647` 创建 `derived/managed/catalog/data` 之后，**为这些目录显式设置允许 Low IL 写入的强制标签**（`SetNamedSecurityInfo` 写 SACL `ML;;NW;;;LW`，或直接 `S:(ML;;NW;;;LW)`），即"数据目录对低完整性进程可写"。副作用：削弱这些目录的防降级保护，应为**临时 workaround**，且必须在允许后重新回归提权路径。
3. **不推荐**：让 sidecar 走 `--uac-admin`/服务化来强制提权（改变产品安全姿态，且与"不高权运行"目标冲突）。

**C. 回归验证（AC9 验收口径）**
- 非提权连续 3 次冷启动：窗口出现 ≤5 s；`core_service.exe` 存活 ≥60 s；`%APPDATA%\com.newmanga.desktop\{catalog\catalog.sqlite, data\library.db, derived\.preview-lifecycle.lock}` 全部生成；stderr 无 traceback、无 `supervisor restart`。
- 提权 3 次对照：同样全部通过（防止修复引入回归）。
- 每次保留：进程树采样、app.stderr、子进程令牌报告（`child-token-probe.ps1`）、事件日志切片。

---

## 7. 未闭合 / BLOCKED 项

**BLOCKED（PARTIAL）**：「谁把非提权时的 sidecar 令牌降到 Low」尚未定位。已排除 exe 清单、兼容层、IFEO、文件 IL 标签、ACL、AppContainer（`appContainer=0`）与产品代码；剩下三类候选：

1. **本机安全/沙箱组件**（最可疑）：本机存在 `HOME-MY\CodexSandboxUsers` 组与非标准 SID 的 ACL 痕迹，且正好只有 **PyInstaller 未签名 sidecar**（而非 python/cmd/notepad）被降级——符合"按映像/来源匹配的完整性策略"特征（如 EDR/SRP/沙箱的 low-integrity 规则）。
2. **PyInstaller bootloader 在非提权下的异常行为**（需干净机器复验；本机无法排除机器级策略污染）。
3. 组策略/EDR 的进程缓解策略（`Get-ProcessMitigation`、`GPResult`、EDR 控制台日志）。

**需要的证据/环境**：一台**无本机沙箱痕迹的干净 Windows** 重复 §4-E6（1 次即可判定）；或在受影响机用 Procmon 捕获 `CreateFile` 计划（需要能装 Sysinternals；本机没有 procmon）与 EDR 策略导出。

判定后：若 1 成立 → 修复在环境/策略侧（§6-A），产品只需加 §6-B1 诊断；若 2/3 成立 → 按 §6-B2 落产品修复。

---

## 8. 证据清单（本目录 `evidence/`，均为非提权/提权实跑产物）

- `nonadmin-app-01.{app.stderr.log,samples.json,host.log,probe-token.json,launch-env.json}` —— 非提权 app 冷启动全量（窗口时间线、traceback、panic）
- `admin-app-01.{app.stderr.log,host.log,probe-token.json,launch-env.json}` —— 提权对照（同 exe/同 env，成功）
- `nonadmin-core-01.{app.stderr.log,run-summary.json}`、`nonadmin-core-02.precreated-lock.app.stderr.log` —— 冻结 `core_service.exe` 单独非提权、预置锁后仍失败
- `admin-core-01.app.stderr.log` —— 冻结 sidecar 提权对照（成功建锁 403B）
- `token-frozen-core-medium.json` / `token-frozen-core-admin.json` / `token-core-medium-repeat.json` / `token-{host,acceptance,python,cmd,notepad}-medium.json` —— **Low/Medium/High 令牌矩阵（核心证据）**
- `token-probe-medium.{txt,json}`、`python-lock-medium.stdout.json` —— Medium 令牌下同目录同参数 CreateFileW 成功（排除 ACL）
- `repo-core-medium.stdout.json` —— 仓库源码在 Medium 下 `initialize_namespace` 成功（排除代码缺陷）

复现/取证脚本与全部 run 原始产物在 `G:/CODEX/New Manga.workspace/task-envs/DISPLAY-PERF-DECISION-1/nonadmin/{scripts,runs}/`。所有启动均隔离 env，未触碰用户真实 `%APPDATA%`/媒体库/产品代码；无残留进程、无临时计划任务。
