# Codex VERIFY 与结果裁决：baseline-20261014T0430CST-ac3fix

## 裁决

本结果是一次完整、失败闭合的新时点采集；它不满足 AC3，不构成准入，不释放 X6。旧 H1/P2-1 结论、OPEN finding 与 13 项历史来源缺失记录保持原样。唯一输出不重试。

## 证据绑定与 Codex VERIFY

- 运行时源码 HEAD：`360d7286e32b4d7b766aa434c0e31f210100ec18`；证据提交/review_head：`83588bbdca96a3c2d52a0ccae73f3710eda296c1`。证据提交只记录 Task、freeze 与失败输出；collector 源文件未改。
- Freeze manifest：`freeze/baseline-20261014T0430CST-ac3fix.freeze.json`，SHA-256 `37B2D607DC44944B085561F8C17DB0FBA512589AF9D0BC3E3F270B42E9ED9535`。
- 唯一 closed output：`run-baseline-20261014T0430CST-ac3fix.json`，SHA-256 `FBDF1E9C4AEB76E327C3C143C7B24C5F98DC27840D774741D442C24CD3728C49`；6 行，末行 `closed`，`FAILED_STOPPED / BLOCKED_EXCEPTION_FAIL_CLOSED / exitCode=6`。冻结 RunId 永久保留，不得复用。
- DSH input manifest：`dsh-result-review-manifest-20261014T0430CST-ac3fix.json`，SHA-256 `EBEB326B39C1A77962C82CE85D371F2316BF403DD88696C79F79F8D3B216DA07`。Codex 使用官方 `generate-evidence-manifest.py --verify` 复验 3 项（collector source、freeze manifest、closed output）：`PASS`, 3/3, exit 0。DSH 无法在其 shell 重算 hashes；其 hash 结论保持 UNKNOWN，不覆盖 Codex 的独立验证。
- DSH `ACCEPTED_RESULT` 仅接受运行闭合和失败机制，不表示 AC3、Task 或 X6 通过。原始 DSH 结果、prompt、exit 与 manifest 均已保存；原始 DSH stderr 只保留在 workspace agent-output，不作 Review 内容展示。
- Freeze preflight 记录 `/git/head=360d728…`、分支 ref 正确，`p02-task` frozen pin expected=observed=`463BDE6D925BE3CF892A84E9E8BFB5C1903C17602A58F722CEC79B0EA57854A4`、match=true。`freeze/p02-task-pre-run-20261014T0430CST-ac3fix.md` 与该 SHA 相同。其后 Task 更新记录采集结果；这是预期的 post-run 状态变化，不是冻结输入被篡改。未来每次采集仍须按当次 Task/source 重建 freeze。

## Finding 与范围

- `AC3-WHOAMI-HELPER-OUTPUT-SHAPE`：Codex 采纳 DSH 的 P1。`Invoke-HelperProcess` 成功和异常路径均生成 `output.stdout/stderr`，而 `Invoke-InProcessGetter` 与所有 helper consumers/pointers 使用 `output.value.*`。`identity-whoami` 在 `output` 缺少 `value` 时抛 `PropertyNotFoundException`；同一形状还影响 Git helper 的 9 个读取位置及 4 条 JSON pointer，若只改 whoami 会把失败移到 Git pin 阶段。当前 AC3 blocker、关键路径、不可独立拆分；AI 可修复，无用户独有输入。
- `AC3-SELFTEST-HELPER-SHAPE-COVERAGE-GAP`：采纳 DSH 的 P2，与根因一并放入同一个 resolution Task；加入纯静态形状断言，覆盖 helper producer 成功/异常两条输出构造。不会再为同一根因另开 Task。
- `AC3-FREEZE-PIN-P02TASK-POST-RUN-STALE`：DSH 建议 P2；Codex 定为 P3。preflight 与冻结 Task snapshot 证明该 pin 在采集前正确；运行后 Task 记录结果造成的 SHA 变化是正常时序。AC4 按 freeze-time snapshot 核验，不把当前 Task SHA 与旧 freeze pin 混比。
- `AC3-RESULT-PROTECTION-RECHECK-NOT-RUN`：P3。执行在 identity 阶段停止；保护对象前后 hash、Git HEAD/ref/status 与 index 检查均 `NOT_RUN`，不得写成 PASS。
- `AC3-RESULT-RAW-MATERIAL-STDOUT-ENCODING`：P4。raw stdout 的解码与手写 prelaunch 备注不作为确定性证据；以已验证 NDJSON closed output、freeze manifest 与 process exit 为准。原始材料保留。
- 已确认的安全边界：历史路径隔离、CreateNew 输出准备、runtime 三项检查均 PASS；失败点早于任何 Git child、pin/index 查询或保护源写入。此结果不证明后续未运行检查，也不外推历史行为。

## 收敛与下一节点

正式 `decide-convergence.py --mode converge --dry-run` 输入/输出见 `convergence-ac3-helper-shape-review-{input,output}.json`。结果：`BLOCKED`，I1/I2=2/2，禁止 I3；创建一个 resolution Task 并重规划 DAG；`wait_external=false`，没有用户独有输入。

下一节点为 `P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION`：只在 `tools/p02/p02-new-time-baseline.ps1` 两个 helper 输出构造点统一 `output.value` 形状，并在对应 selftest 加纯形状断言。Task 不运行 collector，不重用旧 RunId，不执行 X6 或后续 Gate。ZCode 实现、DSH 有界 Review、Codex VERIFY/集成。集成后父 Task 重新冻结源码与全新 RunId，才能尝试一次新的 AC3 采集。