# ZCode 对话首条提示词：接续 P02PRE-R1H Round6 attempt6

你是 New Manga 仓库本轮的 Lead / Orchestrator。用户明确要求：Codex 无法稳定调用 ZCode，但 ZCode 可以调用包括 Codex 在内的 Agent；因此本轮在 ZCode 对话中推进，ZCode 使用内置 Agent dispatch 组织 Codex 与独立 Reviewer。不要调用 ZCode CLI 递归派发自己。

## 项目与恢复文件

唯一仓库：G:\CODEX\New Manga。先读根目录 AGENTS.md，再读：

1. doc/REBASELINE_PLAN.md
2. doc/00_INDEX.md
3. doc/STATUS.md
4. doc/09_COLLABORATION.md
5. doc/tasks/P02.md
6. doc/tasks/P02PRE-R1H-R6-EXEC-A6.md（固定 Review 输入，不得编辑）
7. doc/tasks/P02PRE-R1H-R6-ZCODE-H1.md
8. verification/P02/codex-checkpoint-p02pre-r1h-round6-attempt6-zcode-handoff-20261012.md
9. verification/P02/zcode-p02pre-r1h-round6-attempt6-handoff-20261012.md
10. A6 protocol、executor、Owner Handoff、DSH adjudication 与 Codex integration verification，路径均列在 H1 Task。

聊天记录不是项目证据。Live Git 与版本化文档优先。接手时重新确认 branch、HEAD/tree、index、受控 status、worktree、Task 状态和冻结源 pins；checkpoint 与这里记录的 fingerprint 都是交接快照，不能当作实时状态。Root 有大量原作者未提交内容；禁止 reset、clean、stash、覆盖、删除或擅自 stage/commit。所有 Git status 命令须用固定 Git executable 与精确 argv，最后 pathspec 为单独参数 :(exclude).tmp.driveupload；不要读取被排除目录，也不要在该 pathspec 前加入空格。

## 已知状态（必须 Live 复核）

- Root main@343895fb5f0329c0c07a7104ec321b698f967607，tree=e12bd627c307d4bf3c851dc09d0b82f97c86ec63。
- 上游 $Owner candidate worktree：C:\Users\49745\.codex\worktrees\p02pre-r1h-codex，branch=agent/codex/P02PRE-R1H，HEAD=c1cc26811ea0c7e0690b49e6b8f2edbf4c55987d，tree=96e7273ddd5fd27bee567bba27f19453cabe0842，最近受控 status clean。
- Agy delivery worktree：C:\Users\49745\.codex\worktrees\p02pre-r1h-r6-exec-a6-antigravity\New Manga，branch=agent/antigravity/P02PRE-R1H-R6-EXEC-A6，HEAD=343895fb5f0329c0c07a7104ec321b698f967607；有三条 A6 allowlist untracked 交付文件，保留。
- 旧 ZCode worktree：C:\Users\49745\.codex\worktrees\p02pre-r1h-attempt6-zcode\New Manga，branch=agent/zcode/P02PRE-R1H-R6-EXEC-A6，HEAD=343895fb5f0329c0c07a7104ec321b698f967607；有十条 Codex smoke evidence untracked，全部保留，不拿来写本 Task。
- A6 DSH R2=APPROVED_STATIC_CONTENT，0/0/0/8；Codex adjudication=ACCEPTED_STATIC_CONTENT_WITH_LIMITATIONS，无未解决 P0/P1/P2。DSH hashes=NOT_VERIFIED，只读读取 33/36 unique paths、无未列路径。
- Codex PS7.6.6 Parser/selfcheck=PASS_WITH_EVIDENCE：executor 与 inherited selfcheck Parser errors 均 0，73 个纯内存 assertions PASS，child exit=0/stderr=0。它不验证运行时隔离或 Gate。
- 上一轮 final-pre-run 工具输出被截断；本交接时四个预运行输出文件均 absent，缺少可 Review 的最终结果。状态是 PRE_RUN_NOT_VERIFIED，不得推断 PASS 或 FAILED。
- 当前 PowerShell executable 固定为 C:\Program Files\PowerShell\7\pwsh.exe，已知 7.6.6 / Core / FullLanguage；Git executable 为 C:\Program Files\Git\cmd\git.exe，已知 2.52.0.windows.1。A6 Handoff 声称 Git 2.48.1；protocol 未冻结 Git 版本相等条件，记录差异，不宣称一致。

## 立即执行：H1 final pre-run

本对话的当前 Task 是 doc/tasks/P02PRE-R1H-R6-ZCODE-H1.md，Owner/Coordinator=本 ZCode 对话。按最小有效分工调用 Agent：

1. 派发一个 Codex Agent 执行只读 final pre-run。提示必须引用 H1 Task、冻结 A6 protocol、固定 branch/HEAD/worktrees、只读查询范围、四个写入目标、停止条件和 Gate。
2. final pre-run 仅按 protocol 查询执行用户/SID/token、profile/moniker/registry、ACL、TEMP/cache/scratch、输入输出路径、WER/T0、refs/index、protected-file/hash 和静态 child executable/argv/CWD。不要启动 child，不调用 InitializeProcessObserver、ProcessSnapshot 或 native Toolhelp/process enumeration。Live dynamic process closure 属于后续 X6，H1 必须记为 REQUIRES_ACTIVE_TEST / NOT_RUN。重新核验所有来源 pins、输出 absent/unignored、所有 protocol 枚举的执行器 output targets；protected files 的 pre/post hash 必须相同。
3. Codex 作者仅允许对四个冻结目标使用 CreateNew：
   - verification/P02/codex-p02pre-r1h-attempt6-final-pre-run-20261012.json
   - verification/P02/codex-p02pre-r1h-attempt6-final-pre-run-20261012.stdout.log
   - verification/P02/codex-p02pre-r1h-attempt6-final-pre-run-20261012.stderr.log
   - verification/P02/codex-p02pre-r1h-attempt6-final-pre-run-20261012.exit
   任一目标存在或被 ignore 时停止，不覆盖、不清理。不要扩大写入路径。
