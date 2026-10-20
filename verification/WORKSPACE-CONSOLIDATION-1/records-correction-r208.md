# R208 数值与 AC 更正底稿（records-correction）

- task_id：`WORKSPACE-CONSOLIDATION-1`
- 角色：DSH teammate `records-correction`（只读实测；只写本文件与 `measurements-r208.json`）
- 实测时点：2026-10-20T21:34–21:47 +08:00
- 复核 HEAD：`3947d63447457fe3ef8d3587942e632724ab3d72`（`3947d6344`），分支 `antigravity/P09-AC3-DELETE-HARDEN-1`
- tracked dirty / staged：`0 / 0`；默认 `git status --porcelain` 条目 `1239`，`-uall` 条目 `1595`
- 权威 Review：`verification/WORKSPACE-CONSOLIDATION-1/codex-review-r208.md`（`decision: changes_requested`）
- 机器可读实测：`verification/WORKSPACE-CONSOLIDATION-1/measurements-r208.json`
- 结论性质：**更正底稿与 AC 重评建议**，不是批准、不是自我审查、不修改任何 `doc/**`。

---

## 0. 摘要（先给结论）

| 项 | 本轮独立实测 | 与 Review / 原记录的关系 |
|---|---|---|
| 注册 worktree | **132**（`git worktree list --porcelain` 计 `worktree ` 行） | 原记录 126 是回建前时点；132 = 213 − 50 − 37 + 6 |
| 本地分支 | **93**（74 已并入 + 19 未并入） | 与 Review 一致；418 − 323 − 2 = 93 |
| 19 条未合并分支 | **19/19** 均有 `archive/*` tag、tag tip 与分支 tip 相同、bundle 存在、`git bundle verify` **exit 0** | Review 附录 C 结论成立；本轮逐条给出完整 SHA |
| 76 条原归档 corpus | 逐分支 `rev-list mainline..tag` 计数合计 **1,223**；去重提交集合 **320** | 与 Review Q4 一致；**口径 A** |
| 当前 archive ref 总集 | **77 tags / 1,225 合计 / 322 去重** | P03 返修新增 2 提交导致；**口径 B，不得与 A 混用** |
| 删除收据逻辑字节 | `31,493,644,833 + 21,636,208,040 = 53,129,852,873 B` = **49.481031 GiB**（≈53.13 GB） | 与 Review 算术一致；但**不是物理净释放** |
| `workspace/worktrees` 移除 | 实际移除 **7 处**，其中 **4 处回建**；合计 13,225,660,979 B | 推翻「workspace/worktrees 完全没动」 |
| `task-envs` | 总逻辑 **3,880,296,828 B（3.613808 GiB）**，6 个直接子目录；检测环境 `M2-PROD-DETECT-ENV-1` 仅 **138,129,041 B（131.73 MiB）** | 不得把整个 3.61 GiB 都称检测环境 |
| 57/57 保护名 | **57/57** 名称仍对应已注册 worktree 且目录存在 | 仅名称子集；不覆盖 18 个受影响资源 |
| 18 个受影响资源 | 7 存在 / 11 原位置缺失；P06 保留子树缺失；6 个仅部分回建 | 与 Review Q1 一致（独立存在性复核） |
| AC1/AC2/AC6/AC9 | **均不能判 MET**（建议 PARTIAL；AC3/AC7 另有保护/安全目标 FAIL） | Task 里 AC1/AC2/AC6/AC9 的 `<<MET>>` 与证据冲突 |
| 治理检查 | `PASS (4 warnings)`，exit **0** | 当前 warning 基线；本文件写入会使未登记清单增加 2 个文件名 |

**关于派发说明中的「41 个 archive bundle」**：Lead 已确认该数字是派发说明的笔误（2026-10-20），正确口径为 **76（`archive-manifest.json` 的原分支归档 corpus）**，返修期 P03 保全后为 **77**。本项目所有证据中不存在「41 个 bundle」的口径，因此**不作为差异项**，也不影响下列 76/77、1,223/320、1,225/322 的口径。

**写入后复测（2026-10-20T21:52）**：写入本文件与 `measurements-r208.json` 后，HEAD `3947d6344`、tracked dirty `0`、staged `0`、93 分支、77 tags、132 worktree 均未变；默认 `git status --porcelain` 为 1243 条（+2 本交付物，另 +2 为并发协作者新增的 `incident-ledger-r208.md/.json`）；治理检查仍为 `PASS (4 warnings)`、exit 0，未登记清单新增本文件与 measurements（Owner 需登记）。

---

## 1. 两个 archive 口径：必须分开写、分开引用

这是本轮最容易误引的数字，先单列。

### 口径 A：原 76 个分支归档 corpus（Review Q4 与本 Task 原记录的口径）

- 定义：`archive-manifest.json` 的 `archived[]` 的 **76 条 branch 记录**，**排除**返修期新增的 `archive/P03-review-prep-112495c7`。
- 算法：对 manifest 中每个 tag 执行 `git rev-list <mainline>..<tag>`，逐分支计数求和；提交集合取并集再求大小。
- 实测：**sum = 1,223；union = 320**。
- 复算命令（按 manifest 循环，而不是按当前全部 tag）：

```powershell
@'
import json, subprocess
repo=r"G:/CODEX/New Manga"; ml="antigravity/P09-AC3-DELETE-HARDEN-1"
def git(*a):
    return subprocess.run(["git","--no-optional-locks",*a],cwd=repo,capture_output=True,text=True,encoding="utf-8",errors="replace")
man=json.load(open(r"verification/WORKSPACE-CONSOLIDATION-1/archive-manifest.json",encoding="utf-8"))
s=0; u=set()
for e in man["archived"]:              # 76 条，排除 P03
    ids=git("rev-list",f"{ml}..{e['tag']}").stdout.split()
    s+=len(ids); u.update(ids)
print("SCOPE-A tags=%d sum=%d union=%d"%(len(man["archived"]),s,len(u)))
'@ | C:/Python314/python.exe -B -
# 实测输出：SCOPE-A tags=76 sum=1223 union=320
```

### 口径 B：返修后当前全部 archive ref（含 P03）

- 定义：`git tag -l 'archive/*'` 当前全部 **77** 个 tag。
- 实测：**sum = 1,225；union = 322**。
- 差集正是 P03 两个提交：`0a25ceb4577158d9dff184776ff4599e74e25c57`、`112495c70ff8a9c50fe00f4cd2eaa861d9a11b69`。

```powershell
@'
import json, subprocess
repo=r"G:/CODEX/New Manga"; ml="antigravity/P09-AC3-DELETE-HARDEN-1"
def git(*a):
    return subprocess.run(["git","--no-optional-locks",*a],cwd=repo,capture_output=True,text=True,encoding="utf-8",errors="replace")
tags=git("tag","-l","archive/*").stdout.split()
s=0; u=set()
for t in tags:
    ids=git("rev-list",f"{ml}..{t}").stdout.split()
    s+=len(ids); u.update(ids)
print("SCOPE-B tags=%d sum=%d union=%d"%(len(tags),s,len(u)))
'@ | C:/Python314/python.exe -B -
# 实测输出：SCOPE-B tags=77 sum=1225 union=322
# extra_tags = ['archive/P03-review-prep-112495c7']
# extra_commits = P03 两提交（见上）
```

### 引用规则（给 STATUS / Plan / Task / Inventory 作者）

- 写「1,223 是分支计数合计、去重 320」时，必须限定 **「76 个 manifest 分支归档 corpus」**，并注明用 manifest 列表循环。
- 写当前状态时必须写 **「77 个 archive ref（含 P03 返修保全），1,225 合计 / 322 去重」**。
- 两个数字不可互相替代；更不可把 1,223 当去重提交数，也不可把 1,225 冒充 Review 口径。
- P03 的 tag/bundle 由另一协作者在 Review 之后创建（bundle mtime `2026-10-20 21:32:49`，证据：`p03-preservation-r208.md`）；本文件已独立 `git bundle verify` 复核为 exit 0，但**不把该证据当作我自己的交付**。

---

## 2. 与 Review 的数值差异（逐项、含原因）

