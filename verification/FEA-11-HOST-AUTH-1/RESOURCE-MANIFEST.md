# FEA-11-HOST-AUTH-1 Resource Manifest

生成：2026-11-05（DSH closeout）。

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | NOT_APPLICABLE（任务在 main 工作树实施，非 linked worktree） | NOT_APPLICABLE | — | — | 无 worktree 需删除；未执行 `git worktree remove/prune` |
| agent-output | NOT_APPLICABLE（本任务无可复用 agent-output 目录） | NOT_APPLICABLE | — | — | 未在 workspace 产生本任务专属 agent-output |
| dataset/model/test-material | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 无数据集/模型/测试素材 |
| artifact | NOT_APPLICABLE（无发布产物） | NOT_APPLICABLE | — | — | 无 artifact |
| temp | NOT_APPLICABLE（无本任务专属临时目录） | NOT_APPLICABLE | — | — | 无临时目录 |
| exchange | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 无 exchange |
| evidence | `verification/FEA-11-HOST-AUTH-1/`（EV.md、gates.log、changed-files.txt、RESOURCE-MANIFEST.md、DELIVERY-MANIFEST.md） | PRESERVE_REFERENCED | 原位保留 | 见 EV.md / DELIVERY-MANIFEST.md | 当前 Task 与 Review/Closeout 引用；保留不清理 |
| 代码/测试 | `apps/desktop-avalonia/src/NewManga.CoreClient/Commands/**`、`NewManga.Host/**`、对应 tests | PRESERVE_REFERENCED | 仓库内 | delivery head `cbd561b4` | 已集成 main；不得回滚 |
| 仓外临时文件 | NOT_APPLICABLE | NOT_APPLICABLE | — | — | closeout 未创建仓外临时 DB/fixture；全量 .NET 后 `verification/FEA-09` 已由 r8 Reviewer 恢复（零 diff） |

关闭结论：无 `DELETE_SAFE` 项；无用户数据；无未知/无法核实资源。`resource_closeout_status: complete`。
