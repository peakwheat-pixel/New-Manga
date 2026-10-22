# 当前恢复点

2026-10-22 / dsh epoch 10（lease `37230d7822a141fcae8f46acd7841890`）/ GIT-MAINLINE-CONVERGENCE-1。
TaskStatus=`blocked`；resume_status=`blocked`；ExecutionState=CHECKPOINTED；RESUME_SAFE。
canonical main `G:/CODEX/New Manga`；common `.git`；最近提交 `3264e0b61ea509ff1cd0db46be85567a0a0adb25`（实际 HEAD 启动时核对）。

## 本轮已完成（dsh 接管后）

1. **原子接管**：`coordinator-lease.py takeover --agent dsh --expected-epoch 9` → TAKEN_OVER，epoch 10，lease `37230d78…`；helper selftest 127 passed。原 Codex epoch 9 正常交接，无并发争写迹象（HEAD/tracked/分支数与交接快照一致）。
2. **GOV-RESIDUAL-RUNTIME-IDENTITY-1 `done`**（只读取证）：
   - 生产审计 7 项错误完整复现并逐项固定身份；`%TEMP%`/`%APPDATA%` 历史展开值由其他 Task 的 tracked 明文记录 + 当前字节 SHA-256 交叉校验证明。
   - 结论：**唯一真实保护缺口 = `C:/Users/49745/AppData/Roaming/com.newmanga.m2rc1.desktop` 的 catalog/data/derived（真实用户数据，hits=0）**；其余五项无现存资源、无缺口；七项均技术可解、**0 项需用户裁决**。
   - r1 `changes_requested`（R-001 运行记录矛盾 / R-002 自指两行 / R-003 导航漂移）→ 全部返修；r2 **approved** `8e31aaa1d`；集成复验同点 PASS。
3. **GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1 `in_review`**（实施）：
   - 新增 `tools/governance/residual-runtime-identity.json`（7 binding、canonical SHA `5a47481d…`）与 `_apply_residual_runtime_identity`（挂在 HIE 阶段之后）+ 12 个测试。
   - **实测 7 errors → 0**（2639/1936/7/285 → 2648/1939/0/292，exit 2→0）；保护根 1936 → 1939（新增 APPDATA 三根）；旧集合为新集合真子集；无通配/环境变量展开。
   - 治理 check PASS(2 warnings)、`git diff --check` 0、12/12 + 既有治理测试全绿；真实资源操作 0。
   - 固定 head `3264e0b61`；Antigravity 独立审查进行中（结果未回；**未 approved 前不得 done**）。
4. **收敛增量盘点**：`verification/GIT-MAINLINE-CONVERGENCE-1/delta-20261022.md`（新增证据，不改既有）。
   - 103 heads = main + 83 A（已完整并入、独有提交 0）+ 19 D（保留待裁决）；B/C = 0。
   - 142 worktrees = 135 基线 + 6 治理 Task + 1 本日实施 Task；其中 `WORKSPACE-CLEANUP-TOOL-HARDENING-1` 是 clean 且无独有提交的技术候选。
   - 真实删除/迁移/归档/GC/prune/push/reset/stash = **0**。

## 保护与禁令（全部有效）

r212 禁令、五广域根整体保护、P22 untracked 内容、旧 pin、六个 DSH 旧探针、用户未提交内容（1246+ untracked）全部原样保留；未 push、未 GC/prune、未实施任何清理。

## 恢复位置

- 父 Task 恢复点：本文件；盘点增量：`verification/GIT-MAINLINE-CONVERGENCE-1/delta-20261022.md`。
- 既有全 refs 备份 `all-refs-56272e40b.bundle` 截至 `56272e40b`，**不覆盖本轮提交**；D-1 要求先建新备份。
- 本日实施开发 worktree：`G:/CODEX/New Manga.workspace/worktrees/GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1`（分支 `codex/gov-residual-runtime-identity-impl-1`，PRESERVE_REFERENCED，不合并不删除）。

## 下一节点与最小裁决

- 立即可做：等待并处理 Antigravity 对 `3264e0b61` 的 Review；approved → 集成复验 → `GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1` done；若 `changes_requested` → 按最小修正返修并复审。
- 需要用户裁决（**未执行，不在本轮推进**）：`delta-20261022.md` §6 的 D-1（新全 refs 备份 + 删除 83 条已并入分支）、D-2（确认 19 条 D 类继续保留）、D-3（clean 且无独有提交的工作树退出）、D-4（不建议解除五广域根保护/r212）。
- **尚未达到只剩 main**；在 D-1/D-3 获授权并完成「新备份 + 占用核实」前，不执行任何真实收敛。

## 2026-10-22 第二轮（同一会话继续，dsh epoch 10）

- 工作树逐项安全盘点 142/142：38 clean、104 dirty/untracked、118 独有提交 0、24 有独有提交；**26 个安全退出技术候选**（clean + 独有提交 0 + 无进程占用），清单见 `delta-20261022.md` §9.1。
- 19 条 D 类分支证据深化：**19/19 均未被当前 `doc/tasks`/`doc/handoffs` 引用**；仅 `agent/zcode/T3.2.1-repair-13` 含 8 个 Legacy 路径（不得重新引入）。
- **新全 refs 备份已创建并验证**：`all-refs-352410640c.bundle`（239,944,235 B，SHA-256 `35869bc3442be3ab2af78da3a09d927d30701e70db262b33654f3aa8eadcc6cd`）；221 refs → 空 bare 仓库恢复 221 refs、missing 0 / extra 0、`fsck --full` clean。**D-1 的「新备份 + 恢复验证」前置已满足**。
- 新增证据：`worktree-inventory-20261022.json`、`unmerged-evidence-20261022.json`、`backup-all-refs-352410640.json`/`.log`；`delta-20261022.md` 追加 §9。
- 真实删除/迁移/归档/GC/prune/push/reset/stash：0。
- **仍未达到只剩 main**；等待 D-1（删 83 条已并入分支）/ D-2（保留 19 条）/ D-3（26 个工作树退出）的用户裁决。
### 执行链修正（2026-10-22，第 2 轮）

