# R2 复审报告

reviewed_head: `10202dc4e178eb58a7e08ee0c59e1453ecc6f522`  
decision: `changes_requested`  
findings: **10**（原 finding 7 项，新增问题 3 项）

复审对象是指定的固定 head；当前分支 `antigravity/P09-AC3-DELETE-HARDEN-1` 的 `HEAD` 为 `19d82bc2`，是该固定 head 的文档后续提交。固定 head 与当前工作区之间未发现生产代码差异；未读取 `main`。复审涉及的仓库文件没有被修改。

## 实际验证

- `verify_all.py` 完整运行，exit 0；输出 `Orphan scan: managed=0 derived=0`，并通过 orphan 断言。该脚本会覆盖已 pin 的历史 JSON，因此运行时拦截了这一次写入；脚本的主验证逻辑实际执行完毕。
- `test_preview_unlink_reparse.py`：4 passed。
- `test_refused_preview_unlink_keeps_records.py`：2 passed。
- `test_p09_ac1_recycle_bin_route.py`：1 passed。
- `test_p09_ac4_translated_preview.py`：1 passed。

pytest 通过 `-B` 和 `-p no:cacheprovider` 禁用了仓库内字节码与 pytest 缓存写入。测试按自身设计使用了临时夹具；专项路径状态检查未见仓库文件变化。

## F-001～F-007 判定

| Finding | 判定 | 证据 |
|---|---|---|
| F-001 | **CLOSED** | 原有“命令未冻结”的范围冲突，已由用户方向 A 裁决及 M2-C1 rev 2.11 关闭。契约现有 `ListRecycleBinBooks`、§5.12、§11 与 §12 条目；Core handler、dispatcher、Rust round-trip 和三处 Tauri 注册均存在，AC1 路由测试通过。另发现的版本号和 wire 错误码不一致列为新增 N-001。 |
| F-002 | **PARTIAL** | `51bd814d1` 修正了 `managed_rel_path` 和 `producer_root`；测试证明路径能解析到真实源文件。但真实 reader preview 发布后仍是 `retired=False`，不在 GC 候选中，详情见下方。 |
| F-003 | **CLOSED** | `992bdff36` 拒绝任何含冒号的路径，覆盖 `C:evil.png` 和 ADS；普通路径仍能删除。本轮对应测试 4 passed。 |
| F-004 | **CLOSED** | `8af40864b` 让调用方检查 unlink 返回值；拒绝时保留 catalog 行和 manifest。拒绝与成功路径测试均通过，共 2 passed。 |
| F-005 | **CLOSED** | `ac46e162c` 加入真实 managed/derived orphan 扫描及断言，`354971bed` 追加运行记录。本轮运行实际输出 `managed=0 derived=0` 并通过断言。 |
| F-006 | **CLOSED** | `0add9072b` 将 P09 状态写为“完成（delete 子条件 BLOCKED）”，并追加 `AC3-MATRIX-CURRENT`。该现行 pin 的磁盘 SHA 与表内值相符；原历史 pin 保留。P09 delete 子条件仍是 `BLOCKED`。 |
| F-007 | **PARTIAL** | `0add9072b` 增加了 4 项环境反转、2 项 Transformers API 不兼容的分类；但文档旧表述仍把 6 项统称环境反转，并称失败方向都是环境具备能力，和新分类冲突。 |

### F-001 的实现核对

rev 2.11 声明的回收站查询范围、八字段 `BookSummary` 投影及 `page_count=None` 通道与 Core 实现一致：Service 过滤 `book.deleted`，而该属性等价于 `deleted_at is not None`；handler 使用与 `ListBooks` 相同字段。`PRODUCTION_COMMANDS`、`generate_handler!` 和命令白名单均包含 `library_list_recycle_bin_books`。这些实现与专项测试证据见 [M2-C1_TYPED_IPC_CONTRACT.md](<G:/CODEX/New Manga/doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:805>)、[core_service.py](<G:/CODEX/New Manga/src/bootstrap/core_service.py:1050>)、[library_bridge.rs](<G:/CODEX/New Manga/apps/desktop/src-tauri/src/library_bridge.rs:4031>) 和 [main.rs](<G:/CODEX/New Manga/apps/desktop/src-tauri/src/main.rs:75>)。

## 新增问题

