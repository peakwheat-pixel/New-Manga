# R5b 两个 P1 的接线方案（TOCTOU 删除路径）

起草者：dsh（Coordinator, epoch 8）· 2026-10-19 · HEAD：`601688094` · **本文件只做准备：未改产品代码、未申请豁免、未改任何指针**

两个 P1 均已在本机独立复现（探针已入库）：

| 探针 | `outcome` | 返回值 | 外部文件 |
|---|---|---|---|
| `r5b-p1-remove-managed-race-probe.py` | **`NO_EXCEPTION`** | 正常返回 | **被删** |
| `r5b-p1-collect-orphans-race-probe.py` | **`NO_EXCEPTION`** | **`{'orphan_files_removed': 1}`** | **被删** |

---

## 一、为什么修法现成

`src/infrastructure/filesystem/win_unlink.py` 的 `unlink_by_handle(root, segments)` 就是为这类 TOCTOU 写的（N-002 时建好并验证）。它：

- 从**驱动器根**逐段打开句柄（锚点不可被替换）
- 每段校验 `REPARSE_POINT`（**包括根本身**）
- 只对**末段文件**请求 `DELETE`（中间目录请求 DELETE 会 `STATUS_SHARING_VIOLATION`）
- 用 `FILE_OPEN`（不创建缺失组件）
- **`finally` 释放全部句柄**

**唯一的问题是它只被接进了 `unlink_preview_without_following` 一个调用点。**

---

## 二、接线 1：`managed_storage.py:187-188`

**当前**：

```python
        if absolute.is_file():
            absolute.unlink()
```

**改为**：

```python
        # R5b P1: delete through the handle chain, not through the name again.
        # is_file() and unlink() were two resolutions of the same path with room
        # between them to repoint a directory; the probe wins that race and the
        # outside file is deleted with no exception raised.  `segments` is already
        # computed above for the reparse walk, so the chain needs nothing new.
        handled = unlink_by_handle(self._root, segments)
        if handled is not None:
            if not handled:
                raise ImmutablePathViolation(
                    f"refusing to remove {relative_path!r}:"
                    " handle chain refused (missing component, link, or wrong type)"
                )
            return
        # Non-Windows fallback: no handle chain available.
        if absolute.is_file():
            absolute.unlink()
```

**注意三点**：

1. **`segments` 的来源**：该函数已在 L175-176 用它做 reparse walk —— **直接复用，无需重算**
2. **返回值语义**：`unlink_by_handle` 返回 `bool | None`；**`None` 仅表示「该平台无此实现」**，**Windows 上不会出现** → 回退到原路径逻辑（保持既有非 Windows 行为）
3. **拒绝时应抛异常**：该函数的契约是「越界即 `ImmutablePathViolation`」；当前实现对「文件不存在」是静默跳过（`is_file()` 为假即不删）。**接线后需保持这一点** —— 若 `handled is False` 是因为**文件不存在**而非链接，静默跳过可能更符合既有语义。

   **已实测（2026-10-19）**，四种情况的既有行为：

   | 输入 | 结果 |
   |---|---|
   | 文件不存在 | **`NO EXCEPTION`**（静默跳过）|
   | 文件存在 | **`NO EXCEPTION`**（正常删除）|
   | 目录不存在 | **`NO EXCEPTION`**（静默跳过）|
   | 越界（`../outside.png`）| **`ImmutablePathViolation`** |

   **因此接线不能直接 `return unlink_by_handle(...)`** —— 句柄链把「缺失」与「被拒绝」**都报成 `False`**，会丢掉「缺失即静默」这一既有语义。**正确写法**：

   ```python
   if not absolute.is_file():
       return                      # 缺失：既有语义是静默跳过，保持不变
   handled = unlink_by_handle(self._root, segments)
   if handled is None:
       absolute.unlink()           # 非 Windows：无句柄链，回退
   elif not handled:
       raise ImmutablePathViolation(
           f"refusing to remove {relative_path!r}:"
           " handle chain refused (link in the path or wrong object type)"
       )
   ```

   **为什么这个顺序是对的**：`is_file()` 为真**不代表安全**（**它正是竞态里被绕过的那次检查**）—— 它**只用来区分「缺失」与「存在」**；**真正的防护在后面的句柄链**，它不复用 `is_file()` 的结果，而是**重新逐段打开并校验**。