| # | 项 | Review r208 | 本轮实测 | 差异 | 解释 |
|---|---|---|---|---|---|
| 1 | bundle 数量/字节 | 76 / 22,106,711 B | **77 / 22,111,102 B** | +1 / +4,391 B | 返修期新增 `P03-review-prep-112495c7.bundle`（21:32:49）。Review 的 76 在新增之前成立，不是算错 |
| 2 | manifest 提交合计/去重 | 1,223 / 320 | **1,223 / 320**（口径 A）；**1,225 / 322**（口径 B） | 口径 A 一致；口径 B +2 | P03 两提交 |
| 3 | worktrees 逻辑字节 | 120,225,570,583 B / 111.97 GiB / 952,193 files；7 处权限拒绝 | **120,499,443,541 B / 112.223852 GiB / 954,980 files；0 处权限拒绝** | +273,872,958 B / +2,787 files | 本扫描晚于 Review，且 7 处原拒绝子树本次可读；未逐路径归因（NOT_RUN） |
| 4 | `git fsck` dangling | 382 blob / 75 tree / **157** commit = 614 | 382 blob / 75 tree / **156** commit = 613 | −1 commit | P03 tag 使两提交可达本应 −2；实测 −1，+1 未归因（NOT_RUN）。exit 0 与「无 corruption」不变 |
| 5 | 治理 warning | 写报告后 PASS (4 warnings) | **PASS (4 warnings)**，exit 0 | 一致 | 未登记证据文件在同一 warning 清单中 |
| 6 | 18 个受影响资源 | 18 source / 15 删除根 / 12 完整性缺口 | 18 source、15 根；**11 个原位置缺失 + P06 子树缺失 + 6 个部分回建** | 一致 | 本轮独立 `os.path.isdir` + P06 子树 + 6 处 HEAD 核对 |
| 7 | 49.48 GiB | 逻辑合计，不能认证物理净释放 | **49.481031 GiB = 53.129853 GB**；收据匹配；无卷空间前后差值 | 一致 | 删除后 6 处回建，回建占用未扣 |
| 8 | 82 个 dirty worktree | Review 未展开 | inventory `dirty>0` = **82**；apply `refused` = **105**（68 dirty + 37 permission）；57 protected + main skipped | 文档口径需更正 | 「82 未碰」是 inventory 口径；apply 实际拒绝 105，其中 37 条是 Permission denied，不是 dirty |

> 派发说明中的「41 个 archive bundle」经 Lead 确认系笔误（正确口径 76/77），**不列入差异项**。

补充：19 条未合并分支的逐分支计数合计 **351**、去重 **224**（子集，不与上述口径混用）；Review 附录 C 的逐条数字与本轮一致。

---

## 3. 关键数字的复算明细

### 3.1 注册 worktree = 132，且数量闭环成立

```powershell
(git worktree list --porcelain | Where-Object { $_ -match '^worktree ' }).Count   # 132，exit 0
```

闭环（用 `inventory.json` 213 条原记录对当前注册表求差）：

```text
213（删除前注册）
- 50（目录实际移除）
- 37（仅移除登记；目录仍在、.git 不再存在）
+  6（回建并重新注册：GOV-PIN-LINEAGE-1/worktree、FEAT-CREATE-1/2/4、P19-UI-FIX-2、P02-real-webview-harness-antigravity）
= 132（当前注册）
```

独立验证：`inventory` 中未再注册的 81 条 = 44 条目录已缺失 + **37 条目录仍存在**；50 条移除目录中 6 条重新注册（44 条未注册）。当前注册表**没有** inventory 之外的路径（`cur_not_in_inventory = 0`）。

### 3.2 本地分支 = 93；未合并 = 19

```powershell
(git show-ref --heads).Count                                  # 93
# 逐条：git merge-base --is-ancestor <branch> antigravity/P09-AC3-DELETE-HARDEN-1
# 结果：74 exit 0（已并入） / 19 exit 1（未并入）
```

删除收据：`deleted = 323 = 267(-d) + 56(-D)`；`skipped = 95 = 92 checked out in a worktree + 2 reserved for AC8 + 1 mainline`；另 `main`、`master` 单独删除 2 条；净删除 **325**，`418 − 325 = 93`。

### 3.3 19 条未合并分支：tag / 完整 tip / bundle / verify exit

全部 **19/19** 满足：`archive/*` tag 存在、`tag tip == branch tip`、bundle 文件存在、`git bundle verify` **exit 0**。明细见附录 C；逐分支计数合计 **351**，去重 **224**。

### 3.4 49.48 GiB：只是「删除前递归逻辑字节合计」

```text
worktree-removal.json removed[] 合计：31,493,644,833 B（29.330742 GiB）
workspace-cleanup.json removed[] 合计：21,636,208,040 B（20.150289 GiB）
合计：53,129,852,873 B = 49.481031 GiB = 53.129853 GB
```

- 两份收据的字段只有 `bytes`，**没有删除前后 G: 卷可用空间差值**。
- 没有 junction / 硬链接分摊说明；worktrees 目录存在 1,520 个 reparse point（本次扫描不跟随）。
- 删除后 6 个 worktree 回建，回建占用未从合计中扣除。
- 因此：**只能写「删除前递归逻辑字节合计 49.48 GiB」，不能写「实测物理净释放 49.5 GB」**。

### 3.5 `workspace/worktrees` 实际移除 7 处，4 处回建

来自 `worktree-removal.json` 的 `removed[]` 过滤 `G:/CODEX/New Manga.workspace/worktrees/`：

| path | bytes | 原 branch | 现在存在 | 回建 |
|---|---:|---|---|---|
| `.../workspace/worktrees/FEAT-CREATE-1` | 305,714,018 | `codex/FEAT-CREATE-1` | 是 | 是 |
| `.../workspace/worktrees/FEAT-CREATE-2` | 1,601,245,026 | `codex/FEAT-CREATE-2` | 是 | 是 |
| `.../workspace/worktrees/FEAT-CREATE-4` | 5,045,303,306 | `codex/FEAT-CREATE-4` | 是 | 是 |
| `.../workspace/worktrees/P02-NEW-TIME-X6-AC1-AC7` | 291,116,178 | `agent/zcode/P02-NEW-TIME-X6-AC1-AC7` | 否 | 否 |
| `.../workspace/worktrees/P15-C1-review` | 302,460,207 | (detached) | 否 | 否 |
| `.../workspace/worktrees/P19-AC3-1` | 308,738,904 | `codex/P19-AC3-1` | 否 | 否 |
| `.../workspace/worktrees/P19-UI-FIX-2` | 5,371,083,340 | `codex/P19-UI-FIX-2` | 是 | 是 |
| **合计** | **13,225,660,979** | | | **4** |

结论：**不得写「workspace/worktrees 完全没动」**；Phase B 实际动了 7 处，且其中 4 处已回建。

### 3.6 task-envs：总逻辑字节、子目录、检测环境边界

| 直接子目录 | 逻辑字节 | 占总量 |
|---|---:|---:|
| `M2-PROD-DETECT-ENV-1` | **138,129,041**（131.73 MiB） | 3.56% |
| `P02-NEW-TIME-X6-AC1-AC7` | 305,640,790 | 7.88% |
| `P02-NEW-TIME-X6-BUILD-CARGO` | **2,328,053,874** | 60.00% |
| `P04` | 364,553,476 | 9.39% |
| `P04-integration` | 364,553,476 | 9.39% |
| `P22-REBASE-1` | 379,366,171 | 9.78% |
| **合计** | **3,880,296,828**（3.613808 GiB） | 100% |

- 扫描方法：Python `os.scandir/lstat`，不跟随 reparse/junction；104,117 个普通文件、22,923 个目录、0 个 reparse、0 个权限拒绝。
- 检测环境复核：`M2-PROD-DETECT-ENV-1/venv/pyvenv.cfg` 写明 `include-system-site-packages = true`、`home = C:\Python314`、Python 3.14.6；`transformers-5.17.0.dist-info/METADATA` 为 `Name: transformers / Version: 5.17.0`；`Scripts/python.exe` 存在。它是**全局 Python + transformers 覆盖层**，不是完全自包含环境。
- 收据中没有任何 `task-envs` 字样（4 份 receipts 的 `task-envs` 计数均为 0），未发现 task-envs 被删除。
- **不得把整个 3.61 GiB 称为「检测环境」**；检测环境仅 131.73 MiB。

### 3.7 57/57 保护名的口径边界

- `inventory.json.protected_worktree_names`：57 个名字；`worktree-removal.json.skipped[why=protected]`：57 个路径；两边 basename 集合完全相等。
- 当前 `git worktree list --porcelain` 中，57/57 都能按 basename 匹配到已注册 worktree，且目录 `os.path.isdir` 均存在。
- **边界**：这只证明「这 57 个名称子集仍注册且目录存在」，不证明：
  1. 保护枚举完整（Review Q1 已指出共享根声明、38 个 verification json + Task 表的口径）；
  2. 目录内字节未变；
  3. 能覆盖 18 个具体受影响资源——反例：`P06-GC-DISTRIBUTION-MIGRATION` 根目录仍在 57 名单内且存在，但其受保护子树 `old-runtime/worktree` 已缺失。
- **不得把 57/57 写成「保护项全在位」**。

### 3.8 18 个受影响资源：本轮独立存在性复核

