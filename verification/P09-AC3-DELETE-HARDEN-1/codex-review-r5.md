<!-- codex session: 01a151c0-319a-70a1-813d-78f8d345368b | reviewed_head: 86f0bcc86 -->

## reviewed_head

`ff19ec6a565d059b28be66723a06bd2d73a514ec`  
**Decision:** `changes_requested`  
**New findings:** 5

### R4 三项处置

| 项 | Verdict | 证据 |
|---|---|---|
| N-004 根路径修复 | **PARTIAL** | [library.py](<G:/CODEX/New Manga/src/infrastructure/sqlite/library.py:1118>) 已改用 `os.path.abspath`，生产代码中 `unlink_by_handle` 只有这一个调用点；[win_unlink.py](<G:/CODEX/New Manga/src/infrastructure/filesystem/win_unlink.py:130>) 从盘符根开始逐段开句柄。根不存在、中间段为文件、根路径带尾部斜杠及早退句柄释放的只读检查均符合预期。但要求的 junction 探针未运行，不能据此判定攻击验证通过。 |
| R4 探针注入判定缺陷 | **CLOSED（仅源码核对）** | [n004-ancestor-probe.py](<G:/CODEX/New Manga/verification/P09-AC3-DELETE-HARDEN-1/n004-ancestor-probe.py:24>) 检查 `mklink` 返回码、junction 是否存在，以及是否能访问外部文件；失败会终止。探针未运行，执行结果仍为 `NOT_VERIFIED`。 |
| R4 系统临时目录问题 | **CLOSED（仅源码核对）** | [n004-ancestor-probe.py](<G:/CODEX/New Manga/verification/P09-AC3-DELETE-HARDEN-1/n004-ancestor-probe.py:6>) 将夹具放在 workspace 下的 `n004-tmp`。探针未运行。 |

### AC1–AC12

| AC | Verdict | 依据 |
|---|---|---|
| AC1 | `NOT_VERIFIED` | 指定验收测试未运行。 |
| AC2 | `NOT_VERIFIED` | 指定验收测试未运行。 |
| AC3 | `NOT_VERIFIED` | 指定验收测试未运行。 |
| AC4 | `NOT_VERIFIED` | 指定验收测试未运行。 |
| AC5 | `PARTIAL` | 新的路径处理和句柄边界检查已核对；junction 探针未运行，且发现其他删除路径仍存在路径解析风险，见 Finding 1、2。 |
| AC6 | `NOT_VERIFIED` | 指定验收测试未运行。 |
| AC7 | `NOT_VERIFIED` | `verify_all.py` 未运行。 |
| AC8 | `PARTIAL` | 已检查目录清理实现；要求的 Core/storage 测试未运行。 |
| AC9 | `NOT_VERIFIED` | Rust 测试未运行。 |
| AC10 | `NOT_VERIFIED` | 指定测试未运行。 |
| AC11 | `PASS` | Task 中 15 个 40 位提交号均可解析；11 个证据 pin 均通过 `git cat-file -e "<commit>:<path>"`，且按磁盘字节计算的 SHA-256 全部匹配。已核对 [P09.md](<G:/CODEX/New Manga/doc/tasks/P09.md:59>) 的 AC3 delete 子条件仍为 `BLOCKED`。 |
| AC12 | `NOT_VERIFIED` | 本轮未运行全量 pytest；Task 中记录的失败和通过数量未独立确认。 |

### 探针与测试运行

受 `READ ONLY` 约束，本轮未运行会创建或删除夹具文件的四个探针、`pytest tests/storage`、`pytest tests/core` 或 `verify_all.py`。`verify_all.py` 还会写入历史 pin；本轮没有触碰该文件。四个探针的注入和外部文件结果如下；**所有未运行项均为 INCONCLUSIVE，不判 SAFE**：

| 探针 | `injection_fired` | `outside_survived` | 判定 |
|---|---|---|---|
| `n002-race-probe.py` | 未运行；当前 Windows 控制流会绕过 `Path.is_file` 注入点 | `NOT_VERIFIED` | `INCONCLUSIVE` |
| `n002-race-probe2.py` | `NOT_VERIFIED`；源码在创建 junction 前就设置标记 | `NOT_VERIFIED` | `INCONCLUSIVE` |
| `n004-ancestor-probe.py` | 未运行 | `NOT_VERIFIED` | `INCONCLUSIVE` |
| `n004-production-order-probe.py` | 未运行 | `NOT_VERIFIED` | `INCONCLUSIVE` |

我运行了不创建文件的句柄边界检查：不存在的 root 返回拒绝且 3/3 个打开句柄关闭；中间段为文件时拒绝且 6/6 个关闭；带尾斜杠的 root 成功打开且所有 5 个句柄在检查结束时关闭；盘符根的早退句柄也关闭。另用内存替身检查了相对路径尾斜杠：`pages/file.png/` 被拆成 `pages/file.png` 并传入删除链，没有执行实际删除。

