# P02-NEW-TIME-X6-AC1-AC7 — Findings (run-r1, 2026-10-14)

RunId=`p02-newtime-ac-20261014-r1`。本文件只登记 finding，不修复、不扩大范围。产品级 finding 必须来自真实运行观察；本轮**没有任何真实运行发生**，因此**没有产品 finding**，只有环境/流程 finding。

## ENV-01（环境/流程，非产品）

- **严重度**：P1（阻断本 Task 全部产品 AC 的执行）
- **类别**：execution-environment
- **事实**：Owner（ZCode）派发会话的 Bash 工具没有权限客户端（"No permission client configured for Bash"）。一切执行类命令（`node <script>`、`python -c`、`powershell`、`certutil`、`git add/commit`）被拒；只读探针（`node --version`、`sha256sum`、`ls`、`grep`、`git log`）可用。general-purpose 子代理复现同样错误，证明是环境级而非单命令问题。逐字错误与复现命令清单见 [execution-blocker-evidence.json](execution-blocked/execution-blocker-evidence.json)。
- **影响**：AC1–AC6 无法建立真实 Tauri/WebView2 运行，按冻结 Task 诚实性规则记 `BLOCKED`；AC7 无逐场景证据可裁决，记 `NOT_RUN`。固定 EXE 与 run-r1 目录未被触碰（run-r1 保持 0 items）。
- **禁止的替代路径（未使用）**：外部浏览器、Vite、JSDOM、fake timer、静态模型、仅截图 —— 均被冻结 Task 排除为 WebView2 证据；`mcp__node_repl__js` 的工具契约禁止通用执行用途，不作为通道。
- **建议处置**：由 Codex 判定故障面（ZCode CLI 会话权限模式 vs 派发侧配置），以允许 spawn 的会话重派本 Task 或由授权 harness 直接执行已交付驱动；无需改 AC/范围/DAG。

## 交付物（供恢复使用，非 finding）

- `apps/desktop/frontend/e2e/p02-new-time/`：AC1–AC6 全套零依赖驱动（README 说明逐脚本运行方式、mock 面标注与隔离断言）。
- `verification/P02-NEW-TIME-X6-AC1-AC7/execution-blocked/execution-blocker-evidence.json`：阻塞复现证据。
- 固定对象核验（本轮完成，只读）：EXE SHA-256=`92AC7B8EFB646FE77DF8245B13C9AF9314BEF415B2F0E007B1CDCEA729BC13FD`、9,367,040 bytes，与 Build/Cargo 冻结 pin 一致（`sha256sum` 复算，输出已存证于 blocker-evidence control probe）。

## 历史保留（本轮未触碰）

旧 H1 / P2-1 结论与 13 项历史原始来源缺失记录保持原样。Build/Cargo BC-AC5=`PARTIAL` 及其 residual 继续保留，不因本 Task 状态变化被称 PASS 或清除。
