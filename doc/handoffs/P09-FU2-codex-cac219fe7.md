---
task_id: P09-FU2
author: Codex
recipient: DeepSeek Harness
base_commit: 9fe6ac5cd116474de1006b4ab4b1e5341b71cf41
delivery_head: cac219fe7d5df272d51e105d0905b272db2bf7e2
status: in_review
---

# Handoff：P09-FU2

## 交付结果

实现提交 `cac219fe7d5df272d51e105d0905b272db2bf7e2` 已固定在分支 `codex/P09-FU2-import-ipc-runtime`。Core 现在注册并装配 `ImportPages`，用 Core 内部的 host grant seam 校验 opaque 来源引用，以既有 P09 图片/PDF importer 导入；importer、library 和 SQLite 实现均未修改。

变更集中在：

- `src/bootstrap/core_service.py`、`src/bootstrap/core_assembly.py`
- `src/application/resource_channel/__init__.py`、`dto.py`
- `src/infrastructure/resource_channel/handle_resolver.py`、`import_source_refs.py`
- `tests/core/test_p09_fu2_import_pages.py` 和既有 Core 协议版本断言
- `verification/P09-FU2/**`

AC1–AC8 的 Owner 验证通过；AC9 固定实现 head、测试和 Handoff 已完成。非作者 Review 与 Coordinator 集成未运行，Task 保持 `in_review`。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 | 通过真实 `serve_forever` stdio 发送 `ImportPages` | task-env Python 3.12.3；`cac219fe7d5df272d51e105d0905b272db2bf7e2` | PASS；Core exit 0，response `error: null`，命令结果含 imported Page | `verification/P09-FU2/logs/ac1-importpages-stdio.txt` |
| AC2 | 六类核心 REF 拒绝及 session、文件、reparse、identity、size、digest 拒绝；逐项比较 Page/库与 Managed Storage 快照 | 同上 | PASS；12 cases passed，错误引用零库写/零 Managed Storage 文件写，来源哈希保持不变 | `verification/P09-FU2/logs/ac2-ref-rejections-zero-side-effects.txt` |
| AC3 / AC5 / AC6 | 既有图片/PDF importer 接线、页 hash/尺寸/序、重复、Unicode、损坏/加密、中断 | 同上 | PASS；9 cases passed；P09 importer 只读复用 | `verification/P09-FU2/logs/ac3-importer-and-report-cases.txt`、`verification/P09-FU2/import-report-sample.json` |
| AC4 | `user-source` Core-only scope、目录直接子项与路径回退拒绝 | 同上 | PASS；3 cases passed | `verification/P09-FU2/logs/ac4-user-source-scope.txt` |
| AC1–AC7 / regression | `& 'G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe' -m pytest tests/core -q` | 同上 | PASS；377 passed，0 failed，0 skipped，1 unrelated Pillow deprecation warning；exit 0 | `verification/P09-FU2/logs/pytest-tests-core.txt` |
| AC8 | 核对 host issuer 待办与注入 seam 边界 | 同上 | PASS；issuer 未实现；seam 仅为 Core 内部方法；测试 key/signature 未入证据 | `verification/P09-FU2/host-issuer-and-test-seam.md` |
| AC7 / resource | 核对 linked worktree 和既有 Python 环境处置 | 同上 | PASS；`PRESERVE_REFERENCED`；0 删除、0 迁移、0 归档；主仓未写 | `verification/P09-FU2/resource-manifest.json` |
| AC9 | 固定 head、保存 Handoff 并提交 | 同上 | PARTIAL；实现提交与本 Handoff 已提交；非作者 Review、Coordinator 集成 `NOT_RUN` | 本文件；Task `doc/tasks/P09-FU2.md` |

完整命令、环境和结果索引见 `verification/P09-FU2/test-run-record.md`。全量测试的唯一 warning 是既有 `tests/core/test_rc4_stdio_render_preview.py` 使用 Pillow `Image.getdata` 的弃用提示。

## 接收方式

