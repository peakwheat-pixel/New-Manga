# P02 文档改动来源调查（用户要求 · Coordinator 取证报告）

- **发起**：用户 2026-10-18 裁决 —— 对 `doc/tasks/P02.md`、`doc/tasks/P02-NEW-TIME-X6.md`、`doc/tasks/P02-NEW-TIME-X6-BUILD-CARGO.md` 三文件的未提交改动，用户明确回答 **"不是我改的"**，要求调查来源并如实上报。
- **执行**：Coordinator = dsh，epoch 8
- **方法**：只读取证（`git diff` / `git hash-object` / `git log --find-object` / `git reflog` / 文件系统 mtime 扫描）。**未修改、未恢复、未暂存任何文件。**

## 1. 直接结论（先说结论）

**这三个文件的未提交改动不是用户手动编辑产生的，而是 2026-10-17 20:30:51 一次「程序化批量文件写入」的结果；其内容相对当前 HEAD 是「更旧的历史状态」。**

进一步地：**它们并非孤立事件** —— 同一秒被写入的正好是上一会话所称的 **"用户 20 个具名 dirty 文件"全部成员**。因此上一会话把该集合定性为"用户的未提交改动"并设为绝对禁区，**很可能是一次误判**。

## 2. 关键证据

### 2.1 同一秒批量写入

扫描仓库（排除 `.git`）中 mtime 落在 `2026-10-17 20:25–20:35` 的文件：

| 时间 | 文件 |
|---|---|
| 20:30:50 | `verification/FEAT-CREATE-3/dsh-review-r1.md` |
| **20:30:51** | **恰好 20 个文件**：`.qoder-credits/report.json`、`AGENTS.md`、`doc/00_INDEX.md`、`doc/01_FUNCTIONAL_ARCHITECTURE.md`、`doc/03_DATA_MODEL.md`、`doc/04_USER_FLOW.md`、`doc/06_TRANSLATION_PIPELINE.md`、`doc/09_COLLABORATION.md`、`doc/11_ARCHITECTURE_MAPS.md`、`doc/12_ROADMAP.md`、`doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md`、`doc/WORKTREE_SAFETY_INVENTORY.md`、`doc/templates/HANDOFF.md`、`doc/templates/REVIEW.md`、`doc/templates/TASK.md`、`doc/tasks/P02.md`、`doc/tasks/P02-NEW-TIME-X6.md`、`doc/tasks/P02-NEW-TIME-X6-BUILD-CARGO.md`、`verification/P19/codex-review-r2.md`、`verification/PROJECT-ROADMAP-20261008/ROADMAP.md` |
| 20:30:59 | `apps/desktop/src-tauri/target/**/out/acl-manifests.json`、`capabilities.json`（构建产物） |

**这 20 个文件与交接文件 §6"用户 20 个具名 dirty 文件"清单逐项完全一致。** 没有任何人类能在同一秒手改 20 个文件。

### 2.2 内容方向：更旧的历史状态

`doc/tasks/P02.md` 的 diff 方向（`-` = HEAD，`+` = 工作区）：

```
-  Build/Cargo Task `P02-NEW-TIME-X6-BUILD-CARGO` 已集成并获 DSH/Codex official convergence APPROVED…
-  新建独立 Task `P02-NEW-TIME-X6-AC1-AC7`… 当前状态=`in_progress / DISPATCHED`…
+  当前唯一 READY 节点为 `P02-NEW-TIME-X6-BUILD-CARGO`，Owner=ZCode … 等待 Build worktree、输入冻结与 AGENT_PREFLIGHT。preflight PASS 前不启动 Build。
+  恢复点见 `verification/P02-NEW-TIME-X6/checkpoint.md` 与 `verification/P02-NEW-TIME-X6-POSTRUN-REVIEW/checkpoint-r1.md`。
```

工作区版本描述的是 **Build Task 尚未启动**时的状态，而 HEAD 已记录它"已集成并 APPROVED" —— 即**工作区内容更旧**。

### 2.3 blob 级溯源

`git hash-object`（磁盘字节）逐个比对，并 `git log --all --find-object` 搜索该 blob 是否存在于任何 commit：

| 文件 | 工作区 blob | 是否存在于历史 |
|---|---|---|
| `doc/tasks/P02-NEW-TIME-X6-BUILD-CARGO.md` | `e0b7d869a72084fa770994380c65f1bf92fdd637` | **是** —— `cb452b7db`（2026-10-14 14:43 `docs(P02): record frozen Build input gate`）、`83979dac1` |
| `doc/00_INDEX.md` | — | 是 —— `aa629c7c7` |
| `doc/09_COLLABORATION.md` | — | 是 —— `aa629c7c7` |
| `doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md` | — | 是 —— `aa629c7c7` |
| `doc/01_FUNCTIONAL_ARCHITECTURE.md`、`03_DATA_MODEL.md`、`04_USER_FLOW.md`、`06_TRANSLATION_PIPELINE.md` | — | 是 —— `000cbfe99` |
| `doc/tasks/P02.md` | `e232686a1d4dd642498153e61ecf8f8a38d73d18` | **否**（不在任何 commit） |
| `doc/tasks/P02-NEW-TIME-X6.md` | `defc7318b39881b446932e495595418ab463c940` | **否** |
| `AGENTS.md`、`11_ARCHITECTURE_MAPS.md`、`12_ROADMAP.md`、`WORKTREE_SAFETY_INVENTORY.md`、`templates/*.md`、`P19/codex-review-r2.md`、`ROADMAP.md` | — | 否 |

