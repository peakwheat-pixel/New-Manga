# P02PRE-R1H Frozen Manifest — symlink representation recovery

## Authoritative inherited contract

本 manifest 的 inherited execution contract 精确固定为：

- Source manifest=`verification/P02/p02pre-r1g-manifest-20261011.md`，bytes=`26657`，SHA-256=`1111EB70AC8BCCA4A2D3C236E653553D6A52EA99F626670AE18D7FDDCDD430B8`。
- R1G Task=`doc/tasks/P02PRE-R1G.md`；R1G base=`cddff58469b56e181019a8ddfeade80684bc7eb9`；reviewed source commit=`946938bd0696dfddd01f87d61fe6723c63ecdc86`。
- R1H base/source branch commit=`946938bd0696dfddd01f87d61fe6723c63ecdc86`；branch=`agent/antigravity/P02PRE-R1H`；worktree=`C:\Users\49745\.codex\worktrees\p02pre-r1g\New Manga`。

R1G manifest hash 所冻结的身份、预期用户/SID/token、AppContainer profile/moniker/SID、registry/ACL getter、TEMP/cache/scratch/main paths、T0/WER paths、96 protected paths、Git executable/argv/order、excluded pathspec、child allowlist、failure-stop 规则与禁止写入范围均**原样继承，不作变更**。不得从聊天或其他历史文档替代该 hash-pinned manifest。

## 唯一功能差异

R1G 在 Git stage mode=`120000`、文件系统无 `ReparsePoint` 时 fail-stop。本候选仅可增加一个窄分支：当 Git/index stage 明确为 `120000`，路径是普通非目录 leaf，main/scratch frozen refs/index/status 均精确匹配，身份与其它前置条件通过时，允许记录 `SKIPPED_GIT_SYMLINK_NONREPARSE`，随后完全跳过该条目。必须证明该分支不读取/hash内容、不跟随 target、不查 ACL、不枚举子项、不解析 target；Git mode 或 filesystem object 有任何其它不匹配时维持 `STOP`。若其安全成立条件不能由当前冻结证据与已有只读查询证明，保持 `STOP / UNPROVABLE`，禁止 capture。

本变更只关乎 inventory 对 tracked symlink 的 path-only 处理，不改变 inventory 的根/文件范围、Git/query child、输入输出、profile/registry/ACL、TEMP/cache/WER 或写权限。

## Candidate / executor

- 新 candidate=`verification/P02/p02pre-r1h-capture.ps1`（以 R1G reviewed source 为基底的独立文件；禁止修改 R1G source）。
- 新 self-check=`verification/P02/p02pre-r1h-selfcheck.ps1`；仅 parser、纯函数/断言及 AST/control-flow 检查，不调用 capture、Git、host getter、registry/ACL/profile API、Build/Cargo/AC。
- 固定 child executable=`C:\Program Files\PowerShell\7\pwsh.exe`；必须是 PowerShell `7.6.6` / Core / FullLanguage / NoProfile。
- Child argv 与 R1G manifest 相同，唯一文件路径替换为 `verification/P02/p02pre-r1h-capture.ps1`；必须通过 `ProcessStartInfo.ArgumentList` 逐项传参并留证。不得使用拼接 command string。
- R1G 允许的 Git 与 `whoami.exe /all` 子进程及原有有序参数完全继承；不得新增 executable/API/query/path。

## R1H one-shot outputs

以下目标都必须在启动前逐一核验 absent，child exit 后用 `CreateNew` 写入；任一已存在即停止，不覆盖、不删除、不重试：

1. `verification/P02/p02pre-r1h-runner-evidence-20261012.json`
2. `verification/P02/p02pre-r1h-evidence-20261012.json`
3. `verification/P02/p02pre-r1h-capture-20261012.stdout.log`
4. `verification/P02/p02pre-r1h-capture-20261012.stderr.log`
5. `verification/P02/p02pre-r1h-capture-20261012.exit`

Parser/self-check、engine-preflight、final-pre-run、pin、Review、adjudication 与 checkpoint evidence 也必须使用此前确认 absent 的唯一名称和 `CreateNew`。全部 R1G output paths 永远只读保留。

## 不变量与放行条件

- P02 owner waiver 保持原值；`private_registry_absence=UNPROVABLE`、Technical Gate=`NOT_SATISFIED`、Owner Risk Acceptance=`APPROVED`、Gate Disposition=`WAIVED_BY_OWNER`、Build Authorization=`AUTHORIZED_WITH_EXCEPTION`，原文 `technical condition unmet; user explicitly accepted residual risk`。
- Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；Build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`。
- Capture 前需非作者独立 Review、root Codex 复算精确 pins、Codex adjudication、以 `CreateNew` 集成、PS7 parser/self-check、no-profile engine preflight 和最终 `PRE_RUN_PASS`。
- 每项身份、path、registry/ACL query、Git process、scratch、TEMP/cache、protected hash 与输出证据均按 R1G hash-pinned base contract执行；未知子进程、身份错误、任何未授权读写、基线变化、output collision 或 hash 异常立即 stop。
- R1H capture 最多一次。fail-stop 结果属于本 Task 的真实结果，不允许重试；之后由独立 post-run Reviewer 与 Codex 五态 adjudication。
- 禁止 Windows Sandbox、系统功能变更、profile 创建/删除、registry/ACL 写入、Build/Cargo 和 AC1–AC7。
