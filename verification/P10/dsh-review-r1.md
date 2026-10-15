---
task_id: P10
title: 凭据与配置通道契约
reviewer: dsh（非作者；Owner=codex，role_exclusion 机器排除 owner，未参与 implementation/repair）
owner: codex
base_commit: 2f4144b4ae53220e768071ee5e2a53a42fd990d0
declared_delivery_head: a6e2cf58f85c6614fa349161bcd6f62388ffe792
reviewed_head: fa20602debb2d5f16f315bbed4180eae6f8821c5
review_worktree: G:/CODEX/New Manga.workspace/worktrees/P10-CREDENTIAL-CONFIG-CONTRACT
base_worktree: G:/CODEX/New Manga（用户 dirty 未被触碰）
date: 2026-10-15
mode: 只读审查 + 独立 Git/blob/SHA-256 复核 + 来源锚点与实现符号实证 + secret 边界安全检查；未修改被审分支或主仓任何文件
object_binding: VERIFIED
architecture_axis: PASS
security_axis: PASS（静态：无 secret 形态值、边界条款可判定；runtime 安全验证 NOT_RUN）
verification_axis: PASS（静态；runtime/UI 明确 NOT_RUN 并移交 P15/P19）
decision: approved_with_conditions
---

# P10 凭据与配置通道契约 — 独立 Review（R1）

## 0. 审查对象与方法

- 对象：`codex/P10-credential-config-contract`，`2f4144b4..fa20602d`（Owner=codex）。
- Reviewer 实际执行 Git、SHA-256、锚点、符号与安全检查；**未采信 Owner 自述**。

### 0.1 实际执行的复核

| 项 | 方式 | 结果 |
|---|---|---|
| 变更范围 | `git diff --name-only 2f4144b4..HEAD` | **仅 3 条授权路径**（契约、`doc/tasks/P10.md`、Handoff）；无越界 |
| worktree 洁净 | `git status --porcelain` | **空（clean）** |
| 主仓零改动 | `git status --porcelain --untracked-files=no` | **19 项，与开工前完全一致**（全部为用户既有 dirty） |
| **secret 泄漏扫描** | 对 3 份交付物正则扫描 `sk-*`/`sk-ant-*`/`AIza*`/`ghp_*`/`Bearer <len>` 及 `(api_key\|secret\|password\|token)\s*[:=]<len>` | **0 命中**；无看似可用的凭据串 |
| AC id 真实性 | 对契约引用的 15 个 AC id 在主仓 grep 章节标题 | **15/15 各自 1 次命中**（含 `AC-FALLBACK-002`） |
| AC-SET 无编号 | `rg '^## AC-SET-'` | **无输出**；确认该节只能按章节引用，契约未编造 AC id |
| 13 条 Canonical Evidence | 独立 `Get-FileHash` + `git cat-file -e <commit>:<path>` | **sha256 13/13 一致；commit 13/13 可解析** |
| §10 代码符号 | 对 8 个文件逐一 grep 契约列出的 21 个符号 | **21/21 存在** |
| §10 缺口断言 | 全 `src/**` 搜 `CredentialRef`/`CredentialManager`/`credential_ref` | 近零命中 → **"未发现凭据存储 / exchange 实现"成立** |
| 契约结构 | 标题清单 | §1 范围与强制边界、§2 需求映射、§3 CredentialRef exchange、§4 Secret 边界、§5 Provider/绑定/Snapshot、§6 Network Profile、§7 缺失/过期/替换/清除、§8 日志与错误、§9 P15 边界、§10 现状对照、§11 Verification 状态 |

## 1. AC 逐项结论

