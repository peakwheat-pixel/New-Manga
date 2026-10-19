# R5 的 P1：`remove_managed()` 的祖先 junction 重定向

起草者：dsh（Coordinator, epoch 8）· 2026-10-19 · HEAD：`ff19ec6a5` · **本文件只做准备：未创建 Task、未申请豁免、未改任何指针、未修产品代码**

---

## 一、问题陈述（可直接作为新 Task 输入）

`src/infrastructure/filesystem/managed_storage.py` 的 `remove_managed()`（L125）是**托管文件的永久删除路径**。它有两道防线，**各自都是对的，但因为一道用「解析后」路径、一道用「未解析」路径，它们保护的其实是两个不同的位置**：

```python
L147  absolute = Path(self.absolute_path(relative_path)).resolve()   # 解析：跟随 junction
L148  root     = self._root.resolve()                                # 解析：跟随 junction
L150  absolute.relative_to(root)                                     # 防线一：containment
L167  probe = self._root                                             # 未解析！
L168-173  逐段 probe.lstat()                                          # 防线二：reparse walk
```

**失败链条**：

1. `_root` 的**祖先**是 junction（例如 `trusted` → 外部目录）
2. `root = self._root.resolve()` → **基准漂到外部**（`.../outside/derived`）
3. `absolute` 同样 resolve → **也落在外部** → **`relative_to` 通过**
4. reparse walk 从**未解析**的 `self._root` 出发 —— **junction 在祖先上，不在被检查的段上** → **`lstat` 看不到 reparse** → 通过
5. `unlink()` 跟随祖先 junction → **删除外部文件**

**docstring（L139-145）记录的原始设计意图是正确的**：「根内 junction 会解析回根内，所以 containment 单独不够，必须加 reparse walk」。**缺陷不在设计，而在于根本身被 `resolve()` 了，于是 containment 的基准跟着一起漂移。**

---

## 二、复现（已实测，非分析）

探针：`workspace/agent-output/coordinator/p1-repro.py`（隔离夹具建于 workspace，未改仓库任何文件）

```
managed_root     = ...\coordinator\p1-repro\trusted\derived
inside file exists = True
injection        = ancestor 'trusted' is now a junction to 'outside'
resolve(root)    = ...\coordinator\p1-repro\outside\derived     ← 基准已漂到外部
remove_managed   = NOT_RAISED                                    ← 未抛 ImmutablePathViolation
outside_survived = False                                         ← 外部文件被删除
RESULT           = VULNERABLE
```

`NOT_RAISED` 是关键：**调用方不会收到任何异常** —— 删除成功返回，外部文件消失。

---

## 三、修法（一行）

```python
# managed_storage.py:148  当前
root = self._root.resolve()

# 改为
root = Path(os.path.abspath(str(self._root)))
```

**为什么这一行就够**：`_root` 保持**未解析**后，`absolute`（仍 `resolve()`）一旦越过 junction 就落到外部 → **`relative_to(root)` 抛 `ValueError`** → **正确转为 `ImmutablePathViolation`**。**两道防线重新指向同一个位置。**

**注意**：`absolute` 应**保留** `resolve()` —— 它正是检测手段（解析后越界即拒绝）。

---

## 四、必须交付的验证

1. **祖先 junction 注入用例**：断言抛 `ImmutablePathViolation` 且**外部文件存活**（当前探针的直接产物）
2. **既有 managed_storage 测试不回归**（需先确认测试文件位置与数量）
3. **根内 junction 仍被拒绝**（docstring 描述的原始场景 —— 不得因本次修改而回退）
4. **正常删除语义不变**（普通托管文件仍能删除）
5. **`self._root` 为相对路径时行为不变**（`abspath` 相对 CWD；需确认 `absolute_path()` 是否已保证绝对）

---

## 五、Task 定义草案

```yaml
id: P09-MANAGED-REMOVE-ROOT-TRUST-1
title: remove_managed 的祖先 junction 重定向加固（R5 P1）
kind: security-hardening
status: proposed          # 待 Codex 释放
suggested_owner: dsh
suggested_reviewer: Codex
depends_on: [P09-AC3-DELETE-HARDEN-1]
```

**范围**：`src/infrastructure/filesystem/managed_storage.py` 的 `remove_managed`（含 `_root` 解析基准）；对应测试。
**禁止范围**：不改 IPC 契约、Schema、ACL、依赖；不改 `remove_managed` 的对外语义（仍为「越界即抛 `ImmutablePathViolation`」）；不动前端。

---

## 六、与 N-004 的关系（重要）

**同病根**：

| | N-004 | R5 P1 |
|---|---|---|
| 位置 | `library.py` 预览清理 | `managed_storage.py` **托管文件删除** |
| 病根 | `Path.resolve()` 跟随 junction，使防护基准漂移 | **同一病根** |
| 修法 | `os.path.abspath` | **同一修法** |
| 状态 | ✅ 已修（`842792a56`）| 🔴 **未修，已复现** |

