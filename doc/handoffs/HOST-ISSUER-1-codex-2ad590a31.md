---
task_id: HOST-ISSUER-1
author: Codex
recipient: DeepSeek Harness
base_commit: 8a990a345c91b4e36cc0bfc6549104b454b24556
delivery_head: 2ad590a31ac2271db7de45f349d94eeaa494775c
status: in_review
---

# Handoff：HOST-ISSUER-1

## 交付结果

实现提交：`2ad590a31ac2271db7de45f349d94eeaa494775c`；branch=`codex/HOST-ISSUER-1-tauri-ref-issuer`；worktree=`G:/CODEX/New Manga.workspace/worktrees/HOST-ISSUER-1`。

Rust `StdioLibraryChannel` 直接持有 `bootstrap.core_service` 子进程，并在其 stdio 上用独立 `channel: "host-control"` envelope 实现 `OpenHostSession`、`RegisterImportSource`、`RevokeImportSource`、`RegisterExportTarget`、`RevokeExportTarget`、`CloseHostSession`。普通 Core request 已升至 protocol 2.3。Host session credential 和 HMAC key 在 Rust session 内存态生成并保存；已认证 envelope 绑定 `host_session_id`、`core_session_id` 与 credential。HostControl 不经过 `core_bridge` resource sidecar，也不暴露为 WebView command。

OS 原生 picker 提供单文件、直接子项文件夹与单目标保存入口。Ref/path 只在 Rust host 与 Core child 之间流动；WebView 命令只接收请求元数据并返回无路径/ref 的摘要。ref 字段、签名输入、过期和 `REF_*` consumer semantics 沿用冻结契约与既有 Core seam。

实现改动范围：`apps/desktop/src-tauri/**` 与 `verification/HOST-ISSUER-1/**`。Task/Handoff 文档记录在后续文档提交；没有改冻结契约、Python Core 或 React/WebView 源码。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1/AC2 issuer 与 wire | `cargo test --locked --manifest-path apps/desktop/src-tauri/Cargo.toml host_` | Windows PowerShell；H1=`2ad590a31...` | PASS：12 passed；目录直接子项、ref 形状、HMAC vectors、export expiry/token tests 通过；HostControl packaged E2E `NOT_RUN` | `verification/HOST-ISSUER-1/cargo-test-host-unit.txt`、`ac7-key-and-ref-security.md` |
| AC3 session/key | 同上；核对 open envelope 双 session 测试 | H1 | PASS：CSPRNG credential 格式、HostControl envelope 与 Core/host session 绑定断言通过；key 不持久化 | `cargo-test-host-unit.txt`、`ac7-key-and-ref-security.md` |
| AC4 WebView 隔离 | `rg -n -i <sensitive-pattern> apps/desktop/frontend/src` 与 capability scan | H1 | PASS：两次扫描均 exit `1`（无匹配）；summary DTO 与 host-only command Rust 断言通过 | `verification/HOST-ISSUER-1/ac4-webview-negative.md` |
| AC5 拒绝码 | `host_control_denial_codes_are_preserved_for_host_handling`；HOST-CORE-1 source evidence | H1 + HOST-CORE-1 base pin | PASS：三拒绝码原样保留；Core 对三类拒绝逐例断言 seam 未调用 | `verification/HOST-ISSUER-1/ac5-host-denials.md` |
| AC6 四面同步 | `cargo test --locked --manifest-path apps/desktop/src-tauri/Cargo.toml app_acl_manifest_is_generated_and_enforced` | H1 | PASS：1 passed；`command_allowlist`、`generate_handler!`、`build.rs`、capability 同步新增三个安全用户动作 | `cargo-test-acl-sync.txt`、`build.rs`、`main.rs`、capability |
| AC7 key/scope/no side effects | host HMAC/canonical vectors + P09-FU2/P16 Core rejection evidence | H1 + source pins | PASS：不可伪造签名与越 scope Core 拒绝证据对齐；HostControl packaged E2E `NOT_RUN` | `verification/HOST-ISSUER-1/ac7-key-and-ref-security.md` |
| AC8 build | `C:\Users\49745\.cargo\bin\cargo.exe build --locked --manifest-path apps/desktop/src-tauri/Cargo.toml` | Windows PowerShell；pre-existing junction build prerequisites；H1 | PASS，exit `0` | `verification/HOST-ISSUER-1/cargo-build-locked.txt` |
| AC8 Cargo suite | `cargo test --locked --manifest-path apps/desktop/src-tauri/Cargo.toml` | Windows PowerShell；Python 3.12.3 `T1.1.1-impl-py312`；`M2RC1_SRC_ROOT` 指向当前 worktree `src`；H1 | PASS：76 passed / 0 failed / 1 ignored；exit `0`。唯一 ignored 是既有显式性能探针 `perf_chunk_request_digest_cost` | `verification/HOST-ISSUER-1/cargo-test-full-python312.txt`、`bl11b-status.md` |
| AC9 固定交付 | `git rev-parse HEAD`、`git status --porcelain`、范围 diff | branch/worktree 如上 | PASS：实现 head 固定；Task 状态 `in_review`；Review/Coordinator integration `NOT_RUN` | 本 Handoff、`doc/tasks/HOST-ISSUER-1.md`、最终 Git 记录 |

