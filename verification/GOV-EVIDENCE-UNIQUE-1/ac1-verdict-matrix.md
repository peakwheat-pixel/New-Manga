# AC1 — 61 项逐文件判定矩阵（初版）

**Task**: GOV-EVIDENCE-UNIQUE-1 · **冻结 head**: `3c9ee0877` · **性质**: 只读

## 结论摘要（先说不好看的）

| 判定 | 数量 |
|---|---:|
| `YES`（唯一最终证据） | **1** |
| `NO`（非唯一） | **5** |
| `UNKNOWN`（无法判定） | **55** |
| 其中：文件不存在 | 7 |

**55 个 UNKNOWN 不是没做完，是判据不允许我按文件名猜。**

`GOV-EVIDENCE-UNIQUE-1` 的 AC1 明文禁止「只依据文件名、目录或表面存在性判定」。
本 Task 的判据（见 `ac1-input-freeze-and-criteria.md`）进一步要求：
`linked_ac` 必须由**文件自身内容**唯一指向某个 AC，否则记 `UNKNOWN`。

实测结果是：**61 项中只有 1 项的内容本身唯一点名了一个 AC**。

## 为什么会这样

绝大多数候选是**测试/构建日志**（33 份 `RESULT_LOG`）。它们记录了「跑了什么、结果如何」，
但**不声明自己在证明哪个 AC**。例如：

```
verification/EXPORT-REVEAL-1/rust-source.log     —— 84 个 pass，但全文无 AC 引用
verification/P15/cargo-test-unfiltered-first-run.log —— 97 pass / 28 fail，无 AC 引用
```

要知道它证明哪个 AC，必须去读来源 Task 的 AC 原文并做语义判断。
**那是 AC2 的工作，不是我能在 AC1 的机械判据里代劳的。**

## 唯一判为 YES 的项

| seq | 路径 | 理由 |
|---:|---|---|
| 5 | `verification/FEAT-CREATE-3/dsh-review-r1.md` | 内容是独立 Review 叙述，自身点名 **AC1**，且同 Task 内无其它文件指向同一 AC |

同 Task（`FEAT-CREATE-3`）只有这 1 个候选，所以「无等效替代」自动成立。

## 判为 NO 的 5 项

4 项是因为**同 Task 内有等效替代**（多个 attempt 日志指向同一 AC）：

| seq | 路径 | 指向 | 替代数 |
|---:|---|---|---:|
| 40 | `P15-HOST-2/frontend-vitest-alias-attempt.log` | AC1 | 有 |
| 42 | `P15-HOST-2/frontend-vitest-isolated.log` | AC1 | 有 |
| 41 | `P15-HOST-2/frontend-vitest-final.log` | AC1–AC4 | 有 |
| 58 | `P19-UI-FIX-2/bookshelf-import-targeted-test.log` | AC3 | 有 |

第 5 项是 `SCRIPT`/`CONFIG` 类：**它们能产生证据，本身不是证据**。

## 7 项不存在（BLOCKED_ABSENT）

全部在 `FEAT-IMPORT-MULTI-1`：

```
appdata-preservation.log      checkpoint.md
fixture-generation.log        gui-runner-console.log
isolation-prepare.log         main-worktree-status.log
make-fixtures-r1.py
```

**按判据，缺失记 `UNKNOWN` 而不是 `NO`**——不知道内容就不能断言它不唯一。

这 7 项也再次证明 `GOV-DEBT-CLEANUP-2` AC7 的分类是**纯按文件名**做的：
它把 7 个不存在的路径当成候选列了出来。

## 完整矩阵

逐项数据见 `ac1-verdict-matrix.json`（含 sha256、content_kind、linked_ac、
equivalent_substitutes、verdict、reason 六个字段）。

## 我必须声明的局限

**本矩阵的 55 个 UNKNOWN 不等于"它们不唯一"，只等于"用内容自身无法判定"。**

要让判定推进到 `YES`/`NO`，需要 AC2 的工作：把每个来源 Task 的 AC 原文与
候选内容做**语义对照**。那一步不能靠脚本，也不能靠文件名。

**因此 AC1 目前只能算部分达成。** 我不会为了让表好看而把 UNKNOWN 改写成 NO ——
那正是本 Task 要清理的那类债务。

## 下一步（AC2 计划）

对 13 个来源 Task（全部 `done`）逐个：

1. 读该 Task 的 AC 原文；
2. 读它名下候选的实际内容；
3. 判断每份候选在证明哪个 AC；
4. 建立 `AC → 全部候选` 的映射，据此判定唯一性。

这一步需要逐文件语义判断，会慢，但**这正是本 Task 存在的理由**。
