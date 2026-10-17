# P19-UI-FIX-3 硬门结论：创建作品/章节从未实现（缺 wire + Core + host）

**Owner（Codex）在动手前按硬门停止并上报**，结论经 Coordinator 采信。依据（全部可核验）：

| 层 | 证据 | 事实 |
|---|---|---|
| 契约 | `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:139` | `CreateBook` 仅在 **§5 提案目录（proposal）** |
| 契约 | 同文件 L141 | **`CreateChapter` 仍是 PROPOSAL** |
| host | `apps/desktop/src-tauri/src/main.rs:71,110` | 生产命令只有 `library_list_books`、`list_chapters` —— **无任何 create 命令** |
| Core | `src/bootstrap/core_service.py:3080-3086` | 导航 handler 只分发 `list_chapters` / `list_chapter_pages` —— **无 create handler** |
| 旧架构 | `src/ui/viewmodels/bookshelf/viewmodel.py:287,313` | 仅 Legacy Qt 方法，不在 AD-001 新架构路径 |

## 结论（修正我先前的表述）

用户裁决 **A（空书架应允许新建作品/章节）**。但实测+代码核对表明：**这不是"按钮被误禁用"的 UI 缺陷，而是整条创建能力从未实现**（契约仍为 proposal，Core/host/前端均无）。故 `+ 新建作品` 的 `IsEnabled=False` **是当前产品能力的如实反映**。

→ **满足裁决 A 需要新功能立项**（契约冻结 → Core → host → 前端），非本 Task 范围。

## 待用户裁决的两条路

- **A1**：立项「创建作品/章节」新功能（3–4 个 Task），真正满足 A；**不阻塞** P20 发布。
- **B**：接受当前产品不支持创建；P19 的 AC2 以"预置带章节数据"为前提验收并登记限制 → 先收尾 P19 并释放 P20，创建能力另立功能。

## 状态
- `P19-UI-FIX-3` 在其分支上 `blocked`（主仓任务仍为 `ready`，未污染 DAG）。
- 无产品代码被改动；Owner 工作树仅含检查点与状态更新。