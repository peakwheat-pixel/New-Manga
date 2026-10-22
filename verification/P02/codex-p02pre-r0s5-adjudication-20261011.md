# P02PRE-R0S5 Codex 最终 adjudication

## 裁决对象与来源

- Task=`doc/tasks/P02PRE-R0S5.md`；Owner/Author/Integrator/Adjudicator=`Codex /root`；非作者 Reviewer=`DeepSeek Harness`。
- branch=`main`；base/reviewed HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`；本 Task 文档为未提交工作区文件。
- 授权仅为 2026-10-11 用户批准的受控只读取证阶段；它不是新风险豁免、Gate PASS 或 Build Barrier 放行。
- Round 1 Review=`verification/P02/dsh-p02pre-r0s5-review-20261011.md`；Round 2=`verification/P02/dsh-p02pre-r0s5-review-r2-20261011.md`；Round 3=`verification/P02/dsh-p02pre-r0s5-review-r3-20261011.md`。
- Round 3 报告由 DeepSeek Harness 经 `dsh headless` 生成，dispatch exit=`0`；session=`session-f78b23bc-9619-47b8-83b8-84507d9b74ef`。`mount_session.py --latest` 输出确认该 session 已挂载到 `New Manga` workspace；该次 mount 命令未单独留存数值 exit marker。
- Codex 记录 Round 3 报告=`10056 bytes / SHA-256 02AB67DD56CD3D5E8F33364909B6D769A5BA8EB72B67D51FEBC3DF4E36F5FD98`；dispatch stdout=`4967 bytes / SHA-256 39B5DD9275522A94AFE7647A7689CB634DFDCD6476D36A14BE9C6F442244FB60`。Reviewer 未自行验证这些 hashes；Live Git 与 artifact 核验另见集成验证。

## Review findings adjudication

| Review / finding | 处置 | Codex 依据 |
|---|---|---|
| R1 `DSH-R0S5-P2-01` | CLOSED | 限定历史 hash collection 为 R0 evidence 的 12 份列名文档 + `.git/index` 共 13 项；说明不是完整 R6 protected-invariants 清单，也不证明当前 runner/method 安全。 |
| R1 `DSH-R0S5-P2-02` | CLOSED | 固定 r6 用户/SID/非提权/无 thread impersonation 比对基准；ACL 对象逐项冻结为 12 input roots、13 scratch output leaves、3 scratch canary leaves。R2 发现的 canary 根误指主仓另立项并修正。 |
| R1 `DSH-R0S5-P3-01` | CLOSED | Review 期间 Task/STATUS/PLAN/Index 状态已统一为 `in_review`；最终状态现为 `blocked`，与 runner blocker 一致。 |
| R1 `DSH-R0S5-P3-02` | CLOSED | manifest 明确这是本次新建 `P02PRE-R0S5` 的用户授权，不扩展既有 risk waiver。 |
| R1 `DSH-R0S5-P3-03` | CLOSED | Task/manifest/Plan 均明确当前没有任何 host getter/query 获准，执行必须晚于独立 Review 与 Codex adjudication。 |
| R1 `DSH-R0S5-P3-04` | CLOSED | AC 已按实际文档交付和最终状态逐项勾选；未把未执行检查记为成功或失败。 |
| R2 `DSH-R0S5R2-P2-01` | CLOSED | 三个 canary leaf 已绑定 `G:\CODEX\P02-scratch-build-source` 与 r6 精确相对路径；主仓仍为禁止 ACL 查询范围，且没有获准的写 canary。R3 独立复核确认路径与 r6 一致。 |
| R2 `DSH-R0S5R2-P3-01` | CLOSED | R0 hash 方法引用改为真实的 `实际执行调用与结果` 段及 L18–L29。 |
| R2 `DSH-R0S5R2-P3-02` | CLOSED | Task Reviewer write ownership 只列 R1/R2/R3 三个精确报告路径；prompt/log 属 Codex。 |
| R2 `DSH-R0S5R2-P3-03` | CLOSED | Task 先要求独立 Review 与 Codex adjudication，再允许任何逐项获准的查询，并明确当前没有候选获准。 |
| R2 `DSH-R0S5R2-P3-04` | CLOSED | AC L41 与 scratch 根修正后的 28 个精确 r6 ACL 对象相符。 |
| R3 `DSH-R0S5R3-P3-01` | CLOSED_BY_WORDING_FIX | Reviewer 指出 Task L55 将 12 个只读输入根置于 “scratch 仅限” 句式。Codex 已改为“对象集合仅限 12 个只读输入根、13 个 scratch 输出 leaf 和三个 scratch-root canary leaf”。该修改只澄清对象分类，不改变路径、查询或执行范围；R3 已判该 finding 非阻断。 |

Round 3 decision=`APPROVED`，findings P0/P1/P2/P3=`0/0/0/1`；唯一 P3 已做上述措辞修正。Reviewer 未核验 bytes/hash、Live Git、宿主状态，亦未独立证明“零查询”；这些限制维持 `NOT_VERIFIED`，不由 Codex 文档裁决伪装成独立证据。

## 五类条件分类

| P02PRE 条件 | 最终分类 | 证据边界 |
|---|---|---|
| 历史 R0 固定时点的身份/SID、精确受限路径与 ACL metadata、WER 候选 metadata、13 项 hash collection（12 文档 + `.git/index`） | `PASS_WITH_EVIDENCE` | 仅适用于 R0 evidence 记录的对象和时点；13 项不是完整 protected-file inventory，且不证明当前 runner 或 getter 安全。 |
| 本轮实际失败项 | `FAILED=∅` | 本 Task 没有运行 P02PRE host check；未执行不等于失败。 |
| 当前 user/SID/token/elevation/impersonation；当前 profile/target path（未登记的 profile path 不猜测）；r6 的 28 个 ACL 对象；TEMP/cache/scratch/path resolution；当前保护文件 hash；WER/T0；`private_registry_absence` | `UNPROVABLE` | 没有当前主机 capture。具体查询方法受 runner/method gate 阻止。 |
| 有效 LPAC 读写行为、permission canary 结果、子进程/broker/write closure、stop/cleanup | `REQUIRES_ACTIVE_TEST` | 需要之后单独冻结并授权的动态测试；本 R0 只读任务不执行。 |
| 当前 `exec_command`/PowerShell launcher 与 wrapper；身份、profile、registry、ACL、environment、path、hash、WER/T0 等所有当前 host getter/query | `NOT_SAFE_FOR_R0` | executable/version、完整 argv、startup/profile/cache/history/wrapper/temp/log 与子进程边界未证明无副作用；没有任何候选由 Review + Codex adjudication 清除。 |

条件状态与方法状态分开：当前目标值为 `UNPROVABLE`；由于执行方法不安全，不能把它们升级或降格为 PASS/FAILED。

## 最终决定、Gate 与接续

文档 delivery、三轮非作者 Review、finding adjudication 和静态分类已完成；P02PRE-R0S5 整体仍=`blocked / NOT_SAFE_FOR_R0`，不是 `done`。没有安全 READY 的下一项 host capture Task。恢复前置是取得精确 runner/方法无副作用证据，先经非作者 Reviewer Review，再由 Codex adjudicate；在此前不得切换 shell、运行 getter 或 host query。

风险裁决保持原值：`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；`technical condition unmet; user explicitly accepted residual risk`。因此 P02PRE/Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；profile=`NOT_CREATED`；ACL/registry=`NOT_MODIFIED`；build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`。本 Task 未查询、安装、启用或启动 Windows Sandbox。

Round 3 Review 与本 adjudication 只裁决静态文件，不是当前 host Gate，不构成任何风险 waiver、API 执行许可或 Build Barrier 解除。
