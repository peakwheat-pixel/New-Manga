---
id: P02PRE-R1
title: P02PRE R1 宿主只读取证与证据 adjudication
kind: verification
status: closed_with_limitations
approval: user_authorized
suggested_owner: Codex
owner: Codex
reviewer: DeepSeek Harness
depends_on: [P02]
base_commit: cddff58469b56e181019a8ddfeade80684bc7eb9
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
---

# P02PRE-R1：宿主只读取证与证据 adjudication

## 来源与目标

用户最新裁决继续授权 P02 一次性持续推进，并将 runner/source-contract 与 host getter 的绝对无副作用预证明风险纳入 Owner Risk Acceptance。R0 阶段结束；不重做 R0 runner/source 静态研究。此 Task 只采集 r6 已列对象的宿主基线，作为后续 native dynamic isolation Task 的输入；不把查询成功解释为 Gate PASS。

保留原风险裁决：`private_registry_absence=UNPROVABLE`、Technical Gate=`NOT_SATISFIED`、Owner Risk Acceptance=`APPROVED`、Gate Disposition=`WAIVED_BY_OWNER`；必须逐字记录 `technical condition unmet; user explicitly accepted residual risk`。R1 采集授权不等于新的风险豁免。Build Gate=`BLOCKED`，Hard Build Barrier=`EFFECTIVE`，Build/Cargo 与 AC1–AC7=`NOT_RUN`。

## 基线、角色和交付物

- 仓库=`G:/CODEX/New Manga`；branch=`main`；base HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`；tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`；working tree dirty，所有既有未提交内容原样保留，未知作者归属不推断。
- Owner/Author/Integrator/Adjudicator=`Codex /root`；非作者 Reviewer=`DeepSeek Harness`。
- r6 source manifest=`verification/P02/p02-owner-risk-waiver-execution-manifest-r6-20261011.md`，SHA-256=`626E000A94C8C3561DBB13BFA4C5BC66DA315001B9F50B5AC1669339407009DE`。
- Frozen capture manifest=`verification/P02/p02pre-r1-manifest-20261011.md`；精确脚本=`verification/P02/p02pre-r1-capture.ps1`；唯一运行结果=`verification/P02/p02pre-r1-evidence-20261011.json`；独立 Review、Codex adjudication 与 checkpoint 见同目录对应文件。
- Round 2 parser evidence：Windows PowerShell `5.1.26100.9549`，stdout=`verification/P02/p02pre-r1-windows-powershell-parse-20261011.stdout.log`（45 bytes，SHA-256=`C076120D0E62CF013CE1C521C5F091133497468263805D4B417F968B910D952A`）、stderr=`...stderr.log`（0 bytes，SHA-256=`E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855`）、exit=`...exit`（2 bytes，SHA-256=`9A271F2A916B0B6EE6CECB2426F0B3206EF074578BE55D9BC94F6F3FE3AB86AA`，内容为 `0\r\n`）。该命令仅 `ScriptBlock::Create` 解析，不调用脚本。
- Round 2 frozen review inputs：manifest=`11206 bytes / SHA-256 594690BF104A657064A82C96B1E4FB3421AA37E24701799C429D0F6C55E13212`；capture=`35725 bytes / SHA-256 CAC5F08C10555F7A68C047CFA6D33287671581CB56CF9BDDE5D98243D0BA1A0D`。Task 与 prompt 的 hash pin 在本 Task 的 Round 2 Review 证据记录中给出。
- Round 2 修复后 parser evidence：Windows PowerShell `5.1.26100.9549`，stdout=`verification/P02/p02pre-r1-windows-powershell-parse-r2-20261011.stdout.log`（45 bytes，SHA-256=`C076120D0E62CF013CE1C521C5F091133497468263805D4B417F968B910D952A`）、stderr=`...stderr.log`（0 bytes，SHA-256=`E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855`）、exit=`...exit`（2 bytes，SHA-256=`9A271F2A916B0B6EE6CECB2426F0B3206EF074578BE55D9BC94F6F3FE3AB86AA`，`0\r\n`）。只运行 `ScriptBlock::Create`，未调用脚本。
- Round 3 冻结 Review 输入：manifest=`11908 bytes / SHA-256 06E3351D0DBF0CC5194D61A6E491151CFC58D2FA837DEF97BDCE1F1BC3C01FD2`；capture=`37945 bytes / SHA-256 E97AD8A05B36753FC3F646E480628665328442B0EE8BAACB5C80B45DBDBB5893`。Task 与 Round 3 prompt 的 byte/hash pins 记录在 Round 3 Review prompt 与本 Task 后续版本。
- Round 2 Review=`CHANGES_REQUESTED`（新计 P0/P1/P2/P3=`0/0/3/2`）；Report=`verification/P02/dsh-p02pre-r1-review-r2-20261011.md`，原始 JSONL/stderr/exit 同目录；Reviewer 9 项 Round 1 finding 判 `CLOSED`、P1-1 与 P3-1 判 `PARTIALLY_CLOSED`，并提出 3 P2、2 P3。DSH 再次无法 hash-pin 文件（Win32 5），未运行任何 query/capture。Codex 接受实际缺口，并会把 WER registry 计数写成显式独立累加以消除审查歧义。

