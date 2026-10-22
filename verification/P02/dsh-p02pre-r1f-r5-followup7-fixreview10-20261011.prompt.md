# DeepSeek Harness 独立只读 Review 委托 — P02PRE-R1F / R1F-R7 cohort #11（fixreview10）

## 角色与绑定

- Repo=`G:/CODEX/New Manga`；branch=`main`；base HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`；Task=`P02PRE-R1F`。
- 当前为 R1F-R7 governance cohort #11（label=`fixreview10`），不是 parser R8、capture round 或旧 R5 follow-up #10。
- Owner/Author/Integrator/Adjudicator=`Codex /root`；本轮非作者 Reviewer=`DeepSeek Harness`，必须使用全新 session。
- 只读审查：不得编辑、创建或删除仓库文件；不得运行命令、脚本、Git、hash/API、host getter、profile、registry、ACL、capture、Build/Cargo 或 AC1–AC7。只读取冻结输入并在响应中交付报告。
- 不输出内部推理过程；只报告可复核的 verdict、findings、证据和限制。

## 审查任务

独立确认 cohort #10/fixreview9 的唯一 finding F9-1/P3 是否已完整修复，检查 Task、manifest、Plan、STATUS、Index、README、P02 与 checkpoint 路径和 pins 一致。cohort #10 原始 verdict=`CHANGES_REQUESTED (0/0/0/1)` 必须保持历史原值；本轮不得把它回写成 PASS。

1. **F9-1 精确路径修复。** 核对 manifest 中 cohort #10 的 prompt/stdout/stderr/exit 四行均采用 `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview9-20261011.{prompt.md,stdout.md,stderr.log,exit}`；Task AC、checkpoint、adjudication、文件系统实际路径也一致。确认 manifest 不再列出漏 `dsh-` 的四个旧路径。adjudication 的独立文件名是 `p02pre-r1f-r5-followup7-fixreview9-adjudication-20261011.md`，此路径本来就不带 `dsh-`。
2. **cohort #10 原 verdict 与证据。** 核对 Task/manifest/checkpoint 保留 `CHANGES_REQUESTED (0/0/0/1)` 与 F9-1 finding、Codex 接受及修复记录；核对 #10 prompt/stdout/exit/adjudication 的 manifest pins。#10 stderr 原文件含原始 DSH 运行期内容：不要打开、引用或复述其内容，只核对 manifest 对其 canonical path、size 和 SHA-256 的记录；Codex 已独立复算本轮所列 source pins。
3. **当前状态和 DAG。** 唯一 Active 产品 Task=`P02`，Active 子 Task=`P02PRE-R1F`；#11/fixreview10 是唯一 READY。冻结时受控 status snapshot=`714 NUL / 46886 bytes / SHA-256 6E58E901E923AE9D2A65F1B4FB088C3C5996C9D417C26B66C98560822AE9FDDA`，包含 cohort #10 五件套，早于 #11 artifacts；不要声称 prompt 创建后的 live status 仍是这个值。更早 `760/48780→688/44882` 继续=`UNKNOWN / NOT_VERIFIED`，旧 checkpoint active-block diff 继续=`NOT_VERIFIED`。
4. **输出流程。** 核对 Task、manifest、Plan、STATUS、checkpoint 要求的 PowerShell 7 `dsh.ps1` 调用与 Python `subprocess.PIPE` 缓冲流程：DSH 退出后才以 `CreateNew` 写入规范 stdout/stderr/真实 CLI exit，reviewer 运行期间目标不存在。文本审查不能证明未来运行时行为，不得声称已实测 #11 launcher。
5. **PowerShell 执行契约。** 编排 shell=`PowerShell 7.6.6`；capture/parser target 仍是 Windows PowerShell `5.1.26100.9549`；R8 仅为 5.1 parse-only。PowerShell 7 `Parser::ParseFile` errors=0 只是语法观察；项目没有证据表明 7 不兼容，当前也没有擅自切换已 Review 的执行契约。
6. **Gate 边界。** 原样保持 `private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；原文=`technical condition unmet; user explicitly accepted residual risk`。Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；Build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`。本 Review 不运行 getter，不释放 capture 或 Build。

若发现问题，给出 `CHANGES_REQUESTED`，列 P0/P1/P2/P3 counts、finding ID、severity、路径/行、证据与最小修复；不得编辑或替 Codex adjudicate。没有 findings 且输入足以确认时给 `APPROVED (0/0/0/0)`。证据不足给 `NOT_VERIFIED` 或 `BLOCKED_BY_MISSING_EVIDENCE`，明确只做了哪些文本/路径核对、哪些未能独立验证。不要复述原始 stderr 内容或内部推理。

## Frozen source pins

| Path | Bytes | SHA-256 |
|---|---:|---|
| `doc/tasks/P02PRE-R1F.md` | 30248 | `6281131B3215A44973AC2AC2F4BD45AB8729A5C54010C508C253E8E839D0418F` |
| `verification/P02/p02pre-r1f-manifest-20261011.md` | 43904 | `844BD146BD6A1023C2141FF7511B6AABBE259B7513C4376F660A97A564EDE251` |
| `doc/REBASELINE_PLAN.md` | 277719 | `B65327C0BC011654F479415A0D90FB9E2E5D240B27BA1349D2198B4AB519B07A` |
| `doc/STATUS.md` | 286064 | `575FB7BE439B779CBECEF71E1B4C9449EA6BC8DA8EC78AE9EE71CB16C643BE3C` |
| `doc/00_INDEX.md` | 56887 | `D01D75076543DE4F835AB3C69AEE998E8DDF43F487CE50CD6E5DB79544DCB8FD` |
| `doc/tasks/README.md` | 36352 | `A7A4803F2081D86514FD2DA876511B0C4D3926428206A0765AAFED436B3F23F7` |
| `doc/tasks/P02.md` | 222233 | `7A35B3594BE7D0512F373EFAE2DC6233F45E72882F5937B15EF95CF540431DF9` |
| `verification/P02/codex-checkpoint-p02pre-r1f-20261011.md` | 24894 | `2BA5E73365469DC94F47DAFA5104778AEDDDC289677CB9F913A9CDE4F46FA6A2` |
| `verification/P02/p02pre-r1f-capture.ps1` | 67582 | `5A3FE118A8758CCDF0BEDBE170D31B34DA6C338101096EAA825DE80DF70E8316` |
| `verification/P02/p02pre-r1f-parser-windows-powershell-5.1-r8-20261011.json` | 2595 | `2C3BA665FF16D5CD8F9749CEE4BB2BCDCB4102661ACAFDF67A889FEA8F66A696` |
| `verification/P02/p02pre-r1f-r5-followup7-fixreview8-adjudication-20261011.md` | 4794 | `44DDE1EB9191062FCFFAA4FE0A714A01963763D514EF2BE812A034573C4AF864` |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview9-20261011.prompt.md` | 6989 | `1AE76EBA5796B32BA5F2328F53095BD3D67E9F437764F83C0B04858B13727EEC` |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview9-20261011.stdout.md` | 1269 | `22A8759A2CE3550B86B295E8FCA6715A1EBD1F181EEC26352B84D522E5822787` |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview9-20261011.exit` | 3 | `13BF7B3039C63BF5A50491FA3CFD8EB4E699D1BA1436315AEF9CBE5711530354` |
| `verification/P02/p02pre-r1f-r5-followup7-fixreview9-adjudication-20261011.md` | 3994 | `083632D5C56A87C32B7045B69287F667107A9A0C2701270603F28F6393C79C36` |

如果任一 input pin 不匹配，停止引用该路径并报告 `NOT_VERIFIED`；不要声称复核通过。