- 18 条 source 中：**7 条当前存在**（6 个回建 + P06 根）、**11 条原位置缺失**（4 个 review-scratch + 7 个 temp 路径）。
- P06：`P06-GC-DISTRIBUTION-MIGRATION/old-runtime` 存在，但 `old-runtime/worktree` **不存在**。
- 6 个回建 worktree：HEAD 均匹配 `inventory` 九位前缀，均 detached，`status --porcelain -uall` 均为空；但原分支检出形态、ignored 内容、目录元数据未恢复。
- review-scratch 4 条收据合计 **14,699,110,702 B（13.689614 GiB）**；temp 4 个删除根合计 **56,994 B**（X6 根 32,624 B 已包含两个 selftest 与 capture 子路径，子路径不得重复加总）。
- X6 capture 副本独立复核：`stdout.md` 32,426 B SHA-256 `0109aed4...a3602`，`stderr.md` 0 B SHA-256 `e3b0c442...b855`，与 Review Q3 相同。
- 结论：**「8 个 temp 夹具永久丢失」不能作为既证事实**；应写「原位置缺失；副本/可重建/未证实」分类，具体 availability 见附录 D 与 Review Q3。

### 3.9 治理检查原始输出（当前 warning 基线）

```text
Shell: PowerShell
Governance scope: 13 current documents; no historical directory scan.
Task: doc\tasks\WORKSPACE-CONSOLIDATION-1.md
WARN: 存在 38 个非终态 Task（见 TASK_LEDGER）；状态字段不能证明活性，不得据此批量关闭（r38）
WARN: doc/STATUS.md 已达到预算的 80%：3152 bytes / 26 lines
WARN: doc/REBASELINE_PLAN.md 已达到预算的 80%：5997 bytes / 55 lines
WARN: evidence_dir 含未登记过程文件（归入 workspace 或列为 SOURCE_PIN）：G:\CODEX\New Manga\verification\WORKSPACE-CONSOLIDATION-1\codex-review-r208.md, G:\CODEX\New Manga\verification\WORKSPACE-CONSOLIDATION-1\p03-preservation-r208.json, G:\CODEX\New Manga\verification\WORKSPACE-CONSOLIDATION-1\p03-preservation-r208.md
Governance check: PASS (4 warnings)
EXIT: 0
```

命令：`pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/WORKSPACE-CONSOLIDATION-1.md`（只读，exit 0）。本文件与 `measurements-r208.json` 写入后会追加到同一 warning 的未登记清单，warning 数仍为 4；Owner 需在 Task 证据表登记，不能据此判失败。

### 3.10 `git fsck`

`git fsck --no-progress` → exit 0；382 dangling blob / 75 dangling tree / **156** dangling commit（合计 613 行），非 dangling 诊断 0。**dangling 不等于损坏，也不能作为「ignored/源数据未丢失」证明。**

---

## 4. AC 重评证据（AC1、AC2、AC6、AC9；同时覆盖 AC3、AC7）

规则：**没有证据的 AC 不能写 MET**。下表把 `executed`（本轮实际跑过、可复算）、`NOT_RUN`（原计划命令未执行/无原始输出）、`UNVERIFIED`（没有可核实证据）分开。判定是**建议**，最终由独立 Reviewer 裁定。

### 4.1 AC1 四表盘点（原记录 MET）

| 类别 | 证据 |
|---|---|
| executed | `inventory.json` 可读：`counts=418/342/76/213/57`；`branches=418` 条；`worktrees=213` 条；`protected_worktree_names=57`；`inventory.md` 含「AC1 四表」与六节；5 份收据齐全（archive 76、worktree-removal 50/105/58、branch-deletion 323/95、workspace-cleanup 158/5） |
| NOT_RUN | Task「测试要求」AC1 行写 `NOT_RUN`；没有任何逐条 `git rev-list --count` 的原始输出 |
| UNVERIFIED | 未跟踪逐文件大小/引用表缺失；branch 记录只有 `branch/merged/unique_commits/tip_date/checked_out_at/is_mainline`，**无原 tip SHA**；267 条已合并删除项只有 19 条有原 tip 交叉证据 |

**建议**：`PARTIAL`，不能 MET。理由：表存在且总数可复算，但不是「完整安全盘点」（R208-07 的缺口仍在）。

### 4.2 AC2 刷新权威清单（原记录 MET）

| 类别 | 证据 |
|---|---|
| executed | `doc/WORKTREE_SAFETY_INVENTORY.md` Stage 7 节存在（52–150 行），已读 |
| UNVERIFIED / 与事实冲突 | 「126」与当前 **132** 不一致；「不忽略 ignored」与默认 `git status` 不展开 ignored 的事实相反；「8 个 temp 夹具永久丢失」被现存同哈希副本与可重建固定字节反证；「workspace/worktrees 一律不动」与实际移除 7 处不符；把 1,223 当去重提交数（实际 320）；把 3.6 GiB task-envs 整体称检测环境（实际 131.73 MiB）；`fsck 0 problems` 未提 613 条 dangling；治理 warning 已从 3 变 4 |

**建议**：`PARTIAL`，不能 MET。Stage 7 必须按第 5 节的替换文本更正。

### 4.3 AC3 保护项全量枚举（原记录 PARTIAL，13 条）

| 类别 | 证据 |
|---|---|
| executed | 57/57 名称子集（见 3.7）；18 条 source 存在性（7 存在 / 11 缺失）；P06 子树缺失；review-scratch 收据 14,699,110,702 B；X6 副本 hash 复核 |
| NOT_RUN | 保护枚举的完整重建（共享根 SEC-FIX 泛化声明、38 个 verification json + Task 表） |
| UNVERIFIED | 57 名子集之外的字节完整性；7 个 temp source 的备份/恢复搜索 |

**建议**：`PARTIAL / 保护目标 FAIL`。18 个具体资源不能只写「13 条」，也不能用 57/57 盖过。

### 4.4 AC6 worktree 清理（原记录 MET）

| 类别 | 证据 |
|---|---|
| executed | 50 目录移除（移除项在 inventory 中 `dirty=0`）；105 refused = 68 dirty + 37 Permission denied；58 skipped = 57 protected + 1 main；213 − 50 − 37 + 6 = 132；6 处回建 HEAD 九位前缀匹配、detached、status 空；44 个移除目录未注册且不存在、37 个仅登记移除目录仍存在 |
| NOT_RUN | 删除时原始 `status`/`stash` stdout、stderr、退出码未保存 |
| UNVERIFIED | ignored 内容逐文件清册；protected/unique/terminal/reference 门槛是否完整落实（18 资源与 P03 detached 两提交已证否） |

**建议**：`PARTIAL`，不能 MET。

### 4.5 AC7 workspace 体积释放（原记录 PARTIAL，20.15 GB）

| 类别 | 证据 |
|---|---|
| executed | 158 项合计 21,636,208,040 B（20.150289 GiB）；50 个 worktree 合计 31,493,644,833 B（29.330742 GiB）；总逻辑 53,129,852,873 B = 49.481031 GiB；7 处 workspace/worktrees 移除，4 处回建 |
| NOT_RUN / UNVERIFIED | 无 G: 卷可用空间前后差值；无 junction/硬链接分摊；回建占用未扣；物理净释放未证实 |

**建议**：`PARTIAL / 安全目标 FAIL`；收益只能写「删除前递归逻辑字节合计」。

### 4.6 AC9 验收（原记录 MET：PASS 3 warnings / fsck 0 problems / 26 草稿）

| 类别 | 证据 |
|---|---|
| executed | governance `PASS (4 warnings)` exit 0；`git fsck` exit 0（613 dangling，0 其他诊断）；untracked `doc/tasks` 26、tracked `doc/tasks` 296；tracked dirty 0/staged 0；93 分支/132 worktree |
| NOT_RUN | bundle 恢复演练；未跟踪文件全量字节哈希 |
| UNVERIFIED / 不成立 | 保护与恢复验收（18 资源、11 缺失、6 部分回建）；「8 个永久丢失」；AC9 的 MET 与 Task 测试表 NOT_RUN 冲突 |

**建议**：`PARTIAL`，不能 MET。

> 附：AC4/AC5/AC8 不在本次重评范围。AC4 payload 已验证 76/76（当前 77/77）；AC5 净删除 325；AC8 主线裁定未变。

---

## 5. 文档更正建议（可直接替换；不要覆盖历史 pin）

以下替换文本只针对**当前摘要/AC/事故叙述**；历史 Review、原 pin、原 Task 证据不改写。行号以本轮读取的 HEAD `3947d6344` 为准。

### 5.1 `doc/STATUS.md` 第 7 行（只替换 WORKSPACE-CONSOLIDATION-1 的括号段）

旧片段：

```text
（用户 2026-10-20 授权执行，已完成：418→93 分支、213→126 worktree、释放约 49.5 GB、57/57 保护项在位；待 Codex 复核）
```

建议替换为：

```text
（用户 2026-10-20 授权执行，返修中；r208=changes_requested：418→93 分支、213→132 注册 worktree；76 条 archive bundle，P03 返修保全后 77 条且 77/77 `git bundle verify` exit 0；两份删除收据的删除前递归逻辑字节合计 53,129,852,873 B = 49.48 GiB（≈53.13 GB），未测物理净释放；18 个具体保护资源受影响：11 个原位置缺失、P06 保留子树缺失、6 个仅部分回建，57/57 仅为名称子集；AC1/AC2/AC3/AC6/AC7/AC9 不能判 MET；详见 verification/WORKSPACE-CONSOLIDATION-1/codex-review-r208.md 与 records-correction-r208.md）
```

