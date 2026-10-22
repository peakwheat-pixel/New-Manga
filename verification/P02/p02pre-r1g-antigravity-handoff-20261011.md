---
task_id: P02PRE-R1G
author: Antigravity
recipient: Codex
base_commit: cddff58469b56e181019a8ddfeade80684bc7eb9
implementation_commit: 9eb14e35d39bcfa9f6bd89553a94dd5d86da2cd3
previous_owner_revision_commit: 6e1c00fee3db07805c92c25cdc311af9279ceb51
predecessor_reviewed_delivery_head: 9ec34a8847f625331c729306fd303bd5df09ab92
status: delivered
---

# Handoff：P02PRE-R1G — PowerShell 7 只读取证恢复（R-009/R-010 最小修复交付）

## 交付结果

本任务严格依照 [P02PRE-R1G.md](../../doc/tasks/P02PRE-R1G.md) 与 [p02pre-r1g-manifest-20261011.md](p02pre-r1g-manifest-20261011.md) 授权边界执行，写入范围仅限于分配的任务工作区 `C:\Users\49745\.codex\worktrees\p02pre-r1g\New Manga` 及分支 `agent/antigravity/P02PRE-R1G`，未修改主仓任何文件、未修改 R1F 历史证据产物、未修改 Plan/STATUS/共享契约。

- 初始实现提交（Initial Implementation Commit）：`9eb14e35d39bcfa9f6bd89553a94dd5d86da2cd3`
- 前序被审交付 HEAD（Predecessor Reviewed Delivery HEAD）：`9ec34a8847f625331c729306fd303bd5df09ab92`
- 早期作者修订提交（Earlier Owner Revision Commits）：`133a832b2fa0d450fcfd131c085698841cfbfafb`、`6943c6727c82c706d90a3ed4c14617b04c98d360`
- 前序作者修订提交（Previous Owner Revision Commit）：`6e1c00fee3db07805c92c25cdc311af9279ceb51`（Review follow-up 2 被审 HEAD）
- 本轮返修交付提交（Current Follow-up Delivery Commit）：本轮以单独 commit 提交，最终 delivery HEAD 由 Codex 在 Task/checkpoint 外部记录。
- **说明**：Git commit ID 强依赖 commit 内文件字节，Handoff 无法在自身内容中稳定自引用包含它自己的 HEAD；本文件已彻底移除自引用 `delivery_head` 字段，全篇不将 `6e1c00fee3db07805c92c25cdc311af9279ceb51` 称作本轮返修后的最终 HEAD。

### 交付产物与 SHA-256 钉选

| 文件路径 | 字节数 (bytes) | SHA-256 | 说明 |
|---|---:|---|---|
| `verification/P02/p02pre-r1g-capture.ps1` | 81991 | `3C7D85AB3E20C023873197FE391B8F22DFB319038F43B7C554DC4F38927AADDF` | R1G 候选只读取证脚本（PowerShell 7.6.6，修复 R-009 WER 非法目录 fail-fast 与 R-010 证据 fallback bounded phase map） |
| `verification/P02/p02pre-r1g-author-selfcheck-20261011.json` | 2462 | `54D71B4F10F4520F12D7EB41389BE750301A6A726ECCE8655A3D7CCDEAC4B20C` | 作者交付自检 JSON，诚实钉选候选产物哈希，依发布顺序记录未运行项 |
| `verification/P02/p02pre-r1g-antigravity-handoff-20261011.md` | 本文件 | 见提交元数据 | 交付交接文档与后继建议（修复 R-009 与 R-010 细节说明） |

### 审查与返修处置说明

依据 Codex sub-agent 独立审查报告 (`codex-subagent-p02pre-r1g-review-followup2-20261012.md`) 及 Codex 集成裁定 (`p02pre-r1g-review-followup2-adjudication-20261012.md`)，原实现 Owner Antigravity 对接受的两项 P2 发现项完成最小闭环修复，既有已闭环项保持不变：

