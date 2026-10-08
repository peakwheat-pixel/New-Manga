## P01 只读执行预检报告

### 结论
**本会话无法执行任何 shell 命令**：DSH 的 `pwsh` 沙箱在初始化阶段（为工作区授予写权限 ACL）即失败，命令在启动前就被拒绝。因此第 1–8 项全部为 **NOT_RUN**，没有任何命令产生 exit code。

阻断原因（三次独立尝试，结果完全一致）：
```
Error: SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga)
```
一次提权重试也被拒绝：`sandbox escalation to "danger-full-access" requires approval, but no approval channel is available`。

注意：目标路径**不是** denied/missing，本会话也**没有**改用 canonical main checkout 替代。

### 逐条结果（command / 工作目录 / 结果 / exit code）

| # | 命令 | 工作目录 | 结果 | exit code |
|---|---|---|---|---|
| 1 | `Get-Location`；`Test-Path -LiteralPath "G:\CODEX\New Manga.worktrees\P01-metadata-audit-codex"` | 未能确定（`Get-Location` 未执行；运行时声明为 `G:\CODEX\New Manga`，未经验证） | NOT_RUN（沙箱 ACL 初始化失败） | 无 |
| 2 | `cmd /c dir "G:\CODEX\New Manga.worktrees\P01-metadata-audit-codex"` | 同上 | NOT_RUN（同上） | 无 |
| 3 | `git -C "G:\CODEX\New Manga.worktrees\P01-metadata-audit-codex" rev-parse HEAD` | 同上 | NOT_RUN，**未能核对** `06f52f5a644079afeb57abb38f0ac674c02531c8` | 无 |
| 4 | `git -C 同一路径 show -s --format=%T HEAD` | 同上 | NOT_RUN，**未能核对** `d868ecf40b4724227b74686e666f6005428e7b88` | 无 |
| 5 | `git -C 同一路径 status --porcelain=v1 --no-optional-locks` | 同上 | NOT_RUN，**未证实**工作区为空 | 无 |
| 6 | `git -C 同一路径 merge-base --is-ancestor 826bea1… 06f52f5…` | 同上 | NOT_RUN | 无 |
| 7 | `git -C 同一路径 diff --check 826bea1…06f52f5…` | 同上 | NOT_RUN | 无 |
| 8 | `python -B -X utf8 "G:\CODEX\New Manga.worktrees\P01-metadata-audit-codex\verification\PROJECT-ROADMAP-20261008\verify_plan.py"` | 同上 | NOT_RUN，**未执行、无 exit code** | 无 |

第 8 项说明：该 validator 的路径**确实属于 P01 linked worktree**（不是 canonical main checkout），但脚本从未被执行，因此不能给出退出码。

### 附加事实（非上述 8 条命令，仅为只读文件系统工具观测）
- 文件系统工具可读取该 linked worktree：`G:\CODEX\New Manga.worktrees\P01-metadata-audit-codex` 下可枚举 7378 个文件（仅展示前 100 个）。
- 第 8 项指定的脚本文件存在且可读：`…\verification\PROJECT-ROADMAP-20261008\verify_plan.py`（共 120 行，首行注释为 `"""Validate this fixed planning snapshot; does not run product tests."""`）。
- 以上仅为路径存在性/可读性证据，**不构成** SHA、tree、worktree 清洁度或 `merge-base` 的任何验证，不能替代第 3–7 项的 Git 结果。

### 边界声明
即使上述检查全部通过，也**只能证明只读执行访问能力**，**不构成对 P01 Review 的批准**。本次预检未做任何正式审查，未修改任何文件、Git index、分支、worktree、DSH 设置或仓库状态。

### 推荐下一步
在具备可用审批通道、或工作区 ACL 可写（不再触发 `SetNamedSecurityInfoW Win32 5`）的环境中重新启动 DSH 会话，并原样重跑本 1–8 条命令；在此之前不要用 canonical main checkout 或其它替代路径得出结论。