**N-004 的修复只覆盖了它自己的调用点** —— 我修完 `library.py` 后**没有排查其他 `resolve()` 调用点**，**R5 排查了并找到了这一处**。

**因此建议**：本 Task 应**同时排查全仓其他「以 resolve() 结果为防护基准」的删除路径**，而不只修这一行 —— 否则同一病根可能还有第三处。

**建议的排查方式**：搜索 `resolve()` 与 `unlink`/`remove`/`rmtree` 同现的函数，逐个判断其基准是否被解析。

### 六之二、同类排查结果（2026-10-19 实查，只读）

按上述方式搜索「同时含 `resolve()` 与 `unlink`/`remove`/`rmtree`」的文件，再逐处判断其 `resolve()` 是否**用作防护基准**。**结果：同一写法共 6 处，另有 1 处待判**。

| # | 文件 | 函数 | 位置 | 写法 | 后果面 |
|---|---|---|---|---|---|
| 1 | `managed_storage.py` | `remove_managed` | L147-150 | `root = self._root.resolve()` + `absolute.relative_to(root)` | **P1，已复现** |
| 2 | **`library.py`** | **`preflight_permanent_delete`** | **L819-820** | `abs_p = …resolve()` + `root = storage.root.resolve()` | ⚠️ **永久删除的预检门** |
| 3 | **`library.py`** | **`cleanup_book_files`** | **L1148-1151** | `root = storage.root.resolve()` + `books_base = (root/"books").resolve()` | ⚠️ **永久删除** |
| 4 | `render_preview.py` | `publish` | L57-61 | `root = self._root.resolve()` + `is_relative_to(root)` | 预览发布 |
| 5 | `render_preview.py` | `publish_original` | L99-103 | 同上 | 原图发布 |
| 6 | `render_preview.py` | `collect_orphans` | L155-176 | `root = self._root.resolve()`；**且 L176 用解析后的 `candidate`** | 孤儿回收 |
| 7 | `backup.py` | `restore_backup` | L149-150 | `target = …resolve()` + `target.parent != self._backup_root.resolve()` | **恢复备份的落点** |

**判断依据**：凡「先 `resolve()` 出一个根，再用它做 `relative_to` / `is_relative_to` / `parent ==` 比较」的，都是同一病根 —— **基准本身会跟随 junction 漂移**。

**两处特别值得注意**：

- **#2 `preflight_permanent_delete`**：函数名说明它是**删除前把关的那道门**。**若它的基准会漂移，这道门就形同虚设** —— 而它守卫的是永久删除。
- **#7 `restore_backup`**：比较的是**落点父目录**。**恢复备份时把数据库写到错误位置**，后果与误删同级。

**#3 `cleanup_book_files`** 是**本 Task 已接触过的函数**（`library.py:1125` 的预览清理在其内部）—— **但我修的是它里面 `root_res` 那一处，没有看它自己的 `root = storage.root.resolve()`**。**同一函数内、相隔 20 行，一处已修一处未修**，这本身就说明「只修报告点」的做法不可靠。

**结论**：这是**一类系统性缺陷**（至少 6 处），**不是一行的问题**。因此建议新 Task 的范围定为「整类修复 + 每处加注入回归用例」，而不是只修 P1 报告点。

---

## 七、`P09-AC3-DELETE-HARDEN-1` 的收口声明（若选路线 C）

> **本 Task 在用户提升后的 6 轮返修额度内闭合了 R1/R2/R3/R4 的全部 finding，唯 R5 的 P1 转出。**
>
> - **P1（`remove_managed()` 祖先 junction 重定向，P1 安全，已复现）** → `P09-MANAGED-REMOVE-ROOT-TRUST-1`
>
> **本 Task 不声称 P1 已解决。** AC5 的定性为：**预览清理路径的静态 junction、子路径替换、祖先替换均已防护（三个探针实测）；托管文件删除路径的祖先替换未防护（P1，已复现）。**
>
> **R5 的判定缺口**：因该轮任务描述同时要求「READ ONLY」与「实际运行探针/测试」，R5 选择了保守解释，**未运行探针与测试套件**，故其 AC1–AC10、AC12 为 `NOT_VERIFIED`（**非失败**），AC11 为 `PASS`（15 个 40 位 SHA 可解析、11 个 pin 与磁盘一致、AC3 仍 `BLOCKED`）。**这是任务描述的缺陷，不是 R5 的失误**；下一轮任务须写明「可在隔离目录内创建夹具，仅不得改动仓库文件」。
>
> **本 Task 的其余 AC 不受影响**，`P09` 的 AC3 delete 子条件**仍为 `BLOCKED`**。

---

## 八、边界声明

**只读准备，未实施**：未创建 Task 文件、未改 `P09-AC3-DELETE-HARDEN-1` 的 status/AC、未申请豁免、未改任何指针、**未修改 `managed_storage.py`**。

**探针位置**：`workspace/agent-output/coordinator/p1-repro.py`（夹具已清理，无残留）。
