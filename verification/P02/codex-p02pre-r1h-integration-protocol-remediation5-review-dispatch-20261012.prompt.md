# P02PRE-R1H post-initial integration protocol 独立 Review

你是非作者 Reviewer `/root/p02_r1h_remediation_review`；Integrator/Adjudicator=`/root`。本次不复审候选代码本身的静态 verdict；Round5 candidate 已有单独 `APPROVED_STATIC_CONTENT` 报告。请独立评估 Task 新增的 post-initial integration update rule 是否足够安全、精确、可恢复，是否与协作治理和 Task 范围冲突。

## 冻结对象

- 仓库=`G:\CODEX\New Manga`
- Task=`doc/tasks/P02PRE-R1H.md`（当前追加 Round5 AC4 integration remediation protocol）
- Delivery=`agent/codex/P02PRE-R1H@dd5d2e3bc8e0702da9d059131f6364a997897661`
- frozen Task base=`946938bd0696dfddd01f87d61fe6723c63ecdc86`
- pins=`verification/P02/codex-p02pre-r1h-integration-protocol-remediation5-review-pins-20261012.json`
- prompt=`verification/P02/codex-p02pre-r1h-integration-protocol-remediation5-review-dispatch-20261012.prompt.md`
- 唯一报告=`verification/P02/codex-subagent-p02pre-r1h-integration-protocol-remediation5-review-20261012.md`

先验证 Task/current governance/protocol pins、round5 commit candidate pins、当前集成 selfcheck old hash=`EEFB...` / 57,623 bytes、new reviewed candidate hash=`977C...` / 57,648 bytes、stage/backup 唯一路径 absent。报告 pre/post pins。若任何不符，停止。

## 审查问题

Task addendum 的方案是：现有 root-created integrated R4 file 必须仍与精确旧 SHA/bytes 匹配；新 stage 与 backup paths 必须 absent；先以 `CreateNew` 写入且 hash-match 评审通过的 R5 bytes；再用同目录 `.NET File.Replace(stage, destination, backup)` 原子替换；验证 backup 保留旧 R4 hash/bytes、新 destination 为 R5 hash/bytes；异常或碰撞立即停止。评估：

1. 旧 destination ownership 与 expected hash 是否足以授权唯一指定文件的更新；
2. backup/stage 的路径/同卷/absent/CreateNew/atomic replace 与 post-hash 是否闭合且可恢复；
3. 该 narrow procedure 是否违反 AC4 的首次 `CreateNew` 要求、协作协议或用户数据保护，Task 是否足够限制为单文件/单次；
4. 是否遗漏 ACL/streams/metadata 语义等实际会影响该 `.ps1` 的重要风险；
5. 如何避免备份/stage path 被捕获器当作未授权变化或未知输出。

如需修改 Task wording，给出具体 finding 与最小建议，不要直接修改 Task。Review 可给 `APPROVED_STATIC_CONTENT` 或 `CHANGES_REQUESTED`，附 P0/P1/P2/P3 count。

## 限制

只读检查、hash、Git diff/metadata；仅允许写唯一报告路径。不得运行 parser/selfcheck/fixtures/preflight/capture、host getter/API、tests、Build/Cargo、AC1–AC7、OS dynamic/Sandbox；不得集成或改源码。不要访问 `.tmp.driveupload`。报告准确记录 actual model/effort (UNKNOWN if unavailable)、pins pre/post 与未运行项。