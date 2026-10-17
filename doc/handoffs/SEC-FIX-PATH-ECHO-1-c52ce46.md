---
task_id: SEC-FIX-PATH-ECHO-1
author: Codex
recipient: DeepSeek Harness
base_commit: f4bbc59c9e5cf9864ab0ab0e97277b826b9a0a5f
delivery_head: c52ce4695802a06fde8f4e08f2d96a8cecfd855d
status: in_review
---

# Handoff：SEC-FIX-PATH-ECHO-1

## 交付结果

实现提交：`cd78a333577365466726e1f32d3ef95be22d7324`（`fix(settings): redact paths from IPC projection`）、`5b9f6c422df5cdb601522c91cb447702a2e78efc`（`fix(settings): preserve non-string path fields`）和 `c52ce4695802a06fde8f4e08f2d96a8cecfd855d`（`fix(settings): redact protocol rejection request ids`）。最终提交包含 Core 修复、反例测试及针对最终代码复跑的四套件日志。Task 与 Handoff 的文档更新不改变 `delivery_head`。

修复位于 Core 公共 settings 输出投影：`src/bootstrap/core_service.py:340-379` 检测并遮蔽 OS 路径和路径类字段，同时保留 `file: false` 等非路径类型；`handle_settings_get`（`:1250-1267`）及 `handle_settings_update_section`（`:1269-1309`）在返回前使用该投影。通用 dispatcher 在协议校验前为 settings 命令投影路径型 `request_id`（`:2644-2655`），协议错误和 settings 成功/错误 envelope 使用安全 ID（`:2726-2743`、`:3014-3061`），settings 错误消息也经过投影（`:3030`）。写入仍保存原始值，脱敏只作用于 IPC 响应。Tauri `settings_get` / `settings_update_section` 在 `apps/desktop/src-tauri/src/main.rs:519-550` 与 `library_bridge.rs:1665-1685` 将 Core 结果透传，不需要 host 修改。

| AC | 结果 | 证据 |
|---|---|---|
| AC1 | PASS | 响应中的 Windows、UNC、POSIX 路径、用户目录片段、路径类字段值、路径型 section key 与路径型 request ID 已遮蔽。 |
| AC2 | PASS | 非法 `sfx.policy`、非法 section 与非法 protocol 的错误响应均不包含合成路径；两命令的 protocol 错误也遮蔽路径型 `request_id`。 |
| AC3 | PASS | `tests/core/test_core_service_settings.py::test_settings_commands_redact_paths_in_every_section` 覆盖 13 个 section 的读写、全量读取、路径形式、相对 `*_path`、动态键、request ID、非法协议版本、错误及存储值保留。 |
| AC4 | PASS（按实际基线对比） | Core 535→536 passed；Rust source 107/0/1→107/0/1；packaged 12/0→12/0；Frontend 285/0→285/0。Task 记载前端 278，但同一基线实测 285，修复前后没有回归。 |
| AC5 | PASS | 本 Handoff 与验证日志已固定；Task Canonical Evidence pin 在后续纯文档提交收尾并在交 Reviewer 前完成；Task 状态为 `in_review`。 |
| AC6 | PASS | 等价复现脚本修复前 `path_value_returned=true`，修复后 `false`；两个输出均归档。 |

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC3 反例 | `python -m pytest tests/core/test_core_service_settings.py::test_settings_commands_redact_paths_in_every_section -q -p no:cacheprovider` | Python 3.14.6；修复提交 | 1 passed | `verification/SEC-FIX-PATH-ECHO-1/counterexample.log` |
| AC6 修复前复现 | `python verification/SEC-FIX-PATH-ECHO-1/repro_settings_path_projection.py` | 基线 `f4bbc59c9e5cf9864ab0ab0e97277b826b9a0a5f`；测试退出码 1 为预期缺陷证据 | `path_value_returned=true` | `verification/SEC-FIX-PATH-ECHO-1/baseline/repro-before.log` |
| AC6 修复后复现 | 同上 | `c52ce4695802a06fde8f4e08f2d96a8cecfd855d` | `path_value_returned=false`，退出码 0 | `verification/SEC-FIX-PATH-ECHO-1/repro-after.log` |
| AC4 Core | `python -m pytest tests/core -q -p no:cacheprovider` | Python 3.14.6；基线 / 修复提交 | 535 / 536 passed，0 skipped | `baseline/core-pytest.log`、`core-pytest.log` |
| AC4 Rust source | `$env:M2RC1_PYTHON='C:\Python314\python.exe'; $env:TAURI_CONFIG='{"build":{"frontendDist":"target/host-test-frontend"}}'; cargo test --locked --manifest-path apps/desktop/src-tauri/Cargo.toml -- --skip packaged_sidecar_tests` | 显式设置 `M2RC1_PYTHON`；临时 `frontendDist` 位于 worktree 的 `target` | 两次均 107 passed / 0 failed / 1 ignored | `baseline/rust-source.log`、`rust-source-tests.log` |
| AC4 packaged | 清除 `$env:M2RC1_PYTHON` / `$env:M2RC1_SRC_ROOT`；设置 `$env:M2RC1_PACKAGED='1'` 和相同 `TAURI_CONFIG`；`cargo test --locked --manifest-path apps/desktop/src-tauri/Cargo.toml packaged_sidecar_tests -- --test-threads=1 --nocapture` | Rust packaged 模式；`M2RC1_PYTHON`、`M2RC1_SRC_ROOT` 未设置 | 两次均 12 passed / 0 failed | `baseline/rust-packaged.log`、`rust-packaged-tests.log` |
| AC4 frontend | `npm test -- --reporter=dot` | `npm ci` 按锁文件安装；未改前端源码 | 两次均 285 passed / 0 failed | `baseline/frontend-vitest.log`、`frontend-vitest.log` |

