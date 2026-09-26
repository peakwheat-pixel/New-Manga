---
task_id: M2-C1
author: ZCode
recipient: Codex
base_commit: 7478f72fe6f9872cae29f4fa12888b5e1f2380f1
delivery_head: 7de1cd27e22037d4b76b235c9f11399b0cea9463
status: in_review
---

# Handoff：M2-C1 — Typed IPC Contract（ZCode Owner Delivery）

## 交付结果

- **Owner disposition：`OWNER_ADOPTED_WITHOUT_SEMANTIC_CHANGE`（Case A）。**
- Adopted source head：`ac38dede84ff22290c9b9d579c1372c8184a7bd5`（Codex 草案最终内容 head，即 Qoder R3 的 `reviewed_head`；历史 disposition 为 `ARCHITECTURE_DRAFT / PRE_OWNER_BASELINE` + `APPROVED_ARCHITECTURE_DRAFT`，不构成本 Task 的最终双 Review）。
- **Owner Delivery head：`7de1cd27e22037d4b76b235c9f11399b0cea9463`**（branch `agent/zcode/M2-C1-typed-ipc-contract`，固定 base `7478f72fe6f9872cae29f4fa12888b5e1f2380f1`）。
- `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` 以逐字节方式取自 adopted head：Git blob SHA-1 = `4b503a170ff8ff6e995e5e5d70e3a053f9cc62c3`，SHA-256 = `c04b5af59c1c36ecaf862c9b63e8e410219966ea3d1e526e711ea19904b6f0d8`，与草案 blob 完全一致（复现命令与双侧取值见 [03-blob-equivalence.md](../../verification/M2-C1/zcode-owner/03-blob-equivalence.md)）。**任何后续 Review 都应核验被审 head 中该文件 blob 等于 `4b503a17…`，这是 Case A 等价性的精确证据。**
- Owner verification（`verification/M2-C1/zcode-owner/`）：`00` 环境与五项依赖 ancestry 复跑、`01` Owner base 锚定的 source trace 与抽查、`02` Owner decision log、`03` blob 等价对照、`04` scope/whitespace 检查、`05` 漂移核对与链接策略。
- 变更路径（base..delivery，7 个新增文件，全部在 Task 允许范围内）：Contract ×1、`verification/M2-C1/zcode-owner/**` ×6。无 `src/**`、`tests/**`、Schema、依赖、bootstrap、QML、React、Tauri/Rust/Python runtime、Domain Contract、Task/Plan/Status/Index 或历史 Review/evidence 变更。
- 本 Handoff 文件在 Delivery 之上的独立 commit 中提交；该 commit 不包含自身 hash。**ZCode final reviewed_head 应固定为本 Handoff commit（Owner branch tip）**：它包含 Delivery 全部内容，且其树中 Contract blob 仍为 `4b503a17…`。两位 Reviewer 必须绑定同一个 head。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| 环境与依赖 | `rev-parse --show-toplevel / branch --show-current / rev-parse HEAD / --git-common-dir / status`；5 × `merge-base --is-ancestor <dep> <base>` | Owner worktree，base=`7478f72…` | PASS：root/branch/HEAD/common dir 全部符合；开工前 status 0 行；D1/I1/I2/R1/UI1 ancestry 全 exit 0 | `verification/M2-C1/zcode-owner/00-environment.md` |
| 来源接管 AC-1 | 读取草案 Task/Contract/Handoff/source-trace/decision-log/remediation、Qoder R3 报告与 8 件 evidence；R-001…R-008 逐项重读 | 只读历史对象（`4d66523…`、`4ee7b3e5…`、`ac38dede…`、`1950a23…`、`86013b3…`） | PASS：全部可解析并重读；Task 指令示例文件名 `03-finding-recheck.md` 实际不存在，R3 evidence 03 号文件为 `03-delivery-scope.log`（已记录，非漂移） | `zcode-owner/00-environment.md`、`01-source-trace-owner-base.md` |
| AS-IS 在 Owner base 重验 | 9 个被引用文件 `git rev-parse <base>:$f` 双基线 blob 对比；枚举/行号/字段数/零命中探针抽查（`PipelineRunStatus` 九值、half-up 公式、`control_run:829`、`recover_running_runs:886`、`retry_failed_targets:903`+`TARGET_NOT_FOUND`、`TaskProjection` 23 字段、`list_revisions` 在 port、AD-001:33/:35、`CredentialRef` 零命中） | base=`7478f72…`，对照 `eec1aa4…` | PASS：9/9 blob SAME；`src/application`、`src/domain`、`src/ui` diff 为空；抽查全部吻合 | `zcode-owner/01-source-trace-owner-base.md` |
| Case A blob 等价 AC-3A | `git rev-parse` blob OID 双侧对比；`git hash-object`；Python SHA-256 双侧计算 | adopted=`ac38dede…` vs delivery=`7de1cd2…` | PASS：SHA-1 与 SHA-256 完全一致；行数 276=276 | `zcode-owner/03-blob-equivalence.md` |
| Scope / whitespace AC-6/7 | `git diff --name-status 7478f72…..7de1cd27…`；`git diff --check 7478f72… 7de1cd27…`（commit 后原样输出见下） | Git Bash；Git 2.52.0.windows.1 | PASS：7 个 A 路径全部允许；`--check` 无输出 exit 0 | `zcode-owner/04-git-scope-check.md`（staged 口径）+ 本表下方 commit 口径 |
| 漂移核对 | `git diff --name-status eec1aa4… 7478f72… -- src/ tests/` + 逐 diff 检视 | 两基线 | 无漂移：仅 `src/bootstrap/app.py`（PyInstaller frozen 资源根解析）与 4 个新增 `tests/packaging/**`，均不触及契约声明；`DRIFT_DETECTED` 不触发 | `zcode-owner/05-drift-and-links.md` |
| 链接策略 AC-7 | Owner 新增 Markdown 链接逐条检视 | delivery=`7de1cd2…` | PASS：新增文件只引用允许路径；Contract 内部链接保持草案原样（Case A blob 不变），其中 `../../verification/M2-C1/source-trace.md` 在 Owner 树内无目标，作为已解释的非语义限制记录（目标可经固定对象 `ac38dede…` 只读解析；Owner base 等效 trace 已提供） | `zcode-owner/02-decision-log.md` D-O2、`05-drift-and-links.md` |
| 产品 pytest / GUI / IPC Runtime | 未运行、未添加 | 文档-only Task | **NOT_RUN**（范围要求）；Collected/Passed/Failed/Skipped/Exit=`N/A` | `zcode-owner/04-git-scope-check.md` NOT_RUN register |

