---
task_id: P09-AC3-DELETE-HARDEN-1
author: dsh
recipient: Codex
base_commit: a04e4ea78d5b33a0f91efcdc06b396391c4b165e
delivery_head: 1878f0b126e8a0e2603570f9b2009d8b70a259f1
status: in_review
---

# Handoff：P09-AC3-DELETE-HARDEN-1（托管文件删除路径加固）

> 本文件按 `doc/09_COLLABORATION.md` §5 建立（交付文件为 `doc/handoffs/TASK-xxx-<short-head>.md`）。
> 验证证据在 `verification/P09-AC3-DELETE-HARDEN-1/`，由本文件引用（协议 L106）。

## 交付结果

**范围**：删除路径加固 —— **静态 junction 基准 9 处** + **TOCTOU 删除路径 4 条** + **新增句柄链删除原语**。

**变更路径**

| 路径 | 内容 |
|---|---|
| `src/infrastructure/filesystem/win_unlink.py` | **新增**：`unlink_by_handle(root, segments)` —— 从驱动器根逐段打开句柄、逐段校验 reparse、只对末段文件请求 `DELETE`、`FILE_OPEN` 不创建缺失组件、`finally` 释放全部句柄；非 Windows 返回 `None` 由调用方回退 |
| `src/infrastructure/filesystem/managed_storage.py` | 基准改 `abspath`；`remove_managed` 接线句柄链（保留 `is_file()` 仅为区分「缺失静默」与「越界抛错」，**非防护**）|
| `src/infrastructure/sqlite/library.py` | `preflight_permanent_delete` / `cleanup_book_files`（含其 `books_base`）基准改 `abspath`；预览删除走句柄链 |
| `src/infrastructure/resource_channel/render_preview.py` | `publish` / `publish_original` / `collect_orphans` 基准改 `abspath`；新增 `_cleanup_quietly`（异常清理走句柄链）；`collect_orphans` 拒绝项不计入 `removed_files` |
| `src/infrastructure/sqlite/backup.py` | `restore_backup` 基准改 `abspath` |
| `src/infrastructure/imaging/tile_cache_sweep.py` | `list_cache_files` 基准改 `abspath` |

**AC 对照**

| AC | 状态 | 依据 |
|---|---|---|
| AC1 | PARTIAL | `tests/core` 通过；未跑 Tauri/前端 |
| AC2 | **PASS** | `tests/core` |
| AC3 | PARTIAL | Core 通过；前端 mixed-batch retry 未验 |
| **AC4** | **FAIL（已转出）** | 见下「遗留问题」 |
| AC5 | **PASS** | storage 测试 + junction/竞态探针；R7 判 PASS |
| AC6–AC8 | **PASS** | `tests/core` + `verify_all.py`（孤儿扫描 0）|
| AC9/AC10/AC12 | **带限制关闭** | 验收表 `PASS` 为**历史测试运行结果**（各附命令）；**R6 之后未再运行** Rust/前端/packaging/全量集，**当前复审状态 NOT_VERIFIED** |
| AC11 | PARTIAL | `P09` AC3 delete 子条件仍 `BLOCKED`（未翻为 PASS）|

**提交列表**：句柄链与其接线、9 处基准修复、4 条 TOCTOU 修复、9 个探针 —— 详见 `git log 1878f0b1`。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| 静态 junction 基准 | 5 个探针（`n004-*`、`r5-p1-*`）| Windows / `1878f0b126e8a0e2603570f9b2009d8b70a259f1` | **SAFE**（注入触发且外部文件存活）| `verification/P09-AC3-DELETE-HARDEN-1/*.py` |
| TOCTOU `remove_managed` | `r5b-p1-remove-managed-race-probe.py` | 同上 | **旧版 VULNERABLE → 当前版 SAFE**（判别力由 R7 独立复现）| 同上 |
| TOCTOU `collect_orphans` | `r5b-p1-collect-orphans-race-probe.py` | 同上 | **旧版 VULNERABLE → 当前版 SAFE**；`orphan_files_removed` 由 1 变 0 | 同上 |
| 发布异常清理 | `r6-p1a-publish-cleanup-race-probe.py` | 同上 | **旧版 VULNERABLE → 当前版 SAFE** | 同上 |
| 存储层回归 | `python -m pytest tests/storage -q` | 同上 | **86 passed** | 见各轮 Review |
| Core 回归 | `python -m pytest tests/core -q` | 同上 | **558 passed, 1 warning** | 同上 |
| 验收查询 | `python verification/P09-AC3-DELETE-1/verify_all.py` | 同上 | **exit 0**；孤儿扫描 `managed=0 derived=0` | 同上 |

