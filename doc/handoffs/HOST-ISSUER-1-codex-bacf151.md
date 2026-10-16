---
task_id: HOST-ISSUER-1
author: Codex
recipient: Coordinator (dsh) / user decision
base_commit: 2eaa3241295e1f483eabf640289a4bea4126370c
delivery_head: null
status: blocked
---

# Handoff：HOST-ISSUER-1

## 交付结果

未交付 issuer 实现。Reality Check 确认现有 Tauri `StdioLibraryChannel` 可访问 Core JSON-RPC，但 P09-FU2/P16 的 `_register_*` / `_revoke_*` 只可在 live `CoreServiceServer` 进程内调用；当前 dispatcher 没有 host-only 注册通道。资源 `host_bridge` 是另一个 sidecar，不持有 Import/Export grant registry。绕过需要新增或变更 Python Core 通道，当前 Task 明确禁止修改 `src/**`，且契约 §11 将 runtime transport / auth handshake 标为 `UNKNOWN / NOT_IN_SCOPE`。

阻塞分析与 Cargo 原始日志固定于 evidence commit `bacf151b7f4fd61f5b34666b96a444ee95030874`。本 Handoff 与 Task 状态更新在后续文档提交中记录。没有 Rust、Python、React、contract、ACL 或 capability 代码变更。

| AC | 状态 | 结果 |
|---|---|---|
| AC1 | BLOCKED | 无法把签发 grant 登记到 live Core。 |
| AC2 | BLOCKED | 同一注入缺口阻止 `ExportTargetRef` 注册与受信 `StartExport`。 |
| AC3 | BLOCKED | 未生成/保存 key；session、轮换与撤销依赖缺失通道。 |
| AC4 | BLOCKED | 前端源码静态扫描为 NO_MATCHES，但无实现级负向测试可运行。 |
| AC5 | BLOCKED | 未新增 Tauri 命令/权限；未落地需要四处同步的新命令。 |
| AC6 | BLOCKED_WAITING_EXTERNAL_DECISION | 需要决定并授权 trusted host→live-Core transport；未改 wire。 |
| AC7 | BLOCKED | 既有 Core 拒绝测试不证明 host issuer 的端到端安全。 |
| AC8 | BLOCKED | build/test 均在 `build.rs` 前置检查以 exit 101 结束。 |
| AC9 | NOT_RUN | 没有实现 head；非作者 Review 与 Coordinator 集成未执行。 |

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC4 WebView 静态负向扫描 | `rg -n -e ImportSourceRef -e ExportTargetRef -e host_signature -e source_path -e target_path apps/desktop/frontend/src` | Windows PowerShell；base `2eaa3241295e1f483eabf640289a4bea4126370c` | NO_MATCHES；ripgrep exit 1（未找到是预期）。这只说明当前前端源码无匹配项，不替代实现验收。 | `verification/HOST-ISSUER-1/webview-static-scan.txt` |
| AC8 Build | `C:\Users\49745\.cargo\bin\cargo.exe build` | Windows PowerShell；`apps/desktop/src-tauri`；`2eaa3241295e1f483eabf640289a4bea4126370c` | BLOCKED；exit 101，`build.rs` 报缺少 ignored `target/core-sidecar/core-sidecar`。 | `verification/HOST-ISSUER-1/cargo-build.txt` |
| AC8 Rust tests | `C:\Users\49745\.cargo\bin\cargo.exe test` | Windows PowerShell；`apps/desktop/src-tauri`；`2eaa3241295e1f483eabf640289a4bea4126370c` | BLOCKED；exit 101；Rust tests 未启动。 | `verification/HOST-ISSUER-1/cargo-test.txt` |
| AC1–AC3/AC7 host flow | 源码/dispatcher 路由检查 | `2eaa3241295e1f483eabf640289a4bea4126370c` | BLOCKED；只找到 Core 内部私有 seam，现有 Tauri channel 无注册路由。 | `verification/HOST-ISSUER-1/blocker-assessment.md` |

专用打包 Python 环境、`apps/desktop/frontend/node_modules` 与 `dist` 不存在。未创建环境、安装依赖或构建 sidecar；因此 cargo 命令未验证 Rust 改动（本 Task 无 Rust 改动）。所有未运行项如上标注。

## 接收方式

