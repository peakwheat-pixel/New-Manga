# P02PRE-R1H Owner remediation dispatch

你是本 Task Owner（Antigravity），不是 Reviewer 或 Integrator。请只在已存在的候选 linked worktree 内处理首轮独立 Review findings。

## 冻结任务输入

- 仓库：`G:\CODEX\New Manga`
- Task：`doc/tasks/P02PRE-R1H.md`，8324 bytes，SHA-256=`09081A45535BB92529118E59D85739C029B23C6982E7E54F9225B95F64652E55`
- Manifest：`verification/P02/p02pre-r1h-manifest-20261012.md`，4760 bytes，SHA-256=`28E0313B1300AB571C268A32101C4B8ABACEA9855FD5CED563A4535A8F1E3D74`
- 首轮 Review：`verification/P02/codex-subagent-p02pre-r1h-static-review-20261012.md`，2308 bytes，SHA-256=`4BB1D8B8C8FACD96C4C087774756A71D79F832F10AD75026ADA3800579EE6688`
- Codex adjudication：`verification/P02/p02pre-r1h-review-adjudication-20261012.md`，1543 bytes，SHA-256=`20EA61BC98F5826BF7FDF487E01B3F34CF6FBA609E9C3999C242100920268497`
- Review post-pins：`verification/P02/codex-p02pre-r1h-review-input-pins-post-20261012.json`，2070 bytes，SHA-256=`9AA0A6783B9466BD146DB04A65FC61287144C6ADA5B6747AE5958538251BCDB4`
- 当前 main HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`。

## Owner branch/worktree

- Branch=`agent/antigravity/P02PRE-R1H`
- Worktree=`C:\Users\49745\.codex\worktrees\p02pre-r1g\New Manga`
- Base=`946938bd0696dfddd01f87d61fe6723c63ecdc86`
- Current HEAD=`256e3ea622cba7a658020ddcf015b18894d88b38`
- 派发前 root 已核实 branch/HEAD 完全匹配且受控 worktree clean（status 精确排除 `:(exclude).tmp.driveupload`）。若不匹配，停止并报告，不切换或重置历史。

## 修改范围与交付

只允许修改并提交以下三项现有 candidate 文件，不得改 Task、manifest、Plan/STATUS、R1G source/evidence 或其他文件：

1. `verification/P02/p02pre-r1h-capture.ps1`
2. `verification/P02/p02pre-r1h-selfcheck.ps1`
3. `verification/P02/p02pre-r1h-handoff-20261012.md`

在同一 branch 产生新的 delivery commit。交付准确 branch/base/HEAD/tree、三文件 diff、clean status、`git diff --check` 结果（允许仅运行这项只读检查）及新的每文件 bytes/SHA-256 pins。Owner 不审核自己的工作。

## 必须修复的 Review findings

1. **R1H-001 / P1：冻结 status/index 基线**。非-reparse skip 前必须证明 main 与 scratch 的 refs、`.git/index` 和 `git status --porcelain=v1 -z --untracked-files=all --no-renames --ignore-submodules=none -- . :(exclude).tmp.driveupload` 精确匹配可核验的冻结 baseline，并在任何 skip 前确认两个仓库均通过。status exit=0、查询成功或仅本次运行前后稳定都不够。不得猜造 hash、偷换 baseline、扩大 API/path/child allowlist 或访问 `.tmp.driveupload`。请先按 Task/manifest/R1G 证据判断是否存在精确可核验的 frozen status/index expected values；若不存在或不能安全比较，保持该对象为 `STOP / UNPROVABLE`，禁止非-reparse skip，并在 Handoff 明确缺少的证据和未执行项。**这时不要为了让 capture 继续而自行修改 manifest 或放宽条件。**
2. **R1H-002 / P2：Git index stage**。解析并保留每个 entry 的 mode 与 stage；只有唯一且准确的 stage=0 entry 可参与分类，任何 stage=1/2/3、重复、冲突、未知 mode 或解析异常都 fail-stop。若候选不能安全构造该证明，STOP。
3. **R1H-003 / P2：ordinary leaf 类型**。不能仅凭 `IsLeaf/!PSIsContainer/!ReparsePoint` 跳过。使用现有、已允许 metadata 明确白名单证明普通文件；Device、目录、未知 provider/object type 或未知属性必须 STOP。不得新增 target 解析、读取/哈希内容、ACL 查询或子项枚举。
4. **R1H-004 / P2：self-check**。消除当前 regex 因注释而不匹配的问题；改为绑定实际 `Get-RepositoryRecord` AST 分支及退出路径的静态断言，证明非-reparse skip 分支中没有内容读取/hash、ACL、目录枚举、target 解析/读取或写入，并证明 branch break 后外层跳过。为 frozen baseline mismatch、stage 1–3/重复 entry、Device/未知对象添加反例。若证明能力不足，应 fail-check/维持 STOP，不得返回保证超出检查实际覆盖面的 PASS。

## 安全与执行限制

- 阅读上述精确 Task/manifest/Review/adjudication 与当前 candidate source；不得从聊天摘要取代冻结证据。
- 禁止运行候选 parser/self-check、任何测试、preflight/capture/getter；禁止 Build/Cargo、AC1–AC7、registry/ACL/profile/Windows feature 修改或 Windows Sandbox 操作。Codex 会在新 Review 与 adjudication 后按 Task 推进验证。
- 不读取/stat/hash/query `.tmp.driveupload`；若使用 `git status`，必须通过精确 exclude pathspec，且它是独立单个 argv 参数。
- 不读、跟随、解析、打开或哈希 tracked symlink target；不新增 executable/API/path/query/child/write scope。
- 不覆盖、删除、清理、重跑或改写任何既有 R1G/R1H 输出。遇到无法证明的条件，保持 fail-stop 并如实交付 `UNPROVABLE`。

## Handoff 必须写明

逐条列出四项 finding 的状态与代码位置；R1H-001 是否存在可核验的 frozen status/index baseline 及证据来源；如果不存在，说明 candidate 将 fail-stop 且不允许 capture；parser/self-check/preflight/capture/Build/Cargo/AC 均保持未运行；不得声称任何 Gate PASS。