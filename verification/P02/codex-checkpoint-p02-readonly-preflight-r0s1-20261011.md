# P02PRE-R0S1 查询前 Rolling Checkpoint

更新时间=`2026-10-11 08:24 Asia/Shanghai`。这是查询前冻结点；本文件不记录 R0S1 OS capture 结果，也不构成任何 Gate PASS。

## Live Git 与工作区

- Repo=`G:/CODEX/New Manga`；branch=`main`；HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`；tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`；common-dir=`G:/CODEX/New Manga/.git`。
- 安全 NUL status=`git -c core.fsmonitor=false --no-optional-locks status --porcelain=v1 -z --untracked-files=all`，exit=`0`、`522 records`、stderr 为空。`.git/index` 查询前后 SHA-256 均=`214767403C469B15D2BDEE786080E58B4D78BF12C541B9FFB7E8A7FA08F3B89C`，保持一致。登记 worktrees=`361`；未 prune。
- 工作区存在大量进入本任务前已存在的未提交内容；均归其原作者，未 reset、clean、stash、覆盖、删除或提交。本轮在授权范围内新增/修改的 Task、治理文档和 manifest 归当前 Codex Owner；本轮文档写入均留在共享工作区并未提交。
- 早期普通 `git status` 曾无紧邻 index pre-hash，历史记录仍为 `index_side_effect=NOT_VERIFIED`；本次安全快照不能回溯补证，也未尝试恢复 index。

## 当前任务与角色

- 唯一 Active 产品 Task=P02；Active verification Task=`P02PRE-R0S1`，状态=`ACTIVE / STATIC_SAFE_TO_CAPTURE / PRE-QUERY-CHECKPOINT-CREATED / CAPTURE_NOT_RUN`。
- Owner/Author=`Codex /root`；正式非作者 Reviewer=`DeepSeek Harness`；Integrator/Adjudicator=`Codex /root`。Review 仅在 capture evidence 固定后派发。
- 静态 manifest advisor=`/root/r0s1_manifest_advisor`，实际配置=`gpt-6.1-sol / high`。三轮修订循环结论为 `BLOCK_CAPTURE`、`BLOCK_CAPTURE`、`SAFE_TO_CAPTURE`；第四次只确认 Task runner 文字与 manifest 一致。它只做静态文档阅读，不是正式 DSH Review，不是运行证据或 Gate 凭证。当前 runtime 未向 root 暴露可核验的 root model ID/effort，不声称 root 使用该 advisor 配置。
- R0S1 独立 Task=`doc/tasks/P02PRE-R0S1.md`，查询前 pins：`8303 bytes / SHA-256 BD73A543B2DBA2A28A38493769B64770C88DB14188D6BBD97189EA903082E2AD`。
- 冻结 manifest=`verification/P02/p02-readonly-preflight-r0s1-manifest-20261011.md`，查询前 pin：`22925 bytes / SHA-256 CA293C34473D25E406E72B7DB05AC9364A69544D41214B93857ABAD11FEC6DE3`。

## 用户授权与风险状态

用户批准 P02PRE 受控只读取证，仅允许不创建、删除或修改系统/项目状态的 getter/query。R0S1 只检查当前执行身份、已加载 PowerShell built-in module/provider 信息、两条登记 scratch leaf 的冻结祖先 metadata 与两个 leaf 的 direct-child count。不得读取 child 名称、属性或内容；不得查询冻结路径以外对象；不得执行写入、profile/API、registry/ACL、protected-path write probe、build/Cargo、AC1–AC7、Windows feature 或 Windows Sandbox 查询/变更。

