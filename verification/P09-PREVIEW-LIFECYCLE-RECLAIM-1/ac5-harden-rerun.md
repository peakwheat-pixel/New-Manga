# AC5 重跑记录：P09-AC3-DELETE-HARDEN-1 探针

**重跑时间**：2026-10-19 · **HEAD**：`77dfdd29b` · **执行**：dsh
**触发**：R3 Finding 4 —— 此前 AC5 为 `NOT_VERIFIED`，因为只跑了 `tests/storage` 而未跑该 Task 的探针。

## 调用方式（仓库内无驱动脚本，这是完整所需）

`n002-race-probe.py` 与 `n002-race-probe2.py` 从环境读取隔离目录，其余由探针自建：

```powershell
New-Item -ItemType Directory -Force -Path $root, $outside
$env:N002_ROOT = $root
$env:N002_OUTSIDE = $outside
python verification/P09-AC3-DELETE-HARDEN-1/n002-race-probe2.py
```

其余探针直接运行，无前置条件。

## 结果

| 探针 | 结果 | 备注 |
|---|---|---|
| `n004-ancestor-probe.py` | **SAFE** | 静态 junction 基准 |
| `n004-production-order-probe.py` | **SAFE** | 生产顺序 |
| `r5-p1-managed-remove-probe.py` | **SAFE** | delete 路径 |
| `r5-p1-cleanup-book-files-probe.py` | **SAFE** | delete 路径 |
| `r5b-p1-remove-managed-race-probe.py` | **SAFE** | TOCTOU |
| `r5b-p1-collect-orphans-race-probe.py` | **SAFE** | TOCTOU |
| `r6-p1a-publish-cleanup-race-probe.py` | **SAFE** | TOCTOU |
| `n002-race-probe2.py` | **SAFE** | `injection_fired=True`、`unlink_returned=False`、`outside_survived=True` |
| `n002-race-probe.py` | **INCONCLUSIVE** | `race_hook_fired=False` —— 它 hook 旧实现的 `Path.is_file`，在新实现下钩子不触发。**这是预期状态**，不是回归 |
| `ac7-verify-query-check.py` | **OK** | `queries_ok=9/9`；非 SAFE/FAIL 型，是查询检查 |

**计数**：**8 个有效 SAFE + 1 个预期 INCONCLUSIVE + 1 个查询检查**。

## 探针到覆盖项的映射（R6 Finding 2）

**上一版只并列了两组结果，读者需要自己推断 `probe2` 与 `probe` 的关系。这里写成一對一。**

| 覆盖项（HARDEN Task 的缺陷类别） | 承担证据的探针 | 结果 | 是否计入 AC5 |
|---|---|---|---|
| 静态 junction 基准 / 祖先重定向 | `n004-ancestor-probe.py`、`n004-production-order-probe.py` | SAFE | ✅ 计入 |
| `remove_managed` 删除路径 | `r5-p1-managed-remove-probe.py` | SAFE | ✅ 计入 |
| `cleanup_book_files` 删除路径 | `r5-p1-cleanup-book-files-probe.py` | SAFE | ✅ 计入 |
| `remove_managed` 的 TOCTOU 竞态 | `r5b-p1-remove-managed-race-probe.py` | SAFE | ✅ 计入 |
| `collect_orphans` 的 TOCTOU 竞态 | `r5b-p1-collect-orphans-race-probe.py` | SAFE | ✅ 计入 |
| publish/cleanup 的 TOCTOU 竞态 | `r6-p1a-publish-cleanup-race-probe.py` | SAFE | ✅ 计入 |
| **N-002：检查与删除之间父目录被替换** | **`n002-race-probe2.py`** | **SAFE，`injection_fired=True`** | ✅ **计入** |
| **同一 N-002 的初版实现** | **`n002-race-probe.py`** | **`race_hook_fired=False`** | ❌ **不计入** |
| 验收查询 | `ac7-verify-query-check.py` | `queries_ok=9/9` | ➖ 非 SAFE/FAIL 型 |

**关键映射**：**`n002-race-probe2.py` 覆盖的就是 `n002-race-probe.py` 试图覆盖的那一项（同一个 N-002 竞态）**，**两者是同一缺陷的两个版本，不是两个缺陷。** **因此 AC5 的覆盖项一项不少；`probe` 只是不作为证据，由 `probe2` 承担。**

**为什么 `probe` 不计入**：**它 hook 旧实现的 `Path.is_file`，在当前实现下钩子不触发（`race_hook_fired=False`）**。**它仍然打印 `SAFE`，因为在「外部文件存活」这个判定上无注入时结果恰好也是 SAFE** —— **这是 R6 Finding 2 指出的输出标签缺陷，属前置 Task 范围，未修改。** **`probe2` 的 `injection_fired=True` 使它的 SAFE 具备判别力。**

## 结论

**AC5（不回归 HARDEN 九探针）→ `VERIFIED`。**

**区别要点**：`n002-race-probe.py` 的 INCONCLUSIVE 与 SAFE 不同 —— 它的注入没有触发，所以它**不能**作为「竞态被防住」的证据；**能作此证据的是 `probe2`**（`injection_fired=True`）。两者都列在此处，以免读者把 9 个 SAFE 与 8 个有效证据混为一谈。