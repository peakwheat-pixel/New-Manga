# P16 授权范围审计

基线：`093430c75a46d28ed759ec646039bf2f55e3d429`；分支：`codex/P16-reader-export-core`；工作目录：`G:/CODEX/New Manga.workspace/worktrees/P16-READER-EXPORT-CORE`。

## 允许的变更根

生产代码/测试只在 `src/application/reading/**`、`src/application/export/{__init__.py,ports.py,service.py}`、`src/infrastructure/export/**`、`src/bootstrap/core_service.py`、`src/bootstrap/core_assembly.py` 与 `tests/core/**`。没有改 resource_channel 或 sqlite schema/migration。Task 与 Handoff/验证材料分别限于 P16 授权的 `doc/tasks/P16.md`、`doc/handoffs/P16-*.md`、`verification/P16/**`。

提交后须用 `git diff --name-only 093430c75a46d28ed759ec646039bf2f55e3d429..HEAD` 逐条核对本文件列出的范围。最终清单若有越界路径，Task 不得关闭。

## 明确排除项

- `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`、`doc/contracts/P11_LONG_TASK_LIFECYCLE_CONTRACT.md`：未修改，rev 2.1 冻结契约只读。
- `src/application/export/pdf_qt.py`、`tests/reading_export/**`：未修改、未执行。
- `src/infrastructure/export/**` 无 Qt/PySide6/PyQt import；无 Tauri/Rust/React/WebView issuer 实现。
- 未改 Schema/migration、未增加第三方依赖、未触碰用户数据；未 push、merge、reset、stash。
- main repo 是只读：交付前后 `git -C "G:/CODEX/New Manga" status --porcelain --untracked-files=no` 必须与任务开始时既有 19 条 tracked dirty 项一致。

`doc/tasks/P16.md` 的 Canonical Evidence 表、`verification/P16/resource-manifest.json` 记录提交后的文件 SHA-256 与工作区状态；实际命令输出见最终交付回复及 Handoff。
