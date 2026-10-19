# 注入证据（P09-PREVIEW-LIFECYCLE-RECLAIM-1）

**最终更新**：2026-10-19 · **HEAD**：`583d2f257` · **执行**：dsh

**本文件取代早先版本。** 早先版本里有一句被 R9 证明为假的话（「三者都拒绝空目录」，而当时只有 AC2 拒绝）—— 那句及其原因保留在 §5，因为删掉它等于抹去发现。

---

## 读之前需要知道的两件事

**① 探针会清理自己的固定 fixture 目录。** 四个探针启动时 `shutil.rmtree` 自己的 `agent-output/coordinator/<name>/`。**若该目录里有先前运行的数据，它会被删除。** R10 因此无法按文档给出的路径逐字运行这四条命令，只能绕道副本。**这不是本轮引入的行为，但它是复审的固定成本，写在这里以免下一位复审者再发现一遍。**

**② 有三处断言，我无法在本平台上用注入区分。** 见 §4。

---

## 1. lock 幸存者断言（R7 → R8 → R9 → R10）

**最终形式**：`survivor_names == ['.preview-lifecycle.lock']`，**且 `survivor_names` 取【根目录相对路径】**，不是 basename。

| 注入 | 基线 | 注入后 | 判别力 |
|---|---|---|---|
| 空目录（连锁文件也没了）· leak probe | exit 0 | **exit 1** | ✅ CONFIRMED |
| 空目录 · retry probe | exit 0 | **exit 1** | ✅ CONFIRMED |
| orphan-dir 下的 decoy lock · batch probe | exit 0 · `0 unexplained` | **exit 1** · `1 unexplained` | ✅ CONFIRMED |

**注入输出（batch）**：
```
INJECTED: decoy lock at orphan-dir/.preview-lifecycle.lock (root lock untouched)
A) LEAK: 0 row(s), 0 unexplained file(s)   RESULT = PASS
B) LEAK: 0 row(s), 1 unexplained file(s)   RESULT = FAIL (unexplained files survived)
```

## 2. 同名、异路径孤儿文件（batch）

**针对**：文件归属按完整相对路径而非 basename。

| 运行 | 结果 |
|---|---|
| 基线 | `exit 0` · `LEAK: 0 row(s), 0 unexplained file(s)` · PASS |
| 注入 | **`exit 1`** · `LEAK: 0 row(s), 1 unexplained file(s)` · **FAIL** |

```
INJECTED: orphan-dir/preview-b4bd1a05….png (same basename as previews/preview-b4bd1a05….png)
```

**⚠️ 第一次尝试无效**：注入建在 `files_after` 收集【之后】，孤儿从未进入被测列表，探针 PASS 与断言无关。**若不检查注入点位置，那次运行会被误读成「探针仍有洞」。**

## 3. 存活 row 的文件缺失（batch）与 AC2 失败侧

| 注入 | 基线 | 注入后 | 判别力 |
|---|---|---|---|
| 删除 b2 预览文件、保留其 catalog row | exit 0 | **exit 1** · `row survived but its file is missing` | ✅ CONFIRMED |
| 快照注入为空（删除成功但不回收）· **AC2** | exit 0 · `0 rows, 1 files` | **exit 1** · `1 rows, 2 files` | ✅ CONFIRMED |

**AC2 注入的完整输出**：
```
B) 注入空快照    exit=1  after delete: 1 rows, 2 files
   RESULT = FAIL (C1 says referenced previews are reclaimed; they were not)
   - keys handed to the reader were not reclaimed: ['preview-d1a77afb99da49c5...']
```

**注入点**：`src/bootstrap/core_service.py` 单书路径的 `preview_resource_ids_for_artifacts(...)` 调用替换为 `[]`。

**这条注入证明**：**「删除报告成功」与「预览被回收」是两件可分离的事，而 AC2 探针区分它们** —— 注入后删除仍报成功，探针仍报红。

## 4. ⚠️ 三处我无法在本平台上区分的断言

**leak / retry / AC2 三个探针的 lock 比较从 basename 改为相对路径（R10 Finding 1）。我对 batch 证明了该改动有效（§1 第三行），但对这三个无法做同一种注入。**

**R10 的注入方式是「删掉根 lock + 在子目录建一个」。我尝试后得到**：

```
PermissionError: [WinError 32] 另一个程序正在使用此文件，进程无法访问:
  ...\ac4-assert\derived\.preview-lifecycle.lock
```

**探针运行时 `ResourceCatalogStore` 持有根 lock，Windows 不允许删除它。** R10 能在那个时点删掉，说明它的插入位置与判定时点不同；在判定时点我做不到。

**而「只加 decoy、不删根 lock」对这个三个探针不构成区分**：

| 实现 | decoy 存在时的 `survivor_names` | 结果 |
|---|---|---|
| basename 比较（修复前） | `['.preview-lifecycle.lock', '.preview-lifecycle.lock']` | 长度 2 ≠ 预期 → **FAIL** |
| 相对路径比较（修复后） | `['.preview-lifecycle.lock', 'orphan-dir/.preview-lifecycle.lock']` | ≠ 预期 → **FAIL** |

**两边都 FAIL，所以这个注入证明不了改动修好了什么。**

**结论**：**这三处的改动是代码审查可读的（一行比较表达式），但缺少失败侧注入证据。我不把「两边都红」的注入记作已验证。**

## 5. 早先版本为何有一句假话（保留）

**早先版本写着「孤立 PNG 注入下四个 probe 都拒绝」与「三者都拒绝空目录」。R9 复跑后指出：当时只有 AC2 probe 会 exit 1。**

**原因**：**R8 的修复把判定写成了 `leaked_files = 0 if survivor_names == expected else len(survivor_names)`** —— **`len([])` 是 0，所以空目录读作「无泄漏」。** **同一个洞换了个写法又被造了一遍。**

**我当时的注入只跑了一个探针，却把结论推广到三个。** **这句话不成立不是因为代码没修，而是因为我从一个样本推到了全部。** R9 之后判定改为布尔比较本身，§1 的两行是那之后的运行。