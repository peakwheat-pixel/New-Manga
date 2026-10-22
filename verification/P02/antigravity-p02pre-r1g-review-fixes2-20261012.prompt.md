# P02PRE-R1G：完成 Codex 集成核对后的两项返修

你是 R1G 原实现 Owner Antigravity。继续在既有 worktree `C:\Users\49745\.codex\worktrees\p02pre-r1g\New Manga`、branch `agent/antigravity/P02PRE-R1G`、HEAD=`133a832b2fa0d450fcfd131c085698841cfbfafb` 工作。只可修改以下三份分配文件：
- `verification/P02/p02pre-r1g-capture.ps1`
- `verification/P02/p02pre-r1g-author-selfcheck-20261011.json`
- `verification/P02/p02pre-r1g-antigravity-handoff-20261011.md`

Codex 静态核对确认 R-003 的 protected-hash guard 已阻止后续 ACL re-query，ACL phase 状态已添加；R-001 的 size-limit 分支保留原 stop data。但仍有两项待修：

1. **序列化失败保留底层原因（R-001）**：在主 `ConvertTo-Json` 的 catch 内，先保存当前 `Result.stopCategory`、`stopReason`、`stopDetail`，再设置 `EVIDENCE_SERIALIZATION_FAILED`。最小 fallback JSON 必须同时包含这三个 `underlyingStop...` 字段与新的 evidence failure category/reason/detail，以及 serialization exception。现有 size-limit `New-PartialEvidence` 行为保留。证据目标无法写入时，错误仍只由 stderr/runner evidence证明。
2. **移除 Handoff 的自引用 delivery_head（R-005）**：Git commit ID 依赖 commit 内文件字节，Handoff 不可能在自身内容中稳定写入包含它自己的 HEAD。删除误导的 `delivery_head` 字段，不要把旧值改成 `133a...` 冒充最终 HEAD。保留 `implementation_commit=9eb14e...`，把当前已知的前一修订 `133a832b2fa0d450fcfd131c085698841cfbfafb` 明确标为 `previous_owner_revision_commit`，把 `9ec34a...` 标为更早的 predecessor/reviewed head。补一句说明 Codex 会在 Task/checkpoint 外部记录包含该 Handoff 的最终 delivery HEAD。全篇不得把 `133a...` 称作本轮返修后的最终 HEAD。

其余 finding 处置不变，R-004/R-007 由 Codex 处理。仅按原三文件权限工作；脚本有改动时，更新 selfcheck 中的源文件 bytes/SHA-256。不要改 Task、manifest、Plan、STATUS、checkpoint、main checkout 或其他路径。

严格禁止运行 candidate parser/self-check、no-profile child preflight、capture、host getter、registry/ACL/profile API、Build/Cargo/AC、Windows Sandbox。不要检查 `.tmp.driveupload`。不要 reset/clean/stash/覆盖/删除其他用户数据。完成后单独 commit，输出新的 actual HEAD、相较于 base 的精确三文件 diff、各文件 bytes/SHA-256、实际运行过的命令与明确未运行项。不要自审、不要声称 Review 或 Gate PASS。