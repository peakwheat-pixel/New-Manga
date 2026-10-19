# AC1 / AC3 — 预算变更与边界验证

**Task**: GOV-PLAN-BUDGET-1 · **性质**: 单一数值变更 + 隔离 fixture 边界验证

## AC1 — 只改目标预算项

`tools/governance/check.ps1` L127 是预算循环中的一项：

```powershell
foreach ($budget in @(
    @{ Path = 'doc/STATUS.md'; Bytes = 3200; Lines = 45 },
    @{ Path = 'doc/REBASELINE_PLAN.md'; Bytes = 2500; Lines = 35 }
)) {
```

改动（**仅此一处**）：

```diff
-    @{ Path = 'doc/REBASELINE_PLAN.md'; Bytes = 2500; Lines = 35 }
+    @{ Path = 'doc/REBASELINE_PLAN.md'; Bytes = 7000; Lines = 64 }
```

验证：

| 检查 | 结果 |
|---|---|
| diff 行数 | **1 行改动**（`1 insertion(+), 1 deletion(-)`） |
| `doc/STATUS.md` 预算项 | 仍为 `3200 / 45`，**未改动**（脚本内断言其出现次数仍为 1） |
| 其它预算项 / 比较条件 / warning 逻辑 | 未触碰 |
| 文件行尾 | 改前 275 LF / 0 CRLF，改后 275 LF / 0 CRLF |

## AC3 — 边界验证（隔离 fixture）

方法：在隔离 worktree `GOV-PLAN-BUDGET-1` 内，用备份的 Plan 构造精确大小的副本覆盖
`doc/REBASELINE_PLAN.md`，运行真实的 `tools/governance/check.ps1`，读取其预算相关输出，
最后从备份恢复（已验证恢复后 `git diff --stat` 为空）。

| 用例 | 检查器输出 | 判定 |
|---|---|---|
| 恰好 **7000 bytes / 64 lines** | `WARN: 已达到预算的 80%：7000 bytes / 64 lines` | **不超限**，仅 80% 提示 ✓ |
| **7001 bytes / 64 lines**（超 1 字节） | `FAIL: 超过防膨胀预算：7001 bytes / 64 lines` | 正确拦截 ✓ |
| **7000 bytes / 65 lines**（超 1 行） | `FAIL: 超过防膨胀预算：7000 bytes / 65 lines` | 正确拦截 ✓ |
| **5600 bytes / 40 lines**（7000 的 80%） | `WARN: 已达到预算的 80%：5600 bytes / 40 lines` | 80% 阈值随新上限正确移动 ✓ |

**结论**：新上限 `7000 / 64` 生效，边界判定严格（等于上限通过、超 1 单位即拦截），
且 80% warning 阈值按新数值计算（5600 bytes / 51.2→52 行），未出现旧阈值残留。

## 未做的事

- 未修改 `doc/STATUS.md` 的预算项或内容。
- 未修改 Plan 的预算数值（Plan 只被 fixture 临时覆盖并已完整恢复）。
- 未改动检查器的其它任何逻辑。
