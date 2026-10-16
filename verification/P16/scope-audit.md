# P16 授权范围审计

基线：`093430c75a46d28ed759ec646039bf2f55e3d429`；分支：`codex/P16-reader-export-core`；工作目录：`G:/CODEX/New Manga.workspace/worktrees/P16-READER-EXPORT-CORE`。

## 允许的变更根

生产代码/测试只在 `src/application/reading/**`、`src/application/export/{__init__.py,ports.py,service.py}`、`src/infrastructure/export/**`、`src/bootstrap/core_service.py`、`src/bootstrap/core_assembly.py` 与 `tests/core/**`。没有改 resource_channel 或 sqlite schema/migration。Task 与 Handoff/验证材料分别限于 P16 授权的 `doc/tasks/P16.md`、`doc/handoffs/P16-*.md`、`verification/P16/**`。

最终 `git diff --name-only 093430c75a46d28ed759ec646039bf2f55e3d429..HEAD` 预期清单如下；Owner 交付后逐条核验，Task/Handoff/manifest 三项由文档提交补入：

```text
src/application/export/__init__.py
src/application/export/service.py
src/application/reading/ports.py
src/application/reading/service.py
src/bootstrap/core_assembly.py
src/bootstrap/core_service.py
src/infrastructure/export/__init__.py
src/infrastructure/export/jobs.py
src/infrastructure/export/qt_free.py
src/infrastructure/export/target_refs.py
tests/core/test_core_detect.py
tests/core/test_core_service.py
tests/core/test_core_service_retype.py
tests/core/test_core_service_settings.py
tests/core/test_p13_run_runtime.py
tests/core/test_p16_reader_export.py
tests/core/test_page_catalog_modes.py
tests/core/test_page_nav_projection.py
tests/core/test_page_resource_resolve.py
doc/tasks/P16.md
doc/handoffs/P16-codex-e2c07fa9.md
verification/P16/ac-matrix.md
verification/P16/ac3-target-ref-matrix.md
verification/P16/host-issuer-todo.md
verification/P16/py-compile.log
verification/P16/pytest-p16.log
verification/P16/pytest-tests-core.log
verification/P16/resource-manifest.json
verification/P16/scope-audit.md
```

该清单每条路径均在冻结 allowlist；Task/Handoff/manifest 是 owner 交付记录，不扩大产品实现范围。最终实际命令输出以交付回复为准。

## 明确排除项

- `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`、`doc/contracts/P11_LONG_TASK_LIFECYCLE_CONTRACT.md`：未修改，rev 2.1 冻结契约只读。
- `src/application/export/pdf_qt.py`、`tests/reading_export/**`：未修改、未执行。
- `src/infrastructure/export/**` 无 Qt/PySide6/PyQt import；无 Tauri/Rust/React/WebView issuer 实现。
- 未改 Schema/migration、未增加第三方依赖、未触碰用户数据；未 push、merge、reset、stash。
- main repo 是只读：交付前后 `git -C "G:/CODEX/New Manga" status --porcelain --untracked-files=no` 必须与任务开始时既有 19 条 tracked dirty 项一致。

`doc/tasks/P16.md` 的 Canonical Evidence 表、`verification/P16/resource-manifest.json` 记录提交后的文件 SHA-256 与工作区状态；实际命令输出见最终交付回复及 Handoff。
