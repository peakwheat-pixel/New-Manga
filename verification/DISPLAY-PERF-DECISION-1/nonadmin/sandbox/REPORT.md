# DISPLAY-PERF-DECISION-1 / AC11 —— 干净机复核「非管理员启动时 Core 不启动」

- 父任务：`DISPLAY-PERF-DECISION-1`（AC11）；本任务：`task-6`；Owner：`sandbox-verify`（DSH teammate）
- 日期：2026-10-26 22:31–23:55（Asia/Shanghai）；本机 `HOME-MY\49745`，Windows 11 `10.0.26300`（26H2），G: 本地 NTFS 固定盘
- 被测二进制：**pinned baseline**，`new-manga.exe` SHA-256 `1136BB0A…3226`、`core_service.exe` SHA-256 `E0A1EFF8…14BC0`（与 `target/release/resources/core-sidecar` 逐字节一致）
- 结论状态：**H1 判定成立（本机环境/机器级强制标签所致，非产品缺陷）**；干净机（Windows Sandbox）已完成机制判定实验，非提权（Medium）矩阵为 PARTIAL（见 §7）
- 未修改任何产品源码/配置/依赖；未启用/安装任何软件；未改本机安全策略；测试结束已关闭 Sandbox/VM，本机无残留进程（§8）

---

## 1. 结论摘要（TL;DR）

| 问题 | 答案 |
|---|---|
| 谁把非管理员时的 sidecar 降到 Low？ | **不是产品，也不是"按映像匹配的策略"**：是**文件系统自带的 Low 完整性强制标签（mandatory label）**。`G:\CODEX\New Manga`（仓库根）带 `Mandatory Label\Low Mandatory Level:(OI)(CI)(NW)`，全仓库文件继承该标签；本机在启动带 Low 标签的映像时，子进程令牌被置为 **Low (0x1000)**。 |
| 为什么只有 3 个 PyInstaller sidecar 看起来"被降级"？ | RCA 的采样路径偏差：sidecar 从**仓库内**（带 Low 标签）启动，而 `cmd/python/notepad` 从 `C:\Windows\System32`（无标签）启动。同一 sidecar 复制到无标签路径即为 Medium。 |
| 干净机是否复现？ | 在**全新 Windows Sandbox** 中用同一 pinned baseline：无标签副本 → 进程 **High**、Core **启动成功**（`[core.derived_gc]` + `.preview-lifecycle.lock` + `catalog.sqlite`）；同一文件**人为加 Low 标签** → 进程 **Low**、Core **以完全相同的 `win32 error 5` 失败**。干净机无任何仓库/沙箱账户痕迹。 |
| 判定 | **H1 机器策略/环境**。产品侧无缺陷；AC9 修复归属 = 环境侧清理 Low 强制标签（拷贝/重新构建即消失）+ 产品侧只做「可诊断 + 优雅失败」（RCA §6-B1）。 |

---

## 2. 决定性证据：Low 令牌来自文件的 Low 强制标签

### 2.1 仓库根标签 & ACL 签名

```
G:\CODEX\New Manga                        => Mandatory Label\Low Mandatory Level:(OI)(CI)(NW)
G:\CODEX\New Manga\apps\desktop\...\release\resources\core-sidecar => Mandatory Label\Low Mandatory Level:(I)(OI)(CI)(NW)
  core_service.exe                          => Mandatory Label\Low Mandatory Level:(I)(NW)
  new-manga.exe (release)                   => Mandatory Label\Low Mandatory Level:(I)(NW)
pinned-baseline\new-manga.exe               => Mandatory Label\Low Mandatory Level:(I)(NW)     # 复制时带上了标签
pinned-baseline\resources\core-sidecar\core_service.exe => (无标签)                            # RCA 应用失败的真因：app 自身 Low → 子进程继承 Low
sandbox\payload\...\core_service.exe        => (无标签)                                         # 本轮 payload 副本
```

release 目录 SACL 还带 `HOME-MY\CodexSandboxUsers`、`S-1-4-…`（AppContainer）ACE、`(D;CIID;DT;;;WD)` deny-delete 等，与**本机 Agent 沙箱/工作区保护工具**的写入签名一致（不是产品安装包的一部分）。

### 2.2 对照实验（同一 pinned baseline `core_service.exe`，同一 Medium 非提权父进程；explorer-DDE 启动的 Medium PowerShell，与 RCA 同通道）

| # | 被测文件位置 | Low 标签 | 子进程令牌 | Core 结果 |
|---|---|---|---|---|
| 1 | `apps\desktop\...\target\release\...\core_service.exe`（仓库内，RCA 原路径） | **有** | **0x1000 Low** | **失败**（无 GC、无 lock/catalog） |
| 2 | `pinned-baseline\resources\core-sidecar\core_service.exe` | 无 | 0x2000 Medium | 成功（GC + lock 429B + catalog） |
| 3 | `sandbox\payload\resources\core-sidecar\core_service.exe` | 无 | 0x2000 Medium | 成功 |
| 4 | `sandbox\work\copytest\core_service.exe`（全新拷贝） | 无 | 0x2000 Medium | 成功 |
| 5 | `sandbox\work\labeltest\core_service.exe`（无标签副本 **手工** `icacls /setintegritylevel Low`） | **有** | **0x1000 Low** | **失败**（与 RCA 一致） |