**BL-11b 口径：**治理基线记录旧 bundle 配置下 `58 passed / 6 failed / 1 ignored`，主仓对照相同；六项真实打包 sidecar 失败为协议版本债务。本次正确 task Python + 当前源码测试跑法得到上表结果，未重建旧 bundle，故没有复现或关闭 BL-11b，也不声称 HostControl packaged E2E 已可用。当前完整日志与基线差异见 `verification/HOST-ISSUER-1/bl11b-status.md`。

## 接收方式

- 仓库/worktree：`G:/CODEX/New Manga.workspace/worktrees/HOST-ISSUER-1`
- branch：`codex/HOST-ISSUER-1-tauri-ref-issuer`
- base：`8a990a345c91b4e36cc0bfc6549104b454b24556`
- reviewed head：`2ad590a31ac2271db7de45f349d94eeaa494775c`
- 实现 review 应读完整 `base..head` diff、Task AC、`M2-C1_TYPED_IPC_CONTRACT.md` §5.7/§10.3/§10.4/§12、HOST-CORE-1 denial/session evidence、P09-FU2 与 P16 consumer evidence。
- 可复核命令：`cargo build --locked --manifest-path apps/desktop/src-tauri/Cargo.toml`、`cargo test --locked --manifest-path apps/desktop/src-tauri/Cargo.toml host_`、`cargo test --locked --manifest-path apps/desktop/src-tauri/Cargo.toml app_acl_manifest_is_generated_and_enforced`。Full suite 使用 `G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe` 并设置 `M2RC1_SRC_ROOT`。
- 构建依赖已由 Coordinator 提供的 gitignored junction 满足；这只是 build prerequisite，不代表 bundle 与 Core 2.3 源码匹配。

## 下一任务建议（必填）

- Task ID / 标题：`HOST-ISSUER-1` 独立 Review 与返修（若有）。
- 推荐 Agent / Reviewer：DeepSeek Harness；Owner 仍为 Codex，二者不同。
- 推荐原因与前置依赖：实现 head 与 Rust 证据已固定；HOST-CORE-1、C1、P09-FU2、P16 均已集成，可独立检查 wire 对接、安全边界、ACL 和测试口径。
- Recovery point：仓库 `G:/CODEX/New Manga`；branch=`codex/HOST-ISSUER-1-tauri-ref-issuer`；worktree=`G:/CODEX/New Manga.workspace/worktrees/HOST-ISSUER-1`；base=`8a990a345c91b4e36cc0bfc6549104b454b24556`；reviewed head=`2ad590a31ac2271db7de45f349d94eeaa494775c`；Reviewer 独立 worktree：待 Codex 创建。
- 允许修改路径：Reviewer 仅新增 `verification/HOST-ISSUER-1/review-2ad590a31.md`；不得修改实现。
- 禁止范围与新增授权条件：不得改 `doc/contracts/**`、`src/**`、`apps/desktop/frontend/src/**`，不得新增 WebView HostControl command、不得 push/merge；返修须由 Owner 在本 Task worktree 新提交并生成新 Handoff/head。
- 交付物：固定 base/head 的 Architecture + Verification Review；逐项覆盖 AC1–AC7、P0/P1 与测试边界；任何 blocker/finding 给复现命令与源码位置。
- 验证命令、环境与完成 Gate：Review 至少复核 build log、12 个 focused Rust tests、ACL manifest test、WebView/三拒绝码/签名证据；必要时使用记录的 Python 3.12.3 env 复跑 full suite，并列明唯一 ignored 项与 BL-11b 限制。Reviewer 报告需绑定固定 head；未完成 Review 不得将 Task 标为 approved/done。
- 可直接转发给 Agent 的指令：请在独立只读 worktree 审查 `G:/CODEX/New Manga.workspace/worktrees/HOST-ISSUER-1` 的 `codex/HOST-ISSUER-1-tauri-ref-issuer`，固定 base=`8a990a345c91b4e36cc0bfc6549104b454b24556` 与 reviewed head=`2ad590a31ac2271db7de45f349d94eeaa494775c`。逐项检查 HOST-ISSUER-1 AC1–AC7、完整 Rust diff、`M2-C1` §5.7/§10.3/§10.4/§12、HOST-CORE-1 Core 接收端和 P09-FU2/P16 consumer tests。只在 `verification/HOST-ISSUER-1/review-2ad590a31.md` 交付 Architecture + Verification Review；不得修改实现、契约、Python Core 或 WebView，也不得 merge/push。复核 build、host focused tests、ACL test 与现有 WebView/拒绝码/签名证据；说明 packaged HostControl E2E `NOT_RUN` 和 BL-11b，不得冒称端到端可用。

## 风险与遗留

- BL-11b：打包 sidecar 仍是过期版本；需要独立重建 bundle 后再做 packaged HostControl E2E。
- Rust host 自身尚无六个 HostControl 操作的 live packaged integration test；当前 HostControl 互操作证据由 Rust unit vectors、Core HOST-CORE-1 测试和 frozen wire 对接检查构成。
- 新增官方 `tauri-plugin-dialog`，锁定版本与安全影响见 `verification/HOST-ISSUER-1/dependencies.md`；未添加 JS plugin permission。
- `doc/STATUS.md` 不在本 Task 的改动范围；主仓现有状态指针需由 Coordinator 在后续集成时同步。
- 未触碰用户数据，未修改主仓，未 push、未 merge。
