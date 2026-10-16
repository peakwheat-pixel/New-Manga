---
task_id: HOST-ISSUER-1
title: Tauri host 引用签发能力（ImportSourceRef / ExportTargetRef 的 issuer 与受信注入）
reviewer: dsh（项目权威 Reviewer，`.orchestrator/tasks/HOST-ISSUER-1-role.json`；role_exclusion 已排除 owner=codex）
owner: codex
base_commit: 8a990a345c91b4e36cc0bfc6549104b454b24556
declared_delivery_head: 2ad590a31ac2271db7de45f349d94eeaa494775c
reviewed_head: deb2dfc0b863e75aa0fcb0f843127947031d6865
review_worktree: G:/CODEX/New Manga.workspace/worktrees/HOST-ISSUER-1
date: 2026-10-16
mode: 只读审查 + 独立 Git/实现/构建与测试日志复核；未修改被审分支或主仓任何文件
object_binding: VERIFIED
severity: Tauri/Rust 侧签发能力（第三次尝试，前两次均被正确阻塞后解阻）
decision: approved
---

# HOST-ISSUER-1 独立 Review（R1）

## 0. 复核结果（未采信自述）

| 项 | 方式 | 结果 |
|---|---|---|
| 变更范围 | `git diff --name-only 8a990a34..HEAD` | **27 个路径，全部在授权范围** |
| **未碰 Python Core** | 过滤 `^src/`、`^tests/` | **空** ✅（Core 侧属 HOST-CORE-1） |
| **未碰 React/WebView** | 过滤 `^apps/desktop/src/` | **空** ✅ |
| **未碰冻结契约** | 过滤 `doc/contracts/` | **空** ✅ |
| worktree / 主仓 | `git status` | worktree **clean**；主仓 **19 项 dirty 未变** |
| **HostControl 是否被暴露为 Tauri 命令**（关键安全点） | 在 `*.rs` 中检索 `#[tauri::command]` 与 HostControl 命令名的共现 | **无命中** ✅ —— HostControl 保持内部 stdio |
| 构建 | 读原始日志 | `cargo build --locked` **EXIT_CODE=0** |
| host 定向单测 | 读原始日志 | **12 passed / 0 failed**，EXIT_CODE=0 |
| 完整 Rust suite | 读原始日志 | **76 passed / 0 failed / 1 ignored**，EXIT_CODE=0 |

## 1. AC 逐项结论

| AC | 判定 | 依据（抽查） |
|---|---|---|
| AC1 导入来源签发 | **接受** | 原生文件/文件夹 picker、直接子项与 PDF scope、签名与 ref 单测 |
| AC2 导出目标签发 | **接受** | 原生保存 picker、单目标签发、冻结格式与签名向量 |
| AC3 session 与 credential | **接受** | `OsRng` 生成 **32-byte** credential 与 HMAC key；`signing_key: &[u8; 32]`；双 session 绑定；正常 drop 发送 `CloseHostSession`，Core 侧撤销 grants；进程重启产生新 session/key |
| **AC4 受信注入、不经 WebView** | **接受（重点）** | 见 §2 |
| AC5 三拒绝码 | **接受** | Host 保留 Core 的三类 error（`HOST_ONLY_REQUIRED`/`HOST_SESSION_INVALID`/`CORE_SESSION_MISMATCH`）原始 `code/category`；Core 侧负向用例断言拒绝时 seam 未被调用 |
| **AC6 宿主同步纪律** | **接受** | 四处同步（`HOST_ISSUER_PRODUCTION_ONLY_COMMANDS` / `command_allowlist`、`generate_handler!` 字面清单、`build.rs` app-manifest、`capabilities/m2rc1-commands.json`）均在实现提交 `2ad590a3` 内；ACL 同步单测通过 |
| AC7 安全 | **接受** | HMAC/canonical 签名向量、越 scope 拒绝 + Core 零副作用证据；key/credential 仅存于 Rust session 内存，不写文件/环境变量、不进 WebView |
| AC8 构建与测试 | **接受** | 见 §0；**且方法上更优**：suite 通过 `M2RC1_SRC_ROOT` 指向**当前 Core 源码**运行，从而真实覆盖协议 2.3 的 Core，而非依赖过期 bundle |
| AC9 固定交付 | **Review 由本文件闭合；集成由 Coordinator 执行** | Task 保持 `in_review` |

