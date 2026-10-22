# DeepSeek Harness 独立只读 Review 委托 — P02PRE-R1F / R1F-R7 cohort #8（fixreview7）

## 角色与绑定

- Repo=`G:/CODEX/New Manga`；branch=`main`；base HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`；Task=`P02PRE-R1F`。
- 当前为 R1F-R7 governance cohort #8（label=`fixreview7`），不是 parser R7、capture round 或旧 R5 follow-up #7。
- Owner/Author/Integrator/Adjudicator=`Codex /root`；非作者 Reviewer=`DeepSeek Harness`。
- 只读审查：不要编辑、创建或删除仓库文件；不要运行命令、脚本、Git、hash/API、host getter、profile、registry、ACL、capture、Build/Cargo 或 AC1–AC7。只读取被冻结输入并在响应中返回报告。

## 审查范围

独立复核 cohort #7/fixreview6 的两项 P3 finding 与 Codex integration finding 是否已正确处置，并确认 Task、manifest、唯一 DAG、STATUS、Index、Task README、P02 导航和 rolling checkpoint 状态一致。特别检查：

1. **F7-1**：Task 的“当前 host capture”行是否改为要求最新 R1F-R7 cohort Review=`APPROVED` 且 Codex adjudication 通过，再由 final pre-run adjudication 明确释放；不得仍要求 cohort #6 approval。
2. **F7-2**：STATUS 对 cohort #8/fixreview7 路径的引用是否指向 manifest/checkpoint；是否诚实说明 bytes/SHA-256 仍 pending，不声称 DAG 已列出预留 paths/pins。
3. **F7-3 / artifact integration**：manifest 中规范 cohort #7 exit path=`dsh-p02pre-r1f-r5-followup7-fixreview6-20261011.exit` 是否为 3 bytes、raw `30 0D 0A`、与 wrapper exit 0 一致；是否透明记录另一个少日期的 noncanonical sidecar=`dsh-p02pre-r1f-r5-followup7-fixreview6.exit`、将其保留并单独列出，而未把它冒充规范输出或覆盖/删除。Codex 声称已复核两个 exit 文件同 hash；本 Review 只做文本与已冻结 pin 的交叉检查，不运行 hash 命令。
4. **cohort #7 状态与 pins**：原 Review verdict=`CHANGES_REQUESTED (0/0/0/2)` 必须保留；Codex adjudication 接受 F7-1/F7-2 与 integration finding；规范五件套和 noncanonical sidecar pins 应与 manifest、checkpoint 一致。
5. **cohort #8 委托**：Task/manifest/checkpoint 是否登记同一组五个精确路径、Owner/Reviewer/基线 HEAD、非作者 Review 约束、文件写入范围和验收标准；manifest 表格是否连续，#1–#7 为 FROZEN、#8 为 PLANNED/pending。
6. **全局状态**：唯一 Active 子 Task=`P02PRE-R1F`；cohort #8/fixreview7 是唯一下一 READY。Build Gate 与 Hard Build Barrier 不得因文档 Review 或用户 waiver 自动放行。
7. **历史未验证项**：旧 checkpoint 活动区块逐字差异继续=`NOT_VERIFIED`；`760/48780→688/44882` status 变化继续=`UNKNOWN / NOT_VERIFIED`；不得推断删除、归属或无遗漏。
8. **Gate 原值**：`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；必须保留原句 `technical condition unmet; user explicitly accepted residual risk`；Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；Build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`。
9. **PowerShell 语义**：R8 仍为 Windows PowerShell 5.1 parse-only；PowerShell 7.6.6 仅有补充 `Parser::ParseFile` 语法观察，不证明运行期兼容，也不切换 reviewed executor contract。

本 Review 与 Codex adjudication 不释放 capture、Build Gate 或 Hard Build Barrier。

## 返回格式

中文报告：`APPROVED`、`CHANGES_REQUESTED`、`NOT_VERIFIED` 或 `BLOCKED_BY_MISSING_EVIDENCE`；列 P0/P1/P2/P3 finding 数，逐项给 ID、级别、路径/行号、证据、最小修复。说明实际读取范围以及未执行/未验证项目；明确区分观察和推断。不要声称运行命令、hash、API 或替 Codex adjudicate。

## 冻结输入 pins

| Path | Bytes | SHA-256 |
|---|---:|---|
| `doc/tasks/P02PRE-R1F.md` | 27280 | `A82B3FC4FF74B0540C3B039DE3808C8B87B55933FAAD9E78CDE11B34CF739D9C` |
| `verification/P02/p02pre-r1f-manifest-20261011.md` | 39358 | `5B47B18E804123D17427EA44C0BF767D477771A97DA12E50074F638B35483CDE` |
| `doc/REBASELINE_PLAN.md` | 277203 | `1C54F3385B0BFD6BB6E87E5E09F0779864E647961EAB2F5CC52D2A7BB8FFDAE0` |
| `doc/STATUS.md` | 285951 | `06F096492C51F72BF60D6948C87F83F5749A5D8B684EB32B981CD6804AB5719C` |
| `doc/00_INDEX.md` | 56815 | `16D2930844131BAD00DE6131373BF4ED85000BD14C6C789798E86EB941037B32` |
| `doc/tasks/README.md` | 36336 | `3E7852EE337286EB825B07E714BCBFB5074E73876DED824E37B48E467D09490F` |
| `doc/tasks/P02.md` | 222130 | `508FCDA99F39A303A3E7E11BCDB3CD2591F550913DF3C74AFD02E798014AB96A` |
| `verification/P02/codex-checkpoint-p02pre-r1f-20261011.md` | 19517 | `E24104BF29846002252FBF2FF17256A16EBAE71C17A5839C8F70ABDCD79A6AE7` |
| `verification/P02/p02pre-r1f-capture.ps1` | 67582 | `5A3FE118A8758CCDF0BEDBE170D31B34DA6C338101096EAA825DE80DF70E8316` |
| `verification/P02/p02pre-r1f-parser-windows-powershell-5.1-r8-20261011.json` | 2595 | `2C3BA665FF16D5CD8F9749CEE4BB2BCDCB4102661ACAFDF67A889FEA8F66A696` |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview6-20261011.prompt.md` | 5720 | `58FF0AE2845AA3818D82015784598A9AD4580ED838EA2DD069CFBABABD283F03` |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview6-20261011.stdout.md` | 176354 | `91DBAA27F6C8DCCF357D121047774995B1A53135AEB59EB25E4FC6C9C2122FF5` |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview6-20261011.stderr.log` | 0 | `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855` |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview6-20261011.exit` | 3 | `13BF7B3039C63BF5A50491FA3CFD8EB4E699D1BA1436315AEF9CBE5711530354` |
| `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview6.exit` | 3 | `13BF7B3039C63BF5A50491FA3CFD8EB4E699D1BA1436315AEF9CBE5711530354` |
| `verification/P02/p02pre-r1f-r5-followup7-fixreview6-adjudication-20261011.md` | 3879 | `2BA8EADD18E1279F4AEEF7B837AFDBFC3D8177B01DA46F9F9591CDB53B91F451` |
| `verification/P02/p02pre-r1f-r5-followup7-fixreview5-adjudication-20261011.md` | 4287 | `6B27CFD4179C9ADC5C6E05FFD77148BDEE992859678CAE4351CBAB9754778D64` |

若任一冻结输入 byte size/SHA-256 不匹配，停止引用该路径并记 `NOT_VERIFIED`，不要继续据此给出通过结论。