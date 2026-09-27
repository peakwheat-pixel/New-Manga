# DIAG-READING-EXPORT-001-FIX-A 集成核验记录（Integrator=代行 Codex，2026-09-28）

- Owner：ZCode；非作者 Reviewer：DeepSeek Harness（双轮）；Integrator：代行 Codex（ZCode 会话，待真 Codex 追认）
- 固定 base：`32ef1dd60cd82ac3a5fa18dfc5f834ec8639164a`（FIX-A 释放冻结点）
- Owner 交付：R1=`77a78b25`（tip `3f3bd7a9`）→ DSH R1 `changes_requested` → R2=`db5ee918`（tip `6fe7bd86`）→ DSH R2 `approved`
- Review 归档：[r1](../../../../doc/reviews/DIAG-READING-EXPORT-001-FIX-A-dsh-r1.md)（changes_requested，1×P2+5×P3）、[r2](../../../../doc/reviews/DIAG-READING-EXPORT-001-FIX-A-dsh-r2.md)（approved，6/6 处置通过 + 5×P4 观察），逐字节导入，SHA256：[sha256.txt](../review-dsh-import/sha256.txt)（r1=`fff5f1f6…`、r2=`5dbce59e…`）
- **Integration merge：`a8b94df1f1ee091a9cca894c421e9ffc3ad30614`**（parents `0b30d3d9`（Review 归档 commit）+ `6fe7bd86`（Owner tip）；Owner 历史未改写；唯一冲突 `doc/tasks/DIAG-READING-EXPORT-001-FIX-A.md` 按先例取 Owner 交付版，随后治理写入 `done`）

## 集成核验

| # | 检查 | 方式 | 结果 |
|---|---|---|---|
| N1 | 历史 | `git merge-base 878bf2a5 6fe7bd86` = `32ef1dd6`（Owner 分支直接生长于固定 base；提交链 claim `d793939d` → R1 `77a78b25`/`3f3bd7a9` → R2 `db5ee918`/`6fe7bd86`） | PASS |
| N2 | 范围 | `git diff --name-status 32ef1dd6..6fe7bd86` = 8 路径（6A+2M），全部在 Task allowed 清单；`src/**`、`packaging/**`、`requirements*`、`doc/contracts/**` 零命中（产品代码零改动，测试侧方案） | PASS |
| N3 | 卫生 | `git diff --check 32ef1dd6..6fe7bd86` | exit 0，PASS |
| N4 | Review 双轮闭环 | R1 `changes_requested` 的 P2（snapshots 排队消费暴露面）经 R2 实质修复；5×P3 逐条处置；R2 复核 `approved` 且确认"合取谓词严格强于旧谓词，未放宽断言" | PASS |
| N5 | 集成 head 全仓复跑（DSH O5） | `python -m pytest -q -p no:cacheprovider -rs tests` @ 集成 head：**1316 passed, 5 skipped, 1 warning, 68.51s**，[integration-full-suite.log](../integration-full-suite.log) | EXIT=0，PASS |
| N6 | 口径一致性 | 1316+5 与 R1 全仓一致；与 DIAG 基线 1310+11 的差值 = 6 个 OpenSSL 用例（本 shell `/mingw64/bin/openssl` 3.5.4 在 PATH，实跑通过）；5 skip = 2 docTR + 1 numpy + 2 torch | PASS |
| N7 | 结论口径 | 修复=测试等待语义；产品排队投递行为未变，QML/用户路径不受影响；诊断 U3 仍未决；无"flaky 已解决"的产品级声明 | PASS |

## DSH R2 五条 P4 非阻塞观察（全部 deferred，集成后择机）

| O# | 内容 | 处置 |
|---|---|---|
| O1 | 探针阶段 B "MISSES" 行结构性恒 0，标签易误读 | deferred（判定已用 completed，结论不受影响） |
| O2 | 探针 `broken iters == 0` 时误报负判定 | deferred（退化调用防护） |
| O3 | Handoff :106 措辞与 C 阶段实际判定（detected_failures）不完全对应 | deferred（含义可由上下文与代码恢复） |
| O4 | Handoff §3 行 1 证据列未更新为 targeted-suite.log | deferred（targeted-suite.log 本身已入库可查） |
| O5 | R2 head 未重跑全仓 | **closed by N5**：集成 head（包含 R2）全仓复跑 EXIT=0 |

## 结论

[DIAG-READING-EXPORT-001-FIX-A](../../../tasks/DIAG-READING-EXPORT-001-FIX-A.md) 置 `done`，integration_commit=`a8b94df1f1ee091a9cca894c421e9ffc3ad30614`。下一 Task：按串行规则释放 [DIAG-READING-EXPORT-001-FIX-B](../../../tasks/DIAG-READING-EXPORT-001-FIX-B.md)（读者心跳生命周期，Owner=ZCode、Reviewer=DeepSeek Harness），base=本集成治理提交后的 main HEAD。