### 新问题

1. **P1 — 托管文件删除仍可被祖先 junction 重定向**（[managed_storage.py](<G:/CODEX/New Manga/src/infrastructure/filesystem/managed_storage.py:147>)、[library.py](<G:/CODEX/New Manga/src/infrastructure/sqlite/library.py:1095>)）  
   `remove_managed()` 先对目标和 root 调用 `resolve()`，随后才从未解析的 `_root` 做 `lstat`。如果 `_root` 的祖先是 junction，解析后的目标与 root 都落在 junction 目标下，包含检查会通过；后续逐段 `lstat` 也会沿祖先 junction 访问普通子项，最后 `absolute.unlink()` 删除外部文件。  
   **复现：**把 `ManagedStorage.root` 放在一个目录下，准备一个外部目录，其中有相同相对路径的文件；将 root 的祖先替换为指向外部目录的 junction，然后调用 `remove_managed(relative_path)` 或永久删除路径，检查外部文件是否被删除。

2. **P2 — retired-preview GC 也先解析删除根**（[handle_resolver.py](<G:/CODEX/New Manga/src/infrastructure/resource_channel/handle_resolver.py:855>)、[render_preview.py](<G:/CODEX/New Manga/src/infrastructure/resource_channel/render_preview.py:202>)）  
   `handle_verified_delete()` 对 `scope_root` 调用 `resolve()` 后才进行 reparse walk，并按完整路径打开父目录和目标。根祖先被重定向时，walk 检查的是解析后的路径；若重定向位置有匹配资源 ID、大小和哈希的文件，校验可以针对该文件通过。生产调用受 namespace lease 流程约束，但该路径的祖先替换场景本轮未验证。  
   **复现：**让 publisher 保留原始 root 路径；在 GC 删除前将其祖先重定向到含同名、同哈希 retired preview 的目录，再触发 `delete_retired_preview_copy()`，检查重定向目录中的文件是否被删除。

3. **P2 — N-002 探针可能在注入失败时报告 SAFE**（[n002-race-probe.py](<G:/CODEX/New Manga/verification/P09-AC3-DELETE-HARDEN-1/n002-race-probe.py:46>)、[n002-race-probe2.py](<G:/CODEX/New Manga/verification/P09-AC3-DELETE-HARDEN-1/n002-race-probe2.py:51>)）  
   第一个探针在 Windows 句柄链返回结果后不会走到 `Path.is_file` 注入点，但仍会仅凭外部文件存在输出 `SAFE`。第二个探针在执行 `mklink` 前就设置 `injected`，且不检查命令返回码或 junction 是否可访问，因此注入失败时也可能报 `injection_fired=True` 和 `SAFE`。  
   **复现：**第一个探针在 Windows 当前实现下观察 hook 未触发时的结果；第二个探针令 `mklink` 失败，观察其是否仍将未注入情形报告为 SAFE。

4. **P2 — 生产顺序探针会递归删除固定 workspace 目录**（[n004-production-order-probe.py](<G:/CODEX/New Manga/verification/P09-AC3-DELETE-HARDEN-1/n004-production-order-probe.py:5>)）  
   脚本运行前对固定的 `...\agent-output\coordinator\n004-prod` 执行 `shutil.rmtree`。该路径本轮检查时不存在，但以后若放入其他内容，运行探针会先将其删除。  
   **复现：**在该固定目录下放一个哨兵文件，再运行探针；脚本会在建立夹具前删除它。本轮没有运行该脚本。

5. **P3 — 相对路径尾部斜杠被静默丢弃**（[library.py](<G:/CODEX/New Manga/src/infrastructure/sqlite/library.py:1270>)）  
   `split("/")` 后过滤空段，使 `pages/file.png/` 变成 `pages/file.png`。对于损坏或被篡改的 catalog 条目，句柄链会把目录尾缀形式误当成普通文件路径并尝试删除该文件。  
   **复现：**在 derived root 放置 `pages/file.png`，让 catalog 的 `rel_path` 为 `pages/file.png/`，触发永久删除；路径会以不带尾斜杠的文件段传入句柄链。

## 集成结论

**尚未准备好集成 `done`。** 本轮没有运行指定的攻击探针、测试套件或 `verify_all.py`，并发现 5 个新问题；其中托管文件删除路径的祖先 junction 风险属于 P1。`P09` 的 AC3 delete 子条件仍保持 `BLOCKED`。审查期间未创建、修改或删除文件。

**推荐下一步：**保持 Task 为 `in_review`，先处理 Finding 1–5；在允许隔离夹具文件的审查环境中运行指定探针与测试后，再进行独立复审。