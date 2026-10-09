角色：P02 的独立非作者 Reviewer（DeepSeek Harness）。本轮作者为 Codex；请独立判断，不预设通过。

任务：复审 P02 R7 Smoke pre-start 证据返修，确认 R7 F-01..F-10 是否得到充分处置，并检查本轮新增问题。
Review base=26691a90e7005afa43c9390d51b0640335cdb2e0
固定 Delivery HEAD=6be3dfdb1911a358ac779e1398437b0411bf2cfa
固定 Delivery tree=f2d7b2637e18b59470cffd239287f130fe0beebc
branch=codex/P02-process-isolation；review worktree/当前目录=C:\Users\49745\.codex\worktrees\p02-process-isolation-plan\New Manga。

先核实 git rev-parse HEAD 与 git rev-parse 'HEAD^{tree}' 精确匹配；只对该 commit 作结论。请以 git diff base..HEAD、git show HEAD:path 读取已提交内容；不要把当前 worktree 的任何 untracked 文件当成候选交付内容。

范围：仅 documentation / verification；29 个变更路径见 git diff --name-only 26691a90e7005afa43c9390d51b0640335cdb2e0 6be3dfdb1911a358ac779e1398437b0411bf2cfa。主要文件：doc/tasks/P02.md、Plan/Status/Index、R2 admission/delivery/R3 timing checkpoints、R1/R2 collector、codex-smoke-prestart-manifest-check.py、其 synthetic self-test、R2 errata 与验证日志。

请逐项判断：
1. F-01：artifact-only validator 和持久 stdout/exit 是否真正独立复核 summary + 11 records 的 SHA/canonical/schema/order/count/mapping/policy 等内部一致性；检查日志是否绑定候选 checker。
2. F-02：compare/recheck 是否只读，能比较当前 11 个映射的路径/type/size/selected hashes 与基线，并 fail closed；synthetic match 和 mismatch 自检是否能验证核心判决。静态检查实现即可，禁止实际运行 recheck。
3. F-03..F-10：P05 failover checkpoint 链接恢复；R2 item 5 的 superseded timing 标记；12-root Stage-1 vs 11-mapping Smoke scope 桥接；R1 invalid marker；原 R2 capture exit 保持 UNKNOWN / NOT_RECORDED；硬编码 reparse 计数的事实澄清/派生；旧 UI enumeration 标明历史并要求启动前新证据；INDEX 显示 50,356 full hashes、33 samples、138,947 未计算文件内容。
4. Task/Plan/Status/Index 和 checkpoints 的状态一致，且 Smoke=NOT_RUN、完整 preflight=BLOCKED / INCOMPLETE、Build Gate=BLOCKED、build=NOT_AUTHORIZED / NOT_RUN、AC1–AC7=BLOCKED / NOT_RUN、Hard Build Barrier=EFFECTIVE。

安全边界：只读。不要修改任何文件；不要调用 recheck 或 scanner；不要读取、枚举、扫描或哈希任何实际 HostFolder 内容；不要启动 WSB/Sandbox、guest command、Build、runner/Vitest/GUI/WebView 或产品测试。可执行 artifact-only validate（若环境可用）和路线 validator；必须区分实际执行与静态检查。

最终报告（简洁中文）：decision: APPROVED | CHANGES_REQUESTED | NOT_VERIFIED | BLOCKED_BY_MISSING_EVIDENCE；确认 HEAD/tree；P0/P1/P2/P3 counts；每个 finding 的稳定 ID、级别、精确路径/行号、影响、最小修复；列出实际运行与未运行项。若没有发现，写 findings: none 并保留尚未验证的宿主/运行时限制。不要把 NOT_RUN/BLOCKED/UNKNOWN 写成 PASS。