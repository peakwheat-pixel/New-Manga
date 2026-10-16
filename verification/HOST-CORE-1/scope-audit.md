# HOST-CORE-1 范围审计

- 固定实现 head：`4af86abb374cfccf92de07d4e5b975dfbaf0dd2b`
- 执行基线：`ed79b76f9191f0a5ebb6932a53a992a33a274041`
- 授权生产代码路径：`src/bootstrap/core_service.py`
- 其余实现 diff：仅 `tests/core/**`（HostControl 用例与协议 minor 2.3 的既有测试断言）。
- `src/bootstrap/core_assembly.py` 未改：该装配已经创建进程内 import/export grant registries。
- `doc/contracts/**`、`apps/**`、Schema/migration、依赖、`src/application/**`、`src/infrastructure/**` 均未改。
- Owner 测试：指定 Python 3.12.3 task-env 执行 `python -m pytest tests/core -q`，`393 passed / 0 failed / exit 0`。
- Handoff / verification / Task 文档均限于本任务授权目录。
- 主仓只读；未执行 push、merge、reset、stash，也未清理或迁移 worktree、主仓 dirty 文件或用户数据。
