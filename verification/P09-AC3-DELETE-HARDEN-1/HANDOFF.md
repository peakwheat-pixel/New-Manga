# HANDOFF — P09-AC3-DELETE-HARDEN-1

- `task_id`: P09-AC3-DELETE-HARDEN-1
- `branch`: antigravity/P09-AC3-DELETE-HARDEN-1
- `handoff_head`: 见文末「固定规则」——**收口时由 `git rev-parse` 重取**
- `owner`: dsh
- `reviewer`: Codex（R1–R7 独立复审）
- `status`: `in_review` → **不建议置为 done**（AC4 未通过）
- `date`: 2026-10-19

---

## 一、交付内容

### 1. 新增：句柄链删除原语

`src/infrastructure/filesystem/win_unlink.py`（约 255 行）

`unlink_by_handle(root, segments) -> bool | None`：从**驱动器根**逐段打开句柄、**逐段校验 reparse**、**只对末段文件**请求 `DELETE`、用 `FILE_OPEN`（**不创建缺失组件**）、`finally` 释放全部句柄。非 Windows 返回 `None`（调用方回退）。

**这是本 Task 的核心基建** —— 后续 4 条删除路径都接线到它。

### 2. 静态 junction 基准修复（9 处）

`managed_storage.remove_managed` · `library.preflight_permanent_delete` · `library.cleanup_book_files`（含其 `books_base`）· `render_preview.publish` / `publish_original` / `collect_orphans` · `backup.restore_backup` · `tile_cache_sweep.list_cache_files`

**共同缺陷**：**根与被比较对象都被 `resolve()`** → **根之上的 junction 会让两者一起漂移，containment 检查形同虚设**。
**修法**：**基准改 `os.path.abspath`，候选保持 `resolve()`** —— **containment 因此变成检测器**。

**为什么是 9 处而不是 6 处**：**第一次排查搜的是我预设的写法**；**改为枚举全部 44 个 `.resolve()` 逐个判角色后找到 9 处** —— 多出的 2 处**对前一种搜索在构造上不可见**（一处由子路径构造、一处内联在 `relative_to` 调用里）。

### 3. TOCTOU 删除路径修复（4 条，均接线到句柄链）

| # | 位置 | 提交 | 探针判别力 |
|---|---|---|---|
| 1 | `library` 预览删除（N-002）| （早前轮次）| ✅ |
| 2 | `managed_storage.remove_managed` | `f25d41d50` | ✅ |
| 3 | `render_preview.collect_orphans` | `652d88e65` | ✅ |
| 4 | `render_preview.publish` / `publish_original` 异常清理 | `897e48042` | ✅ |

**判别力由 R7 独立复现**（它在 `%TEMP%` 用旧快照跑，未 checkout、未改仓库）：**三组均为「旧版 VULNERABLE → 当前版 SAFE」**。

**`collect_orphans` 的计数语义随修复改变**：**被拒绝的条目不再计入 `removed_files`** —— **修复前探针拿到 `orphan_files_removed: 1`，修复后为 0**。**那个数字是对该缺陷最清楚的概括。**

**`remove_managed` 保留 `is_file()` 但不是防护**：它**只为保持「缺失静默、越界抛异常」的既有差异**（**实测确认**：missing → `NO_EXCEPTION`，escape → `ImmutablePathViolation`），**句柄链把两者都报成 `False`，无法表达该差异**。**真正的防护在链**，**它不复用 `is_file()` 的结果**。

---

## 二、探针清单（8 个，全部在库）