Commit 后原样复核（Owner Delivery=`7de1cd27e22037d4b76b235c9f11399b0cea9463`）：

```text
$ git diff --name-status 7478f72fe6f9872cae29f4fa12888b5e1f2380f1..7de1cd27e22037d4b76b235c9f11399b0cea9463
A	doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md
A	verification/M2-C1/zcode-owner/00-environment.md
A	verification/M2-C1/zcode-owner/01-source-trace-owner-base.md
A	verification/M2-C1/zcode-owner/02-decision-log.md
A	verification/M2-C1/zcode-owner/03-blob-equivalence.md
A	verification/M2-C1/zcode-owner/04-git-scope-check.md
A	verification/M2-C1/zcode-owner/05-drift-and-links.md
(exit 0)

$ git diff --check 7478f72fe6f9872cae29f4fa12888b5e1f2380f1 7de1cd27e22037d4b76b235c9f11399b0cea9463
(no output; exit 0)

$ git rev-parse 7de1cd27e22037d4b76b235c9f11399b0cea9463:doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md
4b503a170ff8ff6e995e5e5d70e3a053f9cc62c3
```

## 接收方式

- Owner branch / worktree：`agent/zcode/M2-C1-typed-ipc-contract` / `G:/CODEX/New Manga.worktrees/M2-C1-zcode-typed-ipc-contract`；commit 后 status clean。
- **ZCode final reviewed_head（建议 Codex 直接固定）**：本 Handoff commit（Owner branch tip）。核验三件套：(1) `git rev-parse <tip>:doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` = `4b503a170ff8ff6e995e5e5d70e3a053f9cc62c3`；(2) `git merge-base --is-ancestor 7de1cd27e22037d4b76b235c9f11399b0cea9463 <tip>` exit 0；(3) `git diff --name-status 7478f72fe6f9872cae29f4fa12888b5e1f2380f1..<tip>` 全部落在允许路径（Contract + zcode-owner/** + 本 Handoff）。
- 两位 Reviewer 的专属 Review worktree 由 Codex 从同一 reviewed_head 创建并登记后，Reviewer 路径授权才生效（本 Task §Review 阶段授权条款）。本 Handoff 不派发 Review。
- Qoder 可申请按 Case A 以旧 R3 evidence 做 `equivalence re-validation`（前提：核验被审 head 的 Contract blob=`4b503a17…` 且对 adopted head 的语义等价证据充分）；DeepSeek Harness 按协议做完整独立技术 Review。两者均不得复用彼此或 Owner 结论替代。

## 下一任务建议（必填）

- Task ID / 标题：M2-C1 双 Review 派发（当前 Task 的下一 Gate，不创建新 Task）。
- 推荐 Agent / 派发方：Codex（Scheduler/Release Control）；Reviewer A=DeepSeek Harness，Reviewer B=Qoder（均独立、非作者）。
- 推荐原因与前置依赖：Owner Delivery 与 Handoff 已固定，Case A 证据完备；两位 Reviewer 需绑定同一 `ZCode final reviewed_head`（本 Handoff commit）。
- Recovery point：仓库 `G:/CODEX/New Manga`（共享 common dir）；Owner branch `agent/zcode/M2-C1-typed-ipc-contract`；固定 base `7478f72fe6f9872cae29f4fa12888b5e1f2380f1`；Owner Delivery `7de1cd27e22037d4b76b235c9f11399b0cea9463`；最终 reviewed_head=Handoff commit（见本文件 frontmatter 之外的 Owner branch tip）。Reviewer worktree 待 Codex 创建。
- 允许修改路径：仅各 Reviewer 自己的 `doc/reviews/M2-C1-zcode-<delivery-short>-dsh.md` / `-qoder.md` 与对应 `verification/M2-C1/review-dsh-zcode-<delivery-short>/**` / `review-qoder-zcode-<delivery-short>/**`。
- 禁止范围与新增授权条件：不修改 Owner 文件、产品代码/测试、Schema/依赖、bootstrap、QML/React/Tauri/runtime、Domain Contract、历史 Review/evidence；不进入 Integration Gate、不集成、不启动 M2-S1；页级 `blocked` 映射与 React UI Owner 仍待用户裁决。
- 交付物：各 Reviewer 固定 head 的独立报告、命令与 exit codes、对 R-001…R-008 契约点的本轮独立结论、各自 Review commit 与 session 事实。
- 验证命令、环境与完成 Gate：按 Task §Review 与 Integration Gate 条款；双 Review 均 `APPROVED` 且绑定同一 head 后由 Codex 另行开启 Integration Gate。
- 可直接转发给 Agent 的指令：由 Codex 在创建并登记 Reviewer worktree 后生成；本 Handoff 不预生成 Reviewer prompt。

## 风险与遗留

- Contract §1 的 `../../verification/M2-C1/source-trace.md` 相对链接在 Owner branch 树内无目标（Case A 保持 blob 不变 + Owner 允许路径不含 `zcode-owner/` 之外的 verification 文件）。目标内容可经固定对象 `ac38dede…` 只读解析；Owner base 等效 trace 在 `verification/M2-C1/zcode-owner/01-source-trace-owner-base.md`。若 Codex 集成时希望消除该树内断链，属集成面的治理导航决定，需相应 Case 语义评估，不属本 Handoff 授权。
- 草案树的三条 R3 非阻塞说明（被删 ACL 链接、`source-trace.md:28` 引用格式、`531647e` Task 措辞残留）保持原状：前两条在草案/Codex 治理面，第三条在 reviewed head 之外；均不影响契约条款。
- 页级 `blocked` 的产品含义与视觉映射保持 `USER_DECISION_REQUIRED / DEFERRED`；Run 级映射未被套用；未指定 glyph 或用户行为。React UI Owner 未决定。大型媒体通道选型与容量验证留给独立 Spike。M2-S1 保持 `NOT_RELEASED`。
- 所有产品测试、GUI、IPC runtime、序列化与大媒体容量验证保持 `NOT_RUN`。本交付不授权 Integration Gate、集成或任何实现。
