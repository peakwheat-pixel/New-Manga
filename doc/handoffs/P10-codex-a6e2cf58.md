---
task_id: P10
author: Codex
recipient: Coordinator（建议独立 Reviewer：DeepSeek Harness；待路由）
base_commit: 2f4144b4ae53220e768071ee5e2a53a42fd990d0
delivery_head: a6e2cf58f85c6614fa349161bcd6f62388ffe792
status: in_progress
---

# Handoff：P10

## 交付结果

- 唯一权威契约：[P10_CREDENTIAL_CONFIG_CONTRACT.md](../contracts/P10_CREDENTIAL_CONFIG_CONTRACT.md)。
- Task 记录：[P10.md](../tasks/P10.md)。
- 交付 commit：`a6e2cf58f85c6614fa349161bcd6f62388ffe792`；仅新增契约文件。Task 证据与本 Handoff 在后续文档提交中追加。
- 当前 Owner=Codex；Task 保持 `in_progress`。AC1–AC5 已完成契约与静态核验；AC6 因非作者 Reviewer 尚未路由、且本次禁止 merge，保持 `NOT_RUN`。
- 基线矛盾：Task 原 `base_commit=9aa4ff4b163107dea00d95337f0a10d7a616dec3`，但用户固定坐标与本 worktree 实测 HEAD 都是 `2f4144b4ae53220e768071ee5e2a53a42fd990d0`。Task 已记录并更新为实际固定基线。

### 契约要点

1. `CredentialRef` 是不透明引用；普通配置和 Run Snapshot 只持有引用，受保护 Credential Manager 持有持久凭据，Host/Core transport 仅在单次请求期间接触短期明文。
2. 创建/替换先写受保护存储、成功后才切换引用；旧 Snapshot 继续使用原引用，明确清除则立即撤销并使后续解析安全失败。
3. Secret **MUST NOT** 进入普通 settings DTO、SQLite 明文、日志、错误、摘要或诊断包；不得回显已保存 Secret。
4. Credential Manager 被定义为逻辑端口；具体凭据后端和加密方案未在 P10 擅自选择，须在 runtime 适配器实现前另行确定。
5. Proxy 失败 **不得静默 Direct**；只有 `allow_proxy_failure_direct_fallback = true` 才允许直连，且结果与 Audit 必须可见。
6. Provider 选择、设置继承、Run Snapshot、TLS 确认、连接测试各阶段、超时/Retry 与 P15/Core/Host 职责均有条款和真实来源映射。

### AC 状态

| AC | 状态 | 证据 |
|---|---|---|
| AC1 | 完成 | 契约 §2；来源 grep 锚点见下表；Canonical Evidence 在 `doc/tasks/P10.md` |
| AC2 | 完成（契约） | 契约 §3–§4、§7–§8；Credential Manager/SQLite/日志实测 `NOT_RUN` |
| AC3 | 完成（契约） | 契约 §5–§7；Proxy/连接 runtime 验证 `NOT_RUN` |
| AC4 | 完成（只读对照） | 契约 §10；8 个 settings 文件 SOURCE_PIN 见 `doc/tasks/P10.md` |
| AC5 | 完成（验证计划与静态核验） | 契约 §11；Credential Manager、日志脱敏、UI 与 E2E `NOT_RUN` |
| AC6 | NOT_RUN | 未有非作者 Review；本次硬约束禁止 merge；见 `doc/tasks/P10.md` |

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| D04 来源锚点 | `rg -n '^#{1,4} (38|39|40|41|41\.1|41\.2|41\.3|41\.4|42)[ .：]' doc/04_USER_FLOW.md` | PowerShell；源文件来自 base `2f4144b4...` | exit 0；§38–§42 命中行 1482、1505、1538、1562、1564、1575、1585、1597、1621 | `doc/tasks/P10.md` Canonical Evidence |
| D08 来源锚点 | `rg -n '^# (33|34|35|36|59)\.|^## AC-PROVIDER-00[1-4]|^## AC-FALLBACK-00[12]|^## AC-NET-00[1-4]|^## AC-SEC-00[1-5]|^## AC-SET-' doc/08_ACCEPTANCE_CRITERIA.md` | PowerShell；base `2f4144b4...` | exit 0；§33 行1705及 AC 行1707/1721/1727/1737；§34 行1748及 AC 行1750/1762；§35 行1780及 AC 行1782/1798/1810/1824；§36 行1840及 AC 行1842/1855/1863/1875/1885；§59 行2667 | `doc/tasks/P10.md` Canonical Evidence |
| D08 §59 编号核对 | `rg -n '^## AC-SET-' doc/08_ACCEPTANCE_CRITERIA.md` | PowerShell；base `2f4144b4...` | exit 1、无输出（预期）；§59 仅章节引用，无编号 AC | 同上 |
| D07 来源锚点 | `rg -n '^# (57|58|60|63|64|67|105)\.' doc/07_NON_FUNCTIONAL_REQUIREMENTS.md` | PowerShell；base `2f4144b4...` | exit 0；行1494、1516、1560、1632、1655、1722、2595 | `doc/tasks/P10.md` Canonical Evidence |
| P08 来源锚点 | `rg -n 'Provider/凭据/网络/设置|\| P10 \|' verification/P08/SCOPE_DRAFT.md` | PowerShell；base `2f4144b4...` | exit 0；第37、76行 | `doc/tasks/P10.md` Canonical Evidence |
| 契约静态完整性 | PowerShell 对 36 个来源/条款必需字符串执行 `Contains` 断言 | 工作区 contract；delivery head `a6e2cf58...` | `PASS contract static assertions: 36 required anchors/clauses present` | 契约 §2–§11 |
| 实现现状对照 | 对 `bindings.py`、`models.py`、`network.py`、`privacy.py`、`resolution.py`、`snapshots.py`、`pipeline_defaults.py`、`errors.py` 执行 `rg -n` 并阅读符号实现；另查 `CredentialRef|CredentialManager|CredentialStore|credential_ref|resolve_credential|CredentialLease` | 仓库只读；base `2f4144b4...` | 已有 Provider/Network/Settings/Snapshot 符号可复用；凭据存储与 exchange 检索无命中（exit 1） | 契约 §10；`doc/tasks/P10.md` SOURCE_PIN |
| Hash 与树对象核对 | `Get-FileHash -LiteralPath <path> -Algorithm SHA256`；`git cat-file -e <commit>:<path>` | Windows PowerShell；当前工作区 CRLF；source commit=`2f4144b4...`，contract commit=`a6e2cf58...` | SOURCE_PIN 全部为 64 位 SHA-256 且树对象存在；CANONICAL contract hash 见 Task 表 | `doc/tasks/P10.md` Canonical Evidence |
| runtime、安全实测、UI/E2E | 未执行 | 本 Task 为契约设计；实现与实测交后续 Task | `NOT_RUN` | 契约 §11 |