**未运行项**：完整 `pytest tests`、Cargo、前端、packaging —— 自 R6 起未再运行。

## 接收方式

- **分支**：`antigravity/P09-AC3-DELETE-HARDEN-1`（`main` 落后，勿读 `main`）
- **worktree**：当前仓库工作区
- **复现**：`python verification/P09-AC3-DELETE-HARDEN-1/<probe>.py`（**探针自建隔离夹具，不需预先准备**；**每个探针分别报告 `injection_fired` 与 `outside_survived`**）
- **注意**：junction 夹具需先 `rmdir` 才能删除父目录；`verify_all.py` 会覆写 pinned JSON，**须拦截该写入**

## 遗留问题

**AC4（译图预览在永久删除时不被回收）—— 判 FAIL 并转出。**

- **根因**：`publish` 生成 `preview-{uuid4}`（`render_preview.py:69`），清理查 `page-original-{page_id}`（`library.py:1124`），**永不相等** → 文件与 catalog 行都留下且 `retired=0`，GC 也不认
- **量化**：**每次译图阅读泄漏 1 行 + 1 文件**（实测；R7 独立复现：读 5 次后永久删除仍剩 5 行 + 5 PNG）
- **代码注释自证**：`core_service.py:1968-1976` 写出了该缺陷，**结论却写成「can be reclaimed by reference」**
- **两版方案均被否**（详见转出 Task），核心障碍是**产品级**：**没有任何现有字段能区分「在用行」与「遗留行」**
- **转出至**：`doc/tasks/P09-PREVIEW-LIFECYCLE-RECLAIM-1.md`

**R5b P2 的 8 处读取/导出路径**（7 处比较点 + `handle_resolver.resolve_namespace_identity`）→ **`doc/tasks/P09-MANAGED-READ-ROOT-TRUST-1.md`**

## 下一任务建议（必填）

- **Task ID / 标题**：`P09-PREVIEW-LIFECYCLE-RECLAIM-1` —— 译图预览的永久删除回收
- **推荐 Agent / Reviewer**：Owner 建议 **Antigravity**（仓库故障转移顺序）；Reviewer **Codex**
- **推荐原因与前置依赖**：**泄漏在持续发生**（每次译图阅读 1 行 + 1 文件）；依赖本 Task 的删除路径加固（已闭环）
- **Recovery point**：仓库 `G:\CODEX\New Manga`，branch/worktree **待 Codex 创建**
- **允许修改路径**：待 Codex 冻结（建议含 `render_preview.py`、`library.py`、`core_service.py` 及对应测试）
- **禁止范围与新增授权条件**：不改 IPC 契约（如需 Schema 变更**先冻结契约**）；**不改删除路径加固**；**不得默认采用「全删 + 容忍旧引用失效」**（需产品裁决）；`P09` AC3 delete 子条件保持 `BLOCKED`
- **交付物**：**第一个交付物是设计答案**（如何判定 `preview_lifecycle` 行「仍在使用」），**不是补丁**
- **验证命令与完成 Gate**：`ac4-leak-count-probe.py` 改为**断言**（**修前先跑出红**）；「读多次后永久删除」残留归零；`tests/storage` + `tests/core` 不回归
- **可直接转发给 Agent 的指令**：

```
Task: P09-PREVIEW-LIFECYCLE-RECLAIM-1
Repo: G:\CODEX\New Manga
Branch: 待 Codex 创建

先读（顺序固定）：
  doc/tasks/P09-PREVIEW-LIFECYCLE-RECLAIM-1.md
  verification/P20-CLOSE-BOUND-HARDEN-2/ac4-reclaim-task-draft.md
  doc/handoffs/P09-AC3-DELETE-HARDEN-1-1878f0b1.md
  verification/P20-CLOSE-BOUND-HARDEN-2/ac4-leak-count-probe.py

第一个交付物不是补丁，是设计答案：如何判定 preview_lifecycle 行「仍在使用」。
六个候选已排查失败、两版方案已被否——先读第二份文件，不要重走。
```n