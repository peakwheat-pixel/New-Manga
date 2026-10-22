# P02PRE-R1H integration protocol Review R2 — Codex adjudication

日期：2026-10-12（Asia/Shanghai）。Adjudicator/Integrator=`/root`；候选实现Owner=`/root/p02_r1h_codex_owner`；非作者协议Reviewer=`/root/p02_r1h_remediation_review`。

## 判定

- Reviewer verdict=`APPROVED_STATIC_PROTOCOL`，P0/P1/P2/P3=`0/0/0/0`。Root 独立重算13项输入与3个候选文件，合计16/16匹配、0 mismatch；Owner branch/HEAD/parent/tree与冻结值相同，受控工作区状态0 bytes，index SHA=`DCBE24A2827B8465807C5627523DC6570346278935DA4A71BEF3FF969A9341FE`。
- Root 接受 `INT-R5-001` 与 `INT-R5-002` 的 `FIXED_STATIC_PROTOCOL` 结论。经修订的status delta、独立CreateNew旧字节recovery、API backup、异常时fail-stop和单独恢复裁决协议足以进入本 Task 的执行前核验。
- 本 adjudication 只接受集成程序静态设计；不表示动态前置条件已满足，不是 AC4 PASS，不解除任何产品/Build Gate。
- 当前旧目标重核为 57,623 bytes / `EEFB41141EBE162503047C20CAF4F41D5E8E01EEF2FCEE0C90DA7185A8164CF1`；stage、recovery、API backup仍 absent 且未被ignore。此处仅为当前只读pin结果；执行前需再次核验。
- AC4仍=`NOT_VERIFIED`；Round4真实失败证据保留。Round5候选尚未集成、parser/selfcheck/preflight尚未重跑，capture尚未执行。

## 精确受限执行范围

仅限 Task `doc/tasks/P02PRE-R1H.md` §“Post-initial integration repair rule”规定的四个 `verification/P02/` 路径与三参数 `.NET [IO.File]::Replace(stage,destination,apiBackup)`。唯一内容来源为 pinned Owner working-tree candidate；唯一旧默认数据流恢复来源为从精确旧destination经 `CreateNew` 复制的recovery。运行前后核验Git porcelain-v2 NUL record multiset、index SHA、ACL SDDL与alternate-stream清单/内容。不得调用其它Replace overload，不得创建其它临时/备份文件；异常不得重试、清理或自动回滚，须按Task fail-stop并保留部分状态。

在开始创建stage/recovery前，Codex仍须先完成目标目录/卷、普通非reparse、源/目标hash、stage/recovery/API backup absent及not-ignored、只读ACL/ADS查询、受控status/index基线和所有证据路径核验。任何未知状态或失败即停止，不调用Replace。只有Replace及所有post-check均成功后才记录该单文件集成成功，并由Codex运行AC4规定的PowerShell 7.6.6 parser/selfcheck/preflight。

## Gate与授权原值

保持：`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；风险原文=`technical condition unmet; user explicitly accepted residual risk`。Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；Build/Cargo=`NOT_RUN`；系统AC1–AC7=`BLOCKED / NOT_RUN`。本次静态Review和adjudication不把其中任一项改为PASS。

实际根环境=`gpt-6-luna/max`；优先配置`gpt-6.1-sol/high`当前不可用。Reviewer实际模型/力度未提供，记录=`UNKNOWN`。

## 证据

- Task：`doc/tasks/P02PRE-R1H.md`，本轮前SHA-256=`10CD84B847AD82D02BF3D1AD48711FDB095E17F703A27FB2EC6E7B51F9E1D108`。
- R2 Review：`verification/P02/codex-subagent-p02pre-r1h-integration-protocol-review-r2-20261012.md`，9375 bytes / SHA-256=`1D8D78A479887470B0B2065F68E4DC5073493C141868320C231B55198F2F3E7C`。
- Frozen pins：`verification/P02/codex-p02pre-r1h-integration-protocol-review-r2-pins-20261012.json`，SHA-256=`DE58847092D56476B54323E0FE4E8103D8E7FBD99D47D11C6F191289BEEBED51`。
- Review dispatch：`verification/P02/codex-p02pre-r1h-integration-protocol-review-r2-dispatch-20261012.prompt.md`，且包含上述完整pins hash。
- Root post-review独立复算：13/13 inputs、3/3 candidate files、Owner frozen identity/status、destination bytes、Review report与dispatch/pins链接均匹配；三个候选写入路径逐项`Test-Path=false`、`git check-ignore` exit 1。

**下一步：**准备唯一执行证据文件并刷新唯一DAG/STATUS/checkpoint；随后在创建任何Stage/Recovery之前执行完整只读preflight并记录S0。未经preflight全通过，不执行文件创建或Replace。