## Acceptance Criteria

- [x] manifest 与脚本经非作者 DeepSeek Harness Review；DSH 审阅冻结内容、查询对象、进程、停止条件和唯一证据写入范围。DSH 因 sandbox 初始化 Win32 5 无法独立复算文件 hash；Codex 对最终 manifest/script SHA 做本机三方法复算并在 adjudication 中记录此限制。
- [ ] 仅在核实当前用户/SID 与仓库、scratch 目标匹配后执行；记录 T0、当前进程身份/token 摘要、精确命令/子进程、Git 基线、受保护文件 SHA-256、R6 12 个只读输入根、13 个候选输出叶、3 个 canary 叶、R6 指定 TEMP/cache 环境项、精确 WER registry getter 与 3 个 WER 目录 metadata/ACL。
- [ ] 用户文件、漫画、数据库、Lock、Revision、凭据、模型、WER dump 内容不读取；任何现有输出内容不改、不移、不删，不写 protected path，不修改 ACL/owner/label。
- [ ] 只允许将结构化结果用 `FileMode.CreateNew` 写入唯一证据文件；文件已存在、目标身份错误、Git target 错误、证据异常或范围外进程/访问即停止，不覆盖、不重试、不清理。
- [ ] 逐项分类为 `PASS_WITH_EVIDENCE`、`FAILED`、`UNPROVABLE`、`REQUIRES_ACTIVE_TEST` 或 `NOT_SAFE_FOR_R0`；最后一类仅标注历史 R0 结论，不作为 R1 阻塞理由。未执行不记为 `FAILED`。
- [x] 非作者 Review 与 Codex pre-run adjudication 分开记录；本次 R1 只授权单次只读取证，不自动满足或解除其它技术 Gate。profile API/ACL/registry 写、Build/Cargo 与 AC1–AC7 须按后续对应 Task、证据和 Gate 单独 adjudicate。

## 精确范围

唯一执行脚本是 `p02pre-r1-capture.ps1`，所有查询方法、路径、registry view/value 与环境变量以 R1 manifest 为准。没有外部下载，没有依赖安装，没有 profile/Create/Delete，没有手工 registry 写、ACL 变化、canary 写入、build 或 AC。

允许读取对象只有：R6 固定 12 个 tool/input 根、13 个 output leaf、3 个 canary leaf；R6 明列的 TEMP/cache/config 环境变量；R6 的两个 LocalDumps key 在 Registry32/Registry64 的 key existence 与四个固定 value 名；R6 三个 WER 目录的 metadata/ACL（不列举内容）；main/scratch 两个项目仓库的固定 Git metadata 与 Git 已登记 regular files hash。Profile API path、API-owned registry store、per-image WER subkeys、WER dump 内容、用户数据以及其它路径均不扩展；缺少接口证据的部分归 `UNPROVABLE` 或 `REQUIRES_ACTIVE_TEST`。

## 写入范围

