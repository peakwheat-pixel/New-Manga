# P02PRE-R0S4 Owner Delivery：受控只读预检安全停止

## 对象、基线与授权

- Task=doc/tasks/P02PRE-R0S4.md；manifest=verification/P02/p02-readonly-preflight-r0s4-manifest-20261011.md。
- Repo=G:/CODEX/New Manga；branch=main；base HEAD=cddff58469b56e181019a8ddfeade80684bc7eb9；tree=c25d051a4b9a0bd9773b50170e100f575ea19f2b。
- Owner/Author=Codex /root；非作者 Reviewer=DeepSeek Harness；Integrator/Adjudicator=Codex /root。
- Root runtime=gpt-6-luna / max；未使用 gpt-6.1-sol / high。
- 用户授权是 P02PRE controlled read-only 阶段许可，不是风险 waiver 或 Gate PASS；private_registry_absence=UNPROVABLE 及 Owner 风险接受裁决逐项保留。

## 实际工作与安全处置

静态来源核对范围为 doc/STATUS.md、doc/REBASELINE_PLAN.md、doc/00_INDEX.md、doc/09_COLLABORATION.md、doc/tasks/P02.md、doc/tasks/P02PRE-R0.md、doc/tasks/P02PRE-R0S2.md、doc/tasks/P02PRE-R0S3.md、verification/P02/p02-owner-risk-waiver-execution-manifest-r6-20261011.md、verification/P02/codex-p02pre-r0s2-adjudication-20261011.md、verification/P02/codex-p02pre-r0s3-adjudication-20261011.md 和上述 Task 所指向的 R0/R0S2 证据。此为编排与文档核对记录，不是宿主状态或 Git gate evidence。新 Task 和 manifest 将 r6 候选查询逐项映射到五类状态，区分条件与采集方法，并冻结精确对象候选。

未运行任何 P02PRE host、OS、Registry、WER、profile、token、ACL、path、TEMP/cache、scratch 或 protected-file hash query。R0S2 的非作者 DSH Review 已判定当前 PowerShell/login=false 与 exec_command wrapper 的 startup/profile/module/cache/history/executable/argv side-effect 边界未证明；R0S1 在 G: path query 前安全停止。当前没有新的 runner/API/argv evidence，故本轮不换 shell、不启动子进程、不以 NoProfile 假设替代 Review。安全结果是 STOP_BEFORE_HOST_QUERY。

治理侧 Git 命令在本轮 Task/manifest 创建前执行，shell=PowerShell、login=false。完整组合文本为：git rev-parse --show-toplevel; git branch --show-current; git rev-parse HEAD; git rev-parse HEAD^{tree}; git status --porcelain=v2 -z --untracked-files=all --ignore-submodules=all | Measure-Object -Character; git rev-parse --git-common-dir; git worktree list --porcelain | Measure-Object -Line。可见工具输出给出 root=G:/CODEX/New Manga、branch=main、HEAD=cddff58469b56e181019a8ddfeade80684bc7eb9、status pipeline character count=35961、worktree-list line count=1083；组合输出含 rev-parse HEAD^{tree} 的 fatal ambiguous argument 错误。该 exec 脚本未序列化 exit code，stdout/stderr 未分流保存，status NUL bytes 未留档，具体 UTC 时刻不可恢复。不能断言“未观察到 Git 错误”或把 count 当作 status manifest。

status 命令没有 --no-optional-locks；运行前无紧邻 .git/index pre-hash，所以 index_side_effect=NOT_VERIFIED。旧 index hash 不能补证；未恢复、覆盖或重写 index。未运行 reset、clean、stash、删除或提交；未保存本轮用户未提交文件清单，因此其当前完整性为 NOT_VERIFIED。本段是对缺失记录的披露，不宣称本轮已证明 Git index 或用户未提交状态完整。

## 条件分类

| 条件/对象 | 分类 | 本轮结论 |
|---|---|---|
| R0 固定时点的既有 identity、限定路径 metadata/ACL descriptor、WER 局部 snapshot 与 13 个 protected-file hashes | PASS_WITH_EVIDENCE | 只适用于原 evidence 的对象与时间，不外推至现在或完整集合。 |
| 当前 host/user/SID/token、路径存在性/metadata/ACL、TEMP/cache/scratch/path 映射、当前 protected baseline、LocalDumps 候选状态 | UNPROVABLE | 本轮未运行安全 runner；不得用旧快照代替当前状态。 |
| r6 已列的两个 Registry candidate、三个 WER 目录、12 个只读输入根、13 个 scratch output leaves 与三个 canary leaves | UNPROVABLE | 全部精确登记于 manifest 的 r6 对象表；本轮均 NOT_RUN，不读取内容、不检查 emptiness、不授予写入。 |
| profile path getter、private registry getter、PowerShell/tool wrapper、R0S1 continuation/direct-child inventory、未冻结 WER/environment/path/hash helper | NOT_SAFE_FOR_R0 | 已有独立 Review 或 r6 证据未证明无副作用，或者与精确读取范围不符；均未运行。 |
| LPAC/canary、未来子进程/broker/WER、cache/TEMP/scratch 写闭包、stop/cleanup | REQUIRES_ACTIVE_TEST | 超出只读 R0；当前执行对象仍未冻结。 |
| 本轮普通 git status 的 index side effect 及用户未提交状态完整性 | UNPROVABLE | 原始完整性属性为 index_side_effect=NOT_VERIFIED；该属性不是第六类枚举，旧 index hash 不补紧邻 pre-hash，也不重跑/恢复 index。 |
| FAILED | ∅ | 本轮没有目标 OS 查询；未执行和安全停止不是失败。 |

口径：五类枚举标记条件及方法的分类；NOT_VERIFIED 是原始记录/完整性属性，不是第六类枚举。方法 NOT_SAFE_FOR_R0 表示未运行该方法，不代表条件已测试失败。

private_registry_absence=UNPROVABLE；Technical Gate=NOT_SATISFIED；Owner Risk Acceptance=APPROVED；Gate Disposition=WAIVED_BY_OWNER；Build Authorization=AUTHORIZED_WITH_EXCEPTION；technical condition unmet; user explicitly accepted residual risk。

## 未改变的安全状态

P02PRE=BLOCKED；profile=NOT_CREATED；ACL/registry=NOT_MODIFIED；Build Gate=BLOCKED；Hard Build Barrier=EFFECTIVE；build/Cargo=NOT_RUN；AC1–AC7=BLOCKED / NOT_RUN。不得查询、安装、启用或启动 Windows Sandbox。

本 Delivery 不以普通 git status 的 index_side_effect 未验证项宣称 Git gate 通过。待非作者 Review 与 Codex adjudication 核对本交付、manifest、Task 以及本项完整性限制。

## 非作者 Review Round 1

DeepSeek Harness DSH version=0.2.0-rc.2；只回复“收到”的 availability probe exit=0；正式 Review session=session-e11c835e-8ebb-49d7-8d38-47183462779f，dispatch exit=0，并已挂入 New Manga DSH workspace。Round 1 结论=CHANGES_REQUESTED，P0/P1/P2/P3=0/1/5/6。报告=dsh-p02pre-r0s4-review-20261011.md。Reviewer 未运行 shell/Git/host query，未独立复算 artifact pins 或验证零 host query 声明。Owner 正在按 findings 做最小文档修订；不能将该 Round 1 当作最终 Review。
