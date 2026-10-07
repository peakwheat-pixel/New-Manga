---
task_id: M2-DERIVED-GC-2
reviewer: Codex（非作者）
reviewed_head: 8291f33652e32175e44a8b282318604136673d96
evidence_tip: 83d8d693e2ef5ea5f88044f34b153ff104e94e2b
decision: changes_requested
findings: 1
---

## Verdict：changes_requested

### F-01 — P1：Unicode 空白仍能绕过规范 schema 比较

ASCII 反例 `TEXTN OTNULL` 已由折叠空白比较拒绝。[对应测试](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/tests/m2_resource_channel/test_catalog_authority.py:924>) 建立了完整三表，并断言专属 schema 不匹配错误。

但比较仍用 Python `str.split()`：[规范化常量](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/src/infrastructure/resource_channel/catalog_store.py:108>)、[实际比较](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/src/infrastructure/resource_channel/catalog_store.py:386>)。Python 会把 NBSP（U+00A0）当作空白；SQLite tokenizer 则把 UTF-8 中的高位字节作为标识符字符。因此将 `derived_root TEXT NOT NULL` 写成 `derived_root TEXT NOT\u00A0NULL`，Python 归一化后仍与规范文本相等，但 SQLite 不会把 `NOT\u00A0NULL` 识别为 `NOT NULL` 约束。SQLite 的列定义允许多词类型名，且类型名与列约束分开解析。[SQLite tokenizer 源码](https://www.sqlite.org/src/doc/c5e2de1d24d34589/src/tokenize.c)、[CREATE TABLE 文档](https://www.sqlite.org/lang_createtable.html)

该空表可通过当前布局检查：它只比较列名和主键位置，不核对 `NOT NULL` 属性。[布局检查](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/src/infrastructure/resource_channel/catalog_store.py:263>) 因此“归一化全文相等 ⇒ 语义等价”的论证尚未闭合。

建议在比较前拒绝非 ASCII DDL，或只折叠 SQLite 认可的 ASCII 空白，并增加 NBSP 反例用例。

### 其余核查

- **证据绑定：通过。** pytest 日志标题和 HEAD 均为 `8291f336`，记录 `1940 passed, 1 skipped`、`EXIT=0`。[pytest 日志](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/verification/M2-DERIVED-GC-2/raw/pytest-full.log:1>) packaged 日志也绑定同一 HEAD，记录 NSIS 构建成功和定向回归 162 项通过；runner 的唯一失败仍是 `CS-L1`，整体 `GATE: FAIL`、`EXIT=1`。完整安装包 SHA 由归档的 gate JSON 与构建日志互相对应。[第九轮构建日志](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/verification/M2-DERIVED-GC-2/raw/packaged-ac5-run/ninth-round-build-and-run.log:686>) [gate.json](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/verification/M2-DERIVED-GC-2/raw/packaged-ac5-run/ninth-run-artifacts/M2-AC5/raw/cleanstart-gate.json:39>)
- **范围：通过。** `a4f80bf0..83d8d693` 的差量仅涉及允许的 `catalog_store.py`、`test_catalog_authority.py`、本 Task 的 review/handoff/verification 文件；`apps`、`src/apps` 和 `packaging` 零差量。

本轮只执行了只读 `git show`、`git diff --name-status` 和路径差量核查；未运行测试或打包，也未写入文件。下一步建议修复 Unicode 空白绕过并补上反例，再提交复核。