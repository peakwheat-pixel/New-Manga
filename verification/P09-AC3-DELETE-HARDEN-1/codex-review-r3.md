<!-- codex session: 01a15198-e1cf-73a1-81ae-50637f2f8f64 | reviewed_head: 1a2e0a61f -->

# P09-AC3-DELETE-HARDEN-1 第三轮独立复审

reviewed_head: `a73bf6b10b76b2bcdd2b7ed4f843608c661d8c6e`  
decision: `changes_requested`  
findings: **6**（4 项 R2 finding 仍部分未闭合，另有 2 项新增）

复审只依据指定固定 head。工作区 `HEAD` 是 `65ca604…`；本轮运行所用的源码、测试和验证脚本与固定 head 一致，未读取 `main`。仓库文件未改动；探针在 `%TEMP%` 使用了隔离夹具。

## R2 findings 判定

| Finding | 判定 | 证据 |
|---|---|---|
| N-001 | **CLOSED** | 当前 M2-C1 rev 2.11 正确记为协议版本不变（`minor=3`），wire 错误码为 `LIST_BOOKS_FAILED` / `UNKNOWN`。Task 中 F-001 关闭记录仍保留当时的旧说法，但后续 R2 记录已说明发现该问题；现行契约正文已修正。 |
| N-002 | **PARTIAL** | 旧实现探针复现了外部文件被删；新句柄链探针实际触发注入并保住外部文件。但根路径仍由完整路径打开，祖先 junction 替换可绕过该链，详见新增 N-004。 |
| N-003 | **PARTIAL** | 按磁盘字节复算 11 个 pin：11/11 的 `commit:path` 可由 `git cat-file -e` 验证，但只有 10/11 的 SHA 匹配。`AC2-AC6-AC8-IMPL` 登记为 `c042875…`，磁盘值为 `2243c80e…`；见 [Task 证据表](<G:/CODEX/New Manga/doc/tasks/P09-AC3-DELETE-HARDEN-1.md:163>)。 |
| F-002 | **PARTIAL** | 新测试直接调用 `catalog.mark_preview_retired(key)`，再检查候选列表；这验证了退休后的 GC 候选路径，却没有证明真实 reader 发布会退休 preview。生产标记仅在请求带 `retire_preview=true` 时发生，现有 Tauri 调用是 rerender 轮换旧 key。见 [preview 测试](<G:/CODEX/New Manga/tests/core/test_p09_ac4_translated_preview.py:176>)、[host bridge](<G:/CODEX/New Manga/src/infrastructure/resource_channel/host_bridge.py:136>)、[main.rs](<G:/CODEX/New Manga/apps/desktop/src-tauri/src/main.rs:1083>)。 |
| F-007 | **PARTIAL** | 4 项环境反转 / 2 项 Transformers API 不兼容的分类表已修正，但 [AC12 证据](<G:/CODEX/New Manga/verification/P09-AC3-DELETE-HARDEN-1/ac12-no-regression.md:66>) 仍笼统称“这些测试”都要求运行时或模型缺失；[Task 的 AC12 行](<G:/CODEX/New Manga/doc/tasks/P09-AC3-DELETE-HARDEN-1.md:85>) 仍把 6 项统称环境反转。 |

## N-002 句柄链核对

- `_open_relative` 的子对象通过 `OBJECT_ATTRIBUTES.RootDirectory` 相对父句柄打开；中间段强制目录、末段强制非目录，并检查子对象的 reparse 属性。句柄均加入 `opened` 后由 `finally` 逆序关闭。未发现一般成功、拒绝或异常路径上的句柄泄漏。
- `del buffer, us, attrs, iosb` 在 `NtCreateFile` 返回后执行；传入的对象名缓冲区在调用期间仍有局部引用，未发现生命周期缺陷。
- `None` 在非 Windows 平台会触发旧路径实现回退，该回退仍有路径竞态；当前产品目标是 Windows，正常 Windows 调用不会因打开失败而返回 `None`。若此 helper 被跨平台复用，回退并不安全。
- 根句柄没有属性检查，而且其打开仍重新解析完整根路径；新增复现证明这会绕过子句柄链的保护。

