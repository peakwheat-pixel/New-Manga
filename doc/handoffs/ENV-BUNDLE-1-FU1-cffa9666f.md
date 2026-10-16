---
task_id: ENV-BUNDLE-1-FU1
author: Codex
recipient: Coordinator
base_commit: 3bf2604dc9e8ef6be47bd80897e4df05cae077b3
delivery_head: cffa9666fbbe5f2adfe213de37a8beb20a994a38
status: ready_for_review
---

# Handoff：ENV-BUNDLE-1-FU1 I1 有界返修

## 交付结果

本次仅处理独立 Reviewer=dsh 对 AC2 启动超时脆弱性的 I1 finding。返修代码提交为 `cffa9666fbbe5f2adfe213de37a8beb20a994a38`（`test(ENV-BUNDLE-1-FU1): widen packaged startup deadline`）；该 Task 仍待独立复审，**不代表已接受**。

| AC | 当前结果 | 对照 |
|---|---|---|
| AC1 | PASS（此前证据） | 2.3 frozen bundle 来源、大小、SHA 与 protocol 见既有 manifest。 |
| AC2 | PASS（I1返修后全量重跑） | 六项使用真实 frozen bundle；新默认超时 120 秒；启动 ping 和所有场景断言仍有效。详见下表及 I1 记录。 |
| AC3 | BLOCKED（原判保持） | HostControl `RegisterImportSource` 返回 `REF_EXPIRED`；本次不改、不重测产品语义。 |
| AC4 | PASS（此前证据） | 主仓 ignored bundle/frontend 产物对齐证据不变。 |
| AC5 | PASS（本次范围） | 唯一代码文件为测试夹具；无产品语义、契约、Schema 或依赖改动。27 个 Cargo 行尾噪音文件已逐个恢复。 |
| AC6 | PASS（此前证据） | 本次未进入主仓或触碰 19 项 dirty；此前对比证据不变。 |
| AC7 | PASS（本次交接） | 固定返修提交、原始日志、Reviewer 日志副本、Task 记录和本 Handoff 已归档；未 push/merge。最终 Task Gate 仍等待 Reviewer。 |

### 变更路径与提交

- `apps/desktop/src-tauri/src/packaged_sidecar_tests.rs`：`PackagedLab::start_library()` 从 `M2RC1_PACKAGED_STARTUP_TIMEOUT_SECS` 读取正整数超时；变量未设置时使用 120 秒默认值。startup ping 仍必须成功，六项场景断言未改。
- `verification/ENV-BUNDLE-1-FU1/ac2-packaged-six-tests-i1-repair.log`：本次 PowerShell/Cargo 全量六项运行原始日志，记录退出码、耗时、环境、bundle 路径和 SHA，以及实际测试源 SHA。
- `verification/ENV-BUNDLE-1-FU1/reviewer-rerun-{packaged,isolated,isolated-2}.log`：从 Reviewer 给出的只读来源逐字节复制，原始路径和 SHA 见 [I1 返修记录](../../verification/ENV-BUNDLE-1-FU1/ac2-i1-startup-timeout-repair.md)。
- Reviewer 来源和逐项结论、复现条件、生产启动路径调查见 `verification/ENV-BUNDLE-1-FU1/ac2-i1-startup-timeout-repair.md`。