| 项 | 严重度 | 涉及领域 | 处置状态 | 处置说明 |
|---|---|---|---|---|
| **R-009** | P2 | WER 非法目录状态提前停机（Fail-fast）与阶段阻断 | **CLOSED (Author)** | 在 `capture.ps1` 的 WER phase 中，增加对冻结 WER 目录记录状态的检查：通过 `$werInvalidDirectoryRecords` 显式检测 `REPARSE_POINT` 与 `NOT_DIRECTORY` 状态。若发现任一非法目录，立即将 `phases.wer` 标为 `FAILED`，将 `classifications.werQueriedFields` 标为 `FAILED`（绝不报为 `PASS_WITH_EVIDENCE`），填入 `stopCategory = 'INVENTORY_OR_QUERY_STOP'`、`stopReason = if ($werInvalidDirectoryCount -gt 0) { 'WER_INVALID_DIRECTORY_FAILED' } else { 'WER_QUERY_FAILED' }`，并在 `stopDetail` 中详细列出非法目录计数、具体路径及状态。由于此时 `$Result.stopReason` 已被设置，脚本直接阻断后续 `protectedHashes` 与 `aclStability` phase（保持 `NOT_REACHED`），不再触发后续 getter 或重解析点查询。现有 helper 与已有的 `QUERY_ERROR`/`ACL_QUERY_ERROR` fail-stop 行为完整保留。 |
| **R-010** | P2 | 两个 evidence fallback 分支保留 bounded phases 字典 | **CLOSED (Author)** | 新增纯函数 `Get-BoundedPhaseMap([object]$Phases)`，将 phase 字典投影为一个固定大小、仅包含当前脚本全部 8 个阶段 key（`identity`、`mainRepository`、`scratchRepository`、`environment`、`paths`、`wer`、`protectedHashes`、`aclStability`）的有序字符串映射。在主 `ConvertTo-Json` 异常捕获 fallback（Fallback 1）和 bounded partial JSON 超限（>64 MiB）fallback（Fallback 2）中，均加入 `phases = Get-BoundedPhaseMap $Result.phases`。同时完整保留 `underlyingStop...` 与 `originalStop...` 字段、各级停机分类/原因/细节以及 `captureStatus = 'PARTIAL_EVIDENCE'`，绝不将 unbounded Result 或完整文件列表塞入 fallback。在 `New-PartialEvidence` 中亦同步采用 `Get-BoundedPhaseMap` 确保一致性。 |
| **ArgumentList 契约** | P2 | 子进程有序参数与 ProcessStartInfo.ArgumentList 传递 | **CLOSED (Author)** | 维持前序修复：有序 string 数组传递，消除 `.Arguments` 赋值，留存 `argumentList` 与 `workingDirectory`。 |
| **R-001** | P2 | 证据写出与序列化失败停机机读区分及底层原因保留 | **CLOSED (Author)** | 维持前序修复：底层停机字段在 fallback JSON 中完整保留，写出失败由 runner 留证。 |
| **R-002** | P2 | Handoff AC 状态声明客观性 | **CLOSED (Author)** | 维持前序修复：严禁将 Codex-owned 或未运行项标为作者 PASS。 |
| **R-003** | P2 | 受保护哈希失效 fail-stop 顺序与 ACL stability phase 状态 | **CLOSED (Author)** | 维持前序修复：受保护哈希失效立即 fail-stop 并阻断 ACL stability。 |
| **R-004** | P2 | task/manifest/code source pin 一致性 | **DEFERRED_TO_CODEX** | 维持 Codex 职责。 |
| **R-005** | P3 | Handoff front-matter 移除自引用 delivery_head | **CLOSED (Author)** | 维持前序修复：移除自引用 `delivery_head`，记录前序修订 commit。 |
| **R-006** | P3 | Engine attestation 进程内断言范围声明 | **CLOSED (Author)** | 维持前序修复：进程中断言与诊断记录严格区分。 |
| **R-007** | P3 | manifest predecessor pin 与 Task 历史对齐 | **DEFERRED_TO_CODEX** | 维持 Codex 职责。 |
| **R-008** | P3 | author-selfcheck executionAttestation 措辞精确性 | **CLOSED (Author)** | 维持前序修复：诚实声明只读工具与未运行项。 |

### 设计说明与最小安全后继变更（Minimal Safe Successor）

1. **继承范围（完全继承 R1F 安全契约）**：
   - 严格继承 R1F manifest 的 identity（`HOME-MY\49745` / `S-1-5-21-2196946971-914346751-4210154634-1001`）。
   - 继承 main（`cddff584` / `c25d051a`）与 scratch（`7ce3c40c` / `ce8056b8`）仓库 roots、heads、trees 及 refs 校验。
   - 继承 `.tmp.driveupload` path-only 路径排除策略与 `Test-UnreadUserDataStagingPath` 严格不读内容边界。
   - 继承 tracked symlink（mode `120000`）`SKIP_TRACKED_SYMLINK` 不跟从策略与元数据仅存留。
   - 继承 Git CLI 参数及调用次序，仅允许已列明的 Git 可执行文件与 `whoami.exe /all` 子进程。
   - 继承 96 项受保护路径策略（96 protected path policy）。
   - 继承 TEMP/cache/scratch/WER/registry/ACL getter 白名单与只读检查。
   - 继承所有失败即停（fail-stop）语义与唯一的 `FileMode.CreateNew` 证据文件写出（无追加、无覆盖、无重试）。