- 仓库/worktree：`G:/CODEX/New Manga.workspace/worktrees/P09-FU2-IMPORT-IPC-RUNTIME`
- Branch：`codex/P09-FU2-import-ipc-runtime`
- Base：`9fe6ac5cd116474de1006b4ab4b1e5341b71cf41`
- 固定 review head：`cac219fe7d5df272d51e105d0905b272db2bf7e2`
- 复现命令：`& 'G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe' -m pytest tests/core -q`
- 测试没有外部数据；fixture 自建在 pytest `tmp_path`。未安装依赖。
- Reviewer 请独立检查完整 diff、引用安全边界、报表与 importer 语义，并将 Review 记录提交到 `verification/P09-FU2/`；之后由 Coordinator 决定集成。

## 下一任务建议（必填）

- Task ID / 标题：P09-FU2 AC9 — 独立 Review 与 Coordinator 集成验证。
- 推荐 Agent / Reviewer：DeepSeek Harness 独立 Review；Codex Coordinator 后续集成。Owner 与 Reviewer 不同。
- 推荐原因与前置依赖：P09-FU2 AC1–AC8 Owner 证据已齐，Review 固定在实现 head；集成前必须先独立审查通过。
- Recovery point：`G:/CODEX/New Manga.workspace/worktrees/P09-FU2-IMPORT-IPC-RUNTIME`，branch `codex/P09-FU2-import-ipc-runtime`，base `9fe6ac5cd116474de1006b4ab4b1e5341b71cf41`，head `cac219fe7d5df272d51e105d0905b272db2bf7e2`。如需隔离 Review worktree，待 Codex 创建。
- 允许修改路径：Reviewer 只读实现 worktree；Review 文档限 `verification/P09-FU2/**`。Coordinator 集成须在独立授权的集成工作区进行。
- 禁止范围与新增授权条件：不得修改冻结契约、importing/library/sqlite、Schema、host issuer；不得 push。集成须服从当前 Coordinator 授权与允许路径。
- 交付物：固定 head 的 Review 文档、Coordinator 集成结果与集成后 `pytest tests/core -q` 日志；未跑项标 `NOT_RUN`/`BLOCKED`。
- 验证命令、环境与完成 Gate：task-env Python 3.12.3 下运行 `& 'G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe' -m pytest tests/core -q`；Review 通过且集成后回归通过后，AC9 才可 PASS。
- 可直接转发给 Agent 的指令：请在 `G:/CODEX/New Manga.workspace/worktrees/P09-FU2-IMPORT-IPC-RUNTIME` 独立审查 P09-FU2 固定 head `cac219fe7d5df272d51e105d0905b272db2bf7e2`（base `9fe6ac5cd116474de1006b4ab4b1e5341b71cf41`，branch `codex/P09-FU2-import-ipc-runtime`）。完整检查 diff、任务 AC、契约 rev 2.2、P09 importer 接入和错误引用零副作用证据；只将 Review 文档写入 `verification/P09-FU2/**`，不得改实现、冻结契约、importing/library/sqlite、Schema 或 host issuer。Coordinator 后续负责集成及集成后回归。若运行测试，请用 `& 'G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe' -m pytest tests/core -q` 并保存原始日志、退出码；逐项记录 PASS/FAIL/BLOCKED/NOT_RUN。

## 风险与遗留

- **Tauri host issuer 待办**：仍需独立 Task 实现用户显式选择后的签发、受信 host→Core grant 注册、HMAC key 生命周期、host session 结束时撤销与进程重启清理。引用不能传给 React/WebView，路径不能进入 JSON-RPC。细项见 `verification/P09-FU2/host-issuer-and-test-seam.md`。
- 测试签发通过 `_register_import_source` / `_revoke_import_source` 注入 seam 和测试专用 key；它们不是 JSON-RPC 命令，不构成 host issuer 实现。
- 中断仅通过 `CoreServiceServer(import_cancelled=...)` 回调验证 importer 的 pending/已提交结果；契约没有取消 `ImportPages` command，UI/host 取消接线仍待定。
- 既有 P09 importer 需要完整 bytes；本次未添加大媒体阈值，保留其原有内存行为。
- 未执行 Review、主线集成或集成后回归；未 push、未 merge。工作区应保留供 Reviewer/Coordinator 使用。
