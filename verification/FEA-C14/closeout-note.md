# FEA-C14-DRAFT 收口资源说明

- **Task**：`FEA-C14-DRAFT`（C-14 Source 重定位/同步/容器页/缓存边界，D05 剩余范围）
- **契约冻结**：`e35f37603`（v3），pin `05056cbf…`（`verify_pins.ps1` 13/13）
- **本目录用途**：登记本 Task 的资源实况；**本 Task 无判别力原始产物**（纯文档 Task，证据均为版本化复核报告）。

## 仓库内资源

- worktree：无（本 Task 未建 linked worktree）
- task-env：无
- 构建产物 / artifact：无
- 临时产物：无（仓内）
- 用户数据：**未访问**

## 仓库外临时脚本

本 Task 相关的一次性脚本与 D06 共用同一批残留，位于 `G:\CODEX\New Manga.workspace\tmp\`：

| 文件 | 关联 |
|---|---|
| `fix_c14_r1.py` | C-14 r1 处置 |
| `fix_c14_r2.py` | C-14 r2 处置 |
| `c14_sha.txt` | C-14 pin 记录 |

逐项 sha256、大小、mtime 见共享清单 `verification/FEA-D06-GAP/workspace-tmp-manifest.md`（第 18–20 行）。处置：`PRESERVE_UNKNOWN`（原地保留，不删除、不迁移、不归档）；原因是其中 `add_c08_d06.py` 等生成过被冻结契约字节，删除会破坏可复现性。

## 关闭计数

`deleted=0 / moved=0 / migrated=0 / archived=0`。
