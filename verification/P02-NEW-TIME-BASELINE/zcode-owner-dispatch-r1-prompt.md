请严格按本 Task 已冻结范围，执行一次 P02 新时点基线采集。

本次目的仅为判断当前版本是否具备继续 X6 的准入资格。不得声称补齐或替代旧 H1 / P2-1 证据；不得修改代码、Task、状态、计划或历史证据；不得执行 X6、post-run Review、Build/Cargo 或 AC1–AC7。只运行下方唯一的采集器调用一次。无论成功或失败都保留输出，不得使用相同 RunId 重试。执行前确认工作目录和 Freeze Manifest SHA；目标文件若已存在则停止并报告，不得覆盖。

工作目录：
G:\CODEX\New Manga.workspace\worktrees\P02-NEW-TIME-BASELINE

Freeze Manifest：
G:\CODEX\New Manga.workspace\agent-output\zcode\P02-NEW-TIME-BASELINE\baseline-20261014T0915CST-p02-admission-r2\freeze-manifest.json
SHA-256：8662DEC583D2FD865532A414F0BEDE63B7F02872AB3C9232553C3B01E239006D

唯一采集器：
G:\CODEX\New Manga.workspace\worktrees\P02-NEW-TIME-BASELINE\tools\p02\p02-new-time-baseline.ps1

在 PowerShell 中通过 Start-Process 启动以下固定命令，stdout / stderr 分别重定向到外部路径，保存退出码；不执行其它业务命令：
- Executable: C:\Program Files\PowerShell\7\pwsh.exe
- ArgumentList: -NoProfile, -File, "G:\CODEX\New Manga.workspace\worktrees\P02-NEW-TIME-BASELINE\tools\p02\p02-new-time-baseline.ps1", -RunId baseline-20261014T0915CST-p02-admission-r2, -FreezeManifestPath "G:\CODEX\New Manga.workspace\agent-output\zcode\P02-NEW-TIME-BASELINE\baseline-20261014T0915CST-p02-admission-r2\freeze-manifest.json", -FreezeManifestSha256 8662DEC583D2FD865532A414F0BEDE63B7F02872AB3C9232553C3B01E239006D
- Working directory: G:\CODEX\New Manga.workspace\worktrees\P02-NEW-TIME-BASELINE
- stdout: G:\CODEX\New Manga.workspace\agent-output\zcode\P02-NEW-TIME-BASELINE\baseline-20261014T0915CST-p02-admission-r2\collector.stdout.txt
- stderr: G:\CODEX\New Manga.workspace\agent-output\zcode\P02-NEW-TIME-BASELINE\baseline-20261014T0915CST-p02-admission-r2\collector.stderr.txt
- exit code: G:\CODEX\New Manga.workspace\agent-output\zcode\P02-NEW-TIME-BASELINE\baseline-20261014T0915CST-p02-admission-r2\collector.exit.txt

示例实现可使用 Start-Process -Wait -PassThru -WindowStyle Hidden -RedirectStandardOutput / -RedirectStandardError，并将带空格的路径用双引号包住。开始前再次确认唯一输出目标不存在：
G:\CODEX\New Manga.workspace\agent-output\zcode\P02-NEW-TIME-BASELINE\run-baseline-20261014T0915CST-p02-admission-r2.json

完成后只报告实际退出码、RunId、输出目标是否存在、stdout/stderr/采集结果的 SHA-256 与大小、以及是否有文件被意外修改。不要解释性改写采集器数据。