| 探针 | 覆盖 | 结果 |
|---|---|---|
| `n002-race-probe.py` | N-002 旧实现 | **INCONCLUSIVE**（hook `Path.is_file`，当前实现不调用它）|
| `n002-race-probe2.py` | N-002 子路径竞态 | SAFE |
| `n004-ancestor-probe.py` | 祖先 junction | SAFE |
| `n004-production-order-probe.py` | 生产顺序（先建链接再取根）| SAFE |
| `r5-p1-managed-remove-probe.py` | `remove_managed` 静态 | SAFE |
| `r5-p1-cleanup-book-files-probe.py` | `cleanup_book_files` 静态 | SAFE |
| `r5b-p1-remove-managed-race-probe.py` | `remove_managed` 竞态 | SAFE |
| `r5b-p1-collect-orphans-race-probe.py` | `collect_orphans` 竞态 | SAFE |
| `r6-p1a-publish-cleanup-race-probe.py` | 发布异常清理竞态 | SAFE |

**每个探针都分别报告 `injection_fired` 与 `outside_survived`** —— **注入未触发时报 INCONCLUSIVE，绝不读作 SAFE**。

---

## 三、未完成项（**不得在收口中被表述为已解决**）

### AC4：译图预览在永久删除时不被回收 —— **FAIL**

- **根因**：`publish` 生成 `preview-{uuid4}`（`render_preview.py:69`），清理查 `page-original-{page_id}`（`library.py:1124`），**两者永不相等**
- **量化**：**每次译图阅读泄漏 1 个 catalog 行 + 1 个文件**（实测：5 次读取 → 5 行；永久删除后 **R7 独立复现仍有 5 行 + 5 个 PNG**）
- **代码注释自证**：`core_service.py:1968-1976` **已写出该缺陷**（「cleanup only knows the deterministic page-original key」）**但结论写成「can be reclaimed by reference」**
- **两版修复方案均被否**：
  - **第一版**（按 `artifact_id` 反查）—— **被「同一 artifact 累积多行、`retired` 无法区分在用与遗留」否定**（R7 独立确认无字段可判定）
  - **第二版被 R7 指出时序缺陷**：**生产流程先 `execute_permanent_delete_db`（删 `media_artifacts` 行）再 `cleanup_book_files`**，**清理阶段已无映射可查**
- **核心障碍**：**没有任何现有数据能区分「在用行」与「遗留行」** → **属产品级生命周期决策，不是接线或时序修补**

### Handoff / 正式转交 Task

**本次交付即补齐 Handoff**；**转交 Task 文件见第四节**。

### `delivery_head` 的固定规则

**R7 的 P2 #4 指出它落后**。**本 Task 的历史表明「每次提交后手动更新」不可靠**（我曾在修完 P1-A 后连提 3 次未更新）。

**规则**：**收口时执行 `git rev-parse HEAD` 一次性固定**，**并在 Task 内注明「此值为收口时快照」**。**不得在返修过程中反复更新**（否则每次复审都会看到不一致）。

---

## 四、转交

| 项 | 去向 |
|---|---|
| **AC4** | **`P09-PREVIEW-LIFECYCLE-RECLAIM-1`（建议新建）** —— 需先定义「在用行」的判定依据 |
| **R5b P2 的 8 处读取/导出路径** | **`P09-MANAGED-READ-ROOT-TRUST-1`**（草案：`verification/P20-CLOSE-BOUND-HARDEN-2/r5b-p2-read-path-draft.md`，**scope 与 AC3 均已含 `handle_resolver`**）|

---

## 五、硬约束遵守情况

| 约束 | 状态 |
|---|---|
| `P09` AC3 delete 子条件保持 `BLOCKED` | ✅ **R7 已核对，从未翻为 PASS** |
| 未触碰 20 个指定用户文件 | ✅ |
| 无 `git add -A` / `commit -a` / `reset --hard` / `clean` / `push` / `stash` | ✅ |
| 证据 pin 取自磁盘字节，40 位 commit 经 `git cat-file -e` 验证 | ✅ |
| 无伪造 SHA（一次早期失误已用 `git rev-parse` 纠正并加入扫描）| ✅ |
| Codex 未修改仓库文件（每轮前后 `git status` 对比）| ✅ **R1–R7 全部零差异** |
| Reviewer ≠ Owner | ✅ Codex 复审 |
