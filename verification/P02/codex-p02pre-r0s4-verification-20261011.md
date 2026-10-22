# P02PRE-R0S4 Codex 集成验证

## 范围与裁决

- Task=`doc/tasks/P02PRE-R0S4.md`，最终状态=`blocked / NOT_SAFE_FOR_R0`。
- Owner/Author/Integrator/Adjudicator=`Codex /root`；非作者 Reviewer=`DeepSeek Harness`。
- 唯一输入 manifest=`verification/P02/p02-readonly-preflight-r0s4-manifest-20261011.md`；Owner delivery=`verification/P02/codex-p02pre-r0s4-delivery-20261011.md`。
- Codex runtime=`gpt-6-luna / max`；没有使用或声称使用 `gpt-6.1-sol / high`。DeepSeek Reviewer runtime effort/model=`NOT_VERIFIED`。
- 当前唯一规划事实源=`doc/REBASELINE_PLAN.md`；最新状态=`doc/STATUS.md`；恢复点=`verification/P02/codex-checkpoint-p02pre-r0s4-20261011.md`。

## 独立 Review（与集成验证分开）

DeepSeek Harness DSH version=`0.2.0-rc.2`，availability probe 回复“收到”、exit `0`。Round 1=`CHANGES_REQUESTED`（P0/P1/P2/P3=`0/1/5/6`）；Round 2=`APPROVED`（`0/0/0/3`），同 session=`session-e11c835e-8ebb-49d7-8d38-47183462779f`，两次 dispatch exit=`0`。Round 2 未发现未关闭 P0/P1/P2，不需要 Round 3。正式报告分别为 `dsh-p02pre-r0s4-review-20261011.md` 和 `dsh-p02pre-r0s4-review-r2-20261011.md`；prompt 见同目录的相应 `.prompt.md` 文件。

Round 1 的实质性意见已按 Round 2 复核的方式处置。Round 2 P3-01（`--ignore-submodules=all` 比 r6 `none` 范围更窄）和 P3-02（`Measure-Object -Character` 不是原始 status bytes/record count）接受为非阻断记录限制；不将该旧命令作为 Gate evidence，也不重跑补造旧 pre-hash。P3-03 在本次补齐 adjudication、verification、checkpoint、Plan、Status、Index 和 P02 父 Task 后关闭。Review 人员未运行 Git/host 查询或复算 hash，相关能力限制保留为 `NOT_VERIFIED`。

## Codex 集成核验

1. 两轮 Review、Task/manifest/delivery 与 adjudication 的引用路径存在，Round 2 输入对象 pins 已列于 adjudication；最终集成态 Task 和其他治理文件 pins 记录在 rolling checkpoint。
2. Task frontmatter 已更新为 `blocked`；Acceptance Criteria 记录文档授权、分类、Review、adjudication 与安全停止均完成。Task 仍 blocked，因为没有已证明无副作用的 runner，未满足真实 host capture 目标。
3. `REBASELINE_PLAN.md` 仅保留一个当前 DAG；Mermaid 每个节点附中文目的、状态和主要依赖。`STATUS.md`、`00_INDEX.md` 和父 Task `P02.md` 与该 DAG、R0S4 Task 和 checkpoint 互相指向。
4. 五类最终分类与 Gate/risk state 在 adjudication、Task、Plan、Status、父 Task 中一致；`NOT_VERIFIED` 仅作为记录属性，不作为第六类，安全停止不当作 `FAILED`。
5. 本次只改项目治理/Task/verification 文档，未修改产品代码、测试、manifest 以外的执行面、系统状态或用户数据。没有 build、Cargo、AC1–AC7、Windows Sandbox 或目标机 P02PRE query。

## Git、工作区与命令证据

Live root=`G:/CODEX/New Manga`；branch=`main`；HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`；tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`；common dir=`.git`。本轮的分开 `git rev-parse --show-toplevel`、`git branch --show-current`、`git rev-parse HEAD`、`git rev-parse 'HEAD^{tree}'`、`git rev-parse --git-common-dir` 均 exit `0`。

