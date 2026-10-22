# P02PRE-R1G Follow-up 1 DSH Review 派发裁定

日期：2026-10-12（Asia/Shanghai）  
Task=`P02PRE-R1G`；Codex role=`Integrator/Adjudicator`；implementation Owner=`Antigravity`；attempted Reviewer=`DeepSeek Harness`。

## 裁定

`REVIEW_STATUS=INVALIDATED / NOT_A_REVIEW`；`AC4_RELEASE_REVIEW=NOT_ACCEPTED`。本次没有有效 final report 或 verdict；未确认任何实现 finding，也不形成 candidate approval。候选代码没有因本次 DSH 轨迹发生改动。

## 派发与原始证据

- DSH CLI=`0.2.0-rc.2`；session=`session-d65775ad-9be3-4f16-892e-c08fb8c1c018`。Codex 从主仓 `G:\CODEX\New Manga` 启动 DSH；项目协作协议 `doc/09_COLLABORATION.md` §6.1 要求从被审查 Task 的 linked worktree 根目录启动。此为 Codex 派发程序偏差。
- Frozen prompt=`verification/P02/dsh-p02pre-r1g-remediation-review-followup1-20261012.prompt.md`，`7237 / 3510E5B9C0CA57B0E9853E47281019B10E7DA6ECF39CEE5C4165FE09BE12E4CA`；pre-dispatch pin evidence=`verification/P02/codex-p02pre-r1g-review-input-pins-followup1-20261012.json`，`4679 / 46EC1777D269146CE8B902957F9ABFB98C10ADF871DC5A34710EE333D31FD14C`。
- Raw JSONL=`verification/P02/dsh-p02pre-r1g-remediation-review-followup1-20261012.stdout.jsonl`，`167850 / D8A5A1004BA5279B37AE211048B9B821E16F59D1B0A37F7FEE4096D45953842F`；86 行中 85 行可解析 JSON，最后一个可解析事件为 `tool_call`，没有 final Review event。stderr=`0 / E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855`。`.exit` 目标不存在，实际 DSH exit code=`NOT_OBSERVED`；未伪造数值 exit。Codex 在发现策略违规后终止精确进程树 PID `52472` (`node.exe`) → `34048` (`pwsh.exe`) → `29612` (DSH launcher)；事后核验这些 PID 均已退出。
- Post-review pin evidence=`verification/P02/codex-p02pre-r1g-review-input-pins-followup1-post-20261012.json`，`11289 / D561AD873B309091CFFCAE816A03EAED31C49B88CAEB8BDB3632E74F2B1513D9`；12 个 pre-dispatch input pins 均匹配 (`12/12 MATCH`)。候选 branch/HEAD 与授权三文件 diff 未改变。

## Raw tool-trace 审计

- 停止时 JSONL 记录 `20` 次 tool call、`19` 个 result、`1` 个未完成 call；工具仅有 `read=16`、`grep=4`。
- Frozen prompt 只允许对表列 exact paths 使用 `read`，明确禁止 `grep`。DSH 对 candidate 与 predecessor source 使用了 4 次 `grep`，其中最后一次仍 pending；即使检索对象在表列路径内，工具类型仍属越界。
- 一次 `read` 访问了 `codex-p02pre-r1g-review-input-pins-followup1-20261012.json`。Prompt 在叙述中提到此 evidence path，却没有把它加入 exact-path allowlist 表，因此该访问也超出冻结表列路径。该偏差由 Codex prompt 文案造成；下一轮不再把 pin evidence 路径放入 Reviewer 的内容读取范围。
- 轨迹中没有记录对 `.tmp.driveupload` 路径的读/搜寻；这只表示本次已保存轨迹的目标列表未出现该路径，不推断其他状态。Codex 没有读取/stat/hash/查询该路径。

## 影响与后续

以上工具边界违规及派发 CWD 偏差使本轮不能作为独立 Review。保留所有原始 JSONL/stderr 与 pin evidence，不将部分文字/思考内容当作报告或 findings。主仓仍未集成 candidate；parser/self-check、PS7 child preflight、capture、host getter、Build/Cargo、AC1–AC7 均未运行。Gate 仍为：`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；`technical condition unmet; user explicitly accepted residual risk`；Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；Build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`。

下一轮由非作者 Codex Reviewer sub-agent 执行静态内容 Review（项目协作协议 §1 允许 Codex Review Antigravity 实现），root 继续担任 Integrator/Adjudicator。Review 前先更新 Task/manifest，冻结精确输入 pins；Reviewer 不写文件、不运行代码、不访问 `.tmp.driveupload`。这不豁免 AC4 的独立审查或任何后续 Gate。
