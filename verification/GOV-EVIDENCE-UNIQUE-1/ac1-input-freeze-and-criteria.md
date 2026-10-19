# AC1 准备 — 61 个输入文件的冻结清单与方法定义

**Task**: GOV-EVIDENCE-UNIQUE-1 · **性质**: 只读判定 · **冻结 head**: `3c9ee0877`

本文只做两件事：**冻结输入**、**定义判据**。判定结论在 AC1 的逐项矩阵里，
不在本文。

## 一、输入来源

唯一输入是 `verification/GOV-DEBT-CLEANUP-2/ac7-evidence-dir-files.md` 的「逐文件」节。
该节按 13 个来源 Task 分组，每组一张 4 列表：

```
| 文件 | 候选分类 | 唯一最终证据 | 处理结论 |
```

原始共 **61 行**，与 `GOV-DEBT-CLEANUP-2` AC7 声称的 61 项一致（该数字经 Antigravity
独立复核确认）。逐项清单见 `input-manifest.json`。

## 二、冻结发现：61 项里有 7 项不存在

这是本次冻结最重要的结果，它本身就说明 AC7 的原始分类有问题。

| 项 | 结果 |
|---|---|
| 存在 | **54** |
| **不存在** | **7** |
| 存在的 54 项是否都在 Git 追踪中 | **是，54/54** |
| 存在但未入库 | 0 |

**7 个不存在的文件全部位于 `FEAT-IMPORT-MULTI-1`**（该组共 8 项，只活下来 1 项）：

```
verification/FEAT-IMPORT-MULTI-1/appdata-preservation.log
verification/FEAT-IMPORT-MULTI-1/checkpoint.md
verification/FEAT-IMPORT-MULTI-1/fixture-generation.log
verification/FEAT-IMPORT-MULTI-1/gui-runner-console.log
verification/FEAT-IMPORT-MULTI-1/isolation-prepare.log
verification/FEAT-IMPORT-MULTI-1/main-worktree-status.log
verification/FEAT-IMPORT-MULTI-1/make-fixtures-r1.py
```

### 这说明什么

`GOV-DEBT-CLEANUP-2` AC7 的分类是**纯按文件名产生的**：它从各 Task 的 evidence 目录
**列出文件名**并分类，**没有验证文件是否存在**。于是 7 个已经不存在的路径被当成
「候选证据」列了出来。

这与 AC7 自己的表述一致——它承认「**没有做**『唯一最终证据』判定」。
但比它自己说的更糟一点：**连"这些文件是否存在"都没验证**。

**因此本 Task 对缺失项的处理是**：判为 `BLOCKED_ABSENT`，不猜内容、不按名字推断，
并记录每个缺失项在 `FEAT-IMPORT-MULTI-1` 的现有证据中是否有等效替代。

## 三、候选分类的实际分布

| 分类 | 数量 | 来源表的含义 |
|---|---:|---|
| `A` | 10 | 来源表未给出定义 |
| `B` | 49 | 来源表未给出定义 |
| `C` | 2 | 来源表未给出定义 |

**注意**：`ac7-evidence-dir-files.md` **从未定义 A/B/C 是什么**。
我在该文件中找不到分类标准的任何说明。

**因此本 Task 不使用 A/B/C 作为判据**，只把它们作为来源表的历史标注记录下来。
判定完全基于下节的独立判据。

## 四、判据（本 Task 定义的唯一标准）

对每一项，回答一个问题：

> **这个文件本身的内容，是否足以独立证明某个**已释放** AC 已被满足，
> 并且**没有其它文件能起到同样作用**？**

拆成可操作的六个字段：

| 字段 | 取值 | 判定方式 |
|---|---|---|
| `file_sha256` | 哈希或 `ABSENT` | 直接从文件字节算；缺失记 `ABSENT` |
| `content_kind` | 见下 | 读文件内容后归类，**不按文件名推断** |
| `linked_ac` | `TASK#ACn` 或 `NONE_FOUND` | 读内容找它证明的是哪个 AC |
| `equivalent_substitutes` | 路径列表或 `NONE` | 同 Task 内是否有其它文件能证明同一 AC |
| `unique_final_evidence` | `YES` / `NO` / `UNKNOWN` | 仅在 `linked_ac` 明确且替代为 `NONE` 时为 `YES` |
| `reason` | 一句话 | 必须引用文件的实际内容特征 |

`content_kind` 取值：

- `RESULT_LOG` —— 测试/构建/运行输出，含 pass/fail 或 exit 码
- `EVIDENCE_NARRATIVE` —— 人工撰写的证据说明（如 checkpoint.md、总结）
- `SCRIPT` —— 可执行脚本（不是运行结果）
- `CONFIG` —— 配置或 fixture 定义
- `UNKNOWN` —— 读完仍无法归类

**判定规则（硬约束，防止按名字猜）**：

1. **必须读过文件内容**才能填 `content_kind` 与 `reason`。仅凭文件名/目录/扩展名的判定无效。
2. `unique_final_evidence = YES` 需要同时满足：`linked_ac` 非 `NONE_FOUND`、
   `equivalent_substitutes = NONE`、且内容是 `RESULT_LOG` 或 `EVIDENCE_NARRATIVE`。
   **脚本与配置文件永远不是 `YES`**——它们能产生证据，但本身不是证据。
3. 缺失文件一律 `UNKNOWN`（不是 `NO`）——不知道内容就不能断言它不唯一。
4. 任何"看起来应该能证明"但读后无法确认对应哪个 AC 的，一律 `UNKNOWN`。

## 五、AC2 的映射口径

对**每个已释放 AC** 建立 `AC → 它的 Canonical Evidence` 映射，然后判断
本 Task 的 61 项在其中的角色。只对能在来源 Task 里找到已释放 AC 的建立映射。

**已释放**的定义：该 Task 的 `status` 为 `done` / `closed_with_limitations` /
`cancelled` / `superseded` / `historical`。非终态 Task 的 AC 不参与唯一性判定，
其证据只记为 `NOT_RELEASED`。

## 六、明确不做

- 不修改 61 个文件中的任何一个（只读）。
- 不修改任何 Task、Review、pin、Plan、STATUS。
- 不补登记、不移走、不归档任何候选。
- 不创建 worktree。
- 不把"缺失"写成"不存在所以不唯一"——缺失是 `BLOCKED_ABSENT`，不是结论。

## 七、复跑

```powershell
python -c "import json,io; d=json.load(io.open(r'verification/GOV-EVIDENCE-UNIQUE-1/input-manifest.json',encoding='utf-8')); print(d['total'], d['exists'], d['missing'])"
git -C "G:\CODEX\New Manga" ls-files --error-unmatch <path>
```
