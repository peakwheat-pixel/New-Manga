# TASK-030 Codex 集成验证

日期：2026-09-16（Asia/Shanghai）

## 固定对象

- `base_commit=087da45590c84227e9695eb829669e9cee805ef2`
- `reviewed_head=c3f189396d9efdceb0e3e42ba7db62b25d77853a`
- `review_report_commit=dba26372dc63d4d23acfd809e7b646106693c230`
- `implementation_merge=a58ff84`
- `integration_commit=fef9dd3`
- Review 分支：`agent/deepseek/TASK-030-review`
- 作者分支：`agent/zcode/TASK-030-main-bootstrap-assembly`

## 集成方式

Codex 在 `G:/CODEX/New Manga` 的 `master` 上按协作协议 §6.6 串行执行：

1. `git merge --no-ff agent/zcode/TASK-030-main-bootstrap-assembly` → `a58ff84`，纳入 reviewed head `c3f1893` 及 Handoff。
2. `git merge --no-ff agent/deepseek/TASK-030-review` → `fef9dd3`，纳入 approved Review `dba2637`。
3. 在集成结果上以 Codex 修订提交 `a29f02e` 关闭 R-001～R-003、登记 D03/D07 数据根默认并修正 `app.py` 注释；未合并其他分支，未 push。

`integration_commit` 由 Codex 填写为 `fef9dd3`，不是 Review 报告代填。修订提交位于集成提交之后，不改变固定 reviewed head 的含义。

## 集成后验证

环境：Windows `win32 10.0.26200`；Python 3.12.3；PySide6 6.11.2；pytest 9.1.1；解释器
`G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe`；`QT_QPA_PLATFORM` 未设置，使用默认 Windows Qt，未使用 offscreen。

| 命令 | passed | skipped | failed | 退出码 |
|---|---:|---:|---:|---:|
| `PYTHONPATH=src G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe -m bootstrap.app --smoke-test` | — | — | — | 0 |
| `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe -m pytest tests/core/test_bootstrap.py -v` | 8 | 0 | 0 | 0 |
| `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe -m pytest tests/ui_shell -v` | 46 | 0 | 0 | 0 |
| `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe -m pytest tests -q -rs` | 382 | 6 | 0 | 0 |

全量 6 个 skip 均为 `openssl unavailable`：

- `tests/network/test_connection_tester.py:106`
- `tests/network/test_transport_tls.py:39`
- `tests/network/test_transport_tls.py:47`
- `tests/network/test_transport_tls.py:62`
- `tests/network/test_transport_tls.py:69`
- `tests/network/test_transport_tls.py:83`

## Review findings 与裁决落地

- **R-001 closed**：150% 实测 `1920×1061`，200% 实测 `1924×1062`；作者证据改为实测值并说明 1920×1080 显示器导致的可见范围限制，结论收窄为可见范围内未观察到错位；新增 125% 完整入口抓帧 `verification/TASK-030/dpi-highres-125pct.png`，实测 `1600×1000`。
- **R-002 closed**：清除 `doc/tasks/TASK-030.md` frontmatter 的预填 `decision` 字段。
- **R-003 closed**：`assemble_services` 对已打开连接包裹异常回收；迁移/装配失败回归测试通过；`main` 异常路径清理临时数据根。
- **裁决① closed**：D03 §18.1 与 D07 §33 登记 `%LOCALAPPDATA%/New Manga` 默认数据根，`NEWMANGA_DATA_ROOT`/`--data-root` 可覆盖；正式设置 UI/迁移仍为 TASK-022 范围。
- **裁决② closed**：`app.py` 顶层 `QQuickWindow` 注释改为强类型包装与 `_grab_and_quit` rewrap 第二道保险的准确表述。

## AC 与范围

- AC1～AC5：集成后代码、测试及证据成立；AC4 的 150%/200% 截图如实保留显示器边界，不将受限画面声称为完整窗口验证。
- AC6：**PASS**；approved Review 已合入，四条集成验证命令均退出 0，Task 可置 `done`。
- 未执行项继续记录：真实 `%LOCALAPPDATA%` 数据根启动 `NOT_RUN`；多显示器、键盘焦点全量、原生文件对话框 `NOT_RUN`；工作台/阅读器/设置真实内容 `N/A`；性能 `N/A`。
- 范围检查：未修改 `src/domain/**`、Schema/migration、依赖清单、`src/ui` 其他文件、TASK-012 已审实现、TASK-013/TASK-015 或其他冻结 Task、AGENTS；未 push。
