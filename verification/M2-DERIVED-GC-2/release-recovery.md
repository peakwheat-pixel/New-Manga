# M2-DERIVED-GC-2 正式释放恢复点

2026-10-07 / Codex。用户明确授权正式释放与同步，不启动实现。
TaskStatus=ready；ExecutionState=IDLE / AWAITING_OWNER_CLAIM。
Owner=ZCode；非作者 Reviewer=DeepSeek Harness；Integrator=Codex。

设计 base=ad75fadc2944983b4322f353176ba70cf0b0b7ae；
设计批准 head=e4c0967f83a08d9b9e2d84605d17923e81a844b6。
唯一仓库=G:/CODEX/New Manga；
branch=agent/zcode/M2-DERIVED-GC-2；
worktree=G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode；
common-dir=G:/CODEX/New Manga/.git。

释放前 main=02ff655b64b3835bed7207bc26b723547c1febdb；
释放前 Owner HEAD=e093f0106bf62476c640dbcf8bb47448c8cc644c，均 clean。
依赖 GC-1@44859014、RC4@0a7e0d5b、设计 merge@ad75fadc 的 ancestry 检查 EXIT0。
设计 base 至释放前 main 的 src/apps/tests/packaging/requirements.txt 差量为零。

正式 release commit 及快进后的实测 HEAD 在提交后追加，避免自引用 hash；
同步未核验前 Owner 不开始。完整指令见 zcode-instruction.md。
AC/G1-G7/native/产品测试全部 planned / NOT_RUN；本次仅治理检查。

下一步：ZCode 核对 release HEAD/clean/common-dir/Task ready 后认领 in_progress，
按冻结范围实施并交固定 head、verification、Handoff；
真实非作者 DSH Review 条件闭合后，由 Codex 集成并验证才 done。

## 释放后实际恢复点（已同步）

release_commit = 5896db8c64b90b53b015eb9c46c7dab6ab29210b
Owner worktree HEAD = 5896db8c64b90b53b015eb9c46c7dab6ab29210b
branch = agent/zcode/M2-DERIVED-GC-2
worktree = G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode
common-dir = G:/CODEX/New Manga/.git
Working Tree = clean
TaskStatus = ready
ExecutionState = IDLE / AWAITING_OWNER_CLAIM
Resume Safety = RESUME_SAFE

Codex 实际执行 merge --ff-only，EXIT0；从 e093f010 快进到以上固定 release。
设计 base 保留 ad75fadc；release 含治理增量。ad75fadc 至 release 的产品
src/apps/tests/packaging/requirements.txt 差量为零，git diff --check EXIT0。
详见 release-check.log。没有派发/启动 ZCode，没有运行产品或 native 测试。

本实测记录和完整指令在主仓库后续纯治理提交追加；Owner checkout 固定留在
上述 release commit，不要求同步追加证据提交。该后续治理提交只填恢复点，
不改变授权、allowed_paths、设计或产品代码；主 Plan/STATUS 与 Owner release 一致。
Owner checkout 中本文件的提交后 hash 占位以此主仓库追加记录为准；
可直接核对本固定 release，不猜最新 main，不 merge 他人变更。