Core 修复前，等价脚本输出：

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

Task 指定的主仓只读源文件 `verification/P19-AC3-1/repro_settings_path_roundtrip.py` 与 `raw/settings-path-roundtrip.*` 在当前主仓 checkout 不存在。`baseline/repro-before.log` 是同一修复等价脚本在原基线上的实际复现；原始发现的 `path_value_returned=true` 也保留在 Task 来源记录中。

## 接收方式

- 仓库：`G:/CODEX/New Manga`
- 分支 / worktree：`codex/SEC-FIX-PATH-ECHO-1` / `G:/CODEX/New Manga.workspace/worktrees/SEC-FIX-PATH-ECHO-1`
- 基线：`f4bbc59c9e5cf9864ab0ab0e97277b826b9a0a5f`
- 实现 head：`c52ce4695802a06fde8f4e08f2d96a8cecfd855d`
- 复现命令：`python verification/SEC-FIX-PATH-ECHO-1/repro_settings_path_projection.py`
- Review 时固定 `reviewed_head` 为实现提交；文档提交只追加 Task/Handoff/Canonical Evidence，不修改实现。

## 下一任务建议（必填）

- Task ID / 标题：SEC-FIX-PATH-ECHO-1 / 独立 Review 与 AC 证据核对。
- 推荐 Agent / Reviewer：DeepSeek Harness。
- 推荐原因与前置依赖：Task 已指定 DeepSeek Harness 为独立 Reviewer；Review 必须与 Codex 实现 Owner 分离。依赖为本交付 `delivery_head` 与本 Handoff / Canonical Evidence。
- Recovery point：仓库 `G:/CODEX/New Manga`；branch `codex/SEC-FIX-PATH-ECHO-1`；worktree `G:/CODEX/New Manga.workspace/worktrees/SEC-FIX-PATH-ECHO-1`；base `f4bbc59c9e5cf9864ab0ab0e97277b826b9a0a5f`；实现 head `c52ce4695802a06fde8f4e08f2d96a8cecfd855d`。
- 允许修改路径：Review 只读；仅 Review 报告可写入 `verification/SEC-FIX-PATH-ECHO-1/`。
- 禁止范围与新增授权条件：不改实现、契约、Schema、依赖、STATUS、PLAN 或用户数据；发现需要改实现时报告 finding，不在 Review 中直接修复。
- 交付物：按 `doc/templates/REVIEW.md` 提交固定 `base_commit` / `reviewed_head` 的独立 Review，核实 Core 与 host 边界、AC1–AC6、磁盘 SHA 与完整测试输出。
- 验证命令、环境与完成 Gate：复跑 targeted pytest 与等价 repro；检查 Task Canonical Evidence 所列 `git cat-file -e <commit>:<path>` 和 `Get-FileHash -Algorithm SHA256`；仅在无未解决 finding 且所有 pin/复现输出匹配时标记 approved。
- 可直接转发给 Agent 的指令：

  > 请对 Task `SEC-FIX-PATH-ECHO-1` 做独立只读 Review。仓库 `G:/CODEX/New Manga`，分支 `codex/SEC-FIX-PATH-ECHO-1`，worktree `G:/CODEX/New Manga.workspace/worktrees/SEC-FIX-PATH-ECHO-1`；固定 base `f4bbc59c9e5cf9864ab0ab0e97277b826b9a0a5f`、实现 head `c52ce4695802a06fde8f4e08f2d96a8cecfd855d`。核对 `src/bootstrap/core_service.py` 的 Core 投影覆盖成功和错误响应、协议校验前 request ID 投影、读写全量/分节，核对 host 透传路径，审阅 `tests/core/test_core_service_settings.py` 反例及 `verification/SEC-FIX-PATH-ECHO-1/` 中复现和四套件日志、Task Canonical Evidence 的磁盘 SHA 与树对象。按 `doc/templates/REVIEW.md` 写报告，只能写 `verification/SEC-FIX-PATH-ECHO-1/`；不要改实现、契约、Schema、依赖、STATUS 或 PLAN。复跑 targeted pytest 和等价复现，记录固定 reviewed_head、命令、结果及 findings；无未解决问题且 pin 一致时才建议 `approved`。

## 风险与遗留

- 脱敏只改变 IPC 投影，不改持久化设置；调用方仍可通过业务 Core 内部配置使用存储路径。
- Task 来源指定的原始 P19 复现脚本与 raw 输出在当前主仓不存在；以本 Task 的同基线等价复现作为可执行证据。
- Rust source 测试在 worktree 的 `verification/P04/` 生成四个未跟踪 diagnostic JSONL，且测试临时目录保留在 `verification/SEC-FIX-PATH-ECHO-1/tmp/`；没有清理这些文件，也未纳入提交。测试自动改写的 Tauri schema/permission 生成文件已恢复。
- 首次 Rust source 尝试因 Tauri `frontendDist` 缺失失败，随后使用 worktree `target/host-test-frontend` 临时覆盖配置并通过；阻塞日志与通过日志均保留。