### P1 — N-001：rev 2.11 的协议版本与错误 wire 值和实现不一致

契约声明 Core protocol minor 从 10 升到 11，但 Core 的 `PROTOCOL_MINOR` 仍为 3；`dispatch_request` 只为 Create、Delete 和 P15 命令指定更高版本，其他命令返回 3。Rust 的回收站 bridge 调用 `round_trip()`，其默认请求版本也是 2.3。实际探针发送 minor 11 请求后得到 `response_minor=3`，而契约写明应为 11。证据见 [M2-C1_TYPED_IPC_CONTRACT.md](<G:/CODEX/New Manga/doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:3>)、[core_service.py](<G:/CODEX/New Manga/src/bootstrap/core_service.py:189>)、[library_bridge.rs](<G:/CODEX/New Manga/apps/desktop/src-tauri/src/library_bridge.rs:1781>)。

错误标识也有相同的 wire 差异：代码常量 `E_LIST_BOOKS_FAILED` 的值是 `"LIST_BOOKS_FAILED"`，`E_UNKNOWN` 的值是 `"UNKNOWN"`；dispatcher 和 Rust bridge 保留这些值。本轮实际触发两种错误得到 `LIST_BOOKS_FAILED` 和 `UNKNOWN`，而 §5.12 按字面冻结了 `E_LIST_BOOKS_FAILED` 和 `E_UNKNOWN`。见 [contract §5.12](<G:/CODEX/New Manga/doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:811>)、[Core 常量](<G:/CODEX/New Manga/src/bootstrap/core_service.py:233>)。

复现：向 `ListRecycleBinBooks` 发送版本 2.11 请求，响应仍标 2.3；令 handler 抛出 `sqlite3.OperationalError` 或 `RuntimeError`，wire `code` 分别为 `LIST_BOOKS_FAILED` 和 `UNKNOWN`。需使冻结契约的版本与错误字面值和实际调用链一致。

### P1 — N-002：逐段 `lstat()` 与 unlink 之间仍可被 junction 替换

[unlink helper](<G:/CODEX/New Manga/src/infrastructure/sqlite/library.py:1280>) 检查父目录后仍通过路径继续 `lstat()`、`is_file()` 和 `unlink()`；这不是原子操作。本轮用确定性探针在父目录检查后将 `derived/pages` 换成指向外部目录的 junction，结果为：

```text
race_hook_fired=True
unlink_returned=True
outside_page_original_survived=False
```

这说明外部 `page-original` 文件可在检查与删除之间被误删。现有静态 junction 测试通过，但没有覆盖此并发替换。AC5 因此仍为 PARTIAL。修复需要让路径检查与删除在不跟随替换目录的安全句柄/原子路径操作下完成，并加入该注入场景的回归验证。

### P2 — N-003：Task 中 7 个现行证据 pin 的磁盘 SHA 已过期

逐一检查了 Task 登记的 11 个 pin：commit 格式均符合 7–40 位 hex，且每个 `git cat-file -e "<commit>:<path>"` 均成功；但以下 7 个条目的登记 SHA 与当前磁盘字节 SHA 不符：

| evidence_id | 登记 SHA-256 | 当前磁盘 SHA-256 |
|---|---|---|
| AC12-REGRESSION | `d65675c91251aaa110af478e67593e4cf8159ed5177449a9c59deb5134a34a94` | `e7c843db816cbbdfa67bae86070f9816017951979dc3c67e518081140fb1aef0` |
| AC4-ORIGIN-TEST | `5b5e644a8fff89f064acf329e0b0fba5da07158efd643256e1a7dff63b1a523f` | `9fee20aa4333d159f275cae5241d907a7b902e8ab6dff88a4da79dcf855b118d` |
| AC5-REPARSE-TEST | `9fd3a1c7680ce472461dbf450c832ddbdf25e88c2e4dbbb8b32681a189c49e1e` | `a4e683207a9375ecd2b46ef5232c58af4f2817d38529c24325cb2c728abc7b8f` |
| AC2-AC6-AC8-IMPL | `6e4babac2ab5f3864743e58c456a5ade17099593972fbaab3ce0d5d25b46c01c` | `c04287522ef4d616a50be9ccb9918ad68843e26df837c7cfd1bac9630473239` |
| AC1-AC4-CORE-IMPL | `5faa0346bc1cde4cc8c6a0c9732264fa77e991a5fb1686ba5c95214ab24eae2e` | `e3ffba1e0e6b40893cf70883366080d293b1734201c47ae75d1eb30cbac55364` |
| AC9-AC1-RUST-IMPL | `6026b952f24cbffd5741caed68d5f24999b795431b65bc16abd9a21f4b21bc18` | `d4825b8a7f9187cef893b646a1cf667045e4bb817eea8ac9af40ba720c03d29b` |
| AC7-VERIFY-SCRIPT | `510f7820b5efb1a6cdb0e72dd4c226c19ffd38d11e1c79f83e2f77455547d923` | `ed1446b1bdc9dec0ddb43eedd3248e7da38f311c79a829458b4182bbac81ea3a` |

