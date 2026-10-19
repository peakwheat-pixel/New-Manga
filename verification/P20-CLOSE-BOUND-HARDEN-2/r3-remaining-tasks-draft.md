# R3 剩余两项的独立 Task 草案

起草者：dsh（Coordinator, epoch 8）· 2026-10-19 · HEAD：`2e336a28c` · **本文件只做准备：未创建 Task、未申请豁免、未改任何指针**

`P09-AC3-DELETE-HARDEN-1` 在 DIR-4 的两轮返修额度内已闭合 R3 六项 finding 中的四项（N-001、N-003、N-005、F-007，另 R1/R2 的 finding 亦全部闭合）。**剩余两项都不是确定性修复**：一项需要设计选择，一项需要改生产行为。

---

## 一、N-004（P1）：根路径的祖先可信性

### 问题陈述（可直接作为新 Task 输入）

`src/infrastructure/filesystem/win_unlink.py` 的 `_open_root` 用

```python
_kernel32.CreateFileW(str(root), ..., _FILE_FLAG_BACKUP_SEMANTICS | _FILE_FLAG_OPEN_REPARSE_POINT, None)
```

打开**完整根路径**。该标志**只对路径的最后一段生效**，**不能阻止祖先段被重新解析**；根句柄也**未做属性校验**。

**因此**：句柄链保护了 `root` 之下的每一段，**却假设 `root` 本身不可变** —— 而这个假设不成立。

### 复现（Codex R3，可复算）

先解析 `trusted/derived`，在 `_open_root` 之前把 **`trusted` 替换为指向外部目录的 junction**：

```
root_swap_injection_fired  = True
unlink_returned            = True
outside_survived           = False     ← 根外文件被删除
original_inside_survived   = True      ← 根内的"原始"目标反而未被触碰
```

### 修法（两个方案，需在新 Task 中定夺）

| 方案 | 做法 | 代价 |
|---|---|---|
| **① 根的祖先也逐段走句柄** | 从某个可信锚点（如卷根 `\\.\C:`）开始，逐段相对打开直到 `root`，每段校验非 reparse | 需定义"可信锚点"；路径分段需处理 UNC 与长路径前缀 |
| **② 以卷句柄为锚** | `CreateFileW("\\\\.\\C:", ...)` 取得卷句柄，之后全部相对打开 | 需要管理员权限？需实测；对 UNC 路径不适用 |

**方案 ① 更通用**；**方案 ② 更简单但适用范围受限**。**这个选择应在新 Task 中由 Codex 定范围。**

### 必须交付的验证

1. **祖先替换注入用例**：在 `_open_root` 前替换根的父目录为 junction，**断言外部文件存活**
2. **现有两个探针不回归**（`n002-race-probe.py` 对旧实现、`n002-race-probe2.py` 对新实现）
3. **`tests/storage` 全套不回归**（当前 86 passed）
4. **句柄在所有路径（含异常）上释放**
5. **`FILE_OPEN` 语义保持**（N-005 已修，不得回退为 `OPEN_IF`）

### Task 定义草案

```yaml
id: P09-AC3-DELETE-ROOT-TRUST-1
title: 预览 unlink 的根路径祖先可信性（N-004）
kind: security-hardening
status: proposed          # 待 Codex 释放
suggested_owner: dsh
suggested_reviewer: Codex
depends_on: [P09-AC3-DELETE-HARDEN-1]
```

**范围**：`src/infrastructure/filesystem/win_unlink.py` 的 `_open_root` 及其辅助；对应测试。
**禁止范围**：不改 IPC 契约、Schema、ACL、依赖；不改 `cleanup_book_files` 对外语义；不动 `apps/desktop/frontend/**`。

---

## 二、F-002：真实 reader 发布是否会退休 preview

### 问题陈述

R2 后我补的测试**直接调用** `catalog.mark_preview_retired(key)`，然后断言候选列表包含该 preview。**它验证了「退休之后 GC 能看见它」，但没有证明「真实 reader 发布会退休 preview」。**

