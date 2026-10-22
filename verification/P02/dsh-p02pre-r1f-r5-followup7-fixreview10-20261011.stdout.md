# 独立只读 Review 报告 — P02PRE-R1F / R1F-R7 cohort #11（fixreview10）

- 绑定：Repo=`G:/CODEX/New Manga`，branch=`main`，Task=`P02PRE-R1F`，base HEAD 记载=`cddff58469b56e181019a8ddfeade80684bc7eb9`；Owner/Author/Integrator/Adjudicator=`Codex /root`，本轮 Reviewer=`DeepSeek Harness`（非作者，全新 session，无前序 cohort 上下文）。
- 本轮只做文本/路径核对与只读文件读取；**未**运行 Git/hash/getter/profile/registry/ACL/capture/Build/Cargo/AC，**未**编辑、创建或删除仓库文件。Qoder 未参与。

## VERDICT: `APPROVED (0/0/0/0)`

无 P0/P1/P2/P3 finding。下述“限制与未独立验证项”是可复核的证据边界，不是被计数的 finding。

---

## 一、F9-1/P3 精确路径修复：已完整关闭

| 核对点 | 证据 | 结论 |
|---|---|---|
| manifest 中 cohort #10 四条 DSH 路径 | `p02pre-r1f-manifest-20261011.md:119-122` 为 `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview9-20261011.{prompt.md,stdout.md,stderr.log,exit}` | 四条均带 `dsh-` |
| cohort #10 adjudication 文件名 | 同文件 `:123` + Task `:55` + checkpoint `:33` 均为 `p02pre-r1f-r5-followup7-fixreview9-adjudication-20261011.md`（本就不带 `dsh-`） | 一致 |
| 旧漏 `dsh-` 路径是否仍被列出 | 全仓库检索 `p02pre-r1f-r5-followup7-fixreview9-20261011` 的全部命中前面均为 `dsh-`；检索 `dsh-…-fixreview9-adjudication` 零命中 | 未见残留旧路径 |
| Task AC / checkpoint / Plan / 磁盘 | Task `:55`；checkpoint `:7,:9,:33`；Plan `:7`；`glob verification/P02/*fixreview9*` 返回五件套（prompt/stdout/stderr/exit/adjudication） | 文本与磁盘一致 |
| F9-1 修复记录 | `p02pre-r1f-r5-followup7-fixreview9-adjudication-20261011.md:17-19` 记录“原 rows 119–122 漏 `dsh-`、Codex 独立确认属实、只改 manifest 四行与 cohort mapping、未移动/覆盖/删除证据”，并给出修复前 `42318/437A21D7…` 与修复后 `43780/32A8DA05…` 两个历史 manifest pin | 修复记录完整、最小 |

补充：manifest `:63` 的 cohort mapping 与 `:124-128` 的 cohort #11 五行均带 `dsh-` 前缀，与 Task `:56`、checkpoint `:15` 登记的五个精确路径逐字一致。

## 二、cohort #10 原 verdict 与证据：#10 未被回写成 PASS

- 原 verdict 保留：Task `:40,:55`、manifest `:134`、checkpoint `:7`、STATUS `:5,:9`、Index `:5`、README `:5`、P02.md `:24` 一律为 `CHANGES_REQUESTED (0/0/0/1)` + 唯一 finding `F9-1/P3`；adjudication `:9` 明写“原 Review verdict 保留，不能改写为 PASS”。
- #10 五件套 pins 在 manifest `:119-123`、checkpoint `:9`、adjudication `:11`、Task `:55` 四处一致：prompt `6989/1AE76EBA…`、stdout `1269/22A8759A…`、stderr `61730/3F36DDF0…`、exit `3/13BF7B30…`、adjudication `3994/083632D5…`；与本次委托 Frozen source pins 表逐项相同。
- `#10 stderr` 我只核对了 manifest/checkpoint/Task 记录的 canonical path、size 与 SHA-256；按指令未打开、未引用、未复述其内容（本轮检索工具曾顺带命中该文件一行文本，我未将其作为证据引用）。

## 三、当前状态与 DAG：与冻结记载一致

- 唯一 Active 产品 Task=`P02`、Active 子 Task=`P02PRE-R1F`、唯一 READY=`#11/fixreview10`：Task `:40,:56`、Plan `:7,:30,:42`、STATUS `:5,:13`、Index `:5`、README `:3,:5`、P02.md `:24`、checkpoint `:1,:3,:15` 一致；DAG 仍唯一指向 `doc/REBASELINE_PLAN.md`，恢复点仍为 `verification/P02/codex-checkpoint-p02pre-r1f-20261011.md`。
- 冻结 status snapshot=`714 NUL / 46886 bytes / SHA-256 6E58E901…FDDA` 在 Plan `:5,:11`、STATUS `:5,:7`、Index `:5,:7`、README `:5,:7`、P02.md `:24`、checkpoint `:23` 六处一致，并注明“含 #10 五件套、早于 #11 artifacts、final pre-run 需重采”。**我不声称 prompt 创建后的 live status 仍是该值**；本 session 无法复算。
- 更早 `760/48780→688/44882` 在 Plan `:5`、STATUS `:5,:7`、Index `:5`、README `:5`、checkpoint `:23` 继续保持 `UNKNOWN / NOT_VERIFIED`；旧 checkpoint active-block 差异在 checkpoint `:23` 为 `NOT_VERIFIED`。checkpoint `:49` 起的历史段（`:55,:61,:68`）仍保留 #9 时代的旧 pin 与 `709/46498` 快照，处于文件自身声明的历史区块内，未与当前段混用；该历史段尾部本轮未展开阅读（见“限制”第 3 条）。
- manifest 仍将 cohort #11 五条登记为 `PLANNED / pending`（`:124-128`），并声明 `:130` “pending row 是 blocker，不是隐式 pass”；Task AC `:56` 仍未勾选。未发现把 #11 误报为已派发或已完成。

