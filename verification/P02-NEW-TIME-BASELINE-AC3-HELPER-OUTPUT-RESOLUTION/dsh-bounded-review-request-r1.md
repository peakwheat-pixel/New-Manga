# DSH Bounded Review Request r1

Task：`P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION`

你是该 Task 的独立、只读 Reviewer；Owner=ZCode。请只审查固定 commit `b87ef080f1a7a5fb7a930753b26b5ab1e83efe49`，不要把当前较新的 Task 状态或 preflight-only 提交当作被审实现。

## 固定输入

- 代码与验证 HEAD：`b87ef080f1a7a5fb7a930753b26b5ab1e83efe49`
- 官方输入清单：`verification/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION/dsh-bounded-review-manifest-r1.json`
- 清单 SHA-256：`628AD5AA9F2A95109CAE9D4BF7DCB1BE33DBEDAC375951C6A15C92756250772F`
- 清单声明 `source_commit=review_head=b87ef080f1a7a5fb7a930753b26b5ab1e83efe49`，Codex 已验证 17/17 输入文件。
- 基线 commit：`16db22c707faf8336f2fc1e44397eaf1f8cb51ef`
- 允许的代码改动仅为 `tools/p02/p02-new-time-baseline.ps1` 与 `tools/p02/p02-new-time-baseline-selftest.ps1`。

先核对清单文件 hash 与声明的 source/review head。若无法核实固定输入，请停止并给出 `BLOCKED`，不要改用其他 HEAD。

## 有界审查范围

只判断以下事项：

1. 上一 blocker `AC3-WHOAMI-HELPER-OUTPUT-SHAPE` 是否在 helper-process 成功和异常 producer 路径均闭合：消费者读取的 `observation.output.value.stdout/stderr` 形状一致；whoami/Git consumers 和既有 JSON pointers 保持有效；不改变 `Invoke-InProcessGetter` 契约。
2. 本次两文件 diff 是否引入新的 P0/P1/P2；原 Task AC1–AC3、AC6 是否仍成立；新增纯静态断言是否覆盖两条 producer 路径且不启动 collector/child。
3. 受保护源文件、历史 H1/P2-1 结论与缺失记录、用户数据、运行输出及不可逆操作风险；确认本 Task 没有越界触发 collector/live query、RunId、X6、post-run Review、Build/Cargo、产品 AC1–AC7 或 Windows Sandbox。

不要扩展为仓库级审计。P3/P4 仅在与上述直接相关时记录为非阻断 backlog；不要把旧 H1/P2-1 的缺失证据当成本 Task 可修复范围。

## 执行与结果

- 只读静态检查；不要编辑/新增/删除文件，不要运行产品代码、collector、live query 或 child process。
- 对每个 P0/P1/P2 finding 给出唯一 ID、严重级别、固定输入中的文件/行或证据路径、影响的 AC/安全边界、最小必要处理动作。没有 finding 时明确写 `none`。
- 输出清单验证结果、上述三项逐项结论、发现清单、未执行项与最终结论。
- 最终结论只能是：无 P0/P1/P2 且输入有效时 `APPROVED`；存在需处理的 P0/P1/P2 时 `CHANGES_REQUESTED`；固定输入失效、无法核验或边界冲突时 `BLOCKED`。
- 不要把 `ACCEPTED_RESULT`、静态 Review 或测试摘要误写为父 Task 准入 PASS；本 Review 只决定该 resolution Task 的独立审查结果。
