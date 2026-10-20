# 审计处置裁定（r188，dsh 代裁）

**产出**：2026-10-20
**程序说明**：本轮原拟交 Codex 裁定（r43），但 Codex CLI 返回
`You've hit your usage limit ... try again at 7:44 PM`，**不可用**。
**按用户 r115 指令「本会话一直按推荐自行裁决」，由 dsh 裁定并记录理由，待 Codex 恢复后复核。**

## 一、处置结果总览

| 项 | 前 | 后 | 处置 |
|---|---:|---:|---|
| **逐 Task 检查失败** | **91** | **87** | — |
| `READY Task 未出现在 Plan 的 READY 节点` | 4 | **0** | **已裁定并修复**（§二）|
| `当前 DAG 未登记非终态 Task` | 26 | **22** | 同批 4 个随状态变更消除 |
| `Evidence SHA-256 不匹配` | 163 | **163** | **不逐个修**（§四）|
| AC 行不可见（CRLF） | 60 个文件 | **0** | **治本修复**（§三）|

## 二、裁定 1：4 个 `ready` 却未释放的 Task → 改 `proposed`

### 事实

`T3.2.1-REPAIR-3 / -7 / -9 / -10`：

| 字段 | 值 |
|---|---|
| `status` | **`ready`** |
| `owner` | Antigravity |
| `parent` 系列根 Task `T3.2.1` | **`closed_with_limitations`** |
| 是否在 `REBASELINE_PLAN` | **完全没有提及 `T3.2.1`** |
| `base_commit` | 均为 Rebaseline 之前的旧哈希 |

**同系列 16 个 Task 的状态分布**：`ready` 4、`changes_requested` 4、`approved` 2、
`done` 2、`proposed` 3、`closed_with_limitations` 1。

### 判据

`AGENTS.md`：

> **当前 Milestone、Task 树、依赖和 Legacy Mapping 只以 `REBASELINE_PLAN` 为准。**
> **只有 Rebaseline Plan 明确激活且范围已冻结的 Task 才允许实施。**

**所以：状态字段说「可以开工」，授权链说「不可以」。两者冲突时必须服从授权链。**

### 裁定

**4 个 Task 的 `status` 由 `ready` 改为 `proposed`**，并写入 `blocked_reason`：

> **未在 REBASELINE_PLAN 释放；父 Task T3.2.1 已 `closed_with_limitations`（Rebaseline 前遗留）。
> r188：状态 ready 与授权矛盾，改回 proposed；重新开工须先由 Codex 在 Plan 登记。**

### 为什么是 `proposed` 而不是 `blocked`

| 选项 | 判断 |
|---|---|
| `blocked` | **不准确**——它们不是被条件阻塞，是从未被释放 |
| **`proposed`** | **准确**——已起草、未释放；**且同系列已有 3 个 Task 处于此状态** |
| `superseded` | **越权**——r38 要求 `superseded` 必须有具名替代物或架构裁定，我没有 |

**附带效果**：`check.ps1` 的「非终态 Task 必须在 DAG 登记」门禁只对
`ready`/`in_progress`/`blocked`/`in_review`/`changes_requested`/`approved` 生效，
**`proposed` 不在其列**——所以改状态同时消除了那 4 条 DAG 登记错误。
**这不是为了绕过检查而选 `proposed`，而是两个独立结论恰好一致。**

### 未做

**没有改同系列其余 12 个非终态 Task 的状态。**
**r38 明确禁止按状态字段批量关闭，我也没有「顺手统一」。**

## 三、裁定 2：AC 正则治本修复（不只是 `.gitattributes` 治标）

**Round 187 我只加了 `doc/tasks/*.md text eol=lf`。**
**那让行尾变成我需要的值，但检查器本身仍然脆**——
**任何 CRLF 来源（别的平台、`core.autocrlf=input`、外部工具写回）都会让它再次失明。**

### 两处改动（`tools/governance/check.ps1`）

**1. AC 行正则（L455）**

```diff
- '(?m)^[ \t]*-[ \t]*\[([ xX])\][ \t]*\*\*AC[^\r\n]*$'
+ '(?m)^[ \t]*-[ \t]*\[([ xX])\][ \t]*\*\*AC[^\r\n]*\r?$'
```

**2. 取出匹配行后剥掉尾部 `\r`（L460 附近）**

```powershell
$acLine = $am.Value.TrimEnd([char]13)
```

**第 2 处必要**：标记校验正则 `'<<(MET|...)(?::...)?>>[ \t]*$'` 锚定 `$`，
**若不剥 `\r`，CRLF 行会通过第 1 关却卡在第 2 关。**

### 验证（构造 CRLF 文件实测）

**把 `PDF-STREAM-FIX-1` 转成纯 CRLF、改名后在临时路径检查**：

| 阶段 | 结果 |
|---|---|
| 修复前 | **`未找到任何 AC 行`** |
| 只改第 1 处 | 找到 AC1–AC5，但 **`AC 状态标记缺失或非法`** ×5 |
| **两处都改** | **AC 与标记全部合法**（仅剩临时文件造成的台账过期） |

**临时探测文件已删除。**

**回归验证**：9 个 Task 单独检查全部 `PASS`。

## 四、裁定 3：163 条哈希腐坏**不逐个修**

### 理由

**它们不是 AC 问题，是证据机制问题。**
**逐个改哈希只会让记录重新变绿，而机制依然会在下次 checkout 时再次腐坏。**

**而 r38 禁止批量回改历史 Task —— 即便只改哈希不动结论，也是在 39 个终态 Task 上做批量写入。**

### 处置

**记录在案，不改。**
**已修的两个（`PDF-STREAM-FIX-1`、`SEC-FMT-IMPL-1`）改成了 commit-only pin，
作为正确做法的示范，而不是批量模板。**

### 待 Codex 裁定

**检查器应否把 Evidence 哈希改为对 `git blob` 计算？**
**若改，163 条记录会一次性重新变得可验证——但那会改变「证据哈希」的语义，
不是我能单方决定的。**

## 五、裁定 4：其余不处置

| 项 | 数 | 处置 |
|---|---:|---|
| `Canonical evidence 路径缺失` | 23 | 不处置（多为历史 Task，需逐个人工判断）|
| `当前 DAG 未登记非终态 Task` | 22 | **不处置**（r38：不得批量改状态）|
| `Resource manifest 不存在` | 20 | 不处置（同 §四 理由，属历史记录）|
| `DONE evidence_dir 含未登记文件` | 11 | 不处置 |
| `DONE 不能保留未完成 AC` | 10 | **不处置**——r39/r38 已裁定不批量回改 |
| `P22` 失效本地引用 3 条 | 3 | 不处置（`in_review`，属其返修范围，需其 Owner 判断）|

## 六、明确未做

- **未逐个修 163 条哈希**（§四）
- **未改 22 个 Plan 外 Task 的状态**（r38）
- **未改 `task_ledger.py` 的扫描口径**（磁盘 vs git 跟踪）——需先裁定
- **未改 `doc/templates/TASK.md`**
- **未处理 `P22` 的失效引用**
- **未提交 26 个未跟踪草稿**

## 七、待 Codex 复核的事项

1. **§二 的 `proposed` 选择是否恰当**（vs `blocked` / `superseded`）
2. **§三 修改 `check.ps1` 是否越权**（共享契约，我以「治本 + 有验证」为由自行修改）
3. **§四 是否应改 Evidence 哈希口径**
4. **`task_ledger.py` 应否区分磁盘与已跟踪文件**
