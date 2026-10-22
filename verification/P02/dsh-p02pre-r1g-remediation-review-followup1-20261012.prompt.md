# P02PRE-R1G 修订 Review Follow-up 1：只读内容审查

## 角色与冻结对象

你是本 Task 的非作者独立 Reviewer。实现 Owner=`Antigravity`；Integrator/Adjudicator=`Codex /root`。Task=`P02PRE-R1G`。固定基线=`cddff58469b56e181019a8ddfeade80684bc7eb9`；候选分支=`agent/antigravity/P02PRE-R1G`；冻结 delivery HEAD=`6e1c00fee3db07805c92c25cdc311af9279ceb51`。候选尚未集成到 main。

Codex 已在 `verification/P02/codex-p02pre-r1g-review-input-pins-followup1-20261012.json` 独立核对以下 12 个输入的精确 bytes/SHA-256、branch/HEAD、授权 diff 和 linked worktree clean 状态。DSH 的 `read` 工具不提供可靠的原始文件 byte/hash；**你不需要也不得自行计算或核验 hashes**。Codex 会在 Review 后对同一批输入复算 pins；任何不匹配将使 Review 无效。只依据下表列出的冻结文件内容进行评审。

| 内容 | exact absolute path | bytes | SHA-256 |
|---|---|---:|---|
| 当前 Task | `G:\CODEX\New Manga\doc\tasks\P02PRE-R1G.md` | 18910 | `870278C6156A7AE08AAAB73AFC5A052E172EB8CC201B12CAFC9B52B16B80870A` |
| 当前 manifest | `G:\CODEX\New Manga\verification\P02\p02pre-r1g-manifest-20261011.md` | 17710 | `B9A7546EE62246E530D2113FBBEB95369AC3E19DF2F410B315972C8C86EAFB55` |
| candidate script | `C:\Users\49745\.codex\worktrees\p02pre-r1g\New Manga\verification\P02\p02pre-r1g-capture.ps1` | 80593 | `2CC9C49F0708B4D174749ACE5F3C92BCD6D6B2E2825CA908412BCE2B2436778F` |
| author self-check attestation | `C:\Users\49745\.codex\worktrees\p02pre-r1g\New Manga\verification\P02\p02pre-r1g-author-selfcheck-20261011.json` | 2462 | `016FA5BA0FCA16FCDB63D62CD0BAF5B723DE5AEF0A6B392DA13C41D88230AEB6` |
| Owner Handoff | `C:\Users\49745\.codex\worktrees\p02pre-r1g\New Manga\verification\P02\p02pre-r1g-antigravity-handoff-20261011.md` | 22604 | `2996A3D05E9010C73F7D57B7249532EB3B33FE071E071FA009968B38DFE1D716` |
| initial Review adjudication and findings | `G:\CODEX\New Manga\verification\P02\p02pre-r1g-review-adjudication-20261012.md` | 6144 | `493A2FE96C4534ED000D7A055F7E3C54CC4A1DC2C15B9D7303FC692A440D1673` |
| remediation Review round-1 process adjudication | `G:\CODEX\New Manga\verification\P02\p02pre-r1g-remediation-review-adjudication-20261012.md` | 4618 | `E31D021C5888AFBBDD99700FF4B8A092535BCDA6D0E78B56D964D3BF9734F5B0` |
| round-1 post-review pin evidence | `G:\CODEX\New Manga\verification\P02\codex-p02pre-r1g-review-input-pins-remediation-20261012.json` | 4796 | `4C0F166343F9A59B904A6D1E0BB1105D6AA8FA61494672C4C927DFEFBC4209CF` |
| current Owner delivery adjudication | `G:\CODEX\New Manga\verification\P02\p02pre-r1g-argumentlist-delivery-adjudication-20261012.md` | 4541 | `9C99E69BB3B0BD849796C96455996BC901AD7760F40A233F123F065B70D15A04` |
| Review template | `G:\CODEX\New Manga\doc\templates\REVIEW.md` | 3915 | `048DD2C001BC16CE68B46460C2D23AA32BA1119091CA1E2ABA3EE4EE63ED4762` |
| predecessor R1F script | `G:\CODEX\New Manga\verification\P02\p02pre-r1f-capture.ps1` | 67582 | `5A3FE118A8758CCDF0BEDBE170D31B34DA6C338101096EAA825DE80DF70E8316` |
| predecessor R1F manifest | `G:\CODEX\New Manga\verification\P02\p02pre-r1f-manifest-20261011.md` | 49783 | `F91AF7B1785B77A57CEEAFE0FFD879345CF361FD85A5E147CD970CF5EF43717B` |