2. **核心功能差异（Deltas）与审查修复（Remedies）**：
   - **WER 阶段非法目录检测与 Fail-fast（R-009）**：
     在 WER 采集阶段，原有逻辑仅对 `QUERY_ERROR` 和 `ACL_QUERY_ERROR` 进行阶段级计数，导致 `Get-ExactDirectoryRecord` 返回 `REPARSE_POINT` 或 `NOT_DIRECTORY` 时，`phases.wer` 仍会被标记为 `COMPLETED`，`werQueriedFields` 被标记为 `PASS_WITH_EVIDENCE`，并继续向后执行 `protectedHashes` 与 `aclStability`。
     本轮修复在 WER 阶段显式增加：
     `$werInvalidDirectoryRecords = @($werDirectoryRecords | Where-Object { $_.state -in @('REPARSE_POINT','NOT_DIRECTORY') })`
     一旦 `$werInvalidDirectoryCount -gt 0`：
     - `werQueriedFields` 立即置为 `'FAILED'`；
     - `phases.wer` 立即置为 `'FAILED'`；
     - 设置 `stopCategory = 'INVENTORY_OR_QUERY_STOP'` 与 `stopReason = 'WER_INVALID_DIRECTORY_FAILED'`；
     - `stopDetail` 包含具体的目录查询错误数、非法目录数及每个非法目录的路径与状态详情；
     - 由于 `$Result.stopReason` 已非空，后续的 `protectedHashes`（L847）和 `aclStability`（L965）均被跳过，在最终输出中保持 `NOT_REACHED`，实现严格的阶段失败即停。
   - **证据回退分支保留阶段证据（R-010）**：
     原候选在主 `ConvertTo-Json` 序列化异常 fallback（L1122）以及 bounded partial JSON 二次超限 fallback（L1148）中均省略了 `phases` 字段，导致 post-run 无法根据生成的最小证据文件机读还原已到达和未到达阶段。
     本轮修复新增轻量纯函数 `Get-BoundedPhaseMap`，从 `$Result.phases` 中提取全部 8 个冻结阶段键（`identity`、`mainRepository`、`scratchRepository`、`environment`、`paths`、`wer`、`protectedHashes`、`aclStability`），保证其为固定深度与大小的受限字典，并分别写入两个 fallback JSON 对象中。
   - **保持安全与架构边界**：不引入任何新增路径查询，不跟随重解析点，不修改已有路径 helper 语义，不增加任何子进程调用。

### Acceptance Criteria 对照表

| AC 项 | 描述 | 状态 | 交付说明 |
|---|---|---|---|
| AC1 | Codex 冻结本 Task、manifest、精确 executor/preflight、唯一输出路径与 allowlist | CODEX_OWNED / NOT_VERIFIED_BY_AUTHOR | Codex 负责契约冻结；Antigravity 作为只读输入加载核验，哈希匹配但未独立认证 Codex 契约完整性。 |
| AC2 | Antigravity 从主仓 R1F 源码只读加载，仅在本分支创建新 script/self-check/Handoff，更新 pins，增加显式 phase 与 engine attestation，保持安全契约 | DELIVERED_BY_AUTHOR | 交付 `p02pre-r1g-capture.ps1`、`p02pre-r1g-author-selfcheck-20261011.json` 及本 Handoff，并完成 R-009/R-010 闭环修复。 |
| AC3 | Candidate self-check 仅做 PS7 parse 与纯函数内存 assertion，不 invoke capture/getters/writes/build/AC | NOT_RUN / NOT_VERIFIED | 依冻结发布顺序，PowerShell 7 子进程语法解析与自检未运行，作者交付自检 JSON 真实记录为 `NOT_RUN`。 |
| AC4 | 非作者独立 Review exact Task/manifest/script/self-check/Handoff pins；Codex adjudicate | CODEX_OWNED / IN_PROGRESS | Codex sub-agent 第二轮审查已完成，本轮返修交付闭环 R-009/R-010，后继交由 Codex 裁决及安排非作者复审。作者不声称 AC4 通过。 |
| AC5 | Codex 运行独立 capability preflight，核对版本、edition、language mode、命令解析 | CODEX_OWNED / NOT_RUN | 属于 Review approved 后的 Codex 集成步骤。 |
| AC6 | pre-run 核对身份/SID、refs、Git status、96 protected hashes，匹配后最多调用一次 capture | CODEX_OWNED / NOT_RUN | 属于 Codex pre-run release 步骤。 |
| AC7 | 独立 post-run Review 与 Codex adjudication 按证据分类已到达/未到达阶段；不自动解除 Gate | CODEX_OWNED / NOT_RUN | 属于 post-run 阶段。 |