返修提交的代码与日志已固定；本 Handoff 和 Task / 验证说明作为后续文档交付提交。`delivery_head` 指返修实现提交，不要求实现提交包含自己的 Handoff。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| I1 / AC2 packaged 六项 | `cargo test --locked --manifest-path apps/desktop/src-tauri/Cargo.toml packaged_sidecar_tests::real_ -- --nocapture --test-threads=1` | PowerShell 7.6.6；cargo 1.98.1；rustc 1.98.1；实现代码 `cffa9666fbbe5f2adfe213de37a8beb20a994a38`；`M2RC1_PACKAGED=1`，source env unset，超时变量 unset（默认 120 s）；frozen `core_service.exe` 68,717,156 bytes，SHA-256 `896bd56286b25bc8539028d52f3ef991cfbcbda24f93ae6c6d75758a7dbfd842` | `6 passed; 0 failed; 0 ignored; 77 filtered out`；Cargo 测试 `139.55 s`，含编译命令总耗时 `174.24 s`，exit `0` | `verification/ENV-BUNDLE-1-FU1/ac2-packaged-six-tests-i1-repair.log` |
| Reviewer 脆弱性复现 | 只读核对 full、isolated 首次失败和 isolated 再次通过的原始日志 | Reviewer 原始来源位于 `G:/CODEX/New Manga.workspace/tmp/guarded/` | full `4/6`（111.59 s），isolated 首次 `0/1`（35.03 s），同用例再次隔离 `1/1`（13.58 s）；均如实保留，未把失败归作返修后结果 | `verification/ENV-BUNDLE-1-FU1/reviewer-rerun-*.log`、I1 返修记录 |
| AC1 / AC4 / AC6 | 复用此前已归档证据，本次未重跑 | 原交付证据 commit `998200d48e10899e2916a73143578c69bceb30cf` | PASS（沿用此前结论） | Task Canonical Evidence 表中的 AC1/AC4/AC6 项 |
| AC3 HostControl | 本次不重测 | 原 frozen Core 探测 | BLOCKED：`REF_EXPIRED`，保持原判 | `verification/ENV-BUNDLE-1-FU1/ac3-host-control-blocked.md` |

本次未运行既有 77 项 source-backed 用例、NSIS installer 或 GUI 安装验收；均保持 `NOT_RUN`。环境变量覆盖分支未单独运行；全量六项运行使用 unset 变量的新默认值。

## 接收方式

- Branch：`codex/ENV-BUNDLE-1-FU1-packaged-acceptance`
- Owner worktree：`G:/CODEX/New Manga.workspace/worktrees/ENV-BUNDLE-1-FU1`
- Task base：`3bf2604dc9e8ef6be47bd80897e4df05cae077b3`
- I1 implementation head：`cffa9666fbbe5f2adfe213de37a8beb20a994a38`
- AC2 复现：保留该 worktree ignored frozen bundle；设置 `M2RC1_PACKAGED=1`，清除 `M2RC1_SRC_ROOT` 和 `M2RC1_PYTHON`，清除 `M2RC1_PACKAGED_STARTUP_TIMEOUT_SECS` 以使用默认 120 秒，再执行验证表中完整 Cargo 命令。
- Reviewer 复跑仍必须确认六项启动均走该 worktree frozen bundle、环境变量实际取值、六项真实断言、原始日志/退出码及生成物噪音恢复情况。不要将此次 Owner 自测描述为独立 Review。

## 下一任务建议（必填）