若 `STATUS` 行数预算吃紧（当前 warning 3152 bytes / 26 lines 已 80%），可只保留「132、77/77、49.48 GiB 逻辑、18 资源、AC 不能 MET、Review 指针」，明细留在 Task。

### 5.2 `doc/REBASELINE_PLAN.md` 第 54 行（整行替换）

旧行：

```text
|WORKSPACE-CONSOLIDATION-1|—|**in_review**（用户 2026-10-20 授权执行；9 AC 全 MET；418→93 分支、213→126 worktree、释放约 49.5 GB；57/57 保护项在位；待 Codex 复核）|
```

建议替换为：

```text
|WORKSPACE-CONSOLIDATION-1|—|**in_review / changes_requested（r208）**：418→93 分支、213→132 注册 worktree；76 条 archive bundle（返修期 P03 保全后 77 条，77/77 verify exit 0）；49.48 GiB 为两份删除收据的删除前递归逻辑字节合计，非物理净释放；18 个具体保护资源受影响（11 个原位置缺失、P06 子树缺失、6 个仅部分回建）；AC1/AC2/AC3/AC6/AC7/AC9 不能判 MET。详见 records-correction-r208|
```

### 5.3 `doc/tasks/WORKSPACE-CONSOLIDATION-1.md`

#### (a) AC 清单（第 68–76 行）

建议把 AC1/AC2/AC3/AC6/AC7/AC9 六行替换为（AC4/AC5/AC8 保留原文）：

```markdown
- [ ] **AC1 四表盘点** <<PARTIAL: 表已生成且数量可复算（418/342/76/213/57），但缺未跟踪逐文件大小/引用表、缺 267 条已删分支原始 tip；测试表仍为 NOT_RUN，不能判 MET>>
- [ ] **AC2 刷新权威清单** <<PARTIAL: Stage 7 已追加，但 126、"不忽略 ignored"、"8 个永久丢失"、workspace/worktrees 未动、1223>320、3.6 GiB 检测环境等表述与实测不符（见 records-correction-r208）>>
- [ ] **AC3 保护项全量枚举** <<PARTIAL / 保护目标 FAIL: 18 个具体 source（15 个删除根）= 6 worktree + 7 temp 路径 + 4 review-scratch + P06 old-runtime/worktree；11 个原位置缺失、6 个仅部分回建；57/57 只证明名称子集>>
- [ ] **AC6 worktree 清理** <<PARTIAL: 50 目录移除 + 37 仅登记移除 − 6 回建 = 132；ignored 清册、原始 status/stash 输出、独有/终态/引用门槛不完整>>
- [ ] **AC7 workspace 体积释放** <<PARTIAL / 安全目标 FAIL: 收据逻辑字节 53,129,852,873 B（49.48 GiB），无卷可用空间前后差值；workspace/worktrees 实际移除 7 处（4 处回建）>>
- [ ] **AC9 验收** <<PARTIAL: governance PASS exit 0（4 warnings）、fsck exit 0（613 dangling）、26 草稿；保护/恢复验收不成立，不得判 MET>>
```

#### (b) AC 证据表对应行（第 82–90 行）

- AC1 行补：`缺未跟踪逐文件大小/引用表；branch 表无原 tip SHA；267 条已合并删除项仅 19 条有 tip 证据`。
- AC3 行改为：`57 名子集仍注册且目录存在；18 个具体 source 受影响（11 缺失、P06 子树缺失、6 部分回建）；不能证明枚举完整`。
- AC6 行补：`另 37 个仅登记移除、6 个回建，当前 132`。
- AC7 行改为：`158 项删除前逻辑字节 21,636,208,040 B（20.15 GiB）；总逻辑 53,129,852,873 B = 49.48 GiB，非物理净释放`。
- AC9 行改为：`治理 PASS (4 warnings) exit 0；fsck exit 0 但 613 条 dangling；26 草稿路径；296 tracked doc/tasks`。

#### (c) 「本 Task 自身缺陷」段（第 96–121 行，整段替换建议）

```markdown
### ⚠ 本 Task 自身缺陷（r208 复核后确认，未修复部分仍 open）

**清理过程中删除了 18 个被 Task 资源清单声明为 `PRESERVE_REFERENCED` / `PRESERVE_UNKNOWN` 的具体 source（命中 15 个删除根）。**

口径更正：原写「13 条」= 6 worktree + 7 个 temp 路径；X6 capture 在父 Task 与 POSTRUN-REVIEW 两处重复登记，不是两份独立目录；另有 **4 个 P09 review-scratch** 与 **P06 `old-runtime/worktree` 保留子树** 未被原记录计入。
因此「13」必须改为 **18 个 source / 15 个删除根**。

**根因**：`tools/governance/clean_workspace.py` 的 pin 提取只认反引号包裹的表格单元格，而部分清单把路径裸写在单元格里；同时保护判断只按精确名称，未处理父目录保护（P06）与 shared-root 泛化声明。

**可用性分类（不得再写「8 个永久丢失」为既证事实）：**

| 类别 | 数量 / source | 说明 |
|---|---:|---|
| 原位置缺失、恢复能力未证实 | 7 个 temp 路径 + 4 个 review-scratch + P06 子树 | 原目录不存在；未做全盘/卷快照/备份搜索，不能证明永久不可恢复 |
| 可用副本 | X6 capture stdout/stderr | 现存 `stdout.md` 32,426 B SHA 0109…a3602、`stderr.md` 0 B SHA e3b0…b855，可经授权复制 |
| 精确字节可重建 | 两轮 X6 pure-selftest 的固定内容文件 | 可由受跟踪 selftest 源码在内存重建并匹配原 pin；重建不等于原工件实例 |
| 部分重建 | 6 个 worktree | HEAD 九位前缀匹配、detached、status 空；原分支检出、ignored 内容、目录元数据未恢复 |

**这 18 个 source 中 6 个仅部分回建、11 个原位置缺失、1 个（P06）保留子树缺失——所以「保护项全部在位」在本 Task 上不能成立。**
受影响 Task：`P02-NEW-TIME-BASELINE`、`P02-NEW-TIME-X6`、`P02-NEW-TIME-X6-POSTRUN-REVIEW`、`GOV-PIN-LINEAGE-1`、`FEAT-CREATE-1/2/4`、`P19-UI-FIX-2`、`P02-MAINLINE-INTEGRATION`、`P09-PREVIEW-LIFECYCLE-RECLAIM-1`、`P06`。

**教训**：区域/名称/父目录不是同一层语义；保护判断必须按路径身份与父子覆盖，且命令失败必须拒绝。
```

#### (d) 测试要求表（第 140–150 行）

表内 `NOT_RUN` 是**原计划命令未执行**的事实，不需要改成「已跑」；但必须加注：

```markdown
> **记录更正（r208）**：本表「实际结果」列的 `NOT_RUN` 表示原计划命令未按原样执行；它不能与 AC `<<MET>>` 并存。AC 判定只能依据实际收据与独立复算（见同目录 `records-correction-r208.md` 第 4 节），不得依据本表的计划行。
```

#### (e) 交付与运行记录（第 162–164 行）

```markdown
- Handoff：待返修完成后按固定 head 提交。
- Review：Codex 已交付 `verification/WORKSPACE-CONSOLIDATION-1/codex-review-r208.md`（`reviewed_head=3947d63447457fe3ef8d3587942e632724ab3d72`，`decision=changes_requested`）；本 Task 由 dsh 执行，按协作协议不得自审。
- 实际测试：见同目录 receipts、`codex-review-r208.md` 与本目录 `records-correction-r208.md`；原「测试要求」表多为 NOT_RUN，不能作为 AC MET 依据。
```

#### (f) 机器字段与 Canonical Evidence

- `delivery_head: 811fc2ea4c3c134b111347bcfe2f5adf25a9ff71` 早于 Review 与实际清理提交；返修交付时应更新为本轮固定 head。`canonical_evidence_status: complete` 与 r208 `changes_requested` 冲突，登记补证前不得判 complete。
- 建议在 Canonical Evidence 追加（commit/sha256 由 Owner 固定 head 后填写，**现在不得先填**）：

```markdown
| EV-REVIEW-R208 | Review | `verification/WORKSPACE-CONSOLIDATION-1/codex-review-r208.md` | 待固定 head | 待计算 | SOURCE_PIN |
| EV-RECORDS-R208 | AC 复算 | `verification/WORKSPACE-CONSOLIDATION-1/records-correction-r208.md` | 待固定 head | 待计算 | SOURCE_PIN |
| EV-MEASURE-R208 | 数值 | `verification/WORKSPACE-CONSOLIDATION-1/measurements-r208.json` | 待固定 head | 待计算 | SOURCE_PIN |
| EV-P03-PRESERVATION | R208-01 | `verification/WORKSPACE-CONSOLIDATION-1/p03-preservation-r208.md` / `.json` | 待固定 head | 待计算 | SOURCE_PIN |
```