Codex 唯一可写文件：本 Task、`verification/P02/p02pre-r1-manifest-20261011.md`、`verification/P02/p02pre-r1-capture.ps1`、`verification/P02/p02pre-r1-evidence-20261011.json`、Round 1/2/3/4 的 `dsh-p02pre-r1-review[-r2|-r3|-r4]-20261011.prompt.md`、Round 4 focused follow-ups 的 `dsh-p02pre-r1-review-r4-followup[-2]-20261011.prompt.md`，以及相应 `.stdout.jsonl`、`.stderr.log`、`.exit`、`.md`；本次 post-run evidence review 的 `verification/P02/dsh-p02pre-r1-evidence-review-20261011.prompt.md` 及对应 `.stdout.jsonl`、`.stderr.log`、`.exit`、`.md`；`verification/P02/p02pre-r1-windows-powershell-parse-20261011.stdout.log`、`.stderr.log`、`.exit`、Round 2/3 parser 的 `verification/P02/p02pre-r1-windows-powershell-parse-r[23]-20261011.stdout.log`、`.stderr.log`、`.exit`、R4 hash-bound parser=`verification/P02/p02pre-r1-windows-powershell-parse-r4-20261011.json`、`verification/P02/p02pre-r1-adjudication-20261011.md`、`verification/P02/codex-checkpoint-p02pre-r1-20261011.md`。只可按项目治理职责更新 `doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/00_INDEX.md`、`doc/tasks/README.md`、`doc/tasks/P02.md` 的状态/Task 导航/链接。其它代码、用户文件、历史 Task/Review/evidence、scratch 与 worktree 均只读；既有未提交修改一律保留。

## Independent Review Round 1 与 Codex disposition

2026-10-11 DeepSeek Harness Review=`CHANGES_REQUESTED`，P0/P1/P2/P3=`0/2/6/3`；完整 report=`verification/P02/dsh-p02pre-r1-review-20261011.md`，原始 DSH JSONL/stderr/exit 同目录。Reviewer 未发现越界写入/路径，但指出证据超限会无证据退出、Git status hash 不是原始 bytes，并指出 home 口径、QUERY_ERROR/ACL 稳定性/reparse、Git metadata 汇总、registry enum 可读性、last-write 标记、NUL 计数和 serializer 错误归因缺口。Codex 接受全部 11 项为修订范围；DSH 无法独立复算文件 bytes/SHA，因为其只读环境 ACL 初始化失败（Win32 5），该限制保留，不声称 hash 级独立绑定。

Codex R2 修订包含：raw stdout bytes 与 hash/Base64；drive root 至对象的逐段 reparse 检查；身份/home 对照与 whoami fail-stop；bounded partial evidence 与 hash/计数保留；Git metadata/index 前后稳定断言；ACL endpoint SDDL/owner/祖先链对照和 query-error 聚合；enum 名称+数值；明确 status NUL 口径及 WER last-write unavailable 标记。R3 修订追加：partial 保留原始 stop reason；WER directory/registry query error 分开统计并显式进入 fail-stop；owner/SDDL 不可核验记 `ACL_UNVERIFIABLE`、分类 `UNPROVABLE` 并停止后续依赖；write failure exception 带 stop reason；文本解码口径与 encoding/code page 同原始 bytes 一并记录。未被 R1 查询证明的 `tempCache`、有效 WER policy、缺失目标 ACL 和 access/child/write closure 仍保持 `UNPROVABLE` 或 `REQUIRES_ACTIVE_TEST`。第二轮 Review 已发现 3 P2/2 P3；第三轮 parser 与复审通过、Codex adjudication 完成前禁止 capture。

## Independent Review Round 2 与 Codex disposition

2026-10-11 DeepSeek Harness Round 2=`CHANGES_REQUESTED`，P0/P1/P2/P3=`0/0/3/2`；review input Task=`9028 bytes / SHA-256 6E901052AADA0242CA65EFD98E1283F789762322EEAA6956303F2CEBDA15C4C8`、prompt=`6100 bytes / SHA-256 64B387FC705A6234028B141CDF7AE8CF14C61BD598DF6863B345EEB998B4E643`；完整报告=`verification/P02/dsh-p02pre-r1-review-r2-20261011.md`（`18951 bytes / SHA-256 DD49F407A2C639DBC53427C5459622D33CBF6B6AC9B56C2335CCD754FD3BF6D8`），原始 stdout JSONL=`94518 bytes`、stderr=`0 bytes`、exit=`0`，同目录可追溯。Reviewer 把 Round 1 十一项判为 9 closed、2 partially closed（P1-1 / P3-1），新增：P2-1 size partial 覆盖既有 stopReason；P2-2 WER registry getter error 可能未进 fail-stop；P2-3 owner/SDDL 空值可能假 PASS；P3-1 写文件失败异常未带原 stopReason；P3-2 whoami 展示文本解码口径未记录。Reviewer 未发现范围外读取写入/进程；未执行 capture、OS query、Build/Cargo/AC；bytes/SHA 仍因其沙箱 ACL Win32 5 未独立复算。

