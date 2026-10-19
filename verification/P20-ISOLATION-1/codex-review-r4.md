---
task_id: P20-ISOLATION-1
reviewer: Codex
author: Antigravity
base_commit: dbeca3babfb8689da113b5ef263501bcdf6ece61
reviewed_head: 3f4939d2110cae84f2533956f235ea6823030b9b
decision: changes_requested
---

# P20-ISOLATION-1 独立复审 R4

## 1. 结论

**decision = `changes_requested`。** R3 的 AC3 误定位已被真实注入修复；R-016 已闭环；当前代码也补上了 R-009 所缺的有界回收。R3 的两个 P2 均已处理。

仍不能批准：R-015 的交付元数据与 Canonical Evidence 仍未自洽，当前治理检查因 `library_bridge.rs` 的工作区 SHA 不匹配而 FAIL；此外，AC4 最新回归记录对应的可执行文件 SHA 与当前工作区可执行文件不同，所记录的 NFR 运行还包含 `ASSERT FAIL ac3:idle-memory`，因此 AC4 对当前 reviewed head 的“不回归”证据不完整。AC3 的真实运行也有计数台账错误：Task 写 12 项断言，trace 实际有 15 条 `ASSERT PASS`。

本 Review 固定审查 `dbeca3babfb8689da113b5ef263501bcdf6ece61..3f4939d2110cae84f2533956f235ea6823030b9b`。当前仓库 HEAD 是 R4 前审计提交 `3f4939d`。本次未运行产品测试；按只读要求核查了脚本、日志、截图、源码、Task/Handoff 和治理检查器。

## 2. R3 五项发现状态

| R3 finding | 级别 | R4 状态 | 核验结论 |
|---|---|---|---|
| R-009：关闭过程可能无界等待 | P1 | **已修复（代码路径）** | 当前 `library_bridge.rs` 的生产关闭路径使用带 reap timeout 的 `try_wait` 轮询，不再在强杀后无期限调用 `child.wait()`；reader 完成后才 join，超时则转交有界清理路径。R3 发现的阻塞点已不在当前实现。R4 未重新运行 Rust 测试。 |
| R-010：真实草稿写错控件 | P1 | **已修复** | 新 locator 先从“作品标题”标签的祖先容器查 Edit，trace 报告 `input-is-not-search-box (name='作品标题')`；之后才强杀 sidecar。 |
| R-015：交付头及证据记录互相不一致 | P1 | **未修复，阻断批准** | Task 为 `baf4ec90c`、Handoff 为 `796613ef4`；二者落后于最后一个 Task 实质验证提交 `e8cc6d1e4f441d2d43136c43281b3f59e36ab216`。检查器仍报 `library_bridge.rs` SHA mismatch。 |
| R-012：时间戳在慢查询前采样 | P2 | **已修复** | 当前 R004 脚本在 UIA/进程查询后采样；`r004-20261018-0838/trace.log` 记录故障文案 +84 ms、重生 +655 ms、恢复文案 +935 ms。 |
| R-016：行为断言 FAIL 不导致非零退出 | P2 | **已修复** | `A()` 在失败时执行 `$script:scriptFails++`（L25）；故障文案和重生行为断言调用 `A()`；末尾 `exit ([int]($script:scriptFails -gt 0))` 会对任何已计数失败返回非零。 |

R-015 中的 `delivery_head` 是交付元数据。把 Task 与 Handoff 对齐到完整的 `e8cc6d1e4f441d2d43136c43281b3f59e36ab216` 不会改 Git 历史或任何内容 hash；如果将来确定有多个提交共同构成交付，可在正文列出范围，而单值字段仍指向最终包含交付的提交。此字段与 Evidence pin 的 `commit` 不同。依 r27 §3、r28，**不得为消除 hash mismatch 而默默改写旧 pin 的 `commit` 或 SHA**；应保留原值、追溯失配来源，需要时追加有来源链的新 pin。当前检查器 FAIL 仍须在 closeout 中解决或明确留下经授权的限制，不能将“blob hash 不同”直接判为行尾问题。