| AC | Owner 结论 | Reviewer 判定 | 说明 |
|---|---|---|---|
| AC1 | 完成 | **接受** | §2 需求映射逐条给出真实章节/AC 引用；Reviewer 15/15 AC id 与 D04/D07/D08 章节均实证存在，AC-SET 处理正确 |
| AC2 | 完成（契约） | **接受** | §3 六条 exchange 协议（专用一次性操作、不复用普通 DTO、引用不授权读取、请求期租约、引用与明文持有者、替换/清除语义）；§4 MUST NOT 清单覆盖 settings DTO / SQLite / 日志 / 错误 / 摘要 / 诊断包 / Snapshot；§7 生命周期；§8 序列化前脱敏 |
| AC3 | 完成（契约） | **接受** | §5 Provider/绑定/Snapshot/设置继承；§6 多 Network Profile、**Proxy 失败不得静默 Direct**、显式 Direct Fallback、连接测试分阶段、TLS 默认开启与关闭确认 |
| AC4 | 完成（只读对照） | **接受** | §10 逐文件对照，21 个符号实证存在；缺口标注为"拟议新增"；未修改任何实现 |
| AC5 | 完成（静态计划） | **接受** | §11 明确 SQLite 扫描、Credential Manager 真实读写、脱敏实测、TLS/代理端点、UI/E2E 全部 `NOT_RUN` 并移交 P15/P19 |
| AC6 | NOT_RUN | **Review 由本文件闭合；集成待 Coordinator** | Task 保持 `in_progress`，未越权标 done |

## 2. Findings

| id | 级别 | 内容 | 处置 |
|---|---|---|---|
| **F1** | **P2（流程）** | **交付 head 未冻结**：`delivery_head=a6e2cf58`（契约交付 commit），分支实际 `HEAD=fa20602d`（其后还有 `fa20602d docs: hand off P10 credential contract`）。与 P11 的同类问题重复出现 | Reviewer 已将本 Review 绑定**实际 HEAD `fa20602d`**（契约 blob 自 `a6e2cf58` 起未变，pin 13/13 一致，故内容风险低）。closeout 必须把 `delivery_head` 修正为实际值 |
| F2 | P3 | Task frontmatter `owner: Codex`（大写）与 role state 的 `codex`（小写）不一致；`reviewer: null` 未反映已路由的 dsh | closeout 统一为小写并填入 reviewer |
| **F3** | **P2（后续前置）** | 契约 §3.6 正确地**未选择**具体凭据后端与静态加密方案（"不在本契约选择范围内"）。这避免了自行作用户产品取舍，但意味着"Windows 凭据后端选型"成为 P15/Core runtime 适配的前置未决项 | 登记 BACKLOG；P15 释放时必须先冻结后端选型或明确由适配器层承担，不得在 runtime 中隐式决定 |
| F4 | P3 | 契约 §2 引用 `AC-FALLBACK-002`（P1 显式 fallback），Owner 回答的锚点清单未列出该 id | 已由 Reviewer 独立确认其真实存在（D08 L1762）；补充记录，不阻塞 |
| F5 | P4 | `evidence_dir=verification/P10` 在 Task 交付时尚无 `resource-manifest.json`（Resource Manifest 的 integrity 列指向它） | closeout 时由 Coordinator 创建并登记 |

## 3. 条件

- **C1**：Coordinator 集成时冻结实际被审 head `fa20602debb2d5f16f315bbed4180eae6f8821c5`，并把 Task `delivery_head` 与 `reviewer` 修正（F1/F2）。
- **C2**：P15 释放时引用本 Task 与契约 §3.6，把**凭据后端与静态加密方案选型**作为显式前置（F3 / BL-6），不得让 runtime 隐式决定。
- **C3**：closeout 登记证据 pin 与 Resource Manifest（F5）。
- 契约内容本身无需返修。

## 4. 能力边界

- 本 Review 仅覆盖契约交付面的静态正确性、范围合规与 secret 边界的条款可判定性；**不代表**任何 runtime 安全保证。
- `AC-SEC-001..005` 的 runtime Gate（SQLite 无明文、日志无明文、Credential Manager、TLS）仍全部 `NOT_RUN`，须在 P15/P19 以真实测试验收。
- 所有 Git / SHA-256 / 锚点 / 符号 / 扫描结论均由 Reviewer 在 live 环境实际执行。
- Reviewer 未修改被审分支、主仓或任何证据文件；未 push。