## 验证证据

| 验证场景 / 步骤 | 实际命令 / 步骤 | 环境与被测 Commit | 结果 | 产物 / 证据 |
|---|---|---|---|---|
| 工作区与分支合规核查 | `git rev-parse --show-toplevel`<br>`git rev-parse --git-common-dir`<br>`git status --porcelain=v1 -z --untracked-files=all --no-renames --ignore-submodules=none -- . ':(exclude).tmp.driveupload'`<br>`git rev-parse HEAD`<br>`git branch --show-current` | Windows x64, worktree `p02pre-r1g`, base `cddff584` | PASS | Worktree clean, 分支为 `agent/antigravity/P02PRE-R1G`, common-dir 为 `G:/CODEX/New Manga/.git` |
| 冻结输入校验 | Python 检查报告与裁定文件 | 主仓 `G:\CODEX\New Manga` | PASS | 详细研读 `codex-subagent-p02pre-r1g-review-followup2-20261012.md` 与 `p02pre-r1g-review-followup2-adjudication-20261012.md` |
| R-009 / R-010 静态审查 | Python 静态审查对比 | Worktree `p02pre-r1g` | PASS | 确认 WER 阶段非法目录即刻 fail-fast 并阻断后续阶段；确认两个 fallback 均注入 bounded phases 字典 |
| 候选脚本差异审计与哈希计算 | Python hashlib 核验 `capture.ps1` | 本地工作树 | PASS | 字节数 81991，SHA-256 `3C7D85AB3E20C023873197FE391B8F22DFB319038F43B7C554DC4F38927AADDF` |
| 自检 JSON 哈希核验 | Python hashlib 核验 `author-selfcheck.json` | 本地工作树 | PASS | 字节数 2462，SHA-256 `54D71B4F10F4520F12D7EB41389BE750301A6A726ECCE8655A3D7CCDEAC4B20C` |
| Git 变更集严格核查 | `git diff cddff584... --name-only` | 本地工作树 | PASS | 严格仅包含分配的 3 个文件，未修改其他任何路径 |
| PowerShell 7 子进程语法解析 / Self-check | 未运行（依发布顺序禁止作者派发时调用） | N/A | NOT_RUN | `verification/P02/p02pre-r1g-author-selfcheck-20261011.json` |
| Engine capability preflight | 未运行（待 Review approved 后由 Codex 执行） | N/A | NOT_RUN | [P02PRE-R1G.md](../../doc/tasks/P02PRE-R1G.md) AC5 |
| R1G Capture 运行时采集 | 未运行（待 pre-run release 后最多调用一次） | N/A | NOT_RUN | [P02PRE-R1G.md](../../doc/tasks/P02PRE-R1G.md) AC6 |
| Build / Cargo / AC1–AC7 | 未运行（硬构建屏障生效中） | N/A | BLOCKED / NOT_RUN | Gate 状态保持 |

## 接收方式

1. **分支与工作树**：
   - 分支：`agent/antigravity/P02PRE-R1G`
   - worktree：`C:\Users\49745\.codex\worktrees\p02pre-r1g\New Manga`
   - base HEAD：`cddff58469b56e181019a8ddfeade80684bc7eb9`
   - common-dir：`G:/CODEX/New Manga/.git`
2. **前置核验步骤**：
   - 检查 `git diff cddff58469b56e181019a8ddfeade80684bc7eb9..HEAD --name-only` 严格仅输出分配的 3 个文件。
   - 校验 `verification/P02/p02pre-r1g-capture.ps1` 之字节数（81991）与 SHA-256（`3C7D85AB3E20C023873197FE391B8F22DFB319038F43B7C554DC4F38927AADDF`）。
   - 校验 `verification/P02/p02pre-r1g-author-selfcheck-20261011.json` 之字节数（2462）与 SHA-256（`54D71B4F10F4520F12D7EB41389BE750301A6A726ECCE8655A3D7CCDEAC4B20C`）。

## 下一任务建议（协作协议 §5.1）