Codex R3 查明：**生产标记仅在请求带 `retire_preview=true` 时发生**（`src/infrastructure/resource_channel/host_bridge.py:136`），而**现有 Tauri 调用是 rerender 轮换旧 key**（`apps/desktop/src-tauri/src/main.rs:1083` 附近）。

**因此仍有一个未回答的问题**：**译图 preview 在真实阅读流程中能否被退休**？若不能，AC4 所声称的「可被引用回收」在生产上仍不成立 —— **泄漏仍在**，只是测试看起来通过了。

### 需要先做（诊断，不是实现）

1. **定位**：谁在真实阅读路径上调用 `retire_preview=true`？如果没有人，说明轮换策略（rerender 换 key）取代了退休策略
2. **判定**：轮换旧 key 后，**旧的 `preview_lifecycle` 行**是否仍为 `retired=0`？若是，**它们永不被 GC 回收** → AC4 的修复在生产上不完整
3. **定策**：或让轮换时退休旧 key，或明确「轮换即取代退休」并修正 AC4 的表述

### Task 定义草案

```yaml
id: P09-AC4-PREVIEW-RETIRE-WIRING-1
title: 译图 preview 的生产退休接线（F-002 续）
kind: feature
status: proposed
suggested_owner: dsh
suggested_reviewer: Codex
depends_on: [P09-AC3-DELETE-HARDEN-1]
```

**注意**：若第 2 步确认「轮换后旧行永不被回收」，则这是**产品行为缺陷**（每页每次译图阅读泄漏一个 artifact），**优先级应高于 N-004**。

---

## 三、`P09-AC3-DELETE-HARDEN-1` 的收口声明（供路线 B 使用）

> **本 Task 在 DIR-4 两轮返修额度内闭合了 R1、R2、R3 的全部 finding，唯 N-004 与 F-002 两项转出。**
>
> - N-004（根路径祖先可信性，P1 安全）→ `P09-AC3-DELETE-ROOT-TRUST-1`
> - F-002 的剩余部分（生产退休接线）→ `P09-AC4-PREVIEW-RETIRE-WIRING-1`
>
> **本 Task 不声称这两项已解决。** AC5 的定性为：**静态 junction 已防护；子路径并发替换已防护（句柄链）；根路径祖先替换未防护（N-004）**。AC4 的定性为：**GC 侧候选路径已验证；生产发布是否退休未验证（F-002）**。
>
> **本 Task 的其余 AC 不受影响**，`P09` 的 AC3 delete 子条件**仍为 `BLOCKED`**。
>
> **已修复并被 R3 确认的部分**：N-001（契约版本与 wire 错误码对齐）、N-003（11 个 pin 与磁盘一致）、N-005（缺失组件拒绝而非创建）、F-007（分类表述三处收窄）；R1 的 F-003/F-004/F-005/F-006 与 R2 的 F-002 测试接线亦已闭合。

---

## 四、需要谁做什么

| 事项 | 归属 |
|---|---|
| **释放两个新 Task** | **Codex**（Lead/Architect）|
| **DIR-4 豁免** | **用户** —— 本 Task 以 4/6 收敛、2 项转独立 Task |
| **或选路线 A** | 用户 —— 授权在本 Task 内继续（需突破轮次上限）|

## 五、边界

**只读准备，未实施**：未创建 Task 文件、未改 `P09-AC3-DELETE-HARDEN-1` 的 status 或 AC、未申请豁免、未改任何指针。本文件写入 `verification/P20-CLOSE-BOUND-HARDEN-2/`（当前 Task 证据目录）。

**证据来源**：N-004 与 F-002 的复现与判定均在 `verification/P09-AC3-DELETE-HARDEN-1/codex-review-r3.md`（Codex session `01a15198-e1cf-73a1-81ae-50637f2f8f64`），含可复算的命令与输出。
