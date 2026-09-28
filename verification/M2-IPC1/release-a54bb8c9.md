# M2-IPC1 Release Record

- **Decision:** 用户批准释放（2026-09-28；"释放 M2-IPC1"，指向上轮汇报的建议分工 Owner=Antigravity、Reviewer=DeepSeek Harness、Integrator=Codex 代行）。
- **Task / state:** [`M2-IPC1`](../../doc/tasks/M2-IPC1.md), `ready / M2_IPC1_PRODUCTION_CORE_LIBRARY_RELEASED`。
- **Owner / Reviewer / Integrator:** Antigravity / DeepSeek Harness（非作者）/ Codex（代行=ZCode 会话，用户全权授权 2026-09-28）。
- **Dependency:** M2-P1=`done`（`a174fb9c`）、M2-RC2=`done`（`88f972fe`）、M2-AC1=`done`（`f162193b`）；[Contract 1.1](../../doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md) blob 不变。
- **Fixed base (code freeze point):** `a54bb8c92faefa90f4077e7ac2bb000f6b6712fd`。
- **Branch:** `agent/antigravity/M2-IPC1-production-core-library`。
- **Worktree:** `G:/CODEX/New Manga.worktrees/M2-IPC1-agy`（从 release commit 检出）。
- **Dispatch:** `AWAITING_DISPATCH`。

## Production IPC seam 冻结（Codex 代行架构裁决 2026-09-28）

Contract 1.1 §12 将 serialization / Tauri command names / process supervision / handshake 留给 runtime Task。本释放冻结如下（Task 文件 §Seam 冻结 为权威全文，此处为摘要；实现偏离即违宪）：

1. **Transport**：stdio JSON-lines sidecar，与既有 `core_bridge.rs` / `ac1_bridge.rs` 同构；串行请求；`request_id` 仅关联。
2. **Envelope**：Contract §3 形状（`protocol:"new-manga.core"`、`version:{1,0}`）；major 拒绝 → `PROTOCOL_VERSION_UNSUPPORTED`；未知命令 → `UNKNOWN_COMMAND`；`result`/`error` 互斥。
3. **命令面（仅三条）**：`core.ping`（握手：装配完成后即 ready；§7.2.1 事件以 ping 替代）、`ListBooks`（只读，DTO 字段冻结、无 OS 路径）、`core.shutdown`（exit 0；host wait 5s→kill）。
4. **生命周期**：spawn `<python> -m bootstrap.core_service`（解释器定位沿用既有机制）；EOF/非零退出 → `CORE_UNAVAILABLE`（unavailable/retryable=true）；**不自动重启**（自动监督登记后续 Task）；启动即执行既有装配与恢复。
5. **安全**：T5 分层信任——WebView 永不接触 OS 路径；错误按 §8 envelope；traceback 不出 Core。
6. **Command surface**：production invoke 命名冻结 `core_ping` / `library_list_books`；三视图（constants / `generate_handler!` / build.rs manifest+capabilities）同一 commit 同步（F-008 机制）；probe/ac1 面零变化。

## Release Gate

| Required field | Frozen evidence |
|---|---|
| Base | `a54bb8c92faefa90f4077e7ac2bb000f6b6712fd`（代码面与 release commit 零差异，release 仅治理文档） |
| Branch / worktree | 已固定于 Task frontmatter |
| Allowed paths | Task §允许修改范围（bootstrap core_service + tests、Rust bridge/命令面三视图、frontend library 模块、Task/Handoff/verification） |
| Forbidden paths | Task §禁止范围（写入类命令、Contract、既有两桥语义、Schema、自动监督、打包、Legacy QML） |
| Acceptance Criteria | AC1–AC5 已冻结（AC4=真实进程链判别） |
| Verification commands | pytest / cargo test / npm test / `git diff --check` 已冻结 |

释放前主线为 `main@a54bb8c9`，无 Active Task。本 Task 是 M2 主线第一个打通 production React → Tauri → Python Core → SQLite 的竖切；写入类命令与事件通道仍属后续 Task。