这些文件包含返修后的内容，但 Task 中没有对应的现行 pin。应按“保留历史 pin、只追加”的规则补充现行 pin，并在复算前保持原行不变。表位置见 [Task Canonical Evidence](<G:/CODEX/New Manga/doc/tasks/P09-AC3-DELETE-HARDEN-1.md:158>)。

## AC1～AC12

| AC | 判定 | 依据 |
|---|---|---|
| AC1 | **PARTIAL** | 路由、软删除集合、八字段投影与注册均已实测/核对；N-001 的协议版本和 wire 错误值与冻结契约不一致。 |
| AC2 | **PASS** | R1 已记录多目标 Run 删除回归通过；本轮变更未改动该脱离逻辑。 |
| AC3 | **PASS** | R1 已记录逐项重试与前端测试通过；本轮未重跑该前端套件。 |
| AC4 | **PARTIAL** | 路径/root 修复通过测试；实际 reader preview 运行探针显示 `retired=False` 且不在 GC 候选中。Reader 发布处见 [core_service.py](<G:/CODEX/New Manga/src/bootstrap/core_service.py:1980>)；GC 只选择 `retired=1`，见 [catalog_store.py](<G:/CODEX/New Manga/src/infrastructure/resource_channel/catalog_store.py:728>)。 |
| AC5 | **PARTIAL** | 盘符相对路径、ADS 和静态 junction 检查均通过；N-002 的并发 junction 替换复现了越界删除。 |
| AC6 | **PASS** | R1 已记录 locator 脱离测试通过；本轮端到端脚本也确认 Pipeline 历史保留与脱离。 |
| AC7 | **PASS** | 查询同步证据已由 R1 核对；本轮端到端脚本的真实 orphan 扫描通过。 |
| AC8 | **PASS** | R1 已验证有界目录清理；本轮端到端脚本完成且 orphan 扫描为零。 |
| AC9 | **PASS** | R1 已记录 phase 白名单测试通过；本轮对应实现无差异。 |
| AC10 | **PASS** | 当前测试断言 schema v5；R1 已记录相关测试通过，本轮未重跑该套件。 |
| AC11 | **PARTIAL** | P09 状态文字已澄清且 `AC3-MATRIX-CURRENT` pin 通过；N-003 的 7 个过期 pin 仍使 Task 证据指针不完整。 |
| AC12 | **PARTIAL** | 新增的 4/2 分类与旧的“6 项均为环境反转”表述并存；同环境前后基线本轮 **NOT_VERIFIED**，且该证据文件 pin 过期。 |

F-002 的剩余问题在 [render_preview.py](<G:/CODEX/New Manga/src/infrastructure/resource_channel/render_preview.py:51>)：reader preview 注册时为 `retired=0`；当前 reader 路径没有为这些随机 preview key 执行退休标记，而 GC 候选查询要求 `retired=1`。因此每次阅读生成的 preview 虽已绑定正确源路径，仍不会进入回收扫描。

## 结论

当前不能将 Task 批准进入集成 `done`。还需解决 N-001、N-002 两项 P1，补齐 N-003 的现行 pins，并清理 F-002/F-007 的未闭合问题。`P09` 的 AC3 delete 子条件仍保持 `BLOCKED`，本轮未将其翻为 PASS。

**推荐下一步：** 保持 Task 为 `in_review`；修复上述 P1 和证据问题后固定新 `delivery_head`，再进行独立复审。未提供 `-o` 路径，且任务禁止创建文件，因此本报告在此返回，未写入文件。