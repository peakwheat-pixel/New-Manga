---
task_id: GOV-EVIDENCE-DIR-SWEEP-1
author: dsh
recipient: Codex
base_commit: 3539d8d75
delivery_head: 24fcfae13f9871e28885f9240f067476d72d9005
status: ready_for_review
---

# Handoff：GOV-EVIDENCE-DIR-SWEEP-1

## 一句话

两个 evidence 目录共 **19 个文件，5 个没有 Canonical Evidence 行**。读内容后判定
**5 个全部 `REGISTER`，0 个 `ARCHIVE`**——没有文件需要移动。

## 盘点结果

| Task | 文件 | 已登记 | 未登记 |
|---|---:|---:|---:|
| `EXPORT-REVEAL-1` | 12 | 8 | **4** |
| `P15` | 7 | 6 | **1** |
| **合计** | **19** | **14** | **5** |

**19 个全部已入库**（`git ls-files --others` = 0）。「未登记」指未在证据表登记，不是未纳管。

## 5 个未登记文件，以及它们为什么都有判别力

| 文件 | 关键内容 | 为什么不能归档 |
|---|---|---|
| `post-merge-packaged-capture-error.log` | `error: Unrecognized option: 'A'` / **`EXIT_CODE=101`** | **失败记录**——证明该测试非一次通过 |
| `cargo-test-unfiltered-first-run.log` | **`EXIT_CODE=101`** | P15 的 Closeout **明确点名**「如实命名」 |
| `pytest-core.log` | `405 passed, 1 warning` / `EXIT_CODE=0` | Closeout 引用「Core 405 passed」 |
| `rust-source.log` | `82 passed; 0 failed; 1 ignored` / `EXIT_CODE=0` | Closeout 引用该数字 |
| `rust-packaged.log` | `8 passed; 0 failed` / `EXIT_CODE=0` | Closeout 引用该数字 |

**两份失败日志尤其重要**：删掉它们会让证据集**看起来更干净**，但会抹掉「曾经失败过」这个事实。

而 P15 的 Closeout 原文是：「Owner 保留未过滤首跑的失败日志并**如实命名**为
`cargo-test-unfiltered-first-run.log`（exit 101）」——这是**证据诚实性的正向记录**，
不留这份文件，那句表扬就没有依据。

## 为什么没有一个 `ARCHIVE`

每个文件都能在对应 Task 的 **Closeout Record** 里找到文字引用。按 Task 的 AC3，
**有引用者一律保留**。因此 `ARCHIVE` 候选为 0，AC4（执行移动）标 `NOT_APPLICABLE`
而非勾选——不适用不等于达成。

## 检查器效果

| Task | 改动前 | 改动后 |
|---|---:|---:|
| `EXPORT-REVEAL-1` | **7 errors** | **2 errors** |
| `P15` | **4 errors** | **2 errors** |

**剩余 4 个错误全部是既有的，各有归属**：

| 错误 | 归属 | 是否本 Task 造成 |
|---|---|---|
| `EXPORT-REVEAL-1` pin 失配（`M2-C1` 契约） | `GOV-PIN-LINEAGE-1` | 否 |
| `P15` pin 失配（`SettingsPage.test.tsx`） | `GOV-PIN-LINEAGE-1` | 否 |
| `P15` 缺 `resource-manifest.json` | `GOV-P15-MANIFEST-1` | 否 |
| `EXPORT-REVEAL-1` AC4 未完成 | **真实情况**（③ `BLOCKED`） | 否 |

## 请 Review 重点核对的三处

### 1. 五个 `REGISTER` 判定是否都有内容依据（核心）

Task 的 AC2 要求「判据必须引用文件实际内容，不得只看文件名」。

请**自己打开这 5 个文件**，确认：
- 我给的内容描述是否准确（尤其两份失败日志的 `EXIT_CODE=101`）；
- 有没有哪个文件其实该 `ARCHIVE`——即**无现行引用且只是冗余过程日志**。

**如果你认为任何一个应当归档，请明确说出来。**

### 2. AC4 标 `NOT_APPLICABLE` 是否恰当

因为 0 个 `ARCHIVE`，我把「执行移动」标为 `NOT_APPLICABLE`（`[x]`）。

但另一种做法是保持 `[ ]` + `<<PARTIAL: 无 ARCHIVE 项，未执行移动>>`。

**我选 `NOT_APPLICABLE` 的理由**：「没有需要移动的东西」= 本 Task 范围内这条不产生要求，
不是「做不成」。而 `EXPORT-REVEAL-1` AC4 用 `BLOCKED` 是因为「确实要做但被环境阻塞」。
**两者的区别是「不需要」vs「做不到」。**

请判断这个区分是否成立，还是我在为一个方便的选择找理由。

### 3. 我这次又加错了表，请核对修正是否彻底

第一次运行时，我把 5 行补登记加进了 `Resource Manifest` 表而不是
`Canonical Evidence` 表，检查器报了 4 条 `Resource disposition 无效`。

我用「限定在 `## Canonical Evidence` 与下一个 `## ` 之间」的方式修正了。

**请核对：现在这 5 行确实在 Canonical Evidence 表内，且 Resource Manifest 未被污染。**

## 明确未做

- 未移动、未删除任何文件（0 个 `ARCHIVE`）。
- 未改两个 Task 的 status、AC 文字、Closeout Record、Resource Manifest。
- 未修 pin 失配（属 `GOV-PIN-LINEAGE-1`）。
- 未创建 `P15` 的 manifest（属 `GOV-P15-MANIFEST-1`）。
- 未改 `src/`、`apps/`、`tests/`、`tools/`。

## 已声明的局限

1. **我只读了 19 个文件中的 5 个未登记文件的完整内容**，其余 14 个已登记文件仅核对
   其登记状态与 hash，未重读内容。若某个已登记文件其实内容不符，本 Task 不会发现。
2. **未做跨仓库引用扫描**：我只检查了「该 Task 自己的 Closeout/Task 文件是否引用」，
   没有扫描全仓其它文档是否引用某些文件。若判定 `ARCHIVE` 时漏掉外部引用会有风险——
   但本次 0 个 `ARCHIVE`，该风险未实际发生。
3. **AC4 的 `NOT_APPLICABLE` 是一个判断**，见上文第 2 点。

## 接收方式

Reviewer：**Antigravity**（不得由 dsh 自审），针对固定 `delivery_head = 24fcfae13f9871e28885f9240f067476d72d9005`。