- **Task ID / 标题**：`ENV-BUNDLE-1-FU1` I1 独立复审与 AC2 packaged 六项复跑；Coordinator 应在当前 Handoff 与本次文档证据提交固定后释放。
- **推荐 Agent / Reviewer**：DeepSeek Harness（dsh）；与实现 Owner Codex 不同。
- **推荐原因与前置依赖**：独立确认 I1 修复未改变验收语义，并在其独立工作区重跑 packaged 六项。AC3 `REF_EXPIRED` 仍保持 `BLOCKED`，不得作为该 Review 的返修范围。
- **Recovery point**：仓库 `G:/CODEX/New Manga`；Owner branch `codex/ENV-BUNDLE-1-FU1-packaged-acceptance`；Owner worktree `G:/CODEX/New Manga.workspace/worktrees/ENV-BUNDLE-1-FU1`；Task base `3bf2604dc9e8ef6be47bd80897e4df05cae077b3`；I1 实现 head `cffa9666fbbe5f2adfe213de37a8beb20a994a38`；Reviewer 独立 worktree 与 review head 待 Coordinator 创建/固定。
- **允许修改路径**：Coordinator 释放的 Reviewer worktree 内 Review 报告及必要复核日志。
- **禁止范围与新增授权条件**：只读检查 Owner 代码和既有证据；不得修改测试、产品实现、契约、Schema、依赖、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md` 或主仓 19 项 dirty；不得改变 AC3 判定。
- **交付物**：依 `doc/templates/REVIEW.md` 形成 I1 Review；保存独立 full six-test 原始日志、耗时、退出码、逐项结果与 frozen exe SHA；报告测试生成的 27 个文件是否恢复。
- **验证命令、环境与完成 Gate**：设置 `M2RC1_PACKAGED=1`，unset `M2RC1_SRC_ROOT`、`M2RC1_PYTHON`、`M2RC1_PACKAGED_STARTUP_TIMEOUT_SECS`，执行 `cargo test --locked --manifest-path apps/desktop/src-tauri/Cargo.toml packaged_sidecar_tests::real_ -- --nocapture --test-threads=1`。要求六项 PASS、零 skip、exit `0`，真实 Core startup ping 成功且断言未改变；Reviewer 原始日志入库，未跑项如实标记。Review Gate 由 Coordinator 核对并更新 Task 状态；本 Handoff 不声称已接受。
- **可直接转发给 Agent 的指令**：

  > 请独立复审 `ENV-BUNDLE-1-FU1` 的 I1 返修，并从你的独立 Reviewer worktree 复跑 packaged 六项。恢复点：仓库 `G:/CODEX/New Manga`；Owner branch `codex/ENV-BUNDLE-1-FU1-packaged-acceptance`；Owner worktree `G:/CODEX/New Manga.workspace/worktrees/ENV-BUNDLE-1-FU1`；Task base `3bf2604dc9e8ef6be47bd80897e4df05cae077b3`；I1 实现 head `cffa9666fbbe5f2adfe213de37a8beb20a994a38`；Reviewer worktree/head 待 Coordinator 创建和固定。只读核对测试夹具及 `verification/ENV-BUNDLE-1-FU1/ac2-i1-startup-timeout-repair.md`，检查生产路径风险报告，不改产品代码或 Task 共享范围。保留相同 2.3 frozen bundle，设置 `M2RC1_PACKAGED=1`，清除 `M2RC1_SRC_ROOT`、`M2RC1_PYTHON` 与 `M2RC1_PACKAGED_STARTUP_TIMEOUT_SECS`，执行 `cargo test --locked --manifest-path apps/desktop/src-tauri/Cargo.toml packaged_sidecar_tests::real_ -- --nocapture --test-threads=1`。记录 shell/runtime、bundle 路径与 SHA、逐项结果、耗时、退出码和 27 个生成文件处理结果；要求六项真实断言全通过、无 skip。AC3 `REF_EXPIRED` 保持 `BLOCKED`，任何未跑内容标 `NOT_RUN/BLOCKED`；按模板提交独立 Review 和原始日志，等待 Coordinator 决定 Gate。

## 风险与遗留

- **待 Coordinator 另立产品 Task**：生产 Host 启动 packaged 与 source-backed Core 都使用 30 秒 ping deadline，证据见 `apps/desktop/src-tauri/src/main.rs:816-822,834-851`；调用契约与超时错误见 `apps/desktop/src-tauri/src/library_bridge.rs:611-634`。若生产环境遇到与 Reviewer 相似的并发负载，可能出现同类 Core 冷启动超时。该风险是调用值与测试反例的推断，未生产复现；本次没有修改任何产品文件。
- AC3 `HostControl RegisterImportSource → REF_EXPIRED` 保持 `BLOCKED`，另需获授权的产品 Task。
- 本次只重跑六项 packaged 测试；source-backed 全套、NSIS installer、GUI 安装验收仍未运行。
- 27 个 `gen/schemas/**`、`permissions/autogenerated/**` 文件的 Cargo 纯行尾噪音已逐项恢复，`git diff` 中不含这些路径。
- 未 push、未 merge。实现与 Review 的最终 Gate 仍未关闭。
