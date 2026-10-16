# UI-DESIGN-1 selfcheck — PowerShell 执行 BLOCKED 记录

按 Task 指示登记：可复现脚本 `selfcheck.ps1` 已交付，但在 Owner 会话中**无法执行**，
因为 harness 权限层拒绝了全部 PowerShell 调用。未伪造任何脚本输出。

## 被拦命令与错误原文

以下 6 次调用（Owner 直跑 3 次 + general-purpose 子代理 3 次）全部在执行前被拒，
错误原文完全一致：

```
No permission client configured for Bash
```

| # | 命令 | 途径 |
|---|---|---|
| 1 | `powershell -NoProfile -ExecutionPolicy Bypass -File "verification/UI-DESIGN-1/selfcheck.ps1"` | Owner Bash |
| 2 | `powershell -NoProfile -ExecutionPolicy Bypass -File "G:/CODEX/New Manga.workspace/worktrees/UI-DESIGN-1/verification/UI-DESIGN-1/selfcheck.ps1"` | Owner Bash |
| 3 | `powershell.exe -NoProfile -ExecutionPolicy Bypass -File verification/UI-DESIGN-1/selfcheck.ps1` | Owner Bash |
| 4–6 | 同 1–2 + `pwsh -NoProfile -ExecutionPolicy Bypass -File verification/UI-DESIGN-1/selfcheck.ps1` | 子代理（agent_bab2c908） |

同会话中简单白名单命令（`git status --porcelain`、`grep`、`ls`、`echo`）可正常执行；
复合命令（`&&`、`for` 循环、输出重定向 `>`）同样被拒。判定为权限客户端缺失而非脚本本身问题。

## 已采取的替代措施（不伪造）

`selfcheck-output.txt` 中的日志由**等价白名单 bash 命令**（grep/git/ls/sort/uniq）产生，
其原始输出已逐字转录入库，并在日志头部显式标注了生成方式与本 BLOCKED 事实。
四项检查（(a) 契约名逐字命中 / (b) 本地链接解析 / (c) git 写入范围 / (d) 结构打勾）
在等价运行下全部 PASS。

## 交由 Reviewer 的复跑

在权限客户端可用的环境中，于 worktree
`G:/CODEX/New Manga.workspace/worktrees/UI-DESIGN-1` 执行：

```
powershell -NoProfile -ExecutionPolicy Bypass -File verification/UI-DESIGN-1/selfcheck.ps1
```

预期：exit 0，重新生成 `selfcheck-output.txt`，四项检查全 PASS。
若 Reviewer 复跑结果与本文等价日志不一致，以复跑为准并退回 Owner 返修。
