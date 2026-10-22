# H2 R7 隔离集成验证

- Task：P02PRE-R1H-H2-COLLECTOR
- 集成基线：343895fb5f0329c0c07a7104ec321b698f967607
- 受审 docs head：c763efa27db0f10949a52416f1374e88173a31e2
- 集成提交：1924fbb4fbff6044205e4f8b52adb6aaff879e2a（first parent 为基线；second parent 为受审 docs head）
- Worktree：G:/CODEX/New Manga.workspace/worktrees/P02PRE-R1H-H2-COLLECTOR-INTEGRATION（detached；clean）
- 环境：C:\Program Files\PowerShell\7\pwsh.exe，PowerShell 7.6.6 Core；没有执行 live collector、registry/WER、ACL/SDDL、profile、Git child、executor、Build/Cargo、AC 或 Sandbox。
- root 保持：main/HEAD=343895fb5f0329c0c07a7104ec321b698f967607；root .git/index SHA-256=C5CA88842173A8FE4B9C6B6B675528347EECBDC73F85600ABA06F11E3A692B68。

| 检查 | 命令/输入 | 结果 | 原始输出 |
|---|---|---|---|
| PowerShell Parser | pwsh -NoLogo -NoProfile -NonInteractive -File workspace integration-check/parser.ps1；解析集成 worktree 中两份脚本 | PASS，0 errors，exit 0 | parser.stdout.log；stderr 0 bytes |
| pure selftest | pwsh -NoLogo -NoProfile -NonInteractive -File tools/p02/h1-raw-pre-run-selftest.ps1 -CollectorPath <integration collector> -SelfPath <integration selftest> -TempRoot G:/CODEX/New Manga.workspace/temp/P02PRE-R1H-H2-COLLECTOR -Stamp r7-int-68753f0192004a96b97bbd7fe6273cd2 | PASS，200 PASS / 0 FAIL / 6 SKIP，exit 0 | selftest.stdout.log；stderr 0 bytes |

六项 SKIP 原因保持为：live collector 需独立冻结的 H2-RUN；live registry/WER、ACL/SDDL、profile/AppContainer、Git child 均被本 Task 禁止；executor/ProcessObserver/Build/Cargo/AC/Sandbox 均未运行。自测 SUMMARY-JSON 的 liveCollectorExecuted 与 liveQueriesExecuted 均为 false。

集成前后 collector SHA-256 均为 69dbe8ffd57a4e182f6f79817d2351d519724f69188f2ea7840da187714edc61；selftest SHA-256 均为 e7ad2b19508d8aae0943e4b42e6830d6fc16bec53b757b62d745c017645ad96c。原始验证 JSON 的 result=PASS；测试不修改源码，集成 worktree clean。H2-RUN 将从该集成 worktree只读使用精确 R7 collector；本记录不授予其执行权限。