- 交叉核对 104 heads 后修正结论：**当前可安全 `git branch -d` 的分支为 0 条**；唯一技术上可删的 `antigravity/P09-AC3-DELETE-HARDEN-1` 是 WORKSPACE_GOVERNANCE 明确保留的旧主线。82 条已合并分支**仍被工作树检出**，Git 拒绝删除。
- 正确顺序：**D-3（工作树退出）→ 重新核对 → D-1（分支删除）**。26 个 clean 候选中 20 个检出分支，退出后可使 20 条分支变为可删；6 个是 detached HEAD，退出后不释放分支。
- `doc/WORKTREE_SAFETY_INVENTORY.md` 已追加 Stage 10（只读刷新，未删除/未移动/未 prune 任何工作树）；`delta-20261022.md` 追加 §10 执行链修正。
- 证据：`branch-deletion-readiness-20261022.json`（104 heads 交叉核对）。
- 真实删除/迁移/归档/GC/prune/push/reset/stash：0；**仍未达到只剩 main**。
### 用户授权「全部」后的执行（2026-10-22）

- 授权：用户回复「授权全部」，覆盖 D-1/D-3。D-2（20 条未合并分支）保留；D-4（解除保护/r212）**未执行**（不建议且不需要）。
- **D-3 工作树退出 26/26 成功**（`git worktree remove` 无 --force，0 拒绝）：142 → **116**。
- **D-1 分支删除 20/20 成功**（`git branch -d` 非 -D，0 拒绝）：104 → **84**；保留旧主线 `antigravity/P09-AC3-DELETE-HARDEN-1`。
- 可恢复性已实测：20 条被删分支的 tip 在备份恢复仓中 **20/20 可读、0 缺失**。
- 复验：声明审计 **0 errors / 1946 保护根**；治理检查 **PASS (2 warnings)**；tracked 工作区干净。
- 未执行：`git worktree prune`、GC、push、reset、stash；.git/worktrees 下 37 个历史孤儿元数据保留。
- 剩余：84 heads = main + 62 检出 + 20 未合并 + 1 旧主线；**仍未达到只剩 main**。
### 第二批收敛（2026-10-22）

- 分类 115 个非 main 工作树：CLEAN 12 / BUILD_ONLY 22 / USER_CONTENT 18 / MIXED 63。
- **BUILD_ONLY 退出 20/22 成功**（ignored 全部为 node_modules/target/dist/__pycache__/.pytest_cache）；2 个被 git 拒绝并保留（含 Review 证据 / 构建日志）。
- **分支删除 20/20 成功**：heads 84 → **64**；worktree 116 → **96**。
- 复验：声明审计 0 errors / 1946 保护根；tracked 工作区干净。
- 未执行：prune、GC、push、reset、stash；USER_CONTENT/MIXED 工作树与 20 条未合并分支保留。
- 剩余 64 heads = main 1 + 检出 42 + 未合并 20 + 旧主线 1；**仍未达到只剩 main**。
### 第三批收敛（2026-10-22）

- 退出 12/12「tracked/untracked/ignored 全为 0」的 CLEAN 工作树（`worktree remove`，无 --force，0 拒绝）：worktree 96 → **84**。
- 分支不删除（D-2 保留 20 条未合并分支）：heads 保持 **64**。
- 3 个 detached HEAD 的 commit 在备份恢复仓中逐条验证可读（3/3）。
- 复验：声明审计 0 errors / 1946 保护根；治理检查 PASS；tracked 干净。
- 未执行：prune、GC、push、reset、stash；五广域根保护与 r212 不变。
- 累计：heads 104→64、worktree 142→84；**仍未达到只剩 main**（剩 42 检出 + 20 未合并 + 1 旧主线）。
### 第四批：detached 工作树核查（2026-10-22）

- 84 个注册工作树中 30 个 detached；逐项检查后 **HAS_CONTENT 30 / EMPTY 0 / BUILD_ONLY 0**。
- 内容以 `verification/` 下 Review 证据为主，另有 3 个破损 checkout（2804 deleted）。
- **0 个可退出，本轮删除数为 0**；30 个 detached HEAD 在备份恢复仓中全部可读。
- 当前：heads **64** / worktrees **84**；复验 0 errors、check PASS、tracked 干净。
- **仍未达到只剩 main**：剩余资源全部承载未提交证据、未提交用户内容或未合并历史。
### 第五批：冗余副本退出与边界（2026-10-22）

- 对 81 个工作树逐文件比对 main blob：**仅 3 个**全部未提交文件为冗余副本（SAFE_EXIT）。
- 3 个已退出（唯一一次 `worktree remove --force`，删除对象均为已提交内容副本）：worktree 84 → **81**。
- 其余 **78 个工作树含独有内容**（证据/诊断输出/构建日志/数据库样本），自动化收敛**到此为止**。
- 复验：声明审计 0 errors / 1946 保护根；治理检查 PASS；tracked 干净。
- 当前：heads **64** / worktrees **81**；**仍未达到只剩 main**，剩余三类资源需逐项裁决。
