# UI-DESIGN-1 — git 提交 BLOCKED 记录

Owner 会话（ZCode，2026-10-16）中，harness 权限层拒绝一切非白名单命令
（错误原文统一为 `No permission client configured for Bash`），包括：

- 全部 `powershell` / `powershell.exe` / `pwsh` 调用（selfcheck 复跑，见 `selfcheck-BLOCKED.md`）；
- `git add`（Owner 直跑 1 次 + general-purpose 子代理 1 次，均被拒）；
- `certutil -hashfile`（sha256 补算）；
- 复合命令（`&&`、`for`、输出重定向）。

只读白名单命令（`git rev-parse` / `git status` / `git diff` / `git log` / `grep` / `ls` / `echo`）正常。

因此本 Task 的**交付 commit 未能在 Owner 会话内产生**。所有交付物已在工作树
`G:/CODEX/New Manga.workspace/worktrees/UI-DESIGN-1`（分支 `agent/zcode/UI-DESIGN-1`）就绪，
均为新增 untracked 文件（零 tracked 修改、零删除）：

```
doc/design/AD001_FOUR_PAGE_UI_BASELINE.md
doc/handoffs/UI-DESIGN-1-zcode.md
doc/tasks/UI-DESIGN-1.md            （交付记录更新，见下）
verification/UI-DESIGN-1/selfcheck.ps1
verification/UI-DESIGN-1/selfcheck-output.txt
verification/UI-DESIGN-1/selfcheck-BLOCKED.md
verification/UI-DESIGN-1/commit-BLOCKED.md   （本文件）
verification/UI-DESIGN-1/resource-manifest.json
```

## 待重放的提交命令（交 Coordinator / 下一会话）

在权限客户端可用的环境中，于上述 worktree 执行：

```
git add doc/design/AD001_FOUR_PAGE_UI_BASELINE.md doc/handoffs/UI-DESIGN-1-zcode.md doc/tasks/UI-DESIGN-1.md verification/UI-DESIGN-1
git commit -m "docs(UI-DESIGN-1): deliver AD-001 four-page UI/UX design baseline + selfcheck evidence"
git rev-parse HEAD
```

提交后需要回填两处占位：

1. `doc/handoffs/UI-DESIGN-1-zcode.md` frontmatter `delivery_head: PENDING_COMMIT_A` → 实际 SHA；
2. `doc/tasks/UI-DESIGN-1.md` Canonical Evidence 表中 commit 列的 `WORKTREE_ONLY` → 实际 SHA。

回填属同一 Task 允许范围，可并入同一提交（先回填再 commit，占位指代"本提交自身"）
或紧随其后的登记提交。

不 push、不 merge（集成由 Coordinator 执行）。
