# R5b 的 P2：读取/导出路径的 resolve-then-compare（7 处）

起草者：dsh（Coordinator, epoch 8）· 2026-10-19 · HEAD：`34fe1069f` · **本文件只做准备：未创建 Task、未申请豁免、未改任何指针、未改产品代码**

---

## 一、问题陈述

R5b 在审计 `relative_to()` 比较时发现，`core_service.py` 与 `core_assembly.py` 中有 **7 处**同样「先 `resolve()` 根与候选、再做 containment」的写法：

| 文件 | 行 |
|---|---|
| `src/bootstrap/core_service.py` | **464–467**、**1923–1926**、**2490–2493**、**2533–2542** |
| `src/bootstrap/core_assembly.py` | **227–230**、**236–239**、**270–273** |
| **`src/infrastructure/resource_channel/handle_resolver.py`** | **`resolve_namespace_identity`（609–617）—— R5b 与 R6 各自复现，见下** |

**R5b 的复现**：

> 「在 `_checked_managed_path()` 调用前，把 configured root 的祖先换成指向外部目录的 junction。该方法**接受了外部路径**，随后**读取出 `outside bytes`**。」

**它们不是删除点** —— 属**读取/导出**路径（`_checked_managed_path()` 及各 `absolute_path` 校验点）。

---

## 二、为什么它与两个 P1 是**不同的问题**

| | 两个 P1（删除） | 这 7 处（读取） |
|---|---|---|
| 危害 | **外部文件被删除** | **外部文件内容被读出** |
| 可用手段 | **句柄 disposition**（`SetFileInformationByHandle`）—— 已有实现 | **按句柄读**，或**先校验后句柄打开** |
| 现有基建 | `win_unlink.unlink_by_handle` **已建好** | **无** —— 需要新的读取路径基建 |
| 修法性质 | **接线**（接到已有链）| **新设计** |

**因此把两者混在一个 Task 里，会让「接线」与「新设计」共享同一条返修预算** —— 这正是本项目已经吃过亏的模式。

---

## 三、修法方向（供新 Task 参考，非结论）

**读取与删除的关键差异**：删除只需**打开一次**即可 disposition；**读取需要打开并持续读**，因此**窗口更长**。

**可选方向**：

| 方向 | 做法 | 代价 |
|---|---|---|
| **① 句柄打开后校验身份** | 打开句柄 → `GetFileInformationByHandle` 取得卷序列号+文件索引 → **与「按配置路径应得的身份」比对** | **需要一个可信的期望身份**（从哪来？）|
| **② 逐段句柄链打开**（同 `unlink_by_handle`） | 复用现有逐段打开逻辑，但**只打开不删除** | **`win_unlink` 的链目前只支持 `DELETE` 末段** —— 需扩展为「只打开」模式 |
| **③ 拒绝不可信路径** | 若**任一祖先段**是 reparse 点则直接拒绝 | **最简单，但会误伤合法使用链接的用户** |

**`handle_resolver.resolve_namespace_identity` 已有方向 ① 的雏形**（打开句柄 + `_final_path_of` + 与名字比对）—— **但 R5b 与 R6 都证明它在竞态下仍会接受被重定向的路径**。

**R5b 的实测**：在**首次 `_lstat_reparse_walk(path)` 之后、`path.resolve()` 时**注入祖先 junction → **函数接受并返回了 `outside\derived`**。

**R6 的独立实测**：`injection_fired=True`、**句柄身份函数接受了 `outside\derived`，外部字节可读** → **VULNERABLE**。

**根因**：**它比对的是「已被重定向后的 `resolved` 名字」** —— **即它拿被污染的值去验证自己**。

**⚠️ 本草案初版把这一项写成「已审计、无需改动」，那是错的** —— 我在更早一轮得出该结论时只验证了**静态场景**（junction 在调用前已存在），**并据此推断该类问题不存在**。**R5b 与 R6 各自独立推翻了这个推断。** 该项**必须纳入本 Task 的修复范围**。

**所以新 Task 需要先回答**：**「期望身份」从哪来？** —— 这是设计问题，不是接线问题。**且答案必须是一个在竞态发生前就已固定、且不随后续路径解析而变化的值**（例如启动时对配置根的句柄身份快照）。

---

## 四、Task 定义草案

```yaml
id: P09-MANAGED-READ-ROOT-TRUST-1
title: 托管文件读取/导出路径的 root 可信性（R5b P2）
kind: security-hardening
status: proposed
suggested_owner: dsh
suggested_reviewer: Codex
depends_on: [P09-AC3-DELETE-HARDEN-1]
```

**范围**：`core_service.py` / `core_assembly.py` 中上述 7 处 **+ `handle_resolver.resolve_namespace_identity`**（R5b 与 R6 均已复现）；对应测试。
**先决问题**：**定义「期望身份」的来源**（句柄身份 vs 配置路径 vs 启动时快照）。
**禁止范围**：不改 IPC 契约、Schema、ACL、依赖；不改删除路径（那是 `P09-AC3-DELETE-HARDEN-1` 的范围）。

**验收方向**：
- AC1：R5b 的复现（祖先 junction → 读出 `outside bytes`）**被拒绝**
- AC2：**合法读取不回归**（含符号链接合法使用的场景 —— 需明确产品是否允许）
- AC3：**全部 8 处**（7 处比较点 + **`handle_resolver.resolve_namespace_identity`**）**逐个**有测试或探针，不接受「模式相同所以一起算」。**resolver 那处是 R5b 与 R6 各自复现过的**（静态场景通过、竞态下接受被重定向路径），**不是「顺带一提」**
- AC4：不引入新的依赖或契约变更

---

## 五、`P09-AC3-DELETE-HARDEN-1` 收口时的声明（若选路线 B/C）

> **本 Task 的删除路径加固覆盖**：
>
> - **静态 junction 基准**：9 处（`managed_storage.remove_managed`、`library.preflight_permanent_delete`、`library.cleanup_book_files` 及其 `books_base`、`render_preview` 三处、`backup.restore_backup`、`tile_cache_sweep.list_cache_files`）—— **5 个探针注入触发且 SAFE**
> - **TOCTOU**：`library` 预览路径（N-002，句柄链）—— **已修**；`managed_storage.remove_managed`、`render_preview.collect_orphans` —— **已复现、方案已备，状态取决于裁决**
>
> **不在本 Task 范围**：
>
> - **7 处读取/导出路径**（R5b P2）→ `P09-MANAGED-READ-ROOT-TRUST-1`
>
> **注意**：R5b 的 P2 复现证明**读取路径也会越过根** —— **但那是「读出」而非「删除」**，**修复手段不同**（需按句柄读或身份校验，属新设计）。**本 Task 不声称覆盖读取路径。**

---

## 六、边界声明

**只读准备，未实施**：未改任何产品代码、未创建 Task、未申请豁免、未改指针。本文件写入 `verification/P20-CLOSE-BOUND-HARDEN-2/`。

**R5b 的原始证据**：`workspace/agent-output/coordinator/codex-r5b-result.md`（findings 第 3 项）。
