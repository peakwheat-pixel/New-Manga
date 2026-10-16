---
task_id: HOST-CORE-1
author: Codex
recipient: DeepSeek Harness
base_commit: ed79b76f9191f0a5ebb6932a53a992a33a274041
delivery_head: 4af86abb374cfccf92de07d4e5b975dfbaf0dd2b
status: in_review
---

# Handoff：HOST-CORE-1

## 交付结果

Core 已实现契约 §5.7 HostControl v2.3 接收面：独立 stdio envelope、一次性 Host session、credential/core session 校验、四个 grant 注册/撤销路由、关闭及 EOF 撤销。普通 JSON-RPC 不路由 HostControl command。

- 固定实现提交：`4af86abb374cfccf92de07d4e5b975dfbaf0dd2b`（`feat(HOST-CORE-1): implement HostControl Core handler`）。
- 基线：`ed79b76f9191f0a5ebb6932a53a992a33a274041`。
- 修改路径：`src/bootstrap/core_service.py`、`tests/core/**`。
- 没有修改 `core_assembly.py`：它已装配每个 Core 的 import/export registry。
- 未改变 `ImportSourceRef` / `ExportTargetRef` wire 字段、签名输入与既有 `REF_*` 消费语义。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1–AC3 | stdio 握手、四个 seam 的注册/撤销、ref 消费/撤销 | Python 3.12.3 task-env；`4af86abb` | PASS | `verification/HOST-CORE-1/ac-matrix.md`、`ac2-session-lifecycle.md` |
| AC4 | 三类拒绝 + credential 缺失/错误/关闭变体；spy、registry、SQLite 与磁盘快照断言 | Python 3.12.3 task-env；`4af86abb` | PASS | `verification/HOST-CORE-1/ac4-denials.md` |
| AC5 | 六个 HostControl command 逐一通过普通 JSON-RPC dispatcher | Python 3.12.3 task-env；`4af86abb` | PASS | `verification/HOST-CORE-1/ac5-dispatcher-negative.md` |
| AC6 | diff 路径审计 | 基线 `ed79b76` → 实现 `4af86abb` | PASS | `verification/HOST-CORE-1/scope-audit.md` |
| AC7 | `G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe -m pytest tests/core -q` | Python 3.12.3；`4af86abb` | PASS：393 passed、0 failed、1 个既有 Pillow deprecation warning；exit 0 | `verification/HOST-CORE-1/pytest-tests-core.log` |
| AC8 | 固定 head 与 Handoff | `4af86abb` | PASS | 本文件 |
| AC8 | 非作者 Review、Coordinator integration | 尚未运行 | NOT_RUN | 由接收者后续完成；Task 保持 `in_review` |

## 接收方式

- branch：`codex/HOST-CORE-1-hostcontrol-handler`
- worktree：`G:/CODEX/New Manga.workspace/worktrees/HOST-CORE-1`
- 复现：从 worktree 执行 `G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe -m pytest tests/core -q`。
- Review 固定检查 `reviewed_head=4af86abb374cfccf92de07d4e5b975dfbaf0dd2b`；只读代码和证据，Review 文件可写入 `verification/HOST-CORE-1/`。
- Review 通过后，Codex 再按 Coordinator Gate 处理集成；本 Handoff 不代表已集成。

## 下一任务建议（必填）

- Task ID / 标题：`HOST-CORE-1` 独立 Review 与 Coordinator integration Gate。
- 推荐 Agent / Reviewer：DeepSeek Harness (`dsh`) 独立 Review；Codex 处理后续集成。Owner 与 Reviewer 不同。
- 推荐原因与前置依赖：Codex 是实现作者，需非作者安全审查；AC8 尚未完成。
- Recovery point：主仓 `G:/CODEX/New Manga`（只读）；branch `codex/HOST-CORE-1-hostcontrol-handler`；worktree `G:/CODEX/New Manga.workspace/worktrees/HOST-CORE-1`；base `ed79b76f9191f0a5ebb6932a53a992a33a274041`；固定 head `4af86abb374cfccf92de07d4e5b975dfbaf0dd2b`。
- 允许修改路径：Reviewer 仅写 `verification/HOST-CORE-1/dsh-review-r1.md`；集成由 Codex 按项目集成流程另行执行。
- 禁止范围与新增授权条件：不改 `doc/contracts/**`、`apps/**`、Schema/migration、依赖、`src/bootstrap/core_assembly.py` 或其他生产路径；Review 不得自行修实现。
- 交付物：以 H1 为 reviewed head 的独立 Review、明确结论与逐条 findings；未运行项标 `NOT_RUN`。
- 验证命令、环境与完成 Gate：使用 task-env Python 3.12.3 执行 `G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe -m pytest tests/core -q`；Review 通过、证据和 Task 状态核对后，才进入 Coordinator integration。
- 可直接转发给 Agent 的指令：

  > 请独立 Review HOST-CORE-1 固定 head `4af86abb374cfccf92de07d4e5b975dfbaf0dd2b`，worktree 为 `G:/CODEX/New Manga.workspace/worktrees/HOST-CORE-1`，分支 `codex/HOST-CORE-1-hostcontrol-handler`，基线 `ed79b76f9191f0a5ebb6932a53a992a33a274041`。重点核查 §5.7 envelope/session 失效、三拒绝码的零副作用与未调用 seam、普通 dispatcher 隔离、ref/签名语义不变及范围。只读实现，Review 输出到 `verification/HOST-CORE-1/dsh-review-r1.md`；不要改生产代码、契约或 `apps/**`。使用指定 Python 3.12.3 环境复跑 `python -m pytest tests/core -q`，给出 reviewed head、测试原始结果、findings 与明确结论；未跑项写 `NOT_RUN`。通过后交 Codex 做 Coordinator integration Gate，不要自行 merge 或 push。

## 风险与遗留

- 本次验证了 Core direct stdio 接收与生命周期，没有修改或验证 Rust/Tauri host issuer；这属于 `HOST-ISSUER-1` 范围。
- 当前 AC8 非作者 Review 与集成均 `NOT_RUN`；不能宣称 Task 已 `done`。
- 全量测试唯一 warning 是既有 `Image.Image.getdata` deprecation；本 Task 未改该用例。
