# SEC-FIX-PATH-ECHO-1 验收证据

## 范围与来源

- 基线：`f4bbc59c9e5cf9864ab0ab0e97277b826b9a0a5f`；分支：`codex/SEC-FIX-PATH-ECHO-1`。
- P19 提供的主仓复现脚本与 `raw/settings-path-roundtrip.*` 在主仓 checkout 中不存在。SEC-FIX Task 本身记录了原复现输出 `path_value_returned=true`；本目录的等价脚本在同一基线先复现，再在修复后复跑。
- 契约保持不变：Core 的 settings 响应投影脱敏；Tauri host 继续转发已安全的 Core 响应。

## AC 结果

| AC | 结果 | 证据 |
|---|---|---|
| AC1 | PASS | Core 全量/单节/写后投影会隐藏 OS 路径、路径字段值和路径型 section key；响应中的路径型 request ID 也封闭处理。写入值仍原样保存在 Core。 |
| AC2 | PASS | 合成绝对路径作为非法 `sfx.policy`、非法更新请求和路径型 request ID 输入；settings handler 错误及协议版本提前拒绝响应均不包含路径片段。 |
| AC3 | PASS | `test_settings_commands_redact_paths_in_every_section` 覆盖 12 个设置分类与 `sfx`，包含 Windows 绝对路径、UNC、POSIX 用户目录、相对 `*_path`、section key、request ID、两条命令读写、非法协议版本和错误。 |
| AC4 | PASS（按实测基线对比） | 四套件见下表。Task 记载前端基线 278；当前基线 commit 实测 285，前后均为 285 passed，差异 +7 在本修复前已存在。 |
| AC5 | PASS | 交付状态为 `in_review`；本文件、Handoff 与 Task Canonical Evidence 相互引用，SHA 按 worktree 磁盘字节计算。 |
| AC6 | PASS | `repro_settings_path_projection.py` 前后复跑：修复前 `path_value_returned=true`，修复后 `false`；原始输出见 `baseline/repro-before.log` 与 `repro-after.log`。 |

## 复现输出

修复前，脚本直接向 Core 发 `settings.update_section` 与 `settings.get`，不访问合成路径目标文件：

```text
OBSERVED path_value_returned=true synthetic_secret_returned=false file_io_attempted=false
REPRO_RESULT=FAIL
EXIT_CODE=1
```

修复后：

```text
WRITE_RESPONSE={"protocol": "new-manga.core", "version": {"major": 2, "minor": 3}, "request_id": "sec-fix-path-echo-1", "result": {"settings": {"ocr": {"path": "[redacted]"}}}, "error": null}
READ_RESPONSE={"protocol": "new-manga.core", "version": {"major": 2, "minor": 3}, "request_id": "sec-fix-path-echo-1", "result": {"settings": {"ocr": {"path": "[redacted]"}}}, "error": null}
OBSERVED path_value_returned=false synthetic_secret_returned=false file_io_attempted=false
REPRO_RESULT=PASS
EXIT_CODE=0
```

## 回归套件对比

| 套件 | 基线 | 修复后 | 结论 / 日志 |
|---|---:|---:|---|
| Core pytest (`tests/core`) | 535 passed / 0 skipped | 536 passed / 0 skipped | PASS；增加 1 个路径泄露反例。既有 Pillow 弃用 warning 不变。`baseline/core-pytest.log`、`core-pytest.log` |
| Rust source | 107 passed / 0 failed / 1 ignored | 107 passed / 0 failed / 1 ignored | PASS；`M2RC1_PYTHON=C:\Python314\python.exe`。`baseline/rust-source.log`、`rust-source-tests.log` |
| Packaged | 12 passed / 0 failed | 12 passed / 0 failed | PASS；`M2RC1_PACKAGED=1`，`M2RC1_PYTHON` / `M2RC1_SRC_ROOT` 未设置。`baseline/rust-packaged.log`、`rust-packaged-tests.log` |
| Frontend | 285 passed / 0 failed | 285 passed / 0 failed | PASS；Task 记载 278，但实际基线已是 285；本 Task 未改前端。`baseline/frontend-vitest.log`、`frontend-vitest.log` |

命令与环境：

- Core：`python -m pytest tests/core -q -p no:cacheprovider`；Python 3.14.6。
- Rust source：`$env:M2RC1_PYTHON='C:\Python314\python.exe'; cargo test --locked --manifest-path apps/desktop/src-tauri/Cargo.toml -- --skip packaged_sidecar_tests`。
- Packaged：`$env:M2RC1_PACKAGED='1'; cargo test --locked --manifest-path apps/desktop/src-tauri/Cargo.toml packaged_sidecar_tests -- --test-threads=1 --nocapture`。
- Frontend：`npm test -- --reporter=dot`；依 `package-lock.json` 执行 `npm ci` 后运行。
- Rust 两套件使用临时 `TAURI_CONFIG={"build":{"frontendDist":"target/host-test-frontend"}}` 指向 worktree `target` 下的空目录；Cargo 自动改写的 Tauri schema/permission 生成文件已恢复至基线。

## 环境边界与遗留

- 主仓当前 `doc/STATUS.md` 仍将 `ARCH-DOC-REBASELINE` 标为当前 Task，而 Plan 将本 Task 列为 READY。按禁止项未改 STATUS/PLAN；已在 Task 记录，交 Coordinator 核对。
- Rust 测试产生两个 `verification/P04/diagnostic_p22_*.jsonl` 未跟踪文件，位于本 Task 允许路径之外；保持原样且不纳入提交。
- Python/Node 测试临时目录被定向到 `verification/SEC-FIX-PATH-ECHO-1/tmp`，以限制写入范围。该目录中的临时输出未纳入交付提交。
