verdict: unacceptable

---
task_id: UIUX-V2-RUNTIME-REALCORE-2
reviewer: Codex
author: DSH
base_commit: f68184b60
reviewed_head: 3070050a8db6b9423eff0deb6cbb71d5a5bfa29d
decision: changes_requested
scope: 仅审查 DSH 在 apps/desktop/frontend/e2e/uiux-v2/run.mjs 的收口 diff；不重审整体 Task。

# Review：UIUX-V2-RUNTIME-REALCORE-2 — DSH closeout diff

## 范围与依据

审查固定于 `f68184b60..3070050a8` 的 `apps/desktop/frontend/e2e/uiux-v2/run.mjs`。对照了 Task AC1、DSH r2 的架构证据说明、最终 `run-i34/report.json`，以及脚本打印/exit 判定路径。未修改产品代码或验收脚本。

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态/修订 commit |
|---|---|---|---|---|---|---|
| R-CLOSEOUT-1 | P1 | `apps/desktop/frontend/e2e/uiux-v2/run.mjs:765-771` | 循环把 S8 的**每一条** FAIL 都改成 HUMAN_VERIFY，不只限于 file-input 注入失败。此前 S8 checks 还包含书架数据、创建章节、读取章节、对话框目标等自动化断言（同文件约 595-666 行）；这些真实回归若失败也会变成人工待验。`record()` 只看剩余 FAIL 决定 `ok`，最终 exit 依赖 report.ok，因而此类回归会让 S8/整轮保持 PASS。 | `run-i34/report.json:467,533-541,703` 显示 S8 `ok=true`、4 PASS + 5 HUMAN_VERIFY、`passRate=1`，总 report `ok=true`。在逻辑上只需让任一 S8 前置断言失败即可触发同一 blanket 转换；原 detail 虽保留但状态和失败门禁已被吞掉。 | 只把已证明由无 file input 导致的特定注入/后续依赖断言分类为 HUMAN_VERIFY；其他 FAIL 保持 FAIL。确保被降级状态保留原始类别/原因，并继续使未验证项显眼。 | open |
| R-CLOSEOUT-2 | P2 | `apps/desktop/frontend/e2e/uiux-v2/run.mjs:67-76` | 分母 `passed + failed` 实际同时排除 KNOWN_DEFECT 与 HUMAN_VERIFY，但 `passRateScope` 只声明排除 KNOWN_DEFECT，统计口径说明与实现不一致。 | `run-i34/report.json:533-541` 同时记 `humanVerify=5`、`passRate=1`，但 scope 字符串仍为 `PASS / (PASS + FAIL); KNOWN_DEFECT excluded`。 | 将 scope 文案说明为同时排除 `KNOWN_DEFECT` 与 `HUMAN_VERIFY`，并说明 passRate 不代表人工项已验收。 | open |
| R-CLOSEOUT-3 | P2 | `apps/desktop/frontend/e2e/uiux-v2/run.mjs:758-764` | CDP DOM 注入不可用的结论有实测支持，但“该路径端到端只能人工验”范围过宽。当前证据证明页面无 `input[type=file]`、CDP `inputNodeId=0`；它不证明系统原生选择器无法经 Windows UI Automation/键盘驱动。此前 UIA 轮次的文件名控件定位失败是当前自动化实现失败，不等于原生对话框无法自动化。 | `run-i34/report.json:76-82` 记录 `inputNodeId=0`；`verification/UIUX-V2-RUNTIME-REALCORE-2/test-e2e-r2.log:54-60` 留有注入失败证据；Task 执行记录称先前 UIAutomation 未取得 filename control。没有本次新跑 UIA/键盘自动化的正向或排除性证据。 | 将结论限定为“CDP 文件注入不可用；当前自动化未覆盖原生选择器路径”，将原生选择器自动化作为未验证能力，不要仅据 inputNodeId=0 推出所有自动化路径均不可能。 | open |

## 对必答问题的判断

