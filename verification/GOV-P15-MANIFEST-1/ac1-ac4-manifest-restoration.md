# AC1–AC4 — 重建 P15 缺失的 Resource Manifest

**Task**: GOV-P15-MANIFEST-1 · **基线**: `550636b84` · **授权**: Codex r20 §2.2

## 一、问题

检查器对 `P15` 报：

```
FAIL: Resource manifest 不存在：verification/P15/resource-manifest.json
```

P15 的 `Resource Manifest` 表只有一行，其 `sha256/manifest` 列指向
`verification/P15/resource-manifest.json`——而该文件**在仓库中不存在**。

## 二、r20 的裁定（为什么不能改成 `NOT_APPLICABLE`）

> **P15 的已有 Resource Manifest 行明确记录真实 worktree 为 `PRESERVE_REFERENCED`，
> 且 `resource-manifest.json` 被引用为 closeout 清单。因而资源并非不适用；
> 把引用改为 `NOT_APPLICABLE` 会与既有事实矛盾。**

**这是本 Task 的核心约束**：不能为了消错而改语义。缺失的是**文件**，
不是**事实**——事实（有一个 worktree、状态是 `PRESERVE_REFERENCED`、零删除）都还在。

## 三、AC1：从既有记录能推出什么

**唯一的字段来源是 P15 自己的记录**，不是我发明的：

### 来自 `doc/tasks/P15.md` 的 `Resource Manifest` 表（L104）

| 列 | 值 |
|---|---|
| `resource_type` | `worktree` |
| `source_path` | `G:/CODEX/New Manga.workspace/worktrees/P15` |
| `disposition` | `PRESERVE_REFERENCED` |
| `destination_path` | `G:/CODEX/New Manga.workspace/worktrees/P15` |

### 来自 `Closeout Record`

> `resource_closeout_status`：`complete`（worktree `PRESERVE_REFERENCED`）。
> **删除、迁移、归档数量/字节数：0。**

### 明确**不**推的东西

同类 Task（如 `EXPORT-REVEAL-1`）的 manifest 还有 `junction`、`test-build-output`、
`test-dependencies` 三类条目。

**P15 的记录从未声称这些资源。把它们抄进去就是伪造来源。**

所以本 Task 的 manifest **只有 1 个 resource**。

## 四、AC2：worktree 的实际状态（核实，不假设）

r20 的 AC2 要求：「若原 worktree 已不存在，如实记录为「原 worktree 已清理」，
**不得伪造路径存在性**。」

实测：

```
$ git worktree list | Select-String "worktrees/P15"
G:/CODEX/New Manga.workspace/worktrees/P15    ee19898fc [zcode/P15]
```

| 项 | 值 |
|---|---|
| 路径存在 | **是** |
| HEAD | **`ee19898fc`** |
| 分支 | `zcode/P15` |
| **与 Closeout 的 `delivery_head` 一致** | **是**（Closeout 记 `ee19898fc`） |

**这个一致性是重要的旁证**：worktree 停在交付时的 HEAD 上，说明它确实被
`PRESERVE_REFERENCED` 保留着，没有被后续操作移动。

## 五、AC3：重建的 manifest 内容

写入 `verification/P15/resource-manifest.json`（格式对齐同类 Task）：

```json
{
  "task_id": "P15",
  "recorded_at": "2026-10-20",
  "restored_by": "GOV-P15-MANIFEST-1",
  "restoration_basis": [ 三条来源 ],
  "resources": [ 1 条 worktree，含 verification 子对象 ],
  "closeout_counts": { "deleted": 0, "moved": 0, "archived": 0 },
  "closeout_status": "complete",
  "notes": [ 四条说明 ]
}
```

### 三个设计选择

1. **加了 `restored_by` 与 `restoration_basis`**：这是重建的文件，不是原件的复制。
   **必须让后人知道它是恢复的，以及依据是什么。** 冒充原件是不可接受的。

2. **`verification` 子对象记录实际核实结果**：`exists`、`checked_at`、`head`、
   `head_matches_closeout_delivery_head`、`branch`。
   这样「我核实过」是可复核的事实，不是一句声明。

3. **`notes` 里明确写了「缺什么」**：
   > Absent from this file by design: junction, test-build-output and
   > test-dependencies entries. Sibling task EXPORT-REVEAL-1 has those,
   > but P15's records never claim them, and inventing them would fabricate provenance.

## 六、效果

| 阶段 | 错误 |
|---|---|
| 改动前 | `Resource manifest 不存在` + pin 失配 |
| 写入 manifest 后 | **`Resource manifest 不存在` 消失**，但新增 `evidence_dir 含未登记文件：resource-manifest.json` |
| 登记 `E10` 后 | 只剩 **`SettingsPage.test.tsx` pin 失配**（既有，属 `GOV-PIN-LINEAGE-1`） |

**第二个中间状态值得记录**：修好一个错误会**暴露下一个**——新建的文件本身成了
「未登记文件」。这不是回归，是检查器逐层收紧。

## 七、AC1–AC4 状态

| AC | 结果 | 证据 |
|---|---|---|
| AC1 核实被引用内容 | 达成 | 本文 §三 |
| AC2 核实 worktree 实际状态 | 达成 | 本文 §四（HEAD `ee19898fc` 实测） |
| AC3 重建 manifest | 达成 | `verification/P15/resource-manifest.json` |
| AC4 交付与 Review | 待 | AC5 |

AC5（Handoff + Review）待后续轮次。

## 八、一个声明

**这份 manifest 是恢复的，不是原件。** 它的内容来自 P15 自己的记录与实测事实，
但它不是当初 closeout 时写的那一份——原件从未入库，因此无从比对。

**我没有假装它是原件**：文件里 `restored_by` 与 `restoration_basis` 两字段
明确标注了它的来历。
