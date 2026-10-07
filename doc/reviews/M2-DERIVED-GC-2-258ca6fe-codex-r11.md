---
task_id: M2-DERIVED-GC-2
reviewer: Codex（非作者）
reviewed_head: 258ca6fe45ae75e4165b6ba5624e0c3a1bb7669e
evidence_tip: dc0bb4841908e0c3746b5bb623e190920d2cd61c
decision: approve
findings: 0
---

**Verdict：approve**

1. **NBSP 反例：已闭合。** 新用例建立三张已知空表，并断言初始化抛出 typed error。[测试](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/tests/m2_resource_channel/test_catalog_authority.py:979>) 中的 `derived_root TEXT NOT NULL` 含 U+00A0；[实现](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/src/infrastructure/resource_channel/catalog_store.py:396>) 先判断 `not table_sql.isascii()`，短路后才运行规范化比较，因此 NBSP 路径会被拒绝。SQLite tokenizer 将五种 ASCII 字符作为空白起始字符，并将高位字节归为标识符字符；这支持本次拒绝边界。[SQLite tokenizer 源码](https://www.sqlite.org/src/doc/c5e2de1d24d34589/src/tokenize.c)

   测试断言匹配的是通用 schema 拒绝消息，并未单独标记由 `isascii()` 分支触发；分支顺序由代码确认。测试的表集合断言也没有单独检查行数，但当前执行流在只读复核失败后、打开可写 catalog 连接之前就退出，故该路径不会写入 catalog。

2. **规范化等价性：接受。** 非 ASCII DDL 先拒绝，排除了 Unicode 空白和 Unicode `lower()` 映射；随后正则只折叠 SQLite 使用的五种 ASCII 空白，ASCII `lower()` 只处理大小写差异。[规范化代码](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/src/infrastructure/resource_channel/catalog_store.py:118>) 对边界保留；注释、引号和其他结构字符仍会导致全文不等。未发现可误放行的构造。

3. **证据绑定：通过。** pytest 日志标题和 HEAD 都是 `258ca6fe`，记录 `1941 passed, 1 skipped, EXIT=0`。[pytest 日志](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/verification/M2-DERIVED-GC-2/raw/pytest-full.log:1>) packaged 日志同样绑定该 HEAD；sidecar、NSIS 构建及 163 项定向回归均记录成功，安装包 SHA 与归档 `gate.json` 一致。[构建日志](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/verification/M2-DERIVED-GC-2/raw/packaged-ac5-run/tenth-round-build-and-run.log:4>) [gate.json](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/verification/M2-DERIVED-GC-2/raw/packaged-ac5-run/tenth-run-artifacts/M2-AC5/raw/cleanstart-gate.json:4>) runner 仍记录唯一 `CS-L1` 失败、整体 `GATE: FAIL`；这仍是 F-07 已登记的独立债务，不计为本轮回修通过。

4. **范围：通过。** `8291f336..dc0bb484` 的差量限于允许的 `catalog_store.py`、`test_catalog_authority.py`、本 Task 的 review、handoff 与 verification 文件；`apps`、`src/apps`、`packaging` 零差量。

本轮只读检查了 `git show`、`git diff --name-status` 和路径差量；未运行测试或打包。建议下一步由 Codex 按 AC6 进入集成验证，并继续保留 `CS-L1` 独立债务记录。