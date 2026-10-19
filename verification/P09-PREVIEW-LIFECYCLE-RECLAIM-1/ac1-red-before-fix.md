# AC1 修复前的红灯证据

**采集时间**：2026-10-19 · **采集者**：dsh
**触发**：R4 Finding 1 —— 此前 `ac4-leak-assert-probe.py` 只在修复后运行过，Task 要求「修前必须先跑出红」，而修复前的泄漏记录不能替代这条指定探针的红灯结果。

## 方法

**同一份探针文件**，唯一差异是 `AC4_REPO` 指向哪棵树：

```powershell
# A) 指向主仓库（已修复）
python verification/P09-PREVIEW-LIFECYCLE-RECLAIM-1/ac4-leak-assert-probe.py

# B) 指向修复前的隔离副本
git worktree add --detach <临时目录> 779a571ba          # 探针提交，其父尚未修复
$env:AC4_REPO = <临时目录>
python verification/P09-PREVIEW-LIFECYCLE-RECLAIM-1/ac4-leak-assert-probe.py
git worktree remove --force <临时目录>                   # 只移除自己建的这个
```

**为什么需要 `AC4_REPO`**：探针原先硬编码 `REPO = Path(r"G:\CODEX\New Manga")` 并据此 `sys.path.insert`。**它在副本目录里执行，却 import 主仓库的 `src/`** —— 所以第一次补证时，B 场景跑的是已修复的代码，也报了 PASS。**那次运行对修复前的行为什么也没证明。** 探针现在从环境变量取 `REPO`。

## 结果

| 场景 | 代码版本 | 结果 | 退出码 |
|---|---|---|---|
| **A** | 主仓库，已修复（`6befb8ba5`）| `LEAK: 0 row(s), 0 file(s)` / `RESULT = PASS` | **0** |
| **B** | 副本，修复前（`779a571ba`）| `LEAK: 3 row(s), 3 file(s)` / `RESULT = FAIL (leak present)` | **1** |

**B 的残留明细**：
```
surviving rows:  preview-5480bf38…, preview-81b52ed9…, preview-b6a0707d…
surviving files: .preview-lifecycle.lock, preview-5480bf38….png,
                 preview-81b52ed9….png, preview-b6a0707d….png
```

**3 次读取 → 3 个泄漏行 + 3 个泄漏文件**，1:1 对应，与 Task 记录的泄漏率一致。

## 结论

**AC1 的红灯证据已补齐，`AC1 → VERIFIED`。**

**附带证明**：这条探针在修复前后的代码上分别报红与报绿，**所以它的判别力不需要再靠注入来间接说明** —— 两侧运行的是同一份探针、同一个夹具、同一段序列，唯一变量是被测代码。