#### (g) Resource Manifest（第 188–197 行）

- `derived` 行的 disposition `ARCHIVE` 应改为 `DELETE（rmtree，无归档目的地）`，并注明 158 项删除前逻辑字节 21,636,208,040 B（20.15 GiB）。
- `task-env` 行：区分 `M2-PROD-DETECT-ENV-1` 138,129,041 B（131.73 MiB）与 task-envs 其余 3.74 GB；不要把 3.61 GiB 整体称检测环境。
- 建议追加 18 个受影响资源的行，disposition 保持原枚举，另加 `availability` 字段（不要直接改成 `LOST`，需先冻结 schema）：`LOST_ORIGINAL` / `COPY_AVAILABLE` / `PARTIALLY_RECONSTRUCTED` / `PARTIAL_SUBTREE_LOSS`。

#### (h) Closeout Record（第 199–206 行）

```markdown
- Closeout date / Codex：待返修与复审完成后填写；当前 r208=changes_requested，不得关闭。
- canonical_evidence_status：pending（返修固定 head 后再判）。
- resource_closeout_status：pending / 事故项 open。
- 删除、迁移、归档数量/字节：50 worktree + 37 仅登记移除 − 6 回建 = 132；323+2=325 分支；158 派生项；逻辑 53,129,852,873 B；18 受保护 source 受影响；76/77 bundle。
- 未关闭项及保留原因：见 records-correction-r208 §4 与 codex-review-r208 Findings R208-01…08。
- 当前指针清理：待完成。
```

### 5.4 `doc/WORKTREE_SAFETY_INVENTORY.md` Stage 7

#### (a) 判定规则第 2 条（第 70 行）

旧：

```text
2. `git status --porcelain` 为空（**含未跟踪文件**；不忽略 ignored）
```

建议：

```text
2. `git status --porcelain` 为空（**含未跟踪文件**）；注意默认 `git status` **不展开 ignored**，ignored 内容必须另行逐文件清册，不能以 status 空代证
```

#### (b) 执行结果表（第 83–92 行）

- 「worktree 总数 213 → **126**」→ `213 → **132**`，并加一行：`移除闭环：50 目录 + 37 仅登记 − 6 回建 = 132`。
- 「worktree 移除 50 个实际移除，释放 29.3 GB」→ `50 个目录移除（删除前递归逻辑字节 31,493,644,833 B = 29.330742 GiB，非物理净释放）`。
- 「派生产物清理 158 项，释放 20.15 GB」→ `158 项，删除前逻辑字节 21,636,208,040 B = 20.150289 GiB；总逻辑 53,129,852,873 B = 49.481031 GiB`。
- 「76 个 bundle ... 覆盖 **1,223 个独有提交**」→ `76 个 manifest 分支归档 corpus：逐分支计数合计 1,223、去重 320（口径 A）；返修期新增 P03 后当前 77 refs：1,225 / 322（口径 B）`。
- 删除后状态：`已注册 worktree 126` → `132`；`archive/* tag 76` → `77（含 P03 返修保全）`；`git fsck 0 problems` → `exit 0，无 corruption；613 条 dangling 诊断`；`治理检查 PASS (3 warnings)` → `PASS (4 warnings)`。

#### (c) 拒绝清理的（第 95–99 行）

- 「**82 个 worktree 有未提交改动或 stash**：未碰」→ `inventory 有 82 个 worktree dirty>0（其中 14 个被列为 protected 而 skipped）；apply 实际 refused 105 = 68 dirty + 37 Permission denied；另有 57 protected + 主 checkout 1 个 skipped`。
- 「`workspace/worktrees`（111 GB）……一律不动」→ `workspace/worktrees 当前 71 个直接子目录、逻辑 120,499,443,541 B（112.223852 GiB）；本阶段实际移除其中 7 处（FEAT-CREATE-1/2/4、P02-NEW-TIME-X6-AC1-AC7、P15-C1-review、P19-AC3-1、P19-UI-FIX-2），4 处已回建；不得写「未动」`。
- 「`workspace/task-envs`（3.6 GB）：含 M2-PROD-DETECT-ENV-1 的隔离 venv」→ `task-envs 总逻辑 3,880,296,828 B（3.613808 GiB）；其中 M2-PROD-DETECT-ENV-1 仅 138,129,041 B（131.73 MiB），其余为 P02-NEW-TIME-X6-BUILD-CARGO 2,328,053,874 B 等；不能把整个 3.61 GiB 称为检测环境`。

#### (d) 越界删除段（第 134–150 行，整段替换建议）

```markdown
### Stage 7 执行中的越界删除（同日发现；r208 复核后更正口径）

**18 个被 Task 清单声明为 `PRESERVE_REFERENCED` / `PRESERVE_UNKNOWN` 的具体 source（命中 15 个删除根）被本阶段删除。**
原「13 条」= 6 worktree + 7 temp 路径；另有 4 个 P09 review-scratch 与 P06 `old-runtime/worktree` 保留子树未计入。X6 capture 在两份 Task 文档重复登记，不是两份独立目录。

| 类别 | 数量 | 当前状态 |
|---|---:|---|
| worktree | 6 | 已按 inventory 原 head 部分回建（detached；非原样复原） |
| temp 路径 | 7 | 原位置缺失；X6 capture 有同哈希副本、两轮 selftest 固定字节可重建；其余恢复能力未证实 |
| review-scratch | 4 | 原位置缺失（收据合计 14,699,110,702 B）；未做备份搜索 |
| P06 保留根子树 | 1 | `old-runtime/worktree` 缺失，父目录仍在 |

受影响 Task：`P02-NEW-TIME-BASELINE`、`P02-NEW-TIME-X6`、`P02-NEW-TIME-X6-POSTRUN-REVIEW`、
`GOV-PIN-LINEAGE-1`、`FEAT-CREATE-1/2/4`、`P19-UI-FIX-2`、`P02-MAINLINE-INTEGRATION`、
`P09-PREVIEW-LIFECYCLE-RECLAIM-1`、`P06`。

**本清单的 Stage 7「删除后状态」据此不成立为「保护项全在位」；57/57 只证明名称子集仍注册/存在。**
后续任何依赖 Stage 7 的判断都应先读本节；`P06` 根在 57 名单内且存在，但其受保护子树已缺失，说明名称级检查不足以证明资源完整。
```

#### (e) 独立复核要求（第 128–132 行）

改为：`132 个注册 worktree；57 个名称子集仍注册且目录存在（不等于保护完整）；19 条未合并分支的 tag/bundle/verify；76 manifest + P03 增量共 77 个 bundle；fsck exit 0 但含 dangling；26 个草稿路径不变；18 个受影响 source 按 availability 逐项记录`。

---

## 6. 未完成 / UNVERIFIED 清单与只读边界

### 6.1 本轮未做（NOT_RUN）或未证实（UNVERIFIED）

- NOT_RUN：bundle 恢复演练（未恢复任何 bundle，未建临时仓库；除引用另一协作者 p03 证据外不重复其演练）。
- NOT_RUN：全盘/卷快照/备份搜索（因此 temp/review-scratch 的「不可恢复」不能既证）。
- NOT_RUN：worktrees 扫描差异的逐路径归因（+273,872,958 B / +2,787 files）。
- NOT_RUN：fsck dangling 的 +1 差额归因。
- NOT_RUN：保护枚举的完整重建（共享根声明与全部 `verification/**/*.json` 的 PRESERVE 提取）。
- UNVERIFIED：ignored 内容逐文件清册、删除时原始 status/stash 输出、字节未变证明。
- UNVERIFIED：物理净释放（无卷可用空间前后差值）。

### 6.2 只读边界（实际执行）

- 未运行任何 Git 写命令：无 `add`/`commit`/`tag`/`branch`/`worktree` 写操作、无 `gc`/`prune`、无 `push`、无删除/移动。
- 未修改 `doc/**`、`tools/**`、既有证据；未改 `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/tasks/WORKSPACE-CONSOLIDATION-1.md`、`doc/WORKTREE_SAFETY_INVENTORY.md`。
- 只写两个文件：`verification/WORKSPACE-CONSOLIDATION-1/records-correction-r208.md`、`verification/WORKSPACE-CONSOLIDATION-1/measurements-r208.json`。
- 未修改其他协作者文件（`codex-review-r208.md`、`p03-preservation-r208.*`、`incident-ledger-r208.json` 仅读取）。

### 6.3 「不得把事故降级为 limitation」

本底稿不把 18 个受影响资源、P03 detached 提交、ignored 验证缺口写成 limitation；它们是需要 Owner/用户处置的 open 事件。AC1/AC2/AC3/AC6/AC7/AC9 不能因「补了说明」而判 MET。

---

## 附录 A：命令与原始输出摘要