> 1 号路径复测 3 次全部 Low（`explorer-dde-release`、`-re1`、`-re2`）；无标签副本复测 4 次全部 Medium+成功。
> 结论：**唯一变量是文件自身的 Low 强制标签**，与代码、manifest、PyInstaller、父进程提权状态无关。

---

## 3. Windows Sandbox 干净机判定（决定性含标签对照）

Windows Sandbox（`Containers-DisposableClientVM=Enabled`，包 `MicrosoftWindows.WindowsSandbox 0.8.107.0`）自建干净 VM：

- guest OS build `26100.9711`，用户 `WDAGUtilityAccount`，`EnableLUA=0`（沙箱内无 UAC 过滤令牌，全部进程 High，RCA 意义上的"非提权"在沙箱内不存在，见 §7）
- guest 内无 `CodexSandboxUsers`、无仓库 ACL/标签痕迹（干净机）
- payload 通过 guest→host TCP 注入（`.wsb` mapped folder 在本机不可用，见 §7）；guest 内校验 **zip SHA-256 一致**，解压后 `core_service.exe`/`new-manga.exe` SHA-256 与 pinned baseline **逐字节一致**

同一 guest、同一 exe、同一 High 上下文，只改变 Low 标签：

| 步骤 | 子进程令牌 | Core 结果 | 证据 |
|---|---|---|---|
| 中性副本（无标签） | **0x3000 High** | **成功**：stderr `[core.derived_gc] orphan_files_removed=0 dead_rows_removed=0`；`.preview-lifecycle.lock`(261B)；`catalog.sqlite` 生成 | `evidence/sbx-clean-machine-mini-result.trimmed.json` |
| 同一文件 `icacls /setintegritylevel Low` | **0x1000 Low** | **失败**：`handle_resolver.py … open_exclusive_lock_for_initialize … TypedResourceChannelError: preview namespace unavailable: namespace lock open failed (win32 error 5, exclusive=True)`；无 lock/catalog | 同上 |

→ 干净机上一个**完全没有本机沙箱痕迹**的环境，仅凭文件 Low 标签即可复现 RCA 的全部现象；去掉标签即可通过。**H1 成立。**

---

## 4. 与父任务 RCA 的对账

RCA 的令牌矩阵（§4-E6）被本文修正/补全：

| RCA 观测 | 本文解释 |
|---|---|
| release 路径 sidecar = Low；`cmd/python/notepad` = Medium | sidecar 从仓库内（Low 标签）启动；系统工具从 `C:\Windows\System32`（无标签）启动。按文件标签解释，无需"按映像/来源匹配的低完整性策略"假设 |
| `pinned-baseline\new-manga.exe` 非提权 app 启动失败（stderr 有 win32 error 5） | `pinned-baseline\new-manga.exe` **本身带 Low 标签**（复制时随源标签保留/被标签化）→ app 进程 Low → 其派生的 core/host sidecar 继承 Low → 与 RCA 应用侧失败一致；而 `pinned-baseline` 里的 `core_service.exe`（另有拷贝路径）无标签 |
| 提权（High）时一切正常 | High 令牌不受文件 Low 标签限制（本机行为：Low 标签仅把**新建进程的令牌**降为 Low；High 上下文实测仍为 High？——注意：本机实测 release 路径在 **Medium** 上下文被降为 Low；在 **High** 上下文 release 路径曾返回 `token-frozen-core-admin.json` = High，与本机"标签→子进程 IL"行为在 High 父上下文不生效一致） |

**谁设置的低标签**：仓库根 `G:\CODEX\New Manga` 上的 `Low Mandatory Level:(OI)(CI)(NW)` + 目录 SACL 的 `CodexSandboxUsers`/AppContainer/deny-delete 签名，指向本机 **Agent 沙箱/工作区保护**（DSH/Codex 类工具的写入路径）；属于**机器/工作区状态**，不是产品分发内容（pinned baseline 的 zip 副本、任意新拷贝都无标签且行为正常）。

---

## 5. 修复归属建议（AC9）

1. **环境侧（根因，优先）**：清掉仓库根/构建目录的 Low 强制标签即可让非提权启动恢复正常，例如把发布物复制到未标记目录（本轮 2–4 号样本即证明），或由工具链在产出后 `icacls <path> /setintegritylevel Medium`（**属于用户环境操作，本任务未执行**）。
2. **产品侧（最小、低风险）**：只保留 RCA §6-B1 的「可诊断 + 优雅失败」——spawn 后读子进程令牌，与父进程 IntegrityLevel 比较并给出显式错误（当前只有被 GUI 吞掉的 `[startup] WARNING`）。**不建议**修改产品去适配 Low 标签（`S:(ML;;NW;;;LW)` 之类会削弱数据目录保护）。
3. 该问题属旧架构（Tauri/WebView2）基线；按 AD-002，后续只把「Core 启动失败必须可诊断、不许静默 panic」转化为新架构（Avalonia + Python Core Host）需求，不在旧架构释放修复任务。