Codex 对 Round 2 的临时 finding 处置（最终集成 adjudication 尚未完成）：P2-1、P2-3、P3-1、P3-2 为实际证据语义缺口，本轮已修订。P2-2 的旧脚本将 `$werRegistryQueryErrorCount` 包含在 `$werQueryErrorCount` 并使其进入 `$queryErrorCount` fail-stop；Round 2 将它描述为“不含 registry”与源码表达存在分歧，Codex 未把该原始断言当成已证缺陷，但为消除歧义改成独立的 directory 与 registry 计数并明确相加。R3 确认旧 finding 闭合，且确认 Round 1 与 Round 2 其余 finding 均已闭合；只处理静态证据/停止语义，不放行 host capture。

## Independent Review Round 3 与 Codex 修订

2026-10-11 DeepSeek Harness Round 3=`CHANGES_REQUESTED`，P0/P1/P2/P3=`0/0/1/2`；报告=`verification/P02/dsh-p02pre-r1-review-r3-20261011.md`（`17502 bytes / SHA-256 0CFD9402D196E4BB1477A1325F6FD6D26331F4993C0956565795F8A9D7CBA4B9`），raw JSONL=`75672 bytes / SHA-256 8FCCC62D2E56DCEBB5805683B302DEC6EEAA8047DC17CDC4B07556D111DDD62A`、stderr=`0 bytes`、exit file=`0`，session=`session-a98bffe4-310e-4726-8125-830ca5d0f02c`。Reviewer 逐项确认 Round 1 的 11 项与 Round 2 的 5 项均 `CLOSED`；指出 R3 唯一 P2 是 `ACL_UNVERIFIABLE` 仍可让 `hostPathSnapshots`=`PASS_WITH_EVIDENCE`，另有 manifest 轮次自述滞后，以及 `Get-Acl` 异常会丢掉已取得的 `directEntryCount`。Reviewer 未发现越界路径、进程、读写或新副作用；未运行 capture/query/Build/Cargo/AC。hash 级独立复算仍受 DSH sandbox ACL 初始化失败（Win32 5）限制，不声称已独立绑定。

Codex 已修订：路径存在/形态可查但 ACL owner/SDDL 不可核验时 `hostPathSnapshots`=`UNPROVABLE`；ACL getter 异常改为 `ACL_QUERY_ERROR`，保留此前取得的 metadata/attributes/direct entry count，并使 host path/ACL 快照失败；输出叶使用已取得的 direct entry count 判断非空，不依赖状态为 `PRESENT`；manifest 更新为当前 R4 冻结轮次。Windows PowerShell 5.1 `ScriptBlock::Create` 只读 parse=`PARSE_OK`，stdout=`verification/P02/p02pre-r1-windows-powershell-parse-r3-20261011.stdout.log`（45 bytes / SHA-256 `C076120D0E62CF013CE1C521C5F091133497468263805D4B417F968B910D952A`），stderr=`verification/P02/p02pre-r1-windows-powershell-parse-r3-20261011.stderr.log`（382 bytes / SHA-256 `4F2B6B3ED9201CA459DB2DD042E0A137C4E58BFE8E15A068E45AD8535FA5B1EF`，仅含 PowerShell 启动进度 CLIXML），exit=`verification/P02/p02pre-r1-windows-powershell-parse-r3-20261011.exit`（`0\r\n`, 3 bytes / SHA-256 `13BF7B3039C63BF5A50491FA3CFD8EB4E699D1BA1436315AEF9CBE5711530354`）。该命令仅解析源码，未调用 capture 脚本。Round 4 独立聚焦复审待执行，R1 capture 仍未运行。

