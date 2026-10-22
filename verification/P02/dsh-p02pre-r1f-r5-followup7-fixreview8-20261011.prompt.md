# DeepSeek Harness 独立只读 Review 委托 — P02PRE-R1F / R1F-R7 cohort #9（fixreview8）

## 角色与绑定

- Repo=`G:/CODEX/New Manga`；branch=`main`；base HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`；Task=`P02PRE-R1F`。
- 当前为 R1F-R7 governance cohort #9（label=`fixreview8`），不是 parser R8、capture round 或旧 R5 follow-up #8。
- Owner/Author/Integrator/Adjudicator=`Codex /root`；本轮非作者 Reviewer=`DeepSeek Harness`（必须使用全新 session）。
- 只读审查：不得编辑、创建或删除仓库文件；不得运行命令、脚本、Git、hash/API、host getter、profile、registry、ACL、capture、Build/Cargo 或 AC1–AC7。只读取冻结输入并在响应中交付报告。

## 审查任务

独立复核 R1F-R7 cohort #7/fixreview6 findings 修复和 cohort #8/fixreview7 未启动记录，并判定是否可结束文档/scope review 阶段。具体检查：

1. **cohort #7 原 findings**：Task 的当前 host capture 行要求最新 R1F-R7 Review=`APPROVED` 与 Codex adjudication 后还要 final pre-run 明确释放；STATUS 将 cohort #9 精确路径指向 manifest/checkpoint，并如实标记 pins pending，不误称 DAG 已列出。
2. **cohort #7 exit path integration 修复**：规范日期 `.exit` 和少日期 noncanonical sidecar 在 Task/manifest/checkpoint 中均被区分、保留且可追溯；二者均为 3 bytes/相同 SHA，文本记录 raw `30 0D 0A` 与 CLI exit=0。注意：DSH 报告本身没有运行命令/复算 hashes；Codex 负责证据和 adjudication。
3. **cohort #8 启动失败事实**：其状态必须为 `NOT_DISPATCHED / NOT_REVIEWED`，不得写成 DSH Review 或 CLI exit。确认 Python `FileNotFoundError (WinError 2)` 发生在 DSH 进程创建前；空 stdout/stderr 不是 reviewer 输出；`.exit` 是文字明确的 Codex dispatch marker、不是 CLI exit；没有 DSH session 或 verdict。Task 的 AC 未勾选。
4. **恢复路径**：Task/唯一 DAG/STATUS/Index/README/P02/checkpoint/manifest 均指向 cohort #9/fixreview8 为唯一下一 READY；Owner=`Codex /root`、Reviewer=`DeepSeek Harness`、基线=`main@cddff58469b56e181019a8ddfeade80684bc7eb9`、Task write scope /五个精确目标路径/验收条件一致。新的 DSH 调用使用 PowerShell 7 上已解析的 `dsh.ps1` shim；不得复用 cohort #8 targets。
5. **manifest 结构与证据**：pre-capture checklist 的 Markdown 表连续；cohort #1–#7 规范记录与 pins 为 FROZEN；cohort #7 sidecar 单独标记；cohort #8 只记录 dispatch failure、不是 review；cohort #9 五项均 PLANNED/pending。
6. **当前状态及历史不确定性**：唯一 Active product Task=`P02`，Active subtask=`P02PRE-R1F`；cohort #7 原 verdict=`CHANGES_REQUESTED (0/0/0/2)` 保留；cohort #8 无 verdict；cohort #9 为下一 READY。受控 status=`704 NUL / 46110 bytes / SHA-256 4055D234DF93C21893AEB4AD11B2B86A492F12B3766E70F9D162E123E414A7E`，排除 `.tmp.driveupload`。旧 checkpoint 活动区块逐字差异=`NOT_VERIFIED`；`760/48780→688/44882`=`UNKNOWN / NOT_VERIFIED`，不推断删除/归属。
7. **Gate 与 execution boundary**：`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；准确保留 `technical condition unmet; user explicitly accepted residual risk`。Build Gate=`BLOCKED`、Hard Build Barrier=`EFFECTIVE`、Build/Cargo=`NOT_RUN`、AC1–AC7=`BLOCKED / NOT_RUN`。Review 不解除 gate。
8. **PowerShell**：R8 是 Windows PowerShell 5.1 parse-only；PS 7.6.6 只有补充 `Parser::ParseFile` syntax observation，不表示运行期兼容，不切换 reviewed executor contract。

