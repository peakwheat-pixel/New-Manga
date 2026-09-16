# TASK-031 集成验证

日期：2026-09-16（Asia/Shanghai）

固定对象：

- `base_commit=29b146f76b46682c6e9de3c40631fd7a5debed16`
- `reviewed_head=c67a105c4907be07166fe319c77f56ac4cc5f2f0`
- `review_report_commit=0509003e4df0ca84428d61faf32dd16a70168d30`
- `implementation_merge=0b44b83bec8df8efad52d69f72c7aad2237e530b`
- `integration_commit=e9d5185259ffa175b64d67d5ac00befadc6db643`

## 集成方式

Codex 在 `G:/CODEX/New Manga` 的 `master` 上串行执行：

1. `git merge --no-ff agent/codex/TASK-031-production-import-adapters` → `0b44b83`。
2. `git merge --no-ff agent/deepseek/TASK-031-review` → `e9d5185`，纳入 approved Review `0509003`。

Review 固定审查的实现为 `c67a105`；按用户要求关闭的三个非阻塞 P2 在 `d4fe993` 中以最小增补测试/注解/fallback 收口，未改变应用 Protocol、Schema、入口或其他 Task。未合并其他分支，未 push。

## 集成后主线复验

环境：Windows `win32`；Python `3.12.3`；PySide6 `6.11.2`；pytest `9.1.1`；解释器 `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe`；`QT_QPA_PLATFORM` 未设置，使用默认 Windows Qt 平台，未使用 offscreen。

| 命令 | passed | skipped | failed | 退出码 |
|---|---:|---:|---:|---:|
| `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe -m pytest tests/library/test_production_adapters.py -q` | 8 | 0 | 0 | 0 |
| `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe -m pytest tests/library -q` | 40 | 0 | 0 | 0 |
| `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe -m pytest tests/ui_shell -v` | 46 | 0 | 0 | 0 |
| `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe -m pytest tests -q -rs` | 376 | 6 | 0 | 0 |

全量 6 个 skip：

- `tests/network/test_connection_tester.py:106`
- `tests/network/test_transport_tls.py:39`
- `tests/network/test_transport_tls.py:47`
- `tests/network/test_transport_tls.py:62`
- `tests/network/test_transport_tls.py:69`
- `tests/network/test_transport_tls.py:83`

以上 6 项共同原因均为 `openssl unavailable`；passed 与 skipped 已分列记录。

## AC 与 Review finding

- AC1：PASS；Qt 生产解码器专测覆盖有效/损坏/未知 format。
- AC2：PASS；D03 original 路径、Hash 校验、不可覆盖 publish 与失败清理已验证。
- AC3：PASS；生产适配器驱动 `ImportImagesUseCase`，copy 成功后才生成 Page，copy failure 生成 `COPY_FAILED` 且零 Page。
- AC4：PASS；作者 merge、Review merge、固定验证和本记录均已入库，且范围检查无禁止路径。
- R-001：**closed**；新增真实生产 copy-failure 端到端用例。
- R-002：**closed**；注解改为 `ManagedFileStoragePort`。
- R-003：**closed**；安全 MIME fallback 为 `application/octet-stream`，有回归测试。

## 范围与未执行项

`src/ui/qml/Main.qml`、`src/bootstrap/app.py`、`src/application/**`、`src/domain/**`、`src/ports/**`、Schema/migration、依赖清单和 TASK-012 已审实现均未修改；TASK-030、TASK-013、TASK-015 及其他冻结 Task 未释放/未启动。

- TASK-030 真实入口 smoke、SQLite 真实导入探针、DPI 截图：`BLOCKED`/`NOT_RUN`，不属于 TASK-031 集成范围。
- 性能/大图批量：`N/A`，本 Task 无性能 AC。