- 分支：`codex/HOST-ISSUER-1-tauri-ref-issuer`
- worktree：`G:/CODEX/New Manga.workspace/worktrees/HOST-ISSUER-1`
- 用户指定基线：`2eaa3241295e1f483eabf640289a4bea4126370c`
- 阻塞证据 head：`bacf151b7f4fd61f5b34666b96a444ee95030874`
- 恢复前置：先裁决是否另行授权 Core 侧 trusted host-only grant registration/revocation transport，并冻结其 session binding 与 shutdown/revoke 语义；其后更新本 Task 的 allowed paths/base。
- 当前没有启动命令或可运行 issuer。

## 下一任务建议（必填）

- Task ID / 标题：待裁决后由 Codex 建立；建议主题为“Core trusted host issuer injection seam”。
- 推荐 Agent / Reviewer：Codex 负责 seam 设计与跨层契约；实现 Owner 按更新后授权指定，DeepSeek Harness 作为非作者 Reviewer。
- 推荐原因与前置依赖：HOST-ISSUER-1 的根阻塞是 Core private registries 无 live host 通道；先明确并授权 Python Core 的最小、WebView 不可调用的注册/revoke 入口。
- Recovery point：仓库 `G:/CODEX/New Manga`；本 worktree `G:/CODEX/New Manga.workspace/worktrees/HOST-ISSUER-1`；branch `codex/HOST-ISSUER-1-tauri-ref-issuer`；Task 原始基线 `2eaa3241295e1f483eabf640289a4bea4126370c`；阻塞证据 head `bacf151b7f4fd61f5b34666b96a444ee95030874`。新 Task worktree/base 待 Codex 在授权后创建/登记。
- 允许修改路径：必须由新 Task 明确冻结；若采用当前 Python Core 实例 seam，至少需评估 `src/bootstrap/core_service.py`、必要的 `src/bootstrap/core_assembly.py`、`tests/core/**` 与 Tauri Rust bridge。
- 禁止范围与新增授权条件：不得改 `doc/contracts/**`、React/WebView、SQLite Schema、已有权限强度；不得把注册命令开放给 WebView；需用户/Codex 先授权 Core 路径与 host-only transport。不得在本 Task 阻塞状态下继续实现。
- 交付物：冻结的内部 transport 与 session/auth 语义、最小 Core seam、Rust host issuer/injection、伪造/越 scope/过期/撤销/零副作用测试、WebView 负向证据、cargo 原始日志、Task 与 Handoff。
- 验证命令、环境与完成 Gate：Core 侧执行 `python -m pytest tests/core/test_p09_fu2_import_pages.py tests/core/test_p16_reader_export.py -q`；在已准备 sidecar 与 `frontend/dist` 的 Windows worktree 执行 `cargo build`、`cargo test`。须证明注册 transport 不可由 WebView 调用、错误引用在任何文件/库副作用前拒绝、Export grant 单次消费、Import scope 直接子项/只读、四处 Tauri command surface 同 commit。
- 可直接转发给 Agent 的指令：

  > 暂停 HOST-ISSUER-1 的 Rust issuer 实现，等待用户/Codex 对 Core host-only grant injection transport 作出授权。当前恢复点为 `G:/CODEX/New Manga.workspace/worktrees/HOST-ISSUER-1`、branch `codex/HOST-ISSUER-1-tauri-ref-issuer`、base `2eaa3241295e1f483eabf640289a4bea4126370c`、阻塞证据 head `bacf151b7f4fd61f5b34666b96a444ee95030874`。未收到明确的 Core 路径与 transport 授权前，不得修改 `src/**`、不得新增可被 WebView 调用的注册命令、不得扩展冻结 wire。授权后先由 Codex 更新 Task allowed paths 和 STATUS，并固定新 base/branch/worktree；交付 Core/Tauri seam、AC1–AC8 测试日志与安全证据、Canonical Evidence 表和新的 Handoff，再由非作者 Review。

## 风险与遗留

- HOST-ISSUER-1 未完成，不能供 P12/P17/P19 使用；状态为 `blocked`，不是 `done`。
- WebView 静态扫描只覆盖现有前端代码，不是对未来 Rust 命令输出或运行时行为的负向验证。
- Cargo 退出 101 的根因是缺失打包环境产物，不是 Rust 编译器错误；但当前仍没有成功的 cargo build/test 结果。
- 无新第三方依赖。无用户数据写入、无主仓文件写入、无 push/merge。
- 回退：仅需 revert 当前 Task 分支的两笔本地文档/verification 提交；未改实现代码或外部资源。
