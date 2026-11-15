---
task_id: AC-CHECKBOX-AUTHORITY-1
owner: DSH
status: in_progress
created: 2026-11-15
scope: 全项目 AC 勾选一致性清理（用户 2026-11-15 指示：AC 勾选要成为权威信号）
---

# AC 勾选成为权威信号：清理规范与执行

**用户指示（2026-11-15）**：「希望 AC 勾选成为权威信号，需一次全项目一致性清理」。

## 1. 精确范围（已实测）

```powershell
# 遍历 doc/tasks/*.md：status ∈ {done, closed_with_limitations} 且 "- [ ]" 数>0 且 "- [x]" 数=0
```

| 项 | 数 |
|---|---|
| **需要清理的卡** | **40 张** |
| **AC 总数** | **260 条** |
| 其中 `evidence_dir` 存在 | 31 张 / 208 条 |
| 其中 `evidence_dir` **不存在** | **1 张 / 5 条**（`V11R-C-RESEARCH-1`） |
| 其中**无** `evidence_dir` 字段 | 8 张 / 47 条 |

**全部 40 张**（按 AC 数降序）：`V11R-C-2`(12)、`CHAPTER-MANUAL-SORT`(10)、`V11R-D-1`(10)、`UI-DESIGN-1`(9)、`FEA-04`(8)、`V11R-C-1`(7)、`V11R-B-5`(7)、`V11R-B-4`(7)、`V11R-B-3`(7)、`V11R-B-2`(7)、`V11R-B-1`(7)、`V11R-A-2`(7)、`P20-AC4-FPS-1`(7)、`P02`(7)、`V11R-F0-1`(7)、`GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1`(7)、`GATE3-COVERAGE-MATRIX`(6)、`GOV-PIN-LINEAGE-1`(6)、`GOV-RESIDUAL-RUNTIME-IDENTITY-1`(6)、`V11R-A-3`(6)、`V11R-A-1`(6)、`V11R-C-3`(6)、`FEAT-CREATE-2`(6)、`M2-REGION-RETYPE-CORE`(6)、`TASK-053`(6)、`RUN-IPC-1`(6)、`RELEASE-PACKAGE-1`(6)、`M2-SFX-CORRECTION-EXPORTER`(6)、`M2-SFX-DATA-INFRA`(6)、`P15-C1`(6)、`TASK-056`(6)、`EXPORT-IPC-1`(6)、`DIAG-M2-REGIONLESS-LOCK-CHANGED-001`(5)、`V11R-C-RESEARCH-1`(5)、`M2-SFX-MISROUTE-UI-MITIGATION`(5)、`MICA-FIX-1`(5)、`P19`(5)、`FEA-07-AC5-NATIVE-1`(5)、`V1-RELEASE-SIGNING-1`(4)、`P20-MEM-OPT-1`(4)

## 2. ★ 核心原则：**不得凭空打勾**

要 AC 勾选成为**权威信号**，前提是**每个勾都有可审计的依据**。

**⇒ 因此定义三种勾选标注，禁止裸 `[x]`**：

| 标注 | 含义 | 谁可以打 |
|---|---|---|
| `- [x]` + **行内 `<!-- verified: <方式> @ <commit> -->`** | **已自动核实** | 任何人，只要有可复现的核实命令 |
| `- [ ]` + **行内 `<!-- blocked: <原因> -->`** | **未满足/不可自动验证** | 任何人 |
| **完全不改动** | 该卡不在本次范围 | — |

**`<方式>` 允许的取值（必须可复现）**：
- `grep:<pattern>@<path>:<line>` —— 代码/配置存在性
- `test:<test-id>` —— 有对应测试且全量通过
- `file:<path>` —— 有实物产物（含 sha256 更佳）
- `gate:check|pins|inventory` —— 四件套之一通过
- `human:<who>@<date>` —— **必须是人做的判断**（Agent 不得冒充）

## 3. 分批策略（按可自动验证程度）

| 批次 | 范围 | 预期 |
|---|---|---|
| **B1 试点** | `CHAPTER-MANUAL-SORT`（10 条，我已逐项核实过 6 项） | **本轮完成** |
| **B2 高置信** | `evidence_dir` 存在 + AC 文本里写了可 grep 的符号（文件/命令/测试名） | 每轮 3–5 张 |
| **B3 需找证据** | 8 张无 `evidence_dir` | 先定位证据，再进 B2 |
| **B4 真问题** | `V11R-C-RESEARCH-1`（`evidence_dir` 不存在） | **单独处理：查明是目录名错还是证据丢了** |
| **B5 需人判断** | AC 文本涉及"手感/视觉/体验" | **标 `blocked: 需人工判断`，不冒充** |

## 4. 本轮（B1 试点）要做的

对 `CHAPTER-MANUAL-SORT` 的 10 条 AC：

- **已有证据的**（AC1/AC2/AC4/AC5/AC6 等）：打 `[x]` + `<!-- verified: ... -->`
- **无法自动验证的**（如 AC8"失败与刷新不假装成功"、AC9"并发保护"需要行为断言）：**标 `[ ]` + `<!-- blocked: ... -->`**
- **不修改其他 39 张卡**（本轮只试点）

## 5. 验收（本卡完成条件）

- [ ] **B1 试点完成**：`CHAPTER-MANUAL-SORT` 的 10 条 AC 全部有标注（`verified:` 或 `blocked:`），**无裸 `[x]`**
- [ ] **B2/B3/B4/B5 有明确清单**（哪张卡进哪批，依据是什么）
- [ ] **新增一条治理规则**：写入 `doc/09_COLLABORATION.md`（或等价位置）—— **"`[x]` 必须带 `verified:` 注释；`evidence_dir` 与 AC 勾选不一致时以 AC 注释为准"**
- [ ] **门禁通过**：`check.ps1` / `pins` / `inventory`；**不改任何 pin 与契约字节**

## 6. 已知风险

| 风险 | 缓解 |
|---|---|
| **批量改 40 张卡会污染历史** | 分批；每批单独 commit；**不改 AC 文本本身，只在行尾加注释** |
| **"自动验证"可能验证错东西** | 每条 `verified:` 必须写明具体命令/路径，可复现 |
| **我可能又误判**（本会话已 16 次） | 每条 `verified:` 都由我**实际执行**过一次；无法执行的标 `blocked:` |
| **改别人的卡 = 越权？** | 用户已明确指示做全项目清理；但**只改 AC 勾选与注释，不改结论/status** |
