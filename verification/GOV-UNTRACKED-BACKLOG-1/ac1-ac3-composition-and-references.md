# AC1 / AC3 — 未入库积压的构成与引用关系

**Task**: GOV-UNTRACKED-BACKLOG-1 · **性质**: 只读盘点 · **基线 head**: `20eae780a`

## 一个必须首先说明的自指现象

Task 的 AC5 要求盘点前后 `git ls-files --others --exclude-standard` **保持 1591**。
实测在写入本 Task 的第一份证据后变成了 **1592**。

**原因是我自己的产物也是未入库文件。** 本 Task 的证据写在
`verification/GOV-UNTRACKED-BACKLOG-1/` 下，在提交前它就是新的 untracked 文件。

这不是失败，但如果我假装「1591 保持不变」就是撒谎。**正确的表述是**：

- 盘点开始时：**1591** 个未入库文件，全部属于本 Task 之前就存在的积压；
- 盘点过程中：+1（本 Task 自己的 `ac1-ac3-inventory.json`），之后每次新增证据再 +1；
- **积压本身（1591 项）未被本 Task 增删**——这一点用下面的判据证明：

```
git ls-files --others --exclude-standard | grep -v '^verification/GOV-UNTRACKED-BACKLOG-1/' | wc -l  →  1591
```

## AC1 — 构成

### 按顶层目录

| 目录 | 文件数 | 占比 |
|---|---:|---:|
| `verification/` | **1470** | **92.4%** |
| `.orchestrator/` | 67 | 4.2% |
| `doc/` | 32 | 2.0% |
| `archive/` | 19 | 1.2% |
| 其它（含两个异常条目） | 3 | 0.2% |
| **合计** | **1591** | 100% |

### `verification/` 内部（前 7）

| 子目录 | 文件数 |
|---|---:|
| `P02` | **1072** |
| `P22` | 69 |
| `P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION` | 60 |
| `P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION` | 39 |
| `P04` | 38 |
| `P02-NEW-TIME-BASELINE` | 33 |
| `P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE` | 25 |

`verification/P02` 一项就占 1072 / 1591 = **67%**，且从文件名看主要是
`*.prompt.md` / `*.stdout.md` / `*.stderr.log` / `*.exit` / `*.stdout.jsonl`
这类 **agent 运行产物**（dsh / codex / agy 的派发记录），不是项目文档。

### 为什么 `git status` 只显示 1235

Git 把整目录折叠成一条 `??`。`git ls-files --others --exclude-standard` 才是文件级真相。
**流传的「1233」既不是条目数（1235）也不是文件数（1591）**，来源不明。

## AC3 — 引用关系

判据：在 971 个已入库的 `doc/**/*.md` 中搜索该路径，要求**边界匹配**
（前后不能是路径字符）；短名（<8 字符）额外要求被反引号/引号包裹。

| 类别 | 数量 |
|---|---:|
| 未入库文件总数 | 1591 |
| 被至少一个 `doc/**/*.md` 引用 | **137** |
| 未被引用 | **1454** |

### 137 项引用的性质

全部 137 项都命中 `doc/tasks/`、`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、
`doc/reviews/` 或 `doc/handoffs/`——即**都是 load-bearing 引用**，不是行文里偶然提到。

典型样本：

```
.orchestrator/BACKLOG.md                      <- doc/tasks/ENV-BUNDLE-1.md, doc/tasks/P09.md
.orchestrator/tasks/P04-role.json             <- doc/tasks/P04.md
.orchestrator/tasks/P10-role.json             <- doc/tasks/P10.md
archive/history/2026-10-12/REBASELINE_PLAN.md <- doc/tasks/P06.md
```

**按 AC3，这 137 项一律留在原路径**，不得移动、删除或归档。

### 两个异常条目的引用是自指的

`CON` 与长句名文件都只被 `doc/tasks/GOV-UNTRACKED-BACKLOG-1.md` 引用——
**也就是本 Task 自己刚写的文件**。

也就是说：**它们在被本 Task 记录之前，没有任何已入库文档引用它们**。
这对 AC2 的处置判断很关键：它们不是别人的证据，是无主产物。

## 方法可复跑

```powershell
git -C "G:\CODEX\New Manga" ls-files --others --exclude-standard
git -C "G:\CODEX\New Manga" status --porcelain --untracked-files=all
```

原始数据见 `ac1-ac3-inventory.json` 与 `ac3-references.json`。