---

## 6. 复现命令（关键步骤）

```powershell
# 父上下文：Medium 非提权（与 RCA 相同通道：explorer DDE 启动 .lnk -> powershell）
#   -> 脚本内用 Start-Process 启动 core_service.exe，隔离 env，测令牌
# 本任务脚本：G:\CODEX\New Manga.workspace\task-envs\DISPLAY-PERF-DECISION-1\sandbox\work\recheck.ps1
#   参数 -Label <name> -CorePath <exe>；由 run-recheck.ps1 生成 .lnk 并用 explorer.exe 启动
# 手工复现 Low 标签：
icacls <exe> /setintegritylevel Low      # 加标签 -> 复现 Low+fail
icacls <exe> /setintegritylevel Medium   # 去除标签 -> 恢复 Medium+success
```

Windows Sandbox 复现链（干净机）：`run-mini.wsb` + `work/run-probe-runner.ps1`（guest 内 `stage/bootstrap-mini.ps1`：TCP 取 payload → 校验 SHA → 中性副本/加 Low 标签两份对照 → 上报结果）。

---

## 7. 限制 / BLOCKED（诚实标注）

1. **沙箱内没有"非提权"上下文**：Windows Sandbox guest `EnableLUA=0`，所有进程 High（`elevationType=1`），无法直接测 Medium 令牌；本轮改用"High 上下文 + 文件 Low 标签"做机制判定（§3），Medium 上下文对照在**宿主机**完成（§2.2 表 1/2/5）。二者组合覆盖了"标签→令牌→Core"全链。
2. **Windows Sandbox `.wsb` MappedFolder 在本机完全不可用**：guest `Test-Path C:\payload/C:\out=False`、`Get-PSDrive` 只有 C:，25s/85s 两次采样一致；即使换 C: 源目录、并以**非提权** WSB 客户端（explorer 启动，client token=Medium）亦然。故改用 guest→host TCP 通道（已验证：1.28GB payload 传输约 2s、SHA 校验通过），不影响判定结论，但说明本机 WSB/工作区保护存在额外限制。
3. **guest 内 WMI 不可用**：`Get-CimInstance Win32_Process` 在 guest 内返回空/长时间卡死；探针已改为 `Get-Process` + 创建时间发现进程（宿主机同样可用）。
4. **完整 probe（含 app 冷启动、schtasks 降权兜底）一轮在 guest 内挂起 >20min 未产出**（round 3，23:42–00:04），已终止；因此 app 级（窗口/panic）干净机证据缺失。round 1 中 guest 已跑到 elevated 阶段（因探针自身 catalog 目录 bug 失败，非 guest 问题），round 4（本文 §3 判定实验）完整成功。
5. **"Low 标签→子进程 Low"是否为 Windows 通用行为未在第三方干净机确认**：本机与 Windows Sandbox 均观测到该行为；但结论 H1 只依赖"标签是本机/工作区强加、产品副本无标签时正常"这一事实，不依赖该行为是否通用。

---

## 8. 资源与残留

- Windows Sandbox/VM：每次运行结束均已关闭；结束时 `WindowsSandbox*`/`vmwp`/`vmmemWindowsSandbox` 进程数 = 0，`hcsdiag list` 仅剩系统模板（`SavedAsTemplate`）；`Containers-DisposableClientVM` 状态保持 `Enabled`（未改动）。
- 本机残留：无 probe/服务端残留进程（19080 仅剩内核 TimeWait），临时目录 `C:\nm-wsb-test` 已删除；未创建/保留任何计划任务或本地用户（沙箱内的 `NMProbe` 用户仅在一次性 VM 内创建，随 VM 销毁）。
- 证据/中间产物：`G:\CODEX\New Manga.workspace\task-envs\DISPLAY-PERF-DECISION-1\sandbox\`（payload、stage、work、mini-out、sbx-out、*.wsb），全部为可删的派生产物。
- 剪贴板：本轮未写入用户剪贴板（未触碰）。

## 9. 证据索引

| 文件（`verification/DISPLAY-PERF-DECISION-1/nonadmin/sandbox/evidence/`） | 内容 |
|---|---|
| `host-recheck-token-matrix.json` | 宿主机 8 组对照（release/pinned/payload/copytest/labeltest）的 selfToken/coreToken/gc/lock/catalog |
| `mandatory-label-and-acl-snapshots.txt` | 仓库路径链、各 exe 的 SHA-256 + mandatory label、release 目录 SACL、release/pinned ACL 原文 |
| `sbx-clean-machine-mini-result.trimmed.json` | 干净机判定实验：中性副本 vs Low 标签副本的令牌/GC/lock/catalog + guest OS/UAC/payload SHA |
| `sbx-clean-machine-mini-bootstrap.log` / `-server.log` | guest 侧时间线（下载/校验/解压/两轮测试）与 host TCP 传输记录 |
| `sbx-server-all-rounds.log`、`residue-check.json` | 沙箱服务器日志、残留检查 |
| （workspace 原始）`sandbox\mini-out\mini-result.json` | 干净机原始结果（931KB，含 whoami/icacls 全量） |