## 接收方式

- 仓库：共享 Git 仓库 `G:/CODEX/New Manga`；当前 linked worktree=`G:/CODEX/New Manga.workspace/worktrees/P10-CREDENTIAL-CONFIG-CONTRACT`。
- 分支：`codex/P10-credential-config-contract`；base=`2f4144b4ae53220e768071ee5e2a53a42fd990d0`；契约 delivery head=`a6e2cf58f85c6614fa349161bcd6f62388ffe792`。
- 本 Task 写入仅限契约、`doc/tasks/P10.md` 与本 Handoff；没有 runtime、Schema 或依赖变更。
- 没有执行 push、merge、rebase、reset、stash、删除文件或 worktree；主仓工作树没有被本次命令写入。最终两个 `git status` 原始输出由交付答复提供。
- 受三路径写入白名单限制，`doc/STATUS.md` / `doc/REBASELINE_PLAN.md` 未改；它们仍把 P10 记为 `ready`、Owner/Reviewer 待路由。本 Task/Handoff 只记录本轮用户指派后的 Task-local `in_progress`，Coordinator 后续需同步权威指针。
- 下游必须保持 runtime、真实凭据读写、日志脱敏与 UI 验收 `NOT_RUN`，直到有对应实现与证据。

## 下一任务建议

- Task ID / 标题：P10 非作者 Review 与 AC6 收口（沿用现有 P10，不创建新产品范围）。
- 推荐 Agent / Reviewer：推荐 DeepSeek Harness 做非作者 Review；P10 路由文件/脚本未提供，须先由 Coordinator 完成正式路由。Codex 作为 Owner 不得 Review 自己的变更。
- 推荐原因与前置依赖：AC1–AC5 已交付，AC6 只待固定 head 独立 Review 与后续 Coordinator 集成。
- Recovery point：当前 worktree / branch 如上；固定 base=`2f4144b4ae53220e768071ee5e2a53a42fd990d0`，交付 head=`a6e2cf58f85c6614fa349161bcd6f62388ffe792`。Review 前先核对 `git rev-parse HEAD` 与 Task 的 `delivery_head`，不得改写该 head。
- 允许修改路径：Review 证据应依 P10 Task 的 `verification/P10/**` 与 Handoff 规则另行授权；本次执行写入白名单不扩大。
- 禁止范围与新增授权条件：不修改 `src/**`、`apps/**`、`packaging/**`、`tests/**`、Schema、D04/D07/D08；不选择凭据存储后端/加密方案；不 push/merge。
- 交付物：固定 head 的 Review 报告，AC/Finding 逐项状态；Coordinator 后续确认集成授权后才能集成。
- 验证命令、环境与完成 Gate：`git rev-parse HEAD`、`git status --porcelain`、本 Task Canonical Evidence 的 SHA/cat-file 校验；Review、集成与集成后验证完成前，P10 不得标 `done`。
- 可直接转发给 Reviewer 的指令：请在只读独立工作区审查 `a6e2cf58f85c6614fa349161bcd6f62388ffe792`，按 P10 AC1–AC6 核验真实来源、Secret 边界、Provider/Network 回退语义及八个只读实现对照。只写经路由授权的 Review 证据，不改 runtime、需求、Schema 或依赖；未实测的 Credential Manager、SQLite、日志脱敏、TLS/网络端点、UI/E2E 继续标 `NOT_RUN`；不得 merge/push。

## 风险与遗留

- 非作者 Reviewer 未路由、Review 未执行、Coordinator 集成未执行，AC6=`NOT_RUN`；本交付不得标成 `done`。
- `doc/STATUS.md` 与本 Task 的 task-local owner/status 暂不一致；需 Coordinator 后续按治理流程同步。
- Credential Store 具体平台后端和加密方案未选择。本契约对此保持后端无关，未替用户作产品选择；该选择须在 runtime Credential Manager 适配实现前另行确定。
- SQLite、日志/诊断脱敏、凭据生命周期、TLS/Proxy transport、真实 Provider Auth、UI/E2E 都未运行验证。
- `verification/P10/resource-manifest.json` 未创建，因为本次授权的写入路径只有三项；没有删除、移动或归档资源，worktree 保留。
- `git commit` 创建 delivery head 时，共享 Git 仓库自动 GC/repack 输出一个既有坏 checkpoint ref 错误；目标 commit 已成功创建并通过 `git cat-file -e`，没有修改或删除该 ref。
- 主仓 `G:/CODEX/New Manga` 零文件写入；未 push。
