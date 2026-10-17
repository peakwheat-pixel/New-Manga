---
task_id: P15-HOST-2
author: Codex
recipient: Coordinator (dsh, epoch 6) / Codex（裁决后恢复）
base_commit: fb232344de986de3cb8d6f25d1988970a596861a
delivery_head: null
status: blocked
---

# Handoff：P15-HOST-2（AC1 blocker）

## 交付结果

未交付产品实现。AC1 硬门发现契约不能唯一确定 WebView 可达命令名、参数与 `PutCredential` Host 外置安全输入面的启动关系；依任务要求停止实现并请求 Coordinator 裁决。Task-local 证据：[AC1 blocker report](../../verification/P15-HOST-2/ac1-coordinator-blocker.md)。

当前检查点：branch `codex/P15-HOST-2`，worktree `G:/CODEX/New Manga.workspace/worktrees/P15-HOST-2`，检查时 HEAD=`fb232344de986de3cb8d6f25d1988970a596861a`。检查前工作树 clean。没有运行测试，也没有修改生产代码、frontend、Core、契约、Schema、依赖或四处 command surface。

### AC 状态

- **AC1：BLOCKED**。§2 L20–L27 将 Tauri 命令固定为 `credential_put` / `credential_clear`；§4.1 L109–L119 又列 `PutCredential` / `ClearCredential` 为 WebView 可调用命令，同时把 `PutCredential` 描述为 Host 提供的 WebView 外输入面。契约没有明确名称映射或输入面启动方式。
- **AC2–AC6：NOT_RUN**。没有在 AC1 未定案时实施或运行产品测试。
- **Host-only Core wire：保留原状**。§4.2 L129–L135 的 `BindProfileCredential` / `ClearProfileCredential` 仍应只经受信 Host→Core 路由，绝不进入 WebView allowlist。
- **凭据通道：当前仍不可用**。本次没有改动现有失败关闭桩，也没有声称 Credential Manager 写入或端到端绑定可用。
- **四处同步计数：未变更、未复核**。既有 P15-HOST-1 证据记录 `PRODUCTION_COMMANDS=47`、probe=7、AC1=6，且 probe/AC1 冻结；本 Task 尚未新增命令，因此本次未重跑同步检查。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 契约核对 | 对照 §2 L20–L27、§4.1 L107–L121、§4.2 L123–L139 与 Task AC1 | 当前 worktree；检查时 HEAD `fb232344de986de3cb8d6f25d1988970a596861a` | BLOCKED：两种以上解释无法排除 | `verification/P15-HOST-2/ac1-coordinator-blocker.md` |
| Rust / packaged / Core / frontend | 未运行；AC1 未定案，按 Task 停止 | — | NOT_RUN | — |
| host-only scan / surface-sync | 未运行；本轮无生产改动 | — | NOT_RUN | — |

## 接收方式

请 Coordinator 先明确 WebView invoke 名、参数/响应，以及 WebView 触发 Host-owned 安全输入面的方式。若需要修改契约，须另行授权契约修订；本 Task 当前禁止自行改契约。收到可执行裁决后由 Codex 在本 worktree 恢复实现，仍需非作者 Reviewer 独立审查。

## 下一任务建议（必填）

- Task ID / 标题：`P15-HOST-2` AC1 wire ruling，然后恢复本 Task。
- 推荐 Agent / Reviewer：Coordinator（dsh, epoch 6）给出裁决；Codex 按裁决续作；独立 Reviewer 待 Coordinator 指定，且必须非作者。
- 推荐原因与前置依赖：AC1 是硬门；命令名、参数和外置输入面的调用关系未定，当前无法安全实现。
- Recovery point：仓库 `G:/CODEX/New Manga`；branch `codex/P15-HOST-2`；worktree `G:/CODEX/New Manga.workspace/worktrees/P15-HOST-2`；起始 HEAD `fb232344de986de3cb8d6f25d1988970a596861a`；当前阻塞报告提交由分支 HEAD 提供。
- 允许修改路径：恢复后仅限 `doc/tasks/P15-HOST-2.md`、`doc/handoffs/P15-HOST-2-*.md`、`verification/P15-HOST-2/**` 与 Task 允许的 Tauri host 路径。
- 禁止范围与新增授权条件：不得在 ruling 前实施；不得修改冻结契约、`src/**`、frontend、Schema、迁移或依赖清单；不得将 `BindProfileCredential` / `ClearProfileCredential` 暴露给 WebView。
- 交付物：明确 AC1 结论的 Handoff、真实 Host Credential Manager 接线或如实失败关闭、四处 surface 同步、反例测试和逐套件原始日志/退出码。
- 验证命令、环境与完成 Gate：按原 Task 逐项执行；Rust source 显式设置 `M2RC1_PYTHON`，packaged 使用 `M2RC1_PACKAGED=1`；host-only 复扫及 surface-sync 复核归档至 `verification/P15-HOST-2/**`。通过 AC1 后才开始，不把 `NOT_RUN` 记作 PASS。
- 可直接转发给 Coordinator 的指令：请对 [AC1 blocker report](../../verification/P15-HOST-2/ac1-coordinator-blocker.md) 中 §2 与 §4.1 的矛盾作唯一、可执行的书面裁决：逐字确定 WebView Tauri command 名、请求/响应字段，并说明 Put 凭据操作由 WebView 无 Secret invoke 启动 Host 外置安全输入，还是由 Host 独立启动且 WebView 不 invoke Put。确认 §4.2 `BindProfileCredential` / `ClearProfileCredential` 永远仅 Host→Core。若契约需要修改，请另行授权契约 Task；在此之前 P15-HOST-2 保持 BLOCKED。

## 风险与遗留

- `P15-C1-FU2.md` closeout 称“命名/版本歧义已消除”，但 FU2 只修复 §4.2 的 minor 文字，没有修复 §2 与 §4.1 的 command 命名/输入面歧义。
- 没有声称端到端凭据可用：Host 当前 `bind_profile_credential` / `clear_profile_credential` 失败关闭桩仍未改。
- `delivery_head=null`；本 Handoff 是阻塞上报，不代表 AC 完成、独立 Review 或集成批准。
