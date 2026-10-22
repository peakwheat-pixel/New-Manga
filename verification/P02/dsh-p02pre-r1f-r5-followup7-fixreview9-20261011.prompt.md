# DeepSeek Harness 独立只读 Review 委托 — P02PRE-R1F / R1F-R7 cohort #10（fixreview9）

## 角色与绑定

- Repo=`G:/CODEX/New Manga`；branch=`main`；base HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`；Task=`P02PRE-R1F`。
- 当前为 R1F-R7 governance cohort #10（label=`fixreview9`），不是 parser R8、capture round 或旧 R5 follow-up #9。
- Owner/Author/Integrator/Adjudicator=`Codex /root`；本轮非作者 Reviewer=`DeepSeek Harness`（必须使用全新 session）。
- 只读审查：不得编辑、创建或删除仓库文件；不得运行命令、脚本、Git、hash/API、host getter、profile、registry、ACL、capture、Build/Cargo 或 AC1–AC7。只读取冻结输入并在响应中交付报告。
- 不输出内部推理过程；只报告可复核的 verdict、findings、证据和限制。

## 审查任务

独立复核 cohort #9/fixreview8 的 F8-1–F8-4 处置是否真实、一致、完整；判断文档/scope review 是否可结束。保持原 cohort #9 verdict=`CHANGES_REQUESTED (0/1/1/1)`，不得把修复后的 #10 verdict 回写成 #9 PASS。

1. **F8-1：#9 artifact 状态与 pins。** 核对 manifest、Task、Plan、STATUS、Index、README、P02 和 checkpoint 是否准确区分 #9 的 `FROZEN` 五件套与 #10 `PLANNED` 五件套；核实 #9 prompt/stdout/stderr/CLI exit/adjudication 路径和实测 pins 是否一致。#9 的 `stderr` 是历史原始流式输出，保持原样，不得改写。
2. **F8-2：缓冲输出流程。** 核对 Task、manifest、Plan、STATUS、checkpoint 对本轮 launcher 的规定是否一致：PowerShell 7 `dsh.ps1` 启动；Python 使用 `subprocess.PIPE` 将完整 stdout/stderr 留在内存；DSH 进程退出后才以 `CreateNew` 写入规范 stdout/stderr/CLI exit，因此 reviewer 执行期间不能读取自身正在增长的输出。审查可判断文档规定和精确输出路径；不要声称从文本证据证明了未来运行时行为。
3. **F8-3：当前快照一致性。** 核对所有当前导航是否统一为受控 Git status=`709 NUL / 46498 bytes / SHA-256 41F6253C130142985095989B4B255E1672910474F080A0EA5EDF391F4DEBECC3`，该快照包含 #9 五件套且早于 #10 artifacts；更早 `760/48780→688/44882` 保持 `UNKNOWN / NOT_VERIFIED`，不得推断文件删除或归属；旧 checkpoint active-block 差异继续 `NOT_VERIFIED`。
4. **F8-4：Task capture 命令引用。** 核对当前 Task 是否明确引用 manifest 冻结的单次 capture command，不留下可能指向未命名“上方命令”的歧义。
5. **历史 #8 dispatch failure。** `NOT_DISPATCHED / NOT_REVIEWED` 是启动前失败而非 Review verdict；无 DSH session/CLI exit；`.exit` marker 不是 CLI exit。核对 Task AC 仍未把它勾为 Review 完成，且输出目标没有被复用。
6. **当前责任、DAG 与边界。** 唯一 Active 产品 Task=`P02`，Active 子 Task=`P02PRE-R1F`；本轮 Reviewer=`DeepSeek Harness`，Owner/Integrator=`Codex /root`；#10 是唯一 READY Review。P02 Gate 必须原样保持：`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；原文=`technical condition unmet; user explicitly accepted residual risk`。Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；Build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`。本 Review 不运行 getter、不释放 capture 或 Build。
7. **PowerShell 版本说明。** 编排 shell 是 PowerShell 7.6.6；冻结 capture/parser target 仍是 Windows PowerShell 5.1.26100.9549，R8 仅证明该候选在 5.1 下 parse-only 成功。PowerShell 7 对同一脚本 `Parser::ParseFile` errors=0 仅是语法观察；项目没有证据表明 PowerShell 7 不兼容，也没有据此切换已审查的执行契约。核对文档未作更强声明。

如果发现问题，给出 `CHANGES_REQUESTED`，列 P0/P1/P2/P3 counts、finding ID、severity、路径/行、证据与最小修复；不得编辑或替 Codex adjudicate。无 findings 且输入足以确认时给 `APPROVED (0/0/0/0)`。证据不足给 `NOT_VERIFIED` 或 `BLOCKED_BY_MISSING_EVIDENCE`，明确哪些只做文本检查、哪些未能独立验证。只输出必要结论，不复述 DSH stderr 中与审查无关的内部推理或进度文本。

## Frozen source pins

| Path | Bytes | SHA-256 |
|---|---:|---|
| `doc/tasks/P02PRE-R1F.md` | 29105 | `4A944D5D6625B5E5A3B457C2923CEC5195013EA278D071E6F6C864780D2AF833` |
| `verification/P02/p02pre-r1f-manifest-20261011.md` | 42318 | `437A21D75876D58459D566AC57826FFF7889E40B11909CC5DB97A5DBD12FA0A3` |
| `doc/REBASELINE_PLAN.md` | 277546 | `B0611EAFAEC0E4C59EEFF47E6712D00B081DD23DB46A270B4C72C6059FB1D41E` |
| `doc/STATUS.md` | 285977 | `7949481E845478481DF7542F55D6C2065C8E15862B749AF4BA1BAC325891F908` |
| `doc/00_INDEX.md` | 56786 | `1B0CDFDE5A5F228CB7355A9F46E85FD2A19BB5778AD9872FAFC8BBBCC5B883E5` |
| `doc/tasks/README.md` | 36301 | `6E655B4E0062F6E12AEF819676F3AE8C5097DE6951EB40D4C605051F11C62A52` |
| `doc/tasks/P02.md` | 222192 | `3AF7DE7FE6976E0D3481FD0E2040A79607DD79BBC1856969B7F6A6E3174EEDC0` |
| `verification/P02/codex-checkpoint-p02pre-r1f-20261011.md` | 18830 | `FCD1C3AF2696D81D7F721603AF3B30CFEDAE8158ABB907F4C5058B6AD6E4FB39` |
| `verification/P02/p02pre-r1f-capture.ps1` | 67582 | `5A3FE118A8758CCDF0BEDBE170D31B34DA6C338101096EAA825DE80DF70E8316` |
| `verification/P02/p02pre-r1f-parser-windows-powershell-5.1-r8-20261011.json` | 2595 | `2C3BA665FF16D5CD8F9749CEE4BB2BCDCB4102661ACAFDF67A889FEA8F66A696` |
| `verification/P02/p02pre-r1f-r5-followup7-fixreview6-adjudication-20261011.md` | 3879 | `2BA8EADD18E1279F4AEEF7B837AFDBFC3D8177B01DA46F9F9591CDB53B91F451` |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview7-20261011.exit` | 49 | `5F9C0A8B9509DDAF4910151DB3883AE591A33445149CAAB59E1CB7B93F0FD94F` |
| `verification/P02/p02pre-r1f-r5-followup7-fixreview7-adjudication-20261011.md` | 2785 | `C7634716FFC1B9501942CD4ACA6A1FA15FF0128CAF0CDF54ABC81C0791EEF97F` |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview8-20261011.prompt.md` | 7211 | `908B80877691497EEE19C6AE9109F863576329CAC8D016C5259D44D2A12D3F7E` |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview8-20261011.stdout.md` | 11853 | `F75C9B90C6F278B61F9F3B2E23DD872ACAFF9A2710227D2F5F572FE4E9110174` |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview8-20261011.stderr.log` | 28870 | `1654CD0806C5B93119F664965D4D236196E570F5EA3A9F26C1BE4960850115F5` |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview8-20261011.exit` | 3 | `13BF7B3039C63BF5A50491FA3CFD8EB4E699D1BA1436315AEF9CBE5711530354` |
| `verification/P02/p02pre-r1f-r5-followup7-fixreview8-adjudication-20261011.md` | 4794 | `44DDE1EB9191062FCFFAA4FE0A714A01963763D514EF2BE812A034573C4AF864` |

若任一输入 pin mismatch，停止引用该路径并报告 `NOT_VERIFIED`；不要声称复核通过。
