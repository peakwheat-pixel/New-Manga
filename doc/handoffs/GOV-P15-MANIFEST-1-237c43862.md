---
task_id: GOV-P15-MANIFEST-1
author: dsh
recipient: Codex
base_commit: 550636b84
delivery_head: 237c43862be57ce8d84b2932abe2c30b279e6c7c
status: ready_for_review
---

# Handoff：GOV-P15-MANIFEST-1

## 一句话

P15 的 `Resource Manifest` 行引用了一个**不存在的文件**。已从 P15 自己的记录重建，
**没有增加一个它没声称过的资源**。

## 为什么不能改成 `NOT_APPLICABLE`（r20 的裁定）

> P15 的已有 Resource Manifest 行明确记录真实 worktree 为 `PRESERVE_REFERENCED`，
> 且 `resource-manifest.json` 被引用为 closeout 清单。**因而资源并非不适用**；
> 把引用改为 `NOT_APPLICABLE` 会与既有事实矛盾。

**缺失的是文件，不是事实。**

## 三个关键判断

### 1. 只写 P15 声称过的资源

同类 Task（`EXPORT-REVEAL-1`）的 manifest 有 4 类：`worktree`、`junction`、
`test-build-output`、`test-dependencies`。

**P15 的 manifest 只有 1 类：`worktree`。**

因为 P15 的记录**从未声称**那三类。抄进来更快、更"完整"、也更可能通过检查器，
**但那是伪造来源**。

文件里明确写了：

> Absent from this file by design: junction, test-build-output and test-dependencies
> entries. Sibling task EXPORT-REVEAL-1 has those, but P15's records never claim them,
> and inventing them would fabricate provenance.

### 2. 核实 worktree，不假设

| 项 | 值 |
|---|---|
| worktree 存在 | **是** |
| HEAD | **`ee19898fc`** |
| 分支 | `zcode/P15` |
| **与 Closeout 的 `delivery_head` 一致** | **是** |

这个一致是旁证：worktree 停在交付时的 HEAD 上，说明它确实被保留着。

结果写进了 manifest 的 `verification` 子对象（`exists` / `checked_at` / `head` /
`head_matches_closeout_delivery_head` / `branch`），使「我核实过」成为可复核的事实。

### 3. 不假装它是原件

**原件从未入库，无从比对。** 所以文件里写了：

```json
"restored_by": "GOV-P15-MANIFEST-1",
"restoration_basis": [ 三条来源 ]
```

**没人应该去猜一份重建的文件是不是真的。**

## 效果

| 阶段 | P15 的错误 |
|---|---|
| 改动前 | `Resource manifest 不存在` + pin 失配 = **2** |
| 写入 manifest 后 | 消失，但新增 `evidence_dir 含未登记文件：resource-manifest.json` |
| 登记 `E10` 后 | 只剩 **pin 失配 = 1**（既有，属 `GOV-PIN-LINEAGE-1`） |

**中间那一步值得注意**：修好一个错误会**暴露下一个**——新建文件本身成了「未登记文件」。
这不是回归，是检查器逐层收紧。

## 请 Review 重点核对的三处

### 1. 重建的每一个字段是否都能在既有记录中找到依据（核心）

Task 的 AC1 要求「**不得凭空发明字段**——只恢复能从既有记录推出的内容」。

请核对 `verification/P15/resource-manifest.json` 的每个字段：

- `task_id` / `resources[0]` 的四列（`resource_type` / `source_path` / `disposition` /
  `destination_path`）应能在 `doc/tasks/P15.md` 的 L104 附近找到；
- 必填项之外，`recorded_at`、`restored_by`、`restoration_basis`、`verification`、
  `notes` 都是**我加的说明性字段**，不是恢复的原始内容。

**请判断：这些说明性字段本身是否恰当？会不会反而让文件偏离了「清单」的用途？**

### 2. 「不抄同类 Task 的字段」是否是正确的判断

我判断 `junction` / `test-build-output` / `test-dependencies` 三类**不该写**，
因为 P15 的记录没声称过。

但另一种看法是：**如果 P15 实际产生过这些资源（它确实跑过前端构建与 Rust 测试），
那它们大概存在，补上更完整。**

**请判断：我坚持「只写声称过的」是否过于保守？**
如果 P15 的 worktree 里确实有 `node_modules`、`dist` 或 sidecar junction，
是否应该核实后补上？

（**注意**：如果应该补，那本 Task 就还没做完——请直接说。）

### 3. 检查器剩下的那 1 个错误是否真的与本 Task 无关

`P15` 现在只剩：

```
FAIL: Evidence SHA-256 不匹配：apps/desktop/frontend/src/settings/SettingsPage.test.tsx
```

请确认这条是**时间性失配**（后续提交 `528c6289c` 改过该文件），
而不是本 Task 引入的。

## 明确未做

- 未把任何资源改成 `NOT_APPLICABLE`。
- 未修改 `doc/tasks/P15.md` 的任何既有字段（`status`、AC、Closeout Record、
  Resource Manifest 表都没动）——只新增了一行 `E10` 证据登记。
- 未伪造 worktree 路径存在性。
- 未修那条 pin 失配（属 `GOV-PIN-LINEAGE-1`）。
- 未动其它 Task 的 manifest。

## 已声明的局限

1. **这是恢复的文件，不是原件**。内容来自 P15 的记录与实测，但原件从未入库，
   因此**无法与原件比对**。
2. **我没有核实 P15 worktree 内部的实际内容**（例如是否存在 `node_modules`）。
   如果 AC2 的意图包含「把实际存在的资源都登记」，那本 Task 的范围就不够。
   见上文第 2 点，请你判断。
3. `recorded_at` 写的是恢复日期（2026-10-20），不是原始 closeout 日期。

## 接收方式

Reviewer：**Antigravity**（不得由 dsh 自审），针对固定 `delivery_head = 237c43862be57ce8d84b2932abe2c30b279e6c7c`。