| # | 命令（只读） | exit | 输出摘要 |
|---:|---|---:|---|
| A1 | `git rev-parse HEAD` | 0 | `3947d63447457fe3ef8d3587942e632724ab3d72` |
| A2 | `git rev-parse --abbrev-ref HEAD` | 0 | `antigravity/P09-AC3-DELETE-HARDEN-1` |
| A3 | `git status --porcelain` | 0 | 1239 条；tracked dirty 0、staged 0 |
| A4 | `git status --porcelain -uall` | 0 | 1595 条 |
| A5 | `git worktree list --porcelain`（计 `^worktree `） | 0 | **132** |
| A6 | `git show-ref --heads` | 0 | **93** |
| A7 | 93 次 `git merge-base --is-ancestor <branch> <mainline>` | 0/1 | 74 exit 0（已并入）/ 19 exit 1（未并入） |
| A8 | `git tag -l 'archive/*'` | 0 | **77** |
| A9 | Python：遍历 manifest 76 tags，`git rev-list <mainline>..<tag>` 求和/并集 | 0 | **1223 / 320（口径 A）** |
| A10 | Python：遍历当前全部 77 tags，同上 | 0 | **1225 / 322（口径 B）**；extra tag=`archive/P03-review-prep-112495c7`；extra commits=2 |
| A11 | 77 次 `git bundle verify <bundle>` | 0 | **77/77 exit 0**；manifest 76 项文件大小逐项匹配 |
| A12 | 19 条未合并分支：tag/tip/bundle/verify 核对 | 0 | 19/19 tag tip==branch tip，19/19 bundle 存在，19/19 verify exit 0 |
| A13 | Python：`sum(worktree-removal.removed[].bytes)` | 0 | **31,493,644,833**（与收据 totals 相等） |
| A14 | Python：`sum(workspace-cleanup.removed[].bytes)` | 0 | **21,636,208,040**（与收据 totals 相等） |
| A15 | Python：53,129,852,873 / 1024³ | 0 | **49.48103136662394 GiB**（= 53.129853 GB） |
| A16 | Python：过滤 `workspace/worktrees/` 的 removed[] | 0 | **7** 条，合计 13,225,660,979 B；`os.path.isdir` 4 真 3 假 |
| A17 | Python：task-envs 递归 lstat 扫描（不跟 reparse） | 0 | **3,880,296,828 B / 104,117 files / 6 子目录 / 0 reparse / 0 denied** |
| A18 | Python：`M2-PROD-DETECT-ENV-1` 子扫描 | 0 | **138,129,041 B / 6,677 files = 131.73 MiB** |
| A19 | Python：worktrees 递归 lstat 扫描 | 0 | **120,499,443,541 B / 954,980 files / 71 子目录 / 1,520 reparse skipped / 0 denied** |
| A20 | 57 保护名 × 注册表 basename + `isdir` | 0 | **57/57** 匹配且目录存在；57 个 skipped protected 路径名集合与 inventory 完全相等 |
| A21 | 18 条 source `os.path.isdir` + P06 子树 + 6 回建 HEAD | 0 | 7 存在 / 11 缺失；`old-runtime/worktree`=False；6 回建 HEAD 九位前缀匹配、detached、status 空 |
| A22 | `Get-FileHash` X6 `stdout.md`/`stderr.md` | 0 | `0109aed4…a3602` / `e3b0c442…b855`，与 r208 Q3 一致 |
| A23 | `git fsck --no-progress` | 0 | 382 blob / 75 tree / **156** commit = 613 dangling；0 其他诊断 |
| A24 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/WORKSPACE-CONSOLIDATION-1.md` | 0 | `PASS (4 warnings)`（原文见 §3.9） |
| A25 | `git ls-files doc/tasks` / `--others --exclude-standard doc/tasks` | 0 | **296 / 26** |
| A26 | `git ls-files` | 0 | 11,295 |
| A27 | 6 个回建 worktree：`git -C <path> rev-parse HEAD`、`symbolic-ref -q HEAD`、`status --porcelain -uall` | 0 / 1 / 0 | HEAD 前缀匹配；detached（symbolic-ref exit 1）；status 空 |

> 说明：Git 查询统一加 `--no-optional-locks`；Python 统一 `-B`。A7 的 exit 1 是预期（分支未并入），不是命令失败。

---

## 附录 B：76 个 manifest 分支归档的逐分支计数（口径 A）

> 数据源：`archive-manifest.json` 的 `archived[]`；算法：`git rev-list antigravity/P09-AC3-DELETE-HARDEN-1..<tag>` 逐 tag 计数。76 项合计 **1,223**，逐项与 manifest `unique_commits` 完全相等；并集 **320**。

| # | branch | tag | 独有提交 |
|---:|---|---|---:|
| 1 | `agent/antigravity/P02PRE-R1G` | `archive/agent_antigravity_P02PRE-R1G` | 6 |
| 2 | `agent/antigravity/P02PRE-R1H` | `archive/agent_antigravity_P02PRE-R1H` | 7 |
| 3 | `agent/antigravity/P02PRE-R1H-H2-COLLECTOR-R3` | `archive/agent_antigravity_P02PRE-R1H-H2-COLLECTOR-R3` | 15 |
| 4 | `agent/antigravity/P02PRE-R1H-R6-A4` | `archive/agent_antigravity_P02PRE-R1H-R6-A4` | 2 |
| 5 | `agent/antigravity/P22-roundtrip-serialization` | `archive/agent_antigravity_P22-roundtrip-serialization` | 10 |
| 6 | `agent/antigravity/T3.2.1-repair-10` | `archive/agent_antigravity_T3.2.1-repair-10` | 49 |
| 7 | `agent/antigravity/T3.2.1-repair-11` | `archive/agent_antigravity_T3.2.1-repair-11` | 53 |
| 8 | `agent/antigravity/T3.2.1-repair-12` | `archive/agent_antigravity_T3.2.1-repair-12` | 54 |
| 9 | `agent/antigravity/T3.2.1-repair-14` | `archive/agent_antigravity_T3.2.1-repair-14` | 4 |
| 10 | `agent/antigravity/T3.2.1-repair-3` | `archive/agent_antigravity_T3.2.1-repair-3` | 15 |
| 11 | `agent/antigravity/T3.2.1-repair-4` | `archive/agent_antigravity_T3.2.1-repair-4` | 19 |
| 12 | `agent/antigravity/T3.2.1-repair-5` | `archive/agent_antigravity_T3.2.1-repair-5` | 25 |
| 13 | `agent/antigravity/T3.2.1-repair-6` | `archive/agent_antigravity_T3.2.1-repair-6` | 30 |
| 14 | `agent/antigravity/T3.2.1-repair-7` | `archive/agent_antigravity_T3.2.1-repair-7` | 41 |
| 15 | `agent/antigravity/T3.2.1-repair-9` | `archive/agent_antigravity_T3.2.1-repair-9` | 46 |
| 16 | `agent/antigravity/T3.2.1-windows-packaging` | `archive/agent_antigravity_T3.2.1-windows-packaging` | 8 |
| 17 | `agent/codex/M2-C1-typed-ipc-contract` | `archive/agent_codex_M2-C1-typed-ipc-contract` | 16 |
| 18 | `agent/codex/P02PRE-R1H` | `archive/agent_codex_P02PRE-R1H` | 13 |
| 19 | `agent/codex/P02PRE-R1H-FORENSIC-RECOVERY-INTEGRATION` | `archive/agent_codex_P02PRE-R1H-FORENSIC-RECOVERY-INTEGRATION` | 3 |
| 20 | `agent/codex/P02PRE-R1H-H1-CURRENT-INPUT-REVIEW` | `archive/agent_codex_P02PRE-R1H-H1-CURRENT-INPUT-REVIEW` | 4 |
| 21 | `agent/codex/P02PRE-R1H-H2-RUN-INTEGRATION` | `archive/agent_codex_P02PRE-R1H-H2-RUN-INTEGRATION` | 3 |
| 22 | `agent/codex/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE` | `archive/agent_codex_P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE` | 18 |
| 23 | `agent/codex/T1.2.1-integration` | `archive/agent_codex_T1.2.1-integration` | 2 |
| 24 | `agent/codex/TASK-013-production-pipeline-seam` | `archive/agent_codex_TASK-013-production-pipeline-seam` | 2 |
| 25 | `agent/deepseek/M2-PACKAGED-AC1-DLL-DIAG` | `archive/agent_deepseek_M2-PACKAGED-AC1-DLL-DIAG` | 1 |
| 26 | `agent/deepseek/T1.1.1-detector-evaluation` | `archive/agent_deepseek_T1.1.1-detector-evaluation` | 1 |
| 27 | `agent/deepseek/T3.2.1-review-740503e` | `archive/agent_deepseek_T3.2.1-review-740503e` | 1 |
| 28 | `agent/deepseek/T3.2.1-review-7d687f5` | `archive/agent_deepseek_T3.2.1-review-7d687f5` | 1 |
| 29 | `agent/deepseek/T3.2.1-review-92c9307c` | `archive/agent_deepseek_T3.2.1-review-92c9307c` | 1 |
| 30 | `agent/deepseek/T3.2.1-review-9622395` | `archive/agent_deepseek_T3.2.1-review-9622395` | 53 |
| 31 | `agent/deepseek/T3.2.1-review-a2f6695` | `archive/agent_deepseek_T3.2.1-review-a2f6695` | 54 |
| 32 | `agent/deepseek/T3.2.1-review-be5200e` | `archive/agent_deepseek_T3.2.1-review-be5200e` | 49 |
| 33 | `agent/deepseek/T3.2.1-review-cdc0b6f` | `archive/agent_deepseek_T3.2.1-review-cdc0b6f` | 6 |
| 34 | `agent/deepseek/T3.2.1-review-d2bf6a8` | `archive/agent_deepseek_T3.2.1-review-d2bf6a8` | 46 |
| 35 | `agent/deepseek/T3.2.1-review-d79d7dd` | `archive/agent_deepseek_T3.2.1-review-d79d7dd` | 14 |
| 36 | `agent/deepseek/T3.2.1-review-f39ddc0` | `archive/agent_deepseek_T3.2.1-review-f39ddc0` | 1 |
| 37 | `agent/deepseek/T3.2.1-review-f6dc383` | `archive/agent_deepseek_T3.2.1-review-f6dc383` | 31 |
| 38 | `agent/deepseek/T3.2.1-review-repair-14` | `archive/agent_deepseek_T3.2.1-review-repair-14` | 3 |
| 39 | `agent/deepseek/T3.2.1-review-repair-14-r2` | `archive/agent_deepseek_T3.2.1-review-repair-14-r2` | 5 |
| 40 | `agent/deepseek/T3.2.1-review-repair-7` | `archive/agent_deepseek_T3.2.1-review-repair-7` | 6 |
| 41 | `agent/deepseek/TASK-004-review` | `archive/agent_deepseek_TASK-004-review` | 1 |
| 42 | `agent/deepseek/TASK-015-posthoc` | `archive/agent_deepseek_TASK-015-posthoc` | 1 |
| 43 | `agent/deepseek/TASK-017-posthoc` | `archive/agent_deepseek_TASK-017-posthoc` | 1 |
| 44 | `agent/deepseek/TASK-024-posthoc` | `archive/agent_deepseek_TASK-024-posthoc` | 1 |
| 45 | `agent/qoder/T1.1.2-region-canvas` | `archive/agent_qoder_T1.1.2-region-canvas` | 2 |
| 46 | `agent/qoder/T2.2.1-reader-workbench-qml` | `archive/agent_qoder_T2.2.1-reader-workbench-qml` | 5 |
| 47 | `agent/qoder/T3.2.1-repair-13` | `archive/agent_qoder_T3.2.1-repair-13` | 54 |
| 48 | `agent/qoder/TASK-047-ui-ux-gui-design` | `archive/agent_qoder_TASK-047-ui-ux-gui-design` | 9 |
| 49 | `agent/qoder/TASK-061-review` | `archive/agent_qoder_TASK-061-review` | 4 |
| 50 | `agent/zcode/M2-I1-core-assembly-seam` | `archive/agent_zcode_M2-I1-core-assembly-seam` | 1 |
| 51 | `agent/zcode/P02-NEW-TIME-BASELINE` | `archive/agent_zcode_P02-NEW-TIME-BASELINE` | 60 |
| 52 | `agent/zcode/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION` | `archive/agent_zcode_P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION` | 31 |
| 53 | `agent/zcode/P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION` | `archive/agent_zcode_P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION` | 78 |
| 54 | `agent/zcode/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION` | `archive/agent_zcode_P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION` | 43 |
| 55 | `agent/zcode/P02PRE-R1H` | `archive/agent_zcode_P02PRE-R1H` | 7 |
| 56 | `agent/zcode/P02PRE-R1H-H2-COLLECTOR` | `archive/agent_zcode_P02PRE-R1H-H2-COLLECTOR` | 4 |
| 57 | `agent/zcode/T1.2.1-settings-ui-viewmodel` | `archive/agent_zcode_T1.2.1-settings-ui-viewmodel` | 1 |
| 58 | `agent/zcode/T2.2.1-reader-workbench-polish` | `archive/agent_zcode_T2.2.1-reader-workbench-polish` | 1 |
| 59 | `agent/zcode/T3.2.1-repair-13` | `archive/agent_zcode_T3.2.1-repair-13` | 64 |
| 60 | `agent/zcode/TASK-045-posthoc` | `archive/agent_zcode_TASK-045-posthoc` | 1 |
| 61 | `codex/FEAT-CREATE-1` | `archive/codex_FEAT-CREATE-1` | 3 |
| 62 | `codex/P02-fallback-scope` | `archive/codex_P02-fallback-scope` | 1 |
| 63 | `codex/P02-hook-cache-isolation-plan` | `archive/codex_P02-hook-cache-isolation-plan` | 7 |
| 64 | `codex/P14` | `archive/codex_P14` | 2 |
| 65 | `codex/P15-C1-FU2` | `archive/codex_P15-C1-FU2` | 2 |
| 66 | `codex/T3.2.1-release-gate-closeout` | `archive/codex_T3.2.1-release-gate-closeout` | 50 |
| 67 | `codex/integration-p02pre-r1h-p2-1-external-harness-trace` | `archive/codex_integration-p02pre-r1h-p2-1-external-harness-trace` | 18 |
| 68 | `codex/project-roadmap-rebaseline` | `archive/codex_project-roadmap-rebaseline` | 1 |
| 69 | `codex/rebaseline-audit-20260921` | `archive/codex_rebaseline-audit-20260921` | 1 |
| 70 | `dsh/GOV-PIN-LINEAGE-1` | `archive/dsh_GOV-PIN-LINEAGE-1` | 2 |
| 71 | `master` | `archive/master` | 3 |
| 72 | `review/deepseek/M2-C1-typed-ipc-7d908a5` | `archive/review_deepseek_M2-C1-typed-ipc-7d908a5` | 4 |
| 73 | `review/deepseek/M2-C1-typed-ipc-r2-7e65f4f` | `archive/review_deepseek_M2-C1-typed-ipc-r2-7e65f4f` | 12 |
| 74 | `review/deepseek/M2-C1-typed-ipc-r3-4d66523` | `archive/review_deepseek_M2-C1-typed-ipc-r3-4d66523` | 14 |
| 75 | `review/deepseek/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-r2` | `archive/review_deepseek_M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-r2` | 1 |
| 76 | `review/qoder/M2-C1-typed-ipc-r3-4d66523` | `archive/review_qoder_M2-C1-typed-ipc-r3-4d66523` | 15 |
| | **合计** | | **1,223** |

---

## 附录 C：19 条当前未并入主线的分支（完整 tip / tag / bundle / verify）

mainline = `antigravity/P09-AC3-DELETE-HARDEN-1`（tip `3947d6344`）。19/19 tag tip 与 branch tip 相同，19/19 bundle 存在，19/19 `git bundle verify` exit 0。逐分支计数合计 **351**，去重 **224**。

| # | branch | 完整 tip | archive tag | bundle verify exit | 独有提交 |
|---:|---|---|---|---:|---:|
| 1 | `agent/antigravity/P02PRE-R1H-H2-COLLECTOR-R3` | `c763efa27db0f10949a52416f1374e88173a31e2` | `archive/agent_antigravity_P02PRE-R1H-H2-COLLECTOR-R3` | 0 | 15 |
| 2 | `agent/antigravity/P22-roundtrip-serialization` | `4a707db80499f11e93cee163a9a10bf6392b1a92` | `archive/agent_antigravity_P22-roundtrip-serialization` | 0 | 10 |
| 3 | `agent/codex/P02PRE-R1H-FORENSIC-RECOVERY-INTEGRATION` | `4569093db896b019cfab401e35b66ed4bcea673d` | `archive/agent_codex_P02PRE-R1H-FORENSIC-RECOVERY-INTEGRATION` | 0 | 3 |
| 4 | `agent/codex/P02PRE-R1H-H1-CURRENT-INPUT-REVIEW` | `a6f33f7be1fc13cca64539ecaaa4bd9528a0184e` | `archive/agent_codex_P02PRE-R1H-H1-CURRENT-INPUT-REVIEW` | 0 | 4 |
| 5 | `agent/codex/P02PRE-R1H-H2-RUN-INTEGRATION` | `06990b7993d042ae5e74ab479e291e494b622588` | `archive/agent_codex_P02PRE-R1H-H2-RUN-INTEGRATION` | 0 | 3 |
| 6 | `agent/codex/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE` | `23bec747df77e67e93ec1fa9fd859d077219e941` | `archive/agent_codex_P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE` | 0 | 18 |
| 7 | `agent/zcode/P02-NEW-TIME-BASELINE` | `7ab5b7d0574041f2ca9fa1424ca5b440ff298aaf` | `archive/agent_zcode_P02-NEW-TIME-BASELINE` | 0 | 60 |
| 8 | `agent/zcode/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION` | `10c35daed241aa3717b248da14c1b9b959ff1fba` | `archive/agent_zcode_P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION` | 0 | 31 |
| 9 | `agent/zcode/P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION` | `0af8980884e9d027042ef145cd966577d86b5bc5` | `archive/agent_zcode_P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION` | 0 | 78 |
| 10 | `agent/zcode/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION` | `14da1e814931e1e32ebc1f76a12bc3685b63646e` | `archive/agent_zcode_P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION` | 0 | 43 |
| 11 | `agent/zcode/P02PRE-R1H-H2-COLLECTOR` | `4a90d820a5d58a54cbc190665fbd87d563bc19af` | `archive/agent_zcode_P02PRE-R1H-H2-COLLECTOR` | 0 | 4 |
| 12 | `agent/zcode/T2.2.1-reader-workbench-polish` | `df637df1f9d6e8468bc73d6ff585bbf55e8e9a64` | `archive/agent_zcode_T2.2.1-reader-workbench-polish` | 0 | 1 |
| 13 | `agent/zcode/T3.2.1-repair-13` | `13ae23f65e963cf1d5aea19634572627e5e709db` | `archive/agent_zcode_T3.2.1-repair-13` | 0 | 64 |
| 14 | `codex/P02-hook-cache-isolation-plan` | `ceca2446da88df23a719f40868cc89e1481ccb2c` | `archive/codex_P02-hook-cache-isolation-plan` | 0 | 7 |
| 15 | `codex/P14` | `41c3206942730536bc9b41e871f23ad9b3de3f1d` | `archive/codex_P14` | 0 | 2 |
| 16 | `codex/P15-C1-FU2` | `0aa01eddcd751adf9c4d2e3894f4cce9ec657909` | `archive/codex_P15-C1-FU2` | 0 | 2 |
| 17 | `codex/project-roadmap-rebaseline` | `000cbfe9909c3eb566fd4d077c77199ce4d7c86e` | `archive/codex_project-roadmap-rebaseline` | 0 | 1 |
| 18 | `review/deepseek/M2-C1-typed-ipc-7d908a5` | `e6fc3a59b913f2aef1ab8c7a77ff47df0cd114a1` | `archive/review_deepseek_M2-C1-typed-ipc-7d908a5` | 0 | 4 |
| 19 | `review/deepseek/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-r2` | `daab1996b99c7036108bc505cc3db29b744fdf9d` | `archive/review_deepseek_M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-r2` | 0 | 1 |
| | **合计 / 去重** | | | | **351 / 224** |

Bundle 路径规则：`G:/CODEX/New Manga.workspace/archive/bundles/<branch 的 / 换成 _>.bundle`（19 条均实际存在，文件大小与 manifest 记录一致）。

---

## 附录 D：18 个受影响资源的当前存在性与可用性

| # | source | 原 disposition | 现在 | 观测 |
|---:|---|---|---|---|
| 1 | `G:/CODEX/New Manga.workspace/GOV-PIN-LINEAGE-1/worktree` | PRESERVE_REFERENCED | 存在 | 提交快照回建，detached；ignored 内容未恢复 |
| 2 | `G:/CODEX/New Manga.workspace/P06-GC-DISTRIBUTION-MIGRATION` | PRESERVE_REFERENCED | 部分 | 父目录在；`old-runtime/worktree` 缺失 |
| 3 | `.../review-scratch/P09-PREVIEW-LIFECYCLE-RECLAIM-1-R11-392977a8` | PRESERVE_UNKNOWN | 缺失 | 收据 1,594,956 B |
| 4 | `.../review-scratch/P09-PREVIEW-LIFECYCLE-RECLAIM-1-R11-392977a8-export` | PRESERVE_UNKNOWN | 缺失 | 收据 351,312,383 B |
| 5 | `.../review-scratch/P09-PREVIEW-LIFECYCLE-RECLAIM-1-R17` | PRESERVE_UNKNOWN | 缺失 | 收据 1,411,503 B |
| 6 | `.../review-scratch/P09-PREVIEW-LIFECYCLE-RECLAIM-1-R18` | PRESERVE_UNKNOWN | 缺失 | 收据 14,344,791,860 B |
| 7 | `.../temp/P02-NEW-TIME-BASELINE` | PRESERVE_REFERENCED | 缺失 | 收据 23,975 B |
| 8 | `.../temp/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION` | PRESERVE_REFERENCED | 缺失 | 收据 80 B |
| 9 | `.../temp/P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION` | PRESERVE_REFERENCED | 缺失 | 收据 315 B |
| 10 | `.../temp/P02-NEW-TIME-X6` | PRESERVE_REFERENCED | 缺失 | 收据根 32,624 B（含下述子路径） |
| 11 | `.../temp/P02-NEW-TIME-X6/codex-ac2-20261014-123308-pure-selftest` | PRESERVE_REFERENCED | 缺失 | 固定字节可重建（r208 Q3） |
| 12 | `.../temp/P02-NEW-TIME-X6/codex-ac2-r2-20261014-124643-pure-selftest` | PRESERVE_REFERENCED | 缺失 | 固定字节可重建（r208 Q3） |
| 13 | `.../temp/P02-NEW-TIME-X6/x6-20261014T1305CST-p02-newtime-r1-capture` | PRESERVE_REFERENCED | 缺失 | 副本可用：stdout 32,426 B / stderr 0 B，hash 匹配 |
| 14 | `.../worktrees/FEAT-CREATE-1` | PRESERVE_UNKNOWN | 存在 | 回建，detached |
| 15 | `.../worktrees/FEAT-CREATE-2` | PRESERVE_UNKNOWN | 存在 | 回建，detached |
| 16 | `.../worktrees/FEAT-CREATE-4` | PRESERVE_UNKNOWN | 存在 | 回建，detached |
| 17 | `.../worktrees/P19-UI-FIX-2` | PRESERVE_UNKNOWN | 存在 | 回建，detached |
| 18 | `G:/CODEX/New Manga.worktrees/P02-real-webview-harness-antigravity` | PRESERVE_UNKNOWN | 存在 | 回建，detached |

> availability 建议字段值：1/14–18 = `PARTIALLY_RECONSTRUCTED`（2 另有 `PARTIAL_SUBTREE_LOSS`）；3–12 = `LOST_ORIGINAL`（恢复能力未证实）；13 = `COPY_AVAILABLE`（外加 selftest 可重建）。不要直接把 disposition 改成 schema 未冻结的 `LOST`。

---

## 附录 E：最小复算脚本（粘贴即用）

```powershell
# E1 基础
git -C 'G:/CODEX/New Manga' rev-parse HEAD
(git -C 'G:/CODEX/New Manga' worktree list --porcelain | Select-String '^worktree ').Count
(git -C 'G:/CODEX/New Manga' show-ref --heads).Count
(git -C 'G:/CODEX/New Manga' tag -l 'archive/*').Count

