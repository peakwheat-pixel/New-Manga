# 逐 Task 治理检查审计（r187）

**产出**：2026-10-20 · **数据**：`per-task-check-audit.json`
**动因**：`check.ps1` 只校验 `doc/STATUS.md` 指向的那**一个** Task。
**因此历次 `Governance check: PASS` 的语义是「这一个 Task 合法」，而不是「所有 Task 合法」。**

**本文档用 `-TaskPath` 逐一对全部 320 个 Task 跑检查，量出这个差距。**

## 一、总量

| 项 | 数 |
|---|---:|
| **Task 文件总数（磁盘）** | **320** |
| **逐个检查失败** | **91**（28.4%）|
| 终态 Task 失败 | **64 / 282** |
| 非终态 Task 失败 | **27 / 38** |

**失败原因分布（全部）**：

| 原因 | 次数 |
|---|---:|
| **Evidence SHA-256 不匹配** | **163** |
| **当前 DAG 未登记非终态 Task** | **26** |
| Canonical evidence 路径缺失 | 23 |
| Resource manifest 不存在 | 20 |
| DONE evidence_dir 含未登记文件 | 11 |
| **DONE 不能保留未完成 AC** | **10** |
| Resource SHA-256 不匹配 | 7 |
| 失效的本地引用 | 7 |
| Resource disposition 无效 | 5 |
| READY Task 未出现在 Plan 的 READY 节点 | 4 |
| 其他（各 1–2） | 6 |

## 二、根因一：AC 行对检查器完全不可见（已修复）

**60 个 Task 文件是 CRLF，而 `check.ps1` 的 AC 正则**：

```powershell
'(?m)^[ \t]*-[ \t]*\[([ xX])\][ \t]*\*\*AC[^\r\n]*$'
```

**`.NET` 的多行 `$` 只匹配 `\n` 之前，不匹配 `\r\n` 之前。**
**`[^\r\n]*` 吃不掉 `\r`，所以 CRLF 文件里**每一行 AC 都匹配不到**。**

**实测：60 个文件 `parsed=0` 而 `would-be=5..10`。**

**这正是那 4 条 `lifecycle v3 Task 进入 REVIEW/DONE 时未找到任何 AC 行` 的来源——
**AC 行在文件里，读的人看不见。**

### 而它不只是「有些文件恰好是 CRLF」

**`.gitattributes` 已经为 `tools/governance/check.ps1` 和几个证据文件钉了 `eol=lf`，
理由正是「`core.autocrlf=true` 会重写成 CRLF 并破坏记录的 sha256」。**
**但 `doc/tasks/**` 没有规则。**

**实测：把仓库 clone 到临时目录，全新 checkout 出来的**每个** Task 文件都是 CRLF。**

**所以这不是历史遗留的偶然状态，是**任何新 clone 上必然重现**的状态——**
**在干净机器上，检查器读不到**全部 320 个**文件的 AC。**

### 修复

**`doc/tasks/*.md text eol=lf`**（沿用该文件已有的 7 条同类规则），
**并把 219 个 CRLF 任务文件转成 LF。**

**结果：**320 个文件的 AC 行全部可解析（0 个仍在隐藏）。**

## 三、根因二：工作区 SHA-256 在 `core.autocrlf=true` 下必然腐坏（未修，已改为 commit pin）

**163 次 `Evidence SHA-256 不匹配`，涉及 **41 个终态 Task，且全部是终态**。**

**`check.ps1:355` 用 `Get-FileHash` 检查**工作区字节**。**

**实测同一 HEAD 的同一文件**：

| 来源 | SHA-256 |
|---|---|
| 工作区字节 | `474f3e2ce96baa03a36fe9bcedce146f55610a42a6cc08c1e383a0293a2403ec` |
| `git show HEAD:` 字节 | `53af6735067367de0ab2b5b0f3d45fabdebcff0f01e32307c56df42e57b5a88c` |

**两者不同，且工作区那份会在下次 checkout 时被重写。**

**所以「证据哈希」记录的是**写它那一刻的工作区状态**，不是文件的内容。**

**已修的部分**：`PDF-STREAM-FIX-1`、`SEC-FMT-IMPL-1`（本会话收口）改用 **commit-only pin**。
**未修的部分**：其余 39 个终态 Task 的 163 条记录——**r38 禁止批量回改历史 Task**。

**已验证**：`PDF-STREAM-FIX-1` 与 `SEC-FMT-IMPL-1` 现在 **PASS**，
且它们的 AC 行是**第一次**被检查器真正读到。

