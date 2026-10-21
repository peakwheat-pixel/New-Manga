# 收敛盘点与裁决请求（非完成声明）

## 当前结果

2026-10-21 / Codex epoch 9。正式接管、新 Task 已释放；所有清理/合并均为 0。**尚未达到只剩 main**；本报告不请求关闭 Task。

|指标|治理前|当前盘点|
|---|---:|---:|
|本地 refs/heads|97|97|
|注册 worktree（含主 checkout）|135|135|
|未并入 main 的本地分支|19|19|
|远程跟踪 refs|3|3|
|archive tags|77|77|
|其他 refs/codex|37|37|
|stash|0|0|

全部 214 refs 已记录。135 worktree 中 Detached 39，dirty/untracked 82，含 ignored 根 60，保护声明命中 125，Git 检查错误 0。分支归属的 Agent 字符串只是提示，不等于当前 Owner 授权；不能从历史文件生命周期或 branch 名称自动恢复任务。

## 逐项处置与集成

97 条逐项 tip、独有提交数、分类与工作树映射见 [branches](branches.md)；135 条逐项文件状态与保护数量见 [worktrees](worktrees.md)。完整原始数据包括精确 dirty/untracked 路径、ignored 根、保护来源与 unique log：branch-analysis.json / worktree-analysis.json / preflight-inventory.json。

78 分支为祖先已合并（含 main）；另有 2 分支的非合并提交全部 patch 等价：`agent/zcode/T2.2.1-reader-workbench-polish`、`review/deepseek/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-r2`。其余 17 支线仍有不等价 patch（逐分支合计 339，不是跨分支去重数）。git cherry 不覆盖 merge commit 的等价性，也不证明产品需求仍有效。没有把 patch 不等价自动判断为应集成。

`codex/P14` 的 2 个独有提交含前端错误本地化及审查证据，需单独技术核对当前实现，不能因 P14 已 done 直接丢弃；`codex/P15-C1-FU2` 的 2 个提交仅涉及历史 Handoff/Task pin 修订，不覆盖当前主线历史记录；`codex/project-roadmap-rebaseline` 是未释放的旧路线草案，不集成其 STATUS/Plan。其余历史分支保持归档和原位保护，不恢复 Legacy 实施。

## 备份与恢复实测

19/19 未合并分支的现有 tag=tip，已有增量 bundle 实际路径存在、SHA 已记录、git bundle verify exit 0。manifest 的 `<repo>` 是占位符，已按唯一仓库路径显式展开；首轮未展开路径的观察不作为文件缺失证据。

另建独立全 refs 备份 `G:\CODEX\New Manga.workspace\archive\git-backups\GIT-MAINLINE-CONVERGENCE-1\all-refs-56272e40b.bundle`，238847964 B，SHA-256 `8128955e47f835989a718b55b3af11754752e893b7f78fe7f337eaef68c0f1a9`。在新建的空 bare 仓库 `G:\CODEX\New Manga.workspace\temp\GIT-MAINLINE-CONVERGENCE-1\restore-all-refs.git` 中验证无外部 prerequisite、fetch 恢复、214 refs 名称/OID 全等，fsck --full --no-reflogs exit 0；135/135 注册 worktree HEAD commit 均可读。原始命令与 exit 见 backup-restoration.json。

该备份只覆盖 Git refs 与可达对象，不备份任何 dirty/untracked/ignored 文件、reflog-only/unreachable 对象或应用会话注册信息。未对含此类内容的工作树执行备份或删除；原位保护全部保留。恢复测试仓库只是 Task 派生产物，不是新的项目真值。

## 删除门槛与最小裁决

当前没有可直接执行的删除动作：

1. STATUS 与 r212 保留全局清理/GC/prune 禁令；WORKSPACE_GOVERNANCE 明确保留旧主线 `antigravity/P09-AC3-DELETE-HARDEN-1`。用户本轮明确要求不得把收敛目标解释为解除保护。
2. 现有保护扫描发现 77 声明错误，工具 exit 1 拒绝发布可信删除清单；错误类型 {'TABLE_SCHEMA_INCOMPLETE': 45, 'TABLE_ROW_ARITY': 1, 'DECL_RELATIVE_UNRESOLVED': 6, 'DECL_RELATIVE_AMBIGUOUS': 1, 'DECL_ENV': 4, 'DECL_GENERALIZED': 6, 'DECL_DESTINATION_GENERALIZED': 6, 'DECL_UNKNOWN_DISPOSITION': 2, 'JSON_PARSE': 2, 'FILE_UNREADABLE': 3, 'DECL_DESTINATION_UNRESOLVED': 1}。保护解析失败不等于资源不受保护，不能绕过。
3. 96/97 分支仍被工作树检出；125 个保护命中、82 个 dirty/untracked、60 个 ignored 根集合存在重叠，不能相加当作独立资源数量。应用仍运行，未逐路径证实无人使用。

唯一表面技术候选为 `G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-CLEANUP-TOOL-HARDENING-1`，branch `dsh/WORKSPACE-CLEANUP-TOOL-HARDENING-1`，HEAD `1dc8a89445207e47a28a330610a925fa8514bf3b`：tracked/untracked/ignored/stash 都为 0，无独有提交，当前无已解析保护命中，已纳入全 refs 备份并实测恢复。但**77 个解析错误与占用未知仍阻止把它判为 DELETE_SAFE**；尚不请求立即删除。

建议第一项用户裁决只处理授权方向：是否允许建立保护声明错误专项，先调查并冻结逐项最小修复范围（生产代码不变、原始 evidence 字节/pin 不变、不降低 fail-closed、不解除任何资源保护）？这不是删除授权。只有错误消解与原有保护逐项裁决完成后，才另行提交精确到 source/HEAD/hash/backup 的删除窗口。

旧主线的保留、其余 134 工作树以及 17 条仍有独有 patch 的分支均不在任何本轮删除请求中。未推远端、未修改 stash、未运行 GC/prune/强制删除。

## 验证与限制

初始全局治理 PASS 4 warnings。新 Task 触发严格检查后发现 Plan 超预算、Ledger 过期与 READY 行解析问题：原 Plan 完整源字节保存到 archive/history/2026-10-21/git-mainline-convergence/rebaseline-plan-before.md，当前 Plan 显式继承其已关闭节点/依赖/限制并保持 1652B/24 行；台账使用现有生成器刷新，未更改任何历史 Task 状态，也未修改 checker 规则。随后治理 PASS 2 warnings；最终逐次日志另存 verification-log.txt。产品测试 NOT_RUN（无产品代码变更）。

独立 Review 待固定盘点交付 head 后由 DeepSeek 执行，只审查非破坏性盘点切片，不把审查通过解释为全部 AC 达成或删除授权。