## Independent Review Round 4 与 Codex disposition

2026-10-11 DeepSeek Harness Round 4=`CHANGES_REQUESTED`，P0/P1/P2/P3=`0/0/0/1`；报告=`verification/P02/dsh-p02pre-r1-review-r4-20261011.md`（`18995 bytes / SHA-256 DD099DCDCA59E1C7EBBB5B9A938C2F50BF31A9F5B39872B738874CF4DEB7ED98`），raw JSONL=`82278 bytes / SHA-256 2B9C35C3DE3FC2AD938B8BD5862898A15ABFAB181A341DADDA7FBE8BFB693E45`、stderr=`0 bytes`、exit file=`0`，Reviewer session=`session-a98bffe4-310e-4726-8125-830ca5d0f02c`。Round 1/2/3 的 19 项 findings 全部判为 `CLOSED`；R3 三项修复与 `ACL_QUERY_ERROR` 全链路均确认正确；脚本无新技术或副作用 finding。唯一新项=`P3-DOC-1`：manifest `:13` 仍写第二轮 Review，且 `:9` 末尾未说明 R3 三项现已在 R4 修订。Reviewer 因此仍判 `CHANGES_REQUESTED`。DSH 未执行命令/采集，未写文件；其沙箱 ACL 初始化 Win32 5 导致 hash pins 未独立复算。

Codex 已按最小范围修正 manifest 两句，脚本与其 SHA 不变；R4 parser 证据=`verification/P02/p02pre-r1-windows-powershell-parse-r4-20261011.json`（`2086 bytes / SHA-256 1AE3462C5EB16E85B47A03E90CBC53DA33F5EAD74BFCFB1992BADC5F6A805841`）。其中 Windows PowerShell `5.1.26100.9549` 的 `ScriptBlock::Create` 对与冻结脚本一致的 `38729 bytes / SHA-256 97400A9EF16E47242DA3C4E53C8265F16BA9A70853B26D3905748B9CA69884AB` 输入返回 `PARSE_OK`、进程 exit=`0`、`captureScriptInvoked=false`；输入 hash 在 parser 同一进程读取的 bytes 上计算，父进程 recheck 相同；startup progress stderr bytes/hash/base64 也在证据中保留。随后由原非作者 Reviewer 对 manifest、Task、脚本 pin 和 hash-bound parser evidence 做 focused follow-up；通过后再由 Codex adjudicate。当前仍禁止 host capture，直到 follow-up 与 adjudication 完成。

### Round 4 focused follow-up #1 history（状态已由下文取代）

Focused report=`verification/P02/dsh-p02pre-r1-review-r4-followup-20261011.md`（`15629 bytes / SHA-256 BFED4454E5F338C59CC2E942D96A48634F67B54DCCED33CECE14C63DFACEA9B9`），raw JSONL=`53111 bytes / SHA-256 90E9167879413D1CDABF2BA8AB7B773EAA0F1DAB5ABDF7F78B92B7EEE5725900`、stderr=`0 bytes`、exit file=`0`；结果=`CHANGES_REQUESTED`（`0/0/0/1`）。报告确认 `P3-DOC-1` 已闭合，parser 证据字段内部一致，脚本仍与 R4 全量审查版本一致；新报 `P3-PIN-1`，声称 prompt 脚本 pin 为 `97400A...` 而 parser JSON 三处为 `97D00A...`。

Codex 对该 pin finding 做只读取证复核：PowerShell .NET SHA-256、`Get-FileHash`、`certutil -hashfile` 对脚本 `38729 bytes` 均返回 `97400A9EF16E47242DA3C4E53C8265F16BA9A70853B26D3905748B9CA69884AB`；parser JSON 的 `childParseResult.inputSha256`、`parentRecheck.inputSha256`、解析 `childStdout.utf8` 后的 `inputSha256` 均完全相同，且与 R4 prompt pin 一致。第三字符码点为十进制 52（`4`），并非 `D`。因此报告中的 `97D00A...` 属于 Reviewer 转录错误，不是仓库 pin/证据不一致。为保留非作者复核链，Codex 正向原 Reviewer 派发极窄确认，附上述机器输出；capture 在该确认与 Codex adjudication 前保持未运行。