Microsoft 文档确认：非空 `RootDirectory` 下的对象名相对于该目录句柄解析；`FILE_OPEN_IF` 会在目标不存在时创建对象。[NtCreateFile 文档](https://learn.microsoft.com/en-us/windows/win32/api/winternl/nf-winternl-ntcreatefile)、[OBJECT_ATTRIBUTES 文档](https://learn.microsoft.com/en-us/windows/win32/api/ntdef/ns-ntdef-_object_attributes)。

## 必须验证的实际结果

- `python -B -m pytest -p no:cacheprovider tests/storage -q`：**86 passed**。
- `python -B -m pytest -p no:cacheprovider tests/core -q`：**558 passed**，1 条 Pillow 弃用警告。
- `verify_all.py`：**exit 0**，孤儿扫描 `managed=0 derived=0`，AppData 前后摘要一致。对已 pin JSON 的 `Path.write_text` 写入做了精确拦截；前后磁盘 SHA 均为 `67d4dbdb…`，未覆盖历史证据。
- `n002-race-probe.py`：旧函数从 `a73bf6b…` 的父提交对象载入内存后运行；旧 probe 在指定的较早基线 `a04e4ea…` 中没有该函数。重跑结果为 `race_hook_fired=True`、`unlink_returned=True`、`outside_survived=False`，即 `VULNERABLE`。
- `n002-race-probe2.py`：`injection_fired=True`、`unlink_returned=False`、`outside_survived=True`，相对路径替换被拒绝。

## 新增问题

1. **N-004 — P1：根目录祖先 junction 替换仍能删除根外文件。**  
   [win_unlink.py](<G:/CODEX/New Manga/src/infrastructure/filesystem/win_unlink.py:132>) 用 `CreateFileW(str(root), … FILE_FLAG_OPEN_REPARSE_POINT)` 打开完整根路径；标志没有阻止祖先路径被重新解析，根句柄也未核验属性。调用方在 [library.py](<G:/CODEX/New Manga/src/infrastructure/sqlite/library.py:1110>) 先解析根，再于 [library.py](<G:/CODEX/New Manga/src/infrastructure/sqlite/library.py:1296>) 调用句柄链。
   
   实际复现：先解析 `trusted/derived`，在 `_open_root` 前将 `trusted` 替换为指向外部目录的 junction。结果：`root_swap_injection_fired=True`、`unlink_returned=True`、`outside_survived=False`、`original_inside_survived=True`。这也是 N-002 仍为 `PARTIAL` 的根锚点缺口。

2. **N-005 — P2：相对打开会创建缺失组件。**  
   [win_unlink.py](<G:/CODEX/New Manga/src/infrastructure/filesystem/win_unlink.py:180>) 把 `_FILE_OPEN_IF` 作为 `CreateDisposition`。实际调用 `unlink_by_handle(empty_root, ["created-parent", "leaf.png"])` 后得到 `missing_chain_returned=True`、`missing_parent_created=True`、`missing_leaf_exists_after=False`：缺失目录被留下，末端文件被创建后删除，函数却返回成功。该行为与缺失组件应拒绝的接口语义不符。

## AC1–AC12 判定

| AC | 判定 | 依据 |
|---|---|---|
| AC1 | **PASS** | 当前契约 wire 值与协议版本已修正；本轮 `tests/core` 通过。 |
| AC2 | **PASS** | 本轮 `tests/core` 全部通过；多目标 `detached:` 逻辑仍在固定 head 中。 |
| AC3 | **PASS** | 后端测试通过，前端逐项重试实现与固定证据保持；本轮未重跑前端 Vitest。 |
| AC4 | **PARTIAL** | preview origin 与路径断言存在，但真实 reader 生产生命周期没有退休接线。 |
| AC5 | **PARTIAL** | 相对句柄链 probe 保护外部文件；根祖先替换仍造成外部删除，且缺失路径会被创建。 |
| AC6 | **PASS** | `tests/core` 通过；stage-state 与嵌套 locator 脱离逻辑保持。 |
| AC7 | **PASS** | 本轮实际运行 `verify_all.py` 成功，孤儿扫描为零；历史 JSON 写入未落盘。 |
| AC8 | **PASS** | `tests/core` 通过；固定代码使用有界祖先清理。 |
| AC9 | **PASS** | 固定 Task 记录对应 Rust 单测 1 passed；本轮未重跑 Rust 测试。 |
| AC10 | **PASS** | 固定代码断言为 `ver == 5`；该 packaging 测试本轮未单独运行。 |
| AC11 | **PARTIAL** | 11 个 pin 中 1 个磁盘 SHA 失配，见 N-003。 |
| AC12 | **PARTIAL** | 固定证据记录了全量结果，但分类文字仍冲突；本轮未重跑全量 `pytest tests`。 |

**结论：不能进入集成 `done`。** 固定 head 的 [P09 Task](<G:/CODEX/New Manga/doc/tasks/P09-AC3-DELETE-1.md>) 仍将 AC3 delete 子条件标为 **`BLOCKED`**。`verify_all.py` 的成功输出没有改变该权威状态，本轮也未覆盖其历史 JSON。

推荐下一步：由当前 Task Owner 修复根句柄锚定与 `FILE_OPEN_IF` 行为，补上生产 reader retirement 生命周期，清理 AC12 残余表述，并更新失配 pin；固定新 head 后再复审。