保持原有风险裁决：`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；固定原文=`technical condition unmet; user explicitly accepted residual risk`。此 waiver 只覆盖创建前证明目标 private registry storage 不存在。

## R0 前序证据 pins

- R0 Owner evidence=`verification/P02/p02-readonly-preflight-r0-evidence-20261011.md`，`99592 bytes / SHA-256 AE16A27C5843C71C9EC9414C54C2FF23EBE5A612F75DA0CB5EA3A49B154879F3`。
- R0 非作者 DSH Review=`verification/P02/p02-readonly-preflight-r0-review-20261011.md`，`29404 bytes / SHA-256 427F582D87A54E8C5B7CB65FB72F1B067BD226B8E6DFA66873FDC996E6B5C554`；结论=`APPROVED_AS_READ_ONLY_EVIDENCE_DELIVERY_ONLY`，P0/P1/P2/P3=`0/0/5/6`。
- R0 Codex adjudication=`verification/P02/codex-p02pre-r0-adjudication-20261011.md`，`11145 bytes / SHA-256 E66131960E35A35C8E6F051EFE0F1C167CEBE2DBC78D849DA00A2642D901375E`；结论=`ACCEPTED_AS_READ_ONLY_EVIDENCE_DELIVERY_ONLY_WITH_LIMITS`。
- R0 发现两个目标 scratch leaf 存在，但未盘点 children，故 empty-or-absent 仍=`UNPROVABLE`。R0 Review P2-3 释放当前受限 Task。R0 capture 中 13 项固定 protected-file pre/post hash 一致；不把该结果外推为当前其他路径或未来执行不变量。

## 唯一下一步 runner 与停止边界

唯一允许的下一条执行为 Codex `exec_command`，参数 `shell="powershell.exe"`、`login=false`，`cmd` 直接使用上方 manifest fenced body；不写临时脚本、不调用外部 executable、不启动额外子进程。manifest body 会先核验 Windows identity/thread token；再核验已加载 Management/Utility 模块路径与 `G:` PSDrive provider/root；随后按冻结顺序逐项核验固定 ancestor/leaf 的 FileSystem provider、resolved `FullName`、普通目录及非-reparse 状态。只有各 leaf 完整路径链通过才列举该 exact leaf 一次，只记录 direct-child count。

Profile 启动行为与实际模块/provider/path 状态在当前 checkpoint 时仍未知；`login=false` 不被描述为 `-NoProfile` 证明。若固定 runner 在启动前被拒绝，维持 `NOT_RUN`；若 shell 启动后出现身份不符、模块/provider 不符、未知进程、冻结范围外访问、reparse/类型异常、未授权写入或输出异常，立即停止，不重试、不清理，并将 capture 记为已启动但不完整，相关项按证据记 `UNPROVABLE` 或 `NOT_SAFE_FOR_R0`。任何命令错误保留原始工具输出。

运行结果只允许按真实证据分类：零 direct child=`PASS_WITH_EVIDENCE`（仅该路径与采集时点）；有 child=`FAILED`（仅该时点 empty-or-absent 条件不成立）；查询/身份/权限证据不足=`UNPROVABLE`；命令或范围的安全性不明=`NOT_SAFE_FOR_R0`。LPAC/token/canary、future freshness、concurrent child/cache/TEMP/write closure 仍是 `REQUIRES_ACTIVE_TEST` 或既有 `UNPROVABLE`。不能凭静态 advisor 或此 checkpoint 记 gate pass。

## Gate 与任务恢复

当前 `private_registry_absence=UNPROVABLE`，owner waiver 保持；Technical Gate=`NOT_SATISFIED`；P02PRE=`BLOCKED`；profile=`NOT_CREATED`；ACL/registry=`NOT_MODIFIED`；Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`（尚未执行，不是失败）。未运行 parser、OS capture、build 或 AC。

捕获完成后，将原始完整工具 stdout/stderr、确切时间/PID/identity、模块/drive/ancestor 结果、两个 leaf 的分类、工具 exit status 和 evidence hash 写入 Task 指定 evidence；再由 DeepSeek Harness 对 Task、pinned manifest/checkpoint、原始 evidence 与分类独立 Review，最后 Codex adjudication。不得把静态 advisor 结论当作 Review，也不得解除 Hard Build Barrier。下一轮从 `P02PRE-R0S1` capture 开始；若状态与本 checkpoint/Live Git 冲突，先核验而不覆盖作者文件。

## Checkpoint 创建后、capture 前核对

时间=`2026-10-11 08:26 Asia/Shanghai`。再次执行安全 NUL status，exit=`0`、`523 records`、stderr 空；命令前后 `.git/index` SHA-256 均=`214767403C469B15D2BDEE786080E58B4D78BF12C541B9FFB7E8A7FA08F3B89C`；HEAD/branch/tree/worktree count 仍与上述一致。再次读取并核验 Task pin=`8303 bytes / BD73A543B2DBA2A28A38493769B64770C88DB14188D6BBD97189EA903082E2AD`、manifest pin=`22925 bytes / CA293C34473D25E406E72B7DB05AC9364A69544D41214B93857ABAD11FEC6DE3`，均匹配。本段仅记 Git/file hash getter；尚未启动 R0S1 PowerShell capture。