### R4 follow-up #2/#3 与 Codex pre-run adjudication（当前）

- Follow-up #2=`APPROVED`（P0/P1/P2/P3=`0/0/0/0`），报告=`verification/P02/dsh-p02pre-r1-review-r4-followup-2-20261011.md`（`6572 bytes / SHA-256 BFEA7516C815F4236A6A7421214720D809164785FD55B8AF1EC22D7F8D576D8E`）。Reviewer 将 `P3-PIN-1` 关闭为其自身报告的字符转录错误，并明确未独立复算 hash；其可见字面值核对与 Codex 三方法复算分开记录。
- Codex 在 live file 中发现 manifest line 9/13 仍有“等待本轮 Review”的过时状态，仅修订这两处流程文字。最终 manifest=`verification/P02/p02pre-r1-manifest-20261011.md`（`12615 bytes / SHA-256 A5510774B47C17EB29C5BF5D73FE7B755C72E2726FC5280E7EF11A91A23C67A7`）；capture script 未改，仍为 `38729 bytes / SHA-256 97400A9EF16E47242DA3C4E53C8265F16BA9A70853B26D3905748B9CA69884AB`。
- Follow-up #3 针对新 manifest bytes=`APPROVED`，P0/P1/P2/P3=`0/0/0/0`；报告=`verification/P02/dsh-p02pre-r1-review-r4-followup-3-20261011.md`（`9399 bytes / SHA-256 86445E85D5CA73C4549C58BCB31E92017CC59619AFFE18A4C53BDF310D52EB0A`），stdout JSONL=`45496 bytes / SHA-256 BC6A5BC8EFD83C150CD05B2C1EDCA70E0F89BD713EFD010FAB59DEDB178D68F2`、stderr=`0 bytes`、exit=`0`；同一 DSH session=`session-a98bffe4-310e-4726-8125-830ca5d0f02c`。Reviewer 报告三项非阻断文字观察，未新增 finding；没有执行命令、重跑源码 Review 或 hash 复算。
- Codex pre-run adjudication=`PRE_RUN_REVIEW_ACCEPTED; RELEASED_FOR_ONE_READ_ONLY_CAPTURE`，详见 `verification/P02/p02pre-r1-adjudication-20261011.md`。最终 manifest/script hashes 已分别用 .NET SHA256、PowerShell `Get-FileHash`、`certutil -hashfile` 复算且三者一致；R4 parser JSON 仍绑定该脚本 exact bytes、`PARSE_OK`、exit 0、`captureScriptInvoked=false`。独立 Review 不代表执行结果或 Gate PASS。
- R1 capture 尚未运行；pre-run adjudication 仅释放由冻结 manifest 定义的一次调用。运行前再次核对 identity/Git target 基线与唯一 evidence target absent；任何身份、路径、hash、ACL、getter、子进程、写入或证据异常均按 manifest 停止并保留 partial evidence，不重试、不清理。
- 风险/Gate 未变：`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；`technical condition unmet; user explicitly accepted residual risk`；Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；Build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`。

## 停机和后续依赖

身份或目标不符、`whoami`/Git 命令异常、精确证据输出已存在、受保护哈希无法完成、遇到 reparse/非 regular 文件无法安全归属、任一冻结 getter 的 query error、ACL endpoint 变化、未知进程或 evidence 写入异常时停止相应后续步骤。per-image/其它 WER scope 不枚举，保持 `UNPROVABLE`；R1 不声称监测了范围外访问或瞬时 ACL 写入。保留实际错误和 partial 结果，不尝试自动恢复。Round 4 聚焦 Review 与 Codex adjudication 通过前禁止唯一一次 host capture。

下一 Task=P02PRE-R2（native API/controller tool preparation 与动态隔离）：必须依赖本 Task Review/adjudication，冻结 controller/probe 源码、编译命令与输出路径后再交独立 Review；只有实际 identity、路径、ACL、TEMP/cache、protected state、WER/T0 与隔离闭包证据齐全时，Codex 才可 adjudicate 后续 Gate。R2 的 compile/helper 产物不等于产品 Build Gate。

