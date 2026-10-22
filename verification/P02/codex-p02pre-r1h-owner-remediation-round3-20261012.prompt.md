P02PRE-R1H Owner remediation round 3 — R1H-006 candidate-loop prefix

Owner: `/root/p02_r1h_codex_owner`。你完成了前一版实现；此次仍不得 Review 自己。Integrator/Adjudicator=`/root`；后续非作者 Reviewer=`/root/p02_r1h_remediation_review`。

## 冻结依据

- Repository：`G:\CODEX\New Manga`
- Owner worktree：`C:\Users\49745\.codex\worktrees\p02pre-r1h-codex`
- Branch：`agent/codex/P02PRE-R1H`
- Starting HEAD/tree：`92c90a9ba20f7a1b4ab090837f99c191745524f6` / `c70bd6c756b5d6931d07a483c958131cd2934a04`
- Frozen Task base：`946938bd0696dfddd01f87d61fe6723c63ecdc86`
- Task：`doc/tasks/P02PRE-R1H.md`，21160 bytes / SHA-256 `2E28B894347FB796978396014E4BC33E4590EFDEDD2F2DE1BCB195056E467491`
- Review/adjudication：`verification/P02/codex-subagent-p02pre-r1h-static-review-remediation2-20261012.md` 与 `verification/P02/p02pre-r1h-remediation2-adjudication-20261012.md`
- Source/start-candidate pins：`verification/P02/codex-p02pre-r1h-owner-remediation-round3-20261012.pins.json`，3440 bytes / SHA-256 `100DAFBD5CA10ADC2689EAB3553504DD18D73CA31E0FE2B863637272F1CBE335`

按 pins 先核验所有 source 与 starting candidate 文件字节数/hash。若任何值不符，停止实现并报告 `INPUT_PIN_MISMATCH`；不要更新 pins。

## 唯一目标

R1H-006=`OPEN / ACTION_REQUIRED / P2`。当前 self-check 绑定 component `pathLoop`，但没有约束真实 `$candidateLoop.Body` 内、该 `pathLoop` 之前的 prefix。Reviewer 静态指出，在 capture 的 `$linkSkipped = $false` 与 component loop 之间插入 `Get-Acl -LiteralPath $full` 或 `[IO.File]::ReadAllText($full)`，现有检查仍可能接受。

请做最小 self-check 修复：

1. 把真实 candidate outer loop 从 candidate 路径处理入口到 component `pathLoop` 前的语句纳入 AST contract；允许现有的合法 path normalization、staging exclude 和必须的初始化，但必须精确 allowlist，不能只检查 loop/pathLoop 邻接。
2. 检查 nested blocks、member calls、commands、assignment/state/control-flow，拒绝额外 ACL/query、内容读取、hash、枚举、target read、动态/未知成员调用和绕过控制流。
3. 添加真正作用于 candidate 源码的 in-memory mutation negative cases：至少在该 prefix 注入 `Get-Acl` 与 `[IO.File]::ReadAllText`；根据目前 contract 覆盖 hash/枚举注入，并确保 mutation 可命中 fixture 且 Contract 因禁用操作而拒绝。fixture 必须只把伪代码当文本解析/检查，绝不执行注入内容。
4. 保留上一版 R1H-001/002/003/005 静态修复和已有 self-check 正/负例；不扩展任何 API、path、产品/子进程、读写或执行范围。若某条合法 prefix 语法无法窄范围允许，保留 fail-stop 并在 Handoff 报明。

## 写入和检查边界

Candidate branch/worktree 只允许写入现有三条路径：

- `verification/P02/p02pre-r1h-capture.ps1`
- `verification/P02/p02pre-r1h-selfcheck.ps1`
- `verification/P02/p02pre-r1h-handoff-20261012.md`

优先仅改 `selfcheck.ps1`；Handoff 只在现有状态/限制必须同步时改。不得改 Task、manifest、REBASELINE_PLAN、STATUS、索引、checkpoint、pins、Review/adjudication、R1G 证据或其它路径。

唯一允许运行的检查为：`git diff --check`。禁止运行 PowerShell parser、candidate self-check、preflight、capture、任何 getter/API、tests、Build/Cargo、AC1–AC7、OS 动态验证或 Windows Sandbox。不得访问 `.tmp.driveupload`。该边界来自本 Task 的 Owner 写入/检查规则；用户持续授权不会把这些 Owner Task 限制变成测试结果。

完成后在同一 branch 提交有界变更，返回 new commit/parent/HEAD/tree、startingHead 与 frozen-base 两组路径范围/stat、controlled status 精确命令结果、`git diff --check` exit、三文件 bytes/SHA-256、实际命令和限制。不得自审、集成、声称 Gate/P02PRE/AC PASS。Codex 验收后交非作者独立 Review。