## 3. AC 独立判断

| AC | R4 判断 | 证据与限制 |
|---|---|---|
| AC1 用户可见故障提示 | **运行中强杀场景 PASS** | R004 trace 与截图区分故障/恢复文案，故障在 +84 ms 被观察。R004 的 FAIL 计数现已闭环。未据此推断启动早期故障路径。 |
| AC2 心跳、自愈及有界关闭 | **当前实现支持；R4 未重跑测试** | R-009 原来的无期限 wait/join 路径已经改成有界进程回收和 reader 清理；R2 证据记录了无响应恢复及关闭测试。R4 只核代码和既存证据，不把它表述为本轮新测试通过。 |
| AC3 状态保全 | **真实注入 PASS** | `run-r010-ac3-real-injection.ps1` L123–151 的弹窗标题 locator 与 L252–262 的标题/非搜索框守卫正确；`r010-20261018-0944/trace.log` 记录输入真实标题、强杀 `core_service`、故障期间草稿保留、sidecar 重生、恢复后草稿保留及提交成功。截图 01/02 显示创建弹窗标题含草稿，截图 03 显示作品已创建。Task 称 12 项断言，但 trace 有 **15 条** `ASSERT PASS`；独立隔离库实查只在 Task 正文记载，数据库文件不在该 run 目录。上述差异应更正记录，不推翻截图和 trace 对草稿路径的证明。 |
| AC4 不回归 | **未充分验证当前 reviewed head** | e8 记录了冷启动 avg 0.474 s、四页 smoke `checks=5 fails=0`，并称 bundle/resource SHA 相等；但该次 EXE 为 `4d759983…`，当前工作区 EXE SHA 为 `BE593A88…`。另 `nfr-20261018-1152/nfr-trace.log` 明确有 `ASSERT FAIL ac3:idle-memory`（idle max 801.8 MB；该列与 CSV 的 `idle_ws_mb`/`total_ws_mb` 口径也不一致）。当前 bundle/resource 文件本身仍同为 `cd8dcc5e…`，但这不能替代当前主程序下的全项回归，也未解释 NFR 失败及 memory regression 条款。 |

### AC6 与 Task 状态

R010 的修正运行足以补上 P20 AC6 的真实草稿保全场景；与原始强杀/恢复证据合并，产品行为证据已明显完整。**但不能据此宣布 Task 或 P20 AC6 的治理 closeout 已完全完成**：本 Task 尚未通过 Review，AC4 当前 head 证据有缺口，Task/Handoff delivery 指针与 checker 错误未解决。P20 Task 的“12 项断言全 PASS”也应核对为 R010 trace 中实际的 15 条 PASS；这属于计数修正，不是 3 条失败。

## 4. 新增 finding

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| R-017 | P1 | `doc/tasks/P20-ISOLATION-1.md:41`; `verification/P20/nfr-20261018-1152/*`; 当前 debug EXE | AC4 标记通过，但测量证据指向 EXE SHA `4d759983…`，当前工作区 EXE 为 `BE593A88…`；同一 NFR trace 有 idle-memory FAIL 且汇总/CSV 字段口径不一致。不能证明当前 reviewed head 满足 Task 的 no-regression 条款。 | 已存 `nfr-trace.log`、`nfr-metadata.txt`、`coldstart-memory.csv`；当前 EXE 以 `Get-FileHash` 只读核验。 | 用当前代码构建重跑冷启动、四页、bundle/resource 和 AC4 明确引用的内存回归；统一并解释内存字段/阈值，保存原始结果。完成前不要把 AC4 作为完整 PASS。 | open |

## 5. R-015 / evidence pin 处置

