# Codex main 集成验证 r1

- Task：`P02-NEW-TIME-BASELINE`
- Target：`main`
- Integration commit：`d6745a45a8100da949004d42cbc9d397c395d303`
- Scope：仅集成 DSH 已审查的两个 Task 脚本；未合并 ZCode worktree 的其他历史变更。

## 精确集成范围

| 路径 | main commit Git blob | 结果 |
|---|---|---|
| `tools/p02/p02-new-time-baseline.ps1` | `630833290e8e6be89ac38ab089bb8efae4872894` | 与 DSH reviewed source `318bc2a1` 一致 |
| `tools/p02/p02-new-time-baseline-selftest.ps1` | `519a48c77e9d4db1c39aa12fd198573f5118a163` | 与 DSH reviewed source `318bc2a1` 一致 |

Commit 变更为 2 个新增文件、2,726 行；不修改共享接口、schema 或依赖。完整快进包含 217 个路径；其中主工作区已有 89 个未跟踪路径会被遮蔽，因此未执行整分支合并，保留原工作区内容，仅集成上述审查范围。

## 自检

- 命令：`pwsh -NoProfile -File tools/p02/p02-new-time-baseline-selftest.ps1`
- PowerShell：7.6.6 Core / FullLanguage。
- 结果：234 assertions PASS / 0 FAIL / 7 SKIP / exit 0；七项 SKIP 逐项原因见 raw stdout，均属于 live collector、外部进程/身份查询、H1/P2-1 或后续 X6/build/AC 禁止范围。
- Raw output：`G:/CODEX/New Manga.workspace/agent-output/codex/P02-NEW-TIME-BASELINE/main-integration-selftest-r1/`（stdout SHA-256 `4C6BDA574C4C62692BFA323054CDEDD4BE7E767F4295DD7AD9D544309EBA8D58`；stderr 0 bytes；exit `0`）。
- 自检对照的 collector/selftest 内容与 integration commit blob 一致；未执行 collector、X6、post-run Review、Build/Cargo、产品 AC1–AC7 或 Windows Sandbox。

未更改任何用户历史证据或旧 H1/P2-1 结论。完整输入/输出与 DSH result review 作为 Task evidence 独立保留。
