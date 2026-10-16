# P15-C1 独立 Review（R1，Coordinator 路由的 Reviewer=dsh）

| 项 | 值 |
|---|---|
| Task | P15-C1（设置面 IPC 契约修订；解 G21–G24 + 部分 G25；**P15 前置**） |
| Owner | Codex |
| Reviewer | **dsh**（本会话，`route-agent.py` 路由；Owner 已机器排除） |
| 交付 | 契约 `8d083ee186ee23b86c4db948f32df12d7120939d`；HEAD `9c0200e88`（Handoff/证据） |
| 基线 | `f2cb340a6` |
| 复核环境 | 独立 Reviewer 工作树 `worktrees/P15-C1-review`（detached `8d083ee18`） |
| 结论 | **approved** |

## 1. 逐项独立验证

| # | 验证项 | 方法 | 结果 |
|---|---|---|---|
| V1 | 范围（**零产品代码**） | `git diff --name-only f2cb340a6..HEAD` | **PASS**：仅 `doc/contracts/P15_SETTINGS_IPC_CONTRACT.md`、`doc/handoffs/P15-C1-8d083ee.md`、`doc/tasks/P15-C1.md`、`verification/P15-C1/checkpoint-*.md`；**未触碰** `apps/**`、`src/**`、`tests/**`、Schema、依赖 |
| V2 | **未重开 P10 语义** | 读 §1/§4 | **PASS**：明写"**不改写其逻辑边界**"、"补充消费 P10 契约"；凭据存储"沿用 P10 §3/§4，不在此选择 OS 后端或加密实现"；仅**新增** wire |
| V3 | **G21 Provider 面** | 读 §3 | **PASS**：Profile CRUD + **多 Profile 同 Provider 由独立 `profile_id` 表达**；Capability 绑定持久范围 `global/book/chapter` + Run 临时范围仅经 `StartRun.overrides.provider_profiles`；解析顺序**任务→章节→作品→全局**且**缺失/禁用不隐式回退**；Run Snapshot 为**创建时冻结值的只读安全投影**，编辑配置不改既有 Snapshot；`endpoint` 要求 absolute HTTP(S) 且**禁 userinfo/query/fragment** |
| V4 | **G22 凭据面（安全红线）** | 读 §4 | **PASS**。WebView 只能调用**无 Secret** 的 production-only 命令（`PutCredential`/`ClearCredential`）；`create`/`replace` 状态机 + 不匹配返 `conflict` 且保留原绑定；**Secret 不入 React/WebView 内存、invoke payload、Core settings DTO、日志、事件或任何错误**；`CredentialRef` **仅在受信 Host↔Core exchange 与 Core 持久配置**，**不注册为 WebView 可调用**、**不经 allowlist 转发**、**不扩展 M2-C1 §5.7 `HostControl`**；写入原子性（**先新引用再切换**，失败保留旧绑定）；清除即撤销且后续 Run 解析按 P10 §7 失败而**不换用其他 Credential/Provider**；**禁止复用 `settings_update_section`** |
| V5 | **G23 Network 面** | 读 §5 | **PASS**：六阶段测试（Proxy→DNS→TCP→TLS→HTTP→Provider Auth）；**未执行阶段标记**、**失败保留阶段**；**`allow_proxy_failure_direct_fallback` 默认 false**（不静默直连）；**`verify_tls` 默认 true 且关闭需 `confirm_disable_tls_verification: true`** |
| V6 | **G24 覆盖解析** | 读 §6 | **PASS**：**只读**返回最终有效值 + 来源标注（全局→作品→章节→任务） |
| V7 | **G25 受限（我裁决的核心）** | 读 §7 | **PASS**。开放表 **4 行**（Provider / Capability 绑定 / Network / SFX），每行均给出**精确键集 + 值域 + 依据来源 + Core/Host 验证方式**；明写"`settings_update_section` 既有语义保持 M2-C1 §5.3 不变"、**未知节/未知键/表外值域一律 UI 禁用**；**禁用表 11 行**（OCR、翻译/上下文、修复、排版、模型/GPU、任务/并发、缓存/Revision、回收站、备份/恢复、Plugin/Hooks、阅读方向）各附依据与**逐节契约 Task 建议**；SFX 行**引用真实 Core 源码与 3 个测试文件**作为可复核依据 |
| V8 | **G2 未开放** | 读 §8 | **PASS**：明确未授权，且**禁止**经 G25 或通用 `settings_update_section` 透传开放 |
| V9 | **Secret/路径四处边界** | 读 §9 | **PASS**：**封闭**的 `SettingsSurfaceError`（固定 category/phase/action/message_key，**不透传底层 `details`/异常对象**）；逐项禁止 Secret、明文凭据、认证头、`CredentialRef`、原始响应、请求体、文件系统路径、Host/Session 凭据、异常文本、不透明写引用进入**请求、返回、事件、错误**任何一处 |
| V10 | 兼容性 | 读 §2 | **PASS**：`protocol = "new-manga.core"`, `version = {major: 2, minor: 6}`（**minor 5→6、major 保持 2**）；声明 probe/AC1 面不变 |
| V11 | 依据映射与验证状态 | 读 §10–§12 | **PASS**：逐节修订记录 + 依据映射（每条裁决 → 契约条文 → 来源章节）；§12 验证状态**全部 `NOT_RUN`** 并说明"设计类、无新 Core/Host handler、未运行产品测试"——**未伪造测试** |
| V12 | **证据（BL-17 强校验）** | `Get-FileHash` + **`git cat-file -e <sha>:<path>`** | **PASS**：`P15-C1-CONTRACT` 的 sha256 与磁盘**一致**、提交包含性**成立**、class=`CANONICAL`（**合规**，非 `REVIEW`——本项目刚登记 BL-19 禁止该类） |

## 2. 结论：approved

契约以**纯新增**方式冻结了 G21–G24 的 IPC wire 与 G25 的受限键域，逐条满足裁决的硬性边界：**未重开 P10**、**Secret 四处零暴露**、**G25 不越界**、**G2 明确未开放**、**兼容性按 M2-C1 §3.2 声明**、**无产品代码**、**测试如实 `NOT_RUN`**。可进入集成。

## 3. 记录性事项（closeout 处理）

1. **BL-15**：`delivery_head` 记契约提交 `8d083ee18`，而分支 HEAD 为 `9c0200e88` → closeout 以实际 HEAD 冻结。
2. **`evidence_dir` 完整性**：`verification/P15-C1/checkpoint-20261016-git-metadata-blocked.md` 目前**仅出现在正文**、**不是证据行**；治理检查器 L217 规定 `done` 时 evidence_dir 内**每个文件都需登记** → closeout 补一行 `SOURCE_PIN`。
3. **过程记录（正向）**：Owner 在共享 `.git` 写入受阻时**正确停下**、写检查点（含失败命令原文与恢复清单）、**保全草案并拒绝伪造 commit SHA**；根因是**我方派发沙箱参数过窄**（linked worktree 的 git 元数据在主仓库），已按 `codex-dispatch` 技能经 `resume` + `sandbox_mode=danger-full-access` 恢复完成。此过程**不影响**契约内容质量。
4. 待用户确认项（Owner 已在 Handoff 显式列出）：**P15 v1 是否扩大 G25 白名单**——当前保持"未开放"，扩展须用户裁决 + 逐节契约 Task（与 [decision-request-20261016.md](../PROJECT-ORCHESTRATION-20261016/decision-request-20261016.md) 第 1 项一致）。
