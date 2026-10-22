P02PRE-R1H round-two Owner 修订的独立静态 Review

你是非作者 Reviewer `/root/p02_r1h_remediation_review`。本次 Owner=`/root/p02_r1h_codex_owner` 已完成实现；Integrator/Adjudicator=`/root`。你未参与本轮实现，不得修改候选或审核自己的工作。

## 冻结输入

- 仓库：`G:\CODEX\New Manga`
- Owner worktree：`C:\Users\49745\.codex\worktrees\p02pre-r1h-codex`
- Branch：`agent/codex/P02PRE-R1H`
- Frozen Task base：`946938bd0696dfddd01f87d61fe6723c63ecdc86`
- 前一 delivery：`4a02811d6edf9ab423d299a36c51f103e62dd5f3`
- 本轮 delivery HEAD：`92c90a9ba20f7a1b4ab090837f99c191745524f6`
- Tree：`c70bd6c756b5d6931d07a483c958131cd2934a04`
- 完整输入 pins：`verification/P02/codex-p02pre-r1h-remediation2-review-input-pins-20261012.json`
- Frozen Task：`doc/tasks/P02PRE-R1H.md`，17675 bytes / SHA-256 `67E063CC603125E99435A11C67E18BCE111A89B2365D07CDEF2D8D198038121C`
- Pins file：3866 bytes / SHA-256 `1AF1D4815B0902B3149056BFA27842FB6EBA6C318709F3A66DFB7F5B0ACC0FB9`
- Review 输入冻结后应有 11/11 source/candidate pins MATCH；逐项复核后才开始 Review。发现不匹配时停止实质审查并报告 `INPUT_PIN_MISMATCH`，不得自行更新 pins。
- Review 完整 diff：frozen Task base → delivery HEAD；候选只能是下列三条路径。

## 唯一允许写入

`verification/P02/codex-subagent-p02pre-r1h-static-review-remediation2-20261012.md`

## 审查要求

1. 独立审查 Task、manifest、round-two delivery 完整 diff、Handoff、旧 Review/adjudication 与输入 pins。给出 `VERDICT`、P0/P1/P2/P3 计数、稳定 finding ID、级别、文件及行号、触发条件、影响、最小修复建议与各验收项 disposition。
2. 重新裁定 R1H-001：缺失精确冻结的 main/scratch status/index 预期时，必须在相关仓库查询、inventory、target 触碰前 `UNPROVABLE` fail-stop；不可用 live read 代替冻结基线。
3. 重新裁定 R1H-002/003：拒绝 nonzero/unmerged/repeated/conflicting/malformed Git stages；只允许可明确证明的 ordinary non-reparse file leaf，未知对象必须 stop。
4. 重新裁定 R1H-004/005：self-check 是否检查真实候选 AST/control flow；已知 `[string]::IsNullOrEmpty`、`[Math]::Max` 纯内存调用是否以最窄准确规则允许，其他/动态/外部 InvokeMember 是否拒绝；正例与外部调用负例能否从静态结构中看见。不得把“预计可运行”描述成 self-check 已执行。
5. 重新裁定 R1H-006：检查是否绑定真实 component loop/direct blocks，覆盖 skip 前后到 outer `continue` 的整个路径、状态修改、`break`/`continue` 旁路，以及注入 hash、ACL、枚举、target read、状态变更或控制流移除的 in-memory AST/source mutation negative cases。注意任何位于已检查 loop 外、`continue` 前的调用缺口。
6. 检查 exception path、fail-stop/error handling、Handoff 声明与允许路径/API/子进程是否仍满足 frozen Task。不得超出 Task 扩大执行权限。
7. 对每项区分静态结论、实际运行证据与未知项；结论只属于 Review。即使静态 Review 通过，也不代表集成、parser/self-check、P02PRE、Gate、Build 或 AC PASS。

## Review 边界

- 仅静态读取文件、审查完整 diff 和必要的只读 Git 元数据。
- 严禁运行 PowerShell parser、candidate self-check、preflight、capture、任何 getter/API、测试、Build/Cargo、AC1–AC7、OS 动态验证或 Windows Sandbox。
- 不修改 Task、manifest、Plan、STATUS、索引、checkpoint、候选、pins 或其他报告。唯一写入上面指定的 Review 报告。
- 不要访问 `.tmp.driveupload`；任何 `git status` argv 必须独立传入 pathspec `:(exclude).tmp.driveupload`。
- 记录实际读取的文件、只读命令及结果、模型/力度和限制。不得将 dispatch/工具故障说成代码失败。

前轮 Review 为 `CHANGES_REQUESTED`，R1H-005/006 曾被 Codex adjudicate 为 P2 findings；本轮必须根据 frozen HEAD 的完整 diff 重新审查，不沿用旧结论。提交报告后等待 Integrator adjudication；不要自行集成或释放 successor。
