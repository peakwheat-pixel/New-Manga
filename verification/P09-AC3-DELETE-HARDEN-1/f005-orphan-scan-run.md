# F-005：orphan 扫描补入后 verify_all.py 的独立运行记录

日期：2026-10-19（本地）· 执行者：dsh（Coordinator, epoch 8）· 触发：Codex R1 finding F-005（R3 R-008）

---

## 1. 修复内容

`verify_all.py` 原先只打印 managed / derived 目录的**文件数与字节数**，运行摘要却据此宣称 "zero orphan files"。**计数无法支撑该声明**：目录可以在前后文件数相同的情况下、让每一个存活文件都是无引用的 —— 这正是 R-008 所指的问题。

现改为**真实 orphan 扫描**：

- **managed**：逐个文件比对 `artifact_revisions.managed_path` 与 `pages.managed_original_ref` 中实际被指向的路径集合
- **derived**：检出本次验证工作流从未登记的文件
- 两者都必须为空；非空时**打印具体文件名**（而非只给一个数字）

## 2. 扫描立刻发现了真实文件

首次运行输出：

```
Orphan scan: managed=1 derived=0
  managed orphans: ['trash-manifest.json']
AssertionError: orphan managed files survive permanent delete: ['trash-manifest.json']
```

`trash-manifest.json` 是**回收站自身的记账文件**：随 storage root 创建，且**刻意不被任何 revision 行引用**。它因此被**按名字显式排除**（而非通配符）—— 这样真正的孤儿无法藏在模式后面。

## 3. 修复后运行结果

```
EXIT=0
Orphan scan: managed=0 derived=0
[PASS] Orphan scan: zero unreferenced managed and derived files
```

`verify_all.py` **完整跑通，退出码 0**。

## 4. 关于被覆盖的既有证据文件（重要）

运行 `verify_all.py` 会**重写** `verification/P09-AC3-DELETE-1/evidence/p09_ac3_delete_evidence.json`。

本次运行后 `git diff` 显示该文件**仅一行变化**：

```diff
-  "verified_at": "2026-10-18T06:03:50Z",
+  "verified_at": "2026-10-18T16:19:26Z",
```

`status: "PASS"` 与 `ac_results` **逐字节未变**。

**这一差异本身即是一项结论**：F-005 的改动**没有改变任何既有判定**，`PASS` 保持。

**处置**：按本 Task 约束「**不得为消除失败而改写历史 pin**；只允许**追加**说明」，该文件已**恢复为原提交字节**，本次运行记录改为**追加**写入本 Task 的证据目录（即本文件）。历史 pin 的时间戳没有证据价值，保留其原始字节才有可追溯性。

## 5. 本项覆盖范围（如实声明）

本 suite **不执行 reader preview 路径**，因此其中的 derived 检查是**残留检出器**，而非回收证明。

译图 preview 的**回收证明**由 F-002 承担：
- `tests/core/test_p09_ac4_translated_preview.py` 断言 `producer_root / managed_rel_path` **解析到真实文件**（即 GC 实际执行的检查）
- 生产装配两处 `producer_root` 由 `data_root` 更正为 `core.storage.root`

二者互补，不可互相替代。
