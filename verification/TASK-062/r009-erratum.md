# TASK-062 · R-009 勘误记录（TASK-060 复审 P3「记录勘误」）

来源：[TASK-060 复审](../../doc/reviews/TASK-060-b28c615.md) 的 **R-009（P3，记录勘误）**。
TASK-062 的任务书把该项列为「R-009（P3，docs）：记录勘误建议（随手）」。

## 1. 复核结果（本次独立核对，2026-09-19）

### E-1：Handoff 的用例路径不存在

- 记录：`doc/handoffs/TASK-060-zcode-handoff.md:59` ——
  「`tests/workbench/test_shutdown_drain.py`：stub 适配 `shutdown() -> bool` 新契约…」
- 实测：
  ```powershell
  Get-ChildItem -Recurse -Filter test_shutdown_drain.py -Path tests
  ```
  唯一命中 **`tests/core/test_shutdown_drain.py`**；`tests/workbench/` 下**不存在**该文件。
  ⇒ 原记录的路径**错误**。（TASK-060 复审表把行号写作 `:57`，实测该 bullet 在第 **59** 行——
  行号亦需更正。）
- 实质影响：**无**。受影响的只是"哪份文件被适配"的文字描述；stub 适配本身由
  `tests/core/test_shutdown_drain.py` 承载，且 TASK-060 集成后全仓绿色。

### E-2：Task 的 `base_commit` 与判别树不一致

- 记录：`doc/tasks/TASK-060.md:11` `base_commit: 9522f2d…`；`:19` 亦写 base=`9522f2d`。
- 记录：`doc/tasks/TASK-060.md:68` 写「基线 master=`a2b23ad`」；`:71` 写「判别力（修前树
  **`a2b23ad`** detached）」。
- 实测：
  ```powershell
  git diff --name-only 9522f2d a2b23ad -- src tests    # 输出为空
  ```
  ⇒ 两棵树在 `src/` 与 `tests/` 上**逐字节等价**，AC ①「修前失败」的判别证据**仍然有效**，
  不因 base 标注不一致而失效。
- 实质影响：**无**（`9522f2d` 是"复审报告落库"提交，`a2b23ad` 是其后的 master 头；
  TASK-060 的 AC ① 本就允许 `be558ca` / `9522f2d` 二者之一）。

## 2. 可直接套用的更正文本

### 2.1 `doc/handoffs/TASK-060-zcode-handoff.md:59`

```diff
-1. `tests/workbench/test_shutdown_drain.py`：stub 适配 `shutdown() -> bool` 新契约（修前 `shutdown()` 无返回值，TASK-058 用例断言的是排空行为本身；现契约返回 drained 布尔，stub 需返回布尔）。
+1. `tests/core/test_shutdown_drain.py`：stub 适配 `shutdown() -> bool` 新契约（修前 `shutdown()` 无返回值，TASK-058 用例断言的是排空行为本身；现契约返回 drained 布尔，stub 需返回布尔）。（R-009 勘误：原文误记 `tests/workbench/…`）
```

### 2.2 `doc/tasks/TASK-060.md:11`

```diff
-base_commit: 9522f2df66a79b82bb2419bc99f84ef39694e513
+base_commit: 9522f2df66a79b82bb2419bc99f84ef39694e513   # 判别树 a2b23ad 与之在 src/tests 上逐字节等价（R-009）
```

### 2.3 `doc/tasks/TASK-060.md:19`

```diff
-**READY（2026-09-19，用户依 Qoder 后置复审报告重开）**：… base=9522f2d。开工先 `git merge master`。
+**READY（2026-09-19，用户依 Qoder 后置复审报告重开）**：… base=9522f2d（实际判别树 `a2b23ad`，二者在 `src/tests` 上 `git diff` 为空，代码等价；R-009）。开工先 `git merge master`。
```

### 2.4 `doc/STATUS.md` 台账（TASK-060 那一行，可选一句）

```diff
+修前树与 `9522f2d` 代码等价（`git diff --name-only 9522f2d a2b23ad -- src tests` 为空，R-009 勘误）。
```

## 3. 本切片的处置与理由（为何此处只是"记录"）

TASK-062 的任务书在 **允许修改范围** 中枚举的是
`src/application/maintenance/diagnostics.py`、`tests/diagnostics/**`、`tests/reading_export/**`、
本 Task / Handoff / `verification/TASK-062/**` / `doc/STATUS.md`（台账行）；
在 **禁止范围** 中写明「不得改 …**其他 Task**」。
`doc/tasks/TASK-060.md` 与 `doc/handoffs/TASK-060-zcode-handoff.md` **均不在允许范围内**，
因此本切片**不直接改**这两份文件，改为：

1. 在本文件中留下**逐条复核结论 + 可直接套用的更正文本**（上节 §2）；
2. 在 `doc/STATUS.md` 台账行登记该勘误（含"修前树与 `9522f2d` 代码等价"这一句，
   即 TASK-060 复审 R-009 明确要求集成时记录的内容）；
3. 在 Handoff 的"残留"节把 §2 的三处文字更正列为**集成时顺手可做的 docs-only 更正**
   （不改代码、无需重跑产品测试，符合协作协议 §6.8）。

**状态：`open`（已记录，未落改）** —— 不是遗漏，而是范围约束下的显式划分。
若集成方决定扩大本切片范围，则 §2 的补丁可直接套用；否则应在后续 docs 卫生提交中关闭。
