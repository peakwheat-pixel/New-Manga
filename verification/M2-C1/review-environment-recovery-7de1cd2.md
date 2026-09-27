# M2-C1 Reviewer 环境恢复与 Qoder 提交核验

日期：2026-09-26（Asia/Shanghai）

## 固定产品与 Review 对象

- Owner：ZCode；Owner Delivery：`7de1cd27e22037d4b76b235c9f11399b0cea9463`。
- Handoff 与两位 Reviewer 的绑定 head：`b2377288680569dbee4e2299fd7dfae4de067c54`。
- Case A disposition 保持 `OWNER_ADOPTED_WITHOUT_SEMANTIC_CHANGE`。
- 已复核 Owner worktree：branch=`agent/zcode/M2-C1-typed-ipc-contract`，HEAD=`b2377288680569dbee4e2299fd7dfae4de067c54`，status clean。未修改 Owner 文件。

## Qoder Git 写入 blocker：通过受支持的命令前缀授权解除

Qoder Review worktree 本身没有 OS/NTFS 写入故障：

- 当前主机身份：`HOME-MY\49745`，SID=`S-1-5-21-2196946971-914346751-4210154634-1001`。
- Qoder worktree 与 `.git/worktrees/M2-C1-qoder-review-7de1cd2` 均有普通继承写权限。在两处分别创建、写入并删除本次唯一命名的 probe 文件，均成功。
- Qoder per-worktree index 可用 `FileAccess.ReadWrite` 打开；长度保持 `256716` bytes，`LastWriteTimeUtc` 未改变。
- Qoder 自己运行的 `git status --short` 在 `Bash(git status:*)` 命令 allowlist 下成功；提交前只显示 `.qoder-credits/`、Review report 和授权 evidence 目录。

根因：先前 Qoder `--allowed-tools` 规则使用精确命令文本但没有 CLI 要求的命令前缀通配后缀，因此 `git add` 仍触发 `Allow Bash to run`。先以只读 `git status` 验证受支持的 `Bash(<command-prefix>:*)` 形式，再仅开放两个路径限定的 `git add` 前缀、staged scope/whitespace 只读检查、`git commit -m`、status 与 HEAD 查询。未使用宽泛权限模式。

Qoder 在 branch=`review/qoder/M2-C1-zcode-7de1cd2` 自行提交 Review commit=`0d73983a5e1f37f104c76d8bd4c70c6f98fa36f5`。Codex 独立运行：

```powershell
git rev-parse --show-toplevel
git branch --show-current
git rev-parse HEAD
git status --short
git diff --name-status b2377288680569dbee4e2299fd7dfae4de067c54..HEAD
git diff --check b2377288680569dbee4e2299fd7dfae4de067c54 HEAD
git merge-base --is-ancestor b2377288680569dbee4e2299fd7dfae4de067c54 HEAD
```

观察结果：HEAD=`0d73983a5e1f37f104c76d8bd4c70c6f98fa36f5`；ancestry exit `0`；diff 恰有 8 个新增路径（Review report + `verification/M2-C1/review-qoder-zcode-7de1cd2/**` 下七个文件）；whitespace 检查无输出且 exit `0`；report frontmatter 绑定 `reviewed_head=b237728...`、`decision=approved`。提交后 `git status --short` 仅有 `?? .qoder-credits/`。该目录按用户指示标为 `PRE_EXISTING_OR_TOOL_GENERATED_OUT_OF_SCOPE`，保持未触碰，未进入 Review commit。

## DSH sandbox ACL blocker：已隔离原因，原 worktree 保留

当前主机与文件系统检查结果：

- `G:` 是本机 NTFS 卷（`DriveType=3`），不是网络或映射盘。
- DSH worktree、父目录 `G:\CODEX\New Manga.worktrees`、`G:\CODEX` 与 Owner worktree 使用相同、未保护的继承 ACL；owner=`HOME-MY\49745`，未发现显式 DENY ACE。这不是单独损坏的 worktree ACL。
- 当前主机账户在原 DSH worktree 与 `.git/worktrees/M2-C1-dsh-review-7de1cd2` metadata 目录中的 create/write/delete probe 均成功；probe 创建后立即删除。worktree index 可 ReadWrite 打开，长度和时间戳未变。common `.git`、`objects`、`refs` ACL 均有普通 `Authenticated Users: Modify`。
- DSH headless 配置启用了 Windows `pwsh-sandbox`，`sandbox-policy mode=workspace-write`，`workspaceRoot=process.cwd`。

没有修改任何 DACL。在原 G: worktree 下运行无害 `Write-Output` probe，复现工具初始化阶段的原始错误，命令未执行：

```text
Error: SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga.worktrees\M2-C1-dsh-review-7de1cd2)
```

主机账户可以在该目录普通读写，但 DSH sandbox preflight 无法在此位置完成 `grantWrite` ACL 操作。DSH 没有暴露内部受限 token/ACL access check 细节，因此不推断更窄的内部原因。原 DSH report 记录一次失败的 `danger-full-access` 请求；该请求被拒绝且未执行，禁止重试。

另在 `C:\Users\49745\.codex\worktrees` 下新建临时诊断目录。该父目录对 `HOME-MY\49745` 有继承的 `FullControl`。在该目录中，DSH 成功执行唯一命令 `Write-Output DSH_USER_WORKTREE_PROBE`。该临时 probe 目录保留在仓库外；DSH 未在其中读写文件或创建 Review artifact。

据此，原 G: DSH worktree/branch 和未提交 report/evidence 继续作为 blocker evidence 保留。Codex 从未改变的 Owner reviewed head 新建了一个 clean linked worktree：

| 字段 | 值 |
|---|---|
| Branch | `review/deepseek/M2-C1-zcode-7de1cd2-r2` |
| Worktree | `C:/Users/49745/.codex/worktrees/M2-C1-dsh-review-7de1cd2-r2` |
| HEAD | `b2377288680569dbee4e2299fd7dfae4de067c54` |
| Common Git dir | `G:/CODEX/New Manga/.git` |
| 初始 status | clean |
| 授权 report | `doc/reviews/M2-C1-zcode-7de1cd2-dsh-r2.md` |
| 授权 evidence | `verification/M2-C1/review-dsh-zcode-7de1cd2-r2/**` |

DSH 需在新 worktree 自行重跑必要 Git 检查并完成完整技术 Review。旧 DSH report/findings 不能替代新 Review，也不得直接继承旧结论。必须独立判断 §1 source-trace 断链；若认为必须修改 Owner Delivery，决定应为 `CHANGES_REQUESTED` 并退回 ZCode。产品测试、GUI、IPC runtime 保持 `NOT_RUN`。

## 当前状态

- Qoder：正式 `APPROVED`，Review commit=`0d73983a5e1f37f104c76d8bd4c70c6f98fa36f5`，绑定 `b237728...`。
- DSH：原 G: 工作区阻塞现场已保留；新 C: worktree 已创建并授权，完整独立 Review 已重新派发并正在进行。Codex terminal exec session=`18242`（不是 DSH 内部 session ID）。
- M2-C1 保持 `blocked`，等待 DSH 正式提交 Review。
- Integration Gate 未 ready、未开启；未集成、未启动 M2-S1。页级 `blocked` 映射和 React UI Owner 仍是 `USER_DECISION_REQUIRED / DEFERRED`。