→ `BUILD-CARGO.md` 精确等于 **2026-10-14** 的版本；其余多为"历史版本 + 局部差异"的混合体，**不是单一 commit 的检出结果**。

### 2.4 排除 git 操作路径

- `git reflog --all` 中 **2026-10-17 20:xx 无任何记录**（该日最早可见记录为 22:45）；
- `.git/index`、`ORIG_HEAD`、`HEAD` 的 mtime 均**不是** 2026-10-17 20:30；
- 因此可排除 `commit` / `checkout <branch>` / `reset` / `merge` 这类会改写 HEAD 或 reflog 的操作。
- 注意：`git checkout <commit> -- <paths>` 或 `git restore --source=<commit> -- <paths>` **不写 reflog**，无法据此排除；但 §2.3 显示多数文件的内容**不等于**任何单一 commit，故"单条 pathspec 检出"不足以解释全部差异。

### 2.5 时间上与谁重叠

`agent-output/codex/FEAT-CREATE-3/` 显示 Codex 的该次会话为 `20:16:00`（prompt）→ `20:31:17`（result），20:30:51 落在其区间内；但 Codex 的交付说明与其全部产物路径都在 **worktree** `G:/CODEX/New Manga.workspace/worktrees/FEAT-CREATE-3/`，其 result/stdout 中**没有任何**主仓库这 20 个文件的写入记录。紧邻 20:30:50 的 `verification/FEAT-CREATE-3/dsh-review-r1.md` 是**上一会话 DSH Coordinator 自己的 review 产物**，位于主仓库。

## 3. 能够确定与不能确定的

**能够确定**：
1. 不是用户手动编辑（用户已确认 + 一秒内 20 文件 + 内容为历史状态）；
2. 是一次程序化批量写入，时刻 `2026-10-17 20:30:51`；
3. 其中 `P02-NEW-TIME-X6-BUILD-CARGO.md` 精确回退到 `cb452b7db`（10-14）版本；
4. 其余多数为"历史版本混合体"，不对应任何单一 commit；
5. 该集合恰等于上一会话认定的"用户 20 个 dirty 文件"全集 → **该定性缺乏依据**。

**不能确定（如实声明）**：
- 具体执行的命令与调用方（无 Agent 会话原始日志；`git reflog` 与 `.git/index` mtime 均不支持 git 操作路径）。**不从现有证据推断出唯一的操作者指令，也不臆造**。

## 4. 影响与风险

1. 这 3 个 P02 文件当前内容**与项目真实状态矛盾**（描述 Build Task 尚未启动），会成为后续 Agent 与审计者的错误事实来源。
2. 上一会话把它们设为"绝不可动"，实际上**把一个错误状态固化成了禁区**，且掩盖了它的真实来源。
3. 若 20 个文件中还有其它同类"历史回退"，其影响需逐一核对（本报告仅逐项给出 blob 归属，未逐份评估内容正确性）。

## 5. 建议（待用户裁决，本报告不执行任何动作）

1. **不擅自恢复**：在用户裁决前，这 20 个文件保持现行字节不变（本轮已遵守）。
2. 建议立专项 Task 处置，范围建议为：
   - 逐一评估 20 个文件的工作区内容 vs HEAD 的实际差异与正确性；
   - 明确哪些属于"应丢弃的历史回退"、哪些可能含真实新内容（如 `.qoder-credits/report.json` 的工作区版本 `generatedAt=2026-10-08` **比** HEAD 的 `2026-09-26` **更新**，方向相反，需单独判定）；
   - 恢复动作若获授权，须逐文件留证（改动前后 sha256）并作为独立 commit。
3. 无论结论如何，交接与 §6 清单中的定性应更正为"来源未经证实的 dirty 文件"，避免后续 Agent 再次误判。

## 6. 复现命令

```powershell
Set-Location 'G:\CODEX\New Manga'
# 1) mtime 批量窗口
Get-ChildItem -Recurse -File -Force | Where-Object {
  $_.LastWriteTime -ge (Get-Date '2026-10-17 20:25:00') -and
  $_.LastWriteTime -le (Get-Date '2026-10-17 20:35:00') -and $_.FullName -notmatch '\\\.git\\' } |
  Sort-Object LastWriteTime | Select-Object LastWriteTime, FullName
# 2) blob 溯源
git hash-object -- doc/tasks/P02-NEW-TIME-X6-BUILD-CARGO.md
git log --all --oneline --find-object=e0b7d869a72084fa770994380c65f1bf92fdd637
# 3) 排除 git 操作
git reflog --date=format:'%Y-%m-%d %H:%M:%S' --all | Select-String '2026-10-17 2[0-9]:'
```

**未执行**：本轮未修改/恢复/暂存/提交任何文件；未删除任何内容。
