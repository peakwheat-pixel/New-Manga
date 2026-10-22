P02PRE-R1H round-three Owner 修订独立静态 Review

你是非作者 Reviewer `/root/p02_r1h_remediation_review`。你未参与此次 Owner 实现；Owner=`/root/p02_r1h_codex_owner`；Integrator/Adjudicator=`/root`。请只审查下列冻结 commit，不要修改 candidate 或治理文件。

## 冻结输入

- Repository=`G:\CODEX\New Manga`
- Owner worktree=`C:\Users\49745\.codex\worktrees\p02pre-r1h-codex`
- branch=`agent/codex/P02PRE-R1H`
- frozen Task base=`946938bd0696dfddd01f87d61fe6723c63ecdc86`
- previous HEAD=`92c90a9ba20f7a1b4ab090837f99c191745524f6`
- delivery HEAD=`0ecada4182d624d4f352a253e09db3bdecbee5d1`
- tree=`06986f47ac8363a32ecbf2d0e41ec1d680510940`
- current Task=`doc/tasks/P02PRE-R1H.md`，22941 bytes / SHA-256 `45671AD744C2CD51D831F3513F16CE573D24E7A0CF679DC087E98A29B27A4486`
- full source/candidate pins=`verification/P02/codex-p02pre-r1h-remediation3-review-input-pins-20261012.json`，3599 bytes / SHA-256 `502D164909D99C1BB6E9C4DB918D268181DE5C629F377764103DFBBDCD1CD655`

逐项复核 10 个 source/candidate pins。任一不匹配即停止实质 Review，报告 `INPUT_PIN_MISMATCH`，不得更新 pin JSON。

## Review 范围与唯一写入

审查 frozen Task base→delivery HEAD 完整 diff，且仅以下三条 candidate paths：

1. `verification/P02/p02pre-r1h-capture.ps1`
2. `verification/P02/p02pre-r1h-selfcheck.ps1`
3. `verification/P02/p02pre-r1h-handoff-20261012.md`

唯一允许写入：`verification/P02/codex-subagent-p02pre-r1h-static-review-remediation3-20261012.md`。

## 核心验收

1. 重新裁定 R1H-006 prefix finding：检查是否绑定真实 candidate outer loop `$candidateLoop.Body`，完整约束从 candidate 路径处理入口至 component `pathLoop` 前的 13 条 direct statement，并覆盖 nested staging branch/guard、commands、member calls、assignments 和控制流。确认允许的路径归一化、staging exclude、必要初始化均是精确 allowlist。
2. 静态检查四个 mutation fixtures 是否真实锚定到 candidate outer-loop prefix，并会因 contract 拒绝 ACL (`Get-Acl`)、目标内容读取 (`[IO.File]::ReadAllText`)、hash 与 directory enumeration 的注入；确认这些 fixtures 只把变异源码当作内存文本解析/检查，绝无执行注入内容的代码路径。不得运行这些 fixtures。
3. 验证 loop prefix 的邻接、候选路径解析、嵌套语句、异常路径不会允许未经审核的 member/command 或路径操作；仅验证 Task 要求的局部属性，不得扩大 Task 范围。
4. 重看 R1H-005 精确 pure-memory helper allowlist 和正/负例；重看 R1H-001/002/003 静态 fail-stop/stage/type 修复未回归。检查 Capture/Handoff、失败路径与输出保留声明是否匹配冻结 Task/manifest。
5. 给出 `VERDICT`、P0/P1/P2/P3 计数、稳定 finding IDs、严重度、精确文件/行号、触发条件、影响、最小修复，以及 R1H-001..006 和 AC1–AC7 disposition。区分静态意见、实际运行证据与 `NOT_RUN`；Review 成功也不等于集成、P02PRE、Gate、Build 或 AC PASS。

## 限制

- 仅静态阅读、完整 diff 与必要只读 Git 元数据。
- 禁止 PowerShell parser、candidate self-check、preflight、capture、getter/API、任何 tests、Build/Cargo、AC1–AC7、OS dynamic 或 Windows Sandbox。
- 不修改候选、Task、manifest、Plan/STATUS/index/checkpoint、pins 或其他报告。只能写上方 Review 报告。
- 不访问 `.tmp.driveupload`；运行 Git status 时把 `:(exclude).tmp.driveupload` 作为单独参数。
- 报告实际读取文件、只读命令/结果、pins pre/post 结果、限制和 Review 时间/角色。不要将静态推理描述成执行通过。

前两轮存在真实 P2 findings；这次须独立重新审查 frozen complete diff，不能只沿用 Owner 摘要或旧意见。提交报告后由 `/root` root adjudicate；你不得集成或释放 successor。