若发现缺陷，保持原始 cohort #7 verdict 与 Gate 事实，给出 P0/P1/P2/P3 counts、finding ID、severity、path/line、证据与最小修复；不要编辑文件或替 Codex adjudicate。没有 findings 时给 `APPROVED` 并列出实际读取文件。允许 verdict=`APPROVED`、`CHANGES_REQUESTED`、`NOT_VERIFIED`、`BLOCKED_BY_MISSING_EVIDENCE`。明确哪些仅为文本检查、没有运行命令/hash/API。

## Frozen source pins

| Path | Bytes | SHA-256 |
|---|---:|---|
| `doc/tasks/P02PRE-R1F.md` | 28157 | `339F1883AD7DA4C18FFF0264D0A3278D5CD3C10F7C8D216E20AF9FD7AEDFED59` |
| `verification/P02/p02pre-r1f-manifest-20261011.md` | 40808 | `DF041E2C2C4668766E5F937783081C42C7B12CEE351FAACE4FF50125F36180CF` |
| `doc/REBASELINE_PLAN.md` | 277573 | `17E3F5C9BB5540E55163D057B548FF66AAEC9518B90427972A1ED9050BC2A34C` |
| `doc/STATUS.md` | 286252 | `BDA45A190D613BD4222C4600EE65272AC62812851CB4ACC9CFDF2D6890E11E16` |
| `doc/00_INDEX.md` | 56967 | `6CC76212F765041E979A1ABED925B7D053D1F83BCCF8B9D1E29D349E71497BA3` |
| `doc/tasks/README.md` | 36515 | `B437D1BA80D3EE546B96461A29ACE80F22F6633BFE3CD964ABACD54C7CEF3F21` |
| `doc/tasks/P02.md` | 222293 | `CF156734A1D07A936A32E41AE85D584BEB2ADFE3EDD3D25BFB70D3886A01CCAB` |
| `verification/P02/codex-checkpoint-p02pre-r1f-20261011.md` | 20544 | `69D9F5ECCDBBC1A86B2D9B09D6F234485F496C73DE55AC7981368A3D18B58C27` |
| `verification/P02/p02pre-r1f-capture.ps1` | 67582 | `5A3FE118A8758CCDF0BEDBE170D31B34DA6C338101096EAA825DE80DF70E8316` |
| `verification/P02/p02pre-r1f-parser-windows-powershell-5.1-r8-20261011.json` | 2595 | `2C3BA665FF16D5CD8F9749CEE4BB2BCDCB4102661ACAFDF67A889FEA8F66A696` |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview6-20261011.prompt.md` | 5720 | `58FF0AE2845AA3818D82015784598A9AD4580ED838EA2DD069CFBABABD283F03` |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview6-20261011.stdout.md` | 176354 | `91DBAA27F6C8DCCF357D121047774995B1A53135AEB59EB25E4FC6C9C2122FF5` |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview6-20261011.stderr.log` | 0 | `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855` |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview6-20261011.exit` | 3 | `13BF7B3039C63BF5A50491FA3CFD8EB4E699D1BA1436315AEF9CBE5711530354` |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview6.exit` | 3 | `13BF7B3039C63BF5A50491FA3CFD8EB4E699D1BA1436315AEF9CBE5711530354` |
| `verification/P02/p02pre-r1f-r5-followup7-fixreview6-adjudication-20261011.md` | 3879 | `2BA8EADD18E1279F4AEEF7B837AFDBFC3D8177B01DA46F9F9591CDB53B91F451` |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview7-20261011.prompt.md` | 6332 | `0C89498657B242D4A3F63EB21574D5BA582EB1BD382A751564635986412E1306` |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview7-20261011.stdout.md` | 0 | `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855` |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview7-20261011.stderr.log` | 0 | `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855` |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview7-20261011.exit` | 49 | `5F9C0A8B9509DDAF4910151DB3883AE591A33445149CAAB59E1CB7B93F0FD94F` |
| `verification/P02/p02pre-r1f-r5-followup7-fixreview7-adjudication-20261011.md` | 2785 | `C7634716FFC1B9501942CD4ACA6A1FA15FF0128CAF0CDF54ABC81C0791EEF97F` |

如果任一输入 pin mismatch，停止引用该路径并报告 `NOT_VERIFIED`；不要声称复核通过。