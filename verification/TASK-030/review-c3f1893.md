# TASK-030 独立 Review 记录（Reviewer 侧）

- Reviewer：DeepSeek Harness（非本变更作者；作者为 ZCode）
- base_commit：`087da45590c84227e9695eb829669e9cee805ef2`
- reviewed_head：`c3f189396d9efdceb0e3e42ba7db62b25d77853a`
- delivery_head：`a64c93ab22d8aa18201f0d7eb3f4a3652dd9b0fd`（`c3f1893` 的子提交，仅 Handoff 文档，不属被审范围）
- 报告：[doc/reviews/TASK-030-c3f1893.md](../../../doc/reviews/TASK-030-c3f1893.md)（decision：**approved**）
- Reviewer worktree / 分支：`G:/CODEX/New Manga.worktrees/TASK-030-deepseek-review` / `agent/deepseek/TASK-030-review`（基于 `c3f1893` 新建；被审 worktree 仅只读访问）

## 环境

| 项 | 值 |
|---|---|
| OS | Windows 10.0.26200 x64 |
| Python | 3.12.3（`G:/CODEX/New Manga.task-envs/TASK-012-py312`） |
| PySide6 / pytest | 6.11.2 / 9.1.1 |
| Qt 平台 | **Windows 默认**（`QT_QPA_PLATFORM` 实测为空，未使用 offscreen） |
| openSSL | **PATH 中不存在**（解释与作者数字差异，见下） |

## 实际执行（passed / skipped 分列）

| # | 命令 | 退出码 | passed | skipped | 本机 skip 原因 |
|---|---|---|---|---|---|
| A | `PYTHONPATH=src …python.exe -m bootstrap.app --smoke-test` | 0 | —（入口进程） | — | — |
| B | `…python.exe -m pytest tests/ui_shell -v` | 0 | 46 | 0 | — |
| C | `…python.exe -m pytest tests/core/test_bootstrap.py -q` | 0 | 7 | 0 | — |
| D | `…python.exe -m pytest tests -q -rs` | 0 | 381 | 6 | 全部 `openssl unavailable` |

命令 D 的 6 项 skip：`tests/network/test_connection_tester.py:106`(×1)、`tests/network/test_transport_tls.py:39/47/62/69/83`(×5)。

## 与作者证据的差异

| 项 | 作者 | Reviewer | 归因 |
|---|---|---|---|
| 全量 | 387 passed / 0 skipped | 381 passed / 6 skipped | **主机环境差异**：作者机 PATH 有 `openssl`，本机无；381+6=387，差的正是 6 项 TLS 用例。作者的 `pytest-full.txt` 原文确为 `387 passed`，**不是把 skip 计入 passed** |

## DPI 截图核对

| 档位 | 作者声称尺寸 | 实测尺寸 |
|---|---|---|
| 100% | 1280×800 | **1280×800** ✓ |
| 150% | 1920×1200 | **1920×1061** ✗ |
| 200% | 2560×1600 | **1924×1062** ✗ |

两档不符，原因是测试机虚拟显示器 `1920×1080` 限制了窗口尺寸。→ 报告 R-001（P2）。
**画面内容的人工目视核对：NOT_RUN** —— 当前模型不声明图像输入，Reviewer **未**读取任何截图的画面内容，报告不含对布局/错位的目视判断。

## 未执行（NOT_RUN / N/A）

真实 `%LOCALAPPDATA%` 数据根入口启动（NOT_RUN，作者亦如实记录）；DPI 截图内容的目视核对（NOT_RUN，Reviewer 模型能力限制）；多显示器/键盘焦点全量/原生文件对话框（NOT_RUN，归 TASK-022/026）；工作台·阅读器·设置业务内容（N/A）；性能（N/A）。

## 结论

`c3f1893` **approved**：AC1/AC2/AC3/AC5 成立，AC4 部分成立（抓帧机制与 100% 档成立，高 DPI 尺寸声明需更正），AC6 待集成；四项装配不变量（生产解码器、Managed Copy、真实 `book_id_for_chapter`、QML 不触库）全部通过。**P0=0 / P1=0 / P2=3**（R-001 高 DPI 证据描述、R-002 Task 预填 `decision`、R-003 错误路径连接回收）。两项登记事项已裁决：数据根默认 `%LOCALAPPDATA%/New Manga` **批准**（建议登记进 D03/D07）；顶层 `QQuickWindow` 导入**保留**（必要性表述需修正为"强类型保障 + rewrap 为第二道保险"）。**本记录与报告均不含 `integration_commit`**（被审 head 未合入主线，该值只能由 Codex 填写）。

## Reviewer 过程失误（如实记录并已修正）

1. 报告初稿被写入**被审的 ZCode worktree**（应写入 Reviewer 自己的 worktree）——违反"被审 worktree 只读"。已删除该文件并移入 Reviewer worktree。
2. 首次修正命令因 PowerShell 把 `$repo.worktrees` 解析为 `$null` 而造成参数错位，在被审仓库相对路径 `G:/CODEX/New Manga/c3f1893` 误建了一个 worktree（分支 `agent/deepseek/TASK-030-review`）。
3. 已完成清理：移除误建 worktree、删除该分支（无独有提交）、在正确路径 `…/TASK-030-deepseek-review` 重建。核验结果：**ZCode worktree `git status` 为空**、**主工作区 `git status` 为空**、报告位于 Reviewer worktree。被审生产代码、测试与作者提交**始终未被修改**。
