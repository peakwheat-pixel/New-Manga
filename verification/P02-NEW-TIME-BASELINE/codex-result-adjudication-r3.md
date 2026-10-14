# Codex 结果裁决 r3：P02 新时点基线准入

- Task：`P02-NEW-TIME-BASELINE`
- 裁决者：Codex /root
- 结果：`AC3=PASS`；`AC5=ADMIT_X6`
- 适用范围：仅判定 `baseline-20261014T0915CST-p02-admission-r2` 对当前版本新时点准入的证明力。

## 证据与 Codex 验证

- Freeze manifest：`verification/P02-NEW-TIME-BASELINE/freeze/baseline-20261014T0915CST-p02-admission-r2.freeze.json`，SHA-256 `8662DEC583D2FD865532A414F0BEDE63B7F02872AB3C9232553C3B01E239006D`。Codex 重新验证 17/17 immutable pins，全部匹配。
- Collector result：`verification/P02-NEW-TIME-BASELINE/run-baseline-20261014T0915CST-p02-admission-r2.json`，SHA-256 `CAAC6AFDE8D479CABCD839E2B74FDD86A1ECD8B59E5E8C88100A552382A9458E`，161,783 bytes；64 行闭合（1 meta、62 observations、1 closed），57/57 checks PASS，collector exit 0，stderr 0 bytes。
- Codex deterministic result verify：`codex-result-verify-r2.json` 状态 `PASS`；17/17 freeze pins 仍匹配，结果与 RunId/hash 绑定，采集时记录的 Git status bytes 与 Codex 核验时一致。旧 H1/P2-1 未被替代或声称关闭；该验证记录的 `x6Released/postRunReviewRun/buildCargoRun/productAC1toAC7Run` 均为 false。
- DSH 输入 manifest：SHA-256 `82B0A97B8C95C2D268DFACB04C333260CC48D01E964E81FDE6969927B6A10BDB`；Codex 官方 verifier 在 DSH Review 后再次验证为 `PASS`，28/28，`problems=[]`。DSH 无 PowerShell/Git 权限，故其哈希与 commit 核验限于记录值交叉比对；该限制按 F-05 保留。
- 独立 DSH Result Review：`dsh-result-review-baseline-20261014T0915CST-p02-admission-r2-r3.md`，SHA-256 `D0F4C7C40D0E770FC12E9B520E194678FF030114F6035DEA501DC5C6F4871B9C`；结论 `ACCEPTED_RESULT`，无 P0/P1/P2。它只接受结果证据，不替 Codex 关闭 AC3/AC5，也不批准下游 Gate。
- 集成验证：main commit `d6745a45a8100da949004d42cbc9d397c395d303` 只新增已审查的 collector 与 selftest 两个文件，其 Git blobs 分别为 `630833290e8e6be89ac38ab089bb8efae4872894`、`519a48c77e9d4db1c39aa12fd198573f5118a163`，与 delivery `318bc2a1` 一致。PowerShell 7.6.6 `-NoProfile` 自检为 234 PASS / 0 FAIL / 7 SKIP / exit 0；七项均为本 Task 禁止或后续 Gate 保留项。

## DSH Findings 处置

| Finding | 级别 | Codex 处置 |
|---|---:|---|
| F-01：Owner 披露的内部 pre-collector launcher probe 未提供原始命令/输出或独立 launcher 文件 | P3 | `DOCUMENTED / BACKLOG`。DSH 接受唯一已完成 collector 结果；Codex 保留该证据完备性限制，不将它记为 collector 失败，也不要求返修。 |
| F-02：冻结 Task snapshot 的 AC2 状态文本滞后 | P4 | `DOCUMENTED / BACKLOG`。AC2 的 source Review 与 Codex VERIFY 早于采集，且各自有独立证据。 |
| F-03：真实 stdout 表格有截断/编码问题 | P4 | `DOCUMENTED / BACKLOG`。完整结果 JSON 是权威证据，57 项 check ID/result/pointer 可枚举。 |
| F-04：collector argv 未在 freeze manifest 中机读记录 | P4 | `DOCUMENTED / BACKLOG`。argv 保存在已 pin 的派发 prompt；RunId、CWD、freeze hash 与唯一输出目标由代码 fail-closed 校验。 |
| F-05：DSH 环境无法执行 shell/Git/官方 verify | P4 | `DOCUMENTED / COVERAGE LIMITATION`。Codex 已独立核验当前 pins，并重跑官方 manifest verify 28/28。 |

这些 finding 均未构成当前 AC 的 P0/P1/P2 blocker；按新版 orchestrator 不开 I3、不为 P3/P4 启动返修或 follow-up。F-01 至 F-05 保留为 backlog/限制，不隐藏或升级为技术 PASS。

## AC 与 Gate 裁决

- AC1、AC2、AC4、AC6：沿用 Task 中已完成且有证据的结论；本轮未改写其来源。
- AC3：`PASS`。Freeze/result pins、one-shot 结果闭合、57/57 checks、DSH `ACCEPTED_RESULT` 与 Codex 官方 verify 均通过。
- AC5：`ADMIT_X6`。只释放独立的 X6 Task；下一 Gate 是 X6 的受控执行与 post-run Review。
- AC7：代码集成及集成后 selftest 已通过；Task closeout 仍需完成文档、证据清单、资源分类与 governance check。

官方 convergence 输入/输出见 `codex-baseline-convergence-r3-{input,dry-run,output}.json`：`APPROVED`、`REPLAN_DAG`、`BACKLOG_NONBLOCKERS`、`wait_external=false`、禁止 I3。无 `BLOCKED_WAITING_EXTERNAL_DECISION`，不请求人工裁决。

## 历史边界与下游门禁

本次新时点结果不补齐、不覆盖、不关闭或替代旧 H1 / P2-1 结论、OPEN finding 或 13 项原始来源缺失记录。X6 是唯一可进入下一 READY 的 Gate；post-run Review、Build/Cargo、AC1–AC7 尚未释放、未执行。Build/Cargo 与产品 AC 必须分别满足其后续 Gate；既有 `Hard Build Barrier=EFFECTIVE` 不因本裁决自动解除。