- Task `delivery_head: baf4ec90c` 与 Handoff `delivery_head: 796613ef4` 应在后续有授权的文档 closeout 中统一为完整的最终 Task 交付提交；本 Review 只读，不直接改写它们。
- 证据 pin 的 6/10 blob 不匹配不能按 R3 建议一概归为时间/行尾失配。r27/r28 要求旧 basis 未明的 pin 保留原值；其中当前工作区 `library_bridge.rs` 确实不匹配，故仍是 checker FAIL，需要逐项来源核验/按规则追加 superseding pin，而不是覆盖旧字段。
- R010 run/script 的新 pin 已指向 `8898e56a0`，与 locator 修复提交相符；但 AC4 的当前运行证据没有出现在本 Task Canonical Evidence 表中。新产生的 Review/R4 也应依生命周期流程更新最新 Review 指针；本轮无权修改 Task/Handoff。
- 本轮执行 `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/P20-ISOLATION-1.md`：**FAIL（1 error, 2 warnings）**。唯一 error 为 `library_bridge.rs` SHA-256 不匹配；warnings 为 STATUS 预算 80% 及 evidence_dir 未登记过程文件。检查器不替代 pin basis 裁定或本 Review。

## 6. 完成状态与具体返修项

当前应保持 `status: in_review`、`review_status: changes_requested`。不应标 `done` 或 `closed_with_limitations`：剩余项是已声明 AC 的验证缺口和未解决的 P1 证据链错误，尚无授权把它们降为可接受限制。

完成下一轮前至少需要：

1. 在 Task 与 Handoff 中把 `delivery_head` 对齐至完整的最终交付提交；保留所有既有 Evidence pin 原值。
2. 追溯 `library_bridge.rs` 旧 pin 的 hash 来源，按 r27/r28 留痕；通过可追溯新记录解决当前 checker error，或提交明确的授权裁定与限制，不能静默重算。
3. 在当前主线代码上重跑 AC4，解释并处理 idle-memory FAIL/字段口径；将当前结果纳入 Canonical Evidence。
4. 把 R010 的断言数更正为 trace 中的 15 条 PASS，并将最新 Review 指针更新到 R4。

本 Task 尚未达 `done`，Plan 的 done 数仍为 42；本轮不应设置 `integration_commit`。若后续所有 Gate 通过并完成 closeout，因本 Task 直接在主线实施，`integration_commit` 应指向主线中实际包含已接受交付的完整提交（当前交付候选 `e8cc6d1e4f441d2d43136c43281b3f59e36ab216`，若 closeout 另产生提交则按实际集成记录填写）。在 R4 当前结论下，Plan 行保持 `in_review`、done 计数不变。

## 7. 验证记录

| 检查 | 方法 | 结果 | 说明 |
|---|---|---|---|
| R010 桌面注入 | 静态检查脚本、trace 和三张截图 | PASS（既存证据） | 未在本 Review 重跑。真实草稿定位/保全/提交成立。 |
| R004 时间与退出码 | 读 `run-r004-timeline.ps1`、trace | PASS（静态 + 既存运行） | `A()` 递增失败数；结尾将失败数映射为非零退出。 |
| R009 关闭路径 | 静态检查当前 `library_bridge.rs` 有界 wait/reap/join 代码 | PASS（代码路径） | R4 未运行 Rust 测试。 |
| AC4 当前 head 回归 | 核查 e8 的原始记录与当前 EXE | BLOCKED | EXE SHA 不同；已有 NFR trace 有失败项且内存列口径不一致。 |
| Governance checker | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/P20-ISOLATION-1.md` | FAIL（1 error, 2 warnings） | `library_bridge.rs` pin mismatch。 |
| 产品测试/新桌面注入 | 未执行 | NOT_RUN | 用户限定只写 Review，未授权运行或改写其他产物。 |

**推荐下一步：** Antigravity 先完成上述 1–3 项返修并提交可复核证据，再由 Codex 对新 reviewed head 复审；当前不派发新的独立 Task，也不关闭本 Task。
