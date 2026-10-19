# 注入证据（R8 → R9 → R10 演进）

**最终更新**：2026-10-19 · **HEAD**：`82ead8c3f`

---

## ⚠️ 本文件早先版本含有一句与代码不符的话

**早先版本写着「孤立 PNG 注入下四个 probe 都拒绝，证明该问题已修复」以及「三者都拒绝空目录」。**

**R9 复跑后指出**：**当时只有 `ac2-referenced-preview-probe.py` 会在空快照下 exit 1，而 `ac4-leak-assert-probe.py` 与 `ac4-retry-manifest-probe.py` 都是 exit 0 / PASS。**

**原因**：**R8 的修复把判定写成了 `leaked_files = 0 if survivor_names == expected else len(survivor_names)`** —— **而 `len([])` 是 0，所以空目录读作「无泄漏」。** **同一个洞换了个写法又被造了一遍。**

**我当时的注入只跑了 `ac4-leak-assert-probe.py` 一个，却把结论推广到了三个。** **这句话不成立不是因为代码没修，而是因为我从一个样本推到了全部。**

**R9 之后**：**两个 probe 的判定改为布尔比较本身（`survivors_match = (survivor_names == expected_survivors)`），数字只用于打印。** **本文件下面的记录是那次修复之后的运行。**

---

## 注入 1：空幸存列表（连锁文件也没了）

**针对**：`survivor_names == ['.preview-lifecycle.lock']` 的字面集合断言。

**两个 probe 分别运行、分别记录**（不再从一个推广到全部）：

| 探针 | 基线 | 注入空目录 | 判别力 |
|---|---|---|---|
| `ac4-leak-assert-probe.py` | exit 0 · PASS | **exit 1** | **CONFIRMED** |
| `ac4-retry-manifest-probe.py` | exit 0 · PASS | **exit 1** | **CONFIRMED** |

## 注入 2：同名、异路径孤儿文件

**针对**：**文件归属按完整相对路径而非 basename 判定**。

**注入方式**：取 b2 预期存活预览的 `rel_path`（`previews/preview-<hex>.png`），**在 `orphan-dir/` 下创建同名文件**。

**⚠️ 第一次尝试无效，原因值得记录**：**注入建在 `files_after` 收集【之后】**，**所以孤儿根本不在被测文件列表里 —— 探针 PASS 是必然的，与断言是否严格无关。** **若不检查注入点位置，这次运行会被误读成「探针仍有洞」。**

| 运行 | 结果 |
|---|---|
| 基线 | `exit 0` · `LEAK: 0 row(s), 0 unexplained file(s)` · PASS |
| 注入（正确位置） | **`exit 1`** · `LEAK: 0 row(s), 1 unexplained file(s)` · **FAIL (unexplained files survived)** |
| 注入输出 | `INJECTED: orphan-dir/preview-b4bd1a05….png (same basename as previews/preview-b4bd1a05….png)` |

**判别力 = CONFIRMED。**

**这条注入同时是「完整路径比较生效」的直接证据**：**同名、不同目录 → 判为 unexplained**；**若仍按 basename 比较，它会与 `previews/…` 的同名文件混淆而不被发现。**

## 注入 3：存活 row 的文件被删（R8 Finding 2）

| 运行 | 结果 |
|---|---|
| 基线 | `exit 0` · PASS |
| 注入 | `exit 1` · `RESULT = FAIL (row survived but its file is missing: ['preview-…'])` |

**判别力 = CONFIRMED。** **失败信息曾误报为「book b2 itself is gone」，已在 R9 前修正。**

## 结论

**三组断言各有失败侧证据，且每组都在基线与注入两侧运行。**

**空目录注入之所以曾经失败，是因为判定用了计数；同名异路径注入之所以曾经误读，是因为注入点在被测数据收集之后。** **两次都不是断言写得不够漂亮，而是断言与实际执行路径不一致。**