先前的编排组合命令曾把 `git status --porcelain=v2 -z --untracked-files=all --ignore-submodules=all` 管道接到 `Measure-Object -Character`，并使用未引用的 `HEAD^{tree}`。它产生 Git fatal，status 只剩字符计数；没有分流原始 stdout/stderr、NUL bytes、独立 exit code 或紧邻 `.git/index` pre-hash。该旧操作的 `index_side_effect=NOT_VERIFIED` 不可追补。本次另行执行受控只读 NUL status，参数为 `git -c core.fsmonitor=false --no-optional-locks status --porcelain=v2 -z --untracked-files=all --ignore-submodules=none`，在前后读取 `.git/index` hash：exit `0`，569 NUL records / 36542 bytes / stderr empty / status SHA-256=`0E52E6B4ADACC0AC9C4F29A8FAD402DDAF9A7FB51B21A789FBE57EDE82681E8C`；index 前后均为 `214767403C469B15D2BDEE786080E58B4D78BF12C541B9FFB7E8A7FA08F3B89C`。该新快照只描述其捕获时点，不证明旧操作无副作用。

该受控 Git 命令第一次未启动：PowerShell 的 `Get-Command git` 返回两个 executable 路径并被误传为一个 FileName；exit/status artifact=`NOT_CAPTURED`，没有 Git 进程。第二次显式选用 `C:\Program Files\Git\cmd\git.exe` 并成功取得状态。该启动失败不影响 `index_side_effect` 的历史限制，也不产生 P02PRE query。

最终 artifact pins 列表的首次 PowerShell 语句因把 `foreach` 块直接管道到 `ConvertTo-Json` 而产生 `ParserError`，在读取文件前停止；修正为先收集 `$results = foreach (...)` 后运行成功。未创建临时文件或修改 pin 对象。

初版风险一致性断言把带 Markdown backtick 的 Plan/STATUS/Index 值当作不一致，返回 false；直接搜索确认字段值一致后，改用允许可选 backtick 的逐文件检查，Task、Plan、STATUS、Index、adjudication 五份当前文档均通过。另一个同类 `foreach` 诊断片段也在解析阶段失败，后用 `rg` 和正确的逐项循环完成检查；没有修改文档状态值。

`git worktree list --porcelain` exit `0`、stderr empty、361 worktrees，current=`G:/CODEX/New Manga`，没有 `--prune`。所有既有未提交文件保留；本轮未 reset、clean、stash、restore、commit、删除或覆盖其他作者内容。当前 status snapshot 识别到 10 个 R0S4 新增文件；其他历史修改的逐项作者归属不由记录数量推断。完整工作树 status records 是仓库状态快照，不在本报告展开无关用户/历史文件清单。

## 最终五类分类、风险与 Gate

- `PASS_WITH_EVIDENCE`：仅 R0 固定时点已经接受的局部 identity、精确 metadata/ACL descriptor、WER snapshot 与固定文件 hash 子集；不代表当前状态、不扩展到完整保护集。
- `FAILED`：`∅`；P02PRE host query 没有运行。
- `UNPROVABLE`：当前用户/SID/token、r6 目标 paths/ACL/TEMP/cache/scratch、当前 protected-file state、WER 状态及 `private_registry_absence`。
- `REQUIRES_ACTIVE_TEST`：有效 LPAC/canary、未来子进程/broker/WER、cache/TEMP/scratch/write closure 与 stop/cleanup。
- `NOT_SAFE_FOR_R0`：PowerShell/exec wrapper、未获副作用合同的 profile/registry getters 及未审 runner/helper。

保留风险裁决：`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；`technical condition unmet; user explicitly accepted residual risk`。P02PRE=`BLOCKED`；profile=`NOT_CREATED`；ACL/registry=`NOT_MODIFIED`；Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`。这次只读授权没有新增 waiver，也没有解除任何 barrier。

## 结论与精确下一步

文档集成与五类分类已核验；OS preflight、产品构建和 AC 均未验证/未运行。当前没有 READY task。只有先有精确绑定且经非作者 Review、Codex adjudication 的 runner 启动/缓存/history/wrapper 无副作用证据，才可再建 capture Task；目前不派发该尚无输入依据的 Task。Windows Sandbox 不查询、不安装、不启用、不启动。
