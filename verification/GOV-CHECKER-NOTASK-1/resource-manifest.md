# 资源记录（待 Integrator 裁决）

核验时间 2026-11-11；主仓库 `G:/CODEX/New Manga`，当时 HEAD `2afe986b6fd61a89a194176b1f5321d0aed6846c`。新增 delivery audit 是唯一当时未跟踪的主树文件；不删除或迁移任何资源。此文仅记录观察，不单独授权资源处置。

仓外目录 `G:/CODEX/New Manga.workspace/GOV-CHECKER-NOTASK-1/` 由本 Task 创建；以下三个本地 shared clone 均经 `git status --porcelain` 显示 clean：

| 名称 | detached HEAD | 用途 |
|---|---|---|
| baseline | `eb06df0d8e8521d43753823a8ef00166f19121b1` | CRLF 诊断，未用于通过结论 |
| baseline-blob | `eb06df0d8e8521d43753823a8ef00166f19121b1` | 基线与边界矩阵 |
| implementation | `21ce0f24f2c4b0a153f85163eadc64b36b7bf72b` | 实现矩阵与两次变异，checker 已恢复 |

三者依赖主仓库对象库，保留原位置；HEAD 和 clean 仅描述已跟踪状态，不授权清理，也不证明 ignored 文件不存在。Review CLI 已返回；无待观察的本 Task 进程。环境未单独创建 task-env、数据集、模型、安装包或 exchange。

同目录原始日志的 SHA-256（工作区原始字节）：

| 文件 | SHA-256 |
|---|---|
| baseline-run-eb06df0-blob.log | ee830505bd4202a7747f655c9152c6f36cd0f6512333f18b95de6d6bd9ff6dd7 |
| baseline-run-eb06df0.log | 433a6d22df1f66a4f76250fb5ed875b85c776815ea632dc9aab5088477aee61e |
| boundary-run-eb06df0.log | 80e34ad917d91001032ebbaa491618e3d2b470500cc585832c70f037471d8ce6 |
| implementation-run-21ce0f2.log | 4d6b09b57499e7063855e4a23fbdddc9feabb5afe95395b70f8fd1f3c75b60a0 |
| implementation-run-21ce0f2-r2.log | 7f2106d1c4f27e059d60f0fa831c5da5078c451dbc3c4c1a381c4626eb8a720f |
| implementation-run-21ce0f2-r3.log | 0ca70ec8248d57edce5cb09ca1d0f63e746cbdb24cefca426b6b68bed1e3648c |

保留 disposition 建议：主 worktree `PRESERVE_REFERENCED`；仓外目录 `PRESERVE_REFERENCED`；未使用资源 `NOT_APPLICABLE`。最终 closeout 由 Integrator 核定。
