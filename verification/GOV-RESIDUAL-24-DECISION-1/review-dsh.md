# DeepSeek 独立审查

session: session-5102f87a-ff32-417f-a755-d8c05f0e23c4；exit0；web_visibility=unverified

## 结论

**approved**（仅批准本 Task 的只读研究、事实汇总与自有 metadata；不批准 24 项修复、父 Task `done` 或任何保护解除）。

- 固定 base：`a2cceac539a77d8de9c0158b0b58a0063381dc66`
- Reviewed head：`d1ad7e525399d9fe50a05b9ddc0c74db067ce808`
- 分支：`main`
- 仓库：`G:/CODEX/New Manga`

## P0 / P1 / P2

- **P0：0**
- **P1：0**
- **P2：0（无阻塞性发现）**

口径说明（非缺陷）：`delivery_head` 与 4EV 的 commit 为 `9915cb69a...`，本次独立审查固定 head 为 `d1ad7e525...`。`9915` 是内容/证据提交，`d1ad` 是审核提交；4EV 在 `9915` 和 `d1ad` 均存在且字节一致。不得把 `9915` 误写成本次 reviewed head。

## 实测

- **Guard 24 项完整一致**：实际 `scan_repo_declarations(唯一 repo, workspace)` 返回 **24 errors**；`code/message/file` 多重集合与 `facts.errors[].error` 完全相等，missing/extra 均为 0。当前 guard 计数为 **2463 declarations / 1794 protected roots / 24 errors / 252 warnings**。`facts.protection_counts_snapshot` 的 2459/1790 是历史快照，不作为当前删除授权。
- **9 源保全**：9/9 的 raw SHA-256、字节数、NUL 偏移、Git status 与 `facts.source_fingerprints` 一致；P22 为 `?? verification/P22/...`，其余 8 个为 clean。9/9 的 SHA 同时与原 32 矩阵的 `source_sha256` 及 `source-facts.json` 一致。
- **分组正确**：`12` 个广域根错误 = **6 条 record、每条恰好触发 source/destination 两次、5 个唯一根**；`7` 个历史身份 = P19 3 项 + ENV-BUNDLE 1 项 + P19-UI 3 项；P19-UI 的 `%APPDATA%` 为 **2 条 record、1 个唯一用户根**；`2` 个 Review 模板均来自 `codex-closeout-p19-view-r12.md` 的嵌入式模板；`3` 个 NUL = P14 r1/r2 各 offset `286`，P22 offset `12330,20486`。NUL 偏移和严格 UTF-8 可解码性均实测通过。
- **NUL 记录未新引入声明**：`decision-facts.json` 自身的声明计数为 **0**；guard 新声明仅来自本 Task 自有 EV 表和 Resource Manifest，不是 quoted `verbatim_record_json` 被误当资源。
- **Git 支线**：19 条 branch tip 逐一 `rev-parse`，与 `facts.branches[]` 和父 `boundary-adjudication.md` **19/19 相等**；当前 **99 local heads / 137 worktrees**，与 facts 一致。19 条均写 `NOT_RESCANNED`，没有把旧 dirty/占用快照当当前删除依据。
- **diff 范围**：`base..HEAD` 仅 9 个文件：`STATUS`、`REBASELINE_PLAN`、`TASK_LEDGER`、本 Task 文档、Handoff，以及本 Task verification 下 4 个 evidence/metadata 文件。无旧 Task、旧 Review、旧 pin、代码或产品文件改动。
- **检查命令**：`git diff --check base..HEAD` 为 0；工作区 `git diff --check` 为 0；`pwsh -NoProfile -File tools/governance/check.ps1` 为 **PASS / EXIT0（2 warnings）**。warnings 是非终态 Task 数量提示和 STATUS 体量提示，不是本 Task 错误。
- **4EV**：4 行 path/commit/SHA 均正确；逐项核验为 **raw = Git blob = pin SHA**，且在 reviewed head 存在。`check.ps1` 实际对 4 行 EV 逐项校验通过；其 stdout 不单列 pin 计数，故“4”来自独立表行计数，不冒充脚本输出“EVIDENCE_PIN4”。

## 未测 / 限制

- 未重新计算 19 条支线的 patch、dirty、ignored、worktree 占用；旧快照不能作为当前删除依据。
- 未运行 24 项修复、guard 例外、模板/NUL 实现、父 Task `done` 或保护解除。
- 产品、构建、工具 109 回归、真实资源释放和恢复演练：**NOT_RUN**。
- 旧 bundle 仅确认文件存在并做了只读 `list-heads`，未做恢复验证；其“仅覆盖旧基线、不含后续/dirty/ignored/会话”只作为文档边界，不据此授权删除。
- 未逐行重读全部 24 条 `actual_locator` 原文；已用 guard 完整错误身份、9 源 raw SHA 和原 32 矩阵交叉核对。

## 边界

广域根“继续整体保留还是逐项核实后只保护已证明资源”仍待用户**显式裁决**；7 项历史身份缺少真实来源时继续 BLOCKED，不能用当前 `%TEMP%` / `%APPDATA%` 或用户记忆猜路径；模板/NUL 只允许后续另冻只读研究，不得跳过错误、收窄保护、重签旧 pin、删除 NUL、改原 JSON 或改原 Review。19 条支线全部保留；`main` 是唯一开发/集成主线，不代表 refs 只剩 `main`；r212 禁令和父 `blocked` 不变；未请求远端操作或删除窗口。

本 Task 未写任何文件，未改 ACL/ref/checkout/commit/apply，未执行 cleanup/GC/prune/push/网络/派发/Legacy 运行，未使用 `--out`。

## 推荐下一步

由用户先显式裁定 5 个广域根是否“继续整体保留”；Codex 再另冻精确保全解释设计、测试和独立审查，DeepSeek 复核。该设计不得实施清理、不得改旧 pin、不得猜历史路径；在用户裁决前保持现状和 BLOCKED。
