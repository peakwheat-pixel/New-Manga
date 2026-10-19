# AC3 — 只读保护核验

**Task**: GOV-EVIDENCE-UNIQUE-1 · **性质**: 只读 · **核验时间**: 2026-10-20

## 一、要求

AC3 原文：

> 不改来源 Task、Review、Canonical Evidence/pin、61 项源文件或生产文件；
> 本 Task **不补登记来源 pin、不处置文件**。

## 二、核验方法

以**冻结 head `3c9ee0877`** 为基准，检查本 Task 至此的全部提交改动了哪些路径，
再与 61 项源文件清单、13 个来源 Task、`doc/reviews/`、`doc/handoffs/` 逐一比对。

```powershell
git log --oneline 3c9ee0877..HEAD
git diff --name-only 3c9ee0877..HEAD
```

## 三、本 Task 的全部提交（7 个）

```
2f36f71ec  AC1 v2 adds each file's role in its evidence group
ef2182efa  AC2 complete - 83 ACs judged across all 13 tasks
318a69642  coverage batch 2 - three of four tasks record failures, not passes
fa5ecb678  per-AC coverage for the first four tasks
349277de3  rewrite the goal to AC evidence coverage, per r18
c9a4d1d76  AC mapping finds gaps, not unique evidence
7a434a82d  freeze the 61-file input and report what the strict criteria actually yield
```

## 四、改动路径全清单（15 条）

| 路径 | 归属 | 是否允许 |
|---|---|---|
| `doc/REBASELINE_PLAN.md` | 本 Task 的 DAG 状态（ready → in_progress） | ✔ 生命周期元数据 |
| `doc/tasks/GOV-EVIDENCE-UNIQUE-1.md` | 本 Task 自身 | ✔ 允许 |
| `verification/GOV-EVIDENCE-UNIQUE-1/ac1-input-freeze-and-criteria.md` | 本 Task 证据 | ✔ 允许 |
| `verification/GOV-EVIDENCE-UNIQUE-1/ac1-matrix-v2.json` | 同上 | ✔ |
| `verification/GOV-EVIDENCE-UNIQUE-1/ac1-matrix-v2.md` | 同上 | ✔ |
| `verification/GOV-EVIDENCE-UNIQUE-1/ac1-verdict-matrix.json` | 同上 | ✔ |
| `verification/GOV-EVIDENCE-UNIQUE-1/ac1-verdict-matrix.md` | 同上 | ✔ |
| `verification/GOV-EVIDENCE-UNIQUE-1/ac2-ac-mapping-and-uniqueness.md` | 同上 | ✔ |
| `verification/GOV-EVIDENCE-UNIQUE-1/ac2-coverage-batch1.md` | 同上 | ✔ |
| `verification/GOV-EVIDENCE-UNIQUE-1/ac2-coverage-batch2.md` | 同上 | ✔ |
| `verification/GOV-EVIDENCE-UNIQUE-1/ac2-coverage-batch3-and-summary.md` | 同上 | ✔ |
| `verification/GOV-EVIDENCE-UNIQUE-1/content-digest.json` | 同上 | ✔ |
| `verification/GOV-EVIDENCE-UNIQUE-1/input-manifest.json` | 同上 | ✔ |
| `verification/GOV-EVIDENCE-UNIQUE-1/source-task-acs.json` | 同上 | ✔ |
| `verification/P09-GOVERNANCE-DEBT-20261019/codex-adjudicate-evidence-unique-r18.md` | Codex r18 裁定（本 Task 的授权来源） | ✔ |

**15 条全部属于「本 Task 自身」或「本 Task 的生命周期元数据」。零越界。**

## 五、三项关键比对

### 5.1 61 项源文件：**零变动**

```
overlapping paths: 0
```

把 `input-manifest.json` 的 61 个 `path` 与 `git diff --name-only` 结果求交集，
**交集为空**。

### 5.2 13 个来源 Task：**零变动**

对 `doc/tasks/` 下的 13 个来源 Task 文件做匹配，**命中 0**。

### 5.3 `doc/reviews/` 与 `doc/handoffs/`：**零变动**

匹配 `doc/reviews/` 与 `doc/handoffs/`（排除本 Task 未来可能产生的 Handoff/Review），
**命中 0**。

### 5.4 生产文件：**零变动**

15 条改动路径中**没有任何** `src/`、`apps/`、`tests/`、`tools/` 下的文件。

## 六、本 Task 明确未做的事

| 项 | 状态 |
|---|---|
| 补登记来源 pin | **未做**（AC3 禁止） |
| 处置/移动/删除/归档任何候选文件 | **未做** |
| 修改 61 项源文件内容 | **未做** |
| 修改来源 Task 的 AC 勾选或 status | **未做**（含 `EXPORT-REVEAL-1` 0/7 与 `P15` 0/6 两个异常） |
| 修改任何 Review | **未做** |
| 创建 linked worktree | **未做** |
| 修改 `.gitattributes` / `.gitignore` | **未做** |

## 七、两个异常的处理方式（AC3 的关键边界）

`EXPORT-REVEAL-1`（0/7 勾选）与 `P15`（0/6 勾选）都标 `done`。

**我发现它们在 AC 层面完全未勾选，但一个框都没有补勾。**

理由：
1. **AC3 明文禁止**修改来源 Task；
2. r18 §一 明确「本 Task 不得代替来源 Owner 勾选 13 项」；
3. 补勾需要逐项审查 AC 是否真被满足——而本 Task 的候选集只能证明
   「evidence 目录里有什么」，**不能证明来源 Task 的 AC 是否满足**。

**发现异常 → 记录 → 交裁定，不自行修复。** 这是 AC3 边界被真正遵守的证据。

## 八、可复跑

```powershell
git -C "G:\CODEX\New Manga" log --oneline 3c9ee0877..HEAD
git -C "G:\CODEX\New Manga" diff --name-only 3c9ee0877..HEAD
```

将 61 个 `path` 与第二条输出求交集，应为 0。

## 九、AC3 结论

**达成。** 本 Task 从冻结 head 起到 AC1/AC2 完成，未修改任何来源 Task、Review、
pin、61 项源文件或生产文件；未补登记、未处置任何文件。
15 条改动全部落在本 Task 自身与生命周期元数据范围内。