1. **可见性与是否被吞掉：部分可见，但失败门禁确实被吞。** `humanVerify()` 的 `ok=false`（`run.mjs:107-115`）没有被 `record()` 用作 scenario 判定；它按 status 另计数，只有 `totals.failed===0` 时 `ok=true`（`run.mjs:56-76`）。JSON 保留每条 HUMAN_VERIFY、原注入失败原因和人工步骤，且 S8 `checkSummary.humanVerify=5`（`run-i34/report.json:500-541`）；终端逐条打印 status/detail（`run.mjs:78-80`）。但场景摘要/最终摘要打印 PASS，process exit 取 `report.ok`（`run.mjs:989-993`），因此报告明确存在未验项的同时会整体 exit 0。尤其 blanket 降级会令真实前置失败失去 FAIL 状态。它不是完全隐藏，但会呈现“测试全绿、另有人工项”的易误读结果；标题虽写 HUMAN_VERIFY，仍不能代替正确的失败分类。
2. **可自动化路径：**返修轮确实实测了 CDP DOM 注入无节点，`inputNodeId=0`（`run-i34/report.json:76-82`），所以 `DOM.setFileInputFiles` 这条具体方案不可行。它没有证明 Windows 原生 picker 不能由 UI Automation 或键盘操作驱动；现有 filename control 定位失败仅说明该轮方法失败。若范围允许继续试，可在隔离验收环境中启动原生选择器后用 Windows UI Automation；若控件树不可用，再评估受控键盘导航/文件名输入并验证导入结果。没有足够证据断言该路径已经自动化，也没有证据断言不可能自动化。
3. **标题与 detail：基本诚实。** 标题明确标注“架构性 HUMAN_VERIFY，非失败”，check status 及 detail 明示人工步骤与原注入原因（`run.mjs:769-780`；`run-i34/report.json:465-530`），没有声称导入已通过。但“非失败”与 S8 PASS/整轮 exit 0 组合会淡化未验收事实，建议摘要同时显示 HUMAN_VERIFY 数量和待人工验收状态。
4. **统计口径：有一处明确不一致。** 每场景 `checkSummary` 含 `humanVerify` 和 `total`，所以没有漏计（`run.mjs:56-76`; `run-i34/report.json:533-541`）。但 `passRateScope` 漏写 HUMAN_VERIFY 被排除；并且它只在每场景里计数，没有全局 HUMAN_VERIFY 汇总。当前 S8 `passRate=1` 是自动化 PASS/(PASS+FAIL)，不代表 G1 验收完成。
5. **Verdict：unacceptable。** HUMAN_VERIFY 作为单独可见状态本身合理，CDP `inputNodeId=0` 也支持该注入方式不可用；然而无差别降级会隐藏 S8 中本来可自动化的前置回归，且 scope 描述错误、对“只能人工验”的结论超出证据。应先修正分类边界与统计说明，再接受该收口。

## 验证

| 场景 | 命令或手工步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| 指定单文件 diff | `git show 3070050a8 -- apps/desktop/frontend/e2e/uiux-v2/run.mjs` | 仓库 `main`，HEAD `3070050a8` | PASS（只读审查） | 目标 diff |
| 最终 JSON 与 CDP 注入数据 | 读取 `run-i34/report.json` | `3070050a8` | PASS（取证；未重跑 E2E） | `run-i34/report.json:76-82,465-541,703` |
| 终端呈现与 exit 判定 | 检查 `run.mjs` 打印及退出代码 | `3070050a8` | PASS（静态检查；未重跑 E2E） | `run.mjs:78-80,989-993` |
| 原生 picker 的非 CDP 自动化 | 未执行 UIA/键盘路径试验 | `3070050a8` | NOT_RUN | 既有 `test-e2e-r2.log:54-60` 只证明 CDP 注入失败 |

## 结论与复审

本报告只裁决 DSH 的单文件收口 diff，不重审整个 REALCORE-2 Task。当前 diff 不应按 `acceptable` 接受：R-CLOSEOUT-1 是 P1 判定门禁问题；R-CLOSEOUT-2/3 分别是统计文案与架构结论范围问题。修订后需针对新 diff 复审。没有执行测试；没有改动产品代码或验收脚本。