## 严格工具边界

只允许 `read` 工具读取上表的 exact absolute paths。禁止 shell、PowerShell、Git、命令执行、测试、glob、grep、目录枚举、subagent、其他路径/文件读取与文件写入。若某文件超过单次 read 限制，只对同一精确路径分段读取到文件末尾；不得寻找替代路径。不要读取、stat、hash、解析或查询 `.tmp.driveupload` 路径/元数据；允许在 Handoff 文本中看到该名称，但不得对该路径做任何查询。完成后将 Review 直接作为最终回答，不写文件。

## Review 范围

静态审查候选是否满足冻结 Task/manifest 的范围、安全、fail-stop、argv、证据和恢复要求，并逐项对照旧 findings 的处置：

- R-001：序列化/尺寸/写入异常是否保留底层停止类别、原因和细节；是否把无法由 child 证明的 runner 写入问题归到正确证据层。
- R-002、R-006、R-008：Handoff/self-check 是否准确区分作者交付、Codex 核验、`NOT_RUN` 与 `NOT_VERIFIED`；是否避免把 engine attestation 说成尚未实现的断言。
- R-003：protected-hash 失败后是否阻止 ACL re-query，`aclStability` phase 的意义与停止语义是否一致。
- R-004、R-007：候选执行文件/绝对 source/worktree HEAD/pins 是否自洽；Task/manifest 是否区分当前与历史 pins；集成是否要求 Review/adjudication 后对 absent target 使用 `CreateNew` 并复算目标 hash。
- R-005：Handoff 是否不再自引用其自身无法稳定记录的 delivery HEAD，Codex 外部记录是否清楚。
- `.Arguments` 修复：`Invoke-CapturedProcess` 是否使用 `ProcessStartInfo.ArgumentList` 按顺序逐个加入；每个 Git/whoami 调用是否把每个原生 argv 元素作为单独参数传入；状态查询的 `:(exclude).tmp.driveupload` 是否保持为单一 argv；captured evidence 是否准确记录 argumentList、CWD、PID、exit 与相关输出。
- 全面核对 inherited getter/API/child/path/write allowlist、no-read/no-follow、唯一输出与 `CreateNew`、stop conditions、用户数据保护、Windows Sandbox 禁止项和已批准 waiver 边界；不要因 Owner self-check 而宣称运行验证通过。

Handoff 报告还记录 Antigravity 在独立 linked worktree 中执行过未带该 exclusion pathspec 的 `git status --porcelain`。同名相对路径是否被查询=`WORKTREE_RELATIVE_EXCLUDED_PATH_ACCESS=NOT_VERIFIED`；这不证明访问主仓受保护路径。请基于冻结证据判断该程序不确定性是否影响此候选的内容审查结论，不能把它抹成 PASS，也不得为验证而访问该路径。

本轮仅为静态内容 Review：不要运行 parser/self-check、PowerShell child preflight、capture、host getter、registry/ACL/profile 操作、Build/Cargo 或 AC1–AC7。上述运行时行为必须标为 `NOT_RUN`，不能从源代码或 Owner attestation 推断通过。此 Review 本身不等于 Codex adjudication、集成或 Gate PASS。保持：`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；Build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`。

## 报告格式与 verdict

依照 Review template，报告固定对象/HEAD、Architecture/Safety 与 Task/AC 范围、逐条旧 finding disposition、任何新 findings（级别、精确文件/行、触发与影响、建议）、静态审查边界、未运行检查与剩余风险；给出 P0/P1/P2/P3 数量，并且只选择一个 verdict：`APPROVED`、`CHANGES_REQUESTED`、`NOT_VERIFIED` 或 `BLOCKED_BY_MISSING_EVIDENCE`。如无发现，明确写 `0/0/0/0`。`APPROVED` 只表示此冻结候选的静态内容 Review 通过，可交 Codex adjudicate；不得声称 parser、self-check、preflight、capture、Host evidence、Build、AC 或 Gate 通过。
