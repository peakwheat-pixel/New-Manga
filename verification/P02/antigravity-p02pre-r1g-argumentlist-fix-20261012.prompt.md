# P02PRE-R1G owner follow-up：ProcessStartInfo.ArgumentList 修复

## Task / Agent / 基线

Task=`P02PRE-R1G`，唯一实现 Owner=`Antigravity`，当前 task branch=`agent/antigravity/P02PRE-R1G`，linked worktree=`C:\Users\49745\.codex\worktrees\p02pre-r1g\New Manga`，冻结输入 HEAD=`6943c6727c82c706d90a3ed4c14617b04c98d360`，base=`cddff58469b56e181019a8ddfeade80684bc7eb9`。Codex=`Integrator/Adjudicator`，非作者 Reviewer=`DeepSeek Harness`。

这是原 R1G Task 三文件范围内的窄修复。主仓当前有效 Task=`G:\CODEX\New Manga\doc\tasks\P02PRE-R1G.md`，manifest=`G:\CODEX\New Manga\verification\P02\p02pre-r1g-manifest-20261011.md`；请先只读这两份最新契约与当前 worktree candidate。主仓文件不得修改。

## 已核实的契约缺口

Codex 静态核实 manifest 要求 child 使用 `.NET ProcessStartInfo.ArgumentList` 并留 exact ordered argv，但 candidate `Invoke-CapturedProcess` 当前把一个 string 赋给 `$info.Arguments`。调用点在 `Invoke-Git` 五个 Git commands（`rev-parse`、`symbolic-ref`、`status`、两条 `ls-files`）与 `whoami.exe /all`。R1G DSH Review round 1 因 prompt 设计错误返回 `BLOCKED_BY_MISSING_EVIDENCE`，不是 candidate Review 通过；Codex adjudication 已保留在主仓 `verification/P02/p02pre-r1g-remediation-review-adjudication-20261012.md`。本修复不是扩大范围。

## 允许写入范围

仅当前 branch/worktree 中的以下三个文件：

1. `verification/P02/p02pre-r1g-capture.ps1`
2. `verification/P02/p02pre-r1g-author-selfcheck-20261011.json`
3. `verification/P02/p02pre-r1g-antigravity-handoff-20261011.md`

允许读取以上文件，以及 Task/manifest/adjudication 的上述主仓绝对路径。禁止修改主仓、其他 worktree 或任何其他文件。

## 实施要求

- 将 `Invoke-CapturedProcess` 改为接收有序 string-array 参数；通过 `$info.ArgumentList.Add(<one arg>)` 逐项传递，不再向 `.Arguments` 写入拼接字符串。
- 更新所有调用者，审阅整个函数与全部 call sites 后才改：Git 公共参数前缀依次为 `--no-optional-locks`, `-c`, `core.quotepath=false`, `-c`, `core.fsmonitor=false`, `-c`, `core.untrackedCache=false`, `-C`, `<Root>`；其后依次保留：
  1. `rev-parse --show-toplevel --git-common-dir HEAD HEAD^{tree}`
  2. `symbolic-ref --short HEAD`
  3. `status --porcelain=v1 -z --untracked-files=all --no-renames --ignore-submodules=none -- . :(exclude).tmp.driveupload`（`: (exclude)` 不拆分；实际字面量是 `:(exclude).tmp.driveupload`，作为**单个 argv element**；不要访问该排除路径）
  4. `ls-files --cached --others --exclude-standard -z`
  5. `ls-files --stage -z`
  `whoami.exe` 唯一参数保持 `/all`。
- Child evidence 记录 executable、exact ordered `argumentList`（array，而非渲染字符串）、working directory、PID、exit code，以及既有 stdout/stderr raw byte / hash / encoding facts；不改变现有 capture、error/exit、文本解码和字节保留行为。
- 严格保持现有 executable、child、path、getter/API、read/write、output target 与停机范围；不得访问 `.tmp.driveupload`，不得增加其它子进程或权限。
- 同步更新 author self-check JSON 与 Handoff 中的当前 candidate byte/SHA、implementation commit / delivery metadata、argv 记录语义及未执行状态；不得把 `NOT_RUN` 写成 PASS。Handoff 不得自引用包含自身的 delivery HEAD。
- 检查状态开始应为 frozen HEAD，提交一个仅含上述三个文件的 commit。报告 old/new commit、改动路径、size/SHA、worktree clean 状态。

## 禁止运行的检查

当前新 candidate 尚未通过非作者 Review + Codex adjudication。此轮不得运行 parser/self-check、`-NoProfile` engine preflight、capture、host getter、registry/ACL/profile API、Build/Cargo 或 AC1–AC7；不安装/启用/启动 Windows Sandbox。不得覆盖、删除或清理任何历史证据。

## 验收与返回

- `ProcessStartInfo.ArgumentList` 用于所有既有 child，candidate 中不再以 `$info.Arguments` 传递子进程参数。
- 五个 Git call sites 与 `whoami.exe /all` 的 ordered argv 与上列契约逐项相符；特别确认 pathspec 是一个元素。
- stdout/stderr/process PID/exit 证据保留原行为与语义；Handoff/self-check pins 与交付 HEAD 文案无自引用或 PASS 误报。
- branch/base 正确；仅三个允许文件改变并提交；不运行被禁止的检查。
- 输出：改动摘要、逐条验收、提交 SHA、文件 bytes/SHA、worktree status、所有未运行项和风险。若你认为实现会改变冻结语义，停止并说明，不要自行扩大范围。