# P02PRE-R1H Owner Implementation Dispatch

你是本 Task Owner（Antigravity），不是 Reviewer 或 Integrator。请先读取唯一仓库 `G:\CODEX\New Manga` 中的：

- Task：`doc/tasks/P02PRE-R1H.md`，冻结 bytes=`7290` / SHA-256=`388AA4FEF2F47EE1B3EC88BEEBD5A51FCE8C568DE30C7AF12F1D0C6EAA3766F8`
- Manifest：`verification/P02/p02pre-r1h-manifest-20261012.md`，冻结 bytes=`4760` / SHA-256=`28E0313B1300AB571C268A32101C4B8ABACEA9855FD5CED563A4535A8F1E3D74`
- 继承 source：当前 worktree 的 `verification/P02/p02pre-r1g-capture.ps1`，以及 main 仓中 SHA-pinned 的 R1G manifest。

执行位置：`C:\Users\49745\.codex\worktrees\p02pre-r1g\New Manga`；branch=`agent/antigravity/P02PRE-R1H`；base/current HEAD=`946938bd0696dfddd01f87d61fe6723c63ecdc86`。派发前该分支受控状态 clean。

## 交付目标

在上述 branch 上只新增以下三个文件，并提交一个固定 delivery commit：

1. `verification/P02/p02pre-r1h-capture.ps1`
2. `verification/P02/p02pre-r1h-selfcheck.ps1`
3. `verification/P02/p02pre-r1h-handoff-20261012.md`

将冻结的 R1G script 复制成新的 R1H source 后再作最小修改；不得修改或覆盖任何 R1G 文件。按 Task AC1 严格实现 Git mode=`120000` 的 no-follow 分类：只有普通非目录 leaf 且 frozen Git/index/status 和其它前置条件匹配时，方可 path-only skip，记录 `SKIPPED_GIT_SYMLINK_NONREPARSE`；该分支绝不能读/hash 内容、解析或跟随 target、查 ACL 或枚举子项。真实 reparse symlink 仍 no-follow skip；其他模式、类型、stage、基线或身份不匹配均 fail-stop。若安全分类无法证明，保留 STOP 并在 Handoff 标记 `UNPROVABLE`，不得为了让 capture 继续而放宽。

Self-check 只实现 parser、纯函数 assertions 和静态控制流保证；不得调用 capture、Git、任何 host getter、registry/ACL/profile API、Build/Cargo 或 AC。Handoff 如实报告实现、精确 files/commit、限制以及所有未运行项；Owner 不审核自己的代码。

## 严格边界

- 写入范围仅上述三个新文件。不得更改 Task/manifest/Plan/STATUS、R1G source/evidence、其他用户文件或任何其他代码。
- 不运行 parser/self-check、preflight、capture、Git/source/host getter、profile/registry/ACL API、Build/Cargo 或 AC；这些由 Codex 在独立 Review 后按 manifest 执行。
- 不创建/删除 profile，不写 registry/ACL，不改 Windows feature、环境/全局配置，不访问 Windows Sandbox。
- 不读取/stat/hash/query `.tmp.driveupload`；如需 Git status，必须使用 `-- . ':(exclude).tmp.driveupload'`，pathspec 作为独立参数。禁止目录枚举或未经冻结 manifest 的命令/路径。
- 保留现有 R1G 文件与五个 R1G capture outputs，不重跑、不覆盖、不清理。
- 不扩大 R1G 的固定 identity、AppContainer/profile/moniker/SID、registry/ACL/TEMP/cache/scratch/path、protected-file、child process、argv 或写入范围。唯一 R1H runtime outputs 由 Codex manifest 冻结。

## 返回字段

交付 branch、base HEAD、delivery HEAD/commit、worktree path、精确三文件 diff、diff-check（如运行，仅限 Git diff --check，不运行代码）、commit、clean state 的证据路径及摘要；明确 parser/self-check/preflight/capture/build/AC 均未运行。若任务前置条件不符，停止并报告具体差异，不覆盖文件，不改分支历史。