## 四、输出流程：文档规定一致，未实测 #11 launcher

- Task `:68`（write scope）、manifest `:59`、Plan `:42`、checkpoint `:15` 一致规定：PowerShell 7.6.6 的 `dsh.ps1` shim 启动 DSH；Python launcher 用 `subprocess.PIPE` 在内存缓冲完整 stdout/stderr；DSH 进程退出后才以 `CreateNew` 写规范 stdout/stderr/真实 CLI exit；reviewer 运行期间不得读取自身正在增长的输出。
- checkpoint `:43` 另要求派发前“复核 cohort #11 五个输出 targets 全部不存在”。**观察**：当前磁盘上 `dsh-…-fixreview10-20261011.prompt.md` 已存在（即本次委托输入本身），stdout/stderr/exit 与 adjudication 不存在；这与“prompt 先 CreateNew、其余输出在 CLI 退出后落盘”的既定时序相符，但也意味着“五个 targets 全部不存在”在文本冻结时刻已不再成立，只能按逐 target 判断（见“限制”第 5 条）。
- #10 的产物形态与该流程自洽：stdout `1269` bytes、stderr `61730` bytes、`.exit` `3` bytes（`30 0D 0A`，`13BF7B30…`）——即三路输出在进程退出时才关闭冻结，不是流式追加。launcher 自身未被文本证据证明；我**未独立实测 #11 launcher**，也不声称已实测。

## 五、PowerShell 执行契约：文档未作更强声明

- 编排 shell=PowerShell `7.6.6`；capture/parser target 仍=`Windows PowerShell 5.1.26100.9549`（`PSEdition=Desktop`，R8 `PARSE_OK`、errors=0、`captureScriptInvoked=false`）：Task `:33`、Plan `:19`、STATUS `:13`、checkpoint `:17`、manifest `:27`、P02.md `:24` 一致；R8 artifact pin `2595/2C3BA665…` 与 source pin `67582/5A3FE118…` 在各处一致。
- PowerShell 7 的 `Parser::ParseFile` errors=0 均被表述为“仅语法观察、不证明运行期兼容”（Plan `:19`、checkpoint `:17,:55`、Task `:33`）；仓库未声称 7 不兼容，也未见任何把执行契约擅自从已 Review 的 5.1 切换到 7 的表述。

## 六、Gate 边界：原值原样保持

Plan `:7`、Task `:40`、STATUS `:11`、checkpoint `:39`、P02.md `:26`、Index `:5,:7` 一致：`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；原文=`technical condition unmet; user explicitly accepted residual risk`；Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；Build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`；Capture=`BLOCKED / NOT_RUN`。本 Review 未运行 getter，未释放 capture 或 Build，未替 Codex 作任何 adjudication。

---

## 限制与未独立验证项（不计入 finding）

1. **输入 pins 的 bytes/SHA-256 未在本 session 独立复算。** 本 session 的 `pwsh` 工具在沙箱初始化阶段即失败（`SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga)`），两次尝试（默认 workdir、`C:\Windows\Temp`）均未执行任何命令，因此无命令可用、无 hash 工具可用。我只完成了：全部 15 个冻结路径的存在性核对（读取成功）、以及 pins 在 prompt 表 / manifest / checkpoint / Task / fixreview9 adjudication 之间的**文本互证一致性**核对（逐字符相同，无内部冲突）。**字节级结论仍以 Codex 的独立复算为准**；manifest `:58,:65` 与 checkpoint `:45` 描述的 final pre-run inventory membership + size/SHA-256 复算我未执行、未观察。
2. **live Git 状态未复算**：HEAD/tree/index/worktrees、`git status` records/bytes/digest 均按文档记载比对，未独立验证。
3. **checkpoint 历史段未全文展开**：该文件共 177 行，我按当前段（`:1-50`）与针对性检索核对；`:51-177` 历史内容仅抽查（`:61,:68`），未逐行阅读，故不对历史段完整性作结论；旧 active-block 差异继续 `NOT_VERIFIED`。
4. **未复核 stderr 内容**：按指令未打开 #10 `stderr`（61730 bytes）内容；仅核对其被记录的 canonical path/size/SHA-256。
5. **目标不存在性未全量确认**：#11 的四路 DSH 输出与 adjudication 当前不存在；但 `prompt.md` 已存在（即本次输入），故“五个 targets 全部不存在”只能按逐 target 表述。
6. **未实测运行期行为**：文本审查不能证明未来 launcher/缓冲/`CreateNew` 的运行期行为；Codex launcher 本身不在本轮审查范围内。

## 建议（供 Codex 判断，不构成裁定）

1. 由 Codex 对本轮 15 项 frozen inputs 独立复算 bytes/SHA-256 并留存记录，随后读取本报告并 adjudicate。
2. 在 cohort #11 adjudication 中回写本报告 verdict、`#10` 五件套与 `#11` prompt 的实测 pins，并按 manifest `:130` 将五条 `PLANNED` 行推进到已关闭/已 pin 状态。
3. 若判 `APPROVED` 且接受本报告的证据边界，再按 checkpoint `:45` 执行 final pre-run；本 Review、R8 与 Owner waiver 均不释放 Build Gate，capture 在 pre-run 全部匹配前保持 `BLOCKED / NOT_RUN`。