# E2 两个口径（务必分开）
@'
import json, subprocess
repo=r"G:/CODEX/New Manga"; ml="antigravity/P09-AC3-DELETE-HARDEN-1"
def git(*a): return subprocess.run(["git","--no-optional-locks",*a],cwd=repo,capture_output=True,text=True,encoding="utf-8",errors="replace")
man=json.load(open(r"verification/WORKSPACE-CONSOLIDATION-1/archive-manifest.json",encoding="utf-8"))
s=0; u=set()
for e in man["archived"]:
    ids=git("rev-list",f"{ml}..{e['tag']}").stdout.split(); s+=len(ids); u.update(ids)
print("A manifest76",len(man["archived"]),s,len(u))
s=0; u=set(); tags=git("tag","-l","archive/*").stdout.split()
for t in tags:
    ids=git("rev-list",f"{ml}..{t}").stdout.split(); s+=len(ids); u.update(ids)
print("B current77",len(tags),s,len(u))
'@ | C:/Python314/python.exe -B -

# E3 字节合计
@'
import json
b=r"verification/WORKSPACE-CONSOLIDATION-1/"
wt=json.load(open(b+"worktree-removal.json",encoding="utf-8"))
ws=json.load(open(b+"workspace-cleanup.json",encoding="utf-8"))
a=sum(x["bytes"] for x in wt["removed"]); c=sum(x["bytes"] for x in ws["removed"])
print(a,c,a+c,(a+c)/1024**3)
'@ | C:/Python314/python.exe -B -

# E4 task-envs / worktrees 逻辑字节（不跟随 reparse）
# 见 measurements-r208.json 的 task_envs.commands / workspace_worktrees_scan.commands
```

---

## 签署信息

- 生成者：`records-correction`（DSH teammate）
- 只读实测 + 只写本文件与 `measurements-r208.json`
- 建议下一位读者：Lead / Codex（独立复核）；文档替换由 Owner 在获准窗口执行
- 本文件不构成批准，也不改变 Task 状态
