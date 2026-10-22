# DeepSeek Harness Review Task：P02PRE-R1 R4 manifest 状态文字窄复核

Reviewer=`DeepSeek Harness`（沿用既定 DSH session）；Owner/Author/Integrator/Adjudicator=`Codex /root`。本轮只复核 manifest 中两处状态说明与当前 Review/adjudication 顺序是否一致，不重跑源码 Review，不执行命令或 OS/API/registry/WER/token/ACL/path/environment/hash query，不运行 capture，不修改文件，不 build/Cargo/AC，不改变 Gate。

## 固定输入

- 当前 manifest=`verification/P02/p02pre-r1-manifest-20261011.md`，`12615 bytes / SHA-256 A5510774B47C17EB29C5BF5D73FE7B755C72E2726FC5280E7EF11A91A23C67A`。
- Capture script=`verification/P02/p02pre-r1-capture.ps1`，`38729 bytes / SHA-256 97400A9EF16E47242DA3C4E53C8265F16BA9A70853B26D3905748B9CA69884AB`（脚本未改）。
- R4 parser evidence=`verification/P02/p02pre-r1-windows-powershell-parse-r4-20261011.json`，`2086 bytes / SHA-256 1AE3462C5EB16E85B47A03E90CBC53DA33F5EAD74BFCFB1992BADC5F6A805841`，其中 exact script input hash/bytes=`97400A9E…84AB / 38729`、`PARSE_OK`、`captureScriptInvoked=false`。
- R4 full Review=`verification/P02/dsh-p02pre-r1-review-r4-20261011.md`：`CHANGES_REQUESTED`，P0/P1/P2/P3=`0/0/0/1`，只剩 P3-DOC-1。
- R4 focused follow-up #1=`verification/P02/dsh-p02pre-r1-review-r4-followup-20261011.md`：P3-DOC-1 闭合；提出 P3-PIN-1，但把 `4` 转录为 `D`。
- R4 focused follow-up #2=`verification/P02/dsh-p02pre-r1-review-r4-followup-2-20261011.md`：`APPROVED`，`0/0/0/0`；P3-PIN-1 确认为 Reviewer 报告转录错误。Reviewer 明确没有独立复算 hash；它只确认文件内可见字符串一致。
- Task=`doc/tasks/P02PRE-R1.md`。Owner 授权的 gate 状态必须维持：`private_registry_absence=UNPROVABLE`、Technical Gate=`NOT_SATISFIED`、Owner Risk Acceptance=`APPROVED`、Gate Disposition=`WAIVED_BY_OWNER`、Build Authorization=`AUTHORIZED_WITH_EXCEPTION`、`technical condition unmet; user explicitly accepted residual risk`、Build Gate=`BLOCKED`、Hard Build Barrier=`EFFECTIVE`、Build/Cargo=`NOT_RUN`、AC1–AC7=`BLOCKED / NOT_RUN`。

## 复核问题

1. 阅读当前 manifest 的第 9、13 行及其周边流程文字，确认它们不再声称等待已经完成的 R4 Review；能否看出必须先由 Codex adjudicate 最终 manifest/script pins，随后才允许唯一一次只读取证？
2. 对照上述 R4 full/focused Review 与 parser 证据，确认文字如实记录：19 个历史 findings、P3-DOC-1、P3-PIN-1 均 closed；P3-PIN-1 是 Reviewer 自身转录错误；不声称 DSH 独立 hash；script/parser bytes 未变。
3. 确认两处 prose 更新没有扩张执行对象、路径、进程、argv、写入范围、AC 或 Gate 权限；脚本仍只有原 manifest 记载的唯一 `CreateNew` evidence target。

只作文件内容审查。若仅凭给定文件看不出某项，标 `NOT_VERIFIED`，不要推断为 PASS。R4 Report 的本轮结果仅供 Review/adjudication，不是技术 Gate PASS。

## 返回格式

使用简体中文，报告结论必须且只能为 `APPROVED`、`CHANGES_REQUESTED`、`NOT_VERIFIED`、`BLOCKED_BY_MISSING_EVIDENCE` 之一；列出 P0/P1/P2/P3 数量、上述三项逐条状态、任何 finding、DSH 是否独立复算 hash、当前 bytes 是否可进入 Codex pre-run adjudication。不要声称任何宿主条件已通过，不要运行或授权 Build/Cargo/AC。
