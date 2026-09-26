# M2-S1 固定点与环境记录（Owner 独立核验）

原始转录：[`raw/00-recon.log`](raw/00-recon.log)（由 `probes/00_recon.ps1` 生成）。
本文件是转录的可读摘要；如两者不一致，以转录与 `git` 实测为准。

## 1. Clone 形态（判定：可用，未触碰 G:）

| 命令 | 实测输出 | 判定 |
|---|---|---|
| `git rev-parse --show-toplevel` | `C:/Users/49745/.codex/worktrees/M2-S1-dsh-resource-channel` | 预期 C: 工作区 |
| `git rev-parse --git-dir` | `.git` | 本地 |
| `git rev-parse --absolute-git-dir` | `C:/Users/49745/.codex/worktrees/M2-S1-dsh-resource-channel/.git` | 本地 |
| `git rev-parse --git-common-dir` | `.git` | 本地 |
| `.git/commondir` 是否存在 | `NO (standalone clone)` | **非 linked worktree** |
| `.git/objects/info/alternates` | `NO` | 非共享对象库 |
| `git worktree list` | 仅本 clone 一行 | 未创建/删除 worktree |
| `.git/config` 的 `remote.origin.url` | `G:/CODEX/New Manga` | 仅 remote 指向 G:；git 目录与对象均在 C: |

释放证据（`origin/master:verification/M2-S1/release-85a2aa7.md`）记录的创建方式为
`git clone --no-local --branch master --single-branch G:/CODEX/New Manga` 后
`git switch -c agent/deepseek/M2-S1-resource-channel-spike`；本次核验与之一致。

**结论：元数据未指向 G: 作为 git 目录，base/branch 与 Task 一致，无 `BLOCKED` 条件。**
M2-C1 的 Owner/Review worktree 与全部审计证据未被读写。

## 2. 固定点

| 项目 | 值 |
|---|---|
| `HEAD` | `85a2aa7fd07a2dca843bf5cea3ec34070b63bdbc` |
| branch | `agent/deepseek/M2-S1-resource-channel-spike` |
| 开始工作时 `git status --porcelain` | 空（clean） |
| `HEAD:doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` | `4b503a170ff8ff6e995e5e5d70e3a053f9cc62c3` |
| 同上（base 与 `origin/master` 三方） | 三者相同 |
| `refs/remotes/origin/master` | `610f99dc79923e0be48c5b5dd633ff4facfb40e4`（Codex 释放提交，**未 merge**） |
| base 处的 `verification/M2-S1/` 已有文件 | 仅 `scheduler-registration-0c2e202.md`（Codex 范围登记，未修改） |

## 3. 执行环境

| 项目 | 值 |
|---|---|
| OS | `Microsoft Windows NT 10.0.26200.0`（Windows 11 24H2/25H2 家族） |
| Shell | PowerShell 7.6.6，`LanguageMode=FullLanguage`（workspace-write） |
| Python | 3.14.6（`C:\Python314\python.exe`；MSC v.1944 64-bit） |
| 处理器 | `AMD64 Family 25 Model 97 Stepping 2, AuthenticAMD`，32 逻辑处理器 |
| 物理内存（运行时探测） | 总计 32407.0 MB，可用 9063.9 MB，`memory_load=72%` |
| Pagefile | 总计 65175.0 MB，可用 26668.3 MB |
| C: 磁盘 | 已用 487.63 GB，可用 442.76 GB |
| 用户/域 | `49745 / HOME-MY`（同用户同会话；这决定了 C2 的 ACL 观测范围） |
| Lab 目录 | `%TEMP%\m2s1-lab`（`C:\Users\49745\AppData\Local\Temp\dsh-K8Ki2H\m2s1-lab`） |
| `M2S1_MAX_MEDIA_BYTES` | `67108864`（64 MiB，**探针配置**，非产品阈值） |

内存说明：可用物理内存约 9.0 GB 且系统负载 72%，因此所有探针都设置了**受控拒绝上限**，并在
`probe_d` 的 naive 对照中只做**一次** 75.9 MB 资源的最坏情况测量（实测进程峰值 385.6 MB），
未使用任何耗尽物理内存的失败路径。

## 4. 只读性声明

- 本核验只执行 `rev-parse` / `status` / `log` / `ls-files` / `ls-tree` / `remote` / `worktree list` 与文件读取。
- 未 `fetch`、未 `merge`、未 `push`、未创建或删除 worktree、未改动其他 Agent 的未提交内容（开始时 workspace 完全干净）。