**可选**：接线后 L175-186 的 reparse walk 变成冗余（句柄链逐段做了同样的事）。**建议保留** —— 它提供更早、更明确的错误信息，且删除它属于额外风险。

---

## 三、接线 2：`render_preview.py:181-185`

**当前**：

```python
            for item in sorted(resolved_dir.iterdir()):
                if not item.is_file():
                    continue
                if item.stem not in catalogued:
                    item.unlink(missing_ok=True)
                    removed_files += 1
```

**改为**（对每个 item 走句柄链）：

```python
            for item in sorted(resolved_dir.iterdir()):
                if not item.is_file():
                    continue
                if item.stem not in catalogued:
                    # R5b P1: unlink() resolved the name a third time, after the
                    # containment check and after the enumeration.  The chain works
                    # relative to the configured root and re-verifies each segment,
                    # so a directory repointed mid-enumeration is refused instead of
                    # followed.  Enumeration stays one level deep, so the relative
                    # path is simply <dirname>/<name>.
                    handled = unlink_by_handle(root, [dirname, item.name])
                    if handled is None:
                        item.unlink(missing_ok=True)
                    elif not handled:
                        continue  # refused: do not count it as removed
                    removed_files += 1
```

**注意两点**：

1. **一层枚举**：`iterdir()` 只列 `previews/` 或 `pages/` 的直接子项，所以相对分段就是 `[dirname, item.name]` —— **不需要通用的相对路径计算**
2. **计数语义**：**被拒绝的不能计入 `removed_files`** —— 否则又会返回一个「成功」的统计（**这正是当前 P1 复现里 `orphan_files_removed: 1` 的由来**）

**`root` 的可用性**：`collect_orphans` 里的 `root` 已在早前轮次改为 `abspath(self._root)`（静态基准修复）**且未解析** —— **正好是 `unlink_by_handle` 需要的形态**。

---

## 四、必须交付的验证

1. **两个既有竞态探针转 SAFE**（`r5b-p1-remove-managed-race-probe.py`、`r5b-p1-collect-orphans-race-probe.py`）—— **它们已是现成的回归用例**
2. **既有静态 junction 探针不回归**（5 个）
3. **`tests/storage` 与 `tests/core` 不回归**
4. **`collect_orphans` 的计数语义**：被拒绝的文件不计入 `removed_files`（需专门断言）
5. **`remove_managed` 对「文件不存在」的既有行为不变**（需先读既有测试确认该行为是什么）

---

## 五、范围问题（需裁决）

**R5b 的 P2** 指出 **7 处读取/导出路径**同样「先 resolve 再 containment」：

- `core_service.py:464-467 / 1923-1926 / 2490-2493 / 2533-2542`
- `core_assembly.py:227-230 / 236-239 / 270-273`

**R5b 已复现**：在 `_checked_managed_path()` 前替换配置根的祖先为 junction → **方法接受了外部路径并读出 `outside bytes`**。

**它们不是删除点**（属读取/导出）—— **但同样是 TOCTOU 可绕的**。

**R5b 自己的话**：「**它们是否纳入本 Task 的范围需由 Task 范围裁定。**」

**建议**：**转独立 Task** —— 理由是**读取路径的加固手段与删除不同**（删除可用句柄 disposition；读取需要「按句柄读」或「先校验后句柄打开」），**属于不同的设计问题**，**且本 Task 的范围是「删除加固」**。

---

## 六、边界声明

**只读准备，未实施**：未改 `managed_storage.py` / `render_preview.py`，未创建 Task，未申请豁免，未改任何指针。

**两个探针已在仓库中**（`verification/P09-AC3-DELETE-HARDEN-1/r5b-p1-*-race-probe.py`），**当前均报 `VULNERABLE`** —— 修好后应转为 `SAFE`，无需另写回归用例。
