# Antigravity follow-up：P02PRE-R1H-R6-EXEC-A6 revision 2

你正在继续同一 A6 Owner 会话。项目仓库 `G:\CODEX\New Manga`；Owner worktree `C:\Users\49745\.codex\worktrees\p02pre-r1h-r6-exec-a6-antigravity\New Manga`；branch `agent/antigravity/P02PRE-R1H-R6-EXEC-A6`；base/current HEAD `343895fb5f0329c0c07a7104ec321b698f967607`。不得创建新 worktree、切换分支、stage、commit 或修改 `.git/index`。

## 固定审查结论与任务

DSH 对第一版三文件 delivery 的独立静态 Review 为 `CHANGES_REQUESTED`（P0/P1/P2/P3=`0/0/2/3`）。Codex adjudication 接受两项 P2，并将另一项 findings 中的 AC2 输出命名缺口升为 P2。请只修复下列事项：

1. 将执行器新建的 7 个输出路径全部改为唯一且明确含 `attempt6` 的名字，同时保留 `[IO.FileMode]::CreateNew`、原有 absent/write-safe 校验、同目录约束和写入闭包。建议采用下列精确 basename，并同步更新 executor、protocol、Handoff 中的每一处引用：
   - `stage`: `p02pre-r1h-selfcheck-round6-attempt6-stage-20261012.ps1`
   - `recovery`: `p02pre-r1h-selfcheck-round6-attempt6-recovery-20261012.ps1`
   - `apiBackup`: `p02pre-r1h-selfcheck-round6-attempt6-integrated-backup-20261012.ps1`
   - `handoff`: `p02pre-r1h-round6-attempt6-handoff-20261012.md`
   - `execution`: `p02pre-r1h-integration-round6-attempt6-execution-20261012.json`
   - `selfcheckEvidence`: `p02pre-r1h-selfcheck-round6-attempt6-20261012.json`
   - `engineEvidence`: `p02pre-r1h-engine-preflight-round6-attempt6-20261012.json`
   上述七个目标在 main 根仓库按 Codex 只读 `Test-Path` 均为 `ABSENT`。受保护的 `destination` `p02pre-r1h-selfcheck.ps1` 必须保持原样。
2. 按 Codex adjudication 修正 Handoff 与 protocol 对输入包和证据的表述。只读清单 `verification/P02/agy-p02pre-r1h-r6-exec-a6-input-manifest-r2-20261012.json` 已由 Codex 冻结：包含 27 个输入 pins、`checkpointIncludedInInputPins=true`、明确列出 attempt5 parser-pass checkpoint、root legacy Handoff 及 immutable A6 Task contract。此 manifest 和其中全部输入不可修改；不得声称你独立复算了 Codex pins。
3. 准确引用 Codex adjudication `verification/P02/codex-p02pre-r1h-attempt6-review-adjudication-20261012.md` 的裁决。DSH 把 `639 - 10` 说成不等于 629 是算术错误，Codex 已拒绝该子 finding；F05 的 worktree 归因也已由 Codex 拒绝。保留 attempt6 文件与 A4/A5 源隔离。
4. 修正验证声明：第一版 Handoff 的 Parser 结果目前只有 Owner 声明，没有 Codex 可复核的 raw 输出；普通 `git diff --check` 不会检查未跟踪文件。不要把这两项描述成 Codex 已验证。允许你现在仅对最终 executor 运行 PowerShell 7.6.6 Parser-only 语法解析（不得 dot-source/invoke），并在 Handoff 原样记录实际命令、版本、Parser error count 和结果；不运行 executor 或其它测试。

## 写入范围与禁止项

你只可修改现有三条 A6 allowlist 文件，不得新建或改动其它路径：

- `verification/P02/p02pre-r1h-round6-integrator-attempt6-20261012.ps1`
- `verification/P02/p02pre-r1h-round6-integration-protocol-attempt6-20261012.md`
- `verification/P02/p02pre-r1h-round6-attempt6-exec-handoff-20261012.md`

不得改动原始 25-pin manifest、revision 2 manifest、immutable Task contract、任何 Task/Plan/STATUS/checkpoint、root legacy Handoff、A4/A5 文件、项目输入、用户数据或 `.git/index`；不得 stage/commit。每条 `git status` 命令都必须使用独立最终 pathspec `:(exclude).tmp.driveupload`，不得查询该路径。

禁止 dot-source/invoke attempt6 executor，禁止调用 `File.Replace`、任何 OS/API、child-process、capture/getter、profile/registry/ACL 操作、Build/Cargo、系统 AC1–AC7。不得做 final pre-run 或声称任何 Gate/AC 已通过。保留原风险/Gate 原值，不将 `private_registry_absence=UNPROVABLE` 伪记为 PASS。

## 交付要求

在同一个 worktree 和 HEAD 上仅修改上述三文件。返回每个文件的 byte length/SHA-256、精确三路径变更清单、七个新的输出 basename、修订点、Parser-only 实际结果及逐项 AC 状态。AC1/AC2/AC3 的结论只能说明 Owner 修改声明；独立 pins、whitespace 检查和最终 adjudication 由 Codex 完成。DSH 后续 Review 尚未运行，不能声称已批准。