## 四、非终态 Task：27 个失败，但绝大多数是**已知**的

| 原因 | 数 | 说明 |
|---|---:|---|
| **当前 DAG 未登记非终态 Task** | **26** | 即 r38 记录的「Plan 外 Task」——**已知债务，不是新问题** |
| **READY Task 未出现在 Plan 的 READY 节点** | **4** | `T3.2.1-REPAIR-3/7/9/10` **状态是 `ready` 却未在 Plan 中释放** |
| Resource manifest / disposition | 11 | 部分可能是本文档 §五 的表头问题 |
| 失效的本地引用 | 3 | `P22`（`in_review`）|
| 其他 | 2 | `P02-NEW-TIME-X6-BUILD-CARGO`（`approved`）含 1 条未完成 AC |

### 4 个 `ready` 却未释放的 Task 值得单独指出

**`T3.2.1-REPAIR-3/7/9/10` 的 `status: ready`，但 `REBASELINE_PLAN` 的 READY 节点里没有它们。**

**按 `AGENTS.md`「只有 Rebaseline Plan 明确激活且范围已冻结的 Task 才允许实施」——
**这 4 个 Task 的状态字段在说「可以开工」，而授权在说「不可以」。**

**我没有改它们**：状态与授权谁对，需要 Codex 裁定，不是我能单方决定的。

## 五、新发现：台账数的是磁盘文件，不是 git 里的文件

**`task_ledger.py` 扫描的是 `doc/tasks/` 目录，不是 `git ls-files`。**

**实测**：

| 来源 | 数 |
|---|---:|
| 磁盘上的 Task 文件 | **320** |
| git 中已跟踪的 Task 文件 | **295** |
| **未跟踪的 Task 草稿** | **26** |

**所以「320 个 Task / 38 个非终态」这两个数字里，包含 26 个**从未提交的本地草稿**。**

**这也解释了为什么 26 条 `当前 DAG 未登记非终态 Task` 与那 26 个未跟踪文件数量吻合——
**几乎可以确定是同一批。**

**我没有把这 26 个文件提交，也没有删除它们**——按 `AGENTS.md`「未提交内容归原作者所有」。

## 六、我在本轮犯的错

**修 LF 时用了 `git add -A doc/tasks`，把上述 26 个未跟踪文件扫进了提交。**

**这正是我自己早就记录过的一条（「`git add <directory>` 会扫进别人的未跟踪文件，要用 `-u` 或显式路径」）。**

**发现后立即 `git rm --cached` 退回未跟踪状态，工作区文件未动。**

**犯这个错的原因很具体**：那条命令的**主题是行尾**，而我把注意力放在「哪些文件需要转 LF」上，
**「这次 add 会包含哪些文件」不在我当时的问题里。**

## 七、结论

| 项 | 数 |
|---|---:|
| **逐个检查失败的 Task** | **91 / 320** |
| 其中**终态**（历史债，r38 禁止批量回改） | **64** |
| 其中**非终态**（活跃问题） | **27** |
| 非终态里属「Plan 外 Task」已知债务 | **26** |
| **真正的**新发现** | **4 个 `ready` 未释放的 Task** |

**所以 91 这个数字里，绝大多数**不是新问题**：
**163 条哈希腐坏 + 26 条 Plan 外 Task 都属于已登记债务。**

**真正需要决策的只有一处**：4 个 `T3.2.1-REPAIR-*` 的状态与授权矛盾。

## 八、建议（需 Codex 裁定）

1. **`check.ps1` 的 AC 正则应对 `\r` 宽容**（例如 `\r?$`），
   让它在任何行尾下都能工作——`.gitattributes` 规则只是把症状压住
2. **Evidence SHA-256 应改为对 **git blob** 计算**，或在文档里明确其口径
3. **裁定 4 个 `T3.2.1-REPAIR-*`**：改状态为 `blocked`，或在 Plan 中释放
4. **`task_ledger.py` 应区分「磁盘文件」与「已跟踪文件」**，
   否则台账会把未提交草稿计为项目事实
5. **收口流程应显式 `-TaskPath` 复检该 Task**（本轮已验证：这能立刻发现 STATUS 指针跳过的文件）

## 九、明确未做

- **未修改 `tools/governance/check.ps1`**（共享契约）
- **未修改 `doc/templates/TASK.md`**
- **未批量回改 64 个终态 Task**（r38）
- **未改 4 个 `ready` Task 的状态**（需裁定）
- **未提交或删除 26 个未跟踪草稿**（归原作者）
- **未修 `task_ledger.py` 的跟踪口径**
