# N-002 独立 Task 草案 + 本 Task 已知未闭合项

起草者：dsh（Coordinator, epoch 8）· 2026-10-19 · HEAD：`4c3cd3603` · **本文件只做准备，未创建 Task、未申请豁免**

---

## 一、为什么要为 N-002 立独立 Task

`P09-AC3-DELETE-HARDEN-1` 已用掉 **DIR-4 的两轮返修额度**（R1 后第 1 轮 6 个 finding；R2 后第 2 轮 5 项）。**R2 的 4 项非安全 finding 已全部闭合**（N-001、N-003、F-002、F-007），**唯一剩余的是 N-002 —— 一个 P1 安全缺陷**。

**把 P1 安全项塞进一个已到轮次上限的 Task 里赶工，是最容易出事的地方。** 而 N-002 的价值与风险都足以支撑独立预算：

- **它的失败模式是「删除用户文件」**，不是渲染错误或断言失效
- **正确修法涉及未文档化的 NT API**（见下），需要专门的注入测试
- **它需要一个不被轮次压力挤压的实现与复审周期**

---

## 二、N-002 的完整问题陈述（可直接作为新 Task 的输入）

### 现象

`src/infrastructure/sqlite/library.py` 的 `unlink_preview_without_following`（约 L1247）**逐段校验路径后，仍按路径执行 `unlink()`**：

```python
L1276  probe = root_res
L1277  for segment in segments:
L1278      probe = probe / segment
L1280      probe_stat = probe.lstat()          # 路径解析 #1
L1283      if _is_reparse_point(probe_stat): return False
...
L1285  if probe.is_file():                     # 路径解析 #2
L1286      probe.unlink(missing_ok=True)       # 路径解析 #3，跟随 junction
```

### 复现（Codex R2 的确定性探针）

在父目录校验通过之后、`unlink` 之前，把 `derived/pages` 替换为指向外部目录的 junction：

```text
race_hook_fired=True
unlink_returned=True
outside_page_original_survived=False     ← 外部文件被删除
```

### 为什么现有测试挡不住

现有静态 junction 测试通过，因为它**在调用前就把 junction 放好** —— 那会被逐段 `lstat` 拒绝。**并发替换**（校验后、删除前）不在覆盖范围内。

### 为什么「用句柄删除」的直觉解法不够

`CreateFileW(..., FILE_FLAG_OPEN_REPARSE_POINT)` **只对路径的最后一个组件生效**，**中间目录仍会被跟随**。攻击者替换 `derived/pages` 后，`CreateFileW` 会**穿过 junction** 打开外部文件，而 `FILE_FLAG_OPEN_REPARSE_POINT` 什么也没挡住（末段是普通文件），随后 disposition **删除的就是那个外部文件**。

### 正确修法

**逐段句柄链**：每一步都以「父句柄 + 段名」打开子对象（不再按完整路径解析），校验该对象的 `dwFileAttributes` 是否含 `REPARSE_POINT`，末段校验为普通文件后对**该句柄**执行 disposition 删除。

**在 Windows 上这通常需要 `NtCreateFile` + `OBJECT_ATTRIBUTES.RootDirectory`** 才能做到真正的相对打开 —— 这是本 Task 的主要技术风险所在。

### 必须交付的验证

1. **并发替换注入用例**：在校验后、删除前替换父目录为 junction，**断言外部文件存活**
2. **静态 junction 用例不回归**（既有 3 项）
3. **普通文件仍能正常删除**
4. **句柄不泄漏**（所有路径含异常路径都 `CloseHandle`）

---

## 三、拟立 Task 的定义草案

```yaml
id: P09-AC3-DELETE-RACE-HARDEN-1
title: 预览 unlink 的并发目录替换竞态加固（N-002）
kind: security-hardening
status: proposed          # 待 Codex 释放；本文件不创建它
suggested_owner: dsh
suggested_reviewer: Codex # 必须 owner != reviewer
depends_on: [P09-AC3-DELETE-HARDEN-1]
base_commit: <由 Codex 在释放时填入当前 main>
```

**范围**：仅 `src/infrastructure/sqlite/library.py` 的 `unlink_preview_without_following` 及其新增的 Win32 helper；对应测试。

**禁止范围**：
- 不改 IPC 契约、Schema、ACL、依赖
- 不改 `cleanup_book_files` 的对外语义（只把 `unlink` 换成安全实现）
- 不动 `apps/desktop/frontend/**`

**验收标准草案**：
- AC1：并发替换注入用例通过（外部文件存活）
- AC2：既有静态 junction 3 项测试不回归
- AC3：普通文件删除语义不变（含 `missing_ok` 语义）
- AC4：句柄在成功、拒绝、异常三条路径上均被释放（可注入计数断言）
- AC5：不引入未冻结的 IPC 命令或契约变更
- AC6：报告的 40 位 SHA 过 `git cat-file -e`；`sha256` 按磁盘字节实算

---

## 四、`P09-AC3-DELETE-HARDEN-1` 的已知未闭合项声明（供其收口记录使用）

> **本 Task 在 DIR-4 的两轮返修额度内闭合了 R2 的全部 4 项非安全 finding（N-001、N-003、F-002、F-007）。唯一未闭合项为 N-002 —— 「预览 unlink 的并发目录替换竞态」，P1 安全缺陷。**
>
> **未闭合的直接原因**：其正确修法需要逐段句柄链（Windows 上通常需 `NtCreateFile`）。**在已用尽返修额度的 Task 内引入未文档化的底层 API，其回归风险与被保护的目标（不删错用户文件）不成比例。**
>
> **因此本 Task 不声称 N-002 已解决**，AC5（symlink 替换）的定性为：**静态 junction 已防护；并发替换窗口未关闭**。该未闭合项由 `P09-AC3-DELETE-RACE-HARDEN-1` 承接（待 Codex 释放）。
>
> **本 Task 的其余 12 项 AC 不受 N-002 影响**：N-002 的攻击面是「攻击者能在校验与删除之间替换父目录」，需要本地并发写入能力；它不改变 `P09` 的 AC3 delete 子条件（**仍为 `BLOCKED`**）。

---

## 五、需要谁做什么

| 事项 | 归属 | 说明 |
|---|---|---|
| **释放独立 Task** | **Codex**（Lead/Architect，按 AGENTS.md）| 本文件只给草案 |
| **DIR-4 豁免** | **用户** | 第二轮返修以 4/5 收敛、1 项 P1 安全项转独立 Task，需用户认可这一处置 |
| **或改为路线 1** | 用户决定 | 即在本 Task 内硬做 `NtCreateFile`，承担回归风险 |
| **或改为路线 2** | 用户决定 | 不立新 Task，仅把并发替换窗口记为已知限制 |

**本文件不替你决定** —— 它把三条路线中**我的建议（路线 3）**所需的全部材料准备好，使裁决从「需要设计的开放问题」变成「一个选择」。

---

## 六、边界声明

**只读准备，未实施**：未创建任何 Task 文件、未修改 `P09-AC3-DELETE-HARDEN-1` 的 status 或 AC、未申请 DIR-4 豁免、未改任何指针。本文件写入 `verification/P20-CLOSE-BOUND-HARDEN-2/`（当前 Task 证据目录）。

**另注**：N-002 的探针证据在 `verification/P09-AC3-DELETE-HARDEN-1/codex-review-r2.md` 的 N-002 小节，含 `race_hook_fired` / `unlink_returned` / `outside_page_original_survived` 三项输出，新 Task 可直接引用。