## R1 单次 capture 与 post-run evidence review（2026-10-11）

- Capture 由 `p02pre-r1-capture.ps1` 精确调用一次，PowerShell 退出码=`1`，脚本按冻结停止规则返回 `MAIN_REPOSITORY_BASELINE_OR_HASH_FAILED`。证据=`verification/P02/p02pre-r1-evidence-20261011.json`，`2588454 bytes / SHA-256 8A1A056600F6A1B5C2E7980E4CCAE2B3DB085B1EF7EC7DC5CC7FD35A4A068B9C`；不得重跑或覆盖该文件。
- 已收集的字段显示身份=`PASS_WITH_EVIDENCE`；main Git target 与预期相符；受保护文件 inventory 在 `.codex/skills/ask-matt` 停止，原因是现有 tracked symbolic link/reparse point，未读取或跟随 link target；此前 662 个 regular files 的 SHA-256 已记录。后续 scratch/path ACL/TEMP/cache/WER getter 未执行，因此仍为 `UNPROVABLE`，不等同测试失败。原始 status snapshot=`651 NUL records / 41249 bytes / SHA-256 ECFEBBC7D617B06FCFFFDAE9041103785C6D04E48B40C10F1F38E372D3F29D02`；`.git/index` 前后 SHA 相同=`214767403C469B15D2BDEE786080E58B4D78BF12C541B9FFB7E8A7FA08F3B89C`。Capture 后只新增该证据文件；其后状态文件变更另行标注。
- Owner=`Codex /root`；本地进程执行者=`HOME-MY\49745`，SID=`S-1-5-21-2196946971-914346751-4210154634-1001`；非作者 Reviewer=`DeepSeek Harness`，同一项目 session。派发范围只读本 JSON 与本 Task/manifest，审查 stop reason、分类、hash/status/identity 摘要和 tracked-link 边界；禁止执行命令、重跑查询/capture、读取或跟随 link target、访问用户/漫画数据、改写任何现有证据。交付物为本节列出的 prompt/raw stdout/stderr/exit/report；验收为逐项证据一致性审查、诚实五态分类及独立 finding 清单，不授予 Gate PASS。
- Post-run review=`changes_requested`，报告=`verification/P02/dsh-p02pre-r1-evidence-review-20261011.md`，SHA-256=`3B949CF20160BFFC0122A489C632D00C7CF84540571305567B4A23D5DF701736`；raw stdout JSONL=`103356 bytes / SHA-256 685D388657C87FB65771E0AE2179968105E32114AE27AEDF4A096A92EE292CB6`，stderr=`0 bytes`，exit=`0`。DSH 未复算 evidence hash、未运行命令；Codex 本机已用 `Get-FileHash` 固定 evidence 与 Review artifact hashes。
- Codex adjudication 接受 F-01 至 F-04：原 capture 在首次 tracked reparse path 停机是安全且可解释的 partial 结果；同一脚本不得重跑。新 successor `P02PRE-R1F` 将在独立 Task/manifest/script 中对 Git index mode=`120000` 且 live object 为 reparse point 的对象只记录 mode/metadata 并明确 `SKIPPED_SYMLINK_NOT_FOLLOWED`，不跟随、不读目标、不 hash；任何模式不符的 reparse、其它非 regular 对象继续 fail-closed。R1F 同时修复空终止项计数及命令记录多余空对象问题，重新采集完整所需 getter，不复用旧 662 条 hash 作为当前状态。旧 JSON、manifest、script 保留不变。
- R1 的 single-capture attempt 以 `closed_with_limitations` 收口，依据为被新 no-follow capture 代替的采集路径；未完成 AC 均按实际证据保留为 `FAILED`、`UNPROVABLE`、`REQUIRES_ACTIVE_TEST` 或 `NOT_RUN`。这不是技术 Gate PASS，也不是 P02 完成。
- R1F 将作为下一独立 Task；只有其固定 manifest/script 经非作者 Review、Codex pre-run adjudication、一次新 evidence capture、非作者 post-run Review 和 Codex adjudication 后，才可向后续动态 isolation Task 交接。风险裁决与 Build Gate/Hard Barrier 保持原值。