- **Task ID / 标题**：`P02PRE-R1G — PowerShell 7 只读取证恢复`（Codex 裁决与后继复审派发）
- **推荐 Agent / Reviewer**：`Codex`（Integrator/Adjudicator）；`DeepSeek Harness` / 独立 Reviewer（非作者 Reviewer）
- **推荐原因与前置依赖**：Antigravity 已对 Review follow-up 2 中接受的全部两项发现（R-009 WER 非法目录 fail-fast 与 R-010 证据 fallback bounded phase map）完成代码与交接文档修复。依据协作协议与 Codex 裁定，下一步需由 Codex 独立核验本次交付、冻结新一轮输入 pins，并在 Task/checkpoint 外部记录包含本 Handoff 的最终 delivery HEAD，然后派发非作者独立 Review 或进入后续隔离步骤。
- **Recovery point**：
  - Repo：`G:\CODEX\New Manga`
  - Branch：`agent/antigravity/P02PRE-R1G`
  - Base commit：`cddff58469b56e181019a8ddfeade80684bc7eb9`
  - Initial implementation commit：`9eb14e35d39bcfa9f6bd89553a94dd5d86da2cd3`
  - Predecessor reviewed delivery HEAD：`9ec34a8847f625331c729306fd303bd5df09ab92`
  - Earlier owner revision commits：`133a832b...`、`6943c672...`
  - Previous owner revision commit：`6e1c00fee3db07805c92c25cdc311af9279ceb51`
- **允许修改路径**：
  - Codex：`doc/tasks/P02PRE-R1G.md`、`verification/P02/p02pre-r1g-manifest-20261011.md`、`codex-checkpoint-p02pre-r1g-20261011.md` 及裁决产物。
  - 非作者 Reviewer：只读审查，输出新一轮 review 产物。
- **禁止范围与新增授权条件**：
  - 禁止重跑、覆盖或修改任何 R1F artifact。
  - 禁止未完成 Review 与 preflight 即调用 capture。
  - 严禁调用 Build/Cargo/AC1–AC7 或修改主仓未提交文件。
- **交付物**：
  - Codex 交付核验与新 pins 冻结记录。
  - 非作者独立 Review 报告。
- **验证命令、环境与完成 Gate**：
  - Gate 保持不变，未完成 capture 与 post-run adjudication 前任何 Gate 不得释放。
- **可直接转发给 Codex 的指令**：
  ```markdown
  请对任务 P02PRE-R1G 的最新修订交付进行裁决与集成处理：
  - 工作树：C:\Users\49745\.codex\worktrees\p02pre-r1g\New Manga
  - 分支：agent/antigravity/P02PRE-R1G
  - 基线：base=cddff58469b56e181019a8ddfeade80684bc7eb9
  - 前序修订提交：previous_owner_revision_commit=6e1c00fee3db07805c92c25cdc311af9279ceb51
  - 本轮修复项：Antigravity 已闭环处置 R-009 与 R-010：
    1. R-009：在 WER 阶段显式检查 REPARSE_POINT 与 NOT_DIRECTORY，若存在立即置 phases.wer='FAILED'、werQueriedFields='FAILED'、stopCategory='INVENTORY_OR_QUERY_STOP'、stopReason='WER_INVALID_DIRECTORY_FAILED'，并跳过后续 protectedHashes 与 aclStability；
    2. R-010：实现 Get-BoundedPhaseMap，在 ConvertTo-Json 异常 fallback 与 64 MiB 超限 fallback 中均注入 bounded phases 字典，保留 underlyingStop/originalStop 字段与 partial 分类；
    3. 交付文件钉选：已同步更新 author-selfcheck.json 与 Handoff 中的字节数与 SHA-256。
  - Codex 待处理项：独立核验 delivery，更新 Task/manifest pins，在外部记录最终 delivery HEAD，并派发非作者独立 Review 或 preflight。
  ```

## 风险与遗留

1. **Gate 与风险不变性声明（完全维持原值）**：
   - `private_registry_absence=UNPROVABLE`
   - Technical Gate=`NOT_SATISFIED`
   - Owner Risk Acceptance=`APPROVED`
   - Gate Disposition=`WAIVED_BY_OWNER`
   - Build Authorization=`AUTHORIZED_WITH_EXCEPTION`
   - 残余风险说明：`technical condition unmet; user explicitly accepted residual risk`
   - Build Gate=`BLOCKED`
   - Hard Build Barrier=`EFFECTIVE`
   - Build/Cargo=`NOT_RUN`
   - AC1–AC7=`BLOCKED / NOT_RUN`
2. **执行器可用性风险**：PowerShell 7.6.6 的 `Get-FileHash` 与 `Get-Acl` 在 `-NoProfile` 无配置文件子环境中的实际命令解析与模块发现，目前尚无 child runtime 证据，必须依靠 Codex 在后继步骤中执行独立的 capability preflight 确认。
3. **一次性采集约束**：R1G capture 在 pre-run release 后仅允许执行一次，一旦遭遇任何非预期失败必须 fail-stop 并完整保留现场，严禁重试或覆盖。