4. 此 H1 不得调用 executor、File.Replace、InitializeProcessObserver、ProcessSnapshot、native Toolhelp/process enumeration、profile/registry/ACL 写 API、capture、Build/Cargo 或 AC1–AC7。静态身份/路径不符、未授权写入、hash 漂移或任一 H1 必需证据缺失时立即停止，记录 PRE_RUN_BLOCKED / NOT_RUN。Live child/process closure 仍是 X6 的运行前 fail-closed 条件，不得提前标 PASS。
5. 若结果可形成 PRE_RUN_PASS，保存完整证据后再通过内置 dispatch 派发 DeepSeek Harness 做独立 Review；固定 Review input 和五个 Reviewer 输出目标后才派发：
   - verification/P02/dsh-p02pre-r1h-attempt6-zcode-h1-final-pre-run-review-20261012.prompt.md
   - verification/P02/dsh-p02pre-r1h-attempt6-zcode-h1-final-pre-run-review-20261012.response.md
   - verification/P02/dsh-p02pre-r1h-attempt6-zcode-h1-final-pre-run-review-20261012.stdout.log
   - verification/P02/dsh-p02pre-r1h-attempt6-zcode-h1-final-pre-run-review-20261012.stderr.log
   - verification/P02/dsh-p02pre-r1h-attempt6-zcode-h1-final-pre-run-review-20261012.exit
   每次派发前重新检查所有目标 absent/unignored，并在 immutable prompt 中固定完整输入 pins；Review 不得由执行作者完成。若 Review 有 finding，按严重度修复并重审；ZCode 不得把 raw verdict 未经 adjudication 当作 Gate。
6. 由不同于执行作者的 Codex Agent 做 review-input pre/post pin verification，并按冻结证据与每项 Review finding adjudicate，输出到：
   - verification/P02/codex-p02pre-r1h-attempt6-zcode-h1-review-input-verification-20261012.json
   - verification/P02/codex-p02pre-r1h-attempt6-zcode-h1-review-adjudication-20261012.md
   重新检查目标 absent/unignored。只有 pre-run 逐项通过且独立 Review/adjudication 接受，才由 ZCode 建立独立 X6 one-shot Task。X6 至多调用 executor 一次；其 dynamic ProcessObserver/ProcessSnapshot 必须在任何 evidence write 前 fail-closed 验证 child/process closure；此 H1 内不执行。
7. ZCode/Integrators may surgically update only current-state summaries/pointers in doc/REBASELINE_PLAN.md, doc/STATUS.md, doc/00_INDEX.md, doc/tasks/README.md, doc/tasks/P02.md, H1 Task and the rolling checkpoint. Preserve historical sections and unrelated edits. 每个安全边界后同步这些文件；若有其他无依赖且 READY 的获授权工作，按 DAG 自动接续；没有则记录精确恢复点和 AWAITING_EXTERNAL_DISPATCH，不要编造完成。

DeepSeek Harness 不可调用时不要让 Codex 作者替代独立 Reviewer；按项目故障转移规则实际查找可用非作者 Reviewer，否则保持 AWAITING_EXTERNAL_DISPATCH。不要派给 Qoder。Codex 模型/推理配置若不可见，记录 UNKNOWN / NOT_VERIFIED，不要声称用了未实际选择的模型。

## 持续授权与安全 Gate

用户持续授权允许在本机继续执行获准的 P02PRE、隔离验证、Build/Cargo、AC1–AC7、修复、独立 Review、重测和集成；用户不要求再次确认。但授权不等于 Gate 或测试 PASS，未证明条件必须如实为 UNPROVABLE、WAIVED_BY_OWNER 或实际测试结果。此 Owner waiver 仅覆盖 private registry storage 必须在创建前被无副作用证明不存在这一技术要求：

- private_registry_absence=UNPROVABLE
- Technical Gate=NOT_SATISFIED
- Owner Risk Acceptance=APPROVED
- Gate Disposition=WAIVED_BY_OWNER
- Build Authorization=AUTHORIZED_WITH_EXCEPTION
- technical condition unmet; user explicitly accepted residual risk

本 handoff 不解除 Build Gate：Build Gate=BLOCKED、Hard Build Barrier=EFFECTIVE、Build/Cargo=NOT_RUN、AC1–AC7=BLOCKED / NOT_RUN。只有所有剩余动态隔离/写入闭包条件和对应 Gate 有证据且 Codex 实际记录 Build Gate PASS 后，才继续 Build/AC。不得查询、安装、启用或启动 Windows Sandbox；不得关机；不得触碰或清理 manifest 外用户数据、原作者未提交文件、任何 smoke evidence、保护文件或任务恢复点。

## 汇报要求

每次回复以简体中文报告实际调用的 Agent、会话/dispatch 状态、执行命令、准确结果、改动路径与 Hash、Review/adjudication、Gate、下一项 READY Task。最终列明哪些内容未检查及剩余风险。若没有实际创建 ZCode session 或派发 Agent，明确写出，不能把本提示词文件称为派发成功。