## 2. AC4 的独立复核

- **capability 描述**已明确 "**HostControl remains internal to Rust stdio**"；新增的 3 个 WebView 可触发命令是
  **用户动作**（`library_import_file` / `library_import_folder` / `library_start_export`），
  **不含 ref、路径或 credential**；对应 3 个权限 `allow-library-import-file` / `allow-library-import-folder` / `allow-library-start-export`。
- **Rust 侧断言**：`host_control_operations_are_never_webview_commands`、`webview_summaries_exclude_paths_and_refs` 通过。
- **静态负向证据**：对 `apps/desktop/frontend/src` 扫描 HostControl 操作名、ref、签名、路径与 credential → **无匹配**；capabilities 对 host-only 操作名与敏感字段 → 无匹配。
- **代码层**：我在 `*.rs` 中检索 `#[tauri::command]` 与 HostControl 六个命令名的共现 → **零命中**，与 Owner 声明一致。

**结论**：受信边界在**路由层**成立（HostControl 不经 Tauri/WebView），新增的 WebView 命令只承载"用户动作"，符合 §5.7 与 §10.3/§10.4。

## 3. Findings

| id | 级别 | 内容 | 处置 |
|---|---|---|---|
| **F1** | **P3（流程，同类第 12 次）** | `delivery_head` 申报 `2ad590a3`（实现提交），实际 HEAD=`deb2dfc0`（证据 pin 提交） | closeout 冻结实际 HEAD；BL-7 再次确认 |
| **F2** | **P2（环境限制，未解）** | **packaged HostControl E2E 为 `NOT_RUN`** —— BL-11b（旧 bundle 与协议 2.3 不匹配）未重建 | 不影响本 Task 的 Rust 逻辑验收；**真实打包端到端仍不可声称**。Owner 已在 `bl11b-status.md` 如实记录 |
| **F3** | P3（依赖合规） | 新增**官方**依赖 `tauri-plugin-dialog`（锁定 `2.8.3`），用于 Rust 侧原生选择器；`dependencies.md` 记录传递依赖与安全影响，**未**为其添加 WebView capability permission | 符合"官方插件 + 单列理由"的授权条件；**接受** |
| **F4** | P3（自身维护） | Owner 指出 `doc/STATUS.md` 仍有历史 `blocked` 指针 | Coordinator 已在 closeout 同步为 `done`（本 Review 后执行） |
| F5 | P4 | 完整套件 1 项 ignored 为既有性能探针（需显式运行） | 既有行为，非本次引入 |

**无 P0/P1 finding。**

## 4. 值得记录的方法亮点

Owner 面对 **BL-11b**（旧 bundle 与协议 2.3 不匹配导致的 6 项 sidecar 集成失败）时，
**没有**把它当作本 Task 的失败，也**没有**伪造打包验证，而是把完整 Rust suite 的 Core 源根
显式指向**当前 worktree 的 Core 源码**（`M2RC1_SRC_ROOT`），从而真实覆盖协议 2.3 并与实现联调，
**同时**如实声明"packaged HostControl E2E 未运行、六项既有失败仍属 BL-11b"。
这是**既推进验收又不越界声称**的正确处理，与 Coordinator 在 AC8 中设定的口径一致。

## 5. 条件

- **C1**：Coordinator 集成时冻结实际被审 head `deb2dfc0b863e75aa0fcb0f843127947031d6865`。
- **C2**：**不得**据本 Task 声称"打包产品端到端可用"；该结论需在 **BL-11b 解决后**（重建 sidecar 并跑 packaged E2E）单独取得。
- **C3**：`HOST-ISSUER-1` 可标 `done`（AC1–AC9 闭合 + 本 Review + 集成）；F2 的打包 E2E 作为**独立登记项**保留。
- **C4**：新增的 3 个 WebView 用户动作命令将成为 **P12/P17** 的对接面；其 UI 接线属后续 UI Task，不在本 Task 范围。
- 实现本身无需返修。

## 6. 能力边界

- 本 Review 覆盖范围合规、HostControl 的 WebView 隔离、key/credential 内存态、宿主同步纪律与构建/测试证据；
  **未重跑** cargo 命令（原始日志已核验 exit 0），**未做**打包端到端。
- 所有 Git / 代码 / 日志结论均由 Reviewer 在 live 环境实际执行。
- Reviewer 未修改被审分支、主仓或任何证据文件；未 push。
