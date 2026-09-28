# STALE ARCHIVE（r1 前存档，R2-03）

本目录是 M2-AC1 **DSH r1 之前**的一次 skip-build gate 运行存档（2026-09-28 早期）。

它已被 `verification/M2-AC1/e2e-gate-full/`（r1 返修后、完整构建版、45 场景）**取代**：

- 本存档的 gate JSON 为**旧格式**：无顶层 `implementation_commit` / `runner_executable` 字段；
- `EVN-python` / `EVN-python-resolved` 场景记录的是 PATH 上系统 Python 3.14.6（工具链探测），
  不是 gate runner 解释器——该歧义由 F-005 修复（`EVN-runner-python`）消除，本存档保留旧记录仅作历史；
- 本存档**不含** F-001/F-002/F-004 的 4 个新增断言场景（36 场景 vs 终版 45 场景）。

勿引用本存档作为当前验收证据；请引用 `e2e-gate-full/`。

另：r1 前通过版全仓日志（1322 passed / EXIT 0，本文件被重采覆盖前的版本）可用 `git show a74ce105:verification/M2-AC1/pytest-full-suite.log` 取回。
