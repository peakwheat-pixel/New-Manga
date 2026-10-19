# 用户裁决记录（2026-10-19）

**裁决人**：用户（项目 Owner）
**记录人**：dsh（Coordinator，持 `epoch 8` lease）
**触发**：`GOV-DEBT-CLEANUP-2` 的释放门槛（见 `codex-debt-ruling-r2.md` §「释放门槛」）
**性质**：这是用户裁决的**原始记录**，不是 Agent 的推断。四项均为用户从给定选项中明确选定。

---

## 裁决 1：Plan 预算

**问**：`doc/REBASELINE_PLAN.md` 当前 2332 bytes / 35 lines，检查器上限 2500 / 35。Codex 建议提到 7000 bytes / 64 lines。

**裁决**：**批准提高到 7000 bytes / 64 lines。**

**含义**：

- `tools/governance/check.ps1` 中针对 `doc/REBASELINE_PLAN.md` 的两个预算数值（2500 → 7000、35 → 64）获授权修改。
- 只改这两个数值，不放宽其它任何规则。
- 29 个非终态 Task 此后**具备**登记进 DAG 的容量前提；但是否登记仍受裁决 2 约束。

## 裁决 2：29 个非终态 Task

**问**：其中 10 个 Task 文件未入库、28/29 在 STATUS 与 Plan 中零指涉、20 个仍有未勾选 AC。

**裁决**：**全部暂缓 —— 保持原状态与原 AC 不动。**

**含义**：

- 29 个 Task 的 `status` 一律维持现值，不改终态、不改非终态。
- 10 个未入库 Task **不执行 `git add`**，维持 `UNREGISTERED_UNTRUSTED_SNAPSHOT`。
- 本轮**不向 Plan 登记**这些 Task（即便裁决 1 已扩容）。
- 「当前 DAG 未登记非终态 Task」这 29 行错误**继续保留为已知债务**，不通过伪装终态或移入历史快照来消除。

## 裁决 3：未完成 AC

**问**：11 行为 `done` 但仍有未勾选 AC。Codex 裁定 `done` 与未勾选 AC 不兼容。

**裁决**：**全部保留未完成，不改任何 AC。**

**含义**：

- 不勾选、不删除、不转移、不改写任何 AC 原文。
- 不为消除检查器错误而放宽规则。
- 这些 Task 的完成性**承认存疑**，如实保留；不得把未完成写成 PASS。
- 对应错误行继续保留为已知债务。

## 裁决 4：`workspace.json` 快照

**问**：`P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE` pin 了 `C:/Users/49745/.dsh/storages/workspace.json`——会随使用持续变化的 DSH 用户态文件。

**裁决**：**不允许快照，只记元数据原位保留。**

**含义**：

- 不复制、不归档、不迁移该文件；不把它纳入版本化证据。
- 该行改为指向**可复核的元数据记录**（路径、文件存在性、大小、记录时点），而非文件本体 hash。
- 文件本体原位保留，归用户所有。

---

## 这四项裁决共同确定的范围

1. **可做**：Plan 预算扩容（7000/64）；把上述决定记录进对应 Task / 证据；对剩余债务做**只读**标注（`BLOCKED_*` 类事实标注）。
2. **不做**：登记 29 个 Task、改任何 Task 状态、改任何 AC、`git add` 未入库 Task、重钉 pin、删除/移动 worktree、合并 AC3 分支、复制 `workspace.json`。
3. **因此仍然保留的已知债务**：29 行 DAG 未登记、11 行未完成 AC、66 行 SHA 不匹配（其中 78/13/11 三类按 `sha-mismatch-evidence-chain.md` 分别处理）、23 行 P02 AC3 缺失证据、20 行 Resource manifest 不存在、13 行 evidence_dir 未登记文件、7 行缺 Manifest、4 行 disposition 无效、7 行失效引用等。

**明确声明**：本记录不构成任何资源处置、pin 重钉、Task 状态变更或集成的授权。那些仍需 `GOV-DEBT-CLEANUP-2` 释放后按其实 AC 逐项执行。
